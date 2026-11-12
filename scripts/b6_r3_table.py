#!/usr/bin/env python3
"""Block 6 §17-R3 printed-quantity table, regenerated from code (OPEN[R3-TABLE]).

Inputs (code and configuration only; no custody, no outcome):
- configs/b6/recompute/production_comparison_keys.json: every printed key;
- configs/b6/recompute/precision.json: the S-13 print precision (bars);
- joulewise/b6_analysis_check.py: the option (c) second side. Which keys it
  produces is read from its source (``check_block`` is one function with no
  importable key table), with ``ast``;
- scripts/independent_recompute_b6.py: RC-B6-1, the production program. Its
  producing functions and the pinned Block 5 functions they call are read
  with ``ast``; ``decimals_for`` and ``quantity_class`` are imported.

Label rules (each row cites the rule it used):
- the key is a row of the option (c) comparison table -> "computed and
  compared" (§17-R3 decision 6 (a));
- the key's result field is checked inside the option (c) gate but is not a
  table row -> "computed and compared (gate check only)";
- the per-phase whole-machine line -> the literal RC-B6-1 stamps on it
  (§17-R8), which must also be b6_analysis_check's single_implementation;
- one producer, value a field of the Block 5 cell or floor estimator's output
  for the registered selection (B5.make_reported / B5.make_floors) ->
  `single-source` (RL-99 item 1);
- any other one-producer key -> "not independently recomputed" (§17-R3: "Where
  there is one producer, label it 'not independently recomputed'").

Exit 1, naming the groups, when any key has no stated producer or label.
Output is deterministic: no clock, no environment, sorted rows.
"""
import argparse
import ast
import collections
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DEFAULTS = {
    "keys": "configs/b6/recompute/production_comparison_keys.json",
    "precision": "configs/b6/recompute/precision.json",
    "check": "joulewise/b6_analysis_check.py",
    "recompute": "scripts/independent_recompute_b6.py",
}
R8_LITERAL = "single implementation; not independently recomputed"
UNSTATED = "UNSTATED"
LABEL_COMPARED = "computed and compared (decision 6 (a))"
LABEL_GATE = "computed and compared inside the option (c) gate (check family {}); not an S-13 table row"
LABEL_SINGLE_SOURCE = "`single-source` (RL-99 item 1)"
LABEL_ONE = "not independently recomputed (§17-R3, one producer)"
LABEL_R8 = '"' + R8_LITERAL + '" (§17-R8)'
B5_ESTIMATORS = ("make_reported", "make_floors")

# Which RC-B6-1 function writes each key family, and the pinned Block 5 calls
# it must contain. Verified against the source below; a missing function or
# call leaves the family UNSTATED.
PRODUCERS = (
    # (regex on the concrete key, packs, RC-B6-1 function, required B5 calls, estimator output?)
    (r"^calibration/b_op_s$", None, "Session.calibration", (), False),
    (r"^neg8/", None, "Session.screen", (), False),
    (r"^reported/", ("ALPHA", "BETA"), "floor_session", ("make_reported",), True),
    (r"^floor/", ("ALPHA", "BETA"), "floor_session", ("make_floors",), True),
    (r"^dominance/qwen3-[^/]+/", ("ALPHA", "BETA"), "dominance_rows", (), True),
    (r"^dominance/branch$", ("GAMMA",), "attach_gamma", (), False),
    (r"^lines/(load_sensitivity|battery_assist|waited_runs|outside_processor_alternative)/qwen3-",
     ("ALPHA", "BETA"), "subset_estimate", ("make_reported",), False),
    (r"^lines/(load_sensitivity|battery_assist|waited_runs|outside_processor_alternative)/(decode|prefill-p2048)",
     ("GAMMA",), "subset_estimate", ("contrast_stats", "quad_difference"), False),
    (r"^lines/single_step_reconstruction/", ("ALPHA", "BETA"), "single_step_cell",
     ("single_step_member", "diagnostic_estimate"), False),
    (r"^lines/scaled_allowance/qwen3-", ("ALPHA", "BETA"), "floor_session",
     ("allowance_factor", "scaled_reported", "scaled_floor"), False),
    (r"^lines/scaled_allowance/(decode|prefill-p2048)/", ("GAMMA",), "finish_gamma",
     ("scaled_gamma_inputs", "finish_contrast"), False),
    (r"^lines/whole_machine/", ("ALPHA", "BETA"), "add_session_machine", ("add_machine",), False),
    (r"^contrast/(decode|prefill-p2048)/(energy_ratio|energy_ratio_lower|energy_ratio_upper|per_token_j)$",
     ("GAMMA",), "finish_gamma", ("descriptive_estimate",), False),
    (r"^contrast/", ("GAMMA",), "finish_gamma", ("finish_contrast",), False),
    (r"^cross_session/", ("GAMMA",), "finish_gamma", ("cross_window",), False),
)
BLOCK_PRODUCER = "block_lines"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def functions(tree):
    """{qualified name: FunctionDef} for module functions and class methods."""
    out = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            out[node.name] = node
        elif isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    out[node.name + "." + item.name] = item
    return out


