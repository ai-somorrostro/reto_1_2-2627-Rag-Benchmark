"""CLI del pipeline de troceado.

Uso:
    ragbench chunk build --dry-run
    ragbench chunk build --scenario boe
    ragbench chunk build
    ragbench chunk validate
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import load_settings
from .pipeline import build_scenario, token_stats
from .validate import validate_scenario

DEFAULT_CONFIG = Path("config/chunking.toml")


def _selected(settings, names: list[str] | None) -> list[str]:
    if not names:
        return sorted(settings.scenarios)
    unknown = [name for name in names if name not in settings.scenarios]
    if unknown:
        raise SystemExit(
            f"escenario(s) desconocido(s): {', '.join(unknown)}. "
            f"Disponibles: {', '.join(sorted(settings.scenarios))}"
        )
    return names


def _print_stats(stats: dict, prefix: str) -> None:
    print(
        f"{prefix} {stats.get('chunks', 0)} chunks | tokens min/mediana/p95/max: "
        f"{stats.get('tokens_min', 0)}/{stats.get('tokens_median', 0)}/"
        f"{stats.get('tokens_p95', 0)}/{stats.get('tokens_max', 0)}"
    )


def cmd_build(args: argparse.Namespace) -> int:
    settings = load_settings(args.config)
    names = _selected(settings, args.scenario)
    for name in names:
        result = build_scenario(settings, name, dry_run=args.dry_run)
        _print_stats(token_stats(result.chunks), f"[{name}]")
        if result.warnings:
            print(f"  avisos del parser: {len(result.warnings)}")
            for warning in result.warnings[:5]:
                print(f"    - {warning}")
        if result.out_path:
            print(f"  -> {result.out_path}")
        else:
            print("  (dry-run: no se escribe nada)")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    settings = load_settings(args.config)
    names = _selected(settings, args.scenario)
    failed = False
    for name in names:
        report = validate_scenario(settings, name)
        _print_stats(report.stats, f"[{name}]")
        for error in report.errors:
            print(f"  ERROR {error}")
        for warning in report.warnings:
            print(f"  AVISO {warning}")
        if report.ok:
            print(f"  OK ({report.chunks} chunks)")
        else:
            failed = True
            print(f"  FALLAN {len(report.errors)} comprobaciones")
    return 1 if failed else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ragbench", description="Pipeline de benchmark RAG"
    )
    areas = parser.add_subparsers(dest="area", required=True)
    chunk = areas.add_parser("chunk", help="troceado del corpus")
    actions = chunk.add_subparsers(dest="action", required=True)

    build = actions.add_parser("build", help="genera los chunks")
    build.add_argument(
        "--config", type=Path, default=DEFAULT_CONFIG, help="ruta del TOML"
    )
    build.add_argument(
        "--scenario",
        action="append",
        help="escenario a trocear (repetible); por defecto, todos",
    )
    build.add_argument(
        "--dry-run",
        action="store_true",
        help="calcula y muestra estadísticas sin escribir ficheros",
    )
    build.set_defaults(func=cmd_build)

    validate = actions.add_parser("validate", help="valida los chunks generados")
    validate.add_argument(
        "--config", type=Path, default=DEFAULT_CONFIG, help="ruta del TOML"
    )
    validate.add_argument(
        "--scenario",
        action="append",
        help="escenario a validar (repetible); por defecto, todos",
    )
    validate.set_defaults(func=cmd_validate)

    from ..embeddings.cli import configure_parser

    embeddings = areas.add_parser(
        "embeddings", help="benchmark local de recuperación con embeddings"
    )
    configure_parser(embeddings)

    from ..llms.cli import configure_parser as configure_llms_parser

    llms = areas.add_parser("llms", help="benchmark local de generación con LLMs")
    configure_llms_parser(llms)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
