"""Shared campaign-provenance schema and authentication primitives.

The v2 attestation is an anti-malformation discriminator: it proves that the
campaign writer emitted a particular raw manifest snapshot.  It is not an
anti-tamper signature; a coordinated rewrite of both the manifest and its
external log can recreate the evidence.  Claim-path tamper resistance remains
the separately rechecked source-manifest hashes carried by verdict provenance.

The shared authentication predicate has two named aggregation policies.
``load_authenticated_campaign_manifest`` performs pointwise dereference for a
pinned-descriptor verifier.  ``load_authenticated_campaign_catalog`` performs
all-or-nothing enumeration for consumers whose inputs are the complete catalog.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

from joulewise.authentication_io import read_authentication_input

CAMPAIGN_PROVENANCE_SCHEMA_V1 = "joulewise.campaign_provenance.v1"
CAMPAIGN_PROVENANCE_SCHEMA_V2 = "joulewise.campaign_provenance.v2"
CAMPAIGN_PROVENANCE_SCHEMAS = frozenset(
    {CAMPAIGN_PROVENANCE_SCHEMA_V1, CAMPAIGN_PROVENANCE_SCHEMA_V2}
)
CAMPAIGN_PROVENANCE_OUTCOMES = frozenset(
    {"usable", "failed", "incomplete", "waived"}
)
CAMPAIGN_PROVENANCE_ATTESTATION_SCHEMA = (
    "joulewise.campaign_provenance_attestation.v1"
)
CAMPAIGN_PROVENANCE_ATTESTATION_RECORD_TYPE = (
    "campaign_provenance_attestation"
)
CAMPAIGN_PROVENANCE_WRITER_PATH_PATTERN = (
    r"campaign_manifests/[A-Za-z0-9][A-Za-z0-9._-]{0,250}\.json"
)


@dataclass(frozen=True)
class AuthenticatedCampaignManifest:
    """One shape-valid, and for v2 externally authenticated, manifest."""

    path: Path
    raw_bytes: bytes
    value: Mapping[str, Any]


def campaign_manifest_member_shape_valid(
    member: object, schema_version: object
) -> bool:
    """Validate the execution/outcome wire shared by every catalog reader."""

    if not isinstance(member, Mapping):
        return False
    execution = member.get("execution")
    bundle_ids = member.get("bundle_ids")
    if (
        schema_version not in CAMPAIGN_PROVENANCE_SCHEMAS
        or execution not in {"invoked", "existing", "blocked_before_invoke"}
        or not isinstance(member.get("run_id"), str)
        or not member["run_id"]
        or not isinstance(bundle_ids, list)
        or not bundle_ids
        or any(
            not isinstance(bundle_id, str) or not bundle_id
            for bundle_id in bundle_ids
        )
    ):
        return False
    if execution == "existing":
        config = member.get("config")
        if not isinstance(config, str) or not config:
            return False
        if schema_version == CAMPAIGN_PROVENANCE_SCHEMA_V2:
            return member.get("outcome") in CAMPAIGN_PROVENANCE_OUTCOMES
        return "outcome" not in member
    return "outcome" not in member


_PREFIX_COMPLETE = "complete"
_PREFIX_INCOMPLETE = "incomplete"
_PREFIX_INVALID = "invalid"
_JSON_SIMPLE_ESCAPES = frozenset('"\\bfnrt')
_JSON_LOWER_HEX = frozenset("0123456789abcdef")
_JSON_SIMPLE_ESCAPE_VALUES = {
    '"': '"',
    "\\": "\\",
    "b": "\b",
    "f": "\f",
    "n": "\n",
    "r": "\r",
    "t": "\t",
}
_JSON_UNICODE_ESCAPE_RANGES = (
    (0x00, 0x07),
    (0x0B, 0x0B),
    (0x0E, 0x1F),
    (0x7F, 0xFFFF),
)
_HIGH_SURROGATE_RANGE = (0xD800, 0xDBFF)
_LOW_SURROGATE_RANGE = (0xDC00, 0xDFFF)
_UNICODE_MAX = 0x10FFFF

# D-105 deliberately specifies a decidable superset rather than the image of
# CPython's shortest-representation algorithm.  These are the observable
# structural bounds of json.dumps float spellings: fixed notation covers
# decimal exponents -4 through 15, while scientific notation has one normalized
# coefficient digit and a signed exponent padded to at least two and at most
# three digits.  The superset does not try to decide which digit sequences are
# shortest round trips.
_FLOAT_FIXED_MIN_EXPONENT = -4
_FLOAT_FIXED_MAX_EXPONENT = 15
_FLOAT_EXPONENT_MAX_DIGITS = 3


def _writer_emits_unicode_escape(codepoint: int) -> bool:
    """Match the escapes emitted by ``ensure_ascii=True`` exactly."""

    return (
        codepoint < 0x20
        and codepoint not in {0x08, 0x09, 0x0A, 0x0C, 0x0D}
    ) or codepoint >= 0x7F


def _unicode_escape_prefix_can_complete(digits: str) -> bool:
    return _unicode_escape_prefix_max_codepoint(digits) is not None


def _interval_maximum(
    low: int, high: int, ranges: Sequence[tuple[int, int]]
) -> int | None:
    candidates = [
        min(high, range_high)
        for range_low, range_high in ranges
        if low <= range_high and high >= range_low
    ]
    return max(candidates) if candidates else None


def _surrogate_pair_codepoint(high: int, low: int) -> int:
    return (
        0x10000
        + ((high - _HIGH_SURROGATE_RANGE[0]) << 10)
        + (low - _LOW_SURROGATE_RANGE[0])
    )


def _unicode_escape_prefix_max_codepoint(
    digits: str, *, preceding_high_surrogate: int | None = None
) -> int | None:
    """Return the greatest scalar possible after an unfinished ``\\u``.

    The hexadecimal prefix defines a closed code-unit interval.  A high
    surrogate can begin a second escape, so its interval is lifted through the
    surrogate-pair arithmetic before key-order feasibility is decided.
    """

    remaining = 4 - len(digits)
    low = int(digits + ("0" * remaining), 16)
    high = int(digits + ("f" * remaining), 16)
    emitted_maximum = _interval_maximum(
        low, high, _JSON_UNICODE_ESCAPE_RANGES
    )
    if preceding_high_surrogate is not None:
        low_surrogate_maximum = _interval_maximum(
            low, high, (_LOW_SURROGATE_RANGE,)
        )
        paired_maximum = (
            _surrogate_pair_codepoint(
                preceding_high_surrogate, low_surrogate_maximum
            )
            if low_surrogate_maximum is not None
            else None
        )
        candidates = [preceding_high_surrogate]
        if paired_maximum is not None:
            candidates.append(paired_maximum)
        return max(candidates)
    high_surrogate_maximum = _interval_maximum(
        low, high, (_HIGH_SURROGATE_RANGE,)
    )
    paired_maximum = (
        _surrogate_pair_codepoint(
            high_surrogate_maximum, _LOW_SURROGATE_RANGE[1]
        )
        if high_surrogate_maximum is not None
        else None
    )
    candidates = [
        candidate
        for candidate in (emitted_maximum, paired_maximum)
        if candidate is not None
    ]
    return max(candidates) if candidates else None


def _canonical_number(text: str) -> bool:
    try:
        value = json.loads(text)
    except (ValueError, json.JSONDecodeError):
        return False
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and json.dumps(value) == text
    )


def _scientific_exponent_can_complete(sign: str, digits: str) -> bool:
    if not digits:
        return True
    if not digits.isdigit() or len(digits) > _FLOAT_EXPONENT_MAX_DIGITS:
        return False
    if len(digits) == 1:
        # A positive zero prefix can reach only +00..+09, all inside the
        # fixed-notation window.  Every other one-digit prefix can reach an
        # admitted two-digit exponent.
        return sign == "-" or digits != "0"
    if digits[0] == "0":
        return sign == "-" and int(digits) >= -_FLOAT_FIXED_MIN_EXPONENT + 1
    # A two-digit value still inside the fixed window can extend to three
    # digits; every other nonzero-leading two- or three-digit value is a
    # complete superset exponent.
    return True


def _scientific_coefficient(coefficient: str) -> bool:
    if not coefficient or coefficient[0] not in "123456789":
        return False
    if len(coefficient) == 1:
        return True
    if coefficient[1:2] != ".":
        return False
    fraction = coefficient[2:]
    return bool(fraction) and fraction.isdigit() and not fraction.endswith("0")


def _documented_float_superset_prefix(text: str) -> bool:
    """Recognize a complete spelling or prefix in D-105's float superset.

    The language preserves the writer's fixed/scientific notation boundary,
    normalized scientific coefficient, and exponent padding.  Coefficient
    digits remain a superset of the shortest-round-trip image by design.
    """

    unsigned = text[1:] if text.startswith("-") else text
    if not unsigned:
        return text == "-"
    if unsigned[0] not in "0123456789":
        return False

    if "e" in unsigned:
        if unsigned.count("e") != 1:
            return False
        coefficient, exponent = unsigned.split("e", 1)
        if not _scientific_coefficient(coefficient):
            return False
        if not exponent:
            return True
        if exponent[0] not in "+-":
            return False
        return _scientific_exponent_can_complete(exponent[0], exponent[1:])

    if unsigned.startswith("0"):
        if unsigned == "0":
            return True
        if not unsigned.startswith("0."):
            return False
        fraction = unsigned[2:]
        if not fraction:
            return True
        if not fraction.isdigit():
            return False
        first_nonzero = next(
            (index for index, digit in enumerate(fraction, start=1) if digit != "0"),
            None,
        )
        if first_nonzero is None:
            return len(fraction) <= -_FLOAT_FIXED_MIN_EXPONENT - 1
        return first_nonzero <= -_FLOAT_FIXED_MIN_EXPONENT

    integer, dot, fraction = unsigned.partition(".")
    if not integer.isdigit() or integer[0] == "0":
        return False
    if not dot:
        return True
    if len(integer) > _FLOAT_FIXED_MAX_EXPONENT + 1:
        return False
    return not fraction or fraction.isdigit()


@dataclass(frozen=True)
class _IncompleteStringPrefix:
    decoded_alternatives: tuple[str, ...]
    next_codepoint_maximum: int | None


@dataclass(frozen=True)
class _CompleteWriterString:
    decoded_alternatives: tuple[str, ...]


def _key_prefix_can_exceed(
    prefix: _IncompleteStringPrefix, previous: str
) -> bool:
    """Return whether some completion of ``prefix`` can sort after ``previous``."""

    for decoded in prefix.decoded_alternatives:
        for current_character, previous_character in zip(decoded, previous):
            if current_character != previous_character:
                break
        else:
            if len(decoded) >= len(previous):
                # Equality can be broken by extending the unfinished key.
                return True
            if prefix.next_codepoint_maximum is None:
                # The raw prefix ends at a character boundary. Reproducing the
                # rest of ``previous`` and adding one character is feasible.
                return True
            if prefix.next_codepoint_maximum >= ord(previous[len(decoded)]):
                return True
            continue
        if current_character > previous_character:
            return True
    return False


def _writer_string_alternatives(token: str) -> tuple[str, ...]:
    """Decode every Python string that ``json.dumps`` can spell as ``token``.

    A serialized high/low surrogate pair is ambiguous: it can originate from
    one non-BMP scalar or from two literal surrogate code units. Python sorts
    mapping keys before serialization, so both originals remain live until
    key-order feasibility has been decided.
    """

    units: list[str] = []
    index = 1
    while index < len(token) - 1:
        character = token[index]
        if character != "\\":
            units.append(character)
            index += 1
            continue
        escape = token[index + 1]
        if escape in _JSON_SIMPLE_ESCAPE_VALUES:
            units.append(_JSON_SIMPLE_ESCAPE_VALUES[escape])
            index += 2
            continue
        assert escape == "u"
        units.append(chr(int(token[index + 2 : index + 6], 16)))
        index += 6

    alternatives = {""}
    index = 0
    while index < len(units):
        unit = ord(units[index])
        if (
            _HIGH_SURROGATE_RANGE[0] <= unit <= _HIGH_SURROGATE_RANGE[1]
            and index + 1 < len(units)
            and _LOW_SURROGATE_RANGE[0]
            <= ord(units[index + 1])
            <= _LOW_SURROGATE_RANGE[1]
        ):
            low = ord(units[index + 1])
            alternatives = {
                candidate + suffix
                for candidate in alternatives
                for suffix in (
                    chr(_surrogate_pair_codepoint(unit, low)),
                    units[index] + units[index + 1],
                )
            }
            index += 2
            continue
        alternatives = {candidate + units[index] for candidate in alternatives}
        index += 1
    return tuple(sorted(alternatives))


def _decode_incomplete_writer_string(token: str) -> _IncompleteStringPrefix:
    """Decode the fixed part of a validated unfinished writer string.

    The return value separates fixed decoded characters from the greatest
    feasible code point at the first unfinished escape.  This is sufficient
    for an exact existential lexicographic comparison: later characters cannot
    change an earlier unequal position.
    """

    decoded = {""}
    pending_high_surrogate: int | None = None
    index = 1  # opening quote

    def flush_pending_high() -> None:
        nonlocal decoded, pending_high_surrogate
        if pending_high_surrogate is not None:
            decoded = {
                candidate + chr(pending_high_surrogate) for candidate in decoded
            }
            pending_high_surrogate = None

    def append_character(character: str) -> None:
        nonlocal decoded
        decoded = {candidate + character for candidate in decoded}

    while index < len(token):
        character = token[index]
        if character != "\\":
            flush_pending_high()
            append_character(character)
            index += 1
            continue
        if index + 1 == len(token):
            maximum = (
                _surrogate_pair_codepoint(
                    pending_high_surrogate, _LOW_SURROGATE_RANGE[1]
                )
                if pending_high_surrogate is not None
                else _UNICODE_MAX
            )
            return _IncompleteStringPrefix(tuple(sorted(decoded)), maximum)
        escape = token[index + 1]
        if escape in _JSON_SIMPLE_ESCAPE_VALUES:
            flush_pending_high()
            append_character(_JSON_SIMPLE_ESCAPE_VALUES[escape])
            index += 2
            continue
        assert escape == "u"
        digits = token[index + 2 : index + 6]
        if len(digits) < 4:
            maximum = _unicode_escape_prefix_max_codepoint(
                digits, preceding_high_surrogate=pending_high_surrogate
            )
            assert maximum is not None
            return _IncompleteStringPrefix(tuple(sorted(decoded)), maximum)
        unit = int(digits, 16)
        index += 6
        if pending_high_surrogate is not None:
            if _LOW_SURROGATE_RANGE[0] <= unit <= _LOW_SURROGATE_RANGE[1]:
                combined = chr(
                    _surrogate_pair_codepoint(pending_high_surrogate, unit)
                )
                separate = chr(pending_high_surrogate) + chr(unit)
                decoded = {
                    candidate + suffix
                    for candidate in decoded
                    for suffix in (combined, separate)
                }
                pending_high_surrogate = None
                continue
            flush_pending_high()
        if _HIGH_SURROGATE_RANGE[0] <= unit <= _HIGH_SURROGATE_RANGE[1]:
            pending_high_surrogate = unit
        else:
            append_character(chr(unit))

    if pending_high_surrogate is not None:
        return _IncompleteStringPrefix(
            tuple(sorted(decoded)),
            _surrogate_pair_codepoint(
                pending_high_surrogate, _LOW_SURROGATE_RANGE[1]
            ),
        )
    return _IncompleteStringPrefix(tuple(sorted(decoded)), None)


class _CanonicalWriterPrefixRecognizer:
    """Incrementally recognize proper prefixes of the writer's JSON grammar."""

    def __init__(self, text: str) -> None:
        self.text = text
        self.index = 0

    def recognizes_proper_prefix(self) -> bool:
        if not self.text.startswith("{"):
            return False
        status = self._parse_object()
        return status == _PREFIX_INCOMPLETE and self.index == len(self.text)

    def _expect(self, token: str) -> str:
        remaining = self.text[self.index :]
        if remaining.startswith(token):
            self.index += len(token)
            return _PREFIX_COMPLETE
        if token.startswith(remaining):
            self.index = len(self.text)
            return _PREFIX_INCOMPLETE
        return _PREFIX_INVALID

    def _parse_object(self) -> str:
        self.index += 1  # ``{`` was selected by the caller.
        if self.index == len(self.text):
            return _PREFIX_INCOMPLETE
        if self.text[self.index] == "}":
            self.index += 1
            return _PREFIX_COMPLETE
        previous_keys: tuple[str, ...] | None = None
        while True:
            if self.text[self.index] != '"':
                return _PREFIX_INVALID
            status, key = self._parse_string()
            if status == _PREFIX_INCOMPLETE:
                if (
                    previous_keys is not None
                    and isinstance(key, _IncompleteStringPrefix)
                    and not any(
                        _key_prefix_can_exceed(key, previous)
                        for previous in previous_keys
                    )
                ):
                    return _PREFIX_INVALID
                return status
            if status != _PREFIX_COMPLETE or not isinstance(
                key, _CompleteWriterString
            ):
                return status
            if previous_keys is None:
                previous_keys = key.decoded_alternatives
            else:
                previous_keys = tuple(
                    current
                    for current in key.decoded_alternatives
                    if any(previous < current for previous in previous_keys)
                )
                if not previous_keys:
                    return _PREFIX_INVALID
            status = self._expect(": ")
            if status != _PREFIX_COMPLETE:
                return status
            status = self._parse_value()
            if status != _PREFIX_COMPLETE:
                return status
            if self.index == len(self.text):
                return _PREFIX_INCOMPLETE
            if self.text[self.index] == "}":
                self.index += 1
                return _PREFIX_COMPLETE
            status = self._expect(", ")
            if status != _PREFIX_COMPLETE:
                return status
            if self.index == len(self.text):
                return _PREFIX_INCOMPLETE

    def _parse_array(self) -> str:
        self.index += 1  # ``[`` was selected by the caller.
        if self.index == len(self.text):
            return _PREFIX_INCOMPLETE
        if self.text[self.index] == "]":
            self.index += 1
            return _PREFIX_COMPLETE
        while True:
            status = self._parse_value()
            if status != _PREFIX_COMPLETE:
                return status
            if self.index == len(self.text):
                return _PREFIX_INCOMPLETE
            if self.text[self.index] == "]":
                self.index += 1
                return _PREFIX_COMPLETE
            status = self._expect(", ")
            if status != _PREFIX_COMPLETE:
                return status
            if self.index == len(self.text):
                return _PREFIX_INCOMPLETE

    def _parse_value(self) -> str:
        if self.index == len(self.text):
            return _PREFIX_INCOMPLETE
        character = self.text[self.index]
        if character == "{":
            return self._parse_object()
        if character == "[":
            return self._parse_array()
        if character == '"':
            status, _value = self._parse_string()
            return status
        for literal in ("true", "false", "null", "NaN", "Infinity"):
            if character == literal[0]:
                return self._parse_literal(literal)
        if self.text.startswith("-I", self.index):
            return self._parse_literal("-Infinity")
        if character == "-" or character.isdigit():
            return self._parse_number()
        return _PREFIX_INVALID

    def _parse_literal(self, literal: str) -> str:
        remaining = self.text[self.index :]
        if remaining.startswith(literal):
            self.index += len(literal)
            return _PREFIX_COMPLETE
        if literal.startswith(remaining):
            self.index = len(self.text)
            return _PREFIX_INCOMPLETE
        return _PREFIX_INVALID

    def _parse_number(self) -> str:
        start = self.index
        while (
            self.index < len(self.text)
            and self.text[self.index] in "-+0123456789.e"
        ):
            self.index += 1
        token = self.text[start : self.index]
        if self.index < len(self.text):
            return _PREFIX_COMPLETE if _canonical_number(token) else _PREFIX_INVALID
        if _canonical_number(token):
            return _PREFIX_COMPLETE
        return (
            _PREFIX_INCOMPLETE
            if _documented_float_superset_prefix(token)
            else _PREFIX_INVALID
        )

    def _parse_string(
        self,
    ) -> tuple[
        str, _CompleteWriterString | _IncompleteStringPrefix | None
    ]:
        start = self.index

        self.index += 1
        while self.index < len(self.text):
            character = self.text[self.index]
            if character == '"':
                self.index += 1
                token = self.text[start : self.index]
                try:
                    value = json.loads(token)
                except json.JSONDecodeError:
                    return _PREFIX_INVALID, None
                if not isinstance(value, str) or json.dumps(value) != token:
                    return _PREFIX_INVALID, None
                return (
                    _PREFIX_COMPLETE,
                    _CompleteWriterString(_writer_string_alternatives(token)),
                )
            if ord(character) < 0x20 or ord(character) >= 0x7F:
                return _PREFIX_INVALID, None
            if character != "\\":
                self.index += 1
                continue
            self.index += 1
            if self.index == len(self.text):
                return (
                    _PREFIX_INCOMPLETE,
                    _decode_incomplete_writer_string(self.text[start:self.index]),
                )
            escape = self.text[self.index]
            if escape in _JSON_SIMPLE_ESCAPES:
                self.index += 1
                continue
            if escape != "u":
                return _PREFIX_INVALID, None
            self.index += 1
            digit_start = self.index
            while (
                self.index < len(self.text)
                and self.index - digit_start < 4
                and self.text[self.index] in _JSON_LOWER_HEX
            ):
                self.index += 1
            digits = self.text[digit_start : self.index]
            if len(digits) < 4:
                if self.index < len(self.text):
                    return _PREFIX_INVALID, None
                return (
                    (
                        _PREFIX_INCOMPLETE,
                        _decode_incomplete_writer_string(
                            self.text[start:self.index]
                        ),
                    )
                    if _unicode_escape_prefix_can_complete(digits)
                    else (_PREFIX_INVALID, None)
                )
            if not _writer_emits_unicode_escape(int(digits, 16)):
                return _PREFIX_INVALID, None
        return (
            _PREFIX_INCOMPLETE,
            _decode_incomplete_writer_string(self.text[start:self.index]),
        )


