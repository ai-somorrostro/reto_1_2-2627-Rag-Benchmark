# Teleco — Benchmark RAG (BOE y Debian)

## ¿Qué es esta práctica?

Esta práctica mide con IA dos cosas en un sistema RAG (sistema que responde preguntas con información de un documento):

1. **Embeddings**: modelos que traducen texto a números, para que una pregunta encuentre el fragmento que la responde.
2. **LLM pequeños**: modelos de IA que responden preguntas basándose solo en lo que el embedding trajo.

El equipo usa dos documentos:

- El **Estatuto de los Trabajadores** (España), para medir artículos parecidos y remisiones.
- El **manual del Administrador de Debian** (en español, para Debian 11).

En resumen:

1. El equipo crea un **golden set** de 15 preguntas por documento: 8 con respuesta corta, 4 que necesitan mezclar dos fragmentos, y 3 sin respuesta en el documento.
2. Se elige el mejor **embedding** por documento, mirando solo la calidad de la búsqueda (Fase 2).
3. Luego se elige el **LLM pequeño** que responde mejor (Fase 3).
4. Al final cada equipo da una frase: «Para el documento X usaría el modelo Y, porque mi métrica Z dio mejor» (Fase 4).

## Los dos escenarios

| Escenario | Documento | Qué pone a prueba |
| --- | --- | --- |
| 1. Normativa larga | Estatuto de los Trabajadores consolidado | Artículos parecidos, lenguaje jurídico, remisiones entre artículos, pedir el artículo exacto |
| 2. Documentación técnica | Manual del Administrador de Debian (español, Debian 11) | Prosa mezclada con comandos y rutas |

## Requeresitos previos

- Python 3.12 o superior
- GPU NVIDIA (la VRAM depende del modelo; el Plan B pega con 8 GB)
- Unos 6 GB libres en disco
- Acceso a Hugging Face (token opcional)

## Instalación (pasos en orden)

1. Clonar y ponerte en la rama del equipo:

```
git clone git@github.com:ai-somorrostro/reto_1_2-2627-Rag-Benchmark.git
cd reto_1_2-2627-Rag-Benchmark
git checkout TeamTeleco
```

2. Crear el entorno virtual (instala las dependencias y crea `.env` si no existe):

```
./setup.sh
```

3. Activar el entorno virtual:

```
source .venv/bin/activate
```

4. Cargar las variables de entorno:

```
set -a; source .env; set +a
```

5. Verificar que todo funciona:

```
python --version
python -c "import torch, docling, pymupdf4llm; print('OK')"
```

## Flujo básico (qué ejecutar, por carpeta de equipo)

En cada carpeta de equipo (`Artic`, `BGE`, `Multilingual`) hay un benchmark por escenario:

```
cd Artic
python benchmark_boe.py      # benchmark del escenario BOE
python benchmark_debian.py   # benchmark del escenario Debian
```

1. **Preparar corpus:**

```
python3 pdf_preparation.py   # BOE.pdf -> BOE.md
python3 epub_preparation.py  # debian.epub -> debian.md
python3 generar_chunks.py    # genera chunks_boe.csv y chunks_debian.csv
```

2. **Ejecutar benchmark** con la ventana de un equipo.

3. Los resultados quedan en `resultados_boe/` y `resultados_debian/` de la carpeta del equipo.

El detalle de cómo comparar, calificar y decidir los modelos está en `README.md`.
