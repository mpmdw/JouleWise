"""Commit-1 tests for the inactive root-owned quiet-guard lease engine."""

from __future__ import annotations

from contextlib import contextmanager
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid
from unittest import mock

import joulewise.quiet_guard as guard_module
from joulewise.quiet_guard import (
    ACTORS,
    CONFIG_SCHEMA,
    CUSTODY_ROOTS_SCHEMA,
    EVENT_SCHEMA,
    FAILURE_CAUSES,
    FAILURE_SCHEMA,
    FAILURE_SIGNATURES,
    GuardEngine,
    GuardError,
    POWERMETRICS_PROBE,
    PRODUCTION_STATE_ROOT,
    RECOVERY_ACKNOWLEDGMENT,
    LEASE_SCHEMA,
    SETUP_AUTHORITY_DECISION,
    STATE_FIELDS,
    STATE_FIELD_ROOT_RULES,
    STATE_SCHEMA,
    STATES,
    TRANSITION_TABLE,
    _atomic_write_json,
    canonical_json_bytes,
    failure_mapping,
    initial_state,
    transition_rule,
    validate_state,
)
from joulewise.quiet_guard_process import (
    AncestorIdentity,
    KernelProcessRecord,
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
    "custody_roots_invalid",
    "registry_invalid",
    "lease_invalid",
    "identity_mismatch",
    "stale_registry",
    "pid_reuse_detected",
    "recovery_acknowledgment_missing",
    "processes_remain",
    "independent_census_nonzero",
    "process_observation_unavailable",
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
    "custody_roots_invalid": "quiet_guard/custody_roots_invalid/v1",
    "registry_invalid": "quiet_guard/registry_invalid/v1",
    "lease_invalid": "quiet_guard/lease_invalid/v1",
    "identity_mismatch": "quiet_guard/identity_mismatch/v1",
    "stale_registry": "quiet_guard/stale_registry/v1",
    "pid_reuse_detected": "quiet_guard/pid_reuse_detected/v1",
    "recovery_acknowledgment_missing": "quiet_guard/recovery_acknowledgment_missing/v1",
    "processes_remain": "quiet_guard/processes_remain/v1",
    "independent_census_nonzero": "quiet_guard/independent_census_nonzero/v1",
    "process_observation_unavailable": "quiet_guard/process_observation_unavailable/v1",
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
            self.root,
            host_id="host-A",
            boot_id="boot-A",
            test_mode=True,
            process_source=SnapshotProcessSource(),
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
        return self.engine.audit_registry(SnapshotProcessSource())


class InstallationTests(EngineTestCase):
    def test_installation_is_explicitly_inactive(self) -> None:
        status = self.engine.status()
        self.assertEqual(status["config"]["schema"], CONFIG_SCHEMA)
        self.assertIs(status["config"]["live_promotion"], False)
        self.assertIsNone(status["config"]["t3_char_pair_verdict"])
        self.assertEqual(tuple(status["config"]["powermetrics_probe"]), POWERMETRICS_PROBE)
        self.assertEqual(status["state"]["state"], "idle")
        self.assertIsNone(status["state"]["lease"])

    def test_setup_authority_marker_is_binding_d115(self) -> None:
        contract = (REPO_ROOT / "docs/contracts/quiet_guard.md").read_text()
        source = (REPO_ROOT / "joulewise/quiet_guard.py").read_text()
        self.assertEqual(SETUP_AUTHORITY_DECISION, "D-115")
        self.assertIn("D-115 (ADJUDICATED)", source)
        self.assertIn("D-115 (ADJUDICATED)", contract)
        self.assertNotIn("OPEN DECISION MARKER", contract)
        self.assertNotIn("D-114 (PROPOSED)", source + contract)

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

    def test_inactive_initialization_is_idempotent_without_rewrite(self) -> None:
        before = self.engine.paths.state.read_bytes()
        with mock.patch.object(guard_module, "_atomic_write_json") as write:
            state = self.engine.initialize_inactive()
        self.assertEqual(state["state"], "idle")
        write.assert_not_called()
        self.assertEqual(self.engine.paths.state.read_bytes(), before)

    def test_interrupted_inactive_initialization_completes_on_retry(self) -> None:
        root = self.root / "interrupted"
        engine = GuardEngine(root, host_id="host-A", boot_id="boot-A", test_mode=True)
        real_write = guard_module._atomic_write_json
        calls = 0

        def fail_state_once(path, value):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("injected state write failure")
            return real_write(path, value)

        with mock.patch.object(guard_module, "_atomic_write_json", side_effect=fail_state_once):
            with self.assertRaisesRegex(OSError, "injected state write failure"):
                engine.initialize_inactive()
        self.assertTrue(engine.paths.config.exists())
        self.assertFalse(engine.paths.state.exists())

        recovered = engine.initialize_inactive()
        self.assertEqual(recovered, initial_state("host-A", "boot-A"))
        self.assertEqual(engine.status()["state"], recovered)

    def test_init_retry_must_complete_its_own_directory_durability_pass(self) -> None:
        root = self.root / "directory-fsync-retry"
        engine = GuardEngine(root, host_id="host-A", boot_id="boot-A", test_mode=True)
        real_fsync_directory = guard_module._fsync_directory
        first_calls: list[Path] = []

        def fail_after_state_replace(directory):
            first_calls.append(Path(directory))
            if len(first_calls) == 2:
                raise OSError("state directory fsync failed")
            return real_fsync_directory(directory)

        with mock.patch.object(
            guard_module, "_fsync_directory", side_effect=fail_after_state_replace
        ):
            with self.assertRaisesRegex(OSError, "state directory fsync failed"):
                engine.initialize_inactive()
        self.assertTrue(engine.paths.config.exists())
        self.assertTrue(engine.paths.state.exists())

        with mock.patch.object(
            guard_module,
            "_fsync_directory",
            side_effect=OSError("retry directory fsync still failed"),
        ) as still_failing, mock.patch.object(guard_module, "_atomic_write_json") as write:
            with self.assertRaisesRegex(OSError, "retry directory fsync still failed"):
                engine.initialize_inactive()
        still_failing.assert_called_once_with(engine.paths.root)
        write.assert_not_called()

        retry_calls: list[Path] = []

        def successful_retry(directory):
            retry_calls.append(Path(directory))
            return real_fsync_directory(directory)

        with mock.patch.object(
            guard_module, "_fsync_directory", side_effect=successful_retry
        ), mock.patch.object(guard_module, "_atomic_write_json") as write:
            recovered = engine.initialize_inactive()
        self.assertEqual(recovered, initial_state("host-A", "boot-A"))
        self.assertEqual(retry_calls, [engine.paths.root, engine.paths.root.parent])
        write.assert_not_called()

    def test_install_preflight_refuses_noninitial_recovery_history(self) -> None:
        self.pending(entries=(self.owner,))
        self.engine.audit_registry(SnapshotProcessSource())
        with self.assertRaises(GuardError) as caught:
            self.engine.validate_inactive_installation()
        self.assertEqual(caught.exception.cause, "schema_mismatch")

    def test_validation_refusal_does_not_create_missing_control_lock(self) -> None:
        root = self.root / "validation-only-refusal"
        root.mkdir()
        (root / "config.json").write_text("not-json")
        before = {path.name: path.read_bytes() for path in root.iterdir()}
        engine = GuardEngine(root, host_id="host-A", boot_id="boot-A", test_mode=True)
        with self.assertRaises(GuardError) as caught:
            engine.validate_inactive_installation()
        self.assertEqual(caught.exception.cause, "lock_unavailable")
        self.assertEqual({path.name: path.read_bytes() for path in root.iterdir()}, before)
        self.assertFalse(engine.paths.lock.exists())

    def test_validation_of_absent_installation_creates_no_state_path(self) -> None:
        root = self.root / "absent-validation"
        engine = GuardEngine(root, host_id="host-A", boot_id="boot-A", test_mode=True)
        self.assertEqual(
            engine.validate_inactive_installation(),
            initial_state("host-A", "boot-A"),
        )
        self.assertFalse(root.exists())

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
        self.assertEqual(pending["custody_roots"]["entries"], [self.owner.to_mapping()])
        self.assertEqual(held["custody_roots"]["entries"], [self.owner.to_mapping()])
        self.assertEqual(idle["custody_roots"]["entries"], [])

    def test_no_ttl_release_exists(self) -> None:
        pending = self.pending()
        serialized = canonical_json_bytes(pending).decode()
        self.assertNotIn("ttl", serialized.lower())
        self.assertNotIn("expires", serialized.lower())
        self.assertEqual(self.engine.read_state()["state"], "handoff_pending")
        self.assertEqual(self.engine.read_state()["lease"], pending["lease"])

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

    def test_kernel_table_and_state_schema_root_rules_are_explicit(self) -> None:
        state = initial_state("host-A", "boot-A")
        self.assertEqual(STATE_SCHEMA, "joulewise.quiet_guard.state/v2")
        self.assertEqual(EVENT_SCHEMA, "joulewise.quiet_guard.event/v2")
        self.assertEqual(
            state["custody_roots"]["schema"], CUSTODY_ROOTS_SCHEMA
        )
        self.assertEqual(set(STATE_FIELD_ROOT_RULES), set(STATE_FIELDS))
        self.assertEqual(
            {
                field
                for field, rule in STATE_FIELD_ROOT_RULES.items()
                if rule.startswith("identity:")
            },
            {"custody_roots", "registry", "lease", "events"},
        )
        state["future_identity"] = self.owner.to_mapping()
        with self.assertRaises(GuardError) as caught:
            validate_state(state, "host-A", "boot-A")
        self.assertEqual(caught.exception.cause, "schema_mismatch")

    def test_custody_roots_cannot_shrink_while_lease_is_retained(self) -> None:
        registered = identity(202)
        self.pending(entries=(registered,))
        self.engine.transition(
            "quiet_held",
            "watcher",
            registry_entries=(),
            independent_census_zero=True,
        )

        def shrink(raw):
            retained = [self.owner.to_mapping()]
            raw["custody_roots"]["entries"] = retained
            raw["events"][-1]["custody_roots"] = retained

        self.rewrite_state(shrink)
        with self.assertRaises(GuardError) as caught:
            self.engine.read_state()
        self.assertEqual(caught.exception.cause, "custody_roots_invalid")

    def test_lease_owner_and_registry_entries_must_be_exact_roots(self) -> None:
        registered = identity(202)
        pending = self.pending(entries=(registered,))
        self.assertEqual(
            pending["custody_roots"]["entries"],
            [self.owner.to_mapping(), registered.to_mapping()],
        )
        self.rewrite_state(
            lambda raw: raw["custody_roots"]["entries"].remove(
                registered.to_mapping()
            )
        )
        with self.assertRaises(GuardError) as caught:
            self.engine.read_state()
        self.assertEqual(caught.exception.cause, "custody_roots_invalid")

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

    def test_idle_with_live_lease_and_registry_refuses_canonically(self) -> None:
        state = initial_state("host-A", "boot-A")
        state["registry"]["entries"] = [self.owner.to_mapping()]
        state["lease"] = {
            "schema": LEASE_SCHEMA,
            "host_id": "host-A",
            "boot_id": "boot-A",
            "epoch": 0,
            "lease_id": str(uuid.uuid4()),
            "owner": self.owner.to_mapping(),
            "created_epoch": 0,
        }
        with self.assertRaises(GuardError) as caught:
            validate_state(state, "host-A", "boot-A")
        self.assertEqual(caught.exception.cause, "lease_invalid")
        self.assertEqual(
            caught.exception.to_mapping()["signature"],
            "quiet_guard/lease_invalid/v1",
        )

    def test_idle_with_registry_but_null_lease_refuses(self) -> None:
        state = initial_state("host-A", "boot-A")
        state["registry"]["entries"] = [self.owner.to_mapping()]
        with self.assertRaises(GuardError) as caught:
            validate_state(state, "host-A", "boot-A")
        self.assertEqual(caught.exception.cause, "registry_invalid")

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
        source = SnapshotProcessSource((self.owner,))
        state = self.engine.audit_registry(source)
        self.assertEqual(state["state"], "handoff_pending")
        self.assertEqual(source.inventory_calls, 1)

    def test_absent_registered_identity_enters_recovery_required(self) -> None:
        state = self.recovery_with_stale_owner()
        self.assertEqual(state["state"], "recovery_required")
        self.assertEqual(state["events"][-1]["cause"], "stale_registry")
        self.assertIsNotNone(state["lease"])

    def test_pid_reuse_enters_recovery_and_records_observation(self) -> None:
        self.pending(entries=(self.owner,))
        reused = identity(self.owner.pid, start="boot+99")
        state = self.engine.audit_registry(SnapshotProcessSource((reused,)))
        self.assertEqual(state["events"][-1]["cause"], "pid_reuse_detected")
        evidence = state["events"][-1]["evidence"]["revalidation"][0]
        self.assertEqual(evidence["result"], "pid_reused")
        self.assertEqual(evidence["observed"], reused.to_mapping())

    def test_unobservable_registry_enters_recovery_and_retains_lease(self) -> None:
        self.pending(entries=(self.owner,))
        state = self.engine.audit_registry(
            SnapshotProcessSource(
                (self.owner,), unobservable_pids=(self.owner.pid,)
            )
        )
        self.assertEqual(state["state"], "recovery_required")
        self.assertEqual(
            state["events"][-1]["cause"], "process_observation_unavailable"
        )
        self.assertIsNotNone(state["lease"])

    def test_recovery_requires_exact_acknowledgment(self) -> None:
        self.recovery_with_stale_owner()
        with self.assertRaises(GuardError) as caught:
            self.engine.recover(
                acknowledgment="yes",
                acknowledged_by="Ed",
            )
        self.assertEqual(caught.exception.cause, "recovery_acknowledgment_missing")

    def test_recovery_refuses_while_exact_registered_process_remains(self) -> None:
        self.recovery_with_stale_owner()
        source = SnapshotProcessSource((self.owner,))
        self.engine._process_source = source
        with self.assertRaises(GuardError) as caught:
            self.engine.recover(
                acknowledgment=RECOVERY_ACKNOWLEDGMENT,
                acknowledged_by="Ed",
            )
        self.assertEqual(caught.exception.cause, "processes_remain")
        self.assertEqual(source.inventory_calls, 1)

    def test_recovery_refuses_unobservable_identity_without_releasing_custody(self) -> None:
        recovery = self.recovery_with_stale_owner()
        lease_id = recovery["lease"]["lease_id"]
        before = self.engine.paths.state.read_bytes()
        self.engine._process_source = SnapshotProcessSource(
            (self.owner,), unobservable_pids=(self.owner.pid,)
        )
        with self.assertRaises(GuardError) as caught:
            self.engine.recover(
                acknowledgment=RECOVERY_ACKNOWLEDGMENT,
                acknowledged_by="Ed",
            )
        self.assertEqual(caught.exception.cause, "process_observation_unavailable")
        retained = self.engine.read_state()
        self.assertEqual(retained["state"], "recovery_required")
        self.assertEqual(retained["lease"]["lease_id"], lease_id)
        self.assertEqual(self.engine.paths.state.read_bytes(), before)

    def test_custody_root_lease_owner_survives_empty_registry_and_blocks_recovery(self) -> None:
        pending = self.pending(entries=())
        held = self.engine.transition(
            "quiet_held",
            "watcher",
            registry_entries=(),
            independent_census_zero=True,
        )
        recovery = self.engine.transition("recovery_required", "watcher")
        for state in (pending, held, recovery):
            self.assertEqual(
                state["custody_roots"]["entries"], [self.owner.to_mapping()]
            )
        self.assertEqual(recovery["registry"]["entries"], [])
        lease_id = recovery["lease"]["lease_id"]
        before = self.engine.paths.state.read_bytes()

        self.engine._process_source = SnapshotProcessSource(
            (self.owner,), unobservable_pids=(self.owner.pid,)
        )
        with self.assertRaises(GuardError) as unobservable:
            self.engine.recover(
                acknowledgment=RECOVERY_ACKNOWLEDGMENT,
                acknowledged_by="Ed",
            )
        self.assertEqual(unobservable.exception.cause, "process_observation_unavailable")
        self.assertEqual(self.engine.paths.state.read_bytes(), before)

        reused = identity(self.owner.pid, executable="/app/reused")
        child = identity(
            202,
            ancestry=(
                AncestorIdentity(
                    reused.pid,
                    reused.start_time,
                    reused.executable,
                    reused.argv_digest,
                ),
            ),
        )
        self.engine._process_source = SnapshotProcessSource((reused, child))
        with self.assertRaises(GuardError) as descendant:
            self.engine.recover(
                acknowledgment=RECOVERY_ACKNOWLEDGMENT,
                acknowledged_by="Ed",
            )
        self.assertEqual(descendant.exception.cause, "independent_census_nonzero")
        self.assertEqual(self.engine.paths.state.read_bytes(), before)
        self.assertEqual(self.engine.read_state()["lease"]["lease_id"], lease_id)

    def test_acknowledged_zero_proof_clears_and_records_exact_abandonment(self) -> None:
        recovery = self.recovery_with_stale_owner()
        lease_id = recovery["lease"]["lease_id"]
        state = self.engine.recover(
            acknowledgment=RECOVERY_ACKNOWLEDGMENT,
            acknowledged_by="Ed",
        )
        self.assertEqual(state["state"], "idle")
        self.assertEqual(state["registry"]["entries"], [])
        self.assertEqual(state["custody_roots"]["entries"], [])
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
        self.engine.audit_registry(SnapshotProcessSource((reused,)))
        source = SnapshotProcessSource((reused,))
        self.engine._process_source = source
        state = self.engine.recover(
            acknowledgment=RECOVERY_ACKNOWLEDGMENT,
            acknowledged_by="lead",
        )
        abandoned = state["events"][-1]["evidence"]["abandoned_exact_identities"][0]
        self.assertEqual(abandoned["result"], "pid_reused")
        self.assertEqual(abandoned["observed"], reused.to_mapping())
        self.assertEqual(source.inventory_calls, 1)

    def test_recover_owns_entire_proof_under_one_control_lock(self) -> None:
        self.recovery_with_stale_owner()
        active = False
        acquisitions = 0
        real_locked = self.engine.locked
        real_read = self.engine._read_persisted_bindings
        real_write = guard_module._atomic_write_json
        reused = identity(self.owner.pid, start="boot+99")

        class LockAwareSource(SnapshotProcessSource):
            def inventory(source_self):
                self.assertTrue(active)
                return super().inventory()

            def observe(source_self, pid, snapshot):
                self.assertTrue(active)
                return super().observe(pid, snapshot)

        source = LockAwareSource((reused,))
        self.engine._process_source = source

        @contextmanager
        def tracked_lock(*args, **kwargs):
            nonlocal active, acquisitions
            acquisitions += 1
            with real_locked(*args, **kwargs):
                active = True
                try:
                    yield
                finally:
                    active = False

        def tracked_read():
            self.assertTrue(active)
            return real_read()

        def tracked_write(path, value):
            self.assertTrue(active)
            return real_write(path, value)

        with mock.patch.object(self.engine, "locked", side_effect=tracked_lock), mock.patch.object(
            self.engine, "_read_persisted_bindings", side_effect=tracked_read
        ), mock.patch.object(
            guard_module, "_atomic_write_json", side_effect=tracked_write
        ):
            state = self.engine.recover(
                acknowledgment=RECOVERY_ACKNOWLEDGMENT,
                acknowledged_by="lead",
            )
        self.assertEqual(state["state"], "idle")
        self.assertEqual(acquisitions, 1)
        self.assertEqual(source.inventory_calls, 1)

    def test_pid_reuse_snapshot_boundary_refuses_then_fresh_invocation_clears(self) -> None:
        recovery = self.recovery_with_stale_owner()
        lease_id = recovery["lease"]["lease_id"]
        before = self.engine.paths.state.read_bytes()
        reused = identity(self.owner.pid, start="boot+99")
        first = SnapshotProcessSource(
            (reused,),
            inventory_rows=(
                KernelProcessRecord(self.owner.pid, 0, self.owner.start_time),
            ),
        )
        self.engine._process_source = first
        with self.assertRaises(GuardError) as caught:
            self.engine.recover(
                acknowledgment=RECOVERY_ACKNOWLEDGMENT,
                acknowledged_by="lead",
            )
        self.assertEqual(caught.exception.cause, "process_observation_unavailable")
        self.assertEqual(first.inventory_calls, 1)
        self.assertEqual(self.engine.paths.state.read_bytes(), before)
        self.assertEqual(self.engine.read_state()["lease"]["lease_id"], lease_id)

        fresh = SnapshotProcessSource((reused,))
        self.engine._process_source = fresh
        state = self.engine.recover(
            acknowledgment=RECOVERY_ACKNOWLEDGMENT,
            acknowledged_by="lead",
        )
        abandoned = state["events"][-1]["evidence"]["abandoned_exact_identities"]
        self.assertEqual(abandoned[0]["expected"], self.owner.to_mapping())
        self.assertEqual(abandoned[0]["result"], "pid_reused")
        self.assertEqual(abandoned[0]["observed"], reused.to_mapping())
        self.assertEqual(fresh.inventory_calls, 1)

    def test_clean_exit_requires_fresh_recover_invocation(self) -> None:
        self.recovery_with_stale_owner()
        before = self.engine.paths.state.read_bytes()
        listed_then_gone = SnapshotProcessSource(
            (),
            inventory_rows=(
                KernelProcessRecord(self.owner.pid, 0, self.owner.start_time),
            ),
        )
        self.engine._process_source = listed_then_gone
        with self.assertRaises(GuardError) as caught:
            self.engine.recover(
                acknowledgment=RECOVERY_ACKNOWLEDGMENT,
                acknowledged_by="Ed",
            )
        self.assertEqual(caught.exception.cause, "process_observation_unavailable")
        self.assertEqual(self.engine.paths.state.read_bytes(), before)
        self.assertEqual(listed_then_gone.inventory_calls, 1)

        fresh_absence = SnapshotProcessSource()
        self.engine._process_source = fresh_absence
        self.assertEqual(
            self.engine.recover(
                acknowledgment=RECOVERY_ACKNOWLEDGMENT,
                acknowledged_by="Ed",
            )["state"],
            "idle",
        )
        self.assertEqual(fresh_absence.inventory_calls, 1)

    def test_unrelated_churn_is_never_exactly_observed(self) -> None:
        self.recovery_with_stale_owner()
        unrelated = identity(303)
        source = SnapshotProcessSource(
            (unrelated,), unobservable_pids=(unrelated.pid,)
        )
        self.engine._process_source = source
        state = self.engine.recover(
            acknowledgment=RECOVERY_ACKNOWLEDGMENT,
            acknowledged_by="Ed",
        )
        self.assertEqual(state["state"], "idle")
        self.assertEqual(source.inventory_calls, 1)
        self.assertEqual(source.observed_pids, [])


class BindingRecoveryTests(EngineTestCase):
    def test_cross_reboot_status_reports_and_acknowledged_recovery_rebinds(self) -> None:
        rebooted = GuardEngine(
            self.root,
            host_id="host-A",
            boot_id="boot-B",
            test_mode=False,
            process_source=SnapshotProcessSource(),
        )
        status = rebooted.status()
        self.assertEqual(status["binding"]["status"], "recovery_required")
        self.assertEqual(status["binding"]["causes"], ["boot_mismatch"])
        state = rebooted.recover(
            acknowledgment=RECOVERY_ACKNOWLEDGMENT,
            acknowledged_by="Ed",
        )
        self.assertEqual((state["host_id"], state["boot_id"], state["state"]), ("host-A", "boot-B", "idle"))
        self.assertIsNone(state["lease"])
        self.assertEqual(rebooted.status()["binding"]["status"], "current")
        self.assertIs(rebooted.read_config()["live_promotion"], False)

    def test_hostname_drift_acknowledged_recovery_rebinds(self) -> None:
        renamed = GuardEngine(
            self.root,
            host_id="host-B",
            boot_id="boot-A",
            test_mode=False,
            process_source=SnapshotProcessSource(),
        )
        self.assertEqual(renamed.status()["binding"]["causes"], ["host_mismatch"])
        state = renamed.recover(
            acknowledgment=RECOVERY_ACKNOWLEDGMENT,
            acknowledged_by="lead",
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
        with mock.patch.object(self.client.subprocess, "run") as run, mock.patch(
            "builtins.print"
        ) as emit:
            exit_code = self.client.main(("arm",))
        self.assertEqual(exit_code, self.client.EXIT_REFUSED)
        payload = json.loads(emit.call_args.args[0])
        self.assertEqual(payload["cause"], "t3_char_pair_verdict_missing")
        run.assert_not_called()

    def test_cli_arm_refusal_cause_matches_commit_one_contract(self) -> None:
        contract = (REPO_ROOT / "docs/contracts/quiet_guard.md").read_text()
        match = re.search(
            r"`quiet_guard arm` refuses.*?canonical cause\s+`([^`]+)`",
            contract,
            re.DOTALL,
        )
        self.assertIsNotNone(match)
        assert match is not None
        with mock.patch.object(self.client.subprocess, "run") as run, mock.patch(
            "builtins.print"
        ) as emit:
            exit_code = self.client.main(("arm",))
        self.assertEqual(exit_code, self.client.EXIT_REFUSED)
        self.assertEqual(json.loads(emit.call_args.args[0])["cause"], match.group(1))
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

    def test_privileged_recovery_supplies_acknowledgment_only(self) -> None:
        engine = mock.Mock()
        engine.recover.return_value = {"state": "idle"}
        with mock.patch.object(self.helper.os, "geteuid", return_value=0), mock.patch.object(
            self.helper, "GuardEngine", return_value=engine
        ), mock.patch.dict(self.helper.os.environ, {"SUDO_USER": "Ed"}, clear=False), mock.patch.object(
            self.helper, "_emit"
        ):
            exit_code = self.helper.main(
                ("recover", "--ack", RECOVERY_ACKNOWLEDGMENT)
            )
        self.assertEqual(exit_code, 0)
        engine.status.assert_not_called()
        engine.recover.assert_called_once_with(
            acknowledgment=RECOVERY_ACKNOWLEDGMENT,
            acknowledged_by="Ed",
        )

    def test_protected_pid_and_caller_census_machinery_no_longer_exists(self) -> None:
        engine_source = (REPO_ROOT / "joulewise/quiet_guard.py").read_text()
        process_source = (
            REPO_ROOT / "joulewise/quiet_guard_process.py"
        ).read_text()
        helper_source = (
            REPO_ROOT / "scripts/quiet_guard_privileged.py"
        ).read_text()
        combined = engine_source + process_source + helper_source
        self.assertNotIn("protected_identities", combined)
        self.assertNotIn("protected_pids", combined)
        self.assertNotIn("_recovery_inputs", combined)
        self.assertNotIn("independent_census_rows", combined)

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

    def test_executable_helper_uses_isolated_no_site_interpreter(self) -> None:
        helper_path = REPO_ROOT / "scripts/quiet_guard_privileged.py"
        helper_source = helper_path.read_text()
        self.assertEqual(
            helper_source.splitlines()[:4],
            [
                "#!/bin/sh",
                '""":"',
                'exec /usr/bin/python3 -I -S "$0" "$@"',
                ':"""',
            ],
        )
        self.assertNotIn("/usr/bin/env", helper_source)
        self.assertNotIn("REPOSITORY_ROOT", helper_source)
        self.assertIn('sys.path[:] = [_INSTALLED_LIBRARY, *_stdlib]', helper_source)
        self.assertTrue(os.access(helper_path, os.X_OK))
        completed = subprocess.run(
            (
                "/usr/bin/python3",
                "-I",
                "-S",
                "-c",
                "import sys; print(sys.flags.ignore_environment, "
                "sys.flags.no_user_site, sys.flags.isolated, sys.flags.no_site)",
            ),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout.strip(), "1 1 1 1")

    def test_installed_helper_bootstrap_rejects_path_poisoning(self) -> None:
        source = (REPO_ROOT / "scripts/quiet_guard_privileged.py").read_text()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            helper_path = root / "libexec" / "joulewise-quiet-guard"
            library = root / "install" / "lib"
            package = library / "joulewise"
            helper_path.parent.mkdir(parents=True)
            package.mkdir(parents=True)
            (package / "__init__.py").write_text("")
            shutil.copyfile(REPO_ROOT / "joulewise/quiet_guard.py", package / "quiet_guard.py")
            shutil.copyfile(
                REPO_ROOT / "joulewise/quiet_guard_process.py",
                package / "quiet_guard_process.py",
            )
            installed_source = source.replace(
                '_INSTALLED_HELPER = "/usr/local/libexec/joulewise-quiet-guard"',
                f'_INSTALLED_HELPER = "{helper_path}"',
            ).replace(
                '_INSTALLED_LIBRARY = "/Library/Application Support/JouleWise/quiet-guard-install/lib"',
                f'_INSTALLED_LIBRARY = "{library}"',
            )
            helper_path.write_text(installed_source)
            helper_path.chmod(0o755)

            attacker = root / "attacker"
            attacker.mkdir()
            marker = attacker / "attacker-ran"
            attacker_package = attacker / "joulewise"
            attacker_package.mkdir()
            (attacker_package / "__init__.py").write_text("")
            (attacker_package / "quiet_guard.py").write_text(
                f"from pathlib import Path\nPath({str(marker)!r}).touch()\n"
            )
            environment = dict(os.environ, PATH=str(attacker), PYTHONPATH=str(attacker))
            completed = subprocess.run(
                (str(helper_path), "status"),
                cwd=attacker,
                env=environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(completed.returncode, self.helper.EXIT_REFUSED, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["cause"], "privileged_command_refused")
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
        revoke = setup.index("/usr/bin/sudo -k")
        authorize = setup.index("/usr/bin/sudo -v")
        stage = setup.index("STAGE_ROOT=$(/usr/bin/sudo")
        self.assertLess(revoke, authorize)
        self.assertLess(authorize, stage)
        self.assertEqual(setup.count("/usr/bin/sudo"), 17)
        logical_setup = setup.replace("\\\n", " ")
        sudo_targets = [
            re.search(r"/usr/bin/sudo\s+([^\s)]+)", line).group(1)
            for line in logical_setup.splitlines()
            if "/usr/bin/sudo" in line and not line.lstrip().startswith("#")
        ]
        self.assertEqual(
            sudo_targets,
            [
                "-k",
                "-v",
                "/usr/bin/mktemp",
                "/bin/rm",
                "/usr/bin/install",
                "/usr/bin/install",
                "/usr/bin/install",
                "/usr/bin/install",
                "/usr/bin/python3",
                "/usr/bin/python3",
                "/usr/sbin/visudo",
                "/usr/bin/python3",
                "/usr/bin/install",
                "/usr/bin/install",
                "/usr/bin/python3",
                "/usr/bin/python3",
                '"$HELPER"',
            ],
        )
        self.assertIn("install-inactive", setup)
        self.assertIn("live_promotion=false", setup)
        self.assertNotIn("systemsetup", setup)
        self.assertNotIn("sudo -v", client + helper)
        self.assertIn('"/usr/bin/sudo", "-n"', client)
        syntax = subprocess.run(
            ("/bin/sh", "-n", str(REPO_ROOT / "scripts/setup_quiet_guard.sh")),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(syntax.returncode, 0, syntax.stderr)

    def test_setup_validates_and_installs_identical_root_staged_bytes(self) -> None:
        setup = (REPO_ROOT / "scripts/setup_quiet_guard.sh").read_text()
        for mutable_path in (
            "$REPO_ROOT/joulewise/quiet_guard.py",
            "$REPO_ROOT/joulewise/quiet_guard_process.py",
            "$REPO_ROOT/scripts/quiet_guard_privileged.py",
        ):
            self.assertEqual(setup.count(mutable_path), 1, mutable_path)
        validation_and_install = setup.split("# Authenticate the exact root-staged bytes", 1)[1]
        self.assertNotIn("$REPO_ROOT/", validation_and_install)
        self.assertIn('visudo -cf "$STAGE_ROOT/joulewise-quiet-guard.sudoers"', setup)
        self.assertIn(
            'f"{stage_root}/joulewise-quiet-guard.sudoers", sudoers_path', setup
        )
        self.assertIn("with engine.inactive_installation_lock", setup)
        self.assertNotIn("recover --ack *", setup)
        self.assertIn("unsafe root-helper parent", setup)

    def test_setup_interleaved_state_change_refuses_before_every_artifact_write(self) -> None:
        setup = (REPO_ROOT / "scripts/setup_quiet_guard.sh").read_text()
        preflight = setup.index("validate_inactive_installation(privileged_setup=True)")
        locked_revalidation = setup.index("with engine.inactive_installation_lock")
        self.assertLess(preflight, locked_revalidation)
        for install_fragment in (
            'f"{stage_root}/joulewise/quiet_guard.py", f"{lib_root}/quiet_guard.py"',
            'f"{stage_root}/joulewise/quiet_guard_process.py", f"{lib_root}/quiet_guard_process.py"',
            'f"{stage_root}/quiet_guard_privileged.py", helper',
            'f"{stage_root}/joulewise-quiet-guard.sudoers", sudoers_path',
        ):
            self.assertIn(install_fragment, setup)
        self.assertLess(
            locked_revalidation,
            setup.index("subprocess.run(command, check=True)"),
        )

        with tempfile.TemporaryDirectory(prefix=guard_module.TEST_STATE_ROOT_PREFIX) as temporary:
            temporary_root = Path(temporary)
            state_root = temporary_root / "state"
            install_root = temporary_root / "install"
            lib_root = install_root / "lib" / "joulewise"
            helper = temporary_root / "libexec" / "joulewise-quiet-guard"
            sudoers = temporary_root / "sudoers" / "joulewise-quiet-guard"
            credential_root = temporary_root / "credentials"
            GuardEngine(
                state_root, host_id="host-A", boot_id="boot-A", test_mode=True
            ).initialize_inactive()
            installed = {
                lib_root / "quiet_guard.py": b"before:quiet_guard.py",
                lib_root / "quiet_guard_process.py": b"before:quiet_guard_process.py",
                helper: b"before:helper",
                sudoers: b"before:sudoers",
            }
            for path, payload in installed.items():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(payload)
            before = {path: path.read_bytes() for path in installed}

            fake_sudo = temporary_root / "sudo"
            fake_sudo.write_text(
                f"#!{sys.executable}\n"
                "import subprocess, sys\n"
                "arguments = sys.argv[1:]\n"
                "if arguments in (['-k'], ['-v']):\n"
                "    raise SystemExit(0)\n"
                "if arguments and arguments[0] == '/usr/sbin/visudo':\n"
                "    raise SystemExit(0)\n"
                "if arguments and arguments[0] == '/usr/bin/install':\n"
                "    filtered = [arguments[0]]\n"
                "    offset = 1\n"
                "    while offset < len(arguments):\n"
                "        if arguments[offset] in ('-o', '-g'):\n"
                "            offset += 2\n"
                "        else:\n"
                "            filtered.append(arguments[offset])\n"
                "            offset += 1\n"
                "    arguments = filtered\n"
                "raise SystemExit(subprocess.run(arguments, check=False).returncode)\n"
            )
            fake_sudo.chmod(0o755)

            rendered = setup
            replacements = {
                'REPO_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)':
                    f'REPO_ROOT="{REPO_ROOT}"',
                'STATE_ROOT="/Library/Application Support/JouleWise/quiet-guard"':
                    f'STATE_ROOT="{state_root}"',
                'INSTALL_ROOT="/Library/Application Support/JouleWise/quiet-guard-install"':
                    f'INSTALL_ROOT="{install_root}"',
                'CREDENTIAL_ROOT="/Library/Application Support/JouleWise/quiet-guard-credentials"':
                    f'CREDENTIAL_ROOT="{credential_root}"',
                'HELPER="/usr/local/libexec/joulewise-quiet-guard"': f'HELPER="{helper}"',
                'SUDOERS_PATH="/etc/sudoers.d/joulewise-quiet-guard"':
                    f'SUDOERS_PATH="{sudoers}"',
                "/usr/local/libexec": str(helper.parent),
                "/usr/bin/sudo": str(fake_sudo),
            }
            for original, replacement in replacements.items():
                rendered = rendered.replace(original, replacement)
            rendered = rendered.replace("row.st_uid != 0", "False")
            production_preflight = (
                "from joulewise.quiet_guard import GuardEngine, PRODUCTION_STATE_ROOT\n"
                "GuardEngine(PRODUCTION_STATE_ROOT).validate_inactive_installation("
                "privileged_setup=True)\n"
                "' \"$STAGE_ROOT\""
            )
            fixture_preflight = (
                "from pathlib import Path\n"
                "from joulewise.quiet_guard import GuardEngine\n"
                'GuardEngine(Path(sys.argv[2]), host_id="host-A", boot_id="boot-A", '
                "test_mode=True).validate_inactive_installation()\n"
                "' \"$STAGE_ROOT\" \"$STATE_ROOT\""
            )
            self.assertIn(production_preflight, rendered)
            rendered = rendered.replace(production_preflight, fixture_preflight)
            rendered = rendered.replace(
                "import subprocess, sys\nsys.path.insert(0, sys.argv[1])",
                "import subprocess, sys\nfrom pathlib import Path\nsys.path.insert(0, sys.argv[1])",
            )
            rendered = rendered.replace(
                "engine = GuardEngine(PRODUCTION_STATE_ROOT)",
                'engine = GuardEngine(Path(sys.argv[5]), host_id="host-A", '
                'boot_id="boot-A", test_mode=True)',
            )
            rendered = rendered.replace(
                "with engine.inactive_installation_lock(privileged_setup=True):",
                "with engine.inactive_installation_lock():",
            )
            rendered = rendered.replace(
                "' \"$STAGE_ROOT\" \"$LIB_ROOT\" \"$HELPER\" \"$SUDOERS_PATH\"",
                "' \"$STAGE_ROOT\" \"$LIB_ROOT\" \"$HELPER\" \"$SUDOERS_PATH\" \"$STATE_ROOT\"",
            )
            mutator = temporary_root / "mutate_state.py"
            mutator.write_text(
                "import sys\n"
                "from pathlib import Path\n"
                f"sys.path.insert(0, {str(REPO_ROOT)!r})\n"
                "from joulewise.quiet_guard import GuardEngine\n"
                'GuardEngine(Path(sys.argv[1]), host_id="host-A", boot_id="boot-A", '
                'test_mode=True).transition("recovery_required", "engine")\n'
            )
            rendered = rendered.replace(
                fixture_preflight,
                fixture_preflight
                + f'\n"{sys.executable}" "{mutator}" "$STATE_ROOT"',
            )
            sandboxed_setup = temporary_root / "setup.sh"
            sandboxed_setup.write_text(rendered)
            completed = subprocess.run(
                ("/bin/sh", str(sandboxed_setup)),
                cwd=REPO_ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertNotEqual(completed.returncode, 0, completed.stdout)
            self.assertIn(b"existing guard state is not initial", completed.stderr)
            self.assertEqual({path: path.read_bytes() for path in installed}, before)

    def test_setup_digest_pins_match_every_reviewed_root_executable_artifact(self) -> None:
        setup = (REPO_ROOT / "scripts/setup_quiet_guard.sh").read_text()
        expected = {
            "QUIET_GUARD_SHA256": REPO_ROOT / "joulewise/quiet_guard.py",
            "QUIET_GUARD_PROCESS_SHA256": REPO_ROOT / "joulewise/quiet_guard_process.py",
            "QUIET_GUARD_PRIVILEGED_SHA256": REPO_ROOT / "scripts/quiet_guard_privileged.py",
        }
        for variable, path in expected.items():
            match = re.search(rf'^{variable}="([0-9a-f]{{64}})"$', setup, re.MULTILINE)
            self.assertIsNotNone(match, variable)
            assert match is not None
            pinned = match.group(1)
            payload = path.read_bytes()
            self.assertEqual(pinned, hashlib.sha256(payload).hexdigest(), path)
            self.assertNotEqual(pinned, hashlib.sha256(payload + b"\n# tampered").hexdigest())
        self.assertIn("hmac.compare_digest(observed, expected)", setup)
        self.assertIn("reviewed-artifact digest mismatch", setup)
        validator = setup.split(
            "/usr/bin/sudo /usr/bin/python3 -I -S -B -c '\n", 1
        )[1].split("\n' \\\n", 1)[0]
        with tempfile.TemporaryDirectory() as temporary:
            staged = Path(temporary) / "quiet_guard.py"
            payload = (REPO_ROOT / "joulewise/quiet_guard.py").read_bytes()
            staged.write_bytes(payload)
            digest = hashlib.sha256(payload).hexdigest()
            valid = subprocess.run(
                (sys.executable, "-I", "-S", "-B", "-c", validator, str(staged), digest),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(valid.returncode, 0, valid.stderr)
            staged.write_bytes(payload + b"\n# syntactically valid tampering\n")
            tampered = subprocess.run(
                (sys.executable, "-I", "-S", "-B", "-c", validator, str(staged), digest),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertNotEqual(tampered.returncode, 0)
            self.assertIn(b"reviewed-artifact digest mismatch", tampered.stderr)

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

    def test_commit_one_omits_drain_constants_and_launch_refusal_surface(self) -> None:
        engine_source = (REPO_ROOT / "joulewise/quiet_guard.py").read_text()
        removed_constants = {
            "SESSION_EXIT_TIMEOUT_S": 120,
            "APP_QUIT_TIMEOUT_S": 30,
            "TERM_WAIT_TIMEOUT_S": 10,
            "KILL_WAIT_TIMEOUT_S": 5,
        }
        for name, former_value in removed_constants.items():
            self.assertFalse(hasattr(guard_module, name), name)
            self.assertNotIn(f"{name} = {former_value}", engine_source)
        self.assertFalse(hasattr(guard_module, "agent_launch_refusal"))
        self.assertNotIn("agent_launch_refusal", engine_source)
        self.assertNotIn("agent_launch_blocked", guard_module.FAILURE_CAUSES)
        self.assertNotIn("agent_launch_blocked", engine_source)


if __name__ == "__main__":
    unittest.main()
