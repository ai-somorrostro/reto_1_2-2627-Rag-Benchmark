#!/usr/bin/env python3
"""
Plan B (8 GB de VRAM): los dos LLM medianos cuantizados a 4 bits (GGUF Q4_K_M) con llama.cpp.

Por qué llama.cpp y no vLLM
  Las versiones de 4 bits para vLLM (AWQ / W4A16) solo cuantizan las capas del transformer; los
  embeddings de entrada y salida se quedan en BF16, y en estos modelos son enormes (vocabulario de
  ~250k tokens). Lo comprobamos leyendo las cabeceras safetensors de Hugging Face:
    - cyankiwi/Qwen3.5-9B-AWQ-4bit:  capas 3,9 GB + embed_tokens 2,0 GB + lm_head 2,0 GB ≈ 8,0 GB solo de pesos
    - turintech/Nemotron-3.5-Bolt-E4B-Artemis-W4A16: capas 3,1 GB + embeddings por capa 5,8 GB + embed 1,3 GB ≈ 10,3 GB
  Sin contar la caché KV ni el embedding del retrieval, ya no caben en 8 GB.
  En GGUF Q4_K_M también se cuantizan los embeddings, y llama.cpp deja la tabla de embeddings de
  entrada en la RAM de la CPU, así que el modelo ocupa mucho menos en la GPU.

Qué mide (igual que benchmark_llms_vllm.py, para poder comparar)
  - Mismo retrieval fijo (top-5 del embedding ganador de la Fase 2), mismo prompt, temperatura 0,
    max_tokens 512, ventana de 8192 tokens, sin razonamiento.
  - Calidad: las 15 preguntas (+ oráculo). Coste: 5 preguntas, 1 ronda descartada + 3 medidas, mediana.
    TTFT = petición con max_tokens=1; tokens/s = (tokens − 1) / (latencia − TTFT).
    La caché de prompts de llama.cpp se desactiva (cache_prompt=false) para no abaratar el TTFT.
  - VRAM: memoria usada en toda la instancia MIG, muestreada cada 50 ms. Se guarda:
      vram_pico_gb      pico total (incluye el contexto CUDA de este proceso, que solo vigila)
      vram_base_gb      lo que había antes de arrancar llama-server
      vram_llm_gb       pico − base = lo que ocupa llama-server (la cifra para el Plan B)
    Para el Plan B hay que sumarle el embedding del retrieval (~1,1 GB en FP16, decision_fase4.md).

Salida: results/llms/plan_b/data/<modelo>_<escenario>.json, con el mismo formato que la Fase 3.
Después:  python scripts/generar_tablas_llm.py --dir results/llms/plan_b --plantilla   (puntuar a mano)
          python scripts/generar_tablas_llm.py --dir results/llms/plan_b

Requisito: llama-server con CUDA. Build oficial fijada (driver ≥ 570):
  mkdir -p tools/llama.cpp && cd tools/llama.cpp
  V=b12633
  curl -LO https://github.com/ggml-org/llama.cpp/releases/download/$V/llama-$V-bin-ubuntu-cuda-12.8-x64.tar.gz
  curl -LO https://github.com/ggml-org/llama.cpp/releases/download/$V/cudart-llama-$V-bin-ubuntu-cuda-12.8-x64.tar.gz
  for f in *.tar.gz; do tar xzf $f; done
  cp cudart-llama-$V-bin-ubuntu-cuda-12.8-x64/* llama-$V/
  cd ../.. && LD_LIBRARY_PATH=tools/llama.cpp/llama-$V tools/llama.cpp/llama-$V/llama-server --version
  (debe listar la A800 como dispositivo CUDA)

Uso (desde la raíz del repo, con el entorno de vLLM: hace falta torch para medir la VRAM):
  python scripts/benchmark_plan_b_llamacpp.py                          # Qwen y Nemotron en Q4, 2 escenarios
  python scripts/benchmark_plan_b_llamacpp.py --model qwen3.5-9b-q4 --scenario boe
  python scripts/benchmark_plan_b_llamacpp.py --model qwen3.5-9b-q8    # extra: Q8 del mismo modelo
  python scripts/benchmark_plan_b_llamacpp.py --llama-server /ruta/llama-server
"""

