"""A small JSON Schema (draft 2020-12) checker for the look's own schemas, standard library only (Sol cold seat N3).

The look's schemas (docs/process/cadence/looks/*.schema.json) use a fixed subset of the vocabulary, and CI has no
``jsonschema``. This module implements exactly that subset:

* ``type`` (one name or a list; ``integer`` and ``number`` exclude booleans), ``const``, ``enum``;
* ``properties``, ``required``, ``additionalProperties`` (``false`` or a schema), ``minProperties``,
  ``propertyNames`` (each key checked as a string: a map's keys are constrained, so no leg-keyed value fits where a
  day or a column is meant; Sol NEW-1, Mythos N9);
* ``items``, ``minItems``, ``maxItems``, ``uniqueItems``, ``contains``;
* ``pattern`` (``re.search``), ``minLength``;
* ``minimum``, ``maximum``, ``exclusiveMinimum``;
* ``oneOf``, ``anyOf``, ``allOf``, ``not``;
* ``$ref`` to ``#/$defs/<name>`` within the same document.

A schema that uses any other keyword is refused (``SchemaUnsupported``) rather than silently half-checked. The
annotation keywords (``$schema``, ``$id``, ``$comment``, ``title``, ``description``) are ignored.
``tests/cadence/test_schema_check.py`` compares the results with ``jsonschema`` where that package is
installed.
"""
from __future__ import annotations

import json
import math
import re

ANNOTATIONS = {"$schema", "$id", "$comment", "title", "description", "$defs"}
KEYWORDS = {"type", "const", "enum", "properties", "required", "additionalProperties", "minProperties", "propertyNames", "items",
            "minItems", "maxItems", "uniqueItems", "contains", "pattern", "minLength", "minimum", "maximum",
            "exclusiveMinimum", "oneOf", "anyOf", "allOf", "not", "$ref"}


class SchemaUnsupported(ValueError):
    pass


def _is_type(value, name):
    if name == "null":
        return value is None
    if name == "boolean":
        return isinstance(value, bool)
    if name == "integer":
        return (isinstance(value, int) and not isinstance(value, bool)) or \
            (isinstance(value, float) and math.isfinite(value) and value.is_integer())
    if name == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if name == "string":
        return isinstance(value, str)
    if name == "array":
        return isinstance(value, list)
    if name == "object":
        return isinstance(value, dict)
    raise SchemaUnsupported(f"type {name!r}")


def _equal(a, b):
    """JSON equality: 1 == 1.0, but True != 1."""
    if isinstance(a, bool) or isinstance(b, bool):
        return type(a) is type(b) and a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return a == b
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(_equal(x, y) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(_equal(a[k], b[k]) for k in a)
    return type(a) is type(b) and a == b


def _ecma_end(pattern):
    """JSON Schema patterns are ECMA-262: "$" matches only at the end of the string, where Python's also matches
    before a final newline. A trailing unescaped "$" becomes "\\Z" (Mythos/r6 test: "dev-01\\n" must not pass)."""
    if pattern.endswith("$") and not pattern.endswith("\\$"):
        return pattern[:-1] + "\\Z"
    return pattern


def errors(instance, schema, root=None, path="$"):
    """Every violation of ``schema`` by ``instance``, as ["<json path>: <message>"]; [] when valid."""
    root = schema if root is None else root
    if schema is True:
        return []
    if schema is False:
        return [f"{path}: not allowed"]
    unknown = set(schema) - KEYWORDS - ANNOTATIONS
    if unknown:
        raise SchemaUnsupported(f"{path}: keywords {sorted(unknown)}")
    out = []
    if "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/$defs/"):
            raise SchemaUnsupported(f"$ref {ref!r}")
        out += errors(instance, root["$defs"][ref[len("#/$defs/"):]], root, path)
    if "type" in schema:
        names = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_is_type(instance, n) for n in names):
            return out + [f"{path}: expected {'/'.join(names)}, got {type(instance).__name__}"]
    if "const" in schema and not _equal(instance, schema["const"]):
        out.append(f"{path}: must be {json.dumps(schema['const'])}")
    if "enum" in schema and not any(_equal(instance, v) for v in schema["enum"]):
        out.append(f"{path}: must be one of {json.dumps(schema['enum'])}")
    if isinstance(instance, dict):
        props = schema.get("properties", {})
        for k in schema.get("required", []):
            if k not in instance:
                out.append(f"{path}: missing {k!r}")
        for k, v in instance.items():
            if k in props:
                out += errors(v, props[k], root, f"{path}.{k}")
            elif "additionalProperties" in schema:
                ap = schema["additionalProperties"]
                if ap is False:
                    out.append(f"{path}.{k}: not allowed")
                elif isinstance(ap, dict):
                    out += errors(v, ap, root, f"{path}.{k}")
        if "propertyNames" in schema:
            for k in instance:
                out += [f"{path}: key {k!r}: {e.split(': ', 1)[-1]}" for e in errors(k, schema["propertyNames"], root, path)]
        if "minProperties" in schema and len(instance) < schema["minProperties"]:
            out.append(f"{path}: fewer than {schema['minProperties']} properties")
    if isinstance(instance, list):
        if "items" in schema:
            for i, v in enumerate(instance):
                out += errors(v, schema["items"], root, f"{path}[{i}]")
        if "minItems" in schema and len(instance) < schema["minItems"]:
            out.append(f"{path}: fewer than {schema['minItems']} items")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            out.append(f"{path}: more than {schema['maxItems']} items")
        if schema.get("uniqueItems") and any(_equal(a, b) for i, a in enumerate(instance) for b in instance[i + 1:]):
            out.append(f"{path}: items are not unique")
        if "contains" in schema and not any(not errors(v, schema["contains"], root, path) for v in instance):
            out.append(f"{path}: contains no item matching {json.dumps(schema['contains'])[:80]}")
    if isinstance(instance, str):
        if "pattern" in schema and not re.search(_ecma_end(schema["pattern"]), instance):
            out.append(f"{path}: does not match {schema['pattern']!r}")
        if "minLength" in schema and len(instance) < schema["minLength"]:
            out.append(f"{path}: shorter than {schema['minLength']}")
    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            out.append(f"{path}: below {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            out.append(f"{path}: above {schema['maximum']}")
        if "exclusiveMinimum" in schema and instance <= schema["exclusiveMinimum"]:
            out.append(f"{path}: not above {schema['exclusiveMinimum']}")
    if "allOf" in schema:
        for sub in schema["allOf"]:
            out += errors(instance, sub, root, path)
    if "anyOf" in schema and not any(not errors(instance, sub, root, path) for sub in schema["anyOf"]):
        out.append(f"{path}: matches none of anyOf")
    if "oneOf" in schema:
        n = sum(1 for sub in schema["oneOf"] if not errors(instance, sub, root, path))
        if n != 1:
            out.append(f"{path}: matches {n} of oneOf, not exactly 1")
    if "not" in schema and not errors(instance, schema["not"], root, path):
        out.append(f"{path}: matches a schema it must not")
    return out


def sub_schema(schema, name):
    """A $defs entry as a standalone schema (its $refs still resolve)."""
    return {**schema["$defs"][name], "$defs": schema["$defs"]}
