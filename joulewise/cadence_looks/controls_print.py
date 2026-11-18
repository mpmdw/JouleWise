"""In-memory checks for the lm-ctl-01 print seam.

The caller supplies authenticated projections. This module has no reader,
registration, or execution entry point. Output encoders cover the synthetic
projection; the final print inventory is subject to the manifest cold pass.
"""

from dataclasses import dataclass
from enum import Enum, auto
from hashlib import sha256
import json
import re


PILOT = ("L001", "L002", "L003")
REMAINDER = tuple(f"L{i:03}" for i in range(4, 13))
LOOK_ID = "lm-ctl-01"
KIT_ID = "cl-ctl-01"
MASTER_SEED = 2026111601
CHANNELS = ("gpu_rail", "cpu_rail", "rail_sum", "dc_in")
CPU_DOSES = (10, 30, 90)
PAIR_LABEL = "equal counts, same prompt and seed, different context depth"


class Refusal(Enum):
    IDENTITY = auto()
    LAYOUT = auto()
    PILOT_HAND_READ = auto()
    SPLIT_HAND_READ = auto()
    PRE_READ_FREEZE = auto()
    BINDING = auto()
    ROSTER = auto()
    REFERENCE = auto()
    SCRIPT_DIGEST = auto()
    SCRIPT_KIND = auto()
    PHYSICAL_ORDER = auto()
    ENVELOPE = auto()
    PAIR_COUNT = auto()
    PAIR_IDENTITY = auto()
    CONTEXT = auto()
    SCRIPT_DELIVERY = auto()
    PRIVATE_DISCLOSURE = auto()
    QUALIFIER = auto()
    PUBLIC_DISCLOSURE = auto()


class ControlsRefusal(ValueError):
    """An in-memory validation refusal with a fixed reason."""

    def __init__(self, reason: Refusal):
        self.reason = reason
        super().__init__(reason.name)


@dataclass(frozen=True)
class LookIdentity:
    look_id: str
    kit_id: str
    kit_sha256: str
    runner_commit: str


@dataclass(frozen=True)
class InstrumentLeaf:
    look_id: str
    manifest_sha256: str
    kit_id: str
    leg_id: str
    channel: str
    window_s: int
    print_id: str


@dataclass(frozen=True)
class BlindPlan:
    identity: LookIdentity
    master_seed: int
    spans: tuple[tuple[str, ...], ...]
    pilot_pass_order: int
    remainder_start_order: int
    split_hand_pass: bool
    freeze_order: int
    reservation_order: int
    instrument: InstrumentLeaf
    manifest_sha256: str
    code_sha256: str
    schema_sha256: str


@dataclass(frozen=True)
class LegBinding:
    kit_id: str
    kit_sha256: str
    runner_commit: str
    span: int
    leg_id: str
    attempt: int
    role: str
    reference_sha256: str

    @property
    def member(self):
        return (self.kit_id, self.kit_sha256, self.runner_commit, self.span, self.leg_id)


@dataclass(frozen=True)
class Delivery:
    visible_tokens: tuple[int, ...]
    hidden_tokens: int
    cpu_s: int
    gap_s: int
    recovery_s: float


@dataclass(frozen=True)
class Episode:
    kind: str
    steps: tuple[str, ...]
    delivery: Delivery
    start_contexts: tuple[int, ...]
    seed: int
    prompt_sha256: str


def _hex_pin(value, width):
    return (type(value) is str and re.fullmatch(rf"[0-9a-f]{{{width}}}", value)
            is not None and value != "0" * width)


def _ordered(before, after):
    return type(before) is int and type(after) is int and 0 < before < after


