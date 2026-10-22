"""Offline HTTP worlds for streaming, accounting, tokenization and retries."""

from __future__ import annotations

import json
import socket
import threading
import time
import http.client
import unittest
from collections import deque
from contextlib import AbstractContextManager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from unittest.mock import patch

from joulewise.align.endpoints import EndpointRequestFailed, MockEndpoint, OpenAICompatEndpoint, assistant_message
from joulewise.align.interfaces import ChatEndpoint, ChatMessage, TokenCounter, ToolCallRequest


def stream_packets(*, flavour: str = "vllm", content: str = "Done.",
                   reasoning: str = "Plan carefully.", calls: tuple[dict, ...] = (),
                   prompt: int = 4096, cached: int = 3072, completion: int = 512,
                   hidden: int = 384) -> dict[str, Any]:
    """Wire fields from the vLLM/llama.cpp source excerpts in shade_port.md.

    Counts are exact scripted integers. llama.cpp does not report reasoning
    counts, even when it emits separated reasoning text.
    """
    chunks = [
        {"choices": [{"index": 0, "delta": {"role": "assistant"}}]},
        {"choices": [{"index": 0, "delta": {"reasoning" if flavour == "vllm" else "reasoning_content": reasoning}}]},
        {"choices": [{"index": 0, "delta": {"content": content}}]},
    ]
    for index, call in enumerate(calls):
        name = call["name"]
        arguments = json.dumps(call["arguments"])
        # Server identifiers are complete fields; JSON arguments stream in pieces.
        split = len(arguments) // 2
        chunks.extend([
            {"choices": [{"index": 0, "delta": {"tool_calls": [
                {"index": index, "id": call["id"], "type": "function",
                 "function": {"name": name, "arguments": arguments[:split]}}]}}]},
            {"choices": [{"index": 0, "delta": {"tool_calls": [
                {"index": index, "function": {"arguments": arguments[split:]}}]}}]},
        ])
    final = {"choices": [], "usage": {
        "prompt_tokens": prompt, "completion_tokens": completion,
        "prompt_tokens_details": {"cached_tokens": cached},
    }}
    if flavour == "vllm":
        final["usage"]["completion_tokens_details"] = {"reasoning_tokens": hidden}
    if flavour == "llamacpp":
        # tools/server/server-task.cpp puts timings on the final usage chunk.
        final["timings"] = {"cache_n": cached, "prompt_n": prompt - cached,
                            "predicted_n": completion, "prompt_ms": 240.5, "predicted_ms": 8640.25}
    chunks.append({"choices": [{"index": 0, "delta": {},
                                "finish_reason": "tool_calls" if calls else "stop"}]})
    chunks.append(final)
    return {"chunks": chunks}


class HTTPWorld(AbstractContextManager):
    """Loopback only; arbitrary scripted SSE/JSON/status/disconnect responses."""

    def __init__(self, packets: list[dict[str, Any]]) -> None:
        self.packets = deque(packets)
        self.requests: list[dict[str, Any]] = []
        self.errors: list[BaseException] = []
        self.emitted_ns: list[int] = []
        world = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args: Any) -> None:
                pass

            def do_POST(self) -> None:
                try:
                    size = int(self.headers.get("Content-Length", "0"))
                    body = json.loads(self.rfile.read(size))
                    world.requests.append({"path": self.path, "body": body})
                    packet = world.packets.popleft()
                    if "respond" in packet:
                        packet = packet["respond"](body)
                    if packet.get("disconnect"):
                        self.connection.shutdown(socket.SHUT_RDWR)
                        return
                    if "partial_header" in packet:
                        self.wfile.write(packet["partial_header"])
                        self.wfile.flush()
                        self.connection.shutdown(socket.SHUT_RDWR)
                        return
                    time.sleep(packet.get("header_delay_s", 0))
                    self.send_response(packet.get("status", 200))
                    is_json = "json" in packet
                    self.send_header("Content-Type", "application/json" if is_json else "text/event-stream")
                    self.end_headers()
                    if is_json:
                        self.wfile.write(json.dumps(packet["json"]).encode())
                    else:
                        self.wfile.write(b": heartbeat\n\n")
                        for index, chunk in enumerate(packet.get("chunks", [])):
                            time.sleep(packet.get("delays_s", {}).get(index, 0))
                            world.emitted_ns.append(time.monotonic_ns())
                            self.wfile.write(("data: " + json.dumps(chunk) + "\n\n").encode())
                            self.wfile.flush()
                        if not packet.get("omit_done"):
                            self.wfile.write(b"data: [DONE]\n\n")
                except (BrokenPipeError, ConnectionResetError):
                    pass
                except BaseException as exc:
                    world.errors.append(exc)

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.url = "http://127.0.0.1:" + str(self.server.server_address[1]) + "/v1"

    def __enter__(self) -> "HTTPWorld":
        self._proxy_patch = patch.dict("os.environ", {"NO_PROXY": "127.0.0.1", "no_proxy": "127.0.0.1"})
        self._proxy_patch.start()
        self.thread.start()
        return self

    def __exit__(self, *args: Any) -> None:
        self.server.shutdown()
        self.thread.join()
        self.server.server_close()
        self._proxy_patch.stop()
        if self.errors:
            raise self.errors[0]