def b5_calls(fn):
    return {n.func.attr for n in ast.walk(fn) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
            and isinstance(n.func.value, ast.Name) and n.func.value.id == "B5"}


def strings(node):
    return [n.value for n in ast.walk(node) if isinstance(n, ast.Constant) and isinstance(n.value, str)]


def leftmost(node):
    """The first string of a left-nested ``a + b + c`` chain, or None."""
    while isinstance(node, ast.BinOp):
        node = node.left
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else None


def is_name(node, name):
    return isinstance(node, ast.Name) and node.id == name


# ---------------------------------------------------------------- the option (c) side

def read_check(path):
    """What check_block writes into its comparison table, and which result fields it checks."""
    tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    fn = functions(tree).get("check_block")
    if fn is None:
        raise SystemExit("b6_r3_table: check_block not found in " + str(path))
    session_keys, contrast_fields, phases = {}, {}, set()
    gate_fields, block_heads, single = {}, {}, []
    for node in ast.walk(fn):
        # q["calibration/b_op_s"] = ...  and  q["contrast/" + phase + "/" + exposed[key]] = expected
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Subscript) and is_name(target.value, "q"):
                    if isinstance(target.slice, ast.Constant):
                        session_keys[target.slice.value] = node.lineno
                    elif isinstance(target.slice, ast.BinOp):
                        parts = strings(target.slice)
                        if leftmost(target.slice) == "contrast/":
                            phases.update(p for p in parts if p in ("decode", "prefill-p2048"))
                            contrast_fields["__line__"] = node.lineno
        # q.update({"neg8/allowance_j": ..., ...})
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "update"
                and is_name(node.func.value, "q") and node.args and isinstance(node.args[0], ast.Dict)):
            for k in node.args[0].keys:
                if isinstance(k, ast.Constant):
                    session_keys[k.value] = node.lineno
        # exposed = {"n": "n", ...}: the contrast fields that become table rows
        if (isinstance(node, ast.Assign) and any(is_name(t, "exposed") for t in node.targets)
                and isinstance(node.value, ast.Dict)):
            for v in node.value.values:
                contrast_fields[v.value] = node.lineno
        # check("engine", cid + "/" + key, original[key], expected) over a literal tuple of (field, value)
        if isinstance(node, ast.For) and isinstance(node.iter, ast.Tuple):
            fams = [c.args[0].value for c in ast.walk(node) if isinstance(c, ast.Call) and is_name(c.func, "check")
                    and c.args and isinstance(c.args[0], ast.Constant)]
            firsts = [e.elts[0].value for e in node.iter.elts if isinstance(e, ast.Tuple) and e.elts
                      and isinstance(e.elts[0], ast.Constant)]
            if "engine" in fams:
                for f in firsts:
                    gate_fields[f] = (("engine",), (node.lineno,))
            if "section10" in fams:
                for f in firsts:
                    block_heads[f] = node.lineno
        if isinstance(node, ast.Call) and is_name(node.func, "check") and len(node.args) >= 3:
            fam = node.args[0].value if isinstance(node.args[0], ast.Constant) else None
            actual = node.args[2]
            # original["outcome"], original["decision_interval_j"][i]
            while isinstance(actual, ast.Subscript) and not (is_name(actual.value, "original")):
                actual = actual.value
            if (fam and isinstance(actual, ast.Subscript) and is_name(actual.value, "original")
                    and isinstance(actual.slice, ast.Constant)):
                prior = gate_fields.get(actual.slice.value, ((), ()))
                gate_fields[actual.slice.value] = (tuple(sorted(set(prior[0]) | {fam})),
                                                   tuple(sorted(set(prior[1]) | {node.lineno})))
            # table["block"]["quantities"][name] for "side_by_side/" + ... and "replication/" + ...
        if isinstance(node, ast.Assign):
            for expr in [node.value] + [t.slice for t in node.targets if isinstance(t, ast.Subscript)]:
                head = leftmost(expr)
                if head in ("side_by_side/", "replication/"):
                    block_heads[head.rstrip("/")] = node.lineno
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Dict):
            for k, v in zip(node.value.keys, node.value.values):
                if isinstance(k, ast.Constant) and k.value == "single_implementation":
                    single = [e.value for e in v.elts]
    line = contrast_fields.pop("__line__", None)
    if line is None or not phases:
        raise SystemExit("b6_r3_table: contrast row form not found in check_block")
    return {"session_keys": session_keys, "contrast_fields": contrast_fields, "contrast_line": line,
            "phases": phases, "gate_fields": gate_fields, "block_heads": block_heads, "single": single,
            "lines": (fn.lineno, fn.end_lineno)}


