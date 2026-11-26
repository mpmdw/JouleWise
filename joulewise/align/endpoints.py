"""Stdlib OpenAI streaming client and deterministic endpoints for alignment runs.

Server counts are authoritative. Missing accounting and incomplete streams are
flags, never estimates. Failed requests raise EndpointRequestFailed with a
partial ChatResult attached, so protocol-only runners record an endpoint error
without inventing a zero-token turn. Other diagnostics live in
raw_usage["joulewise"] and flags; runners should copy them into Episode.flags.
"""

from __future__ import annotations

import errno
import http.client
import json
import os
import socket
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

from joulewise.align.interfaces import ChatMessage, ChatResult, ToolCallRequest


@dataclass(frozen=True)
class AssistantMessage(ChatMessage):
    """Lane-local extension retaining tool requests absent from ChatMessage."""

    tool_calls: tuple[ToolCallRequest, ...] = ()
    reasoning_text: str = ""


def assistant_message(result: ChatResult) -> AssistantMessage:
    """Retain a completion's structured tool history for the next model call."""
    return AssistantMessage("assistant", result.content, tool_calls=result.tool_calls,
                            reasoning_text=result.reasoning_text)


def finish_reason(result: ChatResult) -> str | None:
    """Read the shared, budget-local, then legacy finish-reason metadata."""
    diagnostics = result.raw_usage.get("joulewise", {})
    values = ((diagnostics.get("finish_reason") if isinstance(diagnostics, Mapping) else None),
              result.raw_usage.get("_finish_reason"), result.raw_usage.get("finish_reason"))
    return next((value for value in values if isinstance(value, str)), None)


def reasoning_fields(fields: Mapping[str, Any]) -> tuple[str, tuple[str, ...]]:
    """Prefer nonempty reasoning_content, then reasoning; never join aliases.

    Equal aliases count once. Different nonempty strings keep reasoning_content
    (the older parser's precedence) and flag the discarded alternative.
    Null, empty and non-string values cannot hide the other alias.
    """
    preferred, other = fields.get("reasoning_content"), fields.get("reasoning")
    preferred = preferred if isinstance(preferred, str) else ""
    other = other if isinstance(other, str) else ""
    flags = ("reasoning_fields_disagree",) if preferred and other and preferred != other else ()
    return preferred or other, flags


def split_inline_thinking(text: str, *, open_tag: str = "<think>",
                          close_tag: str = "</think>", thinking_enabled: bool = False,
                          finish_reason: str | None = None) -> tuple[str, str, tuple[str, ...]]:
    """Split one budget thinking block, including a prompt-held opening tag.

    A tagless ceiling hit is reasoning only when thinking is explicitly enabled.
    The shared streaming endpoint deliberately does not apply this content rule.
    """
    flags: list[str] = []
    reasoning, answer = "", text
    opened = bool(open_tag and open_tag in text)
    if opened:
        before, _, rest = text.partition(open_tag)
        reasoning, closed, after = rest.partition(close_tag)
        answer = before + after if closed else before
        if not closed:
            flags.append("reasoning_block_unclosed")
    elif thinking_enabled and close_tag and close_tag in text:
        reasoning, _, answer = text.partition(close_tag)
    elif thinking_enabled and text and finish_reason == "length":
        reasoning, answer = text, ""
        flags.append("reasoning_block_unclosed")
    if (reasoning or opened) and not answer.strip() and finish_reason == "length":
        flags.append("reasoning_censored_at_token_limit")
    return reasoning, answer, tuple(flags)


def _coalesce_assistant_calls(messages: Sequence[ChatMessage]) -> list[ChatMessage]:
    """Fold the runner's per-call records into their assistant turn.

    A plain assistant message with tool_call_id contains arguments, never
    visible text. Results can be interleaved with these call records; collect
    all calls on the preceding assistant and leave its results in order.
    With no plain assistant (runner actions_only), a synthetic assistant ends
    at the first result. Parallel grouping cannot be reconstructed in that view.
    Structured AssistantMessage transcripts already have the desired shape.
    """
    output: list[ChatMessage] = []
    assistant_index: int | None = None
    synthetic = False
    for message in messages:
        if message.role == "assistant" and message.tool_call_id is not None:
            if assistant_index is None or (synthetic and output[-1].role == "tool"):
                assistant_index = len(output)
                output.append(AssistantMessage("assistant", ""))
                synthetic = True
            previous = output[assistant_index]
            call = ToolCallRequest(message.tool_call_id, message.name or "", message.content)
            calls = list(getattr(previous, "tool_calls", ()))
            if call not in calls:
                calls.append(call)
            output[assistant_index] = AssistantMessage(
                "assistant", previous.content, previous.name, previous.tool_call_id,
                tuple(calls), getattr(previous, "reasoning_text", ""))
            continue
        output.append(message)
        if message.role == "assistant":
            assistant_index = len(output) - 1
            synthetic = False
        elif message.role != "tool":
            assistant_index = None
    return output


