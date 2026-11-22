"""Closed controls manifest and blind verification against a committed ledger."""

from dataclasses import dataclass
from hashlib import sha256
import json

from .controls_print import (
    KIT_ID, LOOK_ID, PILOT, REMAINDER, LegBinding, LookIdentity, _hex_pin, validate_roster,
)
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
    pins: dict
    stage1_entry: dict | None


@dataclass(frozen=True)
class VerifiedStage1:
    public: dict
    legs: tuple[tuple[LegBinding, str | None], ...]


def verify_stage1(freeze, committed, candidate):
    """Bind the blind roster and public fields to the authorized ledger entry."""
    entry = freeze.stage1_entry
    if entry is None:
        raise ValueError("stage1_commitment")
    revision = entry.get("revision")
    count = entry.get("n_legs")
    digest = entry.get("stage1_sha256")
    ids = PILOT + REMAINDER
    if (entry.get("manifest_sha256") != freeze.manifest_sha256 or not _hex_pin(revision, 40)
            or not _hex_pin(digest, 64) or type(count) is not int or not 0 <= count <= len(ids)):
        raise ValueError("stage1_commitment")
    raw = committed.get(revision, {}).get("stage1")
    if type(raw) is not bytes or type(candidate) is not bytes or raw != candidate or sha256(raw).hexdigest() != digest:
        raise ValueError("stage1_commitment")

    roster = _decode(raw)
    if (type(roster) is not dict or roster.keys() != {"n_legs", "legs"}
            or type(roster["n_legs"]) is not int or roster["n_legs"] != count
            or type(roster["legs"]) is not dict or roster["legs"].keys() != set(ids)):
        raise ValueError("stage1_roster")

    legs = []
    for leg_id in ids:
        row = roster["legs"][leg_id]
        if (type(row) is not dict or row.keys() != {"identity", "role", "reference", "script_sha"}
                or type(row["identity"]) is not list or len(row["identity"]) != 6
                or (row["script_sha"] is not None and not _hex_pin(row["script_sha"], 64))):
            raise ValueError("stage1_roster")
        legs.append((LegBinding(*row["identity"], row["role"], row["reference"]), row["script_sha"]))

    first = legs[0][0]
    if not _hex_pin(first.kit_sha256, 64) or not _hex_pin(first.runner_commit, 40):
        raise ValueError("stage1_roster")
    identity = LookIdentity(LOOK_ID, KIT_ID, first.kit_sha256, first.runner_commit)
    bindings = tuple((binding.leg_id, binding) for binding, _ in legs)
    validate_roster(identity, bindings, dict(bindings))
    public = dict(look_id=LOOK_ID, manifest_sha256=freeze.manifest_sha256, commit=revision,
                  stage1_sha256=digest, n_legs=count)
    return VerifiedStage1(public, tuple(legs))


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
    stage1_entry = None
    for row in history:
        if type(row) is not dict:
            raise ValueError("freeze_ledger")
        if row.get("kind") == "ctl01_withheld":
            raise ValueError("ctl01_withheld")
        if row.get("kind") in ("first_ctl_read", "reserved") and row.get("look_id", LOOK_ID) == LOOK_ID:
            # The caller is trying to reserve again, or its receipt is too late.
            raise ValueError("freeze_read_order")
        if row.get("look_id") != LOOK_ID:
            continue
        kind = row.get("kind")
        if stage1_entry is not None and kind in ("design_pass", "byte_pass", "receipt"):
            raise ValueError("stage1_order")
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
        elif kind == "stage1":
            if not eligible_receipt or stage1_entry is not None:
                raise ValueError("stage1_order")
            stage1_entry = dict(row)
    if not eligible_receipt:
        raise ValueError("freeze_receipt")
    return VerifiedFreeze(current_revision, digest, pins["instrument_manifest"], snapshot["output_schema"],
                          snapshot["restricted_schema"], reasons, pins, stage1_entry)
