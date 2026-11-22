"""Benchmark RAG para la carpeta BGE.

Referencia: rag.py de RAG_IACT.
Embedding: BAAI/bge-m3.
LLMs: 2 pequenos (Qwen 2.5 3B y SmolLM2 1.7B) y 2 medianos
(Qwen 2.5 7B y Mistral 7B).

Uso:
    python benchmark_bge.py                     # los 4 LLMs y los 2 escenarios
    python benchmark_bge.py --llm qwen2.5-3b    # solo un LLM
    python benchmark_bge.py --escenario boe     # solo un escenario
    python benchmark_bge.py --max-preguntas 2   # prueba rapida

Los resultados se guardan en BGE/resultados_<llm>.txt. Si el fichero ya
existe, se anaden solo las preguntas que falten (no se repiten).
"""

import argparse
import csv
import gc
import os
import re
import time

import torch
from sentence_transformers import SentenceTransformer, util
from transformers import AutoModelForCausalLM, AutoTokenizer

# --- CONFIGURACION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

EMBEDDING_MODEL = "BAAI/bge-m3"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DTYPE = torch.float16 if DEVICE == "cuda" else torch.float32
CUANTIZACION = "fp16" if DEVICE == "cuda" else "fp32"

TOP_K = 3
MAX_CHARS = 1200
OVERLAP = 200
MAX_NEW_TOKENS = 350

SYSTEM_PROMPT = (
    "Eres un asistente experto en el documento proporcionado. "
    "Responde de forma precisa y concisa usando EXCLUSIVAMENTE la información del contexto. "
    "Si la respuesta no aparece en el contexto, responde exactamente: 'No aparece en el documento'. "
    "Cuando el contexto lo indique, cita el artículo o la sección correspondiente. "
    "Responde siempre en español."
)

ESCENARIOS = {
    "boe": {
        "corpus": os.path.join(ROOT_DIR, "BOE.md"),
        "preguntas": os.path.join(BASE_DIR, "boe_preguntas.txt"),
    },
    "debian": {
        "corpus": os.path.join(ROOT_DIR, "debian.md"),
        "preguntas": os.path.join(BASE_DIR, "debian_preguntas.txt"),
    },
}

LLMS = {
    "qwen2.5-3b": ("Qwen/Qwen2.5-3B-Instruct", "3B", "pequeno"),
    "smollm2-1.7b": ("HuggingFaceTB/SmolLM2-1.7B-Instruct", "1.7B", "pequeno"),
    "qwen2.5-7b": ("Qwen/Qwen2.5-7B-Instruct", "7B", "mediano"),
    "mistral-7b": ("mistralai/Mistral-7B-Instruct-v0.3", "7B", "mediano"),
}


def cargar_env(ruta: str):
    """Carga HF_TOKEN/HF_HOME desde .env sin sobrescribir el entorno."""
    if not os.path.exists(ruta):
        return
    with open(ruta, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            clave, valor = linea.split("=", 1)
            os.environ.setdefault(clave.strip(), valor.strip().strip('"').strip("'"))


def dividir_markdown(texto_md: str, max_chars: int = MAX_CHARS, overlap: int = OVERLAP) -> list[str]:
    """Mismo troceado que rag.py: bloques de hasta max_chars con solape."""
    bloques = re.split(r"\n{2,}", texto_md)
    chunks = []
    actual = ""

    for bloque in bloques:
        bloque = bloque.strip()
        if not bloque:
            continue

        if len(actual) + len(bloque) + 2 <= max_chars:
            actual = f"{actual}\n\n{bloque}" if actual else bloque
        else:
            if actual:
                chunks.append(actual)
            if len(bloque) > max_chars:
                inicio = 0
                while inicio < len(bloque):
                    chunks.append(bloque[inicio : inicio + max_chars])
                    inicio += max_chars - overlap
                actual = ""
            else:
                solape = actual[-overlap:] if len(actual) > overlap else actual
                actual = f"{solape}\n\n{bloque}".strip()

    if actual:
        chunks.append(actual)
    return chunks


def cargar_preguntas(ruta: str) -> list[dict]:
    with open(ruta, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def construir_indice(embedder: SentenceTransformer, texto: str):
    chunks = dividir_markdown(texto)
    embeddings = embedder.encode(chunks, convert_to_tensor=True, show_progress_bar=True).cpu()
    return chunks, embeddings


def recuperar(pregunta: str, embedder: SentenceTransformer, chunks, embeddings, top_k: int):
    query_emb = embedder.encode([str(pregunta)], convert_to_tensor=True).cpu()
    hits = util.semantic_search(query_emb, embeddings, top_k=top_k)[0]
    return [(hit["corpus_id"], hit["score"], chunks[hit["corpus_id"]]) for hit in hits]


def formatear_contexto(recuperados) -> str:
    partes = [
        f"[Fragmento {idx} | Similitud: {score:.2f}]\n{texto}"
        for idx, score, texto in recuperados
    ]
    return "\n\n---\n\n".join(partes)


def generar_respuesta(model, tokenizer, contexto: str, pregunta: str):
    mensajes = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Contexto del documento:\n\n{contexto}\n\nPregunta: {pregunta}",
        },
    ]
    texto_entrada = tokenizer.apply_chat_template(
        mensajes, tokenize=False, add_generation_prompt=True
    )
    inputs = tokenizer([texto_entrada], return_tensors="pt").to(DEVICE)

    t0 = time.time()
    with torch.no_grad():
        salida = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
        )
    latencia = time.time() - t0

    generados = salida[0][inputs["input_ids"].shape[1] :]
    respuesta = tokenizer.decode(generados, skip_special_tokens=True).strip()
    return respuesta, latencia, len(generados)