class EndpointTests(unittest.TestCase):
    def chat(self, endpoint: ChatEndpoint, messages: tuple[ChatMessage, ...] = ()) -> Any:
        return endpoint.chat(messages, max_tokens=1024, temperature=0.0, seed=17)

    def test_stream_both_flavours_and_history(self) -> None:
        for flavour in ("vllm", "llamacpp"):
            with self.subTest(flavour=flavour), HTTPWorld([
                stream_packets(flavour=flavour, calls=(
                    {"id": "call_read", "name": "read_ledger", "arguments": {"batch": 12}},
                    {"id": "call_list", "name": "list_invoices", "arguments": {}})),
                stream_packets(flavour=flavour, reasoning="", hidden=0),
            ]) as world:
                client = OpenAICompatEndpoint(world.url, "local-8b", timeout_s=5)
                self.assertIsInstance(client, ChatEndpoint)
                self.assertIsInstance(client, TokenCounter)
                result = self.chat(client, (ChatMessage("user", "Reconcile the last quarter."),))
                # Server counters are integers, so bit identity is the accounting property.
                self.assertEqual((result.prompt_tokens, result.cached_prompt_tokens,
                                  result.completion_tokens, result.reasoning_tokens),
                                 (4096, 3072, 512, 384 if flavour == "vllm" else 0))
                self.assertEqual(result.reasoning_text, "Plan carefully.")
                self.assertEqual(result.content, "Done.")
                self.assertEqual(result.tool_calls[0], ToolCallRequest(
                    "call_read", "read_ledger", '{"batch": 12}'))
                self.assertEqual(len(result.tool_calls), 2)
                self.assertLessEqual(result.start_ns, result.first_token_ns)
                self.assertLessEqual(result.first_token_ns, result.end_ns)
                self.assertEqual(result.raw_usage["joulewise"]["flags"],
                                 [] if flavour == "vllm" else ["reasoning_tokens_unreported"])
                if flavour == "llamacpp":
                    # Exact equality compares untouched JSON, not independent measurements.
                    self.assertEqual(result.raw_usage["timings"],
                                     {"cache_n": 3072, "prompt_n": 1024, "predicted_n": 512,
                                      "prompt_ms": 240.5, "predicted_ms": 8640.25})
                # Protocol-only callers lack tool_calls on ChatMessage. Recover from result IDs.
                self.chat(client, (ChatMessage("assistant", result.content),
                                   ChatMessage("tool", "ledger rows", name="read_ledger",
                                               tool_call_id="call_read"),
                                   ChatMessage("tool", "invoice rows", name="list_invoices",
                                               tool_call_id="call_list")))
                sent = world.requests[1]["body"]["messages"][0]["tool_calls"]
                self.assertEqual([c["id"] for c in sent], ["call_read", "call_list"])
                self.assertTrue(world.requests[0]["body"]["stream_options"]["include_usage"])

    def test_vllm_default_cache_usage_is_unknown_on_every_turn(self) -> None:
        # Growing 4K+ prompts with whole 16-token KV-block reuse model a
        # multi-turn vLLM session. All counts are scripted integers; no
        # measured/derived agreement bar is needed for exact accounting.
        packets = []
        truths = []
        for turn in range(3):
            prompt, cached = 4096 + 512 * turn, 3072 + 512 * turn
            packet = stream_packets(prompt=prompt, cached=cached)
            del packet["chunks"][-1]["usage"]["prompt_tokens_details"]
            packets.append(packet)
            truths.append((prompt, cached))
        # A reported zero, usage-level count and timings count are all known.
        explicit_zero = stream_packets(cached=0)
        usage_level = stream_packets(cached=3072)
        usage_level["chunks"][-1]["usage"].pop("prompt_tokens_details")
        usage_level["chunks"][-1]["usage"]["cached_tokens"] = 3072
        timing_level = stream_packets(flavour="llamacpp", cached=3072)
        timing_level["chunks"][-1]["usage"].pop("prompt_tokens_details")
        with HTTPWorld(packets + [explicit_zero, usage_level, timing_level]) as world:
            client = OpenAICompatEndpoint(world.url, "local-8b", timeout_s=5)
            messages = [ChatMessage("user", "Review the next ledger page.")]
            for prompt, cached in truths:
                result = self.chat(client, tuple(messages))
                self.assertEqual(result.prompt_tokens, prompt)
                self.assertEqual(result.cached_prompt_tokens, 0)
                self.assertIn("cached_prompt_tokens_unreported",
                              result.raw_usage["joulewise"]["flags"])
                messages.append(assistant_message(result))
                messages.append(ChatMessage("user", "Continue the review."))
            self.assertIn("cached_prompt_tokens_unreported", client.flags)
            for expected in (0, 3072, 3072):
                result = self.chat(client)
                self.assertEqual(result.cached_prompt_tokens, expected)
                self.assertNotIn("cached_prompt_tokens_unreported",
                                 result.raw_usage["joulewise"]["flags"])

    def test_tokenize_has_the_same_special_token_rule_on_both_backends(self) -> None:
        text = "one two three four five six seven eight nine ten"
        for flavour in ("vllm", "llamacpp"):
            def respond(body):
                if flavour == "vllm":
                    count = len(body["prompt"].split()) + int(body.get("add_special_tokens", True))
                    return {"json": {"count": count}}
                count = len(body["content"].split()) + int(body.get("add_special", False))
                return {"json": {"tokens": list(range(count))}}
            with self.subTest(flavour=flavour), HTTPWorld([{"respond": respond}]) as world:
                client = OpenAICompatEndpoint(world.url, "local-bos-model", timeout_s=5)
                # Synthetic tokenizer has exactly one token per word; BOS would
                # add one. Exact equality detects that per-call backend bias.
                self.assertEqual(client.count_tokens(text), len(text.split()))
                self.assertIs(world.requests[0]["body"]["add_special_tokens"], False)
                self.assertIs(world.requests[0]["body"]["add_special"], False)

    def test_first_token_tracks_reasoning_and_tool_generation(self) -> None:
        # This is the reviewer's timing world: 200 ms prefill, then six
        # reasoning deltas 100 ms apart. A 50 ms bar is half the smallest
        # wrong-delta offset (100 ms); stamping role is about 200 ms early.
        for flavour in ("vllm", "llamacpp"):
            for thinking, tool in ((True, False), (True, True), (False, True), (False, False)):
                key = "reasoning" if flavour == "vllm" else "reasoning_content"
                generated = ([{key: "step %d of the private plan. " % n} for n in range(6)]
                             if thinking else [])
                generated.append({"tool_calls": [{"index": 0, "id": "c",
                    "function": {"name": "end_task", "arguments": "{}"}}]} if tool else {"content": "Done."})
                packet = stream_packets(flavour=flavour, hidden=42 if thinking else 0)
                packet["chunks"] = (
                    [{"choices": [{"index": 0, "delta": {"role": "assistant"}}]}]
                    + [{"choices": [{"index": 0, "delta": d}]} for d in generated]
                    + packet["chunks"][-2:])
                packet["delays_s"] = {1: 0.20, **{i: 0.10 for i in range(2, len(generated) + 1)}}
                with self.subTest(flavour=flavour, thinking=thinking, tool=tool), HTTPWorld([packet]) as world:
                    result = self.chat(OpenAICompatEndpoint(world.url, "local", timeout_s=5))
                    self.assertIsNotNone(result.first_token_ns)
                    self.assertLess(abs(result.first_token_ns - world.emitted_ns[1]), 50_000_000)
                    self.assertEqual(len(result.reasoning_text), 168 if thinking else 0)
                    self.assertEqual(len(result.tool_calls), int(tool))

    def test_empty_reasoning_delta_is_not_unreported_work(self) -> None:
        cases = (
            ("", 0, True, False),
            ("", 0, False, False),
            ("Plan carefully.", 0, True, True),
            ("Plan carefully.", 0, False, True),
            ("Plan carefully.", 384, True, False),
        )
        for flavour in ("vllm", "llamacpp"):
            for reasoning, hidden, reported, flagged in cases:
                with self.subTest(flavour=flavour, reasoning=reasoning, reported=reported,
                                  hidden=hidden):
                    packet = stream_packets(flavour=flavour, reasoning=reasoning, hidden=hidden)
                    if not reported:
                        packet["chunks"][-1]["usage"].pop("completion_tokens_details", None)
                    with HTTPWorld([packet]) as world:
                        client = OpenAICompatEndpoint(world.url, "local", timeout_s=5)
                        result = self.chat(client)
                    self.assertEqual(result.reasoning_text, reasoning)
                    # Exact server integers; missing counts retain the contract's zero.
                    expected = hidden if flavour == "vllm" and reported else 0
                    self.assertEqual(result.reasoning_tokens, expected)
                    flagged = bool(reasoning) and expected == 0
                    self.assertEqual("reasoning_tokens_unreported" in
                                     result.raw_usage["joulewise"]["flags"], flagged)
                    self.assertEqual("reasoning_tokens_unreported" in client.flags, flagged)

    def test_derived_reasoning_count_is_opt_in_and_never_a_server_counter(self) -> None:
        pieces = ["Check invoice 1. ", "Check invoice 2. ", "Reconcile totals."]
        thought = "".join(pieces)
        def tokenize(body):
            self.assertEqual(body["content"], thought)
            self.assertIs(body["add_special_tokens"], False)
            self.assertIs(body["add_special"], False)
            # This synthetic tokenizer counts joined text, as a real /tokenize
            # call does; the exact integer is not a server completion counter.
            return {"json": {"tokens": list(range(len(thought) // 4))}}
        packet = stream_packets(flavour="llamacpp", reasoning=thought)
        with HTTPWorld([packet]) as world:
            default = self.chat(OpenAICompatEndpoint(world.url, "local", timeout_s=5))
            self.assertEqual(len(world.requests), 1)
            self.assertNotIn("derived_reasoning_tokens", default.raw_usage["joulewise"])
        with HTTPWorld([packet, {"respond": tokenize}]) as world:
            client = OpenAICompatEndpoint(world.url, "local", timeout_s=5,
                                          derive_reasoning_tokens=True)
            result = self.chat(client)
            diagnostic = result.raw_usage["joulewise"]["derived_reasoning_tokens"]
            self.assertEqual(diagnostic["count"], len(thought) // 4)
            self.assertEqual(diagnostic["source"], "server:/tokenize")
            self.assertEqual(result.reasoning_tokens, 0)
            self.assertEqual(result.completion_tokens, 512)
            self.assertIn("reasoning_tokens_unreported", result.raw_usage["joulewise"]["flags"])
            self.assertIn("reasoning_tokens_derived_from_tokenize", client.flags)
            self.assertEqual([r["path"] for r in world.requests],
                             ["/v1/chat/completions", "/tokenize"])
        with HTTPWorld([packet, {"status": 503, "json": {"error": "unavailable"}}]) as world:
            result = self.chat(OpenAICompatEndpoint(world.url, "local", timeout_s=5,
                                                     derive_reasoning_tokens=True))
            self.assertIsNone(result.raw_usage["joulewise"]["derived_reasoning_tokens"]["count"])
            self.assertEqual(result.reasoning_tokens, 0)
            self.assertIn("reasoning_tokenize_unavailable", result.raw_usage["joulewise"]["flags"])

    def test_tokenize_both_shapes(self) -> None:
        worlds = [
            ([{"json": {"count": 120, "tokens": list(range(120))}}], 1),
            ([{"respond": lambda body: {"json": {"tokens": list(range(
                len(body.get("content", "").split())))}}}], 1),
            ([{"json": {"tokens": []}},
              {"json": {"tokens": [{"id": n, "piece": "x"} for n in range(120)]}}], 2),
            ([{"status": 422, "json": {"error": "schema"}},
              {"json": {"tokens": list(range(120))}}], 2),
        ]
        for packets, count in worlds:
            with HTTPWorld(packets) as world:
                client = OpenAICompatEndpoint(world.url, "local", timeout_s=5)
                self.assertEqual(client.count_tokens("invoice " * 120), 120)
                self.assertEqual(len(world.requests), count)
                self.assertTrue(all(r["path"] == "/tokenize" for r in world.requests))
                self.assertEqual(world.requests[0]["body"]["content"], "invoice " * 120)
                self.assertTrue(any(flag.startswith("tokenize_shape:") for flag in client.flags))
                if count == 2:
                    self.assertEqual(world.requests[-1]["body"],
                                     {"content": "invoice " * 120,
                                      "add_special_tokens": False, "add_special": False})

    def test_retry_only_before_any_response_byte(self) -> None:
        cases = [
            ([{"disconnect": True}], 1, False),
            ([{"partial_header": b"HTTP/1.1 "}], 1, False),
            ([{"status": 503, "json": {"error": "unavailable"}}], 1, False),
            ([{**stream_packets(), "omit_done": True}], 1, False),
        ]
        for packets, requests, retried in cases:
            with self.subTest(packets=packets[0].keys()), HTTPWorld(packets) as world:
                client = OpenAICompatEndpoint(world.url, "local", timeout_s=5, max_retries=1)
                if "omit_done" in packets[0]:
                    result = self.chat(client)  # Complete usage survived the missing sentinel.
                else:
                    with self.assertRaises(EndpointRequestFailed) as caught:
                        self.chat(client)
                    result = caught.exception.partial_result
                self.assertEqual(len(world.requests), requests)
                self.assertEqual(bool(result.raw_usage["joulewise"]["retries"]), retried)
                if retried:
                    self.assertEqual(result.raw_usage["joulewise"]["retries"][0]["received_bytes"], 0)
                else:
                    self.assertIn("stream_missing_done", result.raw_usage["joulewise"]["flags"])

    def test_retry_connect_failure_but_never_a_sent_request_timeout(self) -> None:
        connect = http.client.HTTPConnection.connect
        attempts = []

        def fail_first(conn):
            attempts.append(True)
            if len(attempts) == 1:
                raise ConnectionRefusedError("synthetic failed connect")
            return connect(conn)

        with HTTPWorld([stream_packets()]) as world:
            with patch.object(http.client.HTTPConnection, "connect", fail_first):
                client = OpenAICompatEndpoint(world.url, "local", timeout_s=5)
                result = self.chat(client)
            self.assertEqual(len(world.requests), 1)
            self.assertEqual(len(attempts), 2)
            self.assertEqual(len(result.raw_usage["joulewise"]["retries"]), 1)
        # Operator transport budgets: delay exceeds timeout to force the
        # post-send failure. Only exact request/retry counts are asserted.
        with HTTPWorld([{**stream_packets(), "header_delay_s": 0.15}]) as world:
            client = OpenAICompatEndpoint(world.url, "local", timeout_s=0.05)
            with self.assertRaises(EndpointRequestFailed) as caught:
                self.chat(client)
            result = caught.exception.partial_result
            self.assertEqual(len(world.requests), 1)
            self.assertEqual(client.retries, [])
            self.assertIn("request_timeout_after_connect", result.raw_usage["joulewise"]["flags"])

    def test_repeated_identifiers_conflicts_and_generation_caps(self) -> None:
        chunks = [
            {"choices": [{"index": 0, "delta": {"tool_calls": [{"index": 0,
                "id": "c1", "function": {"name": "end_task", "arguments": "{"}}]}}]},
            {"choices": [{"index": 0, "delta": {"tool_calls": [{"index": 0,
                "id": "c1", "function": {"name": "end_task", "arguments": "}"}}]}}]},
            {"choices": [{"index": 0, "delta": {}, "finish_reason": "length"}]},
            {"choices": [], "usage": {"prompt_tokens": 4096, "completion_tokens": 512}},
        ]
        conflicting = json.loads(json.dumps(chunks))
        conflicting[1]["choices"][0]["delta"]["tool_calls"][0].update(
            id="other", function={"name": "other", "arguments": "}"})
        with HTTPWorld([{"chunks": chunks}, {"chunks": conflicting}]) as world:
            client = OpenAICompatEndpoint(world.url, "local", timeout_s=5)
            first, second = self.chat(client), self.chat(client)
            self.assertEqual(first.tool_calls, (ToolCallRequest("c1", "end_task", "{}"),))
            self.assertNotIn("tool_call_id_conflict", first.raw_usage["joulewise"]["flags"])
            self.assertIn("tool_call_id_conflict", second.raw_usage["joulewise"]["flags"])
            self.assertIn("tool_call_name_conflict", second.raw_usage["joulewise"]["flags"])
            self.assertEqual(first.raw_usage["joulewise"]["finish_reason"], "length")
            self.assertIn("generation_cap_reached", first.raw_usage["joulewise"]["flags"])

    def test_missing_counts_and_unsafe_url_are_flags(self) -> None:
        with HTTPWorld([{"chunks": [{"choices": [{"delta": {"content": "partial"}}]}]}]) as world:
            client = OpenAICompatEndpoint(world.url, "local", timeout_s=5)
            with self.assertRaises(EndpointRequestFailed) as caught:
                self.chat(client)
            result = caught.exception.partial_result
            self.assertEqual(result.prompt_tokens, 0)
            self.assertEqual(result.content, "partial")
            self.assertEqual(caught.exception.flags, tuple(result.raw_usage["joulewise"]["flags"]))
            self.assertIn("usage_unavailable", caught.exception.flags)
            self.assertIn("missing_or_invalid_prompt_tokens", result.raw_usage["joulewise"]["flags"])
        client = OpenAICompatEndpoint("file:///unavailable", "local", timeout_s=5)
        with self.assertRaises(EndpointRequestFailed) as caught:
            self.chat(client)
        self.assertIn("invalid_base_url", caught.exception.flags)
        self.assertEqual(client.count_tokens("anything"), 0)

    def test_llamacpp_timings_fallback_preserves_accounting(self) -> None:
        timings = {"prompt_n": 1024, "cache_n": 3072, "predicted_n": 768}
        with HTTPWorld([{"chunks": [
            {"choices": [{"index": 0, "delta": {"content": "Complete."}}]},
            {"choices": [], "timings": timings},
        ]}]) as world:
            result = self.chat(OpenAICompatEndpoint(world.url, "local", timeout_s=5))
            # Exact integer record: total prompt = processed + cached positions.
            self.assertEqual((result.prompt_tokens, result.cached_prompt_tokens,
                              result.completion_tokens), (4096, 3072, 768))
            self.assertEqual(result.raw_usage["timings"], timings)
            self.assertIn("prompt_tokens_from_timings", result.raw_usage["joulewise"]["flags"])



    def test_partial_reasoning_failures_preserve_evidence_and_never_retry(self) -> None:
        # The server emits exactly 120 synthetic reasoning tokens before either
        # closing or exceeding an operator transport budget; no timing bar is used.
        deltas = [{"choices": [{"index": 0, "delta": {"reasoning": "think "}}]}] * 120
        for mode in ("http400", "stall", "cut", "missing_usage", "invalid_usage"):
            with self.subTest(mode=mode):
                packet = {"chunks": list(deltas), "omit_done": True}
                if mode == "http400":
                    packet = {"status": 400, "json": {"error": "context length exceeded"}}
                elif mode == "stall":
                    # Delay exceeds timeout to force a failure after generated bytes.
                    packet["chunks"].append({"choices": []})
                    packet["delays_s"] = {len(deltas): 0.15}
                elif mode in ("missing_usage", "invalid_usage"):
                    packet["omit_done"] = False
                    if mode == "invalid_usage":
                        packet["chunks"].append({"choices": [], "usage": {
                            "prompt_tokens": 5000, "completion_tokens": None}})
                with HTTPWorld([packet]) as world:
                    client = OpenAICompatEndpoint(world.url, "local", timeout_s=0.05)
                    with self.assertRaises(EndpointRequestFailed) as caught:
                        self.chat(client)
                    partial = caught.exception.partial_result
                    self.assertEqual(len(world.requests), 1)
                    self.assertEqual(client.retries, [])
                    self.assertIn("usage_unavailable", caught.exception.flags)
                    if mode == "http400":
                        self.assertIn("http_error:400", caught.exception.flags)
                        self.assertIsNone(partial.first_token_ns)
                    else:
                        self.assertEqual(partial.reasoning_text, "think " * 120)
                        self.assertIsNotNone(partial.first_token_ns)
                    if mode == "stall":
                        self.assertTrue(any(f.startswith("transport_or_stream_error:")
                                            for f in caught.exception.flags))

    def test_runner_call_records_become_one_assistant_wire_message(self) -> None:
        calls = (ToolCallRequest("c1", "approve_invoice", '{"invoice_id": "INV-001"}'),
                 ToolCallRequest("c2", "approve_invoice", '{"invoice_id": "INV-002"}'))
        messages = [ChatMessage("system", "s"), ChatMessage("user", "Review."),
                    ChatMessage("assistant", "<jw_reasoning>private</jw_reasoning>Approving two.")]
        for call in calls:
            messages.extend((ChatMessage("assistant", call.arguments_json, call.name, call.call_id),
                             ChatMessage("tool", "Approved", call.name, call.call_id)))
        with HTTPWorld([stream_packets()]) as world:
            endpoint = OpenAICompatEndpoint(world.url, "local", timeout_s=5)
            endpoint._requests.update((call.call_id, call) for call in calls)
            endpoint.chat(messages, max_tokens=2048, temperature=0.0, seed=7)
            wire = world.requests[0]["body"]["messages"]
        self.assertEqual([m["role"] for m in wire],
                         ["system", "user", "assistant", "tool", "tool"])
        self.assertEqual(wire[2]["content"], messages[2].content)
        self.assertEqual(wire[2]["tool_calls"], [
            {"id": c.call_id, "type": "function",
             "function": {"name": c.name, "arguments": c.arguments_json}} for c in calls])
        self.assertNotIn("tool_call_id", wire[2])
        self.assertEqual([m["tool_call_id"] for m in wire[3:]], ["c1", "c2"])

    def test_assistant_extension_and_mock_are_deterministic(self) -> None:
        script = [{"content": "read", "reasoning_text": "plan", "prompt_tokens": 2048,
                   "completion_tokens": 256, "reasoning_tokens": 128,
                   "tool_calls": [{"call_id": "a", "name": "read", "arguments_json": "{}"}]}]
        one, two = MockEndpoint(script), MockEndpoint(script)
        self.assertIsInstance(one, ChatEndpoint)
        self.assertIsInstance(one, TokenCounter)
        result = self.chat(one)
        self.assertEqual(result, self.chat(two))
        self.assertEqual(assistant_message(result).tool_calls, result.tool_calls)
        exact = MockEndpoint([result], token_counts={"known": 7})
        self.assertIs(self.chat(exact), result)
        self.assertEqual(exact.count_tokens("known"), 7)
        self.assertIn("mock_script_exhausted", self.chat(exact).raw_usage["joulewise"]["flags"])


if __name__ == "__main__":
    unittest.main()
