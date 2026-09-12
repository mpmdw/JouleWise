"""Repository-wide guard for disposable Git fixture hygiene."""

from __future__ import annotations

import ast
import shlex
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.git_fixture import GIT_MAINTENANCE_CONTROLS, init_git_fixture


TESTS_ROOT = Path(__file__).resolve().parent
GIT_INIT_SUBCOMMAND = "init"
EXPECTED_MAINTENANCE_CONTROLS = (
    ("maintenance.auto", "false"),
    ("gc.auto", "0"),
    ("maintenance.autoDetach", "false"),
    ("gc.autoDetach", "false"),
)
ESTABLISHED_LOCAL_HELPERS = {
    "tests/git_fixture.py": {"init_git_fixture"},
    "tests/test_calibration_exits.py": {
        "CalibrationExitReliabilityTests._configure_fixture_repo",
        "PublicGovernedExitWitnessTests.setUp",
    },
    "tests/test_identity_pins.py": {"init_git"},
}
# GIT-FIXTURE-MAINTENANCE-SWEEP-01 fence, authority:
# docs/process_traces/2026-08-26-t26-ci-reliability/README.md,
# "What this cure does NOT cover, and the row that would".
# Both deliberately override maintenance after using _configure_fixture_repo.
# Keep the exception at named scopes, never at file level.
MAINTENANCE_ON_EXCEPTIONS = {
    "tests/test_calibration_exits.py": {
        "CalibrationExitReliabilityTests.test_minimal_git_create_commit_cleanup_cycles_are_bounded",
        "CalibrationExitReliabilityTests.test_forced_auto_maintenance_mutation_reproduces_cleanup_race",
    },
}


def _string_literals(node: ast.AST) -> tuple[str, ...]:
    return tuple(
        child.value
        for child in ast.walk(node)
        if isinstance(child, ast.Constant) and isinstance(child.value, str)
    )


