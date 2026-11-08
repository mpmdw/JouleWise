"""Replicate ci.yml's test/calibration job planning in the cwd tree; emit every test id per job.

Run with cwd = tree root. Imports test modules (to enumerate ids) but runs no test.
"""
import json, os, sys, unittest, collections
from pathlib import Path
sys.path.insert(0, "scripts")
import shard_tests as st

out = {"jobs": {}, "meta": {}}
overlay = json.loads(Path("scripts/test_timings.json").read_text())
exclusive = frozenset(overlay["exclusive_modules"])
discovered = st.discover_test_modules()
assert exclusive <= set(discovered)
timings = st.load_timing_map()
ordinary = tuple(m for m in discovered if m not in exclusive)
allsplits = st.load_split_declarations()
splits = {m: d for m, d in allsplits.items() if m in set(ordinary)}
unknown = st.conservative_unknown_weight()
units, weights = st.expand_units(ordinary, timings, splits, unknown_weight=unknown)
parts = st.partition_modules(units, weights, 12, unknown_weight=unknown)
totals = st.partition_totals(parts, weights, unknown_weight=unknown)
out["meta"]["n_discovered"] = len(discovered)
out["meta"]["exclusive"] = sorted(exclusive)
out["meta"]["ordinary_estimates"] = [round(t, 1) for t in totals]
out["meta"]["untimed_ordinary"] = sorted(m for m in ordinary if m not in timings and m not in splits)
out["meta"]["splits_active"] = sorted(splits)
out["meta"]["splits_declared"] = sorted(allsplits)
if hasattr(st, "forward_declaration_problems"):
    out["meta"]["forward_problems"] = st.forward_declaration_problems(allsplits, discovered)

st._ensure_import_paths()
loader = unittest.TestLoader()
id_cache = {}
def ids_of(module):
    if module not in id_cache:
        try:
            id_cache[module] = sorted(st.discover_test_ids(module))
        except Exception as exc:
            id_cache[module] = [f"{module}::IMPORT_ERROR::{type(exc).__name__}"]
    return id_cache[module]

def resolve(job, unit_list, all_splits):
    res = []
    for module, whole, unit_ids in st._group_units_by_module(unit_list):
        disc = ids_of(module)
        if whole:
            res.extend(disc)
        else:
            res.extend(st.resolve_units_to_test_ids(module, unit_ids, disc, all_splits.get(module, {}).get("declared", ())))
    out["jobs"][job] = res

for i, p in enumerate(parts, 1):
    resolve(f"test (3.13, {i})", p, allsplits)
mod = "tests.test_calibration_writer_crash_matrix"
u2, w2 = st.expand_units((mod,), timings, {mod: allsplits[mod]}, unknown_weight=unknown)
p2 = st.partition_modules(u2, w2, 2, unknown_weight=unknown)
for i, p in enumerate(p2, 1):
    resolve(f"calibration-writer-crash-matrix-exclusive (3.13, {i})", p, allsplits)
out["jobs"]["calibration-exits-exclusive (3.13)"] = ids_of("tests.test_calibration_exits")
covered = collections.Counter(t for v in out["jobs"].values() for t in v)
out["meta"]["dupes"] = sorted(t for t, c in covered.items() if c > 1)
alltests = set(t for m in discovered for t in ids_of(m))
out["meta"]["n_test_ids"] = len(alltests)
out["meta"]["uncovered"] = sorted(alltests - set(covered))
Path(sys.argv[1]).write_text(json.dumps(out, indent=1))
print(json.dumps(out["meta"], indent=1)[:3000])
