#!/usr/bin/env python3
"""Compare RL-182 protected source bytes and public-safe prompt hash projections."""

import argparse
import ast
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from fractions import Fraction
import hashlib
import importlib
from inspect import signature
from io import BytesIO
from itertools import accumulate
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import symtable
import sys
from tempfile import TemporaryDirectory
import tokenize
from types import CellType, CodeType, FunctionType, ModuleType, SimpleNamespace
import unicodedata
import warnings


SCORER = "joulewise/align/apple/rl176.py"
MODULES = (SCORER, "joulewise/align/apple/rl176_phases.py")
ENTRY = "scripts/align_v4_series_release.py"
IMPORTABLE_SUFFIXES = {".py", ".pyc", ".pyo", ".so", ".pyd", ".zip", ".whl"}
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


def git(repo, *args, data=None):
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(GIT_NO_LAZY_FETCH="1", GIT_ALLOW_PROTOCOL="", GIT_OPTIONAL_LOCKS="0")
    return subprocess.check_output([
        "git", "--no-pager", "--no-replace-objects", "--literal-pathspecs", "-C", repo, *args,
    ], input=data, env=env, stderr=subprocess.DEVNULL)


def read_revision(repo, label, commit, oid_pattern):
    if not oid_pattern.fullmatch(commit):
        raise InvalidInput(f"{label} requires a full commit ID")
    commit = commit.lower()
    try:
        if git(repo, "cat-file", "-t", commit) != b"commit\n":
            raise InvalidInput(f"{label} ID is not a commit")
        entries = git(repo, "ls-tree", "-rz", "--full-tree", commit)
    except (OSError, subprocess.CalledProcessError):
        raise InvalidInput(f"{label} commit or tree is unreadable") from None

    tree = {}
    for entry in entries.split(b"\0")[:-1]:
        metadata, _, pathname = entry.partition(b"\t")
        path = os.fsdecode(pathname)
        if path in tree:
            raise InvalidInput(f"{label} tree has ambiguous entries")
        mode, kind, oid = metadata.decode("ascii").split()
        tree[path] = {"blob": oid, "mode": mode, "kind": kind}
    modules = {}
    sources = {}
    errors = []
    for path in MODULES:
        record = tree.get(path)
        if record is None:
            modules[path] = None
            errors.append(f"{label} {path} is missing")
        else:
            modules[path] = {"blob": record["blob"], "mode": record["mode"]}
            if not regular_source(record):
                errors.append(f"{label} {path} requires a regular Git blob")
                continue
            oid = record["blob"]
            try:
                if git(repo, "cat-file", "-t", oid) != b"blob\n":
                    errors.append(f"{label} {path} requires a regular Git blob")
                    continue
                sources[path] = git(repo, "cat-file", "blob", oid)
            except (OSError, subprocess.CalledProcessError):
                errors.append(f"{label} {path} blob is unreadable")
    return {"commit": commit, "modules": modules}, tree, sources, errors


def regular_source(entry):
    return entry is not None and entry["kind"] == "blob" and entry["mode"] in ("100644", "100755")


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
    return start, end


def protected_regions(source):
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

    contents = source.removeprefix(b"\xef\xbb\xbf")
    lines = PHYSICAL_LINES.split(contents)
    offsets = tuple(accumulate(map(len, lines), initial=len(source) - len(contents)))
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
                start, end = source_span(lines, statement, previous_end, next_start, decorator_lines)
                definitions[name] = offsets[start], offsets[end]
            except InvalidInput:
                raise InvalidInput(f"{name} has an ambiguous source span") from None
        previous_end = statement.end_lineno

    missing = [name for name in PROTECTED if name not in definitions]
    if missing:
        raise InvalidInput("missing or unsupported module binding: " + ", ".join(missing))
    return definitions


def protected_sources(source):
    return {name: source[start:end] for name, (start, end) in protected_regions(source).items()}


def changed_hashes(w1, c1):
    return {
        name: {"w1": w1.get(name), "c1": c1.get(name)}
        for name in sorted(w1.keys() | c1.keys())
        if w1.get(name) != c1.get(name)
    }


def importable_paths(tree):
    # The checkout root is on sys.path. Static imports are covered by keeping
    # the entire repository import space, including dynamic import candidates.
    # Native and archived modules participate in the byte freeze as metadata.
    return {path for path in tree if Path(path).suffix in IMPORTABLE_SUFFIXES} | {ENTRY, *MODULES}


