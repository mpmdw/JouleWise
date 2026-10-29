"""RC-CMP8-FABLE-REV: the required-key tables against the producers on origin/main (read as text, AST only).

For each compared line word, the keys the producer's _item call passes literally, plus the keys of each **expansion
resolved from the producer's own dict builder (table below, with the producer line). A required key that is not
unconditional in the producer is an over-refusal route; a producer-unconditional key that is not required is a
key the comparator never requires.
"""
import ast
import sys

sys.path.insert(0, "/home/user/JouleWise")
from scripts import compare_b5_recompute as cmp  # noqa: E402

SRC = "/tmp/claude-0/rcfable8/producers/disclosures_b5_analysis.py"
tree = ast.parse(open(SRC).read())

# **name expansions in _item calls, resolved by reading the builder (disclosures.py line in the comment).
EXPANSIONS = {
    ("cells", "reported_cell", "primary"): ("status", "mean_j", "h_j", "B_j", "lower_j", "upper_j"),  # _cell_values :271
    ("contrasts", "battery_assist_contrast", "value"): ("status", "n"),  # _paired_values :340 (estimates conditional)
    ("block_lines", "dominance_ratio", "values"): ("cell_id", "component", "n", "status"),  # :1148 (ratio keys conditional)
    ("block_lines", "sensitivity_bmax", "bmax"): ("value_s", "T", "attained_by_sequence"),  # bracket.BMax, sensitivity.py :275
    ("block_lines", "sensitivity_window", "row"): ("plan_id", "b_op_s", "b_sens_s", "widened"),  # sensitivity.py :276-279
    ("window_lines", "corpus_counts", "corpus"): ("collected", "in_window", "deciding", "desk_cap", "drop_counts"),  # :999
    ("window_lines", "machine_summary", "values"): (),  # :666-688: every statistic conditional
    ("window_lines", "battery_temperature", "values"): None,  # not a compared line
    ("block_lines", "attempt_history", "values"): None, ("block_lines", "reharvest_account", "fields"): None,
    ("window_lines", "reference_lost", "values"): None, ("window_lines", "deciding_membership", "counts"): None,
    ("window_lines", "stored_member_reason", "values"): None,
}


def section_of(node):
    """result["cells"].append(_item(...)) -> cells; result["window_lines"][pack] -> window_lines; result[section] -> ?"""
    target = node.func.value if isinstance(node.func, ast.Attribute) else None
    while isinstance(target, ast.Subscript):
        inner = target.value
        if isinstance(target.slice, ast.Constant) and isinstance(inner, ast.Name) and inner.id == "result":
            return target.slice.value
        target = inner
    return "?"


calls = {}
for node in ast.walk(tree):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "append" and node.args:
        inner = node.args[0]
        if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Name) and inner.func.id == "_item" and inner.args:
            word = inner.args[0].value if isinstance(inner.args[0], ast.Constant) else None
            if word is None:
                continue
            section = section_of(node)
            literal = tuple(k.arg for k in inner.keywords if k.arg is not None)
            stars = tuple(k.value.id if isinstance(k.value, ast.Name) else ast.unparse(k.value)
                          for k in inner.keywords if k.arg is None)
            calls.setdefault((section, word), []).append((inner.lineno, literal, stars))

# kept_units is appended through result[section] (:721); it is not a compared line.
print("producer _item calls found:", sum(len(v) for v in calls.values()))
problems = []
for (section, word), required in sorted(cmp.REQUIRED_KEYS.items()):
    found = calls.get((section, word), [])
    if not found:
        problems.append(f"{section}/{word}: no _item call found under result[{section!r}]")
        continue
    unconditional = None
    for lineno, literal, stars in found:
        keys = set(literal)
        for star in stars:
            resolved = EXPANSIONS.get((section, word, star))
            if resolved is None:
                problems.append(f"{section}/{word} :{lineno}: unresolved **{star}")
                resolved = ()
            keys |= set(resolved)
        unconditional = keys if unconditional is None else unconditional & keys
    missing = [k for k in required if k not in unconditional]
    extra = sorted(unconditional - set(required) - set(cmp.LINE_COMMON))
    status = "OK" if not missing else "OVER-REFUSAL RISK"
    print(f"{section}/{word}: required={list(required)} producer_unconditional={sorted(unconditional)} "
          f"lines={[l for l, _, _ in found]} -> {status}" + (f" missing_in_producer={missing}" if missing else "")
          + (f" producer_keys_not_required={extra}" if extra else ""))
for p in problems:
    print("NOTE:", p)
print()
print("fixed-size producer lines never required by any pairing (unconditional per key in the producer, see report):")
for sec, word, where in (("contrasts", "primary_contrast", ":482"), ("contrasts", "contrast_interval", ":537"),
                         ("contrasts", "decision_floor", ":546"), ("cells", "attribution_floor", ":429"),
                         ("block_lines", "sensitivity_bmax", ":1245"), ("block_lines", "sensitivity_window", ":1250"),
                         ("block_lines", "sensitivity_reported", ":1266"), ("block_lines", "sensitivity_floor", ":1266"),
                         ("block_lines", "sensitivity_contrast", ":1266"), ("block_lines", "dominance_ratio", ":1157"),
                         ("block_lines", "dominance_branch", ":1159 (if branch in closeout)")):
    print(f"  {sec}/{word} {where}")
