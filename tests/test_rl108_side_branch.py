"""RL-108 side branch (NOT FOR MERGE): exit contract, one restore_owed(), the window journal.

Condition 2: ``ExitContractTableTests`` compares the driver's ``_chain_outcome`` against a verbatim copy of the
function at a6a09e6d7 for every declared code of every chain contract, and for undeclared codes.
Condition 3: ``TerminalHostEndStateTests`` drives each terminal path of ``run_night`` under fakes (the suite-wide
host-command guard stays installed by ``tests/__init__.py``; no real pmset/systemsetup/sudo/kill is reached:
the probe seam is faked and ``os.killpg`` is replaced by a tripwire). ``GOLDEN`` was captured by running this
same class on an unmodified a6a09e6d7 checkout; ``python3.13 -B -m unittest tests.test_rl108_side_branch
-k TerminalHostEndState`` passes there too (``RL108_BASE=1`` skips the branch-only assertions).
Condition 4: ``WindowJournalTests``.
"""
from __future__ import annotations

import ast
import json
import os
import re
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

from tests import test_run_night as trn
from joulewise import night_gate

BASE = os.environ.get("RL108_BASE") == "1"
NETWORK_TIME_ON_ARGV = ("/usr/bin/sudo", "-n", "/usr/sbin/systemsetup", "-setusingnetworktime", "on")
NETWORK_TIME_QUERY_ARGV = ("/usr/bin/sudo", "-n", "/usr/sbin/systemsetup", "-getusingnetworktime")
OFF_ARGV = ["/usr/bin/sudo", "-n", "/usr/sbin/systemsetup", "-setusingnetworktime", "off"]


def _chain_outcome_a6a09e6d7(rt, plan, night_dir, verdict, chain_exit_code, aborted_reason=None):
    """Verbatim body of scripts/run_night.py:_chain_outcome at a6a09e6d7 (only ``rt.`` added)."""
    reasons = []
    started = (night_dir / "chain.started").exists()
    payload = night_dir / "align-r1" / "r1_result.json"
    is_r1 = (str(plan.plan_id).startswith("align-r1-")
             or "align_r1_rehearsal" in str(getattr(plan, "chain_path", ""))
             or payload.exists())
    status = None
    refusal = {"chain_refused_phase": None, "chain_refusal_codes": []}
    if is_r1 and started:
        try:
            raw = json.loads(payload.read_text(encoding="utf-8"))
            status = raw.get("status") if isinstance(raw, dict) else None
            if status not in ("complete", "refused", "aborted", "running"):
                status = "invalid"
            if status in ("refused", "aborted"):
                try:
                    refusal = rt._r1_refusal_summary(raw)
                except Exception:  # noqa: BLE001
                    pass
        except FileNotFoundError:
            status = "absent"
        except (OSError, ValueError):
            status = "unreadable"
        if status != "complete":
            reasons.append("r1_status:" + status)
    if chain_exit_code not in (0, None):
        reasons.append(f"chain_exit_nonzero:{chain_exit_code}")
    if verdict == "REFUSED" and not started:
        outcome = "REFUSED_PRE_CHAIN"
        reasons.append("refusal:" + str(aborted_reason or "unknown"))
    elif verdict == "ABORTED":
        outcome = "ABORTED"
        reasons.append("abort:" + str(aborted_reason or "unknown"))
    elif reasons or verdict in ("REFUSED", "CHAIN_STOPPED"):
        outcome = "CHAIN_FAILED"
        if not reasons:
            reasons.append("chain_verdict:" + verdict)
    elif started and chain_exit_code == 0:
        outcome = "COMPLETE"
    else:
        outcome = "UNKNOWN"
    return {"chain_outcome": outcome, "measurement_outcome": status, **refusal,
            "fault": bool(reasons), "fault_reasons": reasons}


