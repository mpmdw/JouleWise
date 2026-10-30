"""RC-CMP9-FABLE-REV answer 3: the table's required nested key paths for every disclosure line against the producer's
_item calls on origin/main (AST, text only), with ** expansions and dict-valued keywords resolved from the producer's
own builders (EXPANSIONS, producer line in the comment). Reports, per line word:
  OVER-REFUSAL RISK: a required path the producer does not write unconditionally;
  GAP: a key the producer writes unconditionally (literal keyword or resolved **) that the table does not require and
       that is not the line's selector or a LINE_COMMON field.
Run with --dump to print each _item call's keywords and their value expressions (the basis of EXPANSIONS)."""
import ast
import sys

sys.path.insert(0, "/home/user/JouleWise")
from scripts import compare_b5_recompute as cmp  # noqa: E402

SRC = sys.argv[1]
DUMP = "--dump" in sys.argv
tree = ast.parse(open(SRC).read())

# (word, keyword) -> the keys of the object the producer passes, when it is not a dict literal at the call site.
# (word, "**name") -> the keys the ** expansion writes unconditionally.
EXPANSIONS = {
    ("reported_cell", "**primary"): ("status", "mean_j", "h_j", "B_j", "lower_j", "upper_j"),  # _cell_values :271 (pinned)
    ("battery_assist_cell", "primary"): ("status", "mean_j", "h_j", "B_j", "lower_j", "upper_j"),  # _cell_values
    ("battery_assist_cell", "without"): ("status",),  # _descriptive_cell or dict(primary): status always; values when computed
    ("battery_assist_cell", "assist_members"): (),  # Counter: keys are strata present
    ("primary_contrast", "estimator"): tuple(cmp.ENGINE_KEYS["estimator"]),  # _plain(verdict["estimator"]) (pinned)
    ("primary_contrast", "decision_interval"): ("lower", "upper"),  # verdict deterministic_bounds.decision_interval
    ("battery_assist_contrast", "**value"): ("status", "n"),  # _paired_values :340 (estimates conditional, F5)
    ("magnitude_per_token", "metrology"): ("lower", "upper"), ("magnitude_per_token", "decision"): ("lower", "upper"),
    ("decision_floor", "decision_interval"): ("lower", "upper"),
    ("dominance_ratio", "**values"): ("cell_id", "component", "n", "status"),  # :1146 (ratio keys conditional, F5)
    ("sensitivity_bmax", "**bmax"): ("value_s", "T", "attained_by_sequence"),  # bracket.BMax (pinned)
    ("sensitivity_window", "**row"): ("plan_id", "b_op_s", "b_sens_s", "widened"),  # sensitivity.py row (pinned SENSITIVITY_KEYS)
    ("corpus_counts", "**corpus"): ("collected", "in_window", "deciding", "desk_cap", "drop_counts"),  # :999
    ("corpus_counts", "drop_counts"): ("status", "desk_cap"),  # dropped_counts (pinned CORPUS_DROPS)
    ("battery_counts", "counts"): tuple(cmp.BATTERY_CODES),  # :925 counts per registered code
    ("reference_counts", "counts"): ("start", "midpoint", "end"), ("reference_counts", "planned"): ("start", "midpoint", "end"),
    ("neg8_allowance", "values_j"): tuple(cmp.NEG8_TERM + t for t in cmp.NEG8_TERMS),  # :1022 seven registered terms
    ("erratum3_triggers", "values"): (),  # None or the trigger object (F5 gate)
    ("deciding_membership", "**counts"): ("deciding_references", "deciding_spares", "writer_excluded_count"),  # :1199
    ("corpus_counts", "drop_counts"): ("status", "desk_cap"),  # dropped_counts (pinned CORPUS_DROPS)
    ("stored_member_reason", "**values"): (),
    ("machine_summary", "**values"): (), ("machine_member", "**values"): (), ("battery_temperature", "**values"): (),
    ("attempt_history", "**values"): (), ("reharvest_account", "**fields"): (), ("reference_lost", "**values"): (),
    ("g10", "**values"): (), ("flag_count", "**values"): (),
}


def section(target):
    keys = []
    while isinstance(target, ast.Subscript):
        keys.append(target.slice)
        target = target.value
    return (keys[-1].value if isinstance(keys[-1], ast.Constant) else "*") if keys else None


calls = {}
for node in ast.walk(tree):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "append" and node.args:
        inner = node.args[0]
        if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Name) and inner.func.id == "_item" \
                and isinstance(inner.args[0], ast.Constant):
            word = inner.args[0].value
            kwargs = {k.arg: k.value for k in inner.keywords if k.arg is not None}
            stars = ["**" + (k.value.id if isinstance(k.value, ast.Name) else ast.unparse(k.value))
                     for k in inner.keywords if k.arg is None]
            calls.setdefault(word, []).append((inner.lineno, section(node.func.value), kwargs, stars))

