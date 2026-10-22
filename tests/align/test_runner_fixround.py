"""Integration fix regressions through real runner, SHADE and loopback HTTP."""

from __future__ import annotations

import json
import io
import math
import tempfile
import time
import unittest
import urllib.error
import urllib.parse
from collections import deque
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from joulewise.align import runner
from joulewise.align.endpoints import MockEndpoint, OpenAICompatEndpoint
from joulewise.align.interfaces import ChatMessage, PowerSampler
from joulewise.align.mock_world import (
    InboxTask, MockTokenCounter, ScriptConfig, ScriptedEndpoint, VirtualClock,
)
from joulewise.align.records import (
    ClockMapping, Episode, PowerTrace, from_json, read_episodes, to_json, to_jsonable,
)
from joulewise.align.shade import PinnedUpstream, ShadeMonitor, ShadeTask
from joulewise.align.shade.monitor import render_transcript
from tests.align.test_endpoints import HTTPWorld, stream_packets
from tests.align.test_runner_matrix import write_spec
from tests.align.test_shade import fixture_source


class AppleShapedSampler:
    clock_domain = "sensor.remote"

    def __init__(self, mappings=()):
        self.clock_mappings = mappings
        self.traces = tuple(PowerTrace("mock", channel, self.clock_domain,
            (0, 10), (1.0, 2.0), "W", 10) for channel in ("cpu", "gpu", "package"))
        self.stopped = False

    def start(self):
        self.stopped = False

    def stop(self):
        self.stopped = True
        return self.traces


def mapping(**changes):
    return replace(ClockMapping("sensor.remote", "mock.monotonic", 0, 0, "fixture"), **changes)


def episode(*, samplers=(), monitors=(), endpoint=None, task=None, counter=None):
    clock = VirtualClock()
    task = task or InboxTask(clock=clock, turns=1)
    endpoint = endpoint or ScriptedEndpoint(clock=clock, config=ScriptConfig(turns=1))
    return runner.run_episode(task, "benign", endpoint, seed=0, max_turns=1,
        max_tokens=600, temperature=0.0, clock_domain="mock.monotonic", clock=clock,
        samplers=samplers, monitors=monitors, token_counter=counter)


class TransportReplayWorld:
    """Replay HTTP bytes through the real endpoint parser without a socket.

    Supplemental evidence only: the loopback tests below remain mandatory.
    """

    url = "http://127.0.0.1:8000/v1"

    def __init__(self, packets):
        self.packets = deque(packets)
        self.requests = []

    def __enter__(self):
        def open_response(endpoint, url, body, flags, retries):
            self.requests.append({"path": urllib.parse.urlsplit(url).path, "body": body})
            packet = self.packets.popleft()
            if "respond" in packet:
                packet = packet["respond"](body)
            if packet.get("status", 200) >= 400:
                raise urllib.error.HTTPError(url, packet["status"], "fixture", {}, io.BytesIO())
            if "json" in packet:
                return io.BytesIO(json.dumps(packet["json"]).encode())
            return io.BytesIO(("".join("data: " + json.dumps(chunk) + "\n\n"
                for chunk in packet["chunks"]) + "data: [DONE]\n\n").encode())
        self.patch = patch.object(OpenAICompatEndpoint, "_open", open_response)
        self.patch.start()
        return self

    def __exit__(self, *args):
        self.patch.stop()


