# Qwen/Qwen3-8B · boe · 2026-11-22T20:47:12

## Tabla B (calidad)
| Modelo | Tamaño | Cuantización | Corrección media (0–2) | Respuestas fieles (%) | Abstención correcta (de 3) | Falsas abstenciones | Formato e idioma (%) |
|---|---|---|---|---|---|---|---|
| Qwen/Qwen3-8B | 8.19 B | bf16 | 2.0 | 100 | 3 | 0 (de 12) | 100 |

## Tabla C (coste)
| Modelo | Stack | TTFT (s) | Tokens/s | Latencia total (s) | VRAM pico (GB) |
|---|---|---|---|---|---|
| Qwen/Qwen3-8B | transformers 5.23.0 | 0.37 | 31.9 | 3.79 | 16.57 |

## Trazabilidad
- Respuestas y tiempos brutos: `Qwen_Qwen3-8B__boe__20261122-204343.jsonl`
- Puntuación a mano (15 respuestas, puntuado por: Mikel (revisión manual)): `Qwen_Qwen3-8B__boe__20261122-204343_puntuacion.csv`
- Registro de GPU (pico 16.57 GB, nvidia-smi de la instancia): `Qwen_Qwen3-8B__boe__20261122-204343_gpu.csv`
- Configuración: `Qwen_Qwen3-8B__boe__20261122-204343_meta.json` (top-k 5, fragmentos: retrieval, embedding: Qwen/Qwen3-Embedding-0.6B, prompt sha256 699851d26936eb1d, temperatura 0, máx. tokens 300)
- Coste: mediana de 3 repeticiones por pregunta (tras calentamiento descartado), y mediana entre las preguntas q_boe_01, q_boe_02, q_boe_09, q_boe_10, q_boe_13
