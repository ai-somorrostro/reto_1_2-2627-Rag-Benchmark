# Qwen/Qwen3-8B · debian · 2026-11-22T20:33:57

## Tabla B (calidad)
| Modelo | Tamaño | Cuantización | Corrección media (0–2) | Respuestas fieles (%) | Abstención correcta (de 3) | Falsas abstenciones | Formato e idioma (%) |
|---|---|---|---|---|---|---|---|
| Qwen/Qwen3-8B | 8.19 B | bf16 | 1.6 | 93 | 3 | 2 (de 12) | 67 |

## Tabla C (coste)
| Modelo | Stack | TTFT (s) | Tokens/s | Latencia total (s) | VRAM pico (GB) |
|---|---|---|---|---|---|
| Qwen/Qwen3-8B | transformers 5.23.0 | 0.41 | 31.5 | 3.7 | 16.48 |

## Trazabilidad
- Respuestas y tiempos brutos: `Qwen_Qwen3-8B__debian__20261122-203013.jsonl`
- Puntuación a mano (15 respuestas, puntuado por: Mikel (revisión manual), Pre-puntuación asistida por LLM (pendiente de validar a mano)): `Qwen_Qwen3-8B__debian__20261122-203013_puntuacion.csv`
- Registro de GPU (pico 16.48 GB, nvidia-smi de la instancia): `Qwen_Qwen3-8B__debian__20261122-203013_gpu.csv`
- Configuración: `Qwen_Qwen3-8B__debian__20261122-203013_meta.json` (top-k 5, fragmentos: retrieval, embedding: ../sendoa/modelos/embeddinggemma-300m, prompt sha256 699851d26936eb1d, temperatura 0, máx. tokens 300)
- Coste: mediana de 3 repeticiones por pregunta (tras calentamiento descartado), y mediana entre las preguntas q_deb_01, q_deb_02, q_deb_09, q_deb_10, q_deb_13
