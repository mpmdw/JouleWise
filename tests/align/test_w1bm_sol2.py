"""Merged W1 blocker review at 565cb1e47. Synthetic inputs and stdlib only.

Its two review witnesses (counts-only export stdout, S2-02; the B-only exclusion
leaking into the full-desk gate, S2-01) were red at 565cb1e47 and pass after the
merged-branch repairs.
"""
from contextlib import redirect_stdout
from copy import deepcopy
import io
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.apple import thermal_desk, v4_battery, v4_cadence, v4_registration, v4_u3
from scripts import align_pilot_session, align_v4_session, align_v4_u3_export
from tests.align.test_r11_delta_sol1 import TemporaryCandidate
from tests.align.test_thermal_desk import member
from tests.align.test_v4_cadence import IDENTITY, INTERNAL, NOW_EPOCH, passing_packet
from tests.align.v4_registration_fixtures import battery_policy, export, signed_bar


def independent_series_tail(q, n, comparisons=16, steps=4096):
    """Integrate over the chi *radius*, independently of production's chi2 grid.

    For U=sqrt(chi2_n/n), density is
    2*(n/2)**(n/2)/Gamma(n/2) * u**(n-1)*exp(-n*u*u/2).
    Conditional on U, all N tests pass with probability erf(q*U/sqrt(2))**N.
    Simpson integration on [0,12] has negligible truncation for n>=5.
    """
    h = 12 / steps
    log_constant = math.log(2) + n/2*math.log(n/2) - math.lgamma(n/2)
    return h/3 * math.fsum(
        (1 if i == steps else 4 if i % 2 else 2)
        * math.exp(log_constant + (n-1)*math.log(i*h) - n*(i*h)**2/2)
        * (1 - math.erf(q*i*h/math.sqrt(2))**comparisons)
        for i in range(1, steps+1))


def independent_quantile(n, beta):
    lo, hi = 0., 20.
    for _ in range(40):
        q = (lo+hi)/2
        if independent_series_tail(q, n) > beta:
            lo = q
        else:
            hi = q
    return (lo+hi)/2


def adopted(data):
    bar = v4_registration.derive_u3(data['pairs'], {'pairs.json': 'a'*64, 'transfer.md': 'f'*64},
                                     policy=data['policy'])
    bar.update(status='registered', lead_signature='lead: synthetic-review 2026-11-08',
               independent_gate={'verdict': 'ADMIT', 'path': 'docs/align/v4/synthetic-gate.json',
                                 'sha256': 'd'*64, 'derivation_sha256': bar['derivation_sha256']})
    return bar


class IndependentArithmeticTests(unittest.TestCase):
    def test_q_against_independent_radius_integral_at_both_betas(self):
        for n in (5, 7):
            for beta in (.05, .025):
                with self.subTest(n=n, beta=beta):
                    expected = independent_quantile(n, beta)
                    actual = v4_u3.series_quantile(n, 16, beta)
                    # Production's fixed chi2 grid has up to 4.25e-5 q error
                    # at n=5; the probability error is less than 1e-6.
                    self.assertAlmostEqual(actual, expected, delta=5e-5)
                    self.assertAlmostEqual(independent_series_tail(actual, n), beta, delta=1e-6)
        self.assertAlmostEqual(independent_quantile(7, .05), 4.089789793720, places=9)

    def test_loo_boundary_is_strict_and_zero_centring_retains_common_drift(self):
        data = export()
        data['pairs'] = data['pairs'][:5]  # the R1 screen is optional
        for row, r in zip(data['pairs'], [.375, .125, -.125, .125, -.125]):
            row['energies_j'] = [1-r/2, 1+r/2]  # exact binary fractions
        p = v4_u3.prediction(data['pairs'], data['policy'])
        self.assertFalse(p['heavy_tail_rule_applied'])  # exactly 3x other-session RMS
        data['pairs'][0]['energies_j'] = [1-.376/2, 1+.376/2]
        p = v4_u3.prediction(data['pairs'], data['policy'])
        self.assertTrue(p['heavy_tail_rule_applied'])
        self.assertEqual(p['series_beta'], .025)
        self.assertLess(.376/p['rms_rel'], 3)  # an in-sample rule would miss it
        for row in data['pairs']:
            row['energies_j'] = [1-.125/2, 1+.125/2]
        p = v4_u3.prediction(data['pairs'], data['policy'])
        self.assertEqual((p['df'], p['rms_rel'], p['s_rel_sample']), (5, .125, 0.))

    def test_ruled_roster_and_relative_only_margin(self):
        template = align_v4_u3_export.policy_template()
        self.assertEqual(template['checks_by_window'], export()['policy']['checks_by_window'])
        self.assertEqual(sum(sum(w.values()) for w in template['checks_by_window'].values()), 24)      # R25: 16 + C9-C14
        self.assertEqual((template['series_alpha'], template['d_transfer_factor']), (.05, 1.5))
        bar = signed_bar()
        for energy in (1e-6, 1000., 1e6):
            a = v4_registration.u3_margin(energy, bar)
            d = v4_registration.u3_margin(energy, bar, population='D')
            self.assertAlmostEqual(a/energy, bar['prediction']['relative_bar_30B'])
            self.assertAlmostEqual(d/a, 1.5)

    def test_pilot_reuse_or_fewer_than_five_or_judged_windows_refuses(self):
        for change in ('few', 'duplicate_session', 'W1', 'C1'):
            data = export()
            if change == 'few':
                data['pairs'] = data['pairs'][:4]
            elif change == 'duplicate_session':
                data['pairs'][1]['session'] = data['pairs'][0]['session']
            else:
                data['pairs'][0]['phase'] = change
            with self.subTest(change=change), self.assertRaises(ValueError):
                v4_u3.prediction(data['pairs'], data['policy'])


