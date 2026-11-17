from pathlib import Path
import re
from docling.document_converter import DocumentConverter

RAIZ = Path(__file__).resolve().parent.parent
PDF = RAIZ / "data" / "raw" / "BOE-A-2015-11430-consolidado.pdf"
CRUDO = RAIZ / "data" / "interim" / "boe_docling.md"
LIMPIO = RAIZ / "data" / "interim" / "boe_limpio.md"

patron_ruido = re.compile(r"^(BOLETÍN OFICIAL DEL ESTADO|LEGISLACIÓN CONSOLIDADA|Página \d+|\s)+$")
patron_marcador = re.compile(r"^(\d+|[a-zñ])[.)]$")
patron_letra = re.compile(r"^[a-zñ]\)")
etiquetas_ruido = ["page_header", "page_footer"]

# 1. Convertir con docling
convertidor = DocumentConverter()
resultado = convertidor.convert(str(PDF))
doc = resultado.document

# Markdown crudo, solo para auditar
CRUDO.write_text(doc.export_to_markdown(), encoding="utf-8")

# 2. Recoger los textos con su página y su posición, sin cabeceras ni pies
elementos = []
for item in doc.texts:
    if item.label.value in etiquetas_ruido:
        continue
    texto_item = item.text.strip()
    if texto_item == "":
        continue
    if patron_ruido.match(texto_item):
        continue
    if ". . . ." in texto_item:
        continue
    if len(item.prov) == 0:
        continue

    # Recuperar la numeración de los apartados (1., 2., a), b)...)
    marcador = getattr(item, "marker", "")
    if marcador:
        marcador = marcador.strip()
        if patron_marcador.match(marcador) and not texto_item.startswith(marcador):
            texto_item = marcador + " " + texto_item

    prov = item.prov[0]
    pagina = prov.page_no
    altura = doc.pages[pagina].size.height
    caja = prov.bbox.to_top_left_origin(altura)
    elementos.append((pagina, round(caja.t, 1), round(caja.l, 1), texto_item))

# 3. Ordenar por página y, dentro de cada página, de arriba abajo
elementos.sort()
print("Elementos de texto:", len(elementos))

# 4. Empezar en "Artículo único" (el del cuerpo, no el del índice)
inicio = -1
for i in range(len(elementos)):
    if elementos[i][3].startswith("Artículo único"):
        inicio = i
        break
if inicio == -1:
    print("AVISO: no encuentro 'Artículo único'")
else:
    elementos = elementos[inicio:]

# 5. Unir los párrafos cortados al cambiar de página:
#    si un elemento empieza en minúscula (y no es "a)", "b)"...), continúa al anterior
textos = []
unidos = 0
for elemento in elementos:
    t = elemento[3]
    if len(textos) > 0 and t[0].islower() and not patron_letra.match(t):
        textos[-1] = textos[-1] + " " + t
        unidos = unidos + 1
    else:
        textos.append(t)
print("Párrafos unidos por cambio de página:", unidos)

texto = "\n\n".join(textos)
LIMPIO.write_text(texto, encoding="utf-8")
print("Caracteres:", len(texto))