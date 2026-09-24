import unittest

from joulewise.energy_per_correct import decide, ratio_interval


def cell(model, level, gross_each, outcomes):
    blocks = []
    for index, (gross, correct) in enumerate(zip(gross_each, outcomes)):
        blocks.append({"block_id": f"{model}:{level}:{index}", "level": level,
                       "gross_j": gross, "items": [{"item_id": f"p{level}-{index}",
                                                     "generated_tokens": 10 + index,
                                                     "correct": correct}]})
    return {"model": model, "level": level, "blocks": blocks,
            "gross_j": sum(gross_each), "correct": sum(outcomes)}


class EnergyPerCorrectTests(unittest.TestCase):
    def test_estimate_interval_seed_and_instrument_widening(self):
        eight = cell("8B", 1, [20, 30, 40, 50, 60], [1, 1, 1, 0, 0])
        small = cell("1.7B", 1, [10, 15, 20, 25, 30], [1, 1, 1, 0, 0])
        plain = ratio_interval(eight, small, n_boot=200, seed=13, floor_j=0, anchor_j=0)
        widened = ratio_interval(eight, small, n_boot=200, seed=13, floor_j=1, anchor_j=1)
        self.assertEqual(plain, ratio_interval(eight, small, n_boot=200, seed=13, floor_j=0, anchor_j=0))
        self.assertEqual(plain["estimate"], 2)
        self.assertLessEqual(widened["interval"][0], plain["interval"][0])
        self.assertGreaterEqual(widened["interval"][1], plain["interval"][1])
        self.assertLessEqual(widened["p_above"], 1)
        self.assertGreaterEqual(widened["p_below"], plain["p_below"])

    def test_worked_constant_ratio_and_exact_widening(self):
        eight = cell("8B", 1, [20] * 5, [1] * 5)
        small = cell("1.7B", 1, [10] * 5, [1] * 5)
        result = ratio_interval(eight, small, n_boot=99, seed=7, floor_j=1, anchor_j=1)
        self.assertEqual(result["estimate"], 2)
        self.assertEqual(result["interval"], (1.5, 2.75))
        self.assertEqual(result["p_above"], 0.01)
        self.assertEqual(result["p_below"], 1.0)
        self.assertEqual(result["p_two_sided"], 0.02)

    def test_block_variation_changes_interval_and_pairing_required(self):
        eight = cell("8B", 1, [5, 5, 5, 5, 80], [1] * 5)
        small = cell("1.7B", 1, [10] * 5, [1] * 5)
        result = ratio_interval(eight, small, n_boot=1000, seed=1, floor_j=0, anchor_j=0)
        self.assertLess(result["interval"][0], result["estimate"])
        self.assertGreater(result["interval"][1], result["estimate"])
        small["blocks"][0]["items"][0]["item_id"] = "unpaired"
        with self.assertRaises(ValueError):
            ratio_interval(eight, small, n_boot=10, seed=1, floor_j=0, anchor_j=0)

    def test_holm_hand_computed_fixed_five_and_crossover(self):
        # Sorted p: .001,.006,.011,.020,.040; Holm cutoffs .010,.0125,.0167,.025,.05.
        ps = [0.001, 0.006, 0.011, 0.020, 0.040]
        levels = {}
        for level, p in enumerate(ps, 1):
            below = level <= 2
            levels[level] = {"cell_8b": cell("8B", level, [10] * 3, [1] * 3),
                             "cell_1p7b": cell("1.7B", level, [10] * 3, [1] * 3),
                             "ratio": {"estimate": 0.7 if below else 1.4,
                                       "interval": (0.5, 0.9) if below else (1.1, 1.7),
                                       "p_below": p / 2 if below else 1,
                                       "p_above": 1 if below else p / 2,
                                       "p_two_sided": p}}
        result = decide(levels)
        self.assertEqual(result["family_size"], 5)
        self.assertEqual([result["levels"][level]["decision"] for level in range(1, 6)],
                         ["8B cheaper", "8B cheaper", "1.7B cheaper", "1.7B cheaper", "1.7B cheaper"])
        self.assertEqual(result["crossover_level"], 3)
        levels[4]["ratio"]["interval"] = (0.9, 1.7)
        self.assertEqual(decide(levels)["levels"][4]["decision"], "not resolved")
        levels[2]["ratio"]["p_two_sided"] = 0.03
        self.assertEqual(decide(levels)["levels"][2]["decision"], "not resolved")

    def test_sparse_merge_by_correct_counts(self):
        levels = {}
        for level in range(1, 6):
            successes = [1, 1, 0] if level == 5 else [1, 1, 1]
            levels[level] = {"cell_8b": cell("8B", level, [5] * 3, successes),
                             "cell_1p7b": cell("1.7B", level, [10] * 3, successes),
                             "bootstrap": {"n_boot": 40, "seed": 4}}
        result = decide(levels)
        self.assertEqual(result["levels"][4]["merged_level"], "4–5")
        self.assertEqual(result["levels"][5]["merged_level"], "4–5")
        self.assertEqual(result["family_size"], 5)
        # Level 4 itself can be sparse: the declared high-side first merge is still 5→4.
        levels[5]["cell_8b"] = cell("8B", 5, [5] * 3, [1] * 3)
        levels[5]["cell_1p7b"] = cell("1.7B", 5, [10] * 3, [1] * 3)
        levels[4]["cell_8b"] = cell("8B", 4, [5] * 3, [1, 1, 0])
        self.assertEqual(decide(levels)["levels"][4]["merged_level"], "4–5")


if __name__ == "__main__":
    unittest.main()
