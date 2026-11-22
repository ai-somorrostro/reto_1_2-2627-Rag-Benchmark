# HuggingFaceTB/SmolLM3-3B · boe · 2026-11-22T15:52:30

## Tabla B (calidad)
| Modelo | Tamaño | Cuantización | Corrección media (0–2) | Respuestas fieles (%) | Abstención correcta (de 3) | Falsas abstenciones | Formato e idioma (%) |
|---|---|---|---|---|---|---|---|
| HuggingFaceTB/SmolLM3-3B | 3.08 B | bf16 | 1.4 | 60 | 2 | 0 (de 12) | 73 |

## Tabla C (coste)
| Modelo | Stack | TTFT (s) | Tokens/s | Latencia total (s) | VRAM pico (GB) |
|---|---|---|---|---|---|
| HuggingFaceTB/SmolLM3-3B | transformers 5.23.0 | 0.17 | 52.4 | 3.27 | 6.8 |

## Trazabilidad
- Respuestas y tiempos brutos: `HuggingFaceTB_SmolLM3-3B__boe__20261122-155026.jsonl`
- Puntuación a mano (15 respuestas, puntuado por: Julen (revisión manual)): `HuggingFaceTB_SmolLM3-3B__boe__20261122-155026_puntuacion.csv`
- Registro de GPU (pico 6.8 GB, nvidia-smi de la instancia): `HuggingFaceTB_SmolLM3-3B__boe__20261122-155026_gpu.csv`
- Configuración: `HuggingFaceTB_SmolLM3-3B__boe__20261122-155026_meta.json` (top-k 5, fragmentos: retrieval, embedding: Qwen/Qwen3-Embedding-0.6B, prompt sha256 699851d26936eb1d, temperatura 0, máx. tokens 300)
- Coste: mediana de 3 repeticiones por pregunta (tras calentamiento descartado), y mediana entre las preguntas q_boe_01, q_boe_02, q_boe_09, q_boe_10, q_boe_13
