"""MLX runtime adapter for local Apple Silicon generation (Slice 2G).

The core package remains stdlib-only: this module is importable without MLX,
and ``mlx_lm`` is imported only inside ``prepare``. Tests exercise the workload
mapping and event shape with fakes, while real runs use the same adapter path.
"""

from __future__ import annotations

import importlib
import inspect
import json
import os
import subprocess
from collections.abc import Iterable
from dataclasses import dataclass
from importlib import metadata as importlib_metadata
from pathlib import Path
from typing import Any

from joulewise.clock import Clock
from joulewise.interfaces import AdapterResult, RunContext, RuntimeEvent, RuntimeResult
from joulewise.provenance import (
    PROMPT_TOKEN_IDS_HASH_DOMAIN,
    output_policy,
    prompt_provenance,
    sha256_hex,
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
    order_seed,
    suite_manifest_sha256,
)

DEFAULT_OUTPUT_TOKENS = 8
WARMUP_TOKENS = 4
SYNTHETIC_PROMPT_SEED = "JouleWise synthetic prompt token sequence."


@dataclass(frozen=True)
class _GenerationRecord:
    events: list[RuntimeEvent]
    token_records: list[dict[str, float | int]]
    text: str
    stop_condition: str
    prompt_tokens: int
    output_tokens: int
    sampler_provenance: dict[str, Any]
    prompt_token_ids: list[int]
    prompt_text: str | None


