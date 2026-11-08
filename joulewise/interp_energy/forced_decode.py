"""Teacher-forced, batch-one decode through an mlx-lm-style cache.

Prefill consumes prompt[:-1]; step i consumes prompt[-1] (i=0) or
forced[i-1] and scores forced[i]. Like normal generation, the last emitted
token is NOT yet in the cache. EOS has no special meaning during replay.
No sampler, logits processor, cache trimming, or tokenization runs in this loop.

Forward timestamps bracket completed device work, including cache updates.
Diagnostics are separately timed and JSON serialization happens after replay.
Diagnostics still add work BETWEEN forwards: this is an instrumented replay,
not an uninstrumented mlx-lm throughput or energy measurement.
"""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import math
import operator
import platform
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, TextIO

SCHEMA = "interp_energy.forced_decode.v1"


def canonical_sha256(value: Any) -> str:
    """SHA-256 of UTF-8, sorted-key compact JSON, without a trailing newline."""
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()


def _positive_int(value: Any, name: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a positive integer")
    try:
        value = operator.index(value)
    except TypeError as exc:
        raise ValueError(f"{name} must be a positive integer") from exc
    if value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return value


def token_ids(values: Iterable[int], name: str = "tokens") -> list[int]:
    """Validate without silently coercing floats, strings, or booleans."""
    result = []
    for value in values:
        if isinstance(value, bool):
            raise ValueError(f"{name} must contain integer token IDs")
        try:
            value = operator.index(value)
        except TypeError as exc:
            raise ValueError(f"{name} must contain integer token IDs") from exc
        if not 0 <= value < 2**31:
            raise ValueError(f"{name} token IDs must be in [0, 2**31)")
        result.append(value)
    if not result:
        raise ValueError(f"{name} must not be empty")
    return result


def token_sequence_sha256(tokens: Iterable[int]) -> str:
    """Hash canonical JSON integer IDs, never their text or a tokenizer name."""
    return canonical_sha256(token_ids(tokens))


def weight_file_identity(model_dir: Path) -> dict[str, Any]:
    """Hash the local safetensors manifest used by the CLI (before timing).

    The aggregate is a manifest digest, not the SHA of concatenated raw weights.
    Its sorted filenames, sizes and individual file SHAs are retained for audit.
    The API also accepts externally computed identities for in-process edits.
    """
    files = []
    for path in sorted(model_dir.glob("*.safetensors")):
        digest = hashlib.sha256()
        size = 0
        with path.open("rb") as stream:
            while chunk := stream.read(1024 * 1024):
                digest.update(chunk)
                size += len(chunk)
        files.append({"name": path.name, "size_bytes": size, "sha256": digest.hexdigest()})
    if not files:
        raise ValueError("local model directory must contain safetensors weights")
    return {"scheme": "safetensors-manifest-json-v1", "files": files,
            "sha256": canonical_sha256(files)}


def _version(distribution: str) -> str | None:
    try:
        return importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        return None


def _ordered_top_k(indices: list[int], logprobs: list[float]) -> list[dict[str, Any]]:
    return [{"token_id": i, "logprob": p} for i, p in sorted(
        zip(indices, logprobs), key=lambda pair: (-pair[1], pair[0]),
    )]


class NumpyBackend:
    """Eager reference backend; optional NumPy is imported at construction."""

    name = "numpy"

    def __init__(self) -> None:
        import numpy as np
        self.np = np

    def make_cache(self, model: Any) -> list[Any]:
        return model.make_cache()

    def prepare(self, model: Any) -> None:
        pass

    def prefill(self, model: Any, inputs: list[int], cache: list[Any]) -> None:
        model(self.np.array([inputs], dtype=self.np.int32), cache=cache)

    def forward(self, model: Any, inputs: list[int], cache: list[Any]) -> Any:
        logits = model(self.np.array([inputs], dtype=self.np.int32), cache=cache)
        if logits.ndim != 3 or logits.shape[:2] != (1, len(inputs)):
            raise ValueError("model must return logits with shape [1, input_length, vocab]")
        return logits[0, -1, :]

    def diagnostics(self, logits: Any, forced: int, top_k: int) -> dict[str, Any]:
        np = self.np
        values = np.asarray(logits, dtype=np.float64)
        if not np.isfinite(values).all():
            raise ValueError("model produced non-finite logits")
        shifted = values - values.max()
        logprobs = shifted - np.log(np.exp(shifted).sum())
        indices = np.argsort(-logprobs, kind="stable")[:top_k].tolist()
        return {
            "argmax_token_id": int(np.argmax(values)),
            "forced_token_logprob": float(logprobs[forced]),
            "top_k": _ordered_top_k(indices, [float(logprobs[i]) for i in indices]),
        }


class MLXBackend:
    """Native mlx-lm prompt caches, including model-specific hybrid caches.

    No cache implementation is substituted. Both logits and every cache state
    are evaluated before the completion timestamp (MLX is otherwise lazy).
    """

    name = "mlx"

    def __init__(self) -> None:
        import mlx.core as mx
        from mlx_lm.models.cache import make_prompt_cache
        self.mx = mx
        self._make_prompt_cache = make_prompt_cache

    def make_cache(self, model: Any) -> list[Any]:
        return self._make_prompt_cache(model)

    def prepare(self, model: Any) -> None:
        self.mx.eval(model.parameters())

    def prefill(self, model: Any, inputs: list[int], cache: list[Any]) -> None:
        # Discard lazy prefill logits, just as mlx-lm's generate_step does.
        model(self.mx.array([inputs], dtype=self.mx.int32), cache=cache)
        self.mx.eval([entry.state for entry in cache])

    def forward(self, model: Any, inputs: list[int], cache: list[Any]) -> Any:
        logits = model(self.mx.array([inputs], dtype=self.mx.int32), cache=cache)
        if logits.ndim != 3 or logits.shape[:2] != (1, len(inputs)):
            raise ValueError("model must return logits with shape [1, input_length, vocab]")
        last = logits[0, -1, :]
        self.mx.eval(last, [entry.state for entry in cache])
        return last

    def diagnostics(self, logits: Any, forced: int, top_k: int) -> dict[str, Any]:
        mx = self.mx
        # Promote bf16/fp16 diagnostics; the model's forward dtype is untouched.
        values = logits.astype(mx.float32)
        shifted = values - mx.max(values)
        logprobs = shifted - mx.logsumexp(shifted)
        indices = mx.argsort(-logprobs)[:top_k]
        probs = logprobs[indices]
        forced_prob = logprobs[forced]
        argmax = mx.argmax(values)
        finite = mx.all(mx.isfinite(values))
        mx.eval(indices, probs, forced_prob, argmax, finite)
        if not finite.item():
            raise ValueError("model produced non-finite logits")
        return {"argmax_token_id": int(argmax.item()),
                "forced_token_logprob": float(forced_prob.item()),
                "top_k": _ordered_top_k(indices.tolist(), probs.tolist())}


@dataclass
class ReplayResult:
    metadata: dict[str, Any]
    tokens: list[dict[str, Any]]
    summary: dict[str, Any]

    def write_jsonl(self, stream: TextIO) -> None:
        """Write a header, token rows, and a completion footer after replay."""
        for record in (self.metadata, *self.tokens, self.summary):
            stream.write(json.dumps(record, sort_keys=True, allow_nan=False) + "\n")


def replay(
    model: Any,
    prompt_tokens: Iterable[int],
    forced_tokens: Iterable[int],
    *,
    model_weights_sha256: str,
    vocab_size: int,
    backend: Any = None,
    top_k: int = 5,
    prefill_chunk_size: int = 512,
    clock_ns: Callable[[], int] = time.monotonic_ns,
) -> ReplayResult:
    """Replay fixed IDs with a fresh cache; return buffered JSON-compatible rows.

    ``model_weights_sha256`` identifies the CURRENT weights, not a base model
    name. API callers own that assertion, especially after in-process edits.
    The CLI computes a file-manifest identity. Match prompt/sequence/policy
    hashes across arms; weights are the intended varying identity.
    """
    prompt = token_ids(prompt_tokens, "prompt")
    forced = token_ids(forced_tokens, "forced sequence")
    vocab_size = _positive_int(vocab_size, "vocab_size")
    top_k = _positive_int(top_k, "top_k")
    chunk_size = _positive_int(prefill_chunk_size, "prefill_chunk_size")
    if max(prompt + forced) >= vocab_size:
        raise ValueError("token ID exceeds model vocabulary")
    if not isinstance(model_weights_sha256, str) or not re.fullmatch(
        r"[0-9a-f]{64}", model_weights_sha256,
    ):
        raise ValueError("model_weights_sha256 must be a lowercase SHA-256 hex digest")
    backend = backend if backend is not None else MLXBackend()
    if hasattr(model, "eval"):
        model.eval()
    backend.prepare(model)
    cache = backend.make_cache(model)
    if not cache:
        raise ValueError("model must supply a nonempty prompt cache")
    k = min(top_k, vocab_size)
    versions = {name: _version(name) for name in (
        ("mlx", "mlx-lm") if backend.name == "mlx" else ("numpy",))}
    policy = {"backend": backend.name, "batch_size": 1, "sampling": "none",
              "vocab_size": vocab_size, "runtime_versions": versions,
              "execution": "synchronous-forward-default-stream",
              "cache_policy": "fresh-model-default-no-trimming",
              "cache_types": [f"{type(c).__module__}.{type(c).__qualname__}" for c in cache],
              "prefill_chunk_size": chunk_size, "prefill": "prompt-except-last",
              "decode": "last-prompt-then-previous-forced-token",
              "top_k_requested": top_k, "top_k_effective": k,
              "top_k_ties": "backend-defined-membership-token-id-order-within-ties"}
    identity = {"model_weights_sha256": model_weights_sha256,
                "prompt_sha256": token_sequence_sha256(prompt),
                "token_sequence_sha256": token_sequence_sha256(forced),
                "replay_policy_sha256": canonical_sha256(policy)}
    metadata = {"schema": SCHEMA, "record_type": "replay", **identity,
                "prompt_tokens": prompt, "forced_tokens": forced,
                "vocab_size": vocab_size, "policy": policy,
                "clock": "time.monotonic_ns", "python_version": platform.python_version(),
                "runtime_versions": versions,
                "weights_identity_source": "caller-asserted",
                "timing_note": "forward includes synchronization; diagnostics between forwards"}
    prefill_started = clock_ns()
    for start in range(0, len(prompt) - 1, chunk_size):
        backend.prefill(model, prompt[start:min(start + chunk_size, len(prompt) - 1)], cache)
    prefill_finished = clock_ns()
    if prefill_finished < prefill_started:
        raise ValueError("clock must return nondecreasing monotonic nanoseconds")
    previous_finished = prefill_finished
    rows = []
    for i, target in enumerate(forced):
        consumed = prompt[-1] if i == 0 else forced[i - 1]
        started = clock_ns()
        logits = backend.forward(model, [consumed], cache)
        finished = clock_ns()
        if tuple(logits.shape) != (vocab_size,):
            raise ValueError("logits vocabulary does not match vocab_size")
        diagnostics = backend.diagnostics(logits, target, k)
        diagnostics_finished = clock_ns()
        if not previous_finished <= started <= finished <= diagnostics_finished:
            raise ValueError("clock must return nondecreasing monotonic nanoseconds")
        previous_finished = diagnostics_finished
        if not math.isfinite(diagnostics["forced_token_logprob"]):
            raise ValueError("forced token log-probability must be finite")
        rows.append({"schema": SCHEMA, "record_type": "token", **identity,
                     "token_index": i, "input_token_id": consumed,
                     "forced_token_id": target, "context_tokens": len(prompt) + i,
                     "forward_started_ns": started, "forward_finished_ns": finished,
                     "diagnostics_finished_ns": diagnostics_finished,
                     "forward_duration_ns": finished - started,
                     "argmax_agrees": diagnostics["argmax_token_id"] == target,
                     "forced_in_top_k": any(p["token_id"] == target for p in diagnostics["top_k"]),
                     **diagnostics})
    summary = {"schema": SCHEMA, "record_type": "complete", **identity,
               "token_count": len(rows),
               "argmax_agreement_count": sum(r["argmax_agrees"] for r in rows),
               "prefill_started_ns": prefill_started, "prefill_finished_ns": prefill_finished,
               "decode_started_ns": rows[0]["forward_started_ns"],
               "decode_finished_ns": rows[-1]["diagnostics_finished_ns"],
               "cache_input_token_count": len(prompt) + len(forced) - 1}
    return ReplayResult(metadata, rows, summary)
