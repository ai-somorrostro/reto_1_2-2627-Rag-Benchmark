from pathlib import Path
import json
import re

RAIZ = Path(__file__).resolve().parent.parent
CARPETA_CHUNKS = RAIZ / "data" / "chunks"
CARPETA_CHUNKS.mkdir(parents=True, exist_ok=True)

# ---------------- BOE: un chunk por artículo o disposición ----------------
texto = (RAIZ / "data" / "interim" / "boe_limpio.md").read_text(encoding="utf-8")

patron_articulo = re.compile(
    r"^(#+\s*)?(Artículo \d+( (bis|ter|quater|quinquies|sexies|septies|octies))?\.|Disposición (adicional|transitoria|derogatoria|final)\b)"
)
patron_titulo = re.compile(r"^(#+\s*)?(TÍTULO|CAPÍTULO)\b")
patron_seccion = re.compile(r"^(#+\s*)?(Sección|SECCIÓN)\b")

chunks_boe = []
actual = None
estructura = ""
esperando_nombre = False

for linea in texto.split("\n"):
    limpia = linea.strip("# ").strip()

    if esperando_nombre and limpia != "" and not patron_articulo.match(linea):
        estructura = estructura + " - " + limpia
        esperando_nombre = False
        continue

    if patron_titulo.match(linea):
        estructura = limpia
        esperando_nombre = True
        continue

    if patron_seccion.match(linea):
        estructura = limpia
        continue

    if patron_articulo.match(linea):
        if actual is not None:
            chunks_boe.append(actual)
        actual = {
            "id": "boe_" + str(len(chunks_boe) + 1),
            "titulo": limpia,
            "estructura": estructura,
            "texto": limpia,
        }
        continue

    if actual is not None:
        actual["texto"] = actual["texto"] + "\n" + linea

if actual is not None:
    chunks_boe.append(actual)

# ---------------- Debian: un chunk por sección ----------------
NIVEL_MAXIMO = 2   # 1 = solo "# ", 2 = hasta "## ", 3 = hasta "### "
LONGITUD_MINIMA = 80

texto = (RAIZ / "data" / "interim" / "debian.md").read_text(encoding="utf-8")
patron_encabezado = re.compile(r"^(#{1,6}) (.+)$")

chunks_debian = []
titulo_actual = ""
lineas_actual = []
dentro_codigo = False
descartados = 0


def guardar_chunk():
    global descartados
    contenido = "\n".join(lineas_actual).strip()
    if len(contenido) < LONGITUD_MINIMA:
        if contenido != "":
            descartados = descartados + 1
        return
    chunks_debian.append({
        "id": "debian_" + str(len(chunks_debian) + 1),
        "titulo": titulo_actual,
        "texto": contenido,
    })


for linea in texto.split("\n"):
    if linea.strip().startswith("```"):
        dentro_codigo = not dentro_codigo

    encontrado = patron_encabezado.match(linea)
    if encontrado and not dentro_codigo and len(encontrado.group(1)) <= NIVEL_MAXIMO:
        guardar_chunk()
        titulo_actual = encontrado.group(2)
        lineas_actual = [linea]
    else:
        lineas_actual.append(linea)

guardar_chunk()

# ---------------- Guardar y medir ----------------
(CARPETA_CHUNKS / "boe_chunks.json").write_text(
    json.dumps(chunks_boe, ensure_ascii=False, indent=2), encoding="utf-8")
(CARPETA_CHUNKS / "debian_chunks.json").write_text(
    json.dumps(chunks_debian, ensure_ascii=False, indent=2), encoding="utf-8")

for nombre, chunks in [("BOE", chunks_boe), ("Debian", chunks_debian)]:
    longitudes = []
    for chunk in chunks:
        longitudes.append(len(chunk["texto"]))
    print(nombre, "chunks:", len(chunks),
          "min:", min(longitudes), "max:", max(longitudes),
          "media:", sum(longitudes) // len(longitudes))

print("Debian: chunks descartados por ser casi vacíos:", descartados)