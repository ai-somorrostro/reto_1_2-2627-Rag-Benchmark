from pathlib import Path
import json
import re

RAIZ = Path(__file__).resolve().parent.parent
CARPETA = RAIZ / "data" / "chunks"
MAX_CARACTERES = 1800   # unos 450-500 tokens en español


def dividir_en_unidades(texto):
    # Un párrafo o un bloque de código completo es una unidad
    unidades = []
    actual = []
    dentro_codigo = False
    for linea in texto.split("\n"):
        if linea.strip().startswith("```"):
            dentro_codigo = not dentro_codigo
        if linea.strip() == "" and not dentro_codigo:
            if len(actual) > 0:
                unidades.append("\n".join(actual))
                actual = []
        else:
            actual.append(linea)
    if len(actual) > 0:
        unidades.append("\n".join(actual))
    return unidades


def empaquetar(piezas, separador, maximo):
    trozos = []
    actual = ""
    for pieza in piezas:
        while len(pieza) > maximo:
            if actual != "":
                trozos.append(actual)
                actual = ""
            trozos.append(pieza[:maximo])
            pieza = pieza[maximo:]
        if actual == "":
            actual = pieza
        elif len(actual) + len(separador) + len(pieza) <= maximo:
            actual = actual + separador + pieza
        else:
            trozos.append(actual)
            actual = pieza
    if actual != "":
        trozos.append(actual)
    return trozos


def partir_unidad_larga(unidad, maximo):
    if unidad.startswith("```") and unidad.endswith("```"):
        lineas = unidad.split("\n")
        apertura = lineas[0]
        interior = lineas[1:-1]
        trozos = empaquetar(interior, "\n", maximo - 20)
        resultado = []
        for trozo in trozos:
            resultado.append(apertura + "\n" + trozo + "\n```")
        return resultado
    if "\n" in unidad:
        return empaquetar(unidad.split("\n"), "\n", maximo)
    frases = re.split(r"(?<=[.;:])\s+", unidad)
    return empaquetar(frases, " ", maximo)


def trocear(texto, maximo):
    unidades = dividir_en_unidades(texto)
    trozos = []
    actual = ""
    for unidad in unidades:
        if len(unidad) > maximo:
            if actual != "":
                trozos.append(actual)
                actual = ""
            for parte in partir_unidad_larga(unidad, maximo):
                trozos.append(parte)
            continue
        if actual == "":
            actual = unidad
        elif len(actual) + 2 + len(unidad) <= maximo:
            actual = actual + "\n\n" + unidad
        else:
            trozos.append(actual)
            actual = unidad
    if actual != "":
        trozos.append(actual)
    return trozos


def procesar(entrada, salida, corpus):
    chunks = json.loads((CARPETA / entrada).read_text(encoding="utf-8"))
    finales = []
    for chunk in chunks:
        titulo = chunk["titulo"]
        maximo = MAX_CARACTERES - len(titulo) - 30
        if maximo < 500:
            maximo = 500
        trozos = trocear(chunk["texto"], maximo)
        total = len(trozos)
        for numero in range(total):
            texto = trozos[numero]
            if numero > 0:
                texto = titulo + " (parte " + str(numero + 1) + " de " + str(total) + ")\n\n" + texto
            nuevo = {
                "id": chunk["id"] + "_p" + str(numero + 1),
                "corpus": corpus,
                "grupo": chunk["id"],
                "fuente": titulo,
                "parte": numero + 1,
                "partes_total": total,
                "anterior": "",
                "siguiente": "",
                "texto": texto,
            }
            if "estructura" in chunk:
                nuevo["estructura"] = chunk["estructura"]
            finales.append(nuevo)

    # Enlazar cada trozo con el anterior y el siguiente de su mismo grupo
    for i in range(len(finales)):
        if finales[i]["parte"] > 1:
            finales[i]["anterior"] = finales[i - 1]["id"]
        if finales[i]["parte"] < finales[i]["partes_total"]:
            finales[i]["siguiente"] = finales[i + 1]["id"]

    (CARPETA / salida).write_text(
        json.dumps(finales, ensure_ascii=False, indent=2), encoding="utf-8")

    longitudes = []
    pasan = 0
    for chunk in finales:
        longitudes.append(len(chunk["texto"]))
        if len(chunk["texto"]) > MAX_CARACTERES:
            pasan = pasan + 1
    print(entrada, "->", salida)
    print("  chunks originales:", len(chunks), " chunks finales:", len(finales))
    print("  min:", min(longitudes), "max:", max(longitudes),
          "media:", sum(longitudes) // len(longitudes), " pasan del máximo:", pasan)


procesar("boe_chunks.json", "boe_final.json", "boe")
procesar("debian_chunks.json", "debian_final.json", "debian")