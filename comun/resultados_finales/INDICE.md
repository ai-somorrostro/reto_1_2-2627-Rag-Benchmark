# Índice de trazabilidad: de dónde sale cada cifra

Todos los ficheros brutos están en `nahia/resultados/` (LLMs) y `sendoa/resultados_oficiales/` (embeddings). Datos congelados: `comun/chunks_*.json`, `comun/golden_set_*.json`; prompt: `nahia/prompt.py` (copia idéntica en `comun/prompt.py`); umbrales: `comun/umbrales.md`.

## Tabla A (embeddings)
Ver `tabla_A/tabla_a_boe.md` y `tabla_A/tabla_a_debian.md`: la última columna indica el JSON de origen de cada fila (en `sendoa/resultados_oficiales/`). Embeddings ganadores en `ganadores_embedding.json`.

## Tablas B y C (LLMs): una por ejecución final
Ver `INDICE_ejecuciones.md` (generado por `nahia/consolidar.py`): para cada modelo y escenario, su tabla individual, respuestas, GPU, ficha y hoja de puntuación.

## Decisión por escenario (Fase 4)
`decision_fase4_20GB.md` y `decision_fase4_8GB.md` (plan B), generados con `nahia/decision_fase4.py` a partir de las hojas anteriores y de `comun/umbrales.md`.

## Validación manual de la ayuda del LLM
`validacion_10/`: 10 respuestas puntuadas a ciegas por una persona y su comparación con la hoja (8 de 10 coinciden en corrección, 10 de 10 en abstención).

## Cómo se reproduce todo
`comun/notebook_final.ipynb` ejecuta las Fases 2 y 3 y calcula las tablas (necesita GPU libre, ~50-60 min).

## Nota sobre EmbeddingGemma
Se cargó de una copia local (`sendoa/modelos/embeddinggemma-300m`) del modelo `google/embeddinggemma-300m`.

## Tablas consolidadas por escenario
`Tabla_B_BOE.md`, `Tabla_C_BOE.md`, `Tabla_B_Debian.md`, `Tabla_C_Debian.md` (generadas por `nahia/consolidar.py`) y `tabla_A/` para los embeddings.

## Versiones de los modelos
`versiones_modelos.md`: hash de revisión de Hugging Face de cada modelo; los LLM finales lo guardan también en `version_modelo` de su `_meta.json`.

## Conclusiones
`CONCLUSIONES.md`: candidatos y stack, recomendación por escenario, plan B, lo que no esperábamos y limitaciones.

## Corrección del golden de Debian
q_deb_10 se reescribió (ejemplo /srv/files, fragmento 824) y se repitieron retrieval y LLM de Debian; los BOE se repitieron para guardar la versión del modelo. Ver `CONCLUSIONES.md` §4.
