#!/usr/bin/env python3
"""
Fase 3: benchmark de LLMs locales con vLLM para RAG (BOE y Debian).
Mismo stack que la Fase 2 (scripts/benchmark_embeddings_vllm.py).

Qué hace:
  1. Retrieval FIJO: reutiliza el top-k que el embedding ganador de la Fase 2 guardó en
     results/embeddings/data/<embedding>_<escenario>.json. Todos los LLMs reciben exactamente
     los mismos fragmentos (solo cambia una variable: el LLM).
  2. Calidad: las 15 preguntas del golden set, una vez (temperatura 0). Respuestas brutas a JSON.
  3. Coste: 5 preguntas. 1 ronda de calentamiento descartada + 3 rondas medidas; mediana.
       - TTFT: tiempo de una petición con max_tokens=1 (= prefill + primer token).
       - Latencia total: tiempo de la petición completa.
       - Tokens/s: (tokens generados − 1) / (latencia total − TTFT).
     La caché de prefijos de vLLM se desactiva para que repetir el prompt no abarate el TTFT.
  4. Oráculo (extra): la pregunta con los chunks correctos del golden set en lugar de los recuperados.
  5. VRAM pico de la GPU durante la prueba, con la MISMA caché KV para todos los modelos,
     para que la cifra compare modelos y no la reserva de vLLM.

Cada modelo × escenario se ejecuta en un proceso aparte (vLLM no libera bien la GPU dentro
del mismo proceso), igual que run_all_embeddings.py.

Uso (desde la raíz del repo):
  python scripts/benchmark_llms_vllm.py                        # 4 modelos × 2 escenarios
  python scripts/benchmark_llms_vllm.py --model llama3.2-3b --scenario boe
  python scripts/benchmark_llms_vllm.py --sin-oraculo
Después:  python scripts/generar_tablas_llm.py --plantilla   (y puntuar a mano)
          python scripts/generar_tablas_llm.py
"""

import argparse
import datetime
import json
import os
import re
import statistics
import subprocess
import sys
import threading
import time

# ---------------------------------------------------------------------------
# CONFIGURACIÓN COMÚN (igual para todos los modelos)
# ---------------------------------------------------------------------------
TOP_K = 5
TEMPERATURA = 0.0
SEED = 42
MAX_TOKENS_SALIDA = 512
MAX_MODEL_LEN = 8192            # ventana de contexto (vLLM da error si el prompt no cabe: nunca trunca en silencio)
CUANTIZACION = "fp8"            # la misma para todos; en Ampere (A800) vLLM la ejecuta como FP8 solo-pesos
DTYPE = "bfloat16"
KV_CACHE_GB = 2.0               # misma caché KV para todos (el README estima 1–3 GB)
GPU_MEM_UTIL_FALLBACK = 0.80    # solo si vuestra versión de vLLM no admite kv_cache_memory_bytes

# Embedding ganador de la Fase 2 por escenario. ¡Revisadlo!
#   BOE: harrier gana con cualquier criterio (Recall@5 = 1,00).
#   Debian: con el criterio Hit del README gana bge-m3 (0,83); con el estricto, harrier (0,75).
EMBEDDING_GANADOR = {
    "boe": "harrier-oss-v1",
    "debian": "bge-m3",
}

