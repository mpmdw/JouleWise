#!/usr/bin/env python3
"""Compare L9's block-5 dry-run restricted outputs with the independent recompute.

Standard library only; imports no repository code, in particular none of L9's analysis package.
Inputs: L9's dry-run custody root (its record and restricted folder), the
recompute's --member-detail output, a bar-set config (default: block 5's release
set, configs/analysis/b5/recompute_bars.json), and, for each window whose
disclosure carries the whole-machine line, the harvest's withheld meter record
(--harvest-meter PACK=PATH). No bar is coded here: every numeric family's bar
comes from the config, and a family the config does not name refuses the run
(the meter families when a meter line is compared).

Rules (RC-CMP-1 A1-A4):
- numeric families pass when both sides are finite numbers within the family bar;
- categorical families (outcome words, dominance branch, p42 status, Holm order,
  the recompute's exclusion re-derivation) pass only on equal type and value;
- a value missing or null on either side is DISAGREE; each family compares the
  union of L9's items and the recompute's, so an item on one side only is
  DISAGREE (RC-CMP-3 X3);
- the whole-machine meter line (RC-CMP-2 M4): per member of the union of L9's
  disclosure, the recompute's windows and the harvest meter record, the
  disclosure's rho, dE_rail and dE_machine, and the record's gross meter energy,
  baseline power, battery term, sample counts and window, against the
  recompute's request phase; a disclosed window with no record is DISAGREE; the
  per-model order statistics and central band are re-derived from the
  recompute's member values (RC-CMP-3 X2);
- every leaf of the step-11 outputs (fill input and disclosure record) must match
  a coverage rule. A family rule names the comparison row the leaf copies, and
  the leaf is covered only if that row exists, its L9 value equals the leaf in
  type and value, and the row is AGREE (RC-CMP-3 X1). An "uncovered:" rule
  matches non-numeric leaves only; a numeric leaf is uncovered only by an
  "uncovered-by-name:" rule, and every such leaf is listed (X6). Any other leaf
  refuses the run;
- a NaN or Infinity in an input becomes null with a structure flag (X7);
- stdout carries per-family pass/fail counts and structure codes only; values and
  observed differences go only to the restricted output file, which is written
  whenever the inputs could be read.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import statistics
import sys

SCHEMA = "joulewise.b5_recompute_comparison.v1"
BARS_SCHEMA = "joulewise.b5_comparator_bars.v1"
RECORD = "dry-run/B5-BLIND-DRY-RUN-RECORD.json"
RESTRICTED = "dry-run/restricted"
PACKS = {"alpha": "ALPHA", "beta": "BETA", "gamma": "GAMMA"}
MODELS = {"alpha": "Qwen3-1.7B-4bit", "beta": "Qwen3-8B-4bit"}
NUMERIC = ("run_phase_energy_j", "floor_j", "floor_gate_j", "dominance_ratio", "reported_cell_j",
           "contrast_j", "contrast_p", "descriptive_ratio", "per_token_j", "b_op_s", "count")
# The whole-machine meter line; required of a bar set only when a meter line is compared.
METER = ("meter_j", "meter_w", "machine_j", "rho", "window_edge_s")
CATEGORICAL = ("outcome_word", "dominance_branch", "p42_status", "holm_order", "kept_units", "exclusions_rederivation",
               "battery_term")
DEFAULT_BARS = Path(__file__).resolve().parents[1] / "configs/analysis/b5/recompute_bars.json"


class Refusal(Exception):
    """A structure-only reason the comparison cannot be evaluated."""


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


MISSING = object()


def same(a, b):
    """Equal type and value, recursively (True, 1 and 1.0 differ)."""
    if type(a) is not type(b):
        return False
    if isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    return a == b


def get(obj, *keys, default=None):
    for key in keys:
        if isinstance(obj, dict) and key in obj:
            obj = obj[key]
        elif isinstance(obj, list) and isinstance(key, int) and -len(obj) <= key < len(obj):
            obj = obj[key]
        else:
            return default
    return obj


def bar_spec_valid(spec):
    """A family bar or a per-key override: finite non-negative bars, a non-negative int precision."""
    for key in ("absolute", "relative"):
        if key in spec and (not finite(spec[key]) or spec[key] < 0):
            return False
    if "printed_decimals" in spec and (type(spec["printed_decimals"]) is not int or spec["printed_decimals"] < 0):
        return False
    return bool({"absolute", "relative", "printed_decimals"} & set(spec))


def load_bars(path):
    try:
        bars = json.loads(Path(path).read_bytes())
    except (OSError, ValueError):
        raise Refusal("bars_unreadable") from None
    if not isinstance(bars, dict) or bars.get("schema") != BARS_SCHEMA or not isinstance(bars.get("families"), dict):
        raise Refusal("bars_invalid")
    for family in NUMERIC + METER:
        spec = bars["families"].get(family)
        if spec is None and family in METER:
            continue
        if not isinstance(spec, dict):
            raise Refusal("bars_family_missing:" + family)
        if not bar_spec_valid(spec) or not isinstance(spec.get("keys", []), list):
            raise Refusal("bars_invalid:" + family)
        for override in spec.get("keys", []):
            # A per-key override is a bar like the family's (RC-CMP-3 X5).
            if not isinstance(override, dict) or not isinstance(override.get("match"), str) or not bar_spec_valid(override):
                raise Refusal("bars_invalid:" + family)
            try:
                re.compile(override["match"])
            except re.error:
                raise Refusal("bars_invalid:" + family) from None
    return bars


def family_spec(spec, key):
    """A family's bar, or the first per-key override whose pattern matches the key (a field printed at its own precision)."""
    return next((o for o in spec.get("keys", []) if re.fullmatch(o["match"], key)), spec)


def bar_for(spec, reference):
    parts = [spec.get("absolute", 0.0), spec.get("relative", 0.0) * abs(reference)]
    if "printed_decimals" in spec:
        parts.append(0.5 * 10.0 ** -spec["printed_decimals"])
    return max(parts)


class Comparison:
    def __init__(self, bars):
        self.bars, self.rows = bars, []

    def numeric(self, family, key, l9, ours):
        assert family in NUMERIC + METER, family
        if family not in self.bars["families"]:
            raise Refusal("bars_family_missing:" + family)
        row = {"family": family, "key": key, "l9": l9, "recompute": ours}
        if finite(l9) and finite(ours):
            row["difference"] = ours - l9
            row["bar"] = bar_for(family_spec(self.bars["families"][family], key), l9)
            row["verdict"] = "AGREE" if abs(ours - l9) <= row["bar"] else "DISAGREE"
        else:
            row["verdict"], row["reason"] = "DISAGREE", "missing_or_null"
        self.rows.append(row)
        return row

    def exact(self, family, key, l9, ours, raw=MISSING):
        """Equal type and value. raw: the L9 value as printed, when the compared word is derived from it."""
        assert family in CATEGORICAL, family
        missing = l9 is None or ours is None
        row = {"family": family, "key": key, "l9": l9, "recompute": ours,
               "verdict": "AGREE" if not missing and same(l9, ours) else "DISAGREE"}
        if raw is not MISSING:
            row["l9_raw"] = raw
        if missing:
            row["reason"] = "missing_or_null"
        self.rows.append(row)
        return row

    def keys(self):
        return {(row["family"], row["key"]) for row in self.rows}

    def counts(self):
        counts = {family: {"pass": 0, "fail": 0} for family in NUMERIC + METER + CATEGORICAL
                  if family not in METER or family in self.bars["families"]}
        for row in self.rows:
            counts[row["family"]]["pass" if row["verdict"] == "AGREE" else "fail"] += 1
        return counts


def loads(raw, flags, source):
    """JSON with NaN and Infinity read as null; each such file is flagged (RC-CMP-3 X7)."""
    seen = []

    def nonfinite(word):
        seen.append(word)
        return None
    value = json.loads(raw, parse_constant=nonfinite)
    flag = {"code": "nonfinite_value_read_as_null", "source": source, "count": len(seen)}
    if seen and flag not in flags:
        flags.append(flag)
    return value


class Custody:
    """L9's dry-run custody: every file used must be listed in the record with its digest."""
    def __init__(self, root, flags=None):
        self.root = Path(root)
        self.restricted = self.root / RESTRICTED
        self.flags = [] if flags is None else flags
        try:
            self.record = json.loads((self.root / RECORD).read_bytes())
        except (OSError, ValueError):
            raise Refusal("l9_record_unreadable") from None
        self.listed, self.status = {}, {}
        for row in self.record.get("steps", []):
            key = (row.get("step"), row.get("window"))
            self.status[key] = row.get("status")
            for output in row.get("outputs", []):
                self.listed[output["name"]] = output["sha256"]

    def step_ok(self, step, window=None):
        return self.status.get((step, window)) == "ok"

    def names(self, pattern):
        return sorted(name for name in self.listed if re.fullmatch(pattern, name))

    def read(self, name):
        if name not in self.listed:
            raise Refusal("l9_output_unlisted")
        try:
            raw = (self.restricted / name).read_bytes()
        except OSError:
            raise Refusal("l9_output_unreadable") from None
        if hashlib.sha256(raw).hexdigest() != self.listed[name]:
            raise Refusal("l9_output_digest_differs")
        try:
            return loads(raw, self.flags, "l9:" + name)
        except ValueError:
            raise Refusal("l9_output_unreadable") from None

    def one(self, pattern):
        names = self.names(pattern)
        if len(names) > 1:
            raise Refusal("l9_output_ambiguous")
        return self.read(names[0]) if names else None


def items(value, keep=lambda key, item: True):
    """The recompute's computed items of a keyed section: dict entries whose status, if any, is computed.

    A not-computed section (missing_pack) is a dict of words and has no items.
    """
    if not isinstance(value, dict):
        return {}
    return {key: item for key, item in value.items() if isinstance(item, dict)
            and item.get("status", "computed") == "computed" and keep(key, item)}


def union(l9_keys, our_keys):
    return sorted(set(l9_keys) | set(our_keys), key=str)


