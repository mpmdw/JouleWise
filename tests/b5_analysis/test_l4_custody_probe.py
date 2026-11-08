"""D-188 L4 storability (b5 under-90 round 2): the custody probe thread is exempt, and only it.

The verified store marks any fill that starts a thread unstorable. The calibration
bracket (L4) always ran calibration_ledger.probe_custody's locator probe, so it
was never stored and steps 4 and 5 recomputed every bracket. The probe thread is
exempt only while it does nothing but Path.exists/Path.is_dir (pinned below);
probe_custody itself marks timed-out, failed, negative and backup-locator probes.
"""
from __future__ import annotations

import ast
import inspect
import os
from pathlib import Path
import tempfile
import textwrap
import threading
import unittest
from unittest import mock

from joulewise import analysis_verified_store as vdl
from joulewise import calibration_ledger as ledger


def probe_node():
    tree = ast.parse(textwrap.dedent(inspect.getsource(ledger.probe_custody)))
    outer = tree.body[0]
    return next(node for node in ast.walk(outer) if isinstance(node, ast.FunctionDef) and node.name == 'probe')


class ProbeCodeIsPinned(unittest.TestCase):
    def test_probe_does_only_exists_and_is_dir(self):
        node = probe_node()
        calls = sorted(ast.unparse(call.func) for call in ast.walk(node) if isinstance(call, ast.Call))
        self.assertEqual(calls, ['candidate.exists', 'candidate.is_dir', 'failed.append', 'result.append'])
        names = {name.id for name in ast.walk(node) if isinstance(name, ast.Name)}
        self.assertEqual(names, {'candidate', 'paths', 'result', 'failed', 'BaseException'})
        attributes = {ast.unparse(attr) for attr in ast.walk(node) if isinstance(attr, ast.Attribute)}
        self.assertEqual(attributes, {'candidate.exists', 'candidate.is_dir', 'failed.append', 'result.append'})
        kinds = {type(item).__name__ for item in ast.walk(node)}
        self.assertTrue(kinds <= {'FunctionDef', 'arguments', 'Try', 'For', 'If', 'Call', 'Attribute', 'Name',
                                  'Load', 'Store', 'Expr', 'Tuple', 'Return', 'ExceptHandler', 'Constant'}, kinds)

    def test_the_exempt_code_object_is_that_function(self):
        code = ledger.custody_probe_code()
        self.assertEqual(code.co_qualname, 'probe_custody.<locals>.probe')
        self.assertIn(code, ledger.probe_custody.__code__.co_consts)


class StoreExemption(unittest.TestCase):
    def fill(self):
        vdl._install_hook()
        fill = vdl._Fill()
        token = vdl._FILLS.set((fill,))
        self.addCleanup(vdl._FILLS.reset, token)
        return fill

    def environment(self):
        patcher = mock.patch.dict(os.environ)
        patcher.start()
        self.addCleanup(patcher.stop)
        for name in ('JOULEWISE_BACKUP_ROOTS', ledger.NIGHT_CUSTODY_BUDGET_ENV):
            os.environ.pop(name, None)

    def test_positive_single_locator_probe_keeps_the_fill_storable(self):
        self.environment()
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        fill = self.fill()
        result = ledger.probe_custody(Path(directory.name), lambda path: ('inspected', path), lambda: 'absent')
        self.assertEqual(result[0], 'inspected')
        self.assertEqual(fill.unstorable, set())

    def test_negative_probes_mark_the_fill(self):
        self.environment()
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        directory = holder.name
        file = Path(directory) / 'file'
        file.write_text('x')
        if True:
            fill = self.fill()
            self.assertEqual(ledger.probe_custody(Path(directory) / 'missing', lambda p: 'x', lambda: 'absent'),
                             'absent')
            self.assertEqual(fill.unstorable, {'noted:custody_probe_absent'})
            fill = self.fill()
            self.assertEqual(ledger.probe_custody(file, lambda p: 'x', lambda: 'absent',
                                                  not_directory=lambda: 'nd'), 'nd')
            self.assertEqual(fill.unstorable, {'noted:custody_probe_not_directory'})

    def test_a_failed_probe_marks_the_fill(self):
        self.environment()
        fill = self.fill()
        with mock.patch.object(Path, 'exists', side_effect=RuntimeError('boom')):
            self.assertEqual(ledger.probe_custody(Path('/nonexistent-b5'), lambda p: 'x', lambda: 'absent'), 'absent')
        self.assertIn('noted:custody_probe_exception', fill.unstorable)

    def test_any_other_thread_still_marks_the_fill(self):
        code = ledger.custody_probe_code()
        for name, target in ((ledger.CUSTODY_PROBE_THREAD_NAME, lambda: None),
                             ('other', lambda: None)):
            fill = self.fill()
            thread = threading.Thread(target=target, name=name)
            thread.start()
            thread.join()
            self.assertEqual(fill.unstorable, {'thread'}, name)
        # The exact probe code under another thread name is not exempt either.
        fill = self.fill()
        probe = type(lambda: None)(code, {'BaseException': BaseException},
                                   closure=tuple(type((lambda x: lambda: x)(0).__closure__[0])(v)
                                                 for v in ((), [], [])))
        thread = threading.Thread(target=probe, name='renamed')
        thread.start()
        thread.join()
        self.assertEqual(fill.unstorable, {'thread'})


if __name__ == '__main__':
    unittest.main()