# Modelos (seleccion_llms.md §2), en su repositorio oficial de Hugging Face (safetensors, no GGUF).
# Comprobad en cada ficha que vuestra versión de vLLM soporta la arquitectura.
# `extra`: argumentos de vLLM solo para ese modelo. En los multimodales se ponen a 0 las
# modalidades que no usamos para que vLLM no cargue ni reserve memoria para el codificador
# de imagen/vídeo: así la VRAM compara solo la parte de texto, como en los demás.
# Si en el log de un modelo aparecen líneas de "vit", "vision", "audio" o "Encoder cache",
# añadidle lo mismo con las modalidades que tenga.
SOLO_TEXTO = {"limit_mm_per_prompt": {"image": 0, "video": 0}}
MODELOS = {
    "lfm3-1.7b":         {"repo": "LiquidAI/LFM3-1.7B",                      "tamano": "1,7B",           "categoria": "pequeño", "extra": {}},
    "llama3.2-3b":       {"repo": "meta-llama/Llama-3.2-3B-Instruct",        "tamano": "3B",             "categoria": "pequeño", "extra": {}},
    "nemotron-bolt-e4b": {"repo": "nvidia/NVIDIA-Nemotron-3.5-Bolt-E4B-BF16", "tamano": "8B (4B efect.)", "categoria": "mediano", "extra": {"limit_mm_per_prompt": {"image": 0, "audio": 0, "video": 0}}},
    "qwen3.5-9b":        {"repo": "Qwen/Qwen3.5-9B",                         "tamano": "9B",             "categoria": "mediano", "extra": SOLO_TEXTO},
}

SCENARIOS = {
    "boe": {
        "name": "Estatuto de los Trabajadores (BOE)",
        "chunks_path": "data/chunks/boe_final.json",
        "golden_path": "golden-set/golden_boe.jsonl",
        "cita": "el artículo",
    },
    "debian": {
        "name": "Manual del Administrador de Debian",
        "chunks_path": "data/chunks/debian_final.json",
        "golden_path": "golden-set/golden_debian.jsonl",
        "cita": "la sección",
    },
}

FRASE_ABSTENCION = "No aparece en el documento"

PROMPT_SISTEMA = (
    "Eres un asistente que responde preguntas usando ÚNICAMENTE los fragmentos proporcionados.\n\n"
    "Reglas:\n"
    "1. Responde solo con información que aparezca en los fragmentos. No uses conocimientos propios.\n"
    f"2. Si la respuesta no está en los fragmentos, responde exactamente: \"{FRASE_ABSTENCION}\" y nada más.\n"
    "3. Cita siempre {cita} de donde sale la respuesta (aparece en la línea «Fuente» de cada fragmento).\n"
    "4. Responde en español y de forma breve."
)
PROMPT_USUARIO = "Fragmentos:\n\n{fragmentos}\n\nPregunta: {pregunta}"

# Desactiva el modo razonamiento en las plantillas que lo tienen (Qwen3.5, Nemotron…);
# las que no lo usan ignoran la variable.
CHAT_TEMPLATE_KWARGS = {"enable_thinking": False}

DIR_OUT = "results/llms"


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def ahora():
    return datetime.datetime.now().isoformat(timespec="seconds")


def cargar_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def cargar_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


class VRAMMonitor:
    """Memoria usada en la GPU (toda la instancia MIG), muestreada cada 50 ms, como en la Fase 2."""

    def __init__(self, log_path, interval=0.05):
        self.log_path, self.interval, self.peak = log_path, interval, 0
        self._run, self._t = False, None

    @staticmethod
    def usada_bytes():
        import torch
        free, total = torch.cuda.mem_get_info(0)
        return total - free

    def start(self):
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        self._f = open(self.log_path, "w", buffering=1)
        self._f.write("timestamp,used_mb\n")
        self._run = True
        self._t = threading.Thread(target=self._loop, daemon=True)
        self._t.start()

    def _loop(self):
        while self._run:
            try:
                u = self.usada_bytes()
                self.peak = max(self.peak, u)
                self._f.write(f"{datetime.datetime.now().isoformat()},{u / 2**20:.1f}\n")
            except Exception:  # noqa: BLE001
                pass
            time.sleep(self.interval)

    def stop(self):
        self._run = False
        if self._t:
            self._t.join(timeout=1)
        self._f.close()
        return self.peak / 2**30 if self.peak else None


def formatear_fragmentos(ids, chunks_por_id):
    return "\n\n".join(
        f"[Fragmento {i}]\nFuente: {chunks_por_id[c]['fuente']}\n{chunks_por_id[c]['texto']}"
        for i, c in enumerate(ids, 1))


