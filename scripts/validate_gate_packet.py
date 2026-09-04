#!/usr/bin/env python3
"""Validate the exact bytes of a frozen cold-gate packet.

Packet grammar (intentionally strict and fail-closed):

* Exactly one outside-fence ATX heading, at any level, has the title
  ``Charter pin``
  after an optional numeric section prefix (for example,
  ``## 6. Charter pin``).  Its Markdown section extends to the next heading
  of the same or a higher level.  The section must contain exactly one
  single-line ``Charter ...: `path` `` declaration using a nonempty relative
  POSIX path, exactly one ``sha256`` label, and exactly one standalone 64-hex
  digest, in that order.  Digest text elsewhere in the packet is irrelevant.
* Exactly one outside-fence ATX heading, at any level, has the title
  ``Exhibit manifest`` after an optional numeric prefix and before an optional
  parenthetical.
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

Exit status zero is reserved for a validated ``PASS``.  Usage and argument
errors emit a machine-readable refusal receipt and exit nonzero.  ``--help``
alone is an informational path: it emits ordinary help text, no receipt, and
exits zero.

A ``PASS`` means only that the bytes observed by this invocation matched the
supplied anchors and manifest at validation time.  It is not launch
authorization and does not bind a later judge handoff to those bytes.
"""

from __future__ import annotations

import argparse
import errno
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
from typing import Any, BinaryIO, NamedTuple, Sequence


RECEIPT_SCHEMA = "coldgate-validator-receipt/v2"
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
MARKDOWN_FENCE_OPEN_RE = re.compile(
    r"^ {0,3}(?:(`{3,})[^`]*|(~{3,}).*)$"
)
WINDOWS_DRIVE_RE = re.compile(r"^[A-Za-z]:")


class CliError(Exception):
    """Raised instead of argparse terminating without a refusal receipt."""


class FrozenExhibit(NamedTuple):
    """One manifest-listed exhibit captured as immutable in-process bytes."""

    manifest_path: str
    data: bytes

    @property
    def sha256(self) -> str:
        return _sha256(self.data)


class ValidatedGateSnapshot(NamedTuple):
    """The exact packet, charter, and exhibit bytes accepted together."""

    packet_name: str
    packet_bytes: bytes
    charter_name: str
    charter_bytes: bytes
    exhibits: tuple[FrozenExhibit, ...]


class ReceiptArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise CliError(message)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_handle_once(handle: BinaryIO) -> bytes:
    chunks: list[bytes] = []
    while True:
        chunk = handle.read(1024 * 1024)
        if not chunk:
            return b"".join(chunks)
        chunks.append(chunk)


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
    return None


def _base_receipt(
    *,
    packet_arg: str | None,
    charter_arg: str | None,
    expected_packet_sha256: str | None,
    expected_charter_sha256: str | None,
) -> dict[str, Any]:
    return {
        "binding_scope": "validation_time_observation_only",
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
        "judge_handoff_bound": False,
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


def _outside_fence_mask(lines: list[str]) -> list[bool]:
    """Return a raw-line-indexed mask from one Markdown fence-state scan."""
    outside: list[bool] = []
    marker: str | None = None
    opening_length = 0
    for line in lines:
        if marker is None:
            opening = MARKDOWN_FENCE_OPEN_RE.fullmatch(line)
            if opening is None:
                outside.append(True)
                continue
            fence = opening.group(1) or opening.group(2)
            assert fence is not None
            marker = fence[0]
            opening_length = len(fence)
            outside.append(False)
            continue

        outside.append(False)
        closing = re.fullmatch(
            rf" {{0,3}}{re.escape(marker)}{{{opening_length},}}[ \t]*", line
        )
        if closing is not None:
            marker = None
            opening_length = 0
    return outside


def _section_end(
    lines: list[str], outside_fence: list[bool], heading_index: int, level: int
) -> int:
    for index in range(heading_index + 1, len(lines)):
        if not outside_fence[index]:
            continue
        parsed = _heading(lines[index])
        if parsed is not None and parsed[0] <= level:
            return index
    return len(lines)


def _parse_charter_pin(
    lines: list[str], outside_fence: list[bool]
) -> tuple[str, str, str | None]:
    headings: list[tuple[int, int]] = []
    for index, line in enumerate(lines):
        if not outside_fence[index]:
            continue
        parsed = _heading(line)
        if parsed is not None and CHARTER_TITLE_RE.fullmatch(parsed[1]):
            headings.append((index, parsed[0]))

    if not headings:
        return "", "", "charter_pin_missing"
    if len(headings) != 1:
        return "", "", "charter_pin_duplicate"

    index, level = headings[0]
    section = "\n".join(
        lines[index + 1 : _section_end(lines, outside_fence, index, level)]
    )
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
    raw_lines: list[bytes], text_lines: list[str], outside_fence: list[bool]
) -> tuple[bytes | None, list[str] | None, str | None]:
    headings: list[tuple[int, int]] = []
    for index, line in enumerate(text_lines):
        if not outside_fence[index]:
            continue
        parsed = _heading(line)
        if parsed is not None and MANIFEST_TITLE_RE.fullmatch(parsed[1]):
            headings.append((index, parsed[0]))
    if len(headings) != 1:
        return None, None, "manifest_parse_error"

    index, level = headings[0]
    end = _section_end(text_lines, outside_fence, index, level)
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


