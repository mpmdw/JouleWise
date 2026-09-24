"""Immutable, canonical registration for scored roster infrastructure."""

from __future__ import annotations

import copy
import hashlib
import json
import math


class RegistrationRefusal(ValueError):
    """A proposed registration is incomplete or contradicts the ruled contract."""


_FIELDS = frozenset({
    "schema", "mode", "registration_id", "plan_id", "sizing_receipt_sha256",
    "arm", "arm_to_family", "role_to_model_id", "levels", "merge_order",
    "min_correct", "alpha", "holm_m", "n_boot", "seed", "floor_j",
    "anchor_j", "cap_tokens", "cap_bound_fraction", "block_size",
    "n_per_level", "min_blocks_per_cell", "min_envelopes_per_cell",
    "envelope_s", "offset_s", "interior_s", "guard_s", "pitch_s",
    "s_per_token_upper", "prefill_s", "ceiling_s", "retry_stages",
    "max_drift_lever_slots", "delta_upper_j_per_block_slot", "budget_j",
    "declared_sensitivities", "scorer_id", "item_set_sha256",
})
_STAGES = ["initial", "whole_block", "single_problem", "single_retry", "ceiling_violation"]
_MERGE_ORDER = [[5, 4], [4, 3], [1, 2], [2, 3]]


def _fail(message):
    raise RegistrationRefusal(message)


def _mapping(value, name, keys):
    if type(value) is not dict or set(value) != set(keys):
        _fail(f"{name} must have exactly keys {sorted(keys, key=str)}")


def _text(value, name):
    if type(value) is not str or not value:
        _fail(f"{name} must be nonempty text")


def _integer(value, name, minimum):
    if type(value) is not int or value < minimum:
        _fail(f"{name} must be an integer >= {minimum}")


def _number(value, name, positive):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0 or (positive and value == 0):
        _fail(f"{name} must be finite and {'positive' if positive else 'nonnegative'}")


def _hash(value, name):
    _text(value, name)
    if len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        _fail(f"{name} must be lowercase sha256")


