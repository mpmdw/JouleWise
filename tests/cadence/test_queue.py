"""Queue format, derived span states, the chaining decision, vetoes and halts."""
from __future__ import annotations

import copy
import unittest

from joulewise.cadence import kit as kitmod, queue as q
from tests.cadence.fixtures import kit_bytes, make_kit, make_queue

PATH = "configs/campaigns/conditionless-test/campaign_kit.json"
OK = {"outcome": "MEASURED_OK", "chain_exit_code": 0, "fault": False}
NOW = 1_795_000_000.0


class Format(unittest.TestCase):
    def setUp(self):
        self.kit = kitmod.validate_kit(make_kit())
        _, self.sha = kit_bytes(self.kit)
        self.kits = {PATH: (self.kit, self.sha)}

    def refused(self, doc, fragment, kits=None):
        with self.assertRaises(q.QueueError) as ctx:
            q.validate_queue(doc, kits if kits is not None else self.kits)
        self.assertTrue(any(fragment in p for p in ctx.exception.problems), ctx.exception.problems)

    def test_valid_queue_and_plan_ids(self):
        doc = q.validate_queue(make_queue(self.kit, self.sha), self.kits)
        self.assertEqual([q.plan_id(s) for s in doc["spans"]], ["cq-ct-s01-a1", "cq-ct-s02-a1"])

    def test_refusals(self):
        doc = make_queue(self.kit, self.sha); doc["spans"][1]["seq"] = 1
        self.refused(doc, "strictly increasing")
        doc = make_queue(self.kit, self.sha); doc["spans"][0]["kit"]["sha256"] = "0" * 64
        self.refused(doc, "pinned")
        doc = make_queue(self.kit, self.sha); doc["spans"][0]["legs"] = ["L002", "L001"]
        self.refused(doc, "seeded order")
        doc = make_queue(self.kit, self.sha); doc["spans"][1]["legs"] = ["L003"]
        self.refused(doc, "already in span")
        doc = make_queue(self.kit, self.sha); doc["spans"][0]["legs"].append("L999")
        self.refused(doc, "not in the kit")
        doc = make_queue(self.kit, self.sha); doc["expires_at"] = "2026-12-31T00:00:00"
        self.refused(doc, "explicit offset")
        doc = make_queue(self.kit, self.sha); doc["spans"][0]["command"] = "rm -rf /"
        self.refused(doc, "unknown key 'command'")

    def test_rerun_must_name_an_earlier_span(self):
        doc = make_queue(self.kit, self.sha)
        rerun = copy.deepcopy(doc["spans"][0]); rerun.update(seq=3, span_id="ct-s01r", attempt=2, rerun_of="ct-s01")
        doc["spans"].append(rerun)
        q.validate_queue(doc, self.kits)
        rerun["rerun_of"] = "nope"
        self.refused(doc, "rerun_of")


