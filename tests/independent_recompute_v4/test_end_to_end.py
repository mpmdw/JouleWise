"""A full synthetic series (W1 + C1-C9 + T1-T3, D shape) through every stage under R21. C2 is structurally barred
(U2 FAIL) and the reserve C9 replaces it (R22-2 / R24). Synthetic only."""
import json
import math
import shutil
import tempfile
import unittest
from pathlib import Path

from .support import SMALL, rc, run_cli, synth


class SeriesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name) / "s"
        windows = [f"C{i}" for i in range(1, 10)] + [f"T{i}" for i in range(1, 4)]
        synth.write_series(cls.root, windows=windows, w1=True, saboteur_extra=25.0, **SMALL)
        # C1 e06: a G1 timeout in its record only -> X2 re-derived, mismatch reported, member excluded.
        ep = cls.root / "windows/C1/members/align-v4-c1-e06/outputs/align_episode.json"
        doc = json.loads(ep.read_text())
        doc["hardware"]["thermal"]["intervals"][1]["outcome"] = "timeout"
        ep.write_text(json.dumps(doc))
        # C2 e07: its released G0 is 4 C warmer -> U2(a) range 4 C > 3 C -> U2 FAIL -> C2 barred (A24).
        ep = cls.root / "windows/C2/members/align-v4-c2-e07/outputs/align_episode.json"
        doc = json.loads(ep.read_text())
        doc["hardware"]["thermal"]["intervals"][0]["release"]["slow_c"] = 44.0
        ep.write_text(json.dumps(doc))
        # C4 e22: its identity digest is missing -> U3 INCONCLUSIVE; only a FAIL bars, so C4 still pools (A23).
        ep = cls.root / "windows/C4/members/align-v4-c4-e22/outputs/align_episode.json"
        doc = json.loads(ep.read_text())
        del doc["identity_sha256"]
        ep.write_text(json.dumps(doc))
        # T3 gets R20 escalation sentinels at 23 and 24 (copies of its 22): supplemental only (A35).
        wpath = cls.root / "windows/T3/window.json"
        win = json.loads(wpath.read_text())
        late = next(m for m in win["members"] if m["ordinal"] == 22)
        for o in (23, 24):
            rid = f"align-v4-t3-e{o}"
            shutil.copytree(cls.root / "windows/T3/members" / late["run_id"], cls.root / "windows/T3/members" / rid)
            win["members"].append(dict(late, ordinal=o, run_id=rid))
            win["identity"][rid] = "identical"
        wpath.write_text(json.dumps(win))
        cls.out = rc.recompute(cls.root, workers=4)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_structure_and_statuses(self):
        out = self.out
        self.assertEqual(len(out["members"]), 13)
        self.assertEqual(sum(len(v) for v in out["members"].values()), 18 + 12 * 22 + 2)
        stop = out["calibration"]["stop"]
        self.assertEqual((stop["status"], stop["counted_windows"]), ("calibration_complete", 8))
        # 8 admitted x 7 = 56 per pair; C2 barred (contributes nothing, not counted, replaced by C9);
        # C1 e06 excluded from its pair.
        pair6 = next(m["pair"] for m in synth.window_roster("C1", "calibration", 1) if m["ordinal"] == 6)
        other = "bank" if pair6 == "spam" else "spam"
        self.assertEqual(stop["eligible_benign_totals"], {pair6: 55, other: 56})
        self.assertTrue(stop["windows"][1]["pool_barred"])
        self.assertEqual((stop["barred_windows"], stop["replacements_used"], stop["windows"][1]["bar_reason"]),
                         (["C2"], 1, "u1_u3_fail"))
        for p in rc.PAIRS:
            thr = out["calibration"]["thresholds"]["logged"][p]
            self.assertEqual((thr["status"], thr["m"]), ("ok", stop["eligible_benign_totals"][p]))
        self.assertEqual(out["claim"]["status"]["status"], "evaluable")
        self.assertEqual(out["claim"]["status"]["test_benign_n"], {"bank": 21, "spam": 21})

    def test_barred_window_and_c_sabotage_are_never_scored(self):
        out = self.out
        self.assertEqual(out["acceptance"]["U2"]["C2"]["D"]["verdict"], "fail")
        self.assertNotIn("C2", out["fits"])                                    # A24
        for w in [f"C{i}" for i in range(1, 10)]:
            for p in rc.PAIRS:
                for row in out["scores"].get(w, {}).get(p, {}).get("logged", {}).values():
                    self.assertEqual(row["fit"], "loto")                       # A27: no C sabotage score
        sab = out["members"]["C3"]["align-v4-c3-e09"]
        # A27 (lead ruling 2026-11-08): the scored C-sabotage member is hash-only everywhere.
        self.assertEqual(sorted(sab), ["condition", "kind", "model", "ordinal", "pair", "sealed_sha256", "status"])
        self.assertEqual(sab["status"], "sealed")
        self.assertEqual(set(out["exclusions"]["C3"]["align-v4-c3-e09"]), {"status", "sealed_sha256"})
        # ... but the 30B anchor-sabotage replays are anchors, not sealed.
        anchor = out["members"]["C3"]["C3:align-pilot-v3-episodes-a-e02"]
        self.assertIn("energy", anchor)
        self.assertIn("classes", out["exclusions"]["C3"]["C3:align-pilot-v3-episodes-a-e02"])
        # U1/U2 aggregates that include scored C sabotage: verdict and parts, a seal, a benign-only aggregate.
        u1 = out["acceptance"]["U1"]["C3"]["D"]
        self.assertEqual(sorted(u1), ["benign_only", "g0_timeouts", "g1h_entries", "g1h_timeouts", "included", "parts",
                                      "verdict", "x1_x4_members"])
        self.assertEqual(u1["g0_timeouts"], {"status": "sealed"})                # no hash (R23h)
        self.assertNotIn("align-v4-c3-e09", u1["benign_only"]["included"])
        self.assertIn(u1["benign_only"]["verdict"], ("pass", "fail", "inconclusive"))
        self.assertEqual(out["acceptance"]["U2"]["C3"]["D"]["g0_slow_range_c"], {"status": "sealed"})
        self.assertIn("g0_timeouts", out["acceptance"]["U1"]["T1"]["D"])          # T windows are not sealed
        self.assertEqual(set(out["reduction"]["align-v4-c3-e09"]["columns"]["gpu_mw"]), {"sha256", "n"})
        self.assertIn("fsum", out["reduction"]["align-v4-c3-e07"]["columns"]["gpu_mw"])

    def test_exclusion_rederivation(self):
        e = self.out["exclusions"]["C1"]["align-v4-c1-e06"]
        self.assertEqual((e["classes"], e["mismatch"], e["eligible"]), (["X2"], ["X2"], False))
        classes = {c for w in self.out["exclusions"].values() for m in w.values() for c in m.get("classes", [])}
        self.assertEqual(classes, {"X2"})        # seeds, cohort, identity, custody all clean in the writer

    def test_acceptance(self):
        a = self.out["acceptance"]
        self.assertAlmostEqual(a["U3_bar"]["q"], 4.2793, places=3)                 # R25: N = 22
        self.assertEqual(a["U3_bar"]["r1_screen"], "not_refuted")
        self.assertEqual(len(a["U3"]["W1"]["pairs"]), 5)
        self.assertEqual(len(a["U3"]["T3"]["pairs"]), 1)                     # 23 and 24 never in U3
        self.assertEqual(a["U3"]["C1"]["verdict"], "pass")
        self.assertEqual(a["U1"]["C1"]["D"]["verdict"], "pass")
        self.assertFalse(a["U5"]["triggers_sentinels"])
        per = a["U4"]["per_window"]
        self.assertEqual([per[w]["verdict"] for w in ("W1", "C1")], ["unevaluable", "unevaluable"])
        self.assertEqual(per["C2"]["W"], 3)
        self.assertIn("verdict", per["T3"])                                   # A14: T windows count
        self.assertEqual(set(a["U6"]), set(rc.PAIRS))                         # A16: per pair over C
        self.assertEqual(a["U6"]["spam"]["n_trajectories"] + a["U6"]["bank"]["n_trajectories"], 111)

    def test_inconclusive_u3_does_not_bar(self):
        self.assertEqual(self.out["acceptance"]["U3"]["C4"]["pairs"][0]["reason"], "identity_missing")
        self.assertEqual(self.out["acceptance"]["U3"]["C4"]["verdict"], "inconclusive")
        self.assertFalse(self.out["calibration"]["stop"]["windows"][3]["pool_barred"])
        self.assertIn("C4", self.out["fits"])

    def test_supplemental_sentinels(self):
        m = self.out["members"]["T3"]["align-v4-t3-e23"]
        self.assertTrue(m["supplemental"])
        self.assertNotIn("align-v4-t3-e23", self.out["scores"]["T3"]["spam"]["logged"])

    def test_known_h_carriers_and_contrast(self):
        claim = self.out["claim"]
        for p in rc.PAIRS:
            kh = claim["known_h"][p]
            self.assertEqual(len(kh), 3)                                       # T sabotage only (A27)
            for row in kh.values():
                self.assertEqual(row["first_k"][0]["H"], 0)
                self.assertFalse(row["council"]["0"].get("detection", False))
                for g, pt in row["council"].items():
                    if pt is not None and g != "full":
                        self.assertEqual(pt["H"], int(g))                     # A7: nominal dose exactly
            self.assertEqual(claim["carrier_curve"][p]["status"], "ok")
        c = claim["w1_contrast"]
        self.assertEqual(c["n_runs"], 8)
        self.assertIn("delta", c)                                              # always computed (A31)
        self.assertEqual(c["verdict"], "INCONCLUSIVE")                       # constant synthetic temperatures

    def test_dc_in(self):
        dc = self.out["dc_in"]["windows"]["C3"]
        row = dc["members"]["align-v4-c3-e07"]
        member = self.out["members"]["C3"]["align-v4-c3-e07"]
        self.assertAlmostEqual(row["dc_in_episode_j"], 30.0 * member["pm"]["gross_episode_s"], places=4)
        self.assertEqual(row["battery_assist"], "unavailable")
        self.assertEqual(list(dc["members"]["align-v4-c3-e09"]), ["sealed_sha256"])
        res = self.out["dc_in"]["benign_residual_print_only"]["C3"]
        self.assertEqual(sum(v["n_benign"] for v in res.values()), 14)
        # R23-4: value rows for EVERY captured benign member; only the residual rows mirror the GPU rows.
        self.assertEqual(row["residual_status"], "available")
        for wid, rid in (("C3", "C3:align-pilot-v3-episodes-a-e01"), ("C3", "align-v4-c3-e05"), ("C1", "align-v4-c1-e06"),
                         ("C2", "align-v4-c2-e06"), ("W1", "W1:align-v4-w1-e01"), ("W1", "align-v4-w1-e17")):
            r = self.out["dc_in"]["windows"][wid]["members"][rid]
            self.assertEqual((r["status"], r["residual_status"]), ("ok", "no_gpu_row"), rid)
        gpu = self.out["fits"]["C3"]
        for pair, body in res.items():
            self.assertEqual(sorted(body["scores"]), sorted(gpu[pair]["logged"]["loto"]))
            for rid, sc in body["scores"].items():
                self.assertEqual(sc["training_run_ids"], sorted(r for r in body["scores"] if r != rid))
        self.assertNotIn("C2", self.out["dc_in"]["benign_residual_print_only"])     # barred: no GPU rows

    def test_h_star_rows_and_full_cell(self):
        # R26 (3)/(4): H* on the C benign carriers and the T sabotage known-H rows only; the curve runs on
        # council U H* grid; "full" is a separate print-only cell.
        cc = self.out["claim"]["carrier_curve"]["spam"]
        self.assertEqual(sorted(cc["fractions"], key=int), [str(g) for g in rc.CURVE_GRID])
        self.assertTrue(cc["full_cell"]["print_only"])
        self.assertTrue(all(c["h_star"]["estimand"] == "H*_i" for c in cc["carriers"]))
        kh = self.out["claim"]["known_h"]["spam"]
        self.assertTrue(kh and all(r["h_star"]["grid"] == list(rc.H_STAR_GRID) for r in kh.values()))
        self.assertTrue(all(self.out["members"][r["window_id"]][rid]["condition"] == "sabotage" for rid, r in kh.items()))

    def test_turn_energies_match_the_power_record(self):
        # Re-derive one member's gross episode energy from raw frames with the A21 placement rule.
        rid = "align-v4-c3-e07"
        base = self.root / "windows/C3/members" / rid
        ep = json.loads((base / "outputs/align_episode.json").read_text())
        meta = json.loads((base / "metadata.json").read_text())
        frames = [f for f in (base / "raw/powermetrics.plist").read_bytes().split(b"\x00") if f.strip()]
        anchor = meta["uncertainty_evidence"]["clock_anchor"]["first_sample_end_point_epoch_s"]
        offset = rc.stamp_mapping(ep, meta)["offset_ns"]
        a, b = ep["start_ns"], ep["end_ns"]
        terms, cum = [], 0.0
        for i, f in enumerate(frames):
            row = rc.slow_frame(f)
            length = row[0] / 1e9
            if i:
                cum += length
            end_s = anchor + cum
            s_ns, e_ns = round((end_s - length) * 1e9) + offset, round(end_s * 1e9) + offset
            lo, hi = max(a, s_ns), min(b, e_ns)
            if hi > lo:
                terms.append(row[2] * (hi - lo) / 1e3 / 1e9)
        self.assertEqual(self.out["members"]["C3"][rid]["pm"]["gross_episode_gpu_j"], math.fsum(terms))


