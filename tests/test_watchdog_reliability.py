"""W-01/W-02 witnesses: synthetic installed plans, clocks and process tables."""
import datetime as dt
import json
from pathlib import Path
from unittest import mock

from scripts import magistrate_watchdog as wd
from tests import test_magistrate_watchdog as fixtures
from tests import test_magistrate_watchdog_v5 as installed


class UnsafeHoldTests(fixtures.WatchdogTestCase):
    write_plan = installed.InstalledV5Tests.write_plan

    def advance(self, seconds):
        self.harness.clock.wall += dt.timedelta(seconds=seconds)
        self.harness.clock.mono += seconds

    def test_unknown_installed_key_notices_immediately_then_strands_without_launch(self):
        path, value = self.write_plan(unknown_future_key=1)
        night = Path(value['custody_root']) / 'night'
        (night / 'chain.started').write_text('{"pgid":4242}')
        with mock.patch.object(wd.os, 'fork') as fork:
            first = wd.tick(self.harness.storage, self.harness.deps, dry_run=True)
            self.assertEqual('HOLD_PLAN_MALFORMED', first.state)
            self.assertFalse(first.launch)
            state = wd.load_state(self.harness.storage)
            self.assertEqual('hold_plan_malformed', state['notice_pending'][0]['kind'])
            self.assertEqual(1, len(state['notice_pending']))
            self.advance(wd.UNSAFE_HOLD_DWELL_S - 1)
            self.assertEqual('HOLD_PLAN_MALFORMED', wd.tick(
                self.harness.storage, self.harness.deps, dry_run=True).state)
            self.advance(1)
            terminal = wd.tick(self.harness.storage, self.harness.deps, dry_run=True)
            self.assertEqual('STRANDED', terminal.state)
            self.assertFalse(terminal.launch)
            self.advance(2 * 24 * 60 * 60)
            later = wd.tick(self.harness.storage, self.harness.deps, dry_run=True)
            self.assertEqual('STRANDED', later.state)
            self.assertFalse(later.launch)
            fork.assert_not_called()
        state = wd.load_state(self.harness.storage)
        self.assertEqual(['hold_plan_malformed', 'stranded'], [n['kind'] for n in state['notice_pending']])
        self.assertEqual([], self.harness.spawn_calls)
        # Repairing the schema cannot bypass the still-open chain fence.
        value.pop('unknown_future_key')
        path.write_text(json.dumps(value))
        self.assertFalse(wd.decide(self.harness.storage, self.harness.deps, state).launch)

    def test_unreadable_installed_plan_and_plist_have_distinct_notices(self):
        path, _ = self.write_plan()
        path.write_text('{truncated')
        state = wd.initial_state()
        decision = wd.decide(self.harness.storage, self.harness.deps, state)
        self.assertEqual('HOLD_PLAN_UNREADABLE', decision.state)
        self.assertEqual('hold_plan_unreadable', state['notice_pending'][0]['kind'])
        directory = wd.Path.home() / 'Library/LaunchAgents'
        for plist in directory.iterdir():
            plist.write_text('broken plist')
        state = wd.initial_state()
        decision = wd.decide(self.harness.storage, self.harness.deps, state)
        self.assertEqual('HOLD_PLIST_UNREADABLE', decision.state)
        self.assertEqual('hold_plist_unreadable', state['notice_pending'][0]['kind'])

    def test_changed_bad_key_cannot_restart_dwell_and_ack_does_not_requeue_same_notice(self):
        path, value = self.write_plan(unknown_one=1)
        state = wd.initial_state()
        wd.decide(self.harness.storage, self.harness.deps, state)
        state['notice_pending'] = []  # existing notice.ack consumer's effect
        wd.decide(self.harness.storage, self.harness.deps, state)
        self.assertEqual([], state['notice_pending'])
        self.advance(wd.UNSAFE_HOLD_DWELL_S)
        value.pop('unknown_one')
        value['unknown_two'] = 2
        path.write_text(json.dumps(value))
        self.assertEqual('STRANDED', wd.decide(self.harness.storage, self.harness.deps, state).state)
        self.assertEqual(2, len(state['notice_pending']))

    def test_lock_conflict_process_and_desk_reasons_remain_separate_fail_closed_states(self):
        cases = {
            'plan_conflict: overlapping': 'HOLD_CONFLICT',
            'process table unavailable: denied': 'HOLD_PROCESS_TABLE',
            'corrupt_lock_owned_candidates: pids=1': 'HOLD_LOCK',
            'magistrate.lock could not be cleared': 'HOLD_LOCK',
            'desk_fence: malformed': 'HOLD_DESK_FENCE',
        }
        for reason, expected in cases.items():
            with self.subTest(reason=reason):
                state = wd.initial_state()
                with mock.patch.object(wd, '_decide', return_value=wd.Decision('HOLD_UNSAFE', reason)):
                    decision = wd.decide(self.harness.storage, self.harness.deps, state)
                self.assertEqual(expected, decision.state)
                self.assertFalse(decision.launch)
                self.assertEqual(1, len(state['notice_pending']))


