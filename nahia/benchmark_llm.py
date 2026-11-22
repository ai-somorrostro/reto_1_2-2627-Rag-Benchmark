#!/usr/bin/env python3
"""Fase 3: benchmark de UN LLM en UN escenario (prompt, ejecución, registro, GPU).

Qué hace, en orden:
  1. Recupera los top-k chunks de cada pregunta con el embedding ganador
     (o, con --fragmentos golden, usa directamente los chunks correctos: extra
     opcional para separar fallo de retrieval y fallo del LLM).
  2. Libera la GPU del embedding, arranca el registro de nvidia-smi y carga el LLM.
  3. Calentamiento (una generación que se descarta).
  4. Pasa las 15 preguntas: una ejecución cada una. Las preguntas elegidas para
     coste (--n-coste, por defecto 5) se repiten 3 veces.
  5. Guarda: <base>.jsonl (una línea por ejecución), <base>_gpu.csv (nvidia-smi),
     <base>_meta.json (versión, cuantización, stack, parámetros, prompt...) y
     <base>_puntuacion.csv (hoja para puntuar a mano).

Uso (con turno de GPU):
  python benchmark_llm.py --modelo Qwen/Qwen3-8B --escenario boe \
      --embedding BAAI/bge-m3 --config-embedding ../sendoa/config_bge_m3.json

Prueba del código sin GPU: añadir --dispositivo cpu --max-tokens 20 --n-coste 1
"""
import argparse
import hashlib
import json
import re
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
COMUN = AQUI.parent / "comun"
sys.path.insert(0, str(AQUI))

from gpu_log import RegistradorGPU  # noqa: E402
from prompt import PROMPT, construir_prompt  # noqa: E402
from puntuacion import crear_hoja_puntuacion  # noqa: E402
from registro import CARPETA_RESULTADOS, guardar_registro  # noqa: E402

TEMPERATURA = 0          # do_sample=False (greedy): misma salida en cada repetición
REPETICIONES_COSTE = 3
CUOTA_COSTE = {"directa": 2, "combinada": 2, "sin_respuesta": 1}  # = 5 preguntas


def slug(texto):
    return re.sub(r"[^A-Za-z0-9.-]+", "_", texto).strip("_")


def sha256_fichero(ruta):
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()[:16]


def cargar_json(ruta):
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def titulos_de(chunk):
    """Sección o artículo del chunk, para que el LLM pueda citarlo."""
    meta = chunk.get("metadatos") or {}
    for fuente in (chunk.get("titulos"), chunk.get("headings"), meta.get("headings")):
        if fuente:
            return [str(t) for t in fuente]
    return [str(chunk["articulo"])] if chunk.get("articulo") else []


def etiquetar(chunk):
    etiqueta = chunk["articulo"] if chunk.get("articulo") else " > ".join(titulos_de(chunk))
    return f"[{etiqueta}]\n{chunk['texto']}"


def elegir_preguntas_coste(golden, n_coste):
    """Selección fija y reproducible: las primeras de cada tipo según CUOTA_COSTE."""
    elegidas, cuenta = [], {t: 0 for t in CUOTA_COSTE}
    for q in golden:
        t = q["tipo"]
        if t in CUOTA_COSTE and cuenta[t] < CUOTA_COSTE[t] and len(elegidas) < n_coste:
            elegidas.append(q["id"])
            cuenta[t] += 1
    return set(elegidas)


# --------------------------------------------------------------- retrieval
def recuperar(embedding, cfg, chunks, golden, k, dispositivo):
    """Top-k por pregunta con el mismo trato de prefijos que sendoa/eval_retrieval.py."""
    import gc

    import torch
    from sentence_transformers import SentenceTransformer

    modelo = SentenceTransformer(
        embedding, device=dispositivo, trust_remote_code=cfg.get("trust_remote_code", False)
    )
    if cfg.get("max_seq_length"):
        modelo.max_seq_length = int(cfg["max_seq_length"])
    pref_doc, pref_q = cfg.get("prefijo_documento", ""), cfg.get("prefijo_consulta", "")
    kw = dict(batch_size=int(cfg.get("batch_size", 32)),
              normalize_embeddings=bool(cfg.get("normalizar", True)),
              convert_to_numpy=True, show_progress_bar=False)
    docs = modelo.encode([pref_doc + c["texto"] for c in chunks], **kw)
    qs = modelo.encode([pref_q + g["pregunta"] for g in golden], **kw)
    sims = qs @ docs.T
    top = np.argsort(-sims, axis=1)[:, :k]
    resultado = {
        g["id"]: [(chunks[j]["id"], float(sims[i, j])) for j in top[i]]
        for i, g in enumerate(golden)
    }
    del modelo
    gc.collect()
    if dispositivo == "cuda":
        torch.cuda.empty_cache()
    return resultado


