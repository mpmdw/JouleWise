"""Independent, synthetic stage-1 boundary cases for RL-192b and the provisional lead order."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import test_desc_looks_acceptance as frozen


# The receipt remains authentic and closed. A bad/missing receipt is still a preflight refusal.
# In this projection power_mode belongs to the receipt. "short" is the realized decode
# count, and cap_not_reached is the stop flag. Ordinary planner wall overrun is not a veto.
# Each expected list is literal and independent of the order of fixture assignments below.
VECTORS = (
    ("receipt_g0_load", ("wrong_mode", "unreleased", "loaded")),
    ("completion_through_stop", ("incomplete", "unreleased", "short_hold", "loaded", "short", "cap_not_reached")),
    ("g0_quiet_load", ("unreleased", "short_hold", "loaded")),
    ("quiet_load_stop", ("short_hold", "loaded", "cap_not_reached")),
    ("load_count_stop", ("loaded", "short", "cap_not_reached")),
    ("count_stop_without_load", ("short", "cap_not_reached")),
)


def world_with_failures(base, look, failed, *, pairs=False):
    """Set only ordinal zero's operational facts, before the frozen Book signs the close."""
    class Planted(frozen.World):
        def leg(self, kit, pos, v, day, ordinal, status):
            refs = super().leg(kit, pos, v, day, ordinal, status)
            if ordinal == 0:
                op, receipt, plan, _ = self.records[refs["key"]]
                op["decode_cap_reached"] = "cap_not_reached" not in failed
                op["decode_tokens"] = plan["decode_tokens"] - int("short" in failed)
                op["loaded_flag"] = "loaded" in failed
                if "short_hold" in failed:
                    op["quiet_spans_ns"] = [[0, 599_999_999_999]]
                if "unreleased" in failed:
                    op["g0_outcome"] = "timeout"
                if "incomplete" in failed:
                    op["leg_status"] = "incomplete"
                if "wrong_mode" in failed:
                    receipt["power_mode"] = "High Power"
                frozen.put(self.repo / refs["receipt"], receipt)
                frozen.put(self.repo / refs["leg_record"], op)
            return refs

    return Planted(base, look, "same_work" if pairs else None)


def first_key(look):
    return "f2-inst-01/L001" if look == frozen.IDS[0] else "f2-stab-01/L001"


class RL192b(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name).resolve()

    def stage(self, world, *, due=True):
        rc, stdout, stderr, events = frozen.invoke(world, "stage1")
        self.assertEqual((rc, stdout), (0 if due else 2, b""), stderr)
        self.assertFalse([path for event, path in events if event == "open"])
        self.assertEqual(world.stage.exists(), due)
        if due:
            return frozen.read(world.stage)

    def no_prints(self, world, key):
        # Use the same authenticated scoring entry points as the frozen v2.2 tests.
        # Observe all reads of this invented copy, including opening a loaded hold's support.
        world.bind()
        reader = frozen.executor()
        snapshot = reader.Snapshot(world.repo, world.look, "stage2")
        doc, qualified = reader.census(snapshot)
        snapshot.check_stage1(doc)
        sources = reader.verify_gates(snapshot, qualified)
        seen = set()
        original = Path.open
        def observe(path, *args, **kwargs):
            if path.is_relative_to(world.copy):
                seen.add(path.parent.relative_to(world.copy).as_posix())
            return original(path, *args, **kwargs)
        with patch.object(Path, "open", observe):
            prints = reader.score(snapshot, sources, qualified, lambda: None)
        # Derive the positive controls from the planted roster, never the executor's census.
        expected = {row["key"] for row in world.rows if "receipt" in row
                    and row["key"] != key and world.records[row["key"]][-1] == "qualified"}
        self.assertTrue(expected)
        self.assertEqual(set(qualified), expected)
        self.assertEqual(set(sources), expected)
        self.assertEqual(seen, expected)
        per_leg = ("hold", "turn", "gain", "edges") if world.inst else ("hold", "turn")
        for name in per_leg:
            with self.subTest(output=name):
                self.assertEqual(set(prints[name]), expected)
        if not world.inst:
            contexts = set().union(*(rows.keys() for rows in prints["context"].values()))
            self.assertEqual(contexts, expected)


