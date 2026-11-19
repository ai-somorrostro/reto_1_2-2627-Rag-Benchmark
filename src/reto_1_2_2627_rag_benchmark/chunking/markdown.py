"""Lector de markdown orientado a trocear, no a renderizar.

Solo se necesitan cinco cosas del markdown:

* la jerarquía de títulos, para saber a qué artículo o sección pertenece cada
  fragmento;
* los párrafos, como unidades de corte;
* los bloques de código, que no deben partirse ni mezclarse con la prosa;
* las líneas de origen, para poder revisar un chunk contra el documento;
* avisos de formato raro, sin intentar arreglar el documento.

No se usa una librería de markdown a propósito: el conversor puede dejar
niveles de título irregulares o fences sin cerrar, y aquí interesa ser
tolerante y explícito sobre lo que se encuentra, no fallar.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# Se aceptan hasta 8 almohadillas porque algunos conversores generan
# jerarquías más profundas que el máximo de 6 de CommonMark.
HEADING_RE = re.compile(r"^(#{1,8})[ \t]+(.+?)[ \t]*#*[ \t]*$")
FENCE_RE = re.compile(r"^[ \t]*(`{3,}|~{3,})[ \t]*([^ \t`]*)")

KIND_HEADING = "heading"
KIND_TEXT = "text"
KIND_CODE = "code"


@dataclass(frozen=True)
class Block:
    kind: str
    text: str
    start_line: int
    end_line: int
    level: int = 0
    lang: str = ""


@dataclass
class ParsedMarkdown:
    blocks: list[Block] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _flush_text(
    blocks: list[Block], buffer: list[str], start_line: int, end_line: int
) -> None:
    if not buffer:
        return
    text = "\n".join(buffer).strip()
    if text:
        blocks.append(Block(KIND_TEXT, text, start_line, end_line))
    buffer.clear()


def parse_markdown(document: str) -> ParsedMarkdown:
    """Divide el documento en títulos, párrafos y bloques de código."""
    parsed = ParsedMarkdown()
    lines = document.splitlines()
    buffer: list[str] = []
    buffer_start = 1
    i = 0

    while i < len(lines):
        line = lines[i]

        if not line.strip():
            _flush_text(parsed.blocks, buffer, buffer_start, i)
            i += 1
            continue

        fence = FENCE_RE.match(line)
        if fence:
            _flush_text(parsed.blocks, buffer, buffer_start, i)
            start = i
            marker = fence.group(1)
            lang = fence.group(2)
            i += 1
            while i < len(lines):
                if re.match(
                    r"^[ \t]*" + re.escape(marker[0]) + r"{" + str(len(marker)) + r",}[ \t]*$",
                    lines[i],
                ):
                    i += 1
                    break
                i += 1
            else:
                parsed.warnings.append(
                    f"bloque de código sin cerrar desde la línea {start + 1}"
                )
            text = "\n".join(lines[start:i]).strip()
            parsed.blocks.append(
                Block(KIND_CODE, text, start + 1, i, lang=lang)
            )
            continue

        heading = HEADING_RE.match(line)
        if heading:
            _flush_text(parsed.blocks, buffer, buffer_start, i)
            parsed.blocks.append(
                Block(
                    KIND_HEADING,
                    heading.group(2).strip(),
                    i + 1,
                    i + 1,
                    level=len(heading.group(1)),
                )
            )
            i += 1
            continue

        if not buffer:
            buffer_start = i + 1
        buffer.append(line.rstrip())
        i += 1

    _flush_text(parsed.blocks, buffer, buffer_start, len(lines))
    return parsed
