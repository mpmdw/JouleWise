"""Validate the RL-181 qualification registration and its hash-only finalization."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
import sys

_ROOT = Path(__file__).resolve().parents[2]
_SCHEMA = _ROOT / "docs/process/cadence/looks/look_manifest.v2.schema.json"
_KIT_COMMITMENTS = _SCHEMA.with_name("qualification-kit-commitments.json")
_V2 = "joulewise.cadence_look_manifest.v2"
_PENDING = "PENDING:CODE"
_OPEN = re.compile(r"\bOPEN-[0-9]+\b")


class ManifestError(ValueError):
    """The supplied bytes do not satisfy the registration contract."""


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ManifestError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _reject_constant(value):
    raise ManifestError(f"{value} is not valid JSON")


def _decode(payload):
    try:
        return json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ManifestError(f"invalid UTF-8 JSON: {exc}") from exc


# Only the vocabulary used by the checked-in qualification variant is needed.
_TYPES = {
    "object": (dict,),
    "array": (list,),
    "string": (str,),
    "number": (int, float),
    "integer": (int, float),
    "boolean": (bool,),
}
_KEYWORDS = {
    "$ref", "type", "const", "enum", "pattern", "minimum", "minLength",
    "minItems", "maxItems", "items", "properties", "required", "additionalProperties",
}


def _check(value, rule, definitions, pins, path=()):
    location = "$" + "".join(f"[{part}]" for part in path)

    if rule.keys() - _KEYWORDS:
        raise ManifestError(f"{location}: unsupported schema keyword")
    if "$ref" in rule:
        name = rule["$ref"].removeprefix("#/$defs/")
        if name == "codeHash":
            pins[path] = value
        _check(value, definitions[name], definitions, pins, path)
        return

    kind = rule.get("type")
    if kind and type(value) not in _TYPES[kind]:
        raise ManifestError(f"{location}: expected {kind}")
    if type(value) is float and (
        not math.isfinite(value) or (kind == "integer" and not value.is_integer())
    ):
        raise ManifestError(f"{location}: invalid {kind}")
    if "const" in rule and (
        type(value) is not type(rule["const"]) or value != rule["const"]
    ):
        raise ManifestError(f"{location}: expected {rule['const']!r}")
    if "enum" in rule and value not in rule["enum"]:
        raise ManifestError(f"{location}: unlisted value")

    if isinstance(value, str):
        if _OPEN.search(value) or (_PENDING in value and path not in pins):
            raise ManifestError(f"{location}: placeholder outside a code hash slot")
        if "pattern" in rule and not re.search(rule["pattern"], value):
            raise ManifestError(f"{location}: value does not match the schema pattern")
        if len(value) < rule.get("minLength", 0):
            raise ManifestError(f"{location}: string is too short")
    if "minimum" in rule and value < rule["minimum"]:
        raise ManifestError(f"{location}: value is below the schema minimum")
    if "items" in rule:
        if not rule.get("minItems", 0) <= len(value) <= rule.get("maxItems", len(value)):
            raise ManifestError(f"{location}: wrong number of items")
        for index, item in enumerate(value):
            _check(item, rule["items"], definitions, pins, (*path, index))
    if "properties" in rule:
        properties = rule["properties"]
        missing = set(rule["required"]) - value.keys()
        extra = value.keys() - properties.keys()
        if missing or (extra and rule["additionalProperties"] is False):
            raise ManifestError(f"{location}: missing {sorted(missing)}, extra {sorted(extra)}")
        for key, item in value.items():
            _check(item, properties[key], definitions, pins, (*path, key))


def _parse(payload):
    document = _decode(payload)
    if not isinstance(document, dict) or document.get("schema") != _V2:
        raise ManifestError("expected the v2 qualification manifest schema ID")
    definitions = json.loads(_SCHEMA.read_bytes())["$defs"]
    pins = {}
    _check(document, definitions["qualification"], definitions, pins)
    return document, pins


def _check_registered_kits(document):
    # This roster comes from the reviewed kit source for the look. Reading it
    # independently prevents a well-formed manifest from authenticating itself.
    look_id = document["look_id"]
    record = _decode(_KIT_COMMITMENTS.read_bytes()).get(look_id)
    if record is None:
        raise ManifestError(f"{look_id}: no independent qualification kit commitments")
    expected = record["kit_sha256_by_block"]
    blocks = document["reads"]["blocks"]
    actual = {block["block_id"]: block["kit_sha256"] for block in blocks}
    if len(actual) != len(blocks):
        raise ManifestError("duplicate qualification block ID")
    if actual.keys() != expected.keys():
        raise ManifestError(f"{look_id}: qualification block set differs from the kit commitments")
    for block_id, digest in actual.items():
        if digest != expected[block_id]:
            raise ManifestError(f"{block_id}: kit SHA-256 differs from the kit commitments")


def _registered(payload):
    document, pins = _parse(payload)
    _check_registered_kits(document)
    if not pins or any(value != _PENDING for value in pins.values()):
        raise ManifestError("every registered code and schema hash must be PENDING:CODE")
    sections = payload.split(b'"PENDING:CODE"')
    if len(sections) != len(pins) + 1:
        raise ManifestError("each placeholder must be the literal JSON string PENDING:CODE")
    return document, pins, sections


def validate_registration(payload: bytes) -> dict:
    """Return a registered v2 document after validating its shape and placeholders."""
    document, _, _ = _registered(payload)
    return document


def validate_final(registration: bytes, candidate: bytes) -> dict:
    """Compare a candidate against the trusted registration's exact bytes."""
    _, registered_pins, sections = _registered(registration)
    document, final_pins = _parse(candidate)
    if _PENDING in final_pins.values():
        raise ManifestError("final manifest contains PENDING:CODE")
    if final_pins.keys() != registered_pins.keys():
        raise ManifestError("final manifest changed the registered hash slots")

    # JSON preserves key order and the schema walk reads values in byte order.
    # Rebuild the only allowed byte stream, including its whitespace and escaping.
    expected = [sections[0]]
    for path, suffix in zip(registered_pins, sections[1:], strict=True):
        expected.extend((b'"', final_pins[path].encode("ascii"), b'"', suffix))
    if b"".join(expected) != candidate:
        raise ManifestError("final manifest differs outside the registered hash slots")
    return document


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate", help="validate registered or final manifest bytes")
    validate.add_argument("manifest", type=Path, help="exact bytes from the registration commit")
    validate.add_argument("--final", type=Path, metavar="CANDIDATE")
    args = parser.parse_args(argv)
    try:
        registered = args.manifest.read_bytes()
        if args.final is None:
            validate_registration(registered)
        else:
            validate_final(registered, args.final.read_bytes())
    except (ManifestError, OSError) as exc:
        print(f"qualification manifest: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
