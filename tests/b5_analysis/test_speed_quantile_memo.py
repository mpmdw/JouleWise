"""b5 under-90: the quantile-route memo changes no value, flag or refusal (synthetic only)."""
from __future__ import annotations

from decimal import Decimal, ROUND_DOWN, Inexact, getcontext, localcontext
import time
import unittest
from unittest import mock

import scripts.issue_calibration_acceptance_generation as issuer


def _clear():
    issuer.build_quantile_proof.cache_entries.clear()
    issuer.student_t_quantile.cache_entries.clear()


def _flags():
    return frozenset(signal for signal, raised in getcontext().flags.items() if raised)


class QuantileMemoTests(unittest.TestCase):
    def setUp(self):
        _clear()
        self.addCleanup(_clear)

    def test_values_equal_the_unmemoized_routes_for_both_parities(self):
        for df in (16, 19):
            with localcontext():
                reference = issuer.build_quantile_proof.__wrapped__(df)
                quantile = issuer.student_t_quantile.__wrapped__('0.995', df)
            _clear()
            with localcontext():
                first = issuer.build_quantile_proof(df)
                second = issuer.build_quantile_proof(df)
                self.assertEqual(issuer.student_t_quantile('0.995', df), quantile)
            self.assertEqual(first, reference)
            self.assertEqual(second, reference)
            self.assertIsNot(first, second)
            first['quantiles']['0.995'] = 'mutated'
            first['probabilities'].append('0.5')
            self.assertEqual(issuer.build_quantile_proof(df), reference)

    def test_the_callers_context_is_part_of_the_key_and_flags_replay(self):
        df = 19
        with localcontext() as context:
            context.prec, context.rounding = 40, ROUND_DOWN
            context.clear_flags()
            reference = issuer.build_quantile_proof.__wrapped__(df)
            reference_flags = _flags()
        _clear()
        with localcontext() as context:
            default = issuer.build_quantile_proof(df)
        with localcontext() as context:
            context.prec, context.rounding = 40, ROUND_DOWN
            context.clear_flags()
            miss = issuer.build_quantile_proof(df)
            miss_flags = _flags()
            context.clear_flags()
            hit = issuer.build_quantile_proof(df)
            hit_flags = _flags()
            # Flags already raised before a hit stay raised.
            context.clear_flags()
            context.flags[Inexact] = True
            issuer.build_quantile_proof(df)
            self.assertTrue(getcontext().flags[Inexact])
        self.assertEqual(miss, reference)
        self.assertEqual(hit, reference)
        self.assertEqual(miss_flags, reference_flags)
        self.assertEqual(hit_flags, reference_flags)
        self.assertEqual(len(issuer.build_quantile_proof.cache_entries), 2)
        self.assertIsInstance(default['quantiles']['0.995'], str)

    def test_a_patched_route_is_a_different_key_and_refusals_are_not_kept(self):
        df = 16
        good = issuer.build_quantile_proof(df)

        def wrong(probability, degrees_of_freedom):
            return Decimal('9')

        with mock.patch.object(issuer, 'student_t_quantile_closed_form', wrong):
            for _ in range(2):
                with self.assertRaises(issuer.PrepareRefusal):
                    issuer.build_quantile_proof(df)
        self.assertEqual(len(issuer.build_quantile_proof.cache_entries), 1)
        with mock.patch.object(issuer, 'QUANTILE_PROOF_MINIMUM_AGREEMENT_DIGITS', 10 ** 6):
            with self.assertRaises(issuer.PrepareRefusal):
                issuer.build_quantile_proof(df)
        self.assertEqual(issuer.build_quantile_proof(df), good)

    def test_acceptance_validation_is_unchanged_and_timed(self):
        from joulewise import calibration_bracketing as calibration
        started = time.perf_counter()
        cold = calibration.load_calibration_acceptance_bound()
        cold_s = time.perf_counter() - started
        started = time.perf_counter()
        warm = calibration.load_calibration_acceptance_bound()
        warm_s = time.perf_counter() - started
        with mock.patch.object(issuer, 'build_quantile_proof', issuer.build_quantile_proof.__wrapped__), \
                mock.patch.object(issuer, 'student_t_quantile', issuer.student_t_quantile.__wrapped__):
            reference = calibration.load_calibration_acceptance_bound()
        self.assertIsNotNone(reference)
        self.assertEqual(cold, reference)
        self.assertEqual(warm, reference)
        print(f'\nacceptance validation: cold {cold_s:.3f} s, warm {warm_s:.3f} s')


if __name__ == '__main__':
    unittest.main()
