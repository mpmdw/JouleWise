"""End to end on reduced-size synthetic block-6 sessions through the fake L9.

The sessions are desk-compressed by the real ``joulewise.desk_compress`` (with
a gzip-backed zstd stand-in), restored once per run by the driver, read at
their plain paths by the fake, and compressed again.  Covered: counting from
the loop checked against acceptance (A1, audit L5), pairing (A2), per-session
units and no pooling (A3), every session indexed (A5), structure-only public
bytes (A6), the DAG (serial and parallel give the same bytes), both phases and
their second runs (audit B6-4), the single-session mode (§12.2).  The run
through the real L9 programs is owed at integration (A7).
"""
from __future__ import annotations

import functools
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from joulewise import desk_compress
from joulewise.b6.analysis import driver, public, restore, schedule
from joulewise.b6.analysis.adapter import L9ProgramAdapter, SessionRequest
from tests.b6.analysis.fakes import (CLOSED_BLOCK6, FAKE_ZSTD_DIR, WITH_NONCOUNTING, FakeL9, build_block6, fake_zstd,
                                     tree_digest, write_r2_gamma_exclusions)

ROOT = Path(__file__).resolve().parents[3]
CLEAN = lambda repo_root: "0" * 40  # noqa: E731  a synthetic analysis commit


class Recording(FakeL9):
    """Serial-only fake that records what each call received."""

    def __init__(self, **kwargs):
        kwargs.setdefault("noisy", False)
        super().__init__(**kwargs)
        self.calls = []

    def analyse_floor_session(self, request, custody):
        self.calls.append(("floor", request.session_id, ()))
        return super().analyse_floor_session(request, custody)

    def analyse_gamma_session(self, request, alpha, beta, custody):
        self.calls.append(("gamma", request.session_id, (alpha.session_id, beta.session_id)))
        return super().analyse_gamma_session(request, alpha, beta, custody)

    def block5_session(self, pack, custody):
        self.calls.append(("block5", pack, ()))
        return super().block5_session(pack, custody)


class Harness(unittest.TestCase):
    sessions = CLOSED_BLOCK6

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name).resolve()
        self.block = build_block6(self.tmp / "tree", self.sessions, **self.tree_options())
        self.block5_record = self.tmp / "B5-RELEASE-RECORD.json"
        self.block5_record.write_text(json.dumps({"schema_version": "synthetic", "completed": True}))
        self._zstd = fake_zstd()
        self._zstd.__enter__()

    def tree_options(self):
        return {}

    def tearDown(self):
        self._zstd.__exit__(None, None, None)
        self._tmp.cleanup()

    def fake(self, **kwargs):
        kwargs.setdefault("noisy", False)
        return FakeL9(index=self.block.index, **kwargs)

    def run_driver(self, adapter, name="custody", **kwargs):
        kwargs.setdefault("checkout", CLEAN)
        if kwargs.get("mode") == "cross-block":
            kwargs.setdefault("block5_release_record", self.block5_record)
        self.streams = io.StringIO(), io.StringIO()
        with redirect_stdout(self.streams[0]), redirect_stderr(self.streams[1]):
            return driver.analyse(self.block.loop, self.block.index, self.tmp / name, adapter, **kwargs)

    def both_per_session_runs(self, adapter_factory=None, name="custody"):
        factory = adapter_factory or self.fake
        self.assertEqual(self.run_driver(factory(), name, mode="per-session", run=1), 0, self.streams[1].getvalue())
        self.assertEqual(self.run_driver(factory(), name, mode="per-session", run=2), 0, self.streams[1].getvalue())

    def record(self, directory="per-session-1", name="custody") -> dict:
        return json.loads((self.tmp / name / directory / public.PUBLIC_RECORD).read_bytes())

    def restricted(self, role, directory="per-session-1", name="custody"):
        digest = self.record(directory, name)["restricted"][role]
        return json.loads((self.tmp / name / directory / "restricted/objects" / f"{digest}.json").read_bytes())


