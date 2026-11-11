"""Synthetic witnesses for the 2026-11-10 measurement-system audit fixes."""
import json
import os
import tempfile
import types
import unittest
from pathlib import Path

from tests.test_b5_driver import Harness, FakeArm, load_driver


class OutcomeTests(unittest.TestCase):
    def chain_exit(self, h, code):
        # The sandbox cannot census real process groups reliably. Exercise
        # the production terminal/reporting path with a synthetic proven exit.
        def exited(chain, plan, probes, night, claim, **kwargs):
            os.close(claim)
            (night / 'chain.started').write_text('{"pgid": 1}')
            (night / 'chain.exited').write_text(json.dumps({'exit_code': code}))
            return code, None, 0, [], True
        h.driver._run_chain_once = exited

    def test_nonzero_chain_exit_faults_result_hazard_and_courier_without_changing_go(self):
        h = Harness(self, g10=False)
        h.replace_chain("#!/bin/zsh -f\nexit 3\n")
        self.chain_exit(h, 3)
        self.assertEqual(h.driver.EXIT_CHAIN_FAILED, h.run())
        for record in (h.result(), h.hazard(), h.driver.run_courier.call_args.kwargs['report']['facts']):
            self.assertEqual('GO', record['verdict'])
            self.assertEqual('CHAIN_FAILED', record['chain_outcome'])
            reasons = record.get('fault_reasons', record.get('faults', {}).get('reasons'))
            self.assertIn('chain_exit_nonzero:3', reasons)
        self.assertTrue(h.result()['fault'])

    def test_prechain_refusal_faults_without_claiming_chain_started(self):
        h = Harness(self, arm=FakeArm(verdicts={'clock': 'REFUSE'}))
        self.assertEqual(h.driver.EXIT_REFUSED, h.run())
        result = h.result()
        self.assertEqual('REFUSED', result['verdict'])
        self.assertEqual('REFUSED_PRE_CHAIN', result['chain_outcome'])
        self.assertTrue(result['fault'])
        self.assertFalse((h.night / 'chain.started').exists())
        self.assertTrue(h.driver.run_courier.call_args.kwargs['report']['facts']['fault'])

    def test_r1_status_absent_unreadable_or_incomplete_is_a_fault_even_at_exit_zero(self):
        rt = load_driver()
        with tempfile.TemporaryDirectory() as tmp:
            night = Path(tmp)
            (night / 'chain.started').touch()
            payload = night / 'align-r1/r1_result.json'
            payload.parent.mkdir()
            plan = types.SimpleNamespace(plan_id='align-r1-synthetic')
            for status in ('absent', 'unreadable', 'refused', 'aborted', 'running', 'invalid', 'complete'):
                with self.subTest(status=status):
                    payload.unlink(missing_ok=True)
                    if status != 'absent':
                        payload.write_text('{' if status == 'unreadable' else json.dumps({'status': status}))
                    outcome = rt._chain_outcome(plan, night, 'GO', 0)
                    self.assertEqual(status, outcome['measurement_outcome'])
                    self.assertEqual(status != 'complete', outcome['fault'])
                    self.assertEqual('COMPLETE' if status == 'complete' else 'CHAIN_FAILED', outcome['chain_outcome'])

    def test_success_has_no_new_fault_and_non_r1_needs_no_r1_payload(self):
        h = Harness(self, g10=False)
        h.replace_chain("#!/bin/zsh -f\nexit 0\n")
        self.chain_exit(h, 0)
        self.assertEqual(h.driver.EXIT_GO, h.run())
        self.assertEqual('GO', h.result()['verdict'])
        self.assertEqual('COMPLETE', h.result()['chain_outcome'])
        self.assertFalse(h.result()['fault'])
        self.assertIsNone(h.result()['measurement_outcome'])


if __name__ == '__main__':
    unittest.main()
