"""The battery-float grammar corpus of cold ruling BFG-D-PARSER-ESC-01 §4.

Every case is built from committed bytes: the real capture
`fixtures/battery_float/float-2026-09-25-2047.ioreg` (ex-03) or the earlier
fixtures, with one named edit.  `positives(update)` and `negatives(update)`
re-stamp the top-level `UpdateTime` to `update`, so each negative is wrong in
exactly one structural or typing way and would otherwise be a fresh pass at
the site that consumes it.  The `RED` set names the negatives that
`battery_float.parse` at `faf0ea01` returns as `passed=True`.
"""

from __future__ import annotations

from pathlib import Path
import re

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "battery_float"
REAL = "float-2026-09-25-2047.ioreg"
REAL_SHA256 = "582475270c35c51cc05c2020f500d8c7dfba3eb9a6436a0186cb5ce18a851631"
HEADER = (b"+-o AppleSmartBattery  <class AppleSmartBattery, id 0x100000b3a, registered, "
          b"matched, active, busy 0 (2 ms), retain 7>")


def restamp(raw: bytes, update: int) -> bytes:
    stamped, count = re.subn(rb'(?m)^(      "UpdateTime" = )[0-9]+$',
                             lambda match: match.group(1) + str(update).encode(), raw, count=1)
    assert count == 1
    return stamped


def fixture(name: str, update: int) -> bytes:
    return restamp((FIXTURES / name).read_bytes(), update)


def sub(source: bytes, old: bytes, new: bytes) -> bytes:
    assert source.count(old) == 1, old
    return source.replace(old, new)


def required(update: int, indent: bytes = b"      ") -> bytes:
    return b"".join(indent + line + b"\n" for line in (
        b'"ExternalConnected" = Yes', b'"IsCharging" = No', b'"InstantAmperage" = 0',
        b'"UpdateTime" = ' + str(update).encode()))


def document(body: bytes) -> bytes:
    return HEADER + b"\n    {\n" + body + b"    }\n"


def with_line(base: bytes, line: bytes) -> bytes:
    """``base`` with one extra top-level property line after its first one."""
    return sub(base, b'      "PostChargeWaitSeconds" = 120\n',
               b'      "PostChargeWaitSeconds" = 120\n' + line + b"\n")


def nested(depth: int) -> bytes:
    return b'      "Deep" = ' + b"(" * depth + b")" * depth


def positives(update: int) -> dict[str, bytes]:
    """Documents the grammar accepts.  All but `charging` and `stale` pass."""
    base = fixture(REAL, update)
    lines = base.split(b"\n")
    return {
        "real_capture_ex03": base,
        "float_fixture": fixture("float.ioreg", update),
        "charging_fixture": fixture("charging-synthetic-from-real.ioreg", update),
        "stale_fixture": (FIXTURES / "stale-synthetic-from-real.ioreg").read_bytes(),
        "minimal_four_properties": document(required(update)),
        "reordered_properties": b"\n".join([*lines[:2], *reversed(lines[2:61]), *lines[61:]]),
        "nested_empty_rhs": with_line(base, b'      "Empty" = {"A"=,"B"=0,"C"=}'),
        "string_with_delimiters_and_escapes": with_line(base, b'      "S" = "{(< >)} \\" \\\\"'),
        "empty_containers": with_line(base, b'      "E" = ({},(),<>,"")'),
        "nested_shadow_names": with_line(
            base, b'      "Shadow" = {"ExternalConnected"=No,"IsCharging"=Yes,'
                  b'"InstantAmperage"=999,"UpdateTime"=1}'),
        "trailing_space_and_empty_lines": base + b"  \n\n       \n",
        "hyphen_key_minimal": document(b'      "built-in" = Yes\n' + required(update)),
        "signed_minus_158": sub(base, b'"InstantAmperage" = 0', b'"InstantAmperage" = 18446744073709551458'),
        "depth_64": with_line(base, nested(64)),
        "line_262144_bytes": with_line(base, b'      "Pad" = "' + b"x" * (262_144 - 16) + b'"'),
    }


