"""Thinking controls, exact token deletion and a stdlib local-server adapter."""

from __future__ import annotations

import json
import math
import random
import time
from dataclasses import dataclass, field, replace
from typing import Any, Callable, Mapping, Protocol, Sequence
from urllib.request import Request, urlopen

from joulewise.align.endpoints import reasoning_fields, split_inline_thinking
from joulewise.align.interfaces import ChatMessage, ChatResult, ToolCallRequest

DEFAULT_FRACTIONS = (1.0, 0.6, 0.4, 0.3)  # Pilot design specified in the lane brief.
CONCISE_PROMPT = "Be concise. Use the shortest reasoning that supports your answer."


class TokenCodec(Protocol):
    """Use the served model's tokenizer, never words-as-tokens in production."""

    identity: str

    def encode(self, text: str) -> Sequence[int]: ...

    def decode(self, tokens: Sequence[int]) -> str: ...


@dataclass(frozen=True)
class Condition:
    name: str
    mode: str = "on"  # on, off, budget, concise, deletion
    fraction: float | None = None
    concise_prompt: str = CONCISE_PROMPT
    deletion_span_count: int | None = 4  # Pilot design input; None reproduces old token deletion.


def default_conditions(fractions: Sequence[float] = DEFAULT_FRACTIONS) -> tuple[Condition, ...]:
    return (Condition("thinking_on"), Condition("thinking_off", "off"),
            Condition("concise", "concise"),
            *(Condition(f"budget_{f:g}", "budget", f) for f in fractions),
            *(Condition(f"deletion_{f:g}", "deletion", f) for f in fractions))


def thinking_options(backend: str, enabled: bool) -> dict[str, Any]:
    """Qwen3 template control; llama.cpp additionally exposes reasoning_effort."""
    options: dict[str, Any] = {"chat_template_kwargs": {"enable_thinking": enabled}}
    if backend == "llamacpp" and not enabled:
        options["reasoning_effort"] = "none"
    return options


def cap_tokens(median_tokens: float, fraction: float) -> int:
    """Floor a fractional median; zero means force an answer without a reasoning call."""
    return max(0, math.floor(median_tokens * fraction))


def shakedown_median_length(lengths: Sequence[int], censored: Sequence[bool]) -> tuple[float, tuple[str, ...]]:
    """Return L, statistics.median of hinted thinking-on shakedown lengths only.

    The caller excludes generation failures. Output-cap-censored runs stay at
    their recorded length. Those lengths and the runner's substituted max_tokens
    are both at least every uncensored length, so substitution preserves the
    median when its order statistics are uncensored (2c < n). At 2c >= n the
    median itself is censored and carries L_censored. Empty input has no L.
    """
    from statistics import median

    if not lengths or len(lengths) != len(censored):
        raise ValueError("L needs nonempty lengths and matching censoring indicators")
    if (any(isinstance(n, bool) or not isinstance(n, int) or n < 0 for n in lengths)
            or any(not isinstance(c, bool) for c in censored)):
        raise ValueError("L needs nonnegative integer lengths and boolean censoring indicators")
    return float(median(lengths)), (("L_censored",) if 2 * sum(censored) >= len(lengths) else ())


@dataclass(frozen=True)
class Deletion:
    text: str
    removed_tokens: int
    spans: tuple[tuple[int, int], ...]  # Half-open positions in the original token IDs.
    visible_tokens: int
    flags: tuple[str, ...] = ()


