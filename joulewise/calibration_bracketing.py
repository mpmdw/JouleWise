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
from types import MappingProxyType
from typing import Any, Literal, Mapping, Sequence

from joulewise.authentication_io import read_authentication_input
from joulewise.bundle_read import BundleReadError, BundleReader
from joulewise.calibration_ledger import (
    IDENTITY_EPOCH_FIELDS,
    LEDGER_SCHEMA,
    CalibrationLedgerSnapshot,
    LedgerObservation,
    content_id_from_artifact_hashes,
    probe_custody,
)
try:  # pragma: no cover - exercised on whichever side of the seam is present
    from joulewise.calibration_ledger import (
        SESSION_KIND_BRACKET,
        SESSION_KIND_DERIVATION,
    )
except ImportError:  # pragma: no cover - pre-seam fallback, delete on merge
    # TEMPORARY SEAM SHIM.  The ledger owns this vocabulary and exports both
    # names; this checkout predates that export, so the values are restated
    # here to keep this module importable until the two branches meet.  The
    # integration tree REQUIRES the real import: delete this fallback there,
    # because two sources for one vocabulary is exactly the drift the import
    # exists to prevent.
    SESSION_KIND_BRACKET = "bracket"
    SESSION_KIND_DERIVATION = "derivation"
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
from joulewise.uncertainty_evidence import (
    ACTIVE_CAPTURE_ANCHOR_METHOD,
)

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
# D-079 anchor-v3 production-capture flip reissue. The member table and
# D-102 statistics are unchanged; r5 rotates only governed estimator pins.
ANCHOR_V3_R5_ACCEPTANCE_BOUND_PATH = (
    _CALIBRATION_CONFIG_DIR / "calibration_acceptance_d079_v2_n17_r5.json"
)
ANCHOR_V3_R5_ACCEPTANCE_ID = "d079_calibration_acceptance_v2_n17_r5"
ANCHOR_V3_R5_ACCEPTANCE_BOUND_SHA256 = (
    "92b9c0608bc97fbd7769050213b1433c32d3fe060d1292167920363e58b8cf0f"
)
# D-079 anchor-v3 capture-presentation reissue.  The member table and D-102
# statistics are unchanged; r6 rotates only the two governed estimator pins
# touched by the positive capture-pipeline and calibration-time taxonomy work.
ANCHOR_V3_R6_ACCEPTANCE_BOUND_PATH = (
    _CALIBRATION_CONFIG_DIR / "calibration_acceptance_d079_v2_n17_r6.json"
)
ANCHOR_V3_R6_ACCEPTANCE_ID = "d079_calibration_acceptance_v2_n17_r6"
ANCHOR_V3_R6_ACCEPTANCE_BOUND_SHA256 = (
    "0227bca3f826edc7f0a1baf98a394df01d8f48e9609966088870d712f765697d"
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
    ANCHOR_V3_R5_ACCEPTANCE_ID: {
        "path": ANCHOR_V3_R5_ACCEPTANCE_BOUND_PATH,
        "relative_path": (
            "configs/calibration/calibration_acceptance_d079_v2_n17_r5.json"
        ),
        "file_sha256": ANCHOR_V3_R5_ACCEPTANCE_BOUND_SHA256,
    },
    ANCHOR_V3_R6_ACCEPTANCE_ID: {
        "path": ANCHOR_V3_R6_ACCEPTANCE_BOUND_PATH,
        "relative_path": (
            "configs/calibration/calibration_acceptance_d079_v2_n17_r6.json"
        ),
        "file_sha256": ANCHOR_V3_R6_ACCEPTANCE_BOUND_SHA256,
    },
}
# The LIVE surface: what production loads when no artifact is named.
ACTIVE_ACCEPTANCE_ID = ANCHOR_V3_R6_ACCEPTANCE_ID
DEFAULT_ACCEPTANCE_BOUND_PATH = ANCHOR_V3_R6_ACCEPTANCE_BOUND_PATH
# Authenticates the retained ``schema_fixture_unissued`` genesis bytes; this is
# not the digest of ``DEFAULT_ACCEPTANCE_BOUND_PATH``.
GENESIS_FIXTURE_ACCEPTANCE_SHA256 = (
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
# The identity-epoch generation vocabulary.  A registered generation names the
# epoch ids its prior-observation-set catalog may carry; the TARGET epoch is
# the catalog entry whose six-field vector equals the artifact's own
# ``identity_epoch``, and is resolved from the artifact rather than registered,
# so a catalog can never disagree with the identity it claims to bind.
D079_EPOCH_CATALOG_ID = "d079_epoch"
# Ledger session kinds (ruling 46 §R-a A7) are stamped on the session's open
# receipt by the ledger writer and imported above from the ledger, which owns
# the vocabulary.  A `bracket` session reserves the endpoints of one claim
# window; a `derivation` session reserves a night of derivation-only captures
# that build a future acceptance and license no measurement.  A session record
# that carries no kind at all predates the field and reads as `bracket`; a row
# whose session cannot be resolved at all reads as neither and is barred.
SESSION_KIND_UNRESOLVED = "unresolved-session"
# Prior-set prefix modes (ruling 46 §R-b V6).  ``import_only`` is the genesis
# fence every issued generation to date was derived under: every ledger row at
# or below the cutoff is a historical import.  ``import_plus_live`` is reserved
# for a generation whose corpus was captured live on this machine, whose prefix
# therefore holds finalized live rows as well.
PRIOR_PREFIX_MODE_IMPORT_ONLY = "import_only"
PRIOR_PREFIX_MODE_IMPORT_PLUS_LIVE = "import_plus_live"
_PRIOR_PREFIX_MODES = frozenset(
    {PRIOR_PREFIX_MODE_IMPORT_ONLY, PRIOR_PREFIX_MODE_IMPORT_PLUS_LIVE}
)
# Registered bracket-screen derivation rules (ruling 46 §R-b V7).  Only the
# rule every issued generation was actually derived under is implemented here:
# the quantized corpus range IS the operative screen.  The D-125 envelope rule
# a successor may be derived under is Ed's open item and its
# ``successor_screen_exceeds_budget_ceiling`` refusal is not implemented in
# this module, so an unimplemented rule name refuses here rather than silently
# degrading to the rule below.
SCREEN_RULE_RANGE_EQUALS_SCREEN = "range_equals_screen"
_REGISTERED_SCREEN_RULES = frozenset({SCREEN_RULE_RANGE_EQUALS_SCREEN})
# Mechanism-named, outcome-independent corpus exclusions (ruling 46 §R-a A6).
# Today's only registered class is `affine_clock_fit_empty`: the anchor-v3
# replay found NO feasible affine wall-versus-monotonic clock fit for that
# capture, so no bound can be derived from it at all.  The exclusion turns on
# that replay outcome, never on the value the capture produced.  It is the
# class recorded at r6 `derivation_notes.excluded_predecessor_members`.
REGISTERED_CORPUS_EXCLUSION_REASONS = frozenset({"affine_clock_fit_empty"})
# Terminal dispositions a LIVE row may carry inside an `import_plus_live`
# cutoff prefix.  `abandoned` is deliberately absent: it maps to the
# `unresolved` classification, which is not an observation.
_LIVE_PREFIX_ADMITTED_DISPOSITIONS = frozenset(
    {"valid", "systematic-invalid", "ordinary-invalid"}
)
# The keys every registered generation row must carry, so that a future row
# that forgets one refuses instead of falling back to a literal.
_GENERATION_ROW_REQUIRED_KEYS = frozenset(
    {
        "corpus_n",
        "corpus_doubling_trigger",
        "prediction_95_two_draw_s",
        "prediction_99_two_draw_s",
        "operatives",
        "epoch_catalog_ids",
        "prior_prefix_mode",
        "prior_observation_count",
        "cutoff_sequence",
        "screen_rule",
        "predecessor_ceiling_s",
        "registration_session_ids",
    }
)
# The D-102 derivation is corpus-indexed, not global: corpus size, the two
# two-draw prediction pins, the ratified operative comparators, the
# corpus-doubling trigger vocabulary, the epoch catalog the prior set may name,
# the prior-set size and cutoff sequence, the prefix mode, the screen rule, the
# ceiling a successor inherits, and the ledger sessions of the registration are
# all functions of the member table a generation was derived from.  Retaining
# them per generation is what keeps the predecessor generations authenticating
# byte-identically after the live default moves.
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
    "epoch_catalog_ids": (D079_EPOCH_CATALOG_ID,),
    "prior_prefix_mode": PRIOR_PREFIX_MODE_IMPORT_ONLY,
    "prior_observation_count": 38,
    "cutoff_sequence": 76,
    "screen_rule": SCREEN_RULE_RANGE_EQUALS_SCREEN,
    # The ceiling of the generation this one was derived FROM under D-125's
    # envelope rule, or None when there is no such predecessor.  None here is
    # the truthful registration: the n=19 corpus is the genesis, derived from
    # no predecessor at all, so its ceiling is simply its own 99 % two-draw
    # prediction.  A generation that DOES inherit also names the predecessor's
    # registered row in `predecessor_acceptance_id`, and this number is checked
    # against that row rather than trusted.
    "predecessor_ceiling_s": None,
    # Import-only generations have no live capture registration.
    "registration_session_ids": (),
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
    "epoch_catalog_ids": (D079_EPOCH_CATALOG_ID,),
    "prior_prefix_mode": PRIOR_PREFIX_MODE_IMPORT_ONLY,
    "prior_observation_count": 38,
    "cutoff_sequence": 76,
    "screen_rule": SCREEN_RULE_RANGE_EQUALS_SCREEN,
    # None, not the n=19 ceiling.  The anchor-v3 r-series is a RE-DERIVATION of
    # the same captures under changed estimator bytes (D-145), not a D-125
    # envelope successor of the n=19 generation: its ceiling is its own Q99 and
    # sits BELOW n=19's, which registering n=19 as its predecessor would
    # correctly refuse.
    "predecessor_ceiling_s": None,
    "registration_session_ids": (),
}
_D102_GENERATION_DERIVATIONS: dict[str, dict[str, Any]] = {
    PREDECESSOR_ACCEPTANCE_ID: _D102_N19_DERIVATION,
    SUCCESSOR_ACCEPTANCE_ID: _D102_N19_DERIVATION,
    ANCHOR_V3_ACCEPTANCE_ID: _D102_N17_DERIVATION,
    # r4 is a science-neutral estimator-pin reissue of r3: same corpus, same
    # member table, therefore the same D-102 derivation.
    ANCHOR_V3_R4_ACCEPTANCE_ID: _D102_N17_DERIVATION,
    # r5 is the science-neutral production-capture flip reissue of r4.
    ANCHOR_V3_R5_ACCEPTANCE_ID: _D102_N17_DERIVATION,
    # r6 is the science-neutral capture-presentation reissue of r5.
    ANCHOR_V3_R6_ACCEPTANCE_ID: _D102_N17_DERIVATION,
}


