from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from reto_1_2_2627_rag_benchmark.llms.config import DEFAULT_CONFIG, load_config
from reto_1_2_2627_rag_benchmark.llms.pipeline import (
    SYSTEM_PROMPT,
    _cost_questions,
    _cost_summary,
    _mark_failed_on_error,
    load_scenario_inputs,
    render_prompt,
    summarize_scores,
)


class FakeTokenizer:
    chat_template = "present"
    eos_token = "<|end_of_text|>"

    def apply_chat_template(self, messages, tokenize, add_generation_prompt):
        self.messages = messages
        self.generation_prompt = add_generation_prompt
        return "rendered chat"

    def get_vocab(self):
        return {"<|start_of_role|>": 1, "<|end_of_role|>": 2}


class LLMBenchmarkTests(unittest.TestCase):
    def test_config_has_two_small_and_two_medium_bf16_models(self) -> None:
        config = load_config(DEFAULT_CONFIG)
        small = [model for model in config.models.values() if model.size_category == "small"]
        medium = [model for model in config.models.values() if model.size_category == "medium"]
        self.assertEqual(len(small), 2)
        self.assertEqual(len(medium), 2)
        self.assertEqual(config.top_k, 5)
        self.assertEqual(config.temperature, 0)
        self.assertEqual(config.max_model_len, 3072)
        self.assertTrue(config.enforce_eager)
        self.assertEqual(config.cost_question_count, 5)
        self.assertEqual(config.cost_repeats, 3)

    def test_scenario_inputs_use_selected_embedding_and_top_five(self) -> None:
        config = load_config(DEFAULT_CONFIG)
        scenario = load_scenario_inputs(config, "boe")
        self.assertEqual(scenario.embedding_model, "nemotron_3_5_embed_1b_bf16")
        self.assertEqual(len(scenario.questions), 15)
        question = scenario.questions[0]
        result = scenario.retrieval_by_question[question["id"]]
        self.assertEqual(len(result["ranked_chunk_ids"][: config.top_k]), 5)
        self.assertTrue(
            all(
                chunk_id in scenario.chunk_by_id
                for chunk_id in result["ranked_chunk_ids"][: config.top_k]
            )
        )

    def test_optional_english_scenario_uses_its_own_frozen_retrieval(self) -> None:
        scenario = load_scenario_inputs(load_config(DEFAULT_CONFIG), "debian-en")
        self.assertEqual(scenario.scenario, "debian-en")
        self.assertEqual(len(scenario.questions), 15)
        self.assertEqual(scenario.embedding_model, "nemotron_3_5_embed_1b_bf16")

    def test_prompt_formats_preserve_shared_instructions_and_context(self) -> None:
        config = load_config(DEFAULT_CONFIG)
        tokenizer = FakeTokenizer()
        qwen = config.models["qwen2_5_3b_instruct"]
        self.assertEqual(
            render_prompt(
                tokenizer,
                qwen,
                "¿Cuál es la respuesta?",
                [{"id": "chunk-1", "section": "Artículo 6", "text": "Texto."}],
            ),
            "rendered chat",
        )
        self.assertEqual(tokenizer.messages[0]["content"], SYSTEM_PROMPT)
        self.assertIn("[chunk-1] Artículo 6", tokenizer.messages[1]["content"])
        self.assertTrue(tokenizer.generation_prompt)

        granite = config.models["granite_4_1_8b_llmon_preview"]
        prompt = render_prompt(
            tokenizer,
            granite,
            "¿Cuál es la respuesta?",
            [{"id": "chunk-1", "section": "Artículo 6", "text": "Texto."}],
        )
        self.assertIn("<|start_of_role|>system<|end_of_role|>", prompt)
        self.assertIn("<|start_of_role|>assistant<|end_of_role|>", prompt)
        self.assertIn(SYSTEM_PROMPT, prompt)
        self.assertIn("[chunk-1] Artículo 6", prompt)

    def test_cost_question_sample_covers_all_types(self) -> None:
        questions = [
            {"id": "d1", "type": "direct"},
            {"id": "d2", "type": "direct"},
            {"id": "m1", "type": "multi_fragment"},
            {"id": "n1", "type": "no_answer"},
            {"id": "d3", "type": "direct"},
            {"id": "m2", "type": "multi_fragment"},
        ]
        selected = _cost_questions(questions, 5)
        self.assertEqual(
            [row["id"] for row in selected], ["d1", "m1", "n1", "d2", "d3"]
        )

    def test_cost_summary_uses_medians_and_excludes_warmup(self) -> None:
        rows = [
            {
                "kind": "measurement",
                "model": "qwen",
                "model_id": "Qwen/Qwen2.5-3B-Instruct",
                "size_category": "small",
                "checkpoint_parameters_billions": 3.086,
                "checkpoint_dtype": "bfloat16",
                "quantization": "none",
                "scenario": "boe",
                "question_id": "q1",
                "repetition": repetition,
                "ttft_seconds": value,
                "tokens_per_second": value * 10,
                "latency_seconds": value * 2,
            }
            for repetition, value in enumerate((1.0, 3.0, 2.0), 1)
        ]
        rows.append(
            {
                **rows[0],
                "kind": "warmup",
                "question_id": "warmup",
                "ttft_seconds": 100.0,
            }
        )
        memory = [
            {
                "model": "qwen",
                "peak_allocated_bytes": 1_000,
                "peak_reserved_bytes": 2_000,
                "device_used_bytes": 3_000,
            }
        ]
        summary = _cost_summary(rows, memory, repeats=3)[0]
        self.assertEqual(summary["ttft_seconds"], 2.0)
        self.assertEqual(summary["tokens_per_second"], 20.0)
        self.assertEqual(summary["latency_seconds"], 4.0)
        self.assertEqual(summary["cost_questions"], 1)

    def test_failed_run_is_marked_in_its_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest_path = Path(temp_dir) / "manifest.json"
            manifest = {"status": "running", "active_model": "granite"}
            with self.assertRaisesRegex(RuntimeError, "no KV cache"):
                with _mark_failed_on_error(manifest, manifest_path):
                    raise RuntimeError("no KV cache")
            saved = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["status"], "failed")
            self.assertEqual(saved["failed_model"], "granite")
            self.assertNotIn("active_model", saved)

    def test_manual_scores_generate_quality_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir)
            (run_dir / "manifest.json").write_text(
                json.dumps({"status": "completed"}), encoding="utf-8"
            )
            response_rows = []
            score_rows = []
            for index in range(15):
                question_type = "no_answer" if index >= 12 else "direct"
                response_id = f"qwen:boe:{index}"
                response_rows.append(
                    {
                        "response_id": response_id,
                        "model": "qwen",
                        "model_id": "Qwen/Qwen2.5-3B-Instruct",
                        "size_category": "small",
                        "checkpoint_parameters_billions": 3.086,
                        "checkpoint_dtype": "bfloat16",
                        "quantization": "none",
                        "scenario": "boe",
                        "question_id": str(index),
                        "question_type": question_type,
                    }
                )
                score_rows.append(
                    {
                        "response_id": response_id,
                        "model": "qwen",
                        "model_id": "Qwen/Qwen2.5-3B-Instruct",
                        "size_category": "small",
                        "checkpoint_parameters_billions": 3.086,
                        "checkpoint_dtype": "bfloat16",
                        "quantization": "none",
                        "scenario": "boe",
                        "question_id": str(index),
                        "correctness_score": 2,
                        "faithful": True,
                        "abstention": question_type == "no_answer",
                        "format_language": True,
                    }
                )
            for name, rows in (
                ("responses.jsonl", response_rows),
                ("scores.jsonl", score_rows),
            ):
                (run_dir / name).write_text(
                    "".join(json.dumps(row) + "\n" for row in rows),
                    encoding="utf-8",
                )

            quality_path, combined_path = summarize_scores(run_dir)
            with quality_path.open(encoding="utf-8", newline="") as handle:
                row = next(csv.DictReader(handle))
            self.assertEqual(row["correctness_mean_0_2"], "2")
            self.assertEqual(row["faithful_percent"], "100.0")
            self.assertEqual(row["correct_abstentions_of_3"], "3")
            self.assertEqual(row["false_abstentions"], "0")
            self.assertTrue(combined_path.is_file())


if __name__ == "__main__":
    unittest.main()
