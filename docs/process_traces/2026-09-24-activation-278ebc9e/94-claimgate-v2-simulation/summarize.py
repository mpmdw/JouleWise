#!/usr/bin/env python3
"""Check the committed CG-4(e) Monte Carlo cell files and print stable tails."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
claims = [json.loads(line) for line in (HERE / "claims.jsonl").read_text().splitlines()]
nights = [json.loads(line) for line in (HERE / "nights.jsonl").read_text().splitlines()]

assert len(claims) == 24
assert all(row["N"] == 5000 for row in claims)
claim_null = max(row["rates"]["0"] for row in claims)
equivalence_boundary = max(row["equivalence_boundary_false_admission"] for row in claims)
assert claim_null <= 0.05
assert equivalence_boundary <= 0.05
print(f"CG1 cells={len(claims)} N=5000 max_false_admission={claim_null:.4f}")
print(f"CG2 cells={len(claims)} N=5000 max_boundary_false_admission={equivalence_boundary:.4f}")

fixed = [row for row in nights if row.get("variant") == "fixed"]
sensitivity = [row for row in nights if row.get("variant") == "simulated"]
assert len(fixed) == len(sensitivity) == 48
null = [row["rates"]["fail"] for row in fixed if row["state"] == "null"]
boundary = [row["pass_rate"] for row in fixed if row["state"] == "boundary"]
assert len(null) == len(boundary) == 8
assert max(null) <= 0.05
assert max(boundary) <= 0.05
assert all(row["N"] == 10000 for row in fixed if row["state"] in {"null", "boundary"})
assert all(row["N"] == 2000 for row in fixed if row["state"] not in {"null", "boundary"})
print("CG3 fixed_r7 cells=48 null_boundary_N=10000 permutations=2000")
print(f"CG3 no_change_false_FAIL_range={min(null):.4f}..{max(null):.4f}")
print(f"CG3 margin_false_PASS_range={min(boundary):.4f}..{max(boundary):.4f}")
print("CG3 simulated_old cells=48 N=2000 sensitivity_only")
print("SIMULATION_CHECKS_PASS")
