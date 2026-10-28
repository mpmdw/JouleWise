#!/usr/bin/env python3
"""Compare L9's block-5 dry-run restricted outputs with the independent recompute.

Standard library only; imports no repository code, in particular none of L9's analysis package.
Inputs: L9's dry-run custody root (its record and restricted folder), the
recompute's --member-detail output, and a bar-set config. No bar is coded here:
every numeric family's bar comes from the config, and a family the config does
not name refuses the run.

Rules (RC-CMP-1 A1-A4):
- numeric families pass when both sides are finite numbers within the family bar;
- categorical families (outcome words, dominance branch, p42 status, Holm order,
  the recompute's exclusion re-derivation) pass only on exact equality;
- a value missing or null on either side is DISAGREE;
- every leaf of the step-11 outputs (fill input and disclosure record) must match
  a coverage rule, either a comparison family or a listed uncovered reason; an
  unmapped leaf refuses the run;
- stdout carries per-family pass/fail counts and structure codes only; values and
  observed differences go only to the restricted output file.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys

SCHEMA = "joulewise.b5_recompute_comparison.v1"
BARS_SCHEMA = "joulewise.b5_comparator_bars.v1"
RECORD = "dry-run/B5-BLIND-DRY-RUN-RECORD.json"
RESTRICTED = "dry-run/restricted"
PACKS = {"alpha": "ALPHA", "beta": "BETA", "gamma": "GAMMA"}
MODELS = {"alpha": "Qwen3-1.7B-4bit", "beta": "Qwen3-8B-4bit"}
NUMERIC = ("run_phase_energy_j", "floor_j", "floor_gate_j", "dominance_ratio", "reported_cell_j",
           "contrast_j", "contrast_p", "b_op_s", "count")
CATEGORICAL = ("outcome_word", "dominance_branch", "p42_status", "holm_order", "exclusions_rederivation")


class Refusal(Exception):
    """A structure-only reason the comparison cannot be evaluated."""


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def get(obj, *keys, default=None):
    for key in keys:
        if isinstance(obj, dict) and key in obj:
            obj = obj[key]
        elif isinstance(obj, list) and isinstance(key, int) and -len(obj) <= key < len(obj):
            obj = obj[key]
        else:
            return default
    return obj


def load_bars(path):
    try:
        bars = json.loads(Path(path).read_bytes())
    except (OSError, ValueError):
        raise Refusal("bars_unreadable") from None
    if not isinstance(bars, dict) or bars.get("schema") != BARS_SCHEMA or not isinstance(bars.get("families"), dict):
        raise Refusal("bars_invalid")
    for family in NUMERIC:
        spec = bars["families"].get(family)
        if not isinstance(spec, dict):
            raise Refusal("bars_family_missing:" + family)
        for key in ("absolute", "relative"):
            if key in spec and (not finite(spec[key]) or spec[key] < 0):
                raise Refusal("bars_invalid:" + family)
        if "printed_decimals" in spec and (type(spec["printed_decimals"]) is not int or spec["printed_decimals"] < 0):
            raise Refusal("bars_invalid:" + family)
        if not {"absolute", "relative", "printed_decimals"} & set(spec):
            raise Refusal("bars_invalid:" + family)
    return bars


def bar_for(spec, reference):
    parts = [spec.get("absolute", 0.0), spec.get("relative", 0.0) * abs(reference)]
    if "printed_decimals" in spec:
        parts.append(0.5 * 10.0 ** -spec["printed_decimals"])
    return max(parts)


class Comparison:
    def __init__(self, bars):
        self.bars, self.rows = bars, []

    def numeric(self, family, key, l9, ours):
        assert family in NUMERIC, family
        row = {"family": family, "key": key, "l9": l9, "recompute": ours}
        if finite(l9) and finite(ours):
            row["difference"] = ours - l9
            row["bar"] = bar_for(self.bars["families"][family], l9)
            row["verdict"] = "AGREE" if abs(ours - l9) <= row["bar"] else "DISAGREE"
        else:
            row["verdict"], row["reason"] = "DISAGREE", "missing_or_null"
        self.rows.append(row)
        return row

    def exact(self, family, key, l9, ours):
        assert family in CATEGORICAL, family
        missing = l9 is None or ours is None
        row = {"family": family, "key": key, "l9": l9, "recompute": ours,
               "verdict": "AGREE" if not missing and l9 == ours else "DISAGREE"}
        if missing:
            row["reason"] = "missing_or_null"
        self.rows.append(row)
        return row

    def keys(self):
        return {(row["family"], row["key"]) for row in self.rows}

    def counts(self):
        counts = {family: {"pass": 0, "fail": 0} for family in NUMERIC + CATEGORICAL}
        for row in self.rows:
            counts[row["family"]]["pass" if row["verdict"] == "AGREE" else "fail"] += 1
        return counts


class Custody:
    """L9's dry-run custody: every file used must be listed in the record with its digest."""
    def __init__(self, root):
        self.root = Path(root)
        self.restricted = self.root / RESTRICTED
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
        return json.loads(raw)

    def one(self, pattern):
        names = self.names(pattern)
        if len(names) > 1:
            raise Refusal("l9_output_ambiguous")
        return self.read(names[0]) if names else None


