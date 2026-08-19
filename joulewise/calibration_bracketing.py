"""Claim-time pre/post powermetrics fiducial calibration bracketing.

The bracket carries a nonparametric 95/95 calibration-distribution bound into
claims only under the registered T1-T3 transfer assumptions; it does not turn
either finite sample maximum into an unconditional instrument property.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, replace
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN, localcontext
from pathlib import Path
from typing import Any, Mapping, Sequence

from joulewise.authentication_io import read_authentication_input
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
from joulewise.uncertainty_evidence import ACTIVE_CAPTURE_ANCHOR_METHOD

BRACKET_SCHEMA = "joulewise.instrument_calibration_bracket.v1"
BRACKET_BINDING_SCHEMA = "joulewise.calibration_bracket_binding.v1"
ACCEPTANCE_BOUND_SCHEMA = "joulewise.calibration_acceptance_bound.v2"
ACCEPTANCE_FIXTURE_SCHEMA = (
    "joulewise.calibration_acceptance_bound.v2.fixture.v1"
)
ACCEPTANCE_EVALUATION_SCHEMA = "joulewise.calibration_acceptance_evaluation.v2"
_CALIBRATION_CONFIG_DIR = (
    Path(__file__).resolve().parents[1] / "configs" / "calibration"
)
# D-116 initial issuance.  Retained as a first-class generation: the frozen
# `_v1` packs, their extraction specs, and the genesis bootstrap authenticate
# against these exact bytes forever.  Never repointed.
PREDECESSOR_ACCEPTANCE_BOUND_PATH = (
    _CALIBRATION_CONFIG_DIR / "calibration_acceptance_d079_v2.json"
)
PREDECESSOR_ACCEPTANCE_ID = "d079_calibration_acceptance_v2_n19"
ISSUED_ACCEPTANCE_BOUND_SHA256 = (
    "316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985"
)
# D-138 reissue at the integrated estimator head (WO-DETECT-PULSES-BUDGET
# changed `joulewise/powermetrics_fiducial.py`, one of the four governed
# estimator-source pins).  Same schema, same n=19 corpus, same thresholds,
# same science-facing values; the identity carries the reissue ordinal `_r2`
# rather than a schema bump.
SUCCESSOR_ACCEPTANCE_BOUND_PATH = (
    _CALIBRATION_CONFIG_DIR / "calibration_acceptance_d079_v2_r2.json"
)
SUCCESSOR_ACCEPTANCE_ID = "d079_calibration_acceptance_v2_n19_r2"
SUCCESSOR_ACCEPTANCE_BOUND_SHA256 = (
    "3c92dd664cdf138860f2bb29e8dcf8397d5d1608b24d65e3de62a78d279e0d6e"
)
# D-079 anchor-v3 science-facing generation.  The clock-anchor estimator moved
# from the falsified rate=1 censored intersection to the rate-aware
# set-membership method, so member VALUES change and the corpus SHRINKS: the
# two pre-clock-discipline captures whose stamp rectangles admit no single
# affine wall rate now refuse.  Same schema and same `decision_ids`; the
# identity carries the corpus size and the reissue ordinal.  Ratified by the
# cold science review at
# `docs/process_traces/2026-08-18-anchor-v3-science-review/03-cold-science-review.md`.
ANCHOR_V3_ACCEPTANCE_BOUND_PATH = (
    _CALIBRATION_CONFIG_DIR / "calibration_acceptance_d079_v2_n17_r3.json"
)
ANCHOR_V3_ACCEPTANCE_ID = "d079_calibration_acceptance_v2_n17_r3"
ANCHOR_V3_ACCEPTANCE_BOUND_SHA256 = (
    "73f022633e7bc22e9e129617f3f2ad8797293adaff3b53923dc41f75da2ae917"
)
# D-079 anchor-v3 CAPTURE-ACTIVATION reissue.  Activating the rate-aware
# set-membership anchor as the live capture method
# (`ACTIVE_CAPTURE_ANCHOR_METHOD`, plus the capture/admission/projection wiring)
# changed the bytes of `joulewise/uncertainty_evidence.py`, one of the four
# governed estimator sources, which fires the r3 artifact's own
# `protocol_or_estimator_byte_change` trigger.  SCIENCE-NEUTRAL: the whole
# corpus was re-derived under the anchor-v3 estimator at the activation head and
# every physical value reproduced r3 exactly, so r4 differs from r3 in the
# estimator pin set alone.  r3 is RETAINED as an intermediate generation.
ANCHOR_V3_R4_ACCEPTANCE_BOUND_PATH = (
    _CALIBRATION_CONFIG_DIR / "calibration_acceptance_d079_v2_n17_r4.json"
)
ANCHOR_V3_R4_ACCEPTANCE_ID = "d079_calibration_acceptance_v2_n17_r4"
ANCHOR_V3_R4_ACCEPTANCE_BOUND_SHA256 = (
    "dcb3d3ed2fe41a7b637e9fe6ca6dc5be81c3d57574bfcfa1ab3b97df32bd52eb"
)
# Multi-generation registry.  Authentication is indexed by the artifact's own
# `acceptance_id`, so a caller cannot present one generation's bytes under
# another generation's pin, and predecessor packs stay verifiable unchanged.
ISSUED_ACCEPTANCE_REGISTRY: dict[str, dict[str, Any]] = {
    PREDECESSOR_ACCEPTANCE_ID: {
        "path": PREDECESSOR_ACCEPTANCE_BOUND_PATH,
        "relative_path": "configs/calibration/calibration_acceptance_d079_v2.json",
        "file_sha256": ISSUED_ACCEPTANCE_BOUND_SHA256,
    },
    SUCCESSOR_ACCEPTANCE_ID: {
        "path": SUCCESSOR_ACCEPTANCE_BOUND_PATH,
        "relative_path": "configs/calibration/calibration_acceptance_d079_v2_r2.json",
        "file_sha256": SUCCESSOR_ACCEPTANCE_BOUND_SHA256,
    },
    ANCHOR_V3_ACCEPTANCE_ID: {
        "path": ANCHOR_V3_ACCEPTANCE_BOUND_PATH,
        "relative_path": (
            "configs/calibration/calibration_acceptance_d079_v2_n17_r3.json"
        ),
        "file_sha256": ANCHOR_V3_ACCEPTANCE_BOUND_SHA256,
    },
    ANCHOR_V3_R4_ACCEPTANCE_ID: {
        "path": ANCHOR_V3_R4_ACCEPTANCE_BOUND_PATH,
        "relative_path": (
            "configs/calibration/calibration_acceptance_d079_v2_n17_r4.json"
        ),
        "file_sha256": ANCHOR_V3_R4_ACCEPTANCE_BOUND_SHA256,
    },
}
# The LIVE surface: what production loads when no artifact is named.
ACTIVE_ACCEPTANCE_ID = ANCHOR_V3_R4_ACCEPTANCE_ID
DEFAULT_ACCEPTANCE_BOUND_PATH = ANCHOR_V3_R4_ACCEPTANCE_BOUND_PATH
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
# The D-102 derivation is corpus-indexed, not global: corpus size, the two
# two-draw prediction pins, the ratified operative comparators, and the
# corpus-doubling trigger vocabulary are all functions of the member table a
# generation was derived from.  Retaining them per generation is what keeps the
# predecessor generations authenticating byte-identically after the live
# default moves.
_D102_N19_DERIVATION: dict[str, Any] = {
    "corpus_n": 19,
    "corpus_doubling_trigger": "corpus_doubles_from_19_to_38",
    "prediction_95_two_draw_s": "0.008826584887500717",
    "prediction_99_two_draw_s": "0.012093166090593858",
    "operatives": {
        "bracket_screen_s": "0.010818",
        "preflight_level_screen_s": "0.033558756679900",
        "max_budgetable_excess_s": "0.001275166090593858",
        "maximum_budgetable_drift_s": "0.012093166090593858",
    },
}
_D102_N17_DERIVATION: dict[str, Any] = {
    "corpus_n": 17,
    "corpus_doubling_trigger": "corpus_doubles_from_17_to_34",
    "prediction_95_two_draw_s": "0.007377644019421586",
    "prediction_99_two_draw_s": "0.010164834757777545",
    "operatives": {
        "bracket_screen_s": "0.009724",
        "preflight_level_screen_s": "0.032898493715362",
        "max_budgetable_excess_s": "0.000440834757777545",
        "maximum_budgetable_drift_s": "0.010164834757777545",
    },
}
_D102_GENERATION_DERIVATIONS: dict[str, dict[str, Any]] = {
    PREDECESSOR_ACCEPTANCE_ID: _D102_N19_DERIVATION,
    SUCCESSOR_ACCEPTANCE_ID: _D102_N19_DERIVATION,
    ANCHOR_V3_ACCEPTANCE_ID: _D102_N17_DERIVATION,
    # r4 is a science-neutral estimator-pin reissue of r3: same corpus, same
    # member table, therefore the same D-102 derivation.
    ANCHOR_V3_R4_ACCEPTANCE_ID: _D102_N17_DERIVATION,
}
# Retained name for the D-116/D-138 n=19 generations' comparators.
_D102_OPERATIVE_VALUES = _D102_N19_DERIVATION["operatives"]


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
            relative: hashlib.sha256(
                read_authentication_input(
                    _REPO_ROOT / relative,
                    grammar="raw",
                    label=f"calibration estimator code {relative}",
                )
            ).hexdigest()
            for relative in ESTIMATOR_CODE_PATHS
        }
    except OSError:
        return None


def _valid_acceptance_bound(value: Any) -> bool:
    """Validate the D-102 artifact from its decimal-source member table."""

    if not isinstance(value, Mapping):
        return False
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
    # Identity is generation-indexed: the retained genesis fixture keeps the
    # initial-issuance identity, while an issued artifact must name one of the
    # registered issued generations.  An unregistered id is never authority.
    allowed_acceptance_ids = (
        frozenset(ISSUED_ACCEPTANCE_REGISTRY)
        if role == "issued"
        else frozenset({PREDECESSOR_ACCEPTANCE_ID})
    )
    # The corpus-derived expectations are selected by the artifact's own
    # identity, never by the live default, so every registered generation keeps
    # validating against the member table it was actually derived from.
    generation = _D102_GENERATION_DERIVATIONS.get(value.get("acceptance_id"))
    if generation is None:
        return False
    expected_n = generation["corpus_n"]
    operative_values = generation["operatives"]
    if (
        not role_valid
        or value.get("acceptance_id") not in allowed_acceptance_ids
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
            generation["corpus_doubling_trigger"],
            "new_systematic_failure_challenges_preflight_screen",
        }
        or not isinstance(corpus, Mapping)
        or corpus.get("n") != expected_n
        or not isinstance(corpus.get("members"), list)
        or len(corpus["members"]) != expected_n
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
    if len(set(member_ids)) != expected_n or member_ids != sorted(member_ids):
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
        != generation["prediction_95_two_draw_s"]
        or statistics.get("prediction_99_two_draw_s")
        != generation["prediction_99_two_draw_s"]
        or rounding.get("mode") != "ROUND_HALF_EVEN"
        or not isinstance(rounding.get("operative_bracket_screen"), Mapping)
        or rounding["operative_bracket_screen"].get("quantum_s") != "0.000001"
        or rounding["operative_bracket_screen"].get("value_s")
        != operative_values["bracket_screen_s"]
        or not isinstance(rounding.get("preflight_level_screen"), Mapping)
        or rounding["preflight_level_screen"].get("quantum_s")
        != "0.000000000000001"
        or rounding["preflight_level_screen"].get("value_s")
        != operative_values["preflight_level_screen_s"]
        or any(operatives.get(key) != item for key, item in operative_values.items())
        or operatives.get("allowance_rule")
        != "max(observed_drift_s,bracket_screen_s)"
        or operatives.get("operative_bound_rule")
        != "max(pre_b_fiducial_s,post_b_fiducial_s)+calibration_drift_allowance_s"
        or operatives.get("embedding_count") != 1
    ):
        return False
    screen = Decimal(operative_values["bracket_screen_s"])
    maximum = Decimal(operative_values["maximum_budgetable_drift_s"])
    excess = Decimal(operative_values["max_budgetable_excess_s"])
    return (
        (max(values) - min(values)).quantize(
            Decimal("0.000001"), rounding=ROUND_HALF_EVEN
        )
        == screen
        and max(values).quantize(
            Decimal("0.000000000000001"), rounding=ROUND_HALF_EVEN
        )
        == Decimal(operative_values["preflight_level_screen_s"])
        and screen + excess == maximum
    )


def load_calibration_acceptance_bound(
    path: Path = DEFAULT_ACCEPTANCE_BOUND_PATH,
) -> dict[str, Any] | None:
    """Load the file-pinned D-102 acceptance artifact fail-closed."""

    try:
        raw = read_authentication_input(
            path, grammar="json", label="calibration acceptance artifact"
        )
    except OSError:
        return None
    return _acceptance_bound_from_authenticated_bytes(raw)


def _acceptance_bound_from_authenticated_bytes(
    raw: bytes,
) -> dict[str, Any] | None:
    """Parse acceptance bytes only when their role-indexed pin authenticates."""

    def reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, item in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key {key!r}")
            result[key] = item
        return result

    def reject_nonfinite(value: str) -> None:
        raise ValueError(f"non-finite JSON number {value!r}")

    try:
        value = json.loads(
            raw,
            object_pairs_hook=reject_duplicate_pairs,
            parse_constant=reject_nonfinite,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
        return None
    # Any file route is authenticated by one of the reviewed exact-byte states:
    # the genesis fixture retained for pre-issuance tests, or a registered
    # issued generation.  A caller cannot turn an alternate self-consistent
    # document into authority by choosing a path, and cannot present one issued
    # generation's bytes under another generation's pin: the expected digest is
    # selected by the document's own `acceptance_id`.
    role = value.get("artifact_role") if isinstance(value, Mapping) else None
    if role == "schema_fixture_unissued":
        expected_sha256: str | None = DEFAULT_ACCEPTANCE_BOUND_SHA256
    elif role == "issued":
        registered = ISSUED_ACCEPTANCE_REGISTRY.get(value.get("acceptance_id"))
        expected_sha256 = registered["file_sha256"] if registered else None
    else:
        expected_sha256 = None
    if expected_sha256 is None or hashlib.sha256(raw).hexdigest() != expected_sha256:
        return None
    if not _valid_acceptance_bound(value):
        return None
    return dict(value)


def issued_calibration_allowance_projection(
    acceptance: Mapping[str, Any],
    *,
    pre_exact_bound_lexeme_s: str,
    post_exact_bound_lexeme_s: str,
) -> dict[str, Any] | None:
    """Derive the mint-facing exact-Decimal allowance from issued authority.

    The returned values are a verification projection, not generated pins.
    The artifact must be the exact code-pinned issued acceptance bytes and the
    arithmetic is the same ratified rule used by ``evaluate_calibration_bracket``.
    """

    authenticated = _authenticated_explicit_acceptance_bound(acceptance)
    if authenticated is None or authenticated.get("artifact_role") != "issued":
        return None
    derivation = authenticated.get("decimal_derivation")
    operatives = (
        derivation.get("ratified_operatives")
        if isinstance(derivation, Mapping)
        else None
    )
    if not isinstance(operatives, Mapping):
        return None
    if (
        operatives.get("allowance_rule")
        != "max(observed_drift_s,bracket_screen_s)"
        or operatives.get("embedding_count") != 1
    ):
        return None
    try:
        pre = Decimal(pre_exact_bound_lexeme_s)
        post = Decimal(post_exact_bound_lexeme_s)
        screen = Decimal(str(operatives["bracket_screen_s"]))
        maximum = Decimal(str(operatives["maximum_budgetable_drift_s"]))
    except (InvalidOperation, KeyError, TypeError, ValueError):
        return None
    if any(not value.is_finite() or value < 0 for value in (pre, post, screen, maximum)):
        return None
    observed = abs(pre - post)
    if observed > maximum:
        return None
    return {
        "observed_drift_s": str(observed),
        "allowance_rule": operatives["allowance_rule"],
        "bracket_screen_s": str(screen),
        "applied_allowance_s": str(max(observed, screen)),
        "allowance_embedding_count": operatives["embedding_count"],
    }


def _authenticated_explicit_acceptance_bound(
    value: Mapping[str, Any],
) -> dict[str, Any] | None:
    """Authenticate an in-memory artifact against the checked-in byte pin.

    Routing is generation-indexed so a predecessor pack presenting the D-116
    issuance still authenticates after the live default moved to the successor.
    """

    registered = (
        ISSUED_ACCEPTANCE_REGISTRY.get(value.get("acceptance_id"))
        if isinstance(value, Mapping)
        else None
    )
    path = (
        registered["path"] if registered is not None else DEFAULT_ACCEPTANCE_BOUND_PATH
    )
    pinned = load_calibration_acceptance_bound(path)
    if pinned is None or dict(value) != pinned:
        return None
    return pinned


def _acceptance_artifact_sha256(artifact: Mapping[str, Any]) -> str:
    """Return the reviewed exact-byte pin for a validated artifact identity."""

    if artifact.get("artifact_role") == "issued":
        registered = ISSUED_ACCEPTANCE_REGISTRY[artifact["acceptance_id"]]
        return str(registered["file_sha256"])
    return DEFAULT_ACCEPTANCE_BOUND_SHA256


def _valid_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value)
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
        or post.sequence > ledger_snapshot.head_sequence
        or post.sequence > len(ledger_snapshot.receipts)
        or ledger_snapshot.receipts[post.sequence - 1].get(
            "receipt_digest"
        )
        != post.receipt_digest
    ):
        raise ValueError(
            "bracket session endpoints are not valid in the authenticated ledger"
        )
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
        manifest_raw = read_authentication_input(
            directory / "manifest.json",
            grammar="json",
            label=f"calibration candidate {directory.name} manifest",
        )
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
            raw = read_authentication_input(
                member,
                grammar="raw",
                label=f"calibration candidate {directory.name} artifact {name}",
            )
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
        != ACTIVE_CAPTURE_ANCHOR_METHOD
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
    # A complete session pair makes the binding mandatory only for a window
    # that pair can causally and freshly bracket.  ``candidates`` still spans
    # the full registered universe above, preserving the anti-withholding
    # equality check without coupling historical ordinary windows to later
    # session observations.
    matching = [
        candidate
        for candidate in candidates
        if candidate.protocol_id == PROTOCOL_ID
        and all(
            candidate.bindings.get(field) == bindings.get(field)
            for field in V2_BINDING_FIELDS
        )
    ]
    window_session_pre_ids = {
        candidate.bracket_session_id
        for candidate in matching
        if candidate.bracket_session_id is not None
        and candidate.bracket_slot == "pre"
        and candidate.capture_wall_time_s <= window_start_s
        and window_end_s <= candidate.capture_wall_time_s + MAX_AGE_S
    }
    window_session_post_ids = {
        candidate.bracket_session_id
        for candidate in matching
        if candidate.bracket_session_id is not None
        and candidate.bracket_slot == "post"
        and candidate.capture_wall_time_s >= window_end_s
        and candidate.capture_wall_time_s - window_start_s <= MAX_AGE_S
    }
    has_session_candidates = (
        bool(window_session_pre_ids & window_session_post_ids)
        or bracket_binding is not None
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
    matching_decimals: dict[int, Decimal] = {}
    for candidate in matching:
        candidate_decimal = _candidate_decimal(candidate)
        if candidate_decimal is None or candidate_decimal < 0:
            return result, ("instrument_calibration_invalid",)
        matching_decimals[id(candidate)] = candidate_decimal
    corpus_members = artifact["derivation_corpus"]["members"]
    # The corpus-doubling trigger is a function of THIS artifact's corpus, not
    # a global constant: a generation derived from a smaller corpus reaches its
    # doubling threshold sooner, and says so in its own trigger vocabulary.
    _generation = _D102_GENERATION_DERIVATIONS[artifact["acceptance_id"]]
    corpus_doubling_trigger = _generation["corpus_doubling_trigger"]
    corpus_doubling_threshold = 2 * _generation["corpus_n"]
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
    if len(valid_same_epoch) >= corpus_doubling_threshold:
        observed_triggers.append(corpus_doubling_trigger)
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
        # Session observations are reserved to bracket their own window via an
        # exact binding; they never serve as unbound endpoints, even one-sided
        # (a lone causally-eligible slot must not stand in for a neighbour).
        if (
            pre.bracket_session_id is not None
            or post.bracket_session_id is not None
        ):
            return result, ("calibration_bracket_binding_missing",)
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
            corpus_doubling_trigger,
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
    "BRACKET_BINDING_SCHEMA",
    "BRACKET_SCHEMA",
    "CalibrationCandidate",
    "build_calibration_bracket_binding",
    "calibration_bracket_for_bundles",
    "discover_calibration_candidates",
    "evaluate_calibration_bracket",
    "load_calibration_acceptance_bound",
    "load_calibration_candidate",
    "validate_calibration_bracket_binding",
]
