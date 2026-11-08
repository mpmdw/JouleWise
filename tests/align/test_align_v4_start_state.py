"""Synthetic tests for scripts/align_v4_start_state.py (CONDITION-WAITS-opus.md P1/P3).

All journals are generated here from closed-form cooling curves; no record,
custody or measured value is read.
"""
from __future__ import annotations

import io
import json
import math
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from scripts import align_v4_start_state as sse

NS = 1_000_000_000
TAU = 470.0        # shared slow mode after fans stop (LEAD-RULINGS-2 Round 7: 430-510 s)
FANS_OFF = 180.0   # fans stop about 180 s after load end (same source)


def curve(t, ambient, rise, tau=TAU):
    return ambient + rise * math.exp(-max(0.0, t - FANS_OFF) / tau)


def journal(seconds, *, ambient=30.0, rise_slow=12.0, rise_fast=20.0, start=1000.0, spike=None,
            charging_until=None, missing=(), power=0.4, fan_rpm=None, status=True):
    rows = []
    for i in range(int(seconds)):
        t = start + i
        slow = curve(i, ambient, rise_slow)
        fast = curve(i, ambient + 2.0, rise_fast, tau=TAU * 0.8)
        if spike and spike[0] <= i < spike[1]:
            slow += 3.0
            fast += 5.0
        sensors = {'TV0h': None if i in missing else fast, 'Tf08': None if i in missing else slow,
                   'F0Ac': fan_rpm(i) if fan_rpm else (2000.0 if i < FANS_OFF else 0.0)}
        row = {'monotonic_ns': int(t * NS), 'sensors': sensors,
               'status': {'os_level': 0, 'pm_state': 'Nominal'} if status else {},
               'power_w': power,
               'battery': {'is_charging': bool(charging_until and i < charging_until),
                           'instant_amperage_ma': 1500 if charging_until and i < charging_until else 0}}
        rows.append(row)
    return rows


def policy(**overrides):
    base = dict(s_fast='TV0h', s_slow='Tf08', ref_fast_c=32.0, ref_slow_c=30.0, delta_fast_c=1.0,
                delta_slow_c=1.0, fan_keys=('F0Ac',), fan_idle_rpm=100.0)
    base.update(overrides)
    return sse.Policy.from_mapping(base)


class StartStateTests(unittest.TestCase):
    def test_release_follows_level_and_slope_plus_stability(self):
        result = sse.start_state(journal(4000), policy(), terminal_t_s=1000.0)
        self.assertEqual(result['outcome'], 'released')
        # Level: 12 e^{-t/tau} <= 1 -> t = FANS_OFF + tau ln 12 = 1,348 s; slope 0.1 C/min with a
        # 300 s OLS lag lands later; release adds the 300 s stability interval.
        level_t = FANS_OFF + TAU * math.log(12.0)
        self.assertGreaterEqual(result['release_after_terminal_s'], level_t + 300)
        self.assertLess(result['release_after_terminal_s'], level_t + 300 + 900)
        self.assertLessEqual(result['first_pass_s']['level'], level_t + 60)

    def test_looser_slope_never_releases_later(self):
        tight = sse.start_state(journal(4000), policy(slope_max_c_per_min=0.1), terminal_t_s=1000.0)
        loose = sse.start_state(journal(4000), policy(slope_max_c_per_min=0.2), terminal_t_s=1000.0)
        self.assertLessEqual(loose['release_after_terminal_s'], tight['release_after_terminal_s'])

    def test_floor_holds_an_already_cool_machine(self):
        result = sse.start_state(journal(3000, rise_slow=0.0, rise_fast=0.0), policy(),
                                 terminal_t_s=1000.0)
        self.assertEqual(result['outcome'], 'released')
        self.assertEqual(result['release_after_terminal_s'], 600.0)

    def test_stability_interval_starts_after_quiet(self):
        result = sse.start_state(journal(4000, rise_slow=0.0, rise_fast=0.0), policy(),
                                 terminal_t_s=1000.0, quiet_from_t_s=2000.0)
        self.assertEqual(result['release_after_quiet_s'], 300.0)

    def test_spike_resets_the_stability_run(self):
        calm = sse.start_state(journal(4000, rise_slow=0.0, rise_fast=0.0), policy(), terminal_t_s=1000.0)
        spiked = sse.start_state(journal(4000, rise_slow=0.0, rise_fast=0.0, spike=(500, 520)), policy(),
                                 terminal_t_s=1000.0)
        self.assertGreater(spiked['release_after_terminal_s'], calm['release_after_terminal_s'])

    def test_charging_blocks_release_until_it_stops(self):
        result = sse.start_state(journal(4000, rise_slow=0.0, rise_fast=0.0, charging_until=1500), policy(),
                                 terminal_t_s=1000.0)
        self.assertGreaterEqual(result['release_after_terminal_s'], 1500 + 300)

    def test_power_p95_above_bar_blocks_release(self):
        result = sse.start_state(journal(3000, rise_slow=0.0, rise_fast=0.0, power=2.5), policy(),
                                 terminal_t_s=1000.0)
        self.assertEqual(result['outcome'], 'ceiling_unsettled')

    def test_warm_ambient_ends_at_ceiling_level_with_offset(self):
        result = sse.start_state(journal(4000, ambient=32.0), policy(), terminal_t_s=1000.0)
        self.assertEqual(result['outcome'], 'ceiling_level')
        self.assertEqual(result['release_after_terminal_s'], 2700.0)
        self.assertAlmostEqual(result['slow_offset_above_band_c'], 1.0, delta=0.1)

    def test_large_offset_is_held_for_the_lead(self):
        result = sse.start_state(journal(4000, ambient=35.0), policy(), terminal_t_s=1000.0)
        self.assertEqual(result['outcome'], 'hold_level_offset')

    def test_spinning_fans_are_unsettled_not_level(self):
        result = sse.start_state(journal(4000, fan_rpm=lambda i: 1200.0), policy(), terminal_t_s=1000.0)
        self.assertEqual(result['outcome'], 'ceiling_unsettled')

    def test_missing_reads_are_unobserved(self):
        result = sse.start_state(journal(4000, missing=set(range(0, 4000, 2))), policy(), terminal_t_s=1000.0)
        self.assertEqual(result['outcome'], 'unobserved')

    def test_missing_status_does_not_release(self):
        result = sse.start_state(journal(4000, rise_slow=0.0, rise_fast=0.0, status=False), policy(),
                                 terminal_t_s=1000.0)
        self.assertEqual(result['outcome'], 'ceiling_unsettled')

    def test_raw_sidecar_rows_are_projected(self):
        rows = [{'module': 'temperature', 'kind': 'reading', 'started': {'monotonic_ns': r['monotonic_ns']},
                 'values': {'sensors': r['sensors'], 'status': r['status']}} for r in journal(3000, rise_slow=0.0,
                                                                                         rise_fast=0.0)]
        result = sse.start_state(rows, policy(power_p95_max_w=None), terminal_t_s=1000.0)
        self.assertEqual(result['outcome'], 'released')

    def test_policy_refuses_unknown_and_nonfinite_fields(self):
        with self.assertRaises(ValueError):
            policy(bogus=1)
        with self.assertRaises(ValueError):
            policy(ref_slow_c=float('nan'))
        with self.assertRaises(ValueError):
            policy(floor_s=900.0, ceiling_s=600.0)


