"""Regression tests for the registered dependence-sensitivity calculator."""

from __future__ import annotations

import ast
import contextlib
import hashlib
import io
import json
import math
import re
import shlex
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

from joulewise.aggregate import student_t_critical_95
from joulewise.analysis_engine.estimators import (
    DeterministicBoundTerm,
    PairedObservation,
    StochasticVarianceTerm,
    estimate_paired_blocks,
)
from joulewise.analysis_engine.distributions import student_t_quantile

from scripts import dependence_sensitivity


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "dependence_sensitivity.py"
DOCUMENT = REPO_ROOT / "docs" / "paper" / "round7" / "dependence-sensitivity.md"
TEMPLATE = REPO_ROOT / "docs" / "paper" / "round7" / "dependence-sensitivity.md.in"
EXAMPLE_ARGS = (
    "--block-deltas",
    json.dumps(dependence_sensitivity.EXAMPLE_BLOCK_DELTAS_J, separators=(",", ":")),
    "--floor",
    "3.5",
    "--se-metrology",
    "0.2",
    "--deterministic-bound-total",
    "4.0",
)

REFUSAL_BASE_ARGS = (
    "--floor",
    "1.0",
    "--se-metrology",
    "0.2",
    "--deterministic-bound-total",
    "0.1",
)
OVERFLOW_DELTAS = "[1e308,1e308,1e308,1e308,1e308,1e308,1e308,1e308,1e308,1e308]"
MISSING_DELTAS_FILE = str(REPO_ROOT / "tests" / "not-a-real-dependence-sensitivity-input.json")


def _analyze_string_deltas() -> object:
    return dependence_sensitivity.analyze_deltas(
        "0123456789",
        floor_j=1.0,
        se_metrology_j=0.2,
        deterministic_bound_total_j=0.1,
    )


def _analyze_with_zero_total_standard_error() -> object:
    return dependence_sensitivity._model_result(
        name="zero_standard_error",
        description="test",
        mean_j=1.0,
        sample_stddev_j=0.0,
        n_blocks=10,
        effective_n=10.0,
        variance_inflation_factor=1.0,
        se_metrology_j=0.0,
        deterministic_bound_total_j=0.0,
        floor_j=0.0,
    )


