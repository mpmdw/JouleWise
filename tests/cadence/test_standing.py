"""The standing queue's law (RL-172 (g), (a), (c), (f)), one test per condition, plus Sol's probes.

Pure: synthetic kits from the tree, synthetic queues and ledgers. Nothing here opens a run bundle."""
from __future__ import annotations

import copy
from datetime import datetime
import json
from pathlib import Path
import unittest

from joulewise.cadence import queue as q, standing as law

ROOT = Path(__file__).resolve().parents[2]
KIT04 = json.loads((ROOT / "docs/process/cadence/kits/cl-dev-04.v1.1.json").read_text())
KIT05 = json.loads((ROOT / "docs/process/cadence/kits/cl-dev-05.v1.1.json").read_text())
KIT01 = json.loads((ROOT / "docs/process/cadence/kits/cl-dev-01.json").read_text())
QUAL1 = json.loads((ROOT / "docs/process/cadence/kits/cl-qual-01.v1.1.json").read_text())
QUAL2 = json.loads((ROOT / "docs/process/cadence/kits/cl-qual-02.v1.1.json").read_text())
SHA = {"04": "4" * 64, "05": "5" * 64, "01": "1" * 64, "q1": "a" * 64, "q2": "b" * 64, "f2": "f" * 64}
KITS = {SHA["04"]: KIT04, SHA["05"]: KIT05, SHA["01"]: KIT01, SHA["q1"]: QUAL1, SHA["q2"]: QUAL2}
F2KIT = dict(copy.deepcopy(KIT01), campaign_id="f2-inst-01")
KITS[SHA["f2"]] = F2KIT


def at(text):
    return datetime.fromisoformat(text).timestamp()


NOW = at("2026-11-17T09:00:00-08:00")
L = [f"L{i:03d}" for i in range(1, 13)]


def entry(passed=True):
    return {"source": {"commit": "c" * 40, "path": "kits/x.json"}, "line1": "seat", "line2": "ci",
            "batch_window": "none", "hand_gate": {"passed": passed, "record": "pass" if passed else ""}}


def standing(**over):
    doc = {"schema": law.STANDING_SCHEMA, "standing_id": "cs-test", "queues": [{"path": "Q1.json", "role": "standing"}],
           "kits": {sha: entry() for sha in KITS}, "hand_gates": [], "withdrawn": [], "dispositions": [],
           "prior_spans": [
               {"plan_id": "cq-p1-a1", "campaign_id": "cl-dev-01", "block_id": "dev-01", "legs": 12, "mixed": False,
                "t0": "2026-11-15T01:00:00-08:00", "closed": "2026-11-15T06:00:00-08:00", "desk_final": "hand"},
               {"plan_id": "cq-p2-a1", "campaign_id": "cl-dev-02", "block_id": "dev-02", "legs": 6, "mixed": False,
                "t0": "2026-11-16T01:00:00-08:00", "closed": "2026-11-16T04:00:00-08:00", "desk_final": "auto"}],
           "sessions": [{"session_id": "slot-1", "kind": "r1-slot", "route": "docs/align/r1_arm_runbook.md"}],
           "fallback": [], "freeze2": None}
    doc.update(over)
    return law.validate_standing(doc)


def span(seq, sid, kit, legs, nb="2026-11-17", block=None):
    return {"seq": seq, "span_id": sid, "block_id": block or sid.rsplit("-", 1)[0], "attempt": 1, "not_before": nb,
            "kit": {"path": f"kits/{kit}.json", "sha256": SHA[kit]}, "legs": legs}


def view(spans, path="Q1.json", role="standing", commit=NOW - 3600, fallback=False, expires="2026-11-23T00:00:00-08:00"):
    doc = {"schema": q.SCHEMA, "queue_id": "cq-" + path.lower().replace(".json", "").replace("_", "-"),
           "expires_at": expires, "halt": None, "standing_notice": None, "spans": spans}
    return {"path": path, "role": role, "fallback": fallback, "doc": doc, "commit_epoch": commit,
            "kits": dict(KITS), "reasons": [], "closed_ids": set(), "withdrawn_ids": set(), "digest": "d" * 64}


