"""The standing queue's law (RL-172 (g), (a), (c), (f)): one test per condition, Sol's probes, and a regression for
each gate finding on the law's side (Sol 2026-11-15 #800 gate; Mythos #800 gate). Pure: synthetic kits from the tree,
synthetic queues, ledgers and verdicts. Nothing here opens a run bundle."""
from __future__ import annotations

import copy
from datetime import datetime
import json
from pathlib import Path
import unittest

from joulewise.cadence import desk_final, queue as q, standing as law

ROOT = Path(__file__).resolve().parents[2]


def kit(name):
    return json.loads((ROOT / f"docs/process/cadence/kits/{name}.json").read_text())


KIT04, KIT05, KIT01 = kit("cl-dev-04.v1.1"), kit("cl-dev-05.v1.1"), kit("cl-dev-01")
QUAL1, QUAL2 = kit("cl-qual-01.v1.1"), kit("cl-qual-02.v1.1")
F2KIT = dict(copy.deepcopy(KIT01), campaign_id="f2-inst-01")
SHA = {"04": "4" * 64, "05": "5" * 64, "01": "1" * 64, "q1": "a" * 64, "q2": "b" * 64, "f2": "f" * 64}
KITS = {SHA["04"]: KIT04, SHA["05"]: KIT05, SHA["01"]: KIT01, SHA["q1"]: QUAL1, SHA["q2"]: QUAL2, SHA["f2"]: F2KIT}
BY_KEY = {"04": KIT04, "05": KIT05, "01": KIT01, "q1": QUAL1, "q2": QUAL2, "f2": F2KIT}
WATCHER = "com.joulewise.air-watch"
GATE_NAMES = {law.CLASS_A: "class A smoke hand-read", "L005": "L005 consumer gate", "L002": "L002 consumer gate"}


def at(text):
    return datetime.fromisoformat(text).timestamp()


NOW = at("2026-11-17T09:00:00-08:00")
L = [f"L{i:03d}" for i in range(1, 13)]


def entry():
    return {"source": {"commit": "c" * 40, "path": "kits/x.json"}, "line1": "seat", "line2": "ci", "batch_window": "none"}


PRIOR = [{"plan_id": "cq-p1-a1", "campaign_id": "cl-dev-01", "block_id": "dev-01", "kit_sha256": "1" * 64,
          "roster": [f"L{i:03d}" for i in range(1, 13)], "legs": 12, "mixed": False,
          "t0": "2026-11-15T01:00:00-08:00", "closed": "2026-11-15T06:00:00-08:00", "desk_final": "hand"},
         {"plan_id": "cq-p2-a1", "campaign_id": "cl-dev-01", "block_id": "dev-01", "kit_sha256": "1" * 64,
          "roster": [f"L{i:03d}" for i in range(1, 7)], "legs": 6, "mixed": False,
          "t0": "2026-11-16T01:00:00-08:00", "closed": "2026-11-16T04:00:00-08:00", "desk_final": "auto"}]


def standing(**over):
    doc = {"schema": law.STANDING_SCHEMA, "standing_id": "cs-test", "queues": [{"path": "Q1.json", "role": "standing"}],
           "kits": {sha: entry() for sha in KITS}, "hand_gates": [], "gate_records": [], "withdrawn": [],
           "dispositions": [], "prior_spans": copy.deepcopy(PRIOR),
           "sessions": [{"session_id": "slot-1", "kind": "r1-slot", "route": "docs/align/r1_arm_runbook.md"}],
           "fallback": [], "freeze2": None}
    doc.update(over)
    return law.validate_standing(doc)


def span(seq, sid, key, legs, nb="2026-11-17", block=None, rerun_of=None):
    s = {"seq": seq, "span_id": sid, "block_id": block or sid.rsplit("-s", 1)[0], "attempt": 1, "not_before": nb,
         "kit": {"path": f"kits/{key}.json", "sha256": SHA[key]}, "legs": legs}
    if rerun_of:
        s["rerun_of"] = rerun_of
    return s


def view(spans, path="Q1.json", role="standing", commit=NOW - 3600, first=None, fallback=False,
         expires="2026-11-23T00:00:00-08:00", notice=900):
    doc = {"schema": q.SCHEMA, "queue_id": "cq-" + path.lower().replace(".json", "").replace("_", "-"),
           "expires_at": expires, "halt": None, "standing_notice": None if notice is None else {"issue": notice},
           "spans": spans}
    return {"path": path, "role": role, "fallback": fallback, "doc": doc, "commit_epoch": commit,
            "first_commit_epoch": commit if first is None else first, "first_commit": "1" * 40, "tip_commit": "2" * 40,
            "kits": dict(KITS), "reasons": [], "closed_ids": set(), "withdrawn_ids": set(), "digest": "d" * 64}


def pilot(key, sid=None, **kw):
    sid = sid or f"dev-{'04' if key == '04' else '05'}-s01"
    return view([span(1, sid, key, L[:6])], role="smoke", **kw)


def record(plan_id, key, legs, t0, closed=None, status="CLOSED_OK", bundle="e" * 64, gates=None, finished=None):
    k = BY_KEY[key]
    cls = law.kit_class(k)
    sid = plan_id[3:].rsplit("-a", 1)[0]
    return {"plan_id": plan_id, "kind": "campaign" if cls["k2"] else "f2", "phase": cls["phase"],
            "block_id": sid.rsplit("-s", 1)[0], "legs": legs, "mixed": cls["mixed"], "t0_epoch": t0,
            "closed_epoch": closed if closed is not None else t0 + 3 * 3600, "status": status,
            "bundle_sha256": bundle, "kit_sha256": SHA[key], "campaign_id": k["campaign_id"],
            "gates": law.derived_gates(k, legs) if gates is None else gates,
            "legs_finished": len(legs) if finished is None else finished, "runner_t0": t0,
            "armed": {"plan_id": plan_id, "queue_id": "cq-q1", "span_id": sid, "attempt": 1}}


def released(*plan_gates):
    return [{"plan_id": p, "gate": g, "decision": "release", "record": "hand read"} for p, g in plan_gates]


def kit_holds(rec):
    campaign = KITS[rec["kit_sha256"]]["campaign_id"]
    return [{"code": "HAND_GATE", "scope": f"kit:{campaign}", "gate": GATE_NAMES[g]} for g in rec["gates"]]


def verdict(rec, *, final=True, mock=False, holds=None, next_hold=False, signed=True, anchor=None,
            history="signed-records"):
    doc = {"schema": desk_final.VERDICT_SCHEMA, **rec["armed"], "desk_final": final, "next_arm_hold": next_hold,
           "history_source": history,
           "holds": kit_holds(rec) if holds is None else list(holds), "mock": mock, "transport": {"signed": signed},
           "identities": {"manifest_sha256": anchor or rec["bundle_sha256"]}}
    return {"doc": desk_final._finish(doc)}


def q1_doc(plan_id):
    sid, attempt = plan_id[3:].rsplit("-a", 1)
    return {"schema": desk_final.Q1_RECORD_SCHEMA, "plan_id": plan_id, "span_id": sid, "attempt": int(attempt),
            "signer": "lead", "recorded_at": "2026-11-17T08:00:00-08:00", "print_ref": "Q1 print"}


def snap(views, st=None, *, now=NOW, runs=None, verdicts=None, issues=(), watcher=True, sessions=(), census=None,
         fallback_views=(), plan_worst=None, records=(), externals=(), accept_mock=False, mbp_verdicts=None, q1=None,
         q1_epochs=None):
    st = st or standing()
    runs = runs if runs is not None else law.build_runs(st, list(records), list(externals), kits=KITS)
    halts = law.apply_verdicts(runs, verdicts or {}, accept_mock=accept_mock, mbp_verdicts=mbp_verdicts)
    if q1 is None:      # every span's Q1 record present, committed after its close (RL-173 E has its own tests)
        q1 = {r.plan_id: {"doc": q1_doc(r.plan_id), "error": None} for r in runs if r.kind == "campaign"}
        q1_epochs = {r.plan_id: (r.closed or 0) + 60 for r in runs if r.kind == "campaign"}
    halts += law.apply_q1(runs, q1, KITS, q1_epochs or {})
    ran = {r.plan_id for r in runs}
    for v in [*views, *fallback_views]:
        v["closed_ids"] = ran
        v["withdrawn_ids"] = set(st["withdrawn"])
    stamp = {"schema": law.WATCHER_STAMP_SCHEMA, "watcher": WATCHER, "by": "lead",
             "observed_live_at": datetime.fromtimestamp(now - 3600, law.ZONE).isoformat()}
    return {"now": now, "standing": st, "input_reasons": [], "queues": list(views), "runs": runs, "desk_halts": halts,
            "vetoes": law.veto_reasons(list(issues), "mpmdw"),
            "watcher": (law.watcher_reasons(stamp, now - 1800, now, WATCHER) if watcher
                        else law.watcher_reasons(None, None, now, WATCHER)),
            "sessions": law.session_reasons(st, list(sessions), set()), "census_reasons": [], "census_epoch": census,
            "fallback": st["fallback"], "fallback_queues": list(fallback_views),
            "plan_worst": plan_worst or (lambda cand: 3 * 3600)}


