"""Dispatch cadence manifest validation without editing the pinned v1 entry point."""

from __future__ import annotations

import argparse
from contextlib import suppress
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory

from . import qualification_manifest as schema_check

V1 = "joulewise.cadence_look_manifest.v1"
V2 = "joulewise.cadence_look_manifest.v2"
PRE_READ_REFUSAL = 2
REGISTRATION_PLACEHOLDER = b'"PENDING:CODE"'
FINAL_PLACEHOLDER = re.compile(r"PENDING:CODE|OPEN-[0-9]+")
V2_SCHEMA = schema_check._SCHEMA
V1_TOOL = V2_SCHEMA.parents[4] / "scripts/cadence_look_manifest.py"
KIT_COMMITMENTS = V2_SCHEMA.with_name("look-kit-commitments.v2.json")
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


def _discard_output(fd):
    with suppress(OSError):
        sink = os.open(os.devnull, os.O_WRONLY)
        if sink != fd:
            try:
                os.dup2(sink, fd)
            finally:
                os.close(sink)


def finish_notice(status, *, stdout=None, stderr=None, stderr_fd=None, flush_streams=False):
    """Deliver CLI output without letting stream failures replace the selected status."""
    failed = False
    if stderr_fd is not None:
        try:
            with os.fdopen(stderr_fd, "w", encoding="ascii", closefd=False) as stream:
                stream.write(stderr)
                stream.flush()
        except (OSError, ValueError):
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
        except (OSError, ValueError):
            failed = True

    if failed:
        # BrokenPipeError is an OSError. Replace the endpoints so a later
        # Python shutdown flush cannot turn the chosen exit into status 120.
        _discard_output(2)
        if stdout is not None or flush_streams:
            _discard_output(1)
        return status or PRE_READ_REFUSAL
    return status


class _NoticeArgumentParser(argparse.ArgumentParser):
    def _print_message(self, message, file=None):
        if message:
            if file is sys.stdout:
                status = finish_notice(0, stdout=message)
            else:
                status = finish_notice(0, stderr=message)
            if status:
                raise SystemExit(status)


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


def _validate_shape(document, definitions, commitments):
    kind = document.get("look_kind")
    if kind not in ("qualification", "description", "transfer"):
        raise ManifestError("expected v2 look_kind qualification, description or transfer")
    pins = {}
    schema_check._check(document, definitions[kind], definitions, pins)
    if kind == "transfer":
        _validate_transfer(document, commitments)
    elif kind == "description":
        _validate_description(document, commitments)
    return pins


def _transfer_final(registration, candidate, pins, definitions, commitments):
    registered = schema_check._decode(registration)
    if not isinstance(registered, dict) or (
        registered.get("schema"), registered.get("look_kind"), registered.get("status")
    ) != (V2, "transfer", "registered"):
        raise ManifestError("expected a registered transfer manifest")
    pending = _validate_shape(registered, definitions, commitments)
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


def _reject_reserved_v1_look(document):
    schema = json.loads(V2_SCHEMA.read_bytes())
    definitions = schema["$defs"]
    for variant in schema["oneOf"]:
        name = variant["$ref"].removeprefix("#/$defs/")
        rule = definitions[name]["properties"]["look_id"]
        try:
            schema_check._check(document.get("look_id"), rule, definitions, {})
        except ManifestError:
            continue
        raise ManifestError("look_id is reserved for v2 cadence validation")


def _validate_legacy(tool, payload, final):
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
        return finish_notice(status, stdout=result.stdout or None, stderr=result.stderr or None)


def _check_registration_use(document, final):
    if not final:
        raise ManifestError("--registration requires --final")
    if document.get("look_kind") not in ("qualification", "transfer") or document.get("status") != "registered":
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


def _validate_v2_document(payload, document, final, read_registration):
    if not isinstance(document, dict) or document.get("schema") != V2:
        raise ManifestError("expected the v2 cadence manifest schema ID")
    kind = document.get("look_kind")
    if read_registration is not None:
        _check_registration_use(document, final)
    if final and document.get("status") != "draft":
        _reject_final_placeholders(document)
    commitments = schema_check._decode(KIT_COMMITMENTS.read_bytes())
    if kind == "qualification":
        return _validate_qualification(payload, final, read_registration, commitments)

    definitions = json.loads(V2_SCHEMA.read_bytes())["$defs"]
    pins = _validate_shape(document, definitions, commitments)
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
    read_registration = None if registration is None else lambda: registration
    return _validate_v2_document(payload, document, final, read_registration)


def main(argv=None):
    parser = _NoticeArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate")
    validate.add_argument("manifest", type=Path)
    validate.add_argument("--final", action="store_true")
    validate.add_argument("--registration", type=Path, help="exact trusted v2 scientific registration bytes")
    validate.add_argument("--v1-tool", type=Path, default=V1_TOOL,
                          help="pinned v1 cadence_look_manifest.py when it lives on a separate checkout")
    args = parser.parse_args(argv)
    try:
        payload = args.manifest.read_bytes()
        document = schema_check._decode(payload)
        schema = document.get("schema") if isinstance(document, dict) else None
        if schema == V1:
            if args.registration is not None:
                raise ManifestError("--registration applies to v2 manifests")
            _reject_reserved_v1_look(document)
            if args.final:
                _reject_final_placeholders(document)
            return _validate_legacy(args.v1_tool, payload, args.final)
        if schema != V2:
            raise ManifestError("unknown cadence manifest schema ID")
        read_registration = args.registration.read_bytes if args.registration is not None else None
        doc = _validate_v2_document(payload, document, args.final, read_registration)
    except (ManifestError, OSError) as error:
        return finish_notice(PRE_READ_REFUSAL, stderr=f"REFUSE {error}\n")
    return finish_notice(0, stdout=f"ok {doc['look_id']} ({doc['status']})\n")


if __name__ == "__main__":
    raise SystemExit(main())
