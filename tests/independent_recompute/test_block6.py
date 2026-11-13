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
from unittest import mock

from .support_b6 import CAMPAIGN, b6, build_session, nine_sessions, session_id, write_attempts


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
                body["quantities"][key] = value + fraction * 0.5 * 10.0 ** -b6.decimals_for(key, b6.RATIFIED_COMPARISON_DECIMALS)
    return table


def capture_second_side(mutate=None):
    """Wrap check_block: keep a copy of the second side's table, optionally mutated before the gate compares it."""
    from joulewise import b6_analysis_check
    real, seen = b6_analysis_check.check_block, {}

    def wrapped(*args, **kwargs):
        checks = real(*args, **kwargs)
        if mutate is not None:
            mutate(checks["comparison_table"])
        seen["table"] = copy.deepcopy(checks["comparison_table"])
        return checks
    return mock.patch.object(b6_analysis_check, "check_block", wrapped), seen


def undefined_screen_block(parent, reason):
    """ALPHA, BETA and a GAMMA session whose drift screen is undefined; the screen runs are lost, not excluded."""
    specs = [("ALPHA", 1), ("BETA", 1), ("GAMMA", 1)]
    archives = []
    for k, (pack, rnd) in enumerate(specs):
        archive, _ = build_session(parent, pack, rnd, k)
        if pack == "GAMMA":
            path = archive / "derived/b6-acceptance.json"
            acceptance = json.loads(path.read_text())
            if reason == "corpus_insufficient":
                for i in range(1, 14):
                    shutil.rmtree(archive / f"sources/bound-runs/neg8-refcorpus-r{i:02}")
                acceptance["neg8"].update(verdict="undefined", corpus_clean_n=5)
            else:
                for i in (1, 2):
                    shutil.rmtree(archive / f"sources/claim-runs/neg8-window-start-r{i}")
                acceptance["neg8"].update(verdict="undefined", survivors={"start": 1, "midpoint": 1, "end": 3})
            path.write_text(json.dumps(acceptance))
        archives.append(archive)
    return archives, write_attempts(parent / "attempts.jsonl", [(p, r, True) for p, r in specs])


def screen_exclusion_block(parent, run_id, *, exclude=True, drop_trace=False, survivors=None):
    """RL-121: ALPHA r1, BETA r1 and GAMMA r1; one BETA screen run excluded and/or without its trace."""
    specs = [("ALPHA", 1), ("BETA", 1), ("GAMMA", 1)]
    archives = []
    for k, (pack, rnd) in enumerate(specs):
        options = {"exclude": {run_id: ["member.status_not_succeeded"]}} if pack == "BETA" and exclude else {}
        archive, _ = build_session(parent, pack, rnd, k, **options)
        if pack == "BETA":
            root = "bound-runs" if run_id.startswith("neg8-refcorpus") else "claim-runs"
            if drop_trace:
                (archive / "sources" / root / run_id / "raw/powermetrics.plist").unlink()
            if survivors is not None:
                path = archive / "derived/b6-acceptance.json"
                acceptance = json.loads(path.read_text())
                acceptance["neg8"]["survivors"] = survivors
                path.write_text(json.dumps(acceptance))
        archives.append(archive)
    return archives, write_attempts(parent / "attempts.jsonl", [(p, r, True) for p, r in specs])


