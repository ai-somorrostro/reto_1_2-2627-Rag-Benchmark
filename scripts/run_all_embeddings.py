#!/usr/bin/env python3
"""
Orquestador del Benchmark de Modelos de Embedding con vLLM.
Ejecuta cada modelo y escenario en un proceso independiente para garantizar
aislamiento total de memoria GPU y trazabilidad estricta.
Genera la Tabla A oficial en Markdown (results/embeddings/tabla_a_embeddings.md).
"""

import os
import sys
import json
import subprocess
from datetime import datetime

MODELS = ["bge-m3", "qwen3-embedding", "harrier-oss-v1"]
SCENARIOS = ["boe", "debian"]

def run_single(model, scenario):
    cmd = [
        sys.executable,
        "scripts/benchmark_embeddings_vllm.py",
        "--model", model,
        "--scenario", scenario
    ]
    print(f"\n======================================================================")
    print(f"Lanzando proceso: Modelo={model} | Escenario={scenario}")
    print(f"======================================================================")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"[!] Error ejecutando {model} en {scenario}. Código de salida: {result.returncode}")
        sys.exit(result.returncode)

def generate_markdown_report():
    print("\nGenerando informe consolidado en Markdown...")
    all_results = {}
    for s in SCENARIOS:
        all_results[s] = []
        for m in MODELS:
            res_file = f"results/embeddings/data/{m}_{s}.json"
            if os.path.exists(res_file):
                with open(res_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    all_results[s].append(data["summary"])

    md = []
    md.append("# Resultados del Benchmark de Modelos de Embedding Locales con vLLM")
    md.append(f"\n**Fecha y hora:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    md.append("**Stack de inferencia:** vLLM v0.34.0 (PyTorch 2.14.0+cu130)")
    md.append("**Hardware:** NVIDIA A800 40GB Active (Instancia MIG 3g.20gb)")
    md.append("**Modo de ejecución:** Eager mode (`enforce_eager=True`, `max_model_len=8192`)")
    md.append("\n---\n")

    for s in SCENARIOS:
        scen_name = "1. Normativa larga: Estatuto de los Trabajadores (BOE)" if s == "boe" else "2. Documentación técnica: Manual del Administrador de Debian (Debian)"
        md.append(f"## Escenario {scen_name}\n")
        md.append("### Tabla A. Embeddings (Criterio estricto: en preguntas combinadas ambos chunks deben estar en top-k)\n")
        md.append("| Modelo | Parámetros | Dimensión | Recall@1 | Recall@3 | Recall@5 | MRR | Indexado (s) | Índice (MB) | VRAM pico (GB) |")
        md.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        for res in all_results[s]:
            repo = res["model_repo"]
            params = res["parameters"]
            dim = res["dimension"]
            r1 = f"{res['recall_at_1_all']:.4f}"
            r3 = f"{res['recall_at_3_all']:.4f}"
            r5 = f"{res['recall_at_5_all']:.4f}"
            mrr = f"{res['mrr']:.4f}"
            idx_t = f"{res['index_time_sec']:.2f}"
            idx_sz = f"{res['index_size_mb']:.2f}"
            vram = f"{res['vram_peak_gb']:.3f}"
            md.append(f"| `{repo}` | {params} | {dim} | {r1} | {r3} | **{r5}** | {mrr} | {idx_t} | {idx_sz} | {vram} |")

        md.append("\n### Tabla A (Bis). Embeddings con criterio Hit (al menos 1 chunk relevante en top-k)\n")
        md.append("| Modelo | Parámetros | Dimensión | Recall@1 (Hit) | Recall@3 (Hit) | Recall@5 (Hit) | MRR | Indexado (s) | Índice (MB) | VRAM pico (GB) |")
        md.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        for res in all_results[s]:
            repo = res["model_repo"]
            params = res["parameters"]
            dim = res["dimension"]
            r1 = f"{res['recall_at_1_hit']:.4f}"
            r3 = f"{res['recall_at_3_hit']:.4f}"
            r5 = f"{res['recall_at_5_hit']:.4f}"
            mrr = f"{res['mrr']:.4f}"
            idx_t = f"{res['index_time_sec']:.2f}"
            idx_sz = f"{res['index_size_mb']:.2f}"
            vram = f"{res['vram_peak_gb']:.3f}"
            md.append(f"| `{repo}` | {params} | {dim} | {r1} | {r3} | **{r5}** | {mrr} | {idx_t} | {idx_sz} | {vram} |")

        md.append("\n---\n")

    report_path = "results/embeddings/tabla_a_embeddings.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print(f"[+] Informe guardado en: {report_path}")

def main():
    for s in SCENARIOS:
        for m in MODELS:
            run_single(m, s)
    generate_markdown_report()

if __name__ == "__main__":
    main()
