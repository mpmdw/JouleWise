"""Frozen acceptance cases. All facts and receipt and queue objects are invented."""

from copy import deepcopy
from datetime import date, datetime, timedelta
from hashlib import sha256
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from date_rules import Window, date_dispositions, date_places, midnight

NS = 10**9
DAY = date(2030, 11, 1)
TOMORROW = DAY + timedelta(days=1)


class FakeClock:
    def __init__(self, day=DAY):
        self.day = day

    def at(self, hour=0, minute=0, second=0):
        return midnight(self.day) + 3600 * hour + 60 * minute + second


def places(windows, starts=(), *, as_of, freeze_date=DAY):
    return date_places(windows, starts, freeze_date=freeze_date, as_of=as_of)


def snapshot(day=DAY, *, window=None, eligible_at=None, place=1, prior=()):
    clock = FakeClock(day)
    start = clock.at()
    before = midnight(day + timedelta(days=1))
    if window is None:
        window = Window("invented-W1", "W1", clock.at(1), clock.at(1, 2))
    if eligible_at is None:
        eligible_at = window.t0
    arms_at = clock.at(2)
    close_ns = arms_at * NS + 17
    main = "1" * 40
    kit = {"path": "invented/transfer.json", "sha256": "2" * 64}
    legs = [f"L{i:03}" for i in range(1, 7)]
    span = {"seq": place, "span_id": f"invented-span-{place:02}", "block_id": "invented-transfer",
            "kit": kit, "legs": legs, "attempt": 1, "not_before": day.isoformat()}
    queue = {"schema": "joulewise.cadence_queue.v1", "queue_id": "cq-invented",
             "expires_at": datetime.fromtimestamp(before, tz=local_zone()).isoformat(),
             "halt": None, "standing_notice": None, "spans": [span]}
    raw = json.dumps(queue).encode("ascii")
    authority = {"authorized_t0_date": day.isoformat(), "t0_not_before": arms_at,
                 "t0_not_before_ns": close_ns, "t0_before": before}
    predecessor = {"span_id": "invented-prev", "close_receipt": "invented-prev-close",
                   "close_ns": close_ns}
    issue = {"issue_id": "invented-issue", "day": day, "place": place, "span": deepcopy(span),
             "runner_pin": "3" * 40, "predecessor": predecessor.copy(),
             "queue_sha256": sha256(raw).hexdigest(), "freeze_sha256": "4" * 64,
             "registration_sha256": "5" * 64, "issued_at_ns": (arms_at - 60) * NS,
             "queue_committed_at_ns": (arms_at - 30) * NS, "t0_authority": authority.copy()}
    checked = (arms_at + 1) * NS
    arm = {"checked_at_ns": checked, "main_commit": main,
           "freeze": {"main_commit": main, "look_id": "lm-interim-01", "twin_agrees": "yes",
                      "coefficients_sha256": "4" * 64, "public_sha256": "6" * 64,
                      "published_at_ns": (start + 600) * NS},
           "registration": {"main_commit": main, "sha256": "5" * 64, "ledger_sha256": "5" * 64,
                            "registered_at_ns": (start + 900) * NS, "checked_at_ns": checked},
           "date_authority": {"checked_at_ns": checked, "day": day, "place": place,
                              "issue_ids": ("invented-issue",),
                              "window_attempts": (window.attempt_id,),
                              "observed_at_ns": eligible_at * NS},
           "predecessor": predecessor, "latest_close_ns": close_ns,
           "released_at_ns": None}
    receipt = {"schema": "joulewise.cadence_span_receipt.v1", "span_id": span["span_id"],
               "kit": {"sha256": kit["sha256"], "frozen_commit": issue["runner_pin"]},
               "roster": legs.copy(), "rc": 0,
               "started": {"epoch_s": arms_at + 2, "epoch_ns": (arms_at + 2) * NS},
               "t0_authority": authority.copy()}
    return {"windows": [window], "prior_starts": prior, "issue": issue, "arm": arm,
            "queue_bytes": raw, "receipt": receipt}