import argparse
import json
import os
import socket
import statistics
import subprocess
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from benchmark_llms_vllm import (  # noqa: E402  (misma configuración y utilidades que la Fase 3)
    CHAT_TEMPLATE_KWARGS, EMBEDDING_GANADOR, MAX_MODEL_LEN, MAX_TOKENS_SALIDA, PROMPT_SISTEMA, PROMPT_USUARIO,
    SCENARIOS, SEED, TEMPERATURA, TOP_K, VRAMMonitor, ahora, cargar_json, cargar_jsonl, cita_detectada,
    construir_mensajes, preguntas_coste, se_abstiene,
)

LLAMA_CPP_VERSION = "b12633"
LLAMA_SERVER_DEFECTO = f"tools/llama.cpp/llama-{LLAMA_CPP_VERSION}/llama-server"
LIMITE_PLAN_B_GB = 8.0
EMBEDDING_RETRIEVAL_GB = 1.1   # bge-m3 / harrier en FP16 (decision_fase4.md §5)

# GGUF por modelo. Nemotron: el repositorio oficial de NVIDIA (el que se planeó al principio,
# seleccion_llms.md). Qwen no publica GGUF propio; se usa el de Unsloth.
# Solo el modelo de texto: no se descarga ni se carga el mmproj (codificador de imagen).
MODELOS = {
    "qwen3.5-9b-q4": {"repo": "unsloth/Qwen3.5-9B-GGUF", "archivo": "Qwen3.5-9B-Q4_K_M.gguf",
                      "tamano": "9B", "cuantizacion": "GGUF Q4_K_M", "base": "qwen3.5-9b"},
    "nemotron-bolt-e4b-q4": {"repo": "nvidia/NVIDIA-Nemotron-3.5-Bolt-E4B-4GB", "archivo": "Nemotron-3.5-Bolt-E4B-Q4_K_M.gguf",
                             "tamano": "8B (4B efect.)", "cuantizacion": "GGUF Q4_K_M", "base": "nemotron-bolt-e4b"},
    # Extra del README («comparar Q4 y Q8 del mismo modelo»). No caben en 8 GB; sirven para ver
    # cuánto se pierde al pasar de 8 a 4 bits con el mismo stack.
    "qwen3.5-9b-q8": {"repo": "unsloth/Qwen3.5-9B-GGUF", "archivo": "Qwen3.5-9B-Q8_0.gguf",
                      "tamano": "9B", "cuantizacion": "GGUF Q8_0", "base": "qwen3.5-9b"},
    "nemotron-bolt-e4b-q8": {"repo": "bartowski/NVIDIA-Nemotron-3.5-Bolt-E4B-GGUF", "archivo": "NVIDIA-Nemotron-3.5-Bolt-E4B-Q8_0.gguf",
                             "tamano": "8B (4B efect.)", "cuantizacion": "GGUF Q8_0", "base": "nemotron-bolt-e4b"},
}
MODELOS_POR_DEFECTO = ["qwen3.5-9b-q4", "nemotron-bolt-e4b-q4"]

DIR_OUT = "results/llms/plan_b"


# ---------------------------------------------------------------------------
# llama-server
# ---------------------------------------------------------------------------
def puerto_libre():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def descargar_gguf(cfg):
    from huggingface_hub import hf_hub_download
    return hf_hub_download(cfg["repo"], cfg["archivo"])


