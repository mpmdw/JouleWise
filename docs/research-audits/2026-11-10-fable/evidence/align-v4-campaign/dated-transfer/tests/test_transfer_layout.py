"""Blind transfer regression fixtures. No campaign results are read."""
from copy import deepcopy
from datetime import date, timedelta
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build_kits import HERE, pair_layout, registered_seeds, validate_layout
from date_rules import (CountedClose, Window, arm_bounds, counted_batch_hold, date_places,
                        lower_priority_fits, midnight, permits_t0)
from validate_look import HASHES, LOOK_ID, load, validate_draft, validate_public


class LayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kits = [load(path) for path in sorted((HERE / "kits").glob("cl-transfer-*.json"))]

    def test_one_span_has_both_orders_per_ratio(self):
        validate_layout(self.kits, *registered_seeds())
        self.assertEqual({pair_layout(kit) for kit in self.kits},
                         {(3724, True), (3724, False), (3151, True), (3151, False)})
        # p1 is a local identifier, shared by both ratios even when span position is constant.
        self.assertEqual({leg["pair"] for kit in self.kits for leg in kit["legs"] if leg["leg_type"] == "L"}, {"p1"})

    def test_qualification_p1_alias_cannot_substitute_for_transfer_layout(self):
        qual = load(HERE.parent / "item-drafts-1118" / "kits" / "cl-qual-01.v1.1.json")
        with self.assertRaisesRegex(ValueError, "one six-leg span"):
            pair_layout(qual)

    def test_multispan_family_cannot_bypass_the_single_span_rule(self):
        kits = deepcopy(self.kits)
        kits[0]["seed_law"]["spans"] = 2
        with self.assertRaisesRegex(ValueError, "one six-leg span"):
            validate_layout(kits)

    def test_missing_order_and_rotated_ordinals_are_refused(self):
        kits = deepcopy(self.kits)
        for kit in kits:
            cap, long_first = pair_layout(kit)
            if cap == 3724 and not long_first:
                pair = [leg for leg in kit["legs"] if leg["leg_type"] == "L"]
                pair[0]["decode_tokens"], pair[1]["decode_tokens"] = pair[1]["decode_tokens"], pair[0]["decode_tokens"]
        with self.assertRaisesRegex(ValueError, "both orders"):
            validate_layout(kits)
        shifted = deepcopy(self.kits)
        shifted[0], shifted[1] = shifted[1], shifted[0]
        with self.assertRaisesRegex(ValueError, "original date place"):
            validate_layout(shifted)

    def test_seed_collisions_and_split_pairs_are_refused(self):
        duplicated = deepcopy(self.kits)
        duplicated[-1]["legs"][0]["seed"] = duplicated[0]["legs"][0]["seed"]
        with self.assertRaisesRegex(ValueError, "fresh"):
            validate_layout(duplicated)
        split = deepcopy(self.kits[0])
        pair_end = max(i for i, leg in enumerate(split["legs"]) if leg["leg_type"] == "L")
        gap_index = pair_end + 1 if pair_end < 5 else pair_end - 2
        split["legs"][pair_end], split["legs"][gap_index] = split["legs"][gap_index], split["legs"][pair_end]
        with self.assertRaisesRegex(ValueError, "adjacent"):
            pair_layout(split)


