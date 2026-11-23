import sys
# Evitar conflicto de CUDA entre PyTorch y torchaudio en transformers
if "torchaudio" not in sys.modules:
    sys.modules["torchaudio"] = None

import json
import os
import hashlib

import chromadb
from sentence_transformers import SentenceTransformer

from chunking_debian import chunk_debian


def cargar_documentos(filepath: str) -> list:
    """
    Convierte la salida de chunk_debian (lista de tuplas texto, metadata)
    en una lista de diccionarios, con la misma forma que usa indexar_BOE.

    tambien porque los campos tienen nombre y es mas facil saber que hay dentro de los campos, ademas es mas facil de ampliar
    """
    with open(filepath, encoding="utf-8") as f:
        contenido = f.read()

    documentos = []

    for texto, meta in chunk_debian(contenido):
        ruta = " > ".join(
            meta[k] for k in ("capitulo", "seccion", "subseccion") if meta.get(k)
        )

        documentos.append({
            "ruta": ruta,
            "capitulo": meta.get("capitulo", ""),
            "seccion": meta.get("seccion", ""),
            "subseccion": meta.get("subseccion", ""),
            "tipo": meta.get("tipo", "body"),
            "parte": meta.get("parte", "1/1"),
            "doc": meta.get("doc", "debian-handbook"),
            "texto": texto,  # ya incluye la cabecera de contexto
        })

    return documentos


def generar_id(documento: dict) -> str:
    contenido = (
        documento["ruta"]
        + "|"
        + documento["parte"]
        + "|"
        + documento["texto"]
    )

    return hashlib.sha256(
        contenido.encode("utf-8")
    ).hexdigest()


def indexar_documentos(documentos: list, tipoModelo):

    # Crear/abrir base de datos
    client = chromadb.PersistentClient(
        path="./data/chroma"
    )

    nombre_col = f"debian_{tipoModelo}"
    colecciones = [c.name for c in client.list_collections()]
    if nombre_col in colecciones:
        col = client.get_collection(nombre_col)
        if col.count() > 0:
            print(f"El modelo '{tipoModelo}' ya está indexado ({col.count()} chunks). Omitiendo...")
            return

    # Modelo de embeddings
    ruta_modelo = os.path.join(
        os.path.dirname(__file__),
        "..",
        "Modelos",
        "Embedding",
        tipoModelo,
    )
    modelo = SentenceTransformer(
        ruta_modelo,
        trust_remote_code=True,
    )

    collection = client.get_or_create_collection(
        name=nombre_col
    )

    # Preparar información (evitando IDs duplicados, que Chroma rechaza en un mismo lote)
    ids = []
    textos = []
    metadatas = []
    vistos = set()

    for doc in documentos:

        id_doc = generar_id(doc)
        if id_doc in vistos:
            continue
        vistos.add(id_doc)

        ids.append(id_doc)

        textos.append(doc["texto"])

        # Chroma no admite None en metadatos: todo son strings
        metadatas.append({
            "doc": doc["doc"],
            "ruta": doc["ruta"],
            "capitulo": doc["capitulo"],
            "seccion": doc["seccion"],
            "subseccion": doc["subseccion"],
            "tipo": doc["tipo"],
            "parte": doc["parte"],
        })

    print(f"Chunks: {len(textos)}")

    # Generar embeddings por lotes
    batch_size = 64

    for inicio in range(0, len(textos), batch_size):

        fin = inicio + batch_size

        embeddings = modelo.encode(
            textos[inicio:fin],
            normalize_embeddings=True,
            show_progress_bar=False,
        ).tolist()

        collection.upsert(
            ids=ids[inicio:fin],
            documents=textos[inicio:fin],
            metadatas=metadatas[inicio:fin],
            embeddings=embeddings,
        )

        print(f"Indexados {min(fin, len(textos))}/{len(textos)}")

    print("\nIndexación terminada")
    print(f"Total en ChromaDB: {collection.count()}")


def main(tipoModelo):
    ruta = os.path.join(
        os.path.dirname(__file__),
        "..",
        "docs",
        "limpio",
        "debian-handbook.md",
    )

    documentos = cargar_documentos(ruta)

    print(f"Se han generado {len(documentos)} chunks")

    for modelo in tipoModelo:
        print(f"\nIndexando con modelo: {modelo}")
        indexar_documentos(documentos, modelo)


if __name__ == "__main__":
    tipoModelo = json.loads(sys.argv[1])  # Desde notebook enviamos las variables mediante JSON
    main(tipoModelo)