def _registered_generation_row_is_complete(generation: Any) -> bool:
    """Whether a registered generation row carries every fence it must.

    The validator reads its epoch catalog, prior-set size, cutoff sequence,
    prefix mode and screen rule from this row instead of from literals, so a
    row that omits or malforms one of them must refuse rather than let the
    corresponding check evaporate.

    The row's CEILING IN FORCE (``operatives.maximum_budgetable_drift_s``, the
    largest drift this generation will ever budget) is not an independent fact:
    D-125 cl.2 fixes it exactly.  A generation derived from no predecessor
    takes its own 99 % two-draw prediction; a generation derived from one under
    the envelope rule takes ``max(predecessor ceiling, own Q99)``, so the
    ceiling of a lineage can never FALL.  An inequality cannot transcribe that:
    ``ceiling >= own Q99`` admits both a successor whose ceiling dropped below
    its predecessor's and one whose ceiling was invented above both inputs.
    Only the exact equation refuses both, and only if the row states the
    predecessor's ceiling, which is why ``predecessor_ceiling_s`` exists and is
    checked against the predecessor's own registered row rather than trusted.

    The operative screen must additionally sit strictly BELOW that ceiling, in
    every case: D-102 cl.3 spends the allowance
    ``max(observed_drift_s, bracket_screen_s)`` against it, and
    ``screen + excess == maximum`` at the bottom of ``_valid_acceptance_bound``
    would otherwise demand a zero or negative budgetable excess.  That is the
    shape of D-125's ``successor_screen_exceeds_budget_ceiling`` refusal.
    """

    if not isinstance(generation, Mapping):
        return False
    if not _GENERATION_ROW_REQUIRED_KEYS.issubset(set(generation)):
        return False
    catalog_ids = generation["epoch_catalog_ids"]
    session_ids = generation["registration_session_ids"]
    counts = (generation["prior_observation_count"], generation["cutoff_sequence"])
    operatives = generation["operatives"]
    if not isinstance(operatives, Mapping):
        return False
    # ABSENT and MALFORMED are different: `None` is a generation with no
    # predecessor, while a present value that will not parse as a Decimal --
    # including a non-string such as `0`, which is why the `is None` test comes
    # BEFORE `_decimal` -- is a broken row and refuses.
    predecessor_lexeme = generation["predecessor_ceiling_s"]
    predecessor: Decimal | None = None
    if predecessor_lexeme is not None:
        predecessor = _decimal(predecessor_lexeme)
        # The predecessor's ceiling is READ BACK from the predecessor's own
        # registered row, so a lineage cannot be rebased by editing one number
        # in the successor's row -- and a present value that will not parse
        # dies here too, because it is `None` and no registered Decimal equals
        # `None`.  One term, one job: an unparseable predecessor is not silently
        # promoted to an absent one.
        predecessor_row = _D102_GENERATION_DERIVATIONS.get(
            generation.get("predecessor_acceptance_id")
        )
        predecessor_operatives = (
            predecessor_row.get("operatives")
            if isinstance(predecessor_row, Mapping)
            else None
        )
        registered = (
            _decimal(predecessor_operatives.get("maximum_budgetable_drift_s"))
            if isinstance(predecessor_operatives, Mapping)
            else None
        )
        if registered is None or registered != predecessor:
            return False
    drift = _decimal(operatives.get("maximum_budgetable_drift_s"))
    prediction = _decimal(generation["prediction_99_two_draw_s"])
    screen = _decimal(operatives.get("bracket_screen_s"))
    if (
        drift is None
        or prediction is None
        or screen is None
        or drift
        != (prediction if predecessor is None else max(predecessor, prediction))
        or not screen < drift
    ):
        return False
    if not all(
        isinstance(count, int) and not isinstance(count, bool) and count > 0
        for count in counts
    ):
        return False
    # The cutoff sequence is TWO ledger rows per observation (a reservation and
    # a finalization).  That relation is exact for a prefix built only from the
    # genesis import, and it is deliberately NOT imposed on a live prefix, whose
    # sessions add open and abort control rows the observation count does not
    # predict.
    if (
        generation["prior_prefix_mode"] == PRIOR_PREFIX_MODE_IMPORT_ONLY
        and generation["cutoff_sequence"]
        != 2 * generation["prior_observation_count"]
    ):
        return False
    return (
        isinstance(catalog_ids, tuple)
        and bool(catalog_ids)
        and all(isinstance(item, str) and item for item in catalog_ids)
        and len(set(catalog_ids)) == len(catalog_ids)
        and generation["prior_prefix_mode"] in _PRIOR_PREFIX_MODES
        and generation["screen_rule"] in _REGISTERED_SCREEN_RULES
        and isinstance(session_ids, tuple)
        and all(isinstance(item, str) and item for item in session_ids)
        and len(set(session_ids)) == len(session_ids)
        and (
            bool(session_ids)
            is (
                generation["prior_prefix_mode"]
                == PRIOR_PREFIX_MODE_IMPORT_PLUS_LIVE
            )
        )
    )


