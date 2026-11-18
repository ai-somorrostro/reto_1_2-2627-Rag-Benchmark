# Teleco — Benchmark RAG (BOE y Debian)

Introducción: qué es la práctica, los dos escenarios y la rama TeamTeleco.>

## Requerimientos previos

- Python 3.12 o superior
- GPU NVIDIA (VRAM según el modelo; Plan B con 8 GB)
- Espacio en disco (~6 GB del `.venv` + modelos)
- Acceso a Hugging Face (token opcional)

## Instalación

Sigue estos pasos en orden.

### Paso 1 — Clonar el repositorio

```
git clone git@github.com:ai-somorrostro/reto_1_2-2627-Rag-Benchmark.git
cd reto_1_2-2627-Rag-Benchmark
```
```
Paso 2 — Cambiar a la rama del equipo
git checkout TeamTeleco
```
```
Paso 3 — Crear el entorno virtual
./setup.sh
Este comando crea .venv, instala las dependencias de requirements.txt y genera .env a partir de .env.example si no existe.
```
```
Paso 4 — Activar el entorno virtual
source .venv/bin/activate
```
```
Paso 5 — Cargar las variables de entorno
set -a; source .env; set +a
```
```
Paso 6 — Comprobar que todo funciona
python --version
python -c "import torch, docling, pymupdf4llm; print('OK')"
```
Si ves Python 3.12.x y OK, la instalación está lista.