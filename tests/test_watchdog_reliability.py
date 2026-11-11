"""W-01/W-02 witnesses: synthetic installed plans, clocks and process tables."""
import datetime as dt
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path
from unittest import mock

from scripts import magistrate_watchdog as wd
from scripts import watchdog_status as status
from tests.git_fixture import init_git_fixture
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
            'desk_fence: clock blocked by magistrate.lock': 'HOLD_DESK_FENCE',
            'launch_fence: clock blocked': 'HOLD_UNSAFE',
            'unexpected clock failure': 'HOLD_UNSAFE',
            'unclassified: night_plan_malformed in detail': 'HOLD_UNSAFE',
            'dead_lock_resumed_twin: pids=1': 'HOLD_LOCK',
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

    def stream(self, data=b'{}\n'):
        path = self.harness.storage.root / 'attempts/activation-a/attempt-1.stream.jsonl'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        os.utime(path, (self.harness.clock.wall.timestamp(),) * 2)
        return path

    def test_supervisor_stream_growth_keeps_long_tool_call_live_without_model_heartbeat(self):
        state = wd.initial_state()
        state['attempt'] = 1
        stream = self.stream()
        wd._observe_magistrate_heartbeat(self.harness.storage, state, self.harness.clock.wall, self.lock)
        self.advance(wd.HEARTBEAT_STALE_S - 1)
        with stream.open('ab') as handle:
            handle.write(b'{"type":"tool_result"}\n')
        wd._observe_magistrate_heartbeat(self.harness.storage, state, self.harness.clock.wall, self.lock)
        self.advance(2)
        wd._observe_magistrate_heartbeat(self.harness.storage, state, self.harness.clock.wall, self.lock)
        self.assertFalse(state['magistrate_heartbeat']['stale'])
        self.assertEqual(2, state['magistrate_heartbeat']['age_s'])
        self.assertEqual([], state['notice_pending'])

    def test_unchanged_replaced_truncated_and_old_attempt_streams_cannot_fake_progress(self):
        for change in ('unchanged', 'replace', 'truncate', 'other_attempt'):
            with self.subTest(change=change):
                state = wd.initial_state()
                state['attempt'] = 1
                stream = self.stream(b'a' * 100)
                wd._observe_magistrate_heartbeat(self.harness.storage, state, self.harness.clock.wall, self.lock)
                self.advance(wd.HEARTBEAT_STALE_S + 1)
                if change == 'replace':
                    replacement = stream.with_suffix('.new')
                    replacement.write_bytes(b'x' * 200)
                    replacement.replace(stream)
                elif change == 'truncate':
                    stream.write_bytes(b'x')
                elif change == 'other_attempt':
                    stream.with_name('attempt-2.stream.jsonl').write_bytes(b'x' * 200)
                wd._observe_magistrate_heartbeat(self.harness.storage, state, self.harness.clock.wall, self.lock)
                self.assertTrue(state['magistrate_heartbeat']['stale'])
                self.assertEqual('magistrate_heartbeat_stale', state['notice_pending'][0]['kind'])

    def test_first_observation_of_old_output_does_not_refresh_liveness(self):
        self.stream()
        self.advance(wd.HEARTBEAT_STALE_S + 1)
        state = wd.initial_state()
        state['attempt'] = 1
        wd._observe_magistrate_heartbeat(self.harness.storage, state, self.harness.clock.wall, self.lock)
        self.assertTrue(state['magistrate_heartbeat']['stale'])