def acceptance_generation_operatives(
    acceptance_id: str,
    *,
    acceptance: Mapping[str, Any] | None = None,
) -> Mapping[str, str] | None:
    """Return registered D-102 operatives, refusing an operative crosswire."""

    derivation = _D102_GENERATION_DERIVATIONS.get(acceptance_id)
    if derivation is None:
        return None
    operatives = derivation["operatives"]
    registered_screen = operatives["bracket_screen_s"]
    if acceptance is not None and "decimal_derivation" in acceptance:
        decimal_derivation = acceptance["decimal_derivation"]
        if not isinstance(decimal_derivation, Mapping):
            raise ValueError(
                "supplied acceptance operatives disagree with the registered "
                "generation: decimal_derivation must be a mapping"
            )
        if "ratified_operatives" not in decimal_derivation:
            return MappingProxyType(operatives)
        supplied_operatives = decimal_derivation["ratified_operatives"]
        if not isinstance(supplied_operatives, Mapping):
            raise ValueError(
                "supplied acceptance operatives disagree with the registered "
                "generation: ratified_operatives must be a mapping"
            )
        if supplied_operatives.get("bracket_screen_s") != registered_screen:
            raise ValueError(
                "supplied acceptance operatives disagree with the registered "
                "generation: bracket_screen_s "
                f"{supplied_operatives.get('bracket_screen_s')!r} disagrees with "
                f"registered bracket_screen_s {registered_screen!r} for "
                f"acceptance_id {acceptance_id!r}"
            )
    return MappingProxyType(operatives)


