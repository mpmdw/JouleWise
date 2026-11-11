"""Round-6 reporting regressions; synthetic R1 payloads and host only."""
import json
from unittest import mock

from tests import test_w1_reliability_r2 as r2


ITEM_253_ERROR = (
    'Refusal: runtime.step-30b: exit 1: incomplete '
    'thermal.start_gate_timeout episode.g0_unreleased'
)


class RefusalSummaryTests(r2.DriverCase):
    def refused_night(self):
        h, _ = self.make()
        exited = h.driver._run_chain_once

        def with_payload(*args, **kwargs):
            result = exited(*args, **kwargs)
            path = h.night / 'align-r1/r1_result.json'
            path.parent.mkdir()
            path.write_text(json.dumps({'status': 'refused', 'error': ITEM_253_ERROR}))
            return result

        h.driver._run_chain_once = with_payload
        return h

    def assert_null_summary(self, h, *, outcome='CHAIN_FAILED'):
        result = h.result()
        self.assertEqual(result['measurement_outcome'], 'refused')
        self.assertEqual(result['chain_outcome'], outcome)
        self.assertIsNone(result['chain_refused_phase'])
        self.assertEqual(result['chain_refusal_codes'], [])
        self.assertIn('r1_status:refused', result['fault_reasons'])
        self.assertEqual(h.hazard()['measurement_outcome'], 'refused')

    def test_broken_summary_cannot_remove_primary_terminal_records_or_courier(self):
        h = self.refused_night()
        with mock.patch.object(h.driver, '_r1_refusal_summary', side_effect=ImportError('synthetic')):
            self.assertEqual(h.run(), h.driver.EXIT_GO)
        self.assert_null_summary(h)
        h.driver.run_courier.assert_called_once()

    def test_broken_summary_cannot_remove_fallback_terminal_record_or_delivery_attempt(self):
        h = self.refused_night()
        write_result = h.driver._write_result
        calls = []

        def interrupted_primary(*args, **kwargs):
            calls.append(True)
            if len(calls) == 1:
                raise KeyboardInterrupt('synthetic interruption before primary result write')
            return write_result(*args, **kwargs)

        with mock.patch.object(h.driver, '_write_result', side_effect=interrupted_primary), \
                mock.patch.object(h.driver, '_r1_refusal_summary', side_effect=TypeError('synthetic')):
            with self.assertRaises(KeyboardInterrupt):
                h.run()
        self.assertEqual(len(calls), 2)
        self.assert_null_summary(h, outcome='ABORTED')
        h.driver._durable_record.assert_called_once()

    def test_item_253_error_extracts_digit_bearing_allowlisted_code(self):
        h, _ = self.make()
        summary = h.driver._r1_refusal_summary({'error': ITEM_253_ERROR})
        self.assertEqual(summary, {'chain_refused_phase': 'step_30b',
                                  'chain_refusal_codes': ['episode.g0_unreleased',
                                                          'thermal.start_gate_timeout']})
        for token in ('episode.g0_unreleased99', '1episode.g0_unreleased',
                      'episode.g0_unreleased.extra', 'episode.9g0_unreleased'):
            self.assertEqual(h.driver._r1_refusal_summary({'error': token})['chain_refusal_codes'], [])
