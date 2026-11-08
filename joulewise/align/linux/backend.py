"""llama.cpp implementation of ALIGN's existing ChatEndpoint boundary.

This is an episode backend, not an implementation of MLX-only R0 diagnostics
(teacher-forced NLL, Metal memory probes or thermometry).
"""
from __future__ import annotations

from dataclasses import replace
from typing import Callable, Any

from joulewise.align.endpoints import (
    EndpointRequestFailed, OpenAICompatEndpoint, split_inline_thinking,
)
from joulewise.align.records import to_jsonable


class LlamaCppEndpoint(OpenAICompatEndpoint):
    """Reuse the production SSE/accounting/tool-history parser.

    post is an in-memory HTTP transport seam for tests. No request is retried:
    an uncertain delivery must never cause unlogged duplicate inference.
    Separate reasoning is preferred; inline <think> parsing is opt-in.
    """

    def __init__(self, base_url, model, *, post: Callable[..., Any] | None = None,
                 inline_thinking=False, seed_model_id=None, task_pair=None,
                 thinking="thinking_on", **kwargs):
        extra = dict(kwargs.pop("extra_body", {}) or {})
        extra.setdefault("cache_prompt", False)
        super().__init__(base_url, model, max_retries=0, extra_body=extra, **kwargs)
        if not self._valid_url:
            raise ValueError("invalid llama.cpp base_url")
        self.identity = f"llama.cpp:{model}@{self.base_url}"
        self.post = post
        self.inline_thinking = inline_thinking
        self.seed_model_id, self.task_pair, self.thinking = seed_model_id, task_pair, thinking
        self.turn_index = 0
        self.last_request = None

    def _open(self, url, body, flags, retries):
        self.last_request = {"url": url, "body": body}
        if self.post is not None:
            return self.post(url, body, self.timeout_s)
        return super()._open(url, body, flags, retries)

    def chat(self, *args, **kwargs):
        seed_record = {"requested_seed": kwargs.get("seed"), "policy": "passthrough"}
        if self.seed_model_id is not None:
            from joulewise.align.linux.seeds import episode_seed, turn_seed
            if kwargs.get("seed") is None or not self.task_pair:
                raise ValueError("ALIGN seed law requires a seed index and task pair")
            logical_episode = episode_seed(self.seed_model_id, self.thinking, self.task_pair, kwargs["seed"])
            logical_turn = turn_seed(logical_episode, self.turn_index)
            kwargs["seed"] = logical_turn & 0xFFFFFFFF
            seed_record.update(policy="align-p4-v1/align-p4-turn-v1/low32",
                               episode_seed_uint64=logical_episode, turn_seed_uint64=logical_turn,
                               server_seed_uint32=kwargs["seed"], turn_index=self.turn_index)
        seed = kwargs.get("seed")
        if seed is not None and (type(seed) is not int or not 0 <= seed < 0xFFFFFFFF):
            # UINT32_MAX is llama.cpp's random-seed sentinel, not a fixed seed.
            raise ValueError("llama.cpp requires a fixed uint32 seed below UINT32_MAX")
        self.turn_index += 1
        failure = None
        try:
            result = super().chat(*args, **kwargs)
        except EndpointRequestFailed as exc:
            result, failure = exc.partial_result, exc
        usage = dict(result.raw_usage)
        diagnostics = dict(usage["joulewise"])
        flags = list(diagnostics["flags"])
        # A stream cut short can contain valid counts and partial tool calls.
        # Preserve it as failed evidence; never execute those calls.
        failed_stream = "stream_missing_done" in flags or "server_stream_error" in flags
        if self.inline_thinking and not result.reasoning_text:
            thought, content, extra_flags = split_inline_thinking(
                result.content, thinking_enabled=True,
                finish_reason=diagnostics.get("finish_reason"))
            if thought and result.reasoning_tokens == 0:
                flags.append("reasoning_tokens_unreported")
            flags.extend(extra_flags)
            diagnostics["raw_inline_content"] = result.content
            result = replace(result, content=content, reasoning_text=thought)
        diagnostics.update(flags=list(dict.fromkeys(flags)), backend="llama.cpp",
                           inline_thinking=self.inline_thinking, seed=seed_record,
                           request=self.last_request,
                           completion={"content": result.content,
                                       "reasoning_text": result.reasoning_text,
                                       "tool_calls": to_jsonable(result.tool_calls)})
        usage["joulewise"] = diagnostics
        result = replace(result, raw_usage=usage)
        if failure is not None or failed_stream:
            raise EndpointRequestFailed(result) from failure
        return result


class LlamaCppBackend:
    """Fresh endpoint state per member; SHADE remains the pinned offline port."""

    def __init__(self, endpoint_config, shade_cache, *, post=None):
        self.endpoint_config = dict(endpoint_config)
        self.shade_cache = shade_cache
        self.post = post
        self.endpoint = None

    def new_session(self, task_pair=None):
        self.endpoint = LlamaCppEndpoint(**self.endpoint_config, post=self.post, task_pair=task_pair)
        return self.endpoint

    def task(self, pair):
        from joulewise.align.shade import PinnedUpstream, ShadeTask
        return ShadeTask(pair, upstream=PinnedUpstream(
            cache_dir=self.shade_cache, allow_fetch=False), give_hint=True)
