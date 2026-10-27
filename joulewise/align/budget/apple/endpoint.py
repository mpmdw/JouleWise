"""Budget controls over the Apple lane's in-process MlxEndpoint.

The runtime retains its native tokenizer, generation loop, token IDs, timing
events and greedy sampler. Only chat rendering and string-stop observation
are adapted. One caller owns the prepared runtime at a time.
"""

from __future__ import annotations

from copy import copy
from dataclasses import asdict, replace
from typing import Any, Mapping, Sequence

from joulewise.align.apple.endpoint import MlxEndpoint, parse_completion
from joulewise.align.interfaces import ChatMessage, ChatResult


class MlxCodec:
    def __init__(self, tokenizer: Any, identity: str):
        self.tokenizer, self.identity = tokenizer, identity

    def encode(self, text: str) -> Sequence[int]:
        return self.tokenizer.encode(text, add_special_tokens=False)

    def decode(self, tokens: Sequence[int]) -> str:
        return self.tokenizer.decode(list(tokens))


class _Template:
    def __init__(self, native: Any, options: Mapping[str, Any]):
        self.native, self.options = native, options

    def __getattr__(self, name: str) -> Any:
        return getattr(self.native, name)

    def apply_chat_template(self, messages, **kwargs):
        kwargs.update(self.options.get("chat_template_kwargs", {}))
        for name in ("continue_final_message", "add_generation_prompt"):
            if name in self.options:
                kwargs[name] = self.options[name]
        return self.native.apply_chat_template(messages, **kwargs)


class _StoppingStream:
    def __init__(self, native: Any, stops: Sequence[str]):
        self.native, self.stops = native, stops

    def __getattr__(self, name: str) -> Any:
        return getattr(self.native, name)

    def stream_generate(self, *args, **kwargs):
        stream = self.native.stream_generate(*args, **kwargs)
        text = ""
        try:
            for response in stream:
                text += response.text
                hit = any(stop in text for stop in self.stops)
                if hit:
                    # Keep all emitted text and tokens as observed work. The
                    # caller separates the delimiter; no token is erased.
                    response = copy(response)
                    response.finish_reason = "stop"
                yield response
                if hit:
                    break
        finally:
            close = getattr(stream, "close", None)
            if close is not None:
                close()


class _RuntimeView:
    """Render via a view; generation still sees the real tokenizer's type."""

    def __init__(self, runtime: Any, options: Mapping[str, Any]):
        self.native = runtime
        self._tokenizer = _Template(runtime._tokenizer, options)

    @property
    def _mlx_lm(self):
        return self.native._mlx_lm

    @_mlx_lm.setter
    def _mlx_lm(self, value):
        self.native._mlx_lm = value

    def __getattr__(self, name: str) -> Any:
        return getattr(self.native, name)


class BudgetMlxEndpoint:
    def __init__(self, endpoint: MlxEndpoint, options: Mapping[str, Any] | None = None):
        self.endpoint, self.options = endpoint, dict(options or {})
        self.identity = endpoint.identity
        self.codec = MlxCodec(endpoint.runtime._tokenizer, endpoint.identity)

    def configured(self, options: Mapping[str, Any]) -> BudgetMlxEndpoint:
        return BudgetMlxEndpoint(self.endpoint, {**self.options, **options})

    def chat(self, messages: Sequence[ChatMessage], *, tools=(), max_tokens: int,
             temperature: float, seed: int | None) -> ChatResult:
        if temperature != 0.0 or tools:
            raise ValueError("D3 uses the existing greedy MLX sampler without tools")
        if set(self.options) - {"chat_template_kwargs", "continue_final_message",
                               "add_generation_prompt", "stop"}:
            raise ValueError("unsupported MLX budget option")
        native_runtime = self.endpoint.runtime
        native_module = native_runtime._mlx_lm
        first_event = len(self.endpoint.events)
        self.endpoint.runtime = _RuntimeView(native_runtime, self.options)
        native_runtime._mlx_lm = _StoppingStream(native_module, self.options.get("stop", ()))
        try:
            result = self.endpoint.chat(messages, max_tokens=max_tokens, temperature=0.0, seed=seed)
        finally:
            self.endpoint.runtime = native_runtime
            native_runtime._mlx_lm = native_module
        flags = list(result.raw_usage.get("flags", ()))
        if any(f.startswith("endpoint_error:") for f in flags):
            raise RuntimeError(";".join(flags))
        raw = result.raw_usage["raw_text"]
        finish = self.endpoint.turn_provenance[-1]["generation"]["finish_reason"]
        continuation = self.options.get("continue_final_message", False)
        enabled = self.options.get("chat_template_kwargs", {}).get("enable_thinking", True)
        if continuation:
            content, reasoning = raw, ""
            if "<think>" in raw:
                flags.append("reasoning_after_forced_delimiter")
        elif enabled and "</think>" not in raw:
            content, reasoning = "", raw.removeprefix("<think>")
            flags.append("reasoning_block_unclosed")
            if finish in ("length", "max_tokens", "max_new_tokens") or result.completion_tokens >= max_tokens:
                finish = "length"
        else:
            content, reasoning, _, _ = parse_completion(raw)
        reasoning_tokens = min(result.completion_tokens, len(self.codec.encode(reasoning))) if reasoning else 0
        if reasoning:
            flags.append("reasoning_tokens_retokenized")
        return replace(result, content=content, reasoning_text=reasoning,
                       reasoning_tokens=reasoning_tokens,
                       raw_usage={**result.raw_usage, "_finish_reason": finish,
                                  "_budget_flags": sorted({
                                      "turn_token_budget_reached" if f.startswith("turn_token_budget_reached:") else f
                                      for f in flags}),
                                  "budget_options": self.options,
                                  "native_events": [asdict(e) for e in self.endpoint.events[first_event:]],
                                  "native_generation": self.endpoint.turn_provenance[-1]})
