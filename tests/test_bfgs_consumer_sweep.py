"""Inventory supported ungated bundle reads in tracked production Python.

**51 (0). What a GREEN sweep means.**
**Promised,** at the commit the sweep runs on, for every tracked Python file under the **swept roots**: `joulewise/`, `scripts/`, `docs/paper/`, `configs/`:
1. Every read site written in a supported form (51 (b), as extended by 57 (d) 5), in any scope (51 (b) 0), is either gated in its own scope by a gate call that dominates it (51 (c), (d)), or has an allowlist row.
2. Every allowlist row carries a class whose condition holds. The sweep checks the condition where the class table gives it a check. The refuter checks it by reading otherwise.
3. Five closed lists equal the tree under `joulewise/` and `scripts/` only: the gate bodies (57 (b) 6), the tolerant definitions (57 (d)), the reader's public methods (58 (b)), the journal readers (58 (e)), the raw-capture readers (58 (f)).

**Assumed.** The code was written to do its job. Its author, a person or a model, was not trying to get past the battery check. (D-161: one trusted operator; an adversary inside the process is outside the threat model.)

**Not promised.**
1. That no Python program can read energy from a refused bundle.
2. Anything about a form in the deliberate class (61 (b)).
3. Anything about a blind spot listed in 51 (h).
4. Anything about code outside the swept roots: tracked Python under `tests/`, `docs/process_traces/` and `docs/legacy/`; a notebook; a shell command. And, under `docs/paper/` and `configs/`, anything about the stage journal or the raw capture. One function there reads a raw capture at the commit of this text: `docs/paper/figures/reproduce_worked_examples.py::historical`, which reads `raw/powermetrics.plist` of a capture directory that is not a bundle.
5. That a bundle's bytes are the bytes that were measured. That is custody's duty, not the sweep's.

A GREEN sweep is therefore read as: "no ordinary code in the tree reads energy past the gate without a checked reason". It is not read as: "no ungated read can exist".

**(b) The deliberate class.** A latent form is in the deliberate class if its source, between the scope it starts in and the read it reaches, does at least one of:

1. writes or deletes an attribute whose name begins with `_`, or reads `_cache`, `_path` or a name-mangled attribute (`_<Class>__<name>`), on an object whose class or module is defined under `joulewise/`, from outside the module that defines it (`r._path = b`; `r._cache.update(…)`; `r._BundleReader__root`). A **call** of a private function or method is not in the class. Where it reads a watched file it is a supported form and the sweep reports it (51 (b) 2).
2. assigns to, or deletes, an attribute of a module, class or function defined under `joulewise/` (`battery_float.authenticate_bundle = f`; `BundleReader.metadata = f`);
3. calls `setattr`, `delattr`, `object.__setattr__`, `vars`, `exec`, `eval`, `compile`, `__import__`, `importlib.import_module`, or `type` with three arguments; or names `__dict__`, `__code__`, `__class__` or `sys.modules`;
4. builds the name of a tolerant accessor or of a gate while the program runs (`getattr(r, "raw_" + "summary")`).

A form in the class is **never a finding against the sweep**. It is added to 51 (h) by name if it is not there. A watched **file** name built at run time is not in the class; it is a blind spot (51 (h), "a read that never names the file").

Rules already ruled that guard forms of the class stay as ruled: 57 (b) 1 (iii) and 57 (b) 4. They are written, GREEN on the tree, and cost the seat one check each. **No new rule is added for the class, by this ruling or by any later review of this lane.**

**The class table, `non_claim` clause (i) (amendment 72).** No energy-class value that the function reads from the file, and no value computed from one, **leaves** the function. A value leaves a function when the function returns it, writes it to a file, stores it on an object that outlives the call, or puts it in the message of an exception it raises. A field whose value the function only **tests** (is it absent or null; does it parse as a number; is it finite) and then drops does not leave. A reason under (i) states the fields whose values leave. If it tests and drops an energy-class field, it names that field and its test.

**61 (c), the stop rule, as amended by 66.** The review ends when A1 to A5
hold at one merge candidate, each shown by execution:

- A1, the matrix: every named test row is GREEN on the tree and RED under its
  counterfactual applied in memory.
- A2, the inventory: reported keys equal the allowlist keys, with a stated
  count; one refuter checks every allowlist class and every closed-list kind.
- A3, the tree: the same refuter pass finds no energy-class value that reaches
  a claim artifact without a gate, on the routes through the eight consumers
  and through the envelope gate, other than by a pre-existing route returned
  under row 1c of 61 (c).
- A4, the suites: V1, V2, and the builder's forward check are GREEN.
- A5, the fences: battery_float.py has hash prefix 4b4d7bb20625; it,
  reduce.py, and bundle.py are byte-identical to base; none of the eight
  consumers imports battery_float.

There is one refuter pass. Its findings have these dispositions:

| Finding | Disposition | Another refuter pass? |
|---|---|---|
| 1a: a failure of A1, A2, A4 or A5; or a failure of A3 whose fix is a change ruled in §5 of the SAMESIG ruling or in its erratum | the seat fixes it; the lead re-runs the affected rows | no |
| 1b: a failure of A3 whose fix is production code that no ruling covers, on a route that S1 introduced or changed | the seat returns it; a cold gate rules an S1 fix; it blocks S1's merge | yes, one pass on the fix only |
| 1c: the same on a pre-existing route | the seat returns it; the lead opens a lane with an order and a standing check; it does not block S1's merge | not for S1 |
| a latent deliberate-class form | named in 51 (h); it is never a finding | no |
| a 51 (h) blind spot | nothing | no |
| a missed supported form | closed if the closure is GREEN on the tree | no |
| three or more missed supported forms in that one pass | rule 11; S1 merges and lane BFGS-GATED-SUMMARY-01 is next | no |

For row 1c, pre-existing means an executed probe drives the value to the claim
artifact, the unchanged probe gives the same result on main, and the route's
functions have no changed line between main and the merge candidate. The
number of latent forms never blocks S1's merge; A1 to A5 do.

**58 (f) 6, as replaced by 75 (a).** A member of kind `energy` that has no gate is not given a gate by the seat. The seat returns it. A cold gate then rules one of two things. If the member lies on a route through the eight consumers or the envelope gate, amendment 66 (a) applies, rows 1b and 1c. If it lies on no such route and its file is byte-identical to main, it may take the entry `("energy", ("lane", "<lane name>"))`.
"""
from __future__ import annotations

import ast
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SWEEP_ROOTS = ("joulewise/", "scripts/", "docs/paper/", "configs/")
EXCLUDED_ROOTS = ("tests/", "docs/process_traces/", "docs/legacy/")
SWEEP_LIMITATIONS = (
    "A read that never names the file: a loop over a directory listing, a copy of a whole directory, a digest of a whole bundle.",
    "A path that reaches a function inside an object the sweep did not see stored.",
    "Calls are matched by name, so two helpers of one name are treated as one.",
    "Which bundle the gate authenticated: a window gate on one member list may precede a read of another bundle.",
    "A context manager other than suppress that swallows exceptions in its exit method.",
    "A handler that ends in raise inside a branch of its own and lets another branch fall through is judged by its last statement only.",
    "A value read from the stage journal: events.jsonl is not a watched file; events() cannot gate itself.",
    "A read of the meter's raw capture by its path; raw/powermetrics.plist, raw/powermetrics_idle.plist and raw/nvidia_smi*.csv are not watched files.",
    "A handler that ends in a call of a function that always raises is judged by its last statement, which is a call.",
    "A name built while the program runs, such as getattr(reader, 'raw_' + 'summary'), is not seen.",
    "The gate's behaviour replaced while its name stays: deliberate class; not swept.",
    "A reader pointed at another bundle after metadata() passed: deliberate class; not swept; lane BFGS-READER-ROOT-01.",
    "The same through the interpreter's tables: importlib.import_module, sys.modules, __code__, vars and __dict__; deliberate class; not swept.",
    "A gate in a callee. A gate call inside a function that the row's function calls is not seen. At the merge candidate no read is known to rely on one: the envelope gate's two reads relied on one until amendment 63.",
    "A value that a campaign stores for the next one. The cooldown anchor in a campaign's provenance holds the idle power of a bundle that the later campaign's gate never sees (executed, SAMESIG erratum E1 to E3). The sweep reads source text and does not follow a value through a file. Lane BFGS-COOLDOWN-ANCHOR-01.",
    "A calibration capture parsed by a script. Five functions in four scripts under scripts/ refit power pulses from a capture directory with no battery check (amendment 75 (b)). The capture directory is not a bundle, so no bundle gate applies. A capture enters a measured run or a calibration bracket only through the capture form of the gate (controller.py:448, calibration_bracketing.py:1909). Lane BFGS-RAWCAPTURE-01.",
)
WATCHED = ("summary_metrics.json", "metadata.json", "power_trace.csv")
TOLERANT = {"raw_metadata", "raw_config", "raw_summary", "raw_artifact_bytes"}
PATH_BUILDERS = {"Path","PurePosixPath","PurePath","join","joinpath","str","fspath","with_name","resolve","absolute","expanduser","rglob","glob","iterdir","with_suffix","parent"}
GATES = {"authenticate_window_members"}
NON_READING = {"is_file","exists","is_dir","is_symlink","relative_to","with_name","as_posix",
    "str","repr","Path","PurePosixPath","PurePath","join","append","add","extend","print","format",
    "resolve","lstat","stat","unlink","rename","replace","isinstance","len","sorted","set","tuple",
    "list","dict","frozenset","get","setdefault","update","startswith","endswith","index","count",
    "ValueError","RuntimeError","OSError","TypeError","KeyError","BundleReadError","write_text","write_bytes",
    "items","keys","values","enumerate","zip","any","all","fspath","name","mkdir","touch","add_argument"}
def watched_in(value):
    if isinstance(value, str):
        return next((w for w in WATCHED if value == w or value.endswith("/" + w)), None)
    return None
def const_hit(node):
    for n in ast.walk(node):
        if isinstance(n, ast.Constant):
            w = watched_in(n.value)
            if w: return w
    return None
def name_of(call):
    f = call.func
    return f.attr if isinstance(f, ast.Attribute) else f.id if isinstance(f, ast.Name) else ""
def module_constants(tree, known=None):
    out = {}
    known = known or {}
    def path_value(node):
        if isinstance(node, ast.Constant): return watched_in(node.value)
        if isinstance(node, ast.Name): return out.get(node.id) or known.get(node.id)
        if isinstance(node, ast.Attribute) and node.attr.isupper(): return known.get(node.attr)
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            return path_value(node.left) or path_value(node.right)
        if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
            return next((w for w in map(path_value, node.elts) if w), None)
        if isinstance(node, ast.Call) and name_of(node) in PATH_BUILDERS:
            parts = list(node.args) + [k.value for k in node.keywords]
            if isinstance(node.func, ast.Attribute): parts.append(node.func.value)
            return next((w for w in map(path_value, parts) if w), None)
        return None
    changed = True
    while changed:
        changed = False
        for node in tree.body:
            targets, value = [], None
            if isinstance(node, ast.Assign): targets, value = node.targets, node.value
            elif isinstance(node, ast.AnnAssign) and node.value is not None:
                targets, value = [node.target], node.value
            if value is None: continue
            w = path_value(value)
            if w:
                for t in targets:
                    if isinstance(t, ast.Name) and t.id not in out:
                        out[t.id] = w; changed = True
    return out
def qualified(tree):
    """Yield every execution scope, including definitions in compound suites."""
    yield "<module>", tree
    def visit(node, prefix):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                q = f"{prefix}.{child.name}" if prefix else child.name
                if isinstance(child, ast.ClassDef):
                    yield q + ".<body>", child
                else:
                    yield q, child
                yield from visit(child, q)
            elif not isinstance(child, ast.Lambda):
                yield from visit(child, prefix)
    yield from visit(tree, "")
def stable_parameters(fn):
    if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return set()
    params = {a.arg for a in (fn.args.posonlyargs + fn.args.args +
                              fn.args.kwonlyargs)}
    if fn.args.vararg: params.add(fn.args.vararg.arg)
    if fn.args.kwarg: params.add(fn.args.kwarg.arg)
    rebound = set()
    for node in ast.walk(fn):
        if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            rebound.add(node.id)
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            rebound.update(node.names)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node is not fn:
            rebound.add(node.name)
        elif isinstance(node, ast.MatchAs) and node.name:
            rebound.add(node.name)
        elif isinstance(node, ast.MatchStar) and node.name:
            rebound.add(node.name)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            rebound.add(node.name)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            rebound.update(alias.asname or alias.name.split(".")[0]
                           for alias in node.names)
    return params - rebound


def same_parameter_branch(node, stable):
    if not isinstance(node, ast.If) or not isinstance(node.test, ast.Compare):
        return None
    test = node.test
    if (len(test.ops) == 1 and isinstance(test.ops[0], ast.IsNot)
            and len(test.comparators) == 1
            and isinstance(test.comparators[0], ast.Constant)
            and test.comparators[0].value is None
            and isinstance(test.left, ast.Name) and test.left.id in stable):
        return test.left.id
    return None


def own_nodes(fn):
    """Nodes of fn excluding nested defs/classes, each with its chain of enclosing branches."""
    out = []
    stable = stable_parameters(fn)
    def walk(node, chain):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for expr in [*node.decorator_list, *node.args.defaults, *
                         (value for value in node.args.kw_defaults if value is not None)]:
                walk(expr, chain)
            return
        if isinstance(node, ast.ClassDef):
            for expr in [*node.decorator_list, *node.bases, *
                         (item.value for item in node.keywords)]:
                walk(expr, chain)
            return
        out.append((node, chain))
        for field, value in ast.iter_fields(node):
            items = value if isinstance(value, list) else [value]
            for child in items:
                if not isinstance(child, ast.AST): continue
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)): continue
                if isinstance(child, ast.Lambda):
                    walk(child.body, chain + ((id(child), "lambda"),))
                    continue
                branch = chain
                if isinstance(node, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.Match, ast.IfExp, ast.BoolOp, ast.ExceptHandler, ast.match_case)) and field in ("body","orelse","handlers","finalbody","cases","values","test","iter"):
                    skip = False
                    if field in ("test", "iter"): skip = True
                    if isinstance(node, ast.BoolOp) and child is node.values[0]: skip = True
                    if isinstance(node, ast.Try) and field in ("body", "orelse"):
                        all_raise = all(h.body and isinstance(h.body[-1], (ast.Raise, ast.Return)) for h in node.handlers)
                        if all_raise:
                            skip = None
                            if field == 'body': branch = chain + ((id(node), 'trybody-transparent'),)
                        else: branch = chain + ((id(node), "body"),); skip = None  # body+else share one branch
                    if isinstance(node, ast.ExceptHandler) and field == "body": skip = True  # branch was opened at Try.handlers
                    if skip is False:
                        param = same_parameter_branch(node, stable) if field == "body" else None
                        branch = chain + (((0, "param_non_none", param) if param else
                                          (id(node), field, id(child) if field in ("handlers","cases") else 0)),)
                if isinstance(node, (ast.With, ast.AsyncWith)) and field == "body":
                    if any(isinstance(i.context_expr, ast.Call) and name_of(i.context_expr) == "suppress" for i in node.items):
                        branch = chain + ((id(node), "suppress"),)   # (d) 5
                walk(child, branch)
    for stmt in fn.body: walk(stmt, ())
    return out

def dominates(gch, chain):
    """Rules (d) 1-5 on two branch chains: gate chain gch, later statement chain."""
    trys = {m[0] for m in gch if m[1] in ('trybody-transparent', 'body')}
    if any(m[0] in trys and m[1] in ('handlers', 'finalbody') for m in chain): return False
    g2 = tuple(m for m in gch if m[1] != 'trybody-transparent'); c2 = tuple(m for m in chain if m[1] != 'trybody-transparent')
    return g2 == c2[:len(g2)]
