"""W1 blockers (Opus build): the derived U3 bar and the B window rule.

Synthetic records only; no pilot, R1 or W1 data, no probes, no weights.
Written failing-first against align/2026-11-08-v4-r11 @ 05b6d04cb, where
validate_u3 always raised and every battery window was bar_pass=None.
"""
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.apple import thermal_desk
from joulewise.align.apple import v4_registration as reg
from scripts import align_v4_kit as kit
from tests.align.test_thermal_desk import member

PARAMS = {'series_pair_tests': 16, 'series_false_fail_budget': 0.05, 'min_pairs': 5,
          'oc_seed': 20261108, 'oc_reps': 400}
SIGNATURE = 'lead: synthetic-test 2026-11-08'
GATE = {'verdict': 'ADMIT', 'path': 'docs/align/v4/u3-gate-synthetic.md', 'sha256': 'c'*64}
RELATIVE = [-.004, -.002, .001, .002, .003, -.001, .0035, -.0025]


def pairs(relative=RELATIVE, family='30B', start=1, separation=4):
    return [dict(session=f'p{4 + i % 3}', family=family, ordinals=[start + i, start + i + separation],
                 token_identical=True, energies_j=[1000 * (1 - r / 2), 1000 * (1 + r / 2)])
            for i, r in enumerate(relative)]


def d_transfer(r=.002):
    return [dict(session='R1', family='D', ordinals=[2, 3], token_identical=True,
                 energies_j=[30000 * (1 - r / 2), 30000 * (1 + r / 2)])]


def signed_bar(transfer=(), relative=RELATIVE, params=PARAMS, synthetic=False):
    bar = reg.derive_u3(pairs(relative), {'pairs.json': 'a'*64}, parameters=dict(params),
                        transfer_pairs=list(transfer), synthetic=synthetic)
    return reg.sign_u3(bar, lead_signature=SIGNATURE, gate=dict(GATE))


