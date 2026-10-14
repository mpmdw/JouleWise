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
        result = check(self.repo, self.base, executed, ["reduce.py"], [], "")
        self.assertEqual(result["unreviewed"], ["reduce.py"])
        self.assertIn("code.number_bearing_unreviewed", result["flags"])
        reviewed = check(self.repo, self.base, executed, ["reduce.py"], [{"commit": executed, "record": "executing review"}], "")
        self.assertEqual(reviewed["unreviewed"], [])
        self.assertEqual(reviewed["flags"], ["code.changed_since_registration"])

    def test_docs_only_and_no_executed_head(self):
        (self.repo / "docs.md").write_text("second\n")
        executed = self.commit()
        self.assertEqual(check(self.repo, self.base, executed, ["reduce.py"], [], "")["flags"],
                         ["code.changed_since_registration"])
        self.assertEqual(check(self.repo, self.base, None, ["reduce.py"], [], "")["flags"],
                         ["code.executed_head_unrecorded"])

    def test_deleted_number_file_is_checked(self):
        (self.repo / "reduce.py").unlink()
        executed = self.commit()
        self.assertEqual(check(self.repo, self.base, executed, ["reduce.py"], [])["unreviewed"], ["reduce.py"])

    def test_equal_commits_need_no_historical_objects(self):
        commit = "a" * 40
        result = check(self.repo / "absent", commit, commit, ["reduce.py"], [], "")
        self.assertEqual(result["changed"], [])
        self.assertEqual(result["flags"], [])

    def test_equal_commits_with_tracked_number_edit_are_unreviewed(self):
        path = "joulewise/adapters/mlx_runtime.py"
        result = check(self.repo / "absent", self.base, self.base, [path], [self.base], " M " + path + "\n")
        self.assertEqual(result["unreviewed"], [path])
        self.assertIn("code.number_bearing_unreviewed", result["flags"])

    def test_non_number_edit_discloses_and_untracked_is_ignored(self):
        result = check(self.repo, self.base, self.base, ["reduce.py"], [], " M docs.md\n?? reduce.py\n")
        self.assertEqual(result["flags"], ["code.changed_since_registration"])
        self.assertEqual(result["changed"], ["docs.md"])

    def test_renames_include_both_paths_and_quoted_names(self):
        for porcelain in ('R  reduce.py -> renamed.py\n', ' R "reduce.py" -> "new file.py"\n',
                          'R  docs.md -> reduce.py\n'):
            result = check(self.repo, self.base, self.base, ["reduce.py"], [], porcelain)
            self.assertEqual(result["unreviewed"], ["reduce.py"])
        result = check(self.repo, self.base, self.base, ["reduce.py"], [], 'R  "old -> file.py" -> "reduce.py"\n')
        self.assertEqual(result["changed"], ["old -> file.py", "reduce.py"])

    def test_absent_porcelain_discloses_even_with_absent_head(self):
        self.assertEqual(check(self.repo, self.base, self.base, [], [])["flags"], ["code.tracked_edits_unrecorded"])
        result = check(self.repo, self.base, None, ["reduce.py"], [], " M reduce.py\n")
        self.assertIn("code.executed_head_unrecorded", result["flags"])
        self.assertIn("code.number_bearing_unreviewed", result["flags"])