def sweep(path, source, global_consts):
    tree = ast.parse(source, filename=path)
    consts = dict(global_consts); consts.update(module_constants(tree))
    imported_gate = any(isinstance(n, ast.ImportFrom) and n.module == "joulewise.bundle_read"
                        and any(a.name == "authenticate_window_members" for a in n.names) for n in ast.walk(tree)) \
                    or path == "joulewise/bundle_read.py"
    rows = []
    for q, fn in qualified(tree):
        nodes = own_nodes(fn)
        in_reader = path == "joulewise/bundle_read.py" and q.startswith("BundleReader.")
        # taint: names bound from an expression containing a watched constant / tainted name
        tainted = {}
        def expr_w(e):
            if isinstance(e, ast.Constant): return watched_in(e.value)
            if isinstance(e, ast.Name):
                return tainted.get(e.id) or consts.get(e.id)
            if isinstance(e, ast.Attribute):
                return consts.get(e.attr) if e.attr.isupper() else None
            if isinstance(e, ast.BinOp) and isinstance(e.op, ast.Div):
                return expr_w(e.left) or expr_w(e.right)
            if isinstance(e, (ast.Tuple, ast.List, ast.Set)):
                return next((w for w in map(expr_w, e.elts) if w), None)
            if isinstance(e, ast.Starred): return expr_w(e.value)
            if isinstance(e, ast.Call) and name_of(e) in PATH_BUILDERS:
                parts = list(e.args) + [k.value for k in e.keywords]
                if isinstance(e.func, ast.Attribute): parts.append(e.func.value)
                return next((w for w in map(expr_w, parts) if w), None)
            return None
        readers = set()
        args = fn.args.args + fn.args.kwonlyargs if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)) else []
        for a in args:
            ann = a.annotation
            if ann is not None and "BundleReader" in ast.dump(ann): readers.add(a.arg)
        changed = True
        while changed:
            changed = False
            for n, _ in nodes:
                pairs = []
                if isinstance(n, ast.Assign): pairs = [(t, n.value) for t in n.targets]
                elif isinstance(n, (ast.AnnAssign, ast.NamedExpr)) and getattr(n, "value", None) is not None: pairs = [(n.target, n.value)]
                elif isinstance(n, (ast.For, ast.AsyncFor, ast.comprehension)): pairs = [(n.target, n.iter)]
                elif isinstance(n, ast.withitem) and n.optional_vars is not None: pairs = []  # handle is content, site is the open call
                for target, value in pairs:
                    w = expr_w(value)
                    for t in ast.walk(target):
                        if isinstance(t, ast.Name):
                            if w and t.id not in tainted: tainted[t.id] = w; changed = True
                            if isinstance(value, ast.Call) and name_of(value) == "BundleReader" and t.id not in readers:
                                readers.add(t.id); changed = True
        gates = []
        for n, chain in nodes:
            if not isinstance(n, ast.Call): continue
            nm = name_of(n)
            if (nm == "authenticate_window_members" and imported_gate
                    and isinstance(n.func, ast.Name)):
                gates.append((n.lineno, n.col_offset, chain, None, "window"))
            elif nm == "metadata" and isinstance(n.func, ast.Attribute):
                r = n.func.value
                ok = (isinstance(r, ast.Call) and name_of(r) == "BundleReader") or \
                     (isinstance(r, ast.Name) and (r.id in readers or (r.id == "self" and in_reader)))
                if ok: gates.append((n.lineno, n.col_offset, chain, r.id if isinstance(r, ast.Name) else None, "reader"))
        rebinds = {}
        for n2, _ in nodes:
            tg = []
            if isinstance(n2, ast.Assign): tg = n2.targets
            elif isinstance(n2, (ast.AnnAssign, ast.NamedExpr, ast.For, ast.AsyncFor, ast.comprehension)): tg = [n2.target]
            for t in tg:
                for x in ast.walk(t):
                    if isinstance(x, ast.Name): rebinds.setdefault(x.id, []).append((x.lineno, x.col_offset))
        def gated(n, chain, tolerant_receiver=False):
            if any(mark[1] == "lambda" for mark in chain):
                return False
            pos = (n.lineno, n.col_offset)
            for gl, gc, gch, recv, form in gates:
                trys = {m[0] for m in gch if m[1] in ('trybody-transparent', 'body')}
                if any(m[0] in trys and m[1] in ('handlers', 'finalbody') for m in chain): continue   # (d) 3
                g2 = tuple(m for m in gch if m[1] != 'trybody-transparent'); c2 = tuple(m for m in chain if m[1] != 'trybody-transparent')
                if not ((gl, gc) < pos and g2 == c2[:len(g2)]): continue
                if tolerant_receiver is not False and form == "reader":
                    if recv is None or recv != tolerant_receiver: continue
                    if any((gl, gc) < rb < pos for rb in rebinds.get(recv, [])): continue
                return True
            return False
        for n, chain in nodes:
            if not isinstance(n, ast.Call): continue
            nm = name_of(n)
            op = w = None
            if nm in TOLERANT and isinstance(n.func, ast.Attribute):
                op, w = nm, "-"
            elif nm not in NON_READING and nm not in PATH_BUILDERS and nm not in GATES:
                parts = list(n.args) + [k.value for k in n.keywords]
                if isinstance(n.func, ast.Attribute): parts.append(n.func.value)
                for p in parts:
                    w = expr_w(p)
                    if w: op = "direct:" + nm; break
            if op:
                tr = False
                if nm in TOLERANT and isinstance(n.func, ast.Attribute):
                    rv = n.func.value
                    tr = rv.id if isinstance(rv, ast.Name) else None
                if not gated(n, chain, tr):
                    rows.append((path, q, op, w, n.lineno))
        # Taking a tolerant method for later use cannot inherit this scope's gate.
        callees = {id(n.func) for n, _ in nodes if isinstance(n, ast.Call)}
        for n, _ in nodes:
            ref = (n.attr if isinstance(n, ast.Attribute) else n.value
                   if isinstance(n, ast.Constant) and isinstance(n.value, str)
                   else None)
            if ref in {"raw_summary", "raw_metadata", "raw_artifact_bytes"} and id(n) not in callees:
                rows.append((path, q, "ref:" + ref, "-", n.lineno))
        # (b) 3: store of a path expression to an attribute or subscript
        for n, chain in nodes:
            if isinstance(n, ast.Assign):
                for t in n.targets:
                    if isinstance(t, (ast.Attribute, ast.Subscript)):
                        w = expr_w(n.value)
                        if w and not gated(n, chain):
                            rows.append((path, q, "store:" + ast.unparse(t), w, n.lineno))
    return rows
def tracked(root, rev=None):
    names = subprocess.check_output(["git", "ls-files", "*.py"], cwd=root, text=True).splitlines()
    return [n for n in names if n.startswith(SWEEP_ROOTS)]


def swept_file_violations(names):
    return [f"tracked Python outside swept or excluded roots: {name}" for name in names
            if name.endswith(".py") and not name.startswith(SWEEP_ROOTS + EXCLUDED_ROOTS)]


def all_tracked_python(root=ROOT):
    return subprocess.check_output(["git", "ls-files", "*.py"], cwd=root, text=True).splitlines()
def run(root):
    files = {n: (Path(root)/n).read_text() for n in tracked(root)}
    return sweep_files(files)


def sweep_files(files):
    g = {}
    trees = {n: ast.parse(s, filename=n) for n, s in files.items()}
    changed = True
    while changed:
        changed = False
        for tree in trees.values():
            for k, v in module_constants(tree, g).items():
                if k not in g:
                    g[k] = v; changed = True
    rows = []
    for n, s in files.items(): rows += sweep(n, s, g)
    return rows, g


def sweep_source(path: str, source: str, constants=None):
    return sweep(path, source, constants or module_constants(ast.parse(source)))


def site_keys(rows):
    return {(p, q, op, watched) for p, q, op, watched, _ in rows}


