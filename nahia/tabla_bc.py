#!/usr/bin/env python3
"""Calcula las filas de la Tabla B (calidad) y la Tabla C (coste) de UN modelo y escenario.

Uso:
    python tabla_bc.py resultados/<base>_meta.json

Lee, junto al _meta.json: el .jsonl (coste), la hoja _puntuacion.csv ya rellenada a
mano (calidad) y el _gpu.csv. Escribe tablas/<base>_tablas.md con las dos filas y
de qué fichero sale cada cifra (trazabilidad).
"""
import csv
import json
import statistics
import sys
from pathlib import Path

SI = {"si", "sí", "s", "yes", "y", "1", "true"}
NO = {"no", "n", "0", "false"}


def es_si(v):
    return v.strip().lower() in SI


def es_no(v):
    return v.strip().lower() in NO


def main(ruta_meta):
    ruta_meta = Path(ruta_meta)
    carpeta = ruta_meta.parent
    meta = json.load(open(ruta_meta, encoding="utf-8"))
    base = ruta_meta.name.removesuffix("_meta.json")
    f_jsonl = carpeta / meta["fichero_respuestas"]
    f_punt = carpeta / f"{f_jsonl.stem}_puntuacion.csv"
    f_gpu = carpeta / meta["fichero_gpu"]

    filas = [json.loads(l) for l in open(f_jsonl, encoding="utf-8") if l.strip()]

    # ---- Tabla C: mediana de las 3 repeticiones por pregunta, y mediana entre preguntas
    por_pregunta = {}
    for r in filas:
        if r["para_coste"] and not r.get("descartada"):
            por_pregunta.setdefault(r["pregunta_id"], []).append(r)

    def mediana(campo):
        meds = []
        for reps in por_pregunta.values():
            vals = [r[campo] for r in reps if r[campo] is not None]
            if vals:
                meds.append(statistics.median(vals))
        return round(statistics.median(meds), 2) if meds else None

    ttft, tps, lat = mediana("ttft_s"), mediana("tokens_por_s"), mediana("latencia_total_s")
    vram = meta["vram_pico_nvidia_smi_gb"]

    # ---- Tabla B: sale de la hoja puntuada a mano
    with open(f_punt, encoding="utf-8-sig", newline="") as f:
        punt = list(csv.DictReader(f))
    sin_puntuar = [p["pregunta_id"] for p in punt if not p["correccion_0_2"].strip()]
    if sin_puntuar:
        print(f"AVISO: faltan por puntuar {len(sin_puntuar)} respuestas: {sin_puntuar}")
        sys.exit("Rellena la hoja de puntuación antes de calcular la Tabla B.")

    n = len(punt)
    correccion = round(sum(float(p["correccion_0_2"]) for p in punt) / n, 2)
    fieles = round(100 * sum(es_si(p["fiel_si_no"]) for p in punt) / n)
    formato = round(100 * sum(es_si(p["formato_idioma_si_no"]) for p in punt) / n)
    sin_resp = [p for p in punt if p["tipo"] == "sin_respuesta"]
    con_resp = [p for p in punt if p["tipo"] != "sin_respuesta"]
    abst_ok = sum(es_si(p["se_abstiene_si_no_na"]) for p in sin_resp)
    falsas = sum(es_si(p["se_abstiene_si_no_na"]) for p in con_resp)
    punt_por = sorted({p["puntuado_por"] for p in punt if p["puntuado_por"].strip()})

    tam = f"{meta['parametros_miles_de_millones']} B"
    md = f"""# {meta['modelo']} · {meta['escenario']} · {meta['fecha_hora']}

## Tabla B (calidad)
| Modelo | Tamaño | Cuantización | Corrección media (0–2) | Respuestas fieles (%) | Abstención correcta (de {len(sin_resp)}) | Falsas abstenciones | Formato e idioma (%) |
|---|---|---|---|---|---|---|---|
| {meta['modelo']} | {tam} | {meta['cuantizacion']} | {correccion} | {fieles} | {abst_ok} | {falsas} (de {len(con_resp)}) | {formato} |

## Tabla C (coste)
| Modelo | Stack | TTFT (s) | Tokens/s | Latencia total (s) | VRAM pico (GB) |
|---|---|---|---|---|---|
| {meta['modelo']} | {meta['stack']} | {ttft} | {tps} | {lat} | {vram} |

## Trazabilidad
- Respuestas y tiempos brutos: `{f_jsonl.name}`
- Puntuación a mano ({n} respuestas, puntuado por: {', '.join(punt_por) or '¿?'}): `{f_punt.name}`
- Registro de GPU (pico {vram} GB, nvidia-smi de la instancia): `{f_gpu.name}`
- Configuración: `{ruta_meta.name}` (top-k {meta['top_k']}, fragmentos: {meta['fragmentos']}, embedding: {meta['embedding']}, prompt sha256 {meta['prompt_sha256']}, temperatura {meta['temperatura']}, máx. tokens {meta['max_tokens_salida']})
- Coste: mediana de {meta['repeticiones_coste']} repeticiones por pregunta (tras calentamiento descartado), y mediana entre las preguntas {', '.join(meta['preguntas_coste'])}
"""
    salida = carpeta.parent / "tablas"
    salida.mkdir(exist_ok=True)
    destino = salida / f"{base}_tablas.md"
    destino.write_text(md, encoding="utf-8")
    print(md)
    print("Guardado en", destino)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
