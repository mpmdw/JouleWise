#!/usr/bin/env python3
"""Verify the D-117 v4 family marker in candidate or published custody."""

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
    parser.add_argument("--marker", type=Path, required=True)
    parser.add_argument(
        "--phase",
        choices=("candidate", "publication", "pre-arm", "t0"),
        default="candidate",
    )
    parser.add_argument("--confirmation", type=Path)
    parser.add_argument("--expected-confirmation-digest")
    # Split S-5: candidate mode authenticates the executing tools against the
    # reviewed $INPUT manifest; every other phase requires committed-blob
    # equality. Nothing on disk can switch lanes -- only --phase can.
    parser.add_argument("--candidate-manifest", type=Path)
    parser.add_argument("--receipt-out", type=Path)
    parser.add_argument("--target-pack-root", type=Path)
    return parser


def _write_receipt(path: Path, result: dict[str, object]) -> None:
    raw = readiness.render_json(result)
    readiness._exclusive_write(path, raw)
    readiness._exclusive_write(
        path.with_name(f"{path.name}.sha256"),
        readiness.gnu_sidecar(readiness.sha256_bytes(raw), path.name),
    )


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        result = readiness.verify_family_publication_marker(
            args.repository,
            args.marker,
            phase=args.phase,
            confirmation_path=args.confirmation,
            expected_confirmation_digest=args.expected_confirmation_digest,
            target_pack_root=args.target_pack_root,
            consumer_tool=Path(__file__),
            candidate_manifest=args.candidate_manifest,
        )
        exit_code = 0
    except readiness.FamilyPublicationError as exc:
        result = {
            "schema_version": readiness.FAMILY_PUBLICATION_VERIFICATION_SCHEMA,
            "receipt_kind": "family_publication_verification",
            "phase": args.phase,
            "lane": "candidate" if args.phase == "candidate" else "published",
            "gate_admissible": False,
            "checked_at_utc": readiness._utc_now(),
            "status": "REFUSE",
            "publication_authorized": False,
            "family_id": "d117-v4",
            "marker": None,
            "confirmation": None,
            "consulted_git": None,
            "checks": [{"check_id": exc.check_id, "status": "REFUSE"}],
            "refusals": [
                {
                    "role": "FAMILY_PUBLICATION",
                    "code": "readiness_r1_family_publication",
                    "type": "CUSTODY",
                }
            ],
            "detail": str(exc),
            "assurance": dict(readiness.ASSURANCE),
        }
        exit_code = 2
    except (OSError, readiness.ArmReadinessError) as exc:
        result = {
            "schema_version": readiness.FAMILY_PUBLICATION_VERIFICATION_SCHEMA,
            "receipt_kind": "family_publication_verification",
            "phase": args.phase,
            "lane": "candidate" if args.phase == "candidate" else "published",
            "gate_admissible": False,
            "checked_at_utc": readiness._utc_now(),
            "status": "REFUSE",
            "publication_authorized": False,
            "family_id": "d117-v4",
            "marker": None,
            "confirmation": None,
            "consulted_git": None,
            "checks": [{"check_id": "registry_mismatch", "status": "REFUSE"}],
            "refusals": [
                {
                    "role": "REGISTRY",
                    "code": "readiness_row_registry_mismatch",
                    "type": "STRUCTURE",
                }
            ],
            "detail": str(exc),
            "assurance": dict(readiness.ASSURANCE),
        }
        exit_code = 2
    if args.receipt_out is not None:
        try:
            _write_receipt(args.receipt_out, result)
        except (OSError, readiness.ArmReadinessError) as exc:
            failure = {
                "schema_version": readiness.FAMILY_PUBLICATION_VERIFICATION_SCHEMA,
                "status": "REFUSE",
                "reason_codes": ["readiness_r1_family_publication"],
                "check_id": "output_collision",
                "detail": str(exc),
            }
            sys.stdout.buffer.write(readiness.render_json(failure))
            return 2
    sys.stdout.buffer.write(readiness.render_json(result))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
