from docling.document_converter import DocumentConverter
from pathlib import Path

# Ruta del EPUB de entrada
epub_path = "/home/g5/reto_1_2-2627-Rag-Benchmark/docs/raw/debian-handbook.epub"

# Ruta del Markdown de salida
md_path = "/home/g5/reto_1_2-2627-Rag-Benchmark/docs/procesado/debian-handbook.md"

# Crear directorio de salida
Path(md_path).parent.mkdir(parents=True, exist_ok=True)

# Crear conversor
converter = DocumentConverter()

# Convertir EPUB
result = converter.convert(epub_path)

# Exportar a Markdown
markdown = result.document.export_to_markdown()

# Guardar resultado
Path(md_path).write_text(markdown, encoding="utf-8")

print(f"Conversión finalizada: {md_path}")
print(f"Estado: {result.status}")