def compare_runs(c, custody, ours):
    """S-13's per-run term: each kept run's phase energies (and gross request energy)."""
    members = ours.get("members")
    if not isinstance(members, dict):
        raise Refusal("recompute_member_detail_missing")
    for name in custody.names(r"rereduced/(alpha|beta|gamma)/[^/]+\.rereduced\.json"):
        pack, file = name.split("/")[1:]
        rid = file[:-len(".rereduced.json")]
        l9 = custody.read(name)
        mine = get(members, PACKS[pack], rid, "E_j", default={})
        for phase in ("prefill", "decode"):
            c.numeric("run_phase_energy_j", pack + "/" + rid + "/" + phase,
                      get(l9, "phase_energy_j", phase), get(mine, phase))
        c.numeric("run_phase_energy_j", pack + "/" + rid + "/request", l9.get("gross_energy_j"), get(mine, "request"))


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


def compare_floors(c, custody, ours):
    for pack in ("alpha", "beta"):
        report = custody.one(r"mint/[0-9a-f]{64}-extraction-" + pack + r"\.json")
        if report is None:
            c.exact("p42_status", pack + "/extraction", None, get(ours, "p42", "df-ph-prefill-p42-" + tag(pack), "status"))
            continue
        for cell in report.get("cells", []):
            cid, kind = cell.get("cell_id"), cell.get("kind")
            if "p42" in cid:
                # Registered p42 exit: the p42 floor cells are not extractable (step 4 p42_floor_cells_only).
                l9 = "expected_unresolvable" if cell.get("extractable") is False else "extractable"
                c.exact("p42_status", pack + "/" + cid, l9, get(ours, "p42", "df-ph-prefill-p42-" + tag(pack), "status"))
                continue
            key = MODELS[pack] + "/" + cell_phase(cid) + "/" + kind
            mine = get(ours, "floors", key, default={})
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
    model = MODELS["alpha"] if "-qwen3-1p7b-" in cell_id else MODELS["beta"] if "-qwen3-8b-" in cell_id else None
    return model, cell_phase(cell_id)


def compare_aggregate(c, custody, ours):
    floor = custody.one(r"mint/[0-9a-f]{64}-aggregate-floor\.json")
    for cell in (floor or {}).get("cells", []):
        model, phase = floor_cell_key(cell.get("cell_id", ""))
        mine = get(ours, "floor_cells", str(model) + "/" + phase, default={})
        for field in ("floor_abs_j", "floor_cmp_j", "floor_gate_j"):
            c.numeric("floor_gate_j", str(model) + "/" + phase + "/" + field, cell.get(field), mine.get(field))
    if floor is None:
        c.numeric("floor_gate_j", "aggregate_floor", None, None)
    closeout = custody.one(r"finalized/outputs/closeout\.json")
    ratios = custody.one(r"finalized/outputs/closeout\.ratio-table\.json")
    c.exact("dominance_branch", "branch", get(closeout, "branch"), get(ours, "dominance", "branch"))
    for row in get(ratios, "ratios", default=[]) or [{}]:
        model, phase = floor_cell_key(row.get("cell_id", ""))
        common = row.get("numerator_field", "").startswith("common_mode")
        key = str(model) + "/" + phase + "/" + str(row.get("component"))
        mine = get(ours, "dominance", "common_mode" if common else "ratios",
                   key.rsplit("/", 1)[0] if common else key, default={})
        label = key + ("/common_mode" if common else "")
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


