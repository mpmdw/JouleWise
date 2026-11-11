"""Synthetic witnesses for the W1 watchdog merge boundaries."""
import contextlib
import io
import json
from unittest import mock

from scripts import magistrate_watchdog as wd
from tests.test_magistrate_watchdog import WatchdogTestCase


class IntegratedWatchdogTests(WatchdogTestCase):
    def test_named_hold_receipts_precede_the_status_checkpoint(self):
        storage = self.harness.storage
        storage.mkdir(storage.root)
        state = wd.initial_state()
        checkpoints = []

        def checkpoint(value, *, transition=False):
            events = [json.loads(line) for line in
                      (storage.root / 'events.jsonl').read_text().splitlines()]
            checkpoints.append((value['state'], transition, events))

        storage.status_exporter = mock.Mock(checkpoint=checkpoint)
        wd.transition(storage, state, 'HOLD_PLAN_MALFORMED', 'synthetic unknown key', self.base)
        word, changed, events = checkpoints[-1]
        self.assertEqual(word, 'HOLD_PLAN_MALFORMED')
        self.assertTrue(changed)
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]['activity'], word)
        self.assertEqual(events[0]['event'], 'start')
        self.assertEqual(events[1]['kind'], 'transition')

        wd.transition(storage, state, 'READY', 'synthetic repair', self.base)
        _, changed, events = checkpoints[-1]
        self.assertTrue(changed)
        self.assertEqual(events[-2]['event'], 'end')
        self.assertEqual(events[-2]['span_id'], events[0]['span_id'])
        self.assertEqual(events[-1]['to'], 'READY')

    def test_cli_dry_run_uses_the_integrated_tick_without_writes_or_spawn(self):
        output = io.StringIO()
        with mock.patch.object(wd, 'real_dependencies', return_value=self.harness.deps), \
             mock.patch.object(wd.os, 'fork') as fork, \
             mock.patch.dict(wd.os.environ, {'MAGISTRATE_WATCHDOG_STATUS_HOST': 'synthetic-w1'}), \
             contextlib.redirect_stdout(output):
            code = wd.main(['--dry-run', '--custody-root', str(self.harness.storage.root)])
        self.assertEqual(code, 0)
        self.assertIn('decision=LAUNCHING', output.getvalue())
        self.assertIn('child spawn suppressed', output.getvalue())
        self.assertFalse(self.harness.storage.root.exists())
        self.assertEqual(self.harness.spawn_calls, [])
        fork.assert_not_called()
