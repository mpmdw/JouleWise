from __future__ import annotations

import json
import contextlib
import io
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.lint_runsheet_epoch import lint_contract, main


RUNSHEET = "docs/runsheet.md"


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        stdout=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip()


def _contract(runsheet_revision: str, executing_head: str) -> dict[str, object]:
    return {
        "schema": "joulewise.runsheet_epoch_lint",
        "runsheet": RUNSHEET,
        "runsheet_revision": runsheet_revision,
        "executing_head": executing_head,
        "checks": [
            {
                "id": "symbol",
                "kind": "symbol_existence",
                "reference": "tests/sample.py:test_known",
                "source_path": "tests/sample.py",
                "symbol": "SampleTests.test_known",
            },
            {
                "id": "cli",
                "kind": "contract_required_cli_inputs",
                "block_anchor": "capture 101-ordinary",
                "command": "scripts/tool.py\" freeze",
                "required_flags": ["--table", "--digest"],
            },
            {
                "id": "coordinates",
                "kind": "file_line_coordinates",
                "reference": "scripts/tool.py:1-5",
                "source_path": "scripts/tool.py",
                "start_symbol": "parser",
                "end_symbol": "main",
                "cited_start": 1,
                "cited_end": 5,
            },
        ],
    }


class RunsheetEpochLintTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.repo = Path(self.temporary.name)
        _git(self.repo, "init", "-q")
        _git(self.repo, "config", "user.name", "Epoch Lint Test")
        _git(self.repo, "config", "user.email", "epoch-lint@example.invalid")
        (self.repo / "docs").mkdir()
        (self.repo / "scripts").mkdir()
        (self.repo / "tests").mkdir()
        (self.repo / "scripts/tool.py").write_text(
            "def parser():\n    return 'parser'\n\n"
            "def main():\n    return 'main'\n",
            encoding="utf-8",
        )
        (self.repo / "tests/sample.py").write_text(
            "class SampleTests:\n"
            "    def test_known(self):\n"
            "        return True\n",
            encoding="utf-8",
        )
        (self.repo / RUNSHEET).write_text(self._runsheet(), encoding="utf-8")
        _git(self.repo, "add", ".")
        _git(self.repo, "commit", "-qm", "clean epoch")
        self.clean_head = _git(self.repo, "rev-parse", "HEAD")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    @staticmethod
    def _runsheet(*, symbol: str = "test_known", digest: bool = True) -> str:
        table_line = "  --table table.json \\\n" if digest else "  --table table.json\n"
        digest_line = "  --digest value\n" if digest else ""
        return (
            f"Reference tests/sample.py:{symbol}\n"
            "Coordinate scripts/tool.py:1-5\n\n"
            "```zsh\n"
            "capture 101-ordinary python \"scripts/tool.py\" freeze \\\n"
            f"{table_line}"
            f"{digest_line}"
            "```\n"
        )

    def test_clean_named_git_objects_pass_all_three_kinds(self) -> None:
        result = lint_contract(self.repo, _contract(self.clean_head, self.clean_head))
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["check_count"], 3)
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["runsheet_revision"], self.clean_head)
        self.assertEqual(result["executing_head"], self.clean_head)

    def test_counterfactual_pre_cure_shape_reports_all_three_kinds(self) -> None:
        (self.repo / RUNSHEET).write_text(
            self._runsheet(symbol="test_removed", digest=False), encoding="utf-8"
        )
        _git(self.repo, "add", RUNSHEET)
        _git(self.repo, "commit", "-qm", "stale runsheet")
        stale_runsheet = _git(self.repo, "rev-parse", "HEAD")

        tool = self.repo / "scripts/tool.py"
        tool.write_text(
            "# later interface growth\n" + tool.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        _git(self.repo, "add", "scripts/tool.py")
        _git(self.repo, "commit", "-qm", "move executing surface")
        moved_head = _git(self.repo, "rev-parse", "HEAD")

        contract = _contract(stale_runsheet, moved_head)
        contract["checks"][0]["reference"] = "tests/sample.py:test_removed"  # type: ignore[index]
        contract["checks"][0]["symbol"] = "SampleTests.test_removed"  # type: ignore[index]
        result = lint_contract(self.repo, contract)

        self.assertEqual(result["status"], "REFUSE")
        self.assertEqual(result["finding_count"], 3)
        self.assertEqual(
            {finding["kind"] for finding in result["findings"]},
            {
                "symbol_existence",
                "contract_required_cli_inputs",
                "file_line_coordinates",
            },
        )
        self.assertEqual(
            {finding["reason"] for finding in result["findings"]},
            {
                "symbol_missing_or_ambiguous",
                "contract_required_cli_input_missing",
                "file_line_coordinates_stale",
            },
        )

    def test_required_flag_in_neighboring_block_does_not_discharge_command(self) -> None:
        text = self._runsheet(digest=False) + (
            "\n```zsh\n"
            "echo --digest only-in-another-block\n"
            "```\n"
        )
        (self.repo / RUNSHEET).write_text(text, encoding="utf-8")
        _git(self.repo, "add", RUNSHEET)
        _git(self.repo, "commit", "-qm", "neighboring flag")
        head = _git(self.repo, "rev-parse", "HEAD")
        result = lint_contract(self.repo, _contract(head, self.clean_head))
        self.assertEqual(result["status"], "REFUSE")
        cli = [item for item in result["findings"] if item["kind"] == "contract_required_cli_inputs"]
        self.assertEqual(len(cli), 1)
        self.assertIn("--digest", cli[0]["detail"])

    def test_required_flag_in_neighboring_command_does_not_discharge_invocation(self) -> None:
        text = self._runsheet(digest=False).replace(
            "```\n", "echo --digest only-in-another-command\n```\n"
        )
        (self.repo / RUNSHEET).write_text(text, encoding="utf-8")
        _git(self.repo, "add", RUNSHEET)
        _git(self.repo, "commit", "-qm", "neighboring command flag")
        head = _git(self.repo, "rev-parse", "HEAD")
        result = lint_contract(self.repo, _contract(head, self.clean_head))
        self.assertEqual(result["status"], "REFUSE")
        cli = [
            item
            for item in result["findings"]
            if item["kind"] == "contract_required_cli_inputs"
        ]
        self.assertEqual(len(cli), 1)
        self.assertIn("--digest", cli[0]["detail"])

    def test_dirty_worktree_cannot_make_named_clean_objects_pass(self) -> None:
        (self.repo / "tests/sample.py").write_text("", encoding="utf-8")
        (self.repo / RUNSHEET).write_text(self._runsheet(digest=False), encoding="utf-8")
        result = lint_contract(self.repo, _contract(self.clean_head, self.clean_head))
        self.assertEqual(result["status"], "PASS")

    def test_invalid_revision_is_exit_two_and_named(self) -> None:
        contract = _contract("does-not-exist", self.clean_head)
        path = self.repo / "contract.json"
        path.write_text(json.dumps(contract), encoding="utf-8")
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = main([str(path), "--repository", str(self.repo)])
        self.assertEqual(code, 2)
        payload = json.loads(stderr.getvalue())
        self.assertEqual(payload["status"], "ERROR")
        self.assertEqual(payload["reason"], "epoch_lint_input_invalid")


if __name__ == "__main__":
    unittest.main()
