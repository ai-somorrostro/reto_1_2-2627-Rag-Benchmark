import re
from pathlib import Path
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter 

MAX_CHARS = 1800          # ~450 tokens
OVERLAP   = 200           # ~10-12 %

recursive = RecursiveCharacterTextSplitter( 
    chunk_size=MAX_CHARS,
    chunk_overlap=OVERLAP,
    separators=["\n\n", "\n", r"(?<=\.)\s", "; ", " "],
    is_separator_regex=True,
)


# ---------- Debian: por cabeceras markdown ----------
md_split = MarkdownHeaderTextSplitter( #Dibide
    headers_to_split_on=[("#", "capitulo"), ("##", "seccion"), ("###", "subseccion")],
    strip_headers=False,
)

SIDEBAR_RE = re.compile(r"^\*[A-ZÁÉÍÓÚÑ][A-Za-záéíóúÁÉÍÓÚñÑ ]+\*")


def chunk_debian(text: str):
    out = []
    for d in md_split.split_text(text):
        content = d.page_content.strip()
        if not content:
            continue

        ctx = " > ".join(v for v in d.metadata.values() if v)

        lines_no_header = re.sub(r"^#+\s*.*\n?", "", content).strip()
        kind = "sidebar" if SIDEBAR_RE.match(lines_no_header) else "body"

        pieces = (
            [content]
            if len(content) <= MAX_CHARS
            else recursive.split_text(content)
        )
        total = len(pieces)

        for i, p in enumerate(pieces, 1):
            sufijo = f" (parte {i}/{total})" if total > 1 else ""
            header = f"{ctx}{sufijo}" if ctx else sufijo.strip()

            out.append(
                (
                    f"{header}\n{p}" if header else p,
                    {
                        **d.metadata,
                        "doc": "debian-handbook",
                        "tipo": kind,
                        "parte": f"{i}/{total}" if total > 1 else "1/1",
                    },
                )
            )
    return out


if __name__ == "__main__":
    base = Path("/home/g5/reto_1_2-2627-Rag-Benchmark/docs/limpio")

    debian_file = base / "debian-handbook.md"
    if debian_file.exists():
        debian_chunks = chunk_debian(debian_file.read_text(encoding="utf-8"))

        print(f"{len(debian_chunks)} fragmentos")

        for texto, meta in debian_chunks:
            ruta = " > ".join(
                meta[k] for k in ("capitulo", "seccion", "subseccion") if meta.get(k)
            )
            parte = meta["parte"] if meta["parte"] != "1/1" else ""

            print(
                f"- {ruta}"
                f"{' ' + parte if parte else ''}"
                f" ({len(texto)} caracteres)"
            )
    else:
        print(f"No existe el archivo: {debian_file}")