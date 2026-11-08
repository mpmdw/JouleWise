"""MED-3: top-up evidence is derived from a logged battery record, never typed. Synthetic only."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from joulewise.align.apple import v4_topup as topup
from scripts import align_v4_battery_log as battery_log

NOW = 100000.0


def obs(t, *, charging=False, pct=100, ac=True, error=False):
    return {'schema': topup.SCHEMA, 'probe_error': error, 'wall_time_s': t, 'external_connected': ac,
            'is_charging': charging, 'current_capacity_pct': pct}


def series(*specs):
    return [obs(t, charging=c, pct=p) for t, c, p in specs]


class DeriveTests(unittest.TestCase):
    def test_a_completed_charge_within_1800_s_is_admissible_as_basis_a(self):
        log = series((NOW-1000, True, 97), (NOW-900, False, 100), (NOW-800, False, 100), (NOW-100, False, 100))
        # gaps above 300 s between the second and last observation would refuse; keep it dense
        log = series(*[(NOW-1000+100*i, i < 1, 97 if i < 1 else 100) for i in range(11)])
        result = topup.derive(log, NOW, log_sha256='f' * 64)
        self.assertTrue(result['admissible'], result['reasons'])
        self.assertEqual(result['basis'], 'completed_charge')
        self.assertEqual(result['completed_at_epoch_s'], NOW-900)
        self.assertTrue(result['source'].startswith('battery_log:completed_charge:ffffffff'))

    def test_continuous_float_since_the_last_charge_is_basis_b_with_the_latest_observation_time(self):
        log = series(*[(NOW-3000+100*i, i < 1, 97 if i < 1 else 100) for i in range(30)])   # last at NOW-100
        result = topup.derive(log, NOW)
        self.assertTrue(result['admissible'], result['reasons'])
        self.assertEqual(result['basis'], 'continuous_float')
        self.assertEqual(result['completed_at_epoch_s'], NOW-100)          # the latest qualifying observation
        self.assertEqual(result['completed_charge_epoch_s'], NOW-2900)

    def test_inadmissible_logs_and_hand_entered_nows(self):
        dense = lambda start, n, **kw: [obs(start+100*i, **kw) for i in range(n)]
        charging_then_float = lambda: series((NOW-3000, True, 97), *[(NOW-2900+100*i, False, 100) for i in range(29)])
        cases = {
            'empty': [],
            'no completed charge': dense(NOW-2000, 20),
            'still charging': series(*[(NOW-1000+100*i, True, 97) for i in range(10)]),
            'not floating after the charge': series((NOW-1000, True, 97), (NOW-900, False, 100), (NOW-800, False, 95),
                                                    *[(NOW-700+100*i, False, 100) for i in range(7)]),
            'gap since the charge': series((NOW-3000, True, 97), (NOW-2900, False, 100), (NOW-2000, False, 100),
                                           *[(NOW-1900+100*i, False, 100) for i in range(19)]),
            'stale latest': series((NOW-3000, True, 97), *[(NOW-2900+100*i, False, 100) for i in range(20)]),
            'off AC after the charge': charging_then_float()[:10] + [obs(NOW-1900, ac=False)] + charging_then_float()[11:],
            'probe errors only': [obs(NOW-100*i, error=True) for i in range(5)],
            'out of order': series((NOW-300, True, 97), (NOW-400, False, 100)),
        }
        for name, log in cases.items():
            with self.subTest(name=name):
                result = topup.derive(log, NOW)
                self.assertFalse(result['admissible'], result)
        self.assertFalse(topup.derive(cases['empty'], float('nan'))['admissible'])
        future = series((NOW-100, True, 97), (NOW+50, False, 100))
        self.assertFalse(topup.derive(future, NOW)['admissible'])

    def test_the_arm_clock_decides_not_the_log(self):
        log = series(*[(NOW-3000+100*i, i < 1, 97 if i < 1 else 100) for i in range(30)])
        self.assertTrue(topup.derive(log, NOW)['admissible'])
        self.assertFalse(topup.derive(log, NOW+1000)['admissible'])       # later arm: latest observation stale

    def test_file_loader_hashes_bytes_and_refuses_unparseable_logs(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'log.jsonl'
            path.write_text(''.join(json.dumps(r) + '\n' for r in series(*[(NOW-1000+100*i, i < 1, 97 if i < 1 else 100)
                                                                         for i in range(11)])))
            result = topup.derive_from_file(path, NOW)
            self.assertTrue(result['admissible'])
            import hashlib
            self.assertEqual(result['log_sha256'], hashlib.sha256(path.read_bytes()).hexdigest())
            path.write_text('not json\n')
            self.assertFalse(topup.derive_from_file(path, NOW)['admissible'])
            self.assertFalse(topup.derive_from_file(Path(tmp) / 'absent', NOW)['admissible'])


class LogScriptTests(unittest.TestCase):
    IOREG = b'''+-o AppleSmartBattery  <class AppleSmartBattery>
  {
    "ExternalConnected" = Yes
    "IsCharging" = No
    "InstantAmperage" = 0
    "UpdateTime" = %d
    "CurrentCapacity" = 100
  }
'''

    def test_sample_appends_observe_records_and_derive_reads_them(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / 'battery.jsonl'
            import time
            moment = time.time()
            runner = lambda argv: subprocess.CompletedProcess(argv, 0, self.IOREG % int(moment), b'')
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(battery_log.main(['sample', '--log', str(log)], runner=runner), 0)
                self.assertEqual(battery_log.main(['sample', '--log', str(log)], runner=runner), 0)
            rows = [json.loads(line) for line in log.read_text().splitlines()]
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]['schema'], topup.SCHEMA)
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                code = battery_log.main(['derive', '--log', str(log)], now=lambda: moment+10)
            self.assertEqual(code, 1)                              # floating but no completed charge yet
            self.assertFalse(json.loads(buffer.getvalue())['admissible'])


if __name__ == '__main__':
    unittest.main()
