"""B-3, the structure probe and the scripted term 7 check, on the pinned program's own synthetic fixtures.

Every output here comes from `scripts/independent_recompute_b6.py` run on production-shaped synthetic archives
(tests/independent_recompute/support_b6_production.py): sealed custody pins, `--inputs`, host Air. Seeded stops
edit a copy of a synthetic output. No custody and no R12 root is read.
"""
import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import b6_structure_probe as probe  # noqa: E402
from tests.independent_recompute.support import dump  # noqa: E402
from tests.independent_recompute.support_b6 import b6, build_session, write_attempts, NINE  # noqa: E402
from tests.independent_recompute.support_b6_production import seal, sha  # noqa: E402

GAMMA = "b6-gamma-r1"
DECODE = "ctr-d117-decode-qwen3-1p7b-vs-qwen3-8b"


def r3_table():
    result = subprocess.run([sys.executable, "-I", "-B", str(ROOT / "scripts/b6_r3_table.py")], capture_output=True,
                            text=True, check=True, cwd=ROOT)
    return result.stdout


def undefined_screen(archive):
    """test_block6.undefined_screen_block's corpus_insufficient case; the lost runs also leave the roster, so the
    sealing step (which hashes every roster member) sees the archive as the harvest would have written it."""
    acceptance_path = archive / "derived/b6-acceptance.json"
    acceptance = json.loads(acceptance_path.read_text())
    lost = {f"neg8-refcorpus-r{i:02}" for i in range(1, 14)}
    for run_id in lost:
        shutil.rmtree(archive / "sources/bound-runs" / run_id, ignore_errors=True)
    roster_path = archive / "derived/roster.json"
    roster = json.loads(roster_path.read_text())
    roster["members"] = [m for m in roster["members"] if m["run_id"] not in lost]
    roster_path.write_text(json.dumps(roster))
    acceptance["neg8"].update(verdict="undefined", corpus_clean_n=5)
    acceptance_path.write_text(json.dumps(acceptance))


def below_minimum(archive):
    acceptance_path = archive / "derived/b6-acceptance.json"
    acceptance = json.loads(acceptance_path.read_text())
    acceptance["excluding"].append({"code": "cell.below_minimum", "scope": "window", "why": "cell.below_minimum"})
    acceptance_path.write_text(json.dumps(acceptance))


def sealed_block(parent, specs, *, gamma_options=None, gamma_edit=None, closed=True, block5=None, only=None):
    """Sealed synthetic sessions, a run-input document pinning the loop files (and Block 5, if given), and one run
    of the pinned program. Returns the paths and the exit code."""
    parent.mkdir(parents=True)
    archives = []
    for k, (pack, rnd) in enumerate(specs):
        archive, _ = build_session(parent, pack, rnd, k, **(gamma_options or {} if pack == "GAMMA" else {}))
        if pack == "GAMMA" and gamma_edit:
            gamma_edit(archive)
        archives.append(archive)
    attempts = write_attempts(parent / "attempts.jsonl", [(p, r, True) for p, r in specs])
    state = parent / "state.json"
    dump(state, {"reharvested": {}})
    pins = {a.name: seal(a) for a in archives}
    run = archives if only is None else [a for a in archives if a.name in only]
    external = {"loop_attempts": sha(attempts), "loop_state": sha(state)}
    if block5 is not None:
        b5 = parent / "block5.json"
        dump(b5, block5)
        external["block5"] = sha(b5)
    document = parent / "run-inputs.json"
    dump(document, {"host": "Air", "l9_audit": "not_run", "external": external,
                    "sessions": {a.name: pins[a.name] for a in run}})
    restricted, public = parent / "restricted.json", parent / "public.json"
    argv = ["block", *[x for a in run for x in ("--session", str(a))], "--loop-attempts", str(attempts),
            "--loop-state", str(state), "--inputs", str(document), "--inputs-sha256", sha(document),
            "--restricted-out", str(restricted), "--public-out", str(public)]
    if closed:
        argv.append("--closed")
    if block5 is not None:
        argv += ["--block5", str(parent / "block5.json")]
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as err:
        rc = b6.main(argv)
    return {"rc": rc, "err": err.getvalue(), "restricted": restricted, "public": public, "inputs": document,
            "attempts": attempts}


class ProbeCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="b6-probe-", dir=os.environ.get("TMPDIR")))
        cls.r3 = cls.tmp / "r3.md"
        cls.r3.write_text(r3_table())
        cls.n = 0

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def run_probe(self, block, *, restricted=None, term7=True, extra=(), constants=None, stage="dry", omit=()):
        type(self).n += 1
        out = self.tmp / ("probe-" + str(self.n) + ".json")
        argv = ["--restricted", str(restricted or block["restricted"]), "--public", str(block["public"]),
                "--r3-table", str(self.r3), "--inputs", str(block["inputs"]), "--loop-attempts",
                str(block["attempts"]), "--out", str(out), *extra] + (["--term7"] if term7 else [])
        if stage:
            argv += ["--stage", stage]
        for flag in omit:  # drop a flag and its value
            i = argv.index(flag)
            del argv[i:i + 2]
        patches = [mock.patch.object(probe, k, v) for k, v in (constants or {}).items()]
        for p in patches:
            p.start()
        try:
            with contextlib.redirect_stdout(io.StringIO()) as buffer:
                rc = probe.main(argv)
        finally:
            for p in patches:
                p.stop()
        return rc, buffer.getvalue().splitlines(), (json.loads(out.read_text()) if out.exists() else None), out

    def edited(self, block, edit):
        data = json.loads(block["restricted"].read_text())
        edit(data)
        type(self).n += 1
        path = self.tmp / ("edited-" + str(self.n) + ".json")
        path.write_text(json.dumps(data))
        return path


B5_STUB = {"contrasts": {DECODE: {"n": 10, "dbar_j": 0.5}}}
DRY_CONSTANTS = {
    "NINE": ("b6-alpha-r1", "b6-beta-r1", "b6-gamma-r1", "b6-beta-r2", "b6-gamma-r2", "b6-alpha-r2",
             "b6-alpha-r3", "b6-beta-r3", "b6-gamma-r3"),
    "PAIRING": {"b6-gamma-r1": {"ALPHA": "b6-alpha-r1", "BETA": "b6-beta-r1"},
                "b6-gamma-r2": {"ALPHA": "b6-alpha-r2", "BETA": "b6-beta-r2"},
                "b6-gamma-r3": {"ALPHA": "b6-alpha-r3", "BETA": "b6-beta-r3"}},
}


