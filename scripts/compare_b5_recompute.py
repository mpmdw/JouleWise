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
  the recompute's exclusion re-derivation, routing ids) pass only on equal type and value;
- a value missing or null on either side is DISAGREE;
- one union, one key space (RC-CMP-5 S3): every family pairs L9's keyed items with
  the recompute's through Comparison.pairs, which takes the union of keys and
  writes a routing_id row per key, so a key on one side only is DISAGREE
  missing_or_null; two items under one key on one side, or two rows under one
  (family, key), refuse the run as a structure fault;
- the whole-machine meter line (RC-CMP-2 M4): per member of the union of L9's
  disclosure, the recompute's windows and the harvest meter record, the
  disclosure's rho, dE_rail and dE_machine, and the record's gross meter energy,
  baseline power, battery term, sample counts and window, against the
  recompute's request phase; a disclosed window with no record is DISAGREE; the
  per-model order statistics are re-derived from the recompute's member values
  (RC-CMP-3 X2), and the central band's window is the recompute's own (S2);
- every leaf of the step-11 outputs (fill input and disclosure record) must match
  a coverage rule. A family rule names the comparison row the leaf copies, and
  the leaf is covered only if that row exists, its L9 value equals the leaf in
  type and value, the row is AGREE, and every item routing it is present on both
  sides (RC-CMP-3 X1). The row's key is built only from path components, the
  identity fields of the enclosing containers and list positions, never from an
  attribute the line asserts (S2). Numbers are denied by default (S1): a leaf
  that is a number, null, or read from a NaN or Infinity is numeric-class; an
  "uncovered:" rule matches strings and booleans only; a numeric-class leaf is
  uncovered only by an "uncovered-by-name:" rule (or, when null, an
  "uncovered-null-by-name:" rule), and every such leaf is listed (X6). Any other
  leaf refuses the run;
- a NaN or Infinity in an input becomes null with a structure flag naming its
  leaf paths (X7); one in a step-11 output refuses the run (S1);
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
               "battery_term", "routing_id")
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
        self.bars, self.rows, self.scope, self.seen = bars, [], [], set()

    def add(self, row):
        if (row["family"], row["key"]) in self.seen:
            # One key space (RC-CMP-5 S3): a second row under a key is a structure fault, never shadowed.
            raise Refusal("row_key_duplicated:" + row["family"])
        self.seen.add((row["family"], row["key"]))
        if self.scope:
            row["items"] = list(self.scope)
        self.rows.append(row)
        return row

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
        return self.add(row)

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
        return self.add(row)

    def pairs(self, scope, *sides):
        """The one union (S3): each key of any side, with each side's item (None where absent).

        The sides are maps; the last is the recompute's, the others L9's. Each key gets a
        routing_id row (scope + key): the key on L9's sides against the key on the
        recompute's, so a key on one side only is DISAGREE missing_or_null. Rows built
        for the key carry its routing_id key, which coverage requires to agree (S2).
        """
        for key in sorted(set().union(*sides), key=str):
            name = scope + ("/".join(map(str, key)) if isinstance(key, tuple) else str(key))
            self.exact("routing_id", name, name if all(key in side for side in sides[:-1]) else None,
                       name if key in sides[-1] else None)
            self.scope.append(name)
            try:
                yield (key,) + tuple(side.get(key) for side in sides)
            finally:
                self.scope.pop()

    def keys(self):
        return {(row["family"], row["key"]) for row in self.rows}

    def counts(self):
        counts = {family: {"pass": 0, "fail": 0} for family in NUMERIC + METER + CATEGORICAL
                  if family not in METER or family in self.bars["families"]}
        for row in self.rows:
            counts[row["family"]]["pass" if row["verdict"] == "AGREE" else "fail"] += 1
        return counts


NONFINITE = type("NonFinite", (), {})()


def step(item):
    """A list item's path component: its line word when it is a disclosure line, else *."""
    line = item.get("line") if isinstance(item, dict) else None
    return line if isinstance(line, str) and re.fullmatch(r"[a-z][a-z0-9_]*", line) else "*"


def join(path, key):
    return path + "/" + str(key) if path else str(key)


def scrub(value, path, found):
    """Nonfinite tokens to null, recording each one's leaf path (S1)."""
    if value is NONFINITE:
        found.append(path)
        return None
    if isinstance(value, dict):
        for key in value:
            value[key] = scrub(value[key], join(path, key), found)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            value[index] = scrub(item, path + "/" + step(item), found)
    return value


def loads(raw, flags, source, paths=None):
    """JSON with NaN and Infinity read as null; the flag names each such leaf path (RC-CMP-3 X7, S1)."""
    found = []
    value = scrub(json.loads(raw, parse_constant=lambda word: NONFINITE), "", found)
    flag = {"code": "nonfinite_value_read_as_null", "source": source, "count": len(found), "paths": sorted(set(found))}
    if found and flag not in flags:
        flags.append(flag)
    if paths is not None:
        paths.update(found)
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
        self.listed, self.status, self.nonfinite = {}, {}, {}
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
            return loads(raw, self.flags, "l9:" + name, self.nonfinite.setdefault(name, set()))
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


def keyed(rows, key, label, keep=lambda row: True):
    """One L9 side's list as a map by key; two items under one key refuse the run (S3).

    Family functions build every one-side collection here (or with items()), and
    iterate only Comparison.pairs or constant tuples (tests/independent_recompute/test_structural_rules.py).
    """
    result = {}
    for row in rows if isinstance(rows, list) else []:
        if not isinstance(row, dict):
            raise Refusal("item_not_an_object:" + label)
        if not keep(row):
            continue
        name = key(row)
        if name in result:
            raise Refusal("item_key_duplicated:" + label)
        result[name] = row
    return result


def positions(rows):
    """A registered-order list as a map by position (arm gates, resolutions, source ids)."""
    return dict(enumerate(rows)) if isinstance(rows, list) else {}


def sides(a, b):
    """The lower and upper bounds of two intervals, paired: (side, L9's bound, the recompute's)."""
    return tuple(zip(("lower", "upper"), interval(a), interval(b)))


