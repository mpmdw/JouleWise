import ast
import copy
import inspect
import json
import hashlib
import random
import types
import unittest

import joulewise.scored_packer as scored_packer

from joulewise.scored_packer import PackingRefusal, pack, requeue_overrun


class ScoredPackerTests(unittest.TestCase):
    def fixture(self, levels=(1, 2), count=10, block_size=2, seconds=10, interior=70, guard=10):
        items = {level: [f"L{level}P{i}" for i in range(count)] for level in levels}
        predictions = {model: {item: seconds for rows in items.values() for item in rows}
                       for model in ("8B", "1.7B")}
        return pack(items, predictions, ("8B", "1.7B"), "on", block_size, interior, guard, registered_levels=levels, cap_tokens_by_arm={"on": 100}, envelope_s=600, offset_s=60, pitch_s=600)

    def test_spread_pairing_capacity_digest_and_williams(self):
        roster = self.fixture()
        self.assertEqual(roster, self.fixture())
        self.assertEqual(len(roster["sha256"]), 64)
        self.assertTrue(all(e["predicted_s"] <= 60 for e in roster["envelopes"]))
        models = [e["model"] for e in roster["envelopes"]]
        self.assertEqual(set(models), {"8B", "1.7B"})
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
        second = requeue_overrun(first, block["block_id"], worst_case_s_per_item={item: 11 for item in block["items"]})
        children = [b for b in second["blocks"] if b["block_id"].startswith(block["block_id"] + ":single:")]
        self.assertEqual([b["items"][0] for b in children], block["items"])
        self.assertEqual(len(second["envelopes"]), len(first["envelopes"]) + 1)
        self.assertEqual(second["envelopes"][len(first["envelopes"]) - 1]["blocks"], [])
        self.assertTrue(all(b["block_id"] in second["envelopes"][-1]["blocks"] for b in children))
        self.assertEqual(second["blocks"][0]["superseded"], True)
        self.assertNotEqual(first["sha256"], second["sha256"])
        self.assertEqual([e["index"] for e in first["envelopes"][:len(roster["envelopes"])]],
                         [e["index"] for e in roster["envelopes"]])
        self.assertEqual(first["envelopes"][-1]["index"], len(roster["envelopes"]))
        self.assertTrue(any(block["block_id"] in e.get("voided_block_ids", [])
                            for e in first["envelopes"]))

    def test_cell_specific_overflow(self):
        items = {1: [f"p{i}" for i in range(5)]}
        predicted = {"8B": {p: 1 for p in items[1]}, "1.7B": {p: 100 for p in items[1]}}
        with self.assertRaises(PackingRefusal) as caught:
            pack(items, predicted, ("8B", "1.7B"), "off", 1, 60, 10, registered_levels=(1,), cap_tokens_by_arm={"off": 100}, envelope_s=600, offset_s=60, pitch_s=600)
        self.assertEqual(caught.exception.cell, ("1.7B", "off", 1))

    def test_x3_x4_single_retry_terminal_and_worst_case_packing(self):
        roster = self.fixture(levels=(1,), count=10, block_size=2)
        parent = roster["blocks"][0]
        first = requeue_overrun(roster, parent["block_id"])
        second = requeue_overrun(first, parent["block_id"],
                                 worst_case_s_per_item={item: 20 for item in parent["items"]})
        children = [b for b in second["blocks"] if b.get("parent_block_id") == parent["block_id"]]
        self.assertEqual(len(children), 2)
        self.assertEqual([b["parent_block_id"] for b in children], [parent["block_id"]] * 2)
        self.assertEqual(second["envelopes"][-1]["blocks"], [b["block_id"] for b in children])
        self.assertLessEqual(second["envelopes"][-1]["predicted_s"], second["capacity_s"])
        separate = requeue_overrun(first, parent["block_id"],
                                   worst_case_s_per_item={item: 40 for item in parent["items"]})
        self.assertEqual(len(separate["envelopes"]), len(first["envelopes"]) + 2)
        self.assertTrue(all(e["predicted_s"] <= separate["capacity_s"]
                            for e in separate["envelopes"][-2:]))
        third = requeue_overrun(second, children[0]["block_id"])
        fourth = requeue_overrun(third, children[0]["block_id"])
        flagged = next(b for b in fourth["blocks"] if b["block_id"] == children[0]["block_id"])
        self.assertTrue(flagged["ceiling_violation"])
        self.assertEqual(flagged["retry_stage"], "ceiling_violation")
        self.assertEqual(fourth["terminal_refusals"][0]["type"], "ceiling_violation")
        self.assertFalse(any(flagged["block_id"] in e["blocks"] for e in fourth["envelopes"]))
        with self.assertRaises(PackingRefusal):
            requeue_overrun(first, parent["block_id"],
                            worst_case_s_per_item={item: 61 for item in parent["items"]})

    def test_x5_cell_balance_grid_and_idle_kind(self):
        for count in (10, 11, 13, 17):
            for size in (1, 2, 3, 4):
                for ratio in (5, 1.5):
                    with self.subTest(count=count, size=size, ratio=ratio):
                        if (count + size - 1) // size < 5:
                            continue
                        items = {1: [f"a{i}" for i in range(count)],
                                 2: [f"b{i}" for i in range(count)]}
                        pred = {model: {item: (2 if model == "8B" else 2 * ratio)
                                        for values in items.values() for item in values}
                                for model in ("8B", "1.7B")}
                        roster = pack(items, pred, ("8B", "1.7B"), "on", size, 60, 0,
                                      registered_levels=(1, 2), cap_tokens_by_arm={"on": 100},
                                      envelope_s=600, offset_s=60, pitch_s=600)
                        self.assertLessEqual(max(roster["drift_lever_slots"].values()), 0.5)
                        for e in roster["envelopes"]:
                            self.assertEqual(e["kind"], "loaded" if e["blocks"] else "idle_slot")
        worked = self.fixture(levels=(1,), count=10, block_size=2)
        self.assertEqual(len(worked["envelopes"]), 11)
        self.assertEqual(worked["drift_lever_slots"][1], 0)

    def test_x9_x10_digest_bounds_and_registered_levels(self):
        roster = self.fixture(levels=(1,))
        first = requeue_overrun(roster, roster["blocks"][0]["block_id"])
        self.assertEqual(first["registered_sha256"], roster["sha256"])
        self.assertEqual(first["parent_sha256"], roster["sha256"])
        second = requeue_overrun(first, roster["blocks"][0]["block_id"],
                                 worst_case_s_per_item={item: 10 for item in roster["blocks"][0]["items"]})
        self.assertEqual(second["registered_sha256"], roster["sha256"])
        self.assertEqual(second["parent_sha256"], first["sha256"])
        self.assertNotEqual(roster["sha256"], self.fixture(levels=(1,), seconds=11)["sha256"])
        items = {1: [f"p{i}" for i in range(10)]}
        predictions = {m: {p: 1 for p in items[1]} for m in ("8B", "1.7B")}
        with self.assertRaises(ValueError):
            pack(items, predictions, ("8B", "1.7B"), "on", 2, 60, 0,
                 registered_levels=(1, 2), cap_tokens_by_arm={"on": 100},
                 envelope_s=600, offset_s=60, pitch_s=600)
        common = dict(registered_levels=(1,), cap_tokens_by_arm={"on": 100},
                      envelope_s=600, offset_s=60, pitch_s=600)
        baseline = pack(items, predictions, ("8B", "1.7B"), "on", 2, 60, 0, **common)
        for changed in (dict(cap_tokens_by_arm={"on": 101}), dict(envelope_s=601),
                        dict(offset_s=61), dict(pitch_s=601)):
            self.assertNotEqual(baseline["sha256"],
                                pack(items, predictions, ("8B", "1.7B"), "on", 2, 60, 0,
                                     **{**common, **changed})["sha256"])

    def test_x14_file_behavior_signature(self):
        """Fixed broad roster signature, independent of the module under test."""
        rng = random.Random(17)
        hashes = []
        for n in (10, 11, 12, 13, 17, 21):
            for size in (1, 2, 3):
                if (n + size - 1) // size < 5:
                    continue
                for count_levels in (1, 2, 3):
                    items = {level: [f"{n}-{size}-{count_levels}-{level}-{i}" for i in range(n)]
                             for level in range(1, count_levels + 1)}
                    pred = {m: {p: rng.randint(1, 12) for values in items.values() for p in values}
                            for m in ("8B", "1.7B")}
                    roster = pack(items, pred, ("8B", "1.7B"), "on", size, 100, 5,
                                  registered_levels=tuple(items), cap_tokens_by_arm={"on": 100},
                                  envelope_s=600, offset_s=60, pitch_s=600)
                    hashes.append(roster["sha256"])
        self.assertEqual(len(hashes), 45)
        self.assertEqual(hashlib.sha256(json.dumps(hashes).encode()).hexdigest(),
                         "e6e4becac264cdac2a48ffabd5c8b9f45532c8118b12ae11d79b34b464445064")

    def test_x14_invalid_inputs_and_digest_replay(self):
        roster = self.fixture(levels=(1,))
        with self.assertRaises(KeyError):
            requeue_overrun(roster, "missing")
        unscheduled = copy.deepcopy(roster)
        bid = unscheduled["blocks"][0]["block_id"]
        for envelope in unscheduled["envelopes"]:
            if bid in envelope["blocks"]:
                envelope["blocks"].remove(bid)
        with self.assertRaises(ValueError):
            requeue_overrun(unscheduled, bid)
        first = requeue_overrun(roster, bid)
        payload = {key: value for key, value in first.items() if key != "sha256"}
        expected = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"),
                                            allow_nan=False).encode()).hexdigest()
        self.assertEqual(first["sha256"], expected)
        items = {1: [f"p{i}" for i in range(10)]}
        common = dict(registered_levels=(1,), cap_tokens_by_arm={"on": 100},
                      envelope_s=600, offset_s=60, pitch_s=600)
        predictions = {m: {p: 1 for p in items[1]} for m in ("8B", "1.7B")}
        for duration in (0, -1):
            bad = copy.deepcopy(predictions)
            bad["8B"]["p0"] = duration
            with self.assertRaises(ValueError):
                pack(items, bad, ("8B", "1.7B"), "on", 2, 60, 0, **common)
        for args in ((0, 0), (60, -1)):
            with self.assertRaisesRegex(ValueError, "invalid interior or guard"):
                pack(items, predictions, ("8B", "1.7B"), "on", 2, *args, **common)
        for changed in (dict(cap_tokens_by_arm={"on": 0}), dict(offset_s=-1),
                        dict(offset_s=600), dict(envelope_s=0), dict(pitch_s=0)):
            with self.assertRaises(ValueError):
                pack(items, predictions, ("8B", "1.7B"), "on", 2, 60, 0,
                     **{**common, **changed})
        with self.assertRaises(ValueError):
            requeue_overrun(first, bid)
        with self.assertRaises(PackingRefusal):
            requeue_overrun(first, bid, worst_case_s_per_item={item: 0 for item in roster["blocks"][0]["items"]})

    def test_x14_tight_capacity_behavior_signature(self):
        rng = random.Random(181)
        chosen = {(10, 2, 4), (13, 2, 3), (13, 3, 2), (17, 3, 4)}
        hashes = []
        for n in (10, 11, 13, 17):
            for size in (1, 2, 3):
                if (n + size - 1) // size < 5:
                    continue
                for count_levels in (2, 3, 4):
                    items = {level: [f"{n}-{size}-{count_levels}-{level}-{i}" for i in range(n)]
                             for level in range(1, count_levels + 1)}
                    pred = {m: {p: rng.randint(1, 12) for values in items.values() for p in values}
                            for m in ("8B", "1.7B")}
                    if (n, size, count_levels) in chosen:
                        roster = pack(items, pred, ("8B", "1.7B"), "on", size, 40, 0,
                                      registered_levels=tuple(items), cap_tokens_by_arm={"on": 100},
                                      envelope_s=600, offset_s=60, pitch_s=600)
                        hashes.append(roster["sha256"])
        self.assertEqual(hashlib.sha256(json.dumps(hashes).encode()).hexdigest(),
                         "e15f23c06752c646379ebc81faa6b701e7866a8cb97a91369a63a214f3a77804")



if __name__ == "__main__":
    unittest.main()
