#!/usr/bin/env python3
"""Evaluación de retrieval (Fase 2): solo embeddings, sin LLM.

Mide, por modelo y escenario: Recall@1, Recall@3, Recall@5, MRR, tiempo de
indexado, tamaño del índice y VRAM, y guarda todo en un JSON trazable.

Uso (ejemplo):
    python eval_retrieval.py \
        --modelo intfloat/multilingual-e5-large \
        --escenario debian \
        --chunks ../comun/chunks_debian.json \
        --golden ../comun/golden_debian.json \
        --config config_e5.json \
        --salida resultados \
        --turno-exclusivo

Prueba sin GPU ni modelos (embedder de juguete, solo para validar el código):
    python eval_retrieval.py --backend dummy --modelo dummy --escenario debian \
        --chunks ejemplo/chunks_ejemplo.json --golden ejemplo/golden_ejemplo.json

Formato de los chunks (lista JSON):
    {"id": "chunk_debian_0", "texto": "...", "metadatos": {"headings": [...]}}
    Opcional: "titulos": [...]  (si existe, se usa en vez de metadatos.headings)

Formato del golden set (lista JSON):
    {"id": "g01", "pregunta": "...", "tipo": "directa|combinada|sin_respuesta",
     "respuesta_esperada": "...",
     "chunks_correctos": ["chunk_debian_3", ...],       # ids de chunk
     "secciones_correctas": ["8.1 Configurar..."]}      # opcional: un titulo
    Cada id de chunks_correctos y cada seccion es un "objetivo". Un objetivo de
    seccion se cumple si se recupera cualquier chunk cuyos titulos contengan
    esa seccion.

VRAM: se guardan tres cifras. vram_pico_torch_gb es solo de este proceso;
vram_pico_nvidia_smi_gb y vram_pico_mem_get_info_gb son de toda la GPU/instancia
MIG (incluyen a los demas), asi que solo valen en turno exclusivo.

Config (JSON, opcional): prefijo_consulta, prefijo_documento, max_seq_length,
    batch_size, normalizar, trust_remote_code, dtype ("float16"/"bfloat16"), cpu.
"""
import argparse
import csv
import hashlib
import json
import platform
import re
import subprocess
import sys
import threading
import time
import zlib
from datetime import datetime
from pathlib import Path

import numpy as np

KS = (1, 3, 5)


# ---------------------------------------------------------------- utilidades
def sha256(ruta):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def slug(texto):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", texto).strip("_")


def cargar_json(ruta):
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def titulos_de(chunk):
    """Lista de titulos de seccion de un chunk (plano, Docling o BOE)."""
    meta = chunk.get("metadatos") or {}
    for fuente in (chunk.get("titulos"), chunk.get("headings"), meta.get("headings")):
        if fuente:
            return [str(t) for t in fuente]
    articulo = chunk.get("articulo")
    return [str(articulo)] if articulo else []


def texto_a_indexar(chunk, incluir_titulos):
    if incluir_titulos:
        t = titulos_de(chunk)
        if t:
            return " > ".join(t) + "\n" + chunk["texto"]
    return chunk["texto"]