def codes(decision):
    return {r["code"] for r in decision.reasons} | {c for cs in decision.gates.values() for c in cs}


def pilot_done(key="05", **kw):
    """A clean controller pilot of the kit (dev-05 by default) earlier today, and the lead's release records for
    every gate it raised."""
    pid = f"cq-dev-{'04' if key == '04' else '05'}-s01-a1"
    rec = record(pid, key, L[:6], NOW - 6 * 3600, closed=NOW - 4 * 3600, **kw)
    return rec, released(*[(pid, g) for g in rec["gates"]])


class SolProbes(unittest.TestCase):
    """The probes in sol-throughput/probe_detectors.py, re-aimed at the controller's arm path."""

    def test_future_not_before_does_not_arm(self):
        d = law.select(snap([view([span(1, "dev-05-s01", "05", L[:6], nb="2026-11-20")], role="smoke")]))
        self.assertEqual(d.action, "wait")
        self.assertIn("NOT_BEFORE", codes(d))
        eta = next(r["eta"] for r in d.reasons if r["code"] == "NOT_BEFORE")
        self.assertEqual(eta, at("2026-11-20T00:00:00-08:00"))

    def test_zero_leg_rows_is_a_stop(self):
        receipt = {"roster": ["L001"], "kit": {"sha256": SHA["04"], "frozen_commit": KIT04["frozen"]["commit"]},
                   "legs_planned": 1, "legs": [], "rc": 0}
        rs = law.desk_input_reasons(span=span(1, "s", "04", ["L001"]), kit_sha=SHA["04"], kit=KIT04, receipt=receipt,
                                    summaries={}, plan={"legs": [{"leg_id": "L001"}]})
        self.assertIn("NO_LEG_ROWS", {r["code"] for r in rs})
        self.assertEqual(law.category(rs), "halt")

    def test_a_new_queue_does_not_erase_global_desk_debt(self):
        prior = copy.deepcopy(PRIOR)
        prior[0]["desk_final"] = None
        d = law.select(snap([pilot("05", path="NEW.json")], standing(prior_spans=prior)))
        self.assertEqual(d.action, "wait")
        self.assertIn("K2_DESK_DEBT", codes(d))

    def test_restore_unproven_is_not_healthy(self):
        rs = law.proof_reasons({"powermode": {"ok": True}}, "close")
        self.assertEqual(law.category(rs), "halt")
        self.assertIn("network_time: not observed", json.dumps(rs))


class Condition1Dates(unittest.TestCase):
    def test_clean_pilot_arms(self):
        d = law.select(snap([pilot("05")]))
        self.assertEqual(d.action, "arm", d.reasons)

    def test_missed_date_halts_for_the_lead_to_redate(self):
        d = law.select(snap([view([span(1, "dev-05-s01", "05", L[:6], nb="2026-11-16")], role="smoke")]))
        self.assertEqual(d.action, "halt")
        self.assertIn("DATE_MISSED", codes(d))

    def test_no_dated_arm_in_the_last_two_minutes_of_its_date(self):   # Mythos F19
        d = law.select(snap([pilot("05")], now=at("2026-11-17T23:59:00-08:00")))
        self.assertIn("MIDNIGHT", codes(d))

    def test_twelve_mixed_legs_a_date_counting_legs_run(self):         # Mythos F8 (D)
        rec, rel = pilot_done("05")
        rest = view([span(1, "dev-05-s02", "05", L[6:])], path="Q2.json")
        other = record("cq-dev-04-s01-a1", "04", L[:6], NOW - 3 * 3600, closed=NOW - 2000)
        gates = rel + released(("cq-dev-04-s01-a1", "class-a"), ("cq-dev-04-s01-a1", "L005"))
        d = law.select(snap([rest], standing(gate_records=gates), records=[rec, other]))
        self.assertEqual(d.action, "halt")
        self.assertIn("DATE_DEV_MIXED_CAP", codes(d))
        refused = dict(other, status="REFUSED", legs_finished=0)
        st = standing(gate_records=gates, dispositions=[{"plan_id": "cq-dev-04-s01-a1", "resolution": "rerun",
                                                         "record": "RL-x"}])
        self.assertNotIn("DATE_DEV_MIXED_CAP", codes(law.select(snap([rest], st, records=[rec, refused]))))

    def test_twenty_four_development_legs_a_date(self):
        prior = copy.deepcopy(PRIOR) + [
            {"plan_id": f"cq-x{i}-a1", "campaign_id": "cl-dev-01", "block_id": "dev-0x", "kit_sha256": "1" * 64,
             "roster": L[:12], "legs": 12, "mixed": False,
             "t0": f"2026-11-17T0{i}:00:00-08:00", "closed": f"2026-11-17T0{i}:30:00-08:00", "desk_final": "y"}
            for i in (1, 2)]
        d = law.select(snap([pilot("05")], standing(prior_spans=prior)))
        self.assertIn("DATE_DEV_CAP", codes(d))

    def test_qualification_waits_for_freeze2_then_keeps_off_development_dates(self):
        qv = view([span(1, "qual-01-s01", "q1", L[:6], block="qual-01")], role="smoke")
        self.assertIn("FREEZE2", codes(law.select(snap([qv]))))
        st = standing(freeze2="freeze 2 at abc")
        day16 = at("2026-11-16T09:00:00-08:00")
        d = law.select(snap([view([span(1, "qual-01-s01", "q1", L[:6], nb="2026-11-16", block="qual-01")],
                                  role="smoke", commit=day16 - 3600)], st, now=day16))
        self.assertIn("DATE_QUAL_DEV_OVERLAP", codes(d))   # dev-02 ran on the 16th
        planned = view([span(1, "dev-05-s01", "05", L[:6], nb="2026-11-17")], path="Q2.json", role="smoke")
        d = law.select(snap([view([span(1, "qual-01-s01", "q1", L[:6], block="qual-01")], role="smoke"), planned], st))
        self.assertIn("DATE_QUAL_DEV_OVERLAP", codes(d))   # dev-05 is planned for the 17th

    def test_qualification_blocks_use_two_dates(self):
        st = standing(freeze2="f2", prior_spans=[])
        day = "2026-11-19"
        now = at(f"{day}T15:00:00-08:00")
        rec = record("cq-qual-01-s01-a1", "q1", L[:6], now - 9 * 3600, closed=now - 6 * 3600)
        rec["block_id"] = "qual-01"
        v = view([span(1, "qual-02-s01", "q2", L[:6], nb=day, block="qual-02")], role="smoke", commit=now - 3600)
        d = law.select(snap([v], st, now=now, records=[rec]))
        self.assertIn("DATE_QUAL_SINGLE", codes(d))


