from __future__ import annotations

import json
import argparse
import sys
import tempfile
import unittest
from pathlib import Path

import joulewise.adapters as adapters
from joulewise.axi_decode_config import TargetTokenizerIdentity
from joulewise.clock import Clock, FakeClock
from joulewise.controller import finalize_dispatch_receipt, run_benchmark
from joulewise.interfaces import (
    AdapterResult,
    AttemptIdentity,
    AxiBatchObservation,
    AxiCancelledProposalCounters,
    AxiDecodeEmission,
    AxiPhaseWindow,
    AxiRequestResult,
    AxiRequestToken,
    AxiRuntimeResult,
    RuntimeResult,
)
from joulewise.schemas import BenchmarkConfig, RunStatus, SummaryMetricsV060
from scripts.run_campaign import (
    _axi_strict_reason_codes,
    load_analysis_manifest,
    run_axi_spec_campaign,
)


ROOT = Path(__file__).resolve().parents[1]
AXI_CONFIGS = ROOT / "tests" / "fixtures" / "axi_ap_spec"
GOLDENS = ROOT / "tests" / "goldens"


def load_config(name: str, run_id: str) -> BenchmarkConfig:
    value = json.loads((AXI_CONFIGS / name).read_text())
    value["run_id"] = run_id
    return BenchmarkConfig.from_mapping(value)


class FakeAxiRuntime:
    name = "fake-axi-runtime"

    def __init__(self, clock: Clock, *, cancelled: bool = False) -> None:
        self.clock = clock
        self.cancelled = cancelled

    def prepare(self, config: BenchmarkConfig, context=None) -> AdapterResult:
        return AdapterResult(ok=True, metadata={"fake_axi": True})

    def warmup(self, config: BenchmarkConfig, context=None) -> AdapterResult:
        return AdapterResult(ok=True)

    def cleanup(self, config: BenchmarkConfig, context=None) -> AdapterResult:
        return AdapterResult(ok=True)

    def run_workload(self, config: BenchmarkConfig, context=None) -> RuntimeResult:
        start = self.clock.now()
        off = config.speculation.mode == "off"
        if self.cancelled:
            phases: tuple[AxiPhaseWindow, ...] = ()
            emissions: tuple[AxiDecodeEmission, ...] = ()
            tokens: tuple[AxiRequestToken, ...] = ()
            terminal_status = "cancelled_after_proposal_before_output"
            stop_reason = None
            failure_reason = "cancelled_by_fake_runtime"
            failure_message = "deterministic cancellation"
            response_text = ""
            cancelled = AxiCancelledProposalCounters(tokens_proposed=2)
            terminal_at = start + 0.4
        else:
            phases = (
                AxiPhaseWindow("prefill", 0, start + 0.1, start + 0.6),
                AxiPhaseWindow("decode", 1, start + 0.8, start + 1.8),
            )
            emissions = (
                AxiDecodeEmission(
                    start + 1.0, 0, 0, 2,
                    None if off else 2,
                    None if off else 1,
                    2 if off else 1,
                    (10, 11),
                    "step-000",
                ),
                AxiDecodeEmission(
                    start + 1.5, 1, 2, 1,
                    None if off else 2,
                    None if off else 1,
                    1 if off else 0,
                    (12,),
                    "step-001",
                ),
            )
            tokens = (
                AxiRequestToken(0, 0, 10, start + 1.0, "runtime_per_token_callback"),
                AxiRequestToken(1, 0, 11, start + 1.1, "runtime_per_token_callback"),
                AxiRequestToken(2, 1, 12, start + 1.5, "runtime_per_token_callback"),
            )
            terminal_status = "succeeded"
            stop_reason = "requested_tokens_emitted"
            failure_reason = None
            failure_message = None
            response_text = "abc"
            cancelled = None
            terminal_at = start + 1.9
        request = AxiRequestResult(
            request_id="request-000",
            request_ordinal=0,
            request_input_id="prompt-000",
            submitted_at_s=start + 0.01,
            admitted_at_s=start + 0.02,
            phase_windows=phases,
            emissions=emissions,
            tokens=tokens,
            terminal_at_s=terminal_at,
            terminal_status=terminal_status,
            stop_reason=stop_reason,
            failure_reason=failure_reason,
            failure_message=failure_message,
            response_text=response_text,
            cancelled_proposal_counters=cancelled,
        )
        self.clock.sleep(2.0)
        axi = AxiRuntimeResult(
            requests=(request,),
            batch=AxiBatchObservation(1, 1, 1, 1, None),
            primary_source_identity="mock",
            target_model_artifact_sha256="a" * 64,
            target_tokenizer_identity=TargetTokenizerIdentity(
                name="runtime-observed-target-tokenizer",
                revision="resolved-runtime-revision",
                tokenizer_artifact_sha256="8dc5387f3f8554f444390c99cc4655cd40c8d1f757bc1a0fdce67d463287457b",
            ),
            target_tokenizer_artifact_files={
                "tokenizer.json": "ccf256f856ff12cc59897db26865cc8da53c8f32e4355289598e7693d3eb9137"
            },
        )
        return RuntimeResult(
            events=[],
            token_count=3,
            output_token_count=len(tokens),
            axi_result=axi,
        )


