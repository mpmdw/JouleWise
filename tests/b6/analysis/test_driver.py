"""End to end on reduced-size synthetic block-6 sessions through the fake L9.

A3 (per-session runs, no pooling), A5 (every collected session indexed),
A6 (structure-only public bytes), the DAG schedule (serial and parallel give
the same bytes), the single-session mode of §12.2 and the release replay.
The run through the real L9 programs is owed at integration (A7).
"""
from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from joulewise.b6.analysis import driver, public, schedule
from joulewise.b6.analysis.adapter import L9ProgramAdapter
from tests.b6.analysis.fakes import FakeL9, tree_digest, write_loop_root, write_r2_gamma_exclusions

ROOT = Path(__file__).resolve().parents[3]
CLEAN = lambda repo_root: "0" * 40  # noqa: E731  a synthetic analysis commit


def record_of(custody: Path, mode_directory="dry-run") -> dict:
    return json.loads((custody / mode_directory / public.PUBLIC_RECORD).read_bytes())


def restricted(custody: Path, record: dict, role: str, mode_directory="dry-run"):
    return json.loads((custody / mode_directory / "restricted/objects" / f"{record['restricted'][role]}.json").read_bytes())


class Recording(FakeL9):
    """Serial-only fake that records what each call received."""

    def __init__(self, **kwargs):
        super().__init__(noisy=False, **kwargs)
        self.calls = []

    def analyse_floor_session(self, request, custody):
        self.calls.append(("floor", request.session_id, ()))
        return super().analyse_floor_session(request, custody)

    def analyse_gamma_session(self, request, alpha, beta, custody):
        self.calls.append(("gamma", request.session_id, (alpha.session_id, beta.session_id)))
        return super().analyse_gamma_session(request, alpha, beta, custody)


class Harness(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name).resolve()
        self.loop = write_loop_root(self.tmp / "loop")

    def tearDown(self):
        self._tmp.cleanup()

    def run_driver(self, adapter, name="custody", **kwargs):
        kwargs.setdefault("checkout", CLEAN)
        self.streams = io.StringIO(), io.StringIO()
        with redirect_stdout(self.streams[0]), redirect_stderr(self.streams[1]):
            return driver.analyse(self.loop, self.tmp / name, adapter, **kwargs)