# ------------------------------------------------------------------ backends
class EmbedderST:
    """sentence-transformers (el modelo real)."""

    def __init__(self, nombre, cfg):
        import torch
        from sentence_transformers import SentenceTransformer

        self.torch = torch
        self.cuda = torch.cuda.is_available() and not cfg.get("cpu", False)
        kwargs = {}
        if cfg.get("dtype"):
            kwargs["model_kwargs"] = {"torch_dtype": getattr(torch, cfg["dtype"])}
        self.model = SentenceTransformer(
            nombre,
            device="cuda" if self.cuda else "cpu",
            trust_remote_code=cfg.get("trust_remote_code", False),
            **kwargs,
        )
        if cfg.get("max_seq_length"):
            self.model.max_seq_length = int(cfg["max_seq_length"])
        self.max_seq_length = int(self.model.max_seq_length)
        self.batch_size = int(cfg.get("batch_size", 32))
        self.normalizar = bool(cfg.get("normalizar", True))
        self.default_prompt_name = getattr(self.model, "default_prompt_name", None)
        self.prompts = getattr(self.model, "prompts", None)
        self.parametros = sum(p.numel() for p in self.model.parameters())
        _dim = getattr(self.model, "get_embedding_dimension", None) or \
            self.model.get_sentence_embedding_dimension
        self.dimension = int(_dim())
        self.versiones = {
            "torch": torch.__version__,
            "sentence_transformers": __import__("sentence_transformers").__version__,
            "transformers": __import__("transformers").__version__,
        }

    def sincronizar(self):
        if self.cuda:
            self.torch.cuda.synchronize()

    def reiniciar_pico_vram(self):
        if self.cuda:
            self.torch.cuda.reset_peak_memory_stats()

    def pico_vram_gb(self):
        if not self.cuda:
            return None, None
        gb = 1024 ** 3
        return (
            self.torch.cuda.max_memory_allocated() / gb,
            self.torch.cuda.max_memory_reserved() / gb,
        )

    def prompt_por_defecto(self):
        return {"default_prompt_name": self.default_prompt_name,
                "prompts": self.prompts}

    def contar_truncados(self, textos):
        tok = self.model.tokenizer
        ids = tok(textos, add_special_tokens=True, truncation=False)["input_ids"]
        longitudes = [len(x) for x in ids]
        return sum(1 for n in longitudes if n > self.max_seq_length), max(longitudes)

    def codificar(self, textos):
        return self.model.encode(
            textos,
            batch_size=self.batch_size,
            normalize_embeddings=self.normalizar,
            convert_to_numpy=True,
            show_progress_bar=False,
        ).astype(np.float32)


class EmbedderDummy:
    """Bolsa de palabras con hashing. Solo sirve para probar el codigo sin GPU."""

    def __init__(self, nombre, cfg):
        self.dimension = 512
        self.parametros = 0
        self.max_seq_length = None
        self.default_prompt_name = None
        self.prompts = None
        self.versiones = {}

    def sincronizar(self):
        pass

    def reiniciar_pico_vram(self):
        pass

    def pico_vram_gb(self):
        return None, None

    def prompt_por_defecto(self):
        return {"default_prompt_name": None, "prompts": None}

    def contar_truncados(self, textos):
        return 0, max(len(t.split()) for t in textos)

    def codificar(self, textos):
        m = np.zeros((len(textos), self.dimension), dtype=np.float32)
        for i, t in enumerate(textos):
            for palabra in re.findall(r"\w+", t.lower()):
                m[i, zlib.crc32(palabra.encode()) % self.dimension] += 1.0
        normas = np.linalg.norm(m, axis=1, keepdims=True)
        normas[normas == 0] = 1.0
        return m / normas


# ----------------------------------------------------------- registro de GPU
# En una GPU con MIG, nvidia-smi --query-gpu devuelve "Insufficient Permissions"
# en memory.used. Por eso se guarda la salida de texto completa de nvidia-smi
# (que si muestra la memoria de la instancia MIG) y ademas se muestrea
# torch.cuda.mem_get_info() desde un hilo.
def iniciar_log_gpu(ruta):
    """Lanza nvidia-smi (salida de texto) cada 500 ms. Devuelve (proceso, fichero)."""
    f = open(ruta, "w", encoding="utf-8")
    try:
        p = subprocess.Popen(["nvidia-smi", "-lms", "500"], stdout=f,
                             stderr=subprocess.DEVNULL)
        return p, f
    except OSError:
        f.close()
        Path(ruta).unlink(missing_ok=True)
        print("AVISO: nvidia-smi no disponible, no se guarda registro de GPU.")
        return None, None


def parar_log_gpu(p, f):
    if p is not None:
        p.terminate()
        p.wait()
    if f is not None:
        f.close()


def pico_memoria_nvidia_smi(ruta):
    """Maximo de memoria usada (GB) en el log de texto de nvidia-smi.

    Con MIG lee la fila 'Shared Memory-Usage' (la de BAR1 se descarta). Incluye
    los procesos de todas las personas que comparten la instancia.
    """
    try:
        texto = Path(ruta).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    maximo = None
    for muestra in texto.split("NVIDIA-SMI")[1:]:
        usos = re.findall(r"(\d+)MiB\s*/\s*(\d+)MiB", muestra)
        if "MIG devices" in muestra:
            usos = usos[0::2]
        for usado, _total in usos:
            v = int(usado)
            maximo = v if maximo is None else max(maximo, v)
    return None if maximo is None else maximo / 1024


