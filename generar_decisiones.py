"""Fase 4: decisiones por escenario a partir de puntuaciones + umbrales.

Lee metricas_retrieval.csv, puntuaciones.csv y coste.csv (resultados de la
fase 2 y fase 3a) y escribe decisiones.md con:

  - Tabla A: embeddings por escenario (Recall@1/3/5, MRR, indexado, Índice, VRAM).
  - Tabla B: LLMs (calidad) por escenario/embedding: corrección media, fidelidad,
    abstención correcta, falsas abstenciones, formato e idioma.
  - Tabla C: LLMs (coste) por escenario/embedding: tokens/s, latencia total, VRAM pico.

Decisión (reglas de la fase 4):
  1. Se aplican primero los umbrales (umbrales.csv, o defectos del README).
     Lo que no cumple se descarta.
  2. De los que cumplen, se elige el más barato (menos VRAM, más tokens/s, menos
     latencia) → la recomendación por escenario: "Para <escenario> usaría <llm>
     porque ...".
  3. Plan B: misma tabla sin los umbrales del "ejemplo orientativo" y con los
     más estrictos.

Uso: .venv/bin/python generar_decisiones.py
"""

import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FOLDERS = {"Artic": "Artic/arctic-embed-l-v2.0", "BGE": "BGE/bge-m3", "Multilingual": "Multilingual/e5-large"}
LLMS = {
    "qwen2.5-3b": ("Qwen/Qwen2.5-3B-Instruct", "3B", "pequeno"),
    "smollm2-1.7b": ("HuggingFaceTB/SmolLM2-1.7B-Instruct", "1.7B", "pequeno"),
    "qwen2.5-7b": ("Qwen/Qwen2.5-7B-Instruct", "7B", "mediano"),
    "mistral-7b": ("mistralai/Mistral-7B-Instruct-v0.3", "7B", "mediano"),
}
PARAMS_EST = {"qwen2.5-3b": 3.0, "smollm2-1.7b": 1.7, "qwen2.5-7b": 7.0, "mistral-7b": 7.0}

DEFAULT_UMBRALES = {
    "recall5": 0.80,
    "fidelidad": 90,
    "falsas_abst": 10,
    "formato": 85,
}


