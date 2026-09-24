import unittest

from joulewise.scored_reduce import reduce


class ScoredReduceTests(unittest.TestCase):
    def row(self, item, block, outcome="correct", generated=10):
        return {"item_id": item, "level": 2, "model_id": "8B", "arm": "on",
                "block_id": block, "prompt_tokens": 5, "generated_tokens": generated,
                "outcome": outcome}

    def test_gross_only_and_idle_padding_exact_zero(self):
        rows = [self.row("a", "b1"), self.row("b", "b1", "incorrect"),
                self.row("c", "b2", "malformed"), self.row("d", "b2", "truncated")]
        windows = [{"block_id": "b1", "gross_j": 120, "idle_padding_j": 500},
                   {"block_id": "b2", "gross_j": 80, "offset_j": 30, "tail_j": 900}]
        first = reduce(rows, windows)[("8B", "on", 2)]
        changed = [dict(w, idle_padding_j=100000, offset_j=9999, tail_j=99999) for w in windows]
        second = reduce(rows, changed)[("8B", "on", 2)]
        self.assertEqual(first["gross_j"], 200)
        self.assertEqual(first["j_per_correct"], 200)
        self.assertEqual(second["j_per_correct"] - first["j_per_correct"], 0)
        self.assertEqual(first["accuracy"], 0.25)
        self.assertEqual(first["generated_tokens_per_attempt"], 10)
        self.assertEqual(first["j_per_token"], 5)
        self.assertEqual(first["cap_hit_fraction"], 0.25)
        self.assertTrue(first["cap_bound"])

    def test_zero_correct_undefined(self):
        cell = reduce([self.row("a", "b", "malformed")], [{"block_id": "b", "gross_j": 9}])[("8B", "on", 2)]
        self.assertIsNone(cell["j_per_correct"])
        self.assertEqual(cell["accuracy"], 0)

    def test_cap_bound_strictly_above_twenty_percent(self):
        rows = [self.row(str(i), "b", "truncated" if i == 0 else "incorrect") for i in range(5)]
        at = reduce(rows, [{"block_id": "b", "gross_j": 10}])[("8B", "on", 2)]
        self.assertEqual(at["cap_hit_fraction"], 0.2)
        self.assertFalse(at["cap_bound"])
        rows.append(self.row("5", "b", "truncated"))
        over = reduce(rows, [{"block_id": "b", "gross_j": 10}])[("8B", "on", 2)]
        self.assertTrue(over["cap_bound"])
        self.assertEqual(over["cap_bound_label"], "cap-bound")

    def test_missing_and_double_windows_refused(self):
        with self.assertRaises(ValueError):
            reduce([self.row("a", "b")], [])
        with self.assertRaises(ValueError):
            reduce([self.row("a", "b")], [{"block_id": "b", "gross_j": 1}] * 2)

    def test_x11_capped_correct_refused_and_retry_stage_counts(self):
        for flag in ({"truncated": True}, {"stop_reason": "length"}):
            with self.subTest(flag=flag), self.assertRaises(ValueError):
                reduce([dict(self.row("a", "b"), **flag)], [{"block_id": "b", "gross_j": 10}])
        rows = [dict(self.row("a", "b", "incorrect"), retry_stage="whole_block"),
                dict(self.row("c", "b", "incorrect"), retry_stage="single_problem", stop_reason="length")]
        result = reduce(rows, [{"block_id": "b", "gross_j": 10}])[("8B", "on", 2)]
        self.assertEqual(result["retry_stage_counts"], {"whole_block": 1, "single_problem": 1})
        self.assertEqual(result["cap_hits"], 1)

    def test_x14_reducer_alias_negative_and_item_flags(self):
        alias = {"problem_id": "a", "level": 2, "model": "8B", "arm": "on",
                 "sub_block_id": "b", "prompt_tokens": 5, "emitted_tokens": 10,
                 "outcome": "correct"}
        result = reduce([alias], [{"sub_block_id": "b", "energy_gross_j": 12}])[("8B", "on", 2)]
        self.assertEqual(result["blocks"][0]["items"][0]["correct"], True)
        self.assertEqual(result["correct"], 1)
        with self.assertRaises(ValueError):
            reduce([dict(alias, outcome="incorrect", stop_reason="length")],
                   [{"sub_block_id": "b", "gross_j": -1}])
        uncapped = reduce([dict(alias, outcome="incorrect", stop_reason="stop")],
                          [{"sub_block_id": "b", "gross_j": 12}])[("8B", "on", 2)]
        self.assertEqual(uncapped["cap_hits"], 0)
        self.assertIs(uncapped["blocks"][0]["items"][0]["correct"], False)


if __name__ == "__main__":
    unittest.main()
