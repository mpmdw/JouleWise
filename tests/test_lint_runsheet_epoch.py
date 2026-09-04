from __future__ import annotations

import json
import contextlib
import copy
import hashlib
import io
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.lint_runsheet_epoch import ContractError, _inline_checks, lint_contract, main


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
        "mode": "historical_replay",
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
                "command": "python scripts/tool.py freeze",
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


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _seal_overlay(overlay: dict[str, object]) -> None:
    authenticated = {key: overlay[key] for key in ("schema", "base_revision", "files")}
    raw = (json.dumps(authenticated, sort_keys=True, separators=(",", ":")) + "\n").encode()
    overlay["sha256"] = hashlib.sha256(raw).hexdigest()


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

    def test_comments_and_echo_text_do_not_spoof_cli_inputs(self) -> None:
        text = self._runsheet(digest=False).replace(
            "\n```\n", " # --digest appears only in a comment\n```\n"
        )
        (self.repo / RUNSHEET).write_text(text, encoding="utf-8")
        _git(self.repo, "add", RUNSHEET)
        _git(self.repo, "commit", "-qm", "comment-only authenticator")
        head = _git(self.repo, "rev-parse", "HEAD")
        result = lint_contract(self.repo, _contract(head, self.clean_head))
        cli = [
            item
            for item in result["findings"]
            if item["kind"] == "contract_required_cli_inputs"
        ]
        self.assertEqual(cli[0]["reason"], "contract_required_cli_input_missing")
        self.assertIn("--digest", cli[0]["detail"])

        echo_only = (
            "Reference tests/sample.py:test_known\n"
            "Coordinate scripts/tool.py:1-5\n\n"
            "```zsh\n"
            "capture 101-ordinary echo python scripts/tool.py freeze "
            "--table table.json --digest value\n"
            "```\n"
        )
        (self.repo / RUNSHEET).write_text(echo_only, encoding="utf-8")
        _git(self.repo, "add", RUNSHEET)
        _git(self.repo, "commit", "-qm", "echo-only command text")
        head = _git(self.repo, "rev-parse", "HEAD")
        result = lint_contract(self.repo, _contract(head, self.clean_head))
        cli = [
            item
            for item in result["findings"]
            if item["kind"] == "contract_required_cli_inputs"
        ]
        self.assertEqual(cli[0]["reason"], "command_not_unique")

    def test_mutable_revision_expression_fails_closed(self) -> None:
        contract = _contract("HEAD", self.clean_head)
        with self.assertRaisesRegex(ContractError, "full lowercase 40-hex"):
            lint_contract(self.repo, contract)

    def test_decorators_are_part_of_whole_symbol_coordinates(self) -> None:
        tool = self.repo / "scripts/tool.py"
        tool.write_text(
            "@staticmethod\ndef parser():\n    return 'parser'\n\n"
            "def main():\n    return 'main'\n",
            encoding="utf-8",
        )
        (self.repo / RUNSHEET).write_text(
            self._runsheet().replace("scripts/tool.py:1-5", "scripts/tool.py:2-6"),
            encoding="utf-8",
        )
        _git(self.repo, "add", ".")
        _git(self.repo, "commit", "-qm", "decorated symbol")
        head = _git(self.repo, "rev-parse", "HEAD")
        contract = _contract(head, head)
        contract["checks"][2]["reference"] = "scripts/tool.py:2-6"  # type: ignore[index]
        contract["checks"][2]["cited_start"] = 2  # type: ignore[index]
        contract["checks"][2]["cited_end"] = 6  # type: ignore[index]
        result = lint_contract(self.repo, contract)
        coordinates = [
            item for item in result["findings"] if item["kind"] == "file_line_coordinates"
        ]
        self.assertEqual(len(coordinates), 1)
        self.assertIn("definitions span 1-6", coordinates[0]["detail"])

    def test_module_constant_is_a_resolvable_symbol(self) -> None:
        sample = self.repo / "tests/sample.py"
        sample.write_text("TOKEN = 1\n" + sample.read_text(encoding="utf-8"), encoding="utf-8")
        (self.repo / RUNSHEET).write_text(
            self._runsheet() + "Reference tests/sample.py:TOKEN\n", encoding="utf-8"
        )
        _git(self.repo, "add", ".")
        _git(self.repo, "commit", "-qm", "module constant")
        head = _git(self.repo, "rev-parse", "HEAD")
        contract = _contract(head, head)
        contract["checks"][0]["reference"] = "tests/sample.py:TOKEN"  # type: ignore[index]
        contract["checks"][0]["symbol"] = "TOKEN"  # type: ignore[index]
        result = lint_contract(self.repo, contract)
        self.assertFalse(
            [item for item in result["findings"] if item["kind"] == "symbol_existence"]
        )

    def _ratification_contract(self) -> dict[str, object]:
        contract_path = "configs/epoch-ratification.json"
        check = {
            "id": "overlay-symbol",
            "kind": "symbol_existence",
            "reference": "tests/sample.py:test_overlay",
            "source_path": "tests/sample.py",
            "symbol": "SampleTests.test_overlay",
        }
        declaration = json.dumps({"checks": [check]}, sort_keys=True)
        empty_declaration = json.dumps({"checks": []}, sort_keys=True)
        runsheet = (
            "Reference tests/sample.py:test_overlay\n\n"
            "```zsh\n"
            f"# joulewise-epoch-lint: {declaration}\n"
            "capture overlay python scripts/tool.py freeze --table x --digest y\n"
            "```\n\n"
            "```zsh\n"
            f"# joulewise-epoch-lint: {empty_declaration}\n"
            f"python3 scripts/lint_runsheet_epoch.py {contract_path}\n"
            "```\n"
        )
        (self.repo / RUNSHEET).write_text(runsheet, encoding="utf-8")
        _git(self.repo, "add", RUNSHEET)
        _git(self.repo, "commit", "-qm", "ratified inline census")
        head = _git(self.repo, "rev-parse", "HEAD")
        base = (self.repo / "tests/sample.py").read_text(encoding="utf-8")
        result = base.replace(
            "        return True\n",
            "        return True\n\n    def test_overlay(self):\n        return True\n",
        )
        overlay: dict[str, object] = {
            "schema": "joulewise.runsheet_epoch_lint.patch_overlay",
            "base_revision": head,
            "files": [
                {
                    "path": "tests/sample.py",
                    "base_sha256": _sha256(base),
                    "result_sha256": _sha256(result),
                    "content": result,
                }
            ],
            "sha256": "",
        }
        _seal_overlay(overlay)
        return {
            "schema": "joulewise.runsheet_epoch_lint",
            "mode": "ratification",
            "runsheet": RUNSHEET,
            "runsheet_revision": head,
            "executing_head": head,
            "contract_path": contract_path,
            "patch_overlay": overlay,
        }

    def test_inline_census_ratification_and_authenticated_overlay_pass(self) -> None:
        contract = self._ratification_contract()
        result = lint_contract(self.repo, contract)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["mode"], "ratification")
        self.assertEqual(result["check_count"], 1)
        self.assertEqual(result["overlay_file_count"], 1)

    def test_removed_declaration_or_ratification_command_fails_closed(self) -> None:
        for needle in ("# joulewise-epoch-lint: ", "python3 scripts/lint_runsheet_epoch.py"):
            with self.subTest(needle=needle):
                contract = self._ratification_contract()
                text = (self.repo / RUNSHEET).read_text(encoding="utf-8")
                line = next(line for line in text.splitlines() if line.startswith(needle))
                (self.repo / RUNSHEET).write_text(
                    text.replace(line + "\n", "", 1), encoding="utf-8"
                )
                _git(self.repo, "add", RUNSHEET)
                _git(self.repo, "commit", "-qm", "remove ratification wire")
                contract["runsheet_revision"] = _git(self.repo, "rev-parse", "HEAD")
                with self.assertRaisesRegex(ContractError, "inline declaration|invoke its exact"):
                    lint_contract(self.repo, contract)

    def test_echo_cannot_spoof_ratification_invocation(self) -> None:
        contract = self._ratification_contract()
        text = (self.repo / RUNSHEET).read_text(encoding="utf-8")
        (self.repo / RUNSHEET).write_text(
            text.replace(
                "python3 scripts/lint_runsheet_epoch.py",
                "echo python3 scripts/lint_runsheet_epoch.py",
            ),
            encoding="utf-8",
        )
        _git(self.repo, "add", RUNSHEET)
        _git(self.repo, "commit", "-qm", "echo-only ratification text")
        contract["runsheet_revision"] = _git(self.repo, "rev-parse", "HEAD")
        with self.assertRaisesRegex(ContractError, "invoke its exact"):
            lint_contract(self.repo, contract)

    def test_s0_runsheet_census_has_three_kinds_and_exact_wire(self) -> None:
        runsheet = Path(
            "docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md"
        ).read_text(encoding="utf-8")
        checks, _ = _inline_checks(runsheet, "$EPOCH_CONTRACT")
        self.assertEqual(len(checks), 3)
        self.assertEqual(
            {check["kind"] for check in checks},
            {
                "symbol_existence",
                "contract_required_cli_inputs",
                "file_line_coordinates",
            },
        )

    def test_overlay_byte_base_and_occupied_root_fail_closed(self) -> None:
        contract = self._ratification_contract()
        changed_byte = copy.deepcopy(contract)
        changed_byte["patch_overlay"]["files"][0]["content"] += "# changed\n"  # type: ignore[index]
        with self.assertRaisesRegex(ContractError, "manifest digest mismatch"):
            lint_contract(self.repo, changed_byte)

        changed_base = copy.deepcopy(contract)
        changed_base["patch_overlay"]["base_revision"] = self.clean_head  # type: ignore[index]
        _seal_overlay(changed_base["patch_overlay"])  # type: ignore[arg-type,index]
        with self.assertRaisesRegex(ContractError, "must equal executing_head"):
            lint_contract(self.repo, changed_base)

        occupied = self.repo / "occupied-overlay"
        occupied.mkdir()
        with self.assertRaisesRegex(ContractError, "root is occupied"):
            lint_contract(self.repo, contract, overlay_root=occupied)

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
