"""Fixture-only r1 harvest; never claims a physical G gate was discharged."""
from contextlib import redirect_stdout
from dataclasses import replace
import io
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from joulewise import arm_readiness as readiness, v5_qualification as q
from scripts import harvest_v5_pack_rehearsal as h
from tests.test_t0_rehearsal import FixtureBuilder, fixture_bundle, fixture_replay

SCRATCH = Path(tempfile.gettempdir())


class RehearsalHarvestTests(unittest.TestCase):
    def setUp(self):
        SCRATCH.mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=SCRATCH)
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.root = FixtureBuilder(self.base).build()
        self.manifest = self.root / h.loader.MANIFEST_NAME
        self.complete = q.read(self.manifest)
        self.g7 = Path(self.complete["records"].pop("g7_control")["path"])
        self.g7_staged = self.base / "g7-staged"
        self.g7.parent.parent.rename(self.g7_staged)
        self.manifest.write_bytes(readiness.render_json(self.complete))
        self.plan_path = self.root / "night_plan.json"
        q.write(self.plan_path, {"fixture": "plan"})
        self.chain = self.base / "chain.zsh"
        self.chain.write_text("#!/bin/zsh\nexit 0\n")
        self.sidecar = self.base / "chain.sha256"
        self.sidecar.write_text(q.sha(self.chain) + "\n")
        (self.root / "night/chain.started").write_text('{"pgid":999999}\n')
        self.battery = self.base / "battery.json"
        q.write(self.battery, {"fixture": "battery-boundary"})
        self.plan = SimpleNamespace(custody_root=str(self.root), plan_id=self.root.name,
                                    chain_path=str(self.chain), chain_sha256_path=str(self.sidecar))
        self.args = SimpleNamespace(plan=self.plan_path, archive_root=self.base / "initial", g7_control=None,
            initial_harvest=None, previous_harvest=None, replay_source=[], battery_evidence=self.battery,
            battery_evidence_sha256=q.sha(self.battery))
        self.plan_patch = mock.patch.object(q, "load_plan", return_value=self.plan).start()
        self.addCleanup(mock.patch.stopall)
        mock.patch.object(q, "battery_boundaries", return_value=True).start()

    def run_harvest(self):
        with fixture_replay(self.root):
            return h.harvest(self.args, clear=lambda *a, **k: True, load=fixture_bundle)

    def test_two_stage_real_evaluator_ten_pass_without_source_manifest_edit(self):
        before = q.tree_hash(self.root)
        initial = self.run_harvest()
        self.assertEqual(initial["verdict"], "RECOVER")
        self.assertEqual(initial["cause_codes"], ["g7_not_passed"])
        self.assertFalse(initial["end_state"])
        self.args.initial_harvest = self.args.archive_root
        self.args.archive_root = self.base / "final"
        self.args.g7_control = self.g7
        self.g7_staged.rename(self.g7.parent.parent)
        final = self.run_harvest()
        self.assertEqual(final["verdict"], "PASS")
        self.assertEqual(final["gate_counts"], {"PASS": 10, "FAIL": 0, "UNRULED": 0})
        self.assertEqual(q.tree_hash(self.root), before)
        self.assertNotIn("g7_control", q.read(self.manifest)["records"])
        self.assertIn("g7_control", q.read(self.args.archive_root / "derived/t0-rehearsal-bundle.json")["records"])
        self.assertEqual(q.read(self.args.initial_harvest / "harvest.json")["stage"], "initial")
        self.assertTrue((self.args.archive_root / "SHA256SUMS").is_file())

    def test_swapped_manifest_members_fail_actual_g_evaluators(self):
        data = q.read(self.manifest)
        a, b = "execution", "positive_control"
        data["records"][a], data["records"][b] = data["records"][b], data["records"][a]
        self.manifest.write_bytes(readiness.render_json(data))
        result = self.run_harvest()
        self.assertEqual(result["verdict"], "RECOVER")
        self.assertIn("g1_not_passed", result["cause_codes"])
        self.assertIn("g10_not_passed", result["cause_codes"])
        self.assertTrue(result["end_state"])

    def test_missing_manifest_member_fails_loader_and_cannot_null_started_chain(self):
        data = q.read(self.manifest)
        del data["records"]["execution"]
        self.manifest.write_bytes(readiness.render_json(data))
        self.assertEqual(self.run_harvest()["verdict"], "REFUSED")

    def test_missing_record_bytes_recover_not_pass(self):
        (self.root / "records/execution.json").unlink()
        result = self.run_harvest()
        self.assertEqual(result["verdict"], "RECOVER")
        self.assertIn("g1_not_passed", result["cause_codes"])

    def test_unruled_gate_and_incomplete_overall_cannot_pass(self):
        value = {"overall_verdict": "INCOMPLETE", "gates": [
            {"gate_id": f"G{i}", "status": "UNRULED" if i == 7 else "PASS"} for i in range(1, 11)]}
        with mock.patch.object(h.t0_rehearsal, "evaluate_rehearsal", return_value=value):
            result = h.evaluate(object(), transcript=self.base / "restricted/transcript.txt")
        self.assertEqual(result["overall_verdict"], "FAIL")

    def test_nested_metrics_and_log_tail_never_enter_public_gate_json(self):
        def malicious(_):
            print("UNFILTERED-TAIL secret measured duration energy power")
            return {"overall_verdict": "PASS", "nested": {"gross_energy_j": 314159}, "gates": [
                {"gate_id": f"G{i}", "status": "PASS", "message": "secret metric",
                 "mechanical_evidence": [{"nested": {"power_w": 271828}}]} for i in range(1, 11)]}
        out = io.StringIO()
        with redirect_stdout(out), mock.patch.object(h.t0_rehearsal, "evaluate_rehearsal", side_effect=malicious):
            result = self.run_harvest()
        public = readiness.render_json(result) + (self.args.archive_root / "derived/t0-rehearsal-verdict.json").read_bytes()
        self.assertNotIn(b"314159", public)
        self.assertNotIn(b"271828", public)
        self.assertNotIn(b"secret", public)
        self.assertNotIn("UNFILTERED-TAIL", out.getvalue())
        self.assertIn("UNFILTERED-TAIL", (self.args.archive_root / "withheld/t0-evaluation.txt").read_text())
        with self.assertRaisesRegex(q.HarvestRefusal, "claim_plan_seal"):
            q.release_metrics(sealed=False)

    def test_source_tree_mutation_is_refused(self):
        def mutate(bundle):
            (self.root / "tampered").write_text("changed")
            return {"overall_verdict": "PASS", "gates": [{"gate_id": f"G{i}", "status": "PASS"} for i in range(1, 11)]}
        with mock.patch.object(h.t0_rehearsal, "evaluate_rehearsal", side_effect=mutate):
            result = self.run_harvest()
        self.assertEqual(result["verdict"], "REFUSED")
        self.assertEqual(result["cause_codes"], ["source_tree_mutated"])

    def test_refused_reharvest_requires_identical_sources_and_new_archive(self):
        with mock.patch.object(h.t0_rehearsal, "evaluate_rehearsal", side_effect=RuntimeError("withheld diagnostic")):
            initial = self.run_harvest()
        self.assertEqual(initial["verdict"], "REFUSED")
        previous = self.args.archive_root
        old = (previous / "harvest.json").read_bytes()
        self.args.archive_root = self.base / "reharvest"
        self.args.previous_harvest = previous
        result = self.run_harvest()
        self.assertEqual(result["verdict"], "RECOVER")
        self.assertEqual((previous / "harvest.json").read_bytes(), old)
        self.args.archive_root = self.base / "bad-reharvest"
        (self.root / "records/execution.json").write_text("{}\n")
        with self.assertRaisesRegex(q.HarvestRefusal, "reharvest_source_bytes_changed"):
            self.run_harvest()

    def test_refused_final_stage_reharvest_authenticates_both_prior_stages(self):
        self.run_harvest()
        self.args.initial_harvest = self.args.archive_root
        self.args.archive_root = self.base / "final-refused"
        self.args.g7_control = self.g7
        self.g7_staged.rename(self.g7.parent.parent)
        with mock.patch.object(h.t0_rehearsal, "evaluate_rehearsal", side_effect=RuntimeError("private fault")):
            failed = self.run_harvest()
        self.assertEqual(failed["verdict"], "REFUSED")
        self.args.previous_harvest = self.args.archive_root
        self.args.archive_root = self.base / "final-reharvest"
        self.assertEqual(self.run_harvest()["verdict"], "PASS")
        self.assertEqual(q.read(self.args.previous_harvest / "harvest.json")["verdict"], "REFUSED")

    def test_live_pending_launcher_group_cannot_be_null(self):
        night = self.base / "pending-night"
        night.mkdir()
        pending = {"schema": "joulewise.launch_pending.v1", "pid": 54321, "pgid": 54321,
                   "start_time": "fixture", "plan_id": "fixture", "attempt_id": "one", "epoch_s": 1.0}
        q.write(night / "launch.pending", pending)
        self.assertFalse(q.group_clear(night, killpg=lambda *a: None, plan_id="fixture"))
        self.assertTrue(q.group_clear(night, killpg=mock.Mock(side_effect=ProcessLookupError), plan_id="fixture"))
        q.write(night / "launch.resolved", {"schema": "joulewise.launch_resolved.v1", "basis": "group_absent",
                                            "pgid": 54321, "epoch_s": 2.0, "monotonic_ns": 2})
        kill = mock.Mock(side_effect=AssertionError("closed group must not be reprobed"))
        self.assertTrue(q.group_clear(night, killpg=kill, plan_id="fixture"))
        kill.assert_not_called()

    def test_preflight_fault_retains_structural_refused_record_in_safe_scratch(self):
        out = io.StringIO()
        with redirect_stdout(out):
            result = q.preflight_refusal(h.SCHEMA, self.base / "safe-refusals")
        self.assertEqual(result["verdict"], "REFUSED")
        path, = (self.base / "safe-refusals").glob("*/harvest.json")
        self.assertEqual(q.read(path), result)
        self.assertIn("verdict=REFUSED", out.getvalue())
        self.assertNotIn("fault detail", out.getvalue())


if __name__ == "__main__":
    unittest.main()
