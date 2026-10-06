"""Copy validated claim verdicts into a Results orchestration manifest.

This adapter is not a paper issuer: it grants no custody, registry placement
or claim authority. The supplied ALPHA/BETA paths retain the existing
``results_fill_input.v1`` semantics (relative to the eventual manifest).
The GAMMA object carries a copy-only contrast projection for downstream
rendering. It does not estimate, alter scientific gates or infer floor lineage.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from collections.abc import Mapping
from typing import Any

from joulewise.analysis_engine.artifact import validate_claim_verdicts

INPUT_SCHEMA_VERSION = "joulewise.results_fill_input.v1"


class ResultsFillAdapterError(ValueError):
    """Invalid adapter input; never an empirical outcome or a prose fill."""


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ResultsFillAdapterError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _nonfinite(value):
    raise ResultsFillAdapterError(f"nonfinite JSON number: {value}")


def adapt_claim_verdicts(
    claim_verdicts_raw: bytes, *, campaigns: Mapping[str, Any],
    characterization: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a detached v1 manifest with all five issued outcomes preserved.

    Numeric fields are copied without rounding. ``j_per_token`` is populated
    only for a producer-issued J/token contrast; a J contrast remains null.
    Refused/unavailable estimates and intervals remain null, never zero.
    """
    try:
        if type(claim_verdicts_raw) is not bytes:
            raise ResultsFillAdapterError("raw UTF-8 claim-verdict bytes required")
        artifact = json.loads(claim_verdicts_raw.decode("utf-8"),
                              object_pairs_hook=_object, parse_constant=_nonfinite)
        errors = validate_claim_verdicts(artifact)
        if errors:
            raise ResultsFillAdapterError("invalid claim verdicts: " + "; ".join(errors))
        if not isinstance(campaigns, Mapping) or set(campaigns) != {"alpha", "beta"}:
            raise ResultsFillAdapterError("campaigns must contain alpha and beta exactly")
        if any(not isinstance(campaign, Mapping) for campaign in campaigns.values()):
            raise ResultsFillAdapterError("each campaign must be an object")
        if characterization is None:
            characterization = {"funded": False, "run": False, "verdict": None}
        if (not isinstance(characterization, Mapping)
            or set(characterization) != {"funded", "run", "verdict"}
            or type(characterization["funded"]) is not bool
            or type(characterization["run"]) is not bool):
            raise ResultsFillAdapterError("invalid characterization selection")
        rows = []
        for row in artifact["contrasts"]:
            estimator = row["estimator"]
            rows.append({
                "contrast_id": row["contrast_id"], "metric": row["metric"],
                "conditions": row["conditions"],
                "estimate": estimator["estimate"],
                "interval": estimator["metrology_aware_CI95"],
                "decision_interval": row["deterministic_bounds"]["decision_interval"],
                "deterministic_widening_total": row["deterministic_bounds"]["total"],
                "j_per_token": estimator["estimate"] if row["metric"]["unit"] == "J/token" else None,
                "n": estimator["n"], "floor": row["floor"],
                "multiplicity": row["multiplicity"], "claim_evaluation": row["claim_evaluation"],
            })
        output = deepcopy({
            "schema_version": INPUT_SCHEMA_VERSION, "campaigns": dict(campaigns),
            "gamma": {"claim_verdicts_id": artifact["claim_verdicts_id"],
                      "claim_verdicts_sha256": hashlib.sha256(claim_verdicts_raw).hexdigest(),
                      "evidence_class": artifact["inputs"]["evidence_class"], "contrasts": rows},
            "characterization": dict(characterization),
        })
        # A caller's orchestration fields must also be serializable JSON.
        json.dumps(output, allow_nan=False)
        return output
    except ResultsFillAdapterError:
        raise
    except (KeyError, TypeError, ValueError, ArithmeticError, RecursionError) as exc:
        raise ResultsFillAdapterError(f"invalid results-fill adapter input: {exc}") from exc


__all__ = ["ResultsFillAdapterError", "adapt_claim_verdicts"]
