"""Compare two JSON reports against separately bound, external output schemas.

The caller compiles the two wire schemas from the input design before reading
reports. This module has no producer, analysis or release authority.
"""

from collections import Counter, defaultdict
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from fractions import Fraction
from functools import cache
from itertools import combinations
import json
import math
from pathlib import Path
import re
from types import MappingProxyType

AGREE, HOLD, REFUSED = 0, 1, 2
SIDES = ("L", "R")
UNSET = object()
IDENTITY_TYPES = (str, int)
LEAF_TYPES = (str, int, float, bool, type(None))
WirePath = tuple[str | int, ...]
BARS_PATH = Path(__file__).resolve().parents[1] / "configs/analysis/v4/c1_comparator_bars.json"


@cache
def _bars():
    def freeze(value):
        if isinstance(value, dict):
            return MappingProxyType({key: freeze(child) for key, child in value.items()})
        return value

    return freeze(_load(BARS_PATH.read_text(encoding="utf-8")))


@dataclass(frozen=True)
class Key:
    family: str
    row: WirePath
    leaf: str


METADATA_AUC = Key("metadata_auc", (), "value")


@dataclass(frozen=True)
class Rule:
    kind: type
    unit: str
    source: str
    expected: object = UNSET
    numeric_class: str | None = None
    presence_only: bool = False
    pattern: str | None = None
    refuse_mismatch: bool = False
    expected_hold: bool = False
    sides: tuple[str, ...] = SIDES
    alias_reason: str = ""

    def __post_init__(self):
        if self.kind not in LEAF_TYPES or not self.unit or not self.source:
            raise ValueError("a rule needs a scalar type, unit and source")
        if self.expected is not UNSET and not self.valid_type(self.expected):
            raise ValueError("invalid expected literal")
        if self.numeric_class is not None and (self.kind is not float or self.presence_only):
            raise ValueError("a numeric rule needs a binary64 engine leaf")
        if self.pattern is not None and self.kind is not str:
            raise ValueError("only string leaves can have a pattern")
        if self.pattern is not None:
            re.compile(self.pattern)
        if self.sides != SIDES and (
            (not self.presence_only and self.expected is UNSET) or self.sides not in (("L",), ("R",))
        ):
            raise ValueError("comparison requires both sides")
        if self.expected_hold and self.expected is UNSET:
            raise ValueError("a population check needs an expected value")

    def valid_type(self, value):
        return type(value) is self.kind and (self.kind is not float or math.isfinite(value))

    @property
    def bar(self):
        return _bars()["numeric_families"].get(self.numeric_class)

    def agrees(self, left, right):
        if self.numeric_class in ("N1", "N6"):
            if isinstance(left, Fraction) and isinstance(right, Fraction):
                return left == right
            # float.hex retains the sign of zero.
            return float(left).hex() == float(right).hex()
        if self.numeric_class is not None:
            bar = self.bar
            if bar["operator"] == "relative":
                return abs(left - right) <= bar["tolerance"] * max(abs(left), abs(right))
            return abs(left - right) <= bar["tolerance"]
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
    entries: Mapping[WirePath, Object]
    empty_reason: str = ""

    def __post_init__(self):
        object.__setattr__(self, "entries", MappingProxyType(dict(self.entries)))


Node = Key | Object | Sequence | Rows


@dataclass(frozen=True)
class Closure:
    whole: Key
    phase_sum: Key
    absolute_error: Key
    relative_error: Key