def compare_runs(c, custody, ours):
    """S-13's per-run term: each kept run's phase energies (and gross request energy).

    The key set is the union of L9's re-reduced runs and the recompute's selected
    (kept) runs; a member detail without the selected field counts as selected.
    """
    members = ours.get("members")
    if not isinstance(members, dict):
        raise Refusal("recompute_member_detail_missing")
    named = {}
    for name in custody.names(r"rereduced/(alpha|beta|gamma)/[^/]+\.rereduced\.json"):
        pack, file = name.split("/")[1:]
        named[(pack, file[:-len(".rereduced.json")])] = name
    selected = {(pack, rid) for pack, PACK in PACKS.items() for rid, m in (get(members, PACK) or {}).items()
                if isinstance(m, dict) and m.get("selected", True) is True}
    for pack, rid in union(named, selected):
        l9 = custody.read(named[(pack, rid)]) if (pack, rid) in named else {}
        mine = get(members, PACKS[pack], rid, "E_j", default={})
        for phase in ("prefill", "decode"):
            c.numeric("run_phase_energy_j", pack + "/" + rid + "/" + phase,
                      get(l9, "phase_energy_j", phase), get(mine, phase))
        c.numeric("run_phase_energy_j", pack + "/" + rid + "/request", get(l9, "gross_energy_j"), get(mine, "request"))


# L9 extraction floor field -> recompute floor field (same definitions, different names).
FLOOR_FIELDS = {"corner_widened_unguarded_floor_j": "corner_widened_unguarded_floor_j",
                "unguarded_floor_j": "operative_unguarded_floor_j", "guarded_floor_j": "guarded_floor_j",
                "drift_widened_guarded_floor_j": "drift_widened_guarded_floor_j",
                "prediction_component_j": "prediction_j", "max_abs_deviation_j": "max_abs_deviation_j",
                "sample_stddev_j": "s_j", "whole_window_drift_allowance_j": "allowance_j", "guard_factor": "guard"}


def plus(a, b):
    return a + b if finite(a) and finite(b) else None


def times(a, b):
    return a * b if finite(a) and finite(b) else None


def tag(pack):
    return "qwen3-1p7b" if pack == "alpha" else "qwen3-8b"


def cell_phase(cell_id):
    return "decode" if "decode" in cell_id else "prefill"


def cell_model(cell_id):
    cell_id = str(cell_id)
    return MODELS["alpha"] if "qwen3-1p7b" in cell_id else MODELS["beta"] if "qwen3-8b" in cell_id else None


def floor_kind(cell_id):
    return next((kind for kind in ("absolute", "comparative") if str(cell_id).endswith("-" + kind)), None)


def compare_floors(c, custody, ours):
    for pack in ("alpha", "beta"):
        report = custody.one(r"mint/[0-9a-f]{64}-extraction-" + pack + r"\.json")
        if report is None:
            c.exact("p42_status", pack + "/extraction", None, get(ours, "p42", "df-ph-prefill-p42-" + tag(pack), "status"))
        l9_cells = {}
        for cell in (report or {}).get("cells", []):
            cid, kind = cell.get("cell_id"), cell.get("kind")
            if "p42" in cid:
                # Registered p42 exit: the p42 floor cells are not extractable (step 4 p42_floor_cells_only).
                l9 = "expected_unresolvable" if cell.get("extractable") is False else "extractable"
                c.exact("p42_status", pack + "/" + cid, l9, get(ours, "p42", "df-ph-prefill-p42-" + tag(pack), "status"))
                continue
            l9_cells[MODELS[pack] + "/" + cell_phase(cid) + "/" + str(kind)] = cell
        mine_cells = items(ours.get("floors"), lambda key, _: key.startswith(MODELS[pack] + "/"))
        for key in union(l9_cells, mine_cells):
            cell = l9_cells.get(key, {})
            mine = mine_cells.get(key) or get(ours, "floors", key, default={}) or {}
            floor = cell.get("floor") or {}
            for field, other in FLOOR_FIELDS.items():
                c.numeric("floor_j", key + "/" + field, floor.get(field), mine.get(other))
            c.numeric("floor_j", key + "/operative_floor_j", cell.get("operative_floor_j"),
                      mine.get("drift_widened_guarded_floor_j"))
            # Two L9 fields the recompute composes from its own terms.
            c.numeric("floor_j", key + "/corner_widened_guarded_floor_j", floor.get("corner_widened_guarded_floor_j"),
                      times(mine.get("guard"), mine.get("corner_widened_unguarded_floor_j")))
            c.numeric("floor_j", key + "/drift_widened_unguarded_floor_j", floor.get("drift_widened_unguarded_floor_j"),
                      plus(mine.get("operative_unguarded_floor_j"), mine.get("allowance_j")))
            c.numeric("count", key + "/n", floor.get("n"), mine.get("n"))
            c.numeric("count", key + "/n_admitted", cell.get("n_admitted"), mine.get("n"))


def floor_cell_key(cell_id):
    """d117-qwen3-1p7b-prefill-p2048-floor-v5 -> (model, phase)."""
    return cell_model(cell_id), cell_phase(cell_id)


def compare_aggregate(c, custody, ours):
    floor = custody.one(r"mint/[0-9a-f]{64}-aggregate-floor\.json")
    l9_cells = {"/".join(map(str, floor_cell_key(cell.get("cell_id", "")))): cell for cell in (floor or {}).get("cells", [])}
    mine_cells = items(ours.get("floor_cells"))
    for key in union(l9_cells, mine_cells):
        cell, mine = l9_cells.get(key, {}), mine_cells.get(key) or {}
        for field in ("floor_abs_j", "floor_cmp_j", "floor_gate_j"):
            c.numeric("floor_gate_j", key + "/" + field, cell.get(field), mine.get(field))
    if floor is None:
        c.numeric("floor_gate_j", "aggregate_floor", None, None)
    closeout = custody.one(r"finalized/outputs/closeout\.json")
    ratios = custody.one(r"finalized/outputs/closeout\.ratio-table\.json")
    c.exact("dominance_branch", "branch", get(closeout, "branch"), get(ours, "dominance", "branch"))
    l9_rows = {}
    for row in get(ratios, "ratios", default=[]) or []:
        model, phase = floor_cell_key(row.get("cell_id", ""))
        common = str(row.get("numerator_field", "")).startswith("common_mode")
        l9_rows[f"{model}/{phase}/{row.get('component')}" + ("/common_mode" if common else "")] = row
    mine_rows = {key: item for key, item in items(get(ours, "dominance", "ratios")).items()}
    mine_rows.update({key + "/comparative/common_mode": item
                      for key, item in items(get(ours, "dominance", "common_mode")).items()})
    if not l9_rows and not mine_rows:
        l9_rows["None/prefill/None"] = {}
    for label in union(l9_rows, mine_rows):
        row = l9_rows.get(label, {})
        common = label.endswith("/common_mode")
        key = label[:-len("/common_mode")] if common else label
        mine = get(ours, "dominance", "common_mode" if common else "ratios",
                   key.rsplit("/", 1)[0] if common else key, default={}) or {}
        c.numeric("dominance_ratio", label + "/ratio", row.get("ratio"), mine.get("R_cm" if common else "R"))
        c.numeric("floor_j", label + "/numerator_j", row.get("numerator_j"), mine.get("numerator_j"))
        c.numeric("floor_j", label + "/denominator_j", row.get("denominator_j"), mine.get("denominator_j"))
        c.numeric("count", label + "/n", row.get("n"), mine.get("n"))


def interval(value):
    if isinstance(value, dict):
        return [value.get("lower"), value.get("upper")]
    return list(value) if isinstance(value, list) and len(value) == 2 else [None, None]


def holm_order(rows):
    """Contrast ids by raw p, ties by id; None when any p is missing."""
    if not rows or any(not finite(p) for p in rows.values()):
        return None
    return [cid for cid, _ in sorted(rows.items(), key=lambda item: (item[1], item[0]))]


def contrast_floor_part(cells, cid, field):
    """A contrast's floor_abs_j or floor_cmp_j: the larger of its two models' cells (max, never sum)."""
    phase = cell_phase(cid)
    values = [get(cells, model + "/" + phase, field) for model in MODELS.values()]
    return max(values) if all(finite(v) for v in values) else None


def loo_key(block_id):
    """An omitted block id ...-b03 -> b03, the recompute's block numbering."""
    match = re.search(r"(?:^|-)b(\d+)$", str(block_id))
    return "b%02d" % int(match[1]) if match else None