class IdleShadowTests(unittest.TestCase):
    def kwargs(self, **overrides):
        base = dict(s_fast='TV0h', s_slow='Tf08', ref_fast_c=32.0, ref_slow_c=30.0, delta_fast_c=1.0,
                    delta_slow_c=1.0)
        base.update(overrides)
        return base

    def test_cool_member_holds_after_slope_window_and_ten_samples(self):
        rows = journal(400, rise_slow=0.0, rise_fast=0.0)
        first = sse.idle_shadow(rows, idle_start_t_s=1000.0, idle_end_t_s=1300.0, **self.kwargs())
        self.assertIsNotNone(first)
        self.assertLessEqual(first, 70.0)

    def test_hot_predecessor_never_holds_within_300_s(self):
        rows = journal(400, rise_slow=12.0)
        self.assertIsNone(sse.idle_shadow(rows, idle_start_t_s=1000.0, idle_end_t_s=1300.0, **self.kwargs()))

    def test_mid_cooling_member_holds_inside_idle(self):
        rows = journal(2500)
        first = sse.idle_shadow(rows, idle_start_t_s=2400.0, idle_end_t_s=2700.0, **self.kwargs())
        self.assertIsNotNone(first)


class CliTests(unittest.TestCase):
    def test_start_state_cli_with_grid(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'j.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in journal(4000)))
            (root / 'p.json').write_text(json.dumps(dict(
                s_fast='TV0h', s_slow='Tf08', ref_fast_c=32.0, ref_slow_c=30.0, delta_fast_c=1.0,
                delta_slow_c=1.0, fan_keys=['F0Ac'], fan_idle_rpm=100.0)))
            (root / 's.json').write_text(json.dumps([{'member': 'm1', 'idle_start_t_s': 4000.0,
                                                      'idle_end_t_s': 4300.0}]))
            out = io.StringIO()
            with redirect_stdout(out):
                code = sse.main(['start-state', '--journal', str(root / 'j.jsonl'), '--policy',
                                 str(root / 'p.json'), '--terminal-t-s', '1000', '--grid'])
            self.assertEqual(code, 0)
            result = json.loads(out.getvalue())
            self.assertEqual(result['outcome'], 'released')
            self.assertEqual(len(result['grid']), 6)
            out = io.StringIO()
            with redirect_stdout(out):
                sse.main(['idle-shadow', '--journal', str(root / 'j.jsonl'), '--policy', str(root / 'p.json'),
                          '--spans', str(root / 's.json')])
            shadow = json.loads(out.getvalue())['idle_shadow'][0]
            self.assertEqual(shadow['configured_idle_s'], 300.0)
            self.assertIsNotNone(shadow['g0_predicate_first_hold_s'])


if __name__ == '__main__':
    unittest.main()
