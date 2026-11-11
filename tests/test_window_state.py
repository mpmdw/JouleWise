"""Synthetic structure only. No custody, model, network or host probes."""

from dataclasses import FrozenInstanceError, replace
from contextlib import ExitStack, redirect_stdout
import io
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from joulewise import window_state as ws


class WindowStateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.night = self.root / "night"
        self.night.mkdir()

    def write(self, name, value):
        path = self.night / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def touch(self, name):
        path = self.night / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()

    def result(self, verdict="GO", code=0, **extra):
        self.write("result.json", dict(verdict=verdict, chain_exit_code=code, **extra))

    def chain(self, code=0):
        self.write("chain.started", {"epoch_s": 100})
        self.write("chain.exited", {"exit_code": code, "epoch_s": 200})

    def measured(self):
        self.chain()
        self.result()

    def observe(self, **kwargs):
        return ws.observe_night_dir(self.root, **kwargs)

    def outcome(self, **kwargs):
        return ws.window_outcome(self.night, **kwargs)

    def assert_outcome(self, outcome, **kwargs):
        report = self.outcome(**kwargs)
        self.assertIs(report.outcome, outcome, report)
        return report

    def test_outcome_truth_table_both_record_generations(self):
        cases = [
            ("main", "GO", 0, {}, None, ws.WindowOutcome.MEASURED_OK),
            ("W1", "GO", 0, {"chain_outcome": "COMPLETE", "measurement_outcome": "complete",
                                  "fault": False, "fault_reasons": []}, "complete", ws.WindowOutcome.MEASURED_OK),
            ("flag", "GO", 0, {"fault": True}, None, ws.WindowOutcome.MEASURED_WITH_FLAGS),
            ("reason", "GO", 0, {"fault": False, "fault_reasons": ["synthetic"]}, None, ws.WindowOutcome.MEASURED_WITH_FLAGS),
            ("failed", "GO", 3, {}, "refused", ws.WindowOutcome.CHAIN_FAILED),
            ("refused", "REFUSED", None, {}, None, ws.WindowOutcome.REFUSED_PRE_CHAIN),
            ("abort", "ABORTED", -15, {}, "aborted", ws.WindowOutcome.ABORTED),
            ("stopped", "CHAIN_STOPPED", 10, {}, None, ws.WindowOutcome.CHAIN_FAILED),
            ("unknown", "REHEARSAL_ONLY", 0, {}, None, ws.WindowOutcome.UNKNOWN),
        ]
        for label, verdict, code, extra, payload, expected in cases:
            with self.subTest(label=label), tempfile.TemporaryDirectory() as directory:
                night = Path(directory) / "night"
                night.mkdir()
                (night / "result.json").write_text(json.dumps(dict(verdict=verdict, chain_exit_code=code, **extra)))
                if code is not None:
                    (night / "chain.started").write_text("{}")
                    (night / "chain.exited").write_text(json.dumps({"exit_code": code}))
                if payload:
                    target = night / "align-r1"
                    target.mkdir()
                    (target / "r1_result.json").write_text(json.dumps({"status": payload}))
                    if payload == "complete":
                        (target / "r1_slots.json").touch()
                self.assertIs(ws.window_outcome(night).outcome, expected)

    def test_historical_1108_from_audit_not_data(self):
        self.chain(3)
        self.result(code=3, fault=False)
        self.write("hazard_result.json", {"verdict": "GO", "chain": {"exit_code": 3}, "faults": {"reasons": []}})
        self.write("r1_result.json", {"status": "refused"})
        report = self.assert_outcome(ws.WindowOutcome.CHAIN_FAILED)
        self.assertIn("NONZERO_EXIT_WITHOUT_FAULT", report.violated_invariants)
        self.assertEqual(report.evidence["r1_result.json.status"], "refused")

    def test_historical_1110_from_audit_not_data(self):
        self.result("REFUSED", None, aborted_reason="night_refused_hazard")
        self.write("refusal.json", {"reason": "hazard arm did not return GO"})
        self.write("courier.json", {"sent": True})
        self.touch("courier.sent")
        report = self.assert_outcome(ws.WindowOutcome.REFUSED_PRE_CHAIN)
        self.assertIn("COURIER_SENT_WITHOUT_DELIVERY", report.violated_invariants)
        self.assertFalse(any(n.startswith("chain.") for n in report.evidence["markers"]))

    def test_lifecycle_truth_table_one_directory_per_state(self):
        loaded = {label: ws.PlistFacts(True, True) for label in ws.LABELS}
        removed = {label: ws.PlistFacts(False, False) for label in ws.LABELS}
        cases = [
            (ws.WindowState.UNKNOWN, {}, {}, None, 100),
            (ws.WindowState.PREPARED, {}, {"t0_epoch_s": 1000, "window_max_s": 100}, None, 100),
            (ws.WindowState.INSTALLED, {}, {}, loaded, 100),
            (ws.WindowState.DRIVER_STARTED, {"censuses.jsonl": "exists"}, {}, None, 100),
            (ws.WindowState.REFUSED_PRE_CHAIN, {"refusal.json": {}}, {}, None, 100),
            (ws.WindowState.CHAIN_OPEN, {"chain.started": {}}, {}, None, 100),
            (ws.WindowState.CHAIN_EXITED, {"chain.started": {}, "chain.exited": {"exit_code": 0}}, {}, None, 100),
            (ws.WindowState.CHAIN_UNKILLED, {"chain.started": {}, "chain.unkilled": {}}, {}, None, 100),
            (ws.WindowState.RESULT_WRITTEN, {"result.json": {"verdict": "REFUSED", "chain_exit_code": None}}, {}, None, 100),
            (ws.WindowState.DELIVERED, {"result.json": {"verdict": "REFUSED", "chain_exit_code": None}, "courier.sent": "exists"}, {}, None, 100),
            (ws.WindowState.DEADMAN_TAIL, {"result.json": {"verdict": "REFUSED", "chain_exit_code": None}, "courier.json": {"sent": False}}, {}, None, 100),
            (ws.WindowState.STRANDED, {"result.json": {"verdict": "REFUSED", "chain_exit_code": None, "ended_epoch_s": 100}, "courier.sent": "exists"}, {}, loaded, 3701),
            (ws.WindowState.UNINSTALLED, {"result.json": {"verdict": "REFUSED", "chain_exit_code": None}}, {}, removed, 100),
            (ws.WindowState.LAUNCH_ABANDONED, {"launch_abandoned.json": {"schema": "joulewise.launch_abandoned.v1"}}, {}, None, 100),
        ]
        for expected, files, plan, plists, now in cases:
            with self.subTest(state=expected), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "night").mkdir()
                if plan:
                    (root / "night_plan.json").write_text(json.dumps(plan))
                for name, value in files.items():
                    path = root / "night" / name
                    path.write_text("" if value == "exists" else json.dumps(value))
                report = ws.derive_window_state(ws.observe_night_dir(root, plists=plists), now)
                self.assertIs(report.state, expected, report)

    def test_each_driver_marker(self):
        for marker in ws.DRIVER_MARKERS:
            with self.subTest(marker=marker):
                observation = ws.Observation(markers={marker})
                self.assertIs(ws.derive_window_state(observation, 0).state, ws.WindowState.DRIVER_STARTED)

    def test_lifecycle_precedence(self):
        base = ws.Observation(markers={"chain.started", "chain.unkilled", "result.json", "courier.sent"})
        self.assertIs(ws.derive_window_state(base, 0).state, ws.WindowState.CHAIN_UNKILLED)
        self.assertIs(ws.derive_window_state(replace(base, markers=base.markers - {"chain.unkilled"}), 0).state, ws.WindowState.CHAIN_OPEN)
        resolved = replace(base, markers=base.markers | {"chain.exited"})
        self.assertIs(ws.derive_window_state(resolved, 0).state, ws.WindowState.DELIVERED)
        self.assertIs(ws.derive_window_state(replace(base, markers={"launch_abandoned.json", "receipt.json"}), 0).state, ws.WindowState.DRIVER_STARTED)
        removed = (ws.PlistFacts(False, False),) * 2
        self.assertIs(ws.derive_window_state(replace(base, markers={"launch_abandoned.json"}, plists=removed), 0).state, ws.WindowState.UNINSTALLED)

    def test_plist_tristates_never_invent_uninstall(self):
        for disk in (None, False, True):
            for loaded in (None, False, True):
                with self.subTest(on_disk=disk, loaded=loaded):
                    facts = (ws.PlistFacts(disk, loaded),) * 2
                    state = ws.derive_window_state(ws.Observation(markers={"result.json", "courier.sent"}, plists=facts), 0).state
                    expected = ws.WindowState.UNINSTALLED if disk is False and loaded is False else ws.WindowState.DELIVERED
                    self.assertIs(state, expected)
        partial = {ws.LABELS[0]: ws.PlistFacts(True, True)}
        self.assertIs(ws.derive_window_state(self.observe(plists=partial), 0).state, ws.WindowState.UNKNOWN)
        terminal = ws.Observation(markers={"result.json", "courier.sent"},
                                  plists=(ws.PlistFacts(False, False), ws.PlistFacts()))
        self.assertIs(ws.derive_window_state(terminal, 0).state, ws.WindowState.DELIVERED)

    def test_stranded_and_tail_time_boundaries(self):
        base = ws.Observation(markers={"result.json", "courier.sent"}, completion_epoch_s=100,
                              plists=(ws.PlistFacts(None, True), ws.PlistFacts()))
        self.assertIs(ws.derive_window_state(base, 3700).state, ws.WindowState.DELIVERED)
        self.assertIs(ws.derive_window_state(base, 3700.001).state, ws.WindowState.STRANDED)
        on_disk_only = replace(base, plists=(ws.PlistFacts(True, False), ws.PlistFacts()))
        self.assertIs(ws.derive_window_state(on_disk_only, 3701).state, ws.WindowState.STRANDED)
        self.assertIs(ws.derive_window_state(replace(base, completion_epoch_s=None), 99999).state, ws.WindowState.DELIVERED)
        undelivered = replace(base, markers={"result.json"})
        self.assertIs(ws.derive_window_state(undelivered, 99).state, ws.WindowState.RESULT_WRITTEN)
        self.assertIs(ws.derive_window_state(undelivered, 100).state, ws.WindowState.DEADMAN_TAIL)
        self.assertIs(ws.derive_window_state(undelivered, 3701).state, ws.WindowState.DEADMAN_TAIL)
        self.assertIs(ws.derive_window_state(replace(undelivered, delivery_required=False), 3701).state, ws.WindowState.STRANDED)
        self.assertIs(ws.derive_window_state(replace(undelivered, markers={"result.json", "courier.filed"}), 0).state, ws.WindowState.DEADMAN_TAIL)

    def test_each_invariant_positive_and_negative(self):
        cases = [
            (ws.invariant_go_started, ws.Observation(verdict="GO"), "GO_WITHOUT_CHAIN_STARTED", {"markers": {"chain.started"}}),
            (ws.invariant_exit_started, ws.Observation(markers={"chain.exited"}), "CHAIN_EXITED_WITHOUT_CHAIN_STARTED", {"markers": {"chain.exited", "chain.started"}}),
            (ws.invariant_nonzero_fault, ws.Observation(chain_exit_code=3, fault=False), "NONZERO_EXIT_WITHOUT_FAULT", {"fault": True}),
            (ws.invariant_payload_exit, ws.Observation(chain_exit_code=0, payload_status="refused"), "PAYLOAD_EXIT_MISMATCH", {"payload_status": "complete"}),
            (ws.invariant_payload_slots, ws.Observation(chain_exit_code=0, slots_present=False), "PAYLOAD_SLOTS_MISMATCH", {"slots_present": True}),
            (ws.invariant_courier_delivery, ws.Observation(markers={"courier.sent"}), "COURIER_SENT_WITHOUT_DELIVERY", {"delivery_recorded": True}),
            (ws.invariant_courier_result, ws.Observation(markers={"courier.sent"}), "COURIER_SENT_WITHOUT_RESULT", {"markers": {"result.json", "courier.sent"}}),
        ]
        for check, bad, code, correction in cases:
            with self.subTest(check=check.__name__):
                self.assertEqual(check(bad), code)
                self.assertIsNone(check(replace(bad, **correction)))
                self.assertIsNone(check(ws.Observation()))
                self.assertIn(code, ws.derive_window_state(bad, 0).violated_invariants)
        retained = ws.Observation(markers={"result.json"}, completion_epoch_s=1, plists=(ws.PlistFacts(None, True), ws.PlistFacts()))
        self.assertEqual(ws.invariant_stranded(retained, 3602), "LABEL_RETAINED_AFTER_COMPLETION")
        for update in ({"markers": frozenset()}, {"completion_epoch_s": None}, {"plists": (ws.PlistFacts(),) * 2}):
            self.assertIsNone(ws.invariant_stranded(replace(retained, **update), 3602))
        self.assertIsNone(ws.invariant_stranded(retained, 3601))
        self.assertIsNone(ws.invariant_payload_exit(ws.Observation(chain_exit_code=None, payload_status="refused")))
        self.assertEqual(ws.invariant_payload_exit(ws.Observation(chain_exit_code=3, payload_status="complete")), "PAYLOAD_EXIT_MISMATCH")
        self.assertEqual(ws.invariant_payload_slots(ws.Observation(chain_exit_code=3, slots_present=True)), "PAYLOAD_SLOTS_MISMATCH")
        self.assertIsNone(ws.invariant_nonzero_fault(ws.Observation(chain_exit_code=0)))
        self.assertIsNone(ws.invariant_courier_delivery(ws.Observation(markers={"courier.sent"}, delivery_required=False)))

    def test_purity_and_frozen_observation(self):
        markers = {"chain.started", "chain.exited", "result.json"}
        observation = ws.Observation(markers=markers, verdict="GO", chain_exit_code=0)
        markers.clear()
        self.assertIn("result.json", observation.markers)
        with self.assertRaises(FrozenInstanceError):
            observation.verdict = "REFUSED"
        class Forbidden:
            def __getattribute__(self, name):
                raise AssertionError("impure access: " + name)

        forbidden = Forbidden()
        with ExitStack() as stack:
            stack.enter_context(patch.object(ws, "os", forbidden))
            stack.enter_context(patch.object(ws, "time", forbidden))
            stack.enter_context(patch.dict(sys.modules, {"subprocess": forbidden}))
            for target in ("pathlib.Path.exists", "pathlib.Path.open", "builtins.open"):
                stack.enter_context(patch(target, side_effect=AssertionError("impure")))
            result = ws.derive_window_state(observation, 100)
        self.assertIs(result.state, ws.WindowState.RESULT_WRITTEN)
        self.assertIs(result.outcome.outcome, ws.WindowOutcome.MEASURED_OK)

    def test_random_subsets_totality_no_start_can_never_measure(self):
        rng = random.Random(20261111)
        names = [*ws.JSON_MARKERS, *ws.EXISTENCE_MARKERS, "r1_result.json", "r1_slots.json"]
        # Fixed-seed sampling over the power set, plus both extreme subsets.
        subsets = [set(), set(names)] + [{n for n in names if rng.getrandbits(1)} for _ in range(250)]
        for index, selected in enumerate(subsets):
            with self.subTest(index=index), tempfile.TemporaryDirectory() as directory:
                night = Path(directory) / "night"
                night.mkdir()
                for name in selected:
                    value = {"verdict": "GO", "chain_exit_code": 0, "status": "complete", "exit_code": 0}
                    (night / name).write_text(json.dumps(value))
                observed = ws.observe_night_dir(Path(directory))
                state = ws.derive_window_state(observed, 10000)
                report = ws.window_outcome(night)
                self.assertIsInstance(state.state, ws.WindowState)
                self.assertIsInstance(report.outcome, ws.WindowOutcome)
                if "chain.started" not in selected:
                    self.assertNotIn(report.outcome, (ws.WindowOutcome.MEASURED_OK, ws.WindowOutcome.MEASURED_WITH_FLAGS))

    def test_missing_start_exit_and_unknown_result(self):
        self.result()
        report = self.assert_outcome(ws.WindowOutcome.UNKNOWN)
        self.assertIn("GO_WITHOUT_CHAIN_STARTED", report.violated_invariants)
        self.write("chain.exited", {"exit_code": 0})
        self.assertIn("CHAIN_EXITED_WITHOUT_CHAIN_STARTED", self.assert_outcome(ws.WindowOutcome.UNKNOWN).violated_invariants)
        self.write("chain.started", {})
        (self.night / "chain.exited").unlink()
        self.assert_outcome(ws.WindowOutcome.UNKNOWN)
        self.write("chain.unkilled", {})
        self.assert_outcome(ws.WindowOutcome.UNKNOWN)
        (self.night / "chain.unkilled").unlink()
        self.result(code=None)
        self.assert_outcome(ws.WindowOutcome.UNKNOWN)
        (self.night / "result.json").unlink()
        self.assert_outcome(ws.WindowOutcome.UNKNOWN)

    def test_noncomplete_payloads_and_slots(self):
        self.measured()
        for status in ("refused", "aborted", "running"):
            with self.subTest(status=status):
                self.write("r1_result.json", {"status": status})
                report = self.assert_outcome(ws.WindowOutcome.CHAIN_FAILED)
                self.assertIn("PAYLOAD_EXIT_MISMATCH", report.violated_invariants)
        self.write("r1_result.json", {"status": "complete"})
        self.assert_outcome(ws.WindowOutcome.MEASURED_WITH_FLAGS)
        self.touch("r1_slots.json")
        self.assert_outcome(ws.WindowOutcome.MEASURED_OK)
        (self.night / "r1_result.json").unlink()
        self.assert_outcome(ws.WindowOutcome.UNKNOWN)

    def test_explicit_payload_and_multiple_locations(self):
        self.measured()
        external = self.root / "payload" / "r1_result.json"
        external.parent.mkdir()
        external.write_text('{"status":"complete"}')
        (external.parent / "r1_slots.json").touch()
        self.assert_outcome(ws.WindowOutcome.MEASURED_OK, payload_path=external)
        self.assert_outcome(ws.WindowOutcome.UNKNOWN, payload_path=external.with_name("missing.json"))
        self.assert_outcome(ws.WindowOutcome.UNKNOWN, payload_path=self.root / "missing" / "r1_result.json")
        external.write_text("[]")
        self.assert_outcome(ws.WindowOutcome.UNKNOWN, payload_path=external)
        self.write("r1_result.json", {"status": "complete"})
        self.write("align-r1/r1_result.json", {"status": "refused"})
        report = self.assert_outcome(ws.WindowOutcome.UNKNOWN)
        self.assertIn("CONFLICTING_PAYLOAD_STATUSES", report.reasons)

    def test_exit_contract_cannot_bless_nonzero(self):
        self.measured()
        self.assert_outcome(ws.WindowOutcome.MEASURED_OK, exit_contract={0: "complete", 3: "refused"})
        for contract in ({}, {3: "complete"}, {0: "refused"}, {0: "failed"}, {0: "stopped"}):
            with self.subTest(contract=contract):
                self.assert_outcome(ws.WindowOutcome.CHAIN_FAILED, exit_contract=contract)
        self.assert_outcome(ws.WindowOutcome.ABORTED, exit_contract={0: "aborted"})
        for contract in ({0: "future"}, {0: None}, {0: []}):
            self.assert_outcome(ws.WindowOutcome.UNKNOWN, exit_contract=contract)
        for contract in ([], {"0": "complete"}, {True: "complete"}):
            with self.assertRaises(TypeError):
                self.outcome(exit_contract=contract)
        for code in (-15, 1, 3, 4, 10, 65, 130):
            self.chain(code)
            self.result(code=code)
            self.assert_outcome(ws.WindowOutcome.CHAIN_FAILED, exit_contract={code: "complete"})

    def test_other_terminal_verdicts(self):
        self.result("ABORTED", None)
        self.assert_outcome(ws.WindowOutcome.ABORTED)
        self.result("REFUSED", 0)
        self.assert_outcome(ws.WindowOutcome.UNKNOWN)
        self.chain()
        for verdict in ("REFUSED", "CHAIN_STOPPED"):
            self.result(verdict, 0)
            self.assert_outcome(ws.WindowOutcome.CHAIN_FAILED)
        self.result("REHEARSAL_ONLY", 0)
        self.assert_outcome(ws.WindowOutcome.UNKNOWN)

    def test_fault_sources_are_structural_only(self):
        self.measured()
        for extra in ({"fault": True}, {"fault_reasons": ["secret marker"]}, {"faults": {"reasons": ["secret marker"]}}):
            with self.subTest(extra=extra):
                self.write("hazard_result.json", {"verdict": "GO", **extra, "joules": "DO_NOT_PRINT"})
                report = self.assert_outcome(ws.WindowOutcome.MEASURED_WITH_FLAGS)
                self.assertNotIn("secret marker", repr(report))
                self.assertNotIn("DO_NOT_PRINT", repr(report))
        self.write("hazard_result.json", {"verdict": "GO", "fault": False, "fault_reasons": [], "faults": {"reasons": []}})
        self.assert_outcome(ws.WindowOutcome.MEASURED_OK)

    def test_invalid_objects_types_and_vocabulary_never_succeed(self):
        self.measured()
        cases = [
            ("result.json", {}), ("result.json", {"verdict": "GO"}),
            ("result.json", {"verdict": [], "chain_exit_code": 0}),
            ("result.json", {"verdict": "PASS", "chain_exit_code": 0}),
            ("result.json", {"verdict": "GO", "chain_exit_code": False}),
            ("result.json", {"verdict": "GO", "chain_exit_code": "0"}),
            ("hazard_result.json", []), ("hazard_result.json", {"verdict": "GO", "chain": []}),
            ("hazard_result.json", {"verdict": "GO", "faults": []}),
            ("hazard_result.json", {"verdict": "GO", "fault": 1}),
            ("hazard_result.json", {"verdict": "GO", "fault_reasons": "bad"}),
            ("hazard_result.json", {"verdict": "GO", "faults": {"reasons": [1]}}),
            ("hazard_result.json", {"verdict": "GO", "measurement_outcome": "absent"}),
            ("hazard_result.json", {"verdict": "GO", "chain_outcome": "SUCCESS"}),
            ("chain.exited", {}), ("chain.exited", {"exit_code": 0.0}),
            ("r1_result.json", {}), ("r1_result.json", {"status": "COMPLETE"}),
            ("r1_result.json", {"status": []}), ("courier.json", {"sent": "yes"}),
            ("courier.delivery.json", {"transport": "future"}),
            ("courier.delivery.json", {"message_id": ""}),
        ]
        for name, value in cases:
            with self.subTest(name=name, value=value):
                prior = (self.night / name).read_bytes() if (self.night / name).exists() else None
                self.write(name, value)
                self.assert_outcome(ws.WindowOutcome.UNKNOWN)
                if prior is None:
                    (self.night / name).unlink()
                else:
                    (self.night / name).write_bytes(prior)

    def test_conflicting_structural_sources(self):
        self.measured()
        self.write("hazard_result.json", {"verdict": "REFUSED"})
        self.assertIn("CONFLICTING_VERDICTS", self.assert_outcome(ws.WindowOutcome.UNKNOWN).reasons)
        self.write("hazard_result.json", {"verdict": "GO", "chain": {"exit_code": 3}})
        self.assertIn("CONFLICTING_CHAIN_EXITS", self.assert_outcome(ws.WindowOutcome.UNKNOWN).reasons)
        self.write("hazard_result.json", {"verdict": "GO", "chain": {"exit_code": None}})
        self.assert_outcome(ws.WindowOutcome.UNKNOWN)

    def test_bad_json_binary_duplicate_nonfinite_and_oversize(self):
        self.measured()
        bad_records = [b"{", b"null", b"[]", b"42", b'"GO"', b"\xff", b'{"verdict":"GO","verdict":"REFUSED"}',
                       b'{"verdict":"GO","chain_exit_code":NaN}', b"[" * 2000, b" " * (4 * 1024 * 1024 + 1)]
        for raw in bad_records:
            with self.subTest(prefix=raw[:30]):
                (self.night / "refusal.json").write_bytes(raw)
                self.assert_outcome(ws.WindowOutcome.UNKNOWN)

    def test_io_failures_no_exception_or_sensitive_diagnostics(self):
        self.measured()
        original = os.open

        def fail_result(path, *args, **kwargs):
            if path == "result.json":
                raise PermissionError("SENSITIVE_VALUE")
            return original(path, *args, **kwargs)

        with patch.object(ws.os, "open", side_effect=fail_result):
            report = self.assert_outcome(ws.WindowOutcome.UNKNOWN)
        self.assertNotIn("SENSITIVE_VALUE", repr(report))
        self.assertIs(ws.window_outcome(self.root / "missing").outcome, ws.WindowOutcome.UNKNOWN)
        self.assertIs(ws.window_outcome(self.night / "result.json").outcome, ws.WindowOutcome.UNKNOWN)
        (self.night / "refusal.json").mkdir()
        self.assert_outcome(ws.WindowOutcome.UNKNOWN)

    def test_symlinks_are_rejected_without_opening_targets(self):
        self.measured()
        with tempfile.TemporaryDirectory() as directory:
            external = Path(directory)
            (external / "payload.json").write_text('{"status":"complete"}')
            (self.night / "r1_result.json").symlink_to(external / "payload.json")
            report = self.assert_outcome(ws.WindowOutcome.UNKNOWN)
            self.assertIn("r1_result.json:NOT_REGULAR_FILE", report.reasons)
            (self.night / "r1_result.json").unlink()
            (self.night / "align-r1").symlink_to(external, target_is_directory=True)
            self.assert_outcome(ws.WindowOutcome.UNKNOWN)
            link = self.root / "link"
            link.symlink_to(self.night, target_is_directory=True)
            self.assertIs(ws.window_outcome(link).outcome, ws.WindowOutcome.UNKNOWN)
            self.assert_outcome(ws.WindowOutcome.UNKNOWN, payload_path=link / "r1_result.json")
            root_link = self.root / "root-link"
            root_link.symlink_to(self.root, target_is_directory=True)
            self.assertEqual(ws.observe_night_dir(root_link).errors[0], "DIRECTORY_UNREADABLE_OR_UNSAFE")

    def test_read_races_do_not_follow_symlink_or_accept_disappearance(self):
        self.measured()
        self.write("r1_result.json", {"status": "complete"})
        self.touch("r1_slots.json")
        target = self.root / "synthetic-external.json"
        target.write_text('{"status":"complete"}')
        original = os.open

        def swap_to_symlink(path, *args, **kwargs):
            if path == "r1_result.json":
                (self.night / path).unlink()
                (self.night / path).symlink_to(target)
            return original(path, *args, **kwargs)

        with patch.object(ws.os, "open", side_effect=swap_to_symlink):
            self.assert_outcome(ws.WindowOutcome.UNKNOWN)
        (self.night / "r1_result.json").unlink()
        self.write("hazard_result.json", {"verdict": "GO"})

        def disappear(path, *args, **kwargs):
            if path == "hazard_result.json":
                (self.night / path).unlink()
            return original(path, *args, **kwargs)

        with patch.object(ws.os, "open", side_effect=disappear):
            report = self.assert_outcome(ws.WindowOutcome.UNKNOWN)
        self.assertIn("hazard_result.json:DISAPPEARED_DURING_READ", report.reasons)

    def test_file_replaced_by_directory_after_stat_is_rejected(self):
        self.measured()
        original = os.open

        def swap_to_directory(path, *args, **kwargs):
            if path == "result.json":
                (self.night / path).unlink()
                (self.night / path).mkdir()
            return original(path, *args, **kwargs)

        with patch.object(ws.os, "open", side_effect=swap_to_directory):
            report = self.assert_outcome(ws.WindowOutcome.UNKNOWN)
        self.assertIn("result.json:NOT_REGULAR_FILE", report.reasons)

    def test_reader_ignores_embedded_paths_and_unlisted_files(self):
        self.measured()
        self.result(payload_path="/DO_NOT_OPEN", artifacts=[{"path": "/DO_NOT_OPEN"}], joules="SECRET")
        (self.night / "unlisted.json").write_text("invalid")
        (self.root / "night_plan.json").write_text(json.dumps({"t0_epoch_s": 1, "window_max_s": 2, "custody_root": "/DO_NOT_OPEN"}))
        with patch.object(Path, "iterdir", side_effect=AssertionError("enumeration")), patch.object(Path, "glob", side_effect=AssertionError("enumeration")):
            report = self.assert_outcome(ws.WindowOutcome.MEASURED_OK)
        self.assertNotIn("SECRET", repr(report))
        self.assertNotIn("/DO_NOT_OPEN", repr(report))
        self.assertNotIn("night_plan.json", report.evidence["markers"])

    def test_observation_preserves_bytes_and_never_contacts_a_host(self):
        self.measured()
        self.write("r1_result.json", {"status": "complete", "measurement": "synthetic-unused"})
        self.touch("r1_slots.json")
        paths = list(self.night.iterdir())
        before = {p.name: p.read_bytes() for p in paths}
        original = os.open

        def readonly_open(path, flags, *args, **kwargs):
            self.assertFalse(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
            return original(path, flags, *args, **kwargs)

        with patch.object(ws.os, "open", side_effect=readonly_open), \
                patch("subprocess.run", side_effect=AssertionError("process")), \
                patch("subprocess.Popen", side_effect=AssertionError("process")), \
                patch("socket.socket", side_effect=AssertionError("network")):
            self.assertIs(ws.derive_window_state(self.observe(), 0).outcome.outcome, ws.WindowOutcome.MEASURED_OK)
            self.assert_outcome(ws.WindowOutcome.MEASURED_OK)
        self.assertEqual(before, {p.name: p.read_bytes() for p in paths})

    def test_plan_timing_and_file_only_declaration(self):
        self.result("REFUSED", None, ended_epoch_s=50)
        plan = self.root / "night_plan.json"
        plan.write_text(json.dumps({"t0_epoch_s": 100, "window_max_s": 200, "courier_mode": "file-only"}))
        observed = self.observe()
        self.assertEqual(observed.completion_epoch_s, 600)
        self.assertFalse(observed.delivery_required)
        self.assertIs(ws.derive_window_state(observed, 0).state, ws.WindowState.DELIVERED)
        plan.unlink()
        self.assertEqual(self.observe().completion_epoch_s, 50)
        for value in ({"t0_epoch_s": True, "window_max_s": 2}, {"t0_epoch_s": 1, "window_max_s": -1},
                      {"t0_epoch_s": 1}, {}, {"t0_epoch_s": 10 ** 400, "window_max_s": 1},
                      {"t0_epoch_s": 1e308, "window_max_s": 1e308},
                      {"t0_epoch_s": 1, "window_max_s": 2, "courier_mode": "unknown"}):
            plan.write_text(json.dumps(value))
            self.assertTrue(self.observe().errors)

    def test_two_payload_locations_each_need_slots(self):
        self.measured()
        for name in ("r1_result.json", "align-r1/r1_result.json"):
            self.write(name, {"status": "complete"})
        self.touch("align-r1/r1_slots.json")
        self.assert_outcome(ws.WindowOutcome.MEASURED_WITH_FLAGS)
        self.touch("r1_slots.json")
        self.assert_outcome(ws.WindowOutcome.MEASURED_OK)

    def test_pure_outcome_rejects_unknown_vocabulary_even_without_reader(self):
        base = ws.Observation(markers={"result.json", "chain.started", "chain.exited"},
                              verdict="GO", chain_exit_code=0)
        report = ws.derive_window_state(replace(base, payload_status="future"), 0)
        self.assertIs(report.outcome.outcome, ws.WindowOutcome.UNKNOWN)
        report = ws.derive_window_state(replace(base, verdict="future"), 0)
        self.assertIs(report.outcome.outcome, ws.WindowOutcome.UNKNOWN)

    def test_courier_generations_delivery_and_file_only(self):
        self.measured()
        self.touch("courier.sent")
        self.write("courier.json", {"sent": True})
        self.assertIn("COURIER_SENT_WITHOUT_DELIVERY", self.outcome().violated_invariants)
        for key in ("message_id", "mail_message_id"):
            self.write("courier.json", {"sent": True, key: "synthetic-id"})
            self.assertNotIn("COURIER_SENT_WITHOUT_DELIVERY", self.outcome().violated_invariants)
        self.write("courier.json", {"sent": True})
        receipt = {"transport": "git-push", "ref": "refs/heads/night-results/synthetic", "commit": "a" * 40, "result_sha256": "b" * 64}
        self.write("courier.delivery.json", receipt)
        self.assertTrue(self.observe().delivery_recorded)
        self.assertNotIn("COURIER_SENT_WITHOUT_DELIVERY", self.outcome().violated_invariants)
        for key, value in (("commit", "x" * 40), ("result_sha256", "a"), ("ref", "main")):
            self.write("courier.delivery.json", dict(receipt, **{key: value}))
            self.assert_outcome(ws.WindowOutcome.UNKNOWN)
        self.write("courier.delivery.json", {"transport": "git-push"})
        self.assert_outcome(ws.WindowOutcome.UNKNOWN)
        self.write("courier.delivery.json", {"transport": "file"})
        self.assertFalse(self.observe().delivery_recorded)
        self.write("courier.delivery.json", {"transport": "mail", "message_id": "synthetic-id"})
        self.assertTrue(self.observe().delivery_recorded)

    def test_bad_arguments(self):
        for value in (None, 42, []):
            with self.assertRaises(TypeError):
                self.outcome(payload_path=value) if value is not None else ws.window_outcome(None)
        for plists in ([], {"other": ws.PlistFacts()}, {ws.LABELS[0]: True}):
            with self.assertRaises(TypeError):
                self.observe(plists=plists)
        with self.assertRaises(TypeError):
            ws.PlistFacts(loaded=1)
        with self.assertRaises(TypeError):
            ws.Observation(plists=())
        for observation, now in ((None, 0), (ws.Observation(), None), (ws.Observation(), float("nan")), (ws.Observation(), True)):
            with self.assertRaises(TypeError):
                ws.derive_window_state(observation, now)

    def test_cli_all_exit_classes_and_no_measurements(self):
        self.measured()
        self.result(joules="NEVER_PRINT", ended_epoch_s=1)
        for extra, expected in (({}, 0), ({"fault": True}, 1), ({"verdict": "future"}, 2)):
            self.result(**extra, joules="NEVER_PRINT", ended_epoch_s=1)
            output = io.StringIO()
            with redirect_stdout(output):
                code = ws.main([str(self.root), "--json"])
            self.assertEqual(code, expected)
            parsed = json.loads(output.getvalue())
            self.assertIn("state", parsed)
            self.assertIn("outcome", parsed)
            self.assertIn("violated_invariants", parsed)
            self.assertNotIn("NEVER_PRINT", output.getvalue())
        self.result("REFUSED", None)
        (self.night / "chain.started").unlink()
        (self.night / "chain.exited").unlink()
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(ws.main([str(self.root)]), 1)
        self.assertIn("REFUSED_PRE_CHAIN", output.getvalue())
        command = subprocess.run([sys.executable, "-B", "-m", "joulewise.window_state", str(self.root), "--json"],
                                 capture_output=True, text=True, timeout=10)
        self.assertEqual(command.returncode, 1, command.stderr)
        self.assertEqual(json.loads(command.stdout)["outcome"], "REFUSED_PRE_CHAIN")
        usage = subprocess.run([sys.executable, "-B", "-m", "joulewise.window_state"], capture_output=True, timeout=10)
        self.assertEqual(usage.returncode, 2)


if __name__ == "__main__":
    unittest.main()
