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
  absolute paths, Windows drive-qualified paths, empty/dot/dot-dot components,
  and backslashes are refused.
* The exhibit-manifest digest is SHA-256 over the exact packet bytes between
  the opening and closing fence lines (including their original line endings,
  excluding the fence lines).  Packet, charter, and exhibit digests are over
  the complete file bytes read once.  There is deliberately no line-range or
  partial-file exhibit hashing rule in this validator.

Digest comparisons use semantic hexadecimal equality: accepted upper- or
lowercase input is normalized to lowercase in the canonical receipt.  The
packet's charter path is documentary and is recorded by basename.  The bytes
validated as the charter come only from ``--charter``; their independent trust
anchor comes only from ``--expected-charter-sha256``.  Packet bytes are
independently anchored by the required ``--expected-packet-sha256`` argument.

Exit status zero is reserved for a validated ``PASS``.  Help, usage errors,
and every other non-validation termination are therefore nonzero; help emits
its ordinary help text but no JSON receipt.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
from typing import Any, BinaryIO, Sequence


RECEIPT_SCHEMA = "coldgate-validator-receipt/v1"
REFUSAL_EXIT = 2
HEX_RE = re.compile(r"^[0-9a-fA-F]{64}$")
HEX_TOKEN_RE = re.compile(r"(?<!\w)([0-9a-fA-F]{64})(?!\w)")
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
WINDOWS_DRIVE_RE = re.compile(r"^[A-Za-z]:")


class CliError(Exception):
    """Raised instead of argparse terminating without a refusal receipt."""


class NonValidationExit(Exception):
    """Raised for help or another argparse exit that must remain nonzero."""


class ReceiptArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise CliError(message)

    def exit(self, status: int = 0, message: str | None = None) -> None:
        if message:
            self._print_message(message, sys.stderr)
        raise NonValidationExit


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_handle(handle: BinaryIO) -> str:
    digest = hashlib.sha256()
    while True:
        chunk = handle.read(1024 * 1024)
        if not chunk:
            return digest.hexdigest()
        digest.update(chunk)


def _read_once(path: Path) -> bytes | None:
    try:
        return path.read_bytes()
    except (OSError, ValueError):
        return None


def _basename(value: str | None) -> str | None:
    if value is None:
        return None
    return Path(value).name


def _normalized_digest(value: str | None) -> str | None:
    if value is not None and HEX_RE.fullmatch(value):
        return value.lower()
    return value