def negatives(update: int) -> dict[str, bytes]:
    """Documents the grammar refuses; each is otherwise a fresh pass."""
    base = fixture(REAL, update)
    lines = base.split(b"\n")
    body = b"\n".join(lines[2:61]) + b"\n"
    u = str(update).encode()
    smuggled = (b'      "N" = "a"\r' + b"\r".join(required(update).rstrip(b"\n").split(b"\n")) + b"\n")
    without_required = base
    for line in required(update).split(b"\n")[:-1]:
        without_required = sub(without_required, line + b"\n", b"")

    def top(value: bytes) -> bytes:
        return with_line(base, b'      "X" = ' + value)

    return {
        # Round 1 (fix round 1 closed these).
        "r1_missing_close": sub(base, b"\n    }\n", b"\n"),
        "r1_missing_close_at_eof": b"\n".join(lines[:61]) + b"\n",
        "r1_other_object_name": sub(base, b"+-o AppleSmartBattery  <", b"+-o OtherBattery  <"),
        "r1_required_only_nested_multiline": document(
            b'      "Nested" = {\n' + required(update, b"        ") + b"      }\n"),
        "r1_trailer": base + b"unexpected trailer\n",
        # Round 2 (the escalated signature).
        "r2a_class_field": sub(base, b"<class AppleSmartBattery,", b"<class OtherBattery,"),
        "r2b_early_depth_return": document(
            b'      "Outer" = {\n      "Inner" = {\n        }\n' + required(update)),
        "r2b_same_indent": document(
            b'      "Outer" = {\n      "Inner" = {\n      }\n' + required(update)),
        "sol_outer_map_unclosed": document(b'      "Outer" = {\n' + body),
        # Header.
        "header_garbage": sub(base, HEADER, b"+-o AppleSmartBattery  <anything at all>"),
        "header_class_suffix": sub(base, b"<class AppleSmartBattery,", b"<class AppleSmartBatteryX,"),
        "header_extra_class_field": sub(base, b"retain 7>", b"retain 7, extra>"),
        "header_uppercase_id": sub(base, b"id 0x100000b3a", b"id 0x100000B3A"),
        "leading_blank_line": b"\n" + base,
        # Keys.
        "required_only_nested_inline": document(
            b'      "Box" = {"ExternalConnected"=Yes,"IsCharging"=No,"InstantAmperage"=0,'
            b'"UpdateTime"=' + u + b"}\n"),
        "duplicate_required": sub(base, b'      "InstantAmperage" = 0\n', b'      "InstantAmperage" = 0\n' * 2),
        "duplicate_optional": sub(base, b'      "Voltage" = 12899\n',
                                  b'      "Voltage" = 12899\n      "Voltage" = 1\n'),
        "duplicate_unknown": sub(base, b'      "Location" = 0\n', b'      "Location" = 0\n' * 2),
        "duplicate_nested_key": top(b'{"A"=1,"A"=2}'),
        "escaped_quote_top_key": with_line(base, b'      "Ext\\"ernal" = Yes'),
        "escaped_quote_nested_key": top(b'{"a\\"b"=1}'),
        "top_key_with_space": with_line(base, b'      "A B" = 1'),
        "alias_apple_raw_external_connected": sub(base, b'      "ExternalConnected" = Yes\n', b""),
        "alias_amperage": sub(base, b'      "InstantAmperage" = 0\n', b""),
        "missing_required": sub(base, b'      "IsCharging" = No\n', b""),
        # Framing.
        "crlf": base.replace(b"\n", b"\r\n"),
        "bare_cr": sub(base, b'"IsCharging" = No\n', b'"IsCharging" = No\r'),
        "cr_smuggled_required": sub(without_required, b'      "PostChargeWaitSeconds" = 120\n',
                                    b'      "PostChargeWaitSeconds" = 120\n' + smuggled),
        "tab_indent": sub(base, b'      "IsCharging" = No', b'\t"IsCharging" = No'),
        "tab_in_string": sub(base, b'"bq40z651"', b'"bq40\tz651"'),
        "nul": sub(base, b'"bq40z651"', b'"bq40\x00z651"'),
        "non_ascii": sub(base, b'"bq40z651"', "\"bq40z651é\"".encode()),
        "homoglyph_key": sub(base, b'"ExternalConnected" = Yes',
                             "\"ExternalConnectеd\" = Yes".encode() + b'\n      "ExternalConnected" = Yes'),
        "vertical_tab": sub(base, b'"bq40z651"', b'"bq40\x0bz651"'),
        "missing_final_lf": base + b"    ",
        "missing_final_lf_at_close": base.rstrip(b" \n"),
        "empty": b"",
        "header_only": HEADER + b"\n",
        "header_open_only": HEADER + b"\n    {\n",
        "empty_object": HEADER + b"\n    {\n    }\n",
        "over_1_mib": base + (b" " * 1023 + b"\n") * 1024,
        "line_262145_bytes": with_line(base, b'      "Pad" = "' + b"x" * (262_145 - 16) + b'"'),
        "depth_65": with_line(base, nested(65)),
        "depth_70": with_line(base, nested(70)),
        # Lines after the close.
        "tail_garbage": base + b"garbage\n",
        "property_after_close": base + b'      "IsCharging" = Yes\n',
        "second_object": base + fixture("float.ioreg", update),
        "extra_close": base + b"    }\n",
        "indented_child_after_close": base + b"  +-o Child  <class Child>\n",
        # Line shape.
        "missing_open": sub(base, b"\n    {\n", b"\n"),
        "open_indent_wrong": sub(base, b"\n    {\n", b"\n   {\n"),
        "close_indent_wrong": sub(base, b"\n    }\n", b"\n     }\n"),
        "all_properties_at_8_spaces": base.replace(b'\n      "', b'\n        "'),
        "one_property_at_8_spaces": sub(base, b'      "IsCharging" = No', b'        "IsCharging" = No'),
        "blank_line_in_body": sub(base, b'      "IsCharging" = No\n', b'      "IsCharging" = No\n\n'),
        "space_only_line_in_body": sub(base, b'      "IsCharging" = No\n', b'      "IsCharging" = No\n      \n'),
        "trailing_space_after_value": sub(base, b'"IsCharging" = No\n', b'"IsCharging" = No \n'),
        "two_spaces_around_equals": sub(base, b'"IsCharging" = No', b'"IsCharging"  =  No'),
        "no_spaces_around_equals": sub(base, b'"IsCharging" = No', b'"IsCharging"=No'),
        # Value grammar.
        "unclosed_inline_dict_synthetic": top(b'{"a"=1'),
        "unclosed_inline_dict_real": sub(base, b'"CarrierModeStatus"=0}\n', b'"CarrierModeStatus"=0\n'),
        "unclosed_inline_array": top(b"(1,2"),
        "mismatched_delimiter_dict": top(b'{"a"=1)'),
        "mismatched_delimiter_array": top(b"(1}"),
        "extra_open_brace": top(b'{{"a"=1}'),
        "delimiter_underflow": top(b"1}"),
        "unclosed_quote_top": sub(base, b'"bq40z651"', b'"bq40z651'),
        "unclosed_quote_nested": top(b'{"a"="x}'),
        "dangling_escape": top(b'"abc\\'),
        "bad_escape": top(b'"a\\nb"'),
        "bare_garbage": top(b"garbage"),
        "balanced_garbage": top(b"{garbage}"),
        "two_values": top(b"1 2"),
        "two_adjacent_values": top(b'1"a"'),
        "second_assignment_on_a_line": sub(base, b'"IsCharging" = No\n', b'"IsCharging" = No "IsCharging" = Yes\n'),
        "empty_top_value": with_line(base, b'      "X" = '),
        "empty_array_element": top(b"(1,,2)"),
        "array_trailing_comma": top(b"(1,2,)"),
        "dict_trailing_comma": top(b'{"a"=1,}'),
        "dict_member_without_equals": top(b'{"a"1}'),
        "dict_empty_member_then_close_after_comma": top(b'{"A"=,}'),
        "odd_hex": top(b"<abc>"),
        "bad_hex": top(b"<zz>"),
        "uppercase_hex_data": top(b"<AB>"),
        "ascii_data_rendering": top(b'<"AppleSmartBattery">'),
        "square_array": top(b"[1,2]"),
        "negative_atom": top(b"-1"),
        "float_atom": top(b"1.5"),
        "bare_word_atom": top(b"Maybe"),
        # Required-property typing.
        "uint_overflow": sub(base, b'"InstantAmperage" = 0', b'"InstantAmperage" = 18446744073709551616'),
        "signed_lexeme": sub(base, b'"InstantAmperage" = 0', b'"InstantAmperage" = -158'),
        "quoted_required": sub(base, b'"InstantAmperage" = 0', b'"InstantAmperage" = "0"'),
        "nested_required_value": sub(base, b'"IsCharging" = No', b'"IsCharging" = {"a"=No}'),
        "bool_as_0": sub(base, b'"IsCharging" = No', b'"IsCharging" = 0'),
        "lowercase_bool": sub(base, b'"ExternalConnected" = Yes', b'"ExternalConnected" = yes'),
        "update_time_21_digits": sub(base, b'"UpdateTime" = ' + u, b'"UpdateTime" = 0' + u.rjust(20, b"0")),
        "instant_amperage_21_digits": sub(base, b'"InstantAmperage" = 0', b'"InstantAmperage" = ' + b"0" * 21),
        "malformed_fixture": fixture("malformed-synthetic-from-real.ioreg", update),
        # Recorded-property typing (obligation R2-8; refuter X8 first).
        "x8_apple_raw_current_capacity_yes": sub(base, b'"AppleRawCurrentCapacity" = 7585',
                                                 b'"AppleRawCurrentCapacity" = Yes'),
        "recorded_amperage_bool": sub(base, b'"Amperage" = 0', b'"Amperage" = No'),
        "recorded_voltage_string": sub(base, b'"Voltage" = 12899', b'"Voltage" = "12899"'),
        "recorded_temperature_data": sub(base, b'"Temperature" = 3034', b'"Temperature" = <0bda>'),
        "recorded_fully_charged_int": sub(base, b'"FullyCharged" = Yes', b'"FullyCharged" = 1'),
        "recorded_current_capacity_dict": sub(base, b'"CurrentCapacity" = 100', b'"CurrentCapacity" = {"v"=100}'),
        "recorded_apple_raw_current_capacity_array": sub(base, b'"AppleRawCurrentCapacity" = 7585',
                                                         b'"AppleRawCurrentCapacity" = (7585)'),
        "recorded_apple_raw_max_capacity_overflow": sub(base, b'"AppleRawMaxCapacity" = 7585',
                                                        b'"AppleRawMaxCapacity" = 18446744073709551616'),
        "recorded_voltage_21_digits": sub(base, b'"Voltage" = 12899', b'"Voltage" = 000000000000000012899'),
        "recorded_update_time_string": sub(base, b'"UpdateTime" = ' + u, b'"UpdateTime" = "' + u + b'"'),
    }


