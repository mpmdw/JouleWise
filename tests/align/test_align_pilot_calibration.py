"""Synthetic production members; no live data or registered estimator changes."""
import argparse
import copy
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from joulewise.align.apple.pilot_analysis import alternative_residual_analysis
from scripts import align_pilot_calibration as desk
from scripts.align_pilot_alt_desk import load_members
from tests.align.test_align_pilot_alt_desk import _members, _group


def session(label, members):
    return [{**m, 'run_id': f"{label}/{m['run_id']}"} for m in copy.deepcopy(members)]


def roster(count=6, first=1):
    members = _members(count, pairs=('bank',))
    for m in members:
        m['summary']['seed'] += first-1
        m['repeat'] += first-1
        m['summary']['active_gpu_clock_mhz'] = 1000 + 10*m['summary']['seed']
    return members


def fixed_turn_members():
    members = roster()
    for m in members:
        s = m['summary']
        original = s['residual_rows']['True']
        offset = s['energy']['powermetrics:gpu_power']['joules'] - math.fsum(r['energy_j'] for r in original)
        for key in ('True', 'False'):
            s['residual_rows'][key] = s['residual_rows'][key][:10]
        s['energy']['powermetrics:gpu_power']['joules'] = math.fsum(r['energy_j'] for r in original[:10]) + offset
    return members


