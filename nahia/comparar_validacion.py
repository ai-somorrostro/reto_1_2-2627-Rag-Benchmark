#!/usr/bin/env python3
"""Compara tus notas a ciegas (validacion_10/validacion_ciega.csv) con las de la hoja oficial y dice cuántas coinciden."""
import csv
from pathlib import Path
AQUI = Path(__file__).resolve().parent
filas = list(csv.DictReader(open(AQUI / "validacion_10" / "validacion_ciega.csv", encoding="utf-8-sig")))
if any(not r["TU_correccion_0_2"].strip() or not r["TU_se_abstiene_si_no"].strip() for r in filas):
    raise SystemExit("Faltan notas: rellena TU_correccion_0_2 y TU_se_abstiene_si_no en las 10 filas.")
ok_c = ok_a = 0; out = ["# Validación a ciegas de 10 respuestas\n"]
for r in filas:
    of = next(x for x in csv.DictReader(open(AQUI / "resultados" / f"{r['_clave_fichero']}_puntuacion.csv", encoding="utf-8-sig")) if x["pregunta_id"] == r["pregunta_id"])
    c = r["TU_correccion_0_2"].strip() == of["correccion_0_2"].strip()
    a = r["TU_se_abstiene_si_no"].strip().lower().replace("sí", "si") == of["se_abstiene_si_no_na"].strip().lower()
    ok_c += c; ok_a += a
    out.append(f"- {r['n']}. {r['modelo']} {r['escenario']} {r['pregunta_id']}: tu corrección {r['TU_correccion_0_2']} / hoja {of['correccion_0_2']} {'✔' if c else '✘'}; abstención {'✔' if a else '✘'}")
out.append(f"\n**Coinciden en corrección: {ok_c} de {len(filas)}. En abstención: {ok_a} de {len(filas)}.**\nPuntuado a ciegas por: {', '.join({r['puntuado_por'] for r in filas if r['puntuado_por']})}\n")
(AQUI / "validacion_10" / "resultado_validacion.md").write_text("\n".join(out), encoding="utf-8"); print("\n".join(out))