class EndToEnd(Harness):
    def test_closed_block6_runs_every_session_once_and_alone(self):
        adapter = Recording()
        self.assertEqual(self.run_driver(adapter), 0)
        floors = sorted(c[1] for c in adapter.calls if c[0] == "floor")
        self.assertEqual(floors, ["r1-alpha", "r1-beta", "r2-alpha", "r2-beta", "r3-alpha", "r3-beta", "r4-alpha"])
        gammas = {c[1]: c[2] for c in adapter.calls if c[0] == "gamma"}
        self.assertEqual(gammas, {"r1-gamma": ("r1-alpha", "r1-beta"), "r2-gamma": ("r3-alpha", "r2-beta"),
                                  "r3-gamma": ("r3-alpha", "r3-beta")})
        record = record_of(self.tmp / "custody")
        self.assertTrue(record["completed_without_tooling_refusal"])
        self.assertEqual([row["node"] for row in record["nodes"]][:3],
                         ["block5:alpha:block5", "block5:beta:block5", "block5:gamma:block5"])

    def test_parallel_workers_also_pair_by_round(self):
        self.assertEqual(self.run_driver(FakeL9(), workers=3), 0)
        received = json.loads((self.tmp / "custody/dry-run/restricted/sessions/gamma/r2-gamma/received.json").read_text())
        self.assertEqual(received, {"alpha": "r3-alpha", "beta": "r2-beta"})

    def test_r2_gamma_counts_and_enters_the_registered_lines(self):
        write_r2_gamma_exclusions(self.tmp / "loop")
        self.assertEqual(self.run_driver(FakeL9(noisy=False)), 0)
        record = record_of(self.tmp / "custody")
        lines = restricted(self.tmp / "custody", record, "replication")
        self.assertIn("r2-gamma", [row["session_id"] for row in lines["decode"]["sessions"]])
        summary = restricted(self.tmp / "custody", record, "summary")
        self.assertEqual(summary["gamma"]["quantities"]["contrast/decode/dbar_j"]["sessions"],
                         ["block5", "r1-gamma", "r2-gamma", "r3-gamma"])

    def test_summary_is_block5_plus_the_three_counting_sessions(self):
        self.run_driver(FakeL9(noisy=False))
        record = record_of(self.tmp / "custody")
        summary = restricted(self.tmp / "custody", record, "summary")
        for pack, sessions in (("alpha", ["block5", "r1-alpha", "r3-alpha", "r4-alpha"]),
                               ("beta", ["block5", "r1-beta", "r2-beta", "r3-beta"])):
            for row in summary[pack]["quantities"].values():
                self.assertEqual(row["sessions"], sessions)
        self.assertEqual(summary["alpha"]["label"], "between-session summary (n sessions): mean, standard deviation")
        flagged = restricted(self.tmp / "custody", record, "flagged_inclusive")
        self.assertEqual(flagged["alpha"]["added_sessions"], ["r2-alpha"])
        self.assertEqual(flagged["alpha"]["label"], "including sessions that did not count (n = 5)")
        self.assertEqual(next(iter(flagged["alpha"]["summary"]["quantities"].values()))["sessions"],
                         ["block5", "r1-alpha", "r2-alpha", "r3-alpha", "r4-alpha"])
        self.assertEqual(flagged["beta"]["added_sessions"], [])

    def test_every_collected_session_is_indexed(self):
        sessions = [("r1-alpha", "alpha", 1, "counting"), ("r2-alpha", "alpha", 2, "not_counting"),
                    ("r3-alpha", "alpha", 3, "pending_harvest"), ("r4-alpha", "alpha", 4, "not_counting"),
                    ("r1-beta", "beta", 1, "counting"), ("r1-gamma", "gamma", 1, "counting")]
        write_loop_root(self.tmp / "loop", sessions, overrides={
            "r2-alpha": {"codes": ("model.stack_differs_from_registered",)},
            "r4-alpha": {"codes": ("neg8.survivor_screen_failed",)}})
        adapter = Recording()
        self.run_driver(adapter)
        index = {row["session_id"]: (row["admission"], row["reasons"]) for row in record_of(self.tmp / "custody")["session_index"]}
        self.assertEqual(index, {"r1-alpha": ("counting", []), "r2-alpha": ("not_registered_experiment", ["W2"]),
                                 "r3-alpha": ("not_harvested", []), "r4-alpha": ("added", []),
                                 "r1-beta": ("counting", []), "r1-gamma": ("counting", [])})
        self.assertNotIn("r2-alpha", [c[1] for c in adapter.calls])
        self.assertNotIn("r3-alpha", [c[1] for c in adapter.calls])

    def test_a_noncounting_session_below_five_kept_units_is_not_added(self):
        self.run_driver(FakeL9(noisy=False, kept={"r2-alpha": 4}))
        index = {r["session_id"]: r for r in record_of(self.tmp / "custody")["session_index"]}
        self.assertEqual((index["r2-alpha"]["admission"], index["r2-alpha"]["reasons"]), ("not_computable", ["N3"]))
        flagged = restricted(self.tmp / "custody", record_of(self.tmp / "custody"), "flagged_inclusive")
        self.assertEqual(flagged["alpha"]["added_sessions"], [])

    def test_replication_word_with_a_disagreeing_session(self):
        adapter = FakeL9(noisy=False, contrasts={"block5": {"decode": ("direction_supported", 3.0)},
                                                  "r2-gamma": {"decode": ("unresolved", 0.9)}})
        self.run_driver(adapter)
        lines = restricted(self.tmp / "custody", record_of(self.tmp / "custody"), "replication")
        self.assertEqual(lines["decode"]["word"], "not replicated")
        self.assertEqual(lines["prefill-p2048"]["word"], "replicated")


