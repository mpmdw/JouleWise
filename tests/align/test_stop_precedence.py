"""Regressions for simultaneous ALIGN stop causes."""
from dataclasses import replace
import unittest

from joulewise.align.apple.diagnostics import end_state
from joulewise.align.apple.stop_precedence import has_fault, primary_stop
from tests.align.test_apple_campaign import episode_spec
from joulewise.align.records import Episode


class StopPrecedenceTests(unittest.TestCase):
    def test_faults_outrank_each_thermal_cause_and_are_failures(self):
        cases = (
            (("endpoint_error:RuntimeError:native", "thermal.gate_timeout:1"), "timeout"),
            (("episode_error:RuntimeError:runner", "thermal.hold_timeout:1"), "timeout"),
            (("runner.error:stream", "thermal.state_unobserved"), "unobserved"),
        )
        for flags, outcome in cases:
            with self.subTest(flags=flags):
                intervals = ({"kind": "H", "outcome": outcome},)
                self.assertTrue(has_fault(flags))
                self.assertEqual(primary_stop(flags, thermal_intervals=intervals), "runner.error")

    def test_deadman_then_fault_then_thermal_then_decode_budget(self):
        causes = ("episode.decode_budget:1", "thermal.hold_timeout:1",
                  "endpoint_error:RuntimeError:native", "episode.deadman:1")
        self.assertEqual(primary_stop(causes), "episode.deadman")
        self.assertEqual(primary_stop(causes[:-1]), "runner.error")
        self.assertEqual(primary_stop(causes[:2]), "thermal.incomplete")
        self.assertEqual(primary_stop(causes[:1]), "episode.decode_budget")

    def test_unobserved_g1_and_h_remain_valid_but_flagged_in_diagnostics(self):
        base = episode_spec(hidden=False)
        episode = Episode(episode_id="x", task_pair="x", condition=base.condition,
                          agent_model="x", endpoint="x", seed=1, clock_domain="x",
                          start_ns=0, end_ns=1, turns=(), main_task_score=None,
                          side_task_success=None,
                          hardware={"thermal": {"intervals": [
                              {"kind": "G1", "outcome": "unobserved"},
                              {"kind": "H", "outcome": "unobserved"}]}},
                          flags=("thermal.state_unobserved",))
        self.assertEqual(end_state(episode), "returned_without_tool_call")
