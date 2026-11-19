"""Tests de estructura y trazabilidad del golden set."""

from __future__ import annotations

import json
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_COUNTS = Counter(
    {"direct": 8, "multi_fragment": 4, "no_answer": 3}
)
EXPECTED_REFERENCES = {"direct": 1, "multi_fragment": 2, "no_answer": 0}
REQUIRED_FIELDS = {
    "id",
    "scenario",
    "type",
    "question",
    "expected_answer",
    "relevant_chunk_ids",
}
SCENARIO_CHUNKS = {
    "boe": ROOT / "artifacts/chunks/boe.jsonl",
    "debian": ROOT / "artifacts/chunks/debian.jsonl",
    "debian-en": ROOT / "artifacts/chunks-english/debian-en.jsonl",
}


class GoldenSetTests(unittest.TestCase):
    def test_scenarios_have_required_question_mix_and_valid_chunk_references(self) -> None:
        question_ids: set[str] = set()

        for scenario, chunk_path in SCENARIO_CHUNKS.items():
            with self.subTest(scenario=scenario):
                questions = [
                    json.loads(line)
                    for line in (ROOT / "data/golden_set" / f"{scenario}.jsonl")
                    .read_text(encoding="utf-8")
                    .splitlines()
                    if line.strip()
                ]
                chunk_rows = [
                    json.loads(line)
                    for line in chunk_path.read_text(encoding="utf-8").splitlines()
                    if line.strip()
                ]
                chunks = {row["id"]: row for row in chunk_rows}

                self.assertEqual(len(questions), 15)
                self.assertEqual(
                    Counter(question["type"] for question in questions),
                    EXPECTED_COUNTS,
                )

                for question in questions:
                    self.assertEqual(set(question), REQUIRED_FIELDS)
                    self.assertEqual(question["scenario"], scenario)
                    self.assertTrue(question["question"].strip())
                    self.assertTrue(question["expected_answer"].strip())
                    self.assertNotIn(question["id"], question_ids)
                    question_ids.add(question["id"])

                    references = question["relevant_chunk_ids"]
                    self.assertEqual(
                        len(references),
                        EXPECTED_REFERENCES[question["type"]],
                    )
                    if question["type"] == "no_answer":
                        self.assertIn("no aparece", question["expected_answer"].lower())

                    for chunk_id in references:
                        self.assertIn(chunk_id, chunks)
                        self.assertEqual(chunks[chunk_id]["scenario"], scenario)

    def test_english_golden_set_reuses_spanish_queries_and_answers(self) -> None:
        def read_questions(scenario: str) -> list[dict]:
            return [
                json.loads(line)
                for line in (ROOT / "data/golden_set" / f"{scenario}.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
                if line.strip()
            ]

        spanish = read_questions("debian")
        english = read_questions("debian-en")
        self.assertEqual(
            [
                (row["type"], row["question"], row["expected_answer"])
                for row in spanish
            ],
            [
                (row["type"], row["question"], row["expected_answer"])
                for row in english
            ],
        )


if __name__ == "__main__":
    unittest.main()
