# Adapted from JouleWise-data 6039fff; exercised by ReviewerProbeTests.
"""P02: Bonferroni levels and degrees of freedom; H2 primary family against Addendum 3 items 6, 7, 9.

cd /tmp/jw && JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/jwtmp python3.13 <this>
"""
import json
import math
import random
import sys

sys.path.insert(0, ".")
from joulewise import bytes_analysis as ba
from joulewise.analysis_engine.distributions import student_t_quantile as tq

print("H1 family:", ba.H1_CHECKS, "-> t level 1-0.05/(2*21) =", 1 - .05 / 42)
for df in (9, 8, 7, 4):
    print(f"  df={df}: t_H1={tq(1 - .05 / 42, df):.6f}  (t.975={tq(.975, df):.6f})")

print("\nH2 family in code: H2_INTERVALS =", ba.H2_INTERVALS, "(per boundary)")
print("Addendum 3 item 6: k=9 rails, k=9 DC input, k=11 rest (per boundary)")
for df, label in ((8, "simple eps n=10"), (7, "extended n=10"), (4, "tier one-term n=6 (old)"), (3, "tier two-term n=6 (spec)")):
    c, s9, s11 = tq(1 - .05 / 46, df), tq(1 - .05 / 18, df), tq(1 - .05 / 22, df)
    print(f"  {label:26s} df={df}: old t(k=23)={c:.4f}  spec t(k=9)={s9:.4f} ({c / s9 - 1:+.1%})  spec t(k=11)={s11:.4f} ({c / s11 - 1:+.1%})")

# Ten production-shaped points (pilot-scale regressors from the fixture), bytes world + noise.
design = ba.read_json("tests/fixtures/bytes/campaign_design.json")
rng = random.Random(7)
pts = {b: [] for b in ba.BOUNDARIES}
for m in design["models"]:
    b = (m["W_bytes"] + m["KV_bytes"]) / 1e9
    T = m["synthetic_duration_s"]
    rails = 0.01 * b * 511 / T * (1 + rng.gauss(0, .01)) + 3
    dc = 2 * rails + 5 + rng.gauss(0, .1)
    for boundary, p in (("rails", rails), ("DC input", dc), ("rest", dc - rails)):
        pts[boundary].append({"model": m["model"], "boundary": boundary, "BW": b * 511 / T, "power": p,
                              "resident": m["R_bytes"] / 1e9, "time": T / 511, "tier": m["tier"]})
rails_power = {p["model"]: p["power"] for p in pts["rails"]}
for boundary in ba.BOUNDARIES:
    out = ba.h2(pts[boundary], rails_power)
    terms = [p["term"] for p in out["primary_intervals"]]
    print(f"\n{boundary}: code primary terms ({len(terms)}): {terms}")
    print(f"  tier fit coefficients (code): {len(out['tier']['coefficients'])} -> [P0, epsilon, rho]")
    print(f"  extended eps in primary list: {'extended_epsilon' in terms}; family_size used: {out['two_term']['family_size']}")
    if out["rest"]:
        keys = sorted(k for k in out["rest"])
        print("  rest record keys:", keys, "| VIF printed:", any("vif" in k.lower() for k in json.dumps(out).split('"')))
print("\nspec (A3 item 6) per boundary: eps, ext eps, ext rho, tier eps, tier rho, 4 deviations (+ rest eps_rest, lambda)")