class DryRun(ProbeCase):
    """The closed block run of the program's nine-session fixture, sealed, with a Block 5 stub."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.block = sealed_block(cls.tmp / "dry", NINE, block5=B5_STUB)
        assert cls.block["rc"] == 0, cls.block["err"]
        cls.expected5 = cls.tmp / "b5-expected.json"
        cls.expected5.write_text(json.dumps({"total": 1, "by_pack": {"ALPHA": 0, "BETA": 0, "GAMMA": 1}}))
        restricted = json.loads(cls.block["restricted"].read_text())
        cls.science = sum(len(s["desk_hazards"]["records"]) for s in restricted["sessions"].values())
        cls.constants = {**DRY_CONSTANTS, "SCIENCE_RUNS": cls.science}

    def dry(self, **kw):
        kw.setdefault("constants", self.constants)
        kw.setdefault("extra", ("--block5-expected", str(self.expected5)))
        return self.run_probe(self.block, **kw)

    def test_clean_dry_run_passes_every_check_and_term7(self):
        rc, lines, out, path = self.dry()
        self.assertEqual(lines, ["probe: ok", "term7: pass"], json.dumps(
            {k: v for k, v in (out or {}).get("checks", {}).items() if v["result"] == "departs"}))
        self.assertEqual(rc, 0)
        self.assertEqual(out["stage"], "dry_run")
        self.assertEqual(out["checks"]["block5_included"]["observed"], 1)
        self.assertEqual(out["checks"]["copied_paths_equal_r3"]["result"], "reported")
        self.assertFalse(out["checks"]["copied_paths_equal_r3"]["equal"])  # the fixture copies other files
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        totals = out["term7"]["totals"]
        self.assertEqual(totals["agreeing_on_a_value"], totals["compared"] - totals["both_null"])
        self.assertEqual(totals["first_program_only"], len(out["names"]["first_program_only"]))

    def test_output_is_structure_only_and_never_reads_values(self):
        _, _, out, path = self.dry()
        text = path.read_text()
        probe.guard(json.loads(text))
        restricted = json.loads(self.block["restricted"].read_text())
        self.assertNotIn("quantities", json.dumps(out["sessions"]))
        for word in ("passed", "failed"):  # the NEG-8 verdict words never appear; definedness does
            self.assertFalse(any(s.get("neg8_verdict") == word for s in out["sessions"].values()))
        self.assertTrue(all(isinstance(s["neg8_defined"], bool) for s in out["sessions"].values()))
        detail = json.dumps([f["detail"] for f in restricted["flags"]])
        self.assertNotIn("detail", json.dumps(out["flags"]))
        del detail

    def test_seeded_stops_one_per_ruled_row(self):
        fpo = lambda d: d["block"]["option_c"]["first_program_only"]
        cases = {
            "run_phase_energy": lambda d: fpo(d).append({"class": "run_phase_energy", "session": GAMMA,
                                                         "key": "fixture-decode-b01-a1/decode"}),
            "plain_compared_label": lambda d: fpo(d).append({"class": "calibration", "session": GAMMA,
                                                             "key": "calibration/b_op_s"}),
            "block_scope": lambda d: fpo(d).append({"class": "replication", "session": "__block__",
                                                    "key": "replication/decode/word"}),
            "conditional_unmet": lambda d: fpo(d).append({"class": "contrast", "session": GAMMA,
                                                          "key": "contrast/decode/p"}),
            "no_r3_row": lambda d: fpo(d).append({"class": "nothing", "session": GAMMA, "key": "nothing/at/all"}),
            "copied_family": lambda d: fpo(d).append({"class": "monitor_cost", "session": GAMMA,
                                                      "key": "monitor_cost"}),
            "whole_machine_compared": lambda d: d["block"]["option_c"].update(first_program_only=[
                r for r in fpo(d) if not r["key"].startswith("lines/whole_machine/")]),
            "class_record_kind": lambda d: d["block"]["option_c"]["comparator"]["classes"]["neg8"].update(compared=0),
            "copied_disclosures_missing": lambda d: d["sessions"][GAMMA].pop("copied_disclosures"),
            "host_not_air": lambda d: d["inputs"].update(host="synthetic"),
            "session_missing": lambda d: d["sessions"].pop("b6-beta-r2"),
        }
        for name, edit in cases.items():
            with self.subTest(stop=name):
                rc, lines, out, _ = self.dry(restricted=self.edited(self.block, edit))
                self.assertEqual(rc, 5)
                self.assertIn(name, out["term7"]["stop_classes"], lines)
                self.assertTrue(lines[-1].startswith("term7: stop "), lines)
                offending = out["names"]["term7_offending"]
                self.assertTrue(any(row[0] == name for row in offending))

    def test_seeded_departures(self):
        cases = {
            "block5_included": lambda d: [r.update(block5_included=False) for p in d["block"]["between_session"].values()
                                          for r in p["values"].values()],
            "pstar_desk_removals": lambda d: d["sessions"]["b6-alpha-r1"]["desk_hazards"]["power_removed"].append("x"),
            "option_c_pass": lambda d: d["block"]["option_c"].update(**{"pass": False}),
            "failures_empty": lambda d: d["block"]["option_c"]["failures"].append("engine:" + DECODE + "/p"),
            "program_sha256": lambda d: d.update(program_sha256="0" * 64),
            "closed": lambda d: d.update(closed=False),
        }
        stage = ("--block5-expected", str(self.expected5))
        for name, edit in cases.items():
            with self.subTest(check=name):
                rc, lines, out, _ = self.dry(restricted=self.edited(self.block, edit), extra=stage)
                self.assertEqual(rc, 5)
                self.assertEqual(out["checks"][name]["result"], "departs", name)

    def test_pairing_departure_and_provisional_flag(self):
        constants = {**self.constants, "PAIRING": {**DRY_CONSTANTS["PAIRING"],
                                                   "b6-gamma-r2": {"ALPHA": "b6-alpha-r3", "BETA": "b6-beta-r2"}}}
        rc, lines, out, _ = self.dry(constants=constants)
        self.assertEqual(rc, 5)
        self.assertEqual(out["checks"]["pairing_as_r7"]["result"], "departs")
        self.assertEqual(out["checks"]["nine_sessions"]["result"], "ok")

    def test_guard_refuses_a_float_planted_in_failures(self):
        path = self.edited(self.block, lambda d: d["block"]["option_c"]["failures"].append(12.5))
        rc, lines, out, written = self.dry(restricted=path)
        self.assertEqual((rc, lines), (6, ["probe: refused guard (output not written)"]))
        self.assertFalse(written.exists())

    def test_guard_refuses_a_name_with_a_value(self):
        path = self.edited(self.block, lambda d: d["block"]["option_c"]["failures"].append("engine:x=12.5"))
        rc, _, _, written = self.dry(restricted=path)
        self.assertEqual(rc, 6)
        self.assertFalse(written.exists())

    def test_guard_unit(self):
        probe.guard({"a": 1, "names": {"k": ["contrast/decode/p"]}, "digests": {"x": "3e5" + "0" * 61}})
        for bad in ({"a": 1.5}, {"a": "12.5"}, {"a": "3e5"}, {"a": "replicated"}, {"names": ["a b"]},
                    {"names": ["k=v"]}, {"names": [0.5]}, {"digests": {"x": "12.5"}}):
            with self.subTest(bad=bad), self.assertRaises(probe.GuardRefusal):
                probe.guard(bad)

    def test_existing_out_is_refused(self):
        _, _, _, path = self.dry()
        with contextlib.redirect_stdout(io.StringIO()) as buffer:
            rc = probe.main(["--restricted", str(self.block["restricted"]), "--public", str(self.block["public"]),
                             "--r3-table", str(self.r3), "--stage", "gate", "--out", str(path)])
        self.assertEqual((rc, buffer.getvalue().strip()), (2, "probe: refused out_exists"))

    def test_each_stage_requires_its_inputs(self):
        """RL-139 fix 5: --stage is required; dry needs --inputs, --loop-attempts, --block5-expected; gate --inputs."""
        for flag in ("--inputs", "--loop-attempts", "--block5-expected"):
            with self.subTest(stage="dry", flag=flag):
                rc, lines, out, path = self.dry(omit=(flag,))
                self.assertEqual((rc, lines), (2, ["probe: refused dry_stage_requires " + flag]))
                self.assertFalse(path.exists())
        rc, lines, _, path = self.run_probe(self.block, stage="gate", omit=("--inputs",))
        self.assertEqual((rc, lines), (2, ["probe: refused gate_stage_requires --inputs"]))
        self.assertFalse(path.exists())
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
            self.dry(stage=None)
        self.assertEqual(caught.exception.code, 2)

    def test_a_check_that_did_not_run_is_named_and_is_not_a_pass(self):
        """RL-139 fix 5: a not_checked row is named on stdout and exits 5."""
        with mock.patch.object(probe, "hazard_checks", lambda c, x: c.skip("pstar_desk_removals", "test")):
            rc, lines, out, _ = self.dry()
        self.assertEqual(rc, 5)
        self.assertEqual(lines[0], "probe: not_checked pstar_desk_removals")
        self.assertNotIn("probe: ok", lines)

    def test_an_unexpected_exception_prints_its_type_only_and_writes_nothing(self):
        """RL-139 fix 6."""
        def broken(restricted):
            raise KeyError("12.5 replicated")
        with mock.patch.object(probe, "extract", broken), contextlib.redirect_stderr(io.StringIO()) as err:
            rc, lines, out, path = self.dry()
        self.assertEqual((rc, lines, err.getvalue()), (7, ["probe: refused KeyError"], ""))
        self.assertFalse(path.exists())


class EmptyBlock5(ProbeCase):
    """Opus kit review F3: a pinned Block 5 file that parses to `{}`. The pinned program exits 0 with
    block5_input false while external_supplied.block5 is true; the dry stage departs and exits 5."""

    def test_pinned_empty_block5_departs(self):
        block = sealed_block(self.tmp / "empty-b5", NINE, block5={})
        self.assertEqual(block["rc"], 0, block["err"])
        expected = self.tmp / "b5-empty-expected.json"
        expected.write_text(json.dumps({"total": 0, "by_pack": {"ALPHA": 0, "BETA": 0, "GAMMA": 0}}))
        restricted = json.loads(block["restricted"].read_text())
        science = sum(len(s["desk_hazards"]["records"]) for s in restricted["sessions"].values())
        rc, lines, out, _ = self.run_probe(block, extra=("--block5-expected", str(expected)),
                                           constants={**DRY_CONSTANTS, "SCIENCE_RUNS": science})
        self.assertEqual(rc, 5)
        self.assertEqual(out["checks"]["block5_supplied"]["result"], "ok")
        self.assertEqual(out["checks"]["block5_input"]["result"], "departs")
        self.assertEqual(out["checks"]["block5_included"]["result"], "departs")  # 0 of 0 is a hold
        self.assertTrue(lines[0].startswith("probe: departs "), lines)

    def test_block5_supplied_false_departs(self):
        block = sealed_block(self.tmp / "b5-flag", NINE, block5=B5_STUB)
        self.assertEqual(block["rc"], 0, block["err"])
        expected = self.tmp / "b5-flag-expected.json"
        expected.write_text(json.dumps({"total": 1, "by_pack": {"ALPHA": 0, "BETA": 0, "GAMMA": 1}}))
        edited = self.edited(block, lambda d: d["inputs"]["external_supplied"].update(block5=False))
        rc, _, out, _ = self.run_probe(block, restricted=edited, extra=("--block5-expected", str(expected)),
                                       constants=DRY_CONSTANTS)
        self.assertEqual(rc, 5)
        self.assertEqual(out["checks"]["block5_supplied"]["result"], "departs")


class GateRun(ProbeCase):
    """The one-session gate shape: `block` on one sealed session, not closed, no Block 5."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.block = sealed_block(cls.tmp / "gate", (("ALPHA", 1), ("BETA", 1), ("GAMMA", 1)), closed=False,
                                 only={"b6-alpha-r1"})
        assert cls.block["rc"] == 0, cls.block["err"]

    def test_gate_checks_and_accounting(self):
        rc, lines, out, _ = self.run_probe(self.block, term7=False, stage="gate",
                                           constants={"GATE_SESSION": ("b6-alpha-r1", "ALPHA", 1)})
        self.assertEqual((rc, lines), (0, ["probe: ok"]), json.dumps(out["checks"]))
        self.assertEqual(out["stage"], "gate_run")
        self.assertEqual(out["checks"]["external_supplied"]["observed"],
                         {"block5": False, "loop_attempts": True, "loop_state": True})
        row = out["accounting"]["sessions"]["b6-alpha-r1"]
        self.assertEqual(row["registry_keys"], 122)
        self.assertEqual(row["registry_keys"], row["first_program_only"] + row["compared_derived"])
        self.assertTrue(out["accounting"]["run_closes"])

    def test_gate_departs_on_the_wrong_session(self):
        rc, lines, out, _ = self.run_probe(self.block, term7=False, stage="gate")  # the literal is r1-alpha
        self.assertEqual(rc, 5)
        self.assertEqual(out["checks"]["public_one_session"]["result"], "departs")


