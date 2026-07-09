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
    BLOCK_END,
    BLOCK_START,
    ITEM_END,
    ITEM_START,
    LEVEL_END,
    LEVEL_START,
    SUITE_END,
    SUITE_PHASE,
    SUITE_START,
    ItemStatus,
    SuiteItem,
    SuiteManifest,
    suite_manifest_sha256,
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
            metadata={
                "adapter": "mock_runtime",
                "version": __version__,
                "model_artifact_identity": _mock_model_artifact_identity(config),
            },
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
    ) -> RuntimeResult:
        manifest_sha256 = suite_manifest_sha256(manifest.to_dict())
        events: list[RuntimeEvent] = [
            self._event(
                SUITE_START,
                SUITE_PHASE,
                "mock suite started",
                {
                    "suite_id": manifest.suite_id,
                    "suite_profile": manifest.suite_profile,
                    "suite_revision": manifest.suite_revision,
                    "suite_manifest_sha256": manifest_sha256,
                    "item_count": len(manifest.items),
                    "order_seed": order_seed,
                },
            )
        ]
        output_lines: list[str] = []
        status_counts: dict[str, int] = {}
        total_prompt_tokens = 0
        total_planned_output_tokens = 0
        total_output_tokens = 0
        prompt_hashes: list[str] = []
        previous_item_id: str | None = None
        current_block: str | None = None
        current_level: str | None = None
        block_indices: dict[str, int] = {}
        level_indices: dict[tuple[str, str], int] = {}

        for item_index, item in enumerate(manifest.items):
            block_id = item.grouping.block_id
            level_id = item.grouping.level_id
            if block_id != current_block:
                if current_level is not None:
                    events.append(
                        self._event(
                            LEVEL_END,
                            SUITE_PHASE,
                            f"mock level {current_level} ended",
                            {
                                "level_id": current_level,
                                "level_index": level_indices[(current_block, current_level)],
                            },
                        )
                    )
                    current_level = None
                if current_block is not None:
                    events.append(
                        self._event(
                            BLOCK_END,
                            SUITE_PHASE,
                            f"mock block {current_block} ended",
                            {
                                "block_id": current_block,
                                "block_index": block_indices[current_block],
                            },
                        )
                    )
                block_indices.setdefault(block_id, len(block_indices))
                events.append(
                    self._event(
                        BLOCK_START,
                        SUITE_PHASE,
                        f"mock block {block_id} started",
                        {"block_id": block_id, "block_index": block_indices[block_id]},
                    )
                )
                current_block = block_id
            if level_id != current_level:
                if current_level is not None:
                    events.append(
                        self._event(
                            LEVEL_END,
                            SUITE_PHASE,
                            f"mock level {current_level} ended",
                            {
                                "level_id": current_level,
                                "level_index": level_indices[(current_block, current_level)],
                            },
                        )
                    )
                level_key = (block_id, level_id)
                level_indices.setdefault(level_key, len(level_indices))
                events.append(
                    self._event(
                        LEVEL_START,
                        SUITE_PHASE,
                        f"mock level {level_id} started",
                        {"level_id": level_id, "level_index": level_indices[level_key]},
                    )
                )
                current_level = level_id

            item_result = self._run_suite_item(
                item,
                item_index,
                previous_item_id,
                events,
                suite_identity=_suite_identity(manifest),
            )
            previous_item_id = item.item_id
            output_lines.append(json.dumps(item_result["output"], sort_keys=True) + "\n")
            status = item_result["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
            total_prompt_tokens += item_result["prompt_tokens"]
            total_planned_output_tokens += item_result["planned_output_tokens"]
            total_output_tokens += item_result["emitted_tokens"]
            prompt_hashes.append(item_result["prompt_hash"])

        if current_level is not None:
            events.append(
                self._event(
                    LEVEL_END,
                    SUITE_PHASE,
                    f"mock level {current_level} ended",
                    {
                        "level_id": current_level,
                        "level_index": level_indices[(current_block, current_level)],
                    },
                )
            )
        if current_block is not None:
            events.append(
                self._event(
                    BLOCK_END,
                    SUITE_PHASE,
                    f"mock block {current_block} ended",
                    {"block_id": current_block, "block_index": block_indices[current_block]},
                )
            )
        events.append(
            self._event(
                SUITE_END,
                SUITE_PHASE,
                "mock suite completed",
                {
                    "suite_id": manifest.suite_id,
                    "items_executed": len(manifest.items),
                    "status_counts": status_counts,
                },
            )
        )
        return RuntimeResult(
            events=events,
            output_artifacts={"suite_items.jsonl": "".join(output_lines)},
            token_count=total_prompt_tokens + total_output_tokens,
            output_token_count=total_output_tokens,
            workload_provenance={
                "prompt": suite_prompt_rollup(prompt_hashes, total_prompt_tokens),
                "suite": {
                    "suite_id": manifest.suite_id,
                    "manifest_sha256": manifest_sha256,
                    "item_count": len(manifest.items),
                    "order_seed": order_seed,
                },
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
                    requested_tokens=total_planned_output_tokens,
                    emitted_tokens=total_output_tokens,
                    stop_condition="suite_completed",
                ),
            },
        )

    def cleanup(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> AdapterResult:
        return AdapterResult(ok=True)

    def _run_suite_item(
        self,
        item: SuiteItem,
        item_index: int,
        previous_item_id: str | None,
        events: list[RuntimeEvent],
        *,
        suite_identity: str,
    ) -> dict[str, Any]:
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
                    "position": item_index,
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
            item_phase_metadata = {"item_id": item.item_id, "item_index": item_index}
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
                        metadata={"item_id": item.item_id, "item_index": item_index, "index": index},
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
        return {
            "status": status,
            "prompt_tokens": len(prompt_token_ids),
            "planned_output_tokens": item.shape.planned_output_tokens,
            "emitted_tokens": emitted_tokens,
            "prompt_hash": prompt["token_ids_sha256"],
            "output": output,
        }

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