class U3DerivationTests(unittest.TestCase):
    def test_signed_derived_bar_is_admitted(self):
        bar = signed_bar(d_transfer())
        self.assertIs(reg.validate_u3(bar), bar)
        self.assertEqual(bar['status'], 'registered')
        self.assertEqual(bar['scope'], {'30B': 'source', 'D': 'not_refuted'})
        self.assertGreater(reg.u3_margin(30000, bar, model='Qwen3.8-27B-8bit'), 0)

    def test_quantile_controls_the_series_false_fail_including_scale_uncertainty(self):
        bar = signed_bar()
        n, q = bar['n'], bar['series_quantile_q']
        self.assertAlmostEqual(reg.u3_series_false_fail(q, n, 16), .05, places=9)
        # Predictive per-pair rate is the Student-t(n) tail: P(|t_10| > 2.228139) = .05.
        self.assertAlmostEqual(reg.u3_per_pair_false_fail(2.228139, 10), .05, places=5)
        self.assertLess(bar['per_pair_false_fail'], .05 / 16 * 1.5)
        # The bar is not a normal-theory constant: small n widens it, larger N widens it.
        self.assertGreater(reg.u3_quantile(5, 16, .05), reg.u3_quantile(40, 16, .05))
        self.assertGreater(reg.u3_quantile(12, 24, .05), reg.u3_quantile(12, 5, .05))
        for k in (3, 2.576):
            self.assertNotAlmostEqual(q, k, places=2)

    def test_scale_is_rms_about_zero_so_drift_widens_and_is_never_credited(self):
        drifted = [r + .003 for r in RELATIVE]
        a = reg.derive_u3(pairs(), {'x': 'a'*64}, parameters=dict(PARAMS))
        b = reg.derive_u3(pairs(drifted), {'x': 'a'*64}, parameters=dict(PARAMS))
        self.assertAlmostEqual(a['sample_sd_relative'], b['sample_sd_relative'], places=12)
        self.assertGreater(b['rms_relative_scale'], a['rms_relative_scale'])
        self.assertAlmostEqual(b['rms_relative_scale'],
                               math.sqrt(sum(r * r for r in b['signed_relative_differences']) / b['n']), places=12)

    def test_inputs_are_separated_identical_work_from_one_family(self):
        good = pairs()
        for change in ('adjacent', 'divergent', 'zero_energy', 'no_family', 'duplicate', 'mixed', 'few'):
            bad = deepcopy(good)
            if change == 'adjacent': bad[0]['ordinals'] = [1, 3]
            if change == 'divergent': bad[0]['token_identical'] = False
            if change == 'zero_energy': bad[0]['energies_j'] = [0, 1]
            if change == 'no_family': del bad[0]['family']
            if change == 'duplicate': bad.append(deepcopy(bad[0]))
            if change == 'mixed': bad[0]['family'] = 'D'
            if change == 'few': bad = bad[:4]
            with self.subTest(change=change), self.assertRaises(ValueError):
                reg.derive_u3(bad, {'x': 'a'*64}, parameters=dict(PARAMS))
        # Transfer pairs may be adjacent (R1's D_spam a/b run back to back) but must be another family.
        reg.derive_u3(good, {'x': 'a'*64}, parameters=dict(PARAMS), transfer_pairs=d_transfer())
        with self.assertRaises(ValueError):
            reg.derive_u3(good, {'x': 'a'*64}, parameters=dict(PARAMS),
                          transfer_pairs=[{**d_transfer()[0], 'family': '30B'}])

    def test_parameters_are_lead_frozen_with_no_default(self):
        with self.assertRaises(TypeError):
            reg.derive_u3(pairs(), {'x': 'a'*64})
        for change in ({'series_false_fail_budget': .5}, {'series_pair_tests': 0}, {'min_pairs': 2},
                       {'series_false_fail_budget': 1}, {'k': 3}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                reg.derive_u3(pairs(), {'x': 'a'*64}, parameters={**PARAMS, **change})

    def test_validator_refuses_anything_but_a_recomputing_signed_bar(self):
        bar = signed_bar(d_transfer())
        derived = reg.derive_u3(pairs(), {'pairs.json': 'a'*64}, parameters=dict(PARAMS))
        historical_k3 = {'schema': 'joulewise.align_v4.u3_bar.v1', 'k': 3, 'status': 'registered',
                         'lead_signature': SIGNATURE, 's_rel': .001}
        cases = {'pending_v1': historical_k3, 'unsigned': derived,
                 'bad_signature': {**bar, 'lead_signature': kit.UNSIGNED},
                 'no_gate': {**bar, 'independent_gate': None},
                 'refused_gate': {**bar, 'independent_gate': {**GATE, 'verdict': 'REFUSE'}},
                 'gate_outside_v4': {**bar, 'independent_gate': {**GATE, 'path': 'tmp/gate.md'}},
                 'edited_bar': {**bar, 'relative_bar': bar['relative_bar'] * 1.5},
                 'k3_quantile': {**bar, 'series_quantile_q': 3.0},
                 'edited_scale': {**bar, 'rms_relative_scale': bar['rms_relative_scale'] * 2},
                 'edited_scope': {**bar, 'scope': {'30B': 'source', 'D': 'source'}},
                 'edited_pair': {**bar, 'pairs': [{**bar['pairs'][0], 'energies_j': [1000, 1001]}, *bar['pairs'][1:]]},
                 'edited_parameters': {**bar, 'parameters': {**PARAMS, 'series_pair_tests': 4}},
                 'edited_oc': {**bar, 'operating_characteristics': {
                     **bar['operating_characteristics'],
                     'series_false_fail': {**bar['operating_characteristics']['series_false_fail'],
                                           'heavy_tail_t4': 0.0}}},
                 'wrong_procedure': {**bar, 'procedure': 'k3'},
                 'synthetic_label': {**bar, 'synthetic': True}}
        for name, candidate in cases.items():
            with self.subTest(name=name), self.assertRaises(ValueError):
                reg.validate_u3(candidate)
        synthetic = signed_bar(synthetic=True)
        self.assertIs(reg.validate_u3(synthetic, allow_synthetic=True), synthetic)

    def test_gate_report_bytes_bind_when_root_is_given(self):
        bar = signed_bar()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / GATE['path']
            path.parent.mkdir(parents=True)
            path.write_text('synthetic gate\n')
            with self.assertRaisesRegex(ValueError, 'drift'):
                reg.validate_u3(bar, root=root)
            good = {**bar, 'independent_gate': {**GATE, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}}
            self.assertIs(reg.validate_u3(good, root=root), good)

    def test_transfer_can_refute_but_absence_never_qualifies(self):
        self.assertEqual(signed_bar()['scope'], {'30B': 'source'})
        with self.assertRaisesRegex(ValueError, 'does not apply'):
            reg.u3_margin(30000, signed_bar(), model='Qwen3.8-27B-8bit')
        refuted = signed_bar(d_transfer(r=.05))
        self.assertEqual(refuted['scope']['D'], 'refuted')
        with self.assertRaisesRegex(ValueError, 'refuted'):
            reg.u3_margin(30000, refuted, model='qwen3.8-27b')
        self.assertAlmostEqual(reg.u3_margin(2000, refuted, model='Qwen3-30B-A3B-4bit'), 2000 * refuted['relative_bar'])
        with self.assertRaises(ValueError):
            reg.u3_margin(2000, refuted, model='unknown-model')

    def test_operating_characteristics_cover_predictive_dependence_and_transfer(self):
        oc = signed_bar(params={**PARAMS, 'oc_reps': 3000})['operating_characteristics']
        self.assertEqual(set(oc['series_false_fail']), {
            'null_normal', 'drift_0.5_sigma', 'drift_1.0_sigma', 'heavy_tail_t4', 'dependence_rho_0.3',
            'transfer_scale_0.5', 'transfer_scale_1.5', 'transfer_scale_2.0'})
        # Seeded Monte Carlo agrees with the quadrature under the model (3 SE).
        self.assertLess(abs(oc['series_false_fail']['null_normal'] - .05), 3 * math.sqrt(.05 * .95 / 3000))
        self.assertGreater(oc['series_false_fail']['heavy_tail_t4'], .05)
        self.assertGreater(oc['series_false_fail']['transfer_scale_2.0'], oc['series_false_fail']['transfer_scale_1.5'])
        self.assertLess(oc['series_false_fail']['transfer_scale_0.5'], .05)
        self.assertGreater(oc['per_pair_detection']['shift_8_sigma'], .95)
        self.assertEqual(reg.u3_operating_characteristics(dict(PARAMS), 8),
                         reg.u3_operating_characteristics(dict(PARAMS), 8))

    def test_desk_applies_the_bar_per_pair_and_never_falls_back(self):
        bar = signed_bar(d_transfer())
        width = bar['relative_bar'] * 30000
        a, b = member('a', energy=30000), member('b', energy=30000 + .5 * width)
        c = member('c', energy=30000 + 1.5 * width)
        for m in (a, b, c):
            m['model'] = 'Qwen3.8-27B-8bit'
        self.assertEqual(thermal_desk.acceptance([a, b], pairs=[(a, b)], u3_bar=bar, v4=True)['U3']['status'], 'pass')
        self.assertEqual(thermal_desk.acceptance([a, c], pairs=[(a, c)], u3_bar=bar, v4=True)['U3']['status'], 'fail')
        refuted = signed_bar(d_transfer(r=.05))
        self.assertEqual(thermal_desk.acceptance([a, b], pairs=[(a, b)], u3_bar=refuted, v4=True)['U3']['status'],
                         'inconclusive')

    def test_registration_requires_the_signed_bar(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            directory = root / reg.REGISTRATION
            directory.mkdir(parents=True)
            gate = root / GATE['path']
            gate.parent.mkdir(parents=True)
            gate.write_text('synthetic gate\n')
            bar = {**signed_bar(), 'independent_gate': {**GATE, 'sha256': hashlib.sha256(gate.read_bytes()).hexdigest()}}
            fixture = {'turns': [{'turn': 0, 'prompt_token_ids': [1], 'output_token_ids': [2]}]}
            wp19 = reg.wp19_identity({'X': fixture, 'Y': fixture}, {'X': [[1]], 'Y': [[1]]}, fixture['turns'],
                                     live_source_sha256='b'*64)
            (directory / 'registration_receipt.json').write_text('{}')
            (directory / 'u3_bar.json').write_text(json.dumps(bar))
            (directory / 'wp19_receipt.json').write_text(json.dumps(wp19))
            with patch.object(reg, 'validate_receipt', return_value={'status': 'registered'}):
                reg.require_registration(root)
                (directory / 'u3_bar.json').write_text(json.dumps({**bar, 'synthetic': True}))
                with self.assertRaisesRegex(ValueError, 'synthetic'):
                    reg.require_registration(root)

    def test_u3_script_derives_then_signs(self):
        from scripts import align_v4_u3_bar as script
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / 'pairs.json').write_text(json.dumps({'pairs': pairs(), 'transfer_pairs': d_transfer()}))
            (tmp / 'params.json').write_text(json.dumps(PARAMS))
            self.assertEqual(script.main(['derive', '--input', str(tmp / 'pairs.json'), '--parameters',
                                          str(tmp / 'params.json'), '--output', str(tmp / 'derived.json')]), 0)
            derived = json.loads((tmp / 'derived.json').read_text())
            self.assertEqual(derived['status'], 'derived')
            self.assertEqual(set(derived['source_sha256']), {'pairs.json', 'params.json'})
            self.assertEqual(script.main(['sign', '--bar', str(tmp / 'derived.json'), '--signature', SIGNATURE,
                                          '--gate-path', GATE['path'], '--gate-sha256', GATE['sha256'],
                                          '--output', str(tmp / 'u3_bar.json')]), 0)
            self.assertEqual(reg.validate_u3(json.loads((tmp / 'u3_bar.json').read_text()))['status'], 'registered')
            with self.assertRaises(FileExistsError):
                script.main(['derive', '--input', str(tmp / 'pairs.json'), '--parameters',
                             str(tmp / 'params.json'), '--output', str(tmp / 'derived.json')])


def battery_member(name, codes=(), evaluated=True, model='Qwen3.8-27B-8bit'):
    return {'id': name, 'model': model, 'flags': [c for c in codes if c.startswith('battery.member_span')],
            'battery_codes': list(codes), 'battery_evaluated': evaluated}


class BatteryWindowTests(unittest.TestCase):
    def verdict(self, *members):
        return reg.desk_diagnostics(list(members))['battery_windows']['Qwen3.8-27B-8bit']

    def test_clean_window_passes(self):
        result = self.verdict(*(battery_member(str(i)) for i in range(6)))
        self.assertIs(result['bar_pass'], True)
        self.assertEqual(result['B_count'], 0)

    def test_one_charging_member_is_excluded_but_the_window_passes(self):
        result = self.verdict(battery_member('b', ['battery.member_span']), *(battery_member(str(i)) for i in range(5)))
        self.assertIs(result['bar_pass'], True)
        self.assertEqual(result['B_members'], ['b'])

    def test_two_charging_members_fail_the_window_with_the_ruled_consequence(self):
        result = self.verdict(battery_member('b1', ['battery.member_span']),
                              battery_member('b2', ['battery.member_span:in_force_publication']),
                              battery_member('ok'))
        self.assertIs(result['bar_pass'], False)
        self.assertIn('battery float not maintained', result['consequence'])
        self.assertIn('no next arm', result['consequence'])

    def test_missing_evidence_is_unavailable_never_a_pass(self):
        for members in ([battery_member('b', ['battery.member_span']), battery_member('u', ['battery.unmeasured'])],
                        [battery_member('u1', ['battery.accumulator_excursion']), battery_member('u2', ['battery.unmeasured'])],
                        [battery_member('n1', evaluated=False), battery_member('n2', evaluated=False)]):
            with self.subTest(members=[m['id'] for m in members]):
                self.assertIsNone(self.verdict(*members)['bar_pass'])
        # One possible B alone cannot breach a tolerance of one under any resolution.
        self.assertIs(self.verdict(battery_member('u', ['battery.unmeasured']), battery_member('ok'))['bar_pass'], True)

    def test_assist_is_printed_and_decides_nothing(self):
        result = self.verdict(battery_member('a1', ['battery.assist']), battery_member('a2', ['battery.assist']))
        self.assertIs(result['bar_pass'], True)
        self.assertEqual(result['assist_members_print_only'], ['a1', 'a2'])

    def session_check(self, exclusions, *, harvest=True):
        from scripts import align_v4_session as session
        bar = signed_bar(d_transfer())
        rows = [{'run_id': str(i), 'role': 'D', 'ordinal': i, 'ac_powermode': 0,
                 **({'replay_of': '5'} if i == 17 else {})} for i in (5, 17, 18)]
        records = {str(i): member(str(i), energy=30000 + (10 if i == 17 else 0)) for i in (5, 17, 18)}
        for record in records.values():
            record.update(model='Qwen3.8-27B-8bit', configuration=dict(
                max_tokens=4096, max_turns=12, deadman_s=1000, max_episode_decode_tokens=6144),
                cache_statistics={'rebuilds': 0}, cohort_identity=dict(
                    model_source='tiny', model_revision='synthetic', runtime_sha256='a'*64,
                    execution_policy_sha256='b'*64))
        members = [{'run_id': str(i), 'exclusion_codes': exclusions.get(str(i), []), 'harvest_flags': []}
                   for i in (5, 17, 18)]
        with tempfile.TemporaryDirectory() as tmp, \
             patch.object(session.pilot, '_member_rows', return_value=rows), \
             patch.object(session, 'bundle_ac_powermode', return_value=0), \
             patch('scripts.align_v4_thermal_desk.registration_evidence', return_value=(bar, {})), \
             patch('scripts.align_v4_thermal_desk.enrich_record', side_effect=lambda r, p: r), \
             patch('scripts.align_v4_thermal_desk.r1_soak_c', return_value={}), \
             patch('joulewise.align.apple.thermal_desk.read_bundle_record',
                   side_effect=lambda p: deepcopy(records[p.name])), \
             patch.object(kit, 'read_inputs', return_value={'R1': {'thermal_policy': {'delta_slow_c': 2}}}):
            if harvest:
                (Path(tmp) / 'archive/derived').mkdir(parents=True)
                (Path(tmp) / 'archive/derived/exclusions.json').write_text('{}')
            checks, report = session.powermode_desk_check(
                state={'measurement_root': tmp, 'session_root': tmp}, members=members,
                runs_root=tmp, kit_path=kit.KIT)
        return checks, report

    def test_session_desk_clean_w1_passes_b_and_u3(self):
        checks, report = self.session_check({})
        self.assertIs(checks['v4_B_bar'], True)
        self.assertIs(checks['v4_Qwen3.8-27B-8bit/W1_U3'], True)

    def test_session_desk_charging_window_fails_b(self):
        checks, report = self.session_check({'5': ['battery.member_span'], '18': ['battery.member_span']})
        self.assertIs(checks['v4_B_bar'], False)
        window = report['registration_diagnostics']['battery_windows']['Qwen3.8-27B-8bit']
        self.assertEqual(window['B_members'], ['5', '18'])

    def test_session_desk_without_harvest_record_cannot_pass_b(self):
        checks, _ = self.session_check({}, harvest=False)
        self.assertIs(checks['v4_B_bar'], False)


if __name__ == '__main__':
    unittest.main()
