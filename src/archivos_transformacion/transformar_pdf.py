from docling.document_converter import DocumentConverter
from pathlib import Path

# Ruta del PDF de entrada
pdf_path = "/home/g5/reto_1_2-2627-Rag-Benchmark/docs/raw/BOE-A-2015-11430.pdf"

# Ruta del Markdown de salida
md_path = "/home/g5/reto_1_2-2627-Rag-Benchmark/docs/procesado/BOE.md"

# Crear el conversor
converter = DocumentConverter()

# Convertir el PDF
result = converter.convert(pdf_path)

# Exportar a Markdown
markdown = result.document.export_to_markdown()

# Guardar el resultado
Path(md_path).write_text(markdown, encoding="utf-8")

print(f"Conversión finalizada: {md_path}")
print(f"Estado: {result.status}")