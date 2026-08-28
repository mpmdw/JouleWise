"""Derive D-134 ARM_ONLY evidence from T-0 artifacts and fresh probes.

The public author accepts only the committed pack and the D-134 custody root.
It never accepts conclusions, evidence paths, hashes, probe output, or row
states.  Governed machine-authored command captures live in the private
custody input namespace.  Fresh current-state conditions are probed again here;
historical E-step captures are authenticated for canonical bytes, same-boot
freshness, and ordering.  Faithful invocation remains a trusted-operator
limitation: v1 cannot detect deliberate operator fabrication.
"""

from __future__ import annotations

import copy as _copy
import inspect as _inspect
import json as _json
import os as _os
import re as _re
import shlex as _shlex
import shutil as _shutil
import signal as _signal
import subprocess as _subprocess
import tempfile as _tempfile
import time as _time
from dataclasses import dataclass as _dataclass, field as _field
from decimal import Decimal as _Decimal
from pathlib import Path as _Path, PurePosixPath as _PurePosixPath
from typing import (
    Any as _Any,
    Callable as _Callable,
    Mapping as _Mapping,
    Sequence as _Sequence,
)

from joulewise import arm_readiness as _readiness
from joulewise import calibration_ledger as _ledger
from joulewise import clock_reference as _clock_reference
from joulewise import identity_pins as _identity


