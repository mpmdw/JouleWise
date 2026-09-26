"""The consumer guard of consumer-drift final texts v1.1 §3.10.

A window's battery verdict reaches a consumer through ONE function,
`battery_float.authenticate_committed_verdict`, which replays the custody
bytes, loads the committed record and requires the two to agree.  Every
earlier drift between the desk dry run and the issuer came from a consumer
calling the pieces itself and skipping one.  This test walks every tracked
`*.py` under `joulewise/` and `scripts/` (plus the one test fixture that
writes records) and fails on any reference to a piece outside the seven
allowlisted functions below, including the producer (`verdict_record`) and
the parser (`parse`).
"""

from __future__ import annotations

import ast
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE = "joulewise.battery_float"
GUARDED = frozenset({"load_committed_verdict", "validate_window", "compare_verdict",
                     "verdict_record", "parse"})
FACTORIES = frozenset({"unobserved_historical_verdict", "not_applicable_verdict"})
FACTORY_ALLOWLIST = {"joulewise/bundle_read.py": "text 8 reader states"}
# file::function -> the guarded names it may reference; exactly seven rows.
ALLOWLIST = {
    ("joulewise/battery_float.py", "authenticate_committed_verdict"):
        frozenset({"validate_window", "load_committed_verdict", "compare_verdict"}),
    ("joulewise/battery_float.py", "verdict_record"): frozenset({"validate_window"}),
    ("joulewise/battery_float.py", "observe"): frozenset({"parse"}),
    ("joulewise/battery_float.py", "validate_window"): frozenset({"parse"}),
    ("joulewise/battery_float.py", "authenticate_pair"): frozenset({"parse"}),
    ("scripts/issue_calibration_acceptance_generation.py", "_battery_verdict"):
        frozenset({"verdict_record"}),
    ("tests/fixtures/epoch_bootstrap/build.py", "write_verdict_record"): frozenset({"verdict_record"}),
}
# The only test file the production guard walks.
GUARDED_TEST_FILES = ("tests/fixtures/epoch_bootstrap/build.py",)
# Test files that may use a primitive directly (§3.10, last sentence).
PRIMITIVE_TEST_FILES = frozenset({
    "tests/test_battery_float.py", "tests/battery_float_fixture.py",
    "tests/fixtures/epoch_bootstrap/build.py",
    "tests/test_validate_powermetrics_fiducial_derivation_only.py",
    "tests/test_battery_float_consumers.py",
})


