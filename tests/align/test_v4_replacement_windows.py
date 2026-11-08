"""R22-2: two pre-declared blind replacement calibration windows, C9 and C10. Synthetic only.

Armed ONLY after a STRUCTURAL bar of a C window (U1-U3 FAIL, a whole-window capture failure, or a
zero-capture refusal beyond the retry); never on scores or eligible counts. Exactly 8 COUNTED windows.
``insufficient_calibration`` if a pair is still below 39 after both replacements are used.
"""
from copy import deepcopy
import tempfile
import unittest

from joulewise.align.apple import v4_cadence as cad
from scripts import align_v4_series as series
from tests.align.test_v4_cadence import window
from tests.align.test_v4_next_arm_packet import Scenario


def row(name, spam=7, bank=7, *, status='final', captured=22, barred=None):
    value = window(name, spam, bank, status=status, captured=captured)
    if barred:
        value.update(barred=barred, eligible_benign={'spam': 0, 'bank': 0})
    return value


def eight(*, spam=7, bank=7):
    return [row(f'C{i}', spam, bank) for i in range(1, 9)]


class CadenceTests(unittest.TestCase):
    def test_eight_counted_windows_need_no_replacement(self):
        result = cad.calibration_stop(eight())
        self.assertEqual(result['decision'], 'calibration_complete')
        self.assertEqual((result['replacements_used'], result['barred_windows']), (0, []))

    def test_a_structural_bar_is_not_counted_and_owes_one_replacement(self):
        for reason in cad.STRUCTURAL_BARS:
            rows = [*eight()[:2], row('C3', barred=reason), *eight()[3:]]
            with self.subTest(reason=reason):
                held = cad.calibration_stop(rows)
                self.assertEqual((held['decision'], held['attempted']), ('continue', 7))
                self.assertEqual((held['barred_windows'], held['replacements_used']), (['C3'], 1))
                done = cad.calibration_stop([*rows, row('C9')])
                self.assertEqual((done['decision'], done['attempted']), ('calibration_complete', 8))

    def test_six_replacements_and_the_seventh_bar_cannot_reach_eight(self):
        # R24: the cap is C14. Six bars are absorbed by C9-C14; a seventh leaves 7 admitted windows at most.
        two = [row('C1', barred='u1_u3_fail'), row('C2', barred='whole_window_capture_failure'),
               *[row(f'C{i}') for i in range(3, 9)], row('C9'), row('C10')]
        self.assertEqual(cad.calibration_stop(two)['decision'], 'calibration_complete')
        six = [*[row(f'C{i}', barred='u1_u3_fail') for i in range(1, 7)], row('C7'), row('C8'),
               *[row(f'C{i}') for i in range(9, 15)]]
        done = cad.calibration_stop(six)
        self.assertEqual((done['decision'], done['attempted'], done['replacements_used']),
                         ('calibration_complete', 8, 6))
        short = cad.calibration_stop(six[:-1])                     # C14 not yet run: 7 admitted, a window remains
        self.assertEqual((short['decision'], short['attempted']), ('continue', 7))
        seven = [*[row(f'C{i}', barred='u1_u3_fail') for i in range(1, 8)], row('C8'), *[row(f'C{i}') for i in range(9, 15)]]
        result = cad.calibration_stop(seven)
        self.assertEqual(result['decision'], 'insufficient_calibration')    # C14 reached with fewer than 8 admitted
        self.assertEqual((result['attempted'], result['replacements_used']), (7, 7))

    def test_a_pair_still_below_39_after_8_admitted_windows_is_insufficient(self):
        rows = [row('C1', barred='u1_u3_fail'), row('C2', barred='u1_u3_fail'),
                *[row(f'C{i}', 6, 7) for i in range(3, 9)], row('C9', 1, 7), row('C10', 0, 7)]
        result = cad.calibration_stop(rows)
        self.assertEqual(result['eligible_by_pair']['spam'], 6*6+1)
        self.assertEqual(result['decision'], 'insufficient_calibration')

    def test_low_counts_never_arm_a_replacement(self):
        # not a count stop: a window with no eligible members that is not structurally barred counts, and 8
        # counted windows end the series (insufficient here), with no C9
        rows = [row('C1', 0, 0), row('C2', 0, 0), row('C3', 0, 0), *[row(f'C{i}') for i in range(4, 9)]]
        result = cad.calibration_stop(rows)
        self.assertEqual((result['attempted'], result['replacements_used']), (8, 0))
        self.assertEqual(result['decision'], 'insufficient_calibration')
        self.assertEqual(cad.calibration_stop(rows[:7])['decision'], 'continue')

    def test_a_zero_capture_retry_that_is_also_zero_bars_the_slot(self):
        rows = [row('C1', 0, 0, captured=0), row('C1#2', 0, 0, captured=0)]
        result = cad.calibration_stop(rows)
        self.assertEqual((result['decision'], result['barred_windows'], result['replacements_used']),
                         ('continue', ['C1#2'], 1))
        single = cad.calibration_stop(rows[:1])
        self.assertEqual((single['decision'], single['replacements_used']), ('continue', 0))     # awaits its retry
        six = [row(f'C{n}{suffix}', 0, 0, captured=0) for n in range(1, 7) for suffix in ('', '#2')]
        self.assertEqual(cad.calibration_stop(six)['decision'], 'continue')                      # six bars: all replaced
        seven = [row(f'C{n}{suffix}', 0, 0, captured=0) for n in range(1, 8) for suffix in ('', '#2')]
        self.assertEqual(cad.calibration_stop(seven)['decision'], 'escalate_to_lead')            # beyond all six replacements
        other_slots = [row('C1', 0, 0, captured=0), row('C2', 0, 0, captured=0)]
        self.assertEqual(cad.calibration_stop(other_slots)['decision'], 'escalate_to_lead')      # unchanged RUN_STATE 216 rule

    def test_malformed_bars_and_provisional_bars_hold(self):
        for bad in (row('C1', barred='high_score'),
                    {**row('C1', barred='u1_u3_fail'), 'eligible_benign': {'spam': 1, 'bank': 0}},
                    {**row('C1', barred='u1_u3_fail'), 'captured_members': 0},
                    row('C1', captured=22) | {'barred': 'zero_capture_refusal'}):
            with self.subTest(bad=str(bad)[:80]), self.assertRaises(ValueError):
                cad.calibration_stop([bad])
        held = cad.calibration_stop([row('C1', status='provisional', barred='u1_u3_fail')])
        self.assertEqual(held['decision'], 'pending_final_eligibility')       # a provisional bar is not yet a bar
        with self.assertRaisesRegex(ValueError, 'retry follows only'):
            cad.calibration_stop([row('C1'), row('C1#2')])

    def test_triage_admits_a_replacement_arm_and_never_a_test_arm_before_eight_counted(self):
        rows = [row('C1', barred='u1_u3_fail'), *[row(f'C{i}') for i in range(2, 9)]]
        base = dict(previous_window='C8', calibration_windows=rows)
        from tests.align.test_v4_cadence import IDENTITY, INTERNAL, NOW_EPOCH, passing_packet
        calibration = cad.next_arm_triage(passing_packet(next_window_role='calibration', **base),
                                          INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)
        self.assertTrue(calibration['admitted'], calibration['reasons'])
        test = cad.next_arm_triage(passing_packet(next_window_role='test', **base), INTERNAL, IDENTITY,
                                   now_epoch_s=NOW_EPOCH)
        self.assertFalse(test['admitted'])


class ManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = series.candidate()

    def test_order_and_the_pre_declared_replacement_windows(self):
        self.assertEqual(self.manifest['order'], ['W1', *[f'C{i}' for i in range(1, 15)], 'T1', 'T2', 'T3'])
        by_id = {w['id']: w for w in self.manifest['windows']}
        for name in (f'C{i}' for i in range(9, 15)):          # R24: all six reserve windows are armable
            self.assertIs(by_id[name]['replacement'], True)
            self.assertNotIn('armable', by_id[name])
            self.assertEqual((by_id[name]['role'], by_id[name]['aliases']), ('calibration', []))
            self.assertEqual(len(by_id[name]['members']), 22)
        self.assertTrue(all('replacement' not in by_id[f'C{i}'] for i in range(1, 9)))
        calibration = self.manifest['calibration']
        self.assertEqual((calibration['counted_windows'], calibration['replacement_cap']), (8, 6))
        self.assertEqual(calibration['replacement_windows'], [f'C{i}' for i in range(9, 15)])
        self.assertEqual(calibration['reserve_windows_not_armable'], [])
        self.assertIn('never on scores', calibration['replacement_rule'].replace('ONLY to replace', 'never on scores'))
        self.assertIn('to repair low m', calibration['replacement_rule'])
        series.validate(self.manifest)                                       # the frozen executable design

    def test_t_seeds_are_exactly_r15_and_the_reserve_pool_is_contiguous_after_the_reserved_range(self):
        by_id = {w['id']: w for w in self.manifest['windows']}
        fresh = lambda name: sorted({r['seed_index'] for r in by_id[name]['members'] if r['ordinal'] in range(6, 22)})
        self.assertEqual((fresh('C8')[0], fresh('C8')[-1]), (58, 65))
        for name, (low, high) in {'T1': (66, 73), 'T2': (74, 81), 'T3': (82, 89)}.items():
            self.assertEqual((fresh(name)[0], fresh(name)[-1]), (low, high))     # unchanged from R15
        pool = {}
        for i in range(9, 15):
            name, low = f'C{i}', 100 + 8 * (i - 9)
            self.assertEqual((fresh(name)[0], fresh(name)[-1]), (low, low + 7))
            pool[name] = fresh(name)
        self.assertEqual(fresh('C13')[0], 132)
        self.assertEqual((fresh('C14')[0], fresh('C14')[-1]), (140, 147))
        every = sorted(i for seeds in pool.values() for i in seeds)
        self.assertEqual(every, list(range(100, 148)))                           # one contiguous pool, 8 per pair per window
        self.assertFalse(set(every) & series.RESERVED_INDICES)                    # 91-99 are reserved development indices
        self.assertEqual(self.manifest['seed_allocation']['reserve_pool']['start'], 100)
        per_pair = {pair: [] for pair in series.PAIRS}
        for name in [*(f'C{i}' for i in range(1, 9)), 'T1', 'T2', 'T3', *(f'C{i}' for i in range(9, 15))]:
            for r in by_id[name]['members']:
                if r['ordinal'] in range(6, 22):
                    per_pair[r['pair']].append(r['seed_index'])
        for pair, seeds in per_pair.items():
            self.assertEqual(seeds, sorted(seeds))                                # kit order
            self.assertEqual(len(seeds), len(set(seeds)))                         # distinct across all 17 windows
            self.assertFalse(set(seeds) & series.RESERVED_INDICES)
            self.assertEqual((seeds[0], seeds[-1], len(seeds)), (2, 147, 136))

    def test_every_replacement_window_materializes_and_there_is_no_window_beyond_c14(self):
        root = __import__('pathlib').Path(__file__).resolve().parents[2]
        for name in ('C9', 'C14'):
            self.assertTrue(series.build_files(root, self.manifest, name))
        with self.assertRaisesRegex(ValueError, 'not in the frozen series'):
            series.selected(self.manifest, 'C15')

class SeriesLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = series.candidate()

    def entry(self, window_id, attempt_id=None, *, captured=22, spam=7, bank=7, barred=None):
        value = dict(window_id=window_id, attempt_id=attempt_id or window_id, status='final',
                     captured_members=captured, eligible_benign=dict(spam=spam, bank=bank))
        if barred:
            value.update(barred=barred, eligible_benign=dict(spam=0, bank=0))
        return value

    def history(self, *entries):
        return [self.entry(e) if isinstance(e, str) else e for e in entries]

    def test_c9_is_armed_only_after_a_bar_and_t1_only_after_eight_counted(self):
        plain = self.history(*[f'C{i}' for i in range(1, 9)])
        rows, nxt, previous, _ = series.calibration_rows(self.manifest, plain)
        self.assertEqual((nxt, previous, len(rows)), ('T1', 'C8', 8))        # C9 is skipped: nothing was barred
        with self.assertRaisesRegex(ValueError, 'skips/reorders'):
            series.calibration_rows(self.manifest, [*plain, self.entry('C9')])
        barred = self.history(*[f'C{i}' for i in range(1, 3)], self.entry('C3', barred='u1_u3_fail'),
                              *[f'C{i}' for i in range(4, 9)])
        rows, nxt, _, _ = series.calibration_rows(self.manifest, barred)
        self.assertEqual(nxt, 'C9')                                          # T1 would be refused: only 7 counted
        self.assertTrue(any(r.get('barred') for r in rows))
        rows, nxt, _, _ = series.calibration_rows(self.manifest, [*barred, self.entry('C9')])
        self.assertEqual(nxt, 'T1')
        with self.assertRaisesRegex(ValueError, 'skips/reorders'):
            series.calibration_rows(self.manifest, [*barred, self.entry('T1', spam=0, bank=0)])

    def test_barred_windows_use_the_replacements_in_order_up_to_c14(self):
        history = self.history(self.entry('C1', barred='u1_u3_fail'), self.entry('C2', barred='whole_window_capture_failure'),
                               *[f'C{i}' for i in range(3, 9)])
        self.assertEqual(series.calibration_rows(self.manifest, history)[1], 'C9')
        history.append(self.entry('C9'))
        self.assertEqual(series.calibration_rows(self.manifest, history)[1], 'C10')
        history.append(self.entry('C10'))
        self.assertEqual(series.calibration_rows(self.manifest, history)[1], 'T1')
        with self.assertRaisesRegex(ValueError, 'skips/reorders'):
            series.calibration_rows(self.manifest, [*history[:-1], self.entry('C9', 'C9-again')])
        # six bars walk the whole reserve in order; each is armed only after the previous is consumed
        bars = [self.entry(f'C{i}', barred='u1_u3_fail') for i in range(1, 7)]
        history = [*bars, *self.history('C7', 'C8')]
        for name in (f'C{i}' for i in range(9, 15)):
            self.assertEqual(series.calibration_rows(self.manifest, history)[1], name)
            history.append(self.entry(name))
        self.assertEqual(series.calibration_rows(self.manifest, history)[1], 'T1')
        with self.assertRaisesRegex(ValueError, 'skips/reorders'):
            series.calibration_rows(self.manifest, [*bars, *self.history('C7', 'C8'), self.entry('C10')])
        # a seventh bar leaves 8 unreachable: nothing further is armed (not even T1)
        seven = [self.entry(f'C{i}', barred='u1_u3_fail') for i in range(1, 8)]
        self.assertIsNone(series.calibration_rows(self.manifest, seven)[1])
        with self.assertRaisesRegex(ValueError, 'skips/reorders'):
            series.calibration_rows(self.manifest, [*seven, self.entry('C8')])

    def test_a_zero_capture_retry_that_is_zero_again_is_a_bar_not_an_escalation(self):
        history = self.history(self.entry('C1', 'C1', captured=0, spam=0, bank=0),
                               self.entry('C1', 'C1#2', captured=0, spam=0, bank=0))
        rows, nxt, previous, _ = series.calibration_rows(self.manifest, history)
        self.assertEqual((nxt, previous), ('C2', 'C1'))                      # the slot is consumed (barred)
        # a single zero keeps the slot open for its retry
        self.assertEqual(series.calibration_rows(self.manifest, history[:1])[1], 'C1')
        def zeros(count):
            out = []
            for n in range(1, count + 1):
                out += [self.entry(f'C{n}', f'C{n}', captured=0, spam=0, bank=0),
                        self.entry(f'C{n}', f'C{n}#2', captured=0, spam=0, bank=0)]
            return out
        series.calibration_rows(self.manifest, zeros(6))                      # six zero-capture bars: all replaced
        # a seventh zero-capture bar exhausts the replacements (C14) and escalates
        with self.assertRaisesRegex(ValueError, 'escalate_to_lead'):
            series.calibration_rows(self.manifest, zeros(7))
        release = {'lead_release': dict(ruling_id='R', text_sha256='a' * 64, resets='zero_capture_escalation',
                                        after_window='C7#2', lead_signature='lead: synthetic 2026-11-08')}
        self.assertIsNone(series.calibration_rows(self.manifest, [*zeros(7), release])[1])   # a release cannot repair 8 windows

    def test_only_a_calibration_window_can_be_barred(self):
        history = self.history(*[f'C{i}' for i in range(1, 9)])
        history.append(self.entry('T1', captured=22, spam=0, bank=0, barred='u1_u3_fail'))
        with self.assertRaises(ValueError):
            series.calibration_rows(self.manifest, history)

    def test_desk_row_marks_a_u1_u3_fail_as_barred_and_replaced(self):
        manifest = series.load(__import__('pathlib').Path(__file__).resolve().parents[2])
        pack = series.pack_id('C3')
        members = [{'run_id': f'{pack}-e{o:02}', 'captured': True, 'excluded': False} for o in range(5, 23)]
        row_ = series.desk_row(manifest, 'C3', members, False)
        self.assertEqual(row_['barred'], 'u1_u3_fail')
        self.assertEqual(sum(row_['desk_eligible_benign'].values()), 0)
        self.assertIn('u1_u3_failed:window_barred_and_replaced', row_['flags'])
        self.assertNotIn('barred', series.desk_row(manifest, 'C3', members, True))


