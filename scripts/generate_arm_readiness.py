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
    subparsers = parser.add_subparsers(dest="command", required=True)

    freeze = subparsers.add_parser("freeze")
    freeze.add_argument("--pack-root", type=Path, required=True)
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

    verify = subparsers.add_parser("verify")
    verify.add_argument("--pack-root", type=Path, required=True)
    verify.add_argument("--arm-receipt", type=Path, required=True)

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
                predecessor_pack_root=args.predecessor_pack_root,
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
            )
        elif args.command == "verify":
            result = verify_arm_receipt(args.pack_root, args.arm_receipt)
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
