#!/usr/bin/env python3
"""Certify v1 golden sensitivity once at the reviewed PR-0 source.

Gated: claims, multiplicity, floor resolution, issuance gate, epoch replay.
Measured: artifact validator, estimators, analyze_claims, claim side bound.
Untargeted: reference_envelope and manifest/registry validators.
"""

from __future__ import annotations

import argparse
import ast
from concurrent.futures import ThreadPoolExecutor
import copy
import dis
import inspect
import json
import re
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.capture_claim_replay_golden import GOLDEN, canonical_bytes, capture, _blob_sha

CERTIFICATE = ROOT / "tests/golden/claimgate_v1_sensitivity_certificate.json"
GATED = [
    ("joulewise/analysis_engine/claims.py", None),
    ("joulewise/analysis_engine/multiplicity.py", None),
    ("joulewise/analysis_engine/__init__.py", {"_resolve_contrast_floor"}),
    ("joulewise/paper_custody.py", {"_claim_issuance_gate"}),
    ("scripts/epoch_equivalence_check.py", {"evaluate_session"}),
]
MEASURED = [
    ("joulewise/analysis_engine/artifact.py", {"validate_claim_verdicts"}),
    ("joulewise/analysis_engine/estimators.py", {"estimate_paired_blocks", "_ci_t_critical", "_sample_stddev"}),
    ("joulewise/analysis_engine/__init__.py", {"analyze_claims"}),
    ("joulewise/analysis_engine/claim_side_bound.py", {"produce_claim_side_bound", "validate_claim_side_bound"}),
]

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
        "equivalent: A zero estimate cannot reach direction_supported with a nonnegative floor; negative floors refuse earlier [row: invariant.claim_matrix.direction_at_floor]",
    "joulewise/analysis_engine/claims.py:385:And_delete_1@7":
        "equivalent: direction_supported requires a numeric estimate; the right arc at claims:evaluate_claim:385 is unreachable [row: invariant.claim_matrix.direction_above]",
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


def _mutations(path: str, source: str, functions: set[str] | None):
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
            active = bool(scopes) and (functions is None or scopes[0] in functions)
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
    for path, functions in GATED:
        source = (ROOT / path).read_text()
        mutations.extend(("gated", path, key, index, candidates, tree)
                         for key, index, candidates, tree in _mutations(path, source, functions))
    for path, functions in MEASURED:
        source = (ROOT / path).read_text()
        for function in sorted(functions):
            mutations.extend((f"{path}:{function}", path, key, index, candidates, tree)
                             for key, index, candidates, tree in _mutations(path, source, {function}))
    killed: dict[str, int] = {}
    survivors: dict[str, list[str]] = {}
    with tempfile.TemporaryDirectory(prefix="claimgate-mutant-") as temporary:
        command = [sys.executable, "-B", "-c",
                   "from scripts.capture_claim_replay_golden import capture,canonical_bytes,GOLDEN; "
                   "import json,sys; c=capture(); raw=GOLDEN.read_bytes(); g=json.loads(raw); "
                   "ok=canonical_bytes({**g,'invariant':c['invariant'],'v1_golden_manifest_ids':c['v1_golden_manifest_ids']})==raw "
                   "and all(c['transitions'][r][s]['pre']==g['transitions'][r][s]['pre'] "
                   "for r in g['transitions'] for s in g['transitions'][r]); sys.exit(0 if ok else 1)"]
        def worker(worker_id: int, assigned):
            clone = Path(temporary) / f"checkout-{worker_id}"
            subprocess.run(["git", "clone", "--shared", "--quiet", str(ROOT), str(clone)], check=True)
            for rel in ("scripts/capture_claim_replay_golden.py", "tests/golden/claimgate_v1_replay.json",
                        "tests/golden/claimgate_v1_corpus_bases/gate_fixture.json",
                        "tests/golden/claimgate_v1_corpus_bases/minimal.json"):
                destination = clone / rel
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / rel, destination)
            baseline = subprocess.run(command, cwd=clone, capture_output=True, text=True)
            if baseline.returncode:
                raise RuntimeError(f"mutation clone baseline differs from golden: {baseline.stderr[-1000:]}")
            originals = {path: (clone / path).read_bytes() for path, _ in GATED + MEASURED}
            local_killed: dict[str, int] = {}
            local_survivors: dict[str, list[str]] = {}
            for ordinal, (group, path, key, index, candidates, tree) in enumerate(assigned, start=1):
                target = clone / path
                try:
                    target.write_text(_rewrite(tree, candidates, index))
                    run = subprocess.run(command, cwd=clone, stdout=subprocess.DEVNULL,
                                         stderr=subprocess.DEVNULL)
                    if run.returncode == 0:
                        local_survivors.setdefault(group, []).append(key)
                    else:
                        local_killed[group] = local_killed.get(group, 0) + 1
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
            for group, count in local_killed.items():
                killed[group] = killed.get(group, 0) + count
            for group, keys in local_survivors.items():
                survivors.setdefault(group, []).extend(keys)
    gated_survivors = set(survivors.get("gated", []))
    listed = sorted(gated_survivors & set(EQUIVALENT_MUTANTS))
    gated = {"mutants": sum(group == "gated" for group, *_ in mutations),
             "killed": killed.get("gated", 0), "listed_equivalent": len(listed),
             "unlisted_survivors": sorted(gated_survivors - set(EQUIVALENT_MUTANTS))}
    measured = {}
    for group in sorted({item[0] for item in mutations} - {"gated"}):
        count = sum(item[0] == group for item in mutations)
        dead = killed.get(group, 0)
        measured[group] = {"mutants": count, "killed": dead,
                           "survivors": sorted(survivors.get(group, [])),
                           "kill_rate": dead / count if count else 0.0}
    return {"gated": gated, "measured": measured,
            "unused_equivalents": sorted(set(EQUIVALENT_MUTANTS) - gated_survivors)}


