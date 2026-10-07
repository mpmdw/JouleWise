"""Refusal census of the HAZARD_PACK path (lane 2026-10-06 refusal-census).

Ed, 2026-10-05: physics refuses; everything else is a flag.  Fix rounds kept
adding "fail closed" refusals after the gate prune removed them.  This module
finds every place on the HAZARD path that can refuse, stop or exclude, so a
test (``test_refusal_allowlist``) can require each one to be listed, with the
physical quantity or the number it protects, in
``configs/gates/hazard_refusals.json``.

What counts as a refusal site, found mechanically by parsing the source:

``raise``
    Any ``raise`` statement.  A raise that a caller turns into a refusal is as
    much a refusal as the caller (the 2026-10-06 driver lineage check was a
    ``raise ValueError`` inside a ``try`` whose ``except`` refused the window).
``exit``
    ``sys.exit(x)`` / ``os._exit(x)`` / ``exit(x)`` with ``x`` not the literal 0.
``return_code``
    ``return <int>`` with a nonzero int literal, or ``return <NAME>`` whose last
    name part looks like an exit code (``EXIT_*``, ``*_EXIT*``, ``RC_*``) and
    is not a success code.
``status``
    ``return "<status>"`` (or a tuple starting with one) for a blocking status:
    ``blocked``, ``refused``, ``invalid``, ``aborted``, ``excluded``.
``refusal_call``
    A call to a refusal constructor or writer (``REFUSAL_CALLEES``), and
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
    Inside string constants that look like shell: ``stop_chain <reason>``, and
    ``exit <n>`` / ``return <n>`` with n not 0 (``$rc`` and ``$?`` pass a
    status through and are not counted).
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

Run ``python -m tests.hazards.refusal_census`` from the repository root to
print the sites that the allowlist does not match (unlisted, stale, or a
count that differs), ready to paste and complete.
"""

from __future__ import annotations

import ast
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
BLOCKING_STATUSES = frozenset({"blocked", "refused", "invalid", "aborted", "excluded"})
REASON_LISTS = frozenset({"reasons", "refusals", "refusal_reasons", "blocking_reasons"})
EXIT_CALLEES = frozenset({"sys.exit", "os._exit", "exit", "_exit"})
SUCCESS_NAMES = re.compile(r"(^|_)(OK|GO|SUCCESS|PASS|COMPLETED|CLEAN)$")
EXIT_NAME = re.compile(r"^(EXIT|RC)_|_EXIT(_|$)|^EXIT$")
CODE_SHAPED = re.compile(r"^[a-z][a-z0-9]*(?:[._][a-z0-9]+)+$")
CAPS_CONSTANT = re.compile(r"^_?[A-Z][A-Z0-9_]{2,}$")
SHELL_STOP = re.compile(r"\bstop_chain\s+([A-Za-z_]\w*)")
SHELL_EXIT = re.compile(r"(?<![\w$])(exit|return)\s+(\$\{?\w+\}?|\d+)")
WORD = re.compile(r"[A-Za-z][A-Za-z_'-]*")
CATEGORIES = ("PHYSICS", "NUMBER_INTEGRITY", "INTERNAL", "DEFERRED_REPRESENTATION", "BASELINE")
KINDS = ("raise", "exit", "return_code", "status", "refusal_call", "reason", "kill", "shell")
KILL_CALLEES = frozenset({"kill", "killpg", "terminate", "send_signal"})


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


class _Visitor(ast.NodeVisitor):
    def __init__(self, file: str, prefix: str = "") -> None:
        self.file = file
        self.stack: list[str] = [prefix] if prefix else []
        self.sites: list[tuple[str, str, str, str, int]] = []

    def _function(self) -> str:
        return ".".join(self.stack) or "<module>"

    def _add(self, kind: str, detail: str, node: ast.AST) -> None:
        self.sites.append((self.file, self._function(), kind, detail, getattr(node, "lineno", 0)))

    def _scope(self, node: ast.AST, name: str) -> None:
        self.stack.append(name)
        self.generic_visit(node)
        self.stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
        for decorator in node.decorator_list:
            self.visit(decorator)
        self._scope(node, node.name)

    visit_AsyncFunctionDef = visit_FunctionDef  # type: ignore[assignment]

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
        self._scope(node, node.name)

    def visit_Raise(self, node: ast.Raise) -> None:  # noqa: N802
        self._add("raise", _raise_detail(node), node)
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

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802
        name = _name(node.func)
        last = name.rsplit(".", 1)[-1]
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
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:  # noqa: N802
        if not isinstance(node.value, str):
            return
        text = node.value
        for match in SHELL_STOP.finditer(text):
            self._add("shell", f"stop_chain {match.group(1)}", node)
        if _looks_like_shell(text):
            for match in SHELL_EXIT.finditer(text):
                if match.group(2) not in ("0", "$rc", "$?"):
                    self._add("shell", f"{match.group(1)} {match.group(2)}", node)


