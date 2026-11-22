"""Fase 4: decisiones por escenario a partir de puntuaciones + umbrales.

Lee metricas_retrieval.csv, puntuaciones.csv y coste.csv (resultados de la
fase 2 y fase 3a) y escribe por stdout:

  - Tabla A: embeddings por escenario (Recall@1/3/5, MRR, indexado, Índice, VRAM).
  - Tabla B: LLMs (calidad) por escenario/embedding: corrección media, fidelidad,
    abstención correcta, falsas abstenciones, formato e idioma.
  - Tabla C: LLMs (coste) por escenario/embedding: tokens/s, latencia total.

Decisión (reglas de la fase 4):
  1. Se aplican primero los umbrales (umbrales.csv, o defectos del README).
     Lo que no cumple se descarta.
  2. De los que cumplen, se elige el más barato (menos VRAM, más tokens/s, menos
     latencia) → la recomendación por escenario: "Para <escenario> usaría <llm>
     porque ...".
  3. Plan B: llms que cumplen sin umbrales tan estrictos.

Uso: .venv/bin/python generar_decisiones.py
"""

import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LLMS = {
    "qwen2.5-3b": ("Qwen/Qwen2.5-3B-Instruct", "3B", "pequeno"),
    "smollm2-1.7b": ("HuggingFaceTB/SmolLM2-1.7B-Instruct", "1.7B", "pequeno"),
    "qwen2.5-7b": ("Qwen/Qwen2.5-7B-Instruct", "7B", "mediano"),
    "mistral-7b": ("mistralai/Mistral-7B-Instruct-v0.3", "7B", "mediano"),
}
PARAMS_EST = {"qwen2.5-3b": 3.0, "smollm2-1.7b": 1.7, "qwen2.5-7b": 7.0, "mistral-7b": 7.0}

DEFAULT_UMBRALES = {
    "fidelidad": 90,
    "falsas_abst": 10,
    "formato": 85,
    "abst_correcta": 2.0 / 3.0 * 100,
    "correcion": 0.5,
    "recall5": 0.80,
}

PUNT_GOLDEN = {}


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


def agg_llm(rows):
    n = len(rows)
    if n == 0:
        return {"n": 0, "correccion_media": "-", "fidelidad_pct": "-",
                "abst_correcta": "-", "falsas_abst": "-", "formato_e_idioma_pct": "-"}
    corr = [c for c in (parse_f(r["correccion"]) for r in rows) if c is not None]
    fidel = sum(1 for r in rows if r["fidelidad"] == "si")
    formato = sum(1 for r in rows if r["formato_e_idioma"] == "si")
    abst_rows = [r for r in rows if PUNT_GOLDEN.get(r["pregunta_id"]) == "sin_respuesta"]
    con_resp = [r for r in rows if PUNT_GOLDEN.get(r["pregunta_id"]) != "sin_respuesta"]
    abst_correcta = sum(1 for r in abst_rows if r["abstencion"] == "si")
    falsas_abst = sum(1 for r in con_resp if r["abstencion"] == "si")
    return {
        "n": n,
        "correccion_media": round(sum(corr) / len(corr), 2) if corr else "-",
        "fidelidad_pct": round(100 * fidel / n, 1),
        "abst_correcta": round(100 * abst_correcta / len(abst_rows), 1) if abst_rows else "-",
        "falsas_abst": round(100 * falsas_abst / len(con_resp), 1) if con_resp else "-",
        "formato_e_idioma_pct": round(100 * formato / n, 1),
    }


def umbrales_parse(umb_rows):
    umb = {r["llm"]: r for r in umb_rows}
    out = {}
    for llm in LLMS:
        row = umb.get(llm, {}) or {}
        out[llm] = {
            "fidelidad": parse_f(row.get("fidelidad", DEFAULT_UMBRALES["fidelidad"])),
            "falsas_abst": parse_f(row.get("falsas_abst", DEFAULT_UMBRALES["falsas_abst"])),
            "formato": parse_f(row.get("formato", DEFAULT_UMBRALES["formato"])),
            "abst_correcta": parse_f(row.get("abst_correcta", DEFAULT_UMBRALES["abst_correcta"])),
        }
    return out


def decide(esc, embedding, b_rows, umb, coste_med):
    """Devuelve [(costo, llm, agg), ...] de llms que cumplen los umbrales."""
    cumplen = []
    for llm in LLMS:
        a = next((x[2] for x in b_rows if x[0] == esc and x[1] == llm), None)
        if not a:
            continue
        corr_media = parse_f(a["correccion_media"])
        fidel = parse_f(a["fidelidad_pct"])
        formato = parse_f(a["formato_e_idioma_pct"])
        falsas = parse_f(a["falsas_abst"])
        abst_ok = parse_f(a["abst_correcta"])
        u = umb[llm]
        ok = (
            (fidel is not None and fidel >= u["fidelidad"])
            and (formato is not None and formato >= u["formato"])
            and (falsas is not None and falsas <= u["falsas_abst"])
            and (abst_ok is not None and abst_ok >= u["abst_correcta"])
            and (corr_media is None or corr_media >= u["correcion"])
        )
        if ok:
            lat = parse_f(coste_med.get((esc, embedding, llm), {}).get("median_latencia_s")) or 0
            cumplen.append((PARAMS_EST[llm] + lat, llm, a))
    cumplen.sort(key=lambda x: x[0])
    return cumplen