class MlxRuntimeAdapter:
    """RuntimeAdapter implementation backed by ``mlx_lm``."""

    name = "mlx"

    def __init__(self, clock: Clock) -> None:
        self._clock = clock
        self._mlx_lm: Any | None = None
        self._model: Any | None = None
        self._tokenizer: Any | None = None
        self._model_config: dict[str, Any] | None = None
        self._original_eos_token_ids: set[int] | None = None

    def prepare(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> AdapterResult:
        source = config.model.source
        if not source:
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.RUNTIME_UNAVAILABLE,
                message=(
                    "runtime backend 'mlx' requires model.source to be a local "
                    "MLX model path; install the [mac] extra and configure a "
                    "local mirror to avoid network downloads"
                ),
            )

        try:
            mlx_lm = self._import_mlx_lm()
        except ImportError as exc:
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.RUNTIME_UNAVAILABLE,
                message=(
                    "runtime backend 'mlx' is not installed; install the "
                    "[mac] extra (pip install 'joulewise[mac]'). If MLX cannot "
                    f"be installed on this host, use another runtime. Import "
                    f"error: {exc}"
                ),
            )
        except Exception as exc:  # noqa: BLE001 - imports can fail during backend init
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.RUNTIME_UNAVAILABLE,
                message=(
                    "runtime backend 'mlx' could not initialize; install/use "
                    "the [mac] extra on an Apple Silicon session with GPU "
                    f"access. {type(exc).__name__}: {exc}"
                ),
            )

        start_s = self._clock.now()
        try:
            loaded = mlx_lm.load(
                source,
                revision=config.model.revision,
                return_config=True,
            )
        except Exception as exc:  # noqa: BLE001 - structured adapter failure (D-012)
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.RUNTIME_UNAVAILABLE,
                message=(
                    "runtime backend 'mlx' could not load the configured local "
                    f"model source {source!r}; install/use the [mac] extra and "
                    f"verify the local mirror is complete. {type(exc).__name__}: {exc}"
                ),
            )
        end_s = self._clock.now()

        self._mlx_lm = mlx_lm
        self._model, self._tokenizer, self._model_config = loaded
        self._original_eos_token_ids = _tokenizer_eos_ids(self._tokenizer)

        metadata = {
            "adapter": "mlx_runtime",
            "mlx_lm_version": _module_or_distribution_version(mlx_lm, "mlx-lm"),
            "mlx_version": _distribution_version("mlx"),
            "model_source": str(Path(source).expanduser()),
            "model_source_is_local_path": Path(source).expanduser().exists(),
            "model_revision": config.model.revision,
            "load_wall_time_s": end_s - start_s,
            "weight_format": config.model.weight_format,
            "quantization": config.quantization.name,
        }
        if isinstance(self._model_config, dict):
            metadata["model_config_name"] = self._model_config.get("model_type")
            metadata["model_config_eos_token_id"] = self._model_config.get("eos_token_id")
        metadata["memory_snapshots"] = [self._memory_snapshot("prepare_end")]
        return AdapterResult(ok=True, metadata=metadata)

    def warmup(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> AdapterResult:
        if self._mlx_lm is None or self._model is None or self._tokenizer is None:
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.RUNTIME_UNAVAILABLE,
                message="runtime backend 'mlx' warmup called before prepare succeeded",
            )
        prompt, _, _ = self._prompt_for_workload(config)
        try:
            for _ in self._mlx_lm.stream_generate(
                self._model,
                self._tokenizer,
                prompt,
                max_tokens=WARMUP_TOKENS,
            ):
                pass
        except Exception as exc:  # noqa: BLE001 - structured adapter failure (D-012)
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.RUNTIME_UNAVAILABLE,
                message=f"runtime backend 'mlx' warmup failed: {type(exc).__name__}: {exc}",
            )
        return AdapterResult(ok=True)

    def run_workload(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> RuntimeResult:
        if self._mlx_lm is None or self._model is None or self._tokenizer is None:
            raise RuntimeError("runtime backend 'mlx' run_workload called before prepare")

        max_tokens = config.workload_profile.output_tokens or DEFAULT_OUTPUT_TOKENS
        # The encode runs INSIDE the tokenize phase window (prepare_prompt is
        # called between the tokenize markers) so per-phase attribution covers
        # the real tokenization work on a live clock.
        record = self._generate(
            None,
            [],
            None,
            max_tokens,
            suppress_eos=True,
            prepare_prompt=lambda: self._prompt_for_workload(config),
        )
        prompt_token_ids = record.prompt_token_ids
        prompt_text = record.prompt_text
        tokens_jsonl = "".join(
            json.dumps(token_record, sort_keys=True) + "\n"
            for token_record in record.token_records
        )
        return RuntimeResult(
            events=record.events,
            output_artifacts={
                "response.txt": record.text,
                "tokens.jsonl": tokens_jsonl,
            },
            token_count=record.prompt_tokens + record.output_tokens,
            output_token_count=record.output_tokens,
            workload_provenance={
                "prompt": prompt_provenance(prompt_token_ids, text=prompt_text),
                "generator": {
                    "name": "mlx_lm.stream_generate",
                    "version": _module_or_distribution_version(self._mlx_lm, "mlx-lm"),
                },
                "sampler": record.sampler_provenance,
                "tokenizer": _tokenizer_identity(self._tokenizer, config),
                "model": {
                    "source": config.model.source,
                    "revision": config.model.revision,
                },
                "output_policy": output_policy(
                    "fixed_budget_exact",
                    requested_tokens=max_tokens,
                    emitted_tokens=record.output_tokens,
                    stop_condition=record.stop_condition,
                ),
            },
        )

    def run_suite(
        self,
        config: BenchmarkConfig,
        manifest: SuiteManifest,
        context: RunContext | None = None,
    ) -> RuntimeResult:
        if self._mlx_lm is None or self._model is None or self._tokenizer is None:
            raise RuntimeError("runtime backend 'mlx' run_suite called before prepare")

        manifest_sha256 = suite_manifest_sha256(manifest.to_dict())
        rep_index = _suite_rep_index_from_run_id(config.run_id)
        derived_order_seed = order_seed(
            manifest.suite_seed,
            manifest.execution_policy.order_policy,
            rep_index,
        )
        events: list[RuntimeEvent] = [
            self._event(
                SUITE_START,
                SUITE_PHASE,
                "mlx suite started",
                {
                    "suite_id": manifest.suite_id,
                    "suite_profile": manifest.suite_profile,
                    "suite_revision": manifest.suite_revision,
                    "suite_manifest_sha256": manifest_sha256,
                    "item_count": len(manifest.items),
                    "order_seed": derived_order_seed,
                },
            )
        ]
        output_lines: list[str] = []
        status_counts: dict[str, int] = {}
        total_prompt_tokens = 0
        total_planned_output_tokens = 0
        total_output_tokens = 0
        prompt_hashes: list[str] = []
        suite_sampler_recorded = False
        previous_item_id: str | None = None
        current_block: str | None = None
        current_level: str | None = None
        block_indices: dict[str, int] = {}
        level_indices: dict[tuple[str, str], int] = {}
        sampler_provenance = self._sampler_provenance_unavailable(
            "no suite item generation attempted"
        )

        for item_index, item in enumerate(manifest.items):
            block_id = item.grouping.block_id
            level_id = item.grouping.level_id
            if block_id != current_block:
                if current_level is not None:
                    events.append(
                        self._event(
                            LEVEL_END,
                            SUITE_PHASE,
                            f"mlx level {current_level} ended",
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
                            f"mlx block {current_block} ended",
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
                        f"mlx block {block_id} started",
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
                            f"mlx level {current_level} ended",
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
                        f"mlx level {level_id} started",
                        {"level_id": level_id, "level_index": level_indices[level_key]},
                    )
                )
                current_level = level_id

            item_result = self._run_suite_item(
                item,
                item_index,
                previous_item_id,
                events,
            )
            # First real record wins: an item whose generation never started
            # returns the unavailable sentinel and must not mask an earlier
            # item's pinned sampler provenance (the sampler is constant).
            if item_result["sampler_recorded"] and not suite_sampler_recorded:
                sampler_provenance = item_result["sampler_provenance"]
                suite_sampler_recorded = True
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
                    f"mlx level {current_level} ended",
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
                    f"mlx block {current_block} ended",
                    {"block_id": current_block, "block_index": block_indices[current_block]},
                )
            )
        events.append(
            self._event(
                SUITE_END,
                SUITE_PHASE,
                "mlx suite completed",
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
                    "order_seed": derived_order_seed,
                },
                "generator": {
                    "name": "mlx_lm.stream_generate",
                    "version": _module_or_distribution_version(self._mlx_lm, "mlx-lm"),
                },
                "sampler": sampler_provenance,
                "tokenizer": _tokenizer_identity(self._tokenizer, config),
                "model": {
                    "source": config.model.source,
                    "revision": config.model.revision,
                },
                "output_policy": output_policy(
                    manifest.execution_policy.default_output_policy,
                    requested_tokens=total_planned_output_tokens,
                    emitted_tokens=total_output_tokens,
                    stop_condition="suite_completed",
                ),
            },
        )

    def _run_suite_item(
        self,
        item: SuiteItem,
        item_index: int,
        previous_item_id: str | None,
        events: list[RuntimeEvent],
    ) -> dict[str, Any]:
        prompt_tokens_for_marker = item.shape.planned_prompt_tokens
        prompt_text: str | None = None
        prompt_token_ids: list[int] = []
        prompt_hash = prompt_provenance(prompt_token_ids)["token_ids_sha256"]
        prompt_ready = False
        try:
            prompt, prompt_token_ids, prompt_text = self._prompt_for_suite_item(item)
            prompt_hash = prompt_provenance(prompt_token_ids, text=prompt_text)[
                "token_ids_sha256"
            ]
            prompt_tokens_for_marker = len(prompt_token_ids)
            prompt_ready = True
        except Exception:
            prompt = []

        events.append(
            self._event(
                ITEM_START,
                SUITE_PHASE,
                f"mlx item {item.item_id} started",
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
                    "prompt_sha256": prompt_hash,
                    "planned_prompt_tokens": item.shape.planned_prompt_tokens,
                    "planned_output_tokens": item.shape.planned_output_tokens,
                },
            )
        )

        status_reason: str | None = None
        response_text = ""
        response_sha256 = sha256_hex(response_text)
        stop_reason = "runtime_failed"
        emitted_tokens = 0
        token_records: list[dict[str, float | int]] = []
        sampler_recorded = False
        sampler_provenance = self._sampler_provenance_unavailable(
            "item generation did not start"
        )

        try:
            if not prompt_ready:
                raise RuntimeError("suite item prompt could not be prepared")
            generation = self._generate(
                prompt,
                prompt_token_ids,
                prompt_text,
                item.shape.planned_output_tokens,
                suppress_eos=item.output_policy == "fixed_budget_exact",
                item_id=item.item_id,
                item_index=item_index,
                token_message_prefix=f"mlx suite item {item.item_id}",
            )
            events.extend(generation.events)
            sampler_provenance = generation.sampler_provenance
            sampler_recorded = True
            response_text = generation.text
            response_sha256 = sha256_hex(response_text)
            stop_reason = generation.stop_condition
            emitted_tokens = generation.output_tokens
            token_records = generation.token_records
            prompt_tokens_for_marker = generation.prompt_tokens
            if item.output_policy == "fixed_budget_exact":
                if emitted_tokens < item.shape.planned_output_tokens:
                    status = ItemStatus.MALFORMED.value
                    status_reason = "fixed_budget_underrun"
                else:
                    status = ItemStatus.SUCCEEDED.value
            elif emitted_tokens == item.shape.planned_output_tokens:
                status = ItemStatus.CAPPED.value
                stop_reason = "length"
            else:
                status = ItemStatus.SUCCEEDED.value
        except Exception as exc:  # noqa: BLE001 - per-item containment (D-045)
            status = ItemStatus.RUNTIME_FAILED.value
            status_reason = f"{type(exc).__name__}: {exc}"

        end_metadata = {
            "item_id": item.item_id,
            "item_index": item_index,
            "status": status,
            "prompt_tokens": prompt_tokens_for_marker,
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
                f"mlx item {item.item_id} ended",
                end_metadata,
            )
        )
        output = {
            "item_id": item.item_id,
            "item_index": item_index,
            "status": status,
            "prompt": {
                "token_hash_domain": PROMPT_TOKEN_IDS_HASH_DOMAIN,
                "token_ids_sha256": prompt_hash,
            },
            "response_text": response_text,
            "response_sha256": response_sha256,
            "stop_reason": stop_reason,
            "prompt_tokens": prompt_tokens_for_marker,
            "emitted_tokens": emitted_tokens,
            "tokens": token_records,
        }
        if status_reason is not None:
            output["status_reason"] = status_reason
        return {
            "status": status,
            "prompt_tokens": prompt_tokens_for_marker,
            "planned_output_tokens": item.shape.planned_output_tokens,
            "emitted_tokens": emitted_tokens,
            "prompt_hash": prompt_hash,
            "sampler_provenance": sampler_provenance,
            "sampler_recorded": sampler_recorded,
            "output": output,
        }

    def _generate(
        self,
        prompt: Any,
        prompt_token_ids: list[int],
        prompt_text: str | None,
        max_tokens: int,
        *,
        suppress_eos: bool,
        item_id: str | None = None,
        item_index: int | None = None,
        token_message_prefix: str = "mlx token",
        prepare_prompt: Any | None = None,
    ) -> _GenerationRecord:
        events: list[RuntimeEvent] = [
            self._event("phase_start", "tokenize", "mlx tokenization started")
        ]
        if prepare_prompt is not None:
            # Single-prompt path: the encode happens here, inside the tokenize
            # window. Suite items encode before item_start instead (the marker
            # carries the prompt hash), so their tokenize window is residual.
            prompt, prompt_token_ids, prompt_text = prepare_prompt()
        prompt_tokens = len(prompt_token_ids)
        events.append(
            self._event(
                "phase_end",
                "tokenize",
                "mlx tokenization completed",
                {"prompt_tokens": prompt_tokens},
            )
        )
        events.append(
            self._event(
                "phase_start",
                "generation_setup",
                "mlx generation setup started",
            )
        )
        original_eos_ids = self._suppress_eos() if suppress_eos else None
        eos_suppressed = original_eos_ids is not None
        events.append(
            self._event(
                "phase_end",
                "generation_setup",
                "mlx generation setup completed",
                {
                    "requested_output_tokens": max_tokens,
                    "eos_suppressed": eos_suppressed,
                },
            )
        )
        prefill_metadata: dict[str, Any] = {
            "phase_boundary_method": "first_token",
            "prompt_tokens": prompt_tokens,
            "requested_output_tokens": max_tokens,
            "eos_suppressed": eos_suppressed,
        }
        if item_id is not None:
            prefill_metadata.update({"item_id": item_id, "item_index": item_index})
        events.append(
            self._event(
                "phase_start",
                "prefill",
                "mlx prefill started",
                prefill_metadata,
            )
        )
        token_records: list[dict[str, float | int]] = []
        text_parts: list[str] = []
        last_finish_reason: str | None = None
        sampler, sampler_provenance = self._sampler_for_generation()

        try:
            stream_kwargs: dict[str, Any] = {"max_tokens": max_tokens}
            if sampler is not None:
                stream_kwargs["sampler"] = sampler
            stream = self._mlx_lm.stream_generate(
                self._model,
                self._tokenizer,
                prompt,
                **stream_kwargs,
            )
            for index, response in enumerate(stream):
                if index == 0:
                    prefill_end_metadata: dict[str, Any] = {
                        "phase_boundary_method": "first_token"
                    }
                    decode_start_metadata: dict[str, Any] = {
                        "phase_boundary_method": "first_token",
                        "max_tokens": max_tokens,
                        "eos_suppressed": eos_suppressed,
                        "original_eos_token_ids": (
                            sorted(original_eos_ids)
                            if original_eos_ids is not None
                            else None
                        ),
                    }
                    if item_id is not None:
                        prefill_end_metadata.update(
                            {"item_id": item_id, "item_index": item_index}
                        )
                        decode_start_metadata.update(
                            {"item_id": item_id, "item_index": item_index}
                        )
                    events.append(
                        self._event(
                            "phase_end",
                            "prefill",
                            "mlx prefill completed",
                            prefill_end_metadata,
                        )
                    )
                    events.append(
                        self._event(
                            "phase_start",
                            "decode",
                            "mlx decode started",
                            decode_start_metadata,
                        )
                    )
                timestamp_s = self._clock.now()
                text_parts.append(str(getattr(response, "text", "")))
                finish_reason = getattr(response, "finish_reason", None)
                if isinstance(finish_reason, str):
                    last_finish_reason = finish_reason
                token_metadata: dict[str, Any] = {"index": index}
                if item_id is not None:
                    token_metadata.update({"item_id": item_id, "item_index": item_index})
                events.append(
                    RuntimeEvent(
                        timestamp_s=timestamp_s,
                        event_type="token",
                        phase="decode",
                        message=(
                            f"{token_message_prefix} {index}"
                            if item_id is not None
                            else f"mlx token {index}"
                        ),
                        metadata=token_metadata,
                    )
                )
                token_records.append({"index": index, "timestamp_s": timestamp_s})
        finally:
            self._restore_eos(original_eos_ids)

        if not token_records:
            boundary_metadata: dict[str, Any] = {"phase_boundary_method": "first_token"}
            decode_metadata: dict[str, Any] = {
                "phase_boundary_method": "first_token",
                "max_tokens": max_tokens,
                "eos_suppressed": eos_suppressed,
            }
            if item_id is not None:
                boundary_metadata.update({"item_id": item_id, "item_index": item_index})
                decode_metadata.update({"item_id": item_id, "item_index": item_index})
            boundary_event = self._event(
                "phase_end",
                "prefill",
                "mlx prefill completed without emitted tokens",
                boundary_metadata,
            )
            events.append(boundary_event)
            events.append(
                RuntimeEvent(
                    timestamp_s=boundary_event.timestamp_s,
                    event_type="phase_start",
                    phase="decode",
                    message="mlx decode started without emitted tokens",
                    metadata=decode_metadata,
                )
            )

        decode_end_metadata: dict[str, Any] = {
            "phase_boundary_method": "first_token",
            "emitted_tokens": len(token_records),
            "requested_output_tokens": max_tokens,
        }
        if item_id is not None:
            decode_end_metadata.update({"item_id": item_id, "item_index": item_index})
        events.append(
            self._event(
                "phase_end",
                "decode",
                "mlx decode completed",
                decode_end_metadata,
            )
        )

        response_text = "".join(text_parts)
        output_tokens = len(token_records)
        stop_condition = (
            "requested_tokens_emitted"
            if output_tokens == max_tokens
            else last_finish_reason or "stream_exhausted"
        )
        return _GenerationRecord(
            events=events,
            token_records=token_records,
            text=response_text,
            stop_condition=stop_condition,
            prompt_tokens=prompt_tokens,
            output_tokens=output_tokens,
            sampler_provenance=sampler_provenance,
            prompt_token_ids=prompt_token_ids,
            prompt_text=prompt_text,
        )

    def cleanup(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> AdapterResult:
        metadata = {"memory_snapshots": [self._memory_snapshot("cleanup_start")]}
        self._model = None
        self._tokenizer = None
        self._model_config = None
        self._mlx_lm = None
        self._original_eos_token_ids = None
        return AdapterResult(ok=True, metadata=metadata)

    def _memory_snapshot(self, label: str) -> dict[str, Any]:
        errors: dict[str, str] = {}
        snapshot: dict[str, Any] = {
            "label": label,
            "captured_at_s": self._clock.now(),
            "process_rss_bytes": _process_rss_bytes(errors),
            "mlx_metal": _mlx_metal_memory(errors),
        }
        if errors:
            snapshot["errors"] = errors
        return snapshot

    def _import_mlx_lm(self) -> Any:
        return importlib.import_module("mlx_lm")

    def _prompt_for_workload(
        self, config: BenchmarkConfig
    ) -> tuple[list[int], list[int], str | None]:
        profile = config.workload_profile
        if profile.prompt_text is not None:
            token_ids = _encode(self._tokenizer, profile.prompt_text, add_special_tokens=True)
            return token_ids, token_ids, profile.prompt_text
        if profile.prompt_tokens is not None:
            prompt_tokens = _synthetic_prompt_tokens(self._tokenizer, profile.prompt_tokens)
            return prompt_tokens, prompt_tokens, None
        if profile.dataset_ref is not None:
            prompt = f"Dataset reference: {profile.dataset_ref}"
            token_ids = _encode(self._tokenizer, prompt, add_special_tokens=True)
            return token_ids, token_ids, prompt
        if profile.suite_manifest_ref is not None:
            token_ids = _encode(
                self._tokenizer,
                SYNTHETIC_PROMPT_SEED,
                add_special_tokens=True,
            )
            return token_ids, token_ids, SYNTHETIC_PROMPT_SEED
        raise RuntimeError("workload_profile must define prompt_text, prompt_tokens, or dataset_ref")

    def _prompt_for_suite_item(
        self, item: SuiteItem
    ) -> tuple[list[int], list[int], str | None]:
        if item.source.prompt_text is not None:
            token_ids = _encode(self._tokenizer, item.source.prompt_text, add_special_tokens=True)
            return token_ids, token_ids, item.source.prompt_text
        if item.source.prompt_token_ids is not None:
            token_ids = list(item.source.prompt_token_ids)
            return token_ids, token_ids, None
        token_ids = _synthetic_prompt_tokens(
            self._tokenizer,
            item.shape.planned_prompt_tokens,
        )
        return token_ids, token_ids, None

    def _sampler_for_generation(self) -> tuple[Any | None, dict[str, Any]]:
        base = {
            "kind": "greedy",
            "temperature": 0.0,
        }
        if not self._stream_generate_accepts_sampler():
            return None, {
                **base,
                "pinned": False,
                "reason": "mlx_lm sampler API unavailable",
            }
        make_sampler = getattr(self._mlx_lm, "make_sampler", None)
        sampler_api = "mlx_lm.make_sampler"
        if not callable(make_sampler):
            # Installed mlx_lm exposes make_sampler under sample_utils, not
            # top-level (verified live 2026-07-08); check both homes.
            sample_utils = getattr(self._mlx_lm, "sample_utils", None)
            make_sampler = getattr(sample_utils, "make_sampler", None)
            sampler_api = "mlx_lm.sample_utils.make_sampler"
        if not callable(make_sampler):
            return None, {
                **base,
                "pinned": False,
                "reason": "mlx_lm sampler API unavailable",
            }
        errors: list[str] = []
        for kwargs in ({"temp": 0.0}, {"temperature": 0.0}):
            try:
                return make_sampler(**kwargs), {
                    **base,
                    "pinned": True,
                    "api": sampler_api,
                    "parameter": next(iter(kwargs)),
                }
            except TypeError as exc:
                errors.append(f"{next(iter(kwargs))}: {exc}")
            except Exception as exc:  # noqa: BLE001 - feature detection must be fail-soft
                return None, {
                    **base,
                    "pinned": False,
                    "reason": (
                        "mlx_lm sampler API unavailable: "
                        f"{type(exc).__name__}: {exc}"
                    ),
                }
        try:
            return make_sampler(0.0), {
                **base,
                "pinned": True,
                "api": sampler_api,
                "parameter": "positional_temp",
            }
        except TypeError as exc:
            errors.append(f"positional_temp: {exc}")
        except Exception as exc:  # noqa: BLE001 - feature detection must be fail-soft
            return None, {
                **base,
                "pinned": False,
                "reason": f"mlx_lm sampler API unavailable: {type(exc).__name__}: {exc}",
            }
        return None, {
            **base,
            "pinned": False,
            "reason": "mlx_lm sampler API unavailable",
            "errors": errors,
        }

    def _stream_generate_accepts_sampler(self) -> bool:
        stream_generate = getattr(self._mlx_lm, "stream_generate", None)
        if not callable(stream_generate):
            return False
        try:
            signature = inspect.signature(stream_generate)
        except (TypeError, ValueError):
            return False
        for parameter in signature.parameters.values():
            if parameter.kind == inspect.Parameter.VAR_KEYWORD:
                return True
            if parameter.name == "sampler":
                return True
        return False

    @staticmethod
    def _sampler_provenance_unavailable(reason: str) -> dict[str, Any]:
        return {
            "kind": "greedy",
            "temperature": 0.0,
            "pinned": False,
            "reason": reason,
        }

    def _suppress_eos(self) -> set[int] | None:
        original = _tokenizer_eos_ids(self._tokenizer)
        if original is None:
            return None
        try:
            setattr(self._tokenizer, "eos_token_ids", set())
        except Exception:  # noqa: BLE001 - some tokenizer wrappers may not expose this
            return None
        return original

    def _restore_eos(self, eos_ids: set[int] | None) -> None:
        if eos_ids is None:
            return
        try:
            setattr(self._tokenizer, "eos_token_ids", eos_ids)
        except Exception:
            pass

    def _event(
        self,
        event_type: str,
        phase: str,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> RuntimeEvent:
        return RuntimeEvent(
            timestamp_s=self._clock.now(),
            event_type=event_type,
            phase=phase,
            message=message,
            metadata=metadata or {},
        )


def _encode(tokenizer: Any, text: str, *, add_special_tokens: bool) -> list[int]:
    try:
        encoded = tokenizer.encode(text, add_special_tokens=add_special_tokens)
    except TypeError:
        encoded = tokenizer.encode(text)
    return list(encoded)


def _synthetic_prompt_tokens(tokenizer: Any, target_tokens: int) -> list[int]:
    seed = _encode(tokenizer, SYNTHETIC_PROMPT_SEED, add_special_tokens=False)
    if not seed:
        seed = _encode(tokenizer, "JouleWise", add_special_tokens=False)
    if not seed:
        seed = [0]
    repeated: list[int] = []
    while len(repeated) < target_tokens:
        repeated.extend(seed)
    return repeated[:target_tokens]


def _tokenizer_eos_ids(tokenizer: Any) -> set[int] | None:
    if tokenizer is None:
        return None
    try:
        value = getattr(tokenizer, "eos_token_ids")
    except Exception:  # noqa: BLE001 - wrappers may forward oddly
        return None
    if value is None:
        return None
    if isinstance(value, int):
        return {value}
    if isinstance(value, Iterable):
        result: set[int] = set()
        for item in value:
            if isinstance(item, int) and not isinstance(item, bool):
                result.add(item)
        return result or None
    return None


def _tokenizer_identity(tokenizer: Any, config: BenchmarkConfig) -> dict[str, Any]:
    return {
        "backend": "mlx",
        "identifier": _tokenizer_identifier(tokenizer, config),
        "revision": config.model.revision,
        "class": type(tokenizer).__name__,
        "vocab_size": _tokenizer_vocab_size(tokenizer),
    }


def _tokenizer_identifier(tokenizer: Any, config: BenchmarkConfig) -> str | None:
    for attr in ("name_or_path", "model_id", "model_path"):
        value = getattr(tokenizer, attr, None)
        if isinstance(value, str) and value:
            return value
    return config.model.source


def _tokenizer_vocab_size(tokenizer: Any) -> int | None:
    value = getattr(tokenizer, "vocab_size", None)
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    get_vocab = getattr(tokenizer, "get_vocab", None)
    if callable(get_vocab):
        try:
            vocab = get_vocab()
        except Exception:  # noqa: BLE001 - tokenizer wrappers vary
            return None
        if isinstance(vocab, dict):
            return len(vocab)
    try:
        size = len(tokenizer)
    except Exception:  # noqa: BLE001 - tokenizer wrappers vary
        return None
    if isinstance(size, int) and not isinstance(size, bool):
        return size
    return None


def _module_or_distribution_version(module: Any, distribution: str) -> str | None:
    value = getattr(module, "__version__", None)
    if isinstance(value, str):
        return value
    return _distribution_version(distribution)


def _distribution_version(distribution: str) -> str | None:
    try:
        return importlib_metadata.version(distribution)
    except importlib_metadata.PackageNotFoundError:
        return None


def _process_rss_bytes(errors: dict[str, str]) -> int | None:
    try:
        completed = subprocess.run(
            ["ps", "-o", "rss=", "-p", str(os.getpid())],
            capture_output=True,
            text=True,
            timeout=2.0,
            check=False,
        )
    except FileNotFoundError:
        errors["process_rss"] = "ps_not_found"
        return None
    except subprocess.TimeoutExpired:
        errors["process_rss"] = "timeout"
        return None
    except Exception as exc:  # noqa: BLE001 - memory metadata must be fail-soft.
        errors["process_rss"] = f"{type(exc).__name__}: {exc}"
        return None
    if completed.returncode != 0:
        errors["process_rss"] = f"returncode_{completed.returncode}"
        return None
    try:
        rss_kib = int(completed.stdout.strip())
    except ValueError:
        errors["process_rss"] = "parse"
        return None
    return rss_kib * 1024


def _mlx_metal_memory(errors: dict[str, str]) -> dict[str, Any]:
    unavailable = {
        "api_available": False,
        "active_memory_bytes": None,
        "cache_memory_bytes": None,
        "peak_memory_bytes": None,
    }
    try:
        mx = importlib.import_module("mlx.core")
    except ImportError:
        errors["mlx_metal"] = "mlx_core_not_found"
        return unavailable
    except Exception as exc:  # noqa: BLE001 - memory metadata must be fail-soft.
        errors["mlx_metal"] = f"{type(exc).__name__}: {exc}"
        return unavailable
    # Newer MLX exposes the getters on mx directly; mx.metal.* is deprecated.
    metal = getattr(mx, "metal", None)
    result: dict[str, Any] = {
        "api_available": metal is not None or callable(getattr(mx, "get_active_memory", None)),
        "active_memory_bytes": None,
        "cache_memory_bytes": None,
        "peak_memory_bytes": None,
    }
    numeric_values = 0
    for attr, key in (
        ("get_active_memory", "active_memory_bytes"),
        ("get_cache_memory", "cache_memory_bytes"),
        ("get_peak_memory", "peak_memory_bytes"),
    ):
        getter = getattr(mx, attr, None)
        if not callable(getter):
            getter = getattr(metal, attr, None) if metal is not None else None
        if not callable(getter):
            continue
        try:
            value = getter()
        except Exception as exc:  # noqa: BLE001 - MLX versions differ.
            errors[f"mlx_metal.{attr}"] = f"{type(exc).__name__}: {exc}"
            continue
        if isinstance(value, int | float) and not isinstance(value, bool):
            result[key] = int(value)
            numeric_values += 1
        else:
            errors[f"mlx_metal.{attr}"] = "non_numeric"
    if result["api_available"] and numeric_values == 0:
        errors["mlx_metal"] = "getters_unavailable"
    return result


def _suite_rep_index_from_run_id(run_id: str | None) -> int:
    if run_id is None or "__r" not in run_id:
        return 0
    suffix = run_id.rsplit("__r", 1)[1]
    return int(suffix) if suffix.isdigit() else 0