class Chaining(unittest.TestCase):
    def setUp(self):
        kit = make_kit(n_legs=9)
        _, sha = kit_bytes(kit)
        self.queue = q.validate_queue(make_queue(kit, sha))
        self.p = [q.plan_id(s) for s in self.queue["spans"]]

    def act(self, ev, halts=(), now=NOW):
        return q.next_action(self.queue, ev, halts, now)

    def test_walk_of_a_clean_chain(self):
        d = self.act({})
        self.assertEqual((d.action, d.span["span_id"]), ("arm", "ct-s01"))
        d = self.act({"armed": [self.p[0]]})
        self.assertEqual(d.action, "wait")
        d = self.act({"armed": [self.p[0]], "results": {self.p[0]: OK}})
        self.assertEqual((d.action, d.span["span_id"]), ("close", "ct-s01"))
        ev = {"armed": [self.p[0]], "results": {self.p[0]: OK}, "closed": {self.p[0]: {"stops": []}}}
        d = self.act(ev)
        self.assertEqual((d.action, d.span["span_id"]), ("arm", "ct-s02"))
        # Idempotent: the same evidence gives the same decision.
        self.assertEqual(self.act(ev).as_dict(), d.as_dict())

    def test_go_with_nonzero_exit_is_a_refusal_and_never_chains(self):
        ev = {"armed": [self.p[0]], "results": {self.p[0]: {"outcome": "REFUSED", "chain_exit_code": 3,
                                                            "fault": False, "verdict": "GO"}}}
        d = self.act(ev)
        self.assertEqual(d.action, "halt")
        self.assertEqual(d.states["ct-s01"], q.REFUSED)

    def test_fault_and_named_stop_halt(self):
        ev = {"results": {self.p[0]: {**OK, "fault": True}}}
        self.assertEqual(self.act(ev).states["ct-s01"], q.FAULT)
        ev = {"results": {self.p[0]: OK}, "closed": {self.p[0]: {"stops": [{"code": "LEG_OVERTIME"}]}}}
        d = self.act(ev)
        self.assertEqual((d.action, d.states["ct-s01"]), ("halt", q.STOPPED))

    def test_stranded_when_past_deadline_without_results(self):
        ev = {"armed": [self.p[0]], "deadlines": {self.p[0]: NOW - 1}}
        self.assertEqual(self.act(ev).states["ct-s01"], q.STRANDED)
        self.assertEqual(self.act(ev).action, "halt")

    def test_k_plus_2_desk_finality(self):
        closed = {p: {"stops": []} for p in self.p[:2]}
        ev = {"results": {p: OK for p in self.p[:2]}, "closed": closed}
        d = self.act(ev)
        self.assertEqual(d.action, "wait")
        self.assertIn("k+2", d.reasons[0])
        d = self.act({**ev, "desk_final": [self.p[0]]})
        self.assertEqual((d.action, d.span["span_id"]), ("arm", "ct-s03"))

    def test_drained_halt_expiry(self):
        ev = {"results": {p: OK for p in self.p}, "closed": {p: {"stops": []} for p in self.p}}
        self.assertEqual(self.act(ev).action, "drained")
        self.assertEqual(self.act({}, now=q.parse_time("2027-01-01T00:00:00-08:00")).action, "halt")
        queue = copy.deepcopy(self.queue); queue["halt"] = {"reason": "r", "by": "lead", "at": "x"}
        self.assertEqual(q.next_action(queue, {}, (), NOW).action, "halt")

    def test_transitions_table(self):
        self.assertTrue(q.legal(q.QUEUED, q.ARMED))
        self.assertTrue(q.legal(q.EXITED, q.CLOSED_OK))
        self.assertFalse(q.legal(q.REFUSED, q.ARMED))
        self.assertFalse(q.legal(q.QUEUED, q.CLOSED_OK))
        for state in q.BAD_TERMINAL | {q.CLOSED_OK}:
            self.assertEqual(q.TRANSITIONS[state], set())


class Halts(unittest.TestCase):
    def setUp(self):
        kit = make_kit()
        _, sha = kit_bytes(kit)
        self.queue = q.validate_queue(make_queue(kit, sha))

    def issue(self, title, labels=("directive",), body="", login="mpmdw", state="OPEN", number=5):
        return {"number": number, "title": title, "body": body, "author": {"login": login},
                "labels": [{"name": l} for l in labels], "state": state}

    def test_veto_scopes_and_authority(self):
        H = lambda *i: q.halts_from_issues(list(i), self.queue)
        self.assertEqual(H(self.issue("NO: stop the cadence queue"))[0]["scope"], "queue")
        self.assertEqual(H(self.issue("VETO ct-s02"))[0]["scope"], "ct-s02")
        self.assertEqual(H(self.issue("VETO cq-ct-1"))[0]["scope"], "queue")
        self.assertEqual(H(self.issue("x", body="STOP all\nmore")), [{"scope": "queue", "source": "directive-veto", "issue": 5}])
        self.assertEqual(H(self.issue("NO", login="someone-else")), [])
        self.assertEqual(H(self.issue("NO queue", state="CLOSED")), [])
        self.assertEqual(H(self.issue("please continue the queue")), [])
        self.assertEqual(H(self.issue("CADENCE STOP x", labels=("cadence-stop",)))[0]["source"], "cadence-stop")

    def test_span_veto_halts_at_that_span(self):
        halts = q.halts_from_issues([self.issue("VETO ct-s01")], self.queue)
        d = q.next_action(self.queue, {}, halts, NOW)
        self.assertEqual((d.action, d.span["span_id"]), ("halt", "ct-s01"))


if __name__ == "__main__":
    unittest.main()
