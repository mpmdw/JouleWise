"""Round-3 acceptance: additive disclosures, frozen registered values, allowed data only."""
import copy
import itertools
import json
import math
from pathlib import Path
import plistlib
import random
import shutil
import statistics
import tempfile
from types import SimpleNamespace
import unittest

from .support import (assert_values_agree, assert_printed, archive_available, recompute as r, bundle, dump, full_pack, run_cli)
from .test_meter import member, stream_file
from .test_rehearsals import R18
from .test_reconcile import S10

R2 = Path('/Users/edr/night-archive/independent-recompute/xcheck/r2')
PROTECTED = ('floors', 'floor_cells', 'floor_gate', 'floor_gate_unguarded', 'contrasts',
             'reported_cells', 'dominance', 'descriptive', 'p42', 'windows')


def assert_registered_equal(case, before, after):
    for key in PROTECTED:
        with case.subTest(registered_section=key):
            case.assertEqual(before[key], after[key])


def request_line(identifier, start, rhos, flagged=False, pack_model='model'):
    flags = [{'code': 'meter.supervision_fault', 'scope': {'level': 'window'}}] if flagged else []
    return {'identifier': identifier, 'first_request_epoch_s': start, 'meter_flags': flags,
            'members': {f'm{i}': {'model': pack_model, 'phases': {'request': {
                'delta_J': 100., 'rail_delta_J': rho * 100., 'rho': rho}}} for i, rho in enumerate(rhos)}}


def reconstruction_member(short=False, different=False, duplicate_support=False):
    records = [(float(i), float(i + 1), 0. if i < 7 or i > 25 else
                (30. if i == 7 else (28. if i == 14 else (10. if i == 25 else (40. if i < 14 else 20.)))))
               for i in range(35)]
    edges = {'prefill': (7.3, 14.6), 'decode': (14.6, 25.7), 'request': (7.3, 25.7)}
    if short:
        records = [(a, b, 15. if a == 7 else (10. if different and a == 8 else
                   (20. if 8 <= a < 25 else p))) for a, b, p in records]
        start = 8.1 if different else 7.8
        edges = {'prefill': (7.4, start), 'decode': (start, 25.7), 'request': (7.4, 25.7)}
    if duplicate_support:
        records = [(a, b, p * weight) for a, b, p in records for weight in (.5, .25, .25)]
    return SimpleNamespace(records=records, edges=edges,
        energies={phase: r.overlap(records, *span)[0] for phase, span in edges.items()})