class Schedule(Harness):
    def test_serial_and_parallel_give_identical_bytes(self):
        self.assertEqual(self.run_driver(FakeL9(), name="serial", workers=1), 0)
        self.assertEqual(self.run_driver(FakeL9(), name="parallel", workers=4), 0)
        serial = tree_digest(self.tmp / "serial/dry-run")
        parallel = tree_digest(self.tmp / "parallel/dry-run")
        self.assertEqual(serial, parallel)
        self.assertIn(public.PUBLIC_RECORD, serial)

    def test_gamma_waits_only_on_its_paired_floors(self):
        loop_census = driver.census_module.load_census(self.loop)
        config, _ = driver.load_config()
        nodes, _, _ = driver.plan(loop_census, config)
        depends = {n.id: n.depends for n in nodes}
        self.assertEqual(depends["gamma:gamma:r2-gamma"], ("floor:alpha:r3-alpha", "floor:beta:r2-beta"))
        self.assertTrue(all(depends[n] == () for n in depends if not n.startswith("gamma:")))

    def test_a_refused_floor_stops_only_its_gammas(self):
        rc = self.run_driver(FakeL9(noisy=False, refuse={"r3-alpha": "kept_bundle_strict_validation_failed"}))
        self.assertEqual(rc, 2)
        record = record_of(self.tmp / "custody")
        rows = {row["node"]: (row["status"], row["code"]) for row in record["nodes"]}
        self.assertEqual(rows["floor:alpha:r3-alpha"], ("tooling_refusal", "kept_bundle_strict_validation_failed"))
        self.assertEqual(rows["gamma:gamma:r2-gamma"], ("not_run", "paired_floor_not_analysed"))
        self.assertEqual(rows["gamma:gamma:r3-gamma"], ("not_run", "paired_floor_not_analysed"))
        self.assertEqual(rows["gamma:gamma:r1-gamma"], ("ok", None))
        self.assertFalse(record["completed_without_tooling_refusal"])
        self.assertIn(["summary", "alpha", "input_session_not_analysed"], record["line_refusals"])

    def test_an_outcome_class_stop_completes_with_exit_three(self):
        self.assertEqual(self.run_driver(FakeL9(noisy=False, outcome_class={"r1-gamma"})), 3)
        self.assertTrue(record_of(self.tmp / "custody")["completed_without_tooling_refusal"])

    def test_a_cycle_or_unknown_dependency_is_refused(self):
        from joulewise.b6.analysis.adapter import SessionRequest
        bad = (schedule.Node(schedule.GAMMA, SessionRequest("g", "gamma", 1), ("floor:alpha:missing",)),)
        with self.assertRaises(ValueError):
            schedule.execute(FakeL9(), bad, self.tmp)


class SingleSession(Harness):
    def test_one_gamma_session_with_its_floors_only(self):
        adapter = Recording()
        self.assertEqual(self.run_driver(adapter, mode="session", only="r2-gamma"), 0)
        self.assertEqual(sorted(c[1] for c in adapter.calls), ["r2-beta", "r2-gamma", "r3-alpha"])
        record = record_of(self.tmp / "custody", "session")
        self.assertEqual(sorted(record["restricted"]), ["pairings", "sessions"])
        self.assertEqual(record["only"], "r2-gamma")

    def test_one_floor_session(self):
        adapter = Recording()
        self.assertEqual(self.run_driver(adapter, mode="session", only="r4-alpha"), 0)
        self.assertEqual(adapter.calls, [("floor", "r4-alpha", ())])

    def test_an_arriving_gamma_before_the_close_is_provisional(self):
        write_loop_root(self.tmp / "loop", [("r1-alpha", "alpha", 1, "counting"), ("r1-beta", "beta", 1, "physics_stopped"),
                                            ("r1-gamma", "gamma", 1, "counting")], closed=False)
        self.assertEqual(self.run_driver(FakeL9(noisy=False), mode="session", only="r1-gamma"), 0)
        (pairing_row,) = record_of(self.tmp / "custody", "session")["pairings"]
        self.assertTrue(pairing_row["provisional"])
        self.assertEqual(pairing_row["beta"], {"session_id": "block5", "rule": "floor_from_block_5"})

    def test_mode_and_session_must_agree(self):
        self.assertEqual(self.run_driver(FakeL9(), mode="session"), 2)
        self.assertEqual(self.run_driver(FakeL9(), only="r1-alpha"), 2)

    def test_an_inadmissible_session_is_refused(self):
        write_loop_root(self.tmp / "loop", [("r1-alpha", "alpha", 1, "pending_harvest")])
        self.assertEqual(self.run_driver(FakeL9(), mode="session", only="r1-alpha"), 2)


