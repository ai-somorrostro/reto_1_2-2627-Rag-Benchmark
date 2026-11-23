import os
import re


MAX_CARACTERES = 1500


def nivel_cabecera(linea: str) -> int:
    """
    Detecta la jerarquía jurídica del BOE.

    TÍTULO     -> nivel 1
    CAPÍTULO   -> nivel 2
    Sección    -> nivel 3
    Artículo   -> nivel 4
    """

    linea = linea.strip()

    if re.match(r"^Artículo\s+\d+\s*\.", linea, re.IGNORECASE):
        return 4

    if re.match(r"^Sección\s+\d+", linea, re.IGNORECASE):
        return 3

    if re.match(r"^CAPÍTULO\s+[IVXLCDM]+", linea, re.IGNORECASE):
        return 2

    if re.match(r"^TÍTULO\s+[IVXLCDM]+", linea, re.IGNORECASE):
        return 1

    return 0


def limpiar_titulo(linea: str) -> str:
    return linea.lstrip("#").split("{")[0].strip()


def extraer_parrafos(texto: str) -> list:
    parrafos = []
    actual = []

    for linea in texto.splitlines():
        if not linea.strip():
            if actual:
                parrafos.append("\n".join(actual).strip())
                actual = []
        else:
            actual.append(linea)

    if actual:
        parrafos.append("\n".join(actual).strip())

    return [p for p in parrafos if p]


def cortar_por_lineas(parrafo: str, max_chars: int) -> list:
    partes = []
    actual = []
    tam = 0

    for linea in parrafo.splitlines():
        longitud = len(linea) + 1

        if actual and tam + longitud > max_chars:
            partes.append("\n".join(actual))
            actual = []
            tam = 0

        actual.append(linea)
        tam += longitud

    if actual:
        partes.append("\n".join(actual))

    return partes


def dividir_texto(texto: str, max_chars: int) -> list:
    partes = []
    actual = []
    tam = 0

    for parrafo in extraer_parrafos(texto):

        if len(parrafo) <= max_chars:
            bloques = [parrafo]
        else:
            bloques = cortar_por_lineas(parrafo, max_chars)

        for bloque in bloques:
            longitud = len(bloque) + 2

            if actual and tam + longitud > max_chars:
                partes.append("\n\n".join(actual))
                actual = []
                tam = 0

            actual.append(bloque)
            tam += longitud

    if actual:
        partes.append("\n\n".join(actual))

    return partes


def guardar(documentos: list, pila: list, lineas: list) -> None:
    texto = "\n".join(lineas).strip()

    if not texto or not pila:
        return

    titulos = [titulo for _, titulo in pila]
    ruta = " > ".join(titulos)

    partes = dividir_texto(texto, MAX_CARACTERES)
    total = len(partes)

    articulo = ""

    for _, titulo in reversed(pila):
        if re.match(r"^Artículo\s+\d+\s*\.", titulo, re.IGNORECASE):
            articulo = titulo
            break

    for i, parte in enumerate(partes, 1):

        sufijo = f" (parte {i}/{total})" if total > 1 else ""

        documentos.append({
            "seccion": ruta,
            "articulo": articulo,
            "parte": f"{i}/{total}" if total > 1 else "",
            "texto": parte,
            "texto_completo": f"[{ruta}{sufijo}]\n{parte}",
        })


def cargar_documentos(filepath: str) -> list:
    with open(filepath, encoding="utf-8") as f:
        lineas = f.read().splitlines()

    # Eliminar frontmatter YAML si existe
    if lineas and lineas[0].strip() == "---":
        try:
            fin_frontmatter = lineas.index("---", 1)
            lineas = lineas[fin_frontmatter + 1:]
        except ValueError:
            pass

    documentos = []
    pila = []
    bloque = []

    for linea in lineas:

        nivel = nivel_cabecera(linea)

        if nivel == 0:
            bloque.append(linea)
            continue

        # Guardar el contenido anterior antes de cambiar de sección
        guardar(documentos, pila, bloque)
        bloque = []

        titulo = limpiar_titulo(linea)

        # Quitar de la pila los niveles iguales o superiores
        while pila and pila[-1][0] >= nivel:
            pila.pop()

        pila.append((nivel, titulo))

    # Guardar el último bloque
    guardar(documentos, pila, bloque)

    return documentos


if __name__ == "__main__":

    ruta = os.path.join(
        os.path.dirname(__file__),
        "..",
        "docs",
        "limpio",
        "BOE.md"
    )

    documentos = cargar_documentos(ruta)

    print(f"{len(documentos)} fragmentos")

    for doc in documentos:
        print(
            f"- {doc['seccion']}"
            f"{' ' + doc['parte'] if doc['parte'] else ''}"
            f" ({len(doc['texto'])} caracteres)"
        )