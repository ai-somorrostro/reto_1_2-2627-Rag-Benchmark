"""
Generación de gráficos de benchmark para la presentación de la Fase 4.
Genera figuras PNG/SVG en results/graficos/:
  1. embeddings_comparativa.png: Recall@5 y MRR (BOE vs Debian)
  2. llms_calidad.png: Corrección media y Fidelidad (BOE vs Debian)
  3. llms_coste_velocidad.png: Velocidad de generación (tokens/s) y TTFT
  4. llms_vram_plan_b.png: VRAM (LLM + embedding) frente al límite del Plan B (8 GB): vLLM FP8 y llama.cpp GGUF
  5. retrieval_vs_oraculo.png: Corrección con retrieval vs oráculo
"""

import os
import matplotlib.pyplot as plt
import numpy as np

# Configuración visual limpia
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "figure.titlesize": 14,
})

DIR_OUT = os.path.join(os.path.dirname(__file__), "..", "results", "graficos")
os.makedirs(DIR_OUT, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Embeddings: Recall@5 (Hit y Estricto) y MRR
# ---------------------------------------------------------------------------
def grafico_embeddings():
    modelos = ["bge-m3\n(568M)", "Qwen3-Emb\n(600M)", "harrier-oss\n(600M)"]
    
    # BOE
    recall5_estricto_boe = [0.5833, 0.7500, 1.0000]
    recall5_hit_boe = [0.8333, 0.8333, 1.0000]
    mrr_boe = [0.6983, 0.6991, 0.7361]
    
    # Debian
    recall5_estricto_deb = [0.6667, 0.5833, 0.7500]
    recall5_hit_deb = [0.8333, 0.7500, 0.7500]
    mrr_deb = [0.6219, 0.5769, 0.5573]
    
    x = np.arange(len(modelos))
    width = 0.25

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
    
    # Subplot BOE
    ax1.bar(x - width, recall5_estricto_boe, width, label="Recall@5 (Estricto)", color="#1f77b4")
    ax1.bar(x, recall5_hit_boe, width, label="Recall@5 (Hit)", color="#aec7e8")
    ax1.bar(x + width, mrr_boe, width, label="MRR", color="#2ca02c")
    ax1.set_title("BOE (Estatuto de los Trabajadores)")
    ax1.set_xticks(x)
    ax1.set_xticklabels(modelos)
    ax1.set_ylabel("Métrica (0.0 - 1.0)")
    ax1.set_ylim(0, 1.15)
    ax1.axhline(0.80, color="red", linestyle="--", alpha=0.7, label="Umbral mínimo (0.80)")
    ax1.legend(loc="upper left", frameon=True)
    
    # Subplot Debian
    ax2.bar(x - width, recall5_estricto_deb, width, label="Recall@5 (Estricto)", color="#1f77b4")
    ax2.bar(x, recall5_hit_deb, width, label="Recall@5 (Hit)", color="#aec7e8")
    ax2.bar(x + width, mrr_deb, width, label="MRR", color="#2ca02c")
    ax2.set_title("Debian (Manual del Administrador)")
    ax2.set_xticks(x)
    ax2.set_xticklabels(modelos)
    ax2.axhline(0.80, color="red", linestyle="--", alpha=0.7)
    
    # Destacar ganadores
    ax1.annotate("Ganador BOE: 100%\n(harrier)", xy=(2, 1.0), xytext=(1.4, 1.05),
                 arrowprops=dict(arrowstyle="->", color="black", lw=1.5), fontweight="bold")
    ax2.annotate("Ganador Debian:\nÚnico ≥0.80 Hit", xy=(0, 0.8333), xytext=(0.1, 0.98),
                 arrowprops=dict(arrowstyle="->", color="black", lw=1.5), fontweight="bold")
    
    plt.tight_layout()
    p = os.path.join(DIR_OUT, "embeddings_comparativa.png")
    plt.savefig(p, dpi=200)
    plt.close()
    print(f"Guardado: {p}")

# ---------------------------------------------------------------------------
# 2. LLMs: Calidad (Corrección y Fidelidad)
# ---------------------------------------------------------------------------
def grafico_llm_calidad():
    modelos = ["lfm3-1.7b\n(1.7B)", "llama3.2-3b\n(3B)", "nemotron-bolt\n(8B/4B ef.)", "qwen3.5-9b\n(9B)"]
    
    corr_boe = [0.93, 0.93, 1.60, 1.87]
    fiel_boe = [93, 100, 100, 100]
    
    corr_deb = [0.93, 1.07, 1.53, 1.53]
    fiel_deb = [93, 87, 100, 100]
    
    x = np.arange(len(modelos))
    width = 0.35

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    
    # BOE
    ax1.bar(x - width/2, corr_boe, width, label="BOE (Estatuto)", color="#2b5c8f")
    ax1.bar(x + width/2, corr_deb, width, label="Debian (Manual)", color="#e07a5f")
    ax1.set_title("Corrección media (Escala 0 - 2)")
    ax1.set_xticks(x)
    ax1.set_xticklabels(modelos)
    ax1.set_ylabel("Nota media")
    ax1.set_ylim(0, 2.2)
    ax1.axhline(1.50, color="red", linestyle="--", alpha=0.7, label="Umbral mínimo (1.50)")
    ax1.legend(loc="upper left")
    
    # Fidelidad
    ax2.bar(x - width/2, fiel_boe, width, label="BOE (Estatuto)", color="#2b5c8f")
    ax2.bar(x + width/2, fiel_deb, width, label="Debian (Manual)", color="#e07a5f")
    ax2.set_title("Respuestas Fieles (%)")
    ax2.set_xticks(x)
    ax2.set_xticklabels(modelos)
    ax2.set_ylabel("Porcentaje (%)")
    ax2.set_ylim(70, 105)
    ax2.axhline(80.0, color="red", linestyle="--", alpha=0.7, label="Umbral mínimo (80%)")
    ax2.legend(loc="lower right")

    plt.tight_layout()
    p = os.path.join(DIR_OUT, "llms_calidad.png")
    plt.savefig(p, dpi=200)
    plt.close()
    print(f"Guardado: {p}")

# ---------------------------------------------------------------------------
# 3. LLMs: Coste y Rendimiento (tokens/s vs latencia y TTFT)
# ---------------------------------------------------------------------------
def grafico_llm_coste():
    modelos = ["lfm3-1.7b\n(1.7B)", "llama3.2-3b\n(3B)", "nemotron-bolt\n(8B)", "qwen3.5-9b\n(9B)"]
    
    # Rendimiento
    tps = [63.9, 66.4, 26.7, 45.0]  # Mediana BOE
    ttft = [0.10, 0.20, 0.27, 0.41]
    latencia = [2.80, 0.78, 1.50, 1.35]
    
    x = np.arange(len(modelos))
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    
    # Tokens por segundo
    colores_tps = ["#457b9d", "#1d3557", "#e63946", "#2a9d8f"]
    bars = ax1.bar(x, tps, color=colores_tps, width=0.5)
    ax1.set_title("Velocidad de generación (Tokens/segundo)")
    ax1.set_xticks(x)
    ax1.set_xticklabels(modelos)
    ax1.set_ylabel("Tokens / s")
    ax1.set_ylim(0, 80)
    for b in bars:
        ax1.text(b.get_x() + b.get_width()/2, b.get_height() + 1.5, f"{b.get_height():.1f}",
                 ha="center", va="bottom", fontweight="bold")
    ax1.annotate("Sorpresa 1: Nemotron\nes el más lento (26.7)", xy=(2, 26.7), xytext=(1.4, 45),
                 arrowprops=dict(arrowstyle="->", color="red", lw=1.5), fontweight="bold", color="red")
    
    # TTFT vs Latencia
    w = 0.35
    ax2.bar(x - w/2, ttft, w, label="TTFT (Prefill, s)", color="#f4a261")
    ax2.bar(x + w/2, latencia, w, label="Latencia total (s)", color="#264653")
    ax2.set_title("Tiempos de respuesta (s)")
    ax2.set_xticks(x)
    ax2.set_xticklabels(modelos)
    ax2.set_ylabel("Segundos")
    ax2.set_ylim(0, 3.5)
    ax2.legend(loc="upper left")
    
    plt.tight_layout()
    p = os.path.join(DIR_OUT, "llms_coste_velocidad.png")
    plt.savefig(p, dpi=200)
    plt.close()
    print(f"Guardado: {p}")

# ---------------------------------------------------------------------------
# 4. LLMs: VRAM Pico vs Plan B (8 GB)
# ---------------------------------------------------------------------------
def grafico_vram_plan_b():
    """VRAM del LLM + embedding (~1,1 GB) frente al límite de 8 GB.
    vLLM FP8: Tabla C de results/llms/tablas_b_c.md. llama.cpp GGUF: results/llms/plan_b/tablas_b_c.md."""
    EMB = 1.1
    # (etiqueta, VRAM del LLM, cumple los umbrales de calidad en los dos escenarios)
    datos = [
        ("lfm3-1.7b\nvLLM FP8", 5.36, False),
        ("llama3.2-3b\nvLLM FP8", 7.07, False),
        ("nemotron\nvLLM FP8", 14.80, True),
        ("qwen3.5-9b\nvLLM FP8", 14.27, True),
        ("nemotron\nGGUF Q4", 3.47, True),
        ("qwen3.5-9b\nGGUF Q4", 5.38, True),
        ("nemotron\nGGUF Q8", 5.19, True),
        ("qwen3.5-9b\nGGUF Q8", 8.49, True),
    ]
    total = [v + EMB for _, v, _ in datos]
    colores = ["#e76f51" if t > 8.0 else ("#2a9d8f" if ok else "#adb5bd") for t, (_, _, ok) in zip(total, datos)]

    x = np.arange(len(datos))
    fig, ax = plt.subplots(figsize=(11, 5.2))
    bars = ax.bar(x, total, color=colores, width=0.6)
    ax.axhline(8.0, color="crimson", linestyle="--", lw=2)
    ax.text(7.45, 8.25, "límite Plan B: 8 GB", color="crimson", ha="right", fontweight="bold")
    ax.axvline(3.5, color="#6c757d", lw=1)
    ax.text(1.5, 17.3, "Fase 3: vLLM 0.34 (FP8)", ha="center", color="#495057", fontweight="bold")
    ax.text(5.5, 17.3, "Plan B: llama.cpp b12633 (GGUF)", ha="center", color="#495057", fontweight="bold")
    ax.set_title("VRAM del LLM + embedding del retrieval (~1,1 GB)", pad=26)
    ax.set_xticks(x)
    ax.set_xticklabels([d[0] for d in datos])
    ax.set_ylabel("VRAM (GB)")
    ax.set_ylim(0, 18.5)
    for b, t in zip(bars, total):
        ax.text(b.get_x() + b.get_width() / 2, t + 0.25, f"{t:.1f}", ha="center", va="bottom", fontweight="bold")

    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color="#2a9d8f", label="Cumple calidad y cabe en 8 GB"),
                       Patch(color="#adb5bd", label="Cabe, pero no cumple calidad"),
                       Patch(color="#e76f51", label="No cabe en 8 GB")],
              loc="upper left", bbox_to_anchor=(0.0, 0.93), fontsize=9)

    plt.tight_layout()
    p = os.path.join(DIR_OUT, "llms_vram_plan_b.png")
    plt.savefig(p, dpi=200)
    plt.close()
    print(f"Guardado: {p}")