def compare_runs(c, custody, ours):
    """S-13's per-run term: each kept run's phase energies (and gross request energy).

    The key set is the union of L9's re-reduced runs and the recompute's selected
    (kept) runs; a member detail without the selected field counts as selected.
    """
    members = ours.get("members")
    if not isinstance(members, dict):
        raise Refusal("recompute_member_detail_missing")
    named = rereduced_names(custody)
    selected = selected_runs(members)
    for (pack, rid), name, _ in c.pairs("run/", named, selected):
        l9 = custody.read(name) if name else {}
        mine = get(members, PACKS[pack], rid, "E_j", default={})
        for phase in ("prefill", "decode"):
            c.numeric("run_phase_energy_j", pack + "/" + rid + "/" + phase,
                      get(l9, "phase_energy_j", phase), get(mine, phase))
        c.numeric("run_phase_energy_j", pack + "/" + rid + "/request", get(l9, "gross_energy_j"), get(mine, "request"))


def rereduced_names(custody):
    named = {}
    for name in custody.names(r"rereduced/(alpha|beta|gamma)/[^/]+\.rereduced\.json"):
        pack, file = name.split("/")[1:]
        named[(pack, file[:-len(".rereduced.json")])] = name
    return named


def selected_runs(members):
    return {(pack, rid): m for pack, PACK in PACKS.items() for rid, m in (get(members, PACK) or {}).items()
            if isinstance(m, dict) and m.get("selected", True) is True}


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
    return "decode" if "decode" in str(cell_id) else "prefill"


def cell_model(cell_id):
    cell_id = str(cell_id)
    return MODELS["alpha"] if "qwen3-1p7b" in cell_id else MODELS["beta"] if "qwen3-8b" in cell_id else None


def floor_kind(cell_id):
    return next((kind for kind in ("absolute", "comparative") if str(cell_id).endswith("-" + kind)), None)


def p42_word(cells):
    """L9's p42 status from its p42 cells: the registered exit when none is extractable; None when L9 lists none."""
    cells = [cell for cell in cells if isinstance(cell, dict) and "p42" in str(cell.get("cell_id"))]
    if not cells:
        return None
    return "expected_unresolvable" if all(cell.get("extractable") is False for cell in cells) else "extractable"


def compare_floors(c, custody, ours):
    for pack in ("alpha", "beta"):
        report = custody.one(r"mint/[0-9a-f]{64}-extraction-" + pack + r"\.json")
        cells = (report or {}).get("cells", [])
        # Registered p42 exit: the p42 floor cells are not extractable (step 4 p42_floor_cells_only).
        c.exact("p42_status", pack + "/extraction/p42", p42_word(cells if isinstance(cells, list) else []),
                get(ours, "p42", "df-ph-prefill-p42-" + tag(pack), "status"))
        l9_cells = keyed(cells, lambda cell: MODELS[pack] + "/" + cell_phase(cell.get("cell_id")) + "/" + str(cell.get("kind")),
                         "extraction_cell", lambda cell: "p42" not in str(cell.get("cell_id")))
        mine_cells = items(ours.get("floors"), lambda key, _: key.startswith(MODELS[pack] + "/"))
        for key, cell, mine in c.pairs("floor/", l9_cells, mine_cells):
            cell, mine = cell or {}, mine or get(ours, "floors", key, default={}) or {}
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


def aggregate_key(cell):
    return "/".join(map(str, floor_cell_key(cell.get("cell_id", ""))))


def ratio_label(row):
    model, phase = floor_cell_key(row.get("cell_id", ""))
    common = str(row.get("numerator_field", "")).startswith("common_mode")
    return f"{model}/{phase}/{row.get('component')}" + ("/common_mode" if common else "")


def our_ratios(ours):
    mine = dict(items(get(ours, "dominance", "ratios")))
    mine.update({key + "/comparative/common_mode": item for key, item in items(get(ours, "dominance", "common_mode")).items()})
    return mine


def compare_aggregate(c, custody, ours):
    floor = custody.one(r"mint/[0-9a-f]{64}-aggregate-floor\.json")
    l9_cells = keyed((floor or {}).get("cells", []), aggregate_key, "aggregate_cell")
    for key, cell, mine in c.pairs("aggregate/", l9_cells, items(ours.get("floor_cells"))):
        cell, mine = cell or {}, mine or {}
        for field in ("floor_abs_j", "floor_cmp_j", "floor_gate_j"):
            c.numeric("floor_gate_j", key + "/" + field, cell.get(field), mine.get(field))
    if floor is None:
        c.numeric("floor_gate_j", "aggregate_floor", None, None)
    closeout = custody.one(r"finalized/outputs/closeout\.json")
    ratios = custody.one(r"finalized/outputs/closeout\.ratio-table\.json")
    c.exact("dominance_branch", "branch", get(closeout, "branch"), get(ours, "dominance", "branch"))
    l9_rows, mine_rows = keyed(get(ratios, "ratios", default=[]), ratio_label, "ratio"), our_ratios(ours)
    if not l9_rows and not mine_rows:
        c.numeric("dominance_ratio", "ratio/none", None, None)
    # Ratio rows have their own key prefix: a ratio's n is not its floor cell's n (S3, Opus N2).
    for label, row, mine in c.pairs("ratio/", l9_rows, mine_rows):
        row, mine, common = row or {}, mine or {}, label.endswith("/common_mode")
        key = "ratio/" + label
        c.numeric("dominance_ratio", key + "/ratio", row.get("ratio"), mine.get("R_cm" if common else "R"))
        c.numeric("floor_j", key + "/numerator_j", row.get("numerator_j"), mine.get("numerator_j"))
        c.numeric("floor_j", key + "/denominator_j", row.get("denominator_j"), mine.get("denominator_j"))
        c.numeric("count", key + "/n", row.get("n"), mine.get("n"))


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


def block_key(number):
    """A block number (the recompute's int, or L9's printed string) -> b03."""
    number = str(number)
    return "b%02d" % int(number) if number.isdigit() else None


