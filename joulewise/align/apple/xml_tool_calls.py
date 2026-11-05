"""Strict Qwen3.5/3.8 pseudo-XML, selected by config, never syntax guessing.

This is not XML: names occur after '=' and string values are unescaped.
Only template framing newlines are removed. Strings stay literal; other
values are JSON, disambiguated by the advertised function's parameter schema.
An invalid call invalidates the whole turn, so no partial action is executed.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from typing import Any, Mapping, Sequence

from joulewise.align.interfaces import ToolCallRequest

# HF model_type spellings; qwen3_moe and qwen3_next deliberately stay JSON.
XML_MODEL_FAMILIES = frozenset({
    "qwen3_5", "qwen3_5_moe", "qwen3_5_text", "qwen3_5_moe_text",
    "qwen3_8", "qwen3_8_moe", "qwen3_8_text", "qwen3_8_moe_text",
})
_FUNCTION = re.compile(r"<function=([^<>\s=]+)>")
_PARAMETER = re.compile(r"<parameter=([^<>\s=]+)>")
_CONTROL = re.compile(r"</?(?:tool_call|function|parameter)\b")


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _invalid_constant(value):
    raise ValueError("non-finite JSON constant")


def _json_value(text):
    return json.loads(text, object_pairs_hook=_unique_object,
                      parse_constant=_invalid_constant)


def _accepts(value: Any, schema: Mapping[str, Any], root: Mapping[str, Any], depth=0) -> bool:
    """Check JSON types, unions, enums, and nested declared parameter shapes.

    This is wire type validation, not a general JSON Schema implementation
    (e.g. string patterns/ranges remain the tool's responsibility).
    """
    if depth > 64:
        raise ValueError("parameter schema nesting limit")
    if not isinstance(schema, Mapping):
        raise ValueError("parameter schema must be a mapping")
    if "$ref" in schema:
        ref = schema["$ref"]
        if not isinstance(ref, str) or not ref.startswith("#/"):
            raise ValueError("only local parameter schema references are supported")
        target = root
        for part in ref[2:].split("/"):
            target = target[part.replace("~1", "/").replace("~0", "~")]
        if not _accepts(value, target, root, depth + 1):
            return False
    for keyword in ("anyOf", "oneOf", "allOf"):
        if keyword in schema:
            choices = [_accepts(value, branch, root, depth + 1) for branch in schema[keyword]]
            if not ({"anyOf": any(choices), "oneOf": sum(choices) == 1,
                     "allOf": all(choices)}[keyword]):
                return False
    kind = schema.get("type")
    types = {
        "string": isinstance(value, str), "boolean": type(value) is bool,
        "integer": type(value) is int,
        "number": type(value) in (int, float) and (type(value) is int or math.isfinite(value)),
        "null": value is None, "object": isinstance(value, dict),
        "array": isinstance(value, list),
    }
    if kind is not None:
        kinds = [kind] if isinstance(kind, str) else kind
        if not isinstance(kinds, list) or any(k not in types for k in kinds):
            raise ValueError("unsupported parameter schema type")
        if not any(types[k] for k in kinds):
            return False
    # JSON equality must not identify true with 1 (Python's bool subclasses int).
    def equal(other):
        return json.dumps(value, sort_keys=True, allow_nan=False) == json.dumps(
            other, sort_keys=True, allow_nan=False)
    if "enum" in schema and not any(equal(item) for item in schema["enum"]):
        return False
    if "const" in schema and not equal(schema["const"]):
        return False
    if isinstance(value, dict):
        properties = schema.get("properties", {})
        if any(key not in value for key in schema.get("required", ())):
            return False
        for key, item in value.items():
            if key in properties:
                if not _accepts(item, properties[key], root, depth + 1):
                    return False
            else:
                additional = schema.get("additionalProperties", True)
                if additional is False:
                    return False
                if isinstance(additional, Mapping) and not _accepts(item, additional, root, depth + 1):
                    return False
    if isinstance(value, list) and "items" in schema:
        if not all(_accepts(item, schema["items"], root, depth + 1) for item in value):
            return False
    return True


def _decode(raw, schema, root):
    # The template emits exactly one LF on either side, not arbitrary trim().
    raw = raw.removeprefix("\n").removesuffix("\n")
    candidates = [raw]
    try:
        decoded = _json_value(raw)
    except ValueError:
        pass
    else:
        # A decoded string was actually emitted literally with its quote marks.
        if not isinstance(decoded, str):
            candidates.append(decoded)
    matches = [value for value in candidates if _accepts(value, schema, root)]
    if len(matches) != 1:
        raise ValueError("ambiguous_or_invalid_parameter_type")
    return matches[0]


def parse_xml_calls(
    visible: str, tools: Sequence[Mapping[str, Any]],
) -> tuple[tuple[ToolCallRequest, ...], tuple[str, ...]]:
    """Parse complete sibling calls, or return an actionable refusal flag.

    Natural-language text may precede calls. Reserved control tags in literal
    values are unrepresentable without ambiguity and are refused, not unescaped.
    """
    first = visible.find("<tool_call>")
    if first < 0:
        if _CONTROL.search(visible):
            return (), ("malformed_tool_call:xml:unmatched_control_tag",)
        if any(marker in visible for marker in (
            "<tool", "<function", "<|python_tag|>", "[TOOL_CALLS]",
            '"tool_calls"', '"name"', '"parameters"', '"arguments"',
        )):
            return (), ("unsupported_tool_call_format",)
        return (), ()
    calls = []
    try:
        if _CONTROL.search(visible[:first]):
            raise ValueError("unmatched_control_tag")
        functions = {}
        for tool in tools:
            function = tool["function"]
            if function["name"] in functions:
                raise ValueError("duplicate_function_schema")
            functions[function["name"]] = function.get("parameters", {"type": "object"})
        cursor = first

        def expect(token):
            nonlocal cursor
            if not visible.startswith(token, cursor):
                raise ValueError("invalid_xml_structure")
            cursor += len(token)

        def whitespace():
            nonlocal cursor
            while cursor < len(visible) and visible[cursor].isspace():
                cursor += 1

        while cursor < len(visible):
            start = cursor
            expect("<tool_call>")
            whitespace()
            match = _FUNCTION.match(visible, cursor)
            if match is None:
                raise ValueError("expected_function")
            name = match[1]
            if name not in functions:
                raise ValueError("unknown_function")
            schema = functions[name]
            properties = schema.get("properties", {})
            arguments = {}
            cursor = match.end()
            whitespace()
            while (match := _PARAMETER.match(visible, cursor)) is not None:
                key = match[1]
                if key in arguments:
                    raise ValueError("duplicate_parameter")
                if key not in properties:
                    raise ValueError("unknown_parameter")
                end = visible.find("</parameter>", match.end())
                if end < 0:
                    raise ValueError("unclosed_parameter")
                raw = visible[match.end():end]
                if _CONTROL.search(raw):
                    raise ValueError("nested_control_tag")
                arguments[key] = _decode(raw, properties[key], schema)
                cursor = end + len("</parameter>")
                whitespace()
            expect("</function>")
            whitespace()
            expect("</tool_call>")
            if not _accepts(arguments, schema, schema):
                raise ValueError("invalid_or_missing_parameters")
            arguments_json = json.dumps(arguments, sort_keys=True, separators=(",", ":"), allow_nan=False)
            emitted = visible[start:cursor]
            call_id = hashlib.sha256(f"{len(calls)}\0{emitted}".encode("utf-8")).hexdigest()
            calls.append(ToolCallRequest(call_id, name, arguments_json))
            whitespace()
            # Every remaining non-whitespace byte must start another call.
        return tuple(calls), ()
    except (AttributeError, KeyError, TypeError, ValueError, RecursionError) as exc:
        return (), (f"malformed_tool_call:xml:{exc}",)