# Negatives that `battery_float.parse` at faf0ea01 returns as passed=True
# (executed in /tmp at faf0ea01; the seat report pastes the run).
RED = frozenset({
    "all_properties_at_8_spaces",
    "array_trailing_comma",
    "ascii_data_rendering",
    "bad_escape",
    "bad_hex",
    "balanced_garbage",
    "bare_cr",
    "bare_garbage",
    "bare_word_atom",
    "blank_line_in_body",
    "cr_smuggled_required",
    "crlf",
    "dangling_escape",
    "delimiter_underflow",
    "depth_65",
    "depth_70",
    "dict_empty_member_then_close_after_comma",
    "dict_member_without_equals",
    "dict_trailing_comma",
    "duplicate_nested_key",
    "duplicate_optional",
    "duplicate_unknown",
    "empty_array_element",
    "escaped_quote_nested_key",
    "extra_open_brace",
    "float_atom",
    "header_class_suffix",
    "header_extra_class_field",
    "header_garbage",
    "header_uppercase_id",
    "homoglyph_key",
    "instant_amperage_21_digits",
    "line_262145_bytes",
    "mismatched_delimiter_array",
    "mismatched_delimiter_dict",
    "missing_final_lf",
    "missing_final_lf_at_close",
    "negative_atom",
    "non_ascii",
    "nul",
    "odd_hex",
    "over_1_mib",
    "r2a_class_field",
    "r2b_early_depth_return",
    "r2b_same_indent",
    "recorded_amperage_bool",
    "recorded_apple_raw_current_capacity_array",
    "recorded_apple_raw_max_capacity_overflow",
    "recorded_current_capacity_dict",
    "recorded_fully_charged_int",
    "recorded_temperature_data",
    "recorded_voltage_21_digits",
    "recorded_voltage_string",
    "space_only_line_in_body",
    "square_array",
    "tab_in_string",
    "top_key_with_space",
    "two_adjacent_values",
    "two_values",
    "unclosed_inline_array",
    "unclosed_inline_dict_real",
    "unclosed_inline_dict_synthetic",
    "unclosed_quote_nested",
    "unclosed_quote_top",
    "update_time_21_digits",
    "uppercase_hex_data",
    "vertical_tab",
    "x8_apple_raw_current_capacity_yes",
})
