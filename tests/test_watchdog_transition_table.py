"""RL-53 W-6 / RL-108 condition 6: the watchdog transition table as bound data.

Fakes only (tests.test_magistrate_watchdog's Storage/Dependencies harness under the
suite-wide host-command guard): no real process table, no signal, no launchctl.
"""
from __future__ import annotations

import ast
import datetime as dt
import inspect
import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import magistrate_watchdog as wd
from tests.test_magistrate_watchdog import WatchdogTestCase

SOURCE = Path(wd.__file__).read_text(encoding="utf-8")
TABLE_JSON = json.loads(wd.TRANSITION_TABLE_PATH.read_text(encoding="utf-8"))

# The audit's mermaid edges (implicit-state-machines.md section 4.3) and the supervisor edges.
AUDIT_EDGES = (
    ("BOOT", "LAUNCHING"), ("LAUNCHING", "ACTIVE"), ("ACTIVE", "IDLE"), ("ACTIVE", "STANDDOWN_REQUESTED"),
    ("STANDDOWN_REQUESTED", "FENCED"), ("STANDDOWN_REQUESTED", "HOLD_CENSUS"), ("FENCED", "LAUNCHING"),
    ("IDLE", "LAUNCHING"), ("LAUNCHING", "BACKOFF"), ("BACKOFF", "LAUNCHING"), ("BOOT", "HOLD_UNSAFE"),
    ("FENCED", "HOLD_UNSAFE"), ("HOLD_UNSAFE", "LAUNCHING"), ("BOOT", "STOPPED"), ("BOOT", "CLOCK_UNCERTAIN"),
    ("BOOT", "NETWORK_UNCERTAIN"),
    ("ACTIVE", "STOP_REQUESTED"), ("STOP_REQUESTED", "FENCED"), ("STANDDOWN_REQUESTED", "STANDDOWN_TERM"),
    ("STANDDOWN_TERM", "STANDDOWN_KILL"), ("STANDDOWN_TERM", "FENCED"), ("ACTIVE", "BACKOFF_USAGE"),
)
# Every edge the existing watchdog test modules drive (recorded once on this branch by instrumenting
# transition(); BOOT->IDLE is a fixture artifact: a supervisor built directly from initial_state()).
OBSERVED_EDGES = tuple(tuple(edge.split("->")) for edge in """
BOOT->HOLD_LOCK BOOT->FENCED BOOT->LAUNCHING HOLD_UNSAFE->HOLD_LOCK BOOT->ACTIVE ACTIVE->HOLD_PLIST_UNREADABLE
ACTIVE->FENCED STANDDOWN_TERM->FENCED ACTIVE->HOLD_PLAN_UNREADABLE BOOT->HOLD_PLAN_MALFORMED
HOLD_PLAN_UNREADABLE->FENCED FENCED->STOPPED FENCED->LAUNCHING ACTIVE->STANDDOWN_REQUESTED
ACTIVE->NETWORK_UNCERTAIN ACTIVE->IDLE STANDDOWN_REQUESTED->STANDDOWN_TERM LAUNCHING->FENCED
HOLD_PLIST_UNREADABLE->FENCED HOLD_PLAN_MALFORMED->STRANDED BOOT->HOLD_CENSUS ACTIVE->STANDDOWN_TERM
ACTIVE->HOLD_PLAN_MALFORMED ACTIVE->HOLD_MODEL_REJECTED ACTIVE->HOLD_CONFLICT ACTIVE->BACKOFF_USAGE
ACTIVE->BACKOFF STANDDOWN_REQUESTED->FENCED NETWORK_UNCERTAIN->STANDDOWN_TERM
NETWORK_UNCERTAIN->STANDDOWN_REQUESTED NETWORK_UNCERTAIN->HOLD_PLAN_UNREADABLE LAUNCHING->BACKOFF
LAUNCHING->ACTIVE IDLE->STOPPED IDLE->HOLD_PLAN_UNREADABLE IDLE->FENCED IDLE->ACTIVE HOLD_UNSAFE->FENCED
HOLD_PLAN_MALFORMED->FENCED HOLD_PLAN_MALFORMED->ACTIVE HOLD_LOCK->HOLD_PLAN_UNREADABLE HOLD_LOCK->ACTIVE
FENCED->IDLE CLOCK_UNCERTAIN->FENCED BOOT->STANDDOWN_TERM BOOT->NETWORK_UNCERTAIN BOOT->HOLD_PLIST_UNREADABLE
BOOT->HOLD_MODEL_REJECTED BOOT->CLOCK_UNCERTAIN ACTIVE->HOLD_UNSAFE ACTIVE->HOLD_LOCK ACTIVE->CLOCK_UNCERTAIN
""".split())