def _analyze_with_nonfinite_sample_standard_deviation() -> object:
    with patch.object(dependence_sensitivity.math, "sqrt", return_value=math.inf):
        return dependence_sensitivity.analyze_deltas(
            [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
            floor_j=1.0,
            se_metrology_j=0.2,
            deterministic_bound_total_j=0.1,
        )


REFUSAL_CASES = (
    # name, argv-or-call, expected_reason_regex
    (
        "finite_boolean",
        ("--block-deltas", "[true,2,3,4,5,6,7,8,9,10]", *REFUSAL_BASE_ARGS),
        r"must be a finite number",
    ),
    ("finite_string", lambda: dependence_sensitivity._finite_number("1", "value"), r"must be a finite number"),
    ("dict_deltas", ("--block-deltas", '{"a":1}', *REFUSAL_BASE_ARGS), r"must be a JSON list"),
    ("string_deltas", _analyze_string_deltas, r"must be a JSON list"),
    (
        "four_blocks",
        ("--block-deltas", "[1,2,3,4]", *REFUSAL_BASE_ARGS),
        r"exactly ten complete block deltas are required",
    ),
    (
        "eleven_blocks",
        ("--block-deltas", "[1,2,3,4,5,6,7,8,9,10,11]", *REFUSAL_BASE_ARGS),
        r"exactly ten complete block deltas are required",
    ),
    (
        "invalid_json",
        ("--block-deltas", "[1,]", *REFUSAL_BASE_ARGS),
        r"is not valid JSON",
    ),
    (
        "missing_deltas_file",
        ("--block-deltas-file", MISSING_DELTAS_FILE, *REFUSAL_BASE_ARGS),
        r"cannot read block-delta JSON",
    ),
    (
        "nonfinite_delta",
        ("--block-deltas", "[1,2,3,4,5,6,7,8,9,NaN]", *REFUSAL_BASE_ARGS),
        r"block_deltas_j\[9\] must be a finite number",
    ),
    (
        "constant_sequence",
        ("--block-deltas", "[1,1,1,1,1,1,1,1,1,1]", *REFUSAL_BASE_ARGS),
        r"rho is undefined",
    ),
    (
        "perfect_alternation",
        ("--block-deltas", "[1,-1,1,-1,1,-1,1,-1,1,-1]", *REFUSAL_BASE_ARGS),
        r"abs\(rho\) < 1",
    ),
    (
        "ar1_one_block",
        lambda: dependence_sensitivity.ar1_variance_inflation_factor(1, 0.0),
        r"at least two blocks",
    ),
    (
        "ar1_nonfinite_rho",
        lambda: dependence_sensitivity.ar1_variance_inflation_factor(10, math.nan),
        r"must be a finite number",
    ),
    (
        "ar1_out_of_range",
        lambda: dependence_sensitivity.ar1_variance_inflation_factor(10, 1.0),
        r"abs\(rho\) < 1",
    ),
    (
        "estimated_rho_constant",
        lambda: dependence_sensitivity.estimate_ar1_rho([1.0] * 10, 1.0),
        r"rho is undefined",
    ),
    (
        "estimated_rho_out_of_range",
        lambda: dependence_sensitivity.estimate_ar1_rho([1.0, -1.0] * 5, 0.0),
        r"abs\(rho\) < 1",
    ),
    (
        "five_blocks",
        ("--block-deltas", "[0.461096,0.575454,0.238990,0.073144,-0.228373]", *REFUSAL_BASE_ARGS),
        r"exactly ten complete block deltas are required",
    ),
    (
        "negative_floor",
        ("--block-deltas", "[1,2,3,4,5,6,7,8,9,10]", "--floor", "-0.1", "--se-metrology", "0.2", "--deterministic-bound-total", "0.1"),
        r"must be non-negative",
    ),
    (
        "nonfinite_metrology_se",
        ("--block-deltas", "[1,2,3,4,5,6,7,8,9,10]", "--floor", "1.0", "--se-metrology", "nan", "--deterministic-bound-total", "0.1"),
        r"se_metrology_j must be a finite number",
    ),
    (
        "negative_metrology_se",
        ("--block-deltas", "[1,2,3,4,5,6,7,8,9,10]", "--floor", "1.0", "--se-metrology", "-0.1", "--deterministic-bound-total", "0.1"),
        r"must be non-negative",
    ),
    (
        "negative_deterministic_total",
        ("--block-deltas", "[1,2,3,4,5,6,7,8,9,10]", "--floor", "1.0", "--se-metrology", "0.2", "--deterministic-bound-total", "-0.1"),
        r"must be non-negative",
    ),
    (
        "infinite_interval",
        ("--block-deltas", "[1,2,3,4,5,6,7,8,9,10]", "--floor", "1.0", "--se-metrology", "1e308", "--deterministic-bound-total", "0.1"),
        r"interval is not finite",
    ),
    (
        "infinite_decision_interval",
        ("--block-deltas", "[1,2,3,4,5,6,7,8,9,10]", "--floor", "1.0", "--se-metrology", "5e307", "--deterministic-bound-total", "1.7e308"),
        r"decision interval is not finite",
    ),
    ("effective_n_not_finite", lambda: dependence_sensitivity._degrees_of_freedom(10, math.inf), r"not positive and finite"),
    ("too_few_effective_blocks", lambda: dependence_sensitivity._degrees_of_freedom(10, 1.9), r"fewer than two usable blocks"),
    ("sample_stddev_not_finite", _analyze_with_nonfinite_sample_standard_deviation, r"sample standard deviation is not finite"),
    ("zero_total_standard_error", _analyze_with_zero_total_standard_error, r"total standard error must be positive"),
    ("example_with_floor", ("--example", "--floor", "3.5"), r"cannot be combined"),
    (
        "caller_alpha",
        ("--example", "--alpha", "0.10"),
        r"unrecognized arguments: --alpha",
    ),
    (
        "missing_source",
        ("--floor", "1.0", "--se-metrology", "0.2", "--deterministic-bound-total", "0.1"),
        r"is required unless --example",
    ),
    (
        "missing_metrology",
        ("--block-deltas", "[1,2,3,4,5,6,7,8,9,10]", "--floor", "1.0"),
        r"are required unless --example",
    ),
    (
        "overflow",
        ("--block-deltas", OVERFLOW_DELTAS, *REFUSAL_BASE_ARGS),
        r"overflow",
    ),
)


TEMPLATE_DIGIT_ALLOWLIST = (
    r"DS-SENS-0\d",
    r"PG-SENS-0\d",
    r"DS-\d\d",
    r"PG-\d\d",
    r"_v5",
    r"SHA-256",
    r"UTF-8",
    r"H30",
    r"A/B/B/A",
    r"AR\(1\)",
    r"Table \d",
)
TEMPLATE_MATH_DIGIT_ALLOWLIST = (
    r"[AB]_\{i1\}",
    r"[AB]_\{i2\}",
    r"p_\{\(1\)\}",
    r"p_\{\(2\)\}",
    r"1/2",
    r"\\nu/2",
    r"i=2",
    r"i-1",
    r"\+2\\sum",
    r"k=1",
    r"\(1-k/n\)",
    r"n-1",
    r"\\rfloor-1",
    r"\^2",
    r"\)/2",
)
EXPECTED_AST_CITATION_TARGETS = {
    "citation_two_sided_student_t_p_value": (
        "joulewise/analysis_engine/distributions.py",
        "two_sided_student_t_p_value",
    ),
    "citation_student_t_quantile": (
        "joulewise/analysis_engine/distributions.py",
        "student_t_quantile",
    ),
    "citation_beta_continued_fraction": (
        "joulewise/analysis_engine/distributions.py",
        "_beta_continued_fraction",
    ),
    "citation_ci_t_critical": (
        "joulewise/analysis_engine/estimators.py",
        "_ci_t_critical",
    ),
    "citation_evaluate_claim": (
        "joulewise/analysis_engine/claims.py",
        "evaluate_claim",
    ),
    "citation_estimate_paired_blocks": (
        "joulewise/analysis_engine/estimators.py",
        "estimate_paired_blocks",
    ),
    "citation_model_result": (
        "scripts/dependence_sensitivity.py",
        "_model_result",
    ),
}

# Each rule maps a slot-name pattern to the context that licenses that name at
# one occurrence. The sentinel replaces only the occurrence under inspection,
# so byte-equal swaps cannot borrow context from another occurrence.
PRE_EXAMPLE_SLOT_CONTEXT_RULES = (
    # The generic “for example” cutoff is intentionally the independent model:
    # the nearby degrees-of-freedom concept is instantiated by registered
    # composition (nu=n-1), not by the later AR(1) sensitivity model.
    (
        r"independent_t_critical_three_dp",
        r"(?:for example|the latter supplies) <<SLOT>>",
    ),
    (r"ar1_t_critical_three_dp", r"and <<SLOT>>, rounded"),
    (r"coverage_percent", r"unadjusted two-sided <<SLOT>> interval"),
    (
        r"registered_alpha",
        r"(?:\\\(\\alpha=|p_\{\(2\)\}.*?with \\\(|alpha option: \\\()<<SLOT>>",
    ),
    (r"registered_multiplicity", r"\\\(m=<<SLOT>>"),
    (r"config_generator_path", r"\) in <<SLOT>> by its `family_alpha`"),
    (r"alpha_over_two", r"p_\{\(1\)\}.*?with \\\(<<SLOT>>"),
    (r"one_minus_alpha_over_two", r"t_\{<<SLOT>>"),
    (r"citation_ci_t_critical", r"uses <<SLOT>>;"),
    (
        r"citation_evaluate_claim",
        r"(?:Holm rejection \(|interval check in )<<SLOT>>",
    ),
    (
        r"independent_degrees_integer",
        r"Independent model: \\\(n-1=<<SLOT>>",
    ),
    (r"citation_estimate_paired_blocks", r"replicates <<SLOT>> and"),
    (r"citation_two_sided_student_t_p_value", r"calls <<SLOT>> \(with"),
    (r"citation_beta_continued_fraction", r"in <<SLOT>>\) for p"),
    (r"citation_student_t_quantile", r"and <<SLOT>> for the critical"),
    (r"citation_model_result", r"places at <<SLOT>>"),
    (r"procedure_one", r"^<<SLOT>>\. \*\*Registered composition"),
    (r"procedure_two", r"^<<SLOT>>\. \*\*AR\(1\) estimated-adjacency"),
    (r"procedure_three", r"^<<SLOT>>\. \*\*Fixed effective-n halving"),
    (
        r"independent_v_integer",
        r"^\$\{procedure_one\}\. \*\*Registered composition.*?\\\(V=<<SLOT>>",
    ),
    (
        r"independent_effective_n_integer",
        r"^\$\{procedure_one\}\. \*\*Registered composition.*?"
        r"\\\(n_\{\\mathrm\{eff\}\}=<<SLOT>>",
    ),
    (
        r"independent_degrees_integer",
        r"^\$\{procedure_one\}\. \*\*Registered composition.*?\\nu=<<SLOT>>",
    ),
    (
        r"ar1_v_baseline_integer",
        r"^\$\{procedure_two\}\. \*\*AR\(1\) estimated-adjacency.*?"
        r"\\\(V=<<SLOT>>",
    ),
    (
        r"halving_effective_n_integer",
        r"^\$\{procedure_three\}\. \*\*Fixed effective-n halving.*?"
        r"\\\(n_\{\\mathrm\{eff\}\}=<<SLOT>>",
    ),
    (
        r"halving_v_integer",
        r"^\$\{procedure_three\}\. \*\*Fixed effective-n halving.*?"
        r"\\\(V=<<SLOT>>",
    ),
    (
        r"halving_degrees_integer",
        r"^\$\{procedure_three\}\. \*\*Fixed effective-n halving.*?\\nu=<<SLOT>>",
    ),
    (r"zero_rho", r"(?:set to |\\hat\\rho=)<<SLOT>>"),
    (r"correlation_abs_limit", r"\\ge<<SLOT>>"),
    (r"registered_n_blocks", r"for \\\(n=<<SLOT>>"),
    (r"rho_half", r"and \\\(\\rho=<<SLOT>>"),
    (r"rho_half_variance_inflation", r"gives \\\(V=<<SLOT>>"),
    (
        r"rho_half_effective_n",
        r"and \\\(n_\{\\mathrm\{eff\}\}=<<SLOT>>",
    ),
    (r"rho_nine_tenths", r"at \\\(\\rho=<<SLOT>>"),
    (
        r"rho_nine_tenths_effective_n",
        r"n_\{\\mathrm\{eff\}\}=<<SLOT>>",
    ),
    (r"registered_direction_outcome_placeholder", r"direction gate <<SLOT>>,"),
    (r"h30_link", r"\[retensing-plan\.md, H30\]\(<<SLOT>>\)"),
    (r"h30_replacement", r"^> <<SLOT>>$"),
)
MANDATED_REFUSAL_ROW_NAMES = frozenset(
    {
        "finite_boolean",
        "finite_string",
        "dict_deltas",
        "string_deltas",
        "four_blocks",
        "eleven_blocks",
        "invalid_json",
        "missing_deltas_file",
        "nonfinite_delta",
        "constant_sequence",
        "perfect_alternation",
        "ar1_one_block",
        "ar1_nonfinite_rho",
        "ar1_out_of_range",
        "estimated_rho_constant",
        "estimated_rho_out_of_range",
        "five_blocks",
        "negative_floor",
        "nonfinite_metrology_se",
        "negative_metrology_se",
        "negative_deterministic_total",
        "infinite_interval",
        "infinite_decision_interval",
        "effective_n_not_finite",
        "too_few_effective_blocks",
        "sample_stddev_not_finite",
        "zero_total_standard_error",
        "example_with_floor",
        "caller_alpha",
        "missing_source",
        "missing_metrology",
        "overflow",
    }
)
REFUSAL_SOURCE_SITES = {
    "finite_boolean": "main",
    "finite_string": "_finite_number",
    "dict_deltas": "main",
    "string_deltas": "_validated_deltas",
    "four_blocks": "main",
    "eleven_blocks": "main",
    "invalid_json": "main",
    "missing_deltas_file": "main",
    "nonfinite_delta": "main",
    "constant_sequence": "main",
    "perfect_alternation": "main",
    "ar1_one_block": "_ar1_variance_terms",
    "ar1_nonfinite_rho": "_finite_number",
    "ar1_out_of_range": "_ar1_variance_terms",
    "estimated_rho_constant": "estimate_ar1_rho",
    "estimated_rho_out_of_range": "estimate_ar1_rho",
    "five_blocks": "main",
    "negative_floor": "main",
    "nonfinite_metrology_se": "main",
    "negative_metrology_se": "main",
    "negative_deterministic_total": "main",
    "infinite_interval": "main",
    "infinite_decision_interval": "main",
    "effective_n_not_finite": "_degrees_of_freedom",
    "too_few_effective_blocks": "_degrees_of_freedom",
    "sample_stddev_not_finite": "analyze_deltas",
    "zero_total_standard_error": "_model_result",
    "example_with_floor": "main",
    "caller_alpha": "main",
    "missing_source": "main",
    "missing_metrology": "main",
    "overflow": "main",
}
PLACEMENT_ANCHOR_PATTERN = re.compile(
    r"^\| (?P<site>(?:DS|PG)-SENS-\d+) .*?`docs/paper/draft-v1\.md` line "
    r"(?P<line>\d+) \| `(?P<quote>[^`]+)`",
    re.MULTILINE,
)
BRACKETED_TEN_NUMBER_LIST_PATTERN = re.compile(
    r"\[(?P<values>-?\d+(?:\.\d+)?(?:\s*,\s*-?\d+(?:\.\d+)?){9})\]"
)
SHEET_COMMAND_BLOCK_PATTERN = re.compile(
    r"^```[^\n]*\n(?P<fenced>.*?)^```|^ {4}(?P<indented>\S[^\n]*)$",
    re.MULTILINE | re.DOTALL,
)
TEMPLATE_SLOT_PATTERN = re.compile(r"\$\{(?P<name>[A-Za-z_][A-Za-z0-9_]*)\}")
MATH_SPAN_PATTERN = re.compile(
    r"\\\((?P<inline>.*?)\\\)|\\\[(?P<display>.*?)\\\]", re.DOTALL
)


def _extract_sheet_commands(document: str) -> list[str]:
    """Return each nonblank fenced or four-space-indented command verbatim."""

    commands: list[str] = []
    for match in SHEET_COMMAND_BLOCK_PATTERN.finditer(document):
        if match.group("indented") is not None:
            commands.append(match.group("indented"))
        else:
            commands.extend(
                line for line in match.group("fenced").splitlines() if line.strip()
            )
    return commands


def _assert_documented_command_fixture(test: unittest.TestCase, document: str) -> None:
    matches = tuple(SHEET_COMMAND_BLOCK_PATTERN.finditer(document))
    commands = _extract_sheet_commands(document)
    test.assertEqual(len(matches), len(commands))
    for command, match in zip(commands, matches, strict=True):
        following = document[match.end() :]
        paragraph_match = re.match(
            r"\n\n(?P<paragraph>\S[^\n]*(?:\n(?!\n)[^\n]*)*)", following
        )
        test.assertIsNotNone(paragraph_match, f"command has no following paragraph: {command}")
        assert paragraph_match is not None
        fragments = re.findall(r"`([^`\n]+)`", paragraph_match.group("paragraph"))
        test.assertGreaterEqual(len(fragments), 1, command)
        completed = subprocess.run(
            shlex.split(command),
            cwd=REPO_ROOT,
            check=False,
            text=True,
            capture_output=True,
        )
        test.assertEqual(completed.returncode, 0, completed.stderr)
        for fragment in fragments:
            test.assertIn(fragment, completed.stdout)


def _assert_placement_anchor_fixture(test: unittest.TestCase, document: str) -> None:
    observed = tuple(
        (match.group("site"), int(match.group("line")), match.group("quote"))
        for match in PLACEMENT_ANCHOR_PATTERN.finditer(document)
    )
    test.assertEqual(
        tuple(site for site, _, _ in observed), tuple(dependence_sensitivity.DRAFT_LINE_SLOT_BY_SITE)
    )
    draft_lines = (REPO_ROOT / "docs" / "paper" / "draft-v1.md").read_text(
        encoding="utf-8"
    ).splitlines()
    for site, line_number, quote in observed:
        with test.subTest(site=site):
            test.assertLessEqual(line_number, len(draft_lines))
            matches = [
                index
                for index, line in enumerate(draft_lines, start=1)
                if line.startswith(quote)
            ]
            test.assertEqual(matches, [line_number])


def _assert_refusal_row_fixture(
    test: unittest.TestCase, rows: tuple[tuple[object, ...], ...]
) -> None:
    names = tuple(str(row[0]) for row in rows)
    test.assertEqual(len(names), len(set(names)))
    test.assertEqual(frozenset(names), MANDATED_REFUSAL_ROW_NAMES)
    test.assertEqual(set(REFUSAL_SOURCE_SITES), MANDATED_REFUSAL_ROW_NAMES)
    script_tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    source_sites = {
        node.name for node in ast.walk(script_tree) if isinstance(node, ast.FunctionDef)
    }
    for name in names:
        with test.subTest(name=name):
            test.assertIn(REFUSAL_SOURCE_SITES[name], source_sites)


def _caught_refusal(
    argv_or_call: tuple[str, ...] | Any,
) -> tuple[BaseException, str, str]:
    stdout = contextlib.redirect_stdout(io.StringIO())
    stderr_buffer = io.StringIO()
    try:
        with stdout, contextlib.redirect_stderr(stderr_buffer):
            if callable(argv_or_call):
                argv_or_call()
            else:
                dependence_sensitivity.main(argv_or_call)
    except BaseException as exc:
        script_frames: list[str] = []
        traceback = exc.__traceback__
        while traceback is not None:
            if Path(traceback.tb_frame.f_code.co_filename).resolve() == SCRIPT:
                script_frames.append(traceback.tb_frame.f_code.co_name)
            traceback = traceback.tb_next
        return exc, stderr_buffer.getvalue(), script_frames[-1] if script_frames else ""
    raise AssertionError("refusal case returned without raising")


def _string_literal_fragments(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    if isinstance(node, ast.JoinedStr):
        return [part.value for part in node.values if isinstance(part, ast.Constant) and isinstance(part.value, str)]
    return []


def _source_refusal_literals() -> list[str]:
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    literals: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not node.args:
            continue
        is_value_error = isinstance(node.func, ast.Name) and node.func.id == "ValueError"
        is_parser_error = (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "error"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "parser"
        )
        if is_value_error or is_parser_error:
            literals.extend(_string_literal_fragments(node.args[0]))
    return [literal for literal in literals if literal]


class DependenceSensitivityTests(unittest.TestCase):
    def _run(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *arguments],
            cwd=REPO_ROOT,
            check=False,
            text=True,
            capture_output=True,
        )

    def _assert_cli_refuses(
        self, arguments: tuple[str, ...], expected_reason_regex: str
    ) -> None:
        completed = self._run(*arguments)
        self.assertEqual(completed.returncode, 2, completed.stderr)
        self.assertEqual(completed.stdout, "")
        self.assertRegex(completed.stderr, expected_reason_regex)

    def _example_payload(self) -> dict[str, Any]:
        completed = self._run("--example")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads(completed.stdout)

    def test_worked_example_golden_every_documented_intermediate(self) -> None:
        """Keep every number printed in the worked example aligned with the document."""

        document = DOCUMENT.read_text(encoding="utf-8")
        delta_match = re.search(
            r"^\| Ordered block deltas \(J\) \| `(?P<deltas>\[[^`\n]+\])` \|$",
            document,
            re.MULTILINE,
        )
        self.assertIsNotNone(delta_match)
        assert delta_match is not None
        self.assertEqual(
            len(re.findall(r"^\| Ordered block deltas \(J\) \| `\[[^`\n]+\]` \|$", document, re.MULTILINE)),
            1,
        )
        parsed_deltas = json.loads(delta_match.group("deltas"))
        self.assertEqual(parsed_deltas, dependence_sensitivity.EXAMPLE_BLOCK_DELTAS_J)
        self.assertEqual(self._example_payload()["input"]["block_deltas_j"], parsed_deltas)

        payload = dependence_sensitivity.analyze_deltas(
            parsed_deltas,
            floor_j=3.5,
            se_metrology_j=0.2,
            deterministic_bound_total_j=4.0,
        )
        self.assertEqual(payload["schema_version"], "joulewise.dependence_sensitivity.v1")
        self.assertEqual(payload["input"]["registered_alpha"], 0.05)
        self.assertEqual(payload["input"]["se_metrology_j"], 0.2)
        self.assertEqual(payload["input"]["deterministic_bound_total_j"], 4.0)

        worked_inputs = document[document.index("These invented values") : document.index("Their sum is")]
        for value in (3.5, 0.2, 4.0):
            self.assertIn(f"{value:.6f}", worked_inputs)

        summary = payload["summary"]
        worked_example = document[document.index("Their sum is") : document.index("| Model |")]
        for value in (
            summary["sum_j"],
            summary["mean_j"],
            summary["squared_deviations_sum_j2"],
            summary["sample_stddev_j"],
        ):
            self.assertIn(f"{value:.6f}", worked_example)

        rho = payload["ar1_rho_estimator"]
        for value in (
            rho["numerator"],
            rho["denominator"],
            rho["rho_hat"],
            math.fsum(row["term"] for row in payload["ar1_variance_terms"]),
            *(row["term"] for row in payload["ar1_variance_terms"]),
        ):
            self.assertIn(f"{value:.6f}", worked_example)

        for name, model in payload["models"].items():
            with self.subTest(model=name):
                for value in (
                    model["variance_inflation_factor"],
                    model["effective_n"],
                    model["se_repeat_j"],
                    model["se_total_j"],
                    model["t_critical_95"],
                    model["half_width_j"],
                    model["t_statistic"],
                ):
                    self.assertIn(f"{value:.6f}", worked_example)
                for interval_name in (
                    "repeat_only_interval_j",
                    "metrology_aware_interval_j",
                    "decision_interval_j",
                ):
                    interval = model[interval_name]
                    self.assertIn(
                        f"[{interval['lower']:.6f}, {interval['upper']:.6f}]",
                        worked_example,
                    )
                self.assertIn(f"{model['raw_two_sided_p']:.9f}", worked_example)
                self.assertTrue(model["floor_gate"]["passes"])
                self.assertFalse(model["direction_gate"]["passes"])

        disagreement = dependence_sensitivity.analyze_deltas(
            parsed_deltas,
            floor_j=3.5,
            se_metrology_j=0.2,
            deterministic_bound_total_j=3.5,
        )
        self.assertTrue(disagreement["models"]["independent_blocks"]["direction_gate"]["passes"])
        self.assertFalse(disagreement["models"]["ar1_estimated_rho"]["direction_gate"]["passes"])
        self.assertFalse(disagreement["models"]["fixed_effective_n_halving"]["direction_gate"]["passes"])
        self.assertFalse(disagreement["comparison"]["direction_gate_outcomes_agree"])
        self.assertIn('"direction_gate_outcomes_agree": false', document)

    def test_artifact_hashes_and_omits_holm_or_claim_verdict(self) -> None:
        payload = self._example_payload()
        canonical_deltas = json.dumps(
            payload["input"]["block_deltas_j"],
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        )
        canonical_metrology = json.dumps(
            payload["input_authentication"]["metrology_inputs"],
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        )
        self.assertEqual(
            payload["input_authentication"]["block_deltas_json_sha256"],
            hashlib.sha256(canonical_deltas.encode("utf-8")).hexdigest(),
        )
        self.assertEqual(
            payload["input_authentication"]["metrology_inputs_json_sha256"],
            hashlib.sha256(canonical_metrology.encode("utf-8")).hexdigest(),
        )
        serialized = json.dumps(payload, sort_keys=True).lower()
        self.assertNotIn("holm", serialized)
        self.assertNotIn("support", serialized)

    def test_document_retains_the_registered_contract_and_h30_replacement(self) -> None:
        document = DOCUMENT.read_text(encoding="utf-8")
        required_text = (
            "`_v5` is the fixed name",
            "exactly ten complete blocks",
            "does not accept an alpha option",
            "registered composition with \\(n_{\\mathrm{eff}}=n\\)",
            "p_{(1)}\\) with \\(0.025",
            "p_{(2)}\\) with \\(0.05\\) only if the first rejects; equality passes",
            "Fixed effective-n halving (a named pessimistic scenario, not a bound)",
            "V=2.600391",
            "n_{\\mathrm{eff}}=3.845576",
            "n_{\\mathrm{eff}}=1.374341",
            "DS-SENS-01",
            "DS-SENS-02",
            "PG-SENS-01",
            "PG-SENS-02",
            "The existing DS-26, DS-31, PG-02, and PG-07 rows keep their suppliers and meanings.",
        )
        for required in required_text:
            with self.subTest(required=required):
                self.assertIn(required, document)
        h30_replacement = (
            "The pulse portion of the calibration bound is the largest of 118 observed onset and offset "
            "excursions from 59 commanded pulses in one capture; the clock-anchor allowance is then "
            "added. Because those pulses share one capture and the paper has not shown independence "
            "across pulse order or between onset and offset errors, this value is reported as the observed "
            "sample maximum, not as a “95/95” population-coverage bound. It is not a deterministic "
            "out-of-sample guarantee."
        )
        self.assertIn(h30_replacement, document)
        definitions = document.index("The **sample mean**")
        table = document.index("| Reported quantity |")
        self.assertLess(definitions, table)
        for required in ("**standard error**", "**critical value**", "**half-width**", "**Student-*t* statistic**", "**variance multiplier**", "**floor gate**", "**direction gate**"):
            with self.subTest(definition=required):
                self.assertLess(document.index(required), table)

    def test_registered_independent_composition_matches_engine_to_one_nanajoule(self) -> None:
        # Minimal engine mapping: a calculator delta becomes value_b - value_a
        # with value_a=0; each block carries paired stochastic variance 0.4,
        # so sum(0.4)/10^2 = 0.04 and se_metrology=0.2.  contrast_bound=4
        # maps directly to the calculator's deterministic_bound_total input.
        stochastic = StochasticVarianceTerm(
            name="sensitivity_metrology",
            variance_a=0.0,
            variance_b=0.4,
            covariance_ab=0.0,
        )
        deterministic = DeterministicBoundTerm(
            name="sensitivity_deterministic",
            bound_a=0.0,
            bound_b=0.0,
            contrast_bound=4.0,
        )
        engine = estimate_paired_blocks(
            tuple(
                PairedObservation(
                    block_id=f"block-{index}",
                    value_a=0.0,
                    value_b=delta,
                    stochastic_terms=(stochastic,),
                    deterministic_terms=(deterministic,),
                )
                for index, delta in enumerate(
                    dependence_sensitivity.EXAMPLE_BLOCK_DELTAS_J, start=1
                )
            )
        )
        calculator = dependence_sensitivity.analyze_deltas(
            dependence_sensitivity.EXAMPLE_BLOCK_DELTAS_J,
            floor_j=3.5,
            se_metrology_j=0.2,
            deterministic_bound_total_j=4.0,
        )["models"]["independent_blocks"]
        for observed, expected in (
            (calculator["metrology_aware_interval_j"]["lower"], engine.metrology_aware_ci95.lower),
            (calculator["metrology_aware_interval_j"]["upper"], engine.metrology_aware_ci95.upper),
            (calculator["decision_interval_j"]["lower"], engine.decision_interval.lower),
            (calculator["decision_interval_j"]["upper"], engine.decision_interval.upper),
        ):
            self.assertAlmostEqual(observed, expected, delta=1.0e-9)

    def test_zero_rho_ar1_collapses_to_registered_independent_composition(self) -> None:
        deltas = [6.0, 5.0, 4.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0]
        result = dependence_sensitivity.analyze_deltas(
            deltas,
            floor_j=1.0,
            se_metrology_j=0.2,
            deterministic_bound_total_j=0.1,
        )
        self.assertEqual(result["ar1_rho_estimator"]["rho_hat"], 0.0)
        independent = result["models"]["independent_blocks"]
        ar1 = result["models"]["ar1_estimated_rho"]
        self.assertEqual(ar1["effective_n"], independent["effective_n"])
        self.assertEqual(ar1["degrees_of_freedom"], independent["degrees_of_freedom"])
        self.assertEqual(
            ar1["metrology_aware_interval_j"],
            independent["metrology_aware_interval_j"],
        )
        self.assertEqual(ar1["decision_interval_j"], independent["decision_interval_j"])
        # At rho=0, the AR(1) repeat layer is the engine's ordinary repeat
        # layer. The per-block terms use the minimal mapping documented above.
        engine = estimate_paired_blocks(
            tuple(
                PairedObservation(
                    block_id=f"zero-rho-{index}",
                    value_a=0.0,
                    value_b=delta,
                    stochastic_terms=(
                        StochasticVarianceTerm(
                            name="sensitivity_metrology",
                            variance_a=0.0,
                            variance_b=0.4,
                            covariance_ab=0.0,
                        ),
                    ),
                    deterministic_terms=(
                        DeterministicBoundTerm(
                            name="sensitivity_deterministic",
                            bound_a=0.0,
                            bound_b=0.0,
                            contrast_bound=0.1,
                        ),
                    ),
                )
                for index, delta in enumerate(deltas, start=1)
            )
        )
        for observed, expected in (
            (ar1["metrology_aware_interval_j"]["lower"], engine.metrology_aware_ci95.lower),
            (ar1["metrology_aware_interval_j"]["upper"], engine.metrology_aware_ci95.upper),
            (ar1["decision_interval_j"]["lower"], engine.decision_interval.lower),
            (ar1["decision_interval_j"]["upper"], engine.decision_interval.upper),
        ):
            self.assertAlmostEqual(observed, expected, delta=1.0e-9)

    def test_critical_values_match_aggregate_table_for_df_one_to_nine(self) -> None:
        for degrees_of_freedom in range(1, 10):
            with self.subTest(degrees_of_freedom=degrees_of_freedom):
                self.assertEqual(
                    round(student_t_quantile(0.975, degrees_of_freedom), 3),
                    student_t_critical_95(degrees_of_freedom),
                )

    def test_strict_floor_and_direction_boundaries_fail(self) -> None:
        self.assertFalse(
            dependence_sensitivity._model_result(
                name="floor_boundary",
                description="test",
                mean_j=3.5,
                sample_stddev_j=0.0,
                n_blocks=10,
                effective_n=10.0,
                variance_inflation_factor=1.0,
                se_metrology_j=0.1,
                deterministic_bound_total_j=0.0,
                floor_j=3.5,
            )["floor_gate"]["passes"]
        )
        self.assertIsNone(dependence_sensitivity._strict_direction({"lower": 0.0, "upper": 1.0}))
        self.assertIsNone(dependence_sensitivity._strict_direction({"lower": -1.0, "upper": 0.0}))

    def test_reason_keyed_refusal_cases_bind_to_innermost_script_frame(self) -> None:
        _assert_refusal_row_fixture(self, REFUSAL_CASES)
        for name, argv_or_call, expected_reason_regex in REFUSAL_CASES:
            with self.subTest(name=name):
                exception, stderr, source_site = _caught_refusal(argv_or_call)
                if isinstance(exception, SystemExit):
                    self.assertEqual(exception.code, 2)
                    self.assertRegex(stderr, expected_reason_regex)
                else:
                    self.assertIsInstance(exception, (ValueError, OverflowError))
                    self.assertRegex(str(exception), expected_reason_regex)
                self.assertEqual(source_site, REFUSAL_SOURCE_SITES[name])

    def test_every_literal_refusal_reason_has_a_reason_keyed_row(self) -> None:
        reason_regexes = [expected_reason_regex for _, _, expected_reason_regex in REFUSAL_CASES]
        for literal in _source_refusal_literals():
            with self.subTest(literal=literal):
                self.assertTrue(
                    any(re.search(pattern, literal) for pattern in reason_regexes),
                    f"no refusal row matches source literal: {literal!r}",
                )

    def test_fixed_alpha_is_printed_and_cli_has_no_alpha_option(self) -> None:
        result = dependence_sensitivity.analyze_deltas(
            dependence_sensitivity.EXAMPLE_BLOCK_DELTAS_J,
            floor_j=3.5,
            se_metrology_j=0.2,
            deterministic_bound_total_j=4.0,
        )
        self.assertEqual(result["input"]["registered_alpha"], dependence_sensitivity.REGISTERED_ALPHA)
        self.assertEqual(dependence_sensitivity.REGISTERED_ALPHA, 0.05)
        self._assert_cli_refuses(
            EXAMPLE_ARGS + ("--alpha", "0.05"),
            r"unrecognized arguments: --alpha",
        )

    def test_ar1_multiplier_widens_as_rho_grows(self) -> None:
        low_rho = dependence_sensitivity.ar1_variance_inflation_factor(10, 0.1)
        high_rho = dependence_sensitivity.ar1_variance_inflation_factor(10, 0.5)
        self.assertGreater(high_rho, low_rho)
        self.assertEqual(round(high_rho, 6), 2.600391)
        self.assertTrue(math.isfinite(high_rho))


class DependenceSensitivitySheetFixtureTests(unittest.TestCase):
    """Mechanical contract: the sheet's prose, tables, and commands are fixtures."""

    def _document(self) -> str:
        return DOCUMENT.read_text(encoding="utf-8")

    def _example_payload(self) -> dict[str, Any]:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--example"],
            cwd=REPO_ROOT,
            check=False,
            text=True,
            capture_output=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads(completed.stdout)

    def test_every_documented_command_executes_verbatim_with_its_claimed_outcome(
        self,
    ) -> None:
        _assert_documented_command_fixture(self, self._document())

    def test_every_bracketed_ten_number_list_equals_the_example_constant(self) -> None:
        lists = [
            json.loads(f"[{match.group('values')}]")
            for match in BRACKETED_TEN_NUMBER_LIST_PATTERN.finditer(self._document())
        ]
        self.assertEqual(len(lists), 2)
        for values in lists:
            self.assertEqual(values, dependence_sensitivity.EXAMPLE_BLOCK_DELTAS_J)

    def test_every_draft_line_anchor_resolves_in_the_frozen_draft(self) -> None:
        _assert_placement_anchor_fixture(self, self._document())

    def test_refusal_row_set_is_exact_and_every_row_binds_to_a_source_site(self) -> None:
        _assert_refusal_row_fixture(self, REFUSAL_CASES)

    def test_every_worked_example_number_is_rendered_from_output_or_input_constant(
        self,
    ) -> None:
        document = self._document()
        payload = self._example_payload()
        summary = payload["summary"]
        rho = payload["ar1_rho_estimator"]

        input_line = next(
            line for line in document.splitlines() if line.startswith("These invented values")
        )
        input_match = re.search(
            r"\\\(F=(?P<floor>\d+\.\d+)\\\) J, se_metrology "
            r"\\\(=(?P<se>\d+\.\d+)\\\) J, and deterministic_bound_total "
            r"\\\(=(?P<bound>\d+\.\d+)\\\) J",
            input_line,
        )
        self.assertIsNotNone(input_match)
        assert input_match is not None
        self.assertEqual(
            input_match.groupdict(),
            {
                "floor": f"{dependence_sensitivity.EXAMPLE_FLOOR_J:.6f}",
                "se": f"{dependence_sensitivity.EXAMPLE_SE_METROLOGY_J:.6f}",
                "bound": f"{dependence_sensitivity.EXAMPLE_DETERMINISTIC_BOUND_TOTAL_J:.6f}",
            },
        )

        deltas_match = re.search(
            r"^\| Ordered block deltas \(J\) \| `(?P<deltas>\[[^`\n]+\])` \|$",
            document,
            re.MULTILINE,
        )
        self.assertIsNotNone(deltas_match)
        assert deltas_match is not None
        self.assertEqual(
            json.loads(deltas_match.group("deltas")),
            dependence_sensitivity.EXAMPLE_BLOCK_DELTAS_J,
        )

        summary_line = next(
            line for line in document.splitlines() if line.startswith("Their sum is")
        )
        for rendered in (
            f"{summary['sum_j']:.6f}",
            f"{summary['mean_j']:.6f}",
            f"{summary['squared_deviations_sum_j2']:.6f}",
            f"{summary['sample_stddev_j']:.6f}",
            f"{rho['numerator']:.6f}",
            f"{rho['denominator']:.6f}",
            f"{rho['rho_hat']:.6f}",
            *(f"{row['term']:.6f}" for row in payload["ar1_variance_terms"]),
        ):
            with self.subTest(summary_rendering=rendered):
                self.assertIn(rendered, summary_line)

        model_rows = [
            line
            for line in document.splitlines()
            if line.startswith("| Registered composition")
            or line.startswith("| AR(1),")
            or line.startswith("| Fixed effective-n halving |")
        ]
        self.assertEqual(len(model_rows), 3)
        expected_models = (
            ("Registered composition with \\(n_{\\mathrm{eff}}=n\\)", "independent_blocks"),
            ("AR(1), \\(\\hat\\rho=0.300000\\)", "ar1_estimated_rho"),
            ("Fixed effective-n halving", "fixed_effective_n_halving"),
        )
        for row, (label, model_name) in zip(model_rows, expected_models, strict=True):
            cells = [cell.strip() for cell in row.split("|")[1:-1]]
            model = payload["models"][model_name]
            expected_cells = [
                label,
                f"{model['effective_n']:.6f}",
                str(model["degrees_of_freedom"]),
                (
                    f"[{model['repeat_only_interval_j']['lower']:.6f}, "
                    f"{model['repeat_only_interval_j']['upper']:.6f}]"
                ),
                (
                    f"[{model['metrology_aware_interval_j']['lower']:.6f}, "
                    f"{model['metrology_aware_interval_j']['upper']:.6f}]"
                ),
                (
                    f"[{model['decision_interval_j']['lower']:.6f}, "
                    f"{model['decision_interval_j']['upper']:.6f}]"
                ),
                "pass" if model["floor_gate"]["passes"] else "fail",
                "pass" if model["direction_gate"]["passes"] else "fail",
            ]
            with self.subTest(model=model_name):
                self.assertEqual(cells, expected_cells)

        prose_lines = {
            "independent_blocks": next(
                line
                for line in document.splitlines()
                if line.startswith("For registered composition")
            ),
            "ar1_estimated_rho": next(
                line for line in document.splitlines() if line.startswith("For AR(1)")
            ),
            "fixed_effective_n_halving": next(
                line
                for line in document.splitlines()
                if line.startswith("For fixed effective-n halving")
            ),
        }
        for model_name, prose_line in prose_lines.items():
            model = payload["models"][model_name]
            renderings = (
                f"V={model['variance_inflation_factor']:.6f}",
                f"n_{{\\mathrm{{eff}}}}={model['effective_n']:.6f}",
                f"\\nu={model['degrees_of_freedom']}",
                f"{model['se_repeat_j']:.6f}",
                f"{model['se_total_j']:.6f}",
                f"{model['t_critical_95']:.6f}",
                f"{model['half_width_j']:.6f}",
                f"{model['t_statistic']:.6f}",
                f"{model['raw_two_sided_p_replay']['x']:.12f}",
                f"{model['raw_two_sided_p']:.9f}",
            )
            for rendered in renderings:
                with self.subTest(model=model_name, rendering=rendered):
                    self.assertIn(rendered, prose_line)
            for interval_name in (
                "repeat_only_interval_j",
                "metrology_aware_interval_j",
                "decision_interval_j",
            ):
                interval = model[interval_name]
                self.assertIn(
                    f"[{interval['lower']:.6f}, {interval['upper']:.6f}]",
                    prose_line,
                )
            self.assertIn(
                "floor gate " + ("passes" if model["floor_gate"]["passes"] else "fails"),
                prose_line,
            )
            self.assertIn(
                "direction gate "
                + ("passes" if model["direction_gate"]["passes"] else "fails"),
                prose_line,
            )

    def test_tail_replay_formula_values_and_source_locations_are_current(self) -> None:
        document = self._document()
        payload = self._example_payload()
        for model in payload["models"].values():
            replay = model["raw_two_sided_p_replay"]
            with self.subTest(model=model["model"]):
                self.assertEqual(replay["formula"], "p = I_x(ν/2, 1/2)")
                self.assertEqual(replay["x_formula"], "x = ν/(ν + t²)")
                self.assertAlmostEqual(
                    replay["x"],
                    model["degrees_of_freedom"]
                    / (model["degrees_of_freedom"] + model["t_statistic"] ** 2),
                )
        actual_targets = {
            slot_name: (path.resolve().relative_to(REPO_ROOT).as_posix(), function_name)
            for slot_name, (path, function_name) in dependence_sensitivity.AST_CITATION_SPECS.items()
        }
        self.assertEqual(actual_targets, EXPECTED_AST_CITATION_TARGETS)
        slots = dependence_sensitivity.sheet_slots(TEMPLATE.read_text(encoding="utf-8"))
        for slot_name, (relative_path, function_name) in EXPECTED_AST_CITATION_TARGETS.items():
            path = REPO_ROOT / relative_path
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            definitions = [
                node
                for node in ast.walk(tree)
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name == function_name
            ]
            with self.subTest(citation=function_name):
                self.assertEqual(len(definitions), 1)
                expected = (
                    f"`{function_name}` (`{relative_path}`, line {definitions[0].lineno})"
                )
                self.assertEqual(slots[slot_name], expected)
                self.assertIn(expected, document)
        self.assertIn("regularized incomplete beta function", document)
        self.assertIn("iterative numerical fraction evaluation", document)

    def test_rendered_sheet_is_byte_equal_to_the_tracked_document(self) -> None:
        self.assertEqual(self._document(), dependence_sensitivity.render_sheet())

    def test_check_sheet_returns_two_when_the_tracked_output_drifts(self) -> None:
        stderr = io.StringIO()
        with patch.object(dependence_sensitivity, "SHEET_OUTPUT_PATH", TEMPLATE):
            with contextlib.redirect_stderr(stderr):
                self.assertEqual(dependence_sensitivity.main(("--check-sheet",)), 2)
        self.assertIn("DRIFT", stderr.getvalue())

    def test_template_slots_are_exact_and_every_value_is_preformatted_text(self) -> None:
        template = TEMPLATE.read_text(encoding="utf-8")
        named_slots = {match.group("name") for match in TEMPLATE_SLOT_PATTERN.finditer(template)}
        resolved = dependence_sensitivity.sheet_slots(template)
        self.assertEqual(set(resolved), named_slots)
        self.assertTrue(all(isinstance(value, str) for value in resolved.values()))

    def test_every_pre_example_slot_matches_a_closed_context_rule(self) -> None:
        template = TEMPLATE.read_text(encoding="utf-8")
        pre_example = template[: template.index("## Worked pre-collection example")]
        fixed_start = pre_example.index("## Fixed sensitivity procedure")
        fixed_end = pre_example.index("## Pre-registered disagreement sentence")
        procedure_starts = [
            match.start()
            for match in re.finditer(r"^\$\{procedure_(?:one|two|three)\}", pre_example, re.MULTILINE)
        ]
        covered_rules: set[int] = set()
        for occurrence in TEMPLATE_SLOT_PATTERN.finditer(pre_example):
            slot_name = occurrence.group("name")
            matching_rules = [
                (index, context_pattern)
                for index, (slot_pattern, context_pattern) in enumerate(
                    PRE_EXAMPLE_SLOT_CONTEXT_RULES
                )
                if re.fullmatch(slot_pattern, slot_name)
            ]
            with self.subTest(slot=slot_name, offset=occurrence.start()):
                self.assertTrue(matching_rules, f"uncovered pre-example slot: {slot_name}")
                if fixed_start <= occurrence.start() < fixed_end and procedure_starts[0] <= occurrence.start():
                    scope_start = max(
                        start for start in procedure_starts if start <= occurrence.start()
                    )
                    later_starts = [
                        start for start in procedure_starts if start > occurrence.start()
                    ]
                    scope_end = min(later_starts, default=fixed_end)
                else:
                    scope_start = pre_example.rfind("\n", 0, occurrence.start()) + 1
                    line_end = pre_example.find("\n", occurrence.end())
                    scope_end = len(pre_example) if line_end < 0 else line_end
                relative_start = occurrence.start() - scope_start
                relative_end = occurrence.end() - scope_start
                scope = pre_example[scope_start:scope_end]
                occurrence_context = (
                    scope[:relative_start] + "<<SLOT>>" + scope[relative_end:]
                )
                satisfied = [
                    index
                    for index, context_pattern in matching_rules
                    if re.search(context_pattern, occurrence_context, re.DOTALL)
                ]
                self.assertTrue(
                    satisfied,
                    f"slot {slot_name} disagrees with its context: {occurrence_context!r}",
                )
                covered_rules.update(satisfied)
        self.assertEqual(covered_rules, set(range(len(PRE_EXAMPLE_SLOT_CONTEXT_RULES))))

    def test_correlation_limit_slot_is_bound_to_the_estimator_guard(self) -> None:
        tree = ast.parse(SCRIPT.read_text(encoding="utf-8"), filename=str(SCRIPT))
        estimator = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "estimate_ar1_rho"
        )
        guard_limits = [
            ast.literal_eval(node.comparators[0])
            for node in ast.walk(estimator)
            if isinstance(node, ast.Compare)
            and len(node.ops) == 1
            and isinstance(node.ops[0], ast.GtE)
            and isinstance(node.left, ast.Call)
            and isinstance(node.left.func, ast.Name)
            and node.left.func.id == "abs"
            and len(node.left.args) == 1
            and isinstance(node.left.args[0], ast.Name)
            and node.left.args[0].id == "rho_hat"
        ]
        self.assertEqual(len(guard_limits), 1)
        guard_limit = float(guard_limits[0])
        rendered_limit = dependence_sensitivity.sheet_slots(
            TEMPLATE.read_text(encoding="utf-8")
        )["correlation_abs_limit"]
        expected = str(int(guard_limit)) if guard_limit.is_integer() else str(guard_limit)
        self.assertEqual(rendered_limit, expected)
        with self.assertRaisesRegex(ValueError, r"abs\(rho\) < 1"):
            dependence_sensitivity.estimate_ar1_rho([1.0, -1.0] * 5, 0.0)

    def test_renderer_refuses_registered_alpha_or_multiplicity_constant_drift(
        self,
    ) -> None:
        self.assertEqual(dependence_sensitivity.render_sheet(), self._document())
        for constant_name, mutation in (
            ("REGISTERED_ALPHA", 0.1),
            ("REGISTERED_MULTIPLICITY", 1),
        ):
            with self.subTest(constant=constant_name):
                with patch.object(dependence_sensitivity, constant_name, mutation):
                    with self.assertRaisesRegex(
                        dependence_sensitivity.SheetRenderError,
                        r"config generator .* expected",
                    ):
                        dependence_sensitivity.render_sheet()

    def test_rendered_agreement_words_match_documented_command_payloads(self) -> None:
        document = self._document()
        commands = _extract_sheet_commands(document)
        self.assertEqual(len(commands), 2)
        payloads = []
        for command in commands:
            completed = subprocess.run(
                shlex.split(command),
                cwd=REPO_ROOT,
                check=False,
                text=True,
                capture_output=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payloads.append(json.loads(completed.stdout))

        example_match = re.search(r"^The gates (?P<word>agree|disagree) in ", document, re.MULTILINE)
        self.assertIsNotNone(example_match)
        assert example_match is not None
        example_agrees = payloads[0]["comparison"]["direction_gate_outcomes_agree"]
        self.assertEqual(example_match.group("word"), "agree" if example_agrees else "disagree")

        disagreement_match = re.search(
            r"^That output has the registered-composition direction screen "
            r"(?P<independent>passing|failing) while the AR\(1\) and halving screens "
            r"(?P<nonregistered>pass|fail),",
            document,
            re.MULTILINE,
        )
        self.assertIsNotNone(disagreement_match)
        assert disagreement_match is not None
        disagreement_models = payloads[1]["models"]
        independent_passes = disagreement_models["independent_blocks"]["direction_gate"]["passes"]
        nonregistered_pass = all(
            disagreement_models[name]["direction_gate"]["passes"]
            for name in ("ar1_estimated_rho", "fixed_effective_n_halving")
        )
        self.assertEqual(
            disagreement_match.group("independent"),
            "passing" if independent_passes else "failing",
        )
        self.assertEqual(
            disagreement_match.group("nonregistered"),
            "pass" if nonregistered_pass else "fail",
        )

    def test_template_digit_and_code_citation_lint_has_a_closed_shape_allowlist(self) -> None:
        template = TEMPLATE.read_text(encoding="utf-8")
        math_spans = [
            match.group("inline") if match.group("inline") is not None else match.group("display")
            for match in MATH_SPAN_PATTERN.finditer(template)
        ]
        outside_math = MATH_SPAN_PATTERN.sub("", template)
        outside_math = TEMPLATE_SLOT_PATTERN.sub("", outside_math)
        for allowed_shape in TEMPLATE_DIGIT_ALLOWLIST:
            outside_math = re.sub(allowed_shape, "", outside_math)
        self.assertNotRegex(outside_math, r"\d")
        for math_span in math_spans:
            without_slots = TEMPLATE_SLOT_PATTERN.sub("", math_span)
            without_permitted_digits = without_slots
            for allowed_shape in TEMPLATE_MATH_DIGIT_ALLOWLIST:
                without_permitted_digits = re.sub(
                    allowed_shape, "", without_permitted_digits
                )
            with self.subTest(math_span=math_span):
                self.assertNotRegex(without_permitted_digits, r"\d")
        without_slots = TEMPLATE_SLOT_PATTERN.sub("", template)
        self.assertNotRegex(
            without_slots,
            r"(?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]+\.py",
        )

    def test_renderer_refuses_a_missing_ast_function_or_draft_anchor(self) -> None:
        citation_slot = "citation_two_sided_student_t_p_value"
        citation_path, _ = dependence_sensitivity.AST_CITATION_SPECS[citation_slot]
        with patch.dict(
            dependence_sensitivity.AST_CITATION_SPECS,
            {citation_slot: (citation_path, "missing_sheet_citation_function")},
        ):
            with self.assertRaisesRegex(
                dependence_sensitivity.SheetRenderError,
                r"expected exactly one definition",
            ):
                dependence_sensitivity.render_sheet()
        with patch.object(
            dependence_sensitivity,
            "DRAFT_PATH",
            dependence_sensitivity.RETENSING_PLAN_PATH,
        ):
            with self.assertRaisesRegex(
                dependence_sensitivity.SheetRenderError,
                r"draft anchor .* exactly once",
            ):
                dependence_sensitivity.render_sheet()


if __name__ == "__main__":
    unittest.main()