def _open_exhibit(
    packet_directory_fd: int, exhibit_path: str
) -> tuple[FrozenExhibit | None, tuple[int, int] | None, str | None]:
    components = PurePosixPath(exhibit_path).parts
    directory_fd: int | None = None
    try:
        directory_fd = os.dup(packet_directory_fd)
        directory_flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_DIRECTORY
        for component in components[:-1]:
            next_directory_fd = os.open(
                component, directory_flags, dir_fd=directory_fd
            )
            os.close(directory_fd)
            directory_fd = next_directory_fd

        leaf_flags = os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_NONBLOCK", 0)
        descriptor = os.open(components[-1], leaf_flags, dir_fd=directory_fd)
        with os.fdopen(descriptor, "rb") as handle:
            opened_stat = os.fstat(handle.fileno())
            if not stat.S_ISREG(opened_stat.st_mode):
                return None, None, "exhibit_custody_invalid"
            data = _read_handle_once(handle)
            return (
                FrozenExhibit(
                    manifest_path=exhibit_path,
                    data=data,
                ),
                (opened_stat.st_dev, opened_stat.st_ino),
                None,
            )
    except OSError as error:
        if error.errno in {errno.EISDIR, errno.ELOOP, errno.ENOTDIR}:
            return None, None, "exhibit_custody_invalid"
        return None, None, "exhibit_unreadable"
    except (RuntimeError, ValueError):
        return None, None, "exhibit_unreadable"
    finally:
        if directory_fd is not None:
            os.close(directory_fd)


