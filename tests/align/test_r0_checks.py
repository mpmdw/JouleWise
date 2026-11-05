"""R0 decisions and CLI with tiny, explicit fake evidence; never imports MLX."""
from __future__ import annotations

from copy import deepcopy
from types import SimpleNamespace
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from joulewise.align import r0
from joulewise.align.interfaces import ChatResult, ToolCallRequest
from joulewise.align.r0_host import Refused
from joulewise.align.r0_runner import DeadlineExpired, execute, main, validate_config


class FakeGuard:
    def __init__(self, parents=()):
        self.receipts = []
    def check(self, *, force=False):
        self.receipts.append({"fake": True})


class FakeTask:
    def system_prompt(self, condition):
        return "shade " * 2100
    def user_prompt(self):
        return "Update the filter."
    def tool_schemas(self):
        return r0.ECHO_TOOLS
    def call_tool(self, name, arguments):
        return r0.EchoTask().call_tool(name, arguments)


class FakeBackend:
    def __init__(self, *args):
        self.sessions = []
        self.generation = None
        self.closed = False
        self.endpoint = SimpleNamespace(assistant_history_message=lambda result: r0.ChatMessage("assistant", result.raw_usage["raw_text"]))
        self.config = SimpleNamespace(model=SimpleNamespace(family="qwen3_next"))
    def new_session(self, effort):
        self.sessions.append(effort)
    def device_info(self):
        return {"status": "pass", "fake": True}
    def close(self):
        self.closed = True
    def encode(self, text):
        return list(text.encode())
    def render(self, messages, tools):
        text = "ROOT"
        for message in messages:
            if message.role == "assistant":
                text += "GEN" + message.content + "!"
            else:
                text += message.role + message.content
        return self.encode(text + "GEN")
    def synthetic_completion(self, index):
        raw = '<think>echo</think><tool_call>{"name":"r0_echo","arguments":{"value":"desk-check"}}</tool_call>'
        return raw, self.encode(raw + "!")
    def chat(self, messages, tools, max_tokens, seed):
        short = messages[-1].content == r0.SHORT_PROMPT
        raw = "42" if short else self.synthetic_completion(0)[0]
        calls = () if short else (ToolCallRequest("echo", "r0_echo", '{"value":"desk-check"}'),)
        output = self.encode(raw + "!")
        self.generation = {"prompt_token_ids": self.render(messages, tools), "output_token_ids": output}
        return ChatResult("42" if short else raw, "echo", calls, len(self.generation["prompt_token_ids"]),
                          0, len(output), 4, 0, 1, 1_000_000_000,
                          {"raw_text": raw, "joulewise": {"flags": []}})
    def last_generation(self):
        return self.generation
    def task(self, pair, seed):
        return FakeTask()
    def nll(self, ids):
        return 2.99
    def long_decode(self, *, eval_metadata):
        return {"positions": 40960, "errors": [], "memory_samples": [
            {"position": 0, "active_bytes": 1_000_000_000},
            {"position": 10000, "active_bytes": 1_100_000_000},
            {"position": 40960, "active_bytes": 1_200_000_000}], "eval_metadata": eval_metadata}
    def memory_peak(self, *, context, decode_budget):
        return {"positions": context, "decode_tokens": decode_budget, "peak_bytes": 1_000_000,
                "swap_before_bytes": 0, "swap_after_bytes": 0, "errors": []}


def config_at(root):
    return {"schema": "joulewise.align.r0.config.v1", "models": {
            "D": {"source": str(root / "D")}}, "shade_cache": str(root / "shade"),
            "disk_path": str(root), "custody_parents": [str(root / "custody")], "offloads": [],
            "measurement_hw_model": "MacSynthetic"}


