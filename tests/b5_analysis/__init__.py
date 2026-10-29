"""Load canonical names under both unittest discovery and the shard runner."""
import importlib
import pkgutil


def load_tests(loader, standard_tests, pattern):
    for info in sorted(pkgutil.iter_modules(__path__), key=lambda item: item.name):
        if info.name.startswith("test"):
            module = importlib.import_module(f"tests.b5_analysis.{info.name}")
            standard_tests.addTests(loader.loadTestsFromModule(module))
    return standard_tests
