#!/usr/bin/env python3
"""Atomically consume, revalidate, and exec one frozen D-117 window."""

from __future__ import annotations

import argparse
import hashlib
import os
import secrets
import sys
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from joulewise.arm_readiness import (  # noqa: E402
    ArmReadinessError,
    LaunchLineageError,
    consume_launch_capability,
    parse_json_bytes,
    record_launch_lifecycle_event,
    render_json,
    validate_launch_manifest,
    verify_consumed_launch,
)


# This descriptor number is part of the reviewed chain recipe. Only descriptor
# contents are secret; neither the number nor a receipt path is a capability.
HANDOFF_FD = 198
HANDOFF_TOKEN_BYTES = 32


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack-root", type=Path, required=True)
    parser.add_argument("--arm-receipt", type=Path, required=True)
    parser.add_argument(
        "--arm-readiness-custody-root", type=Path, required=True
    )
    parser.add_argument("--launch-manifest", type=Path, required=True)
    parser.add_argument(
        "--lifecycle-event",
        choices=("start", "settle", "completion"),
        help="private window-chain operation; omit for Ed's physical launch",
    )
    return parser


def _load_manifest(path: Path) -> dict[str, object]:
    try:
        raw = path.resolve(strict=True).read_bytes()
    except OSError as exc:
        raise LaunchLineageError(
            "launch_consumption_missing", f"launch manifest is unavailable: {exc}"
        ) from exc
    try:
        value = validate_launch_manifest(
            parse_json_bytes(raw, require_canonical=True)
        )
    except ArmReadinessError as exc:
        raise LaunchLineageError(
            "launch_consumption_invalid", f"launch manifest is invalid: {exc}"
        ) from exc
    return dict(value)


def _consumption_path(args: argparse.Namespace) -> Path:
    try:
        pack = args.pack_root.resolve(strict=True)
        arm = args.arm_receipt.resolve(strict=True)
        custody = args.arm_readiness_custody_root.resolve(strict=True)
    except OSError as exc:
        raise LaunchLineageError(
            "launch_consumption_missing", f"launch custody input is unavailable: {exc}"
        ) from exc
    expected_pack_custody = custody / pack.name
    if arm.parent.parent != expected_pack_custody:
        raise LaunchLineageError(
            "launch_binding_mismatch",
            "arm receipt is outside the selected pack custody root",
        )
    return (
        expected_pack_custody
        / "arm_readiness.consumptions"
        / f"{arm.stem}.consumed.json"
    )


def _install_handoff(token: bytes) -> None:
    read_fd = -1
    write_fd = -1
    try:
        read_fd, write_fd = os.pipe()
        written = os.write(write_fd, token)
        if written != len(token):
            raise OSError("short anonymous-pipe write")
        os.close(write_fd)
        write_fd = -1
        if read_fd != HANDOFF_FD:
            os.dup2(read_fd, HANDOFF_FD, inheritable=True)
            os.close(read_fd)
            read_fd = -1
        else:
            os.set_inheritable(HANDOFF_FD, True)
    except OSError as exc:
        for descriptor in {write_fd, read_fd, HANDOFF_FD} - {-1}:
            try:
                os.close(descriptor)
            except OSError:
                pass
        raise LaunchLineageError(
            "launch_handoff_invalid",
            f"cannot create inheritable anonymous-FD handoff: {exc}",
        ) from exc


def _read_one_use_handoff() -> bytes:
    try:
        token = os.read(HANDOFF_FD, HANDOFF_TOKEN_BYTES + 1)
    except OSError as exc:
        raise LaunchLineageError(
            "launch_handoff_invalid", f"inherited handoff FD is unavailable: {exc}"
        ) from exc
    finally:
        try:
            os.close(HANDOFF_FD)
        except OSError:
            pass
    if len(token) != HANDOFF_TOKEN_BYTES:
        raise LaunchLineageError(
            "launch_handoff_invalid", "inherited handoff token has invalid length"
        )
    return token


def launch(args: argparse.Namespace) -> int:
    manifest = _load_manifest(args.launch_manifest)
    argv = list(manifest["launch_command"])
    token = secrets.token_bytes(HANDOFF_TOKEN_BYTES)
    _install_handoff(token)
    result = consume_launch_capability(
        args.pack_root,
        args.arm_receipt,
        args.arm_readiness_custody_root,
        launch_manifest=args.launch_manifest,
        exec_argv=argv,
        handoff_token_sha256=hashlib.sha256(token).hexdigest(),
    )
    verified = verify_consumed_launch(
        args.pack_root,
        result["consumption_path"],
        launch_manifest=args.launch_manifest,
        expected_exec_argv=argv,
    )
    if verified["exec_argv"] != argv:
        raise LaunchLineageError(
            "launch_binding_mismatch", "verified exec argv changed before execve"
        )
    # Successful execve never returns. There is deliberately no child process,
    # wait path, or automatic retry after the capability's linearization point.
    os.execve(argv[0], argv, dict(os.environ))
    raise LaunchLineageError(
        "launch_consumption_invalid", "execve returned after consuming the launch"
    )


def lifecycle(args: argparse.Namespace) -> int:
    consumption = _consumption_path(args)
    if args.lifecycle_event == "start":
        # Full volatile replay occurs before the first settle or bundle byte.
        verify_consumed_launch(
            args.pack_root,
            consumption,
            launch_manifest=args.launch_manifest,
        )
        token = _read_one_use_handoff()
    else:
        token = None
    result = record_launch_lifecycle_event(
        args.pack_root,
        consumption,
        args.lifecycle_event,
        handoff_token=token,
    )
    sys.stdout.buffer.write(render_json(result))
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.lifecycle_event is not None:
            return lifecycle(args)
        return launch(args)
    except LaunchLineageError as exc:
        refusal = {
            "status": "REFUSE",
            "reason_codes": [exc.reason_code],
            "detail": str(exc),
        }
    except ArmReadinessError as exc:
        refusal = {
            "status": "REFUSE",
            "reason_codes": [exc.reason_code],
            "detail": str(exc),
        }
    except OSError as exc:
        refusal = {
            "status": "REFUSE",
            "reason_codes": ["launch_consumption_invalid"],
            "detail": f"launch operating-system refusal: {exc}",
        }
    sys.stdout.buffer.write(render_json(refusal))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
