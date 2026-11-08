"""The optional array backends must not be loaded at module import time."""

import subprocess
import sys
import unittest


class LazyImportTests(unittest.TestCase):
    def test_import_without_numerical_backends(self):
        code = '''
import builtins
original = builtins.__import__
def blocked(name, *args, **kwargs):
    if name.split('.')[0] in ('numpy', 'mlx'):
        raise AssertionError('eager numerical import: ' + name)
    return original(name, *args, **kwargs)
builtins.__import__ = blocked
from joulewise.interp_energy.weight_edits import SparseDelta, WeightSwap
assert SparseDelta({}).before_hashes == {}
assert WeightSwap({}, {}).apply().changed_bytes == 0
'''
        result = subprocess.run([sys.executable, "-B", "-c", code], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
