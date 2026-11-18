import json, statistics
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent      # raíz del repo
ruta = RAIZ / "comun" / "chunks_debian.json"

chunks = json.load(open(ruta, encoding="utf-8"))
n = [len(c["texto"].split()) for c in chunks]
print(len(chunks), "chunks")
print("palabras: min", min(n), "mediana", statistics.median(n), "max", max(n))
print(sum(1 for x in n if x < 10), "chunks de menos de 10 palabras")
print(chunks[len(chunks)//2]["metadatos"].get("headings"))
print(Counter(c["texto"] for c in chunks).most_common(5))  # repetidos = ruido de cabeceras/pies