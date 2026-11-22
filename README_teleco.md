# Teleco — Benchmark RAG (BOE y Debian)

## 1. ¿Qué es esta práctica?

Es un proyecto de fin de curso sobre un **sistema RAG**: un programa que responde preguntas sobre un documento buscando en la red la parte relevante (ese búsqueda se llama **embedding**).

Se miden dos cosas:

- **Embeddings**: qué modelo encuentra mejor la parte del documento que responde.
- **LLM pequeños**: qué modelo responde mejor a partir de lo que el embedding encontró.

Los documentos que se miden:

1. **Estatuto de los Trabajadores** (España).
2. **Manual del Administrador de Debian** (en español, para Debian 11).

## 2. Los dos escenarios

| Escenario | Documento | Qué se mide |
| --- | --- | --- |
| 1. Normativa larga | Estatuto de los Trabajadores | Artículos parecidos, remisiones entre artículos, responder al artículo exacto |
| 2. Documentación técnica | Manual del Administrador de Debian | La redacción mezclada con comandos y rutas |

## 3. Preparar el ordenador

- Python 3.12 o más nuevo.
- GPU NVIDIA (necesaria; con 8 GB de RAM también sirve para ciertas pruebas).
- Unos 6 GB libres en disco.
- Acceso a Hugging Face (token opcional).

**Paso 1.** Descargar el proyecto:

```
git clone git@github.com:ai-somorrostro/reto_1_2-2627-Rag-Benchmark.git
```

```
cd reto_1_2-2627-Rag-Benchmark
git checkout TeamTeleco
```

**Paso 2.** Instalar lo necesario (crea la carpeta `.venv` con las dependencias):

```
./setup.sh
```

**Paso 3.** Activar el entorno virtual:

```
source .venv/bin/activate
```

**Paso 4.** Cargar las variables de entorno:

```
set -a; source .env; set +a
```

**Paso 5.** Comprobar que funciona:

```
python --version
python -c "import torch, docling, pymupdf4llm; print('OK')"
```

## 4. Preparar los corpora

Ejecuta estos pasos antes de empezar a medir:

```
python3 pdf_preparation.py   # BOE.pdf -> BOE.md
python3 epub_preparation.py  # debian.epub -> debian.md
python3 generar_chunks.py    # genera los índices de chunks
```

Si ya existen `BOE.md` y `debian.md`, los scripts los dejan tal cual.

## 5. Ejecutar el benchmark

Cada equipo tiene su carpeta: `Artic`, `BGE`, `Multilingual`. Entra en la tuya y lanza:

```
cd Artic
python benchmark_boe.py       # benchmark del escenario BOE
python benchmark_debian.py    # benchmark del escenario Debian
```

Las respuestas se guardan de forma inmediata en `resultados_boe/` y `resultados_debian/` de la carpeta del equipo, un fichero por modelo llamado `resultados_<modelo>.txt`.

## 6. Detener el benchmark en curso

Si quieres pararlo, pulsa `Ctrl+C`. Ya salieron respuestas siguen guardadas, y relanzando el script se saltan las preguntas hechas, así que continúa donde lo dejaste. Detalles en `README.md` ("Detener un benchmark en curso").

## 7. Dónde quedan los resultados

Para cada modelo hay un fichero `resultados_<modelo>.txt` que contiene la pregunta, la respuesta del modelo y datos de latencia. Esos son los datos que se anotan en las tablas de `README.md`.

## 8. Proceso completo: usar el repositorio de principio a fin

El orden natural de los pasos:

1. **Entrar y preparar el entorno** (secciones 2 y 3):
   - `./setup.sh` — crea la carpeta `.venv` con Python ≥ 3.12 y las dependencias; a partir de `.env.example` crea `.env` si no existe.
   - `source .venv/bin/activate`
   - `set -a; source .env; set +a`

