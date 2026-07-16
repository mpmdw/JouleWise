from __future__ import annotations

import json
import argparse
import shutil
import tempfile
import unittest
from pathlib import Path

import joulewise.adapters as adapters
from joulewise.adapters.mock_spec_runtime import (
    MOCK_TARGET_TOKENIZER,
    MockSpecRuntimeAdapter,
    MockSpecScenario,
    MockSpecStep,
)
from joulewise.analysis_engine.registry import AnalysisManifestError
from joulewise.axi_decode_config import TargetTokenizerIdentity
from joulewise.cli import validate_bundle
from joulewise.clock import Clock, FakeClock
from joulewise.controller import run_benchmark
from joulewise.interfaces import AxiCancelledProposalCounters, RuntimeAdapter
from joulewise.output_identity import build_output_identity_report
from joulewise.schemas import BenchmarkConfig, RunStatus
from scripts.run_campaign import load_analysis_manifest, run_axi_spec_campaign


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "configs" / "examples" / "mock_axi_spec.json"
GOLDENS = ROOT / "tests" / "goldens"
B2_ROSTER = ROOT / "tests" / "fixtures" / "axi_mock_spec" / "request_roster_b2.json"
B2_ROSTER_SHA256 = "746b0743e81fd9d78f9598268da7f43c2906ba28776a7c4969518846979a1754"
MANIFEST_ID = "am-" + "a" * 64


def config_mapping(*, mode: str = "draft_model", run_id: str = "mock-axi-test") -> dict:
    value = json.loads(CONFIG_PATH.read_text())
    value["run_id"] = run_id
    if mode == "off":
        value["speculation"] = {
            "mode": "off",
            "max_proposed_tokens": None,
            "draft_model_identity": None,
            "native_mtp_identity": None,
        }
    elif mode == "native_mtp":
        value["speculation"] = json.loads(
            (ROOT / "tests" / "fixtures" / "axi_ap_spec" / "native_spec_on.json").read_text()
        )["speculation"]
    return value


def make_config(*, mode: str = "draft_model", run_id: str = "mock-axi-test") -> BenchmarkConfig:
    return BenchmarkConfig.from_mapping(config_mapping(mode=mode, run_id=run_id))


class MockSpecRegistry:
    def __init__(
        self,
        *,
        scenario: MockSpecScenario | None = None,
        target_tokenizer_identity: TargetTokenizerIdentity = MOCK_TARGET_TOKENIZER,
    ) -> None:
        self.scenario = scenario
        self.target_tokenizer_identity = target_tokenizer_identity

    def resolve_runtime(self, config: BenchmarkConfig, clock: Clock):
        return (
            MockSpecRuntimeAdapter(
                clock,
                scenario=self.scenario,
                target_tokenizer_identity=self.target_tokenizer_identity,
            ),
            None,
        )

    def resolve_telemetry(self, config: BenchmarkConfig, clock: Clock):
        return adapters.resolve_telemetry(config, clock)

    def resolve_transport(self, config: BenchmarkConfig):
        return adapters.resolve_transport(config)


