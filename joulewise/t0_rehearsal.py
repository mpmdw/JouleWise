"""Mechanical judgment for the ruled zero-operator T-0 rehearsal.

A *rehearsal evidence bundle* is an immutable set of custodied artifacts plus
their already-parsed values.  This module performs no collection and launches
no rehearsal: callers supply the bytes that a supervisor and the production
tools recorded.  Each ``evaluate_gN`` function rebuilds one row of the ruled
ten-gate table and returns ``PASS``, ``FAIL``, or ``UNRULED`` with the evidence
it used.  ``compose_overall_verdict`` is the sole composition rule: one FAIL
makes the rehearsal FAIL; otherwise any UNRULED makes it INCOMPLETE; only ten
PASS results can make it PASS.

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
from joulewise import clock_reference


REHEARSAL_RECEIPT_CLASS = "T0_UNATTENDED_SUPERVISED_REHEARSAL"
REHEARSAL_WINDOW_PREFIX = "rehearsal-t0-unattended-"
G7_UNRULED_REASON = (
    "production rejection is UNRULED: HEAD has no production D-149 GO-receipt "
    "consumer or ruled refusal code; the open RF-32 question is recorded in "
    "docs/process_traces/2026-08-23-t22/t0-unattended/impl/"
    "reason-code-coverage-delta.md section 6.2"
)

EXECUTION_SCHEMA = "joulewise.t0_unattended_execution_record.v1"
D149_SCHEMA = "joulewise.t0_unattended_d149_go_receipt.v1"
REHEARSAL_RECEIPT_SCHEMA = "joulewise.t0_unattended_rehearsal_receipt.v1"
PROCESS_LINEAGE_SCHEMA = "joulewise.t0_unattended_process_lineage.v1"
LIFECYCLE_SCHEMA = "joulewise.t0_unattended_lifecycle.v1"
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
_D149_KEYS = {"schema_version", "verdict", "conditions"}
_D149_CONDITION_KEYS = {"condition_id", "status", "evidence"}
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
    if set(value) != _EXECUTION_KEYS or value.get("schema_version") != EXECUTION_SCHEMA:
        return _result("G1", name, GateStatus.FAIL, "execution record schema is invalid", artifact.citation())
    processes = value.get("processes")
    if not isinstance(processes, list) or not processes:
        return _result("G1", name, GateStatus.FAIL, "execution record has no governed process census", artifact.citation())
    top_levels = 0
    for index, process in enumerate(processes):
        if not isinstance(process, Mapping) or set(process) != _EXECUTION_PROCESS_KEYS:
            return _result("G1", name, GateStatus.FAIL, f"governed process {index} record is malformed", artifact.citation())
        if process.get("role") == "top_level":
            top_levels += 1
        if process.get("stdin_fd0_target") != "/dev/null":
            return _result("G1", name, GateStatus.FAIL, f"governed process {index} stdin was not bound to /dev/null", artifact.citation())
        if process.get("state") != "EXITED" or process.get("exit_code") != 0:
            return _result("G1", name, GateStatus.FAIL, f"governed process {index} did not complete successfully", artifact.citation())
        if process.get("prompt_count") != 0:
            return _result("G1", name, GateStatus.FAIL, f"governed process {index} recorded a surviving prompt", artifact.citation())
        if process.get("eof_refusal") is not False:
            return _result("G1", name, GateStatus.FAIL, f"governed process {index} recorded an EOF refusal", artifact.citation())
        if process.get("timed_out") is not False:
            return _result("G1", name, GateStatus.FAIL, f"governed process {index} hung or timed out", artifact.citation())
    if top_levels != 1 or value.get("sequence_completed") is not True:
        return _result("G1", name, GateStatus.FAIL, "top-level T-0 sequence did not record one complete execution", artifact.citation())
    return _result("G1", name, GateStatus.PASS, "top-level and all governed processes completed with fd 0 at /dev/null and no prompt, EOF refusal, or hang", artifact.citation())


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
        if anchor_delta > 5_000_000:
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
            or first_off.get("stdout") != readiness.EXPECTED_NETWORK_TIME_OFF_STDOUT
        ):
            raise ValueError("first exact-Off command result is not mechanically green")
        second_off_artifact, second_off_source = _source_for_row(bundle, "clock.network_time_off")
        evidence.append(second_off_artifact.citation())
        second_probes = second_off_source.get("probes")
        if not isinstance(second_probes, list) or len(second_probes) != 1 or not isinstance(second_probes[0], Mapping):
            raise ValueError("second exact-Off source probe is absent or ambiguous")
        second = second_probes[0]
        if (
            second.get("exit_code") != 0
            or not isinstance(second.get("argv"), list)
            or not t0_author._systemsetup_argv(second["argv"], ("-setusingnetworktime", "off"))
            or second.get("stdout") != readiness.EXPECTED_NETWORK_TIME_OFF_STDOUT
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
    """Evaluate the structured D-149 C1-C5 GO receipt and evidence hashes."""

    name = "D-149 EVALUATION"
    artifact, value, error = _json_record(bundle, "d149_go")
    if artifact is None or value is None:
        return _result("G5", name, GateStatus.FAIL, error or "D-149 receipt is absent")
    evidence = [artifact.citation()]
    try:
        if set(value) != _D149_KEYS or value.get("schema_version") != D149_SCHEMA or value.get("verdict") != "GO":
            raise ValueError("D-149 VERDICT is not GO")
        conditions = value.get("conditions")
        if not isinstance(conditions, list) or [item.get("condition_id") if isinstance(item, Mapping) else None for item in conditions] != [f"C{index}" for index in range(1, 6)]:
            raise ValueError("D-149 condition census is not exactly C1 through C5 in order")
        for condition in conditions:
            condition_id = str(condition["condition_id"])
            if set(condition) != _D149_CONDITION_KEYS:
                raise ValueError(f"D-149 {condition_id} keys are not exact")
            if condition.get("status") != "PASS":
                raise ValueError(f"D-149 {condition_id} is not mechanically green")
            references = condition.get("evidence")
            if not isinstance(references, list) or not references:
                raise ValueError(f"D-149 {condition_id} has no evidence/hash record")
            for index, reference in enumerate(references):
                used = _verify_artifact_reference(bundle, reference, label=f"D-149 {condition_id} evidence {index}")
                evidence.append(used.citation())
    except ValueError as exc:
        return _result("G5", name, GateStatus.FAIL, str(exc), *evidence)
    return _result("G5", name, GateStatus.PASS, "D-149 VERDICT is GO and C1-C5 are mechanically green with matching custody hashes", *evidence)


def _contains(parent: Path, child: Path) -> bool:
    try:
        child.relative_to(parent)
    except ValueError:
        return False
    return True


def evaluate_g6(bundle: EvidenceBundle) -> GateResult:
    """Evaluate rehearsal authority separation and real path containment.

    The production-root census follows the accepted design's dedicated
    runs/custody/ledger/backup requirement (``seat-sol-design.md`` lines
    148-170) and the ruling's outside-production requirement
    (``MAGISTRATE-RULING-T0-UNATTENDED.md`` lines 96-99).  The manifest must
    enumerate those role-labelled roots; resolved ``Path.relative_to`` tests,
    in both directions, reject containment or equality without string-prefix
    guesses.
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
        custody = bundle.custody_root.resolve(strict=True)
    except OSError as exc:
        return _result("G6", name, GateStatus.FAIL, f"rehearsal custody root cannot be resolved: {exc}", artifact.citation())
    if value.get("custody_root") != str(custody):
        return _result("G6", name, GateStatus.FAIL, "rehearsal receipt custody_root does not bind the evaluated root", artifact.citation())
    if not bundle.production_roots:
        return _result("G6", name, GateStatus.FAIL, "production-root census is absent", artifact.citation())
    for production in bundle.production_roots:
        if production.resolution_error is not None:
            return _result("G6", name, GateStatus.FAIL, f"production root {production.role} cannot be resolved: {production.resolution_error}", artifact.citation())
        if _contains(production.path, custody) or _contains(custody, production.path):
            return _result("G6", name, GateStatus.FAIL, f"rehearsal custody overlaps production root {production.role}: {production.path}", artifact.citation())
    return _result("G6", name, GateStatus.PASS, "receipt is non-claim rehearsal authority and resolved custody is disjoint from every enumerated production root", artifact.citation(), bundle.manifest.citation())


