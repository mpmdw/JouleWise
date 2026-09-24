import ast
import copy
import inspect
import json
import types
import unittest

import joulewise.scored_packer as scored_packer

from joulewise.scored_packer import PackingRefusal, pack, requeue_overrun


class ScoredPackerTests(unittest.TestCase):
    def fixture(self, levels=(1, 2), count=10, block_size=2, seconds=10, interior=70, guard=10):
        items = {level: [f"L{level}P{i}" for i in range(count)] for level in levels}
        predictions = {model: {item: seconds for rows in items.values() for item in rows}
                       for model in ("8B", "1.7B")}
        return pack(items, predictions, ("8B", "1.7B"), "on", block_size, interior, guard)

    def test_spread_pairing_capacity_digest_and_williams(self):
        roster = self.fixture()
        self.assertEqual(roster, self.fixture())
        self.assertEqual(len(roster["sha256"]), 64)
        self.assertTrue(all(e["predicted_s"] <= 60 for e in roster["envelopes"]))
        models = [e["model"] for e in roster["envelopes"]]
        self.assertEqual(models, models[::-1])
        for level in (1, 2):
            cell_blocks = {model: [b for b in roster["blocks"] if b["model"] == model and b["level"] == level]
                           for model in ("8B", "1.7B")}
            self.assertEqual([b["items"] for b in cell_blocks["8B"]],
                             [b["items"] for b in cell_blocks["1.7B"]])
            for model in ("8B", "1.7B"):
                ids = {b["block_id"] for b in cell_blocks[model]}
                containing = [e for e in roster["envelopes"] if ids.intersection(e["blocks"])]
                self.assertEqual(len(containing), 5)
                self.assertTrue(all(len(ids.intersection(e["blocks"])) == 1 for e in containing))
        self.assertNotEqual(roster["sha256"], self.fixture(seconds=11)["sha256"])
        a_envelopes = [e for e in roster["envelopes"] if e["model"] == "8B" and e["blocks"]]
        by_id = {b["block_id"]: b for b in roster["blocks"]}
        self.assertEqual([[by_id[bid]["level"] for bid in e["blocks"]] for e in a_envelopes[:2]],
                         [[1, 2], [2, 1]])

    def test_capacity_uses_guard_and_sum_not_each_operand(self):
        roster = self.fixture(levels=(1,), seconds=25, interior=60, guard=10)
        self.assertEqual(max(e["predicted_s"] for e in roster["envelopes"]), 50)
        with self.assertRaises(PackingRefusal) as caught:
            self.fixture(levels=(1,), seconds=26, interior=60, guard=10)
        self.assertEqual(caught.exception.cell, ("8B", "on", 1))
        with self.assertRaises(PackingRefusal):
            self.fixture(levels=(1,), seconds=25, interior=49, guard=0)

    def test_spread_refusal_names_cell(self):
        with self.assertRaises(PackingRefusal) as caught:
            self.fixture(levels=(1,), count=8, block_size=2)
        self.assertEqual(caught.exception.cell, ("8B", "on", 1))

    def test_overrun_requeue_then_split_never_drops_items(self):
        roster = self.fixture(levels=(1,), seconds=11)
        block = roster["blocks"][0]
        first = requeue_overrun(roster, block["block_id"])
        self.assertEqual(roster["blocks"][0]["attempt"], 0)
        self.assertEqual(first["blocks"][0]["attempt"], 1)
        self.assertEqual(first["envelopes"][-1]["blocks"], [block["block_id"]])
        second = requeue_overrun(first, block["block_id"])
        children = [b for b in second["blocks"] if b["block_id"].startswith(block["block_id"] + ":single:")]
        self.assertEqual([b["items"][0] for b in children], block["items"])
        self.assertTrue(all(b["block_id"] in e["blocks"] for b, e in zip(children, second["envelopes"][-2:])))
        self.assertEqual(second["blocks"][0]["superseded"], True)
        self.assertNotEqual(first["sha256"], second["sha256"])
        self.assertEqual([e["index"] for e in first["envelopes"][:len(roster["envelopes"])]],
                         [e["index"] for e in roster["envelopes"]])
        self.assertEqual(first["envelopes"][-1]["index"], len(roster["envelopes"]))
        self.assertIn(block["block_id"], first["envelopes"][0].get("voided_block_ids", []))

    def test_cell_specific_overflow(self):
        items = {1: [f"p{i}" for i in range(5)]}
        predicted = {"8B": {p: 1 for p in items[1]}, "1.7B": {p: 100 for p in items[1]}}
        with self.assertRaises(PackingRefusal) as caught:
            pack(items, predicted, ("8B", "1.7B"), "off", 1, 60, 10)
        self.assertEqual(caught.exception.cell, ("1.7B", "off", 1))

    def test_operand_collapse_cuts(self):
        """Every packer comparison (and min/max, if added) must be observable."""
        source = inspect.getsource(scored_packer)
        original_tree = ast.parse(source)
        candidates = [node for node in ast.walk(original_tree)
                      if isinstance(node, ast.Compare) or
                      (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                       and node.func.id in {"min", "max"})]
        self.assertGreater(len(candidates), 20)

        def signature(module):
            def observe(fn):
                try:
                    return ("ok", json.dumps(fn(), sort_keys=True, default=str))
                except Exception as exc:
                    return ("error", type(exc).__name__, str(exc))

            items = {level: [f"{level}-{index}" for index in range(10)] for level in (1, 2, 3)}
            pred = {model: {item: 10 if model == "A" else 12
                            for values in items.values() for item in values}
                    for model in ("A", "B")}
            roster = module.pack(items, pred, ("A", "B"), "on", 2, 70, 10)
            block_id = roster["blocks"][0]["block_id"]
            first = module.requeue_overrun(roster, block_id)
            second = module.requeue_overrun(first, block_id)
            child_id = second["blocks"][-1]["block_id"]
            unscheduled = copy.deepcopy(roster)
            for envelope in unscheduled["envelopes"]:
                if block_id in envelope["blocks"]:
                    envelope["blocks"].remove(block_id)
            even_odd = {"A": {p: 30 for p in items[1] + items[2]},
                        "B": {p: 12 for p in items[1] + items[2]}}
            even_even = {"A": {p: 30 for p in items[1] + items[2]},
                         "B": {p: 30 for p in items[1] + items[2]}}
            probes = [
                lambda: module.pack(items, pred, ("A", "B"), "on", 2, 70, 10),
                lambda: module.pack({1: items[1]}, pred, ("A", "B"), "on", 2, 50, 10),
                lambda: module.pack({1: items[1][:8]}, pred, ("A", "B"), "on", 2, 50, 10),
                lambda: module.pack({1: items[1], 2: items[2]}, even_odd, ("A", "B"), "on", 2, 70, 10),
                lambda: module.pack({1: items[1], 2: items[2]}, even_even, ("A", "B"), "on", 2, 70, 10),
                lambda: module.pack(items, pred, ("A", "A"), "on", 2, 70, 10),
                lambda: module.pack(items, pred, ("A", "B"), "on", 0, 70, 10),
                lambda: module.pack(items, pred, ("A", "B"), "on", 2, 0, 10),
                lambda: module.pack(items, pred, ("A", "B"), "on", 2, 70, -1),
                lambda: module.pack({1: items[1] + items[1][:1]}, pred, ("A", "B"), "on", 2, 70, 10),
                lambda: module.pack({1: items[1]}, {m: {p: 30 for p in items[1]} for m in ("A", "B")},
                                    ("A", "B"), "on", 2, 60, 10),
                lambda: module.pack({1: items[1]}, {"A": {p: 0 for p in items[1]},
                                                    "B": {p: 1 for p in items[1]}},
                                    ("A", "B"), "on", 2, 60, 10),
                lambda: module.requeue_overrun(roster, block_id),
                lambda: module.requeue_overrun(first, block_id),
                lambda: module.requeue_overrun(second, child_id),
                lambda: module.requeue_overrun(roster, "unknown"),
                lambda: module.requeue_overrun(unscheduled, block_id),
            ]
            return [observe(probe) for probe in probes]

        baseline = signature(scored_packer)

        class Collapse(ast.NodeTransformer):
            def __init__(self, position, operand):
                self.position = position
                self.operand = operand

            def visit_Compare(self, node):
                if (node.lineno, node.col_offset) == self.position:
                    return ast.copy_location(copy.deepcopy(
                        node.left if self.operand == 0 else node.comparators[0]), node)
                return self.generic_visit(node)

            def visit_Call(self, node):
                if (node.lineno, node.col_offset) == self.position:
                    return ast.copy_location(copy.deepcopy(node.args[self.operand]), node)
                return self.generic_visit(node)

        for candidate in candidates:
            for operand in (0, 1):
                tree = Collapse((candidate.lineno, candidate.col_offset), operand).visit(copy.deepcopy(original_tree))
                ast.fix_missing_locations(tree)
                mutant = types.ModuleType("scored_packer_mutant")
                try:
                    exec(compile(tree, "<scored-packer-mutant>", "exec"), mutant.__dict__)
                    observed = signature(mutant)
                except Exception as exc:
                    observed = ("error", type(exc).__name__, str(exc))
                self.assertNotEqual(baseline, observed,
                                    f"surviving operand-collapse cut at line {candidate.lineno}: "
                                    f"{ast.unparse(candidate)} operand {operand}")


if __name__ == "__main__":
    unittest.main()
