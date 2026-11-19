"""CLI del benchmark local de embeddings."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .config import DEFAULT_CONFIG, load_config
from .pipeline import run_model, write_selection_report, write_summary_csv


def configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--model", action="append", help="modelo a ejecutar; repetible")
    parser.add_argument(
        "--scenario",
        action="append",
        choices=("boe", "debian", "debian-en"),
        help="escenario a ejecutar; repetible; por defecto ambos",
    )
    parser.set_defaults(func=cmd_run)


def cmd_run(args: argparse.Namespace) -> int:
    try:
        benchmark = load_config(args.config)
        selected_models = list(dict.fromkeys(args.model or sorted(benchmark.models)))
        unknown = sorted(set(selected_models) - set(benchmark.models))
        if unknown:
            raise ValueError(
                f"modelo(s) desconocido(s): {', '.join(unknown)}. "
                f"Disponibles: {', '.join(sorted(benchmark.models))}"
            )
        scenarios = args.scenario or sorted(benchmark.chunk_hashes)
        selection_path = benchmark.output_dir / "selection.json"
        selection_path.unlink(missing_ok=True)
        (benchmark.output_dir / "summary.csv").unlink(missing_ok=True)
        summaries = []
        failures = []
        for name in selected_models:
            try:
                summaries.extend(
                    run_model(benchmark, benchmark.models[name], scenarios)
                )
            except (FileNotFoundError, RuntimeError, ValueError, OSError) as exc:
                failures.append((name, str(exc)))
                print(f"ERROR [{name}] {exc}", file=sys.stderr)

        for summary in summaries:
            print(
                f"[{summary['scenario']}] {summary['model']}: "
                f"R@1={summary['recall@1']:.3f} "
                f"R@3={summary['recall@3']:.3f} "
                f"R@5={summary['recall@5']:.3f} "
                f"MRR={summary['mrr']:.3f} "
                f"index={summary['index_size_mb']:.2f} MB "
                f"VRAM={summary['vram_peak_gb']}"
            )
        if summaries:
            write_summary_csv(benchmark.output_dir, summaries)
            print(
                "Tabla de resultados (modelos completados): "
                f"{benchmark.output_dir / 'summary.csv'}"
            )
        if (
            not failures
            and set(selected_models) == set(benchmark.models)
            and len(summaries) == len(selected_models) * len(scenarios)
        ):
            write_selection_report(benchmark.output_dir, summaries)
            print(f"Selección por escenario: {selection_path}")
        if failures:
            return 1
        return 0
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ragbench embeddings")
    configure_parser(parser)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