def construir_mensajes(scen_key, pregunta, ids, chunks_por_id):
    sistema = PROMPT_SISTEMA.replace("{cita}", SCENARIOS[scen_key]["cita"])
    usuario = PROMPT_USUARIO.format(fragmentos=formatear_fragmentos(ids, chunks_por_id), pregunta=pregunta)
    return [{"role": "system", "content": sistema}, {"role": "user", "content": usuario}]


def se_abstiene(respuesta):
    return "no aparece en el documento" in respuesta.lower()


def cita_detectada(scen_key, respuesta):
    if scen_key == "boe":
        return bool(re.search(r"\bart(?:[íi]culo|\.)?\s*\d+", respuesta, flags=re.I))
    return bool(re.search(r"\b\d+\.\d+(?:\.\d+)*\b|secci[óo]n", respuesta, flags=re.I))


def preguntas_coste(golden, n=5):
    """5 preguntas fijas y variadas: 3 directas, 1 combinada, 1 sin respuesta."""
    por_tipo = {}
    for g in golden:
        por_tipo.setdefault(g["tipo"], []).append(g)
    sel = por_tipo.get("directa", [])[:3] + por_tipo.get("combinada", [])[:1] + por_tipo.get("sin_respuesta", [])[:1]
    return (sel + [g for g in golden if g not in sel])[:n]


# ---------------------------------------------------------------------------
# vLLM
# ---------------------------------------------------------------------------
def cargar_llm(repo, extra=None):
    from vllm import LLM
    comunes = dict(**(extra or {}), model=repo, dtype=DTYPE, quantization=CUANTIZACION, max_model_len=MAX_MODEL_LEN,
                   enable_prefix_caching=False, enforce_eager=True, seed=SEED, disable_log_stats=True)
    try:
        llm = LLM(**comunes, kv_cache_memory_bytes=int(KV_CACHE_GB * 2**30))
        return llm, f"kv_cache_memory_bytes={KV_CACHE_GB} GB"
    except TypeError:
        # Versiones de vLLM sin ese parámetro: la VRAM medida será la reserva de gpu_memory_utilization
        llm = LLM(**comunes, gpu_memory_utilization=GPU_MEM_UTIL_FALLBACK)
        return llm, f"gpu_memory_utilization={GPU_MEM_UTIL_FALLBACK} (la VRAM pico refleja la reserva, no el modelo)"


class Generador:
    def __init__(self, llm):
        from vllm import SamplingParams
        self.llm = llm
        self.sp = SamplingParams(temperature=TEMPERATURA, max_tokens=MAX_TOKENS_SALIDA, seed=SEED)
        self.sp1 = SamplingParams(temperature=TEMPERATURA, max_tokens=1, seed=SEED)

    def _chat(self, mensajes, sp):
        t0 = time.perf_counter()
        out = self.llm.chat(mensajes, sp, use_tqdm=False, chat_template_kwargs=CHAT_TEMPLATE_KWARGS)[0]
        return out, time.perf_counter() - t0

    def generar(self, mensajes, medir_ttft=False):
        ttft = None
        if medir_ttft:
            _, ttft = self._chat(mensajes, self.sp1)
        out, total = self._chat(mensajes, self.sp)
        o = out.outputs[0]
        texto, n_out = o.text, len(o.token_ids)

        pensado = ""
        m = re.search(r"<think>(.*?)</think>", texto, flags=re.S)
        if m:
            pensado = m.group(1)
            texto = re.sub(r"<think>.*?</think>", "", texto, flags=re.S)

        tps = None
        if ttft is not None and n_out > 1 and total > ttft:
            tps = (n_out - 1) / (total - ttft)
        n_prompt = len(out.prompt_token_ids or [])
        return {
            "respuesta": texto.strip(),
            "razonamiento_detectado": bool(pensado.strip()),
            "ttft_s": round(ttft, 4) if ttft is not None else None,
            "latencia_total_s": round(total, 4),
            "tokens_salida": n_out,
            "tokens_por_s": round(tps, 2) if tps else None,
            "tokens_prompt": n_prompt,
            "finish_reason": o.finish_reason,
        }


