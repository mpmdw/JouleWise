"""Copy validated claim verdicts into a Results orchestration manifest.

This adapter is not a paper issuer: it grants no custody, registry placement
or claim authority. The supplied ALPHA/BETA paths retain the existing
``results_fill_input.v1`` semantics (relative to the eventual manifest).
The GAMMA object carries a copy-only contrast projection for downstream
rendering. It does not estimate, alter scientific gates or infer floor lineage.
"""
from __future__ import annotations

import base64
import binascii
from copy import deepcopy
import hashlib
import json
from collections.abc import Mapping
from typing import Any

from joulewise.b5_analysis.kept_units import CellKeptUnits

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
    finalized_manifest_raw: bytes | None = None,
    floor_artifact_raw: bytes | None = None,
    exclusions_sha256: str | None = None,
    kept_quads: Mapping[str, CellKeptUnits] | None = None,
    expected_contrast_ids=None,
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
        extended = any(value is not None for value in (finalized_manifest_raw, floor_artifact_raw,
                       exclusions_sha256, kept_quads, expected_contrast_ids))
        manifest = None
        if expected_contrast_ids is not None:
            try:
                observed = [row["contrast_id"] for row in artifact["contrasts"]]
                expected = list(expected_contrast_ids)
                if len(observed) != len(set(observed)) or len(expected) != len(set(expected)) or set(observed) != set(expected):
                    raise ValueError()
            except (KeyError, TypeError, ValueError):
                raise ResultsFillAdapterError("results_fill_contrast_census_mismatch") from None
        if finalized_manifest_raw is not None:
            try:
                manifest = json.loads(finalized_manifest_raw.decode("utf-8"),
                                      object_pairs_hook=_object, parse_constant=_nonfinite)
                if (validate_claim_verdicts(artifact, frozen_manifest=manifest)
                    or hashlib.sha256(finalized_manifest_raw).hexdigest() != artifact["inputs"]["analysis_manifest"]["file_sha256"]):
                    raise ValueError()
            except (KeyError, TypeError, ValueError, AttributeError):
                raise ResultsFillAdapterError("results_fill_manifest_mismatch") from None
        if floor_artifact_raw is not None:
            try:
                floor = artifact["inputs"]["floor_artifact"]
                if (floor_artifact_raw != base64.b64decode(floor["embedded_bytes_base64"], validate=True)
                    or hashlib.sha256(floor_artifact_raw).hexdigest() != floor["file_sha256"]):
                    raise ValueError()
            except (KeyError, TypeError, ValueError, binascii.Error):
                raise ResultsFillAdapterError("results_fill_floor_mismatch") from None
        if exclusions_sha256 is not None:
            try:
                if manifest is None or exclusions_sha256 != manifest["evidence"]["analysed_attempt_exclusions"]["sha256"]:
                    raise ValueError()
            except (KeyError, TypeError, ValueError):
                raise ResultsFillAdapterError("results_fill_exclusions_mismatch") from None
        if kept_quads is not None:
            try:
                for row in artifact["contrasts"]:
                    kept = kept_quads[row["contrast_id"]]
                    yes = {u.unit_id for u in kept.kept["quad"]}
                    no = {u.unit_id for u in kept.dropped if u.stratum == "quad"}
                    blocks = row["bundle_blocks"]["blocks"]
                    if ({b["block_id"] for b in blocks if b["included"] is True} != yes
                        or {b["block_id"] for b in blocks if b["included"] is False} != no
                        or row["estimator"]["n"] != len(kept.kept["quad"])):
                        raise ValueError()
            except (KeyError, TypeError, ValueError, AttributeError):
                raise ResultsFillAdapterError("results_fill_kept_quads_mismatch") from None
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
            if extended:
                target = rows[-1]
                target.update({key: row[key] for key in ("plan_id", "claim_role", "hypothesized_direction", "equivalence", "sampling", "loo")})
                target.update({key: estimator[key] for key in ("df", "t_critical_95")})
                included = {b["block_id"] for b in row["bundle_blocks"]["blocks"] if b["included"] is True}
                target["kept_block_ids"] = [bid for bid in row["bundle_blocks"]["planned_block_ids"] if bid in included]
                target["removed_block_ids"] = [bid for bid in row["bundle_blocks"]["planned_block_ids"] if bid not in included]
        output = deepcopy({
            "schema_version": INPUT_SCHEMA_VERSION, "campaigns": dict(campaigns),
            "gamma": {"claim_verdicts_id": artifact["claim_verdicts_id"],
                      "claim_verdicts_sha256": hashlib.sha256(claim_verdicts_raw).hexdigest(),
                      "evidence_class": artifact["inputs"]["evidence_class"], "contrasts": rows},
            "characterization": dict(characterization),
        })
        if extended:
            output["gamma"]["finalized_manifest"] = deepcopy(artifact["inputs"]["analysis_manifest"])
            output["gamma"]["floor_artifact"] = {key: artifact["inputs"]["floor_artifact"][key]
                                                for key in ("artifact_id", "file_sha256")}
            output["gamma"]["exclusions_sha256"] = (exclusions_sha256 if exclusions_sha256 is not None else
                manifest.get("evidence", {}).get("analysed_attempt_exclusions", {}).get("sha256") if manifest is not None else None)
        # A caller's orchestration fields must also be serializable JSON.
        json.dumps(output, allow_nan=False)
        return output
    except ResultsFillAdapterError:
        raise
    except (KeyError, TypeError, ValueError, ArithmeticError, RecursionError) as exc:
        raise ResultsFillAdapterError(f"invalid results-fill adapter input: {exc}") from exc


def render_results_fill_input(value) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                       allow_nan=False) + "\n").encode("utf-8")


__all__ = ["ResultsFillAdapterError", "adapt_claim_verdicts", "render_results_fill_input"]