def kept_blocks(blocks):
    return sorted(b["block_id"] for b in blocks if b.get("included") is True) if isinstance(blocks, list) else None


# The recompute's arms (S2): arm A is the a1/a2 runs on ALPHA's model, arm B the b runs on
# BETA's, in this registered order; each kept unit carries the tag sw-<arm>-<a|b>-<model tag>.
ARMS = {0: "alpha", 1: "beta"}


def arm_condition(cid, pack):
    return f"sw-{'decode' if cell_phase(cid) == 'decode' else 'prefill-p2048'}-{'a' if pack == 'alpha' else 'b'}-{tag(pack)}"


def compare_arms(c, ours, cid, floor):
    """A v3 floor's arm gates and resolutions, by registered position against the recompute's arm (S2).

    The arm a gate or resolution belongs to is its position, never its printed condition;
    the printed arm_id, condition_family_id and source cell ids are compared as routing_id rows.
    """
    cells, phase = ours.get("floor_cells"), cell_phase(cid)
    if "arm_gates" in floor:
        for index, gate, pack in c.pairs(f"contrast/{cid}/arm/", positions(floor["arm_gates"]), ARMS):
            gate = gate if isinstance(gate, dict) else {}
            c.exact("routing_id", f"contrast/{cid}/arm/{index}/arm_id", gate.get("arm_id"),
                    {"alpha": "A", "beta": "B"}.get(pack))
            c.exact("routing_id", f"contrast/{cid}/arm/{index}/condition_family_id", gate.get("condition_family_id"),
                    arm_condition(cid, pack) if pack else None)
            c.numeric("floor_gate_j", f"{cid}/arm/{index}/floor_gate_j", gate.get("floor_gate_j"),
                      get(cells, f"{MODELS.get(pack)}/{phase}", "floor_gate_j"))
    if "resolutions" in floor:
        for index, resolution, pack in c.pairs(f"contrast/{cid}/resolution/", positions(floor["resolutions"]), ARMS):
            resolution = resolution if isinstance(resolution, dict) else {}
            cell = f"{MODELS.get(pack)}/{phase}"
            for field in ("floor_abs_j", "floor_cmp_j", "floor_gate_j"):
                c.numeric("floor_gate_j", f"{cid}/resolution/{index}/{field}", resolution.get(field), get(cells, cell, field))
            sources = positions(resolution.get("source_cell_ids"))
            for number, source, own in c.pairs(f"contrast/{cid}/resolution/{index}/source/", sources, {0: cell}):
                c.exact("routing_id", f"contrast/{cid}/resolution/{index}/source_cell_ids/{number}",
                        "/".join(map(str, floor_cell_key(source))) if isinstance(source, str) else None, own, raw=source)


def compare_contrasts(c, custody, ours):
    verdicts = custody.one(r"outputs/[0-9a-f]{64}-claim-verdicts\.json")
    l9_rows = keyed(get(verdicts, "contrasts", default=[]), lambda row: row.get("contrast_id"), "contrast")
    mine_all = items(ours.get("contrasts"))
    if not l9_rows and not mine_all:
        c.numeric("contrast_j", "contrasts", None, None)
    l9_p, our_p = {}, {}
    for cid, row, mine in c.pairs("contrast/", l9_rows, mine_all):
        row, mine = row or {}, mine or {}
        est = row.get("estimator") or {}
        c.numeric("contrast_j", f"{cid}/dbar_j", est.get("estimate"), mine.get("dbar_j"))
        c.numeric("contrast_j", f"{cid}/s_d_j", est.get("s_d"), mine.get("s_d_j"))
        c.numeric("contrast_j", f"{cid}/se_j", est.get("SE_total"), mine.get("se_j"))
        c.numeric("contrast_p", f"{cid}/t_critical", est.get("t_critical_95"), mine.get("t_star"))
        for side, a, b in sides(est.get("metrology_aware_CI95"), mine.get("metrology_interval_j")):
            c.numeric("contrast_j", f"{cid}/metrology_interval_j/{side}", a, b)
        bounds = row.get("deterministic_bounds") or {}
        c.numeric("contrast_j", f"{cid}/D_j", bounds.get("total"), mine.get("D_j"))
        for side, a, b in sides(bounds.get("decision_interval"), mine.get("decision_interval_j")):
            c.numeric("contrast_j", f"{cid}/decision_interval_j/{side}", a, b)
        c.numeric("floor_gate_j", f"{cid}/active_floor_j", get(row, "floor", "active_floor_j"), mine.get("floor_gate_j"))
        for field in ("floor_abs_j", "floor_cmp_j"):
            c.numeric("floor_gate_j", f"{cid}/{field}", get(row, "floor", field),
                      contrast_floor_part(ours.get("floor_cells"), str(cid), field))
        compare_arms(c, ours, cid, row.get("floor") if isinstance(row.get("floor"), dict) else {})
        multiplicity = row.get("multiplicity") or {}
        c.numeric("contrast_p", f"{cid}/raw_p", multiplicity.get("raw_p"), mine.get("p"))
        c.numeric("contrast_p", f"{cid}/adjusted_p", multiplicity.get("adjusted_p"), mine.get("holm_p"))
        c.exact("outcome_word", f"{cid}/holm_reject", multiplicity.get("rejected"), mine.get("holm_reject"))
        c.numeric("count", f"{cid}/n", est.get("n"), mine.get("n"))
        c.numeric("count", f"{cid}/df", est.get("df"), mine["n"] - 1 if finite(mine.get("n")) else None)
        c.exact("kept_units", f"{cid}/kept_quads", kept_blocks(get(row, "bundle_blocks", "blocks", default=None)),
                sorted(mine["kept_quads"]) if mine.get("kept_quads") else None)
        evaluation = row.get("claim_evaluation") or {}
        c.exact("outcome_word", f"{cid}/outcome", evaluation.get("outcome"), mine.get("outcome"))
        # L9 names a direction only for a supported claim; "none" is a value, absence is not.
        c.exact("outcome_word", f"{cid}/direction", evaluation.get("direction") or "none" if evaluation else None,
                (mine.get("direction") if mine.get("outcome") == "direction_supported" else "none") if mine else None,
                raw=evaluation.get("direction") if "direction" in evaluation else MISSING)
        c.exact("outcome_word", f"{cid}/ceiling", evaluation.get("claim_level_ceiling"), mine.get("ceiling"))
        l9_p[cid], our_p[cid] = multiplicity.get("raw_p"), mine.get("p")
        loo_l9 = keyed(get(row, "loo", "rows", default=[]), lambda r: loo_key(r.get("omitted_block_id")), "loo_row")
        loo_mine = keyed(mine.get("loo"), lambda r: block_key(r.get("block_number")), "recompute_loo_row")
        for block, l9_loo, mine_loo in c.pairs(f"contrast/{cid}/loo/", loo_l9, loo_mine):
            l9_loo, mine_loo = l9_loo or {}, mine_loo or {}
            key = f"{cid}/loo/{block}"
            c.numeric("contrast_j", key + "/dbar_j", l9_loo.get("estimate"), mine_loo.get("dbar_j"))
            c.numeric("contrast_p", key + "/raw_p", l9_loo.get("raw_p"), mine_loo.get("p"))
            c.numeric("contrast_p", key + "/adjusted_p", l9_loo.get("adjusted_p"), mine_loo.get("holm_p"))
            c.exact("outcome_word", key + "/outcome", l9_loo.get("outcome"), mine_loo.get("outcome"))
            for name, other in (("metrology_aware_ci95", "metrology_interval_j"), ("decision_interval", "decision_interval_j")):
                for side, a, b in sides(l9_loo.get(name), mine_loo.get(other)):
                    c.numeric("contrast_j", f"{key}/{other}/{side}", a, b)
            c.numeric("count", key + "/n", l9_loo.get("n_blocks"), mine_loo.get("n"))
            c.numeric("count", key + "/df", l9_loo.get("df"), mine_loo["n"] - 1 if finite(mine_loo.get("n")) else None)
            above = mine_loo.get("above_floor")
            c.exact("outcome_word", key + "/floor_status", l9_loo.get("floor_status"),
                    None if above is None else "above_floor" if above else "not_above_floor")
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