def compare_contrasts(c, custody, ours):
    verdicts = custody.one(r"outputs/[0-9a-f]{64}-claim-verdicts\.json")
    mine_all = items(ours.get("contrasts"))
    l9_rows = {row.get("contrast_id"): row for row in get(verdicts, "contrasts", default=[]) or []}
    if not l9_rows and not mine_all:
        l9_rows[None] = {}
    l9_p, our_p = {}, {}
    for cid in union(l9_rows, mine_all):
        row = l9_rows.get(cid, {})
        mine = mine_all.get(cid) or {}
        est = row.get("estimator") or {}
        c.numeric("contrast_j", f"{cid}/dbar_j", est.get("estimate"), mine.get("dbar_j"))
        c.numeric("contrast_j", f"{cid}/s_d_j", est.get("s_d"), mine.get("s_d_j"))
        c.numeric("contrast_j", f"{cid}/se_j", est.get("SE_total"), mine.get("se_j"))
        c.numeric("contrast_p", f"{cid}/t_critical", est.get("t_critical_95"), mine.get("t_star"))
        for side, (a, b) in zip(("lower", "upper"), zip(interval(est.get("metrology_aware_CI95")),
                                                          interval(mine.get("metrology_interval_j")))):
            c.numeric("contrast_j", f"{cid}/metrology_interval_j/{side}", a, b)
        bounds = row.get("deterministic_bounds") or {}
        c.numeric("contrast_j", f"{cid}/D_j", bounds.get("total"), mine.get("D_j"))
        for side, (a, b) in zip(("lower", "upper"), zip(interval(bounds.get("decision_interval")),
                                                          interval(mine.get("decision_interval_j")))):
            c.numeric("contrast_j", f"{cid}/decision_interval_j/{side}", a, b)
        c.numeric("floor_gate_j", f"{cid}/active_floor_j", get(row, "floor", "active_floor_j"), mine.get("floor_gate_j"))
        for field in ("floor_abs_j", "floor_cmp_j"):
            c.numeric("floor_gate_j", f"{cid}/{field}", get(row, "floor", field),
                      contrast_floor_part(ours.get("floor_cells"), str(cid), field))
        multiplicity = row.get("multiplicity") or {}
        c.numeric("contrast_p", f"{cid}/raw_p", multiplicity.get("raw_p"), mine.get("p"))
        c.numeric("contrast_p", f"{cid}/adjusted_p", multiplicity.get("adjusted_p"), mine.get("holm_p"))
        c.exact("outcome_word", f"{cid}/holm_reject", multiplicity.get("rejected"), mine.get("holm_reject"))
        c.numeric("count", f"{cid}/n", est.get("n"), mine.get("n"))
        c.numeric("count", f"{cid}/df", est.get("df"), mine["n"] - 1 if finite(mine.get("n")) else None)
        blocks = get(row, "bundle_blocks", "blocks", default=None)
        kept = sorted(b["block_id"] for b in blocks if b.get("included") is True) if isinstance(blocks, list) else None
        c.exact("kept_units", f"{cid}/kept_quads", kept, sorted(mine["kept_quads"]) if mine.get("kept_quads") else None)
        evaluation = row.get("claim_evaluation") or {}
        c.exact("outcome_word", f"{cid}/outcome", evaluation.get("outcome"), mine.get("outcome"))
        # L9 names a direction only for a supported claim; "none" is a value, absence is not.
        c.exact("outcome_word", f"{cid}/direction", evaluation.get("direction") or "none" if evaluation else None,
                (mine.get("direction") if mine.get("outcome") == "direction_supported" else "none") if mine else None,
                raw=evaluation.get("direction") if "direction" in evaluation else MISSING)
        c.exact("outcome_word", f"{cid}/ceiling", evaluation.get("claim_level_ceiling"), mine.get("ceiling"))
        l9_p[cid], our_p[cid] = multiplicity.get("raw_p"), mine.get("p")
        loo_l9 = {r.get("omitted_block_id"): r for r in get(row, "loo", "rows", default=[]) or []}
        for mine_loo in mine.get("loo") or []:
            block = next((b for b in loo_l9 if b and b.endswith("-b%02d" % mine_loo.get("block_number", -1))), None)
            l9_loo = loo_l9.pop(block, {})
            key = f"{cid}/loo/b%02d" % mine_loo.get("block_number", -1)
            c.numeric("contrast_j", key + "/dbar_j", l9_loo.get("estimate"), mine_loo.get("dbar_j"))
            c.numeric("contrast_p", key + "/raw_p", l9_loo.get("raw_p"), mine_loo.get("p"))
            c.numeric("contrast_p", key + "/adjusted_p", l9_loo.get("adjusted_p"), mine_loo.get("holm_p"))
            c.exact("outcome_word", key + "/outcome", l9_loo.get("outcome"), mine_loo.get("outcome"))
            for name, other in (("metrology_aware_ci95", "metrology_interval_j"), ("decision_interval", "decision_interval_j")):
                for side, (a, b) in zip(("lower", "upper"), zip(interval(l9_loo.get(name)), interval(mine_loo.get(other)))):
                    c.numeric("contrast_j", f"{key}/{other}/{side}", a, b)
            c.numeric("count", key + "/n", l9_loo.get("n_blocks"), mine_loo.get("n"))
            c.numeric("count", key + "/df", l9_loo.get("df"), mine_loo["n"] - 1 if finite(mine_loo.get("n")) else None)
            above = mine_loo.get("above_floor")
            c.exact("outcome_word", key + "/floor_status", l9_loo.get("floor_status"),
                    None if above is None else "above_floor" if above else "not_above_floor")
        for block in loo_l9:
            c.numeric("contrast_j", f"{cid}/loo/{block}/dbar_j", loo_l9[block].get("estimate"), None)
    c.exact("holm_order", "raw_p_order", holm_order(l9_p), holm_order(our_p))


def compare_brackets(c, custody, ours):
    line = get(ours, "disclosures", "sensitivity_bound", default={})
    for pack in PACKS:
        bracket = custody.one(r"brackets/[0-9a-f]{64}-" + pack + r"\.json")
        c.numeric("b_op_s", pack + "/b_op_s",
                  get(bracket, "evaluation", "acceptance", "allowance", "operative_b_fiducial_binary64_s"),
                  get(ours, "windows", PACKS[pack], "b_op_s"))
        c.numeric("b_op_s", pack + "/b_sens_s", get(bracket, "b_sens"), get(line, "windows", PACKS[pack], "b_sens_s"))
    block = custody.one(r"brackets/[0-9a-f]{64}-block\.json")
    c.numeric("b_op_s", "block/B_max_s", get(block, "value_s"), line.get("B_max_s"))
    c.numeric("count", "block/T", get(block, "T"), line.get("T"))
    c.numeric("count", "block/attained_by_sequence", get(block, "attained_by_sequence"), line.get("attaining_sequence"))


KIND_ORDER = ("E_clock_anchor_shift_bound_j", "E_interpolation_joint_edge_bound_j", "E_whole_window_drift_allowance_j")


def reported_cid(pack, phase):
    return f"df-ph-{'decode' if phase == 'decode' else 'prefill-p2048'}-{tag(pack)}"


def compare_reported(c, custody, ours):
    """Step 10: each pack's reported cells (estimator 1) against the recompute's reported_cells."""
    for pack in ("alpha", "beta"):
        projection = custody.one(r"outputs/[0-9a-f]{64}-projection-" + pack + r"\.json")
        l9_cells = {reported_cid(pack, cell.get("phase") or "missing"): cell
                    for cell in (get(projection, "cells", default=[]) if projection is not None else [{}]) or []}
        mine_cells = items(ours.get("reported_cells"), lambda key, _: key.endswith("-" + tag(pack)) and "p42" not in key)
        for cid in union(l9_cells, mine_cells):
            cell = l9_cells.get(cid, {})
            mine = get(ours, "reported_cells", cid, default={}) or {}
            key = pack + "/" + cid
            for field in ("mean_j", "lower_j", "upper_j"):
                c.numeric("reported_cell_j", key + "/" + field, cell.get(field), mine.get(field))
            ivl, ours_ivl = cell.get("interval") or {}, mine.get("interval") or {}
            for field, other in (("h_j", "h_j"), ("B_j", "B_j"), ("s_r", "s_r"), ("s_b", "s_b"), ("variance", "variance")):
                c.numeric("reported_cell_j", key + "/interval/" + field, ivl.get(field), ours_ivl.get(other))
            kinds = ours_ivl.get("kind_averages_j") or [None] * 3
            for i, name in enumerate(KIND_ORDER):
                c.numeric("reported_cell_j", key + "/interval/" + name, get(ivl, "kind_averages_j", name),
                          kinds[i] if i < len(kinds) else None)
            for field in ("value_j", "minimum_j"):
                c.numeric("reported_cell_j", key + "/attribution_floor/" + field, get(cell, "attribution_floor", field),
                          get(mine, "attribution_floor", field))
            c.numeric("reported_cell_j", key + "/j_per_token", get(cell, "per_token", "j_per_token"),
                      get(mine, "per_token", "j_per_token"))
            for field, other in (("n_r", "n_r"), ("n_b", "n_b")):
                c.numeric("count", key + "/" + field, ivl.get(field), mine.get(other))
            c.numeric("count", key + "/n_bundles", cell.get("n_bundles"), mine.get("n_bundles"))
            kept = cell.get("kept_units")
            c.exact("kept_units", key + "/kept_units",
                    sorted((u.get("stratum"), u.get("unit_id")) for u in kept) if isinstance(kept, list) else None,
                    sorted((s, u) for s, units in (mine.get("kept_units") or {}).items() for u in units) or None)
            c.numeric("count", key + "/interval/df", ivl.get("df"), ours_ivl.get("df"))
        for refused in get(projection, "refused_cells", default=[]) or []:
            if "p42" in str(refused.get("cell_id")):
                c.exact("p42_status", pack + "/" + refused["cell_id"], "expected_unresolvable",
                        get(ours, "p42", "df-ph-prefill-p42-" + tag(pack), "status"))