# ---------------------------------------------------------------------------
# 5. Retrieval frente a Oráculo (Impacto del contexto y ruido)
# ---------------------------------------------------------------------------
def grafico_retrieval_oraculo():
    modelos = ["lfm3-1.7b", "llama3.2-3b", "nemotron-bolt", "qwen3.5-9b"]
    
    # BOE
    ret_boe = [0.67, 0.67, 1.50, 1.83]
    ora_boe = [1.25, 0.92, 1.75, 2.00]
    
    # Debian
    ret_deb = [0.67, 0.83, 1.42, 1.42]
    ora_deb = [1.00, 1.17, 1.75, 1.83]
    
    x = np.arange(len(modelos))
    width = 0.35
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
    
    # BOE
    ax1.bar(x - width/2, ret_boe, width, label="Con Retrieval (Top-5)", color="#457b9d")
    ax1.bar(x + width/2, ora_boe, width, label="Con Oráculo (Chunk exacto)", color="#2a9d8f")
    ax1.set_title("BOE: Retrieval vs Oráculo")
    ax1.set_xticks(x)
    ax1.set_xticklabels(modelos, rotation=15)
    ax1.set_ylabel("Corrección media")
    ax1.set_ylim(0, 2.2)
    ax1.legend(loc="upper left")
    
    # Debian
    ax2.bar(x - width/2, ret_deb, width, label="Con Retrieval (Top-5)", color="#457b9d")
    ax2.bar(x + width/2, ora_deb, width, label="Con Oráculo (Chunk exacto)", color="#2a9d8f")
    ax2.set_title("Debian: Retrieval vs Oráculo")
    ax2.set_xticks(x)
    ax2.set_xticklabels(modelos, rotation=15)
    
    plt.tight_layout()
    p = os.path.join(DIR_OUT, "retrieval_vs_oraculo.png")
    plt.savefig(p, dpi=200)
    plt.close()
    print(f"Guardado: {p}")

if __name__ == "__main__":
    grafico_embeddings()
    grafico_llm_calidad()
    grafico_llm_coste()
    grafico_vram_plan_b()
    grafico_retrieval_oraculo()
    print("Todos los gráficos generados con éxito en results/graficos/")
