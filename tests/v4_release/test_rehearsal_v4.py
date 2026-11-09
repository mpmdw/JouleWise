"""Synthetic full-series rehearsal (RUN_STATE 230 "Next"): engine against recompute on one common series.

Series: W1, C1-C8 with C3's first attempt a zero-capture refusal retried in the same slot and C4 structurally
barred (U2 FAIL, declared u1_u3_fail) and replaced by the reserve C9, T1-T3 with T3 escalated to 24 members
(R20 ordinals 23/24); every export binds the 18-window R24 allocation and a GO terminal result per captured C
attempt. The probe plan adds an unavailable W1 contrast and U5 references with a negative slope and
delta = 2 C. Planted CODE mutations in each build (a patched copy of the pinned tree, never the build's
branch) must turn a named comparator family away from agree; a forged declared bar must refuse on both
sides.
"""
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import support  # noqa: E402
import common_series  # noqa: E402


@unittest.skipUnless(support.have_commits(), "pinned build commits unavailable in this clone")
class RehearsalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.full = support.rehearsal("full")
        cls.tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls.tmp.name)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_series_shape(self):
        cross = json.loads((self.full / "crosswalk.json").read_text())["members"]
        attempts = {m["attempt_id"] for m in cross}
        self.assertEqual(len({m["window"] for m in cross}), 14)          # W1 + C1-C10 + T1-T3
        for w in ("C3", "T2"):
            self.assertIn(w + "#1", attempts)
            self.assertIn(w + "#2", attempts)
            self.assertFalse(any(m["captured"] for m in cross if m["attempt_id"] == w + "#1"))
        self.assertFalse(any(m["captured"] for m in cross if m["attempt_id"] == "C3#1"))
        self.assertEqual(sum(1 for m in cross if m["attempt_id"] == "T3#1"), 24)
        payload = json.loads((self.full / "engine-input.json").read_text())
        manifest = json.loads((self.full / payload["series_source"]["path"]).read_text())
        self.assertEqual([w["window"] for w in manifest["windows"]],
                         ["W1", *[f"C{i}" for i in range(1, 15)], "T1", "T2", "T3"])          # full R24 allocation
        series = json.loads((self.full / "recompute" / "series.json").read_text())
        self.assertEqual(series["allocation_source"]["sha256"], support.common_series.ALLOCATION_SHA256)
        zero = {m["attempt_id"] for m in cross} - {m["attempt_id"] for m in cross if m["captured"]}
        self.assertEqual(zero, {"C1#1", "C1#2", "C3#1", "T2#1"})
        captured_c = [w for w in payload["windows"] if w["window"].startswith("C") and w["attempt_id"] not in zero]
        self.assertTrue(captured_c and all("terminal_result_source" in w for w in captured_c))
        self.assertFalse(any("terminal_result" in w for w in payload["windows"]))      # digest-bound only
        self.assertEqual([w["attempt_id"] for w in payload["windows"] if w.get("barred")], ["C4#1"])

    def test_bar_plus_reserve_on_both_sides(self):
        # R22-2 / R24: C1 (zero capture beyond the retry) and C4 (U2 FAIL, declared and reproduced) are barred,
        # contribute nothing, and the reserves C9 and C10 replace them, in order.
        rec = json.loads((self.full / "recompute-out.json").read_text())["calibration"]["stop"]
        fill = json.loads((self.full / "engine-out" / "fill.json").read_text())
        cal = fill["calibration"]
        self.assertEqual((rec["barred_windows"], rec["replacements_used"], rec["admitted_windows"], rec["status"]),
                         (["C1-z2", "C4"], 2, 8, "calibration_complete"))
        self.assertEqual((sorted(cal["barred_windows"]), cal["replacements_used"], cal["decision"]),
                         (["C1#2", "C4#1"], 2, "calibration_complete"))
        reasons = {w["window_id"]: w["bar_reason"] for w in rec["windows"] if w["barred"]}
        self.assertEqual(reasons, {"C1-z2": "zero_capture_beyond_retry", "C4": "u1_u3_fail"})
        ledger = {r["window"]: r.get("barred") for r in fill["ledger"]}
        # The ledger's barred field is the RECORD-level bar; the slot-level zero-capture bar is in barred_windows.
        self.assertEqual((ledger["C1#2"], ledger["C4#1"], ledger["C1#1"]), (None, "u1_u3_fail", None))
        c4 = next(w for w in rec["windows"] if w["window_id"] == "C4")
        self.assertEqual(c4["eligible_benign"], {"spam": 0, "bank": 0})

    def test_short_trajectory_h_star_rows(self):
        # Permanent fixture (R26 amendment, lead ruling 2026-11-08): C carriers whose trajectories are too
        # short to reach the upper grid, with no exceedance: h_star null, bounded_above false, the unobserved
        # tail listed, on both sides (the comparator compares the list exactly).
        rec = json.loads((self.full / "recompute-out.json").read_text())
        tails = [c["h_star"] for p in rec["claim"]["carrier_curve"].values() for c in p["carriers"]
                 if c["h_star"]["h_star"] is None and c["h_star"]["undefined_missing_grid_doses"]]
        self.assertTrue(tails)
        self.assertTrue(all(h["bounded_above"] is False for h in tails))
        code, pub, _ = support.compare(self.full, self.dir / "full.json")
        self.assertEqual((code, pub["verdict"], pub["families"]["h_star"]["verdict"]), (0, "agree", "agree"))

    def test_seed_probes_agree_with_their_sub_reasons(self):
        # Seed ruling (a) probes, both sub-reasons on one custody: C2 ordinal 6 records the DERIVED seed in its
        # Episode (the old fixture shape: seed_index_differs); C2 ordinal 7's config.json says
        # enable_thinking false (derived_seed_differs). Both builds exclude both and the comparator agrees.
        import hashlib

        def no_thinking(kit):
            d = json.loads(kit)
            spec = json.loads(d["workload_profile"]["prompt_text"])
            spec["enable_thinking"] = False
            d["workload_profile"]["prompt_text"] = json.dumps(spec, sort_keys=True, separators=(",", ":"))
            return (json.dumps(d, indent=2, sort_keys=True) + "\n").encode()
        # Ordinal 7: the planned kit config itself says enable_thinking false (custody loop closed).
        c, _ = self._config_mutation("seeds", 7, kit_fn=no_thinking)
        payload_path = c / "engine-input.json"
        payload = json.loads(payload_path.read_text())
        win = next(w for w in payload["windows"] if w["attempt_id"] == "C2#1")
        raw_path = c / win["raw_source"]["path"]
        raw = json.loads(raw_path.read_text())
        rows = {r["run_id"]: r for r in raw["members"]}
        roster = {s["ordinal"]: s for s in win["roster"]}

        def rewrite(path, fn, binary=False):
            data = json.loads(path.read_text())
            fn(data)
            path.unlink()
            text = (json.dumps(data, indent=1, sort_keys=True) + "\n").encode()
            path.write_bytes(text)
            return hashlib.sha256(text).hexdigest()
        s6, s7 = roster[6], roster[7]
        rec = c / "recompute" / "windows" / "C2" / "members"
        r6 = rows[s6["run_id"]]
        r6["episode"]["sha256"] = rewrite(c / r6["episode"]["path"],
                                          lambda d: d.update(seed=s6["expected_episode_seed"]))
        rewrite(rec / s6["run_id"] / "outputs" / "align_episode.json",
                lambda d: d.update(seed=s6["expected_episode_seed"]))
        raw_bytes = (json.dumps(raw, sort_keys=True, separators=(",", ":")) + "\n").encode()
        raw_path.unlink()
        raw_path.write_bytes(raw_bytes)
        win["raw_source"]["sha256"] = hashlib.sha256(raw_bytes).hexdigest()
        payload_path.unlink()
        payload_path.write_bytes((json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode())
        code, verdict = support.run_engine(c, workers=4)
        self.assertEqual(code, 0, verdict)
        self.assertEqual(support.run_recompute(c), 0)
        code, pub, res = support.compare(c, self.dir / "seeds.json")
        self.assertEqual((code, pub["verdict"]), (0, "agree"))
        rx = json.loads((c / "recompute-out.json").read_text())["exclusions"]["C2"]
        self.assertEqual((rx[s6["run_id"]]["seed_reasons"], rx[s7["run_id"]]["seed_reasons"]),
                         (["seed_index_differs"], ["derived_seed_differs"]))
        fill = json.loads((c / "engine-out" / "fill.json").read_text())
        el = {r["run_id"]: r for w in fill["windows"] if w["attempt_id"] == "C2#1" for r in w["eligibility"]}
        self.assertIn("seed_index_differs", el[s6["run_id"]]["reasons"])
        self.assertIn("derived_seed_differs", el[s7["run_id"]]["reasons"])

    def _config_mutation(self, name, ordinal, kit_fn=None, bundle_fn=None, plan_fn=None):
        """A C2#1 custody copy with one member's config custody changed; every digest that binds the changed
        files is updated in both layouts (one kit, bundle and plan file serve both)."""
        import hashlib
        sha = lambda b: hashlib.sha256(b).hexdigest()
        c = self._custody(name)
        payload_path = c / "engine-input.json"
        payload = json.loads(payload_path.read_text())
        win = next(w for w in payload["windows"] if w["attempt_id"] == "C2#1")
        slot = next(sl for sl in win["roster"] if sl["ordinal"] == ordinal)
        raw_path = c / win["raw_source"]["path"]
        raw = json.loads(raw_path.read_text())
        row = next(r for r in raw["members"] if r["run_id"] == slot["run_id"])
        rwin_path = c / "recompute" / "windows" / "C2" / "window.json"
        rwin = json.loads(rwin_path.read_text())
        rrow = next(m for m in rwin["members"] if m["ordinal"] == ordinal)

        def put(path, data):
            path.unlink()
            path.write_bytes(data)
            return sha(data)
        kit_path, bundle_path, plan_path = (c / row["planned_config"]["path"], c / row["config"]["path"],
                                           c / win["plan_source"]["path"])
        kit = kit_path.read_bytes()
        if kit_fn:
            kit = kit_fn(kit)
            row["planned_config"]["sha256"] = rrow["planned_config"]["sha256"] = put(kit_path, kit)
            bundle_fn = bundle_fn or (lambda _: common_series._production_bundle(kit))
        if bundle_fn:
            row["config"]["sha256"] = put(bundle_path, bundle_fn(bundle_path.read_bytes()))
        plan = json.loads(plan_path.read_text())
        prow = next(r for r in plan["members"] if r["ordinal"] == ordinal)
        prow["config_sha256"] = sha(kit)
        if plan_fn:
            plan_fn(prow)
        win["plan_source"]["sha256"] = rwin["plan_source"]["sha256"] = put(
            plan_path, common_series.canonical(plan))
        win["raw_source"]["sha256"] = put(raw_path, common_series.canonical(raw))
        put(payload_path, common_series.canonical(payload))
        put(rwin_path, (json.dumps(rwin, indent=1, sort_keys=True) + "\n").encode())
        return c, slot

    def test_config_identity_probe_sabotage_config_under_benign_slot(self):
        # r23l / recompute: a SABOTAGE config under a benign slot (custody loop closed) never calibrates: both
        # builds exclude it as config_identity_differs (:condition) and the comparator agrees.
        def sabotage(kit):
            d = json.loads(kit)
            spec = json.loads(d["workload_profile"]["prompt_text"])
            spec["condition"] = "sabotage"
            d["workload_profile"]["prompt_text"] = json.dumps(spec, sort_keys=True, separators=(",", ":"))
            return (json.dumps(d, indent=2, sort_keys=True) + "\n").encode()
        c, slot = self._config_mutation("sabcfg", 8, kit_fn=sabotage)
        self.assertEqual(slot["condition"], "benign")
        code, verdict = support.run_engine(c, workers=4)
        self.assertEqual(code, 0, verdict)
        self.assertEqual(support.run_recompute(c), 0)
        code, pub, _ = support.compare(c, self.dir / "sabcfg.json")
        self.assertEqual((code, pub["verdict"]), (0, "agree"))
        rx = json.loads((c / "recompute-out.json").read_text())["exclusions"]["C2"][slot["run_id"]]
        self.assertEqual((rx["eligible"], rx["config_reasons"]), (False, ["config_identity_differs:condition"]))
        fill = json.loads((c / "engine-out" / "fill.json").read_text())
        el = next(r for w in fill["windows"] if w["attempt_id"] == "C2#1" for r in w["eligibility"]
                  if r["run_id"] == slot["run_id"])
        self.assertIn("config_identity_differs:condition", el["reasons"])

    def test_config_custody_refusals_on_both_sides(self):
        # Each broken link of the custody loop refuses (config_digest_not_planned) on both sides: bundle bytes
        # that are not the writer's, and a plan row whose config_sha256 is not the kit's.
        cases = (("bundle-bytes", dict(bundle_fn=lambda b: json.dumps(json.loads(b)).encode())),
                 ("plan-digest", dict(plan_fn=lambda prow: prow.update(config_sha256="0" * 64))))
        for name, kw in cases:
            c, _ = self._config_mutation(name, 10, **kw)
            code, verdict = support.run_engine(c, through_window="C2")
            self.assertEqual((code, verdict.get("status")), (2, "refused"), name)
            self.assertNotEqual(support.run_recompute(c), 0, name)
            self.assertEqual(json.loads((c / "recompute-stderr.txt").read_text()),
                             {"refused": "config_digest_not_planned"}, name)

    def test_config_invalid_kit_excludes_only_that_member(self):
        # r23l: a planned kit config (digest matches the plan) that is not a JSON object excludes that member
        # alone as config_invalid on both sides; the comparator agrees.
        c, slot = self._config_mutation("badkit", 12, kit_fn=lambda kit: b"[]\n", bundle_fn=lambda b: b)
        code, verdict = support.run_engine(c, workers=4)
        self.assertEqual(code, 0, verdict)
        self.assertEqual(support.run_recompute(c), 0)
        code, pub, _ = support.compare(c, self.dir / "badkit.json")
        self.assertEqual((code, pub["verdict"]), (0, "agree"))
        rx = json.loads((c / "recompute-out.json").read_text())["exclusions"]["C2"]
        self.assertEqual(rx[slot["run_id"]]["classes"], ["config_invalid"])
        self.assertTrue(sum(1 for r in rx.values() if r.get("eligible")) > 10)

    def test_foreign_window_plan_refuses_on_both_sides(self):
        # r23l: C2's plan_source pointing at C3's committed plan (digests valid) refuses as
        # config_digest_not_planned:wrong_window on both sides.
        import hashlib
        c = self._custody("foreign-plan")
        payload_path = c / "engine-input.json"
        payload = json.loads(payload_path.read_text())
        wins = {w["attempt_id"]: w for w in payload["windows"]}
        wins["C2#1"]["plan_source"] = dict(wins["C3#2"]["plan_source"])
        payload_path.unlink()
        payload_path.write_bytes(common_series.canonical(payload))
        rwin_path = c / "recompute" / "windows" / "C2" / "window.json"
        rwin = json.loads(rwin_path.read_text())
        other = json.loads((c / "recompute" / "windows" / "C3" / "window.json").read_text())
        rwin["plan_source"] = other["plan_source"]
        rwin_path.unlink()
        rwin_path.write_text(json.dumps(rwin))
        code, verdict = support.run_engine(c, through_window="C2")
        self.assertEqual((code, verdict.get("status")), (2, "refused"))
        detail = json.loads((c / "engine-out-cal" / "refusal-detail.json").read_text())
        self.assertIn("config_digest_not_planned:wrong_window", detail["detail"])
        self.assertNotEqual(support.run_recompute(c), 0)
        self.assertEqual(json.loads((c / "recompute-stderr.txt").read_text()),
                         {"refused": "config_digest_not_planned:wrong_window"})

    def test_forged_declared_bar_refuses_on_both_sides(self):
        # r23j export rule (a): a declared u1_u3_fail that the window's own U1-U3 does not reproduce refuses.
        c = self._custody("forged")
        for rel in ("engine-input.json", "recompute/windows/C2/window.json"):
            path = c / rel
            doc = json.loads(path.read_text())
            if rel == "engine-input.json":
                next(w for w in doc["windows"] if w["attempt_id"] == "C2#1")["barred"] = "u1_u3_fail"
            else:
                doc["barred"] = "u1_u3_fail"
            path.unlink()                      # hard-linked copy: never write through
            path.write_text(json.dumps(doc))
        code, verdict = support.run_engine(c, through_window="C2")
        self.assertEqual((code, verdict.get("status")), (2, "refused"))
        self.assertNotEqual(support.run_recompute(c), 0)
        err = json.loads((c / "recompute-stderr.txt").read_text())
        self.assertEqual(err, {"refused": "declared_bar_not_reproduced"})

    def test_recompute_handles_the_zero_capture_retry(self):
        self.assertEqual(json.loads((self.full / "timings.json").read_text())["recompute_exit"], 0)
        rec = json.loads((self.full / "recompute-out.json").read_text())
        stop = rec["calibration"]["stop"]
        self.assertEqual((stop["counted_windows"], stop["status"]), (8, "calibration_complete"))
        self.assertTrue(any(not w["counted"] and w["final"] for w in stop["windows"]))

    def test_engine_runs_the_full_series(self):
        # E1 (fixed in engine-r23): a zero-capture window no longer refuses the whole analysis.
        self.assertEqual(json.loads((self.full / "engine-exit.json").read_text())["exit"], 0)

    def test_a37_seam_fixture_has_both_sides_of_the_bar(self):
        seams = json.loads((self.full / "seams.json").read_text())
        self.assertGreater(seams["C5#1"]["gap_le_1us"] + seams["C5#1"]["overlap_le_1us"], 0)
        self.assertEqual(seams["C5#1"]["gap_gt_1us"] + seams["C5#1"]["overlap_gt_1us"], 0)
        # Permanent large-epoch windows (lead ruling on P2): C7 at 4.3e9 s stays <= 1 us, C6 at 9e9 s > 1 us.
        self.assertEqual(seams["C7#1"]["gap_gt_1us"] + seams["C7#1"]["overlap_gt_1us"], 0)
        self.assertEqual(seams["C7#1"]["max_abs_seam_ns"], 954)
        self.assertGreater(seams["C6#1"]["gap_gt_1us"], 0)
        self.assertEqual(seams["C6#1"]["gap_le_1us"] + seams["C6#1"]["overlap_le_1us"], 0)

    def test_probe_series_agrees(self):
        # The probe plan swaps W1 anchor 2's B code for a G1 timeout that stops its episode (lead ruling on P1:
        # X2 is re-derived, A9 union). Both builds must exclude it: W1_anchor_block "excluded:X2" (K = 10 with C6).
        probes = support.rehearsal("probes")
        self.assertEqual(json.loads((probes / "engine-exit.json").read_text())["exit"], 0)
        code, pub, res = support.compare(probes, self.dir / "probes.json")
        self.assertEqual((code, pub["verdict"], pub["unmapped_leaves"]), (0, "agree", 0))
        rec = json.loads((probes / "recompute-out.json").read_text())
        # The timeout now sits on the gated W1 development member (ordinal 11): X2 re-derived on both sides.
        self.assertIn("X2", rec["exclusions"]["W1"]["align-v4-episodes-b-e11"]["classes"])
        # A19 unavailable contrast (ordinal 6 not token-identical) on both sides, by reason_code (seat 1 F3).
        fill = json.loads((probes / "engine-out" / "fill.json").read_text())
        self.assertEqual(fill["W1"]["contrast"]["reason_code"], "insufficient_contrast_runs")
        self.assertEqual(rec["claim"]["w1_contrast"]["reason_code"], "insufficient_contrast_runs")
        self.assertNotIn("arm_effect_j", fill["W1"]["contrast"])
        # U5 with a negative slope and delta = 2 C (seat 2 F7): |beta| x delta and abs_upper_90 x delta.
        u5 = rec["acceptance"]["U5"]
        self.assertLess(u5["beta_T"], 0)
        self.assertEqual((u5["delta_slow_c"], fill["U5"]["delta_slow_c"]), (2.0, 2.0))

    def test_prefix_series_agree(self):
        # D7 (lead ruling): incremental per-window analysis is supported, so prefix output must AGREE: rows for
        # windows not yet present are absent on both sides; no T rows without a T window.
        for plan in ("prefix1", "prefix2", "prefix_t1"):
            base = support.rehearsal(plan)
            self.assertEqual(json.loads((base / "engine-exit.json").read_text())["exit"], 0, plan)
            code, pub, _ = support.compare(base, self.dir / f"{plan}.json")
            self.assertEqual((code, pub["verdict"], pub["unmapped_leaves"]), (0, "agree", 0), plan)
            fill = json.loads((base / "engine-out" / "fill.json").read_text())
            t_present = [w["attempt_id"] for w in fill["windows"] if w["attempt_id"].startswith("T")]
            self.assertEqual(t_present, ["T1#1"] if plan == "prefix_t1" else [], plan)
            if plan == "prefix_t1":    # the T table lists only the T windows present
                by_window = fill["test"]["counts_logged"]["spam"]["benign"]["by_window"]
                self.assertEqual(sorted(by_window), ["T1"])

    def test_real_producer_shape_fixtures(self):
        # Permanent producer-shape fixtures (exporter e2e): a non-integer 42.46 s G0 passes U1(c) on both
        # sides; production cache statistics; DC with variable power, a sub-poll owned prefill segment (C7
        # ordinal 8) and a > 300 ms meter stall inside a gate (C7 ordinal 10).
        rec = json.loads((self.full / "recompute-out.json").read_text())
        self.assertIs(rec["acceptance"]["U1"]["C5"]["D"]["parts"]["c_sidecar_coverage"], True)
        fill = json.loads((self.full / "engine-out" / "fill.json").read_text())
        stats = next(r["statistics"] for r in fill["cache_diagnostics"] if isinstance(r.get("statistics"), dict))
        self.assertEqual(set(stats), {"status", "cached_tokens", "fed_tokens", "trims", "trimmed_tokens", "rebuilds",
                                      "prefill_removed_tokens"})
        dc = rec["dc_in"]["windows"]["C7"]["members"]
        self.assertEqual(dc["align-v4-c7-e08"]["status"], "ok")
        self.assertTrue(all(v is not None for v in dc["align-v4-c7-e08"]["dc_turn_j"]))

    def test_r23m_review_fixtures(self):
        # A D member whose planned G0 is missing (C9 ordinal 13) is excluded on both sides; a window with every
        # G0 removed (C10) leaves U2(a) inconclusive; a member span overhanging the meter (C9 ordinal 1) prints a
        # null whole-member DC-in.
        rec = json.loads((self.full / "recompute-out.json").read_text())
        self.assertIn("g0_missing", rec["exclusions"]["C9"]["align-v4-c9-e13"]["classes"])
        self.assertIsNone(rec["acceptance"]["U2"]["C10"]["D"]["parts"]["a_g0_slow_range_le_3c"])
        first = rec["dc_in"]["windows"]["C9"]["members"]["C9:align-pilot-v3-episodes-a-e01"]
        self.assertIsNone(first.get("dc_in_episode_j"))

    def test_owned_time_and_large_epoch_fixtures(self):
        # A2(4) at owned-time level and the permanent large-epoch A37 windows (lead rulings, 2026-11-08).
        rec = json.loads((self.full / "recompute-out.json").read_text())
        ex = rec["exclusions"]
        self.assertEqual(ex["W1"]["align-v4-episodes-a-e08"]["classes"], ["energy_unavailable"])   # edge partial
        self.assertTrue(ex["C8"]["align-v4-c8-e12"]["eligible"])                       # gate-only seams
        self.assertFalse(rec["members"]["C8"]["align-v4-c8-e12"]["pm"]["episode_covered"])  # disclosed
        self.assertTrue(all(not e.get("eligible") for e in ex["C6"].values()))                     # > 1 us seams
        self.assertTrue(any(e.get("eligible") for e in ex["C7"].values()))                         # 954 ns snapped
        self.assertEqual(rec["acceptance"]["U4"]["anchor_sigma_w_print_only"]["W1_anchor_block"], "excluded:B")

    def _patched(self, commit, rel, old, new):
        src = support.tree(commit)
        dest = self.dir / f"tree-{commit[:7]}-{abs(hash(rel + new)) % 10**6}"
        shutil.copytree(src, dest)
        p = dest / rel
        text = p.read_text()
        self.assertEqual(text.count(old), 1, (rel, old))
        p.write_text(text.replace(old, new))
        return dest

    def _custody(self, name):
        dest = self.dir / name
        shutil.copytree(self.full, dest, ignore=shutil.ignore_patterns("recompute-out.json", "engine-out*"),
                        copy_function=os.link)   # hard links; nothing below writes through them
        return dest

    def test_recompute_code_mutation_disagrees(self):
        tree = self._patched(support.RECOMPUTE_COMMIT, "scripts/independent_recompute_v4.py",
                             "rng = random.Random(0)", "rng = random.Random(1)")
        c = self._custody("mut-rec")
        (c / "engine-out").symlink_to(self.full / "engine-out")
        self.assertEqual(support.run_recompute(c, tree_dir=tree), 0)
        code, pub, _ = support.compare(c, self.dir / "mut-rec.json")
        self.assertEqual(pub["families"]["carrier_bootstrap"]["verdict"], "hold")

    def test_engine_code_mutation_disagrees(self):
        tree = self._patched(support.ENGINE_COMMIT, "joulewise/align/v4_analysis/acceptance.py",
                             "beta = .025 if heavy else .05", "beta = .025 if heavy else .04")
        c = self._custody("mut-eng")
        shutil.copy2(self.full / "recompute-out.json", c / "recompute-out.json")
        code, verdict = support.run_engine(c, tree_dir=tree, workers=4)
        self.assertEqual(code, 0)
        code, pub, _ = support.compare(c, self.dir / "mut-eng.json")
        self.assertEqual(pub["families"]["u3_bar"]["verdict"], "hold")
        self.assertEqual(pub["families"]["u3_bar_values"]["verdict"], "hold")


if __name__ == "__main__":
    unittest.main()
