"""Closed controls manifest and blind verification against a committed ledger."""

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import PurePosixPath
import re

from . import controls_analysis as analysis
from .controls_print import (
    KIT_ID, LOOK_ID, PILOT, REMAINDER, SCRIPT_STEPS, ControlsRefusal, LegBinding, LookIdentity, Refusal,
    _hex_pin, validate_roster,
)
from .qualification_manifest import _decode


SCHEMA_ID = "joulewise.cadence_look_manifest.controls.v1"
LOOK_DIR = "docs/process/cadence/looks/"
INSTRUMENT_ID = "lm-inst-01"
INSTRUMENT_SCHEMA_PATH = LOOK_DIR + "lm-inst-01.restricted.schema.json"
_INSTRUMENT_CHANNELS = ("gpu_rail", "rail_sum", "dc_in")
_INSTRUMENT_MEMBER = re.compile(r"(f2-(?:inst|stab)-[0-9]{2})/(L00[1-9]|L01[0-2])")
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


def _schema_path(value):
    if type(value) is not str or "\\" in value:
        return False
    path = PurePosixPath(value)
    return (not path.is_absolute() and path.as_posix() == value and path.suffix == ".json"
            and all(part not in ("..", "RESTRICTED") for part in path.parts))


def validate_manifest(raw):
    document = _decode(raw)
    identity_fields = {"schema", "status", "look_id", "look_kind", "kit_id", "pins"}
    instrument_fields = {"instrument_output_schema", "instrument_stage1"}
    if (type(document) is not dict
            or not identity_fields <= document.keys() <= identity_fields | instrument_fields
            or (document["schema"], document["status"], document["look_id"],
                document["look_kind"], document["kit_id"]) != (SCHEMA_ID, "final", LOOK_ID, "controls", KIT_ID)):
        raise ValueError("controls_manifest")
    schema = document.get("instrument_output_schema")
    if (type(schema) is not dict or schema.keys() != {"commit", "path", "sha256"}
            or not _schema_path(schema["path"])
            or not _hex_pin(schema["commit"], 40) or not _hex_pin(schema["sha256"], 64)):
        raise ControlsRefusal(Refusal.INSTRUMENT_SCHEMA_BINDING)
    stage1 = document.get("instrument_stage1")
    if (type(stage1) is not dict or stage1.keys() != {"ledger_commit", "stage1_sha256"}
            or not _hex_pin(stage1["ledger_commit"], 40) or not _hex_pin(stage1["stage1_sha256"], 64)):
        raise ControlsRefusal(Refusal.INSTRUMENT_STAGE1_BINDING)
    pins = document["pins"]
    if (type(pins) is not dict or pins.keys() != ROLES
            or not all(_hex_pin(value, 64) for value in pins.values())
            or pins["output_schema"] == pins["restricted_schema"]):
        raise ValueError("controls_pins")
    if pins["instrument_floor_schema"] != schema["sha256"]:
        raise ControlsRefusal(Refusal.INSTRUMENT_SCHEMA_BINDING)
    return document


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
    instrument_pool: analysis.HoldPool
    pins: dict
    stage1_entry: dict | None


@dataclass(frozen=True)
class Stage1Leg:
    binding: LegBinding
    kind: str
    admitted: bool
    g0_released: bool
    script_sha256: str | None
    episode_id: str | None
    episode_sha256: str | None


