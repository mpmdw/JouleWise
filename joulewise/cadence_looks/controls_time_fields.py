"""Blind field projection for ctl-01, using the #795 time-only lexer."""

import csv
from hashlib import sha256
import io
import re
import sys

from joulewise.hazards.smc import KEYS as SMC_KEYS


SAMPLE_BYTES = 20
HEADER_KEYS = ("k", "schema", "status", "rate_idx", "start_raw_ns", "start_real_ns", "start_mono_ns", "boot_id")
TRAILER_KEYS = ("k", "end_raw_ns", "end_mono_ns")
POLL_KEYS = ("tx", "rx", "rt", "n")
RAIL_COLUMNS = ("timestamp_s", "power_w", "source", "rail", "interval_start_s", "interval_end_s")


class TimeFieldError(ValueError):
    """A malformed or unsupported blind field."""


_TOKEN = re.compile(r"""[ \t\n\r]*(?:
     (?P<str>"(?:[^"\\\x00-\x1f]|\\(?:["\\/bfnrt]|u[0-9a-fA-F]{4}))*")
    |(?P<lit>true|false|null|NaN|Infinity|-Infinity)
    |(?P<num>-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][-+]?[0-9]+)?)
    |(?P<punct>[{}\[\]:,])
    )""", re.X)
_TAIL_WS = re.compile(r"[ \t\n\r]*\Z")
MAX_DEPTH = 64
NESTED = object()                    # a member whose value is an object or an array: never converted
EMPTY_ARRAY = object()
SKIP = object()
BOOLEAN = object()
OPAQUE_BOOLEAN = object()
STRING = object()
INTEGER = object()
INT64 = object()
NUMBER = object()
OPAQUE_INTEGER = object()
OPAQUE_NONNEGATIVE_INTEGER = object()
OPAQUE_OBJECT = object()
OPAQUE_FINITE_NUMBER = object()
OPAQUE_NONNEGATIVE_NUMBER = object()
OPAQUE_PERCENT = object()
OPAQUE_STRING = object()
OPAQUE_NONBLANK_STRING = object()
OPAQUE_STRING_OR_INTEGER = object()


class RecordFields(dict):
    """A typed record whose decoder rejects unknown fields."""


class RequiredRecordFields(RecordFields):
    """A record whose native serializer always emits every field."""


class DependentRecord(RequiredRecordFields):
    """A closed record with fields selected by a structural integer sibling."""

    def __init__(self, parameter, specialize, **fields):
        super().__init__(fields)
        self.parameter = parameter
        self.specialize = specialize


class OpaqueIndex:
    """An integer index checked against its exclusive limit without conversion."""

    def __init__(self, limit):
        self.limit = str(max(limit, 0))


class WireRecord(RecordFields):
    """A closed producer record with required and conditional members."""

    def __init__(self, required, optional=None):
        super().__init__(required, **(optional or {}))
        self.required = frozenset(required)


class ExtensionRecord(WireRecord):
    """A typed opaque record that permits producer-defined members."""


class KeyedFields:
    """A vocabulary-constrained map whose entries share one value schema."""

    def __init__(self, key_pattern, values):
        self.key_pattern = re.compile(key_pattern)
        self.values = values


class TokenForms:
    """A field whose producer has variants with distinct JSON types."""

    def __init__(self, variants):
        self.variants = variants


class Nullable:
    """A projection that also accepts JSON null."""

    def __init__(self, fields):
        self.fields = fields


class DiscardedField:
    """Validate a required or optional member and omit it from the projection."""

    def __init__(self, fields):
        self.fields = fields


class DigestFields(dict):
    """A projection paired with a digest of the object's compact JSON bytes."""


class TaggedFields:
    """Select an object's field projection by an order-independent tag."""

    def __init__(self, tag, fields):
        self.tag = tag
        self.fields = fields


class _Bad(Exception):
    pass


_ESC = {'"': '"', "\\": "\\", "/": "/", "b": "\b", "f": "\f", "n": "\n", "r": "\r", "t": "\t"}
_ESC_RE = re.compile(r'\\(?:u([0-9a-fA-F]{4})|(.))')
_NONSPACE_OR_ESCAPE = re.compile(r'[^\\\s]|' + _ESC_RE.pattern)


