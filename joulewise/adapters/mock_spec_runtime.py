"""Deterministic non-live AXI speculative-decode fixture adapter.

This adapter exists only to exercise the frozen AXI-SA bundle contract.  It
does not name or claim support for a production runtime.  All observations are
derived from an injected clock and explicit :class:`MockSpecScenario` values.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from joulewise.axi_decode_config import (
    AXI_CONFIG_EXTENSION,
    RequestRoster,
    TargetTokenizerIdentity,
    canonical_json_bytes,
    sha256_bytes,
)
from joulewise.clock import Clock
from joulewise.interfaces import (
    AdapterResult,
    AxiBatchObservation,
    AxiCancelledProposalCounters,
    AxiDecodeEmission,
    AxiPhaseWindow,
    AxiRequestResult,
    AxiRequestToken,
    AxiRuntimeResult,
    RunContext,
    RuntimeResult,
)
from joulewise.schemas import BenchmarkConfig


# Source identity binds request windows to the mock telemetry ``source`` rows.
# Non-live status is carried separately in adapter metadata and config tags.
MOCK_SPEC_SOURCE_IDENTITY = "mock"
MOCK_TARGET_MODEL_SHA256 = "a" * 64
MOCK_TOKENIZER_FILES = {
    "tokenizer.json": "ccf256f856ff12cc59897db26865cc8da53c8f32e4355289598e7693d3eb9137"
}


def _tokenizer_artifact_sha256(files: dict[str, str]) -> str:
    return sha256_bytes(
        b"joulewise.tokenizer_artifact_identity.v1\0"
        + canonical_json_bytes(files)
    )


MOCK_TARGET_TOKENIZER = TargetTokenizerIdentity(
    name="joulewise-mock-spec-tokenizer",
    revision="fixture-v1",
    tokenizer_artifact_sha256=_tokenizer_artifact_sha256(MOCK_TOKENIZER_FILES),
)


@dataclass(frozen=True)
class MockSpecStep:
    """One independently parameterized mock decode emission."""

    emitted_count: int
    tokens_proposed: int | None
    tokens_accepted: int | None
    target_emitted_count: int
    token_ids: tuple[int, ...] | None
    token_timestamp_offsets_s: tuple[float | None, ...]
    emission_offset_s: float

    def __post_init__(self) -> None:
        if self.emitted_count < 1:
            raise ValueError("mock spec emitted_count must be >= 1")
        if len(self.token_timestamp_offsets_s) != self.emitted_count:
            raise ValueError("mock spec token timestamp count must equal emitted_count")
        if self.token_ids is not None and len(self.token_ids) != self.emitted_count:
            raise ValueError("mock spec token ID count must equal emitted_count")


@dataclass(frozen=True)
class MockSpecScenario:
    """Request behavior replicated across the configured deterministic roster."""

    steps: tuple[MockSpecStep, ...]
    terminal_status: str = "succeeded"
    stop_reason: str | None = "requested_tokens_emitted"
    failure_reason: str | None = None
    failure_message: str | None = None
    response_text: str | None = "mock-spec-output"
    cancelled_proposal_counters: AxiCancelledProposalCounters | None = None
    terminal_offset_s: float = 0.09

    def __post_init__(self) -> None:
        allowed = {
            "succeeded",
            "failed",
            "cancelled",
            "cancelled_after_proposal_before_output",
        }
        if self.terminal_status not in allowed:
            raise ValueError("mock spec terminal status is invalid")
        if self.terminal_status == "succeeded":
            if self.failure_reason is not None or self.failure_message is not None:
                raise ValueError("successful mock scenario cannot carry failure evidence")
        elif not self.failure_reason:
            raise ValueError("non-success mock scenario requires failure_reason")
        if self.terminal_status == "cancelled_after_proposal_before_output":
            if self.steps or self.cancelled_proposal_counters is None:
                raise ValueError("proposal cancellation requires counters and no emissions")
        elif self.cancelled_proposal_counters is not None:
            raise ValueError("cancelled proposal counters require proposal-cancellation terminal")


def default_mock_spec_scenario(config: BenchmarkConfig) -> MockSpecScenario:
    """Return the canonical three-token mock scenario for a config arm."""

    if config.speculation is None:
        raise ValueError("mock spec scenario requires AXI speculation policy")
    if config.speculation.mode == "off":
        steps = (
            MockSpecStep(2, None, None, 2, (101, 102), (0.04, 0.045), 0.04),
            MockSpecStep(1, None, None, 1, (103,), (0.07,), 0.07),
        )
    else:
        steps = (
            MockSpecStep(2, 2, 1, 1, (101, 102), (0.04, 0.045), 0.04),
            MockSpecStep(1, 1, 1, 0, (103,), (0.07,), 0.07),
        )
    return MockSpecScenario(steps=steps)


class MockSpecRuntimeAdapter:
    """Clock-driven AXI fixture producer with no live-support claim."""

    name = "mock-spec-fixture-non-live"

    def __init__(
        self,
        clock: Clock,
        *,
        scenario: MockSpecScenario | None = None,
        target_tokenizer_identity: TargetTokenizerIdentity = MOCK_TARGET_TOKENIZER,
        target_tokenizer_artifact_files: dict[str, str] | None = None,
    ) -> None:
        self._clock = clock
        self._scenario = scenario
        self._target_tokenizer_identity = target_tokenizer_identity
        self._target_tokenizer_artifact_files = dict(
            MOCK_TOKENIZER_FILES
            if target_tokenizer_artifact_files is None
            else target_tokenizer_artifact_files
        )

    def prepare(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> AdapterResult:
        self._require_axi(config)
        return AdapterResult(
            ok=True,
            metadata={
                "adapter": "mock_spec_runtime",
                "evidence_level": "fixture_mock_non_live",
                "production_runtime_support": False,
            },
        )

    def warmup(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> AdapterResult:
        self._require_axi(config)
        self._clock.sleep(0.01)
        return AdapterResult(ok=True)

    def cleanup(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> AdapterResult:
        return AdapterResult(ok=True)

    def run_workload(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> RuntimeResult:
        self._require_axi(config)
        policy = config.batch_policy
        speculation = config.speculation
        assert policy is not None and speculation is not None
        roster = self._load_roster(policy.request_roster_ref, policy.request_roster_sha256)
        if len(roster.requests) != policy.requested_batch_size:
            raise ValueError("mock spec roster count must equal configured batch size")

        scenario = self._scenario or default_mock_spec_scenario(config)
        self._validate_scenario_for_policy(scenario, config)
        start = self._clock.now()
        batch_group_id = (
            "mock-static-batch-000" if policy.mode == "static_batch" else None
        )
        requests = tuple(
            self._request_result(
                descriptor.request_ordinal,
                descriptor.request_input_id,
                start,
                scenario,
            )
            for descriptor in roster.requests
        )
        self._clock.sleep(scenario.terminal_offset_s + 0.01)
        output_count = sum(len(request.tokens) for request in requests)
        axi = AxiRuntimeResult(
            requests=requests,
            batch=AxiBatchObservation(
                realized_batch_size=len(requests),
                submitted_request_count=len(requests),
                admitted_request_count=len(requests),
                terminal_request_count=len(requests),
                batch_group_id=batch_group_id,
            ),
            primary_source_identity=MOCK_SPEC_SOURCE_IDENTITY,
            target_model_artifact_sha256=MOCK_TARGET_MODEL_SHA256,
            target_tokenizer_identity=self._target_tokenizer_identity,
            target_tokenizer_artifact_files=dict(
                self._target_tokenizer_artifact_files
            ),
        )
        return RuntimeResult(
            events=[],
            token_count=output_count,
            output_token_count=output_count,
            metadata={
                "evidence_level": "fixture_mock_non_live",
                "production_runtime_support": False,
            },
            axi_result=axi,
        )

    @staticmethod
    def _require_axi(config: BenchmarkConfig) -> None:
        if config.schema_extensions != [AXI_CONFIG_EXTENSION]:
            raise ValueError("mock spec adapter requires the AXI config extension")

    @staticmethod
    def _load_roster(reference: str, expected_sha256: str) -> RequestRoster:
        raw = Path(reference).read_bytes()
        if sha256_bytes(raw) != expected_sha256:
            raise ValueError("mock spec request roster byte hash mismatch")
        roster = RequestRoster.from_mapping(json.loads(raw))
        if roster.to_bytes() != raw:
            raise ValueError("mock spec request roster is not normalized bytes")
        return roster

    @staticmethod
    def _validate_scenario_for_policy(
        scenario: MockSpecScenario, config: BenchmarkConfig
    ) -> None:
        speculation = config.speculation
        assert speculation is not None
        for step in scenario.steps:
            if not 0.02 <= step.emission_offset_s <= 0.08:
                raise ValueError("mock spec emission lies outside decode window")
            for offset in step.token_timestamp_offsets_s:
                if offset is not None and not 0.02 <= offset <= 0.08:
                    raise ValueError("mock spec token timestamp lies outside decode window")
            if speculation.mode == "off":
                if (
                    step.tokens_proposed is not None
                    or step.tokens_accepted is not None
                    or step.target_emitted_count != step.emitted_count
                ):
                    raise ValueError("mock spec-off counter partition is invalid")
            else:
                if step.tokens_proposed is None or step.tokens_accepted is None:
                    raise ValueError("enabled mock spec step requires proposal counters")
                if step.tokens_proposed > int(speculation.max_proposed_tokens):
                    raise ValueError("mock proposal exceeds configured cap")
                if step.tokens_accepted > step.tokens_proposed:
                    raise ValueError("mock acceptance exceeds proposals")
                if step.emitted_count != step.tokens_accepted + step.target_emitted_count:
                    raise ValueError("mock enabled counter partition is invalid")
        cancelled = scenario.cancelled_proposal_counters
        if cancelled is not None:
            if speculation.mode == "off":
                raise ValueError("spec-off cannot retain proposal cancellation counters")
            if cancelled.tokens_proposed > int(speculation.max_proposed_tokens):
                raise ValueError("mock cancelled proposal exceeds configured cap")

    @staticmethod
    def _request_result(
        ordinal: int,
        request_input_id: str,
        start: float,
        scenario: MockSpecScenario,
    ) -> AxiRequestResult:
        tokens: list[AxiRequestToken] = []
        emissions: list[AxiDecodeEmission] = []
        output_ordinal = 0
        for step_ordinal, step in enumerate(scenario.steps):
            emissions.append(
                AxiDecodeEmission(
                    timestamp_s=start + step.emission_offset_s,
                    decode_step_ordinal=step_ordinal,
                    output_token_start_ordinal=output_ordinal,
                    emitted_count=step.emitted_count,
                    tokens_proposed=step.tokens_proposed,
                    tokens_accepted=step.tokens_accepted,
                    target_emitted_count=step.target_emitted_count,
                    emitted_token_ids=step.token_ids,
                    scheduler_step_id=f"mock-step-{step_ordinal:03d}",
                )
            )
            for offset_index, timestamp_offset in enumerate(
                step.token_timestamp_offsets_s
            ):
                tokens.append(
                    AxiRequestToken(
                        output_token_ordinal=output_ordinal,
                        decode_step_ordinal=step_ordinal,
                        token_id=(
                            step.token_ids[offset_index]
                            if step.token_ids is not None
                            else None
                        ),
                        timestamp_s=(
                            start + timestamp_offset
                            if timestamp_offset is not None
                            else None
                        ),
                        timestamp_provenance=(
                            "runtime_per_token_callback"
                            if timestamp_offset is not None
                            else None
                        ),
                    )
                )
                output_ordinal += 1
        return AxiRequestResult(
            request_id=f"request-{ordinal:03d}",
            request_ordinal=ordinal,
            request_input_id=request_input_id,
            submitted_at_s=start + 0.001,
            admitted_at_s=start + 0.002,
            phase_windows=(
                AxiPhaseWindow("prefill", 0, start + 0.005, start + 0.02),
                AxiPhaseWindow("decode", 1, start + 0.02, start + 0.08),
            ),
            emissions=tuple(emissions),
            tokens=tuple(tokens),
            terminal_at_s=start + scenario.terminal_offset_s,
            terminal_status=scenario.terminal_status,
            stop_reason=scenario.stop_reason,
            failure_reason=scenario.failure_reason,
            failure_message=scenario.failure_message,
            response_text=scenario.response_text,
            cancelled_proposal_counters=scenario.cancelled_proposal_counters,
        )
