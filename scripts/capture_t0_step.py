#!/usr/bin/env python3
"""Execute and byte-canonically capture one governed D-134 T-0 E-step.

The production CLI is a trusted-operator ceremony interface, not independent
producer attestation.  When faithfully invoked it derives commands,
identities, and canonical captures; the only operator-supplied values are
E-4's two registered irreducible observations (the independent-clock UTC
literal and the pasted prior network-time state output). v1 does not defend
against deliberate operator fabrication.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Callable, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise import arm_readiness as readiness  # noqa: E402


COMMAND_CAPTURE_SCHEMA = "joulewise.arm_readiness_t0_command_capture.v1"
CLOCK_ATTESTATION_SCHEMA = "joulewise.arm_readiness_t0_clock_attestation.v1"
LAUNCH_MANIFEST_SCHEMA = "joulewise.arm_readiness_t0_launch_manifest.v1"
INPUT_DIRECTORY = "arm_readiness.t0.inputs"
REFERENCE_TIME_PROMPT = (
    "Independent trusted-clock UTC literal (for example 2026-08-15T12:34:56Z): "
)
PRIOR_STATE_PROMPT = (
    "Paste Ed's exact interactive prior network-time output "
    "(Network Time: On or Network Time: Off): "
)
INTERACTIVE_PRIOR_STATE_ARGV = (
    "operator-interactive",
    "network-time-prior-state",
)
GOVERNED_SUBPROCESS_ENVIRONMENT = {
    "LANG": "C",
    "LC_ALL": "C",
    "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
}

STEP_FILENAMES = {
    "clock-prior-state": "clock-prior-state.json",
    "clock-disable": "clock-disable.json",
    "quiet-mac-prep": "quiet-mac-prep.json",
    "prewindow-check": "prewindow-check.json",
    "ledger-readiness": "ledger-readiness.json",
    "ledger-reservation": "ledger-reservation.json",
}
STEP_ORDER = tuple(STEP_FILENAMES)
CAPTURE_KEYS = frozenset(
    {
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
)

# D-078's closed capture-producer vocabulary.  Every spelling is registered in
# docs/decision_log.md and every failure is a refusal, never launch authority.
CAPTURE_REASON_CODES = frozenset(
    {
        "evidence_author_t0_capture_usage_invalid",
        "evidence_author_t0_capture_environment_invalid",
        "evidence_author_t0_capture_boot_probe_failed",
        "evidence_author_t0_capture_plan_invalid",
        "evidence_author_t0_capture_terminal_review_missing",
        "evidence_author_t0_capture_sequence_invalid",
        "evidence_author_t0_capture_clock_observation_invalid",
        "evidence_author_t0_capture_command_failed",
        "evidence_author_t0_capture_result_invalid",
        "evidence_author_t0_capture_output_collision",
        "evidence_author_t0_capture_io_error",
        "evidence_author_t0_capture_internal_error",
    }
)

_ENV_KEYS = frozenset(
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


class CaptureT0Error(ValueError):
    """Fail-closed producer refusal with one registered reason code."""

    def __init__(self, reason_code: str, detail: str) -> None:
        if reason_code not in CAPTURE_REASON_CODES:
            raise AssertionError(f"unregistered T-0 capture reason code: {reason_code}")
        super().__init__(detail)
        self.reason_code = reason_code


@dataclass(frozen=True)
class CaptureContext:
    repository: Path
    pack_root: Path
    custody_root: Path
    custody_pack_root: Path
    input_root: Path
    window_plan_root: Path
    tree: Mapping[str, object]
    assignments: Mapping[str, str]
    frozen_plan_path: Path
    frozen_plan_relative: str
    plan_id: str
    plan_sha256: str
    pack_sha256: str
    boot_session_id: str
    arm_context: Mapping[str, object]
    prewindow_command: tuple[str, ...]
    launch_command: tuple[str, ...]


def _refuse(reason_code: str, detail: str) -> CaptureT0Error:
    return CaptureT0Error(reason_code, detail)


def _regular_bytes(path: Path, *, label: str) -> bytes:
    try:
        if path.is_symlink() or not path.is_file():
            raise OSError("not a regular non-symlink file")
        return path.read_bytes()
    except OSError as exc:
        raise _refuse(
            "evidence_author_t0_capture_io_error",
            f"{label} is unreadable: {path}: {exc}",
        ) from exc


def _write_no_clobber(path: Path, raw: bytes, *, accept_identical: bool) -> bool:
    """Publish one complete file without ever replacing an existing path."""

    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        if accept_identical and _regular_bytes(path, label="existing derived input") == raw:
            return False
        raise _refuse(
            "evidence_author_t0_capture_output_collision",
            f"refusing to replace existing T-0 input: {path}",
        )
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            prefix=".capture-t0-", dir=path.parent, delete=False
        ) as stream:
            temporary_name = stream.name
            os.chmod(temporary_name, 0o600)
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary_name, path)
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    except FileExistsError as exc:
        raise _refuse(
            "evidence_author_t0_capture_output_collision",
            f"T-0 input appeared concurrently: {path}",
        ) from exc
    except OSError as exc:
        raise _refuse(
            "evidence_author_t0_capture_io_error",
            f"cannot publish T-0 input {path}: {exc}",
        ) from exc
    finally:
        if temporary_name is not None:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass
    return True


def _parse_window_environment(raw: bytes) -> dict[str, str]:
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise _refuse(
            "evidence_author_t0_capture_environment_invalid",
            "window.env is not UTF-8",
        ) from exc
    values: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = re.fullmatch(r"([A-Z][A-Z0-9_]*)=(.*)", stripped)
        if match is None:
            raise _refuse(
                "evidence_author_t0_capture_environment_invalid",
                f"window.env contains a non-assignment line: {stripped!r}",
            )
        name, value_text = match.groups()
        try:
            parts = shlex.split(value_text, posix=True)
        except ValueError as exc:
            raise _refuse(
                "evidence_author_t0_capture_environment_invalid",
                f"window.env value for {name} is malformed",
            ) from exc
        if name in values or len(parts) != 1 or "$" in parts[0]:
            raise _refuse(
                "evidence_author_t0_capture_environment_invalid",
                f"window.env value for {name} is ambiguous",
            )
        values[name] = parts[0]
    missing = _ENV_KEYS - set(values)
    unknown = set(values) - _ENV_KEYS
    if missing or unknown:
        raise _refuse(
            "evidence_author_t0_capture_environment_invalid",
            f"window.env exact keys differ; missing={sorted(missing)!r}, unknown={sorted(unknown)!r}",
        )
    return values


def _current_boot_session_id() -> str:
    try:
        return readiness._current_boot_session_id()
    except readiness.ArmReadinessError as exc:
        raise _refuse(
            "evidence_author_t0_capture_boot_probe_failed", str(exc)
        ) from exc


def _git_text(repository: Path, *args: str) -> str:
    value = readiness._git_text(repository, *args)
    if value is None:
        raise _refuse(
            "evidence_author_t0_capture_terminal_review_missing",
            f"Git proof is unavailable: {' '.join(args)}",
        )
    return value


def _verify_terminal_review(
    repository: Path, pack_root: Path, *, pack_sha256: str
) -> None:
    reviewed = readiness.reviewed_main(pack_root)
    if not reviewed["clean"] or not reviewed["exact_match"]:
        raise _refuse(
            "evidence_author_t0_capture_terminal_review_missing",
            "reviewed checkout is dirty or differs from local/origin main",
        )
    message = _git_text(repository, "show", "-s", "--format=%B", "HEAD")
    tree_oid = _git_text(repository, "rev-parse", "HEAD^{tree}")
    trailers: dict[str, list[str]] = {}
    for line in message.splitlines():
        match = re.fullmatch(
            r"(JouleWise-Terminal-Review(?:-Tree-Oid|-Pack-Sha256)?):\s*(\S+)",
            line,
        )
        if match:
            trailers.setdefault(match.group(1), []).append(match.group(2))
    expected = {
        "JouleWise-Terminal-Review": "PASS",
        "JouleWise-Terminal-Review-Tree-Oid": tree_oid,
        "JouleWise-Terminal-Review-Pack-Sha256": pack_sha256,
    }
    if any(trailers.get(name) != [value] for name, value in expected.items()):
        raise _refuse(
            "evidence_author_t0_capture_terminal_review_missing",
            "HEAD lacks the exact lead-owned PASS/tree/pack terminal-review trailers",
        )


def _absolute(values: Mapping[str, str], name: str) -> Path:
    path = Path(values[name])
    if not path.is_absolute():
        raise _refuse(
            "evidence_author_t0_capture_environment_invalid",
            f"window.env {name} must be an absolute literal",
        )
    return path


def _load_context(
    pack_root: Path | str,
    custody_root: Path | str,
    window_plan_root: Path | str,
) -> CaptureContext:
    try:
        pack = Path(pack_root).resolve(strict=True)
        custody = Path(custody_root).resolve(strict=True)
        window = Path(window_plan_root).resolve(strict=True)
        repository = readiness._repo_for_pack(pack).resolve(strict=True)
    except (OSError, readiness.ArmReadinessError) as exc:
        raise _refuse(
            "evidence_author_t0_capture_environment_invalid",
            f"pack/custody/window roots are unavailable: {exc}",
        ) from exc
    if repository != REPO_ROOT.resolve(strict=True):
        raise _refuse(
            "evidence_author_t0_capture_environment_invalid",
            "pack repository differs from the executing capture tool",
        )
    if not custody.is_dir() or custody.is_symlink() or not window.is_dir() or window.is_symlink():
        raise _refuse(
            "evidence_author_t0_capture_environment_invalid",
            "custody and window-plan roots must be regular directories",
        )
    try:
        window.relative_to(custody)
    except ValueError as exc:
        raise _refuse(
            "evidence_author_t0_capture_environment_invalid",
            "window-plan root must be inside the D-134 custody root",
        ) from exc

    tree, _tree_raw = readiness._plan_tree(pack)
    try:
        frozen_path, frozen_relative, plan_id, plan_raw = (
            readiness.resolve_frozen_plan(pack, tree)
        )
        pack_sha256 = readiness.committed_pack_tree_sha256(pack)
    except readiness.ArmReadinessError as exc:
        raise _refuse("evidence_author_t0_capture_plan_invalid", str(exc)) from exc
    assignments = _parse_window_environment(
        _regular_bytes(window / "window.env", label="window.env")
    )
    expected_literals = {
        "MEASUREMENT_REPO": str(repository),
        "PACK_ROOT": str(pack),
        "PACK_ID": pack.name,
        "PLAN_ID": plan_id,
        "FROZEN_PLAN": str(frozen_path),
        "ARM_READINESS_CUSTODY_ROOT": str(custody),
    }
    window_identity = tree.get("window_identity")
    if not isinstance(window_identity, Mapping):
        raise _refuse(
            "evidence_author_t0_capture_plan_invalid",
            "plan tree omits window_identity",
        )
    try:
        window_id = readiness._require_string(
            window_identity.get("window_id"), "window_identity.window_id"
        )
        evidence_root_id = readiness._require_string(
            window_identity.get("evidence_root_id"),
            "window_identity.evidence_root_id",
        )
    except readiness.ArmReadinessError as exc:
        raise _refuse("evidence_author_t0_capture_plan_invalid", str(exc)) from exc
    expected_literals.update(
        {
            "WINDOW_ID": window_id,
            "EVIDENCE_ROOT_ID": evidence_root_id,
        }
    )
    if any(assignments.get(name) != value for name, value in expected_literals.items()):
        raise _refuse(
            "evidence_author_t0_capture_environment_invalid",
            "window.env differs from the R2 pack/repository/custody identity",
        )
    if assignments["CUSTODY_ROOT"] != assignments["WINDOW_CUSTODY_ROOT"]:
        raise _refuse(
            "evidence_author_t0_capture_environment_invalid",
            "CUSTODY_ROOT and WINDOW_CUSTODY_ROOT must be the same literal",
        )
    if assignments["SETTLE_S"] != "180":
        raise _refuse(
            "evidence_author_t0_capture_environment_invalid",
            "SETTLE_S must be the frozen 180-second literal",
        )
    for name in (
        "RUNS_ROOT",
        "BOUND_RUNS_ROOT",
        "CUSTODY_ROOT",
        "WINDOW_CUSTODY_ROOT",
        "QUARANTINE_ROOT",
        "CLAIM_BACKUP_DEST",
        "BOUND_BACKUP_DEST",
        "IDENTITY_EPOCH_JSON",
        "T1_BINDINGS_JSON",
        "CALIBRATION_LEDGER",
        "LEDGER_HEAD_PIN",
        "WAIVER_PATH",
    ):
        _absolute(assignments, name)

    arm_context = {
        "bracket_session_id": assignments["BRACKET_SESSION_ID"],
        "pre_attempt_id": assignments["PRE_ATTEMPT_ID"],
        "post_attempt_id": assignments["POST_ATTEMPT_ID"],
        "clock_route": "MANUAL",
        "claim_runs_root": assignments["RUNS_ROOT"],
        "bound_runs_root": assignments["BOUND_RUNS_ROOT"],
        "custody_root": assignments["CUSTODY_ROOT"],
        "quarantine_root": assignments["QUARANTINE_ROOT"],
        "claim_backup_destination": assignments["CLAIM_BACKUP_DEST"],
        "bound_backup_destination": assignments["BOUND_BACKUP_DEST"],
        "waiver_path": assignments["WAIVER_PATH"],
    }
    try:
        arm_context = dict(readiness.validate_arm_context(arm_context))
        profile = readiness._plan_profile(pack).lower()
    except readiness.ArmReadinessError as exc:
        raise _refuse(
            "evidence_author_t0_capture_environment_invalid", str(exc)
        ) from exc

    chain = window / "window-chain.zsh"
    try:
        chain_text = _regular_bytes(chain, label="window-chain.zsh").decode(
            "utf-8", errors="strict"
        )
    except UnicodeDecodeError as exc:
        raise _refuse(
            "evidence_author_t0_capture_environment_invalid",
            "window-chain.zsh is not UTF-8",
        ) from exc
    repo_matches = re.findall(
        r"(?m)^REPO=(?:\"([^\"]+)\"|'([^']+)'|([^\s]+))$", chain_text
    )
    repo_values = [next(item for item in match if item) for match in repo_matches]
    if repo_values != [str(repository)] or re.search(
        r"(?m)^QUARANTINE_ROOT=", chain_text
    ):
        raise _refuse(
            "evidence_author_t0_capture_environment_invalid",
            "window-chain.zsh must contain one literal reviewed REPO binding and no quarantine override",
        )

    boot_session_id = _current_boot_session_id()
    prewindow_command = (
        "/bin/bash",
        str(repository / "scripts/prewindow_check.sh"),
        "--wait",
        "--timeout-min",
        "45",
        "--window",
        profile,
    )
    launch_command = (
        "/usr/bin/caffeinate",
        "-is",
        "/bin/zsh",
        str(chain),
        str(window),
    )
    _verify_terminal_review(repository, pack, pack_sha256=pack_sha256)
    return CaptureContext(
        repository=repository,
        pack_root=pack,
        custody_root=custody,
        custody_pack_root=custody / pack.name,
        input_root=custody / pack.name / INPUT_DIRECTORY,
        window_plan_root=window,
        tree=tree,
        assignments=assignments,
        frozen_plan_path=frozen_path,
        frozen_plan_relative=frozen_relative,
        plan_id=plan_id,
        plan_sha256=readiness.sha256_bytes(plan_raw),
        pack_sha256=pack_sha256,
        boot_session_id=boot_session_id,
        arm_context=arm_context,
        prewindow_command=prewindow_command,
        launch_command=launch_command,
    )


def _prepare_derived_inputs(context: CaptureContext) -> list[str]:
    context.input_root.mkdir(parents=True, exist_ok=True)
    arm_path = context.input_root / "arm-context.json"
    launch_path = context.input_root / "launch-manifest.json"
    launch = {
        "schema_version": LAUNCH_MANIFEST_SCHEMA,
        "boot_session_id": context.boot_session_id,
        "window_plan_root": str(context.window_plan_root),
        "prewindow_command": list(context.prewindow_command),
        "launch_command": list(context.launch_command),
    }
    _write_no_clobber(
        arm_path, readiness.render_json(dict(context.arm_context)), accept_identical=True
    )
    _write_no_clobber(
        launch_path, readiness.render_json(launch), accept_identical=True
    )
    return [str(arm_path), str(launch_path)]


def _clock_attestation(
    context: CaptureContext,
    *,
    prompt: Callable[[str], str],
    monotonic_ns: Callable[[], int],
    utc_now: Callable[[], str],
) -> str:
    try:
        literal = prompt(REFERENCE_TIME_PROMPT).strip()
    except (EOFError, OSError) as exc:
        raise _refuse(
            "evidence_author_t0_capture_clock_observation_invalid",
            "trusted-clock literal was not provided",
        ) from exc
    try:
        reference = datetime.fromisoformat(literal.replace("Z", "+00:00"))
    except ValueError as exc:
        raise _refuse(
            "evidence_author_t0_capture_clock_observation_invalid",
            "trusted-clock literal is not an ISO-8601 timestamp",
        ) from exc
    if reference.tzinfo is None or reference.utcoffset() != timedelta(0):
        raise _refuse(
            "evidence_author_t0_capture_clock_observation_invalid",
            "trusted-clock literal must carry the UTC offset",
        )
    system_literal = utc_now()
    try:
        system = datetime.fromisoformat(system_literal.replace("Z", "+00:00"))
    except ValueError as exc:
        raise _refuse(
            "evidence_author_t0_capture_internal_error",
            "derived system clock is not ISO-8601",
        ) from exc
    if system.tzinfo is None or system.utcoffset() != timedelta(0):
        raise _refuse(
            "evidence_author_t0_capture_internal_error",
            "derived system clock does not carry the UTC offset",
        )
    difference = abs(
        (system.astimezone(UTC) - reference.astimezone(UTC)).total_seconds()
    )
    if difference > 2.0:
        raise _refuse(
            "evidence_author_t0_capture_clock_observation_invalid",
            f"independent clocks differ by {difference:.6f} seconds",
        )
    observed = monotonic_ns()
    seed = (
        f"{context.boot_session_id}\0{observed}\0{system_literal}\0{literal}"
    ).encode("utf-8")
    value = {
        "schema_version": CLOCK_ATTESTATION_SCHEMA,
        "attestation_id": f"clock-{hashlib.sha256(seed).hexdigest()[:24]}",
        "observer": "lead_operator",
        "reference_source": "independent_trusted_clock",
        "system_time_utc": system_literal,
        "reference_time_utc": literal,
        "observed_monotonic_ns": observed,
        "boot_session_id": context.boot_session_id,
    }
    path = context.input_root / "clock-attestation.json"
    _write_no_clobber(path, readiness.render_json(value), accept_identical=False)
    return str(path)


def _command_for_step(context: CaptureContext, step_id: str) -> tuple[str, ...]:
    values = context.assignments
    python = str(context.repository / ".venv/bin/python")
    if step_id == "clock-prior-state":
        return INTERACTIVE_PRIOR_STATE_ARGV
    if step_id == "clock-disable":
        return (
            "/usr/bin/sudo",
            "-n",
            "/usr/sbin/systemsetup",
            "-setusingnetworktime",
            "off",
        )
    if step_id == "quiet-mac-prep":
        return ("/bin/bash", str(context.repository / "scripts/quiet_mac_prep.sh"))
    if step_id == "prewindow-check":
        return context.prewindow_command
    if step_id == "ledger-readiness":
        return (
            python,
            str(context.repository / "scripts/recover_calibration_ledger.py"),
            "readiness",
            "--phase",
            "pre-reserve",
            "--session-id",
            values["BRACKET_SESSION_ID"],
            "--plan",
            str(context.frozen_plan_path),
        )
    if step_id == "ledger-reservation":
        return (
            python,
            str(context.repository / "scripts/reserve_calibration_window_bracket.py"),
            "--ledger",
            values["CALIBRATION_LEDGER"],
            "--head-pin",
            values["LEDGER_HEAD_PIN"],
            "--session-id",
            values["BRACKET_SESSION_ID"],
            "--window-id",
            values["WINDOW_ID"],
            "--plan-id",
            context.plan_id,
            "--plan-sha256",
            context.plan_sha256,
            "--plan",
            str(context.frozen_plan_path),
            "--evidence-root-id",
            values["EVIDENCE_ROOT_ID"],
            "--runs-root",
            values["RUNS_ROOT"],
            "--pre-attempt-id",
            values["PRE_ATTEMPT_ID"],
            "--post-attempt-id",
            values["POST_ATTEMPT_ID"],
            "--pre-custody-locator",
            str(
                Path(values["RUNS_ROOT"])
                / "instrument_validation"
                / values["PRE_ATTEMPT_ID"]
            ),
            "--post-custody-locator",
            str(
                Path(values["RUNS_ROOT"])
                / "instrument_validation"
                / values["POST_ATTEMPT_ID"]
            ),
            "--identity-epoch-json",
            values["IDENTITY_EPOCH_JSON"],
            "--t1-bindings-json",
            values["T1_BINDINGS_JSON"],
            "--execute",
        )
    raise _refuse(
        "evidence_author_t0_capture_usage_invalid", f"unknown T-0 step: {step_id}"
    )


def _require_sequence(context: CaptureContext, step_id: str) -> None:
    index = STEP_ORDER.index(step_id)
    for prior in STEP_ORDER[:index]:
        path = context.input_root / STEP_FILENAMES[prior]
        if path.is_symlink() or not path.is_file():
            raise _refuse(
                "evidence_author_t0_capture_sequence_invalid",
                f"{step_id} cannot run before {prior}",
            )
        try:
            value = readiness.parse_json_bytes(
                path.read_bytes(), require_canonical=True
            )
            if (
                not isinstance(value, Mapping)
                or set(value) != CAPTURE_KEYS
                or value.get("schema_version") != COMMAND_CAPTURE_SCHEMA
                or value.get("step_id") != prior
                or value.get("argv") != list(_command_for_step(context, prior))
                or value.get("cwd") != str(context.repository)
                or not isinstance(value.get("exit_code"), int)
                or isinstance(value.get("exit_code"), bool)
                or value["exit_code"] != 0
                or not isinstance(value.get("stdout"), str)
                or not isinstance(value.get("stderr"), str)
                or not isinstance(value.get("started_monotonic_ns"), int)
                or isinstance(value.get("started_monotonic_ns"), bool)
                or not isinstance(value.get("finished_monotonic_ns"), int)
                or isinstance(value.get("finished_monotonic_ns"), bool)
                or value["started_monotonic_ns"] < 1
                or value["finished_monotonic_ns"] < value["started_monotonic_ns"]
                or value.get("boot_session_id") != context.boot_session_id
                or (
                    prior == "prewindow-check"
                    and value["finished_monotonic_ns"]
                    - value["started_monotonic_ns"]
                    < 600 * 1_000_000_000
                )
            ):
                raise ValueError("capture fields differ from the governed result")
            _validate_result(context, prior, value["stdout"], value["stderr"])
        except (OSError, ValueError, readiness.ArmReadinessError, CaptureT0Error) as exc:
            raise _refuse(
                "evidence_author_t0_capture_sequence_invalid",
                f"{step_id} predecessor {prior} is not a validated capture",
            ) from exc
    current = context.input_root / STEP_FILENAMES[step_id]
    if current.exists() or current.is_symlink():
        raise _refuse(
            "evidence_author_t0_capture_output_collision",
            f"refusing to recapture completed step {step_id}",
        )
    for later in STEP_ORDER[index + 1 :]:
        path = context.input_root / STEP_FILENAMES[later]
        if path.exists() or path.is_symlink():
            raise _refuse(
                "evidence_author_t0_capture_sequence_invalid",
                f"future capture {later} exists before {step_id}",
            )


def _execute(argv: Sequence[str], *, cwd: Path) -> subprocess.CompletedProcess[bytes]:
    try:
        return subprocess.run(
            list(argv),
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            env=GOVERNED_SUBPROCESS_ENVIRONMENT,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise _refuse(
            "evidence_author_t0_capture_io_error",
            f"T-0 command could not execute: {exc}",
        ) from exc


def _text(value: bytes | str) -> str:
    return value if isinstance(value, str) else value.decode("utf-8", errors="replace")


def _interactive_prior_state(
    *, prompt: Callable[[str], str]
) -> subprocess.CompletedProcess[bytes]:
    """Capture Ed's separately executed interactive observation without privilege."""

    try:
        output = prompt(PRIOR_STATE_PROMPT).strip()
    except (EOFError, OSError) as exc:
        raise _refuse(
            "evidence_author_t0_capture_result_invalid",
            "E-4 interactive prior network-time output was not provided",
        ) from exc
    if re.fullmatch(r"Network Time:\s*(?:On|Off)", output) is None:
        raise _refuse(
            "evidence_author_t0_capture_result_invalid",
            "E-4 interactive prior network-time output is not exact",
        )
    return subprocess.CompletedProcess(
        INTERACTIVE_PRIOR_STATE_ARGV,
        0,
        f"{output}\n".encode("utf-8"),
        b"",
    )


