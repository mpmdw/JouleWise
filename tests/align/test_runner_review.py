"""Direct current-code regressions retained from the first execution review.

No history checkout, subprocess discovery or archived implementation is involved.
The endpoint/task ledger and independently reconstructed matrix counts exercise
the same public paths as production.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from joulewise.align import runner
from joulewise.align.mock_world import (
    InboxTask, MockMonitor, MockTokenCounter, ScriptConfig, ScriptedEndpoint,
    SyntheticPowerSampler, VirtualClock,
)
from joulewise.align.records import PowerTrace, read_episodes, to_json
from tests.align.test_runner import inbox_episode
from tests.align.test_runner_matrix import write_spec


class ReviewProbeTests(unittest.TestCase):
    def test_matrix_cells_equal_standalone_and_resume_with_unavailable_endpoint(self):
        with tempfile.TemporaryDirectory() as directory:
            path = runner.run_matrix(write_spec(directory))
            records = read_episodes(path)
            self.assertEqual(len(records), 20)  # Two pairs x two conditions x five seeds.
            for episode in records:
                self.assertEqual(episode.flags, ())
                clock = VirtualClock()
                task = InboxTask(episode.task_pair, clock=clock)
                endpoint = ScriptedEndpoint(clock=clock, condition=episode.condition)
                sampler = SyntheticPowerSampler(clock=clock, seed=episode.seed,
                    interval_ns=100_000_000, averaging_window_ns=100_000_000,
                    noise_watts=0.0, quantum_watts=0.0)
                direct, _ = runner.run_episode(task, episode.condition, endpoint,
                    monitors=((MockMonitor(), ("full", "no_scratchpad", "actions_only")),),
                    samplers=(sampler,), seed=episode.seed, max_turns=40, max_tokens=600,
                    temperature=0.0, clock_domain="mock.monotonic", clock=clock,
                    token_counter=MockTokenCounter(), matrix_id="twenty-inbox-v1")
                # Identical components, code and virtual inputs: bit identity is
                # intended for work, traces, views and scores, apart from matrix IDs.
                for field in ("turns", "power_traces", "monitor_verdicts", "main_task_score",
                              "side_task_success", "start_ns", "end_ns", "flags"):
                    self.assertEqual(getattr(episode, field), getattr(direct, field))
            before = path.read_bytes()
            with patch.object(runner, "_make", side_effect=AssertionError("completed cells skip factories")):
                runner.run_matrix(path.parent.parent / "matrix.json")
            self.assertEqual(path.read_bytes(), before)

    def test_twelve_commit_boundaries_recover_identical_files(self):
        class Killed(BaseException):
            pass
        with tempfile.TemporaryDirectory() as directory:
            base = runner.run_matrix(write_spec(directory, "base.json", output_dir="base"))
            expected = {name: base.with_name(name).read_bytes()
                        for name in ("episodes.jsonl", "transcripts.jsonl")}
            for ordinal in range(1, 13):
                spec = write_spec(directory, str(ordinal) + ".json", output_dir=str(ordinal))
                append = runner._append
                count = 0
                def kill(path, value):
                    nonlocal count
                    if path.name == "episodes.jsonl":
                        count += 1
                        if count == ordinal:
                            raise Killed()
                    append(path, value)
                with patch.object(runner, "_append", side_effect=kill):
                    with self.assertRaises(Killed):
                        runner.run_matrix(spec)
                recovered = runner.run_matrix(spec)
                for name, content in expected.items():
                    self.assertEqual(recovered.with_name(name).read_bytes(), content)

    def test_null_and_bytes_model_work_reaches_independent_ledger_count(self):
        class Null(ScriptedEndpoint):
            def chat(self, messages, **kwargs):
                result = super().chat(messages, **kwargs)
                return replace(result, content=None) if result.tool_calls else result
        class Bytes(InboxTask):
            def call_tool(self, name, arguments_json):
                super().call_tool(name, arguments_json)
                return b"\x00raw"
        for count, options, flag in (
            (26, {"endpoint_class": Null}, "endpoint.content_missing"),
            (10, {"task_class": Bytes}, "tool.non_text_result"),
        ):
            # Configured turn counts reproduce the old null/bytes review worlds.
            ep, _, task, endpoint, _ = inbox_episode("benign", config=ScriptConfig(turns=count), **options)
            self.assertEqual(len(ep.turns), count)
            self.assertEqual(len(ep.turns), len(endpoint.ledger.turns))
            self.assertEqual([(c.name, c.start_ns, c.end_ns) for t in ep.turns for c in t.tool_calls],
                             [(c.name, c.start_ns, c.end_ns) for c in task.ledger.tools])
            self.assertIn(flag, ep.flags)
            self.assertFalse(any(f.startswith("runner.error.") for f in ep.flags))

    def test_corrupt_metadata_empty_matrix_string_visibility_and_changed_spec(self):
        with tempfile.TemporaryDirectory() as directory:
            spec = write_spec(directory, seeds=[0])
            path = runner.run_matrix(spec)
            path.with_name("run.json").write_text("{broken")
            runner.run_matrix(spec)
            self.assertIn("resume.invalid_metadata",
                          json.loads(path.with_name("run.json").read_text())["flags"])
            payload = json.loads(spec.read_text())
            payload["max_tokens"] += 1  # Explicit settings mutation under a fixed matrix ID.
            spec.write_text(json.dumps(payload))
            runner.run_matrix(spec)
            self.assertIn("matrix.spec_changed",
                          json.loads(path.with_name("run.json").read_text())["flags"])
            empty = runner.run_matrix(write_spec(directory, "empty.json", endpoints=[], output_dir="empty"))
            self.assertEqual(read_episodes(empty), [])
            self.assertIn("matrix.empty", json.loads(empty.with_name("run.json").read_text())["flags"])
            visible = runner.run_matrix(write_spec(directory, "vis.json", seeds=[0], conditions=["benign"],
                output_dir="vis", monitors=[{"factory": "mock.monitor", "visibilities": "full"}]))
            self.assertEqual([len(e.monitor_verdicts) for e in read_episodes(visible)], [1, 1])

    def test_late_trace_and_reasoning_counts_without_scratchpad_counter(self):
        class Late(SyntheticPowerSampler):
            def stop(self):
                self.started = False
                # Sampling begins one configured cadence after the stop bracket,
                # so both integer stamps are provably later than episode.end_ns.
                first = self.clock() + self.interval_ns
                return (PowerTrace("mock", "gpu0", self.clock_domain,
                    (first, first + self.interval_ns), (self.model.idle_watts,) * 2,
                    "W", self.interval_ns),)
        episode = inbox_episode(sampler_class=Late)[0]
        self.assertEqual(len(episode.power_traces), 1)
        self.assertGreater(episode.power_traces[0].t_ns[0], episode.end_ns)
        for seed in range(6):
            ep, archive, _, _, _ = inbox_episode(seed=seed)
            no_counter = inbox_episode(seed=seed, counter=False)[0]
            scratch = sum(ep.hardware["runner"]["scratchpad_tokens"].values())
            self.assertEqual(ep.totals()["hidden_tokens"] - no_counter.totals()["hidden_tokens"], scratch)
            self.assertEqual(no_counter.totals()["hidden_tokens"], 120)
            self.assertTrue(any("<jw_reasoning>" in m.content for m in archive))


if __name__ == "__main__":
    unittest.main()
