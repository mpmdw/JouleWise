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
            'not floating after an old charge (basis b)': series((NOW-3000, True, 97), (NOW-2900, False, 100),
                                                                 (NOW-2800, False, 95),
                                                                 *[(NOW-2700+100*i, False, 100) for i in range(28)]),
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

    def test_basis_a_has_no_continuity_requirement_but_needs_a_fresh_floating_latest_row(self):
        # delta2 S2 M3: completion 1200 s ago, then a sampling gap and a current float row.
        rows = series((NOW-1300, True, 97), (NOW-1200, False, 100), (NOW-100, False, 100))
        result = topup.derive(rows, NOW)
        self.assertTrue(result['admissible'], result['reasons'])
        self.assertEqual((result['basis'], result['completed_at_epoch_s']), ('completed_charge', NOW-1200))
        self.assertFalse(topup.derive(series((NOW-1300, True, 97), (NOW-1200, False, 100), (NOW-400, False, 100)), NOW)['admissible'])
        self.assertFalse(topup.derive(series((NOW-1300, True, 97), (NOW-1200, False, 100), (NOW-100, True, 97)), NOW)['admissible'])
        self.assertFalse(topup.derive(series((NOW-1300, True, 97), (NOW-1200, False, 100), (NOW-100, False, 95)), NOW)['admissible'])
        # the 1800 s bound itself is not extended: 1801 s needs basis (b)'s continuity
        old = series((NOW-1901, True, 97), (NOW-1801, False, 100), (NOW-100, False, 100))
        self.assertFalse(topup.derive(old, NOW)['admissible'])

    def test_filtering_can_never_manufacture_a_completed_charge_transition(self):
        # delta2 S1 F03: an off-AC row or a probe error between charging and float is not removed.
        reconnect = [obs(NOW-2000, charging=True, pct=97), obs(NOW-1900, ac=False)]
        reconnect += [obs(NOW-1700+100*i) for i in range(18)]
        self.assertFalse(topup.derive(reconnect, NOW)['admissible'])
        errored = [obs(NOW-300, charging=True, pct=97), obs(NOW-200, error=True), obs(NOW-100), obs(NOW)]
        self.assertFalse(topup.derive(errored, NOW)['admissible'])
        # consecutive valid rows do establish it, and a later real charge can supersede an old poison
        later = errored + [obs(NOW+100, charging=True, pct=97), obs(NOW+200)]
        self.assertTrue(topup.derive(later, NOW+200)['admissible'])

    def test_untimed_or_invalid_rows_break_float_continuity_rather_than_disappearing(self):
        base = [obs(NOW-3000, charging=True, pct=97)] + [obs(NOW-2900+100*i) for i in range(30)]
        self.assertTrue(topup.derive(base, NOW)['admissible'])
        for bad in ({'schema': topup.SCHEMA, 'probe_error': True, 'wall_time_s': None},
                    {'schema': topup.SCHEMA, 'probe_error': False, 'wall_time_s': None, 'external_connected': True,
                     'is_charging': False, 'current_capacity_pct': 100},
                    obs(NOW-1850, error=True), obs(NOW-1850, ac=False), 'not an object'):
            rows = list(base)
            rows.insert(12, bad)
            with self.subTest(bad=str(bad)[:40]):
                self.assertFalse(topup.derive(rows, NOW)['admissible'])

    def test_a_continuous_sampler_leaves_back_to_back_arms_unstranded(self):
        # One completed charge, then a sampler running through an 11 h window and the turnaround.
        rows = [obs(NOW-45000, charging=True, pct=97)] + [obs(NOW-44900+120*i) for i in range(375)]
        result = topup.derive(rows, rows[-1]['wall_time_s']+60)
        self.assertTrue(result['admissible'], result['reasons'])
        self.assertEqual(result['basis'], 'continuous_float')
        # the same battery sampled only between windows (a 10 h hole) is the stranded case
        stranded = rows[:20] + rows[300:]
        self.assertFalse(topup.derive(stranded, rows[-1]['wall_time_s']+60)['admissible'])

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


def journal_row(t, *, smc_ma=None, ioreg=None, error=None, kind='reading'):
    """A hazard battery journal row (joulewise.hazard_journal.v1): an SMC 1 Hz line or an ioreg line."""
    stamp = {'wall_ns': int(t*1e9), 'monotonic_ns': int(t*1e9), 'monotonic_raw_ns': int(t*1e9)}
    if ioreg is not None:
        values = {'returncode': 0, **ioreg}
    elif smc_ma is not None:
        values = {'source': 'smc', 'smc': {'values': {'B0AC': smc_ma, 'B0AV': 12000}, 'errors': {}, 'finished': stamp}}
    else:
        values = {'source': 'smc', 'smc': {'values': {'B0AC': None}, 'errors': {'B0AC': 'unreadable'}, 'finished': stamp}}
    return {'schema': topup.JOURNAL_SCHEMA, 'module': 'battery', 'session': 's', 'seq': 1, 'kind': kind,
            'started': stamp, 'finished': stamp, 'values': values, 'error': error, 'raw': []}