@unittest.skipIf(BASE, "branch-only")
class ExitContractTableTests(unittest.TestCase):
    """RL-108 condition 2: identical fault reasons for every declared code; undeclared keep chain_exit_nonzero."""

    UNDECLARED = (1, 2, 5, 6, 7, 9, 14, 63, 65, 74, 76, 99, 126, 127, 128, 129, 130, 137, 143, 255, 256, 1000,
                  -1, -2, -9, -15)

    @classmethod
    def setUpClass(cls):
        from tests.test_run_night import _load_driver
        from joulewise import exit_contract
        cls.rt, cls.ec = _load_driver(), exit_contract

    def plans(self):
        return {
            "r1_driver": types.SimpleNamespace(plan_id="align-r1-20261113T0000Z", receipt_class="DIAGNOSTIC_NO_PACK",
                                               chain_path="/x/scripts/night_chains/align_r1_rehearsal.zsh"),
            "b5_chain": types.SimpleNamespace(plan_id="night-hazard", receipt_class=night_gate.HAZARD_PACK,
                                              chain_path="/x/chain.zsh"),
            "undeclared": types.SimpleNamespace(plan_id="night-other", receipt_class="DIAGNOSTIC_NO_PACK",
                                                chain_path="/x/chain.zsh"),
        }

    def declared_codes(self, name):
        contract = self.rt.UNDECLARED_CHAIN_CONTRACT if name == "undeclared" else self.ec.CONTRACTS[name]
        return sorted(self.ec.as_outcome_map(contract))

    def compare(self, plan, code, *, payload=None):
        for verdict in ("GO", "REFUSED", "ABORTED", "CHAIN_STOPPED"):
            for started in (True, False):
                with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
                    night = Path(tmp)
                    if started:
                        (night / "chain.started").write_text("{}")
                    if payload is not None:
                        (night / "align-r1").mkdir()
                        (night / "align-r1" / "r1_result.json").write_text(json.dumps(payload))
                    with self.subTest(plan=plan.plan_id, code=code, verdict=verdict, started=started,
                                      payload=payload):
                        self.assertEqual(_chain_outcome_a6a09e6d7(self.rt, plan, night, verdict, code, "why"),
                                         self.rt._chain_outcome(plan, night, verdict, code, "why"))

    def test_every_declared_code_of_every_chain_contract_keeps_todays_reasons(self):
        seen = {}
        for name, plan in self.plans().items():
            codes = self.declared_codes(name)
            seen[name] = codes
            for code in codes:
                self.compare(plan, code)
                if name == "r1_driver":
                    for status in ("complete", "refused", "aborted"):
                        self.compare(plan, code, payload={"status": status})
        # The table the test walks is the declared table, not a hand list.
        self.assertEqual(seen["r1_driver"], [0, 3, 4])
        self.assertEqual(seen["b5_chain"], [0, 10, 11, 12, 13, 64, 75])
        self.assertEqual(seen["undeclared"], [0])

    def test_undeclared_codes_keep_chain_exit_nonzero(self):
        for name, plan in self.plans().items():
            declared = set(self.declared_codes(name))
            for code in self.UNDECLARED + (None,):
                if code in declared:
                    continue
                self.compare(plan, code)
                with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
                    night = Path(tmp)
                    (night / "chain.started").write_text("{}")
                    reasons = self.rt._chain_outcome(plan, night, "GO", code)["fault_reasons"]
                    if code is not None:
                        self.assertIn(f"chain_exit_nonzero:{code}", reasons)

    def test_the_contract_selects_by_chain(self):
        plans = self.plans()
        night = Path("/nonexistent-night")
        self.assertEqual(self.rt._chain_exit_contract_name(plans["r1_driver"], True), "r1_driver")
        self.assertEqual(self.rt._chain_exit_contract_name(plans["b5_chain"], False), "b5_chain")
        self.assertEqual(self.rt._chain_exit_contract_name(plans["undeclared"], False), "undeclared")
        fact = self.rt._chain_exit_fact(plans["r1_driver"], night, 3)
        self.assertEqual(fact, {"contract": "r1_driver", "word": "refused", "class": "refused", "declared": True})
        self.assertEqual(self.rt._chain_exit_fact(plans["b5_chain"], night, 2)["declared"], False)
        self.assertIsNone(self.rt._chain_exit_fact(plans["undeclared"], night, None))

    def test_the_one_changed_edge_non_int_codes_is_listed(self):
        # The only inputs whose reasons differ from a6a09e6d7: exit codes that are not exact ints but compare
        # equal to 0 (False, 0.0). No writer produces them (Popen.wait/poll and chain.exited carry int or None).
        # Under the contract they are undeclared, hence a fault; listed in the draft deviation row.
        plan = self.plans()["undeclared"]
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
            night = Path(tmp)
            (night / "chain.started").write_text("{}")
            for code in (False, 0.0):
                self.assertEqual([], _chain_outcome_a6a09e6d7(self.rt, plan, night, "GO", code)["fault_reasons"])
                self.assertEqual([f"chain_exit_nonzero:{code}"],
                                 self.rt._chain_outcome(plan, night, "GO", code)["fault_reasons"])
            for code in (True, 3.0):   # nonzero non-ints already faulted; same string
                self.assertEqual(_chain_outcome_a6a09e6d7(self.rt, plan, night, "GO", code),
                                 self.rt._chain_outcome(plan, night, "GO", code))


