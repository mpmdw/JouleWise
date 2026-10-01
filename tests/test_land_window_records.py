"""GAP 3: real harvest records become discoverable in the next HEAD tree."""
import contextlib
import copy
import io
from pathlib import Path
import subprocess
import tempfile
import unittest

from scripts import land_window_records as landing
from scripts import issue_calibration_acceptance_generation as issuer
from tests.git_fixture import init_git_fixture
from tests import test_harvest_window as windows


class LandWindowRecordsTests(unittest.TestCase):
    def test_gap3_landing_commits_referenced_bytes_refuses_bad_digest_and_preserves_null_absences(self):
        fixture = windows.HarvestWindowTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        fixture.revision6_fixture(fill_slots=0, abort_reason="start refused")
        record = fixture.run_harvest()
        harvest_path = fixture.args.custody / "harvest.json"
        self.assertEqual(record["valid_captures"], 0)
        self.assertEqual(record["sessions"][-1]["captures"], [])

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            init_git_fixture(root, "-q")

            def git(*arguments):
                return subprocess.run(["git", "-C", str(root), *arguments],
                    capture_output=True, text=True, check=True).stdout.strip()

            git("config", "user.name", "fixture")
            git("config", "user.email", "fixture@example.invalid")
            (root / "README").write_text("landing checkout\n")
            git("add", "README")
            git("commit", "-q", "-m", "initial")
            original_head = git("rev-parse", "HEAD")
            (root / "unrelated.txt").write_text("preserve staged work\n")
            git("add", "unrelated.txt")

            # Each present reference must authenticate before any copies or
            # Git mutations. The same harvested bytes exercise every refusal.
            bad_path = fixture.base / "bad-harvest.json"
            for label in ("r9_window", "start_conditions", "window_end.source"):
                bad = copy.deepcopy(record)
                reference = bad["window_end"]["source"] if label == "window_end.source" else bad[label]
                reference["sha256"] = "0" * 64
                bad_path.write_bytes(windows.harvest.json_bytes(bad))
                with self.subTest(reference=label), self.assertRaisesRegex(issuer.PrepareRefusal, "sha256 disagreement"):
                    landing.land(bad_path, root, "docs/bad")
                self.assertFalse((root / "docs").exists())
                self.assertEqual(git("rev-parse", "HEAD"), original_head)

            bad = copy.deepcopy(record)
            bad["start_conditions"]["path"] = "night/missing.json"
            bad_path.write_bytes(windows.harvest.json_bytes(bad))
            with self.assertRaises(issuer.PrepareRefusal):
                landing.land(bad_path, root, "docs/bad")
            self.assertFalse((root / "docs").exists())

            # Existing different destination bytes are never overwritten.
            conflict = root / "docs/conflict/harvest.json"
            conflict.parent.mkdir(parents=True)
            conflict.write_bytes(b"existing owner bytes")
            with self.assertRaisesRegex(landing.LandingRefusal, "different bytes"):
                landing.land(harvest_path, root, "docs/conflict")
            self.assertEqual(conflict.read_bytes(), b"existing owner bytes")
            self.assertEqual(git("rev-parse", "HEAD"), original_head)

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                self.assertEqual(landing.main(["--harvest", str(harvest_path), "--repo-root", str(root)]), 0)
            base = f"docs/process_traces/rev6-windows/{fixture.sid}"
            references = (record["r9_window"], record["start_conditions"], record["window_end"]["source"])
            expected = sorted([f"{base}/harvest.json", *[f"{base}/{ref['path']}" for ref in references]])
            lines = stdout.getvalue().splitlines()
            commit = git("rev-parse", "HEAD")
            self.assertEqual(lines, expected + [commit])
            self.assertEqual(git("log", "-1", "--format=%s"), f"Harvest {fixture.sid}: window records")
            self.assertEqual(git("diff-tree", "--no-commit-id", "--name-only", "-r", commit).splitlines(), expected)
            self.assertEqual(git("diff", "--cached", "--name-only"), "unrelated.txt")
            self.assertEqual((root / base / "harvest.json").read_bytes(), harvest_path.read_bytes())
            for reference in references:
                source = Path(record["custody_root"]) / reference["path"]
                raw = source.read_bytes()
                self.assertEqual((root / base / reference["path"]).read_bytes(), raw)
                self.assertEqual(landing.digest(raw), reference["sha256"])
                self.assertEqual(issuer._revision_six_committed(source, raw, root), commit)
            self.assertEqual(issuer._revision_six_committed(harvest_path, harvest_path.read_bytes(), root), commit)

            # A null harvest without start or exit references lands exactly
            # its R9 and harvest records; it never synthesizes timing evidence.
            null = copy.deepcopy(record)
            del null["start_conditions"]
            null["window_end"] = None
            null_path = fixture.base / "null-harvest.json"
            null_path.write_bytes(windows.harvest.json_bytes(null))
            paths, null_commit = landing.land(null_path, root, "docs/null")
            self.assertEqual(paths, ["docs/null/harvest.json", "docs/null/harvest/r9_window.json"])
            self.assertEqual(sorted(path.relative_to(root).as_posix() for path in (root / "docs/null").rglob("*")
                                    if path.is_file()), paths)
            self.assertEqual((root / "docs/null/harvest.json").read_bytes(), null_path.read_bytes())
            self.assertEqual(git("diff-tree", "--no-commit-id", "--name-only", "-r", null_commit).splitlines(), paths)


if __name__ == "__main__":
    unittest.main()
