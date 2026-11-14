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
