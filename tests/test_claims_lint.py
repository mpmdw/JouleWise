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
        "MDE/n sizing + predeclared top-up rule": (
            "n is frozen before outcomes under D-062; any outcome-dependent "
            "top-up permanently demotes the contrast to exploratory."
        ),
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


def claims_ladder_with_list_and_clause_terms() -> str:
    return """# Claims Ladder

## Ladder

| Level | Allowed Claim Shape | Required Evidence | Forbidden Language |
|---|---|---|---|
| L2 | shape | evidence | cross-boundary winner without calibration, universal, architecture-wide conclusion, extrapolated crossover |
| L4 | shape | evidence | unqualified claims outside tested hardware, workloads, runtime versions, policies, or calibration scope |
"""


def run_cli(args: list[str], cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def run_all_cli(
    root: Path,
    index: Path = Path("claims.jsonl"),
    projection: Path = Path("claims.md"),
) -> subprocess.CompletedProcess[str]:
    return run_cli(
        [
            "--mode",
            "all",
            "--root",
            str(root),
            "--analysis-plans",
            str(ROOT / claims_lint.DEFAULT_AP_PATH),
            "--registry",
            str(ROOT / claims_lint.DEFAULT_REGISTRY_PATH),
            "--campaign-packs",
            str(ROOT / claims_lint.DEFAULT_PACK_DIR),
            "--claims-ladder",
            str(ROOT / claims_lint.DEFAULT_CLAIMS_LADDER_PATH),
            "--analysis-registry",
            str(ROOT / claims_lint.DEFAULT_ANALYSIS_REGISTRY_PATH),
            "--claims-index",
            str(index),
            "--claim-verdict-dir",
            "analysis",
            "--claims-projection",
            str(projection),
            "--json",
        ]
    )


class ClaimsLintFixtureTests(unittest.TestCase):
    def test_marker_mangled_pack_fails_instead_of_disappearing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pack_dir = Path(tmp)
            write(pack_dir / "README.md", "# Pack index")
            write(
                pack_dir / "mangled.md",
                "# Campaign\n\nPlan marker was accidentally renamed beyond recognition.",
            )
            findings = claims_lint.lint_packs(pack_dir, REQUIRED_FIELDS)
            self.assertEqual(
                [finding.code for finding in findings], ["PACK_STRUCTURE_MISSING"]
            )

    def test_good_ap_row_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write(Path(tmp) / "ap.md", ap_document())
            findings, labels = claims_lint.lint_ap_document(path, "ap")
            self.assertEqual(findings, [])
            self.assertEqual(labels, ["AP-1"])

    def test_unqualified_outcome_dependent_top_up_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write(
                Path(tmp) / "ap.md",
                ap_document(
                    {
                        "MDE/n sizing + predeclared top-up rule": (
                            "n=5; top-up near-floor cells after inspecting the CI."
                        )
                    }
                ),
            )

            findings, _ = claims_lint.lint_ap_document(path, "ap")

            self.assertIn(
                "AP_UNQUALIFIED_OUTCOME_DEPENDENT_TOP_UP",
                {finding.code for finding in findings},
            )

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
            (
                "Holm at alpha 0.05 across the primary paired execution-unit "
                "gross-energy contrast and gross-per-committed-output-token companion."
            ),
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

    def test_frozen_axi_rules_pass_while_prior_unqualified_rule_still_fails(self) -> None:
        frozen_multiplicity = (
            "Holm at alpha 0.05 across the primary paired execution-unit "
            "gross-energy contrast and gross-per-committed-output-token companion; "
            "accepted-draft energy is a spec-on mechanism diagnostic, not an on/off contrast."
        )
        frozen_top_up = (
            "Every v2 registry freezes non-null paired n. The closed technical-invalid "
            "set is dispatch failure and strict invalidity; unknown reasons count eligible. "
            "Analysis uses first-eligible-per-cell. Outcome-dependent replacement is refused "
            "as outcome_dependent_topup_forbidden; AP-SPEC permits no post-hoc top-up or pair subset."
        )
        prior_rejected = "n=5; top-up near-floor cells after inspecting the CI."
        with tempfile.TemporaryDirectory() as tmp:
            path = write(
                Path(tmp) / "accepted.md",
                ap_document(
                    {
                        "multiplicity_rule": frozen_multiplicity,
                        "MDE/n sizing + predeclared top-up rule": frozen_top_up,
                    }
                ),
            )
            findings, _ = claims_lint.lint_ap_document(path, "ap")
            self.assertEqual(findings, [])

            rejected_path = write(
                Path(tmp) / "rejected.md",
                ap_document(
                    {"MDE/n sizing + predeclared top-up rule": prior_rejected}
                ),
            )
            rejected_findings, _ = claims_lint.lint_ap_document(rejected_path, "ap")
            self.assertIn(
                "AP_UNQUALIFIED_OUTCOME_DEPENDENT_TOP_UP",
                {finding.code for finding in rejected_findings},
            )

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

    def test_forbidden_terms_split_list_cells_and_keep_comma_clause_whole(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write(
                Path(tmp) / "claims_ladder.md",
                claims_ladder_with_list_and_clause_terms(),
            )
            terms = claims_lint.forbidden_terms_from_claims_ladder(path)
            self.assertIn("universal", terms)
            self.assertIn("cross-boundary winner without calibration", terms)
            self.assertIn(
                "unqualified claims outside tested hardware, workloads, runtime versions, policies, or calibration scope",
                terms,
            )
            self.assertNotIn("workloads", terms)
            self.assertNotIn("policies", terms)

    def test_forbidden_cli_warns_list_terms_not_clause_fragments(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            contracts = tmp_path / "docs" / "contracts"
            contracts.mkdir(parents=True)
            write(contracts / "claims_ladder.md", claims_ladder_with_list_and_clause_terms())
            write(
                tmp_path / "README.md",
                """
                This line makes a universal claim.
                These workloads are listed without the L4 clause.
                These policies are listed without the L4 clause.
                """,
            )
            result = run_cli(["--mode", "forbidden", "--root", str(tmp_path), "--json"])
            payload = json.loads(result.stdout)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            messages = [finding["message"] for finding in payload["findings"]]
            self.assertTrue(any("`universal`" in message for message in messages), payload)
            self.assertFalse(any("`workloads`" in message for message in messages), payload)
            self.assertFalse(any("`policies`" in message for message in messages), payload)

    def test_json_error_envelope_for_claims_lint_error(self) -> None:
        result = run_cli(["--mode", "ap", "--analysis-plans", "missing.md", "--json"])
        payload = json.loads(result.stdout)
        self.assertEqual(result.returncode, 3, result.stderr + result.stdout)
        self.assertEqual(payload["errors"], 1, payload)
        self.assertEqual(payload["findings"][0]["code"], "CLAIMS_LINT_ERROR")

    def test_json_error_envelope_for_argparse_error(self) -> None:
        result = run_cli(["--mode", "nope", "--json"])
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

    def test_pack_lint_rejects_undeclared_overview_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pack_dir = Path(tmp) / "packs"
            pack_dir.mkdir()
            write(
                pack_dir / "overview.md",
                """
                # Campaign Pack Overview

                | Pack | File |
                |---|---|
                | Fixture | fixture.md |
                """,
            )
            findings = claims_lint.lint_packs(pack_dir, REQUIRED_FIELDS)
            self.assertEqual(
                [finding.code for finding in findings], ["PACK_STRUCTURE_MISSING"]
            )

    def test_pack_lint_errors_on_marker_bearing_file_with_broken_ap_table(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pack_dir = Path(tmp) / "packs"
            pack_dir.mkdir()
            write(
                pack_dir / "broken_pack.md",
                """
                # Broken Pack

                ### AP-77: broken

                | Field | Value |
                |-|-|
                | Plan ID / RQ consumer | AP-77 / fixture |
                """,
            )
            findings = claims_lint.lint_packs(pack_dir, REQUIRED_FIELDS)
            codes = {finding.code for finding in findings}
            self.assertIn("AP_TABLE_MISSING", codes)
            self.assertIn("AP_NO_TABLES", codes)

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

    def test_governed_surfaces_include_publication_sources_and_exclude_history(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            governed = (
                "README.md",
                "PROJECT_STATUS.md",
                "docs/phase_4/claims_index.md",
                "docs/report_src/report.md",
                "docs/report_src/chapters/07_results.md",
                "slides/defense.md",
                "docs/slides/backup.md",
                "captions/F1.md",
                "docs/captions/F2.md",
                "tables/T1.md",
                "docs/tables/T2.md",
                "analysis/rpt/tables/T3.md",
                "figures/rpt/captions/F3.md",
            )
            excluded = (
                "docs/run_reports/2026-07-13-history.md",
                "docs/decision_log.md",
                "docs/contracts/other_contract.md",
            )
            for relative in (*governed, *excluded):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                write(path, "Known forbidden wording appears here.")

            contracts = root / "docs/contracts"
            write(contracts / "claims_ladder.md", claims_ladder_document())
            actual = {
                path.relative_to(root).as_posix()
                for path in claims_lint.reader_facing_surfaces(root)
            }
            self.assertEqual(actual, set(governed))

            findings = claims_lint.lint_forbidden_language(
                root, contracts / "claims_ladder.md"
            )
            self.assertTrue(findings)
            self.assertTrue(all(finding.severity == "warning" for finding in findings))
            finding_paths = {Path(finding.path).relative_to(root).as_posix() for finding in findings}
            self.assertEqual(finding_paths, set(governed))


class ClaimsLintRepoTests(unittest.TestCase):
    def test_phase4_repo_projection_is_current(self) -> None:
        findings = claims_lint.lint_phase4(
            ROOT, Path("analysis/rpt001-v1/claims_index.jsonl"),
            Path("docs/phase_4/claims_index.md"), False)
        self.assertFalse([f for f in findings if f.severity == "error"], findings)

    def test_unified_index_malformed_mutated_legacy_and_projection_drift_fail(self) -> None:
        canonical = json.loads((ROOT / "analysis/rpt001-v1/claims_index.jsonl").read_text())
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            index = Path("claims.jsonl")
            projection = Path("claims.md")
            write(root / index, "not-json\n")
            result = run_all_cli(root, index, projection)
            payload = json.loads(result.stdout)
            self.assertEqual(result.returncode, 2, result.stderr + result.stdout)
            self.assertIn(
                "CLAIM_INDEX_MALFORMED_JSONL",
                {finding["code"] for finding in payload["findings"]},
            )

            # Historic divergence pinned: phase4 accepted a structurally valid
            # mutated legacy row, while claim-index rejected it as unsupported.
            # The unified --mode all row dispatch must reject it once, uniformly.
            canonical["claim_text"] = (
                "Separate stack-specific L1 observations remain provisional."
            )
            write(root / index, json.dumps(canonical) + "\n")
            result = run_all_cli(root, index, projection)
            payload = json.loads(result.stdout)
            self.assertEqual(result.returncode, 2, result.stderr + result.stdout)
            self.assertEqual(
                sum(
                    finding["code"] == "CLAIM_INDEX_UNKNOWN_DIALECT"
                    for finding in payload["findings"]
                ),
                1,
                payload,
            )

            canonical = json.loads(
                (ROOT / "analysis/rpt001-v1/claims_index.jsonl").read_text()
            )
            write(root / index, json.dumps(canonical) + "\n")
            write(root / projection, "stale\n")
            result = run_all_cli(root, index, projection)
            payload = json.loads(result.stdout)
            self.assertEqual(result.returncode, 2, result.stderr + result.stdout)
            self.assertIn(
                "PROJECTION_DRIFT",
                {finding["code"] for finding in payload["findings"]},
            )

    def test_real_analysis_plans_and_registries_lint_clean(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--mode",
                "ap",
                "--mode",
                "registry",
                "--mode",
                "analysis-registry",
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