class MuestreadorVram:
    """Muestrea torch.cuda.mem_get_info() cada 100 ms en un hilo.

    Mide memoria usada en la GPU o instancia MIG completa (incluye a otros).
    'base_gb' es lo ya ocupado al empezar, para poder restarlo.
    """

    def __init__(self, torch, intervalo=0.1):
        self.torch = torch
        self.intervalo = intervalo
        self.base_gb = None
        self.pico_gb = None
        self.error = None
        self._parar = threading.Event()
        self._hilo = threading.Thread(target=self._bucle, daemon=True)

    def _bucle(self):
        gb = 1024 ** 3
        try:
            while not self._parar.is_set():
                libre, total = self.torch.cuda.mem_get_info()
                usada = (total - libre) / gb
                if self.base_gb is None:
                    self.base_gb = usada
                self.pico_gb = usada if self.pico_gb is None else max(self.pico_gb, usada)
                time.sleep(self.intervalo)
        except Exception as e:  # permisos, MIG, etc.
            self.error = repr(e)

    def iniciar(self):
        self._hilo.start()

    def parar(self):
        self._parar.set()
        self._hilo.join(timeout=2)


def crear_muestreador(backend, cfg):
    if backend != "st":
        return None
    try:
        import torch
        if torch.cuda.is_available() and not cfg.get("cpu", False):
            return MuestreadorVram(torch)
    except Exception:
        pass
    return None


# ------------------------------------------------------------------- metricas
def construir_objetivos(item, ids_corpus, ids_por_seccion, avisos):
    objetivos = []
    for cid in item.get("chunks_correctos", []) or []:
        if cid not in ids_corpus:
            avisos.append(f"{item['id']}: el chunk {cid} no existe en el corpus")
        objetivos.append({cid})
    for sec in item.get("secciones_correctas", []) or []:
        ids = ids_por_seccion.get(sec, set())
        if not ids:
            avisos.append(f"{item['id']}: la seccion '{sec}' no coincide con ningun chunk")
        objetivos.append(set(ids))
    return objetivos


def evaluar(golden, ids, titulos, matriz, consultas_emb, criterio_combinadas):
    ids_corpus = set(ids)
    ids_por_seccion = {}
    for cid, tits in zip(ids, titulos):
        for t in tits:
            ids_por_seccion.setdefault(t, set()).add(cid)

    avisos, detalle = [], []
    aciertos = {k: [] for k in KS}
    aciertos_tipo = {}
    rr = []
    rr_tipo = {}

    for item, q in zip(golden, consultas_emb):
        puntuaciones = matriz @ q
        orden = np.argsort(-puntuaciones)
        top5 = [(ids[i], float(puntuaciones[i])) for i in orden[: max(KS)]]
        fila = {
            "id": item["id"],
            "tipo": item["tipo"],
            "pregunta": item["pregunta"],
            "top5": [{"chunk": c, "puntuacion": round(s, 5)} for c, s in top5],
        }
        if item["tipo"] == "sin_respuesta":
            detalle.append(fila)
            continue

        objetivos = construir_objetivos(item, ids_corpus, ids_por_seccion, avisos)
        if not objetivos or any(len(o) == 0 for o in objetivos):
            avisos.append(f"{item['id']}: objetivos vacios o invalidos, pregunta ignorada")
            continue

        relevantes = set().union(*objetivos)
        posicion = next(
            (p for p, i in enumerate(orden, start=1) if ids[i] in relevantes), None
        )
        exigir_todos = item["tipo"] == "combinada" and criterio_combinadas == "todos"
        por_k = {}
        for k in KS:
            top_k = {ids[i] for i in orden[:k]}
            if exigir_todos:
                ok = all(o & top_k for o in objetivos)
            else:
                ok = any(o & top_k for o in objetivos)
            por_k[k] = ok
            aciertos[k].append(ok)
            aciertos_tipo.setdefault(item["tipo"], {kk: [] for kk in KS})[k].append(ok)
        inverso = 1.0 / posicion if posicion else 0.0
        rr.append(inverso)
        rr_tipo.setdefault(item["tipo"], []).append(inverso)

        fila.update({
            "posicion_primer_relevante": posicion,
            **{f"acierto@{k}": por_k[k] for k in KS},
        })
        detalle.append(fila)

    def media(valores):
        return float(np.mean(valores)) if valores else None

    metricas = {f"recall@{k}": media(aciertos[k]) for k in KS}
    metricas["mrr"] = media(rr)
    metricas["n_preguntas_con_respuesta"] = len(rr)
    metricas["por_tipo"] = {
        t: {
            **{f"recall@{k}": media(v[k]) for k in KS},
            "mrr": media(rr_tipo[t]),
            "n": len(rr_tipo[t]),
        }
        for t, v in aciertos_tipo.items()
    }
    return metricas, detalle, avisos


