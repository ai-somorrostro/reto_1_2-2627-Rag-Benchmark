import argparse
import contextlib
import os
import re
import sys
import tempfile

import pymupdf4llm

# Carpeta donde está este script: así las rutas son válidas aunque
# ejecutemos el script desde otra carpeta.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Entrada y salida
PDF_PATH = os.path.join(BASE_DIR, "BOE.pdf")   # PDF original
MD_PATH = os.path.join(BASE_DIR, "BOE.md")     # Markdown que se genera


@contextlib.contextmanager
def filtrar_avisos_onnxruntime():
    # onnxruntime escribe sus avisos directamente al descriptor 2 (no a
    # sys.stderr); capturamos ese tráfico y reemitimos todo menos las líneas
    # de onnxruntime, que en este contenedor son ruido no fatal.
    with tempfile.TemporaryFile(mode="w+") as buf:
        guardado = os.dup(2)
        os.dup2(buf.fileno(), 2)
        try:
            yield
        finally:
            os.dup2(guardado, 2)
            os.close(guardado)
            buf.seek(0)
            for linea in buf:
                if "onnxruntime" not in linea:
                    sys.stderr.write(linea)


# Si ya existe BOE.md no se repite la conversión (ahorra tiempo).
def limpiar_markdown(markdown: str) -> str:
    """Quita cabeceras y números de página repetidos del BOE."""
    lineas = []
    for linea in markdown.splitlines():
        if re.fullmatch(r"\s*Página \d+\s*", linea):
            continue
        if re.fullmatch(
            r"\s*BOLETÍN OFICIAL DEL ESTADO\s+LEGISLACIÓN CONSOLIDADA\s*", linea
        ):
            continue
        lineas.append(linea)
    texto = "\n".join(lineas)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip() + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="Convierte BOE.pdf a Markdown y limpia cabeceras/pies."
    )
    parser.add_argument(
        "--forzar",
        action="store_true",
        help="Vuelve a convertir el PDF aunque BOE.md ya exista.",
    )
    args = parser.parse_args()

    if os.path.exists(MD_PATH) and not args.forzar:
        print(f"'{MD_PATH}' ya existe; no se vuelve a convertir.")
        return

    print(f"Convirtiendo '{PDF_PATH}' a Markdown...")
    # to_markdown() extrae el texto del PDF y lo devuelve como Markdown
    with filtrar_avisos_onnxruntime():
        markdown = pymupdf4llm.to_markdown(PDF_PATH)
    markdown = limpiar_markdown(markdown)
    with open(MD_PATH, "w", encoding="utf-8") as f:
        f.write(markdown)
    print(f"Listo: '{MD_PATH}' ({len(markdown)} caracteres).")


if __name__ == "__main__":
    main()