class PerSessionPhase(Harness):
    def test_closed_block6_runs_every_unit_once_and_alone(self):
        adapter = Recording(index=self.block.index)
        self.assertEqual(self.run_driver(adapter), 0)
        floors = sorted(c[1] for c in adapter.calls if c[0] == "floor")
        self.assertEqual(floors, ["r1-alpha", "r1-beta", "r2-beta", "r3-alpha", "r3-beta", "r4-alpha"])
        gammas = {c[1]: c[2] for c in adapter.calls if c[0] == "gamma"}
        self.assertEqual(gammas, {"r1-gamma": ("r1-alpha", "r1-beta"), "r2-gamma": ("r3-alpha", "r2-beta"),
                                  "r3-gamma": ("r3-alpha", "r3-beta")})
        self.assertNotIn("block5", [c[0] for c in adapter.calls])
        record = self.record()
        self.assertTrue(record["completed_without_tooling_refusal"])
        self.assertEqual(record["cross_block"], "not_run")
        self.assertEqual(sorted(record["restricted"]), ["pairings", "sessions"])
        self.assertEqual(len(record["sessions"]), 9)
        for row in record["sessions"]:
            self.assertEqual((row["loop_counting"], row["acceptance_counting"], row["analysed"]), (True, True, True))
        self.assertEqual(sorted(record["bindings"]["harvest_records"]), sorted(s[0] for s in CLOSED_BLOCK6))

    def test_parallel_workers_also_pair_by_round(self):
        self.assertEqual(self.run_driver(self.fake(), workers=3), 0)
        received = json.loads((self.tmp / "custody/per-session-1/restricted/sessions/gamma/r2-gamma/received.json")
                              .read_text())
        self.assertEqual(received, {"alpha": "r3-alpha", "beta": "r2-beta"})

    def test_r2_gamma_counts_although_its_exclusions_say_claim_usable_false(self):
        write_r2_gamma_exclusions(self.tmp / "tree/b6")
        self.assertEqual(self.run_driver(self.fake()), 0)
        row = next(r for r in self.record()["sessions"] if r["session_id"] == "r2-gamma")
        self.assertEqual((row["loop_counting"], row["acceptance_counting"], row["analysed"]), (True, True, True))

    def test_every_collected_session_is_indexed(self):
        sessions = [("r1-alpha", "alpha", 1, "counting"), ("r2-alpha", "alpha", 2, "not_counting"),
                    ("r4-alpha", "alpha", 4, "not_counting"), ("r5-alpha", "alpha", 5, "not_counting"),
                    ("r6-alpha", "alpha", 6, "not_counting"),
                    ("r1-beta", "beta", 1, "counting"), ("r1-gamma", "gamma", 1, "counting")]
        self.block = build_block6(self.tmp / "other", sessions, overrides={
            "r2-alpha": {"codes": ("model.stack_differs_from_registered",)},
            "r4-alpha": {"codes": ("neg8.survivor_screen_failed",)},
            "r5-alpha": {"codes": ("neg8.survivor_screen_undefined",)},
            "r6-alpha": {"structure_ok": False}})
        adapter = Recording(index=self.block.index, drift={"r5-alpha": "undefined"})
        self.assertEqual(self.run_driver(adapter), 0)
        record = self.record()
        index = {row["session_id"]: (row["admission"], row["reasons"]) for row in record["sessions"]}
        self.assertEqual(index, {"r1-alpha": ("counting", []), "r2-alpha": ("not_registered_experiment", ["W2"]),
                                 "r4-alpha": ("added", []), "r5-alpha": ("not_computable", ["drift_screen_undefined"]),
                                 "r6-alpha": ("not_registered_experiment", ["S1"]),
                                 "r1-beta": ("counting", []), "r1-gamma": ("counting", [])})
        analysed = [c[1] for c in adapter.calls]
        self.assertIn("r5-alpha", analysed)          # (i) decides what is analysed; (ii) is read from it
        self.assertNotIn("r2-alpha", analysed)
        self.assertNotIn("r6-alpha", analysed)
        self.assertEqual(record["sessions_unaccounted"], [])

    def test_an_undecided_session_leaves_the_run_incomplete(self):
        sessions = list(CLOSED_BLOCK6) + [("r5-alpha", "alpha", 5, "pending_harvest")]
        self.block = build_block6(self.tmp / "other", sessions, decided={s[0] for s in CLOSED_BLOCK6})
        self.assertEqual(self.run_driver(self.fake()), 2)
        self.assertEqual(self.record()["sessions_unaccounted"], ["r5-alpha"])

    def test_a_refused_floor_stops_only_its_gammas(self):
        self.assertEqual(self.run_driver(self.fake(refuse={"r3-alpha": "kept_bundle_strict_validation_failed"})), 2)
        rows = {row["node"]: (row["status"], row["code"]) for row in self.record()["nodes"]}
        self.assertEqual(rows["floor:alpha:r3-alpha"], ("tooling_refusal", "kept_bundle_strict_validation_failed"))
        self.assertEqual(rows["gamma:gamma:r2-gamma"], ("not_run", "paired_floor_not_analysed"))
        self.assertEqual(rows["gamma:gamma:r3-gamma"], ("not_run", "paired_floor_not_analysed"))
        self.assertEqual(rows["gamma:gamma:r1-gamma"], ("ok", None))
        self.assertEqual(sorted(self.record()["sessions_unaccounted"]), ["r2-gamma", "r3-alpha", "r3-gamma"])

    def test_an_outcome_class_stop_completes_with_exit_three(self):
        self.assertEqual(self.run_driver(self.fake(outcome_class={"r1-gamma"})), 3)
        self.assertTrue(self.record()["completed_without_tooling_refusal"])

    def test_a_gamma_needing_a_block5_floor_is_deferred(self):
        sessions = [("r1-alpha", "alpha", 1, "counting"), ("r1-gamma", "gamma", 1, "counting")]
        self.block = build_block6(self.tmp / "other", sessions)
        self.assertEqual(self.run_driver(self.fake()), 0)
        record = self.record()
        rows = {row["node"]: (row["status"], row["code"]) for row in record["nodes"]}
        self.assertEqual(rows["gamma:gamma:r1-gamma"], ("deferred", "block5_not_released"))
        self.assertEqual(record["pairings"][0]["beta"], {"session_id": "block5", "rule": "block5"})
        self.assertEqual(record["sessions_unaccounted"], [])


