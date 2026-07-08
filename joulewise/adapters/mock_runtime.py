"""Deterministic mock runtime adapter (decisions D-009, D-019).

The mock runtime derives its entire timeline from the benchmark config and an
injected :class:`joulewise.clock.Clock` (D-019): prefill costs 1 ms per prompt
token, decode costs 10 ms per output token with one ``token`` event each, so
expected timestamps and energies are closed-form when driven by a
``FakeClock``. It is part of the stdlib-only core (D-009) and exists so the
controller lifecycle, bundle contract, and reducer math can be proven without
hardware.

Fault-injection conventions (internal convention per the Phase 2 plan, Slice
2B; revisit if configs need first-class fault injection):

- ``model.name == "mock-unsupported"`` makes :meth:`MockRuntimeAdapter.prepare`
  return a structured ``did_not_fit`` failure, so the controller's
  ``FailureReason -> RunStatus`` mapping (D-012, status ``unsupported``) can be
  tested end-to-end.
- The companion telemetry convention (``hardware_target.notes ==
  "telemetry-denied"`` => ``permission_denied``) is documented in
  :mod:`joulewise.adapters.mock_telemetry`.
"""

from __future__ import annotations

import json

from joulewise import __version__
from joulewise.clock import Clock
from joulewise.interfaces import AdapterResult, RunContext, RuntimeEvent, RuntimeResult
from joulewise.provenance import output_policy, prompt_provenance
from joulewise.schemas import BenchmarkConfig, FailureReason

#: model.name value that triggers the did_not_fit fault injection (see module
#: docstring).
UNSUPPORTED_MODEL_NAME = "mock-unsupported"

#: Deterministic timeline constants (D-019).
WARMUP_SECONDS = 0.05
PREFILL_SECONDS_PER_PROMPT_TOKEN = 0.001
DECODE_SECONDS_PER_OUTPUT_TOKEN = 0.010

#: Fallbacks when the workload profile does not pin token counts.
DEFAULT_PROMPT_TOKENS = 32
DEFAULT_OUTPUT_TOKENS = 8


class MockRuntimeAdapter:
    """Deterministic, clock-driven implementation of ``RuntimeAdapter``."""

    name = "mock"

    def __init__(self, clock: Clock) -> None:
        self._clock = clock

    def prepare(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> AdapterResult:
        if config.model.name == UNSUPPORTED_MODEL_NAME:
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.DID_NOT_FIT,
                message=(
                    "mock fault injection: model.name == 'mock-unsupported' "
                    "simulates a model that does not fit on the target "
                    "(did_not_fit); internal convention documented in "
                    "joulewise.adapters.mock_runtime"
                ),
            )
        return AdapterResult(
            ok=True,
            metadata={"adapter": "mock_runtime", "version": __version__},
        )

    def warmup(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> AdapterResult:
        self._clock.sleep(WARMUP_SECONDS)
        return AdapterResult(ok=True)

    def run_workload(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> RuntimeResult:
        prompt_tokens = self._prompt_tokens(config)
        prompt_token_ids = self._prompt_token_ids(prompt_tokens)
        output_tokens = config.workload_profile.output_tokens or DEFAULT_OUTPUT_TOKENS
        clock = self._clock

        events: list[RuntimeEvent] = []
        events.append(self._event("phase_start", "prefill", "mock prefill started"))
        clock.sleep(prompt_tokens * PREFILL_SECONDS_PER_PROMPT_TOKEN)
        events.append(self._event("phase_end", "prefill", "mock prefill completed"))

        events.append(self._event("phase_start", "decode", "mock decode started"))
        token_records: list[dict[str, float | int]] = []
        for index in range(output_tokens):
            clock.sleep(DECODE_SECONDS_PER_OUTPUT_TOKEN)
            timestamp_s = clock.now()
            events.append(
                RuntimeEvent(
                    timestamp_s=timestamp_s,
                    event_type="token",
                    phase="decode",
                    message=f"mock token {index}",
                    metadata={"index": index},
                )
            )
            token_records.append({"index": index, "timestamp_s": timestamp_s})
        events.append(self._event("phase_end", "decode", "mock decode completed"))

        response_text = (
            f"mock response from model {config.model.name}: "
            f"prompt_tokens={prompt_tokens} output_tokens={output_tokens}\n"
        )
        tokens_jsonl = "".join(
            json.dumps(record, sort_keys=True) + "\n" for record in token_records
        )
        return RuntimeResult(
            events=events,
            output_artifacts={
                "response.txt": response_text,
                "tokens.jsonl": tokens_jsonl,
            },
            token_count=prompt_tokens + output_tokens,
            output_token_count=output_tokens,
            workload_provenance={
                "prompt": prompt_provenance(
                    prompt_token_ids,
                    text=config.workload_profile.prompt_text,
                ),
                "generator": {
                    "name": "mock_runtime",
                    "version": __version__,
                },
                "tokenizer": {
                    "backend": "mock",
                    "identifier": "joulewise.mock_tokenizer.v1",
                    "revision": __version__,
                    "class": "MockRuntimeAdapter",
                    "vocab_size": None,
                },
                "model": {
                    "source": config.model.source,
                    "revision": config.model.revision,
                },
                "output_policy": output_policy(
                    "fixed_budget_exact",
                    requested_tokens=output_tokens,
                    emitted_tokens=output_tokens,
                    stop_condition="requested_tokens_emitted",
                ),
            },
        )

    def cleanup(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> AdapterResult:
        return AdapterResult(ok=True)

    def _event(self, event_type: str, phase: str, message: str) -> RuntimeEvent:
        return RuntimeEvent(
            timestamp_s=self._clock.now(),
            event_type=event_type,
            phase=phase,
            message=message,
        )

    @staticmethod
    def _prompt_tokens(config: BenchmarkConfig) -> int:
        profile = config.workload_profile
        if profile.prompt_tokens is not None:
            return profile.prompt_tokens
        if profile.prompt_text:
            return len(profile.prompt_text.split())
        return DEFAULT_PROMPT_TOKENS

    @staticmethod
    def _prompt_token_ids(prompt_tokens: int) -> list[int]:
        return list(range(1, prompt_tokens + 1))
