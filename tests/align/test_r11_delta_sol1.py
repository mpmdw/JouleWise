"""R11 delta review: synthetic witnesses, no hardware or measurement inputs.

The five Witness tests intentionally fail on 353446ad6. Product repairs and
scientific rulings belong to the lead. Controls characterize the working
paths and the receipt's conservative B6 coupling.
"""
from tests.git_fixture import init_git_fixture
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.apple import v4_cadence as cadence
from joulewise.align.apple import v4_registration as registration
from scripts import align_v4_session as session
from tests.align.test_v4_cadence import INTERNAL, arm_seams, passing_packet, window, write_battery_log


class TemporaryCandidate:
    """A complete receipt in an isolated, synthetic Git repository."""

    def __init__(self, root):
        self.root = root
        for relative in registration.ARTIFACTS:
            self.write(relative, 'synthetic registered bytes\n')
        # W1's HAZARD_PACK chain executes this as campaign_runner; it is not
        # an import edge, and the current receipt does not bind it.
        self.write('scripts/run_campaign.py', 'synthetic campaign implementation\n')
        self.gates = {s: f'docs/align/v4/delta-witness-{s}.md' for s in ('A', 'B')}
        for relative in self.gates.values():
            self.write(relative, 'synthetic admitted gate\n')
        init_git_fixture(self.root, '-q')
        reviewed = self.commit('Synthetic reviewed candidate')
        self.receipt = {
            'schema': registration.RECEIPT_SCHEMA, 'status': 'registered',
            'commit': reviewed, 'lead_signature': 'lead: synthetic-delta 2026-11-08',
            'rulings': {str(n): 'installed' for n in registration.RULINGS},
            'artifacts': {p: self.digest(p) for p in registration.ARTIFACTS},
            'gates': {s: {'verdict': 'ADMIT', 'path': p, 'sha256': self.digest(p)}
                      for s, p in self.gates.items()},
        }
        registration.validate_receipt(self.receipt, self.root)

    def write(self, relative, value):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value)

    def digest(self, relative):
        return hashlib.sha256((self.root / relative).read_bytes()).hexdigest()

    def git(self, *args):
        return subprocess.run(
            ['git', '-c', 'core.hooksPath=/dev/null', *args], cwd=self.root,
            check=True, capture_output=True, text=True).stdout.strip()

    def commit(self, message):
        self.git('add', '.')
        self.git('-c', 'user.name=Synthetic', '-c', 'user.email=synthetic@example.invalid',
                 'commit', '-qm', message)
        return self.git('rev-parse', 'HEAD')


class ExecutedReceiptWitness(unittest.TestCase):
    def test_changed_launched_campaign_code_requires_a_new_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidate = TemporaryCandidate(Path(tmp))
            candidate.write('scripts/run_campaign.py', 'different campaign implementation\n')
            candidate.commit('Synthetic unreviewed campaign change')
            self.assertEqual(candidate.git('status', '--porcelain'), '')
            with self.assertRaises(ValueError, msg='launched W1 code drift needs a new candidate gate'):
                registration.validate_receipt(candidate.receipt, candidate.root)


class CalibrationEvidenceWitnesses(unittest.TestCase):
    def test_eligible_members_cannot_outnumber_captured_members(self):
        # Six captures in total cannot establish 42 eligible benign per pair.
        rows = [window(f'C{i}', 7, 7, captured=1) for i in range(1, 7)]
        with self.assertRaises(ValueError, msg='contradictory counts must not authorize test entry'):
            cadence.calibration_stop(rows)

    def test_zero_capture_provisional_window_is_not_a_terminal_refusal(self):
        # After six final but insufficient windows, C7 is still in flight and
        # has not captured its first member. It must block another arm.
        rows = [window(f'C{i}', 6, 6) for i in range(1, 7)]
        rows.append(window('C7', 0, 0, status='provisional', captured=0))      # still unfinished
        self.assertEqual(cadence.calibration_stop(rows)['decision'], 'pending_final_eligibility')


