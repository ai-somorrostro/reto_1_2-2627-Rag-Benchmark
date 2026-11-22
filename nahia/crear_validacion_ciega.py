#!/usr/bin/env python3
"""Crea validacion_10/validacion_ciega.csv: 10 respuestas al azar (semilla fija) SIN las notas previas.
Las puntúa una persona a mano; luego comparar_validacion.py calcula cuántas coinciden con la hoja oficial."""
import csv, glob, json, random
from pathlib import Path
AQUI = Path(__file__).resolve().parent
ganadores = json.load(open(AQUI / "ganadores_embedding.json", encoding="utf-8"))
cand = []
for mf in sorted(glob.glob(str(AQUI / "resultados" / "*_meta.json"))):
    meta = json.load(open(mf, encoding="utf-8"))
    if meta["embedding"].replace("../", "") != ganadores[meta["escenario"]]:
        continue
    stem = Path(meta["fichero_respuestas"]).stem
    hoja = AQUI / "resultados" / f"{stem}_puntuacion.csv"
    notas = {r["pregunta_id"]: r for r in csv.DictReader(open(hoja, encoding="utf-8-sig")) if r["pregunta_id"]}
    for r in map(json.loads, open(AQUI / "resultados" / meta["fichero_respuestas"], encoding="utf-8")):
        if r["repeticion"] == 1 and notas.get(r["pregunta_id"], {}).get("correccion_0_2", "").strip():
            cand.append((meta["modelo"], meta["escenario"], stem, r))
random.Random(2026).shuffle(cand)
muestra, usados = [], set()
for c in cand:  # que no se repita la misma pregunta de la misma ejecución, y variedad de modelos
    if len(muestra) == 10: break
    if (c[2], c[3]["pregunta_id"]) not in usados and sum(1 for m in muestra if m[0] == c[0]) < 3:
        muestra.append(c); usados.add((c[2], c[3]["pregunta_id"]))
with open(AQUI / "validacion_10" / "validacion_ciega.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["n", "modelo", "escenario", "pregunta_id", "pregunta", "respuesta_esperada", "respuesta_del_modelo",
                "TU_correccion_0_2", "TU_se_abstiene_si_no", "puntuado_por", "_clave_fichero"])
    for n, (m, e, stem, r) in enumerate(muestra, 1):
        w.writerow([n, m, e, r["pregunta_id"], r["pregunta"], r["respuesta_esperada"], r["respuesta"], "", "", "", stem])
print("creado con", len(muestra), "respuestas")