class CountingAgainstAcceptance(Harness):
    """Audit L5: counting is the loop's and must equal the acceptance's for every session."""

    def test_a_loop_acceptance_disagreement_refuses_before_anything_runs(self):
        self.block = build_block6(self.tmp / "other", acceptance={"r2-gamma": False})
        adapter = Recording(index=self.block.index)
        self.assertEqual(self.run_driver(adapter), 2)
        self.assertEqual(self.streams[1].getvalue().strip(), "analysis - tooling_refusal b6_counting_records_disagree")
        self.assertEqual(adapter.calls, [])
        self.assertFalse((self.tmp / "custody/per-session-1").exists())

    def test_analysis_counting_must_equal_acceptance_counting(self):
        self.assertEqual(self.run_driver(self.fake(analysis_counting={"r3-alpha": False, "r1-alpha": True})), 2)
        record = self.record()
        self.assertEqual(record["line_refusals"], [["counting", "r3-alpha", "analysis_counting_differs_from_acceptance"]])
        row = next(r for r in record["sessions"] if r["session_id"] == "r3-alpha")
        self.assertEqual((row["acceptance_counting"], row["analysis_counting"]), (True, False))

    def test_an_analysed_session_must_report_its_analysis_counting(self):
        class Silent(FakeL9):
            def _counting(self, session_id):
                return None if session_id == "r2-beta" else super()._counting(session_id)

        self.assertEqual(self.run_driver(Silent(index=self.block.index, noisy=False)), 2)
        self.assertEqual(self.record()["line_refusals"], [["counting", "r2-beta", "analysis_counting_not_reported"]])

    def test_an_index_that_names_other_sessions_refuses(self):
        index = json.loads(self.block.index.read_text())
        index["sessions"] = index["sessions"][:-1]
        self.block.index.write_text(json.dumps(index))
        self.assertEqual(self.run_driver(self.fake()), 2)
        self.assertIn("session_index_differs_from_census", self.streams[1].getvalue())

    def test_a_changed_acceptance_record_after_indexing_refuses(self):
        path = self.block.session_dir("r1-alpha") / "archive/derived/b6-acceptance.json"
        record = json.loads(path.read_text())
        path.write_text(json.dumps({**record, "counting": False}))
        self.assertEqual(self.run_driver(self.fake()), 2)
        self.assertIn("session_index_digest_mismatch", self.streams[1].getvalue())


