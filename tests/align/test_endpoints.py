"""Offline HTTP worlds for streaming, accounting, tokenization and retries."""

from __future__ import annotations

import json
import socket
import threading
import unittest
from collections import deque
from contextlib import AbstractContextManager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from unittest.mock import patch

from joulewise.align.endpoints import MockEndpoint, OpenAICompatEndpoint, assistant_message
from joulewise.align.interfaces import ChatEndpoint, ChatMessage, TokenCounter, ToolCallRequest


def stream_packets(*, flavour: str = "vllm", content: str = "Done.",
                   reasoning: str = "Plan carefully.", calls: tuple[dict, ...] = (),
                   prompt: int = 4096, cached: int = 3072, completion: int = 512,
                   hidden: int = 384) -> dict[str, Any]:
    """A production-sized accounting record; all counts are exact fixture integers."""
    chunks = [
        {"choices": [{"index": 0, "delta": {"role": "assistant"}}]},
        {"choices": [{"index": 0, "delta": {"reasoning_content": reasoning}}]},
        {"choices": [{"index": 0, "delta": {"content": content}}]},
    ]
    for index, call in enumerate(calls):
        name = call["name"]
        arguments = json.dumps(call["arguments"])
        # Split both function name and JSON across SSE records, as servers do.
        split = len(arguments) // 2
        chunks.extend([
            {"choices": [{"index": 0, "delta": {"tool_calls": [
                {"index": index, "id": call["id"], "type": "function",
                 "function": {"name": name[:len(name) // 2], "arguments": arguments[:split]}}]}}]},
            {"choices": [{"index": 0, "delta": {"tool_calls": [
                {"index": index, "function": {"name": name[len(name) // 2:],
                                             "arguments": arguments[split:]}}]}}]},
        ])
    final = {"choices": [], "usage": {
        "prompt_tokens": prompt, "completion_tokens": completion,
        "prompt_tokens_details": {"cached_tokens": cached},
        "completion_tokens_details": {"reasoning_tokens": hidden},
    }}
    if flavour == "llamacpp":
        # llama.cpp supplies timings alongside OpenAI usage; preserve every field.
        final["timings"] = {"cache_n": cached, "prompt_n": prompt - cached,
                            "predicted_n": completion, "prompt_ms": 240.5, "predicted_ms": 8640.25}
    chunks.append(final)
    return {"chunks": chunks}


class HTTPWorld(AbstractContextManager):
    """Loopback only; arbitrary scripted SSE/JSON/status/disconnect responses."""

    def __init__(self, packets: list[dict[str, Any]]) -> None:
        self.packets = deque(packets)
        self.requests: list[dict[str, Any]] = []
        self.errors: list[BaseException] = []
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
                    self.send_response(packet.get("status", 200))
                    is_json = "json" in packet
                    self.send_header("Content-Type", "application/json" if is_json else "text/event-stream")
                    self.end_headers()
                    if is_json:
                        self.wfile.write(json.dumps(packet["json"]).encode())
                    else:
                        self.wfile.write(b": heartbeat\n\n")
                        for chunk in packet.get("chunks", []):
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
                                 (4096, 3072, 512, 384))
                self.assertEqual(result.reasoning_text, "Plan carefully.")
                self.assertEqual(result.content, "Done.")
                self.assertEqual(result.tool_calls[0], ToolCallRequest(
                    "call_read", "read_ledger", '{"batch": 12}'))
                self.assertEqual(len(result.tool_calls), 2)
                self.assertLessEqual(result.start_ns, result.first_token_ns)
                self.assertLessEqual(result.first_token_ns, result.end_ns)
                self.assertEqual(result.raw_usage["joulewise"]["flags"], [])
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

    def test_first_token_is_reasoning_or_content_never_role_or_tool(self) -> None:
        with HTTPWorld([stream_packets(content="", reasoning="", hidden=0, calls=(
                {"id": "only", "name": "end_task", "arguments": {}},))]) as world:
            result = self.chat(OpenAICompatEndpoint(world.url, "local", timeout_s=5))
            self.assertIsNone(result.first_token_ns)

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
                        del packet["chunks"][-1]["usage"]["completion_tokens_details"]
                    with HTTPWorld([packet]) as world:
                        client = OpenAICompatEndpoint(world.url, "local", timeout_s=5)
                        result = self.chat(client)
                    self.assertEqual(result.reasoning_text, reasoning)
                    # Exact server integers; missing counts retain the contract's zero.
                    self.assertEqual(result.reasoning_tokens, hidden)
                    self.assertEqual("reasoning_tokens_unreported" in
                                     result.raw_usage["joulewise"]["flags"], flagged)
                    self.assertEqual("reasoning_tokens_unreported" in client.flags, flagged)

    def test_tokenize_both_shapes(self) -> None:
        worlds = [
            ([{"json": {"count": 120, "tokens": list(range(120))}}], 1),
            ([{"status": 400, "json": {"error": "content required"}},
              {"json": {"tokens": [{"id": n, "piece": "x"} for n in range(120)]}}], 2),
        ]
        for packets, count in worlds:
            with HTTPWorld(packets) as world:
                client = OpenAICompatEndpoint(world.url, "local", timeout_s=5)
                self.assertEqual(client.count_tokens("invoice " * 120), 120)
                self.assertEqual(len(world.requests), count)
                self.assertTrue(all(r["path"] == "/tokenize" for r in world.requests))
                if count == 2:
                    self.assertEqual(world.requests[-1]["body"], {"content": "invoice " * 120})

    def test_retry_only_before_any_response_byte(self) -> None:
        cases = [
            ([{"disconnect": True}, stream_packets()], 2, True),
            ([{"partial_header": b"HTTP/1.1 "}], 1, False),
            ([{"status": 503, "json": {"error": "unavailable"}}], 1, False),
            ([{**stream_packets(), "omit_done": True}], 1, False),
        ]
        for packets, requests, retried in cases:
            with self.subTest(packets=packets[0].keys()), HTTPWorld(packets) as world:
                client = OpenAICompatEndpoint(world.url, "local", timeout_s=5, max_retries=1)
                result = self.chat(client)
                self.assertEqual(len(world.requests), requests)
                self.assertEqual(bool(result.raw_usage["joulewise"]["retries"]), retried)
                if retried:
                    self.assertEqual(result.raw_usage["joulewise"]["retries"][0]["received_bytes"], 0)
                else:
                    self.assertIn("stream_missing_done", result.raw_usage["joulewise"]["flags"])

    def test_missing_counts_and_unsafe_url_are_flags(self) -> None:
        with HTTPWorld([{"chunks": [{"choices": [{"delta": {"content": "partial"}}]}]}]) as world:
            client = OpenAICompatEndpoint(world.url, "local", timeout_s=5)
            result = self.chat(client)
            self.assertEqual(result.prompt_tokens, 0)
            self.assertIn("missing_or_invalid_prompt_tokens", result.raw_usage["joulewise"]["flags"])
        client = OpenAICompatEndpoint("file:///unavailable", "local", timeout_s=5)
        self.assertIn("invalid_base_url", self.chat(client).raw_usage["joulewise"]["flags"])
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