_SOURCE_SCHEMA = "joulewise.arm_readiness_t0_evidence_source.v1"
_COMMAND_SCHEMA = "joulewise.arm_readiness_t0_command_capture.v1"
_LAUNCH_SCHEMA = "joulewise.arm_readiness_t0_launch_manifest.v1"
_INPUT_DIRECTORY = "arm_readiness.t0.inputs"
_SOURCE_DIRECTORY = "arm_readiness.t0.sources"
_EVIDENCE_DIRECTORY = "arm_readiness.evidence"
# Live machine state can change between authoring and ARM consumption.  Keep
# that unavoidable TOCTOU window bounded to the expected arm-sequence length.
_VOLATILE_EVIDENCE_VALIDITY_NS = 20 * 60 * 1_000_000_000
_NONVOLATILE_EVIDENCE_VALIDITY_NS = 6 * 60 * 60 * 1_000_000_000
_MIN_IDLE_NS = 600 * 1_000_000_000
_MAX_T0_SEQUENCE_AGE_NS = 60 * 60 * 1_000_000_000
_MIN_BACKUP_FREE_BYTES = 20 * 1024**3
_PROBE_TIMEOUT_SECONDS = 45
_RUNNING_REPOSITORY = _Path(__file__).resolve().parents[1]
_AUTHORING_ARTIFACTS = (
    "joulewise/clock_reference.py",
    "joulewise/arm_readiness_evidence_t0.py",
    "scripts/author_arm_evidence_t0.py",
    "scripts/capture_t0_step.py",
    "scripts/collect_clock_reference.py",
)
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
_INTERNAL_ROWS = frozenset(
    {
        "desk.identity_pin_projection",
        "desk.reviewed_checkout",
        "desk.under_lease_rehearsal",
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
_VOLATILE_EVIDENCE_KINDS = frozenset(
    {
        "BACKUP_PREFLIGHT",
        "CLOCK_PROBE",
        "LAUNCH_RECIPE",
        "MAINTENANCE_CENSUS",
        "MACHINE_PREFLIGHT",
        "POWERMETRICS_PROBE",
        "POWER_PREFLIGHT",
        "PROCESS_CENSUS",
        "ROOT_PREFLIGHT",
    }
)
_NONVOLATILE_EVIDENCE_KINDS = frozenset(
    {
        "CLOCK_ATTESTATION",
        "LEDGER_RESERVATION",
        "OFFLINE_INPUT_INVENTORY",
        "TERMINAL_REVIEW",
    }
)
if (
    _VOLATILE_EVIDENCE_KINDS & _NONVOLATILE_EVIDENCE_KINDS
    or _VOLATILE_EVIDENCE_KINDS | _NONVOLATILE_EVIDENCE_KINDS
    != frozenset(_ROW_KIND.values())
):
    raise AssertionError("every governed evidence kind needs one volatility class")
# The last ordinary receipt sidecar is also the publication-completion marker.
# Until this authenticated file exists, arm_readiness._discover_evidence sees
# an unmatched receipt and refuses the namespace as unreadable.
_PUBLICATION_COMPLETION_MARKER = (
    "evidence-t0-t0-storage-backup-capacity.json.sha256"
)
_CAPTURE_FILES = {
    "clock-reference": "clock-reference.json",
    "clock-disable": "clock-disable.json",
    "quiet-mac-prep": "quiet-mac-prep.json",
    "prewindow-check": "prewindow-check.json",
    "ledger-readiness": "ledger-readiness.json",
    "ledger-reservation": "ledger-reservation.json",
}
_CAPTURE_ORDER = tuple(_CAPTURE_FILES)
_RUNBOOK_ARTIFACT_REASON_CODES = {
    "arm_context": "evidence_author_t0_arm_context_missing",
    "clock_reference_capture": "evidence_author_t0_clock_attestation_missing",
    "clock_disable_capture": "evidence_author_t0_clock_disable_missing",
    "quiet_mac_prep_capture": "evidence_author_t0_quiet_mac_prep_missing",
    "prewindow_check_capture": "evidence_author_t0_prewindow_check_missing",
    "ledger_readiness_capture": "evidence_author_t0_ledger_readiness_missing",
    "ledger_reservation_capture": "evidence_author_t0_ledger_reservation_missing",
    "launch_manifest": "evidence_author_t0_launch_manifest_missing",
    "window_environment": "evidence_author_t0_window_environment_missing",
    "window_chain": "evidence_author_t0_window_chain_missing",
    "waiver_record": "evidence_author_t0_waiver_record_missing",
    "identity_epoch": "evidence_author_t0_identity_epoch_missing",
    "t1_bindings": "evidence_author_t0_t1_bindings_missing",
    "production_ledger": "evidence_author_t0_production_ledger_missing",
}
_SOURCE_KEYS = {
    "schema_version",
    "row_id",
    "kind",
    "head_commit",
    "head_tree_oid",
    "pack_sha256",
    "boot_session_id",
    "primary_artifacts",
    "input_artifacts",
    "probes",
    "facts",
    "derivation",
}
_ARTIFACT_KEYS = {"path", "sha256"}
_SOURCE_FACT_KEYS = {"fact_id", "value"}
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
_CLOCK_REFERENCE_KEYS = {
    "schema_version",
    "sample_policy_id",
    "boot_session_id",
    "anchor_realtime_ns",
    "anchor_monotonic_raw_ns",
    "anchor_read_skew_ns",
    "batch_started_monotonic_raw_ns",
    "batch_finished_monotonic_raw_ns",
    "samples",
}
_CLOCK_REFERENCE_SAMPLE_KEYS = {
    "server",
    "argv",
    "exit_code",
    "started_monotonic_raw_ns",
    "finished_monotonic_raw_ns",
    "stdout",
    "stderr",
    "parsed",
    "offset_s",
    "uncertainty_s",
    "peer_address",
    "raw_line",
}
_LAUNCH_KEYS = {
    "schema_version",
    "boot_session_id",
    "window_plan_root",
    "prewindow_command",
    "launch_command",
}
_SHA_RE = _re.compile(r"^[0-9a-f]{64}$")
_GIT_RE = _re.compile(r"^[0-9a-f]{40}$")


class T0EvidenceAuthoringError(ValueError):
    """A fail-closed refusal naming the affected row evidence kind."""

    def __init__(self, kind: str, reason_code: str, detail: str) -> None:
        super().__init__(detail)
        self.kind = kind
        self.reason_code = reason_code


class WindowEnvironmentParseError(ValueError):
    """Boundary-neutral refusal from the shared exact window.env parser."""

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


@_dataclass(frozen=True)
class _ProbeResult:
    argv: tuple[str, ...]
    cwd: str
    exit_code: int
    stdout: str
    stderr: str

    def evidence(self) -> dict[str, _Any]:
        return {
            "argv": list(self.argv),
            "cwd": self.cwd,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
        }


@_dataclass(frozen=True)
class _DerivationClock:
    monotonic_ns: _Callable[[], int]
    utc_now: _Callable[[], str]
    sample_anchor: _Callable[[], _clock_reference.ClockAnchor]


def _production_clock() -> _DerivationClock:
    """Return the ambient clock used by the production author."""

    return _DerivationClock(
        monotonic_ns=_time.monotonic_ns,
        utc_now=_readiness._utc_now,
        sample_anchor=_clock_reference.sample_anchor,
    )


def _default_derivation_clock() -> _DerivationClock:
    return _production_clock()


@_dataclass
class _DerivationContext:
    pack_root: _Path
    repository: _Path
    custody_root: _Path
    custody_pack_root: _Path
    tree: _Mapping[str, _Any]
    pack_sha256: str
    plan_sha256: str
    head_commit: str
    head_tree_oid: str
    boot_session_id: str
    boot_probe: _ProbeResult
    clock: _DerivationClock = _field(default_factory=_default_derivation_clock)
    captures: dict[str, tuple[_Mapping[str, _Any], dict[str, str]]] = _field(
        default_factory=dict
    )
    values: dict[str, _Any] = _field(default_factory=dict)


# Compatibility for focused tests and private callers written before the
# context acquired its explicit clock.
_Context = _DerivationContext


@_dataclass(frozen=True)
class _DerivedRow:
    row_id: str
    kind: str
    value: _Mapping[str, _Any]
    source_kind: str
    primary_artifacts: tuple[_Mapping[str, str], ...] = ()
    input_artifacts: tuple[_Mapping[str, str], ...] = ()
    probes: tuple[_ProbeResult, ...] = ()
    derivation: _Mapping[str, _Any] = _field(default_factory=dict)


def _refuse(kind: str, code: str, detail: str) -> T0EvidenceAuthoringError:
    return T0EvidenceAuthoringError(kind, code, detail)


def _underivable(kind: str, detail: str) -> T0EvidenceAuthoringError:
    return _refuse(
        kind,
        f"evidence_author_t0_{kind.lower()}_underivable",
        detail,
    )


def _missing_artifact(
    kind: str, artifact_class: str, detail: str
) -> T0EvidenceAuthoringError:
    return _refuse(kind, _RUNBOOK_ARTIFACT_REASON_CODES[artifact_class], detail)


def _slug(value: str) -> str:
    return value.lower().replace("_", "-").replace(".", "-")


def _source_path(row_id: str) -> str:
    return f"{_SOURCE_DIRECTORY}/{_slug(row_id)}.json"


def _receipt_name(row_id: str) -> str:
    return f"evidence-t0-{_slug(row_id)}.json"


def _evidence_id(row_id: str) -> str:
    return f"arm-t0-{_slug(row_id)}-v1"


def _regular_bytes(path: _Path, *, kind: str, label: str) -> bytes:
    try:
        mode = path.lstat().st_mode
        if path.is_symlink() or not _os.path.isfile(path):
            raise OSError("not a regular non-symlink file")
        del mode
        return path.read_bytes()
    except OSError as exc:
        raise _underivable(kind, f"{label} is unreadable: {path}: {exc}") from exc


def _committed_artifact(
    repository: _Path, relative: str, *, kind: str
) -> tuple[dict[str, str], bytes]:
    path = repository / _PurePosixPath(relative)
    raw = _regular_bytes(path, kind=kind, label="committed primary artifact")
    committed = _readiness._git_blob_at_head(repository, relative)
    if committed is None or committed != raw:
        raise _underivable(
            kind, f"primary artifact is not byte-identical to HEAD: {relative}"
        )
    return {"path": relative, "sha256": _readiness.sha256_bytes(raw)}, raw


def _input_identity(path: _Path, *, kind: str, label: str) -> tuple[dict[str, str], bytes]:
    raw = _regular_bytes(path, kind=kind, label=label)
    return {"path": str(path.resolve()), "sha256": _readiness.sha256_bytes(raw)}, raw


def _canonical_object(
    path: _Path,
    *,
    kind: str,
    label: str,
) -> tuple[_Mapping[str, _Any], dict[str, str], bytes]:
    identity, raw = _input_identity(path, kind=kind, label=label)
    try:
        value = _readiness.parse_json_bytes(raw, require_canonical=True)
    except _readiness.ArmReadinessError as exc:
        raise _underivable(kind, f"{label} is not canonical strict JSON: {exc}") from exc
    if not isinstance(value, _Mapping):
        raise _underivable(kind, f"{label} must contain one object")
    return value, identity, raw


def _execute_probe(argv: _Sequence[str], *, cwd: _Path) -> _ProbeResult:
    """Execute one bounded probe without a shell or inherited environment."""

    environment = {
        name: _os.environ[name]
        for name in ("SYSTEMROOT", "WINDIR")
        if name in _os.environ
    }
    environment.update({"LANG": "C", "LC_ALL": "C", "PATH": "/usr/bin:/bin:/usr/sbin:/sbin"})
    try:
        with _tempfile.TemporaryFile() as stdout, _tempfile.TemporaryFile() as stderr:
            process = _subprocess.Popen(
                list(argv),
                cwd=cwd,
                env=environment,
                stdin=_subprocess.DEVNULL,
                stdout=stdout,
                stderr=stderr,
                start_new_session=True,
            )
            timed_out = False
            try:
                process.wait(timeout=_PROBE_TIMEOUT_SECONDS)
            except _subprocess.TimeoutExpired:
                timed_out = True
            finally:
                if timed_out:
                    try:
                        _os.killpg(process.pid, _signal.SIGKILL)
                    except ProcessLookupError:
                        pass
            process.wait()
            stdout.seek(0)
            stderr.seek(0)
            stdout_raw = stdout.read()
            stderr_raw = stderr.read()
    except (OSError, _subprocess.SubprocessError) as exc:
        raise ValueError(f"probe could not execute: {exc}") from exc
    if timed_out:
        raise ValueError(f"probe timed out after {_PROBE_TIMEOUT_SECONDS} seconds")
    return _ProbeResult(
        tuple(argv),
        str(cwd.resolve()),
        int(process.returncode),
        stdout_raw.decode("utf-8", errors="replace"),
        stderr_raw.decode("utf-8", errors="replace"),
    )


def _fresh_probe(
    context: _Context,
    kind: str,
    label: str,
    argv: _Sequence[str],
) -> _ProbeResult:
    if kind in {"MAINTENANCE_CENSUS", "PROCESS_CENSUS"}:
        r1_finished = context.values.get("r1_batch_finished_monotonic_ns")
        if (
            not _real_int(r1_finished)
            or r1_finished > context.clock.monotonic_ns()
        ):
            raise _underivable(
                kind,
                "fresh census cannot run before the R1 clock-reference batch completes",
            )
    try:
        return _execute_probe(argv, cwd=context.repository)
    except Exception as exc:
        raise _underivable(kind, f"fresh {label} probe could not execute: {exc}") from exc


def _boot_probe(repository: _Path) -> tuple[str, _ProbeResult]:
    kind = "AUTHORING_SET"
    try:
        result = _execute_probe(
            ("/usr/sbin/sysctl", "-n", "kern.bootsessionuuid"), cwd=repository
        )
    except Exception as exc:
        raise _underivable(kind, f"fresh boot-session probe failed: {exc}") from exc
    value = result.stdout.strip().lower()
    try:
        parsed = _readiness._require_boot_session_id(value, "kern.bootsessionuuid")
    except _readiness.ArmReadinessError as exc:
        raise _underivable(kind, f"fresh boot-session probe was invalid: {exc}") from exc
    if result.exit_code != 0:
        raise _underivable(kind, "fresh boot-session probe refused")
    return parsed, result


def _capture(
    context: _Context, step_id: str, *, kind: str
) -> tuple[_Mapping[str, _Any], dict[str, str]]:
    if step_id in context.captures:
        return context.captures[step_id]
    filename = _CAPTURE_FILES[step_id]
    path = context.custody_pack_root / _INPUT_DIRECTORY / filename
    try:
        value, identity, _raw = _canonical_object(
            path, kind=kind, label=f"{step_id} command capture"
        )
    except T0EvidenceAuthoringError as exc:
        raise _refuse(
            kind,
            _RUNBOOK_ARTIFACT_REASON_CODES[
                f"{step_id.replace('-', '_')}_capture"
            ],
            str(exc),
        ) from exc
    if set(value) != _CAPTURE_KEYS or value.get("schema_version") != _COMMAND_SCHEMA:
        raise _underivable(kind, f"{step_id} command capture schema/keys are invalid")
    if value.get("step_id") != step_id:
        raise _underivable(kind, f"{step_id} command capture names a different step")
    argv = value.get("argv")
    if (
        not isinstance(argv, list)
        or not argv
        or any(not isinstance(item, str) or not item for item in argv)
        or not isinstance(value.get("cwd"), str)
        or not _Path(value["cwd"]).is_absolute()
        or not isinstance(value.get("exit_code"), int)
        or isinstance(value.get("exit_code"), bool)
        or not isinstance(value.get("stdout"), str)
        or not isinstance(value.get("stderr"), str)
        or not isinstance(value.get("started_monotonic_ns"), int)
        or not isinstance(value.get("finished_monotonic_ns"), int)
        or value["started_monotonic_ns"] < 1
        or value["finished_monotonic_ns"] < value["started_monotonic_ns"]
        or value.get("boot_session_id") != context.boot_session_id
    ):
        raise _underivable(kind, f"{step_id} command capture fields are invalid or stale")
    now = context.clock.monotonic_ns()
    if (
        value["finished_monotonic_ns"] > now
        or now - value["finished_monotonic_ns"] > _MAX_T0_SEQUENCE_AGE_NS
    ):
        raise _underivable(kind, f"{step_id} command capture is not a live T-0 artifact")
    result = (value, identity)
    context.captures[step_id] = result
    return result


@_dataclass(frozen=True)
class _ReferenceAgreement:
    server_count: int
    midpoint: _Decimal
    bound: _Decimal


def _real_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _clock_reference_capture_argv(context: _Context) -> list[str]:
    return [
        str(context.repository / ".venv/bin/python"),
        str(context.repository / "scripts/collect_clock_reference.py"),
    ]


def _validate_reference_object(
    value: object,
    *,
    kind: str,
    label: str,
    boot_session_id: str,
) -> list[tuple[str, _clock_reference.ParsedSntpLine]]:
    if (
        not isinstance(value, _Mapping)
        or set(value) != _CLOCK_REFERENCE_KEYS
        or value.get("schema_version") != _clock_reference.SCHEMA_VERSION
        or value.get("sample_policy_id") != _clock_reference.SAMPLE_POLICY_ID
        or value.get("boot_session_id") != boot_session_id
    ):
        raise _underivable(
            kind, f"{label} schema, sample policy, or boot binding is invalid"
        )
    integer_names = (
        "anchor_realtime_ns",
        "anchor_monotonic_raw_ns",
        "anchor_read_skew_ns",
        "batch_started_monotonic_raw_ns",
        "batch_finished_monotonic_raw_ns",
    )
    if any(not _real_int(value.get(name)) for name in integer_names):
        raise _underivable(kind, f"{label} numeric endpoint is not an integer")
    if not (
        value["anchor_read_skew_ns"] >= 0
        and value["anchor_monotonic_raw_ns"]
        <= value["batch_started_monotonic_raw_ns"]
        <= value["batch_finished_monotonic_raw_ns"]
    ):
        raise _underivable(kind, f"{label} RAW endpoint ordering is invalid")
    samples = value.get("samples")
    if not isinstance(samples, list) or len(samples) != len(
        _clock_reference.SERVER_ROSTER
    ):
        raise _underivable(
            kind, f"{label} does not prove the fixed roster and one-attempt policy"
        )
    parsed_legs: list[tuple[str, _clock_reference.ParsedSntpLine]] = []
    previous_finish = value["batch_started_monotonic_raw_ns"]
    for server, sample in zip(_clock_reference.SERVER_ROSTER, samples):
        if (
            not isinstance(sample, _Mapping)
            or set(sample) != _CLOCK_REFERENCE_SAMPLE_KEYS
            or sample.get("server") != server
            or sample.get("argv") != _clock_reference.build_sntp_argv(server)
        ):
            raise _underivable(
                kind, f"{label} does not prove the fixed roster and one-attempt policy"
            )
        if any(
            not _real_int(sample.get(name))
            for name in (
                "exit_code",
                "started_monotonic_raw_ns",
                "finished_monotonic_raw_ns",
            )
        ):
            raise _underivable(kind, f"{label} leg endpoint is not an integer")
        if (
            not isinstance(sample.get("stdout"), str)
            or not isinstance(sample.get("stderr"), str)
            or not isinstance(sample.get("parsed"), bool)
            or not previous_finish <= sample["started_monotonic_raw_ns"]
            <= sample["finished_monotonic_raw_ns"]
            <= value["batch_finished_monotonic_raw_ns"]
        ):
            raise _underivable(kind, f"{label} leg fields or ordering are invalid")
        previous_finish = sample["finished_monotonic_raw_ns"]
        # The JSON float values are reader aids.  Evidence arithmetic always
        # reparses raw_line/stdout so Decimal retains the exact measured text.
        parsed = (
            _clock_reference.parse_sntp_stdout(sample["stdout"], server=server)
            if sample["exit_code"] == 0
            else None
        )
        if parsed is None:
            if sample["parsed"] is not False or any(
                sample.get(name) is not None
                for name in (
                    "offset_s",
                    "uncertainty_s",
                    "peer_address",
                    "raw_line",
                )
            ):
                raise _underivable(kind, f"{label} unparseable leg fields disagree")
            continue
        if (
            sample["parsed"] is not True
            or not isinstance(sample.get("offset_s"), float)
            or not isinstance(sample.get("uncertainty_s"), float)
            or sample["offset_s"] != float(parsed.offset_s)
            or sample["uncertainty_s"] != float(parsed.uncertainty_s)
        ):
            raise _underivable(
                kind, f"{label} parseable leg omits or alters its numeric fields"
            )
        if sample.get("peer_address") != parsed.peer_address:
            raise _underivable(kind, f"{label} parseable leg alters its peer address")
        if sample.get("raw_line") != parsed.raw_line:
            raise _underivable(kind, f"{label} parseable leg alters its raw line")
        parsed_legs.append((server, parsed))
    return parsed_legs


def _reference_agreement(
    legs: _Sequence[tuple[str, _clock_reference.ParsedSntpLine]],
    *,
    kind: str,
    label: str,
) -> _ReferenceAgreement:
    if len(legs) < 2:
        raise _underivable(kind, f"{label} quorum has fewer than two parseable legs")
    lower = max(parsed.offset_s - parsed.uncertainty_s for _server, parsed in legs)
    upper = min(parsed.offset_s + parsed.uncertainty_s for _server, parsed in legs)
    if lower > upper:
        raise _underivable(kind, f"{label} agreement intervals have empty intersection")
    midpoint = (lower + upper) / _Decimal(2)
    halfwidth = (upper - lower) / _Decimal(2)
    bound = abs(midpoint) + halfwidth
    if bound > _Decimal("0.5"):
        raise _underivable(kind, f"{label} bound exceeds 0.5 seconds")
    return _ReferenceAgreement(len(legs), midpoint, bound)


def _captured_clock_reference(
    context: _Context, *, kind: str
) -> tuple[_Mapping[str, _Any], dict[str, str], _ReferenceAgreement]:
    cached = context.values.get("clock_reference")
    if cached is not None:
        return cached
    capture, identity = _capture(context, "clock-reference", kind=kind)
    _capture_ok(capture, kind=kind, label="R0 clock-reference capture")
    if capture["argv"] != _clock_reference_capture_argv(context):
        raise _underivable(
            kind, "R0 clock reference does not prove the fixed collector invocation"
        )
    try:
        value = _readiness.parse_json_bytes(
            capture["stdout"].encode("utf-8"), require_canonical=True
        )
    except (UnicodeError, _readiness.ArmReadinessError) as exc:
        raise _underivable(kind, f"R0 clock reference stdout is not canonical: {exc}") from exc
    legs = _validate_reference_object(
        value,
        kind=kind,
        label="R0 clock reference",
        boot_session_id=context.boot_session_id,
    )
    if value["anchor_read_skew_ns"] > 1_000_000:
        raise _underivable(kind, "R0 anchor read skew exceeds 1000000 ns")
    agreement = _reference_agreement(legs, kind=kind, label="R0 reference")
    result = (value, identity, agreement)
    context.values["clock_reference"] = result
    return result


def _arm_context(
    context: _Context, *, kind: str
) -> tuple[_Mapping[str, _Any], dict[str, str]]:
    cached = context.values.get("arm_context")
    if cached is not None:
        return cached
    path = context.custody_pack_root / _INPUT_DIRECTORY / "arm-context.json"
    try:
        value, identity, _raw = _canonical_object(path, kind=kind, label="arm-context input")
        validated = _readiness.validate_arm_context(value)
    except (T0EvidenceAuthoringError, _readiness.ArmReadinessError) as exc:
        raise _refuse(
            kind,
            "evidence_author_t0_arm_context_missing",
            f"arm-context input is unavailable or invalid: {exc}",
        ) from exc
    result = (validated, identity)
    context.values["arm_context"] = result
    return result


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


def _parse_window_environment(raw: bytes, *, kind: str) -> dict[str, str]:
    try:
        return parse_window_environment(raw)
    except WindowEnvironmentParseError as exc:
        raise _underivable(kind, exc.detail) from exc


def _launch_manifest(
    context: _Context, *, kind: str
) -> tuple[_Mapping[str, _Any], tuple[dict[str, str], ...], dict[str, str]]:
    cached = context.values.get("launch_manifest")
    if cached is not None:
        return cached
    path = context.custody_pack_root / _INPUT_DIRECTORY / "launch-manifest.json"
    try:
        value, manifest_identity, _raw = _canonical_object(
            path, kind=kind, label="launch manifest"
        )
    except T0EvidenceAuthoringError as exc:
        raise _refuse(
            kind,
            "evidence_author_t0_launch_manifest_missing",
            str(exc),
        ) from exc
    if set(value) != _LAUNCH_KEYS or value.get("schema_version") != _LAUNCH_SCHEMA:
        raise _underivable(kind, "launch manifest schema/keys are invalid")
    if value.get("boot_session_id") != context.boot_session_id:
        raise _underivable(kind, "launch manifest belongs to another boot session")
    root_value = value.get("window_plan_root")
    prewindow = value.get("prewindow_command")
    launch = value.get("launch_command")
    if (
        not isinstance(root_value, str)
        or not _Path(root_value).is_absolute()
        or not isinstance(prewindow, list)
        or not prewindow
        or any(not isinstance(item, str) or not item for item in prewindow)
        or not isinstance(launch, list)
        or not launch
        or any(not isinstance(item, str) or not item for item in launch)
    ):
        raise _underivable(kind, "launch manifest command/path fields are invalid")
    window_root = _Path(root_value)
    try:
        resolved_window = window_root.resolve(strict=True)
        resolved_window.relative_to(context.custody_root)
    except (OSError, ValueError) as exc:
        raise _underivable(kind, "window plan root is not inside the D-134 custody root") from exc
    env_path = resolved_window / "window.env"
    chain_path = resolved_window / "window-chain.zsh"
    try:
        env_identity, env_raw = _input_identity(
            env_path, kind=kind, label="window.env"
        )
    except T0EvidenceAuthoringError as exc:
        raise _missing_artifact(kind, "window_environment", str(exc)) from exc
    try:
        chain_identity, chain_raw = _input_identity(
            chain_path, kind=kind, label="window-chain.zsh"
        )
    except T0EvidenceAuthoringError as exc:
        raise _missing_artifact(kind, "window_chain", str(exc)) from exc
    assignments = _parse_window_environment(env_raw, kind=kind)
    arm, arm_identity = _arm_context(context, kind=kind)
    expected_env = {
        "PACK_ROOT": str(context.pack_root),
        "RUNS_ROOT": str(arm["claim_runs_root"]),
        "BOUND_RUNS_ROOT": str(arm["bound_runs_root"]),
        "CUSTODY_ROOT": str(arm["custody_root"]),
        "QUARANTINE_ROOT": str(arm["quarantine_root"]),
        "CLAIM_BACKUP_DEST": str(arm["claim_backup_destination"]),
        "BOUND_BACKUP_DEST": str(arm["bound_backup_destination"]),
        "BRACKET_SESSION_ID": str(arm["bracket_session_id"]),
        "PRE_ATTEMPT_ID": str(arm["pre_attempt_id"]),
        "POST_ATTEMPT_ID": str(arm["post_attempt_id"]),
        "POWER_POLICY": _frozen_power_policy(context, kind=kind),
    }
    if any(assignments.get(name) != expected for name, expected in expected_env.items()):
        raise _underivable(kind, "window.env differs from pack/arm-context bindings")
    try:
        chain_text = chain_raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise _underivable(kind, "window-chain.zsh is not UTF-8") from exc
    repo_matches = _re.findall(r"(?m)^REPO=(?:\"([^\"]+)\"|'([^']+)'|([^\s]+))$", chain_text)
    repo_values = [next(item for item in match if item) for match in repo_matches]
    if repo_values != [str(context.repository)]:
        raise _underivable(kind, "window-chain.zsh does not bind exactly the reviewed repository")
    if _re.search(r"(?m)^QUARANTINE_ROOT=", chain_text):
        raise _underivable(kind, "window-chain.zsh overrides the sibling quarantine binding")
    expected_prewindow_script = context.repository / "scripts/prewindow_check.sh"
    readiness_attachment = context.tree.get("arm_attachments", {}).get(
        "arm_readiness", {}
    )
    registry_reference = (
        readiness_attachment.get("row_registry")
        if isinstance(readiness_attachment, _Mapping)
        else None
    )
    profile = (
        registry_reference.get("plan_profile")
        if isinstance(registry_reference, _Mapping)
        else None
    )
    expected_prewindow = [
        "/bin/bash",
        str(expected_prewindow_script),
        "--wait",
        "--timeout-min",
        "45",
        "--window",
        str(profile).lower(),
    ]
    if (
        len(prewindow) != len(expected_prewindow)
        or _Path(prewindow[0]).name != "bash"
        or prewindow[1:] != expected_prewindow[1:]
    ):
        raise _underivable(
            kind,
            "prewindow command is not the reviewed 45-minute profile-bound literal",
        )
    if (
        len(launch) != 5
        or _Path(launch[0]).name != "caffeinate"
        or launch[1] != "-is"
        or launch[2] != "/bin/zsh"
        or _Path(launch[3]).resolve() != chain_path.resolve()
        or _Path(launch[4]).resolve() != resolved_window
    ):
        raise _underivable(kind, "launch command is not the exact foreground single-launch recipe")
    artifacts = (manifest_identity, env_identity, chain_identity, arm_identity)
    result = (value, artifacts, assignments)
    context.values["launch_manifest"] = result
    return result


def _required_rows(context: _Context) -> list[_Mapping[str, _Any]]:
    registry, _raw, reference = _readiness._registry_reference(context.pack_root)
    rows = _readiness._profile_rows(registry, reference["plan_profile"], phase="arm")
    selected = [
        row
        for row in rows
        if row["evaluation_phase"] == "ARM_ONLY"
        and row["row_id"] not in _INTERNAL_ROWS
        and _readiness.applicability_for_row(
            row, clock_route="MANUAL", successor_acceptance=False
        )
        == "REQUIRED"
    ]
    if tuple(row["row_id"] for row in selected) != _EXPECTED_ROWS:
        raise _refuse(
            "AUTHORING_SET",
            "evidence_author_t0_row_census_mismatch",
            "ARM_ONLY evidence row census differs from the ratified fifteen-row set",
        )
    if any(row["required_evidence_kinds"] != [_ROW_KIND[row["row_id"]]] for row in selected):
        raise _refuse(
            "AUTHORING_SET",
            "evidence_author_t0_row_census_mismatch",
            "ARM_ONLY evidence-kind mapping differs from the ratified registry",
        )
    return selected


def _frozen_power_policy(context: _Context, *, kind: str) -> str:
    cached = context.values.get("power_policy")
    if cached is not None:
        return cached
    policies: set[str] = set()
    for stage in context.tree.get("stage_graph", []):
        commands = stage.get("launch", {}).get("commands", []) if isinstance(stage, _Mapping) else []
        for command in commands:
            arguments = command.get("argv_template", {}).get("arguments", []) if isinstance(command, _Mapping) else []
            for index, item in enumerate(arguments[:-1]):
                if isinstance(item, _Mapping) and item.get("value") in {"--power-policy", "--instrument-power-policy"}:
                    following = arguments[index + 1]
                    if isinstance(following, _Mapping) and following.get("kind") == "literal" and isinstance(following.get("value"), str):
                        policies.add(following["value"])
    if policies != {"ac_high_power"}:
        raise _underivable(kind, f"frozen power policy is missing or ambiguous: {sorted(policies)!r}")
    context.values["power_policy"] = "ac_high_power"
    return "ac_high_power"


def _root_observation(context: _Context, *, kind: str) -> tuple[dict[str, _Any], dict[str, str]]:
    cached = context.values.get("root_observation")
    if cached is not None:
        return cached
    arm, arm_identity = _arm_context(context, kind=kind)
    names = ("claim_runs_root", "bound_runs_root", "custody_root", "quarantine_root")
    paths = [_Path(str(arm[name])) for name in names]
    if any(not path.is_absolute() for path in paths):
        raise _underivable(kind, "arm roots are not absolute")
    try:
        resolved = [path.resolve(strict=True) for path in paths]
    except OSError as exc:
        raise _underivable(kind, f"arm root is absent: {exc}") from exc
    if len(set(resolved)) != len(resolved) or any(not path.is_dir() for path in paths):
        raise _underivable(kind, "arm roots are not distinct directories")
    try:
        if any(any(path.iterdir()) for path in paths):
            raise _underivable(kind, "arm root is not empty")
    except OSError as exc:
        raise _underivable(kind, f"arm root cannot be inspected: {exc}") from exc
    roots = context.tree.get("roots")
    if (
        not isinstance(roots, _Mapping)
        or paths[0].name != roots.get("claim_root_leaf")
        or paths[1].name != roots.get("bound_root_leaf")
    ):
        raise _underivable(kind, "arm roots do not derive from frozen leaves")
    waiver_path = _Path(str(arm["waiver_path"]))
    try:
        waiver_identity, waiver_raw = _input_identity(
            waiver_path, kind=kind, label="waiver input"
        )
    except T0EvidenceAuthoringError as exc:
        raise _missing_artifact(kind, "waiver_record", str(exc)) from exc
    try:
        waivers = _readiness.parse_json_bytes(waiver_raw, require_canonical=True)
    except _readiness.ArmReadinessError as exc:
        raise _underivable(kind, f"waiver input is invalid: {exc}") from exc
    if waivers != []:
        raise _underivable(kind, "waiver input is not exactly an empty array")
    locks = [path / "campaign.lock" for path in paths[:2]]
    for lock in locks:
        try:
            lock.lstat()
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise _underivable(kind, f"campaign lock is unreadable: {lock}: {exc}") from exc
        raise _underivable(kind, f"campaign lock exists: {lock}")
    observation = {
        "arm_context": _copy.deepcopy(dict(arm)),
        "resolved_roots": [str(path) for path in resolved],
        "waiver_bytes_decoded": [],
        "campaign_locks": [str(path) for path in locks],
    }
    result = (observation, arm_identity)
    context.values["root_observation"] = result
    context.values["waiver_identity"] = waiver_identity
    return result


def _capture_ok(capture: _Mapping[str, _Any], *, kind: str, label: str) -> None:
    if capture["exit_code"] != 0:
        raise _underivable(kind, f"{label} exited {capture['exit_code']}")


def _systemsetup_argv(argv: _Sequence[str], operation: _Sequence[str]) -> bool:
    try:
        system_index = next(index for index, item in enumerate(argv) if _Path(item).name == "systemsetup")
    except StopIteration:
        return False
    return list(argv[system_index + 1 :]) == list(operation) and any(
        _Path(item).name == "sudo" for item in argv[:system_index]
    )


def _sample_anchor(
    context: _Context, *, kind: str, label: str
) -> _clock_reference.ClockAnchor:
    try:
        anchor = context.clock.sample_anchor()
    except Exception as exc:
        raise _underivable(kind, f"{label} could not be sampled: {exc}") from exc
    if any(
        not _real_int(value)
        for value in (
            anchor.realtime_ns,
            anchor.monotonic_raw_ns,
            anchor.read_skew_ns,
        )
    ) or anchor.read_skew_ns < 0:
        raise _underivable(kind, f"{label} endpoints are invalid")
    return anchor


def _fresh_clock_reference_batch(
    context: _Context, *, kind: str
) -> tuple[
    _ReferenceAgreement,
    tuple[_ProbeResult, ...],
    int,
    _clock_reference.ClockAnchor,
    int,
]:
    r1_started_monotonic_ns = context.clock.monotonic_ns()
    context.values["r1_batch_started_monotonic_ns"] = r1_started_monotonic_ns
    started_anchor = _sample_anchor(context, kind=kind, label="R1 batch start")
    probes: list[_ProbeResult] = []
    legs: list[tuple[str, _clock_reference.ParsedSntpLine]] = []
    for server in _clock_reference.SERVER_ROSTER:
        argv = tuple(_clock_reference.build_sntp_argv(server))
        probe = _fresh_probe(context, kind, f"R1 {server}", argv)
        probes.append(probe)
        if probe.argv != argv:
            raise _underivable(
                kind, "R1 clock reference does not prove the fixed one-attempt roster"
            )
        parsed = (
            _clock_reference.parse_sntp_stdout(probe.stdout, server=server)
            if probe.exit_code == 0
            else None
        )
        if parsed is not None:
            legs.append((server, parsed))
    finished_anchor = _sample_anchor(context, kind=kind, label="author anchor")
    r1_finished_monotonic_ns = context.clock.monotonic_ns()
    duration = finished_anchor.monotonic_raw_ns - started_anchor.monotonic_raw_ns
    if not 0 <= duration <= 30_000_000_000:
        raise _underivable(kind, "R1 batch duration is outside 0 through 30000000000 ns")
    agreement = _reference_agreement(legs, kind=kind, label="R1 reference")
    context.values["r1_batch_finished_monotonic_ns"] = r1_finished_monotonic_ns
    return (
        agreement,
        tuple(probes),
        started_anchor.monotonic_raw_ns,
        finished_anchor,
        r1_finished_monotonic_ns,
    )


def _derive_clock_attestation(context: _Context) -> _DerivedRow:
    kind = "CLOCK_ATTESTATION"
    r0, r0_identity, _r0_agreement = _captured_clock_reference(
        context, kind=kind
    )
    disable, disable_identity = _capture(context, "clock-disable", kind=kind)
    _capture_ok(disable, kind=kind, label="network-time disable capture")
    if not _systemsetup_argv(disable["argv"], ("-setusingnetworktime", "off")):
        raise _underivable(kind, "network-time disable capture used the wrong command")
    if not (
        r0["batch_finished_monotonic_raw_ns"]
        >= r0["anchor_monotonic_raw_ns"]
        and context.captures["clock-reference"][0]["finished_monotonic_ns"]
        <= disable["started_monotonic_ns"]
    ):
        raise _underivable(kind, "R0 did not complete before the first clock-disable action")
    (
        r1_agreement,
        r1_probes,
        r1_started_raw,
        author_anchor,
        r1_finished_monotonic_ns,
    ) = _fresh_clock_reference_batch(context, kind=kind)
    r1_started_monotonic_ns = context.values.get("r1_batch_started_monotonic_ns")
    # ``_fresh_clock_reference_batch`` samples its ordinary start before any
    # network probe.  Record it only for the same-clock capture-order proof;
    # the governed value publishes the RAW endpoint used for duration.
    if r1_started_monotonic_ns is None:
        r1_started_monotonic_ns = context.clock.monotonic_ns()
    if disable["finished_monotonic_ns"] > r1_started_monotonic_ns:
        raise _underivable(kind, "clock-disable did not finish before the R1 batch")
    span = author_anchor.monotonic_raw_ns - r0["anchor_monotonic_raw_ns"]
    if span < _MIN_IDLE_NS:
        raise _underivable(kind, "T-0 RAW anchor span is below 600000000000 ns")
    if span > _MAX_T0_SEQUENCE_AGE_NS:
        raise _underivable(kind, "T-0 RAW anchor span exceeds 3600000000000 ns")
    anchor_delta = abs(
        (author_anchor.realtime_ns - author_anchor.monotonic_raw_ns)
        - (r0["anchor_realtime_ns"] - r0["anchor_monotonic_raw_ns"])
    )
    if anchor_delta > 5_000_000:
        raise _underivable(kind, "R0-to-author RAW anchor delta exceeds 5000000 ns")
    if author_anchor.read_skew_ns > 1_000_000:
        raise _underivable(kind, "author anchor read skew exceeds 1000000 ns")
    r1_finished_raw = author_anchor.monotonic_raw_ns
    r1_duration = r1_finished_raw - r1_started_raw
    value = {
        "independent_clock_attestation": True,
        "reference_quorum_satisfied": True,
        "absolute_offset_within_ceiling": True,
        # True means no adjustment above the 5 ms ceiling was detected between
        # the reference sample and authoring; it does not assert that the clock
        # is disciplined.
        "unstepped_across_t0_sequence": True,
        "sample_policy_id": _clock_reference.SAMPLE_POLICY_ID,
        "reference_server_count": r1_agreement.server_count,
        "reference_bound_seconds": float(r1_agreement.bound),
        "comparison_delta_seconds": float(r1_agreement.midpoint),
        "r0_anchor_realtime_ns": r0["anchor_realtime_ns"],
        "r0_anchor_monotonic_raw_ns": r0["anchor_monotonic_raw_ns"],
        "r0_anchor_read_skew_ns": r0["anchor_read_skew_ns"],
        "anchor_realtime_ns": author_anchor.realtime_ns,
        "anchor_monotonic_raw_ns": author_anchor.monotonic_raw_ns,
        "anchor_read_skew_ns": author_anchor.read_skew_ns,
        "anchor_delta_ns": anchor_delta,
        "t0_span_ns": span,
        "r1_batch_started_monotonic_raw_ns": r1_started_raw,
        "r1_batch_finished_monotonic_raw_ns": r1_finished_raw,
        "r1_batch_duration_ns": r1_duration,
        "r1_batch_finished_monotonic_ns": r1_finished_monotonic_ns,
    }
    return _DerivedRow(
        "clock.correct_and_prior_state",
        kind,
        value,
        "PROBE",
        input_artifacts=(r0_identity, disable_identity),
        probes=r1_probes,
        derivation={"sample_policy_id": _clock_reference.SAMPLE_POLICY_ID},
    )


def _derive_clock_probe(context: _Context) -> _DerivedRow:
    kind = "CLOCK_PROBE"
    disable, disable_identity = _capture(context, "clock-disable", kind=kind)
    _capture_ok(disable, kind=kind, label="network-time disable capture")
    probe = _fresh_probe(
        context,
        kind,
        "network-time off enforcement",
        (
            "/usr/bin/sudo",
            "-n",
            "/usr/sbin/systemsetup",
            "-setusingnetworktime",
            "off",
        ),
    )
    if probe.exit_code != 0:
        raise _underivable(
            kind, "fresh D-127 enforcement exited nonzero before setting Off"
        )
    if probe.stdout != _readiness.EXPECTED_NETWORK_TIME_OFF_STDOUT:
        raise _underivable(
            kind, "fresh D-127 enforcement stdout did not exactly report Off"
        )
    return _DerivedRow(
        "clock.network_time_off",
        kind,
        {"fresh_probe": True, "network_time": "off"},
        "PROBE",
        input_artifacts=(disable_identity,),
        probes=(probe,),
    )


def _git_message(context: _Context) -> str:
    value = _readiness._git_text(context.repository, "show", "-s", "--format=%B", "HEAD")
    if value is None:
        raise _underivable("TERMINAL_REVIEW", "HEAD commit message is unreadable")
    return value


def _derive_terminal_review(context: _Context) -> _DerivedRow:
    kind = "TERMINAL_REVIEW"
    message = _git_message(context)
    trailers: dict[str, list[str]] = {}
    for line in message.splitlines():
        match = _re.fullmatch(r"(JouleWise-Terminal-Review(?:-Tree-Oid|-Pack-Sha256)?):\s*(\S+)", line)
        if match:
            trailers.setdefault(match.group(1), []).append(match.group(2))
    expected_exact = {
        "JouleWise-Terminal-Review": "PASS",
        "JouleWise-Terminal-Review-Tree-Oid": context.head_tree_oid,
    }
    packs = trailers.get("JouleWise-Terminal-Review-Pack-Sha256", [])
    # An empty Pack-Sha256 list refuses via the membership clause below.
    if (
        any(
            trailers.get(name) != [value]
            for name, value in expected_exact.items()
        )
        or any(_SHA_RE.fullmatch(pack) is None for pack in packs)
        or len(set(packs)) != len(packs)
        or context.pack_sha256 not in packs
    ):
        raise _refuse(
            kind,
            "evidence_author_t0_terminal_review_record_missing",
            "HEAD commit lacks exact PASS/tree and valid pack-membership terminal-review trailers",
        )
    primary = tuple(
        _committed_artifact(context.repository, relative, kind=kind)[0]
        for relative in _AUTHORING_ARTIFACTS
    )
    return _DerivedRow(
        "desk.terminal_review",
        kind,
        {"same_head_tree": True, "same_pack_digest": True, "terminal_review_status": "PASS"},
        "GIT",
        primary_artifacts=primary,
        derivation={"commit_message_sha256": _readiness.sha256_bytes(message.encode("utf-8"))},
    )


def _prewindow_capture(
    context: _Context, *, kind: str
) -> tuple[_Mapping[str, _Any], dict[str, str], tuple[dict[str, str], ...]]:
    capture, identity = _capture(context, "prewindow-check", kind=kind)
    manifest, artifacts, _assignments = _launch_manifest(context, kind=kind)
    _capture_ok(capture, kind=kind, label="prewindow readiness wait")
    if capture["argv"] != manifest["prewindow_command"]:
        raise _underivable(kind, "prewindow capture differs from the frozen command")
    if capture["finished_monotonic_ns"] - capture["started_monotonic_ns"] < _MIN_IDLE_NS:
        raise _underivable(kind, "prewindow capture does not prove the required ten-minute idle")
    if "TIMED OUT" in capture["stdout"] or "BLOCK" in capture["stdout"] or _re.search(
        r"READY after [0-9]+ min\.", capture["stdout"]
    ) is None:
        raise _underivable(kind, "prewindow capture does not end in READY")
    return capture, identity, artifacts


def _expect_absent(result: _ProbeResult, *, kind: str, label: str) -> None:
    if result.exit_code != 1 or result.stdout.strip():
        raise _underivable(kind, f"fresh {label} census found a forbidden process")


def _maintenance_probe(context: _Context, *, kind: str) -> _ProbeResult:
    probe = _fresh_probe(
        context,
        kind,
        "maintenance",
        (
            "/usr/bin/pgrep",
            "-lf",
            "XProtect|mds_stores|mdworker|mdbulkimport|backupd|photoanalysisd|softwareupdated|Spotlight|mediaanalysisd",
        ),
    )
    _expect_absent(probe, kind=kind, label="maintenance")
    return probe


def _derive_background_quiet(context: _Context) -> _DerivedRow:
    kind = "MAINTENANCE_CENSUS"
    _prewindow, prewindow_identity, manifest_artifacts = _prewindow_capture(context, kind=kind)
    probe = _maintenance_probe(context, kind=kind)
    return _DerivedRow(
        "t0.background_quiet",
        kind,
        {"observation_status": "PASS", "fresh_maintenance_census": True},
        "PROBE",
        input_artifacts=(prewindow_identity, *manifest_artifacts),
        probes=(probe,),
    )


def _derive_campaign_lock(context: _Context) -> _DerivedRow:
    kind = "ROOT_PREFLIGHT"
    observation, arm_identity = _root_observation(context, kind=kind)
    return _DerivedRow(
        "t0.campaign_lock_absent",
        kind,
        {
            "fresh_root_receipt": True,
            "live_lock_absent": True,
            "stale_lock_absent": True,
            "unreadable_lock_absent": True,
        },
        "PROBE",
        input_artifacts=(arm_identity,),
        derivation={"campaign_locks": observation["campaign_locks"]},
    )


def _thermal_probe(context: _Context, *, kind: str) -> _ProbeResult:
    probe = _fresh_probe(context, kind, "thermal", ("/usr/bin/pmset", "-g", "therm"))
    if probe.exit_code != 0:
        raise _underivable(kind, "fresh thermal probe refused")
    required_nominal = (
        "No thermal warning level has been recorded",
        "No performance warning level has been recorded",
    )
    limits = [int(value) for value in _re.findall(r"(?:CPU|GPU)_Speed_Limit\s*=\s*([0-9]+)", probe.stdout)]
    if (
        any(item not in probe.stdout for item in required_nominal)
        or any(value < 100 for value in limits)
        or _re.search(r"thermal warning.*(?:serious|critical)", probe.stdout, _re.I)
    ):
        raise _underivable(kind, "fresh thermal probe is not nominal")
    return probe


def _quiet_capture(context: _Context, *, kind: str) -> tuple[_Mapping[str, _Any], dict[str, str]]:
    capture, identity = _capture(context, "quiet-mac-prep", kind=kind)
    _capture_ok(capture, kind=kind, label="quiet-Mac preparation")
    expected = ["/bin/bash", str(context.repository / "scripts/quiet_mac_prep.sh")]
    if capture["argv"] != expected or _Path(capture["cwd"]).resolve() != context.repository:
        raise _underivable(kind, "quiet-Mac capture did not execute the reviewed script")
    required = (
        "OK: passwordless powermetrics works.",
        "OK: display verification reports all online displays asleep.",
        "OK: post-arm evidence reports screensaver disengaged.",
    )
    if "FAIL:" in capture["stdout"] or any(item not in capture["stdout"] for item in required):
        raise _underivable(kind, "quiet-Mac capture contains a failed/missing predicate")
    return capture, identity


def _derive_display_idle(context: _Context) -> _DerivedRow:
    kind = "MACHINE_PREFLIGHT"
    _quiet, quiet_identity = _quiet_capture(context, kind=kind)
    _prewindow, prewindow_identity, manifest_artifacts = _prewindow_capture(context, kind=kind)
    thermal = _thermal_probe(context, kind=kind)
    return _DerivedRow(
        "t0.display_thermal_idle",
        kind,
        {
            "display_predicate": True,
            "idle_predicate": True,
            "prewindow_check_wait_status": "PASS",
            "quiet_mac_prep_status": "PASS",
            "screensaver_predicate": True,
            "thermal_predicate": True,
        },
        "PROBE",
        input_artifacts=(quiet_identity, prewindow_identity, *manifest_artifacts),
        probes=(thermal,),
    )


def _derive_fresh_roots(context: _Context) -> _DerivedRow:
    kind = "ROOT_PREFLIGHT"
    _observation, arm_identity = _root_observation(context, kind=kind)
    waiver_identity = context.values["waiver_identity"]
    return _DerivedRow(
        "t0.fresh_roots_waivers",
        kind,
        {
            "roots_absolute": True,
            "roots_derived_from_frozen_leaves_and_arm_context": True,
            "roots_distinct": True,
            "roots_empty": True,
            "waiver_bytes_decoded": [],
        },
        "PROBE",
        input_artifacts=(arm_identity, waiver_identity),
    )


def _argv_flags(argv: _Sequence[str], *, valueless: frozenset[str]) -> dict[str, str | bool]:
    result: dict[str, str | bool] = {}
    index = 0
    while index < len(argv):
        item = argv[index]
        if not item.startswith("--"):
            index += 1
            continue
        if item in result:
            raise ValueError(f"duplicate option {item}")
        if item in valueless:
            result[item] = True
            index += 1
        else:
            if index + 1 >= len(argv) or argv[index + 1].startswith("--"):
                raise ValueError(f"missing value for {item}")
            result[item] = argv[index + 1]
            index += 2
    return result


def _json_stdout(capture: _Mapping[str, _Any], *, kind: str, label: str) -> _Mapping[str, _Any]:
    try:
        value = _json.loads(capture["stdout"])
    except (TypeError, _json.JSONDecodeError) as exc:
        raise _underivable(kind, f"{label} stdout is not one JSON object") from exc
    if not isinstance(value, _Mapping):
        raise _underivable(kind, f"{label} stdout is not one JSON object")
    return value


def _frozen_plan(
    context: _Context, *, kind: str
) -> tuple[_Path, str, str, bytes]:
    cached = context.values.get("frozen_plan")
    if cached is not None:
        return cached
    try:
        result = _readiness.resolve_frozen_plan(context.pack_root, context.tree)
    except _readiness.ArmReadinessError as exc:
        raise _underivable(kind, f"R2 frozen-plan reference is invalid: {exc}") from exc
    context.values["frozen_plan"] = result
    return result


def _derive_ledger(context: _Context) -> _DerivedRow:
    kind = "LEDGER_RESERVATION"
    arm, arm_identity = _arm_context(context, kind=kind)
    plan_path, _plan_relative, plan_id, plan_raw = _frozen_plan(
        context, kind=kind
    )
    diagnostic, diagnostic_identity = _capture(context, "ledger-readiness", kind=kind)
    reservation, reservation_identity = _capture(context, "ledger-reservation", kind=kind)
    _capture_ok(diagnostic, kind=kind, label="ledger diagnostic")
    _capture_ok(reservation, kind=kind, label="ledger reservation")
    diagnostic_value = _json_stdout(diagnostic, kind=kind, label="ledger diagnostic")
    if (
        diagnostic_value.get("status") != "ready"
        or diagnostic_value.get("early_warning_only") is not True
        or not isinstance(diagnostic_value.get("frozen_plan"), _Mapping)
        or diagnostic_value["frozen_plan"].get("path") != str(plan_path)
        or diagnostic_value["frozen_plan"].get("plan_id") != plan_id
        or diagnostic_value["frozen_plan"].get("sha256") != context.plan_sha256
    ):
        raise _underivable(kind, "ledger diagnostic does not bind the ready frozen plan")
    expected_python = str(context.repository / ".venv/bin/python")
    expected_recovery_script = str(
        context.repository / "scripts/recover_calibration_ledger.py"
    )
    expected_diagnostic = [
        expected_python,
        expected_recovery_script,
        "readiness",
        "--phase",
        "pre-reserve",
        "--session-id",
        str(arm["bracket_session_id"]),
        "--plan",
        str(plan_path),
    ]
    if (
        diagnostic["argv"] != expected_diagnostic
        or _Path(diagnostic["cwd"]).resolve() != context.repository
    ):
        raise _underivable(kind, "ledger diagnostic did not execute the reviewed literal")
    try:
        flags = _argv_flags(reservation["argv"], valueless=frozenset({"--execute"}))
    except ValueError as exc:
        raise _underivable(kind, f"reservation argv is malformed: {exc}") from exc
    required = {
        "--session-id": arm["bracket_session_id"],
        "--window-id": context.tree.get("window_identity", {}).get("window_id"),
        "--plan-id": context.tree.get("plan", {}).get("plan_id"),
        "--plan-sha256": context.plan_sha256,
        "--evidence-root-id": context.tree.get("window_identity", {}).get("evidence_root_id"),
        "--runs-root": arm["claim_runs_root"],
        "--pre-attempt-id": arm["pre_attempt_id"],
        "--post-attempt-id": arm["post_attempt_id"],
        "--pre-custody-locator": str(_Path(str(arm["claim_runs_root"])) / "instrument_validation" / str(arm["pre_attempt_id"])),
        "--post-custody-locator": str(_Path(str(arm["claim_runs_root"])) / "instrument_validation" / str(arm["post_attempt_id"])),
        "--execute": True,
    }
    if any(flags.get(name) != value for name, value in required.items()):
        raise _underivable(kind, "reservation argv differs from frozen pack/arm-context bindings")
    allowed = set(required) | {"--ledger", "--head-pin", "--plan", "--identity-epoch-json", "--t1-bindings-json"}
    if set(flags) != allowed:
        raise _underivable(kind, "reservation argv is not the frozen-plus-plan superset")
    script = str(context.repository / "scripts/reserve_calibration_window_bracket.py")
    if (
        reservation["argv"][:2] != [expected_python, script]
        or _Path(reservation["cwd"]).resolve() != context.repository
    ):
        raise _underivable(kind, "reservation did not execute from the reviewed checkout")
    head_pin = _Path(str(flags["--head-pin"]))
    if head_pin.resolve() != (context.repository / "configs/calibration/calibration_ledger_head.json").resolve():
        raise _underivable(kind, "reservation head pin is not the reviewed checkout pin")
    head_pin_identity, _head_pin_raw = _committed_artifact(
        context.repository,
        "configs/calibration/calibration_ledger_head.json",
        kind=kind,
    )
    recovery_identity, _recovery_raw = _committed_artifact(
        context.repository, "scripts/recover_calibration_ledger.py", kind=kind
    )
    reservation_script_identity, _reservation_script_raw = _committed_artifact(
        context.repository,
        "scripts/reserve_calibration_window_bracket.py",
        kind=kind,
    )
    if flags["--plan"] != str(plan_path):
        raise _underivable(kind, "reservation --plan is not the R2 execution literal")
    plan_identity, captured_plan_raw = _input_identity(
        plan_path, kind=kind, label="frozen reservation plan"
    )
    if captured_plan_raw != plan_raw or _readiness.sha256_bytes(plan_raw) != context.plan_sha256:
        raise _underivable(kind, "reservation --plan bytes differ from the pack plan")
    try:
        plan_value = _readiness.parse_json_bytes(plan_raw)
    except _readiness.ArmReadinessError as exc:
        raise _underivable(kind, "reservation --plan is invalid JSON") from exc
    if (
        not isinstance(plan_value, _Mapping)
        or plan_value.get("plan_id") != plan_id
    ):
        raise _underivable(kind, "reservation --plan does not name the frozen plan ID")
    extra_inputs: list[dict[str, str]] = [plan_identity]
    reservation_inputs: dict[str, _Mapping[str, _Any]] = {}
    for option in ("--identity-epoch-json", "--t1-bindings-json"):
        artifact_class = {
            "--identity-epoch-json": "identity_epoch",
            "--t1-bindings-json": "t1_bindings",
        }[option]
        try:
            identity, raw = _input_identity(
                _Path(str(flags[option])), kind=kind, label=option
            )
        except T0EvidenceAuthoringError as exc:
            raise _missing_artifact(kind, artifact_class, str(exc)) from exc
        try:
            value = _readiness.parse_json_bytes(raw)
        except _readiness.ArmReadinessError as exc:
            raise _underivable(kind, f"{option} is invalid JSON") from exc
        if not isinstance(value, _Mapping):
            raise _underivable(kind, f"{option} is not an object")
        reservation_inputs[option] = value
        extra_inputs.append(identity)
    output = _json_stdout(reservation, kind=kind, label="ledger reservation")
    receipt = output.get("receipt")
    if output.get("status") != "reserved" or not isinstance(receipt, _Mapping):
        raise _underivable(kind, "reservation stdout is not status reserved with a receipt")
    receipt_identity = {
        "session_id": arm["bracket_session_id"],
        "window_id": context.tree.get("window_identity", {}).get("window_id"),
        "plan_id": context.tree.get("plan", {}).get("plan_id"),
        "plan_sha256": context.plan_sha256,
        "evidence_root_id": context.tree.get("window_identity", {}).get(
            "evidence_root_id"
        ),
        "runs_root": arm["claim_runs_root"],
    }
    expected_slots = {
        role: {
            "attempt_id": arm[f"{role}_attempt_id"],
            "custody_locator": required[f"--{role}-custody-locator"],
            "identity_epoch": dict(reservation_inputs["--identity-epoch-json"]),
            "t1_bindings": dict(reservation_inputs["--t1-bindings-json"]),
            "expected_time_role": role,
        }
        for role in ("pre", "post")
    }
    if (
        receipt.get("schema_version") != _ledger.BRACKET_SESSION_SCHEMA
        or receipt.get("event") != _ledger.BRACKET_SESSION_OPEN_EVENT
        or any(receipt.get(name) != value for name, value in receipt_identity.items())
        or receipt.get("slots") != expected_slots
        or not _ledger._valid_session_receipt_shape(receipt)
    ):
        raise _underivable(kind, "reservation stdout receipt is not the governed session-open receipt")
    events = []
    for line in reservation["stderr"].splitlines():
        try:
            event = _json.loads(line)
        except _json.JSONDecodeError:
            continue
        if isinstance(event, _Mapping) and event.get("event") == "calibration_pre_reserve_authorized":
            events.append(event["event"])
    if events != ["calibration_pre_reserve_authorized"]:
        raise _underivable(kind, "reservation stderr lacks the unique pre-reserve authorization event")
    ledger_path = _Path(str(flags["--ledger"]))
    try:
        ledger_identity, ledger_raw = _input_identity(
            ledger_path, kind=kind, label="production ledger"
        )
    except T0EvidenceAuthoringError as exc:
        raise _missing_artifact(kind, "production_ledger", str(exc)) from exc
    receipts, reasons = _ledger._parse_ledger(ledger_raw)
    if reasons or not receipts or dict(receipts[-1]) != dict(receipt):
        raise _underivable(kind, f"production ledger does not end in the captured reservation: {sorted(reasons)!r}")
    return _DerivedRow(
        "t0.ledger_reservation",
        kind,
        {
            "diagnostic_status": "PASS",
            "events": ["calibration_pre_reserve_authorized"],
            "execute_mode": True,
            "plan_sha256": context.plan_sha256,
            "status": "reserved",
        },
        "PROBE",
        primary_artifacts=(
            head_pin_identity,
            recovery_identity,
            reservation_script_identity,
        ),
        input_artifacts=(
            arm_identity,
            diagnostic_identity,
            reservation_identity,
            ledger_identity,
            *extra_inputs,
        ),
        derivation={"ledger_sequence": receipt["sequence"], "ledger_receipt_digest": receipt["receipt_digest"]},
    )


def _derive_machine_readiness(context: _Context) -> _DerivedRow:
    kind = "MACHINE_PREFLIGHT"
    plan_path, _plan_relative, plan_id, _plan_raw = _frozen_plan(
        context, kind=kind
    )
    _quiet, quiet_identity = _quiet_capture(context, kind=kind)
    _prewindow, prewindow_identity, manifest_artifacts = _prewindow_capture(context, kind=kind)
    diagnostic, diagnostic_identity = _capture(context, "ledger-readiness", kind=kind)
    _capture_ok(diagnostic, kind=kind, label="ledger diagnostic")
    diagnostic_value = _json_stdout(diagnostic, kind=kind, label="ledger diagnostic")
    if (
        diagnostic_value.get("status") != "ready"
        or diagnostic_value.get("early_warning_only") is not True
        or not isinstance(diagnostic_value.get("frozen_plan"), _Mapping)
        or diagnostic_value["frozen_plan"].get("path") != str(plan_path)
        or diagnostic_value["frozen_plan"].get("plan_id") != plan_id
        or diagnostic_value["frozen_plan"].get("sha256") != context.plan_sha256
    ):
        raise _underivable(kind, "machine readiness does not bind the pack plan")
    _root_observation(context, kind=kind)
    return _DerivedRow(
        "t0.machine_readiness",
        kind,
        {
            "current": True,
            "frozen_prewindow_check_wait_command": True,
            "same_plan": True,
            "same_roots": True,
            "status": "READY",
        },
        "PROBE",
        input_artifacts=(quiet_identity, prewindow_identity, diagnostic_identity, *manifest_artifacts),
        probes=(context.boot_probe,),
    )


def _derive_process_census(context: _Context) -> _DerivedRow:
    kind = "PROCESS_CENSUS"
    probes = (
        _fresh_probe(context, kind, "keep-awake", ("/usr/bin/pgrep", "-x", "caffeinate")),
        _fresh_probe(context, kind, "agent", ("/usr/bin/pgrep", "-lf", "codex|claude|t3")),
        _fresh_probe(context, kind, "browser", ("/usr/bin/pgrep", "-lf", "Safari|Google Chrome|Chromium|Firefox|browser automation")),
        _fresh_probe(context, kind, "monitor", ("/usr/bin/pgrep", "-lf", "powermetrics|window-chain|run_campaign|tail -f|watch")),
    )
    for label, probe in zip(("keep-awake", "agent", "browser", "monitor"), probes, strict=True):
        _expect_absent(probe, kind=kind, label=label)
    return _DerivedRow(
        "t0.no_stray_keepawake",
        kind,
        {"absent_process_classes": ["agent", "browser", "keep_awake", "monitor"], "fresh_process_census": True},
        "PROBE",
        probes=probes,
    )


def _reverify_offline_inputs(context: _Context, *, kind: str) -> tuple[list[dict[str, str]], dict[str, _Any]]:
    primary: list[dict[str, str]] = []
    external = context.tree.get("external_inputs")
    if not isinstance(external, _Mapping):
        raise _underivable(kind, "pack external-input registry is missing")
    pins: list[_Mapping[str, _Any]] = []
    for item in external.get("artifacts", []):
        if isinstance(item, _Mapping):
            pins.append(item)
    for item in external.get("manifests", []):
        if isinstance(item, _Mapping):
            manifest = item.get("manifest")
            if isinstance(manifest, _Mapping):
                pins.append(manifest)
            pins.extend(member for member in item.get("members", []) if isinstance(member, _Mapping))
    for pin in pins:
        path = pin.get("path")
        digest = pin.get("sha256")
        if not isinstance(path, str) or not isinstance(digest, str):
            raise _underivable(kind, "external-input pin is malformed")
        artifact, _raw = _committed_artifact(context.repository, path, kind=kind)
        if artifact["sha256"] != digest:
            raise _underivable(kind, f"external-input pin differs from committed bytes: {path}")
        primary.append(artifact)
    try:
        tree, projection, _producer = _identity._load_pack_projection(context.pack_root)
        frozen, _raw = _identity._load_frozen_receipt(context.pack_root, projection)
        current_units, current_sha, checks = _identity._derive_projection_units(context.pack_root, projection)
    except _identity.IdentityPinProjectionError as exc:
        raise _underivable(kind, f"live U11 input re-derivation refused: {exc.reason_code}") from exc
    if (
        not _identity._frozen_pack_matches_receipt(projection, frozen)
        or not _identity._frozen_pack_identity_matches_receipt(context.pack_root, tree, frozen)
        or current_sha != frozen["pack"]["projection_input_sha256"]
        or [unit["model_runtime_config"] for unit in current_units]
        != [unit["model_runtime_config"] for unit in frozen["identity_units"]]
    ):
        raise _underivable(kind, "live U11 input derivation differs from the frozen projection")
    return primary, {"projection_input_sha256": current_sha, "identity_check_count": len(checks)}


def _derive_offline_inputs(context: _Context) -> _DerivedRow:
    kind = "OFFLINE_INPUT_INVENTORY"
    primary, derivation = _reverify_offline_inputs(context, kind=kind)
    identity_source, _raw = _committed_artifact(context.repository, "joulewise/identity_pins.py", kind=kind)
    primary.append(identity_source)
    return _DerivedRow(
        "t0.offline_inputs",
        kind,
        {
            "file_inventory_matches_frozen_inputs": True,
            "no_network_fetch": True,
            "u11_live_derivation_matches_frozen_inputs": True,
        },
        "PROBE",
        primary_artifacts=tuple(primary),
        derivation=derivation,
    )


def _derive_powermetrics(context: _Context) -> _DerivedRow:
    kind = "POWERMETRICS_PROBE"
    probe = _fresh_probe(
        context,
        kind,
        "passwordless powermetrics",
        ("/usr/bin/sudo", "-n", "/usr/bin/powermetrics", "-i", "200", "-n", "1"),
    )
    if probe.exit_code != 0:
        raise _underivable(kind, "exact reviewed sudo -n powermetrics probe refused")
    script, _raw = _committed_artifact(context.repository, "scripts/quiet_mac_prep.sh", kind=kind)
    return _DerivedRow(
        "t0.passwordless_powermetrics",
        kind,
        {"exact_reviewed_sudo_n_powermetrics_command": True, "exit_code": 0},
        "PROBE",
        primary_artifacts=(script,),
        probes=(probe,),
    )


def _recursive_values(value: _Any, token: str) -> list[_Any]:
    result: list[_Any] = []
    if isinstance(value, _Mapping):
        for key, item in value.items():
            if token in str(key).lower():
                result.append(item)
            result.extend(_recursive_values(item, token))
    elif isinstance(value, list):
        for item in value:
            result.extend(_recursive_values(item, token))
    return result


def _derive_power(context: _Context) -> _DerivedRow:
    kind = "POWER_PREFLIGHT"
    policy = _frozen_power_policy(context, kind=kind)
    batt = _fresh_probe(context, kind, "AC state", ("/usr/bin/pmset", "-g", "batt"))
    custom = _fresh_probe(context, kind, "low-power mode", ("/usr/bin/pmset", "-g", "custom"))
    profiler = _fresh_probe(
        context,
        kind,
        "power supply",
        ("/usr/sbin/system_profiler", "SPPowerDataType", "-json"),
    )
    if batt.exit_code != 0 or "AC Power" not in batt.stdout:
        raise _underivable(kind, "fresh power probe does not report AC power")
    if custom.exit_code != 0 or _re.search(r"lowpowermode\s+0", custom.stdout, _re.I) is None:
        raise _underivable(kind, "fresh power probe does not report low-power mode off")
    try:
        power_value = _json.loads(profiler.stdout)
    except _json.JSONDecodeError as exc:
        raise _underivable(kind, "system-profiler power output is not JSON") from exc
    watts: list[int] = []
    for value in _recursive_values(power_value, "wattage"):
        match = _re.search(r"([0-9]+)", str(value))
        if match:
            watts.append(int(match.group(1)))
    connected = [str(value).lower() for value in _recursive_values(power_value, "connected")]
    if profiler.exit_code != 0 or not watts or max(watts) <= 0 or not any(value in {"yes", "true", "1"} for value in connected):
        raise _underivable(kind, "fresh supply probe lacks a connected known-wattage adapter")
    return _DerivedRow(
        "t0.power_path",
        kind,
        {
            "ac_state_matches_frozen_policy": True,
            "negotiation_matches_frozen_policy": True,
            "power_policy_matches": True,
            "supply_matches_frozen_policy": True,
            "observed_adapter_wattage": max(watts),
            "low_power_mode": "off",
        },
        "PROBE",
        probes=(batt, custom, profiler),
        derivation={"frozen_power_policy": policy},
    )


def _derive_launch(context: _Context) -> _DerivedRow:
    kind = "LAUNCH_RECIPE"
    manifest, artifacts, _assignments = _launch_manifest(context, kind=kind)
    arm, arm_identity = _arm_context(context, kind=kind)
    _root_observation(context, kind=kind)
    reservation, reservation_identity = _capture(context, "ledger-reservation", kind=kind)
    output = _json_stdout(reservation, kind=kind, label="ledger reservation")
    receipt = output.get("receipt")
    if not isinstance(receipt, _Mapping) or receipt.get("session_id") != arm["bracket_session_id"]:
        raise _underivable(kind, "launch session does not match the reserved bracket")
    arm_namespace = context.custody_pack_root / "arm_readiness.receipts"
    consumption_namespace = context.custody_pack_root / "arm_readiness.consumptions"
    if (arm_namespace.exists() and any(arm_namespace.iterdir())) or (
        consumption_namespace.exists() and any(consumption_namespace.iterdir())
    ):
        raise _underivable(kind, "an arm or consumption record already occupies the launch capability")
    for attempt in (arm["pre_attempt_id"], arm["post_attempt_id"]):
        attempt_path = _Path(str(arm["claim_runs_root"])) / "instrument_validation" / str(attempt)
        if attempt_path.exists() or attempt_path.is_symlink():
            raise _underivable(kind, f"reserved attempt ID already has custody: {attempt}")
    return _DerivedRow(
        "t0.single_launch_capability",
        kind,
        {
            "atomic_single_use_capability_available": True,
            "attempt_ids_unused": True,
            "exact_launch_command_frozen": True,
            "session_id_unused": True,
        },
        "PROBE",
        input_artifacts=(*artifacts, arm_identity, reservation_identity),
        derivation={"launch_command": _copy.deepcopy(manifest["launch_command"])},
    )


def _derive_backup(context: _Context) -> _DerivedRow:
    kind = "BACKUP_PREFLIGHT"
    arm, arm_identity = _arm_context(context, kind=kind)
    destinations = [
        _Path(str(arm["claim_backup_destination"])),
        _Path(str(arm["bound_backup_destination"])),
    ]
    try:
        resolved = [path.resolve(strict=True) for path in destinations]
    except OSError as exc:
        raise _underivable(kind, f"backup destination is absent: {exc}") from exc
    if len(set(resolved)) != 2 or any(not path.is_dir() or not _os.access(path, _os.W_OK) for path in destinations):
        raise _underivable(kind, "backup destinations are not distinct writable directories")
    free_bytes = [_shutil.disk_usage(path).free for path in destinations]
    if any(value < _MIN_BACKUP_FREE_BYTES for value in free_bytes):
        raise _underivable(kind, "backup destination lacks the required 20 GiB free capacity")
    return _DerivedRow(
        "t0.storage_backup_capacity",
        kind,
        {
            "destinations_distinct": True,
            "destinations_exist": True,
            "destinations_have_required_capacity": True,
            "destinations_writable": True,
            "free_bytes": free_bytes,
            "required_free_bytes": _MIN_BACKUP_FREE_BYTES,
        },
        "PROBE",
        input_artifacts=(arm_identity,),
    )


_DERIVERS = {
    "clock.correct_and_prior_state": _derive_clock_attestation,
    "clock.network_time_off": _derive_clock_probe,
    "desk.terminal_review": _derive_terminal_review,
    "t0.background_quiet": _derive_background_quiet,
    "t0.campaign_lock_absent": _derive_campaign_lock,
    "t0.display_thermal_idle": _derive_display_idle,
    "t0.fresh_roots_waivers": _derive_fresh_roots,
    "t0.ledger_reservation": _derive_ledger,
    "t0.machine_readiness": _derive_machine_readiness,
    "t0.no_stray_keepawake": _derive_process_census,
    "t0.offline_inputs": _derive_offline_inputs,
    "t0.passwordless_powermetrics": _derive_powermetrics,
    "t0.power_path": _derive_power,
    "t0.single_launch_capability": _derive_launch,
    "t0.storage_backup_capacity": _derive_backup,
}


def _validate_capture_order(context: _Context) -> None:
    captures = [context.captures[name][0] for name in _CAPTURE_ORDER]
    if any(
        left["finished_monotonic_ns"] > right["started_monotonic_ns"]
        for left, right in zip(captures, captures[1:])
    ):
        raise _refuse(
            "AUTHORING_SET",
            "evidence_author_t0_tap_sequence_invalid",
            "T-0 command captures do not follow E-4 clock-reference/E-5/E-7a/E-7b/E-8/E-9 order",
        )


def _source_bytes(context: _Context, derived: _DerivedRow) -> bytes:
    return _readiness.render_json(
        {
            "schema_version": _SOURCE_SCHEMA,
            "row_id": derived.row_id,
            "kind": derived.kind,
            "head_commit": context.head_commit,
            "head_tree_oid": context.head_tree_oid,
            "pack_sha256": context.pack_sha256,
            "boot_session_id": context.boot_session_id,
            "primary_artifacts": sorted(
                (_copy.deepcopy(dict(item)) for item in derived.primary_artifacts),
                key=lambda item: item["path"],
            ),
            "input_artifacts": sorted(
                (_copy.deepcopy(dict(item)) for item in derived.input_artifacts),
                key=lambda item: item["path"],
            ),
            "probes": [probe.evidence() for probe in derived.probes],
            "facts": [{"fact_id": f"{derived.row_id}.v1", "value": _copy.deepcopy(dict(derived.value))}],
            "derivation": _copy.deepcopy(dict(derived.derivation)),
        }
    )


def _assemble_receipt(
    context: _Context,
    derived: _DerivedRow,
    source_raw: bytes,
    *,
    issued_at_utc: str,
    valid_until_monotonic_ns: int,
) -> dict[str, _Any]:
    receipt = {
        "schema_version": _readiness.EVIDENCE_RECEIPT_SCHEMA,
        "evidence_id": _evidence_id(derived.row_id),
        "kind": derived.kind,
        "status": "PASS",
        "issued_at_utc": issued_at_utc,
        "boot_session_id": context.boot_session_id,
        "valid_until_monotonic_ns": valid_until_monotonic_ns,
        "pack_sha256": context.pack_sha256,
        "head_commit": context.head_commit,
        "facts": [
            {
                "fact_id": f"{derived.row_id}.v1",
                "value_type": "OBJECT",
                "value": _copy.deepcopy(dict(derived.value)),
                "source_kind": derived.source_kind,
                "source_path": _source_path(derived.row_id),
                "source_sha256": _readiness.sha256_bytes(source_raw),
            }
        ],
        "checks": [{"check_id": f"derive-{_slug(derived.row_id)}", "status": "PASS"}],
        "reason_codes": [],
        "assurance": _copy.deepcopy(_readiness.ASSURANCE),
    }
    _readiness.validate_evidence_receipt(receipt)
    return receipt


def _validate_source(value: object, *, expected_row: str, expected_kind: str) -> _Mapping[str, _Any]:
    if not isinstance(value, _Mapping) or set(value) != _SOURCE_KEYS:
        raise ValueError("T-0 evidence source has unknown or missing keys")
    if (
        value["schema_version"] != _SOURCE_SCHEMA
        or value["row_id"] != expected_row
        or value["kind"] != expected_kind
        or not isinstance(value["head_commit"], str)
        or _GIT_RE.fullmatch(value["head_commit"]) is None
        or not isinstance(value["head_tree_oid"], str)
        or _GIT_RE.fullmatch(value["head_tree_oid"]) is None
        or not isinstance(value["pack_sha256"], str)
        or _SHA_RE.fullmatch(value["pack_sha256"]) is None
    ):
        raise ValueError("T-0 evidence source identity is invalid")
    _readiness._require_boot_session_id(value["boot_session_id"], "T-0 source boot_session_id")
    for field_name in ("primary_artifacts", "input_artifacts"):
        items = value[field_name]
        if not isinstance(items, list):
            raise ValueError(f"T-0 source {field_name} is invalid")
        for item in items:
            if (
                not isinstance(item, _Mapping)
                or set(item) != _ARTIFACT_KEYS
                or not isinstance(item["path"], str)
                or not isinstance(item["sha256"], str)
                or _SHA_RE.fullmatch(item["sha256"]) is None
            ):
                raise ValueError(f"T-0 source {field_name} item is invalid")
    facts = value["facts"]
    if (
        not isinstance(facts, list)
        or len(facts) != 1
        or not isinstance(facts[0], _Mapping)
        or set(facts[0]) != _SOURCE_FACT_KEYS
        or facts[0]["fact_id"] != f"{expected_row}.v1"
        or not isinstance(facts[0]["value"], _Mapping)
        or not isinstance(value["probes"], list)
        or not isinstance(value["derivation"], _Mapping)
    ):
        raise ValueError("T-0 evidence source facts/probes/derivation are invalid")
    return value


def _reauthenticate_artifacts(context: _Context, derived: _Sequence[_DerivedRow]) -> None:
    for item in derived:
        for primary in item.primary_artifacts:
            actual, _raw = _committed_artifact(context.repository, primary["path"], kind=item.kind)
            if actual != primary:
                raise _refuse(item.kind, "evidence_author_t0_input_changed", f"primary artifact changed: {primary['path']}")
        for source in item.input_artifacts:
            path = _Path(source["path"])
            actual, _raw = _input_identity(path, kind=item.kind, label="T-0 input artifact")
            if actual != source:
                raise _refuse(item.kind, "evidence_author_t0_input_changed", f"T-0 input changed: {path}")


def _validity_horizon_ns(kind: str) -> int:
    if kind in _VOLATILE_EVIDENCE_KINDS:
        return _VOLATILE_EVIDENCE_VALIDITY_NS
    if kind in _NONVOLATILE_EVIDENCE_KINDS:
        return _NONVOLATILE_EVIDENCE_VALIDITY_NS
    raise _refuse(
        kind,
        "evidence_author_t0_internal_error",
        "evidence kind has no volatility classification",
    )


def _publication_complete(source_dir: _Path, evidence_dir: _Path) -> bool:
    marker = evidence_dir / _PUBLICATION_COMPLETION_MARKER
    return (
        source_dir.is_dir()
        and evidence_dir.is_dir()
        and marker.is_file()
        and not marker.is_symlink()
    )


def _publish_staged_namespaces(
    staged_sources: _Path,
    staged_evidence: _Path,
    staged_marker: _Path,
    source_dir: _Path,
    evidence_dir: _Path,
) -> None:
    """Publish two directories with a last-written authenticated marker.

    APFS cannot atomically rename two sibling destinations as one transaction.
    Crash matrix: before rename 1 leaves the full pre-state; after rename 1
    leaves sources only, so required ARM rows are absent; after rename 2 leaves
    the evidence receipt without its marker/sidecar, so discovery refuses the
    namespace as unreadable; during rename 3, atomic rename leaves either that
    detectable marker-absent state or the complete state; after rename 3 the
    full governed set is visible.  Never roll back a partial publication:
    process death cannot make rollback reliable, while marker absence is an
    unambiguous recovery signal.
    """

    _os.replace(staged_sources, source_dir)
    _os.replace(staged_evidence, evidence_dir)
    _os.replace(staged_marker, evidence_dir / _PUBLICATION_COMPLETION_MARKER)


def _authenticate_existing(
    context: _Context,
    rows: _Sequence[_Mapping[str, _Any]],
) -> dict[str, _Any]:
    source_dir = context.custody_pack_root / _SOURCE_DIRECTORY
    evidence_dir = context.custody_pack_root / _EVIDENCE_DIRECTORY
    if not source_dir.is_dir() or not evidence_dir.is_dir():
        raise _refuse("AUTHORING_SET", "evidence_author_t0_output_collision", "existing T-0 evidence/source namespace is incomplete")
    expected_sources = {f"{_slug(row['row_id'])}.json" for row in rows}
    expected_evidence = {
        name
        for row in rows
        for name in (_receipt_name(row["row_id"]), f"{_receipt_name(row['row_id'])}.sha256")
    }
    if {path.name for path in source_dir.iterdir()} != expected_sources or {path.name for path in evidence_dir.iterdir()} != expected_evidence:
        raise _refuse("AUTHORING_SET", "evidence_author_t0_output_collision", "existing T-0 namespace differs from the governed fifteen-row set")
    derived: dict[str, _DerivedRow] = {}
    for row in rows:
        row_id = str(row["row_id"])
        try:
            item = _DERIVERS[row_id](context)
        except T0EvidenceAuthoringError:
            raise
        except Exception as exc:
            raise _underivable(
                _ROW_KIND[row_id], f"unexpected fresh re-derivation failure: {exc}"
            ) from exc
        derived[row_id] = item
    _validate_capture_order(context)
    _reauthenticate_artifacts(context, tuple(derived.values()))
    now = context.clock.monotonic_ns()
    paths: list[str] = []
    for row in rows:
        row_id = str(row["row_id"])
        kind = _ROW_KIND[row_id]
        source_path = source_dir / f"{_slug(row_id)}.json"
        receipt_path = evidence_dir / _receipt_name(row_id)
        try:
            source_raw = _regular_bytes(source_path, kind=kind, label="existing source")
            receipt_raw = _regular_bytes(receipt_path, kind=kind, label="existing receipt")
            sidecar = _regular_bytes(receipt_path.with_name(f"{receipt_path.name}.sha256"), kind=kind, label="existing sidecar")
            source = _validate_source(
                _readiness.parse_json_bytes(source_raw, require_canonical=True),
                expected_row=row_id,
                expected_kind=kind,
            )
            receipt = _readiness.validate_evidence_receipt(
                _readiness.parse_json_bytes(receipt_raw, require_canonical=True)
            )
        except (ValueError, _readiness.ArmReadinessError, T0EvidenceAuthoringError) as exc:
            raise _refuse(kind, "evidence_author_t0_existing_invalid", f"existing {row_id} evidence is invalid: {exc}") from exc
        digest = _readiness.sha256_bytes(receipt_raw)
        if sidecar != _readiness.gnu_sidecar(digest, receipt_path.name):
            raise _refuse(kind, "evidence_author_t0_existing_invalid", "existing sidecar differs")
        expected_receipt = _assemble_receipt(
            context,
            derived[row_id],
            source_raw,
            issued_at_utc=str(receipt["issued_at_utc"]),
            valid_until_monotonic_ns=int(receipt["valid_until_monotonic_ns"]),
        )
        if (
            receipt["evidence_id"] != _evidence_id(row_id)
            or receipt["kind"] != kind
            or receipt["boot_session_id"] != context.boot_session_id
            or receipt["valid_until_monotonic_ns"] < now
            or receipt["pack_sha256"] != context.pack_sha256
            or receipt["head_commit"] != context.head_commit
            or source["head_commit"] != context.head_commit
            or source["head_tree_oid"] != context.head_tree_oid
            or source["pack_sha256"] != context.pack_sha256
            or source["boot_session_id"] != context.boot_session_id
            or source_raw != _source_bytes(context, derived[row_id])
            or receipt["facts"][0]["source_sha256"] != _readiness.sha256_bytes(source_raw)
            or receipt["facts"][0]["value"] != source["facts"][0]["value"]
            or receipt != expected_receipt
            or not _readiness._predicate_passes(
                receipt,
                row["predicate_id"],
                expected_plan_sha256=context.plan_sha256,
                # Existing-namespace re-authentication must remain byte/semantic
                # replay and cannot add a later live anchor observation.
                live_clock_anchor=_readiness._PREDICATE_LIVE_ANCHOR_NOT_APPLICABLE,
            )
        ):
            raise _refuse(kind, "evidence_author_t0_existing_stale", f"existing {row_id} evidence is stale or semantically invalid")
        for primary in source["primary_artifacts"]:
            actual, _raw = _committed_artifact(context.repository, primary["path"], kind=kind)
            if actual != primary:
                raise _refuse(kind, "evidence_author_t0_existing_stale", f"primary artifact changed: {primary['path']}")
        for input_item in source["input_artifacts"]:
            actual, _raw = _input_identity(_Path(input_item["path"]), kind=kind, label="existing T-0 input")
            if actual != input_item:
                raise _refuse(kind, "evidence_author_t0_existing_stale", f"T-0 input changed: {input_item['path']}")
        paths.append(str(receipt_path))
    return {
        "status": "PASS",
        "authored_rows": [row["row_id"] for row in rows],
        "authored_kinds": sorted(set(_ROW_KIND[row["row_id"]] for row in rows)),
        "receipt_paths": paths,
        "mutated": False,
    }


def author_arm_readiness_evidence_t0(
    pack_root: _Path | str,
    custody_root: _Path | str,
) -> dict[str, _Any]:
    """Author all fifteen evidence-backed ARM_ONLY row receipts."""

    root = _Path(pack_root).resolve(strict=True)
    repository = _readiness._repo_for_pack(root).resolve(strict=True)
    if repository != _RUNNING_REPOSITORY.resolve(strict=True):
        raise _refuse(
            "AUTHORING_SET",
            "evidence_author_t0_repository_mismatch",
            "pack repository differs from the executing T-0 evidence author",
        )
    custody = _Path(custody_root).resolve(strict=True)
    if not custody.is_dir() or custody.is_symlink():
        raise _underivable("AUTHORING_SET", "custody root is not a regular directory")
    reviewed = _readiness.reviewed_main(root)
    if not reviewed["clean"] or not reviewed["exact_match"]:
        raise _refuse(
            "AUTHORING_SET",
            "evidence_author_t0_reviewed_tree_mismatch",
            "reviewed checkout is dirty or differs from local/origin main",
        )
    head = reviewed["head_commit"]
    head_tree = reviewed["head_tree_oid"]
    if _GIT_RE.fullmatch(str(head)) is None or _GIT_RE.fullmatch(str(head_tree)) is None:
        raise _underivable("AUTHORING_SET", "reviewed HEAD/tree identity is unavailable")
    tree, _tree_raw = _readiness._plan_tree(root)
    try:
        frozen_plan = _readiness.resolve_frozen_plan(root, tree)
    except _readiness.ArmReadinessError as exc:
        raise _underivable(
            "AUTHORING_SET", f"R2 frozen-plan reference is invalid: {exc}"
        ) from exc
    try:
        pack_sha = _readiness.committed_pack_tree_sha256(root)
    except _readiness.ArmReadinessError as exc:
        raise _refuse("AUTHORING_SET", "evidence_author_t0_pack_uncommitted", str(exc)) from exc
    boot_session, boot_probe = _boot_probe(repository)
    context = _DerivationContext(
        pack_root=root,
        repository=repository,
        custody_root=custody,
        custody_pack_root=custody / root.name,
        tree=tree,
        pack_sha256=pack_sha,
        plan_sha256=_readiness.sha256_bytes(frozen_plan[3]),
        head_commit=str(head),
        head_tree_oid=str(head_tree),
        boot_session_id=boot_session,
        boot_probe=boot_probe,
    )
    context.values["frozen_plan"] = frozen_plan
    rows = _required_rows(context)
    source_dir = context.custody_pack_root / _SOURCE_DIRECTORY
    evidence_dir = context.custody_pack_root / _EVIDENCE_DIRECTORY
    if source_dir.exists() or evidence_dir.exists():
        if not _publication_complete(source_dir, evidence_dir):
            raise _refuse(
                "AUTHORING_SET",
                "evidence_author_t0_publication_incomplete",
                "T-0 publication is incomplete; recovery must preserve and inspect "
                "the marker-absent namespace",
            )
        return _authenticate_existing(context, rows)
    derived: list[_DerivedRow] = []
    for row in rows:
        row_id = str(row["row_id"])
        try:
            item = _DERIVERS[row_id](context)
        except T0EvidenceAuthoringError:
            raise
        except Exception as exc:
            raise _underivable(_ROW_KIND[row_id], f"unexpected derivation failure: {exc}") from exc
        if item.row_id != row_id or item.kind != _ROW_KIND[row_id]:
            raise _refuse(_ROW_KIND[row_id], "evidence_author_t0_internal_error", "deriver returned the wrong row/kind")
        derived.append(item)
    _validate_capture_order(context)
    issued_at = context.clock.utc_now()
    validity_origin = context.clock.monotonic_ns()
    sources: dict[str, bytes] = {}
    receipts: dict[str, bytes] = {}
    semantic: dict[str, _Mapping[str, _Any]] = {}
    definitions = {row["row_id"]: row for row in rows}
    for item in derived:
        source_raw = _source_bytes(context, item)
        sources[f"{_slug(item.row_id)}.json"] = source_raw
        receipt = _assemble_receipt(
            context,
            item,
            source_raw,
            issued_at_utc=issued_at,
            valid_until_monotonic_ns=(
                validity_origin + _validity_horizon_ns(item.kind)
            ),
        )
        if not _readiness._predicate_passes(
            receipt,
            definitions[item.row_id]["predicate_id"],
            expected_plan_sha256=context.plan_sha256,
            # Issuance proves the published numeric relations; the separate
            # live anchor check belongs only to original ARM evaluation.
            live_clock_anchor=_readiness._PREDICATE_LIVE_ANCHOR_NOT_APPLICABLE,
        ):
            raise _refuse(item.kind, "evidence_author_t0_predicate_refused", f"derived facts do not satisfy {item.row_id}")
        raw = _readiness.render_json(receipt)
        name = _receipt_name(item.row_id)
        receipts[name] = raw
        receipts[f"{name}.sha256"] = _readiness.gnu_sidecar(_readiness.sha256_bytes(raw), name)
        semantic[receipt["evidence_id"]] = receipt
    _reauthenticate_artifacts(context, derived)
    if _readiness.reviewed_main(root) != reviewed or _readiness.committed_pack_tree_sha256(root) != pack_sha:
        raise _refuse("AUTHORING_SET", "evidence_author_t0_input_changed", "HEAD, tree, or pack changed during derivation")
    second_boot, _second_boot_probe = _boot_probe(repository)
    if second_boot != boot_session:
        raise _refuse("AUTHORING_SET", "evidence_author_t0_input_changed", "boot session changed during derivation")

    context.custody_pack_root.mkdir(parents=True, exist_ok=True)
    staging = _Path(_tempfile.mkdtemp(prefix=".arm-readiness-t0-", dir=context.custody_pack_root))
    try:
        staged_sources = staging / _SOURCE_DIRECTORY
        staged_evidence = staging / _EVIDENCE_DIRECTORY
        staged_sources.mkdir()
        staged_evidence.mkdir()
        for name, raw in sources.items():
            (staged_sources / name).write_bytes(raw)
        for name, raw in receipts.items():
            (staged_evidence / name).write_bytes(raw)
        items, discovered, refusals = _readiness._discover_evidence(
            root,
            staging,
            pack_sha256=pack_sha,
            head_commit=head,
            boot_session_id=boot_session,
            now_monotonic_ns=context.clock.monotonic_ns(),
            include_pack=False,
        )
        if refusals or set(discovered) != set(semantic):
            raise _refuse("AUTHORING_SET", "evidence_author_t0_validation_failed", f"staged discovery refused: {refusals!r}")
        for receipt in discovered.values():
            _readiness.validate_evidence_receipt(receipt)
        if source_dir.exists() or evidence_dir.exists():
            raise _refuse("AUTHORING_SET", "evidence_author_t0_output_collision", "T-0 output namespace appeared during derivation")
        marker_in_directory = staged_evidence / _PUBLICATION_COMPLETION_MARKER
        if not marker_in_directory.is_file() or marker_in_directory.is_symlink():
            raise _refuse(
                "AUTHORING_SET",
                "evidence_author_t0_internal_error",
                "staged publication completion marker is absent",
            )
        staged_marker = staging / _PUBLICATION_COMPLETION_MARKER
        _os.replace(marker_in_directory, staged_marker)
        try:
            _publish_staged_namespaces(
                staged_sources,
                staged_evidence,
                staged_marker,
                source_dir,
                evidence_dir,
            )
        except Exception as exc:
            raise _refuse(
                "AUTHORING_SET",
                "evidence_author_t0_publication_interrupted",
                "T-0 publication was interrupted; the completion marker records "
                "whether recovery sees a partial or complete namespace",
            ) from exc
        paths = [str(context.custody_pack_root / item["path"]) for item in sorted(items, key=lambda value: value["evidence_id"])]
    finally:
        _shutil.rmtree(staging, ignore_errors=True)
    return {
        "status": "PASS",
        "authored_rows": [row["row_id"] for row in rows],
        "authored_kinds": sorted(set(_ROW_KIND[row["row_id"]] for row in rows)),
        "receipt_paths": paths,
        "mutated": True,
    }


def _assert_public_author_signature() -> None:
    parameters = tuple(_inspect.signature(author_arm_readiness_evidence_t0).parameters)
    if parameters != ("pack_root", "custody_root"):
        raise AssertionError("public T-0 evidence author must accept exactly pack_root and custody_root")


_assert_public_author_signature()


__all__ = [
    "T0EvidenceAuthoringError",
    "WINDOW_ENV_KEYS",
    "WindowEnvironmentParseError",
    "author_arm_readiness_evidence_t0",
    "parse_window_environment",
]
