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
import subprocess
from functools import wraps
from dataclasses import dataclass
from typing import Mapping, Sequence

from joulewise.b5_analysis.kept_units import ReportedCellKept


SCHEMA = "joulewise.paper_reported_energy_projection.v1"
REGISTRATION_SCHEMA = "joulewise.paper_reported_energy_registration.v1"
INTERVAL_METHOD = "stratified_repeat_abba_mean_t9_plus_kind_bounds.v1"
EXCLUDED_PREDICTION_TERM = "detection_floor.py:sqrt(1+1/n)"
T975: Mapping[int, float] = {
    9: 2.262157162798205, 8: 2.306004135204166, 7: 2.364624251592785,
    6: 2.44691185114497, 5: 2.5705818356363155, 4: 2.7764451051977943,
    3: 3.1824463052837095, 2: 4.302652729749464, 1: 12.706204736174705,
}
T975_DF9 = T975[9]
BOUND_KINDS = (
    "E_clock_anchor_shift_bound_j",
    "E_interpolation_joint_edge_bound_j",
    "E_whole_window_drift_allowance_j",
)
MODELS = ("qwen3-1p7b", "qwen3-8b")
PREFILL_LADDER_PROMPT_TOKENS = (512, 1024, 2048, 4096)
CELL_RE = re.compile(r"d117-reported-mean-ph-(decode|prefill-p42|prefill-p(?:512|1024|2048|4096))-(qwen3-1p7b|qwen3-8b)")
SHA_RE = re.compile(r"[0-9a-f]{64}")


PAPER_REPORTED_ENERGY_REFUSAL_CODES = frozenset({
    "paper_reported_energy_binding_mismatch",
    "paper_reported_energy_cell_census_invalid",
    "paper_reported_energy_cell_identity_invalid",
    "paper_reported_energy_cell_registration_mismatch",
    "paper_reported_energy_denominator_invalid",
    "paper_reported_energy_digest_invalid",
    "paper_reported_energy_floor_census_invalid",
    "paper_reported_energy_floor_identity_mismatch",
    "paper_reported_energy_floor_member_mismatch",
    "paper_reported_energy_floor_stratum_mismatch",
    "paper_reported_energy_kept_units_below_minimum",
    "paper_reported_energy_whole_window_allowance_unrecorded",
    "paper_reported_energy_member_count_invalid",
    "paper_reported_energy_member_duplicate",
    "paper_reported_energy_member_identity_invalid",
    "paper_reported_energy_member_order_invalid",
    "paper_reported_energy_model_invalid",
    "paper_reported_energy_number_invalid",
    "paper_reported_energy_ordering_history_invalid",
    "paper_reported_energy_projection_absent",
    "paper_reported_energy_projection_mismatch",
    "paper_reported_energy_prompt_surfaces_disagree",
    "paper_reported_energy_ratio_estimand_invalid",
    "paper_reported_energy_record_identity_mismatch",
    "paper_reported_energy_record_invalid",
    "paper_reported_energy_registration_digest_mismatch",
    "paper_reported_energy_registration_invalid",
    "paper_reported_energy_registration_not_before_spec",
    "paper_reported_energy_request_invalid",
    "paper_reported_energy_schema_invalid",
    "paper_reported_energy_spec_binding_mismatch",
    "paper_reported_energy_spec_invalid",
    "paper_reported_energy_token_scope_mismatch",
})


class PaperReportedEnergyRefusal(ValueError):
    """Closed, out-of-band diagnostic; never a paper result or capability."""

    def __init__(self, code):
        self.code = code if code in PAPER_REPORTED_ENERGY_REFUSAL_CODES else "paper_reported_energy_request_invalid"
        self.rendered_output = ()
        super().__init__(self.code)


