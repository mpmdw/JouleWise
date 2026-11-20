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
            test.assertEqual(document["counts"]["n_local_dates"], len(self.qualified_dates()))
        self.bind()

    def leg(self, kit, pos, v, day, ordinal, status):
        refs = super().leg(kit, pos, v, day, ordinal, status)
        key = refs["key"]
        record, receipt, plan, _ = self.records[key]
        loaded = key in self.loaded_keys
        if record["loaded_flag"] is not loaded:
            record["loaded_flag"] = loaded
            frozen.put(self.repo / refs["leg_record"], record)
            self.records[key] = (record, receipt, plan, "not_qualified:loaded" if loaded else status)
            if status == "qualified":
                if loaded:
                    self.good.pop(key)
                else:
                    self.good[key] = (v, ordinal)
        return refs