class Condition2Debt(unittest.TestCase):
    def setUp(self):
        self.p1, self.rel = pilot_done("05")
        self.p2 = record("cq-dev-05-s02-a1", "05", L[6:9], NOW - 3 * 3600, closed=NOW - 2 * 3600)
        self.v3 = view([span(1, "dev-05-s03", "05", L[9:])], path="Q3.json")
        self.st = standing(prior_spans=[], gate_records=self.rel)

    def test_k_plus_two_counts_machine_order_across_queues(self):
        self.assertEqual(law.select(snap([self.v3], self.st, records=[self.p1])).action, "arm")
        d = law.select(snap([self.v3], self.st, records=[self.p1, self.p2]))
        self.assertIn("K2_DESK_DEBT", codes(d))      # span 3 needs span 1's verdict
        d = law.select(snap([self.v3], self.st, records=[self.p1, self.p2],
                            verdicts={self.p1["plan_id"]: verdict(self.p1)}))
        self.assertNotIn("K2_DESK_DEBT", codes(d))

    def test_only_a_signed_nonmock_final_verdict_on_the_published_anchor_counts(self):   # FORMAT 4.1; Sol 1
        for bad in (verdict(self.p1, final=False), verdict(self.p1, mock=True), verdict(self.p1, signed=False),
                    verdict(self.p1, history="file"), verdict(self.p1, history="none")):   # Mythos N11, Sol R8
            d = law.select(snap([self.v3], self.st, records=[self.p1, self.p2], verdicts={self.p1["plan_id"]: bad}))
            self.assertIn("K2_DESK_DEBT", codes(d))
        d = law.select(snap([self.v3], self.st, records=[self.p1, self.p2],
                            verdicts={self.p1["plan_id"]: verdict(self.p1, mock=True)}, accept_mock=True))
        self.assertNotIn("K2_DESK_DEBT", codes(d))   # synthetic runs only

    def test_unreadable_or_contradicting_verdicts_halt(self):
        for entry in ({"error": "TransportRefusal: no good SSH signature"}, verdict(self.p1, anchor="9" * 64)):
            d = law.select(snap([self.v3], self.st, records=[self.p1], verdicts={self.p1["plan_id"]: entry}))
            self.assertEqual(d.action, "halt")
            self.assertIn("DESK_VERDICT_INVALID", codes(d))

    def test_a_named_stop_hold_halts_until_cleared(self):
        v = verdict(self.p1, next_hold=True, holds=[{"code": "LEG_OVERTIME", "scope": "queue"}] + kit_holds(self.p1))
        d = law.select(snap([self.v3], self.st, records=[self.p1], verdicts={self.p1["plan_id"]: v}))
        self.assertIn("DESK_HOLD", codes(d))
        st = standing(prior_spans=[], gate_records=self.rel,
                      dispositions=[{"plan_id": self.p1["plan_id"], "resolution": "cleared", "record": "RL-x"}])
        d = law.select(snap([self.v3], st, records=[self.p1], verdicts={self.p1["plan_id"]: v}))
        self.assertNotIn("DESK_HOLD", codes(d))

    def test_a_verdict_gate_the_controller_did_not_derive_halts(self):
        extra = kit_holds(self.p1) + [{"code": "HAND_GATE", "scope": "kit:cl-dev-05", "gate": "L005 consumer gate"}]
        d = law.select(snap([self.v3], self.st, records=[self.p1], verdicts={self.p1["plan_id"]: verdict(self.p1, holds=extra)}))
        self.assertIn("GATE_DISAGREEMENT", codes(d))

    def test_a_rerun_resolution_takes_a_refused_span_out_of_the_count(self):   # Mythos F8 (D2)
        refused = dict(self.p2, status="REFUSED", legs_finished=0)
        p3 = record("cq-dev-05-s03-a1", "05", L[9:], NOW - 3000, closed=NOW - 1000)
        rerun = view([span(1, "dev-05-s02r", "05", L[6:9], rerun_of="dev-05-s02")], path="Q4.json")
        st = standing(prior_spans=[], gate_records=self.rel,
                      dispositions=[{"plan_id": refused["plan_id"], "resolution": "rerun", "record": "RL-x"}])
        d = law.select(snap([rerun], st, records=[self.p1, refused, p3], verdicts={self.p1["plan_id"]: verdict(self.p1)}))
        self.assertNotIn("K2_DESK_DEBT", codes(d))


class SecondGate(unittest.TestCase):
    """Regressions for the second gate's law-side findings (Mythos N2, N3, N8, N14, N16; Sol R6, R9)."""

    def test_a_hand_armed_pilot_raises_the_same_gates(self):          # Mythos N2: dev-04-s01 was a prior span
        prior = copy.deepcopy(PRIOR) + [
            {"plan_id": "cq-dev-04-s01-a1", "campaign_id": "cl-dev-04", "block_id": "dev-04", "kit_sha256": SHA["04"],
             "roster": L[:6], "legs": 6, "mixed": True, "t0": "2026-11-17T01:00:00-08:00",
             "closed": "2026-11-17T04:00:00-08:00", "desk_final": "hand"}]
        rest = view([span(1, "dev-04-s02", "04", L[6:])], path="Q2.json")
        d = law.select(snap([rest], standing(prior_spans=prior)))
        self.assertIn("HAND_GATE", codes(d))
        self.assertIn("L005", json.dumps(d.reasons))
        st = standing(prior_spans=prior, gate_records=released(("cq-dev-04-s01-a1", "class-a"),
                                                               ("cq-dev-04-s01-a1", "L005")))
        self.assertEqual(law.select(snap([rest], st)).action, "arm")

    def test_a_prior_span_whose_kit_is_unreadable_halts(self):
        prior = copy.deepcopy(PRIOR)
        st = standing(prior_spans=prior)
        runs = law.build_runs(st, [], [], kits={})
        d = law.select(snap([pilot("05")], st, runs=runs))   # dev-05 is not the unreadable campaign
        self.assertEqual(d.action, "arm")
        rest = view([span(1, "dev-01-s03", "01", L[9:])], path="Q2.json")
        self.assertIn("PRIOR_GATES_UNKNOWN", codes(law.select(snap([rest], st, runs=runs))))

    def test_a_prior_span_contradicting_its_queue_or_receipt_halts(self):
        st = standing()
        v = view([span(1, "p2", "01", L[:5])], path="Q9.json")   # plan id cq-p2-a1, other roster
        self.assertIn("PRIOR_CONTRADICTS", codes(law.select(snap([v, pilot("05")], st))))
        s = snap([pilot("05")], st)
        s["receipts"] = {"cq-p1-a1": {"roster": L[:11], "kit_sha256": "1" * 64}}
        self.assertIn("PRIOR_CONTRADICTS", codes(law.select(s)))

    def test_a_release_committed_before_the_close_halts(self):        # Mythos N14
        rec, rel = pilot_done("05")
        rest = view([span(1, "dev-05-s02", "05", L[6:])], path="Q2.json")
        s = snap([rest], standing(gate_records=rel), records=[rec])
        s["record_epochs"] = {(rec["plan_id"], "class-a"): rec["closed_epoch"] - 60}
        self.assertIn("GATE_RECORD_PREMATURE", codes(law.select(s)))
        s["record_epochs"] = {(rec["plan_id"], "class-a"): rec["closed_epoch"] + 60}
        self.assertEqual(law.select(s).action, "arm")

    def test_a_refused_judged_span_recovers_by_rerun(self):           # Mythos N3, Sol R9
        p1, rel = pilot_done("05")
        refused = record("cq-dev-05-s02-a1", "05", L[6:9], NOW - 3 * 3600, closed=NOW - 2 * 3600, status="REFUSED",
                         finished=0)
        negative = verdict(refused, final=False, next_hold=True, holds=[{"code": "REFUSAL", "scope": "queue"}])
        q2 = view([span(1, "dev-05-s02", "05", L[6:9]), span(2, "dev-05-s02r", "05", L[6:9], rerun_of="dev-05-s02")],
                  path="Q2.json")
        v = {p1["plan_id"]: verdict(p1), refused["plan_id"]: negative}
        st = standing(prior_spans=[], gate_records=rel)
        self.assertIn("DESK_HOLD", codes(law.select(snap([q2], st, records=[p1, refused], verdicts=v))))
        st = standing(prior_spans=[], gate_records=rel,
                      dispositions=[{"plan_id": refused["plan_id"], "resolution": "rerun", "record": "RL-x"}])
        d = law.select(snap([q2], st, records=[p1, refused], verdicts=v))
        self.assertEqual(d.action, "arm", d.reasons)
        self.assertEqual(d.candidate["span"]["span_id"], "dev-05-s02r")

    def test_a_refused_pilot_is_rerun_in_its_own_smoke_queue(self):    # Mythos N3: the documented shape
        refused = dict(pilot_done("05")[0], status="REFUSED", legs_finished=0)
        smoke = view([span(1, "dev-05-s01", "05", L[:6]), span(2, "dev-05-s01r", "05", L[:6], rerun_of="dev-05-s01")],
                     role="smoke")
        st = standing(dispositions=[{"plan_id": refused["plan_id"], "resolution": "rerun", "record": "RL-x"}])
        self.assertEqual(law.select(snap([smoke], st, records=[refused])).action, "arm")
        cleared = standing(dispositions=[{"plan_id": refused["plan_id"], "resolution": "cleared", "record": "x"}])
        self.assertIn("SMOKE_QUEUE_NOT_PILOT_ONLY", codes(law.select(snap([smoke], cleared, records=[refused]))))

    def test_a_refused_launch_counts_no_legs_on_its_date(self):       # Mythos N16
        refused = record("cq-dev-04-s01-a1", "04", L[:6], NOW - 3600, status="LAUNCH_REFUSED")
        refused["closed_epoch"] = None
        st = standing(dispositions=[{"plan_id": refused["plan_id"], "resolution": "rerun", "record": "x"}])
        run = next(r for r in law.build_runs(st, [refused], [], kits=KITS) if r.plan_id == refused["plan_id"])
        self.assertEqual(run.legs, 0)

    def test_a_first_commit_in_the_future_halts(self):                # Mythos N8
        self.assertIn("QUEUE_COMMIT_IN_FUTURE", codes(law.select(snap([pilot("05", commit=NOW - 60,
                                                                                first=NOW + 30 * 86400)]))))

    def test_a_global_refusal_is_on_the_pending_spans_ledger(self):   # Sol R6
        owner = {"login": "mpmdw"}
        d = law.select(snap([pilot("05")], issues=[{"number": 1, "title": "STOP", "labels": ["directive"],
                                                    "author": owner}]))
        self.assertEqual(d.gates, {"dev-05-s01": ["VETO_OPEN"]})

    def test_a_night_window_waits_long_before_paging(self):           # Mythos N15
        self.assertEqual(law.stall_bound(["NIGHT_AGENT"]), law.STALL_LONG_S)
        self.assertEqual(law.stall_bound(["NIGHT_UNKNOWN"]), law.STALL_SHORT_S)


