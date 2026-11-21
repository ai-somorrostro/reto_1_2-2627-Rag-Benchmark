# Benchmark RAG: trabajo del grupo 1

El enunciado está en [`README.md`](README.md). Este documento explica cómo reproducir nuestros resultados y de qué fichero sale cada cifra.

## Decisión final

| Escenario | Embedding | LLM | Documento |
| --- | --- | --- | --- |
| BOE (Estatuto de los Trabajadores) | `microsoft/harrier-oss-v1-0.6b` | `Qwen/Qwen3.5-9B` (FP8, vLLM) | [`decision_fase4.md`](decision_fase4.md) §5 |
| Debian (manual del administrador) | `BAAI/bge-m3` | `nvidia/NVIDIA-Nemotron-3.5-Bolt-E4B-BF16` (FP8, vLLM) | [`decision_fase4.md`](decision_fase4.md) §5 |
| Plan B (8 GB de VRAM) | — | Ninguno de los medidos cumple los umbrales | [`decision_fase4.md`](decision_fase4.md) §5 |

## Documentos por punto de la entrega

| Punto de la entrega | Dónde está |
| --- | --- |
| 1. Candidatos y stack | [`modelos_embedding.md`](modelos_embedding.md), [`seleccion_llms.md`](seleccion_llms.md) |
| 2. Tablas A, B y C | [`results/embeddings/tabla_a_embeddings.md`](results/embeddings/tabla_a_embeddings.md), [`results/llms/tablas_b_c.md`](results/llms/tablas_b_c.md) |
| 3. Recomendación y umbrales | [`decision_fase4.md`](decision_fase4.md) §1 a §5 |
| 4. Plan B | [`decision_fase4.md`](decision_fase4.md) §5 |
| 5. Lo que no esperábamos | [`decision_fase4.md`](decision_fase4.md) §8 |
| Golden set | [`golden-set/`](golden-set/) (15 preguntas por escenario: 8 directas, 4 combinadas, 3 sin respuesta) y [`golden_set_revision.md`](golden-set/golden_set_revision.md) |

## Entorno

- Hardware: NVIDIA A800 40GB, instancia MIG 3g.20gb (20 GB).
- Stack: vLLM 0.34.0, PyTorch 2.14.0+cu130, Python ≥ 3.12, gestor de paquetes [uv](https://docs.astral.sh/uv/).
- Hacen falta **dos entornos**, porque docling (Fase 1) necesita `huggingface-hub<2` y vLLM 0.34 necesita `>=2`. Están definidos como extras incompatibles en [`pyproject.toml`](pyproject.toml).
- `meta-llama/Llama-3.2-3B-Instruct` tiene acceso restringido: hay que aceptar la licencia en Hugging Face e iniciar sesión (`hf auth login`) antes de la Fase 3.

## Cómo reproducirlo (desde la raíz del repo)

### Fase 1: corpus y chunks (entorno `corpus`, no necesita GPU)

```bash
uv sync --extra corpus
uv run python scripts/convertir_boe.py      # data/raw/*.pdf  -> data/interim/boe_limpio.md (sin cabeceras ni pies)
uv run python scripts/convertir_debian.py   # data/raw/*.epub -> data/interim/debian.md (con títulos de sección)
uv run python scripts/chunking.py           # -> data/chunks/{boe,debian}_chunks.json (un chunk por artículo / sección)
uv run python scripts/revisar_chunks.py     # opcional: muestra los chunks más cortos y más largos
uv run python scripts/trocear.py            # -> data/chunks/{boe,debian}_final.json (máx. 1.800 caracteres por chunk)
```

Los documentos de origen ya están en `data/raw/` y los chunks finales en `data/chunks/`, así que esta fase solo hace falta para regenerarlos.

### Fase 2: embeddings (entorno `benchmark`, GPU)

```bash
uv sync --extra benchmark
uv run python scripts/run_all_embeddings.py   # 3 modelos × 2 escenarios, cada uno en un proceso aparte
```

### Fase 3: LLMs (entorno `benchmark`, GPU)

```bash
uv run python scripts/benchmark_llms_vllm.py            # 4 modelos × 2 escenarios (retrieval + oráculo + coste)
uv run python scripts/generar_tablas_llm.py --plantilla  # crea o completa los CSV de puntuación sin borrar notas
# puntuar a mano results/llms/puntuacion_{boe,debian}.csv
uv run python scripts/generar_tablas_llm.py              # -> results/llms/tablas_b_c.md
```

El retrieval de la Fase 3 no se recalcula: se reutiliza el top-5 que guardó el embedding ganador en la Fase 2, para que todos los LLMs reciban exactamente los mismos fragmentos.

## Trazabilidad: de dónde sale cada cifra

| Cifra | Fichero de resultados | Generado por |
| --- | --- | --- |
| Tabla A (Recall@k, MRR, indexado, tamaño del índice) | `results/embeddings/data/<embedding>_<escenario>.json` (incluye el top-5 de cada pregunta) | `benchmark_embeddings_vllm.py` |
| Tabla A (VRAM) | `results/embeddings/logs/vram_<embedding>_<escenario>.log` | `benchmark_embeddings_vllm.py` |
| Índices vectoriales | `results/embeddings/indices/<embedding>_<escenario>_index.npy` | `benchmark_embeddings_vllm.py` |
| Respuestas brutas de los LLMs, TTFT, tokens/s, latencia, metadatos (modelo, versión, cuantización, parámetros, fecha) | `results/llms/data/<modelo>_<escenario>.json` | `benchmark_llms_vllm.py` |
| Tabla C (VRAM pico) | `results/llms/logs/vram_<modelo>_<escenario>.log` | `benchmark_llms_vllm.py` |
| Logs completos de ejecución | `results/llms/logs/ejecucion_completa.log`, `results/llms/logs/nemotron.log` | salida de consola |
| Tabla B (corrección, fidelidad, abstención, formato) | `results/llms/puntuacion_<escenario>.csv` | puntuación a mano |
| Tablas B y C | `results/llms/tablas_b_c.md` | `generar_tablas_llm.py` |

Nota sobre la puntuación: la primera pasada la hizo una IA con criterios fijos y el grupo la revisó a mano (ver [`decision_fase4.md`](decision_fase4.md) §7).