def _has_nonblank_text(raw):
    """Apply the typed string predicate to a token without decoding its text."""
    for match in _NONSPACE_OR_ESCAPE.finditer(raw, 1, len(raw) - 1):
        code, escape = match.groups()
        if code is not None:
            if not chr(int(code, 16)).isspace():
                return True
        elif escape not in ("t", "n", "r", "f"):
            return True
    return False


# Binary64 rounds to infinity at this midpoint, and to zero at half the
# smallest subnormal. Compare decimal spellings without converting a reading.
_OVERFLOW = (308, str(2**1024 - 2**970).rstrip("0"))
_HALF_SUBNORMAL = (-324, str(5**1075))
# The halfway point above 100 rounds to 100 (its low significand bit is even).
_PERCENT_CEILING = (2, str((100 * 2**47 + 1) * 5**47))


def _valid_opaque_number(text, *, nonnegative, ceiling=None):
    if not nonnegative and ceiling is None and len(text) < 309 and "e" not in text and "E" not in text:
        return True
    significand, _, exponent = text.lower().partition("e")
    whole, _, fraction = significand.lstrip("-").partition(".")
    digits = (whole + fraction).lstrip("0")
    if not digits:
        return True
    exponent_digits = exponent.lstrip("+-").lstrip("0")
    # Saturate exponents that are already decisive without integer parsing.
    cap = len(significand) + 400
    shift = cap if len(exponent_digits) > len(str(cap)) else int(exponent_digits or "0")
    if exponent.startswith("-"):
        shift = -shift
    magnitude = (len(digits) - len(fraction) - 1 + shift, digits.rstrip("0"))
    if nonnegative and significand.startswith("-"):
        return magnitude <= _HALF_SUBNORMAL
    return magnitude <= ceiling if ceiling is not None else magnitude < _OVERFLOW


def _unstring(raw):
    """A JSON string token's text, as json.loads gives it (escapes, and a \\u surrogate pair joined), without
    json.loads: the reader never hands any part of an energy file's line to the JSON decoder."""
    body = raw[1:-1]
    if "\\" not in body:
        return body
    out, pos = [], 0
    for m in _ESC_RE.finditer(body):
        out.append(body[pos:m.start()])
        pos = m.end()
        if m.group(1) is not None:
            out.append(chr(int(m.group(1), 16)))
        else:
            out.append(_ESC[m.group(2)])
    out.append(body[pos:])
    text = "".join(out)
    # json joins a high surrogate followed by a low one into one character
    return text.encode("utf-16", "surrogatepass").decode("utf-16", "surrogatepass") if any(
        0xD800 <= ord(c) <= 0xDFFF for c in text) else text


_LITERALS = {"true": True, "false": False, "null": None, "NaN": float("nan"), "Infinity": float("inf"),
             "-Infinity": float("-inf")}


def _convert(kind, text):
    """One scalar token's value as json.loads gives it: int for an integer literal, float otherwise."""
    if kind == "str":
        return _unstring(text)
    if kind == "lit":
        return _LITERALS[text]
    if any(c in text for c in ".eE"):
        return float(text)
    return int(text)


def _over_int_limit(text):
    """An integer literal longer than ``sys.get_int_max_str_digits()`` digits: ``json.loads`` raises ValueError on
    it (int() of the token), so the decoder keeps the line as an error line; the scanner refuses it the same way."""
    if "." in text or "e" in text or "E" in text:
        return False
    limit = sys.get_int_max_str_digits()
    return bool(limit) and len(text) - text.startswith("-") > limit


def _tokens(s):
    pos, n = 0, len(s)
    while True:
        m = _TOKEN.match(s, pos)
        if m is None or m.end() == pos:
            if _TAIL_WS.match(s, pos):
                return
            raise _Bad()
        pos = m.end()
        kind = m.lastgroup
        text = m.group(kind)
        if kind == "num" and _over_int_limit(text):
            raise _Bad()             # json.loads refuses an integer literal over the interpreter's digit limit
        yield kind, text
        if pos >= n:
            return


