"""Claim-time pre/post powermetrics fiducial calibration bracketing.

The bracket carries a nonparametric 95/95 calibration-distribution bound into
claims only under the registered T1-T3 transfer assumptions; it does not turn
either finite sample maximum into an unconditional instrument property.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import subprocess
from dataclasses import dataclass, replace
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN, localcontext
from pathlib import Path
from typing import Any, Mapping, Sequence

from joulewise.bundle_read import BundleReadError, BundleReader
from joulewise.calibration_ledger import (
    IDENTITY_EPOCH_FIELDS,
    LEDGER_SCHEMA,
    CalibrationLedgerSnapshot,
    LedgerObservation,
    content_id_from_artifact_hashes,
)
from joulewise.powermetrics_fiducial import (
    CAPTURE_TIME_FIELD,
    MAX_AGE_S,
    PROTOCOL_ID,
    PROTOCOL_V2_ID,
    REGION_COVERAGE_RESOLUTION_S,
    RESIDUAL_REGION_METHOD,
    V2_BINDING_FIELDS,
    capture_wall_time_from_events,
    protocol_pulse_count,
    protocol_sha256,
    verify_stored_evidence_physics,
)
from joulewise.schemas import CalibrationBracketingPolicy

BRACKET_SCHEMA = "joulewise.instrument_calibration_bracket.v1"
BRACKET_BINDING_SCHEMA = "joulewise.calibration_bracket_binding.v1"
ACCEPTANCE_BOUND_SCHEMA = "joulewise.calibration_acceptance_bound.v2"
ACCEPTANCE_SUCCESSOR_SCHEMA = "joulewise.calibration_acceptance_bound.v3"
ACCEPTANCE_FIXTURE_SCHEMA = (
    "joulewise.calibration_acceptance_bound.v2.fixture.v1"
)
ACCEPTANCE_EVALUATION_SCHEMA = "joulewise.calibration_acceptance_evaluation.v2"
ACCEPTANCE_REGISTRY_SCHEMA = "joulewise.calibration_acceptance_registry.v1"
ACCEPTANCE_TRIGGER_PROBE_SCHEMA = (
    "joulewise.calibration_acceptance_trigger_probe.v1"
)
DEFAULT_ACCEPTANCE_BOUND_PATH = (
    Path(__file__).resolve().parents[1]
    / "configs"
    / "calibration"
    / "calibration_acceptance_d079_v2.json"
)
DEFAULT_ACCEPTANCE_REGISTRY_PATH = (
    Path(__file__).resolve().parents[1]
    / "configs"
    / "calibration"
    / "calibration_acceptance_registry.json"
)
DEFAULT_ACCEPTANCE_BOUND_SHA256 = (
    "9a264c57fdc007de473872870f19a5e1c9bd9b11256c25266b0e3e50ebba0ceb"
)
_REPO_ROOT = Path(__file__).resolve().parents[1]
ESTIMATOR_CODE_PATHS = (
    "joulewise/powermetrics_fiducial.py",
    "joulewise/uncertainty_evidence.py",
    "joulewise/adapters/powermetrics.py",
    "joulewise/reduce.py",
)
ACCEPTANCE_IDENTITY_FIELDS = IDENTITY_EPOCH_FIELDS
_D102_OPERATIVE_VALUES = {
    "bracket_screen_s": "0.010818",
    "preflight_level_screen_s": "0.033558756679900",
    "max_budgetable_excess_s": "0.001275166090593858",
    "maximum_budgetable_drift_s": "0.012093166090593858",
}

# COLD-GATE-Q1: the successor corpus is the complete content-distinct valid
# same-epoch ledger prefix, not the triggering suffix or the frozen n=19 set.
SUCCESSOR_CORPUS_SELECTION = (
    "all_content_distinct_valid_same_epoch_observations_through_cutoff"
)
# COLD-GATE-Q2: the successor level screen is the observed corpus maximum
# alone. The 95% two-draw prediction remains recorded derivation evidence but
# is never an input to this systematic-failure comparator.
SUCCESSOR_PREFLIGHT_SCREEN_RULE = "observed_corpus_maximum"
# COLD-GATE-Q3: dependency-free Decimal incomplete-beta inversion runs at 80
# digits. The D-102 df=18 coefficients remain explicit compatibility pins, and
# the public bypass supports independent verification of the numerical path.
SUCCESSOR_QUANTILE_METHOD = "decimal_incomplete_beta_bisection_v1"
SUCCESSOR_DECIMAL_PRECISION = 80
SUCCESSOR_CONTINUED_FRACTION_MAX_ITERATIONS = 10_000
# COLD-GATE-Q4: a range successor below the pending boundary retains it; once
# crossed, the next boundary is twice the newly issued corpus count.
_COUNT_BOUNDARY_RULE_RETAIN_THEN_DOUBLE = (
    "retain_until_crossed_then_double_issued_count"
)
SUCCESSOR_COUNT_BOUNDARY_RULE = _COUNT_BOUNDARY_RULE_RETAIN_THEN_DOUBLE
GENESIS_COUNT_BOUNDARY_RULE = "d102_initial_total_valid_same_epoch_count_38"
_SUPPORTED_COUNT_BOUNDARY_RULES = frozenset(
    {GENESIS_COUNT_BOUNDARY_RULE, _COUNT_BOUNDARY_RULE_RETAIN_THEN_DOUBLE}
)
# Versioning prevents a later rule from being applied retroactively to an
# ancestor. It does not make issued history reversible: each entry's recorded
# rule and resulting boundary remain authenticated, immutable chain facts.
# COLD-GATE-Q5: a new systematic observation remains new and blocks every
# automatic build until an authority ruling disposes it.
SUCCESSOR_SYSTEMATIC_POLICY = "persistent_refusal_pending_new_ruling"
# COLD-GATE-Q6: authenticated terminal abandoned/no-content attempts and
# explicit unused U1 slots are recorded and excluded from the content universe;
# malformed, content-bearing, or unresolved shapes still refuse.
SUCCESSOR_NONCONTENT_POLICY = "exclude_authenticated_terminal_no_content"
# COLD-GATE-Q7: v3 artifacts use cutoff-derived immutable names, remain present
# in the checkout, and form a single-parent ancestry rooted at the issued v2.
SUCCESSOR_LINEAGE_POLICY = "immutable_present_single_parent_cutoff_named_v3"
# COLD-GATE-Q8: the checked-in registry is the sole rotating trust anchor; it
# has exactly one active row and authenticates that artifact's exact bytes.
ACCEPTANCE_REGISTRY_AUTHORITY = "committed_registry_one_active_exact_sha256"
# COLD-GATE-Q9: publication creates one two-path Git commit through an isolated
# index, atomically advances HEAD, then verifies committed-mode selection.
SUCCESSOR_PUBLICATION_POLICY = "single_commit_two_path_atomic_head_update_verified"
# COLD-GATE-Q10: a pre-science probe may inspect exactly U1's governed open
# two-slot extension; a triggered build requires an aborted/finalized terminal
# session and a committed head before issuance.
PRE_PROBE_OPEN_SESSION_POLICY = "permit_governed_open_u1_extension_probe_only"
# COLD-GATE-Q11: post evidence may be consumed under the successor only when
# lineage records its parent-artifact judgment before self-fit construction.
POST_SUCCESSOR_POLICY = "require_explicit_parent_judgment_lineage"
# COLD-GATE-Q12: this four-file exhibit closes the authenticated probe API;
# writer scalar removal and the U8 arm-path call remain separately scoped.
WRITER_INTEGRATION_SCOPE_STATUS = "probe_closed_writer_and_arm_path_residual"
# COLD-GATE-Q13: the allowance generalization remains the exhibit's current
# answer, but n<19 is not licensed while Q13 is pending. The guard prevents the
# df=1 / t~=63.66 path from becoming an issued comparator by accident.
SUCCESSOR_MINIMUM_CORPUS_SIZE = 19
SUCCESSOR_DECISION_IDS = (
    "D-102",
    "D-109",
    "D-117",
    "COLD-GATE-U2-PENDING",
)

_SUCCESSOR_TOP_LEVEL_FIELDS = {
    "schema_version",
    "acceptance_id",
    "decision_ids",
    "artifact_role",
    "issuance",
    "lineage",
    "ledger_cutoff",
    "identity_epoch",
    "prospective_rederivation",
    "derivation_corpus",
    "prior_observation_set",
    "decimal_derivation",
    "derivation_sha256",
}
_SUCCESSOR_ARTIFACT_NAME_RE = re.compile(
    r"^calibration_acceptance_v3_s([1-9][0-9]*)_([0-9a-f]{16})\.json$"
)
_D102_RATIFIED_T_QUANTILES = {
    (18, "0.975"): Decimal(
        "2.1009220402410352934446802481715190309096147708883899652987837826492167345329145"
    ),
    (18, "0.995"): Decimal(
        "2.8784404727135853941939366597008136821841052811738896572381901955286218320347263"
    ),
}


class CalibrationAcceptanceNumericalRefusal(ValueError):
    """A successor numerical kernel could not produce a governed result."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(reason)


class CalibrationAcceptanceRegistryRefusal(ValueError):
    """The rotating registry authority failed with a stable reason code."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(reason)


def _registry_bootstrap_issued_sha256() -> str:
    """Compatibility export for the one legacy issuance-only consumer."""

    try:
        value = json.loads(DEFAULT_ACCEPTANCE_REGISTRY_PATH.read_bytes())
        entries = value.get("entries") if isinstance(value, Mapping) else None
        if isinstance(entries, list):
            for entry in entries:
                if (
                    isinstance(entry, Mapping)
                    and entry.get("acceptance_id")
                    == "d079_calibration_acceptance_v2_n19"
                ):
                    digest = entry.get("artifact_sha256")
                    if isinstance(digest, str) and re.fullmatch(
                        r"[0-9a-f]{64}", digest
                    ):
                        return digest
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        pass
    # D-116's out-of-scope genesis bootstrap is tested from a standalone copy
    # of this module without repository configs. Retain its historical v2
    # emission oracle only; active runtime selection never consults this
    # fallback and every v3 digest exists solely in the committed registry.
    return "316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985"


ISSUED_ACCEPTANCE_BOUND_SHA256 = _registry_bootstrap_issued_sha256()


@dataclass(frozen=True)
class CalibrationCandidate:
    relative_path: str
    manifest_sha256: str
    evidence_sha256: str
    protocol_id: str
    capture_wall_time_s: float
    # Production authentication stores the source decimal lexeme here.  Float
    # remains accepted only for backwards-compatible synthetic callers; the
    # authenticated loader below never takes that branch.
    b_fiducial_s: Decimal | str | float
    bindings: Mapping[str, Any]
    attempt_id: str | None = None
    content_id: str | None = None
    ledger_receipt_digest: str | None = None
    bracket_session_id: str | None = None
    bracket_slot: str | None = None
    bracket_window_id: str | None = None
    bracket_plan_id: str | None = None
    bracket_plan_sha256: str | None = None
    bracket_evidence_root_id: str | None = None
    bracket_runs_root: str | None = None

    def descriptor(self) -> dict[str, Any]:
        bound = _candidate_decimal(self)
        return {
            "relative_path": self.relative_path,
            "manifest_sha256": self.manifest_sha256,
            "evidence_sha256": self.evidence_sha256,
            "protocol_id": self.protocol_id,
            "capture_wall_time_s": self.capture_wall_time_s,
            # This descriptor is the recorded reducer boundary.  Keep both the
            # exact acceptance lexeme and its explicit binary64 projection.
            "b_fiducial_s": float(bound) if bound is not None else self.b_fiducial_s,
            "b_fiducial_decimal_s": str(bound) if bound is not None else None,
            "attempt_id": self.attempt_id,
            "content_id": self.content_id,
            "ledger_receipt_digest": self.ledger_receipt_digest,
            "bracket_session_id": self.bracket_session_id,
            "bracket_slot": self.bracket_slot,
            "bracket_window_id": self.bracket_window_id,
            "bracket_plan_id": self.bracket_plan_id,
            "bracket_plan_sha256": self.bracket_plan_sha256,
            "bracket_evidence_root_id": self.bracket_evidence_root_id,
            "bracket_runs_root": self.bracket_runs_root,
        }


def _canonical_sha256(value: Mapping[str, Any]) -> str:
    raw = json.dumps(
        dict(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _decimal(value: Any) -> Decimal | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        result = Decimal(value)
    except InvalidOperation:
        return None
    return result if result.is_finite() else None


def _decimal_text(value: Decimal) -> str:
    """Render one finite Decimal without exponent or binary64 mediation."""

    if not value.is_finite():
        raise ValueError("decimal value must be finite")
    return format(value, "f")


def _decimal_pi() -> Decimal:
    """Return pi deterministically at the active Decimal precision."""

    one = Decimal(1)
    two = Decimal(2)
    four = Decimal(4)
    a = one
    b = one / two.sqrt()
    t = Decimal(1) / four
    power = one
    for _ in range(10):
        midpoint = (a + b) / two
        b = (a * b).sqrt()
        t -= power * (a - midpoint) ** 2
        a = midpoint
        power *= two
    return (a + b) ** 2 / (four * t)


def _decimal_beta_a_half(df: int) -> Decimal:
    """Compute B(df/2, 1/2) for an integer df without a gamma primitive."""

    if df % 2 == 0:
        m = df // 2
        numerator = Decimal(4**m * math.factorial(m) * math.factorial(m - 1))
        return numerator / Decimal(math.factorial(2 * m))
    m = (df - 1) // 2
    numerator = Decimal(math.factorial(2 * m)) * _decimal_pi()
    denominator = Decimal(4**m * math.factorial(m) ** 2)
    return numerator / denominator


def _decimal_beta_continued_fraction(
    a: Decimal, b: Decimal, x: Decimal
) -> Decimal:
    """Evaluate the incomplete-beta continued fraction by Lentz iteration."""

    one = Decimal(1)
    qab = a + b
    qap = a + one
    qam = a - one
    tiny = Decimal(1).scaleb(-(SUCCESSOR_DECIMAL_PRECISION - 8))
    epsilon = Decimal(1).scaleb(-(SUCCESSOR_DECIMAL_PRECISION - 12))

    def guarded(value: Decimal) -> Decimal:
        if abs(value) >= tiny:
            return value
        return -tiny if value < 0 else tiny

    c = one
    d = one / guarded(one - qab * x / qap)
    result = d
    for iteration in range(1, SUCCESSOR_CONTINUED_FRACTION_MAX_ITERATIONS + 1):
        iteration_start = result
        i = Decimal(iteration)
        doubled = Decimal(2 * iteration)
        numerator = i * (b - i) * x / ((qam + doubled) * (a + doubled))
        d = one / guarded(one + numerator * d)
        c = guarded(one + numerator / c)
        result *= d * c

        numerator = -(
            (a + i)
            * (qab + i)
            * x
            / ((a + doubled) * (qap + doubled))
        )
        d = one / guarded(one + numerator * d)
        c = guarded(one + numerator / c)
        change = d * c
        result *= change
        if (
            abs(change - one) <= epsilon
            and abs(result - iteration_start)
            <= epsilon * max(one, abs(result))
        ):
            return result
    raise CalibrationAcceptanceNumericalRefusal(
        "successor_quantile_continued_fraction_nonconvergence"
    )


def _decimal_regularized_incomplete_beta_df_half(
    x: Decimal, df: int
) -> Decimal:
    if x <= 0:
        return Decimal(0)
    if x >= 1:
        return Decimal(1)
    a = Decimal(df) / Decimal(2)
    b = Decimal("0.5")
    beta = _decimal_beta_a_half(df)
    front = (x**a) * ((Decimal(1) - x) ** b) / beta
    if x < (a + 1) / (a + b + 2):
        result = front * _decimal_beta_continued_fraction(a, b, x) / a
    else:
        result = Decimal(1) - (
            front
            * _decimal_beta_continued_fraction(b, a, Decimal(1) - x)
            / b
        )
    return min(Decimal(1), max(Decimal(0), result))


def _decimal_student_t_survival(value: Decimal, df: int) -> Decimal:
    if value == 0:
        return Decimal("0.5")
    argument = Decimal(df) / (Decimal(df) + value * value)
    return Decimal("0.5") * _decimal_regularized_incomplete_beta_df_half(
        argument, df
    )


def decimal_student_t_quantile(
    probability: str,
    df: int,
    *,
    use_compatibility_pin: bool = True,
) -> Decimal:
    """Return the pinned deterministic Student-t quantile as a Decimal."""

    if isinstance(df, bool) or not isinstance(df, int) or df < 1:
        raise ValueError("df must be an integer >= 1")
    target = _decimal(probability)
    if target is None or not Decimal(0) < target < Decimal(1):
        raise ValueError("probability must be a finite decimal between zero and one")
    if not isinstance(use_compatibility_pin, bool):
        raise ValueError("use_compatibility_pin must be boolean")
    pinned = (
        _D102_RATIFIED_T_QUANTILES.get((df, probability))
        if use_compatibility_pin
        else None
    )
    if pinned is not None:
        return pinned
    if target == Decimal("0.5"):
        return Decimal(0)

    with localcontext() as context:
        context.prec = SUCCESSOR_DECIMAL_PRECISION
        sign = Decimal(-1) if target < Decimal("0.5") else Decimal(1)
        tail = target if target < Decimal("0.5") else Decimal(1) - target
        lower = Decimal(0)
        upper = Decimal(1)
        while _decimal_student_t_survival(upper, df) > tail:
            upper *= 2
        tolerance = Decimal(1).scaleb(-(SUCCESSOR_DECIMAL_PRECISION - 8))
        while upper - lower > tolerance:
            midpoint = (lower + upper) / 2
            if _decimal_student_t_survival(midpoint, df) > tail:
                lower = midpoint
            else:
                upper = midpoint
        return +(sign * ((lower + upper) / 2))


def derive_successor_decimal_derivation(
    members: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Derive the complete v3 Decimal record from authenticated members."""

    if len(members) < SUCCESSOR_MINIMUM_CORPUS_SIZE:
        raise ValueError(
            "successor_corpus_below_pending_q13_minimum_19"
        )
    content_ids: list[str] = []
    values: list[Decimal] = []
    for member in members:
        content_id = member.get("content_id") if isinstance(member, Mapping) else None
        value = _decimal(member.get("b_fiducial_s")) if isinstance(member, Mapping) else None
        if not _valid_sha256(content_id) or value is None or value < 0:
            raise ValueError("successor member has invalid content ID or bound")
        content_ids.append(content_id)
        values.append(value)
    if content_ids != sorted(content_ids) or len(content_ids) != len(set(content_ids)):
        raise ValueError("successor members must be content-ID sorted and distinct")

    with localcontext() as context:
        context.prec = SUCCESSOR_DECIMAL_PRECISION
        count = Decimal(len(values))
        mean = sum(values, Decimal(0)) / count
        sample_sd = (
            sum((value - mean) ** 2 for value in values)
            / Decimal(len(values) - 1)
        ).sqrt()
        minimum = min(values)
        maximum = max(values)
        observed_range = maximum - minimum
        prediction_95 = (
            decimal_student_t_quantile("0.975", len(values) - 1)
            * sample_sd
            * Decimal(2).sqrt()
        )
        prediction_99 = (
            decimal_student_t_quantile("0.995", len(values) - 1)
            * sample_sd
            * Decimal(2).sqrt()
        )
        display_quantum = Decimal("0.000000000000000001")
        prediction_95_display = prediction_95.quantize(
            display_quantum, rounding=ROUND_HALF_EVEN
        )
        prediction_99_display = prediction_99.quantize(
            display_quantum, rounding=ROUND_HALF_EVEN
        )
        bracket_screen = observed_range.quantize(
            Decimal("0.000001"), rounding=ROUND_HALF_EVEN
        )
        preflight_screen = maximum.quantize(
            Decimal("0.000000000000001"), rounding=ROUND_HALF_EVEN
        )
        maximum_budgetable_drift = prediction_99_display
        max_budgetable_excess = max(
            Decimal(0), maximum_budgetable_drift - bracket_screen
        )

    return {
        "numeric_semantics": "decimal_source_lexemes",
        "quantile_method": {
            "algorithm": SUCCESSOR_QUANTILE_METHOD,
            "precision_decimal_digits": SUCCESSOR_DECIMAL_PRECISION,
            "probabilities": {
                "prediction_95_two_draw": "0.975",
                "prediction_99_two_draw": "0.995",
            },
            "rounding": "ROUND_HALF_EVEN",
            "d102_df18_compatibility_pin": True,
        },
        "source_statistics": {
            "minimum_s": _decimal_text(minimum),
            "minimum_content_id": content_ids[values.index(minimum)],
            "maximum_s": _decimal_text(maximum),
            "maximum_content_id": content_ids[values.index(maximum)],
            "range_s": _decimal_text(observed_range),
            "mean_s": _decimal_text(
                mean.quantize(display_quantum, rounding=ROUND_HALF_EVEN)
            ),
            "sample_sd_s": _decimal_text(
                sample_sd.quantize(display_quantum, rounding=ROUND_HALF_EVEN)
            ),
            "prediction_95_two_draw_s": _decimal_text(prediction_95_display),
            "prediction_99_two_draw_s": _decimal_text(prediction_99_display),
        },
        "presentation_values": {
            "range_12_places_s": {
                "value": _decimal_text(
                    observed_range.quantize(
                        Decimal("0.000000000001"), rounding=ROUND_HALF_EVEN
                    )
                ),
                "label": "presentation_only_not_a_comparator",
            }
        },
        "rounding": {
            "mode": "ROUND_HALF_EVEN",
            "source_fields": "authenticated_decimal_lexemes_unrounded",
            "statistics_quantum_s": "0.000000000000000001",
            "bracket_screen": {
                "source": "source_statistics.range_s",
                "quantum_s": "0.000001",
                "value_s": _decimal_text(bracket_screen),
            },
            "preflight_level_screen": {
                "source_rule": SUCCESSOR_PREFLIGHT_SCREEN_RULE,
                "quantum_s": "0.000000000000001",
                "value_s": _decimal_text(preflight_screen),
            },
        },
        "ratified_operatives": {
            "bracket_screen_s": _decimal_text(bracket_screen),
            "preflight_level_screen_s": _decimal_text(preflight_screen),
            "max_budgetable_excess_s": _decimal_text(max_budgetable_excess),
            "maximum_budgetable_drift_s": _decimal_text(
                maximum_budgetable_drift
            ),
            # COLD-GATE-Q13: deliberately unchanged pending the re-convened
            # ruling; n<19 is refused above so this cannot reach df=1.
            "allowance_rule": "max(observed_drift_s,bracket_screen_s)",
            "operative_bound_rule": (
                "max(pre_b_fiducial_s,post_b_fiducial_s)"
                "+calibration_drift_allowance_s"
            ),
            "embedding_count": 1,
        },
    }


