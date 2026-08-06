"""Commit-1 tests for the inactive root-owned quiet-guard lease engine."""

from __future__ import annotations

import fcntl
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import joulewise.quiet_guard as guard_module
from joulewise.quiet_guard import (
    ACTORS,
    APP_QUIT_TIMEOUT_S,
    CONFIG_SCHEMA,
    FAILURE_CAUSES,
    FAILURE_SCHEMA,
    FAILURE_SIGNATURES,
    GuardEngine,
    GuardError,
    POWERMETRICS_PROBE,
    PRODUCTION_STATE_ROOT,
    RECOVERY_ACKNOWLEDGMENT,
    KILL_WAIT_TIMEOUT_S,
    SESSION_EXIT_TIMEOUT_S,
    STATES,
    TERM_WAIT_TIMEOUT_S,
    TRANSITION_TABLE,
    _atomic_write_json,
    agent_launch_refusal,
    canonical_json_bytes,
    failure_mapping,
    transition_rule,
)
from joulewise.quiet_guard_process import (
    AncestorIdentity,
    ProcessIdentity,
    SnapshotProcessSource,
    argv_digest,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
FORBIDDEN_WRITE_PARTS = (
    ".codex-bridge",
    "runs",
    "RUN_STATE.md",
    "TASK_QUEUE.md",
    "decision_log.md",
    "audit",
    "manifest",
    "run-bundle",
    ".log",
)

EXPECTED_TRANSITIONS = {
    ("idle", "handoff_pending", "initiating_session"),
    ("handoff_pending", "quiet_held", "watcher"),
    ("handoff_pending", "recovery_required", "watcher"),
    ("quiet_held", "recovery_required", "watcher"),
    ("idle", "recovery_required", "engine"),
    ("handoff_pending", "recovery_required", "engine"),
    ("quiet_held", "recovery_required", "engine"),
    ("quiet_held", "idle", "watcher"),
    ("recovery_required", "idle", "recovery"),
}

EXPECTED_FAILURE_CAUSES = {
    "t3_char_pair_verdict_missing",
    "live_promotion_disabled",
    "schema_mismatch",
    "host_mismatch",
    "boot_mismatch",
    "malformed_json",
    "lock_unavailable",
    "invalid_transition",
    "epoch_regression",
    "registry_invalid",
    "lease_invalid",
    "identity_mismatch",
    "stale_registry",
    "pid_reuse_detected",
    "recovery_acknowledgment_missing",
    "processes_remain",
    "independent_census_nonzero",
    "agent_launch_blocked",
    "privileged_command_refused",
}

EXPECTED_FAILURE_SIGNATURES = {
    "t3_char_pair_verdict_missing": "quiet_guard/t3_char_pair_verdict_missing/v1",
    "live_promotion_disabled": "quiet_guard/live_promotion_disabled/v1",
    "schema_mismatch": "quiet_guard/schema_mismatch/v1",
    "host_mismatch": "quiet_guard/host_mismatch/v1",
    "boot_mismatch": "quiet_guard/boot_mismatch/v1",
    "malformed_json": "quiet_guard/malformed_json/v1",
    "lock_unavailable": "quiet_guard/lock_unavailable/v1",
    "invalid_transition": "quiet_guard/invalid_transition/v1",
    "epoch_regression": "quiet_guard/epoch_regression/v1",
    "registry_invalid": "quiet_guard/registry_invalid/v1",
    "lease_invalid": "quiet_guard/lease_invalid/v1",
    "identity_mismatch": "quiet_guard/identity_mismatch/v1",
    "stale_registry": "quiet_guard/stale_registry/v1",
    "pid_reuse_detected": "quiet_guard/pid_reuse_detected/v1",
    "recovery_acknowledgment_missing": "quiet_guard/recovery_acknowledgment_missing/v1",
    "processes_remain": "quiet_guard/processes_remain/v1",
    "independent_census_nonzero": "quiet_guard/independent_census_nonzero/v1",
    "agent_launch_blocked": "quiet_guard/agent_launch_blocked/v1",
    "privileged_command_refused": "quiet_guard/privileged_command_refused/v1",
}


def identity(
    pid: int = 101,
    *,
    start: str = "boot+1",
    executable: str = "/Applications/T3 Code (Alpha).app/Contents/MacOS/t3",
    argv: tuple[str, ...] = ("t3", "--thread", "abc"),
    ancestry: tuple[AncestorIdentity, ...] = (),
) -> ProcessIdentity:
    return ProcessIdentity(pid, start, executable, argv_digest(argv), ancestry)


def load_script(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / relative)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class EngineTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(
            prefix=guard_module.TEST_STATE_ROOT_PREFIX
        )
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "guard-state"
        self.engine = GuardEngine(
            self.root, host_id="host-A", boot_id="boot-A", test_mode=True
        )
        self.engine.initialize_inactive()
        self.owner = identity()

    def pending(self, *, entries=()) -> dict:
        return self.engine.transition(
            "handoff_pending",
            "initiating_session",
            owner=self.owner,
            registry_entries=entries,
        )

    def recovery_with_stale_owner(self) -> dict:
        self.pending(entries=(self.owner,))
        return self.engine.audit_registry(SnapshotProcessSource(), ())


class InstallationTests(EngineTestCase):
    def test_installation_is_explicitly_inactive(self) -> None:
        status = self.engine.status()
        self.assertEqual(status["config"]["schema"], CONFIG_SCHEMA)
        self.assertIs(status["config"]["live_promotion"], False)
        self.assertIsNone(status["config"]["t3_char_pair_verdict"])
        self.assertEqual(tuple(status["config"]["powermetrics_probe"]), POWERMETRICS_PROBE)
        self.assertEqual(status["state"]["state"], "idle")
        self.assertIsNone(status["state"]["lease"])

    def test_ratified_timeout_constants_are_pinned_but_not_executed(self) -> None:
        self.assertEqual(
            (
                SESSION_EXIT_TIMEOUT_S,
                APP_QUIT_TIMEOUT_S,
                TERM_WAIT_TIMEOUT_S,
                KILL_WAIT_TIMEOUT_S,
            ),
            (120, 30, 10, 5),
        )

    def test_arm_refuses_with_ratified_canonical_cause(self) -> None:
        refusal = self.engine.arm_refusal()
        self.assertEqual(refusal["cause"], "t3_char_pair_verdict_missing")
        self.assertEqual(
            refusal["signature"],
            "quiet_guard/t3_char_pair_verdict_missing/v1",
        )
        with self.assertRaisesRegex(GuardError, "T3-CHAR-PAIR-01"):
            self.engine.arm()

    def test_non_test_engine_cannot_create_a_lease(self) -> None:
        production_shaped = GuardEngine(
            self.root, host_id="host-A", boot_id="boot-A", test_mode=False
        )
        with self.assertRaises(GuardError) as caught:
            production_shaped.transition(
                "handoff_pending", "initiating_session", owner=self.owner
            )
        self.assertEqual(caught.exception.cause, "live_promotion_disabled")
        self.assertIsNone(production_shaped.read_state()["lease"])

    def test_production_initializer_is_setup_only(self) -> None:
        engine = GuardEngine(
            PRODUCTION_STATE_ROOT,
            host_id="host-A",
            boot_id="boot-A",
        )
        with self.assertRaises(GuardError) as caught:
            engine.initialize_inactive()
        self.assertEqual(caught.exception.cause, "privileged_command_refused")

    def test_test_mode_cannot_target_production_root(self) -> None:
        with self.assertRaises(GuardError):
            GuardEngine(
                PRODUCTION_STATE_ROOT,
                host_id="host-A",
                boot_id="boot-A",
                test_mode=True,
            )

    def test_initialization_does_not_overwrite_existing_install(self) -> None:
        before = self.engine.paths.state.read_bytes()
        with self.assertRaises(GuardError):
            self.engine.initialize_inactive()
        self.assertEqual(self.engine.paths.state.read_bytes(), before)

    def test_non_test_arbitrary_root_cannot_initialize(self) -> None:
        arbitrary = GuardEngine(
            self.root / "other", host_id="host-A", boot_id="boot-A", test_mode=False
        )
        with self.assertRaises(GuardError) as caught:
            arbitrary.initialize_inactive()
        self.assertEqual(caught.exception.cause, "privileged_command_refused")
        self.assertFalse(arbitrary.paths.root.exists())


class FailureCauseTests(unittest.TestCase):
    def test_every_cause_has_one_stable_signature(self) -> None:
        self.assertEqual(set(FAILURE_CAUSES), EXPECTED_FAILURE_CAUSES)
        self.assertEqual(FAILURE_SIGNATURES, EXPECTED_FAILURE_SIGNATURES)
        self.assertEqual(len(FAILURE_SIGNATURES), len(set(FAILURE_SIGNATURES.values())))
        for cause in EXPECTED_FAILURE_CAUSES:
            payload = failure_mapping(cause, "detail")
            self.assertEqual(payload["schema"], FAILURE_SCHEMA)
            self.assertEqual(payload["signature"], EXPECTED_FAILURE_SIGNATURES[cause])

    def test_unknown_failure_cause_is_never_serialized(self) -> None:
        with self.assertRaises(ValueError):
            failure_mapping("wording_changed_to_reset_retries")


class TransitionTableTests(EngineTestCase):
    def test_every_legal_and_illegal_combination_is_table_owned(self) -> None:
        self.assertEqual(set(TRANSITION_TABLE), EXPECTED_TRANSITIONS)
        observed = set()
        for source in STATES:
            for target in STATES:
                for actor in ACTORS:
                    rule = transition_rule(source, target, actor)
                    key = (source, target, actor)
                    if key in EXPECTED_TRANSITIONS:
                        self.assertIsNotNone(rule, key)
                        observed.add(key)
                    else:
                        self.assertIsNone(rule, key)
        self.assertEqual(observed, EXPECTED_TRANSITIONS)

    def test_initiating_session_can_create_only_handoff_pending(self) -> None:
        for target in STATES:
            allowed = transition_rule("idle", target, "initiating_session")
            self.assertEqual(allowed is not None, target == "handoff_pending")

    def test_only_watcher_can_enter_quiet_held(self) -> None:
        for source in STATES:
            for actor in ACTORS:
                allowed = transition_rule(source, "quiet_held", actor)
                self.assertEqual(
                    allowed is not None,
                    source == "handoff_pending" and actor == "watcher",
                )

    def test_two_phase_handoff_requires_both_zero_proofs(self) -> None:
        self.pending(entries=(self.owner,))
        with self.assertRaises(GuardError) as registered:
            self.engine.transition(
                "quiet_held",
                "watcher",
                independent_census_zero=True,
            )
        self.assertEqual(registered.exception.cause, "processes_remain")
        with self.assertRaises(GuardError) as census:
            self.engine.transition(
                "quiet_held", "watcher", registry_entries=()
            )
        self.assertEqual(census.exception.cause, "independent_census_nonzero")
        state = self.engine.transition(
            "quiet_held",
            "watcher",
            registry_entries=(),
            independent_census_zero=True,
        )
        self.assertEqual(state["state"], "quiet_held")

    def test_illegal_transition_refuses_without_mutation(self) -> None:
        before = self.engine.paths.state.read_bytes()
        with self.assertRaises(GuardError) as caught:
            self.engine.transition("quiet_held", "initiating_session")
        self.assertEqual(caught.exception.cause, "invalid_transition")
        self.assertEqual(self.engine.paths.state.read_bytes(), before)

    def test_recovery_transition_cannot_bypass_recover_method(self) -> None:
        self.recovery_with_stale_owner()
        with self.assertRaises(GuardError) as caught:
            self.engine.transition("idle", "recovery")
        self.assertEqual(caught.exception.cause, "invalid_transition")

    def test_monotonic_epoch_and_event_sequence(self) -> None:
        pending = self.pending()
        held = self.engine.transition(
            "quiet_held",
            "watcher",
            registry_entries=(),
            independent_census_zero=True,
        )
        idle = self.engine.transition("idle", "watcher")
        self.assertEqual((pending["epoch"], held["epoch"], idle["epoch"]), (1, 2, 3))
        self.assertEqual([event["epoch"] for event in idle["events"]], [1, 2, 3])
        self.assertEqual(idle["registry"]["epoch"], 3)

    def test_no_ttl_release_exists(self) -> None:
        pending = self.pending()
        serialized = canonical_json_bytes(pending).decode()
        self.assertNotIn("ttl", serialized.lower())
        self.assertNotIn("expires", serialized.lower())
        self.assertEqual(self.engine.read_state()["state"], "handoff_pending")
        self.assertEqual(self.engine.read_state()["lease"], pending["lease"])

    def test_recovery_and_both_handoff_states_block_agent_launch(self) -> None:
        self.assertIsNone(agent_launch_refusal(self.engine.read_state()))
        pending = self.pending()
        self.assertEqual(agent_launch_refusal(pending)["cause"], "agent_launch_blocked")
        held = self.engine.transition(
            "quiet_held",
            "watcher",
            registry_entries=(),
            independent_census_zero=True,
        )
        self.assertEqual(agent_launch_refusal(held)["cause"], "agent_launch_blocked")
        recovery = self.engine.transition("recovery_required", "watcher")
        self.assertEqual(agent_launch_refusal(recovery)["cause"], "agent_launch_blocked")


class ValidationTests(EngineTestCase):
    def rewrite_state(self, mutate) -> None:
        raw = json.loads(self.engine.paths.state.read_text())
        mutate(raw)
        self.engine.paths.state.write_text(json.dumps(raw))

    def test_state_schema_mismatch_refuses(self) -> None:
        self.rewrite_state(lambda raw: raw.__setitem__("schema", "future"))
        with self.assertRaises(GuardError) as caught:
            self.engine.read_state()
        self.assertEqual(caught.exception.cause, "schema_mismatch")

    def test_host_mismatch_refuses(self) -> None:
        self.rewrite_state(lambda raw: raw.__setitem__("host_id", "host-B"))
        with self.assertRaises(GuardError) as caught:
            self.engine.read_state()
        self.assertEqual(caught.exception.cause, "host_mismatch")

    def test_boot_mismatch_refuses(self) -> None:
        self.rewrite_state(lambda raw: raw.__setitem__("boot_id", "boot-B"))
        with self.assertRaises(GuardError) as caught:
            self.engine.read_state()
        self.assertEqual(caught.exception.cause, "boot_mismatch")

    def test_config_host_mismatch_refuses(self) -> None:
        raw = json.loads(self.engine.paths.config.read_text())
        raw["host_id"] = "host-B"
        self.engine.paths.config.write_text(json.dumps(raw))
        with self.assertRaises(GuardError) as caught:
            self.engine.read_config()
        self.assertEqual(caught.exception.cause, "host_mismatch")

    def test_malformed_json_refuses(self) -> None:
        self.engine.paths.state.write_bytes(b'{"schema":')
        with self.assertRaises(GuardError) as caught:
            self.engine.read_state()
        self.assertEqual(caught.exception.cause, "malformed_json")

    def test_truncated_utf8_refuses(self) -> None:
        self.engine.paths.state.write_bytes(b"\xff")
        with self.assertRaises(GuardError) as caught:
            self.engine.read_state()
        self.assertEqual(caught.exception.cause, "malformed_json")

    def test_epoch_rollback_refuses(self) -> None:
        self.pending()
        self.rewrite_state(lambda raw: raw.__setitem__("epoch", 0))
        with self.assertRaises(GuardError) as caught:
            self.engine.read_state()
        self.assertEqual(caught.exception.cause, "epoch_regression")

    def test_registry_identity_is_strictly_validated(self) -> None:
        self.pending(entries=(self.owner,))
        self.rewrite_state(
            lambda raw: raw["registry"]["entries"][0].__setitem__("name_pattern", "t3*")
        )
        with self.assertRaises(GuardError) as caught:
            self.engine.read_state()
        self.assertEqual(caught.exception.cause, "registry_invalid")

    def test_duplicate_registry_pid_refuses(self) -> None:
        self.pending(entries=(self.owner,))
        self.rewrite_state(
            lambda raw: raw["registry"]["entries"].append(
                dict(raw["registry"]["entries"][0])
            )
        )
        with self.assertRaises(GuardError) as caught:
            self.engine.read_state()
        self.assertEqual(caught.exception.cause, "registry_invalid")

    def test_lease_ttl_field_is_rejected(self) -> None:
        self.pending()
        self.rewrite_state(lambda raw: raw["lease"].__setitem__("ttl_s", 30))
        with self.assertRaises(GuardError) as caught:
            self.engine.read_state()
        self.assertEqual(caught.exception.cause, "lease_invalid")

    def test_lease_epoch_mismatch_refuses(self) -> None:
        self.pending()
        self.rewrite_state(lambda raw: raw["lease"].__setitem__("epoch", 0))
        with self.assertRaises(GuardError) as caught:
            self.engine.read_state()
        self.assertEqual(caught.exception.cause, "epoch_regression")

    def test_spliced_event_history_refuses(self) -> None:
        self.pending()
        self.engine.transition("recovery_required", "watcher")

        def splice(raw):
            raw["events"][1]["from_state"] = "idle"
            raw["events"][1]["actor"] = "engine"

        self.rewrite_state(splice)
        with self.assertRaises(GuardError) as caught:
            self.engine.read_state()
        self.assertEqual(caught.exception.cause, "epoch_regression")

    def test_verdict_digest_requires_lowercase_hex(self) -> None:
        config = json.loads(self.engine.paths.config.read_text())
        config["t3_char_pair_verdict"] = {
            "schema": "joulewise.t3_char_pair_verdict_ref/v1",
            "task_id": "T3-CHAR-PAIR-01",
            "verdict": "passed",
            "sha256": "sha256:" + "A" * 64,
        }
        self.engine.paths.config.write_text(json.dumps(config))
        with self.assertRaises(GuardError) as caught:
            self.engine.read_config()
        self.assertEqual(caught.exception.cause, "schema_mismatch")


class LockAndAtomicityTests(EngineTestCase):
    def test_lock_unavailable_is_canonical_refusal(self) -> None:
        descriptor = os.open(self.engine.paths.lock, os.O_RDWR | os.O_CREAT, 0o600)
        self.addCleanup(os.close, descriptor)
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        self.addCleanup(fcntl.flock, descriptor, fcntl.LOCK_UN)
        with self.assertRaises(GuardError) as caught:
            with self.engine.locked():
                pass
        self.assertEqual(caught.exception.cause, "lock_unavailable")

    def test_atomic_replace_flushes_file_then_directory(self) -> None:
        destination = self.root / "atomic.json"
        events: list[str] = []
        real_fsync = os.fsync
        real_replace = os.replace

        def fsync(descriptor):
            events.append("fsync")
            return real_fsync(descriptor)

        def replace(source, target):
            events.append("replace")
            self.assertEqual(Path(source).parent, Path(target).parent)
            return real_replace(source, target)

        with mock.patch.object(guard_module.os, "fsync", side_effect=fsync), mock.patch.object(
            guard_module.os, "replace", side_effect=replace
        ):
            _atomic_write_json(destination, {"value": 1})
        self.assertEqual(events, ["fsync", "replace", "fsync"])
        self.assertEqual(json.loads(destination.read_text()), {"value": 1})

    def test_failed_replace_preserves_prior_document_and_cleans_temp(self) -> None:
        destination = self.root / "atomic.json"
        _atomic_write_json(destination, {"value": 1})
        before = destination.read_bytes()
        with mock.patch.object(guard_module.os, "replace", side_effect=OSError("crash")):
            with self.assertRaises(OSError):
                _atomic_write_json(destination, {"value": 2})
        self.assertEqual(destination.read_bytes(), before)
        self.assertEqual(
            [path.name for path in self.root.iterdir() if path.name.startswith(".atomic.json")],
            [],
        )

    def test_directory_fsync_failure_is_not_reported_as_durable(self) -> None:
        destination = self.root / "atomic.json"
        real_fsync = os.fsync
        calls = 0

        def fail_directory(descriptor):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("directory fsync failed")
            return real_fsync(descriptor)

        with mock.patch.object(guard_module.os, "fsync", side_effect=fail_directory):
            with self.assertRaises(OSError):
                _atomic_write_json(destination, {"value": 1})
        self.assertEqual(calls, 2)


class StaleRecoveryTests(EngineTestCase):
    def test_matching_registry_stays_pending(self) -> None:
        self.pending(entries=(self.owner,))
        state = self.engine.audit_registry(
            SnapshotProcessSource((self.owner,)), (self.owner,)
        )
        self.assertEqual(state["state"], "handoff_pending")

    def test_absent_registered_identity_enters_recovery_required(self) -> None:
        state = self.recovery_with_stale_owner()
        self.assertEqual(state["state"], "recovery_required")
        self.assertEqual(state["events"][-1]["cause"], "stale_registry")
        self.assertIsNotNone(state["lease"])

    def test_pid_reuse_enters_recovery_and_records_observation(self) -> None:
        self.pending(entries=(self.owner,))
        reused = identity(self.owner.pid, start="boot+99")
        state = self.engine.audit_registry(SnapshotProcessSource((reused,)), ())
        self.assertEqual(state["events"][-1]["cause"], "pid_reuse_detected")
        evidence = state["events"][-1]["evidence"]["revalidation"][0]
        self.assertEqual(evidence["result"], "pid_reused")
        self.assertEqual(evidence["observed"], reused.to_mapping())

    def test_recovery_requires_exact_acknowledgment(self) -> None:
        self.recovery_with_stale_owner()
        with self.assertRaises(GuardError) as caught:
            self.engine.recover(
                acknowledgment="yes",
                acknowledged_by="Ed",
                source=SnapshotProcessSource(),
                independent_census_rows=(),
            )
        self.assertEqual(caught.exception.cause, "recovery_acknowledgment_missing")

    def test_recovery_refuses_while_exact_registered_process_remains(self) -> None:
        self.recovery_with_stale_owner()
        with self.assertRaises(GuardError) as caught:
            self.engine.recover(
                acknowledgment=RECOVERY_ACKNOWLEDGMENT,
                acknowledged_by="Ed",
                source=SnapshotProcessSource((self.owner,)),
                independent_census_rows=(),
            )
        self.assertEqual(caught.exception.cause, "processes_remain")

    def test_recovery_refuses_nonzero_independent_census(self) -> None:
        self.recovery_with_stale_owner()
        unknown = identity(202)
        with self.assertRaises(GuardError) as caught:
            self.engine.recover(
                acknowledgment=RECOVERY_ACKNOWLEDGMENT,
                acknowledged_by="lead",
                source=SnapshotProcessSource(),
                independent_census_rows=(unknown,),
            )
        self.assertEqual(caught.exception.cause, "independent_census_nonzero")

    def test_acknowledged_zero_proof_clears_and_records_exact_abandonment(self) -> None:
        recovery = self.recovery_with_stale_owner()
        lease_id = recovery["lease"]["lease_id"]
        state = self.engine.recover(
            acknowledgment=RECOVERY_ACKNOWLEDGMENT,
            acknowledged_by="Ed",
            source=SnapshotProcessSource(),
            independent_census_rows=(),
        )
        self.assertEqual(state["state"], "idle")
        self.assertEqual(state["registry"]["entries"], [])
        self.assertIsNone(state["lease"])
        event = state["events"][-1]
        self.assertEqual(event["lease_id"], lease_id)
        self.assertEqual(event["evidence"]["acknowledged_by"], "Ed")
        self.assertEqual(
            event["evidence"]["abandoned_exact_identities"][0]["expected"],
            self.owner.to_mapping(),
        )

    def test_pid_reuse_can_clear_only_after_zero_census_and_is_preserved(self) -> None:
        self.pending(entries=(self.owner,))
        reused = identity(self.owner.pid, start="boot+99")
        self.engine.audit_registry(SnapshotProcessSource((reused,)), ())
        state = self.engine.recover(
            acknowledgment=RECOVERY_ACKNOWLEDGMENT,
            acknowledged_by="lead",
            source=SnapshotProcessSource((reused,)),
            independent_census_rows=(),
        )
        abandoned = state["events"][-1]["evidence"]["abandoned_exact_identities"][0]
        self.assertEqual(abandoned["result"], "pid_reused")
        self.assertEqual(abandoned["observed"], reused.to_mapping())


class BindingRecoveryTests(EngineTestCase):
    def test_cross_reboot_status_reports_and_acknowledged_recovery_rebinds(self) -> None:
        rebooted = GuardEngine(
            self.root, host_id="host-A", boot_id="boot-B", test_mode=False
        )
        status = rebooted.status()
        self.assertEqual(status["binding"]["status"], "recovery_required")
        self.assertEqual(status["binding"]["causes"], ["boot_mismatch"])
        state = rebooted.recover(
            acknowledgment=RECOVERY_ACKNOWLEDGMENT,
            acknowledged_by="Ed",
            source=SnapshotProcessSource(),
            independent_census_rows=(),
        )
        self.assertEqual((state["host_id"], state["boot_id"], state["state"]), ("host-A", "boot-B", "idle"))
        self.assertIsNone(state["lease"])
        self.assertEqual(rebooted.status()["binding"]["status"], "current")
        self.assertIs(rebooted.read_config()["live_promotion"], False)

    def test_hostname_drift_acknowledged_recovery_rebinds(self) -> None:
        renamed = GuardEngine(
            self.root, host_id="host-B", boot_id="boot-A", test_mode=False
        )
        self.assertEqual(renamed.status()["binding"]["causes"], ["host_mismatch"])
        state = renamed.recover(
            acknowledgment=RECOVERY_ACKNOWLEDGMENT,
            acknowledged_by="lead",
            source=SnapshotProcessSource(),
            independent_census_rows=(),
        )
        self.assertEqual((state["host_id"], state["boot_id"], state["state"]), ("host-B", "boot-A", "idle"))
        self.assertEqual([event["from_state"] for event in state["events"]], ["idle", "recovery_required"])
        self.assertEqual([event["to_state"] for event in state["events"]], ["recovery_required", "idle"])


class ClientAndPrivilegeBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = load_script("quiet_guard_client_test", "scripts/quiet_guard.py")
        cls.helper = load_script("quiet_guard_helper_test", "scripts/quiet_guard_privileged.py")

    def test_runtime_privileged_command_is_sudo_noninteractive(self) -> None:
        command = self.client.privileged_command(("status",))
        self.assertEqual(command[:2], ("/usr/bin/sudo", "-n"))
        self.assertNotIn("-S", command)

    def test_arm_refuses_without_invoking_sudo(self) -> None:
        with mock.patch.object(self.client.subprocess, "run") as run, mock.patch("builtins.print"):
            exit_code = self.client.main(("arm",))
        self.assertEqual(exit_code, self.client.EXIT_REFUSED)
        run.assert_not_called()

    def test_test_initializer_refuses_production_root_without_sudo(self) -> None:
        with mock.patch.object(self.client.subprocess, "run") as run, mock.patch("builtins.print"):
            exit_code = self.client.main(
                (
                    "initialize-test",
                    "--state-root",
                    str(PRODUCTION_STATE_ROOT),
                    "--host-id",
                    "host",
                    "--boot-id",
                    "boot",
                )
            )
        self.assertEqual(exit_code, self.client.EXIT_REFUSED)
        run.assert_not_called()

    def test_test_initializer_refuses_arbitrary_non_tmp_root_without_writes(self) -> None:
        arbitrary = REPO_ROOT / "not-a-test-state-root"
        with mock.patch.object(self.client.subprocess, "run") as run, mock.patch(
            "builtins.print"
        ), mock.patch.object(self.client.GuardEngine, "initialize_inactive") as initialize:
            exit_code = self.client.main(
                (
                    "initialize-test",
                    "--state-root",
                    str(arbitrary),
                    "--host-id",
                    "host",
                    "--boot-id",
                    "boot",
                )
            )
        self.assertEqual(exit_code, self.client.EXIT_REFUSED)
        self.assertFalse(arbitrary.exists())
        initialize.assert_not_called()
        run.assert_not_called()

    def test_test_initializer_accepts_only_named_process_tmpdir_sandbox(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix=self.client.TEST_SANDBOX_PREFIX, dir=tempfile.gettempdir()
        ) as temporary:
            root = Path(temporary) / "state"
            with mock.patch.object(self.client.subprocess, "run") as run, mock.patch(
                "builtins.print"
            ):
                exit_code = self.client.main(
                    (
                        "initialize-test",
                        "--state-root",
                        str(root),
                        "--host-id",
                        "host",
                        "--boot-id",
                        "boot",
                    )
                )
            self.assertEqual(exit_code, self.client.EXIT_OK)
            self.assertEqual({path.name for path in root.iterdir()}, {"config.json", "state.json", "control.lock"})
            run.assert_not_called()

    def test_privileged_command_allowlist_has_no_exec_or_signal(self) -> None:
        self.assertEqual(
            self.helper.ALLOWED_COMMANDS,
            ("install-inactive", "status", "recover"),
        )

    def test_privileged_parser_rejects_non_allowlisted_command(self) -> None:
        with mock.patch("sys.stderr"), self.assertRaises(SystemExit):
            self.helper.parser().parse_args(("agent-exec",))

    def test_sanitized_environment_strips_credentials_and_loader_hooks(self) -> None:
        identity_row = self.helper.InvocationIdentity(
            uid=501,
            gid=20,
            groups=(20, 80),
            user="ed",
            home="/Users/ed",
            shell="/bin/zsh",
            cwd=Path("/tmp/work"),
        )
        environment = self.helper.sanitized_environment(
            identity_row,
            {
                "LANG": "en_US.UTF-8",
                "GITHUB_TOKEN": "secret",
                "PYTHONPATH": "/attacker",
                "DYLD_INSERT_LIBRARIES": "/attacker.dylib",
                "SUDO_COMMAND": "bad",
            },
        )
        self.assertEqual(environment["LANG"], "en_US.UTF-8")
        self.assertEqual(environment["PATH"], self.helper.SAFE_PATH)
        self.assertFalse(
            {"GITHUB_TOKEN", "PYTHONPATH", "DYLD_INSERT_LIBRARIES", "SUDO_COMMAND"}
            & set(environment)
        )

    def test_privilege_drop_order_and_complete_identity(self) -> None:
        identity_row = self.helper.InvocationIdentity(
            uid=501,
            gid=20,
            groups=(20, 80),
            user="ed",
            home="/Users/ed",
            shell="/bin/zsh",
            cwd=Path("/tmp/work"),
        )
        calls: list[tuple[str, object]] = []
        fake_environment = {"SECRET": "remove"}

        class Environment(dict):
            def clear(self):
                calls.append(("environment.clear", None))
                super().clear()

            def update(self, value):
                calls.append(("environment.update", dict(value)))
                super().update(value)

        with mock.patch.object(self.helper.os, "geteuid", return_value=0), mock.patch.object(
            self.helper.os, "setgroups", side_effect=lambda value: calls.append(("setgroups", value))
        ), mock.patch.object(
            self.helper.os, "setgid", side_effect=lambda value: calls.append(("setgid", value))
        ), mock.patch.object(
            self.helper.os, "setuid", side_effect=lambda value: calls.append(("setuid", value))
        ), mock.patch.object(
            self.helper.os, "chdir", side_effect=lambda value: calls.append(("chdir", value))
        ), mock.patch.object(self.helper.os, "environ", Environment(fake_environment)):
            result = self.helper.drop_privileges(identity_row, {"LANG": "C"})
        self.assertEqual(
            [name for name, _ in calls],
            ["setgroups", "setgid", "setuid", "chdir", "environment.clear", "environment.update"],
        )
        self.assertEqual(result["USER"], "ed")
        self.assertNotIn("SECRET", result)

    def test_nonroot_privilege_drop_refuses(self) -> None:
        identity_row = self.helper.InvocationIdentity(
            501, 20, (20,), "ed", "/Users/ed", "/bin/zsh", Path("/tmp")
        )
        with mock.patch.object(self.helper.os, "geteuid", return_value=501):
            with self.assertRaises(GuardError):
                self.helper.drop_privileges(identity_row, {})

    def test_executable_helper_pins_interpreter_and_rejects_path_poisoning(self) -> None:
        helper_path = REPO_ROOT / "scripts/quiet_guard_privileged.py"
        helper_source = helper_path.read_text()
        self.assertEqual(helper_source.splitlines()[0], "#!/usr/bin/python3 -E")
        self.assertNotIn("/usr/bin/env", helper_source)
        self.assertNotIn("REPOSITORY_ROOT", helper_source)
        self.assertIn('sys.path[:] = [_INSTALLED_LIBRARY, *_stdlib]', helper_source)
        self.assertTrue(os.access(helper_path, os.X_OK))
        with tempfile.TemporaryDirectory() as temporary:
            attacker = Path(temporary)
            marker = attacker / "attacker-ran"
            fake_python = attacker / "python3"
            fake_python.write_text(f"#!/bin/sh\n/usr/bin/touch '{marker}'\nexit 93\n")
            fake_python.chmod(0o755)
            environment = dict(os.environ, PATH=str(attacker), PYTHONPATH=str(attacker))
            completed = subprocess.run(
                (str(helper_path), "status"),
                cwd="/",
                env=environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertNotEqual(completed.returncode, 93)
            self.assertFalse(marker.exists())

    def test_executable_root_helper_enforces_exact_argv(self) -> None:
        helper_path = REPO_ROOT / "scripts/quiet_guard_privileged.py"
        environment = dict(os.environ, PYTHONPATH=str(REPO_ROOT))
        completed = subprocess.run(
            (sys.executable, str(helper_path), "status", "unexpected"),
            cwd="/",
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(completed.returncode, 2)
        self.assertIn(b"unrecognized arguments", completed.stderr)


class WriteBoundaryTests(EngineTestCase):
    def test_transition_writes_only_under_fake_state_root(self) -> None:
        destinations: list[Path] = []
        real_write = guard_module._atomic_write_json

        def tracked(path, value):
            destinations.append(Path(path))
            return real_write(path, value)

        with mock.patch.object(guard_module, "_atomic_write_json", side_effect=tracked):
            self.pending()
        self.assertTrue(destinations)
        for destination in destinations:
            destination.resolve().relative_to(self.root.resolve())
            rendered = str(destination)
            self.assertFalse(any(part in rendered for part in FORBIDDEN_WRITE_PARTS))

    def test_every_engine_write_open_is_confined_to_fake_root(self) -> None:
        opened_for_write: list[Path] = []
        real_open = os.open

        def tracked_open(path, flags, *args, **kwargs):
            if flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC):
                opened_for_write.append(Path(path))
            return real_open(path, flags, *args, **kwargs)

        with mock.patch.object(guard_module.os, "open", side_effect=tracked_open):
            self.pending()
        self.assertTrue(opened_for_write)
        for path in opened_for_write:
            path.resolve().relative_to(self.root.resolve())
            self.assertFalse(
                any(part in str(path) for part in FORBIDDEN_WRITE_PARTS), str(path)
            )

    def test_setup_is_only_interactive_sudo_artifact_and_stays_inactive(self) -> None:
        setup = (REPO_ROOT / "scripts/setup_quiet_guard.sh").read_text()
        client = (REPO_ROOT / "scripts/quiet_guard.py").read_text()
        helper = (REPO_ROOT / "scripts/quiet_guard_privileged.py").read_text()
        self.assertIn("sudo -v", setup)
        self.assertIn("install-inactive", setup)
        self.assertIn("live_promotion=false", setup)
        self.assertNotIn("systemsetup", setup)
        self.assertNotIn("sudo -v", client + helper)
        self.assertIn('"/usr/bin/sudo", "-n"', client)

    def test_setup_validates_and_installs_identical_root_staged_bytes(self) -> None:
        setup = (REPO_ROOT / "scripts/setup_quiet_guard.sh").read_text()
        for mutable_path in (
            "$REPO_ROOT/joulewise/quiet_guard.py",
            "$REPO_ROOT/joulewise/quiet_guard_process.py",
            "$REPO_ROOT/scripts/quiet_guard_privileged.py",
        ):
            self.assertEqual(setup.count(mutable_path), 1, mutable_path)
        validation_and_install = setup.split("# Parse the staged Python bytes", 1)[1]
        self.assertNotIn("$REPO_ROOT/", validation_and_install)
        self.assertIn('visudo -cf "$STAGE_ROOT/joulewise-quiet-guard.sudoers"', setup)
        self.assertIn('"$STAGE_ROOT/joulewise-quiet-guard.sudoers" "$SUDOERS_PATH"', setup)
        self.assertNotIn("recover --ack *", setup)
        self.assertIn("unsafe root-helper parent", setup)

    def test_commit_one_contains_no_launch_quit_or_measurement_command(self) -> None:
        sources = "\n".join(
            (REPO_ROOT / path).read_text()
            for path in (
                "joulewise/quiet_guard.py",
                "joulewise/quiet_guard_process.py",
                "scripts/quiet_guard.py",
                "scripts/quiet_guard_privileged.py",
            )
        )
        for forbidden in ("osascript", "caffeinate", "/usr/bin/open", "SIGTERM", "SIGKILL"):
            self.assertNotIn(forbidden, sources)


if __name__ == "__main__":
    unittest.main()
