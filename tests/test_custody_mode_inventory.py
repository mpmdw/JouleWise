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


def _keyword_modes(expression, scope, seen=frozenset()):
    """Find mode supplied through local **kwargs, dict copies, or updates."""
    if isinstance(expression, ast.Dict):
        for key, value in zip(expression.keys, expression.values):
            if key is None:
                yield from _keyword_modes(value, scope, seen)
            elif isinstance(key, ast.Constant) and key.value == "mode":
                yield value
    elif isinstance(expression, ast.IfExp):
        yield from _keyword_modes(expression.body, scope, seen)
        yield from _keyword_modes(expression.orelse, scope, seen)
    elif isinstance(expression, ast.Call) and _name(expression.func) == "dict":
        for arg in expression.args:
            yield from _keyword_modes(arg, scope, seen)
        for keyword in expression.keywords:
            if keyword.arg == "mode":
                yield keyword.value
            elif keyword.arg is None:
                yield from _keyword_modes(keyword.value, scope, seen)
    elif isinstance(expression, ast.Name) and expression.id not in seen:
        seen = seen | {expression.id}
        for node in _scope_nodes(scope):
            targets = (node.targets if isinstance(node, ast.Assign)
                       else [node.target] if isinstance(node, (ast.AnnAssign, ast.AugAssign))
                       else [])
            for target in targets:
                if isinstance(target, ast.Name) and target.id == expression.id:
                    yield from _keyword_modes(node.value, scope, seen)
                elif (isinstance(target, ast.Subscript)
                      and _name(target.value) == expression.id
                      and isinstance(target.slice, ast.Constant)
                      and target.slice.value == "mode"):
                    yield node.value
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and _name(node.func.value) == expression.id
                    and node.func.attr in {"update", "setdefault"}):
                if node.func.attr == "setdefault":
                    if (len(node.args) >= 2 and isinstance(node.args[0], ast.Constant)
                            and node.args[0].value == "mode"):
                        yield node.args[1]
                else:
                    for arg in node.args:
                        yield from _keyword_modes(arg, scope, seen)
                    for keyword in node.keywords:
                        if keyword.arg == "mode":
                            yield keyword.value
                        elif keyword.arg is None:
                            yield from _keyword_modes(keyword.value, scope, seen)


def inventory(source_overrides=None):
    """Return replay (file, qualified enclosing function) keys and violations."""
    overrides = source_overrides or {}
    replay = set()
    violations = []
    for directory in ("joulewise", "scripts"):
        for path in sorted((REPO_ROOT / directory).rglob("*.py")):
            relative = path.relative_to(REPO_ROOT).as_posix()
            tree = ast.parse(overrides.get(relative, path.read_text()), filename=relative)
            aliases = {
                alias.asname: alias.name
                for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
                for alias in node.names if alias.asname
            }

            def visit(node, names=(), scope=tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    names = (*names, node.name)
                    scope = node
                if isinstance(node, ast.Call):
                    called = _name(node.func)
                    if aliases.get(called, called) in CUSTODY_CALLS:
                        modes = []
                        for keyword in node.keywords:
                            if keyword.arg == "mode":
                                modes.append(keyword.value)
                            elif keyword.arg is None:
                                modes.extend(_keyword_modes(keyword.value, scope))
                        for mode in modes:
                            if isinstance(mode, ast.Constant) and mode.value == "issuing":
                                continue
                            if isinstance(mode, ast.Name) and mode.id == "mode":
                                continue
                            key = (relative, ".".join(names) or "<module>")
                            if isinstance(mode, ast.Constant) and mode.value == "read_replay":
                                replay.add(key)
                            else:
                                violations.append(f"{relative}:{node.lineno}: {ast.unparse(mode)}")
                for child in ast.iter_child_nodes(node):
                    visit(child, names, scope)

            visit(tree)
    return replay, violations


def allowed_replay():
    value = json.loads(ALLOWLIST.read_text())
    allowed = set()
    for file, functions in value.items():
        for function, reason in functions.items():
            if not isinstance(reason, str) or not reason.strip() or "\n" in reason:
                raise AssertionError(f"{file}:{function}: expected one-line replay reason")
            allowed.add((file, function))
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

        for function in (AuthenticatedConsumptionSession.__init__, bind_floor_artifact_evidence,
                         load_analysis_inputs, mint._authenticate_component,
                         mint.bind_floor_artifact_evidence, extract_cells):
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

    def test_inventory_rejects_unlisted_mint_snapshot_opt_in(self):
        path = "scripts/mint_floor_artifact.py"
        tree = ast.parse((REPO_ROOT / path).read_text())
        entry = next(node for node in tree.body
                     if isinstance(node, ast.FunctionDef) and node.name == "mint_floor_artifact")
        call = next(node for node in ast.walk(entry)
                    if isinstance(node, ast.Call) and _name(node.func) == "load_calibration_ledger_snapshot")
        call.keywords.append(ast.keyword(arg="mode", value=ast.Constant(value="read_replay")))
        actual, violations = inventory({path: ast.unparse(ast.fix_missing_locations(tree))})
        self.assertEqual(violations, [])
        self.assertEqual(actual - allowed_replay(), {(path, "mint_floor_artifact")})

    def test_inventory_checks_mode_in_keyword_dictionary(self):
        path = "scripts/mint_floor_artifact.py"
        source = '''def counterfeit():
    options = {"mode": "read_replay"}
    load_calibration_ledger_snapshot(**options)
'''
        actual, violations = inventory({path: source})
        self.assertEqual(violations, [])
        self.assertIn((path, "counterfeit"), actual - allowed_replay())
