#!/usr/bin/env python3
"""Author D-134 freeze evidence from a committed D-117 pack."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise import arm_readiness as readiness  # noqa: E402
from joulewise.arm_readiness import ArmReadinessError, render_json  # noqa: E402
from joulewise.arm_readiness_evidence import (  # noqa: E402
    _EVIDENCE_DIRECTORY,
    _SOURCE_DIRECTORY,
    EvidenceAuthoringError,
    author_arm_readiness_evidence,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack-root", required=True, type=Path)
    parser.add_argument(
        "--expected-confirmation-digest",
        help="out-of-band SHA-256 of the D-117 step-6 confirmation table",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        root = args.pack_root.resolve(strict=True)
        pack_repository = readiness._repo_for_pack(root).resolve(strict=True)
        cli_repository = REPO_ROOT.resolve(strict=True)
        if pack_repository != cli_repository:
            raise EvidenceAuthoringError(
                "AUTHORING_SET",
                "evidence_author_repository_mismatch",
                "pack repository differs from the evidence-author CLI repository",
            )
        result = author_arm_readiness_evidence(
            root,
            expected_confirmation_digest=args.expected_confirmation_digest,
        )
        pack_relative = root.relative_to(cli_repository).as_posix()
        source_path = f"{pack_relative}/{_SOURCE_DIRECTORY}"
        evidence_path = f"{pack_relative}/{_EVIDENCE_DIRECTORY}"
        freeze_command = (
            "python3 scripts/generate_arm_readiness.py freeze "
            f"--pack-root {pack_relative}"
        )
        # D-139: a successor pack refuses to freeze without an authenticated
        # predecessor, so the emitted sequence must carry the flag or it
        # deadlocks the operator.  The predecessor of `<family>_v<N>` is its
        # sibling `<family>_v<N-1>` under the same campaigns root; that is a
        # mechanical derivation from the pack ID, so it is done here rather
        # than typed by hand at 2am.  A first-generation pack opens the chain
        # and must NOT carry the flag.
        generation = readiness._PACK_GENERATION_RE.search(root.name)
        if generation is not None and int(generation.group(1)) > 1:
            predecessor_name = (
                f"{root.name[: generation.start()]}_v{int(generation.group(1)) - 1}"
            )
            predecessor_relative = (
                (root.parent / predecessor_name)
                .relative_to(cli_repository)
                .as_posix()
            )
            freeze_command += f" --predecessor-pack-root {predecessor_relative}"
        result["post_authoring"] = {
            "sequence": [
                f"git add -- {source_path} {evidence_path}",
                "git commit",
                "git push origin HEAD:main",
                freeze_command,
            ],
            "recovery": (
                "A reboot or HEAD change voids all twelve receipts; run "
                f"git rm -r -- {source_path} {evidence_path} before re-authoring."
            ),
        }
    except EvidenceAuthoringError as exc:
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
            "reason_codes": ["evidence_author_io_error"],
            "detail": str(exc),
        }
        code = 2
    else:
        code = 0
    sys.stdout.buffer.write(render_json(result))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
