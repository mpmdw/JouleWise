"""Frozen canonical registration for scored roster planning."""
from __future__ import annotations

import copy
import hashlib
import json
import math
import re

LEVELS = [1, 2, 3, 4, 5]
RETRY_STAGES = ["initial", "whole_block", "single_problem", "single_retry", "ceiling_violation"]
EDGES = [
    ("initial", "whole_block"), ("initial", "reschedule"),
    ("initial", "unattributed_overrun"), ("whole_block", "single_problem"),
    ("whole_block", "unattributed_overrun"), ("single_problem", "single_retry"),
    ("single_problem", "reschedule"), ("single_retry", "ceiling_violation"),
    ("single_retry", "reschedule"), ("single_problem", "unattributed_overrun"),
    ("single_retry", "unattributed_overrun"),
]
MIN_PARENT_BLOCKS = 5
MIN_ENVELOPES = 5
MERGE_ORDER = [[5, 4], [4, 3], [1, 2], [2, 3]]
MIN_CORRECT = 3
HOLM_M = 5
CAP_BOUND_FRACTION = 0.20
REGISTRATION_SCHEMA = "joulewise.scored_registration.v2"
ROSTER_SCHEMA = "joulewise.scored_roster.v3"
REGISTRATION_KEYS = frozenset("schema mode registration_id plan_id scorer_id arm arm_to_family role_to_model_id sizing_receipt_sha256 predictions_sha256 alpha n_boot seed floor_j anchor_j cap_tokens block_size item_ids_by_level envelope_s interior_s pitch_s offset_s guard_s s_per_token_upper prefill_s ceiling_s delta_upper_j_per_block_slot budget_j declared_sensitivities".split())
_HEX = re.compile(r"[0-9a-f]{64}\Z")


class RegistrationRefusal(ValueError):
    def __init__(self, code, detail=""):
        self.code = code
        super().__init__(f"{code}: {detail}")


def _need(ok, code, detail):
    if not ok:
        raise RegistrationRefusal(code, detail)


def _num(value):
    return type(value) in (int, float) and math.isfinite(value)


def _integer(value, minimum):
    return type(value) is int and value >= minimum


def _text(value):
    return type(value) is str and bool(value)