class Release(Harness):
    def test_release_reproduces_the_dry_run(self):
        self.assertEqual(self.run_driver(FakeL9(), name="c"), 0)
        self.assertEqual(self.run_driver(FakeL9(), name="c", mode="release"), 0)
        dry, release = record_of(self.tmp / "c"), record_of(self.tmp / "c", "release")
        self.assertEqual(dry["restricted"], release["restricted"])
        self.assertNotIn("release_difference", release)

    def test_a_changed_output_stops_the_release(self):
        self.run_driver(FakeL9(noisy=False), name="c")
        changed = FakeL9(noisy=False, contrasts={"r1-gamma": {"decode": ("unresolved", 0.5)}})
        self.assertEqual(self.run_driver(changed, name="c", mode="release"), 2)
        release = record_of(self.tmp / "c", "release")
        self.assertEqual(release["release_difference"], {"differs": "nodes"})

    def test_release_needs_a_completed_dry_run(self):
        self.assertEqual(self.run_driver(FakeL9(), name="c", mode="release"), 2)
        self.assertFalse((self.tmp / "c/release").exists())


class PublicBytes(Harness):
    """A6: no number, ratio, word or sign of a science quantity in public bytes."""

    def run_subprocess(self, adapter_expression, *extra):
        script = textwrap.dedent(f"""
            import sys
            from pathlib import Path
            from joulewise.b6.analysis import driver
            from tests.b6.analysis.fakes import FakeL9
            sys.exit(driver.analyse(Path({str(self.loop)!r}), Path({str(self.tmp / 'custody')!r}), {adapter_expression},
                                    checkout=lambda r: "0" * 40{''.join(extra)}))
        """)
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        return subprocess.run([sys.executable, "-c", script], cwd=ROOT, capture_output=True, env=env)

    def assert_structure(self, raw: bytes):
        text = raw.decode("utf-8")
        self.assertTrue(public._text_is_structure(text), text)

    def test_streams_and_record_are_structure_while_restricted_logs_hold_the_noise(self):
        for workers in (1, 3):
            with self.subTest(workers=workers):
                result = self.run_subprocess("FakeL9()", f", workers={workers}")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assert_structure(result.stdout)
                self.assert_structure(result.stderr)
                self.assertEqual(len(result.stdout.splitlines()), 1)
                directory = self.tmp / "custody/dry-run"
                outside = [p for p in directory.rglob("*") if p.is_file() and "restricted" not in p.relative_to(directory).parts]
                self.assertEqual([p.name for p in outside], [public.PUBLIC_RECORD])
                self.assert_structure(outside[0].read_bytes())
                log = (directory / "restricted/sessions/alpha/r1-alpha/logs/stdout.log").read_text()
                self.assertIn("fd-level 12.5 J", log)
                self.assertIn("energy ", log)
                err = (directory / "restricted/sessions/alpha/r1-alpha/logs/stderr.log").read_text()
                self.assertIn("replicated", err)
                for path in directory.rglob("*"):
                    self.assertFalse(path.is_symlink())
                import shutil
                shutil.rmtree(self.tmp / "custody")

    def test_guard_refuses_numbers_and_words(self):
        for value in ({"x": 1.5}, {"x": "26.15"}, {"x": "1e-3"}, {"x": "direction_supported"}, {"x": "not replicated"},
                      {"26.1": 1}, ["unresolved"], {"x": object()}):
            with self.subTest(value=repr(value)):
                self.assertTrue(public.structure_problems(value))
                with self.assertRaises(public.CustodyRefusal):
                    public.require_structure_only(value)
        for value in ({"round": 3, "session_id": "r2-gamma", "counting": True, "sha": "ab" * 32, "x": None},
                      {"kept": {"qwen3-1p7b/decode": {"repeat": 10}}}):
            self.assertEqual(public.structure_problems(value), [])

    def test_restricted_token_never_reaches_the_record(self):
        rc = self.run_driver(FakeL9(noisy=False, refuse={"r1-alpha": "not_resolvable"}))
        self.assertEqual(rc, 2)
        rows = {row["node"]: row["code"] for row in record_of(self.tmp / "custody")["nodes"]}
        self.assertEqual(rows["floor:alpha:r1-alpha"], "restricted_token")

    def test_restricted_flag_codes_appear_only_as_a_count(self):
        from joulewise.flags.catalog import load_catalog
        catalog = load_catalog(ROOT / "configs/b6/flag_catalog_b6.json")
        restricted_codes = sorted(c for c in catalog.codes if catalog.entry(c).get("blinding") == "RESTRICTED")
        structure_code = "neg8.survivor_screen_failed"
        codes = (structure_code,) + tuple(restricted_codes[:1])
        write_loop_root(self.tmp / "loop", [("r1-alpha", "alpha", 1, "not_counting")], overrides={"r1-alpha": {"codes": codes}})
        self.run_driver(FakeL9(noisy=False))
        (row,) = record_of(self.tmp / "custody")["session_index"]
        self.assertEqual(row["flags"], {"codes": [structure_code], "restricted_codes_removed": len(codes) - 1})

    def test_whole_machine_values_on_gamma_are_refused(self):
        self.assertEqual(self.run_driver(FakeL9(noisy=False, whole_machine_on_gamma=True)), 2)
        refusals = record_of(self.tmp / "custody")["line_refusals"]
        self.assertIn(["whole_machine", "gamma:gamma:r1-gamma", "whole_machine_not_given_for_gamma"], refusals)

    def test_an_unexpected_exception_goes_to_restricted_custody(self):
        class Broken(FakeL9):
            def describe(self):
                raise ValueError("value 26.15 J")

        self.assertEqual(self.run_driver(Broken(noisy=False)), 2)
        self.assertNotIn("26.15", self.streams[0].getvalue() + self.streams[1].getvalue())
        self.assertEqual(self.streams[1].getvalue().splitlines()[-1], "analysis - tooling_refusal")
        log = (self.tmp / "custody/dry-run/restricted/driver-traceback.log").read_text()
        self.assertIn("26.15", log)
        self.assertFalse((self.tmp / "custody/dry-run" / public.PUBLIC_RECORD).exists())

    def test_custody_inside_the_repository_or_reused_is_refused(self):
        with redirect_stderr(io.StringIO()):
            self.assertEqual(driver.analyse(self.loop, ROOT / "custody-here", FakeL9(), checkout=CLEAN), 2)
        self.assertFalse((ROOT / "custody-here").exists())
        self.assertEqual(self.run_driver(FakeL9(noisy=False)), 0)
        self.assertEqual(self.run_driver(FakeL9(noisy=False)), 2)

    def test_malformed_loop_record_refuses_with_a_structure_line(self):
        (self.loop / "attempts.jsonl").write_text("{not json\n")
        result = self.run_subprocess("FakeL9()")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stderr.decode().strip(), "analysis - tooling_refusal loop_record_unreadable")
        self.assertEqual(result.stdout, b"")


class ProductionAdapter(Harness):
    def test_l9_is_called_only_through_the_adapter_and_refuses_until_integrated(self):
        rc = self.run_driver(L9ProgramAdapter())
        self.assertEqual(rc, 2)
        record = record_of(self.tmp / "custody")
        codes = {row["code"] for row in record["nodes"] if row["node"].startswith(("floor:", "block5:"))}
        self.assertTrue(codes <= {"l9_absent_from_checkout", "l9_session_seam_absent", "block5_release_record_absent"}, codes)
        self.assertEqual(record["adapter"]["l9_commit"], "8ad47455ce55203949ea77a3ee330432d5a48101")

    def test_no_driver_module_imports_l9_directly(self):
        package = ROOT / "joulewise/b6/analysis"
        for path in sorted(package.glob("*.py")):
            text = path.read_text()
            if path.name == "adapter.py":
                continue
            self.assertNotIn("b5_analysis", text, path.name)
        self.assertNotIn("b5_analysis", (ROOT / "scripts/b6_analyze.py").read_text())


if __name__ == "__main__":
    unittest.main()
