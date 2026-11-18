"""Compare two JSON reports against separately bound, external output schemas.

The caller compiles the two wire schemas from the input design before reading
reports. This module has no producer, analysis or release authority.
"""

from collections import Counter, defaultdict
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from itertools import combinations
import json
import math
import re
from types import MappingProxyType

AGREE, HOLD, REFUSED = 0, 1, 2
SIDES = ("L", "R")
UNSET = object()
IDENTITY_TYPES = (str, int)
LEAF_TYPES = (str, int, float, bool, type(None))
Path = tuple[str | int, ...]


@dataclass(frozen=True)
class Key:
    family: str
    row: Path
    leaf: str


@dataclass(frozen=True)
class Rule:
    kind: type
    unit: str
    source: str
    expected: object = UNSET
    absolute: float | None = None
    presence_only: bool = False
    pattern: str | None = None
    refuse_mismatch: bool = False
    sides: tuple[str, ...] = SIDES
    alias_reason: str = ""

    def __post_init__(self):
        if self.kind not in LEAF_TYPES or not self.unit or not self.source:
            raise ValueError("a rule needs a scalar type, unit and source")
        if self.expected is not UNSET and not self.valid_type(self.expected):
            raise ValueError("invalid expected literal")
        if self.absolute is not None and (
            self.kind is not float or type(self.absolute) not in (int, float)
            or not math.isfinite(self.absolute) or self.absolute < 0 or self.presence_only
        ):
            raise ValueError("invalid absolute bar")
        if self.pattern is not None and self.kind is not str:
            raise ValueError("only string leaves can have a pattern")
        if self.pattern is not None:
            re.compile(self.pattern)
        if self.sides != SIDES and (not self.presence_only or self.sides not in (("L",), ("R",))):
            raise ValueError("comparison requires both sides")

    def valid_type(self, value):
        return type(value) is self.kind and (self.kind is not float or math.isfinite(value))

    def agrees(self, left, right):
        if self.absolute is not None:
            return abs(left - right) <= self.absolute
        return left == right


@dataclass(frozen=True)
class Object:
    family: str
    fields: Mapping[str, "Node"]
    empty_reason: str = ""

    def __post_init__(self):
        object.__setattr__(self, "fields", MappingProxyType(dict(self.fields)))


@dataclass(frozen=True)
class Sequence:
    family: str
    entries: tuple["Node", ...]
    empty_reason: str = ""


@dataclass(frozen=True)
class Rows:
    """An order-insensitive array indexed by named fields in each wire object."""

    family: str
    identity: tuple[str, ...]
    entries: Mapping[Path, Object]
    empty_reason: str = ""

    def __post_init__(self):
        object.__setattr__(self, "entries", MappingProxyType(dict(self.entries)))


Node = Key | Object | Sequence | Rows


def _registered_leaves(node: Node) -> Iterator[Key]:
    if not isinstance(node, (Key, Object, Sequence, Rows)) or not node.family:
        raise ValueError("every schema node needs a family")
    if isinstance(node, Key):
        if not node.leaf or any(type(part) not in IDENTITY_TYPES for part in node.row):
            raise ValueError("invalid logical key")
        yield node
        return
    children = node.fields if isinstance(node, Object) else node.entries
    if not children and not node.empty_reason:
        raise ValueError("empty container needs an independent applicability reason")
    if isinstance(node, Object):
        for name, child in node.fields.items():
            if type(name) is not str:
                raise ValueError("object field name must be a string")
            yield from _registered_leaves(child)
    elif isinstance(node, Sequence):
        for child in node.entries:
            yield from _registered_leaves(child)
    else:
        ids = node.identity
        if not ids or any(type(name) is not str for name in ids) or len(set(ids)) != len(ids):
            raise ValueError("invalid row identity fields")
        for identity, row in node.entries.items():
            if (type(identity) is not tuple or len(identity) != len(ids)
                or any(type(part) not in IDENTITY_TYPES for part in identity)
                or not isinstance(row, Object)
                or any(not isinstance(row.fields.get(name), Key) for name in ids)):
                raise ValueError("row lacks a registered scalar identity")
            yield from _registered_leaves(row)


@dataclass(frozen=True)
class Census:
    left: Object
    right: Object
    rules: Mapping[Key, Rule]

    def __post_init__(self):
        counts = {side: Counter(_registered_leaves(node))
                  for side, node in zip(SIDES, (self.left, self.right), strict=True)}
        rules = dict(self.rules)
        if set(rules) != set(counts["L"]) | set(counts["R"]):
            raise ValueError("unbound leaf or unused rule")
        for key, rule in rules.items():
            if tuple(side for side in SIDES if counts[side][key]) != rule.sides:
                raise ValueError("incorrect wire sides")
            if any(counts[side][key] > 1 for side in SIDES) and not rule.alias_reason:
                raise ValueError("repeated leaf needs an alias relationship")
        object.__setattr__(self, "rules", MappingProxyType(rules))


def pointer(path: Path) -> str:
    return "".join("/" + str(part).replace("~", "~0").replace("/", "~1") for part in path)


@dataclass(frozen=True)
class Finding:
    exit_code: int
    family: str
    side: str
    path: Path
    code: str
    key: Key | None = None
    identity: Path | None = None


@dataclass(frozen=True)
class Binding:
    side: str
    path: Path
    key: Key
    rule: Rule


