"""Independent merged-W1 review witnesses. Synthetic inputs; no hardware or data.

The quantile oracle integrates the density of U directly, independently of the
production integration in chi-square X. Numerical tolerances include the small
documented quadrature error at the minimum permitted pilot sample size.
"""
from contextlib import redirect_stdout
from copy import deepcopy
from functools import lru_cache
import io
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.apple import v4_battery as battery, v4_cadence as cadence
from joulewise.align.apple import v4_registration as registration, v4_u3 as u3
from scripts import align_v4_session as session, align_v4_u3_export as exporter
from tests.align.test_v4_cadence import IDENTITY, INTERNAL, passing_packet
from tests.align.v4_registration_fixtures import battery_policy, export, signed_bar


@lru_cache(maxsize=16)
def independent_quantile(n, comparisons, beta, steps=4096):
    """Stdlib Simpson quadrature in U=sqrt(chi2(n)/n), with bisection.

    f_U(u) = 2 (n/2)^(n/2) / Gamma(n/2) u^(n-1) exp(-n u^2/2).
    The u>10 tail is negligible for the reviewed n>=5 cases.
    """
    h = 10.0 / steps
    log_constant = math.log(2) + n/2*math.log(n/2) - math.lgamma(n/2)
    grid = []
    for i in range(1, steps+1):
        x = i*h
        weight = 1 if i == steps else 4 if i % 2 else 2
        grid.append((x, weight*h/3*math.exp(log_constant+(n-1)*math.log(x)-n*x*x/2)))

    def probability(q):
        # One uncertain scale is shared by the entire frozen series.
        return math.fsum(w*(-math.expm1(comparisons*math.log1p(
            -min(math.erfc(q*x/math.sqrt(2)), 1-1e-16)))) for x, w in grid)

    lo, hi = 0.0, 20.0
    for _ in range(48):
        mid = (lo+hi)/2
        if probability(mid) > beta:
            lo = mid
        else:
            hi = mid
    return hi


def predicted(relative):
    data = export()
    data['pairs'] = data['pairs'][:len(relative)]
    for pair, value in zip(data['pairs'], relative):
        pair['energies_j'] = [1000*(1-value/2), 1000*(1+value/2)]
    return u3.prediction(data['pairs'], data['policy'])


