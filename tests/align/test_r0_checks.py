"""R0 decisions and CLI with tiny, explicit fake evidence; never imports MLX."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import fcntl
from types import SimpleNamespace
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from joulewise.align import r0
from joulewise.align.interfaces import ChatResult, ToolCallRequest
from joulewise.align.r0_host import Refused
from joulewise.align.r0_runner import CHECKS, DeadlineExpired, execute, main, validate_config


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
        self.config = SimpleNamespace(model=SimpleNamespace(family="qwen3_next", revision=FAKE_REVISION))
        self.greedy_turns, self.greedy_session = 0, False
    def new_session(self, effort, *, greedy=False):
        self.sessions.append(effort)
        self.greedy_session = greedy
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
    def chat(self, messages, tools, max_tokens, seed, *, greedy=False):
        if greedy != self.greedy_session:
            raise AssertionError("greedy chat outside a greedy session")
        self.greedy_turns += greedy
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
    def nll_losses(self, ids):
        return [2.99] * (len(ids) - 1)
    def long_decode(self, *, eval_metadata):
        return {"positions": 40960, "errors": [], "memory_samples": [
            {"position": 0, "active_bytes": 1_000_000_000},
            {"position": 10000, "active_bytes": 1_100_000_000},
            {"position": 40960, "active_bytes": 1_200_000_000}], "eval_metadata": eval_metadata}
    def memory_peak(self, *, context, decode_budget):
        return {"positions": context, "decode_tokens": decode_budget, "peak_bytes": 1_000_000,
                "swap_before_bytes": 0, "swap_after_bytes": 0, "errors": []}


FAKE_REVISION = "fake-revision"


def fake_references(mean=2.99, mode="reference", **entry):
    """A verdict table that names FakeBackend's revision and fixture."""
    row = {"label": "fake", "revision": FAKE_REVISION, "mode": mode,
           "fixture_sha256": r0.digest(r0.nll_fixture(FakeBackend())),
           "provenance": {"implementation": "synthetic"}}
    if mode == "reference":
        row.update(targets=2048, reference={"nll_nats_per_token": mean, "bins256": [mean] * 8},
                   tolerance={"mean_nats_per_token": 0.1, "bin_nats_per_token": 0.5})
    else:
        row["nll_limit"] = 3.0
    row.update(entry)
    return {"schema": r0.NLL_REFERENCE_SCHEMA, "bin_width": 256, "targets": 2048, "models": [row]}


def patch_references(case, references=None):
    """Runner paths read the shipped table; point them at the fake model's entry."""
    gate = patch.object(r0, "nll_references", return_value=(references or fake_references(), "0" * 64))
    gate.start()
    case.addCleanup(gate.stop)


def config_at(root):
    return {"schema": "joulewise.align.r0.config.v1", "models": {
            "D": {"source": str(root / "D")}}, "shade_cache": str(root / "shade"),
            "disk_path": str(root), "custody_parents": [str(root / "custody")], "offloads": [],
            "measurement_hw_model": "MacSynthetic", "anchor_source": str(root / "anchor")}


