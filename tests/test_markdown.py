"""Tests del lector de markdown."""

from __future__ import annotations

import unittest

from reto_1_2_2627_rag_benchmark.chunking.markdown import (
    KIND_CODE,
    KIND_HEADING,
    KIND_TEXT,
    parse_markdown,
)


class ParseMarkdownTests(unittest.TestCase):
    def test_separa_titulos_parrafos_y_codigo(self) -> None:
        document = (
            "# Documento\n\n"
            "Intro.\n\n"
            "## Sección 1.1\n\n"
            "Texto de la sección.\n\n"
            "```bash\n"
            "apt update\n"
            "apt install foo\n"
            "```\n"
        )
        parsed = parse_markdown(document)
        kinds = [block.kind for block in parsed.blocks]
        self.assertEqual(
            kinds, [KIND_HEADING, KIND_TEXT, KIND_HEADING, KIND_TEXT, KIND_CODE]
        )
        self.assertEqual(parsed.blocks[2].level, 2)
        self.assertEqual(parsed.blocks[4].lang, "bash")
        self.assertIn("apt install foo", parsed.blocks[4].text)
        self.assertFalse(parsed.warnings)

    def test_acepta_niveles_de_titulo_mayores_de_seis(self) -> None:
        parsed = parse_markdown("######## Título profundo\n\nTexto.\n")
        self.assertEqual(parsed.blocks[0].kind, KIND_HEADING)
        self.assertEqual(parsed.blocks[0].level, 8)

    def test_avisa_de_fence_sin_cerrar(self) -> None:
        parsed = parse_markdown("# Doc\n\n```bash\napt update\n")
        self.assertTrue(any("sin cerrar" in warning for warning in parsed.warnings))
        self.assertEqual(parsed.blocks[-1].kind, KIND_CODE)

    def test_lineas_de_origen(self) -> None:
        parsed = parse_markdown("# Doc\n\nPrimer párrafo.\n\nSegundo párrafo.\n")
        self.assertEqual(parsed.blocks[0].start_line, 1)
        self.assertEqual(parsed.blocks[1].start_line, 3)
        self.assertEqual(parsed.blocks[2].start_line, 5)


if __name__ == "__main__":
    unittest.main()
