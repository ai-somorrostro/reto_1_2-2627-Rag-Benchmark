from pathlib import Path
from docling.document_converter import DocumentConverter
from bs4 import BeautifulSoup
import zipfile
import xml.etree.ElementTree as ET

RAIZ = Path(__file__).resolve().parent.parent
EPUB = RAIZ / "data" / "raw" / "debian-handbook.epub"
CARPETA = RAIZ / "data" / "interim" / "debian_epub"
HTML_LIMPIO = RAIZ / "data" / "interim" / "debian_html"
SALIDA = RAIZ / "data" / "interim" / "debian.md"

HTML_LIMPIO.mkdir(parents=True, exist_ok=True)

with zipfile.ZipFile(EPUB) as epub:
    epub.extractall(CARPETA)

opf = CARPETA / "OEBPS" / "content.opf"
raiz = ET.parse(opf).getroot()
ns = {"o": "http://www.idpf.org/2007/opf"}

# 1. Diccionario: id -> nombre de fichero
manifest = {}
for item in raiz.findall("o:manifest/o:item", ns):
    manifest[item.get("id")] = item.get("href")

# 2. Ficheros en el orden real del libro
excluir = ["cover.html", "bk01-toc.html", "index.html"]

ficheros = []
for itemref in raiz.findall("o:spine/o:itemref", ns):
    href = manifest[itemref.get("idref")]
    nombre = Path(href).name
    if not href.endswith(".html"):
        continue
    if nombre in excluir:
        continue
    ficheros.append(opf.parent / href)

print("Ficheros en orden:", len(ficheros))


# 3. Convertir los <div class="screen"> y <div class="programlisting">
#    en <pre>, para que docling los reconozca como bloques de código
def preparar_html(ruta_origen, ruta_destino):
    html = ruta_origen.read_text(encoding="utf-8")
    sopa = BeautifulSoup(html, "html.parser")
    for clase in ["screen", "programlisting"]:
        for bloque in sopa.find_all("div", class_=clase):
            pre = sopa.new_tag("pre")
            pre.string = bloque.get_text()
            bloque.replace_with(pre)
    ruta_destino.write_text(str(sopa), encoding="utf-8")


# 4. Convertir cada fichero a markdown
convertidor = DocumentConverter()
partes = []
contador = 0
for fichero in ficheros:
    destino = HTML_LIMPIO / fichero.name
    preparar_html(fichero, destino)
    resultado = convertidor.convert(str(destino))
    partes.append(resultado.document.export_to_markdown())
    contador = contador + 1
    print(contador, "/", len(ficheros), fichero.name)

SALIDA.write_text("\n\n".join(partes), encoding="utf-8")
print("Ficheros convertidos:", len(partes))