class RestoreOncePerRun(Harness):
    def compression_rows(self, session_id):
        manifest = Path(str(self.block.session_dir(session_id) / "archive") + ".desk/compression.jsonl")
        return [json.loads(line) for line in manifest.read_text().splitlines() if line.strip()]

    def test_each_session_is_restored_once_and_compressed_again(self):
        before = {s[0]: (self.block.raw_file(s[0]).with_name("powermetrics.plist.zst").exists(),
                         self.block.raw_file(s[0]).exists()) for s in CLOSED_BLOCK6}
        self.assertTrue(all(zst and not plain for zst, plain in before.values()))
        self.assertEqual(self.run_driver(self.fake(), workers=3), 0)
        for session_id, *_ in CLOSED_BLOCK6:
            rows = self.compression_rows(session_id)
            events = [(r["event"], Path(r["path"]).name) for r in rows]
            # ALPHA r3 serves GAMMA r2 and r3 and is still restored once: one
            # restore and one re-compression per file in this run.
            self.assertEqual(sum(e == "restore" for e, _ in events), 2, session_id)
            self.assertEqual(sum(e == "compress" for e, _ in events), 4, session_id)
            self.assertFalse(self.block.raw_file(session_id).exists())
            self.assertTrue(self.block.raw_file(session_id).with_name("powermetrics.plist.zst").exists())
        cycles = self.record()["restore_cycles"]
        self.assertEqual(sorted(cycles), sorted(s[0] for s in CLOSED_BLOCK6))
        self.assertTrue(all(c["after_check"] == "equal" and c["files_restored"] == 2 for c in cycles.values()))

    def test_outputs_on_compressed_and_plain_sessions_are_identical(self):
        """Design §4.1 item 4 (bar B1): the restored bytes are the harvested bytes."""
        self.assertEqual(self.run_driver(self.fake()), 0)
        compressed_nodes = self.record()["nodes"]
        compressed_sessions = self.restricted("sessions")
        self.block = build_block6(self.tmp / "plain", compressed=False)
        self.assertEqual(self.run_driver(self.fake(), name="plain-custody"), 0)
        self.assertEqual(self.record(name="plain-custody")["nodes"], compressed_nodes)
        self.assertEqual(self.restricted("sessions", name="plain-custody"), compressed_sessions)
        cycles = self.record(name="plain-custody")["restore_cycles"].values()
        self.assertTrue(all(c["files_restored"] == 0 and c["after_check"] == "not_compressed" for c in cycles))
        self.assertTrue(self.block.raw_file("r1-alpha").exists())     # left exactly as found

    def test_no_space_refuses_and_leaves_the_session_compressed(self):
        class NoSpace(restore.Lifecycle):
            restore = staticmethod(functools.partial(restore.restore_session, free=lambda path: 0))

        self.assertEqual(self.run_driver(self.fake(), lifecycle_class=NoSpace), 2)
        rows = {row["node"]: (row["status"], row["code"]) for row in self.record()["nodes"]}
        self.assertEqual(rows["floor:alpha:r1-alpha"], ("tooling_refusal", "b6_restore_failed"))
        self.assertTrue(self.block.raw_file("r1-alpha").with_name("powermetrics.plist.zst").exists())
        self.assertIn(["restore", "r1-alpha", "b6_restore_failed"], self.record()["line_refusals"])

    def test_a_corrupt_compressed_file_refuses(self):
        self.block.raw_file("r4-alpha").with_name("powermetrics.plist.zst").write_bytes(b"not a compressed stream")
        self.assertEqual(self.run_driver(self.fake()), 2)
        rows = {row["node"]: (row["status"], row["code"]) for row in self.record()["nodes"]}
        self.assertEqual(rows["floor:alpha:r4-alpha"], ("tooling_refusal", "b6_restore_failed"))
        self.assertEqual(rows["floor:alpha:r1-alpha"], ("ok", None))

    def test_a_write_into_a_session_during_the_run_is_caught(self):
        block = self.block

        class Tamper(FakeL9):
            def analyse_floor_session(self, request, custody):
                if request.session_id == "r4-alpha":
                    summary = block.raw_file("r4-alpha").parent.parent / "summary.json"
                    summary.write_text(summary.read_text() + " ")
                return super().analyse_floor_session(request, custody)

        self.assertEqual(self.run_driver(Tamper(index=block.index, noisy=False)), 2)
        self.assertIn(["restore", "r4-alpha", "b6_recompress_differs"], self.record()["line_refusals"])
        self.assertEqual(self.record()["restore_cycles"]["r4-alpha"]["after_check"], "b6_recompress_differs")

    def test_without_the_restore_the_unit_cannot_read_its_bytes(self):
        """Counterfactual for the restore: the fake, like L9, refuses compressed bytes."""
        self.assertEqual(self.run_driver(self.fake(), restore=False), 2)
        codes = {row["code"] for row in self.record()["nodes"] if row["node"].startswith("floor:")}
        self.assertEqual(codes, {"session_bytes_not_plain"})


