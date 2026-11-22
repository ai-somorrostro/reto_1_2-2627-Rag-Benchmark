# mistralai/Ministral-3-8B-Instruct-2512 · boe · 2026-11-22T13:33:41

## Tabla B (calidad)
| Modelo | Tamaño | Cuantización | Corrección media (0–2) | Respuestas fieles (%) | Abstención correcta (de 3) | Falsas abstenciones | Formato e idioma (%) |
|---|---|---|---|---|---|---|---|
| mistralai/Ministral-3-8B-Instruct-2512 | 8.92 B | bf16 | 1.8 | 93 | 3 | 0 (de 12) | 100 |

## Tabla C (coste)
| Modelo | Stack | TTFT (s) | Tokens/s | Latencia total (s) | VRAM pico (GB) |
|---|---|---|---|---|---|
| mistralai/Ministral-3-8B-Instruct-2512 | transformers 5.23.0 | 0.43 | 32.3 | 3.78 | 18.39 |

## Trazabilidad
- Respuestas y tiempos brutos: `mistralai_Ministral-3-8B-Instruct-2512__boe__20261122-132937.jsonl`
- Puntuación a mano (15 respuestas, puntuado por: Sendoa): `mistralai_Ministral-3-8B-Instruct-2512__boe__20261122-132937_puntuacion.csv`
- Registro de GPU (pico 18.39 GB, nvidia-smi de la instancia): `mistralai_Ministral-3-8B-Instruct-2512__boe__20261122-132937_gpu.csv`
- Configuración: `mistralai_Ministral-3-8B-Instruct-2512__boe__20261122-132937_meta.json` (top-k 5, fragmentos: retrieval, embedding: Qwen/Qwen3-Embedding-0.6B, prompt sha256 699851d26936eb1d, temperatura 0, máx. tokens 300)
- Coste: mediana de 3 repeticiones por pregunta (tras calentamiento descartado), y mediana entre las preguntas q_boe_01, q_boe_02, q_boe_09, q_boe_10, q_boe_13
