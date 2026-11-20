#!/usr/bin/env python3
"""Compare RL-182 protected source bytes and public-safe prompt hash projections."""

import argparse
import ast
import hashlib
from io import BytesIO
import json
import os
from pathlib import Path
import re
import subprocess
import symtable
import tokenize
import unicodedata
import warnings


SCORER = "joulewise/align/apple/rl176.py"
MODULES = (SCORER, "joulewise/align/apple/rl176_phases.py")
LEVEL = "S_SUPERIORITY_ALPHA"
PROTECTED = (
    LEVEL, "_tail_test", "_holm", "_decode_design", "_decode_rows",
    "_residual_scores", "_s_rank", "_q_energies",
)
PROTECTED_FUNCTIONS = frozenset(PROTECTED) - {LEVEL}
FUNCTION = (ast.FunctionDef, ast.AsyncFunctionDef)
PHYSICAL_LINES = re.compile(rb"(?<=\n)|(?<=\r)(?!\n)")
NAMESPACE_APIS = frozenset({
    "exec", "eval", "globals", "locals", "vars", "getattr", "setattr", "delattr",
    "__import__", "__builtins__", "__getattribute__", "__setattr__", "__delattr__",
})
NAMESPACE_ATTRIBUTES = NAMESPACE_APIS | {
    "modules", "__dict__", "__globals__", "f_globals", "f_locals", "import_module",
}


class InvalidInput(ValueError):
    """An input could not support a complete comparison."""


def git(repo, *args):
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(GIT_NO_LAZY_FETCH="1", GIT_ALLOW_PROTOCOL="", GIT_OPTIONAL_LOCKS="0")
    return subprocess.check_output([
        "git", "--no-pager", "--no-replace-objects", "--literal-pathspecs", "-C", repo, *args,
    ], env=env, stderr=subprocess.DEVNULL)


def read_revision(repo, label, commit, oid_pattern):
    if not oid_pattern.fullmatch(commit):
        raise InvalidInput(f"{label} requires a full commit ID")
    commit = commit.lower()
    try:
        if git(repo, "cat-file", "-t", commit) != b"commit\n":
            raise InvalidInput(f"{label} ID is not a commit")
        entries = git(repo, "ls-tree", "-rz", "--full-tree", commit, "--", *MODULES)
    except (OSError, subprocess.CalledProcessError):
        raise InvalidInput(f"{label} commit or tree is unreadable") from None

    modules = {}
    sources = {}
    for entry in entries.split(b"\0")[:-1]:
        metadata, _, pathname = entry.partition(b"\t")
        path = os.fsdecode(pathname)
        if path not in MODULES or path in modules:
            raise InvalidInput(f"{label} tree has ambiguous module entries")
        mode, kind, oid = metadata.decode("ascii").split()
        if kind != "blob" or mode not in ("100644", "100755"):
            raise InvalidInput(f"{label} {path} requires a regular Git blob")
        try:
            if git(repo, "cat-file", "-t", oid) != b"blob\n":
                raise InvalidInput(f"{label} {path} requires a regular Git blob")
            sources[path] = git(repo, "cat-file", "blob", oid)
        except (OSError, subprocess.CalledProcessError):
            raise InvalidInput(f"{label} {path} blob is unreadable") from None
        modules[path] = {"blob": oid, "mode": mode}
    for path in MODULES:
        if path not in modules:
            raise InvalidInput(f"{label} {path} is missing")
    return {"commit": commit, "modules": modules}, sources


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InvalidInput("duplicate prompt projection key")
        result[key] = value
    return result


def read_prompts(path, label):
    try:
        prompts = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_keys)
    except InvalidInput:
        raise InvalidInput(f"{label} has a duplicate prompt projection key") from None
    except (OSError, ValueError, RecursionError):
        raise InvalidInput(f"{label} prompt projection is unreadable or malformed") from None
    if not isinstance(prompts, dict) or not prompts:
        raise InvalidInput(f"{label} prompt projection requires a nonempty JSON object")
    for name, digest in prompts.items():
        if (not name.strip()
                or any(unicodedata.category(char) in ("Cc", "Cs") for char in name)
                or not isinstance(digest, str)
                or not re.fullmatch(r"[0-9a-fA-F]{64}", digest)):
            raise InvalidInput(f"{label} prompt projection requires identifier-to-SHA-256 entries")
    return {name: digest.lower() for name, digest in prompts.items()}