def _skip_value(it, first, depth, *, strict=False, finite=False):
    kind, text = first
    if kind in ("str", "lit", "num"):
        if strict and kind == "lit" and text not in ("true", "false", "null"):
            raise _Bad()
        if finite and kind == "num" and not _valid_opaque_number(text, nonnegative=False):
            raise _Bad()
        return
    if kind != "punct" or text not in "{[":
        raise _Bad()
    if depth > MAX_DEPTH:
        raise TimeFieldError("a JSON line nests deeper than the reader follows")
    close = "}" if text == "{" else "]"
    seen = set()
    nxt = next(it, None)
    if nxt == ("punct", close):
        return
    while True:
        if close == "}":
            if nxt is None or nxt[0] != "str" or next(it, None) != ("punct", ":"):
                raise _Bad()
            if strict:
                name = _unstring(nxt[1])
                if name in seen:
                    raise _Bad()
                seen.add(name)
            nxt = next(it, None)
        if nxt is None:
            raise _Bad()
        _skip_value(it, nxt, depth + 1, strict=strict, finite=finite)
        sep = next(it, None)
        if sep == ("punct", close):
            return
        if sep != ("punct", ","):
            raise _Bad()
        nxt = next(it, None)


def scan_line(s):
    """The top-level members of one JSON line as ``json.loads`` would accept it, WITHOUT converting any value:
    ``{key: (kind, raw text)}`` with kind "str", "num" or "lit", or ``{key: (NESTED, opener)}`` for an object or array.
    A repeated key keeps its last value, as ``json.loads`` does. Returns None when ``json.loads`` would refuse the
    line or its value is not a JSON object (the decoder then keeps it as an error line and reads no sample from it)."""
    it = _tokens(s)
    try:
        if next(it, None) != ("punct", "{"):
            return None
        out = {}
        nxt = next(it, None)
        if nxt == ("punct", "}"):
            members_done = True
        else:
            members_done = False
        while not members_done:
            if nxt is None or nxt[0] != "str" or next(it, None) != ("punct", ":"):
                return None
            key = _unstring(nxt[1])                    # a member NAME, never a value
            val = next(it, None)
            if val is None:
                return None
            if val[0] == "punct":
                _skip_value(it, val, 1)
                out[key] = (NESTED, val[1])
            else:
                out[key] = val
            sep = next(it, None)
            if sep == ("punct", "}"):
                break
            if sep != ("punct", ","):
                return None
            nxt = next(it, None)
        if next(it, None) is not None:                 # "Extra data"
            return None
        return out
    except _Bad:
        return None


def member(members, key):
    """The converted value of one whitelisted member: str, int, float, bool or None; NESTED for an object or
    array; KeyError when absent."""
    kind, text = members[key]
    return NESTED if kind is NESTED else _convert(kind, text)


def _kind(members):
    """The record kind: the top-level ``k`` member's string value, else None (km003c_parse.load's item.get("k"))."""
    if members is None or "k" not in members:
        return None
    v = member(members, "k")
    return v if isinstance(v, str) else None


def _pick(members, keys):
    return {k: member(members, k) for k in keys if k in members}


def _counters(text, where):
    """The 16-bit device counter of each 20-byte sample in a poll's payload, as km003c_parse.samples unpacks it
    (``bytes.fromhex`` then ``SAMPLE.iter_unpack``); the other 18 bytes of each sample are not looked at."""
    try:
        raw = bytes.fromhex(text)
    except ValueError:
        raise TimeFieldError(f"{where}: a payload that is not hex") from None
    if len(raw) % SAMPLE_BYTES:
        raise TimeFieldError(f"{where}: a payload that is not whole 20-byte samples")
    return tuple(raw[i] | (raw[i + 1] << 8) for i in range(0, len(raw), SAMPLE_BYTES))


