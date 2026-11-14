"""RL-145 addendum row 6: the W1 desk's per-turn prints, on synthetic fixtures only."""
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

from joulewise.align.apple import rl145_prints as p

NS = 1_000_000_000


def turn(start=0, first=10, end=130, tokens=1200, index=0):
    return SimpleNamespace(index=index, start_ns=start * NS, first_token_ns=first * NS, end_ns=end * NS,
                           decode_tokens=tokens)


def pm(seconds, clock=lambda t: 1000.0, state=lambda t: 'Nominal'):
    """One-second PM rows ending at 1..seconds s, fully active."""
    return [{'start_ns': (t - 1) * NS, 'end_ns': t * NS, 'state': state(t), 'active_ns': NS,
             'clock_mhz': clock(t)} for t in range(1, seconds + 1)]


def stamps(first, n, rate=lambda i: 10.0):
    out, t = [], first * NS
    for i in range(n):
        t += int(NS / rate(i))
        out.append(t)
    return out


class TurnPrintsTests(unittest.TestCase):
    def test_start_state_is_the_last_reading_at_or_before_the_turns_start(self):
        t = turn(start=50, first=60, end=70, tokens=100)
        os_readings = [(40 * NS, 0), (50 * NS, 1), (55 * NS, 2)]
        rows = pm(49, state=lambda s: 'Fair' if s == 49 else 'Nominal')
        out = p.turn_prints(t, os_readings=os_readings, pm_rows=rows)
        self.assertEqual(out['start_state'], {'os_level': 1, 'pm_state': 'Fair'})
        self.assertEqual(p.turn_prints(turn(start=0), os_readings=[], pm_rows=[])['start_state'],
                         {'os_level': None, 'pm_state': None})

    def test_first_reading_off_in_seconds_and_tokens(self):
        t = turn()
        st = stamps(10, 1200)                       # 10 tokens a second from the first token at 10 s
        os_readings = [(s * NS, 2 if s >= 40 else 0) for s in range(0, 130)]
        out = p.turn_prints(t, os_readings=os_readings, pm_rows=pm(130), token_stamps_ns=st)
        off = out['first_off']
        self.assertEqual((off['s_after_turn_start'], off['s_after_first_token'], off['in_prefill']), (40.0, 30.0, False))
        self.assertEqual((off['tokens'], off['os_level']), (300, 2))
        # A non-Nominal PM state alone is off, and the earlier of the two wins.
        rows = pm(130, state=lambda s: 'Heavy' if s >= 25 else 'Nominal')
        off = p.turn_prints(t, os_readings=os_readings, pm_rows=rows, token_stamps_ns=st)['first_off']
        self.assertEqual((off['s_after_first_token'], off['pm_state'], off['tokens']), (15.0, 'Heavy', 150))
        # Never off, and off only during prefill.
        self.assertIsNone(p.turn_prints(t, os_readings=[(s * NS, 0) for s in range(130)], pm_rows=pm(130))['first_off'])
        early = p.turn_prints(t, os_readings=[(5 * NS, 1)], pm_rows=pm(130))['first_off']
        self.assertEqual((early['in_prefill'], early['s_after_first_token']), (True, -5.0))
        # Unknown and missing states are not off.
        self.assertIsNone(p.turn_prints(t, os_readings=[], pm_rows=pm(130, state=lambda s: 'Unknown'))['first_off'])

    def test_share_of_decode_readings_at_each_level_counts_decode_only(self):
        t = turn()
        os_readings = [(s * NS, 0 if s < 70 else 1 if s < 100 else 2) for s in range(0, 131)]
        out = p.turn_prints(t, os_readings=os_readings, pm_rows=[])
        # Decode readings are those from 10 s to 130 s inclusive: 121 of them.
        self.assertEqual(out['decode_readings']['os'], 121)
        self.assertAlmostEqual(out['decode_os_level_share']['0'], 60 / 121)
        self.assertAlmostEqual(out['decode_os_level_share']['1'], 30 / 121)
        self.assertAlmostEqual(out['decode_os_level_share']['2'], 31 / 121)
        self.assertAlmostEqual(sum(out['decode_os_level_share'].values()), 1.0)

    def test_clock_ratio_by_256_token_block_and_over_the_last_512(self):
        t = turn(first=10, end=130, tokens=1200)
        st = stamps(10, 1200)                                  # 120 s of decode
        rows = pm(130, clock=lambda s: 1000.0 if s <= 70 else 900.0)   # falls to 0.9 of the base at 70 s
        out = p.turn_prints(t, pm_rows=rows, token_stamps_ns=st)
        self.assertEqual(out['base_clock_mhz'], 1000.0)
        blocks = out['clock_ratio_by_block']
        self.assertEqual([b['block'] for b in blocks], [0, 1, 2, 3, 4])
        self.assertEqual([b['full'] for b in blocks], [True, True, True, True, False])
        self.assertAlmostEqual(blocks[0]['clock_ratio'], 1.0)           # 10.0 to 35.6 s
        self.assertAlmostEqual(blocks[1]['clock_ratio'], 1.0)           # 35.6 to 61.2 s
        self.assertAlmostEqual(blocks[3]['clock_ratio'], 0.9)           # 86.8 to 112.4 s
        self.assertEqual(blocks[4]['tokens'], [1024, 1200])
        self.assertAlmostEqual(out['clock_ratio_last_512'], 0.9)        # 78.8 to 130 s, all below 70 s
        # Token position cannot be printed without stamps.
        bare = p.turn_prints(t, pm_rows=rows)
        self.assertEqual((bare['token_basis'], bare['clock_ratio_by_block'], bare['clock_ratio_last_512']),
                         ('unavailable', [], None))
        self.assertEqual(bare['base_clock_mhz'], 1000.0)

    def test_token_rate_ratio_over_the_last_512_against_the_first_10_s(self):
        t = turn(first=10, end=130, tokens=1200)
        slow = stamps(10, 1200, rate=lambda i: 10.0 if i < 700 else 5.0)
        out = p.turn_prints(t, pm_rows=pm(130), token_stamps_ns=slow)
        self.assertAlmostEqual(out['token_rate_ratio_last_512'], 0.5, delta=0.01)   # 12 of the 512 tokens are fast
        flat = p.turn_prints(t, pm_rows=pm(130), token_stamps_ns=stamps(10, 1200))
        self.assertAlmostEqual(flat['token_rate_ratio_last_512'], 1.0, places=2)
        short = p.turn_prints(t, pm_rows=pm(130), token_stamps_ns=stamps(10, 300))
        self.assertIsNone(short['token_rate_ratio_last_512'])

    def test_hold_time_is_removed_from_block_clock_and_token_rate(self):
        # A 60 s hold between tokens 512 and 513 (clock 500 during it) leaves the clock ratio and rate alone.
        t = turn(first=10, end=200, tokens=1024)
        st = stamps(10, 512)
        resume = st[-1] + 60 * NS
        st += [resume + (i + 1) * NS // 10 for i in range(512)]
        hold = {'kind': 'H', 'turn': 0, 'start_ns': st[511], 'end_ns': resume}
        clock = lambda s: 500.0 if st[511] // NS < s <= resume // NS else 1000.0
        out = p.turn_prints(t, intervals=[hold], pm_rows=pm(200, clock=clock), token_stamps_ns=st)
        self.assertAlmostEqual(out['clock_ratio_last_512'], 1.0, places=2)
        self.assertAlmostEqual(out['token_rate_ratio_last_512'], 1.0, places=2)
        self.assertAlmostEqual(out['clock_ratio_by_block'][2]['clock_ratio'], 1.0, places=2)   # block 2 starts at the hold's end
        # A hold of another turn is ignored.
        other = p.turn_prints(t, intervals=[{**hold, 'turn': 3}], pm_rows=pm(200, clock=clock), token_stamps_ns=st)
        self.assertLess(other['clock_ratio_last_512'], 1.0 - 1e-6)

    def test_no_pm_clock_leaves_clock_prints_null(self):
        out = p.turn_prints(turn(), pm_rows=pm(130, clock=lambda s: None), token_stamps_ns=stamps(10, 1200))
        self.assertIsNone(out['base_clock_mhz'])
        self.assertEqual(out['clock_ratio_by_block'], [])


class UniformEstimateTests(unittest.TestCase):
    def test_uniform_stamps_skip_holds_and_mark_the_basis(self):
        t = turn(first=10, end=210, tokens=1000)
        hold = {'kind': 'H', 'turn': 0, 'start_ns': 60 * NS, 'end_ns': 110 * NS}    # 50 s hold inside 200 s
        st = p.uniform_token_stamps(t, [hold])
        self.assertEqual(len(st), 1000)
        self.assertEqual(st[-1], 210 * NS)
        # 150 s of decode time for 1000 tokens: 0.15 s a token; the hold opens after 50 s of decode.
        self.assertLessEqual(st[332], 60 * NS + 1)   # token 333 arrives at 10 + 50 s, as the hold opens
        self.assertGreater(st[333], 110 * NS)        # token 334 is after the hold
        self.assertEqual(st, sorted(st))
        out = p.turn_prints(t, intervals=[hold], pm_rows=pm(210), token_stamps_ns=st, estimated=True)
        self.assertEqual(out['token_basis'], 'uniform_estimate')
        self.assertIsNone(out['token_rate_ratio_last_512'])
        self.assertAlmostEqual(out['clock_ratio_last_512'], 1.0)
        # Another turn's holds do not move this turn's stamps.
        self.assertEqual(p.uniform_token_stamps(t, [{**hold, 'turn': 4}])[0], 10 * NS + round(200 * NS / 1000))


def sample(t_s, level=0, state='Nominal', pm_age_s=0.5, fast=40.0, slow=40.0):
    t = int(t_s * NS)
    return {'kind': 'sample', 'monotonic_ns': t, 'sensors': {'TV0h': fast, 'TV1h': slow},
            'status': {'os_level': level, 'pm_state': state, 'pm_observed_ns': t - int(pm_age_s * NS)}}


class CloseSection2Tests(unittest.TestCase):
    def test_g1_release_sample_state_and_stamp_age(self):
        rows = [sample(50), sample(100, level=2, state='Heavy', pm_age_s=3.0)]
        intervals = [{'kind': 'G1', 'turn': 1, 'outcome': 'released', 'exit_sample_ns': 100 * NS},
                     {'kind': 'G1', 'turn': 2, 'outcome': 'released', 'exit_sample_ns': 50 * NS},
                     {'kind': 'G0', 'turn': 0, 'outcome': 'released', 'exit_sample_ns': 50 * NS},
                     {'kind': 'G1', 'turn': 3, 'outcome': 'timeout', 'exit_sample_ns': None}]
        out = p.gate_state_prints(intervals, rows, [], 'TV0h')['g1_release_samples']
        self.assertEqual([(r['turn'], r['os_level'], r['pm_state'], r['stamp_fresh']) for r in out],
                         [(1, 2, 'Heavy', False), (2, 0, 'Nominal', True), (3, None, None, False)])
        self.assertAlmostEqual(out[0]['stamp_age_s'], 3.0)

    def test_quiet_after_last_token_needs_five_fresh_readings_at_level_0_and_nominal(self):
        t = turn(start=0, first=10, end=100)
        rows = [sample(100 + i, level=1 if i < 40 else 0, state='Heavy' if i < 40 else 'Nominal', fast=41 - i * 0.01)
                for i in range(60)]
        rows[43] = sample(143, level=0, state='Nominal', pm_age_s=5.0, fast=40.6)   # stale stamp breaks the streak
        got = p.gate_state_prints([], rows, [t], 'TV0h')['quiet_after_last_token'][0]
        self.assertEqual(got['s_from_last_token'], 44.0)        # readings 44..48 are the first five in a row
        self.assertAlmostEqual(got['fast_key_c'], 41 - 44 * 0.01)
        none = p.gate_state_prints([], rows[:20], [t], 'TV0h')['quiet_after_last_token'][0]
        self.assertEqual((none['s_from_last_token'], none['fast_key_c']), (None, None))

    def test_a_stamp_that_follows_the_sample_is_fresh_and_one_over_2_s_is_not(self):
        # RL-149 section 1.6 item 1 and the RL-145 close's row 7 rule as written: at most 2 s old. The sidecar
        # reads the status about 15 ms after the SMC read bracket starts, so a fresh age is slightly negative.
        rows = [sample(50, pm_age_s=-0.015), sample(60, pm_age_s=2.0), sample(70, pm_age_s=2.01)]
        intervals = [{'kind': 'G1', 'turn': t, 'outcome': 'released', 'exit_sample_ns': s * NS}
                     for t, s in ((1, 50), (2, 60), (3, 70))]
        out = p.gate_state_prints(intervals, rows, [], 'TV0h')['g1_release_samples']
        self.assertEqual([r['stamp_fresh'] for r in out], [True, True, False])
        self.assertTrue(p.stamp_fresh(-0.015) and not p.stamp_fresh(None))
        t = turn(start=0, first=10, end=100)
        quiet = [sample(100 + i, pm_age_s=-0.015) for i in range(5)]
        self.assertEqual(p.gate_state_prints([], quiet, [t], 'TV0h')['quiet_after_last_token'][0]['s_from_last_token'],
                         0.0)

    def test_the_stamp_rule_has_a_sanity_floor_and_refuses_non_numbers(self):
        # PR #777 row-1 review, finding 7: below -60 s is a clock mix-up, not a fresh stamp; it warns.
        import contextlib
        import io
        self.assertTrue(p.stamp_fresh(-59.9) and p.stamp_fresh(-0.02) and p.stamp_fresh(2.0))
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertFalse(p.stamp_fresh(-60.5))
        self.assertIn('sanity floor', err.getvalue())
        for bad in (float('nan'), float('-inf'), float('inf'), True, '1.0', None):
            with self.subTest(bad=bad), contextlib.redirect_stderr(io.StringIO()):
                self.assertFalse(p.stamp_fresh(bad))

    def test_tv1h_unequal_rows_are_counted_inside_and_outside_gate_windows(self):
        # RL-149 section 1.7: the per-member count, inside and outside gate windows; outside rows never fire.
        intervals = [{'kind': 'G1', 'turn': 1, 'start_ns': 10 * NS, 'end_ns': 20 * NS}]
        rows = [sample(5, slow=41.0), sample(6, slow=42.0), sample(15), sample(25), sample(26, slow=None)]
        out = p.tv1h_trigger(intervals, rows, 'TV0h', 'TV1h')
        self.assertFalse(out['fires'])
        self.assertEqual(out['unequal_rows'], {'inside_gate_windows': 0, 'outside_gate_windows': 2, 'rows_compared': 4})
        out = p.tv1h_trigger(intervals, rows + [sample(12, slow=40.5)], 'TV0h', 'TV1h')
        self.assertTrue(out['fires'])
        self.assertEqual(out['unequal_rows']['inside_gate_windows'], 1)

    def test_tv1h_trigger_lists_rows_inside_gate_windows_only(self):
        intervals = [{'kind': 'G1', 'turn': 1, 'start_ns': 10 * NS, 'end_ns': 20 * NS},
                     {'kind': 'H', 'turn': 1, 'start_ns': 30 * NS, 'end_ns': 40 * NS}]
        rows = [sample(5, slow=41.0), sample(15, slow=41.0), sample(16), sample(35, slow=39.9), sample(50, slow=1.0)]
        out = p.tv1h_trigger(intervals, rows, 'TV0h', 'TV1h')
        self.assertTrue(out['fires'])
        self.assertEqual([(r['gate'], r['monotonic_ns'] // NS) for r in out['rows']], [('G1', 15), ('H', 35)])
        self.assertFalse(p.tv1h_trigger(intervals, [sample(15), sample(35)], 'TV0h', 'TV1h')['fires'])

    def test_token_times_from_token_events(self):
        t = turn(start=0, first=10, end=20, tokens=3)
        ev = lambda ts, typ, phase, idx=0: {'timestamp_s': ts, 'event_type': typ, 'phase': phase,
                                            'message': '', 'metadata': {'align_turn_index': idx}}
        events = [ev(1000.0, 'phase_end', 'prefill'), ev(1000.5, 'token', 'decode'), ev(1001.5, 'token', 'decode'),
                  ev(1003.0, 'token', 'decode'), ev(1002.0, 'token', 'decode', idx=7), ev(1002.0, 'phase_end', 'prefill', idx=7)]
        self.assertEqual(p.token_stamps_from_events(events, t), [int(10.5 * NS), int(11.5 * NS), int(13.0 * NS)])
        self.assertIsNone(p.token_stamps_from_events(events[:1], t))
        self.assertIsNone(p.token_stamps_from_events(events, turn(index=3)))
        # With real stamps the token-rate ratio is no longer null.
        t2 = turn(first=10, end=130, tokens=1200)
        out = p.turn_prints(t2, pm_rows=pm(130), token_stamps_ns=stamps(10, 1200))
        self.assertIsNotNone(out['token_rate_ratio_last_512'])
        self.assertEqual(out['token_basis'], 'stamps')


class BundlePrintsTests(unittest.TestCase):
    def test_bundle_prints_joins_desk_verdict_token_events_states_and_trigger(self):
        import tempfile
        from unittest.mock import patch
        t = SimpleNamespace(index=0, start_ns=0, first_token_ns=10 * NS, end_ns=130 * NS, decode_tokens=1200,
                            prefill_tokens=11211)
        intervals = [{'kind': 'G1', 'turn': 0, 'outcome': 'released', 'start_ns': 140 * NS, 'end_ns': 150 * NS,
                      'exit_sample_ns': 150 * NS}]
        ep = SimpleNamespace(episode_id='ep', turns=[t], hardware={'thermal': {
            'intervals': intervals, 'policy': {'sensors': {'s_fast': 'TV0h', 's_slow': 'TV1h'}}}})
        rows = [sample(145, slow=40.5), sample(150)]
        events = [{'timestamp_s': 500.0, 'event_type': 'phase_end', 'phase': 'prefill', 'message': '',
                   'metadata': {'align_turn_index': 0}}]
        events += [{'timestamp_s': 500.0 + 0.1 * (i + 1), 'event_type': 'token', 'phase': 'decode', 'message': '',
                    'metadata': {'align_turn_index': 0}} for i in range(1200)]
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / 'outputs').mkdir()
            (Path(tmp) / 'events.jsonl').write_text(''.join(json.dumps(e) + '\n' for e in events))
            (Path(tmp) / 'outputs/align_thermal.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in rows))
            record = {'turn_observation': [{'os_nominal': False, 'pm_nominal': True}],
                      'calibration_exclusions': ['thermal.os_level_nonzero'], 'flags': ['x']}
            with patch('joulewise.align.apple.workload.read_episode_bundle', return_value=ep), \
                    patch('joulewise.align.apple.thermal_desk.native_pm_samples', return_value=pm(160)), \
                    patch('joulewise.align.apple.thermal_desk.read_bundle_record', return_value=record):
                out = p.bundle_prints(tmp)
        row = out['turns'][0]
        self.assertEqual((row['token_basis'], row['prefill_s'], row['prefill_tokens']), ('stamps', 10.0, 11211))
        self.assertEqual((row['decode_s'], row['load_s']), (120.0, 130.0))
        self.assertIsNotNone(row['token_rate_ratio_last_512'])
        self.assertEqual((row['desk_os_nominal'], row['desk_pm_nominal']), (False, True))
        self.assertEqual(out['desk_verdict'], {'member_excluded': True, 'exclusion_reasons': ['thermal.os_level_nonzero'],
                                               'flags': ['x'], 'per_turn': [{'turn': 0, 'os_nominal': False, 'pm_nominal': True}]})
        self.assertEqual(out['gate_states']['g1_release_samples'][0]['os_level'], 0)
        self.assertTrue(out['tv1h_trigger']['fires'])


def reading(t_s, level=0, state='Nominal', pm_age_s=-0.015, fast=40.0, slow=40.0):
    """One row in the runtime Sidecar's journal shape (``joulewise.align_thermal.v1`` ``reading``: stamps nested in
    ``started``/``finished``, the status in ``values.status``). Structure only, synthetic values."""
    t = int(t_s * NS)
    stamp = lambda ns: {'monotonic_ns': ns, 'monotonic_raw_ns': ns + 7, 'wall_ns': ns + 1_700_000_000 * NS}
    return {'schema': 'joulewise.align_thermal.v1', 'module': 'temperature', 'kind': 'reading', 'session': 's',
            'seq': t_s, 'started': stamp(t), 'finished': stamp(t + 2_000_000), 'raw': [], 'error': None,
            'values': {'source': 'smc', 'sensors': {'TV0h': fast, 'TV1h': slow}, 'errors': {}, 'readings': {},
                       'units': {'TV0h': 'degC', 'TV1h': 'degC'},
                       'status': {'monotonic_ns': t + 15_000_000, 'os_level': level, 'pm_state': state,
                                  'pm_observed_ns': t - int(pm_age_s * NS)}}}


class SidecarBundlePrintsTests(unittest.TestCase):
    """RL-149 section 1.2: the prints read the Sidecar's ``reading`` rows through ``thermal_gates.sample_rows``,
    and take token events from ``outputs/align_runtime_events.jsonl`` when ``events.jsonl`` has none (step 0)."""

    def test_reading_rows_and_the_runtime_events_fallback(self):
        import tempfile
        from unittest.mock import patch
        t = SimpleNamespace(index=0, start_ns=0, first_token_ns=10 * NS, end_ns=130 * NS, decode_tokens=1200,
                            prefill_tokens=11211)
        intervals = [{'kind': 'G1', 'turn': 0, 'outcome': 'released', 'start_ns': 140 * NS, 'end_ns': 150 * NS,
                      'exit_sample_ns': 150 * NS}]
        ep = SimpleNamespace(episode_id='ep', turns=[t], hardware={'thermal': {
            'intervals': intervals, 'policy': {'sensors': {'s_fast': 'TV0h', 's_slow': 'TV1h'}}}})
        journal = [{'kind': 'session_start', 'module': 'temperature', 'values': {}}, reading(145, slow=40.5),
                   reading(150), reading(160, slow=41.0), {'kind': 'session_end', 'module': 'temperature', 'values': {}}]
        events = [{'timestamp_s': 500.0, 'event_type': 'phase_end', 'phase': 'prefill', 'message': '',
                   'metadata': {'align_turn_index': 0}}]
        events += [{'timestamp_s': 500.0 + 0.1 * (i + 1), 'event_type': 'token', 'phase': 'decode', 'message': '',
                    'metadata': {'align_turn_index': 0}} for i in range(1200)]
        record = {'turn_observation': [{'os_nominal': True, 'pm_nominal': True}], 'calibration_exclusions': [],
                  'flags': []}
        for where in ('events.jsonl', 'outputs/align_runtime_events.jsonl'):
            with self.subTest(where=where), tempfile.TemporaryDirectory() as tmp:
                (Path(tmp) / 'outputs').mkdir()
                (Path(tmp) / 'events.jsonl').write_text('' if where != 'events.jsonl' else
                                                        ''.join(json.dumps(e) + '\n' for e in events))
                (Path(tmp) / where).write_text(''.join(json.dumps(e) + '\n' for e in events))
                (Path(tmp) / 'outputs/align_thermal.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in journal))
                with patch('joulewise.align.apple.workload.read_episode_bundle', return_value=ep), \
                        patch('joulewise.align.apple.thermal_desk.native_pm_samples', return_value=pm(160)), \
                        patch('joulewise.align.apple.thermal_desk.read_bundle_record', return_value=record):
                    out = p.bundle_prints(tmp)
                self.assertEqual(out['token_events_source'], where)
                self.assertEqual(out['turns'][0]['token_basis'], 'stamps')
                g1 = out['gate_states']['g1_release_samples'][0]
                self.assertEqual((g1['os_level'], g1['pm_state'], g1['stamp_fresh']), (0, 'Nominal', True))
                self.assertTrue(out['tv1h_trigger']['fires'])               # the 145 s row is inside the G1 window
                self.assertEqual(out['tv1h_trigger']['unequal_rows'],
                                 {'inside_gate_windows': 1, 'outside_gate_windows': 1, 'rows_compared': 3})


class ResidualByLoadBinTests(unittest.TestCase):
    def test_bins_by_prefill_plus_decode_seconds(self):
        rows = [{'trajectory': 'a', 'residual_j': r, 'prefill_s': pf, 'decode_s': dc}
                for r, pf, dc in ((1.0, 50, 50), (3.0, 60, 41), (10.0, 100, 100), (20.0, 140, 160), (50.0, 140, 161))]
        rows += [{'trajectory': 'a', 'residual_j': 9.0, 'prefill_s': None, 'decode_s': 5}]
        out = p.residual_by_load_bin(rows)
        self.assertEqual(out['skipped'], 1)
        got = {(r['trajectory'], r['load_bin']): (r['n'], r['mean_residual_j']) for r in out['rows']}
        self.assertEqual(got[('a', '<=100')], (1, 1.0))
        self.assertEqual(got[('a', '101-200')], (2, 6.5))
        self.assertEqual(got[('a', '201-300')], (1, 20.0))
        self.assertEqual(got[('a', '>300')], (1, 50.0))
        self.assertEqual(got[('*', '101-200')], (2, 6.5))


class ResidualByDecodeBinTests(unittest.TestCase):
    def test_bin_edges_and_trajectory_grouping(self):
        rows = [{'trajectory': 'a', 'decode_tokens': n, 'residual_j': r}
                for n, r in ((0, 1.0), (1024, 3.0), (1025, 10.0), (2048, 20.0), (2049, 100.0), (4096, 300.0))]
        rows.append({'trajectory': 'b', 'decode_tokens': 500, 'residual_j': 5.0})
        got = {(r['trajectory'], r['decode_bin']): (r['n'], r['mean_residual_j']) for r in p.residual_by_decode_bin(rows)}
        self.assertEqual(got[('a', '<=1024')], (2, 2.0))
        self.assertEqual(got[('a', '1025-2048')], (2, 15.0))
        self.assertEqual(got[('a', '>2048')], (2, 200.0))
        self.assertEqual(got[('b', '<=1024')], (1, 5.0))
        self.assertEqual(got[('*', '<=1024')], (3, 3.0))
        self.assertEqual(p.residual_by_decode_bin([]), [])

    def test_the_hold_count_print_is_not_what_the_desk_calls(self):
        # The desk glue prints the decode-bin residual; v4_estimands is unchanged (no scorer change).
        import scripts.align_v4_thermal_desk as desk
        report = desk.rl145_prints_report({'members': [], 'residual_rows': 'rows.jsonl'}, Path('.'),
                                          lambda name: [{'trajectory': 'a', 'decode_tokens': 10, 'residual_j': 2.0}])
        self.assertTrue(report['print_only'])
        self.assertEqual(report['residual_by_decode_bin'][0]['decode_bin'], '<=1024')
        self.assertIsNone(desk.rl145_prints_report({'members': []}, Path('.'), None)['residual_by_decode_bin'])


if __name__ == '__main__':
    unittest.main()
