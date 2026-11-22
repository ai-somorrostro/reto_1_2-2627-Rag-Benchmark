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
