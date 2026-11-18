"""Dispatch cadence manifest validation without editing the pinned v1 entry point."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

from . import qualification_manifest as schema_check

V1 = "joulewise.cadence_look_manifest.v1"
V2 = "joulewise.cadence_look_manifest.v2"
PRE_READ_REFUSAL = 2
REGISTRATION_PLACEHOLDER = b'"PENDING:CODE"'
V2_SCHEMA = schema_check.V2_SCHEMA
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
    pins = schema_check.check_variant(document, definitions, kind)
    if kind == "transfer":
        _validate_transfer(document)
    if kind == "description":
        _validate_description(document)
    return pins


def _transfer_final(registration, candidate, pins, definitions):
    if registration is None:
        raise ManifestError("transfer final validation requires the exact registered manifest bytes")
    registered = schema_check.decode_json(registration)
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
    document = schema_check.decode_json(payload)
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


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
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
        document = schema_check.decode_json(payload)
        schema = document.get("schema") if isinstance(document, dict) else None
        if schema == V1:
            if args.registration is not None:
                raise ManifestError("--registration applies to v2 manifests")
            if not args.v1_tool.is_file():
                raise ManifestError("pinned v1 entry point unavailable, supply --v1-tool")
            command = [sys.executable, "-B", str(args.v1_tool), "validate", str(args.manifest)]
            if args.final:
                command.append("--final")
            return subprocess.run(command, check=False).returncode
        if schema != V2:
            raise ManifestError("unknown cadence manifest schema ID")
        if args.registration is not None and not args.final:
            raise ManifestError("--registration requires --final")
        registration = args.registration.read_bytes() if args.registration else None
        doc = validate_v2(payload, final=args.final, registration=registration)
    except (ManifestError, OSError) as error:
        print(f"REFUSE {error}", file=sys.stderr)
        return PRE_READ_REFUSAL
    print(f"ok {doc['look_id']} ({doc['status']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