def _candidate_decimal(candidate: CalibrationCandidate) -> Decimal | None:
    value = candidate.b_fiducial_s
    if isinstance(value, Decimal):
        result = value
    elif isinstance(value, str):
        result = _decimal(value)
        if result is None:
            return None
    elif (
        isinstance(value, int | float)
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    ):
        # Compatibility for synthetic callers that predate D-102. Production
        # candidates carry strings from authenticated evidence bytes instead.
        result = Decimal(str(value))
    else:
        return None
    return result if result.is_finite() else None


def _current_estimator_code_sha256() -> dict[str, str] | None:
    try:
        return {
            relative: hashlib.sha256((_REPO_ROOT / relative).read_bytes()).hexdigest()
            for relative in ESTIMATOR_CODE_PATHS
        }
    except OSError:
        return None


def _path_has_symlink_component(path: Path, root: Path) -> bool:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return True
    current = root
    for part in relative.parts:
        current = current / part
        try:
            if current.is_symlink():
                return True
        except OSError:
            return True
    return False


def _repository_relative_path(value: Any) -> str | None:
    if not isinstance(value, str) or not value or "\\" in value:
        return None
    candidate = Path(value)
    if candidate.is_absolute() or value != candidate.as_posix():
        return None
    if any(part in {"", ".", ".."} for part in candidate.parts):
        return None
    return value


def _valid_registry(value: Any) -> bool:
    if (
        not isinstance(value, Mapping)
        or set(value) != {"schema_version", "authority", "entries"}
        or value.get("schema_version") != ACCEPTANCE_REGISTRY_SCHEMA
        or value.get("authority") != ACCEPTANCE_REGISTRY_AUTHORITY
        or not isinstance(value.get("entries"), list)
        or not value["entries"]
    ):
        return False
    expected_keys = {
        "acceptance_id",
        "artifact_path",
        "artifact_sha256",
        "derivation_sha256",
        "artifact_schema",
        "generation",
        "active",
        "parent_acceptance_id",
        "parent_artifact_sha256",
        "count_boundary_rule",
        "ledger_cutoff",
    }
    ids: set[str] = set()
    paths: set[str] = set()
    entries_by_id: dict[str, Mapping[str, Any]] = {}
    active_count = 0
    for entry in value["entries"]:
        cutoff = entry.get("ledger_cutoff") if isinstance(entry, Mapping) else None
        if (
            not isinstance(entry, Mapping)
            or set(entry) != expected_keys
            or not isinstance(entry.get("acceptance_id"), str)
            or not entry["acceptance_id"]
            or _repository_relative_path(entry.get("artifact_path")) is None
            or not entry["artifact_path"].startswith("configs/calibration/")
            or not _valid_sha256(entry.get("artifact_sha256"))
            or not _valid_sha256(entry.get("derivation_sha256"))
            or entry.get("artifact_schema")
            not in {ACCEPTANCE_BOUND_SCHEMA, ACCEPTANCE_SUCCESSOR_SCHEMA}
            or isinstance(entry.get("generation"), bool)
            or not isinstance(entry.get("generation"), int)
            or entry["generation"] < 1
            or not isinstance(entry.get("active"), bool)
            or entry.get("count_boundary_rule")
            not in _SUPPORTED_COUNT_BOUNDARY_RULES
            or not isinstance(cutoff, Mapping)
            or set(cutoff) != {"sequence", "head_digest", "ledger_schema"}
            or isinstance(cutoff.get("sequence"), bool)
            or not isinstance(cutoff.get("sequence"), int)
            or cutoff["sequence"] < 1
            or not _valid_sha256(cutoff.get("head_digest"))
            or cutoff.get("ledger_schema") != LEDGER_SCHEMA
        ):
            return False
        acceptance_id = entry["acceptance_id"]
        artifact_path = entry["artifact_path"]
        if acceptance_id in ids or artifact_path in paths:
            return False
        ids.add(acceptance_id)
        paths.add(artifact_path)
        entries_by_id[acceptance_id] = entry
        active_count += int(entry["active"])
    if active_count != 1:
        return False

    roots = 0
    child_counts = {entry["acceptance_id"]: 0 for entry in value["entries"]}
    for entry in value["entries"]:
        parent_id = entry["parent_acceptance_id"]
        parent_sha = entry["parent_artifact_sha256"]
        if parent_id is None:
            roots += 1
            if (
                parent_sha is not None
                or entry["generation"] != 1
                or entry["artifact_schema"] != ACCEPTANCE_BOUND_SCHEMA
                or entry["count_boundary_rule"] != GENESIS_COUNT_BOUNDARY_RULE
            ):
                return False
            continue
        parent = entries_by_id.get(parent_id)
        if (
            not isinstance(parent_id, str)
            or parent is None
            or parent_sha != parent["artifact_sha256"]
            or entry["generation"] != parent["generation"] + 1
            or entry["artifact_schema"] != ACCEPTANCE_SUCCESSOR_SCHEMA
            or entry["ledger_cutoff"]["sequence"]
            <= parent["ledger_cutoff"]["sequence"]
        ):
            return False
        child_counts[parent_id] += 1
        if child_counts[parent_id] > 1:
            return False
        seen = {entry["acceptance_id"]}
        cursor: Mapping[str, Any] | None = parent
        while cursor is not None:
            cursor_id = cursor["acceptance_id"]
            if cursor_id in seen:
                return False
            seen.add(cursor_id)
            next_parent = cursor["parent_acceptance_id"]
            cursor = entries_by_id.get(next_parent) if next_parent is not None else None
    leaves = [entry_id for entry_id, count in child_counts.items() if count == 0]
    active_ids = [entry["acceptance_id"] for entry in value["entries"] if entry["active"]]
    return bool(
        roots == 1
        and len(leaves) == 1
        and active_ids == leaves
        and {entry["generation"] for entry in value["entries"]}
        == set(range(1, len(value["entries"]) + 1))
    )


def _git_head_bytes(path: Path, repo_root: Path) -> bytes | None:
    try:
        relative = path.relative_to(repo_root).as_posix()
        completed = subprocess.run(
            ["git", "show", f"HEAD:{relative}"],
            cwd=repo_root,
            check=False,
            capture_output=True,
        )
    except (OSError, ValueError):
        return None
    return completed.stdout if completed.returncode == 0 else None


