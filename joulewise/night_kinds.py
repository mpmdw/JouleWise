"""Immutable facts for the two currently supported night payload kinds.

The idle manifest import is deferred because its module imports night_gate,
which itself needs this table.  The registration still pins only protocol
values and the chain source; Python remains bound by measurement_head and the
sealed per-file manifest.
"""
from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from types import MappingProxyType
from typing import Callable


class UnknownNightKind(ValueError):
    """The requested payload kind has no registered row."""


def _idle_manifest_for(plan):
    return import_module("joulewise.quiet_predicate_campaign").manifest_for(plan)


@dataclass(frozen=True)
class NightKind:
    kind: str
    plan_id_prefix: str | None
    measurement_root_suffix: str | None
    chain_source_path: str
    protocol_path: str | None
    receipt_class: str | None
    window_max_s: int | None
    manifest_for: Callable | None
    manifest_module: str | None
    generator_script: str | None
    executor_module: str | None
    authenticate_chain_source: bool
    requires_chain_bound_registration: bool
    corecaptured_at_arm_and_t0: bool
    non_observer_at_arm_and_t0: bool
    payload_kind: bool
    notice_intro: str
    notice_envelope_noun: str
    notice_work: str
    notice_followup: str
    # Shared entry points dispatch only to handlers explicitly granted here.
    handler: str | None = None
    manifest_name: str | None = None
    wrapper_prefix: str | None = None
    notice_subject_label: str = ""
    notice_power: str = ""
    notice_busy_arm: str = ""
    notice_busy_envelope: str = ""
    notice_publication: str = ""
    notice_courier: str = ""
    artifact_dir: str | None = None
    artifact_names: tuple[str, ...] = ()
    envelope_index_name: str | None = None
    cleanup_name: str | None = None
    outcome_name: str | None = None
    successor_release: bool = False


NIGHT_KINDS = MappingProxyType({
    "quiet_predicate_evidence": NightKind(
        kind="quiet_predicate_evidence",
        plan_id_prefix="qpe01-pilot-n1-",
        measurement_root_suffix="qpe01-pilot-n1",
        chain_source_path="scripts/night_chains/quiet_predicate_evidence.zsh",
        protocol_path="configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v3.json",
        receipt_class="DIAGNOSTIC_NO_PACK",
        window_max_s=9000,
        manifest_for=_idle_manifest_for,
        manifest_module="joulewise.quiet_predicate_campaign",
        generator_script="scripts/gen_evidence_night.py",
        executor_module="joulewise.quiet_predicate_campaign",
        authenticate_chain_source=True,
        requires_chain_bound_registration=True,
        corecaptured_at_arm_and_t0=True,
        non_observer_at_arm_and_t0=True,
        payload_kind=True,
        notice_intro="This idle-variance evidence night sizes a later experiment; it activates no new quietness cutoff.",
        notice_envelope_noun="idle envelopes",
        notice_work="Partial observations and refusals are kept. No model, load generator, calibration-ledger session or measurement pack runs.",
        notice_followup="After delivery the lead sizes block two or records 'no cutoff qualifies'.",
        handler="evidence",
        manifest_name="evidence_manifest.json",
        wrapper_prefix="EVIDENCE",
        notice_subject_label="EVIDENCE",
        notice_power="Power sampling is every 100 ms, with census, AC-power, thermal, timing and cleanup observations and a journal of busy cores (the average number of CPU cores a process kept busy).",
        notice_busy_arm="A process outside the measurement apparatus (the night's own measurement processes) at or above {share:g} busy cores refuses the night at the arm check (the pre-arm checks run before this notice is sent and before the night is installed) or at t0, the scheduled start.",
        notice_busy_envelope="A process outside the measurement apparatus using {bar:g} or more core-seconds (busy cores multiplied by seconds) inside an envelope excludes that envelope. {count} such exclusions in a row end the night.",
        notice_publication="During the night, read-only git show checks run in the measurement clone; successful results publication commits and pushes them from a separate results clone.",
        notice_courier="The scheduler supervises the program and the courier emails the result. Evidence remains PROVISIONAL.",
        artifact_dir="evidence",
        artifact_names=("evidence_busy_cores.jsonl", "evidence_processes.jsonl", "evidence_envelopes.jsonl", "evidence_cleanup.json", "evidence_outcome.json"),
        envelope_index_name="evidence_envelopes.jsonl",
        cleanup_name="evidence_cleanup.json",
        outcome_name="evidence_outcome.json",
        successor_release=True,
    ),
    "calibration": NightKind(
        kind="calibration",
        plan_id_prefix=None,
        measurement_root_suffix=None,
        chain_source_path="scripts/night_chains/calibration_derivation_only.zsh",
        protocol_path=None,
        receipt_class=None,
        window_max_s=None,
        manifest_for=None,
        manifest_module=None,
        generator_script=None,
        executor_module=None,
        authenticate_chain_source=False,
        requires_chain_bound_registration=False,
        corecaptured_at_arm_and_t0=False,
        non_observer_at_arm_and_t0=False,
        payload_kind=False,
        notice_intro="",
        notice_envelope_noun="",
        notice_work="",
        notice_followup="",
        handler="calibration",
        successor_release=True,
    ),
})


def kind_row(kind: str) -> NightKind:
    try:
        return NIGHT_KINDS[kind]
    except (KeyError, TypeError) as exc:
        raise UnknownNightKind(f"unknown night kind: {kind!r}") from exc
