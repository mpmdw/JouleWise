"""R22-1: in-window contention is disclosure-only in v4. Synthetic only."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.apple import v4_contention as contention
from joulewise.flags import catalog

NS = 10**9


def interval(a_s, b_s, rate, error=None):
    return {'interval': {'monotonic_ns': [int(a_s*NS), int(b_s*NS)]}, 'outside_total_cpu_s_per_s': rate,
            'error': error, 'raw': []}


class CodeTests(unittest.TestCase):
    def test_no_contention_code_can_exclude_a_member(self):
        shared = [c for c in vars(catalog).get('_EXCLUDE_CODES', {}) if c.startswith('contention.')]
        catalogued = [c for c in dir(catalog) if False]
        codes = {'contention.request_overlap', 'contention.unmeasured', 'contention.kernel_task_share',
                 'contention.some_future_code', *shared, *catalogued}
        for code in sorted(codes):
            with self.subTest(code=code):
                self.assertTrue(contention.is_disclosure_only(code))
                self.assertEqual(contention.split_codes([code]), ([], [code]))
                record = {'calibration_exclusions': [code], 'flags': []}
                contention.attach(record, Path('/nonexistent-bundle'), ([], None, 1))
                self.assertFalse(record['excluded'], 'a contention code excluded a member')
                self.assertEqual(record['calibration_exclusions'], [])
                self.assertIn(code, record['contention']['disclosed_codes'])
        kept, disclosed = contention.split_codes(['member.runtime_failure', 'contention.request_overlap', 'battery.assist'])
        self.assertEqual((kept, disclosed), (['member.runtime_failure', 'battery.assist'], ['contention.request_overlap']))
        record = {'calibration_exclusions': ['member.runtime_failure', 'contention.unmeasured']}
        contention.attach(record, Path('/nonexistent-bundle'), ([], None, 1))
        self.assertTrue(record['excluded'])                       # other exclusions are untouched
        self.assertEqual(record['calibration_exclusions'], ['member.runtime_failure'])

    def test_the_shared_catalog_contention_codes_are_all_disclosure_only_here(self):
        # the shared (Block 5) catalog excludes on two contention codes; v4 never does
        found = {code for code in catalog.CODES if code.startswith('contention.')} if hasattr(catalog, 'CODES') else set()
        found |= {'contention.request_overlap', 'contention.unmeasured'}
        for code in found:
            self.assertEqual(contention.split_codes([code])[0], [])


class DisclosureTests(unittest.TestCase):
    def test_outside_cpu_seconds_and_a_bounded_unmeasured_gap(self):
        # 0-100 s member span: covered 0-40, 45-50 and 60-100 at 0.02 CPU-s/s; holes of 5 s and 10 s
        intervals = [interval(t, t+10, 0.02) for t in (0, 10, 20, 30, 60, 70, 80, 90)]
        intervals.append(interval(40, 45, 0.0, error='ps failed'))          # an errored interval covers nothing
        intervals.append(interval(45, 50, 0.02))
        record = contention.disclose(intervals, [0, 100*NS])
        self.assertFalse(record['excludes'])
        self.assertAlmostEqual(record['outside_cpu_s'], 0.02*(40+5+40))
        self.assertEqual(record['unmeasured_gaps'], [[40*NS, 45*NS], [50*NS, 60*NS]])
        self.assertAlmostEqual(record['max_unmeasured_gap_s'], 10.0)
        self.assertEqual(record['flags'], [])                               # both holes are below 30 s

    def test_a_gap_over_30_s_is_flagged_and_disclosed_never_excluded(self):
        intervals = [interval(0, 10, 0.01), interval(50, 60, 0.01)]        # a 40 s hole
        record = contention.disclose(intervals, [0, 60*NS])
        self.assertAlmostEqual(record['max_unmeasured_gap_s'], 40.0)
        self.assertEqual(record['flags'], ['contention.unmeasured'])
        self.assertFalse(record['excludes'])
        exactly = contention.disclose([interval(0, 10, 0.01), interval(40, 50, 0.01)], [0, 50*NS])
        self.assertAlmostEqual(exactly['max_unmeasured_gap_s'], 30.0)
        self.assertEqual(exactly['flags'], [])                              # "over 30 s" is strict
        record_row = {'calibration_exclusions': []}
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)
            (bundle / 'metadata.json').write_text('{}')
            (bundle / 'events.jsonl').write_text('')
            with patch('joulewise.b5.harvest.member_spans', return_value={'member': [0, 60*NS], 'request': None}):
                contention.attach(record_row, bundle, (intervals, 'a'*64, 0))
        self.assertFalse(record_row['excluded'])
        self.assertEqual(record_row['contention']['status'], 'observed')
        self.assertEqual(record_row['contention']['disclosed_codes'], ['contention.unmeasured'])
        self.assertAlmostEqual(record_row['contention']['outside_cpu_s'], 0.2)

    def test_a_missing_journal_is_unavailable_and_still_never_excludes(self):
        row = {'calibration_exclusions': []}
        contention.attach(row, Path('/nonexistent-bundle'), ([], None, 1))
        self.assertEqual(row['contention']['status'], 'unavailable')
        self.assertFalse(row['excluded'])
        self.assertIsNone(row['contention']['outside_cpu_s'])

    def test_load_journal_reads_monitor_interval_lines(self):
        line = {'module': 'contention', 'kind': 'interval', 'started': {'monotonic_ns': 0},
                'finished': {'monotonic_ns': 10*NS}, 'values': {'outside_total_cpu_s_per_s': 0.03}, 'error': None, 'raw': []}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'contention.jsonl'
            path.write_text(json.dumps(line) + '\nnot json\n')
            intervals, sha, malformed = contention.load_journal(path)
        self.assertEqual(malformed, 1)
        self.assertEqual(len(sha), 64)
        record = contention.disclose(intervals, [0, 10*NS])
        self.assertAlmostEqual(record['outside_cpu_s'], 0.3)
        self.assertEqual(contention.load_journal(Path('/nonexistent/contention.jsonl'))[1:], (None, 1))


class EligibilityTests(unittest.TestCase):
    def test_a_contention_exclusion_code_never_removes_a_calibrator_from_the_counts(self):
        from tests.align.test_v4_next_arm_packet import Scenario
        from scripts import align_v4_next_arm_packet as builder
        counts = {}
        for label, codes in (('none', []), ('contention', ['contention.request_overlap', 'contention.unmeasured'])):
            with tempfile.TemporaryDirectory() as tmp:
                first = Scenario(tmp, 'W1').finish()
                s = Scenario(tmp, 'C1', previous=first)
                for member in s.members:
                    member['pool_role'] = 'calibration'
                if codes:
                    victim = s.members[0]['run_id']
                    s.sources['exclusions']['members_excluded'] = [{'run_id': victim, 'codes': codes}]
                    # the desk (which strips contention) does not exclude: excluded False, no exclusion codes
                s.finish()
                record = builder.WindowRecord(builder.GitEvidence(s.root), s.record_commit, s.record_path)
                counts[label] = record.eligibility()['eligible_benign']
        self.assertEqual(counts['none'], counts['contention'])
        self.assertEqual(sum(counts['contention'].values()), 2)


if __name__ == '__main__':
    unittest.main()
