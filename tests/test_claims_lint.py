from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "claims_lint.py"

spec = importlib.util.spec_from_file_location("claims_lint", SCRIPT)
claims_lint = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["claims_lint"] = claims_lint
spec.loader.exec_module(claims_lint)

REQUIRED_FIELDS = [
    "Plan ID / RQ consumer",
    "family_id",
    "claim_role",
    "selection_scope",
    "multiplicity_rule",
    "Metric + exact window class",
    "Unit of analysis + dependence structure",
    "Estimator/formula",
    "Inclusion/exclusion + quality-flag waiver rules",
    "Order/blocking/covariates",
    "Floor gate",
    "MDE/n sizing + predeclared top-up rule",
    "Denominator provenance requirement",
    "Holdout cells (L3 only)",
    "Claim ceiling + exact forbidden upgrade",
    "Disqualifiers + not-resolvable conditions",
    "Linked manifests/bundle hashes",
]


def required_fields_table(
    requirement_overrides: dict[str, str] | None = None,
    extra_row: str = "",
) -> str:
    overrides = requirement_overrides or {}
    rows = "\n".join(f"| {field} | {overrides.get(field, 'required.')} |" for field in REQUIRED_FIELDS)
    if extra_row:
        rows = f"{rows}\n{extra_row}"
    return f"""## Required fields

| Field | Requirement |
|---|---|
{rows}
"""


def ap_document(
    overrides: dict[str, str | None] | None = None,
    required_table: str | None = None,
) -> str:
    values = {
        "Plan ID / RQ consumer": "AP-1 / fixture consumer.",
        "family_id": "FAM-FIXTURE",
        "claim_role": "primary",
        "selection_scope": "Frozen fixture metric/window/cell set.",
        "multiplicity_rule": "Holm within FAM-FIXTURE.",
        "Metric + exact window class": "energy_request_j request window.",
        "Unit of analysis + dependence structure": "Bundle-level repetitions.",
        "Estimator/formula": "Paired contrast.",
        "Inclusion/exclusion + quality-flag waiver rules": "Strict-valid bundles only.",
        "Order/blocking/covariates": "Manifest order and block.",
        "Floor gate": "pending-P2-015: request-window floor.",
        "MDE/n sizing + predeclared top-up rule": "n=5; top-up near floor.",
        "Denominator provenance requirement": "Runtime-observed tokens.",
        "Holdout cells (L3 only)": "not applicable.",
        "Claim ceiling + exact forbidden upgrade": "Ceiling L2; no universal claim.",
        "Disqualifiers + not-resolvable conditions": "Below-floor effects are not resolvable.",
        "Linked manifests/bundle hashes": "pending post-execution.",
    }
    if overrides:
        for key, value in overrides.items():
            if value is None:
                values.pop(key, None)
            else:
                values[key] = value
    rows = "\n".join(f"| {field} | {value} |" for field, value in values.items())
    required = required_table or required_fields_table()
    return f"""# AP Fixture

{required}

## Seeded plans

### AP-1: fixture

| Field | Value |
|---|---|
{rows}
"""


def write(path: Path, text: str) -> Path:
    path.write_text(textwrap.dedent(text).strip() + "\n", encoding="utf-8")
    return path


def registry_document(extra_rows: str = "", overrides: dict[str, str] | None = None) -> str:
    row = {
        "canonical_id": "RQ-1",
        "aliases": "Alias one",
        "question_type": "research question",
        "status": "candidate",
        "claim_ceiling": "L2",
        "forbidden_upgrade": "no universal claim",
        "AP owner": "AP-1",
        "campaign owner": "campaign",
        "gate_class": "floor",
        "pre_hardware_preparable": "analysis-plan-only",
        "one-line note": "note.",
    }
    row.update(overrides or {})
    row_values = [
        row["canonical_id"],
        row["aliases"],
        row["question_type"],
        row["status"],
        row["claim_ceiling"],
        row["forbidden_upgrade"],
        row["AP owner"],
        row["campaign owner"],
        row["gate_class"],
        row["pre_hardware_preparable"],
        row["one-line note"],
    ]
    row_line = "| " + " | ".join(row_values) + " |"
    return f"""# Research Question Registry

Column legend:

- `canonical_id`: stable row key for the live index.
- `aliases`: other IDs, names, or capability-map labels for the same question.
- `question_type`: one of `research question`, `capability claim`, `application idea`, or `methodology artifact`.
- `status`: `promoted`, `banked`, `candidate`, `killed`, `answered-L1`, or the review-specific `candidate (C-023)`.
- `gate_class`: dominant gate class: `hardware`, `software`, `floor`, `substrate`, or `coordination`.
- `pre_hardware_preparable`: `fully`, `analysis-plan-only`, or `no`.

## Registry Table

| canonical_id | aliases | question_type | status | claim_ceiling | forbidden_upgrade | AP owner | campaign owner | gate_class | pre_hardware_preparable | one-line note |
|---|---|---|---|---|---|---|---|---|---|---|
{row_line}
{extra_rows}"""