def _golden_path_exists(path: str, golden: dict) -> bool:
    value = golden
    for part in path.split("."):
        if not isinstance(value, dict) or part not in value:
            return False
        value = value[part]
    return True


def _validate_exceptions() -> None:
    golden = json.loads(GOLDEN.read_bytes())
    unreachable = "v1-wire-unreachable: reachable only under the shim scenario; the v1 wire raises KeyError at :632 before this site; re-examine under lane V1-ISSUANCE-GATE-EVIDENCE-CLASS-01"
    for key, proof in EQUIVALENT_MUTANTS.items():
        match = re.fullmatch(r"equivalent: .+ \[row: ([^]]+)\]", proof)
        if match and _golden_path_exists(match.group(1), golden):
            continue
        parts = key.split(":", 2)
        if (proof == unreachable and len(parts) == 3 and
                parts[0] == "joulewise/paper_custody.py" and
                parts[1].isdigit() and int(parts[1]) >= 632 and
                any(key in (mutation_key for mutation_key, *_ in _mutations(
                    parts[0], (ROOT / parts[0]).read_text(), {"_claim_issuance_gate"})))):
            continue
        raise ValueError(f"invalid equivalent mutant proof: {key}: {proof}")


def certify() -> dict:
    _validate_exceptions()
    coverage = coverage_sweep()
    if coverage["unlisted"] or coverage["unused_allowlist"]:
        raise ValueError(f"coverage exceptions: {coverage['unlisted']}; unused: {coverage['unused_allowlist']}")
    mutation = mutation_sweep()
    if mutation["gated"]["unlisted_survivors"] or mutation["unused_equivalents"]:
        raise ValueError(f"mutation exceptions: {mutation['gated']['unlisted_survivors']}; unused: {mutation['unused_equivalents']}")
    paths = {path for path, _ in GATED + MEASURED}
    paths.update(Path(inspect.getsourcefile(function)).resolve().relative_to(ROOT).as_posix()
                 for function in _coverage_functions().values())
    source_blobs = {}
    for path in sorted(paths):
        working = _blob_sha((ROOT / path).read_bytes())
        head = subprocess.check_output(["git", "rev-parse", f"HEAD:{path}"], cwd=ROOT, text=True).strip()
        if working != head:
            raise ValueError(f"source differs from HEAD: {path}")
        source_blobs[path] = head
    certificate = {
        "schema_version": "joulewise.claimgate_v1_sensitivity_certificate.v1",
        "golden_blob_sha": _blob_sha(GOLDEN.read_bytes()),
        "source_blobs": source_blobs,
        "python_version": platform.python_version(),
        "coverage": {"functions": {name: {key: row[key] for key in ("arcs", "covered", "uncovered", "allowlisted")}
                                for name, row in coverage["functions"].items()}, "unlisted": []},
        "mutation": {"gated": mutation["gated"], "measured": mutation["measured"]},
        "equivalent_mutants": EQUIVALENT_MUTANTS,
        "unreachable_arcs": UNREACHABLE_ARCS,
        "meaning": "Sensitivity of the pinned golden to the decision code at source_blobs. Evidence, not a gate; recertify by reviewed PR only.",
    }
    CERTIFICATE.write_bytes(canonical_bytes(certificate))
    return certificate


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--coverage", action="store_true")
    modes.add_argument("--mutate", action="store_true")
    modes.add_argument("--certify", action="store_true")
    args = parser.parse_args()
    if args.certify:
        try:
            result = certify()
        except (ValueError, RuntimeError) as exc:
            print(f"certification refused: {exc}", file=sys.stderr)
            raise SystemExit(2)
        print(json.dumps({"coverage": result["coverage"], "mutation": {
            "gated": result["mutation"]["gated"],
            "measured": {name: {key: row[key] for key in ("mutants", "killed", "kill_rate")}
                         for name, row in result["mutation"]["measured"].items()}}}, sort_keys=True))
        return
    result = coverage_sweep() if args.coverage else mutation_sweep()
    if args.coverage:
        for name, row in result["functions"].items():
            print(f"{name}: arcs={row['arcs']} covered={row['covered']} "
                  f"uncovered={row['uncovered']} allowlisted={row['allowlisted']}")
        print("unlisted uncovered arcs:", json.dumps(result["unlisted"]))
    else:
        print(json.dumps(result["gated"], sort_keys=True))
    if result.get("unlisted") or result.get("gated", {}).get("unlisted_survivors"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
