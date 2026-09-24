import copy
import unittest

from joulewise.scored_packer import pack, requeue_overrun
from joulewise.scored_reduce import reduce, ReductionRefusal
from tests.test_scored_packer import fixture


def records(roster):
    blocks = {b["block_id"]: b for b in roster["blocks"]}
    rows, windows = [], []
    for envelope in roster["envelopes"]:
        for bid in envelope["blocks"]:
            block = blocks[bid]
            windows.append({"block_id": bid, "attempt": block["attempt"], "gross_j": 10})
            for item in block["items"]:
                rows.append({"item_id": item, "model_id": block["model"], "arm": block["arm"],
                    "level": block["level"], "block_id": bid, "attempt": block["attempt"],
                    "prompt_tokens": 5, "generated_tokens": 10, "outcome": "correct",
                    "stop_reason": "stop", "truncated": False,
                    "retry_stage": block["retry_stage"], "parent_block_id": block["parent_block_id"]})
    return rows, windows


class ScoredReduceTests(unittest.TestCase):
    def setUp(self):
        self.reg, items, predicted = fixture()
        self.roster = pack(self.reg, items, predicted)
        self.rows, self.windows = records(self.roster)

    def test_g4_gross_only_cap_bound_and_binding(self):
        first = reduce(self.reg, self.roster, self.rows, self.windows)
        cell = first[("8B", "on", 1)]
        self.assertEqual(cell["correct"], 10)
        self.assertEqual(cell["gross_j"], 50)
        self.assertEqual(cell["registration_sha256"], self.reg.digest)
        self.assertEqual(cell["roster_sha256"], self.roster["sha256"])
        self.assertEqual(cell["retry_stage_counts"], {"initial": 10})
        row = next(r for r in self.rows if r["model_id"] == "8B" and r["level"] == 1)
        row["generated_tokens"] = 100
        with self.assertRaises(ReductionRefusal):
            reduce(self.reg, self.roster, self.rows, self.windows)
        row["stop_reason"] = "length"
        row["truncated"] = True
        with self.assertRaises(ReductionRefusal):
            reduce(self.reg, self.roster, self.rows, self.windows)
        row["outcome"] = "truncated"
        changed = reduce(self.reg, self.roster, self.rows, self.windows)[("8B", "on", 1)]
        self.assertEqual(changed["cap_hits"], 1)
        self.assertFalse(changed["cap_bound"])
        self.assertEqual(changed["correct"], 9)
        self.assertEqual(changed["j_per_correct"], 50 / 9)
        self.assertIs(next(item for block in changed["blocks"] for item in block["items"]
            if item["item_id"] == row["item_id"])["correct"], False)
        for target in [r for r in self.rows if r["model_id"] == "8B" and r["level"] == 1][1:3]:
            target.update(generated_tokens=100, stop_reason="length", truncated=True, outcome="truncated")
        self.assertTrue(reduce(self.reg, self.roster, self.rows, self.windows)[("8B", "on", 1)]["cap_bound"])

    def test_g4_window_attempts_voided_excluded_and_unmatched_refused(self):
        parent = self.roster["blocks"][0]
        executed = requeue_overrun(self.reg, self.roster, parent["block_id"], 2)
        rows, windows = records(executed)
        windows.append({"block_id": parent["block_id"], "attempt": 0, "gross_j": 10000})
        cell = reduce(self.reg, executed, rows, windows)[(parent["model"], parent["arm"], parent["level"])]
        self.assertEqual(cell["gross_j"], 50)
        self.assertEqual(cell["roster_sha256"], executed["sha256"])
        for bad in ({"block_id": "unknown", "attempt": 0, "gross_j": 1},
                    {"block_id": parent["block_id"], "attempt": 2, "gross_j": 1},
                    windows[0]):
            with self.subTest(bad=bad), self.assertRaises(ReductionRefusal):
                reduce(self.reg, executed, rows, windows + [bad])

    def test_g4_completeness_terminal_and_parent(self):
        parent = self.roster["blocks"][0]
        bid = parent["block_id"]
        first = requeue_overrun(self.reg, self.roster, bid, 2)
        second = requeue_overrun(self.reg, first, bid, {item: 3 for item in parent["items"]})
        child = next(b for b in second["blocks"] if b["parent_block_id"] == bid)
        third = requeue_overrun(self.reg, second, child["block_id"], {child["items"][0]: 31})
        fourth = requeue_overrun(self.reg, third, child["block_id"], {child["items"][0]: 31})
        rows, windows = records(fourth)
        result = reduce(self.reg, fourth, rows, windows)
        cell = result[(parent["model"], parent["arm"], parent["level"])]
        self.assertEqual(cell["terminal_refusals"][0]["item_id"], child["items"][0])
        self.assertEqual(cell["retry_stage_counts"]["ceiling_violation"], 1)
        sibling = next(b for b in fourth["blocks"] if b["parent_block_id"] == bid and b["block_id"] != child["block_id"])
        self.assertEqual(next(b for b in cell["blocks"] if b["block_id"] == sibling["block_id"])["parent_block_id"], bid)
        both_third = requeue_overrun(self.reg, fourth, sibling["block_id"], {sibling["items"][0]: 31})
        both_fourth = requeue_overrun(self.reg, both_third, sibling["block_id"], {sibling["items"][0]: 31})
        both_rows, both_windows = records(both_fourth)
        both_cell = reduce(self.reg, both_fourth, both_rows, both_windows)[(parent["model"], parent["arm"], parent["level"])]
        self.assertEqual({r["item_id"] for r in both_cell["terminal_refusals"]}, set(parent["items"]))
        with self.assertRaises(ReductionRefusal):
            reduce(self.reg, fourth, rows[:-1], windows)
        with self.assertRaises(ReductionRefusal):
            reduce(self.reg, fourth, rows + [rows[0]], windows)

    def test_g4_g5_row_and_window_key_sweep_alias_and_stage(self):
        for name, records_list in (("row", self.rows), ("window", self.windows)):
            for key in records_list[0]:
                altered = copy.deepcopy(records_list)
                del altered[0][key]
                with self.subTest(name=name, key=key), self.assertRaises(ReductionRefusal):
                    reduce(self.reg, self.roster, altered if name == "row" else self.rows,
                           altered if name == "window" else self.windows)
            altered = copy.deepcopy(records_list)
            altered[0]["unknown"] = 1
            with self.subTest(name=name, key="unknown"), self.assertRaises(ReductionRefusal):
                reduce(self.reg, self.roster, altered if name == "row" else self.rows,
                       altered if name == "window" else self.windows)
        alias = copy.deepcopy(self.rows)
        alias[0]["model"] = alias[0].pop("model_id")
        with self.assertRaises(ReductionRefusal):
            reduce(self.reg, self.roster, alias, self.windows)
        unknown = copy.deepcopy(self.rows)
        unknown[0]["retry_stage"] = "single_problem"
        with self.assertRaises(ReductionRefusal):
            reduce(self.reg, self.roster, unknown, self.windows)
        unknown[0]["retry_stage"] = "invented"
        with self.assertRaises(ReductionRefusal):
            reduce(self.reg, self.roster, unknown, self.windows)
        for changed in ({"gross_j": -1}, {"attempt": -1}):
            bad_windows = copy.deepcopy(self.windows)
            bad_windows[0].update(changed)
            with self.assertRaises(ReductionRefusal):
                reduce(self.reg, self.roster, self.rows, bad_windows)
        bad_rows = copy.deepcopy(self.rows)
        bad_rows[0]["prompt_tokens"] = -1
        with self.assertRaises(ReductionRefusal):
            reduce(self.reg, self.roster, bad_rows, self.windows)
        for field, value in (("outcome", []), ("block_id", [])):
            bad_rows = copy.deepcopy(self.rows)
            bad_rows[0][field] = value
            with self.assertRaises(ReductionRefusal):
                reduce(self.reg, self.roster, bad_rows, self.windows)
        terminal_roster = copy.deepcopy(self.roster)
        terminal_roster["terminal_refusals"] = [{"type": "ceiling_violation", "block_id": "x",
            "parent_block_id": "p", "item_id": "q", "model": "8B", "arm": "on", "level": 1}] * 2
        from joulewise.scored_packer import _digest
        _digest(terminal_roster)
        with self.assertRaises(ReductionRefusal):
            reduce(self.reg, terminal_roster, self.rows, self.windows)
        terminal_roster["terminal_refusals"][0]["item_id"] = []
        _digest(terminal_roster)
        with self.assertRaises(ReductionRefusal):
            reduce(self.reg, terminal_roster, self.rows, self.windows)
