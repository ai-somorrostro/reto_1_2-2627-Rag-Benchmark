import json
import re
from pathlib import Path

from docling.chunking import HybridChunker
from docling.document_converter import DocumentConverter
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "comun" / "debian-handbook.epub"
OUTPUT = ROOT / "comun" / "chunks_debian.json"
MAX_TOKENS = 450
MIN_WORDS = 10


def word_count(text):
    return len(text.split())


def has_content(text):
    return len(re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]", text)) >= 3


def is_toc(text):
    return (
        "Tabla de contenidos" in text
        and text.count("](") > 15
    ) or text.count("](") > 60


def is_short_noise(text):
    return word_count(text) < MIN_WORDS and (
        text.count("](") > 0
        or text.lstrip().startswith("→")
        or not re.search(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]{4}", text)
    )


def build_chunk(text, headings, meta):
    return {
        "texto": text.strip(),
        "titulos": list(headings),
        "metadatos": meta,
    }


def merge(a, b):
    headings = list(dict.fromkeys(a["titulos"] + b["titulos"]))
    meta = dict(a["metadatos"])
    meta["headings"] = headings
    return build_chunk(a["texto"] + "\n" + b["texto"], headings, meta)


converter = DocumentConverter()
document = converter.convert(SOURCE).document
tokenizer = HuggingFaceTokenizer.from_pretrained(
    model_name="BAAI/bge-m3",
    max_tokens=MAX_TOKENS,
)
raw = list(HybridChunker(tokenizer=tokenizer, merge_peers=True).chunk(document))

chunks = []
for chunk in raw:
    text = chunk.text.strip()
    if not text or not has_content(text) or is_toc(text) or is_short_noise(text):
        continue
    meta = chunk.meta.export_json_dict()
    headings = [h for h in getattr(chunk.meta, "headings", []) or []]
    chunks.append(build_chunk(text, headings, meta))

merged = []
i = 0
while i < len(chunks):
    current = chunks[i]
    j = i
    while word_count(current["texto"]) < MIN_WORDS and j + 1 < len(chunks):
        candidate = merge(current, chunks[j + 1])
        if tokenizer.count_tokens(candidate["texto"]) <= MAX_TOKENS:
            current = candidate
            j += 1
            continue
        if merged:
            candidate = merge(merged[-1], current)
            if tokenizer.count_tokens(candidate["texto"]) <= MAX_TOKENS:
                merged[-1] = candidate
                current = None
        break
    if current is not None:
        merged.append(current)
    i = j + 1

final = []
for chunk in merged:
    chunk["texto"] = re.sub(r"\n{3,}", "\n\n", chunk["texto"]).strip()
    if word_count(chunk["texto"]) >= MIN_WORDS:
        final.append(chunk)

for index, chunk in enumerate(final, start=1):
    chunk_with_id = {"id": f"chunk_debian_{index}"}
    chunk_with_id.update(chunk)
    final[index - 1] = chunk_with_id

OUTPUT.write_text(
    json.dumps(final, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)

tokens = [tokenizer.count_tokens(c["texto"]) for c in final]
words = [word_count(c["texto"]) for c in final]
print(f"fuente: {SOURCE}")
print(f"chunks: {len(final)}")
print(f"menos de {MIN_WORDS} palabras: {sum(w < MIN_WORDS for w in words)}")
print(f"max palabras: {max(words)}")
print(f"max tokens: {max(tokens)}")
print(f"por encima de {MAX_TOKENS} tokens: {sum(t > MAX_TOKENS for t in tokens)}")
print(f"sin titulos: {sum(not c['titulos'] for c in final)}")
