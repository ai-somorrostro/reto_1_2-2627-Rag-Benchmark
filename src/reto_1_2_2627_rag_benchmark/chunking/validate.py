"""Validación de los chunks antes de congelarlos.

El validador no arregla nada: comprueba que el artefacto cumple el contrato
que usarán el golden set y las fases 2 y 3. Los errores bloquean la
congelación; los avisos señalan cosas a revisar a mano (chunks diminutos,
posible ruido de títulos, textos duplicados).
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from .config import ScenarioConfig, Settings, chunks_path
from .pipeline import token_stats
from .tokens import estimate_tokens

ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
PART_RE = re.compile(r"-p(\d+)$")
HEADING_LEAK_RE = re.compile(r"^#{1,8}\s+\S", re.MULTILINE)

REQUIRED_FIELDS = {
    "id": str,
    "scenario": str,
    "source": str,
    "section": str,
    "section_path": list,
    "article": (str, type(None)),
    "text": str,
    "n_chars": int,
    "n_tokens_est": int,
    "part": int,
    "n_parts": int,
    "start_line": int,
    "end_line": int,
}


@dataclass
class Report:
    scenario: str
    path: Path | None = None
    chunks: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    stats: dict = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.errors


def load_records(path: Path) -> list[dict]:
    records: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{number}: JSON inválido: {exc}") from exc
    return records


def _outside_fenced_code(text: str) -> str:
    lines: list[str] = []
    fence_char: str | None = None
    fence_length = 0

    for line in text.splitlines():
        fence = re.match(r"^[ \t]*(`{3,}|~{3,})", line)
        if fence:
            marker = fence.group(1)
            if fence_char is None:
                fence_char = marker[0]
                fence_length = len(marker)
            elif marker[0] == fence_char and len(marker) >= fence_length:
                if re.fullmatch(
                    r"[ \t]*" + re.escape(marker[0]) + "{" + str(fence_length) + r",}[ \t]*",
                    line,
                ):
                    fence_char = None
                    fence_length = 0
            continue

        if fence_char is None:
            lines.append(line)

    return "\n".join(lines)


def validate_records(
    records: list[dict],
    cfg: ScenarioConfig,
    *,
    path: Path | None = None,
) -> Report:
    report = Report(scenario=cfg.name, path=path, chunks=len(records))
    if not records:
        report.errors.append("el fichero no contiene chunks")
        return report

    seen_ids: set[str] = set()
    seen_texts: dict[str, str] = {}
    by_base: dict[str, list[int]] = defaultdict(list)
    declared_parts: dict[str, set[int]] = defaultdict(set)
    tiny: list[str] = []

    for position, record in enumerate(records, start=1):
        label = record.get("id") if isinstance(record, dict) else None
        prefix = f"chunk #{position} ({label or 'sin id'})"

        if not isinstance(record, dict):
            report.errors.append(f"{prefix}: no es un objeto JSON")
            continue

        schema_error = False
        for key, expected in REQUIRED_FIELDS.items():
            if key not in record:
                report.errors.append(f"{prefix}: falta el campo '{key}'")
                schema_error = True
                continue
            value = record[key]
            if not isinstance(value, expected):
                report.errors.append(
                    f"{prefix}: '{key}' debería ser {expected}, es {type(value).__name__}"
                )
                schema_error = True
        if schema_error:
            continue

        chunk_id = record["id"]
        if not ID_RE.match(chunk_id):
            report.errors.append(
                f"{prefix}: id no válido (usa minúsculas, números y guiones)"
            )
        if chunk_id in seen_ids:
            report.errors.append(f"{prefix}: id duplicado")
        seen_ids.add(chunk_id)

        if record["scenario"] != cfg.name:
            report.errors.append(
                f"{prefix}: escenario '{record['scenario']}' != '{cfg.name}'"
            )

        text = record["text"]
        if not text.strip():
            report.errors.append(f"{prefix}: texto vacío")
        if record["n_chars"] != len(text):
            report.errors.append(
                f"{prefix}: n_chars={record['n_chars']} pero el texto tiene {len(text)}"
            )
        expected_tokens = estimate_tokens(text, cfg.chars_per_token)
        if record["n_tokens_est"] != expected_tokens:
            report.errors.append(
                f"{prefix}: n_tokens_est={record['n_tokens_est']} pero la "
                f"estimación actual da {expected_tokens}; vuelve a trocear"
            )
        if record["n_tokens_est"] > cfg.max_tokens:
            report.errors.append(
                f"{prefix}: {record['n_tokens_est']} tokens > máximo {cfg.max_tokens}"
            )
        if record["n_tokens_est"] < cfg.min_tokens:
            tiny.append(chunk_id)

        if not record["section"].strip():
            report.errors.append(f"{prefix}: sección vacía")
        if not record["section_path"] or not all(
            isinstance(item, str) and item.strip() for item in record["section_path"]
        ):
            report.errors.append(f"{prefix}: section_path vacío o inválido")
        if record["section"].startswith("Artículo") and record["article"] is None:
            report.errors.append(
                f"{prefix}: la sección es un artículo pero 'article' es null"
            )

        if record["part"] < 1 or record["n_parts"] < record["part"]:
            report.errors.append(
                f"{prefix}: part={record['part']} incoherente con "
                f"n_parts={record['n_parts']}"
            )
        if record["start_line"] < 1 or record["end_line"] < record["start_line"]:
            report.errors.append(f"{prefix}: líneas de origen inválidas")

        fence_lines = [
            line
            for line in text.splitlines()
            if line.strip().startswith(("```", "~~~"))
        ]
        if len(fence_lines) % 2:
            report.errors.append(f"{prefix}: fence de código sin cerrar")

        if HEADING_LEAK_RE.search(_outside_fenced_code(text)):
            report.warnings.append(
                f"{prefix}: el texto contiene una línea con '#' (posible título mal parseado)"
            )

        normalized = " ".join(text.split())
        if normalized in seen_texts:
            report.warnings.append(
                f"{prefix}: texto idéntico a {seen_texts[normalized]}"
            )
        else:
            seen_texts[normalized] = chunk_id

        match = PART_RE.search(chunk_id)
        if not match:
            report.errors.append(f"{prefix}: el id no termina en '-pNN'")
        else:
            if int(match.group(1)) != record["part"]:
                report.errors.append(
                    f"{prefix}: el sufijo del id no coincide con part="
                    f"{record['part']}"
                )
            base = chunk_id[: match.start()]
            by_base[base].append(record["part"])
            declared_parts[base].add(record["n_parts"])

    for base, parts in by_base.items():
        if sorted(parts) != list(range(1, len(parts) + 1)):
            report.errors.append(
                f"{base}: partes no consecutivas o repetidas: {sorted(parts)}"
            )
        if len(declared_parts[base]) != 1:
            report.errors.append(f"{base}: n_parts incoherente entre sus partes")
        else:
            expected_parts = next(iter(declared_parts[base]))
            if expected_parts != len(parts):
                report.errors.append(
                    f"{base}: declara {expected_parts} partes pero hay {len(parts)}"
                )

    if tiny:
        report.warnings.append(
            f"{len(tiny)} chunks por debajo de min_tokens={cfg.min_tokens} "
            f"(revisar: {', '.join(tiny[:10])}{'…' if len(tiny) > 10 else ''})"
        )

    report.stats = token_stats(records)
    return report


def validate_scenario(settings: Settings, scenario: str) -> Report:
    path = chunks_path(settings, scenario)
    if not path.is_file():
        report = Report(scenario=scenario, path=path)
        report.errors.append(
            f"no existe {path}; ejecuta antes 'ragbench chunk build --scenario {scenario}'"
        )
        return report
    try:
        records = load_records(path)
    except ValueError as exc:
        report = Report(scenario=scenario, path=path)
        report.errors.append(str(exc))
        return report
    return validate_records(records, settings.scenarios[scenario], path=path)