def _docstring_nodes(tree: ast.AST) -> set[int]:
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = node.body
            if (body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                found.add(id(body[0].value))
    return found


def _absolute_module(relative: str, node: ast.ImportFrom) -> str | None:
    """The absolute module an ``ImportFrom`` names, resolving ``from . import x``.

    A relative import in ``joulewise/night_gate.py`` (``from . import
    battery_float``) names the same module as the absolute form; the guard must
    see both (final delta, Astra R1).
    """
    if not node.level:
        return node.module
    package = relative[:-3].split("/")[:-1]          # "joulewise/x.py" -> ["joulewise"]
    if node.level - 1 > len(package):
        return None
    base = package[: len(package) - (node.level - 1)]
    return ".".join(base + ([node.module] if node.module else [])) or None


class _Checker(ast.NodeVisitor):
    def __init__(self, relative: str, tree: ast.AST, source: str) -> None:
        self.relative = relative
        self.in_module = relative == "joulewise/battery_float.py"
        # A string can reach a primitive only through a reference to the
        # module (``getattr``, ``importlib``), so rule (4) binds in files that
        # name ``battery_float`` at all; elsewhere "parse" is an error label.
        self.strings_bind = self.in_module or "battery_float" in source
        self.docstrings = _docstring_nodes(tree)
        self.module_aliases: set[str] = set()      # names bound to joulewise.battery_float
        self.package_aliases: set[str] = set()     # `import joulewise.battery_float` binds `joulewise`
        self.bound: dict[str, str] = {}            # local name -> guarded name it was imported as
        self.pair_constructors: set[str] = set()
        self.factory_names: set[str] = set()
        self.dataclass_modules: set[str] = set()
        self.dataclass_replaces: set[str] = set()
        self.allowed_type_loads: set[int] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ("isinstance", "issubclass") and len(node.args) >= 2:
                self.allowed_type_loads.update(id(part) for part in ast.walk(node.args[1]))
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                annotations = [node.returns, *(arg.annotation for arg in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs))]
                self.allowed_type_loads.update(id(part) for annotation in annotations if annotation for part in ast.walk(annotation))
            if isinstance(node, ast.AnnAssign):
                self.allowed_type_loads.update(id(part) for part in ast.walk(node.annotation))
        self.functions: list[str] = []
        self.found: list[tuple[str, int, str]] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "dataclasses":
                        self.dataclass_modules.add(alias.asname or "dataclasses")
                    if alias.name == MODULE:
                        if alias.asname:
                            self.module_aliases.add(alias.asname)
                        else:
                            self.package_aliases.add("joulewise")
            elif isinstance(node, ast.ImportFrom):
                module = _absolute_module(relative, node)
                if module == "joulewise":
                    for alias in node.names:
                        if alias.name == "battery_float":
                            self.module_aliases.add(alias.asname or alias.name)
                elif module == MODULE:
                    for alias in node.names:
                        if alias.name in GUARDED:
                            self.bound[alias.asname or alias.name] = alias.name
                        if alias.name == "PairVerdict":
                            self.pair_constructors.add(alias.asname or alias.name)
                        if alias.name in FACTORIES:
                            self.factory_names.add(alias.asname or alias.name)
                elif module == "dataclasses":
                    for alias in node.names:
                        if alias.name == "replace":
                            self.dataclass_replaces.add(alias.asname or alias.name)
        self.imports_battery_float = bool(self.module_aliases or self.package_aliases or self.pair_constructors or self.bound or self.factory_names)

    def _flag(self, node: ast.AST, name: str) -> None:
        function = self.functions[-1] if self.functions else None
        if name in ALLOWLIST.get((self.relative, function), frozenset()):
            return
        self.found.append((self.relative, node.lineno, name))

    def _resolves_to_module(self, value: ast.AST) -> bool:
        if isinstance(value, ast.Name):
            return value.id in self.module_aliases
        return (isinstance(value, ast.Attribute) and value.attr == "battery_float"
                and isinstance(value.value, ast.Name) and value.value.id in self.package_aliases)

    def visit_FunctionDef(self, node: ast.AST) -> None:
        self.functions.append(node.name)
        self.generic_visit(node)
        self.functions.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if _absolute_module(self.relative, node) == MODULE:
            for alias in node.names:
                if alias.name in GUARDED:
                    self.found.append((self.relative, node.lineno, alias.name))

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr in GUARDED and self._resolves_to_module(node.value):
            self._flag(node, node.attr)
        if (not self.in_module and node.attr == "PairVerdict"
                and self._resolves_to_module(node.value) and id(node) not in self.allowed_type_loads):
            self._flag(node, "PairVerdict")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        callee = node.func
        if not self.in_module:
            if (isinstance(callee, ast.Name) and callee.id in self.factory_names
                    or isinstance(callee, ast.Attribute) and callee.attr in FACTORIES
                    and self._resolves_to_module(callee.value)):
                if self.relative not in FACTORY_ALLOWLIST:
                    self._flag(node, callee.id if isinstance(callee, ast.Name) else callee.attr)
            if self.imports_battery_float and (
                isinstance(callee, ast.Name) and callee.id in self.dataclass_replaces
                or isinstance(callee, ast.Attribute) and callee.attr == "replace"
                and isinstance(callee.value, ast.Name) and callee.value.id in self.dataclass_modules
            ):
                self._flag(node, "dataclasses.replace")
            if self.imports_battery_float and isinstance(callee, ast.Call) and isinstance(callee.func, ast.Name) and callee.func.id == "type":
                self._flag(node, "type(...)(...)")
            if (isinstance(callee, ast.Name) and callee.id == "getattr" and len(node.args) >= 2
                    and self._resolves_to_module(node.args[0]) and isinstance(node.args[1], ast.Constant)
                    and isinstance(node.args[1].value, str)):
                self._flag(node, "getattr(battery_float, ...)")
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if not self.in_module and node.id in self.pair_constructors and isinstance(node.ctx, ast.Load) and id(node) not in self.allowed_type_loads:
            self._flag(node, "PairVerdict")
        if node.id in self.bound:
            self._flag(node, self.bound[node.id])
        elif self.in_module and node.id in GUARDED:
            self._flag(node, node.id)

    def visit_Constant(self, node: ast.Constant) -> None:
        if self.strings_bind and node.value in GUARDED and id(node) not in self.docstrings:
            self._flag(node, node.value)


def violations(relative: str, source: str) -> list[tuple[str, int, str]]:
    tree = ast.parse(source, filename=relative)
    checker = _Checker(relative, tree, source)
    checker.visit(tree)
    return sorted(checker.found)


def tree_violations(root: Path) -> list[tuple[str, int, str]]:
    found = []
    paths = [path for directory in ("joulewise", "scripts") for path in (root / directory).rglob("*.py")]
    paths += [root / name for name in GUARDED_TEST_FILES if (root / name).exists()]
    for path in sorted(paths):
        relative = path.relative_to(root).as_posix()
        found.extend(violations(relative, path.read_text(encoding="utf-8", errors="replace")))
    return sorted(found)


def _tracked(root: Path, relative: str) -> bool:
    return subprocess.run(("git", "-C", str(root), "ls-files", "--error-unmatch", relative),
                          capture_output=True, check=False).returncode == 0