# Static four-part keys: path, qualified scope, operation, watched file.
CAMPAIGN_VERDICT_USES = (
    ("scripts/run_campaign.py::run_campaign", "classify_campaign_members"),
    ("scripts/run_campaign.py::run_axi_spec_campaign", "_idle_admission_core_evaluation"),
    ("scripts/run_campaign.py::run_axi_spec_campaign", "classify_campaign_members"),
)
CAMPAIGN_COLLECTION_USES = (
    ("scripts/run_campaign.py::run_campaign", "campaign_cooldown_before_member"),
    ("scripts/run_campaign.py::run_campaign", "_first_eligible_cooldown_anchor"),
    ("scripts/run_campaign.py::run_campaign", "record_campaign_member_provenance"),
    ("scripts/run_campaign.py::run_campaign", "evaluation_failure_detail"),
    ("scripts/run_campaign.py::run_campaign", "to_log"),
    ("scripts/run_campaign.py::run_axi_spec_campaign", "campaign_cooldown_before_member"),
    ("scripts/run_campaign.py::run_axi_spec_campaign", "_first_eligible_cooldown_anchor"),
    ("scripts/run_campaign.py::run_axi_spec_campaign", "record_campaign_member_provenance"),
)
CAMPAIGN_PRODUCERS = ("evaluate_member", "evaluate_members")
CAMPAIGN_CONSUMERS_EVIDENCE = {
    "consumers": CAMPAIGN_VERDICT_USES,
    "collection_uses": CAMPAIGN_COLLECTION_USES,
    "producers": CAMPAIGN_PRODUCERS,
}
CAMPAIGN_CONSUMERS_REASON = (
    "consumers form, amendment 66 (c); verdict uses are gated; collection uses are listed; "
    "`_first_eligible_cooldown_anchor` stores a value another campaign reads: "
    "lane BFGS-COOLDOWN-ANCHOR-01"
)
ALLOWLIST = {
    ('docs/paper/figures/reproduce_worked_examples.py', 'historical', 'direct:read_bytes', 'power_trace.csv'): ('non_claim', 'clause (i), fields read: interval_start_s, interval_end_s; the bytes are hashed and compared with the digest in docs/process_traces/2026-08-09-prefill-phase-proof/results.json'),
    ('docs/paper/figures/reproduce_worked_examples.py', 'synthetic', 'direct:read_bytes', 'power_trace.csv'): ('non_claim', 'clause (i), fields read: none; the bytes are hashed into fixture_fingerprints'),
    ('joulewise/analysis_engine/registry.py', 'validate_attempt_ledger', 'direct:read_authentication_input', 'metadata.json'): ('non_claim', 'clause (i), fields read: metadata.run_id and launch and target model identity fields in the attempt ledger'),
    ('joulewise/analysis_engine/registry.py', 'validate_manifest_target_evidence', 'direct:read_authentication_input', 'metadata.json'): ('non_claim', 'clause (i), fields read: metadata.runtime.target_model_artifact_sha256'),
    ('joulewise/analysis_manifest_v3.py', '_derive_arms_and_entries', 'direct:_read_manifest_input', 'metadata.json'): ('non_claim', 'clause (i), fields read: metadata.workload_provenance.model.artifact_identity and tokenizer; adapters.runtime.prepare_metadata and adapters.telemetry; device, model and quantization identities'),
    ('joulewise/analysis_manifest_v3.py', '_floor_consumer_contexts', 'direct:_read_manifest_input', 'metadata.json'): ('non_claim', 'clause (i), fields read: metadata.machine, platform, adapters.runtime.prepare_metadata, adapters.telemetry, workload_provenance model artifact, tokenizer, sampler and output_policy, device and quantization identities'),
    ('joulewise/arm_readiness.py', 'authenticate_bundle_launch_lineage', 'direct:read_bytes', 'metadata.json'): ('non_claim', 'clause (i), fields read: metadata.launch_lineage identity and completion fields'),
    ('joulewise/battery_float.py', 'authenticate_bundle', 'direct:_required_object', 'metadata.json'): ('gate_body', 'authenticate_bundle is one of the three closed gate bodies'),
    ('joulewise/bundle.py', 'RunBundleWriter.write_power_trace', 'direct:open', 'power_trace.csv'): ('non_claim', 'clause (i), fields read: no field read; open is write-only for the new power_trace.csv'),
    ('joulewise/bundle_read.py', 'BundleReader.events', 'direct:_strict_json', 'metadata.json'): ('non_claim', 'clause (i), fields read: metadata.battery_float presence, only when events.jsonl is missing'),
    ('joulewise/bundle_read.py', 'BundleReader.is_complete', 'raw_summary', '-'): ('strict_validation', 'validates summary presence and status; returns boolean'),
    ('joulewise/bundle_read.py', 'BundleReader.is_event_v2', 'raw_metadata', '-'): ('strict_validation', 'validates event semantics identity; returns boolean'),
    ('joulewise/bundle_read.py', 'BundleReader.is_frozen_legacy_identity', 'raw_metadata', '-'): ('strict_validation', 'validates frozen legacy identity; returns boolean'),
    ('joulewise/bundle_read.py', 'BundleReader.metadata', 'direct:_strict_json', 'metadata.json'): ('gate_body', 'BundleReader.metadata is one of the three closed gate bodies'),
    ('joulewise/bundle_read.py', 'BundleReader.problems', 'direct:read_authentication_text', 'metadata.json'): ('strict_validation', 'validates bundle structural validity; returns problem strings'),
    ('joulewise/bundle_read.py', 'BundleReader.rail_manifest', 'raw_metadata', '-'): ('non_claim', 'clause (i), fields read: metadata.rail_manifest identity and rail labels'),
    ('joulewise/bundle_read.py', 'BundleReader.raw_metadata', 'direct:_tolerant_json', 'metadata.json'): ('tolerant_definition', 'BundleReader.raw_metadata forwards the watched metadata.json without a gate; every caller is inventoried'),
    ('joulewise/bundle_read.py', 'BundleReader.raw_summary', 'direct:_tolerant_json', 'summary_metrics.json'): ('tolerant_definition', 'BundleReader.raw_summary forwards the watched summary_metrics.json without a gate; every caller is inventoried'),
    ('joulewise/bundle_read.py', '_check_power_trace', 'direct:open_authentication_input', 'power_trace.csv'): ('strict_validation', 'validates power trace structure; returns problem strings'),
    ('joulewise/bundle_read.py', 'authenticate_window_members', 'direct:_strict_json', 'metadata.json'): ('gate_body', 'authenticate_window_members is one of the three closed gate bodies'),
    ('joulewise/bundle_read.py', 'axi_v2_validation_problems', 'raw_config', '-'): ('strict_validation', 'validates event-v2 and AXI bundle validity; returns problem strings'),
    ('joulewise/bundle_read.py', 'axi_v2_validation_problems', 'raw_metadata', '-'): ('strict_validation', 'validates event-v2 and AXI bundle validity; returns problem strings'),
    ('joulewise/bundle_read.py', 'axi_v2_validation_problems', 'raw_summary', '-'): ('strict_validation', 'validates event-v2 and AXI bundle validity; returns problem strings'),
    ('joulewise/calibration_ledger.py', '_artifact_hashes_unbounded', 'direct:hash_core', 'power_trace.csv'): ('non_claim', 'clause (i), fields read: no parsed field; only opaque bytes and their digests'),
    ('joulewise/calibration_ledger.py', '_custody_state_unbounded', 'direct:custody_state', 'power_trace.csv'): ('non_claim', 'clause (i), fields read: no parsed field; custody state and digests of opaque artifacts'),
    ('joulewise/calibration_ledger.py', '_governed_raw_nofollow_unbounded', 'direct:_read_contained_nofollow_unbounded', 'power_trace.csv'): ('non_claim', 'clause (i), fields read: no parsed field; returns opaque governed artifact bytes to custody verification'),
    ('joulewise/cli.py', '_cmd_reduce', 'direct:read_authentication_text', 'summary_metrics.json'): ('non_claim', 'clause (ii), output: writes the already reduced summary JSON to stdout; returns only a CLI exit code to main; no tracked claim artifact consumes stdout'),
    ('joulewise/cli.py', '_strict_emitted_token_ids_problems', 'raw_metadata', '-'): ('strict_validation', 'validates strict bundle validity; returns problem strings'),
    ('joulewise/cli.py', '_strict_problems', 'raw_config', '-'): ('strict_validation', 'validates strict bundle validity; returns problem strings'),
    ('joulewise/cli.py', '_strict_problems', 'raw_metadata', '-'): ('strict_validation', 'validates strict bundle validity; returns problem strings'),
    ('joulewise/cli.py', '_strict_problems', 'raw_summary', '-'): ('strict_validation', 'validates strict bundle validity; returns problem strings'),
    ('joulewise/cli.py', '_strict_realized_output_problems', 'raw_config', '-'): ('strict_validation', 'validates strict bundle validity; returns problem strings'),
    ('joulewise/cli.py', '_strict_realized_output_problems', 'raw_metadata', '-'): ('strict_validation', 'validates strict bundle validity; returns problem strings'),
    ('joulewise/cli.py', '_strict_reducer_version_dispatch', 'raw_metadata', '-'): ('strict_validation', 'validates strict bundle validity; returns problem strings'),
    ('joulewise/cli.py', '_strict_rich_telemetry_problems', 'raw_metadata', '-'): ('strict_validation', 'validates strict bundle validity; returns problem strings'),
    ('joulewise/cli.py', '_strict_uncertainty_evidence_problems', 'raw_metadata', '-'): ('strict_validation', 'validates strict bundle validity; returns problem strings'),
    ('joulewise/cli.py', '_strict_workload_provenance_problems', 'raw_metadata', '-'): ('strict_validation', 'validates strict bundle validity; returns problem strings'),
    ('joulewise/cli.py', '_verify_nvidia_smi_raw_to_trace', 'raw_metadata', '-'): ('strict_validation', 'validates strict bundle validity; returns problem strings'),
    ('joulewise/cli.py', '_verify_powermetrics_raw_to_trace', 'raw_metadata', '-'): ('strict_validation', 'validates strict bundle validity; returns problem strings'),
    ('joulewise/controller.py', '_experiment_cooldown_anchor', 'direct:read_text', 'metadata.json'): ('non_claim', 'clause (i), fields read: metadata.environment_admission.per_run_environment_evaluation.snapshot_sha256'),
    ('joulewise/controller.py', '_experiment_cooldown_reference_eligibility', 'direct:read_text', 'metadata.json'): ('non_claim', 'clause (i), fields read: metadata.environment_admission decision/critical_environment_passed/reference_provenance_present and campaign_policy.sha256'),
    ('joulewise/controller.py', '_member_gap_note', 'direct:read_text', 'metadata.json'): ('non_claim', 'clause (i), fields read: metadata.extra.preceding_gap_s'),
    ('joulewise/determinism_gate.py', '_check_gate_json_evidence_for_duplicate_keys', 'direct:_load_json_without_duplicate_keys', 'metadata.json'): ('strict_validation', 'validates duplicate JSON keys; appends problem strings only'),
    ('joulewise/determinism_gate.py', '_check_gate_json_evidence_for_duplicate_keys', 'direct:_load_jsonl_without_duplicate_keys', 'metadata.json'): ('strict_validation', 'validates duplicate JSON keys; appends problem strings only'),
    ('joulewise/determinism_gate.py', '_inspect_strict_valid_bundle', 'raw_config', '-'): ('strict_validation', 'validates duplicate JSON keys; appends problem strings only'),
    ('joulewise/envelope_gate.py', '_bundle_hashes', 'direct:encode', 'metadata.json'): ('non_claim', 'clause (i), fields read: no parsed field; hashes artifact bytes as opaque custody evidence'),
    ('joulewise/envelope_gate.py', '_bundle_hashes', 'direct:read_bytes', 'metadata.json'): ('non_claim', 'clause (i), fields read: no parsed field; hashes artifact bytes as opaque custody evidence'),
    ('joulewise/floor_extraction.py', '_cpu_admission_bundle_reasons', 'direct:_strict_admission_json_file', 'metadata.json'): ('behind_gate', 'callers form: _cpu_admission_bundle_reasons has the listed gated caller chain', {'callers': ('joulewise/floor_extraction.py::_evaluate_member', 'joulewise/floor_extraction.py::extract_absolute_cell', 'joulewise/floor_extraction.py::extract_comparative_cell', 'joulewise/floor_extraction.py::extract_cells')}),
    ('joulewise/floor_extraction.py', '_evaluate_member', 'direct:_strict_admission_json_file', 'metadata.json'): ('behind_gate', 'callers form: _evaluate_member has the listed gated caller chain', {'callers': ('joulewise/floor_extraction.py::extract_absolute_cell', 'joulewise/floor_extraction.py::extract_comparative_cell', 'joulewise/floor_extraction.py::extract_cells')}),
    ('joulewise/floor_extraction.py', '_read_summary', 'direct:_strict_admission_json_value', 'summary_metrics.json'): ('behind_gate', 'callers form: _read_summary has the listed gated caller chain', {'callers': ('joulewise/floor_extraction.py::_evaluate_member', 'joulewise/floor_extraction.py::extract_absolute_cell', 'joulewise/floor_extraction.py::extract_comparative_cell', 'joulewise/floor_extraction.py::extract_cells')}),
    ('joulewise/floor_extraction.py', '_read_summary', 'direct:read_authentication_input', 'summary_metrics.json'): ('behind_gate', 'callers form: _read_summary has the listed gated caller chain', {'callers': ('joulewise/floor_extraction.py::_evaluate_member', 'joulewise/floor_extraction.py::extract_absolute_cell', 'joulewise/floor_extraction.py::extract_comparative_cell', 'joulewise/floor_extraction.py::extract_cells')}),
    ('joulewise/idle_dependence.py', 'derive_idle_mean_uncertainty', 'raw_artifact_bytes', '-'): ('behind_gate', 'callers form: derive_idle_mean_uncertainty has the listed gated caller chain', {'callers': ('joulewise/reduce.py::_reduce', 'joulewise/reduce.py::_reduce_v060', 'joulewise/reduce.py::reduce_bundle')}),
    ('joulewise/output_identity.py', '_bundle_reference', 'direct:_hash_file', 'summary_metrics.json'): ('non_claim', 'clause (i), fields read: no summary value; hashes summary bytes as opaque custody evidence'),
    ('joulewise/output_identity.py', '_bundle_reference', 'direct:_json_object', 'metadata.json'): ('non_claim', 'clause (i), fields read: metadata.run_id and runtime.target_tokenizer_identity'),
    ('joulewise/output_identity.py', '_bundle_reference', 'direct:_json_object', 'summary_metrics.json'): ('non_claim', 'clause (i), fields read: no summary value; checks object presence and hashes the bytes'),
    ('joulewise/publication_privacy.py', '_audit_metadata', 'direct:_load_json_object', 'metadata.json'): ('strict_validation', 'validates public-bundle privacy schema; returns problem strings or None'),
    ('joulewise/publication_privacy.py', '_audit_metadata', 'direct:_unknown_keys', 'metadata.json'): ('strict_validation', 'validates public-bundle privacy schema; returns problem strings or None'),
    ('joulewise/publication_privacy.py', '_audit_summary', 'direct:_load_json_object', 'summary_metrics.json'): ('strict_validation', 'validates public-bundle privacy schema; returns problem strings or None'),
    ('joulewise/publication_privacy.py', '_audit_summary', 'direct:_unknown_keys', 'summary_metrics.json'): ('strict_validation', 'validates public-bundle privacy schema; returns problem strings or None'),
    ('joulewise/publication_privacy.py', 'verify_public_bundle', 'direct:_load_json_object', 'metadata.json'): ('strict_validation', 'validates public-bundle privacy schema; returns problem strings or None'),
    ('joulewise/publication_privacy.py', 'verify_public_bundle', 'direct:_load_json_object', 'summary_metrics.json'): ('strict_validation', 'validates public-bundle privacy schema; returns problem strings or None'),
    ('joulewise/reduce.py', '_resolve_reducer_version', 'raw_config', '-'): ('strict_validation', 'validates summary_provenance.reducer_version; returns only reducer version identity'),
    ('joulewise/reduce.py', '_resolve_reducer_version', 'raw_summary', '-'): ('strict_validation', 'validates summary_provenance.reducer_version; returns only reducer version identity'),
    ('joulewise/reduce.py', '_verify_instrument_calibration', 'raw_config', '-'): ('non_claim', 'clause (i), fields read: config.sampling.power_hz, a sampler cadence in Hz, used to compute sampling_interval_ms'),
    ('joulewise/report.py', '_discover_bundles', 'raw_config', '-'): ('non_claim', 'clause (ii), output: returns _Bundle browser records to generate_report; that function writes output_dir/index.html, output_dir/run/<run_id>.html and chart PNGs for the static run browser; no tracked paper claim consumes them'),
    ('joulewise/report.py', '_discover_bundles', 'raw_metadata', '-'): ('non_claim', 'clause (ii), output: returns _Bundle browser records to generate_report; that function writes output_dir/index.html, output_dir/run/<run_id>.html and chart PNGs for the static run browser; no tracked paper claim consumes them'),
    ('joulewise/report.py', '_discover_bundles', 'raw_summary', '-'): ('non_claim', 'clause (ii), output: returns _Bundle browser records to generate_report; that function writes output_dir/index.html, output_dir/run/<run_id>.html and chart PNGs for the static run browser; no tracked paper claim consumes them'),
    ('joulewise/salvage_dangler.py', '_inspect_preworkload_abort', 'direct:_read_json_object', 'metadata.json'): ('non_claim', 'clause (i), fields read: metadata.run_id and environment_admission decision, attempts and claim_reason'),
    ('joulewise/salvage_dangler.py', '_inspect_preworkload_abort', 'direct:_read_json_object', 'summary_metrics.json'): ('non_claim', 'clause (i), fields that leave: `failure_reason`; tested and dropped: `status`, the 17 names of `_MEASURAND_FIELDS`, every other key; test: `status` equals `failed`, each measurand is null, each other key is null or named in `_ALLOWED_FAILED_SUMMARY_NONNULL`'),
    ('joulewise/salvage_dangler.py', '_telemetry_timestamp_bounds', 'direct:open_authentication_input', 'power_trace.csv'): ('non_claim', 'clause (i), fields that leave: `timestamp_s`, `interval_start_s`, `interval_end_s`, as their minimum and maximum; tested and dropped: `power_w`, `source`, `rail`; test: `power_w` parses as a number and is finite, `source` and `rail` hold no workload marker'),
    ('joulewise/salvage_dangler.py', 'inspect_salvage_attempt', 'direct:_read_json_object', 'metadata.json'): ('non_claim', 'clause (i), fields read: metadata.run_id for bundle identity'),
    ('joulewise/whole_window.py', '_authenticated_bundle_launch_lineage_set', 'direct:_read_json_object', 'metadata.json'): ('strict_validation', 'validates launch-lineage identity and completion; returns the shared lineage identity'),
    ('joulewise/whole_window.py', '_consumption_provenance_valid', 'direct:_read_json_object', 'summary_metrics.json'): ('strict_validation', 'validates whole-window provenance and current strict validity; returns identity, boolean, digest or problems'),
    ('joulewise/whole_window.py', '_current_core_rederivation_reasons', 'direct:_read_json_object', 'metadata.json'): ('strict_validation', 'validates whole-window provenance and current strict validity; returns identity, boolean, digest or problems'),
    ('joulewise/whole_window.py', '_current_core_rederivation_reasons', 'direct:_read_json_object', 'summary_metrics.json'): ('strict_validation', 'validates whole-window provenance and current strict validity; returns identity, boolean, digest or problems'),
    ('joulewise/whole_window.py', '_manifest_bundle_paths', 'direct:_read_json_object', 'summary_metrics.json'): ('strict_validation', 'validates bundle identities and returns their path identity map'),
    ('joulewise/whole_window.py', '_manifest_members', 'direct:_read_json_object', 'summary_metrics.json'): ('strict_validation', 'validates bundle identities and returns their identity set'),
    ('joulewise/whole_window.py', '_row_references_current_strict_member', 'direct:_read_json_object', 'summary_metrics.json'): ('strict_validation', 'validates whole-window provenance and current strict validity; returns identity, boolean, digest or problems'),
    ('joulewise/whole_window.py', '_scientific_config_identity', 'direct:_read_json_object', 'metadata.json'): ('strict_validation', 'validates scientific config digest and canonicality boolean'),
    ('joulewise/whole_window.py', '_validate_row_uncached', 'direct:_read_json_object', 'summary_metrics.json'): ('strict_validation', 'validates whole-window provenance and current strict validity; returns identity, boolean, digest or problems'),
    ('joulewise/whole_window.py', '_validated_evaluation_basis', 'direct:read_authentication_input', 'metadata.json'): ('non_claim', 'clause (i), fields read: no parsed field; hashes raw metadata.json bytes against the bound digest'),
    ('joulewise/whole_window.py', 'custody_telemetry_identity', 'direct:_read_json_object', 'metadata.json'): ('strict_validation', 'validates telemetry source identity and returns class identity and agreement booleans'),
    ('joulewise/whole_window.py', 'custody_telemetry_identity', 'direct:_read_json_object', 'summary_metrics.json'): ('strict_validation', 'validates telemetry source identity and returns class identity and agreement booleans'),
    ('joulewise/whole_window.py', 'validate_occurrence_supersession_entry', 'direct:read_authentication_input', 'metadata.json'): ('strict_validation', 'validates whole-window provenance and current strict validity; returns identity, boolean, digest or problems'),
    ('joulewise/whole_window.py', 'whole_window_refusal_reasons', 'direct:_read_json_object', 'summary_metrics.json'): ('strict_validation', 'validates whole-window provenance and current strict validity; returns identity, boolean, digest or problems'),
    ('scripts/analyze_phase_share.py', 'analyze_bundle', 'direct:_sha256', 'power_trace.csv'): ('non_claim', 'clause (ii), output: returns a diagnostic_non_claim_bearing sensitivity record to main, which writes a desk diagnostic JSON, not a governed claim artifact'),
    ('scripts/analyze_phase_share.py', 'analyze_bundle', 'raw_summary', '-'): ('non_claim', 'clause (ii), output: returns a diagnostic_non_claim_bearing sensitivity record to main, which writes a desk diagnostic JSON, not a governed claim artifact'),
    ('scripts/build_battery_float_historical_bundles.py', 'witness', 'direct:_strict_json', 'metadata.json'): ('non_claim', 'clause (i), fields read: metadata.run_id only; the witness compares bundle digests and names'),
    ('scripts/check_window_provenance.py', '_run_assertions.check_a3', 'direct:_read_object', 'summary_metrics.json'): ('non_claim', 'clause (ii), output: returns an assertion string to Reporter.assertion in _run_assertions; Reporter prints it to stdout, and _run_assertions returns an exit code to main; no tracked writer turns stdout into a claim artifact'),
    ('scripts/corpus_compat_receipt.py', 'evaluate_bundle', 'raw_config', '-'): ('non_claim', 'clause (i), fields read: none from config; the raw config is carried to BundleEvidence but token_provenance ignores it'),
    ('scripts/corpus_compat_receipt.py', 'evaluate_bundle', 'raw_metadata', '-'): ('non_claim', 'clause (i), fields read: metadata.run_id and workload_observed.output_token_count, workload_provenance token policy and tokenizer identity, suite identity'),
    ('scripts/corpus_compat_receipt.py', 'evaluate_bundle', 'raw_summary', '-'): ('non_claim', 'clause (i), fields read: summary.measurement_quality.token_counts_source'),
    ('scripts/issue_dg071_dg075_statistics.py', 'main', 'direct:issue_artifacts', 'power_trace.csv'): ('historical', 'amendment 41 pinned a pre-directive a10 power trace by committed SHA-256'),
    ('scripts/make_figures.py', 'extract_rows', 'raw_config', '-'): ('non_claim', 'clause (ii), output: returns figure rows to no tracked production caller; main writes only placeholder figures without measurements', {'callers': ()}),
    ('scripts/make_figures.py', 'extract_rows', 'raw_metadata', '-'): ('non_claim', 'clause (ii), output: returns figure rows to no tracked production caller; main writes only placeholder figures without measurements', {'callers': ()}),
    ('scripts/make_figures.py', 'extract_rows', 'raw_summary', '-'): ('non_claim', 'clause (ii), output: returns figure rows to no tracked production caller; main writes only placeholder figures without measurements', {'callers': ()}),
    ('scripts/make_figures.py', 'gate_inputs', 'raw_summary', '-'): ('non_claim', 'clause (i), fields read: summary.status'),
    ('scripts/make_figures.py', 'realized_output_tokens', 'raw_metadata', '-'): ('non_claim', 'clause (i), fields read: metadata.workload_observed.output_token_count and token count fields'),
    ('scripts/package_bundle_pack.py', '_bundle_id', 'direct:_load_json_file', 'metadata.json'): ('non_claim', 'clause (i), fields read: metadata.run_id'),
    ('scripts/package_bundle_pack.py', '_preflight_bundle', 'raw_metadata', '-'): ('non_claim', 'clause (i), fields read: metadata.source_provenance identity and eligibility fields'),
    ('scripts/package_bundle_pack.py', '_summary_status', 'direct:_load_json_file', 'summary_metrics.json'): ('non_claim', 'clause (i), fields read: summary.status'),
    ('scripts/paper_prefill_resolvability_projection.py', 'scan_corpora', 'direct:read_model', 'metadata.json'): ('non_claim', 'clause (i), fields read: metadata.model.name and revision; summary.measurement_quality.phase_identifiability.prefill; power_trace.csv timestamp_s, interval_start_s and interval_end_s; trace digest is opaque bytes'),
    ('scripts/paper_prefill_resolvability_projection.py', 'scan_corpora', 'direct:read_support_intervals', 'power_trace.csv'): ('non_claim', 'clause (i), fields read: metadata.model.name and revision; summary.measurement_quality.phase_identifiability.prefill; power_trace.csv timestamp_s, interval_start_s and interval_end_s; trace digest is opaque bytes'),
    ('scripts/paper_prefill_resolvability_projection.py', 'scan_corpora', 'direct:recorded_label', 'summary_metrics.json'): ('non_claim', 'clause (i), fields read: metadata.model.name and revision; summary.measurement_quality.phase_identifiability.prefill; power_trace.csv timestamp_s, interval_start_s and interval_end_s; trace digest is opaque bytes'),
    ('scripts/paper_prefill_resolvability_projection.py', 'scan_corpora', 'direct:sha256_of', 'power_trace.csv'): ('non_claim', 'clause (i), fields read: metadata.model.name and revision; summary.measurement_quality.phase_identifiability.prefill; power_trace.csv timestamp_s, interval_start_s and interval_end_s; trace digest is opaque bytes'),
    ('scripts/run_campaign.py', '_axi_discover_finalized_bundles', 'direct:read_bytes', 'metadata.json'): ('non_claim', 'clause (i), fields read: metadata run and attempt identity for finalized-bundle discovery'),
    ('scripts/run_campaign.py', '_basis_member_occurrences', 'direct:read_bytes', 'metadata.json'): ('non_claim', 'clause (i), fields read: metadata run identity and launch lineage for member occurrence binding'),
    ('scripts/run_campaign.py', '_run_record_supersession_locked', 'direct:read_bytes', 'metadata.json'): ('non_claim', 'clause (i), fields read: metadata run identity for supersession'),
    ('scripts/run_campaign.py', 'authenticate_campaign_child_launch_lineage', 'direct:read_bytes', 'metadata.json'): ('non_claim', 'clause (i), fields read: metadata launch lineage and completion identity'),
    ('scripts/run_campaign.py', 'evaluate_member', 'direct:read_text', 'metadata.json'): ('behind_gate', CAMPAIGN_CONSUMERS_REASON, CAMPAIGN_CONSUMERS_EVIDENCE),
    ('scripts/run_campaign.py', 'evaluate_member', 'direct:read_text', 'summary_metrics.json'): ('behind_gate', CAMPAIGN_CONSUMERS_REASON, CAMPAIGN_CONSUMERS_EVIDENCE),
    ('scripts/run_campaign.py', 'evaluate_member', 'direct:summary_status', 'summary_metrics.json'): ('behind_gate', CAMPAIGN_CONSUMERS_REASON, CAMPAIGN_CONSUMERS_EVIDENCE),
    ('scripts/run_campaign.py', 'existing_state', 'direct:summary_status', 'summary_metrics.json'): ('non_claim', 'clause (i), fields read: summary.status only'),
    ('scripts/run_campaign.py', 'run_axi_spec_campaign', 'direct:read_bytes', 'metadata.json'): ('non_claim', 'clause (i), fields read: metadata.batch.admitted_request_count for dispatch receipt'),
    ('scripts/run_campaign.py', 'suite_order_evidence', 'direct:_load_json_object', 'metadata.json'): ('non_claim', 'clause (i), fields read: metadata suite order, run identity and seed'),
    ('scripts/summarize_g2a_prefill_probe.py', 'summarize', 'direct:_load_json', 'metadata.json'): ('non_claim', 'clause (i), fields read: metadata.run_id and workload_provenance.prompt.realized_token_count and token_ids_sha256'),
    ('scripts/summarize_g2a_prefill_probe.py', 'summarize', 'direct:_load_json', 'summary_metrics.json'): ('non_claim', 'clause (i), fields read: summary.window_evidence_precheck.phase.prefill.windows[0].in_window_sample_count'),
    ('scripts/validate_powermetrics_fiducial.py', 'main', 'direct:_write_text_artifact', 'power_trace.csv'): ('non_claim', 'clause (i), fields read: none; this call writes the new trace artifact'),
    ('scripts/validate_powermetrics_fiducial.py', 'main', 'direct:sha256_path', 'power_trace.csv'): ('non_claim', 'clause (i), fields read: none; hashes the trace as opaque bytes'),
}