# ---------------------------------------------------------------------------
# Benchmark de un modelo en un escenario (se ejecuta en su propio proceso)
# ---------------------------------------------------------------------------
def run(model_key, scen_key, oraculo=True, n_coste=5, rondas=3):
    import torch
    import vllm

    cfg, scen = MODELOS[model_key], SCENARIOS[scen_key]
    emb = EMBEDDING_GANADOR[scen_key]
    print(f"\n{'=' * 70}\nLLM: {model_key} ({cfg['repo']}) | {scen['name']} | Embedding: {emb}\n{'=' * 70}")

    chunks_por_id = {c["id"]: c for c in cargar_json(scen["chunks_path"])}
    golden = cargar_jsonl(scen["golden_path"])
    retrieval = {q["id"]: [r["chunk_id"] for r in q["top5"]][:TOP_K]
                 for q in cargar_json(f"results/embeddings/data/{emb}_{scen_key}.json")["questions"]}
    os.makedirs(f"{DIR_OUT}/data", exist_ok=True)

    vram = VRAMMonitor(f"{DIR_OUT}/logs/vram_{model_key}_{scen_key}.log")
    try:
        vram_base_gb = round(VRAMMonitor.usada_bytes() / 2**30, 3)
    except Exception:  # noqa: BLE001
        vram_base_gb = None
    vram.start()

    try:
        t0 = time.perf_counter()
        llm, modo_memoria = cargar_llm(cfg["repo"], cfg.get("extra"))
        t_carga = time.perf_counter() - t0
        gen = Generador(llm)
        print(f"[+] Cargado en {t_carga:.1f} s ({modo_memoria})")

        gen.generar([{"role": "user", "content": "Hola"}])   # calentamiento, no se mide

        # ---- Calidad ----
        respuestas = []
        for modo in ["retrieval"] + (["oraculo"] if oraculo else []):
            for q in golden:
                if modo == "oraculo" and not q.get("chunks"):
                    continue
                ids = q["chunks"] if modo == "oraculo" else retrieval[q["id"]]
                r = gen.generar(construir_mensajes(scen_key, q["pregunta"], ids, chunks_por_id))
                gold = q.get("chunks") or []
                respuestas.append({
                    "modelo": model_key, "escenario": scen_key, "modo": modo,
                    "id": q["id"], "tipo": q["tipo"], "pregunta": q["pregunta"],
                    "respuesta_esperada": q.get("respuesta", ""),
                    "chunks_contexto": ids, "gold_chunks": gold,
                    "gold_en_contexto": all(g in ids for g in gold) if gold else None,
                    "abstiene_auto": se_abstiene(r["respuesta"]),
                    "cita_auto": cita_detectada(scen_key, r["respuesta"]),
                    "posible_truncado": False,   # vLLM no trunca: daría error si no cabe
                    "cortado_por_num_predict": r["finish_reason"] == "length",
                    **r,
                })
                print(f"  [{modo}] {q['id']}: {r['respuesta'][:90]!r}")

        # ---- Coste ----
        qs = preguntas_coste(golden, n_coste)
        medidas = {q["id"]: [] for q in qs}
        for ronda in range(rondas + 1):
            for q in qs:
                r = gen.generar(construir_mensajes(scen_key, q["pregunta"], retrieval[q["id"]], chunks_por_id),
                                medir_ttft=True)
                if ronda > 0:
                    medidas[q["id"]].append(r)
            print(f"  [coste] ronda {ronda}{' (descartada)' if ronda == 0 else ''} hecha")
    finally:
        vram_pico_gb = vram.stop()

    def med(campo, lista):
        vals = [x[campo] for x in lista if x[campo] is not None]
        return round(statistics.median(vals), 4) if vals else None

    campos = ("ttft_s", "tokens_por_s", "latencia_total_s", "tokens_salida")
    todas = [x for rs in medidas.values() for x in rs]
    coste = {c: med(c, todas) for c in campos}

    meta = {
        "modelo": model_key, "repo": cfg["repo"], "tamano": cfg["tamano"], "categoria": cfg["categoria"],
        "cuantizacion": CUANTIZACION.upper(), "dtype": DTYPE, "stack": "vLLM", "stack_version": vllm.__version__,
        "torch_version": torch.__version__, "cuda_device": torch.cuda.get_device_name(0),
        "escenario": scen_key, "embedding": emb, "top_k": TOP_K,
        "opciones": {"temperature": TEMPERATURA, "num_predict": MAX_TOKENS_SALIDA, "num_ctx": MAX_MODEL_LEN,
                     "seed": SEED, "chat_template_kwargs": CHAT_TEMPLATE_KWARGS, "prefix_caching": False},
        "memoria": modo_memoria, "vllm_extra": cfg.get("extra", {}), "prompt_sistema": PROMPT_SISTEMA.replace("{cita}", scen["cita"]),
        "prompt_usuario": PROMPT_USUARIO, "timestamp": ahora(), "tiempo_carga_s": round(t_carga, 2),
        "tokens_prompt_max": max((r["tokens_prompt"] for r in respuestas), default=None),
        "vram_base_gb": vram_base_gb, "vram_pico_gb": round(vram_pico_gb, 3) if vram_pico_gb else None,
    }
    out = {
        "meta": meta,
        "coste": {"preguntas": [q["id"] for q in qs], "rondas_medidas": rondas, "mediana": coste,
                  "mediana_por_pregunta": {k: {c: med(c, v) for c in campos} for k, v in medidas.items()},
                  "ejecuciones": medidas},
        "respuestas": respuestas,
    }
    path = f"{DIR_OUT}/data/{model_key}_{scen_key}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    if any(r["razonamiento_detectado"] for r in respuestas):
        print("[!] Se detectó razonamiento (<think>) en alguna respuesta: revisad chat_template_kwargs.")
    print(f"--- {model_key}/{scen_key}: TTFT {coste['ttft_s']} s | {coste['tokens_por_s']} tok/s | "
          f"latencia {coste['latencia_total_s']} s | VRAM pico {meta['vram_pico_gb']} GB | "
          f"prompt máx. {meta['tokens_prompt_max']} tokens → {path}")