class ArithmeticWitnesses(unittest.TestCase):
    def test_exact_series_quantile_against_independent_stdlib_integral(self):
        for n, beta, reference in ((5, .05, 4.6574497550), (5, .025, 5.5160320381),
                                   (7, .05, 4.0897897937), (7, .025, 4.6927617773)):
            with self.subTest(n=n, beta=beta):
                q = independent_quantile(n, 16, beta)
                self.assertAlmostEqual(q, reference, places=8)
                self.assertAlmostEqual(q, independent_quantile(n, 16, beta, 8192), places=8)
                self.assertAlmostEqual(u3.series_quantile(n, 16, beta), q,
                                       delta=5e-5 if n == 5 else 1e-6)

    def test_zero_centred_scale_preserves_a_common_drift(self):
        result = predicted([.002]*5)
        self.assertAlmostEqual(result['rms_rel'], .002, places=12)
        self.assertEqual(result['s_rel_sample'], 0)
        self.assertEqual((result['df'], result['series_comparisons']), (5, 16))
        self.assertGreater(result['relative_bar_30B'], 0)
        self.assertAlmostEqual(result['relative_bar_D'], 1.5*result['relative_bar_30B'])

    def test_leave_one_out_threshold_and_zero_other_session_scale(self):
        for outlier, heavy in ((.00299, False), (.00301, True)):
            result = predicted([outlier, .001, .001, .001, .001])
            # With n=5, a ratio to the full RMS can NEVER exceed three.
            self.assertLess(outlier/result['rms_rel'], 3)
            self.assertIs(result['heavy_tail_rule_applied'], heavy)
            self.assertEqual(result['series_beta'], .025 if heavy else .05)
        self.assertTrue(predicted([.001, 0, 0, 0, 0])['heavy_tail_rule_applied'])

    def test_d_screen_absence_or_refutation_is_local_to_d(self):
        for screen in ('missing', 'refuted'):
            data = export()
            if screen == 'missing':
                data['pairs'].pop()
            else:
                data['pairs'][-1]['energies_j'] = [100, 200]
            pred = u3.prediction(data['pairs'], data['policy'])
            self.assertEqual(pred['d_screen'], screen)
            self.assertFalse(pred['d_qualification_pass'])
            bar = registration.derive_u3(data['pairs'], {'transfer.md': 'f'*64}, policy=data['policy'])
            bar.update(status='registered', lead_signature='lead: synthetic 2026-11-08',
                       independent_gate={'verdict': 'ADMIT', 'path': 'docs/align/v4/test.json',
                                         'sha256': 'a'*64, 'derivation_sha256': bar['derivation_sha256']})
            registration.validate_u3(bar)
            self.assertGreater(registration.u3_margin(1000, bar), 0)
            with self.assertRaisesRegex(ValueError, 'D U3 inconclusive'):
                registration.u3_margin(1000, bar, population='D')

    def test_pending_unsigned_and_edited_bars_refuse_with_registration_custody(self):
        from tests.align.test_r11_delta_sol1 import TemporaryCandidate

        good = signed_bar()
        registration.validate_u3(good)  # Detached synthetic-desk control.
        for change in ('pending', 'unsigned', 'arithmetic', 'policy', 'synthetic'):
            bar = deepcopy(good)
            if change == 'pending': bar['status'] = 'PENDING'
            if change == 'unsigned': bar['lead_signature'] = None
            if change == 'arithmetic': bar['prediction']['series_quantile_q'] += .1
            if change == 'policy': bar['policy']['series_alpha'] = .1
            with self.subTest(change=change), tempfile.TemporaryDirectory() as tmp:
                candidate = TemporaryCandidate(Path(tmp))
                relative = registration.REGISTRATION+'u3_bar.json'
                candidate.write(relative, json.dumps(bar))
                candidate.receipt['commit'] = candidate.commit('Synthetic review bar')
                candidate.receipt['artifacts'][relative] = candidate.digest(relative)
                candidate.write(registration.REGISTRATION+'registration_receipt.json',
                                json.dumps(candidate.receipt))
                # The complete receipt passes; refusal must come from U3.
                registration.validate_receipt(candidate.receipt, candidate.root)
                with self.assertRaises(ValueError) as refused:
                    registration.require_registration(candidate.root)
                self.assertIn('U3', str(refused.exception))


class ExportWitnesses(unittest.TestCase):
    def test_failed_prespecified_pair_never_reads_a_substitute(self):
        selection = {'sessions': [{'session': 'p4', 'candidates': [
            {'ordinals': [1, 2], 'early_bundle': 'adjacent-a', 'late_bundle': 'adjacent-b'},
            {'ordinals': [5, 17], 'early_bundle': 'chosen-a', 'late_bundle': 'chosen-b'},
            {'ordinals': [6, 16], 'early_bundle': 'substitute-a', 'late_bundle': 'substitute-b'}]}]}
        frozen = deepcopy(selection)
        with patch.object(exporter, 'measure_pair', return_value={'eligible': False, 'reasons': ['unavailable']}) as read:
            result = exporter.pilot_pairs(selection)
        read.assert_called_once_with('chosen-a', 'chosen-b')
        self.assertEqual(selection, frozen)
        self.assertEqual(result['pairs'], [])
        self.assertEqual(result['unavailable_sessions'][0]['ordinals'], [5, 17])

    def test_pilot_and_r1_commands_print_counts_only(self):
        measurement = dict(eligible=True, reasons=[], energies_j=[12345.6789, 12346.9876],
                           clock_difference_fraction=0., token_identical=True,
                           configuration_sha256='b'*64, source_sha256='c'*64)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            selected = root/'selection.json'
            selected.write_text(json.dumps({'sessions': [{'session': 'p4', 'candidates': [
                {'ordinals': [5, 17], 'early_bundle': 'synthetic-a', 'late_bundle': 'synthetic-b'}]}]}))
            for command, arguments in (('pilot', ['--selection', str(selected)]),
                                        ('r1', ['--early-bundle', 'synthetic-a', '--late-bundle', 'synthetic-b',
                                                '--ordinals', '2', '3'])):
                output, stdout = root/(command+'.json'), io.StringIO()
                with patch.object(exporter, 'measure_pair', return_value=measurement), redirect_stdout(stdout):
                    self.assertEqual(exporter.main([command, *arguments, '--output', str(output)]), 0)
                summary = json.loads(stdout.getvalue())
                self.assertEqual(summary, {'pairs': 1, 'unavailable': 0})
                self.assertNotIn('energies_j', stdout.getvalue())
                self.assertNotIn('12345', stdout.getvalue())
                self.assertEqual(json.loads(output.read_text())['pairs'][0]['energies_j'], measurement['energies_j'])

    def test_unavailable_diagnostics_stay_in_the_export_file(self):
        diagnostic = 'synthetic diagnostic 12345.6789'
        with tempfile.TemporaryDirectory() as tmp:
            output, stdout = Path(tmp)/'r1.json', io.StringIO()
            with patch.object(exporter, 'measure_pair', return_value={'eligible': False, 'reasons': [diagnostic]}), \
                    redirect_stdout(stdout):
                exporter.main(['r1', '--early-bundle', 'synthetic-a', '--late-bundle', 'synthetic-b',
                               '--ordinals', '2', '3', '--output', str(output)])
            self.assertEqual(json.loads(stdout.getvalue()), {'pairs': 0, 'unavailable': 1})
            self.assertNotIn(diagnostic, stdout.getvalue())
            self.assertEqual(json.loads(output.read_text())['unavailable'], [diagnostic])