def _function(name):
    tree = ast.parse(SOURCE)
    return next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == name)


def _constants(node):
    return {n.value for n in ast.walk(node) if isinstance(n, ast.Constant) and isinstance(n.value, str)}


def state_literals():
    """Every state name the module can hand to transition() or return as a Decision."""
    names = set(wd.UNSAFE_STATES) | {wd.initial_state()["state"]}
    for node in ast.walk(ast.parse(SOURCE)):
        if not isinstance(node, ast.Call):
            continue
        func = node.func.id if isinstance(node.func, ast.Name) else getattr(node.func, "attr", None)
        if func == "Decision" and node.args:
            names |= {v for v in _constants(node.args[0]) if re.fullmatch(r"[A-Z][A-Z_]*[A-Z]", v)}
        if func == "transition" and len(node.args) >= 3:
            names |= {v for v in _constants(node.args[2]) if re.fullmatch(r"[A-Z][A-Z_]*[A-Z]", v)}
        for keyword in node.keywords:
            if keyword.arg == "state_name":
                names |= {v for v in _constants(keyword.value) if re.fullmatch(r"[A-Z][A-Z_]*", v)}
    names |= {v for v in _constants(_function("_unsafe_state")) if re.fullmatch(r"HOLD_[A-Z_]+", v)}
    # _decide's f"STANDDOWN_{phase}" over standdown_phase's return words.
    phases = {r.value.value for r in ast.walk(_function("standdown_phase"))
              if isinstance(r, ast.Return) and isinstance(r.value, ast.Constant) and r.value.value}
    names |= {f"STANDDOWN_{phase}" for phase in phases}
    return names