@dataclass(frozen=True)
class Result:
    findings: tuple[Finding, ...]
    bindings: tuple[Binding, ...] = ()

    @property
    def exit_code(self):
        return max((finding.exit_code for finding in self.findings), default=AGREE)

    def public_summary(self):
        exit_code = self.exit_code
        return {"verdict": ("AGREE", "HOLD", "REFUSED")[exit_code], "exit_code": exit_code}


class _InvalidJSON(ValueError):
    pass


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise _InvalidJSON("duplicate_json_key")
        result[key] = value
    return result


def _nonfinite(_):
    raise _InvalidJSON("nonfinite_json")


def _finite_float(token):
    value = float(token)
    if not math.isfinite(value):
        _nonfinite(token)
    return value


def _load(text):
    return json.loads(text, object_pairs_hook=_unique_object,
                      parse_constant=_nonfinite, parse_float=_finite_float)


class _Wire:
    def __init__(self, side, rules):
        self.side = side
        self.rules = rules
        self.findings = []
        self.bindings = []
        self.values = defaultdict(list)

    def refuse(self, node, path, code, identity=None):
        key = node if isinstance(node, Key) else None
        self.findings.append(Finding(REFUSED, node.family, self.side, path, code, key, identity))

    def visit(self, node, value, path=()):
        if isinstance(node, Key):
            rule = self.rules[node]
            if not rule.valid_type(value):
                self.refuse(node, path, "type")
            elif rule.expected is not UNSET and value != rule.expected:
                self.refuse(node, path, "state")
            elif rule.pattern is not None and re.fullmatch(rule.pattern, value) is None:
                self.refuse(node, path, "shape")
            else:
                self.bindings.append(Binding(self.side, path, node, rule))
                self.values[node].append((self.side, path, value))
        elif isinstance(node, Object):
            if type(value) is not dict:
                self.refuse(node, path, "type")
                return
            for name in sorted(value.keys() - node.fields.keys()):
                self.refuse(node, path + (name,), "extra")
            for name, child in node.fields.items():
                if name not in value:
                    self.refuse(child, path + (name,), "missing")
                else:
                    self.visit(child, value[name], path + (name,))
        elif type(value) is not list:
            self.refuse(node, path, "type")
        elif isinstance(node, Sequence):
            for index, child in enumerate(node.entries):
                if index >= len(value):
                    self.refuse(child, path + (index,), "missing")
                else:
                    self.visit(child, value[index], path + (index,))
            for index in range(len(node.entries), len(value)):
                self.refuse(node, path + (index,), "extra")
        else:
            self.visit_rows(node, value, path)

    def visit_rows(self, node, rows, path):
        seen = set()
        for index, row in enumerate(rows):
            row_path = path + (index,)
            if type(row) is not dict:
                self.refuse(node, row_path, "type")
                continue
            identity = tuple(row.get(name) for name in node.identity)
            if any(type(part) not in IDENTITY_TYPES for part in identity):
                self.refuse(node, row_path, "invalid_identity")
                continue
            if identity in seen:
                self.refuse(node, row_path, "duplicate_identity", identity)
                continue
            seen.add(identity)
            child = node.entries.get(identity)
            if child is None:
                self.refuse(node, row_path, "extra_row", identity)
            else:
                self.visit(child, row, row_path)
        for identity in node.entries:
            if identity not in seen:
                # No raw index exists for a missing row.
                self.refuse(node, path, "missing_row", identity)


def compare(census: Census, left_json: str, right_json: str) -> Result:
    """Return an internal diagnostic. Publish only Result.public_summary()."""
    wires = []
    for side, schema, text in zip(SIDES, (census.left, census.right), (left_json, right_json), strict=True):
        wire = _Wire(side, census.rules)
        wires.append(wire)
        try:
            document = _load(text)
        except _InvalidJSON as error:
            wire.refuse(schema, (), str(error))
        except (ValueError, TypeError, RecursionError):
            wire.refuse(schema, (), "invalid_json")
        else:
            wire.visit(schema, document)
    failures = [finding for wire in wires for finding in wire.findings]
    if failures:
        return Result(tuple(failures))
    left, right = wires
    for key, rule in census.rules.items():
        if rule.presence_only:
            continue
        # Check every occurrence. An absolute bar is not transitive across aliases.
        for (a_side, _, a), (b_side, b_path, b) in combinations(left.values[key] + right.values[key], 2):
            if not rule.agrees(a, b):
                side = a_side if a_side == b_side else "LR"
                exit_code = REFUSED if rule.refuse_mismatch else HOLD
                failures.append(Finding(exit_code, key.family, side, b_path, "value", key))
    return Result(tuple(failures), tuple(left.bindings + right.bindings))


def mutation_targets(census: Census, control: Result) -> Iterator[Binding]:
    """Join independent expected occurrences with the clean raw pointer map."""
    if control.exit_code != AGREE:
        raise ValueError("mutations require a clean control")
    expected = [(side, key) for side, schema in ((SIDES[0], census.left), (SIDES[1], census.right))
                for key in _registered_leaves(schema)]
    mapped = defaultdict(list)
    for binding in control.bindings:
        mapped[binding.side, binding.key].append(binding)
    if (not expected or Counter(expected) != Counter({pair: len(bindings) for pair, bindings in mapped.items()})
        or len({(binding.side, binding.path) for binding in control.bindings}) != len(expected)
        or any(census.rules[binding.key] != binding.rule for binding in control.bindings)):
        raise ValueError("mutation coverage differs from the external census")
    for pair in expected:
        yield mapped[pair].pop()