def closure_changes(w1_tree, c1_tree, scopes):
    # Only Python source is projected. A read guarded by is_file() can be
    # absent from both import traces when its tracked resource is unstaged.
    # Freeze remaining candidates by Git metadata without opening their blobs.
    return {
        path: {
            "w1": w1_tree.get(path), "c1": c1_tree.get(path),
            "scope": next((name for name, paths in scopes.items() if path in paths),
                          "potential-import-resource"),
        }
        for path in sorted(w1_tree.keys() | c1_tree.keys())
        if w1_tree.get(path) != c1_tree.get(path)
    }


def project_python_sources(repo, commit, directory):
    """Materialize only regular Python source blobs from the requested Git tree."""
    files = {}
    entries = git(repo, "ls-tree", "-rz", "--full-tree", commit)
    for entry in entries.split(b"\0")[:-1]:
        metadata, path = entry.split(b"\t", 1)
        if not path.endswith(b".py"):
            continue
        mode, kind, oid = metadata.split()
        parts = os.fsdecode(path).split("/")
        if any(part in ("", ".", "..") for part in parts) or path in files:
            raise InvalidInput("runtime projection contains an ambiguous source path")
        if kind != b"blob" or mode not in (b"100644", b"100755"):
            raise InvalidInput("runtime projection requires regular Python source blobs")
        files[path] = oid
    if os.fsencode(ENTRY) not in files:
        raise InvalidInput("runtime release entry point is missing")

    batch = BytesIO(git(repo, "cat-file", "--batch", data=b"\n".join(files.values()) + b"\n"))
    for path, oid in files.items():
        header = batch.readline().split()
        if len(header) != 3 or header[:2] != [oid, b"blob"] or not header[2].isdigit():
            raise InvalidInput("runtime source blob is unreadable")
        size = int(header[2])
        blob = batch.read(size)
        if len(blob) != size or batch.read(1) != b"\n":
            raise InvalidInput("runtime source blob is incomplete")
        destination = directory / os.fsdecode(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("xb") as output:
            output.write(blob)


def static_import_closure(root):
    """Resolve literal imports transitively within the source projection."""
    closure = set()
    pending = set()

    def queue(parts):
        for index in range(1, len(parts) + 1):
            package = "/".join(parts[:index])
            pending.update((package + "/__init__.py", package + ".py"))

    for path in (ENTRY, SCORER):
        queue(path.removesuffix(".py").split("/"))

    while pending:
        path = pending.pop()
        if path in closure or not (root / path).is_file():
            continue
        closure.add(path)
        try:
            syntax = ast.parse((root / path).read_bytes())
        except (SyntaxError, ValueError, RecursionError):
            continue  # All potential code files are still frozen by the parent.
        for node in ast.walk(syntax):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    queue(alias.name.split("."))
            elif isinstance(node, ast.ImportFrom):
                package = path.split("/")[:-1]
                if node.level > len(package):
                    continue
                prefix = package[:len(package) - node.level + 1] if node.level else []
                source = prefix + (node.module.split(".") if node.module else [])
                queue(source)
                for alias in node.names:
                    if alias.name != "*":
                        queue([*source, alias.name])
    return closure


CODE_FIELDS = (
    "co_code", "co_consts", "co_names", "co_varnames", "co_freevars", "co_cellvars",
    "co_name", "co_qualname", "co_argcount", "co_posonlyargcount", "co_kwonlyargcount",
    "co_nlocals", "co_stacksize", "co_flags", "co_firstlineno", "co_linetable", "co_exceptiontable",
)
FUNCTION_FIELDS = (
    "__code__", "__defaults__", "__kwdefaults__", "__closure__", "__dict__",
    "__annotations__", "__module__", "__name__", "__qualname__", "__doc__", "__type_params__",
)


class RuntimeIdentity:
    """Encode supported effective Python state without invoking its methods."""

    def __init__(self, root):
        self.root = root
        self.source_prefix = str(root) + os.sep
        self.seen = {}

    def encode(self, value):
        kind = type(value)
        if value is None or value is Ellipsis or value is NotImplemented:
            return [kind.__name__]
        if kind in (bool, int, str):
            return [kind.__name__, value]
        if kind is bytes:
            return ["bytes", value.hex()]
        if kind is Fraction:
            return ["Fraction", value.numerator, value.denominator]
        if kind is type and value in (bool, int, float, complex, str, bytes, tuple, list, dict, set, frozenset, type(None)):
            return ["builtin-type", value.__name__]

        identity = id(value)
        if identity in self.seen:
            return ["reference", self.seen[identity][0]]
        # Retain the object so its ID cannot be reused while encoding.
        self.seen[identity] = len(self.seen), value
        if kind is float:
            return ["float", struct.pack("!d", value).hex()]
        if kind is complex:
            return ["complex", struct.pack("!dd", value.real, value.imag).hex()]
        if kind is CodeType:
            filename = value.co_filename
            if filename.startswith(self.source_prefix):
                filename = "/source/" + filename.removeprefix(self.source_prefix)
            return ["code", filename, *[self.encode(getattr(value, field)) for field in CODE_FIELDS]]
        if kind is FunctionType:
            return ["function", *[self.encode(getattr(value, field)) for field in FUNCTION_FIELDS]]
        if kind is CellType:
            try:
                contents = value.cell_contents
            except ValueError:
                return ["empty-cell"]
            return ["cell", self.encode(contents)]
        if kind in (list, tuple):
            return [kind.__name__, [self.encode(item) for item in value]]
        if kind is dict:
            return ["dict", [[self.encode(key), self.encode(item)] for key, item in value.items()]]
        if kind in (set, frozenset):
            ordered = {}
            for item in value:
                sort_identity = RuntimeIdentity(self.root)
                sort_identity.seen = self.seen.copy()
                key = json.dumps(sort_identity.encode(item))
                if key in ordered:
                    raise InvalidInput("ambiguous ordering of runtime set members")
                ordered[key] = item
            return [kind.__name__, [self.encode(ordered[key]) for key in sorted(ordered)]]
        raise InvalidInput("unsupported runtime state")


def oracle_inputs():
    """Frozen invented input cases. Construct mutable arguments anew per side."""
    def row(decode):
        return SimpleNamespace(context_tokens=3, prefill_tokens=2, decode_tokens=decode, turn=0, end_ns=2)

    turn = SimpleNamespace(index=0, start_ns=0, end_ns=2, first_token_ns=2)
    trace = SimpleNamespace(source="powermetrics", channel="gpu_power", unit="W",
                            t_ns=(0, 2), clock_domain="invented")
    episode = SimpleNamespace(power_traces=(trace,), turns=(turn,), hardware={}, flags=(), clock_domain="invented")
    with_trace = SimpleNamespace(episode=episode, s_rows=(row(1),))
    without_trace = SimpleNamespace(episode=SimpleNamespace(power_traces=()), s_rows=(row(1),))
    segment = SimpleNamespace(start_ns=2, end_ns=3, turn=0, kind="decode", energy=SimpleNamespace(joules=2.0))
    rows = {"a": ({"strata": 8}, Fraction(1, 40)), "b": ({"strata": 8}, Fraction(1, 20))}

    def rank_strata(count):
        return [("invented", 2.0, [1.0]) for _ in range(count)]

    def training(count):
        return {"held": [((1.0,), 8.0, 0.0)],
                "training": [((1.0,), float(index), 0.0) for index in range(count)]}

    return {
        "_decode_design": [(label, (row(value),), {}) for label, value in (
            ("zero", 0), ("one", 1), ("nan", float("nan")), ("infinity", float("inf")),
        )],
        "_decode_rows": [("no-trace", (without_trace,), {}), ("stamp-at-end", (with_trace,), {})],
        "_residual_scores": [(label, (value,), {"edges_per_row": 3}) for label, value in (
            ("empty", {}), ("five-training", training(5)), ("six-training", training(6)),
        )],
        "_tail_test": [(label, (value,), {}) for label, value in (
            ("empty", []), ("tie", [(1.0, [1.0, 1.0])]), ("infinity", [(float("inf"), [0.0, 1.0])]),
        )],
        "_s_rank": [(label, (value,), {"decide": True}) for label, value in (
            ("empty", []), ("tie", [("invented", 1.0, [1.0])]),
            ("above-level", rank_strata(6)), ("below-level", rank_strata(7)),
        )],
        "_holm": [("empty", ({},), {"frozen": True}), ("boundary", (rows,), {"frozen": True})],
        "_q_energies": [
            ("empty", (SimpleNamespace(turns=()), (), None, None), {}),
            ("no-trace-with-stamp", (episode, (), None, None), {}),
            ("stamp-at-segment-start", (episode, (segment,), trace, None), {}),
        ],
    }


def oracle_outputs(namespace):
    table = {}
    if LEVEL in namespace:
        table[LEVEL] = {"value": namespace[LEVEL]}
    for name, cases in oracle_inputs().items():
        function = namespace.get(name)
        if type(function) is not FunctionType:
            continue
        try:
            parameters = signature(function, follow_wrapped=False)
        except (TypeError, ValueError):
            continue
        results = {}
        for label, args, kwargs in [("defaults", (), {}), *cases]:
            try:
                parameters.bind(*args, **kwargs)
            except TypeError:
                continue
            args, kwargs = deepcopy((args, kwargs))
            try:
                value = function(*args, **kwargs)
                results[label] = (value, args[0]) if name == "_holm" and args else value
            except (Exception, SystemExit, KeyboardInterrupt) as error:
                results[label] = {"raised": (type(error).__module__, type(error).__qualname__)}
        table[name] = results
    return table


def identity_hash(value, root):
    return hashlib.sha256(json.dumps(RuntimeIdentity(root).encode(value)).encode("ascii")).hexdigest()


def runtime_worker(source_root):
    """Import the release module inside the isolated worker and emit only evidence."""
    if sys.version_info[:2] != (3, 13):
        raise InvalidInput("runtime requires Python 3.13")
    root = Path(source_root).resolve()
    static_paths = static_import_closure(root)
    import_reads = set()
    measuring_import = True

    def observe(event, args):
        if measuring_import and event == "open" and isinstance(args[0], (bytes, str)):
            path = os.path.abspath(os.fsdecode(args[0]))
            prefix = str(root) + os.sep
            if path.startswith(prefix):
                import_reads.add(path.removeprefix(prefix))

    sys.path.insert(0, str(root))
    fingerprints = {}
    oracle = {}
    unresolved = []
    oracle_unresolved = []
    loaded = False
    with open(os.devnull, "w", encoding="utf-8") as silent, redirect_stdout(silent), redirect_stderr(silent):
        sys.addaudithook(observe)
        try:
            importlib.import_module("scripts.align_v4_series_release")
            scorer = sys.modules.get("joulewise.align.apple.rl176")
            loaded = type(scorer) is ModuleType and Path(scorer.__file__).resolve() == root / SCORER
        except (Exception, SystemExit, KeyboardInterrupt):
            loaded = False
        finally:
            measuring_import = False

        if loaded:
            namespace = vars(scorer).copy()
            for name in PROTECTED:
                try:
                    value = namespace[name]
                    if name in PROTECTED_FUNCTIONS and type(value) is not FunctionType:
                        raise InvalidInput("unsupported protected callable")
                    fingerprints[name] = identity_hash(value, root)
                except (KeyError, AttributeError, ValueError, TypeError, RecursionError):
                    unresolved.append(name)
            try:
                table = oracle_outputs(namespace)
            except (AttributeError, ValueError, TypeError, RecursionError):
                table = {}
            for name in PROTECTED:
                outcomes = table.get(name, {})
                hashes = {}
                for label, value in outcomes.items():
                    try:
                        hashes[label] = identity_hash(value, root)
                    except (AttributeError, ValueError, TypeError, RecursionError):
                        oracle_unresolved.append(f"{name}/{label}")
                if not outcomes:
                    oracle_unresolved.append(name)
                oracle[name] = hashes

    print(json.dumps({"loaded": loaded, "fingerprints": fingerprints, "unresolved": unresolved,
                      "oracle": oracle, "oracle_unresolved": oracle_unresolved,
                      "static_paths": sorted(static_paths), "import_reads": sorted(import_reads)}))


def isolated_identity(repo, commit, image, worker_source):
    with TemporaryDirectory(prefix="row10-source-") as name:
        directory = Path(name).resolve()
        code = directory / "source"
        code.mkdir()
        config = directory / "docker-config"
        config.mkdir()
        worker = directory / "worker.py"
        if any("," in str(path) for path in (worker, code)):
            raise InvalidInput("runtime staging path is incompatible with a bind mount")
        try:
            worker.write_bytes(worker_source)
            worker.chmod(0o444)
            project_python_sources(repo, commit, code)
            # The local temp directory remains private. The read-only mounts
            # are readable by the container user under a restrictive umask.
            code.chmod(0o755)
            for entry in code.rglob("*"):
                entry.chmod(0o755 if entry.is_dir() else 0o444)
            result = subprocess.run([
                "docker", "--host", "unix:///var/run/docker.sock", "--config", config, "run",
                "--rm", "--pull=never", "--network=none", "--read-only", "--ipc=none",
                "--cap-drop=ALL", "--security-opt=no-new-privileges", "--user=65534:65534",
                "--pids-limit=16", "--cpus=1", "--memory=256m", "--memory-swap=256m", "--log-driver=none",
                "--workdir=/source", "--mount", f"type=bind,src={code},dst=/source,readonly",
                "--mount", f"type=bind,src={worker},dst=/row10_worker.py,readonly",
                "--entrypoint=/usr/bin/timeout", image, "--kill-after=2s", "30s", "/usr/local/bin/python3",
                "-I", "-B", "-S", "-c", "import runpy, sys; runpy.run_path(sys.argv[1])['runtime_worker'](sys.argv[2])",
                "/row10_worker.py", "/source",
            ], env={"PATH": os.environ.get("PATH", os.defpath)}, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL, check=True, timeout=60)
            return read_runtime_result(result.stdout)
        except (OSError, subprocess.SubprocessError):
            raise InvalidInput("runtime isolation or release import failed") from None


def read_runtime_result(raw):
    invalid = InvalidInput("malformed runtime evidence")
    try:
        evidence = json.loads(raw, object_pairs_hook=unique_keys)
    except (ValueError, RecursionError):
        raise invalid from None
    keys = {"loaded", "fingerprints", "unresolved", "oracle", "oracle_unresolved", "static_paths", "import_reads"}
    if not isinstance(evidence, dict) or evidence.keys() != keys or type(evidence["loaded"]) is not bool:
        raise invalid

    def validate_digests(mapping, allowed):
        return (isinstance(mapping, dict) and allowed(mapping)
                and all(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value)
                        for value in mapping.values()))

    if not validate_digests(evidence["fingerprints"], lambda row: row.keys() <= set(PROTECTED)):
        raise invalid
    if (not isinstance(evidence["oracle"], dict) or not evidence["oracle"].keys() <= set(PROTECTED)
            or any(not validate_digests(row, lambda cases: all(re.fullmatch(r"[a-z0-9-]{1,48}", case)
                                                             for case in cases))
                   for row in evidence["oracle"].values())):
        raise invalid
    for key in ("unresolved", "oracle_unresolved", "static_paths", "import_reads"):
        if not isinstance(evidence[key], list) or any(not isinstance(value, str) for value in evidence[key]):
            raise invalid
    if any(name not in PROTECTED for name in evidence["unresolved"]):
        raise invalid
    if any(label.split("/", 1)[0] not in PROTECTED or not re.fullmatch(r"[A-Za-z0-9_/-]{1,80}", label)
           for label in evidence["oracle_unresolved"]):
        raise invalid
    identities = set(evidence["fingerprints"])
    unresolved = set(evidence["unresolved"])
    oracle_unresolved = {label.split("/", 1)[0] for label in evidence["oracle_unresolved"]}
    if evidence["loaded"]:
        if (identities & unresolved or identities | unresolved != set(PROTECTED)
                or evidence["oracle"].keys() != set(PROTECTED)
                or any(not cases and name not in oracle_unresolved for name, cases in evidence["oracle"].items())):
            raise invalid
    elif identities or unresolved or evidence["oracle"] or oracle_unresolved:
        raise invalid
    return evidence