def local_zone():
    from zoneinfo import ZoneInfo
    return ZoneInfo("America/Los_Angeles")


def verify(case):
    from issue_gates import verify_transfer_start
    return verify_transfer_start(**case)


class DateAccountingTests(unittest.TestCase):
    def test_0005_refusal_cannot_be_served_by_0100_w1(self):
        clock = FakeClock()
        early, freeze, w1 = clock.at(0, 5), clock.at(0, 10), clock.at(1)
        windows = [Window("invented-W1", "W1", w1, clock.at(1, 2))]
        self.assertLess(early, freeze)
        self.assertEqual(places(windows, as_of=freeze), {})
        admitted_dates = places(windows, as_of=clock.at(2))
        self.assertEqual(admitted_dates, {DAY: (1, ("invented-W1",))})
        # A bare stamp cannot carry the child's authorization or prove that it took t0.
        with self.assertRaisesRegex(ValueError, "verified transfer start"):
            date_dispositions(admitted_dates, (early,), as_of=clock.at(2))
        with self.assertRaisesRegex(ValueError, "verified transfer start"):
            places(windows, (early,), as_of=clock.at(2))
        self.assertEqual(date_dispositions(admitted_dates, (), as_of=clock.at(2))[DAY]["status"], "pending")
        self.assertEqual(date_dispositions(admitted_dates, (), as_of=midnight(TOMORROW))[DAY]["status"], "missed")

    def test_actual_w1_c_t_starts_and_post_t0_abort_supply_distinct_dates(self):
        later = TOMORROW + timedelta(days=2)
        windows = [
            Window("forecast-without-t0", "W1", None),
            Window("ready-without-t0", "C", None),
            Window("pre-t0-refusal", "T", None, midnight(TOMORROW) + 1),
            Window("post-t0-abort", "W1", midnight(DAY) + 1, midnight(DAY) + 2),
            Window("actual-c", "C", midnight(TOMORROW) + 2),
            Window("actual-t", "T", midnight(later) + 1),
            Window("unrelated-r1", "R1", midnight(later) - 10),
            Window("unrelated-part-c", "Part C", midnight(later) - 11),
        ]
        self.assertEqual(places(windows, as_of=midnight(later)),
                         {DAY: (1, ("post-t0-abort",)), TOMORROW: (2, ("actual-c",))})
        self.assertEqual(places(windows, as_of=midnight(later) + 2)[later], (3, ("actual-t",)))

    def test_same_date_closed_windows_share_a_place(self):
        clock = FakeClock()
        w1 = Window("w1", "W1", clock.at(1), clock.at(2))
        c1 = Window("c1", "C", clock.at(3), clock.at(4))
        self.assertEqual(places([w1, c1], as_of=clock.at(5)), {DAY: (1, ("c1", "w1"))})

    def test_unserved_rollover_needs_close_and_deduplicates_close_date(self):
        boundary = midnight(TOMORROW)
        crossing = Window("cross", "C", boundary - 120, boundary + 90, True)
        other = Window("other", "T", boundary + 100, boundary + 110)
        self.assertEqual(places([crossing], as_of=boundary + 10), {})
        self.assertEqual(places([crossing, other], as_of=boundary + 120),
                         {TOMORROW: (1, ("cross", "other"))})

    def test_wholly_pre_freeze_date_is_excluded(self):
        w1 = Window("earlier", "W1", midnight(DAY) + 1, midnight(DAY) + 2)
        c1 = Window("later", "C", midnight(TOMORROW) + 1)
        self.assertEqual(places([w1, c1], freeze_date=TOMORROW, as_of=midnight(TOMORROW) + 2),
                         {TOMORROW: (1, ("later",))})

    def test_pre_freeze_w1_crossing_needs_fable(self):
        boundary = midnight(TOMORROW)
        w1 = Window("w1", "W1", boundary - 90, boundary + 90, True)
        with self.assertRaisesRegex(ValueError, "NEEDS_SPEC"):
            places([w1], freeze_date=TOMORROW, as_of=boundary + 100)

    def test_shared_start_date_with_only_one_crossing_needs_fable(self):
        boundary = midnight(TOMORROW)
        w1 = Window("w1", "W1", midnight(DAY) + 1, midnight(DAY) + 2)
        c1 = Window("c1", "C", boundary - 90, boundary + 90, True)
        with self.assertRaisesRegex(ValueError, "NEEDS_SPEC"):
            places([w1, c1], as_of=boundary + 100)

    def test_final_place_rolls_forward_with_one_miss_and_no_place_21(self):
        days = [DAY + timedelta(days=i) for i in range(22)]
        earlier = [Window(f"c{i}", "C", midnight(day) + 1) for i, day in enumerate(days[:19])]
        boundary = midnight(days[20])
        last = Window("final", "T", boundary - 120, boundary + 90, True)
        self.assertEqual(list(places([*earlier, last], as_of=boundary + 1)), days[:19])
        expiry = midnight(days[21])
        capped = places([*earlier, last], as_of=expiry)
        self.assertEqual(list(capped), [*days[:19], days[20]])
        self.assertEqual(date_dispositions(capped, (), as_of=expiry)[days[20]],
                         {"place": 20, "window_attempts": ("final",), "status": "missed"})
        case = snapshot(days[21], place=21)
        case["windows"][:0] = [*earlier, last]
        case["arm"]["freeze"]["published_at_ns"] = FakeClock().at(0, 10) * NS
        with self.assertRaisesRegex(ValueError, "capacity|place"):
            verify(case)