2. **Preparar los corpora** (sección 4):
   - `python3 pdf_preparation.py` — `BOE.pdf` → `BOE.md`
   - `python3 epub_preparation.py` — `debian.epub` → `debian.md`
   - `python3 generar_chunks.py` — genera `chunks_boe.csv` y `chunks_debian.csv`

3. **Fase 2 — métricas de retrieval**:
   - `python3 metricas_retrieval.py` — genera `metricas_retrieval.csv` (recall@1/3/5, MRR, tiempo de indexado, tamaño del índice y VRAM por embedding y escenario)

4. **Benchmarks en los modelos de referencia** (sección 5):
   - En `Artic/`, `BGE/` y `Multilingual/`: `python3 benchmark_boe.py` y `python3 benchmark_debian.py`
   - Las respuestas se guardan de forma incremental en `resultados_boe/` y `resultados_debian/` de cada carpeta (sección 6: se puede detener y reanudar).

5. **Fase 3a — puntuaciones y coste**:
   - `python3 evaluar_respuestas.py` — genera `puntuaciones.csv` y `coste.csv`

6. **Puntuar a mano**:
   - En `puntuaciones.csv`: campos `correccion` (0-2), `fidelidad` (si/no), `abstencion` (si/no/no aplica) y `formato_e_idioma` (si/no)

7. **Fase 4 — decisiones por escenario**:
   - `python3 generar_decisiones.py` — muestra las tablas A (embeddings), B (LLM calidad) y C (LLM coste) y una recomendación de LLM por escenario

## 9. Qué hace cada script (.py)

| Script | Qué hace | Salida |
| --- | --- | --- |
| `pdf_preparation.py` | Convierte `BOE.pdf` en `BOE.md` con pymupdf4llm y limpia cabeceras y pies de página; si ya existe `BOE.md`, no vuelve a convertir (`--forzar` lo obliga) | `BOE.md` |
| `epub_preparation.py` | Convierte `debian.epub` en `debian.md` con docling; si ya existe, no se reconvierte | `debian.md` |
| `generar_chunks.py` | Trocea `BOE.md` y `debian.md` con la misma función que usan los benchmarks (`dividir_markdown`) para que los IDs de chunk del golden set sean estables entre motores | `chunks_boe.csv`, `chunks_debian.csv` |
| `metricas_retrieval.py` | (Fase 2) Hace retrieval del golden set contra los chunks de cada corpus y calcula Recall@1/3/5 y MRR; mide tiempo de indexado, tamaño del índice y VRAM pico | `metricas_retrieval.csv` |
| `evaluar_respuestas.py` | (Fase 3a) Lee los `resultados_*.txt` de Artic, BGE y Multilingual y extrae las puntuaciones por respuesta LLM, más estadísticas de latencia y tokens/s | `puntuaciones.csv`, `coste.csv` |
| `generar_decisiones.py` | (Fase 4) Aplica los umbrales (`umbrales.csv`) y elige, por escenario, el LLM que cumple y es más barato; imprime tablas A (embeddings), B (LLM calidad) y C (LLM coste) | stdout |
| `Artic/benchmark_boe.py`, `Artic/benchmark_debian.py` | Benchmark de la carpeta Artic: indexa el corpus con el embedding de la carpeta y genera respuestas con los LLMs de referencia, guardando los resultados de forma incremental | `Artic/resultados_boe/`, `Artic/resultados_debian/` |
| `BGE/benchmark_boe.py`, `BGE/benchmark_debian.py` | Benchmark de la carpeta BGE: embedding `BAAI/bge-m3` | `BGE/resultados_boe/`, `BGE/resultados_debian/` |
| `Multilingual/benchmark_boe.py`, `Multilingual/benchmark_debian.py` | Benchmark de la carpeta Multilingual: embedding `intfloat/multilingual-e5-large` con prefijos `query:`/`passage:` | `Multilingual/resultados_boe/`, `Multilingual/resultados_debian/` |

LLMs de referencia: `qwen2.5-3b`, `smollm2-1.7b`, `qwen2.5-7b`, `mistral-7b`.