_METER_HEADER = WireRecord(
    {"k": STRING, "schema": STRING, "status": STRING, "rate_idx": INTEGER},
    {**dict.fromkeys(("start_raw_ns", "start_real_ns", "start_mono_ns"), INT64),
     **dict.fromkeys(("reason", "model", "hardware_version", "manufacture_date",
                      "firmware_version", "firmware_date", "info_error"), Nullable(OPAQUE_STRING)),
     **dict.fromkeys(("vid", "pid", "qos", "hardware_id", "hardware_id_form"), OPAQUE_STRING),
     **dict.fromkeys(("sps", "process_id", "init_attempts", "auth_level"), OPAQUE_INTEGER),
     "poll_s": OPAQUE_FINITE_NUMBER, "boot_id": Nullable(STRING), "init_errors": [OPAQUE_STRING],
     "smc_keys": [OPAQUE_STRING], "smc_units": WireRecord(dict.fromkeys(SMC_KEYS, OPAQUE_STRING)),
     "descriptor": RequiredRecordFields.fromkeys(("bcd_device", "manufacturer", "product", "serial"),
                                                Nullable(OPAQUE_STRING))},
)
_METER_POLL = WireRecord(
    {"k": STRING, "rx": INT64, "n": INTEGER, "p": STRING},
    {"tx": INT64, "rt": INT64, "smc": WireRecord({}, {
        key: Nullable(OPAQUE_INTEGER if key in ("B0AC", "B0AV") else OPAQUE_FINITE_NUMBER)
        for key in SMC_KEYS
     }),
     "smc_err": WireRecord({}, dict.fromkeys(SMC_KEYS, OPAQUE_STRING))},
)
_METER_TRAILER = WireRecord(
    {"k": STRING},
    {**dict.fromkeys(("end_raw_ns", "end_mono_ns"), INT64),
     **dict.fromkeys(("polls", "empties", "bad", "usb_errors", "maxrss", "nvcsw", "nivcsw"), OPAQUE_INTEGER),
     **dict.fromkeys(("elapsed_s", "utime_s", "stime_s"), OPAQUE_FINITE_NUMBER),
     "stop_reason": OPAQUE_STRING},
)
_METER_ERROR = WireRecord({"k": STRING, "rx": INT64}, {"raw": OPAQUE_STRING, "usb_error": OPAQUE_STRING})
METER_FIELDS = TaggedFields("k", {"h": _METER_HEADER, "t": _METER_TRAILER, "b": _METER_POLL, "e": _METER_ERROR})
_METER_PREFIX = re.compile(r'\s*\{\s*"k"\s*:\s*"([htbe])"')


def stream_fields(payload, name):
    """One stream's time view: {"name", "header", "trailer", "first_line_header", "polls", "errors"}. ``header`` is
    the last line of kind "h" and ``trailer`` the last of kind "t" (km003c_parse.load); ``first_line_header`` is the
    first line when it is a header (rule 4's reading). ``polls`` are the kind-"b" lines in file order, each
    {"tx", "rx", "rt", "n", "seq"} with ``seq`` the payload's counters or None (no payload). Absent fields are omitted."""
    try:
        lines = payload.decode("utf-8").split("\n")
    except UnicodeError as error:
        raise TimeFieldError("invalid native stream encoding") from error
    header = trailer = first = None
    polls, errors, seen = [], 0, False
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        is_first, seen = not seen, True
        prefix = _METER_PREFIX.match(line)
        fields = METER_FIELDS.fields[prefix[1]] if prefix else METER_FIELDS
        members = project_json(line, fields, strict=True)
        kind = members["k"]
        if kind == "h":
            if header is not None or not is_first:
                raise TimeFieldError("unexpected native stream header")
            header = {key: members[key] for key in HEADER_KEYS if key in members}
            if is_first:
                first = header
        elif kind == "t":
            if trailer is not None:
                raise TimeFieldError("duplicate native stream trailer")
            trailer = {key: members[key] for key in TRAILER_KEYS if key in members}
        elif kind == "e":
            errors += 1
        elif kind == "b":
            if header is None or trailer is not None:
                raise TimeFieldError("poll outside native stream anchors")
            poll = {key: members[key] for key in POLL_KEYS if key in members}
            if members["p"]:
                poll["seq"] = _counters(members["p"], f"{name}:{number}")
            polls.append(poll)
    return {"name": name, "header": header, "trailer": trailer, "first_line_header": first,
            "polls": polls, "errors": errors}