def _canon(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


class Registration:
    """Immutable canonical JSON; nested accessors return fresh values."""
    __slots__ = ("_json", "_digest")

    def __init__(self):
        raise RegistrationRefusal("inv_51", "use from_mapping")

    def __setattr__(self, name, value):
        raise RegistrationRefusal("inv_51", "registration is frozen")

    def __getattr__(self, name):
        if name in REGISTRATION_KEYS:
            return json.loads(self._json)[name]
        raise AttributeError(name)

    @property
    def digest(self):
        return self._digest

    @property
    def cap(self):
        g = self.to_mapping()
        return g["interior_s"] - g["guard_s"]

    @property
    def n_per_level(self):
        return len(self.item_ids_by_level[str(LEVELS[0])])

    @property
    def blocks_per_cell(self):
        g = self.to_mapping()
        return math.ceil(self.n_per_level / g["block_size"][g["arm"]])

    @property
    def max_gap(self):
        g = self.to_mapping()
        if g["budget_j"] is None or g["delta_upper_j_per_block_slot"] is None:
            return None
        return g["budget_j"] / (g["delta_upper_j_per_block_slot"] * self.blocks_per_cell)

    def worst(self, model):
        g = self.to_mapping()
        arm = g["arm"]
        return g["cap_tokens"][arm] * g["s_per_token_upper"][model][arm] + g["prefill_s"][model][arm]

    def to_mapping(self):
        return json.loads(self._json)

    @classmethod
    def from_mapping(cls, mapping):
        _need(type(mapping) is dict and set(mapping) == REGISTRATION_KEYS, "inv_51", "registration key set")
        try:
            raw = _canon(mapping)
            g = copy.deepcopy(mapping)
        except (TypeError, ValueError, OverflowError) as exc:
            raise RegistrationRefusal("inv_51", "canonical JSON") from exc
        _need(g["schema"] == REGISTRATION_SCHEMA and type(g["schema"]) is str, "inv_51", "schema")
        _need(type(g["mode"]) is str and g["mode"] in ("pilot", "registered"), "inv_51", "mode")
        for key in ("registration_id", "plan_id", "scorer_id", "arm"):
            _need(_text(g[key]), "inv_51", key)
        _need(type(g["arm_to_family"]) is dict and bool(g["arm_to_family"]) and all(_text(k) and _text(v) for k, v in g["arm_to_family"].items()) and g["arm"] in g["arm_to_family"], "inv_51", "arm family")
        roles = g["role_to_model_id"]
        _need(type(roles) is dict and set(roles) == {"8B", "1.7B"} and all(_text(v) for v in roles.values()) and roles["8B"] != roles["1.7B"], "inv_51", "roles")
        for key in ("sizing_receipt_sha256", "predictions_sha256"):
            value = g[key]
            _need((type(value) is str and _HEX.fullmatch(value) is not None) or (g["mode"] == "pilot" and value is None), "inv_51", key)
        _need(_num(g["alpha"]) and 0 < g["alpha"] <= 1, "inv_51", "alpha")
        _need(_integer(g["n_boot"], 1) and _integer(g["seed"], 0), "inv_51", "bootstrap")
        for key in ("floor_j", "anchor_j", "offset_s", "guard_s"):
            _need(_num(g[key]) and g[key] >= 0, "inv_51", key)
        for key in ("envelope_s", "interior_s", "pitch_s"):
            _need(_num(g[key]) and g[key] > 0, "inv_51", key)
        _need(g["offset_s"] + g["interior_s"] <= g["envelope_s"] and g["pitch_s"] >= g["envelope_s"], "inv_51", "grid")
        for key in ("cap_tokens", "block_size"):
            obj = g[key]
            _need(type(obj) is dict and set(obj) == {g["arm"]}, "unselected_arm_entry", key)
            _need(_integer(obj[g["arm"]], 1), "inv_06", key)
        ids = g["item_ids_by_level"]
        _need(type(ids) is dict and set(ids) == {str(level) for level in LEVELS}, "item_ids_by_level_keys", "level keys")
        _need(all(type(v) is list and v and all(_text(x) for x in v) for v in ids.values()), "inv_09", "item ids")
        flat = [item for level in LEVELS for item in ids[str(level)]]
        _need(len(set(flat)) == len(flat), "inv_09", "duplicate item")
        _need(len({len(v) for v in ids.values()}) == 1, "unequal_level_sizes", "level lengths")
        models = {roles["8B"], roles["1.7B"]}
        for key in ("s_per_token_upper", "prefill_s", "ceiling_s"):
            obj = g[key]
            _need(type(obj) is dict and set(obj) == models, "inv_06", key)
            for model in models:
                inner = obj[model]
                _need(type(inner) is dict and set(inner) == {g["arm"]}, "unselected_arm_entry", key)
                val = inner[g["arm"]]
                _need(_num(val) and (val >= 0 if key == "prefill_s" else val > 0), "inv_06", key)
        cap = g["interior_s"] - g["guard_s"]
        for model in models:
            worst = g["cap_tokens"][g["arm"]] * g["s_per_token_upper"][model][g["arm"]] + g["prefill_s"][model][g["arm"]]
            _need(worst <= g["ceiling_s"][model][g["arm"]] <= cap, "inv_06", "physical ceiling")
        for key, positive in (("delta_upper_j_per_block_slot", True), ("budget_j", False)):
            val = g[key]
            _need((_num(val) and (val > 0 if positive else val >= 0)) or (g["mode"] == "pilot" and val is None), "inv_51", key)
        _need(type(g["declared_sensitivities"]) is list and bool(g["declared_sensitivities"]) and all(_text(x) for x in g["declared_sensitivities"]), "inv_51", "sensitivities")
        obj = object.__new__(cls)
        object.__setattr__(obj, "_json", raw.decode("utf-8"))
        object.__setattr__(obj, "_digest", hashlib.sha256(raw).hexdigest())
        return obj