class Condition3Expiry(unittest.TestCase):
    def test_seven_days_from_the_first_commit_not_the_last(self):          # Mythos F13
        v = pilot("05", commit=NOW - 60, first=NOW - 7 * 86400 - 1, expires="2026-12-31T00:00:00-08:00")
        self.assertIn("QUEUE_EXPIRED", codes(law.select(snap([v]))))

    def test_the_field_when_sooner(self):
        v = pilot("05", expires="2026-11-17T08:00:00-08:00")
        self.assertIn("QUEUE_EXPIRED", codes(law.select(snap([v]))))

    def test_a_drained_expired_queue_does_not_halt(self):
        rec, rel = pilot_done("05")
        old = pilot("05", first=NOW - 8 * 86400)
        d = law.select(snap([old, view([span(1, "dev-05-s02", "05", L[6:])], path="Q2.json")],
                            standing(gate_records=rel), records=[rec]))
        self.assertNotIn("QUEUE_EXPIRED", codes(d))

    def test_a_commit_in_the_future_is_a_contradiction(self):
        self.assertIn("QUEUE_COMMIT_IN_FUTURE", codes(law.select(snap([pilot("05", commit=NOW + 3600)]))))

    def test_append_only_history(self):
        a = {"queue_id": "cq-a", "spans": [{"seq": 1}]}
        self.assertEqual(law.append_only_problems([a, {"queue_id": "cq-a", "spans": [{"seq": 1}, {"seq": 2}]}]), [])
        self.assertTrue(law.append_only_problems([a, {"queue_id": "cq-a", "spans": [{"seq": 1, "x": 1}]}]))
        self.assertTrue(law.append_only_problems([a, {"queue_id": "cq-b", "spans": [{"seq": 1}]}]))


class Condition4SmokeAndGates(unittest.TestCase):
    def test_a_pilot_must_be_alone_in_a_smoke_queue(self):
        self.assertIn("SMOKE_QUEUE_NOT_PILOT_ONLY", codes(law.select(snap([view([span(1, "dev-05-s01", "05", L[:6])])]))))
        two = view([span(1, "dev-05-s01", "05", L[:6]), span(2, "dev-05-s02", "05", L[6:])], role="smoke")
        self.assertIn("SMOKE_QUEUE_NOT_PILOT_ONLY", codes(law.select(snap([two]))))

    def test_the_remainder_may_not_be_staged_with_its_pilot(self):
        d = law.select(snap([pilot("05"), view([span(1, "dev-05-s02", "05", L[6:])], path="Q2.json")]))
        self.assertIn("SMOKE_REMAINDER_STAGED", codes(d))

    def test_no_span_before_its_kits_pilot(self):
        self.assertIn("PILOT_MISSING", codes(law.select(snap([view([span(1, "dev-05-s02", "05", L[6:])])]))))

    def test_class_a_is_derived_and_holds_until_the_lead_releases_it(self):   # Sol 6, Mythos F2
        rec, rel = pilot_done("05")
        rest = view([span(1, "dev-05-s02", "05", L[6:])], path="Q2.json")
        d = law.select(snap([rest], standing(), records=[rec]))      # hand_gates is empty: the gate is still there
        self.assertEqual(d.action, "wait")
        self.assertIn("HAND_GATE", codes(d))
        hold = standing(gate_records=[{"plan_id": rec["plan_id"], "gate": "class-a", "decision": "hold", "record": "x"}])
        self.assertIn("HAND_GATE", codes(law.select(snap([rest], hold, records=[rec]))))
        self.assertEqual(law.select(snap([rest], standing(gate_records=rel), records=[rec])).action, "arm")

    def test_l005_gate_is_derived_from_kit_and_roster(self):   # Sol 6, Mythos F2: L005 timed out, no hand_gates
        self.assertEqual(law.derived_gates(KIT04, L[:6]), ["class-a", "L005"])
        self.assertEqual(law.derived_gates(KIT04, L[6:]), [])
        self.assertEqual(law.derived_gates(KIT05, L[:6]), ["class-a"])
        rec, _ = pilot_done("04")
        rest = view([span(1, "dev-04-s02", "04", L[6:])], path="Q2.json")
        d = law.select(snap([rest], standing(gate_records=released((rec["plan_id"], "class-a"))), records=[rec]))
        self.assertIn("HAND_GATE", codes(d))
        self.assertIn("L005", json.dumps(d.reasons))
        both = standing(gate_records=released((rec["plan_id"], "class-a"), (rec["plan_id"], "L005")))
        self.assertEqual(law.select(snap([rest], both, records=[rec])).action, "arm")

    def test_a_refused_pilot_can_be_rerun_alone(self):          # Mythos F8 (C)
        refused = dict(pilot_done("05")[0], status="REFUSED", legs_finished=0)
        rerun = view([span(1, "dev-05-s01r", "05", L[:6], rerun_of="dev-05-s01")], path="Q2.json", role="smoke")
        st = standing(dispositions=[{"plan_id": refused["plan_id"], "resolution": "rerun", "record": "RL-x"}])
        self.assertEqual(law.select(snap([rerun], st, records=[refused])).action, "arm")

    def test_a_named_extra_gate_holds_its_span(self):
        rec, rel = pilot_done("05")
        rest = view([span(1, "dev-05-s02", "05", L[6:])], path="Q2.json")
        st = standing(gate_records=rel, hand_gates=[{"id": "lead-1", "holds": ["dev-05-s02"], "passed": False,
                                                     "record": ""}])
        self.assertIn("HAND_GATE", codes(law.select(snap([rest], st, records=[rec]))))

    def test_standing_has_no_kit_hand_gate_flag(self):          # Mythos F2: a typed pass flag was a contradiction
        with self.assertRaises(law.StandingError):
            standing(kits={SHA["05"]: {**entry(), "hand_gate": {"passed": True, "record": "x"}}})


