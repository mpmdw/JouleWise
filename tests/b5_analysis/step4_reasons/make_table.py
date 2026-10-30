"""Blind classification of every reason-code literal on the step-4 extractor's path (Ed approved, 2026-10-30).

Written and committed before any blinded output was read. MASK: codes that encode a numeric comparison of a
measured quantity against a threshold (printed only as "outcome-class"). TOOLING: every other code literal on the
path (integrity, provenance, wiring, missing or invalid inputs; R3-curable), printed by name. A code in neither set
prints as "unclassified" and counts as needing a cure (fail-closed toward cure-and-rerun).
"""
import ast, json, re, sys
from pathlib import Path

MODULES = ('joulewise/floor_extraction.py', 'joulewise/whole_window.py', 'joulewise/environment_admission.py',
           'joulewise/uncertainty_evidence.py', 'joulewise/arm_readiness.py', 'joulewise/bundle_read.py',
           'joulewise/detection_floor.py', 'joulewise/reduce.py', 'joulewise/authentication_io.py',
           'joulewise/window_lineage.py', 'joulewise/analysis_engine/inputs.py')
CODE = re.compile(r'[a-z][a-z0-9]*(_[a-z0-9]+)+')
MASK = re.compile(r'exceed|below|above|dominat|insufficient|outside_calibrated|stale|minimum|too_|harder_than')

root = Path(sys.argv[1])
codes = set()
for module in MODULES:
    for node in ast.walk(ast.parse((root / module).read_text())):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and CODE.fullmatch(node.value):
            codes.add(node.value)
table = {'modules': MODULES, 'mask_rule': MASK.pattern,
         'mask': sorted(c for c in codes if MASK.search(c)),
         'tooling': sorted(c for c in codes if not MASK.search(c))}
print(json.dumps(table, indent=1, sort_keys=True))
