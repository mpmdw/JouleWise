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
    _consume_launch_capability,
    _verify_arm_receipt,
    parse_json_bytes,
    record_launch_lifecycle_event,
    render_json,
    validate_arm_receipt,
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
    parser.add_argument(
        "--step6-confirmation-table",
        type=Path,
        help="path to the D-117 step-6 confirmation table",
    )
    parser.add_argument(
        "--expected-confirmation-digest",
        help="out-of-band SHA-256 of the D-117 step-6 confirmation table",
    )
    return parser


def _read_required_launch_input(path: Path, label: str) -> tuple[Path, bytes]:
    try:
        if path.is_symlink():
            raise LaunchLineageError(
                "launch_consumption_invalid", f"{label} must not be a symlink"
            )
        resolved = path.resolve(strict=True)
        raw = resolved.read_bytes()
    except LaunchLineageError:
        raise
    except OSError as exc:
        raise LaunchLineageError(
            "launch_consumption_missing", f"{label} is unavailable: {exc}"
        ) from exc
    if not resolved.is_file():
        raise LaunchLineageError(
            "launch_consumption_invalid", f"{label} is not a regular file"
        )
    return resolved, raw


def _load_manifest_input(path: Path) -> tuple[dict[str, object], Path, bytes]:
    resolved, raw = _read_required_launch_input(path, "launch manifest")
    try:
        value = validate_launch_manifest(
            parse_json_bytes(raw, require_canonical=True)
        )
    except ArmReadinessError as exc:
        raise LaunchLineageError(
            "launch_consumption_invalid", f"launch manifest is invalid: {exc}"
        ) from exc
    return dict(value), resolved, raw


def _load_manifest(path: Path) -> dict[str, object]:
    manifest, _resolved, _raw = _load_manifest_input(path)
    return manifest


def _assemble_launch_inputs(args: argparse.Namespace) -> dict[str, object]:
    """Authenticate and assemble every required input for callee replay."""

    try:
        pack_root = args.pack_root.resolve(strict=True)
        custody_root = args.arm_readiness_custody_root.resolve(strict=True)
    except OSError as exc:
        raise LaunchLineageError(
            "launch_consumption_missing", f"launch root is unavailable: {exc}"
        ) from exc
    arm_path, arm_raw = _read_required_launch_input(
        args.arm_receipt, "arm receipt"
    )
    manifest, manifest_path, manifest_raw = _load_manifest_input(
        args.launch_manifest
    )
    try:
        arm = validate_arm_receipt(
            parse_json_bytes(arm_raw, require_canonical=True)
        )
    except ArmReadinessError as exc:
        raise LaunchLineageError(
            "launch_consumption_invalid", f"arm receipt is invalid: {exc}"
        ) from exc
    verified_arm = _verify_arm_receipt(
        pack_root,
        arm_path,
        require_unconsumed=False,
        step6_confirmation_table=args.step6_confirmation_table,
        expected_confirmation_digest=args.expected_confirmation_digest,
    )
    arm_digest = hashlib.sha256(arm_raw).hexdigest()
    if (
        verified_arm["receipt_sha256"] != arm_digest
        or verified_arm["receipt_path"] != str(arm_path)
    ):
        raise LaunchLineageError(
            "launch_binding_mismatch",
            "authenticated arm receipt changed during launch assembly",
        )
    try:
        window_root = Path(str(manifest["window_plan_root"])).resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise LaunchLineageError(
            "launch_consumption_missing", f"window plan root is unavailable: {exc}"
        ) from exc
    _env_path, env_raw = _read_required_launch_input(
        window_root / "window.env", "window.env"
    )
    _chain_path, chain_raw = _read_required_launch_input(
        window_root / "window-chain.zsh", "window chain"
    )
    return {
        "pack_root": pack_root,
        "arm_receipt": arm_path,
        "authenticated_arm_receipt": dict(arm),
        "arm_receipt_sha256": arm_digest,
        "window_custody_root": custody_root,
        "launch_manifest": manifest_path,
        "authenticated_launch_manifest": manifest,
        "launch_manifest_sha256": hashlib.sha256(manifest_raw).hexdigest(),
        "window_plan_root": window_root,
        "window_environment_sha256": hashlib.sha256(env_raw).hexdigest(),
        "window_chain_sha256": hashlib.sha256(chain_raw).hexdigest(),
        "exec_argv": list(manifest["launch_command"]),
    }


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
    launch_inputs = _assemble_launch_inputs(args)
    argv = list(launch_inputs["exec_argv"])
    token = secrets.token_bytes(HANDOFF_TOKEN_BYTES)
    _install_handoff(token)
    result = _consume_launch_capability(
        **launch_inputs,
        handoff_token_sha256=hashlib.sha256(token).hexdigest(),
        step6_confirmation_table=args.step6_confirmation_table,
        expected_confirmation_digest=args.expected_confirmation_digest,
    )
    verified = verify_consumed_launch(
        args.pack_root,
        result["consumption_path"],
        launch_manifest=args.launch_manifest,
        expected_exec_argv=argv,
        step6_confirmation_table=args.step6_confirmation_table,
        expected_confirmation_digest=args.expected_confirmation_digest,
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
            step6_confirmation_table=args.step6_confirmation_table,
            expected_confirmation_digest=args.expected_confirmation_digest,
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
