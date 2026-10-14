"""Pure queue desk tests; no files, sleeps, or processes."""
import unittest
from copy import deepcopy
from datetime import datetime

from joulewise.b6 import queue
from joulewise.b6.lanes import SessionLine
from tests.test_b6_registration import CATALOG, modular, registrations

NOW = datetime.fromisoformat("2026-10-14T00:00:00+00:00").timestamp()


def started(state, selection, status="counting", cause=None):
    state = queue.consume(state, selection)
    state.setdefault("attempts", []).append({"session_id": "s" + str(len(state.get("attempts", []))),
        "round": selection.round, "packs": list(selection.packs), "t0": NOW,
        "outcomes": {p: {"status": status, "cause": cause} for p in selection.packs}, "structure_ok": True})
    return state


class QueueTests(unittest.TestCase):
    def setUp(self):
        self.regs = registrations()
        self.state = {"round": 1, "packs": {}, "attempts": [], "base_order": ["alpha", "beta", "gamma"]}

    def test_rotation_and_nine_sessions_close(self):
        self.assertEqual([queue.rotation(self.state["base_order"], self.regs, i) for i in range(1, 5)],
                         [["alpha", "beta", "gamma"], ["beta", "gamma", "alpha"], ["gamma", "alpha", "beta"], ["alpha", "beta", "gamma"]])
        order = []
        state = self.state
        for _ in range(9):
            selected = queue.next_session(state, self.regs, NOW)
            order += selected.packs
            state = started(state, selected)
        self.assertEqual(order, ["alpha", "beta", "gamma", "beta", "gamma", "alpha", "gamma", "alpha", "beta"])
        self.assertIsInstance(queue.next_session(state, self.regs, NOW), queue.Close)

    def test_noncounting_retries_next_round_and_held_skips(self):
        state = started(self.state, queue.Selection(("alpha",), 1), "not_counting", "test")
        self.assertEqual(queue.next_session(state, self.regs, NOW).packs, ("beta",))
        state["packs"]["beta"] = {"status": "held"}
        self.assertEqual(queue.next_session(state, self.regs, NOW).packs, ("gamma",))
        state = started(state, queue.Selection(("gamma",), 1))
        self.assertEqual(queue.next_session(state, self.regs, NOW), queue.Selection(("gamma",), 2))
        state = started(state, queue.Selection(("gamma",), 2))
        self.assertEqual(queue.next_session(state, self.regs, NOW).packs, ("alpha",))

    def test_resume_joins_unused_slot_midround(self):
        state = started(self.state, queue.Selection(("alpha",), 1))
        state["packs"]["beta"] = {"status": "held"}
        state = queue.resume(state, "beta", 7)
        self.assertEqual(queue.next_session(state, self.regs, NOW), queue.Selection(("beta",), 1))
        self.assertEqual(state["packs"]["beta"]["attempt_limit"], 7)

    def test_pause_five_resume_and_same_cause_only_that_pack(self):
        state = self.state
        for i in range(5):
            state = started(state, queue.Selection(("alpha",), i+1), "not_counting", f"cause{i}")
        state, events = queue.rotate(state, self.regs)
        self.assertEqual(events, [("pack_paused", "alpha")])
        state = queue.resume(state, "alpha", 2)
        self.assertEqual(state["packs"]["alpha"]["attempts_since_resume"], 0)
        for i in (6, 7):
            state = started(state, queue.Selection(("alpha",), i), "physics_stopped", "thermal")
        state, events = queue.rotate(state, self.regs)
        self.assertEqual(events, [("same_cause_twice", "alpha")])
        self.assertEqual(queue.next_session(state, self.regs, NOW).packs, ("beta",))

    def test_target_end_short_and_precision_minimum(self):
        state = self.state
        state["packs"]["alpha"] = {"precision_reached": True}
        self.assertIsNone(queue.done_reason(state, self.regs["alpha"], NOW))
        for i in range(2):
            state = started(state, queue.Selection(("alpha",), i+1))
        self.assertEqual(queue.done_reason(state, self.regs["alpha"], NOW), "precision")
        self.assertEqual(queue.done_reason(state, self.regs["beta"], NOW + 30*86400), "short:0")
        state = started(state, queue.Selection(("alpha",), 3))
        self.assertEqual(queue.done_reason(state, self.regs["alpha"], NOW), "target")

    def test_pending_reharvest_and_pack_scoped_effects(self):
        state = started(self.state, queue.Selection(("alpha",), 1), "pending_harvest")
        self.assertEqual(queue.counting_ids(state, "alpha"), [])
        state["reharvested"] = {"s0": {"alpha": {"status": "counting", "cause": None}}}
        self.assertEqual(queue.counting_ids(state, "alpha"), ["s0"])
        line = SessionLine("s", ("alpha", "beta"), window_flags=("disk.low",),
                           pack_flags={"alpha": ["model.identity_mismatch"]})
        self.assertEqual(queue.outcome(self.regs["alpha"], line, CATALOG)["status"], "not_counting")
        self.assertEqual(queue.outcome(self.regs["beta"], line, CATALOG)["status"], "counting")

    def test_modular_whole_units_and_fixed_not_colocated(self):
        regs = {p: modular(p) for p in ("alpha", "beta")}
        self.assertEqual(queue.next_session(self.state, regs, NOW).packs, ("alpha",))
        state = deepcopy(self.state)
        state["science_minutes_max"] = 480
        self.assertEqual(queue.next_session(state, regs, NOW).packs, ("alpha", "beta"))
        regs["alpha"] = self.regs["alpha"]
        self.assertEqual(queue.next_session(state, regs, NOW).packs, ("alpha",))
        state["science_minutes_max"] = 100
        regs = {p: modular(p) for p in ("alpha", "beta")}
        self.assertIsInstance(queue.next_session(state, regs, NOW), queue.Idle)

    def test_idle_held_and_new_commit_order_and_pure(self):
        state = deepcopy(self.state)
        state["packs"] = {p: {"status": "held"} for p in self.regs}
        self.assertIsInstance(queue.next_session(state, self.regs, NOW), queue.Idle)
        before = deepcopy(self.state)
        queue.next_session(self.state, self.regs, NOW)
        self.assertEqual(before, self.state)
