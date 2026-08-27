"""MLX runtime adapter for local Apple Silicon generation (Slice 2G).

The core package remains stdlib-only: this module is importable without MLX,
and ``mlx_lm`` is imported only inside ``prepare``. Tests exercise the workload
mapping and event shape with fakes, while real runs use the same adapter path.
"""

from __future__ import annotations

import importlib
import inspect
import json
import operator
import os
import subprocess
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from importlib import metadata as importlib_metadata
from pathlib import Path
from typing import Any

from joulewise.adapters.suite_control import SuiteItemResult, execute_suite
from joulewise.clock import Clock
from joulewise.interfaces import (
    AdapterFailure,
    AdapterResult,
    RunContext,
    RuntimeEvent,
    RuntimeResult,
)
from joulewise.provenance import (
    PROMPT_TOKEN_IDS_HASH_DOMAIN,
    fixed_budget_outcome_name,
    model_artifact_identity,
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

DEFAULT_OUTPUT_TOKENS = 8
WARMUP_TOKENS = 4
SYNTHETIC_PROMPT_SEED = "JouleWise synthetic prompt token sequence."

# ``mlx.core`` is a nanobind extension whose native initializer aborts the
# process if it runs twice and tries to register the same types/enums again.
# Keep a successful import alive even if another context evicts it from
# ``sys.modules`` so memory probes never re-execute that initializer.
_MLX_CORE_MODULE: Any | None = None


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
    output_token_ids: list[int]


class MlxRuntimeAdapter:
    """RuntimeAdapter implementation backed by ``mlx_lm``."""

    name = "mlx"

    def __init__(self, clock: Clock) -> None:
        self._clock = clock
        self._mlx_lm: Any | None = None
        self._model: Any | None = None
        self._tokenizer: Any | None = None
        self._model_config: dict[str, Any] | None = None
        self._model_artifact_identity: dict[str, Any] | None = None

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

        self._model_artifact_identity = model_artifact_identity(source)
        metadata = {
            "adapter": "mlx_runtime",
            "mlx_lm_version": _module_or_distribution_version(mlx_lm, "mlx-lm"),
            "mlx_version": _distribution_version("mlx"),
            "transformers_version": _distribution_version("transformers"),
            "model_source": str(Path(source).expanduser()),
            "model_source_is_local_path": Path(source).expanduser().exists(),
            "model_revision": config.model.revision,
            "load_wall_time_s": end_s - start_s,
            "weight_format": config.model.weight_format,
            "quantization": config.quantization.name,
            "model_artifact_identity": self._model_artifact_identity,
        }
        if isinstance(self._model_config, dict):
            metadata["model_config_name"] = self._model_config.get("model_type")
            metadata["model_config_eos_token_id"] = self._model_config.get("eos_token_id")
        metadata["memory_snapshots"] = [self._memory_snapshot("prepare_end")]
        return AdapterResult(ok=True, metadata=metadata)

    def identity_projection_metadata(
        self, config: BenchmarkConfig
    ) -> dict[str, Any]:
        """Probe runtime-owned identity fields after a successful prepare."""

        if self._mlx_lm is None or self._model is None or self._tokenizer is None:
            raise AdapterFailure(
                FailureReason.RUNTIME_UNAVAILABLE,
                "runtime backend 'mlx' identity projection called before prepare",
            )
        _, sampler = self._sampler_for_generation()
        return {
            "model": {
                "name": config.model.name,
                "source": config.model.source,
                "revision": config.model.revision,
                "artifact_identity": self._model_artifact_identity,
            },
            "tokenizer": _tokenizer_identity(self._tokenizer, config),
            "sampler": sampler,
            "output_policy": {
                "name": "fixed_budget_exact",
                "requested_tokens": config.workload_profile.output_tokens,
                "stop_condition": "requested_tokens_emitted",
            },
        }

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
                    "artifact_identity": self._model_artifact_identity,
                },
                "response": {
                    "emitted_token_ids": record.output_token_ids,
                },
                "output_policy": output_policy(
                    fixed_budget_outcome_name(
                        requested_tokens=max_tokens,
                        emitted_tokens=record.output_tokens,
                        stop_condition=record.stop_condition,
                    ),
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
        *,
        order_seed: str,
        order_row: int | None = None,
    ) -> RuntimeResult:
        if self._mlx_lm is None or self._model is None or self._tokenizer is None:
            raise RuntimeError("runtime backend 'mlx' run_suite called before prepare")
        self._sampler_for_generation()
        suite_identity = _suite_identity(manifest)
        control = execute_suite(
            manifest,
            backend_name="mlx",
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
        sampler_provenance = self._sampler_provenance_unavailable(
            "no suite item generation attempted"
        )
        for item_result in control.item_results:
            # First real record wins: an item whose generation never started
            # returns the unavailable sentinel and must not mask an earlier
            # item's pinned sampler provenance (the sampler is constant).
            if item_result.backend_metadata["sampler_recorded"]:
                sampler_provenance = item_result.backend_metadata["sampler_provenance"]
                break
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
                    "name": "mlx_lm.stream_generate",
                    "version": _module_or_distribution_version(self._mlx_lm, "mlx-lm"),
                },
                "sampler": sampler_provenance,
                "tokenizer": _tokenizer_identity(self._tokenizer, config),
                "model": {
                    "source": config.model.source,
                    "revision": config.model.revision,
                    "artifact_identity": self._model_artifact_identity,
                },
                "output_policy": output_policy(
                    manifest.execution_policy.default_output_policy,
                    requested_tokens=control.total_planned_output_tokens,
                    emitted_tokens=control.total_output_tokens,
                    stop_condition="suite_completed",
                ),
            },
        )

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
        prompt_tokens_for_marker = item.shape.planned_prompt_tokens
        prompt_text: str | None = None
        prompt_token_ids: list[int] = []
        prompt_source = item.prompt_source_kind()
        bos_present = False
        prompt_hash = prompt_provenance(prompt_token_ids)["token_ids_sha256"]
        prompt_ready = False
        try:
            (
                prompt,
                prompt_token_ids,
                prompt_text,
                prompt_source,
                bos_present,
            ) = self._prompt_for_suite_item(item)
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
                    "position": position,
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
        emitted_token_ids: list[int] = []
        annotations: list[dict[str, Any]] = []
        sampler_recorded = False
        sampler_provenance = self._sampler_provenance_unavailable(
            "item generation did not start"
        )

        try:
            if not prompt_ready:
                raise RuntimeError("suite item prompt could not be prepared")
            prompt_problem = _suite_prompt_closure_problem(
                item,
                prompt_token_ids,
                prompt_text,
                suite_identity=suite_identity,
            )
            if prompt_problem is not None and prompt_problem["severity"] == "fatal":
                status = ItemStatus.MALFORMED.value
                status_reason = prompt_problem["code"]
                stop_reason = "malformed"
                annotations.append(prompt_problem)
                raise _SuiteItemMalformed()
            if prompt_problem is not None:
                annotations.append(prompt_problem)
            generation = self._generate(
                prompt,
                prompt_token_ids,
                prompt_text,
                item.shape.planned_output_tokens,
                suppress_eos=item.output_policy == "fixed_budget_exact",
                item_id=item.item_id,
                item_index=item_index,
                position=position,
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
            emitted_token_ids = generation.output_token_ids
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
        except _SuiteItemMalformed:
            pass
        except Exception as exc:  # noqa: BLE001 - per-item containment (D-045)
            status = ItemStatus.RUNTIME_FAILED.value
            status_reason = f"{type(exc).__name__}: {exc}"

        end_metadata = {
            "item_id": item.item_id,
            "item_index": item_index,
            "position": position,
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
            "position": position,
            "status": status,
            "prompt_source": prompt_source,
            "bos_present": bos_present,
            "prompt": {
                "token_hash_domain": PROMPT_TOKEN_IDS_HASH_DOMAIN,
                "token_ids_sha256": prompt_hash,
            },
            "response_text": response_text,
            "response_sha256": response_sha256,
            "stop_reason": stop_reason,
            "prompt_tokens": prompt_tokens_for_marker,
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
            prompt_tokens=prompt_tokens_for_marker,
            planned_output_tokens=item.shape.planned_output_tokens,
            emitted_tokens=emitted_tokens,
            prompt_hash=prompt_hash,
            output=output,
            backend_metadata={
                "sampler_provenance": sampler_provenance,
                "sampler_recorded": sampler_recorded,
            },
        )

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
        position: int | None = None,
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
            prefill_metadata.update(
                {"item_id": item_id, "item_index": item_index, "position": position}
            )
        events.append(
            self._event(
                "phase_start",
                "prefill",
                "mlx prefill started",
                prefill_metadata,
            )
        )
        token_records: list[dict[str, float | int]] = []
        output_token_ids: list[int] = []
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
                            {
                                "item_id": item_id,
                                "item_index": item_index,
                                "position": position,
                            }
                        )
                        decode_start_metadata.update(
                            {
                                "item_id": item_id,
                                "item_index": item_index,
                                "position": position,
                            }
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
                token_id = _response_token_id(response)
                output_token_ids.append(token_id)
                token_metadata: dict[str, Any] = {"index": index}
                if item_id is not None:
                    token_metadata.update(
                        {"item_id": item_id, "item_index": item_index, "position": position}
                    )
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
                token_records.append(
                    {"index": index, "timestamp_s": timestamp_s, "token_id": token_id}
                )
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
            output_token_ids=output_token_ids,
        )

    def cleanup(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> AdapterResult:
        metadata = {"memory_snapshots": [self._memory_snapshot("cleanup_start")]}
        self._model = None
        self._tokenizer = None
        self._model_config = None
        self._mlx_lm = None
        self._model_artifact_identity = None
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
    ) -> tuple[list[int], list[int], str | None, str, bool]:
        if item.source.prompt_text is not None:
            token_ids = _encode(self._tokenizer, item.source.prompt_text, add_special_tokens=True)
            return (
                token_ids,
                token_ids,
                item.source.prompt_text,
                "prompt_text",
                _bos_present(self._tokenizer, token_ids, add_special_tokens=True),
            )
        if item.source.prompt_token_ids is not None:
            token_ids = list(item.source.prompt_token_ids)
            return token_ids, token_ids, None, "token_ids", False
        token_ids = _synthetic_prompt_tokens(
            self._tokenizer,
            item.shape.planned_prompt_tokens,
        )
        return token_ids, token_ids, None, "synthetic", False

    def _sampler_for_generation(self) -> tuple[Any | None, dict[str, Any]]:
        base = {
            "kind": "greedy",
            "temperature": 0.0,
        }
        if not self._stream_generate_accepts_sampler():
            self._raise_sampler_pin_failure("mlx_lm stream_generate sampler API unavailable")
        make_sampler = getattr(self._mlx_lm, "make_sampler", None)
        sampler_api = "mlx_lm.make_sampler"
        if not callable(make_sampler):
            # Installed mlx_lm exposes make_sampler under sample_utils, not
            # top-level (verified live 2026-07-08); check both homes.
            sample_utils = getattr(self._mlx_lm, "sample_utils", None)
            make_sampler = getattr(sample_utils, "make_sampler", None)
            sampler_api = "mlx_lm.sample_utils.make_sampler"
        if not callable(make_sampler):
            self._raise_sampler_pin_failure("mlx_lm sampler API unavailable")
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
                self._raise_sampler_pin_failure(
                    f"mlx_lm sampler API unavailable: {type(exc).__name__}: {exc}"
                )
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
            self._raise_sampler_pin_failure(
                f"mlx_lm sampler API unavailable: {type(exc).__name__}: {exc}"
            )
        self._raise_sampler_pin_failure(
            "mlx_lm sampler API unavailable",
            errors=errors,
        )

    @staticmethod
    def _raise_sampler_pin_failure(reason: str, *, errors: list[str] | None = None) -> None:
        metadata: dict[str, Any] = {
            "error": "sampler_pin_unverified",
            "kind": "greedy",
            "temperature": 0.0,
            "pinned": False,
            "reason": reason,
        }
        if errors:
            metadata["errors"] = list(errors)
        raise AdapterFailure(
            FailureReason.RUNTIME_UNAVAILABLE,
            f"sampler_pin_unverified: {reason}",
            metadata=metadata,
        )

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