class RegistrationAndScreenTests(unittest.TestCase):
    def test_registration_refuses_pending_unsigned_edited_and_detached_synthetic_bars(self):
        # Exercise the real receipt validator and require_registration entry;
        # each bad bar is committed and receipt-bound so digest drift cannot
        # mask the U3-specific refusal. Synthetic source/gate bytes are absent.
        with tempfile.TemporaryDirectory() as tmp:
            candidate = TemporaryCandidate(Path(tmp))
            bar_path = v4_registration.REGISTRATION + 'u3_bar.json'
            receipt_path = v4_registration.REGISTRATION + 'registration_receipt.json'
            for change in ('pending', 'unsigned', 'edited', 'synthetic'):
                bar = signed_bar()
                if change == 'pending':
                    bar['status'] = 'PENDING'
                elif change == 'unsigned':
                    bar['lead_signature'] = None
                elif change == 'edited':
                    bar['prediction']['relative_bar_30B'] *= 2
                candidate.write(bar_path, json.dumps(bar))
                candidate.receipt['commit'] = candidate.commit('Synthetic review case ' + change)
                candidate.receipt['artifacts'][bar_path] = candidate.digest(bar_path)
                candidate.write(receipt_path, json.dumps(candidate.receipt))
                with self.subTest(change=change), self.assertRaisesRegex(ValueError, 'U3'):
                    v4_registration.require_registration(candidate.root)

    def test_missing_and_failed_r1_screen_keep_30b_but_block_d_and_full_desk(self):
        for screen in ('missing', 'refuted'):
            data = export()
            if screen == 'missing':
                data['pairs'].pop()
            else:
                data['pairs'][-1]['energies_j'] = [1., 2.]
            bar = adopted(data)
            self.assertIs(v4_registration.validate_u3(bar), bar)
            self.assertGreater(v4_registration.u3_margin(1000, bar), 0)
            a, b = member('a', energy=30000), member('b', energy=30000)
            for row in (a, b):
                row.update(role='D', window='W1', identical_work_group='D-pair',
                           u3_configuration_sha256='b'*64)
            pair = thermal_desk.identical_pair(a, b, u3_bar=bar)
            with self.subTest(screen=screen):
                self.assertEqual(pair['status'], 'inconclusive')
                self.assertIn(screen, pair['reason'])
                result = thermal_desk.window_report([a, b], v4=True, u3_bar=bar)
                u3 = result['model_windows']['synthetic/W1']['U3']['status']
                self.assertEqual(u3, 'inconclusive')
                self.assertFalse(align_v4_session.full_desk_gate_pass({'v4_D_U3': u3 == 'pass'}))


