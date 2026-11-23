import sys
# Evitar conflicto de CUDA entre PyTorch y torchaudio en transformers
if "torchaudio" not in sys.modules:
    sys.modules["torchaudio"] = None

import sys
import json
import os
import hashlib

import chromadb
from sentence_transformers import SentenceTransformer

from chunking_BOE import cargar_documentos


def generar_id(documento: dict) -> str:
    contenido = (
        documento["seccion"]
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

    nombre_col = f"boe_{tipoModelo}"
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
        name=f"boe_{tipoModelo}"
    )

    # Preparar información
    ids = []
    textos = []
    metadatas = []

    for doc in documentos:

        ids.append(generar_id(doc))

        textos.append(doc["texto"])

        metadatas.append({
            "seccion": doc["seccion"],
            "articulo": doc["articulo"],
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
        "BOE.md",
    )

    documentos = cargar_documentos(ruta)

    print(f"Se han generado {len(documentos)} chunks")

    for modelo in tipoModelo:
        print(f"\nIndexando con modelo: {modelo}")
        indexar_documentos(documentos, modelo)


if __name__ == "__main__":
    tipoModelo = json.loads(sys.argv[1])# Desde notebook enviamos las variables mediante JSON
    main(tipoModelo)
