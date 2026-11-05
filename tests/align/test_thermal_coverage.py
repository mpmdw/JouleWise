"""Nominal sampling grid coverage is independent of episode phase."""
import random
import unittest
from joulewise.align.apple import thermal

NS = 10**9
VALUES = {"sensors": {"TDIE": 40}, "errors": {}}

def rows(seconds, jitter_ms=8):
    rng = random.Random(658)
    return [{"module": "temperature", "kind": "reading", "values": VALUES,
             "started": {"monotonic_ns": i*NS+rng.randrange(jitter_ms*10**6+1)},
             "finished": {"monotonic_ns": i*NS+70_000_000}} for i in range(seconds)]

class CoverageTests(unittest.TestCase):
    def test_regular_jittered_samples_pass_at_every_span_phase(self):
        for jitter in (8, 30, 60):
            readings = rows(1810, jitter)
            for phase_ms in (0, 3, 4, 5, 30, 60, 99, 101, 250, 500, 999):
                start = 2*NS+phase_ms*10**6
                result = thermal.coverage(readings, start, start+1800*NS, ["TDIE"])["all_keys"]
                with self.subTest(jitter=jitter, phase_ms=phase_ms):
                    self.assertGreaterEqual(result["sample_fraction"], .99)
                    self.assertLessEqual(result["max_interval_ns"], 2*NS)
                    self.assertEqual(result["gaps_ns"], [])

    def test_short_gate_spans_and_tiny_trailing_edges_have_no_phantom_slot(self):
        readings = rows(70)
        for seconds in (5, 8, 30, 60, 61):
            for phase_ms in (0, 3, 5, 40, 250, 500, 999):
                start = 2*NS+phase_ms*10**6
                result = thermal.coverage(readings, start, start+seconds*NS+3_600_000,
                                           ["TDIE"])["all_keys"]
                with self.subTest(seconds=seconds, phase_ms=phase_ms):
                    self.assertEqual(result["sample_fraction"], 1)
                    self.assertLessEqual(result["max_interval_ns"], 2*NS)

    def test_real_missing_reads_duplicates_edges_and_long_reads_do_not_hide_gaps(self):
        readings = rows(12)
        readings = [r for i, r in enumerate(readings) if i not in (3, 4, 5)]
        readings += [readings[1]]*10
        result = thermal.coverage(readings, 0, 12*NS, ["TDIE"])["all_keys"]
        self.assertLess(result["sample_fraction"], .99)
        self.assertGreater(result["max_interval_ns"], 3*NS)
        self.assertEqual(len(result["gaps_ns"]), 1)
        # A two-second SMC call supplies no one-Hz sample.
        counter = thermal.Coverage(0, ["TDIE"])
        counter.observe(0, 2*NS, VALUES)
        self.assertEqual(counter.report(5*NS)["all_keys"]["sample_fraction"], 0)
        self.assertEqual(counter.report(5*NS)["all_keys"]["max_interval_ns"], 5*NS)
