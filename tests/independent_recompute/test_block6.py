"""Block-6 recompute and S-13 comparator on a nine-session synthetic block; synthetic data only."""
import contextlib
import copy
import io
import json
from pathlib import Path
import shutil
import statistics
import tempfile
import unittest

from .support_b6 import b6, build_session, nine_sessions, session_id, write_attempts


def run(args):
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        rc = b6.main([str(a) for a in args])
    return rc, out.getvalue()


def recompute_block(archives, attempts, out_dir, extra=()):
    out_dir.mkdir(parents=True, exist_ok=True)
    restricted, public = out_dir / "restricted.json", out_dir / "public.json"
    args = ["block", *[x for a in archives for x in ("--session", a)], "--loop-attempts", attempts,
            "--restricted-out", restricted, "--public-out", public, *extra]
    rc, _ = run(args)
    return rc, json.loads(restricted.read_text()), json.loads(public.read_text())


def recompute_single(archive, out_dir, attempts=None):
    out_dir.mkdir(parents=True, exist_ok=True)
    restricted, public = out_dir / "restricted.json", out_dir / "public.json"
    args = ["single", "--session", archive, "--restricted-out", restricted, "--public-out", public]
    if attempts is not None:
        args += ["--loop-attempts", attempts]
    rc, _ = run(args)
    return rc, json.loads(restricted.read_text()), json.loads(public.read_text())


def only_sessions(table, ids):
    return {"schema": table["schema"], "sessions": {sid: table["sessions"][sid] for sid in ids}}


def perturb(table, fraction):
    """Move every float by `fraction` of its own S-13 bar (the driver side of a synthetic comparison)."""
    table = copy.deepcopy(table)
    for body in table["sessions"].values():
        for runs in body["run_phase_energy_j"].values():
            for phase in runs:
                runs[phase] += fraction * b6.RUN_ENERGY_BAR_J
        for key, value in body["quantities"].items():
            if isinstance(value, float):
                body["quantities"][key] = value + fraction * 0.5 * 10.0 ** -b6.decimals_for(key, b6.PROPOSED_PRINT_DECIMALS)
    return table