class ModelStartupTests(fixtures.WatchdogTestCase):
    def test_late_model_capacity_error_uses_backoff_without_latching(self):
        supervisor = self.supervisor(self.make_plan())
        self.harness.clock.wall += dt.timedelta(seconds=wd.MODEL_STARTUP_WINDOW_S + 1)
        self.harness.clock.mono += wd.MODEL_STARTUP_WINDOW_S + 1
        supervisor.stderr_path.write_text('API Error: model not available')
        self.harness.child.exit_code = 1
        self.assertFalse(supervisor.step())
        self.assertEqual('BACKOFF', supervisor.state['state'])
        self.assertFalse(supervisor.state.get('model_startup_hold'))

    def test_early_error_after_assistant_output_beyond_tail_uses_backoff(self):
        supervisor = self.supervisor(self.make_plan())
        supervisor.stdout_path.write_text(json.dumps({'type': 'assistant', 'message': 'working'})
            + '\n' + (json.dumps({'type': 'tool', 'message': 'x' * 1000}) + '\n') * 10)
        supervisor.stderr_path.write_text('Error: model not available')
        self.harness.child.exit_code = 1
        self.assertFalse(supervisor.step())
        self.assertEqual('BACKOFF', supervisor.state['state'])
        self.assertFalse(supervisor.state.get('model_startup_hold'))

    def binary(self):
        target = self.temp / 'cli'
        target.write_text('#!/bin/sh\nexit 0\n')
        target.chmod(0o755)
        link = self.temp / 'session'
        link.symlink_to(target)
        return link

    def test_model_rejection_is_named_noticed_and_latched_across_future_ticks(self):
        supervisor = self.supervisor(self.make_plan())
        state = supervisor.state
        supervisor.stderr_path.write_text('Unknown model: claude-fable-5-2')
        self.harness.child.exit_code = 1
        self.assertFalse(supervisor.step())
        self.assertEqual('HOLD_MODEL_REJECTED', state['state'])
        self.assertEqual('hold_model_rejected', state['notice_pending'][0]['kind'])
        self.assertFalse((self.harness.storage.root / 'magistrate.lock').exists())
        for seconds in (300, 86400):
            self.harness.clock.wall += dt.timedelta(seconds=seconds)
            self.harness.clock.mono += seconds
            decision = wd.decide(self.harness.storage, self.harness.deps, wd.load_state(self.harness.storage))
            self.assertFalse(decision.launch)
        self.assertEqual([], self.harness.spawn_calls)

    def test_ruled_model_is_retained_without_an_unsupervised_probe(self):
        argv = wd.session_argv(self.temp / 'cli', 'prompt', 'activation')
        self.assertEqual('claude-fable-5-2', argv[argv.index('--model') + 1])
        with mock.patch.object(wd.subprocess, 'run') as run:
            wd.model_startup_check('', '')
        run.assert_not_called()

    def test_structured_rejection_is_detected_even_if_cli_returns_zero(self):
        supervisor = self.supervisor(self.make_plan())
        self.harness.storage.atomic_json(self.harness.storage.root / 'standdown.request', {'reason': 'synthetic'})
        supervisor.stdout_path.write_text(json.dumps({'type': 'result', 'is_error': True,
            'errors': ['The selected model does not exist or you do not have access']}))
        self.harness.child.exit_code = 0
        self.assertFalse(supervisor.step())
        self.assertEqual('HOLD_MODEL_REJECTED', supervisor.state['state'])
        self.assertFalse((self.harness.storage.root / 'standdown.request').exists())
        self.assertEqual('COMPLETE', supervisor.state['standdown_phase'])

    def test_successful_transcript_discussing_unknown_models_does_not_latch(self):
        output = json.dumps({'type': 'assistant', 'message': 'Unknown model: claude-fable-5-2'})
        output += '\n' + json.dumps({'type': 'result', 'is_error': False, 'result': 'model not found in tests'})
        wd.model_startup_check(output, 'tool output: unknown model in a test fixture')

    def test_fast_rejection_before_pid_observation_also_latches(self):
        def spawn(argv, cwd, stdout, stderr):
            stderr.write_text('Error: Invalid model claude-fable-5-2')
            self.harness.child.exit_code = 1
            return self.harness.child
        self.harness.deps.spawn = spawn
        state = wd.initial_state()
        self.assertIsNone(wd.start_session_guarded(self.harness.storage, self.harness.deps, state, binary_path=self.binary()))
        self.assertEqual('HOLD_MODEL_REJECTED', state['state'])
        self.assertFalse((self.harness.storage.root / 'magistrate.lock').exists())

    def test_plan_appearing_during_version_work_prevents_spawn(self):
        def version(_):
            self.make_plan(t0=self.base.timestamp())
            return 'synthetic'
        self.harness.deps.version_probe = version
        state = wd.initial_state()
        self.assertIsNone(wd.start_session_guarded(
            self.harness.storage, self.harness.deps, state, binary_path=self.binary()))
        self.assertEqual('FENCED', state['state'])
        self.assertEqual([], self.harness.spawn_calls)


