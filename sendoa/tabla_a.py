#!/usr/bin/env python3
"""Genera la Tabla A (embeddings) a partir de los JSON de eval_retrieval.py.

Por cada pareja (escenario, modelo) elige el ultimo resultado OFICIAL
(coste.turno_exclusivo = true). Si no hay, usa el ultimo disponible y lo marca
NO OFICIAL. Comprueba que las filas de un escenario comparten chunks, golden,
criterio de combinadas y backend, y escribe Markdown + CSV.

Uso:
    python sendoa/tabla_a.py
    python sendoa/tabla_a.py --resultados sendoa/resultados mikel/resultados
    python sendoa/tabla_a.py --resultados /tmp/prueba --salida /tmp/tablas
"""
import argparse
import csv
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ESCENARIOS = ("boe", "debian")

COLS_MD = ["Modelo", "Estado", "Parametros", "Dimension", "Recall@1",
           "Recall@3", "Recall@5", "MRR", "Indexado (s)", "Indice (MB)",
           "VRAM (GB)", "Fichero origen"]

COLS_CSV = ["escenario", "modelo", "estado", "parametros", "dimension",
            "recall@1", "recall@3", "recall@5", "mrr", "indexado_s",
            "indice_mb", "vram_pico_nvidia_smi_gb", "vram_pico_torch_gb",
            "fecha_hora", "chunks_sha256", "golden_sha256",
            "criterio_combinadas", "chunks_truncados_por_limite",
            "n_avisos", "fichero_origen"]


def cargar(ruta):
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def fecha_resultado(d, ruta):
    valor = (d.get("meta") or {}).get("fecha_hora")
    if valor:
        try:
            return datetime.fromisoformat(valor)
        except ValueError:
            pass
    return datetime.fromtimestamp(ruta.stat().st_mtime)


def estado(d):
    if (d.get("meta") or {}).get("backend") == "dummy":
        return "PRUEBA (dummy)"
    if (d.get("coste") or {}).get("turno_exclusivo") is True:
        return "OFICIAL"
    return "NO OFICIAL"


def descubrir(rutas):
    vistos = set()
    for entrada in rutas:
        p = Path(entrada)
        if not p.is_absolute():
            p = RAIZ / p
        if not p.exists():
            print(f"AVISO: no existe {p}", file=sys.stderr)
            continue
        candidatos = [p] if p.is_file() else sorted(p.rglob("*.json"))
        for ruta in candidatos:
            if ruta.suffix != ".json":
                continue
            try:
                d = cargar(ruta)
            except (OSError, json.JSONDecodeError) as e:
                print(f"AVISO: {ruta} no es JSON valido ({e})", file=sys.stderr)
                continue
            if not isinstance(d, dict) or not all(
                    k in d for k in ("meta", "metricas", "coste")):
                continue
            clave = ruta.resolve()
            if clave in vistos:
                continue
            vistos.add(clave)
            yield ruta, d


def elegir(rutas):
    grupos = defaultdict(list)
    for ruta, d in descubrir(rutas):
        meta = d.get("meta") or {}
        modelo, escenario = meta.get("modelo"), meta.get("escenario")
        if not modelo or escenario not in ESCENARIOS:
            print(f"AVISO: {ruta} sin modelo/escenario reconocible; se ignora",
                  file=sys.stderr)
            continue
        grupos[(escenario, modelo)].append((fecha_resultado(d, ruta), ruta, d))

    elegidos = []
    for (escenario, modelo), items in grupos.items():
        oficiales = [x for x in items if estado(x[2]) == "OFICIAL"]
        pool = oficiales if oficiales else items
        fecha, ruta, d = max(pool, key=lambda x: (x[0], x[1].name))
        elegidos.append((escenario, modelo, fecha, ruta, d))
    return elegidos


def fila(escenario, modelo, fecha, ruta, d):
    meta = d.get("meta") or {}
    cfg = d.get("config") or {}
    met = d.get("metricas") or {}
    coste = d.get("coste") or {}
    try:
        origen = str(ruta.relative_to(RAIZ))
    except ValueError:
        origen = str(ruta)
    est = estado(d)
    es_prueba = est == "PRUEBA (dummy)"
    return {
        "escenario": escenario,
        "modelo": modelo,
        "estado": est,
        "parametros": meta.get("parametros"),
        "dimension": meta.get("dimension"),
        "recall@1": met.get("recall@1"),
        "recall@3": met.get("recall@3"),
        "recall@5": met.get("recall@5"),
        "mrr": met.get("mrr"),
        "indexado_s": coste.get("indexado_s"),
        "indice_mb": coste.get("indice_mb"),
        "vram_pico_nvidia_smi_gb": (None if es_prueba
                                    else coste.get("vram_pico_nvidia_smi_gb")),
        "vram_pico_torch_gb": (None if es_prueba
                               else coste.get("vram_pico_torch_gb")),
        "fecha_hora": meta.get("fecha_hora"),
        "chunks_sha256": meta.get("chunks_sha256"),
        "golden_sha256": meta.get("golden_sha256"),
        "criterio_combinadas": cfg.get("criterio_combinadas"),
        "chunks_truncados_por_limite": coste.get("chunks_truncados_por_limite"),
        "n_avisos": len(d.get("avisos") or []),
        "avisos": d.get("avisos") or [],
        "backend": meta.get("backend"),
        "fichero_origen": origen,
    }


