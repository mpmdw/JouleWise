"""Supplemental desk compositions, never evidence of live qualification.

The closeout -> G9 seam is native. Its existing desk fixture substitutes plan
loading and pack metadata/rosters, so this does not discharge addendum C.6's
full driver -> assembly -> qualification acceptance. The author-journal
control runs the real census even on hosts where the process list is denied.
"""
from pathlib import Path
import tempfile
import unittest

from joulewise import arm_readiness as readiness, arm_readiness_evidence_t0 as author
from joulewise import t0_rehearsal as t0
from scripts import produce_t0_rehearsal_bundle as producer
from tests import test_t0_rehearsal as historical
from tests import test_v5_s1_desk_closeout as desk_fixture


class NativeProducerCompositionTests(unittest.TestCase):
    def test_native_closeout_four_copies_on_two_roots_pass_real_g9(self):
        case = desk_fixture.DeskCloseoutTests()
        case.setUp()
        self.addCleanup(case.doCleanups)
        self.assertNotEqual(case.custody, case.arm_root)
        self.assertNotIn(case.custody, case.arm_root.parents)
        self.assertNotIn(case.arm_root, case.custody.parents)
        context = case.custody / case.go["pack_id"] / "arm_readiness.t0.inputs/arm-context.json"
        context.write_bytes(readiness.render_json(case.context))
        chain = case.base / "desk-chain.zsh"
        chain.write_text("export V5_QUALIFICATION_OCCURRENCE=s1\nexport NIGHT_ARM_CONTEXT_SHA256="
                         + producer.reference(context)["sha256"] + "\n")
        case.plan_path.write_bytes(readiness.render_json({"plan_id": case.plan.plan_id,
            "custody_root": str(case.custody), "chain_path": str(chain),
            "measurement_root": str(case.measurement), "pack_night": {"pack_id": case.go["pack_id"]}}))
        case.go.update(plan_sha256=producer.reference(case.plan_path)["sha256"],
                       window_chain_sha256=producer.reference(chain)["sha256"])
        (case.night / "go_receipt.json").write_bytes(readiness.render_json(case.go))
        case.record["plan"] = producer.reference(case.plan_path)
        case.record_path.write_bytes(readiness.render_json(case.record))
        (case.night / "chain.started").write_bytes(readiness.render_json({"pid": 777, "monotonic_ns": 10}))
        for name in ("launch", "capability_consumption", "capture"):
            (case.stage_dir / (name + ".json")).unlink()
        producer.observe_s1_lifecycle(case.plan)
        lifecycle_path = case.custody / "records/lifecycle.json"
        lifecycle_path.unlink()
        case.close()
        lifecycle = {"schema_version": t0.QUALIFICATION_LIFECYCLE_SCHEMA,
            "stages": [{"stage_id": name, "status": "COMPLETE",
                        "evidence": producer.reference(case.stage_dir / (name + ".json"))}
                       for name in t0._LIFECYCLE_STAGES],
            "operator_actions_at_t0": 0, "human_interventions": []}
        lifecycle_path.write_bytes(readiness.render_json(lifecycle))
        result = t0.evaluate_g9(historical.fixture_bundle(case.custody))
        self.assertEqual(result.status, t0.GateStatus.PASS, result.message)

    def test_real_author_tempfile_probe_stdout_is_journaled(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            journal = root / "process-observations.jsonl"
            probes = (producer.night_gate.AGENT_CENSUS_ARGV,
                      ("/usr/bin/pgrep", "-x", "caffeinate"),
                      ("/usr/bin/pgrep", "-lf", author._BROWSER_CENSUS_PATTERN),
                      ("/usr/bin/pgrep", "-lf", author._MONITOR_CENSUS_PATTERN))
            with t0.process_journal(journal):
                answers = [author._execute_probe(argv, cwd=root) for argv in probes]
            events = [readiness.parse_json_bytes(line) for line in journal.read_bytes().splitlines()]
            outputs = [row for row in events if row["event"] == "output"]
            exits = [row for row in events if row["event"] == "exit"]
            spawns = [row for row in events if row["event"] == "spawn"]
            self.assertEqual(len(outputs), len(probes))
            self.assertEqual(len(exits), len(probes))
            for argv, answer, output, exited, spawn in zip(probes, answers, outputs, exits, spawns):
                with self.subTest(argv=argv):
                    self.assertEqual(output["argv"], list(argv))
                    self.assertEqual(output["stdout"], answer.stdout)
                    self.assertEqual(exited["exit_code"], answer.exit_code)
                    self.assertEqual(spawn["stdin_fd0_target"], "/dev/null")
                    self.assertEqual(t0.qualification_process_outcome(spawn["argv"]),
                                     {"exit_code": 1, "stdout": ""})