def _validate_result(
    context: CaptureContext, step_id: str, stdout: str, stderr: str
) -> None:
    if step_id == "clock-prior-state":
        if re.search(r"Network Time:\s*(?:On|Off)\s*$", stdout, re.MULTILINE) is None:
            raise _refuse(
                "evidence_author_t0_capture_result_invalid",
                "E-4 did not capture the prior network-time state",
            )
    elif step_id == "quiet-mac-prep":
        required = (
            "OK: passwordless powermetrics works.",
            "OK: display verification reports all online displays asleep.",
            "OK: post-arm evidence reports screensaver disengaged.",
        )
        if "FAIL:" in stdout or any(item not in stdout for item in required):
            raise _refuse(
                "evidence_author_t0_capture_result_invalid",
                "E-7a contains a failed or missing quiet-Mac predicate",
            )
    elif step_id == "prewindow-check":
        if (
            "TIMED OUT" in stdout
            or "BLOCK" in stdout
            or re.search(r"READY after [0-9]+ min\.", stdout) is None
        ):
            raise _refuse(
                "evidence_author_t0_capture_result_invalid",
                "E-7b did not end in the governed READY result",
            )
    elif step_id == "ledger-readiness":
        try:
            value = json.loads(stdout)
        except json.JSONDecodeError as exc:
            raise _refuse(
                "evidence_author_t0_capture_result_invalid",
                "E-8 stdout is not one JSON object",
            ) from exc
        frozen = value.get("frozen_plan") if isinstance(value, Mapping) else None
        if (
            not isinstance(value, Mapping)
            or value.get("status") != "ready"
            or value.get("early_warning_only") is not True
            or not isinstance(frozen, Mapping)
            or frozen.get("path") != str(context.frozen_plan_path)
            or frozen.get("plan_id") != context.plan_id
            or frozen.get("sha256") != context.plan_sha256
        ):
            raise _refuse(
                "evidence_author_t0_capture_result_invalid",
                "E-8 did not echo the R2 path/plan_id/sha256 identity",
            )
    elif step_id == "ledger-reservation":
        try:
            value = json.loads(stdout)
        except json.JSONDecodeError as exc:
            raise _refuse(
                "evidence_author_t0_capture_result_invalid",
                "E-9 stdout is not one JSON object",
            ) from exc
        authorization_events = 0
        for line in stderr.splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(event, Mapping) and event.get("event") == "calibration_pre_reserve_authorized":
                authorization_events += 1
        receipt = value.get("receipt") if isinstance(value, Mapping) else None
        expected_receipt_identity = {
            "session_id": context.assignments["BRACKET_SESSION_ID"],
            "window_id": context.assignments["WINDOW_ID"],
            "plan_id": context.plan_id,
            "plan_sha256": context.plan_sha256,
            "evidence_root_id": context.assignments["EVIDENCE_ROOT_ID"],
            "runs_root": context.assignments["RUNS_ROOT"],
        }
        if (
            not isinstance(value, Mapping)
            or value.get("status") != "reserved"
            or not isinstance(receipt, Mapping)
            or any(
                receipt.get(name) != expected
                for name, expected in expected_receipt_identity.items()
            )
            or authorization_events != 1
        ):
            raise _refuse(
                "evidence_author_t0_capture_result_invalid",
                "E-9 lacks the bound receipt or unique pre-reserve authorization",
            )


