"""Command-line interface over the shared CT-FFR Python API."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .explain import explain
from .inference import ValidationError, format_report, predict
from .io import read_table, validate, write_results
from .plotting import contribution_figure


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ctffr", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "predict", "explain"):
        command = commands.add_parser(name)
        command.add_argument("--input", required=True, type=Path)
        if name in {"predict", "explain"}:
            command.add_argument("--output", required=True, type=Path)
        if name == "explain":
            command.add_argument("--case-id", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run a CLI command and return 0 on success or 1 on data failure."""
    args = _parser().parse_args(argv)
    try:
        raw = read_table(args.input, args.input.name)
        if args.command == "validate":
            report = validate(raw)
            print(format_report(report))
            return 1 if report.blocking else 0
        if args.command == "predict":
            write_results(predict(raw), args.output)
            print(f"Wrote predictions to {args.output}.")
            return 0
        result = explain(raw, args.case_id)
        contribution_figure(result, args.output)
        contributions = args.output.with_name(f"{args.output.stem}_contributions.csv")
        result.contributions.to_csv(contributions, index=False)
        print(f"Wrote explanation to {args.output.with_suffix('.png')} and {args.output.with_suffix('.svg')}.")
        return 0
    except (ValidationError, ValueError, KeyError, OSError) as error:
        print(str(error).strip("'"))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

