"""Configuración del benchmark local de LLMs."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG = ROOT / "config/llms.toml"
SCENARIOS = ("boe", "debian", "debian-en")


@dataclass(frozen=True)
class LLMModelConfig:
    name: str
    model_id: str
    size_category: str
    checkpoint_dtype: str
    quantization: str
    prompt_format: str


@dataclass(frozen=True)
class LLMBenchmarkConfig:
    config_path: Path
    output_dir: Path
    embedding_config_path: Path
    scenarios: tuple[str, ...]
    top_k: int
    temperature: float
    max_tokens: int
    max_model_len: int
    gpu_memory_utilization: float
    enforce_eager: bool
    seed: int
    cost_question_count: int
    cost_repeats: int
    models: dict[str, LLMModelConfig]


def _resolve(base: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (base / path).resolve()


def load_config(path: Path = DEFAULT_CONFIG) -> LLMBenchmarkConfig:
    path = path.resolve()
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    base = path.parent.parent
    benchmark = data.get("benchmark", {})

    scenarios = tuple(str(value) for value in benchmark.get("scenarios", ["boe", "debian"]))
    if not scenarios or any(scenario not in SCENARIOS for scenario in scenarios):
        raise ValueError(
            f"benchmark.scenarios debe contener valores de: {', '.join(SCENARIOS)}"
        )
    if len(set(scenarios)) != len(scenarios):
        raise ValueError("benchmark.scenarios no puede contener valores duplicados")

    top_k = int(benchmark.get("top_k", 5))
    temperature = float(benchmark.get("temperature", 0))
    max_tokens = int(benchmark.get("max_tokens", 256))
    max_model_len = int(benchmark.get("max_model_len", 8192))
    gpu_memory_utilization = float(benchmark.get("gpu_memory_utilization", 0.9))
    enforce_eager = bool(benchmark.get("enforce_eager", False))
    seed = int(benchmark.get("seed", 42))
    cost_question_count = int(benchmark.get("cost_question_count", 5))
    cost_repeats = int(benchmark.get("cost_repeats", 3))

    if not 1 <= top_k <= 5:
        raise ValueError("benchmark.top_k debe estar entre 1 y 5")
    if temperature != 0:
        raise ValueError("benchmark.temperature debe ser 0 para una comparación justa")
    if max_tokens <= 0 or max_model_len <= max_tokens:
        raise ValueError("max_model_len debe ser mayor que max_tokens > 0")
    if not 0 < gpu_memory_utilization <= 1:
        raise ValueError("gpu_memory_utilization debe estar en el intervalo (0, 1]")
    if cost_question_count < 5:
        raise ValueError("cost_question_count debe ser al menos 5")
    if cost_repeats < 3:
        raise ValueError("cost_repeats debe ser al menos 3")

    models: dict[str, LLMModelConfig] = {}
    for name, raw in data.get("models", {}).items():
        model_id = str(raw.get("model_id", "")).strip()
        size_category = str(raw.get("size_category", ""))
        checkpoint_dtype = str(raw.get("checkpoint_dtype", ""))
        quantization = str(raw.get("quantization", ""))
        prompt_format = str(raw.get("prompt_format", ""))
        if not model_id:
            raise ValueError(f"models.{name}.model_id no puede estar vacío")
        if size_category not in {"small", "medium"}:
            raise ValueError(f"models.{name}.size_category debe ser small o medium")
        if checkpoint_dtype != "bfloat16":
            raise ValueError(f"models.{name} debe usar un checkpoint bfloat16")
        if quantization != "none":
            raise ValueError(f"models.{name} debe estar sin cuantizar")
        if prompt_format not in {"chat_template", "granite_role_markers"}:
            raise ValueError(f"models.{name}.prompt_format no válido: {prompt_format}")
        models[name] = LLMModelConfig(
            name=name,
            model_id=model_id,
            size_category=size_category,
            checkpoint_dtype=checkpoint_dtype,
            quantization=quantization,
            prompt_format=prompt_format,
        )

    if not models:
        raise ValueError(f"{path}: no hay ninguna sección [models.*]")
    for category in ("small", "medium"):
        if sum(model.size_category == category for model in models.values()) < 2:
            raise ValueError(
                f"se necesitan al menos dos modelos de tamaño {category}"
            )

    return LLMBenchmarkConfig(
        config_path=path,
        output_dir=_resolve(base, str(benchmark.get("output_dir", "artifacts/llms"))),
        embedding_config_path=_resolve(
            base,
            str(benchmark.get("embedding_config", "config/embeddings.toml")),
        ),
        scenarios=scenarios,
        top_k=top_k,
        temperature=temperature,
        max_tokens=max_tokens,
        max_model_len=max_model_len,
        gpu_memory_utilization=gpu_memory_utilization,
        enforce_eager=enforce_eager,
        seed=seed,
        cost_question_count=cost_question_count,
        cost_repeats=cost_repeats,
        models=models,
    )
