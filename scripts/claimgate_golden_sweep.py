#!/usr/bin/env python3
"""Mechanical branch and mutation sweep for the v1 replay golden.

Only the seven whole-body decision functions receive branch coverage.
Issuance, artifact, analysis, side-bound, and manifest paths are pinned by
mutations and recorded outcomes.
"""

from __future__ import annotations

import argparse
import ast
from concurrent.futures import ThreadPoolExecutor
import copy
import dis
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.capture_claim_replay_golden import GOLDEN, canonical_bytes, capture

# Key: <module>:<qualname>:<line>:<direction>. Each proof is reviewed with the
# concrete branch offset shown in the sweep table.
UNREACHABLE_ARCS: dict[str, str] = {
    "claims:evaluate_claim:294:right": "JSON floor metadata raises only SingleCountDisciplineError at this reader seam; the nonmatching exception handler is unreachable.",
    "claims:evaluate_claim:337:left": "A missing numeric estimate adds metric_missing_or_nonfinite, forcing not_estimable before this assertion.",
    "claims:evaluate_claim:338:left": "A missing metrology interval adds metric_missing_or_nonfinite, forcing not_estimable before this assertion.",
    "claims:evaluate_claim:339:left": "A missing decision interval adds metric_missing_or_nonfinite, forcing not_estimable before this assertion.",
    "claims:evaluate_claim:385:right": "direction_supported requires a numeric estimate because missing estimates are not_estimable.",
    "epoch_equivalence_check:evaluate_session:501:right": "decimal.localcontext never suppresses an exception, so its __exit__ true branch is unreachable.",
}

# Key: <file>:<line>:<mutation>. Proven semantic equivalents only.
EQUIVALENT_MUTANTS: dict[str, str] = {
    "joulewise/analysis_engine/claims.py:386:Gt_to_GtE@34:0":
        "A zero estimate cannot reach direction_supported with a nonnegative floor; negative floors refuse earlier.",
}


def _coverage_functions():
    from joulewise.analysis_engine import _resolve_contrast_floor, claims, multiplicity
    from scripts import epoch_equivalence_check
    return {
        "claims:evaluate_claim": claims.evaluate_claim,
        "claims:_inside_equivalence": claims._inside_equivalence,
        "claims:_interval": claims._interval,
        "claims:_finite": claims._finite,
        "multiplicity:holm_adjust": multiplicity.holm_adjust,
        "analysis_engine:_resolve_contrast_floor": _resolve_contrast_floor,
        "epoch_equivalence_check:evaluate_session": epoch_equivalence_check.evaluate_session,
    }


def coverage_sweep() -> dict:
    if not hasattr(sys.monitoring.events, "BRANCH_LEFT"):
        raise RuntimeError("sys.monitoring branch events require Python 3.14")
    functions = _coverage_functions()
    events = sys.monitoring.events
    monitor = sys.monitoring
    tool_id = 5
    observed: set[tuple[object, int, str]] = set()
    def left(code, source, destination):
        observed.add((code, source, "left"))
    def right(code, source, destination):
        observed.add((code, source, "right"))
    monitor.use_tool_id(tool_id, "claimgate golden")
    try:
        monitor.register_callback(tool_id, events.BRANCH_LEFT, left)
        monitor.register_callback(tool_id, events.BRANCH_RIGHT, right)
        for function in functions.values():
            monitor.set_local_events(tool_id, function.__code__,
                                     events.BRANCH_LEFT | events.BRANCH_RIGHT)
        capture()
    finally:
        for function in functions.values():
            monitor.set_local_events(tool_id, function.__code__, 0)
        monitor.free_tool_id(tool_id)
    table = {}
    unlisted = []
    used_allowlist = set()
    for label, function in functions.items():
        code = function.__code__
        instructions = {item.offset: item for item in dis.get_instructions(code)}
        arcs = []
        for source, left_target, right_target in code.co_branches():
            instruction = instructions[source]
            line = instruction.positions.lineno or code.co_firstlineno
            for direction, target in (("left", left_target), ("right", right_target)):
                key = f"{label}:{line}:{direction}"
                covered = (code, source, direction) in observed
                allowlisted = not covered and key in UNREACHABLE_ARCS
                if allowlisted:
                    used_allowlist.add(key)
                if not covered and not allowlisted:
                    unlisted.append(f"{key}@{source}->{target}")
                arcs.append({"line": line, "offset": source, "direction": direction,
                             "target": target, "covered": covered, "allowlisted": allowlisted})
        table[label] = {"arcs": len(arcs), "covered": sum(a["covered"] for a in arcs),
                        "uncovered": sum(not a["covered"] for a in arcs),
                        "allowlisted": sum(a["allowlisted"] for a in arcs),
                        "details": arcs}
    return {"functions": table, "unlisted": sorted(unlisted),
            "unused_allowlist": sorted(set(UNREACHABLE_ARCS) - used_allowlist)}