class TriageEvidenceWitnesses(unittest.TestCase):
    def test_previous_w1_cannot_defer_desk_with_a_conflicting_flag(self):
        packet = passing_packet(previous_window='W1', previous_window_is_w1=False,
                                calibration_windows=[])
        packet['checks']['full_desk_gate'] = {'status': 'deferred', 'basis': 'desk still running'}
        self.assertFalse(cadence.next_arm_triage(packet, INTERNAL)['admitted'],
                         'a packet explicitly naming W1 must wait for the full desk')

    def test_arm_retains_evidence_distinguishing_two_calibration_histories(self):
        packets = []
        for last_count in (4, 7):
            # fixed-8 (RUN_STATE 217): two complete histories, 53 vs 56 eligible per pair
            rows = [window(f'C{i}', 7, 7) for i in range(1, 8)]
            rows.append(window('C8', last_count, last_count))
            packets.append(passing_packet(previous_window='C8', next_window_role='test',
                                          calibration_windows=rows))
        good = dict(passed=True, probe_error=False, external_connected=True,
                    is_charging=False, update_age_s=1, current_capacity_pct=99,
                    instant_amperage_ma=0)
        with tempfile.TemporaryDirectory() as tmp, \
             patch('joulewise.align.apple.powermode.admit_ac_powermode', return_value={'admitted': True}), \
             patch('joulewise.align.apple.powermode.host_marker_path', return_value=str(Path(tmp)/'marker')), \
             patch('joulewise.align.apple.powermode.host_state_dir', return_value=tmp), \
             patch('joulewise.align.apple.external_volume.census', return_value={}), \
             patch('joulewise.align.apple.external_volume.arm_check', return_value={'verdict': 'PASS'}), \
             patch('joulewise.battery_float.observe', return_value=(good, b'synthetic raw')), \
             patch.object(session, 'held_window_check', return_value={'ok': True, 'reasons': [], 'synthetic': True}):
            runner = lambda argv: subprocess.CompletedProcess(argv, 0, 'synthetic pmset', '')
            log = write_battery_log(Path(tmp) / 'battery.jsonl', 5000.)
            records = [session.arm_checks(tmp, {}, runner=runner, now=lambda: 5000.,
                        obc_off_attested_by='synthetic', battery_log=log,
                        next_arm_triage=deepcopy(p), **arm_seams()) for p in packets]
        self.assertTrue(all(r['admitted'] for r in records))
        # Both histories complete, but 53 and 56 eligible are different calibration sets.
        # Retaining the packet, its digest or an immutable evidence reference
        # would distinguish them; recording only 'stop_complete' loses it.
        self.assertNotEqual(json.dumps(records[0], sort_keys=True), json.dumps(records[1], sort_keys=True))


class DeltaControls(unittest.TestCase):
    def test_eight_consistent_windows_complete_at_both_pair_targets(self):
        # RUN_STATE 217: fixed 8, no early stop (six windows only continue).
        self.assertEqual(cadence.calibration_stop([window(f'C{i}', 7, 7) for i in range(1, 7)])['decision'], 'continue')
        result = cadence.calibration_stop([window(f'C{i}', 7, 7) for i in range(1, 9)])
        self.assertEqual(result['decision'], 'calibration_complete')
        self.assertEqual(result['eligible_by_pair'], {'spam': 56, 'bank': 56})

    def test_final_zero_capture_refusals_still_follow_the_ruled_cap_and_escalation(self):
        refusal = lambda name: window(name, 0, 0, captured=0)
        result = cadence.calibration_stop([refusal('C1-r1'), refusal('C1-r2')])
        self.assertEqual((result['attempted'], result['decision']), (0, 'escalate_to_lead'))

    def test_receipt_currently_couples_b6_only_analysis_changes(self):
        # Characterization, not a demand to weaken any executed-code binding.
        with tempfile.TemporaryDirectory() as tmp:
            candidate = TemporaryCandidate(Path(tmp))
            candidate.write('joulewise/b6/analysis_lane.py', 'different B6-only analysis implementation\n')
            candidate.commit('Synthetic unrelated B6 change')
            with self.assertRaisesRegex(ValueError, 'digest drift: joulewise/b6/analysis_lane.py'):
                registration.validate_receipt(candidate.receipt, candidate.root)


if __name__ == '__main__':
    unittest.main()
