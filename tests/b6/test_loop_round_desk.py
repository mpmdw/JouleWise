"""Real loop/adapters/plan/installer/harvest/structure/compression, synthetic only."""
import json
from pathlib import Path

from joulewise.b5 import plan
from joulewise.b6.driver_lane import metadata_path, read
from joulewise.b6.lanes import Done, Prepared, Refused, Running
from joulewise.b6.loop import atomic_state
from tests.b6.round_support import Round
from tests.b6.support import DeskCase
from tests import test_harvest_b5_window as windows


def tearDownModule():
    windows.tearDownModule()


class RoundTests(DeskCase):
    def test_alpha_smoke_session_desk_and_beta_rotation(self):
        r = Round(self.root)
        r.until('PRECHECK')
        prepared = Prepared(**r.state()['session']['prepared'])
        self.assertFalse(Path(prepared.plan_path).exists())
        self.assertNotIn('t0_epoch_s', read(metadata_path(prepared))['inputs'])
        r.until('ROTATE')
        state = r.state()
        self.assertEqual(len(state['attempts']), 1)
        line = state['attempts'][0]['line']
        self.assertEqual(line['harvest_rc'], 6)
        self.assertTrue(line['structure_ok'], line)
        self.assertTrue(line['compressed'], line)
        metadata = read(metadata_path(prepared))
        self.assertEqual(metadata['pin_advance']['status'], 'ADVANCED')
        self.assertFalse(plan.ledger_head_status(r.measurement)['blocking'])
        self.assertTrue(list(Path(metadata['paths']['export']).rglob('*.runs.csv')))
        self.assertTrue(Path(metadata['paths']['custody'], 'raw-transcript.txt.zst').is_file())
        before = len(r.calls)
        self.assertIsInstance(r.lanes.driver.launch(prepared), Running)
        r.lanes.driver.status(Running(str(metadata_path(prepared))))
        self.assertFalse(any('--uninstall' in row for row in r.calls[before:]))
        # Re-enter K1 as after a crash following the durable append but before
        # the state transition. Run the real desk a second time on these bytes.
        attempts = (r.loop_root / 'attempts.jsonl').read_bytes()
        state['state'] = 'SESSION_DESK'
        atomic_state(r.loop_root / 'state.json', state)
        r.loop.tick()
        self.assertEqual(r.state()['state'], 'ROTATE')
        self.assertEqual((r.loop_root / 'attempts.jsonl').read_bytes(), attempts)
        self.assertEqual(len(attempts.splitlines()), 1)
        self.assertEqual(r.state()['attempts'][0]['line']['harvest_rc'], 6)
        self.assertFalse(r.state().get('harvest_fault'))
        r.loop.tick()
        r.loop.tick()
        self.assertEqual(r.state()['session']['packs'], ['beta'])

    def test_physics_refusal_wait_reprepare_then_retry(self):
        r = Round(self.root, refuse=True)
        r.until('WAIT_PHYSICS')
        state = r.state()
        self.assertEqual(state['wait']['hazard'], 'battery')
        old = state['session']['smoke_prepared'] if 'smoke_prepared' in state['session'] else None
        r.until('SMOKE_DESK')
        self.assertNotEqual(r.state()['session']['smoke_prepared'], old)
        self.assertEqual(r.state()['session']['smoke_done']['chain_rc'], 0)
        r.until('ROTATE')
        self.assertEqual(len(r.state()['attempts']), 1)

    def test_lost_session_reaches_desk_and_holds_before_beta(self):
        r = Round(self.root)
        r.until('SESSION_RUN')
        control = read(r.control)
        control['lost'] = True
        r.control.write_text(json.dumps(control))
        r.until('HOLD_LOOP')
        state = r.state()
        self.assertEqual(state['hold_reason'], 'structure_defect')
        line = state['attempts'][0]['line']
        self.assertEqual((line['chain_rc'], line['physics_stop']), (1, None))
        self.assertFalse(line['structure_ok'])
        self.assertIn('chain_crashed', line['structure_defects'])
        # The lost chain's open bracket session is aborted at the desk, so the
        # pin advances and the next session's plan can reserve the ledger.
        self.assertIn('records.terminal_record_absent', line['window_flags'])
        self.assertNotIn('records.pin_ledger', line['window_flags'])
        self.assertFalse(plan.ledger_head_status(r.measurement)['blocking'])
        self.assertNotEqual(line['harvest_rc'], 3)
        self.assertEqual(state['session']['packs'], ['alpha'])

    def test_resume_after_hold_continues_real_round(self):
        r = Round(self.root)
        r.until('PRECHECK')
        r.loop.control('hold')
        self.assertEqual(r.state()['state'], 'HOLD_LOOP')
        r.loop.control('resume')
        r.until('ROTATE')
        self.assertTrue(r.state()['attempts'][0]['line']['structure_ok'])
