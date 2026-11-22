# Qwen/Qwen3-1.7B · debian · 2026-11-22T20:27:00

## Tabla B (calidad)
| Modelo | Tamaño | Cuantización | Corrección media (0–2) | Respuestas fieles (%) | Abstención correcta (de 3) | Falsas abstenciones | Formato e idioma (%) |
|---|---|---|---|---|---|---|---|
| Qwen/Qwen3-1.7B | 1.72 B | bf16 | 1.53 | 93 | 3 | 2 (de 12) | 53 |

## Tabla C (coste)
| Modelo | Stack | TTFT (s) | Tokens/s | Latencia total (s) | VRAM pico (GB) |
|---|---|---|---|---|---|
| Qwen/Qwen3-1.7B | transformers 5.23.0 | 0.11 | 51.6 | 1.12 | 3.96 |

## Trazabilidad
- Respuestas y tiempos brutos: `Qwen_Qwen3-1.7B__debian__20261122-202541.jsonl`
- Puntuación a mano (15 respuestas, puntuado por: Nahia (validación manual; pre-puntuación asistida por LLM), Pre-puntuación asistida por LLM (pendiente de validar a mano)): `Qwen_Qwen3-1.7B__debian__20261122-202541_puntuacion.csv`
- Registro de GPU (pico 3.96 GB, nvidia-smi de la instancia): `Qwen_Qwen3-1.7B__debian__20261122-202541_gpu.csv`
- Configuración: `Qwen_Qwen3-1.7B__debian__20261122-202541_meta.json` (top-k 5, fragmentos: retrieval, embedding: ../sendoa/modelos/embeddinggemma-300m, prompt sha256 699851d26936eb1d, temperatura 0, máx. tokens 300)
- Coste: mediana de 3 repeticiones por pregunta (tras calentamiento descartado), y mediana entre las preguntas q_deb_01, q_deb_02, q_deb_09, q_deb_10, q_deb_13
