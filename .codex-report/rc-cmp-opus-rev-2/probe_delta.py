"""RC-CMP-OPUS-REV-2: new false-agreement probes against e5ccf720b (synthetic fixtures only).

Run from the repo root:
TMPDIR=/tmp/rcopusrev2 PYTHONPATH=.:tests PYTHONDONTWRITEBYTECODE=1 python3.13 .codex-report/rc-cmp-opus-rev-2/probe_delta.py
"""
import copy
import json
import sys
import unittest
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parents[2]), str(Path(__file__).resolve().parents[2] / "tests")]
from tests.independent_recompute import test_review_fixes as t  # noqa: E402

cmp, FILL, DISCLOSURE, BARS = t.cmp, t.FILL, t.DISCLOSURE, t.BARS["recompute_coded_7e322b76"]
RATIO_TABLE = "finalized/outputs/closeout.ratio-table.json"


def show(name, case, bars=BARS, meter=()):
    code, err, out = case.exit_code(bars, meter)
    cover = out.get("coverage", {})
    print(f"{name}: exit={code} stderr={err.strip()!r} fails={case.fails(out) if 'counts' in out else None} "
          f"unbound={[(u['path'], u['reason']) for u in cover.get('unbound', [])]} "
          f"flags={[f['code'] for f in out.get('structure_flags', [])]}")
    return out


class Probes(t.Case):
    def runTest(self):
        base = copy.deepcopy((self.files, self.ours))

        def reset():
            self.files, self.ours = copy.deepcopy(base)

        show("N0 baseline", self)

        # N1: a NaN printed under an uncovered: catch-all is read as null, which is not numeric,
        # so the catch-all takes it (X6 only sends *numbers* past an uncovered: rule).
        self.files[FILL]["campaigns"] = {"gamma": {"gross_energy_j": 123.4}}
        show("N1a control: number under fill:campaigns catch-all", self)
        self.files[FILL]["campaigns"] = {"gamma": {"gross_energy_j": float("nan")}}
        show("N1b NaN under fill:campaigns catch-all", self)
        reset()
        self.files[FILL]["gamma"]["contrasts"][0]["j_per_token"] = float("inf")
        show("N1c Infinity printed as a J contrast's j_per_token", self)
        reset()
        self.files[FILL]["gamma"]["contrasts"][0]["sampling"] = {"planned_n": float("nan")}
        out = show("N1d NaN under an uncovered-by-name rule", self)
        print("    uncovered_numeric lists it:", any("planned_n" in p for p in out["coverage"]["uncovered_numeric"]),
              "leaf report:", out["coverage"]["leaves"].get("fill:gamma/contrasts/*/sampling/planned_n", "")[:30])
        reset()

        # N2: (count, <model>/<phase>/absolute/n) is emitted twice: by the floor cell (compare_floors)
        # and by the dominance ratio whose component is 'absolute' (compare_aggregate). coverage()
        # keeps the first row, so the dominance-ratio line's n binds to the floor cell's n.
        keys = [(r["family"], r["key"]) for r in self.shipped()["comparisons"]]
        print("N2 duplicated row keys:", sorted({k for k in keys if keys.count(k) > 1}))
        self.files[RATIO_TABLE]["ratios"][0]["n"] = 7
        self.ours["dominance"]["ratios"]["Qwen3-1.7B-4bit/decode/absolute"]["n"] = 7

        def ratio_line(n):
            row = self.files[RATIO_TABLE]["ratios"][0]
            self.files[DISCLOSURE]["block_lines"] = [{
                "line": "dominance_ratio", "cell_id": row["cell_id"], "component": "absolute",
                "text": "alpha decode: R 1.0395 (synthetic)", "ratio": row["ratio"],
                "numerator_j": row["numerator_j"], "denominator_j": row["denominator_j"], "n": n}]
        ratio_line(9)
        show("N2a ratio line prints the floor cell's n=9 (ratio n is 7 on both sides)", self)
        ratio_line(7)
        show("N2b ratio line prints the correct ratio n=7", self)
        reset()


class Band(t.MeterCase):
    def runTest(self):
        result = self.compare()
        print("N3 baseline meter fixture:", self.fails(result), result["coverage"]["unmapped"])
        summary = next(l for l in self.lines() if l.get("line") == "machine_summary")
        print("    L9 band:", {k: summary["central_band"].get(k) for k in ("pack",)})
        wm = self.case.ours["disclosures"]["whole_machine"]
        models = wm.setdefault("request_cross_check", {}).setdefault("windows", {}).setdefault("ALPHA", {}).setdefault("models", {})
        print("    recompute's own band rows:", json.dumps(models)[:200])
        # The recompute sets no band (it found no clean window); L9 prints one.
        for m in list(models) or [summary["model"]]:
            models.setdefault(m, {})["central_band"] = None
        result = self.compare()
        print("N3a recompute sets no central band, L9 prints one:", self.fails(result), result["coverage"]["unmapped"])
        # The recompute names a different clean window for the band.
        for m in list(models):
            models[m]["central_band"] = {"pack": "BETA", "lower": 0.5, "upper": 0.6}
        result = self.compare()
        print("N3b recompute's band is BETA's, L9's is alpha's:", self.fails(result), result["coverage"]["unmapped"])


Probes.setUpClass(); p = Probes(); p.setUp(); p.runTest()
Band.setUpClass(); b = Band(); b.setUp(); b.runTest(); Band.tearDownClass()
