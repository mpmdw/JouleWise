"""Validate collection-path flags through the production schema builder.

Hazard modules return internal findings; they do not write flags. The actual
continuous-monitor emitter is b5.harvest._Harvest.monitor_joins, whose
FlagLedger supplies the two unobserved clock domains as null.
"""
import tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest import mock

from joulewise.b5 import harvest as h
from joulewise.b6 import smoke
from joulewise.flags.schema import make_flag
from tests.test_harvest_b5_window import L1Journal, l1_stamp, battery_values, REGISTERED_HARVEST_THRESHOLDS


class CollectionEmitterTests(unittest.TestCase):
    def test_all_monitor_emitters_build_valid_flags(self):
        thresholds = REGISTERED_HARVEST_THRESHOLDS
        seen = set()
        # Exercise step overlap with a member, a capture and neither. These
        # are the three distinct window/member emitters in monitor_joins.
        for placement in ('member', 'capture', 'neither'):
            with self.subTest(placement=placement), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                for module in h.MONITOR_MODULES:
                    journal = L1Journal(module)
                    # 1 Hz is the production clock-journal sample interval.
                    for second in range(4):
                        ns = second * 10**9
                        values = {}
                        if module == 'battery':
                            values = battery_values(l1_stamp(ns)['wall_ns'] // 10**9,
                                instant_amperage_ma=int(thresholds['battery_limit_ma']) + 1)
                        elif module == 'thermal':
                            values = {'level': 1}
                        elif module == 'clock':
                            values = {'anchor': {'anchor_ns': 0 if second == 0 else 2 * thresholds['clock_step_ns'],
                                'monotonic_raw_ns': ns, 'read_skew_ns': 0},
                                'frequency': {'raw_word': 0 if second < 2 else 1}}
                        elif module == 'disk':
                            values = {'targets': [{'path': str(root), 'free_bytes': 0}]}
                        journal.write('snapshot' if module == 'contention' else 'reading', ns, values=values)
                    journal.dump(root / (module + '.jsonl'))
                harvest = h._Harvest.__new__(h._Harvest)
                harvest.inputs = SimpleNamespace(monitor_dir=root, thresholds=thresholds)
                harvest.hazards = {}
                harvest.roster = {'members': [{'run_id': 'run', 'stage_id': 'stage'}]}
                harvest.spans = {'run': {'member': [0, 3 * 10**9]}} if placement == 'member' else {}
                harvest.capture_assessments = {'pre': {'span': [0, 3 * 10**9]}} if placement == 'capture' else {}
                harvest.pair_missing = {}
                harvest.battery_assist = {'members': {}, 'captures': {}}
                harvest.withheld = root / 'withheld'
                harvest.flags = h.FlagLedger(plan_id='synthetic', attempt=1,
                    catalog=h.Catalog.load(smoke.CATALOG_PATH), boot_session_uuid='BOOT')
                harvest._pair_assist = mock.Mock()
                harvest._capture_battery_joins = mock.Mock()
                harvest._kernel_task_share = mock.Mock()
                harvest._record_error = mock.Mock(side_effect=AssertionError('monitor join failed'))
                harvest.monitor_joins()
                for flag in harvest.flags.records:
                    fields = {key: value for key, value in flag.items() if key not in ('schema_version', 'flag_id')}
                    self.assertEqual(make_flag(**fields), flag)
                    seen.add(flag['code'])
        self.assertTrue({'battery.member_span', 'thermal.os_level_nonzero', 'clock.frequency_changed',
                         'clock.step_overlap', 'clock.step_overlap_calibration', 'clock.step', 'disk.low'} <= seen, seen)