def compare_contrasts(c, custody, ours):
    verdicts = custody.one(r"outputs/[0-9a-f]{64}-claim-verdicts\.json")
    mine_all = ours.get("contrasts") if isinstance(ours.get("contrasts"), dict) else {}
    l9_p, our_p = {}, {}
    for row in get(verdicts, "contrasts", default=[]) or [{}]:
        cid = row.get("contrast_id")
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
        multiplicity = row.get("multiplicity") or {}
        c.numeric("contrast_p", f"{cid}/raw_p", multiplicity.get("raw_p"), mine.get("p"))
        c.numeric("contrast_p", f"{cid}/adjusted_p", multiplicity.get("adjusted_p"), mine.get("holm_p"))
        c.exact("outcome_word", f"{cid}/holm_reject", multiplicity.get("rejected"), mine.get("holm_reject"))
        c.numeric("count", f"{cid}/n", est.get("n"), mine.get("n"))
        evaluation = row.get("claim_evaluation") or {}
        c.exact("outcome_word", f"{cid}/outcome", evaluation.get("outcome"), mine.get("outcome"))
        # L9 names a direction only for a supported claim; "none" is a value, absence is not.
        c.exact("outcome_word", f"{cid}/direction", evaluation.get("direction") or "none" if evaluation else None,
                (mine.get("direction") if mine.get("outcome") == "direction_supported" else "none") if mine else None)
        c.exact("outcome_word", f"{cid}/ceiling", evaluation.get("claim_level_ceiling"), mine.get("ceiling"))
        l9_p[cid], our_p[cid] = multiplicity.get("raw_p"), mine.get("p")
        loo_l9 = {r.get("omitted_block_id"): r for r in get(row, "loo", "rows", default=[])}
        for mine_loo in mine.get("loo") or []:
            block = next((b for b in loo_l9 if b and b.endswith("-b%02d" % mine_loo.get("block_number", -1))), None)
            l9_loo = loo_l9.pop(block, {})
            key = f"{cid}/loo/b%02d" % mine_loo.get("block_number", -1)
            c.numeric("contrast_j", key + "/dbar_j", l9_loo.get("estimate"), mine_loo.get("dbar_j"))
            c.numeric("contrast_p", key + "/raw_p", l9_loo.get("raw_p"), mine_loo.get("p"))
            c.numeric("contrast_p", key + "/adjusted_p", l9_loo.get("adjusted_p"), mine_loo.get("holm_p"))
            c.exact("outcome_word", key + "/outcome", l9_loo.get("outcome"), mine_loo.get("outcome"))
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


KIND_ORDER = ("E_clock_anchor_shift_bound_j", "E_interpolation_joint_edge_bound_j", "E_whole_window_drift_allowance_j")


def compare_reported(c, custody, ours):
    """Step 10: each pack's reported cells (estimator 1) against the recompute's reported_cells."""
    for pack in ("alpha", "beta"):
        projection = custody.one(r"outputs/[0-9a-f]{64}-projection-" + pack + r"\.json")
        cells = get(projection, "cells", default=[]) if projection is not None else [{}]
        for cell in cells:
            phase = cell.get("phase") or "missing"
            cid = f"df-ph-{'decode' if phase == 'decode' else 'prefill-p2048'}-{tag(pack)}"
            mine = get(ours, "reported_cells", cid, default={})
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
            c.numeric("count", key + "/interval/df", ivl.get("df"), ours_ivl.get("df"))
        for refused in get(projection, "refused_cells", default=[]) or []:
            if "p42" in str(refused.get("cell_id")):
                c.exact("p42_status", pack + "/" + refused["cell_id"], "expected_unresolvable",
                        get(ours, "p42", "df-ph-prefill-p42-" + tag(pack), "status"))


def compare_exclusions(c, ours):
    for pack in sorted(PACKS.values()):
        # L9 consumes derived/exclusions.json; the recompute re-derives it from the flags (AN-18 partial).
        c.exact("exclusions_rederivation", pack, "agrees", get(ours, "exclusions_rederivation", pack, "status"))