def delete_spans(text: str, *, remove_tokens: int, codec: TokenCodec, seed: int,
                 span_count: int | None = 4) -> Deletion:
    """Delete a recorded number of contiguous spans, with uniformly composed lengths.

    Choose positive span lengths summing to the cut and distinct insertion gaps
    in the retained sequence. None is an explicit legacy token-deletion control.
    """
    tokens = tuple(codec.encode(text))
    n = min(len(tokens), max(0, remove_tokens))
    rng = random.Random(seed)
    spans: list[tuple[int, int]] = []
    if span_count is None:
        selected = sorted(rng.sample(range(len(tokens)), n))
        for position in selected:
            if spans and spans[-1][1] == position:
                spans[-1] = (spans[-1][0], position + 1)
            else:
                spans.append((position, position + 1))
    elif n:
        k = min(max(1, span_count), n, len(tokens) - n + 1)
        cuts = sorted(rng.sample(range(1, n), k - 1))
        lengths = [b - a for a, b in zip([0, *cuts], [*cuts, n])]
        gaps = sorted(rng.sample(range(len(tokens) - n + 1), k))
        cursor_keep, out = 0, 0
        for gap, length in zip(gaps, lengths):
            out += gap - cursor_keep
            cursor_keep = gap
            spans.append((out, out + length))
            out += length
    removed = {i for a, b in spans for i in range(a, b)}
    visible = codec.decode([t for i, t in enumerate(tokens) if i not in removed])
    count = len(codec.encode(visible))
    flags = []
    if n != remove_tokens:
        flags.append("deletion_count_clipped")
    if span_count is not None and n and len(spans) != span_count:
        flags.append("deletion_span_count_clipped")
    if count != len(tokens) - n:
        flags.append("deletion_retokenized")
    return Deletion(visible, n, tuple(spans), count, tuple(flags))