class Conditional(ProbeCase):
    """RL-114 and RL-133: the undefined screen and the below-minimum contrast meet their labels' second clause."""

    SPECS = (("ALPHA", 1), ("BETA", 1), ("GAMMA", 1))

    def check(self, block, formula_extra):
        self.assertEqual(block["rc"], 0, block["err"])
        expected = self.tmp / ("b5-none-" + str(self.n) + ".json")
        expected.write_text(json.dumps({"total": 0, "by_pack": {"ALPHA": 0, "BETA": 0, "GAMMA": 0}}))
        rc, lines, out, _ = self.run_probe(block, extra=("--block5-expected", str(expected)))
        self.assertEqual(out["term7"]["result"], "pass", json.dumps(out["names"]["term7_offending"]))
        self.assertEqual(lines[-1], "term7: pass")
        row = out["accounting"]["sessions"][GAMMA]
        base = out["accounting"]["sessions"]["b6-alpha-r1"]["first_program_only"]
        return out, row, base

    def test_undefined_screen_passes_with_the_conditional_clause_met(self):
        block = sealed_block(self.tmp / "undefined", self.SPECS, gamma_edit=undefined_screen)
        out, row, _ = self.check(block, 13)
        self.assertFalse(out["sessions"][GAMMA]["neg8_defined"])
        self.assertGreater(out["term7"]["distinct_keys_by_label_kind"]["conditional_neg8"], 0)
        self.assertGreater(out["term7"]["distinct_keys_by_label_kind"]["conditional_contrast"], 0)
        self.assertTrue(row["formula_holds"], row)

    def test_below_minimum_passes_with_the_conditional_clause_met(self):
        block = sealed_block(self.tmp / "below", self.SPECS, gamma_edit=below_minimum, gamma_options={"exclude": {
            f"fixture-decode-b{i:02}-a1": ["thermal.powermetrics_pressure_elevated"] for i in range(4, 11)}})
        out, row, _ = self.check(block, 2)
        self.assertEqual(out["sessions"][GAMMA]["contrast_n"][DECODE], 3)
        self.assertEqual(out["term7"]["distinct_keys_by_label_kind"]["conditional_p"], 2)
        self.assertTrue(row["formula_holds"], row)

    def test_twin_refusal_passes_with_the_conditional_clause_met(self):
        block = sealed_block(self.tmp / "refusal", self.SPECS, gamma_edit=below_minimum, gamma_options={"exclude": {
            f"fixture-decode-b{i:02}-a1": ["thermal.powermetrics_pressure_elevated"] for i in range(2, 11)}})
        out, row, _ = self.check(block, 5)
        self.assertEqual(out["sessions"][GAMMA]["contrast_n"][DECODE], 1)
        self.assertGreater(out["term7"]["distinct_keys_by_label_kind"]["conditional_contrast"], 0)
        self.assertTrue(row["formula_holds"], row)