def _probe_record(it, token, selector, depth, *, strict):
    captured = []

    def capture():
        for field_token in it:
            captured.append(field_token)
            yield field_token

    return _project(capture(), token, selector, depth, strict=strict), iter(captured)


def _project(it, token, fields, depth, *, strict):
    if depth > MAX_DEPTH:
        raise _Bad()
    if isinstance(fields, Nullable):
        if token == ("lit", "null"):
            return None
        fields = fields.fields
    if isinstance(fields, TokenForms):
        form = token[1] if token[0] == "punct" else token[0]
        if form not in fields.variants:
            raise _Bad()
        return _project(it, token, fields.variants[form], depth, strict=strict)
    if fields is EMPTY_ARRAY:
        if token != ("punct", "[") or next(it) != ("punct", "]"):
            raise _Bad()
        return []
    if fields is SKIP:
        _skip_value(it, token, depth, strict=strict, finite=strict)
        return None
    if fields is OPAQUE_OBJECT:
        if token != ("punct", "{"):
            raise _Bad()
        _skip_value(it, token, depth, strict=True, finite=True)
        return {}
        return None
    if fields in (BOOLEAN, OPAQUE_BOOLEAN):
        if token not in (("lit", "false"), ("lit", "true")):
            raise _Bad()
        return fields is BOOLEAN and token[1] == "true"
    if fields is STRING:
        if token[0] != "str":
            raise _Bad()
        return _convert(*token)
    if fields is OPAQUE_STRING_OR_INTEGER and token[0] == "str":
        return None
    if isinstance(fields, OpaqueIndex):
        kind, text = token
        if kind != "num" or not (text == "-0" or text.isascii() and text.isdecimal()):
            raise _Bad()
        digits = "0" if text == "-0" else text
        limit = fields.limit
        if (len(digits), digits) >= (len(limit), limit):
            raise _Bad()
        return 0
    if fields in (INTEGER, INT64, OPAQUE_INTEGER, OPAQUE_NONNEGATIVE_INTEGER, OPAQUE_STRING_OR_INTEGER):
        if token[0] != "num" or any(marker in token[1] for marker in ".eE"):
            raise _Bad()
        if fields is OPAQUE_NONNEGATIVE_INTEGER and token[1].startswith("-") and token[1] != "-0":
            raise _Bad()
        if fields in (INTEGER, INT64):
            value = _convert(*token)
            if fields is INT64 and not -(2**63) <= value < 2**63:
                raise _Bad()
            return value
        return 0
    if fields is NUMBER:
        if token[0] != "num" or not _valid_opaque_number(token[1], nonnegative=False):
            raise _Bad()
        return float(_convert(*token))
    if fields in (OPAQUE_FINITE_NUMBER, OPAQUE_NONNEGATIVE_NUMBER, OPAQUE_PERCENT):
        if token[0] != "num" or not _valid_opaque_number(
            token[1], nonnegative=fields in (OPAQUE_NONNEGATIVE_NUMBER, OPAQUE_PERCENT),
            ceiling=_PERCENT_CEILING if fields is OPAQUE_PERCENT else None,
        ):
            raise _Bad()
        return 0
    if fields is OPAQUE_STRING:
        if token[0] != "str":
            raise _Bad()
        return "" if token[1] == '""' else "opaque"
    if fields is OPAQUE_NONBLANK_STRING:
        if token[0] != "str" or not _has_nonblank_text(token[1]):
            raise _Bad()
        return "opaque"
    if isinstance(fields, TaggedFields):
        view, replay = _probe_record(it, token, {fields.tag: STRING}, depth, strict=strict)
        projection = fields.fields.get(view.get(fields.tag))
        if projection is None:
            raise _Bad()
        return _project(replay, token, projection, depth, strict=strict)
    if isinstance(fields, DependentRecord):
        selector, replay = _probe_record(it, token, {fields.parameter: INTEGER}, depth, strict=strict)
        if fields.parameter not in selector:
            raise _Bad()
        projection = RequiredRecordFields(fields, **fields.specialize(selector[fields.parameter]))
        return _project(replay, token, projection, depth, strict=strict)
    if isinstance(fields, DigestFields):
        digest = sha256()

        def capture_tokens():
            for member_token in it:
                digest.update(member_token[1].encode("utf-8"))
                yield member_token

        digest.update(token[1].encode("utf-8"))
        view = _project(capture_tokens(), token, dict(fields), depth, strict=strict)
        return view, digest.hexdigest()
    if (token == ("lit", "null") and isinstance(fields, RecordFields)
            and not isinstance(fields, (RequiredRecordFields, WireRecord))):
        return None
    if fields is None:
        kind, value = token
        if kind not in ("str", "num", "lit"):
            raise _Bad()
        if strict and kind == "lit" and value not in ("true", "false", "null"):
            raise _Bad()
        return _convert(kind, value)
    if isinstance(fields, list):
        if token != ("punct", "["):
            raise _Bad()
        result = []
        item = next(it)
        if item == ("punct", "]"):
            return result
        while True:
            result.append(_project(it, item, fields[0], depth + 1, strict=strict))
            separator = next(it)
            if separator == ("punct", "]"):
                return result
            if separator != ("punct", ","):
                raise _Bad()
            item = next(it)
    if token != ("punct", "{"):
        raise _Bad()
    result, seen = {}, set()
    extension = isinstance(fields, ExtensionRecord)
    required = fields.keys() if isinstance(fields, RequiredRecordFields) else getattr(fields, "required", ())
    item = next(it)
    if item == ("punct", "}"):
        if required:
            raise _Bad()
        return result
    while True:
        if item[0] != "str" or next(it) != ("punct", ":"):
            raise _Bad()
        name = _unstring(item[1])
        if name in seen:
            raise _Bad()
        seen.add(name)
        value = next(it)
        if isinstance(fields, KeyedFields):
            if not fields.key_pattern.fullmatch(name):
                raise _Bad()
            result[name] = _project(it, value, fields.values, depth + 1, strict=strict)
        elif name in fields:
            field = fields[name]
            discarded = isinstance(field, DiscardedField)
            projected = _project(it, value, field.fields if discarded else field, depth + 1, strict=strict)
            if not extension and not discarded:
                result[name] = projected
        elif extension:
            _skip_value(it, value, depth + 1, strict=True, finite=True)
        elif isinstance(fields, RecordFields):
            raise _Bad()
        else:
            _skip_value(it, value, depth + 1, strict=strict)
        separator = next(it)
        if separator == ("punct", "}"):
            if required and not required <= seen:
                raise _Bad()
            return result
        if separator != ("punct", ","):
            raise _Bad()
        item = next(it)


