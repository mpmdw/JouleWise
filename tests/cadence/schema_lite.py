"""A small JSON Schema (2020-12 subset) checker for the look's schemas, so the tests need no third-party package.
Covers what docs/process/cadence/looks/*.schema.json use: type, enum, const, required, properties,
additionalProperties, patternProperties, propertyNames, items, prefixItems, $ref (local), pattern, minimum,
maximum, exclusiveMinimum, minItems, maxItems, uniqueItems, minProperties, oneOf, anyOf, allOf, not. Any other
keyword makes the checker refuse, so a schema feature it does not know cannot pass silently."""
from __future__ import annotations

import math
import re

KNOWN = {"$schema", "$id", "$defs", "$comment", "title", "description", "type", "enum", "const", "required",
         "properties", "additionalProperties", "patternProperties", "propertyNames", "items", "prefixItems", "$ref",
         "pattern", "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "minItems", "maxItems",
         "uniqueItems", "minProperties", "maxProperties", "oneOf", "anyOf", "allOf", "not", "default", "examples",
         "format", "minLength", "maxLength"}


def _type_ok(v, t):
    return {"object": isinstance(v, dict), "array": isinstance(v, list), "string": isinstance(v, str),
            "boolean": isinstance(v, bool), "null": v is None,
            "integer": isinstance(v, int) and not isinstance(v, bool),
            "number": isinstance(v, (int, float)) and not isinstance(v, bool)}[t]


def _eq(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return type(a) is type(b) and a == b
    return a == b


def errors(value, schema, root=None, path="$"):
    root = schema if root is None else root
    out = []
    if schema is True:
        return out
    if schema is False:
        return [f"{path}: not allowed"]
    unknown = set(schema) - KNOWN
    if unknown:
        return [f"{path}: schema keyword(s) not supported: {sorted(unknown)}"]
    if "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/"):
            return [f"{path}: non-local $ref"]
        node = root
        for part in ref[2:].split("/"):
            node = node[part]
        out += errors(value, node, root, path)
    if "type" in schema:
        ts = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_type_ok(value, t) for t in ts):
            return out + [f"{path}: type {type(value).__name__} not in {ts}"]
    if "enum" in schema and not any(_eq(value, e) for e in schema["enum"]):
        out.append(f"{path}: {value!r} not in enum")
    if "const" in schema and not _eq(value, schema["const"]):
        out.append(f"{path}: {value!r} != const {schema['const']!r}")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if isinstance(value, float) and not math.isfinite(value):
            out.append(f"{path}: non-finite")
        if "minimum" in schema and value < schema["minimum"]:
            out.append(f"{path}: below minimum")
        if "maximum" in schema and value > schema["maximum"]:
            out.append(f"{path}: above maximum")
        if "exclusiveMinimum" in schema and value <= schema["exclusiveMinimum"]:
            out.append(f"{path}: not above exclusiveMinimum")
        if "exclusiveMaximum" in schema and value >= schema["exclusiveMaximum"]:
            out.append(f"{path}: not below exclusiveMaximum")
    if isinstance(value, str):
        if "pattern" in schema and not re.search(schema["pattern"], value):
            out.append(f"{path}: {value!r} does not match {schema['pattern']!r}")
        if "minLength" in schema and len(value) < schema["minLength"]:
            out.append(f"{path}: too short")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            out.append(f"{path}: too long")
    if isinstance(value, dict):
        for k in schema.get("required", []):
            if k not in value:
                out.append(f"{path}: missing {k!r}")
        props = schema.get("properties", {})
        pats = schema.get("patternProperties", {})
        for k, v in value.items():
            matched = False
            if k in props:
                matched = True
                out += errors(v, props[k], root, f"{path}.{k}")
            for pat, sub in pats.items():
                if re.search(pat, k):
                    matched = True
                    out += errors(v, sub, root, f"{path}.{k}")
            if not matched and "additionalProperties" in schema:
                out += errors(v, schema["additionalProperties"], root, f"{path}.{k}")
            if "propertyNames" in schema:
                out += errors(k, schema["propertyNames"], root, f"{path}.<name {k}>")
        if "minProperties" in schema and len(value) < schema["minProperties"]:
            out.append(f"{path}: too few properties")
        if "maxProperties" in schema and len(value) > schema["maxProperties"]:
            out.append(f"{path}: too many properties")
    if isinstance(value, list):
        pre = schema.get("prefixItems", [])
        for i, v in enumerate(value):
            if i < len(pre):
                out += errors(v, pre[i], root, f"{path}[{i}]")
            elif "items" in schema:
                out += errors(v, schema["items"], root, f"{path}[{i}]")
        if "minItems" in schema and len(value) < schema["minItems"]:
            out.append(f"{path}: too few items")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            out.append(f"{path}: too many items")
        if schema.get("uniqueItems"):
            seen = []
            for v in value:
                if any(_eq(v, s) for s in seen):
                    out.append(f"{path}: items not unique")
                    break
                seen.append(v)
    for sub in schema.get("allOf", []):
        out += errors(value, sub, root, path)
    if "anyOf" in schema and not any(not errors(value, sub, root, path) for sub in schema["anyOf"]):
        out.append(f"{path}: matches no anyOf branch")
    if "oneOf" in schema:
        n = sum(1 for sub in schema["oneOf"] if not errors(value, sub, root, path))
        if n != 1:
            best = min((errors(value, sub, root, path) for sub in schema["oneOf"]), key=len)
            out.append(f"{path}: matches {n} oneOf branches (closest: {best[:3]})")
    if "not" in schema and not errors(value, schema["not"], root, path):
        out.append(f"{path}: matches 'not'")
    return out
