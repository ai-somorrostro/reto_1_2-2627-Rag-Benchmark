# mistralai/Ministral-3-8B-Instruct-2512 · debian · 2026-11-22T13:41:22

## Tabla B (calidad)
| Modelo | Tamaño | Cuantización | Corrección media (0–2) | Respuestas fieles (%) | Abstención correcta (de 3) | Falsas abstenciones | Formato e idioma (%) |
|---|---|---|---|---|---|---|---|
| mistralai/Ministral-3-8B-Instruct-2512 | 8.92 B | bf16 | 1.47 | 100 | 3 | 4 (de 12) | 100 |

## Tabla C (coste)
| Modelo | Stack | TTFT (s) | Tokens/s | Latencia total (s) | VRAM pico (GB) |
|---|---|---|---|---|---|
| mistralai/Ministral-3-8B-Instruct-2512 | transformers 5.23.0 | 0.51 | 32.3 | 2.61 | 18.52 |

## Trazabilidad
- Respuestas y tiempos brutos: `mistralai_Ministral-3-8B-Instruct-2512__debian__20261122-133613.jsonl`
- Puntuación a mano (15 respuestas, puntuado por: Sendoa): `mistralai_Ministral-3-8B-Instruct-2512__debian__20261122-133613_puntuacion.csv`
- Registro de GPU (pico 18.52 GB, nvidia-smi de la instancia): `mistralai_Ministral-3-8B-Instruct-2512__debian__20261122-133613_gpu.csv`
- Configuración: `mistralai_Ministral-3-8B-Instruct-2512__debian__20261122-133613_meta.json` (top-k 5, fragmentos: retrieval, embedding: Qwen/Qwen3-Embedding-0.6B, prompt sha256 699851d26936eb1d, temperatura 0, máx. tokens 300)
- Coste: mediana de 3 repeticiones por pregunta (tras calentamiento descartado), y mediana entre las preguntas q_deb_01, q_deb_02, q_deb_09, q_deb_10, q_deb_13
