import tempfile
import unittest
from pathlib import Path

from joulewise.align.records import (
    ClockMapping, Episode, MonitorVerdict, PowerTrace, RecordError, RouterLog, ToolCall, Turn,
    from_json, read_episodes, to_json, write_episodes,
)


def make_episode(**overrides):
    turns = (
        Turn(index=0, start_ns=1_000, end_ns=5_000, context_tokens=0, prefill_tokens=900,
             decode_tokens=120, hidden_tokens=40, first_token_ns=2_000,
             tool_calls=(ToolCall("send_email", 4_000, 4_500, 210, 64),)),
        Turn(index=1, start_ns=6_000, end_ns=9_000, context_tokens=1_020, prefill_tokens=300,
             decode_tokens=80, logged=False),
    )
    base = dict(
        episode_id="e1", task_pair="shade/bank_transfer", condition="sabotage",
        agent_model="qwen3-8b", endpoint="vllm:local", seed=7, clock_domain="hostA.mono",
        start_ns=0, end_ns=10_000, turns=turns, main_task_score=0.8, side_task_success=True,
        monitor_verdicts=(MonitorVerdict("gpt-oss-20b", "full", 63.5, "ab" * 32),),
        power_traces=(PowerTrace("nvml_energy", "gpu0", "gpu0.mono", (0, 100, 200), (10.0, 12.5, 15.25),
                                 "J_cumulative", 100, resolution=0.001),),
        clock_mappings=(ClockMapping("gpu0.mono", "hostA.mono", 5, 2, "round-trip bracket"),),
        router_log=RouterLog("qwen3-30b-a3b", 8, 2, (0, 1), ("prefill", "decode"),
                             (((0, 1), (2, 3)), ((4, 5), (6, 7)))),
        hardware={"gpu": "RTX 3080 Ti"}, flags=("clock.offset_estimated",),
    )
    base.update(overrides)
    return Episode(**base)


class RecordsTest(unittest.TestCase):
    def test_round_trip_is_exact(self):
        episode = make_episode()
        again = from_json(Episode, to_json(episode))
        self.assertEqual(again, episode)
        self.assertEqual(to_json(again), to_json(episode))

    def test_jsonl_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "episodes.jsonl"
            self.assertEqual(write_episodes(path, [make_episode(), make_episode(episode_id="e2")]), 2)
            self.assertEqual([e.episode_id for e in read_episodes(path)], ["e1", "e2"])

    def test_totals_respect_logging(self):
        episode = make_episode()
        self.assertEqual(episode.totals()["decode_tokens"], 200)
        self.assertEqual(episode.totals(logged_only=True)["decode_tokens"], 120)
        self.assertEqual(episode.totals(logged_only=True)["tool_calls"], 1)

    def test_refusals(self):
        with self.assertRaises(RecordError):
            Turn(index=0, start_ns=5, end_ns=4, context_tokens=0, prefill_tokens=1, decode_tokens=1)
        with self.assertRaises(RecordError):
            Turn(index=0, start_ns=0, end_ns=4, context_tokens=0, prefill_tokens=1, decode_tokens=1,
                 hidden_tokens=2)
        with self.assertRaises(RecordError):
            make_episode(clock_mappings=())  # trace domain without a mapping
        with self.assertRaises(RecordError):
            from_json(Episode, to_json(make_episode()).replace('"seed":7', '"seed":7,"extra":1'))
        with self.assertRaises(RecordError):
            PowerTrace("nvml_power", "gpu0", "d", (0, 0), (1.0, 2.0), "W", 100)


if __name__ == "__main__":
    unittest.main()
