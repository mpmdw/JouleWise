#!/usr/bin/env python3
"""Validate the exact bytes of a frozen cold-gate packet.

Packet grammar (intentionally strict and fail-closed):

* Exactly one ATX heading, at any level, has the title ``Charter pin``
  after an optional numeric section prefix (for example,
  ``## 6. Charter pin``).  Its Markdown section extends to the next heading
  of the same or a higher level.  The section must contain exactly one
  single-line ``Charter ...: `path` `` declaration using a nonempty relative
  POSIX path, exactly one ``sha256`` label, and exactly one standalone 64-hex
  digest, in that order.  Digest text elsewhere in the packet is irrelevant.
* Exactly one ATX heading, at any level, has the title ``Exhibit manifest``
  after an optional numeric prefix and before an optional parenthetical.
  Its section must contain exactly one bare triple-backtick fenced block.
  Every block line must be exactly ``<64 hex><two spaces><path>``.
  Paths are unique, lexical POSIX paths relative to the packet directory;
  absolute paths, empty/dot/dot-dot components, and backslashes are refused.
* The exhibit-manifest digest is SHA-256 over the exact packet bytes between
  the opening and closing fence lines (including their original line endings,
  excluding the fence lines).  Packet, charter, and exhibit digests are over
  the complete file bytes read once.  There is deliberately no line-range or
  partial-file exhibit hashing rule in this validator.

The packet's charter path is documentary and is recorded in the receipt.  The
bytes validated as the charter come only from ``--charter``; their independent
trust anchor comes only from ``--expected-charter-sha256``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from pathlib import PurePosixPath
import re
import sys
from typing import Any, Sequence


RECEIPT_SCHEMA = "coldgate-validator-receipt/v1"
REFUSAL_EXIT = 2
HEX_RE = re.compile(r"^[0-9a-fA-F]{64}$")
HEX_TOKEN_RE = re.compile(r"(?<![0-9a-fA-F])([0-9a-fA-F]{64})(?![0-9a-fA-F])")
SHA_LABEL_RE = re.compile(r"(?i)(?<![A-Za-z0-9])sha-?256(?![A-Za-z0-9])")
PATH_DECL_RE = re.compile(
    r"(?im)^[ \t]*Charter(?:[ \t]+[^:\r\n]*)?:[ \t]*`([^`\r\n]+)`[ \t]*$"
)
HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*$")
CHARTER_TITLE_RE = re.compile(
    r"(?i)^(?:\d+(?:\.\d+)*\.[ \t]+)?Charter[ \t]+pin$"
)
MANIFEST_TITLE_RE = re.compile(
    r"(?i)^(?:\d+(?:\.\d+)*\.[ \t]+)?Exhibit[ \t]+manifest"
    r"(?:[ \t]+\([^()\r\n]*\))?$"
)
MANIFEST_LINE_RE = re.compile(r"^([0-9a-fA-F]{64})  ([^\r\n]+)$")
FENCE_RE = re.compile(r"^[ \t]*```[ \t]*$")


class CliError(Exception):
    """Raised instead of argparse terminating without a JSON receipt."""


class ReceiptArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise CliError(message)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_once(path: Path) -> bytes | None:
    try:
        return path.read_bytes()
    except (OSError, ValueError):
        return None


def _base_receipt(
    *,
    packet_arg: str | None,
    charter_arg: str | None,
    expected_charter_sha256: str | None,
    launch_environment_attestation: str | None,
    contamination_disclosure: str | None,
) -> dict[str, Any]:
    expected = expected_charter_sha256
    if expected is not None and HEX_RE.fullmatch(expected):
        expected = expected.lower()
    return {
        "convening_attestations": {
            "contamination_disclosure": contamination_disclosure,
            "launch_environment": launch_environment_attestation,
        },
        "details": [],
        "digests": {
            "charter_sha256": None,
            "exhibit_manifest_sha256": None,
            "exhibits": [],
            "packet_sha256": None,
        },
        "expected_charter_sha256": expected,
        "inputs": {
            "charter": charter_arg,
            "packet": packet_arg,
        },
        "packet_charter_path": None,
        "packet_charter_pin_sha256": None,
        "reason": None,
        "result": "REFUSE",
        "schema": RECEIPT_SCHEMA,
    }


def _refuse(
    receipt: dict[str, Any], reason: str, details: list[dict[str, Any]] | None = None
) -> dict[str, Any]:
    receipt["result"] = "REFUSE"
    receipt["reason"] = reason
    receipt["details"] = details or []
    return receipt


def _heading(line: str) -> tuple[int, str] | None:
    match = HEADING_RE.fullmatch(line)
    if match is None:
        return None
    return len(match.group(1)), match.group(2).strip()


def _section_end(lines: list[str], heading_index: int, level: int) -> int:
    for index in range(heading_index + 1, len(lines)):
        parsed = _heading(lines[index])
        if parsed is not None and parsed[0] <= level:
            return index
    return len(lines)


def _parse_charter_pin(lines: list[str]) -> tuple[str, str, str | None]:
    headings: list[tuple[int, int]] = []
    for index, line in enumerate(lines):
        parsed = _heading(line)
        if parsed is not None and CHARTER_TITLE_RE.fullmatch(parsed[1]):
            headings.append((index, parsed[0]))

    if not headings:
        return "", "", "charter_pin_missing"
    if len(headings) != 1:
        return "", "", "charter_pin_duplicate"

    index, level = headings[0]
    section = "\n".join(lines[index + 1 : _section_end(lines, index, level)])
    path_matches = list(PATH_DECL_RE.finditer(section))
    sha_labels = list(SHA_LABEL_RE.finditer(section))
    digest_matches = list(HEX_TOKEN_RE.finditer(section))
    if len(path_matches) != 1 or len(sha_labels) != 1 or len(digest_matches) != 1:
        return "", "", "charter_pin_ambiguous"
    path_match = path_matches[0]
    sha_label = sha_labels[0]
    digest_match = digest_matches[0]
    if not (path_match.start() < sha_label.start() < digest_match.start()):
        return "", "", "charter_pin_ambiguous"
    charter_path = path_match.group(1)
    charter_components = charter_path.split("/")
    if (
        not charter_path
        or charter_path != charter_path.strip()
        or charter_path.startswith("/")
        or "\\" in charter_path
        or any(component in {"", ".", ".."} for component in charter_components)
        or PurePosixPath(charter_path).is_absolute()
    ):
        return "", "", "charter_pin_ambiguous"
    return charter_path, digest_match.group(1).lower(), None


def _manifest_block(
    raw_lines: list[bytes], text_lines: list[str]
) -> tuple[bytes | None, list[str] | None, str | None]:
    headings: list[tuple[int, int]] = []
    for index, line in enumerate(text_lines):
        parsed = _heading(line)
        if parsed is not None and MANIFEST_TITLE_RE.fullmatch(parsed[1]):
            headings.append((index, parsed[0]))
    if len(headings) != 1:
        return None, None, "manifest_parse_error"

    index, level = headings[0]
    end = _section_end(text_lines, index, level)
    fence_indexes = [
        candidate
        for candidate in range(index + 1, end)
        if FENCE_RE.fullmatch(text_lines[candidate])
    ]
    if len(fence_indexes) != 2 or fence_indexes[0] >= fence_indexes[1]:
        return None, None, "manifest_parse_error"
    opening, closing = fence_indexes
    body = b"".join(raw_lines[opening + 1 : closing])
    body_lines = text_lines[opening + 1 : closing]
    if not body_lines:
        return body, body_lines, "manifest_parse_error"
    return body, body_lines, None


def _parse_manifest_lines(
    body_lines: list[str],
) -> tuple[list[tuple[str, str]] | None, str | None]:
    entries: list[tuple[str, str]] = []
    seen: set[str] = set()
    for line in body_lines:
        match = MANIFEST_LINE_RE.fullmatch(line)
        if match is None:
            return None, "manifest_parse_error"
        expected, path_text = match.groups()
        components = path_text.split("/")
        if (
            not path_text
            or path_text != path_text.strip()
            or path_text.startswith("/")
            or "\\" in path_text
            or any(component in {"", ".", ".."} for component in components)
            or PurePosixPath(path_text).is_absolute()
            or path_text in seen
        ):
            return None, "manifest_parse_error"
        seen.add(path_text)
        entries.append((expected.lower(), path_text))
    if not entries:
        return None, "manifest_parse_error"
    return entries, None


def validate(
    *,
    packet_arg: str | None,
    charter_arg: str | None,
    expected_charter_sha256: str | None,
    launch_environment_attestation: str | None,
    contamination_disclosure: str | None,
) -> dict[str, Any]:
    receipt = _base_receipt(
        packet_arg=packet_arg,
        charter_arg=charter_arg,
        expected_charter_sha256=expected_charter_sha256,
        launch_environment_attestation=launch_environment_attestation,
        contamination_disclosure=contamination_disclosure,
    )
    missing = [
        name
        for name, value in (
            ("packet", packet_arg),
            ("charter", charter_arg),
            ("expected_charter_sha256", expected_charter_sha256),
        )
        if value is None
    ]
    if missing:
        return _refuse(receipt, "cli_invalid", [{"missing": missing}])
    if not HEX_RE.fullmatch(expected_charter_sha256):
        return _refuse(receipt, "expected_charter_sha256_invalid")

    expected_charter_sha256 = expected_charter_sha256.lower()
    packet_path = Path(packet_arg)
    charter_path = Path(charter_arg)
    packet_bytes = _read_once(packet_path)
    if packet_bytes is None:
        return _refuse(receipt, "packet_unreadable", [{"path": packet_arg}])
    receipt["digests"]["packet_sha256"] = _sha256(packet_bytes)

    charter_bytes = _read_once(charter_path)
    if charter_bytes is None:
        return _refuse(receipt, "charter_unreadable", [{"path": charter_arg}])
    observed_charter_sha256 = _sha256(charter_bytes)
    receipt["digests"]["charter_sha256"] = observed_charter_sha256

    try:
        packet_text = packet_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return _refuse(receipt, "packet_not_utf8")
    raw_lines = packet_bytes.splitlines(keepends=True)
    text_lines = [line.decode("utf-8").rstrip("\r\n") for line in raw_lines]

    packet_charter_path, packet_pin, pin_error = _parse_charter_pin(text_lines)
    if pin_error is not None:
        return _refuse(receipt, pin_error)
    receipt["packet_charter_path"] = packet_charter_path
    receipt["packet_charter_pin_sha256"] = packet_pin

    manifest_body, manifest_lines, manifest_error = _manifest_block(
        raw_lines, text_lines
    )
    if manifest_body is not None:
        receipt["digests"]["exhibit_manifest_sha256"] = _sha256(manifest_body)
    if manifest_error is not None or manifest_lines is None:
        return _refuse(receipt, "manifest_parse_error")
    manifest, manifest_error = _parse_manifest_lines(manifest_lines)
    if manifest_error is not None or manifest is None:
        return _refuse(receipt, "manifest_parse_error")

    unreadable: list[dict[str, Any]] = []
    mismatches: list[dict[str, Any]] = []
    exhibit_receipts: list[dict[str, Any]] = []
    for exhibit_expected, exhibit_path in manifest:
        exhibit_bytes = _read_once(packet_path.parent / PurePosixPath(exhibit_path))
        exhibit_observed = None if exhibit_bytes is None else _sha256(exhibit_bytes)
        exhibit_receipts.append(
            {
                "expected_sha256": exhibit_expected,
                "observed_sha256": exhibit_observed,
                "path": exhibit_path,
            }
        )
        if exhibit_bytes is None:
            unreadable.append({"path": exhibit_path})
        elif exhibit_observed != exhibit_expected:
            mismatches.append({"path": exhibit_path})
    receipt["digests"]["exhibits"] = exhibit_receipts

    if unreadable:
        return _refuse(receipt, "exhibit_unreadable", unreadable)
    if not (
        expected_charter_sha256 == packet_pin == observed_charter_sha256
    ):
        return _refuse(receipt, "charter_digest_mismatch")
    if mismatches:
        return _refuse(receipt, "exhibit_digest_mismatch", mismatches)

    receipt["result"] = "PASS"
    receipt["reason"] = None
    receipt["details"] = []
    return receipt


def _canonical_json(receipt: dict[str, Any]) -> bytes:
    return (
        json.dumps(receipt, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        + "\n"
    ).encode("utf-8")


def _parser() -> ReceiptArgumentParser:
    parser = ReceiptArgumentParser(description=__doc__)
    parser.add_argument("--packet")
    parser.add_argument("--charter")
    parser.add_argument("--expected-charter-sha256")
    parser.add_argument("--receipt-out")
    parser.add_argument("--launch-environment-attestation")
    parser.add_argument("--contamination-disclosure")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = _parser().parse_args(argv)
    except CliError:
        receipt = _refuse(
            _base_receipt(
                packet_arg=None,
                charter_arg=None,
                expected_charter_sha256=None,
                launch_environment_attestation=None,
                contamination_disclosure=None,
            ),
            "cli_invalid",
        )
        sys.stdout.buffer.write(_canonical_json(receipt))
        return REFUSAL_EXIT

    receipt = validate(
        packet_arg=args.packet,
        charter_arg=args.charter,
        expected_charter_sha256=args.expected_charter_sha256,
        launch_environment_attestation=args.launch_environment_attestation,
        contamination_disclosure=args.contamination_disclosure,
    )
    output = _canonical_json(receipt)
    if args.receipt_out is not None:
        try:
            Path(args.receipt_out).write_bytes(output)
        except (OSError, ValueError):
            receipt = _refuse(
                receipt,
                "receipt_write_failed",
                [{"path": args.receipt_out}],
            )
            output = _canonical_json(receipt)
    sys.stdout.buffer.write(output)
    return 0 if receipt["result"] == "PASS" else REFUSAL_EXIT


if __name__ == "__main__":
    raise SystemExit(main())