@dataclass(frozen=True)
class VerifiedStage1:
    public: dict
    legs: tuple[Stage1Leg, ...]


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
        if (type(row) is not dict
                or row.keys() != {"identity", "role", "reference", "script_sha", "kind", "admitted",
                                  "g0_released", "episode_id", "episode_sha256"}
                or type(row["identity"]) is not list or len(row["identity"]) != 6
                or type(row["kind"]) is not str or row["kind"] not in SCRIPT_STEPS
                or type(row["admitted"]) is not bool or type(row["g0_released"]) is not bool
                or (row["script_sha"] is not None and not _hex_pin(row["script_sha"], 64))
                or (row["episode_id"] is None) != (row["episode_sha256"] is None)
                or (row["episode_id"] is not None
                    and (type(row["episode_id"]) is not str or not row["episode_id"]
                         or not _hex_pin(row["episode_sha256"], 64)))
                or (row["admitted"] and not row["g0_released"])):
            raise ValueError("stage1_roster")
        legs.append(Stage1Leg(
            LegBinding(*row["identity"], row["role"], row["reference"]),
            row["kind"], row["admitted"], row["g0_released"], row["script_sha"],
            row["episode_id"], row["episode_sha256"],
        ))

    first = legs[0].binding
    if not _hex_pin(first.kit_sha256, 64) or not _hex_pin(first.runner_commit, 40):
        raise ValueError("stage1_roster")
    identity = LookIdentity(LOOK_ID, KIT_ID, first.kit_sha256, first.runner_commit)
    bindings = tuple((leg.binding.leg_id, leg.binding) for leg in legs)
    validate_roster(identity, bindings, dict(bindings))
    if sum(leg.admitted for leg in legs) != count:
        raise ValueError("stage1_roster")
    public = dict(look_id=LOOK_ID, manifest_sha256=freeze.manifest_sha256, commit=revision,
                  stage1_sha256=digest, n_legs=count)
    return VerifiedStage1(public, tuple(legs))


def _instrument_schema(snapshot, committed, pin):
    try:
        instrument = _decode(snapshot["instrument_manifest"])
        raw = committed[pin["commit"]][pin["path"]]
        if (type(raw) is not bytes or raw != snapshot["instrument_floor_schema"]
                or sha256(raw).hexdigest() != pin["sha256"]
                or (instrument["schema"], instrument["look_kind"], instrument["look_id"], instrument["status"])
                != ("joulewise.cadence_look_manifest.v2", "description", INSTRUMENT_ID, "committed")):
            raise ValueError("instrument registration")
        schema_pin = instrument["code_pins"]["restricted_schema"]
        if schema_pin != {"path": pin["path"], "sha256": pin["sha256"]}:
            raise ValueError("instrument schema pin")
        schema = _decode(raw)
        if schema.get("status", "committed") != "committed":
            raise ValueError("instrument schema status")
        definitions = schema["$defs"]
        reference = schema["properties"]["hold.json"]["$ref"]
        if not reference.startswith("#/$defs/"):
            raise ValueError("instrument hold schema reference")
        patterns = definitions[reference.removeprefix("#/$defs/")]["patternProperties"]
        branches, = (rule["oneOf"] for rule in patterns.values())
        channels, = (rule["properties"] for rule in branches if "properties" in rule)
        fields = {"kept", *(f"sd{width}_w" for width in analysis.FLOOR_WINDOWS)}
        if any(not fields <= channels[channel]["properties"].keys() for channel in _INSTRUMENT_CHANNELS):
            raise ValueError("instrument hold operands")
        # The draft's open string admits no unavailable reason in this print.
        reasons = definitions["undefined"]["properties"]["reason"].get("enum", [])
        if type(reasons) is not list:
            raise ValueError("instrument reason enum")
        vocab = analysis.HoldPool(reason_enum=reasons).reason_enum
        return instrument, channels, vocab
    except (AttributeError, KeyError, TypeError, ValueError) as error:
        raise ControlsRefusal(Refusal.INSTRUMENT_SCHEMA_BINDING) from error


def _instrument_members(committed, history, pin, instrument, manifest_digest):
    try:
        revision = pin["ledger_commit"]
        digest = pin["stage1_sha256"]
        row, = (entry for entry in history if entry.get("look_id") == INSTRUMENT_ID and entry.get("kind") == "stage1")
        if (row.get("status"), row.get("revision"), row.get("stage1_sha256"), row.get("manifest_sha256")) != (
                "committed", revision, digest, manifest_digest):
            raise ValueError("instrument stage1 ledger")
        raw = committed[revision]["instrument_stage1"]
        if type(raw) is not bytes or sha256(raw).hexdigest() != digest:
            raise ValueError("instrument stage1 pin")
        roster = _decode(raw)
        if roster["look_id"] != INSTRUMENT_ID or roster.get("status", "committed") != "committed":
            raise ValueError("instrument stage1 identity")
        kits = instrument["kits"]
        kit_pins = {kit["kit_id"]: kit["sha256"] for kit in kits}
        if len(kit_pins) != len(kits) or any(not _hex_pin(pin, 64) for pin in kit_pins.values()):
            raise ValueError("instrument kit pins")
        members = {}
        for key, position in roster["positions"].items():
            match = _INSTRUMENT_MEMBER.fullmatch(key)
            if match is None:
                raise ValueError("instrument stage1 member")
            kit, leg = match.groups()
            kit_hash = kit_pins[kit]
            if position["disposition"] == "qualified":
                members[key] = (kit, kit_hash, leg)
        count = roster["counts"]["n_legs"]
        if type(count) is not int or count != len(members):
            raise ValueError("instrument stage1 count")
        return members
    except (AttributeError, KeyError, TypeError, ValueError) as error:
        raise ControlsRefusal(Refusal.INSTRUMENT_STAGE1_BINDING) from error


