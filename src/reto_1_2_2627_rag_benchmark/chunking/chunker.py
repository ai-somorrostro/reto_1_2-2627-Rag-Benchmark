"""Troceado del corpus a partir de los markdown de ``data/``.

Reglas que aplica el troceador:

* cada título abre una sección nueva; el texto se agrupa por secciones, de
  modo que un chunk nunca mezcla dos artículos o dos secciones;
* las secciones largas se parten por párrafos, con solape configurable;
* los bloques de código se conservan íntegros y, si no caben, se parten
  cerrando y reabriendo el fence;
* cada chunk lleva el título de su sección al principio del texto, además de
  metadatos para citar (artículo, ruta de títulos) y líneas de origen.

Los IDs son deterministas: mismo documento y misma configuración producen
siempre los mismos IDs. Eso es lo que permite que el golden set apunte a
chunks concretos y que las fases 2 y 3 sean reproducibles.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from .config import ScenarioConfig
from .markdown import (
    KIND_CODE,
    KIND_HEADING,
    Block,
    ParsedMarkdown,
)
from .tokens import estimate_tokens

ARTICLE_RE = re.compile(
    r"^Art[ií]culo\s+(\d+|único|unico)\s*(bis|ter|qu[áa]ter)?\b", re.IGNORECASE
)
DISPOSITION_RE = re.compile(r"^Disposici[oó]n\s+(.+?)(?:[.:]|$)", re.IGNORECASE)
CHAPTER_RE = re.compile(r"^Cap[ií]tulo\s+(\d+)", re.IGNORECASE)
NUMBER_RE = re.compile(r"^(\d+(?:\.\d+)*)\.\s*")

SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
MIN_BODY_CHARS = 120


@dataclass
class Section:
    heading: Block | None
    path: list[str]
    blocks: list[Block]


@dataclass(frozen=True)
class Unit:
    text: str
    start_line: int
    end_line: int


def _slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")
    return slug[:48].rstrip("-") or "doc"


def _article_label(heading: str) -> str | None:
    match = ARTICLE_RE.match(heading)
    if not match:
        return None
    number, suffix = match.group(1), match.group(2)
    return f"{number} {suffix.lower()}" if suffix else number


def _base_id(scenario: str, heading: str | None) -> str:
    if not heading:
        return f"{scenario}-doc"

    article = _article_label(heading)
    if article:
        return f"{scenario}-art{_slugify(article)}"

    disposition = DISPOSITION_RE.match(heading)
    if disposition:
        return f"{scenario}-{_slugify(disposition.group(1))}"

    chapter = CHAPTER_RE.match(heading)
    if chapter:
        return f"{scenario}-cap{chapter.group(1)}"

    number = NUMBER_RE.match(heading)
    if number:
        return f"{scenario}-{number.group(1).replace('.', '-')}"

    return f"{scenario}-{_slugify(heading)}"


def _split_sections(parsed: ParsedMarkdown) -> list[Section]:
    """Agrupa bloques por título. Los títulos sin cuerpo no generan sección."""
    sections: list[Section] = []
    stack: list[Block] = []
    current = Section(heading=None, path=[], blocks=[])

    for block in parsed.blocks:
        if block.kind != KIND_HEADING:
            current.blocks.append(block)
            continue

        if current.blocks:
            sections.append(current)

        while stack and stack[-1].level >= block.level:
            stack.pop()
        stack.append(block)
        current = Section(
            heading=block,
            path=[item.text for item in stack],
            blocks=[],
        )

    if current.blocks:
        sections.append(current)
    return sections


def _hard_split(text: str, budget: int) -> list[str]:
    pieces: list[str] = []
    remaining = text.strip()
    while len(remaining) > budget:
        cut = remaining.rfind(" ", 0, budget)
        if cut < budget // 2:
            cut = budget
        pieces.append(remaining[:cut].strip())
        remaining = remaining[cut:].strip()
    if remaining:
        pieces.append(remaining)
    return [piece for piece in pieces if piece]


def _split_text_block(text: str, budget: int) -> list[str]:
    """Parte un párrafo por frases y, si hace falta, por longitud."""
    sentences: list[str] = []
    for sentence in SENTENCE_RE.split(text):
        sentence = sentence.strip()
        if not sentence:
            continue
        if len(sentence) <= budget:
            sentences.append(sentence)
        else:
            sentences.extend(_hard_split(sentence, budget))

    pieces: list[str] = []
    current: list[str] = []
    size = 0
    for sentence in sentences:
        extra = len(sentence) + (1 if current else 0)
        if current and size + extra > budget:
            pieces.append(" ".join(current))
            current, size = [], 0
            extra = len(sentence)
        current.append(sentence)
        size += extra
    if current:
        pieces.append(" ".join(current))
    return pieces


def _split_code_block(block: Block, budget: int) -> list[str]:
    """Parte un bloque de código sin dejar fences abiertos."""
    lines = block.text.splitlines()
    if not lines:
        return [block.text]

    opening = lines[0]
    closing = lines[-1] if lines[-1].strip().startswith(("```", "~~~")) else None
    body = lines[1:-1] if closing else lines[1:]
    overhead = len(opening) + len(closing or "") + 2
    body_budget = max(MIN_BODY_CHARS, budget - overhead)

    pieces: list[str] = []
    current: list[str] = []
    size = 0
    for line in body:
        line_parts = _hard_split(line, body_budget) if len(line) > body_budget else [line]
        for part in line_parts:
            extra = len(part) + 1
            if current and size + extra > body_budget:
                pieces.append("\n".join(current))
                current, size = [], 0
                extra = len(part)
            current.append(part)
            size += extra
    if current:
        pieces.append("\n".join(current))

    return [
        "\n".join([opening, *piece.splitlines(), closing or ""]).strip()
        for piece in pieces
    ]


def _section_units(section: Section, body_budget: int) -> list[Unit]:
    units: list[Unit] = []
    for block in section.blocks:
        if len(block.text) <= body_budget:
            units.append(Unit(block.text, block.start_line, block.end_line))
            continue
        if block.kind == KIND_CODE:
            pieces = _split_code_block(block, body_budget)
        else:
            pieces = _split_text_block(block.text, body_budget)
        units.extend(
            Unit(piece, block.start_line, block.end_line) for piece in pieces
        )
    return units


def _pack_units(
    units: list[Unit], budget: int, overlap_chars: int
) -> list[list[Unit]]:
    """Reparte unidades en partes con solape, sin superar ``budget``."""
    parts: list[list[Unit]] = []
    start = 0
    total = len(units)

    while start < total:
        current: list[Unit] = []
        size = 0
        index = start
        while index < total:
            extra = len(units[index].text) + (2 if current else 0)
            if current and size + extra > budget:
                break
            current.append(units[index])
            size += extra
            index += 1
        parts.append(current)
        if index >= total:
            break

        overlap: list[Unit] = []
        overlap_size = 0
        back = index - 1
        while back >= start and len(current) - len(overlap) > 1:
            extra = len(units[back].text) + (2 if overlap else 0)
            if overlap_size + extra > overlap_chars:
                break
            overlap.insert(0, units[back])
            overlap_size += extra
            back -= 1

        next_start = back + 1
        if next_start <= start:
            next_start = start + 1
        start = next_start

    return parts


def _section_title(section: Section) -> str:
    if section.heading is not None:
        return section.heading.text
    return "Documento"


def _prefix_for(section: Section, cfg: ScenarioConfig) -> str:
    if not cfg.include_section_title:
        return ""
    title = _section_title(section)
    max_chars = max(40, int((cfg.max_tokens / 4) * cfg.chars_per_token))
    if len(title) > max_chars:
        title = title[: max_chars - 1].rstrip() + "…"
    return title


def chunk_document(
    document: str,
    *,
    scenario: str,
    source: str,
    cfg: ScenarioConfig,
) -> tuple[list[dict], list[str]]:
    """Devuelve los chunks del documento y los avisos del parseo."""
    parsed = parse_and_warn(document)
    sections = _split_sections(parsed)
    chunks: list[dict] = []
    seen_bases: dict[str, int] = {}

    for section in sections:
        prefix = _prefix_for(section, cfg)
        prefix_overhead = len(prefix) + 2 if prefix else 0
        budget = int(cfg.max_tokens * cfg.chars_per_token) - prefix_overhead
        budget = max(MIN_BODY_CHARS, budget)

        units = _section_units(section, budget)
        if not units:
            continue

        body_texts = [unit.text for unit in units]
        if prefix and any(text.startswith(prefix) for text in body_texts):
            prefix = ""
            prefix_overhead = 0
            budget = max(
                MIN_BODY_CHARS, int(cfg.max_tokens * cfg.chars_per_token) - 2
            )
            units = _section_units(section, budget)

        parts = _pack_units(
            units, budget, int(cfg.overlap_tokens * cfg.chars_per_token)
        )
        base = _base_id(scenario, section.heading.text if section.heading else None)
        seen_bases[base] = seen_bases.get(base, 0) + 1
        if seen_bases[base] > 1:
            base = f"{base}-v{seen_bases[base]}"

        title = _section_title(section)
        article = _article_label(title) if section.heading else None

        for part_number, part_units in enumerate(parts, start=1):
            body = "\n\n".join(unit.text for unit in part_units)
            text = f"{prefix}\n\n{body}" if prefix else body
            record = {
                "id": f"{base}-p{part_number:02d}",
                "scenario": scenario,
                "source": source,
                "section": title,
                "section_path": section.path or [title],
                "article": article,
                "text": text,
                "n_chars": len(text),
                "n_tokens_est": estimate_tokens(text, cfg.chars_per_token),
                "part": part_number,
                "n_parts": len(parts),
                "start_line": part_units[0].start_line,
                "end_line": part_units[-1].end_line,
            }
            chunks.append(record)

    return chunks, parsed.warnings


def parse_and_warn(document: str) -> ParsedMarkdown:
    # Import local para que los tests puedan sustituir el parser si hace falta.
    from .markdown import parse_markdown

    return parse_markdown(document)
