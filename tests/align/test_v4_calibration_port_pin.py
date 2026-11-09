"""Merge-order guard (docs/analysis/v4/MERGE-ORDER.md): the engine's calibration
predicate must stay a byte-identical port of align/2026-11-08-v4-r11 @ bbfccb70a.

`audit` starts from the pinned functions and follows every module-scope name
they read: other functions, constants, imports and shadowed builtins. Each name
it reaches must have exactly ONE module-level binding. That binding statement is
pinned by sha256 of its full lines, including decorators and any other
statement sharing those lines.

The audit also refuses these drift paths:
- a second binding of a reached name, whether assignment, augassign, mutation
  through subscript or attribute, `del`, import or rebinding def;
- a `global` or `nonlocal` declaration of a reached name;
- `globals()`/`vars()` keyed by a reached name;
- `setattr`/`delattr` with a reached name;
- `exec`/`eval`/`compile` at module level.

Any change fails the test and forces a re-port. Everything else in
v4_cadence.py and the v4 arm stack is r11-owned, and r11 wins on merge.
"""
import ast
import builtins
import hashlib
from pathlib import Path
import symtable
import unittest

ROOT = Path(__file__).resolve().parents[2]
R11_COMMIT = 'bbfccb70ab993c395f254058694906610547651d'
CADENCE, KIT = 'joulewise/align/apple/v4_cadence.py', 'scripts/align_v4_kit.py'
PINNED_FUNCTIONS = {CADENCE: ('calibration_stop',), KIT: ('valid_lead_signature',)}
SCOPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef,
          ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)
DYNAMIC = {'exec', 'eval', 'compile'}
NAME_KEYED = {'setattr', 'delattr'}


def _segment(lines, node):
    start = min([node.lineno, *(d.lineno for d in getattr(node, 'decorator_list', ()))])
    return ''.join(lines[start-1:node.end_lineno])


def _def_time_nodes(stmt):
    """Expressions a def/class statement evaluates in module scope."""
    nodes = list(getattr(stmt, 'decorator_list', ()))
    if isinstance(stmt, ast.ClassDef):
        nodes += [*stmt.bases, *(k.value for k in stmt.keywords)]
    elif isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
        nodes += [*stmt.args.defaults, *(d for d in stmt.args.kw_defaults if d is not None)]
    return nodes


def _module_bindings(stmt):
    """Names a top-level statement binds, mutates or deletes in module scope."""
    names = set()
    if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        names.add(stmt.name)
        stack = _def_time_nodes(stmt)
    else:
        stack = [stmt]
    while stack:
        node = stack.pop()
        if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            names.add(node.id)
        elif isinstance(node, (ast.Subscript, ast.Attribute)) and isinstance(node.ctx, (ast.Store, ast.Del)):
            base = node.value
            while isinstance(base, (ast.Subscript, ast.Attribute)):
                base = base.value
            if isinstance(base, ast.Name):
                names.add(base.id)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            names.update((a.asname or a.name).split('.')[0] for a in node.names if a.name != '*')
        elif isinstance(node, ast.NamedExpr) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node is not stmt:
            names.add(node.name)
            stack.extend(_def_time_nodes(node))
            continue
        if isinstance(node, SCOPES) and node is not stmt:
            continue
        stack.extend(ast.iter_child_nodes(node))
    return names


def _function_reads(source, stmt):
    """Module-scope names a function reads at call time (all nested scopes) or def time."""
    found = set()
    def visit(table, top):
        for symbol in table.get_symbols():
            if symbol.is_referenced() and (symbol.is_global() or (top and symbol.is_free())):
                found.add(symbol.get_name())
        for child in table.get_children():
            visit(child, False)
    module = symtable.symtable(source, '<pinned>', 'exec')
    visit(next(t for t in module.get_children() if t.get_name() == stmt.name and t.get_lineno() == stmt.lineno), True)
    for node in _def_time_nodes(stmt):
        found.update(n.id for n in ast.walk(node) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load))
    return found