def snap(views, st=None, *, now=NOW, runs=None, desk=None, issues=(), watcher=True, sessions=(), census=None,
         fallback_views=(), plan_worst=None, records=()):
    st = st or standing()
    runs = runs if runs is not None else law.build_runs(st, list(records), [])
    halts = law.apply_desk_finals(runs, desk or {})
    ran = {r.plan_id for r in runs}
    for v in [*views, *fallback_views]:
        v["closed_ids"] = ran
        v["withdrawn_ids"] = set(st["withdrawn"])
    stamp = {"schema": law.WATCHER_STAMP_SCHEMA, "watcher": "air-watch", "by": "lead",
             "observed_live_at": datetime.fromtimestamp(now - 3600, law.ZONE).isoformat()}
    return {"now": now, "standing": st, "input_reasons": [], "queues": list(views), "runs": runs, "desk_halts": halts,
            "vetoes": law.veto_reasons(list(issues), "mpmdw"),
            "watcher": law.watcher_reasons(stamp, now - 1800, now) if watcher else law.watcher_reasons(None, None, now),
            "sessions": law.session_reasons(st, list(sessions), set()), "census_epoch": census,
            "fallback": st["fallback"], "fallback_queues": list(fallback_views),
            "plan_worst": plan_worst or (lambda cand: 3 * 3600)}


def record(plan_id, kit, legs, t0, closed=None, status="CLOSED_OK", bundle="e" * 64):
    cls = law.kit_class(KITS[SHA[kit]])
    return {"plan_id": plan_id, "kind": "campaign" if cls["k2"] else "f2", "phase": cls["phase"],
            "block_id": plan_id.split("-s")[0][3:], "legs": legs, "mixed": cls["mixed"], "t0_epoch": t0,
            "closed_epoch": closed if closed is not None else t0 + 3 * 3600, "status": status,
            "bundle_sha256": bundle, "needs_print": True, "kit_sha256": SHA[kit]}


def codes(decision):
    return {r["code"] for r in decision.reasons} | {c for cs in decision.gates.values() for c in cs}


class SolProbes(unittest.TestCase):
    """The probes in sol-throughput/probe_detectors.py, re-aimed at the controller's arm path."""

    def test_future_not_before_does_not_arm(self):
        d = law.select(snap([view([span(1, "future-span", "04", L[:1], nb="2026-11-20")])]))
        self.assertEqual(d.action, "wait")
        self.assertIn("NOT_BEFORE", codes(d))
        eta = next(r["eta"] for r in d.reasons if r["code"] == "NOT_BEFORE")
        self.assertEqual(eta, at("2026-11-20T00:00:00-08:00"))

    def test_zero_leg_rows_is_a_stop(self):
        receipt = {"roster": ["L001"], "kit": {"sha256": SHA["04"], "frozen_commit": KIT04["frozen"]["commit"]},
                   "legs_planned": 1, "legs": [], "rc": 0}
        rs = law.desk_input_reasons(span=span(1, "s", "04", ["L001"]), kit_sha=SHA["04"], kit=KIT04, receipt=receipt,
                                    bundle_files=["span/meter.json", "span/result.json"], summaries={},
                                    plan={"legs": [{"leg_id": "L001"}]})
        self.assertIn("NO_LEG_ROWS", {r["code"] for r in rs})
        self.assertEqual(law.category(rs), "halt")

    def test_a_new_queue_does_not_erase_global_desk_debt(self):
        st = standing(prior_spans=[dict(standing()["prior_spans"][0], desk_final=None), standing()["prior_spans"][1]])
        d = law.select(snap([view([span(1, "dev-04-s01", "04", L[:6])], path="NEW.json")], st))
        self.assertEqual(d.action, "wait")
        self.assertIn("K2_DESK_DEBT", codes(d))

    def test_restore_unproven_is_not_healthy(self):
        rs = law.proof_reasons({"powermode": {"ok": True}}, "close")
        self.assertEqual(law.category(rs), "halt")
        self.assertIn("network_time: not observed", json.dumps(rs))


