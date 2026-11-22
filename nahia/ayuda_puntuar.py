#!/usr/bin/env python3
"""Genera una vista legible para puntuar a mano (NO puntúa: solo junta la información).

Uso:  python ayuda_puntuar.py resultados/<base>.jsonl
Crea revision/<base>_revision.md con, por pregunta: la pregunta, la respuesta esperada,
la respuesta del modelo, si el retrieval trajo el fragmento correcto y una pista objetiva
(si la respuesta contiene «No aparece en el documento»). La nota final la pone una persona
en la hoja *_puntuacion.csv.
"""
import json
import sys
from pathlib import Path

ABST = "no aparece en el documento"

ruta = Path(sys.argv[1])
filas = [json.loads(l) for l in open(ruta, encoding="utf-8") if l.strip()]
filas = [r for r in filas if r.get("repeticion", 1) == 1]
aciertos = [r["acierto_retrieval"] for r in filas if r.get("acierto_retrieval") is not None]

out = [f"# Revisión: {filas[0]['modelo']} · {filas[0]['escenario']}\n",
       f"Retrieval: el fragmento correcto estaba en el top-k en {sum(aciertos)} de {len(aciertos)} preguntas con respuesta.\n",
       "Pistas automáticas (no son la nota): abstención = la respuesta contiene «No aparece en el documento».\n"]
for r in filas:
    abst = ABST in r["respuesta"].lower()
    retr = {True: "sí", False: "NO (el LLM no pudo acertar por culpa del buscador)", None: "n/a (sin respuesta)"}[r.get("acierto_retrieval")]
    out.append(f"\n## {r['pregunta_id']} · {r['tipo']}\n**Pregunta:** {r['pregunta']}\n\n"
               f"**Esperada:** {r['respuesta_esperada']}\n\n**Respuesta del modelo:** {r['respuesta']}\n\n"
               f"- Fragmento correcto en el top-k: {retr}\n- Se abstiene (pista): {'sí' if abst else 'no'}\n"
               f"- Cita artículo/sección (pista): {'sí' if ('rtículo' in r['respuesta'] or 'ección' in r['respuesta'] or abst) else 'no'}\n")
carpeta = Path(__file__).resolve().parent / "revision"
carpeta.mkdir(exist_ok=True)
destino = carpeta / f"{ruta.stem}_revision.md"
destino.write_text("".join(out), encoding="utf-8")
print("Creado", destino)
