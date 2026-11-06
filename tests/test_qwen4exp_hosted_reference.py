"""Tests for the hosted-reference client: no paid API is ever contacted.

Request building and the live path run against an in-process fake poster or a
local http.server on 127.0.0.1. Template-dependent tests need jinja2 (use an
approved venv: /private/tmp/jwsol/venv-mlx/bin/python).
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import math
import random
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from scripts import qwen4exp_e2e_eval as e2e
from scripts import qwen4exp_hosted_reference as hosted

HAS_JINJA = importlib.util.find_spec("jinja2") is not None


class MathTests(unittest.TestCase):
    def test_bucketed_kl_is_zero_for_identical_and_a_lower_bound(self):
        rng = random.Random(7)
        for _ in range(50):
            raw_p = [rng.random() ** 3 for _ in range(40)]
            raw_q = [x * math.exp(rng.gauss(0, 0.5)) for x in raw_p]
            p = [x / sum(raw_p) for x in raw_p]
            q = [x / sum(raw_q) for x in raw_q]
            full = sum(a * math.log(a / b) for a, b in zip(p, q))
            top = sorted(range(40), key=lambda i: -p[i])[:5]
            hosted_top = [(i, math.log(p[i])) for i in top]
            local = {i: math.log(q[i]) for i in top}
            bucketed = hosted.bucketed_kl(hosted_top, local)
            self.assertLessEqual(bucketed, full + 1e-12)
            self.assertAlmostEqual(hosted.bucketed_kl(hosted_top, {i: math.log(p[i]) for i in top}), 0.0, places=12)

    def test_bucketed_kl_needs_every_hosted_token(self):
        self.assertIsNone(hosted.bucketed_kl([(1, -0.1), (2, -3.0)], {1: -0.1}))
        self.assertIsNone(hosted.bucketed_kl([], {}))


class NormalizeTests(unittest.TestCase):
    def test_chat_response_with_logprobs(self):
        provider = hosted.PROVIDERS["dashscope-intl"]
        response = {"id": "r1", "model": "qwen3.8-flash", "usage": {"prompt_tokens": 12, "completion_tokens": 2},
                    "choices": [{"finish_reason": "length", "message": {"content": "Hi"},
                                 "logprobs": {"content": [
                                     {"token": "H", "logprob": -0.1, "bytes": [72],
                                      "top_logprobs": [{"token": "H", "logprob": -0.1, "bytes": [72]},
                                                       {"token": "Y", "logprob": -2.5, "bytes": [89]}]}]}}]}
        record = hosted.normalize_response(provider, {"prompt_id": "p", "request_sha256": "x",
                                                      "rendered_prompt_sha256": "y"}, response, 0)
        self.assertEqual(record["text"], "Hi")
        self.assertEqual(record["prompt_tokens_reported"], 12)
        self.assertEqual(record["tokens"][0]["bytes"], [72])
        self.assertEqual(len(record["tokens"][0]["top"]), 2)
        self.assertFalse(record["weight_identical"])
        self.assertEqual(record["flags"], [])

    def test_completions_response_vllm_token_ids_and_missing_logprobs(self):
        provider = hosted.PROVIDERS["vllm-selfhost"]
        response = {"choices": [{"text": "ab", "finish_reason": "length",
                                 "logprobs": {"tokens": ["token_id:97", "token_id:98"], "token_logprobs": [-0.2, -0.3],
                                              "top_logprobs": [{"token_id:97": -0.2}, {"token_id:98": -0.3, "token_id:99": -2.0}]}}]}
        record = hosted.normalize_response(provider, {"prompt_id": "p", "request_sha256": "x",
                                                      "rendered_prompt_sha256": "y"}, response, 1)
        self.assertEqual([t["token_id"] for t in record["tokens"]], [97, 98])
        self.assertEqual([t["token_id"] for t in record["tokens"][1]["top"]], [98, 99])
        featherless = hosted.normalize_response(hosted.PROVIDERS["featherless"], {"prompt_id": "p", "request_sha256": "x",
                                                "rendered_prompt_sha256": "y"},
                                                {"choices": [{"text": "ab", "logprobs": None}]}, 0)
        self.assertEqual(featherless["flags"], ["logprobs_unavailable"])

    def test_token_mapper(self):
        adapter = e2e.ScriptedAdapter([])
        mapper = hosted.TokenMapper(adapter)
        self.assertEqual(mapper.map({"token_id": 5}), 5)
        self.assertEqual(mapper.map({"bytes": [97]}), 97)
        self.assertEqual(mapper.map({"token": "<|im_end|>"}), e2e.SPECIAL_TOKENS["<|im_end|>"])
        self.assertIsNone(mapper.map({"token": "ab"}))

        class ByteVocab:  # adapter without token_id_for_bytes: reverse map from token_bytes
            vocab_size = 4

            def token_bytes(self, token_id):
                return [b"a", b"\xe4\xb8", b" the", b"<think>"][token_id]

        mapper = hosted.TokenMapper(ByteVocab())
        self.assertEqual(mapper.map({"token": " the"}), 2)
        self.assertEqual(mapper.map({"token": "bytes:\\xe4\\xb8"}), 1)
        self.assertEqual(mapper.map({"token": "<think>"}), 3)


def stub_traces(adapter, requests, *, perturb=0.0, logprobs=True):
    """Hosted traces generated from the stub itself (a perfect reference)."""
    traces = []
    for request in requests.values():
        prompt_ids = adapter.encode(request["rendered_prompt"])
        generation = adapter.generate(prompt_ids, max_tokens=16, top_k=2)
        tokens = []
        for token, lp, top in zip(generation.token_ids, generation.token_logprobs, generation.top_logprobs):
            tokens.append({"token": adapter.decode([token]), "bytes": list(adapter.token_bytes(token)), "token_id": None,
                           "logprob": lp, "top": [{"token": adapter.decode([t]), "bytes": list(adapter.token_bytes(t)),
                                                   "token_id": None, "logprob": v + perturb * (i + 1)}
                                                  for i, (t, v) in enumerate(top)]})
        traces.append({"schema": hosted.TRACE_SCHEMA, "provider": "fake", "prompt_id": request["prompt_id"],
                       "repeat": 0, "text": generation.text, "tokens": tokens if logprobs else [],
                       "flags": [] if logprobs else ["logprobs_unavailable"], "weight_identical": True,
                       "prompt_tokens_reported": len(prompt_ids)})
    return traces


@unittest.skipUnless(HAS_JINJA, "jinja2 not installed (use an approved venv)")
class RequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.template = e2e.ChatTemplate(e2e.TEMPLATE_PATHS[1])
        cls.prompts = hosted.load_prompts()

    def test_requests_are_deterministic_and_thinking_off_for_every_provider(self):
        for name, provider in hosted.PROVIDERS.items():
            with self.subTest(provider=name):
                requests = hosted.build_requests(provider, self.prompts, self.template)
                self.assertEqual(len(requests), len(self.prompts["prompts"]))
                again = hosted.build_requests(provider, self.prompts, self.template)
                self.assertEqual([r["request_sha256"] for r in requests], [r["request_sha256"] for r in again])
                for request in requests:
                    body = request["body"]
                    self.assertEqual(body["temperature"], 0.0)
                    self.assertEqual(body["presence_penalty"], 0.0)
                    self.assertEqual(body["frequency_penalty"], 0.0)
                    self.assertLessEqual(request["top_logprobs"], provider.max_top_logprobs)
                    self.assertTrue(request["rendered_prompt"].endswith("<think>\n\n</think>\n\n"))
                    if provider.route == "completions":
                        self.assertEqual(body["prompt"], request["rendered_prompt"])
                        self.assertNotIn("messages", body)
                    else:
                        self.assertIs(body["logprobs"], True)
                        self.assertNotIn("prompt", body)
                    for key, value in provider.extra_body.items():
                        self.assertEqual(body[key], value)
                    self.assertNotIn("Authorization", json.dumps(body))

    def test_long_context_prompt_exceeds_the_qsa_budget(self):
        long_prompt = next(p for p in self.prompts["prompts"] if p["id"] == "long_context_qsa")
        self.assertGreater(len(long_prompt["messages"][0]["content"]), 4 * 2048)

    def test_estimate_is_small_and_counts_repeats(self):
        provider = hosted.PROVIDERS["featherless"]
        requests = hosted.build_requests(provider, self.prompts, self.template)
        one = hosted.estimate(requests, provider, 1)
        two = hosted.estimate(requests, provider, 2)
        self.assertEqual(two["requests"], 2 * one["requests"])
        self.assertAlmostEqual(two["usd_upper_bound"], 2 * one["usd_upper_bound"], delta=2e-6)  # rounded to 1e-6
        self.assertLess(two["usd_upper_bound"], 0.05)

    def test_collect_guards(self):
        provider = hosted.PROVIDERS["dashscope-intl"]
        requests = hosted.build_requests(provider, self.prompts, self.template)
        cost = hosted.estimate(requests, provider, 1)
        calls = []

        def poster(url, body, key, timeout):
            calls.append((url, key))
            return {"choices": [{"message": {"content": "ok"}, "logprobs": None}]}

        logs = []
        self.assertEqual(hosted.collect(provider, requests, repeats=1, live=False, max_cost_usd=1, cost=cost,
                                        out=None, env={"DASHSCOPE_API_KEY": "k"}, poster=poster, log=logs.append), [])
        self.assertEqual(calls, [])
        self.assertIn("DRY RUN", logs[0])
        with self.assertRaisesRegex(hosted.CollectRefused, "DASHSCOPE_API_KEY"):
            hosted.collect(provider, requests, repeats=1, live=True, max_cost_usd=1, cost=cost, out=None,
                           env={}, poster=poster, log=logs.append)
        with self.assertRaisesRegex(hosted.CollectRefused, "exceeds"):
            hosted.collect(provider, requests, repeats=1, live=True, max_cost_usd=0.0, cost=cost, out=None,
                           env={"DASHSCOPE_API_KEY": "k"}, poster=poster, log=logs.append)
        self.assertEqual(calls, [])
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "t.jsonl"
            records = hosted.collect(provider, requests[:2], repeats=2, live=True, max_cost_usd=1, cost=cost,
                                     out=out, env={"DASHSCOPE_API_KEY": "secret-key"}, poster=poster, log=logs.append)
            self.assertEqual(len(records), 4)
            self.assertEqual(len(calls), 4)
            self.assertNotIn("secret-key", out.read_text())
            self.assertTrue(all("logprobs_unavailable" in r["flags"] for r in records))

    def test_compare_passes_a_perfect_reference_and_fails_a_perturbed_one(self):
        adapter = e2e.ScriptedAdapter([(r"photosynthesis", "Plants make sugar from light."),
                                       (r".", "A short answer.")], identity="stub")
        provider = hosted.PROVIDERS["featherless"]
        requests = {r["prompt_id"]: r for r in hosted.build_requests(provider, self.prompts, self.template)}
        good = hosted.compare(stub_traces(adapter, requests), adapter, requests, profile="bf16", top_k=2)
        self.assertTrue(good["quality_policy"]["doc"].endswith("quant_quality.md#pass-rules"))  # primary rule
        self.assertEqual(good["verdict"], "pass", json.dumps(good["checks"]))
        self.assertEqual(good["aggregate"]["top1_agreement"], 1.0)
        self.assertAlmostEqual(good["aggregate"]["bucketed_kl_mean"], 0.0, places=9)
        self.assertEqual(good["verdict_kind"], "gating")
        bad = hosted.compare(stub_traces(adapter, requests, perturb=-1.5), adapter, requests, profile="bf16", top_k=2)
        self.assertEqual(bad["verdict"], "fail")
        text_only = hosted.compare(stub_traces(adapter, requests, logprobs=False), adapter, requests,
                                   profile="bf16", top_k=2)
        self.assertEqual(text_only["aggregate"]["bucketed_kl_mean"], None)
        self.assertEqual(text_only["verdict"], "pass")
        self.assertTrue(all("retokenized_hosted_text" in p["flags"] for p in text_only["per_prompt"]))

    def test_non_identical_weights_make_the_verdict_advisory(self):
        adapter = e2e.ScriptedAdapter([(r".", "x")])
        provider = hosted.PROVIDERS["featherless"]
        requests = {r["prompt_id"]: r for r in hosted.build_requests(provider, self.prompts, self.template)}
        traces = stub_traces(adapter, requests)
        for trace in traces:
            trace["weight_identical"] = False
        self.assertTrue(hosted.compare(traces, adapter, requests, profile="bf16", top_k=2)["verdict_kind"]
                        .startswith("advisory"))

    def test_prompt_token_mismatch_is_flagged(self):
        adapter = e2e.ScriptedAdapter([(r".", "x")])
        provider = hosted.PROVIDERS["dashscope-intl"]
        requests = {r["prompt_id"]: r for r in hosted.build_requests(provider, self.prompts, self.template)}
        traces = stub_traces(adapter, requests)
        traces[0]["prompt_tokens_reported"] += 7
        report = hosted.compare(traces, adapter, requests, profile="bf16", top_k=2)
        self.assertTrue(any(f.startswith("prompt_token_count_mismatch") for f in report["per_prompt"][0]["flags"]))


class _FakeOpenAI(BaseHTTPRequestHandler):
    """Minimal OpenAI-compatible /v1/completions with vLLM-style logprobs."""

    seen: list = []

    def do_POST(self):  # noqa: N802 - http.server API
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        type(self).seen.append({"path": self.path, "auth": self.headers.get("Authorization"), "body": body})
        tokens = ["token_id:65", "token_id:66"]
        payload = {"id": "cmpl-1", "model": body["model"], "usage": {"prompt_tokens": 3, "completion_tokens": 2},
                   "choices": [{"text": "AB", "finish_reason": "length",
                                "logprobs": {"tokens": tokens, "token_logprobs": [-0.1, -0.2],
                                             "top_logprobs": [{"token_id:65": math.log(0.9), "token_id:32": math.log(0.05)},
                                                              {"token_id:66": math.log(0.9), "token_id:32": math.log(0.05)}]}}]}
        data = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


@unittest.skipUnless(HAS_JINJA, "jinja2 not installed (use an approved venv)")
class LocalServerTests(unittest.TestCase):
    def test_live_path_over_real_http_to_localhost(self):
        server = HTTPServer(("127.0.0.1", 0), _FakeOpenAI)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            url = f"http://127.0.0.1:{server.server_port}/v1"
            with tempfile.TemporaryDirectory() as directory:
                traces = Path(directory) / "traces.jsonl"
                with contextlib.redirect_stderr(io.StringIO()):
                    code = hosted.main(["collect", "--provider", "vllm-selfhost", "--base-url", url, "--live",
                                        "--repeats", "1", "--chat-template", str(e2e.TEMPLATE_PATHS[1]),
                                        "--traces", str(traces)])
                self.assertEqual(code, 0)
                records = [json.loads(line) for line in traces.read_text().splitlines()]
                self.assertEqual(len(records), len(hosted.load_prompts()["prompts"]))
                self.assertEqual(records[0]["tokens"][0]["token_id"], 65)
                first = _FakeOpenAI.seen[0]
                self.assertEqual(first["path"], "/v1/completions")
                self.assertIsNone(first["auth"])  # no key configured, none sent
                self.assertTrue(first["body"]["prompt"].endswith("<think>\n\n</think>\n\n"))
                self.assertEqual(first["body"]["prompt_logprobs"], 5)
                report_path = Path(directory) / "report.json"
                with contextlib.redirect_stdout(io.StringIO()):
                    code = hosted.main(["compare", "--provider", "vllm-selfhost", "--traces", str(traces),
                                        "--chat-template", str(e2e.TEMPLATE_PATHS[1]), "--out", str(report_path)],
                                       adapter=e2e.ScriptedAdapter([(r".", "AB")]))
                report = json.loads(report_path.read_text())
                self.assertEqual(report["aggregate"]["top1_agreement"], 1.0)
                self.assertEqual(code, 0)
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main()
