"""Register twin tests under the same names for discovery and sharding."""

import fnmatch
import importlib
import pkgutil


def load_tests(loader, standard_tests, pattern):
    for info in sorted(pkgutil.iter_modules(__path__), key=lambda item: item.name):
        if fnmatch.fnmatch(info.name + ".py", pattern or "test*.py"):
            module = importlib.import_module(f"tests.twins.{info.name}")
            standard_tests.addTests(loader.loadTestsFromModule(module))
    return standard_tests
