# Índice de registros de agentes

| Fecha | Fichero | Resumen |
| --- | --- | --- |
| 17/11/2026 | [20261117_example_log.md](20261117_example_log.md) | Ejemplo del formato de registro. |
| 18/11/2026 | [20261118_creacionepub_preparation.md](20261118_creacionepub_preparation.md) | Creación de `epub_preparation.py` (debian.epub → debian.md con docling). |
| 18/11/2026 | [20261118_mejorapdf_preparation.md](20261118_mejorapdf_preparation.md) | Creación de `pdf_preparation.py` (BOE.pdf → BOE.md con pymupdf4llm). |
| 22/11/2026 | [20261122_filtro_stderr_pdf_preparation.md](20261122_filtro_stderr_pdf_preparation.md) | Filtro de avisos onnxruntime en `pdf_preparation.py` y corrección del typo en `setup.sh`. |
| 22/11/2026 | [20261122_benchmark_bge.md](20261122_benchmark_bge.md) | Creación de `BGE/benchmark_bge.py`: benchmark de BGE-M3 con 4 LLMs y guardado incremental por modelo. |
| 22/11/2026 | [20261122_benchmark_multilingual.md](20261122_benchmark_multilingual.md) | Creación de `Multilingual/benchmark_multilingual.py`: mismo benchmark con E5-large y prefijos query/passage. |
| 22/11/2026 | [20261122_benchmark_separado.md](20261122_benchmark_separado.md) | Separación por corpus: scripts BOE/Debian independientes y carpetas `resultados_boe/` y `resultados_debian/` en BGE, Multilingual y Artic. |
| 22/11/2026 | [20261122_golden_set_and_boe_corpus.md](20261122_golden_set_and_boe_corpus.md) | Corrección del golden set (33 preguntas/escenario, columnas `tipo`/`oficial`/`chunks_relevantes`), BOE.md limpiado, `chunks_boe.csv` (486) y `chunks_debian.csv` (1642) regenerados, re-run de BOE reruns en Artic/BGE/Multilingual. |
| 22/11/2026 | [20261122_readme_teleco_y_agents_rule.md](20261122_readme_teleco_y_agents_rule.md) | Reescritura básica de `README_teleco.md`; regla 8 en `AGENTS.md` (prohibido tocar `README.md`); `README.md` restaurado a su estado original. |
| 22/11/2026 | [20261122_detener_benchmark_readme.md](20261122_detener_benchmark_readme.md) | Añadida a `README.md` la sección "Detener un benchmark en curso" (Ctrl+C, botón Cancelar, dónde guarda las respuestas y que se puede reanudar). |
| 22/11/2026 | [20261122_detener_rerun_boe.md](20261122_detener_rerun_boe.md) | Detención del rerun de BOE (Artic iniciado, BGE por empezar); todo detenido, 0 procesos; resultados no guardados en Artic. |
| 22/11/2026 | [20261122_teleco_readme_pasos.md](20261122_teleco_readme_pasos.md) | `README_teleco.md` reescrito como guía paso a paso simple para principiantes (qué es, escenarios, preparar, corpora, ejecutar, detener, resultados). |
| 23/11/2026 | [20261123_gitignore_py_outputs.md](20261123_gitignore_py_outputs.md) | Añadidos a `.gitignore` los archivos generados por los scripts Python (.py). |
