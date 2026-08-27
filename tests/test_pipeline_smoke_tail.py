from __future__ import annotations

import copy
import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from joulewise.analysis_engine import analyze_claims
from joulewise.analysis_engine.reason_kinds import (
    CONTRACT_REASON_CODES,
    assert_data_reason_only,
)
from joulewise.analysis_manifest_v3 import (
    analysis_semantics_sha256_v1,
    calculate_manifest_id,
    render_manifest,
)
from scripts.finalize_analysis_manifest import main as finalize_main
from tests.test_analysis_finalizer import install_synthetic_finalization_fixture
from tests.test_analysis_integration import (
    CLEAN_SOURCE_STATE,
    prepared_minted_consumption_session,
)


def _finalizer_argv(fixture: dict) -> list[str]:
    return [
        "--prospective-manifest",
        str(fixture["prospective_path"]),
        "--plan-tree",
        str(fixture["plan_tree_path"]),
        "--custody-root",
        str(fixture["root"]),
        "--runs-root",
        str(fixture["runs_root"]),
        "--whole-window-verdict",
        str(fixture["verdict_path"]),
        "--bracket-binding",
        str(fixture["bracket_path"]),
        "--calibration-ledger",
        str(fixture["ledger_path"]),
        "--aggregate-floor-artifact",
        str(fixture["floor_path"]),
        "--output-dir",
        str(fixture["root"]),
    ]


def _run_finalizer(fixture: dict) -> tuple[int, dict, str]:
    stdout = io.StringIO()
    with redirect_stdout(stdout):
        exit_code = finalize_main(_finalizer_argv(fixture))
    raw = stdout.getvalue()
    lines = raw.splitlines()
    if len(lines) != 1:
        raise AssertionError(f"finalizer must emit one JSON line, got {lines!r}")
    return exit_code, json.loads(lines[0]), raw


def _rewrite_prospective(fixture: dict, mutate) -> None:
    candidate = copy.deepcopy(fixture["prospective"])
    mutate(candidate)
    if "families" in candidate:
        candidate["frozen_semantics_sha256"] = analysis_semantics_sha256_v1(
            candidate
        )
        candidate["manifest_id"] = calculate_manifest_id(candidate)
    raw = render_manifest(candidate)
    fixture["prospective_path"].write_bytes(raw)
    plan_tree = json.loads(fixture["plan_tree_path"].read_text())
    plan_tree["downstream_contract"]["analysis_manifest_sha256"] = hashlib.sha256(
        raw
    ).hexdigest()
    fixture["plan_tree_path"].write_text(json.dumps(plan_tree, indent=2) + "\n")


class PipelineSmokeTailTests(unittest.TestCase):
    def setUp(self) -> None:
        source_patch = mock.patch(
            "joulewise.bundle._capture_source_state",
            return_value=dict(CLEAN_SOURCE_STATE),
        )
        source_patch.start()
        self.addCleanup(source_patch.stop)
        session_patch = mock.patch(
            "joulewise.analysis_engine.inputs.AuthenticatedConsumptionSession",
            side_effect=prepared_minted_consumption_session,
        )
        session_patch.start()
        self.addCleanup(session_patch.stop)

    def test_mock_config_tail_pending_data_only_ruling(self) -> None:
        """Exercise the real tail and retain the fail-closed mock contradiction."""

        with tempfile.TemporaryDirectory() as tmp:
            fixture = install_synthetic_finalization_fixture(
                Path(tmp),
                shared_family=True,
                runtime_backend="mock",
                telemetry_backend="mock",
            )
            family = fixture["prospective"]["families"][0]
            self.assertEqual(
                family["multiplicity"],
                {"method": "holm", "alpha": 0.05, "q": None, "m": 2},
            )
            self.assertEqual(
                family["contrast_ids"],
                [
                    contrast["contrast_id"]
                    for contrast in fixture["prospective"]["contrasts"]
                ],
            )
            first_member = fixture["prospective"]["contrasts"][0]["members"][0]
            source_config = json.loads(
                (fixture["prospective_path"].parent / first_member["config"]).read_text()
            )
            self.assertEqual(
                source_config["hardware_target"]["runtime_backend"], "mock"
            )
            self.assertEqual(
                source_config["hardware_target"]["telemetry_backend"], "mock"
            )

            code, result, _raw = _run_finalizer(fixture)
            self.assertEqual(code, 0)
            self.assertEqual(result["status"], "FINALIZED")
            finalized_path = Path(result["output"])
            self.assertTrue(finalized_path.is_file())
            artifact = analyze_claims(
                finalized_path,
                fixture["runs_root"],
                fixture["floor_path"],
                strict_validator=lambda path, strict=True: [],
            )
            for contrast in artifact["contrasts"]:
                reasons = contrast["claim_evaluation"]["reason_codes"]
                self.assertEqual(
                    reasons.count("mock_telemetry_claim_ineligible"),
                    1,
                    contrast["contrast_id"],
                )
                self.assertTrue(
                    set(reasons) & CONTRACT_REASON_CODES,
                    contrast["contrast_id"],
                )
            with self.assertRaisesRegex(
                AssertionError,
                "contrast .* emitted non-DATA reason code",
            ):
                assert_data_reason_only(artifact)
            self.skipTest(
                "NEEDS-RULING: config-authenticated mock telemetry is excluded "
                "by the production claim loader, so the existing canned fixture "
                "cannot satisfy D-158's DATA-only predicate without loosening a "
                "production gate or building a new corpus fixture"
            )

    def _assert_prospective_refusal(self, mutate, detail_fragment: str) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = install_synthetic_finalization_fixture(
                Path(tmp), shared_family=True
            )
            _rewrite_prospective(fixture, mutate)
            code, refusal, _raw = _run_finalizer(fixture)
            self.assertEqual(code, 2)
            self.assertEqual(refusal["status"], "REFUSE")
            self.assertEqual(
                refusal["reason"],
                "analysis_finalization_prospective_invalid",
            )
            self.assertIn(detail_fragment, refusal["detail"])
            finalized = list(fixture["root"].glob("*.finalized.json"))
            self.assertEqual(finalized, [])

    def test_mutation_m_one_for_two_contrasts_refuses_in_finalization(self) -> None:
        self._assert_prospective_refusal(
            lambda value: value["families"][0]["multiplicity"].__setitem__(
                "m", 1
            ),
            "analysis_prospective_multiplicity_invalid: "
            "manifest.families[0].multiplicity is incompatible with the "
            "production adjustment method",
        )

    def test_mutation_prefill_empty_slot_refuses_in_finalization(self) -> None:
        self._assert_prospective_refusal(
            lambda value: value["contrasts"][1].__setitem__("test", "EMPTY"),
            "analysis_prospective_unresolved_slot: "
            "manifest contains an EMPTY/TODO placeholder",
        )

    def test_mutation_missing_families_refuses_in_finalization(self) -> None:
        self._assert_prospective_refusal(
            lambda value: value.pop("families"),
            "analysis_prospective_schema_invalid: manifest: missing key(s): families",
        )


if __name__ == "__main__":
    unittest.main()
