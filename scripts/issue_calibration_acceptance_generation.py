#!/usr/bin/env python3
"""Inspect the active calibration epoch at the desk; never authorize capture.

The prospective issuer is reserved for S4. This read-only watch authenticates
the active issued artifact and ledger before comparing machine identity. It
does not evaluate a trigger observation or change the D-102 prior-artifact rule.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping

sys.dont_write_bytecode = True
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from joulewise.calibration_bracketing import (  # noqa: E402
    ACTIVE_ACCEPTANCE_ID,
    DEFAULT_ACCEPTANCE_BOUND_PATH,
    load_calibration_acceptance_bound,
)
from joulewise.calibration_ledger import (  # noqa: E402
    DEFAULT_HEAD_PIN_PATH,
    DEFAULT_LEDGER_PATH,
    load_calibration_ledger_snapshot,
)


WATCH_FIELDS = ("os_build", "hardware_model", "powermetrics_sha256", "mlx_version")
POWERMETRICS_PATH = Path("/usr/bin/powermetrics")
# Absolute, like every other governed invocation: a PATH-resolved probe could
# report an identity this machine does not have.
SYSCTL_PATH = Path("/usr/sbin/sysctl")


def observe_machine() -> dict[str, str | None]:
    """Read identity only: the sampler binary is hashed, never executed."""
    observed: dict[str, str | None] = {}
    for field, key in (("os_build", "kern.osversion"), ("hardware_model", "hw.model")):
        try:
            observed[field] = subprocess.run(
                [str(SYSCTL_PATH), "-n", key], check=True, capture_output=True,
                text=True, timeout=10,
            ).stdout.strip() or None
        except (OSError, subprocess.SubprocessError):
            observed[field] = None
    try:
        observed["powermetrics_sha256"] = hashlib.sha256(
            POWERMETRICS_PATH.read_bytes()
        ).hexdigest()
    except OSError:
        observed["powermetrics_sha256"] = None
    try:
        # Use the same module/version surface as the live writer's T1 vector.
        version = getattr(importlib.import_module("mlx.core"), "__version__", None)
        observed["mlx_version"] = version if isinstance(version, str) and version else None
    except Exception:
        # Optional native dependency: import/link/initialization failure means
        # unavailable, never an assertion that the registered version matches.
        observed["mlx_version"] = None
    return observed


def mismatched_fields(
    expected: Mapping[str, Any], observed: Mapping[str, Any],
) -> tuple[str, ...]:
    """Unknown on either side is a mismatch, including unknown == unknown."""
    return tuple(
        field for field in WATCH_FIELDS
        if not isinstance(expected.get(field), str) or not expected[field]
        or not isinstance(observed.get(field), str) or not observed[field]
        or expected[field] != observed[field]
    )


def check(args: argparse.Namespace) -> int:
    errors: list[str] = []
    expected: dict[str, Any] = {}
    acceptance = load_calibration_acceptance_bound(args.acceptance)
    if (
        acceptance is None or acceptance.get("artifact_role") != "issued"
        or acceptance.get("acceptance_id") != ACTIVE_ACCEPTANCE_ID
        or not isinstance(acceptance.get("identity_epoch"), Mapping)
    ):
        errors.append("acceptance: invalid or not ACTIVE issued acceptance")
    else:
        epoch = acceptance["identity_epoch"]
        expected.update({field: epoch.get(field) for field in WATCH_FIELDS[:2]})

    snapshot = load_calibration_ledger_snapshot(
        args.ledger, args.head_pin, require_committed_pin=True,
        verify_custody=True, mode="read_replay", repo_root=REPO_ROOT,
    )
    if snapshot.refusal_reasons:
        errors.append("ledger: " + ", ".join(snapshot.refusal_reasons))
    elif not snapshot.receipts:
        errors.append("ledger: no last row with T1 bindings")
    else:
        # Do not silently substitute an older row if the physical last row
        # lacks T1 (e.g. an abort/control receipt); report unavailable instead.
        t1 = snapshot.receipts[-1].get("t1_bindings")
        if not isinstance(t1, Mapping):
            errors.append("ledger: last row has no T1 bindings")
        else:
            expected.update({field: t1.get(field) for field in WATCH_FIELDS[2:]})

    observed = observe_machine()
    mismatches = mismatched_fields(expected, observed)
    print("Desk epoch watch (identity comparison only; no capture authorization)")
    print(f"ACTIVE acceptance: {ACTIVE_ACCEPTANCE_ID}")
    print(f"{'field':<22} {'expected':<64} {'observed':<64} status")
    for field in WATCH_FIELDS:
        baseline = expected.get(field) or "unavailable"
        current = observed.get(field) or "unavailable"
        status = "MISMATCH" if field in mismatches else "match"
        print(f"{field:<22} {baseline:<64} {current:<64} {status}")
    for error in errors:
        print(error)
    if mismatches:
        print("mismatched fields: " + ", ".join(mismatches))
    return 3 if errors or mismatches else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    watch = commands.add_parser("check", help="read-only desk epoch watch")
    watch.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER_PATH)
    watch.add_argument("--head-pin", type=Path, default=DEFAULT_HEAD_PIN_PATH)
    watch.add_argument("--acceptance", type=Path, default=DEFAULT_ACCEPTANCE_BOUND_PATH)
    commands.add_parser("prepare-candidate", help="reserved for S4; not implemented")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "prepare-candidate":
        print("not implemented: waits for seat S3's generation-row schema and the corpus")
        return 64
    return check(args)


if __name__ == "__main__":
    raise SystemExit(main())