def _closed_refusals(fn):
    @wraps(fn)
    def checked(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except PaperReportedEnergyRefusal:
            raise
        except (ValueError, TypeError, KeyError, IndexError, AttributeError, ArithmeticError) as exc:
            raise PaperReportedEnergyRefusal("paper_reported_energy_request_invalid") from exc
    return checked


def _exact(value, keys, label):
    if type(value) is not dict or set(value) != set(keys):
        raise PaperReportedEnergyRefusal("paper_reported_energy_schema_invalid")
    return value


def _number(value, label, *, nonnegative=False):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise PaperReportedEnergyRefusal("paper_reported_energy_number_invalid")
    if nonnegative and value < 0:
        raise PaperReportedEnergyRefusal("paper_reported_energy_number_invalid")
    return value


def _sha(value, label):
    if type(value) is not str or SHA_RE.fullmatch(value) is None:
        raise PaperReportedEnergyRefusal("paper_reported_energy_digest_invalid")
    return value


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def _cell_identity(cell_id):
    match = CELL_RE.fullmatch(cell_id) if type(cell_id) is str else None
    if match is None:
        raise PaperReportedEnergyRefusal("paper_reported_energy_cell_identity_invalid")
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


@_closed_refusals
def validate_phase_ratio_estimand(value):
    """Exact sibling schema; the existing B8 ratio_estimand stays untouched."""
    if type(value) is not dict or value != phase_ratio_estimand(value.get("cell_id")):
        raise PaperReportedEnergyRefusal("paper_reported_energy_ratio_estimand_invalid")
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


def _prefill_length(value):
    if type(value) is not int or value not in PREFILL_LADDER_PROMPT_TOKENS:
        raise PaperReportedEnergyRefusal("paper_reported_energy_cell_census_invalid")
    return value


def registration_manifest(model, prefill_length=512):
    if model not in MODELS:
        raise PaperReportedEnergyRefusal("paper_reported_energy_model_invalid")
    length = _prefill_length(prefill_length)
    return [reported_energy_registration(f"d117-reported-mean-ph-{role}-{model}")
            for role in ("decode", "prefill-p42", f"prefill-p{length}")]


def registration_sha256(model, prefill_length=512):
    return _digest(registration_manifest(model, prefill_length))


def _spec_prefill_length(spec):
    """Read the pack declaration, never infer authority from a reported name.

    Historical specs without a declaration retain the original p512 contract.
    Native floor specs declare the length in each long-prefill family binding;
    a registration-level declaration also supports minimal synthetic specs.
    Every declaration must agree before a manifest can be chosen.
    """
    lengths = []
    registration = spec.get("reported_energy_registration", {})
    if "prefill_prompt_tokens" in registration:
        lengths.append(_prefill_length(registration["prefill_prompt_tokens"]))
    for cell in spec.get("cells", [])[4:6]:
        for binding in cell.get("condition_family_definitions", {}).values():
            length = binding["condition_family_definition"]["workload_profile"]["prompt_tokens"]
            lengths.append(_prefill_length(length))
    if len(set(lengths)) > 1:
        raise PaperReportedEnergyRefusal("paper_reported_energy_cell_census_invalid")
    return lengths[0] if lengths else 512


def verify_registration_ordering(repository, model):
    """Read committed history only; this check grants no evidence custody."""
    source = "joulewise/paper_reported_energy.py"
    spec = f"configs/campaigns/d117_floor_{model}_v5/extraction_spec.json"

    def git(*args):
        result = subprocess.run(["git", "-C", str(repository), *args], capture_output=True, text=True)
        if result.returncode:
            raise PaperReportedEnergyRefusal("paper_reported_energy_ordering_history_invalid")
        return result.stdout.strip()

    try:
        current = json.loads(git("show", f"HEAD:{spec}"))
        length = _spec_prefill_length(current)
        expected = registration_sha256(model, length)
        # Require a complete, unambiguous addition history; never infer dates.
        if git("rev-parse", "--is-shallow-repository") != "false":
            raise PaperReportedEnergyRefusal("paper_reported_energy_ordering_history_invalid")
        additions = [git("log", "--format=%H", "--diff-filter=A", "--no-renames", "HEAD", "--", path).splitlines()
                     for path in (source, spec)]
        if any(len(commits) != 1 for commits in additions):
            raise PaperReportedEnergyRefusal("paper_reported_energy_ordering_history_invalid")
        registration_commit, spec_commit = (commits[0] for commits in additions)
        if length != 512:
            # Ladder roles are prospective: their first registration is the
            # addition of this exact declaration, not the original p512 owner.
            introductions = git("log", "--format=%H", "--reverse", "-S",
                                "PREFILL_LADDER_PROMPT_TOKENS = (512, 1024, 2048, 4096)",
                                "HEAD", "--", source).splitlines()
            if not introductions:
                raise PaperReportedEnergyRefusal("paper_reported_energy_ordering_history_invalid")
            registration_commit = introductions[0]
        ancestor = subprocess.run(["git", "-C", str(repository), "merge-base", "--is-ancestor",
                                   registration_commit, spec_commit], capture_output=True)
        if ancestor.returncode not in (0, 1):
            raise PaperReportedEnergyRefusal("paper_reported_energy_ordering_history_invalid")
        if registration_commit == spec_commit or ancestor.returncode == 1:
            raise PaperReportedEnergyRefusal("paper_reported_energy_registration_not_before_spec")
        # Both the first blob and current frozen blob must bind this registration.
        for revision in (spec_commit, "HEAD"):
            document = json.loads(git("show", f"{revision}:{spec}"))
            if (_spec_prefill_length(document) != length
                or document["reported_energy_registration"]["registration_sha256"] != expected):
                raise PaperReportedEnergyRefusal("paper_reported_energy_registration_digest_mismatch")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        if isinstance(exc, PaperReportedEnergyRefusal):
            raise
        raise PaperReportedEnergyRefusal("paper_reported_energy_ordering_history_invalid") from exc
    return {"registration_commit": registration_commit, "spec_commit": spec_commit,
            "registration_sha256": expected}


@_closed_refusals
def _verify_gate_ordering(repository):
    """Require an ordering result for both models before gate registration/use."""
    for model in MODELS:
        proof = verify_registration_ordering(repository, model)
        if (type(proof) is not dict
            or set(proof) != {"registration_commit", "spec_commit", "registration_sha256"}
            or not proof["registration_commit"] or not proof["spec_commit"]
            or proof["registration_commit"] == proof["spec_commit"]
            or proof["registration_sha256"] not in {
                registration_sha256(model, length) for length in PREFILL_LADDER_PROMPT_TOKENS}):
            raise PaperReportedEnergyRefusal("paper_reported_energy_ordering_history_invalid")


def _validate_registration(value):
    if type(value) is not dict:
        raise PaperReportedEnergyRefusal("paper_reported_energy_registration_invalid")
    if value != reported_energy_registration(value.get("cell_id")):
        raise PaperReportedEnergyRefusal("paper_reported_energy_registration_invalid")
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
        raise PaperReportedEnergyRefusal("paper_reported_energy_cell_registration_mismatch")
    members = cell["members"]
    if type(members) is not list or len(members) != 50:
        raise PaperReportedEnergyRefusal("paper_reported_energy_member_count_invalid")
    ids = []
    for ordinal, member in enumerate(members, 1):
        _exact(member, {"ordinal", "bundle_id", "config_sha256"}, "member")
        if type(member["ordinal"]) is not int or member["ordinal"] != ordinal:
            raise PaperReportedEnergyRefusal("paper_reported_energy_member_order_invalid")
        if type(member["bundle_id"]) is not str or not member["bundle_id"]:
            raise PaperReportedEnergyRefusal("paper_reported_energy_member_identity_invalid")
        _sha(member["config_sha256"], "config_sha256")
        ids.append(member["bundle_id"])
    if len(set(ids)) != 50:
        raise PaperReportedEnergyRefusal("paper_reported_energy_member_duplicate")
    return model, phase


@_closed_refusals
def _validate_registered_spec(spec):
    """Corroborate membership against the independent floor census, in order."""
    from joulewise.floor_extraction import validate_extraction_spec
    errors = validate_extraction_spec(spec)
    if errors:
        raise PaperReportedEnergyRefusal("paper_reported_energy_spec_invalid")
    cells = spec.get("reported_energy_cells")
    if type(cells) is not list or len(cells) != 3:
        raise PaperReportedEnergyRefusal("paper_reported_energy_cell_census_invalid")
    model, _ = _validate_members(cells[0])
    length = _spec_prefill_length(spec)
    if [cell.get("cell_id") for cell in cells] != [r["cell_id"] for r in registration_manifest(model, length)]:
        raise PaperReportedEnergyRefusal("paper_reported_energy_cell_census_invalid")
    if spec.get("reported_energy_registration", {}).get("registration_sha256") != registration_sha256(model, length):
        raise PaperReportedEnergyRefusal("paper_reported_energy_registration_digest_mismatch")
    if len(spec["cells"]) != 6:
        raise PaperReportedEnergyRefusal("paper_reported_energy_floor_census_invalid")
    for index, cell in enumerate(cells):
        _validate_members(cell)
        absolute, comparative = spec["cells"][index * 2:index * 2 + 2]
        role = ("decode", "prefill-p42", f"prefill-p{length}")[index]
        if (absolute["cell_id"] != f"d117-df-ph-{role}-{model}-absolute"
            or comparative["cell_id"] != f"d117-df-cmp-abba-ph-{role}-{model}"):
            raise PaperReportedEnergyRefusal("paper_reported_energy_floor_identity_mismatch")
        if (absolute["kind"] != "absolute" or comparative["kind"] != "comparative"
            or type(absolute["expected_n"]) is not int or absolute["expected_n"] != 10
            or type(comparative["expected_n"]) is not int or comparative["expected_n"] != 10
            or len(absolute["members"]) != 10 or len(comparative["blocks"]) != 10
            or absolute["metric"] != cell["metric"] or comparative["metric"] != cell["metric"]):
            raise PaperReportedEnergyRefusal("paper_reported_energy_floor_stratum_mismatch")
        ordered = [row["bundle_id"] for row in absolute["members"]]
        ordered += [block["members"][position] for block in comparative["blocks"]
                    for position in ("A1", "B1", "B2", "A2")]
        pins = absolute["member_config_sha256"] + comparative["member_config_sha256"]
        if ([row["bundle_id"] for row in cell["members"]] != ordered
            or [{k: row[k] for k in ("bundle_id", "config_sha256")} for row in cell["members"]] != pins):
            raise PaperReportedEnergyRefusal("paper_reported_energy_floor_member_mismatch")


def _collapse_prompt_tokens(value):
    """Collapse bundle_read's four prompt surfaces to one agreed integer."""
    counts = [value.get("prompt_realized")]
    for name in ("tokenize_end", "prefill_start"):
        surface = value.get(name)
        if type(surface) in (tuple, list):
            if not surface:
                raise PaperReportedEnergyRefusal("paper_reported_energy_denominator_invalid")
            counts.extend(surface)
        else:
            counts.append(surface)
    total, output = value.get("total"), value.get("output")
    if any(type(n) is not int or n < 0 for n in (total, output, *counts)):
        raise PaperReportedEnergyRefusal("paper_reported_energy_denominator_invalid")
    prompt = total - output
    if prompt <= 0:
        raise PaperReportedEnergyRefusal("paper_reported_energy_denominator_invalid")
    if any(n != prompt for n in counts):
        raise PaperReportedEnergyRefusal("paper_reported_energy_prompt_surfaces_disagree")
    return prompt


def _observed_tokens(row, phase):
    value = row["tokens"]
    required = {"source", "output", "tokenizer_sha256", "output_policy_sha256"}
    prompt_keys = {"total", "prompt_realized", "tokenize_end", "prefill_start"}
    if (type(value) is not dict or not required <= value.keys()
        or not value.keys() <= required | prompt_keys or value["source"] != "runtime_observed"):
        raise PaperReportedEnergyRefusal("paper_reported_energy_denominator_invalid")
    for name in ("tokenizer_sha256", "output_policy_sha256"):
        _sha(value[name], name)
    denominator = value["output"] if phase == "decode" else _collapse_prompt_tokens(value)
    if type(denominator) is not int or denominator <= 0:
        raise PaperReportedEnergyRefusal("paper_reported_energy_denominator_invalid")
    return denominator



@dataclass(frozen=True)
class CellEstimate:
    mean_j: float
    lower_j: float
    upper_j: float
    n_r: int
    n_b: int
    df: int
    s_r: float
    s_b: float
    variance: float
    h_j: float
    kind_averages_j: Mapping[str, float]
    B_j: float
    per_token: Mapping
    attribution_floor: Mapping
    below_minimum: bool


def _kept_ordinals(kept):
    if not isinstance(kept, ReportedCellKept):
        raise PaperReportedEnergyRefusal("paper_reported_energy_request_invalid")
    repeats = tuple(range(1, 11))
    quads = tuple(tuple(range(i, i + 4)) for i in range(11, 51, 4))
    for yes, no, universe in (
        (kept.kept_repeat_ordinals, kept.removed_repeat_ordinals, repeats),
        (kept.kept_quad_ordinals, kept.removed_quad_ordinals, quads),
    ):
        if (type(yes) is not tuple or type(no) is not tuple
            or any(type(x) is not int for x in (yes + no) if universe is repeats)
            or any(type(x) is not tuple or any(type(n) is not int for n in x)
                   for x in (yes + no) if universe is quads)
            or tuple(sorted(yes)) != yes or tuple(sorted(no)) != no
            or len(yes + no) != len(universe) or len(set(yes + no)) != len(universe) or set(yes + no) != set(universe)):
            raise PaperReportedEnergyRefusal("paper_reported_energy_request_invalid")
    return kept.kept_repeat_ordinals + tuple(n for q in kept.kept_quad_ordinals for n in q)


@_closed_refusals
def estimate_reported_cell(rows: Sequence[Mapping], kept: ReportedCellKept, *,
                           minimum: int | None = 5) -> CellEstimate:
    ordinals = _kept_ordinals(kept)
    if (not isinstance(rows, Sequence) or isinstance(rows, (str, bytes))
        or tuple(row["member"]["ordinal"] for row in rows) != ordinals):
        raise PaperReportedEnergyRefusal("paper_reported_energy_member_count_invalid")
    if minimum is not None and (type(minimum) is not int or minimum != 5):
        raise PaperReportedEnergyRefusal("paper_reported_energy_request_invalid")
    n_r, n_b = len(kept.kept_repeat_ordinals), len(kept.kept_quad_ordinals)
    if min(n_r, n_b) < (2 if minimum is None else 5):
        raise PaperReportedEnergyRefusal("paper_reported_energy_kept_units_below_minimum")
    energies = [_number(row["energy_j"], "energy_j", nonnegative=True) for row in rows]
    r, q = energies[:n_r], energies[n_r:]
    b = [statistics.fmean(q[i:i + 4]) for i in range(0, len(q), 4)]
    full = n_r == n_b == 10
    mean = statistics.fmean(energies) if full else 0.2 * statistics.fmean(r) + 0.8 * statistics.fmean(b)
    s_r, s_b = statistics.stdev(r), statistics.stdev(b)
    variance = 0.2 ** 2 * s_r ** 2 / n_r + 0.8 ** 2 * s_b ** 2 / n_b
    df = min(n_r, n_b) - 1
    half = T975[df] * math.sqrt(variance)
    for row in rows:
        _exact(row["bounds_j"], BOUND_KINDS, "bounds_j")
    terms = {}
    for kind in BOUND_KINDS:
        values = [_number(row["bounds_j"][kind], kind, nonnegative=True) for row in rows]
        terms[kind] = (statistics.fmean(values) if full else
                       0.2 * statistics.fmean(values[:n_r]) + 0.8 * statistics.fmean(values[n_r:]))
    bound = math.fsum(terms.values())
    token_error, token_scope, counts = None, None, []
    for row in rows:
        try:
            counts.append(_observed_tokens(row, row["phase"]))
            scope = tuple(row["tokens"][key] for key in ("tokenizer_sha256", "output_policy_sha256"))
            if token_scope is not None and token_scope != scope:
                raise PaperReportedEnergyRefusal("paper_reported_energy_token_scope_mismatch")
            token_scope = scope
        except PaperReportedEnergyRefusal as exc:
            token_error = exc.code
    # Any denominator refusal nulls the sibling, leaving the energy estimator intact.
    sums = {"repeat": {"energy_sum_j": math.fsum(r), "observed_token_sum": None if token_error else sum(counts[:n_r])},
            "quad": {"energy_sum_j": math.fsum(q), "observed_token_sum": None if token_error else sum(counts[n_r:])}}
    ratio = None if token_error else (math.fsum(energies) / sum(counts) if full else
            0.2 * (math.fsum(r) / sum(counts[:n_r])) + 0.8 * (math.fsum(q) / sum(counts[n_r:])))
    per_token = {"status": "refused" if token_error else "computed", "energy_sum_j": math.fsum(energies),
                 "observed_token_sum": None if token_error else sum(counts), "j_per_token": ratio,
                 "reason": token_error, "strata": sums}
    first = [row["bounds_j"][BOUND_KINDS[0]] for row in rows]
    largest = max(first)
    floor = {"value_j": largest, "attained_by": rows[first.index(largest)]["member"]["bundle_id"],
             "minimum_j": min(first)}
    return CellEstimate(mean, mean - half - bound, mean + half + bound, n_r, n_b, df,
                        s_r, s_b, variance, half, terms, bound, per_token, floor, min(n_r, n_b) < 5)


def _reported_unit_records(kept, removed):
    cell = kept.cell
    all_units = [u for units in cell.kept.values() for u in units] + list(cell.dropped)
    dropped = {(u.stratum, u.unit_id) for u in cell.dropped}
    result = []
    for stratum in ("repeat", "quad"):
        units = sorted((u for u in all_units if u.stratum == stratum), key=lambda u: u.positions)
        if len(units) != 10:
            raise PaperReportedEnergyRefusal("paper_reported_energy_request_invalid")
        for i, unit in enumerate(units):
            ordinals = [i + 1] if stratum == "repeat" else list(range(11 + i * 4, 15 + i * 4))
            if ((stratum, unit.unit_id) in dropped) == removed:
                result.append({"stratum": stratum, "unit_id": unit.unit_id, "ordinals": ordinals})
    return result


def _project_kept_cell(cell, rows, binding, kept, exclusions_sha256, minimum):
    ordinals = _kept_ordinals(kept)
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)):
        raise PaperReportedEnergyRefusal("paper_reported_energy_member_count_invalid")
    for row in rows:
        _exact(row, {"member", "model", "phase", "selection_sha256", "prompt_pin_sha256",
                     "whole_window_basis_sha256", "strict_valid", "unit", "energy_j", "bounds_j", "tokens"}, "record")
        member = row["member"]
        ordinal = member.get("ordinal") if type(member) is dict else None
        if (type(ordinal) is not int or not 1 <= ordinal <= 50
            or member != cell["members"][ordinal - 1]):
            raise PaperReportedEnergyRefusal("paper_reported_energy_record_identity_mismatch")
    if tuple(row["member"]["ordinal"] for row in rows) != ordinals:
        raise PaperReportedEnergyRefusal("paper_reported_energy_member_count_invalid")
    model, phase = _cell_identity(cell["cell_id"])
    for row, ordinal in zip(rows, ordinals):
        if (row["member"] != cell["members"][ordinal - 1] or row["model"] != model or row["phase"] != phase
            or any(row[name] != binding[name] for name in ("selection_sha256", "prompt_pin_sha256", "whole_window_basis_sha256"))):
            raise PaperReportedEnergyRefusal("paper_reported_energy_record_identity_mismatch")
        index = ordinal - 1
        unit = ({"kind": "repeat", "index": ordinal, "position": None} if ordinal <= 10 else
                {"kind": "abba", "index": (index - 10) // 4 + 1, "position": ("A1", "B1", "B2", "A2")[(index - 10) % 4]})
        if row["strict_valid"] is not True or row["unit"] != unit or type(row["unit"]["index"]) is not int:
            raise PaperReportedEnergyRefusal("paper_reported_energy_record_invalid")
    estimate = estimate_reported_cell(rows, kept, minimum=minimum)
    if binding["attribution_floor_j"] != estimate.attribution_floor["value_j"]:
        raise PaperReportedEnergyRefusal("paper_reported_energy_binding_mismatch")
    result = {"cell_id": cell["cell_id"], "model": model, "phase": phase, "members": cell["members"],
              "mean_j": estimate.mean_j, "lower_j": estimate.lower_j, "upper_j": estimate.upper_j,
              "n_bundles": estimate.n_r + 4 * estimate.n_b, "independence_units": estimate.n_r + estimate.n_b,
              "interval": {"method": INTERVAL_METHOD, **{k: getattr(estimate, k) for k in
                           ("n_r", "n_b", "df", "s_r", "s_b", "variance", "h_j", "kind_averages_j", "B_j")}},
              "phase_ratio_estimand": cell["phase_ratio_estimand"], "per_token": dict(estimate.per_token),
              "binding": dict(binding), "attribution_floor_composed": False,
              "kept_units": _reported_unit_records(kept, False), "removed_units": _reported_unit_records(kept, True),
              "exclusions_sha256": exclusions_sha256, "attribution_floor": dict(estimate.attribution_floor)}
    if estimate.below_minimum:
        result["below_minimum"] = True
    json.dumps(result, allow_nan=False)
    return result


@_closed_refusals
def _project_cell(cell, rows, binding, *, kept=None, exclusions_sha256=None, minimum=5):
    """Private normalized arithmetic kernel, never an evidence admission API."""
    model, phase = _validate_members(cell)
    _exact(binding, {"model", "cell_id", "extraction_spec_sha256", "selection_sha256",
                     "prompt_pin_sha256", "whole_window_basis_sha256", "attribution_floor_j"}, "binding")
    if binding["model"] != model or binding["cell_id"] != cell["cell_id"]:
        raise PaperReportedEnergyRefusal("paper_reported_energy_binding_mismatch")
    for name in ("extraction_spec_sha256", "selection_sha256", "prompt_pin_sha256", "whole_window_basis_sha256"):
        _sha(binding[name], name)
    _number(binding["attribution_floor_j"], "attribution_floor_j", nonnegative=True)
    if kept is not None:
        if type(exclusions_sha256) is not str or SHA_RE.fullmatch(exclusions_sha256) is None:
            raise PaperReportedEnergyRefusal("paper_reported_energy_request_invalid")
        return _project_kept_cell(cell, rows, binding, kept, exclusions_sha256, minimum)
    if exclusions_sha256 is not None:
        raise PaperReportedEnergyRefusal("paper_reported_energy_request_invalid")
    if type(rows) is not list or len(rows) != 50:
        raise PaperReportedEnergyRefusal("paper_reported_energy_member_count_invalid")
    energy, bounds, tokens = [], {kind: [] for kind in BOUND_KINDS}, []
    token_error = None
    token_scope = None
    for index, (member, row) in enumerate(zip(cell["members"], rows)):
        _exact(row, {"member", "model", "phase", "selection_sha256", "prompt_pin_sha256",
                     "whole_window_basis_sha256", "strict_valid", "unit", "energy_j", "bounds_j", "tokens"}, "record")
        if (row["member"] != member or row["model"] != model or row["phase"] != phase
            or any(row[name] != binding[name] for name in ("selection_sha256", "prompt_pin_sha256", "whole_window_basis_sha256"))):
            raise PaperReportedEnergyRefusal("paper_reported_energy_record_identity_mismatch")
        expected_unit = {"kind": "repeat", "index": index + 1, "position": None} if index < 10 else {
            "kind": "abba", "index": (index - 10) // 4 + 1, "position": ("A1", "B1", "B2", "A2")[(index - 10) % 4]}
        if (row["strict_valid"] is not True or row["unit"] != expected_unit
            or type(row["unit"]["index"]) is not int):
            raise PaperReportedEnergyRefusal("paper_reported_energy_record_invalid")
        energy.append(_number(row["energy_j"], "energy_j", nonnegative=True))
        _exact(row["bounds_j"], BOUND_KINDS, "bounds_j (prediction term forbidden)")
        for kind in BOUND_KINDS:
            bounds[kind].append(_number(row["bounds_j"][kind], kind, nonnegative=True))
        try:
            tokens.append(_observed_tokens(row, phase))
            scope = tuple(row["tokens"][key] for key in ("tokenizer_sha256", "output_policy_sha256"))
            if token_scope is not None and token_scope != scope:
                raise PaperReportedEnergyRefusal("paper_reported_energy_token_scope_mismatch")
            token_scope = scope
        except PaperReportedEnergyRefusal as exc:
            token_error = exc.code
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
        "upper_j": mean + half + bound, "n_bundles": cell["projection_registration"]["expected_n"], "independence_units": 20,
        "interval": {"method": INTERVAL_METHOD, "n_r": 10, "n_b": 10, "df": 9,
                     "s_r": s_r, "s_b": s_b, "variance": variance, "h_j": half,
                     "kind_averages_j": terms, "B_j": bound},
        "phase_ratio_estimand": cell["phase_ratio_estimand"],
        "per_token": {"status": "refused" if token_error else "computed",
                      "energy_sum_j": math.fsum(energy),
                      "observed_token_sum": None if token_error else sum(tokens),
                      "j_per_token": None if token_error else math.fsum(energy) / sum(tokens),
                      "reason": token_error},
        "binding": dict(binding), "attribution_floor_composed": False,
    }
    # Reject overflow in intermediate arithmetic, including otherwise plausible endpoints.
    json.dumps(result, allow_nan=False)
    return result


@_closed_refusals
def _validate_projection(projection, cell, rows, binding):
    expected = _project_cell(cell, rows, binding)
    if type(projection) is not dict or _digest(projection) != _digest(expected):
        raise PaperReportedEnergyRefusal("paper_reported_energy_projection_mismatch")


@_closed_refusals
def _synthetic_projection(documents):
    """Called only inside D-173 fixture replay. No production dispatch exists."""
    _exact(documents, {"spec", "cells"}, "synthetic projection input")
    _validate_registered_spec(documents["spec"])
    cells = documents["cells"]
    if type(cells) is not list or len(cells) != 3:
        raise PaperReportedEnergyRefusal("paper_reported_energy_cell_census_invalid")
    results = []
    for cell, data in zip(documents["spec"]["reported_energy_cells"], cells):
        _exact(data, {"rows", "binding"}, "synthetic cell")
        if data["binding"]["extraction_spec_sha256"] != _digest(documents["spec"]):
            raise PaperReportedEnergyRefusal("paper_reported_energy_spec_binding_mismatch")
        results.append(_project_cell(cell, data["rows"], data["binding"]))
    return {"schema_version": SCHEMA, "mode": "test_fixture_non_issuing", "cells": results}


__all__ = ["phase_ratio_estimand", "validate_phase_ratio_estimand", "reported_energy_registration",
           "registration_manifest", "registration_sha256", "verify_registration_ordering",
           "PaperReportedEnergyRefusal", "PAPER_REPORTED_ENERGY_REFUSAL_CODES"]
