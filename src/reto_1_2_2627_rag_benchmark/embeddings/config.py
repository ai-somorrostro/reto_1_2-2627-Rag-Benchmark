"""Configuración y entradas congeladas de la Fase 2."""

from __future__ import annotations

import hashlib
import tomllib
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG = ROOT / "config/embeddings.toml"


@dataclass(frozen=True)
class ModelConfig:
    name: str
    model_id: str
    input_mode: str
    pooling: str
    query_prefix: str
    document_prefix: str
    max_length: int


@dataclass(frozen=True)
class BenchmarkConfig:
    chunks_dir: Path
    chunk_files: dict[str, Path]
    questions_dir: Path
    output_dir: Path
    device: str
    batch_size: int
    top_k: tuple[int, ...]
    chunk_hashes: dict[str, str]
    question_hashes: dict[str, str]
    models: dict[str, ModelConfig]


def _resolve(base: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (base / path).resolve()


def load_config(path: Path = DEFAULT_CONFIG) -> BenchmarkConfig:
    path = path.resolve()
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    base = path.parent.parent
    benchmark = data.get("benchmark", {})
    frozen = data.get("frozen_inputs", {})

    top_k = tuple(int(k) for k in benchmark.get("top_k", [1, 3, 5]))
    if not top_k or any(k <= 0 for k in top_k) or tuple(sorted(set(top_k))) != top_k:
        raise ValueError(
            "benchmark.top_k debe ser una lista creciente de enteros positivos"
        )

    batch_size = int(benchmark.get("batch_size", 16))
    if batch_size <= 0:
        raise ValueError("benchmark.batch_size debe ser positivo")

    models: dict[str, ModelConfig] = {}
    for name, raw in data.get("models", {}).items():
        model_id = str(raw["model_id"]).strip()
        input_mode = str(raw.get("input_mode", "tokenizer"))
        pooling = str(raw.get("pooling", "auto"))
        max_length = int(raw.get("max_length", 0))
        if not model_id:
            raise ValueError(f"models.{name}.model_id no puede estar vacío")
        if input_mode not in {"tokenizer", "chat_template"}:
            raise ValueError(f"models.{name}.input_mode no válido: {input_mode}")
        if pooling not in {"auto", "cls", "mean"}:
            raise ValueError(f"models.{name}.pooling no válido: {pooling}")
        if max_length < 0:
            raise ValueError(f"models.{name}.max_length no puede ser negativo")
        models[name] = ModelConfig(
            name=name,
            model_id=model_id,
            input_mode=input_mode,
            pooling=pooling,
            query_prefix=str(raw.get("query_prefix", "")),
            document_prefix=str(raw.get("document_prefix", "")),
            max_length=max_length,
        )
    if not models:
        raise ValueError(f"{path}: no hay ninguna sección [models.*]")

    chunk_hashes = frozen.get("chunks_sha256", {})
    question_hashes = frozen.get("questions_sha256", {})
    if (
        not {"boe", "debian"}.issubset(chunk_hashes)
        or set(chunk_hashes) != set(question_hashes)
    ):
        raise ValueError(
            "frozen_inputs debe incluir hashes de chunks y preguntas para todos "
            "los escenarios y conservar boe y debian"
        )

    chunks_dir = _resolve(base, benchmark.get("chunks_dir", "artifacts/chunks"))
    chunk_files = {
        name: chunks_dir / f"{name}.jsonl" for name in chunk_hashes
    }
    chunk_files.update(
        {
            name: _resolve(base, value)
            for name, value in benchmark.get("chunk_files", {}).items()
        }
    )
    if set(chunk_files) != set(chunk_hashes):
        raise ValueError("benchmark.chunk_files debe corresponder a los escenarios congelados")

    return BenchmarkConfig(
        chunks_dir=chunks_dir,
        chunk_files=chunk_files,
        questions_dir=_resolve(base, benchmark.get("questions_dir", "data/golden_set")),
        output_dir=_resolve(base, benchmark.get("output_dir", "artifacts/embeddings")),
        device=str(benchmark.get("device", "auto")),
        batch_size=batch_size,
        top_k=top_k,
        chunk_hashes={key: str(value) for key, value in chunk_hashes.items()},
        question_hashes={key: str(value) for key, value in question_hashes.items()},
        models=models,
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_frozen_file(path: Path, expected_sha256: str) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"falta una entrada congelada de Fase 1: {path}")
    actual = sha256_file(path)
    if actual != expected_sha256:
        raise ValueError(
            f"hash distinto para {path}: esperado {expected_sha256}, obtenido {actual}"
        )
