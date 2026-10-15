"""Desk tests, using canonical names under discovery and the shard runner."""

import fnmatch
import importlib
import pkgutil


def load_tests(loader, standard_tests, pattern):
    # Match tests/hazards: bare ``discover -s tests`` must not rename these
    # classes to quiet_kit.* and disagree with the module-atomic CI runner.
    for info in sorted(pkgutil.iter_modules(__path__), key=lambda item: item.name):
        if info.name.startswith('test_') and fnmatch.fnmatch(info.name+'.py', pattern or 'test*.py'):
            module=importlib.import_module(f'tests.quiet_kit.{info.name}')
            standard_tests.addTests(loader.loadTestsFromModule(module))
    return standard_tests
