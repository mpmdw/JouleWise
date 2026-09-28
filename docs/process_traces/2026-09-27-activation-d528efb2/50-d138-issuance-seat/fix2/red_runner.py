import importlib.util
import os
from pathlib import Path
import sys
import unittest

target = Path(os.environ['D138_TARGET_ROOT'])
fix = Path(os.environ['D138_FIX_ROOT'])
module_name, class_name, method_name = sys.argv[1].split(':')
sys.path.insert(0, str(target))
__import__('tests')
if module_name == 'tests.test_calibration_bracketing':
    helper_name = 'tests.test_claim_hold_routes'
    helper_path = fix / 'tests/test_claim_hold_routes.py'
    helper_spec = importlib.util.spec_from_file_location(helper_name, helper_path)
    helper = importlib.util.module_from_spec(helper_spec)
    sys.modules[helper_name] = helper
    helper_spec.loader.exec_module(helper)
path = fix / (module_name.replace('.', '/') + '.py')
spec = importlib.util.spec_from_file_location(module_name, path)
module = importlib.util.module_from_spec(spec)
sys.modules[module_name] = module
spec.loader.exec_module(module)
case = getattr(module, class_name)(method_name)
result = unittest.TextTestRunner(verbosity=1).run(unittest.TestSuite([case]))
sys.exit(0 if result.wasSuccessful() else 1)
