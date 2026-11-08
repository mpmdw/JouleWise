"""R11 delta3 Sol1 review witnesses, synthetic inputs only.

Negative witnesses intentionally fail at 9891d679b. They specify the required
receipt/custody behavior; product repairs and their disposition belong to the
lead. No native launch, host probe, weights, network or study data is used.
"""
import hashlib
import json
from pathlib import Path
import plistlib
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest

from joulewise.align.apple import km003c as meter
from joulewise.align.apple import v4_cadence as cadence
from joulewise.align.apple import v4_registration as registration
from joulewise.align.apple import v4_topup as topup
from joulewise.external import km003c_parse as kp
from scripts import align_v4_session as session
from tests.align.test_r11_delta_sol1 import TemporaryCandidate
from tests.align.test_v4_cadence import INTERNAL, window
from tests.align.test_v4_receipt_tiers import amendment
from tests.align.test_v4_topup import NOW, obs

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = 'configs/launchd/com.joulewise.night.plist.template'


def fresh_imports(target):
    """Only import the entry point in a fresh interpreter; never call its main."""
    code = '''import json, sys
from pathlib import Path
__import__(sys.argv[1])
root = str(Path.cwd()) + '/'
paths = {str(m.__file__)[len(root):] for m in list(sys.modules.values())
         if isinstance(getattr(m, '__file__', None), str) and str(m.__file__).startswith(root)}
print(json.dumps(sorted(paths)))
'''
    result = subprocess.run([sys.executable, '-B', '-c', code, target], cwd=ROOT,
                            check=True, capture_output=True, text=True, timeout=30)
    return set(json.loads(result.stdout))


class ExecutedTierWitnesses(unittest.TestCase):
    def assert_imports_strict(self, target, expected):
        imported = fresh_imports(target)
        self.assertTrue(set(expected) <= imported)
        self.assertEqual(sorted(imported - set(registration.ARTIFACTS)), [])
        self.assertEqual(sorted(p for p in imported if not registration.is_strict(p)), [],
                         'a production import executes module-level code too')

    def test_production_night_imports_are_strict(self):
        self.assert_imports_strict('scripts.run_night', (
            'joulewise/arm_readiness_evidence_t0.py', 'joulewise/t0_rehearsal.py'))

    def test_measured_member_cli_imports_are_strict(self):
        # run_campaign.command_for uses python -m joulewise; __main__ imports cli.
        self.assert_imports_strict('joulewise.cli', (
            'joulewise/adapters/nvidia_smi.py', 'joulewise/adapters/node_client.py',
            'joulewise/kv_size.py', 'joulewise/report.py'))

    def test_watchdog_imports_are_strict(self):
        self.assert_imports_strict('scripts.magistrate_watchdog', (
            'joulewise/zero_capture_facts.py', 'scripts/fixture_orphan_census.py'))

    def test_actual_harvest_imports_are_strict(self):
        self.assert_imports_strict('scripts.harvest_b6_session', ('joulewise/session_structure.py',))

    def test_actual_install_programs_are_strict(self):
        # bytes_h_session.install launches the shell, which execs -m night_agent_install.
        shell = (ROOT / 'scripts/install_night_agent.sh').read_text()
        self.assertIn('-m joulewise.night_agent_install', shell)
        for path in ('scripts/install_night_agent.sh', 'joulewise/night_agent_install.py'):
            with self.subTest(path=path):
                self.assertIn(path, registration.ARTIFACTS)
                self.assertTrue(registration.is_strict(path))

    def test_signed_amendments_cannot_waive_executed_code_review(self):
        for path in ('scripts/install_night_agent.sh', 'joulewise/arm_readiness_evidence_t0.py'):
            with self.subTest(path=path), tempfile.TemporaryDirectory() as tmp:
                candidate = TemporaryCandidate(Path(tmp))
                candidate.receipt['amendments'] = [amendment(candidate, path, '# changed executable bytes\n')]
                self.assertEqual(candidate.git('status', '--porcelain'), '')
                with self.assertRaises(ValueError, msg=f'executed code amendment admitted: {path}'):
                    registration.validate_receipt(candidate.receipt, candidate.root)

    def test_production_night_scenario_stays_inside_the_strict_receipt(self):
        # The already-existing short production supervisor fixture uses only
        # synthetic child programs and mocks its process census/hardware seams.
        code = '''import contextlib, io, json
from scripts import align_v4_dynamic_trace as t
scenario = ('night', {}, ['tests.align.test_km003c.NightChainTests.test_existing_block_supervisor_covers_first_idle_through_last_member_and_hashes'])
with contextlib.redirect_stdout(io.StringIO()):
    report, recorder, children = t.run_scenarios([scenario])
print(json.dumps({'ok': report['night']['ok'], 'paths': sorted(set(recorder.paths()) | set(children))}))
'''
        result = subprocess.run([sys.executable, '-B', '-c', code], cwd=ROOT,
                                check=True, capture_output=True, text=True, timeout=60)
        trace = json.loads(result.stdout)
        self.assertTrue(trace['ok'], result.stderr)
        paths = set(trace['paths'])
        self.assertIn('scripts/run_night.py', paths)
        self.assertEqual(sorted(paths - set(registration.ARTIFACTS)), [])
        with self.subTest(contract='strict execution'):
            self.assertEqual(sorted(p for p in paths if not registration.is_strict(p)), [])
        committed = json.loads((ROOT / 'docs/align/v4/dynamic_closure_trace.json').read_text())
        with self.subTest(contract='production scenario coverage'):
            self.assertEqual(sorted(paths - set(committed['executed'])), [])


