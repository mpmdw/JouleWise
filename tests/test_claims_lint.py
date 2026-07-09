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


def required_fields_table() -> str:
    rows = "\n".join(f"| {field} | required. |" for field in REQUIRED_FIELDS)
    return f"""## Required fields

| Field | Requirement |
|---|---|
{rows}
"""


def ap_document(overrides: dict[str, str | None] | None = None) -> str:
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
    return f"""# AP Fixture

{required_fields_table()}

## Seeded plans

### AP-1: fixture

| Field | Value |
|---|---|
{rows}
"""


def write(path: Path, text: str) -> Path:
    path.write_text(textwrap.dedent(text).strip() + "\n", encoding="utf-8")
    return path


def registry_document(extra_rows: str = "", bad_status: bool = False) -> str:
    status = "candidate (outside legend)" if bad_status else "candidate"
    return f"""# Research Question Registry

Column legend:

- `canonical_id`: stable row key for the live index.
- `aliases`: other IDs, names, or capability-map labels for the same question.
- `question_type`: one of `research question`, `capability claim`, `application idea`, or `methodology artifact`.
- `status`: `promoted`, `banked`, `candidate`, `killed`, `answered-L1`, or the review-specific `candidate (C-023)`.
- `gate_class`: dominant gate class: `hardware`, `software`, `floor`, `substrate`, or `coordination`.

## Registry Table

| canonical_id | aliases | question_type | status | claim_ceiling | forbidden_upgrade | AP owner | campaign owner | gate_class | pre_hardware_preparable | one-line note |
|---|---|---|---|---|---|---|---|---|---|---|
| RQ-1 | Alias one | research question | {status} | L2 | no universal claim | AP-1 | campaign | floor | analysis-plan-only | note. |
{extra_rows}"""


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

    def test_registry_field_constraints_fail(self) -> None:
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
            registry_path = write(tmp_path / "registry.md", registry_document(bad_status=True))
            findings = claims_lint.lint_registry(registry_path, ap_path)
            self.assertTrue(
                any(finding.code == "REGISTRY_BAD_STATUS" for finding in findings),
                findings,
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
