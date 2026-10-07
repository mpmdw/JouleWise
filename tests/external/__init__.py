"""Tests of joulewise.external (the KM003C wall-meter stream; lane smc-battery-meter).

``unittest discover -s tests`` would import these modules as ``external.*``,
while ``scripts/shard_tests.py`` names them ``tests.external.*``;
tests/test_shard_tests.py requires the two runners to agree.  This package
therefore loads its test modules under their canonical repository names, as
tests/hazards does.
"""

import importlib
import pkgutil


def load_tests(loader, standard_tests, pattern):
    for info in sorted(pkgutil.iter_modules(__path__), key=lambda item: item.name):
        if info.name.startswith("test"):
            module = importlib.import_module(f"tests.external.{info.name}")
            standard_tests.addTests(loader.loadTestsFromModule(module))
    return standard_tests