class Condition1Dates(unittest.TestCase):
    def test_clean_span_arms(self):
        d = law.select(snap([view([span(1, "dev-04-s01", "04", L[:6])])]))
        self.assertEqual(d.action, "arm", d.reasons)

    def test_missed_date_halts_for_the_lead_to_redate(self):
        d = law.select(snap([view([span(1, "dev-04-s01", "04", L[:6], nb="2026-11-16")])]))
        self.assertEqual(d.action, "halt")
        self.assertIn("DATE_MISSED", codes(d))

    def test_twelve_mixed_legs_a_date(self):
        rec = record("cq-dev-04-s01-a1", "04", L[:6], NOW - 4 * 3600, closed=NOW - 3600)
        recs = [rec, record("cq-dev-04-s02-a1", "04", L[6:], NOW - 3 * 3600, closed=NOW - 1000)]
        desk = {r["plan_id"]: {"schema": law.DESK_FINAL_SCHEMA, "plan_id": r["plan_id"], "bundle_sha256": "e" * 64,
                               "verdict": "FINAL", "hand_table": "agree", "reference_print": True, "by": "air",
                               "at": "x"} for r in recs}
        d = law.select(snap([view([span(1, "dev-05-s01", "05", L[:1])])], records=recs, desk=desk))
        self.assertEqual(d.action, "halt")
        self.assertIn("DATE_DEV_MIXED_CAP", codes(d))

    def test_twenty_four_development_legs_a_date(self):
        st = standing(prior_spans=standing()["prior_spans"] + [
            {"plan_id": f"cq-x{i}-a1", "campaign_id": "cl-dev-01", "block_id": "dev-0x", "legs": 12, "mixed": False,
             "t0": f"2026-11-17T0{i}:00:00-08:00", "closed": f"2026-11-17T0{i}:30:00-08:00", "desk_final": "y"}
            for i in (1, 2)])
        d = law.select(snap([view([span(1, "dev-04-s01", "04", L[:1])])], st))
        self.assertIn("DATE_DEV_CAP", codes(d))

    def test_qualification_waits_for_freeze2_then_keeps_off_development_dates(self):
        qv = view([span(1, "qual-01-s01", "q1", L[:6], block="qual-01")])
        self.assertIn("FREEZE2", codes(law.select(snap([qv]))))
        st = standing(freeze2="freeze 2 at abc")
        d = law.select(snap([view([span(1, "qual-01-s01", "q1", L[:6], nb="2026-11-16", block="qual-01")],
                                  commit=at("2026-11-16T08:00:00-08:00"))], st, now=at("2026-11-16T09:00:00-08:00")))
        self.assertIn("DATE_QUAL_DEV_OVERLAP", codes(d))   # dev-02 ran on the 16th
        planned = view([span(1, "dev-05-s01", "05", L[:6], nb="2026-11-17")], path="Q2.json")
        d = law.select(snap([view([span(1, "qual-01-s01", "q1", L[:6], block="qual-01")]), planned], st))
        self.assertIn("DATE_QUAL_DEV_OVERLAP", codes(d))   # dev-05 is planned for the 17th

    def test_qualification_blocks_use_two_dates(self):
        st = standing(freeze2="f2", prior_spans=[])
        day = "2026-11-19"
        now = at(f"{day}T15:00:00-08:00")
        recs = [record("cq-qual-01-s01-a1", "q1", L[:6], now - 9 * 3600, closed=now - 6 * 3600)]
        recs[0]["block_id"] = "qual-01"
        v = view([span(1, "qual-02-s01", "q2", L[:6], nb=day, block="qual-02")])
        d = law.select(snap([v], st, now=now, records=recs))
        self.assertIn("DATE_QUAL_SINGLE", codes(d))


