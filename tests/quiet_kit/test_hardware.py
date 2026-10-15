import ctypes
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from joulewise.quiet_kit.hardware import Hardware, coregraphics_display_state
from joulewise.quiet_kit.runner import Runner
from .fakes import FakeHardware


class DisplayTests(unittest.TestCase):
    def library(self, asleep=1, active=1, display=42):
        return SimpleNamespace(CGMainDisplayID=Mock(return_value=display),
                               CGDisplayIsAsleep=Mock(return_value=asleep),
                               CGDisplayIsActive=Mock(return_value=active))

    def test_coregraphics_ctypes_contract_and_boolean_states(self):
        for asleep, active in [(0, 1), (1, 1), (0, 0)]:
            cg = self.library(asleep, active)
            state, reason = coregraphics_display_state(load=lambda _: cg)
            self.assertEqual(state, {'display_id': 42, 'asleep': bool(asleep), 'active': bool(active)})
            self.assertIsNone(reason)
            self.assertEqual(cg.CGMainDisplayID.argtypes, [])
            self.assertIs(cg.CGMainDisplayID.restype, ctypes.c_uint32)
            for fn in (cg.CGDisplayIsActive, cg.CGDisplayIsAsleep):
                self.assertEqual(fn.argtypes, [ctypes.c_uint32])
                self.assertIs(fn.restype, ctypes.c_uint32)
                fn.assert_called_once_with(42)

    def test_unavailable_coregraphics_and_no_main_display_keep_reasons(self):
        state, reason = coregraphics_display_state(load=Mock(side_effect=OSError('unavailable')))
        self.assertIsNone(state)
        self.assertIn('CoreGraphics unavailable: OSError: unavailable', reason)
        cg = self.library(display=0)
        self.assertEqual(coregraphics_display_state(load=lambda _: cg), (None, 'CoreGraphics reported no main display'))
        cg.CGDisplayIsAsleep.assert_not_called()

    def test_observe_uses_coregraphics_when_ioreg_class_is_absent(self):
        from joulewise.hazards.base import Completed
        ctx = SimpleNamespace(run=lambda argv, timeout: Completed(tuple(argv), 0, b'', b''))
        hw = Hardware(Path(__file__).resolve().parents[2], '/fake/model-python')
        state = {'display_id': 1, 'asleep': True, 'active': True}
        with (patch.object(hw, 'ctx', return_value=ctx),
              patch('joulewise.hazards.contention.take_snapshot', return_value=SimpleNamespace(rows={}, error=None)),
              patch('joulewise.hazards.clock.read_boot_session', return_value='boot'),
              patch('joulewise.quiet_kit.hardware.coregraphics_display_state', return_value=(state, None))):
            out = hw.observe(Path('.'))
        self.assertEqual(out['display_state'], state)
        self.assertEqual(out['diagnostics']['display']['stdout'], '')
        self.assertEqual(out['display_state_source'], 'CoreGraphics')
        runner = Runner(hw.repo, hw.repo/'.scratch-qk/display-test', '/fake/model-python', FakeHardware().seams())
        flags = runner._flags({}, [], out, {**out, 'display_state': {**state, 'asleep': False}})
        self.assertIn('display power state changed during test', [f['reason'] for f in flags])
