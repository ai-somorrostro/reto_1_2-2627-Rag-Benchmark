# Qwen/Qwen3-1.7B · boe · 2026-11-22T15:48:46

## Tabla B (calidad)
| Modelo | Tamaño | Cuantización | Corrección media (0–2) | Respuestas fieles (%) | Abstención correcta (de 3) | Falsas abstenciones | Formato e idioma (%) |
|---|---|---|---|---|---|---|---|
| Qwen/Qwen3-1.7B | 1.72 B | bf16 | 1.33 | 73 | 3 | 2 (de 12) | 73 |

## Tabla C (coste)
| Modelo | Stack | TTFT (s) | Tokens/s | Latencia total (s) | VRAM pico (GB) |
|---|---|---|---|---|---|
| Qwen/Qwen3-1.7B | transformers 5.23.0 | 0.1 | 51.7 | 1.46 | 4.01 |

## Trazabilidad
- Respuestas y tiempos brutos: `Qwen_Qwen3-1.7B__boe__20261122-154806.jsonl`
- Puntuación a mano (15 respuestas, puntuado por: Nahia (validación manual; pre-puntuación asistida por LLM)): `Qwen_Qwen3-1.7B__boe__20261122-154806_puntuacion.csv`
- Registro de GPU (pico 4.01 GB, nvidia-smi de la instancia): `Qwen_Qwen3-1.7B__boe__20261122-154806_gpu.csv`
- Configuración: `Qwen_Qwen3-1.7B__boe__20261122-154806_meta.json` (top-k 5, fragmentos: retrieval, embedding: Qwen/Qwen3-Embedding-0.6B, prompt sha256 699851d26936eb1d, temperatura 0, máx. tokens 300)
- Coste: mediana de 3 repeticiones por pregunta (tras calentamiento descartado), y mediana entre las preguntas q_boe_01, q_boe_02, q_boe_09, q_boe_10, q_boe_13
