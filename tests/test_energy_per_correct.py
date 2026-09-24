import copy
import hashlib
import json
import unittest
from unittest.mock import patch

from joulewise.energy_per_correct import (BelowFloorError, _allocated_energy,
                                          _bounds, _quantile, _ratio, decide, ratio_interval)
from joulewise.scored_packer import pack, requeue_overrun
from joulewise.scored_reduce import reduce


def cell(model, level, gross_each, outcomes, arm="on"):
    blocks = []
    for index, (gross, correct) in enumerate(zip(gross_each, outcomes)):
        blocks.append({"block_id": f"{model}:{level}:{index}", "level": level,
                       "gross_j": gross, "items": [{"item_id": f"p{level}-{index}",
                                                     "generated_tokens": 10 + index,
                                                     "correct": correct}]})
    return {"model": model, "arm": arm, "level": level, "blocks": blocks,
            "gross_j": sum(gross_each), "correct": sum(outcomes)}


def family():
    return {level: {"cell_8b": cell("8B", level, [20] * 3, [1] * 3),
                    "cell_1p7b": cell("1.7B", level, [10] * 3, [1] * 3)}
            for level in range(1, 6)}


def decision(levels, ps, directions):
    values = iter(zip(ps, directions))
    def ratio(*args, **kwargs):
        p, direction = next(values)
        below = direction == "8B cheaper"
        return {"estimate": 0.5 if below else 2.0,
                "interval": (0.4, 0.8) if below else (1.2, 2.5),
                "p_below": p / 2 if below else 1,
                "p_above": 1 if below else p / 2,
                "p_two_sided": p}
    with patch("joulewise.energy_per_correct.ratio_interval", side_effect=ratio):
        return decide(levels, arm="on", family="primary", floor_j=1, anchor_j=1)


def decision_by_group(levels, directions):
    def mocked(a, b, **kwargs):
        group = tuple(sorted({block["level"] for block in a["blocks"]}))
        direction = directions[group]
        below = direction == "8B cheaper"
        return {"estimate": .5 if below else 2,
                "interval": (.4, .8) if below else (1.2, 2.5),
                "p_below": .0005 if below else 1,
                "p_above": 1 if below else .0005,
                "p_two_sided": .001}
    with patch("joulewise.energy_per_correct.ratio_interval", side_effect=mocked):
        return decide(levels, arm="on", family="primary", floor_j=1, anchor_j=1)