class _Reader:
    def __init__(self, reader: Any, received: list[int]) -> None:
        self.reader, self.received = reader, received

    def read(self, *args: Any) -> bytes:
        value = self.reader.read(*args)
        self.received[0] += len(value)
        return value

    def readline(self, *args: Any) -> bytes:
        value = self.reader.readline(*args)
        self.received[0] += len(value)
        return value

    def __getattr__(self, name: str) -> Any:
        return getattr(self.reader, name)


class _Socket:
    def __init__(self, sock: Any, received: list[int]) -> None:
        self.sock, self.received = sock, received

    def makefile(self, *args: Any, **kwargs: Any) -> _Reader:
        return _Reader(self.sock.makefile(*args, **kwargs), self.received)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.sock, name)


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args: Any, **kwargs: Any) -> None:
        return None


def _opener(received: list[int], connected: list[bool]) -> urllib.request.OpenerDirector:
    """Track successful connect and response bytes before urllib parses headers."""
    def connection(cls: type, *args: Any, **kwargs: Any) -> Any:
        conn = cls(*args, **kwargs)
        connect = conn.connect

        def tracked_connect() -> None:
            connect()
            # Once connected, request delivery is uncertain even before any
            # response byte. Never replay a possible prefill after this point.
            connected[0] = True

        conn.connect = tracked_connect
        conn.response_class = lambda sock, **kw: http.client.HTTPResponse(
            _Socket(sock, received), **kw)
        return conn

    class HTTP(urllib.request.HTTPHandler):
        def http_open(self, req: Any) -> Any:
            return self.do_open(lambda *a, **k: connection(http.client.HTTPConnection, *a, **k), req)

    class HTTPS(urllib.request.HTTPSHandler):
        def https_open(self, req: Any) -> Any:
            return self.do_open(lambda *a, **k: connection(http.client.HTTPSConnection, *a, **k),
                                req, context=self._context)

    return urllib.request.build_opener(HTTP(), HTTPS(), _NoRedirect())


def _connection_failure(exc: BaseException) -> bool:
    reason = exc.reason if isinstance(exc, urllib.error.URLError) else exc
    if isinstance(reason, ssl.SSLError):
        return False
    return isinstance(reason, (ConnectionError, TimeoutError, socket.gaierror)) or (
        isinstance(reason, OSError) and reason.errno in {
            errno.ECONNREFUSED, errno.ECONNRESET, errno.ECONNABORTED,
            errno.ENETUNREACH, errno.EHOSTUNREACH, errno.ETIMEDOUT})


def _events(response: Any) -> Iterable[str]:
    data: list[str] = []
    for line in iter(response.readline, b""):
        line = line.decode("utf-8").rstrip("\r\n")
        if not line:
            if data:
                yield "\n".join(data)
                data = []
        elif line.startswith("data:"):
            data.append(line[5:].removeprefix(" "))
    if data:
        yield "\n".join(data)


def _integer(value: Any, name: str, flags: list[str]) -> int:
    if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
        return value
    flags.append("missing_or_invalid_" + name)
    return 0


class EndpointRequestFailed(RuntimeError):
    """An HTTP, transport or accounting failure with the partial completion."""

    def __init__(self, partial_result: ChatResult) -> None:
        self.partial_result = partial_result
        self.flags = tuple(partial_result.raw_usage.get("joulewise", {}).get("flags", ()))
        super().__init__("Endpoint request failed: " + ", ".join(self.flags))


