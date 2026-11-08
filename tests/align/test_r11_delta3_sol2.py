"""R11 delta3 Sol2 review witnesses: synthetic code, records and streams only.

Negative witnesses intentionally fail at 9891d679b. They exercise receipt
classification, ordinary stale-packet reuse, and a stray meter file; no live
runner, hardware probe, model, measurement data, or network is invoked.
"""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from joulewise.align.apple import km003c as meter
from joulewise.align.apple import v4_cadence as cadence
from joulewise.align.apple import v4_registration as registration
from joulewise.align.apple import v4_topup as topup
from scripts import align_v4_session as session, bytes_h_session
from tests.align import test_km003c as meter_fixtures
from tests.align.test_r11_delta_sol1 import TemporaryCandidate
from tests.align.test_v4_cadence import INTERNAL, IDENTITY, passing_packet, window
from tests.align.test_v4_topup import NOW, obs

ROOT = Path(__file__).resolve().parents[2]


class ProductionImportWitnesses(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Import only. Neither main() nor a probe/measurement entry point runs.
        code = '''import json, sys
from pathlib import Path
from scripts import run_night, run_campaign, harvest_b6_session, magistrate_watchdog
from joulewise import cli, night_agent_install
root = Path.cwd()
paths = sorted({Path(m.__file__).relative_to(root).as_posix()
                for m in list(sys.modules.values())
                if getattr(m, '__file__', None) and str(m.__file__).startswith(str(root) + '/')})
print(json.dumps(paths))
'''
        result = subprocess.run([sys.executable, '-B', '-c', code], cwd=ROOT,
                                capture_output=True, text=True, timeout=60, check=True)
        cls.imported = set(json.loads(result.stdout))

    def test_production_entry_imports_are_receipt_bound(self):
        self.assertEqual(sorted(self.imported - set(registration.ARTIFACTS)), [])

    def test_production_entry_imports_cannot_use_the_not_executed_allowlist(self):
        for path in sorted(self.imported & set(registration.AMENDMENT_ALLOWLIST)):
            with self.subTest(path=path):
                self.assertTrue(registration.is_strict(path), 'module body executes at production startup')

    def test_signed_amendment_cannot_waive_executed_night_startup_code(self):
        path = 'joulewise/arm_readiness_evidence_t0.py'
        self.assertIn(path, self.imported)
        with tempfile.TemporaryDirectory() as tmp:
            candidate = TemporaryCandidate(Path(tmp))
            candidate.write(path, 'synthetic changed module initialization\n')
            candidate.commit('Synthetic startup change')
            candidate.receipt['amendments'] = [{
                'path': path, 'old_sha256': candidate.receipt['artifacts'][path],
                'new_sha256': candidate.digest(path), 'reason': 'synthetic startup repair',
                'lead_signature': 'lead: synthetic-delta3-sol2 2026-11-08',
            }]
            self.assertEqual(candidate.git('status', '--porcelain'), '')
            with self.assertRaises(ValueError):
                registration.validate_receipt(candidate.receipt, candidate.root)

    def test_session_install_launches_only_strict_receipt_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'staging').mkdir()
            plan = root / 'plan.json'
            plan.write_text(json.dumps({'t0_epoch_s': 1000}))
            state = {'measurement_root': str(ROOT), 'plan_path': str(plan),
                     'plan_sha256': hashlib.sha256(plan.read_bytes()).hexdigest(),
                     'inputs': {'custody_root': str(root / 'custody')}}
            (root / 'session.json').write_text(json.dumps(state))
            launched = []

            def run(argv, **kwargs):
                if argv[0] == 'launchctl':
                    absent = f'Could not find service "com.joulewise.night" in domain for user gui: {os.getuid()}'
                    return subprocess.CompletedProcess(argv, 113, '', absent)
                launched.append(Path(argv[0]).relative_to(ROOT).as_posix())
                return subprocess.CompletedProcess(argv, 0, 'synthetic installer', '')

            with contextlib.redirect_stdout(io.StringIO()):
                bytes_h_session.install(root, run=run, home=root / 'fake-home', now=lambda: 100.)
            self.assertEqual(launched, ['scripts/install_night_agent.sh'])
            # The wrapper execs python -m joulewise.night_agent_install (line 92).
            for path in (*launched, 'joulewise/night_agent_install.py'):
                with self.subTest(path=path):
                    self.assertIn(path, registration.ARTIFACTS)
                    self.assertTrue(registration.is_strict(path), 'real W1 installer code must be strict')