class BuilderTests(unittest.TestCase):
    def series_with(self, *, fail_at=None, verdict='GO', windows=3):
        temp = tempfile.TemporaryDirectory(prefix='jw-r22-')
        self.addCleanup(temp.cleanup)
        self.root = temp.name
        first = Scenario(temp.name, 'W1').finish()
        previous = first
        for n in range(1, windows + 1):
            s = Scenario(temp.name, f'C{n}', previous=previous)
            s.write(series.MANIFEST.as_posix(), series.raw_json(series.candidate()))
            s.next_plan['window'] = f'C{n + 1}'
            for member in s.members:
                member['pool_role'] = 'calibration'
            if n == fail_at:
                s.thermal['model_windows'][f'tiny/C{n}']['U2']['status'] = 'fail'
            if n == 3 and verdict != 'GO':
                s.sources['result']['verdict'] = verdict
            previous = s.finish()
        return previous

    def test_a_u1_u3_fail_is_derived_from_the_committed_record_and_replaces_the_window(self):
        packet = self.series_with(fail_at=2).build()
        rows = packet['calibration_windows']
        self.assertEqual([r.get('barred') for r in rows], [None, 'u1_u3_fail', None])
        self.assertEqual(rows[1]['eligible_benign'], {'spam': 0, 'bank': 0})
        self.assertEqual(packet['calibration_decision']['attempted'], 2)
        self.assertEqual(packet['calibration_decision']['barred_windows'], ['C2'])
        self.assertEqual([h.get('barred') for h in packet['series_history']], [None, 'u1_u3_fail', None])

    def test_a_non_go_terminal_result_is_a_whole_window_capture_failure(self):
        packet = self.series_with(verdict='NO_GO').build()
        self.assertEqual([r.get('barred') for r in packet['calibration_windows']],
                         [None, None, 'whole_window_capture_failure'])
        self.assertEqual(packet['calibration_decision']['replacements_used'], 1)
        # a barred window contributes NOTHING to calibration, including the members it did capture (no partial
        # use); its capture count stays disclosed and its records stay in custody (the hash-linked chain)
        rows = packet['calibration_windows']
        self.assertEqual(sum(rows[0]['eligible_benign'].values()), 2)
        self.assertEqual(rows[2]['eligible_benign'], {'spam': 0, 'bank': 0})
        self.assertGreater(rows[2]['captured_members'], 0)
        self.assertEqual(packet['calibration_decision']['eligible_by_pair'],
                         {pair: rows[0]['eligible_benign'][pair] + rows[1]['eligible_benign'][pair]
                          for pair in rows[0]['eligible_benign']})
        self.assertEqual(packet['calibration_decision']['barred_windows'], ['C3'])
        self.assertEqual(packet['window_chain'][-1]['window'], 'C3')

    def test_the_series_binds_the_arms_own_rebuild_with_a_bar_and_arms_the_next_primary_window(self):
        packet = self.series_with(fail_at=2).build()
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight'])
        self.assertEqual(packet['next_window_id'], 'C4')
        series.bind_packet(self.root, 'C4', packet, authenticated_by_rebuild=True)       # accepted
        with self.assertRaisesRegex(ValueError, 'does not bind|does not arm the next frozen window'):
            series.bind_packet(self.root, 'C9', packet, authenticated_by_rebuild=True)    # nothing owes C9 yet
        forged = deepcopy(packet)
        forged['calibration_windows'][1].pop('barred')                                   # hiding the bar refuses
        with self.assertRaises(ValueError):
            series.bind_packet(self.root, 'C4', forged, authenticated_by_rebuild=True)

    def test_an_unbarred_series_carries_no_bar(self):
        packet = self.series_with().build()
        self.assertTrue(all('barred' not in r for r in packet['calibration_windows']))
        self.assertTrue(all('barred' not in h for h in packet['series_history']))


if __name__ == '__main__':
    unittest.main()
