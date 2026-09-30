"""Defect-shaped tests for the pull-request gate ledger (D-118 as thinned 2026-09-29)."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tests.git_fixture import init_git_fixture


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

IMPACT_QUESTIONS = (
    ("i", "Raw-bundle byte or recorded timestamp"),
    ("ii", "Reduced energy, time, token count or correctness score"),
    ("iii", "Admit, refuse, select or exclude decision over bundles, nights, blocks, envelopes or items"),
    ("iv", "Unit or uncertainty"),
    ("v", "Registration, prospective manifest, analysis plan or estimator constant"),
    ("vi", "Published number or sentence in the paper, README claims or claim renderers"),
)
FULL_PASS = "gate-ledger: full tier passes (5 rows, Impact statement answered)\n"
LIGHT_PASS = "gate-ledger: light tier passes (5 rows, Impact statement answered)\n"


class CheckGateLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # TMPDIR is optional: CI runners do not export it.
        cls.temporary = tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR"))
        cls.repo = Path(cls.temporary.name) / "repo"
        cls.repo.mkdir()
        (cls.repo / "evidence.txt").write_text("evidence\n", encoding="utf-8")
        init_git_fixture(cls.repo, "-q")
        for command in (
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

    @staticmethod
    def impact(answers: dict[str, str] | None = None) -> str:
        answers = answers or {}
        return "\n".join(
            f"({label}) {question}: {answers.get(label, 'No. Nothing on this path changes.')}"
            for label, question in IMPACT_QUESTIONS
        ) + "\n"

    def row(self, key: int, evidence: str) -> str:
        return f"| {key} | gate {key} | {evidence} |"

    def body(self, tier: str | None = "full", rows: dict[int, str] | None = None,
             impact: dict[str, str] | None = None) -> str:
        evidence = {1: "RUN evidence.txt", 2: "RUN evidence.txt", 3: f"RUN {self.head}",
                    4: "RUN evidence.txt", 5: "RUN evidence.txt"}
        evidence.update(rows or {})
        table = [self.row(key, evidence[key]) for key in sorted(evidence)]
        ledger = "\n".join([
            "## Gate ledger", "",
            "| # | Gate | Evidence |", "| --- | --- | --- |", *table,
        ]) + "\n"
        head = f"Tier: {tier}\n\n" if tier is not None else ""
        return f"{head}{self.impact(impact)}\n{ledger}"

    def light_body(self, rows: dict[int, str] | None = None,
                   impact: dict[str, str] | None = None) -> str:
        light_rows = {1: "N/A (light tier)", 4: "N/A (light tier)", 5: "N/A (light tier)"}
        light_rows.update(rows or {})
        return self.body("light", light_rows, impact)

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

    def assert_passes(self, body: str, expected: str = FULL_PASS) -> None:
        result = self.run_checker(body)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout, expected)

    def assert_rejected(self, body: str, expected: str) -> None:
        result = self.run_checker(body)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(expected, result.stdout.splitlines())

    # --- tiers ----------------------------------------------------------

    def test_full_tier_and_missing_tier_pass_with_five_run_rows(self) -> None:
        for tier in ("full", None):
            with self.subTest(tier=tier):
                self.assert_passes(self.body(tier))

    def test_full_tier_accepts_no_claim_na_on_row_four_when_every_impact_line_is_no(self) -> None:
        self.assert_passes(self.body(rows={4: CHECKER_MODULE.NO_CLAIM_NA_TEXT}))

    def test_full_tier_refuses_no_claim_na_when_an_impact_line_says_yes(self) -> None:
        # Counterfactual: a PR that can change a number skips the cold final pass.
        body = self.body(rows={4: CHECKER_MODULE.NO_CLAIM_NA_TEXT},
                         impact={"iii": "YES. The helper now refuses charging windows."})
        self.assert_rejected(
            body,
            "gate-ledger: row 4: Impact line (iii) says Yes, so this PR needs the cold final pass",
        )

    def test_full_tier_needs_run_in_rows_one_two_five(self) -> None:
        for key in (1, 2, 5):
            with self.subTest(key=key):
                self.assert_rejected(
                    self.body(rows={key: "N/A (light tier)"}),
                    f"gate-ledger: row {key}: full tier needs RUN evidence here, not N/A",
                )

    def test_full_tier_row_four_accepts_only_its_own_na_text(self) -> None:
        self.assert_rejected(
            self.body(rows={4: "N/A (light tier)"}),
            "gate-ledger: row 4: the only N/A this row accepts in full tier is "
            "N/A (no measurement, calibration or claim code)",
        )

    def test_light_tier_passes_with_ci_and_suite(self) -> None:
        self.assert_passes(self.light_body(), LIGHT_PASS)

    def test_light_tier_docs_only_may_skip_the_suite(self) -> None:
        self.assert_passes(self.light_body({2: "N/A (docs only)"}), LIGHT_PASS)

    def test_light_tier_runs_no_audit_rounds(self) -> None:
        for key in (1, 4, 5):
            for replacement in ("RUN evidence.txt", "NOT-RUN", "N/A (light tier) extra"):
                with self.subTest(key=key, replacement=replacement):
                    self.assert_rejected(
                        self.light_body({key: replacement}),
                        f"gate-ledger: row {key}: a light-tier PR writes N/A (light tier) here",
                    )

    def test_light_tier_still_needs_ci_on_the_final_head(self) -> None:
        self.assert_rejected(self.light_body({3: "N/A (light tier)"}),
                             "gate-ledger: row 3: light tier needs RUN evidence here, not N/A")
        self.assert_rejected(self.light_body({3: "NOT-RUN"}), "gate-ledger: row 3: still NOT-RUN")

    def test_light_tier_refuses_a_yes_in_the_impact_statement(self) -> None:
        # Counterfactual: a PR that changes a number declares itself light.
        self.assert_rejected(
            self.light_body(impact={"ii": "Yes: the reducer's rounding changes."}),
            "gate-ledger: Tier is light but Impact line (ii) says Yes; "
            "a PR that can change a number is full tier",
        )

    def test_indented_light_tier_line_is_not_a_declaration(self) -> None:
        self.assert_passes(" Tier: light\n\n" + self.body(None))

    def test_invalid_or_duplicate_tier_declaration_is_refused(self) -> None:
        self.assert_rejected(self.body("full|light"), "gate-ledger: Tier must be full or light")
        self.assert_rejected("Tier: full\n" + self.body("light"),
                             "gate-ledger: the body declares Tier more than once")

    # --- Impact statement ----------------------------------------------

    def test_impact_line_missing_unanswered_or_unmarked_is_refused(self) -> None:
        body = self.body().replace("(iv) Unit or uncertainty: No. Nothing on this path changes.\n", "")
        self.assert_rejected(body, "gate-ledger: Impact statement line (iv) is missing")
        self.assert_rejected(self.body(impact={"v": "TODO"}),
                             "gate-ledger: Impact statement line (v) is not answered")
        self.assert_rejected(self.body(impact={"vi": "the renderer text moves"}),
                             "gate-ledger: Impact statement line (vi) must start with Yes or No")

    def test_impact_answers_none_and_yes_in_any_case_are_accepted(self) -> None:
        self.assert_passes(self.body(impact={"i": "none.", "ii": "NONE directly", "iii": "YES, see above"}))

    def test_duplicate_impact_line_is_refused(self) -> None:
        body = self.body() + "(ii) Reduced energy, time, token count or correctness score: No\n"
        self.assert_rejected(body, "gate-ledger: Impact statement line (ii) appears more than once")

    # --- rows -------------------------------------------------------------

    def test_missing_row_is_refused(self) -> None:
        body = self.body().replace(self.row(4, "RUN evidence.txt") + "\n", "")
        self.assert_rejected(body, "gate-ledger: row 4: missing")

    def test_duplicate_row_is_refused(self) -> None:
        line = self.row(4, "RUN evidence.txt") + "\n"
        self.assert_rejected(self.body().replace(line, line + line),
                             "gate-ledger: row 4: appears more than once")

    def test_empty_and_not_run_evidence_are_refused(self) -> None:
        self.assert_rejected(self.body(rows={1: ""}), "gate-ledger: row 1: evidence is empty")
        self.assert_rejected(self.body(rows={1: "NOT-RUN"}), "gate-ledger: row 1: still NOT-RUN")

    def test_unresolvable_path_is_refused(self) -> None:
        self.assert_rejected(self.body(rows={1: "RUN missing.txt"}),
                             "gate-ledger: row 1: neither a commit nor a file in the repo: missing.txt")

    def test_line_suffix_and_anchor_are_refused_as_paths(self) -> None:
        # Sol 233 SF1: committed files literally named `evidence.txt:12` and
        # `evidence.txt#anchor` exist, so only the syntax guard refuses them.
        for suffixed in ("evidence.txt:12", "evidence.txt#anchor"):
            (self.repo / suffixed).write_text("suffixed\n", encoding="utf-8")
            with self.subTest(target=suffixed):
                self.assert_rejected(
                    self.body(rows={1: f"RUN {suffixed}"}),
                    f"gate-ledger: row 1: a :N line suffix or #anchor is not a path: {suffixed}",
                )

    def test_escaping_path_is_refused(self) -> None:
        outside = Path(self.temporary.name) / "outside-evidence.txt"
        outside.write_text("outside\n", encoding="utf-8")
        (self.repo / "~existing-evidence.txt").write_text("tilde\n", encoding="utf-8")
        # The absolute target also exists at its join-under-root spelling,
        # so only the leading-slash guard refuses it (Sol 233 SF2).
        joined_absolute = self.repo.joinpath(*str(outside).split("/"))
        joined_absolute.parent.mkdir(parents=True, exist_ok=True)
        joined_absolute.write_text("joined\n", encoding="utf-8")
        for target in ("../outside-evidence.txt", "~existing-evidence.txt", str(outside)):
            with self.subTest(target=target):
                result = self.run_checker(self.body(rows={1: f"RUN {target}"}))
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertEqual(
                    result.stdout,
                    f"gate-ledger: row 1: neither a commit nor a file in the repo: {target}\n",
                )

    def test_hex_string_that_is_neither_commit_nor_path_is_refused(self) -> None:
        self.assert_rejected(self.body(rows={1: "RUN badc0de"}),
                             "gate-ledger: row 1: neither a commit nor a file in the repo: badc0de")

    def test_hex_only_filename_is_accepted_as_a_path(self) -> None:
        (self.repo / "deadbee").write_text("path evidence\n", encoding="utf-8")
        self.assert_passes(self.body(rows={1: "RUN deadbee"}))

    def test_lowercase_run_and_unstructured_evidence_are_refused(self) -> None:
        self.assert_rejected(self.body(rows={1: "run evidence.txt"}),
                             "gate-ledger: row 1: write RUN in capitals")
        self.assert_rejected(self.body(rows={1: "ran it, trust me"}),
                             "gate-ledger: row 1: evidence must be RUN <path-or-sha>")

    def test_backticked_evidence_is_refused(self) -> None:
        self.assert_rejected(self.body(rows={1: "RUN `evidence.txt`"}),
                             "gate-ledger: row 1: write the evidence as plain text, without backticks")

    def test_row_three_must_be_the_pr_head_sha(self) -> None:
        self.assert_rejected(self.body(rows={3: "RUN evidence.txt"}),
                             "gate-ledger: row 3: name the final head as a commit sha")
        self.assert_rejected(self.body(rows={3: "RUN deadbee"}),
                             "gate-ledger: row 3: commit sha does not resolve: deadbee")
        (self.repo / "other.txt").write_text("other\n", encoding="utf-8")
        subprocess.run(["git", "add", "other.txt"], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-qm", "other commit"], cwd=self.repo, check=True)
        other = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.repo, check=True,
                               text=True, capture_output=True).stdout.strip()
        self.assert_rejected(
            self.body(rows={3: f"RUN {other}"}),
            "gate-ledger: row 3: sha is not the PR head (a push moved the head; update this row)",
        )

    # --- table shape ------------------------------------------------------

    def test_unescaped_pipe_inside_backticks_is_named_malformed(self) -> None:
        body = self.body().replace("| 4 | gate 4 |", r"| 4 | gate `a | b` |")
        result = self.run_checker(body)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(
            result.stdout,
            "gate-ledger: row 4: has 4 cells, expected 3 "
            "(an unescaped | splits a cell even inside backticks; write \\|)\n",
        )

    def test_escaped_pipe_and_escaped_backtick_in_gate_cell_pass(self) -> None:
        self.assert_passes(self.body().replace("| 4 | gate 4 |", r"| 4 | gate `a \| b` |"))
        self.assert_passes(self.body().replace("| 4 | gate 4 |", r"| 4 | gate \` literal tick |"))

    def test_missing_cell_is_named_malformed(self) -> None:
        body = self.body().replace(self.row(4, "RUN evidence.txt"), "| 4 | gate 4 |")
        self.assert_rejected(
            body,
            "gate-ledger: row 4: has 2 cells, expected 3 "
            "(an unescaped | splits a cell even inside backticks; write \\|)",
        )

    def test_split_table_row_matches_gfm_cell_rule(self) -> None:
        cases = (
            (r"| f\|oo |", ["f|oo"]),
            (r"| b `\|` az |", ["b `|` az"]),
            ("| abc | def |", ["abc", "def"]),
            ("abc | def", ["abc", "def"]),
            ("| a `b | c` |", ["a `b", "c`"]),
            (r"| a \\| b |", ["a " + "\\" * 2, "b"]),
            (r"| a \\\| b |", ["a " + "\\" * 2 + "| b"]),
        )
        for line, expected in cases:
            with self.subTest(line=line):
                self.assertEqual(CHECKER_MODULE._split_table_row(line), expected)

    def test_numbered_row_after_blank_is_outside_ledger_table(self) -> None:
        body = self.body() + "\n| 4 | duplicate outside the table | RUN evidence.txt |\n"
        result = self.run_checker(body)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "gate-ledger: row 4: this row sits outside the ledger table\n")

    def test_unknown_row_key_is_named(self) -> None:
        body = self.body().replace("| 1 | gate 1 |", "| **1** | bold key | RUN evidence.txt |\n| 1 | gate 1 |")
        result = self.run_checker(body)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(result.stdout,
                         "gate-ledger: the ledger table has a row with an unknown key: '**1**'\n")

    def test_old_twelve_row_heading_is_not_the_ledger(self) -> None:
        body = self.body().replace("## Gate ledger\n", "## Gate ledger (D-118 / D-121)\n")
        result = self.run_checker(body)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "gate-ledger: no '## Gate ledger' section in the PR body\n")

    def test_fenced_template_before_real_ledger_fails_closed(self) -> None:
        template = (ROOT / ".github" / "pull_request_template.md").read_text(encoding="utf-8")
        result = self.run_checker(f"```markdown\n{template}\n```\n\n{self.body(None)}")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertNotIn("passes", result.stdout)

    def test_indented_summary_ends_the_ledger_section(self) -> None:
        body = self.body() + "\n  ## Summary\n| 4 | ignored after summary | RUN evidence.txt |\n"
        self.assert_passes(body)

    def test_prose_around_the_ledger_passes(self) -> None:
        self.assert_passes("Introductory prose.\n\n" + self.body() + "\n## Verification\n\nClosing prose.\n")

    # --- parity, inputs, shipped files -----------------------------------

    def test_valid_path_matches_gen_state_check_pointer(self) -> None:
        nested = self.repo / "dir" / "nested.txt"
        nested.parent.mkdir(exist_ok=True)
        nested.write_text("nested\n", encoding="utf-8")
        for shaped in ("/absolute/evidence.txt", "https://example.invalid/evidence.txt"):
            joined = self.repo.joinpath(*shaped.split("/"))
            joined.parent.mkdir(parents=True, exist_ok=True)
            joined.write_text("joined\n", encoding="utf-8")
        pointers = (
            "evidence.txt", "dir/nested.txt", "missing.txt", "dir",
            "/absolute/evidence.txt", "~evidence.txt", "../evidence.txt",
            "dir/../evidence.txt", "https://example.invalid/evidence.txt",
            "evidence.txt:12", "", r"evidence\\.txt",
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

    def test_missing_repo_root_is_an_input_error_without_traceback(self) -> None:
        missing = Path(self.temporary.name) / "missing-repo"
        result = self.run_checker(self.body(), repo_root=missing)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(result.stdout,
                         f"gate-ledger: input error: repository root does not exist: {missing}\n")
        self.assertEqual(result.stderr, "")

    def test_workflow_text_pins(self) -> None:
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
        self.assertEqual(result.stdout, "gate-ledger: Tier must be full or light\n")

    def test_shipped_template_lists_the_five_rows_and_six_impact_lines(self) -> None:
        template = (ROOT / ".github" / "pull_request_template.md").read_text(encoding="utf-8")
        for key in CHECKER_MODULE.KEYS:
            self.assertIn(f"\n| {key} | ", template)
        self.assertNotIn("\n| 6 | ", template)
        for label, question in IMPACT_QUESTIONS:
            self.assertIn(f"\n({label}) {question}: TODO\n", template)
        filled = template.replace("Tier: full|light", "Tier: full")
        rows, _, _, seen = CHECKER_MODULE._ledger_rows(filled)
        self.assertTrue(seen)
        self.assertEqual(sorted(rows), list(CHECKER_MODULE.KEYS))

    def test_acceptance_command_aliases_refuse_the_template(self) -> None:
        result = subprocess.run(
            [sys.executable, str(CHECKER), "--root", str(ROOT), "--body",
             str(ROOT / ".github" / "pull_request_template.md")],
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "gate-ledger: Tier must be full or light\n")


if __name__ == "__main__":
    unittest.main()
