import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import b6_replay_acceptance as replay
from tests.b6.test_export_runs import archive_fixture
from tests.b6.support import write_json


class ReplayTests(unittest.TestCase):
    def test_protected_roots_and_symlink_are_denied_before_open(self):
        policy = replay.ReadPolicy()
        for path in [*(root + "/absent" for root in replay.FORBIDDEN_ROOTS), replay.FORBIDDEN_ARCHIVE_PREFIX + "fixture/archive"]:
            with self.assertRaises(PermissionError):
                policy.check(path)
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / "alias"
            link.symlink_to("/Users/edr/night-b5/absent")
            with self.assertRaises(PermissionError):
                policy.check(link)

    def test_plan_binding_fallbacks_and_owning_reader_opens_are_guarded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive, _reg, plan, _record = archive_fixture(root)
            # Remove the cloned plan so the reader would follow this fallback.
            (archive / "sources/pack/plan_tree.json").unlink()
            plan["pack_root"] = "/Users/edr/night-custody/absent"
            write_json(archive / "sources/night-custody/night_plan.json", plan)
            policy = replay.ReadPolicy()
            sys.addaudithook(policy.audit)
            result = replay.replay(archive, root / "scratch", policy)
            self.assertTrue(result["skipped"])
            self.assertIn("source_skipped: protected path", result["notes"])
            # These are actual open/list events, regardless of which reader
            # follows the path; no protected file or directory is touched.
            with policy.enabled():
                with self.assertRaises(PermissionError):
                    Path("/Users/edr/night-g2a/absent").read_bytes()
                with self.assertRaises(PermissionError):
                    list(Path("/Users/edr/night-b5/absent").iterdir())

    def test_non_claim_replay_stdout_equals_markdown_and_only_structure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive, _reg, plan, _record = archive_fixture(root)
            write_json(archive / "sources/night-custody/night_plan.json", plan)
            out_path = root / "replay.md"
            with contextlib.redirect_stdout(io.StringIO()) as stdout:
                self.assertEqual(replay.main([str(archive), "--non-claim", "--out", str(out_path)]), 0)
            self.assertEqual(stdout.getvalue(), out_path.read_text())
            self.assertIn('"verdict": "EXCLUDE"', stdout.getvalue())
            self.assertIn('"neg8.survivor_screen_undefined"', stdout.getvalue())
            self.assertNotIn("_j", stdout.getvalue())
            self.assertNotIn("operative_bound_s", stdout.getvalue())
            self.assertFalse((archive / "withheld/b6-neg8.json").exists())