def compare_sensitivity(c, custody, ours):
    """Step 11 sensitivity line (registered B_max bound) against the recompute's sensitivity_bound line."""
    names = custody.names(r"outputs/[0-9a-f]{64}\.json")
    record = next((r for r in (custody.read(n) for n in names) if r.get("label") == "sensitivity"), None)
    line = get(ours, "disclosures", "sensitivity_bound", default={}) or {}
    if record is None:
        c.numeric("floor_gate_j", "sensitivity/record", None, None)
        return
    c.numeric("b_op_s", "sensitivity/B_max_s", get(record, "b_max", "value_s"), line.get("B_max_s"))
    c.numeric("count", "sensitivity/T", get(record, "b_max", "T"), line.get("T"))
    c.numeric("count", "sensitivity/attained_by_sequence", get(record, "b_max", "attained_by_sequence"),
              line.get("attaining_sequence"))
    for pack in union(record.get("windows") or {}, PACKS):
        c.numeric("b_op_s", f"sensitivity/windows/{pack}/b_op_s", get(record, "windows", pack, "b_op_s"),
                  get(ours, "windows", PACKS.get(pack, ""), "b_op_s"))
        c.numeric("b_op_s", f"sensitivity/windows/{pack}/b_sens_s", get(record, "windows", pack, "b_sens_s"),
                  get(line, "windows", PACKS.get(pack, ""), "b_sens_s"))
    cells = {"/".join(map(str, floor_cell_key(cell.get("cell_id", "")))): cell for cell in record.get("floor_cells", [])}
    for key in union(cells, items(line.get("floor_cells"))):
        cell, mine = cells.get(key, {}), get(line, "floor_cells", key, default={}) or {}
        for field in ("floor_abs_j", "floor_cmp_j", "floor_gate_j"):
            c.numeric("floor_gate_j", f"sensitivity/{key}/{field}", get(cell, "sensitivity", field), mine.get(field))
        c.numeric("floor_j", f"sensitivity/{key}/allowance_j", get(cell, "sensitivity", "allowance_j"),
                  get(line, "floors", key + "/absolute", "allowance_j"))
    rows = {row.get("contrast_id"): row for row in record.get("contrasts", [])}
    for cid in union(rows, items(line.get("contrasts"))):
        row, mine = rows.get(cid, {}), get(line, "contrasts", cid, default={}) or {}
        c.numeric("contrast_j", f"sensitivity/{cid}/D_j", get(row, "sensitivity", "D_j"), mine.get("D_j"))
        c.numeric("floor_gate_j", f"sensitivity/{cid}/floor_gate_j", get(row, "sensitivity", "floor_gate_j"),
                  mine.get("floor_gate_j"))
        for field in ("floor_abs_j", "floor_cmp_j"):
            c.numeric("floor_gate_j", f"sensitivity/{cid}/{field}", get(row, "sensitivity", field),
                      contrast_floor_part(line.get("floor_cells"), str(cid), field))
        c.exact("outcome_word", f"sensitivity/{cid}/outcome", get(row, "sensitivity", "outcome"), mine.get("outcome"))
    reported = {}
    for cell in record.get("reported_cells", []):
        reported[(cell.get("pack"), str(cell.get("cell_id", "")).replace("d117-reported-mean-ph-", "df-ph-"))] = cell
    mine_reported = {(pack, cid) for cid in items(line.get("reported_cells"), lambda key, _: "p42" not in key)
                     for pack in ("alpha", "beta") if cid.endswith("-" + tag(pack))}
    for pack, cid in union(reported, mine_reported):
        cell = reported.get((pack, cid), {})
        mine = get(line, "reported_cells", cid, default={}) or {}
        sens = cell.get("sensitivity") or {}
        if "p42" in cid:
            # The registered p42 exit: no reported value on either side; compared as a status, not as numbers.
            l9 = "expected_unresolvable" if not any(finite(v) for v in sens.values()) else "computed"
            c.exact("p42_status", f"sensitivity/{pack}/{cid}", l9, get(ours, "p42", cid, "status"))
            continue
        for field in ("mean_j", "lower_j", "upper_j"):
            c.numeric("reported_cell_j", f"sensitivity/{pack}/{cid}/{field}", sens.get(field), mine.get(field))
        c.numeric("reported_cell_j", f"sensitivity/{pack}/{cid}/h_j", sens.get("h_j"), get(mine, "interval", "h_j"))
        c.numeric("reported_cell_j", f"sensitivity/{pack}/{cid}/B_j", sens.get("B_j"), get(mine, "interval", "B_j"))
        c.numeric("reported_cell_j", f"sensitivity/{pack}/{cid}/attribution_floor_j", sens.get("attribution_floor_j"),
                  get(mine, "attribution_floor", "value_j"))


def reported_key(cell_id):
    """d117-reported-mean-ph-decode-qwen3-1p7b -> (recompute cell id, model/phase)."""
    cid = str(cell_id).replace("d117-reported-mean-ph-", "df-ph-")
    model = MODELS["alpha"] if cid.endswith("qwen3-1p7b") else MODELS["beta"]
    return cid, model + "/" + cell_phase(cid)


def compare_disclosures(c, custody, ours):
    """Step 11 disclosure lines that the recompute also computes."""
    names = custody.names(STEP11_SOURCES[1][1])
    record = custody.read(names[0]) if len(names) == 1 else None
    if record is None:
        c.numeric("reported_cell_j", "disclosure/record", None, None)
        return
    disclosures = ours.get("disclosures") or {}
    lines = {}
    for row in record.get("cells", []):
        if row.get("line") in ("cross_window", "battery_assist_cell"):
            lines[(row.get("line"), row.get("pack"), reported_key(row.get("cell_id"))[0])] = row
    for model_phase in items(disclosures.get("cross_window")):
        model, phase = model_phase.split("/", 1)
        pack = next((p for p, m in MODELS.items() if m == model), None)
        lines.setdefault(("cross_window", pack, reported_cid(str(pack), phase)), {})
    for cid in (disclosures.get("battery_assist") or {}):
        pack = next((p for p in ("alpha", "beta") if cid.endswith("-" + tag(p))), None)
        if pack and "p42" not in cid and cid.startswith("df-"):
            lines.setdefault(("battery_assist_cell", pack, cid), {})
    for (kind, pack, cid), row in sorted(lines.items(), key=str):
        key = f"disclosure/{pack}/{cid}/{kind}"
        if kind == "cross_window":
            mine = get(disclosures, "cross_window", reported_key(cid)[1], default={}) or {}
            for field in ("F_j", "G_j", "delta_j", "h_F_j", "h_G_j"):
                c.numeric("reported_cell_j", key + "/" + field, row.get(field), mine.get(field))
            c.exact("outcome_word", key + "/agree", row.get("agree"), mine.get("agree"))
        else:
            mine = get(disclosures, "battery_assist", cid, default={}) or {}
            without = row.get("without") or {}
            for field in ("mean_j", "lower_j", "upper_j"):
                c.numeric("reported_cell_j", key + "/without/" + field, without.get(field), mine.get(field))
            for field in ("h_j", "B_j"):
                c.numeric("reported_cell_j", key + "/without/" + field, without.get(field), get(mine, "interval", field))
            for field in ("n_r", "n_b"):
                c.numeric("count", key + "/without/" + field, row.get(field), mine.get(field))
            for stratum in ("repeat", "quad"):
                c.numeric("count", key + "/assist_members/" + stratum, get(row, "assist_members", stratum),
                          get(mine, "assist_members_by_stratum", stratum))
    contrasts = {}
    for row in record.get("contrasts", []):
        if row.get("line") in ("battery_assist_contrast", "magnitude_ratio", "magnitude_per_token", "loo_counts",
                               "loo_magnitude"):
            contrasts[(row.get("contrast_id"), row.get("line"))] = row
    for cid in items(disclosures.get("battery_assist"), lambda key, _: key.startswith("ctr-")):
        contrasts.setdefault((cid, "battery_assist_contrast"), {})
    for cid in items(ours.get("descriptive")):
        contrasts.setdefault((cid, "magnitude_ratio"), {})
        contrasts.setdefault((cid, "magnitude_per_token"), {})
    for cid in items(ours.get("contrasts")):
        contrasts.setdefault((cid, "loo_counts"), {})
    for (cid, kind), row in sorted(contrasts.items(), key=str):
        key = f"disclosure/{cid}/{kind}"
        if kind == "battery_assist_contrast":
            mine = get(disclosures, "battery_assist", cid, default={}) or {}
            ivl = interval(mine.get("metrology_interval_j"))
            for field, value in (("mean_j", mine.get("dbar_j")), ("lower_j", ivl[0]), ("upper_j", ivl[1]),
                                 ("s_d", mine.get("s_d_j")), ("se", mine.get("se_j"))):
                c.numeric("contrast_j", key + "/" + field, row.get(field), value)
            c.numeric("contrast_p", key + "/t_star", row.get("t_star"), mine.get("t_star"))
            c.numeric("count", key + "/n", row.get("n"), mine.get("n"))
            c.numeric("count", key + "/assist_quads", row.get("assist_quads"), mine.get("assist_quads"))
            for stratum in sorted(row.get("assist_members") or {}):
                c.numeric("count", key + "/assist_members/" + stratum, get(row, "assist_members", stratum),
                          get(mine, "assist_members_by_stratum", stratum))
        elif kind == "magnitude_ratio":
            mine = get(ours, "descriptive", cid, default={}) or {}
            ivl = interval(mine.get("ratio_interval"))
            for field, value in (("ratio", mine.get("ratio")), ("lower", ivl[0]), ("upper", ivl[1])):
                c.numeric("descriptive_ratio", key + "/" + field, row.get(field), value)
        elif kind == "magnitude_per_token":
            mine = get(ours, "descriptive", cid, default={}) or {}
            c.numeric("per_token_j", key + "/value_j", row.get("value_j"), mine.get("per_token_difference_j"))
            for name, other in (("metrology", "per_token_metrology_interval_j"), ("decision", "per_token_decision_interval_j")):
                for side, (a, b) in zip(("lower", "upper"), zip(interval(row.get(name)), interval(mine.get(other)))):
                    c.numeric("per_token_j", f"{key}/{name}/{side}", a, b)
        elif kind == "loo_counts":
            loo = get(ours, "contrasts", cid, "loo")
            c.numeric("count", key + "/count", row.get("count"), len(loo) if isinstance(loo, list) else None)
        else:
            # loo_magnitude: each row's movement |LOO estimate - estimate| at the rows L9's trigger selected.
            mine = get(ours, "contrasts", cid, default={}) or {}
            for item in row.get("rows") or []:
                number = str(item.get("block_number"))
                loo = next((r for r in mine.get("loo") or [] if str(r.get("block_number")) == number), {})
                moved = abs(loo["dbar_j"] - mine["dbar_j"]) if finite(loo.get("dbar_j")) and finite(mine.get("dbar_j")) else None
                block = "b%02d" % int(number) if number.isdigit() else number
                c.numeric("contrast_j", f"{key}/{block}/movement_j", item.get("movement_j"), moved)
    window_lines = record.get("window_lines") or {}
    for pack in sorted(set(window_lines) | {p for p, P in PACKS.items() if get(ours, "windows", P, "neg8")}):
        neg8 = get(ours, "windows", PACKS.get(pack, ""), "neg8", default={}) or {}
        rows = {row.get("line"): row for row in window_lines.get(pack) or []
                if row.get("line") in ("neg8_allowance", "reference_counts", "corpus_counts")}
        if neg8:
            for name in ("neg8_allowance", "reference_counts", "corpus_counts"):
                rows.setdefault(name, {})
        for name, row in sorted(rows.items()):
            key = f"disclosure/{pack}/{name}"
            if name == "neg8_allowance":
                values = row.get("values_j") or {}
                base = "bracket.claim_families.gross_energy."
                for field, other in (("bound_envelope_j", "bound_envelope_j"), ("bound_prediction_j", "bound_prediction_j"),
                                     ("start.mean_j", "start_mean_j"), ("midpoint.mean_j", "midpoint_j"),
                                     ("end.mean_j", "end_mean_j"), ("trajectory_excursion_max_j", "spread_j"),
                                     ("drift_allowance_j", "allowance_j")):
                    c.numeric("floor_j", key + "/" + field, values.get(base + field), neg8.get(other))
            elif name == "reference_counts":
                for slot, other in (("start", "n_start"), ("midpoint", "n_mid"), ("end", "n_end")):
                    c.numeric("count", key + "/" + slot, get(row, "counts", slot), neg8.get(other))
            else:
                c.numeric("count", key + "/deciding", row.get("deciding"), neg8.get("corpus_n"))


