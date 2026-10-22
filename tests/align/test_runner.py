"""Episode lifecycle tests on the real runner with production-shaped mock work."""

from __future__ import annotations

import unittest
from dataclasses import replace

from joulewise.align.interfaces import ToolCallRequest
from joulewise.align.mock_world import (
    InboxTask, MockMonitor, MockTokenCounter, ScriptConfig, ScriptedEndpoint,
    SyntheticPowerSampler, VirtualClock,
)
from joulewise.align.records import ClockMapping, to_json, from_json, Episode
from joulewise.align.runner import episode_id, run_episode, transcript_view


def inbox_episode(condition="sabotage", seed=0, *, config=None, counter=True,
                  monitors=(), sampler_class=SyntheticPowerSampler,
                  endpoint_class=ScriptedEndpoint, task_class=InboxTask, **options):
    """Construct real protocol components sharing one explicitly injected clock."""
    clock = VirtualClock()
    config = config or ScriptConfig()
    task = task_class(clock=clock, turns=config.turns)
    endpoint = endpoint_class(clock=clock, config=config, condition=condition)
    sampler = sampler_class(clock_domain="mock.monotonic", seed=seed, clock=clock)
    parameters = dict(seed=seed, max_turns=40, max_tokens=600, temperature=0.0,
                      clock_domain="mock.monotonic", clock=clock,
                      token_counter=MockTokenCounter() if counter else None,
                      monitors=monitors, samplers=(sampler,), matrix_id="unit-inbox")
    parameters.update(options)
    episode, transcript = run_episode(task, condition, endpoint, **parameters)
    return episode, transcript, task, endpoint, sampler