@dataclass(frozen=True)
class AucNullReason:
    key: Key
    allowed: tuple[str, ...]


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
    closures: tuple[Closure, ...] = ()
    auc_population: Object | Rows | None = None
    auc_null_reason: AucNullReason | None = None

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
        if METADATA_AUC in rules:
            self._check_auc(counts, rules)
        elif self.auc_population is not None or self.auc_null_reason is not None:
            raise ValueError("AUC checks without AUC")
        for closure in self.closures:
            base = (closure.whole, closure.phase_sum)
            remainders = (closure.absolute_error, closure.relative_error)
            if (len(set(base + remainders)) != 4
                or any(counts[side][key] != 1 for side in SIDES for key in base + remainders)
                or any(rules[key].numeric_class not in ("N2", "N2d") for key in base)
                or rules[closure.absolute_error].kind is not float
                or rules[closure.relative_error].kind not in (float, type(None))
                or any(rules[key].numeric_class is not None for key in remainders)):
                raise ValueError("invalid closure binding")
        object.__setattr__(self, "rules", MappingProxyType(rules))

    def _check_auc(self, counts, rules):
        rule = rules[METADATA_AUC]
        if (tuple(counts[side][METADATA_AUC] for side in SIDES) != (1, 1)
            or rule.kind not in (float, type(None)) or rule.numeric_class is not None
            or rule.expected is not UNSET or rule.presence_only):
            raise ValueError("AUC exemption must bind exactly one named value on each side")
        population = self.auc_population
        if not isinstance(population, (Object, Rows)) or not _are_siblings(self.left, METADATA_AUC, population):
            raise ValueError("AUC requires an independent engine fold population")
        for key in _registered_leaves(population):
            if (counts["L"][key] != 1 or counts["R"][key] or rules[key].expected is UNSET
                or rules[key].numeric_class is not None or rules[key].kind not in IDENTITY_TYPES):
                raise ValueError("fold identities and counts must be bound engine-side exactly")
        reason = self.auc_null_reason
        if rule.kind is float:
            if reason is not None:
                raise ValueError("unexpected AUC null reason")
        elif (reason is None or counts["L"][reason.key] != 1 or counts["R"][reason.key]
              or rules[reason.key].kind is not str or rules[reason.key].expected not in reason.allowed
              or rules[reason.key].expected_hold
              or not _are_siblings(self.left, METADATA_AUC, reason.key)):
            raise ValueError("null AUC requires a bound sibling reason from the closed list")


def _are_siblings(node, a, b):
    if isinstance(node, Object):
        children = tuple(node.fields.values())
        if a in children and b in children:
            return True
    elif isinstance(node, Sequence):
        children = node.entries
    elif isinstance(node, Rows):
        children = tuple(node.entries.values())
    else:
        return False
    return any(_are_siblings(child, a, b) for child in children)


def _components(side, key, rule):
    if side == "R":
        if key == METADATA_AUC:
            return tuple(_bars()["metadata_auc"]["recompute_marker"])
        if rule.numeric_class == "N1":
            return (0, 1)
    return (None,)


def pointer(path: WirePath) -> str:
    return "".join("/" + str(part).replace("~", "~0").replace("/", "~1") for part in path)


@dataclass(frozen=True)
class Finding:
    exit_code: int
    family: str
    side: str
    path: WirePath
    code: str
    key: Key | None = None
    identity: WirePath | None = None


@dataclass(frozen=True)
class Binding:
    side: str
    path: WirePath
    key: Key
    rule: Rule
    component: str | int | None = None


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
    def __init__(self, side, census):
        self.side = side
        self.rules = census.rules
        self.closure_keys = {key for closure in census.closures
                             for key in (closure.absolute_error, closure.relative_error)}
        self.findings = []
        self.bindings = []
        self.values = defaultdict(list)

    def refuse(self, node, path, code, identity=None):
        key = node if isinstance(node, Key) else None
        self.findings.append(Finding(REFUSED, node.family, self.side, path, code, key, identity))

    def leaf(self, key, value, path):
        rule = self.rules[key]
        operand = value
        if key == METADATA_AUC:
            if self.side == "R":
                if value != _bars()["metadata_auc"]["recompute_marker"]:
                    self.refuse(key, path, "auc_marker")
                    return
            elif not (value is None if rule.kind is type(None)
                      else type(value) in (int, float) and 0 <= value <= 1):
                self.refuse(key, path, "auc_shape")
                return
        elif rule.kind is float and (
            (rule.numeric_class is not None and rule.bar is None)
            or (rule.numeric_class is None and rule.expected is UNSET and key not in self.closure_keys)
        ):
            self.refuse(key, path, "unbound_numeric")
            return
        elif self.side == "R" and rule.numeric_class in ("N1", "N6"):
            try:
                operand = _rational(value) if rule.numeric_class == "N1" else _nanoseconds(value)
                float(operand)  # Refuse a quotient outside binary64.
            except (ValueError, OverflowError):
                self.refuse(key, path, "numeric_wire")
                return
        elif not rule.valid_type(value):
            self.refuse(key, path, "type")
            return
        if rule.expected is not UNSET and not self.expected_value(rule, operand):
            if rule.expected_hold:
                self.findings.append(Finding(HOLD, key.family, self.side, path, "population", key))
            else:
                self.refuse(key, path, "state")
            return
        if rule.pattern is not None and re.fullmatch(rule.pattern, value) is None:
            self.refuse(key, path, "shape")
            return
        for component in _components(self.side, key, rule):
            raw_path = path if component is None else path + (component,)
            self.bindings.append(Binding(self.side, raw_path, key, rule, component))
        self.values[key].append((self.side, path, operand))

    def expected_value(self, rule, operand):
        if rule.numeric_class in ("N1", "N6"):
            return rule.agrees(operand, rule.expected)
        return operand == rule.expected

    def visit(self, node, value, path=()):
        if isinstance(node, Key):
            self.leaf(node, value, path)
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

    def check_closure(self, closure):
        whole = self.values[closure.whole][0][2]
        phase_sum = self.values[closure.phase_sum][0][2]
        absolute = abs(phase_sum - whole)
        relative = None if whole == 0.0 else absolute / abs(whole)
        for key, expected, bar in (
            (closure.absolute_error, absolute, _bars()["closure"]["absolute_error_j"]),
            (closure.relative_error, relative, _bars()["closure"]["relative_error"]),
        ):
            _, path, reported = self.values[key][0]
            if reported is None or expected is None:
                agrees = reported is expected
            else:
                agrees = abs(reported - expected) <= bar
            if not agrees:
                self.refuse(key, path, "closure")


