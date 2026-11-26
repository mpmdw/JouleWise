"""Seat test of step3_project.py on a step3-shaped object built by the pinned adapter itself (synthetic numbers)."""
import json, subprocess, sys, tempfile, os
sys.path.insert(0, "/Volumes/JW-EXT/jw-wt/lm-interim-exec")
from joulewise.cadence_looks import step3_roster as S3

class Fake:
    """Stands in for the pinned step-3 module: returns analyse()-shaped output with made-up numbers."""
    def __init__(self, table): self.table = table; self.LEGS = []; self.ORIGINAL_EIGHT = []
    def analyse(self, roots):
        ids = list(roots)
        g, rise = self.table[len(ids)]
        return {"legs": [{"leg_id": i, "SECRET_per_leg": 123.456} for i in ids],
                "ii_gamma_per_degC": {"all_nine_legs": {"slope": g, "se": 0.001, "n_obs": 9, "n_groups": 3, "n_groups_with_2plus": 3},
                                      "leave_one_leg_out": {i: g * (1 + 0.01 * k) * (-1 if (len(ids) == 11 and k == 0) else 1) for k, i in enumerate(ids)},
                                      "without_two_high_power_legs": {"slope": g, "se": 0.001},
                                      "original_eight_legs_record_only": {"slope": g}, "max_abs_over_reported": abs(g) * 1.2},
                "gamma_estimability": {"estimable": True, "max_range_c": 9.0},
                "iii_precut_drift": {"median_tv0h_rise_c": {"six_automatic_legs": rise, "seven_automatic_legs_incl_partc": rise},
                                     "drift_fraction_linear": {"six_automatic_legs": abs(g) * 1.2 * rise, "seven_automatic_legs_incl_partc": abs(g) * 1.2 * rise},
                                     "drift_fraction_exp_form": {"six_automatic_legs": abs(g) * 1.3 * rise, "seven_automatic_legs_incl_partc": abs(g) * 1.3 * rise}},
                "iv_jpt_after_over_before": {"per_leg": {i: 0.9 for i in ids}, "automatic_median": 0.91, "automatic_min": 0.85, "automatic_max": 0.96},
                "vi_slope_lnE_on_lnclock": {"all_blocks_k_ge_1_all_nine_legs": {"slope": 1.5}}}
    def custody_check(self, out): return None

table = {10: (-0.011, 7.7), 11: (0.004, 12.0), 12: (0.02, 6.0)}
entries = []
for size, n in ((10000, 10), (2000, 11), (19500, 12)):
    for k in range(n):
        entries.append({"key": f"leg-{size}-{k}", "day": "d%d" % (k % 4), "bundle": "/nowhere", "role": "fit", "leg_type": "A",
                        "included": True, "prompt_tokens_nominal": size})
step3 = S3.run_roster(entries, threshold=0.08, loader=lambda: Fake(table))
step3["custody"] = {"files": [{"path": "x/power_trace.csv", "sha256": "0" * 64}]}
tmp = tempfile.mkdtemp(dir=os.environ.get("TMPDIR"))
src, dst = os.path.join(tmp, "step3.json"), os.path.join(tmp, "out.json")
json.dump(step3, open(src, "w"))
here = os.path.dirname(os.path.abspath(__file__))
r = subprocess.run([sys.executable, "-I", "-B", os.path.join(here, "step3_project.py"), src, dst], capture_output=True, text=True)
print("rc", r.returncode, "| stdout fields:", len(r.stdout.split()), "| stderr empty:", r.stderr == "")
out = json.load(open(dst))
text = open(dst).read()
assert "SECRET" not in text and "leg-" not in text and "details" not in text and "se" not in out["cells"][0]
assert set(out) == {"schema", "source_sha256", "tripwire", "cells"}
assert [c["prompt_tokens"] for c in out["cells"]] == [10000, 2000, 19500]          # the adapter's order: 10k first
assert out["tripwire"]["cell"] == 19500 and out["tripwire"]["trips"] is True and out["tripwire"]["decision"] == "to the research lead"
assert [c["gamma_sign_all_legs"] for c in out["cells"]] == ["-", "+", "+"]
assert [c["gamma_signs_agree"] for c in out["cells"]] == [True, False, True]
assert all(set(c) == {"prompt_tokens", "status", "n_legs", "failed_legs", "gamma_estimable", "iii_drift_fraction_linear",
                      "iii_drift_fraction_exp_form", "gamma_sign_all_legs", "gamma_signs_agree", "gamma_fits_reported"} for c in out["cells"])
r2 = subprocess.run([sys.executable, "-I", "-B", os.path.join(here, "step3_project.py"), src, dst], capture_output=True, text=True)
assert r2.returncode == 1 and r2.stdout.strip() == "refused: FileExistsError", r2.stdout
r3 = subprocess.run([sys.executable, "-I", "-B", os.path.join(here, "step3_project.py"), src + ".missing", dst + "2"], capture_output=True, text=True)
assert r3.returncode == 1 and r3.stdout.strip() == "refused: FileNotFoundError"
print("projection keys per cell:", sorted(out["cells"][0]))
print("PASS")
