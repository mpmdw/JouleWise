"""Opus cross-family cold review witnesses for the R12 next-arm packet (docs/align/v4/triage-packet-opus-review.md).

Brought over from origin/align/2026-11-08-triage-packet-opus-review and run on the v4 head. The
review called the consumer function directly with an edited packet; the guarantee lives in the
ARM (a packet is a pointer, never trusted data), so ``evaluate`` routes through the arm's
rebuild-and-compare (``rebuild_and_compare`` then ``next_arm_triage`` on the arm's own build), which
is exactly what ``align_v4_session.arm_checks`` does. Each test states the property and fails on the
pre-rebuild head. Synthetic Git records only.
"""
import copy
import unittest

from joulewise.align.apple import v4_cadence as cad
from tests.align.test_v4_next_arm_packet import Base, evaluate


class OpusWitnesses(Base):
    def test_honest_synthetic_w1_packet_admits_on_the_consumer_in_tree(self):
        # HIGH-3 (integration): split meter, derived desk digest, signed-ruling wire, new signature.
        s = self.scenario().finish()
        packet = s.build()
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight']['reasons'])
        result = evaluate(s, packet)
        self.assertTrue(result['admitted'], result['reasons'])

    def test_edited_status_on_a_refusing_packet_refuses(self):
        # HIGH-1: the smoke-kit finding. Flipping a failing status to pass must not arm.
        s = self.scenario()
        s.quiet.update(active_work=['hashing'])
        s.finish()
        honest = s.build()
        self.assertEqual(honest['checks']['quiet_start_state']['status'], 'fail')
        self.assertFalse(evaluate(s, honest)['admitted'])
        edited = copy.deepcopy(honest)
        edited['checks']['quiet_start_state'] = {'status': 'pass', 'basis': 'quiet start verified'}
        self.assertFalse(evaluate(s, edited)['admitted'], 'edited packet text with valid statuses was accepted')

    def test_fabricated_calibration_rows_cannot_open_a_test_arm(self):
        # HIGH-1 consequence: eight fabricated 7/7 rows plus role:test must not forge calibration_complete.
        s = self.calibration_series([('C1', True, True)])
        honest = s.build()
        self.assertEqual(honest['next_window_role'], 'calibration')
        forged = copy.deepcopy(honest)
        forged['calibration_windows'] = [
            {'window': f'C{i}', 'status': 'final', 'captured_members': 14,
             'eligible_benign': {'spam': 7, 'bank': 7}} for i in range(1, 9)]
        forged['next_window_role'] = 'test'
        self.assertFalse(evaluate(s, forged)['admitted'], 'fabricated calibration rows authorized a test arm')

    def test_stale_packet_cannot_drop_its_expiry(self):
        # HIGH-2: expiry is mandatory; a packet with it removed is not the arm's own build.
        s = self.scenario().finish()
        honest = s.build()
        stale = copy.deepcopy(honest)
        stale.pop('valid_until_epoch_s', None)
        self.assertFalse(evaluate(s, stale, now=10**9)['admitted'], 'a packet with its expiry removed armed 30 years later')
        self.assertFalse(evaluate(s, honest, now=10**9)['admitted'])      # and an honest one is expired by then

    def test_swapped_record_commit_and_planted_desk_digest_refuse(self):
        s = self.scenario().finish()
        good = s.build()
        swapped = copy.deepcopy(good)
        swapped['record_commit'] = s.code_commit
        self.assertFalse(evaluate(s, swapped)['admitted'])
        planted = copy.deepcopy(good)
        planted['last_desk_passed_artifact_set_sha256'] = 'f' * 64
        self.assertFalse(evaluate(s, planted)['admitted'])


if __name__ == '__main__':
    unittest.main()