def project_json(payload, fields, *, strict=False):
    """Convert only scalars on the allowlist; lex past every other value."""
    try:
        tokens = _tokens(payload if isinstance(payload, str) else payload.decode("utf-8"))
        value = _project(tokens, next(tokens), fields, 0, strict=strict)
        if next(tokens, None) is not None:
            raise _Bad()
        return value
    except (_Bad, StopIteration, UnicodeError) as error:
        raise TimeFieldError("invalid structural projection") from error


def rail_rows(payload):
    """Lex the native rail CSV without interpreting its measurement field."""
    try:
        with io.StringIO(payload.decode("utf-8"), newline="") as stream:
            rows = csv.reader(stream, strict=True)
            if tuple(next(rows, ())) != RAIL_COLUMNS:
                raise TimeFieldError("wrong native rail columns")
            for row in rows:
                if len(row) != len(RAIL_COLUMNS):
                    raise TimeFieldError("wrong native rail row width")
                token = _TOKEN.fullmatch(row[1])
                if (token is None or token.lastgroup != "num"
                        or not _valid_opaque_number(token.group("num"), nonnegative=False)):
                    raise TimeFieldError("invalid native rail reading token")
                yield row
    except (UnicodeError, csv.Error) as error:
        raise TimeFieldError("invalid native rail CSV") from error
