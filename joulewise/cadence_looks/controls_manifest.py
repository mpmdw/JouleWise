"""Closed controls manifest and blind verification against a committed ledger."""

from dataclasses import dataclass
from hashlib import sha256
import json

from .controls_print import LOOK_ID, KIT_ID, _hex_pin
from .qualification_manifest import _decode


SCHEMA_ID = "joulewise.cadence_look_manifest.controls.v1"
LOOK_DIR = "docs/process/cadence/looks/"
CODE_PATHS = {
    "print_code": "joulewise/cadence_looks/controls_release.py",
    "print_code/analysis": "joulewise/cadence_looks/controls_analysis.py",
    "print_code/projection": "joulewise/cadence_looks/controls_print.py",
    "print_code/manifest": "joulewise/cadence_looks/controls_manifest.py",
    "print_code/manifest_json": "joulewise/cadence_looks/qualification_manifest.py",
    "print_code/phase": "joulewise/align/apple/rl176_phases.py",
    "print_code/attribution": "joulewise/align/attribution.py",
    "print_code/records": "joulewise/align/records.py",
    "print_code/windows": "joulewise/align/power/windows.py",
    "print_code/powermetrics_adapter": "joulewise/adapters/powermetrics.py",
    "print_code/trace_point": "joulewise/bundle_read.py",
    "print_code/integrator": "joulewise/reduce.py",
    "print_code/branch_release": "joulewise/cadence_looks/transfer_release.py",
    "print_code/dispatch": "joulewise/cadence_looks/manifest_dispatch.py",
    "output_schema": LOOK_DIR + "lm-ctl-01.output.schema.json",
    "restricted_schema": LOOK_DIR + "lm-ctl-01.restricted.schema.json",
    "controls_route": LOOK_DIR + "look_manifest.controls.v1.schema.json",
}
ROLES = frozenset(CODE_PATHS) | {"instrument_manifest", "instrument_floor_schema", "hold", "edges"}
WITHHELD = ("no_dc_in_floor", "no_prefill_size", "dose_under_floor_at_k2")
ISSUED_SETTINGS = {"hidden_tokens": (128, 256, 512), "recovery_s": 600, "gap_s": 60, "prefill_tokens": 2000}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def validate_manifest(raw):
    document = _decode(raw)
    if (type(document) is not dict
            or document.keys() != {"schema", "status", "look_id", "look_kind", "kit_id", "pins"}
            or (document["schema"], document["status"], document["look_id"],
                document["look_kind"], document["kit_id"]) != (SCHEMA_ID, "final", LOOK_ID, "controls", KIT_ID)):
        raise ValueError("controls_manifest")
    pins = document["pins"]
    if (type(pins) is not dict or pins.keys() != ROLES
            or not all(_hex_pin(value, 64) for value in pins.values())
            or pins["output_schema"] == pins["restricted_schema"]):
        raise ValueError("controls_pins")
    return pins


def append_withheld(row, append):
    """Record exactly one closed withheld reason without a value payload."""
    if (type(row) is not dict or row.keys() != {"kind", "reason"} or row["kind"] != "ctl01_withheld"
            or type(row["reason"]) is not str or row["reason"] not in WITHHELD):
        raise ValueError("ctl01_withheld")
    append(dict(row))


def select_reservation(*, observations, append):
    """Record a withheld look or return eligibility to continue the blind checks."""
    from .controls_analysis import withheld_reason

    reason = withheld_reason(observations["gpu_token_floors"], observations["dc_token_floors"],
                             observations["qualified_prefills"])
    if reason is None:
        return True
    append_withheld({"kind": "ctl01_withheld", "reason": reason}, append)
    return False


@dataclass(frozen=True)
class VerifiedFreeze:
    revision: str
    manifest_sha256: str
    instrument_manifest_sha256: str
    output_schema: bytes
    restricted_schema: bytes
    instrument_reasons: frozenset[str]
    history: tuple


def _instrument_reasons(snapshot, pins):
    instrument = _decode(snapshot["instrument_manifest"])
    schema = _decode(snapshot["instrument_floor_schema"])
    try:
        schema_pin = instrument["code_pins"]["restricted_schema"]
        reasons = schema["$defs"]["undefined"]["properties"]["reason"]["enum"]
    except (KeyError, TypeError) as error:
        raise ValueError("instrument_reason_enum") from error
    if ((instrument.get("schema"), instrument.get("look_kind"), instrument.get("look_id"),
         instrument.get("status")) != ("joulewise.cadence_look_manifest.v2", "description", "lm-inst-01", "committed")
            or schema_pin != {"path": LOOK_DIR + "lm-inst-01.restricted.schema.json",
                              "sha256": pins["instrument_floor_schema"]}
            or type(reasons) is not list or not reasons
            or any(type(reason) is not str or not reason or reason == "missing_floor" for reason in reasons)):
        raise ValueError("instrument_reason_enum")
    return frozenset(reasons)


def verify_freeze(*, current_revision, committed, working, history):
    """Join exact artifact bytes to a prior design pass, byte pass and receipt.

    committed is a read-only revision-to-blob projection from the bound commit
    store. history is the verified ancestry of that ledger. No sibling or
    working ledger data can be used as a witness.
    """
    if not _hex_pin(current_revision, 40):
        raise ValueError("freeze_revision")
    try:
        snapshot = committed[current_revision]
        manifest = snapshot["manifest"]
        if type(manifest) is not bytes or manifest != working["manifest"]:
            raise ValueError("freeze_manifest")
        digest = sha256(manifest).hexdigest()
        pins = validate_manifest(manifest)
        for role, pin in pins.items():
            artifact = snapshot[role]
            if type(artifact) is not bytes or sha256(artifact).hexdigest() != pin or artifact != working[role]:
                raise ValueError("freeze_artifact")
        reasons = _instrument_reasons(snapshot, pins)
    except (KeyError, TypeError) as error:
        raise ValueError("freeze_artifact") from error

    design = False
    prior_byte_pass = False
    eligible_receipt = False
    prefix = []
    for row in history:
        if type(row) is not dict:
            raise ValueError("freeze_ledger")
        if row.get("kind") == "ctl01_withheld":
            raise ValueError("ctl01_withheld")
        if row.get("kind") in ("first_ctl_read", "reserved") and row.get("look_id", LOOK_ID) == LOOK_ID:
            # The caller is trying to reserve again, or its receipt is too late.
            raise ValueError("freeze_read_order")
        prefix.append(dict(row))
        if row.get("look_id") != LOOK_ID:
            continue
        kind = row.get("kind")
        if kind == "design_pass":
            design = True
            prior_byte_pass = eligible_receipt = False
        elif kind == "byte_pass":
            prior_byte_pass = (design and row.get("manifest_sha256") == digest
                               and row.get("hand_vectors_passed") is True)
            eligible_receipt = False
        elif kind == "receipt":
            eligible_receipt = (prior_byte_pass and row.get("manifest_sha256") == digest
                                and row.get("revision") == current_revision)
    if not eligible_receipt:
        raise ValueError("freeze_receipt")
    return VerifiedFreeze(current_revision, digest, pins["instrument_manifest"], snapshot["output_schema"],
                          snapshot["restricted_schema"], reasons, tuple(prefix))


def read_frozen(*, current_revision, committed, working, history, first_read):
    verify_freeze(current_revision=current_revision, committed=committed, working=working, history=history)
    return first_read()