def tabla_A(rows_escenario):
    print("\nTabla A (embeddings)")
    print(f"{'Embedding':26s} {'Params':>6s} {'Dim':>4s} {'Recall@1':>8s} {'Recall@3':>8s} "
          f"{'Recall@5':>8s} {'MRR':>6s} {'Idx(s)':>7s} {'Idx(MB)':>7s} {'VRAM(GB)':>8s}")
    for r in sorted(rows_escenario.values(), key=lambda x: parse_f(x["recall_5"]) or 0, reverse=True):
        idx_mb = (int(r["indice_bytes"]) / 1e6) if r.get("indice_bytes") else "-"
        idx_mb = round(idx_mb, 1) if idx_mb != "-" else "-"
        print(f"{r['embedding']:26s} {str(r.get('params_millions', '-')):>6s} "
              f"{str(r.get('embedding_dim', '-')):>4s} "
              f"{r['recall_1'] or '-':>8s} {r['recall_3'] or '-':>8s} {r['recall_5'] or '-':>8s} "
              f"{r['mrr'] or '-':>6s} {r['tiempo_indexado_s'] or '-':>7s} {idx_mb:>7s} "
              f"{r['vram_pico_gb'] or '-':>8s}")


def tabla_B(puntu, escenarios, embedding):
    print("\nTabla B (LLMs calidad)")
    print(f"{'LLM':14s} {'CorrMedia':>9s} {'Fidel%':>7s} {'AbstOK':>7s} {'FalsesAbst':>10s} {'Formato%':>8s}")
    out = []
    for esc in escenarios:
        for llm in LLMS:
            rows = [p for p in puntu if p["escenario"] == esc and p["embedding"] == embedding and p["llm"] == llm]
            if not rows:
                continue
            a = agg_llm(rows)
            print(f"[{esc}] {llm:14s} {a['correccion_media']:>9s} {a['fidelidad_pct']:>7.1f} "
                  f"{a['abst_correcta']:>7s} {a['falsas_abst']:>10s} {a['formato_e_idioma_pct']:>8.1f}")
            out.append((esc, llm, a))
    return out


def tabla_C(coste):
    print("\nTabla C (LLMs coste) — nota: TTFT y VRAM pico no se registran")
    print(f"{'Escenario':7s} {'LLM':14s} {'Tokens/s':>8s} {'Latencia(s)':>11s} {'VRAM(GB)':>8s}")
    for r in coste:
        print(f"{r['escenario']:7s} {r['llm']:14s} {r['median_tokens_por_s'] or '-':>8s} "
              f"{r['median_latencia_s'] or '-':>11s} {'-':>8s}")
    return []


def main():
    for esc in ("boe", "debian"):
        for p in read_csv(os.path.join(BASE_DIR, "BGE", f"{esc}_preguntas.txt")):
            PUNT_GOLDEN[p["id"]] = p["tipo"]

    metricas = read_csv(os.path.join(BASE_DIR, "metricas_retrieval.csv"))
    puntu = read_csv(os.path.join(BASE_DIR, "puntuaciones.csv"))
    coste = read_csv(os.path.join(BASE_DIR, "coste.csv"))
    umb_path = os.path.join(BASE_DIR, "umbrales.csv")
    if not os.path.exists(umb_path):
        with open(umb_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["llm", "fidelidad", "falsas_abst", "formato", "abst_correcta"])
            w.writeheader()
            for llm in LLMS:
                w.writerow({k: DEFAULT_UMBRALES[k] for k in ["fidelidad", "falsas_abst", "formato", "abst_correcta"]} | {"llm": llm})
        print("Creado plantilla umbrales.csv (rellena los umbrales antes de decidir)")
    umb_rows = read_csv(umb_path)
    umb = umbrales_parse(umb_rows)

    if not puntu:
        print("AVISO: puntuaciones.csv vacías o inexistente. Primero completa Fase 3a.")
    if not metricas:
        print("AVISO: metricas_retrieval.csv vacío o inexistente. Primero completa Fase 2.")

    emb_rows = {esc: {r["embedding"]: r for r in metricas if r["escenario"] == esc}
                for esc in ("boe", "debian")}

    print("=" * 78)
    print("FASE 4: decisiones por escenario")
    print("=" * 78)
    for esc in ("boe", "debian"):
        tabla_A(emb_rows[esc])

    decisiones = {}
    for esc in ("boe", "debian"):
        if not metricas or not puntu:
            decisiones[esc] = None
            continue
        emb_scores = sorted(
            ((parse_f(r["recall_5"]) or 0, parse_f(r["mrr"]) or 0,
              -(parse_f(r["tiempo_indexado_s"]) or 0), e) for e, r in emb_rows[esc].items()),
            reverse=True,
        )
        embedding_win = emb_scores[0][3]
        print(f"\n### Escenario: {esc} — embedding ganador: {embedding_win} "
              f"(Recall@5={emb_scores[0][0]:.2f}, MRR={emb_scores[0][1]:.2f})")

        b_rows = tabla_B([p for p in puntu if p["escenario"] == esc], [esc], embedding_win)
        tabla_C([r for r in coste if r["escenario"] == esc and r["embedding"] == embedding_win])

        cumplen = decide(esc, embedding_win, b_rows, umb,
                         {k: v for k, v in (((r["escenario"], r["embedding"], r["llm"]), r) for r in coste)})
        if cumplen:
            llm_rec = cumplen[0][1]
            print(f"> Recomendación {esc}: usar {llm_rec} ({LLMS[llm_rec][0]}, {LLMS[llm_rec][1]})")
            print(f"> Cumplen: {[c[1] for c in cumplen]} | Descartados: "
                  f"{[llm for llm in LLMS if llm not in [c[1] for c in cumplen]]}")
        else:
            llm_rec = None
            print("> Ningún LLM cumple los umbrales seleccionados; revisa umbrales.csv o REVISAR.")
        decisiones[esc] = llm_rec

    print("\n### Resumen de decisiones")
    for esc, d in decisiones.items():
        print(f"{esc}: {d if d else 'pendiente de resultados (completa Fase 3a)'}")


if __name__ == "__main__":
    main()