def compare(args):
    try:
        object_format = git(args.repo, "rev-parse", "--show-object-format").strip()
        oid_length = {b"sha1": 40, b"sha256": 64}[object_format]
    except (OSError, subprocess.CalledProcessError, KeyError):
        raise InvalidInput("local Git repository or object format is unreadable") from None

    oid_pattern = re.compile(rf"[0-9a-fA-F]{{{oid_length}}}")
    w1, old_tree, old_sources, w1_errors = read_revision(args.repo, "W1", args.w1_commit, oid_pattern)
    c1, new_tree, new_sources, c1_errors = read_revision(args.repo, "C1", args.c1_commit, oid_pattern)
    scopes = {"import-time-open": set(), "static-import": set(),
              "potential-module": importable_paths(old_tree) | importable_paths(new_tree)}
    result = {
        "mode": "static-only" if args.static_only else "static-and-runtime",
        "revisions": {"w1": w1, "c1": c1},
        "protected_changes": {},
        "prompt_changes": {},
    }
    errors = w1_errors + c1_errors

    source_regions = {}
    for side, label, sources in (("w1", "W1", old_sources), ("c1", "C1", new_sources)):
        if SCORER in sources:
            try:
                source_regions[side] = protected_sources(sources[SCORER])
            except (InvalidInput, RecursionError) as error:
                errors.append(f"{label} {error}")
    if source_regions.keys() == {"w1", "c1"}:
        for name in PROTECTED:
            old, new = source_regions["w1"][name], source_regions["c1"][name]
            if old != new:
                result["protected_changes"][name] = {
                    "w1": hashlib.sha256(old).hexdigest(), "c1": hashlib.sha256(new).hexdigest(),
                }
    try:
        result["prompt_changes"] = changed_hashes(
            read_prompts(args.w1_prompts, "W1"), read_prompts(args.c1_prompts, "C1")
        )
    except InvalidInput as error:
        errors.append(str(error))

    if not args.static_only:
        compare_runtime(args, w1, c1, old_tree, new_tree, result, scopes, errors)

    changed = closure_changes(old_tree, new_tree, scopes)
    result["closure_changes"] = changed
    result["files_for_review"] = list(changed)
    result["research_lead_review"] = [path for path in MODULES if path in changed]
    if errors:
        result["error"] = ". ".join(errors)
    return result