def _scope_name(node: ast.AST, parents: dict[ast.AST, ast.AST]) -> str:
    names: list[str] = []
    current: ast.AST | None = node
    while current is not None:
        if isinstance(current, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            names.append(current.name)
        current = parents.get(current)
    return ".".join(reversed(names))


def _uses_local_hygiene(function: ast.AST) -> bool:
    return any(
        isinstance(node, ast.For)
        and isinstance(node.iter, ast.Name)
        and node.iter.id == "GIT_MAINTENANCE_CONTROLS"
        and "config" in _string_literals(node)
        and "--local" in _string_literals(node)
        for node in ast.walk(function)
    )


def _constant_command_value(node: ast.AST) -> str | list[str] | tuple[str, ...] | None:
    """Fold only literal strings and their argv containers, never source calls."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, (ast.List, ast.Tuple)):
        values = [_constant_command_value(element) for element in node.elts]
        if all(isinstance(value, str) for value in values):
            return values if isinstance(node, ast.List) else tuple(values)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = _constant_command_value(node.left)
        right = _constant_command_value(node.right)
        if isinstance(left, (str, list, tuple)) and type(left) is type(right):
            return left + right
    return None


class _CommandLiterals:
    """Resolve literal argv aliases without importing or executing test modules.

    All assignments in the nearest lexical scope contribute, so conditional
    unsafe commands cannot hide behind a safe assignment. Cycles terminate.
    """

    def __init__(self, tree: ast.AST, parents: dict[ast.AST, ast.AST]) -> None:
        self.parents = parents
        self.bindings: dict[tuple[ast.AST, str], list[ast.AST]] = {}
        self.cache: dict[tuple[ast.AST, frozenset[str]], tuple[str, ...]] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                targets = node.targets
            elif isinstance(node, ast.AnnAssign):
                targets = [node.target]
            else:
                continue
            scope = next(self._scopes(node))
            for target in targets:
                if isinstance(target, ast.Name) and node.value is not None:
                    self.bindings.setdefault((scope, target.id), []).append(node.value)

    def _scopes(self, node: ast.AST):
        return (
            scope for scope in _ancestors(node, self.parents)
            if isinstance(scope, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
        )

    def __call__(self, node: ast.AST, seen: frozenset[str] = frozenset()) -> tuple[str, ...]:
        cache_key = (node, seen)
        if cache_key in self.cache:
            return self.cache[cache_key]
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            result = (node.value,)
        elif (
            isinstance(node, ast.BinOp)
            and isinstance(node.op, ast.Add)
            and (folded := _constant_command_value(node)) is not None
        ):
            result = (folded,) if isinstance(folded, str) else tuple(folded)
        elif isinstance(node, ast.JoinedStr):
            result = ("".join(
                part.value if isinstance(part, ast.Constant) else "DYNAMIC"
                for part in node.values
            ),)
        elif isinstance(node, ast.Name):
            values = ()
            if node.id not in seen:
                for scope in self._scopes(node):
                    if values := self.bindings.get((scope, node.id), ()):
                        break
            result = tuple(value for item in values for value in self(item, seen | {node.id}))
        else:
            # Function names are not argv. Only inspect arguments of nested calls.
            children = node.args if isinstance(node, ast.Call) else ast.iter_child_nodes(node)
            result = tuple(value for child in children for value in self(child, seen))
        self.cache[cache_key] = result
        return result


def _shell_git_init(value: str) -> bool:
    try:
        lexer = shlex.shlex(value, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        tokens = list(lexer)
    except ValueError:
        return False
    for index, token in enumerate(tokens):
        if Path(token).name == "git" and "init" in tokens[index + 1:]:
            return True
    return False


def _direct_git_init_lines(
    path: Path, repo_relative_path: str
) -> tuple[int, ...]:
    """Return direct Git initialization sites that bypass the shared helper."""

    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    parents = {
        child: parent
        for parent in ast.walk(tree)
        for child in ast.iter_child_nodes(parent)
    }
    command_literals = _CommandLiterals(tree, parents)
    direct_calls: list[ast.Call] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        literals = tuple(
            value
            for argument in [*node.args, *(keyword.value for keyword in node.keywords)]
            for value in command_literals(argument)
        )
        # Bare init arguments include wrappers that prepend git internally;
        # shell strings and assigned argv must not bypass the census either.
        if GIT_INIT_SUBCOMMAND in literals or any(_shell_git_init(value) for value in literals):
            direct_calls.append(node)
    call_counts: dict[str, int] = {}
    for node in direct_calls:
        scope = _scope_name(node, parents)
        if scope in MAINTENANCE_ON_EXCEPTIONS.get(repo_relative_path, set()):
            continue
        call_counts[scope] = call_counts.get(scope, 0) + 1

    lines: set[int] = set()
    for node in direct_calls:
        scope = _scope_name(node, parents)
        if scope in MAINTENANCE_ON_EXCEPTIONS.get(repo_relative_path, set()):
            continue
        function = next(
            (
                parent
                for parent in _ancestors(node, parents)
                if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef))
            ),
            None,
        )
        if (
            scope in ESTABLISHED_LOCAL_HELPERS.get(repo_relative_path, set())
            and call_counts[scope] == 1
            and function is not None
            and _uses_local_hygiene(function)
            and _maintenance_controls(path) == EXPECTED_MAINTENANCE_CONTROLS
        ):
            continue
        lines.add(node.lineno)
    for node in ast.walk(tree):
        if isinstance(node, (ast.List, ast.Tuple)):
            literals = _string_literals(node)
            if literals[:1] == (GIT_INIT_SUBCOMMAND,):
                if _scope_name(node, parents) not in MAINTENANCE_ON_EXCEPTIONS.get(repo_relative_path, set()):
                    lines.add(node.lineno)
    return tuple(sorted(lines))


def _ancestors(
    node: ast.AST, parents: dict[ast.AST, ast.AST]
) -> tuple[ast.AST, ...]:
    ancestors: list[ast.AST] = []
    current = parents.get(node)
    while current is not None:
        ancestors.append(current)
        current = parents.get(current)
    return tuple(ancestors)


def _maintenance_controls(path: Path) -> tuple[tuple[str, str], ...] | None:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if (
            isinstance(node, ast.ImportFrom)
            and node.module == "tests.git_fixture"
            and any(
                alias.name == "GIT_MAINTENANCE_CONTROLS" and alias.asname is None
                for alias in node.names
            )
        ):
            return _maintenance_controls(TESTS_ROOT / "git_fixture.py")
        if not isinstance(node, ast.Assign):
            continue
        if any(
            isinstance(target, ast.Name) and target.id == "GIT_MAINTENANCE_CONTROLS"
            for target in node.targets
        ):
            return ast.literal_eval(node.value)
    return None


def _git_init_violations(tests_root: Path) -> dict[str, tuple[int, ...]]:
    violations: dict[str, tuple[int, ...]] = {}
    for path in sorted(tests_root.rglob("*.py")):
        tests_relative_path = path.relative_to(tests_root).as_posix()
        repo_relative_path = f"tests/{tests_relative_path}"
        if lines := _direct_git_init_lines(path, repo_relative_path):
            violations[tests_relative_path] = lines
    return violations


class GitFixtureMaintenanceTests(unittest.TestCase):
    def test_shared_helper_installs_the_exact_four_key_tuple(self) -> None:
        self.assertEqual(GIT_MAINTENANCE_CONTROLS, EXPECTED_MAINTENANCE_CONTROLS)
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary) / "repository"
            repository.mkdir()
            init_git_fixture(repository, "-q")
            observed = tuple(
                (
                    key,
                    subprocess.run(
                        ("git", "-C", str(repository), "config", "--local", "--get", key),
                        check=True,
                        capture_output=True,
                        text=True,
                    ).stdout.strip(),
                )
                for key, _value in EXPECTED_MAINTENANCE_CONTROLS
            )
        self.assertEqual(observed, EXPECTED_MAINTENANCE_CONTROLS)

    def test_every_test_module_routes_git_initialization_through_shared_helper(self) -> None:
        self.assertEqual(_git_init_violations(TESTS_ROOT), {})

    def test_guard_flags_direct_init_in_nested_support_module(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            tests_root = Path(temporary) / "tests"
            support_module = tests_root / "support" / "fixture_factory.py"
            support_module.parent.mkdir(parents=True)
            support_module.write_text(
                "import subprocess\n"
                "subprocess.run(('git', 'init'), check=True)\n",
                encoding="utf-8",
            )
            violations = _git_init_violations(tests_root)

        self.assertEqual(violations, {"support/fixture_factory.py": (2,)})

    def test_nested_git_fixture_does_not_inherit_top_level_exemption(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            tests_root = Path(temporary) / "tests"
            support_module = tests_root / "support" / "git_fixture.py"
            support_module.parent.mkdir(parents=True)
            support_module.write_text(
                "import subprocess\n"
                "GIT_MAINTENANCE_CONTROLS = ()\n"
                "def init_git_fixture(repository):\n"
                "    subprocess.run(('git', 'init'), check=True)\n"
                "    for key, value in GIT_MAINTENANCE_CONTROLS:\n"
                "        subprocess.run(('git', 'config', '--local', key, value), check=True)\n",
                encoding="utf-8",
            )
            violations = _git_init_violations(tests_root)

        self.assertEqual(violations, {"support/git_fixture.py": (4,)})

    def test_established_local_helpers_retain_the_exact_tuple(self) -> None:
        observed = {
            name: _maintenance_controls(TESTS_ROOT.parent / name)
            for name in ESTABLISHED_LOCAL_HELPERS
        }
        self.assertEqual(
            observed,
            {name: EXPECTED_MAINTENANCE_CONTROLS for name in ESTABLISHED_LOCAL_HELPERS},
        )


if __name__ == "__main__":
    unittest.main()