class Condition2Debt(unittest.TestCase):
    def test_k_plus_two_counts_machine_order_across_queues(self):
        recs = [record("cq-dev-04-s01-a1", "04", L[:6], NOW - 5 * 3600, closed=NOW - 4 * 3600)]
        v2 = view([span(1, "dev-05-s01", "05", L[:1])], path="Q2.json")
        d = law.select(snap([v2], records=recs))   # campaign span 4: span 2 (prior, final) suffices
        self.assertEqual(d.action, "arm", d.reasons)
        recs.append(record("cq-dev-04-s02-a1", "04", L[6:], NOW - 3 * 3600, closed=NOW - 2 * 3600))
        d = law.select(snap([v2], records=recs))   # campaign span 5: span 3 (controller) is not final
        self.assertIn("K2_DESK_DEBT", codes(d))
        desk = {"cq-dev-04-s01-a1": {"schema": law.DESK_FINAL_SCHEMA, "plan_id": "cq-dev-04-s01-a1",
                                     "bundle_sha256": "e" * 64, "verdict": "FINAL", "hand_table": "not-sampled",
                                     "reference_print": False, "by": "air", "at": "x"}}
        self.assertIn("K2_DESK_DEBT", codes(law.select(snap([v2], records=recs, desk=desk))))  # v1.1: print owed
        desk["cq-dev-04-s01-a1"]["reference_print"] = True
        self.assertNotIn("K2_DESK_DEBT", codes(law.select(snap([v2], records=recs, desk=desk))))

    def test_desk_disagreement_or_contradiction_halts(self):
        rec = record("cq-dev-04-s01-a1", "04", L[:6], NOW - 5 * 3600, closed=NOW - 4 * 3600)
        base = {"schema": law.DESK_FINAL_SCHEMA, "plan_id": rec["plan_id"], "bundle_sha256": "e" * 64,
                "verdict": "FINAL", "hand_table": "disagree", "reference_print": True, "by": "air", "at": "x"}
        v = view([span(1, "dev-05-s01", "05", L[:1])])
        self.assertIn("DESK_DISAGREEMENT", codes(law.select(snap([v], records=[rec], desk={rec["plan_id"]: base}))))
        other = dict(base, hand_table="agree", bundle_sha256="9" * 64)
        self.assertIn("DESK_FINAL_CONTRADICTS", codes(law.select(snap([v], records=[rec], desk={rec["plan_id"]: other}))))


class Condition3Expiry(unittest.TestCase):
    def test_seven_days_from_the_commit_not_the_field(self):
        v = view([span(1, "dev-04-s01", "04", L[:6])], commit=NOW - 7 * 86400 - 1, expires="2026-12-31T00:00:00-08:00")
        self.assertIn("QUEUE_EXPIRED", codes(law.select(snap([v]))))

    def test_the_field_when_sooner(self):
        v = view([span(1, "dev-04-s01", "04", L[:6])], expires="2026-11-17T08:00:00-08:00")
        self.assertIn("QUEUE_EXPIRED", codes(law.select(snap([v]))))

    def test_a_commit_in_the_future_is_a_contradiction(self):
        v = view([span(1, "dev-04-s01", "04", L[:6])], commit=NOW + 3600)
        self.assertIn("QUEUE_COMMIT_IN_FUTURE", codes(law.select(snap([v]))))

    def test_append_only_history(self):
        a = {"queue_id": "cq-a", "spans": [{"seq": 1}]}
        self.assertEqual(law.append_only_problems([a, {"queue_id": "cq-a", "spans": [{"seq": 1}, {"seq": 2}]}]), [])
        self.assertTrue(law.append_only_problems([a, {"queue_id": "cq-a", "spans": [{"seq": 1, "x": 1}]}]))
        self.assertTrue(law.append_only_problems([a, {"queue_id": "cq-b", "spans": [{"seq": 1}]}]))


class Condition4Smoke(unittest.TestCase):
    def test_smoke_queue_holds_the_pilot_only(self):
        st = standing(kits={**{s: entry() for s in KITS}, SHA["05"]: entry(passed=False)})
        v = view([span(1, "dev-05-s01", "05", L[:3]), span(2, "dev-05-s02", "05", L[3:])], role="smoke")
        d = law.select(snap([v], st))
        self.assertIn("SMOKE_QUEUE_NOT_PILOT_ONLY", codes(d))
        self.assertIn("SMOKE_REMAINDER_STAGED", codes(d))

    def test_pilot_alone_arms_then_the_gate_holds(self):
        st = standing(kits={**{s: entry() for s in KITS}, SHA["05"]: entry(passed=False)})
        self.assertEqual(law.select(snap([view([span(1, "dev-05-s01", "05", L[:3])], role="smoke")], st)).action, "arm")
        v = view([span(1, "dev-05-s01", "05", L[:3])], role="standing")
        self.assertIn("SMOKE_REMAINDER_STAGED", codes(law.select(snap([v], st))))

    def test_named_hand_gate_holds_its_span(self):
        st = standing(hand_gates=[{"id": "rl163-l005", "holds": ["dev-04-s02"], "passed": False, "record": ""}])
        rec = record("cq-dev-04-s01-a1", "04", L[:6], NOW - 5 * 3600, closed=NOW - 4 * 3600)
        v = view([span(1, "dev-04-s01", "04", L[:6]), span(2, "dev-04-s02", "04", L[6:])])
        d = law.select(snap([v], st, records=[rec]))
        self.assertEqual(d.action, "wait")
        self.assertIn("HAND_GATE", codes(d))