def load_calibration_acceptance_registry(
    path: Path = DEFAULT_ACCEPTANCE_REGISTRY_PATH,
    *,
    repo_root: Path = _REPO_ROOT,
    require_committed: bool = True,
) -> dict[str, Any]:
    """Load the single-active registry or raise one stable refusal reason.

    COLD-GATE-Q7: every fail-closed branch below has a diagnosable code; no
    invalid registry path collapses to a bare ``None``.
    """

    path = Path(path)
    lexical_repo_root = Path(repo_root).absolute()
    repo_root = Path(repo_root).resolve()
    if _path_has_symlink_component(path.absolute(), lexical_repo_root):
        raise CalibrationAcceptanceRegistryRefusal(
            "acceptance_registry_path_substituted"
        )
    try:
        resolved = path.resolve(strict=True)
        resolved.relative_to(repo_root)
        raw = resolved.read_bytes()
        value = json.loads(raw)
    except (OSError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
        raise CalibrationAcceptanceRegistryRefusal(
            "acceptance_registry_unreadable_or_outside_repository"
        ) from None
    if require_committed and _git_head_bytes(resolved, repo_root) != raw:
        raise CalibrationAcceptanceRegistryRefusal(
            "acceptance_registry_missing_commit"
        )
    if not _valid_registry(value):
        raise CalibrationAcceptanceRegistryRefusal(
            "acceptance_registry_schema_or_ancestry_invalid"
        )
    entries_by_id = {entry["acceptance_id"]: entry for entry in value["entries"]}
    artifacts_by_id: dict[str, Mapping[str, Any]] = {}
    for entry in value["entries"]:
        artifact_path = repo_root / entry["artifact_path"]
        if _path_has_symlink_component(artifact_path.absolute(), repo_root):
            raise CalibrationAcceptanceRegistryRefusal(
                "acceptance_registry_artifact_path_substituted"
            )
        try:
            artifact_resolved = artifact_path.resolve(strict=True)
            artifact_resolved.relative_to(repo_root)
            artifact_raw = artifact_resolved.read_bytes()
            artifact = json.loads(artifact_raw)
        except (OSError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
            raise CalibrationAcceptanceRegistryRefusal(
                "acceptance_registry_artifact_unreadable_or_outside_repository"
            ) from None
        if (
            require_committed
            and _git_head_bytes(artifact_resolved, repo_root) != artifact_raw
        ):
            raise CalibrationAcceptanceRegistryRefusal(
                "acceptance_registry_artifact_missing_commit"
            )
        if (
            hashlib.sha256(artifact_raw).hexdigest() != entry["artifact_sha256"]
            or not _valid_acceptance_bound(artifact)
            or artifact.get("acceptance_id") != entry["acceptance_id"]
            or artifact.get("schema_version") != entry["artifact_schema"]
            or artifact.get("derivation_sha256") != entry["derivation_sha256"]
            or {
                key: artifact["ledger_cutoff"].get(key)
                for key in ("sequence", "head_digest", "ledger_schema")
            }
            != entry["ledger_cutoff"]
        ):
            raise CalibrationAcceptanceRegistryRefusal(
                "acceptance_registry_artifact_authentication_failed"
            )
        artifacts_by_id[entry["acceptance_id"]] = artifact
        if entry["artifact_schema"] == ACCEPTANCE_SUCCESSOR_SCHEMA:
            filename_match = _SUCCESSOR_ARTIFACT_NAME_RE.fullmatch(
                Path(entry["artifact_path"]).name
            )
            if (
                filename_match is None
                or int(filename_match.group(1))
                != entry["ledger_cutoff"]["sequence"]
                or filename_match.group(2)
                != entry["ledger_cutoff"]["head_digest"][:16]
            ):
                raise CalibrationAcceptanceRegistryRefusal(
                    "acceptance_registry_successor_name_invalid"
                )
    for entry in value["entries"]:
        if entry["artifact_schema"] != ACCEPTANCE_SUCCESSOR_SCHEMA:
            continue
        artifact = artifacts_by_id[entry["acceptance_id"]]
        lineage = artifact["lineage"]
        parent_entry = entries_by_id.get(entry["parent_acceptance_id"])
        parent = artifacts_by_id.get(entry["parent_acceptance_id"])
        if parent_entry is None or parent is None:
            raise CalibrationAcceptanceRegistryRefusal(
                "acceptance_registry_parent_missing"
            )
        count = artifact["derivation_corpus"]["n"]
        parent_boundary = _artifact_count_boundary(parent)
        boundary_rule = entry["count_boundary_rule"]
        artifact_boundary_rule = artifact["prospective_rederivation"][
            "count_trigger"
        ]["rule"]
        if boundary_rule != artifact_boundary_rule:
            raise CalibrationAcceptanceRegistryRefusal(
                "acceptance_registry_boundary_rule_mismatch"
            )
        if boundary_rule == _COUNT_BOUNDARY_RULE_RETAIN_THEN_DOUBLE:
            expected_boundary = (
                parent_boundary if count < parent_boundary else 2 * count
            )
        else:
            raise CalibrationAcceptanceRegistryRefusal(
                "acceptance_registry_boundary_rule_unsupported"
            )
        if artifact["prospective_rederivation"]["count_trigger"][
            "next_boundary"
        ] != expected_boundary:
            raise CalibrationAcceptanceRegistryRefusal(
                "acceptance_registry_boundary_value_invalid"
            )
        if (
            lineage["generation"] != entry["generation"]
            or lineage["parent_acceptance_id"] != entry["parent_acceptance_id"]
            or lineage["parent_artifact_sha256"] != parent_entry["artifact_sha256"]
            or lineage["parent_derivation_sha256"] != parent["derivation_sha256"]
            or lineage["parent_ledger_cutoff"] != parent_entry["ledger_cutoff"]
        ):
            raise CalibrationAcceptanceRegistryRefusal(
                "acceptance_registry_lineage_invalid"
            )
    return dict(value)


def _active_registry_entry(registry: Mapping[str, Any]) -> Mapping[str, Any] | None:
    active = [
        entry
        for entry in registry.get("entries", ())
        if isinstance(entry, Mapping) and entry.get("active") is True
    ]
    return active[0] if len(active) == 1 else None


def _load_registry_for_current_active_selection() -> dict[str, Any]:
    """Load committed authority, with one legacy-root schema migration."""

    try:
        return load_calibration_acceptance_registry(require_committed=True)
    except CalibrationAcceptanceRegistryRefusal as exc:
        if exc.reason != "acceptance_registry_missing_commit":
            raise
    committed_raw = _git_head_bytes(
        DEFAULT_ACCEPTANCE_REGISTRY_PATH.resolve(), _REPO_ROOT
    )
    try:
        committed = json.loads(committed_raw) if committed_raw is not None else None
    except (UnicodeDecodeError, json.JSONDecodeError):
        committed = None
    # This branch exists only while the exhibit's additive per-entry field is
    # uncommitted. It authenticates the old HEAD registry and its HEAD artifact;
    # it never consumes a worktree registry or permits an active-entry switch.
    if (
        not isinstance(committed, Mapping)
        or not isinstance(committed.get("entries"), list)
        or len(committed["entries"]) != 1
        or not isinstance(committed["entries"][0], Mapping)
        or "count_boundary_rule" in committed["entries"][0]
    ):
        raise CalibrationAcceptanceRegistryRefusal(
            "acceptance_registry_missing_commit"
        )
    migrated = {
        **committed,
        "entries": [
            {
                **committed["entries"][0],
                "count_boundary_rule": GENESIS_COUNT_BOUNDARY_RULE,
            }
        ],
    }
    if not _valid_registry(migrated):
        raise CalibrationAcceptanceRegistryRefusal(
            "acceptance_registry_schema_or_ancestry_invalid"
        )
    entry = migrated["entries"][0]
    artifact_path = _REPO_ROOT / entry["artifact_path"]
    try:
        artifact_raw = artifact_path.read_bytes()
        artifact = json.loads(artifact_raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        raise CalibrationAcceptanceRegistryRefusal(
            "acceptance_registry_artifact_unreadable_or_outside_repository"
        ) from None
    if (
        _git_head_bytes(artifact_path.resolve(), _REPO_ROOT) != artifact_raw
        or hashlib.sha256(artifact_raw).hexdigest() != entry["artifact_sha256"]
        or not _valid_acceptance_bound(artifact)
        or artifact.get("acceptance_id") != entry["acceptance_id"]
        or artifact.get("schema_version") != entry["artifact_schema"]
        or artifact.get("derivation_sha256") != entry["derivation_sha256"]
    ):
        raise CalibrationAcceptanceRegistryRefusal(
            "acceptance_registry_artifact_authentication_failed"
        )
    return migrated


def _valid_successor_acceptance_bound(value: Mapping[str, Any]) -> bool:
    if (
        set(value) != _SUCCESSOR_TOP_LEVEL_FIELDS
        or value.get("schema_version") != ACCEPTANCE_SUCCESSOR_SCHEMA
        or value.get("artifact_role") != "issued"
        or not isinstance(value.get("acceptance_id"), str)
        or not value["acceptance_id"].startswith("d079_calibration_acceptance_v3_s")
        or value.get("decision_ids") != list(SUCCESSOR_DECISION_IDS)
        or value.get("derivation_sha256")
        != _canonical_sha256(
            {key: item for key, item in value.items() if key != "derivation_sha256"}
        )
    ):
        return False
    issuance = value.get("issuance")
    lineage = value.get("lineage")
    cutoff = value.get("ledger_cutoff")
    identity = value.get("identity_epoch")
    prospective = value.get("prospective_rederivation")
    corpus = value.get("derivation_corpus")
    prior = value.get("prior_observation_set")
    derivation = value.get("decimal_derivation")
    if (
        not isinstance(issuance, Mapping)
        or set(issuance) != {"status", "claim_eligible", "reason"}
        or issuance.get("status") != "issued"
        or issuance.get("claim_eligible") is not True
        or not isinstance(issuance.get("reason"), str)
        or not issuance["reason"]
        or not isinstance(cutoff, Mapping)
        or set(cutoff) != {"sequence", "head_digest", "ledger_schema", "role"}
        or isinstance(cutoff.get("sequence"), bool)
        or not isinstance(cutoff.get("sequence"), int)
        or cutoff["sequence"] < 1
        or not _valid_sha256(cutoff.get("head_digest"))
        or value["acceptance_id"]
        != (
            f"d079_calibration_acceptance_v3_s{cutoff['sequence']}_"
            f"{cutoff['head_digest'][:16]}"
        )
        or cutoff.get("ledger_schema") != LEDGER_SCHEMA
        or cutoff.get("role") != "issued_acceptance_baseline"
        or not isinstance(identity, Mapping)
        or set(identity) != set(ACCEPTANCE_IDENTITY_FIELDS)
        or any(identity.get(field) in (None, "") for field in ACCEPTANCE_IDENTITY_FIELDS)
    ):
        return False
    if (
        not isinstance(lineage, Mapping)
        or set(lineage)
        != {
            "generation",
            "root_acceptance_id",
            "parent_acceptance_id",
            "parent_artifact_sha256",
            "parent_derivation_sha256",
            "parent_ledger_cutoff",
            "trigger_judgment",
        }
        or isinstance(lineage.get("generation"), bool)
        or not isinstance(lineage.get("generation"), int)
        or lineage["generation"] < 2
        or any(
            not isinstance(lineage.get(field), str) or not lineage[field]
            for field in ("root_acceptance_id", "parent_acceptance_id")
        )
        or not _valid_sha256(lineage.get("parent_artifact_sha256"))
        or not _valid_sha256(lineage.get("parent_derivation_sha256"))
        or not isinstance(lineage.get("parent_ledger_cutoff"), Mapping)
        or set(lineage["parent_ledger_cutoff"])
        != {"sequence", "head_digest", "ledger_schema"}
        or isinstance(lineage["parent_ledger_cutoff"].get("sequence"), bool)
        or not isinstance(lineage["parent_ledger_cutoff"].get("sequence"), int)
        or lineage["parent_ledger_cutoff"]["sequence"] >= cutoff["sequence"]
        or not _valid_sha256(lineage["parent_ledger_cutoff"].get("head_digest"))
        or lineage["parent_ledger_cutoff"].get("ledger_schema") != LEDGER_SCHEMA
        or not isinstance(lineage.get("trigger_judgment"), Mapping)
    ):
        return False
    judgment = lineage["trigger_judgment"]
    if (
        set(judgment)
        != {
            "judged_under_acceptance_id",
            "judged_under_artifact_sha256",
            "result",
            "new_content_ids",
            "triggers",
        }
        or judgment.get("judged_under_acceptance_id")
        != lineage["parent_acceptance_id"]
        or judgment.get("judged_under_artifact_sha256")
        != lineage["parent_artifact_sha256"]
        or judgment.get("result") != "successor_required"
        or not isinstance(judgment.get("new_content_ids"), list)
        or judgment["new_content_ids"] != sorted(set(judgment["new_content_ids"]))
        or not all(_valid_sha256(item) for item in judgment["new_content_ids"])
        or not isinstance(judgment.get("triggers"), list)
        or not judgment["triggers"]
        or judgment["triggers"]
        != [
            trigger
            for trigger in (
                "new_valid_same_identity_capture_expands_observed_range",
                "content_distinct_valid_same_epoch_count_boundary",
            )
            if trigger in judgment["triggers"]
        ]
    ):
        return False
    if (
        not isinstance(prospective, Mapping)
        or prospective.get("calendar_expiry") is not None
        or prospective.get("trigger_observation_rule")
        != "judge_under_prior_artifact_never_self_fit"
        or prospective.get("protocol_sha256") != protocol_sha256(PROTOCOL_ID)
        or prospective.get("estimator_code_sha256")
        != _current_estimator_code_sha256()
        or prospective.get("triggers")
        != [
            "identity_field_change",
            "protocol_or_estimator_byte_change",
            "new_valid_same_identity_capture_expands_observed_range",
            "content_distinct_valid_same_epoch_count_boundary",
            "new_systematic_failure_challenges_preflight_screen",
        ]
        or not isinstance(prospective.get("count_trigger"), Mapping)
        or set(prospective["count_trigger"])
        != {"source_corpus_count", "next_boundary", "rule"}
        or prospective["count_trigger"].get("rule")
        not in {
            rule
            for rule in _SUPPORTED_COUNT_BOUNDARY_RULES
            if rule != GENESIS_COUNT_BOUNDARY_RULE
        }
    ):
        return False
    if (
        not isinstance(corpus, Mapping)
        or set(corpus) != {"selection", "n", "members"}
        or corpus.get("selection") != SUCCESSOR_CORPUS_SELECTION
        or isinstance(corpus.get("n"), bool)
        or not isinstance(corpus.get("n"), int)
        or corpus["n"] < SUCCESSOR_MINIMUM_CORPUS_SIZE
        or not isinstance(corpus.get("members"), list)
        or len(corpus["members"]) != corpus["n"]
        or prospective["count_trigger"].get("source_corpus_count") != corpus["n"]
        or isinstance(prospective["count_trigger"].get("next_boundary"), bool)
        or not isinstance(prospective["count_trigger"].get("next_boundary"), int)
        or prospective["count_trigger"]["next_boundary"] <= corpus["n"]
    ):
        return False
    member_keys = {
        "content_id",
        "attempt_id",
        "finalization_sequence",
        "receipt_digest",
        "custody_locator",
        "b_fiducial_s",
        "manifest_sha256",
        "instrument_evidence_sha256",
    }
    member_ids: list[str] = []
    for member in corpus["members"]:
        if (
            not isinstance(member, Mapping)
            or set(member) != member_keys
            or not _valid_sha256(member.get("content_id"))
            or not isinstance(member.get("attempt_id"), str)
            or not member["attempt_id"]
            or isinstance(member.get("finalization_sequence"), bool)
            or not isinstance(member.get("finalization_sequence"), int)
            or member["finalization_sequence"] < 1
            or member["finalization_sequence"] > cutoff["sequence"]
            or not _valid_sha256(member.get("receipt_digest"))
            or not isinstance(member.get("custody_locator"), str)
            or not member["custody_locator"]
            or (bound := _decimal(member.get("b_fiducial_s"))) is None
            or bound < 0
            or not _valid_sha256(member.get("manifest_sha256"))
            or not _valid_sha256(member.get("instrument_evidence_sha256"))
        ):
            return False
        member_ids.append(member["content_id"])
    if member_ids != sorted(set(member_ids)):
        return False
    if (
        not isinstance(prior, Mapping)
        or set(prior)
        != {
            "cutoff",
            "content_identity_method",
            "epoch_catalog",
            "observations",
            "noncontent_attempts",
        }
        or prior.get("cutoff")
        != {key: cutoff[key] for key in ("sequence", "head_digest", "ledger_schema")}
        or prior.get("content_identity_method")
        != "sha256(canonical_json({instrument_evidence.json,manifest.json} byte sha256s))"
        or not isinstance(prior.get("epoch_catalog"), Mapping)
        or prior["epoch_catalog"].get("active_epoch") != identity
        or any(
            not isinstance(epoch_id, str)
            or not epoch_id
            or not isinstance(epoch, Mapping)
            or set(epoch) != set(ACCEPTANCE_IDENTITY_FIELDS)
            or any(epoch.get(field) in (None, "") for field in ACCEPTANCE_IDENTITY_FIELDS)
            for epoch_id, epoch in prior["epoch_catalog"].items()
        )
        or len(
            {
                tuple((field, epoch[field]) for field in ACCEPTANCE_IDENTITY_FIELDS)
                for epoch in prior["epoch_catalog"].values()
            }
        )
        != len(prior["epoch_catalog"])
        or not isinstance(prior.get("observations"), list)
        or not isinstance(prior.get("noncontent_attempts"), list)
    ):
        return False
    all_attempt_ids: set[str] = set()
    all_sequences: set[int] = set()
    all_receipts: set[str] = set()
    for row in prior["noncontent_attempts"]:
        if (
            not isinstance(row, Mapping)
            or set(row)
            != {
                "attempt_id",
                "closure_sequence",
                "receipt_digest",
                "disposition",
                "custody_locator",
            }
            or not isinstance(row.get("attempt_id"), str)
            or not row["attempt_id"]
            or isinstance(row.get("closure_sequence"), bool)
            or not isinstance(row.get("closure_sequence"), int)
            or row["closure_sequence"] < 1
            or row["closure_sequence"] > cutoff["sequence"]
            or not _valid_sha256(row.get("receipt_digest"))
            or row.get("disposition")
            not in {"governed-unused-slot", "abandoned"}
            or not isinstance(row.get("custody_locator"), str)
            or not row["custody_locator"]
            or row["attempt_id"] in all_attempt_ids
            or row["closure_sequence"] in all_sequences
            or row["receipt_digest"] in all_receipts
        ):
            return False
        all_attempt_ids.add(row["attempt_id"])
        all_sequences.add(row["closure_sequence"])
        all_receipts.add(row["receipt_digest"])
    prior_ids: list[str] = []
    valid_active_ids: set[str] = set()
    prior_by_id: dict[str, Mapping[str, Any]] = {}
    for observation in prior["observations"]:
        if (
            not isinstance(observation, Mapping)
            or set(observation)
            != {
                "content_id",
                "epoch_id",
                "disposition",
                "representative_attempt_id",
                "attempts",
            }
            or not _valid_sha256(observation.get("content_id"))
            or observation.get("epoch_id") not in prior["epoch_catalog"]
            or observation.get("disposition")
            not in {"valid", "systematic-invalid", "ordinary-invalid"}
            or not isinstance(observation.get("representative_attempt_id"), str)
            or not isinstance(observation.get("attempts"), list)
            or not observation["attempts"]
        ):
            return False
        attempts = observation["attempts"]
        sequences: list[int] = []
        for attempt in attempts:
            if (
                not isinstance(attempt, Mapping)
                or set(attempt)
                != {
                    "attempt_id",
                    "finalization_sequence",
                    "receipt_digest",
                    "observation_kind",
                    "custody_locator",
                    "exact_bound_lexeme_s",
                    "manifest_sha256",
                    "instrument_evidence_sha256",
                }
                or not isinstance(attempt.get("attempt_id"), str)
                or not attempt["attempt_id"]
                or isinstance(attempt.get("finalization_sequence"), bool)
                or not isinstance(attempt.get("finalization_sequence"), int)
                or attempt["finalization_sequence"] < 1
                or attempt["finalization_sequence"] > cutoff["sequence"]
                or not _valid_sha256(attempt.get("receipt_digest"))
                or attempt.get("observation_kind")
                not in {
                    "historical-import",
                    "live-capture",
                    "bracket-session-finalized",
                    "bracket-session-aborted",
                }
                or not isinstance(attempt.get("custody_locator"), str)
                or not attempt["custody_locator"]
                or not _valid_sha256(attempt.get("manifest_sha256"))
                or not _valid_sha256(attempt.get("instrument_evidence_sha256"))
                or (
                    attempt.get("exact_bound_lexeme_s") is not None
                    and (
                        (attempt_bound := _decimal(attempt["exact_bound_lexeme_s"]))
                        is None
                        or attempt_bound < 0
                    )
                )
                or observation["disposition"] == "valid"
                and attempt.get("exact_bound_lexeme_s") is None
                or attempt["attempt_id"] in all_attempt_ids
                or attempt["finalization_sequence"] in all_sequences
                or attempt["receipt_digest"] in all_receipts
            ):
                return False
            sequences.append(attempt["finalization_sequence"])
            all_attempt_ids.add(attempt["attempt_id"])
            all_sequences.add(attempt["finalization_sequence"])
            all_receipts.add(attempt["receipt_digest"])
        if sequences != sorted(sequences) or observation["representative_attempt_id"] != attempts[0]["attempt_id"]:
            return False
        prior_ids.append(observation["content_id"])
        prior_by_id[observation["content_id"]] = observation
        if observation["disposition"] == "valid" and observation["epoch_id"] == "active_epoch":
            valid_active_ids.add(observation["content_id"])
    if prior_ids != sorted(set(prior_ids)) or valid_active_ids != set(member_ids):
        return False
    for member in corpus["members"]:
        row = prior_by_id[member["content_id"]]
        representative = row["attempts"][0]
        if (
            row["disposition"] != "valid"
            or row["epoch_id"] != "active_epoch"
            or member["attempt_id"] != representative["attempt_id"]
            or member["finalization_sequence"]
            != representative["finalization_sequence"]
            or member["receipt_digest"] != representative["receipt_digest"]
            or member["custody_locator"] != representative["custody_locator"]
            or member["b_fiducial_s"] != representative["exact_bound_lexeme_s"]
            or member["manifest_sha256"] != representative["manifest_sha256"]
            or member["instrument_evidence_sha256"]
            != representative["instrument_evidence_sha256"]
        ):
            return False
    try:
        expected_derivation = derive_successor_decimal_derivation(corpus["members"])
    except (ArithmeticError, InvalidOperation, ValueError):
        return False
    return derivation == expected_derivation


def _valid_acceptance_bound(value: Any) -> bool:
    """Validate the D-102 artifact from its decimal-source member table."""

    if not isinstance(value, Mapping):
        return False
    if value.get("schema_version") == ACCEPTANCE_SUCCESSOR_SCHEMA:
        return _valid_successor_acceptance_bound(value)
    core = {key: item for key, item in value.items() if key != "derivation_sha256"}
    identity = value.get("identity_epoch")
    prospective = value.get("prospective_rederivation")
    corpus = value.get("derivation_corpus")
    prior = value.get("prior_observation_set")
    cutoff = value.get("ledger_cutoff")
    issuance = value.get("issuance")
    backfill = value.get("backfill_candidate")
    derivation = value.get("decimal_derivation")
    role = value.get("artifact_role")
    if role == "schema_fixture_unissued":
        role_valid = (
            value.get("schema_version") == ACCEPTANCE_FIXTURE_SCHEMA
            and isinstance(issuance, Mapping)
            and issuance.get("status") == "unratified_fixture"
            and issuance.get("claim_eligible") is False
            and isinstance(cutoff, Mapping)
            and cutoff.get("sequence") == 0
            and cutoff.get("head_digest") == "0" * 64
            and cutoff.get("role")
            == "fixture_genesis_not_a_production_issuance_cutoff"
            and isinstance(backfill, Mapping)
            and backfill.get("status") == "unratified_candidate_only"
            and backfill.get("production_issuance_blocked") is True
        )
        allowed_prior_dispositions = {
            "valid",
            "systematic-invalid",
            "ordinary-invalid",
            "blind-holdout",
            "unresolved",
        }
    elif role == "issued":
        role_valid = (
            value.get("schema_version") == ACCEPTANCE_BOUND_SCHEMA
            and isinstance(issuance, Mapping)
            and issuance.get("status") == "issued"
            and issuance.get("claim_eligible") is True
            and isinstance(cutoff, Mapping)
            and isinstance(cutoff.get("sequence"), int)
            and not isinstance(cutoff.get("sequence"), bool)
            and cutoff.get("sequence") > 0
            and _valid_sha256(cutoff.get("head_digest"))
            and cutoff.get("head_digest") != "0" * 64
            and cutoff.get("role") == "issued_acceptance_baseline"
            and isinstance(backfill, Mapping)
            and backfill.get("status") == "issued"
            and backfill.get("production_issuance_blocked") is False
        )
        allowed_prior_dispositions = {
            "valid",
            "systematic-invalid",
            "ordinary-invalid",
        }
    else:
        return False
    if (
        not role_valid
        or value.get("acceptance_id") != "d079_calibration_acceptance_v2_n19"
        or value.get("decision_ids") != ["D-102", "D-109"]
        or value.get("derivation_sha256") != _canonical_sha256(core)
        or not isinstance(identity, Mapping)
        or set(identity) != set(ACCEPTANCE_IDENTITY_FIELDS)
        or any(identity.get(field) in (None, "") for field in ACCEPTANCE_IDENTITY_FIELDS)
        or not isinstance(prospective, Mapping)
        or prospective.get("calendar_expiry") is not None
        or prospective.get("trigger_observation_rule")
        != "judge_under_prior_artifact_never_self_fit"
        or prospective.get("protocol_sha256") != protocol_sha256(PROTOCOL_ID)
        or not isinstance(prospective.get("estimator_code_sha256"), Mapping)
        or set(prospective["estimator_code_sha256"]) != set(ESTIMATOR_CODE_PATHS)
        or any(
            not _valid_sha256(item)
            for item in prospective["estimator_code_sha256"].values()
        )
        or not isinstance(prospective.get("triggers"), list)
        or set(prospective["triggers"])
        != {
            "identity_field_change",
            "protocol_or_estimator_byte_change",
            "new_valid_same_identity_capture_expands_observed_range",
            "corpus_doubles_from_19_to_38",
            "new_systematic_failure_challenges_preflight_screen",
        }
        or not isinstance(corpus, Mapping)
        or corpus.get("n") != 19
        or not isinstance(corpus.get("members"), list)
        or len(corpus["members"]) != 19
        or not isinstance(cutoff, Mapping)
        or cutoff.get("ledger_schema") != LEDGER_SCHEMA
        or not isinstance(prior, Mapping)
        or prior.get("cutoff")
        != {
            "sequence": cutoff.get("sequence"),
            "head_digest": cutoff.get("head_digest"),
            "ledger_schema": cutoff.get("ledger_schema"),
        }
        or not isinstance(prior.get("epoch_catalog"), Mapping)
        or set(prior["epoch_catalog"]) != {"d079_epoch"}
        or prior["epoch_catalog"].get("d079_epoch") != identity
        or not isinstance(prior.get("observations"), list)
        or not isinstance(derivation, Mapping)
        or derivation.get("numeric_semantics") != "decimal_source_lexemes"
    ):
        return False
    member_ids: list[str] = []
    values: list[Decimal] = []
    for member in corpus["members"]:
        if (
            not isinstance(member, Mapping)
            or set(member)
            != {
                "member_id",
                "source_directory",
                "b_fiducial_s",
                "manifest_sha256",
                "instrument_evidence_sha256",
            }
            or not isinstance(member.get("member_id"), str)
            or not isinstance(member.get("source_directory"), str)
            or not _valid_sha256(member.get("manifest_sha256"))
            or not _valid_sha256(member.get("instrument_evidence_sha256"))
        ):
            return False
        bound = _decimal(member.get("b_fiducial_s"))
        if bound is None or bound < 0:
            return False
        member_ids.append(member["member_id"])
        values.append(bound)
    if len(set(member_ids)) != 19 or member_ids != sorted(member_ids):
        return False

    prior_ids: list[str] = []
    prior_attempt_ids: list[str] = []
    prior_member_ids: set[str] = set()
    for observation in prior["observations"]:
        if (
            not isinstance(observation, Mapping)
            or set(observation)
            != {"content_id", "epoch_id", "disposition", "attempt_id"}
            or not _valid_sha256(observation.get("content_id"))
            or observation.get("epoch_id") != "d079_epoch"
            or observation.get("disposition") not in allowed_prior_dispositions
            or not isinstance(observation.get("attempt_id"), str)
            or not observation.get("attempt_id")
        ):
            return False
        prior_ids.append(observation["content_id"])
        prior_attempt_ids.append(observation["attempt_id"])
        if observation["attempt_id"] in member_ids:
            prior_member_ids.add(observation["attempt_id"])
    if (
        len(prior_ids) != len(set(prior_ids))
        or len(prior_attempt_ids) != len(set(prior_attempt_ids))
        or prior_member_ids != set(member_ids)
    ):
        return False
    if role == "issued":
        disposition_counts = {
            disposition: sum(
                observation["disposition"] == disposition
                for observation in prior["observations"]
            )
            for disposition in sorted(allowed_prior_dispositions)
        }
        if (
            len(prior["observations"]) != 38
            or cutoff["sequence"] != 2 * len(prior["observations"])
            or backfill.get("candidate_inventory") != disposition_counts
        ):
            return False
    member_content_ids = {
        content_id_from_artifact_hashes(
            {
                "manifest.json": member["manifest_sha256"],
                "instrument_evidence.json": member[
                    "instrument_evidence_sha256"
                ],
            }
        )
        for member in corpus["members"]
    }
    if None in member_content_ids or not member_content_ids.issubset(set(prior_ids)):
        return False

    statistics = derivation.get("source_statistics")
    rounding = derivation.get("rounding")
    operatives = derivation.get("ratified_operatives")
    if not all(isinstance(item, Mapping) for item in (statistics, rounding, operatives)):
        return False
    with localcontext() as context:
        context.prec = 80
        count = Decimal(len(values))
        mean = sum(values, Decimal(0)) / count
        sample_sd = (
            sum((item - mean) ** 2 for item in values) / Decimal(len(values) - 1)
        ).sqrt()
        quantum = Decimal("0.000000000000000001")
        expected_statistics = {
            "minimum_s": str(min(values)),
            "maximum_s": str(max(values)),
            "range_s": str(max(values) - min(values)),
            "mean_presentation_s": str(
                mean.quantize(quantum, rounding=ROUND_HALF_EVEN)
            ),
            "sample_sd_presentation_s": str(
                sample_sd.quantize(quantum, rounding=ROUND_HALF_EVEN)
            ),
        }
    minimum_id = member_ids[values.index(min(values))]
    maximum_id = member_ids[values.index(max(values))]
    if (
        statistics.get("minimum_s") != expected_statistics["minimum_s"]
        or statistics.get("maximum_s") != expected_statistics["maximum_s"]
        or statistics.get("range_s") != expected_statistics["range_s"]
        or statistics.get("minimum_member_id") != minimum_id
        or statistics.get("maximum_member_id") != maximum_id
        or not isinstance(statistics.get("mean_presentation_s"), Mapping)
        or statistics["mean_presentation_s"].get("value")
        != expected_statistics["mean_presentation_s"]
        or statistics["mean_presentation_s"].get("label")
        != "rounded_presentation"
        or not isinstance(statistics.get("sample_sd_presentation_s"), Mapping)
        or statistics["sample_sd_presentation_s"].get("value")
        != expected_statistics["sample_sd_presentation_s"]
        or statistics["sample_sd_presentation_s"].get("label")
        != "rounded_presentation"
        or statistics.get("prediction_95_two_draw_s")
        != "0.008826584887500717"
        or statistics.get("prediction_99_two_draw_s")
        != "0.012093166090593858"
        or rounding.get("mode") != "ROUND_HALF_EVEN"
        or not isinstance(rounding.get("operative_bracket_screen"), Mapping)
        or rounding["operative_bracket_screen"].get("quantum_s") != "0.000001"
        or rounding["operative_bracket_screen"].get("value_s")
        != _D102_OPERATIVE_VALUES["bracket_screen_s"]
        or not isinstance(rounding.get("preflight_level_screen"), Mapping)
        or rounding["preflight_level_screen"].get("quantum_s")
        != "0.000000000000001"
        or rounding["preflight_level_screen"].get("value_s")
        != _D102_OPERATIVE_VALUES["preflight_level_screen_s"]
        or any(operatives.get(key) != item for key, item in _D102_OPERATIVE_VALUES.items())
        or operatives.get("allowance_rule")
        != "max(observed_drift_s,bracket_screen_s)"
        or operatives.get("operative_bound_rule")
        != "max(pre_b_fiducial_s,post_b_fiducial_s)+calibration_drift_allowance_s"
        or operatives.get("embedding_count") != 1
    ):
        return False
    screen = Decimal(_D102_OPERATIVE_VALUES["bracket_screen_s"])
    maximum = Decimal(_D102_OPERATIVE_VALUES["maximum_budgetable_drift_s"])
    excess = Decimal(_D102_OPERATIVE_VALUES["max_budgetable_excess_s"])
    return (
        (max(values) - min(values)).quantize(
            Decimal("0.000001"), rounding=ROUND_HALF_EVEN
        )
        == screen
        and max(values).quantize(
            Decimal("0.000000000000001"), rounding=ROUND_HALF_EVEN
        )
        == Decimal(_D102_OPERATIVE_VALUES["preflight_level_screen_s"])
        and screen + excess == maximum
    )


def load_calibration_acceptance_bound(
    path: Path | None = None,
) -> dict[str, Any] | None:
    """Load the registry-selected D-102 acceptance artifact fail-closed.

    An explicit path retains the exact-byte v2 bootstrap route;
    successors are accepted only through a registry entry.
    """

    if path is None:
        registry = _load_registry_for_current_active_selection()
        active = _active_registry_entry(registry)
        if active is None:
            return None
        requested = _REPO_ROOT / str(active["artifact_path"])
        try:
            raw = requested.read_bytes()
        except OSError:
            return None
        return _acceptance_bound_from_authenticated_bytes(
            raw,
            expected_sha256=str(active["artifact_sha256"]),
        )

    requested = Path(path)
    try:
        raw = requested.read_bytes()
    except OSError:
        return None
    return _acceptance_bound_from_authenticated_bytes(raw)


def _acceptance_bound_from_authenticated_bytes(
    raw: bytes,
    *,
    expected_sha256: str | None = None,
) -> dict[str, Any] | None:
    """Parse acceptance bytes only when their role-indexed pin authenticates."""

    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    # Any file route is authenticated by one of the two reviewed exact-byte
    # states: the genesis fixture retained for pre-issuance tests, or the
    # deterministically emitted issued artifact. A caller cannot turn an
    # alternate self-consistent document into authority by choosing a path.
    role = value.get("artifact_role") if isinstance(value, Mapping) else None
    schema = value.get("schema_version") if isinstance(value, Mapping) else None
    authenticated_sha256 = expected_sha256
    if authenticated_sha256 is None:
        authenticated_sha256 = {
            "schema_fixture_unissued": DEFAULT_ACCEPTANCE_BOUND_SHA256,
            "issued": (
                ISSUED_ACCEPTANCE_BOUND_SHA256
                if schema == ACCEPTANCE_BOUND_SCHEMA
                else None
            ),
        }.get(role)
    if hashlib.sha256(raw).hexdigest() != authenticated_sha256:
        return None
    if not _valid_acceptance_bound(value):
        return None
    return dict(value)


def _authenticated_explicit_acceptance_bound(
    value: Mapping[str, Any],
) -> dict[str, Any] | None:
    """Authenticate an in-memory artifact against the checked-in byte pin."""

    pinned = load_calibration_acceptance_bound()
    if pinned is None or dict(value) != pinned:
        return None
    return pinned


def _acceptance_artifact_sha256(artifact: Mapping[str, Any]) -> str:
    """Return the reviewed exact-byte pin for a validated artifact role."""

    registry = _load_registry_for_current_active_selection()
    active = _active_registry_entry(registry)
    if active is not None and active.get("acceptance_id") == artifact.get("acceptance_id"):
        return str(active["artifact_sha256"])
    return (
        ISSUED_ACCEPTANCE_BOUND_SHA256
        if artifact.get("artifact_role") == "issued"
        else DEFAULT_ACCEPTANCE_BOUND_SHA256
    )


def _valid_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value)
    )


def _artifact_prior_content_ids(artifact: Mapping[str, Any]) -> set[str]:
    return {
        row["content_id"]
        for row in artifact["prior_observation_set"]["observations"]
        if isinstance(row, Mapping) and _valid_sha256(row.get("content_id"))
    }


def _artifact_corpus_values(artifact: Mapping[str, Any]) -> tuple[Decimal, ...]:
    values = tuple(
        value
        for member in artifact["derivation_corpus"]["members"]
        if (value := _decimal(member.get("b_fiducial_s"))) is not None
    )
    return values


def _artifact_count_boundary(artifact: Mapping[str, Any]) -> int:
    if artifact.get("schema_version") == ACCEPTANCE_SUCCESSOR_SCHEMA:
        return int(
            artifact["prospective_rederivation"]["count_trigger"][
                "next_boundary"
            ]
        )
    return 38


def _probe_observation_universe(
    snapshot: CalibrationLedgerSnapshot,
) -> tuple[LedgerObservation, ...]:
    observations = list(snapshot.observations)
    visible_attempts = {observation.attempt_id for observation in observations}
    # U1 deliberately withholds open-session evidence from the ordinary
    # consumption universe. The pre-science probe is the one authorized reader
    # of a finalized PRE in that governed open capability.
    if snapshot.is_governed_open_bracket_extension:
        for session in snapshot.bracket_sessions:
            if session.state != "open":
                continue
            observations.extend(
                observation
                for observation in session.finalized_slots.values()
                if observation.attempt_id not in visible_attempts
            )
    return tuple(sorted(observations, key=lambda observation: observation.sequence))


def _group_probe_observations(
    observations: Sequence[LedgerObservation],
) -> tuple[dict[str, tuple[LedgerObservation, ...]], tuple[LedgerObservation, ...]] | None:
    grouped: dict[str, list[LedgerObservation]] = {}
    noncontent: list[LedgerObservation] = []
    for observation in observations:
        if observation.content_id is None:
            noncontent.append(observation)
            continue
        grouped.setdefault(observation.content_id, []).append(observation)
    result: dict[str, tuple[LedgerObservation, ...]] = {}
    for content_id, aliases in sorted(grouped.items()):
        ordered = tuple(sorted(aliases, key=lambda observation: observation.sequence))
        first = ordered[0]
        expected = (
            first.classification_disposition,
            dict(first.identity_epoch),
            dict(first.artifact_sha256),
            first.exact_bound_lexeme_s,
        )
        if any(
            (
                alias.classification_disposition,
                dict(alias.identity_epoch),
                dict(alias.artifact_sha256),
                alias.exact_bound_lexeme_s,
            )
            != expected
            for alias in ordered[1:]
        ):
            return None
        result[content_id] = ordered
    return result, tuple(sorted(noncontent, key=lambda observation: observation.sequence))


def _terminal_no_content_rows(
    noncontent: Sequence[LedgerObservation],
    ledger_snapshot: CalibrationLedgerSnapshot,
    cutoff_sequence: int,
) -> list[dict[str, Any]]:
    """Authenticate terminal no-content closures and project their audit rows."""

    rows: list[dict[str, Any]] = []
    for observation in noncontent:
        if observation.sequence > cutoff_sequence:
            continue
        if (
            observation.disposition != "abandoned"
            or observation.content_id is not None
            or bool(observation.artifact_sha256)
            or observation.exact_bound_lexeme_s is not None
            or not isinstance(observation.attempt_id, str)
            or not observation.attempt_id
            or not isinstance(observation.custody_locator, str)
            or not observation.custody_locator
            or observation.sequence < 1
            or observation.sequence > len(ledger_snapshot.receipts)
        ):
            raise ValueError("successor_terminal_no_content_closure_invalid")
        receipt = ledger_snapshot.receipts[observation.sequence - 1]
        artifacts = receipt.get("artifact_sha256") if isinstance(receipt, Mapping) else None
        if (
            not isinstance(receipt, Mapping)
            or receipt.get("event")
            not in {"finalization", "bracket-session-slot-finalization"}
            or receipt.get("receipt_digest") != observation.receipt_digest
            or receipt.get("attempt_id") != observation.attempt_id
            or receipt.get("disposition") != "abandoned"
            or receipt.get("content_id") is not None
            or not isinstance(artifacts, Mapping)
            or bool(artifacts)
            or receipt.get("exact_bound_lexeme_s") is not None
        ):
            raise ValueError("successor_terminal_no_content_receipt_malformed")
        rows.append(
            {
                "attempt_id": observation.attempt_id,
                "closure_sequence": observation.sequence,
                "receipt_digest": observation.receipt_digest,
                "disposition": "abandoned",
                "custody_locator": observation.custody_locator,
            }
        )
    return rows


def _observation_custody_authentic(observation: LedgerObservation) -> bool:
    if observation.content_id is None or not observation.artifact_sha256:
        return False
    candidate = _candidate_from_observation(
        observation
        if observation.disposition == "valid"
        else replace(observation, disposition="valid")
    )
    return candidate is not None


def _probe_result(
    *,
    outcome: str,
    active: Mapping[str, Any] | None,
    artifact: Mapping[str, Any] | None,
    snapshot: CalibrationLedgerSnapshot,
    observed_identity_epoch: Mapping[str, Any] | None,
    new_content_ids: Sequence[str] = (),
    triggers: Sequence[str] = (),
    refusal_reasons: Sequence[str] = (),
) -> dict[str, Any]:
    cutoff = artifact.get("ledger_cutoff") if isinstance(artifact, Mapping) else None
    return {
        "schema_version": ACCEPTANCE_TRIGGER_PROBE_SCHEMA,
        "outcome": outcome,
        "active_acceptance_id": (
            artifact.get("acceptance_id") if isinstance(artifact, Mapping) else None
        ),
        "artifact_sha256": active.get("artifact_sha256") if active else None,
        "derivation_sha256": (
            artifact.get("derivation_sha256")
            if isinstance(artifact, Mapping)
            else None
        ),
        "parent_cutoff": (
            {
                key: cutoff.get(key)
                for key in ("sequence", "head_digest", "ledger_schema")
            }
            if isinstance(cutoff, Mapping)
            else None
        ),
        "current_ledger_head": {
            "sequence": snapshot.head_sequence,
            "head_digest": snapshot.head_digest,
            "ledger_schema": snapshot.ledger_schema,
            "committed_sequence": snapshot.committed_head_sequence,
            "committed_digest": snapshot.committed_head_digest,
        },
        "observed_identity_epoch": (
            dict(observed_identity_epoch)
            if isinstance(observed_identity_epoch, Mapping)
            else None
        ),
        "new_content_ids": list(new_content_ids),
        "observed_triggers": list(triggers),
        "refusal_reasons": list(refusal_reasons),
        "writer_integration_scope_status": WRITER_INTEGRATION_SCOPE_STATUS,
    }


def probe_calibration_acceptance_trigger(
    ledger_snapshot: CalibrationLedgerSnapshot,
    *,
    observed_identity_epoch: Mapping[str, Any] | None,
    registry_path: Path = DEFAULT_ACCEPTANCE_REGISTRY_PATH,
    repo_root: Path = _REPO_ROOT,
    require_committed_registry: bool = True,
    verify_custody: bool = True,
) -> dict[str, Any]:
    """Authenticate the active artifact and classify the pre/post trigger.

    This is the U2 hook shape for §5A. It performs no writes and returns one of
    the four closed outcomes required by the cold-gate brief.
    """

    empty_snapshot = isinstance(ledger_snapshot, CalibrationLedgerSnapshot)
    if not empty_snapshot:
        raise TypeError("ledger_snapshot must be a CalibrationLedgerSnapshot")
    try:
        registry = load_calibration_acceptance_registry(
            registry_path,
            repo_root=repo_root,
            require_committed=require_committed_registry,
        )
    except CalibrationAcceptanceRegistryRefusal as exc:
        return _probe_result(
            outcome="authentication_or_epoch_refusal",
            active=None,
            artifact=None,
            snapshot=ledger_snapshot,
            observed_identity_epoch=observed_identity_epoch,
            refusal_reasons=(exc.reason,),
        )
    active = _active_registry_entry(registry)
    artifact: dict[str, Any] | None = None
    if active is not None:
        try:
            raw = (Path(repo_root) / str(active["artifact_path"])).read_bytes()
        except OSError:
            raw = b""
        artifact = _acceptance_bound_from_authenticated_bytes(
            raw,
            expected_sha256=str(active["artifact_sha256"]),
        )
    if active is None or artifact is None:
        return _probe_result(
            outcome="authentication_or_epoch_refusal",
            active=active,
            artifact=artifact,
            snapshot=ledger_snapshot,
            observed_identity_epoch=observed_identity_epoch,
            refusal_reasons=("acceptance_registry_or_artifact_invalid",),
        )
    cutoff = artifact["ledger_cutoff"]
    allow_open = ledger_snapshot.is_governed_open_bracket_extension
    snapshot_reasons = set(ledger_snapshot.refusal_reasons)
    if (
        snapshot_reasons
        and not allow_open
        or allow_open
        and snapshot_reasons
        != {
            "calibration_ledger_bracket_session_open",
            "calibration_ledger_head_mismatch",
        }
        or ledger_snapshot.ledger_schema != LEDGER_SCHEMA
        or ledger_snapshot.head_sequence < cutoff["sequence"]
        or cutoff["sequence"] > len(ledger_snapshot.receipts)
        or cutoff["sequence"] > 0
        and ledger_snapshot.receipts[cutoff["sequence"] - 1].get("receipt_digest")
        != cutoff["head_digest"]
        or ledger_snapshot.head_sequence != len(ledger_snapshot.receipts)
        or ledger_snapshot.head_sequence > 0
        and ledger_snapshot.receipts[-1].get("receipt_digest")
        != ledger_snapshot.head_digest
        or not _prior_set_matches_import_cutoff_prefix(artifact, ledger_snapshot)
    ):
        return _probe_result(
            outcome="authentication_or_epoch_refusal",
            active=active,
            artifact=artifact,
            snapshot=ledger_snapshot,
            observed_identity_epoch=observed_identity_epoch,
            refusal_reasons=("calibration_ledger_prefix_not_authenticated",),
        )
    expected_epoch = artifact["identity_epoch"]
    if (
        not isinstance(observed_identity_epoch, Mapping)
        or set(observed_identity_epoch) != set(ACCEPTANCE_IDENTITY_FIELDS)
        or any(
            observed_identity_epoch.get(field) != expected_epoch.get(field)
            for field in ACCEPTANCE_IDENTITY_FIELDS
        )
    ):
        return _probe_result(
            outcome="authentication_or_epoch_refusal",
            active=active,
            artifact=artifact,
            snapshot=ledger_snapshot,
            observed_identity_epoch=observed_identity_epoch,
            triggers=("identity_field_change",),
            refusal_reasons=("observed_identity_epoch_mismatch",),
        )
    prospective = artifact["prospective_rederivation"]
    if (
        prospective.get("protocol_sha256") != protocol_sha256(PROTOCOL_ID)
        or prospective.get("estimator_code_sha256")
        != _current_estimator_code_sha256()
    ):
        return _probe_result(
            outcome="authentication_or_epoch_refusal",
            active=active,
            artifact=artifact,
            snapshot=ledger_snapshot,
            observed_identity_epoch=observed_identity_epoch,
            triggers=("protocol_or_estimator_byte_change",),
            refusal_reasons=("protocol_or_estimator_bytes_changed",),
        )
    grouped_result = _group_probe_observations(
        _probe_observation_universe(ledger_snapshot)
    )
    if grouped_result is None:
        return _probe_result(
            outcome="authentication_or_epoch_refusal",
            active=active,
            artifact=artifact,
            snapshot=ledger_snapshot,
            observed_identity_epoch=observed_identity_epoch,
            refusal_reasons=("conflicting_content_classification_or_bytes",),
        )
    grouped, noncontent = grouped_result
    prior_ids = _artifact_prior_content_ids(artifact)
    new_ids = sorted(set(grouped) - prior_ids)
    new_observations = [grouped[content_id][0] for content_id in new_ids]
    new_noncontent = [
        observation
        for observation in noncontent
        if observation.sequence > cutoff["sequence"]
    ]
    try:
        _terminal_no_content_rows(
            new_noncontent, ledger_snapshot, ledger_snapshot.head_sequence
        )
    except ValueError as exc:
        return _probe_result(
            outcome="authentication_or_epoch_refusal",
            active=active,
            artifact=artifact,
            snapshot=ledger_snapshot,
            observed_identity_epoch=observed_identity_epoch,
            new_content_ids=new_ids,
            refusal_reasons=(str(exc),),
        )
    if any(
        observation.classification_disposition
        not in {"valid", "systematic-invalid", "ordinary-invalid"}
        for observation in new_observations
    ):
        return _probe_result(
            outcome="authentication_or_epoch_refusal",
            active=active,
            artifact=artifact,
            snapshot=ledger_snapshot,
            observed_identity_epoch=observed_identity_epoch,
            new_content_ids=new_ids,
            refusal_reasons=("unresolved_or_unclassifiable_observation",),
        )
    if verify_custody and any(
        not _observation_custody_authentic(observation)
        for observation in new_observations
    ):
        return _probe_result(
            outcome="authentication_or_epoch_refusal",
            active=active,
            artifact=artifact,
            snapshot=ledger_snapshot,
            observed_identity_epoch=observed_identity_epoch,
            new_content_ids=new_ids,
            refusal_reasons=("new_observation_custody_or_physics_invalid",),
        )
    preflight = _decimal(
        artifact["decimal_derivation"]["ratified_operatives"][
            "preflight_level_screen_s"
        ]
    )
    if preflight is None:
        return _probe_result(
            outcome="authentication_or_epoch_refusal",
            active=active,
            artifact=artifact,
            snapshot=ledger_snapshot,
            observed_identity_epoch=observed_identity_epoch,
            refusal_reasons=("active_preflight_screen_invalid",),
        )
    systematic = [
        observation
        for observation in new_observations
        if dict(observation.identity_epoch) == dict(expected_epoch)
        and (
            observation.classification_disposition == "systematic-invalid"
            or observation.classification_disposition == "valid"
            and (
                (bound := _decimal(observation.exact_bound_lexeme_s)) is None
                or bound > preflight
            )
        )
    ]
    if systematic:
        return _probe_result(
            outcome="systematic_refusal",
            active=active,
            artifact=artifact,
            snapshot=ledger_snapshot,
            observed_identity_epoch=observed_identity_epoch,
            new_content_ids=new_ids,
            triggers=("new_systematic_failure_challenges_preflight_screen",),
            refusal_reasons=(SUCCESSOR_SYSTEMATIC_POLICY,),
        )
    corpus_values = _artifact_corpus_values(artifact)
    if not corpus_values:
        return _probe_result(
            outcome="authentication_or_epoch_refusal",
            active=active,
            artifact=artifact,
            snapshot=ledger_snapshot,
            observed_identity_epoch=observed_identity_epoch,
            refusal_reasons=("active_derivation_corpus_invalid",),
        )
    new_valid_same_epoch = [
        observation
        for observation in new_observations
        if observation.classification_disposition == "valid"
        and dict(observation.identity_epoch) == dict(expected_epoch)
    ]
    triggers: list[str] = []
    if any(
        (bound := _decimal(observation.exact_bound_lexeme_s)) is not None
        and (bound < min(corpus_values) or bound > max(corpus_values))
        for observation in new_valid_same_epoch
    ):
        triggers.append("new_valid_same_identity_capture_expands_observed_range")
    total_valid_same_epoch = sum(
        aliases[0].classification_disposition == "valid"
        and dict(aliases[0].identity_epoch) == dict(expected_epoch)
        for aliases in grouped.values()
    )
    if total_valid_same_epoch >= _artifact_count_boundary(artifact):
        triggers.append("content_distinct_valid_same_epoch_count_boundary")
    outcome = "successor_required" if triggers else "accepted_under_active_artifact"
    return _probe_result(
        outcome=outcome,
        active=active,
        artifact=artifact,
        snapshot=ledger_snapshot,
        observed_identity_epoch=observed_identity_epoch,
        new_content_ids=new_ids,
        triggers=triggers,
    )


_BRACKET_BINDING_KEYS = {
    "schema_version",
    "ledger_schema",
    "session_id",
    "window_id",
    "plan_id",
    "plan_sha256",
    "evidence_root_id",
    "runs_root",
    "capability_receipt_digest",
    "terminal_head",
    "endpoints",
    "binding_digest",
}
_BRACKET_ENDPOINT_KEYS = {
    "attempt_id",
    "receipt_digest",
    "content_digest",
}


def _binding_core(binding: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in binding.items() if key != "binding_digest"}


def build_calibration_bracket_binding(
    ledger_snapshot: CalibrationLedgerSnapshot,
    *,
    session_id: str,
    window_id: str,
    plan_id: str,
    plan_sha256: str,
    evidence_root_id: str,
    runs_root: Path | str,
) -> dict[str, Any]:
    """Bind one frozen window to its exact finalized session endpoints."""

    if not isinstance(ledger_snapshot, CalibrationLedgerSnapshot) or not ledger_snapshot.valid:
        raise ValueError("bracket binding requires a valid pinned ledger snapshot")
    session = ledger_snapshot.bracket_session_by_id.get(session_id)
    expected_identity = (
        window_id,
        plan_id,
        plan_sha256,
        evidence_root_id,
        str(Path(runs_root).absolute()),
    )
    if (
        session is None
        or session.state != "finalized"
        or (
            session.window_id,
            session.plan_id,
            session.plan_sha256,
            session.evidence_root_id,
            session.runs_root,
        )
        != expected_identity
    ):
        raise ValueError("bracket session does not match the frozen window identity")
    pre = session.finalized_slots.get("pre")
    post = session.finalized_slots.get("post")
    if (
        pre is None
        or post is None
        or pre.disposition != "valid"
        or post.disposition != "valid"
        or pre.content_id is None
        or post.content_id is None
        or post.sequence != ledger_snapshot.head_sequence
        or post.receipt_digest != ledger_snapshot.head_digest
    ):
        raise ValueError("bracket session endpoints are not valid at the terminal head")
    binding: dict[str, Any] = {
        "schema_version": BRACKET_BINDING_SCHEMA,
        "ledger_schema": LEDGER_SCHEMA,
        "session_id": session.session_id,
        "window_id": session.window_id,
        "plan_id": session.plan_id,
        "plan_sha256": session.plan_sha256,
        "evidence_root_id": session.evidence_root_id,
        "runs_root": session.runs_root,
        "capability_receipt_digest": session.capability_receipt_digest,
        "terminal_head": {
            "sequence": post.sequence,
            "head_digest": post.receipt_digest,
            "ledger_schema": LEDGER_SCHEMA,
        },
        "endpoints": {
            role: {
                "attempt_id": observation.attempt_id,
                "receipt_digest": observation.receipt_digest,
                "content_digest": observation.content_id,
            }
            for role, observation in (("pre", pre), ("post", post))
        },
    }
    binding["binding_digest"] = _canonical_sha256(binding)
    return binding


def validate_calibration_bracket_binding(
    binding: Mapping[str, Any],
    ledger_snapshot: CalibrationLedgerSnapshot,
    *,
    window_id: str | None = None,
    plan_id: str | None = None,
    plan_sha256: str | None = None,
    evidence_root_id: str | None = None,
    runs_root: Path | str | None = None,
) -> tuple[LedgerObservation, LedgerObservation] | None:
    """Return the exact authenticated pair, or ``None`` on any substitution."""

    if (
        not isinstance(binding, Mapping)
        or set(binding) != _BRACKET_BINDING_KEYS
        or binding.get("schema_version") != BRACKET_BINDING_SCHEMA
        or binding.get("ledger_schema") != LEDGER_SCHEMA
        or not _valid_sha256(binding.get("plan_sha256"))
        or not _valid_sha256(binding.get("capability_receipt_digest"))
        or not _valid_sha256(binding.get("binding_digest"))
        or binding.get("binding_digest") != _canonical_sha256(_binding_core(binding))
        or not isinstance(ledger_snapshot, CalibrationLedgerSnapshot)
        or not ledger_snapshot.valid
    ):
        return None
    if any(
        not isinstance(value, str) or not value
        for value in (window_id, plan_id, plan_sha256, evidence_root_id)
    ) or runs_root is None:
        return None
    expected_runs_root = str(Path(runs_root).absolute())
    for field, expected in (
        ("window_id", window_id),
        ("plan_id", plan_id),
        ("plan_sha256", plan_sha256),
        ("evidence_root_id", evidence_root_id),
        ("runs_root", expected_runs_root),
    ):
        if binding.get(field) != expected:
            return None
    session = ledger_snapshot.bracket_session_by_id.get(str(binding.get("session_id")))
    if (
        session is None
        or session.state != "finalized"
        or binding.get("window_id") != session.window_id
        or binding.get("plan_id") != session.plan_id
        or binding.get("plan_sha256") != session.plan_sha256
        or binding.get("evidence_root_id") != session.evidence_root_id
        or binding.get("runs_root") != session.runs_root
        or binding.get("capability_receipt_digest")
        != session.capability_receipt_digest
    ):
        return None
    terminal = binding.get("terminal_head")
    endpoints = binding.get("endpoints")
    if (
        not isinstance(terminal, Mapping)
        or set(terminal) != {"sequence", "head_digest", "ledger_schema"}
        or terminal.get("ledger_schema") != LEDGER_SCHEMA
        or isinstance(terminal.get("sequence"), bool)
        or not isinstance(terminal.get("sequence"), int)
        or not _valid_sha256(terminal.get("head_digest"))
        or not isinstance(endpoints, Mapping)
        or set(endpoints) != {"pre", "post"}
    ):
        return None
    resolved: list[LedgerObservation] = []
    for role in ("pre", "post"):
        endpoint = endpoints.get(role)
        observation = session.finalized_slots.get(role)
        if (
            not isinstance(endpoint, Mapping)
            or set(endpoint) != _BRACKET_ENDPOINT_KEYS
            or observation is None
            or observation.disposition != "valid"
            or observation.content_id is None
            or endpoint.get("attempt_id") != observation.attempt_id
            or endpoint.get("receipt_digest") != observation.receipt_digest
            or endpoint.get("content_digest") != observation.content_id
        ):
            return None
        resolved.append(observation)
    post = resolved[1]
    if (
        terminal.get("sequence") != post.sequence
        or terminal.get("head_digest") != post.receipt_digest
        or post.sequence > len(ledger_snapshot.receipts)
        or ledger_snapshot.receipts[post.sequence - 1].get("receipt_digest")
        != post.receipt_digest
    ):
        return None
    return resolved[0], resolved[1]


def _binding_evidence_authentic(
    evidence: Mapping[str, Any], bindings: Mapping[str, Any]
) -> bool:
    binding_evidence = evidence.get("binding_evidence")
    binary = (
        binding_evidence.get("powermetrics_binary")
        if isinstance(binding_evidence, Mapping)
        else None
    )
    power_policy = (
        binding_evidence.get("power_policy")
        if isinstance(binding_evidence, Mapping)
        else None
    )
    # Canonical form MUST match the generation (powermetrics_fiducial) and
    # reduce-side consumers byte-for-byte: ensure_ascii=False (delta-review
    # P2 — the ASCII-default form made authentic non-ASCII binding vectors
    # unmatchable as bracket candidates).
    canonical = json.dumps(
        dict(bindings),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return bool(
        isinstance(binding_evidence, Mapping)
        and binding_evidence.get("schema_version")
        == "joulewise.instrument_binding_evidence.v1"
        and binding_evidence.get("binding_vector_sha256")
        == hashlib.sha256(canonical).hexdigest()
        and isinstance(binary, Mapping)
        and binary.get("sha256") == bindings.get("powermetrics_sha256")
        and isinstance(binary.get("path"), str)
        and bool(binary.get("path"))
        and isinstance(power_policy, Mapping)
        and power_policy.get("id") == bindings.get("power_policy")
    )


def load_calibration_candidate(
    directory: Path, *, runs_root: Path
) -> CalibrationCandidate | None:
    """Authenticate one standalone validation directory from primary bytes."""

    root = Path(runs_root).resolve()
    try:
        directory = Path(directory).resolve(strict=True)
        relative = directory.relative_to(root).as_posix()
        manifest_raw = (directory / "manifest.json").read_bytes()
        manifest = json.loads(manifest_raw)
    except (OSError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    artifacts = manifest.get("artifacts") if isinstance(manifest, Mapping) else None
    if (
        not relative
        or not isinstance(artifacts, Mapping)
        or manifest.get("schema_version")
        != "joulewise.instrument_validation_manifest.v1"
    ):
        return None
    members: dict[str, bytes] = {}
    for name, expected in artifacts.items():
        if not isinstance(name, str) or Path(name).is_absolute() or ".." in Path(name).parts:
            return None
        try:
            member = (directory / name).resolve(strict=True)
            member.relative_to(directory)
            raw = member.read_bytes()
        except (OSError, ValueError):
            return None
        if not _valid_sha256(expected) or hashlib.sha256(raw).hexdigest() != expected:
            return None
        members[name] = raw
    try:
        evidence_raw = members["instrument_evidence.json"]
        events_raw = members["events.jsonl"]
        powermetrics_raw = members["raw/powermetrics.plist"]
        evidence = json.loads(evidence_raw)
    except (KeyError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(evidence, Mapping):
        return None
    protocol_id = evidence.get("protocol_id")
    bindings = evidence.get("bindings")
    capture = evidence.get(CAPTURE_TIME_FIELD)
    if (
        protocol_id not in {PROTOCOL_V2_ID, PROTOCOL_ID}
        or evidence.get("schema_version") != "joulewise.instrument_evidence.v1"
        or manifest.get("protocol_id") != protocol_id
        or manifest.get("pulse_count") != protocol_pulse_count(str(protocol_id))
        or not isinstance(bindings, Mapping)
        or any(bindings.get(field) in (None, "") for field in V2_BINDING_FIELDS)
        or not _binding_evidence_authentic(evidence, bindings)
        or bindings.get("pulse_protocol_id") != protocol_id
        or bindings.get("protocol_sha256") != protocol_sha256(str(protocol_id))
        or evidence.get("pulse_count") != protocol_pulse_count(str(protocol_id))
        or evidence.get("anchor_method_version")
        != "powermetrics_native_second_censored_intersection_v1"
        or evidence.get("residual_region_method") != RESIDUAL_REGION_METHOD
        or not isinstance(
            evidence.get("residual_region_coverage_assumption"), str
        )
        or not evidence.get("residual_region_coverage_assumption")
        or evidence.get("residual_region_coverage_resolution_s")
        != REGION_COVERAGE_RESOLUTION_S
        or evidence.get("max_age_s") != MAX_AGE_S
        or isinstance(capture, bool)
        or not isinstance(capture, int | float)
        or not math.isfinite(float(capture))
        or float(capture) < 0.0
    ):
        return None
    artifact_hashes = evidence.get("artifact_sha256")
    if (
        not isinstance(artifact_hashes, Mapping)
        or artifact_hashes.get("events.jsonl")
        != hashlib.sha256(events_raw).hexdigest()
        or artifact_hashes.get("raw/powermetrics.plist")
        != hashlib.sha256(powermetrics_raw).hexdigest()
    ):
        return None
    try:
        authenticated_capture = capture_wall_time_from_events(events_raw)
        effective_bound = verify_stored_evidence_physics(
            evidence, powermetrics_raw, events_raw
        )
    except (KeyError, TypeError, ValueError):
        return None
    if abs(float(capture) - authenticated_capture) > 1.0:
        return None
    try:
        decimal_evidence = json.loads(
            evidence_raw,
            parse_float=str,
            parse_int=str,
        )
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    stored_lexeme = (
        decimal_evidence.get("b_fiducial_s")
        if isinstance(decimal_evidence, Mapping)
        else None
    )
    stored_decimal = _decimal(stored_lexeme)
    if (
        stored_decimal is not None
        and float(stored_decimal) == float(effective_bound)
    ):
        effective_bound_lexeme = stored_lexeme
    else:
        # A physical re-fit can widen beyond the stored scalar. Its returned
        # representation becomes the re-derivation source lexeme; no later
        # acceptance comparison converts that value through binary64 again.
        effective_bound_lexeme = str(float(effective_bound))
    return CalibrationCandidate(
        relative_path=relative,
        manifest_sha256=hashlib.sha256(manifest_raw).hexdigest(),
        evidence_sha256=hashlib.sha256(evidence_raw).hexdigest(),
        protocol_id=str(protocol_id),
        capture_wall_time_s=float(capture),
        b_fiducial_s=effective_bound_lexeme,
        bindings=dict(bindings),
    )


def _candidate_from_observation(
    observation: LedgerObservation,
) -> CalibrationCandidate | None:
    """Authenticate one valid ledger observation from its custody locator."""

    if observation.disposition != "valid" or observation.content_id is None:
        return None
    custody = Path(observation.custody_locator)
    candidate = load_calibration_candidate(
        custody,
        runs_root=custody.parent.parent,
    )
    if candidate is None:
        return None
    bound = _candidate_decimal(candidate)
    receipt_bound = _decimal(observation.exact_bound_lexeme_s)
    try:
        receipt_capture = float(observation.capture_wall_time_s)
    except (TypeError, ValueError):
        return None
    if (
        candidate.manifest_sha256
        != observation.artifact_sha256.get("manifest.json")
        or candidate.evidence_sha256
        != observation.artifact_sha256.get("instrument_evidence.json")
        or content_id_from_artifact_hashes(observation.artifact_sha256)
        != observation.content_id
        or bound is None
        or receipt_bound is None
        or bound != receipt_bound
        or candidate.capture_wall_time_s != receipt_capture
        or any(
            candidate.bindings.get(field) != observation.t1_bindings.get(field)
            for field in V2_BINDING_FIELDS
        )
        or any(
            candidate.bindings.get(field) != observation.identity_epoch.get(field)
            for field in ACCEPTANCE_IDENTITY_FIELDS
        )
    ):
        return None
    return replace(
        candidate,
        relative_path=observation.custody_locator,
        attempt_id=observation.attempt_id,
        content_id=observation.content_id,
        ledger_receipt_digest=observation.receipt_digest,
        bracket_session_id=observation.bracket_session_id,
        bracket_slot=observation.bracket_slot,
        bracket_window_id=observation.bracket_window_id,
        bracket_plan_id=observation.bracket_plan_id,
        bracket_plan_sha256=observation.bracket_plan_sha256,
        bracket_evidence_root_id=observation.bracket_evidence_root_id,
        bracket_runs_root=observation.bracket_runs_root,
    )


def discover_calibration_candidates(
    ledger_snapshot: CalibrationLedgerSnapshot,
) -> tuple[CalibrationCandidate, ...]:
    """Enumerate valid endpoints from the sole ledger authority.

    The mechanism closes workflow omission, unregistered evidence, and
    rollback/stale-head consumption; it does not defend against a malicious
    trusted writer or a rewrite of both Git and full ledger history.
    """

    if (
        not isinstance(ledger_snapshot, CalibrationLedgerSnapshot)
        or not ledger_snapshot.valid
        and not ledger_snapshot.is_governed_open_bracket_extension
    ):
        return ()
    finalized_session_ids = {
        session.session_id
        for session in ledger_snapshot.bracket_sessions
        if session.state == "finalized"
    }
    candidates: list[CalibrationCandidate] = []
    for observation in ledger_snapshot.observations:
        if (
            observation.disposition != "valid"
            or observation.is_historical_import
            or observation.bracket_session_id is not None
            and observation.bracket_session_id not in finalized_session_ids
        ):
            continue
        candidate = _candidate_from_observation(observation)
        if candidate is None:
            return ()
        candidates.append(candidate)
    return tuple(candidates)


def _governed_unused_slot_rows(
    ledger_snapshot: CalibrationLedgerSnapshot,
    cutoff_sequence: int,
) -> list[dict[str, Any]] | None:
    receipts_by_session: dict[str, list[Mapping[str, Any]]] = {}
    for receipt in ledger_snapshot.receipts[:cutoff_sequence]:
        session_id = receipt.get("session_id")
        if isinstance(session_id, str):
            receipts_by_session.setdefault(session_id, []).append(receipt)
    rows: list[dict[str, Any]] = []
    for session in ledger_snapshot.bracket_sessions:
        if session.state != "aborted" or session.capability_sequence > cutoff_sequence:
            continue
        receipts = receipts_by_session.get(session.session_id, [])
        opened = [row for row in receipts if row.get("event") == "bracket-session-open"]
        aborted = [row for row in receipts if row.get("event") == "bracket-session-abort"]
        if len(opened) != 1 or len(aborted) != 1:
            return None
        unused_slots = aborted[0].get("unused_slots")
        reservations = opened[0].get("slots")
        if (
            not isinstance(unused_slots, Sequence)
            or isinstance(unused_slots, (str, bytes))
            or not isinstance(reservations, Mapping)
        ):
            return None
        for slot in unused_slots:
            reservation = reservations.get(slot)
            if (
                not isinstance(slot, str)
                or not isinstance(reservation, Mapping)
                or not isinstance(reservation.get("attempt_id"), str)
                or not reservation["attempt_id"]
                or not isinstance(reservation.get("custody_locator"), str)
                or not reservation["custody_locator"]
                or isinstance(aborted[0].get("sequence"), bool)
                or not isinstance(aborted[0].get("sequence"), int)
                or not _valid_sha256(aborted[0].get("receipt_digest"))
            ):
                return None
            rows.append(
                {
                    "attempt_id": reservation["attempt_id"],
                    "closure_sequence": aborted[0]["sequence"],
                    "receipt_digest": aborted[0]["receipt_digest"],
                    "disposition": "governed-unused-slot",
                    "custody_locator": reservation["custody_locator"],
                }
            )
    return sorted(rows, key=lambda row: (row["closure_sequence"], row["attempt_id"]))


def _governed_noncontent_rows(
    noncontent: Sequence[LedgerObservation],
    ledger_snapshot: CalibrationLedgerSnapshot,
    cutoff_sequence: int,
) -> list[dict[str, Any]]:
    terminal_rows = _terminal_no_content_rows(
        noncontent, ledger_snapshot, cutoff_sequence
    )
    unused_rows = _governed_unused_slot_rows(ledger_snapshot, cutoff_sequence)
    if unused_rows is None:
        raise ValueError("successor_governed_unused_slot_closure_malformed")
    rows = [*terminal_rows, *unused_rows]
    keys = [
        (row["closure_sequence"], row["attempt_id"], row["receipt_digest"])
        for row in rows
    ]
    if len(keys) != len(set(keys)):
        raise ValueError("successor_noncontent_closure_conflict")
    return sorted(rows, key=lambda row: (row["closure_sequence"], row["attempt_id"]))


def _prior_set_matches_import_cutoff_prefix(
    artifact: Mapping[str, Any],
    ledger_snapshot: CalibrationLedgerSnapshot,
) -> bool:
    """Bind issuance prior-set data to the import-marked cutoff prefix."""

    cutoff = artifact["ledger_cutoff"]
    prefix = tuple(
        observation
        for observation in ledger_snapshot.observations
        if observation.sequence <= cutoff["sequence"]
    )
    if artifact.get("schema_version") == ACCEPTANCE_SUCCESSOR_SCHEMA:
        grouped_result = _group_probe_observations(prefix)
        if grouped_result is None:
            return False
        grouped, noncontent = grouped_result
        catalog = artifact["prior_observation_set"]["epoch_catalog"]
        rows = artifact["prior_observation_set"]["observations"]
        expected_ids = [row["content_id"] for row in rows]
        if expected_ids != sorted(grouped):
            return False
        for row in rows:
            aliases = grouped[row["content_id"]]
            epoch_ids = [
                epoch_id
                for epoch_id, epoch in catalog.items()
                if dict(epoch) == dict(aliases[0].identity_epoch)
            ]
            expected_attempts = [
                {
                    "attempt_id": alias.attempt_id,
                    "finalization_sequence": alias.sequence,
                    "receipt_digest": alias.receipt_digest,
                    "observation_kind": alias.observation_kind,
                    "custody_locator": alias.custody_locator,
                    "exact_bound_lexeme_s": alias.exact_bound_lexeme_s,
                    "manifest_sha256": alias.artifact_sha256.get("manifest.json"),
                    "instrument_evidence_sha256": alias.artifact_sha256.get(
                        "instrument_evidence.json"
                    ),
                }
                for alias in aliases
            ]
            if (
                len(epoch_ids) != 1
                or row["epoch_id"] != epoch_ids[0]
                or row["disposition"]
                != aliases[0].classification_disposition
                or row["representative_attempt_id"] != aliases[0].attempt_id
                or row["attempts"] != expected_attempts
            ):
                return False
        try:
            expected_noncontent = _governed_noncontent_rows(
                noncontent, ledger_snapshot, cutoff["sequence"]
            )
        except ValueError:
            return False
        return (
            artifact["prior_observation_set"]["noncontent_attempts"]
            == expected_noncontent
        )
    # The checked-in schema fixture predates issuance and deliberately has a
    # genesis cutoff. Production issuance, or any fixture containing imported
    # prefix rows, must satisfy the exact marker-bound comparison below.
    if not prefix and artifact.get("artifact_role") == "schema_fixture_unissued":
        return True
    if any(not observation.is_historical_import for observation in prefix):
        return False
    catalog = artifact["prior_observation_set"]["epoch_catalog"]
    expected = {
        (
            row["attempt_id"],
            row["content_id"],
            row["disposition"],
            row["epoch_id"],
        )
        for row in artifact["prior_observation_set"]["observations"]
    }
    observed: set[tuple[str, str, str, str]] = set()
    for observation in prefix:
        epoch_ids = [
            epoch_id
            for epoch_id, epoch in catalog.items()
            if dict(epoch) == dict(observation.identity_epoch)
        ]
        if observation.content_id is None or len(epoch_ids) != 1:
            return False
        observed.add(
            (
                observation.attempt_id,
                observation.content_id,
                observation.classification_disposition,
                epoch_ids[0],
            )
        )
    return observed == expected and len(observed) == len(prefix)


def evaluate_calibration_bracket(
    candidates: Sequence[CalibrationCandidate],
    *,
    window_start_s: float,
    window_end_s: float,
    bindings: Mapping[str, Any],
    policy: CalibrationBracketingPolicy,
    acceptance_bound: Mapping[str, Any] | None = None,
    ledger_snapshot: CalibrationLedgerSnapshot | None = None,
    bracket_binding: Mapping[str, Any] | None = None,
    bracket_window_id: str | None = None,
    bracket_plan_id: str | None = None,
    bracket_plan_sha256: str | None = None,
    bracket_evidence_root_id: str | None = None,
    bracket_runs_root: Path | str | None = None,
    _allow_unissued_fixture: bool = False,
) -> tuple[dict[str, Any], tuple[str, ...]]:
    """Select a causal bracket and apply the provenance-bound D-079 budget."""

    result: dict[str, Any] = {
        "schema_version": BRACKET_SCHEMA,
        "policy": {
            "require_bracket": policy.require_bracket,
            "calibration_bracket_max_drift_s": (
                policy.calibration_bracket_max_drift_s
            ),
        },
        "window_start_s": window_start_s,
        "window_end_s": window_end_s,
        "pre": None,
        "post": None,
        "endpoint_max_b_fiducial_s": None,
        "calibration_drift_allowance_s": None,
        "b_fiducial_s": None,
        "drift_s": None,
        "acceptance": None,
        "bracket_binding": None,
        "status": "not_required" if not policy.require_bracket else "failed",
    }
    if not policy.require_bracket:
        return result, ()
    if (
        not math.isfinite(window_start_s)
        or not math.isfinite(window_end_s)
        or window_start_s >= window_end_s
    ):
        return result, ("instrument_calibration_bracket_missing",)

    using_default_bound = acceptance_bound is None
    artifact = (
        load_calibration_acceptance_bound()
        if using_default_bound
        else _authenticated_explicit_acceptance_bound(acceptance_bound)
    )
    if artifact is None:
        result["acceptance"] = {
            "schema_version": ACCEPTANCE_EVALUATION_SCHEMA,
            "artifact": None,
            "freshness": {
                "status": "stale",
                "reason": "acceptance_artifact_missing_or_invalid",
            },
        }
        return result, ("calibration_acceptance_bound_stale",)
    artifact_role = artifact["artifact_role"]
    artifact_sha256 = _acceptance_artifact_sha256(artifact)
    if artifact_role == "schema_fixture_unissued" and not _allow_unissued_fixture:
        result["acceptance"] = {
            "schema_version": ACCEPTANCE_EVALUATION_SCHEMA,
            "artifact": {
                "acceptance_id": artifact["acceptance_id"],
                "artifact_sha256": artifact_sha256,
                "authentication": "checked_in_genesis_fixture_byte_sha256_pin",
                "artifact_role": artifact_role,
                "claim_eligible": False,
            },
            "freshness": {
                "status": "stale",
                "reason": "acceptance_artifact_unissued_fixture",
            },
        }
        return result, ("calibration_acceptance_bound_stale",)
    cutoff = artifact["ledger_cutoff"]
    result["acceptance"] = {
        "schema_version": ACCEPTANCE_EVALUATION_SCHEMA,
        "artifact": {
            "acceptance_id": artifact["acceptance_id"],
            "artifact_sha256": artifact_sha256,
            "authentication": (
                "checked_in_issued_artifact_byte_sha256_pin"
                if artifact_role == "issued"
                else "checked_in_genesis_fixture_byte_sha256_pin"
            ),
            "artifact_role": artifact_role,
            "claim_eligible": False,
        },
        "freshness": {
            "status": "stale",
            "reason": "acceptance_artifact_ledger_authentication_pending",
        },
    }
    if ledger_snapshot is None:
        return result, ("calibration_ledger_snapshot_required",)
    if ledger_snapshot.refusal_reasons:
        return result, tuple(ledger_snapshot.refusal_reasons)
    if (
        ledger_snapshot.baseline_sequence != cutoff["sequence"]
        or ledger_snapshot.baseline_digest != cutoff["head_digest"]
        or ledger_snapshot.ledger_schema != cutoff["ledger_schema"]
        or artifact_role == "issued"
        and (
            ledger_snapshot.head_sequence <= 0
            or ledger_snapshot.head_digest == "0" * 64
        )
    ):
        return result, ("calibration_ledger_baseline_missing",)
    if not _prior_set_matches_import_cutoff_prefix(artifact, ledger_snapshot):
        return result, ("calibration_ledger_baseline_missing",)
    identity_epoch = artifact["identity_epoch"]
    prospective = artifact["prospective_rederivation"]
    result["policy"].update(
        {
            "calibration_bracket_max_drift_s_role": (
                "legacy_obsolete_not_an_acceptance_comparator"
            ),
            "acceptance_bound_id": artifact["acceptance_id"],
            "operative_bracket_screen_decimal_s": (
                artifact["decimal_derivation"]["ratified_operatives"][
                    "bracket_screen_s"
                ]
            ),
        }
    )
    observed_identity = {
        field: bindings.get(field) for field in ACCEPTANCE_IDENTITY_FIELDS
    }
    stale_fields = [
        field
        for field in ACCEPTANCE_IDENTITY_FIELDS
        if observed_identity.get(field) != identity_epoch.get(field)
    ]
    freshness_status = "stale" if stale_fields else "fresh"
    result["acceptance"] = {
        "schema_version": ACCEPTANCE_EVALUATION_SCHEMA,
        "artifact": {
            "acceptance_id": artifact["acceptance_id"],
            "artifact_sha256": artifact_sha256,
            "authentication": (
                "checked_in_issued_artifact_byte_sha256_pin"
                if artifact_role == "issued"
                else "checked_in_genesis_fixture_byte_sha256_pin"
            ),
            "artifact_role": artifact_role,
            "claim_eligible": artifact_role == "issued",
            "derivation_sha256": artifact["derivation_sha256"],
        },
        "freshness": {
            "status": freshness_status,
            "basis": "exact_identity_epoch",
            "expected_identity_epoch": dict(identity_epoch),
            "observed_identity_epoch": observed_identity,
            "trigger_guard_protocol_sha256": prospective["protocol_sha256"],
            "trigger_guard_estimator_code_sha256": dict(
                prospective["estimator_code_sha256"]
            ),
            "stale_fields": stale_fields,
            "calendar_expiry": None,
        },
        "prospective_rederivation": {
            "observation_rule": prospective["trigger_observation_rule"],
            "candidate_set_boundary": (
                "authenticated_calibration_ledger_snapshot_only"
            ),
            "global_runs_root_scan": False,
            "mandatory_triggers": list(prospective["triggers"]),
            "observed_triggers": [],
        },
        "numeric_semantics": {
            "comparisons": "decimal",
            "reducer_boundary": "binary64_recorded_below",
        },
        "ledger_snapshot": {
            "ledger_schema": ledger_snapshot.ledger_schema,
            "sequence": ledger_snapshot.head_sequence,
            "head_digest": ledger_snapshot.head_digest,
            "baseline_sequence": ledger_snapshot.baseline_sequence,
            "baseline_digest": ledger_snapshot.baseline_digest,
            "load_count": 1,
        },
        "preflight": None,
        "drift": None,
    }
    if stale_fields:
        return result, ("calibration_acceptance_bound_stale",)
    observations_by_attempt = ledger_snapshot.observation_by_attempt
    finalized_session_ids = {
        session.session_id
        for session in ledger_snapshot.bracket_sessions
        if session.state == "finalized"
    }
    registered_valid = {
        (
            observation.attempt_id,
            observation.content_id,
            observation.receipt_digest,
        )
        for observation in ledger_snapshot.observations
        if observation.disposition == "valid"
        and not observation.is_historical_import
        and (
            observation.bracket_session_id is None
            or observation.bracket_session_id in finalized_session_ids
        )
    }
    supplied_valid = {
        (
            candidate.attempt_id,
            candidate.content_id,
            candidate.ledger_receipt_digest,
        )
        for candidate in candidates
    }
    # Even the low-level evaluator requires the complete ledger enumeration.
    # This prevents a caller from narrowing the registered universe to a
    # favorable subset while still passing per-candidate membership checks.
    if supplied_valid != registered_valid or len(candidates) != len(supplied_valid):
        return result, ("calibration_ledger_off_ledger_artifact",)
    for candidate in candidates:
        observation = (
            observations_by_attempt.get(candidate.attempt_id)
            if isinstance(candidate.attempt_id, str)
            else None
        )
        if (
            observation is None
            or observation.disposition != "valid"
            or candidate.content_id != observation.content_id
            or candidate.ledger_receipt_digest != observation.receipt_digest
            or candidate.manifest_sha256
            != observation.artifact_sha256.get("manifest.json")
            or candidate.evidence_sha256
            != observation.artifact_sha256.get("instrument_evidence.json")
            or candidate.bracket_session_id != observation.bracket_session_id
            or candidate.bracket_slot != observation.bracket_slot
            or candidate.bracket_window_id != observation.bracket_window_id
            or candidate.bracket_plan_id != observation.bracket_plan_id
            or candidate.bracket_plan_sha256
            != observation.bracket_plan_sha256
            or candidate.bracket_evidence_root_id
            != observation.bracket_evidence_root_id
            or candidate.bracket_runs_root != observation.bracket_runs_root
        ):
            return result, ("calibration_ledger_off_ledger_artifact",)
    has_session_candidates = any(
        candidate.bracket_session_id is not None for candidate in candidates
    )
    bound_observations: tuple[LedgerObservation, LedgerObservation] | None = None
    if has_session_candidates:
        if (
            bracket_binding is None
            or not all(
                isinstance(value, str) and bool(value)
                for value in (
                    bracket_window_id,
                    bracket_plan_id,
                    bracket_plan_sha256,
                    bracket_evidence_root_id,
                )
            )
            or bracket_runs_root is None
        ):
            return result, ("calibration_bracket_binding_missing",)
        expected_runs_root = str(Path(bracket_runs_root).absolute())
        bound_observations = validate_calibration_bracket_binding(
            bracket_binding,
            ledger_snapshot,
            window_id=bracket_window_id,
            plan_id=bracket_plan_id,
            plan_sha256=bracket_plan_sha256,
            evidence_root_id=bracket_evidence_root_id,
            runs_root=expected_runs_root,
        )
        if bound_observations is None:
            return result, ("calibration_bracket_binding_invalid",)
        result["bracket_binding"] = {
            "schema_version": BRACKET_BINDING_SCHEMA,
            "binding_digest": bracket_binding["binding_digest"],
            "session_id": bracket_binding["session_id"],
            "window_id": bracket_binding["window_id"],
            "plan_id": bracket_binding["plan_id"],
            "plan_sha256": bracket_binding["plan_sha256"],
            "evidence_root_id": bracket_binding["evidence_root_id"],
            "runs_root": bracket_binding["runs_root"],
        }
        bound_session_id = str(bracket_binding["session_id"])
        for candidate in candidates:
            if candidate.bracket_session_id != bound_session_id:
                continue
            if (
                candidate.bracket_window_id,
                candidate.bracket_plan_id,
                candidate.bracket_plan_sha256,
                candidate.bracket_evidence_root_id,
                candidate.bracket_runs_root,
            ) != (
                bracket_window_id,
                bracket_plan_id,
                bracket_plan_sha256,
                bracket_evidence_root_id,
                expected_runs_root,
            ):
                return result, ("calibration_bracket_binding_invalid",)
    # v2 remains an authenticated validation/reduction artifact, but only the
    # 59-pulse v3 protocol carries the governed 95/95 claim calibration.
    matching = [
        candidate
        for candidate in candidates
        if candidate.protocol_id == PROTOCOL_ID
        and all(
            candidate.bindings.get(field) == bindings.get(field)
            for field in V2_BINDING_FIELDS
        )
    ]
    matching_decimals: dict[int, Decimal] = {}
    for candidate in matching:
        candidate_decimal = _candidate_decimal(candidate)
        if candidate_decimal is None or candidate_decimal < 0:
            return result, ("instrument_calibration_invalid",)
        matching_decimals[id(candidate)] = candidate_decimal
    corpus_members = artifact["derivation_corpus"]["members"]
    observed_triggers = result["acceptance"]["prospective_rederivation"][
        "observed_triggers"
    ]
    if (
        protocol_sha256(PROTOCOL_ID) != prospective.get("protocol_sha256")
        or _current_estimator_code_sha256()
        != dict(prospective["estimator_code_sha256"])
    ):
        observed_triggers.append("protocol_or_estimator_byte_change")
    prior_ids = {
        observation["content_id"]
        for observation in artifact["prior_observation_set"]["observations"]
    }
    distinct_observations = {
        observation.content_id: observation
        for observation in ledger_snapshot.observations
        if observation.content_id is not None
    }
    distinct_live_observations = {
        content_id: observation
        for content_id, observation in distinct_observations.items()
        if not observation.is_historical_import
    }
    new_observations = [
        observation
        for content_id, observation in sorted(distinct_live_observations.items())
        if content_id not in prior_ids
    ]
    new_observations.extend(
        sorted(
            (
                observation
                for observation in ledger_snapshot.post_cutoff_live_observations(
                    cutoff["sequence"]
                )
                if observation.content_id is None
            ),
            key=lambda observation: (observation.sequence, observation.attempt_id),
        )
    )
    if any(
        observation.classification_disposition
        not in {"valid", "systematic-invalid", "ordinary-invalid"}
        for observation in new_observations
    ):
        return result, ("calibration_observation_unclassifiable",)
    valid_same_epoch = [
        observation
        for observation in distinct_observations.values()
        if observation.disposition == "valid"
        and dict(observation.identity_epoch) == dict(identity_epoch)
    ]
    if len(valid_same_epoch) >= _artifact_count_boundary(artifact):
        observed_triggers.append(
            "content_distinct_valid_same_epoch_count_boundary"
            if artifact.get("schema_version") == ACCEPTANCE_SUCCESSOR_SCHEMA
            else "corpus_doubles_from_19_to_38"
        )
    corpus_values = [
        Decimal(member["b_fiducial_s"]) for member in corpus_members
    ]
    new_valid_values = [
        value
        for observation in new_observations
        if observation.disposition == "valid"
        and dict(observation.identity_epoch) == dict(identity_epoch)
        and (value := _decimal(observation.exact_bound_lexeme_s)) is not None
    ]
    if any(value < min(corpus_values) or value > max(corpus_values) for value in new_valid_values):
        observed_triggers.append(
            "new_valid_same_identity_capture_expands_observed_range"
        )
    if any(
        observation.disposition == "systematic-invalid"
        and dict(observation.identity_epoch) == dict(identity_epoch)
        for observation in new_observations
    ):
        observed_triggers.append(
            "new_systematic_failure_challenges_preflight_screen"
        )
    # R2 trigger evaluation ranges over the observation universe, not the
    # narrower bracket-candidate set.  A governed aborted PRE can therefore
    # stale the acceptance artifact even when no eligible endpoint pair is
    # available for this window.
    observation_stale_triggers = [
        trigger
        for trigger in observed_triggers
        if trigger == "new_systematic_failure_challenges_preflight_screen"
    ]
    if observation_stale_triggers:
        result["acceptance"]["freshness"].update(
            {
                "status": "stale",
                "reason": "prospective_rederivation_required",
                "stale_triggers": observation_stale_triggers,
            }
        )
        return result, ("calibration_acceptance_bound_stale",)
    causal_pre = [
        candidate for candidate in matching if candidate.capture_wall_time_s <= window_start_s
    ]
    causal_post = [
        candidate for candidate in matching if candidate.capture_wall_time_s >= window_end_s
    ]
    fresh_pre = [
        candidate
        for candidate in causal_pre
        if window_end_s <= candidate.capture_wall_time_s + MAX_AGE_S
    ]
    fresh_post = [
        candidate
        for candidate in causal_post
        if candidate.capture_wall_time_s - window_start_s <= MAX_AGE_S
    ]
    if not fresh_pre or not fresh_post:
        reason = (
            "instrument_calibration_stale"
            if (causal_pre and not fresh_pre) or (causal_post and not fresh_post)
            else "instrument_calibration_bracket_missing"
        )
        return result, (reason,)
    if bound_observations is None:
        pre = max(fresh_pre, key=lambda candidate: candidate.capture_wall_time_s)
        post = min(fresh_post, key=lambda candidate: candidate.capture_wall_time_s)
    else:
        candidate_by_receipt = {
            candidate.ledger_receipt_digest: candidate for candidate in matching
        }
        pre = candidate_by_receipt.get(bound_observations[0].receipt_digest)
        post = candidate_by_receipt.get(bound_observations[1].receipt_digest)
        if pre not in fresh_pre or post not in fresh_post:
            return result, ("calibration_bracket_binding_invalid",)
    pre_decimal = matching_decimals[id(pre)]
    post_decimal = matching_decimals[id(post)]
    if (
        not pre_decimal.is_finite()
        or not post_decimal.is_finite()
        or pre_decimal < 0
        or post_decimal < 0
    ):
        return result, ("instrument_calibration_invalid",)
    if isinstance(pre.b_fiducial_s, float) and isinstance(
        post.b_fiducial_s, float
    ):
        # Old synthetic probes supplied only binary64 endpoints. Preserve their
        # source arithmetic without applying Decimal after a second rounding;
        # authenticated production candidates always use the exact branch.
        drift_decimal = Decimal(
            str(abs(pre.b_fiducial_s - post.b_fiducial_s))
        )
    else:
        drift_decimal = abs(pre_decimal - post_decimal)
    endpoint_max_decimal = max(pre_decimal, post_decimal)
    operatives = artifact["decimal_derivation"]["ratified_operatives"]
    screen = Decimal(operatives["bracket_screen_s"])
    preflight_screen = Decimal(operatives["preflight_level_screen_s"])
    maximum_drift = Decimal(operatives["maximum_budgetable_drift_s"])
    maximum_excess = Decimal(operatives["max_budgetable_excess_s"])
    result.update(
        {
            "pre": pre.descriptor(),
            "post": post.descriptor(),
            "endpoint_max_b_fiducial_s": float(endpoint_max_decimal),
            "drift_s": float(drift_decimal),
        }
    )
    result["acceptance"]["numeric_semantics"].update(
        {
            "pre_b_fiducial_binary64_s": float(pre_decimal),
            "pre_b_fiducial_decimal_s": str(pre_decimal),
            "post_b_fiducial_binary64_s": float(post_decimal),
            "post_b_fiducial_decimal_s": str(post_decimal),
            "observed_drift_decimal_s": str(drift_decimal),
        }
    )
    preflight_status = "passed" if pre_decimal <= preflight_screen else "failed"
    result["acceptance"]["preflight"] = {
        "status": preflight_status,
        "observed_pre_b_fiducial_s": str(pre_decimal),
        "level_screen_s": str(preflight_screen),
        "failure_class": (
            None if preflight_status == "passed" else "systematic_not_budgetable"
        ),
    }
    if pre_decimal > preflight_screen:
        observed_triggers.append(
            "new_systematic_failure_challenges_preflight_screen"
        )
        result["acceptance"]["drift"] = {
            "status": "not_evaluated_systematic_preflight_failure",
            "observed_s": str(drift_decimal),
            "screen_s": str(screen),
            "maximum_budgetable_drift_s": str(maximum_drift),
        }
        return result, ("instrument_calibration_mismatch",)

    stale_triggers = [
        trigger
        for trigger in observed_triggers
        if trigger
        in {
            "protocol_or_estimator_byte_change",
            "corpus_doubles_from_19_to_38",
            "content_distinct_valid_same_epoch_count_boundary",
            "new_valid_same_identity_capture_expands_observed_range",
            "new_systematic_failure_challenges_preflight_screen",
        }
    ]
    if stale_triggers:
        result["acceptance"]["freshness"].update(
            {
                "status": "stale",
                "reason": "prospective_rederivation_required",
                "stale_triggers": stale_triggers,
            }
        )
        return result, ("calibration_acceptance_bound_stale",)

    excess = max(drift_decimal - screen, Decimal(0))
    drift_status = (
        "budget_exceeded"
        if drift_decimal > maximum_drift
        else "passed_budgeted"
        if drift_decimal > screen
        else "passed_screen"
    )
    result["acceptance"]["drift"] = {
        "status": drift_status,
        "observed_s": str(drift_decimal),
        "screen_s": str(screen),
        "excess_s": str(excess),
        "max_budgetable_excess_s": str(maximum_excess),
        "maximum_budgetable_drift_s": str(maximum_drift),
    }
    if drift_decimal > maximum_drift:
        return result, ("instrument_calibration_mismatch",)

    # COLD-GATE-Q13: current-answer allowance generalization; the re-convened
    # packet can flip this isolated site without touching downstream shape.
    allowance = max(drift_decimal, screen)
    operative_bound = endpoint_max_decimal + allowance
    result.update(
        {
            "calibration_drift_allowance_s": float(allowance),
            "b_fiducial_s": float(operative_bound),
        }
    )
    result["acceptance"]["allowance"] = {
        "rule": "max(observed_drift_s,bracket_screen_s)",
        "value_s": str(allowance),
        "embedding_count": 1,
        "embedded_in": "b_fiducial_s",
        "endpoint_max_b_fiducial_s": str(endpoint_max_decimal),
        "operative_b_fiducial_decimal_s": str(operative_bound),
        "operative_b_fiducial_binary64_s": float(operative_bound),
    }
    result["status"] = "passed"
    return result, ()


def calibration_bracket_for_bundles(
    runs_root: Path,
    bundle_paths: Sequence[Path],
    policy: CalibrationBracketingPolicy,
    *,
    ledger_snapshot: CalibrationLedgerSnapshot | None = None,
    bracket_binding: Mapping[str, Any] | None = None,
    bracket_window_id: str | None = None,
    bracket_plan_id: str | None = None,
    bracket_plan_sha256: str | None = None,
    bracket_evidence_root_id: str | None = None,
    _allow_unissued_fixture: bool = False,
) -> tuple[dict[str, Any], tuple[str, ...]]:
    """Use the runs root only for the evaluated window's T1/endpoints."""

    if not bundle_paths:
        empty, _ = evaluate_calibration_bracket(
            (),
            window_start_s=0.0,
            window_end_s=0.0,
            bindings={},
            policy=policy,
            ledger_snapshot=ledger_snapshot,
            _allow_unissued_fixture=_allow_unissued_fixture,
        )
        return empty, ("instrument_calibration_bracket_missing",)
    windows = []
    bindings: list[Mapping[str, Any]] = []
    try:
        for path in bundle_paths:
            reader = BundleReader(path)
            window = reader.measured_window()
            metadata = reader.metadata()
            calibration = metadata.get("instrument_calibration")
            binding = calibration.get("bindings") if isinstance(calibration, Mapping) else None
            if window is None or not isinstance(binding, Mapping):
                raise ValueError("member omits calibration binding evidence")
            windows.append(window)
            bindings.append(binding)
    except (BundleReadError, OSError, TypeError, ValueError):
        empty, _ = evaluate_calibration_bracket(
            (),
            window_start_s=0.0,
            window_end_s=0.0,
            bindings={},
            policy=policy,
            ledger_snapshot=ledger_snapshot,
            _allow_unissued_fixture=_allow_unissued_fixture,
        )
        return empty, ("instrument_calibration_bracket_missing",)
    expected = bindings[0]
    if any(
        any(binding.get(field) != expected.get(field) for field in V2_BINDING_FIELDS)
        for binding in bindings[1:]
    ):
        empty, _ = evaluate_calibration_bracket(
            (),
            window_start_s=min(window.start_s for window in windows),
            window_end_s=max(window.end_s for window in windows),
            bindings=expected,
            policy=policy,
            ledger_snapshot=ledger_snapshot,
            _allow_unissued_fixture=_allow_unissued_fixture,
        )
        return empty, ("instrument_calibration_mismatch",)
    if ledger_snapshot is None:
        candidates: tuple[CalibrationCandidate, ...] = ()
    else:
        candidates = discover_calibration_candidates(ledger_snapshot)
        registered_valid = sum(
            observation.disposition == "valid"
            and not observation.is_historical_import
            and (
                observation.bracket_session_id is None
                or any(
                    session.session_id == observation.bracket_session_id
                    and session.state == "finalized"
                    for session in ledger_snapshot.bracket_sessions
                )
            )
            for observation in ledger_snapshot.observations
        )
        if ledger_snapshot.valid and len(candidates) != registered_valid:
            empty, _ = evaluate_calibration_bracket(
                (),
                window_start_s=min(window.start_s for window in windows),
                window_end_s=max(window.end_s for window in windows),
                bindings=expected,
                policy=policy,
                ledger_snapshot=ledger_snapshot,
                _allow_unissued_fixture=_allow_unissued_fixture,
            )
            return empty, ("calibration_ledger_custody_invalid",)
    return evaluate_calibration_bracket(
        candidates,
        window_start_s=min(window.start_s for window in windows),
        window_end_s=max(window.end_s for window in windows),
        bindings=expected,
        policy=policy,
        ledger_snapshot=ledger_snapshot,
        bracket_binding=bracket_binding,
        bracket_window_id=bracket_window_id,
        bracket_plan_id=bracket_plan_id,
        bracket_plan_sha256=bracket_plan_sha256,
        bracket_evidence_root_id=bracket_evidence_root_id,
        bracket_runs_root=runs_root,
        _allow_unissued_fixture=_allow_unissued_fixture,
    )


__all__ = [
    "ACCEPTANCE_BOUND_SCHEMA",
    "ACCEPTANCE_EVALUATION_SCHEMA",
    "ACCEPTANCE_REGISTRY_SCHEMA",
    "ACCEPTANCE_SUCCESSOR_SCHEMA",
    "ACCEPTANCE_TRIGGER_PROBE_SCHEMA",
    "BRACKET_BINDING_SCHEMA",
    "BRACKET_SCHEMA",
    "CalibrationCandidate",
    "build_calibration_bracket_binding",
    "calibration_bracket_for_bundles",
    "decimal_student_t_quantile",
    "derive_successor_decimal_derivation",
    "discover_calibration_candidates",
    "evaluate_calibration_bracket",
    "load_calibration_acceptance_bound",
    "load_calibration_acceptance_registry",
    "load_calibration_candidate",
    "probe_calibration_acceptance_trigger",
    "validate_calibration_bracket_binding",
]
