#!/usr/bin/env python3
"""Generate and verify D-134 arm-readiness receipts."""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path
from typing import Any, Mapping


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.arm_readiness import (  # noqa: E402
    ArmReadinessError,
    generate_arm_receipt,
    generate_dry_run_receipt,
    generate_freeze_receipt,
    parse_json_bytes,
    render_json,
    verify_arm_receipt,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--expected-confirmation-digest",
        help="out-of-band SHA-256 of the D-117 step-6 confirmation table",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    freeze = subparsers.add_parser("freeze")
    freeze.add_argument("--pack-root", type=Path, required=True)
    freeze.add_argument(
        "--measurement-checkout",
        type=Path,
        required=True,
        help="absolute operator-declared measurement checkout",
    )
    freeze.add_argument(
        "--step6-confirmation-table",
        type=Path,
        help="path to the D-117 step-6 confirmation table",
    )
    freeze.add_argument(
        "--expected-confirmation-digest",
        default=argparse.SUPPRESS,
        help="out-of-band SHA-256 of the D-117 step-6 confirmation table",
    )
    # D-139: a successor pack's freeze receipt binds an authenticated
    # predecessor pack.  The command accepts a path only; every recorded ID,
    # digest, and ordinal is derived from that pack's committed bytes.
    freeze.add_argument("--predecessor-pack-root", type=Path, default=None)

    dry_run = subparsers.add_parser("dry-run")
    dry_run.add_argument("--pack-root", type=Path, required=True)
    dry_run.add_argument("--window-custody-root", type=Path, required=True)
    dry_run.add_argument("--rehearsal-id", required=True)
    dry_run.add_argument("--synthetic-root", type=Path, required=True)

    arm = subparsers.add_parser("arm")
    arm.add_argument("--pack-root", type=Path, required=True)
    arm.add_argument("--arm-context", required=True)
    arm.add_argument("--window-custody-root", type=Path, required=True)
    arm.add_argument(
        "--expected-confirmation-digest",
        default=argparse.SUPPRESS,
        help="out-of-band SHA-256 of the D-117 step-6 confirmation table",
    )

    verify = subparsers.add_parser("verify")
    verify.add_argument("--pack-root", type=Path, required=True)
    verify.add_argument("--arm-receipt", type=Path, required=True)
    verify.add_argument(
        "--expected-confirmation-digest",
        default=argparse.SUPPRESS,
        help="out-of-band SHA-256 of the D-117 step-6 confirmation table",
    )

    consume = subparsers.add_parser("consume")
    consume.add_argument("--pack-root", type=Path, required=True)
    consume.add_argument("--arm-receipt", type=Path, required=True)
    consume.add_argument("--window-custody-root", type=Path, required=True)
    return parser


def _arm_context(value: str) -> Mapping[str, Any]:
    if not value.lstrip().startswith("{"):
        raise ArmReadinessError(
            "readiness_usage_invalid",
            "--arm-context must be the JSON object itself, not a path",
        )
    raw = value.encode("utf-8")
    parsed = parse_json_bytes(raw)
    if not isinstance(parsed, Mapping):
        raise ArmReadinessError(
            "readiness_usage_invalid", "--arm-context must contain one JSON object"
        )
    return parsed


def _pack_snapshot(pack_root: Path) -> dict[str, str]:
    root = pack_root.resolve(strict=True)
    result: dict[str, str] = {}
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        if path.is_symlink():
            result[path.relative_to(root).as_posix()] = "symlink:" + str(path.readlink())
        elif path.is_file():
            result[path.relative_to(root).as_posix()] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
    return result


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    read_only = args.command != "freeze"
    before: dict[str, str] | None = None
    try:
        if read_only:
            before = _pack_snapshot(args.pack_root)
        if args.command == "freeze":
            result = generate_freeze_receipt(
                args.pack_root,
                measurement_checkout=args.measurement_checkout,
                predecessor_pack_root=args.predecessor_pack_root,
                step6_confirmation_table=args.step6_confirmation_table,
                expected_confirmation_digest=args.expected_confirmation_digest,
            )
        elif args.command == "dry-run":
            result = generate_dry_run_receipt(
                args.pack_root,
                args.window_custody_root,
                args.rehearsal_id,
                args.synthetic_root,
            )
        elif args.command == "arm":
            result = generate_arm_receipt(
                args.pack_root,
                _arm_context(args.arm_context),
                args.window_custody_root,
                expected_confirmation_digest=args.expected_confirmation_digest,
            )
        elif args.command == "verify":
            result = verify_arm_receipt(
                args.pack_root,
                args.arm_receipt,
                expected_confirmation_digest=args.expected_confirmation_digest,
            )
        else:
            raise ArmReadinessError(
                "readiness_usage_invalid",
                "standalone consume is retired; Ed must invoke "
                "scripts/launch_window.py for the reviewed consume-to-exec route",
            )
        if read_only and before != _pack_snapshot(args.pack_root):
            raise ArmReadinessError(
                "readiness_internal_error", f"{args.command} modified pack bytes"
            )
    except ArmReadinessError as exc:
        if read_only and before is not None:
            try:
                if before != _pack_snapshot(args.pack_root):
                    exc = ArmReadinessError(
                        "readiness_internal_error",
                        f"{args.command} modified pack bytes before refusing",
                    )
            except OSError:
                exc = ArmReadinessError(
                    "readiness_internal_error",
                    f"{args.command} made the pack unreadable before refusing",
                )
        refusal = {
            "status": "REFUSE",
            "arm_disposition": "NO_GO" if args.command in {"arm", "verify", "consume"} else "NOT_APPLICABLE",
            "reason_codes": [exc.reason_code],
            "detail": str(exc),
        }
        sys.stdout.buffer.write(render_json(refusal))
        return 2
    except OSError as exc:
        refusal = {
            "status": "REFUSE",
            "arm_disposition": (
                "NO_GO"
                if args.command in {"arm", "verify", "consume"}
                else "NOT_APPLICABLE"
            ),
            "reason_codes": ["readiness_io_error"],
            "detail": str(exc),
        }
        sys.stdout.buffer.write(render_json(refusal))
        return 2
    sys.stdout.buffer.write(render_json(result))
    return 0 if result.get("status") not in {"REFUSE"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
