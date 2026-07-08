"""MLX runtime adapter for local Apple Silicon generation (Slice 2G).

The core package remains stdlib-only: this module is importable without MLX,
and ``mlx_lm`` is imported only inside ``prepare``. Tests exercise the workload
mapping and event shape with fakes, while real runs use the same adapter path.
"""

from __future__ import annotations

import importlib
import json
import os
import subprocess
from collections.abc import Iterable
from importlib import metadata as importlib_metadata
from pathlib import Path
from typing import Any

from joulewise.clock import Clock
from joulewise.interfaces import AdapterResult, RunContext, RuntimeEvent, RuntimeResult
from joulewise.provenance import output_policy, prompt_provenance
from joulewise.schemas import BenchmarkConfig, FailureReason

DEFAULT_OUTPUT_TOKENS = 8
WARMUP_TOKENS = 4
SYNTHETIC_PROMPT_SEED = "JouleWise synthetic prompt token sequence."


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

        events: list[RuntimeEvent] = [
            self._event("phase_start", "tokenize", "mlx tokenization started")
        ]
        prompt, prompt_token_ids, prompt_text = self._prompt_for_workload(config)
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
        max_tokens = config.workload_profile.output_tokens or DEFAULT_OUTPUT_TOKENS
        original_eos_ids = self._suppress_eos()
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
        events.append(
            self._event(
                "phase_start",
                "prefill",
                "mlx prefill started",
                {
                    "phase_boundary_method": "first_token",
                    "prompt_tokens": prompt_tokens,
                    "requested_output_tokens": max_tokens,
                    "eos_suppressed": eos_suppressed,
                },
            )
        )
        token_records: list[dict[str, float | int]] = []
        text_parts: list[str] = []
        last_finish_reason: str | None = None

        try:
            stream = self._mlx_lm.stream_generate(
                self._model,
                self._tokenizer,
                prompt,
                max_tokens=max_tokens,
            )
            for index, response in enumerate(stream):
                if index == 0:
                    events.append(
                        self._event(
                            "phase_end",
                            "prefill",
                            "mlx prefill completed",
                            {"phase_boundary_method": "first_token"},
                        )
                    )
                    events.append(
                        self._event(
                            "phase_start",
                            "decode",
                            "mlx decode started",
                            {
                                "phase_boundary_method": "first_token",
                                "max_tokens": max_tokens,
                                "eos_suppressed": eos_suppressed,
                                "original_eos_token_ids": (
                                    sorted(original_eos_ids)
                                    if original_eos_ids is not None
                                    else None
                                ),
                            },
                        )
                    )
                timestamp_s = self._clock.now()
                text_parts.append(str(getattr(response, "text", "")))
                finish_reason = getattr(response, "finish_reason", None)
                if isinstance(finish_reason, str):
                    last_finish_reason = finish_reason
                events.append(
                    RuntimeEvent(
                        timestamp_s=timestamp_s,
                        event_type="token",
                        phase="decode",
                        message=f"mlx token {index}",
                        metadata={"index": index},
                    )
                )
                token_records.append({"index": index, "timestamp_s": timestamp_s})
        finally:
            self._restore_eos(original_eos_ids)

        if not token_records:
            boundary_event = self._event(
                "phase_end",
                "prefill",
                "mlx prefill completed without emitted tokens",
                {"phase_boundary_method": "first_token"},
            )
            events.append(boundary_event)
            events.append(
                RuntimeEvent(
                    timestamp_s=boundary_event.timestamp_s,
                    event_type="phase_start",
                    phase="decode",
                    message="mlx decode started without emitted tokens",
                    metadata={
                        "phase_boundary_method": "first_token",
                        "max_tokens": max_tokens,
                        "eos_suppressed": eos_suppressed,
                    },
                )
            )

        events.append(
            self._event(
                "phase_end",
                "decode",
                "mlx decode completed",
                {
                    "phase_boundary_method": "first_token",
                    "emitted_tokens": len(token_records),
                    "requested_output_tokens": max_tokens,
                },
            )
        )

        response_text = "".join(text_parts)
        tokens_jsonl = "".join(
            json.dumps(record, sort_keys=True) + "\n" for record in token_records
        )
        output_tokens = len(token_records)
        stop_condition = (
            "requested_tokens_emitted"
            if output_tokens == max_tokens
            else last_finish_reason or "stream_exhausted"
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
                "prompt": prompt_provenance(prompt_token_ids, text=prompt_text),
                "generator": {
                    "name": "mlx_lm.stream_generate",
                    "version": _module_or_distribution_version(self._mlx_lm, "mlx-lm"),
                },
                "tokenizer": _tokenizer_identity(self._tokenizer, config),
                "model": {
                    "source": config.model.source,
                    "revision": config.model.revision,
                },
                "output_policy": output_policy(
                    "fixed_budget_exact",
                    requested_tokens=max_tokens,
                    emitted_tokens=output_tokens,
                    stop_condition=stop_condition,
                ),
            },
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
        raise RuntimeError("workload_profile must define prompt_text, prompt_tokens, or dataset_ref")

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
    return result
