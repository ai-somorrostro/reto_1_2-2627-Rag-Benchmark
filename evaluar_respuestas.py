"""Fase 3a: extracción de resultados BOE (respuestas LLM + coste).

Lee los ficheros de resultados generados por los benchmarks (Artic, BGE,
Multilingual) para los dos escenarios (boe, debian) y genera:

  - puntuaciones.csv: una fila por respuesta LLM. Incluye los datos extraídos
    (respuesta LLM, latencia, tokens, abstención detectada, ...) y campos
    vacíos para puntuar a mano: correccion (0-2), fidelidad (si/no),
    abstencion (si/no/no aplica) y formato_e_idioma (si/no).

  - coste.csv: una fila por (escenario, embedding, llm) con la mediana de
    latencia total y de tokens/s sobre los registros disponibles.

Uso: .venv/bin/python evaluar_respuestas.py
"""

import csv
import os
import re
import statistics

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FOLDERS = {
    "Artic": "Artic/arctic-embed-l-v2.0",
    "BGE": "BGE/bge-m3",
    "Multilingual": "Multilingual/e5-large",
}
LLMS = ["qwen2.5-3b", "smollm2-1.7b", "qwen2.5-7b", "mistral-7b"]

RECORDS_RE = re.compile(
    r"^\[(?P<ts>[^\]]+)\] Escenario: (?P<esc>\w+) \| Pregunta: (?P<id>\S+)\n"
    r"(?P<body>.*?)\n?(?=^-{70}$|\Z)",
    re.S | re.M,
)


def load_golden(escenario):
    path = os.path.join(BASE_DIR, "BGE", f"{escenario}_preguntas.txt")
    with open(path, encoding="utf-8") as f:
        return {r["id"]: r for r in csv.DictReader(f)}


def parse_result_file(ruta):
    rows = []
    texto = open(ruta, encoding="utf-8").read()
    for m in RECORDS_RE.finditer(texto):
        body = m.group("body")
        mm = re.search(r"^Pregunta: (.*)$", body, re.M)
        pregunta = mm.group(1).strip() if mm else ""
        mm = re.search(r"^Categoria: (.*)$", body, re.M)
        categoria = mm.group(1).split("|")[0].strip() if mm else ""
        mm = re.search(r"^Dificultad: (.*)$", body, re.M)
        dificultad = mm.group(1).strip() if mm else ""
        mm = re.search(r"^Respuesta esperada: (.*)$", body, re.M)
        esperada = mm.group(1).strip() if mm else ""

        partes = re.split(r"^--- Respuesta LLM ---\s*$", body, flags=re.M)
        if len(partes) > 1:
            after = partes[1]
            partes2 = re.split(r"^--- Datos ---\s*$", after, flags=re.M)
            respuesta = partes2[0].strip()
            datos = partes2[1] if len(partes2) > 1 else ""
        else:
            respuesta, datos = "", ""

        lat = re.search(r"latencia_total_s=([\d.]+)", datos)
        tokens = re.search(r"tokens_generados=(\d+)", datos)
        tps = re.search(r"tokens_por_s=([\d.]+)", datos)
        score = re.search(r"score_max=([\d.]+)", datos)
        abst = re.search(r"abstencion_detectada=(\w+)", datos)
        rows.append(
            {
                "ts": m.group("ts"),
                "pregunta_id": m.group("id"),
                "respuesta_esperada": esperada,
                "pregunta": pregunta,
                "categoria": categoria,
                "dificultad": dificultad,
                "respuesta_llm": respuesta,
                "latencia_total_s": float(lat.group(1)) if lat else None,
                "tokens_generados": int(tokens.group(1)) if tokens else None,
                "tokens_por_s": float(tps.group(1)) if tps else None,
                "score_max": float(score.group(1)) if score else None,
                "abstencion_detectada": abst.group(1) if abst else "",
            }
        )
    return rows


def main():
    puntuaciones = []
    coste = []
    for folder, embedding in FOLDERS.items():
        for escenario in ("boe", "debian"):
            golden = load_golden(escenario)
            carpeta = os.path.join(BASE_DIR, folder, f"resultados_{escenario}")
            for llm in LLMS:
                ruta = os.path.join(carpeta, f"resultados_{llm}.txt")
                rows = parse_result_file(ruta) if os.path.exists(ruta) else []
                lat = [r["latencia_total_s"] for r in rows if r["latencia_total_s"] is not None]
                tps = [r["tokens_por_s"] for r in rows if r["tokens_por_s"] is not None]
                coste.append(
                    {
                        "escenario": escenario,
                        "embedding": embedding,
                        "llm": llm,
                        "n_registros": len(rows),
                        "median_latencia_s": round(statistics.median(lat), 2) if lat else None,
                        "mean_latencia_s": round(statistics.mean(lat), 2) if lat else None,
                        "median_tokens_por_s": round(statistics.median(tps), 1) if tps else None,
                        "max_tokens_por_s": round(max(tps), 1) if tps else None,
                    }
                )
                for r in rows:
                    g = golden.get(r["pregunta_id"], {})
                    puntuaciones.append(
                        {
                            "escenario": escenario,
                            "embedding": embedding,
                            "llm": llm,
                            "pregunta_id": r["pregunta_id"],
                            "tipo": g.get("tipo", ""),
                            "pregunta": r["pregunta"] or g.get("pregunta", ""),
                            "referencia": g.get("referencia", ""),
                            "categoria": r["categoria"] or g.get("categoria", ""),
                            "dificultad": r["dificultad"] or g.get("dificultad", ""),
                            "respuesta_esperada": r["respuesta_esperada"] or g.get("respuesta_correcta", ""),
                            "respuesta_llm": r["respuesta_llm"],
                            "latencia_total_s": r["latencia_total_s"],
                            "tokens_generados": r["tokens_generados"],
                            "tokens_por_s": r["tokens_por_s"],
                            "score_max": r["score_max"],
                            "abstencion_detectada": r["abstencion_detectada"],
                            "correccion": "",
                            "fidelidad": "",
                            "abstencion": "",
                            "formato_e_idioma": "",
                        }
                    )
                print(f"{embedding:26s} {escenario:7s} {llm:15s} n={len(rows):3d} "
                      f"med_lat={statistics.median(lat) if lat else float('nan'):6.2f}s")

    puntu_out = os.path.join(BASE_DIR, "puntuaciones.csv")
    campos = [
        "escenario", "embedding", "llm", "pregunta_id", "tipo", "pregunta",
        "referencia", "categoria", "dificultad", "respuesta_esperada",
        "respuesta_llm", "latencia_total_s", "tokens_generados", "tokens_por_s",
        "score_max", "abstencion_detectada",
        "correccion", "fidelidad", "abstencion", "formato_e_idioma",
    ]
    with open(puntu_out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(puntuaciones)
    print("Guardado:", puntu_out, f"({len(puntuaciones)} filas)")

    coste_out = os.path.join(BASE_DIR, "coste.csv")
    campos_coste = ["escenario", "embedding", "llm", "n_registros",
                    "median_latencia_s", "mean_latencia_s",
                    "median_tokens_por_s", "max_tokens_por_s"]
    with open(coste_out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos_coste)
        w.writeheader()
        w.writerows(coste)
    print("Guardado:", coste_out)


if __name__ == "__main__":
    main()
