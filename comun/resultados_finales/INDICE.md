# Índice de trazabilidad: de dónde sale cada cifra

Todos los ficheros brutos están en `nahia/resultados/` (LLMs) y `sendoa/resultados_oficiales/` (embeddings). Datos congelados: `comun/chunks_*.json`, `comun/golden_set_*.json`; prompt: `comun/prompt.py`; umbrales: `comun/umbrales.md`.

## Tabla A (embeddings)
Ver `tabla_A/tabla_a_boe.md` y `tabla_A/tabla_a_debian.md`: la última columna indica el JSON de origen de cada fila (en `sendoa/resultados_oficiales/`). Embeddings ganadores en `ganadores_embedding.json`.

## Tablas B y C (LLMs): una por ejecución final

| Modelo | Escenario | Tablas | Respuestas y tiempos | GPU | Ficha | Hoja de puntuación | Puntuado por |
|---|---|---|---|---|---|---|---|
| HuggingFaceTB/SmolLM3-3B | boe | `tablas_B_C/HuggingFaceTB_SmolLM3-3B__boe__20261122-155026_tablas.md` | `HuggingFaceTB_SmolLM3-3B__boe__20261122-155026.jsonl` | `HuggingFaceTB_SmolLM3-3B__boe__20261122-155026_gpu.csv` | `HuggingFaceTB_SmolLM3-3B__boe__20261122-155026_meta.json` | `HuggingFaceTB_SmolLM3-3B__boe__20261122-155026_puntuacion.csv` | Julen (revisión manual) |
| HuggingFaceTB/SmolLM3-3B | debian | `tablas_B_C/HuggingFaceTB_SmolLM3-3B__debian__20261122-155307_tablas.md` | `HuggingFaceTB_SmolLM3-3B__debian__20261122-155307.jsonl` | `HuggingFaceTB_SmolLM3-3B__debian__20261122-155307_gpu.csv` | `HuggingFaceTB_SmolLM3-3B__debian__20261122-155307_meta.json` | `HuggingFaceTB_SmolLM3-3B__debian__20261122-155307_puntuacion.csv` | Julen (revisión manual) |
| Qwen/Qwen3-1.7B | boe | `tablas_B_C/Qwen_Qwen3-1.7B__boe__20261122-154806_tablas.md` | `Qwen_Qwen3-1.7B__boe__20261122-154806.jsonl` | `Qwen_Qwen3-1.7B__boe__20261122-154806_gpu.csv` | `Qwen_Qwen3-1.7B__boe__20261122-154806_meta.json` | `Qwen_Qwen3-1.7B__boe__20261122-154806_puntuacion.csv` | Nahia (validación manual; pre-puntuación asistida por LLM) |
| Qwen/Qwen3-1.7B | debian | `tablas_B_C/Qwen_Qwen3-1.7B__debian__20261122-154916_tablas.md` | `Qwen_Qwen3-1.7B__debian__20261122-154916.jsonl` | `Qwen_Qwen3-1.7B__debian__20261122-154916_gpu.csv` | `Qwen_Qwen3-1.7B__debian__20261122-154916_meta.json` | `Qwen_Qwen3-1.7B__debian__20261122-154916_puntuacion.csv` | Nahia (validación manual; pre-puntuación asistida por LLM) |
| Qwen/Qwen3-8B | boe | `tablas_B_C/Qwen_Qwen3-8B__boe__20261122-155439_tablas.md` | `Qwen_Qwen3-8B__boe__20261122-155439.jsonl` | `Qwen_Qwen3-8B__boe__20261122-155439_gpu.csv` | `Qwen_Qwen3-8B__boe__20261122-155439_meta.json` | `Qwen_Qwen3-8B__boe__20261122-155439_puntuacion.csv` | Mikel (revisión manual) |
| Qwen/Qwen3-8B | debian | `tablas_B_C/Qwen_Qwen3-8B__debian__20261122-155856_tablas.md` | `Qwen_Qwen3-8B__debian__20261122-155856.jsonl` | `Qwen_Qwen3-8B__debian__20261122-155856_gpu.csv` | `Qwen_Qwen3-8B__debian__20261122-155856_meta.json` | `Qwen_Qwen3-8B__debian__20261122-155856_puntuacion.csv` | Mikel (revisión manual) |
| mistralai/Ministral-3-8B-Instruct-2512 | boe | `tablas_B_C/mistralai_Ministral-3-8B-Instruct-2512__boe__20261122-160150_tablas.md` | `mistralai_Ministral-3-8B-Instruct-2512__boe__20261122-160150.jsonl` | `mistralai_Ministral-3-8B-Instruct-2512__boe__20261122-160150_gpu.csv` | `mistralai_Ministral-3-8B-Instruct-2512__boe__20261122-160150_meta.json` | `mistralai_Ministral-3-8B-Instruct-2512__boe__20261122-160150_puntuacion.csv` | Sendoa |
| mistralai/Ministral-3-8B-Instruct-2512 | debian | `tablas_B_C/mistralai_Ministral-3-8B-Instruct-2512__debian__20261122-160617_tablas.md` | `mistralai_Ministral-3-8B-Instruct-2512__debian__20261122-160617.jsonl` | `mistralai_Ministral-3-8B-Instruct-2512__debian__20261122-160617_gpu.csv` | `mistralai_Ministral-3-8B-Instruct-2512__debian__20261122-160617_meta.json` | `mistralai_Ministral-3-8B-Instruct-2512__debian__20261122-160617_puntuacion.csv` | Sendoa (revisión manual) |

## Decisión por escenario (Fase 4)
`decision_fase4_20GB.md` y `decision_fase4_8GB.md` (plan B), generados con `nahia/decision_fase4.py` a partir de las hojas anteriores y de `comun/umbrales.md`.

## Validación manual de la ayuda del LLM
`validacion_10/`: 10 respuestas puntuadas a ciegas por una persona y su comparación con la hoja (8 de 10 coinciden en corrección, 10 de 10 en abstención).

## Cómo se reproduce todo
`comun/notebook_final.ipynb` ejecuta las Fases 2 y 3 y calcula las tablas (necesita GPU libre, ~50-60 min).

## Nota sobre EmbeddingGemma
Se cargó de una copia local (`sendoa/modelos/embeddinggemma-300m`) del modelo `google/embeddinggemma-300m`.
