"""Refusal census of the HAZARD_PACK path (lane 2026-10-06 refusal-census).

Ed, 2026-10-05: physics refuses; everything else is a flag.  Fix rounds kept
adding "fail closed" refusals after the gate prune removed them.  This module
finds every place on the HAZARD path that can refuse, stop or exclude, so a
test (``test_refusal_allowlist``) can require each one to be listed, with the
physical quantity or the number it protects, in
``configs/gates/hazard_refusals.json``.

What counts as a refusal site, found mechanically by parsing the source:

``raise``
    Any ``raise`` statement, any ``assert`` (``AssertionError``) and any call
    with ``check=True`` (``CalledProcessError``).  A raise that a caller turns
    into a refusal is as much a refusal as the caller (the 2026-10-06 driver
    lineage check was a ``raise ValueError`` inside a ``try`` whose ``except``
    refused the window).
``exit``
    ``sys.exit(x)`` / ``os._exit(x)`` / ``exit(x)`` with ``x`` not the literal 0.
``return_code``
    ``return <int>`` with a nonzero int literal, or ``return <NAME>`` whose last
    name part looks like an exit code (``EXIT_*``, ``*_EXIT*``, ``RC_*``) and
    is not a success code.
``status``
    ``return "<status>"`` (or a tuple starting with one) for a blocking status
    (``BLOCKING_STATUSES``), and a verdict field set to False
    (``valid = False``, ``entry["valid"] = False``, ``valid=False`` as a
    keyword or dict key; fields in ``VERDICT_FIELDS``).
``refusal_call``
    A call to a refusal constructor or writer (``REFUSAL_CALLEES``),
    ``Verdict(module, <status>, ...)`` whose status is not the name ``PASS``,
    and any call passing a refusal name (``REFUSAL_NAMES``: ``finish(NULL,
    "identity", ...)`` in the arm).
``reason``
    ``reasons.append(...)`` / ``refusals.append(...)``: a new reason in a list
    that decides a refusal (hazard judges, cooldown, admission).
``kill``
    A signal sent to a process: ``os.kill``, ``os.killpg``, ``.terminate()``,
    ``.kill()``, ``.send_signal()``.  A stage or member stopped by a wall
    budget or a cap is stopped here.
``shell``
    ``stop_chain <reason>``, and ``exit <n>`` / ``return <n>`` with n not 0
    (``$rc`` and ``$?`` pass a status through), in rendered shell text: every
    string constant of a module in ``SHELL_RENDERING_MODULES``, string
    constants elsewhere that look like shell, whole ``.sh`` files, and the
    runbook shell functions the chain copies verbatim (``RUNBOOK_FUNCTIONS``).
Python sources embedded as string constants named ``*_HELPER`` (the chain's
inline helpers) are parsed and scanned too, under the function name
``<HELPER_NAME>``.

A site's key is ``(file, function, kind, detail)``; ``function`` is the dotted
name of the enclosing def/class (``<module>`` at top level).  ``detail`` is the
exception class or callee plus a reason: a code-shaped string literal
(``launch_binding_mismatch``), an ALL_CAPS constant, a ``_CODES["..."]``
subscript, or else the first three words of the leading literal text of the
message.  Line numbers are never part of a key, so moving code does not churn
the allowlist; adding a refusal in a function, or a new reason, does.

Each key also has a ``guard`` digest: a hash of the conditions that lead to
its sites (the tests of every enclosing ``if``/``while``/conditional
expression, the branch taken, and the exception types of every enclosing
``except``).  Widening an existing refusal (``or x != y``) changes the digest,
and so does narrowing a catcher so that an exception now escapes.  The digest
is built from a version-independent serialization of the syntax tree, so it is
the same on every supported Python.

Run ``python -m tests.hazards.refusal_census`` from the repository root to
print the sites that the allowlist does not match (unlisted, stale, count or
guard changed), ready to paste and complete.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable, Iterator

ROOT = Path(__file__).resolve().parents[2]
ALLOWLIST = ROOT / "configs" / "gates" / "hazard_refusals.json"

REFUSAL_CALLEES = frozenset({
    "refuse", "_refusal_mapping", "Refusal", "_write_standard_refusal_result",
    "_write_driver_refusal", "unmeasured", "fail_closed", "_refuse", "refusal", "Decision",
})
# A call passing one of these names is deciding a refusal (``finish(NULL, ...)``).
REFUSAL_NAMES = frozenset({"NULL", "REFUSE", "UNMEASURED", "REFUSED", "HOLD_UNSAFE"})
BLOCKING_STATUSES = frozenset({"blocked", "refused", "invalid", "aborted", "excluded", "rejected",
                               "not_admitted", "refuse", "abort", "exclude"})
# A verdict field set to False decides a refusal downstream (driver locators "valid").
VERDICT_FIELDS = frozenset({"valid", "admitted", "eligible", "allowed", "passed", "go",
                            "admit", "accept", "accepted"})
REASON_LISTS = frozenset({"reasons", "refusals", "refusal_reasons", "blocking_reasons"})
EXIT_CALLEES = frozenset({"sys.exit", "os._exit", "exit", "_exit"})
SUCCESS_NAMES = re.compile(r"(^|_)(OK|GO|SUCCESS|PASS|COMPLETED|CLEAN)$")
EXIT_NAME = re.compile(r"^(EXIT|RC)_|_EXIT(_|$)|^EXIT$")
CODE_SHAPED = re.compile(r"^[a-z][a-z0-9]*(?:[._][a-z0-9]+)+$")
CAPS_CONSTANT = re.compile(r"^_?[A-Z][A-Z0-9_]{2,}$")
SHELL_STOP = re.compile(r"\bstop_chain\s+([A-Za-z_]\w*)")
SHELL_EXIT = re.compile(r"(?<![\w$.-])(exit|return)\s+(\$\{?\w+\}?|\d+)")
WORD = re.compile(r"[A-Za-z][A-Za-z_'-]*")
CATEGORIES = ("PHYSICS", "NUMBER_INTEGRITY", "INTERNAL", "DEFERRED_REPRESENTATION", "BASELINE")
KINDS = ("raise", "exit", "return_code", "status", "refusal_call", "reason", "kill", "shell")
KILL_CALLEES = frozenset({"kill", "killpg", "terminate", "send_signal"})
# Modules that render shell: every string constant in them is shell text.
SHELL_RENDERING_MODULES = frozenset({"joulewise/b5/chain.py"})
# Non-Python sources whose named shell functions the chain copies verbatim.
RUNBOOK_FUNCTIONS = {"docs/phase_2/window_runbook.md": ("screen_pre_calibration",)}
# A string constant naming a first-party file or module is a dependency (a
# script a stage runs, a module loaded by name).
PATH_LITERAL = re.compile(r"^(?:scripts|joulewise)/[\w./-]+\.(?:py|sh)$")
MODULE_LITERAL = re.compile(r"^(?:joulewise|scripts)(?:\.\w+)+$")
DYNAMIC_LOADERS = frozenset({"import_module", "spec_from_file_location", "_load_script", "load_script",
                             "_script_module", "run_path", "run_module", "__import__"})
_SKIP_FIELDS = frozenset({"ctx", "kind", "type_comment", "lineno", "col_offset", "end_lineno",
                          "end_col_offset"})


def _name(node: ast.AST) -> str:
    """Dotted text of a Name/Attribute chain, else ''."""

    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        return ".".join(reversed(parts))
    return ""


def canonical(node: object) -> str:
    """A serialization of a syntax tree that is the same on Python 3.11 to 3.14."""

    if isinstance(node, ast.AST):
        fields = []
        for field in node._fields:
            if field in _SKIP_FIELDS:
                continue
            value = getattr(node, field, None)
            if value is None or value == []:
                continue
            fields.append(f"{field}={canonical(value)}")
        return f"{type(node).__name__}({','.join(fields)})"
    if isinstance(node, list):
        return "[" + ",".join(canonical(item) for item in node) + "]"
    return repr(node)


def _leading_text(node: ast.AST | None) -> str:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        return " ".join(part.value for part in node.values
                        if isinstance(part, ast.Constant) and isinstance(part.value, str))
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Mod)):
        return _leading_text(node.left)
    if isinstance(node, ast.Call) and _name(node.func).endswith(".format"):
        return _leading_text(node.func.value)  # type: ignore[attr-defined]
    return ""


def _reason(node: ast.AST | None) -> str:
    """A stable reason for a refusal argument: code, constant, subscript or message stem."""

    if node is None:
        return ""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        text = node.value.strip()
        if CODE_SHAPED.match(text) or CAPS_CONSTANT.match(text):
            return text
    if isinstance(node, (ast.Name, ast.Attribute)):
        last = _name(node).rsplit(".", 1)[-1]
        if CAPS_CONSTANT.match(last):
            return last
    if isinstance(node, ast.Subscript):
        index = node.slice
        if isinstance(index, ast.Constant) and isinstance(index.value, str):
            return f"{_name(node.value).rsplit('.', 1)[-1]}[{index.value}]"
    words = WORD.findall(_leading_text(node))[:3]
    return " ".join(word.lower() for word in words)


def _first_arg(call: ast.Call) -> ast.AST | None:
    if call.args:
        return call.args[0]
    for keyword in call.keywords:
        if keyword.arg in ("reason", "code", "message", "msg", "detail"):
            return keyword.value
    return None


def _raise_detail(node: ast.Raise) -> str:
    exc = node.exc
    if exc is None:
        return "<reraise>"
    if isinstance(exc, ast.Call):
        cls = _name(exc.func).rsplit(".", 1)[-1] or "<call>"
        if cls == "SystemExit":
            arg = _first_arg(exc)
            return f"SystemExit|{ast.unparse(arg)[:60] if arg is not None else ''}"
        reason = _reason(_first_arg(exc))
        return f"{cls}|{reason}" if reason else cls
    name = _name(exc)
    if name and name.rsplit(".", 1)[-1][:1].isupper():
        return name.rsplit(".", 1)[-1]
    return f"<expr:{ast.unparse(exc)[:40]}>"


def _is_exit_value(node: ast.AST | None) -> str | None:
    """The exit-code text if ``node`` is a nonzero exit value, else None."""

    if node is None:
        return None
    if isinstance(node, ast.Constant) and isinstance(node.value, int) and not isinstance(node.value, bool):
        return None if node.value == 0 else str(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub) and isinstance(node.operand, ast.Constant):
        return "-" + str(node.operand.value)
    name = _name(node)
    if name:
        last = name.rsplit(".", 1)[-1]
        if EXIT_NAME.search(last) and not SUCCESS_NAMES.search(last):
            return last
    return None


def _is_false(node: ast.AST | None) -> bool:
    return isinstance(node, ast.Constant) and node.value is False


def _field_name(target: ast.AST) -> str:
    if isinstance(target, ast.Name):
        return target.id
    if isinstance(target, ast.Attribute):
        return target.attr
    if isinstance(target, ast.Subscript) and isinstance(target.slice, ast.Constant) \
            and isinstance(target.slice.value, str):
        return target.slice.value
    return ""


def _looks_like_shell(text: str) -> bool:
    return any(token in text for token in ("$(", "${", "(( ", "[[ ", "() {", "\nfi", "; then", " || ", " && "))


def shell_sites(text: str) -> list[tuple[str, str]]:
    found = [("shell", f"stop_chain {match.group(1)}") for match in SHELL_STOP.finditer(text)]
    found += [("shell", f"{match.group(1)} {match.group(2)}") for match in SHELL_EXIT.finditer(text)
              if match.group(2) not in ("0", "$rc", "$?")]
    return found


class _Visitor(ast.NodeVisitor):
    def __init__(self, file: str, prefix: str = "", *, all_strings_are_shell: bool = False) -> None:
        self.file = file
        self.stack: list[str] = [prefix] if prefix else []
        self.guards: list[str] = []
        self.sites: list[tuple[str, str, str, str, int, str]] = []
        self.all_strings_are_shell = all_strings_are_shell

    def _function(self) -> str:
        return ".".join(self.stack) or "<module>"

    def _add(self, kind: str, detail: str, node: ast.AST) -> None:
        self.sites.append((self.file, self._function(), kind, detail, getattr(node, "lineno", 0),
                           "|".join(self.guards)))

    def _scope(self, node: ast.AST, name: str) -> None:
        self.stack.append(name)
        saved, self.guards = self.guards, []
        self.generic_visit(node)
        self.guards = saved
        self.stack.pop()

    def _guarded(self, label: str, nodes: Iterable[ast.AST]) -> None:
        self.guards.append(label)
        for child in nodes:
            self.visit(child)
        self.guards.pop()

    # -- scopes and guards ---------------------------------------------------
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
        for decorator in node.decorator_list:
            self.visit(decorator)
        self._scope(node, node.name)

    visit_AsyncFunctionDef = visit_FunctionDef  # type: ignore[assignment]

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
        self._scope(node, node.name)

    def visit_If(self, node: ast.If) -> None:  # noqa: N802
        self.visit(node.test)
        test = canonical(node.test)
        self._guarded("if:" + test, node.body)
        self._guarded("else:" + test, node.orelse)

    visit_While = visit_If  # type: ignore[assignment]

    def visit_IfExp(self, node: ast.IfExp) -> None:  # noqa: N802
        self.visit(node.test)
        test = canonical(node.test)
        self._guarded("if:" + test, [node.body])
        self._guarded("else:" + test, [node.orelse])

    def visit_Try(self, node: ast.Try) -> None:  # noqa: N802
        caught = canonical([handler.type for handler in node.handlers])
        self._guarded("try:" + caught, node.body)
        for handler in node.handlers:
            self._guarded("except:" + canonical(handler.type), handler.body)
        self._guarded("tryelse:" + caught, node.orelse)
        for child in node.finalbody:
            self.visit(child)

    visit_TryStar = visit_Try  # type: ignore[assignment]

    # -- sites ---------------------------------------------------------------
    def visit_Raise(self, node: ast.Raise) -> None:  # noqa: N802
        self._add("raise", _raise_detail(node), node)
        self.generic_visit(node)

    def visit_Assert(self, node: ast.Assert) -> None:  # noqa: N802
        reason = _reason(node.msg)
        self._add("raise", f"AssertionError|{reason}" if reason else "AssertionError", node)
        self.generic_visit(node)

    def visit_Return(self, node: ast.Return) -> None:  # noqa: N802
        value = node.value
        code = _is_exit_value(value)
        if code is not None:
            self._add("return_code", code, node)
        head = value.elts[0] if isinstance(value, ast.Tuple) and value.elts else value
        if isinstance(head, ast.Constant) and head.value in BLOCKING_STATUSES:
            self._add("status", str(head.value), node)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:  # noqa: N802
        targets = [_name(target) for target in node.targets]
        value = node.value
        if isinstance(value, ast.Constant) and isinstance(value.value, str) \
                and any(target.endswith("_HELPER") for target in targets):
            try:
                tree = ast.parse(value.value)
            except SyntaxError:
                tree = None
            if tree is not None:
                inner = _Visitor(self.file, f"<{targets[0]}>")
                inner.visit(tree)
                self.sites.extend(inner.sites)
                return
        if _is_false(value):
            for target in node.targets:
                if _field_name(target) in VERDICT_FIELDS:
                    self._add("status", f"{_field_name(target)}=False", node)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:  # noqa: N802
        if _is_false(node.value) and _field_name(node.target) in VERDICT_FIELDS:
            self._add("status", f"{_field_name(node.target)}=False", node)
        self.generic_visit(node)

    def visit_Dict(self, node: ast.Dict) -> None:  # noqa: N802
        for key, value in zip(node.keys, node.values):
            if isinstance(key, ast.Constant) and key.value in VERDICT_FIELDS and _is_false(value):
                self._add("status", f"{key.value}=False", node)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802
        name = _name(node.func)
        last = name.rsplit(".", 1)[-1]
        for keyword in node.keywords:
            if keyword.arg in VERDICT_FIELDS and _is_false(keyword.value):
                self._add("status", f"{keyword.arg}=False", node)
            if keyword.arg == "check" and isinstance(keyword.value, ast.Constant) \
                    and keyword.value.value is True:
                self._add("raise", f"CalledProcessError|{last}", node)
        if name in EXIT_CALLEES or last == "_exit" and name.startswith("os"):
            arg = node.args[0] if node.args else None
            if not (isinstance(arg, ast.Constant) and arg.value == 0):
                self._add("exit", ast.unparse(arg)[:60] if arg is not None else "", node)
        elif last in KILL_CALLEES and isinstance(node.func, ast.Attribute):
            signal = next((arg for arg in node.args if "SIG" in _name(arg)), None)
            self._add("kill", f"{last}|{_name(signal).rsplit('.', 1)[-1] if signal is not None else ''}", node)
        elif last in REFUSAL_CALLEES:
            self._add("refusal_call", f"{last}|{_reason(_first_arg(node))}", node)
        elif any(_name(arg).rsplit(".", 1)[-1] in REFUSAL_NAMES for arg in node.args) and last != "Verdict":
            names = [_name(arg).rsplit(".", 1)[-1] for arg in node.args]
            marker = next(name for name in names if name in REFUSAL_NAMES)
            rest = [arg for arg, name in zip(node.args, names) if name != marker]
            self._add("refusal_call", f"{last}|{marker}|{_reason(rest[0]) if rest else ''}", node)
        elif last == "Verdict" and len(node.args) >= 2 and _name(node.args[1]) != "PASS":
            self._add("refusal_call", f"Verdict|{ast.unparse(node.args[1])[:60]}", node)
        elif last == "append" and isinstance(node.func, ast.Attribute) \
                and _name(node.func.value).rsplit(".", 1)[-1] in REASON_LISTS:
            self._add("reason", _reason(node.args[0] if node.args else None), node)
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:  # noqa: N802
        if not isinstance(node.value, str):
            return
        text = node.value
        if self.all_strings_are_shell or _looks_like_shell(text):
            for kind, detail in shell_sites(text):
                self._add(kind, detail, node)
        else:
            for match in SHELL_STOP.finditer(text):
                self._add("shell", f"stop_chain {match.group(1)}", node)


def shell_functions(text: str, names: Iterable[str]) -> Iterator[tuple[str, str]]:
    """``(name, body)`` of each named ``name() {`` ... ``}`` shell function in ``text``."""

    for name in names:
        start = text.find(f"{name}() {{")
        if start < 0:
            continue
        end = text.find("\n}", start)
        yield name, text[start:end + 2 if end >= 0 else len(text)]


def scan_source(file: str, source: str) -> list[tuple[str, str, str, str, int, str]]:
    if file in RUNBOOK_FUNCTIONS:
        return [(file, f"<shell:{name}>", kind, detail, 0, "")
                for name, body in shell_functions(source, RUNBOOK_FUNCTIONS[file])
                for kind, detail in shell_sites(body)]
    if file.endswith(".sh"):
        return [(file, "<script>", kind, detail, 0, "") for kind, detail in shell_sites(source)]
    visitor = _Visitor(file, all_strings_are_shell=file in SHELL_RENDERING_MODULES)
    visitor.visit(ast.parse(source))
    return visitor.sites


def scan(files: Iterable[str], root: Path = ROOT) -> list[tuple[str, str, str, str, int, str]]:
    sites = []
    for file in files:
        sites.extend(scan_source(file, (root / file).read_text(encoding="utf-8")))
    return sites


def site_counts(sites: Iterable[tuple]) -> Counter:
    return Counter(tuple(site[:4]) for site in sites)


def site_guards(sites: Iterable[tuple]) -> dict[tuple, str]:
    """One digest per key over the sorted guard paths of its sites."""

    paths: dict[tuple, list[str]] = {}
    for site in sites:
        paths.setdefault(tuple(site[:4]), []).append(site[5])
    return {key: hashlib.sha256("\n".join(sorted(value)).encode("utf-8")).hexdigest()[:16]
            for key, value in paths.items()}


# ---------------------------------------------------------------- scan scope

def _resolve(name: str, root: Path) -> str | None:
    for candidate in (root / (name.replace(".", "/") + ".py"),
                      root / name.replace(".", "/") / "__init__.py"):
        if candidate.is_file():
            return str(candidate.relative_to(root))
    return None


def dependencies(file: str, root: Path = ROOT) -> tuple[set[str], list[str]]:
    """First-party files ``file`` depends on, and its unresolvable dynamic loads.

    Static imports; string constants naming a first-party ``.py``/``.sh`` path
    (a script a stage runs) or a dotted ``joulewise.``/``scripts.`` module; and
    literal arguments of dynamic loaders.  A dynamic loader whose target is not
    a literal is returned in the second list as ``function:line``.
    """

    if not file.endswith(".py"):
        return set(), []
    tree = ast.parse((root / file).read_text(encoding="utf-8"))
    package = file.replace("/", ".").removesuffix(".py").removesuffix(".__init__")
    found: set[str] = set()
    dynamic: list[str] = []

    def add_module(name: str) -> None:
        if name.split(".")[0] in ("joulewise", "scripts"):
            path = _resolve(name, root)
            if path is not None and path != file:
                found.add(path)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                add_module(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                parts = package.split(".")
                keep = len(parts) - node.level + (1 if file.endswith("__init__.py") else 0)
                module = ".".join(parts[:keep] + ([node.module] if node.module else []))
            else:
                module = node.module or ""
            add_module(module)
            for alias in node.names:
                add_module(f"{module}.{alias.name}")
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            text = node.value
            if PATH_LITERAL.match(text) and (root / text).is_file() and text != file:
                found.add(text)
            elif MODULE_LITERAL.match(text):
                add_module(text)
        elif isinstance(node, ast.Call) and _name(node.func).rsplit(".", 1)[-1] in DYNAMIC_LOADERS:
            literal = [arg for arg in node.args if isinstance(arg, ast.Constant) and isinstance(arg.value, str)]
            if not literal:
                dynamic.append(f"{_name(node.func)}:{node.lineno}")
    return found, dynamic


def direct_imports(file: str, root: Path = ROOT) -> set[str]:
    return dependencies(file, root)[0]


def load_allowlist(path: Path = ALLOWLIST) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def allowlist_counts(document: dict) -> Counter:
    counts: Counter = Counter()
    for entry in document["sites"]:
        counts[(entry["file"], entry["function"], entry["kind"], entry["detail"])] += entry["count"]
    return counts


def differences(document: dict, root: Path = ROOT) -> dict[str, list]:
    """Sites the allowlist does not match: unlisted, stale, miscounted and guard-changed."""

    sites = scan(document["scan"]["modules"], root)
    observed = site_counts(sites)
    guards = site_guards(sites)
    listed = allowlist_counts(document)
    listed_guards = {(entry["file"], entry["function"], entry["kind"], entry["detail"]): entry.get("guard")
                     for entry in document["sites"]}
    lines: dict[tuple, list[int]] = {}
    for site in sites:
        lines.setdefault(tuple(site[:4]), []).append(site[4])
    unlisted, stale, miscounted, guard_changed = [], [], [], []
    for key, count in sorted(observed.items()):
        row = {"file": key[0], "function": key[1], "kind": key[2], "detail": key[3]}
        if key not in listed:
            unlisted.append({**row, "count": count, "guard": guards[key], "lines": lines[key]})
        elif listed[key] != count:
            miscounted.append({**row, "listed": listed[key], "observed": count, "lines": lines[key]})
        elif listed_guards.get(key) != guards[key]:
            guard_changed.append({**row, "listed_guard": listed_guards.get(key), "guard": guards[key],
                                  "lines": lines[key]})
    for key in sorted(set(listed) - set(observed)):
        stale.append({"file": key[0], "function": key[1], "kind": key[2], "detail": key[3]})
    return {"unlisted": unlisted, "stale": stale, "miscounted": miscounted, "guard_changed": guard_changed}


def iter_scope_gaps(document: dict, root: Path = ROOT) -> Iterator[str]:
    scanned = set(document["scan"]["modules"])
    not_scanned = document["scan"]["not_scanned"]
    allowed_dynamic = document["scan"].get("dynamic_loads", {})
    for file in sorted(scanned):
        found, dynamic = dependencies(file, root)
        for dependency in sorted(found):
            if dependency not in scanned and dependency not in not_scanned:
                yield f"{file} depends on {dependency}, which is neither scanned nor listed in not_scanned"
        for load in dynamic:
            if f"{file}:{load.rsplit(':', 1)[0]}" not in allowed_dynamic:
                yield (f"{file} loads a module by a computed name ({load}); list "
                       f"'{file}:{load.rsplit(':', 1)[0]}' in scan.dynamic_loads with what it can load")


def main(argv: list[str] | None = None) -> int:
    document = load_allowlist()
    result = differences(document)
    result["scope_gaps"] = list(iter_scope_gaps(document))
    print(json.dumps(result, indent=1))
    return 0 if not any(result.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
