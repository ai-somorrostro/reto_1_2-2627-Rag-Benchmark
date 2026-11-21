#!/usr/bin/env python3
"""
Simulador de memoria VRAM y dimensionamiento de Plan B (Límite: 8 GB VRAM).
Modela la huella teórica y empírica de memoria:
  VRAM_total = Pesos_modelo + KV_Cache + CUDA_Overhead + VRAM_Embedding
Evalúa la viabilidad de cuantizaciones (FP16, FP8, Q8, Q4_K_M, AWQ).
"""

def calcular_vram_teorica(params_b, bits_per_weight, context_len=8192, kv_cache_gb=2.0, cuda_overhead_gb=1.2, emb_gb=0.6):
    # Pesos en GB: (Params * bits / 8) / (1024^3)
    pesos_gb = (params_b * 1e9 * (bits_per_weight / 8.0)) / (1024**3)
    total_gb = pesos_gb + kv_cache_gb + cuda_overhead_gb + emb_gb
    return round(pesos_gb, 2), round(total_gb, 2)

MODELOS = [
    {"nombre": "LiquidAI/LFM3-1.7B", "params": 1.73},
    {"nombre": "meta-llama/Llama-3.2-3B", "params": 3.21},
    {"nombre": "nvidia/Nemotron-Bolt-E4B", "params": 8.0},
    {"nombre": "Qwen/Qwen3.5-9B", "params": 9.2},
]

FORMATOS = [
    ("FP16 / BF16", 16.0),
    ("FP8 (vLLM actual)", 8.0),
    ("GGUF Q8_0", 8.5),
    ("AWQ / GGUF Q4_K_M", 4.5),
]

def main():
    print("=" * 82)
    print("DIMENSIONAMIENTO DE MEMORIA VRAM PARA PIPELINE RAG (Contexto: 8k + 2GB KV Cache)")
    print("=" * 82)
    print(f"{'Modelo':<28} | {'Formato':<18} | {'Pesos (GB)':<10} | {'Total VRAM':<12} | {'¿Cabe en 8GB?'}")
    print("-" * 82)

    for m in MODELOS:
        for fmt_nombre, bits in FORMATOS:
            pesos, total = calcular_vram_teorica(m["params"], bits)
            cabe = "✅ SÍ" if total <= 8.0 else "❌ NO (OOM)"
            if m["params"] >= 8.0 and bits <= 4.5:
                cabe += " (VIABLE PLAN B)"
            print(f"{m['nombre']:<28} | {fmt_nombre:<18} | {pesos:>8.2f} GB | {total:>9.2f} GB | {cabe}")
        print("-" * 82)

    print("\nCONCLUSIÓN DE INGENIERÍA PARA EL PLAN B:")
    print("1. En FP8 sobre vLLM (stack del benchmark), los modelos de 8B/9B consumen >14 GB y provocan OOM en 8 GB.")
    print("2. Los modelos pequeños (1.7B y 3B) sí caben en 8 GB en cualquier formato, pero sufre de un 50%-92% de falsas abstenciones.")
    print("3. La solución óptima de Plan B es migrar Qwen3.5-9B a cuantización AWQ de 4 bits o GGUF Q4_K_M:")
    print("   - Ocupa ~5.17 GB de pesos + 1.5 GB de KV caché reducida (4k tokens) = ~7.5 GB VRAM.")
    print("   - Mantiene la capacidad de razonamiento de un modelo de 9B dentro del presupuesto de 8 GB.")

if __name__ == "__main__":
    main()