def claims_ladder_document(forbidden: str = "known forbidden wording") -> str:
    return f"""# Claims Ladder

## Ladder

| Level | Allowed Claim Shape | Required Evidence | Forbidden Language |
|---|---|---|---|
| L1 | shape | evidence | {forbidden} |
"""


def run_cli(args: list[str], cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


class ClaimsLintFixtureTests(unittest.TestCase):
    def test_good_ap_row_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write(Path(tmp) / "ap.md", ap_document())
            findings, labels = claims_lint.lint_ap_document(path, "ap")
            self.assertEqual(findings, [])
            self.assertEqual(labels, ["AP-1"])

    def test_each_required_ap_field_missing_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            for field in REQUIRED_FIELDS:
                with self.subTest(field=field):
                    path = write(Path(tmp) / f"{field.replace('/', '_')}.md", ap_document({field: None}))
                    findings, _ = claims_lint.lint_ap_document(path, "ap")
                    self.assertTrue(
                        any(finding.code == "AP_MISSING_FIELD" and field in finding.message for finding in findings),
                        findings,
                    )

    def test_each_required_ap_field_empty_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            for field in REQUIRED_FIELDS:
                with self.subTest(field=field):
                    path = write(Path(tmp) / f"{field.replace('/', '_')}.md", ap_document({field: ""}))
                    findings, _ = claims_lint.lint_ap_document(path, "ap")
                    self.assertTrue(
                        any(finding.code == "AP_EMPTY_FIELD" and field in finding.message for finding in findings),
                        findings,
                    )

    def test_required_fields_table_malformed_row_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad_required = required_fields_table(
                {"Plan ID / RQ consumer": "requirement with accidental | extra column"}
            )
            path = write(Path(tmp) / "ap.md", ap_document(required_table=bad_required))
            findings, _ = claims_lint.lint_ap_document(path, "ap")
            codes = {finding.code for finding in findings}
            self.assertIn("REQUIRED_FIELDS_COLUMN_COUNT", codes)
            self.assertIn("REQUIRED_FIELDS_COUNT", codes)

    def test_required_fields_table_contract_count_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            short_rows = "\n".join(f"| {field} | required. |" for field in REQUIRED_FIELDS[:-1])
            required_table = f"""## Required fields

| Field | Requirement |
|---|---|
{short_rows}
"""
            path = write(Path(tmp) / "ap.md", ap_document(required_table=required_table))
            findings, _ = claims_lint.lint_ap_document(path, "ap")
            self.assertTrue(any(finding.code == "REQUIRED_FIELDS_COUNT" for finding in findings), findings)

    def test_required_fields_table_escaped_and_code_span_pipes_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            required_table = required_fields_table(
                {
                    "Plan ID / RQ consumer": "required with escaped \\| pipe.",
                    "family_id": "required with code span `a|b` pipe.",
                }
            )
            path = write(Path(tmp) / "ap.md", ap_document(required_table=required_table))
            findings, _ = claims_lint.lint_ap_document(path, "ap")
            self.assertEqual(findings, [])

    def test_ap_heading_without_parseable_table_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write(
                Path(tmp) / "ap.md",
                f"""{required_fields_table()}

## Seeded plans

### AP-7: broken

| Field | Value |
|-|-|
| Plan ID / RQ consumer | AP-7 |
""",
            )
            findings, _ = claims_lint.lint_ap_document(path, "ap")
            codes = {finding.code for finding in findings}
            self.assertIn("AP_TABLE_MISSING", codes)
            self.assertIn("AP_NO_TABLES", codes)

    def test_ap_malformed_rows_report_column_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write(
                Path(tmp) / "ap.md",
                ap_document({"selection_scope": "Frozen scope | accidental extra column"}),
            )
            findings, _ = claims_lint.lint_ap_document(path, "ap")
            self.assertTrue(any(finding.code == "AP_COLUMN_COUNT" for finding in findings), findings)

    def test_ap_field_constraints_fail(self) -> None:
        cases = {
            "claim_role": ("confirmatory", "AP_BAD_CLAIM_ROLE"),
            "multiplicity_rule": ("familywise correction later", "AP_BAD_MULTIPLICITY_RULE"),
            "Floor gate": ("same metric/window floor before claims", "AP_BAD_FLOOR_GATE"),
        }
        with tempfile.TemporaryDirectory() as tmp:
            for field, (value, code) in cases.items():
                with self.subTest(field=field):
                    path = write(Path(tmp) / f"{field.replace('/', '_')}.md", ap_document({field: value}))
                    findings, _ = claims_lint.lint_ap_document(path, "ap")
                    self.assertTrue(any(finding.code == code for finding in findings), findings)

    def test_multiplicity_rule_accepts_strict_positive_forms(self) -> None:
        accepted = [
            "Holm within FAM-FIXTURE.",
            "Benjamini-Hochberg with q=0.10 across the sweep.",
            "Explicitly exploratory/no-confirmatory-inference.",
        ]
        rejected = [
            "familywise correction later",
            "No Holm correction; multiplicity TBD after execution",
            "not exploratory, promote later",
            "none",
        ]
        for value in accepted:
            with self.subTest(value=value):
                self.assertTrue(claims_lint.multiplicity_rule_is_valid(value))
        for value in rejected:
            with self.subTest(value=value):
                self.assertFalse(claims_lint.multiplicity_rule_is_valid(value))

    def test_registry_duplicate_canonical_id_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            ap_path = write(tmp_path / "analysis_plans.md", ap_document())
            registry_path = write(
                tmp_path / "registry.md",
                registry_document(
                    "| RQ-1 | Alias two | research question | candidate | L2 | no universal claim | AP-1 | campaign | floor | analysis-plan-only | duplicate. |"
                ),
            )
            findings = claims_lint.lint_registry(registry_path, ap_path)
            self.assertTrue(
                any(finding.code == "REGISTRY_DUPLICATE_CANONICAL_ID" for finding in findings),
                findings,
            )

    def test_registry_closed_set_violation_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            ap_path = write(tmp_path / "analysis_plans.md", ap_document())
            cases = [
                ("question_type", "unsupported type", "REGISTRY_BAD_QUESTION_TYPE"),
                ("status", "candidate (outside legend)", "REGISTRY_BAD_STATUS"),
                ("gate_class", "other gate", "REGISTRY_BAD_GATE_CLASS"),
                (
                    "pre_hardware_preparable",
                    "partial",
                    "REGISTRY_BAD_PRE_HARDWARE_PREPARABLE",
                ),
            ]
            for column, value, code in cases:
                with self.subTest(column=column):
                    registry_path = write(tmp_path / f"{column}.md", registry_document(overrides={column: value}))
                    findings = claims_lint.lint_registry(registry_path, ap_path)
                    self.assertTrue(any(finding.code == code for finding in findings), findings)

    def test_registry_wrong_column_count_cli_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            ap_path = write(tmp_path / "analysis_plans.md", ap_document())
            registry_path = write(
                tmp_path / "registry.md",
                registry_document(
                    "| RQ-2 | alias | research question | candidate | L2 | no universal claim | AP-1 | campaign | floor | analysis-plan-only | note | extra |"
                ),
            )
            result = run_cli(
                [
                    "--mode",
                    "registry",
                    "--analysis-plans",
                    str(ap_path),
                    "--registry",
                    str(registry_path),
                    "--json",
                ]
            )
            payload = json.loads(result.stdout)
            self.assertEqual(result.returncode, 2, result.stderr + result.stdout)
            self.assertGreater(payload["errors"], 0, payload)
            self.assertTrue(
                any(finding["code"] == "REGISTRY_COLUMN_COUNT" for finding in payload["findings"]),
                payload,
            )

    def test_forbidden_terms_keep_comma_clause_whole(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write(
                Path(tmp) / "claims_ladder.md",
                claims_ladder_document(
                    "unqualified claims outside tested hardware, workloads, runtime versions, policies, or calibration scope"
                ),
            )
            terms = claims_lint.forbidden_terms_from_claims_ladder(path)
            self.assertIn(
                "unqualified claims outside tested hardware, workloads, runtime versions, policies, or calibration scope",
                terms,
            )
            self.assertNotIn("workloads", terms)
            self.assertNotIn("policies", terms)

    def test_json_error_envelope_for_claims_lint_error(self) -> None:
        result = run_cli(["--mode", "ap", "--analysis-plans", "missing.md", "--json"])
        payload = json.loads(result.stdout)
        self.assertEqual(result.returncode, 3, result.stderr + result.stdout)
        self.assertEqual(payload["errors"], 1, payload)
        self.assertEqual(payload["findings"][0]["code"], "CLAIMS_LINT_ERROR")

    def test_bad_ap_cli_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write(Path(tmp) / "analysis_plans.md", ap_document({"family_id": None}))
            result = run_cli(["--mode", "ap", "--analysis-plans", str(path), "--json"])
            payload = json.loads(result.stdout)
            self.assertEqual(result.returncode, 2, result.stderr + result.stdout)
            self.assertGreater(payload["errors"], 0, payload)
            self.assertTrue(any(finding["code"] == "AP_MISSING_FIELD" for finding in payload["findings"]), payload)

    def test_bad_registry_cli_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            ap_path = write(tmp_path / "analysis_plans.md", ap_document())
            registry_path = write(tmp_path / "registry.md", registry_document(overrides={"status": "later"}))
            result = run_cli(
                [
                    "--mode",
                    "registry",
                    "--analysis-plans",
                    str(ap_path),
                    "--registry",
                    str(registry_path),
                    "--json",
                ]
            )
            payload = json.loads(result.stdout)
            self.assertEqual(result.returncode, 2, result.stderr + result.stdout)
            self.assertGreater(payload["errors"], 0, payload)
            self.assertTrue(any(finding["code"] == "REGISTRY_BAD_STATUS" for finding in payload["findings"]), payload)

    def test_bad_pack_cli_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            ap_path = write(tmp_path / "analysis_plans.md", ap_document())
            pack_dir = tmp_path / "packs"
            pack_dir.mkdir()
            write(pack_dir / "bad_pack.md", ap_document({"family_id": None}))
            result = run_cli(
                [
                    "--mode",
                    "pack",
                    "--analysis-plans",
                    str(ap_path),
                    "--campaign-packs",
                    str(pack_dir),
                    "--json",
                ]
            )
            payload = json.loads(result.stdout)
            self.assertEqual(result.returncode, 2, result.stderr + result.stdout)
            self.assertGreater(payload["errors"], 0, payload)
            self.assertTrue(any(finding["code"] == "AP_MISSING_FIELD" for finding in payload["findings"]), payload)

    def test_forbidden_cli_warns_but_exits_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            contracts = tmp_path / "docs" / "contracts"
            contracts.mkdir(parents=True)
            write(contracts / "claims_ladder.md", claims_ladder_document())
            write(tmp_path / "README.md", "This has known forbidden wording in reader-facing prose.")
            result = run_cli(["--mode", "forbidden", "--root", str(tmp_path), "--json"])
            payload = json.loads(result.stdout)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertEqual(payload["errors"], 0, payload)
            self.assertGreater(payload["warnings"], 0, payload)
            self.assertTrue(
                any(finding["code"] == "FORBIDDEN_LANGUAGE_REVIEW" for finding in payload["findings"]),
                payload,
            )


class ClaimsLintRepoTests(unittest.TestCase):
    def test_real_analysis_plans_and_registry_lint_clean(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--mode",
                "ap",
                "--mode",
                "registry",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertEqual(payload["errors"], 0, payload)


if __name__ == "__main__":
    unittest.main()
