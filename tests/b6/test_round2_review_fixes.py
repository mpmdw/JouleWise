"""Desk failures and abandoned notices must not stall unattended collection."""
import ast
from pathlib import Path
import subprocess
from types import SimpleNamespace
from unittest.mock import Mock, patch

from joulewise.b5 import chain, plan
from joulewise.b6.desk_lane import DeskLane
from joulewise.b6.driver_lane import write
from joulewise.b6.mailer import Mailer
from joulewise.b6.loop import Loop
from joulewise.b6.lanes import Hazard, PrecheckResult
from scripts import run_night
from tests.b6.support import DeskCase


class RoundTwoReviewTests(DeskCase):
    def test_every_driver_courier_path_supplies_its_plan(self):
        # Each entry path must preserve block 6's program-only courier policy,
        # including the malformed-plan and dead-man reporting paths.
        tree = ast.parse(Path(run_night.__file__).read_text())
        calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
                 and isinstance(node.func, ast.Name) and node.func.id == '_resolve_courier_bin']
        self.assertTrue(calls)
        for call in calls:
            self.assertIn('plan', [key.arg for key in call.keywords])

    def test_malformed_block6_plan_retains_program_courier_selection(self):
        path = self.root / 'malformed.json'
        write(path, {'measurement_root': str(self.root), 'hazard_window': {'bindings': {'capture_screen': {}}}})
        fallback = run_night._fallback_plan(path)
        with patch('joulewise.b6.courier.resolve', return_value=(None, 'fixture_missing')) as resolve:
            self.assertEqual(run_night._resolve_courier_bin(None, plan=fallback), (None, 'fixture_missing', None))
        resolve.assert_called_once_with(None, str(self.root))

    def test_clock_rate_hold_attempts_one_remedy_and_wakes_without_wait_loop(self):
        loop = object.__new__(Loop)
        loop.state = {'state': 'PRECHECK', 'wait': None}
        loop.clock = lambda: 10
        loop.lanes = SimpleNamespace(precheck=SimpleNamespace(remedy=Mock(return_value=False)))
        loop._transition = lambda state: loop.state.update(state=state)
        loop._event, loop._missing = Mock(), Mock(return_value=False)
        loop._wait_for(PrecheckResult(would_refuse=(Hazard('clock'),), remedies=('clock',)), 'PRECHECK')
        self.assertEqual(loop.state['state'], 'HOLD_LOOP')
        loop.lanes.precheck.remedy.assert_called_once_with('clock')
        loop._event.assert_called_once_with('loop_hold', 'clock_rate_after_remedy')

    def test_failed_resume_retries_once_then_aborts_and_names_slot(self):
        metadata = {'paths': {'measurement': str(self.root), 'custody': str(self.root / 'custody')},
                    'runs_roots': [str(self.root / 'runs')], 'inputs': {'bracket_session_id': 's'},
                    'prepared': {'plan_path': str(self.root / 'night_plan.json')}}
        write(self.root / 'night_plan.json', {'hazard_window': {'bindings': {},
              'pack': {'pack_root': str(self.root / 'pack')}}})
        write(self.root / 'pack/plan_tree.json', {})
        status = {'open_sessions': ['s'], 'open_session_next_slots': {
            's': {'next_slot': 'pre', 'custody_state': 'complete'}}}
        for failures in ((SimpleNamespace(returncode=1, stdout=''),) * 2,
                         (subprocess.TimeoutExpired('fixture', 120),) * 2):
            with self.subTest(failures=type(failures[0]).__name__):
                runner = Mock(side_effect=failures)
                metadata.pop('bracket_resume', None)
                lane = DeskLane(self.root, self.root / 'loop', runner)
                with patch.object(plan, 'ledger_head_status', return_value=status), \
                     patch.object(chain, 'stage_plan', return_value=[SimpleNamespace(kind='bracket_reservation')]), \
                     patch.object(chain, 'stage_argv', return_value=['reserve', '--plan', 'frozen.json']), \
                     patch('joulewise.calibration_ledger.abort_bracket_session') as abort, \
                     patch.object(plan, 'advance_ledger_pin', return_value={'status': 'ADVANCED'}), \
                     patch('joulewise.flags.core.hazard_flag_context', return_value=object()), \
                     patch('joulewise.flags.core.emit') as emit:
                    flags = lane._advance(metadata)
                self.assertEqual([c.kwargs['timeout'] for c in runner.call_args_list], [120, 600])
                abort.assert_called_once()
                self.assertIn('records.resume_finalize_failed', flags)
                self.assertEqual(emit.call_args.kwargs['observed']['slot'], 'pre')
                self.assertEqual(metadata['bracket_resume'][-1]['slot'], 'pre')

    def test_closing_undelivered_notice_withdraws_it_permanently(self):
        transport, smtp = Mock(), Mock()
        mailer = Mailer(self.root, {}, clock=lambda: 10_000, transport=transport, smtp=smtp)
        key = mailer.enqueue('arm_notice', 'dropped-session', None, {})
        mailer.close_notice(key)
        mailer.flush()
        self.assertTrue(mailer.entry(key)['withdrawn'])
        transport.send.assert_not_called()
        smtp.send.assert_not_called()

    def test_closing_delivered_notice_closes_its_remote_receipt(self):
        transport = Mock()
        transport.send.return_value = {'issue_number': 123}
        mailer = Mailer(self.root, {}, clock=lambda: 10_000, transport=transport)
        key = mailer.enqueue('arm_notice', 'delivered-session', None, {})
        mailer.flush()
        mailer.close_notice(key)
        mailer.flush()
        transport.close.assert_called_once_with({'issue_number': 123})
