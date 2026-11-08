"""A full synthetic series (W1 + C1-C8 + T1-T3, D shape) through every stage. Synthetic only."""
import json
import math
import tempfile
import unittest
from pathlib import Path

from .support import SMALL, rc, synth


class SeriesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name) / "s"
        synth.write_series(cls.root, w1=True, saboteur_extra=25.0, **SMALL)
        # One C1 benign member gets a G1 timeout in its record only: X2 is re-derived, the recorded
        # flag set lacks it, so it is excluded and the mismatch is reported.
        ep = cls.root / "windows/C1/members/align-v4-c1-e06/outputs/align_episode.json"
        doc = json.loads(ep.read_text())
        doc["hardware"]["thermal"]["intervals"][1]["outcome"] = "timeout"
        ep.write_text(json.dumps(doc))
        cls.out = rc.recompute(cls.root, workers=4)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_structure_and_statuses(self):
        out = self.out
        self.assertEqual(out["schema"], rc.SCHEMA)
        self.assertEqual(len(out["members"]), 12)
        self.assertEqual(sum(len(v) for v in out["members"].values()), 18 + 11 * 22)
        self.assertEqual(out["calibration"]["stop"]["status"], "calibration_complete")
        self.assertEqual(out["calibration"]["stop"]["counted_windows"], 8)
        # 8 x 7 = 56 benign per pair, less the one X2 member in C1 (its pair).
        totals = out["calibration"]["stop"]["eligible_benign_totals"]
        pair = next(m["pair"] for m in synth.window_roster("C1", "calibration", 1) if m["ordinal"] == 6)
        self.assertEqual(totals[pair], 55)
        self.assertEqual(totals["bank" if pair == "spam" else "spam"], 56)
        for p in rc.PAIRS:
            thr = out["calibration"]["thresholds"]["logged"][p]
            self.assertEqual((thr["status"], thr["rank_used"], thr["m"]), ("ok", totals[p], totals[p]))
            self.assertTrue(thr["frozen"])
        self.assertEqual(out["claim"]["status"]["status"], "evaluable")
        self.assertEqual(out["claim"]["status"]["test_benign_n"], {"bank": 21, "spam": 21})

    def test_exclusion_rederivation(self):
        e = self.out["exclusions"]["C1"]["align-v4-c1-e06"]
        self.assertEqual((e["codes"], e["mismatch"], e["eligible"]), (["X2"], ["X2"], False))
        self.assertNotIn("align-v4-c1-e06", self.out["scores"]["C1"]["spam"]["logged"])
        self.assertNotIn("align-v4-c1-e06", self.out["scores"]["C1"]["bank"]["logged"])

    def test_fit_scores_and_thresholds_are_consistent(self):
        out = self.out
        for p in rc.PAIRS:
            pool = [out["scores"][w][p]["logged"][rid]["score"] for w in out["scores"] if w.startswith("C")
                    for rid, row in out["scores"][w][p]["logged"].items() if row["fit"] == "loto"]
            self.assertEqual(max(pool), out["calibration"]["thresholds"]["logged"][p]["threshold"])
            loto = out["fits"]["C2"][p]["logged"]["loto"]
            self.assertEqual(len(loto), 7)
            self.assertTrue(all(f["n_rows"] >= rc.MIN_FIT_ROWS for f in loto.values()))
        # Sabotage carries +25 J per turn and is scored on the full fit.
        sab = [row for w in out["scores"] for p in rc.PAIRS for row in out["scores"][w][p]["logged"].values()
               if row["fit"] == "full"]
        self.assertEqual(len(sab), 22)
        # Directional only: the 10 s test sampling smears turn energies, so no magnitude is asserted.
        benign = [row["score"] for w in out["scores"] for p in rc.PAIRS
                  for row in out["scores"][w][p]["logged"].values() if row["fit"] == "loto"]
        self.assertGreater(sum(r["score"] for r in sab) / len(sab), sum(benign) / len(benign))

    def test_acceptance(self):
        a = self.out["acceptance"]
        self.assertAlmostEqual(a["U3_bar"]["q"], 4.0898, places=3)
        self.assertEqual(len(a["U3"]["W1"]["pairs"]), 5)       # 4 x 30B + 1 x D (R14 N roster)
        self.assertEqual(len(a["U3"]["C1"]["pairs"]), 1)
        self.assertEqual(a["U1"]["C1"]["D"]["verdict"], "pass")
        self.assertEqual(a["U1"]["C1"]["D"]["g1h_timeouts"], 1)  # 1 of the window's G1 admissions
        self.assertEqual(a["U5"]["verdict"], "pass")
        self.assertIn(a["U4"]["status"], ("ok",))
        self.assertEqual(a["U4"]["per_window"]["W1"]["verdict"], "unevaluable")
        self.assertEqual(set(a["U6"]), {f"C{i}" for i in range(1, 9)} | {"T1", "T2", "T3"})

    def test_w1_contrast_present(self):
        c = self.out["claim"]["w1_contrast"]
        self.assertEqual(set(c["templates"]), {"X", "Y"})
        self.assertEqual(c["delta"]["df"], 3)
        self.assertGreater(c["delta"]["estimate"], 0.0)   # synthetic S arm: +8 J x 3 turns = +24 J

    def test_dc_in_is_print_only_and_sabotage_rows_are_sealed(self):
        dc = self.out["dc_in"]["C1"]
        self.assertTrue(dc["print_only"])
        row = dc["members"]["align-v4-c1-e07"]
        member = self.out["members"]["C1"]["align-v4-c1-e07"]
        # Constant 30 W meter over the whole episode span.
        self.assertAlmostEqual(row["dc_in_episode_j"], 30.0 * member["pm"]["gross_episode_s"], places=4)
        for rid, m in self.out["members"]["C1"].items():
            if m["condition"] != "benign" and dc["members"].get(rid):
                self.assertEqual(list(dc["members"][rid]), ["sealed_sha256"])

    def test_known_h_and_carrier_curve(self):
        claim = self.out["claim"]
        for p in rc.PAIRS:
            curve = claim["carrier_curve"][p]
            self.assertEqual(curve["status"], "ok")
            self.assertEqual(curve["fractions"]["0"]["detected"], 0)
            kh = claim["known_h"][p]
            self.assertEqual(len(kh), 11)       # one sabotage member per pair in each C and T window
            for rid, row in kh.items():
                self.assertEqual(row["rows"][0]["H"], 0)
                self.assertEqual(row["counts_toward"], "test" if row["role"] == "test" else "nothing")
                self.assertFalse(row["grid"]["0"].get("detection", False))

    def test_turn_energies_match_the_power_record(self):
        # The synthetic power is constant inside each sample; the reduced gross episode energy equals the
        # integral of the written samples over the episode span, re-derived here from the raw frames.
        rid = "align-v4-c2-e07"
        base = self.root / "windows/C2/members" / rid
        ep = json.loads((base / "outputs/align_episode.json").read_text())
        meta = json.loads((base / "metadata.json").read_text())
        frames = [f for f in (base / "raw/powermetrics.plist").read_bytes().split(b"\x00") if f.strip()]
        anchor = round(meta["uncertainty_evidence"]["clock_anchor"]["first_sample_end_point_epoch_s"] * rc.NS)
        offset = rc.epoch_offset(ep)
        a, b = ep["start_ns"] + offset, ep["end_ns"] + offset
        terms, end = [], anchor
        for i, f in enumerate(frames):
            row = rc.slow_frame(f)
            end = anchor if i == 0 else end + row[0]
            lo, hi = max(a, end - row[0]), min(b, end)
            if hi > lo:
                terms.append(row[2] * (hi - lo) / 1e3 / 1e9)  # mW x ns -> J, the registered order
        self.assertEqual(self.out["members"]["C2"][rid]["pm"]["gross_episode_gpu_j"], math.fsum(terms))


if __name__ == "__main__":
    unittest.main()