# ----------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--modelo", required=True, help="Nombre HF del modelo (o 'dummy')")
    ap.add_argument("--escenario", required=True, choices=["boe", "debian"])
    ap.add_argument("--chunks", required=True)
    ap.add_argument("--golden", required=True)
    ap.add_argument("--config", help="JSON con prefijos, max_seq_length, etc.")
    ap.add_argument("--salida", default="resultados")
    ap.add_argument("--backend", choices=["st", "dummy"], default="st")
    ap.add_argument("--criterio-combinadas", choices=["todos", "alguno"], default="todos",
                    help="Preguntas combinadas: recuperar todos los fragmentos o basta uno")
    ap.add_argument("--incluir-titulos", action="store_true",
                    help="Anteponer los titulos de seccion al texto de cada chunk al indexar")
    ap.add_argument("--turno-exclusivo", action="store_true",
                    help="Marcar que la ejecucion se hizo con la GPU en turno exclusivo")
    args = ap.parse_args()

    cfg = cargar_json(args.config) if args.config else {}
    marca = datetime.now().strftime("%Y%m%d-%H%M%S")
    base = f"{slug(args.modelo)}__{args.escenario}__{marca}"
    salida = Path(args.salida)
    salida.mkdir(parents=True, exist_ok=True)

    chunks = cargar_json(args.chunks)
    golden = cargar_json(args.golden)
    ids = [c["id"] for c in chunks]
    titulos = [titulos_de(c) for c in chunks]
    docs = [texto_a_indexar(c, args.incluir_titulos) for c in chunks]
    pref_doc = cfg.get("prefijo_documento", "")
    pref_q = cfg.get("prefijo_consulta", "")

    ruta_gpu = salida / f"{base}__nvidia-smi.log"
    proc_gpu, fich_gpu = iniciar_log_gpu(ruta_gpu)
    muestreador = crear_muestreador(args.backend, cfg)
    if muestreador:
        muestreador.iniciar()
    try:
        # carga del modelo
        t0 = time.perf_counter()
        Emb = EmbedderST if args.backend == "st" else EmbedderDummy
        emb = Emb(args.modelo, cfg)
        carga_s = time.perf_counter() - t0
        emb.reiniciar_pico_vram()

        avisos_config = []
        if pref_q and emb.default_prompt_name:
            avisos_config.append(
                "El modelo trae prompt por defecto "
                f"'{emb.default_prompt_name}' y ademas se aplica prefijo_consulta; "
                "podria duplicarse la instruccion."
            )

        # calentamiento (no se cuenta): evita medir la inicializacion de CUDA
        emb.codificar([pref_doc + d for d in docs[:8]])
        emb.sincronizar()

        truncados, max_tokens = emb.contar_truncados([pref_doc + d for d in docs])

        # indexado
        t0 = time.perf_counter()
        matriz = emb.codificar([pref_doc + d for d in docs])
        emb.sincronizar()
        indexado_s = time.perf_counter() - t0

        # consultas
        preguntas = [g["pregunta"] for g in golden]
        t0 = time.perf_counter()
        consultas = emb.codificar([pref_q + p for p in preguntas])
        emb.sincronizar()
        consultas_s = time.perf_counter() - t0

        pico_alloc, pico_reserv = emb.pico_vram_gb()
    except BaseException:
        # Si falla, no dejar logs huerfanos de una ejecucion que no produjo resultados
        parar_log_gpu(proc_gpu, fich_gpu)
        if muestreador:
            muestreador.parar()
        Path(ruta_gpu).unlink(missing_ok=True)
        raise
    parar_log_gpu(proc_gpu, fich_gpu)
    if muestreador:
        muestreador.parar()

    ruta_indice = salida / f"{base}__indice.npy"
    np.save(ruta_indice, matriz)
    indice_mb = ruta_indice.stat().st_size / (1024 * 1024)

    metricas, detalle, avisos = evaluar(
        golden, ids, titulos, matriz, consultas, args.criterio_combinadas
    )

    resultado = {
        "meta": {
            "fecha_hora": datetime.now().isoformat(timespec="seconds"),
            "modelo": args.modelo,
            "backend": args.backend,
            "escenario": args.escenario,
            "parametros": emb.parametros,
            "dimension": emb.dimension,
            "max_seq_length": emb.max_seq_length,
            "prompt_por_defecto_del_modelo": emb.prompt_por_defecto(),
            "versiones": {"python": platform.python_version(), "numpy": np.__version__,
                          **emb.versiones},
            "chunks_fichero": str(args.chunks),
            "chunks_sha256": sha256(args.chunks),
            "golden_fichero": str(args.golden),
            "golden_sha256": sha256(args.golden),
            "n_chunks": len(chunks),
            "n_preguntas": len(golden),
            "comando": " ".join(sys.argv),
        },
        "config": {
            "prefijo_consulta": pref_q,
            "prefijo_documento": pref_doc,
            "criterio_combinadas": args.criterio_combinadas,
            "incluir_titulos": args.incluir_titulos,
            "extra": {k: v for k, v in cfg.items()
                      if k not in ("prefijo_consulta", "prefijo_documento")},
        },
        "metricas": metricas,
        "coste": {
            "carga_modelo_s": round(carga_s, 3),
            "indexado_s": round(indexado_s, 3),
            "consultas_s": round(consultas_s, 3),
            "indice_mb": round(indice_mb, 3),
            "vram_pico_torch_gb": None if pico_alloc is None else round(pico_alloc, 3),
            "vram_reservada_pico_torch_gb": None if pico_reserv is None else round(pico_reserv, 3),
            "vram_pico_nvidia_smi_gb": (
                lambda v: None if v is None else round(v, 3)
            )(pico_memoria_nvidia_smi(ruta_gpu)),
            "vram_pico_mem_get_info_gb": (
                None if not muestreador or muestreador.pico_gb is None
                else round(muestreador.pico_gb, 3)),
            "vram_base_mem_get_info_gb": (
                None if not muestreador or muestreador.base_gb is None
                else round(muestreador.base_gb, 3)),
            "vram_muestreo_error": muestreador.error if muestreador else None,
            "turno_exclusivo": args.turno_exclusivo,
            "chunks_truncados_por_limite": truncados,
            "max_tokens_de_un_chunk": max_tokens,
        },
        "avisos": avisos_config + avisos,
        "detalle": detalle,
    }
    ruta_json = salida / f"{base}.json"
    with open(ruta_json, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    m = metricas
    print(f"Modelo: {args.modelo} | escenario: {args.escenario}")
    print(f"Recall@1={m['recall@1']:.3f}  Recall@3={m['recall@3']:.3f}  "
          f"Recall@5={m['recall@5']:.3f}  MRR={m['mrr']:.3f}  "
          f"(n={m['n_preguntas_con_respuesta']})")
    print(f"Indexado: {indexado_s:.2f} s | indice: {indice_mb:.2f} MB | "
          f"chunks truncados: {truncados}")
    avisos_todos = avisos_config + avisos
    if avisos_todos:
        print("AVISOS:")
        for a in avisos_todos:
            print("  -", a)
    if truncados:
        print("ATENCION: hay chunks mas largos que el limite del modelo; "
              "el final no se indexa.")
    print(f"Resultados: {ruta_json}")


if __name__ == "__main__":
    main()