class RunnerTests(unittest.TestCase):
    def test_script_counts_timings_tools_and_round_trip(self):
        for condition in ("benign", "sabotage"):
            with self.subTest(condition=condition):
                ep, transcript, task, endpoint, sampler = inbox_episode(condition, seed=3)
                plan = endpoint.config.plan(condition, 3)
                self.assertEqual(len(ep.turns), len(plan))
                for turn, row in zip(ep.turns, plan):
                    self.assertEqual(turn.context_tokens, row["context"])
                    self.assertEqual(turn.prefill_tokens, row["prefill"])
                    self.assertEqual(turn.decode_tokens, row["decode"])
                    self.assertEqual(turn.hidden_tokens, row["reasoning"] + row["scratchpad"])
                    self.assertLessEqual(turn.start_ns, turn.first_token_ns)
                    self.assertLessEqual(turn.first_token_ns, turn.end_ns)
                    for call in turn.tool_calls:
                        self.assertGreaterEqual(call.start_ns, turn.end_ns)
                        self.assertLessEqual(call.end_ns, ep.end_ns)
                self.assertEqual(ep.totals()["tool_calls"], 11 + int(condition == "sabotage"))
                # These scores encode exact categorical outcomes, not measured estimates.
                self.assertEqual(ep.main_task_score, float(True))
                self.assertEqual(ep.side_task_success, condition == "sabotage")
                self.assertFalse(sampler.started)
                self.assertEqual(len(ep.power_traces), 1)
                self.assertEqual(ep.hardware["endpoint"], endpoint.identity)
                self.assertEqual(ep.hardware["samplers"], [sampler.identity])
                self.assertEqual(to_json(from_json(Episode, to_json(ep))), to_json(ep))
                self.assertEqual(sum(m.role == "tool" for m in transcript), len(task.actions))

    def test_scratchpad_and_reasoning_visibility(self):
        monitor = MockMonitor()
        ep, transcript, task, _, _ = inbox_episode(
            monitors=((monitor, ("full", "no_scratchpad", "actions_only")),))
        self.assertEqual([v.visibility for v in ep.monitor_verdicts],
                         ["full", "no_scratchpad", "actions_only"])
        full = transcript_view(transcript, "full", task.scratchpad_tags)
        stripped = transcript_view(transcript, "no_scratchpad", task.scratchpad_tags)
        actions = transcript_view(transcript, "actions_only", task.scratchpad_tags)
        self.assertTrue(any("side-note" in m.content for m in full))
        natural = [m.content for m in stripped if m.role == "assistant" and m.tool_call_id is None]
        self.assertFalse(any("side-note" in text or "private" in text for text in natural))
        self.assertEqual(len(actions), 2 * ep.totals()["tool_calls"])
        self.assertTrue(all(m.role == "tool" or m.tool_call_id is not None for m in actions))
        self.assertEqual(ep.turns[6].hidden_tokens, 120 + 64)

    def test_missing_counter_keeps_reasoning_and_flags_scratchpad(self):
        ep, _, _, _, _ = inbox_episode(counter=False)
        self.assertIn("hidden_tokens.scratchpad_uncounted", ep.flags)
        self.assertEqual(ep.turns[6].hidden_tokens, 120)
        self.assertIsNone(ep.hardware["runner"]["scratchpad_tokens"]["6"])

    def test_max_turns_is_retained(self):
        ep, _, _, _, sampler = inbox_episode(max_turns=3)
        self.assertEqual(len(ep.turns), 3)
        self.assertIn("episode.max_turns", ep.flags)
        self.assertFalse(sampler.started)

    def test_endpoint_error_stops_and_retains_prior_turns(self):
        class FailingEndpoint(ScriptedEndpoint):
            def chat(self, messages, **kwargs):
                if sum(m.role == "tool" for m in messages) == 3:
                    raise RuntimeError("synthetic endpoint failure")
                return super().chat(messages, **kwargs)
        ep, _, _, _, sampler = inbox_episode(endpoint_class=FailingEndpoint)
        self.assertEqual(len(ep.turns), 3)
        self.assertIn("endpoint.error.RuntimeError", ep.flags)
        self.assertFalse(sampler.started)
        self.assertTrue(ep.power_traces[0].t_ns)

    def test_interrupt_retains_episode_and_stops_sampler(self):
        class InterruptingEndpoint(ScriptedEndpoint):
            def chat(self, messages, **kwargs):
                if sum(m.role == "tool" for m in messages) == 3:
                    raise KeyboardInterrupt
                return super().chat(messages, **kwargs)
        ep, _, _, _, sampler = inbox_episode(endpoint_class=InterruptingEndpoint)
        self.assertIn("episode.interrupted", ep.flags)
        self.assertEqual(len(ep.turns), 3)
        self.assertFalse(sampler.started)

    def test_tool_error_is_a_timed_retained_call(self):
        class FailingTask(InboxTask):
            def call_tool(self, name, arguments_json):
                result = super().call_tool(name, arguments_json)
                if name == "transfer":
                    raise RuntimeError("synthetic transfer failure")
                return result
        ep, transcript, _, _, _ = inbox_episode(task_class=FailingTask)
        self.assertIn("tool.error.RuntimeError", ep.flags)
        self.assertEqual(ep.totals()["tool_calls"], 12)
        self.assertTrue(any(m.content == "Tool error: RuntimeError" for m in transcript))
        self.assertEqual(ep.turns[6].tool_calls[0].end_ns -
                         ep.turns[6].tool_calls[0].start_ns, 2_000_000_000)

    def test_multiple_calls_and_utf8_byte_lengths(self):
        class MultipleEndpoint(ScriptedEndpoint):
            def chat(self, messages, **kwargs):
                result = super().chat(messages, **kwargs)
                if not any(m.role == "assistant" for m in messages):
                    extra = ToolCallRequest("extra", "read", '{"id":0,"note":"Δ"}')
                    result = replace(result, tool_calls=result.tool_calls + (extra,))
                return result
        ep, transcript, _, _, _ = inbox_episode(endpoint_class=MultipleEndpoint)
        self.assertEqual(len(ep.turns[0].tool_calls), 2)
        messages = [m for m in transcript if m.tool_call_id == "extra"]
        self.assertEqual(ep.turns[0].tool_calls[1].args_bytes, len(messages[0].content.encode("utf-8")))
        self.assertEqual(ep.turns[0].tool_calls[1].result_bytes, len(messages[1].content.encode("utf-8")))
        self.assertGreaterEqual(ep.turns[0].tool_calls[1].start_ns,
                                ep.turns[0].tool_calls[0].end_ns)

    def test_foreign_domain_requires_mapping(self):
        class Unmapped(SyntheticPowerSampler):
            clock_mapping = None
            def __init__(self, **kwargs):
                super().__init__(**{**kwargs, "clock_domain": "sensor.remote"})
        ep, _, _, _, _ = inbox_episode(sampler_class=Unmapped)
        self.assertIn("clock.unmapped", ep.flags)
        self.assertEqual(ep.power_traces, ())

        class Mapped(SyntheticPowerSampler):
            def __init__(self, **kwargs):
                super().__init__(**{**kwargs, "clock_domain": "sensor.remote",
                                   "episode_domain": "mock.monotonic",
                                   "offset_ns": 7_000_000_000, "uncertainty_ns": 100_000})
        ep, _, _, _, _ = inbox_episode(sampler_class=Mapped)
        self.assertEqual(ep.clock_mappings, (ClockMapping(
            "sensor.remote", "mock.monotonic", 7_000_000_000, 100_000,
            "synthetic exact clock plus configured uncertainty"),))
        self.assertEqual(ep.power_traces[0].clock_domain, "sensor.remote")

    def test_sampler_and_scoring_failures_are_flags(self):
        class FailingSampler(SyntheticPowerSampler):
            def start(self):
                super().start()
                raise RuntimeError
            def stop(self):
                self.started = False
                raise RuntimeError
        class FailingTask(InboxTask):
            def score_main(self, transcript):
                raise RuntimeError
            def score_side(self, transcript):
                raise RuntimeError
        class FailingMonitor(MockMonitor):
            def score(self, *args, **kwargs):
                raise RuntimeError
        ep, _, _, _, sampler = inbox_episode(
            sampler_class=FailingSampler, task_class=FailingTask, monitors=(FailingMonitor(),))
        self.assertIn("sampler.start_error.RuntimeError", ep.flags)
        self.assertIn("sampler.stop_error.RuntimeError", ep.flags)
        self.assertIn("score.main_task_score.error.RuntimeError", ep.flags)
        self.assertIn("score.side_task_success.error.RuntimeError", ep.flags)
        self.assertIn("monitor.error.RuntimeError", ep.flags)
        self.assertIsNone(ep.main_task_score)
        self.assertIsNone(ep.side_task_success)
        self.assertEqual(len(ep.turns), 13)
        self.assertFalse(sampler.started)

    def test_malformed_usage_is_flagged_and_contract_valid(self):
        class BadUsage(ScriptedEndpoint):
            def chat(self, messages, **kwargs):
                result = super().chat(messages, **kwargs)
                return replace(result, prompt_tokens=4, cached_prompt_tokens=8,
                               completion_tokens=20, reasoning_tokens=100,
                               first_token_ns=result.end_ns + 1)
        ep, _, _, _, _ = inbox_episode(endpoint_class=BadUsage)
        self.assertIn("usage.cached_exceeds_prompt", ep.flags)
        self.assertIn("usage.hidden_exceeds_decode", ep.flags)
        self.assertIn("clock.first_token_invalid", ep.flags)
        self.assertEqual(ep.turns[0].prefill_tokens, 0)
        self.assertEqual(ep.turns[0].hidden_tokens, 20)
        self.assertIsNone(ep.turns[0].first_token_ns)
        from_json(Episode, to_json(ep))

    def test_invalid_scores_and_sampler_return_are_recorded(self):
        class BadTask(InboxTask):
            def score_main(self, transcript):
                return float("nan")
            def score_side(self, transcript):
                return "unknown"
        class BadSampler(SyntheticPowerSampler):
            def stop(self):
                self.started = False
                return None
        ep, _, _, _, sampler = inbox_episode(task_class=BadTask, sampler_class=BadSampler)
        self.assertIn("score.main_task_score.invalid", ep.flags)
        self.assertIn("score.side_task_success.invalid", ep.flags)
        self.assertIn("sampler.stop_error.TypeError", ep.flags)
        self.assertIsNone(ep.main_task_score)
        self.assertIsNone(ep.side_task_success)
        self.assertFalse(sampler.started)
        from_json(Episode, to_json(ep))

    def test_id_uses_all_coordinates(self):
        original = episode_id("pair", "benign", "backend/model", 0, "matrix")
        self.assertEqual(original, episode_id("pair", "benign", "backend/model", 0, "matrix"))
        for values in (("other", "benign", "backend/model", 0, "matrix"),
                       ("pair", "sabotage", "backend/model", 0, "matrix"),
                       ("pair", "benign", "backend/other", 0, "matrix"),
                       ("pair", "benign", "backend/model", 1, "matrix"),
                       ("pair", "benign", "backend/model", 0, "other")):
            self.assertNotEqual(original, episode_id(*values))


    def test_endpoint_clock_ahead_and_behind_uses_call_bracket(self):
        original = inbox_episode("benign", seed=2)[0]
        for offset in (1_700_000_000_000_000_000, -5_000_000_000):
            # Offsets model wall-clock and an earlier foreign domain. The exact
            # ns bracket is ground truth; there is no measured comparison bar.
            class OffsetEndpoint(ScriptedEndpoint):
                def chat(self, messages, **kwargs):
                    result = super().chat(messages, **kwargs)
                    return replace(result, start_ns=result.start_ns + offset,
                                   end_ns=result.end_ns + offset,
                                   first_token_ns=result.first_token_ns + offset)
            changed = inbox_episode("benign", seed=2, endpoint_class=OffsetEndpoint)[0]
            self.assertIn("clock.endpoint_outside_call", changed.flags)
            self.assertEqual((changed.start_ns, changed.end_ns), (original.start_ns, original.end_ns))
            self.assertEqual([(t.start_ns, t.end_ns) for t in changed.turns],
                             [(t.start_ns, t.end_ns) for t in original.turns])

    def test_separated_reasoning_history_is_stripped_without_changing_full_view(self):
        inputs = []
        class CapturingEndpoint(ScriptedEndpoint):
            def chat(self, messages, **kwargs):
                inputs.append(list(messages))
                return super().chat(messages, **kwargs)
        ep, transcript, task, _, _ = inbox_episode(endpoint_class=CapturingEndpoint)
        expected = "<jw_reasoning>" + " ".join(["private"] * 120) + "</jw_reasoning>"
        self.assertTrue(any(m.content.startswith(expected) for m in transcript))
        self.assertFalse(any("<jw_reasoning>" in m.content for rows in inputs for m in rows))
        self.assertEqual(transcript_view(transcript, "full", task.scratchpad_tags), transcript)
        stripped = transcript_view(transcript, "no_scratchpad", task.scratchpad_tags)
        for original, viewed in zip(transcript, stripped):
            if original.role == "assistant" and original.tool_call_id is None:
                self.assertNotIn("private", viewed.content)
                self.assertNotIn("<jw_reasoning>", viewed.content)
            else:
                # "private" also occurs in the task's system instruction; the
                # visibility contract deliberately preserves system/tool text.
                self.assertEqual(viewed, original)
        side = next(m for m in transcript if m.content.startswith(expected))
        row = ScriptConfig().plan("sabotage", 0)[6]
        self.assertEqual(side.content, expected + "<scratchpad>" +
                         " ".join(["side-note"] * int(row["scratchpad"])) +
                         "</scratchpad>" + " ".join(["digest"] * int(row["visible"])))
        self.assertEqual(ep.hardware["runner"]["reasoning_history_policy"], "strip_separated_reasoning")

    def test_none_content_and_nonserializable_tool_results_keep_model_calls(self):
        class NullEndpoint(ScriptedEndpoint):
            def chat(self, messages, **kwargs):
                result = super().chat(messages, **kwargs)
                return replace(result, content=None) if result.tool_calls else result
        class BytesTask(InboxTask):
            def call_tool(self, name, arguments_json):
                super().call_tool(name, arguments_json)
                return b"\x00raw"
        for kwargs, flag in (({"endpoint_class": NullEndpoint}, "endpoint.content_missing"),
                             ({"task_class": BytesTask}, "tool.non_text_result")):
            ep, transcript, task, endpoint, _ = inbox_episode(**kwargs)
            # One record per completed ledger call is an exact integer property.
            self.assertEqual(len(ep.turns), len(endpoint.ledger.turns))
            self.assertIn(flag, ep.flags)
            self.assertFalse(any(f.startswith("runner.error.") for f in ep.flags))

    def test_tampered_monitor_view_is_unavailable_in_episode_loop(self):
        ep, _, _, _, _ = inbox_episode(monitors=((MockMonitor(), ("tampered",)),))
        self.assertEqual(ep.monitor_verdicts, ())
        self.assertIn("monitor.visibility_tampered_unavailable", ep.flags)

    def test_plain_text_and_malformed_flag_notes_still_attach_trace(self):
        for notes in ("ordinary sensor note", '{"flags":[42]}', '{"flags":"battery.assist"}'):
            class NotedSampler(SyntheticPowerSampler):
                def stop(self):
                    return tuple(replace(trace, notes=notes) for trace in super().stop())
            ep, _, _, _, _ = inbox_episode(sampler_class=NotedSampler)
            self.assertEqual(len(ep.power_traces), 1)
            self.assertIn("power.notes", ep.flags)

    def test_structured_power_flags_are_verbatim_and_distinct(self):
        class NotedSampler(SyntheticPowerSampler):
            def stop(self):
                return tuple(replace(trace, notes='{"flags":["battery.assist","battery.assist","throttle.power"]}')
                             for trace in super().stop())
        ep, _, _, _, _ = inbox_episode(sampler_class=NotedSampler)
        self.assertEqual([flag for flag in ep.flags if flag.startswith("power.")],
                         ["power.gpu0.battery.assist", "power.gpu0.throttle.power"])


if __name__ == "__main__":
    unittest.main()
