"""Drift guard: the exact-candidate receipt binds the executed code closure.

Stdlib ``ast``/``re`` only. Edges followed: static imports (module and function
level, so lazy imports are included) and script launch edges (a string constant that
is exactly ``scripts/<name>.py|zsh|sh`` in Python outside docstrings, or such a token
on a non-comment shell line: argv paths, the chain tool table, wrappers' exec
targets). It cannot see ``importlib.import_module(<string>)`` loads, computed paths
or third-party code.
"""
import ast
from functools import lru_cache
import json
from pathlib import Path
import re
import unittest

from joulewise.align.apple import v4_registration as registration

ROOT = Path(__file__).resolve().parents[2]
# The episode path and the W1/D/R1 execution entry points (R11 lead rulings 3, delta H01):
# the episode endpoint, the night runner, the session/kit/budget procedure and every
# night_chains shell wrapper.
ENTRY_POINTS = ('joulewise/align/apple/endpoint.py', 'scripts/run_night.py',
                'scripts/align_v4_session.py', 'scripts/align_v4_kit.py',
                'scripts/align_w1_budget_procedure.py',
                *sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / 'scripts/night_chains').glob('*')))
FIRST_PARTY = ('joulewise', 'scripts')
SCRIPT_EXACT = re.compile(r'^scripts/[A-Za-z0-9_./-]+\.(?:py|zsh|sh)$')
SCRIPT_TOKEN = re.compile(r'scripts/[A-Za-z0-9_./-]+?\.(?:py|zsh|sh)\b')


def _resolve(module):
    base = ROOT.joinpath(*module.split('.'))
    for candidate in (base.with_suffix('.py'), base / '__init__.py'):
        if candidate.is_file():
            return candidate.relative_to(ROOT).as_posix()
    return None


@lru_cache(maxsize=None)
def _edges(relative):
    """(imported module names, launched script paths) of one file."""
    path = ROOT / relative
    text = path.read_text()
    names, scripts = set(), set()
    if relative.endswith('.py'):
        package = relative[:-3].split('/')
        package = package if path.name == '__init__.py' else package[:-1]
        if path.name == '__init__.py':
            package = package[:-1]
        tree = ast.parse(text)
        docstrings = {id(n.body[0].value) for n in ast.walk(tree)
                      if isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
                      and n.body and isinstance(n.body[0], ast.Expr)
                      and isinstance(n.body[0].value, ast.Constant)}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                base = package[:len(package)-(node.level-1)] if node.level else []
                module = '.'.join(base + ([node.module] if node.module else []))
                names.add(module)
                names.update(f'{module}.{alias.name}' for alias in node.names)
            elif (isinstance(node, ast.Constant) and isinstance(node.value, str)
                  and id(node) not in docstrings and SCRIPT_EXACT.match(node.value)):
                scripts.add(node.value)
            elif isinstance(node, (ast.List, ast.Tuple)):
                # `python -m pkg` runs pkg/__main__.py: an argv sequence naming '-m' then a module.
                items = [e.value if isinstance(e, ast.Constant) and isinstance(e.value, str) else None
                         for e in node.elts]
                for flag, module in zip(items, items[1:]):
                    if flag == '-m' and module and module.split('.')[0] in FIRST_PARTY:
                        names.add(module + '.__main__')
    else:
        for line in text.splitlines():
            if not line.lstrip().startswith('#'):
                scripts.update(SCRIPT_TOKEN.findall(line))
    return names, {s for s in scripts if (ROOT / s).is_file()}


def executed_closure(entries=ENTRY_POINTS):
    """Repo-relative first-party files statically reachable from ``entries``."""
    seen, todo = set(), list(entries)
    while todo:
        relative = todo.pop()
        if relative in seen:
            continue
        seen.add(relative)
        names, scripts = _edges(relative)
        todo.extend(scripts)
        for name in names:
            parts = name.split('.')
            if parts[0] not in FIRST_PARTY:
                continue
            for end in range(1, len(parts)+1):   # parent packages execute too
                found = _resolve('.'.join(parts[:end]))
                if found:
                    todo.append(found)
    return seen