class ExportWitnesses(unittest.TestCase):
    def selection(self):
        return {'sessions': [{'session': 'pilot-review', 'candidates': [
            {'ordinals': [1, 2], 'early_bundle': 'adjacent', 'late_bundle': 'unused'},
            {'ordinals': [5, 17], 'early_bundle': 'chosen', 'late_bundle': 'chosen-late'},
            {'ordinals': [6, 16], 'early_bundle': 'substitute', 'late_bundle': 'forbidden'}]}]}

    def measurement(self, *, eligible=True):
        return {'eligible': eligible, 'reasons': [] if eligible else ['energy unavailable'],
                'energies_j': [87654.321, 87655.432], 'clock_difference_fraction': 0.,
                'configuration_sha256': 'b'*64, 'source_sha256': 'c'*64}

    def test_selection_is_fixed_by_positions_before_measurement_and_never_substitutes(self):
        selection = self.selection()
        frozen = deepcopy(selection)
        def measure(early, late):
            self.assertEqual(selection, frozen)
            self.assertEqual((early, late), ('chosen', 'chosen-late'))
            return self.measurement(eligible=False)
        with patch.object(align_v4_u3_export, 'measure_pair', side_effect=measure) as measured:
            result = align_v4_u3_export.pilot_pairs(selection)
        measured.assert_called_once()
        self.assertEqual(result['pairs'], [])
        self.assertEqual(len(result['unavailable_sessions']), 1)

    def run_export(self, command, directory, *, eligible=True):
        output = directory / (command + '.json')
        if command == 'pilot':
            selection = directory / 'selection.json'
            selection.write_text(json.dumps(self.selection()))
            argv = [command, '--selection', str(selection)]
        else:
            argv = [command, '--early-bundle', 'early', '--late-bundle', 'late', '--ordinals', '2', '3']
        stdout = io.StringIO()
        with patch.object(align_v4_u3_export, 'measure_pair', return_value=self.measurement(eligible=eligible)), \
                redirect_stdout(stdout):
            self.assertEqual(align_v4_u3_export.main([*argv, '--output', str(output)]), 0)
        return stdout.getvalue(), json.loads(output.read_text())

    def test_steps_four_and_five_never_print_energy_but_export_it_to_explicit_file(self):
        for command in ('pilot', 'r1'):
            with self.subTest(command=command), tempfile.TemporaryDirectory() as tmp:
                stdout, result = self.run_export(command, Path(tmp))
                self.assertNotIn('87654', stdout)
                self.assertNotIn('87655', stdout)
                self.assertNotIn('energies_j', stdout)
                self.assertEqual(result['pairs'][0]['energies_j'], [87654.321, 87655.432])

    def test_steps_four_and_five_stdout_contains_counts_only(self):
        # Review finding S2-02: currently `unavailable` is a list, not a count.
        for command in ('pilot', 'r1'):
            with self.subTest(command=command), tempfile.TemporaryDirectory() as tmp:
                stdout, _ = self.run_export(command, Path(tmp), eligible=False)
                summary = json.loads(stdout)
                self.assertEqual(summary['pairs'], 0)
                self.assertIs(type(summary['unavailable']), int)
                self.assertEqual(summary['unavailable'], 1)