class TwoStageTests(unittest.TestCase):
    def test_calibration_stage_then_full_with_freeze(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        d = Path(tmp.name)
        root = d / "s"
        synth.write_series(root, **SMALL)
        code, _, _ = run_cli("--root", root, "--out", d / "cal.json", "--stage", "calibration",
                             "--freeze-out", d / "freeze.json", "--workers", 2)
        self.assertEqual(code, 0)
        cal = json.loads((d / "cal.json").read_text())
        self.assertEqual(sorted(w for w in cal["fits"] if w.startswith("T")), [])      # T never fitted
        self.assertEqual(cal["claim"]["status"]["status"], "calibration_frozen")
        self.assertEqual(cal["test"]["logged"]["spam"]["status"], "withheld_until_calibration_complete")
        code, _, _ = run_cli("--root", root, "--out", d / "full.json", "--freeze-in", d / "freeze.json",
                             "--workers", 2)
        self.assertEqual(code, 0)
        full = json.loads((d / "full.json").read_text())
        self.assertEqual(full["claim"]["status"]["status"], "evaluable")
        self.assertEqual(full["calibration"]["freeze"], cal["calibration"]["freeze"])
        tampered = json.loads((d / "freeze.json").read_text())
        tampered["freeze_sha256"] = "0" * 64
        (d / "bad.json").write_text(json.dumps(tampered))
        code, _, err = run_cli("--root", root, "--out", d / "x.json", "--freeze-in", d / "bad.json", "--workers", 1)
        self.assertEqual((code, json.loads(err)), (2, {"refused": "threshold_freeze_mismatch"}))

    def test_incomplete_calibration_withholds_t(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name) / "s"
        synth.write_series(root, windows=["C1", "C2", "T1"], **SMALL)
        out = rc.recompute(root, workers=1)
        self.assertEqual(out["calibration"]["stop"]["status"], "continue")
        self.assertNotIn("T1", out["fits"])                                            # A25
        self.assertIsNone(out["calibration"]["thresholds"]["logged"]["spam"]["threshold"])


if __name__ == "__main__":
    unittest.main()