def acceptance_bracket_screen_s(
    acceptance_id: str,
    *,
    acceptance: Mapping[str, Any] | None = None,
) -> str | None:
    """Resolve the registered bracket screen for an acceptance generation."""

    operatives = acceptance_generation_operatives(
        acceptance_id, acceptance=acceptance
    )
    return operatives["bracket_screen_s"] if operatives is not None else None


def acceptance_allowance_rule(
    acceptance_id: str,
    *,
    acceptance: Mapping[str, Any] | None = None,
) -> str | None:
    """Render the registered never-zero allowance rule for a generation."""

    screen = acceptance_bracket_screen_s(acceptance_id, acceptance=acceptance)
    return f"max(observed_drift_s,{screen})" if screen is not None else None


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
    if generation is None or not _registered_generation_row_is_complete(generation):
        return False
    expected_n = generation["corpus_n"]
    operative_values = generation["operatives"]
    prefix_mode = generation["prior_prefix_mode"]
    registered_epoch_catalog_ids = set(generation["epoch_catalog_ids"])
    # The TARGET epoch is the catalog entry that equals the artifact's own
    # identity: exactly one, or the artifact does not unambiguously bind the
    # epoch it claims.  A generation whose corpus was captured after an epoch
    # change carries the predecessor's epoch in the catalog too, so the target
    # can no longer be the single literal `d079_epoch` it was through r6.
    epoch_catalog = prior.get("epoch_catalog") if isinstance(prior, Mapping) else None
    target_epoch_ids = (
        [
            epoch_id
            for epoch_id, epoch in epoch_catalog.items()
            if epoch == identity
        ]
        if isinstance(epoch_catalog, Mapping)
        else []
    )
    # A live-prefix generation declares which ledger session each prior-set row
    # came from, so the registration the completeness check ranges over is
    # ledger-bound rather than asserted.
    expected_observation_keys = {
        "content_id",
        "epoch_id",
        "disposition",
        "attempt_id",
    }
    if prefix_mode == PRIOR_PREFIX_MODE_IMPORT_PLUS_LIVE:
        expected_observation_keys = expected_observation_keys | {"session_id"}
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
        or set(prior["epoch_catalog"]) != registered_epoch_catalog_ids
        or len(target_epoch_ids) != 1
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

    target_epoch_id = target_epoch_ids[0]
    prior_ids: list[str] = []
    prior_attempt_ids: list[str] = []
    prior_member_ids: set[str] = set()
    prior_row_by_content_id: dict[str, Mapping[str, Any]] = {}
    for observation in prior["observations"]:
        if (
            not isinstance(observation, Mapping)
            or set(observation) != expected_observation_keys
            or not _valid_sha256(observation.get("content_id"))
            or observation.get("epoch_id") not in registered_epoch_catalog_ids
            or observation.get("disposition") not in allowed_prior_dispositions
            or not isinstance(observation.get("attempt_id"), str)
            or not observation.get("attempt_id")
            or "session_id" in expected_observation_keys
            and not (
                observation.get("session_id") is None
                or isinstance(observation.get("session_id"), str)
                and observation["session_id"]
            )
        ):
            return False
        prior_ids.append(observation["content_id"])
        prior_attempt_ids.append(observation["attempt_id"])
        prior_row_by_content_id[observation["content_id"]] = observation
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
        # Prior-set size and cutoff sequence are registered per generation, not
        # literal: every generation issued to date was derived from the 38-row
        # genesis import at ledger sequence 76, and a successor derived from a
        # longer ledger must register its own pair rather than move a literal
        # every predecessor still validates against.
        if (
            len(prior["observations"]) != generation["prior_observation_count"]
            or cutoff["sequence"] != generation["cutoff_sequence"]
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
    # PURITY.  Every corpus member's own prior-set row must carry the epoch the
    # artifact binds.  Without this a member captured under the PREVIOUS epoch
    # could be averaged into the screens that judge the new one, which is the
    # cross-epoch contamination the per-row epoch id exists to prevent.
    for content_id in member_content_ids:
        member_row = prior_row_by_content_id.get(content_id)
        if member_row is None or member_row["epoch_id"] != target_epoch_id:
            return False
    # COMPLETENESS.  A generation whose corpus was captured live must account
    # for every valid observation of its own registration: each one is either a
    # member or a named, mechanism-based exclusion.  Selecting members by
    # outcome after the values are known would fit the new screens to the old
    # ones, and nothing else in the artifact would show it.
    if prefix_mode == PRIOR_PREFIX_MODE_IMPORT_PLUS_LIVE:
        registration_session_ids = set(generation["registration_session_ids"])
        registration_valid_ids: set[str] = set()
        for observation in prior["observations"]:
            if (
                observation["disposition"] != "valid"
                or observation["epoch_id"] != target_epoch_id
            ):
                continue
            # A valid same-epoch row from OUTSIDE this registration refuses
            # issuance rather than being silently absorbed into the corpus:
            # its capture conditions were never pre-registered.
            if observation.get("session_id") not in registration_session_ids:
                return False
            registration_valid_ids.add(observation["content_id"])
        notes = value.get("derivation_notes")
        excluded = notes.get("excluded_members") if isinstance(notes, Mapping) else None
        if not isinstance(excluded, list):
            return False
        excluded_content_ids: set[str] = set()
        for entry in excluded:
            if (
                not isinstance(entry, Mapping)
                or set(entry)
                != {
                    "member_id",
                    "manifest_sha256",
                    "instrument_evidence_sha256",
                    "reason",
                }
                or not isinstance(entry.get("member_id"), str)
                or not entry["member_id"]
                or not _valid_sha256(entry.get("manifest_sha256"))
                or not _valid_sha256(entry.get("instrument_evidence_sha256"))
                or entry.get("reason") not in REGISTERED_CORPUS_EXCLUSION_REASONS
            ):
                return False
            # The exclusion entry carries no content id, so it is matched into
            # the prior set by the id derived from its two artifact hashes.
            excluded_content_id = content_id_from_artifact_hashes(
                {
                    "manifest.json": entry["manifest_sha256"],
                    "instrument_evidence.json": entry["instrument_evidence_sha256"],
                }
            )
            if excluded_content_id is None:
                return False
            excluded_content_ids.add(excluded_content_id)
        if (
            len(excluded_content_ids) != len(excluded)
            or member_content_ids & excluded_content_ids
            or member_content_ids | excluded_content_ids != registration_valid_ids
        ):
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
    # The bracket screen's derivation rule is generation-keyed.  Every issued
    # generation to date was derived under `range_equals_screen`: the corpus
    # range quantized to 1e-6 s IS the screen.  A generation registering any
    # other rule refuses here until that rule is implemented, so a successor
    # derived under a D-125 envelope cannot pass by defaulting to this one.
    if generation["screen_rule"] != SCREEN_RULE_RANGE_EQUALS_SCREEN:
        return False
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
        expected_sha256: str | None = GENESIS_FIXTURE_ACCEPTANCE_SHA256
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
    return GENESIS_FIXTURE_ACCEPTANCE_SHA256


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
    directory: Path, *, runs_root: Path,
    mode: Literal["read_replay", "issuing"] = "issuing",
) -> CalibrationCandidate | None:
    """Probe the locator, then authenticate primary bytes on the caller thread."""

    original = Path(directory)

    def inspect(mapped: Path) -> CalibrationCandidate | None:
        mapped_runs_root = Path(runs_root)
        if mapped != original:
            # Preserve the candidate's relative identity when a backup moves.
            try:
                relative = original.absolute().relative_to(mapped_runs_root.absolute())
            except ValueError:
                return None
            mapped_runs_root = mapped
            for _ in relative.parts:
                mapped_runs_root = mapped_runs_root.parent
        return _load_calibration_candidate_unbounded(mapped, runs_root=mapped_runs_root)

    return probe_custody(original, inspect, lambda: None, mode=mode)