GATE_BODIES = {
    ("joulewise/battery_float.py", "authenticate_bundle"),
    ("joulewise/bundle_read.py", "authenticate_window_members"),
    ("joulewise/bundle_read.py", "BundleReader.metadata"),
}
TOLERANT_DEFINITIONS = {
    ("joulewise/bundle_read.py", "BundleReader.raw_metadata", "direct:_tolerant_json", "metadata.json"),
    ("joulewise/bundle_read.py", "BundleReader.raw_summary", "direct:_tolerant_json", "summary_metrics.json"),
}
READER_METHODS = {
    "metadata": "gate", "trace_rows": "gated_energy", "summed_curve": "gated_energy",
    "source_curve": "gated_energy", "measured_window": "gated_energy",
    "raw_metadata": "tolerant", "raw_config": "tolerant", "raw_summary": "tolerant",
    "raw_artifact_bytes": "tolerant", "events": "journal",
    **{name: "other" for name in (
        "path", "config", "problems", "is_complete", "is_event_v2",
        "is_frozen_legacy_identity", "rail_manifest", "request_roster",
        "request_rows", "request_token_rows", "request_phase_windows",
        "runtime_cleanup_ok", "phase_windows", "token_timestamps",
        "suite_manifest", "suite_item_records", "suite_window", "item_windows",
        "block_windows", "level_windows")},
}
JOURNAL_ENERGY_READERS = {
    "joulewise/cli.py::_strict_uncertainty_evidence_problems",
    "joulewise/reduce.py::_reduce_v060",
    "scripts/analyze_phase_share.py::analyze_bundle",
    "scripts/paper/partial_record_enclosure.py::_derive_bundle_authenticated",
}

# 58(f): checked inventory, including names reached through cross-module constants.
# Capture functions are classified by what leaves them; energy entries need a gate.
RAW_CAPTURE_READERS = {
    "joulewise/calibration_bracketing.py::_load_calibration_candidate_unbounded": (
        "energy", ("capture_chain", (
            "joulewise/calibration_bracketing.py::load_calibration_candidate.inspect",
            "joulewise/calibration_bracketing.py::load_calibration_candidate",
            "joulewise/calibration_bracketing.py::_candidate_from_observation",
            "joulewise/calibration_bracketing.py::discover_calibration_candidates"))),
    "joulewise/cli.py::_strict_rich_telemetry_problems": ("validation", None),
    "joulewise/cli.py::_strict_uncertainty_evidence_problems": ("validation", None),
    "joulewise/cli.py::_verify_powermetrics_raw_to_trace": ("validation", None),
    "joulewise/controller.py::_load_instrument_calibration_attachment": ("energy", "capture_in_function"),
    "joulewise/environment_admission.py::_window_thermal_pressure_refusals": ("validation", None),
    "joulewise/calibration_ledger.py::_artifact_hashes_unbounded": ("custody", None),
    "joulewise/calibration_ledger.py::_custody_state": ("custody", None),
    "joulewise/calibration_ledger.py::_custody_state_unbounded": ("custody", None),
    "joulewise/calibration_ledger.py::_custody_store_manifest_projection": ("names", None),
    "joulewise/calibration_ledger.py::_custody_store_reasons": ("custody", None),
    "joulewise/calibration_ledger.py::_governed_raw_nofollow_unbounded": ("custody", None),
    "joulewise/calibration_ledger.py::_historical_import_table": ("names", None),
    "joulewise/calibration_ledger.py::_inspect_historical_candidate": ("custody", None),
    "joulewise/calibration_ledger.py::artifact_hashes": ("custody", None),
    "joulewise/calibration_ledger.py::resume_finalize_bracket_session": ("custody", None),
    "joulewise/idle_dependence.py::_base_payload": ("names", None),
    "joulewise/idle_dependence.py::derive_idle_mean_uncertainty": ("energy", ("joulewise/reduce.py::_reduce", "joulewise/reduce.py::_reduce_v060", "joulewise/reduce.py::reduce_bundle")),
    "joulewise/powermetrics_fiducial.py::instrument_evidence": ("names", None),
    "joulewise/publication_privacy.py::_audit_idle_mean_uncertainty": ("names", None),
    "joulewise/publication_privacy.py::_path_policy": ("names", None),
    "joulewise/receipt_oracle.py::derive_bracket_session_receipt_oracle": ("names", None),
    "joulewise/reduce.py::_derive_anchor_context": ("energy", ("joulewise/reduce.py::_reduce", "joulewise/reduce.py::_reduce_v060", "joulewise/reduce.py::reduce_bundle")),
    "joulewise/reduce.py::_verify_instrument_calibration": (
        "energy", ("joulewise/reduce.py::_derive_anchor_context",
                   "joulewise/whole_window.py::AuthenticatedConsumptionSession._prepare",
                   "joulewise/whole_window.py::_current_core_rederivation_reasons")),
    "joulewise/salvage_dangler.py::_expected_idle_artifact_sets": ("names", None),
    "joulewise/schemas.py::SummaryMetrics.json_schema": ("names", None),
    "joulewise/uncertainty_evidence.py::derive_idle_drift_evidence": ("names", None),
    "joulewise/window_duration_margins.py::_observe_member": ("custody", None),
    "scripts/calibration_cadence_report.py::capture_paths": ("custody", None),
    "scripts/calibration_cadence_report.py::report_window": ("timing", None),
    "scripts/check_paper_replay_fence.py::locate_raw_powermetrics": ("custody", None),
    "scripts/check_paper_replay_fence.py::derive_from_artifacts": ("energy", ("lane", "BFGS-RAWCAPTURE-01")),
    "scripts/check_paper_round7_artifacts.py::_required_corpus_paths": ("names", None),
    "scripts/floor_reconciliation_receipt.py::_anchored_records": ("energy", ("scripts/floor_reconciliation_receipt.py::_bundle_row",)),
    "scripts/floor_reconciliation_receipt.py::_bundle_row": ("energy", "in_function"),
    "scripts/floor_reconciliation_receipt.py::build_receipt": ("custody", None),
    "scripts/hydrate_d117_fixture.py::_validate_archive": ("names", None),
    "scripts/hydrate_d117_fixture.py::load_descriptor": ("names", None),
    "scripts/issue_calibration_acceptance_generation.py::_derivation_frame_cadence": ("timing", None),
    "scripts/package_d117_fixture.py::load_census_bytes": ("names", None),
    "scripts/paper_anchor_correction_quantified.py::locate_raw_powermetrics": ("custody", None),
    "scripts/paper_anchor_correction_quantified.py::analyse_capture": ("energy", ("lane", "BFGS-RAWCAPTURE-01")),
    "scripts/paper_excursion_decomposition.py::build_payload": ("names", None),
    "scripts/paper_excursion_decomposition.py::locate_raw_powermetrics": ("custody", None),
    "scripts/paper_excursion_decomposition.py::rederive": ("energy", ("lane", "BFGS-RAWCAPTURE-01")),
    "scripts/run_campaign.py::assert_production_uncertainty": ("custody", None),
    "scripts/validate_powermetrics_fiducial.py::main": ("energy", ("lane", "BFGS-RAWCAPTURE-01")),
    "scripts/validate_powermetrics_fiducial.py::rederive_artifact": ("energy", ("lane", "BFGS-RAWCAPTURE-01")),
}

RAW_CAPTURE_LANE_MEMBERS = {
    "scripts/check_paper_replay_fence.py::derive_from_artifacts",
    "scripts/paper_anchor_correction_quantified.py::analyse_capture",
    "scripts/paper_excursion_decomposition.py::rederive",
    "scripts/validate_powermetrics_fiducial.py::main",
    "scripts/validate_powermetrics_fiducial.py::rederive_artifact",
}

CAPTURE_PATTERN = re.compile(r"^(raw/)?(powermetrics[A-Za-z0-9_]*\.plist|nvidia_smi[^ /]*\.csv)$")


def capture_readers(files):
    """58(f)2-3: exact screen by literal and module/class capture names."""
    files = {path: source for path, source in files.items()
             if path.startswith(("joulewise/", "scripts/"))}
    trees = {path: ast.parse(source, filename=path) for path, source in files.items()}
    names = set()
    def is_capture(n):
        return isinstance(n, ast.Constant) and isinstance(n.value, str) and bool(CAPTURE_PATTERN.fullmatch(n.value))
    changed = True
    while changed:
        changed = False
        for tree in trees.values():
            bodies = [tree.body] + [n.body for n in tree.body if isinstance(n, ast.ClassDef)]
            for body in bodies:
                for n in body:
                    if isinstance(n, ast.Assign): pairs = [(t, n.value) for t in n.targets]
                    elif isinstance(n, ast.AnnAssign) and n.value is not None: pairs = [(n.target, n.value)]
                    else: continue
                    for target, value in pairs:
                        if isinstance(target, ast.Name) and (any(is_capture(x) for x in ast.walk(value))
                                or any(isinstance(x, ast.Name) and x.id in names for x in ast.walk(value))):
                            if target.id not in names: names.add(target.id); changed = True
    found = set()
    for path, tree in trees.items():
        if path.startswith("joulewise/adapters/"): continue
        for qualname, fn in qualified(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)): continue
            nodes = own_nodes(fn)
            if any(is_capture(n) or isinstance(n, ast.Name) and n.id in names
                   or isinstance(n, ast.Attribute) and n.attr.isupper() and n.attr in names
                   for n, _ in nodes):
                found.add(f"{path}::{qualname}")
    return found


def validation_shape(files, key):
    path, qualname = key.split("::", 1)
    fn = dict(qualified(ast.parse(files[path]))).get(qualname)
    return (isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef))
            and fn.returns is not None and ast.unparse(fn.returns) in
            {"list[str]", "tuple[str, ...]", "set[str]", "bool"})


def capture_in_function_violations(files, key):
    path, qualname = key.split("::", 1)
    fn = dict(qualified(ast.parse(files[path]))).get(qualname)
    if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return [f"{key}: capture function missing"]
    body = fn.body
    for index, stmt in enumerate(body[:-1]):
        if not (isinstance(stmt, ast.Assign) and len(stmt.targets) == 1
                and isinstance(stmt.targets[0], ast.Name)
                and isinstance(stmt.value, ast.Call)
                and ast.unparse(stmt.value.func) == "battery_float.authenticate_capture"):
            continue
        verdict = stmt.targets[0].id
        refusal = body[index + 1]
        test = refusal.test if isinstance(refusal, ast.If) else None
        valid_test = (isinstance(test, ast.Compare) and len(test.ops) == 1
                      and isinstance(test.ops[0], ast.NotEq)
                      and len(test.comparators) == 1
                      and isinstance(test.comparators[0], ast.Constant)
                      and test.comparators[0].value == "pass"
                      and isinstance(test.left, ast.Attribute) and test.left.attr == "status"
                      and isinstance(test.left.value, ast.Name) and test.left.value.id == verdict)
        if not (valid_test
                and refusal.body and isinstance(refusal.body[-1], ast.Raise)):
            continue
        capture_mentions = [i for i, item in enumerate(body)
                            if any((isinstance(node, ast.Constant)
                                    and isinstance(node.value, str)
                                    and CAPTURE_PATTERN.fullmatch(node.value))
                                   or (isinstance(node, ast.Name) and node.id.isupper()
                                       and ("POWERMETRICS" in node.id or "NVIDIA_SMI" in node.id))
                                   for node in ast.walk(item))]
        if any(i <= index + 1 for i in capture_mentions):
            return [f"{key}: capture named before refusal"]
        return []
    return [f"{key}: capture gate/refusal missing or malformed"]