# -------------------------------------------------------------- generación
def crear_cronometro():
    from transformers.generation.streamers import BaseStreamer

    class Cronometro(BaseStreamer):
        """Apunta cuándo llega cada token, para medir TTFT y tokens/s."""

        def __init__(self):
            self.t_inicio = time.perf_counter()
            self.t_primer_token = None
            self.t_fin = None
            self.n_tokens = 0
            self._es_el_prompt = True

        def put(self, valor):
            if self._es_el_prompt:  # la primera llamada es el prompt, no un token generado
                self._es_el_prompt = False
                return
            if self.t_primer_token is None:
                self.t_primer_token = time.perf_counter()
            self.n_tokens += 1

        def end(self):
            self.t_fin = time.perf_counter()

    return Cronometro()


def generar(modelo, tokenizador, prompt, max_tokens, dispositivo):
    import torch

    texto = tokenizador.apply_chat_template(
        [{"role": "user", "content": prompt}],
        tokenize=False, add_generation_prompt=True,
        enable_thinking=False,  # trampa: razonamiento activo = más latencia y texto extra
    )
    entradas = tokenizador(texto, return_tensors="pt", add_special_tokens=False).to(dispositivo)
    n_prompt = entradas["input_ids"].shape[1]

    if dispositivo == "cuda":
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()
    crono = crear_cronometro()
    with torch.no_grad():
        salida = modelo.generate(**entradas, max_new_tokens=max_tokens,
                                 do_sample=False, streamer=crono)
    if dispositivo == "cuda":
        torch.cuda.synchronize()
    respuesta = tokenizador.decode(salida[0][n_prompt:], skip_special_tokens=True).strip()

    gen = (crono.t_fin - crono.t_primer_token) if crono.t_primer_token else 0
    return {
        "respuesta": respuesta,
        "tokens_prompt": n_prompt,
        "tokens_generados": crono.n_tokens,
        "ttft_s": round(crono.t_primer_token - crono.t_inicio, 3) if crono.t_primer_token else None,
        "tokens_por_s": round(crono.n_tokens / gen, 1) if crono.n_tokens > 1 and gen > 0 else None,
        "latencia_total_s": round(crono.t_fin - crono.t_inicio, 3),
        "vram_pico_torch_gb": round(torch.cuda.max_memory_allocated() / 1024**3, 2)
        if dispositivo == "cuda" else None,
    }


