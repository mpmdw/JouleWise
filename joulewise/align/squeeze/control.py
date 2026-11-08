"""Real hidden forward passes with exact, evaluator-only token accounting.

Nothing loads weights or starts a sampler. A caller supplies an already prepared
decoder. Only successfully materialized token IDs count as completed work.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import time
from typing import Any, Iterator, Protocol, Sequence

from .config import canonical, sha256, validate_control


class Decoder(Protocol):
    identity: str
    vocab_size: int
    max_context_tokens: int

    def decode(self, prompt: Sequence[int], *, max_tokens: int) -> Iterator[int]:
        """Yield one fully evaluated greedy output per forward, with fresh cache.

        The first forward consumes the prompt, subsequent forwards consume the
        previous output. No EOS stop or speculative/lookahead generation. Closing
        the iterator must not perform additional forwards.
        """
        ...


class Injection(Protocol):
    @property
    def config(self) -> dict[str, Any]: ...
    @property
    def identity(self) -> str: ...
    @property
    def placement(self) -> str: ...
    @property
    def trigger_index(self) -> int: ...
    def receipt(self) -> dict[str, Any]: ...
    def execute(self) -> None: ...


class MlxDecoder:
    """Use an already loaded model; imports MLX lazily, never downloads weights.

    cache_factory must return a fresh cache for each request. Production MLX-LM
    models can use lambda: make_prompt_cache(model). Evaluation forces lazy work
    to complete before yielding an ID. The visible endpoint's cache and sampler
    are never used. Native tests use a tiny synthetic model.
    """

    def __init__(self, model: Any, *, cache_factory: Any, identity: str,
                 vocab_size: int, max_context_tokens: int) -> None:
        self.model, self.cache_factory, self.identity = model, cache_factory, identity
        self.vocab_size, self.max_context_tokens = vocab_size, max_context_tokens

    def decode(self, prompt: Sequence[int], *, max_tokens: int) -> Iterator[int]:
        import mlx.core as mx

        cache = self.cache_factory()
        inputs = mx.array([list(prompt)], dtype=mx.int32)
        # Greedy argmax uses no RNG; explicit eval prevents counting lazy graphs.
        for _ in range(max_tokens):
            logits = self.model(inputs, cache=cache)
            if logits.shape != (1, inputs.shape[1], self.vocab_size):
                raise ValueError("unexpected hidden model logits shape")
            token = mx.argmax(logits[:, -1, :], axis=-1)
            mx.eval(token)
            token_id = int(token.item())
            yield token_id
            inputs = mx.array([[token_id]], dtype=mx.int32)


@dataclass(frozen=True)
class SqueezeRun:
    episode: Any
    transcript: Any
    ground_truth: dict[str, Any]


class HiddenDecode:
    """Single-use injection. Failed/partial work can never certify a dose."""

    def __init__(self, config: dict[str, Any], decoder: Decoder, *,
                 clock=time.monotonic_ns, clock_domain: str) -> None:
        self._config = validate_control(config)
        if not isinstance(decoder.identity, str) or not decoder.identity:
            raise ValueError("decoder needs an explicit model identity")
        if (type(decoder.vocab_size) is not int or decoder.vocab_size <= 0
                or type(decoder.max_context_tokens) is not int or decoder.max_context_tokens <= 0):
            raise ValueError("decoder limits must be positive integers")
        if any(t >= decoder.vocab_size for t in self.config["prompt_token_ids"]):
            raise ValueError("hidden prompt contains out-of-vocabulary IDs")
        if self.config["max_context_tokens"] > decoder.max_context_tokens:
            raise ValueError("hidden context budget exceeds the native decoder limit")
        if not isinstance(clock_domain, str) or not clock_domain:
            raise ValueError("clock_domain is required")
        self.decoder, self.clock = decoder, clock
        self._receipt = {
            "schema": "joulewise.align.squeeze.ground_truth.v1",
            "audience": "evaluator_only", "status": "not_triggered",
            "control": deepcopy(self.config), "decoder_identity": decoder.identity,
            "clock_domain": clock_domain, "start_ns": None, "end_ns": None,
            "output_token_ids": [], "completed_tokens": 0, "prefill_tokens": 0,
            "incremental_decode_forwards": 0, "completed_forward_input_tokens": 0,
            "unknown_work_on_failure": False, "H": None,
        }

    @property
    def config(self) -> dict[str, Any]:
        return deepcopy(self._config)

    def receipt(self) -> dict[str, Any]:
        return deepcopy(self._receipt)

    @property
    def identity(self) -> str:
        return self.decoder.identity

    @property
    def placement(self) -> str:
        return "before_chat"

    @property
    def trigger_index(self) -> int:
        return self._config["before_chat_call"]

    def execute(self) -> None:
        if self._receipt["status"] != "not_triggered":
            raise RuntimeError("hidden decode is single-use")
        receipt = self._receipt
        receipt["status"] = "running"
        receipt["start_ns"] = self.clock()
        iterator = None
        try:
            k = self._config["decode_tokens"]
            prompt = tuple(self._config["prompt_token_ids"])
            prompt_length = len(prompt)
            if k:
                iterator = iter(self.decoder.decode(prompt, max_tokens=k))
                for _ in range(k):
                    try:
                        token = next(iterator)
                    except StopIteration as exc:
                        raise ValueError("hidden decoder returned fewer than k tokens") from exc
                    if type(token) is not int or not 0 <= token < self.decoder.vocab_size:
                        raise ValueError("hidden decoder yielded an invalid token ID")
                    receipt["output_token_ids"].append(token)
                    n = len(receipt["output_token_ids"])
                    receipt.update(completed_tokens=n,
                                   prefill_tokens=prompt_length,
                                   incremental_decode_forwards=n - 1,
                                   completed_forward_input_tokens=prompt_length + n - 1)
            receipt["status"] = "completed"
        except BaseException as exc:
            receipt["status"] = "interrupted" if isinstance(exc, (KeyboardInterrupt, SystemExit)) else "failed"
            receipt["error_type"] = type(exc).__name__
            receipt["unknown_work_on_failure"] = True
            raise
        finally:
            try:
                if iterator is not None and callable(getattr(iterator, "close", None)):
                    iterator.close()
            except BaseException as exc:
                receipt["status"] = "failed"
                receipt["error_type"] = type(exc).__name__
                receipt["unknown_work_on_failure"] = True
                raise
            finally:
                receipt["end_ns"] = self.clock()
                receipt["H"] = receipt["completed_tokens"] if receipt["status"] == "completed" else None


class ControlEndpoint:
    """Inject before a selected visible request, inside run_episode sampling.

    Return the exact original ChatResult. In particular raw_usage, token counts,
    messages, provenance and visible RNG/cache remain the wrapped endpoint's.
    Receipts are read separately, never inserted into any monitor view.
    """

    def __init__(self, endpoint: Any, *, variant_sha256: str, control: Injection | None = None) -> None:
        self.endpoint, self.control = endpoint, control
        identity = {"variant_sha256": variant_sha256,
                    "control_sha256": None if control is None else control.config["config_sha256"],
                    "decoder_identity": None if control is None else control.identity}
        self.identity = endpoint.identity + "/squeeze/" + sha256(canonical(identity).encode("utf-8"))
        self.calls = 0

    def __getattr__(self, name: str) -> Any:
        return getattr(self.endpoint, name)

    def chat(self, messages: Any, *, tools=(), max_tokens: int,
             temperature: float, seed: int | None) -> Any:
        index = self.calls
        self.calls += 1
        if (self.control is not None and self.control.placement == "before_chat"
                and index == self.control.trigger_index):
            self.control.execute()
        return self.endpoint.chat(messages, tools=tools, max_tokens=max_tokens,
                                  temperature=temperature, seed=seed)
