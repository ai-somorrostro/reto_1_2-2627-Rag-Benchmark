# Qwen/Qwen3-8B · boe · 2026-11-22T21:18:54

## Tabla B (calidad)
| Modelo | Tamaño | Cuantización | Corrección media (0–2) | Respuestas fieles (%) | Abstención correcta (de 3) | Falsas abstenciones | Formato e idioma (%) |
|---|---|---|---|---|---|---|---|
| Qwen/Qwen3-8B | 4.72 B | nf4 | 2.0 | 100 | 3 | 0 (de 12) | 100 |

## Tabla C (coste)
| Modelo | Stack | TTFT (s) | Tokens/s | Latencia total (s) | VRAM pico (GB) |
|---|---|---|---|---|---|
| Qwen/Qwen3-8B | transformers 5.23.0 | 0.4 | 28.5 | 4.13 | 7.08 |

## Trazabilidad
- Respuestas y tiempos brutos: `Qwen_Qwen3-8B-nf4__boe__20261122-211519.jsonl`
- Puntuación a mano (15 respuestas, puntuado por: Mikel (revisión manual), Nahia (validación manual; pre-puntuación asistida por LLM)): `Qwen_Qwen3-8B-nf4__boe__20261122-211519_puntuacion.csv`
- Registro de GPU (pico 7.08 GB, nvidia-smi de la instancia): `Qwen_Qwen3-8B-nf4__boe__20261122-211519_gpu.csv`
- Configuración: `Qwen_Qwen3-8B-nf4__boe__20261122-211519_meta.json` (top-k 5, fragmentos: retrieval, embedding: Qwen/Qwen3-Embedding-0.6B, prompt sha256 699851d26936eb1d, temperatura 0, máx. tokens 300)
- Coste: mediana de 3 repeticiones por pregunta (tras calentamiento descartado), y mediana entre las preguntas q_boe_01, q_boe_02, q_boe_09, q_boe_10, q_boe_13