def _base_receipt(
    *,
    packet_arg: str | None,
    charter_arg: str | None,
    expected_packet_sha256: str | None,
    expected_charter_sha256: str | None,
    launch_environment_attestation: str | None,
    contamination_disclosure: str | None,
) -> dict[str, Any]:
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
        "expected_charter_sha256": _normalized_digest(expected_charter_sha256),
        "expected_packet_sha256": _normalized_digest(expected_packet_sha256),
        "inputs": {
            "charter": _basename(charter_arg),
            "packet": _basename(packet_arg),
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
    return Path(charter_path).name, digest_match.group(1).lower(), None


def _charter_mismatch_reason(trusted: str, packet_pin: str, observed: str) -> str | None:
    if trusted == packet_pin == observed:
        return None
    if packet_pin == observed and trusted != observed:
        return "charter_trusted_observed_mismatch"
    if trusted == observed and trusted != packet_pin:
        return "charter_trusted_packet_pin_mismatch"
    if trusted == packet_pin and packet_pin != observed:
        return "charter_packet_pin_observed_mismatch"
    if trusted != packet_pin:
        return "charter_trusted_packet_pin_mismatch"
    if packet_pin != observed:
        return "charter_packet_pin_observed_mismatch"
    return "charter_trusted_observed_mismatch"


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
            or WINDOWS_DRIVE_RE.match(path_text)
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


def _is_within(path: Path, directory: Path) -> bool:
    try:
        path.relative_to(directory)
    except ValueError:
        return False
    return True


def _receipt_out_reason(
    receipt_out_arg: str | None, packet_path: Path, charter_path: Path
) -> str | None:
    if receipt_out_arg is None:
        return None
    try:
        target = Path(receipt_out_arg)
        resolved_target = target.resolve(strict=False)
        packet_directory = packet_path.parent.resolve(strict=True)
        resolved_charter = charter_path.resolve(strict=True)
    except (OSError, RuntimeError, ValueError):
        return "receipt_out_unsafe"
    if _is_within(resolved_target, packet_directory) or resolved_target == resolved_charter:
        return "receipt_out_unsafe"
    try:
        if target.is_symlink() or target.exists():
            return "receipt_out_exists"
    except OSError:
        return "receipt_out_unsafe"
    return None


def _open_exhibit(
    packet_directory: Path, exhibit_path: str
) -> tuple[str | None, tuple[int, int] | None, str | None]:
    candidate = packet_directory.joinpath(*PurePosixPath(exhibit_path).parts)
    current = packet_directory
    leaf_lstat: os.stat_result | None = None
    try:
        for index, component in enumerate(PurePosixPath(exhibit_path).parts):
            current = current / component
            component_stat = os.lstat(current)
            if stat.S_ISLNK(component_stat.st_mode):
                return None, None, "exhibit_custody_invalid"
            if index < len(PurePosixPath(exhibit_path).parts) - 1:
                if not stat.S_ISDIR(component_stat.st_mode):
                    return None, None, "exhibit_custody_invalid"
            else:
                leaf_lstat = component_stat
        resolved_candidate = candidate.resolve(strict=True)
        if not _is_within(resolved_candidate, packet_directory):
            return None, None, "exhibit_custody_invalid"
        if leaf_lstat is None or not stat.S_ISREG(leaf_lstat.st_mode):
            return None, None, "exhibit_custody_invalid"
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(candidate, flags)
        with os.fdopen(descriptor, "rb") as handle:
            opened_stat = os.fstat(handle.fileno())
            if (
                not stat.S_ISREG(opened_stat.st_mode)
                or opened_stat.st_dev != leaf_lstat.st_dev
                or opened_stat.st_ino != leaf_lstat.st_ino
            ):
                return None, None, "exhibit_custody_invalid"
            return (
                _sha256_handle(handle),
                (opened_stat.st_dev, opened_stat.st_ino),
                None,
            )
    except (OSError, RuntimeError, ValueError):
        return None, None, "exhibit_unreadable"


def validate(
    *,
    packet_arg: str | None,
    charter_arg: str | None,
    expected_packet_sha256: str | None,
    expected_charter_sha256: str | None,
    receipt_out_arg: str | None,
    launch_environment_attestation: str | None,
    contamination_disclosure: str | None,
) -> dict[str, Any]:
    receipt = _base_receipt(
        packet_arg=packet_arg,
        charter_arg=charter_arg,
        expected_packet_sha256=expected_packet_sha256,
        expected_charter_sha256=expected_charter_sha256,
        launch_environment_attestation=launch_environment_attestation,
        contamination_disclosure=contamination_disclosure,
    )
    missing = [
        name
        for name, value in (
            ("packet", packet_arg),
            ("charter", charter_arg),
            ("expected_packet_sha256", expected_packet_sha256),
            ("expected_charter_sha256", expected_charter_sha256),
        )
        if value is None
    ]
    if missing:
        return _refuse(receipt, "cli_invalid", [{"missing": missing}])
    if not HEX_RE.fullmatch(expected_packet_sha256):
        return _refuse(receipt, "expected_packet_sha256_invalid")
    if not HEX_RE.fullmatch(expected_charter_sha256):
        return _refuse(receipt, "expected_charter_sha256_invalid")

    trusted_packet_sha256 = expected_packet_sha256.lower()
    trusted_charter_sha256 = expected_charter_sha256.lower()
    packet_path = Path(packet_arg)
    charter_path = Path(charter_arg)

    packet_bytes = _read_once(packet_path)
    if packet_bytes is None:
        return _refuse(receipt, "packet_unreadable", [{"path": packet_path.name}])
    observed_packet_sha256 = _sha256(packet_bytes)
    receipt["digests"]["packet_sha256"] = observed_packet_sha256
    if observed_packet_sha256 != trusted_packet_sha256:
        return _refuse(receipt, "packet_digest_mismatch")

    charter_bytes = _read_once(charter_path)
    if charter_bytes is None:
        return _refuse(receipt, "charter_unreadable", [{"path": charter_path.name}])
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

    mismatch_reason = _charter_mismatch_reason(
        trusted_charter_sha256, packet_pin, observed_charter_sha256
    )
    if mismatch_reason is not None:
        return _refuse(receipt, mismatch_reason)

    receipt_out_reason = _receipt_out_reason(receipt_out_arg, packet_path, charter_path)
    if receipt_out_reason is not None:
        return _refuse(
            receipt,
            receipt_out_reason,
            [{"path": _basename(receipt_out_arg)}],
        )

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

    try:
        packet_directory = packet_path.parent.resolve(strict=True)
    except (OSError, RuntimeError, ValueError):
        return _refuse(receipt, "packet_unreadable", [{"path": packet_path.name}])

    unreadable: list[dict[str, Any]] = []
    custody_invalid: list[dict[str, Any]] = []
    mismatches: list[dict[str, Any]] = []
    aliases: list[dict[str, Any]] = []
    exhibit_receipts: list[dict[str, Any]] = []
    seen_identities: dict[tuple[int, int], str] = {}
    for exhibit_expected, exhibit_path in manifest:
        exhibit_name = Path(exhibit_path).name
        exhibit_observed, identity, exhibit_error = _open_exhibit(
            packet_directory, exhibit_path
        )
        exhibit_receipts.append(
            {
                "expected_sha256": exhibit_expected,
                "observed_sha256": exhibit_observed,
                "path": exhibit_name,
            }
        )
        if exhibit_error == "exhibit_unreadable":
            unreadable.append({"path": exhibit_name})
        elif exhibit_error == "exhibit_custody_invalid":
            custody_invalid.append({"path": exhibit_name})
        elif identity is not None and identity in seen_identities:
            aliases.append(
                {"path": exhibit_name, "aliases": seen_identities[identity]}
            )
        elif identity is not None:
            seen_identities[identity] = exhibit_name
        if exhibit_observed is not None and exhibit_observed != exhibit_expected:
            mismatches.append({"path": exhibit_name})
    receipt["digests"]["exhibits"] = exhibit_receipts

    if unreadable:
        return _refuse(receipt, "exhibit_unreadable", unreadable)
    if custody_invalid:
        return _refuse(receipt, "exhibit_custody_invalid", custody_invalid)
    if aliases:
        return _refuse(receipt, "exhibit_alias_duplicate", aliases)
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
    parser.add_argument("--expected-packet-sha256", required=True)
    parser.add_argument("--expected-charter-sha256")
    parser.add_argument("--receipt-out")
    parser.add_argument("--launch-environment-attestation")
    parser.add_argument("--contamination-disclosure")
    return parser


def _write_receipt_exclusive(path: Path, output: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as handle:
        handle.write(output)


def _cli_refusal() -> dict[str, Any]:
    return _refuse(
        _base_receipt(
            packet_arg=None,
            charter_arg=None,
            expected_packet_sha256=None,
            expected_charter_sha256=None,
            launch_environment_attestation=None,
            contamination_disclosure=None,
        ),
        "cli_invalid",
    )


def _run(argv: Sequence[str] | None) -> int:
    try:
        args = _parser().parse_args(argv)
    except CliError:
        sys.stdout.buffer.write(_canonical_json(_cli_refusal()))
        return REFUSAL_EXIT

    receipt = validate(
        packet_arg=args.packet,
        charter_arg=args.charter,
        expected_packet_sha256=args.expected_packet_sha256,
        expected_charter_sha256=args.expected_charter_sha256,
        receipt_out_arg=args.receipt_out,
        launch_environment_attestation=args.launch_environment_attestation,
        contamination_disclosure=args.contamination_disclosure,
    )
    output = _canonical_json(receipt)
    if args.receipt_out is not None:
        receipt_target_reason = _receipt_out_reason(
            args.receipt_out,
            Path(args.packet) if args.packet is not None else Path(""),
            Path(args.charter) if args.charter is not None else Path(""),
        )
        if receipt_target_reason is None:
            try:
                _write_receipt_exclusive(Path(args.receipt_out), output)
            except (OSError, ValueError):
                receipt = _refuse(
                    receipt,
                    "receipt_write_failed",
                    [{"path": _basename(args.receipt_out)}],
                )
                output = _canonical_json(receipt)
    sys.stdout.buffer.write(output)
    return 0 if receipt["result"] == "PASS" else REFUSAL_EXIT


def main(argv: Sequence[str] | None = None) -> int:
    try:
        return _run(argv)
    except NonValidationExit:
        return REFUSAL_EXIT
    except SystemExit:
        return REFUSAL_EXIT
    except Exception:
        receipt = _refuse(_cli_refusal(), "internal_error")
        sys.stdout.buffer.write(_canonical_json(receipt))
        return REFUSAL_EXIT


if __name__ == "__main__":
    raise SystemExit(main())