class ModuleBindings(ast.NodeVisitor):
    """Record explicit bindings executed in the module's lexical scope."""

    def __init__(self):
        self.bindings = {name: [] for name in PROTECTED}

    def record(self, name, node):
        if name in self.bindings:
            self.bindings[name].append(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, (ast.Store, ast.Del)):
            self.record(node.id, node)

    def visit_FunctionDef(self, node):
        self.record(node.name, node)
        for child in ast.iter_child_nodes(node):
            if child not in node.body:
                self.visit(child)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node):
        self.visit_FunctionDef(node)

    def visit_Lambda(self, node):
        self.visit(node.args)

    def visit_comprehension(self, node):
        # The iteration target is local to the comprehension.
        self.visit(node.iter)
        for condition in node.ifs:
            self.visit(condition)

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name == "*":
                raise InvalidInput("ambiguous module wildcard import")
            self.record(alias.asname or alias.name.split(".")[0], node)

    visit_ImportFrom = visit_Import

    def visit_ExceptHandler(self, node):
        self.record(node.name, node)
        self.generic_visit(node)

    def visit_MatchAs(self, node):
        self.record(node.name, node)
        self.generic_visit(node)

    visit_MatchStar = visit_MatchAs

    def visit_MatchMapping(self, node):
        self.record(node.rest, node)
        self.generic_visit(node)


def reject_dynamic_namespace(module):
    """Refuse reflective access and escapes of mutable protected callable objects."""
    nodes = tuple(ast.walk(module))
    direct_callees = {node.func for node in nodes if isinstance(node, ast.Call)}
    ambiguous_access = False
    for node in nodes:
        references = ()
        if isinstance(node, ast.Attribute):
            if isinstance(node.ctx, (ast.Store, ast.Del)) and node.attr in PROTECTED:
                raise InvalidInput(f"{node.attr} has an ambiguous namespace write")
            if isinstance(node.ctx, ast.Load):
                references = (node.attr,)
            if node.attr in NAMESPACE_ATTRIBUTES:
                ambiguous_access = True
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            references = (node.id,)
            if node.id in NAMESPACE_APIS:
                ambiguous_access = True
        elif isinstance(node, (ast.ImportFrom, ast.MatchClass)):
            references = (tuple(alias.name for alias in node.names)
                          if isinstance(node, ast.ImportFrom) else node.kwd_attrs)
            if any(name in NAMESPACE_ATTRIBUTES for name in references):
                ambiguous_access = True

        # A first-class reference can mutate a function through aliases,
        # containers or callees. A direct invocation does not expose its identity.
        if node not in direct_callees:
            for name in references:
                if name in PROTECTED_FUNCTIONS:
                    raise InvalidInput(f"{name} has ambiguous callable namespace access")
    if ambiguous_access:
        raise InvalidInput("ambiguous dynamic module namespace access")


def reject_nested_global_writes(scope):
    for child in scope.get_children():
        for name in PROTECTED:
            if name in child.get_identifiers():
                symbol = child.lookup(name)
                if symbol.is_declared_global() and (symbol.is_assigned() or symbol.is_imported()):
                    raise InvalidInput(f"{name} has a nested global binding")
        reject_nested_global_writes(child)


def module_decorator_lines(source):
    """Locate module-scope decorator tokens at the start of logical lines."""
    # Tokenize with universal newlines and slice the original bytes separately.
    stream = BytesIO(re.sub(rb"\r\n?", b"\n", source))
    decorators = set()
    depth = 0
    at_start = True
    for token in tokenize.tokenize(stream.readline):
        if token.type == tokenize.INDENT:
            depth += 1
        elif token.type == tokenize.DEDENT:
            depth -= 1
        elif token.type == tokenize.NEWLINE:
            at_start = True
        elif token.type not in (tokenize.ENCODING, tokenize.NL, tokenize.COMMENT):
            if at_start and depth == 0 and token.exact_type == tokenize.AT:
                decorators.add(token.start[0] - 1)
            at_start = False
    return decorators


def source_span(lines, statement, previous_end, next_start, decorator_lines):
    start = statement.lineno - 1
    if isinstance(statement, FUNCTION) and statement.decorator_list:
        starts = sorted(line for line in decorator_lines if previous_end <= line < start)
        if len(starts) != len(statement.decorator_list):
            raise InvalidInput("protected decorator boundaries are ambiguous")
        start = starts[0]
    end = statement.end_lineno
    if start < previous_end or end >= next_start:
        raise InvalidInput("protected binding shares a physical line with another statement")
    # AST ends at the last token. Keep complete physical lines and immediately
    # following indented body comments, including blank lines between them.
    if isinstance(statement, FUNCTION):
        for index in range(end, next_start - 1):
            line = lines[index].rstrip(b"\r\n")
            content = line.lstrip(b" \t\f")
            if not content:
                continue
            if not content.startswith(b"#") or content == line:
                break
            end = index + 1
    return b"".join(lines[start:end])


