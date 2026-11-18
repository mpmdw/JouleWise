"""Dispatch cadence manifest validation without editing the pinned v1 entry point."""

from __future__ import annotations

import argparse
import errno
import fcntl
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory
from typing import NoReturn

from . import qualification_manifest as schema_check

V1 = "joulewise.cadence_look_manifest.v1"
V2 = "joulewise.cadence_look_manifest.v2"
PRE_READ_REFUSAL = 2
REGISTRATION_PLACEHOLDER = b'"PENDING:CODE"'
FINAL_PLACEHOLDER = re.compile(r"PENDING:CODE|OPEN-[0-9]+")
V2_SCHEMA = schema_check._SCHEMA
V1_TOOL = V2_SCHEMA.parents[4] / "scripts/cadence_look_manifest.py"
KIT_COMMITMENTS = V2_SCHEMA.with_name("look-kit-commitments.v2.json")
FILLER_KIT_REGISTRY = V2_SCHEMA.with_name("filler-kit-registry.json")
ManifestError = schema_check.ManifestError

_MANIFEST_ROUTES = frozenset((
    (V1, "interim", "lm-interim-01"),
    (V2, "qualification", "lm-qual-01"),
    (V2, "description", "lm-inst-01"),
    (V2, "description", "lm-stab-01"),
    (V2, "description", "lm-stab-02"),
    (V2, "transfer", "lm-transfer-01"),
))

TRANSFER_PRINTS = (
    "daily_errors",
    "evaluable_dates",
    "largest_absolute_daily_error",
    "days_within_comparison_cutoff",
    "mean_signed_error_and_interval",
    "pooled_signed_error",
    "date_map",
)


def save_public_stderr():
    """Fill vacant standard descriptors before reserving private redirections."""
    for fd, name, mode in ((0, "stdin", "r"), (1, "stdout", "w"), (2, "stderr", "w")):
        try:
            fcntl.fcntl(fd, fcntl.F_GETFD)
        except OSError as error:
            if error.errno != errno.EBADF:
                raise
            replacement = os.open(os.devnull, os.O_RDWR)
            if replacement == fd:
                os.set_inheritable(fd, True)
            else:
                try:
                    os.dup2(replacement, fd)
                finally:
                    os.close(replacement)
        # Python can leave its stream unset when the descriptor was closed at exec.
        if getattr(sys, name) is None:
            setattr(sys, name, os.fdopen(fd, mode, closefd=False))
    return fcntl.fcntl(2, fcntl.F_DUPFD_CLOEXEC, 10)


def finish_notice(status, *, stdout=None, stderr=None, stderr_fd=None, flush_streams=False):
    """Attempt delivery and report stream failure on a success path."""
    failed = False
    if stderr_fd is not None and stderr is not None:
        try:
            with os.fdopen(stderr_fd, "w", encoding="utf-8", errors="backslashreplace", closefd=False) as stream:
                stream.write(stderr)
                stream.flush()
        except BaseException:
            failed = True
        stderr = None

    for stream, message in ((sys.stdout, stdout), (sys.stderr, stderr)):
        if message is None and not flush_streams:
            continue
        if stream is None:
            failed = True
            continue
        try:
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

    def exit(self, status=0, message=None):
        self._print_message(message, sys.stderr)
        raise _ParserExit(status)


def _manifest_route(document):
    if not isinstance(document, dict) or document.get("schema") not in (V1, V2):
        raise ManifestError("unknown cadence manifest schema ID")
    route = (document["schema"], document.get("look_kind"), document.get("look_id"))
    if not all(isinstance(value, str) for value in route) or route not in _MANIFEST_ROUTES:
        raise ManifestError("unrecognized cadence manifest schema, look_kind and look_id combination")
    return route


def _reject_filler_kits(document, kind):
    if kind == "description":
        return

    registry = schema_check._decode(FILLER_KIT_REGISTRY.read_bytes())
    registered = registry["kit_sha256_by_id"]
    filler_ids = {kit_id.casefold() for kit_id in (*registered, *registry["other_ids"])}
    filler_digests = frozenset(registered.values())
    filler_prefixes = ("f2-inst-", "f2-stab-", "r1-partc-f0-")
    pending = [(document, False)]
    while pending:
        value, in_kit = pending.pop()
        if isinstance(value, list):
            pending.extend((item, in_kit) for item in value)
        elif isinstance(value, dict):
            identifiers = [value.get("block_id"), value.get("kit_id")]
            digests = [value.get("kit_sha256")]
            # Unqualified sha256 fields elsewhere bind files such as schemas, not kits.
            if in_kit or "kit_id" in value:
                identifiers.append(value.get("id"))
                digests.append(value.get("sha256"))
            matched_id = any(
                kit_id in filler_ids or kit_id.startswith(filler_prefixes)
                for kit_id in (item.casefold() for item in identifiers if isinstance(item, str))
            )
            matched_digest = any(
                digest.lower() in filler_digests for digest in digests if isinstance(digest, str)
            )
            if matched_id or matched_digest or value.get("queue_class") == "filler":
                raise ManifestError("counted roster references a filler kit")
            pending.extend((item, key in ("kit", "kits")) for key, item in value.items())


