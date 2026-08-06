"""Fail-closed durable lease engine for QUIET-GUARD-01 Commit 1.

This module deliberately cannot promote a production quiet lease.  It lands
the state, registry, lease, event, lock, recovery, and inactive-installation
contracts against parameterized roots so tests can exercise the complete
engine without touching the production state root.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import fcntl
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import socket
import subprocess
import tempfile
from typing import Any, Callable, Iterator, Mapping, Sequence
import uuid

from joulewise.quiet_guard_process import (
    ProcessIdentity,
    ProcessIdentityError,
    ProcessSource,
    Revalidation,
    revalidate_identity,
    validate_identity_mapping,
)


PRODUCTION_STATE_ROOT = Path("/Library/Application Support/JouleWise/quiet-guard")
TEST_STATE_ROOT_PREFIX = "joulewise-quiet-guard-test-"

CONFIG_SCHEMA = "joulewise.quiet_guard.config/v1"
STATE_SCHEMA = "joulewise.quiet_guard.state/v1"
REGISTRY_SCHEMA = "joulewise.quiet_guard.registry/v1"
LEASE_SCHEMA = "joulewise.quiet_guard.lease/v1"
EVENT_SCHEMA = "joulewise.quiet_guard.event/v1"
FAILURE_SCHEMA = "joulewise.quiet_guard.failure/v1"

POWERMETRICS_PROBE = (
    "/usr/bin/sudo",
    "-n",
    "/usr/bin/powermetrics",
    "-n",
    "1",
    "-i",
    "100",
)
STATES = (
    "idle",
    "handoff_pending",
    "quiet_held",
    "recovery_required",
)
ACTORS = ("initiating_session", "watcher", "engine", "recovery")


@dataclass(frozen=True)
class TransitionRule:
    source: str
    target: str
    actor: str
    lease_action: str


# This is the one state-transition authority.  In particular, an initiating
# session can create handoff_pending only; it can never enter quiet_held.
TRANSITION_RULES = (
    TransitionRule("idle", "handoff_pending", "initiating_session", "create"),
    TransitionRule("handoff_pending", "quiet_held", "watcher", "retain"),
    TransitionRule("handoff_pending", "recovery_required", "watcher", "retain"),
    TransitionRule("quiet_held", "recovery_required", "watcher", "retain"),
    TransitionRule("idle", "recovery_required", "engine", "retain"),
    TransitionRule("handoff_pending", "recovery_required", "engine", "retain"),
    TransitionRule("quiet_held", "recovery_required", "engine", "retain"),
    TransitionRule("quiet_held", "idle", "watcher", "clear"),
    TransitionRule("recovery_required", "idle", "recovery", "clear"),
)
TRANSITION_TABLE = {
    (rule.source, rule.target, rule.actor): rule for rule in TRANSITION_RULES
}

RECOVERY_ACKNOWLEDGMENT = (
    "I acknowledge quiet-guard recovery and exact-identity abandonment"
)

# D-115 (ADJUDICATED) binds the fixed installation capability and its fresh
# authorization, authenticated-content, and interpreter-isolation conditions.
SETUP_AUTHORITY_DECISION = "D-115"

FAILURE_CAUSES = (
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
    "process_observation_unavailable",
    "privileged_command_refused",
)
FAILURE_SIGNATURES = {
    cause: f"quiet_guard/{cause}/v1" for cause in FAILURE_CAUSES
}


class GuardError(RuntimeError):
    """A fail-closed guard refusal carrying a canonical cause."""

    def __init__(self, cause: str, detail: str = "") -> None:
        if cause not in FAILURE_SIGNATURES:
            raise ValueError(f"unknown quiet-guard cause: {cause}")
        super().__init__(detail or cause)
        self.cause = cause
        self.detail = detail
        self.signature = FAILURE_SIGNATURES[cause]

    def to_mapping(self) -> dict[str, Any]:
        return failure_mapping(self.cause, self.detail)


def failure_mapping(cause: str, detail: str = "") -> dict[str, Any]:
    """Return the stable wire representation for one refusal cause."""

    if cause not in FAILURE_SIGNATURES:
        raise ValueError(f"unknown quiet-guard cause: {cause}")
    return {
        "schema": FAILURE_SCHEMA,
        "cause": cause,
        "signature": FAILURE_SIGNATURES[cause],
        "detail": detail,
    }


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def current_host_id() -> str:
    """Return a stable local host binding without consulting the network."""

    node = platform.node() or socket.gethostname()
    if not node:
        raise GuardError("host_mismatch", "local host identity is unavailable")
    return node


def current_boot_id(
    runner: Callable[..., subprocess.CompletedProcess[str]] | None = None,
) -> str:
    """Return a boot-session binding on Linux or macOS, fail closed otherwise."""

    linux_boot = Path("/proc/sys/kernel/random/boot_id")
    try:
        value = linux_boot.read_text(encoding="ascii").strip()
    except OSError:
        value = ""
    if value:
        return value
    run = runner or subprocess.run
    result = run(
        ["/usr/sbin/sysctl", "-n", "kern.boottime"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode == 0 and result.stdout.strip():
        return "sha256:" + hashlib.sha256(result.stdout.strip().encode()).hexdigest()
    raise GuardError("boot_mismatch", "local boot identity is unavailable")


def validate_test_state_root(requested: Path) -> Path:
    """Confine fixture initialization to a named process-tmpdir sandbox."""

    root = Path(requested).expanduser().resolve()
    if root == PRODUCTION_STATE_ROOT.resolve():
        raise GuardError("live_promotion_disabled", "production root refused")
    temp_root = Path(tempfile.gettempdir()).resolve()
    try:
        relative = root.relative_to(temp_root)
    except ValueError as exc:
        raise GuardError(
            "privileged_command_refused", "test state root must be under the process tmpdir"
        ) from exc
    if not relative.parts or not relative.parts[0].startswith(TEST_STATE_ROOT_PREFIX):
        raise GuardError(
            "privileged_command_refused",
            f"test state root must use the {TEST_STATE_ROOT_PREFIX!r} sandbox prefix",
        )
    return root


@dataclass(frozen=True)
class GuardPaths:
    root: Path

    @property
    def config(self) -> Path:
        return self.root / "config.json"

    @property
    def state(self) -> Path:
        return self.root / "state.json"

    @property
    def lock(self) -> Path:
        return self.root / "control.lock"


def _require_exact_fields(value: Any, fields: set[str], cause: str, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or set(value) != fields:
        raise GuardError(cause, f"{label} fields are invalid")
    return value


def _plain_string(value: Any, cause: str, field: str) -> str:
    if type(value) is not str or not value:
        raise GuardError(cause, f"{field} must be a non-empty string")
    return value


def _nonnegative_epoch(value: Any) -> int:
    if type(value) is not int or value < 0:
        raise GuardError("epoch_regression", "epoch must be an integer >= 0")
    return value


def inactive_config(host_id: str) -> dict[str, Any]:
    """Return the only configuration this commit can install."""

    return {
        "schema": CONFIG_SCHEMA,
        "host_id": _plain_string(host_id, "host_mismatch", "host_id"),
        "live_promotion": False,
        "t3_char_pair_verdict": None,
        "powermetrics_probe": list(POWERMETRICS_PROBE),
    }


def _validate_config(value: Any, host_id: str) -> dict[str, Any]:
    raw = _require_exact_fields(
        value,
        {
            "schema",
            "host_id",
            "live_promotion",
            "t3_char_pair_verdict",
            "powermetrics_probe",
        },
        "schema_mismatch",
        "config",
    )
    if raw["schema"] != CONFIG_SCHEMA:
        raise GuardError("schema_mismatch", "config schema mismatch")
    if raw["host_id"] != host_id:
        raise GuardError("host_mismatch", "config belongs to another host")
    if type(raw["live_promotion"]) is not bool:
        raise GuardError("schema_mismatch", "live_promotion must be boolean")
    verdict = raw["t3_char_pair_verdict"]
    if verdict is not None:
        verdict_raw = _require_exact_fields(
            verdict,
            {"schema", "task_id", "verdict", "sha256"},
            "schema_mismatch",
            "T3 verdict reference",
        )
        if (
            verdict_raw["schema"] != "joulewise.t3_char_pair_verdict_ref/v1"
            or verdict_raw["task_id"] != "T3-CHAR-PAIR-01"
            or verdict_raw["verdict"] != "passed"
            or type(verdict_raw["sha256"]) is not str
            or re.fullmatch(r"sha256:[0-9a-f]{64}", verdict_raw["sha256"])
            is None
        ):
            raise GuardError("schema_mismatch", "T3 verdict reference is invalid")
    if raw["powermetrics_probe"] != list(POWERMETRICS_PROBE):
        raise GuardError("schema_mismatch", "powermetrics probe shape drifted")
    return dict(raw)


def _validate_registry(value: Any, host_id: str, boot_id: str, epoch: int) -> dict[str, Any]:
    raw = _require_exact_fields(
        value,
        {"schema", "host_id", "boot_id", "epoch", "entries"},
        "registry_invalid",
        "registry",
    )
    if raw["schema"] != REGISTRY_SCHEMA:
        raise GuardError("schema_mismatch", "registry schema mismatch")
    if raw["host_id"] != host_id:
        raise GuardError("host_mismatch", "registry belongs to another host")
    if raw["boot_id"] != boot_id:
        raise GuardError("boot_mismatch", "registry belongs to another boot")
    if _nonnegative_epoch(raw["epoch"]) != epoch:
        raise GuardError("epoch_regression", "registry epoch differs from state")
    if not isinstance(raw["entries"], list):
        raise GuardError("registry_invalid", "registry entries must be a list")
    identities: list[ProcessIdentity] = []
    try:
        identities = [validate_identity_mapping(item) for item in raw["entries"]]
    except ProcessIdentityError as exc:
        raise GuardError("registry_invalid", str(exc)) from exc
    if len({identity.pid for identity in identities}) != len(identities):
        raise GuardError("registry_invalid", "registry contains duplicate PIDs")
    return {
        "schema": REGISTRY_SCHEMA,
        "host_id": host_id,
        "boot_id": boot_id,
        "epoch": epoch,
        "entries": [identity.to_mapping() for identity in identities],
    }


def _validate_lease(value: Any, host_id: str, boot_id: str, epoch: int, state: str) -> dict[str, Any] | None:
    if value is None:
        if state in {"handoff_pending", "quiet_held"}:
            raise GuardError("lease_invalid", f"{state} requires a lease")
        return None
    if state == "idle":
        raise GuardError("lease_invalid", "idle requires a null lease")
    raw = _require_exact_fields(
        value,
        {"schema", "host_id", "boot_id", "epoch", "lease_id", "owner", "created_epoch"},
        "lease_invalid",
        "lease",
    )
    if raw["schema"] != LEASE_SCHEMA:
        raise GuardError("schema_mismatch", "lease schema mismatch")
    if raw["host_id"] != host_id:
        raise GuardError("host_mismatch", "lease belongs to another host")
    if raw["boot_id"] != boot_id:
        raise GuardError("boot_mismatch", "lease belongs to another boot")
    if _nonnegative_epoch(raw["epoch"]) != epoch:
        raise GuardError("epoch_regression", "lease epoch differs from state")
    created_epoch = _nonnegative_epoch(raw["created_epoch"])
    if created_epoch > epoch:
        raise GuardError("epoch_regression", "lease was created in a future epoch")
    lease_id = _plain_string(raw["lease_id"], "lease_invalid", "lease_id")
    try:
        uuid.UUID(lease_id)
        owner = validate_identity_mapping(raw["owner"])
    except (ValueError, ProcessIdentityError) as exc:
        raise GuardError("lease_invalid", "lease identity is invalid") from exc
    return {
        "schema": LEASE_SCHEMA,
        "host_id": host_id,
        "boot_id": boot_id,
        "epoch": epoch,
        "lease_id": lease_id,
        "owner": owner.to_mapping(),
        "created_epoch": created_epoch,
    }


def _validate_event(value: Any, host_id: str, boot_id: str, epoch: int) -> dict[str, Any]:
    raw = _require_exact_fields(
        value,
        {
            "schema",
            "host_id",
            "boot_id",
            "epoch",
            "from_state",
            "to_state",
            "actor",
            "cause",
            "lease_id",
            "evidence",
        },
        "schema_mismatch",
        "event",
    )
    if raw["schema"] != EVENT_SCHEMA:
        raise GuardError("schema_mismatch", "event schema mismatch")
    if raw["host_id"] != host_id:
        raise GuardError("host_mismatch", "event belongs to another host")
    if raw["boot_id"] != boot_id:
        raise GuardError("boot_mismatch", "event belongs to another boot")
    if _nonnegative_epoch(raw["epoch"]) != epoch:
        raise GuardError("epoch_regression", "event epoch is not monotonic")
    if raw["from_state"] not in STATES or raw["to_state"] not in STATES:
        raise GuardError("schema_mismatch", "event contains an unknown state")
    if raw["actor"] not in ACTORS:
        raise GuardError("schema_mismatch", "event contains an unknown actor")
    if (raw["from_state"], raw["to_state"], raw["actor"]) not in TRANSITION_TABLE:
        raise GuardError("invalid_transition", "event transition is not legal")
    _plain_string(raw["cause"], "schema_mismatch", "event.cause")
    if raw["lease_id"] is not None:
        _plain_string(raw["lease_id"], "lease_invalid", "event.lease_id")
    if not isinstance(raw["evidence"], Mapping):
        raise GuardError("schema_mismatch", "event evidence must be an object")
    return dict(raw)


def validate_state(value: Any, host_id: str, boot_id: str) -> dict[str, Any]:
    """Validate the complete crash-atomic state document."""

    raw = _require_exact_fields(
        value,
        {"schema", "host_id", "boot_id", "epoch", "state", "registry", "lease", "events"},
        "schema_mismatch",
        "state",
    )
    if raw["schema"] != STATE_SCHEMA:
        raise GuardError("schema_mismatch", "state schema mismatch")
    if raw["host_id"] != host_id:
        raise GuardError("host_mismatch", "state belongs to another host")
    if raw["boot_id"] != boot_id:
        raise GuardError("boot_mismatch", "state belongs to another boot")
    epoch = _nonnegative_epoch(raw["epoch"])
    state = raw["state"]
    if state not in STATES:
        raise GuardError("schema_mismatch", "unknown guard state")
    registry = _validate_registry(raw["registry"], host_id, boot_id, epoch)
    lease = _validate_lease(raw["lease"], host_id, boot_id, epoch, state)
    if state == "idle" and registry["entries"]:
        raise GuardError("registry_invalid", "idle requires an empty registry")
    if not isinstance(raw["events"], list) or len(raw["events"]) != epoch:
        raise GuardError("epoch_regression", "event count must equal state epoch")
    events = [
        _validate_event(event, host_id, boot_id, expected_epoch)
        for expected_epoch, event in enumerate(raw["events"], start=1)
    ]
    if events and events[0]["from_state"] != "idle":
        raise GuardError("epoch_regression", "first event must begin at idle")
    for previous, current in zip(events, events[1:]):
        if current["from_state"] != previous["to_state"]:
            raise GuardError("epoch_regression", "event history is discontinuous")
    if events and events[-1]["to_state"] != state:
        raise GuardError("epoch_regression", "last event does not name current state")
    return {
        "schema": STATE_SCHEMA,
        "host_id": host_id,
        "boot_id": boot_id,
        "epoch": epoch,
        "state": state,
        "registry": registry,
        "lease": lease,
        "events": events,
    }


def initial_state(host_id: str, boot_id: str) -> dict[str, Any]:
    return {
        "schema": STATE_SCHEMA,
        "host_id": host_id,
        "boot_id": boot_id,
        "epoch": 0,
        "state": "idle",
        "registry": {
            "schema": REGISTRY_SCHEMA,
            "host_id": host_id,
            "boot_id": boot_id,
            "epoch": 0,
            "entries": [],
        },
        "lease": None,
        "events": [],
    }


def _read_json(path: Path) -> Any:
    try:
        payload = path.read_bytes()
        return json.loads(payload)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GuardError("malformed_json", f"cannot read canonical JSON at {path.name}") from exc


def _fsync_directory(directory: Path) -> None:
    descriptor = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _atomic_write_json(path: Path, value: Any) -> None:
    """Durably replace one JSON document in its destination directory."""

    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent)
    )
    temporary = Path(temporary_name)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(canonical_json_bytes(value))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        _fsync_directory(path.parent)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def transition_rule(source: str, target: str, actor: str) -> TransitionRule | None:
    """Return the table-owned rule, or ``None`` for every illegal edge."""

    return TRANSITION_TABLE.get((source, target, actor))


class GuardEngine:
    """Root-parameterized durable state engine.

    ``test_mode`` is the only Commit-1 capability that permits lease-bearing
    transitions.  It is rejected for the production root.  Production helper
    calls can install inactive files, inspect them, and execute the narrow
    recovery path, but cannot arm or create a lease.
    """

    def __init__(
        self,
        state_root: Path,
        *,
        host_id: str | None = None,
        boot_id: str | None = None,
        test_mode: bool = False,
    ) -> None:
        root = Path(state_root).expanduser().resolve()
        production_root = PRODUCTION_STATE_ROOT.resolve()
        if test_mode and root == production_root:
            raise GuardError("live_promotion_disabled", "test mode cannot target production")
        if test_mode:
            root = validate_test_state_root(root)
        self.paths = GuardPaths(root)
        self.host_id = host_id or current_host_id()
        self.boot_id = boot_id or current_boot_id()
        self.test_mode = test_mode

    def initialize_inactive(self, *, privileged_setup: bool = False) -> dict[str, Any]:
        self._require_inactive_installation_authority(privileged_setup)
        with self.locked():
            config, state, config_exists, state_exists = self._inactive_installation_state()
            if not config_exists:
                _atomic_write_json(self.paths.config, config)
            if not state_exists:
                _atomic_write_json(self.paths.state, state)
            # This invocation reports success only after both directory entries
            # and the state-root entry itself have a completed durability pass.
            # In particular, an idempotent retry cannot launder a prior
            # post-replace directory-fsync failure into reported success.
            _fsync_directory(self.paths.root)
            _fsync_directory(self.paths.root.parent)
            return state

    def validate_inactive_installation(self, *, privileged_setup: bool = False) -> dict[str, Any]:
        """Refuse an incompatible installed state without replacing artifacts."""

        self._require_inactive_installation_authority(privileged_setup)
        if not self.paths.root.exists():
            return initial_state(self.host_id, self.boot_id)
        with self.locked(create=False):
            _, state, _, _ = self._inactive_installation_state()
            return state

    @contextmanager
    def inactive_installation_lock(
        self, *, privileged_setup: bool = False
    ) -> Iterator[dict[str, Any]]:
        """Hold one lock across inactive-state validation and artifact writes."""

        self._require_inactive_installation_authority(privileged_setup)
        with self.locked():
            _, state, _, _ = self._inactive_installation_state()
            yield state

    def _require_inactive_installation_authority(self, privileged_setup: bool) -> None:
        is_production = self.paths.root == PRODUCTION_STATE_ROOT.resolve()
        if is_production and (not privileged_setup or self.test_mode):
            raise GuardError("privileged_command_refused", "production initialization is setup-only")
        if not is_production and (not self.test_mode or privileged_setup):
            raise GuardError(
                "privileged_command_refused", "non-production initialization is test-sandbox-only"
            )

    def _inactive_installation_state(self) -> tuple[dict[str, Any], dict[str, Any], bool, bool]:
        """Validate the fresh/retryable state accepted by inactive setup."""

        config = inactive_config(self.host_id)
        state = initial_state(self.host_id, self.boot_id)
        config_exists = self.paths.config.exists()
        state_exists = self.paths.state.exists()
        if config_exists:
            installed_config = self.read_config()
            if installed_config != config:
                raise GuardError("schema_mismatch", "existing inactive config differs")
        if state_exists:
            installed_state = self.read_state()
            if installed_state != state:
                raise GuardError("schema_mismatch", "existing guard state is not initial")
        return config, state, config_exists, state_exists

    @contextmanager
    def locked(
        self, *, blocking: bool = False, create: bool = True
    ) -> Iterator[None]:
        if create:
            self.paths.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        elif not self.paths.root.is_dir() or not self.paths.lock.exists():
            raise GuardError(
                "lock_unavailable", "existing installation has no control lock"
            )
        flags = os.O_RDWR | (os.O_CREAT if create else 0)
        descriptor = os.open(self.paths.lock, flags, 0o600)
        operation = fcntl.LOCK_EX | (0 if blocking else fcntl.LOCK_NB)
        try:
            try:
                fcntl.flock(descriptor, operation)
            except BlockingIOError as exc:
                raise GuardError("lock_unavailable", "control lock is held") from exc
            try:
                yield
            finally:
                fcntl.flock(descriptor, fcntl.LOCK_UN)
        finally:
            os.close(descriptor)

    def read_config(self) -> dict[str, Any]:
        return _validate_config(_read_json(self.paths.config), self.host_id)

    def read_state(self) -> dict[str, Any]:
        return validate_state(_read_json(self.paths.state), self.host_id, self.boot_id)

    def status(self) -> dict[str, Any]:
        try:
            return {
                "config": self.read_config(),
                "state": self.read_state(),
                "binding": {"status": "current", "recoverable": False},
            }
        except GuardError as exc:
            if exc.cause not in {"host_mismatch", "boot_mismatch"}:
                raise
        config, state = self._read_persisted_bindings()
        causes = []
        if config["host_id"] != self.host_id or state["host_id"] != self.host_id:
            causes.append("host_mismatch")
        if state["boot_id"] != self.boot_id:
            causes.append("boot_mismatch")
        if not causes:
            raise GuardError("schema_mismatch", "binding validation failed inconsistently")
        return {
            "config": config,
            "state": state,
            "binding": {
                "status": "recovery_required",
                "recoverable": True,
                "causes": causes,
                "persisted_host_id": state["host_id"],
                "persisted_boot_id": state["boot_id"],
                "current_host_id": self.host_id,
                "current_boot_id": self.boot_id,
            },
        }

    def _read_persisted_bindings(self) -> tuple[dict[str, Any], dict[str, Any]]:
        """Strictly validate persisted bytes against their own bindings.

        This is used only to report or perform an acknowledged binding
        recovery.  Normal reads remain bound to the current host and boot.
        Config and state are validated independently so an interrupted
        config-first rebind is itself recoverable on the next acknowledged
        attempt.
        """

        config_raw = _read_json(self.paths.config)
        state_raw = _read_json(self.paths.state)
        if not isinstance(config_raw, Mapping) or type(config_raw.get("host_id")) is not str:
            raise GuardError("schema_mismatch", "persisted config binding is invalid")
        if (
            not isinstance(state_raw, Mapping)
            or type(state_raw.get("host_id")) is not str
            or type(state_raw.get("boot_id")) is not str
        ):
            raise GuardError("schema_mismatch", "persisted state binding is invalid")
        config = _validate_config(config_raw, config_raw["host_id"])
        state = validate_state(state_raw, state_raw["host_id"], state_raw["boot_id"])
        if config["host_id"] != state["host_id"] and config["host_id"] != self.host_id:
            raise GuardError(
                "schema_mismatch", "config/state bindings are inconsistent"
            )
        return config, state

    def arm_refusal(self) -> dict[str, Any]:
        config = self.read_config()
        verdict = config["t3_char_pair_verdict"]
        if verdict is None:
            return failure_mapping(
                "t3_char_pair_verdict_missing",
                "a lead-installed passing T3-CHAR-PAIR-01 verdict is required",
            )
        return failure_mapping(
            "live_promotion_disabled",
            "Commit 1 has no production promotion capability",
        )

    def arm(self) -> None:
        refusal = self.arm_refusal()
        raise GuardError(refusal["cause"], refusal["detail"])

    def _event(
        self,
        state: Mapping[str, Any],
        target: str,
        actor: str,
        cause: str,
        evidence: Mapping[str, Any],
        lease_id: str | None,
    ) -> dict[str, Any]:
        return {
            "schema": EVENT_SCHEMA,
            "host_id": self.host_id,
            "boot_id": self.boot_id,
            "epoch": state["epoch"] + 1,
            "from_state": state["state"],
            "to_state": target,
            "actor": actor,
            "cause": cause,
            "lease_id": lease_id,
            "evidence": dict(evidence),
        }

    def _write_transition(
        self,
        state: Mapping[str, Any],
        *,
        target: str,
        actor: str,
        cause: str,
        evidence: Mapping[str, Any],
        registry_entries: Sequence[ProcessIdentity] | None = None,
        new_owner: ProcessIdentity | None = None,
        independent_census_zero: bool = False,
    ) -> dict[str, Any]:
        rule = transition_rule(state["state"], target, actor)
        if rule is None:
            raise GuardError(
                "invalid_transition",
                f"illegal transition {state['state']}->{target} by {actor}",
            )
        if actor == "recovery":
            raise GuardError(
                "invalid_transition", "recovery_required may clear only through recover()"
            )
        if target == "quiet_held" and not independent_census_zero:
            raise GuardError(
                "independent_census_nonzero", "watcher did not prove a zero-agent census"
            )
        epoch = state["epoch"] + 1
        entries = [
            identity.to_mapping()
            for identity in (
                registry_entries
                if registry_entries is not None
                else [validate_identity_mapping(item) for item in state["registry"]["entries"]]
            )
        ]
        if target == "quiet_held" and entries:
            raise GuardError(
                "processes_remain", "quiet_held requires a zero-entry registry"
            )
        lease = state["lease"]
        if rule.lease_action == "create":
            if new_owner is None:
                raise GuardError("lease_invalid", "handoff_pending requires an exact owner")
            lease = {
                "schema": LEASE_SCHEMA,
                "host_id": self.host_id,
                "boot_id": self.boot_id,
                "epoch": epoch,
                "lease_id": str(uuid.uuid4()),
                "owner": new_owner.to_mapping(),
                "created_epoch": epoch,
            }
        elif rule.lease_action == "retain":
            if lease is not None:
                lease = dict(lease)
                lease["epoch"] = epoch
        elif rule.lease_action == "clear":
            lease = None
            entries = []
        lease_id = lease["lease_id"] if lease is not None else (
            state["lease"]["lease_id"] if state["lease"] is not None else None
        )
        event = self._event(state, target, actor, cause, evidence, lease_id)
        updated = {
            "schema": STATE_SCHEMA,
            "host_id": self.host_id,
            "boot_id": self.boot_id,
            "epoch": epoch,
            "state": target,
            "registry": {
                "schema": REGISTRY_SCHEMA,
                "host_id": self.host_id,
                "boot_id": self.boot_id,
                "epoch": epoch,
                "entries": entries,
            },
            "lease": lease,
            "events": list(state["events"]) + [event],
        }
        validated = validate_state(updated, self.host_id, self.boot_id)
        _atomic_write_json(self.paths.state, validated)
        return validated

    def transition(
        self,
        target: str,
        actor: str,
        *,
        cause: str = "test_transition",
        evidence: Mapping[str, Any] | None = None,
        registry_entries: Sequence[ProcessIdentity] | None = None,
        owner: ProcessIdentity | None = None,
        independent_census_zero: bool = False,
    ) -> dict[str, Any]:
        if not self.test_mode:
            raise GuardError("live_promotion_disabled", "lease transitions are fixture-only in Commit 1")
        with self.locked():
            state = self.read_state()
            return self._write_transition(
                state,
                target=target,
                actor=actor,
                cause=cause,
                evidence=evidence or {},
                registry_entries=registry_entries,
                new_owner=owner,
                independent_census_zero=independent_census_zero,
            )

    def audit_registry(
        self,
        source: ProcessSource,
        independent_census_rows: Sequence[ProcessIdentity],
    ) -> dict[str, Any]:
        """Detect stale/reused registered identities and retain custody."""

        with self.locked():
            state = self.read_state()
            results: list[dict[str, Any]] = []
            cause = ""
            registered_identities: list[ProcessIdentity] = []
            for raw in state["registry"]["entries"]:
                expected = validate_identity_mapping(raw)
                registered_identities.append(expected)
                verdict, observed = revalidate_identity(expected, source)
                results.append(
                    {
                        "expected": expected.to_mapping(),
                        "result": verdict.value,
                        "observed": observed.to_mapping() if observed else None,
                    }
                )
                if verdict == Revalidation.UNOBSERVABLE:
                    cause = "process_observation_unavailable"
                elif (
                    verdict == Revalidation.PID_REUSED
                    and cause != "process_observation_unavailable"
                ):
                    cause = "pid_reuse_detected"
                elif verdict == Revalidation.ABSENT and not cause:
                    cause = "stale_registry"
            unknown_census = [
                row for row in independent_census_rows if row not in registered_identities
            ]
            if unknown_census and not cause:
                cause = "stale_registry"
            if not cause:
                return state
            if state["state"] == "recovery_required":
                return state
            return self._write_transition(
                state,
                target="recovery_required",
                actor="engine",
                cause=cause,
                evidence={
                    "revalidation": results,
                    "independent_census_count": len(independent_census_rows),
                    "unknown_census_count": len(unknown_census),
                },
            )

    def recover(
        self,
        *,
        acknowledgment: str,
        acknowledged_by: str,
        source: ProcessSource,
        independent_census_rows: Sequence[ProcessIdentity],
    ) -> dict[str, Any]:
        """Clear recovery only after acknowledgment and two zero proofs.

        No timeout or TTL participates.  Registered entries are abandoned only
        after their exact identities are absent; PID reuse is recorded rather
        than mistaken for a match.
        """

        if acknowledgment != RECOVERY_ACKNOWLEDGMENT or not acknowledged_by:
            raise GuardError(
                "recovery_acknowledgment_missing", "the exact recovery acknowledgment is required"
            )
        with self.locked():
            config, state = self._read_persisted_bindings()
            binding_changed = (
                config["host_id"] != self.host_id
                or state["host_id"] != self.host_id
                or state["boot_id"] != self.boot_id
            )
            if binding_changed:
                return self._recover_changed_binding(
                    config=config,
                    state=state,
                    acknowledgment=acknowledgment,
                    acknowledged_by=acknowledged_by,
                    source=source,
                    independent_census_rows=independent_census_rows,
                )
            if state["state"] != "recovery_required":
                raise GuardError("invalid_transition", "guard is not in recovery_required")
            abandoned: list[dict[str, Any]] = []
            for raw in state["registry"]["entries"]:
                expected = validate_identity_mapping(raw)
                verdict, observed = revalidate_identity(expected, source)
                if verdict == Revalidation.MATCH:
                    raise GuardError("processes_remain", f"registered PID {expected.pid} still matches")
                if verdict == Revalidation.UNOBSERVABLE:
                    raise GuardError(
                        "process_observation_unavailable",
                        f"registered PID {expected.pid} could not be observed",
                    )
                abandoned.append(
                    {
                        "expected": expected.to_mapping(),
                        "result": verdict.value,
                        "observed": observed.to_mapping() if observed else None,
                    }
                )
            if independent_census_rows:
                raise GuardError(
                    "independent_census_nonzero",
                    f"independent census contains {len(independent_census_rows)} process(es)",
                )
            epoch = state["epoch"] + 1
            lease_id = state["lease"]["lease_id"] if state["lease"] else None
            event = self._event(
                state,
                "idle",
                "recovery",
                "acknowledged_zero_process_recovery",
                {
                    "acknowledged_by": acknowledged_by,
                    "acknowledgment": acknowledgment,
                    "abandoned_exact_identities": abandoned,
                    "independent_census_count": 0,
                },
                lease_id,
            )
            updated = {
                "schema": STATE_SCHEMA,
                "host_id": self.host_id,
                "boot_id": self.boot_id,
                "epoch": epoch,
                "state": "idle",
                "registry": {
                    "schema": REGISTRY_SCHEMA,
                    "host_id": self.host_id,
                    "boot_id": self.boot_id,
                    "epoch": epoch,
                    "entries": [],
                },
                "lease": None,
                "events": list(state["events"]) + [event],
            }
            validated = validate_state(updated, self.host_id, self.boot_id)
            _atomic_write_json(self.paths.state, validated)
            return validated

    def _recover_changed_binding(
        self,
        *,
        config: Mapping[str, Any],
        state: Mapping[str, Any],
        acknowledgment: str,
        acknowledged_by: str,
        source: ProcessSource,
        independent_census_rows: Sequence[ProcessIdentity],
    ) -> dict[str, Any]:
        """Re-bind an acknowledged stale installation to this host/boot.

        The old event history remains represented by its canonical digest in
        recovery evidence rather than being relabelled as if it occurred on
        the new binding.  The replacement document is a fresh, continuous
        idle -> recovery_required -> idle recovery history and can never
        contain a lease.
        """

        if independent_census_rows:
            raise GuardError(
                "independent_census_nonzero",
                f"independent census contains {len(independent_census_rows)} process(es)",
            )
        boot_changed = state["boot_id"] != self.boot_id
        abandoned: list[dict[str, Any]] = []
        for raw in state["registry"]["entries"]:
            expected = validate_identity_mapping(raw)
            if boot_changed:
                verdict, observed = Revalidation.ABSENT, None
            else:
                verdict, observed = revalidate_identity(expected, source)
                if verdict == Revalidation.MATCH:
                    raise GuardError(
                        "processes_remain", f"registered PID {expected.pid} still matches"
                    )
                if verdict == Revalidation.UNOBSERVABLE:
                    raise GuardError(
                        "process_observation_unavailable",
                        f"registered PID {expected.pid} could not be observed",
                    )
            abandoned.append(
                {
                    "expected": expected.to_mapping(),
                    "result": verdict.value,
                    "observed": observed.to_mapping() if observed else None,
                }
            )
        old_binding = {
            "config_host_id": config["host_id"],
            "state_host_id": state["host_id"],
            "state_boot_id": state["boot_id"],
            "state_digest": canonical_sha256(state),
            "state_name": state["state"],
            "epoch": state["epoch"],
        }
        fresh = initial_state(self.host_id, self.boot_id)
        recovery_event = self._event(
            fresh,
            "recovery_required",
            "engine",
            "binding_change_detected",
            {"prior_binding": old_binding},
            None,
        )
        recovering = {
            **fresh,
            "epoch": 1,
            "state": "recovery_required",
            "registry": {**fresh["registry"], "epoch": 1},
            "events": [recovery_event],
        }
        recovered_event = self._event(
            recovering,
            "idle",
            "recovery",
            "acknowledged_binding_recovery",
            {
                "acknowledged_by": acknowledged_by,
                "acknowledgment": acknowledgment,
                "abandoned_exact_identities": abandoned,
                "independent_census_count": 0,
                "prior_binding": old_binding,
            },
            None,
        )
        recovered = {
            **recovering,
            "epoch": 2,
            "state": "idle",
            "registry": {**recovering["registry"], "epoch": 2},
            "events": [recovery_event, recovered_event],
        }
        validated = validate_state(recovered, self.host_id, self.boot_id)
        # Config first makes a crash between these writes recoverable: status
        # sees current config plus stale state and the same acknowledged path
        # can safely retry.  At no point is live promotion enabled.
        _atomic_write_json(self.paths.config, inactive_config(self.host_id))
        _atomic_write_json(self.paths.state, validated)
        return validated
