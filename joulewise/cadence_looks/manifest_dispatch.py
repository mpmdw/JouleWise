"""Dispatch cadence manifest validation without editing the pinned v1 entry point."""

from __future__ import annotations

import argparse
import errno
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import NoReturn
import warnings

from . import qualification_manifest as schema_check

V1 = "joulewise.cadence_look_manifest.v1"
V2 = "joulewise.cadence_look_manifest.v2"
PRE_READ_REFUSAL = 2
REGISTRATION_PLACEHOLDER = b'"PENDING:CODE"'
V2_SCHEMA = schema_check._SCHEMA
V1_TOOL = V2_SCHEMA.parents[4] / "scripts/cadence_look_manifest.py"
ManifestError = schema_check.ManifestError

TRANSFER_PRINTS = (
    "daily_errors",
    "evaluable_dates",
    "largest_absolute_daily_error",
    "days_within_comparison_cutoff",
    "mean_signed_error_and_interval",
    "pooled_signed_error",
    "date_map",
)


def redirect_to_devnull(fd):
    replacement = os.open(os.devnull, os.O_RDWR)
    try:
        os.dup2(replacement, fd)
        if replacement == fd:
            os.set_inheritable(fd, True)
    finally:
        if replacement != fd:
            os.close(replacement)


def save_public_stderr():
    """Fill vacant standard descriptors before reserving private redirections."""
    for fd in range(3):
        try:
            fcntl.fcntl(fd, fcntl.F_GETFD)
        except OSError as error:
            if error.errno != errno.EBADF:
                raise
            redirect_to_devnull(fd)
    return fcntl.fcntl(2, fcntl.F_DUPFD_CLOEXEC, 10)


def _write_notice(fd, message):
    remaining = memoryview(message.encode("utf-8", errors="backslashreplace"))
    while remaining:
        count = os.write(fd, remaining)
        if count == 0:
            raise OSError("notice write made no progress")
        remaining = remaining[count:]


def finish_notice(status, *, stdout=None, stderr=None, stderr_fd=None, flush_streams=False):
    """Attempt delivery and report stream failure on a success path."""
    failed = False
    if stderr_fd is not None and stderr is not None:
        try:
            _write_notice(stderr_fd, stderr)
        except BaseException:
            failed = True
        stderr = None

    for fd, stream, message in ((1, sys.stdout, stdout), (2, sys.stderr, stderr)):
        if message is None and not flush_streams:
            continue
        try:
            if stream is None:
                if message is not None:
                    _write_notice(fd, message)
            else:
                if message is not None:
                    stream.write(message)
                stream.flush()
        except BaseException:
            failed = True

    return PRE_READ_REFUSAL if failed and status == 0 else status


def exit_with_failure(status, notice, *, stderr_fd=None, flush_streams=False) -> NoReturn:
    try:
        finish_notice(status, stderr=notice(), stderr_fd=stderr_fd, flush_streams=flush_streams)
    except BaseException:
        pass
    # This is the process boundary. A Python shutdown flush cannot choose
    # a different status, even if the process has no available descriptor.
    os._exit(status)


class _ParserExit(SystemExit):
    """A normal exit selected by this argparse frontend."""


class _NoticeArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, stderr_fd=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._stderr_fd = stderr_fd

    def _print_message(self, message, file=None):
        if message:
            if file is sys.stdout:
                status = finish_notice(0, stdout=message)
            else:
                status = finish_notice(0, stderr=message, stderr_fd=self._stderr_fd)
            if status:
                raise _ParserExit(status)

    def error(self, message):
        self.exit(PRE_READ_REFUSAL, f"{self.format_usage()}{self.prog}: error: {message}\n")

    def exit(self, status=0, message=None):
        if message:
            status = finish_notice(status, stderr=message, stderr_fd=self._stderr_fd)
        raise _ParserExit(status)


def _validate_transfer(document):
    kits = document["reads"]["kits"]
    if [kit["kit_id"] for kit in kits] != [f"cl-transfer-{place:02}" for place in range(1, 21)]:
        raise ManifestError("the transfer kit family must follow the twenty original date places")
    prints = document["estimate"]["restricted_prints"]
    if tuple(row["id"] for row in prints) != TRANSFER_PRINTS:
        raise ManifestError("the transfer print inventory must name each ruled print once")


def _validate_description(document):
    instrument = document["look_id"] == "lm-inst-01"
    kit_ids = [kit["kit_id"] for kit in document["kits"]]
    prefix = "f2-inst-" if instrument else "f2-stab-"
    if len(set(kit_ids)) != len(kit_ids) or any(not kit.startswith(prefix) for kit in kit_ids):
        raise ManifestError("the description must name distinct kits from its own filler series")
    channels = document["channels"]
    if len(set(channels)) != len(channels):
        raise ManifestError("description channels must be distinct")
    outputs = document["outputs"]
    names = ["hold.json", "turn.json"]
    names += ["gain.json", "edges.json"] if instrument else ["date_spreads.json", "context.json"]
    counts = ["n_legs"] if instrument else ["n_legs", "n_local_dates"]
    if outputs["custody_names"] != [*names, "stdout", "stderr"] or outputs["counts"] != counts:
        raise ManifestError("description output inventory differs from the selected look")
    if {row["destination"] for row in document["prints"]} != set(names):
        raise ManifestError("description prints must cover exactly the selected look's destinations")