class FakeAxiRegistry:
    def __init__(self, *, cancelled: bool = False) -> None:
        self.cancelled = cancelled

    def resolve_runtime(self, config: BenchmarkConfig, clock: Clock):
        return FakeAxiRuntime(clock, cancelled=self.cancelled), None

    def resolve_telemetry(self, config: BenchmarkConfig, clock: Clock):
        return adapters.resolve_telemetry(config, clock)

    def resolve_transport(self, config: BenchmarkConfig):
        return adapters.resolve_transport(config)


class AxiControllerEventTests(unittest.TestCase):
    def run_axi(self, config_name: str, *, cancelled: bool = False):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        config = load_config(config_name, f"axi-controller-{'cancel' if cancelled else config_name[:-5]}")
        return run_benchmark(
            config,
            Path(temporary.name),
            FakeClock(start=1000.0),
            registry=FakeAxiRegistry(cancelled=cancelled),
            environment_snapshot=None,
        )

    def test_spec_on_controller_emits_request_events_and_artifacts(self) -> None:
        bundle, summary = self.run_axi("draft_spec_on.json")
        self.assertIsInstance(summary, SummaryMetricsV060)
        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        events = [json.loads(line) for line in (bundle / "events.jsonl").read_text().splitlines()]
        request_events = [row for row in events if "request_id" in row["metadata"]]
        self.assertEqual(
            [row["metadata"]["request_event_ordinal"] for row in request_events],
            list(range(len(request_events))),
        )
        emissions = [row for row in request_events if row["event_type"] == "decode_emission"]
        self.assertEqual(len(emissions), 2)
        self.assertTrue(all(isinstance(row["metadata"]["request_id"], str) for row in emissions))
        self.assertTrue(all(not isinstance(row["metadata"]["request_id"], list) for row in emissions))
        self.assertEqual(
            (bundle / "outputs" / "requests.jsonl").read_bytes(),
            (GOLDENS / "axi_controller_requests.jsonl").read_bytes(),
        )
        self.assertEqual(
            (bundle / "outputs" / "request_tokens.jsonl").read_bytes(),
            (GOLDENS / "axi_controller_request_tokens.jsonl").read_bytes(),
        )
        request_event_bytes = "".join(
            json.dumps(row, separators=(",", ":"), sort_keys=True) + "\n"
            for row in request_events
        ).encode()
        self.assertEqual(
            request_event_bytes,
            (GOLDENS / "axi_controller_request_events.jsonl").read_bytes(),
        )

        metadata = json.loads((bundle / "metadata.json").read_text())
        self.assertEqual(metadata["batch"]["realized_batch_size"], 1)
        self.assertEqual(metadata["batch"]["submitted_request_count"], 1)
        self.assertEqual(
            metadata["runtime"]["target_tokenizer_identity"]["name"],
            "runtime-observed-target-tokenizer",
        )
        self.assertEqual(
            metadata["runtime"]["target_tokenizer_identity"]["revision"],
            "resolved-runtime-revision",
        )

    def test_spec_off_and_on_use_the_same_v2_event_shapes(self) -> None:
        off_bundle, _ = self.run_axi("draft_spec_off.json")
        on_bundle, _ = self.run_axi("draft_spec_on.json")
        def shapes(bundle: Path):
            rows = [json.loads(line) for line in (bundle / "events.jsonl").read_text().splitlines()]
            return [
                (row["event_type"], set(row), set(row["metadata"]))
                for row in rows
                if "request_id" in row["metadata"]
            ]
        self.assertEqual(shapes(off_bundle), shapes(on_bundle))
        off = [json.loads(line) for line in (off_bundle / "events.jsonl").read_text().splitlines()]
        for row in off:
            if row["event_type"] == "decode_emission":
                self.assertIsNone(row["metadata"]["tokens_proposed"])
                self.assertIsNone(row["metadata"]["tokens_accepted"])

    def test_cancelled_terminal_survives_structured_runtime_failure(self) -> None:
        bundle, summary = self.run_axi("draft_spec_on.json", cancelled=True)
        self.assertEqual(summary.status, RunStatus.FAILED)
        events = [json.loads(line) for line in (bundle / "events.jsonl").read_text().splitlines()]
        terminal = next(row for row in events if row["event_type"] == "request_terminal")
        self.assertEqual(
            terminal["metadata"]["terminal_status"],
            "cancelled_after_proposal_before_output",
        )
        self.assertEqual(
            terminal["metadata"]["cancelled_proposal_counters"]["tokens_proposed"],
            2,
        )
        self.assertTrue((bundle / "summary_metrics.json").is_file())

    def test_dispatch_receipts_are_identity_bound_and_immutable_even_without_bundle(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        path = Path(temporary.name) / "receipts" / "draft-off-000__a0.json"
        identity = AttemptIdentity(
            manifest_id="am-" + "a" * 64,
            entry_id="draft-off-000",
            pair_id="pair-000",
            arm="spec_off",
            attempt_ordinal=0,
        )
        finalize_dispatch_receipt(
            path,
            identity,
            dispatch_started=True,
            transport_status="failed",
            process_exit_code=17,
            admitted_request_count=0,
            finalized_run_id=None,
        )
        receipt = json.loads(path.read_text())
        self.assertEqual(
            {key: receipt[key] for key in ("manifest_id", "entry_id", "pair_id", "arm", "attempt_ordinal")},
            {
                "manifest_id": identity.manifest_id,
                "entry_id": identity.entry_id,
                "pair_id": identity.pair_id,
                "arm": identity.arm,
                "attempt_ordinal": identity.attempt_ordinal,
            },
        )
        self.assertIsNone(receipt["finalized_run_id"])
        with self.assertRaises(FileExistsError):
            finalize_dispatch_receipt(
                path,
                identity,
                dispatch_started=True,
                transport_status="ok",
                process_exit_code=0,
                admitted_request_count=1,
                finalized_run_id="favorable-later-run",
            )

    def test_campaign_prebundle_process_failure_retains_identity_receipt_and_row(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        state = load_analysis_manifest(AXI_CONFIGS)
        self.assertIsNotNone(state)
        self.assertTrue(state.valid)
        result = run_axi_spec_campaign(
            argparse.Namespace(
                dry_run=False,
                cli_cmd="/definitely/missing/joulewise",
            ),
            state,
            runs_dir=Path(temporary.name),
        )
        self.assertEqual(result, 1)
        evidence = Path(temporary.name) / "axi_attempt_evidence" / state.manifest_id
        identities = list((evidence / "attempt_identities").glob("*.json"))
        receipts = list((evidence / "dispatch_receipts").glob("*.json"))
        rows = list((evidence / "ledger_rows").glob("*.jsonl"))
        self.assertEqual((len(identities), len(receipts), len(rows)), (1, 1, 1))
        identity = json.loads(identities[0].read_text())
        receipt = json.loads(receipts[0].read_text())
        row = json.loads(rows[0].read_text())
        self.assertEqual(
            {key: receipt[key] for key in identity},
            identity,
        )
        self.assertTrue(receipt["dispatch_started"])
        self.assertEqual(receipt["transport_status"], "failed")
        self.assertEqual(receipt["admitted_request_count"], 0)
        self.assertIsNone(receipt["finalized_run_id"])
        self.assertEqual(
            row["technical_invalid_reason_code"],
            "dispatch_failed_before_bundle_creation",
        )
        self.assertFalse(row["eligible_for_analysis"])

    def test_campaign_projects_diagnostics_to_frozen_validator_reason_enum(self) -> None:
        self.assertEqual(
            _axi_strict_reason_codes(
                [
                    "config.json generic structural diagnostic",
                    "axi:request_output_count_mismatch: realized count differs",
                    "axi:request_output_count_mismatch: duplicate detail",
                ]
            ),
            ["request_output_count_mismatch"],
        )
        with self.assertRaisesRegex(ValueError, "AXI_VALIDATOR_REASON_CODES"):
            _axi_strict_reason_codes(["arbitrary diagnostic sentence"])

    def test_campaign_zero_exit_without_finalized_bundle_is_dispatch_failure(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        state = load_analysis_manifest(AXI_CONFIGS)
        self.assertIsNotNone(state)
        self.assertTrue(state.valid)
        result = run_axi_spec_campaign(
            argparse.Namespace(
                dry_run=False,
                cli_cmd=f"{sys.executable} -c pass",
            ),
            state,
            runs_dir=Path(temporary.name),
        )
        self.assertEqual(result, 1)
        evidence = (
            Path(temporary.name)
            / "axi_attempt_evidence"
            / state.manifest_id
        )
        receipt = json.loads(
            next((evidence / "dispatch_receipts").glob("*.json")).read_text()
        )
        row = json.loads(
            next((evidence / "ledger_rows").glob("*.jsonl")).read_text()
        )
        self.assertEqual(receipt["process_exit_code"], 0)
        self.assertEqual(receipt["transport_status"], "failed")
        self.assertIsNone(receipt["finalized_run_id"])
        self.assertEqual(
            row["technical_invalid_reason_code"],
            "dispatch_failed_before_bundle_creation",
        )
        self.assertFalse(row["eligible_for_analysis"])


if __name__ == "__main__":
    unittest.main()