def _load_calibration_candidate_unbounded(
    directory: Path, *, runs_root: Path
) -> CalibrationCandidate | None:
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
    observation: LedgerObservation, *,
    mode: Literal["read_replay", "issuing"] = "issuing",
) -> CalibrationCandidate | None:
    """Authenticate one valid ledger observation from its custody locator."""

    if observation.disposition != "valid" or observation.content_id is None:
        return None
    custody = Path(observation.custody_locator)
    candidate = load_calibration_candidate(
        custody,
        runs_root=custody.parent.parent,
        mode=mode,
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


def _session_record_kind(session: Any) -> str:
    """Read one session record's kind, defaulting to ``bracket``.

    The kind is stamped on the session's open receipt.  This reader is
    deliberately defensive: a ledger written before that field existed carries
    no kind at all, and the only safe reading of a missing kind is the ordinary
    bracket session every historical row belongs to.
    """

    kind = getattr(session, "session_kind", None)
    return kind if isinstance(kind, str) and kind else SESSION_KIND_BRACKET


def _observation_session_kind(
    observation: Any,
    ledger_snapshot: CalibrationLedgerSnapshot,
) -> str:
    """Resolve one ledger ROW's session kind.

    A row belonging to no session, or to a session the ledger holds without a
    kind, is ``bracket`` -- that is every row written before derivation kinds
    existed.  A row naming a session the snapshot CANNOT resolve is neither:
    it returns ``SESSION_KIND_UNRESOLVED`` and is barred from the endpoint
    universe.
    """

    kind = getattr(observation, "session_kind", None)
    if isinstance(kind, str) and kind:
        return kind
    session_id = getattr(observation, "bracket_session_id", None)
    if not isinstance(session_id, str) or not session_id:
        return SESSION_KIND_BRACKET
    session = ledger_snapshot.bracket_session_by_id.get(session_id)
    if session is None:
        # FAIL CLOSED.  A row that names a session the snapshot does not hold
        # is not a bracket endpoint by default; nothing here can tell whether
        # the missing session was a derivation night, so the row is barred from
        # the endpoint universe rather than admitted into it.
        return SESSION_KIND_UNRESOLVED
    return _session_record_kind(session)


def _is_derivation_kind_observation(
    observation: Any,
    ledger_snapshot: CalibrationLedgerSnapshot,
) -> bool:
    """Whether a row was captured to DERIVE a future acceptance.

    A derivation-only capture is taken under a deliberately stale acceptance
    to build the successor's corpus; it is never evidence that a claim window
    was bracketed.  After the successor issues, such a row is same-epoch and
    inside the endpoint horizon, so without this predicate a corpus member
    would end up judging itself (D-102 cl.2).

    A row whose session cannot be resolved is barred for the same reason: it
    may be a derivation row, and admitting it on that doubt is the fail-open
    reading.
    """

    return _observation_session_kind(observation, ledger_snapshot) in (
        SESSION_KIND_DERIVATION,
        SESSION_KIND_UNRESOLVED,
    )


def _capture_pipeline_refusal_for_observation(
    observation: LedgerObservation,
) -> str | None:
    """Classify a ledger-valid candidate's capture era before reconciliation."""

    method = observation.t1_bindings.get("anchor_method_version")
    # This is deliberately an allowlist: every stored era other than the
    # active claim-bearing method is replay evidence, never a claim candidate.
    if method != ACTIVE_CAPTURE_ANCHOR_METHOD:
        return "capture_pipeline_superseded"
    return None


def discover_calibration_candidates(
    ledger_snapshot: CalibrationLedgerSnapshot, *,
    mode: Literal["read_replay", "issuing"] = "issuing",
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
            # Derivation-only rows are skipped, never returned as a discovery
            # failure: they are ordinary valid observations that simply cannot
            # bracket a claim window.  A `return None` here would empty the
            # whole enumeration (the `return ()` on a `None` candidate at the
            # bottom of this loop), and this skip must stay
            # symmetric with the `registered_valid` universe below or the
            # anti-withholding equality every caller satisfies exactly would
            # break on a night that captured any of them.
            or _is_derivation_kind_observation(observation, ledger_snapshot)
        ):
            continue
        if _capture_pipeline_refusal_for_observation(observation) is not None:
            continue
        candidate = _candidate_from_observation(observation, mode=mode)
        if candidate is None:
            return ()
        candidates.append(candidate)
    return tuple(candidates)


def _prior_set_matches_import_cutoff_prefix(
    artifact: Mapping[str, Any],
    ledger_snapshot: CalibrationLedgerSnapshot,
) -> bool:
    """Bind issuance prior-set data to the cutoff prefix its generation allows.

    The prefix rule is generation-keyed (ruling 46 §R-b V6).  Under
    ``import_only`` — every generation issued to date — a single live row at or
    below the cutoff refuses, which is what makes the genesis import the sole
    provenance of those corpora.  Under ``import_plus_live`` the prefix may
    also hold live rows that reached a terminal disposition and carry a content
    id, including the finalized slots of a session closed by abort; a pending
    row (no content id) or an ``abandoned`` row (classification ``unresolved``)
    still refuses, because neither is an observation anything may be derived
    from.
    """

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
    generation = _D102_GENERATION_DERIVATIONS.get(artifact.get("acceptance_id"))
    if generation is None or not _registered_generation_row_is_complete(generation):
        return False
    prefix_mode = generation["prior_prefix_mode"]
    live_prefix_allowed = prefix_mode == PRIOR_PREFIX_MODE_IMPORT_PLUS_LIVE
    if live_prefix_allowed:
        # `registration_session_ids` must name DERIVATION-kind sessions, and the
        # ledger is what says so.  Without this, a registration could point at
        # ordinary claim-window bracket sessions, and the completeness check
        # would then treat captures taken to MEASURE something as if they had
        # been pre-registered to derive the successor's screens.  A session the
        # ledger does not hold, or one whose kind is missing (read as
        # `bracket`), refuses.
        sessions = ledger_snapshot.bracket_session_by_id
        for session_id in generation["registration_session_ids"]:
            session = sessions.get(session_id)
            if (
                session is None
                or _session_record_kind(session) != SESSION_KIND_DERIVATION
            ):
                return False
    for observation in prefix:
        if observation.is_historical_import:
            continue
        if (
            not live_prefix_allowed
            or observation.content_id is None
            or observation.classification_disposition
            not in _LIVE_PREFIX_ADMITTED_DISPOSITIONS
        ):
            return False
    catalog = artifact["prior_observation_set"]["epoch_catalog"]
    expected = {
        (
            row["attempt_id"],
            row["content_id"],
            row["disposition"],
            row["epoch_id"],
        )
        + ((row.get("session_id"),) if live_prefix_allowed else ())
        for row in artifact["prior_observation_set"]["observations"]
    }
    observed: set[tuple[Any, ...]] = set()
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
            # A live-prefix artifact must also declare, per row, the ledger
            # session it came from; that is what makes the registration the
            # completeness check ranges over ledger-bound rather than asserted.
            + (
                (observation.bracket_session_id,)
                if live_prefix_allowed
                else ()
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
        and _capture_pipeline_refusal_for_observation(observation) is None
        and (
            observation.bracket_session_id is None
            or observation.bracket_session_id in finalized_session_ids
        )
        # The same derivation-kind skip as `discover_calibration_candidates`.
        # Both sites move together: dropping it here alone would put a row in
        # the registered universe that discovery never offers, and the exact
        # equality below would refuse every claim window on the machine.
        and not _is_derivation_kind_observation(observation, ledger_snapshot)
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
    mode: Literal["read_replay", "issuing"] = "issuing",
    ledger_snapshot: CalibrationLedgerSnapshot | None = None,
    bracket_binding: Mapping[str, Any] | None = None,
    bracket_window_id: str | None = None,
    bracket_plan_id: str | None = None,
    bracket_plan_sha256: str | None = None,
    bracket_evidence_root_id: str | None = None,
    diagnostics: list[dict[str, str]] | None = None,
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
    superseded_observations: list[LedgerObservation] = []
    if ledger_snapshot is None:
        candidates: tuple[CalibrationCandidate, ...] = ()
    else:
        candidates = discover_calibration_candidates(ledger_snapshot, mode=mode)
        superseded_observations = [
            observation
            for observation in ledger_snapshot.observations
            if observation.disposition == "valid"
            and not observation.is_historical_import
            and (
                observation.bracket_session_id is None
                or any(
                    session.session_id == observation.bracket_session_id
                    and session.state == "finalized"
                    for session in ledger_snapshot.bracket_sessions
                )
            )
            and _capture_pipeline_refusal_for_observation(observation) is not None
        ]
        registered_valid = sum(
            observation.disposition == "valid"
            and not observation.is_historical_import
            and _capture_pipeline_refusal_for_observation(observation) is None
            and (
                observation.bracket_session_id is None
                or any(
                    session.session_id == observation.bracket_session_id
                    and session.state == "finalized"
                    for session in ledger_snapshot.bracket_sessions
                )
            )
            # Third site of the same universe: this count is compared to the
            # discovery enumeration directly above, so a derivation row left in
            # here would make every window on the machine refuse
            # `calibration_ledger_custody_invalid` for as long as the row is on
            # the ledger, which is forever.
            and not _is_derivation_kind_observation(observation, ledger_snapshot)
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
    result, reasons = evaluate_calibration_bracket(
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
    if superseded_observations:
        recorded_diagnostics = [
            {
                "attempt_id": observation.attempt_id,
                "reason": "capture_pipeline_superseded",
            }
            for observation in superseded_observations
        ]
        # This assessment is the production-persisted surface.  Keep era
        # observations visible here without promoting them into the refusal
        # reasons for an otherwise valid current-era bracket.
        result["diagnostics"] = recorded_diagnostics
        if diagnostics is not None:
            diagnostics.extend(recorded_diagnostics)
        if not candidates:
            reasons = tuple(dict.fromkeys((*reasons, "capture_pipeline_superseded")))
    return result, reasons


__all__ = [
    "ACCEPTANCE_BOUND_SCHEMA",
    "ACCEPTANCE_EVALUATION_SCHEMA",
    "BRACKET_BINDING_SCHEMA",
    "BRACKET_SCHEMA",
    "CalibrationCandidate",
    "acceptance_allowance_rule",
    "acceptance_bracket_screen_s",
    "acceptance_generation_operatives",
    "build_calibration_bracket_binding",
    "calibration_bracket_for_bundles",
    "discover_calibration_candidates",
    "evaluate_calibration_bracket",
    "load_calibration_acceptance_bound",
    "load_calibration_candidate",
    "validate_calibration_bracket_binding",
]
