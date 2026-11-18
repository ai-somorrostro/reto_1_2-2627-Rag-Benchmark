import os
import pymupdf4llm

# Carpeta donde está este script: así las rutas son válidas aunque
# ejecutemos el script desde otra carpeta.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Entrada y salida
PDF_PATH = os.path.join(BASE_DIR, "BOE.pdf")   # PDF original
MD_PATH = os.path.join(BASE_DIR, "BOE.md")     # Markdown que se genera

# Si ya existe BOE.md no se repite la conversión (ahorra tiempo).
if os.path.exists(MD_PATH):
    print(f"'{MD_PATH}' ya existe; no se vuelve a convertir.")
else:
    print(f"Convirtiendo '{PDF_PATH}' a Markdown...")
    # to_markdown() extrae el texto del PDF y lo devuelve como Markdown
    markdown = pymupdf4llm.to_markdown(PDF_PATH)
    with open(MD_PATH, "w", encoding="utf-8") as f:
        f.write(markdown)
    print(f"Listo: '{MD_PATH}' ({len(markdown)} caracteres).")