def _validate_transfer(document, commitments):
    record = commitments[document["look_id"]]
    reads = document["reads"]
    if reads["planned_date_places"] != record["planned_date_places"]:
        raise ManifestError("transfer date-place roster commitment differs from the published roster")
    if len(reads["kits"]) != len(record["kits"]):
        raise ManifestError("transfer kit commitment count differs from the published roster")
    for actual, expected in zip(reads["kits"], record["kits"], strict=True):
        if actual != expected:
            raise ManifestError(f"{expected['kit_id']}: kit commitment differs from the published date place")
    prints = document["estimate"]["restricted_prints"]
    if tuple(row["id"] for row in prints) != TRANSFER_PRINTS:
        raise ManifestError("the transfer print inventory must name each ruled print once")


def _validate_description(document, commitments):
    instrument = document["look_id"] == "lm-inst-01"
    source_look = "lm-inst-01" if instrument else "lm-stab-01"
    expected = commitments[source_look]["kit_sha256_by_id"]
    actual = {kit["kit_id"]: kit["sha256"] for kit in document["kits"]}
    if len(actual) != len(document["kits"]) or actual.keys() != expected.keys():
        raise ManifestError("the description must name every kit from its own filler series once")
    for kit_id, digest in actual.items():
        if digest != expected[kit_id]:
            raise ManifestError(f"{kit_id}: kit commitment differs from the published filler kit")
    channels = document["channels"]
    if len(set(channels)) != len(channels):
        raise ManifestError("description channels must be distinct")
    if "rail_sum" in channels and "rail_sum_columns" not in document:
        raise ManifestError("a description with rail_sum requires rail_sum_columns")
    kit_index = document.get("kit_index_path")
    if kit_index is not None and (
        document["look_id"] != "lm-stab-02" or Path(kit_index).parts[-2:] != ("f2-stab", "KITS.json")
    ):
        raise ManifestError("only lm-stab-02 can name the f2-stab/KITS.json index")
    outputs = document["outputs"]
    names = ["hold.json", "turn.json"]
    names += ["gain.json", "edges.json"] if instrument else ["date_spreads.json", "context.json"]
    counts = ["n_legs"] if instrument else ["n_legs", "n_local_dates"]
    if outputs["custody_names"] != [*names, "stdout", "stderr"] or outputs["counts"] != counts:
        raise ManifestError("description output inventory differs from the selected look")
    if {row["destination"] for row in document["prints"]} != set(names):
        raise ManifestError("description prints must cover exactly the selected look's destinations")


def _validate_shape(document, kind, definitions, commitments):
    pins = {}
    schema_check._check(document, definitions[kind], definitions, pins)
    if kind == "transfer":
        _validate_transfer(document, commitments)
    elif kind == "description":
        _validate_description(document, commitments)
    return pins


def _transfer_final(registration, candidate, pins, definitions, commitments):
    registered = schema_check._decode(registration)
    schema, kind, _ = _manifest_route(registered)
    if (schema, kind, registered.get("status")) != (V2, "transfer", "registered"):
        raise ManifestError("expected a registered transfer manifest")
    _reject_filler_kits(registered, kind)
    pending = _validate_shape(registered, kind, definitions, commitments)
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


def _reject_final_placeholders(document):
    # Search decoded strings, including object keys and strings in arrays.
    marker = FINAL_PLACEHOLDER.search(json.dumps(document))
    if marker:
        raise ManifestError(f"final manifest contains {marker.group()}")


