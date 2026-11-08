"""R22-3: the printed balance check by condition. Synthetic only."""
import unittest

from joulewise.align.apple import v4_balance as balance


def member(i, condition, pair, *, events=0, exposure=830.0):
    return {'id': f'm{i}', 'condition': condition, 'task_pair': pair, 'gross_latency_s': exposure,
            'flags': [f'flag.{k}' for k in range(events)], 'calibration_exclusions': []}


class BalanceTests(unittest.TestCase):
    def records(self, *, sabotage_events=0):
        rows = []
        for i in range(14):
            rows.append(member(i, 'benign', 'spam' if i % 2 else 'bank', events=1 if i < 4 else 0))
        for i in range(2):
            rows.append(member(100+i, 'sabotage', 'spam' if i else 'bank', events=sabotage_events))
        return rows

    def test_rates_are_per_member_second_and_expectation_is_exposure_adjusted(self):
        report = balance.balance_check(self.records())
        self.assertEqual(report['status'], 'print_only')
        self.assertTrue(report['disclosed'])
        benign, sabotage = report['by_condition']['benign'], report['by_condition']['sabotage']
        self.assertEqual((benign['members'], benign['events']), (14, 4))
        self.assertEqual((sabotage['members'], sabotage['events']), (2, 0))
        self.assertAlmostEqual(benign['exposure_s'], 14*830.0)
        pooled = 4 / (16*830.0)
        self.assertAlmostEqual(benign['expected_events'], pooled*14*830.0)
        self.assertAlmostEqual(sabotage['expected_events'], pooled*2*830.0)
        self.assertAlmostEqual(report['total']['expected_rate_per_member_hour'], pooled*3600)
        self.assertEqual(sorted(report['by_pair']), ['bank', 'spam'])
        for pair in report['by_pair'].values():
            self.assertEqual(set(pair), {'benign', 'sabotage'})

    def test_it_prints_and_gates_nothing(self):
        report = balance.balance_check(self.records(sabotage_events=3))
        text = '\n'.join(balance.lines(report))
        self.assertIn('balance benign:', text)
        self.assertIn('balance sabotage:', text)
        self.assertIn('(print only)', text)
        p = report['benign_vs_sabotage']['exact_binomial_p']
        self.assertTrue(0 < p <= 1)
        self.assertGreater(report['benign_vs_sabotage']['rate_ratio_sabotage_over_benign'], 1)
        self.assertNotIn('admitted', report)          # a disclosure, never a gate

    def test_contention_codes_count_as_disclosed_events_and_missing_exposure_is_listed(self):
        rows = self.records()
        rows[0]['calibration_exclusions'] = ['contention.request_overlap']
        rows.append({'id': 'no-exposure', 'condition': 'benign', 'task_pair': 'spam', 'flags': []})
        rows.append({'id': 'no-condition', 'gross_latency_s': 800.0, 'flags': []})
        report = balance.balance_check(rows)
        self.assertEqual(report['by_condition']['benign']['events'], 5)
        self.assertEqual(report['members_without_exposure_or_condition'], ['no-exposure', 'no-condition'])

    def test_empty_and_one_sided_inputs_do_not_raise(self):
        empty = balance.balance_check([])
        self.assertIsNone(empty['benign_vs_sabotage']['exact_binomial_p'])
        only = balance.balance_check([member(1, 'benign', 'spam', events=1)])
        self.assertIsNone(only['benign_vs_sabotage']['exact_binomial_p'])
        balance.lines(empty)
        balance.lines(only)


if __name__ == '__main__':
    unittest.main()