class TableShapeTests(unittest.TestCase):
    def test_table_parses_and_groups_match_the_module(self):
        table = wd._parse_transition_table(wd.TRANSITION_TABLE_PATH.read_bytes())
        self.assertEqual(wd.UNSAFE_STATES, table["unsafe_holds"])
        hold_set = next(n for n in ast.walk(_function("_hold_boundaries")) if isinstance(n, ast.BinOp))
        self.assertEqual(_constants(hold_set.left) | wd.UNSAFE_STATES, table["timing_holds"])
        self.assertEqual("BOOT", TABLE_JSON["initial_state"])
        self.assertFalse(set(table["dwell_limits_s"]) & table["unsafe_holds"])

    def test_every_state_literal_in_the_module_is_declared(self):
        literals = state_literals()
        self.assertTrue({"STANDDOWN_REQUEST", "STANDDOWN_KILL", "STOP_REQUESTED", "IDLE", "HOLD_DESK_FENCE",
                         "HOLD_STATUS_EXPORT", "HOLD_MODEL_CHECK", "BACKOFF_USAGE"} <= literals)
        self.assertEqual(set(), literals - set(TABLE_JSON["states"]))
        self.assertEqual(set(), set(TABLE_JSON["states"]) - literals, "declared state no code enters")

    def test_audit_supervisor_and_observed_edges_are_declared(self):
        table = wd.transition_table()
        for old, new in AUDIT_EDGES + OBSERVED_EDGES:
            if (old, new) == ("BOOT", "IDLE"):
                continue
            with self.subTest(edge=f"{old}->{new}"):
                self.assertTrue(wd.declared_edge(table, old, new))
        self.assertFalse(wd.declared_edge(table, "BOOT", "IDLE"))   # supervisor-only target
        self.assertFalse(wd.declared_edge(table, "BACKOFF", "STOP_REQUESTED"))
        self.assertFalse(wd.declared_edge(table, "ACTIVE", "NOT_A_STATE"))

    def test_dwell_limits_follow_their_basis_constants(self):
        interval = wd.LAUNCHD_START_INTERVAL_S
        expected = {
            "LAUNCHING": wd.LAUNCH_LIVENESS_S,
            "ACTIVE": 86400,
            "IDLE": 300 + interval,
            "BACKOFF": max(wd.GENERIC_BACKOFF_S) + interval,
            "BACKOFF_USAGE": max(wd.USAGE_BACKOFF_S) + 120 + interval,
            "STANDDOWN_REQUEST": wd.REQUEST_LEAD_S - wd.TERM_LEAD_S + interval,
            "STANDDOWN_REQUESTED": wd.REQUEST_LEAD_S - wd.TERM_LEAD_S + interval,
            "STANDDOWN_TERM": wd.TERM_LEAD_S - wd.KILL_LEAD_S + interval,
            "STANDDOWN_KILL": wd.KILL_LEAD_S + interval,
            "STOP_REQUESTED": wd.STOP_COOPERATIVE_S + wd.STOP_TERM_GRACE_S + interval,
        }
        self.assertEqual(expected, wd.transition_table()["dwell_limits_s"])
        self.assertEqual(120, max(wd.jitter_for_activation(str(n)) for n in range(5000)))
        template = (wd.REPO_ROOT / "configs/launchd/com.joulewise.magistrate.plist.template").read_text()
        self.assertRegex(template, r"<key>StartInterval</key>\s*<integer>%d</integer>" % interval)

    def test_strict_parse_refuses_unknown_and_malformed_rows(self):
        base = json.loads(json.dumps(TABLE_JSON))
        cases = {
            "extra key": {**base, "tolerant": True},
            "schema": {**base, "schema": "v0"},
            "dwell on unsafe hold": {**base, "dwell_limits_s": {**base["dwell_limits_s"],
                                                                 "HOLD_UNSAFE": {"limit_s": 1, "basis": "x"}}},
            "zero limit": {**base, "dwell_limits_s": {"ACTIVE": {"limit_s": 0, "basis": "x"}}},
            "undeclared group member": {**base, "tick_targets": [*base["tick_targets"], "NOPE"]},
        }
        for name, value in cases.items():
            with self.subTest(case=name), self.assertRaises(wd.TransitionTableError):
                wd._parse_transition_table(json.dumps(value).encode())
        with self.assertRaises(wd.TransitionTableError):
            wd._parse_transition_table(b"{not json")