def unit_list(kept):
    return sorted((u.get("stratum"), u.get("unit_id")) for u in kept) if isinstance(kept, list) else None


def our_units(kept):
    return sorted((s, u) for s, units in (kept or {}).items() for u in units) or None


def compare_reported(c, custody, ours):
    """Step 10: each pack's reported cells (estimator 1) against the recompute's reported_cells."""
    for pack in ("alpha", "beta"):
        projection = custody.one(r"outputs/[0-9a-f]{64}-projection-" + pack + r"\.json")
        if projection is None:
            c.numeric("reported_cell_j", pack + "/projection", None, None)
        l9_cells = keyed(get(projection, "cells", default=[]), lambda cell: reported_cid(pack, cell.get("phase") or "missing"),
                         "projection_cell")
        mine_cells = items(ours.get("reported_cells"), lambda key, _: key.endswith("-" + tag(pack)) and "p42" not in key)
        for cid, cell, _ in c.pairs(f"reported/{pack}/", l9_cells, mine_cells):
            cell = cell or {}
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
            c.exact("kept_units", key + "/kept_units", unit_list(cell.get("kept_units")), our_units(mine.get("kept_units")))
            c.numeric("count", key + "/interval/df", ivl.get("df"), ours_ivl.get("df"))
        # The registered p42 exit, when L9's projection lists its refused p42 cells.
        refused = refused_p42(get(projection, "refused_cells", default=[]))
        if refused is not None:
            c.exact("p42_status", pack + "/projection/p42", refused, get(ours, "p42", "df-ph-prefill-p42-" + tag(pack), "status"))


def refused_p42(cells):
    return p42_word([dict(cell, extractable=False) for cell in cells if isinstance(cell, dict)]) if isinstance(cells, list) else None


def any_finite(values):
    return any(finite(v) for v in values.values())


def labelled(custody, pattern, label):
    return next((r for r in (custody.read(n) for n in custody.names(pattern)) if get(r, "label") == label), None)


def by_pack(windows):
    return {pack: window for pack, PACK in PACKS.items() for window in [get(windows, PACK)] if window is not None}


def sensitivity_reported(cells):
    return keyed(cells, lambda cell: (cell.get("pack"), str(cell.get("cell_id", "")).replace("d117-reported-mean-ph-", "df-ph-")),
                 "sensitivity_reported_cell")


def our_sensitivity_reported(line, ours):
    """The recompute's sensitivity cells, and its p42 cells (L9 lists them as refused cells)."""
    cells = dict(items(line.get("reported_cells"), lambda key, _: "p42" not in key))
    cells.update({cid: item for cid, item in (ours.get("p42") or {}).items() if "p42" in cid})
    return {(pack, cid): item for cid, item in cells.items() for pack in ("alpha", "beta") if cid.endswith("-" + tag(pack))}