class Determinism(Harness):
    def test_serial_and_parallel_give_identical_bytes(self):
        self.assertEqual(self.run_driver(self.fake(noisy=True), name="serial", workers=1), 0)
        self.assertEqual(self.run_driver(self.fake(noisy=True), name="parallel", workers=4), 0)
        serial = tree_digest(self.tmp / "serial/per-session-1/restricted")
        self.assertEqual(serial, tree_digest(self.tmp / "parallel/per-session-1/restricted"))
        one, four = self.record(name="serial"), self.record(name="parallel")
        self.assertEqual({k: one[k] for k in driver.COMPARED}, {k: four[k] for k in driver.COMPARED})

    def test_the_second_per_session_run_must_reproduce_the_first(self):
        self.both_per_session_runs()
        second = self.record("per-session-2")
        self.assertIsNone(second["comparison"]["differs"])
        self.assertEqual(len(second["comparison"]["against_sha256"]), 64)
        self.assertEqual(self.run_driver(self.fake(), "changed", mode="per-session", run=1), 0)
        changed = self.fake(contrasts={"r1-gamma": {"decode": ("unresolved", 0.5)}})
        self.assertEqual(self.run_driver(changed, "changed", mode="per-session", run=2), 2)
        self.assertEqual(self.record("per-session-2", "changed")["comparison"]["differs"], "nodes")

    def test_a_second_run_needs_a_completed_first(self):
        self.assertEqual(self.run_driver(self.fake(), mode="per-session", run=2), 2)
        self.assertIn("per_session_1_missing_or_incomplete", self.streams[1].getvalue())


