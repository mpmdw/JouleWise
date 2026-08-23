#!/usr/bin/env python3
"""Build the custody-external D-117 v4 family-publication marker."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise import arm_readiness as readiness  # noqa: E402


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--pack-root", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    consumer = Path(__file__).with_name("verify_family_marker.py")
    try:
        result = readiness.build_family_publication_marker(
            args.repository,
            args.head,
            args.pack_root,
            args.output,
            builder_tool=Path(__file__),
            consumer_tool=consumer,
        )
    except readiness.FamilyPublicationError as exc:
        result = {
            "schema_version": "joulewise.d117_family_publication_build.v1",
            "status": "REFUSE",
            "reason_codes": ["readiness_r1_family_publication"],
            "check_id": exc.check_id,
            "detail": str(exc),
        }
        sys.stdout.buffer.write(readiness.render_json(result))
        return 2
    except (OSError, readiness.ArmReadinessError) as exc:
        result = {
            "schema_version": "joulewise.d117_family_publication_build.v1",
            "status": "REFUSE",
            "reason_codes": ["readiness_row_registry_mismatch"],
            "check_id": "registry_mismatch",
            "detail": str(exc),
        }
        sys.stdout.buffer.write(readiness.render_json(result))
        return 2
    sys.stdout.buffer.write(readiness.render_json(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
