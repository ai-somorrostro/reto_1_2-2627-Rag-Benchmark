"""Pruebas de métricas para retrieval de una o varias evidencias."""

from __future__ import annotations

import unittest

from reto_1_2_2627_rag_benchmark.embeddings.config import (
    DEFAULT_CONFIG,
    load_config,
    verify_frozen_file,
)
from reto_1_2_2627_rag_benchmark.embeddings.metrics import (
    aggregate_metrics,
    query_metrics,
    rank_models,
)


class EmbeddingMetricsTests(unittest.TestCase):
    def test_config_uses_the_three_fixed_local_models(self) -> None:
        benchmark = load_config(DEFAULT_CONFIG)
        self.assertEqual(
            set(benchmark.models),
            {
                "snowflake_arctic_embed_l_v2_0",
                "nemotron_3_5_embed_1b_bf16",
                "hs_embed_1",
            },
        )
        self.assertEqual(benchmark.top_k, (1, 3, 5))

    def test_frozen_chunk_hash_matches_phase_one(self) -> None:
        benchmark = load_config(DEFAULT_CONFIG)
        verify_frozen_file(
            benchmark.chunks_dir / "boe.jsonl",
            benchmark.chunk_hashes["boe"],
        )

    def test_multi_fragment_recall_requires_all_evidence_and_mrr_uses_first(self) -> None:
        metrics = query_metrics(
            ["irrelevant", "evidence-a", "evidence-b"],
            ["evidence-a", "evidence-b"],
            [1, 3],
        )
        self.assertEqual(metrics["recall@1"], 0.0)
        self.assertEqual(metrics["recall@3"], 1.0)
        self.assertEqual(metrics["fragment_recall@1"], 0.0)
        self.assertEqual(metrics["fragment_recall@3"], 1.0)
        self.assertAlmostEqual(metrics["mrr"], 0.5)

    def test_unanswerable_questions_are_excluded_from_aggregate(self) -> None:
        aggregate = aggregate_metrics(
            [
                query_metrics(["target"], ["target"], [1]),
                query_metrics(["anything"], [], [1]),
            ],
            [1],
        )
        self.assertEqual(aggregate["answerable_questions"], 1)
        self.assertEqual(aggregate["recall@1"], 1.0)
        self.assertEqual(aggregate["mrr"], 1.0)

    def test_missing_relevant_chunk_is_zero_not_a_false_positive(self) -> None:
        metrics = query_metrics(["other"], ["missing"], [1, 3])
        self.assertEqual(metrics["recall@1"], 0.0)
        self.assertEqual(metrics["recall@3"], 0.0)
        self.assertEqual(metrics["mrr"], 0.0)

    def test_no_answer_query_has_no_retrieval_metric(self) -> None:
        metrics = query_metrics(["chunk"], [], [1, 3])
        self.assertIsNone(metrics["recall@1"])
        self.assertIsNone(metrics["mrr"])

    def test_ranking_uses_recall_then_mrr_then_cost(self) -> None:
        rows = [
            {
                "model": "costly",
                "recall@5": 0.9,
                "mrr": 0.8,
                "vram_peak_gb": 5.0,
                "index_time_seconds": 4.0,
                "index_size_mb": 10.0,
            },
            {
                "model": "best",
                "recall@5": 0.9,
                "mrr": 0.9,
                "vram_peak_gb": 6.0,
                "index_time_seconds": 4.0,
                "index_size_mb": 10.0,
            },
            {
                "model": "cheapest",
                "recall@5": 0.9,
                "mrr": 0.8,
                "vram_peak_gb": 3.0,
                "index_time_seconds": 5.0,
                "index_size_mb": 10.0,
            },
        ]
        self.assertEqual(
            [row["model"] for row in rank_models(rows)],
            ["best", "cheapest", "costly"],
        )


if __name__ == "__main__":
    unittest.main()