def leer_preguntas_hechas(ruta: str) -> set[tuple[str, str]]:
    hechas = set()
    if not os.path.exists(ruta):
        return hechas
    with open(ruta, "r", encoding="utf-8") as f:
        for linea in f:
            m = re.search(r"Escenario: (\w+) \| Pregunta: (\S+)", linea)
            if m:
                hechas.add((m.group(1), m.group(2)))
    return hechas


def escribir_cabecera(
    ruta: str, model_id: str, tamano: str, tipo: str, top_k: int
):
    if os.path.exists(ruta) and os.path.getsize(ruta) > 0:
        return
    with open(ruta, "a", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write(f"Benchmark RAG - Embedding: {EMBEDDING_MODEL}\n")
        f.write(f"LLM: {model_id} ({tamano}, {tipo}) - cuantizacion: {CUANTIZACION}\n")
        f.write(f"Dispositivo: {DEVICE}\n")
        f.write(
            f"Config: top_k={top_k}, max_new_tokens={MAX_NEW_TOKENS}, "
            f"chunk={MAX_CHARS}/{OVERLAP}\n"
        )
        f.write("=" * 70 + "\n\n")


def guardar_resultado(
    ruta: str,
    escenario: str,
    pregunta: dict,
    recuperados,
    respuesta: str,
    latencia: float,
    tokens: int,
):
    abstencion = "si" if "no aparece en el documento" in respuesta.lower() else "no"
    with open(ruta, "a", encoding="utf-8") as f:
        f.write("-" * 70 + "\n")
        f.write(
            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] "
            f"Escenario: {escenario} | Pregunta: {pregunta['id']}\n"
        )
        f.write(
            f"Categoria: {pregunta.get('categoria', '')} | "
            f"Dificultad: {pregunta.get('dificultad', '')}\n"
        )
        f.write(f"Pregunta: {pregunta['pregunta']}\n")
        f.write(f"Referencia: {pregunta.get('referencia', '')}\n")
        f.write(f"Respuesta esperada: {pregunta.get('respuesta_correcta', '')}\n")
        f.write(f"--- Recuperados (top {len(recuperados)}) ---\n")
        for i, (idx, score, texto) in enumerate(recuperados, start=1):
            f.write(f"  [{i}] chunk={idx} score={score:.4f}\n")
            f.write(f"      {texto}\n")
        f.write("--- Respuesta LLM ---\n")
        f.write(respuesta + "\n")
        f.write("--- Datos ---\n")
        f.write(f"  latencia_total_s={latencia:.2f}\n")
        f.write(f"  tokens_generados={tokens}\n")
        f.write(f"  tokens_por_s={tokens / latencia if latencia else 0:.1f}\n")
        f.write(f"  score_max={recuperados[0][1]:.4f}\n")
        f.write(f"  abstencion_detectada={abstencion}\n")
        f.write("\n")


