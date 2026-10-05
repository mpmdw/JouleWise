"""Measured-offset and a2 -> G10 -> s1 kill-tests; fixture evidence only."""
import shutil
from pathlib import Path
import subprocess
from types import SimpleNamespace
import unittest
from unittest import mock

from joulewise import arm_readiness as readiness, arm_readiness_evidence_t0 as author
from joulewise import v5_qualification as q, t0_rehearsal as t0
from scripts import capture_t0_step, write_v5_qualification_plan as writer
from scripts.ed_session import capture_t0_anchor_positive_control as g10
from tests import test_v5_qualification_plan as plan_fixture
from tests.test_capture_t0_anchor_positive_control import ControlFixture


class G10PlacementTests(unittest.TestCase):
    def setUp(self):
        self.control = ControlFixture(self)
        self.assertEqual(self.control.run()["status"], "DISCHARGED")
        self.plan_case = plan_fixture.PrerequisiteTests()
        self.plan_case.setUp()
        self.addCleanup(self.plan_case.doCleanups)
        self.base = self.control.case.base_ns
        self.boot = self.control.case.stamp()["boot_id"]
        self.head = subprocess.check_output([
            "git", "-C", str(self.control.case.repository), "rev-parse", "HEAD"], text=True).strip()
        self.refs = self.plan_case.refs
        for label, check, start in (("a1", self.base - 4 * 10**9, self.base - 5 * 10**9),
                                    ("a2", self.base - 2 * 10**9, self.base - 3 * 10**9)):
            path, value = self.plan_case.controls[label]
            context = Path(value["context"]["path"])
            context.write_bytes(readiness.render_json({"head": self.head}))
            observation = Path(value["observation"]["path"])
            observation.write_bytes(readiness.render_json({"first_t0_boundary_monotonic_ns": start}))
            value.update(checked_monotonic_ns=check, boot_session_id=self.boot,
                context=q.reference(context), observation=q.reference(observation), arm_receipt=q.reference(observation))
            path.write_bytes(readiness.render_json(value))
            self.refs[label + "_control"] = q.reference(path)
        self.refs.update(g10_control=q.reference(self.control.case.control / "positive-control.json"),
            g10_artifacts=[q.reference(self.control.case.control / "custody-manifest.json")])
        self.custody = self.plan_case.custody
        self.plan = self.custody / "night-plan.json"
        q.write(self.plan, {"measurement_root": str(self.control.case.repository),
                            "pack_night": {"pack_id": self.control.case.pack.name}})
        self.boundary = self.base + 2 * 10**9
        self.set_s1_boundary(self.boundary)
        shutil.copytree(self.control.case.control, self.custody / "records/g10-custody" / self.control.case.control.name)
        self.save_record()

    def save_record(self):
        path = self.custody / "qualification-plan-record.json"
        path.write_bytes(readiness.render_json({"head": self.head, "plan": q.reference(self.plan), "prerequisites": self.refs}))

    def set_s1_boundary(self, at, *, boot=None):
        root = self.custody / self.control.case.pack.name / author._INPUT_DIRECTORY
        root.mkdir(parents=True, exist_ok=True)
        for index, filename in enumerate(author._CAPTURE_FILES.values()):
            (root / filename).write_bytes(readiness.render_json({
                "started_monotonic_ns": at + index * 1000, "boot_session_id": boot or self.boot}))

    def write(self, *, at=None, boot=None):
        with mock.patch.object(writer.time, "monotonic_ns", return_value=self.boundary if at is None else at), \
             mock.patch.object(readiness, "_current_boot_session_id", return_value=boot or self.boot):
            writer.prerequisites("s1", self.refs, self.head, 3000, self.custody,
                code_root=self.control.case.repository)

    def replay(self):
        return q.replay_g10_custody(self.custody, g10.read_json(self.control.case.control / "positive-control.json"))

    def test_new_placement_passes_writer_and_harvester_after_a1_and_a2(self):
        self.write()
        self.assertEqual(self.replay(), self.refs["g10_artifacts"][0])

    def test_harvester_boundary_is_bound_to_the_loaded_capture_bytes(self):
        root = self.custody / self.control.case.pack.name / author._INPUT_DIRECTORY
        artifacts = tuple(t0.EvidenceArtifact(p.relative_to(self.custody).as_posix(), p,
            p.read_bytes(), q.sha(p), q.read(p)) for p in sorted(root.glob("*.json")))
        bundle = SimpleNamespace(artifacts=artifacts)
        positive = g10.read_json(self.control.case.control / "positive-control.json")
        self.assertEqual(q.replay_g10_custody(self.custody, positive, bundle=bundle), self.refs["g10_artifacts"][0])
        path = root / "clock-reference.json"
        value = q.read(path)
        value["started_monotonic_ns"] += 1
        path.write_bytes(readiness.render_json(value))
        with self.assertRaisesRegex(ValueError, "g10_s1_boundary_custody"):
            q.replay_g10_custody(self.custody, positive, bundle=bundle)

    def test_g10_before_a2_check_refuses_writer_and_harvester(self):
        path, value = self.plan_case.controls["a2"]
        value["checked_monotonic_ns"] = self.base + 1
        path.write_bytes(readiness.render_json(value))
        self.refs["a2_control"] = q.reference(path)
        self.save_record()
        for operation in (self.write, self.replay):
            with self.subTest(operation=operation.__name__), self.assertRaisesRegex(ValueError, "g10_boot_or_order"):
                operation()

    def test_g10_last_stamp_at_or_after_s1_first_boundary_refuses(self):
        for boundary in (self.base, self.base - 1):
            with self.subTest(boundary=boundary):
                self.set_s1_boundary(boundary)
                with self.assertRaisesRegex(ValueError, "g10_boot_or_order"):
                    self.replay()
                with self.assertRaisesRegex(ValueError, "g10_boot_or_order"):
                    self.write(at=boundary)

    def test_off_receipt_at_or_after_upper_bound_refuses_without_late_author_stamp(self):
        path = self.control.case.control / "network_time_off.json"
        value = g10.read_json(path)
        value["monotonic_s"] = self.boundary / 1e9
        path.write_bytes(readiness.render_json(value))
        (self.control.case.control / "commands/off.json").write_bytes(readiness.render_json(value))
        self.control.reseal()
        self.refs["g10_artifacts"] = [q.reference(self.control.case.control / "custody-manifest.json")]
        self.save_record()
        for operation in (self.write, self.replay):
            with self.subTest(operation=operation.__name__), self.assertRaisesRegex(ValueError, "g10_boot_or_order"):
                operation()

    def test_different_s1_boot_refuses_writer_and_harvester(self):
        other = "00000000-0000-0000-0000-000000000001"
        with self.assertRaises(ValueError):
            self.write(boot=other)
        self.set_s1_boundary(self.boundary, boot=other)
        with self.assertRaisesRegex(ValueError, "g10_boot_or_order"):
            self.replay()

    def test_different_a1_boot_refuses_writer_and_harvester(self):
        path, value = self.plan_case.controls["a1"]
        value["boot_session_id"] = "00000000-0000-0000-0000-000000000001"
        path.write_bytes(readiness.render_json(value))
        self.refs["a1_control"] = q.reference(path)
        self.save_record()
        with self.assertRaisesRegex(ValueError, "a1_before_a2"):
            self.write()
        with self.assertRaisesRegex(ValueError, "g10_boot_or_order"):
            self.replay()