def protected_sources(source):
    try:
        with warnings.catch_warnings():
            # Parser diagnostics can contain source text. Report a fixed error
            # for rejected input and leave warnings out of the comparison.
            warnings.simplefilter("ignore")
            module = ast.parse(source, filename="<scorer>")
            compile(module, "<scorer>", "exec", dont_inherit=True)
            scopes = symtable.symtable(source, "<scorer>", "exec")
            decorator_lines = module_decorator_lines(source)
    except (SyntaxError, ValueError, RecursionError, tokenize.TokenError):
        raise InvalidInput("scorer is not valid Python source") from None
    bindings = ModuleBindings()
    bindings.visit(module)
    reject_nested_global_writes(scopes)
    reject_dynamic_namespace(module)

    lines = PHYSICAL_LINES.split(source.removeprefix(b"\xef\xbb\xbf"))
    definitions = {}
    previous_end = 0
    for index, statement in enumerate(module.body):
        if isinstance(statement, FUNCTION):
            name, binding = statement.name, statement
        elif (isinstance(statement, ast.Assign) and len(statement.targets) == 1
              and isinstance(statement.targets[0], ast.Name)):
            binding = statement.targets[0]
            name = LEVEL if binding.id == LEVEL else None
        elif (isinstance(statement, ast.AnnAssign) and statement.simple and statement.value is not None
              and isinstance(statement.target, ast.Name)):
            binding = statement.target
            name = LEVEL if binding.id == LEVEL else None
        else:
            name = None
        if name in bindings.bindings and (name != LEVEL or not isinstance(statement, FUNCTION)):
            if bindings.bindings[name] != [binding]:
                raise InvalidInput(f"{name} has multiple or rebound module bindings")
            following = module.body[index + 1:index + 2]
            next_start = following[0].lineno if following else len(lines) + 1
            try:
                definitions[name] = source_span(lines, statement, previous_end, next_start, decorator_lines)
            except InvalidInput:
                raise InvalidInput(f"{name} has an ambiguous source span") from None
        previous_end = statement.end_lineno

    missing = [name for name in PROTECTED if name not in definitions]
    if missing:
        raise InvalidInput("missing or unsupported module binding: " + ", ".join(missing))
    return definitions


def changed_hashes(w1, c1):
    return {
        name: {"w1": w1.get(name), "c1": c1.get(name)}
        for name in sorted(w1.keys() | c1.keys())
        if w1.get(name) != c1.get(name)
    }


def compare(args):
    try:
        object_format = git(args.repo, "rev-parse", "--show-object-format").strip()
        oid_length = {b"sha1": 40, b"sha256": 64}[object_format]
    except (OSError, subprocess.CalledProcessError, KeyError):
        raise InvalidInput("local Git repository or object format is unreadable") from None

    oid_pattern = re.compile(rf"[0-9a-fA-F]{{{oid_length}}}")
    w1, w1_sources = read_revision(args.repo, "W1", args.w1_commit, oid_pattern)
    c1, c1_sources = read_revision(args.repo, "C1", args.c1_commit, oid_pattern)
    scorer_equal = w1_sources[SCORER] == c1_sources[SCORER]
    files_for_review = [path for path in MODULES
                        if w1["modules"][path] != c1["modules"][path]
                        or w1_sources[path] != c1_sources[path]]

    protected_changes = {}
    try:
        old = protected_sources(w1_sources[SCORER])
        new = old if scorer_equal else protected_sources(c1_sources[SCORER])
    except RecursionError:
        raise InvalidInput("scorer source nesting is too deep") from None
    for name in PROTECTED:
        if old[name] != new[name]:
            protected_changes[name] = {
                "w1": hashlib.sha256(old[name]).hexdigest(),
                "c1": hashlib.sha256(new[name]).hexdigest(),
            }
    prompt_changes = changed_hashes(read_prompts(args.w1_prompts, "W1"), read_prompts(args.c1_prompts, "C1"))
    return {
        "revisions": {"w1": w1, "c1": c1},
        "files_for_review": files_for_review,
        "protected_changes": protected_changes,
        "prompt_changes": prompt_changes,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path, help="local public-code Git repository")
    for label in ("w1", "c1"):
        parser.add_argument(f"--{label}-commit", required=True, help="full commit ID")
        parser.add_argument(f"--{label}-prompts", required=True, type=Path,
                            help="public-safe JSON object mapping prompt identifiers to SHA-256")
    args = parser.parse_args()
    try:
        result = compare(args)
    except InvalidInput as error:
        print(json.dumps({"error": str(error)}))
        return 2
    print(json.dumps(result, indent=2))
    return int(bool(result["protected_changes"] or result["prompt_changes"]))


if __name__ == "__main__":
    raise SystemExit(main())