def evaluate_g7(_bundle: EvidenceBundle) -> GateResult:
    """Preserve the unresolved production-consumer question as a gate."""

    return _result("G7", "PRODUCTION REJECTION", GateStatus.UNRULED, G7_UNRULED_REASON)


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


def evaluate_g9(bundle: EvidenceBundle) -> GateResult:
    """Evaluate the complete launch-through-restore lifecycle."""

    name = "FULL LIFECYCLE"
    artifact, value, error = _json_record(bundle, "lifecycle")
    if artifact is None or value is None:
        return _result("G9", name, GateStatus.FAIL, error or "lifecycle record is absent")
    evidence = [artifact.citation()]
    try:
        if set(value) != _LIFECYCLE_KEYS or value.get("schema_version") != LIFECYCLE_SCHEMA:
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
        if value.get("operator_actions_at_t0") != 0:
            raise ValueError("operator action occurred during T-0")
        interventions = value.get("human_interventions")
        if not isinstance(interventions, list) or interventions:
            raise ValueError("human intervention occurred during the rehearsal")
    except ValueError as exc:
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
        if not _real_int(before) or not _real_int(after) or abs(after - before) <= 5_000_000:
            raise ValueError("privileged anchor positive control did not visibly move the RAW anchor beyond 5 ms")
        if positive.get("author_refusal_reason_code") != "evidence_author_t0_clock_attestation_underivable":
            raise ValueError("privileged anchor positive control did not record the real author refusal code")
    except ValueError as exc:
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


__all__ = [
    "D149_SCHEMA",
    "EXECUTION_SCHEMA",
    "EvidenceArtifact",
    "EvidenceBundle",
    "FALSIFIER_SCHEMA",
    "G7_UNRULED_REASON",
    "GATE_EVALUATORS",
    "GateResult",
    "GateStatus",
    "LIFECYCLE_SCHEMA",
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
    "parse_hid_idle_time",
]