class Condition5Proofs(unittest.TestCase):
    LINES = {k: {"ok": True} for k in law.PROOF_LINES}

    def test_every_line_needed(self):
        self.assertEqual(law.proof_reasons(self.LINES, "arm"), [])
        for line, kinds in law.PROOF_LINES.items():
            lines = dict(self.LINES)
            del lines[line]
            for kind in kinds:
                self.assertEqual(law.category(law.proof_reasons(lines, kind)), "halt", (line, kind))

    def test_bad_readbacks_halt(self):
        for line in ("kernel_frequency", "network_time", "powermode", "high_power_marker", "root_powermetrics"):
            lines = dict(self.LINES, **{line: {"ok": False, "detail": "x"}})
            self.assertEqual(law.category(law.proof_reasons(lines, "close")), "halt", line)

    def test_signing_unavailable_is_its_own_halt(self):          # Mythos F11
        rs = law.proof_reasons(dict(self.LINES, signing={"ok": False, "detail": "no key"}), "arm")
        self.assertEqual([r["code"] for r in rs], ["SIGNING_UNAVAILABLE"])

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
        for refused in (self.receipt(rc=3, legs_finished=1), self.receipt(error="ValueError: x")):
            self.assertIn("RECEIPT_NOT_CLEAN", {r["code"] for r in law.receipt_command_reasons(refused, [])})
        for feeds in ({"meter": {"stop": {"proven_stopped": False}}}, {}):
            self.assertIn("CLOSE_UNPROVEN",
                          {r["code"] for r in law.receipt_command_reasons(self.receipt(feeds=feeds), [])})

    def test_a_soak_retry_is_normal_and_legacy_receipts_have_one_soak(self):
        retried = self.receipt(steps=[{"name": "soak", "rc": 5}, {"name": "soak.a2", "rc": 0},
                                      {"name": "restore", "rc": 0}, {"name": "stop-meter", "rc": 0}],
                               soak_attempts=[{"attempt": 1, "refused": "unsettled"}, {"attempt": 2, "refused": None}])
        self.assertEqual(law.receipt_command_reasons(retried, []), [])
        three = self.receipt(soak_attempts=[{"attempt": i, "refused": "x"} for i in (1, 2)] + [{"attempt": 3, "refused": None}])
        self.assertIn("ROSTER_MISMATCH", {r["code"] for r in law.receipt_command_reasons(three, [])})
        legacy = self.receipt()
        del legacy["soak_attempts"]
        self.assertEqual(law.receipt_command_reasons(legacy, []), [])
        legacy["steps"][0]["rc"] = 2
        self.assertIn("ROSTER_MISMATCH", {r["code"] for r in law.receipt_command_reasons(legacy, [])})


class Condition6Gap(unittest.TestCase):
    def test_three_hundred_after_campaign_twelve_hundred_after_other(self):
        rec, rel = pilot_done("05")
        rec["closed_epoch"] = NOW - 100
        rest = view([span(1, "dev-05-s02", "05", L[6:])], path="Q2.json")
        st = standing(gate_records=rel)
        self.assertIn("GAP", codes(law.select(snap([rest], st, records=[rec]))))
        self.assertEqual(law.select(snap([rest], st, records=[rec], now=NOW + 200)).action, "arm")
        self.assertIn("GAP", codes(law.select(snap([rest], st, records=[rec], now=NOW + 200, census=NOW))))


class Condition7Evidence(unittest.TestCase):
    def test_vetoes(self):
        owner = {"login": "mpmdw"}
        for issue in ({"number": 1, "title": "STOP everything", "labels": [{"name": "directive"}], "author": owner},
                      {"number": 2, "title": "x", "body": "NO dev-04 tonight", "labels": ["directive"], "author": owner},
                      {"number": 3, "title": "desk stop", "labels": [{"name": "cadence-stop"}], "author": owner}):
            self.assertEqual(law.select(snap([pilot("05")], issues=[issue])).action, "halt", issue)
        ignored = [{"number": 4, "title": "STOP", "labels": ["directive"], "author": {"login": "someone"}},
                   {"number": 5, "title": "Note", "body": "fyi", "labels": ["directive"], "author": owner}]
        self.assertEqual(law.select(snap([pilot("05")], issues=ignored)).action, "arm")

    def test_unreadable_issues_never_mean_no_veto(self):
        s = snap([pilot("05")])
        s["vetoes"] = law.veto_reasons(None, "mpmdw")
        self.assertEqual(law.select(s).action, "wait")

    def test_watcher_stamp(self):                               # Sol 12: the named watcher only
        self.assertEqual(law.select(snap([pilot("05")], watcher=False)).action, "halt")
        stamp = {"schema": law.WATCHER_STAMP_SCHEMA, "watcher": WATCHER, "by": "lead",
                 "observed_live_at": datetime.fromtimestamp(NOW - 25 * 3600, law.ZONE).isoformat()}
        self.assertEqual(law.watcher_reasons(stamp, NOW - 25 * 3600, NOW, WATCHER)[0]["code"], "WATCHER_STALE")
        stamp["observed_live_at"] = datetime.fromtimestamp(NOW, law.ZONE).isoformat()
        self.assertEqual(law.watcher_reasons(stamp, NOW - 3600, NOW, WATCHER)[0]["code"], "WATCHER_STAMP_INVALID")
        stamp["observed_live_at"] = datetime.fromtimestamp(NOW - 3600, law.ZONE).isoformat()
        self.assertEqual(law.watcher_reasons(dict(stamp, watcher="imaginary"), NOW - 60, NOW, WATCHER)[0]["code"],
                         "WATCHER_STAMP_INVALID")


class Condition8BadTerminal(unittest.TestCase):
    def test_a_bad_span_halts_until_the_lead_disposes_of_it(self):
        rec, rel = pilot_done("05", status="STOPPED")
        rest = view([span(1, "dev-05-s02", "05", L[6:])], path="Q2.json")
        self.assertIn("SPAN_BAD_TERMINAL", codes(law.select(snap([rest], standing(gate_records=rel), records=[rec]))))

    def test_a_foreign_close_is_unproven_until_noted(self):   # Sol 10
        ext = {"run_id": "align-r0:f0", "kind": "other", "t0_epoch": NOW - 9000, "closed_epoch": NOW - 5000,
               "restore": "unproven"}
        self.assertIn("FOREIGN_CLOSE_UNPROVEN", codes(law.select(snap([pilot("05")], externals=[ext]))))
        self.assertEqual(law.select(snap([pilot("05")], externals=[dict(ext, restore="proven")])).action, "arm")


class Condition9Fallback(unittest.TestCase):
    def test_only_f0_and_f2(self):
        with self.assertRaises(law.StandingError) as ctx:
            standing(fallback=[{"kind": "F3", "queues": [{"path": "x", "role": "standing"}]}])
        self.assertIn("FALLBACK_INVALID", str(ctx.exception))

    def test_f0_pages_when_nothing_counted_can_hold(self):
        st = standing(fallback=[{"kind": "F0", "standing_item": "RUN_STATE 999", "worst_case_s": 12180}])
        v = view([span(1, "dev-05-s01", "05", L[:6], nb="2026-11-18")], role="smoke")
        d = law.select(snap([v], st))
        self.assertEqual((d.action, d.reasons[0]["code"]), ("page", "FALLBACK_F0_DUE"))
        self.assertEqual(law.select(snap([v], st, now=at("2026-11-17T22:30:00-08:00"))).action, "wait")

    def test_f0_spacing(self):
        st = standing(fallback=[{"kind": "F0", "standing_item": "RUN_STATE 999", "worst_case_s": 12180}])
        ext = [{"run_id": "f0-1", "kind": "F0", "t0_epoch": NOW - 3600, "closed_epoch": NOW - 1300, "restore": "proven"}]
        v = view([span(1, "dev-05-s01", "05", L[:6], nb="2026-11-18")], role="smoke")
        self.assertIn("FALLBACK_SPACING", codes(law.select(snap([v], st, externals=ext))))

    def test_f2_arms_only_when_it_costs_no_counted_date(self):
        f2 = view([span(1, "f2-inst-01-p1", "f2", L[:3], block="f2-inst-01")], path="F2.json", role="smoke",
                  fallback=True)
        rec, rel = pilot_done("05")
        held = view([span(1, "dev-05-s02", "05", L[6:])], path="Q2.json")
        hg = standing(fallback=[{"kind": "F2", "queues": [{"path": "F2.json", "role": "smoke"}]}], gate_records=rel,
                      hand_gates=[{"id": "x", "holds": ["dev-05-s02"], "passed": False, "record": ""}])
        self.assertEqual(law.select(snap([held], hg, fallback_views=[f2], records=[rec])).action, "arm-fallback")
        d = law.select(snap([held], hg, fallback_views=[f2], records=[rec], now=at("2026-11-17T22:00:00-08:00")))
        self.assertIn("FALLBACK_DAY_COST", codes(d))

    def test_a_filler_kit_in_a_counted_queue_halts(self):
        d = law.select(snap([view([span(1, "f2-inst-01-p1", "f2", L[:3])], role="smoke")]))
        self.assertIn("KIT_ROLE_MISMATCH", codes(d))


