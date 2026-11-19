"""Ejecución del troceado y generación de artefactos trazables."""

from __future__ import annotations

import hashlib
import json
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from .chunker import chunk_document
from .config import ScenarioConfig, Settings, chunks_path


@dataclass
class BuildResult:
    scenario: str
    source: Path
    source_sha256: str
    chunks: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    out_path: Path | None = None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def token_stats(chunks: list[dict]) -> dict:
    if not chunks:
        return {
            "chunks": 0,
            "tokens_min": 0,
            "tokens_median": 0,
            "tokens_p95": 0,
            "tokens_max": 0,
            "chars_total": 0,
        }
    tokens = sorted(chunk["n_tokens_est"] for chunk in chunks)
    p95_index = max(0, int(round(0.95 * (len(tokens) - 1))))
    return {
        "chunks": len(chunks),
        "tokens_min": tokens[0],
        "tokens_median": int(statistics.median(tokens)),
        "tokens_p95": tokens[p95_index],
        "tokens_max": tokens[-1],
        "chars_total": sum(chunk["n_chars"] for chunk in chunks),
    }


def _relative(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def build_scenario(
    settings: Settings,
    scenario: str,
    *,
    dry_run: bool = False,
) -> BuildResult:
    cfg: ScenarioConfig = settings.scenarios[scenario]
    if not cfg.source.is_file():
        raise FileNotFoundError(
            f"no existe el markdown de '{scenario}': {cfg.source}\n"
            "Revisa la ruta en config/chunking.toml o espera a que esté listo."
        )

    document = cfg.source.read_text(encoding="utf-8")
    source_relative = _relative(cfg.source, settings.config_path.parent.parent)
    chunks, warnings = chunk_document(
        document, scenario=scenario, source=source_relative, cfg=cfg
    )
    result = BuildResult(
        scenario=scenario,
        source=cfg.source,
        source_sha256=sha256_file(cfg.source),
        chunks=chunks,
        warnings=warnings,
    )

    if not dry_run:
        settings.out_dir.mkdir(parents=True, exist_ok=True)
        out_path = chunks_path(settings, scenario)
        tmp_path = out_path.with_suffix(".jsonl.tmp")
        with tmp_path.open("w", encoding="utf-8") as handle:
            for chunk in chunks:
                handle.write(json.dumps(chunk, ensure_ascii=False) + "\n")
        tmp_path.replace(out_path)
        result.out_path = out_path
        _update_manifest(settings, result)

    return result


def _update_manifest(settings: Settings, result: BuildResult) -> None:
    manifest_path = settings.out_dir / "manifest.json"
    manifest: dict = {"scenarios": {}}
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    manifest["config"] = _relative(settings.config_path, settings.config_path.parent.parent)
    manifest["config_sha256"] = sha256_file(settings.config_path)
    manifest["updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    manifest.setdefault("scenarios", {})[result.scenario] = {
        "source": _relative(result.source, settings.config_path.parent.parent),
        "source_sha256": result.source_sha256,
        "output": _relative(result.out_path, settings.config_path.parent.parent)
        if result.out_path
        else None,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "stats": token_stats(result.chunks),
        "parser_warnings": result.warnings,
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def build_all(settings: Settings, *, dry_run: bool = False) -> list[BuildResult]:
    return [
        build_scenario(settings, name, dry_run=dry_run)
        for name in sorted(settings.scenarios)
    ]