class Round3ArithmeticTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)
        self.root = Path(self.tmp)

    def test_PLAN_8_2_worked_example_hard_band_flags_and_no_exclusion(self):
        values = [.78, .80, .81, .79, .82, .80, .77, .81, .80, .83]
        line = request_line('first', 1., values)
        line['members']['bad'] = {'model': 'model', 'phases': {'request': {
            'delta_J': 600., 'rail_delta_J': 640., 'rho': 640. / 600.}}}
        flag = {'code': 'meter.battery_activity', 'scope': {'level': 'member', 'run_id': 'bad'}}
        line['meter_flags'] = [flag, {'code': 'meter.duplicates', 'scope': {'level': 'window'}}]
        before = copy.deepcopy(line)
        summary = r.request_cross_check({'ALPHA': line})['windows']['ALPHA']['models']['model']
        self.assertEqual(line, before)
        self.assertEqual(summary['outside_hard_band'][0]['run_id'], 'bad')
        self.assertFalse(summary['outside_hard_band'][0]['removed_by_this_check'])
        self.assertEqual(summary['outside_hard_band'][0]['meter_flags'], [line['meter_flags'][1], flag])
        self.assertEqual(summary['plausible_n'], 10)
        assert_values_agree(self, summary['within_model_spread'], .075)
        self.assertEqual(summary['consistency'], 'consistent')
        clean = r.request_cross_check({'ALPHA': request_line('clean', 1., values)})
        summary = clean['windows']['ALPHA']['models']['model']
        assert_values_agree(self, summary['rho_median'], .80)
        assert_values_agree(self, (summary['rho_min'], summary['rho_max']), (.77, .83))
        assert_values_agree(self, summary['rho_iqr'], [.7925, .81])
        self.assertEqual(clean['boundary'], r.MACHINE_BOUNDARY)

    def test_first_clean_is_chronological_later_k_of_n_and_no_clean(self):
        lines = {'GAMMA': request_line('later', 3., [.79, .84, .81]),
                 'BETA': request_line('first-clean', 2., [.78, .82]),
                 'ALPHA': request_line('early-dirty', 1., [.2, .9], True)}
        result = r.request_cross_check(lines)
        self.assertEqual(result['central_bands']['model']['window_identifier'], 'first-clean')
        band = result['windows']['GAMMA']['models']['model']['central_band']
        self.assertEqual(band['note'], "2 of 3 member windows inside the first clean window's band")
        for line in lines.values():
            line['meter_flags'] = [{'code': 'meter.drops_excess', 'scope': {'level': 'window'}}]
        result = r.request_cross_check(lines)
        self.assertEqual(result['central_bands'], {})
        self.assertEqual(result['note'], 'no window is clean; no central band is set')

    def test_rich_idle_elapsed_weighting_not_metadata_or_trace(self):
        flags = []
        m = SimpleNamespace(path=self.root, run_id='idle', reader=r.Reader('ALPHA', flags))
        (self.root / 'rich_telemetry_idle.jsonl').write_text(''.join(json.dumps(row) + '\n' for row in (
            {'elapsed_ns': 1_000_000_000, 'rail_sum_power_w': .1},
            {'elapsed_ns': 3_000_000_000, 'rail_sum_power_w': .3})))
        assert_values_agree(self, r.rail_idle_power(m), .25)
        self.assertEqual(flags, [])

    def test_gross_meter_100_samples_and_request_B0AC_activity(self):
        for current in (0., .5):
            with self.subTest(nonzero_B0AC=current != 0):
                flags = []
                reader = r.Reader('ALPHA', flags)
                path = self.root / str(current) / 'stream-001.jsonl'
                # Battery changes only before the phase, but inside the request.
                stream_file(path, lambda t: 50. if t >= 15. else 10., lambda t: current if 19. <= t < 20. else 0.)
                stream = r.MeterStream(path, reader)
                m = member(reader)
                m.edges['request'] = (19., 22.)
                row = r.machine_member(m, 'decode', [stream], [], .045)
                self.assertEqual(row['meter']['n'], 100)
                assert_values_agree(self, row['energy_J'], 50. * 2.)
                self.assertNotIn('battery', row)
                self.assertNotIn('delta_J', row)
                self.assertEqual(row['share_label'], 'gross share')
                assert_values_agree(self, row['gross_share'], .6)
                self.assertEqual(row['battery_activity']['active'], current != 0)
                self.assertEqual(any(f['code'] == 'meter_battery_activity' for f in flags), current != 0)
                self.assertEqual(stream.fit['bin_origin'], 'device time 0 at the first kept sample')

    def test_gross_phase_has_no_idle_stage_dependency_and_four_corners(self):
        reader = r.Reader('ALPHA', [])
        path = self.root / 'stream-001.jsonl'
        stream_file(path, lambda t: 50.)
        stream = r.MeterStream(path, reader)
        m = member(reader)
        m.events = []
        row = r.machine_member(m, 'decode', [stream], [], .045)
        assert_values_agree(self, row['energy_J'], 100.)
        for corner in itertools.product((-1, 1), repeat=2):
            with self.subTest(corner=corner):
                shifted = r.machine_member(m, 'decode', [stream], [], .045, corner)
                assert_values_agree(self, shifted['energy_J'], 50. * (2. + .045 * (corner[1] - corner[0])))

    def test_nonzero_B0AC_flag_does_not_require_a_B0AV_value(self):
        reader = r.Reader('ALPHA', [])
        path = self.root / 'stream-001.jsonl'
        stream_file(path, lambda t: 50., lambda t: .5)
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        for row in rows:
            if 'smc' in row:
                row['smc'].pop('B0AV')
        path.write_text(''.join(json.dumps(row) + '\n' for row in rows))
        stream = r.MeterStream(path, reader)
        row = r.machine_member(member(reader), 'decode', [stream], [], .045)
        self.assertTrue(row['battery_activity']['active'])
        self.assertEqual(stream.battery_powers, [])

    def test_GAMMA_request_line_remains_but_no_phase_line_even_with_meter(self):
        reader = r.Reader('GAMMA', [])
        meter_dir = self.root / 'meter'
        stream_file(meter_dir / 'stream-001.jsonl', lambda t: 50.)
        m = member(reader)
        m.model = r.MODELS['ALPHA']
        dump(self.root / m.run_id / 'metadata.json', {})
        dump(self.root / 'withheld/meter.json', {'members': {m.run_id: {}}})
        roles = []
        def load_member(rid, role):
            roles.append(role)
            return m
        w = SimpleNamespace(archive=self.root, claim_root=self.root, bound_root=self.root,
            reader=reader, b={'b_op_s': .045}, flag_rows=[], harvest={'plan_id': 'gamma'},
            roster={'members': [{'run_id': m.run_id, 'kind': 'science'}]}, member=load_member)
        out = {'disclosures': {}}
        r.add_machine(out, {('GAMMA', 'decode'): {'quad': []}}, {'GAMMA': w}, meter_dir)
        line = out['disclosures']['whole_machine']['windows']['GAMMA']
        self.assertEqual(line['cells'], {})
        self.assertEqual(set(line['members'][m.run_id]['phases']), {'request'})
        self.assertEqual(roles, ['science'])

    def test_phase_cell_missing_units_count_assist_members_and_m_h(self):
        repeats = [(f'r{i}', [SimpleNamespace(run_id=f'r{i}')]) for i in range(5)]
        quads = [(f'b{i}', [SimpleNamespace(run_id=f'b{i}-{p}') for p in r.POSITIONS]) for i in range(6)]
        values = {m.run_id: {'energy_J': float(i + 1), 'gross_share': .5,
                            'battery_activity': {'active': m.run_id == 'b0-a1'}}
                  for i, (_, ms) in enumerate(repeats + quads) for m in ms}
        values['b0-b2']['energy_J'] = None
        row = r.phase_machine_mean(repeats, quads, values)
        self.assertEqual(row['missing_units_by_stratum'], {'repeat': 0, 'quad': 1})
        self.assertEqual((row['n_r'], row['n_b']), (5, 5))
        self.assertEqual(row['battery_assist_members'], ['b0-a1'])
        self.assertEqual(row['battery_assist_count'], 1)
        self.assertEqual(row['gross_share']['n'], 25)
        expected = r.reported_estimate([1., 2., 3., 4., 5.], [7., 8., 9., 10., 11.])
        self.assertEqual(row['mean_j'], expected['mean_j'])
        self.assertEqual(row['h_j'], expected['interval']['h_j'])
        self.assertNotIn('B_j', row['interval'])

    def test_single_step_known_edge_and_record_energy_conservation(self):
        edge = r.step_edge([(0., 1., 30.)], .3, 0., 40.)
        assert_values_agree(self, edge['step_fraction'], .25)
        assert_values_agree(self, 21. - edge['right_bias_j'], 28.)
        assert_values_agree(self, edge['left_model_j'] + edge['right_model_j'], 30.)
        # An observed average outside the two plateaus is clamped and rescaled.
        edge = r.step_edge([(0., 1., 60.)], .3, 0., 40.)
        assert_values_agree(self, edge['step_fraction'], 0.)
        assert_values_agree(self, edge['left_model_j'] + edge['right_model_j'], 60.)

    def test_single_step_plateaus_summed_supports_and_phase_biases(self):
        for duplicate in (False, True):
            with self.subTest(duplicate_support=duplicate):
                row = r.single_step_member(reconstruction_member(duplicate_support=duplicate))
                assert_values_agree(self, row['plateau_w'], {'idle_before': 0., 'idle_after': 0., 'prefill': 40., 'decode': 20.})
                assert_values_agree(self, row['energy_j']['prefill'], 288.)
                assert_values_agree(self, row['energy_j']['decode'], 218.)
                assert_values_agree(self, row['bias_j']['request'], row['bias_j']['prefill'] + row['bias_j']['decode'])
                self.assertEqual(set(row['edges']), {'prefill_start', 'decode_start', 'decode_end'})

    def test_short_prompt_decode_after_its_stamp_same_and_different_records(self):
        for different in (False, True):
            with self.subTest(onset_records_different=different):
                m = reconstruction_member(short=True, different=different)
                row = r.single_step_member(m)
                self.assertEqual(row['kind'], 'decode42')
                self.assertEqual(row['onset_records'], 'different' if different else 'same')
                self.assertNotIn('prefill', row['energy_j'])
                self.assertIn('prefill-p42', row['prefill']['reason'])
                assert_values_agree(self, row['edges']['decode_start']['right_model_j'], 10. if different else 4.)
                assert_values_agree(self, row['bias_j']['decode'], row['edges']['decode_start']['right_bias_j'] + row['edges']['decode_end']['left_bias_j'])

    def test_reconstructed_cell_same_units_m_h_shift_SD_ratio_and_no_B(self):
        repeats, quads = [], []
        for stratum, count in (('repeat', 6), ('quad', 5)):
            for i in range(count):
                uid = f"known-{'r' if stratum == 'repeat' else 'b'}{i+1:02}"
                ms = []
                for p in (('',) if stratum == 'repeat' else r.POSITIONS):
                    m = reconstruction_member()
                    m.run_id = uid + ('-' + p if p else '')
                    multiplier = 1. + i * .01 + (.005 if p.startswith('b') else 0.)
                    m.records = [(a, b, power * multiplier) for a, b, power in m.records]
                    m.energies = {phase: r.overlap(m.records, *span)[0] for phase, span in m.edges.items()}
                    ms.append(m)
                (repeats if stratum == 'repeat' else quads).append((uid, ms))
        cid = 'df-ph-prefill-p2048-qwen3-1p7b'
        chosen = {'repeat': repeats, 'quad': quads}
        original = r.reported_estimate([ms[0].energies['prefill'] for _, ms in repeats],
            [statistics.fmean(m.energies['prefill'] for m in ms) for _, ms in quads])
        output = {'disclosures': {}, 'reported_cells': {cid: original}}
        r.add_reconstruction(output, {('ALPHA', cid): chosen}, {})
        row = output['disclosures']['single_step_reconstruction']['cells'][cid]
        expected = r.reported_estimate([288. * (1. + i * .01) for i in range(6)],
                                      [288. * (1. + i * .01 + .0025) for i in range(5)])
        self.assertEqual((row['n_r'], row['n_b']), (6, 5))
        assert_values_agree(self, row['mean_j'], expected['mean_j'])
        assert_values_agree(self, row['h_j'], expected['interval']['h_j'])
        assert_values_agree(self, row['shift_j'], expected['mean_j'] - original['mean_j'])
        assert_values_agree(self, row['stratified_sd_ratio'], math.sqrt(
            expected['interval']['variance'] / original['interval']['variance']))
        self.assertNotIn('B_j', row['interval'])

    def test_scaled_GAMMA_D_and_outcome_acceptance_8(self):
        reference = SimpleNamespace(run_id='reference', usable=True,
            model='Qwen2.5-1.5B-Instruct-4bit', energies={'request': 10.}, edges={'request': (0., 1.)})
        cid = 'ctr-d117-decode-qwen3-1p7b-vs-qwen3-8b'
        for E_a, E_b, T_b, factor, expected_outcome in (
                (17., 20., .5, 2., 'not_resolvable'),
                (20., 17., .5, 2., 'not_resolvable'),
                (5., 8., .5, 1., 'direction_supported'),
                (5., 8., 3., 3., 'not_resolvable')):
            with self.subTest(E_a=E_a, E_b=E_b, T_b=T_b):
                windows = {pack: SimpleNamespace(members={'reference': reference},
                    neg8={'survivor_ids': ['reference'], 'allowance_j': 2. if pack == 'GAMMA' else .1},
                    exclusion_cells={}) for pack in ('ALPHA', 'BETA', 'GAMMA')}
                quads = []
                for index in range(5):
                    members = []
                    for position in r.POSITIONS:
                        side = position[0]
                        energy = (E_a if side == 'a' else E_b) + (-.5 if position[-1] == '1' else .5)
                        duration = ((.2 if position[-1] == '1' else .8) if side == 'a' else
                                    T_b + (-.2 if position[-1] == '1' else .2))
                        members.append(SimpleNamespace(run_id=f'unit-b{index + 1:02}-{position}',
                            energies={'decode': energy}, edges={'decode': (0., duration)},
                            op={'decode': {'max_abs_delta_j': .2}}))
                    quads.append((f'unit-b{index + 1:02}', members))
                selections = {('GAMMA', cid): {'quad': quads}}
                output = {key: {} for key in PROTECTED}
                output['disclosures'] = {}
                for pack in ('ALPHA', 'BETA'):
                    reported_cid = 'df-ph-decode-' + ('qwen3-1p7b' if pack == 'ALPHA' else 'qwen3-8b')
                    selections[(pack, reported_cid)] = {'repeat': [('repeat', [SimpleNamespace(
                        edges={'decode': (0., .5)})])], 'quad': []}
                    output['reported_cells'][reported_cid] = r.reported_estimate([5.] * 5, [5.] * 5, (.1, 0., .05))
                    prefix = r.MODELS[pack] + '/decode'
                    output['floor_cells'][prefix] = {'floor_abs_j': .5, 'floor_cmp_j': .5, 'floor_gate_j': .5}
                    for form in ('absolute', 'comparative'):
                        output['floors'][prefix + '/' + form] = {'allowance_j': .1, 'guarded_floor_j': .4,
                            'drift_widened_guarded_floor_j': .5}
                stats, kinds, _, _ = r.contrast_inputs(windows['GAMMA'], quads, 'decode')
                registered = r.finish_contrast(stats, 1., .5, [uid for uid, _ in quads], kinds)
                output['contrasts'][cid] = registered
                self.assertEqual(registered['outcome'], 'direction_supported')
                before = copy.deepcopy(output)
                r.add_scaled_allowance(output, selections, windows)
                assert_registered_equal(self, before, output)
                line = output['disclosures']['scaled_allowance']
                row = line['contrasts'][cid]
                self.assertEqual((row['E_a_j'], row['E_b_j']), (E_a, E_b))
                assert_values_agree(self, row['T_a_s'], .5)
                assert_values_agree(self, row['T_b_s'], T_b)
                self.assertEqual(row['factor'], factor)
                self.assertEqual(row['D_terms_j'][2], stats['D_terms_j'][2] * factor)
                assert_values_agree(self, row['scaled_allowance_j'], 2. * factor)
                self.assertEqual(row['D_terms_j'][:2], stats['D_terms_j'][:2])
                assert_values_agree(self, row['D_j'], .4 + 2. * factor)
                self.assertEqual(row['outcome'], expected_outcome)
                self.assertEqual(row['registered_outcome'], registered['outcome'])
                self.assertEqual(row['outcome_equals_primary'], factor == 1.)
                self.assertEqual(row['metrology_interval_j'], registered['metrology_interval_j'])
                assert_values_agree(self, row['decision_interval_j'], r.contrast_stats(
                    [E_b - E_a] * 5, .4 + 2. * factor)['decision_interval_j'])
                self.assertEqual(line['decision_vs_floor'][cid], factor == 1.)
                for key in ('p', 'holm_p', 'holm_reject'):
                    self.assertEqual(row[key], registered[key])
                self.assertEqual(row['floor']['attained_by'], ['ALPHA', 'BETA'])
                assert_values_agree(self, row['floor_gate_j'], .5)
                for side, energy, duration in (('a', E_a, .5), ('b', E_b, T_b)):
                    own_factor = max(1., energy / 10., duration)
                    self.assertEqual(row['sides'][side]['factor'], own_factor)
                    assert_values_agree(self, row['sides'][side]['scaled_allowance_j'], 2. * own_factor)
                if factor == 1.:
                    self.assertEqual(row['D_j'], registered['D_j'])
                    self.assertEqual(row['decision_interval_j'], registered['decision_interval_j'])

    def test_scaled_allowance_energy_duration_and_floor(self):
        primary = r.reported_estimate([20.] * 5, [20.] * 5, (1., 0., 2.))
        basis = {'E_ref_j': 10., 'T_ref_s': 1.}
        for E, T, factor in ((20., .5, 2.), (5., .5, 1.), (5., 3., 3.)):
            with self.subTest(E=E, T=T):
                self.assertEqual(r.allowance_factor(E, T, basis), factor)
                row = r.scaled_reported(primary, factor, 4.)
                assert_values_agree(self, row['interval']['kind_averages_j'][2], 2. * factor)
                assert_values_agree(self, row['interval']['B_j'], 1. + 2. * factor)
                self.assertEqual(row['mean_j'], primary['mean_j'])
                floor = r.scaled_floor({'allowance_j': 4., 'guarded_floor_j': 3., 'drift_widened_guarded_floor_j': 7.}, factor)
                assert_values_agree(self, floor['drift_widened_guarded_floor_j'], 3. + 4. * factor)
        self.assertEqual(r.scaled_reported(primary, 1., 4.)['interval'], primary['interval'])
        with self.subTest(unavailable_registered_anchor_bound=True):
            unavailable = r.reported_estimate([20.] * 5, [20.] * 5, (None, 0., 2.))
            row = r.scaled_reported(unavailable, 2., 4.)
            self.assertEqual(row['status'], 'not_computed')
            self.assertEqual(row['reason'], 'registered bound term unavailable')
            self.assertIsNone(row['interval']['B_j'])

    def test_no_excluded_reference_allowance_equal_and_scaled_basis_printed(self):
        archive = full_pack(self.root, 'ALPHA', 5)
        _, out, _ = run_cli({'ALPHA': archive}, self.root / 'out.json')
        alternative = out['disclosures']['excluded_reference_allowance']['windows']['ALPHA']
        self.assertEqual(alternative['note'], 'no excluded reference in the screen')
        assert_values_agree(self, alternative['difference_j'], 0.)
        self.assertEqual(alternative['allowance_j'], out['windows']['ALPHA']['neg8']['allowance_j'])
        basis = out['disclosures']['scaled_allowance']['windows']['ALPHA']
        assert_values_agree(self, basis['E_ref_j'], 10.)
        assert_values_agree(self, basis['T_ref_s'], 2.)
        for row in out['disclosures']['scaled_allowance']['reported_cells'].values():
            self.assertGreaterEqual(row['factor'], 1.)

    def test_scaled_line_doubles_B_floor_allowance_and_floor_gate_integration(self):
        archive = full_pack(self.root, 'ALPHA', 5)
        roster = json.loads((archive / 'derived/roster.json').read_text())
        for m in roster['members']:
            if m['kind'] != 'science':
                continue
            short = 'decode' in m['run_id']
            edges = {'request': (1., 3.), 'decode': (2., 3.), 'prefill': (1., 1.03125 if short else 2.)}
            bundle(archive / 'sources/claim-runs', m['run_id'], power=20., prompt=42 if short else 2048, edges=edges)
        _, out, _ = run_cli({'ALPHA': archive}, self.root / 'scaled.json')
        line = out['disclosures']['scaled_allowance']
        allowance = out['windows']['ALPHA']['neg8']['allowance_j']
        for cid, row in line['reported_cells'].items():
            assert_values_agree(self, row['factor'], 2.)
            assert_values_agree(self, row['scaled_allowance_j'], 2. * allowance)
            original = out['reported_cells'][cid]
            assert_values_agree(self, row['interval']['B_j'], original['interval']['B_j'] + allowance / 2.)
        for key, floor in line['floors'].items():
            assert_values_agree(self, floor['drift_widened_guarded_floor_j'], out['floors'][key]['drift_widened_guarded_floor_j'] + allowance)
        for key, cell in line['floor_cells'].items():
            assert_values_agree(self, cell['floor_gate_j'], out['floor_cells'][key]['floor_gate_j'] + allowance)

    def test_member_bound_missing_and_finite_mismatch_closed_flags(self):
        archive = full_pack(self.root, 'ALPHA', 5)
        for missing in (True, False):
            with self.subTest(missing=missing):
                path = archive / 'sources/claim-runs/fixture-decode-r01/metadata.json'
                meta = json.loads(path.read_text())
                meta['instrument_calibration']['b_fiducial_s'] = None if missing else .99
                dump(path, meta)
                flags = []
                w = r.Window('ALPHA', archive, flags)
                w.member('fixture-decode-r01')
                codes = {f['code'] for f in flags}
                self.assertIn('member_pre_bound_missing' if missing else 'member_pre_bound_mismatch', codes)
                self.assertNotIn('member_pre_bound_mismatch' if missing else 'member_pre_bound_missing', codes)
        for code in ('member_pre_bound_missing', 'meter_battery_activity'):
            self.assertIn(code, r.FLAG_CODES)
            self.assertNotIn(code, r.STOP_FLAG_CODES)


