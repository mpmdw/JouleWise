"""Defect-shaped tests for the pull-request D-118/D-121 gate ledger."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_gate_ledger.py"


class CheckGateLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory(dir=os.environ["TMPDIR"])
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

    def test_pipe_inside_backticked_gate_item_does_not_lose_row(self) -> None:
        body = self.body().replace(
            "| 4 | gate 4 |",
            r"| 4 | gate `escaped \| and raw |` |",
        )
        result = self.run_checker(body)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "gate-ledger: 12/12 RUN\n")

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


if __name__ == "__main__":
    unittest.main()
