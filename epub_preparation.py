import os
from docling.document_converter import DocumentConverter

# Carpeta donde está este script (rutas válidas desde cualquier cwd)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Entrada y salida
EPUB_PATH = os.path.join(BASE_DIR, "debian.epub")   # EPUB original
MD_PATH = os.path.join(BASE_DIR, "debian.md")       # Markdown que se genera

# Si ya existe debian.md no se repite la conversión
if os.path.exists(MD_PATH):
    print(f"'{MD_PATH}' ya existe; no se vuelve a convertir.")
else:
    print(f"Convirtiendo '{EPUB_PATH}' a Markdown con docling...")
    # DocumentConverter detecta el formato por la extensión (.epub)
    result = DocumentConverter().convert(EPUB_PATH)
    # save_as_markdown exporta a Markdown; las imágenes quedan como <!-- image -->
    result.document.save_as_markdown(MD_PATH)
    print(f"Listo: '{MD_PATH}' ({os.path.getsize(MD_PATH)} bytes).")