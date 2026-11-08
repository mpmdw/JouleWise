"""Opus cross-family cold review witnesses for the R12 next-arm packet builder.

Failing-first: each test states the property the arm must hold and FAILS at
f1b90f950 (packet branch) and on the scratch merge with the v4 head 2cce80ede.
Synthetic Git records only; no measurements, probes, models or network.
See docs/align/v4/triage-packet-opus-review.md.
"""
import copy
import inspect
import tempfile
import unittest

from joulewise.align.apple import v4_cadence as cad
from tests.align.test_v4_next_arm_packet import INTERNAL, Scenario


def evaluate(packet, now):
    """Call whichever consumer signature is present (packet branch or v4 head)."""
    params = inspect.signature(cad.next_arm_triage).parameters
    args, kwargs = [packet, INTERNAL], {}
    if 'identity' in params:
        args.append({'artifact_set_sha256': packet.get('last_desk_passed_artifact_set_sha256'),
                     'record_commit_exists': True})
    if 'now_epoch_s' in params:
        kwargs['now_epoch_s'] = now
    return cad.next_arm_triage(*args, **kwargs)


class OpusWitnesses(unittest.TestCase):
    def scenario(self, window='W1'):
        temp = tempfile.TemporaryDirectory(prefix='jw-triage-opus-')
        self.addCleanup(temp.cleanup)
        return Scenario(temp.name, window)

    def test_honest_synthetic_w1_packet_admits_on_the_consumer_in_tree(self):
        # HIGH-3 (integration): passes at f1b90f950, fails against the v4 head
        # consumer (meter_samples_clock unlisted, meter_reader_live missing,
        # code_or_config_changed contradicts the derived artifact-set digest,
        # now_epoch_s TypeError inside build_packet).
        packet = self.scenario().finish().build()
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight']['reasons'])
        result = evaluate(packet, 111)
        self.assertTrue(result['admitted'], result['reasons'])

    def test_edited_status_on_a_refusing_packet_refuses(self):
        # HIGH-1: the smoke-kit finding. An honest packet refuses (hashing still
        # running on the MBP); flipping the status text to pass must not arm.
        s = self.scenario()
        s.quiet.update(active_work=['hashing'])
        honest = s.finish().build()
        self.assertEqual(honest['checks']['quiet_start_state']['status'], 'fail')
        self.assertFalse(evaluate(honest, 111)['admitted'])
        edited = copy.deepcopy(honest)
        edited['checks']['quiet_start_state'] = {'status': 'pass', 'basis': 'quiet start verified'}
        self.assertFalse(evaluate(edited, 111)['admitted'],
                         'edited packet text with valid statuses was accepted')

    def test_fabricated_calibration_rows_cannot_open_a_test_arm(self):
        # HIGH-1 consequence: calibration_stop is "derived", but from packet rows
        # the consumer never re-derives from the committed records.
        s = self.scenario('C1')
        honest = s.finish().build()
        self.assertEqual(honest['next_window_role'], 'calibration')
        forged = copy.deepcopy(honest)
        forged['calibration_windows'] = [
            {'window': f'C{i}', 'status': 'final', 'captured_members': 14,
             'eligible_benign': {'spam': 7, 'bank': 7}} for i in range(1, 9)]
        forged['next_window_role'] = 'test'
        self.assertFalse(evaluate(forged, 111)['admitted'],
                         'fabricated calibration rows authorized a test arm')

    def test_stale_packet_cannot_drop_its_expiry(self):
        # HIGH-2: the consumer checks expiry only when the key is present.
        honest = self.scenario().finish().build()
        stale = copy.deepcopy(honest)
        stale.pop('valid_until_epoch_s', None)
        self.assertFalse(evaluate(stale, 10**9)['admitted'],
                         'a packet with its expiry removed armed 30 years later')


if __name__ == '__main__':
    unittest.main()