class OpenAICompatEndpoint:
    """OpenAI chat/SSE and vLLM or llama.cpp tokenize, using urllib only.

    timeout_s and max_retries are operator-set transport budgets, not analysis
    thresholds. Retries apply only to failed connects with zero bytes read.
    No HTTP status, partial header or partial completion is ever retried.
    derive_reasoning_tokens is accepted for old configurations but ignored and
    flagged. The runner computes tokenizer diagnostics after the episode.
    flags/retries describe only the latest chat or count_tokens operation;
    raw_usage retains each chat's diagnostics. Tool recovery retains only IDs
    referenced by the current transcript plus the latest generated requests.
    """

    def __init__(self, base_url: str, model: str, *, api_key_env: str | None = None,
                 timeout_s: float = 120.0, extra_body: Mapping[str, Any] | None = None,
                 max_retries: int = 1, derive_reasoning_tokens: bool = False) -> None:
        parsed = urllib.parse.urlsplit(base_url)
        self._valid_url = (parsed.scheme in {"http", "https"} and bool(parsed.netloc)
                           and parsed.username is None and parsed.password is None
                           and not parsed.query and not parsed.fragment)
        self.base_url = base_url.rstrip("/") if self._valid_url else ""
        self.model, self.api_key_env = model, api_key_env
        self.timeout_s, self.max_retries = timeout_s, max(0, max_retries)
        self.extra_body = dict(extra_body or {})
        self.derive_reasoning_tokens = derive_reasoning_tokens
        self.identity = f"openai_compat:{model}@{self.base_url or 'invalid_url'}"
        self.flags: list[str] = []
        self.retries: list[dict[str, Any]] = []
        self._requests: dict[str, ToolCallRequest] = {}

    def _headers(self, flags: list[str]) -> dict[str, str]:
        headers = {"Content-Type": "application/json", "Accept": "text/event-stream"}
        if self.api_key_env:
            key = os.environ.get(self.api_key_env)
            if key:
                headers["Authorization"] = "Bearer " + key
            else:
                flags.append("api_key_env_unset")
        return headers

    def _open(self, url: str, body: Mapping[str, Any], flags: list[str],
              retries: list[dict[str, Any]]) -> Any:
        request = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"),
                                         headers=self._headers(flags), method="POST")
        for attempt in range(self.max_retries + 1):
            received, connected = [0], [False]
            try:
                return _opener(received, connected).open(request, timeout=self.timeout_s)
            except (OSError, http.client.HTTPException) as exc:
                reason = exc.reason if isinstance(exc, urllib.error.URLError) else exc
                if isinstance(reason, TimeoutError):
                    flags.append("request_timeout_after_connect" if connected[0] else "connect_timeout")
                if (connected[0] or received[0] or not _connection_failure(exc)
                        or attempt == self.max_retries):
                    raise
                retry = {"attempt": attempt + 1, "error": type(exc).__name__, "received_bytes": 0}
                retries.append(retry)
                self.retries.append(dict(retry))
                flags.append("connection_retry")

    def _messages(self, messages: Sequence[ChatMessage], flags: list[str]) -> list[dict[str, Any]]:
        messages = _coalesce_assistant_calls(messages)
        output = []
        for index, message in enumerate(messages):
            value: dict[str, Any] = {"role": message.role, "content": message.content}
            if message.name is not None:
                value["name"] = message.name
            if message.tool_call_id is not None:
                value["tool_call_id"] = message.tool_call_id
            if message.role == "assistant":
                calls = getattr(message, "tool_calls", ())
                if not calls:
                    recovered = []
                    for following in messages[index + 1:]:
                        if following.role != "tool":
                            break
                        call = self._requests.get(following.tool_call_id or "")
                        if call is not None:
                            recovered.append(call)
                        else:
                            flags.append("tool_history_unavailable")
                    calls = recovered
                if calls:
                    value["tool_calls"] = [
                        {"id": c.call_id, "type": "function",
                         "function": {"name": c.name, "arguments": c.arguments_json}}
                        for c in calls]
                reasoning = getattr(message, "reasoning_text", "")
                if reasoning:
                    value["reasoning_content"] = reasoning
            output.append(value)
        return output

    def chat(self, messages: Sequence[ChatMessage], *, tools: Sequence[Mapping[str, Any]] = (),
             max_tokens: int, temperature: float, seed: int | None) -> ChatResult:
        self.flags.clear()
        self.retries.clear()
        referenced = {m.tool_call_id for m in messages if m.tool_call_id is not None}
        self._requests = {key: value for key, value in self._requests.items() if key in referenced}
        start = time.monotonic_ns()
        first: int | None = None
        flags: list[str] = []
        if self.derive_reasoning_tokens:
            flags.append("derive_reasoning_tokens_ignored")
        retries: list[dict[str, Any]] = []
        content: list[str] = []
        reasoning: list[str] = []
        calls: dict[int, dict[str, str]] = {}
        usage: dict[str, Any] = {}
        done = False
        finish_reason: str | None = None
        body = dict(self.extra_body)
        reserved = {"model", "messages", "tools", "stream", "max_tokens", "temperature", "seed", "n"}
        if reserved.intersection(body):
            flags.append("extra_body_reserved_fields_ignored")
        body.update(model=self.model, messages=self._messages(messages, flags), stream=True,
                    max_tokens=max_tokens, temperature=temperature, n=1)
        body.pop("tools", None)
        body.pop("seed", None)
        options = body.get("stream_options") or {}
        if not isinstance(options, Mapping):
            flags.append("invalid_stream_options")
            options = {}
        body["stream_options"] = {**options, "include_usage": True}
        if tools:
            body["tools"] = list(tools)
        if seed is not None:
            body["seed"] = seed
        path = "/chat/completions" if self.base_url.endswith("/v1") else "/v1/chat/completions"
        try:
            if not self._valid_url:
                flags.append("invalid_base_url")
            else:
                with self._open(self.base_url + path, body, flags, retries) as response:
                    for event in _events(response):
                        if event == "[DONE]":
                            done = True
                            break
                        try:
                            chunk = json.loads(event)
                        except json.JSONDecodeError:
                            flags.append("invalid_sse_json")
                            continue
                        if not isinstance(chunk, dict):
                            flags.append("invalid_sse_chunk")
                            continue
                        if chunk.get("error"):
                            flags.append("server_stream_error")
                        if isinstance(chunk.get("usage"), dict):
                            usage.update(chunk["usage"])
                        if isinstance(chunk.get("timings"), dict):
                            usage["timings"] = chunk["timings"]
                        for choice in chunk.get("choices") or ():
                            if choice.get("index", 0) != 0:
                                flags.append("extra_choice_ignored")
                                continue
                            if choice.get("finish_reason") is not None:
                                finish_reason = choice["finish_reason"]
                            delta = choice.get("delta") or {}
                            text = delta.get("content")
                            # vLLM currently emits reasoning; llama.cpp and older
                            # vLLM parsers emit reasoning_content.
                            thought, thought_flags = reasoning_fields(delta)
                            flags.extend(thought_flags)
                            generated_tool = any(
                                (c.get("function") or {}).get("name")
                                or (c.get("function") or {}).get("arguments")
                                for c in delta.get("tool_calls") or ())
                            if (text or thought or generated_tool) and first is None:
                                first = time.monotonic_ns()
                            if isinstance(text, str):
                                content.append(text)
                            if isinstance(thought, str):
                                reasoning.append(thought)
                            for call in delta.get("tool_calls") or ():
                                slot = calls.setdefault(call.get("index", 0),
                                                        {"id": "", "name": "", "arguments": ""})
                                fn = call.get("function") or {}
                                # ID and function name are identifiers, unlike the
                                # streamed arguments. Tolerate identical repeats.
                                for key, value in (("id", call.get("id")),
                                                   ("name", fn.get("name"))):
                                    if value:
                                        if not slot[key]:
                                            slot[key] = value
                                        elif slot[key] != value:
                                            flags.append("tool_call_" + key + "_conflict")
                                slot["arguments"] += fn.get("arguments") or ""
        except urllib.error.HTTPError as exc:
            flags.append(f"http_error:{exc.code}")
            exc.close()
        except (OSError, http.client.HTTPException, UnicodeError, ValueError, TypeError,
                AttributeError, KeyError, IndexError) as exc:
            flags.append("transport_or_stream_error:" + type(exc).__name__)
        if not done:
            flags.append("stream_missing_done")
        if finish_reason == "length":
            flags.append("generation_cap_reached")
        timing = usage.get("timings") or {}
        if not isinstance(timing, Mapping):
            flags.append("invalid_timings")
            timing = {}
        prompt_value = usage.get("prompt_tokens")
        if prompt_value is None and "prompt_n" in timing:
            prompt_value = (_integer(timing["prompt_n"], "timings_prompt_n", flags)
                            + _integer(timing.get("cache_n", 0), "timings_cache_n", flags))
            flags.append("prompt_tokens_from_timings")
        prompt = _integer(prompt_value, "prompt_tokens", flags)
        completion = _integer(usage.get("completion_tokens", timing.get("predicted_n")),
                              "completion_tokens", flags)
        prompt_details = usage.get("prompt_tokens_details") or {}
        completion_details = usage.get("completion_tokens_details") or {}
        if not isinstance(prompt_details, Mapping):
            flags.append("invalid_prompt_tokens_details")
            prompt_details = {}
        if not isinstance(completion_details, Mapping):
            flags.append("invalid_completion_tokens_details")
            completion_details = {}
        cached_value = next((value for value in (
            prompt_details.get("cached_tokens"), usage.get("cached_tokens"),
            timing.get("cache_n")) if value is not None), None)
        if cached_value is None:
            # vLLM omits this unless --enable-prompt-tokens-details is enabled,
            # even when prefix caching reused KV. The contract's zero is unknown.
            flags.append("cached_prompt_tokens_unreported")
        cached = _integer(0 if cached_value is None else cached_value,
                          "cached_prompt_tokens", flags)
        hidden = _integer(completion_details.get(
            "reasoning_tokens", 0), "reasoning_tokens", flags)
        if cached > prompt:
            flags.append("cached_prompt_tokens_exceed_prompt")
        if hidden > completion:
            flags.append("reasoning_tokens_exceed_completion")
        # Empty reasoning deltas carry no generated text or unreported work.
        if any(reasoning) and not hidden:
            flags.append("reasoning_tokens_unreported")
        requests = []
        for index, call in sorted(calls.items()):
            if not call["id"]:
                call["id"] = f"unreported_{index}"
                flags.append("tool_call_id_unreported")
            request = ToolCallRequest(call["id"], call["name"], call["arguments"])
            requests.append(request)
            self._requests[request.call_id] = request
        # Only prompt/completion totals are mandatory accounting. Cached and
        # reasoning counters retain the shared contract's flagged unknown zero.
        missing_usage = any(flag in flags for flag in (
            "missing_or_invalid_prompt_tokens", "missing_or_invalid_completion_tokens"))
        if missing_usage:
            flags.append("usage_unavailable")
        failed = missing_usage or any(flag.startswith((
            "http_error:", "transport_or_stream_error:")) for flag in flags)
        usage["joulewise"] = {"flags": list(dict.fromkeys(flags)), "retries": retries,
                              "finish_reason": finish_reason}
        self.flags.extend(usage["joulewise"]["flags"])
        result = ChatResult("".join(content), "".join(reasoning), tuple(requests), prompt, cached,
                            completion, hidden, start, first, time.monotonic_ns(), usage)
        if failed:
            raise EndpointRequestFailed(result)
        return result

    def count_tokens(self, text: str) -> int:
        """Ask the server tokenizer; raise when no valid count is available."""
        self.flags.clear()
        self.retries.clear()
        flags: list[str] = []
        retries: list[dict[str, Any]] = []
        root = self.base_url.removesuffix("/v1")
        if not self._valid_url:
            self.flags.append("tokenize_invalid_base_url")
            raise RuntimeError("server tokenizer invalid base URL")
        # Both servers accept unknown fields. Including both text keys avoids
        # llama.cpp's valid 200 {"tokens": []} response to a missing content key.
        # Count text only on both backends: vLLM otherwise defaults to adding
        # special tokens, while llama.cpp does not. Keep the fallback consistent.
        special = {"add_special_tokens": False, "add_special": False}
        bodies = ({"model": self.model, "prompt": text, "content": text, **special},
                  {"content": text, **special})
        for index, body in enumerate(bodies):
            try:
                with self._open(root + "/tokenize", body, flags, retries) as response:
                    value = json.load(response)
                if (isinstance(value.get("count"), int) and not isinstance(value["count"], bool)
                        and value["count"] >= 0):
                    result = value["count"]
                elif isinstance(value.get("tokens"), list):
                    result = len(value["tokens"])
                else:
                    flags.append("tokenize_unrecognized_shape")
                    continue
                if text and result == 0 and index == 0:
                    flags.append("tokenize_empty_response_retry")
                    continue
                flags.append("tokenize_shape:prompt_and_content" if index == 0
                             else "tokenize_shape:content")
                self.flags.extend(flags)
                return result
            except urllib.error.HTTPError as exc:
                status = exc.code
                exc.close()
                if index == 0 and status in {400, 404, 422}:
                    flags.append("tokenize_llamacpp_shape")
                    continue
                flags.append(f"tokenize_http_error:{status}")
                break
            except (OSError, http.client.HTTPException, ValueError, TypeError) as exc:
                flags.append("tokenize_error:" + type(exc).__name__)
                break
        self.flags.extend(flags + ["tokenize_unavailable"])
        raise RuntimeError("server tokenizer unavailable")