class Block6(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="b6-recompute-"))
        cls.archives, cls.attempts, cls.oracles = nine_sessions(cls.tmp / "block")
        cls.rc, cls.R, cls.P = recompute_block(cls.archives, cls.attempts, cls.tmp)
        cls.by_id = {a.name: a for a in cls.archives}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def session(self, pack, rnd):
        return self.R["sessions"][session_id(pack, rnd)]

    # ---------------------------------------------------------------- counting, pairing, structure

    def test_counting_from_acceptance_and_loop(self):
        self.assertEqual(self.rc, 0)
        self.assertFalse(self.R["comparison_stopped"])
        counting = {sid: r["counting"] for sid, r in self.R["sessions"].items()}
        self.assertEqual([sid for sid, c in sorted(counting.items()) if not c], ["b6-alpha-r2"])
        alpha2 = self.session("ALPHA", 2)
        self.assertEqual(alpha2["neg8"]["verdict"], "failed")
        self.assertTrue(alpha2["inclusive"]["eligible"])
        self.assertEqual(self.P["counting_by_pack"], {"ALPHA": 2, "BETA": 3, "GAMMA": 3})

    def test_gamma_pairing_by_registered_round(self):
        expected = {1: ("b6-alpha-r1", "1_same_round", "b6-beta-r1", "1_same_round"),
                    2: ("b6-alpha-r3", "2_next_counting", "b6-beta-r2", "1_same_round"),
                    3: ("b6-alpha-r3", "1_same_round", "b6-beta-r3", "1_same_round")}
        for rnd, (alpha, alpha_rule, beta, beta_rule) in expected.items():
            pairing = self.session("GAMMA", rnd)["pairing"]
            self.assertEqual((pairing["ALPHA"]["session_id"], pairing["ALPHA"]["rule"]), (alpha, alpha_rule))
            self.assertEqual((pairing["BETA"]["session_id"], pairing["BETA"]["rule"]), (beta, beta_rule))
        # The floor gate is the paired sessions' larger floor gate (section 9.4 item 5).
        g2 = self.session("GAMMA", 2)["contrasts"]["ctr-d117-decode-qwen3-1p7b-vs-qwen3-8b"]
        gates = [self.R["sessions"][sid]["floor_cells"][model + "/decode"]["floor_gate_j"]
                 for sid, model in (("b6-alpha-r3", "Qwen3-1.7B-4bit"), ("b6-beta-r2", "Qwen3-8B-4bit"))]
        self.assertEqual(g2["floor_gate_j"], max(gates))

    def test_pair_rules(self):
        floors = [(1, "a1"), (3, "a3")]
        self.assertEqual(b6.pair(1, floors), {"session_id": "a1", "rule": "1_same_round"})
        self.assertEqual(b6.pair(2, floors), {"session_id": "a3", "rule": "2_next_counting"})
        self.assertEqual(b6.pair(4, floors), {"session_id": "a3", "rule": "3_last_earlier_counting"})
        self.assertEqual(b6.pair(1, []), {"session_id": None, "rule": "3_floor_from_block_5"})

    def test_block6_operative_bound(self):
        cal = self.session("ALPHA", 1)["calibration"]
        self.assertEqual(cal["s_bracket_s"], 0.010818)
        self.assertEqual(cal["b_op_s"], max(cal["b_pre_s"], cal["b_post_s"]) + 0.010818)

    def test_kept_units_from_acceptance_exclusions(self):
        a1 = self.session("ALPHA", 1)
        self.assertNotIn("fixture-decode-r03", a1["kept_units"]["df-ph-decode-qwen3-1p7b"]["repeat"])
        self.assertNotIn("fixture-prefill-p2048-b04", a1["kept_units"]["df-ph-prefill-p2048-qwen3-1p7b"]["quad"])
        lines = a1["lines"]["df-ph-decode-qwen3-1p7b"]
        self.assertEqual(lines["load_sensitivity"]["restored_by_stratum"], {"repeat": 1, "quad": 0})
        self.assertEqual(lines["battery_assist"]["removed_by_stratum"], {"repeat": 1, "quad": 0})
        waited = a1["lines"]["df-ph-prefill-p2048-qwen3-1p7b"]["waited_runs"]
        self.assertEqual(waited["removed_by_stratum"], {"repeat": 1, "quad": 0})

    def test_public_outputs_structure_only(self):
        b6.require_structure_only({k: v for k, v in self.P.items() if k != "restricted_sha256"})
        text = json.dumps(self.P)
        for word in ("direction_supported", "not_resolvable", "unresolved", "positive", "negative", "_j\""):
            self.assertNotIn(word, text)
        for bad in (1.5, "direction_supported", "a 3.14 b", {"x": [0.1]}):
            with self.assertRaises(ValueError):
                b6.require_structure_only(bad)

    # ---------------------------------------------------------------- arithmetic against closed forms

    def test_run_phase_energies_match_closed_form(self):
        oracle = {"schema": b6.TABLE_SCHEMA, "sessions": {
            sid: {"quantities": {}, "run_phase_energy_j": {
                rid: energies for rid, energies in self.oracles[sid].items()
                if rid in self.R["comparison_table"]["sessions"][sid]["run_phase_energy_j"]}}
            for sid in self.oracles}}
        own = {"comparison_table": {"schema": b6.TABLE_SCHEMA, "sessions": {
            sid: {"quantities": {}, "run_phase_energy_j": body["run_phase_energy_j"]}
            for sid, body in self.R["comparison_table"]["sessions"].items()}}}
        restricted, public = b6.compare(own, oracle)
        self.assertTrue(public["pass"], public)
        self.assertGreater(public["classes"]["run_phase_energy"]["compared"], 9 * 300)

    def test_reported_mean_and_contrast_closed_form(self):
        oracle = self.oracles["b6-beta-r1"]
        repeats = [oracle[f"fixture-prefill-p2048-r{i:02}"]["prefill"] for i in range(1, 11)]
        quads = [statistics.fmean(oracle[f"fixture-prefill-p2048-b{i:02}-{p}"]["prefill"] for p in ("a1", "b1", "b2", "a2"))
                 for i in range(1, 11)]
        expected = 0.2 * statistics.fmean(repeats) + 0.8 * statistics.fmean(quads)
        got = self.session("BETA", 1)["quantities"]["reported/qwen3-8b/prefill-p2048/mean_j"]
        self.assertLessEqual(abs(got - expected), 0.5e-4)
        oracle = self.oracles["b6-gamma-r3"]
        d = [(oracle[f"fixture-decode-b{i:02}-b1"]["decode"] + oracle[f"fixture-decode-b{i:02}-b2"]["decode"]) / 2
             - (oracle[f"fixture-decode-b{i:02}-a1"]["decode"] + oracle[f"fixture-decode-b{i:02}-a2"]["decode"]) / 2
             for i in range(1, 11)]
        got = self.session("GAMMA", 3)["quantities"]["contrast/decode/dbar_j"]
        self.assertLessEqual(abs(got - statistics.fmean(d)), 0.5e-4)

    # ---------------------------------------------------------------- comparator

    def test_clean_rerun_agrees_within_bars(self):
        rc, again, _ = recompute_block(self.archives, self.attempts, self.tmp / "rerun")
        restricted, public = b6.compare(self.R, again["comparison_table"])
        self.assertTrue(public["pass"], public["classes"])
        for cls, row in restricted["classes"].items():
            self.assertEqual(row["max_observed_difference"] or 0.0, 0.0, cls)

    def test_bar_semantics(self):
        table = self.R["comparison_table"]
        _, inside = b6.compare(self.R, perturb(table, 0.9))
        self.assertTrue(inside["pass"], inside["classes"])
        _, outside = b6.compare(self.R, perturb(table, 1.2))
        self.assertFalse(outside["pass"])
        self.assertFalse(outside["classes"]["run_phase_energy"]["pass"])
        self.assertFalse(outside["classes"]["reported"]["pass"])

    def test_word_unmatched_and_unspecified_precision_fail(self):
        table = copy.deepcopy(self.R["comparison_table"])
        table["sessions"]["b6-gamma-r1"]["quantities"]["contrast/decode/outcome"] = "unresolved"
        _, public = b6.compare(self.R, table)
        self.assertFalse(public["classes"]["contrast_word"]["pass"])
        table = copy.deepcopy(self.R["comparison_table"])
        del table["sessions"]["b6-beta-r2"]["quantities"]["floor/qwen3-8b/decode/absolute/floor_j"]
        _, public = b6.compare(self.R, table)
        self.assertEqual(public["classes"]["floor"]["unmatched"], 1)
        self.assertFalse(public["pass"])
        restricted, public = b6.compare(self.R, table, spec=(("reported/*", 4),), spec_source="test")
        self.assertFalse(public["pass"])
        self.assertTrue(any(r.get("reason") == "print_precision_unspecified" for r in restricted["rows"]))

    def test_single_session_equals_block_session(self):
        archive = self.by_id["b6-alpha-r1"]
        rc, single, public = recompute_single(archive, self.tmp / "single-a1", self.attempts)
        self.assertEqual(rc, 0)
        self.assertEqual(public["mode"], "SINGLE_SESSION")
        b6.require_structure_only({k: v for k, v in public.items() if k != "restricted_sha256"})
        _, cmp = b6.compare(single, only_sessions(self.R["comparison_table"], ["b6-alpha-r1"]))
        self.assertTrue(cmp["pass"], cmp["classes"])

    def test_single_gamma_without_floors(self):
        rc, single, public = recompute_single(self.by_id["b6-gamma-r2"], self.tmp / "single-g2")
        self.assertEqual(rc, 0)
        self.assertEqual(public["sessions"]["b6-gamma-r2"]["pairing"]["ALPHA"]["session_id"], None)
        contrast = single["sessions"]["b6-gamma-r2"]["contrasts"]["ctr-d117-decode-qwen3-1p7b-vs-qwen3-8b"]
        self.assertIsNone(contrast["floor_gate_j"])
        block = self.session("GAMMA", 2)["contrasts"]["ctr-d117-decode-qwen3-1p7b-vs-qwen3-8b"]
        self.assertEqual(contrast["dbar_j"], block["dbar_j"])

    def mutated(self, name, mutate):
        root = self.tmp / ("mutated-" + name)
        shutil.copytree(self.by_id["b6-alpha-r1"], root / "b6-alpha-r1")
        mutate(root / "b6-alpha-r1/sources/claim-runs")
        _, clean, _ = recompute_single(self.by_id["b6-alpha-r1"], root / "clean-out")
        _, bad, _ = recompute_single(root / "b6-alpha-r1", root / "bad-out")
        return clean, bad

    def test_one_ms_edge_shift_caught(self):
        def shift(claim):
            path = claim / "fixture-decode-r01/events.jsonl"
            rows = [json.loads(line) for line in path.read_text().splitlines()]
            for row in rows:
                if row["phase"] == "decode" and row["event_type"] == "phase_start":
                    row["timestamp_s"] += 0.001
            path.write_text("".join(json.dumps(r) + "\n" for r in rows))
        clean, bad = self.mutated("edge", shift)
        restricted, public = b6.compare(bad, clean["comparison_table"])
        self.assertFalse(public["pass"])
        self.assertFalse(public["classes"]["run_phase_energy"]["pass"])
        failed = [r for r in restricted["rows"] if r["class"] == "run_phase_energy" and not r["pass"]]
        self.assertEqual(sorted(r["key"] for r in failed), ["fixture-decode-r01/decode"])
        self.assertGreater(failed[0]["difference"], 10 * b6.RUN_ENERGY_BAR_J)
        self.assertIn("stored_energy_mismatch", {f["code"] for f in bad["flags"]})

    def test_dropped_record_caught(self):
        def drop(claim):
            path = claim / "fixture-prefill-p2048-r01/raw/powermetrics.plist"
            frames = path.read_bytes().split(b"\x00")
            path.write_bytes(b"\x00".join(frames[:6] + frames[7:]))
        clean, bad = self.mutated("record", drop)
        restricted, public = b6.compare(bad, clean["comparison_table"])
        self.assertFalse(public["pass"])
        self.assertFalse(public["classes"]["run_phase_energy"]["pass"])
        self.assertIn("trace_csv_plist_mismatch", {f["code"] for f in bad["flags"]})

    def test_compare_cli_public_is_structure_only(self):
        driver = self.tmp / "driver.json"
        driver.write_text(json.dumps(perturb(self.R["comparison_table"], 1.2)))
        rc, _ = run(["compare", "--recompute", self.tmp / "restricted.json", "--driver", driver,
                     "--restricted-out", self.tmp / "cmp-r.json", "--public-out", self.tmp / "cmp-p.json"])
        self.assertEqual(rc, 1)
        public = json.loads((self.tmp / "cmp-p.json").read_text())
        self.assertEqual(set(public), {"schema", "pass", "recompute_stopped", "print_spec_ratified", "classes",
                                       "restricted_sha256"})
        self.assertFalse(public["print_spec_ratified"])
        for row in public["classes"].values():
            self.assertEqual(set(row), {"compared", "passed", "failed", "unmatched", "pass"})
        restricted = json.loads((self.tmp / "cmp-r.json").read_text())
        self.assertTrue(all("difference" in r for r in restricted["rows"]))

    # ---------------------------------------------------------------- sections 10 and 11

    def test_between_session_summary_and_inclusive_line(self):
        key = "reported/qwen3-1p7b/decode/mean_j"
        values = [self.session("ALPHA", r)["quantities"][key] for r in (1, 3)]
        row = self.R["block"]["between_session"]["ALPHA"]["values"][key]
        self.assertEqual((row["n"], row["block5_included"]), (2, False))
        self.assertEqual(row["mean"], statistics.fmean(values))
        self.assertEqual(row["sd"], statistics.stdev(values))
        inclusive = self.R["block"]["flagged_inclusive"]["ALPHA"]
        self.assertEqual(inclusive["added_sessions"], ["b6-alpha-r2"])
        self.assertEqual(inclusive["values"][key]["n"], 3)
        self.assertTrue(self.R["block"]["short"]["ALPHA"]["short"])
        self.assertIsNone(self.R["block"]["replication"]["decode"]["word"])

    def test_replication_word_with_block5(self):
        words = {r["quantities"]["contrast/decode/outcome"] for r in self.R["sessions"].values() if r["pack"] == "GAMMA"}
        self.assertEqual(words, {"direction_supported"})
        contrast = copy.deepcopy(self.session("GAMMA", 1)["contrasts"]["ctr-d117-decode-qwen3-1p7b-vs-qwen3-8b"])
        b5 = {"contrasts": {"ctr-d117-decode-qwen3-1p7b-vs-qwen3-8b": contrast}, "descriptive": {}}
        lines = b6.block_lines(self.R["sessions"], b6.block5_quantities(b5))
        self.assertEqual(lines["replication"]["decode"]["word"], "replicated")
        self.assertEqual(lines["between_session"]["GAMMA"]["values"]["contrast/decode/dbar_j"]["n"], 4)
        contrast["outcome"] = "unresolved"
        lines = b6.block_lines(self.R["sessions"], b6.block5_quantities(b5))
        self.assertEqual(lines["replication"]["decode"]["word"], "not replicated")