def run_block_capturing(archives, attempts, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    restricted, public = out_dir / "restricted.json", out_dir / "public.json"
    err = io.StringIO()
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
        rc = b6.main(["block", *[str(x) for a in archives for x in ("--session", a)], "--loop-attempts", str(attempts),
                      "--restricted-out", str(restricted), "--public-out", str(public)])
    return rc, err.getvalue(), (json.loads(restricted.read_text()) if restricted.exists() else None)


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


    # ---------------------------------------------------------------- RL-113: first-program-only keys

    def test_gate_reports_first_program_only_keys_without_counting_them(self):
        """RL-113: a key the second side lacks is listed with its class, not compared, counted in public, pass unchanged."""
        def drop(table):
            del table["sessions"]["b6-beta-r1"]["quantities"]["calibration/b_op_s"]
        patch, _ = capture_second_side(drop)
        with patch:
            rc, R, _ = recompute_block(self.archives, self.attempts, self.tmp / "rl113-drop")
        base, gate = self.R["block"]["option_c"], R["block"]["option_c"]
        row = {"class": "calibration", "session": "b6-beta-r1", "key": "calibration/b_op_s"}
        self.assertIn(row, gate["first_program_only"])
        self.assertNotIn(row, base["first_program_only"])
        self.assertEqual(gate["first_program_only"],
                         sorted(gate["first_program_only"], key=lambda r: (r["class"], r["session"], r["key"])))
        self.assertEqual(set(gate["first_program_only"][0]), {"class", "session", "key"})
        classes, base_classes = gate["comparator"]["classes"], base["comparator"]["classes"]
        self.assertEqual(classes["calibration"]["compared"], base_classes["calibration"]["compared"] - 1)
        self.assertEqual(classes["calibration"]["unmatched"], 0)
        self.assertEqual(classes["calibration"]["first_program_only"],
                         base_classes["calibration"]["first_program_only"] + 1)
        listed = {}
        for r in gate["first_program_only"]:
            listed[r["class"]] = listed.get(r["class"], 0) + 1
        self.assertEqual({c: v["first_program_only"] for c, v in classes.items() if v["first_program_only"]}, listed)
        self.assertEqual((rc, gate["pass"], gate["comparator"]["pass"]), (self.rc, base["pass"], base["comparator"]["pass"]))
        self.assertTrue(gate["pass"])
        # Cold review finding 2: a class compare() never judged carries no "pass"; every judged class carries one.
        self.assertTrue(any(v["compared"] == 0 for v in classes.values()))
        for cls, v in classes.items():
            self.assertEqual("pass" in v, v["compared"] > 0, cls)

    def test_gate_fails_on_second_side_only_key(self):
        """RL-113 item 3: a key only the second side holds is compared against None and fails the gate."""
        def add(table):
            table["sessions"]["b6-beta-r1"]["quantities"]["neg8/second_side_only"] = 0
        patch, _ = capture_second_side(add)
        with patch:
            _, R, _ = recompute_block(self.archives, self.attempts, self.tmp / "rl113-add")
        gate = R["block"]["option_c"]
        self.assertFalse(gate["comparator"]["pass"])
        self.assertFalse(gate["pass"])
        self.assertGreaterEqual(gate["comparator"]["classes"]["neg8"]["failed"], 1)
        self.assertIn("option_c_disagrees", {f["code"] for f in R["flags"]})
        self.assertNotIn("neg8/second_side_only", {r["key"] for r in gate["first_program_only"]})

    def test_gate_names_failed_comparator_rows(self):
        """Cold review finding 5: a comparator failure is named in option_c.failures by class, session and key,
        with no value, and the option_c_disagrees flag carries it."""
        def add(table):
            table["sessions"]["b6-beta-r1"]["quantities"]["neg8/second_side_only"] = 0
        patch, _ = capture_second_side(add)
        with patch:
            _, R, _ = recompute_block(self.archives, self.attempts, self.tmp / "rl113-named")
        gate = R["block"]["option_c"]
        named = [f for f in gate["failures"] if f.startswith("comparator:")]
        self.assertEqual(named, ["comparator:neg8:b6-beta-r1:neg8/second_side_only"])
        flags = [f for f in R["flags"] if f["code"] == "option_c_disagrees"]
        self.assertTrue(flags)
        self.assertTrue(all("comparator:neg8:b6-beta-r1:neg8/second_side_only" in f["detail"] for f in flags))
        self.assertEqual([f for f in self.R["block"]["option_c"]["failures"] if f.startswith("comparator:")], [])

    def test_compare_reports_only_in_driver(self):
        """RL-113: standalone compare() with a key deleted from the recompute's side reports only_in_driver."""
        own = copy.deepcopy(self.R)
        del own["comparison_table"]["sessions"]["b6-beta-r2"]["quantities"]["floor/qwen3-8b/decode/absolute/floor_j"]
        restricted, public = b6.compare(own, self.R["comparison_table"])
        self.assertEqual(public["classes"]["floor"]["unmatched"], 1)
        self.assertEqual([r["reason"] for r in restricted["rows"] if "reason" in r and r["class"] == "floor"],
                         ["only_in_driver"])
        self.assertFalse(public["pass"])

    def test_single_session_equals_block_session(self):
        archive = self.by_id["b6-alpha-r1"]
        rc, single, public = recompute_single(archive, self.tmp / "single-a1", self.attempts)
        self.assertEqual(rc, 0)
        self.assertEqual(public["mode"], "SINGLE_SESSION")
        b6.require_structure_only({k: v for k, v in public.items() if k != "restricted_sha256"})
        _, cmp = b6.compare(single, only_sessions(self.R["comparison_table"], ["b6-alpha-r1"]))
        self.assertTrue(cmp["pass"], cmp["classes"])

    def test_release_comparison_requires_closed_block(self):
        _, public = b6.compare(self.R, self.R["comparison_table"], release=True)
        self.assertFalse(public["release_inputs_valid"])
        self.assertFalse(public["pass"])
        rc, closed, _ = recompute_block(self.archives, self.attempts, self.tmp / "closed", ["--closed"])
        self.assertEqual(rc, 0)
        _, public = b6.compare(closed, self.R["comparison_table"], release=True)
        self.assertTrue(public["release_inputs_valid"])
        self.assertTrue(public["pass"], public["classes"])
        pairing = closed["sessions"]["b6-gamma-r2"]["pairing"]["ALPHA"]
        self.assertEqual((pairing["rule"], pairing["provisional"]), ("2_next_counting", False))

    def test_idle_family_uses_block5_source(self):
        families = self.session("BETA", 1)["neg8"]["families"]
        self.assertTrue(families["idle_subtracted"]["passed"])
        gross, idle = families["gross"]["start_mean_j"], families["idle_subtracted"]["start_mean_j"]
        self.assertAlmostEqual(gross - idle, 0.5 * 2.0, delta=1e-12)

    def test_key_contract_matches_published_file(self):
        """Legacy published names plus the explicit retained-empty-cell fixture correction; computation is unchanged."""
        published = json.loads((b6.ROOT_DIR / "configs/b6/recompute/comparison_keys.json").read_text())
        # The historical toy key census omitted these n=0 floor-line cells.
        # The reader now deliberately retains them (n=0, mean/sd/delta=None).
        # Enumerate that correction independently, rather than regenerating
        # expected keys from the implementation or weakening the exact match.
        empty = {}
        for pack, model in (("ALPHA", "qwen3-1p7b"), ("BETA", "qwen3-8b")):
            for phase in ("decode", "prefill-p2048"):
                cell = f"{pack}/lines/whole_machine/{model}/{phase}/mean_j"
                for view in ("inclusive", "summary"):
                    for statistic in ("mean", "n", "sd"):
                        empty[f"{view}/{cell}/{statistic}"] = 0 if statistic == "n" else None
                empty[f"side_by_side/{cell}/delta"] = None
        self.assertTrue(set(empty).isdisjoint(published["block_quantity_keys"]))
        corrected = copy.deepcopy(published)
        corrected["block_quantity_keys"] = sorted(published["block_quantity_keys"] + list(empty))
        self.assertEqual(b6.key_contract(self.R), corrected)
        block = self.R["comparison_table"]["block"]["quantities"]
        self.assertEqual({key: block[key] for key in empty}, empty)
        for r in self.R["sessions"].values():
            self.assertEqual(sorted(r["quantities"]), published["session_quantity_keys"][r["pack"]], r["session_id"])

    def test_single_gamma_without_floors(self):
        rc, single, public = recompute_single(self.by_id["b6-gamma-r2"], self.tmp / "single-g2")
        self.assertEqual(rc, 0)
        self.assertEqual(public["sessions"]["b6-gamma-r2"]["pairing"]["ALPHA"]["session_id"], None)
        published = json.loads((b6.ROOT_DIR / "configs/b6/recompute/comparison_keys.json").read_text())
        self.assertEqual(sorted(single["sessions"]["b6-gamma-r2"]["quantities"]), published["single_session_gamma_keys"])
        # Lead decision 5: run energies and floor-free statistics agree with the block run.
        block = only_sessions(self.R["comparison_table"], ["b6-gamma-r2"])
        block["sessions"]["b6-gamma-r2"] = {**block["sessions"]["b6-gamma-r2"], "quantities": b6.single_gamma_view(
            block["sessions"]["b6-gamma-r2"]["quantities"])}
        _, cmp = b6.compare(single, block)
        self.assertTrue(cmp["pass"], cmp["classes"])
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
        self.assertEqual(set(public), {"schema", "pass", "recompute_stopped", "release", "release_inputs_valid",
                                       "print_spec_ratified", "classes", "restricted_sha256"})
        self.assertTrue(public["print_spec_ratified"])
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


class GammaUndefinedScreen(unittest.TestCase):
    """RL-114: a GAMMA session whose NEG-8 screen is undefined, for both registered reasons."""
    REASONS = ("corpus_insufficient", "references_insufficient")

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="b6-undefined-"))
        cls.blocks, cls.runs = {}, {}
        for reason in cls.REASONS:
            cls.blocks[reason] = undefined_screen_block(cls.tmp / reason, reason)
            patch, seen = capture_second_side()
            with patch:
                rc, err, R = run_block_capturing(*cls.blocks[reason], cls.tmp / (reason + "-out"))
            cls.runs[reason] = (rc, err, R, seen.get("table"))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_gamma_undefined_screen_block_run_completes(self):
        for reason in self.REASONS:
            with self.subTest(reason=reason):
                rc, err, R, _ = self.runs[reason]
                self.assertNotEqual(rc, 4, err)
                self.assertNotIn("refused: TypeError", err)
                g = R["sessions"]["b6-gamma-r1"]
                self.assertEqual((g["neg8"]["verdict"], g["neg8"]["reason"]), ("undefined", reason))
                self.assertTrue(any(units["quad"] for units in g["kept_units"].values()))  # a selected quad
                self.assertTrue(R["block"]["option_c"]["pass"], R["block"]["option_c"])
                self.assertNotIn("option_c_disagrees", {f["code"] for f in R["flags"]})

    def test_gamma_undefined_screen_skips_engine_and_keeps_pairing(self):
        """RL-114 items 1 to 3, in the same fixture: no contrast/neg8 key on the second side, one guard per
        contrast, and the pairing checks still count the session."""
        for reason in self.REASONS:
            with self.subTest(reason=reason):
                _, _, R, second = self.runs[reason]
                sid = "b6-gamma-r1"
                held = set(second["sessions"][sid]["quantities"])
                self.assertFalse({k for k in held if k.startswith(("contrast/", "neg8/"))})
                first = {k for k in R["comparison_table"]["sessions"][sid]["quantities"]
                         if k.startswith(("contrast/", "neg8/"))}
                self.assertTrue(first)
                gate = R["block"]["option_c"]
                listed = {r["key"] for r in gate["first_program_only"] if r["session"] == sid}
                self.assertLessEqual(first, listed)
                families = gate["families"]
                self.assertEqual(families["engine_screen_undefined"], len(R["sessions"][sid]["contrasts"]))
                self.assertGreaterEqual(families["engine_screen_undefined"], 1)
                self.assertNotIn("engine", families)
                self.assertNotIn("engine_word", families)
                self.assertNotIn("engine_refusal", families)
                self.assertEqual(families["pairing"], 4)  # one GAMMA session x (ALPHA, BETA) x (session, rule)

    def test_gamma_undefined_screen_guard_fails_on_a_claim_word(self):
        """RL-114 item 2: a claim word or a finite D_j from a session without a drift allowance fails the gate."""
        cid = "ctr-d117-decode-qwen3-1p7b-vs-qwen3-8b"
        original = b6.attach_gamma
        for reason in self.REASONS:
            # Cold review finding 1: a finite decision interval and a word outside the two are each refused.
            for i, (field, value) in enumerate((("outcome", "direction_supported"), ("D_j", 1.0),
                                                ("decision_interval_j", [0.0, 1.0]), ("outcome", "unresolved"))):
                with self.subTest(reason=reason, field=field, value=value):
                    def forced(result, *args, **kwargs):
                        original(result, *args, **kwargs)
                        result["contrasts"][cid][field] = value
                    with mock.patch.object(b6, "attach_gamma", forced):
                        rc, err, R = run_block_capturing(*self.blocks[reason], self.tmp / (reason + "-forced-" + str(i)))
                    self.assertNotEqual(rc, 4, err)
                    gate = R["block"]["option_c"]
                    self.assertFalse(gate["pass"])
                    self.assertIn("engine_screen_undefined:" + cid, gate["failures"])
                    self.assertEqual([f for f in gate["failures"] if f.startswith("engine_screen_undefined:")],
                                     ["engine_screen_undefined:" + cid])