class TableBehaviourTests(WatchdogTestCase):
    def events(self, kind):
        path = self.harness.storage.root / "events.jsonl"
        if not path.exists():
            return []
        return [row for row in map(json.loads, path.read_text().splitlines()) if row.get("kind") == kind]

    def notices(self, state, kind):
        return [item for item in state.get("notice_pending", []) if item.get("kind") == kind]

    def test_undeclared_edge_is_recorded_and_noticed_but_still_taken(self):
        for target in ("IDLE", "NOT_A_STATE"):
            with self.subTest(target=target):
                state = wd.initial_state()
                wd.transition(self.harness.storage, state, target, "synthetic", self.base)
                self.assertEqual(target, state["state"])
                ids = [n["id"] for n in self.notices(state, "undeclared_transition")]
                self.assertEqual([f"undeclared-transition-BOOT-{target}"], ids)
                state["state"] = "BOOT"   # the same edge again: one notice per edge
                wd.transition(self.harness.storage, state, target, "again", self.base)
                self.assertEqual(ids, [n["id"] for n in self.notices(state, "undeclared_transition")])
        self.assertEqual([("BOOT", "IDLE")] * 2 + [("BOOT", "NOT_A_STATE")] * 2,
                         [(row["from"], row["to"]) for row in self.events("undeclared_transition")])

    def test_declared_edge_adds_nothing(self):
        state = wd.initial_state()
        wd.transition(self.harness.storage, state, "LAUNCHING", "clear", self.base)
        wd.transition(self.harness.storage, state, "ACTIVE", "spawned", self.base)
        self.assertEqual([], self.events("undeclared_transition"))
        self.assertEqual([], state.get("notice_pending", []))

    def test_dwell_expiry_notices_once_and_changes_nothing(self):
        limits = wd.transition_table()["dwell_limits_s"]
        for name in ("ACTIVE", "BACKOFF", "LAUNCHING", "STANDDOWN_TERM", "STANDDOWN_REQUESTED", "STOP_REQUESTED"):
            with self.subTest(state=name):
                state = wd.initial_state()
                state.update(state=name, transition_seq=7,
                             transition_epoch_s=self.base.timestamp() - limits[name] + 5)
                wd.transition(self.harness.storage, state, name, "same", self.base)
                self.assertEqual({"state": name, "since_epoch_s": state["transition_epoch_s"],
                                  "limit_s": limits[name], "exceeded": False}, state["dwell"])
                self.assertEqual([], self.notices(state, "dwell_exceeded"))
                later = self.base + dt.timedelta(seconds=10)
                for _ in range(3):
                    wd.transition(self.harness.storage, state, name, "same", later)
                self.assertEqual(name, state["state"])
                self.assertEqual(7, state["transition_seq"])
                self.assertTrue(state["dwell"]["exceeded"])
                self.assertEqual(1, len(self.notices(state, "dwell_exceeded")))
                wd.transition(self.harness.storage, state, "FENCED", "moved", later)
                self.assertNotIn("dwell", state)
        self.assertEqual(6, len(self.events("dwell_exceeded")))
        self.assertEqual([], self.harness.processes.signals)
        self.assertEqual([], self.harness.spawn_calls)

    def test_backoff_tick_past_its_dwell_neither_launches_nor_signals(self):
        state = wd.initial_state()
        state.update(state="BACKOFF", transition_seq=3, transition_epoch_s=self.base.timestamp() - 7200,
                     next_eligible_epoch_s=self.base.timestamp() + 600, next_eligible_monotonic=5000.0,
                     backoff_boot_id="boot-a")
        self.harness.storage.atomic_json(self.harness.storage.root / "state.json", state)
        with mock.patch.object(wd, "current_boot_id", return_value="boot-a"), \
                mock.patch.object(wd.os, "fork", side_effect=AssertionError("tick must not fork")):
            decision = wd.tick(self.harness.storage, self.harness.deps)
        self.assertEqual("BACKOFF", decision.state)
        self.assertFalse(decision.launch)
        saved = json.loads((self.harness.storage.root / "state.json").read_text())
        self.assertEqual("BACKOFF", saved["state"])
        self.assertTrue(saved["dwell"]["exceeded"])
        self.assertEqual(1, len(self.notices(saved, "dwell_exceeded")))
        self.assertEqual([], self.harness.spawn_calls)
        self.assertEqual([], self.harness.processes.signals)

    def test_active_supervisor_step_past_its_dwell_keeps_the_session(self):
        supervisor = self.supervisor(self.make_plan(t0=self.base.timestamp() + 86400 * 3))
        supervisor.state.update(transition_seq=4, transition_epoch_s=self.base.timestamp() - 90000)
        supervisor._remote_stop = wd.StopObservation("CLEAR", "clear")
        supervisor._remote_probe_started_monotonic = self.harness.clock.mono
        self.assertTrue(supervisor.step(publish_background=False))
        self.assertEqual("ACTIVE", supervisor.state["state"])
        self.assertEqual(1, len(self.notices(supervisor.state, "dwell_exceeded")))
        self.assertEqual([], self.harness.processes.signals)
        self.assertFalse((self.harness.storage.root / "standdown.request").exists())

    def test_unsafe_hold_keeps_stranded_and_has_no_dwell_row(self):
        state = wd.initial_state()
        state["unsafe_hold"] = {"since_epoch_s": self.base.timestamp() - wd.UNSAFE_HOLD_DWELL_S,
                                "since_monotonic": self.harness.clock.mono - wd.UNSAFE_HOLD_DWELL_S}
        decision = wd._surface_unsafe_decision(self.harness.storage, self.harness.deps, state,
                                               wd.Decision("HOLD_UNSAFE", "night_plan_unreadable: x"), self.base)
        self.assertEqual("STRANDED", decision.state)
        self.assertFalse(decision.launch)
        state.update(state="HOLD_PLAN_UNREADABLE", transition_epoch_s=0.0)
        wd.transition(self.harness.storage, state, "HOLD_PLAN_UNREADABLE", "same", self.base)
        self.assertNotIn("dwell", state)
        self.assertEqual([], self.notices(state, "dwell_exceeded"))

    def test_open_chain_past_completion_keeps_the_fence_and_notices_once(self):
        plan = self.make_plan(t0=self.base.timestamp() - 7200, authored_epoch_s=self.base.timestamp() - 9000)
        night = Path(plan.custody_root) / "night"
        night.mkdir()
        (night / "chain.started").write_text("{}", encoding="utf-8")
        self.assertGreater(self.base.timestamp(), wd.plan_completion_epoch(plan))
        state = wd.initial_state()
        for _ in range(2):
            decision = wd.decide(self.harness.storage, self.harness.deps, state)
            self.assertEqual("FENCED", decision.state)
            self.assertFalse(decision.launch)
        self.assertEqual(1, len(self.notices(state, "chain_open_past_completion")))
        self.assertEqual([plan.plan_id], [row["plan_id"] for row in self.events("chain_open_past_completion")])
        (night / "chain.exited").write_text("{}", encoding="utf-8")
        state = wd.initial_state()
        wd.decide(self.harness.storage, self.harness.deps, state)
        self.assertEqual([], self.notices(state, "chain_open_past_completion"))

    def test_open_chain_within_completion_has_no_notice(self):
        plan = self.make_plan(t0=self.base.timestamp() - 60, authored_epoch_s=self.base.timestamp() - 3600)
        night = Path(plan.custody_root) / "night"
        night.mkdir()
        (night / "chain.started").write_text("{}", encoding="utf-8")
        state = wd.initial_state()
        self.assertEqual("FENCED", wd.decide(self.harness.storage, self.harness.deps, state).state)
        self.assertEqual([], self.notices(state, "chain_open_past_completion"))