def main():
    parser = argparse.ArgumentParser(description="Benchmark RAG de la carpeta BGE")
    parser.add_argument("--llm", default="all", choices=["all", *LLMS], help="LLM a ejecutar")
    parser.add_argument(
        "--escenario", default="all", choices=["all", *ESCENARIOS], help="Escenario a ejecutar"
    )
    parser.add_argument("--top-k", type=int, default=TOP_K)
    parser.add_argument(
        "--max-preguntas",
        type=int,
        default=0,
        help="Limite de preguntas por escenario (0 = todas)",
    )
    args = parser.parse_args()
    if args.top_k < 1:
        parser.error("--top-k debe ser mayor o igual que 1")

    cargar_env(os.path.join(ROOT_DIR, ".env"))

    llms = LLMS if args.llm == "all" else {args.llm: LLMS[args.llm]}
    escenarios = (
        ESCENARIOS if args.escenario == "all" else {args.escenario: ESCENARIOS[args.escenario]}
    )

    print(f"Embedding: {EMBEDDING_MODEL} en {DEVICE} ({CUANTIZACION})")
    embedder = SentenceTransformer(EMBEDDING_MODEL, device=DEVICE)

    # Se hace todo el retrieval antes de cargar los LLM: asi el embedding
    # libera su VRAM y los modelos grandes caben en la GPU.
    preparadas = []
    for nombre, cfg in escenarios.items():
        print(f"\nIndexando escenario '{nombre}'...")
        with open(cfg["corpus"], "r", encoding="utf-8") as f:
            texto = f.read()
        chunks, embeddings = construir_indice(embedder, texto)
        print(f"  {len(chunks)} fragmentos indexados")

        preguntas = cargar_preguntas(cfg["preguntas"])
        if args.max_preguntas:
            preguntas = preguntas[: args.max_preguntas]
        for pregunta in preguntas:
            recuperados = recuperar(
                pregunta["pregunta"], embedder, chunks, embeddings, args.top_k
            )
            preparadas.append(
                {
                    "escenario": nombre,
                    "pregunta": pregunta,
                    "recuperados": recuperados,
                    "contexto": formatear_contexto(recuperados),
                }
            )

    del embedder
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    print(f"\n{len(preparadas)} preguntas preparadas (retrieval hecho).")

    for llm_key, (model_id, tamano, tipo) in llms.items():
        ruta = os.path.join(BASE_DIR, f"resultados_{llm_key}.txt")
        hechas = leer_preguntas_hechas(ruta)

        # Si ya estan todas las preguntas, no hace falta cargar el modelo.
        if all(
            (item["escenario"], item["pregunta"]["id"]) in hechas
            for item in preparadas
        ):
            print(f"\n[saltado] {llm_key}: ya tiene las {len(preparadas)} preguntas")
            continue

        print(f"\n{'=' * 60}")
        print(f"LLM: {llm_key} -> {model_id} ({tamano}, {tipo})")
        print(f"Resultados: {ruta}")
        print(f"{'=' * 60}")

        try:
            tokenizer = AutoTokenizer.from_pretrained(model_id)
            model = AutoModelForCausalLM.from_pretrained(model_id, dtype=DTYPE).to(DEVICE)
        except Exception as e:
            print(f"ERROR al cargar {model_id}: {e}")
            print("Si el modelo es privado, define HF_TOKEN en .env y vuelve a intentarlo.")
            continue

        escribir_cabecera(ruta, model_id, tamano, tipo, args.top_k)

        for item in preparadas:
            nombre = item["escenario"]
            pregunta = item["pregunta"]
            recuperados = item["recuperados"]

            if (nombre, pregunta["id"]) in hechas:
                print(f"  [saltada] {nombre} {pregunta['id']} (ya estaba en el txt)")
                continue

            try:
                respuesta, latencia, tokens = generar_respuesta(
                    model, tokenizer, item["contexto"], pregunta["pregunta"]
                )
            except Exception as e:
                respuesta, latencia, tokens = f"ERROR: {e}", 0.0, 0

            guardar_resultado(
                ruta,
                nombre,
                pregunta,
                recuperados,
                respuesta,
                latencia,
                tokens,
            )
            print(
                f"  [{nombre}] {pregunta['id']} -> {latencia:.1f}s, "
                f"score_max={recuperados[0][1]:.2f}, tokens={tokens}"
            )

        del model, tokenizer
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