class R0ChecksTest(unittest.TestCase):
    def setUp(self):
        gate = patch("joulewise.align.r0_runner.host_identity", return_value={"status": "pass", "fake": True})
        gate.start()
        self.addCleanup(gate.stop)

    def test_wrong_host_blocks_all_model_loads_even_if_host_check_not_selected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch("joulewise.align.r0_runner.host_identity", return_value={"status": "fail"}), \
                    patch.object(FakeBackend, "__init__") as load:
                report = execute(config_at(root), root, ["load"], ["D"], guard=FakeGuard(), backend_factory=FakeBackend)
            load.assert_not_called()
            self.assertEqual(report["status"], "fail")
    def test_rewrite_counts_consumed_output_not_just_prior_prompt(self):
        self.assertEqual(r0.rewrite([1, 2], [3, 4], [1, 2, 9])["rewritten_prefix_tokens"], 2)
        self.assertEqual(r0.rewrite([1], [2, 3], [1, 2, 3, 4])["rewritten_prefix_tokens"], 0)
        self.assertEqual(r0.rewrite([1, 2], [3], [1])["rewritten_prefix_tokens"], 2)

    def test_synthetic_and_generated_evidence_are_distinct(self):
        backend = FakeBackend()
        synthetic = r0.template_rewrites(backend)
        generated = r0.generated_rewrites(backend)
        self.assertEqual(len(synthetic["transitions"]), 12)
        self.assertEqual(synthetic["status"], "diagnostic")
        self.assertEqual(generated["status"], "pass")
        self.assertNotEqual(synthetic["evidence"], generated["evidence"])

    def test_checkpoint_sample_floor_closed_reasoning_and_threshold(self):
        rows = [{"closed_reasoning": True, "rewritten_prefix_tokens": 0} for _ in range(12)]
        self.assertEqual(r0.checkpoint_verdict("D", {"transitions": rows[:11]})["status"], "inconclusive")
        rows[0]["rewritten_prefix_tokens"] = 1
        self.assertEqual(r0.checkpoint_verdict("D", {"transitions": rows})["status"], "required")
        self.assertEqual(r0.checkpoint_verdict("N", {"transitions": rows})["status"], "not_required")
        rows[1]["rewritten_prefix_tokens"] = 1
        self.assertEqual(r0.checkpoint_verdict("N", {"transitions": rows})["status"], "required")
        rows[0]["closed_reasoning"] = False
        self.assertEqual(r0.checkpoint_verdict("D", {"transitions": rows})["status"], "inconclusive")

    def test_load_nll_and_roundtrip(self):
        result = r0.load_coherence(FakeBackend())
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["nll_targets"], 2048)
        self.assertTrue(result["tool_round_trip"]["tool_outputs"])
        with patch.object(FakeBackend, "nll", return_value=3.0001):
            self.assertEqual(r0.load_coherence(FakeBackend())["status"], "fail")
        with patch.object(FakeBackend, "nll", return_value=float("nan")):
            self.assertEqual(r0.load_coherence(FakeBackend())["status"], "fail")

    def test_missing_generation_evidence_never_passes(self):
        backend = FakeBackend()
        with patch.object(backend, "last_generation", return_value={"prompt_token_ids": [1], "output_token_ids": []}):
            with self.assertRaises(ValueError):
                r0.load_coherence(backend)

    def test_effort_order_default_omission_and_stop_first_passing(self):
        backend = FakeBackend()
        def episode(*args, **kwargs):
            effort = backend.sessions[-1]
            return {"pair": args[2], "turns": [{"hit_cap": effort is None, "closed_reasoning": effort is not None,
                                                 "reasoning_tokens": 1000}]}
        with patch.object(r0, "screen_episode", side_effect=episode):
            result = r0.ladder(backend, "D")
        self.assertEqual(backend.sessions, [None, None, "medium", "medium"])
        self.assertEqual(result["selected"], "medium")
        self.assertEqual(result["rungs"][0]["template_kwargs"], {})

    def test_n_cap_ladder_and_no_rung_fallback(self):
        backend = FakeBackend()
        ep = {"turns": [{"hit_cap": True, "closed_reasoning": True, "reasoning_tokens": 500}]}
        with patch.object(r0, "screen_episode", return_value=ep):
            result = r0.ladder(backend, "N")
        self.assertEqual([r["cap"] for r in result["rungs"]], [4096, 8192])
        self.assertIn("no reasoning-omission estimand", result["consequence"])
        ep["turns"][0]["closed_reasoning"] = False
        with patch.object(r0, "screen_episode", return_value=ep):
            result = r0.ladder(backend, "D")
        self.assertEqual([r["rung"] for r in result["rungs"]], ["xhigh", "medium", "low"])
        self.assertEqual(result["consequence"], "D screen-only")

    def test_d_ladder_20_percent_and_median_bars(self):
        turns = [{"hit_cap": i == 0, "closed_reasoning": i != 0, "reasoning_tokens": 2048} for i in range(5)]
        with patch.object(r0, "screen_episode", return_value={"turns": turns}):
            self.assertEqual(r0.ladder(FakeBackend(), "D")["selected"], "xhigh")
        turns[1]["reasoning_tokens"] = turns[2]["reasoning_tokens"] = turns[3]["reasoning_tokens"] = 2049
        with patch.object(r0, "screen_episode", return_value={"turns": turns}):
            self.assertEqual(r0.ladder(FakeBackend(), "D")["status"], "fallback")

    def test_decisions_are_successful_checks_and_template_is_diagnostic(self):
        backend = FakeBackend()
        with patch.object(backend, "render", return_value=[999]):
            result = r0.template_rewrites(backend)
        self.assertFalse(result["prefix_stable"])
        self.assertEqual(result["status"], "diagnostic")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch.object(r0, "checkpoint_verdict", return_value={"status": "required"}), \
                    patch.object(r0, "ladder", return_value={"status": "fallback", "selected": None, "rungs": []}):
                report = execute(config_at(root), root, ["generated", "ladder", "template"], ["D"],
                                 guard=FakeGuard(), backend_factory=FakeBackend)
            self.assertEqual(report["status"], "pass")
            self.assertIn("required", [r["status"] for r in report["checks"]])

    def test_coherence_format_and_echo_are_diagnostics_but_nll_is_a_bar(self):
        from dataclasses import replace
        class Backend(FakeBackend):
            def chat(self, *args, **kwargs):
                result = super().chat(*args, **kwargs)
                return replace(result, content="\\boxed{42}") if result.content == "42" else replace(result, tool_calls=())
        result = r0.load_coherence(Backend())
        self.assertEqual(result["status"], "pass")
        self.assertFalse(result["coherent"])
        self.assertFalse(result["tool_round_trip"]["succeeded"])
        self.assertNotIn("exactly once", r0.ECHO_PROMPT)

    def test_episode_enforces_decode_ceiling_and_seed_law(self):
        result = r0.screen_episode(FakeBackend(), "D", r0.PAIRS[0], 91, 4096, budget=4300)
        self.assertLessEqual(result["decode_tokens"], 4300)
        self.assertTrue(result["turns"])
        self.assertLess(len(result["turns"]), 6)
        self.assertTrue(all(t["requested_tokens"] == 4096 for t in result["turns"]))
        self.assertEqual(result["seed"], r0.episode_seed(r0.PINS["D"]["tag"], "thinking_on", "shade/" + r0.PAIRS[0], 91))

    def test_shade_tool_error_is_returned_to_model_but_echo_check_is_strict(self):
        task = FakeTask()
        task.call_tool = Mock(side_effect=ValueError("bad argument"))
        backend = FakeBackend()
        result = backend.chat([r0.ChatMessage("user", "echo")], r0.ECHO_TOOLS, 4096, 91)
        messages = []
        replies = r0.append_result(backend, messages, result, task)
        self.assertIn("bad argument", json.loads(replies[0])["error"])
        self.assertEqual(messages[-1].role, "tool")
        with self.assertRaises(ValueError):
            r0.append_result(backend, [], result, task, strict=True)

    def test_envelope_denominator_and_unsupported_flags(self):
        row = {"raw_text": "unused", "visible_text": "<tool_call>a</tool_call><tool_call>broken", "tool_calls": 1, "flags": []}
        self.assertEqual(r0.tool_envelopes([row])["parse_fraction"], 0.5)
        self.assertEqual(r0.tool_envelopes([row])["status"], "fail")
        row.update(visible_text="<tool_call>a</tool_call>", flags=["unsupported_tool_call_format"])
        self.assertEqual(r0.tool_envelopes([row])["status"], "fail")
        self.assertEqual(r0.tool_envelopes([])["status"], "fail")

    def test_envelope_census_excludes_reasoning_quotes_and_reports_capped_tail(self):
        row = {"raw_text": "thought <tool_call>quoted</think><tool_call>real</tool_call><tool_call>cut",
               "visible_text": "<tool_call>real</tool_call><tool_call>cut",
               "tool_calls": 1, "flags": ["turn_token_budget_reached:0"], "hit_cap": True}
        result = r0.tool_envelopes([row])
        self.assertEqual(result["attempted_envelopes"], 1)
        self.assertEqual(result["truncated_envelopes"], 1)
        self.assertEqual(result["status"], "pass")

    def test_ladder_evidence_retains_tool_errors(self):
        task = FakeTask()
        task.call_tool = Mock(side_effect=ValueError("saved tool failure"))
        backend = FakeBackend()
        with patch.object(backend, "task", return_value=task):
            result = r0.screen_episode(backend, "D", r0.PAIRS[0], 91, 4096, max_turns=1)
        self.assertIn("saved tool failure", result["turns"][0]["tool_outputs"][0])

    def test_long_decode_retests_metadata_eval_and_checks_growth(self):
        backend = FakeBackend()
        good = backend.long_decode(eval_metadata=True)
        good["metadata_arrays_evaluated"] = 2
        bad = deepcopy(good)
        bad["memory_samples"][1]["active_bytes"] += 2_000_000_000
        bad["errors"] = ["Resource limit"]
        with patch.object(backend, "long_decode", side_effect=[bad, good]) as call:
            result = r0.long_decode(backend)
        self.assertEqual(call.call_args_list[0].kwargs, {"eval_metadata": False})
        self.assertEqual(call.call_args_list[1].kwargs, {"eval_metadata": True})
        self.assertTrue(result["metadata_eval_required"])
        bad["errors"] = ["Resource limit"]
        self.assertEqual(r0.long_decode_verdict(bad)["status"], "fail")

    def test_memory_transient_is_not_sustained_growth_and_kv_is_reported(self):
        samples = [{"position": p, "active_bytes": 1_000_000_000 + p * 66000,
                    "kv_cache_bytes": p * 66000} for p in range(2049, 40961, 256)]
        samples[-2]["active_bytes"] += 8_000_000_000
        result = r0.long_decode_verdict({"positions": 40960, "errors": [], "memory_samples": samples})
        self.assertEqual(result["status"], "pass")
        self.assertAlmostEqual(result["trend_bytes_per_10k"], 660_000_000)
        self.assertAlmostEqual(result["kv_bytes_per_10k"], 660_000_000)
        for sample in samples:
            sample["active_bytes"] = 1_000_000_000 + sample["position"] * 210000
        self.assertEqual(r0.long_decode_verdict({"positions": 40960, "memory_samples": samples})["status"], "fail")

    def test_empty_metadata_retest_cannot_claim_a_mitigation(self):
        backend = FakeBackend()
        good = backend.long_decode(eval_metadata=True)
        good.update(metadata_arrays_evaluated=0, metadata_evaluation="metadata_absent_single_stream")
        bad = {**good, "errors": ["Resource limit"]}
        with patch.object(backend, "long_decode", side_effect=[bad, good]):
            result = r0.long_decode(backend)
        self.assertFalse(result["metadata_eval_required"])
        self.assertEqual(result["status"], "inconclusive")

    def test_memory_swap_peak_and_token_positions(self):
        backend = FakeBackend()
        self.assertEqual(r0.memory_peak(backend, "D")["status"], "pass")
        bad = backend.memory_peak(context=40960, decode_budget=6144)
        bad["swap_after_bytes"] = 1
        with patch.object(backend, "memory_peak", return_value=bad):
            self.assertEqual(r0.memory_peak(backend, "D")["status"], "fail")
        bad.update(swap_after_bytes=0, positions=40959, errors=[])
        with patch.object(backend, "memory_peak", return_value=bad):
            self.assertEqual(r0.memory_peak(backend, "D")["status"], "fail")
        bad.update(positions=40960, errors=["Resource limit"])
        with patch.object(backend, "memory_peak", return_value=bad):
            self.assertEqual(r0.memory_peak(backend, "D")["status"], "fail")

    def test_deadline_bypasses_native_exception_handlers_and_is_recorded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch.object(FakeBackend, "long_decode", side_effect=DeadlineExpired("bounded")):
                result = execute(config_at(root), root, ["long-decode"], ["D"],
                                 guard=FakeGuard(), backend_factory=FakeBackend)
            self.assertEqual(result["status"], "fail")
            self.assertIn("DeadlineExpired", result["checks"][-1]["error"])
    def test_runner_reports_refusal_before_model_or_host(self):
        class Occupied(FakeGuard):
            def check(self, **kwargs):
                raise Refused("agent alive")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch("joulewise.align.r0_runner.host_snapshot") as host, patch.object(FakeBackend, "__init__") as load:
                result = execute(config_at(root), root, ["host", "load"], ["D"], guard=Occupied(), backend_factory=FakeBackend)
            host.assert_not_called()
            load.assert_not_called()
            self.assertEqual(result["status"], "refused")
            self.assertEqual(json.loads((root / "report.json").read_text())["status"], "refused")

    def test_unattended_fake_cli_writes_both_outputs_and_never_claims_live(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "config.json"
            config.write_text(json.dumps(config_at(root)))
            out = root / "output"
            code = main(["--config", str(config), "--output", str(out), "--models", "D", "--checks",
                         "load,template,generated,ladder,long-decode,memory"], backend_factory=FakeBackend, guard_factory=FakeGuard)
            result = json.loads((out / "report.json").read_text())
            self.assertEqual(code, 0)
            self.assertFalse(result["complete_r0"])
            self.assertEqual(result["evidence_kind"], "injected_backend")
            self.assertIn("Rewritten prefix tokens", (out / "report.md").read_text())
            self.assertIn("Reasoning tokens", (out / "report.md").read_text())

    def test_config_pins_cannot_be_overridden(self):
        config = config_at(Path("/tmp/fake"))
        validate_config(config)
        config["models"]["D"]["revision"] = "new-pin"
        with self.assertRaises(ValueError):
            validate_config(config)

    def test_amendment_one_selects_d_only_and_refuses_dropped_next(self):
        config = config_at(Path("/tmp/synthetic-r0-config"))
        self.assertEqual(validate_config(config)["models"].keys(), {"D"})
        self.assertEqual(set(r0.PINS), {"D"})
        config["models"]["N"] = {"source": "/tmp/synthetic-dropped-next"}
        with self.assertRaises(ValueError):
            validate_config(config)
        config = config_at(Path("/tmp/fake"))
        config["shade_cache"] = "/tmp/restricted/cache"
        with self.assertRaises(ValueError):
            validate_config(config)


if __name__ == "__main__":
    unittest.main()
