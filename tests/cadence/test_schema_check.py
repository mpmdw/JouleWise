"""The standard-library schema checker assemble and validate --output use (Sol N3). Synthetic documents only."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from joulewise.cadence_looks import schema_check as sc
from tests.cadence.look_fixtures import minimal

REPO = Path(__file__).resolve().parents[2]
LOOKS = REPO / "docs/process/cadence/looks"
SCHEMAS = ["lm-interim-01.stage1.schema.json", "lm-interim-01.output.schema.json", "look_manifest.schema.json"]


class Keywords(unittest.TestCase):
    def bad(self, instance, schema, fragment):
        errs = sc.errors(instance, schema)
        self.assertTrue(any(fragment in e for e in errs), f"{fragment!r} not in {errs}")

    def test_types(self):
        self.assertEqual(sc.errors(1, {"type": "integer"}), [])
        self.assertEqual(sc.errors(1.0, {"type": "integer"}), [])
        self.bad(True, {"type": "integer"}, "expected integer")
        self.bad(True, {"type": "number"}, "expected number")
        self.bad(1.5, {"type": "integer"}, "expected integer")
        self.assertEqual(sc.errors(None, {"type": ["number", "null"]}), [])
        self.bad("x", {"type": ["number", "null"]}, "expected number/null")

    def test_const_and_enum_keep_booleans_apart(self):
        self.bad(1, {"const": True}, "must be true")
        self.assertEqual(sc.errors(1.0, {"const": 1}), [])
        self.bad(0, {"enum": [False, "x"]}, "must be one of")

    def test_objects(self):
        schema = {"type": "object", "required": ["a"], "additionalProperties": False,
                  "properties": {"a": {"type": "string", "minLength": 2}}}
        self.bad({}, schema, "missing 'a'")
        self.bad({"a": "xy", "b": 1}, schema, "$.b: not allowed")
        self.bad({"a": "x"}, schema, "$.a: shorter than 2")
        self.bad({}, {"type": "object", "minProperties": 1}, "fewer than 1 properties")
        self.bad({"k": "v"}, {"type": "object", "additionalProperties": {"type": "number"}}, "$.k: expected number")

    def test_arrays(self):
        self.bad([], {"type": "array", "minItems": 1}, "fewer than 1 items")
        self.bad([1, 2], {"type": "array", "maxItems": 1}, "more than 1 items")
        self.bad([1, 1.0], {"type": "array", "uniqueItems": True}, "not unique")
        self.assertEqual(sc.errors([1, True], {"type": "array", "uniqueItems": True}), [])
        self.bad([1], {"type": "array", "contains": {"const": 2}}, "contains no item")
        self.bad([1, "x"], {"type": "array", "items": {"type": "integer"}}, "$[1]: expected integer")

    def test_strings_and_numbers(self):
        self.bad("ab", {"pattern": "^[0-9]+$"}, "does not match")
        self.bad(-1, {"minimum": 0}, "below 0")
        self.bad(2, {"maximum": 1}, "above 1")
        self.bad(0, {"exclusiveMinimum": 0}, "not above 0")

    def test_combinators_and_refs(self):
        root = {"$defs": {"n": {"type": "number"}}, "oneOf": [{"$ref": "#/$defs/n"}, {"type": "integer"}]}
        self.bad(1, root, "matches 2 of oneOf")
        self.assertEqual(sc.errors(1.5, root), [])
        self.bad("x", {"anyOf": [{"type": "number"}, {"type": "null"}]}, "matches none of anyOf")
        self.bad(1, {"allOf": [{"type": "number"}, {"maximum": 0}]}, "above 0")
        self.bad(1, {"not": {"type": "integer"}}, "matches a schema it must not")

    def test_unknown_keywords_are_refused_not_ignored(self):
        for schema in ({"format": "date"}, {"if": {}}, {"$ref": "other.json#/x"}, {"type": "decimal"}):
            with self.assertRaises(sc.SchemaUnsupported):
                sc.errors("2026-11-15", schema)

    def test_the_look_schemas_use_only_the_supported_subset(self):
        for name in SCHEMAS:
            schema = json.loads((LOOKS / name).read_text(encoding="utf-8"))
            sc.errors({}, schema)                     # raises SchemaUnsupported on any keyword outside the subset
            for d in schema.get("$defs", {}):
                sc.errors({}, sc.sub_schema(schema, d))


def _mutants(doc):
    """Single-edit variants of a document: each key dropped, an unknown key added, each scalar retyped."""
    out = []

    def walk(node, path):
        if isinstance(node, dict):
            for k in list(node):
                out.append((path + [k], "drop"))
                walk(node[k], path + [k])
            out.append((path, "extra"))
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, path + [i])
        else:
            out.append((path, "retype"))
    walk(doc, [])
    for path, op in out:
        d = copy.deepcopy(doc)
        if op == "extra":
            node = d
            for p in path:
                node = node[p]
            node["per_leg_joules"] = 1.0
        elif path:
            node = d
            for p in path[:-1]:
                node = node[p]
            if op == "drop":
                del node[path[-1]]
            else:
                v = node[path[-1]]
                node[path[-1]] = "x" if not isinstance(v, str) else 7
        yield d


class AgreesWithJsonschema(unittest.TestCase):
    """Where ``jsonschema`` is installed, the checker's valid/invalid verdict equals jsonschema's on every
    single-edit mutant of a minimal valid instance of each of the look's schemas."""

    def test_verdicts_match(self):
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema not installed; the keyword tests above stand alone")
        checked = 0
        for name in SCHEMAS[:2]:
            schema = json.loads((LOOKS / name).read_text(encoding="utf-8"))
            parts = [schema] + [sc.sub_schema(schema, d) for d in ("fit_output", "step3_output") if d in
                                schema.get("$defs", {})]
            for part in parts:
                base = minimal(part)
                self.assertEqual(sc.errors(base, part), [])
                validator = jsonschema.Draft202012Validator(part)
                for d in _mutants(base):
                    ours = not sc.errors(d, part)
                    theirs = validator.is_valid(d)
                    self.assertEqual(ours, theirs, f"{name}: {json.dumps(d)[:300]}")
                    checked += 1
        self.assertGreater(checked, 100)


if __name__ == "__main__":
    unittest.main()