class CrossBlockPhase(Harness):
    sessions = WITH_NONCOUNTING

    def test_cross_block_needs_both_per_session_runs_the_close_and_block5(self):
        self.assertEqual(self.run_driver(self.fake(), mode="cross-block"), 2)
        self.assertIn("per_session_1_missing_or_incomplete", self.streams[1].getvalue())
        self.assertEqual(self.run_driver(self.fake(), mode="per-session", run=1), 0)
        self.assertEqual(self.run_driver(self.fake(), mode="cross-block"), 2)
        self.assertIn("per_session_2_missing_or_incomplete", self.streams[1].getvalue())
        self.assertEqual(self.run_driver(self.fake(), mode="per-session", run=2), 0)
        self.assertEqual(self.run_driver(self.fake(), mode="cross-block", block5_release_record=self.tmp / "absent"), 2)
        self.assertIn("block5_not_released", self.streams[1].getvalue())
        self.assertEqual(self.run_driver(self.fake(), mode="cross-block", checkout=lambda r: "1" * 40), 2)
        self.assertIn("analysis_commit_differs_from_per_session_run", self.streams[1].getvalue())
        self.assertEqual(self.run_driver(self.fake(), mode="cross-block"), 0, self.streams[1].getvalue())
        self.assertEqual(self.run_driver(self.fake(), mode="cross-block", run=2), 0)
        self.assertIsNone(self.record("cross-block-2")["comparison"]["differs"])

    def test_lines_over_block5_and_the_counting_sessions(self):
        self.both_per_session_runs()
        adapter = Recording(index=self.block.index)
        self.assertEqual(self.run_driver(adapter, mode="cross-block"), 0)
        self.assertEqual(sorted(c for c in adapter.calls), [("block5", "alpha", ()), ("block5", "beta", ()),
                                                           ("block5", "gamma", ())])
        summary = self.restricted("summary", "cross-block-1")
        for pack, sessions in (("alpha", ["block5", "r1-alpha", "r3-alpha", "r4-alpha"]),
                               ("beta", ["block5", "r1-beta", "r2-beta", "r3-beta"]),
                               ("gamma", ["block5", "r1-gamma", "r2-gamma", "r3-gamma"])):
            for key, row in summary[pack]["quantities"].items():
                if "prefill-p42" in key:
                    self.assertEqual((row["n"], row["note"]), (0, "not computable (n < 2)"))
                else:
                    self.assertEqual(row["sessions"], sessions, key)
        side = self.restricted("side_by_side", "cross-block-1")
        self.assertEqual(len(side["alpha"]["facts"]), 2)
        flagged = self.restricted("flagged_inclusive", "cross-block-1")
        self.assertEqual(flagged["alpha"]["label"], "including sessions that did not count (n = 5)")
        self.assertEqual([a["session_id"] for a in flagged["alpha"]["added_sessions"]], ["r5-alpha"])
        self.assertEqual(flagged["beta"]["label"], "including sessions that did not count: none")
        replication = self.restricted("replication", "cross-block-1")
        self.assertEqual({c: r["word"] for c, r in replication.items()},
                         {"decode": "replicated", "prefill-p2048": "replicated"})

    def test_a_disagreeing_session_is_not_replicated(self):
        disagree = {"block5": {"decode": ("direction_supported", 3.0)}, "r2-gamma": {"decode": ("unresolved", 0.9)}}
        self.both_per_session_runs(lambda: self.fake(contrasts=disagree))
        self.assertEqual(self.run_driver(self.fake(contrasts=disagree), mode="cross-block"), 0)
        self.assertEqual(self.restricted("replication", "cross-block-1")["decode"]["word"], "not replicated")

    def test_whole_machine_values_on_gamma_are_refused(self):
        self.both_per_session_runs(lambda: self.fake(whole_machine_on_gamma=True))
        self.assertEqual(self.run_driver(self.fake(whole_machine_on_gamma=True), mode="cross-block"), 2)
        self.assertIn(["whole_machine", "gamma:gamma:r1-gamma", "whole_machine_not_given_for_gamma"],
                      self.record("cross-block-1")["line_refusals"])

    def test_a_deferred_gamma_runs_in_the_cross_block_phase(self):
        sessions = [("r1-alpha", "alpha", 1, "counting"), ("r1-gamma", "gamma", 1, "counting")]
        self.block = build_block6(self.tmp / "other", sessions)
        self.both_per_session_runs()
        adapter = Recording(index=self.block.index)
        self.assertEqual(self.run_driver(adapter, mode="cross-block"), 0, self.streams[1].getvalue())
        self.assertIn(("gamma", "r1-gamma", ("r1-alpha", "block5")), adapter.calls)
        lines = self.restricted("replication", "cross-block-1")
        self.assertTrue(lines["decode"]["floor_from_block_5"])
        self.assertEqual(lines["decode"]["short"],
                         "short: 1 counting block-6 sessions of the 3 targeted; below the commitment of 2")

    def test_cross_block_refuses_before_the_close(self):
        self.block = build_block6(self.tmp / "other", closed=False)
        self.both_per_session_runs()
        self.assertEqual(self.run_driver(self.fake(), mode="cross-block"), 2)
        self.assertIn("block6_not_closed", self.streams[1].getvalue())


