"""Pure CPU-aware idle-admission core (T0.5; audit P1.1/P1.2).

Every evaluator in this module is a pure function over injected evidence:
no subprocesses, no filesystem reads, no clock access.  The campaign runner
(and, after the post-merge hookup, the controller) supplies the pre-run
baseline rich-telemetry records, the adapter-wattage observations, and the
NEG-8 bracket gross energies; this module returns deterministic verdict
surfaces with stable named conditions.

Design rules (audit P1.1/P1.2):

- GPU-idle-only evaluation is no longer sufficient: admission requires the
  CPU/combined-power criteria to pass in addition to the existing GPU-idle
  evidence.
- Missing or malformed required telemetry FAILS CLOSED under a production
  policy (``on_missing_telemetry='fail'``); an exploratory policy may flag
  instead but is explicitly non-claim-bearing (``claim_bearing`` must be
  false).
- Adapter-wattage discontinuities (the real 140->70->140 W precedent) and
  description/power-source changes are recorded as named conditions - data,
  never a silent pass and never an implicit abort.
- The prospective NEG-8 bracket check requires BOTH the absolute and the
  relative tolerance to hold; exactly-on-threshold passes, one ULP over
  fails, and a missing bracket fails under a production policy.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from typing import Any, Mapping, Sequence

EXTENSION_SCHEMA_VERSION = "joulewise.idle_admission_extension.v1"
CPU_ADMISSION_SCHEMA = "joulewise.cpu_idle_admission.v1"
ADAPTER_CONTINUITY_SCHEMA = "joulewise.adapter_wattage_continuity.v1"
NEG8_BRACKET_SCHEMA = "joulewise.neg8_bracket_check.v1"

ON_MISSING_TELEMETRY_FAIL = "fail"
ON_MISSING_TELEMETRY_FLAG = "flag"

# Stable named conditions (campaign-verdict vocabulary).
CONDITION_CPU_TELEMETRY_MISSING = "cpu_baseline_telemetry_missing"
CONDITION_CPU_TELEMETRY_MALFORMED = "cpu_baseline_telemetry_malformed"
CONDITION_CPU_SAMPLES_INSUFFICIENT = "cpu_baseline_sample_count_insufficient"
CONDITION_CPU_BUSY_EXCEEDED = "cpu_busy_ratio_p95_exceeded"
CONDITION_COMBINED_POWER_EXCEEDED = "processor_combined_power_w_p95_exceeded"
CONDITION_GPU_ADMISSION_NOT_PASSED = "gpu_idle_admission_not_passed"
CONDITION_GPU_ADMISSION_UNKNOWN = "gpu_idle_admission_unknown"
CONDITION_ADAPTER_OBSERVATIONS_MISSING = "adapter_observations_missing"
CONDITION_ADAPTER_WATTAGE_UNKNOWN = "adapter_wattage_unknown"
CONDITION_ADAPTER_WATTAGE_DISCONTINUITY = "adapter_wattage_discontinuity"
CONDITION_ADAPTER_DESCRIPTION_CHANGED = "adapter_description_changed"
CONDITION_ADAPTER_POWER_SOURCE_CHANGED = "adapter_power_source_changed"
CONDITION_NEG8_BRACKET_MISSING = "neg8_bracket_missing"
CONDITION_NEG8_REFERENCE_INVALID = "neg8_bracket_reference_invalid"
CONDITION_NEG8_ABS_EXCEEDED = "neg8_bracket_abs_delta_exceeded"
CONDITION_NEG8_REL_EXCEEDED = "neg8_bracket_rel_delta_exceeded"


class IdleAdmissionPolicyError(ValueError):
    """The idle-admission extension mapping is malformed or inconsistent."""


def _require_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise IdleAdmissionPolicyError(f"{field_name} must be a JSON object")
    return value


def _require_exact_keys(
    data: Mapping[str, Any], field_name: str, keys: frozenset[str]
) -> None:
    unknown = sorted(set(data) - keys)
    if unknown:
        raise IdleAdmissionPolicyError(
            f"{field_name} has unknown key(s): {', '.join(unknown)}"
        )
    missing = sorted(keys - set(data))
    if missing:
        raise IdleAdmissionPolicyError(
            f"{field_name} is missing required key(s): {', '.join(missing)}"
        )


def _require_bool(value: Any, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise IdleAdmissionPolicyError(f"{field_name} must be a boolean")
    return value


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise IdleAdmissionPolicyError(f"{field_name} must be a non-empty string")
    return value


def _require_finite_number(
    value: Any, field_name: str, *, minimum: float | None = None
) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise IdleAdmissionPolicyError(f"{field_name} must be a finite number")
    number = float(value)
    if not math.isfinite(number):
        raise IdleAdmissionPolicyError(f"{field_name} must be a finite number")
    if minimum is not None and number < minimum:
        raise IdleAdmissionPolicyError(f"{field_name} must be >= {minimum}")
    return number


def _require_positive_int(value: Any, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise IdleAdmissionPolicyError(f"{field_name} must be a positive integer")
    return value


def canonical_sha256(value: Any) -> str:
    """Hash-bind one canonical JSON rendering of ``value``."""

    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class CpuAdmissionCriteria:
    """Processor/combined-power criteria over the pre-run idle telemetry."""

    cpu_busy_ratio_p95_max: float
    processor_combined_power_w_p95_max: float
    min_samples: int
    on_missing_telemetry: str

    @classmethod
    def from_mapping(cls, data: Any) -> "CpuAdmissionCriteria":
        data = _require_mapping(data, "idle_admission_extension.cpu_criteria")
        _require_exact_keys(
            data,
            "idle_admission_extension.cpu_criteria",
            frozenset(
                {
                    "cpu_busy_ratio_p95_max",
                    "processor_combined_power_w_p95_max",
                    "min_samples",
                    "on_missing_telemetry",
                }
            ),
        )
        on_missing = _require_string(
            data.get("on_missing_telemetry"),
            "idle_admission_extension.cpu_criteria.on_missing_telemetry",
        )
        if on_missing not in {ON_MISSING_TELEMETRY_FAIL, ON_MISSING_TELEMETRY_FLAG}:
            raise IdleAdmissionPolicyError(
                "idle_admission_extension.cpu_criteria.on_missing_telemetry "
                "must be 'fail' or 'flag'"
            )
        return cls(
            cpu_busy_ratio_p95_max=_require_finite_number(
                data.get("cpu_busy_ratio_p95_max"),
                "idle_admission_extension.cpu_criteria.cpu_busy_ratio_p95_max",
                minimum=0.0,
            ),
            processor_combined_power_w_p95_max=_require_finite_number(
                data.get("processor_combined_power_w_p95_max"),
                "idle_admission_extension.cpu_criteria."
                "processor_combined_power_w_p95_max",
                minimum=0.0,
            ),
            min_samples=_require_positive_int(
                data.get("min_samples"),
                "idle_admission_extension.cpu_criteria.min_samples",
            ),
            on_missing_telemetry=on_missing,
        )


@dataclass(frozen=True)
class AdapterWattagePolicy:
    """Continuity policy for per-admission adapter-wattage observations."""

    require_known_wattage: bool

    @classmethod
    def from_mapping(cls, data: Any) -> "AdapterWattagePolicy":
        data = _require_mapping(data, "idle_admission_extension.adapter_wattage")
        _require_exact_keys(
            data,
            "idle_admission_extension.adapter_wattage",
            frozenset({"require_known_wattage"}),
        )
        return cls(
            require_known_wattage=_require_bool(
                data.get("require_known_wattage"),
                "idle_admission_extension.adapter_wattage.require_known_wattage",
            )
        )


@dataclass(frozen=True)
class Neg8BracketPolicy:
    """Prospective start/end NEG-8 gross-energy bracket acceptance policy."""

    require_bracket: bool
    max_abs_delta_j: float
    max_rel_delta: float

    @classmethod
    def from_mapping(cls, data: Any) -> "Neg8BracketPolicy":
        data = _require_mapping(data, "idle_admission_extension.neg8_bracket")
        _require_exact_keys(
            data,
            "idle_admission_extension.neg8_bracket",
            frozenset({"require_bracket", "max_abs_delta_j", "max_rel_delta"}),
        )
        return cls(
            require_bracket=_require_bool(
                data.get("require_bracket"),
                "idle_admission_extension.neg8_bracket.require_bracket",
            ),
            max_abs_delta_j=_require_finite_number(
                data.get("max_abs_delta_j"),
                "idle_admission_extension.neg8_bracket.max_abs_delta_j",
                minimum=0.0,
            ),
            max_rel_delta=_require_finite_number(
                data.get("max_rel_delta"),
                "idle_admission_extension.neg8_bracket.max_rel_delta",
                minimum=0.0,
            ),
        )


@dataclass(frozen=True)
class IdleAdmissionExtension:
    """Additive, hash-bound idle-admission policy extension (T0.5 core).

    The extension travels as the ``idle_admission_extension`` key of the
    campaign policy sidecar.  ``CampaignPolicy.from_mapping`` predates the
    key and rejects unknown keys, so the loader strips the section before
    the base parse and hands it here together with the base profile; the
    sidecar's byte hash still covers every extension byte.
    """

    schema_version: str
    policy_version: str
    claim_bearing: bool
    cpu_criteria: CpuAdmissionCriteria
    adapter_wattage: AdapterWattagePolicy
    neg8_bracket: Neg8BracketPolicy

    @classmethod
    def from_mapping(cls, data: Any, *, profile: str) -> "IdleAdmissionExtension":
        data = _require_mapping(data, "idle_admission_extension")
        _require_exact_keys(
            data,
            "idle_admission_extension",
            frozenset(
                {
                    "schema_version",
                    "policy_version",
                    "claim_bearing",
                    "cpu_criteria",
                    "adapter_wattage",
                    "neg8_bracket",
                }
            ),
        )
        schema_version = _require_string(
            data.get("schema_version"), "idle_admission_extension.schema_version"
        )
        if schema_version != EXTENSION_SCHEMA_VERSION:
            raise IdleAdmissionPolicyError(
                "idle_admission_extension.schema_version must be "
                f"'{EXTENSION_SCHEMA_VERSION}'"
            )
        extension = cls(
            schema_version=schema_version,
            policy_version=_require_string(
                data.get("policy_version"), "idle_admission_extension.policy_version"
            ),
            claim_bearing=_require_bool(
                data.get("claim_bearing"), "idle_admission_extension.claim_bearing"
            ),
            cpu_criteria=CpuAdmissionCriteria.from_mapping(data.get("cpu_criteria")),
            adapter_wattage=AdapterWattagePolicy.from_mapping(
                data.get("adapter_wattage")
            ),
            neg8_bracket=Neg8BracketPolicy.from_mapping(data.get("neg8_bracket")),
        )
        if profile == "production":
            problems = []
            if not extension.claim_bearing:
                problems.append("claim_bearing must be true")
            if (
                extension.cpu_criteria.on_missing_telemetry
                != ON_MISSING_TELEMETRY_FAIL
            ):
                problems.append("cpu_criteria.on_missing_telemetry must be 'fail'")
            if not extension.adapter_wattage.require_known_wattage:
                problems.append("adapter_wattage.require_known_wattage must be true")
            if not extension.neg8_bracket.require_bracket:
                problems.append("neg8_bracket.require_bracket must be true")
            if problems:
                raise IdleAdmissionPolicyError(
                    "production idle_admission_extension must fail closed: "
                    + "; ".join(problems)
                )
        elif profile == "exploratory":
            if extension.claim_bearing:
                raise IdleAdmissionPolicyError(
                    "exploratory idle_admission_extension must set "
                    "claim_bearing=false (explicitly non-claim-bearing)"
                )
        else:
            raise IdleAdmissionPolicyError(
                f"idle_admission_extension does not support profile {profile!r}"
            )
        return extension

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def sha256(self) -> str:
        return canonical_sha256(self.to_dict())


def _p95(values: Sequence[float]) -> float:
    """Deterministic nearest-rank p95 (no interpolation)."""

    ordered = sorted(values)
    return ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)]


def _record_cpu_busy_ratio(record: Mapping[str, Any]) -> float | None:
    """Max per-CPU busy ratio for one rich-telemetry record.

    powermetrics reports per-CPU ``idle_ratio`` and ``down_ratio`` whose sum
    with the busy share is ~1; a parked CPU carries ``down_ratio`` ~1 with
    ``idle_ratio`` 0 and must not read as busy.  Returns ``None`` when the
    record lacks well-formed cluster evidence (malformed telemetry).
    """

    clusters = record.get("clusters")
    if not isinstance(clusters, list) or not clusters:
        return None
    busiest: float | None = None
    for cluster in clusters:
        if not isinstance(cluster, Mapping):
            return None
        cpus = cluster.get("cpus")
        if not isinstance(cpus, list):
            return None
        for cpu in cpus:
            if not isinstance(cpu, Mapping):
                return None
            idle_ratio = cpu.get("idle_ratio")
            down_ratio = cpu.get("down_ratio")
            for value in (idle_ratio, down_ratio):
                if (
                    isinstance(value, bool)
                    or not isinstance(value, int | float)
                    or not math.isfinite(float(value))
                ):
                    return None
            busy = min(1.0, max(0.0, 1.0 - float(idle_ratio) - float(down_ratio)))
            busiest = busy if busiest is None else max(busiest, busy)
    return busiest


def _record_combined_power_w(record: Mapping[str, Any]) -> float | None:
    value = record.get("processor_combined_power_w")
    if (
        isinstance(value, bool)
        or not isinstance(value, int | float)
        or not math.isfinite(float(value))
        or float(value) < 0.0
    ):
        return None
    return float(value)


def evaluate_cpu_idle_admission(
    records: Sequence[Mapping[str, Any]] | None,
    criteria: CpuAdmissionCriteria,
    *,
    gpu_admitted: bool | None,
) -> dict[str, Any]:
    """Evaluate the CPU-aware admission criteria over injected records.

    ``records`` are the pre-run baseline rich-telemetry rows
    (``rich_telemetry_idle.jsonl``); ``gpu_admitted`` is the outcome of the
    existing GPU-idle admission (``idle_window_suspect is False``), injected
    so this evaluator stays pure.  GPU-idle evidence alone never admits: the
    decision is ``admitted`` only when the GPU admission passed AND every
    CPU/combined-power criterion holds on sufficient telemetry.
    """

    conditions: set[str] = set()
    cpu_busy_ratio_p95: float | None = None
    combined_power_w_p95: float | None = None
    sample_count = 0 if records is None else len(records)

    if records is None or not records:
        conditions.add(CONDITION_CPU_TELEMETRY_MISSING)
    else:
        busy_values: list[float] = []
        power_values: list[float] = []
        malformed = False
        for record in records:
            if not isinstance(record, Mapping):
                malformed = True
                break
            busy = _record_cpu_busy_ratio(record)
            power = _record_combined_power_w(record)
            if busy is None or power is None:
                malformed = True
                break
            busy_values.append(busy)
            power_values.append(power)
        if malformed:
            conditions.add(CONDITION_CPU_TELEMETRY_MALFORMED)
        else:
            if sample_count < criteria.min_samples:
                conditions.add(CONDITION_CPU_SAMPLES_INSUFFICIENT)
            cpu_busy_ratio_p95 = _p95(busy_values)
            combined_power_w_p95 = _p95(power_values)
            if cpu_busy_ratio_p95 > criteria.cpu_busy_ratio_p95_max:
                conditions.add(CONDITION_CPU_BUSY_EXCEEDED)
            if combined_power_w_p95 > criteria.processor_combined_power_w_p95_max:
                conditions.add(CONDITION_COMBINED_POWER_EXCEEDED)

    if gpu_admitted is None:
        conditions.add(CONDITION_GPU_ADMISSION_UNKNOWN)
    elif gpu_admitted is not True:
        conditions.add(CONDITION_GPU_ADMISSION_NOT_PASSED)

    evidence_conditions = conditions & {
        CONDITION_CPU_TELEMETRY_MISSING,
        CONDITION_CPU_TELEMETRY_MALFORMED,
        CONDITION_CPU_SAMPLES_INSUFFICIENT,
        CONDITION_GPU_ADMISSION_UNKNOWN,
    }
    threshold_conditions = conditions & {
        CONDITION_CPU_BUSY_EXCEEDED,
        CONDITION_COMBINED_POWER_EXCEEDED,
        CONDITION_GPU_ADMISSION_NOT_PASSED,
    }
    if threshold_conditions:
        decision = "failed"
    elif evidence_conditions:
        decision = (
            "failed"
            if criteria.on_missing_telemetry == ON_MISSING_TELEMETRY_FAIL
            else "flagged"
        )
    else:
        decision = "admitted"
    return {
        "schema_version": CPU_ADMISSION_SCHEMA,
        "decision": decision,
        "admitted": decision == "admitted",
        "conditions": sorted(conditions),
        "sample_count": sample_count,
        "cpu_busy_ratio_p95": cpu_busy_ratio_p95,
        "processor_combined_power_w_p95": combined_power_w_p95,
        "criteria": asdict(criteria),
        "gpu_admitted": gpu_admitted,
    }


def extract_adapter_observation(
    power: Mapping[str, Any] | None,
    *,
    source: str,
    power_source: Any = None,
) -> dict[str, Any]:
    """Normalize one adapter-wattage observation from a power mapping.

    Unknown or malformed values stay ``None`` (evidence capture is
    fail-soft); the continuity evaluator is where ``None`` fails closed
    under a production policy.
    """

    watts: float | None = None
    description: str | None = None
    if isinstance(power, Mapping):
        raw_watts = power.get("adapter_watts")
        if (
            not isinstance(raw_watts, bool)
            and isinstance(raw_watts, int | float)
            and math.isfinite(float(raw_watts))
            and float(raw_watts) > 0.0
        ):
            watts = float(raw_watts)
        raw_description = power.get("adapter_description")
        if isinstance(raw_description, str) and raw_description.strip():
            description = raw_description
    return {
        "source": source,
        "adapter_watts": watts,
        "adapter_description": description,
        "power_source": power_source if isinstance(power_source, str) else None,
    }


def evaluate_adapter_wattage_continuity(
    observations: Sequence[Mapping[str, Any]],
    policy: AdapterWattagePolicy,
) -> dict[str, Any]:
    """Judge adapter-wattage continuity across admission observations.

    Discontinuities (e.g. the observed 140->70->140 W negotiation drop) and
    description/power-source changes are named conditions - recorded data,
    not an abort.  Unknown wattage fails closed only when the policy
    requires known wattage (production).
    """

    conditions: set[str] = set()
    known_watts: list[float] = []
    transitions: list[dict[str, Any]] = []
    descriptions: set[str] = set()
    power_sources: set[str] = set()
    unknown_count = 0
    previous_watts: float | None = None
    for index, observation in enumerate(observations):
        watts = observation.get("adapter_watts")
        if (
            isinstance(watts, bool)
            or not isinstance(watts, int | float)
            or not math.isfinite(float(watts))
        ):
            unknown_count += 1
            watts = None
        else:
            watts = float(watts)
            known_watts.append(watts)
            if previous_watts is not None and watts != previous_watts:
                transitions.append(
                    {
                        "index": index,
                        "source": observation.get("source"),
                        "from_watts": previous_watts,
                        "to_watts": watts,
                    }
                )
            previous_watts = watts
        description = observation.get("adapter_description")
        if isinstance(description, str) and description.strip():
            descriptions.add(description)
        power_source = observation.get("power_source")
        if isinstance(power_source, str) and power_source.strip():
            power_sources.add(power_source)

    if not observations:
        conditions.add(CONDITION_ADAPTER_OBSERVATIONS_MISSING)
    if unknown_count or (not known_watts and observations):
        conditions.add(CONDITION_ADAPTER_WATTAGE_UNKNOWN)
    if len(set(known_watts)) > 1:
        conditions.add(CONDITION_ADAPTER_WATTAGE_DISCONTINUITY)
    if len(descriptions) > 1:
        conditions.add(CONDITION_ADAPTER_DESCRIPTION_CHANGED)
    if len(power_sources) > 1:
        conditions.add(CONDITION_ADAPTER_POWER_SOURCE_CHANGED)

    unknown_conditions = conditions & {
        CONDITION_ADAPTER_OBSERVATIONS_MISSING,
        CONDITION_ADAPTER_WATTAGE_UNKNOWN,
    }
    if unknown_conditions and policy.require_known_wattage:
        decision = "failed"
    elif conditions:
        decision = "flagged"
    else:
        decision = "stable"
    return {
        "schema_version": ADAPTER_CONTINUITY_SCHEMA,
        "decision": decision,
        "stable": decision == "stable",
        "conditions": sorted(conditions),
        "observation_count": len(observations),
        "unknown_wattage_count": unknown_count,
        "distinct_adapter_watts": sorted(set(known_watts)),
        "distinct_adapter_descriptions": sorted(descriptions),
        "distinct_power_sources": sorted(power_sources),
        "wattage_transitions": transitions,
        "policy": asdict(policy),
    }


def _finite_positive(value: Any) -> float | None:
    if (
        isinstance(value, bool)
        or not isinstance(value, int | float)
        or not math.isfinite(float(value))
        or float(value) <= 0.0
    ):
        return None
    return float(value)


def evaluate_neg8_bracket(
    start_gross_j: Any,
    end_gross_j: Any,
    policy: Neg8BracketPolicy,
) -> dict[str, Any]:
    """Compare start/end NEG-8 gross energy against BOTH tolerances.

    The bracket passes only when the absolute delta satisfies the absolute
    tolerance AND the relative tolerance (relative to the start gross).
    Comparisons are ``<=``: exactly-on-threshold passes, one ULP over
    fails.  A missing or invalid bracket fails closed when the policy
    requires the bracket (production) and is flagged otherwise.
    """

    conditions: set[str] = set()
    start = _finite_positive(start_gross_j)
    end = (
        None
        if isinstance(end_gross_j, bool)
        or not isinstance(end_gross_j, int | float)
        or not math.isfinite(float(end_gross_j))
        else float(end_gross_j)
    )
    abs_delta_j: float | None = None
    rel_delta: float | None = None
    if start_gross_j is None or end_gross_j is None:
        conditions.add(CONDITION_NEG8_BRACKET_MISSING)
    elif start is None or end is None:
        conditions.add(CONDITION_NEG8_REFERENCE_INVALID)
    else:
        abs_delta_j = abs(end - start)
        rel_delta = abs_delta_j / start
        if abs_delta_j > policy.max_abs_delta_j:
            conditions.add(CONDITION_NEG8_ABS_EXCEEDED)
        if abs_delta_j > policy.max_rel_delta * start:
            conditions.add(CONDITION_NEG8_REL_EXCEEDED)

    evidence_conditions = conditions & {
        CONDITION_NEG8_BRACKET_MISSING,
        CONDITION_NEG8_REFERENCE_INVALID,
    }
    if evidence_conditions:
        decision = "failed" if policy.require_bracket else "flagged"
    elif conditions:
        decision = "failed"
    else:
        decision = "passed"
    return {
        "schema_version": NEG8_BRACKET_SCHEMA,
        "decision": decision,
        "passed": decision == "passed",
        "conditions": sorted(conditions),
        "start_gross_j": start_gross_j if isinstance(start_gross_j, int | float) and not isinstance(start_gross_j, bool) else None,
        "end_gross_j": end_gross_j if isinstance(end_gross_j, int | float) and not isinstance(end_gross_j, bool) else None,
        "abs_delta_j": abs_delta_j,
        "rel_delta": rel_delta,
        "policy": asdict(policy),
    }