class Condition5Proofs(unittest.TestCase):
    LINES = {k: {"ok": True} for k in law.PROOF_LINES}

    def test_every_line_needed(self):
        self.assertEqual(law.proof_reasons(self.LINES, "arm"), [])
        for line in law.PROOF_LINES:
            lines = dict(self.LINES)
            del lines[line]
            kinds = law.PROOF_LINES[line]
            for kind in kinds:
                self.assertEqual(law.category(law.proof_reasons(lines, kind)), "halt", (line, kind))

    def test_kernel_frequency_word_nonzero_and_network_time_on_fail(self):
        for line in ("kernel_frequency", "network_time", "powermode", "high_power_marker", "root_powermetrics"):
            lines = dict(self.LINES, **{line: {"ok": False, "detail": "x"}})
            self.assertEqual(law.category(law.proof_reasons(lines, "close")), "halt", line)

    def test_an_agent_is_a_wait(self):
        lines = dict(self.LINES, agents={"ok": False, "detail": "claude"},
                     measurement_mode={"ok": False, "agent_only": True, "detail": "FAIL agent process present"})
        self.assertEqual(law.category(law.proof_reasons(lines, "arm")), "wait")
        lines["measurement_mode"] = {"ok": False, "agent_only": False, "detail": "FAIL spotlight"}
        self.assertEqual(law.category(law.proof_reasons(lines, "arm")), "halt")

    def receipt(self, **over):
        r = {"rc": 0, "legs_planned": 2, "legs_finished": 2, "batch_windows": [],
             "span_result": {"chain_exit_code": 0, "chain_outcome": "COMPLETE", "fault": False, "outcome": "MEASURED_OK"},
             "steps": [{"name": "soak", "rc": 0}, {"name": "restore", "rc": 0}, {"name": "stop-meter", "rc": 0}],
             "feeds": {"meter": {"stop": {"proven_stopped": True}}},
             "soak_attempts": [{"attempt": 1, "refused": None}]}
        r.update(over)
        return r

    def test_receipt_command_result(self):
        self.assertEqual(law.receipt_command_reasons(self.receipt(), []), [])
        bad = self.receipt(steps=[{"name": "soak", "rc": 0}, {"name": "restore", "rc": 2}])
        self.assertIn("CLOSE_UNPROVEN", {r["code"] for r in law.receipt_command_reasons(bad, [])})
        refused = self.receipt(rc=3, legs_finished=1)
        self.assertIn("RECEIPT_NOT_CLEAN", {r["code"] for r in law.receipt_command_reasons(refused, [])})
        unstopped = self.receipt(feeds={"meter": {"stop": {"proven_stopped": False}}})
        self.assertIn("CLOSE_UNPROVEN", {r["code"] for r in law.receipt_command_reasons(unstopped, [])})

    def test_a_soak_retry_is_normal(self):
        retried = self.receipt(steps=[{"name": "soak", "rc": 5}, {"name": "soak.a2", "rc": 0},
                                      {"name": "restore", "rc": 0}],
                               soak_attempts=[{"attempt": 1, "refused": "unsettled"}, {"attempt": 2, "refused": None}])
        self.assertEqual(law.receipt_command_reasons(retried, []), [])
        three = self.receipt(soak_attempts=[{"attempt": i, "refused": "x"} for i in (1, 2)] + [{"attempt": 3, "refused": None}])
        self.assertIn("ROSTER_MISMATCH", {r["code"] for r in law.receipt_command_reasons(three, [])})
        pre_rl171 = self.receipt()
        del pre_rl171["soak_attempts"]
        self.assertEqual(law.receipt_command_reasons(pre_rl171, []), [])


class Condition6Gap(unittest.TestCase):
    def test_three_hundred_after_campaign_twelve_hundred_after_other(self):
        rec = record("cq-dev-04-s01-a1", "04", L[:6], NOW - 4 * 3600, closed=NOW - 100)
        v = view([span(1, "dev-04-s02", "04", L[6:])])
        d = law.select(snap([v], records=[rec]))
        self.assertIn("GAP", codes(d))
        self.assertEqual(law.select(snap([v], records=[rec], now=NOW + 200)).action, "arm")
        d = law.select(snap([v], records=[rec], now=NOW + 200, census=NOW))    # an unknown later close: 1,200 s
        self.assertIn("GAP", codes(d))


