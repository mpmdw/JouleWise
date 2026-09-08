"""D-179 reported-energy registration and non-issuing projection kernel.

Evidence ingress belongs exclusively to paper_custody.open_paper_input. Private
arithmetic helpers accept normalized records for synthetic verification; they
are not authentication APIs and cannot mint a paper capability.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import statistics


SCHEMA = "joulewise.paper_reported_energy_projection.v1"
REGISTRATION_SCHEMA = "joulewise.paper_reported_energy_registration.v1"
INTERVAL_METHOD = "stratified_repeat_abba_mean_t9_plus_kind_bounds.v1"
EXCLUDED_PREDICTION_TERM = "detection_floor.py:sqrt(1+1/n)"
T975_DF9 = 2.262157162798205
BOUND_KINDS = (
    "E_clock_anchor_shift_bound_j",
    "E_interpolation_joint_edge_bound_j",
    "E_whole_window_drift_allowance_j",
)
MODELS = ("qwen3-1p7b", "qwen3-8b")
CELL_RE = re.compile(r"d117-reported-mean-ph-(decode|prefill-p42|prefill-p512)-(qwen3-1p7b|qwen3-8b)")
SHA_RE = re.compile(r"[0-9a-f]{64}")


def _exact(value, keys, label):
    if type(value) is not dict or set(value) != set(keys):
        raise ValueError(f"{label}: exact keys required")
    return value


def _number(value, label, *, nonnegative=False):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError(f"{label}: finite non-boolean number required")
    if nonnegative and value < 0:
        raise ValueError(f"{label}: negative value")
    return value


def _sha(value, label):
    if type(value) is not str or SHA_RE.fullmatch(value) is None:
        raise ValueError(f"{label}: SHA-256 required")
    return value


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def _cell_identity(cell_id):
    match = CELL_RE.fullmatch(cell_id) if type(cell_id) is str else None
    if match is None:
        raise ValueError("cell_id: exact registered model/phase/length required")
    role, model = match.groups()
    return model, "decode" if role == "decode" else "prefill"


def phase_ratio_estimand(cell_id):
    """Build registration metadata only; this reads no measurement evidence."""
    _, phase = _cell_identity(cell_id)
    return {
        "cell_id": cell_id, "form": "ratio_of_totals",
        "numerator": "gross_phase_energy_j", "phase": phase,
        "denominator": ("runtime_observed_output_tokens" if phase == "decode"
                        else "runtime_observed_prompt_tokens"),
        "denominator_unit": "token", "tokenizer_scope": "same_identity_required",
        "output_policy_scope": "same_policy_required",
    }


def validate_phase_ratio_estimand(value):
    """Exact sibling schema; the existing B8 ratio_estimand stays untouched."""
    if type(value) is not dict or value != phase_ratio_estimand(value.get("cell_id")):
        raise ValueError("phase_ratio_estimand: exact registered ratio_of_totals required")
    return value


def reported_energy_registration(cell_id):
    model, phase = _cell_identity(cell_id)
    return {
        "schema_version": REGISTRATION_SCHEMA, "authority": "D-179",
        "cell_id": cell_id, "model": model, "phase": phase,
        "reducer": "arithmetic_mean_over_fixed_member_universe.v1",
        "expected_n": 50, "missing_or_invalid_member": "refuse_reported_mean",
        "independence_units": 20, "absolute_repeats": 10, "complete_abba_blocks": 10,
        "stratum_weights": [0.2, 0.8], "reference_df": 9,
        "interval_method": INTERVAL_METHOD, "deterministic_bound_kinds": list(BOUND_KINDS),
        "excluded_prediction_term": EXCLUDED_PREDICTION_TERM,
        "attribution_floor": "labelled_beside_never_composed",
        "phase_ratio_estimand": phase_ratio_estimand(cell_id),
    }


def registration_manifest(model):
    if model not in MODELS:
        raise ValueError("unregistered model")
    return [reported_energy_registration(f"d117-reported-mean-ph-{role}-{model}")
            for role in ("decode", "prefill-p42", "prefill-p512")]


def registration_sha256(model):
    return _digest(registration_manifest(model))


def _validate_registration(value):
    if type(value) is not dict:
        raise ValueError("registration: exact object required")
    if value != reported_energy_registration(value.get("cell_id")):
        raise ValueError("registration: changed registered semantics; prediction-term substitution forbidden")
    validate_phase_ratio_estimand(value["phase_ratio_estimand"])


def _validate_members(cell):
    _exact(cell, {"cell_id", "metric", "window_class", "target_precheck_path", "measurand",
                  "reducer", "expected_n", "members", "missing_or_invalid_member", "numeric_value",
                  "projection_registration", "phase_ratio_estimand"}, "reported cell")
    reg = cell["projection_registration"]
    _validate_registration(reg)
    model, phase = _cell_identity(cell["cell_id"])
    if (reg["cell_id"] != cell["cell_id"] or cell["metric"] != f"phase_energy_j.{phase}"
        or cell["window_class"] != "phase" or cell["target_precheck_path"] != ["phase", phase]
        or cell["measurand"] != "gross_phase_energy_j" or cell["numeric_value"] is not None
        or cell["reducer"] != reg["reducer"] or type(cell["expected_n"]) is not int
        or cell["expected_n"] != 50 or cell["missing_or_invalid_member"] != reg["missing_or_invalid_member"]
        or cell["phase_ratio_estimand"] != reg["phase_ratio_estimand"]):
        raise ValueError("reported cell: identity or registration mismatch")
    members = cell["members"]
    if type(members) is not list or len(members) != 50:
        raise ValueError("members: complete 50-member universe required")
    ids = []
    for ordinal, member in enumerate(members, 1):
        _exact(member, {"ordinal", "bundle_id", "config_sha256"}, "member")
        if type(member["ordinal"]) is not int or member["ordinal"] != ordinal:
            raise ValueError("member: ordered ordinal mismatch")
        if type(member["bundle_id"]) is not str or not member["bundle_id"]:
            raise ValueError("member: bundle identity required")
        _sha(member["config_sha256"], "config_sha256")
        ids.append(member["bundle_id"])
    if len(set(ids)) != 50:
        raise ValueError("members: duplicate bundle")
    return model, phase


def _validate_registered_spec(spec):
    """Corroborate membership against the independent floor census, in order."""
    from joulewise.floor_extraction import validate_extraction_spec
    errors = validate_extraction_spec(spec)
    if errors:
        raise ValueError(f"extraction_spec: {errors}")
    cells = spec.get("reported_energy_cells")
    if type(cells) is not list or len(cells) != 3:
        raise ValueError("reported_energy_cells: three registered cells per model required")
    model, _ = _validate_members(cells[0])
    if [cell.get("cell_id") for cell in cells] != [r["cell_id"] for r in registration_manifest(model)]:
        raise ValueError("reported_energy_cells: ordered model/cell census mismatch")
    if spec.get("reported_energy_registration", {}).get("registration_sha256") != registration_sha256(model):
        raise ValueError("registration digest mismatch")
    if len(spec["cells"]) != 6:
        raise ValueError("floor census: exactly six cells required")
    for index, cell in enumerate(cells):
        _validate_members(cell)
        absolute, comparative = spec["cells"][index * 2:index * 2 + 2]
        role = ("decode", "prefill-p42", "prefill-p512")[index]
        if (absolute["cell_id"] != f"d117-df-ph-{role}-{model}-absolute"
            or comparative["cell_id"] != f"d117-df-cmp-abba-ph-{role}-{model}"):
            raise ValueError("floor census: model/phase cell identity mismatch")
        if (absolute["kind"] != "absolute" or comparative["kind"] != "comparative"
            or type(absolute["expected_n"]) is not int or absolute["expected_n"] != 10
            or type(comparative["expected_n"]) is not int or comparative["expected_n"] != 10
            or len(absolute["members"]) != 10 or len(comparative["blocks"]) != 10
            or absolute["metric"] != cell["metric"] or comparative["metric"] != cell["metric"]):
            raise ValueError("floor census: stratum shape/phase mismatch")
        ordered = [row["bundle_id"] for row in absolute["members"]]
        ordered += [block["members"][position] for block in comparative["blocks"]
                    for position in ("A1", "B1", "B2", "A2")]
        pins = absolute["member_config_sha256"] + comparative["member_config_sha256"]
        if ([row["bundle_id"] for row in cell["members"]] != ordered
            or [{k: row[k] for k in ("bundle_id", "config_sha256")} for row in cell["members"]] != pins):
            raise ValueError("members: exact ordered floor/config census mismatch")


def _observed_tokens(row, phase):
    value = row["tokens"]
    _exact(value, {"source", "total", "output", "prompt_realized", "tokenize_end",
                   "prefill_start", "tokenizer_sha256", "output_policy_sha256"}, "tokens")
    if value["source"] != "runtime_observed":
        raise ValueError("tokens: configured/fallback denominator forbidden")
    for name in ("total", "output", "prompt_realized", "tokenize_end", "prefill_start"):
        if type(value[name]) is not int or value[name] < 0:
            raise ValueError("tokens: absent or malformed denominator")
    prompt = value["total"] - value["output"]
    if prompt <= 0 or any(value[name] != prompt for name in ("prompt_realized", "tokenize_end", "prefill_start")):
        raise ValueError("tokens: four prompt surfaces disagree")
    for name in ("tokenizer_sha256", "output_policy_sha256"):
        _sha(value[name], name)
    denominator = value["output"] if phase == "decode" else prompt
    if denominator <= 0:
        raise ValueError("tokens: zero denominator")
    return denominator


def _project_cell(cell, rows, binding):
    """Private normalized arithmetic kernel, never an evidence admission API."""
    model, phase = _validate_members(cell)
    _exact(binding, {"model", "cell_id", "extraction_spec_sha256", "selection_sha256",
                     "prompt_pin_sha256", "whole_window_basis_sha256", "attribution_floor_j"}, "binding")
    if binding["model"] != model or binding["cell_id"] != cell["cell_id"]:
        raise ValueError("binding: swapped model/phase")
    for name in ("extraction_spec_sha256", "selection_sha256", "prompt_pin_sha256", "whole_window_basis_sha256"):
        _sha(binding[name], name)
    _number(binding["attribution_floor_j"], "attribution_floor_j", nonnegative=True)
    if type(rows) is not list or len(rows) != 50:
        raise ValueError("members: missing/invalid member refuses mean; never 49")
    energy, bounds, tokens = [], {kind: [] for kind in BOUND_KINDS}, []
    token_error = None
    token_scope = None
    for index, (member, row) in enumerate(zip(cell["members"], rows)):
        _exact(row, {"member", "model", "phase", "selection_sha256", "prompt_pin_sha256",
                     "whole_window_basis_sha256", "strict_valid", "unit", "energy_j", "bounds_j", "tokens"}, "record")
        if (row["member"] != member or row["model"] != model or row["phase"] != phase
            or any(row[name] != binding[name] for name in ("selection_sha256", "prompt_pin_sha256", "whole_window_basis_sha256"))):
            raise ValueError("record: ordered identity/provenance mismatch")
        expected_unit = {"kind": "repeat", "index": index + 1, "position": None} if index < 10 else {
            "kind": "abba", "index": (index - 10) // 4 + 1, "position": ("A1", "B1", "B2", "A2")[(index - 10) % 4]}
        if (row["strict_valid"] is not True or row["unit"] != expected_unit
            or type(row["unit"]["index"]) is not int):
            raise ValueError("record: invalid member or incomplete/reordered ABBA unit")
        energy.append(_number(row["energy_j"], "energy_j", nonnegative=True))
        _exact(row["bounds_j"], BOUND_KINDS, "bounds_j (prediction term forbidden)")
        for kind in BOUND_KINDS:
            bounds[kind].append(_number(row["bounds_j"][kind], kind, nonnegative=True))
        try:
            tokens.append(_observed_tokens(row, phase))
            scope = tuple(row["tokens"][key] for key in ("tokenizer_sha256", "output_policy_sha256"))
            if token_scope is not None and token_scope != scope:
                raise ValueError("tokens: tokenizer/output-policy scope mismatch")
            token_scope = scope
        except (ValueError, KeyError, TypeError) as exc:
            token_error = str(exc)
    repeats = energy[:10]
    blocks = [statistics.fmean(energy[start:start + 4]) for start in range(10, 50, 4)]
    mean = statistics.fmean(energy)
    s_r, s_b = statistics.stdev(repeats), statistics.stdev(blocks)
    variance = 0.2 ** 2 * s_r ** 2 / 10 + 0.8 ** 2 * s_b ** 2 / 10
    half = T975_DF9 * math.sqrt(variance)
    terms = {kind: statistics.fmean(values) for kind, values in bounds.items()}
    bound = math.fsum(terms.values())
    result = {
        "cell_id": cell["cell_id"], "model": model, "phase": phase,
        "members": cell["members"], "mean_j": mean, "lower_j": mean - half - bound,
        "upper_j": mean + half + bound, "n_bundles": 50, "independence_units": 20,
        "interval": {"method": INTERVAL_METHOD, "n_r": 10, "n_b": 10, "df": 9,
                     "s_r": s_r, "s_b": s_b, "variance": variance, "h_j": half,
                     "kind_averages_j": terms, "B_j": bound},
        "phase_ratio_estimand": cell["phase_ratio_estimand"],
        "per_token": {"status": "refused" if token_error else "computed",
                      "energy_sum_j": math.fsum(energy),
                      "observed_token_sum": None if token_error else sum(tokens),
                      "j_per_token": None if token_error else math.fsum(energy) / sum(tokens),
                      "reason": "runtime_observed_denominator_invalid" if token_error else None},
        "binding": dict(binding), "attribution_floor_composed": False,
    }
    # Reject overflow in intermediate arithmetic, including otherwise plausible endpoints.
    json.dumps(result, allow_nan=False)
    return result


def _validate_projection(projection, cell, rows, binding):
    expected = _project_cell(cell, rows, binding)
    if type(projection) is not dict or _digest(projection) != _digest(expected):
        raise ValueError("projection: recomputation mismatch (schema, endpoints, ratio, count or provenance)")


def _synthetic_projection(documents):
    """Called only inside D-173 fixture replay. No production dispatch exists."""
    _exact(documents, {"spec", "cells"}, "synthetic projection input")
    _validate_registered_spec(documents["spec"])
    cells = documents["cells"]
    if type(cells) is not list or len(cells) != 3:
        raise ValueError("synthetic cells: exact census required")
    results = []
    for cell, data in zip(documents["spec"]["reported_energy_cells"], cells):
        _exact(data, {"rows", "binding"}, "synthetic cell")
        if data["binding"]["extraction_spec_sha256"] != _digest(documents["spec"]):
            raise ValueError("frozen extraction spec binding mismatch")
        results.append(_project_cell(cell, data["rows"], data["binding"]))
    return {"schema_version": SCHEMA, "mode": "test_fixture_non_issuing", "cells": results}


__all__ = ["phase_ratio_estimand", "validate_phase_ratio_estimand", "reported_energy_registration",
           "registration_manifest", "registration_sha256"]