class PreparationIsolationTests(unittest.TestCase):
    def test_run_rechecks_offset_after_standalone_preflight_passes(self):
        fixture = ControlFixture(self, offset="0.020")
        with mock.patch.object(g10, "REPO_ROOT", fixture.case.repository):
            result, _ = g10.check_preflight(sample=fixture.case.sample, runner=fixture.runner)
        self.assertEqual(result["status"], "PASS")
        self.assertFalse(fixture.case.control.exists())
        fixture.offset = "0.019"
        self.assertEqual(fixture.run(), {"status": "g10_preflight_offset_too_small", "g10_attempt": False})
        self.assertEqual(fixture.argv, [g10.preflight_argv(fixture.case.repository)] * 2)
        self.assertNotIn(g10.ON_ARGV, fixture.argv)
        self.assertEqual(fixture.case.author_calls, [])

    def test_preparation_cannot_reach_arm_reference_resync_on(self):
        for offset, expected_ons in (("0.020", 1), ("1.150", 0)):
            with self.subTest(offset=offset):
                fixture = ControlFixture(self, offset=offset)
                def forbidden_resync(*args, **kwargs):
                    fixture.runner(g10.ON_ARGV, timeout=30)
                    raise AssertionError("preparation entered _arm_reference")
                with mock.patch.object(capture_t0_step, "_arm_reference", side_effect=forbidden_resync) as arm, \
                     mock.patch.object(capture_t0_step, "capture_step", side_effect=AssertionError("capture preparation invoked")) as capture:
                    result = fixture.run()
                arm.assert_not_called()
                capture.assert_not_called()
                self.assertEqual(fixture.argv.count(g10.ON_ARGV), expected_ons)
                self.assertEqual(result["status"], "DISCHARGED" if expected_ons else "g10_preflight_offset_too_large")
                if not expected_ons:
                    self.assertFalse(result["g10_attempt"])


if __name__ == "__main__":
    unittest.main()