SHORT_MODELS = {"Qwen3-1.7B-4bit": "qwen3-1p7b", "Qwen3-8B-4bit": "qwen3-8b"}


def percentile(values, q):
    """Linear-interpolation percentile, the registered parser's definition (numpy's default)."""
    ordered = sorted(values)
    position = (len(ordered) - 1) * q / 100.0
    low = math.floor(position)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def plausible_rho(row):
    rho, machine, rail = row.get("rho"), row.get("delta_J"), row.get("rail_delta_J")
    return all(finite(v) for v in (rho, machine, rail)) and 0 < rho <= 1 and machine - rail >= 0


def model_groups(members):
    """The recompute's request rows by the disclosure's model word."""
    groups = {}
    for _, member in sorted((members or {}).items()):
        if isinstance(member, dict):
            model = member.get("model")
            groups.setdefault(str(SHORT_MODELS.get(model, model)), []).append(get(member, "phases", "request", default={}) or {})
    return groups


def machine_summary(rows):
    """PLAN 8.2 per-model summary: order statistics of every finite rho; spread of the plausible ones."""
    rhos = [row["rho"] for row in rows if finite(row.get("rho"))]
    plausible = [row["rho"] for row in rows if plausible_rho(row)]
    values = {}
    if rhos:
        values.update(median=statistics.median(rhos), minimum=min(rhos), maximum=max(rhos),
                      q25=percentile(rhos, 25), q75=percentile(rhos, 75))
    if plausible:
        values["spread"] = (max(plausible) - min(plausible)) / statistics.median(plausible)
    return values, plausible


def compare_machine(c, custody, ours, meter_records):
    """The whole-machine meter line: L9's disclosure and the harvest's meter record against the recompute.

    Members are the union of L9's disclosure, the recompute's window and the
    harvest record; a member missing from any of them, or without its machine
    object in the record, is DISAGREE (RC-CMP-3 X3).
    """
    names = custody.names(STEP11_SOURCES[1][1])
    record = custody.read(names[0]) if len(names) == 1 else {}
    windows = get(ours, "disclosures", "whole_machine", "windows", default={}) or {}
    window_lines = record.get("window_lines") or {}
    for pack in sorted(PACKS):
        lines = window_lines.get(pack) or []
        disclosed = {row.get("run_id"): row for row in lines if row.get("line") == "machine_member"}
        mine = get(windows, PACKS[pack], "members", default={}) or {}
        stored = meter_records.get(pack)
        harvested = get(stored, "members", default={}) or {}
        if not (disclosed or mine or harvested):
            continue
        if stored is None:
            # The disclosure shows a meter line, so its source record is required.
            c.numeric("meter_j", f"machine/{pack}/meter_record", None, None)
        for rid in union(disclosed, set(mine) | set(harvested)):
            row = disclosed.get(rid, {})
            own = get(mine, rid, "phases", "request", default={}) or {}
            key = f"machine/{pack}/{rid}/request"
            c.numeric("rho", key + "/rho", row.get("rho"), own.get("rho"))
            c.numeric("machine_j", key + "/rail_delta_J", row.get("rail_j"), own.get("rail_delta_J"))
            c.numeric("machine_j", key + "/delta_J", row.get("machine_j"), own.get("delta_J"))
            if stored is None:
                continue
            row = harvested.get(rid) if isinstance(harvested.get(rid), dict) else {}
            machine = row.get("machine") if isinstance(row.get("machine"), dict) else {}
            key = f"meter/{pack}/{rid}/request"
            c.numeric("meter_j", key + "/meter/energy_J", get(machine, "meter", "energy_J"), get(own, "meter", "energy_J"))
            c.numeric("meter_j", key + "/meter/delta_J", get(machine, "meter", "delta_J"), get(own, "meter", "delta_J"))
            c.numeric("meter_w", key + "/meter/baseline_W", get(machine, "meter", "baseline_W"), get(own, "meter", "baseline_W"))
            for field in ("n", "n_baseline"):
                c.numeric("count", key + "/meter/" + field, get(machine, "meter", field), get(own, "meter", field))
            available = machine.get("battery_term_available")
            c.exact("battery_term", key + "/battery_term_available", available, own.get("battery_term_available"))
            if available:
                c.numeric("machine_j", key + "/battery/delta_J", get(machine, "battery", "delta_J"), get(own, "battery", "delta_J"))
                c.numeric("count", key + "/battery/n", get(machine, "battery", "n"), get(own, "battery", "n"))
            c.numeric("machine_j", key + "/delta_J", machine.get("delta_J"), own.get("delta_J"))
            c.numeric("machine_j", key + "/rail_delta_J", row.get("rail_delta_J"), own.get("rail_delta_J"))
            c.numeric("rho", key + "/rho", row.get("rho"), own.get("rho"))
            for index, edge in enumerate(("start", "end")):
                l9_edge, our_edge = get(machine, "window_ns", index), get(own, "window_ns", index)
                if own.get("window_basis") == "controller_stamps":
                    # Controller stamps are identical integer-ns inputs: exact (7e322b76).
                    c.numeric("count", f"{key}/window_ns/{edge}", l9_edge, our_edge)
                else:
                    # A legacy wall placement compares the edge in seconds (7e322b76: 1e-6 s).
                    c.numeric("window_edge_s", f"{key}/window_s/{edge}", l9_edge / 1e9 if finite(l9_edge) else None,
                              our_edge / 1e9 if finite(our_edge) else None)
        compare_machine_summary(c, pack, lines, get(ours, "disclosures", "whole_machine", default={}) or {})


def compare_machine_summary(c, pack, lines, whole_machine):
    """L9's per-model order statistics and central band, re-derived from the recompute's member rho (X2)."""
    windows = whole_machine.get("windows") or {}
    summaries = {row.get("model"): row for row in lines if row.get("line") == "machine_summary"}
    groups = model_groups(get(windows, PACKS[pack], "members"))
    checked = {str(SHORT_MODELS.get(model, model)): row for model, row in
               (get(whole_machine, "request_cross_check", "windows", PACKS[pack], "models", default={}) or {}).items()}
    for model in union(summaries, groups):
        line = summaries.get(model, {})
        derived, _ = machine_summary(groups.get(model, []))
        key = f"machine_summary/{pack}/{model}"
        for stat in ("median", "minimum", "maximum", "q25", "q75", "spread"):
            if stat in line or stat in derived:
                c.numeric("rho", f"{key}/{stat}", line.get(stat), derived.get(stat))
        # The band's window is L9's (each model's first clean window); its bounds are re-derived
        # from that window's plausible members. A band on the recompute's side only is DISAGREE.
        band = line.get("central_band") if isinstance(line.get("central_band"), dict) else {}
        own_band = get(checked, model, "central_band", default={}) or {}
        band_pack = band.get("pack") or (own_band.get("pack") or "").lower() or None
        if not band and not band_pack:
            continue
        _, plausible = machine_summary(model_groups(get(windows, PACKS.get(band_pack, ""), "members")).get(model, []))
        for side, value in (("lower", min(plausible) if plausible else None), ("upper", max(plausible) if plausible else None)):
            c.numeric("rho", f"{key}/central_band/{side}", band.get(side), value)


def load_meter_records(specs, flags=None):
    """--harvest-meter PACK=PATH: the harvest's withheld meter record, with its digest."""
    records, digests = {}, {}
    flags = [] if flags is None else flags
    for spec in specs or ():
        pack, _, path = spec.partition("=")
        if pack not in PACKS or not path or pack in records:
            raise Refusal("harvest_meter_argument_invalid")
        try:
            raw = Path(path).read_bytes()
            records[pack] = loads(raw, flags, "harvest_meter:" + pack)
        except (OSError, ValueError):
            raise Refusal("harvest_meter_unreadable") from None
        if not isinstance(records[pack], dict):
            raise Refusal("harvest_meter_unreadable")
        digests[pack] = hashlib.sha256(raw).hexdigest()
    return records, digests


def compare_exclusions(c, ours):
    for pack in sorted(PACKS.values()):
        # L9 consumes derived/exclusions.json; the recompute re-derives it from the flags (AN-18 partial).
        c.exact("exclusions_rederivation", pack, "agrees", get(ours, "exclusions_rederivation", pack, "status"))


# Step-11 coverage (RC-CMP-3 X1, X6). Each leaf of the fill input and the disclosure
# record has a path like fill:gamma/contrasts/*/estimate: a list item becomes *, or
# its line word when the item is a disclosure line (window_lines/alpha/machine_member/rho).
# A rule is (pattern, target) or (pattern, family, key). The first rule that matches wins:
# - (pattern, family, key): the leaf copies the comparison row (family, key). The key
#   template is filled from the pattern's named groups and from the scalar fields of the
#   objects enclosing the leaf (its contrast, cell, run or line; see binding()). The leaf is
#   covered only if that row exists, its L9 value equals the leaf in type and value, and
#   it is AGREE; otherwise the run refuses;
# - "uncovered:<reason>" matches non-numeric leaves only: a numeric leaf falls through;
# - "uncovered-by-name:<reason>" names numeric leaves left uncovered; each one is listed.
# A leaf no rule matches refuses the run.
STEP11_SOURCES = (("fill", r"outputs/[0-9a-f]{64}-results-fill-input\.json"),
                  ("disclosure", r"disclosures/[0-9a-f]{64}\.json"))
UNCOVERED, NAMED = "uncovered:", "uncovered-by-name:"
TEXT = UNCOVERED + "rendered text and labels; checked against issued values by the post-release reader (synthesis 2(b)(iii))"
IDENTITY = UNCOVERED + "identity, label or provenance (ids, digests, pins, stage names); bound by L9's record, not a computed quantity"
IDENTITY_NUMBER = NAMED + "attempt numbers, positions and ledger sequences: identity bound by L9's record, not a computed quantity"
STRUCTURE = (UNCOVERED + "window structure the recompute does not re-derive (flag tallies, hazards, monitor, battery, "
             "ledger, tripwires); reader item 2(b)")
