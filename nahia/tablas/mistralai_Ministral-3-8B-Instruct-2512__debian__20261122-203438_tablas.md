# mistralai/Ministral-3-8B-Instruct-2512 · debian · 2026-11-22T20:38:52

## Tabla B (calidad)
| Modelo | Tamaño | Cuantización | Corrección media (0–2) | Respuestas fieles (%) | Abstención correcta (de 3) | Falsas abstenciones | Formato e idioma (%) |
|---|---|---|---|---|---|---|---|
| mistralai/Ministral-3-8B-Instruct-2512 | 8.92 B | bf16 | 1.6 | 100 | 3 | 3 (de 12) | 100 |

## Tabla C (coste)
| Modelo | Stack | TTFT (s) | Tokens/s | Latencia total (s) | VRAM pico (GB) |
|---|---|---|---|---|---|
| mistralai/Ministral-3-8B-Instruct-2512 | transformers 5.23.0 | 0.49 | 32.0 | 4.55 | 18.44 |

## Trazabilidad
- Respuestas y tiempos brutos: `mistralai_Ministral-3-8B-Instruct-2512__debian__20261122-203438.jsonl`
- Puntuación a mano (15 respuestas, puntuado por: Nahia (validación manual; pre-puntuación asistida por LLM), Sendoa (revisión manual)): `mistralai_Ministral-3-8B-Instruct-2512__debian__20261122-203438_puntuacion.csv`
- Registro de GPU (pico 18.44 GB, nvidia-smi de la instancia): `mistralai_Ministral-3-8B-Instruct-2512__debian__20261122-203438_gpu.csv`
- Configuración: `mistralai_Ministral-3-8B-Instruct-2512__debian__20261122-203438_meta.json` (top-k 5, fragmentos: retrieval, embedding: ../sendoa/modelos/embeddinggemma-300m, prompt sha256 699851d26936eb1d, temperatura 0, máx. tokens 300)
- Coste: mediana de 3 repeticiones por pregunta (tras calentamiento descartado), y mediana entre las preguntas q_deb_01, q_deb_02, q_deb_09, q_deb_10, q_deb_13