class RecordFreshnessWitnesses(unittest.TestCase):
    def test_new_window_record_at_a_new_path_invalidates_old_window_packet(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            def git(*args):
                return subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', *args], cwd=root,
                                      check=True, capture_output=True, text=True).stdout.strip()

            def commit_record(name, value):
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(value) + '\n')
                git('add', '.')
                git('-c', 'user.name=Synthetic', '-c', 'user.email=s@example.invalid',
                    'commit', '-qm', 'Synthetic completed window')
                return git('rev-parse', 'HEAD'), hashlib.sha256(path.read_bytes()).hexdigest()

            def commit_ledger(commit, path, digest):
                ledger = root / 'series/state.json'
                ledger.parent.mkdir(parents=True, exist_ok=True)
                ledger.write_text(json.dumps({'previous_record': {'commit': commit, 'path': path, 'sha256': digest}}) + '\n')
                git('add', '.')
                git('-c', 'user.name=Synthetic', '-c', 'user.email=s@example.invalid',
                    'commit', '-qm', 'Synthetic series ledger')
                return hashlib.sha256(ledger.read_bytes()).hexdigest()

            git('init', '-q')
            path = 'staging/window-C2-record.json'
            commit, digest = commit_record(path, {'window': 'C2', 'status': 'final'})
            series_sha = commit_ledger(commit, path, digest)
            packet = passing_packet(record_path=path, record_commit=commit, record_sha256=digest,
                                    series_path='series/state.json', series_sha256=series_sha)
            self.assertTrue(session._record_bound(root, packet))
            # the next window's record moves the canonical ledger; the old packet goes stale
            new_commit, new_digest = commit_record('staging/window-C3-record.json', {'window': 'C3', 'status': 'final'})
            commit_ledger(new_commit, 'staging/window-C3-record.json', new_digest)
            self.assertEqual(git('status', '--porcelain'), '')
            identity = {**IDENTITY, 'record_commit_exists': session._commit_exists(root, commit),
                        'record_bound': session._record_bound(root, packet)}
            result = cadence.next_arm_triage(packet, INTERNAL, identity)
            self.assertFalse(result['admitted'], 'C2 is no longer the last committed window record')


