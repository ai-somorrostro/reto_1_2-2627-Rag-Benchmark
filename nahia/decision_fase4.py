#!/usr/bin/env python3
"""Fase 4: aplica los umbrales de comun/umbrales.md a todos los modelos puntuados.

Uso:  python decision_fase4.py [--vram-max 20]      (plan B: --vram-max 8)
Lee nahia/resultados/*_meta.json y sus _puntuacion.csv (ya puntuados a mano).
Escribe tablas/decision_fase4_<vram>GB.md con, por escenario, qué modelos cumplen,
cuáles se descartan y por qué, y cuál es el más barato entre los que cumplen.
"""
import argparse
import csv
import glob
import json
import statistics
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SI = {"si", "sí", "s", "yes", "y", "1", "true"}
U = dict(fieles=90, abst=2, falsas=1, correccion=1.5, formato=90, latencia=5.0)


def metricas(ruta_meta):
    meta = json.load(open(ruta_meta, encoding="utf-8"))
    d = ruta_meta.parent
    jsonl = d / meta["fichero_respuestas"]
    hoja = d / f"{jsonl.stem}_puntuacion.csv"
    punt = list(csv.DictReader(open(hoja, encoding="utf-8-sig", newline="")))
    if any(not p["correccion_0_2"].strip() for p in punt):
        return None, f"sin puntuar: {hoja.name}"
    es = lambda v: v.strip().lower() in SI
    n = len(punt)
    sin = [p for p in punt if p["tipo"] == "sin_respuesta"]
    con = [p for p in punt if p["tipo"] != "sin_respuesta"]
    filas = [json.loads(l) for l in open(jsonl, encoding="utf-8") if l.strip()]
    por_q = {}
    for r in filas:
        if r["para_coste"] and not r.get("descartada"):
            por_q.setdefault(r["pregunta_id"], []).append(r)
    med = lambda c: statistics.median(statistics.median([r[c] for r in v if r[c] is not None]) for v in por_q.values())
    return {
        "modelo": meta["modelo"] + ("" if meta["cuantizacion"] == "bf16" else f" ({meta['cuantizacion']})"), "embedding": meta["embedding"], "fecha": meta["fecha_hora"], "escenario": meta["escenario"], "oficial": meta["turno_exclusivo"],
        "correccion": sum(float(p["correccion_0_2"]) for p in punt) / n,
        "fieles": 100 * sum(es(p["fiel_si_no"]) for p in punt) / n,
        "abst": sum(es(p["se_abstiene_si_no_na"]) for p in sin),
        "falsas": sum(es(p["se_abstiene_si_no_na"]) for p in con),
        "formato": 100 * sum(es(p["formato_idioma_si_no"]) for p in punt) / n,
        "latencia": med("latencia_total_s"), "tps": med("tokens_por_s"),
        "vram": meta["vram_pico_nvidia_smi_gb"],
    }, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vram-max", type=float, default=20)
    a = ap.parse_args()
    ganadores = json.load(open(AQUI / "ganadores_embedding.json", encoding="utf-8"))
    ms, avisos = [], []
    norm = lambda e: (e or "").replace("../", "")
    grupos = {}  # (modelo, escenario) -> lista de ejecuciones del embedding ganador
    for f in sorted(glob.glob(str(AQUI / "resultados" / "*_meta.json"))):
        meta = json.load(open(f, encoding="utf-8"))
        if norm(meta["embedding"]) != ganadores[meta["escenario"]]:
            continue
        if meta["cuantizacion"] != "bf16" and a.vram_max > 8:
            continue  # las ejecuciones en 4 bits solo cuentan en el plan B (--vram-max 8)  # ejecución con un embedding que no es el ganador: no cuenta
        m, av = metricas(Path(f))
        grupos.setdefault((meta["modelo"], meta["cuantizacion"], meta["escenario"]), []).append((meta["fecha_hora"], m, av))
    for clave, ejecs in grupos.items():
        ejecs.sort(key=lambda x: x[0])
        puntuadas = [e for e in ejecs if e[1]]
        if puntuadas:
            ms.append(puntuadas[-1][1])  # la última ejecución ya puntuada
        for e in ejecs:
            if not e[1] and (not puntuadas or e[0] > puntuadas[-1][0]):
                avisos.append(e[2])
    out = [f"# Decisión Fase 4 (VRAM máx. {a.vram_max} GB)\n"]
    # Primer filtro (README: retrieval antes que LLM): Recall@5 del mejor embedding oficial, umbral >= 0,80
    r5 = {}
    for f in sorted(glob.glob(str(AQUI.parent / "sendoa" / "resultados_oficiales" / "*.json"))):
        try:
            d = json.load(open(f, encoding="utf-8"))
            if d["coste"].get("turno_exclusivo") and d["meta"]["escenario"] in ("boe", "debian"):
                r5.setdefault(d["meta"]["escenario"], {})[d["meta"]["modelo"]] = d["metricas"]["recall@5"]
        except (KeyError, ValueError, TypeError):
            pass
    for esc in ("boe", "debian"):
        out.append(f"\n## {esc.upper()}\n")
        mejor = max(r5.get(esc, {"-": 0}).values())
        if mejor < 0.80:
            out.append(f"**Retrieval: el mejor Recall@5 es {mejor:.3f} (< 0,80). Para {esc.upper()} no se recomienda este RAG tal cual: primero hay que mejorar el retrieval; los LLM de abajo se evalúan igualmente.**\n")
        else:
            out.append(f"Retrieval: mejor Recall@5 = {mejor:.3f} (>= 0,80, cumple).\n")
        cumplen = []
        for m in [x for x in ms if x["escenario"] == esc]:
            fallos = []
            if m["fieles"] < U["fieles"]: fallos.append(f"fieles {m['fieles']:.0f}%")
            if m["abst"] < U["abst"]: fallos.append(f"abstención {m['abst']}/3")
            if m["falsas"] > U["falsas"]: fallos.append(f"falsas abst. {m['falsas']}")
            if m["correccion"] < U["correccion"]: fallos.append(f"corrección {m['correccion']:.2f}")
            if m["formato"] < U["formato"]: fallos.append(f"formato {m['formato']:.0f}%")
            if m["latencia"] > U["latencia"]: fallos.append(f"latencia {m['latencia']:.1f}s")
            if m["vram"] > a.vram_max: fallos.append(f"VRAM {m['vram']} GB")
            estado = "CUMPLE" if not fallos else "DESCARTADO: " + ", ".join(fallos)
            if not m["oficial"]: estado += " (medida NO oficial)"
            out.append(f"- {m['modelo']}: corrección {m['correccion']:.2f}, fieles {m['fieles']:.0f}%, abst. {m['abst']}/3, "
                       f"falsas {m['falsas']}, formato {m['formato']:.0f}%, lat. {m['latencia']:.2f}s, "
                       f"{m['tps']:.1f} tok/s, VRAM {m['vram']} GB -> {estado}")
            if not fallos: cumplen.append(m)
        if cumplen:
            g = min(cumplen, key=lambda m: (m["vram"], -m["tps"], m["latencia"]))
            out.append(f"\n**Para {esc.upper()} el más barato que cumple: {g['modelo']}** "
                       f"(VRAM {g['vram']} GB, {g['tps']:.1f} tok/s, latencia {g['latencia']:.2f} s).")
        elif any(x["escenario"] == esc for x in ms):
            out.append("\n**Ningún modelo cumple todos los umbrales en este escenario.**")
        else:
            out.append("Sin modelos puntuados todavía.")
    if avisos:
        out.append("\n## Pendiente de puntuar\n" + "\n".join(f"- {x}" for x in avisos))
    (AQUI / "tablas").mkdir(exist_ok=True)
    destino = AQUI / "tablas" / f"decision_fase4_{a.vram_max:g}GB.md"
    destino.write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