class TestCalibration(unittest.TestCase):
    def test_rank_algebra(self):
        for m, k in ((16, 17), (18, 19), (19, 19), (20, 20), (21, 20),
                     (38, 38), (39, 38), (40, 39)):
            with self.subTest(m=m):
                t = desk.split_threshold(list(range(m)))
                self.assertEqual((t['m'], t['rank']), (m, k))
                self.assertEqual(t['value'], k-1 if k <= m else None)
                self.assertEqual(t['flags'], ['no_finite_threshold'] if k > m else
                                 ['quantile_at_sample_max'] if k == m else [])
        self.assertEqual(desk.split_threshold([])['flags'], ['no_finite_threshold'])
        self.assertIn('nonfinite_calibration_score', desk.split_threshold([None])['flags'])

    def test_seed_parser(self):
        self.assertIsNone(desk.calibration_seeds('all'))
        self.assertEqual(desk.calibration_seeds('1,17-26'), {1, *range(17, 27)})
        for invalid in ('', '0', '26-17', 'a', '1-2-3'):
            with self.assertRaises(argparse.ArgumentTypeError):
                desk.calibration_seeds(invalid)

    def test_session_offset_and_cross_session_contrast(self):
        base = fixed_turn_members()
        later = copy.deepcopy(base)
        for m in later:
            m['summary']['seed'] += 16  # Distinct trajectory indices, same work.
        shifted = copy.deepcopy(later)
        for m in shifted:
            for rows in m['summary']['residual_rows'].values():
                for r in rows:
                    r['energy_j'] += .8  # Ten turns: constant intercept +.8 J => episode +8 J.
            m['summary']['energy']['powermetrics:gpu_power']['joules'] += 8
        unshifted = desk.calibrate(session('a', base) + session('b', later))
        shifted_result = desk.calibrate(session('a', base) + session('b', shifted))
        for a, b in zip(unshifted['pooled'], shifted_result['pooled'], strict=True):
            self.assertEqual(len(a['scores']), 12)
            for x, y in zip(a['scores'], b['scores'], strict=True):
                # Per-session intercept absorbs .8 J/turn = 8 J/episode exactly.
                # Float noise is ~1e-12 relative. 1e-6 is 1e6 times that,
                # below 1% of the 1 J attribution limit on 2000-4000 J episodes.
                self.assertTrue(math.isclose(x['score'], y['score'], rel_tol=1e-6), (x['score'], y['score']))
        cross_base = alternative_residual_analysis(session('a', base) + session('b', later))
        cross_shift = alternative_residual_analysis(session('a', base) + session('b', shifted))
        x = _group(cross_base, 'bank')['designs']['sequence']['counts_logged']['residuals']
        y = _group(cross_shift, 'bank')['designs']['sequence']['counts_logged']['residuals']
        # Same 1e-6 invariance bar; no new quantitative acceptance threshold.
        self.assertTrue(any(not math.isclose(a['score'], b['score'], rel_tol=1e-6)
                            for a, b in zip(x, y, strict=True) if a['condition'] == 'benign'))

    def test_dedup_and_seed_selection(self):
        members = roster(3)
        replay = copy.deepcopy(members[0])
        replay['run_id'] = 'replay'
        replay['summary']['energy']['powermetrics:gpu_power']['joules'] += 1_000_000
        inputs = session('first', members + [replay]) + session('second', members) + session('third', members)
        result = desk.calibrate(inputs)
        for pool in result['pooled']:
            self.assertEqual(len(pool['scores']), 3)
            self.assertEqual([r['session'] for r in pool['scores']], ['first']*3)
            self.assertEqual([r['seed'] for r in pool['scores']], [1, 2, 3])
            self.assertFalse(any('replay' in r['run_id'] for r in pool['scores']))
        excluded = desk.calibrate(inputs, desk.calibration_seeds('17-26'))
        for pool in excluded['pooled']:
            self.assertEqual(pool['scores'], [])
            self.assertEqual(pool['threshold']['m'], 0)

    def test_identical_session_values_and_clock_independence(self):
        inputs = session('first', roster(3)) + session('second', roster(3, 17))
        result = desk.calibrate(inputs)
        for row in result['sessions']:
            direct = alternative_residual_analysis([m for m in inputs if m['run_id'].startswith(row['session']+'/')])
            # Identical frozen code on identical inputs requires exact equality.
            self.assertEqual(row['values'], _group(direct, row['task_pair'])['designs'][row['design']]['counts_logged'])
        changed = copy.deepcopy(inputs)
        for m in changed:
            m['summary']['active_gpu_clock_mhz'] = None
        self.assertEqual(result, desk.calibrate(changed))
        self.assertEqual(desk.pearson([(1, 10), (2, 20), (None, 30)]), {'n': 2, 'correlation': 1.0})
        self.assertEqual(desk.pearson([(1, 10), (2, 10)]), {'n': 2, 'correlation': None})

    def test_registered_eligibility_and_configuration_separation(self):
        members = roster(3)
        excluded = copy.deepcopy(members[0])
        excluded.update(run_id='excluded', excluded=True)
        excluded['summary']['seed'] = 99
        other = _members(3, pairs=('bank',), model='synthetic-B')
        result = desk.calibrate(session('a', members + [excluded] + other))
        self.assertEqual(len(result['pooled']), 4)  # Two configurations, two designs.
        for pool in result['pooled']:
            self.assertEqual([r['seed'] for r in pool['scores']], [1, 2, 3])
            self.assertEqual({r['session'] for r in pool['scores']}, {'a'})
            self.assertTrue(all('excluded' not in r['run_id'] for r in pool['scores']))

    def test_pooled_crossings_strictness_H0_and_unavailable(self):
        curve = [{'k': 0, 'H': 0, 'score': 2}, {'k': 1, 'H': 9, 'score': 3}]
        self.assertEqual(desk.pooled_crossing(curve, 1),
                         {'status': 'above_at_H0', 'k': 0, 'H': 0, 'detection': False})
        self.assertEqual(desk.pooled_crossing(curve, 2),
                         {'status': 'detected', 'k': 1, 'H': 9, 'detection': True})
        self.assertEqual(desk.pooled_crossing(curve, 3)['status'], 'not_crossed')
        self.assertEqual(desk.pooled_crossing(curve, None)['status'], 'not_evaluated')

    def test_real_cli_three_pilots_with_pilot8_roster(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = []
            cohorts = [roster(6), roster(6, 7)]
            pilot8 = [m for m in roster(10, 17) if m['condition'] == 'benign']
            pilot8 += [m for m in roster(1) if m['condition'] == 'sabotage']
            cohorts.append(pilot8)
            for i, members in enumerate(cohorts):
                path = root/f'pilot{i}'/'inspection'/'PILOT.json'
                path.parent.mkdir(parents=True)
                path.write_text(json.dumps({'members': members, 'residual_analysis': 'unusable aggregate'}))
                paths.append(path)
            out = root/'result.json'
            command = [sys.executable, str(desk.ROOT/'scripts/align_pilot_calibration.py'), '--out', str(out)]
            for path in paths:
                command += ['--pilot', str(path)]
            completed = subprocess.run(command, text=True, capture_output=True, check=True)
            result = json.loads(out.read_text())
            self.assertEqual(completed.stdout.splitlines()[0], desk.LABEL)
            self.assertEqual(result, desk.calibrate(load_members(paths)))
            for pool in result['pooled']:
                self.assertEqual((pool['threshold']['m'], pool['threshold']['rank']), (22, 22))
                self.assertEqual(len([r for r in pool['sabotage'] if r['session'] == 'pilot2']), 1)
                for r in pool['sabotage']:
                    first = next((p for p in r['curve'] if p['score'] > pool['threshold']['value']), None)
                    self.assertEqual(r['crossing']['H'], first['H'] if first else None)
                    self.assertEqual(r['crossing']['detection'], bool(first and first['k'] > 0))
            self.assertIn('CLOCK DIAGNOSTIC ONLY', completed.stdout)
            self.assertIn('clock_Pearson benign n', completed.stdout)
            subprocess.run(command + ['--calibration-seeds', '17-26'], text=True, capture_output=True, check=True)
            selected = json.loads(out.read_text())
            for pool in selected['pooled']:
                self.assertEqual([r['seed'] for r in pool['scores']], list(range(17, 27)))
                self.assertEqual(pool['threshold']['flags'], ['no_finite_threshold'])
            # Duplicate labels are rejected by the imported loader, including CLI.
            duplicate = subprocess.run(command + ['--pilot', str(paths[0])], text=True, capture_output=True)
            self.assertNotEqual(duplicate.returncode, 0)
            self.assertIn('duplicate session label', duplicate.stderr)


if __name__ == '__main__':
    unittest.main()