class LaunchTemplateWitnesses(unittest.TestCase):
    def test_launch_argument_template_drift_requires_a_new_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidate = TemporaryCandidate(Path(tmp))
            original = (ROOT / TEMPLATE).read_text()
            candidate.write(TEMPLATE, original)
            candidate.receipt['commit'] = candidate.commit('Synthetic reviewed launch template')
            if TEMPLATE in candidate.receipt['artifacts']:
                candidate.receipt['artifacts'][TEMPLATE] = candidate.digest(TEMPLATE)
            registration.validate_receipt(candidate.receipt, candidate.root)
            candidate.write(TEMPLATE, original.replace('@@REPO@@/scripts/run_night.py',
                                                       '@@REPO@@/scripts/align_r1_runtime.py'))
            candidate.commit('Synthetic changed clean launch arguments')
            self.assertEqual(candidate.git('status', '--porcelain'), '')
            with self.assertRaises(ValueError, msg='unreviewed production launch arguments admitted'):
                registration.validate_receipt(candidate.receipt, candidate.root)

    def test_template_actually_controls_rendered_production_argv_without_launching(self):
        from joulewise.night_agent_install import Prepared
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            prepared = Prepared(SimpleNamespace(receipt_class='HAZARD_PACK', custody_root=str(root)),
                                root / 'night_plan.json', root, sys.executable,
                                (ROOT / TEMPLATE).read_text(), '/bin/true', '/usr/bin:/bin',
                                {'night_calendar': {'Month': 11, 'Day': 8, 'Hour': 1, 'Minute': 0}}, None)
            before = plistlib.loads(next(prepared.render(['com.joulewise.night']))[1])
            prepared.template = prepared.template.replace('@@REPO@@/scripts/run_night.py',
                                                          '@@REPO@@/scripts/align_r1_runtime.py')
            after = plistlib.loads(next(prepared.render(['com.joulewise.night']))[1])
            self.assertEqual(before['ProgramArguments'][1], str(root / 'scripts/run_night.py'))
            self.assertEqual(after['ProgramArguments'][1], str(root / 'scripts/align_r1_runtime.py'))


class RecordFreshnessWitnesses(unittest.TestCase):
    def test_packet_for_an_older_window_refuses_after_a_new_record_at_a_new_path(self):
        from tests.align.test_v4_record_binding import RecordBindingTests
        helper = RecordBindingTests()
        helper.setUp()
        try:
            commit, digest = helper.commit('staging/window-C2-record.json', '{"window":"C2"}\n')
            packet = helper.packet(commit, digest)
            helper.commit('staging/window-C3-record.json', '{"window":"C3","thermal":"fail"}\n')
            identity = helper.arm_identity(packet)
            self.assertEqual(helper.git('status', '--porcelain'), '')
            self.assertFalse(cadence.next_arm_triage(packet, INTERNAL, identity)['admitted'],
                             'a packet naming C2 is stale after C3 closes at its own record path')
        finally:
            helper.doCleanups()

    def test_unrelated_commit_is_allowed_but_same_record_recommit_refuses(self):
        from tests.align.test_v4_record_binding import RecordBindingTests
        helper = RecordBindingTests()
        helper.setUp()
        try:
            commit, digest = helper.commit('staging/window-C2-record.json', '{"window":"C2"}\n')
            packet = helper.packet(commit, digest)
            helper.commit('docs/unrelated.md', 'unrelated\n')
            self.assertTrue(session._record_bound(helper.root, packet))
            helper.commit('staging/window-C2-record.json', '{"window":"C2","revised":true}\n')
            self.assertFalse(session._record_bound(helper.root, packet))
        finally:
            helper.doCleanups()


