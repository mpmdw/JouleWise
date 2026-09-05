"""Closed reader inventory: stdlib AST plus a textual grep backstop.

The manifest is reviewed source data, never learned from the checkout at test
runtime. Entries pin path, owning symbol, access kind, normalized AST, count,
and display current lines on drift. Alias handling is deliberately local:
constant keys, import/API aliases, and assignment aliases, not dynamic Python.
"""
from __future__ import annotations

import ast
import html
import json
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCAN_ROOTS = ("joulewise", "scripts", "docs/paper/fill-rehearsal", "tests")
# This file contains the scanner and its self-referential manifest/mutation
# strings, not a helper supplying discipline objects to production consumers.
SOURCE_EXEMPTIONS = {"tests/test_single_count_discipline_census.py"}
KEY = "single_count_discipline"
MARKERS = re.compile(r"single_count_discipline|single.count.discipline|SINGLE_COUNT_DISCIPLINE|DisciplineV[12]|SingleCountDiscipline|planning_sizing_(?:expression|formula)|effective_clearable_effect_formula|attribution_floor_plus_claim_side_bound\.v[12]")
APIS = {
    "attribution_single_count_discipline", "attribution_single_count_discipline_is_canonical",
    "read_single_count_discipline", "read_single_count_profile", "check_single_count_cohort",
    "read_floor_resolution_discipline", "render_single_count_statement", "_read_mint_disciplines",
    "_validate_claim_discipline_cohort", "_validate_attribution_floor_metadata",
    "_ATTRIBUTION_FLOOR_KEYS", "_ATTRIBUTION_LIMIT_CONTAINER_KEYS",
    "_D117_MINT_REPORT_OPTIONAL_KEYS", "_D117_MINT_CELL_OPTIONAL_KEYS",
}
# Exact raw adapter/parser exceptions. No module or function-wide read exemption.
RAW_EXCEPTIONS = {
    ("joulewise/detection_floor.py", "read_single_count_discipline", "carrier.get('single_count_discipline', _DISCIPLINE_ABSENT)"),
    ("joulewise/detection_floor.py", "read_single_count_discipline", "value.get('rule_id')"),
    ("joulewise/analysis_engine/inputs.py", "read_floor_resolution_discipline", "resolution.single_count_discipline"),
}
EMITTERS = {
    ("joulewise/detection_floor.py", "attribution_single_count_discipline"),
    ("joulewise/detection_floor.py", "_add_attribution_limit_metadata"),
    ("joulewise/detection_floor.py", "build_floor_cell"),
    ("joulewise/detection_floor.py", "build_transport_group"),
    ("joulewise/floor_extraction.py", "CellReport.as_row"),
    ("joulewise/floor_extraction.py", "extract_cells"),
}
VOCABULARY = {
    ("joulewise/floor_extraction.py", "_D117_MINT_REPORT_OPTIONAL_KEYS"),
    ("joulewise/floor_extraction.py", "_D117_MINT_CELL_OPTIONAL_KEYS"),
}
SCHEMA_DECLARATIONS = {
    ("joulewise/detection_floor.py", "_ATTRIBUTION_LIMIT_RECORD_KEYS"),
    ("joulewise/detection_floor.py", "_ATTRIBUTION_LIMIT_CONTAINER_KEYS"),
    ("joulewise/analysis_engine/artifact.py", "_ATTRIBUTION_FLOOR_KEYS"),
    ("joulewise/analysis_engine/artifact.py", "_FLOOR_LIMIT_KEYS"),
    ("joulewise/analysis_engine/claims.py", "evaluate_claim"),
    ("joulewise/analysis_engine/inputs.py", "FloorResolution"),
    ("joulewise/analysis_engine/inputs.py", "resolve_floor"),
}
# Independently pinned delegate edges: removing an edge fails even when no raw
# key is present in that function. Calls are inventoried with full normalized AST.
EDGES = {
    ("joulewise/detection_floor.py", "validate_floor_artifact", "read_single_count_profile"),
    ("joulewise/detection_floor.py", "read_single_count_profile", "check_single_count_cohort"),
    ("joulewise/analysis_engine/inputs.py", "authenticate_floor_artifact_bytes", "validate_floor_artifact"),
    ("joulewise/analysis_engine/__init__.py", "_combined_floor", "read_floor_resolution_discipline"),
    ("joulewise/analysis_engine/artifact.py", "validate_claim_verdicts", "_validate_claim_discipline_cohort"),
    ("joulewise/analysis_engine/artifact.py", "finalize_claim_verdicts", "validate_claim_verdicts"),
    ("joulewise/analysis_engine/artifact.py", "write_claim_verdicts_atomic", "validate_claim_verdicts"),
    ("scripts/mint_floor_artifact.py", "render_single_count_statement", "_read_mint_disciplines"),
    ("scripts/mint_floor_artifact.py", "write_outputs_exclusive", "render_single_count_statement"),
    ("scripts/mint_floor_artifact.py", "mint_floor_artifact", "write_outputs_exclusive"),
    ("scripts/mint_floor_artifact.py", "mint_authenticated_artifact", "validate_floor_artifact"),
    ("scripts/mint_floor_artifact_generalized.py", "validate_floor_artifact", "core.validate_floor_artifact"),
    ("scripts/mint_floor_artifact_generalized.py", "_pre_admit_legacy_report", "detection_floor.read_single_count_profile"),
    ("scripts/mint_floor_artifact_generalized.py", "_v2_gate_postcollection", "detection_floor.read_single_count_profile"),
    ("scripts/mint_floor_artifact_generalized.py", "_write_v2_artifact_outputs", "output_core.render_single_count_statement"),
    ("scripts/mint_floor_artifact_generalized.py", "_mint_multi_cell_floor_artifact_active", "output_core.write_outputs_exclusive"),
    ("scripts/mint_floor_artifact_generalized.py", "_mint_multi_cell_floor_artifact_active", "_write_v2_artifact_outputs"),
    ("scripts/mint_floor_artifact_generalized.py", "mint_floor_artifact", "core.mint_floor_artifact"),
    ("scripts/mint_floor_artifact_generalized.py", "mint_authenticated_artifact", "core.mint_authenticated_artifact"),
}


def sources():
    return {str(path.relative_to(ROOT)): path.read_text(encoding="utf-8")
            for directory in SCAN_ROOTS
            for path in sorted((ROOT / directory).rglob("*.py"))}


def helper_source(path, source):
    """Scan reusable test helpers, retaining source lines for the grep pin.

    Test entry-point bodies contain intentional malformed objects and raw
    assertions. Omit those bodies; retain imports, fixtures, setup/teardown,
    module functions and other class methods, including their nested helpers.
    Paper rehearsal scripts are scanned in full.
    """
    if path in SOURCE_EXEMPTIONS:
        return ""
    if not path.startswith("tests/"):
        return source
    lines = source.splitlines(keepends=True)
    tree = ast.parse(source, filename=path)
    entry_points = [node for node in tree.body
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            entry_points.extend(child for child in node.body
                                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)))
    for node in entry_points:
        if node.name.startswith("test_"):
            start = min([node.lineno] + [item.lineno for item in node.decorator_list]) - 1
            lines[start:node.end_lineno] = [
                " " * node.col_offset + "pass\n",
                *["\n"] * (node.end_lineno - start - 1),
            ]
    return "".join(lines)


def normalized_ast(node):
    """Ignore empty optional fields added by Python (for example type_params).

    A structural tuple avoids ast.dump formatting changes between supported
    Python 3.11 and newer runtimes; source locations never enter the pin.
    """
    def shape(value):
        if isinstance(value, ast.AST):
            return (type(value).__name__, tuple(
                (name, shape(child)) for name, child in ast.iter_fields(value)
                if child is not None and child != []
            ))
        if isinstance(value, list):
            return tuple(shape(child) for child in value)
        return value
    return repr(shape(node))


@lru_cache(maxsize=2048)
def scan_source(path, source):
    source = helper_source(path, source)
    tree = ast.parse(source, filename=path)
    parents = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
    events = defaultdict(list)
    edges = set()
    raw = []
    owners = {}

    def owner(node):
        if node in owners:
            return owners[node]
        parts = [node.name] if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) else []
        current = node
        while current in parents:
            current = parents[current]
            if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                parts.append(current.name)
        if not parts:
            current = node
            while current in parents and not isinstance(parents[current], ast.Module):
                current = parents[current]
            if isinstance(current, ast.Assign) and isinstance(current.targets[0], ast.Name):
                parts = [current.targets[0].id]
        result = ".".join(reversed(parts)) or "<module>"
        owners[node] = result
        return result

    aliases = {node.asname or node.name: node.name for node in ast.walk(tree)
               if isinstance(node, ast.alias) and node.name in APIS}
    key_aliases = {}
    derived = defaultdict(set)
    wire_copies = defaultdict(set)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) and node.value.value == KEY:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    key_aliases[(owner(node), target.id)] = KEY
    # Fixed point over simple assignment aliases only. No dataflow claims about
    # dynamic code, arbitrary calls, or interprocedural Python taint.
    changed = True
    while changed:
        changed = False
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Assign, ast.AnnAssign)) or node.value is None:
                continue
            symbol = owner(node)
            if (isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute)
                    and node.value.func.attr == "copy_wire"):
                for target in node.targets if isinstance(node, ast.Assign) else (node.target,):
                    if isinstance(target, ast.Name):
                        wire_copies[symbol].add(target.id)
            has_source = any(
                (isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value == KEY)
                or (isinstance(n, ast.Attribute) and n.attr == KEY)
                or (isinstance(n, ast.Name) and n.id in derived[symbol])
                for n in ast.walk(node.value)
            )
            if has_source:
                for target in node.targets if isinstance(node, ast.Assign) else (node.target,):
                    if isinstance(target, ast.Name) and target.id not in derived[symbol]:
                        derived[symbol].add(target.id)
                        changed = True

    def add(node, kind, normalized=None):
        normalized = normalized or normalized_ast(node)
        events[(path, owner(node), kind, normalized)].append(node.lineno)

    def key_value(node):
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Name):
            return key_aliases.get((owner(node), node.id))
        return None

    for node in ast.walk(tree):
        symbol = owner(node)
        if isinstance(node, ast.FunctionDef) and path == "joulewise/detection_floor.py" and node.name == "attribution_single_count_discipline":
            add(node, "canonical-emitter")
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Subscript) and key_value(target.slice) == KEY:
                    emission = isinstance(node.value, ast.Call) and ast.unparse(node.value.func) == "attribution_single_count_discipline"
                    add(node, "emitter" if emission and (path, symbol) in EMITTERS else "output")
        if isinstance(node, ast.Call):
            call = ast.unparse(node.func)
            call = aliases.get(call, call)
            edge = (path, symbol, call)
            if edge in EDGES:
                edges.add(edge)
                add(node, "delegate")
            elif call.split(".")[-1] in APIS:
                add(node, "delegate")
        expression = None
        key = None
        receiver = None
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in ("get", "pop", "setdefault", "__getitem__") and node.args:
            key = key_value(node.args[0]); receiver = node.func.value; expression = node
        elif isinstance(node, ast.Subscript) and isinstance(node.ctx, ast.Load):
            key = key_value(node.slice); receiver = node.value; expression = node
        elif isinstance(node, ast.Attribute) and node.attr == KEY and isinstance(node.ctx, ast.Load):
            key = KEY; receiver = node.value; expression = node
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ("getattr", "hasattr") and len(node.args) > 1:
            key = key_value(node.args[1]); receiver = node.args[0]; expression = node
        if expression is not None:
            if key in ("planning_sizing_expression", "planning_sizing_formula", "effective_clearable_effect_formula"):
                typed = isinstance(receiver, ast.Name) and receiver.id in wire_copies[symbol]
                add(expression, "typed-reader" if typed else "RAW-UNCLASSIFIED")
                if not typed:
                    raw.append((path, symbol, ast.unparse(expression), node.lineno))
            discipline_id = key == "rule_id" and (
                (path == "joulewise/detection_floor.py" and symbol == "read_single_count_discipline")
                or any(isinstance(n, ast.Name) and n.id in derived[symbol] for n in ast.walk(receiver)))
            if key == KEY or discipline_id:
                location = (path, symbol, ast.unparse(expression))
                kind = "parser" if location in RAW_EXCEPTIONS else "RAW-UNCLASSIFIED"
                add(expression, kind)
                if kind == "RAW-UNCLASSIFIED":
                    raw.append((*location, node.lineno))
        if isinstance(node, ast.Attribute) and node.attr in ("copy_wire", "rule_id"):
            add(node, "typed-reader")
        if isinstance(node, ast.Name) and (node.id in APIS or node.id in aliases):
            add(node, "api-alias" if node.id in aliases and node.id != aliases[node.id] else "api-reference")
        if isinstance(node, ast.alias) and (node.name in APIS or MARKERS.search(node.name)):
            add(node, "api-alias")
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == KEY:
            add(node, "schema")
        if isinstance(node, ast.keyword) and node.arg == KEY:
            add(node, "output")
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and MARKERS.search(node.value):
            parent = parents.get(node)
            if node.value == KEY:
                if (path, symbol) in VOCABULARY:
                    kind = "vocabulary"
                elif (path, symbol) in SCHEMA_DECLARATIONS and isinstance(parent, (ast.Set, ast.Tuple)):
                    kind = "schema"
                    add(parent, kind)
                elif isinstance(parent, ast.Dict) and node in parent.keys:
                    index = parent.keys.index(node)
                    value = parent.values[index]
                    emission = any(isinstance(n, ast.Call) and ast.unparse(n.func) == "attribution_single_count_discipline" for n in ast.walk(value))
                    kind = "emitter" if emission and (path, symbol) in EMITTERS else "output"
                    add(value, kind)
                else:
                    kind = "key-token"
            else:
                kind = "version" if re.fullmatch(r"attribution_floor_plus_claim_side_bound\.v[12]", node.value) else "text-token"
            add(node, kind)
    # Grep backstop inventories exact matching text independently of AST
    # classification, including unsupported string spellings and comments.
    # Pure reflows require reviewed manifest updates; revisiting this cost is
    # a post-submission decision (counter-review 45, N2).
    for line_number, line in enumerate(source.splitlines(), 1):
        if MARKERS.search(line):
            events[(path, "<grep>", "grep", line.strip())].append(line_number)
    return events, edges, raw