# ---------------------------------------------------------------- RC-B6-1

def read_recompute(path):
    tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    fns = functions(tree)
    # contrast_keys: printed suffix -> result field (decision_lower_j -> decision_interval_j)
    printed = {}
    ck = fns.get("contrast_keys")
    if ck is not None:
        for node in ast.walk(ck):
            if isinstance(node, ast.Dict):
                for k, v in zip(node.keys, node.values):
                    ks, vs = strings(k) if k is not None else [], strings(v)
                    if ks and ks[-1].startswith("/") and vs:
                        printed[ks[-1][1:]] = vs[0]
            if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Subscript):
                ks, vs = strings(node.targets[0].slice), strings(node.value)
                if ks and ks[-1].startswith("/") and vs:
                    printed[ks[-1][1:]] = vs[0]
    machine = fns.get("add_session_machine")
    r8 = None if machine is None else next((n.lineno for n in ast.walk(machine) if isinstance(n, ast.Constant)
                                            and n.value == R8_LITERAL), None)
    return {"fns": fns, "printed": printed, "r8": r8}


def load_module(path):
    spec = importlib.util.spec_from_file_location("b6_r3_recompute", path)
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(Path(path).resolve().parents[1]))
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------- grouping

def generalize(key):
    key = re.sub(r"qwen3-[0-9a-z]+", "<model>", key)
    key = re.sub(r"/(decode|prefill-p2048)(/|$)", r"/<phase>\2", key)
    return re.sub(r"/(absolute|comparative)(/|$)", r"/<mode>\2", key)


def split_block(key):
    parts = key.split("/")
    if parts[0] in ("summary", "inclusive", "side_by_side"):
        return "/".join(parts[:-1]), parts[-1]
    return key, None


def classify_session(key, pack, check, rc):
    """(producers, label) for one session key; UNSTATED where nothing in the code states it."""
    fns, rows = rc["fns"], []
    for pattern, packs, fname, needs, estimator in PRODUCERS:
        if re.search(pattern, key) and (packs is None or pack in packs):
            rows.append((fname, needs, estimator))
            break
    if not rows:
        return UNSTATED, UNSTATED, "no RC-B6-1 producer declared"
    fname, needs, estimator = rows[0]
    fn = fns.get(fname)
    missing = sorted(set(needs) - b5_calls(fn)) if fn is not None else list(needs)
    if fn is None or missing:
        return UNSTATED, UNSTATED, "RC-B6-1 `{}` missing or lacks B5.{}".format(fname, ",".join(missing))
    calls = ", ".join("B5." + c for c in needs)
    primary = "RC-B6-1 `{}` (RC:{}){}".format(fname, fn.lineno, "; " + calls if calls else "")
    c0, c1 = check["lines"]
    field = key.rsplit("/", 1)[-1]
    # 1. a row of the option (c) comparison table
    if key in check["session_keys"]:
        return (primary + "; second: `check_block` (CHK:{})".format(check["session_keys"][key]), LABEL_COMPARED,
                "CHK:{}".format(check["session_keys"][key]))
    if key.startswith("contrast/") and field in check["contrast_fields"]:
        return (primary + "; second: engine twin via `check_block` (CHK:{})".format(check["contrast_line"]),
                LABEL_COMPARED, "CHK:{}".format(check["contrast_line"]))
    # 2. checked inside the gate on the result field the printed key reads
    if key.startswith("contrast/"):
        source = rc["printed"].get(field)
        if source in check["gate_fields"]:
            fams, lines = check["gate_fields"][source]
            line = ",".join(str(x) for x in lines)
            return (primary + "; second: engine twin via `check_block` (CHK:{})".format(line),
                    LABEL_GATE.format(", ".join("`" + f + "`" for f in fams)),
                    "CHK:{} (result field `{}`)".format(line, source))
    # 3. the per-phase whole-machine line (R8)
    if key.startswith("lines/whole_machine/"):
        if not (rc["r8"] and any("per-phase whole-machine" in s for s in check["single"])):
            return UNSTATED, UNSTATED, "R8 literal or single_implementation entry missing"
        return (primary + "; per-phase line only (request-level line is `request_cross_check`, not a printed key)",
                LABEL_R8, "RC:{} literal; CHK:{} single_implementation".format(rc["r8"], c1))
    # 4. one producer
    if estimator and set(needs) & set(B5_ESTIMATORS) or estimator and fname == "dominance_rows":
        return primary + "; no second producer in `check_block`", LABEL_SINGLE_SOURCE, "CHK:{}-{} (absent)".format(c0, c1)
    return primary + "; no second producer in `check_block`", LABEL_ONE, "CHK:{}-{} (absent)".format(c0, c1)


