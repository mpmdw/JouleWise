"""R23j hand witnesses (Opus review of r23i, lead rulings). All inputs synthetic."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from joulewise.align.v4_analysis import analyze, engine as e, raw
from joulewise.align.v4_analysis.io import load
from joulewise.align.v4_analysis.synthetic import series
from tests.align.test_v4_r23c_engine import native_payload, r24_manifest, write_export

FROZEN = Path(__file__).resolve().parents[1] / 'fixtures/align_v4/r24_series_manifest.json'


def win(p, name):
    return next(w for w in p['windows'] if w['window'] == name)


def u1_fail(w):
    for m in w['members'][6:8]:
        m['thermal']['registered_os_nonzero'] = True


def zero(w):
    z = copy.deepcopy(w)
    z['members'] = [raw.member(Path.cwd(), m['slot'], {'captured': False}) for m in z['members']]
    return z


class ReproducibleBarTests(unittest.TestCase):
    """p10's forged-bar cases refuse; evidence-backed bars stand."""

    def test_forged_bars_refuse(self):
        cases = (
            ('u1_u3_fail with passing U1-U3', dict(barred='u1_u3_fail'), 'not reproduced'),
            ('capture failure without terminal result', dict(barred='whole_window_capture_failure'),
             'needs non-GO terminal_result'),
            ('capture failure against a GO chain', dict(barred='whole_window_capture_failure',
             terminal_result=dict(verdict='GO', chain_exit_code=0)), 'needs non-GO terminal_result'),
            ('unregistered bar', dict(barred='low_m'), 'registered structural bar'),
        )
        for label, fields, pattern in cases:
            with self.subTest(case=label):
                p = series(turns=4, reserves=1)
                win(p, 'C2').update(fields)
                with self.assertRaisesRegex(ValueError, pattern):
                    analyze(p)

    def test_declared_bar_on_zero_capture_refuses(self):
        p = series(turns=4)
        z = zero(win(p, 'C1'))
        z['barred'] = 'whole_window_capture_failure'
        z['terminal_result'] = dict(verdict='NO_GO', chain_exit_code=1)
        p['windows'] = [z]
        with self.assertRaisesRegex(ValueError, 'zero-capture window is not reproducible'):
            analyze(p)

    def test_evidence_backed_bars_stand(self):
        for label, fields, recompute in (
                ('recomputed U1 fail, declared', dict(barred='u1_u3_fail'), True),
                ('recomputed U1 fail, undeclared', {}, True),
                ('non-GO verdict', dict(terminal_result=dict(verdict='NO_GO', chain_exit_code=0)), False),
                ('non-zero chain exit', dict(barred='whole_window_capture_failure',
                    terminal_result=dict(verdict='GO', chain_exit_code=7)), False)):
            with self.subTest(case=label):
                p = series(turns=4, reserves=1)
                w = win(p, 'C2')
                w.update(fields)
                if recompute:
                    u1_fail(w)
                fill, _ = analyze(p)
                self.assertEqual(fill['calibration']['barred_windows'], ['C2#1'])
                self.assertEqual(fill['calibration']['decision'], 'calibration_complete')
                self.assertEqual(fill['ledger'][1]['barred'], 'u1_u3_fail' if recompute else
                                 'whole_window_capture_failure')


