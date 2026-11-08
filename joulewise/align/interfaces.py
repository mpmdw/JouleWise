"""Cross-lane interfaces for the alignment pipeline (docs/align/PIPELINE.md).

Lanes build against these protocols, never against each other's modules, so
they can be written in parallel: the runner (A5) drives any ``ChatEndpoint``,
samples any ``PowerSampler`` and scores with any ``Monitor``; the SHADE port
(A1), the NVIDIA and Jetson samplers (A2, A3) and the mocks implement them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, Sequence, runtime_checkable

from joulewise.align.records import ClockMapping, MonitorVerdict, PowerTrace, Visibility


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
    # Populated by stop(); empty when all traces use clock_domain already.
    clock_mappings: tuple[ClockMapping, ...]

    def start(self) -> None: ...

    def stop(self) -> tuple[PowerTrace, ...]: ...


@runtime_checkable
class Monitor(Protocol):
    """Scores a transcript for suspicion under a given visibility.

    Optional ``last_verdict`` holds per-call diagnostics, including ``flags``.
    The runner snapshots it after score(); exceptions may instead expose the
    same object as ``diagnostics``. Neither attribute is required for conformance.
    """

    model: str

    def score(self, transcript: Sequence[ChatMessage], *, visibility: Visibility,
              task_description: str) -> MonitorVerdict: ...


@runtime_checkable
class AgentTask(Protocol):
    """One agentic task pair (a main task and, under "sabotage", a side task).

    ``scratchpad_tags`` names the open/close tags of a hidden scratchpad the
    agent is told the monitor cannot see (SHADE-Arena convention), or None.
    The runner strips only closed pairs before a ``no_scratchpad`` monitor
    reads the transcript; unclosed suffixes stay visible. Optional ``flags``
    contains diagnostic strings copied after scoring as ``task.<flag>``.
    """

    task_pair: str
    scratchpad_tags: tuple[str, str] | None

    def reset(self, seed: int) -> None: ...

    def system_prompt(self, condition: str) -> str: ...

    def user_prompt(self) -> str: ...

    def task_description(self) -> str: ...  # what the monitor is told the agent was asked to do

    def tool_schemas(self) -> Sequence[Mapping[str, Any]]: ...  # OpenAI "tools" entries

    def call_tool(self, name: str, arguments_json: str) -> str: ...

    def score_main(self, transcript: Sequence[ChatMessage]) -> float | None: ...

    def score_side(self, transcript: Sequence[ChatMessage]) -> bool | None: ...


@runtime_checkable
class TokenCounter(Protocol):
    """Counts tokens of text with the served model's tokenizer (vLLM and llama.cpp expose /tokenize)."""

    def count_tokens(self, text: str) -> int: ...


__all__ = ["ChatMessage", "ToolCallRequest", "ChatResult", "ChatEndpoint", "PowerSampler", "Monitor",
           "AgentTask", "TokenCounter"]