@dataclass(frozen=True)
class LocalEndpoint:
    """Bind extra body options while preserving the shared ChatEndpoint signature.

    The endpoint and tokenizer routes are local serving APIs; no SDK or hosted
    service is used. Inject transport in tests. Timing uses the client's monotonic
    clock; nonstreaming APIs do not supply a trustworthy first-token timestamp.
    chat() performs no tokenizer I/O. Missing counters remain flagged zero until
    account_tokens() is called by the budget runner after sampler.stop().
    """

    base_url: str
    model: str
    backend: str
    timeout_s: float
    options: Mapping[str, Any] = field(default_factory=dict)
    transport: Callable[[str, dict[str, Any]], dict[str, Any]] | None = field(
        default=None, compare=False, repr=False)

    @property
    def identity(self) -> str:
        return f"{self.backend}:{self.model}"

    def configured(self, options: Mapping[str, Any]) -> LocalEndpoint:
        return replace(self, options={**self.options, **options})

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        if self.transport is not None:
            return self.transport(path, payload)
        root = self.base_url.rstrip("/").removesuffix("/v1")
        request = Request(root + path,
                          data=json.dumps(payload, allow_nan=False).encode(),
                          headers={"Content-Type": "application/json"})
        with urlopen(request, timeout=self.timeout_s) as response:
            return json.loads(response.read())

    def encode(self, text: str) -> Sequence[int]:
        payload = ({"model": self.model, "prompt": text, "add_special_tokens": False}
                   if self.backend == "vllm" else {"content": text, "add_special": False})
        return self._post("/tokenize", payload)["tokens"]

    def decode(self, tokens: Sequence[int]) -> str:
        payload: dict[str, Any] = {"tokens": list(tokens)}
        if self.backend == "vllm":
            payload["model"] = self.model
        result = self._post("/detokenize", payload)
        return result.get("prompt", result.get("content", ""))

    def chat(self, messages: Sequence[ChatMessage], *,
             tools: Sequence[Mapping[str, Any]] = (), max_tokens: int,
             temperature: float, seed: int | None) -> ChatResult:
        payload: dict[str, Any] = {
            **self.options,
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content,
                          **({"name": m.name} if m.name else {}),
                          **({"tool_call_id": m.tool_call_id} if m.tool_call_id else {})}
                         for m in messages],
            "max_tokens": max_tokens, "temperature": temperature, "stream": False,
        }
        if seed is not None:
            payload["seed"] = seed
        if tools:
            payload["tools"] = list(tools)
        start = time.monotonic_ns()
        raw = self._post("/v1/chat/completions", payload)
        end = time.monotonic_ns()
        message = raw["choices"][0]["message"]
        content = message.get("content") or ""
        reasoning, reasoning_flags = reasoning_fields(message)
        native_reasoning = bool(reasoning)
        usage = dict(raw.get("usage") or {})
        flags = ["first_token_time_unavailable", *reasoning_flags]
        if raw["choices"][0].get("finish_reason") == "length":
            flags.append("generation_cap_reached")
        # vLLM's strict qwen3 parser files an unclosed thinking block as
        # content. It is still reasoning, including when max_tokens cuts it.
        if not reasoning:
            reasoning, content, split_flags = split_inline_thinking(
                content,
                thinking_enabled=(self.options.get("chat_template_kwargs", {}).get("enable_thinking")
                                  is True and not self.options.get("continue_final_message")),
                finish_reason=(None if "</think>" in self.options.get("stop", ())
                               else raw["choices"][0].get("finish_reason")))
            flags.extend(split_flags)
        details = usage.get("completion_tokens_details") or {}
        reasoning_tokens = details.get("reasoning_tokens", usage.get("reasoning_tokens"))
        if native_reasoning and not reasoning_tokens:
            flags.append("reasoning_tokens_unreported")
        pending = []
        if reasoning_tokens is None:
            reasoning_tokens = 0
            pending.append("reasoning")
        completion = usage.get("completion_tokens")
        if completion is None:
            completion = 0
            pending.append("completion")
        prompt = usage.get("prompt_tokens")
        if prompt is None:
            prompt = 0
            pending.append("prompt")
        cached = (usage.get("prompt_tokens_details") or {}).get("cached_tokens", 0) or 0
        usage["_budget_flags"] = flags
        usage["joulewise"] = {"flags": flags, "finish_reason": raw["choices"][0].get("finish_reason")}
        if pending:
            usage["_budget_token_counts_pending"] = pending
        usage["_finish_reason"] = raw["choices"][0].get("finish_reason")
        calls = tuple(ToolCallRequest(c.get("id", ""), c["function"]["name"],
                                      c["function"].get("arguments", "{}"))
                      for c in (message.get("tool_calls") or ()))
        return ChatResult(content, reasoning, calls, int(prompt), int(cached),
                          int(completion), int(reasoning_tokens), start, None, end, usage)

    def account_tokens(self, result: ChatResult, messages: Sequence[ChatMessage]) -> ChatResult:
        """Resolve chat's missing counters outside every measured sampler span."""
        usage = dict(result.raw_usage)
        pending = usage.pop("_budget_token_counts_pending", ())
        flags = list(usage.get("_budget_flags", ()))
        reasoning, completion, prompt = (result.reasoning_tokens, result.completion_tokens,
                                         result.prompt_tokens)
        def count(text: str, field: str, fallback: int) -> int:
            try:
                return len(self.encode(text)) if text else 0
            except Exception as exc:
                # Generation already completed. A tokenizer is diagnostic I/O;
                # preserve the result and mark the unknown count explicitly.
                flags.extend((f"token_accounting_error:{field}:{type(exc).__name__}",
                              f"{field}_tokens_unavailable"))
                return fallback

        if "reasoning" in pending:
            reasoning = count(result.reasoning_text, "reasoning", reasoning)
            if result.reasoning_text and "reasoning_tokens_unavailable" not in flags:
                flags.append("reasoning_tokens_from_tokenizer")
        if "completion" in pending:
            completion = reasoning + count(result.content, "completion", completion)
            if "reasoning_tokens_unavailable" in flags:
                flags.append("completion_tokens_unavailable")
            if "completion_tokens_unavailable" not in flags:
                flags.append("completion_tokens_from_tokenizer")
        if "prompt" in pending:
            # A concatenation is not the chat template; never claim an exact count.
            prompt = count("\n".join(m.content for m in messages), "prompt", prompt)
            if "prompt_tokens_unavailable" not in flags:
                flags.append("prompt_tokens_template_estimate")
        usage["_budget_flags"] = list(dict.fromkeys(flags))
        usage["joulewise"] = {**usage.get("joulewise", {}), "flags": usage["_budget_flags"]}
        return replace(result, prompt_tokens=int(prompt), completion_tokens=int(completion),
                       reasoning_tokens=int(reasoning), raw_usage=usage)
