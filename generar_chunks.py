"""Genera el índice de chunks fijo de cada corpus.

Usa el mismo troceado que los benchmarks (dividir_markdown) para que los
identificadores de chunk del golden set sean estables entre motores.
"""

import csv
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "BGE"))

from benchmark_common import dividir_markdown  # noqa: E402

CORPORA = {
    "boe": os.path.join(BASE_DIR, "BOE.md"),
    "debian": os.path.join(BASE_DIR, "debian.md"),
}


def escribir_chunks(nombre: str, ruta_md: str, ruta_csv: str):
    with open(ruta_md, "r", encoding="utf-8") as f:
        texto = f.read()
    chunks = dividir_markdown(texto)
    with open(ruta_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["chunk_id", "caracteres", "texto"])
        for i, chunk in enumerate(chunks):
            writer.writerow([i, len(chunk), chunk])
    print(f"{nombre}: {len(chunks)} chunks -> {ruta_csv}")


if __name__ == "__main__":
    for nombre, ruta_md in CORPORA.items():
        escribir_chunks(
            nombre, ruta_md, os.path.join(BASE_DIR, f"chunks_{nombre}.csv")
        )