class StatusExportTests(fixtures.WatchdogTestCase):
    def test_pre_span_push_announces_end_then_25_armed_ticks_do_no_transport(self):
        plan = self.make_plan(t0=self.base.timestamp() + 550, window_max_s=3 * 3600)
        state = wd.initial_state()
        wd._configure_status_export(self.harness.storage, self.harness.deps, state)
        self.checkpoint('IDLE', state)
        self.exporter.flush()
        record = self.snapshot()
        end = wd.plan_completion_epoch(plan)
        self.assertEqual(end, record['span_end_epoch_s'])
        self.assertEqual(end + status.AIR_STALE_S, record['next_status_expected_epoch_s'])
        self.assertNotIn('watchdog_status_stale', status.alarm_reasons(record, self.exporter.host, end + 1))
        self.assertIn('watchdog_status_stale', status.alarm_reasons(record, self.exporter.host, end + status.AIR_STALE_S))
        self.advance(371)  # inside the span's 180-second lead
        night = Path(plan.custody_root) / 'night'
        night.mkdir(exist_ok=True)
        (night / 'chain.started').write_text('{"pgid":123}')
        first = self.git('--git-dir=' + str(self.origin), 'rev-parse', self.exporter.ref)
        with mock.patch.object(status.GitTransport, 'publish') as publish:
            for _ in range(25):
                self.assertEqual('FENCED', wd.tick(self.harness.storage, self.harness.deps).state)
                self.advance(300)
            self.exporter.flush_background()
            self.exporter.finish()
            publish.assert_not_called()
        self.assertEqual(first, self.git('--git-dir=' + str(self.origin), 'rev-parse', self.exporter.ref))
        (night / 'chain.exited').write_text('{}')
        (night / 'courier.sent').write_text('sent')
        self.advance(end - self.harness.clock.wall.timestamp() + 1)
        self.exporter.flush()
        self.assertNotEqual(first, self.git('--git-dir=' + str(self.origin), 'rev-parse', self.exporter.ref))

    def test_imminent_span_and_unknown_span_defer_transport(self):
        self.checkpoint()
        self.make_plan(t0=self.base.timestamp() + wd.PLAN_LEAD_S + 10)
        wd._configure_status_export(self.harness.storage, self.harness.deps, wd.initial_state())
        with mock.patch.object(status.GitTransport, 'publish') as publish:
            self.exporter.flush()
            publish.assert_not_called()
        with mock.patch.object(wd, '_remote_probe_allowed', side_effect=ValueError('unknown span')):
            self.assertFalse(self.exporter.probe_allowed())

    def test_each_git_operation_rechecks_span_gate_before_starting_process(self):
        transport = status.GitTransport(self.clone)
        transport.probe_allowed = lambda: False
        with mock.patch.object(status.subprocess, 'Popen') as popen, self.assertRaisesRegex(RuntimeError, 'deferred'):
            transport.run(['version'])
        popen.assert_not_called()

    def test_missing_failed_old_exports_all_allow_real_spawn_with_prompt_notice(self):
        binary = ModelStartupTests.binary(self)
        self.harness.storage.mkdir(self.harness.storage.root)
        for kind in ('missing', 'failed', 'old', 'unconfigured'):
            with self.subTest(kind=kind):
                self.harness.storage.status_exporter = self.exporter
                self.harness.storage.unlink(self.harness.storage.root / 'magistrate.lock')
                self.harness.storage.unlink(self.harness.storage.root / 'status-attempt.json')
                self.harness.storage.unlink(self.harness.storage.root / 'status-delivery.json')
                if kind == 'failed':
                    self.harness.storage.atomic_json(self.harness.storage.root / 'status-attempt.json', {'error': 'failed'})
                if kind == 'old':
                    self.harness.storage.atomic_json(self.harness.storage.root / 'status-delivery.json', {
                        'ref': self.exporter.ref, 'delivered_epoch_s': self.base.timestamp() - status.KEEPALIVE_S})
                if kind == 'unconfigured':
                    self.harness.storage.status_exporter = None
                    self.harness.storage.status_export_error = 'status_export: host missing'
                self.harness.processes.rows = [wd.ProcessInfo(100, 99, 'token-a', 'session')]
                state = wd.initial_state()
                supervisor = wd.start_session_guarded(self.harness.storage, self.harness.deps, state, binary_path=binary)
                self.assertIsNotNone(supervisor)
                prompt = self.harness.spawn_calls[-1][2].parent / 'prompt.md'
                self.assertIn('status_export_failed', prompt.read_text())
        self.assertEqual(len(self.harness.spawn_calls), 4)

    def test_configured_host_is_stable_and_missing_host_never_falls_back_to_hostname(self):
        with mock.patch.dict(os.environ, {'MAGISTRATE_WATCHDOG_STATUS_HOST': 'fixed-mbp'}):
            self.assertEqual('refs/heads/watchdog-status/fixed-mbp',
                             status.StatusExporter(self.harness.storage, self.clone).ref)
        with mock.patch.dict(os.environ, {}, clear=True), self.assertRaises(ValueError):
            status.StatusExporter(self.harness.storage, self.clone)

    def test_air_rejects_inconsistent_expectation_and_preserves_hold_alarm_in_span(self):
        self.checkpoint('HOLD_LOCK')
        self.exporter.flush()
        record = self.snapshot()
        now = self.base.timestamp()
        record.update(span_end_epoch_s=now + 10000, next_status_expected_epoch_s=now + 10000 + status.AIR_STALE_S)
        self.assertEqual(['HOLD_LOCK'], status.alarm_reasons(record, self.exporter.host, now + status.AIR_STALE_S))
        record['next_status_expected_epoch_s'] += 1
        self.assertEqual(['watchdog_status_invalid'], status.alarm_reasons(record, self.exporter.host, now))

    def setUp(self):
        super().setUp()
        self.origin = self.temp / 'origin.git'
        self.origin.mkdir()
        init_git_fixture(self.origin, '--bare')
        self.clone = self.temp / 'code'
        self.clone.mkdir()
        init_git_fixture(self.clone)
        self.git('-C', str(self.clone), 'remote', 'add', 'origin', str(self.origin))
        self.exporter = status.StatusExporter(self.harness.storage, self.clone, host='synthetic-mbp',
                                              wall=lambda: self.harness.clock.wall.timestamp())
        self.harness.storage.status_exporter = self.exporter

    def git(self, *args):
        return subprocess.run(['/usr/bin/git', *args], capture_output=True, text=True, check=True).stdout.strip()

    def advance(self, seconds):
        self.harness.clock.wall += dt.timedelta(seconds=seconds)
        self.harness.clock.mono += seconds

    def snapshot(self):
        return json.loads(self.git('--git-dir=' + str(self.origin), 'show', self.exporter.ref + ':status.json'))

    def checkpoint(self, word='FENCED', state=None):
        state = state or wd.initial_state()
        wd.transition(self.harness.storage, state, word, 'synthetic private detail', self.harness.clock.wall)
        self.harness.storage.atomic_json(self.harness.storage.root / 'state.json', state)
        return state

    def test_real_local_bare_push_exports_status_only_and_preserves_transition_history(self):
        state = self.checkpoint('HOLD_PLAN_MALFORMED')
        state.update(activation_id='last-activation', unsafe_hold={'category': 'HOLD_PLAN_MALFORMED',
                     'since_epoch_s': self.harness.clock.wall.timestamp() - 120},
                     magistrate_heartbeat={'age_s': 42, 'stale': True, 'observed_epoch_s': self.harness.clock.wall.timestamp()})
        self.harness.storage.atomic_json(self.harness.storage.root / 'state.json', state)
        self.exporter.flush()
        record = self.snapshot()
        self.assertEqual('HOLD_PLAN_MALFORMED', record['hold_reason'])
        self.assertEqual(120, record['dwell_s'])
        self.assertEqual(42, record['last_heartbeat_age_s'])
        self.assertEqual('last-activation', record['last_activation_id'])
        self.assertNotIn('private detail', json.dumps(record))
        self.assertEqual(['status.json', 'transitions.jsonl'], self.git('--git-dir=' + str(self.origin), 'ls-tree', '--name-only', self.exporter.ref).splitlines())
        self.assertIsNone(self.exporter.launch_hold())
        first = self.git('--git-dir=' + str(self.origin), 'rev-parse', self.exporter.ref)
        self.advance(60)
        self.checkpoint('STRANDED', state)
        self.exporter.flush()
        self.assertEqual(first, self.git('--git-dir=' + str(self.origin), 'rev-parse', self.exporter.ref + '^'))
        self.assertEqual('STRANDED', self.snapshot()['state'])

    def test_rate_limit_retains_every_transition_then_hourly_keepalive(self):
        state = self.checkpoint()
        self.exporter.flush()
        first = self.git('--git-dir=' + str(self.origin), 'rev-parse', self.exporter.ref)
        self.advance(1)
        self.checkpoint('IDLE', state)
        self.checkpoint('STOPPED', state)
        self.exporter.flush()
        self.assertEqual(first, self.git('--git-dir=' + str(self.origin), 'rev-parse', self.exporter.ref))
        self.advance(59)
        self.exporter.flush()
        rows = self.git('--git-dir=' + str(self.origin), 'show', self.exporter.ref + ':transitions.jsonl').splitlines()
        self.assertEqual(['IDLE', 'STOPPED'], [json.loads(row)['state'] for row in rows])
        second = self.git('--git-dir=' + str(self.origin), 'rev-parse', self.exporter.ref)
        self.advance(status.KEEPALIVE_DUE_S - 1)
        self.checkpoint('STOPPED', state)
        self.exporter.flush()
        self.assertEqual(second, self.git('--git-dir=' + str(self.origin), 'rev-parse', self.exporter.ref))
        self.advance(1)
        self.checkpoint('STOPPED', state)
        self.exporter.flush()
        self.assertNotEqual(second, self.git('--git-dir=' + str(self.origin), 'rev-parse', self.exporter.ref))

    def test_failed_push_retains_outbox_and_notices_without_blocking_launch(self):
        self.checkpoint()
        hook = self.origin / 'hooks/pre-receive'
        hook.write_text('#!/bin/sh\nexit 1\n')
        hook.chmod(0o755)
        self.exporter.flush()
        self.assertIsNotNone(self.exporter.launch_hold())
        self.assertFalse((self.harness.storage.root / 'status-delivery.json').exists())
        self.assertTrue(list((self.harness.storage.root / 'status-outbox').glob('*.json')))
        state = wd.initial_state()
        decision = wd.decide(self.harness.storage, self.harness.deps, state)
        self.assertTrue(decision.launch)
        self.assertIn('status_export_failed', [n['kind'] for n in state['notice_pending']])
        hook.unlink()
        self.advance(status.MIN_PUSH_INTERVAL_S)
        # Reconstructing the exporter simulates launchd restarting it.
        self.exporter = status.StatusExporter(self.harness.storage, self.clone, host='synthetic-mbp',
                                              wall=lambda: self.harness.clock.wall.timestamp())
        self.exporter.flush()
        self.assertIsNone(self.exporter.launch_hold())
        self.assertEqual([], list((self.harness.storage.root / 'status-outbox').glob('*.json')))

    def test_missing_stale_or_corrupt_receipt_notices_without_weakening_plan_fence(self):
        self.checkpoint()
        for raw in ('[]', '{broken', '{"ref":"other","delivered_epoch_s":1}'):
            (self.harness.storage.root / 'status-delivery.json').write_text(raw)
            self.assertIsNotNone(self.exporter.launch_hold())
        self.make_plan(t0=self.base.timestamp())
        self.assertEqual('FENCED', wd.decide(self.harness.storage, self.harness.deps, wd.initial_state()).state)

    def test_in_flight_refresh_with_fresh_receipt_allows_admission_but_not_old_failure(self):
        self.checkpoint()
        self.exporter.flush()
        self.advance(60)
        self.harness.storage.atomic_json(self.harness.storage.root / 'status-attempt.json', {
            'attempt_epoch_s': self.harness.clock.wall.timestamp(), 'pending': True, 'error': None})
        self.assertIsNone(self.exporter.launch_hold())
        self.harness.storage.atomic_json(self.harness.storage.root / 'status-attempt.json', {
            'attempt_epoch_s': self.harness.clock.wall.timestamp(), 'pending': True, 'error': 'delivery failed'})
        self.assertIn('delivery failed', self.exporter.launch_hold())
        self.harness.storage.atomic_json(self.harness.storage.root / 'status-attempt.json', {
            'attempt_epoch_s': self.harness.clock.wall.timestamp(), 'pending': True, 'error': None})
        self.advance(status.TRANSPORT_BUDGET_S + 6)
        self.assertIn('worker did not finish', self.exporter.launch_hold())

    def test_backward_clock_step_never_bypasses_export_rate_limit(self):
        state = self.checkpoint()
        self.exporter.flush()
        self.advance(-120)
        self.checkpoint('STOPPED', state)
        with mock.patch.object(status.GitTransport, 'publish') as publish:
            for _ in range(5):
                self.exporter.flush()
                self.advance(10)
        publish.assert_not_called()

    def test_heartbeat_staleness_change_exports_without_waiting_for_hour_or_state_transition(self):
        state = self.checkpoint('ACTIVE')
        self.exporter.flush()
        self.advance(60)
        state['magistrate_heartbeat'] = {'stale': True, 'age_s': 901, 'observed_epoch_s': self.harness.clock.wall.timestamp()}
        self.harness.storage.atomic_json(self.harness.storage.root / 'state.json', state)
        self.exporter.flush()
        self.assertIn('magistrate_heartbeat_stale', status.alarm_reasons(self.snapshot(), self.exporter.host, self.harness.clock.wall.timestamp()))

    def test_background_push_does_not_block_resident_standdown(self):
        started, release = threading.Event(), threading.Event()
        def blocked(*args):
            started.set()
            release.wait(5)
            return 'a' * 40
        self.checkpoint()
        with mock.patch.object(status.GitTransport, 'publish', side_effect=blocked):
            self.exporter.flush_background()
            self.assertTrue(started.wait(1))
            plan = self.make_plan(t0=self.base.timestamp() + wd.KILL_LEAD_S)
            supervisor = self.supervisor(plan)
            self.harness.processes.rows = [wd.ProcessInfo(100, 99, 'token-a', 'session')]
            before = time.monotonic()
            supervisor.step()
            self.assertLess(time.monotonic() - before, 1)
            self.assertTrue(self.harness.processes.signals)
            release.set()
            self.exporter.finish()

    def test_launchd_environment_disables_prompts_and_transport_has_shared_deadline(self):
        with mock.patch.dict(os.environ, {'GIT_DIR': 'unsafe', 'GIT_INDEX_FILE': 'unsafe'}):
            transport = status.GitTransport(self.clone)
        self.assertEqual('0', transport.env['GIT_TERMINAL_PROMPT'])
        self.assertIn('BatchMode=yes', transport.env['GIT_SSH_COMMAND'])
        self.assertNotIn('GIT_DIR', transport.env)
        self.assertNotIn('GIT_INDEX_FILE', transport.env)
        transport.deadline = time.monotonic() - 1
        with self.assertRaises(TimeoutError):
            transport.origin()

    def test_transport_timeout_kills_owned_helpers_that_hold_output_pipes(self):
        binary = self.temp / 'synthetic-git'
        binary.write_text('#!/bin/sh\nsleep 20 &\nwait\n')
        binary.chmod(0o755)
        transport = status.GitTransport(self.clone)
        transport.deadline = time.monotonic() + 0.1
        before = time.monotonic()
        with mock.patch.object(status, 'GIT', str(binary)), self.assertRaises(TimeoutError):
            transport.origin()
        self.assertLess(time.monotonic() - before, 3)

    def test_air_poller_reads_real_status_and_alarms_on_missing_stale_hold_and_silence(self):
        state = self.checkpoint('HOLD_LOCK')
        self.exporter.flush()
        record = status.GitTransport(self.clone).read(self.exporter.ref)
        now = self.harness.clock.wall.timestamp()
        self.assertEqual(['HOLD_LOCK'], status.alarm_reasons(record, self.exporter.host, now))
        self.assertIn('watchdog_status_stale', status.alarm_reasons(record, self.exporter.host, now + status.AIR_STALE_S))
        self.assertEqual(['watchdog_status_invalid'], status.alarm_reasons({}, self.exporter.host, now))
        cursor = self.temp / 'air-cursor.json'
        with mock.patch.object(status.time, 'time', return_value=now), mock.patch('sys.stdout'):
            self.assertEqual(3, status.main(['poll', '--repository', str(self.clone), '--host', self.exporter.host, '--cursor-file', str(cursor)]))
            self.assertEqual(3, status.main(['poll', '--repository', str(self.clone), '--host', 'absent', '--cursor-file', str(self.temp / 'absent.json')]))

    def test_air_cursor_preserves_recovered_holds_between_polls_until_acknowledged(self):
        state = self.checkpoint('ACTIVE')
        self.exporter.flush()
        cursor = self.temp / 'air-cursor.json'
        argv = ['poll', '--repository', str(self.clone), '--host', self.exporter.host, '--cursor-file', str(cursor)]
        with mock.patch.object(status.time, 'time', side_effect=lambda: self.harness.clock.wall.timestamp()), mock.patch('sys.stdout'):
            self.assertEqual(0, status.main(argv))
            # A hold and recovery in the same rate-limited batch cannot vanish.
            self.advance(60)
            self.checkpoint('HOLD_PLAN_MALFORMED', state)
            self.checkpoint('ACTIVE', state)
            self.exporter.flush()
            self.assertEqual('ACTIVE', self.snapshot()['state'])
            self.assertEqual(3, status.main(argv))
            self.assertIn('transition:HOLD_PLAN_MALFORMED', json.loads(cursor.read_text())['pending_reasons'])
            self.assertEqual(3, status.main(argv))
            self.assertEqual(0, status.main([*argv, '--ack']))
            # A whole hold publication overwritten before the next poll is
            # also retained by traversal from the Air's acknowledged cursor.
            self.advance(60)
            self.checkpoint('HOLD_LOCK', state)
            self.exporter.flush()
            self.advance(60)
            self.checkpoint('ACTIVE', state)
            self.exporter.flush()
            self.assertEqual(3, status.main(argv))
            self.assertIn('transition:HOLD_LOCK', json.loads(cursor.read_text())['pending_reasons'])

    def test_real_entry_point_and_named_red_mutation_status_wiring_removed(self):
        # Real main: argv, Storage, service flock and real_dependencies. Only
        # the process-table and network endpoint seams are replaced. The plan
        # refusal precedes every host command, binary lookup and fork.
        installed.InstalledV5Tests.write_plan(self, unknown_future_key=1)
        source = Path(wd.__file__).read_text()
        line = '        storage.status_exporter = StatusExporter(storage, REPO_ROOT)\n'
        self.assertEqual(1, source.count(line))
        runner = self.temp / 'entry.py'
        runner.write_text('''import json, os, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from scripts import magistrate_watchdog as wd
from scripts import watchdog_status as status
if sys.argv[5] == "mutant":
    source = Path(wd.__file__).read_text().replace("        storage.status_exporter = StatusExporter(storage, REPO_ROOT)\\n", "        pass\\n")
    exec(compile(source, wd.__file__, "exec"), wd.__dict__)
wd.RealProcessTable.snapshot = lambda self: []
status.GitTransport.origin = lambda self: sys.argv[3]
# This entry-point wiring witness isolates the transport gate; the R3 span
# witnesses exercise the real gate against installed plans separately.
wd._configure_status_export = lambda storage, deps, state: None
code = wd.main(["--custody-root", sys.argv[2]])
root = Path(sys.argv[2])
assert code == 0
assert (root / "watchdog.lock").exists()
assert json.loads((root / "state.json").read_text())["state"] == "HOLD_PLAN_MALFORMED"
assert (root / "status-delivery.json").exists(), "STATUS-WIRING-REMOVED: no off-host receipt"
''')
        for variant in ('normal', 'mutant'):
            root = self.harness.storage.root
            (root / 'status-delivery.json').unlink(missing_ok=True)
            result = subprocess.run([sys.executable, '-B', str(runner), str(wd.REPO_ROOT), str(root),
                                     str(self.origin), 'unused', variant], capture_output=True, text=True,
                                    timeout=30, env={**os.environ, 'HOME': str(self.temp / 'home'),
                                                    'MAGISTRATE_WATCHDOG_STATUS_HOST': 'synthetic-mbp'})
            if variant == 'normal':
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual('HOLD_PLAN_MALFORMED', self.snapshot()['state'])
            else:
                self.assertNotEqual(0, result.returncode)
                self.assertIn('STATUS-WIRING-REMOVED', result.stderr)
