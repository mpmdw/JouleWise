"""R23m lead-ruling hand witnesses; synthetic observations only."""
from dataclasses import replace
from pathlib import Path
import tempfile
import unittest

from joulewise.align.records import ToolCall
from joulewise.align.v4_analysis import analyze, acceptance as ac, dc, engine as e, raw
from joulewise.align.v4_analysis.io import canonical, load
from joulewise.align.v4_analysis.synthetic import series
from joulewise.external import km003c_parse as kp
from tests.align.test_attribution import episode, turn
from tests.align.test_v4_r23_engine import w1_window
from tests.align.test_v4_r23c_engine import native_payload, write_export

MS = 1_000_000


def stream(times_ms, watts, *, offset_ns=7_000_000_000):
    """Already fitted meter samples; RAW = episode monotonic + offset."""
    return kp.Stream(
        dict(status='streaming', start_raw_ns=offset_ns, start_mono_ns=0),
        dict(end_raw_ns=offset_ns+MS, end_mono_ns=MS), [], [],
        kp.Samples(times_ms, [28.]*len(watts), [w/28 for w in watts],
                   [0]*len(watts), 0, 100),
        kp.Fit(offset_ns, 1e6, dict(excess_latency_ms_max=0.)),
        [offset_ns+t*MS for t in times_ms], watts, [], [])


def capture(ep, meter):
    return dc.capture([('synthetic', meter)], ep, (ep.start_ns, ep.end_ns))


class TurnDCHoldTests(unittest.TestCase):
    def test_subpoll_prefill_is_defined_and_whole_member_stays_production(self):
        ep = episode(turns=(turn(start=20*MS, first=59_600_000, end=250*MS),),
                     start_ns=0, end_ns=300*MS)
        meter = stream([0, 100, 200, 300], [10., 20., 40., 80.])
        result = capture(ep, meter)
        self.assertEqual(result['status'], 'available')
        # Prefill: 10 W * .0396 s. Remaining owned time:
        # 10 W * .0404 s + 20 W * .1 s + 40 W * .05 s.
        self.assertAlmostEqual(result['turn_owned_j'], .396+.404+2.+2.)
        a, b = (v+7_000_000_000 for v in (ep.start_ns, ep.end_ns))
        self.assertEqual(result['whole_member_j'], kp.integrate(meter.host_ns, meter.watts, a, b)[0])
        self.assertEqual(result['whole_member_j'], 7.)  # mean(10,20,40) * .3

    def test_variable_power_hold_with_own_tool_and_unowned_hold(self):
        call = ToolCall(name='synthetic', args_bytes=2, start_ns=300*MS,
                        end_ns=350*MS, result_bytes=2)
        ep = episode(turns=(turn(start=50*MS, first=75*MS, end=250*MS, calls=(call,)),),
                     start_ns=0, end_ns=400*MS,
                     hardware={'thermal': {'intervals': [dict(kind='H', turn=0,
                         start_ns=100*MS, end_ns=150*MS)]}})
        result = capture(ep, stream([0, 100, 200, 300, 400], [10., 20., 40., 80., 160.]))
        self.assertEqual(result['status'], 'available')
        # Owned model: .05*10 + .05*20 + .05*40 = 3.5 J.
        # Own tool after the turn adds .05*80 = 4 J; the hold/gaps add zero.
        self.assertEqual(result['turn_owned_j'], 7.5)
        self.assertEqual(result['whole_member_j'], 15.)

    def test_400ms_gap_in_owned_time_is_uncovered(self):
        for start, end in ((50*MS, 550*MS), (150*MS, 175*MS)):
            with self.subTest(start=start, end=end):
                ep = episode(turns=(turn(start=start, first=start+MS, end=end),),
                             start_ns=0, end_ns=600*MS)
                result = capture(ep, stream([0, 100, 500, 600], [10.]*4))
                self.assertEqual(result['status'], 'missing')
                self.assertIn('meter.turn_uncovered', result['flags'])

    def test_drop_outside_owned_time_does_not_uncover_turn(self):
        ep = episode(turns=(turn(start=500*MS, first=525*MS, end=550*MS),),
                     start_ns=0, end_ns=600*MS)
        result = capture(ep, stream([0, 100, 500, 600], [10.]*4))
        self.assertEqual(result['status'], 'available')
        self.assertEqual(result['turn_owned_j'], .5)
        self.assertEqual(result['whole_member_j'], 6.)
        self.assertNotIn('meter.turn_uncovered', result['flags'])

    def test_300ms_hold_is_covered_but_never_extrapolate_stream_edges(self):
        ep = episode(turns=(turn(start=50*MS, first=75*MS, end=250*MS),),
                     start_ns=0, end_ns=400*MS)
        result = capture(ep, stream([0, 300, 400], [10.]*3))
        self.assertEqual(result['status'], 'available')
        self.assertEqual(result['turn_owned_j'], 2.)
        for start, end in ((-MS, 50*MS), (350*MS, 401*MS)):
            with self.subTest(start=start, end=end):
                outside = replace(ep, start_ns=min(0, start), end_ns=max(400*MS, end),
                    turns=(turn(start=start, first=start+MS, end=end),))
                result = capture(outside, stream([0, 100, 200, 300, 400], [10.]*5))
                self.assertIn('meter.turn_uncovered', result['flags'])