class SectionF_Sessions(unittest.TestCase):
    def ready(self, sid="slot-1"):
        return {"schema": law.SESSION_READY_SCHEMA, "session_id": sid, "by": "lead", "ready_at": "2026-11-17T08:00:00-08:00"}

    def test_ready_session_cedes_and_nothing_lower_arms(self):
        d = law.select(snap([pilot("05")], sessions=[self.ready()]))
        self.assertEqual(d.action, "cede")
        self.assertIn("docs/align/r1_arm_runbook.md", d.reasons[0]["detail"])

    def test_done_session_releases_and_unknown_session_halts(self):
        st = standing()
        self.assertEqual(law.session_reasons(st, [self.ready()], {"slot-1"}), [])
        self.assertEqual(law.session_reasons(st, [self.ready("nope")], set())[0]["code"], "SESSION_INVALID")


class QueueIntegrity(unittest.TestCase):
    def test_a_missing_or_invalid_queue_halts_even_when_another_can_arm(self):   # Sol 5
        missing = {**view([]), "doc": None, "reasons": [law.reason("QUEUE_MISSING", "Q0.json")], "path": "Q0.json"}
        self.assertEqual(law.select(snap([missing, pilot("05", path="Q2.json")])).action, "halt")

    def test_a_halt_in_a_later_queue_halts_the_earlier_one(self):              # Sol 5
        later = pilot("04", path="Q2.json")
        later["doc"]["halt"] = {"reason": "lead", "by": "lead", "at": "now"}
        d = law.select(snap([pilot("05"), later]))
        self.assertEqual(d.action, "halt")
        self.assertIn("QUEUE_HALT", codes(d))

    def test_a_rewritten_queue_halts(self):                                     # Mythos F4 (the reader raises it)
        v = pilot("05")
        v["reasons"].append(law.reason("QUEUE_REWRITTEN", "first commit changed"))
        self.assertEqual(law.select(snap([v])).action, "halt")

    def test_a_queue_without_its_standing_notice_halts(self):                  # Mythos F16
        self.assertIn("QUEUE_NO_NOTICE", codes(law.select(snap([pilot("05", notice=None)]))))

    def test_the_same_legs_or_plan_in_two_queues_halt(self):                   # Mythos F12
        a = pilot("05")
        b = view([span(1, "dev-05-s01x", "05", L[:6])], path="Q2.json", role="smoke")
        self.assertIn("QUEUE_DUPLICATE", codes(law.select(snap([a, b]))))
        c = view([span(1, "dev-05-s01", "05", L[:2])], path="Q3.json", role="smoke")
        self.assertIn("QUEUE_DUPLICATE", codes(law.select(snap([a, c]))))


def marker(plan_id, **over):
    doc = {"schema": law.OFFLOAD_MARKER_SCHEMA, "plan_id": plan_id, "source": f"/o/cl-dev-05/{plan_id}-20261117T160000Z",
           "manifest_sha256": "a" * 64, "manifest_files": 10, "ciphertext_sha256": "b" * 64, "ciphertext_bytes": 4096,
           "provider": "cloud", "remote_path": f"offload/{plan_id}.enc",
           "upload": {"confirmed": True, "readback": "size", "value": 4096, "evidence": "provider size readback"},
           "verified": True, "key_second_copy": "the Air's custody root", "written_at": "2026-11-17T09:02:00-08:00"}
    doc.update(over)
    return doc


class Census(unittest.TestCase):
    def runs(self):
        return law.build_runs(standing(), [record("cq-dev-05-s01-a1", "05", L[:6], NOW - 9000)], [], kits=KITS)

    def test_copy_gate_binds_the_newest_campaign_close(self):                  # Sol 11
        newest = "/o/cl-dev-05/cq-dev-05-s01-a1-20261117T160000Z/runner_receipt.json"
        census = {"newest": (int(NOW), newest), "campaign": [newest]}
        self.assertEqual([r["code"] for r in law.census_reasons(census, self.runs(), "/o", {})], ["JOURNAL_COPY"])
        good = {"cq-dev-05-s01-a1": {"doc": marker("cq-dev-05-s01-a1"), "error": None, "failed": False}}
        self.assertEqual(law.census_reasons(census, self.runs(), "/o", good, now=NOW), [])
        other = {"newest": (int(NOW), "/w/f0/runner_receipt.json"), "campaign": [newest]}
        self.assertEqual(law.census_reasons(other, self.runs(), "/o", {}), [])

    def test_an_unknown_campaign_receipt_or_a_failed_census_halts(self):       # Mythos F18
        stray = "/o/cl-dev-03/cq-dev-03-s01-a1-20261117T020000Z/runner_receipt.json"
        census = {"newest": (int(NOW), "/w/x/runner_receipt.json"), "campaign": [stray]}
        self.assertEqual([r["code"] for r in law.census_reasons(census, self.runs(), "/o", {})],
                         ["UNKNOWN_CAMPAIGN_RECEIPT"])
        self.assertEqual(law.census_reasons("receipt root missing", self.runs(), "/o", {})[0]["code"], "CENSUS_FAILED")


class Bounds(unittest.TestCase):
    def test_every_reason_is_named_categorized_and_bounded(self):              # Mythos F7
        for code, (cat, text) in law.REASONS.items():
            self.assertIn(cat, ("halt", "wait", "retry", "cede", "page"), code)
            self.assertTrue(text)
        self.assertEqual(law.stall_bound(["AGENT_PRESENT"]), law.STALL_SHORT_S)
        self.assertEqual(law.stall_bound(["PLAN_REFUSED_AT_T0"]), law.STALL_SHORT_S)
        self.assertEqual(law.stall_bound(["NOT_BEFORE"]), law.STALL_S)

    def test_classes_come_from_the_kit(self):
        self.assertEqual(law.kit_class(KIT04), {"phase": "development", "mixed": True, "k2": True, "dated": True})
        self.assertEqual(law.kit_class(KIT01)["mixed"], False)
        self.assertEqual(law.kit_class(QUAL1)["phase"], "qualification")
        self.assertEqual(law.kit_class({"campaign_id": "cl-hp-01"})["dated"], False)
        with self.assertRaises(law.StandingError):
            law.kit_class({"campaign_id": "mystery-01"})


