import re
import html
from pathlib import Path

# ---------- BOE ----------
BOE_NOISE = [
    r"^\s*(?:#+\s*)?BOLETÍN OFICIAL DEL ESTADO\s*$",
    r"^\s*Núm\.\s*\d+\s*$",
    r"^\s*(?:Lunes|Martes|Miércoles|Jueves|Viernes|Sábado|Domingo)\s+\d{1,2}\s+de\s+\w+\s+de\s+\d{4}\s*$",
    r"^\s*Sec\.\s*[IVX]+\.\s*Pág\.\s*\d+\s*$",
    r"^\s*cve:\s*BOE-[A-Z]-\d+-\d+\s*$",
    r"^\s*Verificable en https?://www\.boe\.es\s*$",
    r"^\s*<!--\s*image\s*-->\s*$",
    r"^\s*(?:3\.0|3|E|FELIPE R\.)\s*$",
]

BOE_STRUCT_RE = re.compile(
    r"^(?:TÍTULO [IVX]+|CAPÍTULO [IVX]+|Sección \d|Artículo \d+\.|Disposición (?:adicional|transitoria|derogatoria|final))"
)


def limpiar_boe(text: str) -> str:
    # 1. Quedarse con el articulado (descarta preámbulo e índice)
    text = text[text.index("## TÍTULO I"):] if "## TÍTULO I" in text else text

    # 2. Eliminar cabeceras/pies de página y artefactos del PDF
    for p in BOE_NOISE:
        text = re.sub(p, "", text, flags=re.M | re.I)

    # 3. Normalizar listas y quitar almohadillas Markdown para el splitter de BOE
    text = re.sub(r"^\s*-\s+(?=[a-z]\)|\d+\.)", "", text, flags=re.M)
    text = re.sub(r"^#+\s*", "", text, flags=re.M)

    # 4. Reunir párrafos cortados por salto de página
    paras = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
    merged = []
    for p in paras:
        if (
            merged
            and not BOE_STRUCT_RE.match(p)
            and not re.search(r"[.;:]$", merged[-1])
            and p[0].islower()
        ):
            merged[-1] += " " + p
        else:
            merged.append(p)

    return "\n\n".join(merged)


# ---------- Debian ----------
def limpiar_debian(text: str) -> str:
    text = html.unescape(text)

    # 1. Saltar índice, créditos, prólogo y agradecimientos: ir directo al Capítulo 1
    m_start = re.search(r"(?m)^#\s+(?:Capítulo\s+)?1\.\s+El proyecto Debian", text)
    if m_start:
        text = text[m_start.start():]
    elif "# Prólogo" in text:
        text = text[text.index("# Prólogo"):]

    # 2. Eliminar marcadores de imagen y flechas de enlaces externos sueltos
    text = re.sub(r"<!--\s*image\s*-->", "", text)
    text = re.sub(r"^\s*→\s*\[.*?\]\(.*?\)\s*$", "", text, flags=re.M)

    # 3. Limpiar enlaces Markdown conservando texto y formato de código
    text = re.sub(r"\[(?:\*{1,2})?(`[^`]+`)(?:\*{1,2})?\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[\*{0,2}(.*?)\*{0,2}\]\([^)]*\)", r"\1", text)

    # 4. Limpiar correos entre < > tipo <user@debian.org>
    text = re.sub(r"<([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})>", r"\1", text)

    # 5. Normalizar escapes y código en negrita
    text = text.replace(r"\_", "_")
    text = re.sub(r"\*\*`(.*?)`\*\*", r"`\1`", text)

    # 6. Eliminar posibles restos de navegación HTML
    text = re.sub(r"^\s*(?:Anterior|Siguiente|Subir|Inicio)\s*$", "", text, flags=re.M)

    # 7. Normalizar saltos de línea excesivos
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Eliminar flechas + URL que quedaron en mitad de párrafo (ej. "→ https://...") para que el llm no alucine con esos url y lo use para todo
    text = re.sub(r"\s*→\s*https?://\S+", "", text)

    # Limpiar correos con formato roto tipo `<``user@debian.org``>` puede corromper los tokens
    text = re.sub(r"`<``([^`]+)``>`", r"`\1`", text)

    # Normalizar encabezados mal formados (ej. "# ## 1.2. Título" -> "## 1.2. Título")
    text = re.sub(r"^(#+)\s+#+\s*", r"\1 ", text, flags=re.M)
    text = re.sub(r"^(#+)\s+", r"\1 ", text, flags=re.M)

    return text.strip()

if __name__ == "__main__":
    base = Path("/home/g5/reto_1_2-2627-Rag-Benchmark/docs")
    (base / "limpio").mkdir(parents=True, exist_ok=True)

    # Limpiar BOE
    boe_in = base / "procesado/BOE.md"
    if boe_in.exists():
        (base / "limpio/BOE.md").write_text(
            limpiar_boe(boe_in.read_text(encoding="utf-8")), encoding="utf-8"
        )
        print("BOE limpio guardado.")

    # Limpiar Debian
    debian_in = base / "procesado/debian-handbook.md"
    if debian_in.exists():
        (base / "limpio/debian-handbook.md").write_text(
            limpiar_debian(debian_in.read_text(encoding="utf-8")), encoding="utf-8"
        )
        print("Debian limpio guardado.")