class TableUnavailableTests(WatchdogTestCase):
    def use_table(self, path):
        patch = mock.patch.object(wd, "TRANSITION_TABLE_PATH", path)
        patch.start()
        cache = dict(wd._TABLE_CACHE)
        wd._TABLE_CACHE.clear()

        def restore():
            patch.stop()
            wd._TABLE_CACHE.clear()
            wd._TABLE_CACHE.update(cache)
        self.addCleanup(restore)

    def test_malformed_or_unreadable_table_holds_and_never_raises(self):
        bad = self.temp / "table.json"
        for name, content in (("malformed", '{"schema": "x"}'), ("unreadable", None)):
            with self.subTest(case=name):
                if content is not None:
                    bad.write_text(content, encoding="utf-8")
                else:
                    bad.unlink(missing_ok=True)
                self.use_table(bad)
                state = wd.initial_state()
                decision = wd.decide(self.harness.storage, self.harness.deps, state)
                self.assertEqual("HOLD_UNSAFE", decision.state)
                self.assertTrue(decision.reason.startswith(wd.TRANSITION_TABLE_REASON + " " + name))
                self.assertEqual("HOLD_UNSAFE", wd._unsafe_state(decision.reason))
                self.assertFalse(decision.launch)
                wd.transition(self.harness.storage, state, "IDLE", "no table", self.base)
                wd.transition(self.harness.storage, state, "IDLE", "no table", self.base)
                self.assertEqual("IDLE", state["state"])
                self.assertEqual([], [n for n in state.get("notice_pending", [])
                                      if n.get("kind") in ("undeclared_transition", "dwell_exceeded")])


if __name__ == "__main__":
    unittest.main()