class R3Parse(unittest.TestCase):
    def test_labels_and_lookup(self):
        rows = probe.parse_r3(r3_table())
        self.assertEqual(len(rows), 157)
        kinds = {r["kind"] for r in rows}
        self.assertLessEqual({"single_source", "not_independently_recomputed", "r8_single_implementation", "gate",
                              "block_scope", "plain_compared", "conditional_neg8", "conditional_contrast",
                              "conditional_p", "copied"}, kinds)
        self.assertNotIn("unknown", kinds)
        self.assertNotIn("unstated", kinds)
        for key, pack, kind in (("contrast/decode/p", "GAMMA", "conditional_p"),
                                ("contrast/prefill-p2048/holm_p", "GAMMA", "conditional_p"),
                                ("contrast/decode/dbar_j", "GAMMA", "conditional_contrast"),
                                ("contrast/decode/outcome", "GAMMA", "gate"),
                                ("neg8/bound_j", "ALPHA", "conditional_neg8"),
                                ("calibration/b_op_s", "BETA", "plain_compared"),
                                ("lines/whole_machine/qwen3-8b/decode/mean_j", "BETA", "r8_single_implementation"),
                                ("lines/battery_assist/decode/dbar_j", "GAMMA", "not_independently_recomputed"),
                                ("summary/ALPHA/floor/qwen3-1p7b/decode/absolute/floor_j/mean", None, "block_scope"),
                                ("reported/qwen3-1p7b/prefill-p2048/mean_j", "ALPHA", "single_source")):
            with self.subTest(key=key):
                self.assertEqual(probe.lookup(rows, key, pack)["kind"], kind)
        self.assertIsNone(probe.lookup(rows, "nothing/at/all", "ALPHA"))
        copied = {r["group"]: r["copied_paths"] for r in rows if r["scope"] == "session (copied)"}
        self.assertEqual(copied["reference_history"], ["derived/flags.jsonl", "withheld/b6-neg8.json"])


if __name__ == "__main__":
    unittest.main()
