"""Closed-shape primitives for stage-1 admission (RL-184 section 3.3).

A check is a callable ``check(value, where)`` that returns None or raises ``Refusal``. ``where`` names the file and
the member; a refusal never carries a value. Objects are closed: an unknown member refuses, so does a missing one.
JSON kinds are kept apart: a boolean is not an integer, an integral float is not an integer, text is never a number.
"""
from __future__ import annotations

import math
import re

from joulewise.cadence_looks import custody_pins

SHIELDED = custody_pins.SHIELDED


class Refusal(ValueError):
    """A shape no pinned writer serializes. The message names the place, never a value."""


def refuse(where, what):
    raise Refusal(f"{where}: {what}")


# ------------------------------------------------------------------------------------------------ strict decoding
def decode(raw, where):
    """One strict JSON document from UTF-8 bytes: no duplicate member, no nonfinite number, no trailing document,
    no byte-order mark. Member order and insignificant whitespace are not shape. A number under an energy-named
    member is never converted: the look's one decoder of operational files leaves ``SHIELDED`` in its place
    (``custody_pins.operational_json``), and ``MEASURED`` is the leaf that admits it."""
    try:
        return custody_pins.operational_json(bytes(raw).decode("utf-8"))
    except custody_pins.OperationalJSONError as error:
        refuse(where, {"duplicate": "a duplicate member", "nonfinite": "a nonfinite number"}.get(
            error.reason, "not UTF-8 JSON as the pinned writers serialize it"))
    except ValueError:
        refuse(where, "not UTF-8 JSON as the pinned writers serialize it")


def decode_lines(raw, where):
    """A JSON-lines journal: one strict object per LF-terminated record. A cut final record, a blank record and a
    record that is not an object refuse. CR before LF and spaces around a record are not shape."""
    data = bytes(raw)
    if not data:
        return []
    if not data.endswith(b"\n"):
        refuse(where, "a final record without its line end")
    rows = []
    for index, line in enumerate(data[:-1].split(b"\n")):
        if not line.strip(b" \t\r"):
            refuse(where, "a blank record")
        row = decode(line, where)
        if type(row) is not dict:
            refuse(f"{where}[{index}]", "not an object")
        rows.append(row)
    return rows


# ------------------------------------------------------------------------------------------------------ leaves
def is_int(value):
    return type(value) is int


def is_num(value):
    """A finite JSON number of either kind; never a boolean."""
    if type(value) is int:
        return True
    return type(value) is float and math.isfinite(value)


def INT(value, where):
    if type(value) is not int:
        refuse(where, "not an integer")


def NAT(value, where):
    if type(value) is not int or value < 0:
        refuse(where, "not a count")


def POS(value, where):
    if type(value) is not int or value < 1:
        refuse(where, "not a positive integer")


def FLOAT(value, where):
    """A float the writer took from a clock or a difference of clocks: never an integer token."""
    if type(value) is not float or not math.isfinite(value):
        refuse(where, "not a float")


def NUM(value, where):
    if not is_num(value):
        refuse(where, "not a number")


def MEASURED(value, where):
    """A number under an energy-named member (the idle baseline's mean power in ``events.jsonl``). The decoder
    never made it a number, so there is no value here to check: only that the writer put a number there."""
    if value is not SHIELDED:
        refuse(where, "not a number")


def NONNEG(value, where):
    if not is_num(value) or value < 0:
        refuse(where, "not a nonnegative number")


def STR(value, where):
    if type(value) is not str:
        refuse(where, "not text")


def TEXT(value, where):
    if type(value) is not str or not value:
        refuse(where, "not nonempty text")


def BOOL(value, where):
    if type(value) is not bool:
        refuse(where, "not a boolean")


def NULL(value, where):
    if value is not None:
        refuse(where, "not null")


def const(expected):
    def check(value, where):
        if type(value) is not type(expected) or value != expected:
            refuse(where, "not the value the writer fixes here")
    return check


def enum(*allowed):
    allowed = tuple(allowed)

    def check(value, where):
        if not any(type(value) is type(item) and value == item for item in allowed):
            refuse(where, "not a registered value")
    return check


def rx(pattern):
    compiled = re.compile(pattern)

    def check(value, where):
        if type(value) is not str or not compiled.fullmatch(value):
            refuse(where, "not the registered spelling")
    return check


DIGEST = rx(r"[0-9a-f]{64}")
REVISION = rx(r"[0-9a-f]{40}")


def nullable(check):
    def nullable_check(value, where):
        if value is not None:
            check(value, where)
    return nullable_check


def either(*checks):
    """The value satisfies one of the alternatives. The refusal names none of them."""
    def check(value, where):
        for alternative in checks:
            try:
                alternative(value, where)
                return
            except Refusal:
                continue
        refuse(where, "not one of the writers' alternatives")
    return check


def arr(item, *, least=0, most=None):
    def check(value, where):
        if type(value) is not list or len(value) < least or (most is not None and len(value) > most):
            refuse(where, "not the array the writer serializes")
        for index, element in enumerate(value):
            item(element, f"{where}[{index}]")
    return check


def obj(required, optional=None):
    """A closed object: exactly ``required`` plus any of ``optional``, each member checked."""
    optional = optional or {}

    def check(value, where):
        if type(value) is not dict:
            refuse(where, "not an object")
        for key in value:
            if key not in required and key not in optional:
                refuse(where, "a member no pinned writer serializes")
        for key, member in required.items():
            if key not in value:
                refuse(where, f"lacks {key}")
            member(value[key], f"{where}.{key}")
        for key, member in optional.items():
            if key in value:
                member(value[key], f"{where}.{key}")
    return check


def mapping(member, key=None):
    """An object whose member names the writer does not fix (a sensor map), each value checked."""
    def check(value, where):
        if type(value) is not dict:
            refuse(where, "not an object")
        for name, item in value.items():
            if key is not None:
                key(name, where)
            member(item, f"{where}.{name}")
    return check


def keys(value, where, required, optional=()):
    """Exact member set of an object already known to be one."""
    if type(value) is not dict:
        refuse(where, "not an object")
    for key in value:
        if key not in required and key not in optional:
            refuse(where, "a member no pinned writer serializes")
    for key in required:
        if key not in value:
            refuse(where, f"lacks {key}")