class _NetworkTimeHost(trn._PowerHost):
    """_PowerHost plus a stateful network-time setting behind the narrow systemsetup rule."""

    def __init__(self, base, mode, *, network_time="off", **kwargs):
        super().__init__(base, mode, **kwargs)
        self.network_time = network_time

    def __getitem__(self, argv):
        if argv == NETWORK_TIME_QUERY_ARGV:
            self.calls.append("nt_query")
            return trn._probe(argv, stdout=f"Network Time: {self.network_time.capitalize()}\n")
        if argv == NETWORK_TIME_ON_ARGV:
            self.calls.append("nt_on")
            self.network_time = "on"
            return trn._probe(argv, stdout="setUsingNetworkTime: On\n")
        return super().__getitem__(argv)


# Captured at a6a09e6d7 with RL108_BASE=1 (see the module docstring). Each value: exit code, the ordered host
# operations, end power mode, end network time, host marker present, R1 marker present, the result's
# host_restoration ok/action (None when absent), the custody-log restore labels, and the refusal's
# exit_restore ok/action (None when absent).
GOLDEN = {
 "admission_refused_under_the_lock": {"calls": ["read", "restore", "read", "nt_query"], "exit": 3, "exit_restore": {"action": "restored", "ok": True}, "host_marker": False, "labels": ["ac powermode close: restore Automatic; network time left_off"], "mode": 0, "network_time": "off", "r1_marker": False, "restoration": {"action": "restored", "ok": True}},
 "another_night_holds_the_lock": {"calls": [], "exit": 3, "exit_restore": None, "host_marker": True, "labels": ["ac powermode close deferred:"], "mode": 2, "network_time": "off", "r1_marker": False, "restoration": {"action": None, "ok": False}},
 "chain_exit_nonzero_high_power": {"calls": ["read", "restore", "read", "nt_query"], "exit": 5, "exit_restore": None, "host_marker": False, "labels": ["ac powermode close: restore Automatic; network time left_off"], "mode": 0, "network_time": "off", "r1_marker": False, "restoration": {"action": "restored", "ok": True}},
 "close_restore_fails": {"calls": ["read", "restore", "read", "nt_query"], "exit": 0, "exit_restore": None, "host_marker": True, "labels": ["ac powermode close: restore Automatic; network time left_off"], "mode": 2, "network_time": "off", "r1_marker": False, "restoration": {"action": "restore_failed", "ok": False}},
 "deadman_absent_marker_at_completion": {"calls": ["restore", "read", "nt_query"], "exit": 0, "exit_restore": None, "host_marker": False, "labels": ["ac powermode close: restore Automatic; network time left_off"], "mode": 0, "network_time": "off", "r1_marker": False, "restoration": {"action": "restored", "ok": True}},
 "deadman_after_courier_sent": {"calls": ["restore", "read", "nt_query"], "exit": 0, "exit_restore": None, "host_marker": False, "labels": ["ac powermode close: restore Automatic; network time left_off"], "mode": 0, "network_time": "off", "r1_marker": False, "restoration": {"action": "restored", "ok": True}},
 "exception_after_parse_before_admission": {"calls": ["restore", "read", "nt_query"], "exit": None, "exit_restore": None, "host_marker": False, "labels": ["ac powermode close: restore Automatic; network time left_off", "ac powermode exit restore (exception_before_admission)"], "mode": 0, "network_time": "off", "r1_marker": False, "restoration": {"action": "restored", "ok": True}},
 "exception_before_plan_parse": {"calls": ["restore", "read", "nt_query"], "exit": None, "exit_restore": None, "host_marker": False, "labels": ["ac powermode close: restore Automatic; network time left_off", "ac powermode exit restore (exception_before_admission)"], "mode": 0, "network_time": "off", "r1_marker": False, "restoration": {"action": "restored", "ok": True}},
 "go_complete_high_power": {"calls": ["read", "restore", "read", "nt_query"], "exit": 0, "exit_restore": None, "host_marker": False, "labels": ["ac powermode close: restore Automatic; network time left_off"], "mode": 0, "network_time": "off", "r1_marker": False, "restoration": {"action": "restored", "ok": True}},
 "go_complete_high_power_network_time_turned_off": {"calls": ["read", "restore", "read", "nt_on", "nt_query"], "exit": 0, "exit_restore": None, "host_marker": False, "labels": ["ac powermode close: restore Automatic and network time ON"], "mode": 0, "network_time": "on", "r1_marker": False, "restoration": {"action": "restored", "ok": True}},
 "go_complete_mode_zero": {"calls": ["read", "restore", "read", "nt_query"], "exit": 0, "exit_restore": None, "host_marker": False, "labels": ["ac powermode close: restore Automatic; network time left_off"], "mode": 0, "network_time": "off", "r1_marker": False, "restoration": {"action": "restored", "ok": True}},
 "host_lock_error": {"calls": ["restore", "read", "nt_query"], "exit": 3, "exit_restore": {"action": "restored", "ok": True}, "host_marker": False, "labels": ["ac powermode close: restore Automatic; network time left_off", "ac powermode exit restore (host_lock_error)"], "mode": 0, "network_time": "off", "r1_marker": False, "restoration": {"action": "restored", "ok": True}},
 "launch_abandoned": {"calls": ["restore", "read", "nt_query"], "exit": 3, "exit_restore": None, "host_marker": False, "labels": ["ac powermode close: restore Automatic; network time left_off", "ac powermode exit restore (launch_abandoned)"], "mode": 0, "network_time": "off", "r1_marker": False, "restoration": None},
 "mode_zero_host_left_at_two_refused": {"calls": ["read", "restore", "read", "nt_query"], "exit": 3, "exit_restore": None, "host_marker": False, "labels": ["ac powermode close: restore Automatic; network time left_off"], "mode": 0, "network_time": "off", "r1_marker": False, "restoration": {"action": "restored", "ok": True}},
 "plan_malformed": {"calls": ["restore", "read", "nt_query"], "exit": 3, "exit_restore": None, "host_marker": False, "labels": [], "mode": 0, "network_time": "off", "r1_marker": False, "restoration": None},
 "prechain_gate_refusal": {"calls": ["read", "restore", "read", "nt_query"], "exit": 3, "exit_restore": None, "host_marker": False, "labels": ["ac powermode close: restore Automatic; network time left_off"], "mode": 0, "network_time": "off", "r1_marker": False, "restoration": {"action": "restored", "ok": True}},
 "rerun": {"calls": ["restore", "read", "nt_query"], "exit": 3, "exit_restore": None, "host_marker": False, "labels": ["ac powermode close: restore Automatic; network time left_off", "ac powermode exit restore (rerun)"], "mode": 0, "network_time": "off", "r1_marker": False, "restoration": None},
}


