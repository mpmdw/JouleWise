#!/usr/bin/env python3
"""Pinned mlx-lm speculative-decode/MTP feasibility probe.

The controller is standard-library-only.  MLX import, model load, and external
draft execution happen in a captured child process so a missing Metal device,
missing artifact, pin mismatch, or worker failure remains machine-readable
JSONL evidence.  The controller suppresses the worker's verdict and re-derives
the final result from identity-anchored evidence.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.metadata
import inspect
import io
import json
import math
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCHEMA = "joulewise.axi_sc_spec_decode_spike.v1"
EXPECTED_MLX_LM = "0.31.3"
EXPECTED_MLX = "0.31.2"
EXPECTED_GENERATE_SHA256 = (
    "270778ad53eaca55a8533d82e6752660fe5d2605c4aa0879b48a50a91f69345f"
)
EXPECTED_QWEN35_SHA256 = (
    "f0daa30bba5cb521c8bdfa7093101a544c6a37bbba09bca582288219cb04ae3a"
)
DEFAULT_TARGET_MODEL = (
    "/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit"
)
EXPECTED_DRAFT_MODEL = (
    "/Users/edr/jw_models/mlx-community/Qwen2.5-0.5B-Instruct-4bit"
)
NATIVE_MTP_CANDIDATE = (
    "/Users/edr/jw_models/mlx-community/Qwen3.5-122B-A10B-4bit"
)
DEFAULT_PROMPT = "State one reason to preserve proposal counters."
REQUEST_ID = "axi-sc-000"
WEIGHT_SUFFIXES = (".safetensors", ".bin", ".pt", ".pth", ".npz", ".gguf")
SPECULATIVE_DECODE_CALLBACK = "speculative_decode_callback"
RUNTIME_CALLBACK_SOURCE = "mlx_lm.speculative_decode_callback"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def json_line(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class Emitter:
    def __init__(self, stream: Any = None) -> None:
        self.stream = stream if stream is not None else sys.stdout
        self.sequence = 0

    def emit(self, event: str, **payload: Any) -> dict[str, Any]:
        row = {
            "schema": SCHEMA,
            "sequence": self.sequence,
            "event": event,
            "recorded_at_utc": utc_now(),
            **payload,
        }
        self.sequence += 1
        print(json_line(row), file=self.stream, flush=True)
        return row


def _safe_error(exc: BaseException) -> dict[str, str]:
    return {"type": type(exc).__name__, "message": str(exc)[:1000]}


def _diagnostic_tail(value: str | bytes, limit: int = 2000) -> str | None:
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="replace")
    value = value.strip()
    return value[-limit:] if value else None


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_path(value: str) -> str:
    return str(Path(value).expanduser().resolve(strict=False))


def _prompt_sha256(prompt: str) -> str:
    return hashlib.sha256(
        b"joulewise.axi_sc_prompt.v1\0" + prompt.encode("utf-8")
    ).hexdigest()


def output_ids_sha256(token_ids: Sequence[int]) -> str:
    preimage = b"joulewise.request_output_token_ids.v1\n" + json.dumps(
        list(token_ids), separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(preimage).hexdigest()


def _distribution_record(name: str) -> dict[str, Any]:
    try:
        distribution = importlib.metadata.distribution(name)
        top_level = "mlx_lm" if name == "mlx-lm" else "mlx"
        return {
            "name": name,
            "version": distribution.version,
            "package_root": str(Path(distribution.locate_file(top_level)).resolve()),
        }
    except importlib.metadata.PackageNotFoundError:
        return {"name": name, "version": None, "package_root": None}


def _source_surface_record(package_root: str | None) -> dict[str, Any]:
    if not package_root:
        return {
            "available": False,
            "reason": "mlx_lm_package_root_missing",
            "generate_path": None,
            "generate_sha256": None,
            "qwen3_5_path": None,
            "qwen3_5_sha256": None,
        }
    root = Path(package_root)
    generate_path = root / "generate.py"
    qwen_path = root / "models" / "qwen3_5.py"
    try:
        generate_text = generate_path.read_text(encoding="utf-8")
        qwen_text = qwen_path.read_text(encoding="utf-8")
        generate_sha = hashlib.sha256(generate_text.encode("utf-8")).hexdigest()
        qwen_sha = hashlib.sha256(qwen_text.encode("utf-8")).hexdigest()
    except OSError as exc:
        return {
            "available": False,
            "reason": "installed_source_unreadable",
            "error": _safe_error(exc),
            "generate_path": str(generate_path),
            "generate_sha256": None,
            "qwen3_5_path": str(qwen_path),
            "qwen3_5_sha256": None,
        }
    return {
        "available": True,
        "reason": None,
        "generate_path": str(generate_path),
        "generate_sha256": generate_sha,
        "generate_sha256_expected": EXPECTED_GENERATE_SHA256,
        "qwen3_5_path": str(qwen_path),
        "qwen3_5_sha256": qwen_sha,
        "qwen3_5_sha256_expected": EXPECTED_QWEN35_SHA256,
        "external_draft_generation_surface": all(
            marker in generate_text
            for marker in (
                "def speculative_generate_step(",
                "draft_model: Optional[nn.Module] = None",
                "num_draft_tokens",
            )
        ),
        "accepted_token_marker_surface": "from_draft: bool" in generate_text,
        "tokens_proposed_callback_surface": "tokens_proposed" in generate_text,
        "decode_emission_callback_surface": "decode_emission" in generate_text,
        "native_mtp_generation_surface": any(
            marker in generate_text
            for marker in ("native_mtp", "native_mtp_generate", "mtp_generate")
        ),
        "qwen35_mtp_weights_discarded": (
            'if "mtp." not in k' in qwen_text
            and 'has_mtp_weights = any("mtp." in k' in qwen_text
        ),
    }


def _source_surface_matches_pin(surface: Mapping[str, Any]) -> bool:
    return (
        surface.get("available") is True
        and surface.get("generate_sha256") == EXPECTED_GENERATE_SHA256
        and surface.get("qwen3_5_sha256") == EXPECTED_QWEN35_SHA256
        and surface.get("external_draft_generation_surface") is True
        and surface.get("accepted_token_marker_surface") is True
        and surface.get("tokens_proposed_callback_surface") is False
        and surface.get("decode_emission_callback_surface") is False
        and surface.get("native_mtp_generation_surface") is False
        and surface.get("qwen35_mtp_weights_discarded") is True
    )


def _read_config(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    config_path = path / "config.json"
    try:
        raw = config_path.read_bytes()
        value = json.loads(raw)
    except (OSError, json.JSONDecodeError):
        return None, None
    if not isinstance(value, dict):
        return None, None
    return value, hashlib.sha256(raw).hexdigest()


def _artifact_record(role: str, value: str) -> dict[str, Any]:
    path = Path(value).expanduser()
    resolved = Path(_canonical_path(value))
    config, config_sha = _read_config(resolved)
    text_config = config.get("text_config", {}) if isinstance(config, dict) else {}
    if not isinstance(text_config, dict):
        text_config = {}
    vocab_size = None
    if isinstance(config, dict):
        vocab_size = config.get("vocab_size", text_config.get("vocab_size"))
    return {
        "role": role,
        "requested_path": str(path),
        "resolved_path": str(resolved),
        "directory_present": resolved.is_dir(),
        "config_present": (resolved / "config.json").is_file(),
        "config_sha256": config_sha,
        "model_type": config.get("model_type") if isinstance(config, dict) else None,
        "vocabulary_size": vocab_size,
        "quantization": config.get("quantization") if isinstance(config, dict) else None,
        "native_mtp_candidate_config": {
            "mtp_num_hidden_layers": text_config.get("mtp_num_hidden_layers"),
            "mtp_use_dedicated_embeddings": text_config.get(
                "mtp_use_dedicated_embeddings"
            ),
        },
    }


def _folded_model_artifact_sha256(root: Path) -> tuple[str | None, dict[str, str]]:
    try:
        weight_files = sorted(
            child
            for child in root.rglob("*")
            if child.is_file() and child.name.endswith(WEIGHT_SUFFIXES)
        )
    except OSError:
        return None, {}
    file_hashes: dict[str, str] = {}
    try:
        for child in weight_files:
            file_hashes[child.relative_to(root).as_posix()] = _sha256_file(child)
    except OSError:
        return None, {}
    if not file_hashes:
        return None, {}
    canonical = json.dumps(file_hashes, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(
        b"joulewise.model_artifact_identity.v1\0" + canonical.encode("utf-8")
    ).hexdigest()
    return digest, file_hashes


def _requested_parameters(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "mode": args.mode,
        "request_id": REQUEST_ID,
        "target_model_path": _canonical_path(args.target_model),
        "draft_model_path": (
            _canonical_path(args.draft_model) if args.draft_model is not None else None
        ),
        "max_proposed_tokens": args.max_proposed_tokens,
        "max_tokens": args.max_tokens,
        "prompt_sha256": _prompt_sha256(args.prompt),
    }


def _params_match(row: Mapping[str, Any], requested: Mapping[str, Any]) -> bool:
    return all(row.get(key) == value for key, value in requested.items())


def _is_nonbool_int(value: Any, minimum: int = 0) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= minimum


def _is_finite_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def _rates_match(left: Any, right: Any) -> bool:
    return (
        _is_finite_number(left)
        and _is_finite_number(right)
        and math.isclose(float(left), float(right), rel_tol=1e-12, abs_tol=1e-12)
    )


def _draft_identity_is_complete(
    value: Any, requested: Mapping[str, Any], draft_artifact_sha256: str | None
) -> bool:
    if not isinstance(value, Mapping) or draft_artifact_sha256 is None:
        return False
    if set(value) != {
        "model_name",
        "model_revision",
        "model_artifact_sha256",
        "weight_format",
        "quantization",
        "runtime_backend",
        "runtime_version",
        "tokenizer",
    }:
        return False
    tokenizer = value.get("tokenizer")
    return (
        value.get("model_name") == Path(str(requested["draft_model_path"])).name
        and isinstance(value.get("model_revision"), str)
        and bool(value.get("model_revision"))
        and value.get("model_artifact_sha256") == draft_artifact_sha256
        and isinstance(value.get("weight_format"), str)
        and bool(value.get("weight_format"))
        and isinstance(value.get("quantization"), str)
        and bool(value.get("quantization"))
        and value.get("runtime_backend") == "mlx-lm"
        and value.get("runtime_version") == EXPECTED_MLX_LM
        and isinstance(tokenizer, Mapping)
        and set(tokenizer) == {"name", "revision", "class", "vocabulary_size"}
        and all(
            isinstance(tokenizer.get(key), str) and bool(tokenizer.get(key))
            for key in ("name", "revision", "class")
        )
        and _is_nonbool_int(tokenizer.get("vocabulary_size"), 1)
    )


def _matching_rows(
    rows: Sequence[Mapping[str, Any]], event: str, requested: Mapping[str, Any]
) -> list[Mapping[str, Any]]:
    return [
        row
        for row in rows
        if row.get("event") == event and _params_match(row, requested)
    ]


def _runtime_generation_evidence(
    rows: Sequence[Mapping[str, Any]],
    observation: Mapping[str, Any],
    requested: Mapping[str, Any],
    draft_artifact_sha256: str | None,
) -> tuple[bool, bool]:
    """Return (generation_observed, lifecycle_and_output_consistent)."""

    if not _params_match(observation, requested):
        return False, False
    mode = requested["mode"]
    if mode == "native_mtp":
        generation = (
            observation.get("runtime_generation_supported") is True
            and observation.get("native_mtp_execution_observed") is True
            and observation.get("draft_model_identity") is None
            and isinstance(observation.get("native_mtp_identity"), Mapping)
        )
        return generation, generation

    loaded_target = _matching_rows(rows, "model_loaded", requested)
    loaded_draft = [
        row
        for row in loaded_target
        if row.get("role") == "draft"
        and row.get("resolved_path") == requested["draft_model_path"]
    ]
    loaded_target = [
        row
        for row in loaded_target
        if row.get("role") == "target"
        and row.get("resolved_path") == requested["target_model_path"]
    ]
    generation = (
        observation.get("runtime_generation_supported") is True
        and observation.get("generation_completed") is True
        and observation.get("loaded_target_model_path")
        == requested["target_model_path"]
        and observation.get("loaded_draft_model_path")
        == requested["draft_model_path"]
        and observation.get("target_model_call_count", 0) > 0
        and observation.get("draft_model_call_count", 0) > 0
        and len(loaded_target) == 1
        and len(loaded_draft) == 1
        and _draft_identity_is_complete(
            observation.get("draft_model_identity"),
            requested,
            draft_artifact_sha256,
        )
        and observation.get("native_mtp_identity") is None
    )
    if not generation:
        return False, False

    submitted = _matching_rows(rows, "request_submitted", requested)
    admitted = _matching_rows(rows, "request_admitted", requested)
    terminals = _matching_rows(rows, "request_terminal", requested)
    generations = _matching_rows(rows, "generation_response", requested)
    if len(submitted) != 1 or len(admitted) != 1 or len(terminals) != 1:
        return True, False
    terminal = terminals[0]
    token_ids = [row.get("token_id") for row in generations]
    ordinals = [row.get("output_token_ordinal") for row in generations]
    accepted_count = sum(row.get("from_draft") is True for row in generations)
    valid_generation_rows = (
        bool(generations)
        and all(_is_nonbool_int(token, 0) for token in token_ids)
        and ordinals == list(range(len(generations)))
        and all(isinstance(row.get("from_draft"), bool) for row in generations)
    )
    expected_hash = output_ids_sha256(token_ids) if valid_generation_rows else None
    observation_tokens = observation.get("output_token_ids")
    accepted_source = observation.get("tokens_accepted_observation_source")
    terminal_consistent = (
        valid_generation_rows
        and observation_tokens == token_ids
        and observation.get("output_token_count") == len(token_ids)
        and observation.get("output_token_ids_sha256") == expected_hash
        and terminal.get("output_token_ids") == token_ids
        and terminal.get("output_token_count") == len(token_ids)
        and terminal.get("output_token_ids_sha256") == expected_hash
        and isinstance(terminal.get("stop_reason"), str)
        and bool(terminal.get("stop_reason"))
        and observation.get("tokens_accepted") == accepted_count
        and accepted_source
        in {"GenerationResponse.from_draft", RUNTIME_CALLBACK_SOURCE}
    )
    return True, terminal_consistent


def _claim_observability_evidence(
    rows: Sequence[Mapping[str, Any]],
    observation: Mapping[str, Any],
    requested: Mapping[str, Any],
) -> bool:
    """Validate exercised AXI-SA callback evidence; never infer it from a cap."""

    emissions = _matching_rows(rows, "decode_emission", requested)
    if (
        not emissions
        or observation.get("tokens_proposed_observation_source")
        != RUNTIME_CALLBACK_SOURCE
        or observation.get("tokens_accepted_observation_source")
        != RUNTIME_CALLBACK_SOURCE
        or observation.get("acceptance_rate_observation_source")
        != RUNTIME_CALLBACK_SOURCE
        or observation.get("decode_emission_observation_source")
        != RUNTIME_CALLBACK_SOURCE
        or observation.get("decode_emission_event_count") != len(emissions)
    ):
        return False
    proposed_total = 0
    accepted_total = 0
    emitted_total = 0
    emitted_token_ids: list[int] = []
    for ordinal, row in enumerate(emissions):
        proposed = row.get("tokens_proposed")
        accepted = row.get("tokens_accepted")
        emitted = row.get("emitted_count")
        target = row.get("target_emitted_count")
        token_slice = row.get("emitted_token_ids")
        running_proposed = proposed_total + proposed if _is_nonbool_int(proposed) else 0
        running_accepted = accepted_total + accepted if _is_nonbool_int(accepted) else 0
        expected_running_rate = (
            running_accepted / running_proposed if running_proposed else None
        )
        if not (
            row.get("decode_step_ordinal") == ordinal
            and row.get("counter_source") == RUNTIME_CALLBACK_SOURCE
            and row.get("acceptance_rate_source") == RUNTIME_CALLBACK_SOURCE
            and row.get("emission_boundary_source") == RUNTIME_CALLBACK_SOURCE
            and _is_nonbool_int(proposed, 1)
            and _is_nonbool_int(accepted)
            and _is_nonbool_int(emitted, 1)
            and _is_nonbool_int(target)
            and accepted <= proposed <= requested["max_proposed_tokens"]
            and emitted == accepted + target
            and isinstance(token_slice, list)
            and len(token_slice) == emitted
            and all(_is_nonbool_int(token) for token in token_slice)
            and _rates_match(
                row.get("aggregate_acceptance_rate"), expected_running_rate
            )
        ):
            return False
        proposed_total += proposed
        accepted_total += accepted
        emitted_total += emitted
        emitted_token_ids.extend(token_slice)
    expected_rate = accepted_total / proposed_total if proposed_total else None
    return (
        emitted_total == observation.get("output_token_count")
        and emitted_token_ids == observation.get("output_token_ids")
        and observation.get("tokens_proposed") == proposed_total
        and observation.get("tokens_accepted") == accepted_total
        and _rates_match(observation.get("acceptance_rate"), expected_rate)
        and observation.get("acceptance_rate_reason") is None
    )


def derive_evidence_verdict(
    rows: Sequence[Mapping[str, Any]],
    requested: Mapping[str, Any],
    draft_artifact_sha256: str | None,
) -> dict[str, Any]:
    """Reconstruct the semantic verdict from evidence anchored to the request."""

    observations = [row for row in rows if row.get("event") == "capability_observation"]
    if len(observations) != 1:
        return {
            "verdict": "unsupported_for_joulewise",
            "reason": (
                "native_mtp_generation"
                if requested["mode"] == "native_mtp"
                else "draft_model_generation"
            ),
            "runtime_generation_supported": False,
            "claim_instrumentable": False,
        }
    observation = observations[0]
    if not _params_match(observation, requested):
        return {
            "verdict": "runtime_unavailable",
            "reason": "evidence_verdict_mismatch",
            "runtime_generation_supported": False,
            "claim_instrumentable": False,
        }
    generation, lifecycle_consistent = _runtime_generation_evidence(
        rows, observation, requested, draft_artifact_sha256
    )
    if not generation:
        return {
            "verdict": "unsupported_for_joulewise",
            "reason": (
                "native_mtp_generation"
                if requested["mode"] == "native_mtp"
                else "draft_model_generation"
            ),
            "runtime_generation_supported": False,
            "claim_instrumentable": False,
        }
    observable = lifecycle_consistent and _claim_observability_evidence(
        rows, observation, requested
    )
    if not observable:
        return {
            "verdict": "unsupported_for_joulewise",
            "reason": "event_observability",
            "runtime_generation_supported": True,
            "claim_instrumentable": False,
        }
    return {
        "verdict": "supported",
        "reason": None,
        "runtime_generation_supported": True,
        "claim_instrumentable": True,
    }


class ModelCallObserver:
    """Transparent model proxy recording calls to target or draft model."""

    def __init__(self, model: Any) -> None:
        self.model = model
        self.calls: list[dict[str, Any]] = []

    def __getattr__(self, name: str) -> Any:
        return getattr(self.model, name)

    def __call__(self, inputs: Any, *args: Any, **kwargs: Any) -> Any:
        shape = None
        try:
            shape = [int(value) for value in inputs.shape]
        except (AttributeError, TypeError, ValueError):
            pass
        started = time.perf_counter()
        result = self.model(inputs, *args, **kwargs)
        self.calls.append(
            {
                "call_index": len(self.calls),
                "input_shape": shape,
                "started_at_s": started,
                "returned_at_s": time.perf_counter(),
            }
        )
        return result


def _worker_emit(stream: Any, event: str, **payload: Any) -> None:
    print(json_line({"event": event, **payload}), file=stream, flush=True)


def _worker_outcome(
    stream: Any,
    verdict: str,
    reason: str | None,
    *,
    stage: str,
    error: BaseException | None = None,
) -> int:
    payload: dict[str, Any] = {"verdict": verdict, "reason": reason, "stage": stage}
    if error is not None:
        payload["error"] = _safe_error(error)
    _worker_emit(stream, "probe_outcome", **payload)
    return 0


def _tokenizer_vocabulary_size(tokenizer: Any) -> int | None:
    value = getattr(tokenizer, "vocab_size", None)
    return int(value) if _is_nonbool_int(value, 1) else None


def _draft_model_identity(
    args: argparse.Namespace, tokenizer: Any
) -> dict[str, Any]:
    name = Path(args.draft_model).name
    vocabulary_size = _tokenizer_vocabulary_size(tokenizer)
    tokenizer_name = getattr(tokenizer, "name_or_path", None) or name
    tokenizer_class = type(tokenizer).__name__
    quantization = args._draft_quantization or "none"
    weight_format = args._draft_weight_format or "unknown"
    return {
        "model_name": name,
        "model_revision": f"local-artifact-sha256:{args._draft_artifact_sha256}",
        "model_artifact_sha256": args._draft_artifact_sha256,
        "weight_format": weight_format,
        "quantization": quantization,
        "runtime_backend": "mlx-lm",
        "runtime_version": EXPECTED_MLX_LM,
        "tokenizer": {
            "name": str(tokenizer_name),
            "revision": f"local-config-sha256:{args._draft_config_sha256}",
            "class": tokenizer_class,
            "vocabulary_size": vocabulary_size,
        },
    }


def _has_explicit_runtime_callback(stream_generate: Any) -> bool:
    """Return true only for an explicit callback parameter, never bare **kwargs."""

    try:
        parameters = inspect.signature(stream_generate).parameters
    except (TypeError, ValueError):
        return False
    parameter = parameters.get(SPECULATIVE_DECODE_CALLBACK)
    return parameter is not None and parameter.kind in {
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        inspect.Parameter.KEYWORD_ONLY,
    }


def _callback_event_payload(
    args: Sequence[Any], kwargs: Mapping[str, Any]
) -> dict[str, Any]:
    """Normalize one exercised runtime callback without deriving missing fields."""

    value: Mapping[str, Any]
    if len(args) == 1 and isinstance(args[0], Mapping) and not kwargs:
        value = args[0]
    elif not args:
        value = kwargs
    else:
        value = {}
    token_slice = value.get("emitted_token_ids")
    normalized_slice = (
        [int(token) for token in token_slice]
        if isinstance(token_slice, (list, tuple))
        and all(_is_nonbool_int(token) for token in token_slice)
        else None
    )
    integer_fields = {
        name: int(value[name]) if _is_nonbool_int(value.get(name)) else None
        for name in (
            "decode_step_ordinal",
            "tokens_proposed",
            "tokens_accepted",
            "target_emitted_count",
            "emitted_count",
        )
    }
    acceptance_rate = value.get("aggregate_acceptance_rate")
    return {
        **integer_fields,
        "aggregate_acceptance_rate": (
            float(acceptance_rate) if _is_finite_number(acceptance_rate) else None
        ),
        "emitted_token_ids": normalized_slice,
        "counter_source": RUNTIME_CALLBACK_SOURCE,
        "acceptance_rate_source": RUNTIME_CALLBACK_SOURCE,
        "emission_boundary_source": RUNTIME_CALLBACK_SOURCE,
    }


def _callback_totals(
    events: Sequence[Mapping[str, Any]],
) -> tuple[int | None, int | None, float | int | None]:
    """Expose callback totals only when every required counter/rate is present."""

    if not events:
        return None, None, None
    proposed = [event.get("tokens_proposed") for event in events]
    accepted = [event.get("tokens_accepted") for event in events]
    rate = events[-1].get("aggregate_acceptance_rate")
    if (
        not all(_is_nonbool_int(value, 1) for value in proposed)
        or not all(_is_nonbool_int(value) for value in accepted)
        or not _is_finite_number(rate)
    ):
        return None, None, None
    return sum(proposed), sum(accepted), rate


def runtime_worker(args: argparse.Namespace) -> int:
    """Run the Metal/runtime work inside the captured child process."""

    evidence_stream = sys.stdout
    captured_stdout = io.StringIO()
    captured_stderr = io.StringIO()
    requested = _requested_parameters(args)
    try:
        with contextlib.redirect_stdout(captured_stdout), contextlib.redirect_stderr(
            captured_stderr
        ):
            import mlx.core as mx
            import mlx_lm
    except BaseException as exc:  # MLX import can fail before ordinary imports finish.
        return _worker_outcome(
            evidence_stream,
            "runtime_unavailable",
            "runtime_import_failed",
            stage="runtime_import",
            error=exc,
        )

    try:
        metal_available = bool(mx.metal.is_available())
    except BaseException as exc:
        return _worker_outcome(
            evidence_stream,
            "runtime_unavailable",
            "metal_probe_failed",
            stage="metal_probe",
            error=exc,
        )
    _worker_emit(evidence_stream, "metal_probe", metal_available=metal_available)
    if not metal_available:
        return _worker_outcome(
            evidence_stream,
            "runtime_unavailable",
            "metal_unavailable",
            stage="metal_probe",
        )

    if args.mode == "native_mtp":
        _worker_emit(
            evidence_stream,
            "capability_observation",
            **requested,
            runtime_available=True,
            runtime_generation_supported=False,
            native_mtp_execution_observed=False,
            native_mtp_failure_reason="pinned_runtime_has_no_native_mtp_generation_surface",
            generation_completed=False,
            loaded_target_model_path=None,
            loaded_draft_model_path=None,
            target_model_call_count=0,
            draft_model_call_count=0,
            draft_model_identity=None,
            native_mtp_identity=None,
            tokens_proposed=None,
            tokens_accepted=None,
            acceptance_rate=None,
            decode_emission_event_count=0,
        )
        return _worker_outcome(
            evidence_stream,
            "unsupported_for_joulewise",
            "native_mtp_generation",
            stage="runtime_surface",
        )

    try:
        with contextlib.redirect_stdout(captured_stdout), contextlib.redirect_stderr(
            captured_stderr
        ):
            target_model, target_tokenizer = mlx_lm.load(args.target_model)
            draft_model, draft_tokenizer = mlx_lm.load(args.draft_model)
    except BaseException as exc:
        return _worker_outcome(
            evidence_stream,
            "runtime_unavailable",
            "model_load_failed",
            stage="model_load",
            error=exc,
        )

    target_vocab = _tokenizer_vocabulary_size(target_tokenizer)
    draft_vocab = _tokenizer_vocabulary_size(draft_tokenizer)
    if target_vocab is None or draft_vocab is None or target_vocab != draft_vocab:
        return _worker_outcome(
            evidence_stream,
            "runtime_unavailable",
            "draft_tokenizer_mismatch",
            stage="tokenizer_compatibility",
        )

    target_observer = ModelCallObserver(target_model)
    draft_observer = ModelCallObserver(draft_model)
    callback_available = _has_explicit_runtime_callback(mlx_lm.stream_generate)
    callback_events: list[dict[str, Any]] = []

    def speculative_decode_callback(
        *callback_args: Any, **callback_kwargs: Any
    ) -> None:
        payload = _callback_event_payload(callback_args, callback_kwargs)
        event = {"event": "decode_emission", **requested, **payload}
        callback_events.append(event)
        _worker_emit(evidence_stream, "decode_emission", **requested, **payload)

    _worker_emit(
        evidence_stream,
        "runtime_observability_surface",
        **requested,
        callback_parameter=SPECULATIVE_DECODE_CALLBACK,
        callback_parameter_explicit=callback_available,
        required_callback_fields=[
            "decode_step_ordinal",
            "tokens_proposed",
            "tokens_accepted",
            "aggregate_acceptance_rate",
            "target_emitted_count",
            "emitted_count",
            "emitted_token_ids",
        ],
    )
    for role, path in (
        ("target", requested["target_model_path"]),
        ("draft", requested["draft_model_path"]),
    ):
        _worker_emit(
            evidence_stream,
            "model_loaded",
            **requested,
            role=role,
            resolved_path=path,
        )
    submitted_at = time.perf_counter()
    _worker_emit(
        evidence_stream,
        "request_submitted",
        **requested,
        timestamp_s=submitted_at,
    )
    admitted_at = time.perf_counter()
    _worker_emit(
        evidence_stream,
        "request_admitted",
        **requested,
        timestamp_s=admitted_at,
    )

    token_ids: list[int] = []
    accepted_flags: list[bool] = []
    stop_reason: str | None = None
    generation_completed = False
    try:
        with contextlib.redirect_stdout(captured_stdout), contextlib.redirect_stderr(
            captured_stderr
        ):
            generation_kwargs = {
                "max_tokens": args.max_tokens,
                "draft_model": draft_observer,
                "num_draft_tokens": args.max_proposed_tokens,
            }
            if callback_available:
                generation_kwargs[SPECULATIVE_DECODE_CALLBACK] = (
                    speculative_decode_callback
                )
            responses = mlx_lm.stream_generate(
                target_observer,
                target_tokenizer,
                args.prompt,
                **generation_kwargs,
            )
            for response in responses:
                timestamp = time.perf_counter()
                token_id = int(response.token)
                from_draft = bool(response.from_draft)
                token_ids.append(token_id)
                accepted_flags.append(from_draft)
                if response.finish_reason is not None:
                    stop_reason = str(response.finish_reason)
                _worker_emit(
                    evidence_stream,
                    "generation_response",
                    **requested,
                    output_token_ordinal=len(token_ids) - 1,
                    token_id=token_id,
                    from_draft=from_draft,
                    finish_reason=response.finish_reason,
                    timestamp_s=timestamp,
                    observation_source="GenerationResponse",
                )
        generation_completed = True
    except BaseException as exc:
        _worker_emit(
            evidence_stream,
            "capability_observation",
            **requested,
            runtime_available=True,
            runtime_generation_supported=False,
            native_mtp_execution_observed=False,
            generation_completed=False,
            loaded_target_model_path=requested["target_model_path"],
            loaded_draft_model_path=requested["draft_model_path"],
            target_model_call_count=len(target_observer.calls),
            draft_model_call_count=len(draft_observer.calls),
            draft_model_identity=_draft_model_identity(args, draft_tokenizer),
            native_mtp_identity=None,
            output_token_ids=token_ids,
            output_token_count=len(token_ids),
            output_token_ids_sha256=output_ids_sha256(token_ids),
            tokens_proposed=None,
            tokens_accepted=sum(accepted_flags),
            acceptance_rate=None,
            decode_emission_event_count=0,
            error=_safe_error(exc),
        )
        return _worker_outcome(
            evidence_stream,
            "unsupported_for_joulewise",
            "draft_model_generation",
            stage="generation",
            error=exc,
        )

    if stop_reason is None:
        stop_reason = "generator_exhausted"
    identity = _draft_model_identity(args, draft_tokenizer)
    callback_proposed, callback_accepted, callback_rate = _callback_totals(
        callback_events
    )
    callback_complete = (
        callback_proposed is not None
        and callback_accepted is not None
        and callback_rate is not None
    )
    observed_accepted = (
        callback_accepted if callback_complete else sum(accepted_flags)
    )
    accepted_source = (
        RUNTIME_CALLBACK_SOURCE
        if callback_complete
        else "GenerationResponse.from_draft"
    )
    terminal_at = time.perf_counter()
    _worker_emit(
        evidence_stream,
        "request_terminal",
        **requested,
        output_token_ids=token_ids,
        output_token_count=len(token_ids),
        output_token_ids_sha256=output_ids_sha256(token_ids),
        stop_reason=stop_reason,
        terminal_timestamp_s=terminal_at,
    )
    capability_observation = {
        "event": "capability_observation",
        **requested,
        "runtime_available": True,
        "runtime_generation_supported": (
            generation_completed
            and bool(token_ids)
            and bool(target_observer.calls)
            and bool(draft_observer.calls)
        ),
        "runtime_generation_evidence_source": (
            "target_and_draft_model_call_observers_plus_stream_generate"
        ),
        "native_mtp_execution_observed": False,
        "generation_completed": generation_completed,
        "loaded_target_model_path": requested["target_model_path"],
        "loaded_draft_model_path": requested["draft_model_path"],
        "target_model_call_count": len(target_observer.calls),
        "draft_model_call_count": len(draft_observer.calls),
        "target_model_calls": target_observer.calls,
        "draft_model_calls": draft_observer.calls,
        "draft_model_identity": identity,
        "native_mtp_identity": None,
        "output_token_ids": token_ids,
        "output_token_count": len(token_ids),
        "output_token_ids_sha256": output_ids_sha256(token_ids),
        "tokens_proposed": callback_proposed,
        "tokens_proposed_observation_source": (
            RUNTIME_CALLBACK_SOURCE if callback_complete else None
        ),
        "tokens_accepted": observed_accepted,
        "tokens_accepted_observation_source": accepted_source,
        "acceptance_rate": callback_rate,
        "acceptance_rate_observation_source": (
            RUNTIME_CALLBACK_SOURCE if callback_complete else None
        ),
        "acceptance_rate_reason": (
            None if callback_complete else "tokens_proposed_unavailable"
        ),
        "decode_emission_event_count": len(callback_events),
        "decode_emission_observation_source": (
            RUNTIME_CALLBACK_SOURCE if callback_events else None
        ),
    }
    _worker_emit(
        evidence_stream,
        "capability_observation",
        **{
            key: value
            for key, value in capability_observation.items()
            if key != "event"
        },
    )
    diagnostics = {
        "captured_stdout_tail": _diagnostic_tail(captured_stdout.getvalue()),
        "captured_stderr_tail": _diagnostic_tail(captured_stderr.getvalue()),
    }
    if any(diagnostics.values()):
        _worker_emit(evidence_stream, "runtime_diagnostics", **diagnostics)
    observable = _claim_observability_evidence(
        callback_events, capability_observation, requested
    )
    return _worker_outcome(
        evidence_stream,
        "supported" if observable else "unsupported_for_joulewise",
        None if observable else "event_observability",
        stage="complete",
    )


def parse_worker_lines(stdout: str) -> tuple[list[dict[str, Any]], list[str]]:
    rows: list[dict[str, Any]] = []
    malformed: list[str] = []
    for line in stdout.splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            malformed.append(line[-1000:])
            continue
        if not isinstance(row, dict) or not isinstance(row.get("event"), str):
            malformed.append(line[-1000:])
            continue
        rows.append(row)
    return rows, malformed


def controller(args: argparse.Namespace, emitter: Emitter | None = None) -> int:
    emitter = emitter or Emitter()
    requested = _requested_parameters(args)
    emitter.emit(
        "probe_start",
        probe="pinned_mlx_lm_spec_decode",
        **requested,
        measurement_kind="feasibility_not_energy",
        timeout_seconds=args.timeout_seconds,
    )
    distributions = [_distribution_record("mlx-lm"), _distribution_record("mlx")]
    emitter.emit(
        "runtime_environment",
        python_executable=sys.executable,
        python_version=sys.version.split()[0],
        distributions=distributions,
        expected_versions={"mlx-lm": EXPECTED_MLX_LM, "mlx": EXPECTED_MLX},
    )
    versions = {row["name"]: row["version"] for row in distributions}
    if versions != {"mlx-lm": EXPECTED_MLX_LM, "mlx": EXPECTED_MLX}:
        emitter.emit(
            "probe_outcome",
            verdict="runtime_unavailable",
            reason="pin_mismatch",
            stage="runtime_environment",
            runtime_generation_supported=None,
            claim_instrumentable=None,
        )
        return 0

    mlx_lm_root = next(
        row["package_root"] for row in distributions if row["name"] == "mlx-lm"
    )
    source_surface = _source_surface_record(mlx_lm_root)
    emitter.emit("installed_source_surface", **source_surface)
    if not _source_surface_matches_pin(source_surface):
        emitter.emit(
            "probe_outcome",
            verdict="runtime_unavailable",
            reason="source_identity_mismatch",
            stage="installed_source_surface",
            runtime_generation_supported=None,
            claim_instrumentable=None,
        )
        return 0

    target_artifact = _artifact_record("target", args.target_model)
    emitter.emit("model_artifact", **target_artifact)
    if not target_artifact["directory_present"] or not target_artifact["config_present"]:
        emitter.emit(
            "probe_outcome",
            verdict="runtime_unavailable",
            reason="target_model_artifact_missing",
            stage="model_artifact",
            runtime_generation_supported=None,
            claim_instrumentable=None,
        )
        return 0

    draft_artifact: dict[str, Any] | None = None
    draft_artifact_sha256: str | None = None
    if args.mode == "draft_model":
        assert args.draft_model is not None
        draft_artifact = _artifact_record("draft", args.draft_model)
        emitter.emit("model_artifact", **draft_artifact)
        if (
            not draft_artifact["directory_present"]
            or not draft_artifact["config_present"]
        ):
            emitter.emit(
                "probe_outcome",
                verdict="runtime_unavailable",
                reason="draft_model_artifact_missing",
                stage="model_artifact",
                runtime_generation_supported=None,
                claim_instrumentable=None,
            )
            return 0
        if target_artifact["resolved_path"] == draft_artifact["resolved_path"]:
            emitter.emit(
                "probe_outcome",
                verdict="runtime_unavailable",
                reason="target_draft_identity_collision",
                stage="model_artifact",
                runtime_generation_supported=None,
                claim_instrumentable=None,
            )
            return 0
        draft_artifact_sha256, file_hashes = _folded_model_artifact_sha256(
            Path(draft_artifact["resolved_path"])
        )
        emitter.emit(
            "model_artifact_identity",
            role="draft",
            resolved_path=draft_artifact["resolved_path"],
            model_artifact_sha256=draft_artifact_sha256,
            weight_file_count=len(file_hashes),
            weight_file_sha256=file_hashes,
        )
        if draft_artifact_sha256 is None:
            emitter.emit(
                "probe_outcome",
                verdict="runtime_unavailable",
                reason="draft_model_identity_unavailable",
                stage="model_artifact_identity",
                runtime_generation_supported=None,
                claim_instrumentable=None,
            )
            return 0

    command = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--_worker",
        "--mode",
        args.mode,
        "--target-model",
        target_artifact["resolved_path"],
        "--max-proposed-tokens",
        str(args.max_proposed_tokens),
        "--max-tokens",
        str(args.max_tokens),
        "--timeout-seconds",
        str(args.timeout_seconds),
        "--prompt",
        args.prompt,
    ]
    if draft_artifact is not None:
        quantization = draft_artifact.get("quantization")
        weight_suffixes = sorted(
            {
                Path(name).suffix.lstrip(".")
                for name in file_hashes
                if Path(name).suffix
            }
        )
        command.extend(
            [
                "--draft-model",
                draft_artifact["resolved_path"],
                "--_draft-artifact-sha256",
                str(draft_artifact_sha256),
                "--_draft-config-sha256",
                str(draft_artifact["config_sha256"]),
                "--_draft-quantization",
                json.dumps(quantization, sort_keys=True, separators=(",", ":")),
                "--_draft-weight-format",
                ",".join(weight_suffixes) or "unknown",
            ]
        )
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=args.timeout_seconds,
            env=environment,
        )
    except subprocess.TimeoutExpired as exc:
        emitter.emit(
            "probe_outcome",
            verdict="runtime_unavailable",
            reason="probe_timeout",
            stage="worker",
            timeout_seconds=args.timeout_seconds,
            captured_stdout_tail=_diagnostic_tail(exc.stdout or ""),
            captured_stderr_tail=_diagnostic_tail(exc.stderr or ""),
            runtime_generation_supported=None,
            claim_instrumentable=None,
        )
        return 0
    except OSError as exc:
        emitter.emit(
            "probe_outcome",
            verdict="runtime_unavailable",
            reason="worker_launch_failed",
            stage="worker",
            error=_safe_error(exc),
            runtime_generation_supported=None,
            claim_instrumentable=None,
        )
        return 0

    rows, malformed = parse_worker_lines(completed.stdout)
    last_worker_event = rows[-1]["event"] if rows else None
    if malformed or completed.stderr.strip():
        emitter.emit(
            "worker_diagnostics",
            malformed_stdout=malformed,
            captured_stderr_tail=_diagnostic_tail(completed.stderr),
            worker_exit_code=completed.returncode,
        )
    valid_worker_protocol = last_worker_event == "probe_outcome" and completed.returncode == 0
    forwarded_rows = rows[:-1] if last_worker_event == "probe_outcome" else rows
    for row in forwarded_rows:
        emitter.emit(row["event"], **{key: value for key, value in row.items() if key != "event"})
    if not valid_worker_protocol:
        emitter.emit(
            "probe_outcome",
            verdict="runtime_unavailable",
            reason=(
                "worker_protocol_failure"
                if last_worker_event != "probe_outcome"
                else "worker_nonzero_exit"
            ),
            stage="worker",
            worker_exit_code=completed.returncode,
            runtime_generation_supported=None,
            claim_instrumentable=None,
        )
        return 0

    child_outcome = rows[-1]
    child_verdict = child_outcome.get("verdict")
    child_reason = child_outcome.get("reason")
    has_observation = any(row.get("event") == "capability_observation" for row in rows)
    if child_verdict == "runtime_unavailable" and not has_observation:
        emitter.emit(
            "probe_outcome",
            **{key: value for key, value in child_outcome.items() if key != "event"},
            runtime_generation_supported=None,
            claim_instrumentable=None,
        )
        return 0

    evidence_outcome = derive_evidence_verdict(
        rows, requested, draft_artifact_sha256
    )
    matches = (
        child_verdict == evidence_outcome["verdict"]
        and child_reason == evidence_outcome["reason"]
    )
    if evidence_outcome["verdict"] == "supported" and not matches:
        emitter.emit(
            "probe_outcome",
            verdict="runtime_unavailable",
            reason="evidence_verdict_mismatch",
            stage="controller_evidence_validation",
            child_verdict=child_verdict,
            child_reason=child_reason,
            evidence_verdict=evidence_outcome["verdict"],
            evidence_reason=evidence_outcome["reason"],
            runtime_generation_supported=evidence_outcome[
                "runtime_generation_supported"
            ],
            claim_instrumentable=evidence_outcome["claim_instrumentable"],
        )
    else:
        emitter.emit(
            "probe_outcome",
            verdict=evidence_outcome["verdict"],
            reason=evidence_outcome["reason"],
            stage="controller_evidence_validation",
            evidence_verdict_mismatch=not matches,
            child_verdict=child_verdict,
            child_reason=child_reason,
            runtime_generation_supported=evidence_outcome[
                "runtime_generation_supported"
            ],
            claim_instrumentable=evidence_outcome["claim_instrumentable"],
        )
    return 0


class JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        Emitter().emit(
            "probe_outcome",
            verdict="runtime_unavailable",
            reason="invalid_probe_configuration",
            stage="argument_parsing",
            error={"type": "ArgumentError", "message": message},
            runtime_generation_supported=None,
            claim_instrumentable=None,
        )
        raise SystemExit(2)


def build_parser() -> argparse.ArgumentParser:
    parser = JsonArgumentParser(
        description=(
            "Emit JSONL evidence for pinned mlx-lm external-draft or native-MTP "
            "feasibility."
        )
    )
    parser.add_argument("--mode", choices=("draft_model", "native_mtp"), required=True)
    parser.add_argument("--target-model", default=DEFAULT_TARGET_MODEL)
    parser.add_argument("--draft-model")
    parser.add_argument("--max-proposed-tokens", type=int, default=3)
    parser.add_argument("--max-tokens", type=int, default=8)
    parser.add_argument("--timeout-seconds", type=float, default=300.0)
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--_worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--_draft-artifact-sha256", help=argparse.SUPPRESS)
    parser.add_argument("--_draft-config-sha256", help=argparse.SUPPRESS)
    parser.add_argument("--_draft-quantization", help=argparse.SUPPRESS)
    parser.add_argument("--_draft-weight-format", help=argparse.SUPPRESS)
    return parser


def _validate_args(args: argparse.Namespace) -> str | None:
    if args.mode == "draft_model" and not args.draft_model:
        return "--draft-model is required for --mode draft_model"
    if args.mode == "native_mtp" and args.draft_model is not None:
        return "--draft-model must be absent for --mode native_mtp"
    if args.max_proposed_tokens <= 0:
        return "--max-proposed-tokens must be greater than 0"
    if args.max_tokens <= 0:
        return "--max-tokens must be greater than 0"
    if args.timeout_seconds <= 0:
        return "--timeout-seconds must be greater than 0"
    if not args.prompt:
        return "--prompt must be non-empty"
    if args._worker and args.mode == "draft_model":
        hidden = (
            args._draft_artifact_sha256,
            args._draft_config_sha256,
            args._draft_quantization,
            args._draft_weight_format,
        )
        if not all(hidden):
            return "worker draft identity arguments are incomplete"
    return None


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    problem = _validate_args(args)
    if problem is not None:
        Emitter().emit(
            "probe_outcome",
            verdict="runtime_unavailable",
            reason="invalid_probe_configuration",
            stage="argument_validation",
            error={"type": "ValueError", "message": problem},
            runtime_generation_supported=None,
            claim_instrumentable=None,
        )
        return 2
    if args._worker:
        return runtime_worker(args)
    return controller(args)


if __name__ == "__main__":
    raise SystemExit(main())
