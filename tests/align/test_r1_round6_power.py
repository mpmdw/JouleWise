"""Lead ruling R6-7: no exit path leaves the host at AC powermode 2 unrestored.

The High Power marker lives at one host-level path every session, night and
the watchdog see; a measuring night holds the host night lock, and nothing
restores under it. Fake sudo/pmset only; nothing real runs. (The run_night
exit paths are in tests/test_run_night.py, the watchdog J4 restore in
tests/test_magistrate_watchdog.py.)
"""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from joulewise.align.apple import powermode
from scripts import align_pilot_session as pilot, align_r1_rehearsal as r1, align_v4_kit as kit
from scripts import align_v4_session as session
from tests.align import test_r1_rehearsal as rehearsal_tests
from tests.align.test_v4_kit import FakeArmHost, W1DiskGateTests

SET_HIGH = ('sudo', '-n', '/usr/bin/pmset', '-c', 'powermode', '2')
RESTORE = ('sudo', '-n', '/usr/bin/pmset', '-c', 'powermode', '0')


class HostStateCase(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.tmp = Path(temporary.name)
        env = patch.dict(os.environ, {powermode.HOST_STATE_ENV: str(self.tmp / 'host-power')})
        env.start()
        self.addCleanup(env.stop)
        self.marker = Path(powermode.host_marker_path())

    def hold_lock_elsewhere(self):
        other = powermode.HostLock(role='a measuring night')
        self.assertTrue(other.acquire())
        self.addCleanup(other.release)
        return other

    def w1_marker(self, custody_root):
        powermode.write_host_marker(self.marker, tag=powermode.W1_MARKER_TAG,
                                    owner={'custody_root': custody_root})


class HostLevelPrimitivesTests(HostStateCase):
    def test_host_paths_are_outside_any_session_and_follow_the_override(self):
        self.assertEqual(Path(powermode.host_state_dir()), self.tmp / 'host-power')
        with patch.dict(os.environ, {powermode.HOST_STATE_ENV: ''}):
            self.assertEqual(powermode.host_state_dir(), powermode.HOST_STATE_DEFAULT)
        self.assertFalse(powermode.HOST_STATE_DEFAULT.startswith(str(Path.home())))

    def test_the_night_lock_dies_with_its_holder_even_on_sigkill(self):
        code = ('import sys, time; from joulewise.align.apple import powermode; '
                'lock = powermode.HostLock(); assert lock.acquire(); print("held", flush=True); time.sleep(60)')
        root = Path(__file__).resolve().parents[2]
        holder = subprocess.Popen([sys.executable, '-B', '-c', code], cwd=root, stdout=subprocess.PIPE, text=True,
                                  env=dict(os.environ, PYTHONPATH=str(root)))
        try:
            self.assertEqual(holder.stdout.readline().strip(), 'held')
            self.assertFalse(powermode.HostLock().acquire())
            holder.send_signal(signal.SIGKILL)
            holder.wait(timeout=10)
            lock = powermode.HostLock()
            self.assertTrue(lock.acquire(wait_s=5, poll_s=0.05))
            lock.release()
        finally:
            if holder.poll() is None:
                holder.kill()
                holder.wait()
            holder.stdout.close()

    def test_restore_owed_respects_owner_and_a_measuring_night(self):
        mine, other = self.tmp / 'mine/custody', self.tmp / 'other/custody'
        self.w1_marker(other)
        host = FakeArmHost(mode=2)
        record = powermode.restore_owed([self.marker], runner=host, owner={'custody_root': mine}, reason='t')
        self.assertEqual((record['action'], host.mode), ('not_owner', 2))
        self.w1_marker(mine)
        lock = self.hold_lock_elsewhere()
        record = powermode.restore_owed([self.marker], runner=host, owner={'custody_root': mine}, reason='t')
        self.assertEqual((record['action'], host.mode, host.calls), ('deferred_measuring_night', 2, []))
        lock.release()
        record = powermode.restore_owed([self.marker], runner=host, owner={'custody_root': mine}, reason='t')
        self.assertEqual((record['action'], host.mode), ('restored', 0))
        self.assertFalse(self.marker.exists())
        self.assertEqual(powermode.restore_owed([self.marker], runner=host, reason='t')['action'], 'none')

    def test_admission_restores_a_host_marker_but_never_under_a_measuring_night(self):
        powermode.write_host_marker(self.marker, tag=powermode.R1_MARKER_TEXT)
        host = FakeArmHost(mode=2)
        lock = self.hold_lock_elsewhere()
        refused = powermode.admit_ac_powermode(0, markers=[self.marker], runner=host)
        self.assertFalse(refused['admitted'])
        self.assertIn('holds the host night lock', refused['reason'])
        self.assertNotIn(RESTORE, host.calls)
        lock.release()
        admitted = powermode.admit_ac_powermode(0, markers=[self.marker], runner=host)
        self.assertTrue(admitted['admitted'])
        self.assertFalse(self.marker.exists())


class V4SessionHighPowerTests(HostStateCase):
    """install: host-level marker naming the session; the installer's no-op
    return restores; session start restores a foreign marker; never under a
    measuring night."""

    def make_session(self, ac_powermode=2):
        measurement = self.tmp / 'm'
        (measurement / kit.KIT).mkdir(parents=True, exist_ok=True)
        from tests.align.test_v4_kit import seed_series
        seed_series(measurement)
        (measurement / kit.KIT / 'collection_plan.json').write_text(json.dumps(
            {'runtime_requirements': {'ac_powermode': ac_powermode}}))
        root = self.tmp / 's'
        (root / 'staging').mkdir(parents=True, exist_ok=True)
        self.custody = self.tmp / 's/custody'
        (root / 'session.json').write_text(json.dumps(
            {'measurement_root': str(measurement), 'inputs': {'custody_root': str(self.custody)},
             'plan_path': str(self.custody / 'night_plan.json')}))
        return measurement, root

    def install(self, root, host, *, installed=None):
        from tests.align.test_v4_kit import topup
        with patch.object(kit, 'require_w1_ready'), patch.object(kit, 'generate'), \
                patch.object(pilot, 'install', return_value={'exit_code': 0} if installed is None else installed) \
                as install:
            try:
                return session.install(root, runner=host, volume_runner=host, obc_off_attested_by='synthetic',
                                       w1_disk_config=W1DiskGateTests.config(self, self.tmp), **topup(),
                                       disk_gate=lambda c: {'status': 'pass', 'offloads': []})
            finally:
                self.installer_called = install.called

    def test_the_w1_marker_is_host_level_and_names_its_session(self):
        measurement, root = self.make_session()
        host = FakeArmHost(mode=0, marker=self.marker)
        self.install(root, host)
        self.assertEqual(host.mode, 2)
        self.assertTrue(powermode.w1_marker(self.marker))
        self.assertTrue(powermode.owned_by(self.marker, custody_root=self.custody))
        self.assertFalse((measurement / powermode.R1_HIGH_POWER_MARKER).exists())
        # A later session (its own measurement view) sees the same marker.
        self.assertEqual(Path(powermode.host_marker_path()), self.marker)

    def test_an_installer_that_installs_nothing_restores_automatic(self):
        # Round-5 cold pass MEDIUM-1: launchd already holds a night job, so the
        # shared installer returns without installing; the host stayed at 2.
        _measurement, root = self.make_session()
        host = FakeArmHost(mode=0, marker=self.marker)
        with self.assertRaisesRegex(ValueError, 'did not install'):
            self.install(root, host, installed={})
        self.assertTrue(self.installer_called)
        self.assertEqual(host.mode, 0)
        self.assertFalse(self.marker.exists())
        [restore] = (root / 'staging').glob('v4-arm-restore-*.json')
        self.assertTrue(json.loads(restore.read_text())['ok'])

    def test_session_start_restores_a_foreign_marker_and_keeps_its_own(self):
        _measurement, root = self.make_session()
        self.w1_marker(self.tmp / 'an-abandoned-session/custody')
        host = FakeArmHost(mode=2, marker=self.marker)
        self.install(root, host)
        self.assertEqual(host.calls.index(RESTORE) < host.calls.index(SET_HIGH), True)
        self.assertTrue(powermode.owned_by(self.marker, custody_root=self.custody))
        [start] = (root / 'staging').glob('v4-session-start-restore-*.json')
        self.assertEqual(json.loads(start.read_text())['action'], 'restored')
        # Re-install of the installed session: its own marker is kept, no pmset change.
        state = json.loads((root / 'session.json').read_text())
        state['install'] = {'exit_code': 0}
        (root / 'session.json').write_text(json.dumps(state))
        calls = len(host.calls)
        self.install(root, host)
        self.assertNotIn(RESTORE, host.calls[calls:])
        self.assertNotIn(SET_HIGH, host.calls[calls:])
        self.assertEqual(host.mode, 2)

    def test_install_never_runs_under_a_measuring_night(self):
        _measurement, root = self.make_session()
        self.w1_marker(self.tmp / 'measuring/custody')
        self.hold_lock_elsewhere()
        host = FakeArmHost(mode=2)
        with self.assertRaisesRegex(ValueError, 'holds the host night lock'):
            self.install(root, host)
        self.assertEqual(host.calls, [])
        self.assertFalse(self.installer_called)

    def test_install_holds_the_lock_until_it_returns(self):
        _measurement, root = self.make_session()
        seen = []

        def installer(*_args, **_kwargs):
            probe = powermode.HostLock(role='late launchd fire')
            seen.append(probe.acquire())
            probe.release()
            return {'exit_code': 0}
        host = FakeArmHost(mode=0, marker=self.marker)
        from tests.align.test_v4_kit import topup
        with patch.object(kit, 'require_w1_ready'), patch.object(kit, 'generate'), \
                patch.object(pilot, 'install', side_effect=installer):
            session.install(root, runner=host, volume_runner=host, obc_off_attested_by='synthetic', **topup(),
                            w1_disk_config=W1DiskGateTests.config(self, self.tmp),
                            disk_gate=lambda c: {'status': 'pass', 'offloads': []})
        self.assertEqual(seen, [False])
        free = powermode.HostLock()
        self.assertTrue(free.acquire())
        free.release()

    def test_prepare_restores_an_owed_marker_first(self):
        measurement, _root = self.make_session()
        powermode.write_host_marker(self.marker, tag=powermode.R1_MARKER_TEXT)
        host = FakeArmHost(mode=2)
        order = []
        with patch.object(kit, 'generate', side_effect=lambda *a, **k: order.append(('generate', host.mode))), \
                patch.object(session, 'series_ac_powermode', return_value=0), \
                patch.object(pilot, 'prepare', side_effect=lambda *a, **k: order.append(('prepare', host.mode))):
            session.prepare(measurement, self.tmp / 'new-session', power_runner=host)
        self.assertEqual(order, [('generate', 0), ('prepare', 0)])
        self.assertFalse(self.marker.exists())

    def test_prepare_refuses_when_the_owed_restore_fails(self):
        measurement, _root = self.make_session()
        powermode.write_host_marker(self.marker, tag=powermode.R1_MARKER_TEXT)

        def denied(argv):
            if tuple(argv) == RESTORE:
                return subprocess.CompletedProcess(argv, 1, '', 'sudo: a password is required')
            return FakeArmHost(mode=2)(argv)
        with patch.object(kit, 'generate') as generate, self.assertRaisesRegex(ValueError, 'session start refused'):
            session.prepare(measurement, self.tmp / 'new-session', power_runner=denied)
        generate.assert_not_called()
        self.assertTrue(self.marker.exists())


class R1DriverHostLevelTests(HostStateCase):
    def args(self, **changes):
        return rehearsal_tests.R1Tests().args(self.tmp, include_4bit=False, **changes)

    def run_driver(self, world=None):
        world = world or rehearsal_tests.FakeWorld()
        args = self.args()
        with patch.object(r1, '_run', world), patch.object(r1, '_now_local', lambda: rehearsal_tests.NOON_SAFE):
            code = r1.run(args)
        return code, args, json.loads((args.output / 'r1_result.json').read_text())

    def test_the_guard_writes_and_clears_the_host_level_marker(self):
        guard = r1.PowerModeGuard(FakeArmHost(mode=0), self.tmp / 'legacy', self.marker)
        guard.high()
        self.assertTrue(self.marker.exists())
        self.assertFalse(powermode.w1_marker(self.marker))       # an R1 marker, never a W1 one
        # A SIGKILL here runs no restore: the next admission anywhere sees it.
        host = FakeArmHost(mode=2)
        admitted = powermode.admit_ac_powermode(0, markers=[self.marker], runner=host)
        self.assertTrue(admitted['admitted'])
        self.assertFalse(self.marker.exists())
        guard.high()
        self.assertTrue(guard.restore())
        self.assertFalse(self.marker.exists())

    def test_r1_measures_holding_the_night_lock(self):
        world = rehearsal_tests.FakeWorld()
        seen = []

        def probing(argv, **kwargs):
            if '--r1-kind' in argv and argv[argv.index('--r1-kind') + 1] == 'step-d':
                probe = powermode.HostLock(role='session start')
                seen.append(probe.acquire())
                probe.release()
            return world(argv, **kwargs)
        code, _args, result = self.run_driver(probing)
        self.assertEqual((code, result['status']), (0, 'complete'))
        self.assertEqual(seen, [False])
        free = powermode.HostLock()
        self.assertTrue(free.acquire())
        free.release()

    def test_r1_keeps_the_host_level_marker_through_its_high_power_leg(self):
        world = rehearsal_tests.FakeWorld()
        seen = []

        def probing(argv, **kwargs):
            if '--r1-kind' in argv and argv[argv.index('--r1-kind') + 1] == 'high-power-aba-b':
                seen.append((world.mode, self.marker.exists()))
            return world(argv, **kwargs)
        code, _args, _result = self.run_driver(probing)
        self.assertEqual(code, 0)
        self.assertEqual(seen, [(2, True)])
        self.assertFalse(self.marker.exists())          # cleared by the verified restore

    def test_r1_never_restores_under_another_nights_high_power(self):
        # Round-6 Sol critique: the refused run's teardown restored Automatic
        # (and dropped the other night's marker) without holding the lock.
        self.hold_lock_elsewhere()
        powermode.write_host_marker(self.marker, tag=powermode.W1_MARKER_TAG,
                                    owner={'custody_root': self.tmp / 'measuring/custody'})
        world = rehearsal_tests.FakeWorld()
        world.mode = 2
        code, args, result = self.run_driver(world)
        self.assertEqual((code, world.mode), (3, 2))
        self.assertTrue(self.marker.exists())
        self.assertNotIn('restore_automatic', [r['point'] for r in result['powermode']])
        # A rerun into the existing output (refused before the lock) neither.
        with patch.object(r1, '_run', world), patch.object(r1, '_now_local', lambda: rehearsal_tests.NOON_SAFE):
            self.assertEqual(r1.run(args), 3)
        self.assertEqual(world.mode, 2)

    def test_r1_refuses_before_any_work_while_another_night_holds_the_lock(self):
        self.hold_lock_elsewhere()
        world = rehearsal_tests.FakeWorld()
        code, args, result = self.run_driver(world)
        self.assertEqual(code, 3)
        self.assertIn('host_lock_held', result['error'])
        self.assertFalse(args.registration.exists())
        self.assertEqual(world.invocations, [])


class R1RegistrationAuthorityTests(HostStateCase):
    """Round-5 executing review LOW-6: r1_result.status is the authority for
    committing r1_slots; the registration exists only beside a complete
    terminal record."""

    def run_driver(self, write_result=None):
        args = rehearsal_tests.R1Tests().args(self.tmp, include_4bit=False)
        with patch.object(r1, '_run', rehearsal_tests.FakeWorld()), \
                patch.object(r1, '_now_local', lambda: rehearsal_tests.NOON_SAFE), \
                patch.object(r1, '_write_result', write_result or r1._write_result):
            try:
                code = r1.run(args)
            except OSError:
                code = None
        return code, args

    def test_the_registration_is_written_after_a_complete_terminal_record(self):
        seen = []
        original = r1._write_result

        def write_result(output, record, created):
            seen.append(((self.tmp / 'registration/r1_slots.json').exists(), record['status']))
            return original(output, record, created)
        code, args = self.run_driver(write_result)
        self.assertEqual(code, 0)
        self.assertEqual(seen, [(False, 'complete')])
        result = json.loads((args.output / 'r1_result.json').read_text())
        raw = args.registration.read_bytes()
        import hashlib
        self.assertEqual(result['registration_sha256'], hashlib.sha256(raw).hexdigest())

    def test_no_registration_without_a_terminal_record(self):
        def failing(output, record, created):
            raise OSError('disk full')
        code, args = self.run_driver(failing)
        self.assertIsNone(code)
        self.assertFalse(args.registration.exists())

    def test_a_signal_after_the_slots_are_built_leaves_no_registration(self):
        # A first signal between building r1_slots and the return records
        # status aborted; no r1_slots may then exist for the magistrate.
        original = r1.hashlib.sha256
        state = {'fired': False}

        def interrupting(*args, **kwargs):
            value = original(*args, **kwargs)
            if not state['fired'] and args and isinstance(args[0], bytes) and r1.SCHEMA.encode() in args[0]:
                state['fired'] = True          # the registration bytes: the slots are complete
                raise KeyboardInterrupt('signal 15')
            return value
        with patch.object(r1.hashlib, 'sha256', interrupting):
            code, args = self.run_driver()
        self.assertTrue(state['fired'])
        self.assertEqual(code, 4)
        self.assertEqual(json.loads((args.output / 'r1_result.json').read_text())['status'], 'aborted')
        self.assertFalse(args.registration.exists())


class R1NightWorstCaseTests(unittest.TestCase):
    """Round-5 cold pass LOW-6: the all-caps R1 night wall, from the phase table."""

    def test_worst_case_sums_every_phase_cap(self):
        value = r1.night_worst_case_s(['fake-runtime'])
        names = [row['name'] for row in value['segments']]
        self.assertEqual(names, [row[0] for row in r1.phase_plan(False)])
        bounds = {row['name']: row['bound_s'] for row in value['segments']}
        self.assertEqual(bounds['idle_soak'], 1800)
        # R7-2 and R8-4: 1,750 + 1.13544 x 1,580 + 120 (the re-armed member) + 1,200 + 300 + 600
        self.assertAlmostEqual(bounds['step_D_prefill_10k_decode_4096'], 5763.9952)
        self.assertAlmostEqual(bounds['high_power_B'], r1.aba_leg_bound_s(['fake-runtime']))
        self.assertAlmostEqual(value['no_redo_s'], sum(bounds.values()))
        self.assertEqual(value['batch_blackout_s'], 5400)
        self.assertAlmostEqual(value['batch_encounter_max_s'], max(bounds.values()) + 5400)

    def test_worst_case_uses_the_round6_table_and_counts_the_r6_2_retries(self):
        # Round-6 integration: the R6-1/R6-2/R6-6 phase table with the runtime
        # config's precool cap, and one R6-2 retry per calibration segment.
        value = r1.night_worst_case_s(['fake-runtime'])
        cap = r1.runtime_precool_cap_s(['fake-runtime'])
        self.assertEqual(value['precool_cap_s'], cap)
        names = [row['name'] for row in value['segments']]
        self.assertEqual(names, [row[0] for row in r1.phase_plan(False, precool_cap_s=cap)])
        self.assertNotIn('cooldown_after_30b', names)
        bounds = {row['name']: row['bound_s'] for row in value['segments']}
        self.assertEqual(bounds[r1.STEP_D_NAME + r1.PRECOOL_SUFFIX], cap)
        calibration = [row for row in value['segments'] if row['kind'] in r1.contract.G0_INCONCLUSIVE_KINDS]
        self.assertEqual(len(calibration), 4)
        self.assertAlmostEqual(value['r6_2_retry_max_s'], sum(cap + row['bound_s'] for row in calibration))
        self.assertAlmostEqual(value['with_retries_and_one_batch_encounter_s'],
                               value['no_redo_s'] + value['r6_2_retry_max_s'] + value['batch_encounter_max_s'])


if __name__ == '__main__':
    unittest.main()