def classify_block(key, check, rc):
    head = key.split("/", 1)[0]
    fn = rc["fns"].get(BLOCK_PRODUCER)
    if fn is None or head not in check["block_heads"]:
        return UNSTATED, UNSTATED, "no §10-§11 producer for `{}`".format(head)
    line = check["block_heads"][head]
    return ("RC-B6-1 `{}` (RC:{}); second: `check_block` §10-§11 arithmetic (CHK:{}) over RC-B6-1's session values"
            .format(BLOCK_PRODUCER, fn.lineno, line), LABEL_COMPARED, "CHK:{}".format(line))


def bar(key, rc_module, spec):
    places = rc_module.decimals_for(key, spec)
    family = rc_module.quantity_class(key)
    if places is None:
        return "`{}`, exact (count or word)".format(family)
    return "`{}`, {} decimals, bar {:g}".format(family, places, 0.5 * 10.0 ** -places)


def build(paths):
    keys = json.loads(Path(paths["keys"]).read_text(encoding="utf-8"))
    spec = tuple((p, d) for p, d in json.loads(Path(paths["precision"]).read_text(encoding="utf-8"))["decimals"])
    check, rc = read_check(paths["check"]), read_recompute(paths["recompute"])
    module = load_module(paths["recompute"])
    groups = collections.OrderedDict()

    def add(scope, pack, key, stat, result, bar_text):
        name = generalize(key)
        row = groups.setdefault((scope, name), {"packs": set(), "stats": set(), "n": 0, "result": set(),
                                                "bar": set()})
        row["packs"].add(pack)
        row["n"] += 1
        row["result"].add(result)
        row["bar"].add(bar_text)
        if stat:
            row["stats"].add(stat)

    for pack in sorted(keys["session_quantity_keys"]):
        for key in keys["session_quantity_keys"][pack]:
            add("session", pack, key, None, classify_session(key, pack, check, rc), bar(key, module, spec))
    for key in keys["block_quantity_keys"]:
        base, stat = split_block(key)
        m = re.search(r"/(ALPHA|BETA|GAMMA)/", key)
        add("block", m.group(1) if m else "all", base, stat, classify_block(key, check, rc), bar(key, module, spec))
    return keys, groups


def render(paths, keys, groups):
    out = ["# Block 6 §17-R3 printed-quantity table (generated by scripts/b6_r3_table.py)", "",
           "Inputs (SHA-256):", ""]
    for name in ("keys", "precision", "check", "recompute"):
        out.append("- `{}` `{}`".format(DEFAULTS[name], sha256(paths[name])))
    out += ["", "CHK = `joulewise/b6_analysis_check.py`, RC = `scripts/independent_recompute_b6.py` (line numbers).",
            "", "| # | Scope | Key group | Packs | Stats | Keys | Producer(s) | Comparator family, bar | Label | Source |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    unstated = []
    labels = collections.Counter()
    for i, ((scope, name), row) in enumerate(sorted(groups.items()), 1):
        if len(row["result"]) != 1:
            prod = label = UNSTATED
            src = "keys in this group disagree: " + "; ".join(sorted(r[1] for r in row["result"]))
        else:
            prod, label, src = next(iter(row["result"]))
        if UNSTATED in (prod, label):
            unstated.append("{} `{}`: {}".format(scope, name, src))
        labels[label] += row["n"]
        out.append("| {} | {} | `{}` | {} | {} | {} | {} | {} | {} | {} |".format(
            i, scope, name, ",".join(sorted(row["packs"])), ",".join(sorted(row["stats"])) or "—", row["n"], prod,
            " / ".join(sorted(row["bar"])), label, src))
    total = len(keys["block_quantity_keys"]) + sum(len(v) for v in keys["session_quantity_keys"].values())
    covered = sum(r["n"] for r in groups.values())
    out += ["", "Keys covered: {} of {}; {} groups; UNSTATED groups: {}.".format(covered, total, len(groups),
                                                                             len(unstated)), "",
            "Keys by label:", ""]
    out += ["- {}: {}".format(k, v) for k, v in sorted(labels.items())]
    return "\n".join(out) + "\n", unstated, covered, total


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for name, default in DEFAULTS.items():
        parser.add_argument("--" + name, default=str(ROOT / default))
    args = parser.parse_args(argv)
    paths = {k: Path(getattr(args, k)) for k in DEFAULTS}
    keys, groups = build(paths)
    text, unstated, covered, total = render(paths, keys, groups)
    sys.stdout.write(text)
    if unstated or covered != total:
        sys.stderr.write("b6_r3_table: {} UNSTATED group(s):\n".format(len(unstated)))
        for row in unstated:
            sys.stderr.write("  " + row + "\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