def _looks_like_shell(text: str) -> bool:
    return any(token in text for token in ("$(", "${", "(( ", "[[ ", "() {", "\nfi", "; then", " || ", " && "))


def scan_source(file: str, source: str) -> list[tuple[str, str, str, str, int]]:
    visitor = _Visitor(file)
    visitor.visit(ast.parse(source))
    return visitor.sites


def scan(files: Iterable[str], root: Path = ROOT) -> list[tuple[str, str, str, str, int]]:
    sites = []
    for file in files:
        sites.extend(scan_source(file, (root / file).read_text(encoding="utf-8")))
    return sites


def site_counts(sites: Iterable[tuple[str, str, str, str, int]]) -> Counter:
    return Counter(site[:4] for site in sites)


# ---------------------------------------------------------------- scan scope

def direct_imports(file: str, root: Path = ROOT) -> set[str]:
    """First-party modules ``file`` imports directly, as repository paths."""

    tree = ast.parse((root / file).read_text(encoding="utf-8"))
    package = file.replace("/", ".").removesuffix(".py").removesuffix(".__init__")
    found: set[str] = set()

    def resolve(name: str) -> str | None:
        for candidate in (root / (name.replace(".", "/") + ".py"),
                          root / name.replace(".", "/") / "__init__.py"):
            if candidate.is_file():
                return str(candidate.relative_to(root))
        return None

    for node in ast.walk(tree):
        names: list[str] = []
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                parts = package.split(".")
                keep = len(parts) - node.level + (1 if file.endswith("__init__.py") else 0)
                module = ".".join(parts[:keep] + ([node.module] if node.module else []))
            else:
                module = node.module or ""
            names = [module] + [f"{module}.{alias.name}" for alias in node.names]
        elif isinstance(node, ast.Call) and _name(node.func).rsplit(".", 1)[-1] in (
                "spec_from_file_location", "_load_script", "load_script", "_script_module"):
            for arg in node.args:
                text = _leading_text(arg)
                if text.startswith("scripts/") and text.endswith(".py"):
                    names.append(text.removesuffix(".py").replace("/", "."))
        for name in names:
            if name.split(".")[0] in ("joulewise", "scripts"):
                path = resolve(name)
                if path is not None and path != file:
                    found.add(path)
    return found


def load_allowlist(path: Path = ALLOWLIST) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def allowlist_counts(document: dict) -> Counter:
    counts: Counter = Counter()
    for entry in document["sites"]:
        counts[(entry["file"], entry["function"], entry["kind"], entry["detail"])] += entry["count"]
    return counts


def differences(document: dict, root: Path = ROOT) -> dict[str, list]:
    """Sites the allowlist does not match: unlisted, stale and miscounted."""

    observed = site_counts(scan(document["scan"]["modules"], root))
    listed = allowlist_counts(document)
    lines: dict[tuple, list[int]] = {}
    for site in scan(document["scan"]["modules"], root):
        lines.setdefault(site[:4], []).append(site[4])
    unlisted, stale, miscounted = [], [], []
    for key, count in sorted(observed.items()):
        if key not in listed:
            unlisted.append({"file": key[0], "function": key[1], "kind": key[2], "detail": key[3],
                             "count": count, "lines": lines[key]})
        elif listed[key] != count:
            miscounted.append({"file": key[0], "function": key[1], "kind": key[2], "detail": key[3],
                               "listed": listed[key], "observed": count, "lines": lines[key]})
    for key in sorted(set(listed) - set(observed)):
        stale.append({"file": key[0], "function": key[1], "kind": key[2], "detail": key[3]})
    return {"unlisted": unlisted, "stale": stale, "miscounted": miscounted}


def iter_scope_gaps(document: dict, root: Path = ROOT) -> Iterator[str]:
    scanned = set(document["scan"]["modules"])
    not_scanned = document["scan"]["not_scanned"]
    for file in sorted(scanned):
        for imported in sorted(direct_imports(file, root)):
            if imported not in scanned and imported not in not_scanned:
                yield f"{file} imports {imported}, which is neither scanned nor listed in not_scanned"


def main(argv: list[str] | None = None) -> int:
    document = load_allowlist()
    result = differences(document)
    result["scope_gaps"] = list(iter_scope_gaps(document))
    print(json.dumps(result, indent=1))
    return 0 if not any(result.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
