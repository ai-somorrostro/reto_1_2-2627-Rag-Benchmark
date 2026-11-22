import json
import re
import importlib.metadata
from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker

# 1. Conversión del PDF limpio con Docling
converter = DocumentConverter()
result = converter.convert("boe_limpio.pdf")
doc = result.document

# 2. Configurar HybridChunker (compatible con distintas versiones de Docling 2.x)
MAX_TOKENS = 450
TOKENIZER_MODEL = "BAAI/bge-m3"

try:
    from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
    tokenizer = HuggingFaceTokenizer.from_pretrained(
        model_name=TOKENIZER_MODEL,
        max_tokens=MAX_TOKENS,
    )
    chunker = HybridChunker(tokenizer=tokenizer, merge_peers=True)
except Exception:
    chunker = HybridChunker(max_tokens=MAX_TOKENS)

# 3. Generar chunks conservando artículo/sección en metadatos
chunks_export = []
ultimo_articulo = "Preámbulo / Disposiciones iniciales"
patron_art = re.compile(
    r"^(Artículo\s+\d+(?:\s+bis|\s+ter)?\.?[^\n]*|Disposición\s+(?:adicional|transitoria|derogatoria|final)\s+[^\n]*)",
    re.IGNORECASE | re.MULTILINE,
)

for idx, chunk in enumerate(chunker.chunk(dl_doc=doc), start=1):
    headings = list(chunk.meta.headings) if getattr(chunk.meta, "headings", None) else []
    texto_limpio = chunk.text.strip()

    # Detectar artículo desde los encabezados de Docling o desde el propio texto
    articulo_detectado = None
    for h in reversed(headings):
        if re.match(r"^(Artículo|Disposición)\s+", h.strip(), re.IGNORECASE):
            articulo_detectado = h.strip()
            break

    if not articulo_detectado:
        match = patron_art.search(texto_limpio)
        if match:
            articulo_detectado = match.group(1).strip()

    if articulo_detectado:
        ultimo_articulo = articulo_detectado

    chunks_export.append({
        "id": f"boe_{idx:04d}",
        "articulo": ultimo_articulo,
        "headings": headings,
        "texto": texto_limpio,
    })

# 4. Guardar JSON de chunks
with open("chunks_boe.json", "w", encoding="utf-8") as f:
    json.dump(chunks_export, f, ensure_ascii=False, indent=2)

# 5. Guardar evidencia de trazabilidad
version_docling = importlib.metadata.version("docling")
trazabilidad = (
    f"Versión de Docling: {version_docling}\n"
    f"Documento fuente: BOE-A-2015-11430-consolidado.pdf (páginas 8-97, sin índice, cabeceras ni pies)\n"
    f"Estrategia: HybridChunker (merge_peers=True)\n"
    f"Tokenizador: {TOKENIZER_MODEL}\n"
    f"Tamaño máximo de chunk: {MAX_TOKENS} tokens\n"
    f"Total de chunks generados: {len(chunks_export)}\n"
)

with open("trazabilidad_boe.txt", "w", encoding="utf-8") as f:
    f.write(trazabilidad)

print(trazabilidad)
print("--- Primeros 3 chunks de muestra ---")
for c in chunks_export[:3]:
    print(json.dumps(c, ensure_ascii=False, indent=2))