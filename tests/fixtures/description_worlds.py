"""Synthetic operational fixtures for builder tests under RL-192b."""

from tests import test_desc_looks_acceptance as frozen


class DescriptionWorld(frozen.World):
    loaded_keys = frozenset()

    def commit_stage1(self, test):
        rc, stdout, stderr, events = frozen.invoke(self, "stage1")
        test.assertEqual((rc, stdout, stderr), (0, b"", b""))
        test.assertFalse([path for event, path in events if event == "open"])
        document = frozen.read(self.stage)
        test.assertEqual(document["counts"]["n_legs"], len(self.good))
        if not self.inst:
            test.assertEqual(document["counts"]["n_local_dates"], len({row[-1] for row in self.specimens}))
        self.bind()

    def leg(self, kit, pos, v, day, ordinal, status):
        refs = super().leg(kit, pos, v, day, ordinal, status)
        record = self.records[refs["key"]][0]
        loaded = refs["key"] in self.loaded_keys
        if record["loaded_flag"] is not loaded:
            record["loaded_flag"] = loaded
            frozen.put(self.repo / refs["leg_record"], record)
        return refs
