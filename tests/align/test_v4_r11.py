"""R11 Track 1 regressions. Synthetic rows only; no hardware or data discovery."""
from copy import deepcopy
import unittest
from unittest.mock import patch

from joulewise.align.apple import v4_registration as reg, v4_estimands as est
from joulewise.align.apple import thermal_desk, thermal_gates
from scripts import align_v4_kit as kit, align_w1_budget_procedure as proc
from tests.align.test_v4_kit import ready_inputs
from tests.align.test_w1_kit_r10 import eight_bit_case, signed_receipt, arm_receipt
from tests.align.test_thermal_desk import contrast, member


def counted(slots, counts=(2048, 2048, 2048, 2048)):
    for row in slots['deadman_budget']:
        row.update(turn_decode_counts=list(counts), turn_completed=[True]*len(counts),
                   turn_counts_source_sha256='c'*64, decode_tokens=sum(counts),
                   admitted_turns=len(counts), x7=False)
    return slots


class R11Tests(unittest.TestCase):
    def test_battery_uses_required_instant_current_not_optional_average(self):
        good = dict(passed=True, probe_error=False, external_connected=True, is_charging=False,
                    update_age_s=1, current_capacity_pct=99, instant_amperage_ma=0, amperage_ma=None)
        topup = {'completed_at_epoch_s': 1000., 'source': 'synthetic'}
        self.assertTrue(reg.battery_arm(good, 'synthetic', topup, now_epoch_s=1060.)['admitted'])
        self.assertFalse(reg.battery_arm({**good, 'instant_amperage_ma': None, 'amperage_ma': 0},
                                         'synthetic', topup, now_epoch_s=1060.)['admitted'])

    def test_u3_diagnostics_do_not_install_a_constant_or_a_bar(self):
        # W1-BLOCKERS (Opus): a derivation is unsigned until the lead signs it
        # with an independent gate; no k or fitted-normal constant is emitted.
        pairs = [dict(session='synthetic', family='synthetic', ordinals=[i, i+3], token_identical=True,
                      energies_j=[1000, 1000+i]) for i in (1, 2, 3)]
        pending = reg.derive_u3(pairs, {'synthetic': 'a'*64}, parameters=dict(series_pair_tests=16, series_false_fail_budget=.05, min_pairs=3, oc_seed=1, oc_reps=100))
        self.assertEqual(pending['status'], 'derived')
        self.assertNotIn('k', pending)
        self.assertNotIn('normal_theory_false_fail_per_pair', pending)
        with self.assertRaisesRegex(ValueError, 'PENDING'):
            reg.validate_u3(pending)

    def test_partial_native_x_cannot_pass_wp19(self):
        fixtures = {arm: {'turns': [{'turn': i, 'prompt_token_ids': [i], 'output_token_ids': [i+1]}
                                   for i in range(3)]} for arm in ('X', 'Y')}
        rendered = {a: [t['prompt_token_ids'] for t in f['turns']] for a, f in fixtures.items()}
        receipt = reg.wp19_identity(fixtures, rendered, fixtures['X']['turns'][:1], live_source_sha256='b'*64)
        self.assertEqual(receipt['verdict'], 'fail')
        self.assertEqual(receipt['contrast_predeclared'], 'INCONCLUSIVE: identity broken')

    def test_delivery_cannot_be_borrowed_from_the_other_template(self):
        runs = contrast(effect=15, noise=.1)
        for i, r in enumerate(runs):
            r.update(stage='a' if i < 4 else 'b', admission_slow_c=40,
                     g1_wait_s_by_turn=[1, 1] if r['template']=='X' else [0, 0])
        result = thermal_desk.deciding_experiment(runs, v4=True, delta_slow_c=2)
        self.assertEqual(result['verdict'], 'INCONCLUSIVE')
        self.assertFalse(result['delivery']['by_template']['Y']['delivered'])

    def test_contrast_impossible_or_missing_episode_uses_zero_cap_and_nonveto(self):
        _, slots = ready_inputs()
        for x in ({}, dict(status='measured', g0_outcome='released', g0_wait_s=10,
                            admitted_turns=12, x7=False,
                            phases_s=dict(G1=0, H=0, prefill=0, decode=2000, tool=0))):
            result = kit.w1_contrast_g0_cap({**slots, 'x_g': x}, 12)
            self.assertEqual(result['value_s'], 0)
            self.assertTrue(result['predeclared'].startswith('INCONCLUSIVE'))
            self.assertIn('predecessor', result['history_disclosure'])

    def test_contrast_failure_never_vetoes_an_otherwise_valid_d_receipt(self):
        inputs, slots = eight_bit_case()
        slots['x_g']['phases_s']['decode'] = 2000
        receipt = signed_receipt(slots)
        # The D receipt stays verifiable; the contrast conclusion is explicitly unavailable.
        derived = kit.verify_ruling_1f_receipt(receipt, slots, inputs['R1']['T_dead'], 12)
        self.assertTrue(derived['contrast']['predeclared'].startswith('INCONCLUSIVE'))

    def test_contrast_cap_record_is_required_on_receipt_and_no_receipt_paths(self):
        inputs, slots = ready_inputs()
        fit = kit.w1_contrast_g0_cap(slots, 12)
        policy = inputs['R1']['thermal_policy']
        policy.update(contrast_g0_cap_s=fit['value_s'], contrast_fit=fit)
        runtime = kit.gate_policy_fields(policy, role='contrast')
        runtime.update(heavy=False, per_turn=True, window_reference={'role': 'capture'})
        self.assertEqual(thermal_gates.validate_gate_policy(runtime)['g0_cap_s'], 0)
        self.assertNotIn('contrast_fit', kit.gate_policy_fields(policy, role='D'))
        runtime['heavy'] = True
        with self.assertRaises(ValueError):
            thermal_gates.validate_gate_policy(runtime)

    def test_bare_duty_fallback_and_unexpressible_steps_are_refused(self):
        inputs, slots = ready_inputs()
        slots['duty_bar'].update(verdict='fail', **{'pass': False})
        slots['deadman_budget'][0]['duty_bar'].update(verdict='fail', **{'pass': False})
        for step in (1, 2, 3):
            slots['duty_bar']['lead_fallback'] = dict(step=step, authority='synthetic')
            with patch.object(kit, 'check_r1_budget_and_policy'), self.subTest(step=step), \
                 self.assertRaisesRegex(ValueError, 'remeasured|qualified|fallback'):
                kit.check_r1_evidence(inputs, slots)

    def test_r0_digest_is_bound_to_sensor_policy(self):
        inputs, slots = ready_inputs()
        inputs['R0']['record_sha256'] = 'f'*64
        with self.assertRaisesRegex(ValueError, 'R0.*record_sha256|r0_sha256'):
            kit.require_ready(inputs, slots)

    def test_chosen_budget_counts_actual_turns_and_keeps_missing_evidence_unresolved(self):
        _, slots = ready_inputs()
        counted(slots, (4096, 4096, 100))
        small = kit.turn_opportunity(slots, 6144)
        self.assertEqual(small['status'], 'fail')
        self.assertEqual([r['admitted_at_B_D'] for r in small['runs']], [2]*3)
        self.assertEqual(kit.turn_opportunity(slots, 9216)['status'], 'pass')
        del slots['deadman_budget'][0]['turn_completed']
        self.assertEqual(kit.turn_opportunity(slots, 6144)['status'], 'inconclusive')

    def test_procedure_routes_two_turn_opportunity_to_four_bit(self):
        _, slots = eight_bit_case()
        counted(slots, (4096, 4096, 100))
        decision = proc.decide(slots, 12)
        self.assertEqual(decision['step'], 'R10-2(b)')
        self.assertEqual(decision['turn_opportunity']['status'], 'fail')

    def test_sentinel_fallback_has_no_silent_single_run_reference(self):
        r = member('18')
        r.update(role='D', ordinal=18, status='completed', turns=3, x_flags=[])
        sentinel = reg.desk_diagnostics([r])['sentinel']
        self.assertEqual(sentinel['reference_status'], 'unresolved')
        self.assertNotIn('single ordinal-18 run', sentinel['E_ref_basis'])
        missing = reg.desk_diagnostics([])['sentinel']
        self.assertNotIn('extension windows required', missing['E_ref_basis'])

    def test_h_star_is_strict_and_undefined_crossings_stay_undefined(self):
        self.assertIsNone(est.subturn_h_star([(128, 1)], 1)['h_star'])

    def test_calibration_rank_and_fpr_are_one_rule(self):
        rows = [{'window': 'D1', 'score': float(i)} for i in range(39)]
        result = est.conformal_threshold_diagnostics(rows, alpha=.025)
        self.assertEqual(result['rank'], 39)
        self.assertAlmostEqual(result['marginal_fpr_bound'], .025)
        result = est.conformal_threshold_diagnostics(rows, alpha=.05)
        self.assertEqual(result['rank'], 38)
        self.assertAlmostEqual(result['marginal_fpr_bound'], .05)

    def test_carrier_uses_untouched_h0_and_allows_only_strict_alarms(self):
        rows = [dict(pair='spam', window=f'D{i//8}', carrier=str(i), h=h, score=float(i)+h)
                for i in range(40) for h in (0, 128)]
        curve = est.benign_carrier_curve(rows, bootstrap_replicates=0)['pairs']['spam']
        self.assertEqual(dict(curve['curve'])[128], 1)
        self.assertEqual(dict(curve['curve'])[0], 1/40)
        tied = [{**r, 'score': 1.0} for r in rows]
        self.assertEqual(dict(est.benign_carrier_curve(tied, bootstrap_replicates=0)
                              ['pairs']['spam']['curve'])[128], 0)
        few = [r for r in rows if r['carrier'] != '39']
        result = est.benign_carrier_curve(few, bootstrap_replicates=0)['pairs']['spam']
        self.assertEqual(result['status'], 'insufficient_calibration')
        self.assertIsNone(result['H50'])
        self.assertIsNone(result['curve'][0][1])

    def test_carrier_doses_are_actual_and_duplicate_rows_refuse(self):
        rows = [dict(pair='spam', window='D1', carrier=str(i), h=h, score=0.)
                for i in range(40) for h in (0, 127)]
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            est.benign_carrier_curve(rows+rows[:1], bootstrap_replicates=0)
        rows[1]['h'] = 128.5
        with self.assertRaisesRegex(ValueError, 'dose|integer'):
            est.benign_carrier_curve(rows, bootstrap_replicates=0)

    def test_crossings_use_observed_doses_and_censored_bootstraps_are_counted(self):
        rows = [dict(pair='spam', window=f'D{i//8}', carrier=str(i), h=h, score=h)
                for i in range(40) for h in (0, 127)]
        result = est.benign_carrier_curve(rows, bootstrap_replicates=8)['pairs']['spam']
        self.assertEqual(result['H50'], 127)
        self.assertEqual(result['bootstrap_undefined_replicates']['H50'], 0)

    def test_four_slots_do_not_bind_model_stack_and_execution_policy(self):
        config = dict(max_episode_decode_tokens=6144, deadman_s=1000, max_tokens=4096, max_turns=12)
        self.assertFalse(est.d_configuration_assertion([{'configuration': config}])['instrument_ok'])
        identity = dict(model_source='tiny', model_revision='synthetic', runtime_sha256='a'*64,
                        execution_policy_sha256='b'*64)
        rows = [dict(configuration=config, cohort_identity=identity)]*2
        self.assertTrue(est.d_configuration_assertion(rows)['instrument_ok'])
        rows[1] = dict(configuration=config, cohort_identity={**identity, 'runtime_sha256': 'c'*64})
        self.assertFalse(est.d_configuration_assertion(rows)['instrument_ok'])

    def test_no_invented_offload_freshness_constant(self):
        from scripts import align_v4_session as session
        config = {'offloads': [{'label': 'synthetic'}]}
        gate = lambda c: {'status': 'pass', 'offloads': [{'label': 'synthetic', 'pass': True,
                                                       'observed': [{'sha256': 'a'*64}]}]}
        with self.assertRaisesRegex(ValueError, 'freshness'):
            session.daytime_offload_receipt(config, now=lambda: 1000, gate=gate)

    def test_v4_never_falls_back_to_v3_u3_margin(self):
        a, b = member('a'), member('b')
        report = thermal_desk.acceptance([a, b], pairs=[(a, b)], v4=True)
        self.assertEqual(report['U3']['status'], 'inconclusive')

    def test_bundle_identity_includes_actual_runtime_and_effective_policy(self):
        from joulewise.align.apple.workload import EpisodeSpec
        spec = EpisodeSpec(task_factory='tiny:task', condition='benign', seed=1, max_tokens=8,
                           max_turns=12, temperature=1)
        runtime = dict(mlx_version='synthetic', mlx_lm_version='synthetic', model_artifact_identity={'sha256': 'a'*64})
        identity = reg.cohort_identity({'model': {'source': 'tiny', 'revision': 'synthetic'}}, spec, runtime)
        self.assertEqual(identity['model_source'], 'tiny')
        self.assertIsNotNone(identity['runtime_sha256'])
        self.assertIsNone(reg.cohort_identity({'model': {}}, spec, {})['runtime_sha256'])

    def test_desk_combines_frozen_contrast_fit_and_identity_predeclarations(self):
        from scripts import align_v4_thermal_desk as desk
        self.assertEqual(desk.contrast_predeclaration({}, {'contrast_fit': {'predeclared': 'INCONCLUSIVE: cap'}}),
                         'INCONCLUSIVE: cap')
        self.assertIn('identity', desk.contrast_predeclaration({'contrast_predeclared': 'INCONCLUSIVE: identity broken'},
                                                              {'contrast_fit': {'predeclared': 'INCONCLUSIVE: cap'}}))

    def test_battery_window_without_battery_evidence_is_unavailable(self):
        # W1-BLOCKERS (Opus) B rule: missing observations remain unavailable, never a pass.
        r, other = member('battery'), member('other')
        result = reg.desk_diagnostics([r, other])['battery_windows']['synthetic']
        self.assertIsNone(result['bar_pass'])
        self.assertEqual(result['status'], 'unavailable')

    def test_template_has_contrast_fit_on_every_path(self):
        from scripts import validate_align_v4_w1_plan as validator
        policy = validator.build_template()['align_v4']['thermal_policy']
        self.assertIn('every path', policy['contrast_fit'])
        self.assertNotIn('delete', policy['contrast_g0_cap_s'])

    def test_incomplete_actual_dose_grid_never_shrinks_the_denominator(self):
        rows = [dict(pair='spam', window=f'D{i//8}', carrier=str(i), h=h, score=h)
                for i in range(40) for h in (0, 128)]
        rows.pop()
        result = est.benign_carrier_curve(rows, bootstrap_replicates=4)['pairs']['spam']
        self.assertIsNone(dict(result['curve'])[128])
        self.assertIsNone(result['H50'])
        self.assertEqual(result['n_by_h'][128], 39)
        self.assertGreater(result['bootstrap_undefined_replicates']['H50'], 0)

    def test_passing_duty_label_cannot_waive_an_observed_deadman(self):
        inputs, slots = ready_inputs()
        slots['deadman_budget'][0]['x7'] = True
        with self.assertRaisesRegex(ValueError, 'X7|deadman'):
            kit.require_ready(inputs, slots)

    def test_receipt_binds_plan_validator_and_actual_legacy_scorer(self):
        self.assertTrue({'scripts/validate_align_v4_w1_plan.py',
                         'joulewise/align/apple/pilot_analysis.py',
                         'joulewise/align/energy_residual.py'} <= set(reg.ARTIFACTS))


if __name__ == '__main__':
    unittest.main()