class Condition7Evidence(unittest.TestCase):
    def test_vetoes(self):
        v = [view([span(1, "dev-04-s01", "04", L[:6])])]
        owner = {"login": "mpmdw"}
        for issue in ({"number": 1, "title": "STOP everything", "labels": [{"name": "directive"}], "author": owner},
                      {"number": 2, "title": "x", "body": "NO dev-04 tonight", "labels": ["directive"], "author": owner},
                      {"number": 3, "title": "desk stop", "labels": [{"name": "cadence-stop"}], "author": owner}):
            self.assertEqual(law.select(snap(v, issues=[issue])).action, "halt", issue)
        ignored = [{"number": 4, "title": "STOP", "labels": ["directive"], "author": {"login": "someone"}},
                   {"number": 5, "title": "Note", "body": "fyi", "labels": ["directive"], "author": owner}]
        self.assertEqual(law.select(snap(v, issues=ignored)).action, "arm")

    def test_unreadable_issues_never_mean_no_veto(self):
        s = snap([view([span(1, "dev-04-s01", "04", L[:6])])])
        s["vetoes"] = law.veto_reasons(None, "mpmdw")
        self.assertEqual(law.select(s).action, "wait")

    def test_watcher_stamp(self):
        self.assertEqual(law.select(snap([view([span(1, "dev-04-s01", "04", L[:6])])], watcher=False)).action, "halt")
        stamp = {"schema": law.WATCHER_STAMP_SCHEMA, "watcher": "w", "by": "lead",
                 "observed_live_at": datetime.fromtimestamp(NOW - 25 * 3600, law.ZONE).isoformat()}
        self.assertEqual(law.watcher_reasons(stamp, NOW - 25 * 3600, NOW)[0]["code"], "WATCHER_STALE")
        stamp["observed_live_at"] = datetime.fromtimestamp(NOW, law.ZONE).isoformat()
        self.assertEqual(law.watcher_reasons(stamp, NOW - 3600, NOW)[0]["code"], "WATCHER_STAMP_INVALID")


class Condition8BadTerminal(unittest.TestCase):
    def test_a_bad_span_halts_until_the_lead_disposes_of_it(self):
        rec = record("cq-dev-04-s01-a1", "04", L[:6], NOW - 5 * 3600, closed=NOW - 4 * 3600, status="STOPPED")
        v = view([span(1, "dev-04-s01", "04", L[:6]), span(2, "dev-04-s02", "04", L[6:])])
        self.assertIn("SPAN_BAD_TERMINAL", codes(law.select(snap([v], records=[rec]))))
        st = standing(dispositions=[{"plan_id": "cq-dev-04-s01-a1", "record": "RL-x: refusal disposed"}])
        self.assertEqual(law.select(snap([v], st, records=[rec])).action, "arm")