class ExcludedScreenRun(unittest.TestCase):
    """RL-121: an excluded drift-screen run is read but is not a compared run."""
    CASES = (("neg8-window-start-r1", {"start": 2, "midpoint": 1, "end": 3}),
             ("neg8-window-midpoint", {"start": 3, "midpoint": 0, "end": 3}),
             ("neg8-refcorpus-r01", {"start": 3, "midpoint": 1, "end": 3}))

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="b6-rl121-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_excluded_screen_run_is_not_compared(self):
        for run_id, survivors in self.CASES:
            with self.subTest(run_id=run_id):
                block = screen_exclusion_block(self.tmp / run_id, run_id, survivors=survivors)
                patch, seen = capture_second_side()
                with patch:
                    rc, err, R = run_block_capturing(*block, self.tmp / (run_id + "-out"))
                self.assertEqual(rc, 0, err)
                gate = R["block"]["option_c"]
                self.assertTrue(gate["pass"], gate["comparator"])
                self.assertNotIn("option_c_disagrees", {f["code"] for f in R["flags"]})
                self.assertNotIn(run_id, seen["table"]["sessions"]["b6-beta-r1"]["run_phase_energy_j"])
                self.assertNotIn(run_id, R["comparison_table"]["sessions"]["b6-beta-r1"]["run_phase_energy_j"])
                first_rows = sum(len(phases) for body in R["comparison_table"]["sessions"].values()
                                 for phases in body["run_phase_energy_j"].values())
                self.assertEqual(gate["comparator"]["classes"]["run_phase_energy"]["compared"], first_rows)

    def test_excluded_screen_run_without_trace_does_not_stop(self):
        run_id = "neg8-window-start-r1"
        block = screen_exclusion_block(self.tmp / "excluded", run_id, drop_trace=True,
                                       survivors={"start": 2, "midpoint": 1, "end": 3})
        rc, err, R = run_block_capturing(*block, self.tmp / "excluded-out")
        missing = [f for f in R["flags"] if f["code"] == "trace_plist_missing" and f["scope"] == run_id]
        self.assertTrue(missing)
        self.assertTrue(all(f["stops_comparison"] is False for f in missing))
        self.assertFalse(R["comparison_stopped"])
        self.assertEqual(rc, 0, err)

    def test_unexcluded_screen_run_without_trace_still_stops(self):
        run_id = "neg8-window-start-r1"
        block = screen_exclusion_block(self.tmp / "kept", run_id, exclude=False, drop_trace=True,
                                       survivors={"start": 2, "midpoint": 1, "end": 3})
        rc, err, R = run_block_capturing(*block, self.tmp / "kept-out")
        missing = [f for f in R["flags"] if f["code"] == "trace_plist_missing" and f["scope"] == run_id]
        self.assertTrue(missing)
        self.assertTrue(all(f["stops_comparison"] is True for f in missing))
        self.assertTrue(R["comparison_stopped"])
        self.assertEqual(rc, 3, err)