def _num(valor, por_defecto):
    return por_defecto if valor is None else valor


def orden(f):
    return (
        -_num(f["recall@5"], -1.0),
        -_num(f["mrr"], -1.0),
        _num(f["vram_pico_nvidia_smi_gb"], float("inf")),
        _num(f["indexado_s"], float("inf")),
    )


def comprobar_equidad(filas):
    avisos = []
    for campo in ("chunks_sha256", "golden_sha256", "criterio_combinadas", "backend"):
        valores = {str(f[campo]) for f in filas}
        if len(valores) > 1:
            avisos.append(
                f"El campo {campo} no coincide entre filas: {sorted(valores)}. "
                "La comparacion no seria justa."
            )
    return avisos


def fmt(valor, decimales=3):
    if valor is None:
        return "n/d"
    if isinstance(valor, float):
        return f"{valor:.{decimales}f}"
    return str(valor)


def fila_md(f):
    return "| " + " | ".join([
        str(f["modelo"]), f["estado"], fmt(f["parametros"], 0),
        fmt(f["dimension"], 0), fmt(f["recall@1"]), fmt(f["recall@3"]),
        fmt(f["recall@5"]), fmt(f["mrr"]), fmt(f["indexado_s"], 2),
        fmt(f["indice_mb"], 2), fmt(f["vram_pico_nvidia_smi_gb"]),
        f["fichero_origen"],
    ]) + " |"


def escribir_escenario(escenario, filas, salida, avisos_equidad, generado):
    filas = sorted(filas, key=orden)
    lineas = [f"# Tabla A - Escenario {escenario.upper()}", "",
              f"Generado: {generado}", f"Filas: {len(filas)}", ""]
    if any(f["estado"] != "OFICIAL" for f in filas):
        lineas += ["> AVISO: hay filas NO OFICIALES o de PRUEBA; "
                   "no usar para decidir.", ""]
    for a in avisos_equidad:
        lineas += [f"> AVISO: {a}", ""]
    for f in filas:
        if f["chunks_truncados_por_limite"]:
            lineas += [f"> AVISO: {f['modelo']} tiene "
                       f"{f['chunks_truncados_por_limite']} chunks truncados.", ""]
        if f["n_avisos"]:
            lineas += [f"> AVISO: {f['modelo']} tiene {f['n_avisos']} avisos "
                       "en el JSON.", ""]
    lineas.append("| " + " | ".join(COLS_MD) + " |")
    lineas.append("| " + " | ".join("---" for _ in COLS_MD) + " |")
    lineas += [fila_md(f) for f in filas]
    lineas.append("")
    (salida / f"tabla_a_{escenario}.md").write_text(
        "\n".join(lineas), encoding="utf-8")

    with open(salida / f"tabla_a_{escenario}.csv", "w", newline="",
              encoding="utf-8") as fh:
        escritor = csv.DictWriter(fh, fieldnames=COLS_CSV, extrasaction="ignore")
        escritor.writeheader()
        for f in filas:
            escritor.writerow({k: f.get(k) for k in COLS_CSV})


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--resultados", nargs="+",
                    default=["sendoa/resultados", "sendoa/resultados_oficiales",
                             "julen/resultados", "mikel/resultados"],
                    help="Carpetas o ficheros JSON de resultados")
    ap.add_argument("--salida", default="sendoa/tablas",
                    help="Carpeta donde escribir los .md y .csv")
    ap.add_argument("--escenarios", nargs="+", choices=ESCENARIOS,
                    default=list(ESCENARIOS))
    ap.add_argument("--solo-oficiales", action="store_true",
                    help="Excluir filas NO OFICIALES o de PRUEBA")
    args = ap.parse_args()

    salida = Path(args.salida)
    if not salida.is_absolute():
        salida = RAIZ / salida
    salida.mkdir(parents=True, exist_ok=True)

    elegidos = elegir(args.resultados)
    if args.solo_oficiales:
        elegidos = [x for x in elegidos if estado(x[4]) == "OFICIAL"]

    por_escenario = defaultdict(list)
    for escenario, modelo, fecha, ruta, d in elegidos:
        por_escenario[escenario].append(fila(escenario, modelo, fecha, ruta, d))

    generado = datetime.now().isoformat(timespec="seconds")
    for escenario in args.escenarios:
        filas = por_escenario.get(escenario, [])
        if not filas:
            print(f"AVISO: no hay resultados para {escenario}", file=sys.stderr)
            continue
        avisos_equidad = comprobar_equidad(filas)
        escribir_escenario(escenario, filas, salida, avisos_equidad, generado)
        print(f"{escenario}: {len(filas)} filas -> "
              f"{salida}/tabla_a_{escenario}.md/.csv")
        for a in avisos_equidad:
            print(f"  AVISO: {a}", file=sys.stderr)


if __name__ == "__main__":
    main()
