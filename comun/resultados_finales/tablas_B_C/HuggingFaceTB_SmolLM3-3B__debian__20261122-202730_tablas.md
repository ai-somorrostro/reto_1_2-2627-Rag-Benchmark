# HuggingFaceTB/SmolLM3-3B · debian · 2026-11-22T20:29:30

## Tabla B (calidad)
| Modelo | Tamaño | Cuantización | Corrección media (0–2) | Respuestas fieles (%) | Abstención correcta (de 3) | Falsas abstenciones | Formato e idioma (%) |
|---|---|---|---|---|---|---|---|
| HuggingFaceTB/SmolLM3-3B | 3.08 B | bf16 | 1.4 | 73 | 3 | 1 (de 12) | 33 |

## Tabla C (coste)
| Modelo | Stack | TTFT (s) | Tokens/s | Latencia total (s) | VRAM pico (GB) |
|---|---|---|---|---|---|
| HuggingFaceTB/SmolLM3-3B | transformers 5.23.0 | 0.18 | 52.3 | 1.44 | 6.56 |

## Trazabilidad
- Respuestas y tiempos brutos: `HuggingFaceTB_SmolLM3-3B__debian__20261122-202730.jsonl`
- Puntuación a mano (15 respuestas, puntuado por: Julen (revisión manual), Pre-puntuación asistida por LLM (pendiente de validar a mano)): `HuggingFaceTB_SmolLM3-3B__debian__20261122-202730_puntuacion.csv`
- Registro de GPU (pico 6.56 GB, nvidia-smi de la instancia): `HuggingFaceTB_SmolLM3-3B__debian__20261122-202730_gpu.csv`
- Configuración: `HuggingFaceTB_SmolLM3-3B__debian__20261122-202730_meta.json` (top-k 5, fragmentos: retrieval, embedding: ../sendoa/modelos/embeddinggemma-300m, prompt sha256 699851d26936eb1d, temperatura 0, máx. tokens 300)
- Coste: mediana de 3 repeticiones por pregunta (tras calentamiento descartado), y mediana entre las preguntas q_deb_01, q_deb_02, q_deb_09, q_deb_10, q_deb_13