_TARGETS = {
    "joulewise/analysis_engine/claims.py": None,
    "joulewise/analysis_engine/multiplicity.py": None,
    "joulewise/analysis_engine/__init__.py": {"_resolve_contrast_floor"},
    "joulewise/paper_custody.py": {"_claim_issuance_gate"},
    "joulewise/analysis_engine/artifact.py": {"validate_claim_verdicts"},
    "scripts/epoch_equivalence_check.py": {"evaluate_session"},
}


def _mutations(path: str, source: str):
    tree = ast.parse(source)
    scopes = []
    candidates = []
    class Finder(ast.NodeVisitor):
        def visit_FunctionDef(self, node):
            scopes.append(node.name)
            self.generic_visit(node)
            scopes.pop()
        def visit_AsyncFunctionDef(self, node):
            scopes.append(node.name)
            self.generic_visit(node)
            scopes.pop()
        def generic_visit(self, node):
            active = bool(scopes) and (_TARGETS[path] is None or scopes[0] in _TARGETS[path])
            if active:
                if isinstance(node, ast.Compare):
                    partners = {ast.Lt: ast.LtE, ast.LtE: ast.Lt,
                                ast.Gt: ast.GtE, ast.GtE: ast.Gt}
                    for index, op in enumerate(node.ops):
                        for old, new in partners.items():
                            if isinstance(op, old):
                                candidates.append((node, f"{old.__name__}_to_{new.__name__}@{node.col_offset}:{index}",
                                                   ("compare", index, new)))
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"max", "min"}:
                    for index in range(len(node.args)):
                        candidates.append((node, f"{node.func.id}_operand_{index}@{node.col_offset}",
                                           ("call", index)))
                if isinstance(node, ast.If):
                    candidates.append((node, f"if_false@{node.col_offset}", ("if",)))
                if isinstance(node, ast.IfExp):
                    candidates.append((node, f"ifexp_false@{node.col_offset}", ("ifexp",)))
                if isinstance(node, ast.comprehension):
                    for index, test in enumerate(node.ifs):
                        candidates.append((test, f"comprehension_if_false_{index}@{test.col_offset}",
                                           ("replace_false",)))
                if isinstance(node, ast.BoolOp):
                    for index in range(len(node.values)):
                        candidates.append((node, f"{type(node.op).__name__}_delete_{index}@{node.col_offset}",
                                           ("bool", index)))
            super().generic_visit(node)
    Finder().visit(tree)
    for index, (node, description, operation) in enumerate(candidates):
        yield f"{path}:{node.lineno}:{description}", index, candidates, tree


def _rewrite(tree, candidates, index):
    cloned = copy.deepcopy(tree)
    # The visitor traversal is identical on a deep copy, so locate by the
    # original node's source coordinates and structural type.
    original, _, operation = candidates[index]
    matches = [node for node in ast.walk(cloned)
               if type(node) is type(original)
               and getattr(node, "lineno", None) == original.lineno
               and getattr(node, "col_offset", None) == original.col_offset]
    if len(matches) != 1:
        raise RuntimeError(f"ambiguous mutation site {original.lineno}:{original.col_offset}")
    target = matches[0]
    kind = operation[0]
    if kind == "compare":
        target.ops[operation[1]] = operation[2]()
    elif kind == "call":
        replacement = target.args[operation[1]]
        target.func = ast.Name(id="__identity_mutant", ctx=ast.Load())
        target.args = [replacement]
        target.keywords = []
        # Replace the call with its operand, not a helper that may not exist.
        class Replace(ast.NodeTransformer):
            def visit_Call(self, node):
                if node is target:
                    return replacement
                return self.generic_visit(node)
        cloned = Replace().visit(cloned)
    elif kind in {"if", "ifexp"}:
        target.test = ast.Constant(False)
    elif kind == "replace_false":
        class Replace(ast.NodeTransformer):
            def generic_visit(self, node):
                if node is target:
                    return ast.Constant(False)
                return super().generic_visit(node)
        cloned = Replace().visit(cloned)
    else:
        del target.values[operation[1]]
        if len(target.values) == 1:
            replacement = target.values[0]
            class Replace(ast.NodeTransformer):
                def visit_BoolOp(self, node):
                    if node is target:
                        return replacement
                    return self.generic_visit(node)
            cloned = Replace().visit(cloned)
    ast.fix_missing_locations(cloned)
    return ast.unparse(cloned) + "\n"


