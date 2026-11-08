"""Mutation checks for the independent checker, using no model/runtime imports."""
from copy import deepcopy
import json
import unittest

from check_manifest import (CANONICAL_SHA256, FILE_SHA256, anchor_evidence,
                            check, differences, encode_manifest, sha,
                            slot_comparison, turn_zero)
from derive_slots import PAIRS, compact, derive, episode_seed


class SeedCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.slots = derive()
        cls.manifest = encode_manifest(cls.slots)

    def test_pinned_hashes_and_precomparison_snapshot(self):
        raw, receipt = check()
        self.assertEqual(receipt["verdict"], "MATCH")
        self.assertTrue(all(receipt["checks"].values()))
        self.assertEqual(sha(raw), FILE_SHA256)
        self.assertEqual(sha(compact(json.loads(raw))), CANONICAL_SHA256)
        self.assertEqual(receipt["slot_count"], 260)

    def test_changed_identity_axes_are_all_reported(self):
        # Each mutation independently changes one of the seven requested axes.
        axes = {"pair": "other_pair", "condition": "sabotage", "seed_index": 90,
                "episode_seed": 0, "model_id": "other_model", "pool": "anchor",
                "ordinal": 99}
        for key, wrong in axes.items():
            with self.subTest(key=key):
                changed = deepcopy(self.manifest)
                changed["windows"][1]["members"][5][key] = wrong
                self.assertTrue(slot_comparison(self.slots, changed))
                self.assertTrue(differences(self.manifest, changed))

    def test_every_changed_leaf_is_reported_and_w1_role_is_checked(self):
        changed = deepcopy(self.manifest)
        row = changed["windows"][0]["members"][0]
        for key in ("condition", "model_id", "role", "pair"):
            row[key] = "changed"
        self.assertEqual(len(slot_comparison(self.slots, changed)), 4)
        self.assertEqual(len(differences(self.manifest, changed)), 4)

    def test_window_and_member_order_missing_and_extra_records(self):
        for operation in ("missing_window", "extra_window", "window_order",
                          "missing_member", "extra_member", "member_order"):
            with self.subTest(operation=operation):
                changed = deepcopy(self.manifest)
                windows = changed["windows"]
                members = windows[1]["members"]
                if operation == "missing_window":
                    windows.pop()
                elif operation == "extra_window":
                    windows.append(deepcopy(windows[-1]))
                elif operation == "window_order":
                    windows[1], windows[2] = windows[2], windows[1]
                elif operation == "missing_member":
                    members.pop()
                elif operation == "extra_member":
                    members.append(deepcopy(members[-1]))
                else:
                    members[5], members[6] = members[6], members[5]
                self.assertTrue(slot_comparison(self.slots, changed))
                self.assertTrue(differences(self.manifest, changed))

    def test_non_slot_metadata_and_turn_seed_are_not_ignored(self):
        for where in ("turn", "mapping", "extra_role", "midpoint", "ceiling"):
            with self.subTest(where=where):
                changed = deepcopy(self.manifest)
                if where == "turn":
                    changed["windows"][1]["members"][5]["turn_seed_0"] += 1
                elif where == "mapping":
                    changed["d_mapping"] = "separate"
                elif where == "extra_role":
                    changed["windows"][1]["members"][0]["role"] = "wrong"
                elif where == "midpoint":
                    changed["windows"][1]["midpoint_after_ordinal"] = 9
                else:
                    changed["sentinel"]["escalated_ceiling_s"] = 59520
                self.assertTrue(differences(self.manifest, changed))

    def test_seed_law_known_kit_vectors(self):
        self.assertEqual(episode_seed("qwen3.8-27b", PAIRS[0], 1), 11160969177166136631)
        self.assertEqual(episode_seed("qwen3.8-27b", PAIRS[1], 2), 16052326787332467059)
        self.assertEqual(episode_seed("qwen3-30b-a3b", PAIRS[0], 16), 7655467588542005630)
        self.assertEqual(turn_zero(11160969177166136631), 13933079069872451601)

    def test_disjoint_complete_seed_streams_and_counts(self):
        for pair in PAIRS:
            for cohort, wanted in (("C", list(range(2, 66))), ("T", list(range(66, 90)))):
                rows = [r for w in self.slots if w["window_id"].startswith(cohort)
                        for r in w["slots"] if r["task_pair"] == pair
                        and r["role"].startswith("held_out_")]
                self.assertEqual([r["seed_index"] for r in rows], wanted)
                self.assertEqual(sum(r["condition"] == "benign" for r in rows),
                                 56 if cohort == "C" else 21)
        for w in self.slots[1:]:
            rows = w["slots"]
            self.assertEqual(len(rows), 22)
            self.assertEqual([r["ordinal"] for r in rows[5:21]
                              if r["condition"] == "sabotage"], [9, 18])
            self.assertEqual(rows[4]["expected_episode_seed"], rows[21]["expected_episode_seed"])

    def test_original_anchors_are_exact_repository_bytes(self):
        self.assertEqual(len(anchor_evidence()), 4)
        self.assertTrue(all(row["byte_identical"] for row in anchor_evidence()))


if __name__ == "__main__":
    unittest.main()
