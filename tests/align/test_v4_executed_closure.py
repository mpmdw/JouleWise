"""Drift guard: the exact-candidate receipt binds the executed module closure.

Stdlib ``ast`` only; static imports (module level and function level, so lazy
imports such as the endpoint's cache/sampling/MLX adapter are included). It
cannot see ``importlib.import_module(<string>)`` loads or third-party code.
"""
import ast
import json
from pathlib import Path
import unittest

from joulewise.align.apple import v4_registration as registration

ROOT = Path(__file__).resolve().parents[2]
# The episode path and the W1/D night entry points (R11 lead ruling 3).
ENTRY_POINTS = ('joulewise/align/apple/endpoint.py', 'scripts/run_night.py',
                'scripts/align_v4_session.py')
FIRST_PARTY = ('joulewise', 'scripts')


def _resolve(module):
    base = ROOT.joinpath(*module.split('.'))
    for candidate in (base.with_suffix('.py'), base / '__init__.py'):
        if candidate.is_file():
            return candidate.relative_to(ROOT).as_posix()
    return None


def _imports(relative):
    path = ROOT / relative
    package = relative[:-3].split('/')
    package = package if path.name == '__init__.py' else package[:-1]
    if path.name == '__init__.py':
        package = package[:-1]
    names = set()
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            base = package[:len(package)-(node.level-1)] if node.level else []
            module = '.'.join(base + ([node.module] if node.module else []))
            names.add(module)
            names.update(f'{module}.{alias.name}' for alias in node.names)
    return names


def executed_closure(entries=ENTRY_POINTS):
    """Repo-relative first-party files statically reachable from ``entries``."""
    seen, todo = set(), list(entries)
    while todo:
        relative = todo.pop()
        if relative in seen:
            continue
        seen.add(relative)
        for name in _imports(relative):
            parts = name.split('.')
            if parts[0] not in FIRST_PARTY:
                continue
            for end in range(1, len(parts)+1):   # parent packages execute too
                found = _resolve('.'.join(parts[:end]))
                if found:
                    todo.append(found)
    return seen


class ExecutedClosureBindingTests(unittest.TestCase):
    def test_every_executed_joulewise_module_is_in_the_receipt_artifact_set(self):
        closure = {p for p in executed_closure() if p.startswith('joulewise/')}
        for required in ('joulewise/align/apple/prompt_cache.py', 'joulewise/align/apple/sampler.py',
                         'joulewise/align/apple/sampling.py', 'joulewise/align/apple/generation.py',
                         'joulewise/align/apple/budget.py', 'joulewise/align/apple/xml_tool_calls.py',
                         'joulewise/adapters/mlx_runtime.py', 'joulewise/external/km003c_parse.py'):
            self.assertIn(required, closure)
        missing = sorted(closure - set(registration.ARTIFACTS))
        self.assertEqual(missing, [], 'add these to v4_registration.ARTIFACTS (and the receipt template)')

    def test_artifact_set_has_no_duplicates_or_missing_files_and_matches_template(self):
        artifacts = registration.ARTIFACTS
        self.assertEqual(len(artifacts), len(set(artifacts)))
        pending = {p for p in artifacts if p.startswith(registration.REGISTRATION)}   # lead-supplied inputs
        self.assertEqual([p for p in artifacts if p not in pending and not (ROOT / p).is_file()], [])
        template = json.loads((ROOT / registration.REGISTRATION / 'registration_receipt.json').read_text())
        self.assertEqual(set(template['artifacts']), set(artifacts))


if __name__ == '__main__':
    unittest.main()
