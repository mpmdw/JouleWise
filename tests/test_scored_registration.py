import ast
import copy
import hashlib
import inspect
import json
from pathlib import Path
import unittest

from joulewise.scored_registration import Registration, RegistrationRefusal
import joulewise.scored_registration as scored_registration
import joulewise.scored_packer as scored_packer
import joulewise.scored_reduce as scored_reduce


def mapping(mode="pilot"):
    digest = "a" * 64
    return {"schema": "joulewise.scored_registration.v1", "mode": mode,
        "registration_id": "R1", "plan_id": "AP-5M", "sizing_receipt_sha256": digest if mode == "registered" else None,
        "arm": "on", "arm_to_family": {"on": "thinking_on"},
        "role_to_model_id": {"8B": "8B", "1.7B": "1.7B"}, "levels": [1, 2, 3, 4, 5],
        "merge_order": [[5, 4], [4, 3], [1, 2], [2, 3]], "min_correct": 3,
        "alpha": .05, "holm_m": 5, "n_boot": 100, "seed": 7,
        "floor_j": 1, "anchor_j": 1, "cap_tokens": {"on": 100},
        "cap_bound_fraction": .2, "block_size": {"on": 2}, "n_per_level": 10,
        "min_blocks_per_cell": 5, "min_envelopes_per_cell": 5,
        "envelope_s": 600, "offset_s": 60, "interior_s": 60, "guard_s": 10, "pitch_s": 600,
        "s_per_token_upper": {"8B": {"on": .3}, "1.7B": {"on": .3}},
        "prefill_s": {"8B": {"on": 0}, "1.7B": {"on": 0}},
        "ceiling_s": {"8B": {"on": 30}, "1.7B": {"on": 30}},
        "retry_stages": ["initial", "whole_block", "single_problem", "single_retry", "ceiling_violation"],
        "max_drift_lever_slots": 100 if mode == "registered" else None,
        "delta_upper_j_per_block_slot": 1 if mode == "registered" else None,
        "budget_j": 500 if mode == "registered" else None,
        "declared_sensitivities": ["paired_drop_retried"], "scorer_id": "S1",
        "item_set_sha256": digest}


def fixture(mode="pilot"):
    return Registration.from_mapping(mapping(mode))


class RegistrationTests(unittest.TestCase):
    def test_g1_drop_unknown_type_and_frozen_digest(self):
        source = mapping()
        for key in source:
            with self.subTest(key=key):
                changed = copy.deepcopy(source)
                del changed[key]
                with self.assertRaises(RegistrationRefusal):
                    Registration.from_mapping(changed)
        with self.assertRaises(RegistrationRefusal):
            Registration.from_mapping({**source, "surprise": 1})
        for key in ("min_correct", "holm_m", "n_boot", "seed", "n_per_level",
                    "min_blocks_per_cell", "min_envelopes_per_cell"):
            with self.subTest(key=key), self.assertRaises(RegistrationRefusal):
                Registration.from_mapping({**source, key: True})
        for key in ("cap_tokens", "block_size"):
            with self.subTest(key=key), self.assertRaises(RegistrationRefusal):
                Registration.from_mapping({**source, key: {"on": True}})
        for key, value in (("levels", [True, 2, 3, 4, 5]),
                           ("merge_order", [[5, 4], [4, 3], [True, 2], [2, 3]])):
            with self.subTest(key=key), self.assertRaises(RegistrationRefusal):
                Registration.from_mapping({**source, key: value})
        reg = fixture()
        raw = json.dumps(source, sort_keys=True, separators=(",", ":"), allow_nan=False)
        self.assertEqual(reg.digest, hashlib.sha256(raw.encode()).hexdigest())
        with self.assertRaises(RegistrationRefusal):
            reg.arm = "off"
        reg.cap_tokens["on"] = 500
        self.assertEqual(reg.cap_tokens["on"], 100)
        with self.assertRaises(RegistrationRefusal):
            Registration()
        with self.assertRaises(AttributeError):
            getattr(reg, "not_a_field")
        self.assertEqual(reg.family, "thinking_on")

    def test_g1_coherence_and_ruled_constants(self):
        source = mapping()
        changes = [
            {"offset_s": -1}, {"interior_s": 10, "guard_s": 10},
            {"offset_s": 550}, {"pitch_s": 599},
            {"s_per_token_upper": {"8B": {"on": .6}, "1.7B": {"on": .3}}},
            {"ceiling_s": {"8B": {"on": 51}, "1.7B": {"on": 30}}},
            {"levels": [1, 2, 3, 4]}, {"min_correct": 2}, {"holm_m": 4},
            {"merge_order": [[5, 4], [1, 2]]},
            {"alpha": 0}, {"envelope_s": 0}, {"pitch_s": 0},
            {"floor_j": -1}, {"anchor_j": -1}, {"offset_s": -1},
            {"n_boot": 0}, {"n_per_level": 0}, {"min_blocks_per_cell": 0},
        ]
        for change in changes:
            with self.subTest(change=change), self.assertRaises(RegistrationRefusal):
                Registration.from_mapping({**source, **change})
        for key in ("sizing_receipt_sha256", "max_drift_lever_slots", "delta_upper_j_per_block_slot", "budget_j"):
            changed = mapping("registered")
            changed[key] = None
            with self.subTest(key=key), self.assertRaises(RegistrationRefusal):
                Registration.from_mapping(changed)
        self.assertEqual(fixture("registered").mode, "registered")
        mismatch = mapping("registered")
        mismatch["budget_j"] = 499
        with self.assertRaises(RegistrationRefusal):
            Registration.from_mapping(mismatch)
        zero_mismatch = mapping("registered")
        zero_mismatch["max_drift_lever_slots"] = 0
        with self.assertRaises(RegistrationRefusal):
            Registration.from_mapping(zero_mismatch)
        zero_delta = mapping("registered")
        zero_delta["delta_upper_j_per_block_slot"] = 0
        with self.assertRaises(RegistrationRefusal):
            Registration.from_mapping(zero_delta)
        zero_allowed = mapping()
        zero_allowed.update(floor_j=0, anchor_j=0, offset_s=0, guard_s=0)
        self.assertEqual(Registration.from_mapping(zero_allowed).floor_j, 0)
        exact_balance = mapping("registered")
        exact_balance["max_drift_lever_slots"] = 0
        exact_balance["budget_j"] = 0
        self.assertEqual(Registration.from_mapping(exact_balance).max_drift_lever_slots, 0)

    def test_g5_public_signatures_and_input_default_ast(self):
        self.assertTrue(all(p.default is inspect.Parameter.empty
            for p in inspect.signature(Registration.from_mapping).parameters.values()))
        for module in (scored_registration, scored_packer, scored_reduce):
            for name, obj in vars(module).items():
                if name.startswith("_") or getattr(obj, "__module__", None) != module.__name__:
                    continue
                if inspect.isfunction(obj):
                    self.assertTrue(all(p.default is inspect.Parameter.empty
                        for p in inspect.signature(obj).parameters.values()), name)
            source = Path(module.__file__).read_text()
            tree = ast.parse(source)
            lines = source.splitlines()
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in ("get", "setdefault"):
                    self.assertIn("# internal", lines[node.lineno - 1], f"{module.__name__}:{node.lineno}")