def ioreg_values(pct=100, charging=False, ac=True):
    return {'external_connected': ac, 'is_charging': charging, 'current_capacity_pct': pct, 'instant_amperage_ma': 0}


def window_journal(start, end, *, step=1, ioreg_every=60, smc_ma=0, drop=()):
    rows = [journal_row(start-1, kind='session_start')] if False else []
    t = start
    while t <= end:
        if t not in drop:
            rows.append(journal_row(t, ioreg=ioreg_values()) if (t-start) % ioreg_every == 0
                        else journal_row(t, smc_ma=smc_ma))
        t += step
    return rows


class WindowJournalTests(unittest.TestCase):
    """Lead ruling: no sampler in a window; the window's own 1 Hz SMC capture carries float evidence."""

    def log(self, start, end, *, charge_at=None, step=100):
        rows, t = [], start
        while t <= end:
            charging = charge_at is not None and t < charge_at
            rows.append(obs(t, charging=charging, pct=97 if charging else 100))
            t += step
        return rows

    def test_window_records_convert_ioreg_and_smc_lines_into_observations(self):
        rows = [journal_row(100, kind='session_start'), journal_row(101, ioreg=ioreg_values()),
                journal_row(102, smc_ma=0), journal_row(103, smc_ma=450), journal_row(104, smc_ma=-865)]
        records = topup.window_records(rows)
        self.assertEqual(len(records), 4)                          # the session_start line carries no observation
        self.assertEqual([r['is_charging'] for r in records], [False, False, True, False])
        self.assertTrue(all(r['current_capacity_pct'] == 100 and r['external_connected'] for r in records))
        self.assertTrue(all(topup._valid(r) for r in records))

    def test_unusable_journal_lines_become_invalid_rows_not_missing_ones(self):
        rows = [journal_row(100, smc_ma=0),                         # no ioreg state yet
                journal_row(101, ioreg=ioreg_values()), journal_row(102),                  # B0AC error
                journal_row(103, ioreg=ioreg_values(), error='ioreg timed out'),
                {'schema': 'wrong'}, journal_row(104, smc_ma=0)]
        records = topup.window_records(rows)
        self.assertEqual(len(records), 6)
        self.assertEqual([topup._valid(r) for r in records], [False, True, False, False, False, True])

    def test_window_smc_journal_plus_between_window_logs_give_continuous_float(self):
        # completed charge long before; between-window log (sampler) before and after; the window in the middle.
        window_start, window_end = int(NOW)-40000, int(NOW)-2000
        before = self.log(window_start-1500, window_start-100, charge_at=window_start-1300)         # a charge completes here
        after = self.log(window_end+100, NOW)
        journal = window_journal(window_start, window_end)
        with tempfile.TemporaryDirectory() as tmp:
            paths = []
            for name, rows in (('before', before), ('after', after)):
                path = Path(tmp)/f'{name}.jsonl'
                path.write_text(''.join(json.dumps(r) + '\n' for r in rows))
                paths.append(path)
            jpath = Path(tmp)/'window-battery.jsonl'
            jpath.write_text(''.join(json.dumps(r) + '\n' for r in journal))
            result = topup.derive_from_sources(paths, [jpath], NOW)
            self.assertTrue(result['admissible'], result['reasons'])
            self.assertEqual(result['basis'], 'continuous_float')
            self.assertEqual(result['sources']['window_journals'], 1)
            # without the window journal the 11 h hole breaks continuity
            missing = topup.derive_from_sources(paths, [], NOW)
            self.assertFalse(missing['admissible'])
            self.assertIn('gap above', missing['reasons'][0])

    def test_a_missing_window_journal_or_a_boundary_gap_breaks_continuity(self):
        window_start, window_end = int(NOW)-5000, int(NOW)-2000
        before = self.log(window_start-1500, window_start-100, charge_at=window_start-1300)
        after = self.log(window_end+100, NOW)
        merged = topup.merge_in_time_order(before, topup.window_records(window_journal(window_start, window_end)), after)
        self.assertTrue(topup.derive(merged, NOW)['admissible'])
        # a boundary gap just over 300 s at the window start
        late = window_journal(window_start+250, window_end)
        gap = topup.merge_in_time_order(before, topup.window_records(late), after)
        self.assertFalse(topup.derive(gap, NOW)['admissible'])
        # exactly 300 s still holds
        edge = window_journal(window_start-100+300, window_end)
        self.assertTrue(topup.derive(topup.merge_in_time_order(before, topup.window_records(edge), after), NOW)['admissible'])
        # a hole in the middle of the journal (SMC capture lost for 2 minutes)
        hole = window_journal(window_start, window_end, drop=set(range(window_start+1000, window_start+1400)))
        self.assertFalse(topup.derive(topup.merge_in_time_order(before, topup.window_records(hole), after), NOW)['admissible'])

    def test_off_ac_or_low_soc_inside_the_window_breaks_float_and_a_charge_there_is_a_new_event(self):
        window_start, window_end = int(NOW)-5000, int(NOW)-2000
        before = self.log(window_start-1500, window_start-100, charge_at=window_start-1300)
        after = self.log(window_end+100, NOW)

        def with_row(bad):
            rows = window_journal(window_start, window_end)
            return [bad if r['finished']['wall_ns'] == int((window_start+1000)*1e9) else r for r in rows]
        for bad in (journal_row(window_start+1000, ioreg=ioreg_values(ac=False)),       # unplugged
                    journal_row(window_start+1000, ioreg=ioreg_values(pct=95))):        # SoC below the float bar
            with self.subTest(bad=str(bad['values'])[:50]):
                merged = topup.merge_in_time_order(before, topup.window_records(with_row(bad)), after)
                self.assertFalse(topup.derive(merged, NOW)['admissible'])
        # charging current (B0AC above 200 mA) is not floating; a charge that then completes is the new event
        merged = topup.merge_in_time_order(before, topup.window_records(
            with_row(journal_row(window_start+1000, smc_ma=500))), after)
        result = topup.derive(merged, NOW)
        self.assertTrue(result['admissible'], result['reasons'])
        self.assertEqual(result['completed_charge_epoch_s'], window_start+1001)

    def test_merge_keeps_an_untimed_row_after_its_predecessor(self):
        a = [obs(10), obs(20), {'schema': topup.SCHEMA, 'probe_error': True, 'wall_time_s': None}, obs(30)]
        b = [obs(25)]
        merged = topup.merge_in_time_order(a, b)
        self.assertEqual([r.get('wall_time_s') for r in merged], [10, 20, None, 25, 30])


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

    def test_loop_mode_samples_on_an_interval_until_stopped(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / 'battery.jsonl'
            import time
            moment = time.time()
            runner = lambda argv: subprocess.CompletedProcess(argv, 0, self.IOREG % int(moment), b'')
            slept = []
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(battery_log.main(['sample', '--log', str(log), '--loop', '--interval-s', '90',
                                                   '--max-samples', '4'], runner=runner, sleep=slept.append), 0)
            self.assertEqual(len(log.read_text().splitlines()), 4)
            self.assertEqual(slept, [90.0, 90.0, 90.0])

    def test_pidfile_and_stop_wire_the_between_window_sampler(self):
        with tempfile.TemporaryDirectory() as tmp:
            log, pidfile = Path(tmp) / 'battery.jsonl', Path(tmp) / 'sampler.pid'
            import time
            moment = time.time()
            runner = lambda argv: subprocess.CompletedProcess(argv, 0, self.IOREG % int(moment), b'')
            seen = []

            def sleeper(seconds):
                seen.append(pidfile.read_text().strip())               # the pidfile exists while looping
            with contextlib.redirect_stdout(io.StringIO()):
                battery_log.main(['sample', '--log', str(log), '--loop', '--interval-s', '1', '--max-samples', '2',
                                  '--pidfile', str(pidfile)], runner=runner, sleep=sleeper)
            self.assertEqual(len(seen), 1)
            self.assertTrue(seen[0].isdigit())
            self.assertFalse(pidfile.exists())                         # removed when the loop ends
            pidfile.write_text('4242\n')
            killed = []
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(battery_log.main(['stop', '--pidfile', str(pidfile)], kill=lambda pid, sig: killed.append((pid, sig))), 0)
            import signal
            self.assertEqual(killed, [(4242, signal.SIGTERM)])
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(battery_log.main(['stop', '--pidfile', str(Path(tmp) / 'absent.pid')]), 1)

    def test_derive_accepts_logs_and_window_journals(self):
        with tempfile.TemporaryDirectory() as tmp:
            log, journal = Path(tmp) / 'l.jsonl', Path(tmp) / 'j.jsonl'
            log.write_text(''.join(json.dumps(r) + '\n' for r in [obs(NOW-1000, charging=True, pct=97), obs(NOW-900), obs(NOW-800)]))
            journal.write_text(''.join(json.dumps(r) + '\n' for r in window_journal(NOW-700, NOW-100)))
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                code = battery_log.main(['derive', '--log', str(log), '--window-journal', str(journal)], now=lambda: NOW)
            self.assertEqual(code, 0, buffer.getvalue())
            self.assertEqual(json.loads(buffer.getvalue())['basis'], 'completed_charge')

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