class ReleaseTerminalResultTests(unittest.TestCase):
    def test_captured_c_window_without_terminal_result_refuses(self):
        p = native_payload()
        with tempfile.TemporaryDirectory() as tmp:
            path = write_export(Path(tmp), p)
            document = json.loads(path.read_text())
            next(w for w in document['windows'] if w['window'] == 'C3').pop('terminal_result_source')
            path.write_text(json.dumps(document))
            with self.assertRaisesRegex(ValueError, 'lacks terminal_result_source: C3'):
                load(path)

    def test_zero_capture_attempt_needs_no_terminal_result(self):
        p = native_payload()
        i = next(i for i, w in enumerate(p['windows']) if w['window'] == 'C3')
        z = zero(p['windows'][i])
        p['windows'][i]['attempt_id'] = 'C3#2'
        p['windows'].insert(i, z)
        with tempfile.TemporaryDirectory() as tmp:
            path = write_export(Path(tmp), p)
            document = json.loads(path.read_text())
            next(w for w in document['windows'] if w['attempt_id'] == 'C3#1').pop('terminal_result_source')
            path.write_text(json.dumps(document))
            loaded = load(path)
        fill, _ = analyze(loaded)
        self.assertEqual(fill['calibration']['zero_capture_refusals'], 1)

    def test_terminal_result_bar_from_release_source(self):
        p = native_payload()
        win(p, 'C2')['terminal_result'] = dict(verdict='HOLD', chain_exit_code=0)
        with tempfile.TemporaryDirectory() as tmp:
            loaded = load(write_export(Path(tmp), p))
        fill, _ = analyze(loaded)
        self.assertEqual(fill['ledger'][1]['barred'], 'whole_window_capture_failure')


class ReleaseManifestTests(unittest.TestCase):
    def test_full_r24_allocation_loads(self):
        with tempfile.TemporaryDirectory() as tmp:
            loaded = load(write_export(Path(tmp), native_payload()))
        self.assertEqual(tuple(w['window'] for w in loaded['series_manifest']['windows']), e.R24_SERIES_ORDER)
        fill, _ = analyze(loaded)
        self.assertEqual(fill['calibration']['decision'], 'calibration_complete')

    def test_legacy_or_partial_manifests_refuse_on_release(self):
        for label, keep in (('legacy R15 11 + W1', ('W1',)+e.LEGACY_R15_MANIFEST_ORDER),
                            ('no W1', e.ORDER), ('one reserve short', ('W1',)+e.ORDER[:13]+e.TEST_ORDER)):
            with self.subTest(case=label):
                p = native_payload()
                p['series_manifest']['windows'] = [w for w in p['series_manifest']['windows']
                                                   if w['window'] in keep]
                with tempfile.TemporaryDirectory() as tmp:
                    with self.assertRaisesRegex(ValueError, 'full R24 allocation'):
                        load(write_export(Path(tmp), p))

    def test_legacy_shape_survives_only_on_the_named_api_seam(self):
        p = native_payload()
        p['series_manifest']['windows'] = [w for w in p['series_manifest']['windows']
                                           if w['window'] in ('W1',)+e.LEGACY_R15_MANIFEST_ORDER]
        fill, _ = analyze(p)
        self.assertEqual(fill['calibration']['decision'], 'calibration_complete')

    def test_engine_roster_reproduces_the_frozen_r24_manifest(self):
        data = FROZEN.read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(), e.R24_SERIES_MANIFEST_SHA256)
        frozen = json.loads(data)
        self.assertEqual(tuple(w['id'] for w in frozen['windows']), e.R24_SERIES_ORDER)
        compared = 0
        for w in frozen['windows']:
            if w['id'] == 'W1':
                # W1 ordinals 1-4 are the registered anchors: the C/T anchor seeds.
                anchors = {s['ordinal']: s for s in e.roster('C1') if s['series_role'] == 'anchor'}
                for m in w['members']:
                    if m['ordinal'] in e.W1_ANCHOR_ORDINALS:
                        a = anchors[m['ordinal']]
                        self.assertEqual((m['pair'], m['condition'], m['model_id'], m['episode_seed']),
                                         (a['task_pair'], a['condition'], a['model_id'], a['expected_episode_seed']))
                self.assertEqual(sorted(m['ordinal'] for m in w['members']), list(range(1, 19)))
                continue
            expected = {s['ordinal']: s for s in e.roster(w['id'])}
            self.assertEqual(set(expected), {m['ordinal'] for m in w['members']})
            for m in w['members']:
                s = expected[m['ordinal']]
                self.assertEqual((m['pair'], m['condition'], m['model_id'], m['seed_index'], m['episode_seed']),
                                 (s['task_pair'], s['condition'], s['model_id'], s['seed_index'],
                                  s['expected_episode_seed']), (w['id'], m['ordinal']))
                compared += 1
        self.assertEqual(compared, 17*22)


if __name__ == '__main__':
    unittest.main()