def census(source_map):
    events = defaultdict(list)
    edges = set()
    raw = []
    for path, source in source_map.items():
        found, delegates, raw_reads = scan_source(path, source)
        events.update(found); edges.update(delegates); raw.extend(raw_reads)
    return events, edges, raw


def assert_inventory(source_map):
    events, edges, raw = census(source_map)
    actual = Counter({key: len(lines) for key, lines in events.items()})
    expected = Counter({tuple(row[:4]): row[4] for row in MANIFEST})
    if raw:
        raise AssertionError(f"unclassified raw readers: {raw}")
    missing_edges = EDGES - edges
    if missing_edges:
        raise AssertionError(f"deleted delegate edges: {sorted(missing_edges)}")
    if actual != expected:
        added = [(key, count, events[key]) for key, count in (actual - expected).items()]
        stale = list((expected - actual).items())
        raise AssertionError(f"reader census drift; added (with lines): {added}; stale: {stale}")


# Reviewed manifest: path, symbol, kind, normalized AST (or grep text), multiplicity.
MANIFEST = [('joulewise/analysis_engine/__init__.py', '<grep>', 'grep', '"single_count_discipline": discipline.copy_wire(),', 2),
 ('joulewise/analysis_engine/__init__.py', '<grep>', 'grep',
  '"single_count_discipline": disciplines[resolutions.index(limited[0])].copy_wire(),', 1),
 ('joulewise/analysis_engine/__init__.py', '<grep>', 'grep', 'SingleCountDisciplineError,', 1),
 ('joulewise/analysis_engine/__init__.py', '<grep>', 'grep',
  'discipline = read_single_count_discipline(active_floor, where="active floor")', 1),
 ('joulewise/analysis_engine/__init__.py', '<grep>', 'grep', 'except SingleCountDisciplineError as exc:', 2),
 ('joulewise/analysis_engine/__init__.py', '<grep>', 'grep', 'f"floor resolutions mix single-count discipline rule versions: {exc}"', 1),
 ('joulewise/analysis_engine/__init__.py', '<grep>', 'grep', 'f"floor_resolution_single_count_discipline_invalid: {exc}"', 1),
 ('joulewise/analysis_engine/__init__.py', '<grep>', 'grep', 'read_single_count_discipline,', 1),
 ('joulewise/analysis_engine/__init__.py', '<module>', 'api-alias', "('alias', (('name', 'SingleCountDisciplineError'),))", 1),
 ('joulewise/analysis_engine/__init__.py', '<module>', 'api-alias', "('alias', (('name', 'check_single_count_cohort'),))", 1),
 ('joulewise/analysis_engine/__init__.py', '<module>', 'api-alias', "('alias', (('name', 'read_floor_resolution_discipline'),))", 1),
 ('joulewise/analysis_engine/__init__.py', '<module>', 'api-alias', "('alias', (('name', 'read_single_count_discipline'),))", 1),
 ('joulewise/analysis_engine/__init__.py', '_combined_floor', 'api-reference',
  "('Name', (('id', 'check_single_count_cohort'), ('ctx', ('Load', ()))))", 1),
 ('joulewise/analysis_engine/__init__.py', '_combined_floor', 'api-reference',
  "('Name', (('id', 'read_floor_resolution_discipline'), ('ctx', ('Load', ()))))", 1),
 ('joulewise/analysis_engine/__init__.py', '_combined_floor', 'delegate',
  "('Call', (('func', ('Name', (('id', 'check_single_count_cohort'), ('ctx', ('Load', ()))))), ('args', (('Name', (('id', 'disciplines'), "
  "('ctx', ('Load', ())))),)), ('keywords', (('keyword', (('arg', 'where'), ('value', ('Constant', (('value', 'floor "
  "resolutions'),))))),))))",
  1),
 ('joulewise/analysis_engine/__init__.py', '_combined_floor', 'delegate',
  "('Call', (('func', ('Name', (('id', 'read_floor_resolution_discipline'), ('ctx', ('Load', ()))))), ('args', (('Name', (('id', 'value'), "
  "('ctx', ('Load', ())))),))))",
  1),
 ('joulewise/analysis_engine/__init__.py', '_combined_floor', 'output',
  "('Call', (('func', ('Attribute', (('value', ('Name', (('id', 'discipline'), ('ctx', ('Load', ()))))), ('attr', 'copy_wire'), ('ctx', "
  "('Load', ()))))),))",
  1),
 ('joulewise/analysis_engine/__init__.py', '_combined_floor', 'output',
  "('Call', (('func', ('Attribute', (('value', ('Subscript', (('value', ('Name', (('id', 'disciplines'), ('ctx', ('Load', ()))))), "
  "('slice', ('Call', (('func', ('Attribute', (('value', ('Name', (('id', 'resolutions'), ('ctx', ('Load', ()))))), ('attr', 'index'), "
  "('ctx', ('Load', ()))))), ('args', (('Subscript', (('value', ('Name', (('id', 'limited'), ('ctx', ('Load', ()))))), ('slice', "
  "('Constant', (('value', 0),))), ('ctx', ('Load', ())))),))))), ('ctx', ('Load', ()))))), ('attr', 'copy_wire'), ('ctx', ('Load', "
  '()))))),))',
  1),
 ('joulewise/analysis_engine/__init__.py', '_combined_floor', 'output', "('Constant', (('value', 'single_count_discipline'),))", 2),
 ('joulewise/analysis_engine/__init__.py', '_combined_floor', 'text-token',
  "('Constant', (('value', 'floor resolutions mix single-count discipline rule versions: '),))", 1),
 ('joulewise/analysis_engine/__init__.py', '_combined_floor', 'text-token',
  "('Constant', (('value', 'floor_resolution_single_count_discipline_invalid: '),))", 1),
 ('joulewise/analysis_engine/__init__.py', '_combined_floor', 'typed-reader',
  "('Attribute', (('value', ('Name', (('id', 'discipline'), ('ctx', ('Load', ()))))), ('attr', 'copy_wire'), ('ctx', ('Load', ()))))", 1),
 ('joulewise/analysis_engine/__init__.py', '_combined_floor', 'typed-reader',
  "('Attribute', (('value', ('Subscript', (('value', ('Name', (('id', 'disciplines'), ('ctx', ('Load', ()))))), ('slice', ('Call', "
  "(('func', ('Attribute', (('value', ('Name', (('id', 'resolutions'), ('ctx', ('Load', ()))))), ('attr', 'index'), ('ctx', ('Load', "
  "()))))), ('args', (('Subscript', (('value', ('Name', (('id', 'limited'), ('ctx', ('Load', ()))))), ('slice', ('Constant', (('value', "
  "0),))), ('ctx', ('Load', ())))),))))), ('ctx', ('Load', ()))))), ('attr', 'copy_wire'), ('ctx', ('Load', ()))))",
  1),
 ('joulewise/analysis_engine/__init__.py', '_evaluation', 'api-reference',
  "('Name', (('id', 'read_single_count_discipline'), ('ctx', ('Load', ()))))", 1),
 ('joulewise/analysis_engine/__init__.py', '_evaluation', 'delegate',
  "('Call', (('func', ('Name', (('id', 'read_single_count_discipline'), ('ctx', ('Load', ()))))), ('args', (('Name', (('id', "
  "'active_floor'), ('ctx', ('Load', ())))),)), ('keywords', (('keyword', (('arg', 'where'), ('value', ('Constant', (('value', 'active "
  "floor'),))))),))))",
  1),
 ('joulewise/analysis_engine/__init__.py', '_evaluation', 'output',
  "('Call', (('func', ('Attribute', (('value', ('Name', (('id', 'discipline'), ('ctx', ('Load', ()))))), ('attr', 'copy_wire'), ('ctx', "
  "('Load', ()))))),))",
  1),
 ('joulewise/analysis_engine/__init__.py', '_evaluation', 'output', "('Constant', (('value', 'single_count_discipline'),))", 1),
 ('joulewise/analysis_engine/__init__.py', '_evaluation', 'typed-reader',
  "('Attribute', (('value', ('Name', (('id', 'discipline'), ('ctx', ('Load', ()))))), ('attr', 'copy_wire'), ('ctx', ('Load', ()))))", 1),
 ('joulewise/analysis_engine/artifact.py', '<grep>', 'grep', '"single_count_discipline",', 2),
 ('joulewise/analysis_engine/artifact.py', '<grep>', 'grep', '"single_count_discipline": discipline.copy_wire(),', 1),
 ('joulewise/analysis_engine/artifact.py', '<grep>', 'grep', 'SingleCountDisciplineError,', 1),
 ('joulewise/analysis_engine/artifact.py', '<grep>', 'grep', 'discipline = read_single_count_discipline(floor, where=f"{where}.floor")', 1),
 ('joulewise/analysis_engine/artifact.py', '<grep>', 'grep', 'except SingleCountDisciplineError as exc:', 4),
 ('joulewise/analysis_engine/artifact.py', '<grep>', 'grep', 'read_single_count_discipline(value, where=where, required=True)', 1),
 ('joulewise/analysis_engine/artifact.py', '<grep>', 'grep', 'read_single_count_discipline,', 1),
 ('joulewise/analysis_engine/artifact.py', '<grep>', 'grep', 'views.append(read_single_count_discipline(carrier, where=location))', 1),
 ('joulewise/analysis_engine/artifact.py', '<module>', 'api-alias', "('alias', (('name', 'SingleCountDisciplineError'),))", 1),
 ('joulewise/analysis_engine/artifact.py', '<module>', 'api-alias', "('alias', (('name', 'check_single_count_cohort'),))", 1),
 ('joulewise/analysis_engine/artifact.py', '<module>', 'api-alias', "('alias', (('name', 'read_single_count_discipline'),))", 1),
 ('joulewise/analysis_engine/artifact.py', '_ATTRIBUTION_FLOOR_KEYS', 'api-reference',
  "('Name', (('id', '_ATTRIBUTION_FLOOR_KEYS'), ('ctx', ('Store', ()))))", 1),
 ('joulewise/analysis_engine/artifact.py', '_ATTRIBUTION_FLOOR_KEYS', 'schema', "('Constant', (('value', 'single_count_discipline'),))", 1),
 ('joulewise/analysis_engine/artifact.py', '_ATTRIBUTION_FLOOR_KEYS', 'schema',
  "('Set', (('elts', (('Constant', (('value', 'floor_source'),)), ('Constant', (('value', 'floor_limit_class'),)), ('Constant', (('value', "
  "'point_floor_diagnostics'),)), ('Constant', (('value', 'single_count_discipline'),)))),))",
  1),
 ('joulewise/analysis_engine/artifact.py', '_FLOOR_LIMIT_KEYS', 'schema', "('Constant', (('value', 'single_count_discipline'),))", 1),
 ('joulewise/analysis_engine/artifact.py', '_FLOOR_LIMIT_KEYS', 'schema',
  "('Set', (('elts', (('Constant', (('value', 'floor_source'),)), ('Constant', (('value', 'floor_limit_class'),)), ('Constant', (('value', "
  "'published_floor_j'),)), ('Constant', (('value', 'point_floor_diagnostics'),)), ('Constant', (('value', "
  "'single_count_discipline'),)))),))",
  1),
 ('joulewise/analysis_engine/artifact.py', '_validate_attribution_floor_metadata', 'api-reference',
  "('Name', (('id', 'read_single_count_discipline'), ('ctx', ('Load', ()))))", 1),
 ('joulewise/analysis_engine/artifact.py', '_validate_attribution_floor_metadata', 'delegate',
  "('Call', (('func', ('Name', (('id', 'read_single_count_discipline'), ('ctx', ('Load', ()))))), ('args', (('Name', (('id', 'value'), "
  "('ctx', ('Load', ())))),)), ('keywords', (('keyword', (('arg', 'where'), ('value', ('Name', (('id', 'where'), ('ctx', ('Load', "
  "()))))))), ('keyword', (('arg', 'required'), ('value', ('Constant', (('value', True),)))))))))",
  1),
 ('joulewise/analysis_engine/artifact.py', '_validate_claim_discipline_cohort', 'api-reference',
  "('Name', (('id', 'check_single_count_cohort'), ('ctx', ('Load', ()))))", 1),
 ('joulewise/analysis_engine/artifact.py', '_validate_claim_discipline_cohort', 'api-reference',
  "('Name', (('id', 'read_single_count_discipline'), ('ctx', ('Load', ()))))", 1),
 ('joulewise/analysis_engine/artifact.py', '_validate_claim_discipline_cohort', 'delegate',
  "('Call', (('func', ('Name', (('id', 'check_single_count_cohort'), ('ctx', ('Load', ()))))), ('args', (('Name', (('id', 'views'), "
  "('ctx', ('Load', ())))),)), ('keywords', (('keyword', (('arg', 'where'), ('value', ('Name', (('id', 'where'), ('ctx', ('Load', "
  '()))))))),))))',
  1),
 ('joulewise/analysis_engine/artifact.py', '_validate_claim_discipline_cohort', 'delegate',
  "('Call', (('func', ('Name', (('id', 'read_single_count_discipline'), ('ctx', ('Load', ()))))), ('args', (('Name', (('id', 'carrier'), "
  "('ctx', ('Load', ())))),)), ('keywords', (('keyword', (('arg', 'where'), ('value', ('Name', (('id', 'location'), ('ctx', ('Load', "
  '()))))))),))))',
  1),
 ('joulewise/analysis_engine/artifact.py', '_validate_cross_field_claim_semantics', 'api-reference',
  "('Name', (('id', 'read_single_count_discipline'), ('ctx', ('Load', ()))))", 1),
 ('joulewise/analysis_engine/artifact.py', '_validate_cross_field_claim_semantics', 'delegate',
  "('Call', (('func', ('Name', (('id', 'read_single_count_discipline'), ('ctx', ('Load', ()))))), ('args', (('Name', (('id', 'floor'), "
  "('ctx', ('Load', ())))),)), ('keywords', (('keyword', (('arg', 'where'), ('value', ('JoinedStr', (('values', (('FormattedValue', "
  "(('value', ('Name', (('id', 'where'), ('ctx', ('Load', ()))))), ('conversion', -1))), ('Constant', (('value', '.floor'),)))),))))),))))",
  1),
 ('joulewise/analysis_engine/artifact.py', '_validate_cross_field_claim_semantics', 'output',
  "('Call', (('func', ('Attribute', (('value', ('Name', (('id', 'discipline'), ('ctx', ('Load', ()))))), ('attr', 'copy_wire'), ('ctx', "
  "('Load', ()))))),))",
  1),
 ('joulewise/analysis_engine/artifact.py', '_validate_cross_field_claim_semantics', 'output',
  "('Constant', (('value', 'single_count_discipline'),))", 1),
 ('joulewise/analysis_engine/artifact.py', '_validate_cross_field_claim_semantics', 'typed-reader',
  "('Attribute', (('value', ('Name', (('id', 'discipline'), ('ctx', ('Load', ()))))), ('attr', 'copy_wire'), ('ctx', ('Load', ()))))", 1),
 ('joulewise/analysis_engine/artifact.py', 'finalize_claim_verdicts', 'delegate',
  "('Call', (('func', ('Name', (('id', 'validate_claim_verdicts'), ('ctx', ('Load', ()))))), ('args', (('Name', (('id', 'artifact'), "
  "('ctx', ('Load', ())))),)), ('keywords', (('keyword', (('arg', 'frozen_manifest'), ('value', ('Name', (('id', 'frozen_manifest'), "
  "('ctx', ('Load', ()))))))),))))",
  1),
 ('joulewise/analysis_engine/artifact.py', 'validate_claim_verdicts', 'api-reference',
  "('Name', (('id', '_ATTRIBUTION_FLOOR_KEYS'), ('ctx', ('Load', ()))))", 7),
 ('joulewise/analysis_engine/artifact.py', 'validate_claim_verdicts', 'api-reference',
  "('Name', (('id', '_validate_attribution_floor_metadata'), ('ctx', ('Load', ()))))", 3),
 ('joulewise/analysis_engine/artifact.py', 'validate_claim_verdicts', 'api-reference',
  "('Name', (('id', '_validate_claim_discipline_cohort'), ('ctx', ('Load', ()))))", 1),
 ('joulewise/analysis_engine/artifact.py', 'validate_claim_verdicts', 'delegate',
  "('Call', (('func', ('Name', (('id', '_validate_attribution_floor_metadata'), ('ctx', ('Load', ()))))), ('args', (('Name', (('id', "
  "'floor'), ('ctx', ('Load', ())))), ('JoinedStr', (('values', (('FormattedValue', (('value', ('Name', (('id', 'where'), ('ctx', ('Load', "
  "()))))), ('conversion', -1))), ('Constant', (('value', '.floor'),)))),)), ('Name', (('id', 'errors'), ('ctx', ('Load', ()))))))))",
  1),
 ('joulewise/analysis_engine/artifact.py', 'validate_claim_verdicts', 'delegate',
  "('Call', (('func', ('Name', (('id', '_validate_attribution_floor_metadata'), ('ctx', ('Load', ()))))), ('args', (('Name', (('id', "
  "'floor_limit'), ('ctx', ('Load', ())))), ('JoinedStr', (('values', (('FormattedValue', (('value', ('Name', (('id', 'where'), ('ctx', "
  "('Load', ()))))), ('conversion', -1))), ('Constant', (('value', '.claim_evaluation.floor_limit'),)))),)), ('Name', (('id', 'errors'), "
  "('ctx', ('Load', ()))))))))",
  1),
 ('joulewise/analysis_engine/artifact.py', 'validate_claim_verdicts', 'delegate',
  "('Call', (('func', ('Name', (('id', '_validate_attribution_floor_metadata'), ('ctx', ('Load', ()))))), ('args', (('Name', (('id', "
  "'resolution'), ('ctx', ('Load', ())))), ('Name', (('id', 'resolution_where'), ('ctx', ('Load', ())))), ('Name', (('id', 'errors'), "
  "('ctx', ('Load', ()))))))))",
  1),
 ('joulewise/analysis_engine/artifact.py', 'validate_claim_verdicts', 'delegate',
  "('Call', (('func', ('Name', (('id', '_validate_claim_discipline_cohort'), ('ctx', ('Load', ()))))), ('args', (('Name', (('id', "
  "'contrast'), ('ctx', ('Load', ())))), ('Name', (('id', 'where'), ('ctx', ('Load', ())))), ('Name', (('id', 'errors'), ('ctx', ('Load', "
  '()))))))))',
  1),
 ('joulewise/analysis_engine/artifact.py', 'write_claim_verdicts_atomic', 'delegate',
  "('Call', (('func', ('Name', (('id', 'validate_claim_verdicts'), ('ctx', ('Load', ()))))), ('args', (('Name', (('id', 'value'), ('ctx', "
  "('Load', ())))),)), ('keywords', (('keyword', (('arg', 'frozen_manifest'), ('value', ('Name', (('id', 'frozen_manifest'), ('ctx', "
  "('Load', ()))))))),))))",
  1),
 ('joulewise/analysis_engine/claims.py', '<grep>', 'grep', '"single_count_discipline",', 1),
 ('joulewise/analysis_engine/claims.py', '<grep>', 'grep', '"single_count_discipline": discipline.copy_wire(),', 1),
 ('joulewise/analysis_engine/claims.py', '<grep>', 'grep', 'SingleCountDisciplineError,', 1),
 ('joulewise/analysis_engine/claims.py', '<grep>', 'grep', 'discipline = read_single_count_discipline(', 1),
 ('joulewise/analysis_engine/claims.py', '<grep>', 'grep', 'except SingleCountDisciplineError:', 1),
 ('joulewise/analysis_engine/claims.py', '<grep>', 'grep', 'read_single_count_discipline,', 1),
 ('joulewise/analysis_engine/claims.py', '<module>', 'api-alias', "('alias', (('name', 'SingleCountDisciplineError'),))", 1),
 ('joulewise/analysis_engine/claims.py', '<module>', 'api-alias', "('alias', (('name', 'read_single_count_discipline'),))", 1),
 ('joulewise/analysis_engine/claims.py', 'evaluate_claim', 'api-reference',
  "('Name', (('id', 'read_single_count_discipline'), ('ctx', ('Load', ()))))", 1),
 ('joulewise/analysis_engine/claims.py', 'evaluate_claim', 'delegate',
  "('Call', (('func', ('Name', (('id', 'read_single_count_discipline'), ('ctx', ('Load', ()))))), ('args', (('Name', (('id', "
  "'floor_metadata'), ('ctx', ('Load', ())))),)), ('keywords', (('keyword', (('arg', 'where'), ('value', ('Constant', (('value', 'claim "
  "floor metadata'),))))), ('keyword', (('arg', 'required'), ('value', ('Constant', (('value', True),)))))))))",
  1),
 ('joulewise/analysis_engine/claims.py', 'evaluate_claim', 'output',
  "('Call', (('func', ('Attribute', (('value', ('Name', (('id', 'discipline'), ('ctx', ('Load', ()))))), ('attr', 'copy_wire'), ('ctx', "
  "('Load', ()))))),))",
  1),
 ('joulewise/analysis_engine/claims.py', 'evaluate_claim', 'output', "('Constant', (('value', 'single_count_discipline'),))", 1),
 ('joulewise/analysis_engine/claims.py', 'evaluate_claim', 'schema', "('Constant', (('value', 'single_count_discipline'),))", 1),
 ('joulewise/analysis_engine/claims.py', 'evaluate_claim', 'schema',
  "('Set', (('elts', (('Constant', (('value', 'floor_limit_class'),)), ('Constant', (('value', 'floor_source'),)), ('Constant', (('value', "
  "'point_floor_diagnostics'),)), ('Constant', (('value', 'single_count_discipline'),)))),))",
  1),
 ('joulewise/analysis_engine/claims.py', 'evaluate_claim', 'typed-reader',
  "('Attribute', (('value', ('Name', (('id', 'discipline'), ('ctx', ('Load', ()))))), ('attr', 'copy_wire'), ('ctx', ('Load', ()))))", 1),
 ('joulewise/analysis_engine/inputs.py', '<grep>', 'grep', '"single_count_discipline",', 2),
 ('joulewise/analysis_engine/inputs.py', '<grep>', 'grep', 'SingleCountDisciplineError,', 1),
 ('joulewise/analysis_engine/inputs.py', '<grep>', 'grep', 'carrier["single_count_discipline"] = resolution.single_count_discipline', 1),
 ('joulewise/analysis_engine/inputs.py', '<grep>', 'grep', 'except SingleCountDisciplineError:', 2),
 ('joulewise/analysis_engine/inputs.py', '<grep>', 'grep', 'if resolution.single_count_discipline is not None:', 1),
 ('joulewise/analysis_engine/inputs.py', '<grep>', 'grep', 'read_single_count_discipline,', 1),
 ('joulewise/analysis_engine/inputs.py', '<grep>', 'grep', 'return read_single_count_discipline(carrier, where="floor resolution")', 1),
 ('joulewise/analysis_engine/inputs.py', '<grep>', 'grep', 'single_count = read_single_count_discipline(cell, where="selected cell")', 1),
 ('joulewise/analysis_engine/inputs.py', '<grep>', 'grep', 'single_count = read_single_count_discipline(group, where="selected group")', 1),
 ('joulewise/analysis_engine/inputs.py', '<grep>', 'grep', 'single_count_discipline: Mapping[str, Any] | None = None', 1),
 ('joulewise/analysis_engine/inputs.py', '<grep>', 'grep', 'single_count_discipline=(', 2),
 ('joulewise/analysis_engine/inputs.py', '<module>', 'api-alias', "('alias', (('name', 'SingleCountDisciplineError'),))", 1),
 ('joulewise/analysis_engine/inputs.py', '<module>', 'api-alias', "('alias', (('name', 'read_single_count_discipline'),))", 1),
 ('joulewise/analysis_engine/inputs.py', 'FloorResolution', 'schema',
  "('AnnAssign', (('target', ('Name', (('id', 'single_count_discipline'), ('ctx', ('Store', ()))))), ('annotation', ('BinOp', (('left', "
  "('Subscript', (('value', ('Name', (('id', 'Mapping'), ('ctx', ('Load', ()))))), ('slice', ('Tuple', (('elts', (('Name', (('id', 'str'), "
  "('ctx', ('Load', ())))), ('Name', (('id', 'Any'), ('ctx', ('Load', ())))))), ('ctx', ('Load', ()))))), ('ctx', ('Load', ()))))), ('op', "
  "('BitOr', ())), ('right', ('Constant', ()))))), ('value', ('Constant', ())), ('simple', 1)))",
  1),
 ('joulewise/analysis_engine/inputs.py', 'authenticate_floor_artifact_bytes', 'delegate',
  "('Call', (('func', ('Name', (('id', 'validate_floor_artifact'), ('ctx', ('Load', ()))))), ('args', (('Name', (('id', 'value'), ('ctx', "
  "('Load', ())))),))))",
  1),
 ('joulewise/analysis_engine/inputs.py', 'read_floor_resolution_discipline', 'api-reference',
  "('Name', (('id', 'read_single_count_discipline'), ('ctx', ('Load', ()))))", 1),
 ('joulewise/analysis_engine/inputs.py', 'read_floor_resolution_discipline', 'delegate',
  "('Call', (('func', ('Name', (('id', 'read_single_count_discipline'), ('ctx', ('Load', ()))))), ('args', (('Name', (('id', 'carrier'), "
  "('ctx', ('Load', ())))),)), ('keywords', (('keyword', (('arg', 'where'), ('value', ('Constant', (('value', 'floor "
  "resolution'),))))),))))",
  1),
 ('joulewise/analysis_engine/inputs.py', 'read_floor_resolution_discipline', 'key-token',
  "('Constant', (('value', 'single_count_discipline'),))", 1),
 ('joulewise/analysis_engine/inputs.py', 'read_floor_resolution_discipline', 'output',
  "('Assign', (('targets', (('Subscript', (('value', ('Name', (('id', 'carrier'), ('ctx', ('Load', ()))))), ('slice', ('Constant', "
  "(('value', 'single_count_discipline'),))), ('ctx', ('Store', ())))),)), ('value', ('Attribute', (('value', ('Name', (('id', "
  "'resolution'), ('ctx', ('Load', ()))))), ('attr', 'single_count_discipline'), ('ctx', ('Load', ())))))))",
  1),
 ('joulewise/analysis_engine/inputs.py', 'read_floor_resolution_discipline', 'parser',
  "('Attribute', (('value', ('Name', (('id', 'resolution'), ('ctx', ('Load', ()))))), ('attr', 'single_count_discipline'), ('ctx', "
  "('Load', ()))))",
  2),
 ('joulewise/analysis_engine/inputs.py', 'resolve_floor', 'api-reference',
  "('Name', (('id', 'read_single_count_discipline'), ('ctx', ('Load', ()))))", 2),
 ('joulewise/analysis_engine/inputs.py', 'resolve_floor', 'delegate',
  "('Call', (('func', ('Name', (('id', 'read_single_count_discipline'), ('ctx', ('Load', ()))))), ('args', (('Name', (('id', 'cell'), "
  "('ctx', ('Load', ())))),)), ('keywords', (('keyword', (('arg', 'where'), ('value', ('Constant', (('value', 'selected cell'),))))),))))",
  1),
 ('joulewise/analysis_engine/inputs.py', 'resolve_floor', 'delegate',
  "('Call', (('func', ('Name', (('id', 'read_single_count_discipline'), ('ctx', ('Load', ()))))), ('args', (('Name', (('id', 'group'), "
  "('ctx', ('Load', ())))),)), ('keywords', (('keyword', (('arg', 'where'), ('value', ('Constant', (('value', 'selected group'),))))),))))",
  1),
 ('joulewise/analysis_engine/inputs.py', 'resolve_floor', 'output',
  "('keyword', (('arg', 'single_count_discipline'), ('value', ('IfExp', (('test', ('Name', (('id', 'attribution_limited'), ('ctx', "
  "('Load', ()))))), ('body', ('Call', (('func', ('Attribute', (('value', ('Name', (('id', 'single_count'), ('ctx', ('Load', ()))))), "
  "('attr', 'copy_wire'), ('ctx', ('Load', ()))))),))), ('orelse', ('Constant', ())))))))",
  2),
 ('joulewise/analysis_engine/inputs.py', 'resolve_floor', 'schema', "('Constant', (('value', 'single_count_discipline'),))", 2),
 ('joulewise/analysis_engine/inputs.py', 'resolve_floor', 'schema',
  "('Tuple', (('elts', (('Constant', (('value', 'floor_limit_class'),)), ('Constant', (('value', 'floor_source'),)), ('Constant', "
  "(('value', 'point_floor_diagnostics'),)), ('Constant', (('value', 'single_count_discipline'),)))), ('ctx', ('Load', ()))))",
  2),
 ('joulewise/analysis_engine/inputs.py', 'resolve_floor', 'typed-reader',
  "('Attribute', (('value', ('Name', (('id', 'single_count'), ('ctx', ('Load', ()))))), ('attr', 'copy_wire'), ('ctx', ('Load', ()))))",
  2),
 ('joulewise/detection_floor.py', '<grep>', 'grep', '"DisciplineV1",', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', '"DisciplineV2",', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', '"SINGLE_COUNT_DISCIPLINE_ID",', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', '"SINGLE_COUNT_DISCIPLINE_ID_V1",', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', '"SingleCountDisciplineError",', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', '"attribution_single_count_discipline",', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', '"attribution_single_count_discipline_is_canonical",', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', '"effective_clearable_effect_formula": (', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', '"planning_sizing_expression": "floor_j + claim_side_bound_j",', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', '"read_single_count_discipline",', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', '"rule_id": SINGLE_COUNT_DISCIPLINE_ID,', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', '"rule_id": SINGLE_COUNT_DISCIPLINE_ID_V1,', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', '"single_count_discipline",', 2),
 ('joulewise/detection_floor.py', '<grep>', 'grep', '"single_count_discipline": attribution_single_count_discipline(),', 3),
 ('joulewise/detection_floor.py', '<grep>', 'grep', ') -> DisciplineV1 | DisciplineV2 | None:', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', ') -> tuple[DisciplineV1 | DisciplineV2, ...]:', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', 'SINGLE_COUNT_DISCIPLINE_ID = "attribution_floor_plus_claim_side_bound.v2"', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', 'SINGLE_COUNT_DISCIPLINE_ID_V1 = "attribution_floor_plus_claim_side_bound.v1"', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', 'class DisciplineV1:', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', 'class DisciplineV2(DisciplineV1):', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', 'class SingleCountDisciplineError(ValueError):', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', 'context = f"{where}.single_count_discipline"', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', 'def attribution_single_count_discipline(', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', 'def attribution_single_count_discipline_is_canonical(value: object) -> bool:', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', 'def read_single_count_discipline(', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', 'except SingleCountDisciplineError as exc:', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', 'except SingleCountDisciplineError:', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', 'expected = attribution_single_count_discipline(rule_id)', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', 'f"{where}.{name}: single_count_discipline carriers must be an array"', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', 'f"{where}: single_count_discipline rule versions must not be mixed",', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', 'if rule_id != SINGLE_COUNT_DISCIPLINE_ID:', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', 'if rule_id == SINGLE_COUNT_DISCIPLINE_ID_V1:', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', 'raise SingleCountDisciplineError(', 3),
 ('joulewise/detection_floor.py', '<grep>', 'grep', 'raise SingleCountDisciplineError(f"{context}.rule_id: must be a string")', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', 'raise SingleCountDisciplineError(f"{context}: carrier must be an object")', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', 'raise SingleCountDisciplineError(f"{context}: must be an object")', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', 'raise SingleCountDisciplineError(f"{context}: required metadata is absent")', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', 'raise SingleCountDisciplineError(f"{context}: {exc}") from exc', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', 'raise ValueError(f"unknown single-count discipline rule_id: {rule_id!r}")', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', 'read_single_count_discipline(', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', 'read_single_count_discipline(carrier, where=where, required=True)', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', 'read_single_count_discipline(container, where=location, required=True)', 2),
 ('joulewise/detection_floor.py', '<grep>', 'grep', 'rule_id: str = SINGLE_COUNT_DISCIPLINE_ID,', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', 'value = carrier.get("single_count_discipline", _DISCIPLINE_ABSENT)', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', 'view = read_single_count_discipline(value, where=location)', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep',
  'view_type = DisciplineV1 if rule_id == SINGLE_COUNT_DISCIPLINE_ID_V1 else DisciplineV2', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', 'views: Sequence[DisciplineV1 | DisciplineV2 | None], *, where: str', 1),
 ('joulewise/detection_floor.py', '<grep>', 'grep', '{"single_count_discipline": value}, where="discipline", required=True', 1),
 ('joulewise/detection_floor.py', 'SINGLE_COUNT_DISCIPLINE_ID', 'version',
  "('Constant', (('value', 'attribution_floor_plus_claim_side_bound.v2'),))", 1),
 ('joulewise/detection_floor.py', 'SINGLE_COUNT_DISCIPLINE_ID_V1', 'version',
  "('Constant', (('value', 'attribution_floor_plus_claim_side_bound.v1'),))", 1),
 ('joulewise/detection_floor.py', '_ATTRIBUTION_LIMIT_CONTAINER_KEYS', 'api-reference',
  "('Name', (('id', '_ATTRIBUTION_LIMIT_CONTAINER_KEYS'), ('ctx', ('Store', ()))))", 1),
 ('joulewise/detection_floor.py', '_ATTRIBUTION_LIMIT_CONTAINER_KEYS', 'schema', "('Constant', (('value', 'single_count_discipline'),))",
  1),
 ('joulewise/detection_floor.py', '_ATTRIBUTION_LIMIT_CONTAINER_KEYS', 'schema',
  "('Set', (('elts', (('Constant', (('value', 'floor_source'),)), ('Constant', (('value', 'floor_limit_class'),)), ('Constant', (('value', "
  "'point_floor_diagnostics'),)), ('Constant', (('value', 'single_count_discipline'),)))),))",
  1),
 ('joulewise/detection_floor.py', '_ATTRIBUTION_LIMIT_RECORD_KEYS', 'schema', "('Constant', (('value', 'single_count_discipline'),))", 1),
 ('joulewise/detection_floor.py', '_ATTRIBUTION_LIMIT_RECORD_KEYS', 'schema',
  "('Set', (('elts', (('Constant', (('value', 'floor_source'),)), ('Constant', (('value', 'floor_limit_class'),)), ('Constant', (('value', "
  "'point_floor_diagnostic'),)), ('Constant', (('value', 'single_count_discipline'),)))),))",
  1),
 ('joulewise/detection_floor.py', '__all__', 'text-token', "('Constant', (('value', 'DisciplineV1'),))", 1),
 ('joulewise/detection_floor.py', '__all__', 'text-token', "('Constant', (('value', 'DisciplineV2'),))", 1),
 ('joulewise/detection_floor.py', '__all__', 'text-token', "('Constant', (('value', 'SINGLE_COUNT_DISCIPLINE_ID'),))", 1),
 ('joulewise/detection_floor.py', '__all__', 'text-token', "('Constant', (('value', 'SINGLE_COUNT_DISCIPLINE_ID_V1'),))", 1),
 ('joulewise/detection_floor.py', '__all__', 'text-token', "('Constant', (('value', 'SingleCountDisciplineError'),))", 1),
 ('joulewise/detection_floor.py', '__all__', 'text-token', "('Constant', (('value', 'attribution_single_count_discipline'),))", 1),
 ('joulewise/detection_floor.py', '__all__', 'text-token', "('Constant', (('value', 'attribution_single_count_discipline_is_canonical'),))",
  1),
 ('joulewise/detection_floor.py', '__all__', 'text-token', "('Constant', (('value', 'read_single_count_discipline'),))", 1),
 ('joulewise/detection_floor.py', '_add_attribution_limit_metadata', 'api-reference',
  "('Name', (('id', 'attribution_single_count_discipline'), ('ctx', ('Load', ()))))", 1),
 ('joulewise/detection_floor.py', '_add_attribution_limit_metadata', 'delegate',
  "('Call', (('func', ('Name', (('id', 'attribution_single_count_discipline'), ('ctx', ('Load', ()))))),))", 1),
 ('joulewise/detection_floor.py', '_add_attribution_limit_metadata', 'emitter',
  "('Call', (('func', ('Name', (('id', 'attribution_single_count_discipline'), ('ctx', ('Load', ()))))),))", 1),
 ('joulewise/detection_floor.py', '_add_attribution_limit_metadata', 'emitter', "('Constant', (('value', 'single_count_discipline'),))", 1),
 ('joulewise/detection_floor.py', '_validate_cell', 'api-reference',
  "('Name', (('id', '_ATTRIBUTION_LIMIT_CONTAINER_KEYS'), ('ctx', ('Load', ()))))", 3),
 ('joulewise/detection_floor.py', '_validate_transport_group', 'api-reference',
  "('Name', (('id', '_ATTRIBUTION_LIMIT_CONTAINER_KEYS'), ('ctx', ('Load', ()))))", 3),
 ('joulewise/detection_floor.py', 'attribution_single_count_discipline', 'canonical-emitter',
  "('FunctionDef', (('name', 'attribution_single_count_discipline'), ('args', ('arguments', (('args', (('arg', (('arg', 'rule_id'), "
  "('annotation', ('Name', (('id', 'str'), ('ctx', ('Load', ()))))))),)), ('defaults', (('Name', (('id', 'SINGLE_COUNT_DISCIPLINE_ID'), "
  "('ctx', ('Load', ())))),))))), ('body', (('Expr', (('value', ('Constant', (('value', 'Return the exact canonical object for a supported "
  "rule version.'),))),)), ('If', (('test', ('Compare', (('left', ('Name', (('id', 'rule_id'), ('ctx', ('Load', ()))))), ('ops', (('Eq', "
  "()),)), ('comparators', (('Name', (('id', 'SINGLE_COUNT_DISCIPLINE_ID_V1'), ('ctx', ('Load', ())))),))))), ('body', (('Return', "
  "(('value', ('Dict', (('keys', (('Constant', (('value', 'rule_id'),)), ('Constant', (('value', 'effective_clearable_effect_formula'),)), "
  "('Constant', (('value', 'floor_role'),)), ('Constant', (('value', 'claim_side_bound_role'),)), ('Constant', (('value', "
  "'claim_side_bound_source'),)), ('Constant', (('value', 'both_terms_required'),)), ('Constant', (('value', "
  "'apparent_double_count_removal_forbidden'),)), ('Constant', (('value', 'statement'),)))), ('values', (('Name', (('id', "
  "'SINGLE_COUNT_DISCIPLINE_ID_V1'), ('ctx', ('Load', ())))), ('Constant', (('value', 'floor_j + claim_side_bound_j'),)), ('Constant', "
  "(('value', 'calibration_false_effect_bound'),)), ('Constant', (('value', 'claim_measurement_uncertainty_bound'),)), ('Name', (('id', "
  "'ATTRIBUTION_FLOOR_SOURCE'), ('ctx', ('Load', ())))), ('Constant', (('value', True),)), ('Constant', (('value', True),)), ('Constant', "
  "(('value', 'effective clearable effect = floor + claim-side bound; neither term may be removed as an apparent double "
  "count'),))))))),)),)))), ('If', (('test', ('Compare', (('left', ('Name', (('id', 'rule_id'), ('ctx', ('Load', ()))))), ('ops', "
  "(('NotEq', ()),)), ('comparators', (('Name', (('id', 'SINGLE_COUNT_DISCIPLINE_ID'), ('ctx', ('Load', ())))),))))), ('body', (('Raise', "
  "(('exc', ('Call', (('func', ('Name', (('id', 'ValueError'), ('ctx', ('Load', ()))))), ('args', (('JoinedStr', (('values', (('Constant', "
  "(('value', 'unknown single-count discipline rule_id: '),)), ('FormattedValue', (('value', ('Name', (('id', 'rule_id'), ('ctx', ('Load', "
  "()))))), ('conversion', 114))))),)),))))),)),)))), ('Return', (('value', ('Dict', (('keys', (('Constant', (('value', 'rule_id'),)), "
  "('Constant', (('value', 'planning_sizing_expression'),)), ('Constant', (('value', 'floor_role'),)), ('Constant', (('value', "
  "'claim_side_bound_role'),)), ('Constant', (('value', 'claim_side_bound_source'),)), ('Constant', (('value', 'both_terms_required'),)), "
  "('Constant', (('value', 'apparent_double_count_removal_forbidden'),)), ('Constant', (('value', 'gating'),)), ('Constant', (('value', "
  "'role'),)), ('Constant', (('value', 'not_an_acceptance_gate'),)), ('Constant', (('value', 'note'),)))), ('values', (('Name', (('id', "
  "'SINGLE_COUNT_DISCIPLINE_ID'), ('ctx', ('Load', ())))), ('Constant', (('value', 'floor_j + claim_side_bound_j'),)), ('Constant', "
  "(('value', 'calibration_false_effect_bound'),)), ('Constant', (('value', 'claim_measurement_uncertainty_bound'),)), ('Name', (('id', "
  "'ATTRIBUTION_FLOOR_SOURCE'), ('ctx', ('Load', ())))), ('Constant', (('value', True),)), ('Constant', (('value', True),)), ('Constant', "
  "(('value', False),)), ('Constant', (('value', 'prospective_sizing_diagnostic'),)), ('Constant', (('value', True),)), ('Constant', "
  "(('value', 'The implemented rule is |estimate| > F and zero-exclusion by both intervals, plus the registered multiplicity "
  "adjustment and evidence/eligibility requirements; for symmetric intervals the first two reduce to "
  "|estimate| > max(F, h+B), actual endpoints govern otherwise.'),))))))),)))), ('returns', ('Subscript', (('value', ('Name', (('id', "
  "'dict'), ('ctx', ('Load', ()))))), ('slice', ('Tuple', (('elts', (('Name', (('id', 'str'), ('ctx', ('Load', ())))), ('Name', (('id', "
  "'object'), ('ctx', ('Load', ())))))), ('ctx', ('Load', ()))))), ('ctx', ('Load', ())))))))",
  1),
 ('joulewise/detection_floor.py', 'attribution_single_count_discipline', 'text-token',
  "('Constant', (('value', 'effective_clearable_effect_formula'),))", 1),
 ('joulewise/detection_floor.py', 'attribution_single_count_discipline', 'text-token',
  "('Constant', (('value', 'planning_sizing_expression'),))", 1),
 ('joulewise/detection_floor.py', 'attribution_single_count_discipline', 'text-token',
  "('Constant', (('value', 'unknown single-count discipline rule_id: '),))", 1),
 ('joulewise/detection_floor.py', 'attribution_single_count_discipline_is_canonical', 'api-reference',
  "('Name', (('id', 'read_single_count_discipline'), ('ctx', ('Load', ()))))", 1),
 ('joulewise/detection_floor.py', 'attribution_single_count_discipline_is_canonical', 'delegate',
  "('Call', (('func', ('Name', (('id', 'read_single_count_discipline'), ('ctx', ('Load', ()))))), ('args', (('Dict', (('keys', "
  "(('Constant', (('value', 'single_count_discipline'),)),)), ('values', (('Name', (('id', 'value'), ('ctx', ('Load', ())))),)))),)), "
  "('keywords', (('keyword', (('arg', 'where'), ('value', ('Constant', (('value', 'discipline'),))))), ('keyword', (('arg', 'required'), "
  "('value', ('Constant', (('value', True),)))))))))",
  1),
 ('joulewise/detection_floor.py', 'attribution_single_count_discipline_is_canonical', 'output',
  "('Constant', (('value', 'single_count_discipline'),))", 1),
 ('joulewise/detection_floor.py', 'attribution_single_count_discipline_is_canonical', 'output',
  "('Name', (('id', 'value'), ('ctx', ('Load', ()))))", 1),
 ('joulewise/detection_floor.py', 'build_floor_cell', 'api-reference',
  "('Name', (('id', 'attribution_single_count_discipline'), ('ctx', ('Load', ()))))", 1),
 ('joulewise/detection_floor.py', 'build_floor_cell', 'delegate',
  "('Call', (('func', ('Name', (('id', 'attribution_single_count_discipline'), ('ctx', ('Load', ()))))),))", 1),
 ('joulewise/detection_floor.py', 'build_floor_cell', 'emitter',
  "('Call', (('func', ('Name', (('id', 'attribution_single_count_discipline'), ('ctx', ('Load', ()))))),))", 1),
 ('joulewise/detection_floor.py', 'build_floor_cell', 'emitter', "('Constant', (('value', 'single_count_discipline'),))", 1),
 ('joulewise/detection_floor.py', 'build_transport_group', 'api-reference',
  "('Name', (('id', 'attribution_single_count_discipline'), ('ctx', ('Load', ()))))", 1),
 ('joulewise/detection_floor.py', 'build_transport_group', 'delegate',
  "('Call', (('func', ('Name', (('id', 'attribution_single_count_discipline'), ('ctx', ('Load', ()))))),))", 1),
 ('joulewise/detection_floor.py', 'build_transport_group', 'emitter',
  "('Call', (('func', ('Name', (('id', 'attribution_single_count_discipline'), ('ctx', ('Load', ()))))),))", 1),
 ('joulewise/detection_floor.py', 'build_transport_group', 'emitter', "('Constant', (('value', 'single_count_discipline'),))", 1),
 ('joulewise/detection_floor.py', 'check_single_count_cohort', 'text-token',
  "('Constant', (('value', ': single_count_discipline rule versions must not be mixed'),))", 1),
 ('joulewise/detection_floor.py', 'check_single_count_cohort', 'typed-reader',
  "('Attribute', (('value', ('Name', (('id', 'view'), ('ctx', ('Load', ()))))), ('attr', 'rule_id'), ('ctx', ('Load', ()))))", 1),
 ('joulewise/detection_floor.py', 'read_single_count_discipline', 'api-reference',
  "('Name', (('id', 'attribution_single_count_discipline'), ('ctx', ('Load', ()))))", 1),
 ('joulewise/detection_floor.py', 'read_single_count_discipline', 'delegate',
  "('Call', (('func', ('Name', (('id', 'attribution_single_count_discipline'), ('ctx', ('Load', ()))))), ('args', (('Name', (('id', "
  "'rule_id'), ('ctx', ('Load', ())))),))))",
  1),
 ('joulewise/detection_floor.py', 'read_single_count_discipline', 'key-token', "('Constant', (('value', 'single_count_discipline'),))", 1),
 ('joulewise/detection_floor.py', 'read_single_count_discipline', 'parser',
  "('Call', (('func', ('Attribute', (('value', ('Name', (('id', 'carrier'), ('ctx', ('Load', ()))))), ('attr', 'get'), ('ctx', ('Load', "
  "()))))), ('args', (('Constant', (('value', 'single_count_discipline'),)), ('Name', (('id', '_DISCIPLINE_ABSENT'), ('ctx', ('Load', "
  '()))))))))',
  1),
 ('joulewise/detection_floor.py', 'read_single_count_discipline', 'parser',
  "('Call', (('func', ('Attribute', (('value', ('Name', (('id', 'value'), ('ctx', ('Load', ()))))), ('attr', 'get'), ('ctx', ('Load', "
  "()))))), ('args', (('Constant', (('value', 'rule_id'),)),))))",
  1),
 ('joulewise/detection_floor.py', 'read_single_count_discipline', 'text-token', "('Constant', (('value', '.single_count_discipline'),))",
  1),
 ('joulewise/detection_floor.py', 'read_single_count_profile', 'api-reference',
  "('Name', (('id', 'check_single_count_cohort'), ('ctx', ('Load', ()))))", 1),
 ('joulewise/detection_floor.py', 'read_single_count_profile', 'api-reference',
  "('Name', (('id', 'read_single_count_discipline'), ('ctx', ('Load', ()))))", 3),
 ('joulewise/detection_floor.py', 'read_single_count_profile', 'delegate',
  "('Call', (('func', ('Name', (('id', 'check_single_count_cohort'), ('ctx', ('Load', ()))))), ('args', (('Name', (('id', 'views'), "
  "('ctx', ('Load', ())))),)), ('keywords', (('keyword', (('arg', 'where'), ('value', ('Name', (('id', 'where'), ('ctx', ('Load', "
  '()))))))),))))',
  1),
 ('joulewise/detection_floor.py', 'read_single_count_profile', 'delegate',
  "('Call', (('func', ('Name', (('id', 'read_single_count_discipline'), ('ctx', ('Load', ()))))), ('args', (('Name', (('id', 'carrier'), "
  "('ctx', ('Load', ())))),)), ('keywords', (('keyword', (('arg', 'where'), ('value', ('Name', (('id', 'where'), ('ctx', ('Load', "
  "()))))))), ('keyword', (('arg', 'required'), ('value', ('Constant', (('value', True),)))))))))",
  1),
 ('joulewise/detection_floor.py', 'read_single_count_profile', 'delegate',
  "('Call', (('func', ('Name', (('id', 'read_single_count_discipline'), ('ctx', ('Load', ()))))), ('args', (('Name', (('id', 'container'), "
  "('ctx', ('Load', ())))),)), ('keywords', (('keyword', (('arg', 'where'), ('value', ('Name', (('id', 'location'), ('ctx', ('Load', "
  "()))))))), ('keyword', (('arg', 'required'), ('value', ('Constant', (('value', True),)))))))))",
  2),
 ('joulewise/detection_floor.py', 'read_single_count_profile', 'text-token',
  "('Constant', (('value', ': single_count_discipline carriers must be an array'),))", 1),
 ('joulewise/detection_floor.py', 'read_single_count_profile.admit', 'api-reference',
  "('Name', (('id', 'read_single_count_discipline'), ('ctx', ('Load', ()))))", 1),
 ('joulewise/detection_floor.py', 'read_single_count_profile.admit', 'delegate',
  "('Call', (('func', ('Name', (('id', 'read_single_count_discipline'), ('ctx', ('Load', ()))))), ('args', (('Name', (('id', 'value'), "
  "('ctx', ('Load', ())))),)), ('keywords', (('keyword', (('arg', 'where'), ('value', ('Name', (('id', 'location'), ('ctx', ('Load', "
  '()))))))),))))',
  1),
 ('joulewise/detection_floor.py', 'validate_floor_artifact', 'api-reference',
  "('Name', (('id', 'read_single_count_profile'), ('ctx', ('Load', ()))))", 1),
 ('joulewise/detection_floor.py', 'validate_floor_artifact', 'delegate',
  "('Call', (('func', ('Name', (('id', 'read_single_count_profile'), ('ctx', ('Load', ()))))), ('args', (('Name', (('id', 'value'), "
  "('ctx', ('Load', ())))),)), ('keywords', (('keyword', (('arg', 'profile'), ('value', ('Constant', (('value', 'floor'),))))), "
  "('keyword', (('arg', 'where'), ('value', ('Constant', (('value', 'artifact'),)))))))))",
  1),
 ('joulewise/floor_extraction.py', '<grep>', 'grep', '"single_count_discipline",', 2),
 ('joulewise/floor_extraction.py', '<grep>', 'grep', '"single_count_discipline": (', 1),
 ('joulewise/floor_extraction.py', '<grep>', 'grep', 'attribution_single_count_discipline()', 1),
 ('joulewise/floor_extraction.py', '<grep>', 'grep', 'attribution_single_count_discipline,', 1),
 ('joulewise/floor_extraction.py', '<grep>', 'grep', 'result["single_count_discipline"] = attribution_single_count_discipline()', 1),
 ('joulewise/floor_extraction.py', '<module>', 'api-alias', "('alias', (('name', 'attribution_single_count_discipline'),))", 1),
 ('joulewise/floor_extraction.py', 'CellReport.as_row', 'api-reference',
  "('Name', (('id', 'attribution_single_count_discipline'), ('ctx', ('Load', ()))))", 1),
 ('joulewise/floor_extraction.py', 'CellReport.as_row', 'delegate',
  "('Call', (('func', ('Name', (('id', 'attribution_single_count_discipline'), ('ctx', ('Load', ()))))),))", 1),
 ('joulewise/floor_extraction.py', 'CellReport.as_row', 'emitter',
  "('Call', (('func', ('Name', (('id', 'attribution_single_count_discipline'), ('ctx', ('Load', ()))))),))", 1),
 ('joulewise/floor_extraction.py', 'CellReport.as_row', 'emitter', "('Constant', (('value', 'single_count_discipline'),))", 1),
 ('joulewise/floor_extraction.py', '_D117_MINT_CELL_OPTIONAL_KEYS', 'api-reference',
  "('Name', (('id', '_D117_MINT_CELL_OPTIONAL_KEYS'), ('ctx', ('Store', ()))))", 1),
 ('joulewise/floor_extraction.py', '_D117_MINT_CELL_OPTIONAL_KEYS', 'vocabulary', "('Constant', (('value', 'single_count_discipline'),))",
  1),
 ('joulewise/floor_extraction.py', '_D117_MINT_REPORT_OPTIONAL_KEYS', 'api-reference',
  "('Name', (('id', '_D117_MINT_REPORT_OPTIONAL_KEYS'), ('ctx', ('Store', ()))))", 1),
 ('joulewise/floor_extraction.py', '_D117_MINT_REPORT_OPTIONAL_KEYS', 'vocabulary', "('Constant', (('value', 'single_count_discipline'),))",
  1),
 ('joulewise/floor_extraction.py', 'extract_cells', 'api-reference',
  "('Name', (('id', 'attribution_single_count_discipline'), ('ctx', ('Load', ()))))", 1),
 ('joulewise/floor_extraction.py', 'extract_cells', 'delegate',
  "('Call', (('func', ('Name', (('id', 'attribution_single_count_discipline'), ('ctx', ('Load', ()))))),))", 1),
 ('joulewise/floor_extraction.py', 'extract_cells', 'emitter',
  "('Assign', (('targets', (('Subscript', (('value', ('Name', (('id', 'result'), ('ctx', ('Load', ()))))), ('slice', ('Constant', "
  "(('value', 'single_count_discipline'),))), ('ctx', ('Store', ())))),)), ('value', ('Call', (('func', ('Name', (('id', "
  "'attribution_single_count_discipline'), ('ctx', ('Load', ()))))),)))))",
  1),
 ('joulewise/floor_extraction.py', 'extract_cells', 'key-token', "('Constant', (('value', 'single_count_discipline'),))", 1),
 ('joulewise/floor_extraction.py', 'validate_d117_mint_consumption_report', 'api-reference',
  "('Name', (('id', '_D117_MINT_CELL_OPTIONAL_KEYS'), ('ctx', ('Load', ()))))", 1),
 ('joulewise/floor_extraction.py', 'validate_d117_mint_consumption_report', 'api-reference',
  "('Name', (('id', '_D117_MINT_REPORT_OPTIONAL_KEYS'), ('ctx', ('Load', ()))))", 1),
 ('scripts/mint_floor_artifact.py', '<grep>', 'grep', 'DisciplineV2,', 1),
 ('scripts/mint_floor_artifact.py', '<grep>', 'grep', 'SingleCountDisciplineError,', 1),
 ('scripts/mint_floor_artifact.py', '<grep>', 'grep', 'except SingleCountDisciplineError as exc:', 1),
 ('scripts/mint_floor_artifact.py', '<grep>', 'grep', 'f"Formula: {expected[\'effective_clearable_effect_formula\']}; "', 1),
 ('scripts/mint_floor_artifact.py', '<grep>', 'grep', 'f"Planning sizing expression: {expected[\'planning_sizing_expression\']}; "', 1),
 ('scripts/mint_floor_artifact.py', '<grep>', 'grep', 'if isinstance(view, DisciplineV2):', 1),
 ('scripts/mint_floor_artifact.py', '<grep>', 'grep', 'raise MintError("artifact does not carry a single-count discipline object")', 1),
 ('scripts/mint_floor_artifact.py', '<grep>', 'grep',
  'raise MintError(f"artifact mixes single-count discipline rule versions: {exc}") from exc', 1),
 ('scripts/mint_floor_artifact.py', '<grep>', 'grep',
  'raise MintError(f"artifact single-count discipline is not canonical: {exc}") from exc', 1),
 ('scripts/mint_floor_artifact.py', '<module>', 'api-alias', "('alias', (('name', 'DisciplineV2'),))", 1),
 ('scripts/mint_floor_artifact.py', '<module>', 'api-alias', "('alias', (('name', 'SingleCountDisciplineError'),))", 1),
 ('scripts/mint_floor_artifact.py', '<module>', 'api-alias', "('alias', (('name', 'read_single_count_profile'),))", 1),
 ('scripts/mint_floor_artifact.py', '_read_mint_disciplines', 'api-reference',
  "('Name', (('id', 'read_single_count_profile'), ('ctx', ('Load', ()))))", 1),
 ('scripts/mint_floor_artifact.py', '_read_mint_disciplines', 'delegate',
  "('Call', (('func', ('Name', (('id', 'read_single_count_profile'), ('ctx', ('Load', ()))))), ('args', (('Name', (('id', 'carrier'), "
  "('ctx', ('Load', ())))),)), ('keywords', (('keyword', (('arg', 'profile'), ('value', ('Name', (('id', 'profile'), ('ctx', ('Load', "
  "()))))))), ('keyword', (('arg', 'where'), ('value', ('Constant', (('value', 'artifact'),)))))))))",
  1),
 ('scripts/mint_floor_artifact.py', '_read_mint_disciplines', 'text-token',
  "('Constant', (('value', 'artifact mixes single-count discipline rule versions: '),))", 1),
 ('scripts/mint_floor_artifact.py', '_read_mint_disciplines', 'text-token',
  "('Constant', (('value', 'artifact single-count discipline is not canonical: '),))", 1),
 ('scripts/mint_floor_artifact.py', '_target_report_cell', 'api-reference',
  "('Name', (('id', '_read_mint_disciplines'), ('ctx', ('Load', ()))))", 1),
 ('scripts/mint_floor_artifact.py', '_target_report_cell', 'delegate',
  "('Call', (('func', ('Name', (('id', '_read_mint_disciplines'), ('ctx', ('Load', ()))))), ('args', (('Name', (('id', 'report'), ('ctx', "
  "('Load', ())))),)), ('keywords', (('keyword', (('arg', 'profile'), ('value', ('Constant', (('value', 'extraction'),))))),))))",
  1),
 ('scripts/mint_floor_artifact.py', 'mint_authenticated_artifact', 'api-reference',
  "('Name', (('id', '_read_mint_disciplines'), ('ctx', ('Load', ()))))", 1),
 ('scripts/mint_floor_artifact.py', 'mint_authenticated_artifact', 'delegate',
  "('Call', (('func', ('Name', (('id', '_read_mint_disciplines'), ('ctx', ('Load', ()))))), ('args', (('Attribute', (('value', ('Name', "
  "(('id', 'component'), ('ctx', ('Load', ()))))), ('attr', 'report'), ('ctx', ('Load', ())))),)), ('keywords', (('keyword', (('arg', "
  "'profile'), ('value', ('Constant', (('value', 'extraction'),))))),))))",
  1),
 ('scripts/mint_floor_artifact.py', 'mint_authenticated_artifact', 'delegate',
  "('Call', (('func', ('Name', (('id', 'validate_floor_artifact'), ('ctx', ('Load', ()))))), ('args', (('Name', (('id', 'artifact'), "
  "('ctx', ('Load', ())))),))))",
  1),
 ('scripts/mint_floor_artifact.py', 'mint_floor_artifact', 'delegate',
  "('Call', (('func', ('Name', (('id', 'write_outputs_exclusive'), ('ctx', ('Load', ()))))), ('args', (('Name', (('id', 'artifact'), "
  "('ctx', ('Load', ())))), ('Name', (('id', 'floor_path'), ('ctx', ('Load', ())))), ('Name', (('id', 'statement_path'), ('ctx', ('Load', "
  '()))))))))',
  1),
 ('scripts/mint_floor_artifact.py', 'render_single_count_statement', 'api-reference',
  "('Name', (('id', '_read_mint_disciplines'), ('ctx', ('Load', ()))))", 1),
 ('scripts/mint_floor_artifact.py', 'render_single_count_statement', 'delegate',
  "('Call', (('func', ('Name', (('id', '_read_mint_disciplines'), ('ctx', ('Load', ()))))), ('args', (('Name', (('id', 'artifact'), "
  "('ctx', ('Load', ())))),)), ('keywords', (('keyword', (('arg', 'profile'), ('value', ('Name', (('id', 'profile'), ('ctx', ('Load', "
  '()))))))),))))',
  1),
 ('scripts/mint_floor_artifact.py', 'render_single_count_statement', 'text-token',
  "('Constant', (('value', 'artifact does not carry a single-count discipline object'),))", 1),
 ('scripts/mint_floor_artifact.py', 'render_single_count_statement', 'text-token',
  "('Constant', (('value', 'effective_clearable_effect_formula'),))", 1),
 ('scripts/mint_floor_artifact.py', 'render_single_count_statement', 'text-token',
  "('Constant', (('value', 'planning_sizing_expression'),))", 1),
 ('scripts/mint_floor_artifact.py', 'render_single_count_statement', 'typed-reader',
  "('Attribute', (('value', ('Name', (('id', 'view'), ('ctx', ('Load', ()))))), ('attr', 'copy_wire'), ('ctx', ('Load', ()))))", 1),
 ('scripts/mint_floor_artifact.py', 'render_single_count_statement', 'typed-reader',
  "('Subscript', (('value', ('Name', (('id', 'expected'), ('ctx', ('Load', ()))))), ('slice', ('Constant', (('value', "
  "'effective_clearable_effect_formula'),))), ('ctx', ('Load', ()))))",
  1),
 ('scripts/mint_floor_artifact.py', 'render_single_count_statement', 'typed-reader',
  "('Subscript', (('value', ('Name', (('id', 'expected'), ('ctx', ('Load', ()))))), ('slice', ('Constant', (('value', "
  "'planning_sizing_expression'),))), ('ctx', ('Load', ()))))",
  1),
 ('scripts/mint_floor_artifact.py', 'write_outputs_exclusive', 'api-reference',
  "('Name', (('id', 'render_single_count_statement'), ('ctx', ('Load', ()))))", 1),
 ('scripts/mint_floor_artifact.py', 'write_outputs_exclusive', 'delegate',
  "('Call', (('func', ('Name', (('id', 'render_single_count_statement'), ('ctx', ('Load', ()))))), ('args', (('Name', (('id', 'artifact'), "
  "('ctx', ('Load', ())))),))))",
  1),
 ('scripts/mint_floor_artifact_generalized.py', '<grep>', 'grep', 'except detection_floor.SingleCountDisciplineError as exc:', 2),
 ('scripts/mint_floor_artifact_generalized.py', '_mint_multi_cell_floor_artifact_active', 'delegate',
  "('Call', (('func', ('Attribute', (('value', ('Name', (('id', 'output_core'), ('ctx', ('Load', ()))))), ('attr', "
  "'write_outputs_exclusive'), ('ctx', ('Load', ()))))), ('args', (('Name', (('id', 'artifact'), ('ctx', ('Load', ())))), ('Name', (('id', "
  "'floor_path'), ('ctx', ('Load', ())))), ('Name', (('id', 'statement_path'), ('ctx', ('Load', ()))))))))",
  1),
 ('scripts/mint_floor_artifact_generalized.py', '_mint_multi_cell_floor_artifact_active', 'delegate',
  "('Call', (('func', ('Name', (('id', '_write_v2_artifact_outputs'), ('ctx', ('Load', ()))))), ('keywords', (('keyword', (('arg', "
  "'output_core'), ('value', ('Name', (('id', 'output_core'), ('ctx', ('Load', ()))))))), ('keyword', (('arg', 'artifact'), ('value', "
  "('Name', (('id', 'artifact'), ('ctx', ('Load', ()))))))), ('keyword', (('arg', 'sidecar'), ('value', ('Name', (('id', 'sidecar'), "
  "('ctx', ('Load', ()))))))), ('keyword', (('arg', 'floor_path'), ('value', ('Name', (('id', 'floor_path'), ('ctx', ('Load', ()))))))), "
  "('keyword', (('arg', 'statement_path'), ('value', ('Name', (('id', 'statement_path'), ('ctx', ('Load', ()))))))), ('keyword', (('arg', "
  "'d165_replay_out'), ('value', ('Name', (('id', 'd165_replay_out'), ('ctx', ('Load', ())))))))))))",
  1),
 ('scripts/mint_floor_artifact_generalized.py', '_pre_admit_legacy_report', 'delegate',
  "('Call', (('func', ('Attribute', (('value', ('Name', (('id', 'detection_floor'), ('ctx', ('Load', ()))))), ('attr', "
  "'read_single_count_profile'), ('ctx', ('Load', ()))))), ('args', (('Name', (('id', 'value'), ('ctx', ('Load', ())))),)), ('keywords', "
  "(('keyword', (('arg', 'profile'), ('value', ('Constant', (('value', 'extraction'),))))), ('keyword', (('arg', 'where'), ('value', "
  "('Name', (('id', 'label'), ('ctx', ('Load', ())))))))))))",
  1),
 ('scripts/mint_floor_artifact_generalized.py', '_v2_gate_postcollection', 'delegate',
  "('Call', (('func', ('Attribute', (('value', ('Name', (('id', 'detection_floor'), ('ctx', ('Load', ()))))), ('attr', "
  "'read_single_count_profile'), ('ctx', ('Load', ()))))), ('args', (('Attribute', (('value', ('Name', (('id', 'component'), ('ctx', "
  "('Load', ()))))), ('attr', 'report'), ('ctx', ('Load', ())))),)), ('keywords', (('keyword', (('arg', 'profile'), ('value', ('Constant', "
  "(('value', 'extraction'),))))), ('keyword', (('arg', 'where'), ('value', ('Constant', (('value', 'extraction report'),)))))))))",
  1),
 ('scripts/mint_floor_artifact_generalized.py', '_write_v2_artifact_outputs', 'delegate',
  "('Call', (('func', ('Attribute', (('value', ('Name', (('id', 'output_core'), ('ctx', ('Load', ()))))), ('attr', "
  "'render_single_count_statement'), ('ctx', ('Load', ()))))), ('args', (('Name', (('id', 'artifact'), ('ctx', ('Load', ())))),))))",
  1),
 ('scripts/mint_floor_artifact_generalized.py', 'mint_authenticated_artifact', 'delegate',
  "('Call', (('func', ('Attribute', (('value', ('Name', (('id', 'core'), ('ctx', ('Load', ()))))), ('attr', "
  "'mint_authenticated_artifact'), ('ctx', ('Load', ()))))), ('keywords', (('keyword', (('arg', 'artifact_id'), ('value', ('Name', (('id', "
  "'artifact_id'), ('ctx', ('Load', ()))))))), ('keyword', (('arg', 'plan'), ('value', ('Name', (('id', 'plan'), ('ctx', ('Load', "
  "()))))))), ('keyword', (('arg', 'plan_sha256'), ('value', ('Name', (('id', 'plan_sha256'), ('ctx', ('Load', ()))))))), ('keyword', "
  "(('arg', 'calibration_plan_relative_path'), ('value', ('Name', (('id', 'calibration_plan_relative_path'), ('ctx', ('Load', ()))))))), "
  "('keyword', (('arg', 'absolute'), ('value', ('Name', (('id', 'absolute'), ('ctx', ('Load', ()))))))), ('keyword', (('arg', "
  "'comparative'), ('value', ('Name', (('id', 'comparative'), ('ctx', ('Load', ()))))))), ('keyword', (('arg', 'project_commit'), "
  "('value', ('Name', (('id', 'project_commit'), ('ctx', ('Load', ()))))))), ('keyword', (('arg', 'project_tree_state'), ('value', "
  "('Name', (('id', 'project_tree_state'), ('ctx', ('Load', ())))))))))))",
  1),
 ('scripts/mint_floor_artifact_generalized.py', 'mint_floor_artifact', 'delegate',
  "('Call', (('func', ('Attribute', (('value', ('Name', (('id', 'core'), ('ctx', ('Load', ()))))), ('attr', 'mint_floor_artifact'), "
  "('ctx', ('Load', ()))))), ('keywords', (('keyword', (('arg', 'artifact_id'), ('value', ('Name', (('id', 'artifact_id'), ('ctx', "
  "('Load', ()))))))), ('keyword', (('arg', 'floor_path'), ('value', ('Name', (('id', 'floor_path'), ('ctx', ('Load', ()))))))), "
  "('keyword', (('arg', 'statement_path'), ('value', ('Name', (('id', 'statement_path'), ('ctx', ('Load', ()))))))), ('keyword', (('arg', "
  "'calibration_plan_path'), ('value', ('Name', (('id', 'calibration_plan_path'), ('ctx', ('Load', ()))))))), ('keyword', (('arg', "
  "'calibration_plan_relative_path'), ('value', ('Name', (('id', 'calibration_plan_relative_path'), ('ctx', ('Load', ()))))))), "
  "('keyword', (('arg', 'absolute_paths'), ('value', ('Call', (('func', ('Attribute', (('value', ('Name', (('id', 'core'), ('ctx', "
  "('Load', ()))))), ('attr', 'ComponentPaths'), ('ctx', ('Load', ()))))), ('keywords', (('keyword', (('arg', 'evidence_root_id'), "
  "('value', ('Attribute', (('value', ('Attribute', (('value', ('Name', (('id', 'pinset'), ('ctx', ('Load', ()))))), ('attr', 'absolute'), "
  "('ctx', ('Load', ()))))), ('attr', 'evidence_root_id'), ('ctx', ('Load', ()))))))), ('keyword', (('arg', 'evidence_root'), ('value', "
  "('Attribute', (('value', ('Name', (('id', 'absolute_inputs'), ('ctx', ('Load', ()))))), ('attr', 'evidence_root'), ('ctx', ('Load', "
  "()))))))), ('keyword', (('arg', 'report_path'), ('value', ('Attribute', (('value', ('Name', (('id', 'absolute_inputs'), ('ctx', "
  "('Load', ()))))), ('attr', 'report_path'), ('ctx', ('Load', ()))))))), ('keyword', (('arg', 'spec_path'), ('value', ('Attribute', "
  "(('value', ('Name', (('id', 'absolute_inputs'), ('ctx', ('Load', ()))))), ('attr', 'spec_path'), ('ctx', ('Load', ()))))))), "
  "('keyword', (('arg', 'order_manifest_path'), ('value', ('Attribute', (('value', ('Name', (('id', 'absolute_inputs'), ('ctx', ('Load', "
  "()))))), ('attr', 'order_manifest_path'), ('ctx', ('Load', ()))))))), ('keyword', (('arg', 'calibration_cell_id'), ('value', "
  "('Attribute', (('value', ('Attribute', (('value', ('Name', (('id', 'pinset'), ('ctx', ('Load', ()))))), ('attr', 'absolute'), ('ctx', "
  "('Load', ()))))), ('attr', 'calibration_cell_id'), ('ctx', ('Load', ()))))))), ('keyword', (('arg', 'expected_kind'), ('value', "
  "('Constant', (('value', 'absolute'),)))))))))))), ('keyword', (('arg', 'comparative_paths'), ('value', ('Call', (('func', ('Attribute', "
  "(('value', ('Name', (('id', 'core'), ('ctx', ('Load', ()))))), ('attr', 'ComponentPaths'), ('ctx', ('Load', ()))))), ('keywords', "
  "(('keyword', (('arg', 'evidence_root_id'), ('value', ('Attribute', (('value', ('Attribute', (('value', ('Name', (('id', 'pinset'), "
  "('ctx', ('Load', ()))))), ('attr', 'comparative'), ('ctx', ('Load', ()))))), ('attr', 'evidence_root_id'), ('ctx', ('Load', ()))))))), "
  "('keyword', (('arg', 'evidence_root'), ('value', ('Attribute', (('value', ('Name', (('id', 'comparative_inputs'), ('ctx', ('Load', "
  "()))))), ('attr', 'evidence_root'), ('ctx', ('Load', ()))))))), ('keyword', (('arg', 'report_path'), ('value', ('Attribute', (('value', "
  "('Name', (('id', 'comparative_inputs'), ('ctx', ('Load', ()))))), ('attr', 'report_path'), ('ctx', ('Load', ()))))))), ('keyword', "
  "(('arg', 'spec_path'), ('value', ('Attribute', (('value', ('Name', (('id', 'comparative_inputs'), ('ctx', ('Load', ()))))), ('attr', "
  "'spec_path'), ('ctx', ('Load', ()))))))), ('keyword', (('arg', 'order_manifest_path'), ('value', ('Attribute', (('value', ('Name', "
  "(('id', 'comparative_inputs'), ('ctx', ('Load', ()))))), ('attr', 'order_manifest_path'), ('ctx', ('Load', ()))))))), ('keyword', "
  "(('arg', 'calibration_cell_id'), ('value', ('Attribute', (('value', ('Attribute', (('value', ('Name', (('id', 'pinset'), ('ctx', "
  "('Load', ()))))), ('attr', 'comparative'), ('ctx', ('Load', ()))))), ('attr', 'calibration_cell_id'), ('ctx', ('Load', ()))))))), "
  "('keyword', (('arg', 'expected_kind'), ('value', ('Constant', (('value', 'comparative'),)))))))))))), ('keyword', (('arg', "
  "'project_commit'), ('value', ('Name', (('id', 'project_commit'), ('ctx', ('Load', ()))))))), ('keyword', (('arg', "
  "'project_tree_state'), ('value', ('Name', (('id', 'project_tree_state'), ('ctx', ('Load', ()))))))), ('keyword', (('arg', "
  "'strict_validator'), ('value', ('Name', (('id', 'strict_validator'), ('ctx', ('Load', ()))))))), ('keyword', (('arg', "
  "'consumption_semantics_id'), ('value', ('Name', (('id', 'consumption_semantics_id'), ('ctx', ('Load', ())))))))))))",
  1),
 ('scripts/mint_floor_artifact_generalized.py', 'validate_floor_artifact', 'delegate',
  "('Call', (('func', ('Attribute', (('value', ('Name', (('id', 'core'), ('ctx', ('Load', ()))))), ('attr', 'validate_floor_artifact'), "
  "('ctx', ('Load', ()))))), ('args', (('Name', (('id', 'artifact'), ('ctx', ('Load', ())))),))))",
  1),
 ('scripts/mint_floor_artifact_generalized.py', 'validate_floor_artifact', 'delegate',
  "('Call', (('func', ('Attribute', (('value', ('Name', (('id', 'core'), ('ctx', ('Load', ()))))), ('attr', 'validate_floor_artifact'), "
  "('ctx', ('Load', ()))))), ('args', (('Name', (('id', 'artifact'), ('ctx', ('Load', ())))),)), ('keywords', (('keyword', (('arg', "
  "'pinset_path'), ('value', ('Name', (('id', 'pinset_path'), ('ctx', ('Load', ()))))))), ('keyword', (('arg', 'expected_pinset_sha256'), "
  "('value', ('Name', (('id', 'pinset_sha256'), ('ctx', ('Load', ())))))))))))",
  1)]


# Reviewed reusable-helper/import inventory added by counter-review 45 S3.
MANIFEST += [
 ('tests/test_analysis_claims.py', '<grep>', 'grep',
  'SINGLE_COUNT_DISCIPLINE_ID_V1,', 1),
 ('tests/test_analysis_claims.py', '<grep>', 'grep',
  'attribution_single_count_discipline,', 1),
 ('tests/test_analysis_claims.py', '<module>', 'api-alias',
  "('alias', (('name', 'SINGLE_COUNT_DISCIPLINE_ID_V1'),))", 1),
 ('tests/test_analysis_claims.py', '<module>', 'api-alias',
  "('alias', (('name', 'attribution_single_count_discipline'),))", 1),
 ('tests/test_analysis_integration.py', '<grep>', 'grep',
  'attribution_single_count_discipline,', 1),
 ('tests/test_analysis_integration.py', '<module>', 'api-alias',
  "('alias', (('name', 'attribution_single_count_discipline'),))", 1),
 ('tests/test_detection_floor.py', '<grep>', 'grep',
  'SINGLE_COUNT_DISCIPLINE_ID,', 1),
 ('tests/test_detection_floor.py', '<grep>', 'grep',
  'SINGLE_COUNT_DISCIPLINE_ID_V1,', 1),
 ('tests/test_detection_floor.py', '<grep>', 'grep',
  'attribution_single_count_discipline,', 1),
 ('tests/test_detection_floor.py', '<module>', 'api-alias',
  "('alias', (('name', 'SINGLE_COUNT_DISCIPLINE_ID'),))", 1),
 ('tests/test_detection_floor.py', '<module>', 'api-alias',
  "('alias', (('name', 'SINGLE_COUNT_DISCIPLINE_ID_V1'),))", 1),
 ('tests/test_detection_floor.py', '<module>', 'api-alias',
  "('alias', (('name', 'attribution_single_count_discipline'),))", 1),
 ('tests/test_floor_extraction.py', '<grep>', 'grep',
  'attribution_single_count_discipline,', 1),
 ('tests/test_floor_extraction.py', '<module>', 'api-alias',
  "('alias', (('name', 'attribution_single_count_discipline'),))", 1),
 ('tests/test_mint_floor_artifact.py', '<grep>', 'grep',
  'SINGLE_COUNT_DISCIPLINE_ID_V1,', 1),
 ('tests/test_mint_floor_artifact.py', '<grep>', 'grep',
  'attribution_single_count_discipline,', 1),
 ('tests/test_mint_floor_artifact.py', '<module>', 'api-alias',
  "('alias', (('name', 'SINGLE_COUNT_DISCIPLINE_ID_V1'),))", 1),
 ('tests/test_mint_floor_artifact.py', '<module>', 'api-alias',
  "('alias', (('name', 'attribution_single_count_discipline'),))", 1),
 ('tests/test_single_count_discipline_matrix.py', '<grep>', 'grep',
  '"single_count_discipline",', 1),
 ('tests/test_single_count_discipline_matrix.py', '<grep>', 'grep',
  'VERSIONS = (df.SINGLE_COUNT_DISCIPLINE_ID_V1, df.SINGLE_COUNT_DISCIPLINE_ID)', 1),
 ('tests/test_single_count_discipline_matrix.py', '<grep>', 'grep',
  'canonical = df.attribution_single_count_discipline(rule_id)', 1),
 ('tests/test_single_count_discipline_matrix.py', '<grep>', 'grep',
  'carrier["single_count_discipline"] = copy.deepcopy(bad)', 1),
 ('tests/test_single_count_discipline_matrix.py', '<grep>', 'grep',
  'del carrier["single_count_discipline"]', 1),
 ('tests/test_single_count_discipline_matrix.py', '<grep>', 'grep',
  'if key == "single_count_discipline":', 1),
 ('tests/test_single_count_discipline_matrix.py', '<grep>', 'grep',
  'node[key] = df.attribution_single_count_discipline(rule_id)', 1),
 ('tests/test_single_count_discipline_matrix.py', '<grep>', 'grep',
  'other = df.attribution_single_count_discipline(next(v for v in VERSIONS if v != rule_id))', 1),
 ('tests/test_single_count_discipline_matrix.py', '<grep>', 'grep',
  'single_count_discipline=df.attribution_single_count_discipline(rule_id),', 1),
 ('tests/test_single_count_discipline_matrix.py', 'claim_artifact', 'key-token',
  "('Constant', (('value', 'single_count_discipline'),))", 1),
 ('tests/test_single_count_discipline_matrix.py', 'corrupt', 'key-token',
  "('Constant', (('value', 'single_count_discipline'),))", 2),
 ('tests/test_single_count_discipline_matrix.py', 'corrupt', 'output',
  ("('Assign', (('targets', (('Subscript', (('value', ('Name', (('id', 'carrier'), ('ctx', ('Load', ()))))), ('slice', "
   "('Constant', (('value', 'single_count_discipline'),))), ('ctx', ('Store', ())))),)), ('value', ('Call', (('func', "
   "('Attribute', (('value', ('Name', (('id', 'copy'), ('ctx', ('Load', ()))))), ('attr', 'deepcopy'), ('ctx', ('Load', "
   "()))))), ('args', (('Name', (('id', 'bad'), ('ctx', ('Load', ())))),)))))))"), 1),
 ('tests/test_single_count_discipline_matrix.py', 'resolution', 'delegate',
  ("('Call', (('func', ('Attribute', (('value', ('Name', (('id', 'df'), ('ctx', ('Load', ()))))), ('attr', "
   "'attribution_single_count_discipline'), ('ctx', ('Load', ()))))), ('args', (('Name', (('id', 'rule_id'), ('ctx', "
   "('Load', ())))),))))"), 1),
 ('tests/test_single_count_discipline_matrix.py', 'resolution', 'output',
  ("('keyword', (('arg', 'single_count_discipline'), ('value', ('Call', (('func', ('Attribute', (('value', ('Name', (('id', "
   "'df'), ('ctx', ('Load', ()))))), ('attr', 'attribution_single_count_discipline'), ('ctx', ('Load', ()))))), ('args', "
   "(('Name', (('id', 'rule_id'), ('ctx', ('Load', ())))),)))))))"), 1),
 ('tests/test_single_count_discipline_matrix.py', 'shapes', 'delegate',
  ("('Call', (('func', ('Attribute', (('value', ('Name', (('id', 'df'), ('ctx', ('Load', ()))))), ('attr', "
   "'attribution_single_count_discipline'), ('ctx', ('Load', ()))))), ('args', (('Call', (('func', ('Name', (('id', 'next'), "
   "('ctx', ('Load', ()))))), ('args', (('GeneratorExp', (('elt', ('Name', (('id', 'v'), ('ctx', ('Load', ()))))), "
   "('generators', (('comprehension', (('target', ('Name', (('id', 'v'), ('ctx', ('Store', ()))))), ('iter', ('Name', "
   "(('id', 'VERSIONS'), ('ctx', ('Load', ()))))), ('ifs', (('Compare', (('left', ('Name', (('id', 'v'), ('ctx', ('Load', "
   "()))))), ('ops', (('NotEq', ()),)), ('comparators', (('Name', (('id', 'rule_id'), ('ctx', ('Load', ())))),)))),)), "
   "('is_async', 0))),)))),)))),))))"), 1),
 ('tests/test_single_count_discipline_matrix.py', 'shapes', 'delegate',
  ("('Call', (('func', ('Attribute', (('value', ('Name', (('id', 'df'), ('ctx', ('Load', ()))))), ('attr', "
   "'attribution_single_count_discipline'), ('ctx', ('Load', ()))))), ('args', (('Name', (('id', 'rule_id'), ('ctx', "
   "('Load', ())))),))))"), 1),
 ('tests/test_single_count_discipline_matrix.py', 'versioned.visit', 'delegate',
  ("('Call', (('func', ('Attribute', (('value', ('Name', (('id', 'df'), ('ctx', ('Load', ()))))), ('attr', "
   "'attribution_single_count_discipline'), ('ctx', ('Load', ()))))), ('args', (('Name', (('id', 'rule_id'), ('ctx', "
   "('Load', ())))),))))"), 1),
 ('tests/test_single_count_discipline_matrix.py', 'versioned.visit', 'key-token',
  "('Constant', (('value', 'single_count_discipline'),))", 1)]

class SingleCountCensusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_map = sources()

    def test_closed_inventory_and_no_raw_bypasses(self):
        assert_inventory(self.source_map)

    def test_in_memory_mutations_are_detected(self):
        path = "joulewise/analysis_engine/claims.py"
        mutations = {
            "new_reader": '\ndef rogue(carrier):\n    return carrier.get("single_count_discipline")\n',
            "same_function_bypass": '\ndef bypass(carrier):\n    read_single_count_discipline(carrier, where="ignored")\n    return carrier["single_count_discipline"]\n',
            "key_and_value_alias": '\ndef aliases(carrier):\n    key = "single_count_discipline"\n    value = carrier.get(key)\n    alias = value\n    return alias.get("rule_id")\n',
            "attribute": '\ndef attribute(carrier):\n    return getattr(carrier, "single_count_discipline")\n',
            "api_alias": '\nfrom joulewise.detection_floor import read_single_count_discipline as hidden\ndef alias_api(carrier):\n    return hidden(carrier, where="new")\n',
        }
        for mutation, addition in mutations.items():
            with self.subTest(mutation=mutation):
                changed = dict(self.source_map)
                changed[path] += addition
                with self.assertRaisesRegex(AssertionError, "unclassified raw|reader census drift"):
                    assert_inventory(changed)
        changed = dict(self.source_map)
        changed[path] = changed[path].replace(
            '"single_count_discipline": discipline.copy_wire()',
            '"single_count_discipline": floor_metadata["single_count_discipline"]',
        )
        with self.assertRaisesRegex(AssertionError, "unclassified raw"):
            assert_inventory(changed)
        for path, symbol, callee in EDGES:
            with self.subTest(mutation="deleted_edge", path=path, symbol=symbol, callee=callee):
                tree = ast.parse(self.source_map[path])
                class Delete(ast.NodeTransformer):
                    def visit_Call(self, node):
                        if ast.unparse(node.func) == callee:
                            return ast.copy_location(ast.Constant(None), node)
                        return self.generic_visit(node)
                changed = dict(self.source_map)
                changed[path] = ast.unparse(Delete().visit(tree))
                with self.assertRaisesRegex(AssertionError, "deleted delegate edges|reader census drift"):
                    assert_inventory(changed)

    def test_generated_contract_keeps_the_canonical_v2_object(self):
        from joulewise.detection_floor import (
            attribution_single_count_discipline, SINGLE_COUNT_DISCIPLINE_ID_V1,
        )
        for relative in ("docs/contracts/adapter_contracts.md", "docs/phase_2/detection_floor.md",
                         "docs/site/adapter_contracts.html"):
            text = html.unescape((ROOT / relative).read_text())
            for version, expected in (
                ("v1", attribution_single_count_discipline(SINGLE_COUNT_DISCIPLINE_ID_V1)),
                ("v2", attribution_single_count_discipline()),
            ):
                with self.subTest(document=relative, version=version):
                    candidates = re.findall(
                        r'\{[^{}]*"rule_id"\s*:\s*"attribution_floor_plus_claim_side_bound\.'
                        + version + r'"[^{}]*\}', text,
                    )
                    self.assertEqual(len(candidates), 1, relative)
                    actual = json.loads(candidates[0])
                    self.assertEqual(list(actual.items()), list(expected.items()), relative)
                    self.assertEqual([type(value) for value in actual.values()],
                                     [type(value) for value in expected.values()], relative)

    def test_paper_and_test_helpers_are_scanned(self):
        for directory in SCAN_ROOTS:
            for path in (ROOT / directory).rglob("*.py"):
                self.assertIn(str(path.relative_to(ROOT)), self.source_map)
        for path in ("docs/paper/fill-rehearsal/new_supplier.py", "tests/new_helper.py",
                     "tests/test_new_supplier.py"):
            for body in (
                'def fixture(carrier):\n    return carrier["single_count_discipline"]\n',
                'class Helpers:\n    def setUp(self):\n        return self.carrier.get("single_count_discipline")\n',
                'from joulewise.detection_floor import read_single_count_discipline\n'
                'def fixture(carrier):\n    return read_single_count_discipline(carrier, where="fixture")\n',
            ):
                with self.subTest(path=path, body=body):
                    changed = dict(self.source_map)
                    changed[path] = body
                    with self.assertRaisesRegex(AssertionError, "unclassified raw|reader census drift"):
                        assert_inventory(changed)

    def test_test_entry_points_do_not_hide_reusable_helpers(self):
        source = ('class Checks:\n'
                  '    def test_raw_assertion(self):\n'
                  '        return self.carrier["single_count_discipline"]\n'
                  '    def helper(self):\n'
                  '        return self.carrier["single_count_discipline"]\n')
        _, _, raw = scan_source("tests/test_example.py", source)
        self.assertEqual([(row[1], row[2]) for row in raw],
                         [("Checks.helper", "self.carrier['single_count_discipline']")])

    def test_manifest_exceptions_are_exact_and_used(self):
        kinds = {(row[0], row[1]) for row in MANIFEST if row[2] == "vocabulary"}
        self.assertEqual(kinds, VOCABULARY)
        for path, symbol, expression in RAW_EXCEPTIONS:
            events, _, raw = scan_source(path, self.source_map[path])
            self.assertFalse(raw)
            normalized = normalized_ast(ast.parse(expression, mode="eval").body)
            self.assertIn((path, symbol, "parser", normalized), events)
        emitted = {(row[0], row[1]) for row in MANIFEST if row[2] in ("emitter", "canonical-emitter")}
        self.assertEqual(emitted, EMITTERS)


if __name__ == "__main__":
    unittest.main()
