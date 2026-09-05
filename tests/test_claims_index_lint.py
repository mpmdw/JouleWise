from __future__ import annotations

import base64
import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from joulewise.analysis_engine.artifact import validate_claim_verdicts
from tests.test_detection_floor import make_artifact


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "claims_lint.py"

spec = importlib.util.spec_from_file_location("claims_index_lint_module", SCRIPT)
claims_lint = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["claims_index_lint_module"] = claims_lint
spec.loader.exec_module(claims_lint)

FIXTURE_BLOCK_IDS = tuple(f"block-{index}" for index in range(1, 7))
FIXTURE_BUNDLE_PAIRS = tuple(
    (f"bundle-a-{index}", f"bundle-b-{index}") for index in range(1, 7)
)
FIXTURE_BUNDLE_IDS = tuple(
    bundle_id for pair in FIXTURE_BUNDLE_PAIRS for bundle_id in pair
)


def embedded_floor_fixture() -> tuple[dict, list[dict]]:
    artifact = make_artifact()
    artifact["artifact_id"] = "df-fixture"
    raw = (json.dumps(artifact, indent=2) + "\n").encode("utf-8")
    basis_by_root: dict[str, set[str]] = {}
    for cell in artifact["cells"]:
        for component_name in ("absolute", "comparative"):
            component = cell["provenance"][component_name]
            basis_by_root.setdefault(component["evidence_root_id"], set()).add(
                component["campaign_log"]["sha256"]
            )
    return (
        {
            "artifact_id": artifact["artifact_id"],
            "file_sha256": hashlib.sha256(raw).hexdigest(),
            "embedded_bytes_base64": base64.b64encode(raw).decode("ascii"),
        },
        [
            {
                "scope": "floor_evidence",
                "evidence_root_id": root_id,
                "authenticated_basis": {
                    "kind": "floor_component_campaign_log_sha256",
                    "sha256s": sorted(basis_by_root[root_id]),
                },
                "raw_count": 0,
                "validated_count": 0,
                "status": "clean",
            }
            for root_id in sorted(basis_by_root)
        ],
    )


FLOOR_LINK, FLOOR_AUDITS = embedded_floor_fixture()


def bundle_audit_row(bundle_id: str) -> dict:
    parts = bundle_id.split("-")
    side = parts[1]
    index = parts[2]
    return {
        "bundle_id": bundle_id,
        "relative_path": f"runs/{bundle_id}",
        "entry_id": f"entry-{bundle_id}",
        "block_id": f"block-{index}",
        "cell_id": f"cell-{side}",
        "condition_id": f"condition-{side}",
        "config_sha256": "3" * 64,
        "expected_config_sha256": "3" * 64,
        "manifest_config_sha256": "3" * 64,
        "summary_sha256": "4" * 64,
        "strict_status": "valid",
        "strict_problems": [],
        "summary_status": "succeeded",
        "base_reason_codes": [],
        "window_prechecks": {},
        "cooldown_cap_hit": False,
        "campaign_cooldown": None,
        "idle_window_suspect": False,
        "token_provenance": {
            "output_tokens": None,
            "token_count_source": None,
            "stop_reason": None,
            "output_policy": None,
            "tokenizer_identity": None,
        },
        "scientific_identity": None,
        "replacement_classification": "registered",
        "inclusion_status": "included",
    }