class _SuiteItemMalformed(Exception):
    pass


def _response_token_id(response: Any) -> int:
    for attr in ("token", "token_id", "id"):
        value = getattr(response, attr, None)
        if isinstance(value, bool):
            continue
        try:
            return operator.index(value)
        except TypeError:
            pass
    raise AdapterFailure(
        FailureReason.RUNTIME_UNAVAILABLE,
        "output_token_id_unavailable: mlx_lm stream response did not expose an integer token id",
    )


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
    if suite_identity == "affine":
        return {**annotation, "severity": "advisory"}
    return {**annotation, "severity": "advisory"}


def _bos_present(tokenizer: Any, token_ids: list[int], *, add_special_tokens: bool) -> bool:
    if not add_special_tokens or not token_ids:
        return False
    try:
        bos_token_id = getattr(tokenizer, "bos_token_id")
    except Exception:  # noqa: BLE001 - wrappers may forward oddly
        bos_token_id = None
    if isinstance(bos_token_id, int) and not isinstance(bos_token_id, bool):
        return token_ids[0] == bos_token_id
    # Honest proxy when the tokenizer does not expose BOS identity: record the
    # encode mode that asked the tokenizer to prepend adapter-normal specials.
    return True


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
    global _MLX_CORE_MODULE

    unavailable = {
        "api_available": False,
        "active_memory_bytes": None,
        "cache_memory_bytes": None,
        "peak_memory_bytes": None,
    }
    try:
        # ``sys.modules`` stays authoritative so a test that installs a stand-in
        # under "mlx.core" still gets its stand-in. The fallback below is only
        # for the case a stand-in cannot create: the real extension already
        # loaded into this process but evicted from ``sys.modules``.
        mx = sys.modules.get("mlx.core")
        if mx is None:
            mx = _MLX_CORE_MODULE
        if mx is None:
            # Only a module WE imported is remembered; caching whatever happens
            # to sit in ``sys.modules`` would let a test stand-in outlive its
            # own patch and silently supply memory numbers to real evidence.
            mx = importlib.import_module("mlx.core")
            _MLX_CORE_MODULE = mx
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