def compare_sensitivity(c, custody, ours):
    """Step 11 sensitivity line (registered B_max bound) against the recompute's sensitivity_bound line."""
    record = labelled(custody, r"outputs/[0-9a-f]{64}\.json", "sensitivity")
    line = get(ours, "disclosures", "sensitivity_bound", default={}) or {}
    if record is None:
        c.numeric("floor_gate_j", "sensitivity/record", None, None)
        return
    c.numeric("b_op_s", "sensitivity/B_max_s", get(record, "b_max", "value_s"), line.get("B_max_s"))
    c.numeric("count", "sensitivity/T", get(record, "b_max", "T"), line.get("T"))
    c.numeric("count", "sensitivity/attained_by_sequence", get(record, "b_max", "attained_by_sequence"),
              line.get("attaining_sequence"))
    windows = record.get("windows") if isinstance(record.get("windows"), dict) else {}
    for pack, _, _ in c.pairs("sensitivity/windows/", windows, by_pack(ours.get("windows"))):
        c.numeric("b_op_s", f"sensitivity/windows/{pack}/b_op_s", get(record, "windows", pack, "b_op_s"),
                  get(ours, "windows", PACKS.get(pack, ""), "b_op_s"))
        c.numeric("b_op_s", f"sensitivity/windows/{pack}/b_sens_s", get(record, "windows", pack, "b_sens_s"),
                  get(line, "windows", PACKS.get(pack, ""), "b_sens_s"))
    cells = keyed(record.get("floor_cells", []), aggregate_key, "sensitivity_floor_cell")
    for key, cell, _ in c.pairs("sensitivity/floor_cells/", cells, items(line.get("floor_cells"))):
        cell, mine = cell or {}, get(line, "floor_cells", key, default={}) or {}
        for field in ("floor_abs_j", "floor_cmp_j", "floor_gate_j"):
            c.numeric("floor_gate_j", f"sensitivity/{key}/{field}", get(cell, "sensitivity", field), mine.get(field))
        c.numeric("floor_j", f"sensitivity/{key}/allowance_j", get(cell, "sensitivity", "allowance_j"),
                  get(line, "floors", key + "/absolute", "allowance_j"))
    rows = keyed(record.get("contrasts", []), lambda row: row.get("contrast_id"), "sensitivity_contrast")
    for cid, row, _ in c.pairs("sensitivity/contrasts/", rows, items(line.get("contrasts"))):
        row, mine = row or {}, get(line, "contrasts", cid, default={}) or {}
        c.numeric("contrast_j", f"sensitivity/{cid}/D_j", get(row, "sensitivity", "D_j"), mine.get("D_j"))
        c.numeric("floor_gate_j", f"sensitivity/{cid}/floor_gate_j", get(row, "sensitivity", "floor_gate_j"),
                  mine.get("floor_gate_j"))
        for field in ("floor_abs_j", "floor_cmp_j"):
            c.numeric("floor_gate_j", f"sensitivity/{cid}/{field}", get(row, "sensitivity", field),
                      contrast_floor_part(line.get("floor_cells"), str(cid), field))
        c.exact("outcome_word", f"sensitivity/{cid}/outcome", get(row, "sensitivity", "outcome"), mine.get("outcome"))
    reported = sensitivity_reported(record.get("reported_cells", []))
    for (pack, cid), cell, _ in c.pairs("sensitivity/reported_cells/", reported, our_sensitivity_reported(line, ours)):
        cell = cell or {}
        mine = get(line, "reported_cells", cid, default={}) or {}
        sens = cell.get("sensitivity") or {}
        if "p42" in cid:
            # The registered p42 exit: no reported value on either side; compared as a status, not as numbers.
            l9 = "expected_unresolvable" if not any_finite(sens) else "computed"
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


def pack_of_model(model):
    return next((p for p, m in MODELS.items() if m == model), None)


def pack_of_cell(cid):
    return next((p for p in ("alpha", "beta") if str(cid).endswith("-" + tag(p))), None)


CELL_LINES, CONTRAST_LINES = ("cross_window", "battery_assist_cell"), ("battery_assist_contrast", "magnitude_ratio",
                                                                       "magnitude_per_token", "loo_counts", "loo_magnitude")


def our_cell_lines(disclosures):
    lines = {("cross_window", pack_of_model(key.split("/", 1)[0]), reported_cid(str(pack_of_model(key.split("/", 1)[0])),
              key.split("/", 1)[-1])): item for key, item in items(disclosures.get("cross_window")).items()}
    lines.update({("battery_assist_cell", pack_of_cell(cid), cid): item
                  for cid, item in (disclosures.get("battery_assist") or {}).items()
                  if pack_of_cell(cid) and "p42" not in cid and cid.startswith("df-")})
    return lines


def our_contrast_lines(ours):
    lines = {(cid, "battery_assist_contrast"): item for cid, item in
             items(get(ours, "disclosures", "battery_assist"), lambda key, _: key.startswith("ctr-")).items()}
    for cid, item in items(ours.get("descriptive")).items():
        lines[(cid, "magnitude_ratio")] = lines[(cid, "magnitude_per_token")] = item
    for cid, item in items(ours.get("contrasts")).items():
        lines[(cid, "loo_counts")] = lines[(cid, "loo_magnitude")] = item
    return lines


def magnitude_rows(contrast):
    """The recompute's leave-one-out rows that raise PLAN 7.3's magnitude trigger (movement > a quarter of the floor)."""
    floor, estimate = contrast.get("floor_gate_j"), contrast.get("dbar_j")
    if not (finite(floor) and finite(estimate)):
        return {}
    return {block_key(row.get("block_number")): abs(row["dbar_j"] - estimate) for row in contrast.get("loo") or []
            if isinstance(row, dict) and finite(row.get("dbar_j")) and abs(row["dbar_j"] - estimate) > 0.25 * floor}


def window_line_names(window_lines):
    return {pack: keyed(lines, lambda row: row.get("line"), "window_line",
                        lambda row: row.get("line") in ("neg8_allowance", "reference_counts", "corpus_counts"))
            for pack, lines in (window_lines if isinstance(window_lines, dict) else {}).items()
            if any(isinstance(row, dict) and row.get("line") in ("neg8_allowance", "reference_counts", "corpus_counts")
                   for row in lines or [])}


def our_neg8(ours):
    return {pack: dict.fromkeys(("neg8_allowance", "reference_counts", "corpus_counts"), neg8)
            for pack, PACK in PACKS.items() for neg8 in [get(ours, "windows", PACK, "neg8")] if neg8}


def strata(value):
    return value if isinstance(value, dict) else {}