# Lines printed through a variable word: the sensitivity rows (:1266, record=row: the record's own row, whose keys are
# pinned as SENSITIVITY_KEYS/SENSITIVITY_SHAPE) and the fixed sentences (FIXED_SENTENCES.items(): text only).
for word, section_name in (("sensitivity_reported", "reported_cells"), ("sensitivity_floor", "floor_cells"),
                           ("sensitivity_contrast", "contrasts")):
    calls[word] = [(1266, "block_lines", {"record": ast.Name(id="row")}, [])]
    keys = cmp.SENSITIVITY_KEYS[section_name]
    EXPANSIONS[(word, "record")] = tuple(sorted(set().union(*keys.values()))) if isinstance(keys, dict) else tuple(keys)
for word in cmp.FIXED_SENTENCE_WORDS + ("floor_drift_ownership", "gross_energy"):
    calls.setdefault(word, [(0, "fixed_sentences", {}, [])])
if DUMP:
    for word, found in sorted(calls.items()):
        for lineno, where, kwargs, stars in found:
            print(f"{where}/{word} :{lineno} " + ", ".join(f"{k}={ast.unparse(v)[:60]}" for k, v in kwargs.items())
                  + ("  " + " ".join(stars) if stars else ""))
    sys.exit()


def keys_of(word, name, value):
    """The unconditional nested keys of a keyword's value: a dict literal's constant keys, else EXPANSIONS."""
    if isinstance(value, ast.Dict) and all(isinstance(k, ast.Constant) for k in value.keys):
        return tuple(k.value for k in value.keys)
    return EXPANSIONS.get((word, name))


required, selectors, conditional = {}, {}, {}
for entry in cmp.expected_checks(cmp.load_registry()):
    for locator in entry["l9"]:
        for label, path, paths in (locator[1] if locator[0] == "any" else (locator,)):
            if label == "disclosure" and path and isinstance(path[-1], dict) and "line" in path[-1]:
                word = path[-1]["line"]
                required.setdefault(word, set()).update(paths)
                if entry["condition"] is not None:
                    conditional.setdefault(word, set()).update(paths)
                selectors.setdefault(word, set()).update(k for k in path[-1] if isinstance(k, str))
                selectors[word].update(k[0] for k in path[-1] if isinstance(k, tuple))

risks, gaps, unresolved = [], [], []
for word in sorted(required):
    found = calls.get(word)
    if not found:
        risks.append(f"{word}: no _item call in the producer")
        continue
    # Unconditional = present in every _item call of the word (the sensitivity rows print through a variable word).
    tops, nested = None, {}
    for lineno, where, kwargs, stars in found:
        keys = set(kwargs)
        for star in stars:
            resolved = EXPANSIONS.get((word, star))
            if resolved is None:
                unresolved.append(f"{word} :{lineno} {star}")
                resolved = ()
            keys |= set(resolved)
            for key in resolved:
                nested.setdefault(key, EXPANSIONS.get((word, key)))
        for name, value in kwargs.items():
            nested[name] = keys_of(word, name, value)
        tops = keys if tops is None else tops & keys
    for path in sorted(required[word]):
        top = path[0]
        if path in conditional.get(word, set()) or top in cmp.LINE_COMMON:
            continue  # a declared conditional entry (its registered condition), or _item's positional text
        if top not in tops:
            risks.append(f"{word}/{'/'.join(path)}: not written on every _item call of the word (calls {[l for l, *_ in found]})")
        elif len(path) > 1:
            inner = nested.get(top)
            if inner is None:
                unresolved.append(f"{word}/{top}: nested value unresolved for path {'/'.join(path)}")
            elif path[1] not in inner:
                risks.append(f"{word}/{'/'.join(path)}: nested key not unconditional in the producer ({inner})")
    for top in sorted(tops - {p[0] for p in required[word]} - selectors.get(word, set()) - set(cmp.LINE_COMMON)):
        gaps.append(f"{word}/{top}")
    for top in sorted(tops):
        inner = nested.get(top)
        if inner:
            have = {p[1] for p in required[word] if len(p) > 1 and p[0] == top}
            for key in set(inner) - have:
                if not any(p == (top,) for p in required[word]) or top in ("primary", "without", "estimator", "counts", "planned", "values_j", "drop_counts", "metrology", "decision", "decision_interval"):
                    gaps.append(f"{word}/{top}/{key} (nested; the table requires {('/'.join((top,)+tuple(sorted(have)))) if have else top + ' as a key only'})")

print(f"line words in the table: {len(required)}; producer _item words: {len(calls)}")
print("declared conditional paths (skipped in the risk pass):",
      {w: sorted('/'.join(p) for p in ps) for w, ps in sorted(conditional.items())})
print("\nOVER-REFUSAL RISKS (required path not unconditional in the producer):", len(risks))
for r in risks:
    print("  ", r)
print("\nGAPS (producer-unconditional key or nested key the table does not require):", len(gaps))
for g in gaps:
    print("  ", g)
print("\nUNRESOLVED (needs a manual expansion):", len(unresolved))
for u in unresolved:
    print("  ", u)
print("\nproducer line words not in the table (conditional lines, by the producer's own branches):",
      sorted(set(calls) - set(required)))
