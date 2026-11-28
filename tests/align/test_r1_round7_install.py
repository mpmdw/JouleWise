"""R7-6: census launchd before any High Power install command (fake host only)."""
import os
import subprocess

from tests.align import test_r1_round6_power as power_tests
from tests.align.test_v4_kit import FakeArmHost


CENSUS = ('launchctl', 'print', f'gui/{os.getuid()}/com.joulewise.night')


class InstallCensusTests(power_tests.HostStateCase):
    make_session = power_tests.V4SessionHighPowerTests.make_session
    install = power_tests.V4SessionHighPowerTests.install

    def assert_no_power_or_install(self, host):
        self.assertEqual(host.mode, 0)
        self.assertFalse(any('pmset' in arg for call in host.calls for arg in call), host.calls)
        self.assertNotIn(power_tests.SET_HIGH, host.calls)
        self.assertFalse(self.marker.exists())
        self.assertFalse(self.installer_called)

    def test_loaded_night_job_refuses_without_any_pmset(self):
        _measurement, root = self.make_session()
        host = FakeArmHost(mode=0, marker=self.marker, night_job_loaded=True)
        with self.assertRaisesRegex(ValueError, 'launchd already holds the night job'):
            self.install(root, host)
        self.assertEqual(host.calls, [CENSUS])
        self.assert_no_power_or_install(host)

    def test_unavailable_job_state_refuses_without_any_pmset(self):
        _measurement, root = self.make_session()
        # Exit 113 alone is insufficient: the exact absent line must be on stderr.
        absent = f'Could not find service "com.joulewise.night" in domain for user gui: {os.getuid()}'
        for code, stdout, stderr in ((1, '', 'permission denied'), (113, absent, ''),
                                     (113, '', absent + ' (unverified)')):
            with self.subTest(code=code, stdout=stdout, stderr=stderr):
                host = FakeArmHost(mode=0, marker=self.marker)

                def unavailable(argv):
                    if tuple(argv) == CENSUS:
                        host.calls.append(tuple(argv))
                        return subprocess.CompletedProcess(argv, code, stdout, stderr)
                    return host(argv)

                with self.assertRaisesRegex(ValueError, 'launchd job state unavailable'):
                    self.install(root, unavailable)
                self.assertEqual(host.calls, [CENSUS])
                self.assert_no_power_or_install(host)

    def test_absent_job_census_precedes_set_high(self):
        _measurement, root = self.make_session()
        host = FakeArmHost(mode=0, marker=self.marker)
        self.install(root, host)
        self.assertIn(CENSUS, host.calls)
        self.assertLess(host.calls.index(CENSUS), host.calls.index(power_tests.SET_HIGH))
        self.assertEqual(host.mode, 2)
        self.assertTrue(self.marker.exists())
        self.assertTrue(self.installer_called)


class InstallRecordsTests(power_tests.HostStateCase):
    """R7-10: the arm and session-start records carry the host state dir."""
    make_session = power_tests.V4SessionHighPowerTests.make_session
    install = power_tests.V4SessionHighPowerTests.install

    def test_arm_and_session_start_records_name_the_host_state_dir(self):
        import json
        from joulewise.align.apple import powermode
        _measurement, root = self.make_session()
        self.w1_marker(self.tmp / 'an-abandoned-session/custody')
        host = FakeArmHost(mode=2, marker=self.marker)
        self.install(root, host)
        arm = json.loads((root / 'staging/v4-arm-001.json').read_text())
        [start] = (root / 'staging').glob('v4-session-start-restore-*.json')
        for record in (arm, json.loads(start.read_text())):
            self.assertEqual(record['host_state_dir'], powermode.host_state_dir())
            self.assertEqual(record['host_state_dir'], str(self.tmp / 'host-power'))


class InstallSignalTests(power_tests.HostStateCase):
    """R7-4 with real signals: an install parked in the shared installer
    after it entered High Power must restore Automatic on TERM or HUP."""

    CHILD = r'''
import json, time
from unittest.mock import patch
from joulewise.align.apple import powermode
from scripts import align_pilot_session as pilot, align_v4_kit as kit, align_v4_session as session
from tests.align import test_r1_round6_power as power_tests
from tests.align.test_v4_kit import FakeArmHost, W1DiskGateTests, topup
from tests.align.v4_registration_fixtures import held_window_acceptance
case = power_tests.V4SessionHighPowerTests("test_the_w1_marker_is_host_level_and_names_its_session")
case.setUp()
_measurement, root = case.make_session()
host = FakeArmHost(mode=0, marker=case.marker)
def parked(*args, **kwargs):
    print(json.dumps({"parked": powermode.host_state_dir(), "mode": host.mode}), flush=True)
    time.sleep(60)
    raise AssertionError("not signalled")
outcome = {}
try:
    # The arm now needs its registered evidence (OBC attestation, battery top-up log, next-arm triage with the
    # arm's own packet rebuild, live meter, dwell order) before High Power is entered, exactly as the in-process
    # V4SessionHighPowerTests.install helper supplies it; kit.generate is patched there too.
    with patch.object(kit, "require_w1_ready"), patch.object(kit, "generate"), \
            patch.object(session, "held_window_check", side_effect=held_window_acceptance), \
            patch.object(pilot, "install", side_effect=parked):
        session.install(root, runner=host, volume_runner=host, obc_off_attested_by="synthetic",
                        w1_disk_config=W1DiskGateTests.config(case, case.tmp), **topup(),
                        disk_gate=lambda c: {"status": "pass", "offloads": []})
except BaseException as error:
    outcome["raised"] = type(error).__name__ + ": " + str(error)
outcome.update(mode=host.mode, marker=case.marker.exists(),
               restores=[json.loads(p.read_text())["ok"] for p in (root / "staging").glob("v4-arm-restore-*.json")])
print(json.dumps(outcome), flush=True)
'''

    def run_and_signal(self, signum):
        import json
        import signal as _signal  # noqa: F401
        import sys
        import tempfile
        from pathlib import Path
        from unittest import mock
        from joulewise.align.apple import powermode
        root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as tmp:
            child = subprocess.Popen([sys.executable, '-B', '-c', self.CHILD], cwd=root, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, text=True,
                                     env=dict(os.environ, PYTHONPATH=str(root), TMPDIR=tmp))
            try:
                parked = json.loads(child.stdout.readline())
                self.assertEqual(parked['mode'], 2)            # High Power entered
                with mock.patch.dict(os.environ, {powermode.HOST_STATE_ENV: parked['parked']}):
                    self.assertFalse(powermode.HostLock(role='probe').acquire())   # the install holds it
                child.send_signal(signum)
                out, err = child.communicate(timeout=60)
            finally:
                if child.poll() is None:
                    child.kill()
                    child.communicate()
        self.assertEqual(child.returncode, 0, err)
        return json.loads(out.strip().splitlines()[-1])

    def test_sigterm_restores_automatic(self):
        import signal
        outcome = self.run_and_signal(signal.SIGTERM)
        self.assertIn('KeyboardInterrupt', outcome.get('raised', ''))
        self.assertEqual((outcome['mode'], outcome['marker'], outcome['restores']), (0, False, [True]))

    def test_sighup_restores_automatic(self):
        import signal
        outcome = self.run_and_signal(signal.SIGHUP)
        self.assertIn('KeyboardInterrupt', outcome.get('raised', ''))
        self.assertEqual((outcome['mode'], outcome['marker'], outcome['restores']), (0, False, [True]))
