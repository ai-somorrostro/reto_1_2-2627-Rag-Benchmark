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