class IssueAuthorityTests(unittest.TestCase):
    def test_early_and_refused_child_records_spend_no_place(self):
        case = snapshot()
        clock = FakeClock()
        early = clock.at(0, 5)
        case["receipt"]["started"] = {"epoch_s": early, "epoch_ns": early * NS}
        with self.assertRaises(ValueError):
            verify(case)
        del case["receipt"]["started"]
        case["receipt"]["rc"] = 3
        with self.assertRaises(ValueError):
            verify(case)
        current = places(case["windows"], as_of=clock.at(3))
        self.assertEqual(date_dispositions(current, (), as_of=clock.at(3))[DAY]["status"], "pending")

    def test_both_public_freeze_routes(self):
        twin = snapshot()
        named = snapshot()
        freeze = named["arm"]["freeze"]
        freeze["twin_agrees"] = "no"
        freeze["naming"] = {"verified": True, "main_commit": freeze["main_commit"],
                            "look_id": freeze["look_id"], "ruling": "RL-invented",
                            "coefficients_sha256": freeze["coefficients_sha256"],
                            "public_sha256": freeze["public_sha256"],
                            "named_at_ns": FakeClock().at(0, 20) * NS}
        for case in (twin, named):
            with self.subTest(twin_agrees=case["arm"]["freeze"]["twin_agrees"]):
                start = verify(case)
                as_of = FakeClock().at(3)
                current = places(case["windows"], (start,), as_of=as_of)
                self.assertEqual(date_dispositions(current, (start,), as_of=as_of)[DAY]["status"], "served")
        for field, value in (("verified", False), ("main_commit", "9" * 40),
                             ("coefficients_sha256", "9" * 64), ("public_sha256", "9" * 64),
                             ("named_at_ns", FakeClock().at(3) * NS)):
            with self.subTest(field=field), self.assertRaises(ValueError):
                bad = deepcopy(named)
                bad["arm"]["freeze"]["naming"][field] = value
                verify(bad)

    def test_unknown_or_ineffective_public_freeze_refuses(self):
        for field, value in (("twin_agrees", "no"), ("twin_agrees", "not_evaluable"),
                             ("twin_agrees", "unknown"), ("main_commit", None),
                             ("coefficients_sha256", "9" * 64), ("published_at_ns", None)):
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                case = snapshot()
                case["arm"]["freeze"][field] = value
                verify(case)

    def test_fresh_registration_and_its_main_ledger_are_required(self):
        for field, value in (("checked_at_ns", FakeClock().at(1) * NS), ("main_commit", "9" * 40),
                             ("sha256", None), ("ledger_sha256", "9" * 64), ("registered_at_ns", None),
                             ("registered_at_ns", FakeClock().at(3) * NS)):
            with self.subTest(field=field), self.assertRaises(ValueError):
                case = snapshot()
                case["arm"]["registration"][field] = value
                verify(case)
        case = snapshot()
        del case["arm"]["registration"]
        with self.assertRaises(ValueError):
            verify(case)

    def test_fresh_date_authority_and_single_issue_identity_are_required(self):
        for field, value in (("checked_at_ns", None), ("day", TOMORROW), ("place", 2),
                             ("issue_ids", ()), ("issue_ids", ("invented-issue", "other")),
                             ("issue_ids", ("other",)), ("window_attempts", ("forecast",)),
                             ("observed_at_ns", None)):
            with self.subTest(field=field), self.assertRaises(ValueError):
                case = snapshot()
                case["arm"]["date_authority"][field] = value
                verify(case)
        case = snapshot()
        case["windows"] = [Window("invented-W1", "W1", None)]
        with self.assertRaises(ValueError):
            verify(case)

    def test_known_latest_predecessor_and_exact_close_are_required(self):
        for field, value in (("span_id", "another-span"), ("close_receipt", None), ("close_ns", None),
                             ("close_ns", FakeClock().at(2) * NS + 18)):
            with self.subTest(field=field), self.assertRaises(ValueError):
                case = snapshot()
                case["arm"]["predecessor"][field] = value
                verify(case)
        for close in (None, FakeClock().at(2, 1) * NS):
            with self.subTest(close=close), self.assertRaises(ValueError):
                case = snapshot()
                case["arm"]["latest_close_ns"] = close
                verify(case)

    def test_queue_digest_and_selected_span_binding(self):
        case = snapshot()
        case["queue_bytes"] += b" "
        with self.assertRaises(ValueError):
            verify(case)
        for field, value in (("not_before", TOMORROW.isoformat()), ("attempt", 2),
                             ("span_id", "other-span"), ("legs", ["L999"]), ("seq", 2)):
            with self.subTest(field=field), self.assertRaises(ValueError):
                case = snapshot()
                queue = json.loads(case["queue_bytes"])
                queue["spans"][0][field] = value
                case["queue_bytes"] = json.dumps(queue).encode("ascii")
                case["issue"]["queue_sha256"] = sha256(case["queue_bytes"]).hexdigest()
                verify(case)

    def test_original_child_bounds_and_started_stamp_are_required(self):
        for field, value in (("t0_not_before_ns", None), ("t0_not_before_ns", FakeClock().at(2) * NS),
                             ("t0_not_before", FakeClock().at(1)), ("t0_before", midnight(TOMORROW) + 1),
                             ("authorized_t0_date", TOMORROW.isoformat())):
            with self.subTest(field=field), self.assertRaises(ValueError):
                case = snapshot()
                case["receipt"]["t0_authority"][field] = value
                verify(case)
        case = snapshot()
        del case["receipt"]["started"]["epoch_ns"]
        with self.assertRaises(ValueError):
            verify(case)

    def test_all_lower_authorities_apply(self):
        for field in ("issued_at_ns", "queue_committed_at_ns", "released_at_ns"):
            with self.subTest(field=field), self.assertRaises(ValueError):
                case = snapshot()
                target = case["arm"] if field == "released_at_ns" else case["issue"]
                target[field] = FakeClock().at(2, 1) * NS
                verify(case)

    def test_receipt_must_match_the_issued_span_kit_pin_and_order(self):
        for field, value in (("span_id", "other-span"), ("roster", ["L001"]),
                             ("kit", {"sha256": "9" * 64, "frozen_commit": "3" * 40}),
                             ("kit", {"sha256": "2" * 64, "frozen_commit": "9" * 40})):
            with self.subTest(field=field), self.assertRaises(ValueError):
                case = snapshot()
                case["receipt"][field] = value
                verify(case)

    def test_child_exact_lower_is_inclusive(self):
        case = snapshot()
        lower = case["issue"]["t0_authority"]["t0_not_before_ns"]
        case["arm"]["checked_at_ns"] = lower
        case["arm"]["date_authority"]["checked_at_ns"] = lower
        case["arm"]["registration"]["checked_at_ns"] = lower
        case["receipt"]["started"] = {"epoch_s": lower // NS, "epoch_ns": lower - 1}
        with self.assertRaises(ValueError):
            verify(case)
        case["receipt"]["started"]["epoch_ns"] = lower
        verify(case)

    def test_last_nanosecond_serves_even_with_post_t0_abort_and_late_close(self):
        case = snapshot()
        upper = midnight(TOMORROW)
        case["receipt"]["started"] = {"epoch_s": upper - 1, "epoch_ns": upper * NS - 1}
        case["receipt"]["rc"] = 3
        case["receipt"]["ended"] = {"epoch_ns": (upper + 7) * NS}
        start = verify(case)
        current = places(case["windows"], (start,), as_of=upper + 8)
        self.assertEqual(date_dispositions(current, (start,), as_of=upper + 8)[DAY]["status"], "served")
        case["receipt"]["started"] = {"epoch_s": upper, "epoch_ns": upper * NS}
        with self.assertRaises(ValueError):
            verify(case)

    def test_duplicates_refuse_in_verifier_and_both_accounting_readers(self):
        case = snapshot()
        start = verify(case)
        case["prior_starts"] = (start,)
        with self.assertRaisesRegex(ValueError, "capacity|served|start"):
            verify(case)
        as_of = FakeClock().at(3)
        with self.assertRaisesRegex(ValueError, "multiple transfer starts"):
            places(case["windows"], (start, start), as_of=as_of)
        current = places(case["windows"], (start,), as_of=as_of)
        with self.assertRaisesRegex(ValueError, "multiple transfer starts"):
            date_dispositions(current, (start, start), as_of=as_of)

    def test_miss_does_not_reseed_next_place(self):
        case = snapshot(TOMORROW, place=2)
        case["windows"].insert(0, Window("earlier", "C", FakeClock().at(1)))
        case["arm"]["freeze"]["published_at_ns"] = FakeClock().at(0, 10) * NS
        start = verify(case)
        as_of = FakeClock(TOMORROW).at(3)
        current = places(case["windows"], (start,), as_of=as_of)
        self.assertEqual(date_dispositions(current, (start,), as_of=as_of),
                         {DAY: {"place": 1, "window_attempts": ("earlier",), "status": "missed"},
                          TOMORROW: {"place": 2, "window_attempts": ("invented-W1",), "status": "served"}})

    def test_final_place_can_take_t0_on_its_verified_close_date(self):
        days = [DAY + timedelta(days=i) for i in range(21)]
        boundary = midnight(days[20])
        final = Window("final", "T", boundary - 120, boundary + 90, True)
        case = snapshot(days[20], window=final, eligible_at=final.close, place=20)
        case["windows"][:0] = [Window(f"c{i}", "C", midnight(day) + 1)
                               for i, day in enumerate(days[:19])]
        case["arm"]["freeze"]["published_at_ns"] = FakeClock().at(0, 10) * NS
        start = verify(case)
        as_of = FakeClock(days[20]).at(3)
        current = places(case["windows"], (start,), as_of=as_of)
        self.assertEqual(date_dispositions(current, (start,), as_of=as_of)[days[20]],
                         {"place": 20, "window_attempts": ("final",), "status": "served"})

    def test_validated_start_on_original_date_prevents_rollover(self):
        case = snapshot()
        case["windows"].append(Window("cross", "C", midnight(TOMORROW) - 120,
                                      midnight(TOMORROW) + 90, True))
        start = verify(case)
        self.assertEqual(places(case["windows"], (start,), as_of=midnight(TOMORROW) + 91),
                         {DAY: (1, ("cross", "invented-W1"))})


if __name__ == "__main__":
    unittest.main()