class TerminalHostEndStateTests(unittest.TestCase):
    """RL-108 condition 3: each terminal path's host end state equals a6a09e6d7's, under fakes."""

    setUp = trn.NightDriverTests.setUp
    tearDown = trn.NightDriverTests.tearDown
    _write_plan = trn.NightDriverTests._write_plan
    _popen_recorder = trn.NightDriverTests._popen_recorder
    _run_night = trn.NightDriverTests._run_night
    _declare_high_power = trn.NightDriverTests._declare_high_power
    _w1_host_marker = trn.NightDriverTests._w1_host_marker
    _other_night_holds_the_lock = trn.NightDriverTests._other_night_holds_the_lock

    def host(self, mode, **kwargs):
        host = _NetworkTimeHost(self.source.results, mode, **kwargs)
        self.source.results = host
        return host

    def tripwire(self):
        def refused(*args, **kwargs):
            raise AssertionError(f"a terminal-path test reached os.killpg{args}")
        patch = mock.patch.object(self.driver.os, "killpg", side_effect=refused)
        patch.start()
        self.addCleanup(patch.stop)

    def observe(self, name, host, exit_code, marker=None):
        night = self.custody / "night"
        try:
            restoration = json.loads((night / "result.json").read_text()).get("host_restoration")
        except OSError:
            restoration = None
        try:
            evidence = json.loads((night / "refusal.json").read_text())["refusal"].get("evidence")
            exit_restore = evidence.get("exit_restore") if isinstance(evidence, dict) else None
        except (OSError, KeyError, TypeError):
            exit_restore = None
        log = (self.custody / "night.log").read_text() if (self.custody / "night.log").exists() else ""
        labels = sorted(set(re.findall(r"ac powermode (?:exit restore \([a-z_]+\)|close[^:{]*(?::[^:{]*)?)", log)))
        observed = {"exit": exit_code, "calls": list(host.calls), "mode": host.mode,
                    "network_time": host.network_time,
                    "host_marker": marker is not None and marker.exists(),
                    "r1_marker": (self.root / ".align-r1-high-power").exists(),
                    "restoration": None if restoration is None else
                    {"ok": restoration.get("ok"), "action": restoration.get("action")},
                    "labels": [label.strip() for label in labels],
                    "exit_restore": None if exit_restore is None else
                    {"ok": exit_restore.get("ok"), "action": exit_restore.get("action")}}
        if os.environ.get("RL108_CAPTURE"):
            with open(os.environ["RL108_CAPTURE"], "a", encoding="utf-8") as stream:
                stream.write(json.dumps({name: observed}, sort_keys=True) + "\n")
        if name in GOLDEN:
            self.assertEqual(GOLDEN[name], observed)
        elif not os.environ.get("RL108_CAPTURE"):
            self.fail(f"no golden for {name}")
        return observed

    # -- before admission -----------------------------------------------------------------------------------

    def test_plan_malformed(self):
        self.tripwire()
        host = self.host(2)
        marker = self._w1_host_marker(plan_path=self.plan_path.resolve())
        self.plan_path.write_text("{not json")
        exit_code, calls = self._run_night()
        self.assertEqual(calls, [])
        self.observe("plan_malformed", host, exit_code, marker)

    def test_exception_before_plan_parse(self):
        self.tripwire()
        self._declare_high_power()
        host = self.host(2)
        marker = self._w1_host_marker(plan_path=self.plan_path.resolve())
        with mock.patch.object(self.driver, "agent_census", side_effect=OSError(28, "No space")):
            with self.assertRaises(OSError):
                self._run_night()
        self.observe("exception_before_plan_parse", host, None, marker)

    def test_exception_after_parse_before_admission(self):
        self.tripwire()
        self._declare_high_power()
        host = self.host(2)
        marker = self._w1_host_marker(custody_root=self.custody)
        with mock.patch.object(self.driver, "_append_census", side_effect=OSError(28, "No space")):
            with self.assertRaises(OSError):
                self._run_night()
        self.observe("exception_after_parse_before_admission", host, None, marker)

    def test_launch_abandoned(self):
        self.tripwire()
        self._declare_high_power()
        host = self.host(2)
        marker = self._w1_host_marker(custody_root=self.custody, plan_path=self.plan_path)
        night = self.custody / "night"
        night.mkdir(parents=True, exist_ok=True)
        (night / "launch_abandoned.json").write_text("{}")
        with mock.patch.object(self.driver, "_existing_record", return_value=night / "launch_abandoned.json"):
            exit_code, calls = self._run_night()
        self.assertEqual(calls, [])
        self.observe("launch_abandoned", host, exit_code, marker)

    def test_rerun(self):
        self.tripwire()
        self._declare_high_power()
        host = self.host(2)
        marker = self._w1_host_marker(custody_root=self.custody, plan_path=self.plan_path)
        night = self.custody / "night"
        night.mkdir(parents=True, exist_ok=True)
        (night / "result.json").write_text("{}")
        exit_code, calls = self._run_night()
        self.assertEqual(calls, [])
        self.observe("rerun", host, exit_code, marker)

    def test_host_lock_error(self):
        self.tripwire()
        self._declare_high_power()
        host = self.host(2)
        marker = self._w1_host_marker(custody_root=self.custody)
        with mock.patch.object(self.driver, "_take_host_lock", return_value=(None, "OSError: [Errno 5] I/O")):
            exit_code, calls = self._run_night()
        self.assertEqual(calls, [])
        self.observe("host_lock_error", host, exit_code, marker)

    def test_another_night_holds_the_lock(self):
        self.tripwire()
        self._declare_high_power()
        host = self.host(2)
        marker = self._w1_host_marker(custody_root=self.root / "other" / "custody")
        self._other_night_holds_the_lock()
        from joulewise.align.apple import powermode
        with mock.patch.object(powermode, "NIGHT_LOCK_WAIT_S", 0.0):
            exit_code, calls = self._run_night()
        self.assertEqual(calls, [])
        self.observe("another_night_holds_the_lock", host, exit_code, marker)

    def test_admission_refused_under_the_lock(self):
        self.tripwire()
        self._declare_high_power()
        host = self.host(0)          # plan declares 2, host reads 0: refused while holding the lock
        exit_code, calls = self._run_night()
        self.assertEqual(calls, [])
        self.observe("admission_refused_under_the_lock", host, exit_code)

    def test_mode_zero_host_left_at_two_refused(self):
        self.tripwire()
        host = self.host(2)
        exit_code, calls = self._run_night()
        self.assertEqual(calls, [])
        self.observe("mode_zero_host_left_at_two_refused", host, exit_code)

    # -- after admission ------------------------------------------------------------------------------------

    def test_prechain_gate_refusal(self):
        self.tripwire()
        self._declare_high_power()
        host = self.host(2)
        marker = self._w1_host_marker(custody_root=self.custody)
        self.source.census_responses = [trn._probe(night_gate.AGENT_CENSUS_ARGV, exit_code=1),
                                        trn._probe(night_gate.AGENT_CENSUS_ARGV, stdout="agent\n")]
        exit_code, calls = self._run_night()
        self.observe("prechain_gate_refusal", host, exit_code, marker)

    def test_go_complete_high_power(self):
        self.tripwire()
        self._declare_high_power()
        host = self.host(2)
        marker = self._w1_host_marker(custody_root=self.custody)
        exit_code, calls = self._run_night()
        self.assertEqual(calls, [["/bin/zsh", str(self.chain)]])
        self.observe("go_complete_high_power", host, exit_code, marker)

    def test_go_complete_high_power_network_time_turned_off(self):
        self.tripwire()
        self._declare_high_power()
        host = self.host(2)
        marker = self._w1_host_marker(custody_root=self.custody)
        night = self.custody / "night"
        night.mkdir(parents=True, exist_ok=True)
        (night / "network_time_off.action.json").write_text(json.dumps(
            {"argv": OFF_ARGV, "returncode": 0, "stdout": "setUsingNetworkTime: Off\n"}))
        exit_code, calls = self._run_night()
        self.observe("go_complete_high_power_network_time_turned_off", host, exit_code, marker)

    def test_chain_exit_nonzero_high_power(self):
        self.tripwire()
        self._declare_high_power()
        host = self.host(2)
        marker = self._w1_host_marker(custody_root=self.custody)
        exit_code, calls = self._run_night(return_code=3)
        self.assertEqual(calls, [["/bin/zsh", str(self.chain)]])
        self.observe("chain_exit_nonzero_high_power", host, exit_code, marker)

    def test_close_restore_fails(self):
        self.tripwire()
        self._declare_high_power()
        host = self.host(2, restore_code=1)
        marker = self._w1_host_marker(custody_root=self.custody)
        exit_code, calls = self._run_night()
        self.observe("close_restore_fails", host, exit_code, marker)

    def test_go_complete_mode_zero(self):
        self.tripwire()
        host = self.host(0)
        exit_code, calls = self._run_night()
        self.observe("go_complete_mode_zero", host, exit_code)

    # -- dead-man -------------------------------------------------------------------------------------------

    def test_deadman_after_courier_sent(self):
        self.tripwire()
        self._declare_high_power()
        host = self.host(2)
        marker = self._w1_host_marker(custody_root=self.custody)
        night = self.custody / "night"
        night.mkdir(parents=True, exist_ok=True)
        (night / "courier.sent").write_text("sent\n")
        exit_code = self.driver.dead_man(self.plan_path)
        self.observe("deadman_after_courier_sent", host, exit_code, marker)

    def test_deadman_absent_marker_at_completion(self):
        self.tripwire()
        self._declare_high_power()
        host = self.host(2)
        marker = self._w1_host_marker(custody_root=self.custody)
        (self.custody / "night").mkdir(parents=True, exist_ok=True)
        plan = self.driver._load_plan(self.plan_path)
        with mock.patch.object(self.driver.time, "time",
                               return_value=plan.t0_epoch_s + plan.window_max_s + self.driver.COURIER_DEADLINE_S):
            exit_code = self.driver.dead_man(self.plan_path)
        self.observe("deadman_absent_marker_at_completion", host, exit_code, marker)