class Condition9Fallback(unittest.TestCase):
    def test_only_f0_and_f2(self):
        with self.assertRaises(law.StandingError) as ctx:
            standing(fallback=[{"kind": "F3", "queues": [{"path": "x", "role": "standing"}]}])
        self.assertIn("FALLBACK_INVALID", str(ctx.exception))

    def test_f0_pages_when_nothing_counted_can_hold(self):
        st = standing(fallback=[{"kind": "F0", "standing_item": "RUN_STATE 999", "worst_case_s": 12180}])
        v = view([span(1, "dev-05-s01", "05", L[:6], nb="2026-11-18")])
        d = law.select(snap([v], st, now=at("2026-11-17T09:00:00-08:00")))
        self.assertEqual((d.action, d.reasons[0]["code"]), ("page", "FALLBACK_F0_DUE"))
        d = law.select(snap([v], st, now=at("2026-11-17T22:30:00-08:00")))    # due within 2 h 30 min
        self.assertEqual(d.action, "wait")

    def test_f0_spacing(self):
        st = standing(fallback=[{"kind": "F0", "standing_item": "RUN_STATE 999", "worst_case_s": 12180}])
        runs = law.build_runs(st, [], [{"run_id": "f0-1", "kind": "F0", "t0_epoch": NOW - 3600,
                                         "closed_epoch": NOW - 1300, "restore_ok": True}])
        d = law.select(snap([view([span(1, "dev-05-s01", "05", L[:6], nb="2026-11-18")])], st, runs=runs))
        self.assertIn("FALLBACK_SPACING", codes(d))

    def test_f2_arms_only_when_it_costs_no_counted_date(self):
        f2q = {"path": "F2.json", "role": "standing"}
        st = standing(fallback=[{"kind": "F2", "queues": [f2q]}])
        f2 = view([span(1, "f2-inst-01-p1", "f2", L[:3], nb="2026-11-17", block="f2-inst-01")], path="F2.json",
                  fallback=True)
        held = view([span(1, "dev-04-s02", "04", L[6:])])
        hg = standing(fallback=[{"kind": "F2", "queues": [f2q]}],
                      hand_gates=[{"id": "l005", "holds": ["dev-04-s02"], "passed": False, "record": ""}])
        d = law.select(snap([held], hg, fallback_views=[f2]))
        self.assertEqual(d.action, "arm-fallback")
        late = at("2026-11-17T22:00:00-08:00")
        d = law.select(snap([held], hg, fallback_views=[f2], now=late))
        self.assertIn("FALLBACK_DAY_COST", codes(d))
        del st

    def test_a_filler_kit_in_a_counted_queue_halts(self):
        d = law.select(snap([view([span(1, "f2-inst-01-p1", "f2", L[:3])])]))
        self.assertIn("KIT_ROLE_MISMATCH", codes(d))


class SectionF_Sessions(unittest.TestCase):
    def ready(self, sid="slot-1"):
        return {"schema": law.SESSION_READY_SCHEMA, "session_id": sid, "by": "lead", "ready_at": "2026-11-17T08:00:00-08:00"}

    def test_ready_session_cedes_and_nothing_lower_arms(self):
        d = law.select(snap([view([span(1, "dev-04-s01", "04", L[:6])])], sessions=[self.ready()]))
        self.assertEqual(d.action, "cede")
        self.assertIn("docs/align/r1_arm_runbook.md", d.reasons[0]["detail"])

    def test_done_session_releases_and_unknown_session_halts(self):
        st = standing()
        self.assertEqual(law.session_reasons(st, [self.ready()], {"slot-1"}), [])
        self.assertEqual(law.session_reasons(st, [self.ready("nope")], set())[0]["code"], "SESSION_INVALID")


class MissingInputs(unittest.TestCase):
    def test_no_standing_index_never_passes(self):
        s = snap([view([span(1, "dev-04-s01", "04", L[:6])])])
        s["standing"], s["input_reasons"] = None, [law.reason("STANDING_MISSING")]
        self.assertEqual(law.select(s).action, "halt")
        s["input_reasons"] = [law.reason("FETCH_FAILED")]
        self.assertEqual(law.select(s).action, "wait")

    def test_an_unreadable_kit_or_unknown_sha_halts(self):
        v = view([span(1, "dev-04-s01", "04", L[:6])])
        v["kits"] = {}
        self.assertIn("KIT_UNREADABLE", codes(law.select(snap([v]))))
        st = standing(kits={s: entry() for s in KITS if s != SHA["04"]})
        self.assertIn("KIT_UNKNOWN", codes(law.select(snap([view([span(1, "dev-04-s01", "04", L[:6])])], st))))


class Classification(unittest.TestCase):
    def test_classes_come_from_the_kit(self):
        self.assertEqual(law.kit_class(KIT04), {"phase": "development", "mixed": True, "k2": True, "dated": True})
        self.assertEqual(law.kit_class(KIT01)["mixed"], False)
        self.assertEqual(law.kit_class(QUAL1)["phase"], "qualification")
        self.assertEqual(law.kit_class({"campaign_id": "cl-hp-01"})["dated"], False)
        self.assertEqual(law.kit_class({"campaign_id": "cl-hp-01"})["k2"], True)
        with self.assertRaises(law.StandingError):
            law.kit_class({"campaign_id": "mystery-01"})

    def test_every_reason_is_named_and_categorized(self):
        for code, (cat, text) in law.REASONS.items():
            self.assertIn(cat, ("halt", "wait", "retry", "cede", "page"), code)
            self.assertTrue(text)


if __name__ == "__main__":
    unittest.main()
