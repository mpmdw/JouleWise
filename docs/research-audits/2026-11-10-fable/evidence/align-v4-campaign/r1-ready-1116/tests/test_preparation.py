"""Off-host regression tests. Temporary Git clones and synthetic host commands only."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("r1_verify_sources", HERE / "verify_sources.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)
KIT = json.loads((HERE / "KIT.json").read_text())
SOURCE = Path(os.environ["R1_SOURCE_ROOT"]).resolve()


class SourceChecks(unittest.TestCase):
    def test_real_pinned_sources_pass_without_claiming_native_readiness(self):
        result = verify.check(SOURCE)
        self.assertEqual(result["head"], KIT["measurement_commit"])
        self.assertFalse(result["native_ready"])

    def test_other_commit_refuses_before_file_reads(self):
        with patch.object(verify.subprocess, "check_output", return_value="0" * 40):
            with self.assertRaisesRegex(ValueError, "HEAD differs"):
                verify.check(SOURCE)

    def test_changed_gate_byte_refuses(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in KIT["source_sha256"]:
                dest = root / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(SOURCE / name, dest)
            path = root / "joulewise/align/apple/thermal_gates.py"
            path.write_bytes(path.read_bytes() + b"\n")
            with patch.object(verify.subprocess, "check_output", return_value=KIT["measurement_commit"]):
                with self.assertRaisesRegex(ValueError, "source differs:.*thermal_gates"):
                    verify.check(root)

    def test_dangling_retired_receipt_refuses_unread(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in KIT["source_sha256"]:
                dest = root / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(SOURCE / name, dest)
            (root / "configs/campaigns/align_v4/registration/ruling_1f_receipt.json").symlink_to("missing")
            with patch.object(verify.subprocess, "check_output", return_value=KIT["measurement_commit"]):
                with self.assertRaisesRegex(ValueError, "retired ruling_1f_receipt"):
                    verify.check(root)

    def test_priority_and_plan_are_unissued_and_not_campaign_input(self):
        entry = json.loads((HERE / "ENTRY-DRAFT.json").read_text())
        plan = json.loads((HERE / "PLAN-INPUTS-DRAFT.json").read_text())
        self.assertEqual(entry["status"], "DRAFT_NOT_CONTROLLER_INPUT")
        self.assertEqual(entry["kind"], "v4-session")
        self.assertIn("LEAD FILLS", entry["lead_ready_record"])
        self.assertEqual(plan["window_max_s"], 119880)
        self.assertIsNone(plan["expected_s"])
        self.assertNotIn("ac_powermode", plan)


class StageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="jw-r1-stage-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.repo = self.root / "repo"
        subprocess.run(["git", "clone", "--quiet", "--shared", "--no-checkout", str(SOURCE), str(self.repo)], check=True, capture_output=True)
        self.wt = self.root / "worktree"
        self.out = self.root / "preparation"
        self.fences = self.root / "fences"
        self.fences.mkdir()
        bin_dir = self.root / "bin"
        bin_dir.mkdir()
        for name, source in {
            "pgrep": '#!/bin/sh\nexit "${STAGE_TEST_PGREP_RC:-1}"\n',
            "launchctl": '#!/bin/sh\nprintf "%s\\n" "${STAGE_TEST_JOB:-}"\nexit "${STAGE_TEST_LAUNCHCTL_RC:-0}"\n',
        }.items():
            path = bin_dir / name
            path.write_text(source)
            path.chmod(0o755)
        venv = self.root / "existing-venv"
        (venv / "bin").mkdir(parents=True)
        (venv / "bin/python").symlink_to(shutil.which("python3.13"))
        (venv / "lib").mkdir()
        (venv / "pyvenv.cfg").write_text("synthetic existing environment\n")
        self.env = dict(os.environ, JW_CLOSE_WINDOW_CONFIRMED="yes", JW_NO_FETCH="1",
                        JW_REPO=str(self.repo), JW_R1_WT=str(self.wt), JW_R1_STAGE=str(self.out),
                        JW_FENCE_ROOT=str(self.fences), JW_R1_VENV=str(venv),
                        PATH=str(bin_dir) + os.pathsep + os.environ["PATH"])

    def stage(self, *args):
        return subprocess.run(["zsh", str(HERE / "stage_mbp_r1.sh"), *args], env=self.env, text=True, capture_output=True)

    def assert_refused(self, text, *args):
        result = self.stage(*args)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(text, result.stderr)

    def test_stage_then_repeat_preserves_checkout_and_uses_existing_environment(self):
        first = self.stage()
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(verify.check(self.wt)["head"], KIT["measurement_commit"])
        self.assertTrue((self.wt / ".venv").is_dir())
        self.assertTrue((self.wt / ".venv/bin").is_symlink())
        self.assertEqual((self.out / "KIT.json").read_bytes(), (HERE / "KIT.json").read_bytes())
        again = self.stage()
        self.assertEqual(again.returncode, 0, again.stderr)
        self.assertIn("SOURCE STAGED ONLY", again.stdout)

    def test_dry_run_leaves_worktree_and_outputs_absent(self):
        result = self.stage("--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.wt.exists())
        self.assertFalse(self.out.exists())

    def test_missing_close_confirmation_refuses(self):
        self.env.pop("JW_CLOSE_WINDOW_CONFIRMED")
        self.assert_refused("lead must confirm")
        self.assertFalse(self.wt.exists())

    def test_live_fence_refuses_without_reading_or_removing_it(self):
        fence = self.fences / "desk_fence.json"
        fence.write_text("synthetic opaque fence")
        self.assert_refused("desk fence exists")
        self.assertEqual(fence.read_text(), "synthetic opaque fence")

    def test_missing_fence_root_refuses(self):
        self.fences.rmdir()
        self.assert_refused("fence observation root unavailable")

    def test_live_process_or_process_observation_failure_refuses(self):
        for rc in ("0", "2"):
            with self.subTest(rc=rc):
                self.env["STAGE_TEST_PGREP_RC"] = rc
                self.assert_refused("runner/monitor/offload")

    def test_loaded_job_or_launchctl_observation_error_refuses(self):
        self.env["STAGE_TEST_JOB"] = "123 - com.joulewise.night"
        self.assert_refused("job loaded")
        self.env["STAGE_TEST_JOB"] = ""
        self.env["STAGE_TEST_LAUNCHCTL_RC"] = "1"
        self.assert_refused("launchctl observation failed")

    def test_dirty_checkout_refuses_and_preserves_change(self):
        self.assertEqual(self.stage().returncode, 0)
        path = self.wt / "local-user-note"
        path.write_text("preserve")
        self.assert_refused("dirty")
        self.assertEqual(path.read_text(), "preserve")

    def test_attached_checkout_refuses(self):
        self.assertEqual(self.stage().returncode, 0)
        subprocess.run(["git", "-C", str(self.wt), "switch", "-c", "test-attached"], check=True, capture_output=True)
        self.assert_refused("attached")

    def test_wrong_existing_head_refuses(self):
        self.assertEqual(self.stage().returncode, 0)
        subprocess.run(["git", "-C", str(self.wt), "switch", "--detach", "HEAD^"], check=True, capture_output=True)
        self.assert_refused("another HEAD")

    def test_changed_preparation_is_never_overwritten(self):
        self.assertEqual(self.stage().returncode, 0)
        path = self.out / "KIT.json"
        path.write_text("preserve changed preparation")
        self.assert_refused("existing preparation differs")
        self.assertEqual(path.read_text(), "preserve changed preparation")

    def test_symlink_or_nested_destinations_refuse(self):
        self.wt.symlink_to(self.repo, target_is_directory=True)
        self.assert_refused("symlink destination")
        self.env["JW_R1_WT"] = str(self.repo / "nested")
        self.assert_refused("must be separate")


if __name__ == "__main__":
    unittest.main()
