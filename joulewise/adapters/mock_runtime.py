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
- Suite items tagged ``mock-runtime-failed`` or ``mock-malformed`` receive
  per-item ``runtime_failed`` / ``malformed`` status respectively while the
  suite loop continues.
"""

from __future__ import annotations

import json
from typing import Any

from joulewise import __version__
from joulewise.adapters.suite_control import SuiteItemResult, execute_suite
from joulewise.adapters.mock_spec_runtime import MockSpecRuntimeAdapter
from joulewise.clock import Clock
from joulewise.interfaces import AdapterResult, RunContext, RuntimeEvent, RuntimeResult
from joulewise.provenance import (
    PROMPT_TOKEN_IDS_HASH_DOMAIN,
    normalized_sha256_hex,
    output_policy,
    prompt_provenance,
    sha256_hex,
    suite_prompt_plan_class,
    suite_prompt_rollup,
)
from joulewise.schemas import BenchmarkConfig, FailureReason
from joulewise.suite import (
    ITEM_END,
    ITEM_START,
    SUITE_PHASE,
    ItemStatus,
    SuiteItem,
    SuiteManifest,
)

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
        self._mock_spec = MockSpecRuntimeAdapter(clock)

    def prepare(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> AdapterResult:
        if config.schema_extensions is not None:
            return self._mock_spec.prepare(config, context)
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
            metadata={
                "adapter": "mock_runtime",
                "version": __version__,
                "model_artifact_identity": _mock_model_artifact_identity(config),
            },
        )

    def warmup(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> AdapterResult:
        if config.schema_extensions is not None:
            return self._mock_spec.warmup(config, context)
        self._clock.sleep(WARMUP_SECONDS)
        return AdapterResult(ok=True)

    def run_workload(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> RuntimeResult:
        if config.schema_extensions is not None:
            return self._mock_spec.run_workload(config, context)
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
        emitted_token_ids: list[int] = []
        for index in range(output_tokens):
            clock.sleep(DECODE_SECONDS_PER_OUTPUT_TOKEN)
            timestamp_s = clock.now()
            token_id = index + 1
            emitted_token_ids.append(token_id)
            events.append(
                RuntimeEvent(
                    timestamp_s=timestamp_s,
                    event_type="token",
                    phase="decode",
                    message=f"mock token {index}",
                    metadata={"index": index},
                )
            )
            token_records.append(
                {"index": index, "timestamp_s": timestamp_s, "token_id": token_id}
            )
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
                    "artifact_identity": _mock_model_artifact_identity(config),
                },
                "response": {
                    "emitted_token_ids": emitted_token_ids,
                },
                "output_policy": output_policy(
                    "fixed_budget_exact",
                    requested_tokens=output_tokens,
                    emitted_tokens=output_tokens,
                    stop_condition="requested_tokens_emitted",
                ),
            },
        )

    def run_suite(
        self,
        config: BenchmarkConfig,
        manifest: SuiteManifest,
        context: RunContext | None = None,
        *,
        order_seed: str,
        order_row: int | None = None,
    ) -> RuntimeResult:
        suite_identity = _suite_identity(manifest)
        control = execute_suite(
            manifest,
            backend_name="mock",
            order_seed=order_seed,
            order_row=order_row,
            event_factory=self._event,
            run_item=lambda item, item_index, position, previous_item_id, events: (
                self._run_suite_item(
                    item,
                    item_index,
                    position,
                    previous_item_id,
                    events,
                    suite_identity=suite_identity,
                )
            ),
        )
        return RuntimeResult(
            events=control.events,
            output_artifacts={"suite_items.jsonl": control.output_jsonl},
            token_count=control.total_prompt_tokens + control.total_output_tokens,
            output_token_count=control.total_output_tokens,
            workload_provenance={
                "prompt": suite_prompt_rollup(
                    control.prompt_hashes, control.total_prompt_tokens
                ),
                "suite": control.suite_provenance,
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
                    "artifact_identity": _mock_model_artifact_identity(config),
                },
                "output_policy": output_policy(
                    manifest.execution_policy.default_output_policy,
                    requested_tokens=control.total_planned_output_tokens,
                    emitted_tokens=control.total_output_tokens,
                    stop_condition="suite_completed",
                ),
            },
        )

    def cleanup(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> AdapterResult:
        if config.schema_extensions is not None:
            return self._mock_spec.cleanup(config, context)
        return AdapterResult(ok=True)

    def _run_suite_item(
        self,
        item: SuiteItem,
        item_index: int,
        position: int,
        previous_item_id: str | None,
        events: list[RuntimeEvent],
        *,
        suite_identity: str,
    ) -> SuiteItemResult:
        prompt_token_ids = _mock_suite_prompt_token_ids(item)
        prompt = prompt_provenance(prompt_token_ids, text=item.source.prompt_text)
        events.append(
            self._event(
                ITEM_START,
                SUITE_PHASE,
                f"mock item {item.item_id} started",
                {
                    "item_id": item.item_id,
                    "item_index": item_index,
                    "position": position,
                    "block_id": item.grouping.block_id,
                    "level_id": item.grouping.level_id,
                    "condition_id": item.grouping.condition_id,
                    "prefix_group_id": item.grouping.prefix_group_id,
                    "prev_item": previous_item_id,
                    "category": item.category,
                    "item_type": item.item_type,
                    "output_policy": item.output_policy,
                    "prompt_sha256": prompt["token_ids_sha256"],
                    "planned_prompt_tokens": item.shape.planned_prompt_tokens,
                    "planned_output_tokens": item.shape.planned_output_tokens,
                },
            )
        )
        status_reason: str | None = None
        response_text = ""
        stop_reason = "requested_tokens_emitted"
        emitted_tokens = 0
        emitted_token_ids: list[int] = []
        token_records: list[dict[str, float | int]] = []
        annotations: list[dict[str, Any]] = []
        prompt_problem = _suite_prompt_closure_problem(
            item,
            prompt_token_ids,
            item.source.prompt_text,
            suite_identity=suite_identity,
        )

        if prompt_problem is not None and prompt_problem["severity"] == "fatal":
            status = ItemStatus.MALFORMED.value
            status_reason = prompt_problem["code"]
            stop_reason = "malformed"
            annotations.append(prompt_problem)
        elif "mock-runtime-failed" in item.tags:
            status = ItemStatus.RUNTIME_FAILED.value
            status_reason = "mock-runtime-failed"
            stop_reason = "runtime_failed"
        elif "mock-malformed" in item.tags:
            status = ItemStatus.MALFORMED.value
            status_reason = "mock-malformed"
            stop_reason = "malformed"
        else:
            if prompt_problem is not None:
                annotations.append(prompt_problem)
            item_phase_metadata = {
                "item_id": item.item_id,
                "item_index": item_index,
                "position": position,
            }
            events.append(
                self._event(
                    "phase_start",
                    "prefill",
                    f"{item.item_id} prefill started",
                    item_phase_metadata,
                )
            )
            self._clock.sleep(
                len(prompt_token_ids) * PREFILL_SECONDS_PER_PROMPT_TOKEN
            )
            events.append(
                self._event(
                    "phase_end",
                    "prefill",
                    f"{item.item_id} prefill completed",
                    item_phase_metadata,
                )
            )
            events.append(
                self._event(
                    "phase_start",
                    "decode",
                    f"{item.item_id} decode started",
                    item_phase_metadata,
                )
            )
            for index in range(item.shape.planned_output_tokens):
                self._clock.sleep(DECODE_SECONDS_PER_OUTPUT_TOKEN)
                timestamp_s = self._clock.now()
                token_id = index + 1
                emitted_token_ids.append(token_id)
                events.append(
                    RuntimeEvent(
                        timestamp_s=timestamp_s,
                        event_type="token",
                        phase="decode",
                        message=f"mock suite item {item.item_id} token {index}",
                        metadata={
                            "item_id": item.item_id,
                            "item_index": item_index,
                            "position": position,
                            "index": index,
                        },
                    )
                )
                token_records.append(
                    {"index": index, "timestamp_s": timestamp_s, "token_id": token_id}
                )
            events.append(
                self._event(
                    "phase_end",
                    "decode",
                    f"{item.item_id} decode completed",
                    item_phase_metadata,
                )
            )
            emitted_tokens = item.shape.planned_output_tokens
            status = (
                ItemStatus.CAPPED.value
                if item.output_policy == "natural_eos"
                else ItemStatus.SUCCEEDED.value
            )
            if status == ItemStatus.CAPPED.value:
                stop_reason = "length"
            response_text = (
                f"mock suite response item_id={item.item_id} "
                f"prompt_tokens={len(prompt_token_ids)} "
                f"output_tokens={emitted_tokens}\n"
            )

        response_sha256 = sha256_hex(response_text)
        end_metadata = {
            "item_id": item.item_id,
            "item_index": item_index,
            "position": position,
            "status": status,
            "prompt_tokens": len(prompt_token_ids),
            "emitted_tokens": emitted_tokens,
            "stop_reason": stop_reason,
            "response_sha256": response_sha256,
        }
        if status_reason is not None:
            end_metadata["status_reason"] = status_reason
        events.append(
            self._event(
                ITEM_END,
                SUITE_PHASE,
                f"mock item {item.item_id} ended",
                end_metadata,
            )
        )
        output = {
            "item_id": item.item_id,
            "item_index": item_index,
            "position": position,
            "status": status,
            "prompt_source": _suite_item_prompt_source(item),
            "bos_present": item.source.prompt_text is not None,
            "prompt": {
                "token_hash_domain": PROMPT_TOKEN_IDS_HASH_DOMAIN,
                "token_ids_sha256": prompt["token_ids_sha256"],
            },
            "response_text": response_text,
            "response_sha256": response_sha256,
            "stop_reason": stop_reason,
            "prompt_tokens": len(prompt_token_ids),
            "emitted_tokens": emitted_tokens,
            "emitted_token_ids": emitted_token_ids,
            "tokens": token_records,
        }
        if status_reason is not None:
            output["status_reason"] = status_reason
        if annotations:
            output["annotations"] = annotations
        return SuiteItemResult(
            status=status,
            prompt_tokens=len(prompt_token_ids),
            planned_output_tokens=item.shape.planned_output_tokens,
            emitted_tokens=emitted_tokens,
            prompt_hash=prompt["token_ids_sha256"],
            output=output,
        )

    def _event(
        self,
        event_type: str,
        phase: str,
        message: str,
        metadata: dict[str, object] | None = None,
    ) -> RuntimeEvent:
        return RuntimeEvent(
            timestamp_s=self._clock.now(),
            event_type=event_type,
            phase=phase,
            message=message,
            metadata={} if metadata is None else metadata,
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


def _suite_item_prompt_source(item: SuiteItem) -> str:
    source = item.prompt_source_kind()
    return "token_ids" if source == "prompt_token_ids" else source


def _mock_suite_prompt_token_ids(item: SuiteItem) -> list[int]:
    if item.source.prompt_text is not None:
        return list(range(1, len(item.source.prompt_text.split()) + 1))
    return item.prompt_token_ids()


def _mock_model_artifact_identity(config: BenchmarkConfig) -> dict[str, Any]:
    marker = {
        "adapter": "mock_runtime",
        "model_name": config.model.name,
        "model_source": config.model.source,
        "model_revision": config.model.revision,
    }
    return {
        "status": "ok",
        "kind": "mock_marker",
        "algorithm": "sha256",
        "sha256": sha256_hex(json.dumps(marker, separators=(",", ":"), sort_keys=True)),
        "marker": marker,
    }


def _suite_identity(manifest: SuiteManifest) -> str:
    return suite_prompt_plan_class(
        manifest.suite_id,
        manifest.suite_profile,
        manifest.source_manifest.source_id,
    )


def _suite_prompt_closure_problem(
    item: SuiteItem,
    prompt_token_ids: list[int],
    prompt_text: str | None,
    *,
    suite_identity: str,
) -> dict[str, Any] | None:
    if item.source.prompt_text is None:
        return None
    realized_hash = prompt_provenance(prompt_token_ids, text=prompt_text)[
        "token_ids_sha256"
    ]
    text_hash = sha256_hex(prompt_text or "")
    source_hash = normalized_sha256_hex(item.source.source_sha256)
    if source_hash is not None and source_hash not in {realized_hash, text_hash}:
        return {
            "code": "prompt_ids_mismatch",
            "severity": "fatal",
            "source_sha256": source_hash,
            "realized_prompt_token_ids_sha256": realized_hash,
            "prompt_text_sha256": text_hash,
        }
    planned = item.shape.planned_prompt_tokens
    realized = len(prompt_token_ids)
    if planned == realized:
        return None
    annotation = {
        "code": "planned_prompt_tokens_mismatch",
        "planned_prompt_tokens": planned,
        "realized_prompt_tokens": realized,
    }
    if suite_identity == "budgeted":
        return {**annotation, "severity": "fatal"}
    return {**annotation, "severity": "advisory"}