@unittest.skipUnless(archive_available(R18) and archive_available((R2 / 'r18-registered.json')), 'R18 / round-2 baseline unavailable')
class Round3RehearsalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.addClassCleanup(shutil.rmtree, cls.tmp)
        cls.rc, cls.out, cls.stdout = run_cli({'ALPHA': R18}, Path(cls.tmp) / 'r18.json', ('--member-detail',))

    def test_no_registered_R18_number_moves(self):
        self.assertEqual(self.rc, 0)
        assert_registered_equal(self, json.loads((R2 / 'r18-registered.json').read_text()), self.out)

    def test_R18_idle_request_rail_and_all_53_meter_agreements_or_cause(self):
        line = self.out['disclosures']['whole_machine']['windows']['ALPHA']
        rid = 'd117fq31p7-df-cmp-abba-ph-decode-b01-a1'
        row = line['members'][rid]['phases']['request']
        assert_values_agree(self, row['rail_idle_baseline_W'], .04690475515109604)
        assert_values_agree(self, row['rail_idle_baseline_W'], row['metadata_idle_baseline_power_w_mean'])
        assert_values_agree(self, row['rail_delta_J'], 52.395579790360834)
        archived = json.loads((R18 / 'withheld/meter.json').read_text())['members']
        mismatches = {f['scope']: f for f in self.out['flags'] if f['code'] == 'meter_request_mismatch'}
        self.assertEqual(set(mismatches), {'d117fq31p7-df-cmp-abba-ph-decode-b01-b1'})
        self.assertIn('anchor unknown', next(iter(mismatches.values()))['detail']['cause'])
        # The cross-check's +9.88 J used round 2's trace-idle baseline.
        # REG 5.8's corrected rich-idle baseline adds another .40633 J.
        assert_values_agree(self, next(iter(mismatches.values()))['detail']['rail_difference_J'], 10.286329575567528)
        self.assertEqual(len(line['members']), 53)
        for run_id, record in archived.items():
            for field in ('rail_delta_J', 'rho'):
                with self.subTest(member=run_id, field=field):
                    own = line['members'][run_id]['phases']['request'][field]
                    if run_id not in mismatches:
                        assert_values_agree(self, own, record[field], ratio=field == 'rho')
        summary = self.out['disclosures']['whole_machine']['request_cross_check']['windows']['ALPHA']['models']
        self.assertEqual(set(summary), {'Qwen3-1.7B-4bit', 'Qwen2.5-1.5B-Instruct-4bit'})
        self.assertEqual(sum(m['n_members'] for m in summary.values()), 53)

    def test_R18_gross_meter_phase_and_edge_corners(self):
        line = self.out['disclosures']['whole_machine']['windows']['ALPHA']
        row = line['members']['d117fq31p7-df-cmp-abba-ph-decode-b01-a1']['phases']['decode']
        assert_values_agree(self, row['energy_J'], 150.1952218065738)
        self.assertEqual(row['meter']['n'], 100)
        self.assertEqual(row['share_label'], 'gross share')
        for cell in line['cells'].values():
            self.assertEqual(len(cell['edge_shift_sensitivity']['corners']), 4)
            self.assertIn('gross_share', cell)

    def test_R18_F5_twenty_two_members_bias_and_corrected_prefill(self):
        members = [m for rid, m in self.out['members']['ALPHA'].items() if '-prefill-p2048-' in rid]
        self.assertEqual(len(members), 22)
        for phase, expected in (('prefill', (-1.047, -.598, -.027)),
                                ('decode', (-.657, -.070, .421)), ('request', (-1.016, -.668, -.140))):
            values = [m['single_step_reconstruction']['bias_j'][phase] for m in members]
            for statistic, target in zip((min(values), statistics.fmean(values), max(values)), expected):
                with self.subTest(phase=phase, statistic=statistic):
                    assert_printed(self, statistic, target, 3)
        corrected = [m['single_step_reconstruction']['energy_j']['prefill'] for m in members]
        assert_printed(self, statistics.stdev(corrected), .083, 3)
        assert_printed(self, statistics.fmean(corrected), 26.774, 3)
        line = self.out['disclosures']['single_step_reconstruction']
        self.assertTrue(all(row['label'] == r.RECONSTRUCTION_LABEL for row in line['cells'].values()))
        self.assertTrue(all(row['status'] == 'not_computed' and row['reason'] for row in line['p42'].values()))

    def test_R18_alternative_allowance_reduced_counts_bound_and_difference(self):
        line = self.out['disclosures']['excluded_reference_allowance']['windows']['ALPHA']
        assert_values_agree(self, line['registered_allowance_j'], 1.153521798393328)
        self.assertEqual((line['n_start'], line['n_mid'], line['n_end']), (1, 1, 2))
        self.assertEqual(line['excluded_reference_ids'], ['neg8-window-end-r2', 'neg8-window-start-r1'])
        self.assertTrue(r.finite(line['bound_j']))
        self.assertEqual(line['difference_j'], line['allowance_j'] - line['registered_allowance_j'])
        self.assertEqual(len(line['floors']), 4)
        basis = self.out['disclosures']['scaled_allowance']['windows']['ALPHA']
        self.assertEqual(basis['n'], 6)
        self.assertTrue(r.finite(basis['E_ref_j']) and r.finite(basis['T_ref_s']))