def compare_disclosures(c, custody, ours):
    """Step 11 disclosure lines that the recompute also computes."""
    names = custody.names(STEP11_SOURCES[1][1])
    record = custody.read(names[0]) if len(names) == 1 else None
    if record is None:
        c.numeric("reported_cell_j", "disclosure/record", None, None)
        return
    disclosures = ours.get("disclosures") or {}
    lines = keyed(record.get("cells", []), lambda row: (row.get("line"), row.get("pack"), reported_key(row.get("cell_id"))[0]),
                  "disclosure_cell_line", lambda row: row.get("line") in CELL_LINES)
    for (kind, pack, cid), row, _ in c.pairs("disclosure/cells/", lines, our_cell_lines(disclosures)):
        row, key = row or {}, f"disclosure/{pack}/{cid}/{kind}"
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
            for stratum, a, b in c.pairs(key + "/assist_members/", strata(row.get("assist_members")),
                                         strata(mine.get("assist_members_by_stratum"))):
                c.numeric("count", key + "/assist_members/" + stratum, a, b)
    contrasts = keyed(record.get("contrasts", []), lambda row: (row.get("contrast_id"), row.get("line")),
                      "disclosure_contrast_line", lambda row: row.get("line") in CONTRAST_LINES)
    for (cid, kind), row, _ in c.pairs("disclosure/contrasts/", contrasts, our_contrast_lines(ours)):
        row, key = row or {}, f"disclosure/{cid}/{kind}"
        if kind == "battery_assist_contrast":
            mine = get(disclosures, "battery_assist", cid, default={}) or {}
            ivl = interval(mine.get("metrology_interval_j"))
            for field, value in (("mean_j", mine.get("dbar_j")), ("lower_j", ivl[0]), ("upper_j", ivl[1]),
                                 ("s_d", mine.get("s_d_j")), ("se", mine.get("se_j"))):
                c.numeric("contrast_j", key + "/" + field, row.get(field), value)
            c.numeric("contrast_p", key + "/t_star", row.get("t_star"), mine.get("t_star"))
            c.numeric("count", key + "/n", row.get("n"), mine.get("n"))
            c.numeric("count", key + "/assist_quads", row.get("assist_quads"), mine.get("assist_quads"))
            # The union of both sides' strata (Sol round 2 finding 3).
            for stratum, a, b in c.pairs(key + "/assist_members/", strata(row.get("assist_members")),
                                         strata(mine.get("assist_members_by_stratum"))):
                c.numeric("count", key + "/assist_members/" + stratum, a, b)
        elif kind == "magnitude_ratio":
            mine = get(ours, "descriptive", cid, default={}) or {}
            ivl = interval(mine.get("ratio_interval"))
            for field, value in (("ratio", mine.get("ratio")), ("lower", ivl[0]), ("upper", ivl[1])):
                c.numeric("descriptive_ratio", key + "/" + field, row.get(field), value)
        elif kind == "magnitude_per_token":
            mine = get(ours, "descriptive", cid, default={}) or {}
            c.numeric("per_token_j", key + "/value_j", row.get("value_j"), mine.get("per_token_difference_j"))
            for name, other in (("metrology", "per_token_metrology_interval_j"), ("decision", "per_token_decision_interval_j")):
                for side, a, b in sides(row.get(name), mine.get(other)):
                    c.numeric("per_token_j", f"{key}/{name}/{side}", a, b)
        elif kind == "loo_counts":
            loo = get(ours, "contrasts", cid, "loo")
            c.numeric("count", key + "/count", row.get("count"), len(loo) if isinstance(loo, list) else None)
        else:
            # loo_magnitude: the rows raising the magnitude trigger, L9's against the recompute's own selection,
            # each with its movement |LOO estimate - estimate|.
            l9_rows = keyed(row.get("rows"), lambda item: block_key(item.get("block_number")), "loo_magnitude_row")
            for block, item, moved in c.pairs(key + "/", l9_rows, magnitude_rows(get(ours, "contrasts", cid, default={}) or {})):
                c.numeric("contrast_j", f"{key}/{block}/movement_j", (item or {}).get("movement_j"), moved)
    l9_windows = window_line_names(record.get("window_lines"))
    for pack, rows, neg8s in c.pairs("disclosure/window_lines/", l9_windows, our_neg8(ours)):
        neg8 = get(ours, "windows", PACKS.get(pack, ""), "neg8", default={}) or {}
        for name, row, _ in c.pairs(f"disclosure/window_lines/{pack}/", rows or {}, neg8s or {}):
            row, key = row or {}, f"disclosure/{pack}/{name}"
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


def machine_lines(lines, word):
    return keyed(lines, lambda row: row.get("run_id" if word == "machine_member" else "model"), word,
                 lambda row: row.get("line") == word)


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
        disclosed = machine_lines(lines, "machine_member")
        mine = get(windows, PACKS[pack], "members", default={}) or {}
        stored = meter_records.get(pack)
        harvested = get(stored, "members", default={}) or {}
        if not (disclosed or mine or harvested):
            continue
        if stored is None:
            # The disclosure shows a meter line, so its source record is required.
            c.numeric("meter_j", f"machine/{pack}/meter_record", None, None)
        members = (disclosed, mine) if stored is None else (disclosed, harvested, mine)
        for rid, row, *rest in c.pairs(f"machine/{pack}/", *members):
            row, own = row or {}, get(mine, rid, "phases", "request", default={}) or {}
            key = f"machine/{pack}/{rid}/request"
            c.numeric("rho", key + "/rho", row.get("rho"), own.get("rho"))
            c.numeric("machine_j", key + "/rail_delta_J", row.get("rail_j"), own.get("rail_delta_J"))
            c.numeric("machine_j", key + "/delta_J", row.get("machine_j"), own.get("delta_J"))
            if stored is None:
                continue
            row = rest[0] if isinstance(rest[0], dict) else {}
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


def checked_models(whole_machine, pack):
    models = get(whole_machine, "request_cross_check", "windows", PACKS[pack], "models", default={}) or {}
    return {str(SHORT_MODELS.get(model, model)): row for model, row in models.items()} if isinstance(models, dict) else {}