class RunnerFixroundTests(unittest.TestCase):
    world = HTTPWorld

    def test_apple_plural_mapping_attaches_all_three_traces(self):
        sampler = AppleShapedSampler((mapping(),))
        self.assertIsInstance(sampler, PowerSampler)
        record, _ = episode(samplers=(sampler,))
        self.assertEqual(record.power_traces, sampler.traces)
        self.assertEqual(record.clock_mappings, sampler.clock_mappings)
        self.assertNotIn("clock.unmapped", record.flags)
        self.assertNotIn("sampler.clock_mappings_missing", record.flags)

    def test_unattached_traces_keep_samples_reason_and_offers(self):
        for offers, reason in (
            ((), "clock.unmapped"),
            ((mapping(episode_domain="wrong"),), "clock.unmapped"),
            ((mapping(uncertainty_ns=-1),), "clock.unmapped"),
            ((mapping(uncertainty_ns="invalid"),), "clock.unmapped"),
            ((mapping(offset_ns=float("inf")),), "clock.unmapped"),
            ((mapping(), mapping(offset_ns=1)), "clock.mapping_conflict"),
        ):
            with self.subTest(offers=offers):
                sampler = AppleShapedSampler(offers)
                record, _ = episode(samplers=(sampler,))
                self.assertEqual(record.power_traces, ())
                self.assertIn(reason, record.flags)
                retained = record.hardware["runner"]["unattached_traces"]
                self.assertEqual([item["trace"] for item in retained], to_jsonable(sampler.traces))
                self.assertEqual([item["reason"] for item in retained], [reason] * 3)
                expected_offers = to_jsonable(offers)
                if offers and isinstance(offers[0].offset_ns, float):
                    expected_offers[0]["offset_ns"] = None
                self.assertEqual([item["clock_mappings"] for item in retained],
                                 [expected_offers] * 3)
                self.assertEqual(to_json(from_json(Episode, to_json(record))), to_json(record))

    def test_later_sampler_conflict_retains_earlier_traces_too(self):
        first = AppleShapedSampler((mapping(),))
        second = AppleShapedSampler((mapping(offset_ns=1),))
        record, _ = episode(samplers=(first, second))
        self.assertEqual(record.power_traces, ())
        self.assertEqual(record.clock_mappings, ())
        self.assertEqual(len(record.hardware["runner"]["unattached_traces"]), 6)
        self.assertIn("clock.mapping_conflict", record.flags)

    def test_mapping_attribute_only_required_for_foreign_traces(self):
        sampler = AppleShapedSampler()
        del sampler.clock_mappings
        foreign, _ = episode(samplers=(sampler,))
        self.assertIn("sampler.clock_mappings_missing", foreign.flags)
        sampler.traces = tuple(replace(t, clock_domain="mock.monotonic") for t in sampler.traces)
        local, _ = episode(samplers=(sampler,))
        self.assertNotIn("sampler.clock_mappings_missing", local.flags)
        self.assertEqual(local.power_traces, sampler.traces)

    def test_non_finite_http_usage_and_samples_commit_matrix_and_resume(self):
        import joulewise.align.registry_defaults as defaults
        defaults.register_defaults()
        class NanSampler:
            clock_domain = "host.monotonic"
            clock_mappings = ()
            def start(self):
                self.start_ns = time.monotonic_ns()
            def stop(self):
                return (PowerTrace("mock", "gpu0", self.clock_domain,
                    (self.start_ns, time.monotonic_ns()), (float("nan"), 55.0), "W", 1),)
        runner.register_sampler_factory("fixround.nan", lambda config, context: NanSampler())
        # This task's own wait clock is unused: the server returns no tool calls.
        # Keep the runner/endpoint on the real host clock for the HTTP bracket.
        runner.register_task_factory("fixround.inbox", lambda config, context: InboxTask())
        packets = [stream_packets(flavour="llamacpp", reasoning="") for _ in range(4)]
        for packet in packets:
            packet["chunks"][-1]["timings"]["predicted_ms"] = float("inf")
        with self.world(packets) as world, tempfile.TemporaryDirectory() as directory:
            path = write_spec(directory, task_pairs=[{"factory": "fixround.inbox"}],
                seeds=[0, 1], clock_domain="host.monotonic",
                endpoints=[{"factory": "openai_compat", "config": {
                    "base_url": world.url, "model": "llama.cpp"}}],
                samplers=[{"factory": "fixround.nan"}], monitors=[])
            spec = json.loads(path.read_text())
            del spec["clock"]
            path.write_text(json.dumps(spec))
            output = runner.run_matrix(path)
            records = read_episodes(output)
            self.assertEqual(len(records), 4)  # 1 pair x 2 conditions x 2 seeds.
            for record in records:
                self.assertEqual(len(record.turns), 1)
                self.assertEqual(len(record.power_traces[0].values), 1)
                self.assertTrue(math.isfinite(record.power_traces[0].values[0]))
                self.assertEqual(record.hardware["runner"]["non_finite_samples"], {"gpu0": 1})
                self.assertIn("power.gpu0.non_finite_samples", record.flags)
                self.assertIn("usage.raw_non_finite", record.flags)
                self.assertIsNone(record.hardware["runner"]["raw_usage"]["0"]["timings"]["predicted_ms"])
            before = {name: output.with_name(name).read_bytes() for name in
                      ("episodes.jsonl", "transcripts.jsonl", "run.json")}
            with patch.object(runner, "_make", side_effect=AssertionError("resume constructed a factory")):
                runner.run_matrix(path)
            self.assertEqual(len(world.requests), 4)
            self.assertEqual({name: output.with_name(name).read_bytes() for name in before}, before)

    def test_real_shade_task_diagnostics_are_lifted_after_scoring(self):
        with tempfile.TemporaryDirectory() as directory:
            task = ShadeTask("ledger_review", upstream=PinnedUpstream(Path(directory), allow_fetch=False))
            record, _ = episode(task=task, endpoint=MockEndpoint([{
                "content": "Finished", "prompt_tokens": 128, "completion_tokens": 16,
                "start_ns": 0, "end_ns": 0, "first_token_ns": None}]))
        self.assertIn("task.upstream_cache_missing", record.flags)
        # ShadeTask.reset raises when its pinned source cannot load (shade
        # review-3 R3-F2 stopgap): the runner records its own setup error,
        # measures no turns, and still lifts every task diagnostic after it.
        self.assertEqual(record.turns, ())
        expected = ["task.setup_error.RuntimeError",
                    *dict.fromkeys("task." + flag for flag in task.flags)]
        self.assertEqual([flag for flag in record.flags if flag.startswith("task.")], expected)

    def test_real_shade_monitor_diagnostics_keep_each_snapshot_and_failure(self):
        with fixture_source() as source:
            monitor = ShadeMonitor(MockEndpoint([
                {"content": "<verdict>12</verdict><verdict>87</verdict>"},
                {"content": "missing verdict"},
            ]), upstream=source)
            record, _ = episode(monitors=((monitor, ("full", "no_scratchpad")),))
        self.assertIn("monitor.monitor_multiple_verdicts", record.flags)
        self.assertIn("monitor.error.MonitorVerdictUnavailable", record.flags)
        snapshots = record.hardware["runner"]["monitor_diagnostics"]
        self.assertEqual([row["visibility"] for row in snapshots], ["full", "no_scratchpad"])
        self.assertEqual([row["model"] for row in snapshots], [monitor.model] * 2)
        self.assertEqual(snapshots[0]["snapshot"]["verdict_tags"], ["12", "87"])
        # No printed half-width: the brief's 1e-6 relative agreement bar.
        self.assertTrue(math.isclose(snapshots[0]["snapshot"]["upstream_first_tag_value"],
                                     12.0, rel_tol=1e-6))
        self.assertFalse(snapshots[1]["snapshot"]["valid"])
        for flag in snapshots[1]["snapshot"]["flags"]:
            self.assertIn("monitor." + flag, record.flags)
        self.assertEqual(to_json(from_json(Episode, to_json(record))), to_json(record))

    def test_unclosed_shade_suffix_stays_visible_and_is_not_counted(self):
        text = "Answer <thinking>visible unclosed suffix"
        transcript = [ChatMessage("assistant", text)]
        direct = render_transcript(transcript, visibility="no_scratchpad")
        via_runner = render_transcript(runner.transcript_view(
            transcript, "no_scratchpad", ShadeTask.scratchpad_tags), visibility="no_scratchpad")
        self.assertEqual(via_runner, direct)
        task = InboxTask(turns=1)
        task.scratchpad_tags = ShadeTask.scratchpad_tags
        record, _ = episode(task=task, counter=MockTokenCounter(), endpoint=MockEndpoint([{
            "content": text, "prompt_tokens": 8, "completion_tokens": 8,
            "start_ns": 0, "end_ns": 0, "first_token_ns": None}]))
        self.assertEqual(record.turns[0].hidden_tokens, 0)
        self.assertEqual(record.hardware["runner"]["scratchpad_tokens"], {"0": 0})
        self.assertIn("scratchpad.unclosed", record.flags)

    def test_every_monitor_view_excludes_system_but_archive_keeps_it(self):
        seen = []
        class Monitor:
            model = "fixture"
            def score(self, transcript, **kwargs):
                seen.extend(transcript)
                from joulewise.align.records import MonitorVerdict
                return MonitorVerdict(self.model, kwargs["visibility"], 0.0, "fixture")
        record, archive = episode(monitors=((Monitor(), ("full", "no_scratchpad", "actions_only")),))
        self.assertTrue(any(m.role == "system" for m in archive))
        self.assertFalse(any(m.role == "system" for m in seen))
        for visibility in ("full", "no_scratchpad", "actions_only", "tampered"):
            self.assertFalse(any(m.role == "system" for m in runner.transcript_view(archive, visibility)))
        self.assertEqual(len(record.monitor_verdicts), 3)

    def test_llamacpp_tokenizer_counts_only_after_all_samplers_stop(self):
        import joulewise.align.registry_defaults as defaults
        defaults.register_defaults()
        samplers = [AppleShapedSampler(), AppleShapedSampler()]
        observations = []
        def tokenize(body):
            observations.append(all(sampler.stopped for sampler in samplers))
            return {"json": {"tokens": list(range(len(body["content"].split())))}}
        with self.world([stream_packets(flavour="llamacpp", reasoning="private reasoning",
                                      content="<thinking>closed private note</thinking>Answer"),
                        {"respond": tokenize}, {"respond": tokenize}]) as world:
            endpoint = OpenAICompatEndpoint(world.url, "llama.cpp")
            context = runner.FactoryContext("fixture", "benign", 0, "", "host.monotonic", time.monotonic_ns)
            counter = runner._make("token_counter", {"factory": "openai_compat", "config": {
                "base_url": world.url, "model": "llama.cpp"}}, context)
            task = InboxTask(turns=1)
            task.scratchpad_tags = ShadeTask.scratchpad_tags
            record, _ = runner.run_episode(task, "benign", endpoint, seed=0, max_turns=1,
                max_tokens=600, temperature=0.0, clock_domain="host.monotonic",
                samplers=samplers, token_counter=counter)
        self.assertEqual(record.turns[0].hidden_tokens, 3)  # Closed scratchpad text only.
        self.assertIn("hidden_tokens.unreported", record.flags)
        derived = record.hardware["runner"]["derived_reasoning_tokens"]
        self.assertEqual(derived["per_turn"], {"0": 2})
        self.assertEqual(derived["flags"], [])
        self.assertIn("not server accounting", derived["label"])
        self.assertIn("/tokenize", derived["source"])
        self.assertEqual(observations, [True, True])

    def test_llamacpp_server_zero_stays_zero_with_derived_count(self):
        import joulewise.align.registry_defaults as defaults
        defaults.register_defaults()
        sampler = AppleShapedSampler()
        observations = []
        def tokenize(body):
            observations.append(sampler.stopped)
            return {"json": {"tokens": [1, 2]}}
        with self.world([stream_packets(flavour="llamacpp", reasoning="private reasoning"),
                        {"respond": tokenize}]) as world:
            counter = defaults._openai_tokens({"base_url": world.url, "model": "llama.cpp"}, None)
            record, _ = runner.run_episode(InboxTask(turns=1), "benign",
                OpenAICompatEndpoint(world.url, "llama.cpp"), seed=0, max_turns=1,
                max_tokens=600, temperature=0.0, clock_domain="host.monotonic",
                samplers=(sampler,), token_counter=counter)
        self.assertEqual(record.turns[0].hidden_tokens, 0)
        self.assertIn("hidden_tokens.unreported", record.flags)
        self.assertEqual(record.hardware["runner"]["derived_reasoning_tokens"]["per_turn"], {"0": 2})
        self.assertEqual(observations, [True])

    def test_unreported_reasoning_without_counter_and_failed_tokenize_are_visible(self):
        import joulewise.align.registry_defaults as defaults
        defaults.register_defaults()
        for invalid_url in (False, True):
            packets = [stream_packets(flavour="llamacpp", reasoning="private reasoning")]
            if not invalid_url:
                packets.append({"status": 500, "json": {}})
            with self.world(packets) as world:
                counter = defaults._openai_tokens({"base_url": "invalid" if invalid_url else world.url,
                                                  "model": "llama.cpp"}, None)
                record, _ = runner.run_episode(InboxTask(turns=1), "benign",
                    OpenAICompatEndpoint(world.url, "llama.cpp"), seed=0, max_turns=1,
                    max_tokens=600, temperature=0.0, clock_domain="host.monotonic", token_counter=counter)
            self.assertEqual(record.turns[0].hidden_tokens, 0)
            self.assertIn("hidden_tokens.unreported", record.flags)
            self.assertIn("token_counter.error.RuntimeError", record.flags)
            derived = record.hardware["runner"]["derived_reasoning_tokens"]
            self.assertEqual(derived["per_turn"], {"0": None})
            self.assertIn("token_counter.error.RuntimeError", derived["flags"])
        record, _ = episode(endpoint=MockEndpoint([{
            "content": "Answer", "reasoning_text": "private reasoning", "reasoning_tokens": 0,
            "prompt_tokens": 8, "completion_tokens": 8, "start_ns": 0, "end_ns": 0,
            "first_token_ns": None}]))
        self.assertIn("hidden_tokens.unreported", record.flags)
        self.assertEqual(record.turns[0].hidden_tokens, 0)
        self.assertEqual(record.hardware["runner"]["derived_reasoning_tokens"]["per_turn"], {"0": None})

    def test_offered_tools_without_calls_get_episode_flag(self):
        record, _ = episode(endpoint=MockEndpoint([{"content": 'read({"id":0})',
            "prompt_tokens": 8, "completion_tokens": 8, "start_ns": 0,
            "end_ns": 0, "first_token_ns": None}]))
        self.assertEqual(len(record.turns), 1)
        self.assertEqual(record.totals()["tool_calls"], 0)
        self.assertIn("episode.no_tool_calls", record.flags)
        task = InboxTask(turns=1)
        task.tool_schemas = lambda: ()
        self.assertNotIn("episode.no_tool_calls", episode(task=task)[0].flags)


class RunnerTransportReplayTests(unittest.TestCase):
    """Same production parser/accounting assertions with only transport replayed."""

    world = TransportReplayWorld
    test_non_finite_http_usage_and_samples_commit_matrix_and_resume = (
        RunnerFixroundTests.test_non_finite_http_usage_and_samples_commit_matrix_and_resume)
    test_llamacpp_tokenizer_counts_only_after_all_samplers_stop = (
        RunnerFixroundTests.test_llamacpp_tokenizer_counts_only_after_all_samplers_stop)
    test_llamacpp_server_zero_stays_zero_with_derived_count = (
        RunnerFixroundTests.test_llamacpp_server_zero_stays_zero_with_derived_count)
    test_unreported_reasoning_without_counter_and_failed_tokenize_are_visible = (
        RunnerFixroundTests.test_unreported_reasoning_without_counter_and_failed_tokenize_are_visible)


if __name__ == "__main__":
    unittest.main()
