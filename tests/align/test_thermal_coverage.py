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
    def test_empty_cell_runs_include_edges_duplicates_and_half_period_ties(self):
        # Six one-second cells; missing one is allowed, a run of two is not.
        for missing, longest in (((0,), 1), ((5,), 1), ((0, 1), 2), ((4, 5), 2),
                                 ((2, 3), 2), ((1, 3), 1), (tuple(range(6)), 6)):
            counter = thermal.Coverage(0, ['TDIE'], tolerance_ns=NS//2)
            for tick in range(6):
                for _ in range(2):  # duplicates never close empty cells
                    counter.observe(tick*NS, tick*NS, VALUES if tick not in missing else
                                    {'sensors': {}, 'errors': {'TDIE': 'miss'}})
            self.assertEqual(counter.report(6*NS)['per_key']['TDIE']['max_consecutive_empty_cells'], longest)
        counter = thermal.Coverage(0, ['TDIE'], tolerance_ns=NS//2)
        counter.observe(0, 0, {'sensors': {}, 'errors': {}})
        counter.observe(NS//2, NS//2, VALUES)  # rounds to cell 1
        self.assertEqual(counter.report(3*NS)['all_keys']['max_consecutive_empty_cells'], 1)
        self.assertEqual(counter.report(0)['all_keys']['max_consecutive_empty_cells'], 0)

    def test_default_and_explicit_tolerances(self):
        default = thermal.Coverage(0, ["TDIE"])
        # Preserve the existing default: one tenth of the one-second period.
        self.assertEqual(default.tolerance_ns, NS // 10)
        self.assertEqual(default.report(NS)["tolerance_ns"], NS // 10)
        for tolerance in (1, NS // 10, NS // 2):
            with self.subTest(tolerance=tolerance):
                self.assertEqual(thermal.Coverage(0, ["TDIE"], tolerance_ns=tolerance)
                                 .report(NS)["tolerance_ns"], tolerance)
        for invalid in (0, -1, NS // 2 + 1, .1, "100000000", None, True):
            with self.subTest(invalid=invalid), self.assertRaisesRegex(ValueError, '500000000 ns'):
                thermal.Coverage(0, ["TDIE"], tolerance_ns=invalid)
        self.assertIn('all edges snapped', thermal.Coverage(0, ['TDIE'], tolerance_ns=NS//2)
                      .report(NS)['edge_policy'])

    def test_half_period_duplicates_and_ties_count_once(self):
        counter = thermal.Coverage(0, ["TDIE"], tolerance_ns=NS // 2)
        counter.observe(0, 0, VALUES)
        counter.observe(NS, NS, VALUES)
        counter.observe(NS + NS // 10, NS + NS // 5, VALUES)
        # Exactly half a period rounds forward to tick 1, already occupied.
        counter.observe(NS // 2, NS // 2, VALUES)
        result = counter.report(3 * NS)["all_keys"]
        # [0, 3 s) owns three ticks; the distinct stamps occupy only 0 and 1.
        self.assertEqual(result["expected_samples"], 3)
        self.assertEqual(result["valid_samples"], 2)
        self.assertEqual(result["sample_fraction"], 2 / 3)
        # A call exceeding the one-second period must not fill the empty cell.
        counter.observe(2 * NS, 3 * NS + 1, VALUES)
        self.assertEqual(counter.report(3 * NS)["all_keys"]["valid_samples"], 2)

        tie = thermal.Coverage(0, ["TDIE"], tolerance_ns=NS // 2)
        tie.observe(0, 0, {"sensors": {}, "errors": {}})  # Establish grid only.
        tie.observe(NS // 2, NS // 2, VALUES)
        # The half-period tie belongs to tick 1: outside [0, 1 s),
        # inside [0, 2 s), and counted exactly once.
        self.assertEqual(tie.report(NS)["all_keys"]["valid_samples"], 0)
        self.assertEqual(tie.report(2 * NS)["all_keys"]["valid_samples"], 1)

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