def compare_machine_summary(c, pack, lines, whole_machine):
    """L9's per-model order statistics and central band, re-derived from the recompute's member rho (X2).

    The band's window is the one the recompute chose (each model's first clean window):
    its pack is compared exact, a band on one side only is DISAGREE, and its bounds are
    re-derived from that window's plausible members (S2, Opus N3).
    """
    windows = whole_machine.get("windows") or {}
    summaries = machine_lines(lines, "machine_summary")
    groups, checked = model_groups(get(windows, PACKS[pack], "members")), checked_models(whole_machine, pack)
    for model, line, rows in c.pairs(f"machine_summary/{pack}/", summaries, groups):
        line = line or {}
        derived, _ = machine_summary(rows or [])
        key = f"machine_summary/{pack}/{model}"
        for stat in ("median", "minimum", "maximum", "q25", "q75", "spread"):
            if stat in line or stat in derived:
                c.numeric("rho", f"{key}/{stat}", line.get(stat), derived.get(stat))
        band = line.get("central_band") if isinstance(line.get("central_band"), dict) else {}
        own = get(checked, model, "central_band", "pack")
        own = own.lower() if isinstance(own, str) else None
        if not band and own is None:
            continue
        c.exact("routing_id", f"{key}/central_band/pack", band.get("pack"), own)
        _, plausible = machine_summary(model_groups(get(windows, PACKS.get(own, ""), "members")).get(model, []))
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


# Step-11 coverage (RC-CMP-3 X1, X6; RC-CMP-5 S1, S2). Each leaf of the fill input and the
# disclosure record has a path like fill:gamma/contrasts/*/estimate: a list item becomes *,
# or its line word when the item is a disclosure line (window_lines/alpha/machine_member/rho).
# A leaf is numeric-class when it is a number, null, or was read from a NaN or Infinity.
# A rule is (pattern, target) or (pattern, family, key). The first rule that matches wins:
# - (pattern, family, key): the leaf copies the comparison row (family, key). The key
#   template is filled from the pattern's named groups, the identity fields of the objects
#   enclosing the leaf (its contrast, cell, run or line) and list positions, never from an
#   attribute (see binding()). The leaf is covered only if that row exists, its L9 value
#   equals the leaf in type and value, it is AGREE, each item routing it (its routing_id
#   rows) is AGREE, and no other leaf at its path binds that row; otherwise the run refuses;
# - "uncovered:<reason>" matches strings and booleans only: a numeric-class leaf falls through;
# - "uncovered-by-name:<reason>" names leaves left uncovered; each numeric-class one is listed;
# - "uncovered-null-by-name:<reason>" matches a null only (not one read from a nonfinite
#   token); each one is listed.
# A leaf no rule matches refuses the run.
STEP11_SOURCES = (("fill", r"outputs/[0-9a-f]{64}-results-fill-input\.json"),
                  ("disclosure", r"disclosures/[0-9a-f]{64}\.json"))