def _validate_shape(document, definitions):
    kind = document.get("look_kind")
    if kind not in ("qualification", "description", "transfer"):
        raise ManifestError("expected v2 look_kind qualification, description or transfer")
    pins = {}
    schema_check._check(document, definitions[kind], definitions, pins)
    if kind == "transfer":
        _validate_transfer(document)
    if kind == "description":
        _validate_description(document)
    return pins


def _transfer_final(registration, candidate, pins, definitions):
    if registration is None:
        raise ManifestError("transfer final validation requires the exact registered manifest bytes")
    registered = schema_check._decode(registration)
    if not isinstance(registered, dict) or (
        registered.get("schema"), registered.get("look_kind"), registered.get("status")
    ) != (V2, "transfer", "registered"):
        raise ManifestError("expected a registered transfer manifest")
    pending = _validate_shape(registered, definitions)
    if pending.keys() != pins.keys() or any(value != "PENDING:CODE" for value in pending.values()):
        raise ManifestError("registration must leave every code hash slot pending")
    sections = registration.split(REGISTRATION_PLACEHOLDER)
    if len(sections) != len(pending) + 1:
        raise ManifestError("code hash placeholders must be literal JSON strings")
    # The schema walk follows byte order. Rebuild the exact registered bytes with the final hashes.
    expected = [sections[0]]
    for path, suffix in zip(pending, sections[1:], strict=True):
        expected.extend((b'"', pins[path].encode("ascii"), b'"', suffix))
    if b"".join(expected) != candidate:
        raise ManifestError("final manifest differs outside the registered hash slots")


def validate_v2(payload: bytes, *, final=False, registration: bytes | None = None) -> dict:
    """Check the closed v2 variant and, for final transfer or qualification, its registration."""
    document = schema_check._decode(payload)
    if not isinstance(document, dict) or document.get("schema") != V2:
        raise ManifestError("expected the v2 cadence manifest schema ID")
    kind = document.get("look_kind")
    if kind == "qualification":
        if not final:
            return schema_check.validate_registration(payload)
        if registration is None:
            raise ManifestError("qualification final validation requires the exact registered manifest bytes")
        return schema_check.validate_final(registration, payload)

    definitions = json.loads(V2_SCHEMA.read_bytes())["$defs"]
    pins = _validate_shape(document, definitions)
    if not final:
        return document

    if document["status"] == "draft":
        raise ManifestError("a draft cannot pass final validation")
    if "PENDING:CODE" in pins.values():
        raise ManifestError("final manifest contains PENDING:CODE")
    if kind == "transfer":
        _transfer_final(registration, payload, pins, definitions)
    return document


def _dispatch(argv, *, stderr_fd=None):
    parser = _NoticeArgumentParser(description=__doc__, stderr_fd=stderr_fd)
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate", stderr_fd=stderr_fd)
    validate.add_argument("manifest", type=Path)
    validate.add_argument("--final", action="store_true")
    validate.add_argument("--registration", type=Path, help="exact trusted v2 scientific registration bytes")
    validate.add_argument("--v1-tool", type=Path, default=V1_TOOL,
                          help="pinned v1 cadence_look_manifest.py when it lives on a separate checkout")
    try:
        args = parser.parse_args(argv)
    except _ParserExit as completion:
        return completion.code
    try:
        payload = args.manifest.read_bytes()
        document = schema_check._decode(payload)
        schema = document.get("schema") if isinstance(document, dict) else None
        if schema == V1:
            if args.registration is not None:
                raise ManifestError("--registration applies to v2 manifests")
            if not args.v1_tool.is_file():
                raise ManifestError("pinned v1 entry point unavailable, supply --v1-tool")
            command = [sys.executable, "-B", "-W", "ignore", str(args.v1_tool), "validate", str(args.manifest)]
            if args.final:
                command.append("--final")
            result = subprocess.run(command, check=False, capture_output=True, text=True,
                                    encoding="utf-8", errors="replace")
            status = PRE_READ_REFUSAL if result.returncode else 0
            return finish_notice(status, stdout=result.stdout or None, stderr=result.stderr or None,
                                 stderr_fd=stderr_fd)
        if schema != V2:
            raise ManifestError("unknown cadence manifest schema ID")
        if args.registration is not None and not args.final:
            raise ManifestError("--registration requires --final")
        registration = args.registration.read_bytes() if args.registration else None
        doc = validate_v2(payload, final=args.final, registration=registration)
    except (ManifestError, OSError) as error:
        return finish_notice(PRE_READ_REFUSAL, stderr=f"REFUSE {error}\n", stderr_fd=stderr_fd)
    return finish_notice(0, stdout=f"ok {doc['look_id']} ({doc['status']})\n")


def main(argv=None) -> NoReturn:
    stderr_fd = None
    try:
        warnings.simplefilter("ignore")
        sys.warnoptions = []
        stderr_fd = save_public_stderr()
        redirect_to_devnull(2)
        if _dispatch(argv, stderr_fd=stderr_fd):
            os._exit(PRE_READ_REFUSAL)
        if finish_notice(0, flush_streams=True):
            raise OSError("validation output could not be flushed")
    except BaseException as error:
        exit_with_failure(PRE_READ_REFUSAL, lambda: f"REFUSE {error}\n", stderr_fd=stderr_fd)
    os._exit(0)


if __name__ == "__main__":
    main()
