"""R23d hand witnesses: W1 anchor role bound to ordinals 1-4; dead selection seam.

Every input is synthetic. The regression class re-states the reviewer's
p1-p6 probe outcomes so later rounds cannot silently move them.
"""
from collections import Counter
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.v4_analysis import analyze, dc, engine as e, raw
from joulewise.align.v4_analysis import io as reader
from joulewise.align.v4_analysis.io import canonical, digest, load
from joulewise.align.v4_analysis.synthetic import series
from tests.align.test_v4_r23_engine import w1_window, DCRowTests
from tests.align.test_v4_r23c_engine import native_payload, write_export


def w1_slots(p, target):
    w1 = next(w for w in p['windows'] if w['window'] == 'W1')
    observed = [m['slot'] for m in w1['members']]
    planned = next(w['members'] for w in p['series_manifest']['windows'] if w['window'] == 'W1')
    return {'observation': [observed], 'manifest': [planned], 'both': [observed, planned]}[target]


def w1_member(p, ordinal):
    w1 = next(w for w in p['windows'] if w['window'] == 'W1')
    return next(m for m in w1['members'] if m['slot']['ordinal'] == ordinal)


def strip_w1_anchor_prefix(p):
    for slots in w1_slots(p, 'both'):
        for slot in slots:
            if slot['ordinal'] in e.W1_ANCHOR_ORDINALS:
                slot['run_id'] = slot['run_id'].split(':', 1)[1]
    for m in next(w for w in p['windows'] if w['window'] == 'W1')['members']:
        m['thermal']['id'] = m['slot']['run_id']


class W1AnchorRoleTests(unittest.TestCase):
    def assert_refused(self, p, pattern):
        with self.assertRaisesRegex(ValueError, pattern):
            analyze(copy.deepcopy(p))
        with tempfile.TemporaryDirectory() as tmp:
            path = write_export(Path(tmp), p)
            with self.assertRaisesRegex(ValueError, pattern):
                load(path)

    def test_fully_prefixed_registered_w1_is_included_with_k12(self):
        p = native_payload()
        fill, _ = analyze(copy.deepcopy(p))
        self.assertEqual((fill['anchor_sigma_w']['K'], fill['anchor_sigma_w']['W1_anchor_block']),
                         (12, 'included'))
        with tempfile.TemporaryDirectory() as tmp:
            loaded = load(write_export(Path(tmp), p))
        fill, _ = analyze(loaded)
        self.assertEqual((fill['anchor_sigma_w']['K'], fill['anchor_sigma_w']['W1_anchor_block']),
                         (12, 'included'))

    def test_p6_w1norole_bare_and_roleless_anchors_refuse(self):
        # Reviewer probe p6 'w1norole': ordinals 1-4 lose series_role AND the prefix.
        for target in ('observation', 'manifest', 'both'):
            with self.subTest(target=target):
                p = native_payload()
                for slots in w1_slots(p, target):
                    for slot in slots:
                        if slot['ordinal'] in e.W1_ANCHOR_ORDINALS:
                            slot.pop('series_role')
                            slot['run_id'] = slot['run_id'].split(':', 1)[1]
                if target != 'manifest':
                    for m in next(w for w in p['windows'] if w['window'] == 'W1')['members']:
                        m['thermal']['id'] = m['slot']['run_id']
                self.assert_refused(p, 'W1 anchor role must be exactly ordinals 1-4')

    def test_missing_or_mismatched_role_refuses_even_with_prefix(self):
        cases = (('missing role on 2', 2, None), ('benign role on 3', 3, 'benign'),
                 ('anchor role on 5', 5, 'anchor'), ('anchor role on 17', 17, 'anchor'))
        for label, ordinal, role in cases:
            for target in ('observation', 'manifest'):
                with self.subTest(case=label, target=target):
                    p = native_payload()
                    for slots in w1_slots(p, target):
                        slot = next(s for s in slots if s['ordinal'] == ordinal)
                        if role is None:
                            slot.pop('series_role')
                        else:
                            slot['series_role'] = role
                    self.assert_refused(p, 'W1 anchor role must be exactly ordinals 1-4')

    def test_bare_w1_anchor_ids_with_anchor_role_refuse(self):
        p = native_payload()
        strip_w1_anchor_prefix(p)
        self.assert_refused(p, 'anchor run_id requires window prefix')
        # One bare anchor (mixed window) is just as invalid.
        p = native_payload()
        m = w1_member(p, 1)
        for slots in w1_slots(p, 'both'):
            slot = next(s for s in slots if s['ordinal'] == 1)
            slot['run_id'] = slot['run_id'].split(':', 1)[1]
        m['thermal']['id'] = m['slot']['run_id']
        self.assert_refused(p, 'anchor run_id requires window prefix')

    def test_strict_w1_slot_needs_integer_ordinal(self):
        p = native_payload()
        w1_member(p, 1)['slot'].pop('ordinal')
        with self.assertRaisesRegex(ValueError, 'W1 slot ordinal required'):
            analyze(p)

    def test_rule_lives_in_slot_run_id_and_raw_adapter(self):
        good = dict(ordinal=1, series_role='anchor', run_id='W1:align-pilot-v3-episodes-a-e01')
        self.assertEqual(e.slot_run_id(good, 'W1', strict=True), 'align-pilot-v3-episodes-a-e01')
        for bad in ({**good, 'series_role': None}, {**good, 'ordinal': 5},
                    {**good, 'run_id': 'align-pilot-v3-episodes-a-e01'}):
            with self.assertRaises(ValueError):
                e.slot_run_id(bad, 'W1', strict=True)
        # The raw adapter refuses before opening any member reference.
        slots = [dict(ordinal=i, series_role='anchor' if i != 2 else 'benign',
                      run_id=f'W1:align-pilot-v3-episodes-a-e0{i}') for i in (1, 2, 3, 4)]
        with patch.object(raw, 'member', side_effect=AssertionError('member read')):
            with self.assertRaisesRegex(ValueError, 'W1 anchor role'):
                raw.window(Path.cwd(), dict(members=[dict(run_id=s['run_id']) for s in slots]),
                           slots, window_id='W1')
        # C/T windows keep the frozen engine roster as the role authority.
        self.assertEqual(e.slot_run_id(dict(ordinal=5, series_role='sentinel',
            run_id='align-v4-c1-episodes-a-e05'), 'C1', strict=True), 'align-v4-c1-episodes-a-e05')

    def test_synthetic_api_remains_lenient(self):
        p = series(turns=4)
        w1 = w1_window(p)
        for m in w1['members'][:4]:
            m['slot'].pop('series_role')
        p['windows'].insert(0, w1)
        fill, _ = analyze(p)
        self.assertEqual(fill['anchor_sigma_w']['W1_anchor_block'], 'included')