class LlamaServer:
    def __init__(self, binario, gguf, log_path, extra_args=()):
        self.port = puerto_libre()
        self.url = f"http://127.0.0.1:{self.port}"
        self.cmd = [
            binario, "-m", gguf,
            "--host", "127.0.0.1", "--port", str(self.port),
            "-c", str(MAX_MODEL_LEN),       # misma ventana que en vLLM
            "-ngl", "999",                  # todas las capas en la GPU
            "-np", "1",                     # una sola petición a la vez (como en la Fase 3)
            "--seed", str(SEED),
            "--jinja",                      # plantilla de chat del propio GGUF
            "--chat-template-kwargs", json.dumps(CHAT_TEMPLATE_KWARGS),
            "--reasoning-budget", "0",      # sin razonamiento, igual que enable_thinking=False
            "--no-webui",
            *extra_args,
        ]
        self.log_path = log_path

    def __enter__(self):
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        self._log = open(self.log_path, "w")
        env = dict(os.environ)
        bindir = os.path.dirname(os.path.abspath(self.cmd[0]))
        env["LD_LIBRARY_PATH"] = bindir + os.pathsep + env.get("LD_LIBRARY_PATH", "")
        print("[+] " + " ".join(self.cmd))
        self.proc = subprocess.Popen(self.cmd, stdout=self._log, stderr=subprocess.STDOUT, env=env)
        t0 = time.perf_counter()
        while time.perf_counter() - t0 < 600:
            if self.proc.poll() is not None:
                raise RuntimeError(f"llama-server terminó al arrancar (código {self.proc.returncode}); mira {self.log_path}")
            try:
                with urllib.request.urlopen(f"{self.url}/health", timeout=2) as r:
                    if r.status == 200:
                        self.t_carga = time.perf_counter() - t0
                        return self
            except (urllib.error.URLError, ConnectionError, TimeoutError):
                pass
            time.sleep(0.5)
        raise RuntimeError(f"llama-server no respondió en 10 min; mira {self.log_path}")

    def __exit__(self, *exc):
        self.proc.terminate()
        try:
            self.proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            self.proc.kill()
        self._log.close()

    def version(self):
        try:
            with urllib.request.urlopen(f"{self.url}/props", timeout=5) as r:
                return json.load(r).get("build_info")
        except Exception:  # noqa: BLE001
            return None


class Generador:
    """Misma interfaz y mismas medidas que el Generador de benchmark_llms_vllm.py."""

    def __init__(self, server):
        self.server = server

    def _chat(self, mensajes, max_tokens):
        cuerpo = {
            "messages": mensajes, "temperature": TEMPERATURA, "max_tokens": max_tokens, "seed": SEED,
            "stream": False, "cache_prompt": False, "chat_template_kwargs": CHAT_TEMPLATE_KWARGS,
        }
        req = urllib.request.Request(f"{self.server.url}/v1/chat/completions", data=json.dumps(cuerpo).encode(),
                                     headers={"Content-Type": "application/json"})
        t0 = time.perf_counter()
        with urllib.request.urlopen(req, timeout=600) as r:
            out = json.load(r)
        return out, time.perf_counter() - t0

    def generar(self, mensajes, medir_ttft=False):
        ttft = None
        if medir_ttft:
            _, ttft = self._chat(mensajes, 1)
        out, total = self._chat(mensajes, MAX_TOKENS_SALIDA)
        ch = out["choices"][0]
        msg = ch["message"]
        texto = msg.get("content") or ""
        pensado = msg.get("reasoning_content") or ""
        if "<think>" in texto:
            import re
            m = re.search(r"<think>(.*?)</think>", texto, flags=re.S)
            if m:
                pensado += m.group(1)
            texto = re.sub(r"<think>.*?(</think>|$)", "", texto, flags=re.S)
        uso = out.get("usage", {})
        n_out = uso.get("completion_tokens", 0)
        tps = (n_out - 1) / (total - ttft) if ttft is not None and n_out > 1 and total > ttft else None
        return {
            "respuesta": texto.strip(),
            "razonamiento_detectado": bool(pensado.strip()),
            "ttft_s": round(ttft, 4) if ttft is not None else None,
            "latencia_total_s": round(total, 4),
            "tokens_salida": n_out,
            "tokens_por_s": round(tps, 2) if tps else None,
            "tokens_prompt": uso.get("prompt_tokens", 0),
            "finish_reason": ch.get("finish_reason"),
            "timings_llama_cpp": out.get("timings"),   # medidas internas del servidor, solo como referencia
        }