class R0ChecksTest(unittest.TestCase):
    def setUp(self):
        gate = patch("joulewise.align.r0_runner.host_identity", return_value={"status": "pass", "fake": True})
        gate.start()
        self.addCleanup(gate.stop)
        patch_references(self)

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

    def test_generated_rewrites_survives_one_off_spec_echo_call(self):
        backend = FakeBackend()
        chat = backend.chat
        calls = {"n": 0}
        def flaky(messages, tools, max_tokens, seed):
            result = chat(messages, tools, max_tokens, seed)
            calls["n"] += 1
            if calls["n"] == 3:
                bad = (ToolCallRequest("echo", "r0_echo", '{"value":"desk-chek"}'),)
                result = replace(result, tool_calls=bad)
            return result
        backend.chat = flaky
        generated = r0.generated_rewrites(backend)
        self.assertEqual(generated["status"], "pass")
        self.assertEqual(len(generated["transitions"]), 12)
        self.assertEqual(generated["off_spec_echo_turns"], 1)
        self.assertTrue(generated["transitions"][2]["off_spec_echo"])

    def test_echo_prompt_states_a_total_that_covers_the_b7_floor(self):
        # A model that makes exactly the number of calls the prompt states, then
        # stops to ask the user (R0 2026-11-06T2235Z stopped after 6 without one).
        import re
        stated = [int(n) for n in re.findall(r"\b(\d+)\b", r0.ECHO_PROMPT)]
        self.assertTrue(stated)
        self.assertTrue(all(n == r0.ECHO_CALLS for n in stated))
        self.assertGreater(r0.ECHO_CALLS, r0.ECHO_TRANSITIONS)
        backend = FakeBackend()
        chat = backend.chat
        def obedient(messages, tools, max_tokens, seed):
            result = chat(messages, tools, max_tokens, seed)
            made = sum(m.role == "tool" for m in messages)
            return result if made < stated[0] else replace(result, tool_calls=())
        backend.chat = obedient
        generated = r0.generated_rewrites(backend)
        self.assertEqual(generated["status"], "pass")
        self.assertEqual(len(generated["transitions"]), r0.ECHO_TRANSITIONS)
        self.assertEqual(r0.checkpoint_verdict("D", generated)["status"], "not_required")

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
        self.assertEqual(result["nll_mode"], "reference")
        self.assertEqual(result["generation"]["status"], "pass")
        self.assertTrue(result["tool_round_trip"]["tool_outputs"])
        patch_references(self, fake_references(mean=11.0))
        # No absolute bar in reference mode: a reference-equivalent 11.04 passes.
        with patch.object(FakeBackend, "nll_losses", return_value=[11.04] * 2048):
            self.assertEqual(r0.load_coherence(FakeBackend())["status"], "pass")
        with patch.object(FakeBackend, "nll_losses", return_value=[11.2] * 2048):
            self.assertEqual(r0.load_coherence(FakeBackend())["status"], "fail")
        with patch.object(FakeBackend, "nll_losses", return_value=[float("nan")] * 2048):
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
                if kwargs.get("greedy"):
                    return result  # the generation check is a bar, not a diagnostic
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

    def test_r0l3_guard_and_smc_contention_are_recorded_flagged_and_not_fatal(self):
        class Contended(FakeGuard):
            # Once armed, every census records a flag (QuietGuard under R0-L3).
            armed = False
            contention_flags = []
            def check(self, *, force=False):
                super().check(force=force)
                if self.armed:
                    self.contention_flags.append({"flag": "contaminating CPU contention: 61967 frauddefensed"})
        guard = Contended()
        guard.contention_flags = []
        def template(backend):
            guard.armed = True
            return {"status": "diagnostic"}
        smc = {"status": "pass", "contended": True, "contention_redo": [{"exit_code": 4}],
               "contention": {"flags": [{"heavy": True}, {"heavy": False}], "episodes": [{}], "contended": True}}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch("joulewise.align.r0_runner.smc_enumeration", return_value=smc), \
                    patch.object(r0, "template_rewrites", side_effect=template):
                report = execute(config_at(root), root, ["smc", "template"], ["D"],
                                 guard=guard, backend_factory=FakeBackend)
            self.assertEqual(report["status"], "pass")
            template_row = next(r for r in report["checks"] if r["check"] == "template")
            self.assertEqual(len(guard.contention_flags), 1)  # the census after the armed unit
            self.assertEqual(template_row["contention_flags"], guard.contention_flags)
            self.assertEqual(report["contention"]["smc_contended"], True)
            self.assertEqual(report["contention"]["smc_redo"], 1)
            self.assertEqual(report["contention"]["smc_flagged_intervals"], 2)
            self.assertEqual(report["contention"]["flagged_checks"],
                             [{"check": "template", "model": "D", "flags": 1}])
            self.assertEqual(json.loads((root / "report.json").read_text())["contention"], report["contention"])
            markdown = (root / "report.md").read_text()
            self.assertIn("## Contention (R0-L3: recorded, not fatal)", markdown)
            self.assertIn("SMC capture contended: **True**", markdown)
            self.assertIn("- template (D): 1 guard flag(s)", markdown)

    def test_r0l3_display_wake_during_smc_is_a_flag_never_a_refusal(self):
        import time as clock
        moments = {}
        def smc(*args, **kwargs):
            moments["smc"] = clock.time()
            return {"status": "pass"}
        probes = []
        def display_probe(started, finished):
            probes.append((started, finished))
            wake = moments["smc"]
            return {"displaysleep_minutes": 0, "display_at_start": "off", "display_woke_during_run": True,
                    "transitions": [{"state": "on", "epoch_s": wake, "line": "Display is turned on"},
                                    {"state": "on", "epoch_s": finished + 3600, "line": "after"}]}
        prep = {"displaysleepnow": {"exit_code": 0}, "dwell_s": 300, "dwell_constant_s": 300}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch("joulewise.align.r0_runner.smc_enumeration", side_effect=smc), \
                    patch.dict("os.environ", {"JOULEWISE_R0_DISPLAY_PREP": json.dumps(prep)}):
                report = execute(config_at(root), root, ["smc"], ["D"], guard=FakeGuard(),
                                 backend_factory=FakeBackend, display_probe=display_probe)
            self.assertEqual(report["status"], "pass")
            self.assertEqual(len(probes), 1)
            display = report["display"]
            self.assertEqual(display["launcher_prep"], prep)
            self.assertEqual(display["displaysleep_minutes"], 0)
            self.assertTrue(display["smc_display_wake_flag"])
            self.assertEqual([w["epoch_s"] for w in display["smc_display_wakes"]], [moments["smc"]])
            markdown = (root / "report.md").read_text()
            self.assertIn("## Display (R0-L3, RUN_STATE 206)", markdown)
            self.assertIn("Display wake during the SMC capture: **True** (a flag, not a refusal)", markdown)

    def test_display_probe_failure_never_changes_the_outcome(self):
        def broken(started, finished):
            raise RuntimeError("pmset exploded")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch("joulewise.align.r0_runner.smc_enumeration", return_value={"status": "pass"}):
                report = execute(config_at(root), root, ["smc"], ["D"], guard=FakeGuard(),
                                 backend_factory=FakeBackend, display_probe=broken)
            self.assertEqual(report["status"], "pass")
            self.assertIn("pmset exploded", report["display"]["error"])
            self.assertIsNone(report["display"]["smc_display_wake_flag"])

    def test_unattended_fake_cli_writes_both_outputs_and_never_claims_live(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "config.json"
            config.write_text(json.dumps(config_at(root)))
            out = root / "output"
            code = main(["--config", str(config), "--output", str(out), "--models", "D", "--checks",
                         "load,template,generated,ladder,long-decode,memory"], backend_factory=FakeBackend, guard_factory=FakeGuard,
                         lock_path=out.parent / "r0.lock")
            result = json.loads((out / "report.json").read_text())
            self.assertEqual(code, 0)
            self.assertFalse(result["complete_r0"])
            self.assertEqual(result["evidence_kind"], "injected_backend")
            self.assertIn("Rewritten prefix tokens", (out / "report.md").read_text())
            self.assertIn("Reasoning tokens", (out / "report.md").read_text())

    def test_mocked_full_r0_completes_at_66_gb_without_offloads(self):
        from joulewise.align.r0_mlx import MlxBackend
        class SyntheticMlxBackend:
            __module__ = MlxBackend.__module__
            def __new__(cls, *args, **kwargs):
                return FakeBackend()
        # Exercise the production completion decision with a mocked constructor.
        # All probes and generation here are synthetic, never native evidence.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = config_at(root)
            for tag in ("D", "anchor"):
                folder = root / tag
                folder.mkdir()
                (folder / "model").write_text("synthetic model")
            with patch("joulewise.align.r0_runner.host_snapshot", return_value={"status": "pass", "fake": True}), \
                        patch("joulewise.align.r0_runner.smc_enumeration", return_value={"status": "pass", "fake": True}), \
                        patch("shutil.disk_usage", return_value=SimpleNamespace(free=66_000_000_000)):
                report = execute(config, root, list(CHECKS), ["D"], guard=FakeGuard(),
                                 backend_factory=SyntheticMlxBackend)
            self.assertEqual(report["status"], "pass")
            self.assertTrue(report["complete_r0"])
            disk = next(row for row in report["checks"] if row["check"] == "disk")
            self.assertEqual(disk["status"], "diagnostic")
            self.assertEqual(disk["free_bytes_after_present_weights"], 66_000_000_000)
            self.assertEqual(disk["offloads"], [])
            self.assertIn("R0 report-only", (root / "report.md").read_text())

    def test_injected_machine_lock_refuses_a_second_runner(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "config.json"
            config.write_text(json.dumps(config_at(root)))
            lock_path = root / "r0.lock"
            out = root / "output"
            with lock_path.open("a") as lock:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                with self.assertRaises(SystemExit) as exc:
                    main(["--config", str(config), "--output", str(out)],
                         backend_factory=FakeBackend, guard_factory=FakeGuard, lock_path=lock_path)
            self.assertEqual(exc.exception.code, 2)
            self.assertFalse(out.exists())

    def test_config_offload_labels_are_configured_and_unique(self):
        config = config_at(Path("/tmp/fake"))
        row = {"label": "pilot10", "inventory": "/tmp/fake/manifest.json", "destination": "/tmp/fake/offload"}
        config["offloads"] = [row]
        validate_config(config)
        for labels in (["pilot10", "pilot10"], [""], [None], [5], [[]]):
            with self.subTest(labels=labels), self.assertRaises(ValueError):
                validate_config({**config, "offloads": [{**row, "label": label} for label in labels]})

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