def _capture_step_with_dependencies(
    step_id: str,
    pack_root: Path | str,
    custody_root: Path | str,
    window_plan_root: Path | str,
    *,
    prompt: Callable[[str], str] = input,
    execute: Callable[..., subprocess.CompletedProcess[bytes]] = _execute,
    monotonic_ns: Callable[[], int] = time.monotonic_ns,
    utc_now: Callable[[], str] = readiness._utc_now,
) -> dict[str, object]:
    if step_id not in STEP_FILENAMES:
        raise _refuse(
            "evidence_author_t0_capture_usage_invalid", f"unknown T-0 step: {step_id}"
        )
    context = _load_context(pack_root, custody_root, window_plan_root)
    derived_paths = _prepare_derived_inputs(context)
    _require_sequence(context, step_id)
    if step_id == "clock-prior-state":
        derived_paths.append(
            _clock_attestation(
                context, prompt=prompt, monotonic_ns=monotonic_ns, utc_now=utc_now
            )
        )
    argv = _command_for_step(context, step_id)
    starting_boot = _current_boot_session_id()
    if starting_boot != context.boot_session_id:
        raise _refuse(
            "evidence_author_t0_capture_boot_probe_failed",
            "boot session changed before command execution",
        )
    started = monotonic_ns()
    if step_id == "clock-prior-state":
        completed = _interactive_prior_state(prompt=prompt)
    else:
        completed = execute(argv, cwd=context.repository)
    finished = monotonic_ns()
    ending_boot = _current_boot_session_id()
    if ending_boot != starting_boot:
        raise _refuse(
            "evidence_author_t0_capture_boot_probe_failed",
            "boot session changed during command execution",
        )
    stdout = _text(completed.stdout)
    stderr = _text(completed.stderr)
    capture = {
        "schema_version": COMMAND_CAPTURE_SCHEMA,
        "step_id": step_id,
        "argv": list(argv),
        "cwd": str(context.repository),
        "exit_code": int(completed.returncode),
        "stdout": stdout,
        "stderr": stderr,
        "started_monotonic_ns": started,
        "finished_monotonic_ns": finished,
        "boot_session_id": starting_boot,
    }
    if completed.returncode != 0:
        raise _refuse(
            "evidence_author_t0_capture_command_failed",
            f"{step_id} exited {completed.returncode}; no capture was published",
        )
    if (
        step_id == "prewindow-check"
        and finished - started < 600 * 1_000_000_000
    ):
        raise _refuse(
            "evidence_author_t0_capture_result_invalid",
            "E-7b returned before the required 600-second continuous dwell; no capture was published",
        )
    _validate_result(context, step_id, stdout, stderr)
    capture_path = context.input_root / STEP_FILENAMES[step_id]
    _write_no_clobber(
        capture_path, readiness.render_json(capture), accept_identical=False
    )
    return {
        "status": "PASS",
        "step_id": step_id,
        "capture_path": str(capture_path),
        "derived_input_paths": derived_paths,
        "next_step": (
            STEP_ORDER[STEP_ORDER.index(step_id) + 1]
            if step_id != STEP_ORDER[-1]
            else "author_arm_evidence_t0"
        ),
    }


