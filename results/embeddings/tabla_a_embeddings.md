# Resultados del Benchmark de Modelos de Embedding Locales con vLLM

**Fecha y hora:** 2026-11-19 07:53:44
**Stack de inferencia:** vLLM v0.34.0 (PyTorch 2.14.0+cu130)
**Hardware:** NVIDIA A800 40GB Active (Instancia MIG 3g.20gb)
**Modo de ejecución:** Eager mode (`enforce_eager=True`, `max_model_len=8192`)

---

## Escenario 1. Normativa larga: Estatuto de los Trabajadores (BOE)

### Tabla A. Embeddings (Criterio estricto: en preguntas combinadas ambos chunks deben estar en top-k)

| Modelo | Parámetros | Dimensión | Recall@1 | Recall@3 | Recall@5 | MRR | Indexado (s) | Índice (MB) | VRAM pico (GB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `BAAI/bge-m3` | 568M | 1024 | 0.3333 | 0.5000 | **0.5833** | 0.6983 | 1.06 | 1.36 | 1.888 |
| `Qwen/Qwen3-Embedding-0.6B` | 600M | 1024 | 0.3333 | 0.6667 | **0.7500** | 0.6991 | 1.59 | 1.36 | 3.507 |
| `microsoft/harrier-oss-v1-0.6b` | 600M | 1024 | 0.2500 | 0.6667 | **1.0000** | 0.7361 | 1.60 | 1.36 | 3.507 |

### Tabla A (Bis). Embeddings con criterio Hit (al menos 1 chunk relevante en top-k)

| Modelo | Parámetros | Dimensión | Recall@1 (Hit) | Recall@3 (Hit) | Recall@5 (Hit) | MRR | Indexado (s) | Índice (MB) | VRAM pico (GB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `BAAI/bge-m3` | 568M | 1024 | 0.5833 | 0.7500 | **0.8333** | 0.6983 | 1.06 | 1.36 | 1.888 |
| `Qwen/Qwen3-Embedding-0.6B` | 600M | 1024 | 0.5833 | 0.8333 | **0.8333** | 0.6991 | 1.59 | 1.36 | 3.507 |
| `microsoft/harrier-oss-v1-0.6b` | 600M | 1024 | 0.5000 | 1.0000 | **1.0000** | 0.7361 | 1.60 | 1.36 | 3.507 |

---

## Escenario 2. Documentación técnica: Manual del Administrador de Debian (Debian)

### Tabla A. Embeddings (Criterio estricto: en preguntas combinadas ambos chunks deben estar en top-k)

| Modelo | Parámetros | Dimensión | Recall@1 | Recall@3 | Recall@5 | MRR | Indexado (s) | Índice (MB) | VRAM pico (GB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `BAAI/bge-m3` | 568M | 1024 | 0.3333 | 0.5000 | **0.6667** | 0.6219 | 3.52 | 4.15 | 1.902 |
| `Qwen/Qwen3-Embedding-0.6B` | 600M | 1024 | 0.2500 | 0.5000 | **0.5833** | 0.5769 | 5.29 | 4.15 | 3.492 |
| `microsoft/harrier-oss-v1-0.6b` | 600M | 1024 | 0.2500 | 0.5000 | **0.7500** | 0.5573 | 5.34 | 4.15 | 3.505 |

### Tabla A (Bis). Embeddings con criterio Hit (al menos 1 chunk relevante en top-k)

| Modelo | Parámetros | Dimensión | Recall@1 (Hit) | Recall@3 (Hit) | Recall@5 (Hit) | MRR | Indexado (s) | Índice (MB) | VRAM pico (GB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `BAAI/bge-m3` | 568M | 1024 | 0.5000 | 0.6667 | **0.8333** | 0.6219 | 3.52 | 4.15 | 1.902 |
| `Qwen/Qwen3-Embedding-0.6B` | 600M | 1024 | 0.4167 | 0.6667 | **0.7500** | 0.5769 | 5.29 | 4.15 | 3.492 |
| `microsoft/harrier-oss-v1-0.6b` | 600M | 1024 | 0.4167 | 0.5833 | **0.7500** | 0.5573 | 5.34 | 4.15 | 3.505 |

---