def loaded_alone(test, look):
    world = frozen.World(test.base / "loaded", look)
    key = first_key(look)
    doc = test.stage(world)
    row = doc["positions"][key]
    test.assertEqual(row["disposition"], "not_qualified:loaded")
    test.assertIs(row["loaded_flag"], True)
    test.assertEqual(row["receipt"], world.rows[0]["receipt"])
    test.assertEqual(doc["counts"]["n_legs"], dict(zip(frozen.IDS, (2, 16, 17)))[look])
    test.assertEqual(doc["by_kit"][key.split("/")[0]]["not_qualified:loaded"], 1)
    test.no_prints(world, key)


def singleton_date(test, look):
    # Day 13 was a singleton. Exchange its day with ordinal zero's shared day:
    # the only source of the fourteenth date is now the leg on which load is toggled.
    rows = frozen.layout(look)
    layout = [(*row[:3], 13 if i == 0 else 0 if row[3] == 13 else row[3])
              for i, row in enumerate(rows)]
    with patch.object(frozen, "layout", return_value=layout):
        for loaded in (False, True):
            with test.subTest(loaded=loaded):
                failures = ("loaded",) if loaded else ()
                world = world_with_failures(test.base / str(loaded), look, failures)
                due = not loaded or look == frozen.IDS[2]
                doc = test.stage(world, due=due)
                if due:
                    test.assertEqual(doc["counts"]["n_local_dates"], 13 if loaded else 14)
                    test.assertEqual(doc["counts"]["n_legs"], len(rows) - int(loaded))


def position_pair(test, look):
    for loaded in (False, True):
        with test.subTest(loaded=loaded):
            failures = ("loaded",) if loaded else ()
            world = world_with_failures(test.base / str(loaded), look, failures, pairs=True)
            doc = test.stage(world)
            table = {r["kit_id"] + "/" + r["leg_id"]: r for r in doc["token_table"]}
            row, peer = table[first_key(look)], table["f2-stab-02/L001"]
            test.assertEqual(row["disposition"], "not_qualified:loaded" if loaded else "qualified")
            test.assertIs(row["loaded_flag"], loaded)
            test.assertEqual(peer["disposition"], "qualified")
            test.assertEqual(row["missing_count_reason"], "loaded" if loaded else None)
            for field in ("realised_prefill_tokens", "realised_decode_tokens"):
                test.assertIsInstance(row[field], int)
                test.assertEqual(row[field], peer[field])
            test.assertEqual(doc["counts"], {"n_legs": 23 if loaded else 24, "n_local_dates": 14})
            test.assertEqual(doc["paper_wording"], "the same cell of work" if loaded else "the same work")


def multi_failure(test, look, reasons):
    world = world_with_failures(test.base / "multi", look, set(reasons))
    key = first_key(look)
    doc = test.stage(world)
    row = doc["positions"][key]
    # Separate subtests keep an absent reasons array visible even when the label is wrong.
    with test.subTest(check="first_in_lifecycle"):
        test.assertEqual(row["disposition"], "not_qualified:" + reasons[0])
    with test.subTest(check="full_ordered_reasons"):
        test.assertEqual(row.get("reasons"), list(reasons))
    with test.subTest(check="retained_receipt"):
        test.assertEqual(row["receipt"], world.rows[0]["receipt"])
    with test.subTest(check="excluded_once"):
        test.assertEqual(doc["counts"]["n_legs"], dict(zip(frozen.IDS, (2, 16, 17)))[look])
    with test.subTest(check="zero_prints"):
        test.no_prints(world, key)


def register(name, fn, *args):
    def case(self):
        fn(self, *args)
    case.__name__ = "test_" + name
    assert not hasattr(RL192b, case.__name__)
    setattr(RL192b, case.__name__, case)


for look in frozen.IDS:
    prefix = look.replace("-", "_")
    register(prefix + "_RL192b_loaded_alone_zero_prints", loaded_alone, look)
    if look != frozen.IDS[0]:
        register(prefix + "_RL192b_loaded_singleton_date", singleton_date, look)
        register(prefix + "_RL192b_loaded_position_pair", position_pair, look)
    for label, reasons in VECTORS:
        register(prefix + "_PROVISIONAL_" + label, multi_failure, look, reasons)


if __name__ == "__main__":
    unittest.main()