class BatteryWitnesses(unittest.TestCase):
    def member(self, flags=(), observed=True):
        return dict(id='synthetic', model='D', window='C2',
                    excluded=any(flag in battery.EXCLUDE+battery.MISSING for flag in flags),
                    flags=list(flags), battery={'status': 'observed' if observed else 'unavailable',
                                               'source_sha256': 'a'*64, 'flags': list(flags)})

    def test_accumulator_charge_and_ac_loss_are_zero_tolerance_assist_is_retained(self):
        for flag in ('battery.accumulator_excursion', 'battery.member_span'):
            report = battery.window_consequences([self.member([flag])], battery_policy())['D/C2']
            self.assertEqual(report['B_count'], 1)
            self.assertIs(report['bar_pass'], False)
        report = battery.window_consequences([self.member(['battery.assist'])], battery_policy())['D/C2']
        self.assertIs(report['bar_pass'], True)
        self.assertEqual(report['assist_count'], 1)

    def test_missing_evidence_is_nonpassing_and_first_resume_still_needs_topup(self):
        report = battery.window_consequences([self.member(observed=False)], battery_policy())['D/C2']
        self.assertIsNone(report['bar_pass'])
        self.assertFalse(session.battery_windows_pass({'D/C2': report}))
        packet = passing_packet()
        packet['checks']['battery_window'] = dict(status='fail', basis='missing evidence; not a pass',
                                                 consecutive_non_pass=1)
        result = cadence.next_arm_triage(packet, INTERNAL, IDENTITY)
        self.assertTrue(result['admitted'], result['reasons'])
        self.assertEqual(result['checks']['battery_window']['status'], 'automatic_resume')
        self.assertFalse(cadence.next_arm_triage(packet, {**INTERNAL, 'charging_battery': False}, IDENTITY)['admitted'])

    def test_second_nonpass_requires_a_signed_current_window_ruling(self):
        packet = passing_packet()
        packet['checks']['battery_window'] = dict(status='fail', basis='missing then charging', consecutive_non_pass=2)
        ruling = dict(ruling_id='review-test', text_sha256='a'*64, after_window='C2',
                      lead_signature='lead: synthetic 2026-11-08')
        self.assertFalse(cadence.next_arm_triage(packet, INTERNAL, IDENTITY)['admitted'])
        for bad in ({**ruling, 'lead_signature': None}, {**ruling, 'after_window': 'C1'}):
            self.assertFalse(cadence.next_arm_triage({**packet, 'battery_rulings': [bad]}, INTERNAL, IDENTITY)['admitted'])
        self.assertTrue(cadence.next_arm_triage({**packet, 'battery_rulings': [ruling]}, INTERNAL, IDENTITY)['admitted'])

    def test_only_b_bar_is_exempt_from_full_desk_gate(self):
        self.assertTrue(session.full_desk_gate_pass({'v4_B_bar': False, 'v4_D_U3': True}))
        self.assertFalse(session.full_desk_gate_pass({'v4_B_bar': False, 'v4_D_U3': False}))
        self.assertFalse(session.full_desk_gate_pass({'v4_B_bar': False, 'v4_D_U3': None}))
        self.assertFalse(session.full_desk_gate_pass({'v4_B_bar': False}))


if __name__ == '__main__':
    unittest.main()