class MockEndpoint:
    """Scripted protocol implementation, with no I/O or optional dependencies.

    ChatResult entries are returned intact. Mapping entries use integer synthetic
    clocks and explicit counts when supplied; whitespace counts are labelled as
    synthetic. token_counts supplies exact text-to-count fixtures for tokenizers.
    turn_interval_ns is an operator-set synthetic clock step (default one second),
    not a model-latency estimate or an analysis threshold.
    """

    def __init__(self, script: Iterable[ChatResult | Mapping[str, Any]] = (), *,
                 identity: str = "mock:scripted", token_counts: Mapping[str, int] | None = None,
                 start_ns: int = 0, turn_interval_ns: int = 1_000_000_000) -> None:
        self.identity = identity
        self.model = identity
        self._script = iter(script)
        self._token_counts = dict(token_counts or {})
        self._time, self._interval = start_ns, turn_interval_ns
        self.calls: list[dict[str, Any]] = []
        self.flags: list[str] = []
        self.retries: list[dict[str, Any]] = []

    def count_tokens(self, text: str) -> int:
        if text in self._token_counts:
            return self._token_counts[text]
        self.flags.append("mock_whitespace_tokenizer")
        return len(text.split())

    def chat(self, messages: Sequence[ChatMessage], *, tools: Sequence[Mapping[str, Any]] = (),
             max_tokens: int, temperature: float, seed: int | None) -> ChatResult:
        self.calls.append({"messages": tuple(messages), "tools": tuple(tools),
                           "max_tokens": max_tokens, "temperature": temperature, "seed": seed})
        flag_start = len(self.flags)
        entry = next(self._script, None)
        if isinstance(entry, ChatResult):
            return entry
        if entry is None:
            self.flags.append("mock_script_exhausted")
            entry = {"raw_usage": {"joulewise": {"flags": ["mock_script_exhausted"], "retries": []}}}
        value = dict(entry)
        text = value.pop("content", "")
        thought = value.pop("reasoning_text", "")
        start = value.pop("start_ns", self._time)
        end = value.pop("end_ns", start + self._interval)
        self._time = end
        requests = tuple(c if isinstance(c, ToolCallRequest) else ToolCallRequest(**c)
                         for c in value.pop("tool_calls", ()))
        prompt = value.pop("prompt_tokens", None)
        completion = value.pop("completion_tokens", None)
        if prompt is None:
            prompt = sum(self.count_tokens(m.content) for m in messages)
        if completion is None:
            completion = self.count_tokens(text) + self.count_tokens(thought)
        raw_usage = dict(value.pop("raw_usage", {}))
        diagnostics = dict(raw_usage.get("joulewise", {}))
        diagnostics["flags"] = list(dict.fromkeys(
            list(diagnostics.get("flags", ())) + self.flags[flag_start:]))
        diagnostics.setdefault("retries", [])
        finish_reason = value.pop("finish_reason", diagnostics.get("finish_reason"))
        diagnostics["finish_reason"] = finish_reason
        if finish_reason == "length":
            diagnostics["flags"].append("generation_cap_reached")
        raw_usage["joulewise"] = diagnostics
        return ChatResult(text, thought, requests, prompt, value.pop("cached_prompt_tokens", 0),
                          completion, value.pop("reasoning_tokens", 0), start,
                          value.pop("first_token_ns", start if text or thought or requests else None), end,
                          raw_usage)


__all__ = ["EndpointRequestFailed", "AssistantMessage", "assistant_message", "OpenAICompatEndpoint", "MockEndpoint"]