@unittest.skipUnless(archive_available((S10 / 'alpha/archive')) and archive_available((R2 / 'indep-all-detail.json')),
                     'S10 / round-2 baseline unavailable')
class Round3SyntheticArchiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.addClassCleanup(shutil.rmtree, cls.tmp)
        cls.root = Path(cls.tmp)
        cls.archives = {p: S10 / p.lower() / 'archive' for p in ('ALPHA', 'BETA', 'GAMMA')}
        cls.roots = [arg for p in cls.archives for kind in ('claim', 'bound')
                     for arg in ('--' + kind + '-runs-' + p.lower(),
                                 str(S10 / p.lower() / 'custody' / ('runs_' + kind)))]
        cls.rc, cls.out, cls.stdout = run_cli(cls.archives, cls.root / 's10.json', (*cls.roots, '--member-detail'))

    def test_no_registered_S10_number_moves(self):
        self.assertEqual(self.rc, 0)
        assert_registered_equal(self, json.loads((R2 / 'indep-all-detail.json').read_text()), self.out)

    def test_three_missing_bounds_reclassified_and_no_GAMMA_phase_line(self):
        flags = [f for f in self.out['flags'] if f['code'] == 'member_pre_bound_missing']
        self.assertEqual(len(flags), 3)
        self.assertFalse(any(f['code'] == 'member_pre_bound_mismatch' for f in self.out['flags']))
        self.assertTrue(all(not f['stops_comparison'] for f in flags))
        self.assertFalse(self.out['disclosures']['whole_machine']['windows']['GAMMA'].get('cells'))

    def test_S10_GAMMA_scaled_factors_floors_intervals_and_registered_p_values(self):
        line = self.out['disclosures']['scaled_allowance']
        basis = line['windows']['GAMMA']
        for cid, row in line['contrasts'].items():
            with self.subTest(contrast=cid):
                expected_factor = max(1., row['E_a_j'] / basis['E_ref_j'], row['E_b_j'] / basis['E_ref_j'],
                                      row['T_a_s'] / basis['T_ref_s'], row['T_b_s'] / basis['T_ref_s'])
                self.assertEqual(row['factor'], expected_factor)
                primary = self.out['contrasts'][cid]
                self.assertEqual(row['D_terms_j'][2], primary['D_terms_j'][2] * expected_factor)
                self.assertEqual(row['D_terms_j'][:2], primary['D_terms_j'][:2])
                self.assertEqual(row['D_j'], math.fsum(row['D_terms_j']))
                self.assertEqual(row['decision_interval_j'], [primary['metrology_interval_j'][0] - row['D_j'],
                                                            primary['metrology_interval_j'][1] + row['D_j']])
                for key in ('p', 'holm_p', 'holm_reject'):
                    self.assertEqual(row[key], primary[key])
                phase = 'decode' if 'decode' in cid else 'prefill'
                expected_floor = max(line['floor_cells'][model + '/' + phase]['floor_gate_j']
                                     for model in r.MODELS.values())
                self.assertEqual(row['floor_gate_j'], expected_floor)
                self.assertEqual(row['floor']['floor_gate_j'], expected_floor)
                self.assertTrue(row['floor']['attained_by'])
                self.assertEqual(row['registered_outcome'], primary['outcome'])
                self.assertEqual(line['decision_vs_floor'][cid],
                                 r.decision_beyond_floor(row, expected_floor))

    def test_two_extra_BETA_synthetic_copies_isolated_sessions_flags_and_upper_bound(self):
        args = []
        changed_rid, expected_energy_change = None, None
        for attempt in (1, 4):
            base = self.root / ('extra-' + str(attempt))
            archive = base / 'archive'
            shutil.copytree(S10 / 'beta/archive', archive)
            for name in ('harvest.json', 'derived/exclusions.json'):
                path = archive / name
                data = json.loads(path.read_text())
                data.update(claim_usable=False, attempt=attempt, plan_id='extra-beta-a' + str(attempt))
                dump(path, data)
            flag = {'code': 'calibration.bracket_acceptance_failed', 'scope': {'level': 'window'}}
            with (archive / 'derived/flags.jsonl').open('a') as file:
                file.write(json.dumps(flag) + '\n')
            claim = S10 / 'beta/custody/runs_claim'
            if attempt == 4:
                claim_copy = base / 'runs_claim'
                shutil.copytree(claim, claim_copy)
                claim = claim_copy
                roster = json.loads((archive / 'derived/roster.json').read_text())
                excluded = json.loads((archive / 'derived/exclusions.json').read_text())
                cid = 'df-ph-decode-qwen3-8b'
                uid = next(c for c in excluded['cells'] if c['cell_id'] == cid)['kept_units']['repeat'][0]
                rid = next(m['run_id'] for m in roster['members'] if any(
                    u['cell_id'] == cid and u['unit_id'] == uid for u in m.get('units', [])))
                path = claim / rid / 'raw/powermetrics.plist'
                frames = [plistlib.loads(frame.strip()) for frame in path.read_bytes().split(b'\x00') if frame.strip()]
                for frame in frames:
                    frame['processor']['cpu_power'] += 2000.
                path.write_bytes(b'\x00'.join(plistlib.dumps(frame) for frame in frames))
                changed_rid = rid
                events = [json.loads(line) for line in (claim / rid / 'events.jsonl').read_text().splitlines()]
                onset = next(e['timestamp_s'] for e in events if e['phase'] == 'decode' and e['event_type'] == 'phase_start')
                offset = next(e['timestamp_s'] for e in events if e['phase'] == 'decode' and e['event_type'] == 'phase_end')
                expected_energy_change = 2. * (offset - onset)
            args.extend(('--extra-beta', str(archive), str(claim), str(S10 / 'beta/custody/runs_bound')))
        _, changed, _ = run_cli(self.archives, self.root / 'extra.json', (*self.roots, '--member-detail', *args))
        inclusive = changed['disclosures'].pop('beta_including_removed_sessions')
        self.assertEqual(changed, self.out)
        self.assertEqual(inclusive['label'], r.BETA_INCLUSIVE_LABEL)
        self.assertEqual([s['attempt'] for s in inclusive['sessions']], [1, 4])
        self.assertTrue(all(s['claim_usable'] is False for s in inclusive['sessions']))
        for session in inclusive['sessions']:
            self.assertIn('calibration.bracket_acceptance_failed', session['harvest_flag_counts'])
            self.assertIn('claim_usable_false', session['script_flag_counts'])
            self.assertEqual(len(session['floors']), 4)
        self.assertIn('stored_energy_mismatch', inclusive['sessions'][1]['script_flag_counts'])
        changed_energy = next(f['detail']['own_j'] for f in inclusive['sessions'][1]['script_flags']
                              if f['code'] == 'stored_energy_mismatch' and f['scope'] == changed_rid + '/decode')
        assert_values_agree(self, changed_energy - self.out['members']['BETA'][changed_rid]['E_j']['decode'], expected_energy_change)
        self.assertNotEqual(inclusive['sessions'][0]['floors'], inclusive['sessions'][1]['floors'])
        self.assertEqual(inclusive['pooled']['allowance_j'], max(s['allowance_j'] for s in inclusive['pooled']['session_allowances']))
        for floor in inclusive['pooled']['floors'].values():
            self.assertGreater(floor['n'], 16)
            self.assertEqual(floor['status'], 'computed')
            self.assertTrue(math.isfinite(floor['minted_floor_j']))
            self.assertEqual(floor['corner_method'], 'triangle_inequality_upper_bound')
            self.assertGreaterEqual(floor['operative_unguarded_floor_j'], floor['point_unguarded_floor_j'])
            self.assertEqual(floor['minted_floor_j'], floor['guarded_floor_j'] + inclusive['pooled']['allowance_j'])
            self.assertIn('upper bound on the registered arithmetic, never smaller', floor['label'])