class Registration:
    """Frozen by construction; nested fields are returned as defensive copies."""

    __slots__ = ("_json", "_digest")

    def __init__(self):
        _fail("use Registration.from_mapping")

    def __setattr__(self, name, value):
        _fail("Registration is frozen")

    def __getattr__(self, name):
        if name in _FIELDS:
            return copy.deepcopy(json.loads(self._json)[name])
        raise AttributeError(name)

    @property
    def digest(self):
        return self._digest

    @property
    def family(self):
        data = json.loads(self._json)
        return data["arm_to_family"][data["arm"]]

    def to_mapping(self):
        return json.loads(self._json)

    @classmethod
    def from_mapping(cls, mapping):
        if type(mapping) is not dict:
            _fail("registration must be a mapping")
        if set(mapping) != _FIELDS:
            _fail(f"registration keys differ: missing={sorted(_FIELDS - set(mapping), key=str)}, unknown={sorted(set(mapping) - _FIELDS, key=str)}")
        try:
            data = copy.deepcopy(mapping)
            raw = json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False)
        except (TypeError, ValueError, OverflowError) as exc:
            raise RegistrationRefusal("registration is not canonical JSON") from exc
        for name in ("schema", "registration_id", "plan_id", "arm", "scorer_id"):
            _text(data[name], name)
        if data["schema"] != "joulewise.scored_registration.v1":
            _fail("unsupported registration schema")
        _hash(data["item_set_sha256"], "item_set_sha256")
        if data["mode"] not in ("pilot", "registered") or type(data["mode"]) is not str:
            _fail("mode must be pilot or registered")
        if data["sizing_receipt_sha256"] is None:
            if data["mode"] == "registered":
                _fail("registered mode requires sizing receipt")
        else:
            _hash(data["sizing_receipt_sha256"], "sizing_receipt_sha256")
        if data["levels"] != [1, 2, 3, 4, 5] or any(type(v) is not int for v in data["levels"]):
            _fail("levels differ from ruled levels")
        if data["merge_order"] != _MERGE_ORDER or any(type(v) is not int for pair in data["merge_order"] for v in pair):
            _fail("merge_order differs from ruled order")
        if type(data["min_correct"]) is not int or data["min_correct"] != 3:
            _fail("min_correct must be 3")
        if type(data["holm_m"]) is not int or data["holm_m"] != 5:
            _fail("holm_m must be 5")
        if data["retry_stages"] != _STAGES or type(data["retry_stages"]) is not list:
            _fail("retry stage vocabulary differs")
        for name in ("n_boot", "seed", "n_per_level", "min_blocks_per_cell", "min_envelopes_per_cell"):
            _integer(data[name], name, 0 if name == "seed" else 1)
        for name in ("alpha", "floor_j", "anchor_j", "cap_bound_fraction", "envelope_s", "offset_s", "interior_s", "guard_s", "pitch_s"):
            _number(data[name], name, name in ("alpha", "envelope_s", "interior_s", "pitch_s"))
        if data["alpha"] > 1 or data["cap_bound_fraction"] != .2:
            _fail("alpha or cap fraction exceeds one")
        if data["offset_s"] + data["interior_s"] > data["envelope_s"]:
            _fail("interior extends beyond envelope")
        capacity = data["interior_s"] - data["guard_s"]
        if data["pitch_s"] < data["envelope_s"]:
            _fail("invalid capture capacity or pitch")
        families = data["arm_to_family"]
        if type(families) is not dict or data["arm"] not in families or not families:
            _fail("arm_to_family must contain the selected arm")
        for arm, family in families.items():
            _text(arm, "arm key")
            _text(family, "family")
        roles = data["role_to_model_id"]
        _mapping(roles, "role_to_model_id", ("8B", "1.7B"))
        for model in roles.values():
            _text(model, "model id")
        if len(set(roles.values())) != 2:
            _fail("model IDs must differ")
        arms = set(families)
        for name in ("cap_tokens", "block_size"):
            _mapping(data[name], name, arms)
            for value in data[name].values():
                _integer(value, name, 1)
        for name in ("s_per_token_upper", "prefill_s", "ceiling_s"):
            _mapping(data[name], name, roles.values())
            for model, per_arm in data[name].items():
                _mapping(per_arm, f"{name}[{model}]", arms)
                for value in per_arm.values():
                    _number(value, name, name != "prefill_s")
        for model in roles.values():
            for arm in arms:
                derived = data["cap_tokens"][arm] * data["s_per_token_upper"][model][arm] + data["prefill_s"][model][arm]
                if derived > data["ceiling_s"][model][arm] or data["ceiling_s"][model][arm] > capacity:
                    _fail(f"physical ceiling incoherent for {model}, {arm}")
        for name in ("max_drift_lever_slots", "delta_upper_j_per_block_slot", "budget_j"):
            value = data[name]
            if value is None:
                if data["mode"] == "registered":
                    _fail(f"registered mode requires {name}")
            else:
                _number(value, name, name == "delta_upper_j_per_block_slot")
        if all(data[name] is not None for name in
                ("max_drift_lever_slots", "delta_upper_j_per_block_slot", "budget_j")):
            blocks_per_cell = math.ceil(data["n_per_level"] / data["block_size"][data["arm"]])
            derived_gap = data["budget_j"] / (data["delta_upper_j_per_block_slot"] * blocks_per_cell)
            if not math.isclose(data["max_drift_lever_slots"], derived_gap, rel_tol=1e-12, abs_tol=1e-12):
                _fail("drift lever differs from registered budget formula")
        if type(data["declared_sensitivities"]) is not list or not data["declared_sensitivities"]:
            _fail("declared_sensitivities must be a nonempty list")
        for value in data["declared_sensitivities"]:
            _text(value, "declared sensitivity")
        obj = object.__new__(cls)
        object.__setattr__(obj, "_json", raw)
        object.__setattr__(obj, "_digest", hashlib.sha256(raw.encode()).hexdigest())
        return obj
