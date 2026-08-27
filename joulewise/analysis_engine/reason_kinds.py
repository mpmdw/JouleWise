"""Mechanical DATA/CONTRACT partition for claim-edge smoke tests.

The claim evaluation is the authoritative pass surface.  Per-block reason
codes remain diagnostic inputs: their structure is checked by
``validate_claim_verdicts``, while any operative refusal is propagated into
the contrast's ``claim_evaluation.reason_codes`` by the engine.  Inspecting
the block lists a second time would therefore broaden D-158 R-2 beyond its
declared claim-edge predicate.

An ``unresolved`` evaluation with no reason codes is a DATA result too.  It
needs no vocabulary member: ``evaluate_claim`` selects that outcome when the
metrology interval crosses zero (``claims.py``) and appends no reason.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from typing import Any

from .artifact import validate_claim_verdicts
from .claims import REASON_CODES


# D-158 R-2 defines DATA by an enumerated list plus "the randomization/LOO
# sensitivity set", and CONTRACT as "everything else".  Two codes that live in
# claims._SENSITIVITY are deliberately NOT DATA, because _SENSITIVITY membership
# only drives ordered_reason_codes() precedence and does not make a code an
# answer about the measurement:
#   * outcome_dependent_top_up   (__init__.py:732) - unregistered matching
#     bundles exist, so the frozen sampling plan was violated.
#   * legacy_l1_mechanics_only   (__init__.py:734) - a caller-declared degraded
#     evidence class, i.e. a mode, not a measured result.
# Both are therefore CONTRACT.  This is strictly stricter: assert_data_reason_only
# refuses artifacts it would previously have passed.
DATA_REASON_CODES = frozenset(
    {
        "deterministic_bound_obscures_direction",
        "effect_not_above_floor",
        "equivalence_margin_not_above_floor",
        "equivalence_not_supported",
        "interpolation_bound_exceeds_floor",
        "interpolation_bound_exceeds_half_effect",
        "loo_magnitude_influential",
        "loo_verdict_influential",
        "multiplicity_not_rejected",
        "randomization_check_insufficient_blocks",
        "randomization_sensitivity_disagrees",
    }
)

# These registered spellings have no emitter in joulewise/ or scripts/ at the
# D-158 baseline.  The structural tests force any newly live spelling to move
# into DATA or CONTRACT deliberately.
DEAD_REASON_CODES = frozenset(
    {
        "calibration_ledger_bracket_slot_claimed",
        "multiplicity_family_incomplete",
    }
)

# A lock is neither a scientific answer nor a malformed-input diagnosis.  The
# smoke predicate requires it once in each declared contrast evaluation.
LOCK_REASON_CODES = frozenset({"mock_telemetry_claim_ineligible"})

CONTRACT_REASON_CODES = frozenset(
    REASON_CODES - DATA_REASON_CODES - DEAD_REASON_CODES - LOCK_REASON_CODES
)


def assert_data_reason_only(
    artifact: Mapping[str, Any],
    *,
    expect_lock: str | None = "mock_telemetry_claim_ineligible",
) -> None:
    """Assert that every contrast reached a schema-valid DATA verdict.

    ``present exactly once`` means once within every declared contrast's
    claim-evaluation list, not once across the artifact.  The engine de-dupes
    each contrast independently with ``ordered_reason_codes``; there is no
    artifact-global reason list on this wire.

    Passing ``expect_lock=None`` is useful for non-smoke artifacts and instead
    requires every lock to be absent.
    """

    if not isinstance(artifact, Mapping):
        raise AssertionError("claim artifact must be a mapping")
    contrasts = artifact.get("contrasts")
    if not isinstance(contrasts, list) or not contrasts:
        raise AssertionError("claim artifact must declare at least one contrast")
    if expect_lock is not None and expect_lock not in LOCK_REASON_CODES:
        raise AssertionError(f"unknown expected smoke lock: {expect_lock!r}")

    for index, contrast in enumerate(contrasts):
        if not isinstance(contrast, Mapping):
            raise AssertionError(f"contrast at index {index} is not an object")
        contrast_id = contrast.get("contrast_id")
        label = contrast_id if isinstance(contrast_id, str) else f"index {index}"
        evaluation = contrast.get("claim_evaluation")
        if not isinstance(evaluation, Mapping):
            raise AssertionError(f"contrast {label!r} has no claim evaluation")
        reasons = evaluation.get("reason_codes")
        if not isinstance(reasons, list) or any(
            not isinstance(code, str) for code in reasons
        ):
            raise AssertionError(
                f"contrast {label!r} has a malformed reason-code list"
            )

        counts = Counter(reasons)
        for code in LOCK_REASON_CODES:
            expected = 1 if code == expect_lock else 0
            if counts[code] != expected:
                raise AssertionError(
                    f"contrast {label!r} must contain lock {code!r} exactly "
                    f"{expected} time(s); observed {counts[code]}"
                )
        for code in reasons:
            if code in LOCK_REASON_CODES:
                continue
            if code not in DATA_REASON_CODES:
                raise AssertionError(
                    f"contrast {label!r} emitted non-DATA reason code {code!r}"
                )

    schema_errors = validate_claim_verdicts(artifact)
    if schema_errors:
        raise AssertionError(
            "claim artifact is not schema-valid: " + schema_errors[0]
        )


__all__ = [
    "CONTRACT_REASON_CODES",
    "DATA_REASON_CODES",
    "DEAD_REASON_CODES",
    "LOCK_REASON_CODES",
    "assert_data_reason_only",
]