def ventana_contexto(modelo):
    c = modelo.config
    for cfg in (c, getattr(c, "text_config", None)):
        v = getattr(cfg, "max_position_embeddings", None) if cfg is not None else None
        if v:
            return int(v)
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--modelo", required=True, help="id de Hugging Face del LLM")
    ap.add_argument("--escenario", required=True, choices=["boe", "debian"])
    ap.add_argument("--embedding", help="embedding ganador (obligatorio salvo --fragmentos golden)")
    ap.add_argument("--config-embedding", help="JSON de prefijos de sendoa/config_*.json")
    ap.add_argument("--fragmentos", choices=["retrieval", "golden"], default="retrieval")
    ap.add_argument("--top-k", type=int, default=5)
    ap.add_argument("--max-tokens", type=int, default=300)
    ap.add_argument("--n-coste", type=int, default=5)
    ap.add_argument("--turno-exclusivo", action="store_true",
                    help="marca la medida como oficial (GPU sin nadie más)")
    ap.add_argument("--dispositivo", choices=["cuda", "cpu"], default="cuda")
    args = ap.parse_args()

    if args.fragmentos == "retrieval" and not (args.embedding and args.config_embedding):
        ap.error("con --fragmentos retrieval hacen falta --embedding y --config-embedding")

    chunks = cargar_json(COMUN / f"chunks_{args.escenario}.json")
    golden = cargar_json(COMUN / f"golden_set_{args.escenario}.json")
    por_id = {c["id"]: c for c in chunks}
    if args.fragmentos == "golden":  # sin_respuesta no tiene chunk correcto: se omite
        golden = [g for g in golden if g["chunks_correctos"]]

    # 1. Retrieval (antes del LLM, para que el embedding no ocupe VRAM durante la medida)
    if args.fragmentos == "retrieval":
        cfg_emb = cargar_json(args.config_embedding)
        recuperados = recuperar(args.embedding, cfg_emb, chunks, golden, args.top_k, args.dispositivo)
    else:
        recuperados = {g["id"]: [(i, None) for i in g["chunks_correctos"]] for g in golden}

    marca = datetime.now().strftime("%Y%m%d-%H%M%S")
    base = f"{slug(args.modelo)}__{args.escenario}__{marca}"
    CARPETA_RESULTADOS.mkdir(exist_ok=True)
    nombre_jsonl = f"{base}.jsonl"

    import torch
    import transformers
    from transformers import AutoModelForCausalLM, AutoTokenizer

    coste = elegir_preguntas_coste(golden, args.n_coste)
    with RegistradorGPU(CARPETA_RESULTADOS / f"{base}_gpu.csv") as gpu:
        # 2. Cargar LLM
        t0 = time.perf_counter()
        kw_tok = {"fix_mistral_regex": True} if "istral" in args.modelo else {}
        tokenizador = AutoTokenizer.from_pretrained(args.modelo, **kw_tok)
        try:
            modelo = AutoModelForCausalLM.from_pretrained(args.modelo, dtype=torch.bfloat16)
        except ValueError:  # p. ej. Ministral 3: su clase es multimodal (texto + imagen)
            from transformers import AutoModelForImageTextToText
            modelo = AutoModelForImageTextToText.from_pretrained(args.modelo, dtype=torch.bfloat16)
        modelo.to(args.dispositivo).eval()
        carga_s = time.perf_counter() - t0
        ventana = ventana_contexto(modelo)

        prompts = {}
        for g in golden:
            frags = [etiquetar(por_id[i]) for i, _ in recuperados[g["id"]]]
            prompts[g["id"]] = construir_prompt(frags, g["pregunta"])

        # 3. Calentamiento: se descarta (carga de kernels, caché, etc.)
        generar(modelo, tokenizador, prompts[golden[0]["id"]], 8, args.dispositivo)

        # 4. Preguntas
        for g in golden:
            reps = REPETICIONES_COSTE if g["id"] in coste else 1
            correctos = set(g["chunks_correctos"])
            ids_rec = [i for i, _ in recuperados[g["id"]]]
            for r in range(0 if g['id'] in coste else 1, reps + 1):  # rep 0 = primera ejecución, se descarta
                m = generar(modelo, tokenizador, prompts[g["id"]], args.max_tokens, args.dispositivo)
                if ventana and m["tokens_prompt"] + args.max_tokens > ventana:
                    print(f"AVISO: {g['id']} no cabe en la ventana ({m['tokens_prompt']}+{args.max_tokens}>{ventana})")
                guardar_registro(
                    nombre_jsonl,
                    modelo=args.modelo,
                    version_modelo=getattr(modelo.config, "_commit_hash", None),
                    cuantizacion="bf16",
                    stack="transformers " + transformers.__version__,
                    escenario=args.escenario,
                    pregunta_id=g["id"],
                    tipo=g["tipo"],
                    pregunta=g["pregunta"],
                    respuesta_esperada=g["respuesta_esperada"],
                    modo_fragmentos=args.fragmentos,
                    embedding=args.embedding if args.fragmentos == "retrieval" else None,
                    top_k=args.top_k if args.fragmentos == "retrieval" else len(ids_rec),
                    chunks_pasados=ids_rec,
                    chunks_correctos=sorted(correctos),
                    acierto_retrieval=bool(correctos & set(ids_rec)) if correctos else None,
                    repeticion=r,
                    descartada=(r == 0),
                    para_coste=g["id"] in coste,
                    max_tokens_salida=args.max_tokens,
                    temperatura=TEMPERATURA,
                    ventana_contexto=ventana,
                    **m,
                )
                print(f"{g['id']} rep{r}: {m['latencia_total_s']} s, "
                      f"{m['tokens_por_s']} tok/s, prompt {m['tokens_prompt']} tok")
        pico_smi_mb = gpu.pico_mb

    # 5. Meta + hoja de puntuación
    meta = {
        "modelo": args.modelo,
        "version_modelo": getattr(modelo.config, "_commit_hash", None),
        "parametros_miles_de_millones": round(sum(p.numel() for p in modelo.parameters()) / 1e9, 2),
        "cuantizacion": "bf16",
        "stack": "transformers " + transformers.__version__,
        "torch": torch.__version__,
        "dispositivo": args.dispositivo,
        "escenario": args.escenario,
        "fragmentos": args.fragmentos,
        "embedding": args.embedding,
        "config_embedding": args.config_embedding,
        "top_k": args.top_k,
        "max_tokens_salida": args.max_tokens,
        "temperatura": TEMPERATURA,
        "ventana_contexto": ventana,
        "preguntas_coste": sorted(coste),
        "repeticiones_coste": REPETICIONES_COSTE,
        "chunks_sha256": sha256_fichero(COMUN / f"chunks_{args.escenario}.json"),
        "golden_sha256": sha256_fichero(COMUN / f"golden_set_{args.escenario}.json"),
        "turno_exclusivo": args.turno_exclusivo,
        "enable_thinking_en_plantilla": "enable_thinking" in (tokenizador.chat_template or ""),
        "prompt_sha256": hashlib.sha256(PROMPT.encode()).hexdigest()[:16],
        "carga_modelo_s": round(carga_s, 1),
        "vram_pico_nvidia_smi_gb": round(pico_smi_mb / 1024, 2),
        "fecha_hora": datetime.now().isoformat(timespec="seconds"),
        "fichero_respuestas": nombre_jsonl,
        "fichero_gpu": f"{base}_gpu.csv",
    }
    with open(CARPETA_RESULTADOS / f"{base}_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    ruta, n = crear_hoja_puntuacion(CARPETA_RESULTADOS / nombre_jsonl)
    print(f"\nListo: {n} respuestas para puntuar en {ruta}")
    print(f"VRAM pico (nvidia-smi): {meta['vram_pico_nvidia_smi_gb']} GB")


if __name__ == "__main__":
    main()