def canonical_verdict_id(artifact: dict) -> str:
    body = copy.deepcopy(artifact)
    body.pop("claim_verdicts_id", None)
    canonical = json.dumps(
        body,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return "cv-" + hashlib.sha256(canonical).hexdigest()


def base_artifact() -> dict:
    artifact = {
        "schema_version": "joulewise.claim_verdicts.v1",
        "claim_verdicts_id": "",
        "engine": {
            "implementation": "joulewise.analysis_engine",
            "algorithm_version": "1",
            "difference_orientation": "condition_b_minus_condition_a",
            "policy_identity": {
                "floor_resolution": "declared_exact_bundle_config_floor_v1",
                "stochastic_variance": "p2044_reducer_0_4_1_idle_variance_v1",
                "campaign_cooldown": "campaign_provenance_v1_hash_bound_per_member_v1",
            },
        },
        "inputs": {
            "analysis_manifest": {
                "manifest_id": "am-fixture",
                "file_sha256": "1" * 64,
            },
            "floor_artifact": copy.deepcopy(FLOOR_LINK),
            "runs_root_label": "runs",
            "evidence_class": "current",
            "limitations": [],
        },
        "supersession_audit": [
            {
                "scope": "analysis_corpus",
                "evidence_root_id": None,
                "authenticated_basis": {
                    "kind": "analysis_manifest_file_sha256",
                    "sha256": "1" * 64,
                },
                "raw_count": 0,
                "validated_count": 0,
                "status": "clean",
            },
            *copy.deepcopy(FLOOR_AUDITS),
        ],
        "bundle_audit": [
            bundle_audit_row(bundle_id) for bundle_id in sorted(FIXTURE_BUNDLE_IDS)
        ],
        "sampling_audit": {
            "design": "fixed_n",
            "planned_n_blocks": 6,
            "registered_blocks": list(FIXTURE_BLOCK_IDS),
            "valid_replacements": [],
            "unregistered_matching_bundles": [],
            "top_up_detected": False,
            "demoted_contrast_ids": [],
        },
        "families": [
            {
                "family_instance_id": "family-fixture",
                "plan_id": "AP-2",
                "claim_role": "primary",
                "method": "holm",
                "alpha": 0.05,
                "q": None,
                "m": 1,
                "contrast_ids": ["ctr-fixture-b-minus-a"],
                "finite_test_count": 1,
                "raw_ordering": ["ctr-fixture-b-minus-a"],
                "adjusted_p_values": {"ctr-fixture-b-minus-a": 0.0},
                "missing_test_ids": [],
                "structural_status": "complete",
            }
        ],
        "contrasts": [
            {
                "contrast_id": "ctr-fixture-b-minus-a",
                "plan_id": "AP-2",
                "family_instance_id": "family-fixture",
                "claim_role": "primary",
                "metric": {
                    "name": "gross_energy_j",
                    "metric_tag": "gross",
                    "window_class": "gross_request",
                    "unit": "J",
                    "ratio_estimand": None,
                },
                "conditions": {
                    "condition_a_id": "condition-a",
                    "condition_b_id": "condition-b",
                    "cell_a_id": "cell-a",
                    "cell_b_id": "cell-b",
                    "difference_orientation": "condition_b_minus_condition_a",
                },
                "hypothesized_direction": "positive",
                "equivalence": None,
                "mde": None,
                "bundle_blocks": {
                    "planned_block_ids": list(FIXTURE_BLOCK_IDS),
                    "included_bundle_ids": sorted(FIXTURE_BUNDLE_IDS),
                    "blocks": [
                        {
                            "block_id": block_id,
                            "bundle_a_id": bundle_a_id,
                            "bundle_b_id": bundle_b_id,
                            "included": True,
                            "reason_codes": [],
                        }
                        for block_id, (bundle_a_id, bundle_b_id) in zip(
                            FIXTURE_BLOCK_IDS,
                            FIXTURE_BUNDLE_PAIRS,
                            strict=True,
                        )
                    ],
                },
                "sampling": {
                    "confirmatory_status": "confirmatory",
                    "planned_n": 6,
                    "observed_complete_n": 6,
                },
                "estimator": {
                    "name": "paired_mean_difference",
                    "n": 6,
                    "df": 5,
                    "estimate": 1.0,
                    "s_d": 0.0,
                    "SE_repeat": 0.0,
                    "SE_metrology": 0.0,
                    "SE_total": 0.0,
                    "t_critical_95": 2.571,
                    "repeat_point_CI95": {"lower": 1.0, "upper": 1.0},
                    "metrology_aware_CI95": {"lower": 1.0, "upper": 1.0},
                    "variance_contributions": [],
                    "excluded_stochastic_terms": ["E_gross_repetition_j2"],
                    "raw_p": 0.0,
                },
                "deterministic_bounds": {
                    "terms": [],
                    "total": 0.0,
                    "decision_interval": {"lower": 1.0, "upper": 1.0},
                },
                "floor": {
                    "status": "resolved",
                    "floor_row_ids": ["floor-cell-fixture"],
                    "floor_abs_j": 0.1,
                    "floor_cmp_j": 0.1,
                    "active_floor_j": 0.1,
                    "transport_verdict": "exact",
                    "resolutions": [
                        {
                            "status": "exact",
                            "source_cell_ids": ["floor-cell-fixture"],
                            "transport_group_id": "transport-fixture",
                            "transport_rule_id": "rule-fixture",
                            "floor_abs_j": 0.1,
                            "floor_cmp_j": 0.1,
                            "floor_gate_j": 0.1,
                            "reason_codes": [],
                        }
                    ],
                },
                "multiplicity": {
                    "raw_p": 0.0,
                    "adjusted_p": 0.0,
                    "rejected": True,
                },
                "randomization_check": {
                    "status": "clean",
                    "reason": None,
                    "n_blocks": 6,
                    "exact_two_sided_p": 0.03125,
                    "rejects": True,
                },
                "loo": {
                    "status": "complete",
                    "rows": [
                        {
                            "omitted_block_id": block_id,
                            "n_blocks": 5,
                            "df": 4,
                            "estimate": 1.0,
                            "metrology_aware_ci95": {"lower": 1.0, "upper": 1.0},
                            "decision_interval": {"lower": 1.0, "upper": 1.0},
                            "floor_status": "above_floor",
                            "raw_p": 0.0,
                            "adjusted_p": 0.0,
                            "outcome": "direction_supported",
                            "influence_triggers": [],
                        }
                        for block_id in FIXTURE_BLOCK_IDS
                    ],
                },
                "sensitivity_status": "clean",
                "claim_evaluation": {
                    "outcome": "direction_supported",
                    "direction": "positive",
                    "reason_codes": [],
                    "claim_ready_for_l2_l3": True,
                    "claim_level_ceiling": "L2",
                },
            }
        ],
    }
    artifact["claim_verdicts_id"] = canonical_verdict_id(artifact)
    return artifact


def base_row() -> dict:
    return {
        "schema": "joulewise.claims_index.v1",
        "claim_id": "CLM-FIXTURE-001",
        "claim_text": "The registered condition-B effect is directionally supported.",
        "ladder_level": "L2",
        "AP_id": "AP-2",
        "contrast_id": "ctr-fixture-b-minus-a",
        "verdict_artifact": "analysis/claim_verdicts.json",
        "verdict_sha256": "",
        "engine_outcome": "direction_supported",
        "claim_role": "primary",
        "editorial_status": "supported",
        "figures": ["F-fixture"],
        "script_function": "make_fixture_figure",
        "dataset_filter": "contrast_id == ctr-fixture-b-minus-a",
        "bundle_manifest_ids": {
            "analysis_manifest_id": "am-fixture",
            "floor_artifact_id": "df-fixture",
            "bundle_ids": sorted(FIXTURE_BUNDLE_IDS),
        },
        "caveat": "",
    }


def write_fixture(root: Path, artifact: dict, row: dict) -> tuple[Path, Path]:
    analysis = root / "analysis"
    analysis.mkdir(parents=True, exist_ok=True)
    artifact_path = analysis / "claim_verdicts.json"
    artifact_bytes = (
        json.dumps(artifact, indent=2, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    artifact_path.write_bytes(artifact_bytes)
    row["verdict_sha256"] = hashlib.sha256(artifact_bytes).hexdigest()
    index_path = root / "claims_index.jsonl"
    index_path.write_text(
        json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return index_path, artifact_path


def lint_fixture(root: Path) -> list:
    return claims_lint.lint_claim_index(
        root,
        Path("claims_index.jsonl"),
        Path("analysis"),
    )


def run_all_cli_fixture(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
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
            "claims_index.jsonl",
            "--claim-verdict-dir",
            "analysis",
            "--claims-projection",
            "claims_index.md",
            "--json",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def error_codes(findings: list) -> set[str]:
    return {finding.code for finding in findings if finding.severity == "error"}


class ClaimIndexLintTests(unittest.TestCase):
    def test_default_and_all_include_unified_claim_index_gate(self) -> None:
        self.assertIn("claim-index", claims_lint.selected_modes(None))
        self.assertIn("claim-index", claims_lint.selected_modes(["all"]))

    def test_version_dispatch_authority_cases_fail_closed(self) -> None:
        legacy = json.loads(
            (ROOT / "analysis/rpt001-v1/claims_index.jsonl").read_text(
                encoding="utf-8"
            )
        )
        voided_legacy = json.loads(
            (ROOT / "analysis/rpt001-v2/claims_index.jsonl").read_text(
                encoding="utf-8"
            )
        )
        current = base_row()
        unknown = {
            "schema": "joulewise.claims_index.v1",
            "claim_id": "CLM-UNKNOWN-001",
            "claim_text": "This row has no authority-bearing dialect fields.",
        }
        hybrid = copy.deepcopy(current)
        hybrid["claim_level"] = "L2"
        self.assertEqual(claims_lint._claim_row_dialect(legacy), "exact-legacy")
        self.assertEqual(
            claims_lint._claim_row_dialect(voided_legacy), "voided-legacy"
        )
        self.assertEqual(claims_lint._claim_row_dialect(current), "engine-linked")
        self.assertEqual(claims_lint._claim_row_dialect(unknown), "unknown")
        self.assertEqual(claims_lint._claim_row_dialect(hybrid), "hybrid")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for label, row, expected in (
                ("unknown", unknown, "CLAIM_INDEX_UNKNOWN_DIALECT"),
                ("hybrid", hybrid, "CLAIM_INDEX_AMBIGUOUS_DIALECT"),
            ):
                with self.subTest(label=label):
                    (root / "claims.jsonl").write_text(
                        json.dumps(row) + "\n", encoding="utf-8"
                    )
                    findings = claims_lint.lint_claim_index(
                        root, Path("claims.jsonl"), Path("analysis")
                    )
                    self.assertIn(expected, error_codes(findings))

    def test_historical_pre_p2037_legacy_row_is_exactly_grandfathered(self) -> None:
        canonical_row = json.loads(
            (ROOT / "analysis/rpt001-v1/claims_index.jsonl").read_text(encoding="utf-8")
        )
        self.assertTrue(claims_lint._is_grandfathered_pre_p2037_legacy_row(canonical_row))
        for key, value in (
            ("evidence_class", "legacy_l1"),
            ("verdict_status", "pending"),
            ("claim_level", "L2"),
            ("claim_id", "CLM-RPT001-LEGACY-L1-MUTATED"),
            ("schema", "joulewise.claims_index.mutant"),
            ("status", "weak"),
            ("legacy_label", "legacy L1"),
        ):
            with self.subTest(key=key), tempfile.TemporaryDirectory() as tmp:
                changed = copy.deepcopy(canonical_row)
                if key == "verdict_status":
                    changed["verdict_ref"]["status"] = value
                else:
                    changed[key] = value
                self.assertFalse(
                    claims_lint._is_grandfathered_pre_p2037_legacy_row(changed)
                )
                fixture_root = Path(tmp)
                (fixture_root / "claims.jsonl").write_text(
                    json.dumps(changed) + "\n",
                    encoding="utf-8",
                )
                findings = claims_lint.lint_claim_index(
                    fixture_root,
                    Path("claims.jsonl"),
                    Path("analysis"),
                )
                self.assertTrue(error_codes(findings), findings)
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--mode",
                "phase4",
                "--mode",
                "claim-index",
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
        self.assertEqual(payload["findings"], [])

    def test_voided_legacy_status_kill_rejects_supported(self) -> None:
        row = json.loads(
            (ROOT / "analysis/rpt001-v2/claims_index.jsonl").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(row["status"], "voided")
        row["status"] = "supported"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "claims.jsonl").write_text(
                json.dumps(row) + "\n", encoding="utf-8"
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--mode",
                    "claim-index",
                    "--root",
                    str(root),
                    "--claims-index",
                    "claims.jsonl",
                    "--json",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        payload = json.loads(result.stdout)
        self.assertEqual(result.returncode, 2, result.stderr + result.stdout)
        self.assertIn(
            "CLAIM_INDEX_UNKNOWN_DIALECT",
            {finding["code"] for finding in payload["findings"]},
        )

    def test_default_and_all_cli_reach_unified_version_dispatch(self) -> None:
        for mode_args in ([], ["--mode", "all"]):
            with self.subTest(mode_args=mode_args):
                result = subprocess.run(
                    [sys.executable, str(SCRIPT), *mode_args, "--json"],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                payload = json.loads(result.stdout)
                self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
                self.assertEqual(payload["errors"], 0, payload)
                self.assertEqual(
                    sum(
                        finding["code"] == "CLAIM_INDEX_PRE_P2037_LEGACY_SKIPPED"
                        for finding in payload["findings"]
                    ),
                    0,
                    payload,
                )

    def test_exact_grandfathered_row_may_appear_only_once(self) -> None:
        canonical_row = json.loads(
            (ROOT / "analysis/rpt001-v1/claims_index.jsonl").read_text(encoding="utf-8")
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "claims.jsonl").write_text(
                json.dumps(canonical_row) + "\n" + json.dumps(canonical_row) + "\n",
                encoding="utf-8",
            )
            findings = claims_lint.lint_claim_index(
                root, Path("claims.jsonl"), Path("analysis")
            )
        self.assertIn(
            "CLAIM_INDEX_DUPLICATE_PRE_P2037_LEGACY",
            error_codes(findings),
        )

    def test_supported_row_with_exact_links_passes_cli(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root, base_artifact(), base_row())
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--mode",
                    "claim-index",
                    "--root",
                    str(root),
                    "--claims-index",
                    "claims_index.jsonl",
                    "--claim-verdict-dir",
                    "analysis",
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

    def test_wording_gate_allows_supported_l2_direction_but_keeps_l1_conservative(self) -> None:
        claim_text = (
            "Within the named boundary, condition A uses less energy than condition B."
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            row = base_row()
            row["claim_text"] = claim_text
            write_fixture(root, base_artifact(), row)
            self.assertNotIn(
                "CLAIM_INDEX_FORBIDDEN_CLAIM_UPGRADE",
                error_codes(lint_fixture(root)),
            )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            row = base_row()
            row.update(
                claim_text=claim_text,
                ladder_level="L1",
                caveat="Instrument-level wording only.",
            )
            write_fixture(root, base_artifact(), row)
            self.assertIn(
                "CLAIM_INDEX_FORBIDDEN_CLAIM_UPGRADE",
                error_codes(lint_fixture(root)),
            )

    def test_changed_verdict_bytes_require_updated_index_hash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, artifact_path = write_fixture(root, base_artifact(), base_row())
            artifact_path.write_bytes(artifact_path.read_bytes() + b" ")
            self.assertIn(
                "CLAIM_INDEX_VERDICT_HASH_MISMATCH",
                error_codes(lint_fixture(root)),
            )

    def test_updated_hash_does_not_authorize_noncanonical_artifact_render(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            index_path, artifact_path = write_fixture(root, base_artifact(), base_row())
            artifact_bytes = json.dumps(
                base_artifact(), separators=(",", ":"), ensure_ascii=False
            ).encode("utf-8")
            artifact_path.write_bytes(artifact_bytes)
            row = json.loads(index_path.read_text(encoding="utf-8"))
            row["verdict_sha256"] = hashlib.sha256(artifact_bytes).hexdigest()
            index_path.write_text(json.dumps(row) + "\n", encoding="utf-8")
            self.assertIn(
                "CLAIM_INDEX_VERDICT_RENDER_INVALID",
                error_codes(lint_fixture(root)),
            )

    def test_updated_hash_and_id_do_not_authorize_reordered_b13_envelope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            original = base_artifact()
            artifact = {key: original[key] for key in reversed(tuple(original))}
            artifact["claim_verdicts_id"] = canonical_verdict_id(artifact)
            write_fixture(root, artifact, base_row())
            self.assertIn(
                "CLAIM_INDEX_VERDICT_SCHEMA_INVALID",
                error_codes(lint_fixture(root)),
            )

    def test_all_mode_dispatch_rejects_engine_and_b15_mutation_union(self) -> None:
        mutants: list[tuple[str, dict, str]] = []

        engine_semantic = base_artifact()
        engine_semantic["engine"]["algorithm_version"] = "future"
        engine_semantic["claim_verdicts_id"] = canonical_verdict_id(engine_semantic)
        mutants.append(("engine semantic", engine_semantic, "unsupported implementation"))

        original = base_artifact()
        reordered = {key: original[key] for key in reversed(tuple(original))}
        reordered["claim_verdicts_id"] = canonical_verdict_id(reordered)
        mutants.append(("B15 ordering", reordered, "pinned B13 order"))

        absolute_path = base_artifact()
        absolute_path["bundle_audit"][0]["relative_path"] = "/tmp/run"
        absolute_path["claim_verdicts_id"] = canonical_verdict_id(absolute_path)
        mutants.append(("B15 path", absolute_path, "absolute path is forbidden"))

        two_look = base_artifact()
        two_look["sampling_audit"]["design"] = "two_look_alpha_spending"
        two_look["claim_verdicts_id"] = canonical_verdict_id(two_look)
        mutants.append(("production admission", two_look, "deliberately permits only fixed_n"))

        for source, mutant, expected in mutants:
            with self.subTest(source=source), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                write_fixture(root, mutant, base_row())
                result = run_all_cli_fixture(root)
                payload = json.loads(result.stdout)
                self.assertEqual(result.returncode, 2, result.stderr + result.stdout)
                self.assertTrue(
                    any(
                        finding["code"] == "CLAIM_INDEX_VERDICT_SCHEMA_INVALID"
                        and expected in finding["message"]
                        for finding in payload["findings"]
                    ),
                    payload,
                )

                if source == "B15 ordering":
                    # Historic divergence pinned: the engine validator accepted
                    # reordered keys while the duplicated B15 validator rejected
                    # them. The --mode all row dispatch must retain that rejection.
                    self.assertEqual(validate_claim_verdicts(mutant), [])

    def test_artifact_canonical_id_and_schema_are_validated(self) -> None:
        cases = (
            ("bad_id", "CLAIM_INDEX_VERDICT_ID_MISMATCH"),
            ("extra_key", "CLAIM_INDEX_VERDICT_SCHEMA_INVALID"),
            ("missing_floor", "CLAIM_INDEX_VERDICT_SCHEMA_INVALID"),
            ("duplicate_contrast", "CLAIM_INDEX_CONTRAST_NOT_UNIQUE"),
        )
        for mutation, expected in cases:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                artifact = base_artifact()
                if mutation == "bad_id":
                    artifact["claim_verdicts_id"] = "cv-" + "0" * 64
                elif mutation == "extra_key":
                    artifact["unrecognized"] = True
                    artifact["claim_verdicts_id"] = canonical_verdict_id(artifact)
                elif mutation == "missing_floor":
                    artifact["contrasts"][0].pop("floor")
                    artifact["claim_verdicts_id"] = canonical_verdict_id(artifact)
                else:
                    artifact["contrasts"].append(copy.deepcopy(artifact["contrasts"][0]))
                    artifact["claim_verdicts_id"] = canonical_verdict_id(artifact)
                write_fixture(root, artifact, base_row())
                self.assertIn(expected, error_codes(lint_fixture(root)))

    def test_supported_direction_rejects_zero_crossing_decision_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifact = base_artifact()
            contrast = artifact["contrasts"][0]
            contrast["estimator"]["metrology_aware_CI95"] = {
                "lower": -0.1,
                "upper": 1.1,
            }
            contrast["deterministic_bounds"]["decision_interval"] = {
                "lower": -0.1,
                "upper": 1.1,
            }
            artifact["claim_verdicts_id"] = canonical_verdict_id(artifact)
            write_fixture(root, artifact, base_row())
            self.assertIn(
                "CLAIM_INDEX_VERDICT_SCHEMA_INVALID",
                error_codes(lint_fixture(root)),
            )

    def test_rehashed_loo_family_and_trigger_mutation_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifact = base_artifact()
            loo_row = artifact["contrasts"][0]["loo"]["rows"][0]
            loo_row["adjusted_p"] = 0.999999
            loo_row["outcome"] = "unresolved"
            loo_row["influence_triggers"] = []
            artifact["claim_verdicts_id"] = canonical_verdict_id(artifact)
            write_fixture(root, artifact, base_row())
            self.assertIn(
                "CLAIM_INDEX_VERDICT_SCHEMA_INVALID",
                error_codes(lint_fixture(root)),
            )

    def test_rehashed_loo_escalation_cannot_launder_aggregate_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifact = base_artifact()
            loo_row = artifact["contrasts"][0]["loo"]["rows"][0]
            loo_row["outcome"] = "unresolved"
            loo_row["influence_triggers"] = ["outcome"]
            artifact["claim_verdicts_id"] = canonical_verdict_id(artifact)
            write_fixture(root, artifact, base_row())
            self.assertIn(
                "CLAIM_INDEX_VERDICT_SCHEMA_INVALID",
                error_codes(lint_fixture(root)),
            )

    def test_rehashed_randomization_disagreement_cannot_promote_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifact = base_artifact()
            artifact["contrasts"][0]["randomization_check"]["rejects"] = False
            artifact["claim_verdicts_id"] = canonical_verdict_id(artifact)
            write_fixture(root, artifact, base_row())
            self.assertIn(
                "CLAIM_INDEX_VERDICT_SCHEMA_INVALID",
                error_codes(lint_fixture(root)),
            )

    def test_authoritative_validator_rejects_unknown_and_misordered_reasons(self) -> None:
        cases = (
            ["invented_unratified_code"],
            ["effect_not_above_floor", "metric_missing_or_nonfinite"],
        )
        for reasons in cases:
            with self.subTest(reasons=reasons), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                artifact = base_artifact()
                evaluation = artifact["contrasts"][0]["claim_evaluation"]
                evaluation.update(
                    outcome="not_estimable",
                    direction=None,
                    reason_codes=reasons,
                    claim_ready_for_l2_l3=False,
                )
                artifact["claim_verdicts_id"] = canonical_verdict_id(artifact)
                row = base_row()
                row.update(
                    engine_outcome="not_estimable",
                    editorial_status="weak",
                    claim_text="The registered contrast is not estimable.",
                    caveat=" ".join(reasons),
                )
                write_fixture(root, artifact, row)
                self.assertIn(
                    "CLAIM_INDEX_VERDICT_SCHEMA_INVALID",
                    error_codes(lint_fixture(root)),
                )

    def test_every_exact_link_is_checked(self) -> None:
        cases = (
            ("AP_id", "AP-3", "CLAIM_INDEX_AP_MISMATCH"),
            ("claim_role", "secondary", "CLAIM_INDEX_ROLE_MISMATCH"),
            ("engine_outcome", "equivalent", "CLAIM_INDEX_OUTCOME_MISMATCH"),
            (
                "analysis_manifest_id",
                "am-other",
                "CLAIM_INDEX_ANALYSIS_MANIFEST_MISMATCH",
            ),
            (
                "floor_artifact_id",
                "df-other",
                "CLAIM_INDEX_FLOOR_ARTIFACT_MISMATCH",
            ),
            ("bundle_ids", ["bundle-a"], "CLAIM_INDEX_BUNDLE_IDS_MISMATCH"),
        )
        for field, value, expected in cases:
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                row = base_row()
                if field in {"analysis_manifest_id", "floor_artifact_id", "bundle_ids"}:
                    row["bundle_manifest_ids"][field] = value
                else:
                    row[field] = value
                write_fixture(root, base_artifact(), row)
                self.assertIn(expected, error_codes(lint_fixture(root)))

    def test_supported_l2_l3_requires_every_engine_gate(self) -> None:
        cases = (
            ("outcome", "unresolved", "CLAIM_INDEX_SUPPORTED_OUTCOME_INVALID"),
            (
                "claim_ready_for_l2_l3",
                False,
                "CLAIM_INDEX_SUPPORTED_NOT_CLAIM_READY",
            ),
            ("role", "exploratory", "CLAIM_INDEX_SUPPORTED_EXPLORATORY"),
            ("demotion", "demoted_exploratory", "CLAIM_INDEX_SUPPORTED_DEMOTED"),
            ("ceiling", "L1", "CLAIM_INDEX_SUPPORTED_ABOVE_CEILING"),
        )
        for mutation, value, expected in cases:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                artifact = base_artifact()
                row = base_row()
                contrast = artifact["contrasts"][0]
                evaluation = contrast["claim_evaluation"]
                if mutation == "outcome":
                    evaluation["outcome"] = value
                    evaluation["direction"] = None
                    row["engine_outcome"] = value
                    row["claim_text"] = "The registered comparison remains unresolved."
                elif mutation == "claim_ready_for_l2_l3":
                    evaluation[mutation] = value
                elif mutation == "role":
                    contrast["claim_role"] = value
                    row["claim_role"] = value
                elif mutation == "demotion":
                    contrast["sampling"]["confirmatory_status"] = value
                    row["caveat"] = "outcome_dependent_top_up"
                else:
                    evaluation["claim_level_ceiling"] = value
                artifact["claim_verdicts_id"] = canonical_verdict_id(artifact)
                write_fixture(root, artifact, row)
                self.assertIn(expected, error_codes(lint_fixture(root)))

    def test_refuted_requires_opposite_frozen_direction(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifact = base_artifact()
            artifact["contrasts"][0]["hypothesized_direction"] = "negative"
            artifact["claim_verdicts_id"] = canonical_verdict_id(artifact)
            row = base_row()
            row["editorial_status"] = "refuted"
            write_fixture(root, artifact, row)
            self.assertEqual(error_codes(lint_fixture(root)), set())

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            row = base_row()
            row["editorial_status"] = "refuted"
            write_fixture(root, base_artifact(), row)
            self.assertIn(
                "CLAIM_INDEX_REFUTED_WITHOUT_OPPOSITE_DIRECTION",
                error_codes(lint_fixture(root)),
            )

    def test_l3_refuted_must_pass_the_same_clean_linked_artifact_gates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifact = base_artifact()
            contrast = artifact["contrasts"][0]
            contrast["hypothesized_direction"] = "negative"
            contrast["claim_role"] = "exploratory"
            contrast["sampling"]["confirmatory_status"] = "demoted_exploratory"
            contrast["sensitivity_status"] = "concern"
            contrast["claim_evaluation"].update(
                claim_ready_for_l2_l3=False,
                claim_level_ceiling="L1",
            )
            artifact["claim_verdicts_id"] = canonical_verdict_id(artifact)
            row = base_row()
            row.update(
                ladder_level="L3",
                claim_role="exploratory",
                editorial_status="refuted",
                caveat="demoted exploratory sensitivity concern",
            )
            write_fixture(root, artifact, row)
            codes = error_codes(lint_fixture(root))
            self.assertTrue(
                {
                    "CLAIM_INDEX_SUPPORTED_NOT_CLAIM_READY",
                    "CLAIM_INDEX_SUPPORTED_EXPLORATORY",
                    "CLAIM_INDEX_SUPPORTED_DEMOTED",
                    "CLAIM_INDEX_SUPPORTED_ABOVE_CEILING",
                }.issubset(codes),
                codes,
            )

    def test_not_resolvable_status_and_exact_reasons_are_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifact = base_artifact()
            evaluation = artifact["contrasts"][0]["claim_evaluation"]
            evaluation.update(
                outcome="not_resolvable",
                direction=None,
                reason_codes=["effect_not_above_floor"],
                claim_ready_for_l2_l3=False,
                claim_level_ceiling="L1",
            )
            for loo_row in artifact["contrasts"][0]["loo"]["rows"]:
                loo_row["outcome"] = "not_resolvable"
            artifact["claim_verdicts_id"] = canonical_verdict_id(artifact)
            row = base_row()
            row.update(
                engine_outcome="not_resolvable",
                editorial_status="weak",
                claim_text="The registered comparison is not resolvable.",
                caveat="effect_not_above_floor",
            )
            write_fixture(root, artifact, row)
            self.assertEqual(error_codes(lint_fixture(root)), set())

            row["editorial_status"] = "supported"
            row["caveat"] = "prefix_effect_not_above_floor_suffix"
            write_fixture(root, artifact, row)
            codes = error_codes(lint_fixture(root))
            self.assertIn("CLAIM_INDEX_UNRESOLVABLE_STATUS_INVALID", codes)
            self.assertIn("CLAIM_INDEX_REASON_NOT_SURFACED", codes)

    def test_status_outcome_matrix_covers_all_five_engine_outcomes(self) -> None:
        cases = (
            ("not_estimable", "weak", False),
            ("not_estimable", "out-of-data", False),
            ("not_estimable", "supported", True),
            ("not_resolvable", "refuted", True),
            ("unresolved", "weak", False),
            ("unresolved", "refuted", True),
            ("direction_supported", "supported", False),
            ("equivalent", "supported", False),
        )
        for outcome, status, expect_error in cases:
            with (
                self.subTest(outcome=outcome, status=status),
                tempfile.TemporaryDirectory() as tmp,
            ):
                root = Path(tmp)
                artifact = base_artifact()
                evaluation = artifact["contrasts"][0]["claim_evaluation"]
                row = base_row()
                row["engine_outcome"] = outcome
                row["editorial_status"] = status
                if outcome in {"not_estimable", "not_resolvable"}:
                    evaluation.update(
                        outcome=outcome,
                        direction=None,
                        reason_codes=["metric_missing_or_nonfinite"],
                        claim_ready_for_l2_l3=False,
                        claim_level_ceiling="L1",
                    )
                    row["claim_text"] = "The registered comparison is not resolvable."
                    row["caveat"] = "metric_missing_or_nonfinite"
                elif outcome == "unresolved":
                    evaluation.update(
                        outcome=outcome,
                        direction=None,
                        reason_codes=["multiplicity_not_rejected"],
                        claim_ready_for_l2_l3=False,
                        claim_level_ceiling="L1",
                    )
                    row["claim_text"] = "The registered comparison remains unresolved."
                elif outcome == "equivalent":
                    evaluation.update(outcome=outcome, direction=None)
                    artifact["contrasts"][0]["equivalence"] = {
                        "margin": 2.0,
                        "method": "tost_v1",
                    }
                    artifact["contrasts"][0]["multiplicity"].update(
                        raw_p=0.0,
                        adjusted_p=0.0,
                        rejected=True,
                    )
                    artifact["families"][0]["adjusted_p_values"][
                        "ctr-fixture-b-minus-a"
                    ] = 0.0
                    row["claim_text"] = "The predeclared equivalence claim is supported."
                for loo_row in artifact["contrasts"][0]["loo"]["rows"]:
                    loo_row["outcome"] = outcome
                artifact["claim_verdicts_id"] = canonical_verdict_id(artifact)
                write_fixture(root, artifact, row)
                codes = error_codes(lint_fixture(root))
                self.assertEqual(bool(codes), expect_error, codes)

    def test_unresolved_rejects_supported_status_and_directional_prose(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifact = base_artifact()
            evaluation = artifact["contrasts"][0]["claim_evaluation"]
            evaluation.update(
                outcome="unresolved",
                direction=None,
                reason_codes=["multiplicity_not_rejected"],
                claim_ready_for_l2_l3=False,
            )
            artifact["claim_verdicts_id"] = canonical_verdict_id(artifact)
            row = base_row()
            row.update(
                engine_outcome="unresolved",
                editorial_status="supported",
                claim_text="Condition B is lower than condition A.",
            )
            write_fixture(root, artifact, row)
            codes = error_codes(lint_fixture(root))
            self.assertIn("CLAIM_INDEX_UNRESOLVED_SUPPORTED", codes)
            self.assertIn("CLAIM_INDEX_UNRESOLVED_DIRECTIONAL_PROSE", codes)

    def test_legacy_artifact_is_l0_l1_only_with_exact_caveat(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifact = base_artifact()
            artifact["inputs"]["evidence_class"] = "legacy_l1"
            artifact["inputs"]["limitations"] = ["legacy_l1_mechanics_only"]
            evaluation = artifact["contrasts"][0]["claim_evaluation"]
            evaluation["claim_ready_for_l2_l3"] = False
            evaluation["claim_level_ceiling"] = "L1"
            artifact["claim_verdicts_id"] = canonical_verdict_id(artifact)
            row = base_row()
            row["ladder_level"] = "L1"
            row["caveat"] = "legacy_l1_mechanics_only"
            write_fixture(root, artifact, row)
            self.assertEqual(error_codes(lint_fixture(root)), set())

            row["ladder_level"] = "L2"
            row["caveat"] = "Legacy mechanics only."
            write_fixture(root, artifact, row)
            codes = error_codes(lint_fixture(root))
            self.assertIn("CLAIM_INDEX_LEGACY_LEVEL_EXCEEDED", codes)
            self.assertIn("CLAIM_INDEX_LEGACY_CAVEAT_INVALID", codes)

    def test_caveat_is_required_for_lower_level_and_nonclean_sensitivity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            row = base_row()
            row["ladder_level"] = "L1"
            write_fixture(root, base_artifact(), row)
            self.assertIn("CLAIM_INDEX_CAVEAT_REQUIRED", error_codes(lint_fixture(root)))

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifact = base_artifact()
            artifact["contrasts"][0]["sensitivity_status"] = "concern"
            artifact["claim_verdicts_id"] = canonical_verdict_id(artifact)
            write_fixture(root, artifact, base_row())
            self.assertIn("CLAIM_INDEX_CAVEAT_REQUIRED", error_codes(lint_fixture(root)))

    def test_verdict_path_must_be_repo_relative_and_inside_declared_dir(self) -> None:
        for bad_path in ("../claim_verdicts.json", "/tmp/claim_verdicts.json"):
            with self.subTest(path=bad_path), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                row = base_row()
                row["verdict_artifact"] = bad_path
                write_fixture(root, base_artifact(), row)
                self.assertIn(
                    "CLAIM_INDEX_INVALID_VERDICT_PATH",
                    error_codes(lint_fixture(root)),
                )

    def test_verdict_path_symlink_loop_is_a_named_refusal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            analysis = root / "analysis"
            analysis.mkdir()
            (analysis / "loop.json").symlink_to("loop.json")
            row = base_row()
            row["verdict_artifact"] = "analysis/loop.json"
            (root / "claims_index.jsonl").write_text(
                json.dumps(row) + "\n", encoding="utf-8"
            )

            findings = lint_fixture(root)

        self.assertIn("CLAIM_INDEX_INVALID_VERDICT_PATH", error_codes(findings))

    def test_explicit_mode_fails_closed_when_index_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--mode",
                    "claim-index",
                    "--root",
                    tmp,
                    "--claims-index",
                    "missing.jsonl",
                    "--claim-verdict-dir",
                    "analysis",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, claims_lint.EXIT_USAGE_PARSE)
            self.assertIn("cannot read", result.stderr)


if __name__ == "__main__":
    unittest.main()
