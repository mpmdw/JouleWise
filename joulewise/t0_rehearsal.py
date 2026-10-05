"""Mechanical judgment for historical T-0 rehearsal and s1 qualification.

A *rehearsal evidence bundle* is an immutable set of custodied artifacts plus
their already-parsed values.  This module performs no collection and launches
no rehearsal: callers supply the bytes that a supervisor and the production
tools recorded.  Each ``evaluate_gN`` function rebuilds one row of the ruled
ten-gate table and returns ``PASS``, ``FAIL``, or ``UNRULED`` with the evidence
it used.  ``compose_overall_verdict`` is the sole composition rule: one FAIL
makes the rehearsal FAIL; otherwise any UNRULED makes it INCOMPLETE; only ten
PASS results can make it PASS.

``evaluate_qualification`` uses the ruling-76 eight-gate subset and records
G6/G7 as NOT_APPLICABLE. It does not change the historical verdict wire format.

The terms used below are mechanical.  A *custody document* is a canonical JSON
artifact found under the declared T-0 namespace.  A *RAW anchor* is
``CLOCK_REALTIME - CLOCK_MONOTONIC_RAW``.  An *agreement interval* is the
intersection of every successful parseable SNTP leg's
``offset +/- uncertainty`` interval.  A *production root* is one of the
production runs, custody, quarantine, backup, or ledger roots enumerated in
the custodied bundle manifest.  The rehearsal root must not contain, or be
contained by, any such root.
"""

from __future__ import annotations
import json
import os
import stat
import subprocess
import time
import queue
import threading
import uuid
from contextvars import ContextVar
from contextlib import contextmanager
import re
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Iterable, Mapping, Sequence
from unittest import mock

from joulewise import arm_readiness as readiness
from joulewise import arm_readiness_evidence_t0 as t0_author
from joulewise import kernel_clock
from joulewise import clock_reference
from joulewise import network_time_off


REHEARSAL_RECEIPT_CLASS = "T0_UNATTENDED_SUPERVISED_REHEARSAL"
REHEARSAL_WINDOW_PREFIX = "rehearsal-t0-unattended-"
G7_CONTROL_SCHEMA = "joulewise.pack_night_g7_control.v1"

EXECUTION_SCHEMA = "joulewise.t0_unattended_execution_record.v1"
QUALIFICATION_EXECUTION_SCHEMA = "joulewise.v5_qualification_execution_record.v1"
QUALIFICATION_STAGE_SCHEMA = "joulewise.v5_qualification_lifecycle_stage.v1"
D149_SCHEMA = "joulewise.t0_unattended_d149_go_receipt.v1"
REHEARSAL_RECEIPT_SCHEMA = "joulewise.t0_unattended_rehearsal_receipt.v1"
PROCESS_LINEAGE_SCHEMA = "joulewise.t0_unattended_process_lineage.v1"
LIFECYCLE_SCHEMA = "joulewise.t0_unattended_lifecycle.v1"
QUALIFICATION_LIFECYCLE_SCHEMA = "joulewise.v5_qualification_lifecycle.v1"
FALSIFIER_SCHEMA = "joulewise.t0_unattended_falsifier_controls.v1"
POSITIVE_CONTROL_SCHEMA = "joulewise.t0_unattended_anchor_positive_control.v1"

_SHA256_RE = re.compile(r"[0-9a-f]{64}")
_HID_IDLE_RE = re.compile(r'^\s*"HIDIdleTime"\s*=\s*([0-9]+)\s*$')
_AGENT_TOKEN_RE = re.compile(r"(?:^|[/\s])(codex|claude|t3)(?:[/\s]|$)", re.I)
_CLOCK_ROW_DEFINITION = {
    "applicability_rule": "ALWAYS",
    "evaluation_phase": "ARM_ONLY",
    "predicate_id": "clock.correct_and_prior_state.v1",
    "required_evidence_kinds": ["CLOCK_ATTESTATION"],
    "row_id": "clock.correct_and_prior_state",
}
_LIFECYCLE_STAGES = (
    "launch",
    "capability_consumption",
    "capture",
    "claim_backup",
    "bound_backup",
    "close_out",
    "restore",
)
_EXECUTION_KEYS = {"schema_version", "sequence_completed", "processes"}
_EXECUTION_PROCESS_KEYS = {
    "role",
    "pid",
    "argv",
    "stdin_fd0_target",
    "state",
    "exit_code",
    "prompt_count",
    "eof_refusal",
    "timed_out",
}
_REHEARSAL_RECEIPT_KEYS = {
    "schema_version",
    "receipt_class",
    "claim_eligible",
    "window_id",
    "custody_root",
    "acceptance_target",
}
_PROCESS_LINEAGE_KEYS = {
    "schema_version",
    "agent_pid",
    "agent_exit_monotonic_ns",
    "capture_started_monotonic_ns",
    "capture_finished_monotonic_ns",
    "pre_launch_census",
    "capture_censuses",
}
_PROCESS_CENSUS_KEYS = {"processes"}
_PROCESS_KEYS = {"pid", "argv"}
_LIFECYCLE_KEYS = {
    "schema_version",
    "stages",
    "operator_actions_at_t0",
    "human_interventions",
}
_LIFECYCLE_STAGE_KEYS = {"stage_id", "status", "evidence"}
_FALSIFIER_KEYS = {
    "schema_version",
    "author_inputs",
    "author_cases",
    "arm_cases",
}
_FALSIFIER_CASE_KEYS = {
    "delta_ns",
    "expected_status",
    "expected_reason_code",
    "pass_namespace_published",
}
_AUTHOR_INPUT_KEYS = {
    "reference_server_count",
    "reference_midpoint_seconds",
    "reference_bound_seconds",
    "r0_anchor_realtime_ns",
    "r0_anchor_monotonic_raw_ns",
    "r0_anchor_read_skew_ns",
    "r0_batch_finished_monotonic_raw_ns",
    "clock_reference_capture_finished_monotonic_ns",
    "clock_disable_started_monotonic_ns",
    "clock_disable_finished_monotonic_ns",
    "r1_batch_started_monotonic_ns",
    "r1_batch_started_monotonic_raw_ns",
    "author_anchor_realtime_ns",
    "author_anchor_monotonic_raw_ns",
    "author_anchor_read_skew_ns",
    "r1_batch_finished_monotonic_ns",
}
_POSITIVE_CONTROL_KEYS = {
    "schema_version",
    "performed_by",
    "outside_t0_sequence",
    "network_time_reenabled",
    "forced_resync",
    "anchor_before_ns",
    "anchor_after_ns",
    "author_refusal_reason_code",
}


# An opt-in journal records observations at spawn/wait, never PASS labels.
# Keep it in-process: an inherited shell variable cannot select fixture data.
_PROCESS_JOURNAL = ContextVar("rehearsal_process_journal", default=None)
PROCESS_EVENT_SCHEMA = "joulewise.t0_rehearsal_process_event.v1"


def append_observation(path: Path, value: Mapping[str, Any]) -> None:
    from joulewise.calibration_ledger import canonical_json_bytes
    payload = canonical_json_bytes(value) + b"\n"
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND | os.O_NOFOLLOW, 0o600)
    try:
        if os.write(descriptor, payload) != len(payload):
            raise OSError("short observation write")
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


class _ProcessJournal:
    """A capped queue keeps custody I/O off the process supervision seams."""
    def __init__(self, path, *, observe_only=False):
        self.path = Path(path)
        self.observe_only = observe_only
        self.journal_id = str(uuid.uuid4())
        self.pending = queue.Queue(maxsize=1024)
        self.count = 0
        self.error = None
        self.writer = threading.Thread(target=self._write, daemon=True,
                                       name="rehearsal-process-journal")
        self.writer.start()

    def _write(self):
        try:
            while True:
                value = self.pending.get()
                if value is None:
                    append_observation(self.path, {
                        "schema_version": PROCESS_EVENT_SCHEMA, "event": "seal",
                        "journal_id": self.journal_id, "record_count": self.count})
                    return
                append_observation(self.path, value)
                self.count += 1
        except Exception as exc:
            self.error = str(exc)

    def emit(self, value):
        value = dict(value, journal_id=self.journal_id)
        try:
            self.pending.put_nowait(value)
        except queue.Full:
            # Retain control of the child even if its observation was lost.
            # This context can never seal successfully after overflow.
            self.error = "process observation queue overflow"

    def close(self):
        try:
            self.pending.put_nowait(None)
        except queue.Full:
            self.error = "process observation queue overflow"
        self.writer.join(timeout=2)
        if self.writer.is_alive() or self.error is not None:
            if not self.observe_only:
                raise ValueError("process observation journal incomplete: " + (self.error or "drain timed out"))
            # Missing seal is itself fail-closed evidence even if this write fails.
            try:
                append_observation(self.path.with_name("producer-faults.jsonl"), {
                    "schema_version": "joulewise.v5_qualification_producer_fault.v1",
                    "producer": "process_journal", "status": "REFUSED"})
            except Exception:
                pass


@contextmanager
def process_journal(path: Path, *, observe_only=False):
    journal = _ProcessJournal(path, observe_only=observe_only)
    token = _PROCESS_JOURNAL.set(journal)
    try:
        yield journal
    finally:
        _PROCESS_JOURNAL.reset(token)
        journal.close()


class ObservedProcess(subprocess.Popen):
    """Popen with retained DEVNULL descriptor custody and observed reaping.

    fd0 is identified from the actual descriptor supplied to Popen, rather
    than inferred later from argv. A non-DEVNULL launch is retained as such.
    """
    def __init__(self, args, **kwargs):
        self._journal = _PROCESS_JOURNAL.get()
        self._exit_recorded = False
        self._timed_out = False
        self._command = list(args) if not isinstance(args, str) else [args]
        self._spawned_ns = time.monotonic_ns()
        self._fd0 = "unobserved"
        descriptor = None
        if self._journal is not None and kwargs.get("stdin") == subprocess.DEVNULL:
            try:
                descriptor = os.open(os.devnull, os.O_RDONLY)
                actual, expected = os.fstat(descriptor), os.stat(os.devnull)
                if (stat.S_ISCHR(actual.st_mode) and
                        (actual.st_dev, actual.st_ino, actual.st_rdev) ==
                        (expected.st_dev, expected.st_ino, expected.st_rdev)):
                    self._fd0 = "/dev/null"
                kwargs["stdin"] = descriptor
            except BaseException:
                if not self._journal.observe_only:
                    raise
                self._journal.error = "fd0 observation fault"
        try:
            super().__init__(args, **kwargs)
        finally:
            if descriptor is not None:
                try:
                    os.close(descriptor)
                except BaseException:
                    if not self._journal.observe_only:
                        raise
                    self._journal.error = "fd0 observation close fault"
        self._event("spawn", None)

    def _event(self, event, exit_code):
        if self._journal is not None:
            try:
                value = {
                    "schema_version": PROCESS_EVENT_SCHEMA, "event": event,
                    "pid": self.pid, "argv": self._command,
                    "stdin_fd0_target": self._fd0, "exit_code": exit_code,
                    "timed_out": self._timed_out,
                    "monotonic_ns": time.monotonic_ns(),
                    "spawned_monotonic_ns": self._spawned_ns,
                }
                self._journal.emit(value)
            except BaseException:
                if not self._journal.observe_only:
                    raise
                self._journal.error = "process event producer fault"

    def communicate(self, *args, **kwargs):
        stdout, stderr = super().communicate(*args, **kwargs)
        from joulewise.night_gate import AGENT_CENSUS_ARGV
        if self._journal is not None and tuple(self._command) == AGENT_CENSUS_ARGV:
            try:
                self._journal.emit({"schema_version": PROCESS_EVENT_SCHEMA,
                    "event": "output", "pid": self.pid, "argv": self._command,
                    "spawned_monotonic_ns": self._spawned_ns,
                    "stdout": stdout.decode() if isinstance(stdout, bytes) else stdout})
            except BaseException:
                if not self._journal.observe_only:
                    raise
                self._journal.error = "process output producer fault"
        return stdout, stderr

    def _observe_exit(self, code):
        if code is not None and not self._exit_recorded:
            self._event("exit", code)
            self._exit_recorded = True
        return code

    def wait(self, *args, **kwargs):
        return self._observe_exit(super().wait(*args, **kwargs))

    def poll(self):
        return self._observe_exit(super().poll())