class DeadSelectionSeamTests(unittest.TestCase):
    def test_loader_never_reads_or_synthesizes_selection_snapshot(self):
        p = native_payload()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = write_export(root, p)
            document = reader.strict_json(path.read_bytes())
            document['selection_source'] = dict(path='never-written.json', sha256='0'*64)
            path.write_bytes(canonical(document))
            loaded = load(path)
        self.assertNotIn('selection_desk', loaded)
        self.assertNotIn('never-written.json', [r['path'] for r in loaded['input_census']])
        fill, _ = analyze(loaded)
        self.assertEqual(fill['anchor_sigma_w']['W1_anchor_block'], 'included')

    def test_selection_only_input_still_refuses(self):
        p = series(turns=4)
        p['selection_source'] = dict(path='must-not-open.json', sha256='0'*64)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'input.json'
            path.write_bytes(canonical(p))
            with patch.object(reader, 'read_source', side_effect=AssertionError('source opened')):
                with self.assertRaisesRegex(ValueError, 'selection-only W1'):
                    load(path)
        with self.assertRaisesRegex(ValueError, 'selection-only W1'):
            analyze({**series(turns=4), 'selection_desk': dict(members=[])})


class ReviewerProbeRegressionTests(unittest.TestCase):
    """p1-p6 outcomes from the cold review, unchanged by R23d."""

    def zero_retry(self, p, window):
        i = next(i for i, w in enumerate(p['windows']) if w['window'] == window)
        zero = copy.deepcopy(p['windows'][i])
        zero['members'] = [raw.member(Path.cwd(), m['slot'], {'captured': False}) for m in zero['members']]
        p['windows'][i]['attempt_id'] = window+'#2'
        p['windows'].insert(i, zero)
        return p['windows'][i+1]

    def test_p1_t_retry_reason_comes_from_counted_attempt(self):
        p = series(turns=4)
        retry = self.zero_retry(p, 'T2')
        target = retry['members'][6]
        target['source_flags'] = ['X3']
        fill, verdict = analyze(p)
        self.assertEqual(verdict['counted_windows'], 8)
        test = fill['test']['counts_logged'][e.KEYS[target['slot']['task_pair']]]['benign']
        row = next(r for r in test['members'] if r['run_id'] == target['slot']['run_id'])
        self.assertEqual(row['reasons'], ['X3'])
        self.assertEqual((test['assigned'], test['n']), (21, 20))

    def test_p2_p2b_w1_flaws_drop_the_w1_block(self):
        flaws = (lambda m: m['thermal']['flags'].append('runtime.oom'),
                 lambda m: m['thermal']['battery']['flags'].append('battery.member_span'),
                 lambda m: m['summary'].__setitem__('seed', 12345),
                 lambda m: m['thermal']['flags'].append('episode.deadman:x'))
        for i, flaw in enumerate(flaws):
            with self.subTest(flaw=i):
                p = series(turns=4)
                w1 = w1_window(p)
                flaw(w1['members'][0])
                p['windows'].insert(0, w1)
                self.assertEqual(analyze(copy.deepcopy(p))[0]['anchor_sigma_w']['K'], 11)
                if i < 3:
                    flaw(p['windows'][1]['members'][0])
                    self.assertEqual(analyze(p)[0]['anchor_sigma_w']['K'], 10)

    def test_p3_zero_capture_does_not_reset_battery_streak(self):
        p = series(turns=4)
        for wi in (1, 2):
            p['windows'][wi]['members'][6]['thermal']['battery']['flags'].append('battery.member_span')
        self.zero_retry(p, 'C3')
        fill, _ = analyze(p)
        self.assertEqual([r['consecutive_B_failures'] for r in fill['windows'][:4]], [0, 1, 1, 2])

    def test_p4_prefixed_ids_change_no_number(self):
        base = series(turns=4)
        base['windows'].insert(0, w1_window(base))
        prefixed = copy.deepcopy(base)
        for w in prefixed['windows']:
            for m in w['members']:
                if m['slot']['series_role'] == 'anchor':
                    m['slot']['run_id'] = m['thermal']['id'] = w['window']+':'+m['slot']['run_id']
        a, _ = analyze(base)
        b, _ = analyze(prefixed)
        for key in ('thresholds', 'anchor_sigma_w', 'U4', 'benign_carriers', 'calibration'):
            self.assertEqual(canonical(a[key]), canonical(b[key]), key)
        self.assertEqual([r['score'] for f in a['fits'] for r in f['scores']],
                         [r['score'] for f in b['fits'] for r in f['scores']])

    def test_p5_dc_value_rows_and_residual_rows(self):
        case = DCRowTests()
        p = case.payload()
        p['windows'][1]['members'][7]['source_flags'] = ['X3']
        with patch.object(dc, 'capture', side_effect=case.capture):
            fill, _ = analyze(p)
        self.assertEqual(Counter((r['window'], r.get('residual_status')) for r in fill['dc_secondary']),
                         Counter({('C1', 'available'): 13, ('C1', 'no_gpu_row'): 5,
                                  ('W1', 'no_gpu_row'): 4, ('C1', None): 4, ('W1', None): 2}))
        self.assertFalse(any(k in r for r in fill['dc_secondary'] if r.get('residual_status') == 'no_gpu_row'
                             for k in ('residual_j', 'model', 'training_run_ids')))

    def test_p6_strict_c_window_refusals_unchanged(self):
        for fault, pattern in (('bare', 'anchor run_id requires window prefix'),
                               ('mixed', 'anchor run_id requires window prefix'),
                               ('wrong', 'run_id window prefix differs'),
                               ('nonanchor', 'non-anchor run_id must not have window prefix')):
            with self.subTest(fault=fault):
                p = native_payload()
                c2 = next(w for w in p['windows'] if w['window'] == 'C2')
                planned = next(w['members'] for w in p['series_manifest']['windows'] if w['window'] == 'C2')
                for m, slot in zip(c2['members'], planned):
                    o = m['slot']['ordinal']
                    for s in (m['slot'], slot):
                        if fault == 'bare' and o <= 4 or fault == 'mixed' and 2 <= o <= 4:
                            s['run_id'] = s['run_id'].split(':', 1)[1]
                        elif fault == 'wrong' and o <= 4:
                            s['run_id'] = 'C3:'+s['run_id'].split(':', 1)[1]
                        elif fault == 'nonanchor' and o == 6:
                            s['run_id'] = 'C2:'+s['run_id']
                    m['thermal']['id'] = m['slot']['run_id']
                with self.assertRaisesRegex(ValueError, pattern):
                    analyze(p)


if __name__ == '__main__':
    unittest.main()