class AxiMockSpecTests(unittest.TestCase):
    def assert_oracle_values(self, actual: object, expected: object) -> None:
        if isinstance(expected, dict):
            self.assertIsInstance(actual, dict)
            for key, value in expected.items():
                self.assertIn(key, actual)
                self.assert_oracle_values(actual[key], value)
            return
        if isinstance(expected, list):
            self.assertIsInstance(actual, list)
            self.assertEqual(len(actual), len(expected))
            for got, want in zip(actual, expected):
                self.assert_oracle_values(got, want)
            return
        if isinstance(expected, float):
            self.assertIsInstance(actual, (int, float))
            self.assertAlmostEqual(float(actual), expected, places=9)
            return
        self.assertEqual(actual, expected)

    def run_bundle(
        self,
        *,
        mode: str,
        run_id: str,
        scenario: MockSpecScenario | None = None,
        target_tokenizer_identity: TargetTokenizerIdentity = MOCK_TARGET_TOKENIZER,
    ) -> tuple[Path, object]:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        return run_benchmark(
            make_config(mode=mode, run_id=run_id),
            Path(temporary.name),
            FakeClock(start=1000.0),
            registry=MockSpecRegistry(
                scenario=scenario,
                target_tokenizer_identity=target_tokenizer_identity,
            ),
            environment_snapshot=None,
        )

    def test_mock_spec_adapter_is_explicitly_non_live_and_protocol_conformant(self) -> None:
        adapter = MockSpecRuntimeAdapter(FakeClock())
        self.assertIsInstance(adapter, RuntimeAdapter)
        prepared = adapter.prepare(make_config())
        self.assertEqual(
            prepared.metadata,
            {
                "adapter": "mock_spec_runtime",
                "evidence_level": "fixture_mock_non_live",
                "production_runtime_support": False,
            },
        )

    def test_default_spec_off_external_draft_and_native_mtp_are_separately_valid(self) -> None:
        expected = {
            "off": [(None, None, 2, (101, 102)), (None, None, 1, (103,))],
            "draft_model": [(2, 1, 1, (101, 102)), (1, 1, 0, (103,))],
            "native_mtp": [(2, 1, 1, (101, 102)), (1, 1, 0, (103,))],
        }
        for mode, oracle in expected.items():
            with self.subTest(mode=mode):
                result = MockSpecRuntimeAdapter(FakeClock(start=1000.0)).run_workload(
                    make_config(mode=mode)
                )
                request = result.axi_result.requests[0]
                self.assertEqual(
                    [
                        (
                            step.tokens_proposed,
                            step.tokens_accepted,
                            step.target_emitted_count,
                            step.emitted_token_ids,
                        )
                        for step in request.emissions
                    ],
                    oracle,
                )

    def test_parameterized_proposal_acceptance_target_id_and_timestamp_cases(self) -> None:
        cases = (
            (
                "enabled_zero_proposals",
                MockSpecStep(1, 0, 0, 1, (201,), (0.04,), 0.04),
                (0, 0, 1, (201,), (1000.04,)),
            ),
            (
                "proposal_without_acceptance",
                MockSpecStep(1, 2, 0, 1, (202,), (0.04,), 0.04),
                (2, 0, 1, (202,), (1000.04,)),
            ),
            (
                "mixed_acceptance_and_target_correction",
                MockSpecStep(2, 3, 1, 1, (203, 204), (0.04, 0.045), 0.04),
                (3, 1, 1, (203, 204), (1000.04, 1000.045)),
            ),
            (
                "burst_without_individual_timestamps",
                MockSpecStep(2, 2, 1, 1, (205, 206), (None, None), 0.04),
                (2, 1, 1, (205, 206), (None, None)),
            ),
            (
                "burst_with_genuine_individual_timestamps",
                MockSpecStep(2, 2, 1, 1, (207, 208), (0.041, 0.046), 0.04),
                (2, 1, 1, (207, 208), (1000.041, 1000.046)),
            ),
            (
                "token_ids_unavailable",
                MockSpecStep(2, 2, 1, 1, None, (0.041, 0.046), 0.04),
                (2, 1, 1, None, (1000.041, 1000.046)),
            ),
        )
        for name, step, oracle in cases:
            with self.subTest(name=name):
                scenario = MockSpecScenario(steps=(step,))
                result = MockSpecRuntimeAdapter(
                    FakeClock(start=1000.0), scenario=scenario
                ).run_workload(make_config())
                request = result.axi_result.requests[0]
                emission = request.emissions[0]
                actual = (
                    emission.tokens_proposed,
                    emission.tokens_accepted,
                    emission.target_emitted_count,
                    emission.emitted_token_ids,
                    tuple(token.timestamp_s for token in request.tokens),
                )
                for got, want in zip(actual[-1], oracle[-1]):
                    if want is None:
                        self.assertIsNone(got)
                    else:
                        self.assertAlmostEqual(got, want, places=9)
                self.assertEqual(actual[:-1], oracle[:-1])

    def test_static_batch_has_explicit_b_and_duplicate_synchronized_windows(self) -> None:
        value = config_mapping()
        value["batch_policy"] = {
            "mode": "static_batch",
            "requested_batch_size": 2,
            "admission_policy": "admit_roster_together",
            "synchronization_policy": "barrier_before_prefill",
            "dispatch_policy": "one_native_batch_call",
            "request_roster_ref": str(B2_ROSTER.relative_to(ROOT)),
            "request_roster_sha256": B2_ROSTER_SHA256,
        }
        config = BenchmarkConfig.from_mapping(value)
        result = MockSpecRuntimeAdapter(FakeClock(start=1000.0)).run_workload(config)
        axi = result.axi_result
        self.assertEqual(
            (
                axi.batch.realized_batch_size,
                axi.batch.submitted_request_count,
                axi.batch.admitted_request_count,
                axi.batch.terminal_request_count,
                axi.batch.batch_group_id,
            ),
            (2, 2, 2, 2, "mock-static-batch-000"),
        )
        self.assertEqual(axi.requests[0].phase_windows, axi.requests[1].phase_windows)

    def test_failed_cancelled_and_proposal_cancelled_terminals_retain_evidence(self) -> None:
        cases = (
            (
                MockSpecScenario(
                    (),
                    terminal_status="failed",
                    stop_reason=None,
                    failure_reason="mock_runtime_failed",
                    failure_message="deterministic mock failure",
                    response_text=None,
                ),
                "failed",
                None,
            ),
            (
                MockSpecScenario(
                    (),
                    terminal_status="cancelled",
                    stop_reason=None,
                    failure_reason="mock_cancelled",
                    failure_message="deterministic mock cancellation",
                    response_text=None,
                ),
                "cancelled",
                None,
            ),
            (
                MockSpecScenario(
                    (),
                    terminal_status="cancelled_after_proposal_before_output",
                    stop_reason=None,
                    failure_reason="mock_cancelled_after_proposal",
                    failure_message="deterministic proposal cancellation",
                    response_text=None,
                    cancelled_proposal_counters=AxiCancelledProposalCounters(3),
                ),
                "cancelled_after_proposal_before_output",
                3,
            ),
        )
        for scenario, status, retained in cases:
            with self.subTest(status=status):
                result = MockSpecRuntimeAdapter(
                    FakeClock(start=1000.0), scenario=scenario
                ).run_workload(make_config())
                request = result.axi_result.requests[0]
                self.assertEqual(request.terminal_status, status)
                self.assertEqual(request.failure_reason, scenario.failure_reason)
                self.assertEqual(request.terminal_at_s, 1000.09)
                if retained is None:
                    self.assertIsNone(request.cancelled_proposal_counters)
                else:
                    self.assertEqual(
                        request.cancelled_proposal_counters.tokens_proposed,
                        retained,
                    )

    def test_controller_mock_bundle_matches_independent_event_artifact_and_summary_goldens(self) -> None:
        bundle, summary = self.run_bundle(
            mode="draft_model", run_id="mock-axi-golden"
        )
        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        self.assertEqual(validate_bundle(bundle, strict=True), [])
        events = [json.loads(line) for line in (bundle / "events.jsonl").read_text().splitlines()]
        request_events = [row for row in events if "request_id" in row["metadata"]]
        event_bytes = "".join(
            json.dumps(row, separators=(",", ":"), sort_keys=True) + "\n"
            for row in request_events
        ).encode()
        self.assertEqual(
            event_bytes,
            (GOLDENS / "mock_axi_spec_request_events.jsonl").read_bytes(),
        )
        self.assertEqual(
            (bundle / "outputs" / "requests.jsonl").read_bytes(),
            (GOLDENS / "mock_axi_spec_requests.jsonl").read_bytes(),
        )
        self.assertEqual(
            (bundle / "outputs" / "request_tokens.jsonl").read_bytes(),
            (GOLDENS / "mock_axi_spec_request_tokens.jsonl").read_bytes(),
        )
        self.assert_oracle_values(
            json.loads((bundle / "summary_metrics.json").read_text()),
            json.loads((GOLDENS / "mock_axi_spec_summary_oracle.json").read_text()),
        )

    def test_mock_bundles_exercise_all_output_identity_states_and_dispositions(self) -> None:
        cases = (
            (None, "exact_token_match", "matched_decoded_work", []),
            (
                MockSpecScenario(
                    steps=(
                        MockSpecStep(2, 2, 1, 1, (201, 202), (0.04, 0.045), 0.04),
                        MockSpecStep(1, 1, 1, 0, (203,), (0.07,), 0.07),
                    )
                ),
                "text_match_token_divergent",
                "text_matched_descriptive_or_predeclared_quality_matched",
                ["token_ids_differ"],
            ),
            (
                MockSpecScenario(
                    steps=(
                        MockSpecStep(2, 2, 1, 1, (101, 102), (0.04, 0.045), 0.04),
                        MockSpecStep(1, 1, 1, 0, (103,), (0.07,), 0.07),
                    ),
                    response_text="different-mock-output",
                ),
                "output_divergent",
                "descriptive_only",
                ["response_text_differs"],
            ),
            (
                MockSpecScenario(
                    steps=(
                        MockSpecStep(2, 2, 1, 1, None, (0.04, 0.045), 0.04),
                        MockSpecStep(1, 1, 1, 0, None, (0.07,), 0.07),
                    )
                ),
                "unassessable",
                "refuse_efficiency_claim",
                ["token_ids_unavailable"],
            ),
        )
        for index, (scenario, state, disposition, reasons) in enumerate(cases):
            with self.subTest(state=state):
                paired_run_id = f"mock-report-pair-{index}"
                off, _ = self.run_bundle(mode="off", run_id=paired_run_id)
                on, _ = self.run_bundle(
                    mode="draft_model",
                    run_id=paired_run_id,
                    scenario=scenario,
                )
                report = build_output_identity_report(
                    manifest_id=MANIFEST_ID,
                    pair_id="pair-000",
                    spec_off_bundle=off,
                    spec_on_bundle=on,
                    strict_validator=validate_bundle,
                )
                self.assertEqual(report["overall_state"], state)
                self.assertEqual(report["claim_disposition"], disposition)
                self.assertEqual(report["requests"][0]["reason_codes"], reasons)

    def test_mock_target_tokenizer_exact_mismatch_and_unassessable_cases(self) -> None:
        paired_run_id = "mock-tokenizer-pair"
        off, _ = self.run_bundle(mode="off", run_id=paired_run_id)
        exact, _ = self.run_bundle(mode="draft_model", run_id=paired_run_id)
        mismatch_identity = TargetTokenizerIdentity(
            name=MOCK_TARGET_TOKENIZER.name,
            revision="fixture-v2-other",
            tokenizer_artifact_sha256=MOCK_TARGET_TOKENIZER.tokenizer_artifact_sha256,
        )
        mismatch, _ = self.run_bundle(
            mode="draft_model",
            run_id=paired_run_id,
            target_tokenizer_identity=mismatch_identity,
        )
        exact_report = build_output_identity_report(
            manifest_id=MANIFEST_ID,
            pair_id="pair-000",
            spec_off_bundle=off,
            spec_on_bundle=exact,
            strict_validator=validate_bundle,
        )
        mismatch_report = build_output_identity_report(
            manifest_id=MANIFEST_ID,
            pair_id="pair-000",
            spec_off_bundle=off,
            spec_on_bundle=mismatch,
            strict_validator=validate_bundle,
        )
        self.assertEqual(exact_report["target_tokenizer_comparison"], "exact_match")
        self.assertEqual(mismatch_report["target_tokenizer_comparison"], "mismatch")
        self.assertEqual(mismatch_report["overall_state"], "unassessable")

        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        malformed = Path(temporary.name) / "bundle"
        shutil.copytree(exact, malformed)
        metadata = json.loads((malformed / "metadata.json").read_text())
        del metadata["runtime"]["target_tokenizer_identity"]
        (malformed / "metadata.json").write_text(
            json.dumps(metadata, indent=2, sort_keys=True) + "\n"
        )
        missing_report = build_output_identity_report(
            manifest_id=MANIFEST_ID,
            pair_id="pair-000",
            spec_off_bundle=off,
            spec_on_bundle=malformed,
            strict_validator=validate_bundle,
        )
        self.assertEqual(missing_report["target_tokenizer_comparison"], "unassessable")
        self.assertIn(
            "target_tokenizer_identity_unavailable",
            missing_report["spec_on_bundle"]["missing_evidence_reasons"],
        )

    def test_missing_mock_report_inputs_have_frozen_missing_evidence_reasons(self) -> None:
        report = build_output_identity_report(
            manifest_id=MANIFEST_ID,
            pair_id="pair-000",
            spec_off_bundle=None,
            spec_on_bundle=None,
            strict_validator=validate_bundle,
        )
        oracle = [
            "config_sha256_unavailable",
            "request_tokens_artifact_unavailable",
            "requests_artifact_unavailable",
            "run_id_unavailable",
            "strict_validation_report_unavailable",
            "summary_artifact_unavailable",
            "target_tokenizer_identity_unavailable",
        ]
        self.assertEqual(report["spec_off_bundle"]["missing_evidence_reasons"], oracle)
        self.assertEqual(report["spec_on_bundle"]["missing_evidence_reasons"], oracle)
        self.assertEqual(report["overall_state"], "unassessable")
        self.assertEqual(report["claim_disposition"], "refuse_efficiency_claim")

    def test_v2_campaign_writes_complete_immutable_ledger_and_pair_reports(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        state = load_analysis_manifest(ROOT / "tests" / "fixtures" / "axi_ap_spec")
        self.assertIsNotNone(state)
        self.assertTrue(state.valid)
        args = argparse.Namespace(dry_run=False, cli_cmd=None)
        self.assertEqual(
            run_axi_spec_campaign(args, state, runs_dir=Path(temporary.name)),
            0,
        )
        evidence = Path(temporary.name) / "axi_attempt_evidence" / state.manifest_id
        ledger = evidence / "attempt_ledger.jsonl"
        first_bytes = ledger.read_bytes()
        rows = [json.loads(line) for line in first_bytes.splitlines()]
        self.assertEqual(len(rows), 4)
        self.assertTrue(all(row["eligible_for_analysis"] for row in rows))
        self.assertEqual(
            [row["attempt_ordinal"] for row in rows],
            [0, 0, 0, 0],
        )
        reports = sorted((evidence / "output_identity_reports").glob("*.json"))
        self.assertEqual(len(reports), 2)
        self.assertEqual(
            [json.loads(path.read_text())["overall_state"] for path in reports],
            ["exact_token_match", "exact_token_match"],
        )
        self.assertEqual(
            run_axi_spec_campaign(args, state, runs_dir=Path(temporary.name)),
            0,
        )
        self.assertEqual(ledger.read_bytes(), first_bytes)
        self.assertEqual(len(list((evidence / "dispatch_receipts").glob("*.json"))), 4)

    def test_v2_campaign_refuses_eligible_receipt_after_bundle_store_deletion(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        state = load_analysis_manifest(ROOT / "tests" / "fixtures" / "axi_ap_spec")
        self.assertIsNotNone(state)
        self.assertTrue(state.valid)
        args = argparse.Namespace(dry_run=False, cli_cmd=None)
        runs_dir = Path(temporary.name)
        self.assertEqual(run_axi_spec_campaign(args, state, runs_dir=runs_dir), 0)

        bundle_root = runs_dir / "axi_attempt_bundles" / state.manifest_id
        deleted_bundle = next(bundle_root.rglob("summary_metrics.json")).parent
        shutil.rmtree(deleted_bundle)
        with self.assertRaises(AnalysisManifestError) as raised:
            run_axi_spec_campaign(args, state, runs_dir=runs_dir)
        self.assertEqual(raised.exception.code, "analysis_attempt_ledger_gap")
        self.assertIn("finalized run coverage", raised.exception.detail)


if __name__ == "__main__":
    unittest.main()