class HeartbeatTests(fixtures.WatchdogTestCase):
    def setUp(self):
        super().setUp()
        self.lock = self.write_live_lock()
        self.harness.processes.rows = [wd.ProcessInfo(100, 99, 'token-a', 'session')]

    def advance(self, seconds):
        self.harness.clock.wall += dt.timedelta(seconds=seconds)
        self.harness.clock.mono += seconds

    def heartbeat(self, text=None):
        path = self.harness.storage.root / 'heartbeat'
        path.write_text(text if text is not None else
                        f"100 activation-a {self.harness.clock.wall.timestamp()}\n")

    def test_tick_reads_heartbeat_and_notices_stale_live_pid_once(self):
        self.heartbeat()
        first = wd.tick(self.harness.storage, self.harness.deps, dry_run=True)
        self.assertEqual('ACTIVE', first.state)
        self.assertFalse(wd.load_state(self.harness.storage)['magistrate_heartbeat']['stale'])
        self.advance(wd.HEARTBEAT_STALE_S)
        decision = wd.tick(self.harness.storage, self.harness.deps, dry_run=True)
        self.assertEqual('ACTIVE', decision.state)
        state = wd.load_state(self.harness.storage)
        self.assertTrue(state['magistrate_heartbeat']['stale'])
        self.assertEqual(['magistrate_heartbeat_stale'], [n['kind'] for n in state['notice_pending']])
        state['notice_pending'] = []  # acknowledge the already surfaced episode
        self.harness.storage.atomic_json(self.harness.storage.root / 'state.json', state)
        wd.tick(self.harness.storage, self.harness.deps, dry_run=True)
        self.assertEqual([], wd.load_state(self.harness.storage)['notice_pending'])
        self.assertEqual([], self.harness.processes.signals)
        self.assertEqual([], self.harness.spawn_calls)

    def test_missing_identity_mismatch_malformed_and_future_stamps_cannot_keep_session_live(self):
        self.advance(wd.HEARTBEAT_STALE_S + 1)
        epoch = self.harness.clock.wall.timestamp()
        cases = (None, 'garbage', f'200 activation-a {epoch}', f'100 old-activation {epoch}',
                 '100 activation-a nan', f'100 activation-a {epoch + 60}',
                 f'100 activation-a {self.base.timestamp() - 1}', 'x' * 4097)
        for text in cases:
            with self.subTest(text=text):
                (self.harness.storage.root / 'heartbeat').unlink(missing_ok=True)
                if text is not None:
                    self.heartbeat(text)
                state = wd.initial_state()
                decision = wd.decide(self.harness.storage, self.harness.deps, state)
                self.assertEqual('ACTIVE', decision.state)
                self.assertTrue(state['magistrate_heartbeat']['stale'])
                self.assertEqual('magistrate_heartbeat_stale', state['notice_pending'][0]['kind'])

    def test_start_grace_recovery_and_second_outage(self):
        state = wd.initial_state()
        wd.decide(self.harness.storage, self.harness.deps, state)
        self.assertEqual([], state['notice_pending'])
        self.advance(wd.HEARTBEAT_STALE_S)
        wd.decide(self.harness.storage, self.harness.deps, state)
        self.assertEqual(1, len(state['notice_pending']))
        self.heartbeat()
        wd.decide(self.harness.storage, self.harness.deps, state)
        self.assertFalse(state['magistrate_heartbeat']['stale'])
        self.advance(wd.HEARTBEAT_STALE_S)
        wd.decide(self.harness.storage, self.harness.deps, state)
        self.assertEqual(2, len(state['notice_pending']))
        self.assertEqual(2, len({n['id'] for n in state['notice_pending']}))

    def test_unreadable_heartbeat_is_a_notice_rather_than_an_exception(self):
        self.advance(wd.HEARTBEAT_STALE_S)
        state = wd.initial_state()
        with mock.patch.object(self.harness.storage, 'read_bytes_bounded', side_effect=PermissionError()):
            wd._observe_magistrate_heartbeat(self.harness.storage, state, self.harness.clock.wall, self.lock)
        self.assertEqual('unreadable', state['magistrate_heartbeat']['status'])
        self.assertEqual('magistrate_heartbeat_stale', state['notice_pending'][0]['kind'])

    def test_resident_supervisor_also_reads_heartbeat_without_changing_standdown(self):
        plan = self.make_plan()
        supervisor = self.supervisor(plan)
        supervisor._cached_remote_stop = lambda _mono: self.harness.stop
        self.advance(wd.HEARTBEAT_STALE_S + 1)
        self.assertTrue(supervisor.step())
        self.assertTrue(supervisor.state['magistrate_heartbeat']['stale'])
        self.assertEqual('magistrate_heartbeat_stale', supervisor.state['notice_pending'][0]['kind'])
        self.assertEqual('ACTIVE', supervisor.state['state'])
        self.assertEqual([], self.harness.processes.signals)