def _dynamic_rebinding(tree, reached):
    for node in ast.walk(tree):
        if isinstance(node, (ast.Global, ast.Nonlocal)) and reached & set(node.names):
            return f'global/nonlocal declaration of {sorted(reached & set(node.names))}'
        if (isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant)
                and node.slice.value in reached and isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Name) and node.value.func.id in ('globals', 'vars', 'locals')):
            return f'namespace access keyed by {node.slice.value!r}'
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in NAME_KEYED and any(
                    isinstance(a, ast.Constant) and a.value in reached for a in node.args):
                return f'{node.func.id} of a pinned name'
    for stmt in tree.body:                      # dynamic code at module level
        for node in ast.walk(stmt):
            if isinstance(node, SCOPES):
                break
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in DYNAMIC:
                return f'module-level {node.func.id}'
    return None


def audit(source, functions):
    """Return {reached name: sha256 of its single binding statement}; raise on any drift path."""
    lines = source.splitlines(keepends=True)
    tree = ast.parse(source)
    binders = {}
    for stmt in tree.body:
        for name in _module_bindings(stmt):
            binders.setdefault(name, []).append(stmt)
    reached, frontier = set(), list(functions)
    while frontier:
        name = frontier.pop()
        if name in reached:
            continue
        reached.add(name)
        stmts = binders.get(name, [])
        if len(stmts) != 1:
            raise AssertionError(f'{name} must have exactly one module-level binding, found {len(stmts)}')
        stmt = stmts[0]
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)) and stmt.name == name:
            reads = _function_reads(source, stmt)
        else:
            reads = {n.id for n in ast.walk(stmt) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
        for read in reads:
            if read in binders:
                frontier.append(read)       # includes any shadowed builtin
            elif not hasattr(builtins, read):
                raise AssertionError(f'{name} reads unbound module name {read}')
    problem = _dynamic_rebinding(tree, reached)
    if problem:
        raise AssertionError(problem)
    return {n: hashlib.sha256(_segment(lines, binders[n][0]).encode()).hexdigest() for n in sorted(reached)}


# sha256 of each reached name's binding statement, computed with audit() on the
# files at r11 bbfccb70a (cadence sha256 722323250a77..., kit at the same commit).
PINS = {CADENCE: {
    'BENIGN_PER_PAIR_PER_WINDOW': '126fb412bdb38043bbd064cfc802e9c4b9266bdd0b5da5a27db22a70e683ca3d',
    'CAL_PAIRS': 'cf87368714b7e4d36da2ee4f205cb98ad621745d1657e5ca51317b54150db828',
    'CAL_TARGET_PER_PAIR': 'd41349291dbb0bd77dd52b832d880ecb22f4085004fbd73305211ee585c77e58',
    'CAL_WINDOWS': '3af6dc1464162716638eeeb4abf29d6d19edb9e4d0ffb5f7f62ce46faa004c3a',
    'CAPTURED_MAX': '6ae0e3f36b48153f92289b7ef850201b5f7e5e74bd7353ddb7576cc61fbf4bea',
    'REPLACEMENT_WINDOWS': 'f725b7843c12aa773a6f0b2ba6bb501e97422a200f1d22bd7a3ff4a978e5a8e1',
    'RULING_RESETS': '06d3137b0b8a4d5eb64d73e6d6eb4983ea02058fe3ea9b3b20f5d29e89bc7631',
    'STRUCTURAL_BARS': 'b26405ef9ac1c52882f8d1183d01eed0d85f7d52a12ad19547f7f713a05ccec3',
    'WINDOW_MEMBERS': '0f4b3867965cc483e5e2640b25b65469ebac3c8b1e8249d23c35da6398260830',
    'ZERO_CAPTURE_BAR': '402165e199fb9de188290c880b6223f903782d9bd5df7f5a253b6bec1e181d51',
    '_is_digest': '511404874dfab20a0df2d76f7c1ca5639a360ce8f8339d4476d74b134a2f0e2f',
    '_validated_rulings': 'c7f9aba6169f9565f1985a8804691c9befdbfa88c42c81bf7f67ea49820f205a',
    'calibration_stop': '49de90d88fb46d220359d16ed2216888f110d3a2b02726da8c0bcd0f67abcdf0',
    're': 'a830333312c4c9c2233bb02762bd498203b1c3bf0527614735693b4b79f6d167',
    'slot_of': '0387a14150850dc45244927465fdac8d65794867a34e6f78b643737c17c9f2f8',
}, KIT: {
    'UNSIGNED': '0b47b17e27658c3fa412a1e4c264882548649a2045313fceeabae9ed30a4793a',
    'valid_lead_signature': '8f02eba8fe0d87abe462f2b06f4dc3fb859769270dfb3c5c00f0e335188541f4',
}}


class CalibrationPortPinTests(unittest.TestCase):
    def test_pinned_statements_equal_r11_bbfccb70a(self):
        for path, functions in PINNED_FUNCTIONS.items():
            with self.subTest(path=path):
                self.assertEqual(audit((ROOT/path).read_text(), functions), PINS[path],
                                 f'{path} drifted from r11 {R11_COMMIT}; re-port it')

    def test_engine_uses_this_predicate(self):
        from joulewise.align.apple import v4_cadence
        from joulewise.align.v4_analysis import engine
        self.assertIs(engine.calibration_stop, v4_cadence.calibration_stop)
        self.assertIs(engine.slot_of, v4_cadence.slot_of)
        self.assertIs(engine.STRUCTURAL_BARS, v4_cadence.STRUCTURAL_BARS)

    def test_mutations_fail_the_audit(self):
        source = (ROOT/CADENCE).read_text()
        stop = 'def calibration_stop(windows, lead_rulings=()):'
        for needle in (stop, 'CAL_TARGET_PER_PAIR = 39\n', 'CAL_WINDOWS = 8\n', 'import re\n'):
            self.assertEqual(source.count(needle), 1, needle)
        mutations = {
            'decorator added': source.replace(stop, '@staticmethod\n'+stop),
            'augmented constant': source.replace('CAL_TARGET_PER_PAIR = 39\n',
                                                 'CAL_TARGET_PER_PAIR = 39\nCAL_TARGET_PER_PAIR += 1\n'),
            'appended augassign': source+'\nCAL_WINDOWS += 1\n',
            'wrapped function': source+'\ncalibration_stop = wrapper(calibration_stop)\n',
            'helper rebinding': source+'\ndef slot_of(window_id):\n    return window_id\n',
            'global rebinding': source+'\ndef _late():\n    global CAL_WINDOWS\n    CAL_WINDOWS = 9\n',
            'globals() rebinding': source+"\nglobals()['CAL_WINDOWS'] = 9\n",
            'setattr rebinding': source+"\nimport sys\nsetattr(sys.modules[__name__], 'CAL_WINDOWS', 9)\n",
            'builtin shadowed': source+'\nlen = lambda value: 0\n',
            'helper import alias': source.replace('import re\n', 'import re\nimport json as re\n'),
            'same-line augassign': source.replace('CAL_WINDOWS = 8\n', 'CAL_WINDOWS = 8; CAL_WINDOWS += 1\n'),
            'deleted constant': source+'\ndel CAL_WINDOWS\n',
            'value changed': source.replace('CAL_TARGET_PER_PAIR = 39', 'CAL_TARGET_PER_PAIR = 38'),
            'module exec': source+"\nexec('CAL_WINDOWS = 9')\n",
        }
        for label, mutated in mutations.items():
            with self.subTest(mutation=label):
                self.assertNotEqual(mutated, source)
                try:
                    result = audit(mutated, PINNED_FUNCTIONS[CADENCE])
                except AssertionError:
                    continue
                self.assertNotEqual(result, PINS[CADENCE], 'mutation passed the audit')


if __name__ == '__main__':
    unittest.main()
