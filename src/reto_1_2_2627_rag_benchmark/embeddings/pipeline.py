"""Indexado exacto y evaluación de los golden sets congelados."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from .config import BenchmarkConfig, ModelConfig, sha256_file, verify_frozen_file
from .metrics import aggregate_metrics, query_metrics, rank_models
from .model import LocalEmbeddingModel


def _load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise ValueError(f"{path}:{line_number}: JSON inválido: {exc}") from exc
    return rows


def _model_slug(model_name: str) -> str:
    return model_name.replace("_", "-")


def _hash_strings(values: list[str]) -> str:
    digest = hashlib.sha256()
    for value in values:
        digest.update(value.encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()


def run_scenario(
    benchmark: BenchmarkConfig,
    model_config: ModelConfig,
    model: LocalEmbeddingModel,
    scenario: str,
) -> dict:
    import numpy as np

    if scenario not in benchmark.chunk_files:
        raise ValueError(f"no hay un fichero de chunks configurado para '{scenario}'")
    chunk_path = benchmark.chunk_files[scenario]
    question_path = benchmark.questions_dir / f"{scenario}.jsonl"
    verify_frozen_file(chunk_path, benchmark.chunk_hashes[scenario])
    verify_frozen_file(question_path, benchmark.question_hashes[scenario])

    chunks = _load_jsonl(chunk_path)
    questions = _load_jsonl(question_path)
    chunk_ids = [chunk["id"] for chunk in chunks]
    if len(chunk_ids) != len(set(chunk_ids)):
        raise ValueError(f"{chunk_path}: IDs de chunk duplicados")
    chunk_by_id = dict(zip(chunk_ids, chunks))
    for question in questions:
        for chunk_id in question["relevant_chunk_ids"]:
            if chunk_id not in chunk_by_id:
                raise ValueError(
                    f"{question['id']}: referencia a chunk inexistente {chunk_id}"
                )

    model.start_memory_measurement()
    started = time.perf_counter()
    vectors = model.encode(
        [chunk["text"] for chunk in chunks],
        model_config.document_prefix,
        benchmark.batch_size,
        "documents",
    )
    vectors = np.asarray(vectors, dtype=np.float32)
    if vectors.ndim != 2 or vectors.shape[0] != len(chunks):
        raise ValueError(
            f"{model_config.name}: dimensión de embeddings inesperada {vectors.shape}"
        )
    if not np.isfinite(vectors).all():
        raise ValueError(f"{model_config.name}: embeddings contienen NaN o infinito")

    index_dir = benchmark.output_dir / _model_slug(model_config.name) / scenario
    index_dir.mkdir(parents=True, exist_ok=True)
    vectors_path = index_dir / "embeddings.npy"
    np.save(vectors_path, vectors)
    index_time = time.perf_counter() - started

    query_vectors = model.encode(
        [question["question"] for question in questions],
        model_config.query_prefix,
        benchmark.batch_size,
        "queries",
    )
    if query_vectors.shape[1] != vectors.shape[1]:
        raise ValueError(f"{model_config.name}: dimensión query/documento incompatible")
    similarities = query_vectors @ vectors.T
    per_query = []
    for question, scores in zip(questions, similarities):
        order = np.argsort(-scores, kind="stable")
        ranked_ids = [chunk_ids[index] for index in order]
        relevant_ids = question["relevant_chunk_ids"]
        row = {
            "question_id": question["id"],
            "question_type": question["type"],
            "question": question["question"],
            "relevant_chunk_ids": relevant_ids,
            "ranked_chunk_ids": ranked_ids[: max(benchmark.top_k)],
            "top_scores": [float(scores[index]) for index in order[: max(benchmark.top_k)]],
            **query_metrics(ranked_ids, relevant_ids, benchmark.top_k),
        }
        per_query.append(row)

    summary = aggregate_metrics(per_query, benchmark.top_k)
    summary.update(
        {
            "scenario": scenario,
            "model": model_config.name,
            "model_id": model_config.model_id,
            "parameters_dtype": model.model_dtype,
            "parameter_count": sum(
                parameter.numel() for parameter in model.model.parameters()
            ),
            "parameters_billions": sum(
                parameter.numel() for parameter in model.model.parameters()
            ) / 1_000_000_000,
            "quantization": "none",
            "pooling": model.pooling,
            "query_prefix": model_config.query_prefix,
            "document_prefix": model_config.document_prefix,
            "max_length": model.max_length,
            "dimension": int(vectors.shape[1]),
            "chunks": len(chunks),
            "questions": len(questions),
            "index_time_seconds": index_time,
            "index_size_mb": vectors_path.stat().st_size / (1024**2),
            "vram_peak_gb": model.peak_memory_gb(),
            "vram_peak_reserved_gb": model.peak_reserved_memory_gb(),
            "device": str(model.device),
            "model_revision": model.model_revision,
            "model_path": str(model.model_path) if model.model_path else None,
            "torch_version": model.torch_version,
            "transformers_version": importlib.metadata.version("transformers"),
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "chunks_sha256": sha256_file(chunk_path),
            "questions_sha256": sha256_file(question_path),
            "texts_sha256": _hash_strings([chunk["text"] for chunk in chunks]),
            "embedding_file": str(vectors_path),
        }
    )

    with (index_dir / "results.jsonl").open("w", encoding="utf-8") as handle:
        for row in per_query:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    with (index_dir / "memory.jsonl").open("w", encoding="utf-8") as handle:
        for sample in model.memory_trace:
            handle.write(json.dumps(sample, ensure_ascii=False) + "\n")
    (index_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return summary


def write_summary_csv(output_dir: Path, summaries: list[dict]) -> None:
    import csv

    fields = (
        "scenario",
        "model",
        "parameter_count",
        "dimension",
        "recall@1",
        "recall@3",
        "recall@5",
        "mrr",
        "index_time_seconds",
        "index_size_mb",
        "vram_peak_gb",
        "parameters_dtype",
        "quantization",
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "summary.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({key: row.get(key) for key in fields} for row in summaries)


def write_selection_report(output_dir: Path, summaries: list[dict]) -> None:
    selection = {
        scenario: {
            "winner": rank_models(
                [row for row in summaries if row["scenario"] == scenario]
            )[0]["model"],
            "ranking": [
                {
                    "rank": rank,
                    "model": row["model"],
                    "recall@5": row["recall@5"],
                    "mrr": row["mrr"],
                    "vram_peak_gb": row["vram_peak_gb"],
                    "index_time_seconds": row["index_time_seconds"],
                    "index_size_mb": row["index_size_mb"],
                }
                for rank, row in enumerate(
                    rank_models(
                        [row for row in summaries if row["scenario"] == scenario]
                    ),
                    start=1,
                )
            ],
        }
        for scenario in sorted({row["scenario"] for row in summaries})
    }
    (output_dir / "selection.json").write_text(
        json.dumps(selection, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def run_model(
    benchmark: BenchmarkConfig,
    model_config: ModelConfig,
    scenarios: list[str],
) -> list[dict]:
    model = LocalEmbeddingModel(model_config, benchmark.device)
    return [
        run_scenario(benchmark, model_config, model, scenario)
        for scenario in scenarios
    ]