def main():
    ap = argparse.ArgumentParser(description="Fase 3: benchmark de LLMs con vLLM")
    ap.add_argument("--model", default="all", choices=list(MODELOS) + ["all"])
    ap.add_argument("--scenario", default="all", choices=list(SCENARIOS) + ["all"])
    ap.add_argument("--sin-oraculo", action="store_true")
    ap.add_argument("--n-coste", type=int, default=5)
    ap.add_argument("--rondas", type=int, default=3)
    a = ap.parse_args()

    modelos = list(MODELOS) if a.model == "all" else [a.model]
    escenarios = list(SCENARIOS) if a.scenario == "all" else [a.scenario]

    if len(modelos) == 1 and len(escenarios) == 1:
        run(modelos[0], escenarios[0], oraculo=not a.sin_oraculo, n_coste=a.n_coste, rondas=a.rondas)
        return

    # Varios: un proceso por modelo × escenario (aislamiento de la GPU)
    for s in escenarios:
        for m in modelos:
            cmd = [sys.executable, os.path.abspath(__file__), "--model", m, "--scenario", s,
                   "--n-coste", str(a.n_coste), "--rondas", str(a.rondas)] + (["--sin-oraculo"] if a.sin_oraculo else [])
            print(f"\n>>> Lanzando proceso: {m} / {s}")
            rc = subprocess.run(cmd).returncode
            if rc != 0:
                print(f"[!] {m}/{s} terminó con código {rc}; sigo con el siguiente")
    print("\nHecho. Siguiente paso: python scripts/generar_tablas_llm.py --plantilla")


if __name__ == "__main__":
    main()