def _hold_pool(raw, members, channels, reasons):
    try:
        hold = _decode(raw)
        if type(hold) is not dict or hold.keys() != members.keys():
            raise ValueError("instrument hold roster")
        rows = []
        for key, member in members.items():
            record = hold[key]
            if type(record) is not dict:
                raise ValueError("instrument hold member")
            if record.keys() - channels.keys():
                # The schema has a singleton unavailable member shape.
                if record.keys() != {"value", "reason"} or record["value"] is not None or record["reason"] not in reasons:
                    raise ValueError("instrument hold member")
                rows.extend(analysis.HoldWindow(member, channel, width, 0, None, record["reason"])
                            for channel in _INSTRUMENT_CHANNELS for width in analysis.FLOOR_WINDOWS)
                continue
            for channel in _INSTRUMENT_CHANNELS:
                leaf = record[channel]
                rule = channels[channel]
                if type(leaf) is not dict or not set(rule["required"]) <= leaf.keys() <= rule["properties"].keys():
                    raise ValueError("instrument hold channel")
                kept = leaf["kept"]
                if type(kept) is not list:
                    raise ValueError("instrument hold counts")
                for width, retained in zip(analysis.FLOOR_WINDOWS, kept, strict=True):
                    sd = leaf[f"sd{width}_w"]
                    reason = None
                    if type(sd) is dict:
                        if (not {"value", "reason"} <= sd.keys() <= {"value", "reason", "bound_s"}
                                or sd["value"] is not None or sd["reason"] not in reasons):
                            raise ValueError("instrument hold reason")
                        sd, reason = None, sd["reason"]
                    elif type(sd) not in (int, float):
                        raise ValueError("instrument hold SD")
                    rows.append(analysis.HoldWindow(member, channel, width, retained, sd, reason))
        return analysis.pool_hold_windows(rows, set(members.values()), reason_enum=reasons)
    except (AttributeError, KeyError, TypeError, ValueError, OverflowError) as error:
        raise ControlsRefusal(Refusal.INSTRUMENT_HOLD_BINDING) from error


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
        document = validate_manifest(manifest)
        pins = document["pins"]
        for role, pin in pins.items():
            artifact = snapshot.get(role)
            if type(artifact) is not bytes or sha256(artifact).hexdigest() != pin or artifact != working.get(role):
                if role in ("instrument_manifest", "instrument_floor_schema"):
                    raise ControlsRefusal(Refusal.INSTRUMENT_SCHEMA_BINDING)
                if role == "hold":
                    raise ControlsRefusal(Refusal.INSTRUMENT_HOLD_BINDING)
                raise ValueError("freeze_artifact")
    except (KeyError, TypeError) as error:
        raise ValueError("freeze_artifact") from error

    design = False
    prior_byte_pass = False
    eligible_receipt = False
    stage1_entry = None
    history = tuple(history)
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
    instrument, channels, reasons = _instrument_schema(snapshot, committed, document["instrument_output_schema"])
    members = _instrument_members(committed, history, document["instrument_stage1"], instrument,
                                  pins["instrument_manifest"])
    pool = _hold_pool(snapshot["hold"], members, channels, reasons)
    return VerifiedFreeze(current_revision, digest, pins["instrument_manifest"], snapshot["output_schema"],
                          snapshot["restricted_schema"], pool, pins, stage1_entry)
