"""Synthetic operational fixtures for builder tests under RL-192b."""

from tests import test_desc_looks_acceptance as frozen


class DescriptionWorld(frozen.World):
    loaded_keys = frozenset()

    def leg(self, kit, pos, v, day, ordinal, status):
        refs = super().leg(kit, pos, v, day, ordinal, status)
        record = self.records[refs["key"]][0]
        loaded = refs["key"] in self.loaded_keys
        if record["loaded_flag"] is not loaded:
            record["loaded_flag"] = loaded
            frozen.put(self.repo / refs["leg_record"], record)
        return refs