def capture_chain_violations(files, key, chain):
    problems = []
    names = [key.split("::", 1)[1].split(".")[-1]]
    for scope in chain:
        sites = call_sites(files, names[-1], include_references=True)
        # `inspect` is a local nested closure; unrelated functions of that
        # common name in other modules are not references to this binding.
        if names[-1] == "inspect":
            sites = [site for site in sites if site[0] == key.split("::", 1)[0]]
        if not sites or any(f"{path}::{qualname}" != scope for path, qualname, _, _ in sites):
            problems.append(f"{key}: capture chain caller/reference of {names[-1]} outside {scope}: "
                            + ", ".join(f"{path}::{qualname}" for path, qualname, _, _ in sites))
        names.append(scope.split("::", 1)[1].split(".")[-1])
    final_path, final_scope = chain[-1].split("::", 1)
    fn = dict(qualified(ast.parse(files[final_path]))).get(final_scope)
    if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return problems + [f"{key}: capture chain final scope missing"]
    expected_name = names[-2]
    found = False
    for block in ast.walk(fn):
        if not isinstance(block, (ast.Module, ast.If, ast.For, ast.While, ast.Try,
                                  ast.With, ast.AsyncFor, ast.AsyncWith,
                                  ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        body = getattr(block, "body", ())
        if not isinstance(body, list):
            continue
        for first, second in zip(body, body[1:]):
            if not (isinstance(first, ast.If) and len(first.body) == 1
                    and isinstance(first.body[0], ast.Continue)):
                continue
            test = first.test
            if not (isinstance(test, ast.Compare) and len(test.ops) == 1
                    and isinstance(test.ops[0], ast.IsNot)
                    and len(test.comparators) == 1
                    and isinstance(test.comparators[0], ast.Constant)
                    and test.comparators[0].value is None
                    and isinstance(test.left, ast.Call)
                    and name_of(test.left) == "_battery_exclusion_for_observation"
                    and len(test.left.args) == 1
                    and isinstance(test.left.args[0], ast.Name)):
                continue
            observation = test.left.args[0].id
            if any(isinstance(n, ast.Call) and name_of(n) == expected_name
                   and n.args and isinstance(n.args[0], ast.Name)
                   and n.args[0].id == observation for n in ast.walk(second)):
                found = True
    if not found:
        problems.append(f"{key}: {final_scope} lacks adjacent battery exclusion and {expected_name} call")
    for scope, expected in (
        ("_battery_exclusion_for_observation", "_battery_classification_for_observation"),
        ("_battery_classification_for_observation", "authenticate_capture"),
    ):
        fn = dict(qualified(ast.parse(files[final_path]))).get(scope)
        if fn is None or not any(isinstance(n, ast.Call) and name_of(n) == expected
                                 for n in ast.walk(fn)):
            problems.append(f"{key}: {scope} lacks {expected}")
    return problems


def raw_capture_callers_violations(files, key, listed):
    helper = key.split("::", 1)[1].split(".")[-1]
    sites = call_sites(files, helper, include_references=True)
    problems = []
    for path, qualname, node, chain in sites:
        scope = f"{path}::{qualname}"
        if scope not in listed:
            problems.append(f"{key}: unlisted raw-capture caller/reference {scope}")
            continue
        fn = dict(qualified(ast.parse(files[path]))).get(qualname)
        if gate_dominates_call(path, fn, node, chain):
            continue
        member = RAW_CAPTURE_READERS.get(scope)
        if member is not None and member[0] == "energy" and member[1] is not None:
            continue
        if validation_shape(files, scope):
            continue
        problems.append(f"{key}: ungated raw-capture caller {scope}")
    return problems


def tracked_sources(root=ROOT, replacements=None):
    files = {name: (root / name).read_text() for name in tracked(root)}
    files.update(replacements or {})
    return files


def functions(files):
    for path, source in files.items():
        for qualname, node in qualified(ast.parse(source, filename=path)):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                yield path, qualname, node


def scopes(files):
    for path, source in files.items():
        for qualname, node in qualified(ast.parse(source, filename=path)):
            yield path, qualname, node


def call_sites(files, name, *, attribute_only=False, include_references=False):
    out = []
    for path, qualname, fn in scopes(files):
        nodes = own_nodes(fn)
        callees = {id(n.func) for n, _ in nodes if isinstance(n, ast.Call)}
        for node, chain in nodes:
            if isinstance(node, ast.Call) and name_of(node) == name:
                if not attribute_only or isinstance(node.func, ast.Attribute):
                    out.append((path, qualname, node, chain))
            if include_references and isinstance(node, (ast.Name, ast.Attribute)):
                found = node.id if isinstance(node, ast.Name) else node.attr
                if found == name and id(node) not in callees:
                    out.append((path, qualname, node, chain))
    return out


def scope_gates(path, fn, nodes):
    tree = ast.parse((ROOT / path).read_text()) if (ROOT / path).exists() else None
    imported = path == "joulewise/bundle_read.py" or bool(tree and any(
        isinstance(n, ast.ImportFrom) and n.module == "joulewise.bundle_read"
        and any(a.name == "authenticate_window_members" and a.asname is None for a in n.names)
        for n in tree.body))
    readers = set()
    if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
        readers = {a.arg for a in [*fn.args.posonlyargs, *fn.args.args, *fn.args.kwonlyargs]
                   if a.annotation is not None and "BundleReader" in ast.dump(a.annotation)}
    for node, _ in nodes:
        if isinstance(node, (ast.Assign, ast.AnnAssign)) and isinstance(node.value, ast.Call) and name_of(node.value) == "BundleReader":
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            readers.update(t.id for t in targets if isinstance(t, ast.Name))
    gates = []
    for node, chain in nodes:
        if not isinstance(node, ast.Call): continue
        if (name_of(node) == "authenticate_window_members" and isinstance(node.func, ast.Name)
                and imported):
            gates.append((node, chain))
        elif name_of(node) == "metadata" and isinstance(node.func, ast.Attribute):
            recv = node.func.value
            if (isinstance(recv, ast.Name) and recv.id in readers) or (
                    isinstance(recv, ast.Call) and name_of(recv) == "BundleReader"):
                gates.append((node, chain))
    return gates


def gate_dominates_call(path, fn, node, chain, nodes=None):
    nodes = nodes if nodes is not None else own_nodes(fn)
    return any((gate.lineno, gate.col_offset) < (node.lineno, node.col_offset)
               and dominates(gchain, chain) for gate, gchain in scope_gates(path, fn, nodes))


def callers_violations(files, helper, listed, allowlist):
    """51(f), 59(b), 62(b): include references and intermediate callers."""
    scope_by_key = {f"{p}::{q}": (p, q, fn) for p, q, fn in scopes(files)}
    problems = []
    def visit(name, seen):
        for path, qualname, node, chain in call_sites(files, name, include_references=True):
            key = f"{path}::{qualname}"
            if key not in listed:
                problems.append(f"{name}: unlisted caller/reference {key}:{node.lineno}")
                continue
            if key in seen:
                problems.append(f"{name}: recursive caller chain {key}")
                continue
            _, _, fn = scope_by_key[key]
            if gate_dominates_call(path, fn, node, chain): continue
            if any(p == path and q == qualname and row[0] == "behind_gate"
                   for (p, q, _, _), row in allowlist.items()):
                continue
            visit(qualname.split(".")[-1], seen | {key})
    visit(helper, set())
    return problems


def consumers_violations(files, consumers):
    scopes_by_key = {f"{p}::{q}": fn for p, q, fn in scopes(files)}
    problems = []
    for key, callee in consumers:
        fn = scopes_by_key.get(key)
        if fn is None:
            problems.append(f"{key}: consuming scope missing"); continue
        path = key.split("::", 1)[0]
        calls = [(n, ch) for n, ch in own_nodes(fn) if isinstance(n, ast.Call)
                 and name_of(n) == callee]
        if not calls:
            problems.append(f"{key}: consuming call {callee} missing")
        for node, chain in calls:
            if not gate_dominates_call(path, fn, node, chain):
                problems.append(f"{key}:{node.lineno}: {callee} is not gated")
    return problems


def consumers_form_violations(files, key, evidence, reason):
    if not isinstance(evidence, dict) or set(evidence) != {
            "consumers", "collection_uses", "producers"}:
        return [f"{key}: consumers form fields missing"]
    problems = []
    if reason != CAMPAIGN_CONSUMERS_REASON:
        problems.append(f"{key}: consumers reason differs from amendment 76")
    if evidence["consumers"] != CAMPAIGN_VERDICT_USES:
        problems.append(f"{key}: verdict uses differ")
    problems += consumers_violations(files, evidence["consumers"])
    if not evidence["collection_uses"] or evidence["collection_uses"] != CAMPAIGN_COLLECTION_USES:
        problems.append(f"{key}: collection uses missing or differ")
    scopes_by_key = {f"{p}::{q}": fn for p, q, fn in scopes(files)}
    for scope, callee in evidence["collection_uses"]:
        fn = scopes_by_key.get(scope)
        if fn is None or not any(isinstance(n, ast.Call) and name_of(n) == callee
                                 for n, _ in own_nodes(fn)):
            problems.append(f"{key}: collection use {scope}::{callee} missing")
    producers = evidence["producers"]
    if producers != CAMPAIGN_PRODUCERS:
        problems.append(f"{key}: producers differ")
    allowed = {scope for scope, _ in evidence["consumers"]}
    allowed.update(f"scripts/run_campaign.py::{name}" for name in producers)
    for producer in producers:
        for path, qualname, node, _ in call_sites(files, producer, include_references=True):
            scope = f"{path}::{qualname}"
            if scope not in allowed:
                problems.append(f"{key}: producer {producer} has unlisted caller/reference {scope}")
    return problems


def content_violations(path, source, qualname):
    """57(b)3: source content must not leave before a dominating verdict."""
    fn = dict(qualified(ast.parse(source))).get(qualname)
    if fn is None:
        return [f"{path}::{qualname}: missing gate body"]
    nodes = own_nodes(fn)
    content = set()
    def mentions(expr):
        return any(isinstance(n, ast.Name) and n.id in content for n in ast.walk(expr))
    def is_read(call):
        return (name_of(call) not in NON_READING and
                any(const_hit(part) for part in [*call.args, *(k.value for k in call.keywords)]))
    changed = True
    while changed:
        changed = False
        for n, _ in nodes:
            if isinstance(n, ast.Assign): pairs = [(t, n.value) for t in n.targets]
            elif isinstance(n, (ast.AnnAssign, ast.NamedExpr)) and n.value is not None:
                pairs = [(n.target, n.value)]
            elif isinstance(n, (ast.For, ast.AsyncFor, ast.comprehension)):
                pairs = [(n.target, n.iter)]
            else: continue
            for target, value in pairs:
                if isinstance(value, ast.Call) and name_of(value) in {"_battery_verdict", "authenticate_bundle", "authenticate_pair"}:
                    continue
                if mentions(value) or any(isinstance(c, ast.Call) and is_read(c) for c in ast.walk(value)):
                    for t in ast.walk(target):
                        if isinstance(t, ast.Name) and isinstance(t.ctx, ast.Store) and t.id not in content:
                            content.add(t.id); changed = True
    verdicts = [(n, chain) for n, chain in nodes if isinstance(n, ast.Call)
                and name_of(n) in {"_battery_verdict", "authenticate_bundle", "authenticate_pair"}]
    problems = []
    if not content: problems.append(f"{path}::{qualname}: no watched content name")
    if not verdicts: problems.append(f"{path}::{qualname}: no verdict call")
    for n, chain in nodes:
        leaving = False
        if isinstance(n, (ast.Return, ast.Yield, ast.YieldFrom)) and n.value is not None:
            leaving = mentions(n.value)
        elif isinstance(n, (ast.Assign, ast.AnnAssign)) and n.value is not None:
            targets = n.targets if isinstance(n, ast.Assign) else [n.target]
            leaving = mentions(n.value) and any(isinstance(t, (ast.Attribute, ast.Subscript)) for t in targets)
        if leaving and not any((v.lineno, v.col_offset) < (n.lineno, n.col_offset)
                               and dominates(vc, chain) for v, vc in verdicts):
            problems.append(f"{path}::{qualname}:{n.lineno}: content leaves before verdict")
    return problems


def gate_binding_violations(files):
    problems = []
    gate_names = {"authenticate_window_members", "BundleReader"}
    for path, source in files.items():
        # 68(d) widens read sites and callers, not the closed 57(b) gate-body
        # binding rule. Paper code may import a re-exported BundleReader.
        if not path.startswith(("joulewise/", "scripts/")):
            continue
        tree = ast.parse(source, filename=path)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name in gate_names and (node.module != "joulewise.bundle_read" or alias.asname):
                        problems.append(f"{path}:{node.lineno}: gate name import")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.asname in gate_names: problems.append(f"{path}:{node.lineno}: gate name import")
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.name in gate_names and (path != "joulewise/bundle_read.py" or
                                           not (isinstance(node, ast.ClassDef) and node.name == "BundleReader")
                                           and not (isinstance(node, ast.FunctionDef) and node.name == "authenticate_window_members" and node in tree.body)):
                    problems.append(f"{path}:{node.lineno}: gate name definition")
                if isinstance(node, ast.ClassDef) and any(isinstance(b, ast.Name) and b.id == "BundleReader" for b in node.bases):
                    problems.append(f"{path}:{node.lineno}: BundleReader subclass")
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for arg in [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]:
                        if arg.arg in gate_names: problems.append(f"{path}:{arg.lineno}: gate name parameter")
            elif isinstance(node, ast.Name) and node.id in gate_names and isinstance(node.ctx, (ast.Store, ast.Del)):
                problems.append(f"{path}:{node.lineno}: gate name rebound")
            elif isinstance(node, (ast.Global, ast.Nonlocal)) and gate_names.intersection(node.names):
                problems.append(f"{path}:{node.lineno}: gate name global/nonlocal")
            elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.Delete)):
                targets = node.targets if hasattr(node, "targets") else [node.target]
                if any(isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name)
                       and t.value.id in gate_names for target in targets for t in ast.walk(target)):
                    problems.append(f"{path}:{node.lineno}: gate attribute mutation")
            elif isinstance(node, ast.Call) and name_of(node) in {"setattr", "delattr"} and node.args:
                if isinstance(node.args[0], ast.Name) and node.args[0].id in gate_names:
                    problems.append(f"{path}:{node.lineno}: gate attribute mutation")
    return problems


def cache_violations(files):
    """57(b)4: no other code can populate the metadata cache slot."""
    problems = []
    for path, source in files.items():
        if not path.startswith(("joulewise/", "scripts/")):
            continue
        tree = ast.parse(source, filename=path)
        for node in ast.walk(tree):
            if (isinstance(node, ast.Constant) and node.value == "_cache") or (
                    isinstance(node, ast.keyword) and node.arg == "_cache"):
                problems.append(f"{path}:{node.lineno}: _cache named indirectly")
        for qualname, fn in qualified(tree):
            nodes = own_nodes(fn)
            parents = {id(child): parent for parent, _ in nodes for child in ast.iter_child_nodes(parent)}
            bindings = {}
            for n, _ in nodes:
                if isinstance(n, ast.Assign): pairs = [(t, n.value) for t in n.targets]
                elif isinstance(n, ast.AnnAssign) and n.value is not None: pairs = [(n.target, n.value)]
                else: pairs = []
                for target, value in pairs:
                    if isinstance(target, ast.Name): bindings.setdefault(target.id, []).append(value)
            for n, _ in nodes:
                if not isinstance(n, ast.Attribute) or n.attr != "_cache": continue
                place = f"{path}::{qualname}:{n.lineno}"
                if path != "joulewise/bundle_read.py" or not qualname.startswith("BundleReader."):
                    problems.append(place + ": external _cache access"); continue
                if not isinstance(n.value, ast.Name) or n.value.id != "self":
                    problems.append(place + ": _cache receiver is not self"); continue
                parent = parents.get(id(n))
                if isinstance(parent, ast.AnnAssign) and parent.target is n:
                    if qualname != "BundleReader.__init__" or not isinstance(parent.value, ast.Dict) or parent.value.keys:
                        problems.append(place + ": _cache initializer is not empty")
                elif isinstance(parent, ast.Assign) and n in parent.targets:
                    if qualname != "BundleReader.__init__" or not isinstance(parent.value, ast.Dict) or parent.value.keys:
                        problems.append(place + ": _cache initializer is not empty")
                elif isinstance(parent, ast.Compare) and any(isinstance(op, (ast.In, ast.NotIn)) for op in parent.ops):
                    pass
                elif isinstance(parent, ast.Subscript) and parent.value is n:
                    if isinstance(parent.ctx, ast.Store):
                        key = parent.slice
                        if isinstance(key, ast.Constant) and isinstance(key.value, str):
                            if key.value == "metadata" and qualname != "BundleReader.metadata":
                                problems.append(place + ": metadata slot written outside gate")
                        elif isinstance(key, ast.Name):
                            values = bindings.get(key.id, [])
                            if not (len(values) == 1 and isinstance(values[0], ast.JoinedStr)
                                    and values[0].values and isinstance(values[0].values[0], ast.Constant)
                                    and isinstance(values[0].values[0].value, str)
                                    and values[0].values[0].value.endswith(":")):
                                problems.append(place + ": dynamic cache key")
                        else:
                            problems.append(place + ": unsupported cache key")
                else:
                    problems.append(place + ": unsupported _cache use")
    return problems


def gate_body_violations(files):
    problems = gate_binding_violations(files) + cache_violations(files)
    br = ast.parse(files["joulewise/bundle_read.py"])
    tops = [n for n in br.body if isinstance(n, ast.FunctionDef)
            and n.name == "authenticate_window_members"]
    classes = [n for n in br.body if isinstance(n, ast.ClassDef) and n.name == "BundleReader"]
    if len(tops) != 1 or len(classes) != 1 or sum(
            isinstance(n, ast.FunctionDef) and n.name == "metadata" for n in classes[0].body) != 1:
        problems.append("gate definitions are not unique")
    for path, qualname in GATE_BODIES:
        problems += content_violations(path, files[path], qualname)
    for path, qualname, node, _ in call_sites(files, "authenticate_bundle"):
        if (path, qualname) != ("joulewise/bundle_read.py", "BundleReader._battery_verdict"):
            problems.append(f"{path}::{qualname}:{node.lineno}: verdict source outside gate")
    for path, qualname, node, _ in call_sites(files, "_battery_verdict", attribute_only=True):
        if (path, qualname) not in GATE_BODIES:
            problems.append(f"{path}::{qualname}:{node.lineno}: verdict method outside gate")
    return problems


def reader_method_violations(files):
    tree = ast.parse(files["joulewise/bundle_read.py"])
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "BundleReader")
    methods = {n.name: n for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
               and not n.name.startswith("_")}
    problems = []
    if set(methods) != set(READER_METHODS):
        problems.append(f"reader methods differ: missing={sorted(set(READER_METHODS)-set(methods))} added={sorted(set(methods)-set(READER_METHODS))}")
    if {name for name, kind in READER_METHODS.items() if kind == "tolerant"} != TOLERANT:
        problems.append("tolerant method table differs from detector")
    if {name for name, kind in READER_METHODS.items() if kind == "gate"} != {"metadata"}:
        problems.append("reader gate method differs from closed definition")
    if {name for name, kind in READER_METHODS.items() if kind == "gated_energy"} != {
            "trace_rows", "summed_curve", "source_curve", "measured_window"}:
        problems.append("reader gated energy methods differ")
    if {name for name, kind in READER_METHODS.items() if kind == "journal"} != {"events"}:
        problems.append("reader journal method differs from events")
    for name, kind in READER_METHODS.items():
        fn = methods.get(name)
        if fn is None: continue
        body = [n for n in fn.body if not (isinstance(n, ast.Expr) and
                isinstance(n.value, ast.Constant) and isinstance(n.value.value, str))]
        if kind == "gated_energy":
            if not body or ast.unparse(body[0]) != "self.metadata()":
                problems.append(f"{name}: first statement does not gate")
        elif kind == "journal":
            if not any(isinstance(n, ast.Constant) and n.value == "events.jsonl" for n in ast.walk(fn)):
                problems.append(f"{name}: journal filename missing")
    return problems


def tolerant_definition_violations(files):
    tree = ast.parse(files["joulewise/bundle_read.py"])
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "BundleReader")
    methods = {n.name: n for n in cls.body if isinstance(n, ast.FunctionDef)}
    problems = []
    for name, watched in (("raw_metadata", "metadata.json"), ("raw_summary", "summary_metrics.json")):
        fn = methods[name]
        body = [n for n in fn.body if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant))]
        if not (name in TOLERANT and len(body) == 1 and isinstance(body[0], ast.Return)
                and isinstance(body[0].value, ast.Call)
                and ast.unparse(body[0].value.func) == "self._tolerant_json"
                and len(body[0].value.args) == 1
                and isinstance(body[0].value.args[0], ast.Constant)
                and body[0].value.args[0].value == watched):
            problems.append(f"{name}: tolerant definition changed")
    return problems


def journal_energy_readers(files):
    out = set()
    pattern = re.compile(r"power_w|energy|idle_power|joules|_j$")
    for path, qualname, fn in functions(files):
        if not path.startswith(("joulewise/", "scripts/")):
            continue
        nodes = own_nodes(fn)
        has_journal = any(
            isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
            and n.func.attr in {"events", "_strict_jsonl_objects"} or
            isinstance(n, ast.Constant) and isinstance(n.value, str)
            and (n.value == "events.jsonl" or n.value.endswith("/events.jsonl"))
            for n, _ in nodes)
        has_key = any(isinstance(n, ast.Constant) and isinstance(n.value, str)
                      and len(n.value) <= 40 and " " not in n.value
                      and pattern.search(n.value) for n, _ in nodes)
        if has_journal and has_key: out.add(f"{path}::{qualname}")
    return out


