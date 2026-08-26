from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/window_status.sh"


class WindowStatusGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repository = Path(self.temporary.name) / "repository"
        self.repository.mkdir()
        self._git("init", "-q")
        self._git("config", "user.name", "JouleWise Test")
        self._git("config", "user.email", "joulewise-test@example.invalid")
        (self.repository / "README.md").write_text("initial\n", encoding="utf-8")
        self._git("add", "README.md")
        self._git("commit", "-qm", "initial")

    def _git(self, *args: str) -> str:
        return subprocess.run(
            ("git", *args),
            cwd=self.repository,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    def _run_status(self, sentinel: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ("/bin/bash", str(SCRIPT), "idle", "Synthetic status"),
            cwd=ROOT,
            env={
                **os.environ,
                "JOULEWISE_STATUS_REPO": str(self.repository),
                "JOULEWISE_COMMIT_FREEZE_SENTINEL": str(sentinel),
            },
            capture_output=True,
            text=True,
        )

    def test_present_sentinel_writes_status_without_git_publication(self) -> None:
        sentinel = Path(self.temporary.name) / "COMMIT_FREEZE_OPEN"
        sentinel.write_text("open\n", encoding="utf-8")
        head_before = self._git("rev-parse", "HEAD")

        completed = self._run_status(sentinel)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue((self.repository / "WINDOW_STATUS.md").is_file())
        self.assertEqual(self._git("rev-parse", "HEAD"), head_before)
        self.assertEqual(self._git("diff", "--cached", "--name-only"), "")
        self.assertEqual(self._git("status", "--short"), "?? WINDOW_STATUS.md")
        self.assertIn(
            "freeze span open: status written locally, not published.",
            completed.stdout,
        )

    def test_absent_sentinel_commits_status_as_before(self) -> None:
        sentinel = Path(self.temporary.name) / "sentinel-does-not-exist"
        commit_count_before = int(self._git("rev-list", "--count", "HEAD"))

        completed = self._run_status(sentinel)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue((self.repository / "WINDOW_STATUS.md").is_file())
        self.assertEqual(
            int(self._git("rev-list", "--count", "HEAD")),
            commit_count_before + 1,
        )
        self.assertEqual(
            self._git("log", "-1", "--format=%s"),
            "status: idle — Synthetic status",
        )
        self.assertEqual(
            self._git("show", "--pretty=format:", "--name-only", "HEAD"),
            "WINDOW_STATUS.md",
        )
        self.assertEqual(self._git("status", "--short"), "")


if __name__ == "__main__":
    unittest.main()