def observed_process_type():
    return subprocess.Popen if _PROCESS_JOURNAL.get() is None else ObservedProcess


def observed_popen(args, **kwargs):
    if _PROCESS_JOURNAL.get() is None:
        return subprocess.Popen(args, **kwargs)
    kwargs.setdefault("stdin", subprocess.DEVNULL)
    return ObservedProcess(args, **kwargs)


def observed_run(args, **kwargs):
    """subprocess.run semantics with the same spawn/reap journal seam."""
    if _PROCESS_JOURNAL.get() is None:
        return subprocess.run(args, **kwargs)
    input = kwargs.pop("input", None)
    capture_output = kwargs.pop("capture_output", False)
    timeout = kwargs.pop("timeout", None)
    check = kwargs.pop("check", False)
    if input is not None:
        if "stdin" in kwargs:
            raise ValueError("stdin and input arguments may not both be used")
        kwargs["stdin"] = subprocess.PIPE
    if capture_output:
        if "stdout" in kwargs or "stderr" in kwargs:
            raise ValueError("stdout/stderr with capture_output")
        kwargs.update(stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if input is None:
        kwargs.setdefault("stdin", subprocess.DEVNULL)
    with ObservedProcess(args, **kwargs) as process:
        process._timed_out = False
        try:
            stdout, stderr = process.communicate(input, timeout=timeout)
        except subprocess.TimeoutExpired:
            process._timed_out = True
            process.kill()
            process.communicate()
            raise
        code = process.wait()
        if check and code:
            raise subprocess.CalledProcessError(code, args, output=stdout, stderr=stderr)
        return subprocess.CompletedProcess(args, code, stdout, stderr)


class GateStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNRULED = "UNRULED"


class OverallVerdict(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    INCOMPLETE = "INCOMPLETE"


@dataclass(frozen=True)
class EvidenceArtifact:
    """One regular custodied file and its optional strict-JSON value."""

    relative_path: str
    path: Path
    raw: bytes
    sha256: str
    value: object | None = None
    parse_error: str | None = None

    def citation(self) -> dict[str, object]:
        result: dict[str, object] = {
            "path": self.relative_path,
            "sha256": self.sha256,
        }
        if self.parse_error is not None:
            result["parse_error"] = self.parse_error
        return result


@dataclass(frozen=True)
class ProductionRoot:
    """One role-labelled, resolved root used by production."""

    role: str
    path: Path
    resolution_error: str | None = None


@dataclass(frozen=True)
class EvidenceBundle:
    """All bytes needed to judge one already-performed rehearsal."""

    custody_root: Path
    t0_namespace_root: Path
    manifest: EvidenceArtifact
    artifacts: tuple[EvidenceArtifact, ...]
    record_paths: Mapping[str, str]
    production_roots: tuple[ProductionRoot, ...]
    load_issues: tuple[str, ...] = ()

    def artifact(self, relative_path: str) -> EvidenceArtifact | None:
        return next(
            (item for item in self.artifacts if item.relative_path == relative_path),
            None,
        )

    def record(self, name: str) -> EvidenceArtifact | None:
        relative = self.record_paths.get(name)
        return None if relative is None else self.artifact(relative)

    def namespace_documents(self) -> tuple[EvidenceArtifact, ...]:
        try:
            namespace = self.t0_namespace_root.resolve()
        except OSError:
            namespace = self.t0_namespace_root.absolute()
        result = []
        for artifact in self.artifacts:
            try:
                artifact.path.resolve().relative_to(namespace)
            except (OSError, ValueError):
                continue
            if artifact.relative_path.endswith(".json"):
                result.append(artifact)
        return tuple(result)


@dataclass(frozen=True)
class GateResult:
    gate_id: str
    name: str
    status: GateStatus
    message: str
    mechanical_evidence: tuple[Mapping[str, object], ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "gate_id": self.gate_id,
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "mechanical_evidence": [dict(item) for item in self.mechanical_evidence],
        }


def compose_overall_verdict(statuses: Iterable[GateStatus | str]) -> OverallVerdict:
    """Compose gate states without ever treating missing authority as success."""

    normalized = tuple(GateStatus(item) for item in statuses)
    if not normalized:
        raise ValueError("at least one gate status is required")
    if GateStatus.FAIL in normalized:
        return OverallVerdict.FAIL
    if GateStatus.UNRULED in normalized:
        return OverallVerdict.INCOMPLETE
    return OverallVerdict.PASS


def parse_hid_idle_time(raw: str) -> int:
    """Strictly parse the sole decimal ``HIDIdleTime`` property from ioreg.

    ``HIDIdleTime`` measures local keyboard, trackpad, and mouse input only.  A
    human typing over SSH does not move it; closed stdin, the source/capture
    census, process evidence, and the supervised threat model cover that
    boundary rather than this parser.
    """

    candidates = []
    mentioned = []
    for line in raw.splitlines():
        if "HIDIdleTime" not in line:
            continue
        mentioned.append(line)
        matched = _HID_IDLE_RE.fullmatch(line)
        if matched is not None:
            candidates.append(int(matched.group(1)))
    if not mentioned:
        raise ValueError("HIDIdleTime output is absent")
    if len(mentioned) != 1 or len(candidates) != 1:
        if len(mentioned) > 1:
            raise ValueError("HIDIdleTime output is ambiguous")
        raise ValueError("HIDIdleTime output is unparsable")
    return candidates[0]


def _result(
    gate_id: str,
    name: str,
    status: GateStatus,
    message: str,
    *evidence: Mapping[str, object],
) -> GateResult:
    return GateResult(gate_id, name, status, message, tuple(evidence))


def _json_record(
    bundle: EvidenceBundle, name: str
) -> tuple[EvidenceArtifact | None, Mapping[str, Any] | None, str | None]:
    artifact = bundle.record(name)
    if artifact is None:
        return None, None, f"{name} record is absent"
    if artifact.parse_error is not None:
        return artifact, None, f"{name} record is not canonical strict JSON: {artifact.parse_error}"
    if not isinstance(artifact.value, Mapping):
        return artifact, None, f"{name} record is not one JSON object"
    return artifact, artifact.value, None


def _walk_mappings(value: object) -> Iterable[Mapping[str, Any]]:
    if isinstance(value, Mapping):
        yield value
        for child in value.values():
            yield from _walk_mappings(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_mappings(child)


def _clock_fact_documents(
    bundle: EvidenceBundle,
) -> list[tuple[EvidenceArtifact, Mapping[str, Any], Mapping[str, Any]]]:
    found = []
    for artifact in bundle.namespace_documents():
        value = artifact.value
        if not isinstance(value, Mapping):
            continue
        facts = value.get("facts")
        if not isinstance(facts, list):
            continue
        for fact in facts:
            if (
                isinstance(fact, Mapping)
                and fact.get("fact_id") == "clock.correct_and_prior_state.v1"
            ):
                found.append((artifact, value, fact))
    return found


def _clock_receipt(
    bundle: EvidenceBundle,
) -> tuple[EvidenceArtifact, Mapping[str, Any], Mapping[str, Any]]:
    found = [
        item
        for item in _clock_fact_documents(bundle)
        if item[1].get("kind") == "CLOCK_ATTESTATION"
        and item[1].get("status") == "PASS"
        and "source_kind" in item[2]
    ]
    if len(found) != 1:
        raise ValueError(
            "receipt census must contain exactly one PASS CLOCK_ATTESTATION clock fact"
        )
    return found[0]


def _source_for_row(
    bundle: EvidenceBundle, row_id: str
) -> tuple[EvidenceArtifact, Mapping[str, Any]]:
    found = [
        (artifact, artifact.value)
        for artifact in bundle.namespace_documents()
        if isinstance(artifact.value, Mapping)
        and artifact.value.get("row_id") == row_id
        and isinstance(artifact.value.get("probes"), list)
    ]
    if len(found) != 1:
        raise ValueError(f"source census must contain exactly one {row_id} source")
    artifact, value = found[0]
    return artifact, value  # type: ignore[return-value]


def _capture_for_step(
    bundle: EvidenceBundle, step_id: str
) -> tuple[EvidenceArtifact, Mapping[str, Any]]:
    found = [
        (artifact, artifact.value)
        for artifact in bundle.namespace_documents()
        if isinstance(artifact.value, Mapping)
        and artifact.value.get("schema_version")
        == "joulewise.arm_readiness_t0_command_capture.v1"
        and artifact.value.get("step_id") == step_id
    ]
    if len(found) != 1:
        raise ValueError(f"command census must contain exactly one {step_id} capture")
    artifact, value = found[0]
    return artifact, value  # type: ignore[return-value]


def _artifact_for_path(bundle: EvidenceBundle, path_text: object) -> EvidenceArtifact | None:
    if not isinstance(path_text, str):
        return None
    candidate = Path(path_text)
    if not candidate.is_absolute():
        return bundle.artifact(candidate.as_posix())
    try:
        target = candidate.resolve()
    except OSError:
        target = candidate.absolute()
    for artifact in bundle.artifacts:
        try:
            observed = artifact.path.resolve()
        except OSError:
            observed = artifact.path.absolute()
        if observed == target:
            return artifact
    return None


def _verify_artifact_reference(
    bundle: EvidenceBundle, reference: object, *, label: str
) -> EvidenceArtifact:
    if not isinstance(reference, Mapping) or set(reference) != {"path", "sha256"}:
        raise ValueError(f"{label} artifact reference is malformed")
    digest = reference.get("sha256")
    if not isinstance(digest, str) or _SHA256_RE.fullmatch(digest) is None:
        raise ValueError(f"{label} artifact SHA-256 is malformed")
    artifact = _artifact_for_path(bundle, reference.get("path"))
    if artifact is None:
        raise ValueError(f"{label} artifact path is absent from custody")
    if artifact.sha256 != digest:
        raise ValueError(f"{label} artifact SHA-256 does not match custodied bytes")
    return artifact


def evaluate_g1(bundle: EvidenceBundle) -> GateResult:
    """Evaluate noninteractive execution from the per-process fd-0 record.

    The artifact named ``execution`` in the bundle manifest is the only
    record that carries top-level and governed-subprocess fd-0 targets plus
    completion/prompt/timeout outcomes.  Current D-134 command captures do not
    record stdin at all, so absence of this added record is UNRULED, not PASS.
    """

    name = "NONINTERACTIVE EXECUTION"
    artifact, value, error = _json_record(bundle, "execution")
    if artifact is None:
        return _result(
            "G1",
            name,
            GateStatus.UNRULED,
            "execution evidence is unavailable: current command captures do not record "
            "top-level or subprocess stdin binding",
        )
    if error is not None or value is None:
        return _result("G1", name, GateStatus.FAIL, error or "invalid execution record", artifact.citation())
    qualified = value.get("schema_version") == QUALIFICATION_EXECUTION_SCHEMA
    if set(value) != _EXECUTION_KEYS or value.get("schema_version") not in {EXECUTION_SCHEMA, QUALIFICATION_EXECUTION_SCHEMA}:
        return _result("G1", name, GateStatus.FAIL, "execution record schema is invalid", artifact.citation())
    processes = value.get("processes")
    if not isinstance(processes, list) or not processes:
        return _result("G1", name, GateStatus.FAIL, "execution record has no governed process census", artifact.citation())
    top_levels = 0
    for index, process in enumerate(processes):
        keys = ((_EXECUTION_PROCESS_KEYS - {"prompt_count", "eof_refusal"}) |
                {"expected_outcome", "stdout"}) if qualified else _EXECUTION_PROCESS_KEYS
        if not isinstance(process, Mapping) or set(process) != keys:
            return _result("G1", name, GateStatus.FAIL, f"governed process {index} record is malformed", artifact.citation())
        if process.get("role") == "top_level":
            top_levels += 1
        if process.get("stdin_fd0_target") != "/dev/null":
            return _result("G1", name, GateStatus.FAIL, f"governed process {index} stdin was not bound to /dev/null", artifact.citation())
        from joulewise.night_gate import AGENT_CENSUS_ARGV
        census = qualified and process.get("argv") == list(AGENT_CENSUS_ARGV)
        expected = {"exit_code": 1, "stdout": ""} if census else {"exit_code": 0}
        if qualified and process.get("expected_outcome") != expected:
            return _result("G1", name, GateStatus.FAIL, f"governed process {index} expected outcome is not registered", artifact.citation())
        if (process.get("state") != "EXITED" or qualified and type(process.get("exit_code")) is not int
                or process.get("exit_code") != expected["exit_code"]
                or census and process.get("stdout") != ""):
            return _result("G1", name, GateStatus.FAIL, f"governed process {index} did not complete successfully", artifact.citation())
        if not qualified and process.get("prompt_count") != 0:
            return _result("G1", name, GateStatus.FAIL, f"governed process {index} recorded a surviving prompt", artifact.citation())
        if not qualified and process.get("eof_refusal") is not False:
            return _result("G1", name, GateStatus.FAIL, f"governed process {index} recorded an EOF refusal", artifact.citation())
        if process.get("timed_out") is not False:
            return _result("G1", name, GateStatus.FAIL, f"governed process {index} hung or timed out", artifact.citation())
    if top_levels != 1 or value.get("sequence_completed") is not True:
        return _result("G1", name, GateStatus.FAIL, "top-level T-0 sequence did not record one complete execution", artifact.citation())
    message = ("all governed processes met registered outcomes with fd 0 at /dev/null, no timeout and a complete sequence"
               if qualified else "top-level and all governed processes completed with fd 0 at /dev/null and no prompt, EOF refusal, or hang")
    return _result("G1", name, GateStatus.PASS, message, artifact.citation())


def evaluate_g2(bundle: EvidenceBundle) -> GateResult:
    """Evaluate the complete receipt/source/command census."""

    name = "RECEIPT / SOURCE CENSUS"
    documents = bundle.namespace_documents()
    if not documents:
        return _result("G2", name, GateStatus.FAIL, "T-0 custody namespace contains no JSON documents")
    invalid = [item for item in documents if item.parse_error is not None]
    if invalid:
        return _result("G2", name, GateStatus.FAIL, f"T-0 census contains noncanonical JSON: {invalid[0].relative_path}", invalid[0].citation())
    for artifact in documents:
        for item in _walk_mappings(artifact.value):
            if item.get("source_kind") == "OPERATOR_ATTESTATION":
                return _result("G2", name, GateStatus.FAIL, f"OPERATOR_ATTESTATION fact found in {artifact.relative_path}", artifact.citation())
            argv = item.get("argv")
            if isinstance(argv, list) and argv and argv[0] == "operator-interactive":
                return _result("G2", name, GateStatus.FAIL, f"operator-interactive command capture found in {artifact.relative_path}", artifact.citation())
    clock = [item for item in _clock_fact_documents(bundle) if "source_kind" in item[2]]
    if len(clock) != 1:
        return _result("G2", name, GateStatus.FAIL, "clock fact census is absent or ambiguous")
    if clock[0][2].get("source_kind") != "PROBE":
        return _result("G2", name, GateStatus.FAIL, "clock fact source_kind is not PROBE", clock[0][0].citation())
    return _result(
        "G2",
        name,
        GateStatus.PASS,
        "all T-0 documents contain zero OPERATOR_ATTESTATION facts, zero operator-interactive argvs, and one PROBE clock fact",
        *[item.citation() for item in documents],
    )


def evaluate_g3(bundle: EvidenceBundle) -> GateResult:
    """Evaluate the local-HID idle witness against the measured T-0 span."""

    name = "LOCAL-INPUT WITNESS"
    artifact = bundle.record("hid_idle")
    if artifact is None:
        return _result("G3", name, GateStatus.FAIL, "HIDIdleTime output is absent")
    try:
        text = artifact.raw.decode("utf-8", errors="strict")
        idle_ns = parse_hid_idle_time(text)
        _receipt_artifact, _receipt, fact = _clock_receipt(bundle)
        value = fact.get("value")
        if not isinstance(value, Mapping):
            raise ValueError("clock fact value is absent")
        r0_raw = value.get("r0_anchor_monotonic_raw_ns")
        author_raw = value.get("anchor_monotonic_raw_ns")
        if not _real_int(r0_raw) or not _real_int(author_raw):
            raise ValueError("clock fact T-0 span endpoints are not integers")
        span_ns = author_raw - r0_raw
    except (UnicodeError, ValueError) as exc:
        return _result("G3", name, GateStatus.FAIL, str(exc), artifact.citation())
    if idle_ns < span_ns:
        return _result("G3", name, GateStatus.FAIL, f"HIDIdleTime {idle_ns} ns is below measured T-0 span {span_ns} ns", artifact.citation())
    return _result("G3", name, GateStatus.PASS, f"strict HIDIdleTime {idle_ns} ns covers measured T-0 span {span_ns} ns", artifact.citation())


def _real_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _recompute_r1_agreement(source: Mapping[str, Any]) -> t0_author._ReferenceAgreement:
    probes = source.get("probes")
    if not isinstance(probes, list) or len(probes) != len(clock_reference.SERVER_ROSTER):
        raise ValueError("R1 source does not contain the fixed three-leg roster")
    legs = []
    for server, probe in zip(clock_reference.SERVER_ROSTER, probes):
        if not isinstance(probe, Mapping) or probe.get("argv") != clock_reference.build_sntp_argv(server):
            raise ValueError("R1 source does not prove the fixed one-attempt roster")
        stdout = probe.get("stdout")
        exit_code = probe.get("exit_code")
        if not isinstance(stdout, str) or not _real_int(exit_code):
            raise ValueError("R1 probe result fields are malformed")
        parsed = clock_reference.parse_sntp_stdout(stdout, server=server) if exit_code == 0 else None
        if parsed is not None:
            legs.append((server, parsed))
    try:
        return t0_author._reference_agreement(legs, kind="CLOCK_ATTESTATION", label="R1 reference")
    except t0_author.T0EvidenceAuthoringError as exc:
        raise ValueError(str(exc)) from exc


def evaluate_g4(bundle: EvidenceBundle) -> GateResult:
    """Recompute clock mechanics from raw R0/R1 bytes and RAW endpoints.

    R0 schema/roster parsing and both agreement calculations deliberately call
    the current author's helpers.  R1 lacks per-leg timestamps in the
    published source, so its fixed roster is checked over the source probes and
    the author's shared ``_reference_agreement`` helper performs the arithmetic.
    Stored gate booleans are never used as the answer.
    """

    name = "CLOCK MECHANICS"
    evidence: list[Mapping[str, object]] = []
    try:
        receipt_artifact, receipt, receipt_fact = _clock_receipt(bundle)
        source_artifact, source = _source_for_row(bundle, "clock.correct_and_prior_state")
        evidence.extend((receipt_artifact.citation(), source_artifact.citation()))
        source_facts = source.get("facts")
        if not isinstance(source_facts, list) or len(source_facts) != 1 or not isinstance(source_facts[0], Mapping):
            raise ValueError("clock source facts are malformed")
        value = source_facts[0].get("value")
        if not isinstance(value, Mapping) or receipt_fact.get("value") != value:
            raise ValueError("clock receipt value differs from the published source")
        keys = (readiness._CLOCK_PROBE_RESIDUAL_VALUE_KEYS if "anchor_check_version" in value
                else readiness._CLOCK_PROBE_VALUE_KEYS)
        if set(value) != keys:
            raise ValueError("clock fact keys do not match its recorded anchor semantics")
        if receipt_fact.get("source_sha256") != source_artifact.sha256:
            raise ValueError("clock receipt source SHA-256 does not match custodied source bytes")

        input_refs = source.get("input_artifacts")
        if not isinstance(input_refs, list):
            raise ValueError("clock source input-artifact census is absent")
        r0_candidates = []
        for reference in input_refs:
            if isinstance(reference, Mapping) and str(reference.get("path", "")).endswith("clock-reference.json"):
                r0_candidates.append(_verify_artifact_reference(bundle, reference, label="R0 clock-reference"))
        if len(r0_candidates) != 1:
            raise ValueError("clock source must hash-bind exactly one R0 clock-reference capture")
        r0_capture_artifact = r0_candidates[0]
        evidence.append(r0_capture_artifact.citation())
        r0_capture = r0_capture_artifact.value
        if not isinstance(r0_capture, Mapping) or r0_capture.get("step_id") != "clock-reference" or r0_capture.get("exit_code") != 0:
            raise ValueError("R0 clock-reference command capture did not complete")
        stdout = r0_capture.get("stdout")
        if not isinstance(stdout, str):
            raise ValueError("R0 clock-reference stdout is absent")
        r0 = readiness.parse_json_bytes(stdout.encode("utf-8"), require_canonical=True)
        legs = t0_author._validate_reference_object(
            r0,
            kind="CLOCK_ATTESTATION",
            label="R0 clock reference",
            boot_session_id=str(receipt.get("boot_session_id")),
        )
        r0_agreement = t0_author._reference_agreement(legs, kind="CLOCK_ATTESTATION", label="R0 reference")
        if r0["anchor_read_skew_ns"] > 1_000_000:
            raise ValueError("R0 anchor read skew exceeds 1000000 ns")
        for published_name, raw_name in (
            ("r0_anchor_realtime_ns", "anchor_realtime_ns"),
            ("r0_anchor_monotonic_raw_ns", "anchor_monotonic_raw_ns"),
            ("r0_anchor_read_skew_ns", "anchor_read_skew_ns"),
        ):
            if value.get(published_name) != r0.get(raw_name):
                raise ValueError(
                    f"published {published_name} differs from raw R0 clock-reference bytes"
                )

        r1_agreement = _recompute_r1_agreement(source)
        if value.get("reference_server_count") != r1_agreement.server_count:
            raise ValueError("published R1 server count differs from raw probe quorum")
        if value.get("reference_bound_seconds") != float(r1_agreement.bound):
            raise ValueError("published R1 bound differs from raw agreement arithmetic")
        if value.get("comparison_delta_seconds") != float(r1_agreement.midpoint):
            raise ValueError("published R1 midpoint differs from raw agreement arithmetic")
        if r0_agreement.bound > Decimal("0.5") or r1_agreement.bound > Decimal("0.5"):
            raise ValueError("R0 or R1 agreement bound exceeds 0.5 seconds")

        integer_names = (
            "r0_anchor_realtime_ns",
            "r0_anchor_monotonic_raw_ns",
            "r0_anchor_read_skew_ns",
            "anchor_realtime_ns",
            "anchor_monotonic_raw_ns",
            "anchor_read_skew_ns",
            "r1_batch_started_monotonic_raw_ns",
            "r1_batch_finished_monotonic_raw_ns",
        )
        if any(not _real_int(value.get(field)) for field in integer_names):
            raise ValueError("published clock endpoint is not an integer")
        span = value["anchor_monotonic_raw_ns"] - value["r0_anchor_monotonic_raw_ns"]
        if not 600_000_000_000 <= span <= 3_600_000_000_000:
            raise ValueError("measured T-0 span is outside 600 through 3600 seconds")
        anchor_delta = abs(
            (value["anchor_realtime_ns"] - value["anchor_monotonic_raw_ns"])
            - (value["r0_anchor_realtime_ns"] - value["r0_anchor_monotonic_raw_ns"])
        )
        if "anchor_check_version" in value:
            if value["anchor_check_version"] != kernel_clock.ANCHOR_CHECK_VERSION:
                raise ValueError("unsupported anchor check version")
            frequency = kernel_clock.validate_probe(value.get("r0_kernel_frequency"))
            if frequency != r0_capture.get("kernel_frequency"):
                raise ValueError("published R0 frequency differs from custodied probe")
            if value.get("t_stream_max_s") != r0_capture.get("t_stream_max_s"):
                raise ValueError("published stream maximum differs from R0 custody")
            current = kernel_clock.validate_probe(value.get("kernel_frequency"))
            residual = kernel_clock.anchor_residual_ns(
                (value["anchor_realtime_ns"] - value["anchor_monotonic_raw_ns"])
                - (value["r0_anchor_realtime_ns"] - value["r0_anchor_monotonic_raw_ns"]), span, frequency)
            if current["raw_word"] != frequency["raw_word"]:
                raise ValueError("R0-to-author kernel frequency word changed")
            if (residual > 5_000_000 or type(value.get("anchor_residual_ns")) is not float
                    or value["anchor_residual_ns"] != float(residual)):
                raise ValueError("RAW anchor residual exceeds 5000000 ns or differs from arithmetic")
            if (value.get("t_stream_max_s") is not None
                    and not kernel_clock.frequency_gate(frequency, value["t_stream_max_s"])["passes"]):
                raise ValueError("R0 kernel frequency exceeds the stream clock budget")
        elif anchor_delta > 5_000_000:
            raise ValueError("RAW anchor delta exceeds 5000000 ns")
        if value.get("t0_span_ns") != span:
            raise ValueError("published T-0 span differs from RAW endpoint arithmetic")
        if value.get("anchor_delta_ns") != anchor_delta:
            raise ValueError("published RAW anchor delta differs from endpoint arithmetic")
        if value["anchor_read_skew_ns"] > 1_000_000 or value["r0_anchor_read_skew_ns"] > 1_000_000:
            raise ValueError("RAW anchor read skew exceeds 1000000 ns")
        r1_duration = value["r1_batch_finished_monotonic_raw_ns"] - value["r1_batch_started_monotonic_raw_ns"]
        if not 0 <= r1_duration <= 30_000_000_000:
            raise ValueError("R1 batch duration is outside 0 through 30000000000 ns")
        if value.get("r1_batch_duration_ns") != r1_duration:
            raise ValueError("published R1 duration differs from RAW endpoint arithmetic")

        first_off_artifact, first_off = _capture_for_step(bundle, "clock-disable")
        evidence.append(first_off_artifact.citation())
        off_refs = [
            reference
            for reference in input_refs
            if isinstance(reference, Mapping)
            and str(reference.get("path", "")).endswith("clock-disable.json")
        ]
        if len(off_refs) != 1 or _verify_artifact_reference(
            bundle, off_refs[0], label="first exact-Off capture"
        ).relative_path != first_off_artifact.relative_path:
            raise ValueError("clock source does not hash-bind the first exact-Off capture")
        if (
            first_off.get("exit_code") != 0
            or not isinstance(first_off.get("argv"), list)
            or not t0_author._systemsetup_argv(first_off["argv"], ("-setusingnetworktime", "off"))
            or not readiness.network_time_off_stdout_admitted(first_off.get("stdout"))
        ):
            raise ValueError("first exact-Off command result is not mechanically green")
        second_off_artifact, second_off_source = _source_for_row(bundle, "clock.network_time_off")
        evidence.append(second_off_artifact.citation())
        if second_off_source.get("derivation", {}).get("policy") == network_time_off.SCHEMA:
            refs = [ref for ref in second_off_source.get("input_artifacts", [])
                    if str(ref.get("path", "")).endswith(network_time_off.RECEIPT_BASENAME)]
            if len(refs) != 1:
                raise ValueError("OFF receipt source is absent or ambiguous")
            artifact = _verify_artifact_reference(bundle, refs[0], label="settled OFF receipt")
            off = network_time_off.admit(json.loads(artifact.raw))
            network_time_off.seconds_since_receipt(off, {
                "epoch_s": value["anchor_realtime_ns"] / 1e9,
                "monotonic_s": value["r1_batch_finished_monotonic_ns"] / 1e9,
                "boot_id": first_off["boot_session_id"]})
            evidence.append(artifact.citation())
        else:
            second_probes = second_off_source.get("probes")
            if not isinstance(second_probes, list) or len(second_probes) != 1 or not isinstance(second_probes[0], Mapping):
                raise ValueError("second exact-Off source probe is absent or ambiguous")
            second = second_probes[0]
            if (
                second.get("exit_code") != 0
                or not isinstance(second.get("argv"), list)
                or not t0_author._systemsetup_argv(second["argv"], ("-setusingnetworktime", "off"))
                or not readiness.network_time_off_stdout_admitted(second.get("stdout"))
            ):
                raise ValueError("second exact-Off command result is not mechanically green")
    except (ValueError, readiness.ArmReadinessError, t0_author.T0EvidenceAuthoringError) as exc:
        return _result("G4", name, GateStatus.FAIL, str(exc), *evidence)
    return _result(
        "G4",
        name,
        GateStatus.PASS,
        f"raw R0/R1 quorum, intersections, 0.5 s bounds, exact-Off results, {span} ns span, and {anchor_delta} ns RAW-anchor delta recomputed green",
        *evidence,
    )


def evaluate_g5(bundle: EvidenceBundle) -> GateResult:
    """Recompute C1–C5 through retained v3 launch and ARM evidence replay.

    Historical clock mode uses the consumption instant on its recorded boot;
    it never requires a completed night's GO to remain live on today's boot.
    ARM semantics are nevertheless re-derived explicitly (ordinary historical
    launch replay intentionally skips that step).
    """
    name = "PACK GO EVALUATION"
    artifact, value, error = _json_record(bundle, "d149_go")
    evidence = [] if artifact is None else [artifact.citation()]
    try:
        if artifact is None or value is None:
            raise ValueError(error or "pack GO receipt is absent")
        raw = artifact.path.read_bytes()
        if raw != artifact.raw or readiness.sha256_bytes(raw) != artifact.sha256:
            raise ValueError("GO digest changed")
        go = readiness.validate_pack_night_go_receipt(readiness.parse_json_bytes(raw))
        candidates = [item for item in bundle.artifacts
                      if item.path.name.endswith(".consumed.json")
                      and item.path.is_relative_to(bundle.custody_root / go["pack_id"])]
        same_boot = []
        for item in candidates:
            record, _raw, _digest, path = readiness._read_launch_consumption(
                item.path, require_current_boot=False)
            if record["boot_session_id"] == go["boot_session_id"]:
                same_boot.append((item, record, path))
        if len(same_boot) != 1:
            raise ValueError("C5 requires exactly one consumption this boot")
        consumed, record, path = same_boot[0]
        if (record["schema_version"] != readiness.CONSUMPTION_RECEIPT_SCHEMA_V3
                or record["go_receipt"]["sha256"] != artifact.sha256
                or record["go_receipt"]["path"] != str(artifact.path)
                or record["go_receipt"]["receipt_id"] != go["receipt_id"]):
            raise ValueError("C5 consumption does not bind this pack GO")
        evidence.append(consumed.citation())
        # C1 authorization/attempt/confirmation, C2 exact evidence, C3 census,
        # C4 boot/clock/time bounds and C5 persisted attempt are re-read here.
        table, digest = readiness._consumed_confirmation_pair(record, None, None)
        arm, arm_path, pack_root, _pack = readiness._replay_consumed_arm(
            None, record, path, require_current_boot=False, require_unexpired=False,
            replay_arm_semantics=True, step6_confirmation_table=table,
            expected_confirmation_digest=digest)
        readiness.verify_consumed_launch(pack_root, path, require_current_boot=False)
        issued = go["issued_monotonic_ns"]
        if not issued <= record["consumed_at_monotonic_ns"] < go["valid_until_monotonic_ns"]:
            raise ValueError("C4 consumption outside GO interval")
        for item in readiness.scan_receipt_namespace(arm_path.parent, "arm"):
            if (item["receipt"]["boot_session_id"] == arm["boot_session_id"]
                    and item["number"] > int(arm_path.stem.removeprefix("arm-"))):
                raise ValueError("C5 higher-numbered ARM/re-arm this boot")
        for condition in go["conditions"]:
            if not condition["evidence"] or condition["basis"] is not None:
                raise ValueError(f"{condition['condition_id']} evidence/basis")
            for reference in condition["evidence"]:
                used = _verify_artifact_reference(bundle, reference, label=condition["condition_id"])
                if used.path.read_bytes() != used.raw:
                    raise ValueError("condition evidence changed")
                evidence.append(used.citation())
    except (ValueError, OSError, TypeError, KeyError, readiness.ArmReadinessError) as exc:
        return _result("G5", name, GateStatus.FAIL, str(exc), *evidence)
    return _result("G5", name, GateStatus.PASS,
                   "pack GO C1–C5 recomputed from authenticated ARM, launch, census and one-use custody", *evidence)


def _contains(parent: Path, child: Path) -> bool:
    try:
        child.relative_to(parent)
    except ValueError:
        return False
    return True


def evaluate_g6(bundle: EvidenceBundle) -> GateResult:
    """Check the resolver-derived census with D-176's sibling-child exception.

    The loader authenticates inventory bytes at HEAD and compares the manifest
    evidence record to the whole census. Missing production roots still count;
    resolution errors, equality and either containment direction fail closed.
    """

    name = "REHEARSAL SEPARATION"
    artifact, value, error = _json_record(bundle, "rehearsal_receipt")
    if artifact is None or value is None:
        return _result("G6", name, GateStatus.FAIL, error or "rehearsal receipt is absent")
    if set(value) != _REHEARSAL_RECEIPT_KEYS or value.get("schema_version") != REHEARSAL_RECEIPT_SCHEMA:
        return _result("G6", name, GateStatus.FAIL, "rehearsal receipt schema is invalid", artifact.citation())
    if value.get("receipt_class") != REHEARSAL_RECEIPT_CLASS:
        return _result("G6", name, GateStatus.FAIL, "receipt_class is not T0_UNATTENDED_SUPERVISED_REHEARSAL", artifact.citation())
    if value.get("claim_eligible") is not False:
        return _result("G6", name, GateStatus.FAIL, "claim_eligible is not false", artifact.citation())
    window_id = value.get("window_id")
    if not isinstance(window_id, str) or not window_id.startswith(REHEARSAL_WINDOW_PREFIX):
        return _result("G6", name, GateStatus.FAIL, f"window id does not begin {REHEARSAL_WINDOW_PREFIX}", artifact.citation())
    try:
        if (not bundle.custody_root.is_absolute()
                or any(p.is_symlink() for p in (bundle.custody_root, *bundle.custody_root.parents))):
            raise OSError("custody_root must be absolute and non-symlink")
        custody = bundle.custody_root.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        return _result("G6", name, GateStatus.FAIL, f"rehearsal custody root cannot be resolved: {exc}", artifact.citation())
    if value.get("custody_root") != str(custody):
        return _result("G6", name, GateStatus.FAIL, "rehearsal receipt custody_root does not bind the evaluated root", artifact.citation())
    if not bundle.production_roots:
        return _result("G6", name, GateStatus.FAIL, "production-root census is absent", artifact.citation())
    for production in bundle.production_roots:
        if production.resolution_error is not None:
            return _result("G6", name, GateStatus.FAIL, f"production root {production.role} cannot be resolved: {production.resolution_error}", artifact.citation())
        predicate = next((spec.predicate for spec in readiness.PRODUCTION_CUSTODY_ROOTS
                          if spec.role == production.role.split(":", 1)[0]), None)
        if predicate not in {"DISJOINT", "SIBLING_CHILD"}:
            return _result("G6", name, GateStatus.FAIL, "production-root predicate is absent", artifact.citation())
        if predicate == "SIBLING_CHILD":
            if custody.parent != production.path or custody.name != window_id:
                return _result("G6", name, GateStatus.FAIL, "rehearsal_roots_not_disjoint: custody must be the window-id sibling child", artifact.citation())
            continue
        if _contains(production.path, custody) or _contains(custody, production.path):
            return _result("G6", name, GateStatus.FAIL, f"rehearsal custody overlaps production root {production.role}: {production.path}", artifact.citation())
    return _result("G6", name, GateStatus.PASS, "receipt is non-claim rehearsal authority; resolved custody is the named night-custody child and disjoint from every DISJOINT census role", artifact.citation(), bundle.manifest.citation())


def validate_g7_control(value: object) -> Mapping[str, Any]:
    """Recompute PASS from the exact §10.5 artifact, never its verdict alone."""
    def exact(item, keys, label):
        if not isinstance(item, Mapping) or set(item) != set(keys.split()):
            raise ValueError(f"G7 {label} keys are not exact")
    exact(value, "schema_version control_custody_root rehearsal_window_id control_plan_sha256 presented absence verdict", "artifact")
    if value["schema_version"] != G7_CONTROL_SCHEMA:
        raise ValueError("G7 schema_version")
    window = value["rehearsal_window_id"]
    if not isinstance(window, str) or not window.startswith(REHEARSAL_WINDOW_PREFIX) or Path(window).name != window:
        raise ValueError("G7 rehearsal_window_id")
    root = value["control_custody_root"]
    if not isinstance(root, str) or not Path(root).is_absolute() or Path(root).name != window + "-g7-control":
        raise ValueError("G7 control_custody_root")
    if not isinstance(value["control_plan_sha256"], str) or _SHA256_RE.fullmatch(value["control_plan_sha256"]) is None:
        raise ValueError("G7 control_plan_sha256")
    presented = value["presented"]
    if not isinstance(presented, list) or len(presented) != 2:
        raise ValueError("G7 requires two presentations")
    kinds = set()
    for item in presented:
        exact(item, "kind path sha256 refusal first_refusal presented_monotonic_ns", "presentation")
        kind = item["kind"]
        if not isinstance(kind, str) or kind not in {"rehearsal_receipt", "rehearsal_go"} or kind in kinds:
            raise ValueError("G7 presentation kind")
        kinds.add(kind)
        filename = "presented_go_receipt.json" if kind == "rehearsal_go" else "presented_rehearsal_receipt.json"
        if item["path"] != str(Path(root) / "night" / filename):
            raise ValueError("G7 presentation path")
        if not isinstance(item["sha256"], str) or _SHA256_RE.fullmatch(item["sha256"]) is None:
            raise ValueError("G7 presentation sha256")
        exact(item["refusal"], "reason detail", "refusal")
        expected = "rehearsal_purpose_on_production_id" if kind == "rehearsal_go" else "go_receipt.receipt_class"
        if item["refusal"] != {"reason": "launch_go_receipt_invalid", "detail": expected}:
            raise ValueError("G7 class/purpose refusal missing")
        if item["first_refusal"] is not True:
            raise ValueError("G7 refusal was not first")
        if not _real_int(item["presented_monotonic_ns"]) or item["presented_monotonic_ns"] < 0:
            raise ValueError("G7 presentation timestamp")
    absence = value["absence"]
    exact(absence, "consumption_absent chain_started_absent checked_monotonic_ns", "absence")
    if absence["consumption_absent"] is not True or absence["chain_started_absent"] is not True:
        raise ValueError("G7 control consumption/capture must be absent")
    if (not _real_int(absence["checked_monotonic_ns"])
            or absence["checked_monotonic_ns"] < max(item["presented_monotonic_ns"] for item in presented)):
        raise ValueError("G7 absence timestamp")
    if value["verdict"] != "PASS":
        raise ValueError("G7 verdict is not PASS")
    return value


def evaluate_g7(bundle: EvidenceBundle) -> GateResult:
    """Authenticate the sibling control again, then recompute its PASS conditions."""
    artifact = bundle.record("g7_control")
    evidence = [] if artifact is None else [artifact.citation()]
    if artifact is None:
        return _result("G7", "PRODUCTION REJECTION", GateStatus.FAIL, "g7_control_pending")
    try:
        locator = bundle.manifest.value["records"]["g7_control"]
        raw = artifact.path.read_bytes()
        if readiness.sha256_bytes(raw) != locator["sha256"] or raw != artifact.raw:
            raise ValueError("G7 control digest changed")
        value = validate_g7_control(readiness.parse_json_bytes(raw, require_canonical=True))
        expected_root = bundle.custody_root.with_name(bundle.custody_root.name + "-g7-control")
        if value["control_custody_root"] != str(expected_root) or value["rehearsal_window_id"] != bundle.custody_root.name:
            raise ValueError("G7 control is not this rehearsal's sibling")
        for item in value["presented"]:
            source = bundle.record("d149_go" if item["kind"] == "rehearsal_go" else "rehearsal_receipt")
            if source is None or item["sha256"] != readiness.sha256_bytes(source.raw):
                raise ValueError("G7 presentation is not this rehearsal's retained bytes")
    except (OSError, ValueError, TypeError, KeyError, readiness.ArmReadinessError) as exc:
        return _result("G7", "PRODUCTION REJECTION", GateStatus.FAIL, str(exc), *evidence)
    return _result("G7", "PRODUCTION REJECTION", GateStatus.PASS,
                   "two first class/purpose refusals; control consumption and capture absent", *evidence)


def _process_is_agent(process: object) -> bool:
    if not isinstance(process, Mapping):
        return False
    argv = process.get("argv")
    if not isinstance(argv, list) or any(not isinstance(item, str) for item in argv):
        return False
    return _AGENT_TOKEN_RE.search(" ".join(argv)) is not None


def evaluate_g8(bundle: EvidenceBundle) -> GateResult:
    """Evaluate agent exit ordering and capture-time process censuses."""

    name = "ZERO-AGENT CAPTURE"
    artifact, value, error = _json_record(bundle, "process_lineage")
    if artifact is None or value is None:
        return _result("G8", name, GateStatus.FAIL, error or "process-lineage record is absent")
    try:
        if set(value) != _PROCESS_LINEAGE_KEYS or value.get("schema_version") != PROCESS_LINEAGE_SCHEMA:
            raise ValueError("process-lineage schema is invalid")
        for key in ("agent_pid", "agent_exit_monotonic_ns", "capture_started_monotonic_ns", "capture_finished_monotonic_ns"):
            if not _real_int(value.get(key)):
                raise ValueError(f"process-lineage {key} is not an integer")
        if not value["agent_exit_monotonic_ns"] < value["capture_started_monotonic_ns"] <= value["capture_finished_monotonic_ns"]:
            raise ValueError("agent did not exit before capture began")
        pre = value.get("pre_launch_census")
        if (
            not isinstance(pre, Mapping)
            or set(pre) != _PROCESS_CENSUS_KEYS
            or not isinstance(pre.get("processes"), list)
            or any(
                not isinstance(process, Mapping) or set(process) != _PROCESS_KEYS
                for process in pre.get("processes", [])
            )
        ):
            raise ValueError("pre-launch process census is absent")
        matching_agent_pids = {
            item.get("pid")
            for item in pre["processes"]
            if _process_is_agent(item) and isinstance(item, Mapping)
        }
        if value["agent_pid"] not in matching_agent_pids:
            raise ValueError("pre-launch census does not bind the exiting agent pid")
        censuses = value.get("capture_censuses")
        if not isinstance(censuses, list) or not censuses:
            raise ValueError("capture-time process census is absent")
        for index, census in enumerate(censuses):
            if (
                not isinstance(census, Mapping)
                or set(census) != _PROCESS_CENSUS_KEYS
                or not isinstance(census.get("processes"), list)
                or any(
                    not isinstance(process, Mapping) or set(process) != _PROCESS_KEYS
                    for process in census.get("processes", [])
                )
            ):
                raise ValueError(f"capture census {index} is malformed")
            if any(_process_is_agent(process) for process in census["processes"]):
                raise ValueError(f"agent process existed during capture census {index}")
    except ValueError as exc:
        return _result("G8", name, GateStatus.FAIL, str(exc), artifact.citation())
    return _result("G8", name, GateStatus.PASS, "pre-launch census binds the agent lineage, the agent exited before capture, and every capture census is agent-free", artifact.citation())


def _verified_tree_members(source, destination, files):
    if not source.is_absolute() or not destination.is_absolute() or not isinstance(files, Mapping) or not files:
        raise ValueError("backup lacks independently verified file census")
    if _contains(source, destination) or _contains(destination, source):
        raise ValueError("backup source/destination overlap")
    for relative, digest in files.items():
        path = Path(relative)
        if path.is_absolute() or ".." in path.parts or not isinstance(digest, str) or not _SHA256_RE.fullmatch(digest):
            raise ValueError("backup member escapes tree or has invalid digest")
        for root in (source, destination):
            member = root / path
            if any(p.is_symlink() for p in (member, *member.parents)) or not member.is_file() or readiness.sha256_bytes(member.read_bytes()) != digest:
                raise ValueError("backup member digest mismatch")
    actual = {p.relative_to(destination).as_posix(): readiness.sha256_bytes(p.read_bytes())
              for p in destination.rglob("*") if p.is_file()}
    if any(p.is_symlink() for p in destination.rglob("*")) or actual != files:
        raise ValueError("backup destination census mismatch")


def _qualified_desk_stage(bundle, facts, stage_id, evidence):
    record_artifact = _verify_artifact_reference(bundle, facts.get("plan_record"), label="s1 desk plan")
    record = record_artifact.value
    go = bundle.record("d149_go").value
    if (not isinstance(record, Mapping) or record.get("schema_version") != "joulewise.v5_qualification_plan_record.v1"
            or record.get("occurrence") != "s1" or record.get("head") != go.get("repo_head")
            or record.get("plan", {}).get("sha256") != go.get("plan_sha256")):
        raise ValueError("desk stage is not bound to the s1 plan")
    plan = _verify_artifact_reference(bundle, record.get("plan"), label="s1 plan")
    if not isinstance(plan.value, Mapping) or not isinstance(plan.value.get("plan_id"), str):
        raise ValueError("desk stage lacks its s1 plan identity")
    evidence.append(record_artifact.citation())
    destinations = record.get("backup_destinations", {})
    sources = record.get("desk_sources", {})
    if set(destinations) != {"claim", "bound"} or set(sources) != {"custody", "claim_runs", "bound_runs"}:
        raise ValueError("s1 plan lacks backup destinations or sources")
    arm = _artifact_for_path(bundle, str(bundle.custody_root / go["pack_id"] / "arm_readiness.receipts"
        / (go["arm_receipt"]["receipt_id"] + ".json")))
    if arm is None or not isinstance(arm.value, Mapping) or arm.sha256 != go["arm_receipt"]["sha256"]:
        raise ValueError("desk stage lacks its s1 ARM roots")
    context = arm.value.get("arm_context", {})
    expected_sources = {name: context.get(key) for name, key in (("custody", "custody_root"),
        ("claim_runs", "claim_runs_root"), ("bound_runs", "bound_runs_root"))}
    expected_destinations = {role: context.get(role + "_backup_destination") for role in ("claim", "bound")}
    if (sources != expected_sources or destinations != expected_destinations
            or sources["custody"] != str(bundle.custody_root)):
        raise ValueError("desk backup roots differ from the s1 ARM/plan")
    paths = [Path(destinations[role]) for role in ("claim", "bound")]
    if any(not p.is_absolute() for p in paths) or _contains(paths[0], paths[1]) or _contains(paths[1], paths[0]):
        raise ValueError("backup destinations are not independent")
    if stage_id.endswith("backup"):
        role = "claim" if stage_id == "claim_backup" else "bound"
        if facts.get("destination") != destinations[role] or set(facts.get("copies", {})) != set(sources):
            raise ValueError("backup does not cover both s1 runs roots and custody")
        for name, copy in facts["copies"].items():
            destination = Path(facts["destination"]) / name / "runs"
            if copy.get("source") != sources[name] or copy.get("destination") != str(destination):
                raise ValueError("backup copy source/destination differs from plan")
            _verified_tree_members(Path(sources[name]), destination, copy.get("files"))
    elif stage_id == "close_out":
        stop_artifact = _verify_artifact_reference(bundle, facts.get("stop"), label="s1 STOP")
        stop = stop_artifact.value
        if (not isinstance(stop, Mapping) or stop.get("session_state") != "finalized"
                or stop.get("pin_relation") != "physical_ahead" or stop.get("refusal_code") != "calibration_ledger_head_mismatch"
                or stop.get("terminal_head_pin_candidate") is None):
            raise ValueError("s1 close-out lacks physical_ahead STOP")
        runsheet = _verify_artifact_reference(bundle, facts.get("runsheet"), label="Phase G runsheet")
        if b"### G1 \xe2\x80\x94 post-run assertions" not in runsheet.raw:
            raise ValueError("s1 close-out lacks Phase G authority")
        assertions = facts.get("phase_g", {})
        if (assertions.get("whole_window_verdict_count") != 1
                or any(assertions.get(key) is not True for key in ("no_extra_bundles", "no_scratch_residue", "pack_unchanged"))
                or assertions.get("head") != record["head"]
                or assertions.get("pack_sha256") != record.get("pack_night", {}).get("pack_sha256")
                or not isinstance(assertions.get("git_status"), str)
                or any(line and not line.startswith("##") for line in assertions["git_status"].splitlines())):
            raise ValueError("s1 close-out Phase G assertions failed")
        log = _verify_artifact_reference(bundle, assertions.get("campaign_log"), label="Phase G campaign log")
        rows = [readiness.parse_json_bytes(line) for line in log.raw.splitlines() if line.strip()]
        if sum(row.get("record_type") == "idle_admission_whole_window_verdict" for row in rows) != 1:
            raise ValueError("Phase G requires exactly one whole-window verdict")
        if set(assertions.get("expected_bundles", {})) != {"claim_runs", "bound_runs"} or set(assertions.get("runs_tree", {})) != {"claim_runs", "bound_runs"}:
            raise ValueError("Phase G runs census missing")
        for role, expected in assertions["expected_bundles"].items():
            root = Path(sources[role])
            actual = {p.name for p in root.iterdir() if p.is_dir()
                      and p.name not in {"instrument_validation", "campaign_manifests"}}
            if actual != set(expected):
                raise ValueError("Phase G bundle census mismatch")
        files = assertions.get("custody_files")
        if not isinstance(files, Mapping) or not files:
            raise ValueError("Phase G custody SHA-256 census absent")
        for relative, digest in files.items():
            path = Path(relative)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError("Phase G custody path escapes tree")
            member = Path(sources["custody"]) / path
            if any(p.is_symlink() for p in (member, *member.parents)) or readiness.sha256_bytes(member.read_bytes()) != digest:
                raise ValueError("Phase G custody digest mismatch")
        evidence.extend((stop_artifact.citation(), runsheet.citation(), log.citation()))
    if stage_id in {"close_out", "restore"}:
        off_artifact = _verify_artifact_reference(bundle, facts.get("off_receipt"), label="s1 window OFF receipt")
        off = network_time_off.admit(readiness.parse_json_bytes(off_artifact.raw))
        identity = {key: off[key] for key in ("plan_id", "window_id", "boot_id")}
        if (off["window_id"] != record.get("window_id") or off["plan_id"] != plan.value["plan_id"]
                or off["boot_id"].lower() != go.get("boot_session_id", "").lower()):
            raise ValueError("s1 OFF receipt window identity mismatch")
        if stage_id == "close_out" and facts.get("off_identity") != identity:
            raise ValueError("s1 close-out missing window OFF identity")
        evidence.append(off_artifact.citation())
    if stage_id == "restore":
        standdown = _verify_artifact_reference(bundle, facts.get("standdown"), label="s1 stand-down")
        observation = standdown.value
        if (not isinstance(observation, Mapping)
                or observation.get("schema_version") != "joulewise.t0_rehearsal_standdown_observation.v1"
                or observation.get("boot_session_id") != go.get("boot_session_id")
                or not observation.get("exits") or observation.get("after", {}).get("processes") != []):
            raise ValueError("restore lacks observed stand-down")
        evidence.append(standdown.citation())


def evaluate_g9(bundle: EvidenceBundle) -> GateResult:
    """Evaluate the complete launch-through-restore lifecycle."""

    name = "FULL LIFECYCLE"
    artifact, value, error = _json_record(bundle, "lifecycle")
    if artifact is None or value is None:
        return _result("G9", name, GateStatus.FAIL, error or "lifecycle record is absent")
    evidence = [artifact.citation()]
    try:
        qualified = value.get("schema_version") == QUALIFICATION_LIFECYCLE_SCHEMA
        if set(value) != _LIFECYCLE_KEYS or value.get("schema_version") not in {LIFECYCLE_SCHEMA, QUALIFICATION_LIFECYCLE_SCHEMA}:
            raise ValueError("lifecycle record schema is invalid")
        stages = value.get("stages")
        if not isinstance(stages, list) or [stage.get("stage_id") if isinstance(stage, Mapping) else None for stage in stages] != list(_LIFECYCLE_STAGES):
            raise ValueError("lifecycle stages are not complete launch-through-restore records")
        for stage in stages:
            stage_id = str(stage["stage_id"])
            if set(stage) != _LIFECYCLE_STAGE_KEYS:
                raise ValueError(f"lifecycle stage {stage_id} keys are not exact")
            if stage.get("status") != "COMPLETE":
                raise ValueError(f"lifecycle stage {stage_id} is not complete")
            used = _verify_artifact_reference(bundle, stage.get("evidence"), label=f"lifecycle {stage_id}")
            evidence.append(used.citation())
            facts = used.value
            if qualified and (not isinstance(facts, Mapping) or facts.get("schema_version") != QUALIFICATION_STAGE_SCHEMA):
                raise ValueError("qualification stage lacks observed s1 evidence")
            if isinstance(facts, Mapping) and facts.get("schema_version") in {"joulewise.t0_rehearsal_lifecycle_stage.v1", QUALIFICATION_STAGE_SCHEMA}:
                if facts.get("stage_id") != stage_id:
                    raise ValueError("lifecycle producer stage was swapped")
                if stage_id in {"launch", "capability_consumption"}:
                    source = _verify_artifact_reference(bundle, facts.get("source"), label=f"{stage_id} source")
                    evidence.append(source.citation())
                    source_value = readiness.parse_json_bytes(source.raw, require_canonical=True)
                    if not isinstance(source_value, Mapping):
                        raise ValueError(f"{stage_id} source has no observed record")
                    if stage_id == "launch" and (not _real_int(source_value.get("pid"))
                            or source_value["pid"] <= 0 or not _real_int(source_value.get("monotonic_ns"))):
                        raise ValueError("launch source lacks observed pid/time")
                    if stage_id == "capability_consumption" and not source.path.name.endswith(".consumed.json"):
                        raise ValueError("capability source is not a retained consumption")
                if qualified and stage_id == "capture":
                    refs = facts.get("artifacts")
                    raw_refs = facts.get("sampler_artifacts")
                    if not isinstance(refs, list) or not refs or not isinstance(raw_refs, list) or not raw_refs:
                        raise ValueError("s1 capture lacks metadata and sampler artifacts")
                    for ref in refs:
                        used_capture = _verify_artifact_reference(bundle, ref, label="s1 capture")
                        if used_capture.path.name != "metadata.json" or not isinstance(used_capture.value, Mapping):
                            raise ValueError("s1 capture is not retained metadata")
                        evidence.append(used_capture.citation())
                    for ref in raw_refs:
                        used_raw = _verify_artifact_reference(bundle, ref, label="s1 sampler")
                        if used_raw.path.name != "powermetrics.raw.txt" or not used_raw.raw:
                            raise ValueError("s1 sampler witness is absent")
                        evidence.append(used_raw.citation())
                if qualified and stage_id in {"claim_backup", "bound_backup", "close_out", "restore"}:
                    _qualified_desk_stage(bundle, facts, stage_id, evidence)
                if not qualified and stage_id in {"capture", "close_out"}:
                    references = facts.get("artifacts" if stage_id == "capture" else "sources")
                    if not isinstance(references, list) or len(references) != 2:
                        raise ValueError(f"{stage_id} lacks both activity artifacts")
                    for reference in references:
                        activity = _verify_artifact_reference(bundle, reference, label=f"{stage_id} activity")
                        if (not isinstance(activity.value, Mapping)
                                or activity.value.get("schema_version") != "joulewise.t0_rehearsal_activity.v1"
                                or activity.value.get("claim_eligible") is not False):
                            raise ValueError(f"{stage_id} activity is not non-inference evidence")
                        evidence.append(activity.citation())
                    if stage_id == "close_out":
                        closed = _verify_artifact_reference(bundle, facts.get("ledger_close_out"), label="ledger close-out")
                        if (not isinstance(closed.value, Mapping) or closed.value.get("status") != "aborted"
                                or closed.value.get("terminal_result") != "session_aborted"):
                            raise ValueError("close-out does not record the unused bracket abort")
                        backup_records = facts.get("backup_records")
                        if not isinstance(backup_records, list) or len(backup_records) != 2:
                            raise ValueError("close-out lacks both backup records")
                        for reference in backup_records:
                            _verify_artifact_reference(bundle, reference, label="close-out backup")
                if stage_id == "restore":
                    if facts.get("network_time") != "OFF" or facts.get("stand_down") is not True:
                        raise ValueError("restore-ON is forbidden")
                    observation = facts.get("observation", {})
                    if (observation.get("exit_code") != 0 or observation.get("stdout", "").strip() != "Network Time: Off"
                            or observation.get("argv") != ["/usr/bin/sudo", "-n", "/usr/sbin/systemsetup", "-getusingnetworktime"]):
                        raise ValueError("restore lacks observed OFF query")
                    off_artifact = _verify_artifact_reference(bundle, facts.get("off_receipt"), label="restore OFF receipt")
                    network_time_off.admit(readiness.parse_json_bytes(off_artifact.raw))
                if not qualified and stage_id in {"claim_backup", "bound_backup"}:
                    files = facts.get("files")
                    source, destination = Path(facts.get("source", "")), Path(facts.get("destination", ""))
                    if not source.is_absolute() or not destination.is_absolute() or not isinstance(files, Mapping) or not files:
                        raise ValueError("backup lacks independently verified file census")
                    if _contains(source, destination) or _contains(destination, source):
                        raise ValueError("backup source/destination overlap")
                    for relative, digest in files.items():
                        path = Path(relative)
                        if path.is_absolute() or ".." in path.parts:
                            raise ValueError("backup member escapes tree")
                        for root in (source, destination):
                            member = root / path
                            if any(p.is_symlink() for p in (member, *member.parents)) or not member.is_file() or readiness.sha256_bytes(member.read_bytes()) != digest:
                                raise ValueError("backup member digest mismatch")
        producer_stages = [bundle.artifact(stage["evidence"]["path"]) if not Path(stage["evidence"]["path"]).is_absolute()
                           else _artifact_for_path(bundle, stage["evidence"]["path"]) for stage in stages]
        observed = [item.value for item in producer_stages if item is not None and isinstance(item.value, Mapping)
                    and item.value.get("schema_version") in {"joulewise.t0_rehearsal_lifecycle_stage.v1", QUALIFICATION_STAGE_SCHEMA}]
        if observed:
            if len(observed) != len(_LIFECYCLE_STAGES):
                raise ValueError("mixed lifecycle producer and fixture evidence")
            stamps = [item.get("monotonic_ns") for item in observed]
            if any(not _real_int(stamp) for stamp in stamps) or stamps != sorted(stamps):
                raise ValueError("lifecycle observed order is invalid")
            backups = [Path(item["destination"]) for item in observed if item["stage_id"] in {"claim_backup", "bound_backup"}]
            if _contains(backups[0], backups[1]) or _contains(backups[1], backups[0]):
                raise ValueError("backup destinations are not independent")
        if value.get("operator_actions_at_t0") != 0:
            raise ValueError("operator action occurred during T-0")
        interventions = value.get("human_interventions")
        if not isinstance(interventions, list) or interventions:
            raise ValueError("human intervention occurred during the rehearsal")
    except (ValueError, OSError, TypeError, KeyError, readiness.ArmReadinessError) as exc:
        return _result("G9", name, GateStatus.FAIL, str(exc), *evidence)
    return _result("G9", name, GateStatus.PASS, "launch, capability consumption, capture, both backups, close-out, and restore are complete with zero human intervention", *evidence)


def _run_real_author_boundary(
    inputs: Mapping[str, Any], delta_ns: int
) -> tuple[str, str | None, str]:
    """Run the actual author clock derivation over injected boundary inputs."""

    if set(inputs) != _AUTHOR_INPUT_KEYS:
        raise ValueError("author_inputs keys are not exact")
    integer_names = _AUTHOR_INPUT_KEYS - {
        "reference_midpoint_seconds",
        "reference_bound_seconds",
    }
    if any(not _real_int(inputs.get(name)) for name in integer_names):
        raise ValueError("author_inputs numeric endpoint is not an integer")
    try:
        midpoint = Decimal(str(inputs["reference_midpoint_seconds"]))
        bound = Decimal(str(inputs["reference_bound_seconds"]))
    except Exception as exc:
        raise ValueError("author_inputs reference arithmetic is invalid") from exc
    r0_raw = inputs["r0_anchor_monotonic_raw_ns"]
    author_raw = inputs["author_anchor_monotonic_raw_ns"]
    agreement = t0_author._ReferenceAgreement(
        inputs["reference_server_count"], midpoint, bound
    )
    r0 = {
        "anchor_realtime_ns": inputs["r0_anchor_realtime_ns"],
        "anchor_monotonic_raw_ns": r0_raw,
        "anchor_read_skew_ns": inputs["r0_anchor_read_skew_ns"],
        "batch_finished_monotonic_raw_ns": inputs[
            "r0_batch_finished_monotonic_raw_ns"
        ],
    }
    frequency = inputs.get("r0_kernel_frequency")
    if frequency is None:
        frequency = {"schema_version": kernel_clock.PROBE_SCHEMA, "modes": 0,
                     "raw_word": 0, "ppm": 0.0, "call_status": 0,
                     "timex_status": 0, "errno": 0, "raw_hex": bytes(kernel_clock.Timex()).hex()}
    r0.update(kernel_frequency=frequency, t_stream_max_s=inputs.get("t_stream_max_s"))
    disable = {
        "exit_code": 0,
        "argv": ["/usr/bin/sudo", "-n", "/usr/sbin/systemsetup", "-setusingnetworktime", "off"],
        "started_monotonic_ns": inputs["clock_disable_started_monotonic_ns"],
        "finished_monotonic_ns": inputs["clock_disable_finished_monotonic_ns"],
    }
    context = SimpleNamespace(
        captures={
            "clock-reference": (
                {
                    "finished_monotonic_ns": inputs[
                        "clock_reference_capture_finished_monotonic_ns"
                    ]
                },
                {},
            )
        },
        values={},
        clock=SimpleNamespace(
            monotonic_ns=lambda: inputs["r1_batch_started_monotonic_ns"]
        ),
    )

    def fresh(selected: object, *, kind: str) -> tuple[object, ...]:
        del kind
        selected.values["r1_batch_started_monotonic_ns"] = inputs[
            "r1_batch_started_monotonic_ns"
        ]
        return (
            agreement,
            (),
            inputs["r1_batch_started_monotonic_raw_ns"],
            clock_reference.ClockAnchor(
                realtime_ns=inputs["author_anchor_realtime_ns"] + delta_ns,
                monotonic_raw_ns=author_raw,
                read_skew_ns=inputs["author_anchor_read_skew_ns"],
            ),
            inputs["r1_batch_finished_monotonic_ns"],
        )

    try:
        with (
            mock.patch.object(t0_author, "_captured_clock_reference", return_value=(r0, {"path": "r0", "sha256": "0" * 64}, agreement)),
            mock.patch.object(t0_author, "_capture", return_value=(disable, {"path": "off", "sha256": "1" * 64})),
            mock.patch.object(t0_author, "_fresh_clock_reference_batch", side_effect=fresh),
            mock.patch.object(kernel_clock, "read_kernel_frequency", return_value=frequency),
        ):
            t0_author._derive_clock_attestation(context)
    except t0_author.T0EvidenceAuthoringError as exc:
        return "REFUSE", exc.reason_code, str(exc)
    return "PASS", None, "real author derivation passed"


def _run_real_arm_boundary(
    receipt: Mapping[str, Any], delta_ns: int
) -> tuple[str, str | None]:
    facts = receipt.get("facts")
    if not isinstance(facts, list) or len(facts) != 1 or not isinstance(facts[0], Mapping):
        return "REFUSE", "readiness_clock_preflight_refused"
    value = facts[0].get("value")
    if not isinstance(value, Mapping):
        return "REFUSE", "readiness_clock_preflight_refused"
    live = {
        "boot_session_id": receipt.get("boot_session_id"),
        "realtime_ns": value.get("anchor_realtime_ns") + delta_ns,
        "monotonic_raw_ns": value.get("anchor_monotonic_raw_ns"),
        "read_skew_ns": 1_000,
    }
    if value.get("anchor_check_version") == kernel_clock.ANCHOR_CHECK_VERSION:
        live["kernel_frequency"] = value["kernel_frequency"]
    rows, refusals = readiness._evaluate_rows(
        [_CLOCK_ROW_DEFINITION],
        {str(receipt.get("evidence_id")): receipt},
        clock_route="MANUAL",
        successor_acceptance=False,
        live_clock_anchor=live,
    )
    if rows[0]["verdict"] == "PASS":
        return "PASS", None
    codes = [item.get("code") for item in refusals]
    return "REFUSE", str(codes[0]) if len(codes) == 1 else None


def _expected_cases(
    value: Mapping[str, Any], key: str, *, refusal_code: str
) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    cases = value.get(key)
    if not isinstance(cases, list) or len(cases) != 2 or any(not isinstance(case, Mapping) for case in cases):
        raise ValueError(f"{key} must contain the two software boundary cases")
    by_delta = {case.get("delta_ns"): case for case in cases}
    if any(set(case) != _FALSIFIER_CASE_KEYS for case in cases):
        raise ValueError(f"{key} case keys are not exact")
    if set(by_delta) != {4_999_999, 5_000_001}:
        raise ValueError(f"{key} must contain exactly 5 ms - 1 ns and 5 ms + 1 ns")
    below = by_delta[4_999_999]
    above = by_delta[5_000_001]
    if below.get("expected_status") != "PASS" or below.get("expected_reason_code") is not None:
        raise ValueError(f"{key} 5 ms - 1 ns expected outcome is not PASS")
    if above.get("expected_status") != "REFUSE" or above.get("expected_reason_code") != refusal_code:
        raise ValueError(f"{key} 5 ms + 1 ns expected refusal/code is invalid")
    return below, above


def evaluate_g10(bundle: EvidenceBundle) -> GateResult:
    """Run both real software boundary paths and check Ed's physical control."""

    name = "FALSIFIER CONTROLS"
    controls_artifact, controls, controls_error = _json_record(bundle, "falsifier_controls")
    if controls_artifact is None or controls is None:
        return _result("G10", name, GateStatus.FAIL, controls_error or "software falsifier-control record is absent")
    evidence: list[Mapping[str, object]] = [controls_artifact.citation()]
    try:
        if set(controls) != _FALSIFIER_KEYS or controls.get("schema_version") != FALSIFIER_SCHEMA:
            raise ValueError("software falsifier-control schema is invalid")
        author_inputs = controls.get("author_inputs")
        if not isinstance(author_inputs, Mapping):
            raise ValueError("author_inputs record is absent")
        author_below, author_above = _expected_cases(
            controls,
            "author_cases",
            refusal_code="evidence_author_t0_clock_attestation_underivable",
        )
        arm_below, arm_above = _expected_cases(
            controls,
            "arm_cases",
            refusal_code="readiness_clock_preflight_refused",
        )
        author_observations = []
        for case in (author_below, author_above):
            observed = _run_real_author_boundary(
                author_inputs, int(case["delta_ns"])
            )
            author_observations.append({"delta_ns": case["delta_ns"], "status": observed[0], "reason_code": observed[1], "detail": observed[2]})
            if observed[:2] != (case["expected_status"], case["expected_reason_code"]):
                raise ValueError(f"real author path did not enforce {case['delta_ns']} ns boundary")
        if author_above.get("pass_namespace_published") is not False:
            raise ValueError("real-author +5 ms control does not record absence of a PASS namespace")

        receipt_artifact, receipt, _fact = _clock_receipt(bundle)
        evidence.append(receipt_artifact.citation())
        arm_observations = []
        for case in (arm_below, arm_above):
            observed = _run_real_arm_boundary(receipt, int(case["delta_ns"]))
            arm_observations.append({"delta_ns": case["delta_ns"], "status": observed[0], "reason_code": observed[1]})
            if observed != (case["expected_status"], case["expected_reason_code"]):
                raise ValueError(f"real arm-side predicate path did not enforce {case['delta_ns']} ns boundary")
        evidence.extend(({"author_boundary_observations": author_observations}, {"arm_boundary_observations": arm_observations}))
    except (TypeError, ValueError) as exc:
        return _result("G10", name, GateStatus.FAIL, str(exc), *evidence)

    positive_artifact, positive, positive_error = _json_record(bundle, "positive_control")
    if positive_artifact is None or positive is None:
        return _result(
            "G10",
            name,
            GateStatus.FAIL,
            "outstanding Ed-hands privileged anchor positive-control record is absent",
            *evidence,
        )
    evidence.append(positive_artifact.citation())
    try:
        if set(positive) != _POSITIVE_CONTROL_KEYS or positive.get("schema_version") != POSITIVE_CONTROL_SCHEMA:
            raise ValueError("Ed-hands privileged anchor positive-control schema is invalid")
        if positive.get("performed_by") != "Ed" or positive.get("outside_t0_sequence") is not True:
            raise ValueError("privileged anchor positive control was not recorded as Ed-hands outside T-0")
        if positive.get("network_time_reenabled") is not True or positive.get("forced_resync") is not True:
            raise ValueError("privileged anchor positive control lacks network-time re-enable/forced-resync evidence")
        before = positive.get("anchor_before_ns")
        after = positive.get("anchor_after_ns")
        if not _real_int(before) or not _real_int(after):
            raise ValueError("privileged anchor positive control endpoints are invalid")
        movement_artifact = _artifact_for_path(bundle, str(positive_artifact.path.with_name("anchor-movement.json")))
        movement = movement_artifact.value if movement_artifact is not None else None
        if isinstance(movement, Mapping) and "anchor_check_version" in movement:
            if movement["anchor_check_version"] != kernel_clock.ANCHOR_CHECK_VERSION:
                raise ValueError("unsupported positive-control anchor semantics")
            before_artifact = _artifact_for_path(bundle, str(positive_artifact.path.with_name("before.json")))
            after_artifact = _artifact_for_path(bundle, str(positive_artifact.path.with_name("after.json")))
            if before_artifact is None or after_artifact is None:
                raise ValueError("positive-control residual stamps are absent")
            stamps = (before_artifact.value, after_artifact.value)
            frequency = kernel_clock.validate_probe(stamps[0].get("kernel_frequency"))
            kernel_clock.validate_probe(stamps[1].get("kernel_frequency"))
            if (stamps[0]["realtime_ns"] - stamps[0]["monotonic_raw_ns"] != before
                    or stamps[1]["realtime_ns"] - stamps[1]["monotonic_raw_ns"] != after):
                raise ValueError("positive-control endpoints differ from residual stamps")
            residual = kernel_clock.anchor_residual_ns(after - before,
                stamps[1]["monotonic_raw_ns"] - stamps[0]["monotonic_raw_ns"], frequency)
            if (movement.get("absolute_movement_ns") != abs(after - before)
                    or movement.get("residual_movement_ns") != float(residual)):
                raise ValueError("positive-control residual differs from arithmetic")
            moved = residual > 5_000_000
        else:
            moved = abs(after - before) > 5_000_000
        if not moved:
            raise ValueError("privileged anchor positive control did not visibly move the RAW anchor beyond 5 ms")
        if positive.get("author_refusal_reason_code") != "evidence_author_t0_clock_attestation_underivable":
            raise ValueError("privileged anchor positive control did not record the real author refusal code")
    except (ValueError, TypeError, KeyError) as exc:
        return _result("G10", name, GateStatus.FAIL, str(exc), *evidence)
    return _result("G10", name, GateStatus.PASS, "real author and arm paths enforce 5 ms +/- 1 ns, and Ed's adjacent privileged control visibly moved the RAW anchor", *evidence)


GATE_EVALUATORS = (
    evaluate_g1,
    evaluate_g2,
    evaluate_g3,
    evaluate_g4,
    evaluate_g5,
    evaluate_g6,
    evaluate_g7,
    evaluate_g8,
    evaluate_g9,
    evaluate_g10,
)


def evaluate_rehearsal(bundle: EvidenceBundle) -> dict[str, object]:
    """Evaluate all ten gates in ruled order and return a JSON-ready verdict."""

    gates = tuple(evaluator(bundle) for evaluator in GATE_EVALUATORS)
    overall = compose_overall_verdict(gate.status for gate in gates)
    return {
        "schema_version": "joulewise.t0_unattended_rehearsal_verdict.v1",
        "overall_verdict": overall.value,
        "gate_counts": {
            status.value: sum(gate.status is status for gate in gates)
            for status in GateStatus
        },
        "gates": [gate.to_dict() for gate in gates],
        "load_issues": list(bundle.load_issues),
    }


def evaluate_qualification(bundle: EvidenceBundle, *, purpose="G2B_SHAKEDOWN") -> dict[str, object]:
    """Ruling 76 subset, with retired gates recorded explicitly, never PASS.

    The historical ten-gate entry point and its wire format are unchanged.
    """
    if purpose != "G2B_SHAKEDOWN":
        raise ValueError("qualification requires G2B_SHAKEDOWN")
    go = bundle.record("d149_go")
    if (go is None or not isinstance(go.value, Mapping)
            or go.value.get("purpose") != purpose
            or go.value.get("authorization", {}).get("claim_eligible") is not False):
        raise ValueError("qualification GO purpose/claim binding")
    rows, live = [], []
    for index, evaluator in enumerate(GATE_EVALUATORS, 1):
        if index in (6, 7):
            rows.append({"gate_id": f"G{index}", "name": "RETIRED LIVE GATE",
                         "status": "NOT_APPLICABLE", "basis": "retired_by_ruling_76"})
        else:
            result = evaluator(bundle)
            required_schema = {1: ("execution", QUALIFICATION_EXECUTION_SCHEMA),
                               9: ("lifecycle", QUALIFICATION_LIFECYCLE_SCHEMA)}.get(index)
            if required_schema:
                record = bundle.record(required_schema[0])
                if record is None or not isinstance(record.value, Mapping) or record.value.get("schema_version") != required_schema[1]:
                    result = _result(f"G{index}", result.name, GateStatus.FAIL, "s1 qualification observation schema required")
            live.append(result.status)
            rows.append(result.to_dict())
    return {"schema_version": "joulewise.v5_s1_qualification_verdict.v1",
            "purpose": purpose, "overall_verdict": compose_overall_verdict(live).value,
            "gate_counts": {status: sum(row["status"] == status for row in rows)
                            for status in ("PASS", "FAIL", "UNRULED", "NOT_APPLICABLE")},
            "gates": rows, "load_issues": list(bundle.load_issues)}


__all__ = [
    "D149_SCHEMA",
    "EXECUTION_SCHEMA",
    "EvidenceArtifact",
    "EvidenceBundle",
    "FALSIFIER_SCHEMA",
    "G7_CONTROL_SCHEMA",
    "GATE_EVALUATORS",
    "GateResult",
    "GateStatus",
    "LIFECYCLE_SCHEMA",
    "QUALIFICATION_EXECUTION_SCHEMA",
    "QUALIFICATION_LIFECYCLE_SCHEMA",
    "QUALIFICATION_STAGE_SCHEMA",
    "OverallVerdict",
    "POSITIVE_CONTROL_SCHEMA",
    "PROCESS_LINEAGE_SCHEMA",
    "ProductionRoot",
    "REHEARSAL_RECEIPT_CLASS",
    "REHEARSAL_RECEIPT_SCHEMA",
    "REHEARSAL_WINDOW_PREFIX",
    "compose_overall_verdict",
    "evaluate_g1",
    "evaluate_g2",
    "evaluate_g3",
    "evaluate_g4",
    "evaluate_g5",
    "evaluate_g6",
    "evaluate_g7",
    "evaluate_g8",
    "evaluate_g9",
    "evaluate_g10",
    "evaluate_rehearsal",
    "evaluate_qualification",
    "parse_hid_idle_time",
]
