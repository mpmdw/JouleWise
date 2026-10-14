import subprocess
import tempfile
import unittest
from pathlib import Path

from joulewise.b6.code_check import check
from tests.git_fixture import init_git_fixture


class CodeCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        init_git_fixture(self.repo)
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "user.name", "Fixture")
        (self.repo / "reduce.py").write_text("first\n")
        (self.repo / "docs.md").write_text("first\n")
        self.base = self.commit()

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.repo), *args], check=True,
                              capture_output=True, text=True).stdout.strip()

    def commit(self):
        self.git("add", ".")
        self.git("commit", "-m", "synthetic fixture")
        return self.git("rev-parse", "HEAD")

    def test_unreviewed_number_change_and_reviewed_change(self):
        (self.repo / "reduce.py").write_text("second\n")
        executed = self.commit()
        result = check(self.repo, self.base, executed, ["reduce.py"], [])
        self.assertEqual(result["unreviewed"], ["reduce.py"])
        self.assertIn("code.number_bearing_unreviewed", result["flags"])
        reviewed = check(self.repo, self.base, executed, ["reduce.py"], [{"commit": executed, "record": "executing review"}])
        self.assertEqual(reviewed["unreviewed"], [])
        self.assertEqual(reviewed["flags"], ["code.changed_since_registration"])

    def test_docs_only_and_no_executed_head(self):
        (self.repo / "docs.md").write_text("second\n")
        executed = self.commit()
        self.assertEqual(check(self.repo, self.base, executed, ["reduce.py"], [])["flags"],
                         ["code.changed_since_registration"])
        self.assertEqual(check(self.repo, self.base, None, ["reduce.py"], [])["flags"],
                         ["code.executed_head_unrecorded"])

    def test_deleted_number_file_is_checked(self):
        (self.repo / "reduce.py").unlink()
        executed = self.commit()
        self.assertEqual(check(self.repo, self.base, executed, ["reduce.py"], [])["unreviewed"], ["reduce.py"])

    def test_equal_commits_need_no_historical_objects(self):
        commit = "a" * 40
        result = check(self.repo / "absent", commit, commit, ["reduce.py"], [])
        self.assertEqual(result["changed"], [])
        self.assertEqual(result["flags"], [])