class SingleSession(Harness):
    def test_one_gamma_session_with_its_floors_only(self):
        adapter = Recording(index=self.block.index)
        self.assertEqual(self.run_driver(adapter, mode="session", only="r2-gamma"), 0)
        self.assertEqual(sorted(c[1] for c in adapter.calls), ["r2-beta", "r2-gamma", "r3-alpha"])
        record = self.record("session-r2-gamma")
        self.assertEqual(sorted(record["restricted"]), ["pairings", "sessions"])
        self.assertEqual(sorted(record["restore_cycles"]), ["r2-beta", "r2-gamma", "r3-alpha"])

    def test_one_floor_session(self):
        adapter = Recording(index=self.block.index)
        self.assertEqual(self.run_driver(adapter, mode="session", only="r4-alpha"), 0)
        self.assertEqual(adapter.calls, [("floor", "r4-alpha", ())])

    def test_an_arriving_gamma_before_the_close_is_not_final(self):
        sessions = [("r1-alpha", "alpha", 1, "counting"), ("r1-beta", "beta", 1, "physics_stopped"),
                    ("r1-gamma", "gamma", 1, "counting")]
        self.block = build_block6(self.tmp / "other", sessions, closed=False)
        self.assertEqual(self.run_driver(self.fake(), mode="session", only="r1-gamma"), 0)
        (pairing_row,) = self.record("session-r1-gamma")["pairings"]
        self.assertFalse(pairing_row["final"])
        self.assertEqual(pairing_row["beta"], {"session_id": "block5", "rule": "block5"})

    def test_mode_and_arguments_must_agree(self):
        self.assertEqual(self.run_driver(self.fake(), mode="session"), 2)
        self.assertEqual(self.run_driver(self.fake(), only="r1-alpha"), 2)
        self.assertEqual(self.run_driver(self.fake(), mode="per-session", run=3), 2)

    def test_an_inadmissible_session_is_refused(self):
        sessions = [("r1-alpha", "alpha", 1, "pending_harvest")]
        self.block = build_block6(self.tmp / "other", sessions, decided=set())
        self.assertEqual(self.run_driver(self.fake(), mode="session", only="r1-alpha"), 2)
        self.assertIn("session_not_analysable", self.streams[1].getvalue())


class PublicBytes(Harness):
    """A6: no number, ratio, word or sign of a science quantity in public bytes."""

    def run_subprocess(self, adapter_expression, *extra):
        script = textwrap.dedent(f"""
            import sys
            from pathlib import Path
            from joulewise.b6.analysis import driver
            from tests.b6.analysis.fakes import FakeL9
            sys.exit(driver.analyse(Path({str(self.block.loop)!r}), Path({str(self.block.index)!r}),
                                    Path({str(self.tmp / 'custody')!r}), {adapter_expression},
                                    checkout=lambda r: "0" * 40{''.join(extra)}))
        """)
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "JW_B5_SYNTHETIC_ONLY": "1",
               "TMPDIR": str(tempfile.gettempdir())}
        return subprocess.run([sys.executable, "-c", script], cwd=ROOT, capture_output=True, env=env)

    def assert_structure(self, raw: bytes):
        text = raw.decode("utf-8")
        self.assertTrue(public._text_is_structure(text), text)

    def test_streams_and_record_are_structure_while_restricted_logs_hold_the_noise(self):
        for workers in (1, 3):
            with self.subTest(workers=workers):
                result = self.run_subprocess(f"FakeL9(index={str(self.block.index)!r})", f", workers={workers}")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assert_structure(result.stdout)
                self.assert_structure(result.stderr)
                self.assertEqual(len(result.stdout.splitlines()), 1)
                directory = self.tmp / "custody/per-session-1"
                outside = [p for p in directory.rglob("*") if p.is_file() and "restricted" not in p.relative_to(directory).parts]
                self.assertEqual([p.name for p in outside], [public.PUBLIC_RECORD])
                self.assert_structure(outside[0].read_bytes())
                log = (directory / "restricted/sessions/alpha/r1-alpha/logs/stdout.log").read_text()
                self.assertIn("fd-level 12.5 J", log)
                err = (directory / "restricted/sessions/alpha/r1-alpha/logs/stderr.log").read_text()
                self.assertIn("replicated", err)
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
        self.assertEqual(self.run_driver(self.fake(refuse={"r1-alpha": "not_resolvable"})), 2)
        rows = {row["node"]: row["code"] for row in self.record()["nodes"]}
        self.assertEqual(rows["floor:alpha:r1-alpha"], "restricted_token")

    def test_restricted_flag_codes_appear_only_as_a_count(self):
        from joulewise.flags.catalog import load_catalog
        catalog = load_catalog(ROOT / "configs/b6/flag_catalog_b6.json")
        restricted_codes = sorted(c for c in catalog.codes if catalog.entry(c).get("blinding") == "RESTRICTED")
        codes = ("neg8.survivor_screen_failed",) + tuple(restricted_codes[:1])
        self.block = build_block6(self.tmp / "other", [("r1-alpha", "alpha", 1, "not_counting")],
                                  overrides={"r1-alpha": {"codes": codes}})
        self.run_driver(self.fake())
        (row,) = self.record()["sessions"]
        self.assertEqual(row["flags"], {"codes": ["neg8.survivor_screen_failed"],
                                        "restricted_codes_removed": len(codes) - 1})

    def test_an_unexpected_exception_goes_to_restricted_custody(self):
        class Broken(FakeL9):
            def describe(self):
                raise ValueError("value 26.15 J")

        self.assertEqual(self.run_driver(Broken(index=self.block.index, noisy=False)), 2)
        self.assertNotIn("26.15", self.streams[0].getvalue() + self.streams[1].getvalue())
        self.assertEqual(self.streams[1].getvalue().splitlines()[-1], "analysis - tooling_refusal")
        log = (self.tmp / "custody/per-session-1/restricted/driver-traceback.log").read_text()
        self.assertIn("26.15", log)
        self.assertFalse((self.tmp / "custody/per-session-1" / public.PUBLIC_RECORD).exists())
        # The sessions were compressed again although the run failed late.
        self.assertTrue(self.block.raw_file("r1-alpha").with_name("powermetrics.plist.zst").exists())

    def test_custody_inside_the_repository_or_reused_is_refused(self):
        with redirect_stderr(io.StringIO()):
            self.assertEqual(driver.analyse(self.block.loop, self.block.index, ROOT / "custody-here", self.fake(),
                                            checkout=CLEAN), 2)
        self.assertFalse((ROOT / "custody-here").exists())
        self.assertEqual(self.run_driver(self.fake()), 0)
        self.assertEqual(self.run_driver(self.fake()), 2)

    def test_synthetic_mode_refuses_roots_outside_tmpdir(self):
        os.environ["JW_B5_SYNTHETIC_ONLY"], saved = "1", os.environ.get("JW_B5_SYNTHETIC_ONLY")
        try:
            with redirect_stderr(io.StringIO()) as err:
                code = driver.analyse(self.block.loop, self.block.index, Path("/var/b6-not-tmp"), self.fake(),
                                      checkout=CLEAN)
            self.assertEqual(code, 2)
            self.assertIn("synthetic_root_outside_tmpdir", err.getvalue())
        finally:
            if saved is None:
                os.environ.pop("JW_B5_SYNTHETIC_ONLY", None)
            else:
                os.environ["JW_B5_SYNTHETIC_ONLY"] = saved

    def test_malformed_loop_record_refuses_with_a_structure_line(self):
        (self.block.loop / "attempts.jsonl").write_text("{not json\n")
        result = self.run_subprocess("FakeL9()")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stderr.decode().strip(), "analysis - tooling_refusal loop_record_unreadable")
        self.assertEqual(result.stdout, b"")