def mutation_sweep() -> dict:
    mutations = []
    for path in _TARGETS:
        source = (ROOT / path).read_text()
        mutations.extend((path, key, index, candidates, tree)
                         for key, index, candidates, tree in _mutations(path, source))
    killed = 0
    survivors = []
    with tempfile.TemporaryDirectory(prefix="claimgate-mutant-") as temporary:
        command = [sys.executable, "-B", "-c",
                   "from scripts.capture_claim_replay_golden import capture,canonical_bytes,GOLDEN; "
                   "import sys; sys.exit(0 if canonical_bytes(capture()) == GOLDEN.read_bytes() else 1)"]
        def worker(worker_id: int, assigned):
            clone = Path(temporary) / f"checkout-{worker_id}"
            subprocess.run(["git", "clone", "--shared", "--quiet", str(ROOT), str(clone)], check=True)
            for rel in ("scripts/capture_claim_replay_golden.py", "tests/golden/claimgate_v1_replay.json"):
                destination = clone / rel
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / rel, destination)
            baseline = subprocess.run(command, cwd=clone, capture_output=True, text=True)
            if baseline.returncode:
                raise RuntimeError(f"mutation clone baseline differs from golden: {baseline.stderr[-1000:]}")
            originals = {path: (clone / path).read_bytes() for path in _TARGETS}
            local_killed = 0
            local_survivors = []
            for ordinal, (path, key, index, candidates, tree) in enumerate(assigned, start=1):
                target = clone / path
                try:
                    target.write_text(_rewrite(tree, candidates, index))
                    run = subprocess.run(command, cwd=clone, stdout=subprocess.DEVNULL,
                                         stderr=subprocess.DEVNULL)
                    if run.returncode == 0:
                        local_survivors.append(key)
                    else:
                        local_killed += 1
                finally:
                    target.write_bytes(originals[path])
                if ordinal % 100 == 0:
                    print(f"mutation worker {worker_id}: {ordinal}/{len(assigned)}",
                          file=sys.stderr, flush=True)
            return local_killed, local_survivors
        workers = 4
        with ThreadPoolExecutor(max_workers=workers) as pool:
            results = list(pool.map(lambda item: worker(*item),
                                    ((index, mutations[index::workers]) for index in range(workers))))
        for local_killed, local_survivors in results:
            killed += local_killed
            survivors.extend(local_survivors)
    listed = sorted(set(survivors) & set(EQUIVALENT_MUTANTS))
    return {"mutants": len(mutations), "killed": killed, "listed_equivalent": len(listed),
            "unlisted_survivors": sorted(set(survivors) - set(EQUIVALENT_MUTANTS)),
            "listed": listed, "unused_equivalents": sorted(set(EQUIVALENT_MUTANTS) - set(survivors))}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--coverage", action="store_true")
    modes.add_argument("--mutate", action="store_true")
    args = parser.parse_args()
    result = coverage_sweep() if args.coverage else mutation_sweep()
    if args.coverage:
        for name, row in result["functions"].items():
            print(f"{name}: arcs={row['arcs']} covered={row['covered']} "
                  f"uncovered={row['uncovered']} allowlisted={row['allowlisted']}")
        print("unlisted uncovered arcs:", json.dumps(result["unlisted"]))
    else:
        print(f"mutants={result['mutants']} killed={result['killed']} "
              f"listed-equivalent={result['listed_equivalent']} "
              f"unlisted-survivors={len(result['unlisted_survivors'])}")
        print("unlisted survivors:", json.dumps(result["unlisted_survivors"]))
    if result.get("unlisted") or result.get("unlisted_survivors"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
