"""Stored transaction receipt formats retained for historical authentication.

No capture, launch, receipt issuance or machine probing is performed here.
"""
from __future__ import annotations
import re as _re
import shlex as _shlex
from pathlib import Path as _Path
from typing import Mapping as _Mapping
from dataclasses import dataclass
from pathlib import Path


_COMMAND_SCHEMA = "joulewise.arm_readiness_t0_command_capture.v1"


_INPUT_DIRECTORY = "arm_readiness.t0.inputs"


_EVIDENCE_DIRECTORY = "arm_readiness.evidence"


_MAX_T0_SEQUENCE_AGE_NS = 60 * 60 * 1_000_000_000


WINDOW_ENV_KEYS = frozenset(
    {
        "MEASUREMENT_REPO",
        "WINDOW_ID",
        "BRACKET_SESSION_ID",
        "FROZEN_PLAN",
        "PACK_ROOT",
        "PACK_ID",
        "PLAN_ID",
        "EVIDENCE_ROOT_ID",
        "IDENTITY_EPOCH_JSON",
        "T1_BINDINGS_JSON",
        "PRE_ATTEMPT_ID",
        "POST_ATTEMPT_ID",
        "RUNS_ROOT",
        "BOUND_RUNS_ROOT",
        "CALIBRATION_LEDGER",
        "LEDGER_HEAD_PIN",
        "ARM_READINESS_CUSTODY_ROOT",
        "CUSTODY_ROOT",
        "WINDOW_CUSTODY_ROOT",
        "QUARANTINE_ROOT",
        "CLAIM_BACKUP_DEST",
        "BOUND_BACKUP_DEST",
        "WAIVER_PATH",
        "POWER_POLICY",
        "SETTLE_S",
    }
)


_EXPECTED_ROWS = (
    "clock.correct_and_prior_state",
    "clock.network_time_off",
    "desk.terminal_review",
    "t0.background_quiet",
    "t0.campaign_lock_absent",
    "t0.display_thermal_idle",
    "t0.fresh_roots_waivers",
    "t0.ledger_reservation",
    "t0.machine_readiness",
    "t0.no_stray_keepawake",
    "t0.offline_inputs",
    "t0.passwordless_powermetrics",
    "t0.power_path",
    "t0.single_launch_capability",
    "t0.storage_backup_capacity",
)


_ROW_KIND = {
    "clock.correct_and_prior_state": "CLOCK_ATTESTATION",
    "clock.network_time_off": "CLOCK_PROBE",
    "desk.terminal_review": "TERMINAL_REVIEW",
    "t0.background_quiet": "MAINTENANCE_CENSUS",
    "t0.campaign_lock_absent": "ROOT_PREFLIGHT",
    "t0.display_thermal_idle": "MACHINE_PREFLIGHT",
    "t0.fresh_roots_waivers": "ROOT_PREFLIGHT",
    "t0.ledger_reservation": "LEDGER_RESERVATION",
    "t0.machine_readiness": "MACHINE_PREFLIGHT",
    "t0.no_stray_keepawake": "PROCESS_CENSUS",
    "t0.offline_inputs": "OFFLINE_INPUT_INVENTORY",
    "t0.passwordless_powermetrics": "POWERMETRICS_PROBE",
    "t0.power_path": "POWER_PREFLIGHT",
    "t0.single_launch_capability": "LAUNCH_RECIPE",
    "t0.storage_backup_capacity": "BACKUP_PREFLIGHT",
}


_CAPTURE_FILES = {
    "clock-reference": "clock-reference.json",
    "clock-disable": "clock-disable.json",
    "quiet-mac-prep": "quiet-mac-prep.json",
    "prewindow-check": "prewindow-check.json",
    "ledger-readiness": "ledger-readiness.json",
    "ledger-reservation": "ledger-reservation.json",
}


_CAPTURE_KEYS = {
    "schema_version",
    "step_id",
    "argv",
    "cwd",
    "exit_code",
    "stdout",
    "stderr",
    "started_monotonic_ns",
    "finished_monotonic_ns",
    "boot_session_id",
}


class WindowEnvironmentParseError(ValueError):
    """Boundary-neutral refusal from the shared exact window.env parser."""

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


def _receipt_name(row_id: str) -> str:
    return f"evidence-t0-{_slug(row_id)}.json"


def parse_window_environment(raw: bytes) -> dict[str, str]:
    """Parse the exact 25-key T-0 window environment contract."""

    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise WindowEnvironmentParseError("window.env is not UTF-8") from exc
    values: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = _re.fullmatch(r"([A-Z][A-Z0-9_]*)=(.*)", stripped)
        if match is None:
            raise WindowEnvironmentParseError(
                f"window.env contains a non-assignment line: {stripped!r}"
            )
        name, raw_value = match.groups()
        try:
            parts = _shlex.split(raw_value, posix=True)
        except ValueError as exc:
            raise WindowEnvironmentParseError(
                f"window.env value for {name} is malformed"
            ) from exc
        if len(parts) != 1 or "$" in parts[0] or name in values:
            raise WindowEnvironmentParseError(
                f"window.env value for {name} is ambiguous"
            )
        values[name] = parts[0]
    missing = WINDOW_ENV_KEYS - set(values)
    unknown = set(values) - WINDOW_ENV_KEYS
    if missing or unknown:
        raise WindowEnvironmentParseError(
            "window.env exact keys differ; "
            f"missing={sorted(missing)!r}, unknown={sorted(unknown)!r}"
        )
    return values



REHEARSAL_RECEIPT_CLASS = "T0_UNATTENDED_SUPERVISED_REHEARSAL"


REHEARSAL_WINDOW_PREFIX = "rehearsal-t0-unattended-"


G7_CONTROL_SCHEMA = "joulewise.pack_night_g7_control.v1"


REHEARSAL_RECEIPT_SCHEMA = "joulewise.t0_unattended_rehearsal_receipt.v1"


_REHEARSAL_RECEIPT_KEYS = {
    "schema_version",
    "receipt_class",
    "claim_eligible",
    "window_id",
    "custody_root",
    "acceptance_target",
}


@dataclass(frozen=True)
class ProductionRoot:
    """One role-labelled, resolved root used by production."""

    role: str
    path: Path
    resolution_error: str | None = None


def _contains(parent: Path, child: Path) -> bool:
    try:
        child.relative_to(parent)
    except ValueError:
        return False
    return True



def _slug(value: str) -> str:
    return value.lower().replace("_", "-").replace(".", "-")