class RegisteredG0Tests(unittest.TestCase):
    def test_ungated_anchor_model_has_no_registered_g0(self):
        members = series(turns=4)['windows'][0]['members']
        # Deliberately stale observed fields must not invent planned gates.
        result = ac.window_checks(members, {'status': 'inconclusive'}, window='C1')['qwen3-30b-a3b']['U2']
        self.assertEqual(result['parts']['a'], 'not_applicable')

    def test_registered_g0_missing_is_inconclusive_even_if_observed_ungated(self):
        for gated in (False, True):
            with self.subTest(observed_gated=gated):
                members = series(turns=4)['windows'][0]['members']
                for m in members[4:]:
                    # A stale temperature cannot stand in for a released G0.
                    m['thermal'].update(gated=gated, intervals=[], g0_slow_c=55., releases=[])
                result = ac.window_checks(members, {'status': 'inconclusive'}, window='C1')[e.D_MODEL]['U2']
                self.assertEqual(result['parts']['a'], 'inconclusive')

    def test_w1_missing_planned_contrast_does_not_make_anchor_model_g0_inapplicable(self):
        p = series(turns=4)
        w1 = w1_window(p)
        missing = raw.member(Path.cwd(), dict(w1['members'][0]['slot'], ordinal=6,
            series_role='contrast', run_id='W1-missing-X-G'), dict(captured=False))
        w1['members'].append(missing)
        p['windows'] = [w1]
        fill, _ = analyze(p)
        self.assertEqual(fill['W1']['checks']['qwen3-30b-a3b']['U2']['parts']['a'], 'inconclusive')


class CaptureClassTests(unittest.TestCase):
    def test_uncaptured_has_only_not_captured_and_captured_incomplete_keeps_class(self):
        p = series(turns=4)
        p['windows'] = p['windows'][:1]
        p['windows'].insert(0, w1_window(p))
        for w in p['windows']:
            old = w['members'][0]
            missing = raw.member(Path.cwd(), old['slot'],
                dict(captured=False, exclusion_codes=['member_incomplete', 'X3']))
            missing['thermal']['calibration_exclusions'] = ['member_incomplete']
            w['members'][0] = missing
        p['windows'][1]['members'][5]['thermal']['status'] = 'incomplete'
        fill, _ = analyze(p)
        row = fill['windows'][0]['eligibility'][0]
        self.assertEqual(row['classes'], ['not_captured'])
        self.assertEqual(row['reasons'], ['not_captured'])
        self.assertIn('incomplete', fill['windows'][0]['eligibility'][5]['classes'])
        self.assertEqual(fill['anchor_sigma_w']['W1_anchor_block'], 'excluded:not_captured')


class PrefixSeriesTests(unittest.TestCase):
    def test_w1_c1_then_c2_print_only_present_windows(self):
        p = native_payload()
        with tempfile.TemporaryDirectory() as tmp:
            path = write_export(Path(tmp), p)
            for through, expected_k in (('W1', 1), ('C1', 2), ('C2', 3)):
                with self.subTest(through=through):
                    fill, verdict = analyze(load(path, through_window=through))
                    present = {'W1'} | ({'C1'} if through != 'W1' else set()) | ({'C2'} if through == 'C2' else set())
                    self.assertEqual(set(fill['acceptance']), present)
                    self.assertEqual({r['window'] for r in fill['windows']}, present-{'W1'})
                    self.assertEqual({r['window_id'] for r in fill['ledger']}, present-{'W1'})
                    self.assertEqual(fill['test'], {})
                    for key in ('fits', 'dc_secondary', 'realized_counts', 'cache_diagnostics',
                                'no_rebuild_sensitivity'):
                        self.assertLessEqual({r['window'] for r in fill[key]}, present)
                    self.assertEqual(verdict['input_windows'], len(present)-1)
                    self.assertEqual(fill['anchor_sigma_w']['K'], expected_k)
                    if through == 'C1':
                        self.assertEqual(fill['anchor_sigma_w'], dict(status='print_only',
                            W1_anchor_block='included', K=2, anchor_sigma_j=None,
                            ms_window_j2=None, ms_error_j2=None, sigma_w2_raw_j2=None,
                            sigma_w2_reported_j2=None, method='balanced crossed-anchor moment',
                            reason='requires K >= 3 anchor sessions'))

    def test_no_eligible_anchor_blocks_has_fixed_empty_state(self):
        result = ac.anchor_diagnostic([])
        self.assertEqual(result, dict(status='print_only',
            W1_anchor_block='unavailable:W1 window unavailable', K=0, anchor_sigma_j=None,
            ms_window_j2=None, ms_error_j2=None, sigma_w2_raw_j2=None,
            sigma_w2_reported_j2=None, method='balanced crossed-anchor moment',
            reason='requires K >= 3 anchor sessions'))
        self.assertEqual(canonical(result), canonical(ac.anchor_diagnostic([])))


if __name__ == '__main__':
    unittest.main()
