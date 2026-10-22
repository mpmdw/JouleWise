"""Cross-lane interfaces for the alignment pipeline (docs/align/PIPELINE.md).

Lanes build against these protocols, never against each other's modules, so
they can be written in parallel: the runner (A5) drives any ``ChatEndpoint``,
samples any ``PowerSampler`` and scores with any ``Monitor``; the SHADE port
(A1), the NVIDIA and Jetson samplers (A2, A3) and the mocks implement them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, Sequence, runtime_checkable

from joulewise.align.records import MonitorVerdict, PowerTrace, Visibility


@dataclass(frozen=True)
class ChatMessage:
    role: str  # "system" | "user" | "assistant" | "tool"
    content: str
    name: str | None = None
    tool_call_id: str | None = None


@dataclass(frozen=True)
class ToolCallRequest:
    call_id: str
    name: str
    arguments_json: str


@dataclass(frozen=True)
class ChatResult:
    """One completion, with the server's own token counts and the client's timestamps.

    ``reasoning_text`` holds generated text the serving stack separated from
    the visible content (a thinking block); its tokens are inside
    ``completion_tokens``. ``cached_prompt_tokens`` is the prefix the server
    reports it reused (0 when unreported); the runner derives a turn's
    ``context_tokens`` and ``prefill_tokens`` from it.
    """

    content: str
    reasoning_text: str
    tool_calls: tuple[ToolCallRequest, ...]
    prompt_tokens: int
    cached_prompt_tokens: int
    completion_tokens: int
    reasoning_tokens: int
    start_ns: int
    first_token_ns: int | None
    end_ns: int
    raw_usage: Mapping[str, Any] = field(default_factory=dict)


@runtime_checkable
class ChatEndpoint(Protocol):
    """An OpenAI-compatible chat endpoint (vLLM, llama.cpp server, or a mock)."""

    identity: str  # backend kind, model and version; never a credential

    def chat(self, messages: Sequence[ChatMessage], *, tools: Sequence[Mapping[str, Any]] = (),
             max_tokens: int, temperature: float, seed: int | None) -> ChatResult: ...


@runtime_checkable
class PowerSampler(Protocol):
    """Samples one or more channels between start() and stop().

    ``clock_domain`` names the clock its timestamps use; ``stop`` returns one
    trace per channel. A sampler that cannot measure records why in the trace
    ``notes`` and the runner flags the episode; it does not raise.
    """

    clock_domain: str

    def start(self) -> None: ...

    def stop(self) -> tuple[PowerTrace, ...]: ...


@runtime_checkable
class Monitor(Protocol):
    """Scores a transcript for suspicion under a given visibility."""

    model: str

    def score(self, transcript: Sequence[ChatMessage], *, visibility: Visibility,
              task_description: str) -> MonitorVerdict: ...


__all__ = ["ChatMessage", "ToolCallRequest", "ChatResult", "ChatEndpoint", "PowerSampler", "Monitor"]
