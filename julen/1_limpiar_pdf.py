import fitz  # PyMuPDF

pdf_entrada = "BOE-A-2015-11430-consolidado.pdf"
pdf_salida = "boe_limpio.pdf"

doc = fitz.open(pdf_entrada)
doc_limpio = fitz.open()

# Empezamos en el índice 7 (página 8 del PDF) para saltar las 7 páginas del índice
for num_pag in range(7, len(doc)):
    pagina = doc[num_pag]
    rect = pagina.rect
    # Recortamos 85 pt arriba (cabecera BOE) y 60 pt abajo (pie "Página X")
    zona_util = fitz.Rect(rect.x0, rect.y0 + 85, rect.x1, rect.y1 - 60)
    pagina.set_cropbox(zona_util)
    doc_limpio.insert_pdf(doc, from_page=num_pag, to_page=num_pag)

doc_limpio.save(pdf_salida)
print(f"PDF limpio guardado en '{pdf_salida}' con {len(doc_limpio)} páginas.")

# Comprobación rápida de la primera página limpia
print("\n--- Muestra de texto tras limpiar ---")
print(doc_limpio[0].get_text("text")[:400])