# ---------------------------------------------------------------------------
# Benchmark de un modelo en un escenario
# ---------------------------------------------------------------------------
def run(model_key, scen_key, binario, oraculo=True, n_coste=5, rondas=3, extra_args=()):
    import torch

    cfg, scen = MODELOS[model_key], SCENARIOS[scen_key]
    emb = EMBEDDING_GANADOR[scen_key]
    print(f"\n{'=' * 70}\nPlan B · {model_key} ({cfg['repo']}/{cfg['archivo']}) | {scen['name']} | Embedding: {emb}\n{'=' * 70}")

    gguf = descargar_gguf(cfg)
    chunks_por_id = {c["id"]: c for c in cargar_json(scen["chunks_path"])}
    golden = cargar_jsonl(scen["golden_path"])
    retrieval = {q["id"]: [r["chunk_id"] for r in q["top5"]][:TOP_K]
                 for q in cargar_json(f"results/embeddings/data/{emb}_{scen_key}.json")["questions"]}
    os.makedirs(f"{DIR_OUT}/data", exist_ok=True)

    torch.cuda.init()   # el contexto CUDA de este proceso entra en la base, no en la cifra del LLM
    vram_base_gb = round(VRAMMonitor.usada_bytes() / 2**30, 3)
    vram = VRAMMonitor(f"{DIR_OUT}/logs/vram_{model_key}_{scen_key}.log")
    vram.start()

    try:
        with LlamaServer(binario, gguf, f"{DIR_OUT}/logs/llama_server_{model_key}_{scen_key}.log", extra_args) as srv:
            build = srv.version()
            gen = Generador(srv)
            print(f"[+] Cargado en {srv.t_carga:.1f} s")
            gen.generar([{"role": "user", "content": "Hola"}])   # calentamiento, no se mide

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
                        "cortado_por_max_tokens": r["finish_reason"] == "length",
                        **r,
                    })
                    print(f"  [{modo}] {q['id']}: {r['respuesta'][:90]!r}")

            qs = preguntas_coste(golden, n_coste)
            medidas = {q["id"]: [] for q in qs}
            for ronda in range(rondas + 1):
                for q in qs:
                    r = gen.generar(construir_mensajes(scen_key, q["pregunta"], retrieval[q["id"]], chunks_por_id),
                                    medir_ttft=True)
                    if ronda > 0:
                        medidas[q["id"]].append(r)
                print(f"  [coste] ronda {ronda}{' (descartada)' if ronda == 0 else ''} hecha")
            t_carga = srv.t_carga
            cmd = srv.cmd
    finally:
        vram_pico_gb = vram.stop()

    def med(campo, lista):
        vals = [x[campo] for x in lista if x[campo] is not None]
        return round(statistics.median(vals), 4) if vals else None

    campos = ("ttft_s", "tokens_por_s", "latencia_total_s", "tokens_salida")
    todas = [x for rs in medidas.values() for x in rs]
    coste = {c: med(c, todas) for c in campos}
    # Referencia: lo que mide el propio llama-server en la petición completa (sin el ruido de medir
    # el TTFT en una petición aparte). La tabla usa la fórmula de la Fase 3 para poder comparar.
    interno = [x["timings_llama_cpp"] for x in todas if x.get("timings_llama_cpp")]
    for clave, campo in (("tokens_por_s_llama_cpp", "predicted_per_second"), ("prefill_ms_llama_cpp", "prompt_ms")):
        vals = [t[campo] for t in interno if t.get(campo) is not None]
        coste[clave] = round(statistics.median(vals), 2) if vals else None
    vram_llm_gb = round(vram_pico_gb - vram_base_gb, 3) if vram_pico_gb else None
    total_plan_b = round(vram_llm_gb + EMBEDDING_RETRIEVAL_GB, 2) if vram_llm_gb else None

    meta = {
        "modelo": model_key, "repo": f"{cfg['repo']}/{cfg['archivo']}", "tamano": cfg["tamano"], "categoria": "mediano",
        "modelo_base_fase3": cfg["base"], "cuantizacion": cfg["cuantizacion"], "stack": "llama.cpp",
        "stack_version": LLAMA_CPP_VERSION, "build_info": build, "comando": cmd,
        "torch_version": torch.__version__, "cuda_device": torch.cuda.get_device_name(0),
        "escenario": scen_key, "embedding": emb, "top_k": TOP_K,
        "opciones": {"temperature": TEMPERATURA, "max_tokens": MAX_TOKENS_SALIDA, "max_model_len": MAX_MODEL_LEN,
                     "seed": SEED, "chat_template_kwargs": CHAT_TEMPLATE_KWARGS, "prefix_caching": False},
        "memoria": f"caché KV de llama.cpp para {MAX_MODEL_LEN} tokens (F16)",
        "prompt_sistema": PROMPT_SISTEMA.replace("{cita}", scen["cita"]), "prompt_usuario": PROMPT_USUARIO,
        "timestamp": ahora(), "tiempo_carga_s": round(t_carga, 2),
        "tokens_prompt_max": max((r["tokens_prompt"] for r in respuestas), default=None),
        "vram_base_gb": vram_base_gb, "vram_pico_gb": round(vram_pico_gb, 3) if vram_pico_gb else None,
        "vram_llm_gb": vram_llm_gb, "vram_plan_b_con_embedding_gb": total_plan_b,
        "cabe_en_8gb": total_plan_b is not None and total_plan_b <= LIMITE_PLAN_B_GB,
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
        print("[!] Se detectó razonamiento en alguna respuesta: revisad --reasoning-budget / chat_template_kwargs.")
    print(f"--- {model_key}/{scen_key}: TTFT {coste['ttft_s']} s | {coste['tokens_por_s']} tok/s | "
          f"latencia {coste['latencia_total_s']} s | VRAM LLM {vram_llm_gb} GB "
          f"(+ embedding ≈ {total_plan_b} GB → {'CABE' if meta['cabe_en_8gb'] else 'NO CABE'} en 8 GB) → {path}")


def main():
    ap = argparse.ArgumentParser(description="Plan B (8 GB): LLMs en GGUF con llama.cpp")
    ap.add_argument("--model", default="defecto", choices=list(MODELOS) + ["defecto", "all"],
                    help="defecto = los dos Q4; all = también los Q8 (extra)")
    ap.add_argument("--scenario", default="all", choices=list(SCENARIOS) + ["all"])
    ap.add_argument("--llama-server", default=os.environ.get("LLAMA_SERVER", LLAMA_SERVER_DEFECTO))
    ap.add_argument("--server-args", default="", help="argumentos extra para llama-server, entre comillas")
    ap.add_argument("--sin-oraculo", action="store_true")
    ap.add_argument("--n-coste", type=int, default=5)
    ap.add_argument("--rondas", type=int, default=3)
    a = ap.parse_args()

    if not os.path.exists(a.llama_server):
        sys.exit(f"No encuentro llama-server en {a.llama_server}. Instrucciones de instalación al principio del script.")

    modelos = {"defecto": MODELOS_POR_DEFECTO, "all": list(MODELOS)}.get(a.model, [a.model])
    escenarios = list(SCENARIOS) if a.scenario == "all" else [a.scenario]
    for s in escenarios:
        for m in modelos:
            try:
                run(m, s, a.llama_server, oraculo=not a.sin_oraculo, n_coste=a.n_coste, rondas=a.rondas,
                    extra_args=a.server_args.split())
            except Exception as e:  # noqa: BLE001
                print(f"[!] {m}/{s} falló: {e}; sigo con el siguiente")
    print(f"\nHecho. Siguiente paso: python scripts/generar_tablas_llm.py --dir {DIR_OUT} --plantilla")


if __name__ == "__main__":
    main()