class Block6Guards(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="b6-guard-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_synthetic_only_refusal(self):
        archive, _ = build_session(self.tmp, "BETA", 1, 0)
        (archive / b6.SYNTHETIC_MARKER).unlink()
        with mock.patch.dict("os.environ", {"JW_B5_SYNTHETIC_ONLY": "1"}):
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


class PreRebindStopFlags(unittest.TestCase):
    def test_init_stop_flag_counts_under_plan_session_id(self):
        """Predict: a stop flag raised in Session.__init__ before the copied-plan rebinding is filed under the
        final (plan) session ID, so binding_defect is true, the replication word is suppressed and the
        public per-session flag counts keep it."""
        tmp = Path(tempfile.mkdtemp(prefix="b6-prebind-"))
        self.addCleanup(shutil.rmtree, tmp, True)
        archives, attempts, _ = nine_sessions(tmp / "block")
        bracket, outer = session_id("GAMMA", 1), "outer-gamma-1"
        archive = tmp / "block" / bracket
        roster = json.loads((archive / "derived/roster.json").read_text())
        roster["pack_id"] = CAMPAIGN["ALPHA"]  # roster/acceptance pack mismatch: stop flag before rebinding
        (archive / "derived/roster.json").write_text(json.dumps(roster))
        plan = archive / "sources/night-custody/night_plan.json"
        plan.parent.mkdir(parents=True, exist_ok=True)
        plan.write_text(json.dumps({"plan_id": outer, "hazard_window": {"bindings": {"bracket_session_id": bracket}}}))
        rows = [json.loads(line) for line in attempts.read_text().splitlines()]
        for row in rows:
            if row["session_id"] == bracket:
                row["session_id"] = outer
        attempts.write_text("".join(json.dumps(row) + "\n" for row in rows))
        _, R, P = recompute_block(archives, attempts, tmp / "out")
        self.assertIn(outer, R["sessions"])
        self.assertTrue(R["sessions"][outer]["counting"])
        mismatch = [f for f in R["flags"] if f["code"] == "acceptance_session_mismatch"]
        self.assertTrue(mismatch)
        self.assertEqual({f["session"] for f in mismatch}, {outer})
        self.assertTrue(R["sessions"][outer]["binding_defect"])
        self.assertIn("acceptance_session_mismatch", P["sessions"][outer]["flag_counts"])
        contrast = copy.deepcopy(R["sessions"][outer]["contrasts"]["ctr-d117-decode-qwen3-1p7b-vs-qwen3-8b"])
        b5 = {"contrasts": {"ctr-d117-decode-qwen3-1p7b-vs-qwen3-8b": contrast}, "descriptive": {}}
        row = b6.block_lines(R["sessions"], b6.block5_quantities(b5))["replication"]["decode"]
        self.assertIsNone(row["word"])
        self.assertTrue(row["reason"].startswith("binding_defect"))
    def test_plan_refusal_flag_carries_session_pack(self):
        """Predict: a copied plan whose bracket ID does not match refuses binding; its flag is filed under the
        bracket session ID and the session's pack (GAMMA), not an empty pack."""
        tmp = Path(tempfile.mkdtemp(prefix="b6-planrefuse-"))
        self.addCleanup(shutil.rmtree, tmp, True)
        bracket = session_id("GAMMA", 1)
        archive, _ = build_session(tmp, "GAMMA", 1, 0)
        plan = archive / "sources/night-custody/night_plan.json"
        plan.parent.mkdir(parents=True, exist_ok=True)
        plan.write_text(json.dumps({"plan_id": "outer-gamma-1",
                                    "hazard_window": {"bindings": {"bracket_session_id": "other-bracket"}}}))
        flags = []
        s = b6.Session(archive, flags, [])
        self.assertEqual(s.session_id, bracket)
        refusal = [f for f in flags if f["code"] == "acceptance_session_mismatch"
                   and isinstance(f["detail"], dict) and "plan_id" in f["detail"]]
        self.assertEqual([(f["session"], f["pack"]) for f in refusal], [(bracket, "GAMMA")])



if __name__ == "__main__":
    unittest.main()
