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
    ),
})


def kind_row(kind: str) -> NightKind:
    try:
        return NIGHT_KINDS[kind]
    except (KeyError, TypeError) as exc:
        raise UnknownNightKind(f"unknown night kind: {kind!r}") from exc