# Step-11 coverage. Each leaf of the fill input and the disclosure record has a path
# like gamma/contrasts/*/estimate (list indices become *). A rule is a regular
# expression over that path and either a family whose comparisons cover it or
# "uncovered:<reason>". The first matching rule wins; an unmatched leaf refuses.
STEP11_SOURCES = (("fill", r"outputs/[0-9a-f]{64}-results-fill-input\.json"),
                  ("disclosure", r"disclosures/[^/]+\.json"))
COVERAGE = ()


def leaves(value, path=""):
    if isinstance(value, dict) and value:
        for key, item in value.items():
            yield from leaves(item, path + "/" + str(key) if path else str(key))
    elif isinstance(value, list) and value:
        for item in value:
            yield from leaves(item, path + "/*")
    else:
        yield path


def coverage(custody, comparison, rules=None):
    rules = COVERAGE if rules is None else rules
    report, unmapped, absent = {}, [], []
    families = {family for family, _ in comparison.keys()}
    for label, pattern in STEP11_SOURCES:
        names = custody.names(pattern)
        if not names:
            absent.append(label)
        for name in names:
            for leaf in sorted(set(leaves(custody.read(name)))):
                path = label + ":" + leaf
                rule = next((r for r in rules if re.fullmatch(r[0], path)), None)
                if rule is None:
                    unmapped.append(path)
                    continue
                target = rule[1]
                if not target.startswith("uncovered:") and target not in families:
                    # Mapped to a family that produced no comparison: that is not coverage.
                    unmapped.append(path)
                    continue
                report[path] = target
    return {"leaves": report, "unmapped": sorted(set(unmapped)), "absent_sources": absent}


def run(l9_custody, recompute_path, bars_path, rules=None):
    bars = load_bars(bars_path)
    custody = Custody(l9_custody)
    try:
        ours = json.loads(Path(recompute_path).read_bytes())
    except (OSError, ValueError):
        raise Refusal("recompute_output_unreadable") from None
    c = Comparison(bars)
    compare_runs(c, custody, ours)
    compare_brackets(c, custody, ours)
    compare_floors(c, custody, ours)
    compare_aggregate(c, custody, ours)
    compare_contrasts(c, custody, ours)
    compare_reported(c, custody, ours)
    compare_exclusions(c, ours)
    cover = coverage(custody, c, rules)
    return {"schema": SCHEMA, "bar_set": bars.get("bar_set"), "bars": bars["families"],
            "l9_steps": {f"{s}/{w}" if w else str(s): v for (s, w), v in sorted(custody.status.items(), key=str)},
            "recompute_program_sha256": ours.get("program_sha256"), "counts": c.counts(),
            "coverage": cover, "comparisons": c.rows}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--l9-custody", required=True, help="L9 dry-run custody root")
    parser.add_argument("--recompute", required=True, help="independent recompute --member-detail output")
    parser.add_argument("--bars", required=True, help="bar-set config (joulewise.b5_comparator_bars.v1)")
    parser.add_argument("--restricted-out", required=True, help="restricted file for values and differences")
    args = parser.parse_args(argv)
    try:
        result = run(args.l9_custody, args.recompute, args.bars)
        out = Path(args.restricted_out)
        if out.exists():
            raise Refusal("restricted_output_exists")
        out.write_text(json.dumps(result, sort_keys=True, indent=1, allow_nan=False) + "\n")
    except Refusal as exc:
        print("refused=" + str(exc), file=sys.stderr)
        return 2
    except Exception as exc:
        print("error=internal " + type(exc).__name__, file=sys.stderr)
        return 2
    counts = result["counts"]
    cover = result["coverage"]
    # Public line: per-family pass/fail counts and structure only, never a value or a difference.
    print("bar_set=" + str(result["bar_set"]) + " families=" + json.dumps(counts, sort_keys=True, separators=(",", ":"))
          + " step11_unmapped=" + str(len(cover["unmapped"])) + " step11_absent=" + ",".join(cover["absent_sources"] or ["none"]))
    if cover["unmapped"] or cover["absent_sources"]:
        # Coverage of step 11 cannot be shown without every step-11 output.
        print("refused=" + ("step11_unmapped_fill" if cover["unmapped"] else "step11_outputs_absent"), file=sys.stderr)
        return 2
    return 0 if all(v["fail"] == 0 for v in counts.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
