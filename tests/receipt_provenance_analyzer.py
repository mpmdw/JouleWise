"""Interprocedural provenance analysis for receipt-bearing test collections."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping


_NONE = 0
_ROW = 1
_CORPUS = 2
_CORPUS_METHODS = {
    "filter",
    "replace",
    "without",
    "before",
    "replace_group",
    "insert_after",
}
_COPY_CALLS = {"copy", "deepcopy", "list", "tuple", "sorted"}


@dataclass(frozen=True, order=True)
class ProvenanceFinding:
    path: str
    line: int
    column: int
    kind: str
    detail: str


@dataclass
class _Function:
    name: str
    qualname: str
    class_name: str | None
    node: ast.FunctionDef | ast.AsyncFunctionDef
    annotated: bool
    return_kind: int = _NONE


def _call_name(call: ast.Call) -> str:
    function = call.func
    if isinstance(function, ast.Name):
        return function.id
    if isinstance(function, ast.Attribute):
        return function.attr
    return ""


def _annotation_is_corpus(annotation: ast.expr | None) -> bool:
    return bool(
        isinstance(annotation, ast.Name) and annotation.id == "ReceiptCorpus"
        or isinstance(annotation, ast.Attribute)
        and annotation.attr == "ReceiptCorpus"
    )


def _explicitly_wrapped_return(node: ast.AST) -> bool:
    if isinstance(node, ast.Call) and _call_name(node) == "ReceiptCorpus":
        return True
    if isinstance(node, (ast.Tuple, ast.List)):
        return any(_explicitly_wrapped_return(item) for item in node.elts)
    return False


def _scope_nodes(node: ast.AST) -> Iterable[ast.AST]:
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        yield child
        yield from _scope_nodes(child)


class _ModuleAnalyzer:
    def __init__(self, path: str, source: str) -> None:
        self.path = path
        self.tree = ast.parse(source, filename=path)
        self.functions: dict[str, _Function] = {}
        self.functions_by_name: dict[str, list[_Function]] = {}
        self.environments: dict[str, dict[str, int]] = {"<module>": {}}
        self.attribute_kinds: dict[str, int] = {}
        self._collect_functions()

    def _collect_functions(self) -> None:
        def visit(container: ast.AST, prefix: str = "", class_name: str | None = None) -> None:
            for child in ast.iter_child_nodes(container):
                if isinstance(child, ast.ClassDef):
                    visit(child, f"{prefix}{child.name}.", child.name)
                elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    qualname = f"{prefix}{child.name}"
                    annotated = any(
                        isinstance(decorator, ast.Name)
                        and decorator.id == "receipt_collection"
                        or isinstance(decorator, ast.Attribute)
                        and decorator.attr == "receipt_collection"
                        for decorator in child.decorator_list
                    )
                    function = _Function(
                        name=child.name,
                        qualname=qualname,
                        class_name=class_name,
                        node=child,
                        annotated=annotated,
                        return_kind=_CORPUS if annotated else _NONE,
                    )
                    self.functions[qualname] = function
                    self.functions_by_name.setdefault(child.name, []).append(function)
                    environment: dict[str, int] = {}
                    for argument in (*child.args.posonlyargs, *child.args.args, *child.args.kwonlyargs):
                        if _annotation_is_corpus(argument.annotation):
                            environment[argument.arg] = _CORPUS
                    self.environments[qualname] = environment
                    visit(child, f"{qualname}.", class_name)

        visit(self.tree)

    def _attribute_key(self, node: ast.Attribute, function: _Function | None) -> str:
        if isinstance(node.value, ast.Name) and node.value.id in {"self", "cls"}:
            owner = function.class_name if function is not None else "<module>"
            return f"{owner}.{node.attr}"
        return ast.unparse(node)

    def _resolve_function(
        self, call: ast.Call, function: _Function | None
    ) -> _Function | None:
        name = _call_name(call)
        candidates = self.functions_by_name.get(name, [])
        if not candidates:
            return None
        if isinstance(call.func, ast.Attribute) and isinstance(call.func.value, ast.Name):
            if call.func.value.id in {"self", "cls"} and function is not None:
                for candidate in candidates:
                    if candidate.class_name == function.class_name:
                        return candidate
        return candidates[0]

    def _kind(
        self,
        expression: ast.AST | None,
        environment: Mapping[str, int],
        function: _Function | None,
        overrides: Mapping[str, int] | None = None,
    ) -> int:
        if expression is None:
            return _NONE
        local = dict(environment)
        if overrides:
            local.update(overrides)
        if isinstance(expression, ast.Name):
            return local.get(expression.id, _NONE)
        if isinstance(expression, ast.Attribute):
            if expression.attr == "receipts":
                return _CORPUS
            return self.attribute_kinds.get(
                self._attribute_key(expression, function), _NONE
            )
        if isinstance(expression, ast.Call):
            name = _call_name(expression)
            if name == "ReceiptCorpus":
                return _CORPUS
            if isinstance(expression.func, ast.Attribute):
                owner_kind = self._kind(expression.func.value, local, function)
                if owner_kind == _CORPUS and name in _CORPUS_METHODS:
                    return _CORPUS
                if owner_kind == _CORPUS and name == "one":
                    return _ROW
            if name in _COPY_CALLS and expression.args:
                return self._kind(expression.args[0], local, function)
            if name == "next" and expression.args:
                source_kind = self._kind(expression.args[0], local, function)
                return _ROW if source_kind == _CORPUS else source_kind
            target = self._resolve_function(expression, function)
            if target is not None:
                return target.return_kind
            if name in {"decode_receipts", "parse_receipts", "receipt_rows"}:
                return _CORPUS
            return _NONE
        if isinstance(expression, (ast.ListComp, ast.SetComp, ast.GeneratorExp)):
            comprehension_overrides: dict[str, int] = {}
            has_corpus_source = False
            for generator in expression.generators:
                source_kind = self._kind(
                    generator.iter,
                    local,
                    function,
                    comprehension_overrides,
                )
                bound_kind = _ROW if source_kind == _CORPUS else _NONE
                if isinstance(generator.target, ast.Name):
                    comprehension_overrides[generator.target.id] = bound_kind
                has_corpus_source = has_corpus_source or source_kind == _CORPUS
            element_kind = self._kind(
                expression.elt,
                local,
                function,
                comprehension_overrides,
            )
            return _CORPUS if has_corpus_source and element_kind == _ROW else _NONE
        if isinstance(expression, ast.DictComp):
            return _NONE
        if isinstance(expression, (ast.List, ast.Tuple, ast.Set)):
            kinds = [self._kind(item, local, function) for item in expression.elts]
            if _CORPUS in kinds or _ROW in kinds:
                return _CORPUS
            return _NONE
        if isinstance(expression, ast.BinOp) and isinstance(expression.op, ast.Add):
            return max(
                self._kind(expression.left, local, function),
                self._kind(expression.right, local, function),
            )
        if isinstance(expression, ast.IfExp):
            return max(
                self._kind(expression.body, local, function),
                self._kind(expression.orelse, local, function),
            )
        if isinstance(expression, ast.Subscript):
            base_kind = self._kind(expression.value, local, function)
            if base_kind == _CORPUS:
                return _CORPUS if isinstance(expression.slice, ast.Slice) else _ROW
            return _NONE
        return _NONE

    def _assign_target(
        self,
        target: ast.AST,
        kind: int,
        environment: dict[str, int],
        function: _Function | None,
    ) -> bool:
        changed = False
        if isinstance(target, ast.Name):
            if kind > environment.get(target.id, _NONE):
                environment[target.id] = kind
                changed = True
        elif isinstance(target, ast.Attribute):
            key = self._attribute_key(target, function)
            assigned_kind = _CORPUS if target.attr == "receipts" else kind
            if assigned_kind > self.attribute_kinds.get(key, _NONE):
                self.attribute_kinds[key] = assigned_kind
                changed = True
        elif isinstance(target, (ast.Tuple, ast.List)):
            for item in target.elts:
                changed |= self._assign_target(item, kind, environment, function)
        return changed

    def _propagate_call(
        self,
        call: ast.Call,
        environment: Mapping[str, int],
        function: _Function | None,
    ) -> bool:
        target = self._resolve_function(call, function)
        if target is None:
            return False
        target_environment = self.environments[target.qualname]
        parameters = [
            *target.node.args.posonlyargs,
            *target.node.args.args,
        ]
        if isinstance(call.func, ast.Attribute) and parameters and parameters[0].arg in {"self", "cls"}:
            parameters = parameters[1:]
        changed = False
        for argument, parameter in zip(call.args, parameters):
            kind = self._kind(argument, environment, function)
            if kind > target_environment.get(parameter.arg, _NONE):
                target_environment[parameter.arg] = kind
                changed = True
        return changed

    def solve(self) -> None:
        scopes: list[tuple[str, ast.AST, _Function | None]] = [
            ("<module>", self.tree, None)
        ] + [
            (function.qualname, function.node, function)
            for function in self.functions.values()
        ]
        changed = True
        while changed:
            changed = False
            for scope_name, scope, function in scopes:
                environment = self.environments[scope_name]
                for node in _scope_nodes(scope):
                    if isinstance(node, ast.Assign):
                        kind = self._kind(node.value, environment, function)
                        for target in node.targets:
                            changed |= self._assign_target(
                                target, kind, environment, function
                            )
                    elif isinstance(node, ast.AnnAssign):
                        kind = max(
                            self._kind(node.value, environment, function),
                            _CORPUS if _annotation_is_corpus(node.annotation) else _NONE,
                        )
                        changed |= self._assign_target(
                            node.target, kind, environment, function
                        )
                    elif isinstance(node, (ast.For, ast.AsyncFor)):
                        source_kind = self._kind(node.iter, environment, function)
                        changed |= self._assign_target(
                            node.target,
                            _ROW if source_kind == _CORPUS else _NONE,
                            environment,
                            function,
                        )
                    elif isinstance(node, ast.Call):
                        changed |= self._propagate_call(node, environment, function)
                    elif isinstance(node, ast.Return) and function is not None:
                        kind = self._kind(node.value, environment, function)
                        if kind > function.return_kind:
                            function.return_kind = kind
                            changed = True

    def findings(self) -> list[ProvenanceFinding]:
        self.solve()
        findings: list[ProvenanceFinding] = []
        scopes: list[tuple[str, ast.AST, _Function | None]] = [
            ("<module>", self.tree, None)
        ] + [
            (function.qualname, function.node, function)
            for function in self.functions.values()
        ]
        for scope_name, scope, function in scopes:
            environment = self.environments[scope_name]
            for node in _scope_nodes(scope):
                if isinstance(node, ast.Subscript) and self._kind(
                    node.value, environment, function
                ) == _CORPUS:
                    findings.append(
                        ProvenanceFinding(
                            self.path,
                            node.lineno,
                            node.col_offset,
                            "positional_receipt_access",
                            ast.unparse(node),
                        )
                    )
            if function is None or function.annotated:
                continue
            for node in _scope_nodes(scope):
                if not isinstance(node, ast.Return):
                    continue
                if self._kind(node.value, environment, function) != _CORPUS:
                    continue
                if _explicitly_wrapped_return(node.value):
                    continue
                findings.append(
                    ProvenanceFinding(
                        self.path,
                        node.lineno,
                        node.col_offset,
                        "unwrapped_receipt_return",
                        function.qualname,
                    )
                )
        return sorted(set(findings))


def analyze_sources(sources: Mapping[str, str]) -> list[ProvenanceFinding]:
    findings: list[ProvenanceFinding] = []
    for path, source in sources.items():
        findings.extend(_ModuleAnalyzer(path, source).findings())
    return sorted(set(findings))


def analyze_paths(paths: Iterable[Path]) -> list[ProvenanceFinding]:
    return analyze_sources(
        {
            str(path): path.read_text(encoding="utf-8")
            for path in sorted(paths, key=lambda item: str(item))
        }
    )


__all__ = ["ProvenanceFinding", "analyze_paths", "analyze_sources"]
