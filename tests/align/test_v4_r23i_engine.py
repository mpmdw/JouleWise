"""R22-2/R24/R25 and F3 witnesses. All evidence is tiny and synthetic."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.apple import thermal_desk as td, v4_cadence as cad
from joulewise.align.v4_analysis import analyze, acceptance as ac, engine as e, raw
from joulewise.align.v4_analysis.io import canonical, digest, load
from joulewise.align.v4_analysis.synthetic import series
from tests.align.test_thermal_desk import contrast
from tests.align.test_v4_r23c_engine import r24_manifest, write_export


def row(name, *, barred=None, captured=22, n=7, status='final'):
    return dict(window=name, status=status, captured_members=captured,
                eligible_benign=dict(spam=0 if barred else n, bank=0 if barred else n),
                **({'barred': barred} if barred else {}))


def zero(window, attempt):
    w = copy.deepcopy(window)
    w['attempt_id'] = w['window']+'#'+str(attempt)
    w['members'] = [raw.member(Path.cwd(), m['slot'], {'captured': False}) for m in w['members']]
    return w


def bar(window):
    # A healthy, eligible sentinel whose active clock differs by >0.5%.
    window['members'][21]['thermal']['decode_clock_mhz'] = 1300.


class CalibrationStopTests(unittest.TestCase):
    def test_bar_replaced_never_added_and_all_calibrators_count(self):
        rows = [row('C1', barred='u1_u3_fail')]+[row(f'C{i}') for i in range(2, 9)]
        before = cad.calibration_stop(rows)
        self.assertEqual((before['decision'], before['attempted']), ('continue', 7))
        after = cad.calibration_stop(rows+[row('C9')])
        self.assertEqual((after['decision'], after['attempted']), ('calibration_complete', 8))
        self.assertEqual(after['eligible_by_pair'], dict(spam=56, bank=56))
        self.assertEqual(after['barred_windows'], ['C1'])
        self.assertEqual((after['replacements_used'], after['replacements_allowed']), (1, 6))

    def test_seventh_bar_exhausts_cap(self):
        rows = [row(f'C{i}', barred='whole_window_capture_failure') for i in range(1, 7)]
        rows += [row(f'C{i}') for i in range(7, 14)]
        self.assertEqual(cad.calibration_stop(rows)['decision'], 'continue')
        result = cad.calibration_stop(rows+[row('C14', barred='u1_u3_fail')])
        self.assertEqual((result['decision'], result['attempted']), ('insufficient_calibration', 7))

    def test_retry_zero_is_one_bar_and_only_escalates_beyond_six(self):
        rows = [row('C1#1', captured=0, n=0), row('C1#2', captured=0, n=0)]
        result = cad.calibration_stop(rows)
        self.assertEqual((result['decision'], result['replacements_used']), ('continue', 1))
        self.assertEqual(result['zero_capture_refusals'], 2)
        rows += [row(f'C{i}#1', barred='u1_u3_fail') for i in range(2, 7)]
        rows += [row(f'C{i}#1') for i in range(7, 14)]
        rows += [row('C14#1', captured=0, n=0), row('C14#2', captured=0, n=0)]
        self.assertEqual(cad.calibration_stop(rows)['decision'], 'escalate_to_lead')
        ruling = dict(ruling_id='synthetic-R24', text_sha256='d'*64,
                      resets='zero_capture_escalation', after_window='C14#2',
                      lead_signature='lead: synthetic-ruling 2026-11-08')
        result = cad.calibration_stop(rows, [ruling])
        self.assertEqual(result['decision'], 'insufficient_calibration')
        self.assertEqual(result['lead_rulings_applied'], ['synthetic-R24'])

    def test_different_unretried_zero_slots_still_escalate(self):
        self.assertEqual(cad.calibration_stop([row('C1', captured=0, n=0),
                                              row('C2', captured=0, n=0)])['decision'],
                         'escalate_to_lead')

    def test_provisional_bar_holds_and_nonstructural_zero_yield_counts(self):
        pending = cad.calibration_stop([row('C1', barred='u1_u3_fail', status='provisional')])
        self.assertEqual(pending['decision'], 'pending_final_eligibility')
        result = cad.calibration_stop([row('C1', captured=1, n=0)]+[row(f'C{i}') for i in range(2, 9)])
        self.assertEqual((result['decision'], result['attempted']), ('calibration_complete', 8))

    def test_structural_bars_cannot_carry_partial_counts_or_unknown_codes(self):
        for bad in (dict(row('C1'), barred='u1_u3_fail'), row('C1', barred='low_m'),
                    row('C1', barred='whole_window_capture_failure', captured=0)):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                cad.calibration_stop([bad])


class EngineReplacementTests(unittest.TestCase):
    def test_c1_bar_needs_c9_and_barred_members_never_reach_fits(self):
        p = series(turns=4, reserves=1)
        bar(p['windows'][0])
        p['windows'] = p['windows'][:8]
        before, _ = analyze(p)
        self.assertEqual((before['calibration']['decision'], before['calibration']['attempted']), ('continue', 7))
        self.assertTrue(all(c['threshold'] is None for c in before['thresholds'].values()))
        p['windows'].append(series(turns=4, reserves=1)['windows'][8])
        fill, _ = analyze(p)
        self.assertEqual((fill['calibration']['decision'], fill['calibration']['attempted']), ('calibration_complete', 8))
        self.assertEqual(fill['ledger'][0]['barred'], 'u1_u3_fail')
        self.assertEqual(fill['ledger'][0]['eligible_benign'], dict(spam=0, bank=0))
        self.assertTrue(all(f['window'] != 'C1' for f in fill['fits']))
        for cutoff in fill['thresholds'].values():
            self.assertEqual(cutoff['m'], 56)
            self.assertFalse(any(m.startswith('C1/') for m in cutoff['calibration_members']))
            self.assertTrue(any(m.startswith('C9/') for m in cutoff['calibration_members']))
        # Scores/energies in a barred window cannot alter a threshold.
        for m in p['windows'][0]['members'][5:21]:
            if m['slot']['condition'] == 'benign':
                for convention in ('True', 'False'):
                    for r in m['summary']['residual_rows'][convention]:
                        r['energy_j'] += 100000.
        changed, _ = analyze(p)
        self.assertEqual(changed['thresholds'], fill['thresholds'])

    def test_reserves_refuse_without_bar_or_for_low_m_or_out_of_order(self):
        p = series(turns=4, reserves=2)
        for low_m in (False, True):
            q = copy.deepcopy(p)
            q['windows'] = q['windows'][:9]
            if low_m:
                for w in q['windows'][:8]:
                    w['adjudicated_member_ids'] = []
            with self.subTest(low_m=low_m), self.assertRaisesRegex(ValueError, 'reserve requires'):
                analyze(q)
        bar(p['windows'][0])
        p['windows'] = p['windows'][:8]+[p['windows'][9]]
        with self.assertRaisesRegex(ValueError, 'window order'):
            analyze(p)

    def test_retry_identity_must_bind_the_frozen_slot(self):
        for attempt in ('C2#1', 'C1#zero1'):
            p = series(turns=4)
            p['windows'] = [zero(p['windows'][0], 1)]
            p['windows'][0]['attempt_id'] = attempt
            with self.subTest(attempt=attempt), self.assertRaisesRegex(ValueError, 'attempt id'):
                analyze(p)

    def test_seven_bars_including_c14_are_insufficient(self):
        p = series(turns=4, reserves=6)
        p['windows'] = p['windows'][:14]
        for w in p['windows'][:6]+p['windows'][13:]:
            bar(w)
        fill, _ = analyze(p)
        self.assertEqual((fill['calibration']['decision'], fill['calibration']['attempted']), ('insufficient_calibration', 7))
        self.assertEqual(fill['calibration']['replacements_used'], 7)
        self.assertTrue(all(c['threshold'] is None for c in fill['thresholds'].values()))

    def test_partial_capture_with_failed_terminal_chain_enters_no_pool(self):
        for result in (dict(verdict='HOLD', chain_exit_code=0), dict(verdict='GO', chain_exit_code=1)):
            p = series(turns=4, reserves=1)
            p['windows'] = p['windows'][:9]
            p['windows'][0]['terminal_result'] = result
            fill, _ = analyze(p)
            self.assertEqual(fill['ledger'][0]['barred'], 'whole_window_capture_failure')
            self.assertFalse(fill['windows'][0]['pool_entry'])
            self.assertFalse(any(f['window'] == 'C1' for f in fill['fits']))
            self.assertEqual(fill['calibration']['decision'], 'calibration_complete')

    def test_structural_predicate_matches_each_fail_and_explicit_committed_bar(self):
        for unit in ('U1', 'U2', 'U3'):
            checks = {e.D_MODEL: {u: dict(status='fail' if u == unit else 'inconclusive')
                                  for u in ('U1', 'U2', 'U3')}}
            with self.subTest(unit=unit):
                self.assertEqual(e._structural_bar({}, checks, 1), 'u1_u3_fail')
                self.assertIsNone(e._structural_bar({}, checks, 0))
        checks = {e.D_MODEL: {u: dict(status='inconclusive') for u in ('U1', 'U2', 'U3')}}
        self.assertIsNone(e._structural_bar(dict(terminal_result=dict(verdict='GO', chain_exit_code=0)), checks, 1))
        # R23j: a declared bar must be reproduced by its evidence.
        with self.assertRaisesRegex(ValueError, 'needs non-GO terminal_result'):
            e._structural_bar(dict(barred='whole_window_capture_failure'), checks, 1)
        self.assertEqual(e._structural_bar(dict(barred='whole_window_capture_failure',
            terminal_result=dict(verdict='GO', chain_exit_code=2)), checks, 1), 'whole_window_capture_failure')

    def test_seventh_zero_bar_requires_lead_disposition_then_is_insufficient(self):
        p = series(turns=4, reserves=6)
        for w in p['windows'][:6]:
            bar(w)
        last = p['windows'][13]
        p['windows'] = p['windows'][:13]+[zero(last, 1), zero(last, 2)]
        fill, _ = analyze(p)
        self.assertEqual(fill['calibration']['decision'], 'escalate_to_lead')
        p['lead_releases'] = [dict(release_id='synthetic-R24', text_sha256='d'*64,
                                  after_attempt='C14#2', lead_signature='lead: synthetic-ruling 2026-11-08')]
        fill, _ = analyze(p)
        self.assertEqual(fill['calibration']['decision'], 'insufficient_calibration')
        self.assertEqual(fill['calibration']['lead_rulings_applied'], ['synthetic-R24'])

    def test_zero_retry_bars_slot_then_c9_replaces_it(self):
        p = series(turns=4, reserves=1)
        p['windows'] = [zero(p['windows'][0], 1), zero(p['windows'][0], 2), *p['windows'][1:]]
        fill, _ = analyze(p)
        self.assertEqual(fill['calibration']['decision'], 'calibration_complete')
        self.assertEqual(fill['calibration']['barred_windows'], ['C1#2'])
        self.assertTrue(any(f['window'] == 'T1' for f in fill['fits']))
        self.assertFalse(any(f['window'] == 'C1' for f in fill['fits']))
        self.assertEqual(set(fill['test']['counts_logged']['spam']['benign']['by_window']), {'T1', 'T2', 'T3'})

    def test_supplemental_only_capture_consumes_no_slot(self):
        p = series(turns=4)
        z = zero(p['windows'][0], 1)
        for slot in e.roster('C1', escalated=True)[22:]:
            m = copy.deepcopy(p['windows'][0]['members'][4])
            m['slot'] = slot
            m['thermal']['id'] = slot['run_id']
            m['thermal'].pop('identical_work_group')  # supplemental replays join no U3 group
            z['members'].append(m)
        p['windows'] = [z]
        fill, _ = analyze(p)
        self.assertEqual(fill['calibration']['attempted'], 0)
        self.assertEqual(fill['ledger'][0]['captured_members'], 0)
        self.assertFalse(fill['fits'])

    def test_reserved_seeds_and_frozen_t_allocation(self):
        self.assertEqual(e.ORDER, tuple(f'C{i}' for i in range(1, 15))+('T1', 'T2', 'T3'))
        for number in range(9, 15):
            slots = e.roster(f'C{number}')
            for pair in e.PAIRS:
                seeds = [s['seed_index'] for s in slots if s['held_out'] and s['task_pair'] == pair]
                self.assertEqual(seeds, list(range(100+8*(number-9), 108+8*(number-9))))
        self.assertEqual(min(s['seed_index'] for s in e.roster('T1') if s['held_out']), 66)
        self.assertEqual(max(s['seed_index'] for s in e.roster('T3') if s['held_out']), 89)


class ReserveExportTests(unittest.TestCase):
    def test_native_full_manifest_prefix_and_terminal_result_source(self):
        p = series(turns=4, reserves=6)
        for w in p['windows']:
            for m in w['members'][:4]:
                m['slot']['run_id'] = m['thermal']['id'] = w['window']+':'+m['slot']['run_id']
        p['synthetic'] = False
        p['series_manifest'] = r24_manifest(p)  # R23j: release needs the full R24 allocation
        p['windows'] = p['windows'][:9]+p['windows'][14:]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = canonical(dict(verdict='HOLD', chain_exit_code=0))
            (root/'terminal.json').write_bytes(data)
            p['windows'][0]['terminal_result_source'] = dict(path='terminal.json', sha256=digest(data))
            path = write_export(root, p)
            loaded = load(path, through_window='C9')
            self.assertEqual([w['window'] for w in loaded['windows']], [f'C{i}' for i in range(1, 10)])
            fill, _ = analyze(loaded)
            legacy = copy.deepcopy(loaded)
            legacy['series_manifest']['windows'] = [w for w in legacy['series_manifest']['windows']
                if w['window'] in e.ORDER[:8]+e.TEST_ORDER]
            with self.assertRaisesRegex(ValueError, 'missing from frozen series manifest'):
                analyze(legacy)
        self.assertEqual(fill['calibration']['decision'], 'calibration_complete')
        self.assertEqual(fill['ledger'][0]['barred'], 'whole_window_capture_failure')
        self.assertTrue(any(r['path'] == 'terminal.json' for r in fill['input_census']))


class U3AndContrastTests(unittest.TestCase):
    def test_u3_budgets_all_22_scopes_and_evaluates_each_reserve(self):
        p = series(turns=4, reserves=6)
        d = ac.u3_derivation(p['u3_evidence'])
        self.assertEqual(d['comparisons'], 22)
        self.assertEqual(set(d['checks_by_window']), {'W1', *e.ORDER})
        self.assertAlmostEqual(ac._series_tail(d['q'], d['n'], 22), d['beta'], places=10)
        for w in p['windows'][8:14]:
            with self.subTest(window=w['window']):
                self.assertEqual(ac.window_checks(w['members'], d, window=w['window'])[e.D_MODEL]['U3']['status'], 'pass')
                bar(w)
                self.assertEqual(ac.window_checks(w['members'], d, window=w['window'])[e.D_MODEL]['U3']['status'], 'fail')

    def test_inadequate_contrast_has_fixed_reason_and_no_fit_statistics(self):
        for cause in ('missing', 'ineligible', 'nonidentical'):
            runs = contrast()
            if cause == 'missing':
                runs.pop()
            elif cause == 'ineligible':
                runs[0]['excluded'] = True
            else:
                runs[0]['pilot7_token_identical'] = False
            with self.subTest(cause=cause), patch.object(td, 'regression', side_effect=AssertionError('fit attempted')):
                result = e.selection_report(dict(members=runs), {'status': 'inconclusive'}, 1., None)['contrast']
            self.assertEqual(result['verdict'], 'INCONCLUSIVE')
            self.assertEqual(result['reason_code'], 'insufficient_contrast_runs')
            self.assertEqual(result['reason'], 'requires 2 token-identical eligible runs in each template/arm')
            self.assertFalse(set(result) & {'d_template_j', 'arm_effect_j', 'ci90_j', 'df', 'same_arm_pairs', 'turn_tables'})


if __name__ == '__main__':
    unittest.main()