class MeterCustodyWitnesses(unittest.TestCase):
    def fixture(self, root, *, record_hash=False):
        return meter_fixtures.DeskTests().crashed_fixture(root, record_hash=record_hash)

    def test_supervised_unclosed_stream_salvages_only_covered_members(self):
        with tempfile.TemporaryDirectory() as tmp:
            custody, runs, stream, plan, summaries = self.fixture(Path(tmp), record_hash=True)   # lead: recorded digest
            report = meter.session_report(custody, plan, runs, summaries)
            self.assertEqual(report['members']['member']['status'], 'available')
            self.assertIn('meter.stream_unclosed', report['members']['member']['flags'])
            self.assertEqual(report['members']['late']['status'], 'missing')

    def test_unlisted_unclosed_file_cannot_replace_the_supervised_stream(self):
        with tempfile.TemporaryDirectory() as tmp:
            custody, runs, stream, plan, summaries = self.fixture(Path(tmp))
            # Ordinary stale-copy/wrong-file mistake: the only file present is
            # stream-099; supervision names stream-001, never stream-099.
            stream.rename(stream.with_name('stream-099.jsonl'))
            row = meter.session_report(custody, plan, runs, summaries)['members']['member']
            self.assertEqual(row['status'], 'missing', 'an unlisted file has no capture provenance')
            self.assertIsNone(row['dc_in_energy_j'])

    def test_missing_supervision_record_cannot_authenticate_a_stray_stream(self):
        with tempfile.TemporaryDirectory() as tmp:
            custody, runs, stream, plan, summaries = self.fixture(Path(tmp))
            (custody / 'night/hazard_result.json').unlink()
            row = meter.session_report(custody, plan, runs, summaries)['members']['member']
            self.assertEqual(row['status'], 'missing', 'no supervised reader is evidenced')

    def test_recorded_digest_refuses_a_modified_unclosed_stream(self):
        with tempfile.TemporaryDirectory() as tmp:
            custody, runs, stream, plan, summaries = self.fixture(Path(tmp), record_hash=True)
            stream.write_bytes(stream.read_bytes() + b'\n')
            row = meter.session_report(custody, plan, runs, summaries)['members']['member']
            self.assertEqual(row['status'], 'missing')
            self.assertIn('meter.custody_hash_mismatch', row['flags'])


class TopupAndRosterControls(unittest.TestCase):
    def test_transition_requires_two_consecutive_valid_rows(self):
        for fault in (obs(NOW-1100, ac=False), obs(NOW-1100, error=True),
                      {'schema': topup.SCHEMA, 'probe_error': True, 'wall_time_s': None}):
            rows = [obs(NOW-1200, charging=True, pct=97), fault, obs(NOW-1000), obs(NOW-100)]
            with self.subTest(fault=fault):
                self.assertFalse(topup.derive(rows, NOW)['admissible'])

    def test_recent_completion_and_old_continuous_float_are_separate_bases(self):
        recent = [obs(NOW-1900, charging=True, pct=97), obs(NOW-1800), obs(NOW-100)]
        result = topup.derive(recent, NOW)
        self.assertTrue(result['admissible'], result['reasons'])
        self.assertEqual(result['basis'], 'completed_charge')
        old = [obs(NOW-2100, charging=True, pct=97)] + [obs(NOW-2000+i*100) for i in range(21)]
        result = topup.derive(old, NOW)
        self.assertTrue(result['admissible'], result['reasons'])
        self.assertEqual(result['basis'], 'continuous_float')
        for fault in (obs(NOW-950, ac=False), obs(NOW-950, error=True),
                      {'schema': topup.SCHEMA, 'probe_error': True, 'wall_time_s': None}):
            rows = old[:12] + [fault] + old[12:]
            with self.subTest(fault=fault):
                self.assertFalse(topup.derive(rows, NOW)['admissible'])

    def test_transition_gap_stale_tail_and_raw_reordering_refuse(self):
        cases = ([obs(NOW-1000, charging=True, pct=97), obs(NOW-600), obs(NOW-100)],
                 [obs(NOW-1000, charging=True, pct=97), obs(NOW-900)],
                 [obs(NOW-1000, charging=True, pct=97), obs(NOW-900), obs(NOW-950), obs(NOW-100)])
        for rows in cases:
            with self.subTest(rows=rows):
                self.assertFalse(topup.derive(rows, NOW)['admissible'])

    def test_24_captures_do_not_expand_the_calibrator_pool(self):
        rows = [window(f'C{i}', 7, 7, captured=24) for i in range(1, 9)]
        result = cadence.calibration_stop(rows)
        self.assertEqual(result['decision'], 'calibration_complete')
        self.assertEqual(result['eligible_by_pair'], {'spam': 56, 'bank': 56})
        for change in ({'captured_members': 25}, {'eligible_benign': {'spam': 8, 'bank': 7}}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                cadence.calibration_stop([dict(rows[0], **change), *rows[1:]])


if __name__ == '__main__':
    unittest.main()
