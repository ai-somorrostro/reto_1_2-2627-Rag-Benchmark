"""Tests del validador de chunks."""

from __future__ import annotations

import copy
import unittest
from pathlib import Path

from reto_1_2_2627_rag_benchmark.chunking.chunker import chunk_document
from reto_1_2_2627_rag_benchmark.chunking.config import ScenarioConfig
from reto_1_2_2627_rag_benchmark.chunking.tokens import estimate_tokens
from reto_1_2_2627_rag_benchmark.chunking.validate import validate_records


def make_config() -> ScenarioConfig:
    return ScenarioConfig(
        name="boe",
        source=Path("dummy.md"),
        max_tokens=500,
        min_tokens=20,
        overlap_tokens=0,
        chars_per_token=3.6,
        include_section_title=True,
    )


class ValidateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cfg = make_config()
        document = (
            "# Estatuto\n\n"
            "##### Artículo 1. Ámbito.\n\n"
            "Texto del artículo primero con suficiente contenido.\n"
        )
        self.records, warnings = chunk_document(
            document, scenario="boe", source="dummy.md", cfg=self.cfg
        )
        self.assertFalse(warnings)

    def test_chunks_validos(self) -> None:
        report = validate_records(self.records, self.cfg)
        self.assertTrue(report.ok, report.errors)
        self.assertEqual(report.chunks, 1)

    def test_id_duplicado(self) -> None:
        report = validate_records(self.records + [copy.deepcopy(self.records[0])], self.cfg)
        self.assertFalse(report.ok)
        self.assertTrue(any("duplicado" in error for error in report.errors))

    def test_campo_obligatorio_ausente(self) -> None:
        record = copy.deepcopy(self.records[0])
        record.pop("article")
        report = validate_records([record], self.cfg)
        self.assertFalse(report.ok)
        self.assertTrue(any("article" in error for error in report.errors))

    def test_chunk_demasiado_largo(self) -> None:
        record = copy.deepcopy(self.records[0])
        record["text"] = record["text"] + "\n\n" + ("palabra " * 400)
        record["n_chars"] = len(record["text"])
        record["n_tokens_est"] = estimate_tokens(record["text"], self.cfg.chars_per_token)
        report = validate_records([record], self.cfg)
        self.assertFalse(report.ok)
        self.assertTrue(any("máximo" in error for error in report.errors))

    def test_partes_incoherentes(self) -> None:
        record = copy.deepcopy(self.records[0])
        record["id"] = record["id"].replace("-p01", "-p02")
        report = validate_records([record], self.cfg)
        self.assertFalse(report.ok)
        self.assertTrue(any("sufijo del id" in error for error in report.errors))

    def test_avisa_de_titulo_incrustado(self) -> None:
        record = copy.deepcopy(self.records[0])
        record["text"] = "# Título suelto\n\n" + record["text"]
        record["n_chars"] = len(record["text"])
        record["n_tokens_est"] = estimate_tokens(record["text"], self.cfg.chars_per_token)
        report = validate_records([record], self.cfg)
        self.assertTrue(any("'#'" in warning for warning in report.warnings))

    def test_no_avisa_de_comentario_dentro_de_codigo(self) -> None:
        record = copy.deepcopy(self.records[0])
        record["text"] = "```ini\n# Comentario de configuración\nCLAVE=valor\n```\n\n" + record["text"]
        record["n_chars"] = len(record["text"])
        record["n_tokens_est"] = estimate_tokens(record["text"], self.cfg.chars_per_token)
        report = validate_records([record], self.cfg)
        self.assertFalse(any("posible título mal parseado" in warning for warning in report.warnings))

    def test_fichero_vacio(self) -> None:
        report = validate_records([], self.cfg)
        self.assertFalse(report.ok)


if __name__ == "__main__":
    unittest.main()