@unittest.skipIf(BASE, "branch-only")
class OneRestorerTests(unittest.TestCase):
    """RL-108 condition 3, structure: one restorer in the night driver."""

    def test_every_host_restore_goes_through_restore_owed(self):
        tree = ast.parse((trn.REPO_ROOT / "scripts/run_night.py").read_text())
        names = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
        self.assertIn("restore_owed", names)
        self.assertNotIn("_close_ac_powermode", names)
        callers, primitive = set(), []
        for function in (n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)):
            for call in (n for n in ast.walk(function) if isinstance(n, ast.Call)):
                target = call.func
                if isinstance(target, ast.Name) and target.id == "restore_owed":
                    callers.add(function.name)
                if isinstance(target, ast.Attribute) and target.attr in ("restore_owed", "restore_automatic"):
                    primitive.append((function.name, target.attr))
        self.assertEqual(callers, {"_close_night_host", "_deadman_host_restore"})
        # powermode's own primitives are reached only from inside restore_owed (and admission's marker restore).
        self.assertEqual(sorted(primitive), [("restore_owed", "restore_automatic")])


@unittest.skipIf(BASE, "branch-only")
class WindowJournalTests(unittest.TestCase):
    """RL-108 condition 4: appends at transitions only, never while a member may run."""

    def setUp(self):
        from joulewise import window_journal
        self.wj = window_journal
        temporary = tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR"))
        self.addCleanup(temporary.cleanup)
        self.night = Path(temporary.name)

    def test_sequence_and_member_guard(self):
        wj, night = self.wj, self.night
        self.assertTrue(wj.append(night, "DriverStarted", writer="t"))
        descriptor = os.open(night / "chain.started", os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        self.assertTrue(wj.append(night, "ChainOpen", writer="t"))      # empty claim: nothing spawned
        os.write(descriptor, b'{"pid": 1, "pgid": 1}')
        os.close(descriptor)
        for state in ("ChainOpen", "ChainExited", "ResultWritten", "Delivered", "DeadmanTail"):
            self.assertFalse(wj.append(night, state, writer="t"), state)   # a member may be running
        (night / "chain.exited").write_text('{"exit_code": 0}')
        self.assertFalse(wj.append(night, "ChainOpen", writer="t"))
        self.assertTrue(wj.append(night, "ChainExited", writer="t", facts={"exit_code": 0}))
        self.assertTrue(wj.append(night, "ResultWritten", writer="t", facts={
            "verdict": "GO", "chain_outcome": "COMPLETE", "chain_exit_code": 0,
            "chain_exit": {"contract": "r1_driver", "word": "complete", "class": "success", "declared": True}}))
        self.assertTrue(wj.append(night, "Delivered", writer="t", facts={"sent": True}))
        rows = wj.read(night)
        self.assertEqual([r["to"] for r in rows],
                         ["DriverStarted", "ChainOpen", "ChainExited", "ResultWritten", "Delivered"])
        self.assertEqual([r["from"] for r in rows], [None, "DriverStarted", "ChainOpen", "ChainExited",
                                                     "ResultWritten"])

    def test_never_raises_and_refuses_free_text(self):
        self.assertFalse(self.wj.append(self.night, "NotAState", writer="t"))
        self.assertFalse(self.wj.append(self.night, "DriverStarted", writer="t", facts={"detail": "free text"}))
        self.assertFalse(self.wj.append(self.night, "DriverStarted", writer="t", facts={"verdict": {"x": 1}}))
        self.assertFalse(self.wj.append(self.night / "missing" / "dir", "DriverStarted", writer="t"))
        self.assertFalse((self.night / self.wj.NAME).exists())

    def test_a_driver_night_writes_the_transitions(self):
        case = TerminalHostEndStateTests("test_go_complete_mode_zero")
        case.setUp()
        try:
            case.host(0)
            exit_code, calls = case._run_night()
            self.assertEqual(exit_code, 0)
            rows = self.wj.read(case.custody / "night")
        finally:
            case.tearDown()
        self.assertEqual([r["to"] for r in rows],
                         ["DriverStarted", "ChainOpen", "ChainExited", "ResultWritten", "Delivered"])
        self.assertEqual(rows[3]["facts"]["chain_exit"],
                         {"contract": "undeclared", "word": "complete", "class": "success", "declared": True})

    def test_no_reader_of_the_journal_in_gates_harvest_engine_or_recompute(self):
        hits = []
        for path in sorted((trn.REPO_ROOT / "joulewise").rglob("*.py")) + sorted((trn.REPO_ROOT / "scripts").rglob("*.py")):
            relative = path.relative_to(trn.REPO_ROOT).as_posix()
            if relative in ("joulewise/window_journal.py", "scripts/run_night.py", "joulewise/b5/driver.py"):
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            # (v4_topup's "window journal" is the hazard battery journal, a different file.)
            if re.search(r"window\.journal\.jsonl|joulewise\.window_journal|import[^\n]*\bwindow_journal\b", text):
                hits.append(relative)
        self.assertEqual(hits, [])