class Block6Guards(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="b6-guard-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_synthetic_only_refusal(self):
        archive, _ = build_session(self.tmp, "BETA", 1, 0)
        (archive / b6.SYNTHETIC_MARKER).unlink()
        rc, _ = run(["single", "--session", archive, "--restricted-out", self.tmp / "r.json",
                     "--public-out", self.tmp / "p.json"])
        self.assertEqual(rc, 4)
        self.assertFalse((self.tmp / "r.json").exists())

    def test_counting_disagreement_stops_comparison(self):
        archive, _ = build_session(self.tmp, "BETA", 1, 0)
        attempts = write_attempts(self.tmp / "attempts.jsonl", [("BETA", 1, False)])
        rc, restricted, public = recompute_single(archive, self.tmp / "out", attempts)
        self.assertEqual(rc, 3)
        self.assertFalse(public["sessions"]["b6-beta-r1"]["counting"])
        self.assertEqual(public["sessions"]["b6-beta-r1"]["flag_counts"], {"counting_disagrees": 1})
        self.assertTrue(restricted["comparison_stopped"])

    def test_reharvest_correction_in_loop_state(self):
        archive, _ = build_session(self.tmp, "BETA", 1, 0)
        attempts = write_attempts(self.tmp / "attempts.jsonl", [("BETA", 1, False)])
        state = self.tmp / "state.json"
        state.write_text(json.dumps({"reharvested": {"b6-beta-r1": {"beta": {"status": "counting"}}}}))
        out = self.tmp / "out"
        out.mkdir()
        rc, _ = run(["single", "--session", archive, "--loop-attempts", attempts, "--loop-state", state,
                     "--restricted-out", out / "r.json", "--public-out", out / "p.json"])
        self.assertEqual(rc, 0)
        public = json.loads((out / "p.json").read_text())
        self.assertTrue(public["sessions"]["b6-beta-r1"]["counting"])
        self.assertEqual(public["sessions"]["b6-beta-r1"]["flag_counts"], {})

    def test_screen_undefined_below_six_clean_corpus(self):
        exclude = {f"neg8-refcorpus-r{i:02}": ["member.status_not_succeeded"] for i in range(1, 14)}
        archive, _ = build_session(self.tmp, "ALPHA", 1, 0, exclude=exclude)
        _, restricted, public = recompute_single(archive, self.tmp / "out")
        r = restricted["sessions"]["b6-alpha-r1"]
        self.assertEqual((r["neg8"]["verdict"], r["neg8"]["reason"], r["neg8"]["corpus_n"]),
                         ("undefined", "corpus_insufficient", 5))
        self.assertIsNone(r["neg8"]["allowance_j"])
        self.assertFalse(r["inclusive"]["computable"])

    def test_lost_midpoint_narrows_spread_only(self):
        archive, _ = build_session(self.tmp, "GAMMA", 1, 0, exclude={"neg8-window-midpoint": ["member.status_not_succeeded"]})
        _, restricted, public = recompute_single(archive, self.tmp / "out")
        r = restricted["sessions"]["b6-gamma-r1"]
        self.assertEqual(r["neg8"]["verdict"], "passed")
        self.assertIsNone(r["neg8"]["midpoint_j"])
        self.assertEqual(r["neg8"]["n_mid"], 0)
        self.assertIn("neg8_midpoint_lost", public["sessions"]["b6-gamma-r1"]["flag_counts"])


if __name__ == "__main__":
    unittest.main()