def _capture_step_for_test(
    step_id: str,
    pack_root: Path | str,
    custody_root: Path | str,
    window_plan_root: Path | str,
    *,
    prompt: Callable[[str], str] = input,
    execute: Callable[..., subprocess.CompletedProcess[bytes]] = _execute,
    monotonic_ns: Callable[[], int] = time.monotonic_ns,
    utc_now: Callable[[], str] = readiness._utc_now,
) -> dict[str, object]:
    """Private test hook for deterministic capture dependencies."""

    return _capture_step_with_dependencies(
        step_id,
        pack_root,
        custody_root,
        window_plan_root,
        prompt=prompt,
        execute=execute,
        monotonic_ns=monotonic_ns,
        utc_now=utc_now,
    )


def capture_step(
    step_id: str,
    pack_root: Path | str,
    custody_root: Path | str,
    window_plan_root: Path | str,
) -> dict[str, object]:
    """Run one step through the non-injectable production interface."""

    return _capture_step_with_dependencies(
        step_id,
        pack_root,
        custody_root,
        window_plan_root,
        prompt=input,
        execute=_execute,
        monotonic_ns=time.monotonic_ns,
        utc_now=readiness._utc_now,
    )


class _ArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise _refuse("evidence_author_t0_capture_usage_invalid", message)


def _parser() -> argparse.ArgumentParser:
    parser = _ArgumentParser(description=__doc__)
    parser.add_argument("step_id", choices=STEP_ORDER)
    parser.add_argument("--pack-root", required=True, type=Path)
    parser.add_argument("--custody-root", required=True, type=Path)
    parser.add_argument("--window-plan-root", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args: argparse.Namespace | None = None
    try:
        args = _parser().parse_args(argv)
        result = capture_step(
            args.step_id,
            args.pack_root,
            args.custody_root,
            args.window_plan_root,
        )
    except CaptureT0Error as exc:
        result = {
            "status": "REFUSE",
            "step_id": getattr(args, "step_id", None) if args is not None else None,
            "reason_codes": [exc.reason_code],
            "detail": str(exc),
        }
        code = 2
    except Exception as exc:  # Defensive CLI boundary; never emit a traceback as authority.
        result = {
            "status": "REFUSE",
            "step_id": getattr(args, "step_id", None) if args is not None else None,
            "reason_codes": ["evidence_author_t0_capture_internal_error"],
            "detail": str(exc),
        }
        code = 2
    else:
        code = 0
    sys.stdout.buffer.write(readiness.render_json(result))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