def _rational(value):
    if (type(value) is not list or len(value) != 2 or any(type(n) is not int for n in value)
        or value[1] <= 0 or math.gcd(*value) != 1):
        raise ValueError("expected a reduced [numerator, positive denominator]")
    return Fraction(*value)


def _nanoseconds(value):
    if type(value) is not int:
        raise ValueError("expected integer nanoseconds")
    return Fraction(value, 10**9)


def format_sentence_figure(kind, value):
    """Format one figure. The branch and direction words come from the owner."""
    if kind == "count" and type(value) is int:
        return str(value)
    if kind == "one_decimal" and type(value) is float and math.isfinite(value):
        rendered = format(value, ".1f")
        return "0.0" if rendered == "-0.0" else rendered
    if kind == "p" and isinstance(value, Fraction) and 0 <= value <= 1:
        if value < Fraction(1, 10**4):
            return "< 0.0001"
        units, remainder = divmod(value.numerator * 10**4, value.denominator)
        twice = remainder * 2
        if twice > value.denominator or (twice == value.denominator and units % 2):
            units += 1
        return f"{units // 10**4}.{units % 10**4:04d}"
    raise ValueError("invalid sentence figure")


def compare(census: Census, left_json: str, right_json: str) -> Result:
    """Return an internal diagnostic. Publish only Result.public_summary()."""
    wires = []
    for side, schema, text in zip(SIDES, (census.left, census.right), (left_json, right_json), strict=True):
        wire = _Wire(side, census)
        wires.append(wire)
        try:
            document = _load(text)
        except _InvalidJSON as error:
            wire.refuse(schema, (), str(error))
        except (ValueError, TypeError, RecursionError):
            wire.refuse(schema, (), "invalid_json")
        else:
            wire.visit(schema, document)
            for closure in census.closures:
                if all(wire.values.get(key) for key in
                       (closure.whole, closure.phase_sum, closure.absolute_error, closure.relative_error)):
                    wire.check_closure(closure)
    failures = [finding for wire in wires for finding in wire.findings]
    if any(finding.exit_code == REFUSED for finding in failures):
        return Result(tuple(failures))
    left, right = wires
    for key, rule in census.rules.items():
        if key == METADATA_AUC or key in left.closure_keys or rule.presence_only or rule.sides != SIDES:
            continue
        if not left.values.get(key) or not right.values.get(key):
            continue  # A known population differed and already generated HOLD.
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
    expected = [(side, key, component)
                for side, schema in zip(SIDES, (census.left, census.right), strict=True)
                for key in _registered_leaves(schema)
                for component in _components(side, key, census.rules[key])]
    mapped = defaultdict(list)
    for binding in control.bindings:
        mapped[binding.side, binding.key, binding.component].append(binding)
    if (not expected or Counter(expected) != Counter({pair: len(bindings) for pair, bindings in mapped.items()})
        or len({(binding.side, binding.path) for binding in control.bindings}) != len(expected)
        or any(census.rules[binding.key] != binding.rule for binding in control.bindings)):
        raise ValueError("mutation coverage differs from the external census")
    for pair in expected:
        yield mapped[pair].pop()
