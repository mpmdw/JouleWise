"""Scoped parser reuse: same bytes/anchors, independent returned records."""
from pathlib import Path
import unittest
from unittest.mock import patch

from joulewise.adapters import powermetrics as pm

SEED = Path(__file__).parent/'fixtures/d117_v2_production/strict_seed_bundle/raw/powermetrics.plist'


class ParsedRecordsCacheTests(unittest.TestCase):
    def setUp(self):
        self.raw = SEED.read_bytes().split(b'\0')[0]+b'\0'

    def test_reuse_skips_xml_decode_and_returns_independent_records(self):
        with patch.object(pm.plistlib, 'loads', wraps=pm.plistlib.loads) as loads:
            with pm.reuse_parsed_records():
                first = pm.parse_powermetrics_records(self.raw)
                original = pm.parse_powermetrics_records(self.raw)
                self.assertEqual(loads.call_count, 1)
                first[0].metadata['changed'] = True
                first[0].rail_power_w['cpu_power'] = -1
                first.clear()
                self.assertEqual(pm.parse_powermetrics_records(self.raw), original)
            pm.parse_powermetrics_records(self.raw)
            self.assertEqual(loads.call_count, 2)

    def test_changed_bytes_and_anchor_have_distinct_keys(self):
        with patch.object(pm.plistlib, 'loads', wraps=pm.plistlib.loads) as loads:
            with pm.reuse_parsed_records():
                base = pm.parse_powermetrics_records(self.raw)
                changed = pm.parse_powermetrics_records(self.raw+b'\0')
                anchored = pm.parse_powermetrics_records(self.raw, timestamp_anchor_s=10.)
                self.assertEqual(base, changed)
                self.assertNotEqual(base, anchored)
                self.assertEqual(loads.call_count, 3)

    def test_small_cap_and_exception_do_not_leave_stale_cache(self):
        with patch.object(pm.plistlib, 'loads', wraps=pm.plistlib.loads) as loads:
            with pm.reuse_parsed_records(max_bytes=1):
                pm.parse_powermetrics_records(self.raw)
                pm.parse_powermetrics_records(self.raw)
                self.assertEqual(loads.call_count, 2)
            with self.assertRaises(ValueError), pm.reuse_parsed_records():
                pm.parse_powermetrics_records(b'bad')
            self.assertEqual(pm.parse_powermetrics_records(self.raw),
                             pm.parse_powermetrics_records(self.raw))

    def test_dropped_tail_and_diagnostic_bytes_equal(self):
        raw = self.raw+b'broken tail'
        original = pm._parse_powermetrics_records(raw)
        with pm.reuse_parsed_records():
            self.assertEqual(pm._parse_powermetrics_records(raw), original)
            self.assertEqual(pm._parse_powermetrics_records(raw), original)

    def test_invalid_bool_anchor_cannot_hit_numeric_anchor_cache(self):
        with pm.reuse_parsed_records():
            pm.parse_powermetrics_records(self.raw, first_record_endpoint_s=1.)
            with self.assertRaises(ValueError):
                pm.parse_powermetrics_records(self.raw, first_record_endpoint_s=True)


if __name__ == '__main__':
    unittest.main()