def _canonical_unterminated_mapping(segment: bytes) -> dict[str, Any] | None:
    if not segment.isascii():
        return None
    try:
        value = json.loads(segment)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(value, dict):
        return None
    if json.dumps(value, sort_keys=True).encode("ascii") != segment:
        return None
    return value


def _canonical_writer_proper_prefix(segment: bytes) -> bool:
    if not segment or not segment.isascii() or segment[:1] != b"{":
        return False
    return _CanonicalWriterPrefixRecognizer(
        segment.decode("ascii")
    ).recognizes_proper_prefix()


def parse_campaign_log_bytes(
    raw: bytes,
) -> tuple[list[Mapping[str, Any]] | None, str]:
    """Parse object-only JSONL and classify its final segment.

    The writer emits one complete JSON mapping plus LF per append.  Therefore
    an unterminated final segment is tolerable only when it is either a proper
    prefix of the writer's canonical mapping grammar or a byte-exact canonical
    mapping missing its LF.  Every other final segment is corruption.
    """

    terminated = raw.endswith(b"\n")
    lines = raw.split(b"\n")
    if terminated:
        lines = lines[:-1]
    rows: list[Mapping[str, Any]] = []
    final_segment = "terminated" if terminated else "empty"
    for index, line in enumerate(lines):
        is_unterminated_final = not terminated and index == len(lines) - 1
        if not line.strip():
            if is_unterminated_final and raw:
                return None, "invalid"
            continue
        if is_unterminated_final:
            value = _canonical_unterminated_mapping(line)
            if value is not None:
                rows.append(value)
                final_segment = "mapping"
                continue
            if _canonical_writer_proper_prefix(line):
                final_segment = "torn_prefix"
                continue
            return None, "invalid"
        try:
            value = json.loads(line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return None, "invalid"
        if not isinstance(value, Mapping):
            return None, "invalid"
        rows.append(value)
    return rows, final_segment


def load_campaign_log_rows(
    log_path: Path, *, raw_bytes: bytes | None = None
) -> list[Mapping[str, Any]] | None:
    """Read object-only JSONL, tolerating exactly one recognized final tear."""

    if raw_bytes is None:
        try:
            raw_bytes = read_authentication_input(
                log_path,
                grammar="jsonl",
                label="campaign provenance log",
            )
        except FileNotFoundError:
            return []
        except OSError:
            return None
    rows, _final_segment = parse_campaign_log_bytes(raw_bytes)
    return rows


def campaign_provenance_manifest_wire_path(manifest_path: Path) -> str:
    """Return the writer-minted wire path, enforcing the strict grammar."""

    path = f"campaign_manifests/{Path(manifest_path).name}"
    if re.fullmatch(CAMPAIGN_PROVENANCE_WRITER_PATH_PATTERN, path) is None:
        raise ValueError(
            "campaign provenance writer path violates the strict grammar: "
            f"{path!r}"
        )
    return path


def campaign_provenance_attestation(
    *,
    manifest_path: Path,
    raw_manifest_bytes: bytes,
    manifest: Mapping[str, Any],
    timestamp: str,
) -> dict[str, Any]:
    """Bind writer-emitted raw v2 bytes outside the manifest itself."""

    if manifest.get("schema_version") != CAMPAIGN_PROVENANCE_SCHEMA_V2:
        raise ValueError("campaign provenance attestations require a v2 manifest")
    session_id = manifest.get("session_id")
    if not isinstance(session_id, str) or not session_id:
        raise ValueError("campaign provenance v2 manifest lacks a session_id")
    if not isinstance(timestamp, str) or not timestamp:
        raise ValueError("campaign provenance attestation requires a timestamp")
    return {
        "schema_version": CAMPAIGN_PROVENANCE_ATTESTATION_SCHEMA,
        "record_type": CAMPAIGN_PROVENANCE_ATTESTATION_RECORD_TYPE,
        "timestamp": timestamp,
        "campaign_provenance_manifest": campaign_provenance_manifest_wire_path(
            manifest_path
        ),
        "campaign_provenance_manifest_sha256": hashlib.sha256(
            raw_manifest_bytes
        ).hexdigest(),
        "campaign_provenance_schema_version": CAMPAIGN_PROVENANCE_SCHEMA_V2,
        "campaign_provenance_session_id": session_id,
    }


def _recognizable_attestation(row: Mapping[str, Any]) -> bool:
    return bool(
        row.get("schema_version") == CAMPAIGN_PROVENANCE_ATTESTATION_SCHEMA
        or row.get("record_type") == CAMPAIGN_PROVENANCE_ATTESTATION_RECORD_TYPE
    )


def _attestation_shape_valid(row: Mapping[str, Any]) -> bool:
    path_text = row.get("campaign_provenance_manifest")
    prefix = "campaign_manifests/"
    path_name = (
        path_text[len(prefix) :]
        if isinstance(path_text, str) and path_text.startswith(prefix)
        else ""
    )
    reader_path_valid = bool(
        isinstance(path_text, str)
        and path_text.startswith(prefix)
        and path_name
        and "/" not in path_name
        and path_name.endswith(".json")
        and path_name != ".json"
    )
    digest = row.get("campaign_provenance_manifest_sha256")
    return bool(
        row.get("schema_version") == CAMPAIGN_PROVENANCE_ATTESTATION_SCHEMA
        and row.get("record_type")
        == CAMPAIGN_PROVENANCE_ATTESTATION_RECORD_TYPE
        and isinstance(row.get("timestamp"), str)
        and row["timestamp"]
        and reader_path_valid
        and re.fullmatch(r"[0-9a-f]{64}", digest or "") is not None
        and row.get("campaign_provenance_schema_version")
        == CAMPAIGN_PROVENANCE_SCHEMA_V2
        and isinstance(row.get("campaign_provenance_session_id"), str)
        and row["campaign_provenance_session_id"]
    )


def matching_campaign_provenance_attestations(
    rows: Sequence[Mapping[str, Any]],
    *,
    manifest_path: Path,
    raw_manifest_bytes: bytes,
    manifest: Mapping[str, Any],
) -> tuple[Mapping[str, Any], ...]:
    """Return shape-valid attestations for one exact current v2 snapshot."""

    expected_path = f"campaign_manifests/{Path(manifest_path).name}"
    expected_sha = hashlib.sha256(raw_manifest_bytes).hexdigest()
    session_id = manifest.get("session_id")
    return tuple(
        row
        for row in rows
        if _attestation_shape_valid(row)
        and row.get("campaign_provenance_manifest") == expected_path
        and row.get("campaign_provenance_manifest_sha256") == expected_sha
        and row.get("campaign_provenance_schema_version")
        == CAMPAIGN_PROVENANCE_SCHEMA_V2
        and row.get("campaign_provenance_session_id") == session_id
    )


def matching_campaign_provenance_lineage_attestations(
    rows: Sequence[Mapping[str, Any]],
    *,
    manifest_path: Path,
    manifest: Mapping[str, Any],
) -> tuple[Mapping[str, Any], ...]:
    """Return shape-valid attestations proving a path/session lineage."""

    expected_path = f"campaign_manifests/{Path(manifest_path).name}"
    session_id = manifest.get("session_id")
    return tuple(
        row
        for row in rows
        if _attestation_shape_valid(row)
        and row.get("campaign_provenance_manifest") == expected_path
        and row.get("campaign_provenance_schema_version")
        == CAMPAIGN_PROVENANCE_SCHEMA_V2
        and row.get("campaign_provenance_session_id") == session_id
    )


def load_campaign_provenance_manifest(
    path: Path,
) -> AuthenticatedCampaignManifest | None:
    """Load and shape-check one manifest without authenticating v2 bytes."""

    try:
        raw_bytes = read_authentication_input(
            path,
            grammar="json",
            label="campaign provenance manifest",
        )
        raw = json.loads(raw_bytes.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(raw, Mapping):
        return None
    schema_version = raw.get("schema_version")
    members = raw.get("members")
    if (
        schema_version not in CAMPAIGN_PROVENANCE_SCHEMAS
        or not isinstance(members, list)
        or any(
            not campaign_manifest_member_shape_valid(member, schema_version)
            for member in members
        )
    ):
        return None
    return AuthenticatedCampaignManifest(
        path=Path(path),
        raw_bytes=raw_bytes,
        value=raw,
    )


def shape_valid_campaign_provenance_attestations(
    rows: Sequence[Mapping[str, Any]],
) -> list[Mapping[str, Any]] | None:
    """Collect recognizable attestations, refusing any malformed member."""

    attestations: list[Mapping[str, Any]] = []
    for row in rows:
        if not _recognizable_attestation(row):
            continue
        if not _attestation_shape_valid(row):
            return None
        attestations.append(row)
    return attestations


def load_authenticated_campaign_manifest(
    runs_root: Path,
    manifest_path: Path,
    log_path: Path | None = None,
) -> AuthenticatedCampaignManifest | None:
    """Pointwise-dereference one manifest under shared acceptance rules.

    Legacy v1 descriptors retain their existing relocatable path behavior.
    A v2 descriptor is accepted only at its canonical catalog location and
    only when the external campaign log has exactly one attestation for its
    current raw bytes.
    """

    record = load_campaign_provenance_manifest(Path(manifest_path))
    if record is None:
        return None
    if record.value.get("schema_version") == CAMPAIGN_PROVENANCE_SCHEMA_V1:
        return record
    root = Path(runs_root)
    try:
        expected_path = (root / "campaign_manifests" / record.path.name).resolve()
        actual_path = record.path.resolve()
    except (OSError, RuntimeError):
        return None
    if actual_path != expected_path:
        return None
    rows = load_campaign_log_rows(log_path or root / "campaign_log.jsonl")
    if rows is None:
        return None
    attestations = shape_valid_campaign_provenance_attestations(rows)
    if attestations is None:
        return None
    matches = matching_campaign_provenance_attestations(
        attestations,
        manifest_path=record.path,
        raw_manifest_bytes=record.raw_bytes,
        manifest=record.value,
    )
    return record if len(matches) == 1 else None


def load_authenticated_campaign_catalog(
    runs_root: Path, log_path: Path | None = None
) -> list[AuthenticatedCampaignManifest] | None:
    """Load the all-or-nothing v1/v2 campaign-provenance catalog.

    Every manifest must use a known schema and satisfy its member wire.  Each
    current v2 raw snapshot must have exactly one matching writer attestation
    in the selected external campaign log.  Stale valid snapshot attestations
    may coexist, while malformed recognizable rows and duplicate attestations
    for current bytes refuse the entire catalog.
    """

    root = Path(runs_root)
    manifest_dir = root / "campaign_manifests"
    if not manifest_dir.is_dir():
        return []
    catalog: list[AuthenticatedCampaignManifest] = []
    for path in sorted(manifest_dir.glob("*.json"), key=lambda item: item.name):
        record = load_campaign_provenance_manifest(path)
        if record is None:
            return None
        catalog.append(record)

    v2_manifests = [
        record
        for record in catalog
        if record.value.get("schema_version") == CAMPAIGN_PROVENANCE_SCHEMA_V2
    ]
    if not v2_manifests:
        return catalog
    rows = load_campaign_log_rows(log_path or root / "campaign_log.jsonl")
    if rows is None:
        return None
    attestations = shape_valid_campaign_provenance_attestations(rows)
    if attestations is None:
        return None
    for record in v2_manifests:
        session_id = record.value.get("session_id")
        if not isinstance(session_id, str) or not session_id:
            return None
        matches = matching_campaign_provenance_attestations(
            attestations,
            manifest_path=record.path,
            raw_manifest_bytes=record.raw_bytes,
            manifest=record.value,
        )
        if len(matches) != 1:
            return None
    return catalog


def campaign_log_manifest_matches(value: object, manifest_name: str) -> bool:
    """Match a relocatable manifest reference without basename-only aliasing."""

    if not isinstance(value, str) or not value:
        return False
    parts = PurePosixPath(value).parts
    return len(parts) >= 2 and parts[-2:] == ("campaign_manifests", manifest_name)


def _legacy_log_member_classification(value: object) -> str | None:
    if not isinstance(value, Mapping):
        return None
    classification = value.get("collection_classification")
    if classification not in {"usable", "failed", "waived"}:
        return None
    flags = value.get("collection_integrity_flags")
    if not isinstance(flags, list) or any(not isinstance(flag, str) for flag in flags):
        return None
    if classification == "usable" and not (
        value.get("status") == "succeeded"
        and value.get("strict_valid") is True
        and not flags
    ):
        return None
    if classification == "waived" and not isinstance(value.get("waiver"), Mapping):
        return None
    strict_valid = value.get("strict_valid")
    if classification == "failed":
        if strict_valid is not True and strict_valid is not False:
            return None
        if value.get("status") == "succeeded" and strict_valid is True and not flags:
            return None
    return classification


def legacy_existing_outcome(
    *,
    manifest_name: str,
    member: Mapping[str, Any],
    log_rows: Sequence[Mapping[str, Any]],
) -> tuple[str, int] | None:
    """Bind one v1 existing row to its exact outcome and log-row identity."""

    run_id = member.get("run_id")
    config = member.get("config")
    bundle_ids = member.get("bundle_ids")
    if (
        not isinstance(run_id, str)
        or not run_id
        or not isinstance(config, str)
        or not config
        or not isinstance(bundle_ids, list)
        or not bundle_ids
        or any(not isinstance(bundle_id, str) or not bundle_id for bundle_id in bundle_ids)
    ):
        return None
    candidates: list[tuple[int, Mapping[str, Any]]] = []
    for row_index, row in enumerate(log_rows):
        if not campaign_log_manifest_matches(
            row.get("campaign_provenance_manifest"), manifest_name
        ):
            continue
        log_config = row.get("config")
        if (
            row.get("run_id") != run_id
            or not isinstance(log_config, str)
            or Path(log_config).name != config
        ):
            continue
        candidates.append((row_index, row))
    if len(candidates) != 1:
        return None
    row_index, candidate = candidates[0]
    members = candidate.get("members")
    if not isinstance(members, list):
        return None
    logged_bundle_ids = [
        value.get("bundle_id") if isinstance(value, Mapping) else None
        for value in members
    ]
    if logged_bundle_ids != bundle_ids:
        return None
    classifications = [_legacy_log_member_classification(value) for value in members]
    if any(value is None for value in classifications):
        return None
    status = candidate.get("status")
    if status == "skipped" and set(classifications) == {"usable"}:
        return "usable", row_index
    if (
        status == "waived"
        and "waived" in classifications
        and set(classifications) <= {"usable", "waived"}
    ):
        return "waived", row_index
    if status == "failed":
        return "failed", row_index
    if status == "incomplete_existing":
        return "incomplete", row_index
    return None
