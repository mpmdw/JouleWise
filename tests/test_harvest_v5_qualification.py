"""Immutable, blind qualification verdict; fixture evidence is never live PASS."""
from contextlib import redirect_stdout
import copy
import io
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from joulewise import arm_readiness as readiness, v5_qualification as q
from scripts import harvest_v5_qualification as h
from tests.test_t0_rehearsal import FixtureBuilder, fixture_bundle, fixture_replay


def verdict(status="PASS"):
    return {"overall_verdict": status, "gates": [
        {"gate_id": f"G{i}", "status": "NOT_APPLICABLE", "basis": "retired_by_ruling_76"}
        if i in (6, 7) else {"gate_id": f"G{i}", "status": status} for i in range(1, 11)]}


class QualificationHarvestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.root = FixtureBuilder(self.base).build()
        self.plan_path = self.root / "night_plan.json"
        q.write(self.plan_path, {"fixture": "plan"})
        self.chain = self.base / "chain.zsh"; self.chain.write_text("#!/bin/zsh\nexit 0\n")
        self.sidecar = self.base / "chain.sha256"; self.sidecar.write_text(q.sha(self.chain) + "\n")
        (self.root / "night/chain.started").write_text('{"pgid":999999}\n')
        self.battery = self.base / "battery.json"; q.write(self.battery, {"fixture": "boundary"})
        self.plan = SimpleNamespace(custody_root=str(self.root), plan_id=self.root.name,
            chain_path=str(self.chain), chain_sha256_path=str(self.sidecar))
        self.args = SimpleNamespace(plan=self.plan_path, archive_root=self.base / "harvest", previous_harvest=None,
            replay_source=[], battery_evidence=self.battery, battery_evidence_sha256=q.sha(self.battery))
        lifecycle = q.read(self.root / "records/lifecycle.json")
        for row in lifecycle["stages"]:
            if row["stage_id"] in {"claim_backup", "bound_backup", "close_out", "restore"}:
                stage = self.root / "records" / (row["stage_id"] + ".json")
                q.write(stage, {"schema_version": h.t0_rehearsal.QUALIFICATION_STAGE_SCHEMA, "stage_id": row["stage_id"]})
                row.update(status="COMPLETE", evidence=q.reference(stage))
        (self.root / "records/lifecycle.json").write_bytes(readiness.render_json(lifecycle))
        for patch in (mock.patch.object(q, "load_plan", return_value=self.plan),
                      mock.patch.object(q, "battery_boundaries", return_value=True)):
            patch.start(); self.addCleanup(patch.stop)

    def harvest(self):
        return h.harvest(self.args, clear=lambda *a, **k: True, load=fixture_bundle)

    def test_eight_pass_plus_two_retired_passes_distinct_qualification_verdict(self):
        before = q.tree_hash(self.root)
        with mock.patch.object(h.t0_rehearsal, "evaluate_qualification", return_value=verdict()):
            record = self.harvest()
        self.assertEqual(record["verdict"], "PASS")
        self.assertEqual(record["verdict_kind"], "qualification")
        self.assertEqual(set(record["desk_stages"]), {"claim_backup", "bound_backup", "close_out", "restore"})
        for locator in record["desk_stages"].values():
            self.assertEqual(q.reference(locator["path"]), locator)
        self.assertEqual(record["gate_counts"], {"PASS": 8, "FAIL": 0, "UNRULED": 0, "NOT_APPLICABLE": 2})
        self.assertEqual(q.tree_hash(self.root), before)
        self.assertEqual(record["next_step"], "lead_ratification")  # Decision 8: no kernel writes/closure before seal.
        self.assertTrue((self.args.archive_root / "derived/s1-qualification-verdict.json").exists())
        self.assertFalse((self.args.archive_root / "l10-a").exists())

    def test_missing_or_unhashed_desk_stage_refuses_harvest(self):
        lifecycle = q.read(self.root / "records/lifecycle.json")
        next(row for row in lifecycle["stages"] if row["stage_id"] == "claim_backup")["evidence"]["sha256"] = "0" * 64
        (self.root / "records/lifecycle.json").write_bytes(readiness.render_json(lifecycle))
        with mock.patch.object(h.t0_rehearsal, "evaluate_qualification") as evaluate:
            record = self.harvest()
        self.assertEqual(record["verdict"], "REFUSED")
        self.assertEqual(record["cause_codes"], ["s1_desk_stage_digest_mismatch"])
        evaluate.assert_not_called()

    def test_producer_fault_fails_only_qualification_no_recover(self):
        (self.root / "night/producer-faults.jsonl").write_text('{"producer":"hid"}\n')
        with mock.patch.object(h.t0_rehearsal, "evaluate_qualification") as evaluate:
            record = self.harvest()
        evaluate.assert_not_called()
        self.assertEqual(record["verdict"], "FAIL")
        self.assertEqual(record["cause_codes"], ["qualification_observation_producer_fault"])
        self.assertFalse(record["end_state"])
        self.assertEqual(record["next_step"], "r3_identical_byte_reharvest")
        self.assertFalse(record["s2_eligible"])
        self.assertFalse((self.root / "night/g2b-verdict.json").exists())

    def test_live_gate_failure_is_fail_not_g2b_recovery(self):
        value = verdict(); value["gates"][2]["status"] = "FAIL"
        value["overall_verdict"] = "FAIL"
        with mock.patch.object(h.t0_rehearsal, "evaluate_qualification", return_value=value):
            record = self.harvest()
        self.assertEqual(record["verdict"], "FAIL")
        self.assertTrue(record["end_state"])
        self.assertEqual(record["cause_codes"], ["g3_not_passed"])

    def test_retired_gate_pass_is_wire_refusal(self):
        for index in (5, 6):
            value = verdict(); value["gates"][index]["status"] = "PASS"
            with self.subTest(index=index), mock.patch.object(h.t0_rehearsal, "evaluate_qualification", return_value=value):
                with self.assertRaisesRegex(q.HarvestRefusal, "evaluator_wire"):
                    h.evaluate(object(), transcript=self.base / f"fault-{index}.txt")

    def test_metrics_and_nested_messages_stay_withheld(self):
        value = verdict(); value["gross_energy_j"] = 314159
        for row in value["gates"]: row["message"] = "secret power_w=271828"
        def evaluate(_):
            print("raw secret measured duration")
            return value
        output = io.StringIO()
        with redirect_stdout(output), mock.patch.object(h.t0_rehearsal, "evaluate_qualification", side_effect=evaluate):
            record = self.harvest()
        public = readiness.render_json(record) + (self.args.archive_root / "derived/s1-qualification-verdict.json").read_bytes()
        for leaked in (b"314159", b"271828", b"secret", b"gross_energy"):
            self.assertNotIn(leaked, public)
        self.assertEqual(output.getvalue(), "")
        self.assertIn("raw secret", (self.args.archive_root / "withheld/t0-evaluation.txt").read_text())
        with self.assertRaisesRegex(q.HarvestRefusal, "claim_plan_seal"):
            q.release_metrics()

    def test_reharvest_requires_same_bytes_and_new_archive(self):
        with mock.patch.object(h.t0_rehearsal, "evaluate_qualification", side_effect=RuntimeError("fixture fault")):
            self.assertEqual(self.harvest()["verdict"], "REFUSED")
        old = self.args.archive_root
        self.args.previous_harvest = old; self.args.archive_root = self.base / "reharvest"
        with mock.patch.object(h.t0_rehearsal, "evaluate_qualification", return_value=verdict()):
            self.assertEqual(self.harvest()["verdict"], "PASS")
        self.assertEqual(q.read(old / "harvest.json")["verdict"], "REFUSED")
        self.args.archive_root = self.base / "changed"
        (self.root / "changed-bytes").write_text("fault")
        with self.assertRaisesRegex(q.HarvestRefusal, "reharvest_source_bytes_changed"):
            self.harvest()


if __name__ == "__main__": unittest.main()
