import copy
import dataclasses
import importlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from joulewise.b6 import acceptance, acceptance_interface, calibration
from joulewise.b6.acceptance_interface import CaptureEvidence, MemberEvidence, StageEvidence
from joulewise.flags.schema import validate_flag
from scripts import b6_acceptance
from tests.b6.support import IDENTITY, ROOT, prepared, registration_dir, session, write_json


class AcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.prepared = prepared(self.root)

    def evaluate(self, evidence=None, prepared=None):
        return acceptance.ACCEPTANCE.evaluate(prepared or self.prepared, evidence or session())

    def test_clean_synthetic_and_no_energy_fields(self):
        evidence = session()
        result = self.evaluate(evidence)
        self.assertEqual(result.verdict, "ACCEPT")
        self.assertTrue(result.counting)
        self.assertFalse(result.structural)
        self.assertEqual(result.reasons, ())
        self.assertEqual(result.record["cells"], {"decode": {"repeat": 5}})
        self.assertEqual(result.record["neg8"]["verdict"], "pending")

        def walk(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    self.assertFalse(key.endswith(("_j", "_w", "_j2", "_w2")), key)
                    walk(child)
            elif isinstance(value, (tuple, list)):
                for child in value:
                    walk(child)
        walk(result.record)
        self.assertTrue(all(not validate_flag(row) for row in result.record["emitted_flags"]))
        self.assertEqual(result, self.evaluate(evidence))
        with patch.object(Path, "read_text", side_effect=AssertionError("evaluate reads no files")), \
             patch("time.time", side_effect=AssertionError("evaluate reads no clock")):
            self.assertEqual(result, self.evaluate(evidence))

    def test_block_five_record_refusals_now_flags(self):
        codes = ("calibration.ledger_snapshot_refused", "whole_window.verdict_absent", "pack.identity_mismatch",
                 "clock.systematic", "code.identity_unmeasured", "neg8.screen_failed",
                 "records.malformed_flag_exclusion_possible")
        result = self.evaluate(dataclasses.replace(session(), window_flags=codes))
        self.assertEqual(result.verdict, "ACCEPT")
        self.assertTrue(set(codes) <= set(result.flags))
        self.assertEqual(result.reasons, ())

    def test_unknown_code_discloses(self):
        result = self.evaluate(dataclasses.replace(session(), window_flags=("unknown.desk_condition",)))
        self.assertEqual(result.verdict, "ACCEPT")
        self.assertIn("catalog.code_unclassified", result.flags)
        self.assertIn("unknown.desk_condition", result.flags)

    def test_foreign_unclassified_flag_is_still_recorded(self):
        flag = acceptance._flag("unknown.other_attempt", self.prepared.catalog)
        flag["scope"]["plan_id"] = "other"
        base = session()
        result = self.evaluate(dataclasses.replace(base, runtime={**IDENTITY, "_b6": {"flags": [flag], "plan_id": "own"}}))
        self.assertEqual(result.verdict, "ACCEPT")
        self.assertIn("catalog.code_unclassified", result.flags)

    def test_other_session_systematic_and_doubling_shape_accepts(self):
        rows = [{"session_id": "other", "seq": i, "value_s": ".028", "disposition": "valid"} for i in range(48)]
        rows.append({"session_id": "other", "seq": 100, "disposition": "systematic-invalid"})
        prepared_rows = dataclasses.replace(self.prepared, capture_rows=tuple(rows))
        result = self.evaluate(prepared=prepared_rows)
        self.assertEqual(result.verdict, "ACCEPT")
        self.assertIn("calibration.other_session_systematic", result.flags)
        self.assertIn("calibration.corpus_doubling_reached", result.flags)

    def test_absent_post_and_refit_failure_exclude(self):
        first = session()
        for post in (None, CaptureEvidence("post", None, "refit_failed", True)):
            captures = (first.captures[0],) if post is None else (first.captures[0], post)
            result = self.evaluate(dataclasses.replace(first, captures=captures))
            self.assertIn("calibration.bracket_incomplete", result.reasons)
            self.assertEqual(result.verdict, "EXCLUDE")

    def test_model_bytes_stack_and_missing_identity(self):
        base = session()
        member = base.stages[0].members[0]
        for changed, expected in (({"model_artifact_sha256": "b" * 64}, "model.files_differ_from_registered"),
                                  ({"packages": {**IDENTITY["packages"], "mlx": "changed"}}, "model.stack_differs_from_registered"),
                                  ({"status": "missing"}, None)):
            replaced = dataclasses.replace(member, runtime={**IDENTITY, **changed})
            stage = dataclasses.replace(base.stages[0], members=(replaced,) + base.stages[0].members[1:])
            result = self.evaluate(dataclasses.replace(base, stages=(stage,)))
            if expected:
                self.assertEqual(result.verdict, "EXCLUDE")
                self.assertIn(expected, result.reasons)
            else:
                self.assertEqual(result.verdict, "ACCEPT")
                self.assertIn("model.identity_unrecorded", result.flags)

    def test_unreviewed_code_excludes(self):
        code = {**self.prepared.code, "flags": ["code.changed_since_registration", "code.number_bearing_unreviewed"],
                "changed": ["joulewise/reduce.py"], "number_bearing_changed": ["joulewise/reduce.py"],
                "unreviewed": ["joulewise/reduce.py"]}
        result = self.evaluate(prepared=dataclasses.replace(self.prepared, code=code))
        self.assertIn("code.number_bearing_unreviewed", result.reasons)
        reviewed = {**code, "unreviewed": [], "flags": ["code.changed_since_registration"]}
        self.assertEqual(self.evaluate(prepared=dataclasses.replace(self.prepared, code=reviewed)).verdict, "ACCEPT")

    def test_physics_stop_kept_noncounting_crash_structural(self):
        for reason in acceptance.PHYSICS_STOP_REASONS:
            result = self.evaluate(dataclasses.replace(session(), stop_reason=reason))
            self.assertEqual(result.verdict, "ACCEPT")
            self.assertFalse(result.counting)
            self.assertFalse(result.structural)
            self.assertTrue(result.record["physics_stop"])
        crashed = self.evaluate(dataclasses.replace(session(), stop_reason="unexpected_crash"))
        self.assertEqual(crashed.verdict, "EXCLUDE")
        self.assertTrue(crashed.structural)
        self.assertIn("structure.chain_crashed", crashed.reasons)

    def test_smoke_count_reasons_expected_other_exclusions_structural(self):
        evidence = dataclasses.replace(session(1, synthetic=False), runtime={**IDENTITY, "_b6": {"smoke": True}})
        result = self.evaluate(evidence)
        self.assertFalse(result.structural)
        self.assertEqual({row["code"] for row in result.record["expected_in_smoke"]},
                         {"cell.below_minimum", "neg8.survivor_screen_undefined"})
        physical = self.evaluate(dataclasses.replace(evidence, window_flags=("clock.step_overlap_calibration",)))
        self.assertTrue(physical.structural)

    def test_missing_record_classes_and_missing_middle_stage(self):
        base = session()
        result = self.evaluate(dataclasses.replace(base, stages=(), captures=()))
        self.assertIn("structure.no_capture_records", result.reasons)
        self.assertIn("structure.no_roster", result.reasons)
        self.assertTrue(result.structural)
        stage = StageEvidence("missing", "campaign_collection", 5,
                              (MemberEvidence("missing", "missing-member", "failed", runtime={"bundle_present": False}),))
        result = self.evaluate(dataclasses.replace(base, stages=(stage, *base.stages)))
        self.assertIn("structure.missing_stage_bundles", result.reasons)
        self.assertTrue(result.structural)
        failures_with_bundles = dataclasses.replace(stage, members=(dataclasses.replace(stage.members[0], runtime={"bundle_present": True}),))
        result = self.evaluate(dataclasses.replace(base, stages=(failures_with_bundles, *base.stages)))
        self.assertFalse(result.structural)

    def test_source_changed_is_harvest_rerun(self):
        result = self.evaluate(dataclasses.replace(session(), window_flags=("records.source_changed_during_harvest",)))
        self.assertEqual(result.verdict, "HARVEST_RERUN")
        self.assertFalse(result.counting)

    def test_loss_excludes_unit_and_duplicate_positions_have_no_unit(self):
        base = session()
        member = dataclasses.replace(base.stages[0].members[0], flags=("agent.unit_overlap",))
        stage = dataclasses.replace(base.stages[0], members=(member, *base.stages[0].members[1:]))
        result = self.evaluate(dataclasses.replace(base, stages=(stage,)))
        self.assertEqual(result.record["cells"]["decode"]["repeat"], 4)
        self.assertIn("cell.below_minimum", result.reasons)
        stage = dataclasses.replace(base.stages[0], members=(*base.stages[0].members, base.stages[0].members[0]))
        result = self.evaluate(dataclasses.replace(base, stages=(stage,)))
        self.assertEqual(result.record["cells"]["decode"]["repeat"], 4)
        self.assertIn("roster.duplicate_run_id", result.flags)
        self.assertNotIn("roster.duplicate_run_id", result.reasons)

    def test_member_exclusion_keeps_session_when_units_remain_defined(self):
        base = session(6)
        stage = dataclasses.replace(base.stages[0], members=(dataclasses.replace(base.stages[0].members[0],
            flags=("agent.unit_overlap",)), *base.stages[0].members[1:]))
        result = self.evaluate(dataclasses.replace(base, stages=(stage,)))
        self.assertEqual(result.verdict, "ACCEPT")
        self.assertEqual(result.reasons, ())
        self.assertEqual(result.record["cells"]["decode"]["repeat"], 5)
        self.assertTrue(any(item["scope"] == "member" and item["run_id"] == "s0" for item in result.record["excluding"]))

    def test_neg8_record_only_projects_counts_and_verdict(self):
        neg8 = {"verdict": "passed", "survivors": {"start": 3, "midpoint": 1, "end": 2}, "corpus_clean_n": 12,
                "families": {"gross": {"bound_j": 123.0}}}
        result = self.evaluate(dataclasses.replace(session(synthetic=False), runtime={**IDENTITY, "_b6": {"neg8": neg8}}))
        self.assertEqual(result.verdict, "ACCEPT")
        self.assertNotIn("families", result.record["neg8"])
        self.assertNotIn("123.0", json.dumps(result.record))
        neg8["verdict"] = "failed"
        failed = self.evaluate(dataclasses.replace(session(synthetic=False), runtime={**IDENTITY, "_b6": {"neg8": neg8}}))
        self.assertIn("neg8.survivor_screen_failed", failed.reasons)

    def test_precheck_constructors_without_additive_fields_and_stub(self):
        old_member = MemberEvidence("science", "s0", "succeeded")
        base = session()
        old_style = acceptance_interface.SessionEvidence(base.pack_id,
            (StageEvidence("science", "campaign_collection", 1, (old_member,)),),
            base.captures, IDENTITY, True, ())
        self.assertEqual(self.evaluate(old_style).verdict, "ACCEPT")
        self.assertIs(acceptance_interface.load_acceptance(), acceptance.ACCEPTANCE)
        with patch.dict("sys.modules", {"joulewise.b6.acceptance": None}):
            stub = acceptance_interface.load_acceptance()
        self.assertIsInstance(stub, acceptance_interface.StubAcceptance)
        self.assertEqual(stub.evaluate(stub.prepare(), old_style).verdict, "UNAVAILABLE")

    def test_precheck_constructor_units_resolved_from_prepared_roster(self):
        blueprint = {"members": [{"run_id": f"s{i}", "units": [{"cell_id": "decode", "stratum": "repeat", "unit_id": str(i)}]}
                                 for i in range(5)], "cells": [{"cell_id": "decode", "strata": ["repeat"]}]}
        members = tuple(MemberEvidence("science", f"s{i}", "succeeded") for i in range(5))
        evidence = dataclasses.replace(session(), stages=(StageEvidence("science", "campaign_collection", 5, members),))
        result = self.evaluate(evidence, dataclasses.replace(self.prepared, roster=blueprint))
        self.assertEqual(result.verdict, "ACCEPT")
        self.assertEqual(result.record["cells"]["decode"]["repeat"], 5)


class ArchiveAndCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.reg_dir = registration_dir(self.root)
        self.archive = self.root / "archive"
        self.plan = {"pack_id": "desk-pack", "session_id": "session", "pre_calibration_dir": str(self.root / "pre"),
                     "post_calibration_dir": str(self.root / "post"), "chain_exit_code": 0}
        self.plan_path = self.root / "plan.json"
        write_json(self.plan_path, self.plan)
        write_json(self.archive / "derived/code-identity.json", {"executed_head": None})
        write_json(self.archive / "derived/roster.json", {"pack_id": "desk-pack",
            "cells": [{"cell_id": "decode", "strata": ["repeat"]}], "members": [{"run_id": f"s{i}",
            "stage_id": "science", "units": [{"cell_id": "decode", "stratum": "repeat", "unit_id": str(i)}]} for i in range(5)]})
        for i in range(5):
            write_json(self.archive / "sources/claim-runs" / f"s{i}" / "metadata.json", IDENTITY)
            write_json(self.archive / "sources/claim-runs" / f"s{i}" / "status.json", {"status": "succeeded"})
        (self.archive / "derived/flags.jsonl").write_text("")
        write_json(self.archive / "withheld/spans.json", {"spans": {"s0": {"member": [1, 2]}}})
        write_json(self.archive / "withheld/b6-neg8.json", {"verdict": "passed", "survivors": {"start": 3, "midpoint": 1, "end": 3},
                                                        "corpus_clean_n": 12, "bound_j": 100})

    def read(self):
        with patch.object(calibration, "read_own_capture", return_value=calibration.Capture(Decimal(".028"), "valid")):
            return acceptance.evidence_from_archive(self.archive, self.plan, self.reg_dir)

    def test_archive_reads_clones_status_spans_and_stop(self):
        evidence = self.read()
        self.assertEqual(evidence.stop_reason, "completed")
        self.assertEqual(len(evidence.stages[0].members), 5)
        self.assertEqual(evidence.runtime["_b6"]["spans"]["s0"], {"monotonic_ns": [1, 2]})
        self.assertNotIn("bound_j", evidence.runtime["_b6"]["neg8"])
        night = self.archive / "sources/night-custody/night"
        night.mkdir(parents=True)
        (night / "chain-stages.jsonl").write_text(json.dumps({"stage_id": "chain.stop", "kind": "sampler_down", "rc": 12}) + "\n")
        self.assertEqual(self.read().stop_reason, "sampler_down")
        write_json(self.archive / "sources/claim-runs/s0/status.json", {"status": "failed"})
        self.assertEqual(self.read().stages[0].members[0].status, "failed")

    def test_capture_refits_keep_exact_times(self):
        exact = Decimal(".02800000000000000001")
        with patch.object(calibration, "read_own_capture", return_value=calibration.Capture(exact, "valid")):
            evidence = acceptance.evidence_from_archive(self.archive, self.plan, self.reg_dir)
        result = acceptance.ACCEPTANCE.evaluate(prepared(self.root), evidence)
        self.assertEqual(result.record["calibration"]["pre_s"], str(exact))

    def test_smoke_tree_omissions_are_expected_not_missing_stages(self):
        tree = {"smoke_reduction": {"schema": "joulewise.b6_smoke_reduction.v1"},
                "science": [{"run_id": f"s{i}", "stage_id": "science"} for i in range(5)],
                "stage_graph": [{"stage_id": "science", "kind": "campaign_collection", "expected_count": 1}]}
        write_json(self.archive / "sources/repo/configs/campaigns/desk-pack/plan_tree.json", tree)
        evidence = self.read()
        self.assertEqual(len(evidence.stages[0].members), 1)
        result = acceptance.ACCEPTANCE.evaluate(prepared(self.root), evidence)
        self.assertFalse(result.structural)
        self.assertEqual(result.record["mode"], "smoke")
        self.assertIn("cell.below_minimum", {r["code"] for r in result.record["expected_in_smoke"]})

    def test_cli_creates_once_valid_flags_one_stdout_line(self):
        argv = ["--archive", str(self.archive), "--plan", str(self.plan_path), "--registration-dir", str(self.reg_dir)]
        with patch.object(calibration, "read_own_capture", return_value=calibration.Capture(Decimal(".028"), "valid")), \
             redirect_stdout(io.StringIO()) as out:
            self.assertEqual(b6_acceptance.main(argv), 0)
        lines = out.getvalue().splitlines()
        self.assertEqual(len(lines), 1)
        summary = json.loads(lines[0])
        self.assertEqual(summary["verdict"], "ACCEPT")
        self.assertEqual(set(summary), {"verdict", "counting", "structural", "flag_counts"})
        flags = [json.loads(line) for line in (self.archive / "derived/b6-flags.jsonl").read_text().splitlines()]
        self.assertTrue(flags)
        self.assertTrue(all(validate_flag(row) == [] for row in flags))
        original = (self.archive / "derived/b6-acceptance.json").read_bytes()
        with patch.object(calibration, "read_own_capture", return_value=calibration.Capture(Decimal(".028"), "valid")), \
             redirect_stderr(io.StringIO()), redirect_stdout(io.StringIO()) as out:
            self.assertEqual(b6_acceptance.main(argv), 1)
            self.assertEqual(out.getvalue(), "")
        self.assertEqual(original, (self.archive / "derived/b6-acceptance.json").read_bytes())

    def test_cli_program_fault_prints_no_payload(self):
        with redirect_stdout(io.StringIO()) as out, redirect_stderr(io.StringIO()) as err:
            self.assertEqual(b6_acceptance.main(["--archive", str(self.archive), "--plan", "/synthetic/missing-plan",
                                                "--registration-dir", str(self.reg_dir)]), 1)
        self.assertEqual(out.getvalue(), "")
        self.assertIn("program fault: FileNotFoundError", err.getvalue())

    def test_all_three_pack_stage_roles_in_plan_order(self):
        for pack in ("d117_floor_qwen3-1p7b_v5", "d117_floor_qwen3-8b_v5", "d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5"):
            tree = json.loads((ROOT / "configs/campaigns" / pack / "plan_tree.json").read_text())
            stages, roles = acceptance._stage_roles(tree)
            self.assertEqual(len(stages), 107 if "contrast" in pack else 125)
            self.assertEqual(sum(role == "corpus" for role in roles.values()), 18)
