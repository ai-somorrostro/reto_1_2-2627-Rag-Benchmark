#!/usr/bin/env python3
"""
Genera las Tablas B (calidad) y C (coste) de la Fase 3 a partir de:
  - results/llms/data/<modelo>_<escenario>.json   (salida de benchmark_llms_vllm.py)
  - results/llms/puntuacion_<escenario>.csv       (vuestra puntuación a mano)

Paso 1:  python scripts/generar_tablas_llm.py --plantilla
         Crea (o completa sin borrar notas) los CSV de puntuación. Se abren con Excel/LibreOffice (separador «;»).
         Rellenad a mano, para cada fila:
           correccion      0, 1 o 2  (2 correcta y completa, 1 incompleta, 0 incorrecta;
                                      en sin_respuesta, «No aparece en el documento» = 2)
           fiel            1 si todo lo que afirma está en los fragmentos, 0 si inventa algo
           abstiene        viene precalculado (1 si dice «No aparece en el documento»); corregidlo si hace falta
           formato_idioma  1 si responde en español y cita el artículo/sección, 0 si no
                           (cita_auto es solo una pista)
Paso 2:  python scripts/generar_tablas_llm.py
         Escribe results/llms/tablas_b_c.md
"""

import argparse
import csv
import glob
import json
import os
import statistics

DIR = "results/llms"
ESCENARIOS = {"boe": "Estatuto de los Trabajadores (BOE)", "debian": "Manual del Administrador de Debian"}
ORDEN_MODELOS = ["lfm3-1.7b", "llama3.2-3b", "nemotron-bolt-e4b", "qwen3.5-9b"]

COLUMNAS = ["modelo", "modo", "id", "tipo", "pregunta", "respuesta_esperada", "respuesta_modelo",
            "gold_en_contexto", "cita_auto", "abstiene", "correccion", "fiel", "formato_idioma", "notas"]
MANUALES = ["abstiene", "correccion", "fiel", "formato_idioma", "notas"]


def cargar_resultados(esc):
    res = {}
    for p in glob.glob(f"{DIR}/data/*_{esc}.json"):
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        res[d["meta"]["modelo"]] = d
    orden = {m: i for i, m in enumerate(ORDEN_MODELOS)}
    return dict(sorted(res.items(), key=lambda kv: orden.get(kv[0], 99)))


def ruta_csv(esc):
    return f"{DIR}/puntuacion_{esc}.csv"


