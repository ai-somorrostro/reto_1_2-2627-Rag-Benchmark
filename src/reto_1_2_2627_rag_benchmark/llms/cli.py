"""CLI del benchmark local de LLMs."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import DEFAULT_CONFIG, load_config
from .pipeline import run_benchmark, summarize_scores


def configure_parser(parser: argparse.ArgumentParser) -> None:
    actions = parser.add_subparsers(dest="action", required=True)

    run = actions.add_parser("run", help="genera respuestas y mide coste")
    run.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    run.add_argument("--model", action="append", help="modelo de config; repetible")
    run.add_argument(
        "--scenario",
        action="append",
        choices=("boe", "debian", "debian-en"),
        help="escenario; repetible; por defecto los configurados",
    )
    run.add_argument(
        "--dry-run",
        action="store_true",
        help="valida entradas, cachés y prompts sin cargar los modelos",
    )
    run.set_defaults(func=cmd_run)

    summarize = actions.add_parser(
        "summarize", help="valida puntuaciones manuales y crea tablas CSV"
    )
    summarize.add_argument("run_dir", type=Path)
    summarize.set_defaults(func=cmd_summarize)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ragbench llms")
    configure_parser(parser)
    return parser


def cmd_run(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    run_dir = run_benchmark(
        config,
        selected_models=args.model,
        selected_scenarios=args.scenario,
        dry_run=args.dry_run,
    )
    if run_dir is not None:
        print(f"Resultados brutos y plantilla de puntuación: {run_dir}")
        print(f"Cuando termines de puntuar, ejecuta: ragbench llms summarize {run_dir}")
    return 0


def cmd_summarize(args: argparse.Namespace) -> int:
    quality_path, combined_path = summarize_scores(args.run_dir)
    print(f"Calidad: {quality_path}")
    print(f"Resumen combinado: {combined_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (FileNotFoundError, OSError, RuntimeError, ValueError) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