class ConsumerGuardTests(unittest.TestCase):
    def test_no_consumer_references_a_verdict_primitive(self) -> None:
        found = [row for row in tree_violations(ROOT) if _tracked(ROOT, row[0])]
        self.assertEqual(found, [])

    def test_the_seam_calls_each_of_its_three_primitives(self) -> None:
        tree = ast.parse((ROOT / "joulewise/battery_float.py").read_text(encoding="utf-8"))
        [seam] = [node for node in tree.body if isinstance(node, ast.FunctionDef)
                  and node.name == "authenticate_committed_verdict"]
        called = {node.func.id for node in ast.walk(seam)
                  if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
        self.assertLessEqual({"validate_window", "load_committed_verdict", "compare_verdict"}, called)

    def test_the_allowlist_has_exactly_seven_rows(self) -> None:
        self.assertEqual(len(ALLOWLIST), 7)

    def test_new_parse_reference_outside_pair_seam_is_flagged(self) -> None:
        source = "def new_reader(raw):\n    return parse(raw, 1)\n"
        self.assertEqual(violations("joulewise/battery_float.py", source),
                         [("joulewise/battery_float.py", 2, "parse")])

    def test_pair_verdict_calls_outside_module_are_flagged_but_isinstance_is_allowed(self) -> None:
        source = ("from joulewise.battery_float import PairVerdict as PV\n"
                  "from joulewise import battery_float as bf\n"
                  "def f(value):\n"
                  "    isinstance(value, PV)\n"
                  "    isinstance(value, bf.PairVerdict)\n"
                  "    PV('quiet', 'pass', (), None, None, None, None, None)\n"
                  "    bf.PairVerdict('quiet', 'pass', (), None, None, None, None, None)\n")
        self.assertEqual(violations("scripts/x.py", source), [
            ("scripts/x.py", 6, "PairVerdict"), ("scripts/x.py", 7, "PairVerdict")])

    def test_pair_verdict_forgeries_are_flagged(self) -> None:
        cases = (
            ("from joulewise import battery_float as bf\nPV = bf.PairVerdict\nPV()\n", "PairVerdict"),
            ("from joulewise import battery_float as bf\nimport dataclasses as dc\ndc.replace(v, status='pass')\n", "dataclasses.replace"),
            ("from joulewise import battery_float as bf\nfrom dataclasses import replace as rep\nrep(v, status='pass')\n", "dataclasses.replace"),
            ("from joulewise import battery_float as bf\ntype(v)()\n", "type(...)(...)"),
            ("from joulewise import battery_float as bf\ngetattr(bf, 'PairVerdict')()\n", "getattr(battery_float, ...)"),
        )
        for source, label in cases:
            with self.subTest(label=label):
                self.assertIn(label, [row[2] for row in violations("scripts/x.py", source)])
        self.assertEqual(violations("scripts/x.py",
            "from joulewise import battery_float as bf\nisinstance(v, bf.PairVerdict)\n"
            "issubclass(cls, bf.PairVerdict)\n"), [])

    def test_factory_calls_have_one_named_reader_exemption(self) -> None:
        source = "from joulewise import battery_float as bf\nbf.not_applicable_verdict('bundle')\n"
        self.assertEqual(violations("joulewise/x.py", source),
                         [("joulewise/x.py", 2, "not_applicable_verdict")])
        self.assertEqual(violations("joulewise/bundle_read.py", source), [])
        self.assertEqual(FACTORY_ALLOWLIST,
                         {"joulewise/bundle_read.py": "text 8 reader states"})

    def test_only_core_references_parser_and_wrappers_only_call_core(self) -> None:
        tree = ast.parse((ROOT / "joulewise/battery_float.py").read_text())
        functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
        for name in ("authenticate_quiet_session", "authenticate_bundle", "authenticate_capture"):
            calls = {node.func.id for node in ast.walk(functions[name])
                     if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                     and node.func.id in {"authenticate_pair", "parse", "validate_window"}}
            self.assertEqual(calls, {"authenticate_pair"})

    # ---- self-test (§3.10) ----

    def test_self_test_the_pre_seam_epoch_bound_body_is_one_violation(self) -> None:
        # The body of `_dry_run_epoch_bound` at 3e984ecc:358.
        source = (
            "from joulewise import battery_float\n"
            "def _dry_run_epoch_bound(root, candidate_id, session, preregistration_sha256):\n"
            "    record = battery_float.load_committed_verdict(\n"
            "        root, candidate_id, session=session,\n"
            "        preregistration_sha256=preregistration_sha256,\n"
            "    )\n"
            "    return record\n"
        )
        self.assertEqual(violations("scripts/x.py", source),
                         [("scripts/x.py", 3, "load_committed_verdict")])

    def test_self_test_an_aliased_import_and_an_attribute_reference_are_two(self) -> None:
        source = (
            "from joulewise.battery_float import compare_verdict as cv\n"
            "import joulewise.battery_float\n"
            "def f():\n"
            "    return joulewise.battery_float.validate_window\n"
        )
        self.assertEqual(violations("scripts/x.py", source),
                         [("scripts/x.py", 1, "compare_verdict"), ("scripts/x.py", 4, "validate_window")])

    def test_self_test_relative_imports_are_resolved(self) -> None:
        # Final delta (Astra R1): a relative import in the package names the
        # same module and must be caught exactly like the absolute form.
        source = ("from . import battery_float as rbf\n"
                  "from .battery_float import compare_verdict\n"
                  "def f(s, a, b):\n"
                  "    rbf.validate_window(s)\n"
                  "    return compare_verdict(a, b)\n")
        self.assertEqual(violations("joulewise/night_gate.py", source), [
            ("joulewise/night_gate.py", 2, "compare_verdict"),
            ("joulewise/night_gate.py", 4, "validate_window"),
            ("joulewise/night_gate.py", 5, "compare_verdict"),
        ])

    def test_self_test_a_producer_status_read_outside_the_allowlist_is_one(self) -> None:
        source = (
            "from joulewise import battery_float as bf\n"
            "def dry_run(session, snapshot):\n"
            "    return bf.verdict_record(session, snapshot=snapshot, preregistration_sha256='x',\n"
            "                             tool_commit='y', module_sha256='z', wall_time_s=0)['status']\n"
        )
        self.assertEqual(violations("scripts/x.py", source), [("scripts/x.py", 3, "verdict_record")])

    def test_self_test_bound_names_strings_and_in_module_names(self) -> None:
        source = (
            "from joulewise.battery_float import parse\n"
            "from joulewise import battery_float\n"
            "def g(raw):\n"
            "    '''validate_window in a docstring is prose.'''\n"
            "    getattr(battery_float, 'validate_window')\n"
            "    return parse(raw, 0)\n"
        )
        self.assertEqual(violations("scripts/x.py", source), [
            ("scripts/x.py", 1, "parse"), ("scripts/x.py", 5, "getattr(battery_float, ...)"),
            ("scripts/x.py", 5, "validate_window"),
            ("scripts/x.py", 6, "parse")])
        self.assertEqual(violations("joulewise/x.py", "ERRORS = {'vm_stat': 'parse'}\n"), [])
        in_module = "def summary(session):\n    return validate_window(session)['status']\n"
        self.assertEqual(violations("joulewise/battery_float.py", in_module),
                         [("joulewise/battery_float.py", 2, "validate_window")])

    # ---- §3.12 (xii): the guard over the reviewed tree ----

    def test_the_guard_reports_every_primitive_call_of_the_pre_seam_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "tree.tar"
            made = subprocess.run(
                ("git", "-C", str(ROOT), "archive", "-o", str(archive), "3e984ecc",
                 "joulewise", "scripts", "tests/fixtures/epoch_bootstrap/build.py"),
                capture_output=True, check=False)
            if made.returncode != 0:
                self.skipTest("commit 3e984ecc is not in this clone's history")
            with tarfile.open(archive) as bundle:
                bundle.extractall(Path(tmp) / "tree", filter="data")
            found = tree_violations(Path(tmp) / "tree")
        issuer = "scripts/issue_calibration_acceptance_generation.py"
        cadence = "scripts/calibration_cadence_report.py"
        self.assertEqual([(name, line) for name, line, primitive in found if primitive in GUARDED], [
            (cadence, 81), (cadence, 85), (cadence, 93),
            (issuer, 243), (issuer, 250), (issuer, 263), (issuer, 358),
            (issuer, 1586), (issuer, 1593), (issuer, 1602),
        ])

    # ---- the test-file rule (§3.10, last sentence) ----

    def test_test_files_use_no_primitive_outside_the_permitted_four(self) -> None:
        found = []
        for path in sorted((ROOT / "tests").rglob("*.py")):
            relative = path.relative_to(ROOT).as_posix()
            if relative in PRIMITIVE_TEST_FILES or not _tracked(ROOT, relative):
                continue
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
            for node in ast.walk(tree):
                if (isinstance(node, ast.ImportFrom) and node.module == MODULE
                        and any(alias.name in GUARDED for alias in node.names)):
                    found.append((relative, node.lineno))
                elif (isinstance(node, ast.Attribute) and node.attr in GUARDED
                      and ((isinstance(node.value, ast.Name) and node.value.id == "battery_float")
                           or (isinstance(node.value, ast.Attribute)
                               and node.value.attr == "battery_float"))):
                    found.append((relative, node.lineno))
        self.assertEqual(found, [])


if __name__ == "__main__":
    unittest.main()