class ProductionAdapter(Harness):
    def test_l9_is_called_only_through_the_adapter_and_refuses_until_integrated(self):
        self.assertEqual(self.run_driver(L9ProgramAdapter(self.block.index)), 2)
        record = self.record()
        codes = {row["code"] for row in record["nodes"]}
        self.assertTrue(codes <= {"l9_absent_from_checkout", "l9_session_seam_absent", "paired_floor_not_analysed"}, codes)
        self.assertEqual(record["adapter"]["l9_commit"], "8ad47455ce55203949ea77a3ee330432d5a48101")
        # Refused units still leave every session compressed again.
        self.assertTrue(all(c["after_check"] == "equal" for c in record["restore_cycles"].values()))

    def test_no_driver_module_imports_l9_directly(self):
        for path in sorted((ROOT / "joulewise/b6/analysis").glob("*.py")):
            if path.name != "adapter.py":
                self.assertNotIn("b5_analysis", path.read_text(), path.name)
        self.assertNotIn("b5_analysis", (ROOT / "scripts/b6_analyze.py").read_text())

    def test_no_module_opens_the_export(self):
        """Design §4.1: the export carries hidden-offset factors; numbers come from the bundles."""
        for path in sorted((ROOT / "joulewise/b6/analysis").glob("*.py")):
            self.assertNotIn('"export"', path.read_text(), path.name)
            self.assertNotIn("export_runs", path.read_text(), path.name)

    def test_schedule_refuses_an_unknown_dependency(self):
        bad = (schedule.Node(schedule.GAMMA, SessionRequest("g", "gamma", 1), ("floor:alpha:missing",)),)
        with self.assertRaises(ValueError):
            schedule.execute(self.fake(), bad, self.tmp)


if __name__ == "__main__":
    unittest.main()