def read_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def parse_f(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def tabla_A(rows_escenario):
    print(f"\nTabla A (embeddings) — escenario(s): {', '.join(rows_escenario)}")
    hdr = f"{'Embedding':26s} {'B':>6s} {'DIM':>5s} {'Recall@1':>8s} {'Recall@3':>8s} {'Recall@5':>8s} {'MRR':>6s} {'Idx(s)':>7s} {'Idx(MB)':>8s} {'VRAM(GB)':>9s}"
    print(hdr)
    print("-" * len(hdr))
    lines = []
    for esc, r in sorted(rows_escenario.items()):
        rec1 = r["recall_1"] or "-"
        rec3 = r["recall_3"] or "-"
        rec5 = r["recall_5"] or "-"
        mrr = r["mrr"] or "-"
        idx_mb = (int(r["indice_bytes"]) / 1e6) if r["indice_bytes"] else "-"
        line = (f"{r['embedding']:26s} {r['params_millones']:>6.1f} {r['embedding_dim']:>5d} "
                f"{rec1:>8s} {rec3:>8s} {rec5:>8s} {mrr:>6s} "
                f"{r['tiempo_indexado_s'] or '-':>7s} {idx_mb:>8.1f} {r['vram_pico_gb'] or '-':>9s}")
        print(line)
        lines.append(f"| {r['embedding']} | {r['params_millions']} | {r['embedding_dim']} | "
                     f"{rec1} | {rec3} | {rec5} | {mrr} | {r['tiempo_indexado_s'] or '-'} | "
                     f"{round(idx_mb, 1) if idx_mb != '-' else '-'} | {r['vram_pico_gb'] or '-'} |")
    return lines


def agg_llm(punt_rows):
    n = len(punt_rows)
    corr = [parse_f(r["correccion"]) for r in punt_rows]
    corr = [c for c in corr if c is not None]
    fidel = [r["fidelidad"] for r in punt_rows]
    abst = [r["abstencion"] for r in punt_rows]
    abst_ok = [r["abstencion"] for r in punt_rows]
    formato = [r["formato_e_idioma"] for r in punt_rows]
    golden = PUNT_GOLDEN  # {id: tipo}
    n_sin = sum(1 for r in punt_rows if golden.get(r["pregunta_id"]) == "sin_respuesta")
    n_con = sum(1 for r in punt_rows if golden.get(r["pregunta_id"]) != "sin_respuesta")
    abst_correcta = sum(1 for r in punt_rows if r["abstencion"] == "si" and golden.get(r["pregunta_id"]) == "sin_respuesta")
    falsas_abst = sum(1 for r in punt_rows if r["abstencion"] == "si" and golden.get(r["pregunta_id"]) != "sin_respuesta")
    return {
        "n": n,
        "correccion_media": round(sum(corr) / len(corr), 2) if corr else "-",
        "fidelidad_pct": round(100 * sum(1 for x in fidel if x == "si") / n, 1) if n else "-",
        "abst_correcta": (round(100 * abst_correcta / n_sin, 1) if n_sin else "-"),
        "falsas_abst": round(100 * falsas_abst / n_con, 1) if n_con else "-",
        "formato_e_idioma_pct": round(100 * sum(1 for x in formato if x == "si") / n, 1) if n else "-",
    }


def tabla_B(puntu, escenarios, embedding):
    print(f"\nTabla B (LLMs calidad) — escenario(s): {', '.join(escenarios)}")
    hdr = f"{'LLM':14s} {'Corr':>5s} {'Fidel%':>7s} {'AbstOK':>7s} {'FalAbst':>8s} {'Formato%':>8s}"
    print(hdr)
    print("-" * len(hdr))
    lines = []
    for esc in escenarios:
        print(f"[{esc}]")
        for llm, (model_id, _, _) in LLMS.items():
            rows = [p for p in puntu if p["escenario"] == esc and p["embedding"] == embedding and p["llm"] == llm]
            if not rows:
                continue
            a = agg_llm(rows)
            print(f"  {llm:14s} {str(a['correccion_media']):>5s} {str(a['fidelidad_pct']):>7s} "
                  f"{str(a['abst_correcta']):>7s} {str(a['falsas_abst']):>8s} {str(a['formato_e_idioma_pct']):>8s}")
            lines.append((esc, llm, a))
    return lines


def tabla_C(coste):
    print("\nTabla C (LLMs coste) — note: TTFT y VRAM pico no se registran en los resultados")
    hdr = f"{'Escenario':7s} {'LLM':14s} {'Tokens/s':>8s} {'Latencia':>9s} {'VRAM':>5s}"
    print(hdr)
    print("-" * len(hdr))
    lines = []
    for r in coste:
        lat = r["median_latencia_s"] or "-"
        tps = r["median_tokens_por_s"] or "-"
        print(f"{r['escenario']:7s} {r['llm']:14s} {tps:>8s} {lat:>9s} {'-':>5s}")
        lines.append((r["escenario"], r["llm"], r["median_tokens_por_s"], r["median_latencia_s"]))
    return lines


PUNT_GOLDEN = {}


def load_golden():
    global PUNT_GOLDEN
    for esc in ("boe", "debian"):
        for p in read_csv(os.path.join(BASE_DIR, "BGE", f"{esc}_preguntas.txt")):
            PUNT_GOLDEN[p["id"]] = p["tipo"]


def decide(esc, embedding, b_rows, umbrales):
    """Devuelve la llave LLM recomendada para el escenario, o None."""
    cumplen = []
    for llm, (_, _, _) in LLMS.items():
        rows = [r for r in b_rows if r[1] == llm]
        if not rows:
            continue
        a = agg_llm(rows)
        fidel = parse_f(a["fidelidad_pct"]) or 0
        falsas = parse_f(a["falsas_abst"]) or 99
        formato = parse_f(a["formato_e_idioma_pct"]) or 0
        abst_ok = parse_f(a["abst_correcta"]) or 0
        ok = (
            fidel >= umbrales.get("fidelidad", DEFAULT_UMBRALES["fidelidad"])
            and falsas <= umbrales.get("falsas_abst", DEFAULT_UMBRALES["falsas_abst"])
            and formato >= umbrales.get("formato", DEFAULT_UMBRALES["formato"])
            and (parse_f(a["correccion_media"]) is None or parse_f(a["correccion_media"]) >= 0.5)
            and abst_ok >= umbrales.get("abst_correcta", 2.0 / 3.0 * 100)
        )
        if ok:
            costo = PARAMS_EST[llm] + (parse_f(COSTE_MED.get((esc, embedding, llm), {}).get("median_latencia_s")) or 0)
            cumplen.append((costo, llm, a))
    if not cumplen:
        return None, []
    cumplen.sort(key=lambda x: x[0])
    return cumplen[0][1], cumplen


COSTE_MED = {}


def main():
    load_golden()
    metricas = read_csv(os.path.join(BASE_DIR, "metricas_retrieval.csv"))
    puntu = read_csv(os.path.join(BASE_DIR, "puntuaciones.csv"))
    coste = read_csv(os.path.join(BASE_DIR, "coste.csv"))
    global COSTE_MED
    COSTE_MED = {(r["escenario"], r["embedding"], r["llm"]): r for r in coste}

    umbrales = read_csv(os.path.join(BASE_DIR, "umbrales.csv"))
    umb = {r["llm"]: r for r in umbrales} or {}

    if not puntu:
        print("AVISO: puntuaciones.csv vacías o inexistente. Primero completa Fase 3a.")
    if not metricas:
        print("AVISO: metricas_retrieval.csv vacío o inexistente. Primero completa Fase 2.")

    # Winners de embeddings por escenario (criterio: Recall@5, MRR, coste).
    from collections import defaultdict
    emb_rows = defaultdict(dict)
    for r in metricas:
        emb_rows[r["escenario"]][r["embedding"]] = r

    print("=" * 70)
    print("FASE 4: decisiones por escenario")
    print("=" * 70)
    tabla_A(emb_rows)

    decisiones = {}
    for esc in ("boe", "debian"):
        if not metricas or not puntu:
            decisiones[esc] = None
            continue
        emb_scores = []
        for embedding in emb_rows[esc]:
            r = emb_rows[esc][embedding]
            rec5 = parse_f(r["recall_5"]) or 0
            mrr = parse_f(r["mrr"]) or 0
            coste_i = parse_f(r["tiempo_indexado_s"]) or 0
            emb_scores.append((rec5, mrr, -coste_i, embedding))
        if not emb_scores:
            continue
        emb_scores.sort(reverse=True)
        embedding_win = emb_scores[0][3]
        print(f"\n### Escenario: {esc} — embedding ganador: {embedding_win} (Recall@5={emb_scores[0][0]:.2f})")

        b_rows = tabla_B([p for p in puntu if p["escenario"] == esc], [esc], embedding_win)
        c_rows = tabla_C([r for r in coste if r["escenario"] == esc and r["embedding"] == embedding_win])

        llm_rec, cumplen = decide(esc, embedding_win, b_rows, umb)
        if llm_rec:
            print(f"\n> Recomendación {esc}: usar {llm_rec} ({LLMS[llm_rec][0]}, {LLMS[llm_rec][1]})")
            cum = [x for x in cumplen if x[1] == llm_rec]
            if cum:
                print(f"> Razonamiento: cumple los umbrales y es el más barato; llms disponibles que cumplen: "
                      f"{sorted(set(x[1] for x in cumplen))}")
        decisiones[esc] = llm_rec

    print("\n### Resumen de decisiones")
    for esc, d in decisiones.items():
        if d:
            print(f"{esc}: {d}")
        else:
            print(f"{esc}: pendiente de resultados (completa Fase 3a)")


if __name__ == "__main__":
    main()
