"""R11 delta Sol2 review: deliberately failing contract witnesses, synthetic only.

No model, device, production process, measurement reader or network is used.
The receipt fixtures are independent temporary Git repositories. Product fixes
and the final registration decision remain with the lead.
"""
from contextlib import contextmanager
from copy import deepcopy
import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.apple import v4_cadence as cadence
from joulewise.align.apple import v4_registration as registration
from scripts import align_v4_session as session


def window(name, *, captured=22):
    return {'window': name, 'status': 'final', 'captured_members': captured,
            'eligible_benign': {'spam': 7, 'bank': 7}}


def packet(windows, *, previous='C6', role='test'):
    return {
        'schema': cadence.TRIAGE_SCHEMA, 'previous_window': previous,
        'record_commit': 'b' * 40, 'last_desk_passed_artifact_set_sha256': 'a' * 64,
        'next_window_role': role, 'calibration_windows': windows,
        'checks': {name: {'status': 'pass', 'basis': 'synthetic committed record'}
                   for name in ('record_committed', 'terminal_completion', 'quiet_start_state',
                                'meter_reader_live', 'capture_faults', 'thermal_escalation',
                                'cohort_pool_rules', 'sentinel_roster', 'member_eligibility',
                                'full_desk_gate')},
    }


INTERNAL = {'series_powermode': True, 'external_volume': True, 'charging_battery': True}


@contextmanager
def synthetic_receipt(extra_path):
    with tempfile.TemporaryDirectory(prefix='r11-delta-sol2-receipt-') as temporary:
        root = Path(temporary)
        gates = {stage: f'docs/align/v4/synthetic-gate-{stage}.md' for stage in ('A', 'B')}
        for relative in (*registration.ARTIFACTS, *gates.values(), extra_path):
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text('# Synthetic reviewed bytes\n')

        def git(*args):
            return subprocess.run(
                ['git', '-c', 'core.hooksPath=/dev/null', *args], cwd=root,
                check=True, capture_output=True, text=True).stdout.strip()

        def commit(message):
            git('add', '.')
            git('-c', 'user.name=Synthetic', '-c', 'user.email=synthetic@example.invalid',
                'commit', '-qm', message)
            return git('rev-parse', 'HEAD')

        def digest(relative):
            return hashlib.sha256((root / relative).read_bytes()).hexdigest()

        git('init', '-q')
        reviewed = commit('Synthetic reviewed candidate')
        receipt = {
            'schema': registration.RECEIPT_SCHEMA, 'status': 'registered', 'commit': reviewed,
            'lead_signature': 'lead: synthetic-review 2026-11-08',
            'rulings': {str(n): 'installed' for n in registration.RULINGS},
            'artifacts': {relative: digest(relative) for relative in registration.ARTIFACTS},
            'gates': {stage: {'verdict': 'ADMIT', 'path': relative, 'sha256': digest(relative)}
                      for stage, relative in gates.items()},
        }
        registration.validate_receipt(receipt, root)
        yield root, receipt, git, commit


class ExecutedScriptBindingWitnesses(unittest.TestCase):
    def assert_script_drift_refused(self, relative):
        with synthetic_receipt(relative) as (root, receipt, git, commit):
            (root / relative).write_text('def main(*args, **kwargs):\n    return 0\n')
            self.assertNotEqual(commit('Synthetic unreviewed execution drift'), receipt['commit'])
            self.assertEqual(git('status', '--porcelain'), '')
            with self.assertRaises(ValueError, msg=f'executed script drift must invalidate admission: {relative}'):
                registration.validate_receipt(receipt, root)

    def test_receipt_binds_the_actual_prepare_install_helper(self):
        # align_v4_session -> align_pilot_session -> bytes_h_session.prepare/install.
        self.assert_script_drift_refused('scripts/bytes_h_session.py')

    def test_receipt_binds_the_spawned_hazard_monitor(self):
        # b5.driver.production_seams.monitor_argv launches it; AST imports miss argv paths.
        self.assert_script_drift_refused('scripts/hazard_monitor.py')

    def test_comment_only_b6_file_drift_currently_forces_registration_refresh(self):
        # Characterization of overbinding, not a request to drop shared B6 execution code.
        relative = 'joulewise/b6/model_files.py'
        self.assertIn(relative, registration.ARTIFACTS)
        with synthetic_receipt(relative) as (root, receipt, _git, commit):
            (root / relative).write_text('# Synthetic unrelated B6-only edit\n')
            commit('Synthetic B6-only maintenance')
            with self.assertRaisesRegex(ValueError, 'digest drift'):
                registration.validate_receipt(receipt, root)


class CalibrationCountWitnesses(unittest.TestCase):
    def test_eligible_counts_cannot_exceed_captured_members(self):
        valid = [window(f'C{i}') for i in range(1, 9)]
        self.assertEqual(cadence.calibration_stop(valid)['decision'], 'calibration_complete')      # fixed 8 (217)
        impossible = [window(f'C{i}', captured=1) for i in range(1, 9)]
        # Six captures cannot supply 42 eligible benign members for EACH pair.
        with self.assertRaises(ValueError):
            cadence.calibration_stop(impossible)

    def test_impossible_calibration_yield_cannot_admit_a_test_arm(self):
        impossible = [window(f'C{i}', captured=1) for i in range(1, 9)]
        result = cadence.next_arm_triage(packet(impossible), INTERNAL)
        self.assertFalse(result['admitted'], result)


class PostW1DeskWitness(unittest.TestCase):
    def test_inconsistent_w1_flag_cannot_defer_required_full_desk_at_arm(self):
        after_w1 = packet([], previous='W1', role='calibration')
        after_w1['checks']['full_desk_gate'] = {'status': 'deferred', 'basis': 'still running off MBP'}
        identity = {'artifact_set_sha256': 'a' * 64, 'record_commit_exists': True}
        self.assertFalse(cadence.next_arm_triage(after_w1, INTERNAL, identity)['admitted'])
        # A stale redundant flag must not override the packet's explicit W1 identity.
        bad = deepcopy(after_w1)
        bad['previous_window_is_w1'] = False          # stale flag contradicts the window id
        observation = dict(passed=True, probe_error=False, external_connected=True,
                           is_charging=False, update_age_s=1,
                           current_capacity_pct=100, instant_amperage_ma=0)
        with patch('joulewise.align.apple.powermode.admit_ac_powermode', return_value={'admitted': True}), \
             patch('joulewise.align.apple.powermode.host_marker_path', return_value='/synthetic-unused-marker'), \
             patch('joulewise.align.apple.powermode.host_state_dir', return_value='/synthetic-unused-state'), \
             patch('joulewise.align.apple.external_volume.census', return_value={'mounts': []}), \
             patch('joulewise.align.apple.external_volume.arm_check', return_value={'verdict': 'PASS'}), \
             patch('joulewise.battery_float.observe', return_value=(observation, b'synthetic')):
            run = lambda argv: subprocess.CompletedProcess(argv, 0, 'synthetic pmset', '')
            from tests.align.test_v4_cadence import write_battery_log
            with tempfile.TemporaryDirectory() as tmp:
                log = write_battery_log(Path(tmp) / 'battery.jsonl', 5000.)
                record = session.arm_checks(
                    '.', {}, runner=run, now=lambda: 5000., obc_off_attested_by='synthetic',
                    battery_log=log, commit_check=lambda root, commit: True,
                    record_check=lambda root, packet: True, next_arm_triage=bad)
        self.assertFalse(record['admitted'], record)


if __name__ == '__main__':
    unittest.main()
