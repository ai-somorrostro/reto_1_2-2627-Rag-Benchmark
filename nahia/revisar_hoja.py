#!/usr/bin/env python3
"""Revisión guiada de una hoja de puntuación, pregunta a pregunta.

Uso:  python nahia/revisar_hoja.py <hoja _puntuacion.csv> "<tu nombre>"
Por cada respuesta muestra la pregunta, la solución, lo que dijo el modelo y las notas actuales.
Pulsa ENTER para mantener una nota o escribe la nueva. Al final, si has pasado por las 15 preguntas,
escribe tu nombre en 'puntuado_por' y regenera las tablas. Si cortas antes (Ctrl+C) no se guarda nada.
"""
import csv, json, subprocess, sys
from pathlib import Path

if len(sys.argv) != 3:
    sys.exit(__doc__)
hoja, nombre = Path(sys.argv[1]), sys.argv[2].strip()
if not hoja.exists() or not hoja.name.endswith("_puntuacion.csv"):
    sys.exit("Indica una hoja que termine en _puntuacion.csv")
AQUI = Path(__file__).resolve().parent
stem = hoja.name.removesuffix("_puntuacion.csv")
jsonl = hoja.with_name(stem + ".jsonl")
resp = {r["pregunta_id"]: r for r in map(json.loads, open(jsonl, encoding="utf-8")) if r["repeticion"] == 1}
filas = [r for r in csv.DictReader(open(hoja, encoding="utf-8-sig")) if r["pregunta_id"]]
CAMPOS = [("correccion_0_2", "Corrección (0, 1 o 2)", {"0", "1", "2"}),
          ("fiel_si_no", "¿Fiel? (si/no)", {"si", "no"}),
          ("se_abstiene_si_no_na", "¿Se abstiene? (si/no)", {"si", "no"}),
          ("formato_idioma_si_no", "¿Español y cita artículo/sección? (si/no)", {"si", "no"})]
print("Reglas: 2 = correcta y completa, 1 = falta algo, 0 = incorrecta. Sin respuesta en el doc: 'No aparece' = 2.\n")
cambios = 0
try:
    for i, r in enumerate(filas, 1):
        d = resp[r["pregunta_id"]]
        print("=" * 78, f"\n[{i}/{len(filas)}] {r['pregunta_id']} ({r['tipo']})\nPREGUNTA: {d['pregunta']}\n\nSOLUCIÓN: {d['respuesta_esperada']}\n\nRESPUESTA DEL MODELO:\n{d['respuesta']}\n")
        for k, etiqueta, validos in CAMPOS:
            while True:
                v = input(f"  {etiqueta} [actual: {r[k]}] > ").strip().lower().replace("sí", "si")
                if v == "":
                    break
                if v in validos:
                    if v != r[k]:
                        cambios += 1
                    r[k] = v
                    break
                print(f"    Valor no válido. Opciones: {sorted(validos)}")
except (KeyboardInterrupt, EOFError):
    sys.exit("\nCortado: no se ha guardado nada.")
print(f"\nHas revisado las {len(filas)} respuestas y cambiado {cambios} notas.")
if input(f"¿Confirmas que las has revisado tú y firmar como '{nombre}'? (escribe si) > ").strip().lower() not in ("si", "sí"):
    sys.exit("No se ha guardado nada.")
for r in filas:
    r["puntuado_por"] = f"{nombre} (revisión manual)"
with open(hoja, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(filas[0].keys())); w.writeheader(); w.writerows(filas)
meta = hoja.with_name(stem + "_meta.json")
subprocess.run([sys.executable, str(AQUI / "tabla_bc.py"), str(meta)], check=False)
print(f"\nGuardado. Hoja firmada por {nombre} y tablas regeneradas.")
