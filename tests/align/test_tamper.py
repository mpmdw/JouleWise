"""Tamper transforms on complete real-runner inbox episodes."""

from __future__ import annotations

import random
import unittest
from dataclasses import replace

from joulewise.align.records import to_json
from joulewise.align.tamper import delete_turns, drop_tool_calls, hide_scratchpad, random_tamper
from tests.align.test_runner import inbox_episode


class TamperTests(unittest.TestCase):
    def setUp(self):
        self.ep = inbox_episode()[0]

    def test_turn_deletion_marks_and_preserves_input(self):
        before = to_json(self.ep)
        result = delete_turns(self.ep, [6])
        self.assertFalse(result.turns[6].logged)
        self.assertEqual(result.totals(logged_only=True)["turns"], 12)
        self.assertEqual(result.totals(), self.ep.totals())
        self.assertIs(result.power_traces, self.ep.power_traces)
        self.assertIn("tamper.delete_turns", result.flags)
        self.assertEqual(to_json(self.ep), before)

    def test_tool_drop_keeps_physical_call(self):
        result = drop_tool_calls(self.ep, lambda call: call.name == "transfer")
        self.assertFalse(result.turns[6].tool_calls[0].logged)
        self.assertEqual(result.totals(logged_only=True)["tool_calls"], 11)
        self.assertEqual(result.totals()["tool_calls"], 12)
        self.assertEqual(result.turns[6].tool_calls[0].start_ns,
                         self.ep.turns[6].tool_calls[0].start_ns)
        self.assertIs(result.power_traces, self.ep.power_traces)

    def test_already_hidden_scratchpad_is_idempotent(self):
        before = to_json(self.ep)
        result = hide_scratchpad(self.ep)
        self.assertEqual(result.turns[6].hidden_tokens, 184)
        self.assertEqual(result.flags, (*self.ep.flags, "tamper.hide_scratchpad", "tamper.hide_scratchpad.noop"))
        randomized = random_tamper(self.ep, random.Random(0), "hide_scratchpad", 1.0)
        self.assertEqual(randomized.flags, (*self.ep.flags, "tamper.hide_scratchpad",
                                          "tamper.hide_scratchpad.noop", "tamper.random_tamper"))
        self.assertEqual(result.totals()["decode_tokens"], self.ep.totals()["decode_tokens"])
        self.assertEqual(to_json(hide_scratchpad(result)), to_json(result))
        self.assertEqual(to_json(self.ep), before)

    def test_visible_scratchpad_metadata_moves_tokens_once(self):
        hardware = dict(self.ep.hardware)
        metadata = dict(hardware["runner"])
        metadata["scratchpad_counted_hidden"] = [i for i in metadata["scratchpad_counted_hidden"] if i != 6]
        hardware["runner"] = metadata
        visible = replace(self.ep, hardware=hardware, turns=tuple(
            replace(turn, hidden_tokens=120) if turn.index == 6 else turn for turn in self.ep.turns))
        result = hide_scratchpad(visible)
        self.assertEqual(result.turns[6].hidden_tokens, 120 + 64)
        self.assertEqual(result.totals()["decode_tokens"], visible.totals()["decode_tokens"])
        self.assertNotIn("tamper.hide_scratchpad.noop", result.flags)
        # A second application changes no token count and must now disclose noop.
        repeated = hide_scratchpad(result)
        self.assertEqual(to_json(repeated), to_json(replace(result,
            flags=(*result.flags, "tamper.hide_scratchpad.noop"))))
        self.assertEqual(to_json(hide_scratchpad(repeated)), to_json(repeated))

    def test_missing_counts_flag_without_guess(self):
        source = replace(self.ep, hardware={})
        result = hide_scratchpad(source)
        self.assertIn("tamper.hide_scratchpad.count_unavailable", result.flags)
        self.assertEqual(result.totals(), source.totals())

    def test_random_transforms_are_seeded_and_preserve_measured_work(self):
        for kind in ("delete_turns", "drop_tool_calls", "hide_scratchpad"):
            with self.subTest(kind=kind):
                first = random_tamper(self.ep, random.Random(7), kind, 0.5)
                second = random_tamper(self.ep, random.Random(7), kind, 0.5)
                self.assertEqual(to_json(first), to_json(second))
                self.assertEqual(first.totals(), self.ep.totals())
                self.assertIs(first.power_traces, self.ep.power_traces)
                self.assertIn("tamper.random_tamper", first.flags)
        for fraction in (0.0, 1.0):
            result = random_tamper(self.ep, random.Random(7), "delete_turns", fraction)
            self.assertEqual(result.totals(logged_only=True)["turns"],
                             len(self.ep.turns) - round(fraction * len(self.ep.turns)))

    def test_invalid_requests_are_flags(self):
        result = delete_turns(self.ep, [100])
        self.assertIn("tamper.delete_turns.index_out_of_range", result.flags)
        for fraction in (-0.1, 1.1, float("nan")):
            result = random_tamper(self.ep, random.Random(7), "delete_turns", fraction)
            self.assertIn("tamper.random_tamper.invalid_fraction", result.flags)
        result = random_tamper(self.ep, random.Random(7), "unknown", 0.5)
        self.assertIn("tamper.random_tamper.unknown_kind", result.flags)
        def broken(call):
            raise RuntimeError
        result = drop_tool_calls(self.ep, broken)
        self.assertIn("tamper.drop_tool_calls.predicate_error", result.flags)
        self.assertEqual(result.totals(logged_only=True), self.ep.totals(logged_only=True))


if __name__ == "__main__":
    unittest.main()
