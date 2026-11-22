"""Fase 2: métricas de retrieval (sin LLM) por embedding y escenario.

Para cada embedding (Artic, BGE, Multilingual) y cada escenario (boe, debian),
realiza el retrieval top-5 del golden set de preguntas contra los chunks del
corpus (mismas funciones que los benchmarks: dividir_markdown 1200/200 y
SentenceTransformer.encode/semantic_search) y calcula, sobre las preguntas
con respuesta (chunks_relevantes no vacío):

  - Recall@1, Recall@3, Recall@5
  - MRR: media de 1/posición del primer acierto

También mide, por modelo:
  - tiempo de indexado (segundos, codificación de los chunks del corpus)
  - tamaño del índice (bytes del tensor de embeddings)
  - VRAM pico durante la codificación

Salida: metricas_retrieval.csv en la raíz del repositorio (una fila por
embedding x escenario) y una tabla resumen por stdout.
"""

import csv
import os
import sys
import time

import torch
from sentence_transformers import SentenceTransformer, util

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Importamos el troceado fijo de BGE: generar_chunks.py y los benchmarks usan
# la misma función, así que los identificadores de chunk coinciden.
sys.path.insert(0, os.path.join(BASE_DIR, "BGE"))
from benchmark_common import dividir_markdown  # noqa: E402

TOP_K = 5

EMBEDDINGS = [
    {
        "name": "Artic/arctic-embed-l-v2.0",
        "model_id": "Snowflake/snowflake-arctic-embed-l-v2.0",
        "prefijo_consulta": "query: ",
        "prefijo_documento": "",
    },
    {
        "name": "BGE/bge-m3",
        "model_id": "BAAI/bge-m3",
        "prefijo_consulta": "",
        "prefijo_documento": "",
    },
    {
        "name": "Multilingual/e5-large",
        "model_id": "intfloat/multilingual-e5-large",
        "prefijo_consulta": "query: ",
        "prefijo_documento": "passage: ",
    },
]

ESCENARIOS = {
    "boe": {
        "corpus": os.path.join(BASE_DIR, "BOE.md"),
        "preguntas": os.path.join(BASE_DIR, "BGE", "boe_preguntas.txt"),
    },
    "debian": {
        "corpus": os.path.join(BASE_DIR, "debian.md"),
        "preguntas": os.path.join(BASE_DIR, "BGE", "debian_preguntas.txt"),
    },
}


def cargar_preguntas(ruta):
    with open(ruta, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def calcular_metricas(doc_emb, preguntas, emb, prefijo_consulta, top_k=TOP_K):
    """Recall@k y MRR sobre las preguntas que tienen chunks relevantes."""
    relevantes = [p for p in preguntas if p["chunks_relevantes"].strip()]
    if not relevantes:
        return {1: 0.0, 3: 0.0, 5: 0.0}, 0.0, 0
    consultas = [prefijo_consulta + p["pregunta"] for p in relevantes]
    q_emb = emb.encode(consultas, convert_to_tensor=True).cpu()
    aciertos = {1: 0, 3: 0, 5: 0}
    rr = 0.0
    for p, hits in zip(relevantes, util.semantic_search(q_emb, doc_emb, top_k=top_k)):
        ids = {int(c) for c in p["chunks_relevantes"].split(";") if c.strip()}
        hit_ids = [h["corpus_id"] for h in hits]
        for k in (1, 3, 5):
            if any(i in ids for i in hit_ids[:k]):
                aciertos[k] += 1
        primera = next((i + 1 for i, hid in enumerate(hit_ids) if hid in ids), 0)
        if primera:
            rr += 1.0 / primera
    n = len(relevantes)
    recall = {k: round(aciertos[k] / n, 4) for k in aciertos}
    mrr = round(rr / n, 4)
    return recall, mrr, n


def main():
    rows = []
    for escenario in ("boe", "debian"):
        with open(ESCENARIOS[escenario]["corpus"], encoding="utf-8") as f:
            texto = f.read()
        preguntas = cargar_preguntas(ESCENARIOS[escenario]["preguntas"])
        for e in EMBEDDINGS:
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.reset_peak_memory_stats()
            emb = SentenceTransformer(e["model_id"])
            chunks = dividir_markdown(texto)
            t0 = time.perf_counter()
            doc_emb = emb.encode(
                [e["prefijo_documento"] + c for c in chunks], convert_to_tensor=True
            ).cpu()
            index_time = time.perf_counter() - t0
            vram = (
                round(torch.cuda.max_memory_allocated() / 1024**3, 3)
                if torch.cuda.is_available()
                else 0.0
            )
            recall, mrr, n_resp = calcular_metricas(
                doc_emb, preguntas, emb, e["prefijo_consulta"]
            )
            params = sum(p.numel() for p in emb.parameters()) / 1e6
            row = {
                "embedding": e["name"],
                "model_id": e["model_id"],
                "escenario": escenario,
                "n_chunks": len(chunks),
                "recall_1": recall[1],
                "recall_3": recall[3],
                "recall_5": recall[5],
                "mrr": mrr,
                "tiempo_indexado_s": round(index_time, 2),
                "indice_bytes": doc_emb.nbytes,
                "vram_pico_gb": vram,
                "n_preguntas_con_respuesta": n_resp,
                "n_preguntas_sin_respuesta": len(preguntas) - n_resp,
                "embedding_dim": int(doc_emb.shape[-1]),
                "params_millones": round(params, 1),
            }
            rows.append(row)
            print(
                f"{e['name']:26s} {escenario:7s} recall@1={recall[1]:.3f} "
                f"recall@3={recall[3]:.3f} recall@5={recall[5]:.3f} mrr={mrr:.3f} "
                f"index={index_time:6.2f}s vram={vram:.2f}GB"
            )
            del emb, doc_emb
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

    out = os.path.join(BASE_DIR, "metricas_retrieval.csv")
    fieldnames = [
        "embedding",
        "model_id",
        "escenario",
        "n_chunks",
        "recall_1",
        "recall_3",
        "recall_5",
        "mrr",
        "tiempo_indexado_s",
        "indice_bytes",
        "vram_pico_gb",
        "n_preguntas_con_respuesta",
        "n_preguntas_sin_respuesta",
        "embedding_dim",
        "params_millones",
    ]
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print("\nGuardado:", out)


if __name__ == "__main__":
    main()
