"""Tests of joulewise.hazards (gate-prune lane L1).

``unittest discover -s tests`` would import these modules as ``hazards.*``,
while ``scripts/shard_tests.py`` names them ``tests.hazards.*``;
tests/test_shard_tests.py requires the two runners to agree.  This package
therefore loads its test modules under their canonical repository names.
"""

import importlib
import pkgutil


def load_tests(loader, standard_tests, pattern):
    for info in sorted(pkgutil.iter_modules(__path__), key=lambda item: item.name):
        if info.name.startswith("test"):
            module = importlib.import_module(f"tests.hazards.{info.name}")
            standard_tests.addTests(loader.loadTestsFromModule(module))
    return standard_tests