def compare_runtime(args, w1, c1, old_tree, new_tree, result, scopes, errors):
    result["runtime_changes"] = {}
    result["oracle_changes"] = {}
    if not args.runtime_image or not re.fullmatch(r"sha256:[0-9a-f]{64}", args.runtime_image):
        errors.append("runtime requires a preloaded Python 3.13 image ID")
        return
    try:
        worker_source = Path(__file__).read_bytes()
    except OSError:
        errors.append("runtime worker source is unreadable")
        return

    available = {}
    tracked = old_tree.keys() | new_tree.keys()
    for side, label, revision, tree in (("w1", "W1", w1, old_tree), ("c1", "C1", c1, new_tree)):
        try:
            evidence = isolated_identity(args.repo, revision["commit"], args.runtime_image, worker_source)
        except InvalidInput as error:
            errors.append(f"{label} {error}")
            continue
        observed = tracked.intersection(evidence["import_reads"])
        scopes["import-time-open"].update(observed)
        scopes["static-import"].update(tracked.intersection(evidence["static_paths"]))
        unprojected = sorted(path for path in observed
                             if Path(path).suffix != ".py" or not regular_source(tree.get(path)))
        if unprojected:
            errors.append(f"{label} unresolved import-time file " + ", ".join(unprojected))
        if not evidence["loaded"]:
            errors.append(f"{label} release import or scorer identity failed")
            continue
        available[side] = evidence
        if evidence["unresolved"]:
            errors.append(f"{label} unresolved runtime identity for " + ", ".join(evidence["unresolved"]))
        if evidence["oracle_unresolved"]:
            errors.append(f"{label} unresolved oracle cases " + ", ".join(evidence["oracle_unresolved"]))

    if available.keys() == {"w1", "c1"}:
        old, new = available["w1"], available["c1"]
        result["runtime_changes"] = changed_hashes(old["fingerprints"], new["fingerprints"])
        for name in PROTECTED:
            changes = changed_hashes(old["oracle"].get(name, {}), new["oracle"].get(name, {}))
            if changes:
                result["oracle_changes"][name] = changes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path, help="local public-code Git repository")
    for label in ("w1", "c1"):
        parser.add_argument(f"--{label}-commit", required=True, help="full commit ID")
        parser.add_argument(f"--{label}-prompts", required=True, type=Path,
                            help="public-safe JSON object mapping prompt identifiers to SHA-256")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--runtime-image", help="full image ID of a preloaded trusted Python 3.13 Docker image")
    mode.add_argument("--static-only", action="store_true", help="diagnostic only, skip runtime identity")
    args = parser.parse_args()
    try:
        result = compare(args)
    except InvalidInput as error:
        print(json.dumps({"error": str(error)}))
        return 2
    print(json.dumps(result, indent=2))
    if any(result.get(key) for key in ("error", "closure_changes", "runtime_changes", "oracle_changes")):
        return 2
    return int(bool(result["protected_changes"] or result["prompt_changes"]))


if __name__ == "__main__":
    raise SystemExit(main())
