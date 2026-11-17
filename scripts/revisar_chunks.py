from pathlib import Path
import json

RAIZ = Path(__file__).resolve().parent.parent


def longitud(chunk):
    return len(chunk["texto"])


for nombre in ["boe", "debian"]:
    ruta = RAIZ / "data" / "chunks" / (nombre + "_chunks.json")
    chunks = json.loads(ruta.read_text(encoding="utf-8"))
    ordenados = sorted(chunks, key=longitud)

    print("=====", nombre, "=====")
    print("Los 5 más cortos:")
    for chunk in ordenados[:5]:
        print("  ", chunk["id"], longitud(chunk), chunk["titulo"][:70])
    print("Los 5 más largos:")
    for chunk in ordenados[-5:]:
        print("  ", chunk["id"], longitud(chunk), chunk["titulo"][:70])

    if nombre == "boe":
        articulos = 0
        disposiciones = 0
        for chunk in chunks:
            if chunk["titulo"].startswith("Artículo"):
                articulos = articulos + 1
            if chunk["titulo"].startswith("Disposición"):
                disposiciones = disposiciones + 1
        print("Artículos:", articulos, "Disposiciones:", disposiciones)
        for chunk in chunks:
            if chunk["titulo"].startswith("Artículo 38."):
                print(chunk["texto"][:400])