STRUCTURE_NUMBER = NAMED + "window and block structure counts and readings the recompute does not re-derive; reader item 2(b)"
DERIVED_FLAGS = UNCOVERED + "L9's own consistency booleans and status words over values compared individually here"
NEG8_INTERNALS = (NAMED + "NEG-8 bracket internals (admissible sets, standard errors, idle-subtracted companion, "
                  "drift-bound artifact) that only L9 computes; the seven registered bound terms are compared")
CONSTANT = NAMED + "registered constant (token denominator, planned reference counts, plan size)"
LOAD_LINE = (NAMED + "load-correlated sensitivity line (PLAN 8.1): never replaces a primary value and gates nothing; "
             "not compared here")
ESTIMATOR_INTERNALS = (NAMED + "registered estimator internals beside SE_total and the metrology-aware interval "
                       "(compared): SE_repeat, SE_metrology, repeat-point interval, variance contributions, exact t")
FLOOR_DIAGNOSTICS = NAMED + "attribution-floor diagnostics carried beside the resolved floor; the floor values are compared"
FLOOR_KEPT = NAMED + "kept-unit counts of a floor cell or a contrast's repeat stratum; the floor's n and n_admitted and the contrast's n are compared"
F = r"fill:gamma/contrasts/\*/"
D = "disclosure:"
W = r"disclosure:window_lines/(?P<pack>[a-z]+)/"
SR = r"disclosure:(sensitivity/reported_cells/\*|block_lines/sensitivity_reported/record)/"
SF = r"disclosure:(sensitivity/floor_cells/\*|block_lines/sensitivity_floor/record)/"
SC = r"disclosure:(sensitivity/contrasts/\*|block_lines/sensitivity_contrast/record)/"
COVERAGE = (
    (r"(fill|disclosure):(.*/)?(text|label|line|restricted|schema_version)", TEXT),
    # Fill input: each contrast's copy of its claim verdict, bound by its contrast_id.
    (F + "estimate", "contrast_j", "{cid}/dbar_j"),
    (F + "interval/(?P<side>lower|upper)", "contrast_j", "{cid}/metrology_interval_j/{side}"),
    (F + "decision_interval/(?P<side>lower|upper)", "contrast_j", "{cid}/decision_interval_j/{side}"),
    (F + "deterministic_widening_total", "contrast_j", "{cid}/D_j"),
    (F + "j_per_token", UNCOVERED + "null for a J contrast by registration (J/token contrasts only)"),
    (F + "j_per_token", "contrast_j", "{cid}/dbar_j"),
    (F + "(?P<field>n|df)", "count", "{cid}/{field}"),
    (F + "sampling/kept_n", "count", "{cid}/n"),
    (F + "sampling/(planned_n|observed_complete_n)", CONSTANT + "; the claim engine's complete-observation count beside the kept n (compared)"),
    (F + "t_critical_95", "contrast_p", "{cid}/t_critical"),
    (F + "multiplicity/(?P<field>raw_p|adjusted_p)", "contrast_p", "{cid}/{field}"),
    (F + "multiplicity/rejected", "outcome_word", "{cid}/holm_reject"),
    (F + "claim_evaluation/outcome", "outcome_word", "{cid}/outcome"),
    (F + "claim_evaluation/claim_level_ceiling", "outcome_word", "{cid}/ceiling"),
    (F + "claim_evaluation/direction", "outcome_word", "{cid}/direction"),
    (F + "floor/active_floor_j", "floor_gate_j", "{cid}/active_floor_j"),
    (F + "floor/(?P<field>floor_abs_j|floor_cmp_j)", "floor_gate_j", "{cid}/{field}"),
    (F + r"floor/resolutions/\*/(?P<field>floor_abs_j|floor_cmp_j|floor_gate_j)", "floor_gate_j", "{source_cell}/{field}"),
    (F + r"floor/arm_gates/\*/floor_gate_j", "floor_gate_j", "{arm_cell}/floor_gate_j"),
    (F + r"floor/(resolutions/\*/)?(point_floor_diagnostics|single_count_discipline)(/.*)?", FLOOR_DIAGNOSTICS),
    (F + r"floor/(aggregation|claim_floor_rule|status|transport_verdict|floor_source|floor_limit_class|"
     r"arm_gates/\*/(arm_id|condition_family_id|status)|resolutions/\*/(status|transport_rule_id|reason_codes(/\*)?|"
     r"floor_source|floor_limit_class))", UNCOVERED + "registered floor rule names and resolution status"),
    (F + r"loo/rows/\*/estimate", "contrast_j", "{cid}/loo/{loo}/dbar_j"),
    (F + r"loo/rows/\*/(?P<field>raw_p|adjusted_p)", "contrast_p", "{cid}/loo/{loo}/{field}"),
    (F + r"loo/rows/\*/(?P<field>outcome|floor_status)", "outcome_word", "{cid}/loo/{loo}/{field}"),
    (F + r"loo/rows/\*/n_blocks", "count", "{cid}/loo/{loo}/n"),
    (F + r"loo/rows/\*/df", "count", "{cid}/loo/{loo}/df"),
    (F + r"loo/rows/\*/metrology_aware_ci95/(?P<side>lower|upper)", "contrast_j", "{cid}/loo/{loo}/metrology_interval_j/{side}"),
    (F + r"loo/rows/\*/decision_interval/(?P<side>lower|upper)", "contrast_j", "{cid}/loo/{loo}/decision_interval_j/{side}"),
    (F + r"(claim_evaluation/reason_codes(/\*)?|claim_evaluation/claim_ready_for_l2_l3|loo/status|loo/rows|"
     r"loo/rows/\*/influence_triggers(/\*)?)",
     UNCOVERED + "L9 reason-code vocabulary; the recompute derives the outcome, ceiling and influence, not these codes"),
    (F + r"(kept_block_ids|removed_block_ids|sampling/removed_block_ids)(/\*)?", UNCOVERED + "block identity; kept sets compared as kept_units"),
    (F + r"(conditions|metric|equivalence)(/.*)?", NAMED + "registered contrast definition from the sealed manifest"),
    (F + r"(claim_role|hypothesized_direction|sampling/confirmatory_status)", UNCOVERED + "registered contrast definition from the sealed manifest"),
    (r"fill:(gamma/(evidence_class|limitations(/\*)?|contrasts/\*/limitations(/\*)?))",
     UNCOVERED + "registered limitation notes; copied from the claim verdicts by L9's validated adapter"),
    (r"fill:characterization/.*", UNCOVERED + "characterization selection; not funded, not run (constant)"),
    (r"fill:(campaigns|gamma/finalized_manifest|gamma/floor_artifact)/.*", IDENTITY),
    # Disclosure record: the cells (reported cells and their lines), bound by pack and cell_id.
    (D + r"windows/[a-z]+/attempt", IDENTITY_NUMBER),
    (D + r"cells/(reported_cell|battery_assist_cell/primary)/(?P<field>mean_j|lower_j|upper_j)", "reported_cell_j", "{pack}/{rcid}/{field}"),
    (D + r"cells/(reported_cell|battery_assist_cell/primary)/(?P<field>h_j|B_j)", "reported_cell_j", "{pack}/{rcid}/interval/{field}"),
    (D + r"cells/battery_assist_cell/without/(?P<field>mean_j|lower_j|upper_j|h_j|B_j)", "reported_cell_j",
     "disclosure/{pack}/{rcid}/battery_assist_cell/without/{field}"),
    (D + r"cells/battery_assist_cell/(?P<field>n_r|n_b)", "count", "disclosure/{pack}/{rcid}/battery_assist_cell/without/{field}"),
    (D + r"cells/battery_assist_cell/assist_members/(?P<stratum>repeat|quad)", "count",
     "disclosure/{pack}/{rcid}/battery_assist_cell/assist_members/{stratum}"),
    (D + r"cells/attribution_floor/(?P<field>value_j|minimum_j)", "reported_cell_j", "{pack}/{rcid}/attribution_floor/{field}"),
    (D + r"cells/cross_window/(?P<field>F_j|G_j|delta_j|h_F_j|h_G_j)", "reported_cell_j", "disclosure/{pack}/{rcid}/cross_window/{field}"),
    (D + r"cells/cross_window/agree", "outcome_word", "disclosure/{pack}/{rcid}/cross_window/agree"),
    (D + r"cells/kept_units/(?P<field>n_r|n_b)", "count", "{pack}/{rcid}/{field}"),
    (D + r"(cells|contrasts)/load_correlated_(cell|contrast)/(values/.*|restored_counts/[a-z]+|restored_count)", LOAD_LINE),
    # The floor-composition lines, bound by the extraction cell (model, phase, form).
    (D + r"floors/floor_composition/guarded_j", "floor_j", "{floor_cell}/guarded_floor_j"),
    (D + r"floors/floor_composition/allowance_j", "floor_j", "{floor_cell}/whole_window_drift_allowance_j"),
    (D + r"floors/floor_composition/drift_widened_j", "floor_j", "{floor_cell}/drift_widened_guarded_floor_j"),
    (D + r"floors/floor_composition/minted_j", "floor_gate_j", "{minted_field}"),
    (D + r"floors/kept_units/(n_r|n_b)", FLOOR_KEPT),
    # The contrast lines, bound by contrast_id.
    (D + r"contrasts/primary_contrast/estimator/estimate", "contrast_j", "{cid}/dbar_j"),
    (D + r"contrasts/primary_contrast/estimator/s_d", "contrast_j", "{cid}/s_d_j"),
    (D + r"contrasts/primary_contrast/estimator/SE_total", "contrast_j", "{cid}/se_j"),
    (D + r"contrasts/primary_contrast/estimator/(?P<field>n|df)", "count", "{cid}/{field}"),
    (D + r"contrasts/primary_contrast/estimator/t_critical_95", "contrast_p", "{cid}/t_critical"),
    (D + r"contrasts/primary_contrast/estimator/raw_p", "contrast_p", "{cid}/raw_p"),
    (D + r"contrasts/primary_contrast/estimator/metrology_aware_CI95/(?P<side>lower|upper)", "contrast_j",
     "{cid}/metrology_interval_j/{side}"),
    (D + r"contrasts/primary_contrast/estimator/(SE_repeat|SE_metrology|repeat_point_CI95/(lower|upper)|variance_contributions(/.*)?)",
     ESTIMATOR_INTERNALS),
    (D + r"contrasts/primary_contrast/estimator/(name|excluded_stochastic_terms(/\*)?)",
     UNCOVERED + "registered estimator definition (name, no extra stochastic terms)"),
    (D + r"contrasts/(primary_contrast|decision_floor)/decision_interval/(?P<side>lower|upper)", "contrast_j",
     "{cid}/decision_interval_j/{side}"),
    (D + r"contrasts/decision_floor/floor_j", "floor_gate_j", "{cid}/active_floor_j"),
    (D + r"contrasts/decision_floor/estimate_j", "contrast_j", "{cid}/dbar_j"),
    (D + r"contrasts/battery_assist_contrast/(?P<field>mean_j|lower_j|upper_j|s_d|se)", "contrast_j",
     "disclosure/{cid}/battery_assist_contrast/{field}"),
    (D + r"contrasts/battery_assist_contrast/t_star", "contrast_p", "disclosure/{cid}/battery_assist_contrast/t_star"),
    (D + r"contrasts/battery_assist_contrast/(?P<field>n|assist_quads|assist_members/[a-z]+)", "count",
     "disclosure/{cid}/battery_assist_contrast/{field}"),
    (D + r"contrasts/magnitude_ratio/(?P<field>ratio|lower|upper)", "descriptive_ratio", "disclosure/{cid}/magnitude_ratio/{field}"),
    (D + r"contrasts/magnitude_ratio/(log_mean|log_sd)",
     NAMED + "log-scale internals of the descriptive ratio; ratio and interval compared"),
    (D + r"contrasts/magnitude_per_token/value_j", "per_token_j", "disclosure/{cid}/magnitude_per_token/value_j"),
    (D + r"contrasts/magnitude_per_token/(?P<name>metrology|decision)/(?P<side>lower|upper)", "per_token_j",
     "disclosure/{cid}/magnitude_per_token/{name}/{side}"),
    (D + r"contrasts/magnitude_per_token/denominator", CONSTANT),
    (D + r"contrasts/contrast_interval/n", "count", "{cid}/n"),
    (D + r"contrasts/contrast_interval/rounded_t", "contrast_p", "{cid}/t_critical"),
    (D + r"contrasts/contrast_interval/exact_t", ESTIMATOR_INTERNALS),
    (D + r"contrasts/loo_counts/count", "count", "disclosure/{cid}/loo_counts/count"),
    (D + r"contrasts/loo_magnitude/rows/\*/movement_j", "contrast_j", "disclosure/{cid}/loo_magnitude/{loo_number}/movement_j"),
    (D + r"contrasts/(loo_counts/exclusive_block_numbers(/\*)?|loo_magnitude/rows(/\*/block_number)?)",
     UNCOVERED + "leave-one-out block numbers; the outcomes, estimates and p values of every leave-one-out row are compared"),
    (D + r"contrasts/kept_units/n_b", "count", "{cell_id}/n"),
    (D + r"contrasts/kept_units/n_r", FLOOR_KEPT),
    (D + r"(cells|contrasts|floors)/[a-z_]+/(codes/\*/(blinding|code|family)|families(/\*)?|stratum|removed_unit_ids(/\*)?|"
     r"attained_by(/\*)?|source)",
     UNCOVERED + "removed-unit codes and families; exclusions are re-derived by the recompute (exclusions_rederivation)"),
    (D + r"(cells/[a-z_]+/(status|primary/status|without/status|values/status|values/code)|contrasts/[a-z_]+/(status|values/status|values/code))",
     DERIVED_FLAGS),
    # Window lines: the NEG-8 terms, b_op, reference and corpus counts and the whole-machine line.
    (W + r"neg8_allowance/values_j/bracket\.claim_families\.gross_energy\.(?P<field>bound_envelope_j|bound_prediction_j|"
     r"start\.mean_j|midpoint\.mean_j|end\.mean_j|trajectory_excursion_max_j|drift_allowance_j)",
     "floor_j", "disclosure/{pack}/neg8_allowance/{field}"),
    (W + r"neg8_allowance/values_j/.*", NEG8_INTERNALS),
    (W + r"reference_counts/counts/(?P<slot>start|midpoint|end)", "count", "disclosure/{pack}/reference_counts/{slot}"),
    (W + r"reference_counts/planned/(start|midpoint|end)", CONSTANT),
    (W + r"corpus_counts/deciding", "count", "disclosure/{pack}/corpus_counts/deciding"),
    (W + r"corpus_counts/(collected|in_window|drop_counts/[A-Za-z0-9_.]+)", STRUCTURE_NUMBER),
    (W + r"below_screen_bound/b_op_s", "b_op_s", "{pack}/b_op_s"),
    (W + r"machine_member/rho", "rho", "machine/{pack}/{run_id}/request/rho"),
    (W + r"machine_member/rail_j", "machine_j", "machine/{pack}/{run_id}/request/rail_delta_J"),
    (W + r"machine_member/machine_j", "machine_j", "machine/{pack}/{run_id}/request/delta_J"),
    (W + r"machine_summary/(?P<stat>median|minimum|maximum|q25|q75|spread)", "rho", "machine_summary/{pack}/{model}/{stat}"),
    (W + r"machine_summary/central_band/(?P<side>lower|upper)", "rho", "machine_summary/{pack}/{model}/central_band/{side}"),
    (W + r"machine_summary/central_band/attempt", IDENTITY_NUMBER),
    (W + r"(monitor_cost/(cpu_s|reader_cpu_s|probes_inside_target_phases)|(arm_hazards|battery_phase)/measurements/.*|"
     r"(physics_counts|battery_counts)/counts/[A-Za-z0-9_.]+|(anchor_counts|flag_count|stored_member_reason)/count|"
     r"(anchor_bound|host_cpu)/value_s|(battery_temperature|battery_temperature_sentence)/(readings_centi_c/\*|rise_k)|"
     r"erratum3_triggers/values/(doubling_count|systematic_sequences/\*)|"
     r"deciding_membership/(deciding_references|deciding_spares|writer_excluded_count|writer_excluded_by_family/[A-Za-z0-9_.]+))",
     STRUCTURE_NUMBER),
    (W + r"battery_discharged/value_j", NAMED + "battery-assist discharged energy from the withheld battery record; "
     "the recompute flags battery assist but does not re-derive this energy"),
    (W + r"ledger_binding/terminal_sequence", IDENTITY_NUMBER),
    (r"disclosure:window_lines/.*", STRUCTURE + "; includes NEG-8 bracket provenance that only L9 computes"),
    # Block lines.
    (D + r"block_lines/dominance_ratio/ratio", "dominance_ratio", "{ratio_label}/ratio"),
    (D + r"block_lines/dominance_ratio/(?P<field>numerator_j|denominator_j)", "floor_j", "{ratio_label}/{field}"),
    (D + r"block_lines/dominance_ratio/n", "count", "{ratio_label}/n"),
    (D + r"block_lines/dominance_ratio/(component|status)", IDENTITY),
    (D + r"block_lines/dominance_branch/branch", "dominance_branch", "branch"),
    (D + r"block_lines/dominance_branch/dominance_sentence_licensed", UNCOVERED + "follows from the dominance branch (compared)"),
    (D + r"(block_lines/sensitivity_bmax|sensitivity/b_max)/value_s", "b_op_s", "sensitivity/B_max_s"),
    (D + r"(block_lines/sensitivity_bmax|sensitivity/b_max)/(?P<field>T|attained_by_sequence)", "count", "sensitivity/{field}"),
    (D + r"block_lines/sensitivity_window/(?P<field>b_op_s|b_sens_s)", "b_op_s", "sensitivity/windows/{pack}/{field}"),
    (D + r"sensitivity/windows/(?P<pack>[a-z]+)/(?P<field>b_op_s|b_sens_s)", "b_op_s", "sensitivity/windows/{pack}/{field}"),
    (SR + r"sensitivity/(?P<field>mean_j|lower_j|upper_j|h_j|B_j|attribution_floor_j)", "reported_cell_j",
     "sensitivity/{pack}/{rcid}/{field}"),
    (SR + r"primary/(?P<field>mean_j|lower_j|upper_j)", "reported_cell_j", "{pack}/{rcid}/{field}"),
    (SR + r"primary/(?P<field>h_j|B_j)", "reported_cell_j", "{pack}/{rcid}/interval/{field}"),
    (SR + r"primary/attribution_floor_j", "reported_cell_j", "{pack}/{rcid}/attribution_floor/value_j"),
    (SF + r"sensitivity/(?P<field>floor_abs_j|floor_cmp_j|floor_gate_j)", "floor_gate_j", "sensitivity/{aggregate_cell}/{field}"),
    (SF + r"sensitivity/allowance_j", "floor_j", "sensitivity/{aggregate_cell}/allowance_j"),
    (SF + r"primary/(?P<field>floor_abs_j|floor_cmp_j|floor_gate_j)", "floor_gate_j", "{aggregate_cell}/{field}"),
    (SF + r"primary/allowance_j", "floor_j", "{aggregate_cell}/absolute/whole_window_drift_allowance_j"),
    (SC + r"sensitivity/(?P<field>floor_abs_j|floor_cmp_j|floor_gate_j)", "floor_gate_j", "sensitivity/{cid}/{field}"),
    (SC + r"sensitivity/D_j", "contrast_j", "sensitivity/{cid}/D_j"),
    (SC + r"sensitivity/outcome", "outcome_word", "sensitivity/{cid}/outcome"),
    (SC + r"primary/(?P<field>floor_abs_j|floor_cmp_j)", "floor_gate_j", "{cid}/{field}"),
    (SC + r"primary/floor_gate_j", "floor_gate_j", "{cid}/active_floor_j"),
    (SC + r"primary/D_j", "contrast_j", "{cid}/D_j"),
    (SC + r"primary/outcome", "outcome_word", "{cid}/outcome"),
    (D + r"(block_lines/[a-z_]+/record|sensitivity/[a-z_]+/\*|sensitivity/windows/[a-z]+|block_lines/sensitivity_window)/"
     r"(bound_independent_values_equal_primary|equals_primary|mean_and_half_width_equal_primary|not_below_primary|"
     r"outcome_equals_primary|widened|status|code)", DERIVED_FLAGS),
    (D + r"block_lines/(attempt_count/count|attempt_history/(attempt|collected|planned|flags_by_family/[A-Za-z0-9_.]+|"
     r"triggers/(doubling_count|systematic_sequences/\*))|g10/(codes/[A-Za-z0-9_.]+|redraw_cycles)|"
     r"reharvest_account/(survivors_before|survivors_after))", STRUCTURE_NUMBER),
    (D + r"block_lines/(superseded_history|attempt_count|attempt_history|g10|harvest_once|reharvest_account)/.*", STRUCTURE),
    (D + r"fixed_sentences/.*", TEXT),
    (r"(fill|disclosure):(.*/)?(positions/\*|attempt)", IDENTITY_NUMBER),
    (r"(fill|disclosure):(.*/)?(cell_id|contrast_id|unit_id|plan_id|run_id|bundle_id|pack|harvest_pin|record_shape|model|"
     r"stage_ids/\*|stage_id|floor_cell_ids/\*|floor_row_ids/\*|source_cell_ids/\*|floor_source_cell_ids/\*|"
     r"omitted_block_id|transport_group_id|[a-z_]*sha256|[a-z_]*_id|claim_verdicts_id|manifest_id|artifact_id|"
     r"central_band/(pack|plan_id))", IDENTITY),
)