class MeterCustodyWitnesses(unittest.TestCase):
    def test_an_unlisted_unclosed_stream_cannot_preempt_the_hash_bound_stream(self):
        from tests.align.test_km003c import DeskTests
        with tempfile.TemporaryDirectory() as tmp:
            custody, runs, stream, plan, summaries = DeskTests().fixture(Path(tmp))
            # A stray copy in custody, absent from the supervisor's stream roster.
            # Same sample times, twice the current, no trailer; the genuine stream
            # remains intact and correctly hashed. No deliberate forger is needed.
            stray = stream.with_name('stream-000.jsonl')
            rows = [json.loads(line) for line in stream.read_text().splitlines()]
            for row in rows:
                if row['k'] == 'b':
                    fields = list(kp.SAMPLE.unpack(bytes.fromhex(row['p'])))
                    fields[3] *= 2
                    row['p'] = kp.SAMPLE.pack(*fields).hex()
            stray.write_text(''.join(json.dumps(r) + '\n' for r in rows if r['k'] != 't'))
            result = meter.session_report(custody, plan, runs, summaries)['members']['member']
            self.assertEqual(result['status'], 'available')
            self.assertEqual(result['stream'], stream.relative_to(custody).as_posix())
            self.assertEqual(result['dc_in_energy_j'], 84.)

    def test_known_unclosed_stream_salvages_only_covered_members_when_its_digest_is_recorded(self):
        # Lead disposition 2026-11-08: salvage needs a LISTED, supervised stream with a RECORDED matching
        # digest; the review witness's hashless variant is the opposite case, now excluded (next test).
        from tests.align.test_km003c import DeskTests
        with tempfile.TemporaryDirectory() as tmp:
            custody, runs, stream, plan, summaries = DeskTests().crashed_fixture(Path(tmp), record_hash=True)
            before = hashlib.sha256(stream.read_bytes()).hexdigest()
            report = meter.session_report(custody, plan, runs, summaries)
            row = report['members']['member']
            self.assertEqual((row['status'], row['dc_in_energy_j']), ('available', 56.))
            self.assertIn('meter.stream_unclosed', row['flags'])
            self.assertEqual(report['members']['late']['status'], 'missing')
            self.assertEqual(hashlib.sha256(stream.read_bytes()).hexdigest(), before)

    def test_listed_stream_without_a_recorded_digest_is_excluded_not_salvaged(self):
        from tests.align.test_km003c import DeskTests
        with tempfile.TemporaryDirectory() as tmp:
            custody, runs, stream, plan, summaries = DeskTests().crashed_fixture(Path(tmp), record_hash=False)
            row = meter.session_report(custody, plan, runs, summaries)['members']['member']
            self.assertEqual(row['status'], 'missing')
            self.assertIn('meter.custody_digest_unrecorded', row['flags'])

    def test_recorded_digest_mismatch_is_not_salvaged_after_trailer_removal(self):
        from tests.align.test_km003c import DeskTests
        with tempfile.TemporaryDirectory() as tmp:
            custody, runs, stream, plan, summaries = DeskTests().fixture(Path(tmp))
            stream.write_text(''.join(line + '\n' for line in stream.read_text().splitlines()
                                      if json.loads(line)['k'] != 't'))
            row = meter.session_report(custody, plan, runs, summaries)['members']['member']
            self.assertEqual(row['status'], 'missing')
            self.assertIn('meter.custody_hash_mismatch', row['flags'])


class TopupAndRosterControls(unittest.TestCase):
    def test_charge_pair_raw_order_and_basis_a_boundary(self):
        pair = [obs(NOW-1900, charging=True, pct=97), obs(NOW-1800)]
        gap = [*pair, obs(NOW-100)]
        self.assertEqual(topup.derive(gap, NOW)['basis'], 'completed_charge')
        self.assertFalse(topup.derive(gap, NOW+.001)['admissible'])
        self.assertFalse(topup.derive([pair[0], obs(NOW-1850, error=True), *gap[1:]], NOW)['admissible'])
        self.assertFalse(topup.derive([pair[0], obs(NOW-1850, ac=False), *gap[1:]], NOW)['admissible'])

    def test_old_charge_continuity_breaks_cannot_be_hidden(self):
        rows = [obs(NOW-3300, charging=True, pct=97)] + [obs(NOW-3000+300*i) for i in range(11)]
        self.assertEqual(topup.derive(rows, NOW)['basis'], 'continuous_float')
        for bad in ({'probe_error': True, 'wall_time_s': None}, obs(NOW-2850, ac=False)):
            with self.subTest(bad=bad):
                self.assertFalse(topup.derive([*rows[:2], bad, *rows[2:]], NOW)['admissible'])
        self.assertFalse(topup.derive(rows[:3]+rows[4:], NOW)['admissible'])

    def test_twenty_four_capture_roster_keeps_the_seven_per_pair_and_fixed_eight_limits(self):
        rows = [window(f'C{i}', 7, 7, captured=24) for i in range(1, 9)]
        result = cadence.calibration_stop(rows)
        self.assertEqual(result['decision'], 'calibration_complete')
        self.assertEqual(result['eligible_by_pair'], {'spam': 56, 'bank': 56})
        with self.assertRaises(ValueError):
            cadence.calibration_stop([*rows[:-1], window('C8', 7, 7, captured=25)])
        with self.assertRaises(ValueError):
            cadence.calibration_stop([*rows[:-1], window('C8', 8, 7, captured=24)])
        self.assertEqual(cadence.calibration_stop(rows[:-1])['decision'], 'continue')


if __name__ == '__main__':
    unittest.main()
