"""Comparator mechanics on the synthetic rehearsal (no real data): coverage, families, R-C1..R-C6, R22-3.

The baseline is the full rehearsal (zero-capture retries in C3 and T2, the A37 <= 1 us seam window, the
W1/B screen fixtures). Both builds agree exactly on it, so each planted mutation below must turn a named
family away from agree.
"""
import copy
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import support  # noqa: E402

sys.path.insert(0, str(support.REPO / "scripts"))
import compare_v4_recompute as cmp  # noqa: E402

KNOWN_DISAGREEMENTS = set()     # the full rehearsal agrees exactly (RELEASE-RUNBOOK-v4.md section 6)


@unittest.skipUnless(support.have_commits(), "pinned build commits unavailable in this clone")
class ComparatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = support.rehearsal("full")
        cls.tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls.tmp.name)
        cls.fill = json.loads((cls.base / "engine-out" / "fill.json").read_text())
        cls.rec = json.loads((cls.base / "recompute-out.json").read_text())
        cls.cross = json.loads((cls.base / "crosswalk.json").read_text())
        cls.code, cls.public, cls.restricted = support.compare(cls.base, cls.dir / "baseline.json")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_with(self, name, fill=None, rec=None, cross=None, bars=None):
        paths = {}
        for key, doc in (("fill", fill), ("recompute", rec), ("crosswalk", cross), ("bars", bars)):
            if doc is not None:
                p = self.dir / f"{name}-{key}.json"
                p.write_text(json.dumps(doc))
                paths[key] = p
        if fill is not None:
            # keep the engine's own inventory consistent with the planted fill (the comparator checks it)
            body = {k: v for k, v in fill.items() if k != "leaf_inventory"}
            fill["leaf_inventory"] = [dict(pointer=p, kind="null" if v is None else "bool" if type(v) is bool
                                           else "number" if type(v) in (int, float) else "string")
                                      for p, v in cmp.leaves(body).items()]
            paths["fill"].write_text(json.dumps(fill))
        return support.compare(self.base, self.dir / f"{name}-out.json", **paths)

    def fam(self, public, name):
        return public["families"][name]["verdict"]

    # ---------------------------------------------------------------- baseline
    def test_baseline_every_leaf_mapped_and_only_known_families_disagree(self):
        self.assertEqual(self.public["unmapped_leaves"], 0)
        bad = {k for k, v in self.public["families"].items() if v["verdict"] not in
               ("agree", "exempt", "integrity_only", "expected_empty")}
        self.assertEqual(bad, KNOWN_DISAGREEMENTS)
        self.assertEqual(self.code, 0)
        self.assertEqual(self.public["verdict"], "agree")
        self.assertRegex(self.public["summary"], r"^\d+ families compared, \d+ expected-empty, 0 unexplained-empty$")

    def test_public_line_is_structure_only(self):
        text = json.dumps(self.public)
        sys.path.insert(0, str(support.REPO / "scripts"))
        import release_v4
        self.assertIsNone(release_v4.FLOAT_TOKEN.search(text))
        self.assertNotIn("rows", self.public)

    def test_core_families_agree_exactly(self):
        for name in ("turn_owned_energy_j", "scores", "thresholds_rank", "thresholds_value", "test_counts",
                     "eligible_m_per_pair", "member_eligibility", "fit_coefficients", "carrier_bootstrap",
                     "u3_bar_values", "u4", "u5", "u6", "dc_sealed", "supplemental_sentinels", "balance_by_condition",
                     "sensitivity_lines", "w1_contrast", "known_h_doses"):
            self.assertEqual(self.fam(self.public, name), "agree", name)

    def test_every_family_is_classified(self):          # R-C3
        for name, f in self.public["families"].items():
            self.assertIn(f["classification"], cmp.CLASSES, name)
        self.assertTrue(self.restricted["coverage_map"])

    # ---------------------------------------------------------------- DISAGREE
    def test_engine_energy_mutation_disagrees(self):
        fill = copy.deepcopy(self.fill)
        row = fill["fits"][0]["scores"][0]
        row["measured_j"] *= 1 + 1e-6
        code, pub, _ = self.run_with("energy", fill=fill)
        self.assertEqual(self.fam(pub, "turn_owned_energy_j"), "hold")
        self.assertEqual(code, 1)

    def test_recompute_threshold_rank_mutation_disagrees(self):     # R-C6: ranks exactly
        rec = copy.deepcopy(self.rec)
        rec["calibration"]["thresholds"]["logged"]["spam"]["rank_used"] -= 1
        code, pub, _ = self.run_with("rank", rec=rec)
        self.assertEqual(self.fam(pub, "thresholds_rank"), "hold")

    def test_bootstrap_compared_exactly(self):
        fill = copy.deepcopy(self.fill)
        fill["benign_carriers"]["pairs"]["spam"]["bootstrap_undefined_replicates"]["H90"] += 1
        code, pub, _ = self.run_with("boot", fill=fill)
        self.assertEqual(self.fam(pub, "carrier_bootstrap"), "hold")

    def test_sealed_dc_rows_by_presence_only(self):
        fill = copy.deepcopy(self.fill)
        sealed = [r for r in fill["dc_secondary"] if r.get("status") == "sealed"]
        sealed[0]["sha256"] = "0" * 64           # a different hash is fine: presence only
        code, pub, _ = self.run_with("seal-hash", fill=fill)
        self.assertEqual(self.fam(pub, "dc_sealed"), "agree")
        rec = copy.deepcopy(self.rec)
        for w in rec["dc_in"]["windows"].values():
            for m in w["members"].values():
                m.pop("sealed_sha256", None)
        code, pub, _ = self.run_with("seal-gone", rec=rec)
        self.assertEqual(self.fam(pub, "dc_sealed"), "hold")

    def test_balance_family_sees_an_eligibility_flip(self):       # R22-3
        fill = copy.deepcopy(self.fill)
        w = next(w for w in fill["windows"] if w["window"] == "C2")
        row = next(r for r in w["eligibility"] if r["eligible"] and r["pool_eligible"])
        row["eligible"] = False
        code, pub, res = self.run_with("balance", fill=fill)
        self.assertEqual(self.fam(pub, "member_eligibility"), "hold")
        self.assertEqual(self.fam(pub, "balance_by_condition"), "hold")
        self.assertTrue(res["balance"])
        self.assertTrue(all("exposure_adjusted_expected_excluded" in b for b in res["balance"]))

    # ---------------------------------------------------------------- REFUSE
    def test_unmapped_leaf_refuses(self):
        fill = copy.deepcopy(self.fill)
        fill["U5"]["new_statistic_j"] = 1.5
        code, pub, res = self.run_with("unmapped", fill=fill)
        self.assertEqual((code, pub["verdict"], pub["reason"]), (2, "refused", "unmapped_leaf"))
        self.assertEqual(res["unmapped"], ["/fill/U5/new_statistic_j"])

    def test_eligible_m_per_pair_mismatch_refuses(self):         # R-C5
        fill = copy.deepcopy(self.fill)
        fill["calibration"]["eligible_by_pair"]["spam"] -= 1
        code, pub, _ = self.run_with("m", fill=fill)
        self.assertEqual((code, pub["verdict"], pub["reason"]), (2, "refused", "refusing_family_disagrees"))
        self.assertEqual(self.fam(pub, "eligible_m_per_pair"), "refused")

    def test_engine_refusal_and_bad_bars_refuse(self):
        verdict = dict(schema="joulewise.align_v4.analysis_verdict.v1", status="refused", codes=["input_refused"])
        p = self.dir / "refused-verdict.json"
        p.write_text(json.dumps(verdict))
        code, pub, _ = support.compare(self.base, self.dir / "refused-out.json", verdict=p)
        self.assertEqual((code, pub["reason"]), (2, "engine_refused"))
        bars = json.loads((support.REPO / "configs/analysis/v4/recompute_bars.json").read_text())
        bars["families"]["scores"]["bar"] = -1
        code, pub, _ = self.run_with("bars", bars=bars)
        self.assertEqual((code, pub["reason"]), (2, "bars_malformed"))

    # ---------------------------------------------------------------- HOLD: empty family, row counts
    def test_empty_family_holds(self):                            # R-C1
        fill = copy.deepcopy(self.fill)
        fill.pop("U6")
        code, pub, _ = self.run_with("empty", fill=fill)
        self.assertEqual(self.fam(pub, "u6"), "hold_empty")
        self.assertEqual(self.fam(pub, "u6_values"), "hold_empty")
        self.assertRegex(pub["summary"], r"[1-9]\d* unexplained-empty$")
        self.assertEqual(code, 1)

    def test_expected_empty_needs_its_predicate(self):            # R-C1
        fill, cross = copy.deepcopy(self.fill), copy.deepcopy(self.cross)
        # Plant a series without escalation: drop ordinals 23/24 everywhere.
        drop = {m["engine_run_id"] for m in cross["members"] if m["ordinal"] in (23, 24)}
        cross["members"] = [m for m in cross["members"] if m["ordinal"] not in (23, 24)]
        for w in fill["windows"]:
            w["eligibility"] = [r for r in w["eligibility"] if r["run_id"] not in drop]
            w.pop("supplemental_sentinels", None)
        for k in ("realized_counts", "cache_diagnostics", "dc_secondary"):
            fill[k] = [r for r in fill[k] if r["run_id"] not in drop]
        code, pub, _ = self.run_with("noesc", fill=fill, cross=cross)
        self.assertEqual(self.fam(pub, "supplemental_sentinels"), "expected_empty")
        # Same emptiness while the crosswalk still has an escalated window: the predicate fails -> hold.
        code, pub, _ = self.run_with("noesc-cross", fill=fill)
        self.assertEqual(self.fam(pub, "supplemental_sentinels"), "hold_empty")

    def test_row_count_outside_manifest_holds(self):              # R-C2
        fill = copy.deepcopy(self.fill)
        f = next(f for f in fill["fits"] if f["window"] == "T1" and f["convention"] == "counts_logged")
        f["scores"] = f["scores"][1:]
        code, pub, res = self.run_with("partial", fill=fill)
        self.assertEqual(self.fam(pub, "turn_owned_energy_j"), "hold_row_count")
        self.assertIn("manifest", res["families"]["turn_owned_energy_j"])

    def test_uncomputable_sensitivity_line_holds(self):            # R-C4
        fill = copy.deepcopy(self.fill)
        fill["U5"]["beta_T_j_per_c"] = None
        code, pub, _ = self.run_with("u5", fill=fill)
        self.assertEqual(self.fam(pub, "sensitivity_lines"), "hold")


class BarTests(unittest.TestCase):
    def test_log_relative_bar_separates_small_p_values(self):     # R-C6
        self.assertFalse(cmp.within("log_rel", 1e-6, 1e-11, 1e-15))
        self.assertFalse(cmp.within("abs", 1e-6, 1e-11, 1e-15) is False)   # the B5 absolute bar could not
        self.assertTrue(cmp.within("log_rel", 1e-6, 1e-11, 1e-11 * (1 + 1e-7)))

    def test_exact_and_set_and_presence(self):
        self.assertFalse(cmp.within("exact", None, True, 1))
        self.assertTrue(cmp.within("set", None, ["b", "a"], ["a", "b"]))
        self.assertTrue(cmp.within("presence", None, "x", True))
        self.assertTrue(cmp.within("rel", 1e-9, None, None))
        self.assertFalse(cmp.within("rel", 1e-9, None, 1.0))
        self.assertFalse(cmp.within("rel", 1e-9, math.nan, 1.0))


if __name__ == "__main__":
    unittest.main()
