"""Defect-shaped tests for the pull-request D-118/D-121 gate ledger."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_gate_ledger.py"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECKER_MODULE = _load_module("check_gate_ledger_for_test", CHECKER)
GEN_STATE_MODULE = _load_module("gen_state_for_test", ROOT / "scripts" / "gen_state.py")


class CheckGateLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # TMPDIR is optional: CI runners do not export it (luna 232 caught the
        # KeyError on the pr-fast job); the seats' exported scratchpad masked it.
        cls.temporary = tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR"))
        cls.repo = Path(cls.temporary.name) / "repo"
        cls.repo.mkdir()
        (cls.repo / "evidence.txt").write_text("evidence\n", encoding="utf-8")
        for command in (
            ["git", "init", "-q"],
            ["git", "config", "user.email", "tests@joulewise.invalid"],
            ["git", "config", "user.name", "JouleWise tests"],
            ["git", "add", "evidence.txt"],
            ["git", "commit", "-qm", "ledger fixture"],
        ):
            subprocess.run(command, cwd=cls.repo, check=True)
        cls.head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=cls.repo, check=True, text=True,
            capture_output=True,
        ).stdout.strip()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def body(self) -> str:
        rows = [
            f"| {key} | gate {key} | RUN evidence.txt |" for key in range(1, 12)
        ]
        rows.append(f"| 12 | final head | RUN {self.head} |")
        return "\n".join([
            "## Gate ledger (D-118 / D-121)", "",
            "| # | Gate item | Evidence |", "| --- | --- | --- |", *rows,
        ]) + "\n"

    def run_checker(
        self, body: str, *, repo_root: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        body_file = Path(self.temporary.name) / "body.md"
        body_file.write_text(body, encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(CHECKER), "--body-file", str(body_file),
             "--head-sha", self.head, "--repo-root", str(repo_root or self.repo)],
            text=True, capture_output=True, check=False,
        )

    def assert_rejected(self, body: str, expected: str) -> None:
        result = self.run_checker(body)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(expected, result.stdout.splitlines())

    def test_missing_key_is_refused(self) -> None:
        self.assert_rejected(self.body().replace("| 4 | gate 4 | RUN evidence.txt |\n", ""),
                             "gate-ledger: item 4: missing")

    def test_duplicate_key_is_refused(self) -> None:
        body = self.body().replace("| 4 | gate 4 | RUN evidence.txt |\n",
                                   "| 4 | gate 4 | RUN evidence.txt |\n"
                                   "| 4 | duplicate | RUN evidence.txt |\n")
        self.assert_rejected(body, "gate-ledger: item 4: duplicate key")

    def test_empty_evidence_is_refused(self) -> None:
        self.assert_rejected(self.body().replace("RUN evidence.txt", "", 1),
                             "gate-ledger: item 1: evidence is empty")

    def test_not_run_is_refused(self) -> None:
        self.assert_rejected(self.body().replace("RUN evidence.txt", "NOT-RUN", 1),
                             "gate-ledger: item 1: NOT-RUN")

    def test_unresolvable_path_is_refused(self) -> None:
        self.assert_rejected(self.body().replace("RUN evidence.txt", "RUN missing.txt", 1),
                             "gate-ledger: item 1: neither a commit nor a path: missing.txt")

    def test_line_suffix_is_refused_as_a_path(self) -> None:
        self.assert_rejected(
            self.body().replace("RUN evidence.txt", "RUN evidence.txt:12", 1),
            "gate-ledger: item 1: neither a commit nor a path: evidence.txt:12",
        )

    def test_escaping_path_is_refused(self) -> None:
        outside = Path(self.temporary.name) / "outside-evidence.txt"
        outside.write_text("outside\n", encoding="utf-8")
        tilde_target = self.repo / "~existing-evidence.txt"
        tilde_target.write_text("tilde\n", encoding="utf-8")
        targets = ("../outside-evidence.txt", "~existing-evidence.txt", str(outside))
        for target in targets:
            with self.subTest(target=target):
                result = self.run_checker(
                    self.body().replace("RUN evidence.txt", f"RUN {target}", 1),
                )
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertEqual(
                    result.stdout,
                    f"gate-ledger: item 1: neither a commit nor a path: {target}\n",
                )

    def test_hex_string_that_is_neither_commit_nor_path_is_refused(self) -> None:
        body = self.body().replace("RUN evidence.txt", "RUN badc0de", 1)
        result = self.run_checker(body)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(
            result.stdout,
            "gate-ledger: item 1: neither a commit nor a path: badc0de\n",
        )

    def test_hex_only_filename_is_accepted_as_a_path(self) -> None:
        (self.repo / "deadbee").write_text("path evidence\n", encoding="utf-8")
        result = self.run_checker(self.body().replace("RUN evidence.txt", "RUN deadbee", 1))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "gate-ledger: 12/12 RUN\n")

    def test_unescaped_pipe_inside_backticked_gate_item_is_named_malformed(self) -> None:
        body = self.body().replace(
            "| 4 | gate 4 |",
            r"| 4 | gate `a | b` |",
        )
        result = self.run_checker(body)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(
            result.stdout,
            "gate-ledger: item 4: row has 4 cells, expected 3 "
            "(an unescaped | splits a cell even inside backticks; write \\|)\n",
        )

    def test_escaped_pipe_inside_backticked_gate_item_passes(self) -> None:
        body = self.body().replace(
            "| 4 | gate 4 |",
            r"| 4 | gate `a \| b` |",
        )
        result = self.run_checker(body)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "gate-ledger: 12/12 RUN\n")

    def test_extra_cell_in_numbered_row_is_named_malformed(self) -> None:
        body = self.body().replace(
            "| 4 | gate 4 | RUN evidence.txt |",
            "| 4 | gate 4 | RUN evidence.txt | extra |",
        )
        self.assert_rejected(
            body,
            "gate-ledger: item 4: row has 4 cells, expected 3 "
            "(an unescaped | splits a cell even inside backticks; write \\|)",
        )

    def test_missing_cell_in_numbered_row_is_named_malformed(self) -> None:
        body = self.body().replace(
            "| 4 | gate 4 | RUN evidence.txt |",
            "| 4 | gate 4 |",
        )
        self.assert_rejected(
            body,
            "gate-ledger: item 4: row has 2 cells, expected 3 "
            "(an unescaped | splits a cell even inside backticks; write \\|)",
        )

    def test_escaped_backtick_outside_code_span_does_not_open_a_span(self) -> None:
        # terra 208 I1: a backslash-escaped literal backtick is valid GFM and
        # must not swallow the evidence cell as an unterminated code span.
        body = self.body().replace(
            "| 4 | gate 4 |",
            r"| 4 | gate \` literal tick |",
        )
        result = self.run_checker(body)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "gate-ledger: 12/12 RUN\n")

    def test_split_table_row_matches_gfm_cell_rule(self) -> None:
        cases = (
            (r"| f\|oo |", ["f|oo"]),
            (r"| b `\|` az |", ["b `|` az"]),
            (r"| b **\|** im |", ["b **|** im"]),
            ("| abc | def |", ["abc", "def"]),
            ("| bar |", ["bar"]),
            ("| bar | baz | boo |", ["bar", "baz", "boo"]),
            ("abc | def", ["abc", "def"]),
            ("| a `b | c` |", ["a `b", "c`"]),
            (r"| a \\| b |", ["a " + "\\" * 2, "b"]),
            (r"| a \\\| b |", ["a " + "\\" * 2 + "| b"]),
        )
        for line, expected in cases:
            with self.subTest(line=line):
                self.assertEqual(CHECKER_MODULE._split_table_row(line), expected)

    def test_code_spanned_evidence_is_refused_as_not_plain_text(self) -> None:
        bodies = (
            (
                self.body().replace("RUN evidence.txt", "RUN `evidence.txt`", 1),
                "gate-ledger: item 1: evidence cell must be plain text (no backticks)",
            ),
            (
                self.body().replace(f"RUN {self.head}", f"RUN `{self.head}`"),
                "gate-ledger: item 12: evidence cell must be plain text (no backticks)",
            ),
        )
        for body, expected in bodies:
            with self.subTest(expected=expected):
                self.assert_rejected(body, expected)

    def test_numbered_row_after_blank_is_outside_ledger_table(self) -> None:
        body = self.body() + "\n| 4 | duplicate outside the table | RUN evidence.txt |\n"
        result = self.run_checker(body)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(
            result.stdout,
            "gate-ledger: item 4: ledger row outside the ledger table\n",
        )

    def test_fenced_ledger_before_real_section_fails_closed(self) -> None:
        template = (ROOT / ".github" / "pull_request_template.md").read_text(encoding="utf-8")
        body = f"```markdown\n{template}\n```\n\n{self.body()}"
        result = self.run_checker(body)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertNotIn("gate-ledger: 12/12 RUN", result.stdout)

    def test_unrecognised_ledger_row_is_named(self) -> None:
        body = self.body().replace(
            "| 1 | gate 1 | RUN evidence.txt |",
            "| **1** | bold key | RUN evidence.txt |\n| 1 | gate 1 | RUN evidence.txt |",
        )
        result = self.run_checker(body)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "gate-ledger: unrecognised ledger row: '**1**'\n")

    def test_heading_drift_has_one_named_refusal(self) -> None:
        body = self.body().replace(
            "## Gate ledger (D-118 / D-121)",
            "## Gate ledger (D-118/D-121)",
        )
        result = self.run_checker(body)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(
            result.stdout,
            "gate-ledger: no '## Gate ledger (D-118 / D-121)' section in the PR body\n",
        )

    def test_lowercase_run_is_refused_as_not_uppercase(self) -> None:
        body = self.body().replace("RUN evidence.txt", "run evidence.txt", 1)
        result = self.run_checker(body)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(
            result.stdout,
            "gate-ledger: item 1: evidence must start with RUN (uppercase)\n",
        )

    def test_indented_summary_terminates_the_ledger_section(self) -> None:
        # A numbered key after the indented heading: if the heading were
        # matched raw (unstripped) the section would continue and this row
        # would be refused as "outside the ledger table" (luna 227 SF1).
        body = self.body() + "\n  ## Summary\n| 4 | ignored after summary | RUN evidence.txt |\n"
        result = self.run_checker(body)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "gate-ledger: 12/12 RUN\n")

    def test_valid_path_matches_gen_state_check_pointer(self) -> None:
        nested = self.repo / "dir" / "nested.txt"
        nested.parent.mkdir()
        nested.write_text("nested\n", encoding="utf-8")
        pointers = (
            "evidence.txt",
            "dir/nested.txt",
            "missing.txt",
            "dir",
            "/absolute/evidence.txt",
            "~evidence.txt",
            "../evidence.txt",
            "dir/../evidence.txt",
            "https://example.invalid/evidence.txt",
            "evidence.txt:12",
            "",
            r"evidence\\.txt",
        )
        original_root = GEN_STATE_MODULE.ROOT
        GEN_STATE_MODULE.ROOT = str(self.repo)
        try:
            for pointer in pointers:
                with self.subTest(pointer=pointer):
                    checker_valid = CHECKER_MODULE._valid_path(pointer, self.repo)
                    try:
                        GEN_STATE_MODULE._check_pointer(
                            {"path": pointer, "label": "evidence"}, "test.pointer", {}
                        )
                    except GEN_STATE_MODULE.KernelError:
                        gen_state_valid = False
                    else:
                        gen_state_valid = True
                    self.assertEqual(checker_valid, gen_state_valid)
        finally:
            GEN_STATE_MODULE.ROOT = original_root

    def test_unstructured_evidence_is_refused_with_one_message(self) -> None:
        result = self.run_checker(
            self.body().replace("RUN evidence.txt", "ran it, trust me", 1),
        )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(
            result.stdout,
            "gate-ledger: item 1: evidence must be RUN <path-or-sha>\n",
        )

    def test_item_twelve_path_is_refused_even_when_it_exists(self) -> None:
        result = self.run_checker(
            self.body().replace(f"RUN {self.head}", "RUN evidence.txt"),
        )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(
            result.stdout,
            "gate-ledger: item 12: final-head evidence must be a commit sha\n",
        )

    def test_item_twelve_sha_must_match_head(self) -> None:
        body = self.body().replace(f"RUN {self.head}", "RUN deadbee")
        self.assert_rejected(body, "gate-ledger: item 12: commit sha does not resolve: deadbee")
        # A real commit that is not the fixture head exercises the head mismatch.
        (self.repo / "other.txt").write_text("other\n", encoding="utf-8")
        subprocess.run(["git", "add", "other.txt"], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-qm", "other commit"], cwd=self.repo, check=True)
        other = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.repo, check=True,
                               text=True, capture_output=True).stdout.strip()
        self.assert_rejected(self.body().replace(f"RUN {self.head}", f"RUN {other}"),
                             "gate-ledger: item 12: sha is not the PR head")

    def test_prose_around_table_passes(self) -> None:
        body = "Introductory prose.\n\n" + self.body() + "\n## Verification\n\nClosing prose.\n"
        result = self.run_checker(body)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "gate-ledger: 12/12 RUN\n")

    def test_missing_repo_root_is_an_input_error_without_traceback(self) -> None:
        missing = Path(self.temporary.name) / "missing-repo"
        result = self.run_checker(self.body(), repo_root=missing)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(
            result.stdout,
            f"gate-ledger: input error: repository root does not exist: {missing}\n",
        )
        self.assertEqual(result.stderr, "")

    def test_workflow_text_pins_round1_fixes(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "gate-ledger.yml").read_text(encoding="utf-8")
        self.assertIn("Every fresh PR is red by construction", workflow)
        self.assertIn("ref: ${{ github.event.pull_request.head.sha }}", workflow)
        self.assertIn("types: [opened, synchronize, edited, reopened, ready_for_review]", workflow)
        self.assertNotIn("continue-on-error", workflow)
        self.assertIn("permissions:\n  contents: read", workflow)
        self.assertIn("fetch-depth: 0", workflow)

    def test_shipped_template_is_refused_until_filled(self) -> None:
        template = (ROOT / ".github" / "pull_request_template.md").read_text(encoding="utf-8")
        result = self.run_checker(template)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(
            result.stdout.splitlines(),
            [f"gate-ledger: item {key}: NOT-RUN" for key in range(1, 13)],
        )

    def test_acceptance_command_aliases_refuse_the_template(self) -> None:
        result = subprocess.run(
            [sys.executable, str(CHECKER), "--root", str(ROOT), "--body",
             str(ROOT / ".github" / "pull_request_template.md")],
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(
            result.stdout.splitlines(),
            [f"gate-ledger: item {key}: NOT-RUN" for key in range(1, 13)],
        )


if __name__ == "__main__":
    unittest.main()