def validate_plan(plan: BlindPlan, registered: BlindPlan):
    """Check a blind projection against independent registration evidence."""
    identity = plan.identity
    if (identity != registered.identity or identity.look_id != LOOK_ID
            or identity.kit_id != KIT_ID or not _hex_pin(identity.kit_sha256, 64)
            or not _hex_pin(identity.runner_commit, 40)):
        raise ControlsRefusal(Refusal.IDENTITY)
    if (type(plan.master_seed) is not int or plan.master_seed != MASTER_SEED
            or plan.spans != (PILOT, REMAINDER)):
        raise ControlsRefusal(Refusal.LAYOUT)
    if not _ordered(plan.pilot_pass_order, plan.remainder_start_order):
        raise ControlsRefusal(Refusal.PILOT_HAND_READ)
    if plan.split_hand_pass is not True:
        raise ControlsRefusal(Refusal.SPLIT_HAND_READ)
    if not _ordered(plan.freeze_order, plan.reservation_order):
        raise ControlsRefusal(Refusal.PRE_READ_FREEZE)
    leaf = plan.instrument
    if (plan != registered or leaf.look_id != "lm-inst-01"
            or leaf.channel not in ("gpu_rail", "rail_sum", "dc_in")
            or type(leaf.window_s) is not int or leaf.window_s not in (10, 40, 128)
            or not all(_hex_pin(pin, 64) for pin in (
                leaf.manifest_sha256, plan.manifest_sha256, plan.code_sha256, plan.schema_sha256
            ))):
        raise ControlsRefusal(Refusal.BINDING)


def validate_roster(identity: LookIdentity, rows, registered):
    """Join the ordered leg bindings and verify the two capture groups."""
    expected_ids = PILOT + REMAINDER
    if tuple(leg_id for leg_id, _ in rows) != expected_ids or registered.keys() != set(expected_ids):
        raise ControlsRefusal(Refusal.ROSTER)
    legs = dict(rows)
    for span, ids in enumerate((PILOT, REMAINDER), start=1):
        capture = legs[ids[0]]
        for leg_id in ids:
            leg = legs[leg_id]
            anchor = registered[leg_id]
            member = (identity.kit_id, identity.kit_sha256, identity.runner_commit, span, leg_id)
            if (leg.member != member or leg.member != anchor.member or type(leg.span) is not int
                    or type(leg.attempt) is not int or leg.attempt < 1 or leg.attempt != anchor.attempt):
                raise ControlsRefusal(Refusal.IDENTITY)
            role = "capture" if leg_id == ids[0] else "consume"
            if ((leg.role, leg.reference_sha256) != (anchor.role, anchor.reference_sha256)
                    or leg.role != role or leg.reference_sha256 != capture.reference_sha256
                    or not _hex_pin(leg.reference_sha256, 64)):
                raise ControlsRefusal(Refusal.REFERENCE)


def validate_script_pin(payload: bytes, committed_sha256: str):
    """Authenticate exact work-record bytes against the projected terminal pin."""
    if sha256(payload).hexdigest() != committed_sha256:
        raise ControlsRefusal(Refusal.SCRIPT_DIGEST)


# Interior step names match the published script-work record. The first and
# last boundaries come from the operational and sampling evidence.
SCRIPT_STEPS = {
    "extra-turn": ("turn", "turn"),
    "hidden": ("hidden", "turn"),
    "cpu": ("turn", "cpu", "turn"),
    "split": ("turn", "gap", "turn", "gap", "turn"),
    "plain": ("turn",),
}


def validate_episode(episode: Episode, *, kind: str, envelopes):
    """Require sampled recovery and reconcile the one visible-only envelope."""
    if kind not in SCRIPT_STEPS or episode.kind != kind:
        raise ControlsRefusal(Refusal.SCRIPT_KIND)
    steps = SCRIPT_STEPS[kind]
    if episode.steps != ("G0", *steps, "recovery", "sampling_stop"):
        raise ControlsRefusal(Refusal.PHYSICAL_ORDER)

    visible = episode.delivery.visible_tokens
    contexts = episode.start_contexts
    if (len(contexts) != steps.count("turn") + steps.count("hidden")
            or any(type(count) is not int or count < 1 for count in contexts)
            or (kind == "split" and len(set(contexts)) != 1)):
        raise ControlsRefusal(Refusal.CONTEXT)
    if len(visible) != steps.count("turn") or any(type(n) is not int or n < 0 for n in visible):
        raise ControlsRefusal(Refusal.ENVELOPE)
    projected = {"prompt": sum(contexts[steps.count("hidden"):]), "decoded": sum(visible)}
    if (len(envelopes) != 1 or type(envelopes[0]) is not dict
            or any(type(value) is not int for value in envelopes[0].values())
            or envelopes[0] != projected):
        raise ControlsRefusal(Refusal.ENVELOPE)


