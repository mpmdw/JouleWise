"""Phase 1 command-line helpers."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from joulewise.schemas import BenchmarkConfig, SchemaError, SummaryMetrics


def _load_config(path: Path) -> dict[str, Any]:
    if path.suffix.lower() != ".json":
        raise SchemaError("Phase 1 CLI supports JSON configs; YAML parsing is planned for Phase 2")
    return json.loads(path.read_text())


def _cmd_validate_config(args: argparse.Namespace) -> int:
    path = Path(args.path)
    config = BenchmarkConfig.from_mapping(_load_config(path))
    print(
        "valid config: "
        f"{path} target={config.hardware_target.id} "
        f"runtime={config.hardware_target.runtime_backend.value} "
        f"telemetry={config.hardware_target.telemetry_backend.value}"
    )
    return 0


def _write_or_print_schema(payload: dict[str, Any], output: str | None, label: str) -> int:
    text = json.dumps(payload, indent=2, sort_keys=True)
    if output:
        Path(output).write_text(text + "\n")
        print(f"wrote {label}: {output}")
    else:
        print(text)
    return 0


def _cmd_print_config_schema(args: argparse.Namespace) -> int:
    return _write_or_print_schema(BenchmarkConfig.json_schema(), args.output, "config schema")


def _cmd_print_output_schema(args: argparse.Namespace) -> int:
    return _write_or_print_schema(SummaryMetrics.json_schema(), args.output, "output schema")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="joulewise")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate-config", help="validate a benchmark config")
    validate.add_argument("path", help="path to a JSON benchmark config")
    validate.set_defaults(func=_cmd_validate_config)

    schema = subparsers.add_parser("print-config-schema", help="print draft config JSON Schema")
    schema.add_argument("--output", help="optional path to write schema JSON")
    schema.set_defaults(func=_cmd_print_config_schema)

    output_schema = subparsers.add_parser("print-output-schema", help="print draft summary output JSON Schema")
    output_schema.add_argument("--output", help="optional path to write schema JSON")
    output_schema.set_defaults(func=_cmd_print_output_schema)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (OSError, json.JSONDecodeError, SchemaError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
