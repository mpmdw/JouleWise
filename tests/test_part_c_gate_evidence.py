"""Synthetic gate evidence for the Part C cited rebind."""
import unittest

from joulewise.part_c_gate_evidence import g1_records, gate_durations


def interval(kind, turn, seconds, outcome="released"):
    return {"kind": kind, "turn": turn, "outcome": outcome,
            "start_ns": 1_000_000_000, "end_ns": int((1 + seconds) * 1_000_000_000),
            "duration_s": seconds}


class PartCGateEvidenceTests(unittest.TestCase):
    def test_every_later_admitted_turn_needs_its_own_release(self):
        turns = [{"index": i} for i in range(3)]
        g0, g1, g2 = interval("G0", 0, 10), interval("G1", 1, 20), interval("G1", 2, 30)
        self.assertTrue(g1_records(turns, [g0, g1, g2])["pass"])
        for rows in ([g0], [g0, g1, g1, g2], [g0, g1, {**g2, "turn": 3}],
                     [g0, g1, {**g2, "outcome": "unobserved"}]):
            with self.subTest(rows=rows):
                self.assertFalse(g1_records(turns, rows)["pass"])
        self.assertTrue(g1_records(turns[:1], [g0])["pass"])

    def test_duration_reconciles_to_monotonic_bounds_before_a_total(self):
        g0, g1, hold = interval("G0", 0, 10), interval("G1", 1, 20), interval("H", 1, 30)
        self.assertEqual(gate_durations([g0, g1, hold]), {"pass": True, "errors": [], "total_s": 60})
        for wrong in (0, -1, float("nan"), float("inf"), "20", None):
            with self.subTest(duration=wrong):
                evidence = gate_durations([g0, {**g1, "duration_s": wrong}, hold])
                self.assertFalse(evidence["pass"])
                self.assertIsNone(evidence["total_s"])
        self.assertFalse(gate_durations([g0, {**g1, "end_ns": None}, hold])["pass"])