class ExecutedClosureBindingTests(unittest.TestCase):
    def test_r1_phase_table_is_named_and_strict(self):
        path = 'joulewise/align/apple/r1_phase_table.py'
        self.assertIn(path, registration._NAMED_ARTIFACTS)
        self.assertTrue(registration.is_strict(path))

    def test_v4_desk_harvest_resolves_to_the_bound_flag_catalog(self):
        """RL-62: the catalog that decides ``members_excluded`` in a v4 window is bound, strict.

        The v4 registration directory holds no ``acceptance.json``, so
        ``scripts/harvest_b6_session.py`` falls through to the Block 6 default
        (``(reg or registration.DEFAULTS)["catalog"]``). That fall-through stays;
        this test pins where it lands and the bytes it lands on.
        """
        import hashlib
        from joulewise.b6 import registration as b6_registration
        root = Path(__file__).resolve().parents[2]
        v4_registration_dir = root / registration.REGISTRATION
        self.assertFalse((v4_registration_dir / 'acceptance.json').exists())
        with self.assertRaises((OSError, ValueError)):
            b6_registration.load(v4_registration_dir)
        # The harvest's own resolution expression, read from its source.
        source = (root / 'scripts/harvest_b6_session.py').read_text(encoding='utf-8')
        self.assertIn('"catalog_path": ROOT / (reg or registration.DEFAULTS)["catalog"]', source)
        resolved = b6_registration.DEFAULTS['catalog']
        self.assertEqual(resolved, 'configs/b6/flag_catalog_b6.json')
        self.assertIn(resolved, registration._NAMED_ARTIFACTS)
        self.assertTrue(registration.is_strict(resolved))
        observed = hashlib.sha256((root / resolved).read_bytes()).hexdigest()
        # The digest the research lead read the excluding codes against (RL-62, RL-65). A changed
        # catalog must come back through the research lead before the registration is signed.
        self.assertEqual(observed, '01767fe4e75ed961798f4e6b68cf055a5b3946a474129e93d2b5e7c239a1dd0c')
        receipt = json.loads((v4_registration_dir / 'registration_receipt.json').read_text(encoding='utf-8'))
        self.assertIn(resolved, receipt['artifacts'])
        bound = receipt['artifacts'][resolved]
        if bound is not None:   # signed: the receipt's digest is the bound digest
            self.assertEqual(observed, bound if isinstance(bound, str) else bound.get('sha256'))

    def test_every_executed_module_and_script_is_in_the_receipt_artifact_set(self):
        closure = executed_closure()
        for required in ('joulewise/align/apple/prompt_cache.py', 'joulewise/align/apple/sampler.py',
                         'joulewise/align/apple/sampling.py', 'joulewise/align/apple/generation.py',
                         'joulewise/align/apple/budget.py', 'joulewise/align/apple/xml_tool_calls.py',
                         'joulewise/adapters/mlx_runtime.py', 'joulewise/external/km003c_parse.py',
                         'joulewise/external/km003c_usb.py',
                         # scripts launched as subprocesses / imported by the session (delta H01, L6)
                         'scripts/run_campaign.py', 'scripts/hazard_monitor.py', 'scripts/launch_window.py',
                         'scripts/km003c_monitor.py', 'scripts/bytes_h_session.py',
                         'scripts/align_w1_budget_procedure.py', 'scripts/align_v4_kit.py',
                         'scripts/night_chains/align_r1_rehearsal.zsh'):
            self.assertIn(required, closure)
        missing = sorted(closure - set(registration.ARTIFACTS))
        self.assertEqual(missing, [], 'add these to v4_registration.ARTIFACTS (and the receipt template)')

    def test_script_launch_edges_are_followed(self):
        # chain.py names scripts only as strings ("scripts/run_campaign.py"); no import edge exists.
        names, scripts = _edges('joulewise/b5/chain.py')
        self.assertIn('scripts/run_campaign.py', scripts)
        _names, driver_scripts = _edges('joulewise/b5/driver.py')
        self.assertTrue({'scripts/hazard_monitor.py', 'scripts/km003c_monitor.py'} <= driver_scripts)
        self.assertNotIn('scripts/run_night.py', _edges('joulewise/align/apple/endpoint.py')[1])    # docstring mention only

    def test_no_script_or_module_outside_the_two_tiers(self):
        for path in registration.ARTIFACTS:
            self.assertIsInstance(registration.is_strict(path), bool)
        self.assertTrue(all(registration.is_strict(p) for p in registration.STRICT_SCRIPTS))

    def test_artifact_set_has_no_duplicates_or_missing_files_and_matches_template(self):
        artifacts = registration.ARTIFACTS
        self.assertEqual(len(artifacts), len(set(artifacts)))
        pending = {p for p in artifacts if p.startswith(registration.REGISTRATION)}   # lead-supplied inputs
        self.assertEqual([p for p in artifacts if p not in pending and not (ROOT / p).is_file()], [])
        template = json.loads((ROOT / registration.REGISTRATION / 'registration_receipt.json').read_text())
        self.assertEqual(set(template['artifacts']), set(artifacts))


if __name__ == '__main__':
    unittest.main()