def allowlist_violations(files, allowlist=ALLOWLIST):
    rows, _ = sweep_files(files)
    actual = site_keys(rows)
    expected = set(allowlist)
    problems = [f"unlisted read {key}" for key in sorted(actual - expected)]
    problems += swept_file_violations(all_tracked_python())
    problems += [f"stale allowlist row {key}" for key in sorted(expected - actual)]
    classes = {"strict_validation", "non_claim", "historical", "behind_gate",
               "gate_body", "tolerant_definition"}
    for key, entry in allowlist.items():
        if len(entry) not in {2, 3} or entry[0] not in classes or not entry[1]:
            problems.append(f"invalid class/reason {key}")
            continue
        cls, reason = entry[:2]
        third = entry[2] if len(entry) == 3 else None
        if "only to" in reason.lower() or "reach only" in reason.lower():
            problems.append(f"R58-5 unsupported exclusive reason {key}")
        if cls == "non_claim":
            if "clause (i)" not in reason and "clause (ii)" not in reason:
                problems.append(f"non_claim clause missing {key}")
            if "tested and dropped" in reason and not all(
                    marker in reason for marker in ("fields that leave:", "test:")):
                problems.append(f"non_claim tested-and-dropped evidence missing {key}")
            if "clause (ii)" in reason and "output:" not in reason:
                problems.append(f"non_claim output missing {key}")
            if isinstance(third, dict) and third.get("callers") == ():
                problems += callers_violations(files, key[1].split(".")[-1], (), allowlist)
        if cls != "behind_gate" and any(s in reason.lower() for s in
               ("metadata first", "follows bundlereader.metadata")):
            problems.append(f"unverified gate statement in reason {key}")
        if key == ("joulewise/idle_dependence.py", "derive_idle_mean_uncertainty",
                   "raw_artifact_bytes", "-") and cls not in {"behind_gate", "historical"}:
            if cls != "non_claim" or "clause (ii)" not in reason:
                problems.append(f"R58-5 energy-return class invalid {key}")
        if cls == "behind_gate":
            if not isinstance(third, dict):
                problems.append(f"behind_gate evidence missing {key}")
            elif "callers" in third:
                if set(third) != {"callers"}:
                    problems.append(f"behind_gate callers fields differ {key}")
                problems += callers_violations(files, key[1].split(".")[-1],
                                               third["callers"], allowlist)
            elif "consumers" in third:
                problems += consumers_form_violations(files, key, third, reason)
            else:
                problems.append(f"unknown behind_gate form {key}")
    gate_keys = {key for key, value in allowlist.items() if value[0] == "gate_body"}
    if gate_keys != {
        ("joulewise/battery_float.py", "authenticate_bundle", "direct:_required_object", "metadata.json"),
        ("joulewise/bundle_read.py", "BundleReader.metadata", "direct:_strict_json", "metadata.json"),
        ("joulewise/bundle_read.py", "authenticate_window_members", "direct:_strict_json", "metadata.json"),
    }:
        problems.append("gate_body keys differ from the three closed definitions")
    tolerant_keys = {key for key, value in allowlist.items() if value[0] == "tolerant_definition"}
    if tolerant_keys != TOLERANT_DEFINITIONS:
        problems.append("tolerant_definition keys differ from the two closed definitions")
    historical = [key for key, value in allowlist.items() if value[0] == "historical"]
    if len(historical) != 1 or historical[0][:2] != (
            "scripts/issue_dg071_dg075_statistics.py", "main"):
        problems.append("historical class is not the single pinned amendment-41 row")
    problems += gate_body_violations(files)
    problems += tolerant_definition_violations(files)
    problems += reader_method_violations(files)
    if journal_energy_readers(files) != JOURNAL_ENERGY_READERS:
        problems.append("journal reader set differs")
    return problems


def capture_violations(files, inventory=RAW_CAPTURE_READERS):
    actual = capture_readers(files)
    expected = set(inventory)
    problems = [f"unlisted raw capture reader {key}" for key in sorted(actual - expected)]
    problems += [f"stale raw capture reader {key}" for key in sorted(expected - actual)]
    lane_members = {key for key, (kind, gate) in inventory.items()
                    if kind == "energy" and isinstance(gate, tuple)
                    and len(gate) == 2 and gate[0] == "lane"}
    if lane_members != RAW_CAPTURE_LANE_MEMBERS:
        problems.append("raw-capture lane members differ: " + repr(sorted(lane_members ^ RAW_CAPTURE_LANE_MEMBERS)))
    for key, (kind, gate) in inventory.items():
        if kind not in {"names", "custody", "timing", "validation", "energy"}:
            problems.append(f"{key}: unknown raw-capture kind {kind}")
        elif kind == "validation":
            if not validation_shape(files, key):
                problems.append(f"{key}: validation shape missing")
        elif kind == "energy" and gate is None:
            problems.append(f"{key}: energy reader has no gate")
        elif kind == "energy" and gate != "in_function" and not isinstance(gate, tuple):
            if gate == "capture_in_function":
                problems += capture_in_function_violations(files, key)
            else:
                problems.append(f"{key}: invalid energy gate declaration")
        elif kind == "energy" and isinstance(gate, tuple):
            if len(gate) == 2 and gate == ("lane", "BFGS-RAWCAPTURE-01"):
                pass
            elif len(gate) == 2 and gate[0] == "lane":
                problems.append(f"{key}: unruled raw-capture lane {gate[1]}")
            elif len(gate) == 2 and gate[0] == "capture_chain":
                problems += capture_chain_violations(files, key, gate[1])
            elif key == "joulewise/reduce.py::_verify_instrument_calibration":
                problems += raw_capture_callers_violations(files, key, gate)
            else:
                problems += callers_violations(files, key.split("::", 1)[1].split(".")[-1],
                                               gate, ALLOWLIST)
        elif kind == "energy" and gate == "in_function":
            path, qualname = key.split("::", 1)
            fn = dict(qualified(ast.parse(files[path]))).get(qualname)
            if fn is None:
                problems.append(f"{key}: function missing")
            else:
                nodes = own_nodes(fn)
                reads = [(node, chain) for node, chain in nodes
                         if isinstance(node, ast.Call)
                         and any(isinstance(child, ast.Constant) and isinstance(child.value, str)
                                 and CAPTURE_PATTERN.fullmatch(child.value)
                                 for child in ast.walk(node))
                         and name_of(node) not in PATH_BUILDERS | NON_READING]
                if not reads or any(not gate_dominates_call(path, fn, node, chain, nodes)
                                    for node, chain in reads):
                    problems.append(f"{key}: capture read is not dominated by its gate")
        elif kind != "energy" and gate is not None:
            problems.append(f"{key}: non-energy kind declares a gate")
    return problems


class DetectorExamples(unittest.TestCase):
    """R51-1..13, 18..26, R59-1/2/4/5, R57-10."""

    def check(self, source, operation, scope="f", watched="power_trace.csv", present=True):
        rows = site_keys(sweep_source("scripts/zz_new.py", source))
        match = ("scripts/zz_new.py", scope, operation, watched) in rows
        self.assertEqual(match, present, rows)

    def test_path_forms(self):
        self.check('def f(b):\n return (b / "power_trace.csv").read_bytes()', "direct:read_bytes")  # R51-1
        self.check('def f(b):\n p = b / "power_trace.csv"\n return p.read_bytes()', "direct:read_bytes")  # R51-2
        self.check('P = "power_trace.csv"\ndef f(b):\n return (b / P).read_bytes()', "direct:read_bytes")  # R51-3
        self.check('P = "power_trace.csv"\nQ = P\ndef f(b):\n return (b / Q).read_bytes()', "direct:read_bytes")  # R51-3 constant chain
        self.check('def f(b):\n return open_authentication_input(b / "power_trace.csv")', "direct:open_authentication_input")  # R51-4
        self.check('def f(b):\n return helper(b / "power_trace.csv")', "direct:helper")  # R51-8
        self.check('def f(b):\n for name, field in (("config.json", "c"), ("metadata.json", "m")):\n  (b / name).read_bytes()', "direct:read_bytes", watched="metadata.json")  # R51-9
        self.check('class K:\n def f(self,b):\n  self.trace = b / "power_trace.csv"', "store:self.trace", scope="K.f")  # R51-12

    def test_gate_identity_order_and_branches(self):
        self.check('def f(event,b):\n event.metadata()\n return (b / "power_trace.csv").read_bytes()', "direct:read_bytes")  # R51-5
        self.check('from joulewise.bundle_read import authenticate_window_members\ndef f(b):\n x=(b/"power_trace.csv").read_bytes()\n authenticate_window_members((("m",b),))\n return x', "direct:read_bytes")  # R51-6
        self.check('from joulewise.bundle_read import authenticate_window_members\ndef f(b):\n if b.is_dir(): authenticate_window_members((("m",b),))\n return (b/"power_trace.csv").read_bytes()', "direct:read_bytes")  # R51-7
        self.check('def authenticate_window_members(m): return None\ndef f(b):\n authenticate_window_members((("m",b),))\n return (b/"power_trace.csv").read_bytes()', "direct:read_bytes")  # R51-10
        self.check('from joulewise.bundle_read import authenticate_window_members\ndef f(b):\n authenticate_window_members((("m",b),))\n return (b/"power_trace.csv").read_bytes()', "direct:read_bytes", present=False)  # R51-11
        self.check('def f(r: BundleReader):\n r.metadata()\n return r.raw_summary()', "raw_summary", watched="-", present=False)  # R51-11
        self.check('def f(r: BundleReader, b):\n if b:\n  r.metadata()\n  return r.raw_summary()', "raw_summary", watched="-", present=False)  # R51-11
        self.check('def f(r: BundleReader):\n try: r.metadata()\n except Exception: pass\n return r.raw_summary()', "raw_summary", watched="-")  # R51-18
        self.check('import contextlib\ndef f(r: BundleReader):\n with contextlib.suppress(RuntimeError): r.metadata()\n return r.raw_summary()', "raw_summary", watched="-")  # R51-19
        self.check('def f(r: BundleReader):\n try: r.metadata()\n except RuntimeError: return r.raw_summary()', "raw_summary", watched="-")  # R51-20
        self.check('def f(a,b):\n BundleReader(a).metadata()\n return BundleReader(b).raw_summary()', "raw_summary", watched="-")  # R51-21
        self.check('def f(r: BundleReader):\n try: r.metadata()\n except RuntimeError: raise\n return r.raw_summary()', "raw_summary", watched="-", present=False)  # R51-22
        self.check('def f(r: BundleReader):\n try: r.metadata()\n except ValueError: raise RuntimeError()\n else: return r.raw_summary()', "raw_summary", watched="-", present=False)  # R51-22
        self.check('def f(r: BundleReader):\n try: r.metadata()\n except ValueError: return None\n return r.raw_summary()', "raw_summary", watched="-", present=False)  # R59-1
        self.check('def f(r: BundleReader):\n for x in (1,):\n  try: r.metadata()\n  except ValueError: continue\n return r.raw_summary()', "raw_summary", watched="-")  # R59-2
        self.check('def f(r: BundleReader):\n try: r.metadata()\n except RuntimeError:\n  x=r.raw_summary()\n  raise', "raw_summary", watched="-")  # R59-4
        self.check('def f(r: BundleReader):\n try: r.metadata()\n finally: x=r.raw_summary()', "raw_summary", watched="-")  # R59-5
        self.check('import joulewise.bundle_read as br\ndef f(b):\n br.authenticate_window_members((("m",b),))\n return (b/"power_trace.csv").read_bytes()', "direct:read_bytes")  # R57-10
        for rebound in ('try: pass\nexcept ValueError as policy_binding: pass',
                        'import math as policy_binding'):
            source = 'def f(policy_binding):\n ' + rebound.replace('\n', '\n ') + '\n'
            self.assertNotIn('policy_binding', stable_parameters(ast.parse(source).body[0]))

    def test_all_scopes_and_references(self):
        self.check('g = lambda r: r.raw_summary()', "raw_summary", scope="<module>", watched="-")  # R51-23
        self.check('import os\nif os.environ.get("X"):\n def f(r): return r.raw_summary()', "raw_summary", watched="-")  # R51-24
        self.check('try: pass\nexcept Exception:\n def f(r): return r.raw_summary()', "raw_summary", watched="-")  # R51-24
        self.check('if __name__ == "__main__":\n print(BundleReader("b").raw_summary())', "raw_summary", scope="<module>", watched="-")  # R51-25
        self.check('class K:\n DATA = open("b/summary_metrics.json").read()', "direct:open", scope="K.<body>", watched="summary_metrics.json")  # R51-26
        self.check('if __name__ == "__main__":\n open("b/summary_metrics.json")', "direct:open", scope="<module>", watched="summary_metrics.json")  # R51-26
        self.check('def f(r: BundleReader):\n r.metadata()\n get = r.raw_summary', "ref:raw_summary", watched="-")
        self.check('def f(r: BundleReader):\n r.metadata()\n g = lambda: r.raw_summary()\n return g()',
                   "raw_summary", scope="f", watched="-")  # R51-23b RED for inherited lambda gate
        self.check('import os\ndef f(r: BundleReader):\n r.metadata()\n if os.environ.get("X"):\n  def inner(): return r.raw_summary()\n return inner',
                   "raw_summary", scope="f.inner", watched="-")  # R51-23c RED for inherited nested gate


