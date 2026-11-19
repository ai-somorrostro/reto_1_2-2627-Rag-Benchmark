"""Carga de la configuración de troceado (``config/chunking.toml``)."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ScenarioConfig:
    name: str
    source: Path
    max_tokens: int
    min_tokens: int
    overlap_tokens: int
    chars_per_token: float
    include_section_title: bool

    def __post_init__(self) -> None:
        if self.max_tokens <= 0:
            raise ValueError(f"{self.name}: max_tokens debe ser positivo")
        if self.min_tokens >= self.max_tokens:
            raise ValueError(f"{self.name}: min_tokens debe ser menor que max_tokens")
        if not 0 <= self.overlap_tokens < self.max_tokens:
            raise ValueError(
                f"{self.name}: overlap_tokens debe estar entre 0 y max_tokens"
            )
        if self.chars_per_token <= 0:
            raise ValueError(f"{self.name}: chars_per_token debe ser positivo")


@dataclass(frozen=True)
class Settings:
    scenarios: dict[str, ScenarioConfig]
    out_dir: Path
    config_path: Path


def load_settings(path: Path) -> Settings:
    """Lee el TOML y resuelve rutas relativas a la raíz del repositorio."""
    path = path.resolve()
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    base_dir = path.parent.parent
    defaults = data.get("defaults", {})
    scenarios_raw = data.get("scenarios", {})
    if not scenarios_raw:
        raise ValueError(f"{path}: no hay ninguna sección [scenarios.*]")

    scenarios: dict[str, ScenarioConfig] = {}
    for name, values in scenarios_raw.items():
        merged = {**defaults, **values}
        missing = [
            key
            for key in ("source", "max_tokens", "min_tokens", "overlap_tokens",
                        "chars_per_token", "include_section_title")
            if key not in merged
        ]
        if missing:
            raise ValueError(
                f"{path}: al escenario '{name}' le faltan claves: {', '.join(missing)}"
            )
        source = Path(merged["source"])
        if not source.is_absolute():
            source = base_dir / source
        scenarios[name] = ScenarioConfig(
            name=name,
            source=source.resolve(),
            max_tokens=int(merged["max_tokens"]),
            min_tokens=int(merged["min_tokens"]),
            overlap_tokens=int(merged["overlap_tokens"]),
            chars_per_token=float(merged["chars_per_token"]),
            include_section_title=bool(merged["include_section_title"]),
        )

    out_dir = Path(data.get("out_dir", "artifacts/chunks"))
    if not out_dir.is_absolute():
        out_dir = base_dir / out_dir
    return Settings(scenarios=scenarios, out_dir=out_dir.resolve(), config_path=path)


def chunks_path(settings: Settings, scenario: str) -> Path:
    return settings.out_dir / f"{scenario}.jsonl"
