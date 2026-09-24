import copy
import unittest

from joulewise.scored_registration import Registration
from joulewise.scored_packer import PackingRefusal, pack, requeue_overrun
from tests.test_scored_registration import mapping


def fixture(mode="pilot", seconds=1, changes=None):
    source = mapping(mode)
    if changes:
        source.update(changes)
    registration = Registration.from_mapping(source)
    items = {level: [f"L{level}P{i}" for i in range(source["n_per_level"])] for level in source["levels"]}
    predicted = {model: {item: seconds for rows in items.values() for item in rows}
                 for model in source["role_to_model_id"].values()}
    return registration, items, predicted


class ScoredPackerTests(unittest.TestCase):
    def test_g2_registration_binding_pilot_gap_and_spread(self):
        reg, items, predicted = fixture()
        roster = pack(reg, items, predicted)
        self.assertFalse(roster["claim_ready"])
        self.assertEqual(roster["registration_sha256"], reg.digest)
        self.assertEqual(set(roster["drift_lever_slots"]), set(reg.levels))
        self.assertEqual(roster, pack(reg, items, predicted))
        self.assertEqual(roster["sha256"], "c1ec61e9ff637c9b21ee04994f5e59cee3d050b846c19cf31b3aa415ce8becdd")
        self.assertTrue(all(e["predicted_s"] <= roster["capacity_s"] for e in roster["envelopes"]))
        for level in reg.levels:
            by_model = {model: [b["items"] for b in roster["blocks"] if b["model"] == model and b["level"] == level]
                        for model in roster["models"]}
            self.assertEqual(*by_model.values())
            for model in roster["models"]:
                ids = {b["block_id"] for b in roster["blocks"] if b["model"] == model and b["level"] == level}
                self.assertGreaterEqual(sum(bool(ids.intersection(e["blocks"])) for e in roster["envelopes"]), 5)
        self.assertTrue(any(e["kind"] == "idle_slot" for e in roster["envelopes"]))
        by_id = {b["block_id"]: b for b in roster["blocks"]}
        for model in roster["models"]:
            loaded = [e for e in roster["envelopes"] if e["model"] == model and e["blocks"]]
            self.assertEqual([[by_id[bid]["level"] for bid in e["blocks"]] for e in loaded[:2]],
                             [[1, 5, 2, 4, 3], [2, 1, 3, 5, 4]])

    def test_g2_registered_gap_refusal_and_pilot_recording(self):
        reg, items, predicted = fixture()
        for item in predicted["1.7B"]:
            predicted["1.7B"][item] = 12
        pilot = pack(reg, items, predicted)
        self.assertEqual(pilot["sha256"], "9ebd780ff05805689fc8ab5e53c33d1f6ccffccbed6297395204bf11b2546a29")
        self.assertFalse(pilot["claim_ready"])
        self.assertGreaterEqual(max(pilot["drift_lever_slots"].values()), 0)
        strict, _, _ = fixture("registered", changes={"max_drift_lever_slots": .0001, "budget_j": .0005})
        self.assertGreater(max(pilot["drift_lever_slots"].values()), .0001)
        with self.assertRaises(PackingRefusal):
            pack(strict, items, predicted)
        more_envelopes, _, _ = fixture(changes={"min_envelopes_per_cell": 6})
        crowded = {model: {item: 12 for item in predicted[model]} for model in predicted}
        with self.assertRaises(PackingRefusal):
            pack(more_envelopes, items, crowded)
        loose, _, _ = fixture("registered")
        accepted = pack(loose, items, predicted)
        self.assertTrue(accepted["claim_ready"])
        retry = requeue_overrun(loose, accepted, accepted["blocks"][0]["block_id"], 2)
        self.assertFalse(any(retry["drift_exceeded"].values()))
        modest, _, _ = fixture("registered", changes={"max_drift_lever_slots": .7, "budget_j": 3.5})
        accepted = pack(modest, items, predicted)
        retry = requeue_overrun(modest, accepted, accepted["blocks"][0]["block_id"], 2)
        self.assertTrue(any(retry["drift_exceeded"].values()))

    def test_g3_digest_derived_worst_and_stages(self):
        reg, items, predicted = fixture()
        roster = pack(reg, items, predicted)
        bid = roster["blocks"][0]["block_id"]
        tampered = copy.deepcopy(roster)
        tampered["blocks"][0]["predicted_s"] += 1
        with self.assertRaises(PackingRefusal):
            requeue_overrun(reg, tampered, bid, 2)
        changed = mapping()
        changed["registration_id"] = "R2"
        with self.assertRaises(PackingRefusal):
            requeue_overrun(Registration.from_mapping(changed), roster, bid, 2)
        with self.assertRaises(PackingRefusal):
            requeue_overrun(reg, roster, bid, 61)
        first = requeue_overrun(reg, roster, bid, 2)
        self.assertEqual(first["sha256"], "4cf2bd6cc043886d0d8d2619f4d93653dab9fb68582c59bd46e56df853a5cff3")
        self.assertEqual(first["registered_sha256"], roster["sha256"])
        broken_chain = copy.deepcopy(first)
        broken_chain["registered_sha256"] = None
        from joulewise.scored_packer import _digest
        _digest(broken_chain)
        with self.assertRaises(PackingRefusal):
            requeue_overrun(reg, broken_chain, bid, 2)
        parent = next(b for b in first["blocks"] if b["block_id"] == bid)
        with self.assertRaises(PackingRefusal):
            requeue_overrun(reg, first, bid, {item: 31 for item in parent["items"]})
        second = requeue_overrun(reg, first, bid, {item: 3 for item in parent["items"]})
        self.assertEqual(second["sha256"], "8ddb0a1ac1fa4f77205c1231ca552977d3565e89afd82ad84307f261eabf6119")
        children = [b for b in second["blocks"] if b["parent_block_id"] == bid]
        self.assertEqual({b["retry_stage"] for b in children}, {"single_problem"})
        self.assertEqual({b["predicted_s"] for b in children}, {30})
        one = children[0]
        third = requeue_overrun(reg, second, one["block_id"], {one["items"][0]: 31})
        self.assertEqual(third["sha256"], "0ec85c6b4b4b4bd8f176dd087a9ba1899986d9dd4b39a35f79531d5fb3ac2e00")
        progressed = next(b for b in third["blocks"] if b["block_id"] == one["block_id"])
        self.assertEqual(progressed["retry_stage"], "single_retry")
        within_bound = requeue_overrun(reg, third, one["block_id"], {one["items"][0]: 5})
        self.assertEqual(within_bound["terminal_refusals"], [])
        self.assertEqual(next(b for b in within_bound["blocks"] if b["block_id"] == one["block_id"])["retry_stage"], "single_retry")
        fourth = requeue_overrun(reg, third, one["block_id"], {one["items"][0]: 31})
        self.assertEqual(fourth["sha256"], "3fc426283c3fe5688967cd3ab60119ef463606fdbdf2e6e9fe65a13c4b1f7684")
        terminal = fourth["terminal_refusals"][0]
        self.assertEqual(terminal["type"], "ceiling_violation")
        self.assertEqual(terminal["item_id"], one["items"][0])
        self.assertEqual(fourth["parent_sha256"], third["sha256"])
        self.assertTrue(all(current["registered_sha256"] == roster["sha256"]
            for current in (first, second, third, fourth)))
        self.assertEqual(fourth["registration_sha256"], reg.digest)
        self.assertEqual(set(fourth["drift_lever_slots"]), set(reg.levels))

    def test_g3_innocent_envelope_mate_keeps_retry_budget(self):
        reg, items, predicted = fixture(changes={
            "s_per_token_upper": {"8B": {"on": .2}, "1.7B": {"on": .2}},
            "ceiling_s": {"8B": {"on": 20}, "1.7B": {"on": 20}}})
        roster = pack(reg, items, predicted)
        bid = roster["blocks"][0]["block_id"]
        parent = roster["blocks"][0]
        first = requeue_overrun(reg, roster, bid, 2)
        second = requeue_overrun(reg, first, bid, {item: 3 for item in parent["items"]})
        children = [b for b in second["blocks"] if b["parent_block_id"] == bid]
        self.assertEqual(len(children), 2)
        self.assertTrue(any(set(e["blocks"]) == {b["block_id"] for b in children} for e in second["envelopes"]))
        bad, mate = children
        third = requeue_overrun(reg, second, bad["block_id"], {bad["items"][0]: 21, mate["items"][0]: 5})
        stages = {b["block_id"]: b["retry_stage"] for b in third["blocks"]}
        self.assertEqual(stages[bad["block_id"]], "single_retry")
        self.assertEqual(stages[mate["block_id"]], "single_problem")
        fourth = requeue_overrun(reg, third, bad["block_id"], {bad["items"][0]: 21, mate["items"][0]: 5})
        self.assertEqual({r["item_id"] for r in fourth["terminal_refusals"]}, {bad["items"][0]})
        self.assertEqual(next(b for b in fourth["blocks"] if b["block_id"] == mate["block_id"])["retry_stage"], "single_problem")
        reversed_target = requeue_overrun(reg, second, mate["block_id"],
            {bad["items"][0]: 21, mate["items"][0]: 5})
        self.assertEqual(next(b for b in reversed_target["blocks"] if b["block_id"] == bad["block_id"])["retry_stage"], "single_retry")
        self.assertEqual(next(b for b in reversed_target["blocks"] if b["block_id"] == mate["block_id"])["retry_stage"], "single_problem")
        only_bad = requeue_overrun(reg, second, bad["block_id"], {bad["items"][0]: 21})
        self.assertEqual(next(b for b in only_bad["blocks"] if b["block_id"] == mate["block_id"])["retry_stage"], "single_problem")
        self.assertTrue(any(mate["block_id"] in e["blocks"] for e in only_bad["envelopes"]))

    def test_g5_roster_record_key_sweep(self):
        reg, items, predicted = fixture()
        roster = pack(reg, items, predicted)
        bid = roster["blocks"][0]["block_id"]
        from joulewise.scored_packer import _digest
        for key in roster:
            broken = copy.deepcopy(roster)
            del broken[key]
            if key != "sha256":
                _digest(broken)
            with self.subTest(field="roster", key=key), self.assertRaises(PackingRefusal):
                requeue_overrun(reg, broken, bid, 2)
        broken = copy.deepcopy(roster)
        broken["unknown"] = 1
        _digest(broken)
        with self.assertRaises(PackingRefusal):
            requeue_overrun(reg, broken, bid, 2)
        for field, index in (("blocks", 0), ("envelopes", 0)):
            for key in roster[field][index]:
                broken = copy.deepcopy(roster)
                del broken[field][index][key]
                # Re-hash to test the record schema, not just the digest.
                _digest(broken)
                with self.subTest(field=field, key=key), self.assertRaises(PackingRefusal):
                    requeue_overrun(reg, broken, bid, 2)
            broken = copy.deepcopy(roster)
            broken[field][index]["unknown"] = 1
            _digest(broken)
            with self.assertRaises(PackingRefusal):
                requeue_overrun(reg, broken, bid, 2)

    def test_g5_invalid_predictions_and_requeue_inputs(self):
        reg, items, predicted = fixture()
        for value in (0, -1, True):
            bad = copy.deepcopy(predicted)
            bad["8B"][items[1][0]] = value
            with self.assertRaises(PackingRefusal):
                pack(reg, items, bad)
        with self.assertRaises(PackingRefusal):
            pack(reg, items, {(model, item): 1 for model in predicted for item in predicted[model]})
        roster = pack(reg, items, predicted)
        with self.assertRaises(PackingRefusal):
            requeue_overrun(reg, roster, "missing", 2)
        bid = roster["blocks"][0]["block_id"]
        unscheduled = copy.deepcopy(roster)
        source = next(e for e in unscheduled["envelopes"] if bid in e["blocks"])
        source["blocks"].remove(bid)
        from joulewise.scored_packer import _digest
        _digest(unscheduled)
        with self.assertRaises(PackingRefusal):
            requeue_overrun(reg, unscheduled, bid, 2)
        with self.assertRaises(PackingRefusal):
            requeue_overrun(reg, roster, bid, 0)
        first = requeue_overrun(reg, roster, bid, 2)
        block = next(b for b in first["blocks"] if b["block_id"] == bid)
        with self.assertRaises(PackingRefusal):
            requeue_overrun(reg, first, bid, {item: 0 for item in block["items"]})
        second = requeue_overrun(reg, first, bid, {item: 3 for item in block["items"]})
        child = next(b for b in second["blocks"] if b["parent_block_id"] == bid)
        with self.assertRaises(PackingRefusal):
            requeue_overrun(reg, second, child["block_id"], {child["items"][0]: 0})
