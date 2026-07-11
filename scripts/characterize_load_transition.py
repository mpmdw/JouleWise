#!/usr/bin/env python3
"""Build a PROVISIONAL P2-046 load-transition alignment artifact.

This is an offline analyzer.  It does not invoke powermetrics or generate
load; real-Mac execution is reserved for the lead-controlled P2-046B lane.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.load_transition_alignment import (  # noqa: E402
    AlignmentRefusal,
    build_alignment_artifact,
    write_artifact_atomic,
)


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number {value!r} is forbidden")


def _load_json(path: Path, label: str) -> tuple[dict[str, Any], str]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"), parse_constant=_reject_constant)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise AlignmentRefusal(f"{label}_unreadable", f"{path}: {exc}") from exc
    if not isinstance(value, dict):
        raise AlignmentRefusal(f"{label}_unreadable", f"{path}: top level must be an object")
    return value, hashlib.sha256(raw).hexdigest()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze frozen P2-046 marker/sample observations (fixture-only in Part A)."
    )
    parser.add_argument("--manifest", type=Path, required=True, help="frozen P2-046 manifest JSON")
    parser.add_argument("--observations", type=Path, required=True, help="frozen observations JSON")
    parser.add_argument("--output", type=Path, required=True, help="artifact output JSON")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        manifest, manifest_sha256 = _load_json(args.manifest, "manifest")
        observations, observations_sha256 = _load_json(args.observations, "observations")
        artifact = build_alignment_artifact(
            manifest,
            observations,
            manifest_sha256=manifest_sha256,
            observations_sha256=observations_sha256,
        )
        write_artifact_atomic(args.output, artifact)
    except AlignmentRefusal as exc:
        print(
            f"characterize_load_transition: REFUSED[{exc.reason_code}]: {exc}",
            file=sys.stderr,
        )
        return 2
    except OSError as exc:
        print(f"characterize_load_transition: ERROR: {exc}", file=sys.stderr)
        return 1
    print(
        f"characterize_load_transition: wrote {args.output} "
        f"({artifact['evidence_status']}; {artifact['claim_disposition']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
