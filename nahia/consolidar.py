#!/usr/bin/env python3
"""Genera las tablas consolidadas por escenario (Tabla B y C) y copia lo final a comun/resultados_finales/.

Uso:  python consolidar.py        (después de puntuar y de ejecutar tabla_bc.py)
Para cada (modelo, escenario) toma la última ejecución con el embedding ganador y la hoja ya puntuada,
y copia sus filas de la tabla individual (nahia/tablas/<base>_tablas.md).
"""
import csv, glob, json, shutil, subprocess, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DEST = AQUI.parent / "comun" / "resultados_finales"
norm = lambda e: (e or "").replace("../", "")
gan = json.load(open(AQUI / "ganadores_embedding.json", encoding="utf-8"))


def puntuada(meta):
    jsonl = AQUI / "resultados" / meta["fichero_respuestas"]
    hoja = jsonl.with_name(jsonl.stem + "_puntuacion.csv")
    if not hoja.exists():
        return None
    filas = list(csv.DictReader(open(hoja, encoding="utf-8-sig", newline="")))
    return hoja if filas and all(f["correccion_0_2"].strip() for f in filas) else None


finales = {}
for f in sorted(glob.glob(str(AQUI / "resultados" / "*_meta.json"))):
    m = json.load(open(f, encoding="utf-8"))
    if m["cuantizacion"] != "bf16":
        continue  # el plan B (4 bits) se consolida aparte
    if norm(m["embedding"]) != gan[m["escenario"]] or not m["turno_exclusivo"] or not puntuada(m):
        continue
    k = (m["escenario"], m["modelo"])
    if k not in finales or m["fecha_hora"] > finales[k][0]["fecha_hora"]:
        finales[k] = (m, Path(f))

(DEST / "tablas_B_C").mkdir(parents=True, exist_ok=True)
indice = []
for esc, nombre in (("boe", "BOE"), ("debian", "Debian")):
    B, C = [], []
    for (e, modelo), (m, fmeta) in sorted(finales.items()):
        if e != esc:
            continue
        base = fmeta.name.removesuffix("_meta.json")
        tabla = AQUI / "tablas" / f"{base}_tablas.md"
        if not tabla.exists():
            subprocess.run([sys.executable, str(AQUI / "tabla_bc.py"), str(fmeta)], check=True, capture_output=True)
        lineas = [l for l in tabla.read_text(encoding="utf-8").splitlines() if l.startswith(f"| {modelo} |")]
        B.append(lineas[0]); C.append(lineas[1])
        shutil.copy(tabla, DEST / "tablas_B_C" / tabla.name)
        hoja = puntuada(m)
        por = sorted({r["puntuado_por"] for r in csv.DictReader(open(hoja, encoding="utf-8-sig", newline="")) if r["puntuado_por"].strip()})
        indice.append(f"| {modelo} | {esc} | `tablas_B_C/{tabla.name}` | `{m['fichero_respuestas']}` | `{m['fichero_gpu']}` | `{base}_meta.json` | `{hoja.name}` | {', '.join(por)} |")
    cab_b = ("| Modelo | Tamaño | Cuantización | Corrección media (0–2) | Respuestas fieles (%) | Abstención correcta (de 3) | Falsas abstenciones | Formato e idioma (%) |\n|---|---|---|---|---|---|---|---|")
    cab_c = ("| Modelo | Stack | TTFT (s) | Tokens/s | Latencia total (s) | VRAM pico (GB) |\n|---|---|---|---|---|---|")
    (DEST / f"Tabla_B_{nombre}.md").write_text(f"# Tabla B (calidad), escenario {nombre}\n\n{cab_b}\n" + "\n".join(B) + "\n\nGenerada por `nahia/consolidar.py`. Fuente de cada fila: `INDICE_ejecuciones.md`.\n", encoding="utf-8")
    (DEST / f"Tabla_C_{nombre}.md").write_text(f"# Tabla C (coste), escenario {nombre}\n\n{cab_c}\n" + "\n".join(C) + "\n\nGenerada por `nahia/consolidar.py`. Fuente de cada fila: `INDICE_ejecuciones.md`.\n", encoding="utf-8")
(DEST / "INDICE_ejecuciones.md").write_text("# Ejecuciones finales usadas en las tablas B y C\n\nGenerado por `nahia/consolidar.py`. Ficheros brutos en `nahia/resultados/`.\n\n| Modelo | Escenario | Tablas | Respuestas y tiempos | GPU | Ficha | Hoja de puntuación | Puntuado por |\n|---|---|---|---|---|---|---|---|\n" + "\n".join(indice) + "\n", encoding="utf-8")
for fn in ("decision_fase4_20GB.md", "decision_fase4_8GB.md", "ganadores_embedding.json"):
    src = AQUI / ("tablas/" + fn if fn.endswith(".md") else fn)
    if src.exists():
        shutil.copy(src, DEST / fn)
print("OK:", len(finales), "ejecuciones finales")