def _validate_legacy(tool, payload, final, *, stderr_fd=None):
    if not tool.is_file():
        raise ManifestError("pinned v1 entry point unavailable, supply --v1-tool")
    # Keep the delegated check on the exact bytes used for dispatch.
    with TemporaryDirectory(prefix="cadence-v1-manifest-") as directory:
        manifest = Path(directory) / "manifest.json"
        manifest.write_bytes(payload)
        command = [sys.executable, "-B", str(tool), "validate", str(manifest)]
        if final:
            command.append("--final")
        result = subprocess.run(command, check=False, capture_output=True, text=True,
                                encoding="utf-8", errors="replace")
        status = PRE_READ_REFUSAL if result.returncode else 0
        return finish_notice(status, stdout=result.stdout or None, stderr=result.stderr or None,
                             stderr_fd=stderr_fd)


def _check_registration_use(document, kind, final):
    if not final:
        raise ManifestError("--registration requires --final")
    if kind not in ("qualification", "transfer") or document.get("status") != "registered":
        raise ManifestError("--registration requires a registered qualification or transfer final")


def _validate_qualification(payload, final, read_registration, commitments):
    if final:
        document, _ = schema_check._parse(payload)
        schema_check._check_registered_kits(document)
    else:
        document = schema_check.validate_registration(payload)

    look_id = document["look_id"]
    record = commitments.get(look_id)
    if record is None:
        raise ManifestError(f"{look_id}: no independent qualification span commitments")
    expected = record["span_ids_by_block"]
    for block in document["reads"]["blocks"]:
        block_id = block["block_id"]
        if block["spans"] != expected.get(block_id):
            raise ManifestError(f"{block_id}: span commitment differs from the published qualification queue")

    if final:
        if read_registration is None:
            raise ManifestError("qualification final validation requires the exact registered manifest bytes")
        return schema_check.validate_final(read_registration(), payload)
    return document


def _validate_v2_document(payload, document, kind, final, read_registration):
    _reject_filler_kits(document, kind)
    if read_registration is not None:
        _check_registration_use(document, kind, final)
    if final and document.get("status") != "draft":
        _reject_final_placeholders(document)
    commitments = schema_check._decode(KIT_COMMITMENTS.read_bytes())
    if kind == "qualification":
        return _validate_qualification(payload, final, read_registration, commitments)

    definitions = json.loads(V2_SCHEMA.read_bytes())["$defs"]
    pins = _validate_shape(document, kind, definitions, commitments)
    if not final:
        return document

    if document["status"] == "draft":
        raise ManifestError("a draft cannot pass final validation")
    if kind == "transfer":
        if read_registration is None:
            raise ManifestError("transfer final validation requires the exact registered manifest bytes")
        _transfer_final(read_registration(), payload, pins, definitions, commitments)
    elif document["look_id"] == "lm-stab-02" and "kit_index_path" not in document:
        raise ManifestError("final lm-stab-02 must name the f2-stab/KITS.json index")
    return document


def validate_v2(payload: bytes, *, final=False, registration: bytes | None = None) -> dict:
    """Check the closed v2 variant and, for final transfer or qualification, its registration."""
    document = schema_check._decode(payload)
    schema, kind, _ = _manifest_route(document)
    if schema != V2:
        raise ManifestError("expected the v2 cadence manifest schema ID")
    read_registration = None if registration is None else lambda: registration
    return _validate_v2_document(payload, document, kind, final, read_registration)


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
        schema, kind, _ = _manifest_route(document)
        if schema == V1:
            _reject_filler_kits(document, kind)
            if args.registration is not None:
                raise ManifestError("--registration applies to v2 manifests")
            if args.final:
                _reject_final_placeholders(document)
            return _validate_legacy(args.v1_tool, payload, args.final, stderr_fd=stderr_fd)
        read_registration = args.registration.read_bytes if args.registration is not None else None
        doc = _validate_v2_document(payload, document, kind, args.final, read_registration)
    except (ManifestError, OSError) as error:
        return finish_notice(PRE_READ_REFUSAL, stderr=f"REFUSE {error}\n", stderr_fd=stderr_fd)
    return finish_notice(0, stdout=f"ok {doc['look_id']} ({doc['status']})\n")


def main(argv=None) -> NoReturn:
    stderr_fd = None
    try:
        stderr_fd = save_public_stderr()
        if _dispatch(argv, stderr_fd=stderr_fd):
            os._exit(PRE_READ_REFUSAL)
        if finish_notice(0, flush_streams=True):
            raise OSError("validation output could not be flushed")
    except BaseException as error:
        exit_with_failure(PRE_READ_REFUSAL, lambda: f"REFUSE {error}\n", stderr_fd=stderr_fd)
    os._exit(0)


if __name__ == "__main__":
    main()