class DateTests(unittest.TestCase):
    day = date(2030, 11, 1)
    start = midnight(day)
    next_day = day + timedelta(days=1)
    boundary = midnight(next_day)

    def test_two_windows_share_date_and_only_actual_t0_counts(self):
        windows = [
            Window("W1-abort-after-start", "W1", self.start + 1, self.start + 60),
            Window("C-same-date", "C", self.start + 70),
            Window("T-no-start", "T", None),
            Window("R1-unrelated", "R1", self.boundary + 1),
            Window("part-c-unrelated", "Part C", self.boundary + 2),
            Window("T-forecast", "T", self.boundary + 60),
        ]
        self.assertEqual(date_places(windows, (), freeze_date=self.day, as_of=self.boundary + 10),
                         {self.day: (1, ("C-same-date", "W1-abort-after-start"))})

    def test_midnight_substitution_and_close_date_deduplication(self):
        cross = Window("C-cross", "C", self.boundary - 120, self.boundary + 90, True)
        second = Window("T-close-date", "T", self.boundary + 100)
        self.assertEqual(date_places([cross], (), freeze_date=self.day, as_of=self.boundary + 20), {})
        self.assertEqual(date_places([cross, second], (), freeze_date=self.day, as_of=self.boundary + 200),
                         {self.next_day: (1, ("C-cross", "T-close-date"))})
        self.assertEqual(date_places([cross, second], [self.boundary - 500],
                                     freeze_date=self.day, as_of=self.boundary + 200),
                         {self.day: (1, ("C-cross",)), self.next_day: (2, ("T-close-date",))})

    def test_final_window_rollover_holds_for_ruling(self):
        cross = Window("T-final", "T", self.boundary - 120, self.boundary + 90, True)
        with self.assertRaisesRegex(ValueError, "NEEDS_SPEC"):
            date_places([cross], (), freeze_date=self.day, as_of=self.boundary + 200, final_window_known=True)

    def test_cap_and_missed_dates_keep_original_ordinals(self):
        days = [self.day + timedelta(days=i) for i in range(25)]
        windows = [Window(f"C-{i}", "C", midnight(day) + 99) for i, day in enumerate(days)]
        places = date_places(windows, (midnight(days[3]) + 100,), freeze_date=days[2],
                             as_of=midnight(days[-1]) + 100)
        self.assertEqual(list(places), days[2:22])
        self.assertEqual(places[days[2]], (1, ("C-2",)))
        self.assertEqual(places[days[3]], (2, ("C-3",)))
        self.assertEqual(places[days[21]], (20, ("C-21",)))

    def test_expired_date_dst_and_both_bounds(self):
        early = self.start + 70
        bounds = arm_bounds(self.day, eligible_at=self.start + 10, freeze_at=self.start + 20,
                            registered_at=self.start + 30, close_proven_at=early)
        self.assertFalse(permits_t0(early - 1, bounds))
        self.assertTrue(permits_t0(early, bounds))
        self.assertTrue(permits_t0(self.boundary - 0.01, bounds))
        self.assertFalse(permits_t0(self.boundary, bounds))
        with self.assertRaisesRegex(ValueError, "no authorized t0"):
            arm_bounds(self.day, eligible_at=self.start, freeze_at=self.start,
                       registered_at=self.start, close_proven_at=self.boundary)
        fall = date(2030, 11, 3)
        self.assertEqual(midnight(fall + timedelta(days=1)) - midnight(fall), 25 * 3600)

    def test_lower_priority_fit_includes_second_t0_and_allows_its_close_next_date(self):
        pending = [(self.boundary - 300, self.boundary, 200),
                   (self.boundary - 300, self.boundary, 200)]
        self.assertTrue(lower_priority_fits(self.boundary - 400, 199, pending))
        self.assertFalse(lower_priority_fits(self.boundary - 400, 200, pending))

    def test_batch_hold_counts_two_distinct_contaminated_spans(self):
        first = CountedClose("a", "CONTAMINATED_REDOS", 5, 10, 15)
        second = CountedClose("b", "CONTAMINATED_REDOS", 20, 25, 30)
        outside = CountedClose("c", "CONTAMINATED_REDOS", 20, 35, 30)
        self.assertFalse(counted_batch_hold([first, first, outside], soak_end=1, expected_close=10, predicted_batch=7))
        self.assertTrue(counted_batch_hold([first, second], soak_end=1, expected_close=10, predicted_batch=7))
        self.assertFalse(counted_batch_hold([first, second], soak_end=1, expected_close=10, predicted_batch=12))


class LookTests(unittest.TestCase):
    def test_draft_and_ledger(self):
        manifest = HERE / "looks" / f"{LOOK_ID}.json"
        doc = load(manifest)
        validate_draft(doc, manifest)
        doc["estimate"]["interval"]["series"] = "absolute_daily_error"
        with self.assertRaisesRegex(ValueError, "signed daily interval"):
            validate_draft(doc, manifest)

    def test_only_two_words_and_three_hashes(self):
        fixture = {"transfer_interval": "estimated", "stage2_error": "no", **dict.fromkeys(HASHES, "0" * 64)}
        validate_public(fixture)
        validate_public({**fixture, "transfer_interval": "not_evaluable"})
        for update in ({"transfer_interval": 0.5}, {"transfer_interval": "yes"}, {"stage2_error": "yes"},
                       {"freeze2_sha256": "0" * 64 + "\n"}, {"interval": [0, 0.1]}, {"transfer_holds": "yes"}):
            with self.subTest(update=update), self.assertRaises(ValueError):
                validate_public({**fixture, **update})
        self.assertEqual(json.loads(json.dumps(fixture)), fixture)


if __name__ == "__main__":
    unittest.main()