UNCOVERED, NAMED, NULL_NAMED = "uncovered:", "uncovered-by-name:", "uncovered-null-by-name:"
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
    (F + "j_per_token", NULL_NAMED + "null for a J contrast by registration (J/token contrasts only)"),
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
    # Arm gates and resolutions by registered position (A, B), never by their printed condition (S2).
    (F + r"floor/resolutions/\*/(?P<field>floor_abs_j|floor_cmp_j|floor_gate_j)", "floor_gate_j",
     "{cid}/resolution/{resolution}/{field}"),
    (F + r"floor/resolutions/\*/source_cell_ids/\*", "routing_id", "contrast/{cid}/resolution/{resolution}/source_cell_ids/{source}"),
    (F + r"floor/arm_gates/\*/floor_gate_j", "floor_gate_j", "{cid}/arm/{arm}/floor_gate_j"),
    (F + r"floor/arm_gates/\*/(?P<field>arm_id|condition_family_id)", "routing_id", "contrast/{cid}/arm/{arm}/{field}"),
    (F + r"floor/(resolutions/\*/)?(point_floor_diagnostics|single_count_discipline)(/.*)?", FLOOR_DIAGNOSTICS),
    (F + r"floor/(aggregation|claim_floor_rule|status|transport_verdict|floor_source|floor_limit_class|"
     r"arm_gates/\*/status|resolutions/\*/(status|transport_rule_id|reason_codes(/\*)?|"
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
    (W + r"machine_summary/central_band/pack", "routing_id", "machine_summary/{pack}/{model}/central_band/pack"),
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
    (D + r"block_lines/dominance_ratio/ratio", "dominance_ratio", "ratio/{ratio_label}/ratio"),
    (D + r"block_lines/dominance_ratio/(?P<field>numerator_j|denominator_j)", "floor_j", "ratio/{ratio_label}/{field}"),
    (D + r"block_lines/dominance_ratio/n", "count", "ratio/{ratio_label}/n"),
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
    """(path, value, context): context maps each scalar field of the enclosing objects, nearest
    first, to (value, path of that field), and "@<list>" to the position in each enclosing list."""
    context = context or {}
    if isinstance(value, dict) and value:
        context = {**context, **{key: (item, join(path, key)) for key, item in value.items()
                                 if not isinstance(item, (dict, list))}}
        for key, item in value.items():
            yield from leaves(item, join(path, key), context)
    elif isinstance(value, list) and value:
        name = "@" + path.rsplit("/", 1)[-1]
        for index, item in enumerate(value):
            yield from leaves(item, path + "/" + step(item), {**context, name: (index, None)})
    else:
        yield path, value, context


# The fields a key may be built from (S2): a container's identity (its contrast, cell, pack,
# run, model, ratio component and label, leave-one-out block) and list positions. An
# attribute a line asserts about another object (a gate's condition_family_id, a
# resolution's source_cell_ids, a band's pack) never routes a key; it is compared as a
# routing_id row instead.
IDENTITY_FIELDS = ("contrast_id", "cell_id", "pack", "run_id", "model", "component", "text", "omitted_block_id",
                   "block_number")
POSITIONS = {"arm": "@arm_gates", "resolution": "@resolutions", "source": "@source_cell_ids"}


def binding(context, groups):
    """Key fields, and for each the id leaves it was read from (none for a path group or a position)."""
    value = {name: context[name][0] for name in IDENTITY_FIELDS if name in context}
    fields = {name: item for name, item in value.items()}
    sources = {name: [context[name][1]] for name in value}

    def derive(name, result, *using):
        if result is not None:
            fields[name], sources[name] = result, [context[u][1] for u in using if u in context]
    cell = value.get("cell_id")
    derive("cid", value.get("contrast_id"), "contrast_id")
    if isinstance(cell, str):
        derive("rcid", reported_key(cell)[0], "cell_id")
        model, phase, kind = cell_model(cell), cell_phase(cell), floor_kind(cell)
        if model:
            derive("aggregate_cell", model + "/" + phase, "cell_id")
            if kind:
                derive("floor_cell", f"{model}/{phase}/{kind}", "cell_id")
                derive("minted_field", f"{model}/{phase}/floor_{'abs' if kind == 'absolute' else 'cmp'}_j", "cell_id")
            component = value.get("component")
            label = re.match(r"\S+ \S+: (R|R_cm) ", str(value.get("text", "")))
            if label and component:
                derive("ratio_label", f"{model}/{phase}/{component}" + ("/common_mode" if label[1] == "R_cm" else ""),
                       "cell_id", "component", "text")
    derive("loo", loo_key(value.get("omitted_block_id")), "omitted_block_id")
    derive("loo_number", block_key(value.get("block_number")), "block_number")
    for name, position in POSITIONS.items():
        if position in context:
            fields[name], sources[name] = context[position][0], []
    for name, group in groups.items():
        if group is not None:
            fields[name], sources[name] = group, []
    return fields, sources


def key_for(template, context, groups):
    """The row key a leaf binds to, and the id leaves that routed it; None when a field is unresolved."""
    fields, sources = binding(context, groups)
    names = re.findall(r"\{(\w+)\}", template)
    if any(not isinstance(fields.get(name), (str, int)) or isinstance(fields.get(name), bool) for name in names):
        return None, []
    return template.format(**{name: fields[name] for name in names}), [p for name in names for p in sources[name]]


def admits(rule, value, number, nonfinite):
    """Default deny for numbers (S1): uncovered: takes strings and booleans only; uncovered-null-by-name: a null only."""
    if len(rule) == 3:
        return True
    if rule[1].startswith(UNCOVERED):
        return not number
    if rule[1].startswith(NULL_NAMED):
        return value is None and not nonfinite
    return True


def coverage(custody, comparison, rules=None):
    rules = COVERAGE if rules is None else rules
    rows = {(row["family"], row["key"]): row for row in comparison.rows}
    report, unmapped, unbound, named, absent, nonfinite, routed, bound = {}, set(), {}, set(), [], set(), set(), set()
    for label, pattern in STEP11_SOURCES:
        names = custody.names(pattern)
        if not names:
            absent.append(label)
        for name in names:
            document = custody.read(name)
            odd = custody.nonfinite.get(name, set())
            nonfinite.update(label + ":" + leaf for leaf in odd)
            for leaf, value, context in leaves(document):
                path = label + ":" + leaf
                number = numeric(value) or value is None or leaf in odd
                rule, match = None, None
                for candidate in rules:
                    match = re.fullmatch(candidate[0], path)
                    if match and admits(candidate, value, number, leaf in odd):
                        rule = candidate
                        break
                if rule is None and value in ([], {}):
                    # An empty list or object prints no value.
                    report.setdefault(path, UNCOVERED + "empty container; no printed value")
                elif rule is None:
                    unmapped.add(path)
                elif len(rule) == 2:
                    report.setdefault(path, rule[1])
                    if rule[1].startswith(NULL_NAMED) or (rule[1].startswith(NAMED) and number):
                        named.add(path)
                else:
                    family = rule[1]
                    key, routes = key_for(rule[2], context, match.groupdict())
                    row = rows.get((family, key)) if key is not None else None
                    printed = row.get("l9_raw", row.get("l9")) if row else None
                    reason = ("key_unresolved" if key is None else "no_row" if row is None else
                              "value_differs" if not same(printed, value) else
                              "row_disagrees" if row["verdict"] != "AGREE" else
                              "route_disagrees" if any(get(rows.get(("routing_id", item)), "verdict") != "AGREE"
                                                       for item in row.get("items", [])) else
                              "duplicate_binding" if (path, family, str(key)) in bound else None)
                    bound.add((path, family, str(key)))
                    if reason:
                        # Mapped, but not a copy of an agreeing compared row: not coverage.
                        unbound.setdefault((path, family, str(key), reason), None)
                    else:
                        report.setdefault(path, family)
                        routed.update(label + ":" + source for source in routes)
    uncompared = sorted({path for path, *_ in unbound})
    for path in routed - set(uncompared):
        # An identity field that routed an agreeing binding is compared by its routing_id rows (S2).
        report[path] = "routing_id"
    for path in uncompared:
        report.pop(path, None)
    return {"leaves": report, "unmapped": sorted(unmapped | set(uncompared)), "uncompared": uncompared,
            "unbound": [{"path": p, "family": f, "key": k, "reason": r} for p, f, k, r in sorted(unbound)],
            "uncovered_numeric": sorted(named), "absent_sources": absent, "nonfinite": sorted(nonfinite)}


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
          + " step11_unmapped=" + str(len(cover["unmapped"])) + " step11_nonfinite=" + str(len(cover["nonfinite"]))
          + " step11_uncovered_numeric="
          + str(len(cover["uncovered_numeric"])) + " step11_absent=" + ",".join(cover["absent_sources"] or ["none"])
          + " structure_flags=" + str(len(result["structure_flags"])))
    if cover["nonfinite"]:
        # A NaN or Infinity in a step-11 output is never a printed value to cover (S1).
        print("refused=step11_nonfinite_value", file=sys.stderr)
        return 2
    if cover["unmapped"] or cover["absent_sources"]:
        # Coverage of step 11 cannot be shown without every step-11 output.
        print("refused=" + ("step11_unmapped_fill" if cover["unmapped"] else "step11_outputs_absent"), file=sys.stderr)
        return 2
    return 0 if all(v["fail"] == 0 for v in counts.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
