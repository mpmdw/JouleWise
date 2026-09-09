"""Executable census of custody replay opt-ins, including keyword dictionaries."""

import ast
import inspect
import json
from pathlib import Path
import unittest
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST = REPO_ROOT / "tests/fixtures/custody_read_replay_allowlist.json"
CUSTODY_CALLS = frozenset({
    "load_calibration_ledger_snapshot", "probe_custody", "_custody_probe_paths",
    "_custody_state", "_custody_reasons", "AuthenticatedConsumptionSession",
    "bind_floor_artifact_evidence", "load_analysis_inputs", "extract_cells",
    "load_calibration_candidate", "_candidate_from_observation",
    "discover_calibration_candidates", "calibration_bracket_for_bundles",
})


def _name(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _scope_nodes(scope):
    """Do not attribute nested functions' assignments to their caller."""
    for child in ast.iter_child_nodes(scope):
        yield child
        if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            yield from _scope_nodes(child)


FORWARDED_MODE = object()
FUNCTIONS = (ast.FunctionDef, ast.AsyncFunctionDef)


def _parameters(scope):
    if not isinstance(scope, FUNCTIONS):
        return set()
    args = scope.args
    return {arg.arg for arg in (*args.posonlyargs, *args.args, *args.kwonlyargs)}


def _keyword_modes(expression, scope, seen=frozenset(), *, keywords=False,
                   class_scope=None):
    """Conservatively resolve local values; unknown keyword sources fail closed.

    This is a syntactic census, not Python execution. Factory results and
    forwarded **kwargs are unknown even when their runtime value is safe.
    Only an actual scalar parameter may be opaque caller-mode forwarding.
    """
    def resolve(value):
        return _keyword_modes(value, scope, seen, keywords=keywords,
                              class_scope=class_scope)

    if isinstance(expression, ast.IfExp):
        yield from resolve(expression.body)
        yield from resolve(expression.orelse)
    elif isinstance(expression, ast.Name) and expression.id not in seen:
        assigned = False
        next_seen = seen | {expression.id}
        for node in _scope_nodes(scope):
            targets = (node.targets if isinstance(node, ast.Assign)
                       else [node.target] if isinstance(node, (ast.AnnAssign, ast.AugAssign))
                       else [])
            for target in targets:
                if isinstance(target, ast.Name) and target.id == expression.id:
                    assigned = True
                    yield from _keyword_modes(node.value, scope, next_seen,
                                              keywords=keywords, class_scope=class_scope)
                elif (keywords and isinstance(target, ast.Subscript)
                      and _name(target.value) == expression.id
                      and isinstance(target.slice, ast.Constant)
                      and target.slice.value == "mode"):
                    yield from _keyword_modes(node.value, scope, next_seen,
                                              class_scope=class_scope)
            if (keywords and isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and _name(node.func.value) == expression.id
                    and node.func.attr in {"update", "setdefault"}):
                if node.func.attr == "setdefault":
                    if (len(node.args) >= 2 and isinstance(node.args[0], ast.Constant)
                            and node.args[0].value == "mode"):
                        yield from _keyword_modes(node.args[1], scope, next_seen,
                                                  class_scope=class_scope)
                else:
                    for arg in node.args:
                        yield from _keyword_modes(arg, scope, next_seen, keywords=True,
                                                  class_scope=class_scope)
                    for keyword in node.keywords:
                        if keyword.arg in {None, "mode"}:
                            yield from _keyword_modes(keyword.value, scope, next_seen,
                                keywords=keyword.arg is None, class_scope=class_scope)
        if not assigned:
            yield (FORWARDED_MODE if not keywords and expression.id in _parameters(scope)
                   else expression)
    elif keywords and isinstance(expression, ast.Dict):
        for key, value in zip(expression.keys, expression.values):
            if key is None or isinstance(key, ast.Constant) and key.value == "mode":
                yield from _keyword_modes(value, scope, seen, keywords=key is None,
                                          class_scope=class_scope)
            elif not isinstance(key, ast.Constant):
                yield expression  # A computed key might be "mode".
    elif keywords and isinstance(expression, ast.Call) and _name(expression.func) == "dict":
        for arg in expression.args:
            yield from resolve(arg)
        for keyword in expression.keywords:
            if keyword.arg in {None, "mode"}:
                yield from _keyword_modes(keyword.value, scope, seen,
                    keywords=keyword.arg is None, class_scope=class_scope)
    elif (not keywords and isinstance(expression, ast.Attribute)
          and _name(expression.value) == "self" and class_scope is not None):
        # Trace stored caller modes (e.g. session.__init__ -> session._prepare).
        found = False
        for method in class_scope.body:
            if not isinstance(method, FUNCTIONS):
                continue
            for node in _scope_nodes(method):
                targets = (node.targets if isinstance(node, ast.Assign)
                           else [node.target] if isinstance(node, ast.AnnAssign) else [])
                if any(ast.unparse(target) == ast.unparse(expression) for target in targets):
                    found = True
                    yield from _keyword_modes(node.value, method, seen)
        if not found:
            yield expression
    else:
        yield expression


def inventory(source_overrides=None):
    """Return replay (file, qualified function, replay-call ordinal) keys."""
    overrides = source_overrides or {}
    replay, violations = set(), []
    for directory in ("joulewise", "scripts"):
        for path in sorted((REPO_ROOT / directory).rglob("*.py")):
            relative = path.relative_to(REPO_ROOT).as_posix()
            tree = ast.parse(overrides.get(relative, path.read_text()), filename=relative)
            aliases = {
                alias.asname: alias.name
                for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
                for alias in node.names if alias.asname
            }
            definitions = {node.name: node for node in ast.walk(tree)
                           if isinstance(node, FUNCTIONS)}
            calls = set(CUSTODY_CALLS)
            # A local shared(mode) wrapper must also census its callers,
            # including positional replay arguments and **kwargs forwarding.
            while True:
                aliases_changed = False
                for assignment in ast.walk(tree):
                    targets = (assignment.targets if isinstance(assignment, ast.Assign)
                               else [assignment.target] if isinstance(assignment, ast.AnnAssign)
                               else [])
                    if not targets:
                        continue
                    value = _name(assignment.value)
                    resolved = aliases.get(value, value)
                    if resolved in calls:
                        for target in targets:
                            if isinstance(target, ast.Name) and aliases.get(target.id) not in calls:
                                aliases[target.id] = resolved
                                aliases_changed = True
                wrappers = {name for name, definition in definitions.items()
                            if ("mode" in _parameters(definition) or definition.args.kwarg)
                            and any(isinstance(node, ast.Call)
                                    and aliases.get(_name(node.func), _name(node.func)) in calls
                                    for node in _scope_nodes(definition))}
                if wrappers <= calls and not aliases_changed:
                    break
                calls.update(wrappers)

            replay_ordinals = {}

            def visit(node, names=(), scope=tree, class_scope=None):
                if isinstance(node, ast.ClassDef):
                    names = (*names, node.name)
                    class_scope = node
                elif isinstance(node, FUNCTIONS):
                    names = (*names, node.name)
                    scope = node
                if isinstance(node, ast.Call):
                    called = aliases.get(_name(node.func), _name(node.func))
                    if called in calls:
                        modes = []
                        definition = definitions.get(called)
                        if definition is not None:
                            positional = (*definition.args.posonlyargs, *definition.args.args)
                            for parameter, argument in zip(positional, node.args):
                                if parameter.arg == "mode":
                                    modes.extend(_keyword_modes(argument, scope,
                                                               class_scope=class_scope))
                        for keyword in node.keywords:
                            if keyword.arg in {"mode", None}:
                                modes.extend(_keyword_modes(keyword.value, scope,
                                    keywords=keyword.arg is None, class_scope=class_scope))
                        has_replay = False
                        for mode in modes:
                            if mode is FORWARDED_MODE:
                                continue
                            if isinstance(mode, ast.Constant) and mode.value == "issuing":
                                continue
                            if isinstance(mode, ast.Constant) and mode.value == "read_replay":
                                has_replay = True
                            else:
                                violations.append(f"{relative}:{node.lineno}: {ast.unparse(mode)}")
                        if has_replay:
                            function = ".".join(names) or "<module>"
                            ordinal = replay_ordinals.get(function, 0) + 1
                            replay_ordinals[function] = ordinal
                            replay.add((relative, function, ordinal))
                for child in ast.iter_child_nodes(node):
                    visit(child, names, scope, class_scope)

            visit(tree)
    return replay, violations


def allowed_replay():
    allowed = set()
    for row in json.loads(ALLOWLIST.read_text()):
        file, function, ordinal, line, reason = (
            row[key] for key in ("file", "function", "ordinal", "line", "reason")
        )
        if not isinstance(reason, str) or not reason.strip() or "\n" in reason:
            raise AssertionError(f"{file}:{function}:{line}: expected one-line replay reason")
        if not isinstance(line, int) or line < 1:
            raise AssertionError("expected positive call line")
        if not isinstance(ordinal, int) or ordinal < 1:
            raise AssertionError("expected positive replay-call ordinal")
        key = (file, function, ordinal)
        if key in allowed:
            raise AssertionError(f"duplicate replay call: {key}")
        allowed.add(key)
    return allowed


class CustodyModeInventoryTests(unittest.TestCase):
    def test_read_replay_inventory(self):
        actual, violations = inventory()
        self.assertEqual(violations, [])
        self.assertEqual(actual, allowed_replay())

    def test_shared_validators_default_to_issuing(self):
        from joulewise.whole_window import AuthenticatedConsumptionSession
        from joulewise.floor_extraction import extract_cells
        from joulewise.analysis_engine.inputs import bind_floor_artifact_evidence, load_analysis_inputs
        from scripts import mint_floor_artifact as mint
        from joulewise.calibration_bracketing import (load_calibration_candidate,
            _candidate_from_observation, discover_calibration_candidates, calibration_bracket_for_bundles)

        for function in (AuthenticatedConsumptionSession.__init__, bind_floor_artifact_evidence,
                         load_analysis_inputs, mint._authenticate_component,
                         mint.bind_floor_artifact_evidence, extract_cells, load_calibration_candidate,
                         _candidate_from_observation, discover_calibration_candidates,
                         calibration_bracket_for_bundles):
            with self.subTest(function=function.__qualname__):
                self.assertEqual(inspect.signature(function).parameters["mode"].default, "issuing")

    def test_extract_cells_forwards_caller_mode(self):
        from joulewise import floor_extraction

        class ReachedSession(Exception):
            pass

        for kwargs, expected in (({}, "issuing"), ({"mode": "issuing"}, "issuing"),
                                 ({"mode": "read_replay"}, "read_replay")):
            with (
                self.subTest(kwargs=kwargs),
                mock.patch.object(floor_extraction, "validate_extraction_spec", return_value=[]),
                mock.patch.object(floor_extraction, "campaign_cooldown_evidence", return_value={}),
                mock.patch.object(floor_extraction, "_spec_referenced_bundle_ids", return_value={"member"}),
                mock.patch.object(floor_extraction, "AuthenticatedConsumptionSession",
                                  side_effect=ReachedSession) as session,
            ):
                with self.assertRaises(ReachedSession):
                    floor_extraction.extract_cells(Path("/unused"), {"cells": [{}]}, **kwargs)
                self.assertEqual(session.call_args.kwargs["mode"], expected)

    def test_inventory_counterfactual_escapes(self):
        path = "scripts/mint_floor_artifact.py"
        cases = {
            "literal": 'load_calibration_ledger_snapshot(mode="read_replay")',
            "local_mode_literal": 'mode = "read_replay"; load_calibration_ledger_snapshot(mode=mode)',
            "assignment_alias": 'mode = "read_replay"; alias = mode; load_calibration_ledger_snapshot(mode=alias)',
            "callable_assignment_alias": 'alias = load_calibration_ledger_snapshot; alias(mode="read_replay")',
            "conditional": 'mode = "issuing" if flag else "read_replay"; load_calibration_ledger_snapshot(mode=mode)',
            "local_dict": 'options = {"mode": "read_replay"}; load_calibration_ledger_snapshot(**options)',
            "literal_kwargs": 'load_calibration_ledger_snapshot(**{"mode": "read_replay"})',
            "factory_kwargs": 'load_calibration_ledger_snapshot(**factory())',
            "forwarded_kwargs": 'load_calibration_ledger_snapshot(**kwargs)',
            "import_alias": 'from joulewise.calibration_ledger import load_calibration_ledger_snapshot as load; load(mode="read_replay")',
        }
        for name, body in cases.items():
            with self.subTest(escape=name):
                source = f"def counterfeit(**kwargs):\n    {body}\n"
                # Execute the counterfactual in memory too: every shape really
                # supplies replay, independent of how the scanner classifies it.
                probe = mock.Mock()
                namespace = {"load_calibration_ledger_snapshot": probe,
                             "factory": lambda: {"mode": "read_replay"}, "flag": False}
                exec(compile(source, "<custody-counterfactual>", "exec"), namespace)
                with mock.patch("joulewise.calibration_ledger.load_calibration_ledger_snapshot", probe):
                    namespace["counterfeit"](mode="read_replay")
                self.assertEqual(probe.call_args.kwargs["mode"], "read_replay")
                actual, violations = inventory({path: source})
                self.assertTrue(violations or actual - allowed_replay(), name)
                if name in {"factory_kwargs", "forwarded_kwargs"}:
                    self.assertTrue(violations, name)
                else:
                    self.assertIn((path, "counterfeit", 1), actual)

    def test_shared_parameter_replay_is_censused_at_issuing_caller(self):
        path = "scripts/mint_floor_artifact.py"
        for argument in ('"read_replay"', 'mode="read_replay"'):
            with self.subTest(argument=argument):
                actual, violations = inventory({path: f'''def shared(mode):
    load_calibration_ledger_snapshot(mode=mode)
def issuing_entry():
    shared({argument})
'''})
                self.assertEqual(violations, [])
                self.assertIn((path, "issuing_entry", 1), actual - allowed_replay())
                self.assertNotIn((path, "shared", 1), actual)

    def test_line_shift_does_not_require_allowlist_edit(self):
        path = "joulewise/analysis_engine/__init__.py"
        source = (REPO_ROOT / path).read_text()
        actual, violations = inventory({path: "# Unrelated comment above listed calls.\n" + source})
        self.assertEqual(violations, [])
        self.assertEqual(actual, allowed_replay())

    def test_second_call_requires_its_own_allowlist_row(self):
        path = "joulewise/analysis_engine/__init__.py"
        source = (REPO_ROOT / path).read_text()
        tree = ast.parse(source)
        entry = next(node for node in tree.body
                     if isinstance(node, ast.FunctionDef) and node.name == "analyze_claims")
        # Append within the function, preserving every existing call line.
        lines = source.splitlines(keepends=True)
        lines.insert(entry.end_lineno, '    load_calibration_ledger_snapshot(mode="read_replay")\n')
        actual, violations = inventory({path: "".join(lines)})
        self.assertEqual(violations, [])
        self.assertEqual(actual - allowed_replay(), {(path, "analyze_claims", 2)})