def compare_pair(split: Episode, plain: Episode):
    """Validate delivered-count parity and return the two peak context counts."""
    if sum(split.delivery.visible_tokens) != sum(plain.delivery.visible_tokens):
        raise ControlsRefusal(Refusal.PAIR_COUNT)
    if (split.seed, split.prompt_sha256) != (plain.seed, plain.prompt_sha256):
        raise ControlsRefusal(Refusal.PAIR_IDENTITY)
    if split.start_contexts != plain.start_contexts * 3:
        raise ControlsRefusal(Refusal.CONTEXT)
    peaks = tuple(max(context + count for context, count in zip(
        episode.start_contexts, episode.delivery.visible_tokens, strict=True
    )) for episode in (split, plain))
    if peaks[0] >= peaks[1]:
        raise ControlsRefusal(Refusal.CONTEXT)
    return peaks


def validate_complete_delivery(delivered: Delivery, prescribed: Delivery):
    """A complete delivery must match its prescription."""
    if delivered != prescribed:
        raise ControlsRefusal(Refusal.SCRIPT_DELIVERY)


def _json_bytes(record):
    return json.dumps(record, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def encode_public_projection(record, blind_fields):
    """Encode the proposed public projection using only committed blind fields."""
    if (blind_fields.keys() != {"look_id", "manifest_sha256", "commit", "stage1_sha256", "n_legs"}
            or blind_fields["look_id"] != LOOK_ID or not _hex_pin(blind_fields["commit"], 40)
            or not _hex_pin(blind_fields["manifest_sha256"], 64)
            or not _hex_pin(blind_fields["stage1_sha256"], 64)
            or type(blind_fields["n_legs"]) is not int or blind_fields["n_legs"] < 0
            or type(record) is not dict or record.keys() != blind_fields.keys()
            or any(type(value) is not type(blind_fields[field]) or value != blind_fields[field]
                   for field, value in record.items())):
        raise ControlsRefusal(Refusal.PUBLIC_DISCLOSURE)
    return _json_bytes(blind_fields)


def _integer_table(table, keys, n_legs):
    return (type(table) is dict and table.keys() == set(keys)
            and all(type(column) is list and len(column) == n_legs
                    and all(type(value) is int for value in column) for column in table.values()))


def encode_alignment_projection(record, *, qualifier_ran: bool):
    """Check and encode the synthetic alignment print over tabulated integer inputs."""
    if (type(record) is not dict or record.keys() != {
        "pair_label", "qualifier", "phases", "totals", "cpu_other_by_seconds"
    } or record["pair_label"] != PAIR_LABEL):
        raise ControlsRefusal(Refusal.PRIVATE_DISCLOSURE)
    n_legs = len(PILOT) + len(REMAINDER)
    phases, totals = record["phases"], record["totals"]
    if not (_integer_table(phases, CHANNELS, n_legs) and _integer_table(totals, CHANNELS, n_legs)):
        raise ControlsRefusal(Refusal.PRIVATE_DISCLOSURE)
    cpu = record["cpu_other_by_seconds"]
    if (type(cpu) is not dict or cpu.keys() != set(CPU_DOSES)
            or any(type(key) is not int or type(value) is not int for key, value in cpu.items())):
        raise ControlsRefusal(Refusal.PRIVATE_DISCLOSURE)

    if qualifier_ran:
        checks = (100 * abs(phase - whole) <= whole for channel in CHANNELS
                  for phase, whole in zip(phases[channel], totals[channel], strict=True))
        word = "yes" if all(checks) and cpu[10] < cpu[30] < cpu[90] else "no"
    else:
        word = "not_run"
    if record["qualifier"] != word:
        raise ControlsRefusal(Refusal.QUALIFIER)
    return _json_bytes(record)
