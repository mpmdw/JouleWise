#!/usr/bin/env python3
"""Author the fifteen D-134 T-0 evidence receipts in window custody."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise import arm_readiness as readiness  # noqa: E402
from joulewise.arm_readiness import ArmReadinessError, render_json  # noqa: E402
from joulewise.arm_readiness_evidence_t0 import (  # noqa: E402
    T0EvidenceAuthoringError,
    author_arm_readiness_evidence_t0,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack-root", required=True, type=Path)
    parser.add_argument("--custody-root", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        root = args.pack_root.resolve(strict=True)
        custody = args.custody_root.resolve(strict=True)
        pack_repository = readiness._repo_for_pack(root).resolve(strict=True)
        cli_repository = REPO_ROOT.resolve(strict=True)
        if pack_repository != cli_repository:
            raise T0EvidenceAuthoringError(
                "AUTHORING_SET",
                "evidence_author_t0_repository_mismatch",
                "pack repository differs from the T-0 evidence-author CLI repository",
            )
        result = author_arm_readiness_evidence_t0(root, custody)
        result["next_step"] = {
            "command": (
                "python3 scripts/generate_arm_readiness.py arm "
                f"--pack-root {root} --arm-context '<canonical JSON object>' "
                f"--window-custody-root {custody}"
            ),
            "warning": (
                "Run immediately in the same boot session; any refusal ends this "
                "arm attempt and is not an operator override point."
            ),
        }
    except T0EvidenceAuthoringError as exc:
        result = {
            "status": "REFUSE",
            "kind": exc.kind,
            "reason_codes": [exc.reason_code],
            "detail": str(exc),
        }
        code = 2
    except ArmReadinessError as exc:
        result = {
            "status": "REFUSE",
            "kind": "AUTHORING_SET",
            "reason_codes": [exc.reason_code],
            "detail": str(exc),
        }
        code = 2
    except OSError as exc:
        result = {
            "status": "REFUSE",
            "kind": "AUTHORING_SET",
            "reason_codes": ["evidence_author_t0_io_error"],
            "detail": str(exc),
        }
        code = 2
    else:
        code = 0
    sys.stdout.buffer.write(render_json(result))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
