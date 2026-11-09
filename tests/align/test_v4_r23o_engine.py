"""A20 whole-member DC hull witnesses (lead ruling; synthetic bytes only)."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.v4_analysis import dc, raw
from joulewise.align.v4_analysis.io import canonical, digest, strict_json
from joulewise.b5.harvest import member_spans
from joulewise.external import km003c_parse as kp
from tests.align.test_attribution import episode, turn
from tests.align.test_v4_r23m_engine import stream

MS = 1_000_000


def bundle_inputs(start_ms, end_ms, *, baseline_ms=None, sentinel_ms=None):
    """metadata.json/events.jsonl shaped like production run bundles."""
    stamps = dict(pre_spawn=dict(monotonic_before_s=start_ms/1000), post_parse=dict(monotonic_after_s=end_ms/1000))
    metadata = dict(uncertainty_evidence=dict(clock_anchor=dict(clock_stamps=stamps)))
    events = []
    if baseline_ms is not None:
        events.append(dict(event_type='stage_started', phase='idle_baseline', metadata=dict(monotonic_ns=baseline_ms*MS)))
    if sentinel_ms is not None:
        events.append(dict(event_type='stage_completed', phase='idle_drift_sentinel',
                           metadata=dict(monotonic_ns=sentinel_ms*MS)))
    return metadata, events


class HullCaptureTests(unittest.TestCase):
    def ep(self):
        return episode(turns=(turn(start=300*MS, first=325*MS, end=500*MS),), start_ns=300*MS, end_ns=600*MS)

    def test_hull_longer_than_episode_integrates_over_the_hull(self):
        meter = stream(list(range(0, 1001, 100)), [10.]*11)
        metadata, events = bundle_inputs(100, 800, baseline_ms=50, sentinel_ms=900)
        hull = member_spans(metadata, events)['member']
        self.assertEqual(hull, [50*MS, 900*MS])
        result = dc.capture([('synthetic', meter)], self.ep(), hull)
        self.assertEqual(result['status'], 'available')
        self.assertAlmostEqual(result['whole_member_j'], 10.*0.85)     # hull, not the 0.3 s episode
        self.assertAlmostEqual(result['turn_owned_j'], 10.*0.2)       # turn-owned unchanged
        episode_only = dc.capture([('synthetic', meter)], self.ep(), [300*MS, 600*MS])
        self.assertAlmostEqual(episode_only['whole_member_j'], 3.)
        self.assertEqual(episode_only['turn_owned_j'], result['turn_owned_j'])

    def test_hull_rules_hold_drop_and_coverage_null_the_whole_value(self):
        cases = {
            # a 400 ms hold inside the hull but outside owned time
            'long hold in hull': ([0, 100, 200, 300, 400, 500, 600, 1000], [50*MS, 900*MS]),
            'hull past stream end': (list(range(0, 1001, 100)), [50*MS, 1100*MS]),
        }
        for label, (times, hull) in cases.items():
            with self.subTest(case=label):
                result = dc.capture([('synthetic', stream(times, [10.]*len(times)))], self.ep(), hull)
                self.assertIsNone(result['whole_member_j'])
                self.assertIn('meter.member_uncovered_or_gap', result['flags'])
                self.assertAlmostEqual(result['turn_owned_j'], 2.)       # owned time stays covered

    def test_missing_hull_is_missing_dc(self):
        metadata, events = bundle_inputs(100, 800)
        metadata['uncertainty_evidence']['clock_anchor']['clock_stamps'] = {}
        hull = member_spans(metadata, events)['member']
        self.assertIsNone(hull)
        result = dc.capture([('synthetic', stream([0, 100], [1., 1.]))], self.ep(), hull)
        self.assertEqual((result['status'], result['flags']), ('missing', ['meter.member_span_missing']))


class RawHullDerivationTests(unittest.TestCase):
    def setUp(self):
        from scripts.benchmark_v4_r21 import fixture
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)/'raw'
        path, _ = fixture(self.root, 64, windows=1)
        window = strict_json(path.read_bytes())['windows'][0]
        self.slot = window['roster'][5]
        self.source = strict_json((self.root/window['raw_source']['path']).read_bytes())['members'][5]
        self.assertEqual(self.slot['condition'], 'benign')

    def write(self, name, data):
        (self.root/name).write_bytes(data)
        return dict(path=name, sha256=digest(data))

    def test_engine_derives_the_hull_from_bundle_metadata_and_events(self):
        metadata, events = bundle_inputs(1, 999_999_999, baseline_ms=0, sentinel_ms=1_000_000_000)
        source = dict(self.source, dc_streams=[self.write('meter.jsonl', b'synthetic')],
                      metadata=self.write('metadata.json', canonical(metadata)),
                      events=self.write('events.jsonl', b'\n'.join(canonical(e) for e in events)+b'\n'))
        meter = stream([0, 100], [1., 1.])
        with patch.object(kp, 'parse_bytes', return_value=meter):
            member = raw.member(self.root, self.slot, source)
        self.assertEqual(member['dc_evidence']['member_span_ns'], member_spans(metadata, events)['member'])
        self.assertEqual(member['dc_evidence']['member_span_ns'], [0, 1_000_000_000*MS])
        self.assertEqual(member['dc_sources'], [source['metadata'], source['events']])

    def test_exported_span_or_missing_bundle_inputs_refuse(self):
        meter_ref = self.write('meter.jsonl', b'synthetic')
        for label, extra in (('exported span', dict(member_span_ns=[0, 1])),
                             ('no metadata/events', {})):
            with self.subTest(case=label), patch.object(kp, 'parse_bytes', side_effect=AssertionError('parsed')):
                source = dict(self.source, dc_streams=[meter_ref], **extra)
                with self.assertRaises(ValueError):
                    raw.member(self.root, self.slot, source)


if __name__ == '__main__':
    unittest.main()
