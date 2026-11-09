"""R23h hand witnesses (Opus review of r23g, lead rulings). All inputs synthetic."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.apple import thermal_desk as td
from joulewise.align.v4_analysis import analyze, engine as e, raw
from joulewise.align.v4_analysis.io import load
from joulewise.align.v4_analysis.synthetic import series
from tests.align.test_v4_r23c_engine import native_payload, write_export


def zero_retry(p, window):
    i = next(i for i, w in enumerate(p['windows']) if w['window'] == window)
    zero = copy.deepcopy(p['windows'][i])
    zero['members'] = [raw.member(Path.cwd(), m['slot'], {'captured': False}) for m in zero['members']]
    p['windows'][i]['attempt_id'] = window+'#2'
    p['windows'].insert(i, zero)
    return p


class SealedAggregateTests(unittest.TestCase):
    def test_no_sealed_aggregate_leaf_carries_a_hash_or_value(self):
        p = series(turns=4)
        p['windows'] = p['windows'][:1]
        fill, _ = analyze(p)
        aggregates = []
        def visit(value, path):
            if isinstance(value, dict):
                if value.get('status') == 'sealed' and 'run_id' not in value:
                    aggregates.append((path, value))
                for k, v in value.items():
                    visit(v, path+'/'+k)
            elif isinstance(value, list):
                for i, v in enumerate(value):
                    visit(v, path+'/'+str(i))
        visit(fill['windows'], '/windows')
        visit(fill['acceptance'], '/acceptance')
        self.assertTrue(aggregates)
        for path, value in aggregates:
            with self.subTest(path=path):
                self.assertEqual(value, {'status': 'sealed'})
        checks = fill['windows'][0]['checks'][e.D_MODEL]
        for unit in ('U1', 'U2'):
            self.assertIn('benign_only', checks[unit])
            self.assertNotEqual(checks[unit]['benign_only'].get('status'), 'sealed')
        battery = fill['windows'][0]['battery']
        for key in ('charging_members', 'unobserved_members', 'assist_members'):
            self.assertEqual(battery[key], {'status': 'sealed'})
            self.assertIsInstance(battery['benign_only'][key], int)
        # Per-member seals still commit to the whole record.
        sealed_rows = [r for r in fill['windows'][0]['eligibility'] if r.get('status') == 'sealed']
        self.assertEqual(len(sealed_rows), 2)
        self.assertTrue(all(len(r['sha256']) == 64 for r in sealed_rows))


class AttemptIdentityTests(unittest.TestCase):
    def test_not_counted_attempt_rows_never_collide_with_counted_retry(self):
        p = zero_retry(series(turns=4), 'C3')
        fill, _ = analyze(p)
        for desk in ('dc_secondary', 'cache_diagnostics', 'realized_counts'):
            with self.subTest(desk=desk):
                rows = fill[desk]
                keys = [(r.get('attempt_id'), r['run_id']) for r in rows]
                self.assertEqual(len(keys), len(set(keys)))
                zero_rows = [r for r in rows if r.get('attempt_id') == 'C3#1']
                retry_rows = [r for r in rows if r.get('attempt_id') == 'C3#2']
                self.assertTrue(retry_rows)
                self.assertTrue(all(r.get('captured') is False for r in zero_rows))
                self.assertFalse(any(r.get('captured') is False for r in retry_rows))
                if desk != 'dc_secondary':
                    self.assertEqual(len(zero_rows), 22)
        sabotage = {m['slot']['run_id'] for m in p['windows'][2]['members']
                    if m['slot']['series_role'] == 'sabotage'}
        dc = [(r['attempt_id'], r.get('captured', True)) for r in fill['dc_secondary']
              if r['run_id'] in sabotage and r['window'] == 'C3']
        self.assertEqual(sorted(dc), sorted([('C3#1', False)]*2+[('C3#2', True)]*2))

    def test_trailing_not_counted_t_attempt_discloses_attempt_and_capture(self):
        p = series(turns=4)
        last = copy.deepcopy(p['windows'][-1])
        last['members'] = [raw.member(Path.cwd(), m['slot'], {'captured': False}) for m in last['members']]
        p['windows'][-1] = last
        fill, _ = analyze(p)
        rows = [r for r in fill['test']['counts_logged']['spam']['benign']['members'] if r['window'] == 'T3']
        self.assertTrue(rows)
        self.assertTrue(all(r['attempt_id'] == last['attempt_id'] and r['captured'] is False for r in rows))


class HStarDoseTests(unittest.TestCase):
    def test_off_grid_exact_doses_are_listed_and_ignored(self):
        fill, _ = analyze(series(turns=4))
        rows = [r for f in fill['fits'] if f['convention'] == 'counts_logged' and f['window'].startswith('C')
                for r in f['scores'] if r['condition'] == 'benign']
        self.assertTrue(rows)
        cutoff = fill['thresholds']['counts_logged/spam']['threshold']
        for r in rows:
            off = r['H_star']['off_grid_doses']
            exact = {v['H'] for v in r['H_grid'] if type(v['nominal_H']) is int and v['H'] == v['nominal_H']}
            self.assertEqual(off, sorted(exact - set(r['H_star']['grid'])))
            self.assertIn(0, off)
            if 300 in exact:
                self.assertIn(300, off)
        self.assertTrue(any(300 in r['H_star']['off_grid_doses'] for r in rows))
        # Listing off-grid doses never changes H* itself.
        from joulewise.align.apple import v4_estimands as est
        for f in fill['fits']:
            if f['convention'] != 'counts_logged' or not f['window'].startswith('C'):
                continue
            cut = fill['thresholds']['counts_logged/'+e.KEYS[f['pair']]]['threshold']
            for r in f['scores']:
                grid_only = [(v['H'], v['score']) for v in r['H_grid'] if v['nominal_H'] in est.H_STAR_GRID
                             and v['nominal_H'] == v['H'] and v['score'] is not None]
                self.assertEqual(r['H_star']['h_star'], est.subturn_h_star(grid_only, cut)['h_star'])
        self.assertIsNotNone(cutoff)


class RecordedSecondsTests(unittest.TestCase):
    def source(self, **overrides):
        stamp = dict(epoch_s=1767225600.25, monotonic_before_s=100.5, monotonic_after_s=100.5,
                     wall_resolution_s=1e-6, monotonic_resolution_s=1e-9)
        src = dict(captured=True, episode=dict(path='never.json', sha256='0'*64),
                   config=dict(path='never-config.json', sha256='0'*64),
                   first_record_endpoint_s=1767225601.0, stamps=[stamp])
        src.update(overrides)
        return src

    def test_text_or_bool_seconds_refuse_before_any_source_read(self):
        slot = e.roster('C1')[5]
        cases = [dict(first_record_endpoint_s='1767225601.0'), dict(first_record_endpoint_s=True)]
        for field in raw.STAMP_SECOND_FIELDS:
            stamp = dict(self.source()['stamps'][0]); stamp[field] = str(stamp[field])
            cases.append(dict(stamps=[stamp]))
        for overrides in cases:
            with self.subTest(overrides=overrides):
                with patch.object(raw, 'read_blob', side_effect=AssertionError('source opened')):
                    with self.assertRaisesRegex(ValueError, 'must be a recorded number'):
                        raw.member(Path.cwd(), slot, self.source(**overrides))

    def test_recorded_numbers_pass_the_check(self):
        slot = e.roster('C1')[5]
        for value in (1767225601.0, 1767225601):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as tmp:
                with patch.object(raw, 'read_blob', side_effect=LookupError('reached source read')):
                    with self.assertRaises(LookupError):
                        raw.member(Path(tmp), slot, self.source(first_record_endpoint_s=value))


class OwnedFlagReleaseTests(unittest.TestCase):
    def test_release_desk_export_without_owned_flags_refuses(self):
        p = native_payload()
        member = p['windows'][1]['members'][6]
        member['thermal'].pop('owned_energy_flags')
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, 'lacks owned_energy_flags'):
                load(write_export(Path(tmp), p))

    def test_not_captured_desk_member_needs_no_owned_flags(self):
        p = native_payload()
        member = p['windows'][1]['members'][6]
        member['thermal'].pop('owned_energy_flags')
        member['captured'] = False
        with tempfile.TemporaryDirectory() as tmp:
            loaded = load(write_export(Path(tmp), p))
        self.assertTrue(loaded['windows'])

    def test_legacy_seam_is_named_and_api_only(self):
        legacy = dict(energy_flags=['duty.uncovered'])
        self.assertEqual(td.legacy_episode_energy_flags(legacy), ['duty.uncovered'])
        self.assertEqual(td.screened_energy_flags(legacy), ['duty.uncovered'])
        self.assertEqual(td.screened_energy_flags({**legacy, 'owned_energy_flags': []}), [])
        self.assertIn('energy.value_unavailable', td.energy_exclusions(legacy))
        self.assertIn('duty.uncovered', td.energy_exclusions(legacy))
        self.assertNotIn('duty.uncovered', td.energy_exclusions({**legacy, 'owned_energy_flags': []}))


if __name__ == '__main__':
    unittest.main()