class RL173(unittest.TestCase):
    """RL-173's owner list for the controller, on the law's side: the Q1 record in line 9's debt (E), the L002
    timeout (E), the MBP desk and the off-host re-check (B), the Actions watcher (C.4), the offload marker (A)."""

    def setUp(self):
        self.p1, self.rel = pilot_done("05")
        self.p2 = record("cq-dev-05-s02-a1", "05", L[6:9], NOW - 3 * 3600, closed=NOW - 2 * 3600)
        self.v3 = view([span(1, "dev-05-s03", "05", L[9:])], path="Q3.json")
        self.st = standing(prior_spans=[], gate_records=self.rel)
        self.final = {self.p1["plan_id"]: verdict(self.p1), self.p2["plan_id"]: verdict(self.p2)}

    def test_span_k_q1_record_before_span_k_plus_2_and_nothing_sooner(self):
        recs, epochs = {}, {}
        d = law.select(snap([self.v3], self.st, records=[self.p1], q1=recs, q1_epochs=epochs))
        self.assertEqual(d.action, "arm")           # span 2 owes nothing for span 1's print (it holds nothing sooner)
        d = law.select(snap([self.v3], self.st, records=[self.p1, self.p2], verdicts=self.final, q1=recs,
                            q1_epochs=epochs))
        self.assertIn("K2_Q1_DEBT", codes(d))
        self.assertNotIn("K2_DESK_DEBT", codes(d))
        recs[self.p1["plan_id"]] = {"doc": q1_doc(self.p1["plan_id"]), "error": None}
        epochs[self.p1["plan_id"]] = self.p1["closed_epoch"] + 600
        d = law.select(snap([self.v3], self.st, records=[self.p1, self.p2], verdicts=self.final, q1=recs,
                            q1_epochs=epochs))
        self.assertEqual(d.action, "arm")

    def test_a_bad_or_premature_q1_record_halts_and_a_v1_kit_owes_none(self):
        pid = self.p1["plan_id"]
        for rec, epoch in (({"doc": dict(q1_doc(pid), attempt=2), "error": None}, self.p1["closed_epoch"] + 60),
                           ({"doc": q1_doc(pid), "error": None}, self.p1["closed_epoch"] - 60),
                           ({"doc": None, "error": "q1/x.json: a denied key"}, self.p1["closed_epoch"] + 60)):
            d = law.select(snap([self.v3], self.st, records=[self.p1, self.p2], verdicts=self.final,
                                q1={pid: rec}, q1_epochs={pid: epoch}))
            self.assertEqual(d.action, "halt")
            self.assertIn("Q1_RECORD_INVALID", codes(d))
        runs = law.build_runs(standing(), [], [], kits=KITS)            # the prior dev-01 spans: kit v1
        self.assertEqual(law.apply_q1(runs, {}, KITS, {}), [])
        self.assertEqual({r.extra.get("q1") for r in runs}, {"not-required"})
        runs = law.build_runs(standing(), [], [], kits={})               # a kit that cannot be read owes a record
        law.apply_q1(runs, {}, {}, {})
        self.assertEqual({r.extra.get("q1") for r in runs}, {"missing"})

    def test_an_l002_timeout_halts_every_arm_until_the_lead_releases_it(self):
        dev03 = kit("cl-dev-03.v1.1")
        kits = dict(KITS, **{"3" * 64: dev03})
        rec = record("cq-dev-03-s01-a1", "05", L[:3], NOW - 5 * 3600, closed=NOW - 4 * 3600)
        rec.update(kit_sha256="3" * 64, campaign_id="cl-dev-03", gates=law.derived_gates(dev03, L[:3]),
                   g0_unreleased=["L002"])
        self.assertEqual(rec["gates"], [law.CLASS_A, "L002"])
        other = pilot("04")
        st = standing(prior_spans=[], kits={**{sha: entry() for sha in kits}})
        runs = law.build_runs(st, [rec], [], kits=kits)
        d = law.select(snap([other], st, runs=runs))
        self.assertEqual(d.action, "halt")
        self.assertIn("L002_TIMEOUT", codes(d))
        runs = law.build_runs(st, [dict(rec, g0_unreleased=None)], [], kits=kits)      # not known: never a pass
        self.assertIn("L002_TIMEOUT", codes(law.select(snap([other], st, runs=runs))))
        runs = law.build_runs(st, [dict(rec, g0_unreleased=[])], [], kits=kits)        # L002 released its G0
        self.assertNotIn("L002_TIMEOUT", codes(law.select(snap([other], st, runs=runs))))
        st2 = standing(prior_spans=[], kits={**{sha: entry() for sha in kits}},
                       gate_records=released(("cq-dev-03-s01-a1", "L002")))
        runs = law.build_runs(st2, [rec], [], kits=kits)
        self.assertNotIn("L002_TIMEOUT", codes(law.select(snap([other], st2, runs=runs))))

    def test_the_mbp_desk_counts_and_a_disagreement_with_the_off_host_desk_halts(self):
        mbp = {self.p1["plan_id"]: verdict(self.p1)}
        d = law.select(snap([self.v3], self.st, records=[self.p1, self.p2], mbp_verdicts=mbp))
        self.assertNotIn("K2_DESK_DEBT", codes(d))                     # the MBP desk alone counts for line 9
        pending = verdict(self.p1, final=False)
        d = law.select(snap([self.v3], self.st, records=[self.p1, self.p2], mbp_verdicts={self.p1["plan_id"]: pending},
                            verdicts=mbp))
        self.assertNotIn("K2_DESK_DEBT", codes(d))                     # final by the off-host desk (a hand table)
        self.assertNotIn("DESK_DISAGREEMENT", codes(d))                # desk_final alone is not the automatic part
        other = {"doc": desk_final._finish({**{k: v for k, v in mbp[self.p1["plan_id"]]["doc"].items()
                                               if k != "verdict_sha256"}, "summary_sha256": "9" * 64})}
        d = law.select(snap([self.v3], self.st, records=[self.p1, self.p2], mbp_verdicts=mbp,
                            verdicts={self.p1["plan_id"]: other}))
        self.assertEqual(d.action, "halt")
        self.assertIn("DESK_DISAGREEMENT", codes(d))
        hold = verdict(self.p1, next_hold=True, holds=[{"code": "REFUSAL", "scope": "queue"}] + kit_holds(self.p1))
        d = law.select(snap([self.v3], self.st, records=[self.p1], mbp_verdicts={self.p1["plan_id"]: hold}))
        self.assertIn("DESK_HOLD", codes(d))                           # the MBP desk's hold holds too
        d = law.select(snap([self.v3], self.st, records=[self.p1],
                            mbp_verdicts={self.p1["plan_id"]: {"error": "TransportRefusal: x"}}))
        self.assertIn("DESK_VERDICT_INVALID", codes(d))

    def test_actions_watcher_each_arm_needs_a_successful_run_newer_than_the_last_close(self):
        wf = "mbp-watcher.yml"

        def run(started, conclusion="success", **over):
            return law.actions_run_view({"id": 1, "path": f".github/workflows/{wf}", "status": "completed",
                                         "conclusion": conclusion, "event": "schedule", "head_branch": "main",
                                         "run_started_at": datetime.fromtimestamp(started, law.ZONE).isoformat(),
                                         "updated_at": datetime.fromtimestamp(started + 30, law.ZONE).isoformat(),
                                         **over})
        close = NOW - 600
        self.assertEqual(law.actions_watcher_reasons(run(NOW - 300), NOW, close, wf), [])
        self.assertEqual(law.actions_watcher_reasons(run(NOW - 300), NOW, None, wf), [])
        for r, code in ((run(close - 1), "WATCHER_NOT_NEWER"), (run(close), "WATCHER_NOT_NEWER"),
                        (run(NOW - 300, "failure"), "WATCHER_FAILED"), (run(NOW - 300, None), "WATCHER_FAILED"),
                        (run(NOW - 300, status="in_progress"), "WATCHER_FAILED"),
                        (run(NOW - 300, path=".github/workflows/other.yml"), "WATCHER_FAILED"),
                        (run(NOW + 3600), "WATCHER_FAILED"), (run(NOW - 25 * 3600), "WATCHER_STALE"),
                        (run(NOW - 300, event="pull_request"), "WATCHER_FAILED"),        # gate 3, Opus 6
                        (run(NOW - 300, head_branch="feature"), "WATCHER_FAILED"),
                        (None, "WATCHER_RUN_MISSING"), ("unreadable", "WATCHER_UNREADABLE")):
            self.assertEqual([x["code"] for x in law.actions_watcher_reasons(r, NOW, close, wf)], [code], r)
        self.assertEqual(law.category(law.actions_watcher_reasons("unreadable", NOW, close, wf)), "retry")
        self.assertEqual(law.category(law.actions_watcher_reasons(run(close - 1), NOW, close, wf)), "wait")

    def test_the_offload_marker_must_verify_and_a_failure_holds_f0_too(self):
        pid = "cq-dev-05-s01-a1"
        self.assertEqual(law.offload_marker_problems(marker(pid), pid, NOW), [])
        for bad in (dict(marker(pid), plan_id="cq-x-a1"), marker(pid, ciphertext_bytes=0), marker(pid, verified=False),
                    marker(pid, upload={"confirmed": True, "readback": "size", "value": 1, "evidence": "e"}),
                    marker(pid, upload={"confirmed": False, "readback": "size", "value": 4096, "evidence": "e"}),
                    marker(pid, manifest_sha256="x"), dict(marker(pid), extra=1), "legacy text line"):
            self.assertTrue(law.offload_marker_problems(bad, pid, NOW), bad)
        self.assertTrue(law.offload_marker_problems(marker(pid, key_second_copy=None), pid, NOW))   # A.1: after 24 h
        early = datetime.fromtimestamp(law.KEY_SECOND_COPY_DEADLINE - 60, law.ZONE).isoformat()
        self.assertEqual(law.offload_marker_problems(marker(pid, key_second_copy=None, written_at=early), pid,
                                                     law.KEY_SECOND_COPY_DEADLINE), [])
        # gate 3 (Opus 3): bound to the span's own output and written after its receipt, not after the host clock
        src, after = f"/o/cl-dev-05/{pid}-20261117T160000Z", NOW - 600
        self.assertEqual(law.offload_marker_problems(marker(pid), pid, NOW, source=src, after=after), [])
        for bad in (marker(pid, source="/o/cl-dev-05/cq-dev-05-s00-a1-20261116T160000Z"),
                    marker(pid, written_at="2026-11-15T09:00:00-08:00"),
                    marker(pid, written_at="2027-11-17T09:00:00-08:00")):
            self.assertTrue(law.offload_marker_problems(bad, pid, NOW, source=src, after=after), bad)
        runs = law.build_runs(standing(), [record(pid, "05", L[:6], NOW - 9000)], [], kits=KITS)
        newest = f"/o/cl-dev-05/{pid}-20261117T160000Z/runner_receipt.json"
        census = {"newest": (int(NOW), newest), "campaign": [newest]}

        def got(markers, failures=()):
            return [r["code"] for r in law.census_reasons(census, runs, "/o", markers, now=NOW,
                                                          offload_failures=failures)]
        self.assertEqual(got({}), ["JOURNAL_COPY"])
        self.assertEqual(got({}, [pid]), ["OFFLOAD_FAILED"])
        self.assertEqual(got({pid: {"doc": None, "error": None, "failed": True}}), ["OFFLOAD_FAILED"])
        self.assertEqual(got({pid: {"doc": None, "error": "not JSON", "failed": False}}), ["OFFLOAD_FAILED"])
        self.assertEqual(got({pid: {"doc": marker(pid, verified=False), "error": None, "failed": False}}),
                         ["OFFLOAD_FAILED"])
        f0 = [{"kind": "F0", "standing_item": "item 346", "worst_case_s": 12180}]
        st = standing(fallback=f0)
        sn = snap([], st)
        self.assertEqual(law.select(sn).action, "page")                                 # F0 due with nothing queued
        sn["census_reasons"] = law.census_reasons(census, runs, "/o", {}, now=NOW, offload_failures=[pid])
        d = law.select(sn)
        self.assertEqual(d.action, "halt")                                              # A.7: F0 is held too
        self.assertNotIn("FALLBACK_F0_DUE", codes(d))
        sn["census_reasons"] = law.census_reasons(census, runs, "/o", {}, now=NOW)
        self.assertEqual(law.select(sn).action, "wait")                                 # an offload under way