class BatteryWitnesses(unittest.TestCase):
    def test_excursion_and_missing_are_nonpass_assist_is_retained(self):
        clean = {'id': 'member', 'model': 'D', 'window': 'W1', 'flags': [],
                 'battery': {'status': 'observed', 'source_sha256': 'a'*64, 'flags': []}}
        for flag in ('battery.member_span', 'battery.accumulator_excursion',
                     'battery.unmeasured', 'battery.capture_pair_missing', 'battery.capture_pair_failed'):
            row = deepcopy(clean)
            row['battery']['flags'] = [flag]
            result = v4_battery.window_consequences([row], battery_policy())['D/W1']
            with self.subTest(flag=flag):
                self.assertIsNot(result['bar_pass'], True)
                self.assertEqual(result['B_count'], int(flag in v4_battery.EXCLUDE))
        row = deepcopy(clean)
        row['battery']['flags'] = ['battery.assist']
        result = v4_battery.window_consequences([row], battery_policy())['D/W1']
        self.assertIs(result['bar_pass'], True)
        self.assertEqual(result['assist_count'], 1)
        self.assertFalse(align_v4_session.battery_windows_pass({}))

    def test_nonpass_streak_requires_fresh_arm_evidence_then_signed_exact_window_ruling(self):
        for reason in ('charging member', 'accumulator excursion', 'missing battery evidence'):
            packet = passing_packet()
            packet['checks']['battery_window'] = {'status': 'fail', 'basis': reason,
                                                   'consecutive_non_pass': 1}
            first = v4_cadence.next_arm_triage(packet, INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)
            self.assertTrue(first['admitted'], first['reasons'])
            self.assertEqual(first['checks']['battery_window']['status'], 'automatic_resume')
            self.assertFalse(v4_cadence.next_arm_triage(packet, {**INTERNAL, 'charging_battery': False},
                                                       IDENTITY, now_epoch_s=NOW_EPOCH)['admitted'])
            packet['checks']['battery_window']['consecutive_non_pass'] = 2
            ruling = {'ruling_id': 'synthetic-review', 'text_sha256': 'd'*64, 'after_window': 'C2',
                      'lead_signature': 'lead: synthetic-review 2026-11-08'}
            for rows in ([], [{**ruling, 'lead_signature': None}], [{**ruling, 'after_window': 'C1'}]):
                self.assertFalse(v4_cadence.next_arm_triage({**packet, 'battery_rulings': rows}, INTERNAL,
                                                           IDENTITY, now_epoch_s=NOW_EPOCH)['admitted'])
            self.assertTrue(v4_cadence.next_arm_triage({**packet, 'battery_rulings': [ruling]}, INTERNAL,
                                                      IDENTITY, now_epoch_s=NOW_EPOCH)['admitted'])
        for status in ('inconclusive', 'deferred', 'not_applicable'):
            packet = passing_packet()
            packet['checks']['battery_window'] = {'status': status, 'basis': 'unavailable evidence'}
            self.assertFalse(v4_cadence.next_arm_triage(packet, INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)['admitted'])

    def test_B_only_exclusion_does_not_reblock_full_desk_automatic_resume(self):
        # Review finding S2-01: the common desk also sets no_member_exclusions
        # false. Ignoring only v4_B_bar cannot implement B's automatic resume.
        row = {'id': 'charged', 'task_pair': 'synthetic', 'condition': 'benign',
               'summary': {'energy': {'gpu': {'joules': 1., 'segment_sum_j': 1.}},
                           'flags': [], 'configuration': {'sampler': {}},
                           'window_evidence_precheck': {'eligible': True}}}
        evidence = {'status': 'observed', 'source_sha256': 'a'*64,
                    'flags': ['battery.member_span']}
        with patch.object(v4_battery, 'bundle_evidence', return_value=evidence):
            v4_battery.attach(row, Path('synthetic-unused'), ([], None, 0))
        self.assertTrue(row['excluded'])
        checks, _, _ = align_pilot_session.instrument_checks([row])
        self.assertFalse(checks['no_member_exclusions'])
        # The common desk replaces this legacy diagnostic with I4' checks;
        # isolate the B-only exclusion from unrelated replay sufficiency.
        checks.pop('I4_greedy_repeats_identical_tokens')
        checks['v4_B_bar'] = False
        # The verdict is evidence-aware: it needs the desk's members to know the
        # exclusion is charging-only. Without them the recorded checks stand.
        self.assertTrue(align_v4_session.full_desk_gate_pass(checks, [row]), checks)
        self.assertFalse(align_v4_session.full_desk_gate_pass(checks))
        # Any non-charging exclusion still fails the gate.
        other = deepcopy(row)
        other['calibration_exclusions'] = ['battery.member_span', 'thermal.start_gate_timeout']
        self.assertFalse(align_v4_session.full_desk_gate_pass(checks, [other]))
        unmeasured = deepcopy(row)
        unmeasured['calibration_exclusions'] = ['battery.unmeasured']
        self.assertFalse(align_v4_session.full_desk_gate_pass(checks, [unmeasured]))


if __name__ == '__main__':
    unittest.main()