def leer_csv(esc):
    if not os.path.exists(ruta_csv(esc)):
        return []
    with open(ruta_csv(esc), encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def plantilla(esc):
    resultados = cargar_resultados(esc)
    if not resultados:
        print(f"[{esc}] sin resultados en {DIR}/data/, nada que hacer")
        return
    previas = {(r["modelo"], r["modo"], r["id"]): r for r in leer_csv(esc)}
    filas = []
    for m, d in resultados.items():
        for r in d["respuestas"]:
            clave = (m, r["modo"], r["id"])
            fila = {
                "modelo": m, "modo": r["modo"], "id": r["id"], "tipo": r["tipo"], "pregunta": r["pregunta"],
                "respuesta_esperada": r["respuesta_esperada"], "respuesta_modelo": r["respuesta"],
                "gold_en_contexto": "" if r["gold_en_contexto"] is None else int(r["gold_en_contexto"]),
                "cita_auto": int(r["cita_auto"]), "abstiene": int(r["abstiene_auto"]),
                "correccion": "", "fiel": "", "formato_idioma": "", "notas": "",
            }
            if clave in previas:  # conservar lo ya puntuado
                for c in MANUALES:
                    if previas[clave].get(c, "") != "":
                        fila[c] = previas[clave][c]
            filas.append(fila)
    with open(ruta_csv(esc), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNAS, delimiter=";")
        w.writeheader()
        w.writerows(filas)
    pendientes = sum(1 for f in filas if f["correccion"] == "")
    print(f"[{esc}] {ruta_csv(esc)}: {len(filas)} filas, {pendientes} sin puntuar")


def num(x):
    try:
        return float(str(x).replace(",", "."))
    except ValueError:
        return None


def fmt(x, dec=2, pct=False):
    if x is None:
        return "—"
    s = f"{x * 100:.0f} %" if pct else f"{x:.{dec}f}"
    return s.replace(".", ",")


def media(vals):
    vals = [v for v in vals if v is not None]
    return (sum(vals) / len(vals), len(vals)) if vals else (None, 0)


def tabla_b(esc, resultados, filas):
    out = ["### Tabla B. LLMs: calidad (con retrieval)\n",
           "| Modelo | Tamaño | Cuantización | Corrección media (0–2) | Respuestas fieles (%) | "
           "Abstención correcta (de 3) | Falsas abstenciones | Formato e idioma (%) |",
           "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for m, d in resultados.items():
        meta = d["meta"]
        fr = [f for f in filas if f["modelo"] == m and f["modo"] == "retrieval"]
        n = len(fr)
        corr, nc = media(num(f["correccion"]) for f in fr)
        fiel, nf = media(num(f["fiel"]) for f in fr)
        form, nfo = media(num(f["formato_idioma"]) for f in fr)
        sin = [f for f in fr if f["tipo"] == "sin_respuesta"]
        con = [f for f in fr if f["tipo"] != "sin_respuesta"]
        abst_ok = sum(1 for f in sin if num(f["abstiene"]) == 1)
        falsas = sum(1 for f in con if num(f["abstiene"]) == 1)

        def marca(k):
            return "" if k == n else f" ({k}/{n} puntuadas)"
        out.append(f"| `{m}` | {meta['tamano']} | {meta['cuantizacion']} | {fmt(corr)}{marca(nc)} | "
                   f"{fmt(fiel, pct=True)}{marca(nf)} | {abst_ok} de {len(sin)} | {falsas} de {len(con)} | "
                   f"{fmt(form, pct=True)}{marca(nfo)} |")
    return out


def tabla_oraculo(filas, resultados):
    con_oraculo = [m for m in resultados if any(f["modelo"] == m and f["modo"] == "oraculo" for f in filas)]
    if not con_oraculo:
        return []
    out = ["\n### Extra. Retrieval frente a oráculo (solo preguntas con respuesta)\n",
           "| Modelo | Corrección con retrieval | Corrección con oráculo | Fallo del retrieval | Fallo por ruido |",
           "| --- | --- | --- | --- | --- |"]
    for m in con_oraculo:
        ret = {f["id"]: f for f in filas if f["modelo"] == m and f["modo"] == "retrieval" and f["tipo"] != "sin_respuesta"}
        ora = {f["id"]: f for f in filas if f["modelo"] == m and f["modo"] == "oraculo"}
        c_ret, _ = media(num(ret[i]["correccion"]) for i in ora if i in ret)
        c_ora, _ = media(num(f["correccion"]) for f in ora.values())
        mejora = [i for i in ora if i in ret and num(ora[i]["correccion"]) == 2
                  and num(ret[i]["correccion"]) is not None and num(ret[i]["correccion"]) < 2]
        f_ret = [i for i in mejora if str(ret[i].get("gold_en_contexto")) != "1"]
        f_ruido = [i for i in mejora if str(ret[i].get("gold_en_contexto")) == "1"]
        out.append(f"| `{m}` | {fmt(c_ret)} | {fmt(c_ora)} | {', '.join(f_ret) or 'ninguno'} | {', '.join(f_ruido) or 'ninguno'} |")
    out.append("\n> Con el chunk correcto acierta (2) y con el retrieval no. **Fallo del retrieval**: el chunk correcto "
               "no llegó al top-k. **Fallo por ruido**: sí llegó, pero los demás fragmentos despistaron al LLM "
               "(no es culpa del embedding).")
    return out


def tabla_c(resultados):
    out = ["\n### Tabla C. LLMs: coste (mediana de 3 rondas tras descartar la primera, 5 preguntas)\n",
           "| Modelo | Stack | TTFT (s) | Tokens/s | Latencia total (s) | VRAM pico (GB) |",
           "| --- | --- | --- | --- | --- | --- |"]
    for m, d in resultados.items():
        c, meta = d["coste"]["mediana"], d["meta"]
        if meta.get("stack_version"):
            stack = f"{meta['stack']} {meta['stack_version']}"
        else:
            v = meta.get("ollama_version") or ""
            stack = "Ollama " + ("" if v.startswith("[") else v.split()[-1])
        out.append(f"| `{m}` | {stack} | "
                   f"{fmt(c['ttft_s'])} | {fmt(c['tokens_por_s'], 1)} | {fmt(c['latencia_total_s'])} | "
                   f"{fmt(meta['vram_pico_gb'])} |")
    return out


def notas(resultados):
    out = []
    for m, d in resultados.items():
        meta = d["meta"]
        problemas = []
        if "gpu_memory_utilization" in (meta.get("memoria") or ""):
            problemas.append("VRAM medida con gpu_memory_utilization: refleja la reserva de vLLM, no el modelo")
        if "CPU" in (meta.get("ollama_ps") or ""):
            problemas.append("`ollama ps` muestra parte del modelo en CPU")
        if any(r["razonamiento_detectado"] for r in d["respuestas"]):
            problemas.append("se detectó razonamiento (think) en alguna respuesta")
        if any(r["posible_truncado"] for r in d["respuestas"]):
            problemas.append("algún prompt roza max_model_len")
        cortadas = sum(1 for r in d["respuestas"] if r["cortado_por_num_predict"])
        if cortadas:
            problemas.append(f"{cortadas} respuesta{'s' if cortadas != 1 else ''} cortada{'s' if cortadas != 1 else ''} por max_tokens")
        if problemas:
            out.append(f"- **{m}:** " + "; ".join(problemas))
    return (["\n**Avisos**\n"] + out) if out else []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plantilla", action="store_true", help="crear/completar los CSV de puntuación")
    a = ap.parse_args()

    if a.plantilla:
        for esc in ESCENARIOS:
            plantilla(esc)
        return

    md = ["# Fase 3. Resultados del benchmark de LLMs\n"]
    for esc, nombre in ESCENARIOS.items():
        resultados = cargar_resultados(esc)
        if not resultados:
            continue
        meta0 = next(iter(resultados.values()))["meta"]
        o = meta0["opciones"]
        md.append(f"## Escenario: {nombre}\n")
        md.append(f"Stack: {meta0.get('stack', 'Ollama')} · cuantización {meta0['cuantizacion']} · embedding: `{meta0['embedding']}` · top-k = {meta0['top_k']} · temperatura {o['temperature']} · "
                  f"max_tokens {o['num_predict']} · max_model_len {o['num_ctx']} · mismo prompt para todos\n")
        filas = leer_csv(esc)
        md += tabla_b(esc, resultados, filas)
        md += tabla_oraculo(filas, resultados)
        md += tabla_c(resultados)
        md += notas(resultados)
        md.append("\n---\n")
    os.makedirs(DIR, exist_ok=True)
    with open(f"{DIR}/tablas_b_c.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print(f"[+] {DIR}/tablas_b_c.md")


if __name__ == "__main__":
    main()