class Gate3Law(unittest.TestCase):
    """Gate 3 (Opus 1, 5) on the law's side."""

    def test_the_copy_gate_is_per_span_and_holds_the_cede(self):
        pid = "cq-dev-05-s01-a1"
        runs = law.build_runs(standing(), [record(pid, "05", L[:6], NOW - 9000)], [], kits=KITS)
        newer = {"newest": (int(NOW), "/w/f0/runner_receipt.json"), "campaign": []}
        due = {pid: {"source": f"/o/cl-dev-05/{pid}-20261117T160000Z", "after": NOW - 600}}
        self.assertEqual([r["code"] for r in law.census_reasons(newer, runs, "/o", {}, now=NOW, copy_due=due)],
                         ["JOURNAL_COPY"])                      # a newer non-campaign receipt does not dissolve it
        good = {pid: {"doc": marker(pid), "error": None, "failed": False}}
        self.assertEqual(law.census_reasons(newer, runs, "/o", good, now=NOW, copy_due=due), [])
        st = standing()
        sn = snap([], st, sessions=[{"schema": law.SESSION_READY_SCHEMA, "session_id": "slot-1", "by": "lead",
                                     "ready_at": "2026-11-17T08:00:00-08:00"}])
        self.assertEqual(law.select(sn).action, "cede")
        sn["census_reasons"] = law.census_reasons(newer, runs, "/o", {}, now=NOW, copy_due=due)
        d = law.select(sn)
        self.assertEqual(d.action, "wait")
        self.assertIn("JOURNAL_COPY", codes(d))

    def test_a_disposition_does_not_lift_an_l002_timeout_and_a_missing_l002_summary_is_unknown(self):
        dev03 = kit("cl-dev-03.v1.1")
        kits = dict(KITS, **{"3" * 64: dev03})
        rec = record("cq-dev-03-s01-a1", "05", L[:3], NOW - 5 * 3600, closed=NOW - 4 * 3600)
        rec.update(kit_sha256="3" * 64, campaign_id="cl-dev-03", gates=law.derived_gates(dev03, L[:3]),
                   g0_unreleased=["L002"])
        for resolution in ("rerun", "withdrawn", "cleared"):
            st = standing(prior_spans=[], kits={sha: entry() for sha in kits},
                          dispositions=[{"plan_id": rec["plan_id"], "resolution": resolution, "record": "x"}])
            runs = law.build_runs(st, [rec], [], kits=kits)
            self.assertIn("L002_TIMEOUT", {r["code"] for r in law.l002_reasons(runs, st)}, resolution)


class Gate3LawMythos(unittest.TestCase):
    """Gate 3 (Mythos T1, T2, T3, T17) on the law's side."""

    def test_every_unreleased_outcome_counts_and_a_missing_record_of_a_leg_that_ran(self):
        roster = ["L001", "L002", "L003"]
        for outcome in ("timeout", "deadman", "unobserved", None, ""):
            self.assertIn("L002", law.unreleased({"L001": "released", "L002": outcome, "L003": "released"}, roster))
        self.assertEqual(law.unreleased({"L001": "released", "L002": "released", "L003": "released"}, roster), [])
        self.assertEqual(law.unreleased({"L001": "released", "L003": "released"}, roster), ["L002"])  # ran, no record
        self.assertEqual(law.unreleased({"L001": "released"}, roster), [])                           # never started

    def test_a_lead_record_is_judged_against_the_receipt_not_the_end_of_the_close_work(self):
        p1, rel = pilot_done("05")
        p1 = dict(p1, receipt_epoch=p1["closed_epoch"] - 900)     # the offload ran 15 min after the receipt
        st = standing(prior_spans=[], gate_records=rel)
        v3 = view([span(1, "dev-05-s03", "05", L[9:])], path="Q3.json")
        epochs = {(p1["plan_id"], g): p1["receipt_epoch"] + 60 for g in p1["gates"]}
        runs = law.build_runs(st, [p1], [], kits=KITS)
        sn = snap([v3], st, runs=runs)
        sn["record_epochs"] = epochs
        self.assertNotIn("GATE_RECORD_PREMATURE", codes(law.select(sn)))
        sn["record_epochs"] = {k: p1["receipt_epoch"] - 60 for k in epochs}
        self.assertIn("GATE_RECORD_PREMATURE", codes(law.select(sn)))

    def test_the_actions_run_must_be_this_repositorys(self):
        def run(**over):
            return law.actions_run_view({"id": 1, "path": ".github/workflows/w.yml", "status": "completed",
                                         "conclusion": "success", "event": "schedule", "head_branch": "main",
                                         "run_started_at": "2026-11-17T08:55:00-08:00",
                                         "updated_at": "2026-11-17T08:56:00-08:00",
                                         "head_repository": {"full_name": "o/r"}, **over})
        self.assertEqual(law.actions_watcher_reasons(run(), NOW, None, "w.yml", repo="o/r"), [])
        for bad in (run(head_repository={"full_name": "fork/r"}), run(event="workflow_dispatch"),
                    run(head_branch="patch-1")):
            self.assertEqual([r["code"] for r in law.actions_watcher_reasons(bad, NOW, None, "w.yml", repo="o/r")],
                             ["WATCHER_FAILED"])

    def test_a_foreign_run_waits_long_before_paging(self):
        self.assertEqual(law.stall_bound(["SPAN_LIVE"]), law.STALL_LONG_S)


if __name__ == "__main__":
    unittest.main()