def capture_and_validate(
    *,
    packet_arg: str | None,
    charter_arg: str | None,
    expected_packet_sha256: str | None,
    expected_charter_sha256: str | None,
) -> tuple[dict[str, Any], ValidatedGateSnapshot | None]:
    """Validate once-read inputs and return their immutable bytes only on PASS."""
    receipt = _base_receipt(
        packet_arg=packet_arg,
        charter_arg=charter_arg,
        expected_packet_sha256=expected_packet_sha256,
        expected_charter_sha256=expected_charter_sha256,
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
        return _refuse(receipt, "cli_invalid", [{"missing": missing}]), None
    if not HEX_RE.fullmatch(expected_packet_sha256):
        return _refuse(receipt, "expected_packet_sha256_invalid"), None
    if not HEX_RE.fullmatch(expected_charter_sha256):
        return _refuse(receipt, "expected_charter_sha256_invalid"), None

    trusted_packet_sha256 = expected_packet_sha256.lower()
    trusted_charter_sha256 = expected_charter_sha256.lower()
    packet_path = Path(packet_arg)
    charter_path = Path(charter_arg)

    packet_bytes = _read_once(packet_path)
    if packet_bytes is None:
        return (
            _refuse(receipt, "packet_unreadable", [{"path": packet_path.name}]),
            None,
        )
    observed_packet_sha256 = _sha256(packet_bytes)
    receipt["digests"]["packet_sha256"] = observed_packet_sha256
    if observed_packet_sha256 != trusted_packet_sha256:
        return _refuse(receipt, "packet_digest_mismatch"), None

    charter_bytes = _read_once(charter_path)
    if charter_bytes is None:
        return (
            _refuse(receipt, "charter_unreadable", [{"path": charter_path.name}]),
            None,
        )
    observed_charter_sha256 = _sha256(charter_bytes)
    receipt["digests"]["charter_sha256"] = observed_charter_sha256

    try:
        packet_text = packet_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return _refuse(receipt, "packet_not_utf8"), None
    raw_lines = packet_bytes.splitlines(keepends=True)
    text_lines = [line.decode("utf-8").rstrip("\r\n") for line in raw_lines]
    outside_fence = _outside_fence_mask(text_lines)

    packet_charter_path, packet_pin, pin_error = _parse_charter_pin(
        text_lines, outside_fence
    )
    if pin_error is not None:
        return _refuse(receipt, pin_error), None
    receipt["packet_charter_path"] = packet_charter_path
    receipt["packet_charter_pin_sha256"] = packet_pin

    mismatch_reason = _charter_mismatch_reason(
        trusted_charter_sha256, packet_pin, observed_charter_sha256
    )
    if mismatch_reason is not None:
        return _refuse(receipt, mismatch_reason), None

    manifest_body, manifest_lines, manifest_error = _manifest_block(
        raw_lines, text_lines, outside_fence
    )
    if manifest_body is not None:
        receipt["digests"]["exhibit_manifest_sha256"] = _sha256(manifest_body)
    if manifest_error is not None or manifest_lines is None:
        return _refuse(receipt, "manifest_parse_error"), None
    manifest, manifest_error = _parse_manifest_lines(manifest_lines)
    if manifest_error is not None or manifest is None:
        return _refuse(receipt, "manifest_parse_error"), None

    try:
        packet_directory = packet_path.parent.resolve(strict=True)
    except (OSError, RuntimeError, ValueError):
        return (
            _refuse(receipt, "packet_unreadable", [{"path": packet_path.name}]),
            None,
        )

    packet_directory_flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_DIRECTORY
    try:
        packet_directory_fd = os.open(packet_directory, packet_directory_flags)
    except OSError:
        return (
            _refuse(receipt, "packet_unreadable", [{"path": packet_path.name}]),
            None,
        )

    try:
        unreadable: list[dict[str, Any]] = []
        custody_invalid: list[dict[str, Any]] = []
        mismatches: list[dict[str, Any]] = []
        aliases: list[dict[str, Any]] = []
        exhibit_receipts: list[dict[str, Any]] = []
        exhibit_snapshots: list[FrozenExhibit] = []
        seen_identities: dict[tuple[int, int], str] = {}
        for exhibit_expected, exhibit_path in manifest:
            exhibit_name = Path(exhibit_path).name
            exhibit_snapshot, identity, exhibit_error = _open_exhibit(
                packet_directory_fd, exhibit_path
            )
            exhibit_observed = (
                exhibit_snapshot.sha256 if exhibit_snapshot is not None else None
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
            if exhibit_snapshot is not None:
                exhibit_snapshots.append(exhibit_snapshot)
            if exhibit_observed is not None and exhibit_observed != exhibit_expected:
                mismatches.append({"path": exhibit_name})
    finally:
        os.close(packet_directory_fd)
    receipt["digests"]["exhibits"] = exhibit_receipts

    if unreadable:
        return _refuse(receipt, "exhibit_unreadable", unreadable), None
    if custody_invalid:
        return _refuse(receipt, "exhibit_custody_invalid", custody_invalid), None
    if aliases:
        return _refuse(receipt, "exhibit_alias_duplicate", aliases), None
    if mismatches:
        return _refuse(receipt, "exhibit_digest_mismatch", mismatches), None

    receipt["result"] = "PASS"
    receipt["reason"] = None
    receipt["details"] = []
    return receipt, ValidatedGateSnapshot(
        packet_name=packet_path.name,
        packet_bytes=packet_bytes,
        charter_name=charter_path.name,
        charter_bytes=charter_bytes,
        exhibits=tuple(exhibit_snapshots),
    )


def validate(
    *,
    packet_arg: str | None,
    charter_arg: str | None,
    expected_packet_sha256: str | None,
    expected_charter_sha256: str | None,
) -> dict[str, Any]:
    """Validate arguments and inputs while preserving the validator v2 API."""
    receipt, _snapshot = capture_and_validate(
        packet_arg=packet_arg,
        charter_arg=charter_arg,
        expected_packet_sha256=expected_packet_sha256,
        expected_charter_sha256=expected_charter_sha256,
    )
    return receipt


def _canonical_json(receipt: dict[str, Any]) -> bytes:
    return (
        json.dumps(receipt, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        + "\n"
    ).encode("utf-8")


def _parser() -> ReceiptArgumentParser:
    parser = ReceiptArgumentParser(
        description=__doc__,
        epilog=(
            "PASS means only that this invocation observed bytes matching the "
            "supplied anchors and manifest at validation time. PASS is not launch "
            "authorization and does not bind a judge handoff."
        ),
    )
    parser.add_argument("--packet")
    parser.add_argument("--charter")
    parser.add_argument("--expected-packet-sha256", required=True)
    parser.add_argument("--expected-charter-sha256")
    return parser


def _cli_refusal() -> dict[str, Any]:
    return _refuse(
        _base_receipt(
            packet_arg=None,
            charter_arg=None,
            expected_packet_sha256=None,
            expected_charter_sha256=None,
        ),
        "cli_invalid",
    )


def _emit_receipt(receipt: dict[str, Any]) -> int:
    output = _canonical_json(receipt)
    sys.stdout.buffer.write(output)
    return 0 if receipt["result"] == "PASS" else REFUSAL_EXIT


def _run(argv: Sequence[str] | None) -> int:
    try:
        args = _parser().parse_args(argv)
    except CliError:
        return _emit_receipt(_cli_refusal())

    receipt = validate(
        packet_arg=args.packet,
        charter_arg=args.charter,
        expected_packet_sha256=args.expected_packet_sha256,
        expected_charter_sha256=args.expected_charter_sha256,
    )
    return _emit_receipt(receipt)


def main(argv: Sequence[str] | None = None) -> int:
    try:
        return _run(argv)
    except SystemExit as error:
        if error.code == 0:
            return 0
        return _emit_receipt(_cli_refusal())
    except Exception:
        receipt = _refuse(_cli_refusal(), "internal_error")
        return _emit_receipt(receipt)


if __name__ == "__main__":
    raise SystemExit(main())
