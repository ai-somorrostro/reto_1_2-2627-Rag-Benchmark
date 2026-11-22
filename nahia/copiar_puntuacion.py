#!/usr/bin/env python3
"""Copia las notas ya validadas a una ejecución nueva cuando las respuestas son IDÉNTICAS.

Con temperatura 0 el mismo modelo, prompt y fragmentos dan la misma respuesta. Si el notebook
vuelve a ejecutar un modelo, las respuestas nuevas son las mismas y no hace falta puntuar de nuevo.
Solo copia pregunta a pregunta si el texto de la respuesta coincide letra por letra; si alguna
difiere, esa fila se deja VACÍA para puntuarla a mano.
Uso: python copiar_puntuacion.py
"""
import csv, glob, json
from pathlib import Path
AQUI = Path(__file__).resolve().parent
R = AQUI / "resultados"

def respuestas(meta):
    f = R / meta["fichero_respuestas"]
    return {j["pregunta_id"]: j["respuesta"] for j in map(json.loads, open(f, encoding="utf-8")) if j["repeticion"] == 1}

def hoja(meta):
    return R / (Path(meta["fichero_respuestas"]).stem + "_puntuacion.csv")

metas = []
for f in sorted(glob.glob(str(R / "*_meta.json"))):
    m = json.load(open(f, encoding="utf-8")); m["_f"] = f; metas.append(m)
puntuada = lambda m: all((r["correccion_0_2"] or "").strip() for r in csv.DictReader(open(hoja(m), encoding="utf-8-sig")) if r["pregunta_id"])
for nueva in metas:
    if puntuada(nueva):
        continue
    previas = [m for m in metas if m["modelo"] == nueva["modelo"] and m["escenario"] == nueva["escenario"]
               and m["embedding"].replace("../", "") == nueva["embedding"].replace("../", "")
               and m["fecha_hora"] < nueva["fecha_hora"] and puntuada(m)]
    if not previas:
        continue
    prev = previas[-1]
    rn, rp = respuestas(nueva), respuestas(prev)
    hn = list(csv.DictReader(open(hoja(nueva), encoding="utf-8-sig")))
    hp = {r["pregunta_id"]: r for r in csv.DictReader(open(hoja(prev), encoding="utf-8-sig"))}
    copiadas = 0
    for r in hn:
        q = r["pregunta_id"]
        if q in hp and rn.get(q) == rp.get(q):
            for k in ("correccion_0_2", "fiel_si_no", "se_abstiene_si_no_na", "formato_idioma_si_no", "puntuado_por"):
                r[k] = hp[q][k]
            copiadas += 1
    with open(hoja(nueva), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(hn[0].keys())); w.writeheader(); w.writerows(hn)
    print(f"{nueva['modelo']} {nueva['escenario']}: {copiadas}/{len(hn)} notas copiadas de {Path(prev['_f']).name[:40]}")