class Round3PoolTests(unittest.TestCase):
    def test_triangle_inequality_bound_dominates_exact_corners_seeded_both_forms(self):
        rng = random.Random(20261014)
        for form in ('absolute', 'comparative'):
            for case in range(60):
                n = rng.randint(5, 12)
                values = [rng.uniform(-30., 30.) for _ in range(n)]
                widths = [rng.uniform(0., 10.) if case % 10 else 0. for _ in range(n)]
                with self.subTest(form=form, case=case, n=n):
                    bound = r.corner_upper_bound(values, widths, form)
                    self.assertGreaterEqual(bound['corner_widened_unguarded_floor_j'], r.corner_max(values, widths, form))

    def test_pooled_method_keeps_exact_small_floor_and_registered_cap(self):
        for n in (5, 16, 17):
            for form in ('absolute', 'comparative'):
                values = [i * .1 for i in range(n)]
                widths = [.01 * (i + 1) for i in range(n)]
                with self.subTest(n=n, form=form):
                    registered = r.floor_estimate(values, widths, form)
                    pooled = r.pooled_floor_estimate(values, widths, form)
                    self.assertNotIn('corner_method', registered)
                    if n <= 16:
                        self.assertEqual(pooled.pop('corner_method'), 'exact_enumeration')
                        self.assertEqual(pooled, registered)
                    else:
                        self.assertEqual(registered['status'], 'not_computed')
                        self.assertEqual(registered['reason'], 'width_unavailable_or_corner_cap')
                        self.assertIsNone(registered['guarded_floor_j'])
                        self.assertEqual(pooled['corner_method'], 'triangle_inequality_upper_bound')
                        self.assertEqual(pooled['status'], 'computed')
                        assert_values_agree(self, pooled['guard'], 1.)
                        self.assertTrue(math.isfinite(pooled['guarded_floor_j']))
        invalid = r.pooled_floor_estimate([1.] * 17, [None] * 17, 'absolute')
        self.assertEqual(invalid['status'], 'not_computed')
        self.assertIsNone(invalid['guarded_floor_j'])

    def test_large_pooled_BETA_finite_minted_floor(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        windows = [r.Window('BETA', full_pack(Path(tmp) / str(i), 'BETA', 5), []) for i in range(4)]
        for index, window in enumerate(windows):
            window.neg8['allowance_j'] = float(index + 1)
        out = {'disclosures': {}}
        r.add_beta_inclusive(out, windows[0], windows[1:])
        pooled = out['disclosures']['beta_including_removed_sessions']['pooled']
        assert_values_agree(self, pooled['allowance_j'], 4.)
        self.assertEqual(len(pooled['floors']), 4)
        for floor in pooled['floors'].values():
            self.assertEqual(floor['n'], 20)
            self.assertEqual(floor['status'], 'computed')
            self.assertEqual(floor['corner_method'], 'triangle_inequality_upper_bound')
            self.assertTrue(math.isfinite(floor['minted_floor_j']))
            self.assertGreaterEqual(floor['guarded_floor_j'], floor['point_unguarded_floor_j'])
            assert_values_agree(self, floor['minted_floor_j'], floor['guarded_floor_j'] + 4.)

    def test_small_pooled_BETA_floor_hand_corner_and_own_bounds_largest_allowance(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        root = Path(tmp)
        windows = []
        for index in range(3):
            archive = full_pack(root / str(index), 'BETA', 5)
            # The third session's bound changes only its own unit widths.
            if index == 2:
                for slot in ('pre', 'post'):
                    path = archive / f'sources/claim-runs/instrument_validation/fixture-cal-{slot}/instrument_evidence.json'
                    data = json.loads(path.read_text())
                    data['b_fiducial_s'] += .01
                    dump(path, data)
            w = r.Window('BETA', archive, [])
            w.neg8['allowance_j'] = float(index + 1)
            windows.append(w)
        out = {'disclosures': {}}
        r.add_beta_inclusive(out, windows[0], windows[1:])
        pooled = out['disclosures']['beta_including_removed_sessions']['pooled']
        assert_values_agree(self, pooled['allowance_j'], 3.)
        values, widths = [], []
        cid = 'df-ph-decode-qwen3-8b'
        for w in windows:
            units = w.select(cid, 'repeat')
            values.extend(ms[0].energies['decode'] for _, ms in units)
            widths.extend(ms[0].op['decode']['max_abs_delta_j'] for _, ms in units)
        expected = 0.
        t = round(r.student_quantile(14), 3)
        for signs in itertools.product((-1, 1), repeat=15):
            shifted = [v + s * w for v, s, w in zip(values, signs, widths)]
            mean = statistics.fmean(shifted)
            expected = max(expected, max(abs(x - mean) for x in shifted),
                           t * statistics.stdev(shifted) * math.sqrt(1 + 1 / 15))
        floor = pooled['floors'][r.MODELS['BETA'] + '/decode/absolute']
        self.assertEqual(floor['n'], 15)
        self.assertEqual(floor['corner_method'], 'exact_enumeration')
        assert_values_agree(self, floor['guarded_floor_j'], expected)
        assert_values_agree(self, floor['minted_floor_j'], expected + 3.)
        self.assertEqual(floor['widths_j'], widths)
        self.assertEqual(len({u['b_op_s'] for u in floor['units']}), 2)
