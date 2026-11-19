"""Tests del troceador: límites, solape, código y metadatos."""

from __future__ import annotations

import unittest
from pathlib import Path

from reto_1_2_2627_rag_benchmark.chunking.chunker import chunk_document
from reto_1_2_2627_rag_benchmark.chunking.config import ScenarioConfig


def make_config(**overrides) -> ScenarioConfig:
    values = {
        "name": "boe",
        "source": Path("dummy.md"),
        "max_tokens": 200,
        "min_tokens": 20,
        "overlap_tokens": 0,
        "chars_per_token": 3.6,
        "include_section_title": True,
    }
    values.update(overrides)
    return ScenarioConfig(**values)


def chunk(document: str, **overrides) -> list[dict]:
    cfg = make_config(**overrides)
    records, warnings = chunk_document(
        document, scenario=cfg.name, source="dummy.md", cfg=cfg
    )
    assert not warnings, warnings
    return records


class ChunkingTests(unittest.TestCase):
    def test_asigna_articulo_y_ruta_de_titulos(self) -> None:
        document = (
            "# Estatuto\n\n"
            "#### TÍTULO I\n\n"
            "#### Sección 1.ª\n\n"
            "##### Artículo 1. Ámbito de aplicación.\n\n"
            "Texto del artículo primero.\n"
        )
        records = chunk(document)
        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record["id"], "boe-art1-p01")
        self.assertEqual(record["article"], "1")
        self.assertEqual(record["section"], "Artículo 1. Ámbito de aplicación.")
        self.assertIn("Estatuto", record["section_path"])
        self.assertIn("Artículo 1. Ámbito de aplicación.", record["section_path"])
        self.assertTrue(record["text"].startswith("Artículo 1"))

    def test_articulo_unico(self) -> None:
        document = (
            "##### Artículo único. Aprobación del texto refundido.\n\n"
            "Se aprueba el texto refundido.\n"
        )
        records = chunk(document)
        self.assertEqual(records[0]["article"], "único")
        self.assertEqual(records[0]["id"], "boe-artunico-p01")

    def test_parte_articulos_largos_respetando_el_limite(self) -> None:
        paragraph = "Este es un párrafo suficientemente largo para ocupar espacio. " * 3
        body = "\n\n".join(f"{number}. {paragraph}" for number in range(1, 13))
        document = f"##### Artículo 2. Artículo largo.\n\n{body}\n"
        records = chunk(document, max_tokens=100, overlap_tokens=0)

        self.assertGreater(len(records), 1)
        self.assertEqual({record["article"] for record in records}, {"2"})
        self.assertEqual(
            {record["n_parts"] for record in records}, {len(records)}
        )
        for record in records:
            self.assertLessEqual(record["n_tokens_est"], 100)
            self.assertTrue(record["text"].startswith("Artículo 2"))
        ids = [record["id"] for record in records]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(record_id.endswith(f"-p{index:02d}") for index, record_id in enumerate(ids, start=1)))

    def test_solape_entre_partes(self) -> None:
        paragraph = "Frase de relleno para comprobar el solape. " * 2
        body = "\n\n".join(f"{number}. {paragraph}" for number in range(1, 13))
        document = f"##### Artículo 3. Solape.\n\n{body}\n"
        records = chunk(document, max_tokens=100, overlap_tokens=50)

        self.assertGreater(len(records), 1)
        previous = records[0]["text"].split("\n\n")[1:]
        for record in records[1:]:
            current = record["text"].split("\n\n")[1:]
            shared = [line for line in current if line and line in previous]
            self.assertTrue(shared, "no hay solape entre partes consecutivas")
            previous = current

    def test_conserva_bloques_de_codigo(self) -> None:
        document = (
            "# 1.1. Instalación\n\n"
            "Antes de instalar:\n\n"
            "```bash\n"
            "apt update\n"
            "apt install paquete\n"
            "```\n\n"
            "Después, reinicie.\n"
        )
        records = chunk(document, max_tokens=300)
        self.assertEqual(len(records), 1)
        text = records[0]["text"]
        self.assertIn("```bash", text)
        self.assertIn("apt install paquete", text)
        self.assertEqual(text.count("```"), 2)

    def test_parte_codigo_desmesurado_sin_romper_fences(self) -> None:
        lines = "\n".join(f"linea-de-codigo-muy-larga-{number}" for number in range(60))
        document = f"# 1.1. Código\n\n```bash\n{lines}\n```\n"
        records = chunk(document, max_tokens=80)
        self.assertGreater(len(records), 1)
        for record in records:
            lines_in_text = [
                line
                for line in record["text"].splitlines()
                if line.strip().startswith("```")
            ]
            self.assertEqual(len(lines_in_text), 2)
            self.assertLessEqual(record["n_tokens_est"], 80)

    def test_ids_deterministas(self) -> None:
        document = "# 1.1. Sección\n\nTexto de la sección.\n"
        first = chunk(document)
        second = chunk(document)
        self.assertEqual(
            [record["id"] for record in first], [record["id"] for record in second]
        )

    def test_no_duplica_el_titulo_si_ya_esta_en_el_cuerpo(self) -> None:
        document = (
            "##### Artículo 4. Título.\n\n"
            "Artículo 4. Título.\n\n"
            "Cuerpo del artículo.\n"
        )
        records = chunk(document)
        self.assertEqual(records[0]["text"].count("Artículo 4. Título."), 1)

    def test_contenido_antes_del_primer_titulo(self) -> None:
        document = "Texto de portada.\n\n# Documento\n\nCuerpo.\n"
        records = chunk(document)
        self.assertEqual(records[0]["id"], "boe-doc-p01")
        self.assertEqual(records[0]["article"], None)

    def test_numeracion_debian_en_ids(self) -> None:
        document = (
            "# 1.1. ¿Qué es Debian?\n\n"
            "Debian es una distribución.\n\n"
            "## 1.1.1. Multiplataforma\n\n"
            "Soporta varias arquitecturas.\n"
        )
        records = chunk(document, name="debian")
        self.assertEqual(
            [record["id"] for record in records],
            ["debian-1-1-p01", "debian-1-1-1-p01"],
        )


if __name__ == "__main__":
    unittest.main()
