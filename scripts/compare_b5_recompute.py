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
- the input gate (RC-CMP-6, from L9's own writer and registered ids). G1: a
  step-11 output is read only if its bytes are the canonical serialisation of
  its strict parse (L9's writer flags; no repeated member, no NaN or Infinity);
  every other input refuses a repeated member. G2: an identity field is read
  only on the object it names (IDENTITY_OWNERS); anywhere else refuses, and a
  nested object never re-routes its parent's leaves. G3: every L9 id that
  routes a binding is looked up literally in the sealed campaign configs
  (Registry); an id they do not register refuses; no id is parsed for its parts;
- key universes (RC-CMP-7 G7): run_phase_energy_j compares the science runs L9's
  step 2 re-reduces (its kept-units record), applied identically to both sides; a
  member the window's sealed plan tree registers as a NEG-8 reference is compared in
  its NEG-8 family and listed in the restricted output as excluded (compared_in:<family>);
- line words (RC-CMP-7 F2): a disclosure line is read only with a word its section's
  producer writes and that word's keys; every printed claim word the recompute re-derives
  is compared exactly, and an exemption names only enumerated producer leaves (F3: loo
  rows key on registered block ids, ratio rows on registered numerator fields);
- claim words (RC-CMP-8): readiness (ready iff the recompute's ceiling is L2-L4), each window's
  claim_usable, the sealed manifest's role, direction, confirmatory status, condition, orientation,
  metric, estimator and floor-rule words, the status words the producer fixes (leave-one-out,
  reported cell, assist contrast), the leave-one-out influence triggers and the two by-construction
  words (True) are compared exactly; a compared line, sensitivity row or fill claim key its producer
  always writes is required (required_key_absent), and below_screen_bound and neg8_screen pair per
  registered window;
- the expected-check table (RC-CMP-9): before any family compares, one table built from the registered sources
  only (REGISTERED_SOURCES, closed) lists every item the producers print unconditionally per registered
  window, cell, contrast, block, ratio and record row, with its nested keys (the producers' key sets, copied as
  literals), and each conditional item with the registered condition (a status or kept word on either side)
  that makes it expected; each check must find its item on L9's side and the recompute's (expected/<check>,
  DISAGREE otherwise), an L9 item of a listed collection that no check claims is DISAGREE (unexpected/), and a
  compared step-11 leaf binds only inside a claimed item (not_in_table); a list the fill copies position by
  position prints every position (copy_shortened);
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
        bars = json.loads(Path(path).read_bytes(), object_pairs_hook=unique("bars_duplicate_key"))
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
        self.bars, self.rows, self.scope, self.seen, self.excluded = bars, [], [], set(), []
        # RC-CMP-9: the concrete paths of the items the expected-check table claimed, per L9 document.
        self.claimed = {}

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


def unique(code):
    """An object_pairs_hook: a repeated member refuses, so no reader can pick another of two values (G1)."""
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise Refusal(code)
            result[key] = value
        return result
    return pairs


def canonical(value):
    """L9's writer: results_fill_adapter.render_results_fill_input and calibration_ledger.canonical_json_bytes."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def strict_loads(raw, label, tail):
    """A step-11 output (G1): the unique reading of its bytes, or a refusal naming the shape."""
    def nonfinite(word):
        raise Refusal("l9_output_nonfinite:" + label)
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=unique("l9_output_duplicate_key:" + label),
                           parse_constant=nonfinite)
    except (UnicodeDecodeError, ValueError):
        raise Refusal("l9_output_unreadable") from None
    if canonical(value) + tail != raw:
        raise Refusal("l9_output_not_canonical:" + label)
    return value


def loads(raw, flags, source, paths=None, duplicate="input_duplicate_key"):
    """JSON with NaN and Infinity read as null; the flag names each such leaf path (RC-CMP-3 X7, S1).

    A repeated member refuses with the code duplicate (G1).
    """
    found = []
    value = scrub(json.loads(raw, parse_constant=lambda word: NONFINITE, object_pairs_hook=unique(duplicate)), "", found)
    flag = {"code": "nonfinite_value_read_as_null", "source": source, "count": len(found), "paths": sorted(set(found))}
    if found and flag not in flags:
        flags.append(flag)
    if paths is not None:
        paths.update(found)
    return value


class Custody:
    """L9's dry-run custody: every file used must be listed in the record with its digest.

    A step-11 output is read through the input gate (G1-G3) before anything sees it.
    """
    def __init__(self, root, flags=None, registry=None):
        self.root = Path(root)
        self.restricted = self.root / RESTRICTED
        self.flags = [] if flags is None else flags
        self.registry = load_registry() if registry is None else registry
        try:
            self.record = json.loads((self.root / RECORD).read_bytes(), object_pairs_hook=unique("l9_record_duplicate_key"))
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
        for label, pattern in STEP11_SOURCES:
            if re.fullmatch(pattern, name):
                self.nonfinite.setdefault(name, set())
                value = strict_loads(raw, label, STEP11_TAILS[label])
                gate(value, label, self.registry)
                if label == "disclosure":
                    gate_lines(value)
                else:
                    gate_fill(value)
                return value
        try:
            return loads(raw, self.flags, "l9:" + name, self.nonfinite.setdefault(name, set()), "l9_output_duplicate_key")
        except ValueError:
            raise Refusal("l9_output_unreadable") from None

    def one(self, pattern):
        names = self.names(pattern)
        if len(names) > 1:
            raise Refusal("l9_output_ambiguous")
        return self.read(names[0]) if names else None


# The registered ids (G3): the sealed v5 campaign configs, read as data and pinned by digest
# (the contrast campaign's plan tree binds the consumer declaration by the same digest).
CAMPAIGNS = Path(__file__).resolve().parents[1] / "configs/campaigns"
EXTRACTION_SPECS = {"alpha": "d117_floor_qwen3-1p7b_v5/extraction_spec.json",
                    "beta": "d117_floor_qwen3-8b_v5/extraction_spec.json"}
MANIFEST = "d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/analysis_manifest_v3.json"
DECLARATION = "d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/consumer_family_declaration.json"
# Each window's sealed plan tree (G7): its registered member roles (science runs, NEG-8 references, spares).
PLAN_TREES = {"alpha": "d117_floor_qwen3-1p7b_v5/plan_tree.json", "beta": "d117_floor_qwen3-8b_v5/plan_tree.json",
              "gamma": "d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/plan_tree.json"}
REGISTRY_PINS = {
    PLAN_TREES["alpha"]: "2ec3625a31b796e3fa37e2c39f37508618b649d0d9f61ddbd3fdfe2c5a282809",
    PLAN_TREES["beta"]: "e77e4f6e74f663190d1acfe95c3e2499ec69c1b27ba9e3564c531affee980707",
    PLAN_TREES["gamma"]: "da8028977dfe44b3bf1d13e79e7bfea2b1390aa985bef7faa891369c8e3985bc",
    EXTRACTION_SPECS["alpha"]: "a6498f56469448fd422e6ca2e0787b362a4fd6957bffab7d477ac7f30db38df6",
    EXTRACTION_SPECS["beta"]: "2c0ee7189f9aa7e8f534be3cca3bf6f4125c23b5e7bf7ee1e600c7edf9d81ddc",
    MANIFEST: "4342ea609ec7f57fbb21860440995ac8f2038d93ed508f8d7bb72a540c86050d",
    DECLARATION: "2875c95356812799553614b95dfc5c3237fa396dc70c03c71a91c2a764f3e464"}


class Registry:
    """Each registered id and what it names, from the configs' own fields, never from the id's spelling.

    extraction: a floor extraction cell (its window's model, target phase, kind, condition family);
    reported: a reported energy cell (its window's model and target phase, and the condition family of
      the extraction cells over the same members, which is the recompute's cell id);
    floor: an aggregate floor cell (the consumer declaration's arm A and B cells of each phase);
    contrast: a registered contrast (target phase; floor_selector condition family ids in [A, B] order;
      its claim role, hypothesized direction and confirmatory status, its condition ids, difference orientation,
      metric name, tag and window class, point estimator and floor rule ids, as the sealed manifest registers them).
    A p42 cell is a prefill cell whose workload has 42 prompt tokens.
    roles: each window's member roles from its sealed plan tree (G7); blocks: each contrast's
    registered block ids in order (the recompute numbers them b01, b02, ... in that order).
    """
    def __init__(self, root=CAMPAIGNS, pins=None):
        pins = REGISTRY_PINS if pins is None else pins
        self.digests, self.tables = {}, {"extraction": {}, "reported": {}, "floor": {}, "contrast": {}}
        self.roles, self.blocks = {}, {}
        try:
            for pack, name in PLAN_TREES.items():
                self.roles[pack] = plan_roles(self.read(root, name, pins))
            for pack, name in EXTRACTION_SPECS.items():
                spec = self.read(root, name, pins)
                members = {}
                for cell in spec["cells"]:
                    phase = cell["target_precheck_path"][-1]
                    tokens = {d["condition_family_definition"]["workload_profile"]["prompt_tokens"]
                              for d in cell["condition_family_definitions"].values()}
                    if cell["kind"] not in ("absolute", "comparative"):
                        raise ValueError(cell["kind"])
                    self.register("extraction", cell["cell_id"], pack=pack, model=MODELS[pack], phase=phase,
                                  form=cell["kind"], family=cell["condition_family_id"], p42=phase == "prefill" and tokens == {42})
                    members[cell["cell_id"]] = {m["bundle_id"] for m in cell["member_config_sha256"]}
                for cell in spec["reported_energy_cells"]:
                    phase, own = cell["target_precheck_path"][-1], {m["bundle_id"] for m in cell["members"]}
                    over = [self.tables["extraction"][cid] for cid, ids in members.items()
                            if self.tables["extraction"][cid]["phase"] == phase and ids <= own]
                    (family,), (p42,) = {e["family"] for e in over}, {e["p42"] for e in over}
                    self.register("reported", cell["cell_id"], pack=pack, model=MODELS[pack], phase=phase,
                                  family=family, p42=p42)
            manifest = self.read(root, MANIFEST, pins)
            # F2 (RC-CMP-8): the engine demotes a contrast only for an outcome-dependent top-up, which the
            # sealed replacement policy forbids; so the registered confirmatory status is confirmatory.
            confirmatory = ("confirmatory" if manifest["replacement_policy"]["outcome_dependent_top_up"] == "forbidden"
                            else None)
            for contrast in manifest["contrasts"]:
                selector = contrast["floor_dependency"]["floor_selector"]
                a, b = selector["condition_family_ids"]
                self.register("contrast", contrast["contrast_id"], phase=contrast["target_precheck_path"][-1],
                              conditions=(a, b), role=contrast["claim_role"],
                              direction=contrast["scientific_hypothesis_direction"], confirmatory=confirmatory,
                              definition={"condition_a_id": contrast["condition_a_id"],
                                          "condition_b_id": contrast["condition_b_id"],
                                          "difference_orientation": contrast["difference_orientation"],
                                          "name": contrast["metric"], "metric_tag": contrast["metric_tag"],
                                          "window_class": selector["window_class"]},
                              estimator=contrast["point_estimator"],
                              floor_rules={"claim_floor_rule": selector["claim_floor_rule"],
                                           "transport_rule_id": selector["transport_rule_id"]},
                              # RC-CMP-9 A4: each arm's registered transport group, by its condition family.
                              transport_groups=tuple([
                                  next(group["transport_group_id"]
                                       for group in contrast["floor_dependency"]["transport"]["transport_groups"]
                                       if group["condition_family_id"] == condition) for condition in (a, b)]))
                blocks = contrast["block_ids"]
                if not all(isinstance(bid, str) for bid in blocks) or len(set(blocks)) != len(blocks):
                    raise ValueError(blocks)
                self.blocks[contrast["contrast_id"]] = tuple(blocks)
            declaration = self.read(root, DECLARATION, pins)
            decode = declaration["decode_floor_cells"]
            for phase, (a, b) in (("decode", (decode["condition_a"], decode["condition_b"])),
                                  ("prefill", declaration["prefill_p2048_floor_dependency"]["cell_ids"])):
                for index, cid in enumerate((a, b)):
                    self.register("floor", cid, pack=ARMS[index], model=MODELS[ARMS[index]], phase=phase)
            # RC-CMP-9 A3: each contrast's registered floor source cells, in arm order [A, B] (the declaration's
            # cells of the contrast's phase; the gamma plan tree binds the declaration by digest).
            for entry in self.tables["contrast"].values():
                entry["floor_cells"] = tuple([next(cid for cid, floor in self.tables["floor"].items()
                                                   if floor["phase"] == entry["phase"] and floor["pack"] == pack)
                                              for pack in ARMS.values()])
        except (KeyError, TypeError, ValueError, IndexError, AttributeError, StopIteration):
            raise Refusal("routing_registry_invalid") from None

    def read(self, root, name, pins):
        try:
            raw = (Path(root) / name).read_bytes()
        except OSError:
            raise Refusal("routing_registry_unreadable") from None
        self.digests[name] = hashlib.sha256(raw).hexdigest()
        if pins.get(name) != self.digests[name]:
            raise Refusal("routing_registry_digest_differs")
        return json.loads(raw, object_pairs_hook=unique("routing_registry_duplicate_key"))

    def register(self, kind, cid, **entry):
        if not isinstance(cid, str) or any(cid in table for table in self.tables.values()):
            raise ValueError(cid)
        if entry.get("phase", "decode") not in ("decode", "prefill"):
            raise ValueError(entry["phase"])
        self.tables[kind][cid] = dict(entry, kind=kind)

    def entry(self, cid, *kinds):
        """The registered entry of an L9 id, or None when no table of these kinds lists it literally."""
        return next((self.tables[kind][cid] for kind in kinds if isinstance(cid, str) and cid in self.tables[kind]), None)

    def lookup(self, cid, kinds, where, pack=None):
        """An id that routes: registered under these kinds (and, given a window, for that window), or refuse."""
        found = self.entry(cid, *kinds)
        if found is None or pack is not None and found.get("pack") != pack:
            raise Refusal("routing_id_unregistered:" + where)
        return found

    def registered(self, cid, kinds, where):
        """A routing id, after lookup refused it unless registered."""
        self.lookup(cid, kinds, where)
        return cid

    def families(self, pack, p42):
        """The recompute's reported cell ids (condition families) of a window."""
        return {e["family"] for e in self.tables["reported"].values() if e["pack"] == pack and e["p42"] is p42}

    def reported_family(self, pack, phase):
        """The one non-p42 reported cell id of a window and phase (the cross-window line's cell)."""
        found = {e["family"] for e in self.tables["reported"].values()
                 if e["pack"] == pack and e["phase"] == phase and not e["p42"]}
        return found.pop() if len(found) == 1 else None

    def phase_of_family(self, family):
        """The target phase of a recompute reported cell id (a registered condition family)."""
        found = {e["phase"] for e in self.tables["reported"].values() if e["family"] == family}
        return found.pop() if len(found) == 1 else None


    def role(self, pack, rid):
        """A member's registered role in its window's plan tree (science, start, midpoint, end, corpus,
        diagnostic), or None when the plan tree does not list it."""
        return self.roles.get(pack, {}).get(rid) if isinstance(rid, str) else None

    def block(self, cid, block_id):
        """A contrast's registered block id -> the recompute's block key (b01 for the first), else None (F3)."""
        blocks = self.blocks.get(cid, ())
        return "b%02d" % (blocks.index(block_id) + 1) if isinstance(block_id, str) and block_id in blocks else None


# The plan tree's reference inputs and the role each registers (literal input ids, never parsed); a spare
# takes the slot its stage's spare_retry declares. Interior references are diagnostic: no family uses them.
REFERENCE_INPUTS = {"neg8_bound": "corpus", "neg8_bound_corpus": "corpus", "start_reference": "start",
                    "start_references": "start", "midpoint_reference": "midpoint", "end_reference": "end",
                    "end_references": "end", "decode_midpoint_reference": "diagnostic",
                    "prefill_midpoint_reference": "diagnostic"}


def plan_roles(tree):
    """{run_id: role} from a sealed plan tree: science/*, external_inputs members, spare_retry members."""
    roles = {}

    def assign(rid, role):
        if not isinstance(rid, str) or roles.get(rid, role) != role:
            raise ValueError(rid)
        roles[rid] = role
    for member in tree["science"]:
        assign(member["run_id"], "science")
    inputs = tree["external_inputs"]
    for entry in inputs["manifests"] if isinstance(inputs, dict) else inputs:
        if "members" in entry:
            role = REFERENCE_INPUTS[entry.get("external_input_id", entry.get("input_id"))]
            for member in entry["members"]:
                assign(member["run_id"], role)
    for stage in tree["stage_graph"]:
        spare = stage.get("spare_retry")
        if spare is not None:
            if spare["slot"] not in ("start", "midpoint", "end"):
                raise ValueError(spare["slot"])
            for member in spare["members"]:
                assign(member["run_id"], spare["slot"])
    return roles


_REGISTRY = {}


def load_registry(root=CAMPAIGNS, pins=None):
    """The sealed registry, read once per root (tests pass an edited copy with its own pins)."""
    if pins is not None:
        return Registry(root, pins)
    if root not in _REGISTRY:
        _REGISTRY[root] = Registry(root)
    return _REGISTRY[root]


# RC-CMP-9: the sources an expected check may come from. This list is closed: no other source, in particular no
# L9 output and no recompute output, may create an entry of the expected-check table, now or later.
REGISTERED_SOURCES = (
    "configs/campaigns/d117_floor_qwen3-1p7b_v5/extraction_spec.json",
    "configs/campaigns/d117_floor_qwen3-8b_v5/extraction_spec.json",
    "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/analysis_manifest_v3.json",
    "configs/campaigns/d117_floor_qwen3-1p7b_v5/plan_tree.json",
    "configs/campaigns/d117_floor_qwen3-8b_v5/plan_tree.json",
    "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/plan_tree.json",
    # Bound by digest from the gamma plan tree (consumer declaration); the registry has read it since RC-CMP-6.
    "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/consumer_family_declaration.json",
    # The window index: named, not read (absent from this branch); no entry is taken from it.
    "configs/analysis/b5/analysed_windows.json",
    "the registered packs (PACKS)",
    "the sealed registration and analysis-plan constants the producers apply, copied below as literals")

# F1 (RC-CMP-9): the producers' exact key sets, copied as literals. tests/independent_recompute/test_rc_cmp9.py
# pins each to its source on origin/main: analysis_engine/artifact.py (_CONTRAST_KEYS, _METRIC_KEYS,
# _CONDITION_KEYS, _CONTRAST_SAMPLING_KEYS, _ESTIMATOR_KEYS, _DETERMINISTIC_KEYS, _FLOOR_KEYS, _V3_FLOOR_KEYS,
# _ARM_GATE_KEYS, _FLOOR_RESOLUTION_KEYS, _MULTIPLICITY_EVIDENCE_KEYS, _LOO_KEYS, _LOO_ROW_KEYS, _EVALUATION_KEYS).
ENGINE_KEYS = {
    "contrast": ("contrast_id", "plan_id", "family_instance_id", "claim_role", "metric", "conditions",
                 "hypothesized_direction", "equivalence", "mde", "bundle_blocks", "sampling", "estimator",
                 "deterministic_bounds", "floor", "multiplicity", "randomization_check", "loo", "sensitivity_status",
                 "claim_evaluation"),
    "metric": ("name", "metric_tag", "window_class", "unit", "ratio_estimand"),
    "conditions": ("condition_a_id", "condition_b_id", "cell_a_id", "cell_b_id", "difference_orientation"),
    "sampling": ("confirmatory_status", "planned_n", "observed_complete_n"),
    # Block 5 always passes its kept quads (build_results_fill_input: kept_quads), so the kept sampling keys print.
    "kept_sampling": ("kept_n", "removed_block_ids"),
    "estimator": ("name", "n", "df", "estimate", "s_d", "SE_repeat", "SE_metrology", "SE_total", "t_critical_95",
                  "repeat_point_CI95", "metrology_aware_CI95", "variance_contributions", "excluded_stochastic_terms",
                  "raw_p"),
    "deterministic": ("terms", "total", "decision_interval"),
    "deterministic_term": ("name", "bound"),
    "floor": ("status", "floor_row_ids", "floor_abs_j", "floor_cmp_j", "active_floor_j", "transport_verdict",
              "resolutions"),
    # A v3 contrast requires the complete armwise floor (artifact.py: v3 contrast requires ...); the sealed
    # manifest is analysis_manifest_v3 with a floor_selector claim_floor_rule, so these keys always print.
    "v3_floor": ("claim_floor_rule", "aggregation", "arm_gates"),
    "arm_gate": ("arm_id", "condition_family_id", "status", "floor_gate_j"),
    "resolution": ("status", "source_cell_ids", "transport_group_id", "transport_rule_id", "floor_abs_j",
                   "floor_cmp_j", "floor_gate_j", "reason_codes"),
    "multiplicity": ("raw_p", "adjusted_p", "rejected"),
    "loo": ("status", "rows"),
    "loo_row": ("omitted_block_id", "n_blocks", "df", "estimate", "metrology_aware_ci95", "decision_interval",
                "floor_status", "raw_p", "adjusted_p", "outcome", "influence_triggers"),
    "evaluation": ("outcome", "direction", "reason_codes", "claim_ready_for_l2_l3", "claim_level_ceiling")}
# results_fill_adapter.adapt_claim_verdicts (the 14 base keys of each contrast row and the 10 extended ones; the
# output's gamma and characterization objects) and scripts/build_results_fill_input.py (each campaign's keys).
FILL_SHAPE = {
    "top": ("schema_version", "campaigns", "gamma", "characterization"),
    "gamma": ("claim_verdicts_id", "claim_verdicts_sha256", "evidence_class", "limitations", "contrasts",
              "finalized_manifest", "floor_artifact", "exclusions_sha256"),
    "floor_artifact": ("artifact_id", "file_sha256"),
    "characterization": ("funded", "run", "verdict"),
    "campaign": ("plan_id", "attempt", "claim_usable", "exclusions_sha256", "harvest_record_sha256"),
    "contrast": ("contrast_id", "metric", "conditions", "limitations", "floor_source_cell_ids", "estimate", "interval",
                 "decision_interval", "deterministic_widening_total", "j_per_token", "n", "floor", "multiplicity",
                 "claim_evaluation", "plan_id", "claim_role", "hypothesized_direction", "equivalence", "sampling", "loo",
                 "df", "t_critical_95", "kept_block_ids", "removed_block_ids")}
# b5_analysis/disclosures.py produce_disclosures (the record's sections and each window's identity),
# _cell_values (a computed cell's values), and the lines each producer prints unconditionally.
DISCLOSURE_SHAPE = {
    "top": ("schema_version", "windows", "cells", "floors", "contrasts", "window_lines", "block_lines", "sensitivity",
            "fixed_sentences"),
    "window": ("plan_id", "attempt", "harvest_pin", "record_shape"),
    "cell_values": ("status", "mean_j", "h_j", "B_j", "lower_j", "upper_j")}
# The window lines _structure_lines, _monitor_lines, _reference_lines, _ruling_lines and _machine_lines print for
# every registered window, whatever the window's data (each conditional line is left out: arm_hazards,
# arm_unmeasured, battery_phase, battery_discharged, reference_lost, reference_spare, lost_midpoint,
# corpus_physics_drop, catalog_path, battery_temperature*, temperature_disagreement, stored_condition,
# stored_member_reason, machine_absent, machine_member, machine_summary; flag_count follows the flag catalog,
# which is not a registered source).
WINDOW_LINES = ("monitor_cost", "monitor_sentence", "physics_counts", "anchor_counts", "anchor_bound", "host_cpu",
                "battery_counts", "neg8_screen", "reference_counts", "corpus_counts", "bound_formula", "neg8_allowance",
                "erratum3_triggers", "below_screen_bound", "stored_status", "adapter_continuity",
                "stored_verdict_boundary", "deciding_membership", "reference_parity", "ledger_binding",
                "machine_boundary")
# _ruling_lines prints one tripwire line per registered tripwire key.
TRIPWIRES = ("excluded_reference_in_screen", "kept_member_outside_verdict_membership")
# _monitor_lines' battery_counts line counts each of these codes; _reference_lines' corpus_counts line always counts
# the status and desk-cap drops; _trigger_values' object, when the record has its bracket, carries these keys.
BATTERY_CODES = ("battery.assist", "battery.assist_outside_request", "calibration.capture_battery_assist",
                 "battery.smc_unavailable", "battery.capture_pair_assist", "calibration.capture_battery_pair_assist")
CORPUS_DROPS = ("status", "desk_cap")
TRIGGER_KEYS = ("observed_triggers", "recorded_only_triggers", "doubling_count", "systematic_sequences")
# The fixed sentences produce_disclosures prints whatever the data (conditionality, FIXED_SENTENCES, config_binding);
# floor_drift_ownership and gross_energy print when the record has floor lines and contrast observations.
FIXED_SENTENCE_WORDS = ("conditionality", "single_window", "floor_transfer_assumption", "floor_transfer_limit", "order",
                        "p42", "separate_windows", "dominance", "d177", "fixed_prompt", "config_binding")
# b5_analysis/sensitivity.py sensitivity_pass (the record's sections; bracket.BMax; each window's row) and its value
# sets: _reported_values, _compose_floor and _contrast_values.
SENSITIVITY_SHAPE = {
    "top": ("schema_version", "label", "b_max", "windows", "reported_cells", "floor_cells", "contrasts"),
    "b_max": ("value_s", "attained_by_sequence", "T"),
    "reported_values": ("mean_j", "h_j", "B_j", "lower_j", "upper_j", "attribution_floor_j"),
    "floor_values": ("floor_abs_j", "floor_cmp_j", "floor_gate_j", "allowance_j"),
    "contrast_values": ("floor_abs_j", "floor_cmp_j", "floor_gate_j", "D_j", "outcome")}
# dominance_closeout.validate (D-165): exactly eight independent ratios (each aggregate floor cell, absolute and
# comparative) and four comparative common-mode ratios (each aggregate floor cell).
CLOSEOUT_RATIOS = {"independent": ("absolute", "comparative"), "common_mode": ("comparative",)}
INTERVAL = (("lower",), ("upper",))
REPORTED_VALUE_KEYS = SENSITIVITY_SHAPE["reported_values"]


def nested(prefix, keys):
    return tuple((prefix, key) for key in keys)


def arms(path):
    """A registered-arm list's positions [A, B] (a contrast's floor cells: one per arm)."""
    return tuple(path + (index,) for index in ARMS)


def check_doc(label):
    """An L9 document label -> (how it is read, its pattern)."""
    if label.startswith(("projection:", "extraction:", "bracket:", "kept_units:")):
        kind, pack = label.split(":")
        return {"projection": (r"outputs/[0-9a-f]{64}-projection-%s\.json", "one"),
                "extraction": (r"mint/[0-9a-f]{64}-extraction-%s\.json", "one"),
                "bracket": (r"brackets/[0-9a-f]{64}-%s\.json", "one"),
                "kept_units": (KEPT_UNITS, "one")}[kind][0] % pack, "one"
    return {"fill": (STEP11_SOURCES[0][1], "one"), "disclosure": (STEP11_SOURCES[1][1], "one"),
            "verdicts": (r"outputs/[0-9a-f]{64}-claim-verdicts\.json", "one"),
            "aggregate": (r"mint/[0-9a-f]{64}-aggregate-floor\.json", "one"),
            "closeout": (r"finalized/outputs/closeout\.json", "one"),
            "ratios": (r"finalized/outputs/closeout\.ratio-table\.json", "one"),
            "block_bracket": (r"brackets/[0-9a-f]{64}-block\.json", "one"),
            "sensitivity": (r"outputs/[0-9a-f]{64}\.json", "sensitivity")}[label]


def expected_checks(registry):
    """RC-CMP-9 (the design rule): the one expected-check table, a function of the registered sources only.

    Each entry names a check (its kind and its registered key), the item it expects on L9's side (one locator per
    L9 copy: document, path, required nested key paths) and on the recompute's side (path, required key paths), and,
    for a conditional producer item, the registered condition that makes it expected. A path step is a key, a list
    position, or {field: value} for the one list item carrying those identity fields; "any" lists alternatives
    (a reported cell is either computed or refused). run() checks every entry before any family compares.
    """
    table = []

    def add(kind, check, l9, recompute, condition=None):
        table.append({"kind": kind, "check": check, "l9": tuple(l9), "recompute": tuple(recompute),
                      "condition": condition})

    contrasts = registry.tables["contrast"]
    floors = registry.tables["floor"]
    # The fill and the disclosure: each document and its sections.
    add("fill_document", "fill",
        [("fill", (), tuple((k,) for k in FILL_SHAPE["top"]) + nested("gamma", FILL_SHAPE["gamma"])
          + nested("characterization", FILL_SHAPE["characterization"])
          + tuple(("gamma", "floor_artifact", k) for k in FILL_SHAPE["floor_artifact"]))],
        [(("contrasts",), ()), (("inputs",), ())])
    for pack in ("alpha", "beta"):
        add("fill_campaign", f"fill/campaigns/{pack}", [("fill", ("campaigns", pack), tuple((k,) for k in FILL_SHAPE["campaign"]))],
            [(("inputs", PACKS[pack]), (("claim_usable",), ("exclusions_sha256",)))])
    add("verdicts_document", "verdicts", [("verdicts", (), (("contrasts",),))], [(("contrasts",), ())])
    for pack, PACK in PACKS.items():
        add("kept_units_record", f"kept_units/{pack}",
            [("kept_units:" + pack, (), (("pack",), ("exclusions_sha256",), ("cells",)))],
            [(("inputs", PACK), (("exclusions_sha256",),))])
    add("disclosure_document", "disclosure",
        [("disclosure", (), tuple((k,) for k in DISCLOSURE_SHAPE["top"]))], [(("disclosures",), ())])
    for pack, PACK in PACKS.items():
        add("disclosure_window", f"disclosure/windows/{pack}",
            [("disclosure", ("windows", pack), tuple((k,) for k in DISCLOSURE_SHAPE["window"])),
             ("disclosure", ("window_lines", pack), ())], [(("windows", PACK), ())])
        for word in WINDOW_LINES:
            line = {"below_screen_bound": (("b_op_s",), ("below",)), "neg8_screen": (("decision",),),
                    "neg8_allowance": (("source",),) + tuple(("values_j", NEG8_TERM + term) for term in NEG8_TERMS),
                    "reference_counts": nested("counts", ("start", "midpoint", "end"))
                    + nested("planned", ("start", "midpoint", "end")),
                    "corpus_counts": (("collected",), ("in_window",), ("deciding",), ("desk_cap",))
                    + nested("drop_counts", CORPUS_DROPS),
                    "battery_counts": nested("counts", BATTERY_CODES)}
            own = {"below_screen_bound": (("windows", PACK), (("b_op_s",),)),
                   "neg8_screen": (("windows", PACK, "neg8"), (("screen_decision",),)),
                   "neg8_allowance": (("windows", PACK, "neg8"), (("source",),) + tuple((k,) for k in NEG8_OWN)),
                   "reference_counts": (("windows", PACK, "neg8"), (("n_start",), ("n_mid",), ("n_end",))),
                   "corpus_counts": (("windows", PACK, "neg8"), (("corpus_n",),))}
            keys = line.get(word, tuple((k,) for k in LINE_KEYS["window_lines"][word]))
            add("window_line", f"disclosure/window_lines/{pack}/{word}",
                [("disclosure", ("window_lines", pack, {"line": word}), keys)],
                [own.get(word, (("windows", PACK), ()))])
        for tripwire in TRIPWIRES:
            add("window_line", f"disclosure/window_lines/{pack}/tripwire/{tripwire}",
                [("disclosure", ("window_lines", pack, {"line": "tripwire", "tripwire": tripwire}), (("result",),))],
                [(("windows", PACK), ())])
        add("block_line", f"disclosure/block_lines/attempt_count/{pack}",
            [("disclosure", ("block_lines", {"line": "attempt_count", "pack": pack, "superseded": False}),
              (("count",), ("causes",)))], [(("windows", PACK), ())])
    for word in FIXED_SENTENCE_WORDS:
        add("fixed_sentence", f"disclosure/fixed_sentences/{word}",
            [("disclosure", ("fixed_sentences", {"line": word}), (("text",),))], [(("disclosures",), ())])
    for word in ("floor_drift_ownership", "gross_energy"):
        add("fixed_sentence", f"disclosure/fixed_sentences/{word}",
            [("disclosure", ("fixed_sentences", {"line": word}), (("text",),))], [(("disclosures",), ())])
    add("block_line", "disclosure/block_lines/harvest_once",
        [("disclosure", ("block_lines", {"line": "harvest_once"}), (("no_analysed_window_harvested_twice",),))],
        [(("disclosures",), ())])
    add("block_line", "disclosure/block_lines/sensitivity_boundary",
        [("disclosure", ("block_lines", {"line": "sensitivity_boundary"}), (("text",),))],
        [(("disclosures", "sensitivity_bound"), ())])
    # The sensitivity record (one), its disclosure copy and its block lines.
    bound = ("disclosures", "sensitivity_bound")
    record_keys = tuple((k,) for k in SENSITIVITY_SHAPE["top"]) + nested("b_max", SENSITIVITY_SHAPE["b_max"])
    add("sensitivity_record", "sensitivity",
        [("sensitivity", (), record_keys), ("disclosure", ("sensitivity",), record_keys)], [(bound, ())])
    bmax = tuple((k,) for k in SENSITIVITY_SHAPE["b_max"])
    add("sensitivity_bmax", "sensitivity/b_max",
        [("sensitivity", ("b_max",), bmax), ("disclosure", ("sensitivity", "b_max"), bmax),
         ("disclosure", ("block_lines", {"line": "sensitivity_bmax"}), bmax)],
        [(bound, (("B_max_s",), ("T",), ("attaining_sequence",)))])
    for pack, PACK in PACKS.items():
        window = tuple((k,) for k in SENSITIVITY_KEYS["windows"])
        add("sensitivity_window", f"sensitivity/windows/{pack}",
            [("sensitivity", ("windows", pack), window), ("disclosure", ("sensitivity", "windows", pack), window),
             ("disclosure", ("block_lines", {"line": "sensitivity_window", "pack": pack}), window)],
            [(("windows", PACK), (("b_op_s",),)), (bound + ("windows", PACK), (("b_sens_s",),))])
    for cid, entry in registry.tables["reported"].items():
        pack, family = entry["pack"], entry["family"]
        computed = (("pack",), ("cell_id",), ("status",), ("mean_and_half_width_equal_primary",), ("equals_primary",),
                    ("not_below_primary",)) + nested("primary", SENSITIVITY_SHAPE["reported_values"]) \
            + nested("sensitivity", SENSITIVITY_SHAPE["reported_values"])
        refused = (("pack",), ("cell_id",), ("status",), ("code",))
        keys = refused if entry["p42"] else computed
        match = {"cell_id": cid}
        rows = [(doc, path + (match,), keys) for doc, path in
                (("sensitivity", ("reported_cells",)), ("disclosure", ("sensitivity", "reported_cells")))]
        rows.append(("disclosure", ("block_lines", {"line": "sensitivity_reported", ("record", "cell_id"): cid}),
                     tuple(("record",) + k for k in keys)))
        if entry["p42"]:
            # The registered p42 exit (step 4 p42_floor_cells_only): refused in every copy; the recompute's p42 status.
            add("sensitivity_reported", f"sensitivity/reported_cells/{pack}/{cid}", rows,
                [(("p42", family), (("status",),))])
            add("projection_cell", f"projection/{pack}/{cid}",
                [("projection:" + pack, ("refused_cells", match), (("code",),))], [(("p42", family), (("status",),))])
            continue
        # A non-p42 reported cell is computed or refused (below the registered minimum) on each side; the rows
        # and lines of a computed cell are expected when either side says computed.
        add("projection_cell", f"projection/{pack}/{cid}",
            [("any", (("projection:" + pack, ("cells", match), PROJECTION_KEYS),
                      ("projection:" + pack, ("refused_cells", match), (("code",),))))],
            [(("reported_cells", family), (("status",),))])
        condition = ("reported_computed", pack, cid, family)
        add("sensitivity_reported", f"sensitivity/reported_cells/{pack}/{cid}", rows,
            [(bound + ("reported_cells", family), (("status",),))], condition)
        # Refused on both sides (below the registered minimum): the record keeps the refusal and its code.
        add("sensitivity_reported", f"sensitivity/reported_cells/{pack}/{cid}/refused",
            [(doc, path[:-1] + (match,), refused) for doc, path, _ in rows[:2]]
            + [(rows[2][0], rows[2][1], tuple(("record",) + k for k in refused))],
            [(("reported_cells", family), (("status",),))], ("not", condition))
        cell = {"pack": pack, "cell_id": cid}
        own = (("reported_cells", family), (("mean_j",), ("lower_j",), ("upper_j",), ("interval", "h_j"),
                                            ("interval", "B_j"), ("n_r",), ("n_b",)))
        for word, keys, recompute in (
                ("reported_cell", tuple((k,) for k in DISCLOSURE_SHAPE["cell_values"]), own),
                ("battery_assist_cell", (("n_r",), ("n_b",), ("assist_members",), ("removed_unit_ids",), ("without",),
                                         ("without", "status")) + nested("primary", DISCLOSURE_SHAPE["cell_values"]),
                 (("disclosures", "battery_assist", family), (("n_r",), ("n_b",)))),
                ("attribution_floor", (("value_j",), ("attained_by",), ("minimum_j",)),
                 (("reported_cells", family, "attribution_floor"), (("value_j",), ("minimum_j",)))),
                ("kept_units", (("n_r",), ("n_b",)), (("reported_cells", family), (("n_r",), ("n_b",))))):
            add("cell_line", f"disclosure/cells/{word}/{pack}/{cid}",
                [("disclosure", ("cells", dict(cell, line=word)), keys)], [recompute], condition)
        model, phase = entry["model"], entry["phase"]
        add("cell_line", f"disclosure/cells/cross_window/{pack}/{cid}",
            [("disclosure", ("cells", dict(cell, line="cross_window")),
              (("G_j",), ("h_G_j",), ("F_j",), ("h_F_j",), ("delta_j",), ("agree",)))],
            [(("disclosures", "cross_window", f"{model}/{phase}"), (("G_j",), ("h_G_j",), ("F_j",), ("h_F_j",),
                                                                    ("delta_j",), ("agree",)))],
            ("cross_window", pack, cid, family, phase))
    for cid, entry in floors.items():
        pack, key = entry["pack"], cell_key(entry)
        keys = (("pack",), ("cell_id",), ("equals_primary",), ("not_below_primary",)) \
            + nested("primary", SENSITIVITY_SHAPE["floor_values"]) + nested("sensitivity", SENSITIVITY_SHAPE["floor_values"])
        match = {"cell_id": cid}
        add("sensitivity_floor", f"sensitivity/floor_cells/{cid}",
            [("sensitivity", ("floor_cells", match), keys), ("disclosure", ("sensitivity", "floor_cells", match), keys),
             ("disclosure", ("block_lines", {"line": "sensitivity_floor", ("record", "cell_id"): cid}),
              tuple(("record",) + k for k in keys))],
            [(bound + ("floor_cells", key), (("floor_abs_j",), ("floor_cmp_j",), ("floor_gate_j",)))])
        add("aggregate_cell", f"aggregate/{cid}",
            [("aggregate", ("cells", match), (("floor_abs_j",), ("floor_cmp_j",), ("floor_gate_j",)))],
            [(("floor_cells", key), (("floor_abs_j",), ("floor_cmp_j",), ("floor_gate_j",)))])
        for group, components in CLOSEOUT_RATIOS.items():
            for component in components:
                common = group == "common_mode"
                field = "common_mode_corner_widened_unguarded_floor_j" if common else "corner_widened_unguarded_floor_j"
                name = f"{key}/{component}" + ("/common_mode" if common else "")
                own = ("dominance", "common_mode", key) if common else ("dominance", "ratios", f"{key}/{component}")
                add("ratio", f"ratio/{name}",
                    [("ratios", ("ratios", {"cell_id": cid, "component": component, "numerator_field": field}),
                      (("n",), ("status",))),
                     ("disclosure", ("block_lines", {"line": "dominance_ratio", "cell_id": cid, "component": component,
                                                     "@ratio": "R_cm" if common else "R"}), (("n",), ("status",)))],
                    [(own, (("n",),))])
    add("dominance_branch", "closeout/branch",
        [("closeout", (), (("branch",), ("dominance_sentence_licensed",))),
         ("disclosure", ("block_lines", {"line": "dominance_branch"}), (("branch",), ("dominance_sentence_licensed",)))],
        [(("dominance",), (("branch",),))])
    # The floor windows' extraction cells, their floor lines, and each window's p42 exit.
    for cid, entry in registry.tables["extraction"].items():
        pack, match = entry["pack"], {"cell_id": cid}
        own = (("p42", entry["family"]), (("status",),)) if entry["p42"] else (("floors", floor_key(entry)), ())
        add("extraction_cell", f"extraction/{pack}/{cid}",
            [("extraction:" + pack, ("cells", match), (("kind",), ("extractable",)))], [own])
        add("floor_line", f"disclosure/floors/kept_units/{pack}/{cid}",
            [("disclosure", ("floors", {"line": "kept_units", "pack": pack, "cell_id": cid}), (("n_r",), ("n_b",)))],
            [own])
        if entry["p42"]:
            continue
        condition = ("floor_computed", pack, cid, floor_key(entry))
        add("extraction_floor", f"extraction/{pack}/{cid}/floor",
            [("extraction:" + pack, ("cells", match), (("operative_floor_j",), ("n_admitted",))
              + nested("floor", tuple(FLOOR_FIELDS) + ("corner_widened_guarded_floor_j", "drift_widened_unguarded_floor_j", "n")))],
            [(("floors", floor_key(entry)), tuple((k,) for k in FLOOR_FIELDS.values()) + (("n",),))], condition)
        add("floor_line", f"disclosure/floors/floor_composition/{pack}/{cid}",
            [("disclosure", ("floors", {"line": "floor_composition", "pack": pack, "cell_id": cid}),
              tuple((k,) for k in LINE_KEYS["floors"]["floor_composition"]))],
            [(("floors", floor_key(entry)), (("guarded_floor_j",), ("allowance_j",), ("drift_widened_guarded_floor_j",))),
             (("windows", PACKS[pack], "neg8"), (("source",),))], condition)
    for pack in PACKS:
        add("bracket", f"brackets/{pack}",
            [("bracket:" + pack, (), (("b_sens",), ("evaluation", "acceptance", "allowance", "operative_b_fiducial_binary64_s")))],
            [(("windows", PACKS[pack]), (("b_op_s",),)), (bound + ("windows", PACKS[pack]), (("b_sens_s",),))])
    add("bracket", "brackets/block", [("block_bracket", (), (("value_s",), ("T",), ("attained_by_sequence",)))],
        [(bound, (("B_max_s",), ("T",), ("attaining_sequence",)))])
    # The contrasts: the verdict row, its fill copy, their floors, leave-one-out rows and disclosure lines.
    for cid, entry in contrasts.items():
        match = {"contrast_id": cid}
        verdict = (tuple((k,) for k in ENGINE_KEYS["contrast"]) + nested("metric", ENGINE_KEYS["metric"])
                   + nested("conditions", ENGINE_KEYS["conditions"])
                   + nested("sampling", ENGINE_KEYS["sampling"] + ENGINE_KEYS["kept_sampling"])
                   + nested("estimator", ENGINE_KEYS["estimator"])
                   + tuple(("estimator", "metrology_aware_CI95") + side for side in INTERVAL)
                   + nested("deterministic_bounds", ENGINE_KEYS["deterministic"])
                   + tuple(("deterministic_bounds", "decision_interval") + side for side in INTERVAL)
                   + nested("floor", ENGINE_KEYS["floor"] + ENGINE_KEYS["v3_floor"]) + arms(("floor", "floor_row_ids"))
                   + nested("multiplicity", ENGINE_KEYS["multiplicity"]) + nested("loo", ENGINE_KEYS["loo"])
                   + nested("claim_evaluation", ENGINE_KEYS["evaluation"])
                   + (("bundle_blocks", "planned_block_ids"), ("bundle_blocks", "blocks")))
        fill = (tuple((k,) for k in FILL_SHAPE["contrast"]) + nested("metric", ENGINE_KEYS["metric"])
                + nested("conditions", ENGINE_KEYS["conditions"])
                + nested("sampling", ENGINE_KEYS["sampling"] + ENGINE_KEYS["kept_sampling"])
                + tuple(("interval",) + side for side in INTERVAL)
                + tuple(("decision_interval",) + side for side in INTERVAL)
                + nested("floor", ENGINE_KEYS["floor"] + ENGINE_KEYS["v3_floor"]) + arms(("floor", "floor_row_ids"))
                + arms(("floor_source_cell_ids",)) + nested("multiplicity", ENGINE_KEYS["multiplicity"])
                + nested("loo", ENGINE_KEYS["loo"]) + nested("claim_evaluation", ENGINE_KEYS["evaluation"]))
        own = (("contrasts", cid), tuple((k,) for k in ("n", "dbar_j", "s_d_j", "se_j", "t_star", "metrology_interval_j",
                                                        "D_j", "decision_interval_j", "floor_gate_j", "p", "holm_p",
                                                        "holm_reject", "outcome", "ceiling", "loo", "kept_quads")))
        add("contrast", f"contrast/{cid}", [("verdicts", ("contrasts", match), verdict),
                                            ("fill", ("gamma", "contrasts", match), fill)], [own])
        for index, pack in ARMS.items():
            arm = f"{MODELS[pack]}/{entry['phase']}"
            for name, keys in (("arm_gates", tuple((k,) for k in ENGINE_KEYS["arm_gate"])),
                               ("resolutions", tuple((k,) for k in ENGINE_KEYS["resolution"]) + (("source_cell_ids", 0),))):
                path = ("contrasts", match, "floor", name, index)
                add("contrast_floor_" + name[:-1], f"contrast/{cid}/{name}/{index}",
                    [("verdicts", path, keys), ("fill", ("gamma",) + path, keys)],
                    [(("floor_cells", arm), (("floor_gate_j",),) if name == "arm_gates"
                      else (("floor_abs_j",), ("floor_cmp_j",), ("floor_gate_j",)))])
        for block in registry.blocks[cid]:
            path = ("contrasts", match, "loo", "rows", {"omitted_block_id": block})
            keys = tuple((k,) for k in ENGINE_KEYS["loo_row"]) + tuple(("metrology_aware_ci95",) + s for s in INTERVAL) \
                + tuple(("decision_interval",) + s for s in INTERVAL)
            add("loo_row", f"contrast/{cid}/loo/{block}",
                [("verdicts", path, keys), ("fill", ("gamma",) + path, keys)],
                [(("contrasts", cid, "loo", {"block_number": registry.blocks[cid].index(block) + 1}),
                  (("dbar_j",), ("p",), ("holm_p",), ("outcome",), ("n",), ("above_floor",), ("holm_reject",)))],
                ("loo_block_kept", cid, block))
        line = {"line": None, "contrast_id": cid}
        own_descriptive = (("descriptive", cid), (("per_token_difference_j",), ("per_token_metrology_interval_j",),
                                                  ("per_token_decision_interval_j",)))
        for word, keys, recompute, condition in (
                ("primary_contrast", nested("estimator", ENGINE_KEYS["estimator"])
                 + tuple(("estimator", "metrology_aware_CI95") + s for s in INTERVAL)
                 + tuple(("decision_interval",) + s for s in INTERVAL), own, None),
                ("battery_assist_contrast", (("status",), ("n",), ("assist_quads",), ("assist_members",)),
                 (("disclosures", "battery_assist", cid), (("n",), ("assist_quads",))), None),
                ("magnitude_ratio", (), (("descriptive", cid), ()), None),
                ("magnitude_ratio", (("log_mean",), ("log_sd",), ("ratio",), ("lower",), ("upper",)),
                 (("descriptive", cid), (("ratio",), ("ratio_interval",))), ("ratio_computable", cid)),
                ("magnitude_per_token", (("value_j",), ("denominator",)) + tuple(("metrology",) + s for s in INTERVAL)
                 + tuple(("decision",) + s for s in INTERVAL), own_descriptive, None),
                ("contrast_interval", (("n",), ("rounded_t",), ("exact_t",)), (("contrasts", cid), (("n",), ("t_star",))),
                 None),
                ("decision_floor", (("floor_j",), ("estimate_j",)) + tuple(("decision_interval",) + s for s in INTERVAL),
                 (("contrasts", cid), (("floor_gate_j",), ("dbar_j",), ("decision_interval_j",))), None),
                ("loo_counts", (("count",), ("exclusive_block_numbers",)), (("contrasts", cid), (("loo",),)), None),
                ("loo_magnitude", (("rows",),), (("contrasts", cid), (("loo",),)), None),
                ("kept_units", (("n_r",), ("n_b",)), (("contrasts", cid), (("n",),)), None)):
            selector = dict(line, line=word) if word != "kept_units" else {"line": word, "pack": "gamma", "cell_id": cid}
            check = f"disclosure/contrasts/{word}/{cid}" + ("/estimates" if condition else "")
            add("contrast_line", check, [("disclosure", ("contrasts", selector), keys)], [recompute], condition)
        keys = (("contrast_id",), ("floor_cell_ids",), ("bound_independent_values_equal_primary",),
                ("outcome_equals_primary",), ("not_below_primary",)) + arms(("floor_cell_ids",)) \
            + nested("primary", SENSITIVITY_SHAPE["contrast_values"]) + nested("sensitivity", SENSITIVITY_SHAPE["contrast_values"])
        add("sensitivity_contrast", f"sensitivity/contrasts/{cid}",
            [("sensitivity", ("contrasts", match), keys), ("disclosure", ("sensitivity", "contrasts", match), keys),
             ("disclosure", ("block_lines", {"line": "sensitivity_contrast", ("record", "contrast_id"): cid}),
              tuple(("record",) + k for k in keys))],
            [(bound + ("contrasts", cid), (("floor_gate_j",), ("D_j",), ("outcome",)))])
    return table


# The seven registered NEG-8 bound terms of the neg8_allowance line and the recompute's names for them.
NEG8_TERM = "bracket.claim_families.gross_energy."
NEG8_TERMS = ("bound_envelope_j", "bound_prediction_j", "start.mean_j", "midpoint.mean_j", "end.mean_j",
              "trajectory_excursion_max_j", "drift_allowance_j")
NEG8_OWN = ("bound_envelope_j", "bound_prediction_j", "start_mean_j", "midpoint_j", "end_mean_j", "spread_j", "allowance_j")
# The projection cell keys each compared reported-cell value is read from (paper-reported-energy kernel rows).
PROJECTION_KEYS = (("mean_j",), ("lower_j",), ("upper_j",), ("interval", "h_j"), ("interval", "B_j"), ("interval", "s_r"),
                   ("interval", "s_b"), ("interval", "variance"), ("interval", "n_r"), ("interval", "n_b"),
                   ("interval", "df"), ("interval", "kind_averages_j"), ("attribution_floor", "value_j"),
                   ("attribution_floor", "minimum_j"), ("attribution_floor", "attained_by"), ("per_token", "j_per_token"),
                   ("n_bundles",), ("kept_units",))
# The kinds whose entries are documents or sections: they require their keys but claim no item (an item is claimed
# only by its own entry, so a leaf is in the table only under its own row, line or cell).
CONTAINERS = ("fill_document", "verdicts_document", "disclosure_document", "disclosure_window", "sensitivity_record",
              "kept_units_record", "bracket")
# Every item of these lists must be claimed by an entry (an output item outside the table can only DISAGREE;
# it never creates a check): (document, path with * for each list item or window, the line words concerned).
CELL_WORDS = ("reported_cell", "battery_assist_cell", "attribution_floor", "kept_units", "cross_window")
CONTRAST_WORDS = ("primary_contrast", "battery_assist_contrast", "magnitude_ratio", "magnitude_per_token",
                  "contrast_interval", "decision_floor", "loo_counts", "loo_magnitude", "kept_units")
BLOCK_WORDS = ("sensitivity_bmax", "sensitivity_window", "sensitivity_reported", "sensitivity_floor",
               "sensitivity_contrast", "sensitivity_boundary", "dominance_ratio", "dominance_branch", "harvest_once")
CLOSED = (("fill", ("gamma", "contrasts"), None), ("verdicts", ("contrasts",), None),
          ("fill", ("gamma", "contrasts", "*", "loo", "rows"), None), ("verdicts", ("contrasts", "*", "loo", "rows"), None),
          ("fill", ("gamma", "contrasts", "*", "floor", "arm_gates"), None),
          ("fill", ("gamma", "contrasts", "*", "floor", "resolutions"), None),
          ("verdicts", ("contrasts", "*", "floor", "arm_gates"), None),
          ("verdicts", ("contrasts", "*", "floor", "resolutions"), None),
          ("disclosure", ("cells",), CELL_WORDS), ("disclosure", ("floors",), ("floor_composition", "kept_units")),
          ("disclosure", ("contrasts",), CONTRAST_WORDS),
          ("disclosure", ("window_lines", "*"), WINDOW_LINES + ("tripwire",)),
          ("disclosure", ("block_lines",), BLOCK_WORDS), ("disclosure", ("fixed_sentences",), None),
          ("disclosure", ("sensitivity", "reported_cells"), None), ("disclosure", ("sensitivity", "floor_cells"), None),
          ("disclosure", ("sensitivity", "contrasts"), None), ("sensitivity", ("reported_cells",), None),
          ("sensitivity", ("floor_cells",), None), ("sensitivity", ("contrasts",), None),
          ("projection:alpha", ("cells",), None), ("projection:alpha", ("refused_cells",), None),
          ("projection:beta", ("cells",), None), ("projection:beta", ("refused_cells",), None),
          ("extraction:alpha", ("cells",), None), ("extraction:beta", ("cells",), None),
          ("aggregate", ("cells",), None), ("ratios", ("ratios",), None))
DUPLICATE = object()
# The compared lines the table does not list (NEEDS_RULING RC-CMP-9 2): the whole-machine member and summary lines
# print only when the window has a meter record, per member of that record (pairs over L9's disclosure, the
# harvest meter record and the recompute, RC-CMP-3 X3); the battery-temperature sentence only for a flagged stage.
TABLE_CONDITIONAL_LINES = r"disclosure:window_lines/[a-z]+/(machine_member|machine_summary|battery_temperature_sentence)/"
RATIO_TEXT = r"\S+ \S+: (R|R_cm) "


def listed(value):
    return value if isinstance(value, list) else []


def matches(item, selector):
    """A list item carrying every identity field of the selector (equal type and value)."""
    if not isinstance(item, dict):
        return False
    for field, value in selector.items():
        if field == "@ratio":
            # A dominance ratio line names its ratio (R or R_cm) only in its text (disclosures._closeout_lines).
            found = re.match(RATIO_TEXT, str(item.get("text", "")))
            if not found or found[1] != value:
                return False
        else:
            found = get(item, *field, default=MISSING) if isinstance(field, tuple) else item.get(field, MISSING)
            if type(found) is not type(value) or found != value:
                return False
    return True


def resolve(node, path):
    """(the item at path, its concrete path); MISSING when a step is absent, DUPLICATE when a selector matches twice."""
    at = ()
    for step in path:
        if isinstance(step, dict):
            hits = [i for i, item in enumerate(listed(node)) if matches(item, step)]
            if len(hits) != 1:
                return (DUPLICATE if hits else MISSING), at
            step = hits[0]
        elif isinstance(step, int):
            if not isinstance(node, list) or not 0 <= step < len(node):
                return MISSING, at
        elif not isinstance(node, dict) or step not in node:
            return MISSING, at
        node, at = node[step], at + (step,)
    return node, at


def absent_keys(item, keys):
    return [key for key in keys if resolve(item, key)[0] in (MISSING, DUPLICATE)]


def describe(step):
    return ",".join(f"{'.'.join(k) if isinstance(k, tuple) else k}={v}" for k, v in step.items()) \
        if isinstance(step, dict) else str(step)


class Documents:
    """L9's documents an expected check reads, each read once per run through the custody (and its gate)."""
    def __init__(self, custody):
        self.custody, self.read = custody, {}

    def __getitem__(self, label):
        if label not in self.read:
            pattern, how = check_doc(label)
            self.read[label] = (labelled(self.custody, pattern, "sensitivity") if how == "sensitivity"
                                else self.custody.one(pattern))
        return self.read[label]


def phase_n(docs, ours, registry, phase):
    """The kept n of the contrast of a phase, on either side (the verdict's estimator n, the recompute's n)."""
    values = []
    for cid, entry in registry.tables["contrast"].items():
        if entry["phase"] == phase:
            row = next((r for r in listed(get(docs["verdicts"], "contrasts")) if isinstance(r, dict)
                        and r.get("contrast_id") == cid), {})
            values += [get(row, "estimator", "n"), get(ours, "contrasts", cid, "n")]
    return [v for v in values if finite(v)]


def condition_holds(condition, docs, ours, registry):
    """A conditional entry's registered condition: the status or kept word that makes the producer print the item,
    read on either side (F5), so a word on one side requires the item on both."""
    kind = condition[0]
    if kind == "not":
        return not condition_holds(condition[1], docs, ours, registry)
    if kind == "reported_computed":
        _, pack, cid, family = condition
        own = get(ours, "reported_cells", family)
        return (any(isinstance(cell, dict) and cell.get("cell_id") == cid
                    for cell in listed(get(docs["projection:" + pack], "cells")))
                or isinstance(own, dict) and own.get("status", "computed") == "computed")
    if kind == "cross_window":
        _, pack, cid, family, phase = condition
        return (condition_holds(("reported_computed", pack, cid, family), docs, ours, registry)
                and any(n >= 2 for n in phase_n(docs, ours, registry, phase)))
    if kind == "floor_computed":
        _, pack, cid, key = condition
        cell = next((c for c in listed(get(docs["extraction:" + pack], "cells"))
                     if isinstance(c, dict) and c.get("cell_id") == cid), {})
        own = get(ours, "floors", key)
        return (get(cell, "floor", "guarded_floor_j") is not None
                or isinstance(own, dict) and own.get("status", "computed") == "computed")
    if kind == "loo_block_kept":
        # The engine's leave-one-out rows (analysis_engine _loo_family): one per kept block of a complete contrast;
        # the recompute computes them from three kept quads (finish_contrast). Expected when either side keeps the
        # block and either side's kept n is at least LOO_MIN.
        _, cid, block = condition
        row = next((r for r in listed(get(docs["verdicts"], "contrasts")) if isinstance(r, dict)
                    and r.get("contrast_id") == cid), {})
        ns = [n for n in (get(row, "estimator", "n"), get(ours, "contrasts", cid, "n")) if finite(n)]
        position = registry.blocks[cid].index(block) + 1
        kept = (any(isinstance(b, dict) and b.get("block_id") == block and b.get("included") is True
                    for b in listed(get(row, "bundle_blocks", "blocks")))
                or block in listed(get(ours, "contrasts", cid, "kept_quads"))
                or any(isinstance(r, dict) and same(r.get("block_number"), position)
                       for r in listed(get(ours, "contrasts", cid, "loo"))))
        return kept and any(n >= LOO_MIN for n in ns)
    if kind == "ratio_computable":
        line = next((r for r in listed(get(docs["disclosure"], "contrasts")) if isinstance(r, dict)
                     and r.get("line") == "magnitude_ratio" and r.get("contrast_id") == condition[1]), {})
        return "ratio" in line or finite(get(ours, "descriptive", condition[1], "ratio"))
    raise ValueError(kind)


# The recompute's leave-one-out minimum (independent_recompute_b5.finish_contrast: rows from three kept quads).
LOO_MIN = 3


def expected_items(custody, ours, table, claimed):
    """RC-CMP-9: each expected check's state on both sides, before any comparison.

    Returns (expected, l9, own, missing): the checks whose condition holds; those whose every L9 copy resolves
    with its required keys; those whose every recompute item does; and, per check, what is missing (names only).
    Each item an entry resolves on L9's side is claimed (claimed[document] gets its concrete path). Every item of
    a closed list that no entry claimed becomes an unexpected/ check present on L9's side only (it can confirm a
    check, never create one).
    """
    registry = custody.registry
    docs = Documents(custody)
    expected, l9, own, missing = {}, {}, {}, {}
    for entry in table:
        if entry["condition"] is not None and not condition_holds(entry["condition"], docs, ours, registry):
            continue
        absent = []
        for locator in entry["l9"]:
            choices = locator[1] if locator[0] == "any" else (locator,)
            found = []
            for label, path, keys in choices:
                item, at = resolve(docs[label], path)
                if item is DUPLICATE:
                    absent.append(f"l9:{label}:duplicated:" + "/".join(map(describe, path)))
                elif item is not MISSING:
                    found.append((label, at, absent_keys(item, keys)))
            if len(found) != 1:
                absent.append(f"l9:{choices[0][0]}:" + ("absent:" if not found else "both:")
                              + "/".join(map(describe, choices[0][1])))
            for label, at, keys in found:
                if entry["kind"] not in CONTAINERS:
                    claimed.setdefault(label, set()).add(at)
                absent += [f"l9:{label}:key:" + "/".join(map(str, at + key)) for key in keys]
        for path, keys in entry["recompute"]:
            item, at = resolve(ours, path)
            if item is MISSING or item is DUPLICATE:
                absent.append("recompute:absent:" + "/".join(map(describe, path)))
            else:
                absent += ["recompute:key:" + "/".join(map(str, at + key)) for key in absent_keys(item, keys)]
        expected[entry["check"]] = entry
        if not any(m.startswith("l9:") for m in absent):
            l9[entry["check"]] = entry
        if not any(m.startswith("recompute:") for m in absent):
            own[entry["check"]] = entry
        missing[entry["check"]] = absent
    for label, path, words in CLOSED:
        for at, item in closed_items(docs[label], path):
            if (words is None or isinstance(item, dict) and item.get("line") in words) and at not in claimed.get(label, set()):
                check = f"unexpected/{label}:" + "/".join(map(str, at))
                l9[check], missing[check] = None, ["l9:item_not_in_table"]
    return expected, l9, own, missing


def compare_expected(c, custody, ours):
    """RC-CMP-9 (the design rule): every expected check finds its item on L9's side and on the recompute's.

    One routing_id row per check (expected/<check>): present on L9's side when the table expects it and every L9
    copy resolves with its required keys, on the recompute's when every recompute item does; anything missing is
    DISAGREE (never skipped) and the row lists what is missing (names only). An unexpected/ item (an L9 item no
    entry claimed) is on neither side: DISAGREE.
    """
    table = expected_checks(custody.registry)
    expected, l9, own, missing = expected_items(custody, ours, table, c.claimed)
    for check, _, _, _ in c.pairs("expected/", expected, l9, own):
        if missing.get(check):
            c.rows[-1]["missing"] = missing[check]
    return table


def closed_items(node, path, at=()):
    """(concrete path, item) of every item of the lists at path (* expands every list item or object member)."""
    if not path:
        yield from (((at + (index,)), item) for index, item in enumerate(listed(node)))
        return
    step, rest = path[0], path[1:]
    if step == "*":
        members = enumerate(node) if isinstance(node, list) else node.items() if isinstance(node, dict) else ()
        for key, item in members:
            yield from closed_items(item, rest, at + (key,))
    elif isinstance(node, dict) and step in node:
        yield from closed_items(node[step], rest, at + (step,))


def table_structure(table):
    """The table's structure for the restricted output: its families, each check's name and condition (no value)."""
    families = {}
    for entry in table:
        families[entry["kind"]] = families.get(entry["kind"], 0) + 1
    return {"registered_sources": list(REGISTERED_SOURCES), "families": families,
            "checks": [{"kind": e["kind"], "check": e["check"], "l9": sorted({loc[0] if loc[0] != "any" else loc[1][0][0]
                                                                            for loc in e["l9"]}),
                        "condition": None if e["condition"] is None else str(e["condition"][0])} for e in table]}


# G2: each identity field and the objects that own it, taken from the producers (paths with * per list
# item): the fill's contrast rows and their leave-one-out rows (results_fill_adapter.adapt_claim_verdicts);
# the disclosure record's _item lines (and removed_unit and stored_member_reason lines), the
# loo_magnitude rows, the sensitivity record's rows and their block_lines copies (b5_analysis/disclosures.py).
LINE = r"(cells|floors|contrasts|block_lines|window_lines/[a-z]+)/\*"
IDENTITY_OWNERS = {
    "fill": {"contrast_id": r"gamma/contrasts/\*", "omitted_block_id": r"gamma/contrasts/\*/loo/rows/\*"},
    "disclosure": {
        "text": r"(cells|floors|contrasts|block_lines|fixed_sentences|window_lines/[a-z]+)/\*",
        "contrast_id": r"contrasts/\*|sensitivity/contrasts/\*|block_lines/\*/record",
        "cell_id": r"(cells|floors|contrasts|block_lines)/\*|sensitivity/(reported_cells|floor_cells)/\*|block_lines/\*/record",
        "pack": LINE + r"|sensitivity/(reported_cells|floor_cells)/\*|block_lines/\*/record",
        "run_id": r"window_lines/[a-z]+/\*", "model": r"window_lines/[a-z]+/\*", "component": r"block_lines/\*",
        "block_number": r"contrasts/\*/rows/\*"}}
# Identity-named fields that are an attribute of another object and never route: a band's window.
IDENTITY_ATTRIBUTES = {"fill": r"(?!)", "disclosure": r"window_lines/[a-z]+/\*/central_band/pack"}
# G3: where an L9 id routes a binding, and the registered tables it must be listed in.
ROUTED = {"fill": ((r"gamma/contrasts/\*/contrast_id", ("contrast",)),),
          "disclosure": ((r"cells/\*/cell_id", ("reported",)), (r"floors/\*/cell_id", ("extraction",)),
                         (r"contrasts/\*/(contrast_id|cell_id)", ("contrast",)), (r"block_lines/\*/cell_id", ("floor",)),
                         (r"sensitivity/reported_cells/\*/cell_id", ("reported",)),
                         (r"sensitivity/floor_cells/\*/cell_id", ("floor",)),
                         (r"(sensitivity/contrasts/\*|block_lines/\*/record)/contrast_id", ("contrast",)),
                         (r"block_lines/\*/record/cell_id", ("reported", "floor")))}


# F2 (RC-CMP6-OPUS-REV finding 2): each disclosure section's line words and, for each word, the value keys
# its producer writes beside line, restricted, label and text (b5_analysis/disclosures.py _item calls and the
# removed_unit and stored_member_reason dicts). A line word outside its section's table, or a key outside its
# word's set, refuses line_word_unregistered or line_key_unregistered: a line cannot be relabelled into
# another word's rules (or another section) and carry its own leaves along.
LINE_COMMON = ("line", "restricted", "label", "text")
CELL_LINES_KEYS = {
    "reported_cell": ("pack", "cell_id", "status", "mean_j", "h_j", "B_j", "lower_j", "upper_j"),
    "battery_assist_cell": ("pack", "cell_id", "primary", "without", "n_r", "n_b", "assist_members", "removed_unit_ids"),
    "load_correlated_cell": ("pack", "cell_id", "restored_counts", "families", "values"),
    "attribution_floor": ("pack", "cell_id", "value_j", "attained_by", "minimum_j"),
    "cross_window": ("pack", "cell_id", "G_j", "h_G_j", "F_j", "h_F_j", "delta_j", "agree")}
UNIT_LINES_KEYS = {
    "kept_units": ("pack", "cell_id", "n_r", "n_b"),
    "removed_unit": ("pack", "cell_id", "unit_id", "stratum", "families", "codes", "positions", "stage_ids")}
LINE_KEYS = {
    "cells": {**CELL_LINES_KEYS, **UNIT_LINES_KEYS},
    "floors": {"floor_composition": ("pack", "cell_id", "guarded_j", "allowance_j", "source", "drift_widened_j", "minted_j"),
               **UNIT_LINES_KEYS},
    "contrasts": {
        "primary_contrast": ("contrast_id", "estimator", "decision_interval"),
        "battery_assist_contrast": ("contrast_id", "status", "n", "mean_j", "s_d", "se", "t_star", "lower_j", "upper_j",
                                    "assist_quads", "assist_members"),
        "load_correlated_contrast": ("contrast_id", "restored_count", "families", "values"),
        "magnitude_ratio": ("contrast_id", "log_mean", "log_sd", "ratio", "lower", "upper"),
        "magnitude_per_token": ("contrast_id", "value_j", "denominator", "metrology", "decision"),
        "contrast_interval": ("contrast_id", "n", "rounded_t", "exact_t"),
        "decision_floor": ("contrast_id", "decision_interval", "floor_j", "estimate_j"),
        "loo_counts": ("contrast_id", "count", "exclusive_block_numbers"),
        "loo_magnitude": ("contrast_id", "rows"),
        **UNIT_LINES_KEYS},
    "fixed_sentences": dict.fromkeys(("floor_drift_ownership", "gross_energy", "conditionality", "config_binding",
                                      "single_window", "floor_transfer_assumption", "floor_transfer_limit", "order", "p42",
                                      "separate_windows", "dominance", "d177", "fixed_prompt"), ()),
    "window_lines": {
        "machine_absent": (), "machine_boundary": (), "monitor_sentence": (), "lost_midpoint": (), "catalog_path": (),
        "stored_verdict_boundary": (),
        "machine_member": ("model", "run_id", "rho", "rail_j", "machine_j", "removed", "plausible", "meter_flags",
                           "battery_term_available"),
        "machine_summary": ("model", "median", "minimum", "maximum", "q25", "q75", "spread", "central_band"),
        "monitor_cost": ("cpu_s", "reader_cpu_s", "probes_inside_target_phases"),
        "arm_hazards": ("module", "phase", "verdict", "measurements"),
        "physics_counts": ("counts",), "anchor_counts": ("count",), "anchor_bound": ("value_s",), "host_cpu": ("value_s",),
        "battery_counts": ("counts",), "battery_phase": ("phase", "measurements"), "battery_discharged": ("value_j",),
        "neg8_screen": ("decision",), "reference_counts": ("counts", "planned"),
        "reference_lost": ("run_id", "slot", "reason"), "reference_spare": ("run_id", "slot", "succeeded"),
        "corpus_counts": ("collected", "in_window", "deciding", "desk_cap", "drop_counts"),
        "corpus_physics_drop": ("run_id", "codes"), "bound_formula": ("formula",), "neg8_allowance": ("source", "values_j"),
        "battery_temperature": ("stage_id", "readings_centi_c", "rise_k", "plateau", "harvest_flag", "producer_flag",
                                "temperature_unmeasured", "differs_from_harvest_flag"),
        "temperature_disagreement": ("stage_id",), "battery_temperature_sentence": ("stage_id", "rise_k", "neg8"),
        "flag_count": ("count", "family", "code", "blinding"), "arm_unmeasured": ("modules",), "erratum3_triggers": ("values",),
        "below_screen_bound": ("b_op_s", "below"), "stored_status": ("status",),
        "stored_condition": ("condition", "answered_by"),
        "stored_member_reason": ("pack", "codes", "reason", "count", "all_removed", "families"),
        "adapter_continuity": ("decision",), "tripwire": ("tripwire", "result"),
        "deciding_membership": ("writer_excluded_by_family", "writer_excluded_all_removed", "deciding_references",
                                "deciding_spares", "writer_excluded_count"),
        "reference_parity": ("result", "harvest_pin"),
        "ledger_binding": ("sha256sums_sha256", "ledger_copy_sha256", "terminal_sequence", "prefix_result")},
    "block_lines": {
        "superseded_history": (), "sensitivity_boundary": (),
        "attempt_count": ("pack", "superseded", "count", "causes"),
        "attempt_history": ("pack", "plan_id", "attempt", "verdict", "cause_key", "superseded", "flags_by_family",
                            "collected", "planned", "catalog_path", "triggers"),
        "g10": ("pack", "plan_id", "codes", "redraw_cycles"),
        "harvest_once": ("no_analysed_window_harvested_twice",),
        "reharvest_account": ("pack", "original_pin", "deciding_pin", "original_harvest_sha256", "deciding_harvest_sha256",
                              "reason", "survivors_before", "survivors_after"),
        "sensitivity_bmax": ("value_s", "T", "attained_by_sequence"),
        "sensitivity_window": ("pack", "plan_id", "b_op_s", "b_sens_s", "widened"),
        "sensitivity_reported": ("record",), "sensitivity_floor": ("record",), "sensitivity_contrast": ("record",),
        "dominance_ratio": ("cell_id", "component", "n", "status", "ratio", "numerator_j", "denominator_j"),
        "dominance_branch": ("branch", "dominance_sentence_licensed")}}


# F3 (RC-CMP-8): each compared claim line's required keys, the keys its producer writes unconditionally
# (b5_analysis/disclosures.py). A key a producer writes only for some values is left out: dominance_ratio's
# ratio, numerator and denominator (status complete), battery_assist_contrast's estimates (status computed),
# magnitude_ratio's estimates (computable), machine_summary's statistics and band (finite or plausible rho).
CONDITIONAL_KEYS = {("block_lines", "dominance_ratio"): ("ratio", "numerator_j", "denominator_j"),
                    ("contrasts", "battery_assist_contrast"): ("mean_j", "s_d", "se", "t_star", "lower_j", "upper_j"),
                    ("contrasts", "magnitude_ratio"): ("log_mean", "log_sd", "ratio", "lower", "upper"),
                    ("window_lines", "machine_summary"): ("median", "minimum", "maximum", "q25", "q75", "spread",
                                                         "central_band")}
COMPARED_LINES = {"cells": ("reported_cell", "battery_assist_cell", "cross_window", "attribution_floor"),
                  "floors": ("floor_composition",),
                  "contrasts": ("primary_contrast", "battery_assist_contrast", "magnitude_ratio", "magnitude_per_token",
                                "contrast_interval", "decision_floor", "loo_counts", "loo_magnitude"),
                  "window_lines": ("below_screen_bound", "neg8_screen", "neg8_allowance", "reference_counts",
                                   "corpus_counts", "machine_member", "machine_summary", "battery_temperature_sentence"),
                  "block_lines": ("dominance_branch", "dominance_ratio", "sensitivity_bmax", "sensitivity_window",
                                  "sensitivity_reported", "sensitivity_floor", "sensitivity_contrast")}
REQUIRED_KEYS = {(section, word): tuple(key for key in LINE_KEYS[section][word]
                                        if key not in CONDITIONAL_KEYS.get((section, word), ()))
                 for section, words in COMPARED_LINES.items() for word in words}
# The sensitivity record's rows (sensitivity.py), in the record and in their block_lines copies: a refused
# reported cell carries its code; a computed one its values and three relation words.
SENSITIVITY_KEYS = {
    "reported_cells": {"refused": ("pack", "cell_id", "status", "code"),
                       "computed": ("pack", "cell_id", "status", "primary", "sensitivity",
                                    "mean_and_half_width_equal_primary", "equals_primary", "not_below_primary")},
    "floor_cells": ("pack", "cell_id", "primary", "sensitivity", "equals_primary", "not_below_primary"),
    "contrasts": ("contrast_id", "floor_cell_ids", "primary", "sensitivity", "bound_independent_values_equal_primary",
                  "outcome_equals_primary", "not_below_primary"),
    "windows": ("plan_id", "b_op_s", "b_sens_s", "widened")}
# F5 (RC-CMP-9): the conditional keys and the status word that makes the producer print them: a complete dominance
# ratio carries its ratio, numerator and denominator (disclosures._closeout_lines); a computed assist contrast its
# estimates, a one-quad one its mean (disclosures._paired_values).
STATUS_KEYS = {("block_lines", "dominance_ratio"): ("status", {"complete": ("ratio", "numerator_j", "denominator_j")}),
               ("contrasts", "battery_assist_contrast"): ("status", {
                   "computed": ("mean_j", "s_d", "se", "t_star", "lower_j", "upper_j"), "one_quad": ("mean_j",)})}
SENSITIVITY_LINES = {"sensitivity_reported": "reported_cells", "sensitivity_floor": "floor_cells",
                     "sensitivity_contrast": "contrasts"}
# The fill's claim words (results_fill_adapter.adapt_claim_verdicts copies them from the claim verdicts, which
# carry each unconditionally): per contrast, per leave-one-out row, and each floor window's claim_usable.
FILL_KEYS = {"contrast": ("contrast_id", "claim_role", "hypothesized_direction", "claim_evaluation", "multiplicity",
                          "sampling", "loo"),
             "claim_evaluation": ("outcome", "direction", "reason_codes", "claim_ready_for_l2_l3", "claim_level_ceiling"),
             "multiplicity": ("raw_p", "adjusted_p", "rejected"), "sampling": ("confirmatory_status",),
             "loo": ("status", "rows"), "loo_row": ("omitted_block_id", "outcome", "floor_status", "influence_triggers"),
             "campaign": ("claim_usable",)}


def require(value, keys, where):
    """F3: an object missing a key its producer always writes refuses (an omitted claim word is no agreement)."""
    missing = [key for key in keys if not isinstance(value, dict) or key not in value]
    if missing:
        raise Refusal(f"required_key_absent:{where}/{missing[0]}")


def sensitivity_row(row, name, where):
    keys = SENSITIVITY_KEYS[name]
    if isinstance(keys, dict):
        require(row, ("status",), where)
        keys = keys.get(row["status"], keys["computed"]) if isinstance(row["status"], str) else keys["computed"]
    require(row, keys, where)


def gate_sensitivity(record):
    """F3: the sensitivity record's rows and windows carry their producer's unconditional keys."""
    sensitivity = record.get("sensitivity")
    if not isinstance(sensitivity, dict):
        return
    for name in ("reported_cells", "floor_cells", "contrasts"):
        for row in sensitivity.get(name) or []:
            sensitivity_row(row, name, "disclosure:sensitivity/" + name)
    windows = sensitivity.get("windows")
    for pack in PACKS:
        require(get(windows, pack), SENSITIVITY_KEYS["windows"], "disclosure:sensitivity/windows/" + pack)


def gate_fill(fill):
    """F3: the fill's claim words are present wherever its producer writes them."""
    for pack in ("alpha", "beta"):
        require(get(fill, "campaigns", pack), FILL_KEYS["campaign"], "fill:campaigns/" + pack)
    for row in get(fill, "gamma", "contrasts", default=[]) or []:
        require(row, FILL_KEYS["contrast"], "fill:gamma/contrasts/*")
        for name in ("claim_evaluation", "multiplicity", "sampling", "loo"):
            require(row[name], FILL_KEYS[name], "fill:gamma/contrasts/*/" + name)
        for loo in row["loo"]["rows"] if isinstance(row["loo"]["rows"], list) else ():
            require(loo, FILL_KEYS["loo_row"], "fill:gamma/contrasts/*/loo/rows/*")


def gate_lines(record):
    """F2: every disclosure line carries a word its section's producer writes, with that word's keys only."""
    if not isinstance(record, dict):
        return
    windows = record.get("window_lines", {})
    sections = [(name, record.get(name, [])) for name in ("cells", "floors", "contrasts", "fixed_sentences", "block_lines")]
    if isinstance(windows, dict):
        for pack, lines in windows.items():
            if pack not in PACKS:
                raise Refusal("routing_id_unregistered:disclosure:window_lines/" + str(pack))
            sections.append(("window_lines", lines))
    for section, lines in sections:
        for line in lines if isinstance(lines, list) else ():
            word = line.get("line") if isinstance(line, dict) else None
            if not isinstance(word, str) or word not in LINE_KEYS[section]:
                raise Refusal(f"line_word_unregistered:disclosure:{section}")
            extra = set(line) - set(LINE_COMMON) - set(LINE_KEYS[section][word])
            if extra:
                raise Refusal(f"line_key_unregistered:disclosure:{section}/{word}/{min(extra)}")
            if LINE_KEYS[section][word] and not set(line) & set(LINE_KEYS[section][word]):
                # A keyed word's line always carries one of its values: a bare sentence is not one of them.
                raise Refusal(f"line_keys_absent:disclosure:{section}/{word}")
            require(line, REQUIRED_KEYS.get((section, word), ()), f"disclosure:{section}/{word}")
            # F5 (RC-CMP-9): a conditional key is required when the status word that makes its producer print it is.
            status = STATUS_KEYS.get((section, word))
            if status is not None:
                require(line, status[1].get(line.get(status[0]), ()) if isinstance(line.get(status[0]), str) else (),
                        f"disclosure:{section}/{word}/{line.get(status[0])}")
            if word in SENSITIVITY_LINES:
                sensitivity_row(line["record"], SENSITIVITY_LINES[word], f"disclosure:{section}/{word}/record")
            if word == "erratum3_triggers" and isinstance(line.get("values"), dict):
                # F5 (RC-CMP-9): the trigger object, when the record has its bracket, carries each of its keys.
                require(line["values"], TRIGGER_KEYS, f"disclosure:{section}/{word}/values")
    gate_sensitivity(record)


def owns(label, key, star):
    """Whether the object at star path owns identity field key (G2)."""
    pattern = IDENTITY_OWNERS[label].get(key)
    return pattern is not None and re.fullmatch(pattern, star) is not None


def gate(value, label, registry, star="", seen=frozenset()):
    """G2 and G3 over one step-11 output, before any comparison or binding reads it.

    An identity field anywhere but on the object it names, or repeating one an enclosing
    owner set, refuses identity_field_misplaced; a routing id the registry does not list
    (or lists for another window) refuses routing_id_unregistered.
    """
    if isinstance(value, list):
        for item in value:
            gate(item, label, registry, star + "/*" if star else "*", seen)
        return
    if not isinstance(value, dict):
        return
    named = set()
    for key, item in value.items():
        where = join(star, key)
        if key not in IDENTITY_FIELDS or re.fullmatch(IDENTITY_ATTRIBUTES[label], where):
            continue
        if not owns(label, key, star) or key in seen or not isinstance(item, str):
            raise Refusal(f"identity_field_misplaced:{label}:{where}")
        named.add(key)
        if key == "pack" and item not in PACKS:
            raise Refusal(f"routing_id_unregistered:{label}:{where}")
        for pattern, kinds in ROUTED[label]:
            if re.fullmatch(pattern, where):
                found = registry.lookup(item, kinds, f"{label}:{where}")
                if "pack" in found and isinstance(value.get("pack"), str) and found["pack"] != value["pack"]:
                    # A cell registered for another window than the line prints.
                    raise Refusal(f"routing_id_unregistered:{label}:{where}")
    for key, item in value.items():
        gate(item, label, registry, join(star, key), seen | named)


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


# G7: the NEG-8 family each registered reference role is compared in; such a member never enters
# run_phase_energy_j (L9's step 2 re-reduces science runs only) and is listed as excluded from it.
REFERENCE_FAMILIES = {"start": "reference_counts", "midpoint": "reference_counts", "end": "reference_counts",
                      "corpus": "corpus_counts"}
KEPT_UNITS = r"kept-units/[0-9a-f]{64}-%s\.json"


def compare_runs(c, custody, ours):
    """S-13's per-run term: each kept run's phase energies (and gross request energy).

    G7: the key universe is the registered science runs L9's step 2 re-reduces
    (step_2_universe), applied identically to both sides, never either side's output:
    a key is present on L9's side only when it is in the universe and L9 re-reduced it,
    and on the recompute's only when it is a selected member; so a universe run that
    either side lacks, or a run either side holds outside the universe, is DISAGREE.
    A member whose registered role is a NEG-8 reference is compared in its NEG-8
    family instead and listed in c.excluded with the reason compared_in:<family>.
    """
    members = ours.get("members")
    if not isinstance(members, dict):
        raise Refusal("recompute_member_detail_missing")
    registry = custody.registry
    universe, records = step_2_universe(custody)
    for pack in PACKS:
        # Both sides hash the stored derived/exclusions.json (the recompute's exclusions_sha256 is that file's
        # digest, not of its re-derivation); the kept set is bound to the flags because compare_exclusions
        # requires the recompute's re-derivation of that file to agree (exclusions_rederivation == agrees).
        c.exact("routing_id", f"run/{pack}/kept_units/exclusions_sha256", get(records.get(pack), "exclusions_sha256"),
                get(ours, "inputs", PACKS[pack], "exclusions_sha256"))
        # A4 (RC-CMP-9): the record's own window, against the registered window its file name carries.
        c.exact("routing_id", f"run/{pack}/kept_units/pack", get(records.get(pack), "pack"), pack)
    c.excluded.extend(reference_members(members, registry))
    selected = selected_runs(members, lambda key: registry.role(*key) not in REFERENCE_FAMILIES)
    for (pack, rid), name, _, _ in c.pairs("run/", rereduced_names(custody), universe, selected):
        l9 = custody.read(name) if name else {}
        mine = get(members, PACKS[pack], rid, "E_j", default={})
        for phase in ("prefill", "decode"):
            c.numeric("run_phase_energy_j", pack + "/" + rid + "/" + phase,
                      get(l9, "phase_energy_j", phase), get(mine, phase))
        c.numeric("run_phase_energy_j", pack + "/" + rid + "/request", get(l9, "gross_energy_j"), get(mine, "request"))


def step_2_universe(custody):
    """G7: the science runs L9's step 2 re-reduces, per window, and each window's kept-units record.

    The runs are the run ids of every kept unit of L9's kept-units record (dry_run.kept_bundles reads
    exactly these): L9's registered step-2 selection, read as data. A run it keeps that the window's
    sealed plan tree registers as a reference or diagnostic member refuses. A window without the
    record has no universe; its exclusions_sha256 row is then DISAGREE.

    NEEDS_RULING (RC-CMP-7): no sealed source alone fixes the kept set (it depends on the window's
    exclusions), and the plan tree's science/* list is not required to contain each kept run.
    """
    universe, records = {}, {}
    for pack in PACKS:
        record = custody.one(KEPT_UNITS % pack)
        records[pack] = record
        cells = get(record, "cells", default={})
        for name, cell in (cells.items() if isinstance(cells, dict) else ()):
            strata = get(cell, "kept", default={})
            for units in (strata.values() if isinstance(strata, dict) else ()):
                for unit in units if isinstance(units, list) else ():
                    # A4 (RC-CMP-9): a kept unit names the cell that keeps it (kept_units.KeptUnits.to_record).
                    if not isinstance(unit, dict) or unit.get("cell_id") != name:
                        raise Refusal("kept_units_identity_mismatch:" + pack)
                    for rid in get(unit, "run_ids", default=[]) or []:
                        if not isinstance(rid, str) or custody.registry.role(pack, rid) not in (None, "science"):
                            raise Refusal("kept_units_member_not_science:" + pack)
                        universe[(pack, rid)] = rid
    return universe, records


def reference_members(members, registry):
    """G7: the recompute's members whose registered role is a NEG-8 reference, each with its family."""
    return [{"family": "run_phase_energy_j", "pack": pack, "run_id": rid, "role": registry.role(pack, rid),
             "selected": isinstance(member, dict) and member.get("selected", True) is True,
             "reason": "compared_in:" + REFERENCE_FAMILIES[registry.role(pack, rid)]}
            for pack, PACK in PACKS.items() for rid, member in sorted((get(members, PACK) or {}).items())
            if registry.role(pack, rid) in REFERENCE_FAMILIES]


def rereduced_names(custody):
    named = {}
    for name in custody.names(r"rereduced/(alpha|beta|gamma)/[^/]+\.rereduced\.json"):
        pack, file = name.split("/")[1:]
        named[(pack, file[:-len(".rereduced.json")])] = name
    return named


def selected_runs(members, keep=lambda key: True):
    """The recompute's selected members (a member detail without the selected field counts as selected)."""
    return {(pack, rid): m for pack, PACK in PACKS.items() for rid, m in (get(members, PACK) or {}).items()
            if isinstance(m, dict) and m.get("selected", True) is True and keep((pack, rid))}


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


def p42_word(cells, registry, where):
    """L9's p42 status from its registered p42 cells: the registered exit when none is extractable; None when L9 lists none."""
    cells = [cell for cell in cells if isinstance(cell, dict)
             and registry.lookup(cell.get("cell_id"), ("extraction", "reported"), where)["p42"]]
    if not cells:
        return None
    return "expected_unresolvable" if all(cell.get("extractable") is False for cell in cells) else "extractable"


def p42_family(registry, pack):
    """The recompute's p42 cell id of a window (the registered p42 reported cell's condition family)."""
    found = registry.families(pack, True)
    return found.pop() if len(found) == 1 else None


def compare_floors(c, custody, ours):
    registry = custody.registry
    for pack in ("alpha", "beta"):
        report = custody.one(r"mint/[0-9a-f]{64}-extraction-" + pack + r"\.json")
        cells = (report or {}).get("cells", [])
        cells = cells if isinstance(cells, list) else []
        where = "extraction_cell:" + pack
        # Registered p42 exit: the p42 floor cells are not extractable (step 4 p42_floor_cells_only).
        c.exact("p42_status", pack + "/extraction/p42", p42_word(cells, registry, where),
                get(ours, "p42", p42_family(registry, pack), "status"))
        # Each cell by its registered id (G3): the spec's window, target phase and kind, never its spelling.
        l9_cells = keyed(cells, lambda cell: floor_key(registry.lookup(cell.get("cell_id"), ("extraction",), where, pack)),
                         "extraction_cell", lambda cell: not registry.lookup(cell.get("cell_id"), ("extraction",), where, pack)["p42"])
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


def floor_key(entry):
    """A registered extraction cell -> the recompute's floor key (model/phase/form)."""
    return f"{entry['model']}/{entry['phase']}/{entry['form']}"


def extraction_key(registry, cid):
    """A printed extraction cell id -> the recompute's floor key, or None when no extraction cell is registered so."""
    entry = registry.entry(cid, "extraction")
    return floor_key(entry) if entry else None


def cell_key(entry):
    """A registered aggregate floor or reported cell -> the recompute's cell key (model/phase)."""
    return f"{entry['model']}/{entry['phase']}"


# F3: the ratio table's registered numerator fields (run_d165_closeout_from_custody.build_ratio_table), read
# literally: the independent ratio R and the common-mode ratio R_cm.
NUMERATOR_FIELDS = {"corner_widened_unguarded_floor_j": "", "common_mode_corner_widened_unguarded_floor_j": "/common_mode"}


def ratio_label(row, registry):
    entry = registry.lookup(row.get("cell_id"), ("floor",), "ratio")
    field = row.get("numerator_field")
    suffix = NUMERATOR_FIELDS.get(field) if isinstance(field, str) else None
    # An unregistered numerator field is no ratio: its row keys on nothing the recompute holds (DISAGREE).
    return f"{cell_key(entry)}/{row.get('component')}" + (suffix if suffix is not None else "/unregistered_numerator")


def our_ratios(ours):
    mine = dict(items(get(ours, "dominance", "ratios")))
    mine.update({key + "/comparative/common_mode": item for key, item in items(get(ours, "dominance", "common_mode")).items()})
    return mine


def compare_aggregate(c, custody, ours):
    registry = custody.registry
    floor = custody.one(r"mint/[0-9a-f]{64}-aggregate-floor\.json")
    l9_cells = keyed((floor or {}).get("cells", []),
                     lambda cell: cell_key(registry.lookup(cell.get("cell_id"), ("floor",), "aggregate_cell")), "aggregate_cell")
    for key, cell, mine in c.pairs("aggregate/", l9_cells, items(ours.get("floor_cells"))):
        cell, mine = cell or {}, mine or {}
        for field in ("floor_abs_j", "floor_cmp_j", "floor_gate_j"):
            c.numeric("floor_gate_j", key + "/" + field, cell.get(field), mine.get(field))
    if floor is None:
        c.numeric("floor_gate_j", "aggregate_floor", None, None)
    closeout = custody.one(r"finalized/outputs/closeout\.json")
    ratios = custody.one(r"finalized/outputs/closeout\.ratio-table\.json")
    c.exact("dominance_branch", "branch", get(closeout, "branch"), get(ours, "dominance", "branch"))
    # F2: the licensed word follows the branch by registration (dominance_closeout: licensed iff branch A).
    branch = get(ours, "dominance", "branch")
    c.exact("dominance_branch", "dominance_sentence_licensed", get(closeout, "dominance_sentence_licensed"),
            branch == "A" if branch in ("A", "B") else None)
    l9_rows, mine_rows = keyed(get(ratios, "ratios", default=[]), lambda row: ratio_label(row, registry), "ratio"), our_ratios(ours)
    if not l9_rows and not mine_rows:
        c.numeric("dominance_ratio", "ratio/none", None, None)
    # Ratio rows have their own key prefix: a ratio's n is not its floor cell's n (S3, Opus N2).
    for label, row, mine in c.pairs("ratio/", l9_rows, mine_rows):
        row, mine, common = row or {}, mine or {}, label.endswith("/common_mode")
        key = "ratio/" + label
        c.numeric("dominance_ratio", key + "/ratio", row.get("ratio"), mine.get("R_cm" if common else "R"))
        # F2: the closeout's status word; the recompute's ratio is complete when it is a finite number.
        c.exact("outcome_word", key + "/status", row.get("status"),
                "complete" if finite(mine.get("R_cm" if common else "R")) else None)
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


def contrast_floor_part(cells, contrast, field):
    """A contrast's floor_abs_j or floor_cmp_j: the larger of its two models' cells (max, never sum)."""
    if contrast is None:
        return None
    values = [get(cells, model + "/" + contrast["phase"], field) for model in MODELS.values()]
    return max(values) if all(finite(v) for v in values) else None


def loo_key(registry, cid, block_id):
    """F3: an omitted block id -> the recompute's block key (b03), only as the contrast's registered block id
    (analysis_manifest_v3 contrasts[*].block_ids, in order); any other spelling has no key (None)."""
    return registry.block(cid, block_id)


def block_key(number):
    """A block number (the recompute's int, or L9's printed string) -> b03."""
    number = str(number)
    return "b%02d" % int(number) if number.isdigit() else None


def kept_blocks(blocks):
    return sorted(b["block_id"] for b in blocks if b.get("included") is True) if isinstance(blocks, list) else None


# The recompute's arms (S2): arm A is the a1/a2 runs on ALPHA's model, arm B the b runs on
# BETA's, in the registered floor_selector order [A, B].
ARMS = {0: "alpha", 1: "beta"}


def compare_arms(c, ours, cid, floor, registry):
    """A v3 floor's arm gates and resolutions, by registered position against the recompute's arm (S2).

    The arm a gate or resolution belongs to is its position, never its printed condition;
    the printed arm_id, condition_family_id and source cell ids are compared as routing_id rows
    against the registered contrast's condition (G3) and aggregate floor cell.
    """
    contrast = registry.entry(cid, "contrast")
    if contrast is None:
        return
    cells, phase = ours.get("floor_cells"), contrast["phase"]
    # F2 (RC-CMP-9): both row sets are built from ARMS whatever the floor prints (a v3 contrast always carries
    # exactly two gates and its resolutions; artifact.py v3 floor), so a floor without them is DISAGREE.
    for index, gate, pack in c.pairs(f"contrast/{cid}/arm/", positions(floor.get("arm_gates")), ARMS):
        gate = gate if isinstance(gate, dict) else {}
        c.exact("routing_id", f"contrast/{cid}/arm/{index}/arm_id", gate.get("arm_id"),
                {"alpha": "A", "beta": "B"}.get(pack))
        c.exact("routing_id", f"contrast/{cid}/arm/{index}/condition_family_id", gate.get("condition_family_id"),
                contrast["conditions"][index] if pack else None)
        c.numeric("floor_gate_j", f"{cid}/arm/{index}/floor_gate_j", gate.get("floor_gate_j"),
                  get(cells, f"{MODELS.get(pack)}/{phase}", "floor_gate_j"))
    for index, resolution, pack in c.pairs(f"contrast/{cid}/resolution/", positions(floor.get("resolutions")), ARMS):
        resolution = resolution if isinstance(resolution, dict) else {}
        cell = f"{MODELS.get(pack)}/{phase}"
        for field in ("floor_abs_j", "floor_cmp_j", "floor_gate_j"):
            c.numeric("floor_gate_j", f"{cid}/resolution/{index}/{field}", resolution.get(field), get(cells, cell, field))
        # RC-CMP-8: the transfer rule each resolution applies, as the floor_selector registers it.
        c.exact("routing_id", f"contrast/{cid}/resolution/{index}/transport_rule_id", resolution.get("transport_rule_id"),
                contrast.get("floor_rules", {}).get("transport_rule_id") if pack else None)
        # RC-CMP-9 A4: the arm's transport group, as the manifest registers it for the arm's condition family.
        c.exact("routing_id", f"contrast/{cid}/resolution/{index}/transport_group_id",
                resolution.get("transport_group_id"), contrast["transport_groups"][index] if pack else None)
        sources = positions(resolution.get("source_cell_ids"))
        for number, source, own in c.pairs(f"contrast/{cid}/resolution/{index}/source/", sources, {0: cell}):
            # The printed source id, looked up literally (G3): an unregistered id is no cell.
            entry = registry.entry(source, "floor")
            c.exact("routing_id", f"contrast/{cid}/resolution/{index}/source_cell_ids/{number}",
                    cell_key(entry) if entry else None, own, raw=source)


def registered_floor_keys(contrast, registry):
    """A contrast's registered floor cells [A, B] -> {position: the recompute's cell key}."""
    return {index: cell_key(registry.tables["floor"][cid]) for index, cid in enumerate((contrast or {}).get("floor_cells", ()))}


def printed_block_ids(blocks):
    """The block ids a verdict's bundle_blocks prints (sorted), or None when it prints no block list."""
    return sorted(map(str, (b.get("block_id") if isinstance(b, dict) else b for b in blocks))) if isinstance(blocks, list) else None


def terms_total(terms):
    """The sum of a verdict's deterministic bound terms, or None unless each term has exactly the engine's keys
    (artifact.py _DETERMINISTIC_TERM_KEYS) and a finite bound."""
    if not isinstance(terms, list) or not terms or not all(
            isinstance(t, dict) and set(t) == set(ENGINE_KEYS["deterministic_term"]) and finite(t["bound"]) for t in terms):
        return None
    return math.fsum(t["bound"] for t in terms)


def verdict_block_ids(row):
    """A verdict's kept and removed block ids in planned order (results_fill_adapter: kept_block_ids, removed_block_ids)."""
    blocks = get(row, "bundle_blocks", default={}) or {}
    included = {b.get("block_id") for b in listed(blocks.get("blocks")) if isinstance(b, dict) and b.get("included") is True}
    planned = listed(blocks.get("planned_block_ids"))
    return [bid for bid in planned if bid in included], [bid for bid in planned if bid not in included]


def registered_block_ids(registry, cid, mine):
    """The contrast's registered blocks in registered order that the recompute keeps, and those it leaves out."""
    kept = set(listed(mine.get("kept_quads"))) if isinstance(mine, dict) else set()
    blocks = registry.blocks.get(cid, ())
    return [bid for bid in blocks if bid in kept], [bid for bid in blocks if bid not in kept]


def compare_floor_ids(c, scope, printed, contrast, registry):
    """A3 (RC-CMP-9): a contrast's printed floor cell ids (floor_row_ids, the fill's floor_source_cell_ids, the
    sensitivity record's floor_cell_ids), by position against the registered source cells [A, B]."""
    for index, cell, mine in c.pairs(scope + "_position/", positions(printed), registered_floor_keys(contrast, registry)):
        entry = registry.entry(cell, "floor")
        c.exact("routing_id", f"{scope}/{index}", cell_key(entry) if entry else None, mine, raw=cell)


def compare_contrasts(c, custody, ours):
    registry = custody.registry
    verdicts = custody.one(r"outputs/[0-9a-f]{64}-claim-verdicts\.json")
    l9_rows = keyed(get(verdicts, "contrasts", default=[]),
                    lambda row: registry.registered(row.get("contrast_id"), ("contrast",), "contrast"), "contrast")
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
        # F1 (RC-CMP-9): the printed terms (each with the engine's exact term keys) sum to the compared total.
        c.numeric("contrast_j", f"{cid}/D_terms_j", terms_total(bounds.get("terms")), mine.get("D_j"))
        for side, a, b in sides(bounds.get("decision_interval"), mine.get("decision_interval_j")):
            c.numeric("contrast_j", f"{cid}/decision_interval_j/{side}", a, b)
        c.numeric("floor_gate_j", f"{cid}/active_floor_j", get(row, "floor", "active_floor_j"), mine.get("floor_gate_j"))
        for field in ("floor_abs_j", "floor_cmp_j"):
            c.numeric("floor_gate_j", f"{cid}/{field}", get(row, "floor", field),
                      contrast_floor_part(ours.get("floor_cells"), registry.entry(cid, "contrast"), field))
        compare_arms(c, ours, cid, row.get("floor") if isinstance(row.get("floor"), dict) else {}, registry)
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
        # F1 (RC-CMP-8): the engine fixes ready iff the ceiling permits L2 (artifact.py claim_ready_for_l2_l3).
        ceiling = mine.get("ceiling")
        c.exact("outcome_word", f"{cid}/claim_ready", evaluation.get("claim_ready_for_l2_l3"),
                ceiling in READY_CEILINGS if isinstance(ceiling, str) else None)
        # F2: the contrast-definition words, against the sealed manifest's registration.
        entry = registry.entry(cid, "contrast") or {}
        c.exact("outcome_word", f"{cid}/claim_role", row.get("claim_role"), entry.get("role"))
        c.exact("outcome_word", f"{cid}/hypothesized_direction", row.get("hypothesized_direction"), entry.get("direction"))
        c.exact("outcome_word", f"{cid}/confirmatory_status", get(row, "sampling", "confirmatory_status"),
                entry.get("confirmatory"))
        c.exact("outcome_word", f"{cid}/loo_status", get(row, "loo", "status"),
                loo_status(mine.get("n"), registry.blocks.get(cid)) if mine else None)
        # A2 (RC-CMP-9): each side's leave-one-out rows number its kept n (one row per kept block) when the
        # recompute's rule computes them (LOO_MIN kept quads); a row dropped from both sides is DISAGREE here too.
        n = mine.get("n")
        if finite(n) and n >= LOO_MIN:
            c.numeric("count", f"{cid}/loo/l9_rows", len(listed(get(row, "loo", "rows"))) if row else None, n)
            c.numeric("count", f"{cid}/loo/recompute_rows", est.get("n"),
                      len(mine["loo"]) if isinstance(mine.get("loo"), list) else None)
        # A3: the floor source cells, against the contrast's registered cells; A4: the bundle's block ids.
        compare_floor_ids(c, f"contrast/{cid}/floor_row_ids", get(row, "floor", "floor_row_ids"),
                          registry.entry(cid, "contrast"), registry)
        blocks = get(row, "bundle_blocks", default={}) or {}
        c.exact("routing_id", f"contrast/{cid}/planned_block_ids", blocks.get("planned_block_ids"),
                list(registry.blocks[cid]) if cid in registry.blocks else None)
        c.exact("routing_id", f"contrast/{cid}/bundle_block_ids", printed_block_ids(blocks.get("blocks")),
                sorted(registry.blocks[cid]) if cid in registry.blocks else None)
        # A4: the kept and removed block ids the fill copies (planned order), by position against the registered
        # blocks in registered order that the recompute keeps or leaves out.
        kept_l9, removed_l9 = verdict_block_ids(row)
        kept_own, removed_own = registered_block_ids(registry, cid, mine)
        for index, block, own in c.pairs(f"contrast/{cid}/kept_block_ids_position/", positions(kept_l9), positions(kept_own)):
            c.exact("routing_id", f"contrast/{cid}/kept_block_ids/{index}", block, own)
        for index, block, own in c.pairs(f"contrast/{cid}/removed_block_ids_position/", positions(removed_l9),
                                         positions(removed_own)):
            c.exact("routing_id", f"contrast/{cid}/removed_block_ids/{index}", block, own)
        # RC-CMP-8: the remaining registered words that assert a direction or relation (which condition is A and
        # B, the orientation of the difference, the quantity, the estimator, how the floor combines and transfers).
        definition = entry.get("definition") or {}
        for field, printed in (("condition_a_id", get(row, "conditions", "condition_a_id")),
                               ("condition_b_id", get(row, "conditions", "condition_b_id")),
                               ("difference_orientation", get(row, "conditions", "difference_orientation")),
                               ("name", get(row, "metric", "name")), ("metric_tag", get(row, "metric", "metric_tag")),
                               ("window_class", get(row, "metric", "window_class"))):
            c.exact("routing_id", f"{cid}/definition/{field}", printed, definition.get(field))
        c.exact("routing_id", f"{cid}/estimator_name", est.get("name"), entry.get("estimator"))
        rules = entry.get("floor_rules") or {}
        floor_row = row.get("floor") if isinstance(row.get("floor"), dict) else {}
        c.exact("routing_id", f"{cid}/floor/claim_floor_rule", floor_row.get("claim_floor_rule"), rules.get("claim_floor_rule"))
        # The v3 claim floor's aggregation word is fixed by the engine (artifact.py: v3 floor requires max_never_sum).
        c.exact("routing_id", f"{cid}/floor/aggregation", floor_row.get("aggregation"),
                V3_AGGREGATION if rules.get("claim_floor_rule") else None)
        l9_p[cid], our_p[cid] = multiplicity.get("raw_p"), mine.get("p")
        loo_l9 = keyed(get(row, "loo", "rows", default=[]), lambda r: loo_key(registry, cid, r.get("omitted_block_id")),
                       "loo_row")
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
            # F2: the row's influence triggers, re-derived from the recompute's full and leave-one-out values.
            triggers = loo_triggers(mine, mine_loo) if mine_loo else None
            c.exact("outcome_word", key + "/influence_triggers", l9_loo.get("influence_triggers"), triggers)
            for index, word, own in c.pairs(key + "/influence_triggers/", positions(l9_loo.get("influence_triggers")),
                                            positions(triggers)):
                c.exact("outcome_word", f"{key}/influence_triggers/{index}", word, own)
    c.exact("holm_order", "raw_p_order", holm_order(l9_p), holm_order(our_p))


# The v3 claim floor's aggregation word (analysis_engine/artifact.py: a v3 floor's aggregation must be max_never_sum).
V3_AGGREGATION = "max_never_sum"
# The ceilings that make a contrast claim-ready (analysis_engine/artifact.py: ready iff the ceiling is L2, L3 or L4).
READY_CEILINGS = ("L2", "L3", "L4")
# The engine reports leave-one-out not_required above this many complete observations (analysis_engine _contrast_row).
LOO_REQUIRED_MAX = 10


def loo_status(n, blocks):
    """F2: L9's leave-one-out status word. The engine prints not_required only above LOO_REQUIRED_MAX complete
    observations; the registration plans len(block_ids) blocks and forbids replacements, so with at most
    LOO_REQUIRED_MAX registered blocks the engine computes a row for each kept block of a complete contrast
    (analysis_engine _loo_family; block 5's kept quads make every contrast complete): the word is complete
    when the kept n is at least one, else not_run. A2 (RC-CMP-9): the word follows the kept n (the recompute's,
    compared with L9's by the n row), never how many rows either side printed. More registered blocks than
    LOO_REQUIRED_MAX, or no kept n, leave the word undetermined here (None: DISAGREE)."""
    if not finite(n) or isinstance(n, bool) or blocks is None or len(blocks) > LOO_REQUIRED_MAX:
        return None
    return "complete" if n >= 1 else "not_run"


def sign(value):
    return (value > 0) - (value < 0)


def loo_triggers(full, row):
    """F2: a leave-one-out row's influence triggers in the engine's order (analysis_engine/sensitivity.py
    influence_triggers), from the recompute's full contrast and its row; None when a term is missing."""
    floor, estimate, loo = full.get("floor_gate_j"), full.get("dbar_j"), row.get("dbar_j")
    terms = (full.get("holm_reject"), row.get("holm_reject"), full.get("outcome"), row.get("outcome"), row.get("above_floor"))
    if not (finite(floor) and finite(estimate) and finite(loo)) or any(term is None for term in terms):
        return None
    triggers = []
    if sign(estimate) != sign(loo):
        triggers.append("estimate_sign")
    if (abs(estimate) > floor) != row["above_floor"]:
        triggers.append("floor_status")
    if bool(full["holm_reject"]) != bool(row["holm_reject"]):
        triggers.append("adjusted_rejection")
    if full["outcome"] != row["outcome"]:
        triggers.append("outcome")
    if abs(loo - estimate) > 0.25 * floor:
        triggers.append("estimate_magnitude")
    return triggers


def compare_campaigns(c, custody, ours):
    """F1 (RC-CMP-8): each floor window's claim_usable word in the fill, against the recompute's
    inputs.<PACK>.claim_usable (the stored derived/exclusions.json word, which compare_exclusions binds to its
    re-derivation). L9 analyses only claim-usable windows (b5_analysis/archive.py attempt_not_claim_usable)."""
    fill = custody.one(STEP11_SOURCES[0][1])
    if fill is None:
        return
    for pack in ("alpha", "beta"):
        c.exact("outcome_word", f"campaigns/{pack}/claim_usable", get(fill, "campaigns", pack, "claim_usable"),
                get(ours, "inputs", PACKS[pack], "claim_usable"))


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


def unit_list(kept):
    return sorted((u.get("stratum"), u.get("unit_id")) for u in kept) if isinstance(kept, list) else None


def our_units(kept):
    return sorted((s, u) for s, units in (kept or {}).items() for u in units) or None


def compare_reported(c, custody, ours):
    """Step 10: each pack's reported cells (estimator 1) against the recompute's reported_cells."""
    registry = custody.registry
    for pack in ("alpha", "beta"):
        projection = custody.one(r"outputs/[0-9a-f]{64}-projection-" + pack + r"\.json")
        if projection is None:
            c.numeric("reported_cell_j", pack + "/projection", None, None)
        where = "projection_cell:" + pack
        # Each cell by its registered id (G3): the recompute's cell id is the cell's registered condition family.
        l9_cells = keyed(get(projection, "cells", default=[]),
                         lambda cell: registry.lookup(cell.get("cell_id"), ("reported",), where, pack)["family"], "projection_cell")
        mine_cells = items(ours.get("reported_cells"), lambda key, _: key in registry.families(pack, False))
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
        # The registered p42 exit: L9's projection lists its refused p42 cells. F4 (RC-CMP-9): the row is built for
        # every floor window; a projection without its refused p42 cells is DISAGREE (None).
        refused = refused_p42(get(projection, "refused_cells", default=[]), registry, where)
        c.exact("p42_status", pack + "/projection/p42", refused, get(ours, "p42", p42_family(registry, pack), "status"))


def refused_p42(cells, registry, where):
    return (p42_word([dict(cell, extractable=False) for cell in cells if isinstance(cell, dict)], registry, where)
            if isinstance(cells, list) else None)


def any_finite(values):
    return any(finite(v) for v in values.values())


def labelled(custody, pattern, label):
    return next((r for r in (custody.read(n) for n in custody.names(pattern)) if get(r, "label") == label), None)


def by_pack(windows):
    return {pack: window for pack, PACK in PACKS.items() for window in [get(windows, PACK)] if window is not None}


def sensitivity_reported(cells, registry):
    def key(cell):
        entry = registry.lookup(cell.get("cell_id"), ("reported",), "sensitivity_reported_cell", cell.get("pack"))
        return entry["pack"], entry["family"]
    return keyed(cells, key, "sensitivity_reported_cell")


def our_sensitivity_reported(line, ours, registry):
    """The recompute's sensitivity cells, and its p42 cells (L9 lists them as refused cells), by registered window."""
    cells = {(pack, cid): item for pack in ("alpha", "beta")
             for cid, item in items(line.get("reported_cells"), lambda key, _: key in registry.families(pack, False)).items()}
    cells.update({(pack, cid): item for pack in ("alpha", "beta")
                  for cid, item in (ours.get("p42") or {}).items() if cid in registry.families(pack, True)})
    return cells


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
        b_op, b_sens = get(ours, "windows", PACKS.get(pack, ""), "b_op_s"), get(line, "windows", PACKS.get(pack, ""), "b_sens_s")
        c.numeric("b_op_s", f"sensitivity/windows/{pack}/b_op_s", get(record, "windows", pack, "b_op_s"), b_op)
        c.numeric("b_op_s", f"sensitivity/windows/{pack}/b_sens_s", get(record, "windows", pack, "b_sens_s"), b_sens)
        # F2: "values differ from primary" when the sensitivity bound is not the operative one.
        c.exact("outcome_word", f"sensitivity/windows/{pack}/widened", get(record, "windows", pack, "widened"),
                b_sens != b_op if finite(b_sens) and finite(b_op) else None)
    registry = custody.registry
    cells = keyed(record.get("floor_cells", []), lambda cell: cell_key(registry.lookup(
        cell.get("cell_id"), ("floor",), "sensitivity_floor_cell", cell.get("pack"))), "sensitivity_floor_cell")
    for key, cell, _ in c.pairs("sensitivity/floor_cells/", cells, items(line.get("floor_cells"))):
        cell, mine = cell or {}, get(line, "floor_cells", key, default={}) or {}
        for field in ("floor_abs_j", "floor_cmp_j", "floor_gate_j"):
            c.numeric("floor_gate_j", f"sensitivity/{key}/{field}", get(cell, "sensitivity", field), mine.get(field))
        c.numeric("floor_j", f"sensitivity/{key}/allowance_j", get(cell, "sensitivity", "allowance_j"),
                  get(line, "floors", key + "/absolute", "allowance_j"))
        before = dict(get(ours, "floor_cells", key, default={}) or {},
                      allowance_j=get(ours, "floors", key + "/absolute", "allowance_j"))
        after = dict(mine, allowance_j=get(line, "floors", key + "/absolute", "allowance_j"))
        c.exact("outcome_word", f"sensitivity/{key}/equals_primary", cell.get("equals_primary"),
                relation(before, after, FLOOR_KEYS + ("allowance_j",), lambda a, b: a == b))
        c.exact("outcome_word", f"sensitivity/{key}/not_below_primary", cell.get("not_below_primary"),
                relation(before, after, FLOOR_KEYS, lambda a, b: b >= a))
        # F1 (RC-CMP-9): the record's own primary values, read directly (not only through the disclosure's copy).
        for field in FLOOR_KEYS:
            c.numeric("floor_gate_j", f"sensitivity/primary/{key}/{field}", get(cell, "primary", field), before.get(field))
        c.numeric("floor_j", f"sensitivity/primary/{key}/allowance_j", get(cell, "primary", "allowance_j"),
                  before.get("allowance_j"))
    rows = keyed(record.get("contrasts", []),
                 lambda row: registry.registered(row.get("contrast_id"), ("contrast",), "sensitivity_contrast"),
                 "sensitivity_contrast")
    for cid, row, _ in c.pairs("sensitivity/contrasts/", rows, items(line.get("contrasts"))):
        row, mine = row or {}, get(line, "contrasts", cid, default={}) or {}
        c.numeric("contrast_j", f"sensitivity/{cid}/D_j", get(row, "sensitivity", "D_j"), mine.get("D_j"))
        c.numeric("floor_gate_j", f"sensitivity/{cid}/floor_gate_j", get(row, "sensitivity", "floor_gate_j"),
                  mine.get("floor_gate_j"))
        for field in ("floor_abs_j", "floor_cmp_j"):
            c.numeric("floor_gate_j", f"sensitivity/{cid}/{field}", get(row, "sensitivity", field),
                      contrast_floor_part(line.get("floor_cells"), registry.entry(cid, "contrast"), field))
        c.exact("outcome_word", f"sensitivity/{cid}/outcome", get(row, "sensitivity", "outcome"), mine.get("outcome"))
        c.exact("outcome_word", f"sensitivity/{cid}/outcome_equals_primary", row.get("outcome_equals_primary"),
                mine.get("outcome_equals_primary"))
        # F2: true by construction (sensitivity.py refuses sensitivity_changed_bound_independent_value otherwise).
        c.exact("outcome_word", f"sensitivity/{cid}/bound_independent_values_equal_primary",
                row.get("bound_independent_values_equal_primary"), True)
        entry, primary = registry.entry(cid, "contrast"), get(ours, "contrasts", cid, default={}) or {}
        before = {field: contrast_floor_part(ours.get("floor_cells"), entry, field) for field in ("floor_abs_j", "floor_cmp_j")}
        before.update(floor_gate_j=primary.get("floor_gate_j"), D_j=primary.get("D_j"))
        after = {field: contrast_floor_part(line.get("floor_cells"), entry, field) for field in ("floor_abs_j", "floor_cmp_j")}
        after.update(floor_gate_j=mine.get("floor_gate_j"), D_j=mine.get("D_j"))
        c.exact("outcome_word", f"sensitivity/{cid}/not_below_primary", row.get("not_below_primary"),
                relation(before, after, FLOOR_KEYS + ("D_j",), lambda a, b: b >= a))
        # F1 (RC-CMP-9): the record's own primary values; A3: its floor cell ids against the registered cells.
        for field in FLOOR_KEYS:
            c.numeric("floor_gate_j", f"sensitivity/primary/{cid}/{field}", get(row, "primary", field), before.get(field))
        c.numeric("contrast_j", f"sensitivity/primary/{cid}/D_j", get(row, "primary", "D_j"), before.get("D_j"))
        c.exact("outcome_word", f"sensitivity/primary/{cid}/outcome", get(row, "primary", "outcome"), primary.get("outcome"))
        compare_floor_ids(c, f"sensitivity/{cid}/floor_cell_ids", row.get("floor_cell_ids"), entry, registry)
    reported = sensitivity_reported(record.get("reported_cells", []), registry)
    for (pack, cid), cell, _ in c.pairs("sensitivity/reported_cells/", reported, our_sensitivity_reported(line, ours, registry)):
        cell = cell or {}
        mine = get(line, "reported_cells", cid, default={}) or {}
        sens = cell.get("sensitivity") or {}
        if cid in registry.families(pack, True):
            # The registered p42 exit: no reported value on either side; compared as a status, not as numbers.
            l9 = "expected_unresolvable" if not any_finite(sens) else "computed"
            own = get(ours, "p42", cid, "status")
            c.exact("p42_status", f"sensitivity/{pack}/{cid}", l9, own)
            # F2: the printed status and code words, against the registered exit's words (sensitivity.py).
            exit_words = P42_EXIT if own == "expected_unresolvable" else (own, None)
            c.exact("outcome_word", f"sensitivity/{pack}/{cid}/status", cell.get("status"), exit_words[0])
            c.exact("outcome_word", f"sensitivity/{pack}/{cid}/code", cell.get("code"), exit_words[1])
            continue
        c.exact("outcome_word", f"sensitivity/{pack}/{cid}/status", cell.get("status"),
                "computed" if mine.get("status") == "computed" else mine.get("status"))
        before, after = reported_values(get(ours, "reported_cells", cid, default={}) or {}), reported_values(mine)
        # F1 (RC-CMP-9): the record's own primary values, read directly.
        for field in REPORTED_VALUE_KEYS:
            c.numeric("reported_cell_j", f"sensitivity/primary/{pack}/{cid}/{field}", get(cell, "primary", field),
                      before.get(field))
        c.exact("outcome_word", f"sensitivity/{pack}/{cid}/equals_primary", cell.get("equals_primary"),
                relation(before, after, tuple(before), lambda a, b: a == b))
        c.exact("outcome_word", f"sensitivity/{pack}/{cid}/not_below_primary", cell.get("not_below_primary"),
                relation(before, after, ("attribution_floor_j",), lambda a, b: b >= a))
        # F2: true by construction (sensitivity.py refuses sensitivity_changed_bound_independent_value otherwise).
        c.exact("outcome_word", f"sensitivity/{pack}/{cid}/mean_and_half_width_equal_primary",
                cell.get("mean_and_half_width_equal_primary"), True)
        for field in ("mean_j", "lower_j", "upper_j"):
            c.numeric("reported_cell_j", f"sensitivity/{pack}/{cid}/{field}", sens.get(field), mine.get(field))
        c.numeric("reported_cell_j", f"sensitivity/{pack}/{cid}/h_j", sens.get("h_j"), get(mine, "interval", "h_j"))
        c.numeric("reported_cell_j", f"sensitivity/{pack}/{cid}/B_j", sens.get("B_j"), get(mine, "interval", "B_j"))
        c.numeric("reported_cell_j", f"sensitivity/{pack}/{cid}/attribution_floor_j", sens.get("attribution_floor_j"),
                  get(mine, "attribution_floor", "value_j"))


# The registered p42 exit as L9's sensitivity record prints it (b5_analysis/sensitivity.py: a refused
# projection cell keeps its status and code); the recompute's word for it is expected_unresolvable.
P42_EXIT = ("refused", "p42_expected_unresolvable")
FLOOR_KEYS = ("floor_abs_j", "floor_cmp_j", "floor_gate_j")


def reported_values(cell):
    """A reported cell's six values in L9's sensitivity order (sensitivity._reported_values)."""
    return {"mean_j": cell.get("mean_j"), "h_j": get(cell, "interval", "h_j"), "B_j": get(cell, "interval", "B_j"),
            "lower_j": cell.get("lower_j"), "upper_j": cell.get("upper_j"),
            "attribution_floor_j": get(cell, "attribution_floor", "value_j")}


def relation(before, after, keys, test):
    """F2: a consistency word re-derived from the recompute's primary and sensitivity values (None if any is missing)."""
    pairs = [(before.get(key), after.get(key)) for key in keys]
    return all(test(a, b) for a, b in pairs) if all(finite(a) and finite(b) for a, b in pairs) else None


def pack_of_model(model):
    return next((p for p, m in MODELS.items() if m == model), None)


CELL_LINES, CONTRAST_LINES = ("cross_window", "battery_assist_cell", "reported_cell"), ("battery_assist_contrast", "magnitude_ratio",
                                                                       "magnitude_per_token", "loo_counts", "loo_magnitude")


def our_cell_lines(disclosures, registry, reported=None):
    """The recompute's cell lines by (line, window, registered cell id): cross-window lines are keyed model/phase."""
    lines = {("cross_window", pack, registry.reported_family(pack, phase)): item
             for key, item in items(disclosures.get("cross_window")).items()
             for model, _, phase in [key.partition("/")] for pack in [pack_of_model(model)] if pack}
    lines.update({("battery_assist_cell", pack, cid): item for cid, item in (disclosures.get("battery_assist") or {}).items()
                  for pack in ("alpha", "beta") if cid in registry.families(pack, False)})
    # F2 (RC-CMP-8): L9 prints a reported_cell line for each computed projection cell (disclosures.py).
    lines.update({("reported_cell", pack, cid): item for pack in ("alpha", "beta")
                  for cid, item in items(reported, lambda key, _: key in registry.families(pack, False)).items()})
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
    disclosures, registry = ours.get("disclosures") or {}, custody.registry
    # The gate (G2, G3) admitted only registered cell ids of the line's own window here.
    lines = keyed(record.get("cells", []),
                  lambda row: (row.get("line"), row.get("pack"), registry.entry(row.get("cell_id"), "reported")["family"]),
                  "disclosure_cell_line", lambda row: row.get("line") in CELL_LINES)
    for (kind, pack, cid), row, own in c.pairs("disclosure/cells/", lines,
                                               our_cell_lines(disclosures, registry, ours.get("reported_cells"))):
        row, key = row or {}, f"disclosure/{pack}/{cid}/{kind}"
        if kind == "reported_cell":
            # F2: the producer's word for a projection cell's own values is always computed (disclosures._cell_values).
            c.exact("outcome_word", key + "/status", row.get("status"), "computed" if own else None)
        elif kind == "cross_window":
            mine = get(disclosures, "cross_window", f"{MODELS.get(pack)}/{registry.phase_of_family(cid)}", default={}) or {}
            for field in ("F_j", "G_j", "delta_j", "h_F_j", "h_G_j"):
                c.numeric("reported_cell_j", key + "/" + field, row.get(field), mine.get(field))
            c.exact("outcome_word", key + "/agree", row.get("agree"), mine.get("agree"))
        else:
            mine = get(disclosures, "battery_assist", cid, default={}) or {}
            without = row.get("without") or {}
            # F2: the with-assist side is the primary cell, whose word is always computed (disclosures._cell_values).
            c.exact("outcome_word", key + "/primary/status", get(row, "primary", "status"), "computed" if own else None)
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
            # F2: the producer's status word is fixed by n (disclosures._paired_values).
            c.exact("outcome_word", key + "/status", row.get("status"), paired_status(mine.get("n")))
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
    # RC-CMP-8: each floor-composition line's allowance source word, against the recompute's NEG-8 source of the
    # line's window (disclosures.py reads it from the window's derived/neg8-allowance.json).
    compositions = keyed(record.get("floors", []), lambda row: extraction_key(registry, row.get("cell_id")),
                         "floor_composition_line", lambda row: row.get("line") == "floor_composition")
    mine_floors = items(ours.get("floors"), lambda key, _: pack_of_model(key.partition("/")[0]) is not None)
    for key, row, _ in c.pairs("disclosure/floors/floor_composition/", compositions, mine_floors):
        pack = pack_of_model(str(key).partition("/")[0])
        c.exact("outcome_word", f"disclosure/{key}/floor_composition/source", (row or {}).get("source"),
                get(ours, "windows", PACKS.get(pack, ""), "neg8", "source"))
    windows = record.get("window_lines") if isinstance(record.get("window_lines"), dict) else {}
    # F2: the window lines' claim words, against the recompute's own b_op and NEG-8 screen. F3 (RC-CMP-8): the
    # producer prints both lines for every registered window (disclosures._structure_lines), so each pairs per
    # registered pack and a window without its line is DISAGREE.
    claims = {pack: keyed(windows.get(pack), lambda row: row.get("line"), "window_claim_line",
                          lambda row: row.get("line") in WINDOW_CLAIM_LINES) for pack in PACKS}
    for word in WINDOW_CLAIM_LINES:
        printed = {pack: claims[pack][word] for pack in PACKS if word in claims[pack]}
        for pack, line, _ in c.pairs(f"disclosure/window_lines/{word}/", printed, dict.fromkeys(PACKS)):
            line, own = line or {}, get(ours, "windows", PACKS[pack], default={}) or {}
            if word == "below_screen_bound":
                b_op = own.get("b_op_s")
                c.exact("outcome_word", f"disclosure/{pack}/below_screen_bound/below", line.get("below"),
                        b_op < SCREEN_BOUND_S if finite(b_op) else None)
            else:
                c.exact("outcome_word", f"disclosure/{pack}/neg8_screen/decision", line.get("decision"),
                        get(own, "neg8", "screen_decision"))
    l9_windows = window_line_names(record.get("window_lines"))
    for pack, rows, neg8s in c.pairs("disclosure/window_lines/", l9_windows, our_neg8(ours)):
        neg8 = get(ours, "windows", PACKS.get(pack, ""), "neg8", default={}) or {}
        for name, row, _ in c.pairs(f"disclosure/window_lines/{pack}/", rows or {}, neg8s or {}):
            row, key = row or {}, f"disclosure/{pack}/{name}"
            if name == "neg8_allowance":
                # RC-CMP-8: the allowance's source word (survivor re-screen or stored bound), the recompute's copy.
                c.exact("outcome_word", key + "/source", row.get("source"), neg8.get("source"))
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


WINDOW_CLAIM_LINES = ("below_screen_bound", "neg8_screen")


def paired_status(n):
    """A descriptive contrast line's status word from its quad count (disclosures._paired_values)."""
    if not finite(n) or isinstance(n, float):
        return None
    return "not_computable" if n == 0 else "one_quad" if n == 1 else "computed"


SHORT_MODELS = {"Qwen3-1.7B-4bit": "qwen3-1p7b", "Qwen3-8B-4bit": "qwen3-8b"}
# The registered screen bound of the below_screen_bound line (b5_analysis/disclosures.py SCREEN_BOUND_S).
SCREEN_BOUND_S = 0.03646286164497997


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
            # F2: the member line's words, against the recompute's own member (machine_lines' plausibility rule).
            c.exact("outcome_word", key + "/plausible", row.get("plausible"), plausible_rho(own) if own else None)
            c.exact("battery_term", key + "/battery_term_available", row.get("battery_term_available"),
                    own.get("battery_term_available"))
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
            records[pack] = loads(raw, flags, "harvest_meter:" + pack, duplicate="harvest_meter_duplicate_key")
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


# Step-11 coverage (RC-CMP-3 X1, X6; RC-CMP-5 S1, S2; RC-CMP-6 G5). Each leaf of the fill input and
# the disclosure record has a path like fill:gamma/contrasts/*/estimate: a list item becomes *,
# or its line word when the item is a disclosure line (window_lines/alpha/machine_member/rho).
# A leaf is numeric-class when it is a number, null, or was read from a NaN or Infinity; a string
# spelling a number is numeric-class too, except under the text and identity rules.
# A rule is (pattern, target) or (pattern, family, key). The first rule that matches wins:
# - (pattern, family, key): the leaf copies the comparison row (family, key). The key
#   template is filled from the pattern's named groups, the identity fields of the objects
#   that own them (its contrast, cell, run or line; G2) and list positions, never from an
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
# The bytes after the canonical JSON: render_results_fill_input adds a newline, canonical_json_bytes none.
STEP11_TAILS = {"fill": b"\n", "disclosure": b""}
UNCOVERED, NAMED, NULL_NAMED = "uncovered:", "uncovered-by-name:", "uncovered-null-by-name:"
TEXT = UNCOVERED + "rendered text and labels; checked against issued values by the post-release reader (synthesis 2(b)(iii))"
# RC-CMP-8: restricted is a disclosure control (it publishes or withholds a line), not a claim about a value; the
# recompute has no release policy to re-derive it from. Listed for the lead (RC-CMP7-OPUS-REV finding 2).
DISCLOSURE_CONTROL = (UNCOVERED + "disclosure control: whether the line is withheld before release; asserts no claim, "
                      "direction, status or relation the recompute or the registry determines")
IDENTITY = UNCOVERED + "identity, label or provenance (ids, digests, pins, stage names); bound by L9's record, not a computed quantity"
IDENTITY_NUMBER = NAMED + "attempt numbers, positions and ledger sequences: identity bound by L9's record, not a computed quantity"
STRUCTURE = (UNCOVERED + "window structure the recompute does not re-derive (flag tallies, hazards, monitor, battery, "
             "ledger, tripwires); reader item 2(b)")
STRUCTURE_NUMBER = NAMED + "window and block structure counts and readings the recompute does not re-derive; reader item 2(b)"
DESCRIPTIVE_STATUS = (UNCOVERED + "a battery-assist cell's without-assist status word (computed, one_unit, not_computable): "
                      "the recompute's reported-cell status vocabulary has no registered mapping to it; its values are "
                      "compared where it prints them")
HARVEST_WORDS = (UNCOVERED + "the harvest's and the window index's own records (stored verdict, tripwires, attempts, "
                 "re-harvests), read by L9 as data; the recompute re-derives no such word (reader item 2(b))")
# The measurement keys disclosures._hazard_values keeps (numbers, booleans and status words of monitor readings).
HAZARD = (r"(current_ma|instant_amperage_ma|amperage_ma|temperature_centi_c|temperature_k|os_level|pressure|"
          r"thermal_pressure|thermal_level|frequency_ppm|frequency_word|free_bytes|available_bytes|cpu_self_s|"
          r"cpu_children_s|host_busy_cpu_s_per_s|tree_cpu_s_per_s|outside_tree_cpu_s_per_s|unattributed_cpu_s_per_s|"
          r"smc_min_ma|smc_reads_negative|smc_reads_below|smc_reads_in_force|smc_duration_below_s|"
          r"registry_publications_negative|registry_min_ma|accumulator_intervals_over_limit|ACAttached|IsCharging|"
          r"InstantAmperage|Amperage|Voltage|Temperature|freq|offset|jitter|precision|status|decision|cpu_s_per_s|"
          r"worst_cpu_s_per_s)")
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
    # Enumerated leaf names only (G5): no rule takes a field at any depth.
    (r"(fill|disclosure):schema_version|disclosure:sensitivity/(schema_version|label)|"
     r"disclosure:(cells|floors|contrasts|block_lines|fixed_sentences|window_lines/[a-z]+)/[a-z][a-z0-9_]*/(text|label|line)",
     TEXT),
    (r"disclosure:(cells|floors|contrasts|block_lines|fixed_sentences|window_lines/[a-z]+)/[a-z][a-z0-9_]*/restricted",
     DISCLOSURE_CONTROL),
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
    # F1, F2 (RC-CMP-8): the readiness word, the registered contrast-definition words and the leave-one-out words.
    (F + "claim_evaluation/claim_ready_for_l2_l3", "outcome_word", "{cid}/claim_ready"),
    (F + "(?P<field>claim_role|hypothesized_direction)", "outcome_word", "{cid}/{field}"),
    (F + "sampling/confirmatory_status", "outcome_word", "{cid}/confirmatory_status"),
    (F + "(conditions|metric)/(?P<field>condition_a_id|condition_b_id|difference_orientation|name|metric_tag|window_class)",
     "routing_id", "{cid}/definition/{field}"),
    (F + "floor/(?P<field>claim_floor_rule|aggregation)", "routing_id", "{cid}/floor/{field}"),
    (F + r"floor/resolutions/\*/transport_rule_id", "routing_id", "contrast/{cid}/resolution/{resolution}/transport_rule_id"),
    (F + "loo/status", "outcome_word", "{cid}/loo_status"),
    (F + r"loo/rows/\*/influence_triggers/\*", "outcome_word", "{cid}/loo/{loo}/influence_triggers/{trigger}"),
    # An empty trigger list is a printed word too ("no trigger"): it binds the whole-list row.
    (F + r"loo/rows/\*/influence_triggers", "outcome_word", "{cid}/loo/{loo}/influence_triggers"),
    (F + "floor/active_floor_j", "floor_gate_j", "{cid}/active_floor_j"),
    (F + "floor/(?P<field>floor_abs_j|floor_cmp_j)", "floor_gate_j", "{cid}/{field}"),
    # Arm gates and resolutions by registered position (A, B), never by their printed condition (S2).
    (F + r"floor/resolutions/\*/(?P<field>floor_abs_j|floor_cmp_j|floor_gate_j)", "floor_gate_j",
     "{cid}/resolution/{resolution}/{field}"),
    (F + r"floor/resolutions/\*/source_cell_ids/\*", "routing_id", "contrast/{cid}/resolution/{resolution}/source_cell_ids/{source}"),
    # A3, A4 (RC-CMP-9): the contrast's floor cells and each arm's transport group, against the registered ones.
    (F + r"floor_source_cell_ids/\*", "routing_id", "contrast/{cid}/floor_row_ids/{floor_source}"),
    (F + r"floor/floor_row_ids/\*", "routing_id", "contrast/{cid}/floor_row_ids/{floor_row}"),
    (F + r"floor/resolutions/\*/transport_group_id", "routing_id", "contrast/{cid}/resolution/{resolution}/transport_group_id"),
    (F + r"floor/arm_gates/\*/floor_gate_j", "floor_gate_j", "{cid}/arm/{arm}/floor_gate_j"),
    (F + r"floor/arm_gates/\*/(?P<field>arm_id|condition_family_id)", "routing_id", "contrast/{cid}/arm/{arm}/{field}"),
    (F + r"floor/(resolutions/\*/)?point_floor_diagnostics/(unguarded_floor_j|guard_factor|guarded_floor_j)", FLOOR_DIAGNOSTICS),
    (F + r"floor/(resolutions/\*/)?(point_floor_diagnostics/(label|published_claim_floor)|single_count_discipline/[a-z_]+)",
     UNCOVERED + "attribution-floor diagnostic label and flag, and the single-count discipline's words"),
    (F + r"floor/(status|transport_verdict|floor_source|floor_limit_class|"
     r"arm_gates/\*/status|resolutions/\*/(status|reason_codes(/\*)?|floor_source|floor_limit_class))",
     UNCOVERED + "floor-resolution status and source words: they report how the engine's floor transport resolved "
     "each arm (exact, transported, refused) and its attribution-limit class; the recompute has no transport model "
     "and re-derives no such word (NEEDS_RULING RC-CMP-8 2); every resolved floor value is compared"),
    (F + r"loo/rows/\*/estimate", "contrast_j", "{cid}/loo/{loo}/dbar_j"),
    (F + r"loo/rows/\*/(?P<field>raw_p|adjusted_p)", "contrast_p", "{cid}/loo/{loo}/{field}"),
    (F + r"loo/rows/\*/(?P<field>outcome|floor_status)", "outcome_word", "{cid}/loo/{loo}/{field}"),
    (F + r"loo/rows/\*/n_blocks", "count", "{cid}/loo/{loo}/n"),
    (F + r"loo/rows/\*/df", "count", "{cid}/loo/{loo}/df"),
    (F + r"loo/rows/\*/metrology_aware_ci95/(?P<side>lower|upper)", "contrast_j", "{cid}/loo/{loo}/metrology_interval_j/{side}"),
    (F + r"loo/rows/\*/decision_interval/(?P<side>lower|upper)", "contrast_j", "{cid}/loo/{loo}/decision_interval_j/{side}"),
    (F + r"claim_evaluation/reason_codes/\*",
     UNCOVERED + "L9 reason-code vocabulary: it also names inputs the recompute does not re-derive (randomization "
     "check, floor transport and resolution, legacy mechanics); the outcome, ceiling, readiness and every "
     "leave-one-out influence trigger these codes summarise are compared"),
    # A4 (RC-CMP-9): the fill's block ids, by position against the registered blocks the recompute keeps or leaves out.
    (F + r"kept_block_ids/\*", "routing_id", "contrast/{cid}/kept_block_ids/{kept_block}"),
    (F + r"(sampling/)?removed_block_ids/\*", "routing_id", "contrast/{cid}/removed_block_ids/{removed_block}"),
    (F + r"(equivalence/method|conditions/(cell_a_id|cell_b_id)|metric/unit)",
     UNCOVERED + "contrast-definition words the sealed manifest's contrast row does not register (cell ids, the "
     "metric unit, the equivalence method of a contrast with none); they assert no claim, direction or status"),
    (F + r"equivalence/margin", NAMED + "registered contrast definition from the sealed manifest"),
    (F + r"(equivalence|metric/ratio_estimand)", NULL_NAMED + "registered contrast definition: no equivalence margin, "
     "no ratio estimand (J contrasts)"),
    (r"fill:(gamma/(evidence_class|limitations/\*|contrasts/\*/limitations/\*))",
     UNCOVERED + "registered limitation notes; copied from the claim verdicts by L9's validated adapter"),
    (r"fill:characterization/(funded|run)", UNCOVERED + "characterization selection; not funded, not run (constant)"),
    (r"fill:characterization/verdict", NULL_NAMED + "characterization selection; not funded, not run (constant)"),
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
    (D + r"contrasts/primary_contrast/estimator/(SE_repeat|SE_metrology|repeat_point_CI95/(lower|upper)|"
     r"variance_contributions/\*/(summed_paired_variance|squared_standard_error))", ESTIMATOR_INTERNALS),
    (D + r"contrasts/primary_contrast/estimator/name", "routing_id", "{cid}/estimator_name"),
    (D + r"contrasts/primary_contrast/estimator/(excluded_stochastic_terms/\*|variance_contributions/\*/name)",
     UNCOVERED + "estimator internals' labels (variance-contribution names, no extra stochastic terms); they assert no "
     "claim, and the contributions' values are listed as estimator internals"),
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
    (D + r"contrasts/(loo_counts/exclusive_block_numbers/\*|loo_magnitude/rows/\*/block_number)",
     IDENTITY + "; leave-one-out block numbers (strings by design); the outcomes, estimates and p values of every "
     "leave-one-out row are compared"),
    (D + r"contrasts/kept_units/n_b", "count", "{cell_id}/n"),
    (D + r"contrasts/kept_units/n_r", FLOOR_KEPT),
    (D + r"(cells|contrasts|floors)/[a-z_]+/(codes/\*/(blinding|code|family)|families(/\*)?|stratum|removed_unit_ids(/\*)?|"
     r"attained_by(/\*)?)",
     UNCOVERED + "removed-unit codes and families; exclusions are re-derived by the recompute (exclusions_rederivation)"),
    # F2 (RC-CMP-8): the status words the producer fixes.
    (D + r"cells/reported_cell/status", "outcome_word", "disclosure/{pack}/{rcid}/reported_cell/status"),
    (D + r"cells/battery_assist_cell/primary/status", "outcome_word", "disclosure/{pack}/{rcid}/battery_assist_cell/primary/status"),
    (D + r"contrasts/battery_assist_contrast/status", "outcome_word", "disclosure/{cid}/battery_assist_contrast/status"),
    (D + r"cells/battery_assist_cell/without/status", DESCRIPTIVE_STATUS),
    (D + r"(cells/load_correlated_cell|contrasts/load_correlated_contrast)/values/(status|code)",
     UNCOVERED + "load-correlated sensitivity line's status and refusal code (PLAN 8.1): the line never replaces a "
     "primary value and gates nothing, and the recompute's load-sensitivity block is not compared here"),
    # Window lines: the NEG-8 terms, b_op, reference and corpus counts and the whole-machine line.
    (W + r"neg8_allowance/values_j/bracket\.claim_families\.gross_energy\.(?P<field>bound_envelope_j|bound_prediction_j|"
     r"start\.mean_j|midpoint\.mean_j|end\.mean_j|trajectory_excursion_max_j|drift_allowance_j)",
     "floor_j", "disclosure/{pack}/neg8_allowance/{field}"),
    (W + r"neg8_allowance/values_j/[A-Za-z0-9_.]+_j", NEG8_INTERNALS),
    (W + r"reference_counts/counts/(?P<slot>start|midpoint|end)", "count", "disclosure/{pack}/reference_counts/{slot}"),
    (W + r"reference_counts/planned/(start|midpoint|end)", CONSTANT),
    (W + r"corpus_counts/deciding", "count", "disclosure/{pack}/corpus_counts/deciding"),
    (W + r"corpus_counts/(collected|in_window|drop_counts/[A-Za-z0-9_.]+)", STRUCTURE_NUMBER),
    (W + r"below_screen_bound/b_op_s", "b_op_s", "{pack}/b_op_s"),
    (W + r"neg8_allowance/source", "outcome_word", "disclosure/{pack}/neg8_allowance/source"),
    (D + r"floors/floor_composition/source", "outcome_word", "disclosure/{floor_cell}/floor_composition/source"),
    (W + r"machine_member/rho", "rho", "machine/{pack}/{run_id}/request/rho"),
    (W + r"machine_member/rail_j", "machine_j", "machine/{pack}/{run_id}/request/rail_delta_J"),
    (W + r"machine_member/machine_j", "machine_j", "machine/{pack}/{run_id}/request/delta_J"),
    (W + r"machine_summary/(?P<stat>median|minimum|maximum|q25|q75|spread)", "rho", "machine_summary/{pack}/{model}/{stat}"),
    (W + r"machine_summary/central_band/(?P<side>lower|upper)", "rho", "machine_summary/{pack}/{model}/central_band/{side}"),
    (W + r"machine_summary/central_band/pack", "routing_id", "machine_summary/{pack}/{model}/central_band/pack"),
    (W + r"machine_summary/central_band/attempt", IDENTITY_NUMBER),
    (W + r"below_screen_bound/below", "outcome_word", "disclosure/{pack}/below_screen_bound/below"),
    (W + r"(neg8_screen/decision|battery_temperature_sentence/neg8)", "outcome_word", "disclosure/{pack}/neg8_screen/decision"),
    (W + r"machine_member/plausible", "outcome_word", "machine/{pack}/{run_id}/request/plausible"),
    (W + r"machine_member/battery_term_available", "battery_term", "machine/{pack}/{run_id}/request/battery_term_available"),
    (W + r"(monitor_cost/(cpu_s|reader_cpu_s|probes_inside_target_phases)|(arm_hazards|battery_phase)/measurements/" + HAZARD + "|"
     r"(physics_counts|battery_counts)/counts/[A-Za-z0-9_.]+|(anchor_counts|flag_count|stored_member_reason)/count|"
     r"(anchor_bound|host_cpu)/value_s|(battery_temperature|battery_temperature_sentence)/(readings_centi_c/\*|rise_k)|"
     r"erratum3_triggers/values/(doubling_count|systematic_sequences/\*)|"
     r"deciding_membership/(deciding_references|deciding_spares|writer_excluded_count|writer_excluded_by_family/[A-Za-z0-9_.]+))",
     STRUCTURE_NUMBER),
    (W + r"erratum3_triggers/values", NULL_NAMED + "no calibration bracket recorded for the window: the producer "
     "prints no trigger object (disclosures._trigger_values)"),
    (W + r"battery_discharged/value_j", NAMED + "battery-assist discharged energy from the withheld battery record; "
     "the recompute flags battery assist but does not re-derive this energy"),
    (W + r"ledger_binding/terminal_sequence", IDENTITY_NUMBER),
    # F2: the window lines' remaining words, each by its enumerated leaf name (disclosures.py _item calls).
    (W + r"((arm_hazards|battery_phase)/measurements/" + HAZARD + r"|arm_hazards/(module|phase|verdict)|battery_phase/phase|"
     r"flag_count/(family|code|blinding)|arm_unmeasured/modules/\*|machine_member/(removed|meter_flags/\*)|"
     r"corpus_counts/desk_cap/\*|corpus_physics_drop/codes/\*|reference_lost/(slot|reason)|"
     r"reference_spare/(slot|succeeded)|bound_formula/formula|"
     r"battery_temperature/(plateau|harvest_flag|producer_flag|temperature_unmeasured|differs_from_harvest_flag)|"
     r"erratum3_triggers/values/(observed_triggers|recorded_only_triggers)/\*)", STRUCTURE),
    (W + r"(stored_status/status|stored_condition/(condition|answered_by)|stored_member_reason/(reason|all_removed|families/\*|"
     r"codes/\*/(code|blinding))|adapter_continuity/decision|tripwire/(tripwire|result)|reference_parity/result|"
     r"ledger_binding/prefix_result|deciding_membership/writer_excluded_all_removed)", HARVEST_WORDS),
    (W + r"ledger_binding/(sha256sums_sha256|ledger_copy_sha256)", IDENTITY),
    # Block lines.
    (D + r"block_lines/dominance_ratio/ratio", "dominance_ratio", "ratio/{ratio_label}/ratio"),
    (D + r"block_lines/dominance_ratio/(?P<field>numerator_j|denominator_j)", "floor_j", "ratio/{ratio_label}/{field}"),
    (D + r"block_lines/dominance_ratio/n", "count", "ratio/{ratio_label}/n"),
    (D + r"block_lines/dominance_ratio/status", "outcome_word", "ratio/{ratio_label}/status"),
    (D + r"block_lines/dominance_ratio/component", IDENTITY),
    (D + r"block_lines/dominance_branch/branch", "dominance_branch", "branch"),
    (D + r"block_lines/dominance_branch/dominance_sentence_licensed", "dominance_branch", "dominance_sentence_licensed"),
    (D + r"(block_lines/sensitivity_bmax|sensitivity/b_max)/value_s", "b_op_s", "sensitivity/B_max_s"),
    (D + r"(block_lines/sensitivity_bmax|sensitivity/b_max)/(?P<field>T|attained_by_sequence)", "count", "sensitivity/{field}"),
    (D + r"block_lines/sensitivity_window/(?P<field>b_op_s|b_sens_s)", "b_op_s", "sensitivity/windows/{pack}/{field}"),
    (D + r"sensitivity/windows/(?P<pack>[a-z]+)/(?P<field>b_op_s|b_sens_s)", "b_op_s", "sensitivity/windows/{pack}/{field}"),
    (D + r"block_lines/sensitivity_window/widened", "outcome_word", "sensitivity/windows/{pack}/widened"),
    (D + r"sensitivity/windows/(?P<pack>[a-z]+)/widened", "outcome_word", "sensitivity/windows/{pack}/widened"),
    (SR + r"(?P<field>status|code|equals_primary|not_below_primary)", "outcome_word", "sensitivity/{pack}/{rcid}/{field}"),
    (SF + r"(?P<field>equals_primary|not_below_primary)", "outcome_word", "sensitivity/{aggregate_cell}/{field}"),
    (SC + r"(?P<field>outcome_equals_primary|not_below_primary)", "outcome_word", "sensitivity/{cid}/{field}"),
    # F2 (RC-CMP-8): true by construction (sensitivity.py refuses otherwise); compared against True.
    (SR + r"mean_and_half_width_equal_primary", "outcome_word", "sensitivity/{pack}/{rcid}/mean_and_half_width_equal_primary"),
    (SC + r"bound_independent_values_equal_primary", "outcome_word", "sensitivity/{cid}/bound_independent_values_equal_primary"),
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
    (SC + r"floor_cell_ids/\*", "routing_id", "sensitivity/{cid}/floor_cell_ids/{floor_cell}"),
    (D + r"block_lines/(attempt_count/count|attempt_history/(attempt|collected|planned|flags_by_family/[A-Za-z0-9_.]+|"
     r"triggers/(doubling_count|systematic_sequences/\*))|g10/(codes/[A-Za-z0-9_.]+|redraw_cycles)|"
     r"reharvest_account/(survivors_before|survivors_after))", STRUCTURE_NUMBER),
    # F2: the attempt-history and harvest lines' words, by enumerated leaf name (disclosures._history_lines and
    # the harvest_once and reharvest_account lines).
    (D + r"block_lines/(attempt_count/(superseded|causes/\*)|attempt_history/(verdict|cause_key|superseded|catalog_path|"
     r"triggers/(observed_triggers|recorded_only_triggers)/\*)|harvest_once/no_analysed_window_harvested_twice|"
     r"reharvest_account/(reason|original_pin|deciding_pin|original_harvest_sha256|deciding_harvest_sha256))", HARVEST_WORDS),
    (r"fill:campaigns/(alpha|beta)/attempt|disclosure:(cells|floors|contrasts)/removed_unit/positions/\*", IDENTITY_NUMBER),
    # Identity at the positions L9's producers print it (results_fill_adapter, build_results_fill_input, disclosures).
    (r"fill:campaigns/(?P<pack>alpha|beta)/claim_usable", "outcome_word", "campaigns/{pack}/claim_usable"),
    (r"fill:(campaigns/(alpha|beta)/(plan_id|exclusions_sha256|harvest_record_sha256)|"
     r"gamma/(claim_verdicts_id|claim_verdicts_sha256|exclusions_sha256|finalized_manifest/(manifest_id|file_sha256)|"
     r"floor_artifact/(artifact_id|file_sha256)|contrasts/\*/(contrast_id|plan_id|"
     r"floor/resolutions/\*/source_cell_ids/\*|loo/rows/\*/omitted_block_id)))", IDENTITY),
    (r"disclosure:(windows/[a-z]+/(plan_id|harvest_pin|record_shape)|"
     r"(cells|floors|contrasts)/[a-z_]+/(pack|cell_id|contrast_id|unit_id|stage_ids/\*)|"
     r"window_lines/[a-z]+/[a-z_]+/(pack|run_id|model|stage_id|harvest_pin|central_band/plan_id)|"
     r"block_lines/[a-z_]+/(pack|plan_id|cell_id|component|record/(pack|cell_id|contrast_id))|"
     r"sensitivity/((reported_cells|floor_cells)/\*/(pack|cell_id)|contrasts/\*/contrast_id|"
     r"windows/[a-z]+/plan_id))", IDENTITY),
)


def numeric(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def leaves(value, label, path="", star="", context=None, at=()):
    """(path, value, context): context maps each identity field to (value, path of that field), read
    only from the object that owns it (G2; star is the path with * for each list item), and
    "@<list>" to the position in each enclosing list. Other scalars never enter the context, so a
    nested object cannot re-route its parent's leaves. "@@at" is the leaf's concrete path (keys and
    list positions), which the expected-check table's claims are written in (RC-CMP-9)."""
    context = context or {}
    if isinstance(value, dict) and value:
        context = {**context, **{key: (item, join(path, key)) for key, item in value.items()
                                 if owns(label, key, star) and not isinstance(item, (dict, list))}}
        for key, item in value.items():
            yield from leaves(item, label, join(path, key), join(star, key), context, at + (key,))
    elif isinstance(value, list) and value:
        name = "@" + path.rsplit("/", 1)[-1]
        for index, item in enumerate(value):
            yield from leaves(item, label, path + "/" + step(item), star + "/*" if star else "*",
                              {**context, name: (index, None)}, at + (index,))
    else:
        yield path, value, {**context, "@@at": at}


# The fields a key may be built from (S2): a container's identity (its contrast, cell, pack,
# run, model, ratio component and label, leave-one-out block) and list positions. An
# attribute a line asserts about another object (a gate's condition_family_id, a
# resolution's source_cell_ids, a band's pack) never routes a key; it is compared as a
# routing_id row instead. A cell or contrast id routes only through its registered entry (G3).
IDENTITY_FIELDS = ("contrast_id", "cell_id", "pack", "run_id", "model", "component", "text", "omitted_block_id",
                   "block_number")
POSITIONS = {"arm": "@arm_gates", "resolution": "@resolutions", "source": "@source_cell_ids", "trigger": "@influence_triggers",
             "floor_row": "@floor_row_ids", "floor_source": "@floor_source_cell_ids", "floor_cell": "@floor_cell_ids",
             "kept_block": "@kept_block_ids", "removed_block": "@removed_block_ids"}


def binding(context, groups, registry):
    """Key fields, and for each the id leaves it was read from (none for a path group or a position)."""
    value = {name: context[name][0] for name in IDENTITY_FIELDS if name in context}
    fields = {name: item for name, item in value.items()}
    sources = {name: [context[name][1]] for name in value}

    def derive(name, result, *using):
        if result is not None:
            fields[name], sources[name] = result, [context[u][1] for u in using if u in context]
    cell = value.get("cell_id")
    derive("cid", value.get("contrast_id") if registry.entry(value.get("contrast_id"), "contrast") else None, "contrast_id")
    reported, extraction, floor = (registry.entry(cell, kind) for kind in ("reported", "extraction", "floor"))
    if reported:
        derive("rcid", reported["family"], "cell_id")
    if extraction:
        derive("floor_cell", floor_key(extraction), "cell_id")
        derive("minted_field", f"{cell_key(extraction)}/floor_{'abs' if extraction['form'] == 'absolute' else 'cmp'}_j",
               "cell_id")
    if floor:
        derive("aggregate_cell", cell_key(floor), "cell_id")
        component = value.get("component")
        label = re.match(r"\S+ \S+: (R|R_cm) ", str(value.get("text", "")))
        if label and component:
            derive("ratio_label", f"{cell_key(floor)}/{component}" + ("/common_mode" if label[1] == "R_cm" else ""),
                   "cell_id", "component", "text")
    derive("loo", loo_key(registry, value.get("contrast_id"), value.get("omitted_block_id")), "omitted_block_id")
    derive("loo_number", block_key(value.get("block_number")), "block_number")
    for name, position in POSITIONS.items():
        if position in context:
            fields[name], sources[name] = context[position][0], []
    for name, group in groups.items():
        if group is not None:
            fields[name], sources[name] = group, []
    return fields, sources


def key_for(template, context, groups, registry):
    """The row key a leaf binds to, and the id leaves that routed it; None when a field is unresolved."""
    fields, sources = binding(context, groups, registry)
    names = re.findall(r"\{(\w+)\}", template)
    if any(not isinstance(fields.get(name), (str, int)) or isinstance(fields.get(name), bool) for name in names):
        return None, []
    return template.format(**{name: fields[name] for name in names}), [p for name in names for p in sources[name]]


# A string spelling a number (Opus round 3 F3): numeric-class, except under the text and identity rules.
NUMBER_WORD = r"\s*[+-]?((0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?[0-9]+)?|\.[0-9]+|NaN|nan|Infinity|inf)\s*"


def numeric_word(value):
    return isinstance(value, str) and re.fullmatch(NUMBER_WORD, value) is not None


def admits(rule, value, number, nonfinite, word=False):
    """Default deny for numbers (S1): uncovered: takes strings and booleans only (a string spelling a
    number only under the text and identity rules); uncovered-null-by-name: a null only."""
    if len(rule) == 3:
        return True
    if rule[1].startswith(UNCOVERED):
        return not number and (not word or rule[1].startswith((TEXT, IDENTITY)))
    if rule[1].startswith(NULL_NAMED):
        return value is None and not nonfinite
    return True


# The fill's position-by-position copies of a verdict list, and the comparison rows of their positions.
COPIED_LISTS = ((r"fill:gamma/contrasts/\*/kept_block_ids/\*", r"contrast/ctr-[^/]+/kept_block_ids/[0-9]+"),
                (r"fill:gamma/contrasts/\*/removed_block_ids/\*", r"contrast/ctr-[^/]+/removed_block_ids/[0-9]+"),
                (r"fill:gamma/contrasts/\*/sampling/removed_block_ids/\*", r"contrast/ctr-[^/]+/removed_block_ids/[0-9]+"),
                (r"fill:gamma/contrasts/\*/loo/rows/\*/influence_triggers/\*",
                 r"ctr-[^/]+/loo/b[0-9]+/influence_triggers/[0-9]+"))


def coverage(custody, comparison, rules=None):
    rules = COVERAGE if rules is None else rules
    rows = {(row["family"], row["key"]): row for row in comparison.rows}
    report, unmapped, unbound, named, absent, nonfinite, routed, bound = {}, set(), {}, set(), [], set(), set(), set()
    exemptions = {}
    for label, pattern in STEP11_SOURCES:
        names = custody.names(pattern)
        if not names:
            absent.append(label)
        for name in names:
            document = custody.read(name)
            odd = custody.nonfinite.get(name, set())
            nonfinite.update(label + ":" + leaf for leaf in odd)
            for leaf, value, context in leaves(document, label):
                path = label + ":" + leaf
                number, word = numeric(value) or value is None or leaf in odd, numeric_word(value)
                rule, match = None, None
                for candidate in rules:
                    match = re.fullmatch(candidate[0], path)
                    if match and admits(candidate, value, number, leaf in odd, word):
                        rule = candidate
                        break
                if rule is None and value in ([], {}):
                    # An empty list or object prints no value.
                    report.setdefault(path, UNCOVERED + "empty container; no printed value")
                elif rule is None:
                    unmapped.add(path)
                elif len(rule) == 2:
                    report.setdefault(path, rule[1])
                    if rule[1].startswith(NULL_NAMED) or (rule[1].startswith(NAMED) and (number or word)):
                        named.add(path)
                        exemptions.setdefault(rule[0], set()).add(path)
                else:
                    family = rule[1]
                    key, routes = key_for(rule[2], context, match.groupdict(), custody.registry)
                    row = rows.get((family, key)) if key is not None else None
                    printed = row.get("l9_raw", row.get("l9")) if row else None
                    claimed = comparison.claimed.get(label, set())
                    at = context.get("@@at", ())
                    if re.match(TABLE_CONDITIONAL_LINES, path):
                        claimed = {()}
                    reason = ("key_unresolved" if key is None else "no_row" if row is None else
                              "value_differs" if not same(printed, value) else
                              "row_disagrees" if row["verdict"] != "AGREE" else
                              "route_disagrees" if any(get(rows.get(("routing_id", item)), "verdict") != "AGREE"
                                                       for item in row.get("items", [])) else
                              "duplicate_binding" if (path, family, str(key)) in bound else
                              # RC-CMP-9: a compared leaf binds an expected check only inside an item the
                              # registry-driven table claimed (its own row, line or cell).
                              "not_in_table" if not any(at[:depth] in claimed for depth in range(len(at) + 1)) else None)
                    bound.add((path, family, str(key)))
                    if reason:
                        # Mapped, but not a copy of an agreeing compared row: not coverage.
                        unbound.setdefault((path, family, str(key), reason), None)
                    else:
                        report.setdefault(path, family)
                        routed.update(label + ":" + source for source in routes)
    for pattern, key in COPIED_LISTS if "fill" not in absent else ():
        # RC-CMP-9: a list the fill copies position by position prints every position the comparison holds.
        printed = {bound_key for path, _, bound_key in bound if re.fullmatch(pattern, path)}
        for row in comparison.rows:
            if re.fullmatch(key, row["key"]) and row["l9"] is not None and row["key"] not in printed:
                unbound.setdefault((pattern.replace("\\", ""), row["family"], row["key"], "copy_shortened"), None)
    uncompared = sorted({path for path, *_ in unbound})
    for path in routed - set(uncompared):
        # An identity field that routed an agreeing binding is compared by its routing_id rows (S2).
        report[path] = "routing_id"
    for path in uncompared:
        report.pop(path, None)
    return {"leaves": report, "unmapped": sorted(unmapped | set(uncompared)), "uncompared": uncompared,
            "unbound": [{"path": p, "family": f, "key": k, "reason": r} for p, f, k, r in sorted(unbound)],
            "uncovered_numeric": sorted(named), "absent_sources": absent, "nonfinite": sorted(nonfinite),
            # G5: each named numeric exemption (rule pattern) with the leaves it took, for the full-size census.
            "named_exemptions": {pattern: sorted(paths) for pattern, paths in sorted(exemptions.items())}}


def run(l9_custody, recompute_path, bars_path=DEFAULT_BARS, rules=None, meter=(), registry=None):
    bars = load_bars(bars_path)
    flags = []
    meter_records, meter_digests = load_meter_records(meter, flags)
    custody = Custody(l9_custody, flags, registry)
    try:
        ours = loads(Path(recompute_path).read_bytes(), flags, "recompute", duplicate="recompute_output_duplicate_key")
    except (OSError, ValueError):
        raise Refusal("recompute_output_unreadable") from None
    c = Comparison(bars)
    # RC-CMP-9: the registry-driven walk first: every expected check must find its item on both sides.
    table = compare_expected(c, custody, ours)
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
    compare_campaigns(c, custody, ours)
    cover = coverage(custody, c, rules)
    return {"schema": SCHEMA, "bar_set": bars.get("bar_set"), "bars": bars["families"],
            "l9_steps": {f"{s}/{w}" if w else str(s): v for (s, w), v in sorted(custody.status.items(), key=str)},
            "recompute_program_sha256": ours.get("program_sha256"), "harvest_meter_sha256": meter_digests,
            "routing_registry_sha256": custody.registry.digests,
            "structure_flags": flags, "counts": c.counts(),
            # RC-CMP-9 A1: the expected-check table's structure (families, checks, conditions; no value).
            "expected_checks": table_structure(table),
            # G7: each member kept out of a family's key universe, with the family it is compared in.
            "excluded_members": c.excluded,
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
