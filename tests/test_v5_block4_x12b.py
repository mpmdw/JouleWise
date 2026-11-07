"""Historical argv outcome readers and current process-builder checks.

No command is executed and no sealed source-layout inventory is rewritten.
"""
import ast
import base64
import inspect
import io
import itertools
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import unittest
from unittest import mock

from joulewise import receipt_readers as readiness; from joulewise import physical_checks as author
from joulewise import clock_reference; from joulewise import kernel_clock; from joulewise import night_gate; from joulewise import rehearsal_readers as t0
from joulewise import prewindow
from types import SimpleNamespace
from scripts import run_night as driver

ROOT = Path(__file__).resolve().parents[1]




class RegisteredRosterTests(unittest.TestCase):
    pass

    def test_exact_argv_outcomes_follow_consumers(self):
        cases = [(('/usr/bin/pgrep', '-lf', prewindow.CONTAMINANTS), (0, 1)),
                 (('/usr/bin/pgrep', '-lf', '-g', '123,456', '.'), (0, 1))]
        for argv, codes in cases:
            for code in (*codes, 2):
                row = dict(argv=argv, expected_outcome=t0.qualification_process_outcome(argv),
                           state='EXITED', exit_code=code, timed_out=False, stdout='17 resident matches\n')
                self.assertEqual(t0.qualification_process_completed(row), code in codes)
        for server in clock_reference.SERVER_ROSTER:
            argv = clock_reference.build_sntp_argv(server)
            for code in (0, 1, 2, -9):
                row = dict(argv=argv, expected_outcome=t0.qualification_process_outcome(argv),
                           state='EXITED', exit_code=code, timed_out=False)
                self.assertTrue(t0.qualification_process_completed(row))
                row['timed_out'] = True
                self.assertFalse(t0.qualification_process_completed(row))
        unknown = ['/usr/bin/pgrep', '-lf', 'unregistered-pattern']
        self.assertEqual(t0.qualification_process_outcome(unknown), {'unregistered': True})
        census = cases[0][0]
        outcome = t0.qualification_process_outcome(census)
        outcome['exit_codes'].append(2)
        self.assertEqual(t0.qualification_process_outcome(census), {'exit_codes': [0, 1]})

    def test_ast_literal_argv_census_has_no_missing_registration(self):
        """Census source expressions, including new probes in existing functions.

        Dynamic slots use representative values. Forwarded argv are separately
        exercised through the real stage builders and full author below.
        """
        from scripts import run_night
        modules = (author, run_night, night_gate)
        seen = []
        for module in modules:
            tree = ast.parse(inspect.getsource(module))
            def value(node):
                if isinstance(node, ast.Constant):
                    return node.value
                if isinstance(node, ast.Name):
                    known = vars(module).get(node.id)
                    if isinstance(known, (str, tuple)):
                        return known
                    if node.id == 'expected_prewindow_script':
                        return '/fixture/joulewise/prewindow.py'
                    return ('time.apple.com' if node.id == 'server' else '123' if node.id in {'pgid', 'pids'}
                            else '/fixture/.venv/bin/python' if node.id == 'python' else '/fixture')
                if isinstance(node, ast.Attribute):
                    try:
                        return eval(ast.unparse(node), vars(module))
                    except (NameError, AttributeError):
                        return '/fixture'
                if isinstance(node, ast.Subscript):
                    return '/fixture'
                if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
                    return str(Path(value(node.left)) / str(value(node.right)))
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute) and node.func.attr in {'absolute', 'resolve'}:
                        return value(node.func.value)
                    if isinstance(node.func, ast.Attribute) and node.func.attr == 'join':
                        return '123,456'
                    if node.args:
                        return str(value(node.args[0]))
                    return '/fixture'
                return '/fixture'
            for node in ast.walk(tree):
                if not isinstance(node, (ast.List, ast.Tuple)) or not node.elts:
                    continue
                # Every literal executable vector, plus the stage's python
                # vectors. Plain data arrays are outside the launch census.
                first = node.elts[0]
                dynamic_executable = (isinstance(first, ast.Attribute) and ast.unparse(first) == 'sys.executable'
                    or isinstance(first, ast.Call) and isinstance(first.func, ast.Name) and first.func.id == 'str'
                    and len(node.elts) > 1 and (str(value(first)).endswith('/python')
                        or isinstance(node.elts[1], ast.Constant) and isinstance(node.elts[1].value, str)
                        and node.elts[1].value.startswith('-')))
                if not (isinstance(first, ast.Constant) and isinstance(first.value, str)
                        and (first.value.startswith(('/bin/', '/usr/bin/', '/usr/sbin/')) or first.value == 'git')
                        or isinstance(first, ast.Name) and first.id == 'python' or dynamic_executable):
                    continue
                argv = tuple(str(value(item)) for item in node.elts)
                # Known concatenations (resync prefix, power adapter) are
                # represented by the complete builder test, not a partial argv.
                if any(isinstance(item, ast.Starred) for item in node.elts):
                    continue
                seen.append((module.__name__, node.lineno, argv))
                self.assertIsNotNone(t0.qualification_process_registration(argv),
                                     f'{module.__name__}:{node.lineno}: {argv}')
        self.assertGreater(len(seen), 25)

    def test_current_driver_builder_roster_is_registered(self):
        from types import SimpleNamespace
        for kind in ('sample', 'arm'):
            argv = driver._bind_argv(kind, 'job', 5, {'interval': 1, 'observer_pid': 123})
            self.assertIsNotNone(t0.qualification_process_registration(argv), argv)
        plan = SimpleNamespace(measurement_root='/fixture', custody_root='/fixture/custody', plan_id='fixture',
                               pack_night={'pack_root': '/fixture/pack'})
        with mock.patch.object(driver, '_watchdog_liveness_for_courier', return_value=('/fixture/watchdog', 0, 'idle')):
            argv = driver._courier_argv(Path('/fixture/custody'), plan, Path('/fixture/courier'))
        self.assertIsNotNone(t0.qualification_process_registration(argv), argv)
        from types import SimpleNamespace
        from joulewise.adapters.powermetrics import PowermetricsTelemetryAdapter
        adapter = PowermetricsTelemetryAdapter(None, privilege_prefix=('sudo', '-n'))
        argv = adapter._command(SimpleNamespace(sampling=SimpleNamespace(power_hz=10.)),
                                Path('/fixture/powermetrics-idle.plist'), count=300)
        self.assertIsNotNone(t0.qualification_process_registration(argv), argv)

    def test_missing_table_row_and_new_governed_argv_are_detected(self):
        argv = ('/usr/bin/pgrep', '-lf', prewindow.CONTAMINANTS)
        shortened = tuple(row for row in t0.QUALIFICATION_PROCESS_OUTCOMES if row[0] != argv)
        with mock.patch.object(t0, 'QUALIFICATION_PROCESS_OUTCOMES', shortened):
            with self.assertRaises(AssertionError):
                self.test_ast_literal_argv_census_has_no_missing_registration()
        with mock.patch.object(author, 'AGENT_CENSUS_ARGV', ('/usr/bin/pgrep', '-lf', 'new census'), create=True):
            self.assertIsNone(t0.qualification_process_registration(author.AGENT_CENSUS_ARGV))

















if __name__ == '__main__':
    unittest.main()
