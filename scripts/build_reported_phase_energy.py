#!/usr/bin/env python3
"""Build one content-addressed D-123 reported phase-energy artifact."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.reported_phase_energy import (  # noqa: E402
    StopFill,
    build_reported_phase_energy,
    build_reported_phase_energy_source,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "source",
        type=Path,
        help=(
            "authenticated joulewise.reported_phase_energy_source.v1 JSON, or "
            "source material with --produce-source"
        ),
    )
    parser.add_argument(
        "--produce-source",
        action="store_true",
        help="produce and validate the governed source projection",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="create the artifact here; canonical JSON is written to stdout if omitted",
    )
    return parser


def _read(path: Path) -> bytes:
    try:
        return path.read_bytes()
    except OSError as exc:
        raise StopFill(f"source_unreadable:{exc}") from exc


def _render(artifact: dict) -> bytes:
    return (json.dumps(artifact, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        document = (
            build_reported_phase_energy_source(_read(args.source))
            if args.produce_source
            else build_reported_phase_energy(_read(args.source))
        )
        rendered = _render(document)
        if args.output is None:
            sys.stdout.buffer.write(rendered)
        else:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            try:
                with args.output.open("xb") as handle:
                    handle.write(rendered)
            except FileExistsError as exc:
                raise StopFill(f"output_exists:{args.output}") from exc
    except (OSError, StopFill, TypeError, ValueError) as exc:
        print(f"reported_phase_energy_STOP_FILL: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