class ConsumerSweepTests(unittest.TestCase):
    def test_all_supported_ungated_reads_have_checked_reasons(self):
        self.assertEqual(allowlist_violations(tracked_sources()), [])

    def test_salvage_non_claim_rows(self):
        """R72-1..3: discarded power and absent measurands never enter a license."""
        import csv
        import json
        import shutil
        import tempfile
        from joulewise import salvage_dangler
        from joulewise.salvage_dangler import SalvageAuthorizationError, inspect_preworkload_abort
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as temp:
            fixture = ROOT / "tests/fixtures/salvage_dangler/r5a_idle_abort"
            original = Path(temp) / "original"
            changed = Path(temp) / "changed"
            shutil.copytree(fixture, original)
            for telemetry_name, rows in (
                ("rich_telemetry_idle.jsonl", [
                    {"index": 1, "processor_combined_power_w": 0.19, "timestamp_s": 99.81},
                    {"index": 2, "processor_combined_power_w": 0.21, "timestamp_s": 99.91},
                ]),
                ("rich_telemetry_idle_attempt_2.jsonl", [
                    {"index": 1, "processor_combined_power_w": 0.22, "timestamp_s": 99.92},
                    {"index": 2, "processor_combined_power_w": 0.24, "timestamp_s": 100.05},
                ]),
            ):
                (original / telemetry_name).write_text(
                    "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
            shutil.copytree(original, changed)
            trace = changed / "power_trace.csv"
            with trace.open(newline="", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                fields, rows = reader.fieldnames, list(reader)
            for row in rows:
                row["power_w"] = str(float(row["power_w"]) * 1000 + 7)
            with trace.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)
            base_license = inspect_preworkload_abort(original)
            self.assertEqual(base_license, inspect_preworkload_abort(changed))  # R72-1 GREEN
            # R72-1 RED: a computed power escaping in the license changes it.
            def power_leaking_license(path):
                license = inspect_preworkload_abort(path)
                with (path / "power_trace.csv").open(newline="", encoding="utf-8") as handle:
                    license["mean_power_w"] = sum(float(row["power_w"]) for row in csv.DictReader(handle)) / 2
                return license
            with self.assertRaises(AssertionError):
                self.assertEqual(power_leaking_license(original), power_leaking_license(changed))

            summary_path = changed / "summary_metrics.json"
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            summary["gross_energy_j"] = 12.5
            summary_path.write_text(json.dumps(summary), encoding="utf-8")
            with self.assertRaisesRegex(SalvageAuthorizationError, "measurand bytes"):
                inspect_preworkload_abort(changed)  # R72-2 GREEN
            # R72-2 RED under removal of the named test: the exact refusal
            # contract fails. The separate unknown-field check still refuses.
            with patch.object(salvage_dangler, "_MEASURAND_FIELDS", ()):
                with self.assertRaises(AssertionError):
                    with self.assertRaisesRegex(SalvageAuthorizationError, "measurand bytes"):
                        inspect_preworkload_abort(changed)

        salvage_rows = [key for key, row in ALLOWLIST.items()
                        if key[0] == "joulewise/salvage_dangler.py" and "tested and dropped" in row[1]]
        self.assertEqual(len(salvage_rows), 2)
        for key in salvage_rows:
            bad = dict(ALLOWLIST)
            bad[key] = ("non_claim", "clause (i), fields that leave: time; tested and dropped: power_w")
            self.assertIn(str(key), " ".join(allowlist_violations(tracked_sources(), bad)))  # R72-3 RED

    def test_allowlist_membership_counterfactuals(self):
        files = tracked_sources()
        self.assertEqual({key for key, row in ALLOWLIST.items() if row[0] == "gate_body"}, {
            ("joulewise/battery_float.py", "authenticate_bundle", "direct:_required_object", "metadata.json"),
            ("joulewise/bundle_read.py", "BundleReader.metadata", "direct:_strict_json", "metadata.json"),
            ("joulewise/bundle_read.py", "authenticate_window_members", "direct:_strict_json", "metadata.json"),
        })  # R57-1 GREEN
        extra_gate = dict(ALLOWLIST)
        extra_gate[("joulewise/bundle_read.py", "BundleReader.problems",
                    "direct:read_authentication_text", "metadata.json")] = (
                        "gate_body", "counterfactual fourth gate")
        self.assertIn("gate_body keys differ", " ".join(
            allowlist_violations(files, extra_gate)))  # R57-1 RED
        actual = site_keys(run(ROOT)[0])
        historical = ("scripts/issue_dg071_dg075_statistics.py", "main",
                      "direct:issue_artifacts", "power_trace.csv")
        self.assertIn(historical, actual)
        self.assertIn(historical, ALLOWLIST)
        removed = set(ALLOWLIST) - {historical}
        self.assertEqual(actual - removed, (actual - set(ALLOWLIST)) | {historical})  # R51-15
        added = set(ALLOWLIST) | {("joulewise/zz_new.py", "f", "raw_summary", "-")}
        self.assertIn(("joulewise/zz_new.py", "f", "raw_summary", "-"), added - actual)  # R51-14
        self.assertEqual([key for key, row in ALLOWLIST.items() if row[0] == "historical"],
                         [historical])  # R60-5
        self.assertFalse([key for key in ALLOWLIST if key[0] == "joulewise/envelope_gate.py"
                          and key[2] == "raw_summary"])  # R60-6
        self.assertFalse([key for key, row in ALLOWLIST.items() if row[0] != "behind_gate"
                          and any(word in row[1].lower() for word in
                                  ("metadata first", "follows bundlereader.metadata"))])  # R58-5
        idle_key = ("joulewise/idle_dependence.py", "derive_idle_mean_uncertainty",
                    "raw_artifact_bytes", "-")
        invalid_idle = dict(ALLOWLIST)
        invalid_idle[idle_key] = ("strict_validation", "counterfactual validator class")
        self.assertIn("R58-5 energy-return class invalid", " ".join(
            allowlist_violations(files, invalid_idle)))  # R58-5 RED

    def test_inventory_count_and_scope_boundary(self):
        rows, _ = run(ROOT)
        self.assertEqual((len(rows), len(site_keys(rows)), len({(p, q) for p, q, *_ in rows}),
                          len({(p, line) for p, _, _, _, line in rows})),
                         (125, 119, 88, 125))
        self.assertFalse([row for row in rows if row[2].startswith("ref:")])
        self.assertFalse([row for row in rows if row[1] == "<module>" or row[1].endswith(".<body>")])
        source = 'P = "power_trace.csv"\ndef f(b):\n p = b / P\n return p'
        self.assertFalse(site_keys(sweep_source("scripts/zz_new.py", source)))

    def test_swept_roots_are_closed(self):
        names = all_tracked_python()
        self.assertEqual(swept_file_violations(names), [])
        self.assertIn("tools/zz_new.py", " ".join(
            swept_file_violations(names + ["tools/zz_new.py"])))  # R61-1 RED
        files = tracked_sources()
        source = ('import json\n'
                  'def fig(b): return json.loads((b / "summary_metrics.json").read_text())["gross_energy_j"]\n')
        path = "docs/paper/figures/zz_new.py"
        self.assertIn((path, "fig", "direct:read_text", "summary_metrics.json"),
                      site_keys(sweep_source(path, source)))
        self.assertIn(path, " ".join(allowlist_violations(
            dict(files, **{path: source}))))  # R61-2 RED

    def test_closed_gate_and_reader_definitions(self):
        files = tracked_sources()
        self.assertEqual(gate_body_violations(files), [])
        self.assertEqual(tolerant_definition_violations(files), [])
        self.assertEqual(reader_method_violations(files), [])
        self.assertEqual(journal_energy_readers(files), JOURNAL_ENERGY_READERS)
        base = files["joulewise/bundle_read.py"]
        mutants = {
            "cache_before_verdict": ('            verdict = self._battery_verdict(raw)',
                                     '            self._cache["metadata"] = raw\n            verdict = self._battery_verdict(raw)'),
            "other_cache_writer": ('    def raw_metadata(self) -> dict[str, Any] | None:',
                                   '    def prime(self, value):\n        self._cache["metadata"] = value\n\n    def raw_metadata(self) -> dict[str, Any] | None:'),
            "unknown_public_method": ('    def raw_metadata(self) -> dict[str, Any] | None:',
                                      '    def raw_trace(self):\n        return self._tolerant_json("summary_metrics.json")\n\n    def raw_metadata(self) -> dict[str, Any] | None:'),
            "tolerant_store": ('        return self._tolerant_json("summary_metrics.json")',
                               '        value = self._tolerant_json("summary_metrics.json")\n        self.last_energy = value\n        return value'),
        }
        for label, (before, after) in mutants.items():
            with self.subTest(label=label):
                self.assertIn(before, base)
                changed = dict(files, **{"joulewise/bundle_read.py": base.replace(before, after, 1)})
                self.assertTrue(gate_body_violations(changed) or
                                reader_method_violations(changed) or
                                tolerant_definition_violations(changed))
        before = '            verdict = self._battery_verdict(raw)'
        self.assertIn(before, base)
        changed = dict(files, **{"joulewise/bundle_read.py": base.replace(
            before, '            self._cache["metadata"] = raw\n' + before, 1)})
        self.assertTrue(gate_body_violations(changed))  # R57-2 RED
        trace_gate = '        """Raw ``power_trace.csv`` rows (a missing file is an empty list)."""\n        self.metadata()\n'
        self.assertIn(trace_gate, base)
        changed = dict(files, **{"joulewise/bundle_read.py": base.replace(
            trace_gate, trace_gate.replace('        self.metadata()\n', ''), 1)})
        self.assertIn("trace_rows", " ".join(reader_method_violations(changed)))  # R58-2
        from unittest.mock import patch
        with patch.dict(READER_METHODS, {"events": "other"}):
            self.assertIn("journal", " ".join(reader_method_violations(files)))  # R58-9
        self.assertNotIn("joulewise/reduce.py::_reduce", journal_energy_readers(files))  # R58-6b
        added = dict(files, **{"joulewise/aggregate.py": files["joulewise/aggregate.py"] +
                      '\ndef journal_reader(p):\n    return [e["metadata"]["power_w_mean"] for e in BundleReader(p).events()]\n'})
        self.assertIn("joulewise/aggregate.py::journal_reader", journal_energy_readers(added))  # R58-6

    def test_gate_binding_and_cache_mutants(self):
        files = tracked_sources()
        fake = dict(files, **{"joulewise/zz_new.py":
                    'def authenticate_window_members(m):\n    return (m / "summary_metrics.json").read_text()\n'})
        self.assertIn("gate name definition", " ".join(gate_binding_violations(fake)))  # R57-7
        fake = dict(files, **{"joulewise/zz_new.py":
                    'from joulewise.bundle_read import BundleReader\n'
                    'def f(r):\n    r._cache.update(metadata=r.raw_metadata())\n'})
        self.assertIn("external _cache", " ".join(cache_violations(fake)))  # R57-6b C1
        base = files["joulewise/bundle_read.py"]
        for label, addition in (
            ("C3", '    def prime(self, value):\n        self._cache |= {"metadata": value}\n'),
            ("C4", '    def prime(self, value):\n        setattr(self, "_cache", {"metadata": value})\n'),
            ("C6", '    def prime(self, name, value):\n        self._cache[name] = value\n'),
            ("C8", '    def prime(self, value):\n        slots = self._cache\n        slots["metadata"] = value\n'),
            ("C9", '    def prime(self, name, value):\n        key = f"{name}"\n        self._cache[key] = value\n'),
        ):
            with self.subTest(label=label):
                changed = dict(files, **{"joulewise/bundle_read.py": base.replace(
                    '    def raw_metadata(self) -> dict[str, Any] | None:',
                    addition + '\n    def raw_metadata(self) -> dict[str, Any] | None:', 1)})
                self.assertTrue(cache_violations(changed))
        allowed = dict(files, **{"joulewise/bundle_read.py": base.replace(
            '    def raw_metadata(self) -> dict[str, Any] | None:',
            '    def prime(self):\n        self._cache["extra"] = 1\n\n'
            '    def raw_metadata(self) -> dict[str, Any] | None:', 1)})
        self.assertEqual(cache_violations(allowed), [])  # R57-6b C10

    def test_gate_content_and_verdict_caller_mutants(self):
        files = tracked_sources()
        base = files["joulewise/bundle_read.py"]
        before = '            verdict = self._battery_verdict(raw)\n            if verdict.status not in'
        after = ('            try:\n                verdict = self._battery_verdict(raw)\n'
                 '            except BundleReadError:\n                return raw\n'
                 '            if verdict.status not in')
        self.assertIn(before, base)
        changed = base.replace(before, after, 1)
        self.assertIn("content leaves before verdict", " ".join(content_violations(
            "joulewise/bundle_read.py", changed, "BundleReader.metadata")))  # R57-3
        before = '            metadata = reader._strict_json("metadata.json")\n            if not isinstance(metadata, dict):'
        after = ('            metadata = reader._strict_json("metadata.json")\n'
                 '            verdicts[label + ":metadata"] = metadata\n'
                 '            if not isinstance(metadata, dict):')
        self.assertIn(before, base)
        changed = base.replace(before, after, 1)
        self.assertIn("content leaves before verdict", " ".join(content_violations(
            "joulewise/bundle_read.py", changed, "authenticate_window_members")))  # R57-4
        aggregate = files["joulewise/aggregate.py"]
        before = '    authenticate_window_members(((member, runs_root / member),))'
        self.assertIn(before, aggregate)
        changed = dict(files, **{"joulewise/aggregate.py": aggregate.replace(
            before, '    battery_float.authenticate_bundle(runs_root / member)', 1)})
        self.assertIn(("joulewise/aggregate.py", "_read_member"), {
            (p, q) for p, q, _, _ in call_sites(changed, "authenticate_bundle")
        })  # R57-5
        self.assertIn("joulewise/aggregate.py::_read_member",
                      " ".join(gate_body_violations(changed)))  # R57-5 RED

    def test_reference_sites_and_gate_bindings(self):
        for source in (
            'def f(b):\n    get = BundleReader(b).raw_summary\n    return get()["gross_energy_j"]',
            'def f(b):\n    return getattr(BundleReader(b), "raw_summary")()',
            'def f(readers):\n    return list(map(BundleReader.raw_summary, readers))',
            'def f(b):\n    r = BundleReader(b)\n    r.metadata()\n    get = r.raw_summary\n    return get()',
        ):
            with self.subTest(source=source):
                self.assertIn(("joulewise/zz_new.py", "f", "ref:raw_summary", "-"),
                              site_keys(sweep_source("joulewise/zz_new.py", source)))  # R57-10
        base_import = 'from joulewise.bundle_read import authenticate_window_members, BundleReader\n'
        failures = (
            'authenticate_window_members = lambda members: {}\n',
            'def authenticate_window_members(members): return {}\n',
            'class BundleReader:\n    def metadata(self): return {}\n',
            'class Quick(BundleReader):\n    def metadata(self): return {}\n',
            'BundleReader.metadata = lambda self: {}\n',
            'from other_module import authenticate_window_members\n',
        )
        for source in failures:
            with self.subTest(binding=source):
                files = tracked_sources(replacements={"joulewise/zz_new.py": base_import + source})
                self.assertTrue(gate_binding_violations(files))  # R57-11
        files = tracked_sources(replacements={"joulewise/zz_new.py": base_import +
                                'def f(members): return authenticate_window_members(members)\n'})
        self.assertEqual(gate_binding_violations(files), [])  # R57-11 R9

    def test_subclass_hole_is_pinned(self):
        import inspect
        import tempfile
        import textwrap
        from unittest.mock import patch
        from joulewise import bundle_read
        from joulewise.bundle_read import BundleReader, BatteryStatusRefusal
        from tests.test_bfgs_window_consumers import WindowMembersTests

        class Quick(BundleReader):
            def metadata(self):
                return self.raw_metadata()

        fixture = WindowMembersTests()
        with tempfile.TemporaryDirectory() as tmp:
            bundle = fixture.pair_bundle(Path(tmp), "charging", charging=True)
            (bundle / "power_trace.csv").write_text(
                "timestamp_s,power_w,source,rail,interval_start_s,interval_end_s\n"
                "1,2,cpu,cpu,0,1\n")
            self.assertEqual(Quick(bundle).trace_rows()[0]["power_w"], "2")  # R57-12
            source = textwrap.dedent(inspect.getsource(BundleReader.trace_rows))
            before = '    self.metadata()\n'
            self.assertIn(before, source)
            namespace = {}
            exec(compile(source.replace(before, '    BundleReader.metadata(self)\n', 1),
                         '<R57-12-counterfactual>', 'exec'), vars(bundle_read), namespace)
            with patch.object(BundleReader, "trace_rows", namespace["trace_rows"]):
                with self.assertRaises(BatteryStatusRefusal):
                    Quick(bundle).trace_rows()  # R57-12 RED

    def test_gate_status_counterfactual(self):
        import inspect
        import tempfile
        import textwrap
        from unittest.mock import patch
        from joulewise import bundle_read
        from tests.test_bfgs_window_consumers import WindowMembersTests

        source = textwrap.dedent(inspect.getsource(bundle_read.BundleReader.metadata))
        before = 'if verdict.status not in {"pass", "unobserved_historical", "not_applicable"}:'
        self.assertIn(before, source)
        ns = {}
        exec(compile(source.replace(before, 'if False:', 1), '<R57-12-counterfactual>', 'exec'),
             vars(bundle_read), ns)
        fixture = WindowMembersTests()
        with tempfile.TemporaryDirectory() as tmp:
            charging = fixture.pair_bundle(Path(tmp), "charging", charging=True)
            with self.assertRaises(bundle_read.BatteryStatusRefusal):
                bundle_read.BundleReader(charging).metadata()
            with patch.object(bundle_read.BundleReader, "metadata", ns["metadata"]):
                self.assertIsInstance(bundle_read.BundleReader(charging).metadata(), dict)  # RED

    def test_base_cli_reference_is_reported(self):
        source = subprocess.check_output(["git", "show", "1417c0c4:joulewise/cli.py"],
                                         cwd=ROOT, text=True)
        self.assertIn(("joulewise/cli.py", "_strict_problems", "raw_metadata", "-", 423),
                      sweep_source("joulewise/cli.py", source))  # R51-13

    def test_caller_references_and_campaign_consumers(self):
        files = tracked_sources()
        idle = ALLOWLIST[("joulewise/idle_dependence.py", "derive_idle_mean_uncertainty",
                          "raw_artifact_bytes", "-")][2]["callers"]
        self.assertEqual(callers_violations(files, "derive_idle_mean_uncertainty", idle, ALLOWLIST), [])
        self.assertTrue(callers_violations(files, "derive_idle_mean_uncertainty",
                                           tuple(key for key in idle if not key.endswith("::_reduce_v060")),
                                           ALLOWLIST))  # R59-3
        with_reference = dict(files, **{"joulewise/zz_new.py":
                              'from joulewise.idle_dependence import derive_idle_mean_uncertainty\n'
                              'def f():\n    return derive_idle_mean_uncertainty\n'})
        self.assertIn("joulewise/zz_new.py::f", " ".join(callers_violations(
            with_reference, "derive_idle_mean_uncertainty", idle, ALLOWLIST)))  # R59-3b
        with_call = dict(files, **{"joulewise/zz_new.py":
                          'from joulewise.idle_dependence import derive_idle_mean_uncertainty\n'
                          'def f(reader):\n    return derive_idle_mean_uncertainty(reader)\n'})
        self.assertIn("joulewise/zz_new.py::f", " ".join(callers_violations(
            with_call, "derive_idle_mean_uncertainty", idle, ALLOWLIST)))  # R51-16
        fig = files["scripts/make_figures.py"]
        tree = ast.parse(fig)
        main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
        lines = fig.splitlines(keepends=True)
        lines.insert(main.body[0].lineno - 1, '    rows = extract_rows(runs_root, manifests, tree)\n')
        with_direct = dict(files, **{"scripts/make_figures.py": "".join(lines)})
        self.assertIn("scripts/make_figures.py::main", " ".join(callers_violations(
            with_direct, "extract_rows", (), ALLOWLIST)))  # R60-2 RED
        lines = fig.splitlines(keepends=True)
        lines.insert(main.body[0].lineno - 1, '    rows = list(map(extract_rows, [runs_root]))\n')
        with_map = dict(files, **{"scripts/make_figures.py": "".join(lines)})
        self.assertIn("scripts/make_figures.py::main", " ".join(callers_violations(
            with_map, "extract_rows", (), ALLOWLIST)))  # R60-2b
        consumers = ALLOWLIST[("scripts/run_campaign.py", "evaluate_member",
                               "direct:read_text", "metadata.json")][2]["consumers"]
        self.assertEqual(consumers_violations(files, consumers), [])
        src = files["scripts/run_campaign.py"]
        for label, before, after in (
            ("campaign_gate_removed", '        battery_verdicts = authenticate_window_members(battery_members)',
             '        battery_verdicts = {}'),
            ("axi_gate_removed", '            authenticate_window_members(\n                (label, path) for path, label in sorted(gate_paths.items())\n            )',
             '            pass'),
            ("policy_parameter_rebound", '        finalized_bundles = _axi_discover_finalized_bundles(runs_dir, manifest)',
             '        policy_binding = policy_binding or _default_binding()\n        finalized_bundles = _axi_discover_finalized_bundles(runs_dir, manifest)'),
            ("nested_policy_parameter_rebound", '        finalized_bundles = _axi_discover_finalized_bundles(runs_dir, manifest)',
             '        def _reset_policy_binding():\n            nonlocal policy_binding\n            policy_binding = None\n        _reset_policy_binding()\n        finalized_bundles = _axi_discover_finalized_bundles(runs_dir, manifest)'),
            ("policy_test_widened", '        if policy_binding is not None:\n            gate_paths =',
             '        if policy_binding is not None and receipts:\n            gate_paths ='),
            ("gate_in_else", '        if policy_binding is not None:\n            gate_paths =',
             '        if policy_binding is None:\n            pass\n        else:\n            gate_paths ='),
        ):
            with self.subTest(label=label):
                self.assertIn(before, src)
                changed = dict(files, **{"scripts/run_campaign.py": src.replace(before, after, 1)})
                self.assertTrue(consumers_violations(changed, consumers))  # R51-17, R51-28

    def test_campaign_consumers_form_is_closed(self):
        files = tracked_sources()
        key = ("scripts/run_campaign.py", "evaluate_member", "direct:read_text", "metadata.json")
        self.assertEqual(consumers_form_violations(
            files, key, CAMPAIGN_CONSUMERS_EVIDENCE, CAMPAIGN_CONSUMERS_REASON), [])  # R51-17d GREEN
        for source, expected in (
            ('def f(p, i): return evaluate_member(p, info=i, waivers={}).summary\n',
             'scripts/zz_new.py::f'),
            ('def g(): h = evaluate_members; return h\n', 'scripts/zz_new.py::g'),
        ):
            changed = dict(files, **{"scripts/zz_new.py": source})
            self.assertIn(expected, " ".join(consumers_form_violations(
                changed, key, CAMPAIGN_CONSUMERS_EVIDENCE,
                CAMPAIGN_CONSUMERS_REASON)))  # R51-17b/c RED
        incomplete = dict(CAMPAIGN_CONSUMERS_EVIDENCE, producers=("evaluate_member",))
        self.assertIn("scripts/run_campaign.py::evaluate_members", " ".join(consumers_form_violations(
            files, key, incomplete, CAMPAIGN_CONSUMERS_REASON)))  # R51-17d RED
        no_collection = dict(CAMPAIGN_CONSUMERS_EVIDENCE)
        del no_collection["collection_uses"]
        self.assertIn("fields missing", " ".join(consumers_form_violations(
            files, key, no_collection, CAMPAIGN_CONSUMERS_REASON)))  # R51-17e RED
        old_reason = "consumers form: evaluate_member returns or passes bundle content only to the listed gated chain"
        self.assertIn("reason differs", " ".join(consumers_form_violations(
            files, key, CAMPAIGN_CONSUMERS_EVIDENCE, old_reason)))  # R76-1 RED
        self.assertNotIn("only to", CAMPAIGN_CONSUMERS_REASON)
        self.assertNotIn("reach only", CAMPAIGN_CONSUMERS_REASON)

    def test_raw_capture_screen_mutants(self):
        files = tracked_sources()
        self.assertEqual(len(capture_readers(files)), 48)
        self.assertEqual(capture_readers(files), set(RAW_CAPTURE_READERS))
        extra = 'def new_reader(p):\n    return (p / "raw" / "powermetrics.plist").read_bytes()\n'
        changed = dict(files, **{"joulewise/aggregate.py": files["joulewise/aggregate.py"] + extra})
        self.assertIn("joulewise/aggregate.py::new_reader", capture_readers(changed))  # R58-7
        self.assertIn("joulewise/aggregate.py::new_reader", " ".join(
            capture_violations(changed)))  # R58-7 RED
        extra_name = ('from joulewise.reduce import RAW_POWERMETRICS_NAME\n'
                      'def named_reader(p):\n    return (p / "raw" / RAW_POWERMETRICS_NAME).read_bytes()\n')
        changed = dict(files, **{"joulewise/aggregate.py": files["joulewise/aggregate.py"] + extra_name})
        self.assertIn("joulewise/aggregate.py::named_reader", capture_readers(changed))  # R58-8
        self.assertIn("joulewise/aggregate.py::named_reader", " ".join(
            capture_violations(changed)))  # R58-8 RED

    def test_raw_capture_validation_shape(self):
        files = tracked_sources()
        members = {key for key, (kind, _) in RAW_CAPTURE_READERS.items()
                   if kind == "validation"}
        self.assertEqual(members, {
            "joulewise/cli.py::_verify_powermetrics_raw_to_trace",
            "joulewise/cli.py::_strict_rich_telemetry_problems",
            "joulewise/cli.py::_strict_uncertainty_evidence_problems",
            "joulewise/environment_admission.py::_window_thermal_pressure_refusals",
        })
        for key in members:
            path, qualname = key.split("::", 1)
            fn = dict(qualified(ast.parse(files[path])))[qualname]
            self.assertIn(ast.unparse(fn.returns), {"list[str]", "tuple[str, ...]", "set[str]", "bool"})
        path = "joulewise/cli.py"
        before = "def _verify_powermetrics_raw_to_trace("  # R73-1 counterfactual
        self.assertIn(before, files[path])
        import re as _re
        mutant = _re.sub(r"(def _verify_powermetrics_raw_to_trace\([\s\S]*?\)) -> list\[str\]:",
                         r"\1 -> list[float]:", files[path], count=1)
        self.assertNotEqual(mutant, files[path])
        self.assertIn("_verify_powermetrics_raw_to_trace: validation shape missing",
                      " ".join(capture_violations(dict(files, **{path: mutant}))))  # RED

    def test_capture_gate_forms(self):
        files = tracked_sources()
        controller = "joulewise/controller.py"
        attachment = "joulewise/controller.py::_load_instrument_calibration_attachment"
        self.assertEqual(capture_in_function_violations(files, attachment), [])  # R74-1 GREEN
        source = files[controller]
        before = ('    verdict = battery_float.authenticate_capture(root)\n'
                  '    if verdict.status != "pass":\n'
                  '        raise ValueError(f"instrument calibration {verdict.status}: {\'; \'.join(verdict.reasons)}")\n')
        self.assertIn(before, source)
        removed = dict(files, **{controller: source.replace(before, "", 1)})
        self.assertIn(attachment, " ".join(capture_in_function_violations(removed, attachment)))
        wrong = dict(files, **{controller: source.replace('if verdict.status != "pass":',
                                                        'if verdict.status == "confounded":', 1)})
        self.assertIn(attachment, " ".join(capture_in_function_violations(wrong, attachment)))  # R74-1 RED
        early = dict(files, **{controller: source.replace(
            '    verdict = battery_float.authenticate_capture(root)',
            '    capture_name = RAW_POWERMETRICS_NAME\n'
            '    verdict = battery_float.authenticate_capture(root)', 1)})
        self.assertIn("capture named before refusal", " ".join(
            capture_in_function_violations(early, attachment)))  # R74-1 RED

        calibration = "joulewise/calibration_bracketing.py"
        candidate = "joulewise/calibration_bracketing.py::_load_calibration_candidate_unbounded"
        chain = RAW_CAPTURE_READERS[candidate][1][1]
        self.assertEqual(capture_chain_violations(files, candidate, chain), [])  # R74-2 GREEN
        before = ('        if _battery_exclusion_for_observation(observation) is not None:\n'
                  '            continue\n')
        self.assertIn(before, files[calibration])
        removed = dict(files, **{calibration: files[calibration].replace(before, "", 1)})
        self.assertIn("discover_calibration_candidates", " ".join(
            capture_chain_violations(removed, candidate, chain)))  # R74-2 RED
        extra = dict(files, **{"joulewise/zz_new.py":
                     'def f(d, r): return load_calibration_candidate(d, runs_root=r)\n'})
        self.assertIn("joulewise/zz_new.py::f", " ".join(
            capture_chain_violations(extra, candidate, chain)))  # R74-2 RED

        verifier = "joulewise/reduce.py::_verify_instrument_calibration"
        callers = RAW_CAPTURE_READERS[verifier][1]
        self.assertEqual(raw_capture_callers_violations(files, verifier, callers), [])  # R74-3 GREEN
        window = "joulewise/whole_window.py"
        gate = ('        battery_verdicts = authenticate_window_members(\n'
                '            (bundle_id, path) for bundle_id, path in sorted(bundle_paths.items())\n'
                '        )\n')
        self.assertIn(gate, files[window])
        removed = dict(files, **{window: files[window].replace(gate, '        battery_verdicts = {}\n', 1)})
        self.assertIn("AuthenticatedConsumptionSession._prepare", " ".join(
            raw_capture_callers_violations(removed, verifier, callers)))  # R74-3 RED
        annotation = 'def _current_core_rederivation_reasons('
        self.assertIn(annotation, files[window])
        import re as _re
        changed = _re.sub(r'(def _current_core_rederivation_reasons\([\s\S]*?\)) -> set\[str\]:',
                          r'\1 -> dict[str, float]:', files[window], count=1)
        self.assertNotEqual(changed, files[window])
        mutant = dict(files, **{window: changed})
        self.assertIn("_current_core_rederivation_reasons", " ".join(
            raw_capture_callers_violations(mutant, verifier, callers)))  # R74-3 RED

    def test_raw_capture_lane_is_closed(self):
        files = tracked_sources()
        self.assertEqual({key for key, (kind, gate) in RAW_CAPTURE_READERS.items()
                          if kind == "energy" and gate == ("lane", "BFGS-RAWCAPTURE-01")},
                         RAW_CAPTURE_LANE_MEMBERS)
        extra = dict(RAW_CAPTURE_READERS,
                     **{"joulewise/aggregate.py::zz_new": ("energy", ("lane", "BFGS-RAWCAPTURE-01"))})
        self.assertIn("joulewise/aggregate.py::zz_new", " ".join(
            capture_violations(files, extra)))  # R75-1 RED

    def test_raw_capture_lane_files_match_main(self):
        if subprocess.run(["git", "cat-file", "-e", "97082508^{commit}"], cwd=ROOT,
                          capture_output=True).returncode:
            self.skipTest("R75-2: commit 97082508 absent")
        lane_files = sorted({key.split("::", 1)[0] for key in RAW_CAPTURE_LANE_MEMBERS})
        for path in lane_files:
            with self.subTest(path=path):
                self.assertEqual(subprocess.run(
                    ["git", "diff", "--quiet", "97082508", "--", path], cwd=ROOT).returncode,
                    0, path)  # R75-2 GREEN; any changed file is RED
        path = lane_files[0]
        baseline = subprocess.check_output(["git", "show", f"97082508:{path}"], cwd=ROOT)
        self.assertEqual((ROOT / path).read_bytes(), baseline)
        mutated = (ROOT / path).read_bytes() + b"\n# counterfactual change\n"
        self.assertNotEqual(mutated, baseline)  # R75-2 RED without writing a production file

    def test_raw_capture_inventory(self):
        files = tracked_sources()
        self.assertEqual(capture_violations(files), [])

    def test_envelope_summary_is_gated_in_own_scope(self):
        source = (ROOT / "joulewise/envelope_gate.py").read_text()
        rows = site_keys(sweep_source("joulewise/envelope_gate.py", source))
        self.assertFalse([key for key in rows if key[1] == "_gated_summary"])
        self.assertIn('    reader.metadata()\n    return reader.raw_summary()', source)
        without = source.replace('    reader.metadata()\n    return reader.raw_summary()',
                                 '    return reader.raw_summary()', 1)
        rows = site_keys(sweep_source("joulewise/envelope_gate.py", without))
        self.assertIn(("joulewise/envelope_gate.py", "_gated_summary", "raw_summary", "-"), rows)

    def test_envelope_refusal_custody_and_output_identity(self):
        import dataclasses
        import inspect
        import sys
        import textwrap
        import types
        from unittest.mock import patch
        from joulewise import battery_float, envelope_gate
        from joulewise.bundle_read import BundleReader, BatteryStatusRefusal
        from tests.test_envelope_gate import EnvelopeGateTests

        fixture = EnvelopeGateTests("test_all_pass_verdict")
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        bundle = fixture.make_bundle()
        ordinary = envelope_gate.analyze_envelope_gate([bundle], lambda _: [])
        if subprocess.run(["git", "cat-file", "-e", "315364b2^{commit}"], cwd=ROOT,
                          capture_output=True).returncode:
            self.skipTest("R60-7: commit 315364b2 absent")
        old_source = subprocess.check_output(
            ["git", "show", "315364b2:joulewise/envelope_gate.py"],
            cwd=ROOT, text=True)
        name = "joulewise._envelope_gate_before_bfgs63"
        old = types.ModuleType(name)
        old.__package__ = "joulewise"
        with patch.dict(sys.modules, {name: old}):
            exec(compile(old_source, name, "exec"), old.__dict__)
            self.assertEqual(ordinary, old.analyze_envelope_gate([bundle], lambda _: []))  # R60-7

        original_verdict = BundleReader._battery_verdict
        def confounded(reader, raw):
            return dataclasses.replace(original_verdict(reader, raw),
                                       status="battery_float_confounded", reasons=("stub",))
        with patch.object(BundleReader, "_battery_verdict", confounded):
            refused = envelope_gate.analyze_envelope_gate([bundle], lambda _: [])
            self.assertEqual(refused["verdict"], "bundle_refused")
            self.assertNotIn("calibration_evidence_only", refused)
            original_manifest = envelope_gate._manifest_record
            def without_manifest_gate(reader):
                class ReaderShim:
                    def __init__(self, underlying): self.underlying = underlying
                    def __getattr__(self, name): return getattr(self.underlying, name)
                    def metadata(self): return self.underlying.raw_metadata() or {}
                return original_manifest(ReaderShim(reader))
            with patch.object(envelope_gate, "_manifest_record", without_manifest_gate), \
                 patch.object(envelope_gate, "_gated_summary", lambda reader: reader.raw_summary()):
                leaked = envelope_gate.analyze_envelope_gate([bundle], lambda _: [])
                records = leaked.get("calibration_evidence_only", {}).get("level_window_gross_energies_j")
                self.assertEqual(len(records), 5)  # R60-3 RED counterfactual
            with patch.object(envelope_gate, "_manifest_record", without_manifest_gate):
                with self.assertRaises(BatteryStatusRefusal):
                    envelope_gate.analyze_envelope_gate([bundle], lambda _: [])
        with patch.object(BundleReader, "_battery_verdict",
                          side_effect=battery_float.CustodyUnreadable("stub")):
            with self.assertRaises(battery_float.CustodyFailure):
                envelope_gate.analyze_envelope_gate([bundle], lambda _: [])  # R60-4
            source = textwrap.dedent(inspect.getsource(envelope_gate.analyze_envelope_gate))
            before = '    except BundleReadError as exc:'
            self.assertIn(before, source)
            namespace = {}
            exec(compile(source.replace(before, '    except Exception as exc:', 1),
                         '<R60-4-counterfactual>', 'exec'), vars(envelope_gate), namespace)
            widened = namespace['analyze_envelope_gate']([bundle], lambda _: [])
            self.assertEqual(widened['verdict'], 'bundle_refused')  # R60-4 RED

    def test_reader_gates_and_tolerant_behaviour(self):
        import inspect
        import json
        import tempfile
        import textwrap
        from unittest.mock import patch
        from joulewise import battery_float, bundle_read
        from joulewise.bundle_read import (BundleReader, BatteryStatusRefusal,
                                           WindowBatteryRefusal, authenticate_window_members)
        from tests.test_bfgs_window_consumers import WindowMembersTests

        fixture = WindowMembersTests()
        with tempfile.TemporaryDirectory() as tmp:
            bundle = fixture.pair_bundle(Path(tmp), "charging", charging=True)
            self.assertEqual(battery_float.authenticate_bundle(bundle).status,
                             "battery_float_confounded")
            with self.assertRaises(BatteryStatusRefusal) as refused:
                BundleReader(bundle).metadata()
            self.assertEqual(refused.exception.status, "battery_float_confounded")
            with self.assertRaises(WindowBatteryRefusal) as window:
                authenticate_window_members((("m", bundle),))
            self.assertEqual(window.exception.members[0]["label"], "m")  # R57-8
            for method, args in (("trace_rows", ()), ("summed_curve", ()),
                                 ("source_curve", ("cpu",)), ("measured_window", ())):
                with self.subTest(gated=method), self.assertRaises(BatteryStatusRefusal):
                    getattr(BundleReader(bundle), method)(*args)  # R58-3
            tolerant = BundleReader(bundle)
            for method, args in (("raw_metadata", ()), ("raw_config", ()),
                                 ("raw_summary", ()), ("raw_artifact_bytes", ("battery_float.pre.ioreg",))):
                with self.subTest(tolerant=method):
                    getattr(tolerant, method)(*args)  # R58-4
            raw_source = textwrap.dedent(inspect.getsource(BundleReader.raw_summary))
            raw_namespace = {}
            exec(compile(raw_source.replace(
                '    return self._tolerant_json("summary_metrics.json")',
                '    self.metadata()\n    return self._tolerant_json("summary_metrics.json")', 1),
                '<R58-4-counterfactual>', 'exec'), vars(bundle_read), raw_namespace)
            with patch.object(BundleReader, "raw_summary", raw_namespace["raw_summary"]):
                with self.assertRaises(BatteryStatusRefusal):
                    BundleReader(bundle).raw_summary()  # R58-4 RED
            with (bundle / "events.jsonl").open("a") as handle:
                for event_type, stamp in (("stage_started", 40), ("stage_completed", 50)):
                    handle.write(json.dumps({"timestamp_s": float(stamp),
                                             "event_type": event_type,
                                             "phase": "measured_run", "message": "",
                                             "metadata": {"monotonic_ns": stamp}}) + "\n")
            window_source = textwrap.dedent(inspect.getsource(BundleReader.measured_window))
            window_namespace = {}
            exec(compile(window_source.replace('    self.metadata()\n', '', 1),
                         '<R58-3-counterfactual>', 'exec'), vars(bundle_read),
                 window_namespace)
            with patch.object(BundleReader, "measured_window", window_namespace["measured_window"]):
                self.assertEqual(BundleReader(bundle).measured_window(),
                                 bundle_read.Window(start_s=40.0, end_s=50.0))  # R58-3 RED
            (bundle / "raw" / "battery_float.post.ioreg").unlink()
            for index, call in enumerate((lambda: battery_float.authenticate_bundle(bundle),
                                          lambda: BundleReader(bundle).metadata(),
                                          lambda: authenticate_window_members((("m", bundle),)))):
                with self.assertRaises(battery_float.CustodyFailure) as custody:
                    call()  # R57-9
                if index == 2:
                    self.assertEqual(custody.exception.window_member, "m")
            original_authenticate_bundle = battery_float.authenticate_bundle
            def custody_as_status(path):
                try:
                    return original_authenticate_bundle(path)
                except battery_float.CustodyFailure:
                    return battery_float.authenticate_pair(
                        {}, path, phases=("bundle_pre", "bundle_post"),
                        identity=bundle.name, span=(30, 80))
            with patch.object(battery_float, "authenticate_bundle", custody_as_status):
                self.assertEqual(battery_float.authenticate_bundle(bundle).status,
                                 "battery_float_evidence_missing")
                with self.assertRaises(BatteryStatusRefusal) as converted:
                    BundleReader(bundle).metadata()
                self.assertEqual(converted.exception.status,
                                 "battery_float_evidence_missing")  # R57-9 RED


if __name__ == "__main__":
    unittest.main()
