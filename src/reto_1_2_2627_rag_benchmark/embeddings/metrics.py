"""Métricas de recuperación para preguntas con una o varias evidencias."""

from __future__ import annotations

from collections.abc import Sequence


def query_metrics(
    ranked_ids: Sequence[str],
    relevant_ids: Sequence[str],
    top_k: Sequence[int],
) -> dict[str, float | int | None]:
    """Calcula Recall@k como acierto completo de pregunta y el MRR del primer acierto."""
    if not relevant_ids:
        return {
            **{f"recall@{k}": None for k in top_k},
            "mrr": None,
            **{f"fragment_recall@{k}": None for k in top_k},
        }

    relevant = set(relevant_ids)
    positions = {
        chunk_id: index
        for index, chunk_id in enumerate(ranked_ids, start=1)
        if chunk_id in relevant
    }
    first_position = min(positions.values(), default=None)
    metrics: dict[str, float | int | None] = {
        "mrr": 1 / first_position if first_position is not None else 0.0
    }
    for k in top_k:
        hits = relevant.intersection(ranked_ids[:k])
        metrics[f"recall@{k}"] = float(len(hits) == len(relevant))
        metrics[f"fragment_recall@{k}"] = len(hits) / len(relevant)
    return metrics


def aggregate_metrics(
    per_query: Sequence[dict[str, float | int | None]],
    top_k: Sequence[int],
) -> dict[str, float | int]:
    """Promedia solo consultas respondibles; deja aparte el recall por fragmento."""
    answerable = [row for row in per_query if row["mrr"] is not None]
    if not answerable:
        raise ValueError("no hay preguntas respondibles para calcular métricas")
    result: dict[str, float | int] = {"answerable_questions": len(answerable)}
    for metric in ("mrr", *(f"recall@{k}" for k in top_k)):
        result[metric] = sum(float(row[metric]) for row in answerable) / len(answerable)
    for k in top_k:
        result[f"fragment_recall@{k}"] = (
            sum(float(row[f"fragment_recall@{k}"]) for row in answerable)
            / len(answerable)
        )
    return result


def rank_models(candidates: Sequence[dict]) -> list[dict]:
    """Aplica el criterio de Fase 2: R@5, MRR y después coste."""
    return sorted(
        candidates,
        key=lambda row: (
            -float(row["recall@5"]),
            -float(row["mrr"]),
            float("inf") if row["vram_peak_gb"] is None else row["vram_peak_gb"],
            row["index_time_seconds"],
            row["index_size_mb"],
        ),
    )