class EnergyPerCorrectTests(unittest.TestCase):
    def test_worked_ratio_interval_and_seed(self):
        eight = cell("8B", 1, [20] * 5, [1] * 5)
        small = cell("1.7B", 1, [10] * 5, [1] * 5)
        result = ratio_interval(eight, small, n_boot=99, seed=7, floor_j=1, anchor_j=1)
        self.assertEqual(result, ratio_interval(eight, small, n_boot=99, seed=7,
                                                floor_j=1, anchor_j=1))
        self.assertEqual(result["estimate"], 2)
        self.assertEqual(result["interval"], (1.5, 2.75))
        self.assertEqual((result["p_above"], result["p_below"], result["p_two_sided"]),
                         (.01, 1.0, .02))

    def test_x2_split_parent_pairing_and_per_window_bound(self):
        eight = cell("8B", 1, [20] * 5, [1] * 5)
        small = cell("1.7B", 1, [10] * 5, [1] * 5)
        original = ratio_interval(eight, small, n_boot=99, seed=7, floor_j=1, anchor_j=1)
        split = copy.deepcopy(eight)
        parent = split["blocks"].pop(0)
        parent["items"] = [{"item_id": "p1-0a", "generated_tokens": 10, "correct": 1},
                           {"item_id": "p1-0b", "generated_tokens": 10, "correct": 1}]
        # Pair both models on the same parent membership.
        small["blocks"][0]["items"] = copy.deepcopy(parent["items"])
        small["correct"] += 1
        eight["blocks"][0]["items"] = copy.deepcopy(parent["items"])
        eight["correct"] += 1
        unsplit = ratio_interval(eight, small, n_boot=99, seed=7, floor_j=1, anchor_j=1)
        for i, item in enumerate(parent["items"]):
            split["blocks"].append({"block_id": f"child{i}", "parent_block_id": parent["block_id"],
                                    "level": 1, "gross_j": 10, "items": [item]})
        split["correct"] += 1
        result = ratio_interval(split, small, n_boot=99, seed=7, floor_j=1, anchor_j=1)
        self.assertEqual(result["estimate"], unsplit["estimate"])
        self.assertLess(result["interval"][0], unsplit["interval"][0])
        self.assertGreater(result["interval"][1], unsplit["interval"][1])
        self.assertEqual(original["estimate"], 2)

    def test_x2_requeue_reduce_pairing(self):
        items = {1: [f"p{i}" for i in range(10)]}
        predictions = {model: {item: 2 for item in items[1]} for model in ("8B", "1.7B")}
        roster = pack(items, predictions, ("8B", "1.7B"), "on", 2, 60, 0,
                      registered_levels=(1,), cap_tokens_by_arm={"on": 100},
                      envelope_s=600, offset_s=60, pitch_s=600)
        parent = roster["blocks"][0]
        first = requeue_overrun(roster, parent["block_id"])
        second = requeue_overrun(first, parent["block_id"],
                                 worst_case_s_per_item={item: 5 for item in parent["items"]})
        def reduced(blocks):
            rows, windows = [], []
            for block in blocks:
                if block.get("superseded"):
                    continue
                windows.append({"block_id": block["block_id"],
                                "gross_j": 10 if block["model"] == "8B" and block.get("parent_block_id")
                                else 20 if block["model"] == "8B" else 10})
                for item in block["items"]:
                    rows.append({"item_id": item, "model": block["model"], "arm": "on", "level": 1,
                                 "block_id": block["block_id"], "parent_block_id": block.get("parent_block_id"),
                                 "retry_stage": block["retry_stage"], "prompt_tokens": 1,
                                 "generated_tokens": 1, "outcome": "correct"})
            return reduce(rows, windows)
        cells = reduced(second["blocks"])
        split = ratio_interval(cells[("8B", "on", 1)], cells[("1.7B", "on", 1)],
                               n_boot=99, seed=1, floor_j=1, anchor_j=1)
        unsplit = reduced(roster["blocks"])
        original = ratio_interval(unsplit[("8B", "on", 1)], unsplit[("1.7B", "on", 1)],
                                  n_boot=99, seed=1, floor_j=1, anchor_j=1)
        self.assertEqual(split["estimate"], original["estimate"])
        self.assertLess(split["interval"][0], original["interval"][0])

    def test_x8_floor_gate(self):
        with self.assertRaises(BelowFloorError):
            ratio_interval(cell("8B", 1, [1] * 5, [1] * 5),
                           cell("1.7B", 1, [1] * 5, [1] * 5),
                           n_boot=10, seed=1, floor_j=2, anchor_j=0)

    def test_x13_zero_token_allocation(self):
        self.assertEqual(_allocated_energy(20, {"a": {"generated_tokens": 0},
                                                "b": {"generated_tokens": 0}}, ["a"]), 10)
        eight = cell("8B", 1, [20] * 5, [1] * 5)
        small = cell("1.7B", 1, [10] * 5, [1] * 5)
        for c in (eight, small):
            for block in c["blocks"]:
                block["items"][0]["generated_tokens"] = 0
        self.assertEqual(ratio_interval(eight, small, n_boot=99, seed=7, floor_j=1, anchor_j=1)["estimate"], 2)

    def test_x1_crossover_direction_and_merged_boundary(self):
        ps = [.001, .006, .011, .020, .040]
        self.assertIsNone(decision(family(), ps, ["8B cheaper"] * 2 + ["1.7B cheaper"] * 3)["crossover_level"])
        self.assertIsNone(decision(family(), ps, ["8B cheaper"] * 2 + ["1.7B cheaper"] * 3)["crossover_reason"])
        self.assertEqual(decision(family(), ps, ["1.7B cheaper"] * 2 + ["8B cheaper"] * 3)["crossover_level"], 3)
        no_decision = iter([
            {"estimate": 2, "interval": (1.2, 2.5), "p_below": 1, "p_above": .0005, "p_two_sided": .001},
            {"estimate": 1, "interval": (.8, 1.2), "p_below": .5, "p_above": .5, "p_two_sided": 1},
            *[{"estimate": .5, "interval": (.4, .8), "p_below": .0005, "p_above": 1,
               "p_two_sided": .001} for _ in range(3)]])
        with patch("joulewise.energy_per_correct.ratio_interval", side_effect=lambda *a, **kw: next(no_decision)):
            pattern = decide(family(), arm="on", family="primary", floor_j=1, anchor_j=1)
        self.assertEqual(pattern["levels"][2]["status"], "not resolved")
        self.assertEqual(pattern["crossover_level"], 3)
        levels = family()
        levels[5]["cell_8b"]["correct"] = 2
        result = decision(levels, ps[:4], ["1.7B cheaper"] * 3 + ["8B cheaper"])
        self.assertIsNone(result["crossover_level"])
        self.assertEqual(result["crossover_reason"], "boundary_in_merged_group")
        self.assertEqual(result["levels"][4]["status"], "not estimable")
        self.assertEqual(len([g for g in result["groups"] if g["merged_level"] == "4–5"]), 1)

    def test_x12_holm_stop_and_exact_cutoff(self):
        result = decision(family(), [.02, .03, .04, .045, .05], ["8B cheaper"] * 5)
        self.assertEqual([result["levels"][i]["holm_significant"] for i in range(1, 6)], [False] * 5)
        exact = decision(family(), [.01, .0125, .016, .02, .04], ["8B cheaper"] * 5)
        self.assertTrue(all(exact["levels"][i]["holm_significant"] for i in range(1, 6)))

    def test_x6_x7_family_roles_estimability(self):
        levels = family()
        result = decision(levels, [.001] * 5, ["8B cheaper"] * 5)
        self.assertTrue(result["can_carry_headline"])
        with self.assertRaises(ValueError):
            decide(levels, arm="on", family="other", floor_j=1, anchor_j=1)
        with self.assertRaises(TypeError):
            decide(levels, arm="on", family="primary")
        levels[2]["cell_8b"]["arm"] = "off"
        with self.assertRaises(ValueError):
            decide(levels, arm="on", family="primary", floor_j=1, anchor_j=1)
        levels[2]["cell_8b"]["arm"] = "on"
        levels[2]["ratio"] = {"p_two_sided": 0}
        with self.assertRaises(ValueError):
            decide(levels, arm="on", family="primary", floor_j=1, anchor_j=1)
        del levels[2]["ratio"]
        for entry in levels.values():
            entry["cell_8b"]["correct"] = 0
        result = decide(levels, arm="on", family="secondary", floor_j=1, anchor_j=1, n_boot=10)
        self.assertFalse(result["can_carry_headline"])
        self.assertEqual(result["levels"][1]["status"], "not estimable")

    def test_x14_estimator_behavior_signature(self):
        observed = []
        cases = [
            ([20] * 5, [10] * 5, [1] * 5, [1] * 5, 1, 1),
            ([5, 5, 5, 5, 80], [10] * 5, [1] * 5, [1] * 5, 0, 0),
            ([3, 8, 21, 13, 34], [20, 12, 8, 16, 7], [1, 0, 1, 0, 1], [0, 1, 1, 1, 0], 2, 1),
            ([10] * 5, [10] * 5, [0] * 5, [1] * 5, 1, 0),
            ([10] * 5, [10] * 5, [1] * 5, [0] * 5, 1, 0),
            ([10] * 5, [10] * 5, [0] * 5, [0] * 5, 1, 0),
        ]
        for a, b, ca, cb, floor, anchor in cases:
            try:
                observed.append(ratio_interval(cell("8B", 1, a, ca), cell("1.7B", 1, b, cb),
                                               n_boot=37, seed=19, floor_j=floor, anchor_j=anchor))
            except ValueError as exc:
                observed.append(type(exc).__name__)
        digest = hashlib.sha256(json.dumps(observed, sort_keys=True).encode()).hexdigest()
        self.assertEqual(digest, "69c7dd3e26f6a03221982222f89df5a943c26acc722fd4fbf2303e3d8740466b")

    def test_x14_estimator_boundary_helpers_and_validation(self):
        self.assertEqual(_quantile([1, 3, 7], 0.25), 2)
        self.assertEqual(_quantile([1, 3, 7], 0.5), 3)
        self.assertIsNone(_ratio(0, 0, 0, 0))
        self.assertEqual(_ratio(5, 0, 10, 1), float("inf"))
        self.assertEqual(_ratio(5, 1, 10, 0), 0)
        self.assertEqual(_ratio(5, 1, 0, 1), float("inf"))
        self.assertIsNone(_ratio(-5, 1, 0, 1))
        self.assertIsNone(_ratio(0, 1, 0, 1))
        self.assertEqual(_bounds(1, 1, 1, 1, 2, 2), (0, float("inf")))
        a = cell("8B", 1, [10] * 5, [1] * 5)
        b = cell("1.7B", 1, [10] * 5, [1] * 5)
        for floor, anchor in ((-1, 0), (0, -1)):
            with self.assertRaises(ValueError):
                ratio_interval(a, b, n_boot=10, seed=1, floor_j=floor, anchor_j=anchor)
        for alpha in (0, 1, -0.1, 1.1):
            with self.assertRaises(ValueError):
                decide(family(), arm="on", family="primary", floor_j=1, anchor_j=1, alpha=alpha)

    def test_x14_decision_boundary_directions_and_sparse_shape(self):
        levels = family()
        ratios = {
            1: {"estimate": 2, "interval": (1.0, 2.5), "p_below": 1, "p_above": .0005, "p_two_sided": .001},
            2: {"estimate": 2, "interval": (1.2, 2.5), "p_below": .0005, "p_above": 1, "p_two_sided": .002},
            3: {"estimate": .5, "interval": (.4, 1.0), "p_below": .0015, "p_above": 1, "p_two_sided": .003},
            4: {"estimate": .5, "interval": (.4, .8), "p_below": 1, "p_above": .002, "p_two_sided": .004},
            5: {"estimate": .5, "interval": (.4, .8), "p_below": .0025, "p_above": 1, "p_two_sided": .005},
        }
        def mocked(a, b, **kwargs):
            return ratios[a["blocks"][0]["level"]]
        with patch("joulewise.energy_per_correct.ratio_interval", side_effect=mocked):
            result = decide(levels, arm="on", family="primary", floor_j=1, anchor_j=1)
        self.assertEqual([result["levels"][i]["status"] for i in range(1, 6)],
                         ["not resolved", "not resolved", "not resolved", "not resolved", "8B cheaper"])
        self.assertEqual([result["levels"][i]["holm_significant"] for i in range(1, 6)],
                         [False, False, False, False, True])
        # A sparse high end extends 5→4→3, while the low end extends 1→2.
        sparse = family()
        for i in (1, 4, 5):
            sparse[i]["cell_8b"]["correct"] = 0
            sparse[i]["cell_1p7b"]["correct"] = 0
        result = decide(sparse, arm="on", family="secondary", floor_j=1, anchor_j=1, n_boot=10)
        self.assertEqual([g["levels"] for g in result["groups"]], [[1, 2], [3, 4, 5]])
        high_sparse = family()
        for i in (4, 5):
            high_sparse[i]["cell_8b"]["correct"] = 0
            high_sparse[i]["cell_1p7b"]["correct"] = 0
        high = decide(high_sparse, arm="on", family="secondary", floor_j=1, anchor_j=1, n_boot=10)
        self.assertEqual([g["levels"] for g in high["groups"]], [[1], [2], [3, 4, 5]])
        low_sparse = family()
        for i in (1, 2):
            low_sparse[i]["cell_8b"]["correct"] = 0
            low_sparse[i]["cell_1p7b"]["correct"] = 0
        low = decide(low_sparse, arm="on", family="secondary", floor_j=1, anchor_j=1, n_boot=10)
        self.assertEqual([g["levels"] for g in low["groups"]], [[1, 2, 3], [4], [5]])

    def test_x14_bootstrap_zero_correct_draws_and_point_enclosure(self):
        a = cell("8B", 1, [5, 5, 5, 5, 100], [0, 0, 0, 0, 1])
        b = cell("1.7B", 1, [100, 5, 5, 5, 5], [1, 0, 0, 0, 0])
        result = ratio_interval(a, b, n_boot=99, seed=3, floor_j=1, anchor_j=1)
        self.assertEqual(result["estimate"], 1)
        self.assertLessEqual(result["interval"][0], 1)
        self.assertGreaterEqual(result["interval"][1], 1)
        self.assertEqual(result["p_two_sided"], 1)
        outlier = cell("8B", 1, [10, 10, 10, 10, 100], [1] * 5)
        uniform = cell("1.7B", 1, [10] * 5, [1] * 5)
        low_point = ratio_interval(outlier, uniform, n_boot=1, seed=3, floor_j=1, anchor_j=1)
        high_point = ratio_interval(outlier, uniform, n_boot=1, seed=1, floor_j=1, anchor_j=1)
        self.assertEqual(low_point["interval"][0], 2.1666666666666665)
        self.assertEqual(high_point["interval"][1], 3.75)

    def test_x14_crossover_merge_licensing_and_fallback(self):
        all_lower = decision_by_group(family(), {(i,): "1.7B cheaper" for i in range(1, 6)})
        self.assertIsNone(all_lower["crossover_level"])
        self.assertIsNone(all_lower["crossover_reason"])
        high_merge = family()
        high_merge[5]["cell_8b"]["correct"] = 2
        high_merge[5]["cell_1p7b"]["correct"] = 2
        direction = {(1,): "1.7B cheaper", (2,): "1.7B cheaper", (3,): "1.7B cheaper",
                     (4, 5): "1.7B cheaper"}
        fallback = decision_by_group(high_merge, direction)
        self.assertIsNone(fallback["crossover_level"])
        self.assertEqual(fallback["crossover_reason"], "boundary_in_merged_group")
        direction[(3,)] = "8B cheaper"
        located = decision_by_group(high_merge, direction)
        self.assertEqual(located["crossover_level"], 3)
        self.assertIsNone(located["crossover_reason"])
        low_merge = family()
        low_merge[1]["cell_8b"]["correct"] = 2
        low_merge[1]["cell_1p7b"]["correct"] = 2
        direction = {(1, 2): "1.7B cheaper", (3,): "8B cheaper",
                     (4,): "1.7B cheaper", (5,): "8B cheaper"}
        licensed = decision_by_group(low_merge, direction)
        self.assertIsNone(licensed["crossover_level"])
        self.assertEqual(licensed["crossover_reason"], "boundary_in_merged_group")
        after_only = decision_by_group(low_merge, {(1, 2): "8B cheaper", (3,): "8B cheaper",
                                                   (4,): "1.7B cheaper", (5,): "1.7B cheaper"})
        self.assertIsNone(after_only["crossover_level"])
        self.assertIsNone(after_only["crossover_reason"])


if __name__ == "__main__":
    unittest.main()
