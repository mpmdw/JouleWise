"""Minimal schema-valid documents for the look's schemas, built from the schemas themselves. Synthetic only.

``minimal(schema)`` walks a schema (the subset ``schema_check`` supports) and returns the smallest instance it can:
required keys only, empty arrays and maps where allowed, the first enum or const, null where a type list allows
it, and strings matched to the look's few patterns. The result is checked with ``schema_check`` by the callers.
"""
from __future__ import annotations

PATTERNS = {"[0-9a-f]{64}": "a" * 64, r"\d{4}-\d{2}-\d{2}": "2026-11-16", "[LH]": "dev-03-s01/L001",
            "^RL-": "RL-999", "^lm-": "lm-interim-01"}


def _string(schema):
    pat = schema.get("pattern")
    if pat:
        for key, val in PATTERNS.items():
            if key in pat:
                return val
    return "x" * max(1, schema.get("minLength", 1))


def minimal(schema, root=None):
    root = schema if root is None else root
    if "$ref" in schema:
        return minimal(root["$defs"][schema["$ref"].split("/")[-1]], root)
    if "const" in schema:
        return schema["const"]
    if "enum" in schema:
        return schema["enum"][0]
    if "oneOf" in schema:
        for sub in schema["oneOf"]:
            if sub.get("type") == "null":
                return None
        return minimal(schema["oneOf"][0], root)
    if "allOf" in schema and "type" not in schema:
        return minimal(schema["allOf"][0], root)
    t = schema.get("type")
    if isinstance(t, list):
        if "null" in t:
            return None
        t = t[0]
    if t == "object" or (t is None and "properties" in schema):
        out = {k: minimal(schema["properties"][k], root) for k in schema.get("required", [])}
        ap = schema.get("additionalProperties")
        if isinstance(ap, dict) and schema.get("minProperties"):
            out["k"] = minimal(ap, root)
        return out
    if t == "array":
        n = schema.get("minItems", 0)
        if n and "items" in schema and "enum" in schema["items"]:
            return list(schema["items"]["enum"][:n])
        return [minimal(schema["items"], root) for _ in range(n)] if n else []
    if t == "string":
        return _string(schema)
    if t == "integer":
        return int(schema.get("minimum", 0))
    if t == "number":
        return float(schema.get("minimum", 0.0)) + (1.0 if "exclusiveMinimum" in schema else 0.0)
    if t == "boolean":
        return False
    if t == "null":
        return None
    return {}