def numeric(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def leaves(value, path="", context=None):
    """(path, value, context): context holds the scalar fields of the enclosing objects, nearest first."""
    context = context or {}
    if isinstance(value, dict) and value:
        context = {**context, **{key: item for key, item in value.items() if not isinstance(item, (dict, list))}}
        # A one-item list of ids names its single source (a floor resolution's source cell).
        context.update({key: item[0] for key, item in value.items()
                        if isinstance(item, list) and len(item) == 1 and isinstance(item[0], str)})
        for key, item in value.items():
            yield from leaves(item, path + "/" + str(key) if path else str(key), context)
    elif isinstance(value, list) and value:
        for item in value:
            line = item.get("line") if isinstance(item, dict) else None
            step = line if isinstance(line, str) and re.fullmatch(r"[a-z][a-z0-9_]*", line) else "*"
            yield from leaves(item, path + "/" + step, context)
    else:
        yield path, value, context


def binding(context, groups):
    """Fields a key template may name: the pattern's groups, the leaf's context and ids derived from it."""
    fields = {**context, **{k: v for k, v in groups.items() if v is not None}}
    cell = context.get("cell_id")
    fields["cid"] = context.get("contrast_id")
    if isinstance(cell, str):
        fields["rcid"] = reported_key(cell)[0]
        model, phase, kind = cell_model(cell), cell_phase(cell), floor_kind(cell)
        if model:
            fields["aggregate_cell"] = model + "/" + phase
            if kind:
                fields["floor_cell"] = f"{model}/{phase}/{kind}"
                fields["minted_field"] = f"{model}/{phase}/floor_{'abs' if kind == 'absolute' else 'cmp'}_j"
            component = context.get("component")
            label = re.match(r"\S+ \S+: (R|R_cm) ", str(context.get("text", "")))
            if label and component:
                fields["ratio_label"] = f"{model}/{phase}/{component}" + ("/common_mode" if label[1] == "R_cm" else "")
    source = context.get("source_cell_ids")
    if isinstance(source, str) and cell_model(source):
        fields["source_cell"] = "/".join(floor_cell_key(source))
    arm = context.get("condition_family_id")
    if isinstance(arm, str) and cell_model(arm) and isinstance(fields["cid"], str):
        fields["arm_cell"] = cell_model(arm) + "/" + cell_phase(fields["cid"])
    fields["loo"] = loo_key(context.get("omitted_block_id"))
    number = str(context.get("block_number"))
    fields["loo_number"] = "b%02d" % int(number) if number.isdigit() else None
    return fields


def key_for(template, context, groups):
    fields = binding(context, groups)
    names = re.findall(r"\{(\w+)\}", template)
    if any(not isinstance(fields.get(name), (str, int)) or isinstance(fields.get(name), bool) for name in names):
        return None
    return template.format(**{name: fields[name] for name in names})


def coverage(custody, comparison, rules=None):
    rules = COVERAGE if rules is None else rules
    rows = {}
    for row in comparison.rows:
        rows.setdefault((row["family"], row["key"]), row)
    report, unmapped, unbound, named, absent = {}, set(), {}, set(), []
    for label, pattern in STEP11_SOURCES:
        names = custody.names(pattern)
        if not names:
            absent.append(label)
        for name in names:
            for leaf, value, context in leaves(custody.read(name)):
                path = label + ":" + leaf
                rule, match = None, None
                for candidate in rules:
                    match = re.fullmatch(candidate[0], path)
                    # An uncovered: rule never takes a number (X6); the number falls through.
                    if match and not (candidate[1].startswith(UNCOVERED) and numeric(value)):
                        rule = candidate
                        break
                if rule is None and value in ([], {}):
                    # An empty list or object prints no value.
                    report.setdefault(path, UNCOVERED + "empty container; no printed value")
                elif rule is None:
                    unmapped.add(path)
                elif len(rule) == 2:
                    report.setdefault(path, rule[1])
                    if rule[1].startswith(NAMED) and numeric(value):
                        named.add(path)
                else:
                    family = rule[1]
                    key = key_for(rule[2], context, match.groupdict())
                    row = rows.get((family, key)) if key is not None else None
                    printed = row.get("l9_raw", row.get("l9")) if row else None
                    reason = ("key_unresolved" if key is None else "no_row" if row is None else
                              "value_differs" if not same(printed, value) else
                              "row_disagrees" if row["verdict"] != "AGREE" else None)
                    if reason:
                        # Mapped, but not a copy of an agreeing compared row: not coverage.
                        unbound.setdefault((path, family, str(key), reason), None)
                    else:
                        report.setdefault(path, family)
    uncompared = sorted({path for path, *_ in unbound})
    for path in uncompared:
        report.pop(path, None)
    return {"leaves": report, "unmapped": sorted(unmapped | set(uncompared)), "uncompared": uncompared,
            "unbound": [{"path": p, "family": f, "key": k, "reason": r} for p, f, k, r in sorted(unbound)],
            "uncovered_numeric": sorted(named), "absent_sources": absent}


def run(l9_custody, recompute_path, bars_path=DEFAULT_BARS, rules=None, meter=()):
    bars = load_bars(bars_path)
    flags = []
    meter_records, meter_digests = load_meter_records(meter, flags)
    custody = Custody(l9_custody, flags)
    try:
        ours = loads(Path(recompute_path).read_bytes(), flags, "recompute")
    except (OSError, ValueError):
        raise Refusal("recompute_output_unreadable") from None
    c = Comparison(bars)
    compare_runs(c, custody, ours)
    compare_brackets(c, custody, ours)
    compare_floors(c, custody, ours)
    compare_aggregate(c, custody, ours)
    compare_contrasts(c, custody, ours)
    compare_reported(c, custody, ours)
    compare_sensitivity(c, custody, ours)
    compare_disclosures(c, custody, ours)
    compare_machine(c, custody, ours, meter_records)
    compare_exclusions(c, ours)
    cover = coverage(custody, c, rules)
    return {"schema": SCHEMA, "bar_set": bars.get("bar_set"), "bars": bars["families"],
            "l9_steps": {f"{s}/{w}" if w else str(s): v for (s, w), v in sorted(custody.status.items(), key=str)},
            "recompute_program_sha256": ours.get("program_sha256"), "harvest_meter_sha256": meter_digests,
            "structure_flags": flags, "counts": c.counts(),
            "coverage": cover, "comparisons": c.rows}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--l9-custody", required=True, help="L9 dry-run custody root")
    parser.add_argument("--recompute", required=True, help="independent recompute --member-detail output")
    parser.add_argument("--bars", default=str(DEFAULT_BARS),
                        help="bar-set config (joulewise.b5_comparator_bars.v1); default block 5's release set")
    parser.add_argument("--harvest-meter", action="append", default=[], metavar="PACK=PATH",
                        help="a window's withheld meter record (alpha, beta or gamma); repeat per window")
    parser.add_argument("--restricted-out", required=True, help="restricted file for values and differences")
    args = parser.parse_args(argv)
    out = Path(args.restricted_out)
    if out.exists():
        print("refused=restricted_output_exists", file=sys.stderr)
        return 2
    try:
        result = run(args.l9_custody, args.recompute, args.bars, meter=args.harvest_meter)
        out.write_text(json.dumps(result, sort_keys=True, indent=1, allow_nan=False) + "\n")
    except Refusal as exc:
        # The restricted output is always written; a refusal leaves its structure code there too.
        out.write_text(json.dumps({"schema": SCHEMA, "refused": str(exc)}, sort_keys=True) + "\n")
        print("refused=" + str(exc), file=sys.stderr)
        return 2
    except Exception as exc:
        out.write_text(json.dumps({"schema": SCHEMA, "refused": "internal " + type(exc).__name__}, sort_keys=True) + "\n")
        print("error=internal " + type(exc).__name__, file=sys.stderr)
        return 2
    counts = result["counts"]
    cover = result["coverage"]
    # Public line: per-family pass/fail counts and structure only, never a value or a difference.
    print("bar_set=" + str(result["bar_set"]) + " families=" + json.dumps(counts, sort_keys=True, separators=(",", ":"))
          + " step11_unmapped=" + str(len(cover["unmapped"])) + " step11_uncovered_numeric="
          + str(len(cover["uncovered_numeric"])) + " step11_absent=" + ",".join(cover["absent_sources"] or ["none"])
          + " structure_flags=" + str(len(result["structure_flags"])))
    if cover["unmapped"] or cover["absent_sources"]:
        # Coverage of step 11 cannot be shown without every step-11 output.
        print("refused=" + ("step11_unmapped_fill" if cover["unmapped"] else "step11_outputs_absent"), file=sys.stderr)
        return 2
    return 0 if all(v["fail"] == 0 for v in counts.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
