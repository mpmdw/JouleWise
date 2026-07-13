"""Defect-shaped checks for the tracked bridge-protocol/v1.1 helper."""

from __future__ import annotations

import argparse
from contextlib import redirect_stdout
import fcntl
import hashlib
import importlib.machinery
import importlib.util
import io
import json
import multiprocessing
import os
from pathlib import Path
import select
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
BRIDGE = REPO_ROOT / "scripts" / "bridge"
LOCK_ATTEMPT_SENTINEL = "bridge-test-about-to-attempt-session-lock"

LOCK_HANDSHAKE_CODE = f"""
import contextlib
import importlib.machinery
import importlib.util
import sys

loader = importlib.machinery.SourceFileLoader("bridge_lock_handshake", sys.argv[1])
spec = importlib.util.spec_from_loader(loader.name, loader)
module = importlib.util.module_from_spec(spec)
loader.exec_module(module)
real_session_lock = module.session_lock

@contextlib.contextmanager
def signaling_session_lock(root):
    print({LOCK_ATTEMPT_SENTINEL!r}, flush=True)
    with real_session_lock(root):
        yield

module.session_lock = signaling_session_lock
raise SystemExit(module.main(sys.argv[2:]))
"""


def _racing_acquire(repo: str, barrier: multiprocessing.Barrier, queue: multiprocessing.Queue) -> None:
    barrier.wait()
    result = subprocess.run(
        [
            str(BRIDGE),
            "lease-acquire",
            "--invocation-id",
            f"race-{os.getpid()}",
            "--owner-id",
            f"race-{os.getpid()}",
            "--owner-kind",
            "codex-cli",
            "--access",
            "write",
            "--paths",
            "tracked.txt",
        ],
        cwd=repo,
        text=True,
        capture_output=True,
    )
    queue.put((result.returncode, result.stdout))


def _racing_expand_or_acquire(
    repo: str,
    barrier: multiprocessing.Barrier,
    queue: multiprocessing.Queue,
    lease_id: str,
    operation: str,
) -> None:
    barrier.wait()
    if operation == "expand":
        arguments = [
            str(BRIDGE),
            "lease-expand",
            "--lease-id",
            lease_id,
            "--paths",
            "other.txt",
        ]
    else:
        arguments = [
            str(BRIDGE),
            "lease-acquire",
            "--invocation-id",
            f"expand-race-{os.getpid()}",
            "--owner-id",
            f"expand-race-{os.getpid()}",
            "--owner-kind",
            "codex-cli",
            "--access",
            "write",
            "--paths",
            "other.txt",
        ]
    result = subprocess.run(
        arguments,
        cwd=repo,
        text=True,
        capture_output=True,
    )
    queue.put((operation, result.returncode, result.stdout))


class BridgeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.repo = Path(self.temporary.name)
        self.git("init", "-q")
        self.git("config", "user.name", "Bridge Test")
        self.git("config", "user.email", "bridge@example.invalid")
        (self.repo / "tracked.txt").write_text("base\n", encoding="utf-8")
        (self.repo / "other.txt").write_text("other\n", encoding="utf-8")
        self.git("add", "tracked.txt", "other.txt")
        self.git("commit", "-qm", "base")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def git(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=self.repo,
            text=True,
            capture_output=True,
            check=True,
        )

    def bridge(self, *args: str, expected: int = 0) -> tuple[subprocess.CompletedProcess[str], dict]:
        result = subprocess.run(
            [str(BRIDGE), *args],
            cwd=self.repo,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, expected, result.stderr + result.stdout)
        return result, json.loads(result.stdout)

    def acquire(
        self,
        owner: str,
        path: str,
        *,
        access: str = "write",
        extra: tuple[str, ...] = (),
        expected: int = 0,
    ) -> dict:
        return self.bridge(
            "lease-acquire",
            "--invocation-id",
            owner,
            "--owner-id",
            owner,
            "--owner-kind",
            "codex-cli",
            "--access",
            access,
            "--paths",
            path,
            *extra,
            expected=expected,
        )[1]

    def baseline(self, invocation_id: str = "worker", *, expected: int = 0) -> dict:
        return self.bridge(
            "baseline", "--invocation-id", invocation_id, expected=expected
        )[1]

    def scope_check(
        self,
        baseline: dict,
        *scope: str,
        expected: int = 0,
        allow_commits: bool = False,
        lease_id: str | None = None,
    ) -> dict:
        arguments = [
            "scope-check",
            "--baseline",
            baseline["path"],
            "--expect-digest",
            baseline["manifest_sha256"],
            "--scope",
            *scope,
        ]
        if allow_commits:
            arguments.append("--allow-commits")
        if lease_id is not None:
            arguments.extend(("--lease-id", lease_id))
        return self.bridge(*arguments, expected=expected)[1]

    def session_open(
        self,
        invocation_id: str = "session-worker",
        *paths: str,
        expected: int = 0,
    ) -> dict:
        return self.bridge(
            "session-open",
            "--invocation-id",
            invocation_id,
            "--owner-id",
            invocation_id,
            "--owner-kind",
            "codex-cli",
            "--access",
            "write",
            "--paths",
            *(paths or ("tracked.txt",)),
            "--task",
            "bridge wrapper test",
            "--role",
            "test worker",
            "--genre",
            "implementation",
            "--task-shape",
            "bounded",
            expected=expected,
        )[1]

    def session_close(
        self,
        invocation_id: str = "session-worker",
        status: str = "DONE",
        *,
        expected: int = 0,
    ) -> dict:
        return self.bridge(
            "session-close",
            "--invocation-id",
            invocation_id,
            "--status",
            status,
            expected=expected,
        )[1]

    def jsonl_events(self, relative_path: str) -> list[dict]:
        path = self.repo / relative_path
        if not path.exists():
            return []
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]

    def load_bridge_module(self):
        loader = importlib.machinery.SourceFileLoader(
            f"bridge_script_test_{id(self)}", str(BRIDGE)
        )
        spec = importlib.util.spec_from_loader(loader.name, loader)
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)
        return module

    def handshaking_bridge_process(self, *arguments: str) -> subprocess.Popen[str]:
        process = subprocess.Popen(
            [sys.executable, "-c", LOCK_HANDSHAKE_CODE, str(BRIDGE), *arguments],
            cwd=self.repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        try:
            self.assertIsNotNone(process.stdout)
            ready, _, _ = select.select([process.stdout], [], [], 5)
            self.assertTrue(ready, "child did not reach the session-lock attempt")
            # If the command stops acquiring session.lock, the wrapper is never called:
            # the first line will be command JSON (or EOF), not this sentinel.
            self.assertEqual(process.stdout.readline().strip(), LOCK_ATTEMPT_SENTINEL)
        except BaseException:
            # A failed handshake must not leak a child blocked on the lock
            # (or its open pipes) into later tests.
            process.terminate()
            try:
                process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate(timeout=5)
            raise
        return process

    def test_mutating_commands_outside_repository_emit_command_errors(self) -> None:
        commands = (
            ("baseline", "--invocation-id", "outside"),
            ("thread-record", "--invocation-id", "outside", "--state", "pending"),
            ("lease-release", "--lease-id", "lease-outside"),
            (
                "lease-abandon",
                "--lease-id",
                "lease-outside",
                "--approved-by",
                "test",
                "--reason",
                "outside repository",
            ),
        )
        with tempfile.TemporaryDirectory() as outside_repository:
            for arguments in commands:
                with self.subTest(command=arguments[0]):
                    result = subprocess.run(
                        [str(BRIDGE), *arguments],
                        cwd=outside_repository,
                        text=True,
                        capture_output=True,
                    )
                    self.assertEqual(result.returncode, 5, result.stderr + result.stdout)
                    error = json.loads(result.stdout)
                    self.assertEqual(error["schema"], "bridge-command-error/v1")
                    self.assertEqual(error["command"], arguments[0])
                    self.assertEqual(error["stage"], "repository")
                    self.assertTrue(error["error"])

    def test_decorated_command_session_lock_open_failure_emits_command_error(self) -> None:
        bridge_dir = self.repo / ".codex-bridge"
        bridge_dir.mkdir()
        (bridge_dir / "session.lock").mkdir()
        result = subprocess.run(
            [str(BRIDGE), "baseline", "--invocation-id", "lock-failure"],
            cwd=self.repo,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 5, result.stderr + result.stdout)
        error = json.loads(result.stdout)
        self.assertEqual(
            {
                "schema": error["schema"],
                "command": error["command"],
                "stage": error["stage"],
            },
            {
                "schema": "bridge-command-error/v1",
                "command": "baseline",
                "stage": "session-lock",
            },
        )
        self.assertTrue(error["error"])

    def test_overlapping_write_lease_hard_blocks_with_json_conflicts(self) -> None:
        first = self.acquire("first", "tracked.txt")
        blocked = self.acquire("second", "tracked.txt", expected=3)
        self.assertEqual(blocked["status"], "CONFLICT")
        self.assertEqual(blocked["conflicts"][0]["lease_id"], first["lease_id"])

    def test_nonoverlapping_write_leases_can_coexist(self) -> None:
        self.acquire("first", "tracked.txt")
        second = self.acquire("second", "other.txt")
        self.assertEqual(second["event"], "acquire")

    def test_subtree_lease_conflicts_with_exact_descendant_only(self) -> None:
        self.acquire("tree-owner", "area:subtree")
        blocked = self.acquire("child-owner", "area/child.txt", expected=3)
        self.assertEqual(blocked["status"], "CONFLICT")
        outside = self.acquire("outside-owner", "area-sibling/child.txt")
        self.assertEqual(outside["event"], "acquire")

    def test_override_records_conflicts_and_indeterminate_policy(self) -> None:
        first = self.acquire("first", "tracked.txt")
        override = self.acquire(
            "lead",
            "tracked.txt",
            extra=("--override", "--approved-by", "ed", "--reason", "urgent repair"),
        )
        self.assertEqual(override["event"], "override")
        self.assertEqual(override["conflicting_lease_ids"], [first["lease_id"]])
        self.assertEqual(override["attribution_policy"], "INDETERMINATE")

    def test_release_and_abandon_remain_distinct_terminal_states(self) -> None:
        released = self.acquire("release-owner", "tracked.txt")
        abandoned = self.acquire("abandon-owner", "other.txt")
        self.bridge("lease-release", "--lease-id", released["lease_id"])
        event = self.bridge(
            "lease-abandon",
            "--lease-id",
            abandoned["lease_id"],
            "--approved-by",
            "ed",
            "--reason",
            "worker disappeared",
        )[1]
        self.assertEqual(event["event"], "abandon")
        listing = self.bridge("lease-list")[1]
        states = {row["lease_id"]: row["state"] for row in listing["leases"]}
        self.assertEqual(states[released["lease_id"]], "released")
        self.assertEqual(states[abandoned["lease_id"]], "abandoned")

    def test_snapshot_reads_overlap_only_at_same_repository_pin(self) -> None:
        self.acquire("reader-one", "tracked.txt", access="snapshot_read")
        same = self.acquire("reader-two", "tracked.txt", access="snapshot_read")
        self.assertEqual(same["event"], "acquire")
        (self.repo / "tracked.txt").write_text("moved\n", encoding="utf-8")
        changed = self.acquire("reader-three", "tracked.txt", access="snapshot_read", expected=3)
        self.assertIn("same repository pin", changed["conflicts"][0]["reason"])

    def test_write_and_snapshot_read_conflict_in_both_directions(self) -> None:
        reader = self.acquire("reader", "tracked.txt", access="snapshot_read")
        self.acquire("writer", "tracked.txt", expected=3)
        self.bridge("lease-release", "--lease-id", reader["lease_id"])
        writer = self.acquire("writer", "tracked.txt")
        blocked = self.acquire("reader-again", "tracked.txt", access="snapshot_read", expected=3)
        self.assertEqual(blocked["conflicts"][0]["lease_id"], writer["lease_id"])

    def test_expired_lease_warns_but_remains_active(self) -> None:
        lease = self.acquire("short", "tracked.txt", extra=("--expires-in", "1"))
        log = self.repo / ".codex-bridge" / "workspace-lease-events.jsonl"
        events = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
        events[0]["expires_at"] = "2000-01-01T00:00:00.000000Z"
        log.write_text("\n".join(json.dumps(event) for event in events) + "\n", encoding="utf-8")
        listing = self.bridge("lease-list", "--active")[1]
        self.assertEqual(listing["leases"][0]["lease_id"], lease["lease_id"])
        self.assertTrue(listing["warnings"])

    def test_acquire_conflict_check_and_append_are_atomic_between_processes(self) -> None:
        context = multiprocessing.get_context("fork")
        barrier = context.Barrier(2)
        queue = context.Queue()
        processes = [
            context.Process(target=_racing_acquire, args=(str(self.repo), barrier, queue))
            for _ in range(2)
        ]
        for process in processes:
            process.start()
        results = [queue.get(timeout=10) for _ in processes]
        for process in processes:
            process.join(timeout=10)
            self.assertEqual(process.exitcode, 0)
        self.assertEqual(sorted(code for code, _stdout in results), [0, 3])
        events = (self.repo / ".codex-bridge" / "workspace-lease-events.jsonl").read_text(
            encoding="utf-8"
        )
        self.assertEqual(len(events.splitlines()), 1)

    def test_lease_expand_self_expansion_succeeds_atomically(self) -> None:
        lease = self.acquire("worker", "tracked.txt")
        expanded = self.bridge(
            "lease-expand",
            "--lease-id",
            lease["lease_id"],
            "--paths",
            "other.txt",
        )[1]
        self.assertEqual(expanded["event"], "expand")
        self.assertEqual(
            expanded["paths"],
            [
                {"match": "exact", "path": "other.txt"},
                {"match": "exact", "path": "tracked.txt"},
            ],
        )
        listing = self.bridge("lease-list", "--active")[1]
        self.assertEqual(listing["leases"][0]["paths"], expanded["paths"])
        events = (self.repo / ".codex-bridge" / "workspace-lease-events.jsonl").read_text(
            encoding="utf-8"
        )
        self.assertEqual(len(events.splitlines()), 2)

    def test_lease_expand_overlapping_foreign_lease_hard_blocks(self) -> None:
        lease = self.acquire("worker", "tracked.txt")
        foreign = self.acquire("foreign", "other.txt")
        blocked = self.bridge(
            "lease-expand",
            "--lease-id",
            lease["lease_id"],
            "--paths",
            "other.txt",
            expected=3,
        )[1]
        self.assertEqual(blocked["status"], "CONFLICT")
        self.assertEqual(blocked["conflicts"][0]["lease_id"], foreign["lease_id"])
        events = (self.repo / ".codex-bridge" / "workspace-lease-events.jsonl").read_text(
            encoding="utf-8"
        )
        self.assertEqual(len(events.splitlines()), 2)

    def test_lease_expand_and_acquire_overlap_race_has_exactly_one_winner(self) -> None:
        lease = self.acquire("worker", "tracked.txt")
        context = multiprocessing.get_context("fork")
        barrier = context.Barrier(2)
        queue = context.Queue()
        processes = [
            context.Process(
                target=_racing_expand_or_acquire,
                args=(str(self.repo), barrier, queue, lease["lease_id"], operation),
            )
            for operation in ("expand", "acquire")
        ]
        for process in processes:
            process.start()
        results = [queue.get(timeout=10) for _ in processes]
        for process in processes:
            process.join(timeout=10)
            self.assertEqual(process.exitcode, 0)
        self.assertEqual(sorted(code for _operation, code, _stdout in results), [0, 3])
        events = (self.repo / ".codex-bridge" / "workspace-lease-events.jsonl").read_text(
            encoding="utf-8"
        )
        self.assertEqual(len(events.splitlines()), 2)

    def test_standalone_lease_expand_blocks_while_session_lock_is_held(self) -> None:
        lease = self.acquire("worker", "tracked.txt")
        bridge_dir = self.repo / ".codex-bridge"
        lock_path = bridge_dir / "session.lock"
        holder_code = (
            "import fcntl, sys\n"
            "handle = open(sys.argv[1], 'a+b')\n"
            "fcntl.flock(handle.fileno(), fcntl.LOCK_EX)\n"
            "print('locked', flush=True)\n"
            "sys.stdin.read(1)\n"
        )
        holder = subprocess.Popen(
            [sys.executable, "-c", holder_code, str(lock_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        expand = None
        try:
            self.assertIsNotNone(holder.stdout)
            self.assertEqual(holder.stdout.readline().strip(), "locked")
            expand = self.handshaking_bridge_process(
                "lease-expand",
                "--lease-id",
                lease["lease_id"],
                "--paths",
                "other.txt",
            )
            with self.assertRaises(subprocess.TimeoutExpired):
                expand.wait(timeout=0.2)
            self.assertEqual(
                [event["event"] for event in self.jsonl_events(
                    ".codex-bridge/workspace-lease-events.jsonl"
                )],
                ["acquire"],
            )
        finally:
            if holder.stdin is not None and holder.poll() is None:
                holder.stdin.write("x")
                holder.stdin.flush()
                holder.stdin.close()
            holder.wait(timeout=5)
            holder_stderr = holder.stderr.read() if holder.stderr is not None else ""
            if holder.stdout is not None:
                holder.stdout.close()
            if holder.stderr is not None:
                holder.stderr.close()
        self.assertEqual(holder.returncode, 0, holder_stderr)
        self.assertIsNotNone(expand)
        stdout, stderr = expand.communicate(timeout=5)
        self.assertEqual(expand.returncode, 0, stderr + stdout)
        self.assertEqual(json.loads(stdout)["event"], "expand")

    def test_malformed_lease_log_fails_scope_and_acquire_closed(self) -> None:
        baseline = self.baseline()
        log = self.repo / ".codex-bridge" / "workspace-lease-events.jsonl"
        log.write_text(
            json.dumps(
                {
                    "schema": "bridge-lease-event/v1",
                    "event": "acquire",
                    "lease_id": "lease-malformed",
                    "invocation_id": "worker",
                    "owner_id": "worker",
                    "access": "write",
                    "paths": [],
                    "timestamp": "2026-07-13T00:00:00.000000Z",
                }
            )
            + "\n",
            encoding="utf-8",
        )
        report = self.scope_check(baseline, "tracked.txt", expected=5)
        self.assertEqual(report["verdict"], "CHECK_ERROR")
        self.assertIn("unhealthy_lease_log", report["reasons"][0])
        failed = self.acquire("new-worker", "other.txt", expected=5)
        self.assertEqual(failed["status"], "ERROR")
        self.assertIn("unhealthy_lease_log", failed["error"])

    def test_malformed_override_log_event_forces_scope_check_error(self) -> None:
        governing = self.acquire("worker", "tracked.txt")
        baseline = self.baseline()
        malformed = dict(governing)
        malformed.update(
            {
                "event": "override",
                "lease_id": "lease-malformed-override",
                "invocation_id": "malformed-override",
                "owner_id": "malformed-override",
                "approver": "ed",
            }
        )
        log = self.repo / ".codex-bridge" / "workspace-lease-events.jsonl"
        with log.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(malformed) + "\n")
        report = self.scope_check(baseline, "tracked.txt", expected=5)
        self.assertEqual(report["verdict"], "CHECK_ERROR")
        self.assertIn("unhealthy_lease_log", report["reasons"][0])
        failed = self.acquire("new-worker", "other.txt", expected=5)
        self.assertEqual(failed["status"], "ERROR")
        self.assertIn("unhealthy_lease_log", failed["error"])

    def test_lease_append_rejects_unknown_owner_kind_with_check_error(self) -> None:
        result, report = self.bridge(
            "lease-acquire",
            "--invocation-id",
            "worker",
            "--owner-id",
            "worker",
            "--owner-kind",
            "unknown-owner",
            "--access",
            "write",
            "--paths",
            "tracked.txt",
            expected=5,
        )
        self.assertEqual(report["status"], "ERROR")
        self.assertIn("owner_kind", report["error"])

    def test_lease_pid_is_only_recorded_when_caller_supplies_it(self) -> None:
        without_pid = self.acquire("worker", "tracked.txt")
        self.assertNotIn("pid", without_pid)
        self.bridge("lease-release", "--lease-id", without_pid["lease_id"])
        with_pid = self.acquire(
            "worker-pid",
            "other.txt",
            extra=("--pid", "4242"),
        )
        self.assertEqual(with_pid["pid"], 4242)

    def test_session_open_creates_lease_baseline_pending_receipt_and_header(self) -> None:
        opened = self.session_open()
        requested_scope = [{"match": "exact", "path": "tracked.txt"}]
        expected_head = self.git("rev-parse", "HEAD").stdout.strip()
        expected_manifest_path = ".codex-bridge/baselines/session-worker.json"
        manifest = json.loads(
            (self.repo / expected_manifest_path).read_text(encoding="utf-8")
        )
        manifest_payload = {
            key: value for key, value in manifest.items() if key != "manifest_sha256"
        }
        expected_manifest_digest = "sha256:" + hashlib.sha256(
            json.dumps(
                manifest_payload,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            ).encode("utf-8")
        ).hexdigest()
        expected_scope_digest = "sha256:" + hashlib.sha256(
            json.dumps(
                requested_scope,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            ).encode("utf-8")
        ).hexdigest()
        lease_event = self.jsonl_events(
            ".codex-bridge/workspace-lease-events.jsonl"
        )[0]

        self.assertEqual(opened["schema"], "bridge-session-receipt/v1")
        self.assertEqual(opened["base_head"], expected_head)
        self.assertEqual(opened["baseline_manifest"], expected_manifest_path)
        self.assertEqual(opened["baseline_digest"], expected_manifest_digest)
        self.assertEqual(opened["write_scope"], requested_scope)
        self.assertEqual(opened["write_scope_digest"], expected_scope_digest)
        self.assertEqual(opened["lease_id"], lease_event["lease_id"])
        self.assertEqual(opened["lease_acquired_at"], lease_event["timestamp"])
        self.assertEqual(opened["owner"], {"id": "session-worker", "kind": "codex-cli"})
        self.assertEqual(manifest["manifest_sha256"], expected_manifest_digest)
        self.assertEqual(manifest["head_oid"], expected_head)
        self.assertEqual(manifest["invocation_id"], "session-worker")
        self.assertEqual(
            opened["header_fragment"],
            {
                "BASE_HEAD": expected_head,
                "BASELINE_MANIFEST": expected_manifest_path,
                "BASELINE_DIGEST": expected_manifest_digest,
                "WRITE_SCOPE": requested_scope,
            },
        )
        receipt_path = self.repo / ".codex-bridge" / "receipts" / "session-worker.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        self.assertEqual(receipt, {key: value for key, value in opened.items() if key != "header_fragment"})
        self.assertTrue((self.repo / expected_manifest_path).exists())
        leases = self.bridge("lease-list", "--active")[1]["leases"]
        self.assertEqual(leases[0]["lease_id"], opened["lease_id"])
        threads = self.bridge("thread-list", "--open")[1]["threads"]
        self.assertEqual(threads[0]["state"], "pending")
        self.assertEqual(threads[0]["baseline_digest"], opened["baseline_digest"])

    def test_session_open_existing_receipt_fails_without_new_partial_state(self) -> None:
        self.session_open()
        lease_events_before = self.jsonl_events(
            ".codex-bridge/workspace-lease-events.jsonl"
        )
        thread_events_before = self.jsonl_events(".codex-bridge/mcp-thread-events.jsonl")
        failed = self.session_open(expected=5)
        self.assertIn("session_invocation_id_already_used", failed["error"])
        self.assertIn("new invocation id", failed["error"])
        self.assertEqual(failed["lease_disposition"], "not_acquired")
        self.assertEqual(
            self.jsonl_events(".codex-bridge/workspace-lease-events.jsonl"),
            lease_events_before,
        )
        self.assertEqual(
            self.jsonl_events(".codex-bridge/mcp-thread-events.jsonl"),
            thread_events_before,
        )

    def test_session_open_refuses_baseline_only_invocation_before_acquire(self) -> None:
        self.baseline("baseline-collision")
        lease_events_before = self.jsonl_events(
            ".codex-bridge/workspace-lease-events.jsonl"
        )
        failed = self.session_open("baseline-collision", expected=5)
        self.assertEqual(failed["stage"], "validate")
        self.assertEqual(failed["lease_disposition"], "not_acquired")
        self.assertIn("baselines", failed["error"])
        self.assertEqual(
            self.jsonl_events(".codex-bridge/workspace-lease-events.jsonl"),
            lease_events_before,
        )
        self.assertFalse(
            (self.repo / ".codex-bridge" / "receipts" / "baseline-collision.json").exists()
        )

    def test_session_open_refuses_lease_only_invocation_before_new_event(self) -> None:
        bridge_dir = self.repo / ".codex-bridge"
        bridge_dir.mkdir()
        lock_path = bridge_dir / "session.lock"
        with lock_path.open("a+b") as lock_handle:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
            acquire = self.handshaking_bridge_process(
                "lease-acquire",
                "--invocation-id",
                "lease-only",
                "--owner-id",
                "lease-only",
                "--owner-kind",
                "codex-cli",
                "--access",
                "write",
                "--paths",
                "tracked.txt",
            )
            with self.assertRaises(subprocess.TimeoutExpired):
                acquire.wait(timeout=0.2)
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
        stdout, stderr = acquire.communicate(timeout=5)
        self.assertEqual(acquire.returncode, 0, stderr + stdout)
        self.assertEqual(json.loads(stdout)["event"], "acquire")
        events_before = self.jsonl_events(
            ".codex-bridge/workspace-lease-events.jsonl"
        )
        failed = self.session_open("lease-only", expected=5)
        self.assertEqual(failed["stage"], "validate")
        self.assertIn("lease log", failed["error"])
        self.assertIn("new invocation id", failed["error"])
        self.assertEqual(
            self.jsonl_events(".codex-bridge/workspace-lease-events.jsonl"),
            events_before,
        )
        self.assertFalse(
            (self.repo / ".codex-bridge/receipts/lease-only.json").exists()
        )

    def test_session_open_refuses_thread_only_invocation_before_acquire(self) -> None:
        self.bridge(
            "thread-record",
            "--invocation-id",
            "thread-only",
            "--state",
            "pending",
        )
        lease_events_before = self.jsonl_events(
            ".codex-bridge/workspace-lease-events.jsonl"
        )
        failed = self.session_open("thread-only", expected=5)
        self.assertEqual(failed["stage"], "validate")
        self.assertIn("thread log", failed["error"])
        self.assertEqual(
            self.jsonl_events(".codex-bridge/workspace-lease-events.jsonl"),
            lease_events_before,
        )

    def test_session_open_thread_record_failure_abandons_without_receipt(self) -> None:
        bridge_dir = self.repo / ".codex-bridge"
        bridge_dir.mkdir()
        (bridge_dir / "mcp-thread-events.jsonl").mkdir()
        failed = self.session_open("thread-failure", expected=5)
        self.assertEqual(failed["stage"], "thread-record")
        self.assertEqual(failed["lease_disposition"], "abandoned")
        lease_events = self.jsonl_events(
            ".codex-bridge/workspace-lease-events.jsonl"
        )
        self.assertEqual([event["event"] for event in lease_events], ["acquire", "abandon"])
        self.assertIn("session-open thread-record failed", lease_events[-1]["reason"])
        self.assertEqual(self.bridge("lease-list", "--active")[1]["leases"], [])
        self.assertFalse(
            (bridge_dir / "receipts" / "thread-failure.json").exists()
        )

    def test_session_open_receipt_write_failure_abandons_without_receipt(self) -> None:
        bridge_dir = self.repo / ".codex-bridge"
        bridge_dir.mkdir()
        (bridge_dir / "receipts").write_text("not a directory\n", encoding="utf-8")
        failed = self.session_open("receipt-failure", expected=5)
        self.assertEqual(failed["stage"], "receipt")
        self.assertEqual(failed["lease_disposition"], "abandoned")
        lease_events = self.jsonl_events(
            ".codex-bridge/workspace-lease-events.jsonl"
        )
        self.assertEqual([event["event"] for event in lease_events], ["acquire", "abandon"])
        self.assertIn("session-open receipt failed", lease_events[-1]["reason"])
        self.assertEqual(self.bridge("lease-list", "--active")[1]["leases"], [])
        self.assertFalse(
            (bridge_dir / "receipts" / "receipt-failure.json").exists()
        )

    def test_session_close_scope_ok_done_completes_and_releases(self) -> None:
        opened = self.session_open()
        self.assertTrue((self.repo / ".codex-bridge/session.lock").is_file())
        (self.repo / "tracked.txt").write_text("allowed\n", encoding="utf-8")
        closed = self.session_close()
        self.assertEqual(closed["scope_verdict"], "SCOPE_OK")
        self.assertEqual(closed["thread_state"], "complete")
        self.assertEqual(closed["lease_disposition"], "released")
        lease = next(
            item
            for item in self.bridge("lease-list")[1]["leases"]
            if item["lease_id"] == opened["lease_id"]
        )
        self.assertEqual(lease["state"], "released")
        thread = self.bridge("thread-list")[1]["threads"][0]
        self.assertEqual(thread["last_bridge_status"], "DONE")
        self.assertEqual(thread["scope_verdict"], "SCOPE_OK")

    def test_session_close_honors_prospective_lease_expansion(self) -> None:
        opened = self.session_open()
        expanded = self.bridge(
            "lease-expand",
            "--lease-id",
            opened["lease_id"],
            "--paths",
            "other.txt",
        )[1]
        (self.repo / "other.txt").write_text("expanded edit\n", encoding="utf-8")
        closed = self.session_close()
        expected_digest = "sha256:" + hashlib.sha256(
            json.dumps(
                expanded["paths"],
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            ).encode("utf-8")
        ).hexdigest()
        self.assertEqual(closed["scope_verdict"], "SCOPE_OK")
        self.assertEqual(closed["thread_state"], "complete")
        self.assertEqual(closed["lease_disposition"], "released")
        self.assertEqual(closed["scope_check"]["scope"], expanded["paths"])
        closing_thread = self.jsonl_events(
            ".codex-bridge/mcp-thread-events.jsonl"
        )[-1]
        self.assertEqual(closing_thread["write_scope_digest"], expected_digest)
        receipt = json.loads(
            (self.repo / ".codex-bridge/receipts/session-worker.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(receipt["write_scope"], [{"match": "exact", "path": "tracked.txt"}])
        self.assertNotEqual(receipt["write_scope_digest"], expected_digest)

    def test_session_close_needs_ruling_waits_and_retains_lease(self) -> None:
        opened = self.session_open()
        closed = self.session_close(status="NEEDS_RULING")
        self.assertEqual(closed["scope_verdict"], "SCOPE_OK")
        self.assertEqual(closed["thread_state"], "waiting_lead")
        self.assertEqual(closed["lease_disposition"], "retained")
        active = self.bridge("lease-list", "--active")[1]["leases"]
        self.assertEqual(active[0]["lease_id"], opened["lease_id"])
        thread = self.bridge("thread-list", "--open")[1]["threads"][0]
        self.assertEqual(thread["state"], "waiting_lead")
        self.assertEqual(thread["last_bridge_status"], "NEEDS_RULING")

    def test_session_close_edit_without_expand_violates_and_retains_lease(self) -> None:
        opened = self.session_open()
        (self.repo / "other.txt").write_text("outside scope\n", encoding="utf-8")
        closed = self.session_close(expected=3)
        self.assertEqual(closed["scope_verdict"], "SCOPE_VIOLATION")
        self.assertEqual(closed["thread_state"], "waiting_lead")
        self.assertEqual(closed["lease_disposition"], "retained")
        active = self.bridge("lease-list", "--active")[1]["leases"]
        self.assertEqual(active[0]["lease_id"], opened["lease_id"])
        thread = self.bridge("thread-list", "--open")[1]["threads"][0]
        self.assertEqual(thread["scope_verdict"], "SCOPE_VIOLATION")
        thread_events = self.jsonl_events(".codex-bridge/mcp-thread-events.jsonl")
        repeated = self.session_close(expected=3)
        self.assertIn("already recorded", repeated["notice"])
        self.assertEqual(
            self.jsonl_events(".codex-bridge/mcp-thread-events.jsonl"),
            thread_events,
        )

    def test_session_close_same_terminal_outcome_is_idempotent(self) -> None:
        self.session_open()
        self.session_close()
        thread_events_before = self.jsonl_events(".codex-bridge/mcp-thread-events.jsonl")
        lease_events_before = self.jsonl_events(
            ".codex-bridge/workspace-lease-events.jsonl"
        )
        repeated = self.session_close()
        self.assertEqual(repeated["lease_disposition"], "already_released")
        self.assertIn("already recorded", repeated["notice"])
        self.assertEqual(
            self.jsonl_events(".codex-bridge/mcp-thread-events.jsonl"),
            thread_events_before,
        )
        self.assertEqual(
            self.jsonl_events(".codex-bridge/workspace-lease-events.jsonl"),
            lease_events_before,
        )
        complete_events = [
            event
            for event in thread_events_before
            if event["state"] == "complete"
        ]
        self.assertEqual(len(complete_events), 1)
        release_events = [
            event for event in lease_events_before if event["event"] == "release"
        ]
        self.assertEqual(len(release_events), 1)
        refused = self.session_close(status="FAILED", expected=5)
        self.assertIn("contradictory terminal event", refused["error"])
        self.assertEqual(
            self.jsonl_events(".codex-bridge/mcp-thread-events.jsonl"),
            thread_events_before,
        )
        self.assertEqual(
            self.jsonl_events(".codex-bridge/workspace-lease-events.jsonl"),
            lease_events_before,
        )

    def test_session_close_discussion_is_access_independent_hard_error(self) -> None:
        errors = []
        opened_sessions = []
        for invocation_id, path, access in (
            ("discussion-write", "tracked.txt", "write"),
            ("discussion-snapshot", "other.txt", "snapshot_read"),
        ):
            opened = self.session_open(invocation_id, path)
            opened_sessions.append(opened)
            if access == "snapshot_read":
                lease_events = self.jsonl_events(
                    ".codex-bridge/workspace-lease-events.jsonl"
                )
                for event in lease_events:
                    if event["lease_id"] == opened["lease_id"]:
                        event["access"] = "snapshot_read"
                log_path = self.repo / ".codex-bridge/workspace-lease-events.jsonl"
                log_path.write_text(
                    "".join(json.dumps(event) + "\n" for event in lease_events),
                    encoding="utf-8",
                )
            thread_events_before = self.jsonl_events(
                ".codex-bridge/mcp-thread-events.jsonl"
            )
            failed = self.session_close(
                invocation_id, status="DISCUSSION", expected=5
            )
            errors.append(failed["error"])
            self.assertEqual(failed["lease_disposition"], "retained")
            self.assertEqual(
                self.jsonl_events(".codex-bridge/mcp-thread-events.jsonl"),
                thread_events_before,
            )
        self.assertEqual(errors[0], errors[1])
        self.assertIn("refuses --status DISCUSSION", errors[0])
        active_ids = {
            lease["lease_id"]
            for lease in self.bridge("lease-list", "--active")[1]["leases"]
        }
        self.assertEqual(active_ids, {opened["lease_id"] for opened in opened_sessions})

    def test_session_close_blocked_and_failed_wait_and_retain(self) -> None:
        for status in ("BLOCKED", "FAILED"):
            with self.subTest(status=status):
                invocation_id = f"session-{status.lower()}"
                opened = self.session_open(invocation_id)
                closed = self.session_close(invocation_id, status=status)
                self.assertEqual(closed["scope_verdict"], "SCOPE_OK")
                self.assertEqual(closed["thread_state"], "waiting_lead")
                self.assertEqual(closed["lease_disposition"], "retained")
                latest = self.jsonl_events(
                    ".codex-bridge/mcp-thread-events.jsonl"
                )[-1]
                self.assertEqual(latest["state"], "waiting_lead")
                self.assertEqual(latest["last_bridge_status"], status)
                active_ids = {
                    lease["lease_id"]
                    for lease in self.bridge("lease-list", "--active")[1]["leases"]
                }
                self.assertIn(opened["lease_id"], active_ids)
                self.bridge(
                    "lease-abandon",
                    "--lease-id",
                    opened["lease_id"],
                    "--approved-by",
                    "test",
                    "--reason",
                    "subtest cleanup",
                )

    def test_session_close_waiting_outcome_is_idempotent(self) -> None:
        self.session_open()
        first = self.session_close(status="NEEDS_RULING")
        events_after_first = self.jsonl_events(".codex-bridge/mcp-thread-events.jsonl")
        repeated = self.session_close(status="NEEDS_RULING")
        self.assertEqual(first["thread_state"], "waiting_lead")
        self.assertEqual(repeated["thread_state"], "waiting_lead")
        self.assertEqual(repeated["lease_disposition"], "retained")
        self.assertIn("already recorded", repeated["notice"])
        self.assertEqual(
            self.jsonl_events(".codex-bridge/mcp-thread-events.jsonl"),
            events_after_first,
        )
        waiting = [event for event in events_after_first if event["state"] == "waiting_lead"]
        self.assertEqual(len(waiting), 1)

    def test_waiting_close_dedupe_includes_current_scope_digest(self) -> None:
        opened = self.session_open()
        self.session_close(status="NEEDS_RULING")
        expanded = self.bridge(
            "lease-expand",
            "--lease-id",
            opened["lease_id"],
            "--paths",
            "other.txt",
        )[1]
        repeated = self.session_close(status="NEEDS_RULING")
        self.assertNotIn("notice", repeated)
        waiting = [
            event
            for event in self.jsonl_events(".codex-bridge/mcp-thread-events.jsonl")
            if event["state"] == "waiting_lead"
        ]
        self.assertEqual(len(waiting), 2)
        expected_digest = "sha256:" + hashlib.sha256(
            json.dumps(
                expanded["paths"],
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            ).encode("utf-8")
        ).hexdigest()
        self.assertNotEqual(waiting[0]["write_scope_digest"], expected_digest)
        self.assertEqual(waiting[1]["write_scope_digest"], expected_digest)

    def test_session_close_after_abandon_fails_with_observed_state(self) -> None:
        opened = self.session_open()
        self.bridge(
            "lease-abandon",
            "--lease-id",
            opened["lease_id"],
            "--approved-by",
            "test",
            "--reason",
            "explicit abandon before close",
        )
        lease_events_before = self.jsonl_events(
            ".codex-bridge/workspace-lease-events.jsonl"
        )
        thread_events_before = self.jsonl_events(".codex-bridge/mcp-thread-events.jsonl")
        failed = self.session_close(expected=5)
        self.assertEqual(failed["lease_disposition"], "abandoned")
        self.assertIn("already abandoned", failed["error"])
        self.assertEqual(
            self.jsonl_events(".codex-bridge/workspace-lease-events.jsonl"),
            lease_events_before,
        )
        self.assertFalse(any(event["event"] == "release" for event in lease_events_before))
        self.assertEqual(
            self.jsonl_events(".codex-bridge/mcp-thread-events.jsonl"),
            thread_events_before,
        )

    def test_session_close_lease_id_mismatch_reports_receipt_lease_state(self) -> None:
        self.session_open()
        failed = self.bridge(
            "session-close",
            "--invocation-id",
            "session-worker",
            "--status",
            "DONE",
            "--lease-id",
            "lease-" + "0" * 32,
            expected=5,
        )[1]
        self.assertEqual(failed["lease_disposition"], "retained")
        self.assertIn("does not match", failed["error"])

    def test_session_close_refreshes_disposition_after_abandon_during_release(self) -> None:
        opened = self.session_open()
        module = self.load_bridge_module()
        original_primitive = module.run_bridge_primitive

        def abandon_before_release(root: Path, arguments: list[str]):
            if arguments and arguments[0] == "lease-release":
                code, event = original_primitive(
                    root,
                    [
                        "lease-abandon",
                        "--lease-id",
                        opened["lease_id"],
                        "--approved-by",
                        "test",
                        "--reason",
                        "simulate external abandon during release",
                    ],
                )
                self.assertEqual(code, 0, event)
            return original_primitive(root, arguments)

        module.run_bridge_primitive = abandon_before_release
        arguments = argparse.Namespace(
            invocation_id="session-worker",
            status="DONE",
            lease_id=None,
            expect_digest=None,
        )
        output = io.StringIO()
        with mock.patch.object(module, "repository_root", return_value=self.repo):
            with redirect_stdout(output):
                code = module.command_session_close(arguments)
        self.assertEqual(code, 5)
        failed = json.loads(output.getvalue())
        self.assertEqual(failed["lease_disposition"], "abandoned")
        self.assertIn("already abandoned", failed["error"])

    def test_session_close_uses_receipt_digest_not_tampered_manifest_digest(self) -> None:
        opened = self.session_open()
        thread_events_before = self.jsonl_events(".codex-bridge/mcp-thread-events.jsonl")
        path = self.repo / opened["baseline_manifest"]
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["captured_at"] = "2026-07-13T01:02:03.000000Z"
        payload = {key: value for key, value in manifest.items() if key != "manifest_sha256"}
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        manifest["manifest_sha256"] = "sha256:" + hashlib.sha256(
            canonical.encode("utf-8")
        ).hexdigest()
        path.write_text(json.dumps(manifest), encoding="utf-8")
        closed = self.session_close(expected=5)
        self.assertEqual(closed["scope_verdict"], "CHECK_ERROR")
        self.assertEqual(closed["lease_disposition"], "retained")
        self.assertIn("--expect-digest", closed["error"])
        active = self.bridge("lease-list", "--active")[1]["leases"]
        self.assertEqual(active[0]["lease_id"], opened["lease_id"])
        self.assertEqual(
            self.jsonl_events(".codex-bridge/mcp-thread-events.jsonl"),
            thread_events_before,
        )

    def test_session_close_receipt_tampering_fails_before_terminal_or_release(self) -> None:
        zero_digest = "sha256:" + "0" * 64
        cases = (
            ("invocation_id", "tampered-invocation"),
            ("lease_id", "lease-" + "0" * 32),
            ("baseline_manifest", ".codex-bridge/baselines/missing.json"),
            ("baseline_digest", zero_digest),
            ("write_scope", [{"match": "exact", "path": "other.txt"}]),
            ("write_scope_digest", zero_digest),
            ("owner", {"id": "tampered-owner", "kind": "codex-cli"}),
        )
        for field, value in cases:
            with self.subTest(field=field):
                invocation_id = f"tamper-{field.replace('_', '-')}"
                opened = self.session_open(invocation_id)
                receipt_path = (
                    self.repo
                    / ".codex-bridge"
                    / "receipts"
                    / f"{invocation_id}.json"
                )
                receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
                receipt[field] = value
                if field == "write_scope":
                    receipt["write_scope_digest"] = "sha256:" + hashlib.sha256(
                        json.dumps(
                            value,
                            sort_keys=True,
                            separators=(",", ":"),
                            ensure_ascii=True,
                        ).encode("utf-8")
                    ).hexdigest()
                receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
                lease_events_before = self.jsonl_events(
                    ".codex-bridge/workspace-lease-events.jsonl"
                )
                thread_events_before = self.jsonl_events(
                    ".codex-bridge/mcp-thread-events.jsonl"
                )

                failed = self.session_close(invocation_id, expected=5)
                self.assertEqual(failed["scope_verdict"], "CHECK_ERROR")
                self.assertEqual(
                    self.jsonl_events(".codex-bridge/workspace-lease-events.jsonl"),
                    lease_events_before,
                )
                self.assertFalse(
                    any(
                        event["event"] == "release"
                        and event["lease_id"] == opened["lease_id"]
                        for event in lease_events_before
                    )
                )
                self.assertEqual(
                    self.jsonl_events(".codex-bridge/mcp-thread-events.jsonl"),
                    thread_events_before,
                )
                self.bridge(
                    "lease-abandon",
                    "--lease-id",
                    opened["lease_id"],
                    "--approved-by",
                    "test",
                    "--reason",
                    "tamper subtest cleanup",
                )

    def test_baseline_refuses_reused_invocation_id(self) -> None:
        first = self.baseline("stable")
        second = self.baseline("stable", expected=5)
        self.assertEqual(second["status"], "ERROR")
        self.assertIn("baseline_already_exists", second["error"])
        manifest = json.loads((self.repo / first["path"]).read_text(encoding="utf-8"))
        self.assertEqual(manifest["manifest_sha256"], first["manifest_sha256"])
        payload = {key: value for key, value in manifest.items() if key != "manifest_sha256"}
        shuffled = dict(reversed(list(payload.items())))
        canonical = json.dumps(shuffled, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        self.assertEqual(
            first["manifest_sha256"],
            "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        )

    def test_baseline_captures_dirty_file_content_sha256(self) -> None:
        content = b"dirty bytes\n"
        (self.repo / "tracked.txt").write_bytes(content)
        baseline = self.baseline("dirty")
        manifest = json.loads((self.repo / baseline["path"]).read_text(encoding="utf-8"))
        row = next(item for item in manifest["dirty_paths"] if item["path"] == "tracked.txt")
        self.assertEqual(row["entry_type"], "file")
        self.assertEqual(row["mode"], "100644")
        self.assertEqual(row["content_sha256"], hashlib.sha256(content).hexdigest())

    def test_scope_ok_for_in_scope_persistent_edit(self) -> None:
        self.acquire("worker", "tracked.txt")
        baseline = self.baseline()
        (self.repo / "tracked.txt").write_text("allowed\n", encoding="utf-8")
        report = self.scope_check(baseline, "tracked.txt")
        self.assertEqual(report["verdict"], "SCOPE_OK")
        row = next(item for item in report["paths"] if item["path"] == "tracked.txt")
        self.assertEqual(row["disposition"], "in_scope")

    def test_scope_check_without_governing_lease_is_indeterminate(self) -> None:
        baseline = self.baseline()
        (self.repo / "tracked.txt").write_text("allowed but unattributed\n", encoding="utf-8")
        report = self.scope_check(baseline, "tracked.txt", expected=4)
        self.assertEqual(report["verdict"], "ATTRIBUTION_INDETERMINATE")
        self.assertIn("no_governing_lease", report["reasons"])

    def test_scope_check_accepts_released_governing_lease(self) -> None:
        lease = self.acquire("worker", "tracked.txt")
        baseline = self.baseline()
        (self.repo / "tracked.txt").write_text("allowed\n", encoding="utf-8")
        self.bridge("lease-release", "--lease-id", lease["lease_id"])
        report = self.scope_check(baseline, "tracked.txt")
        self.assertEqual(report["verdict"], "SCOPE_OK")

    def test_scope_check_can_select_explicit_governing_lease(self) -> None:
        lease = self.acquire("lease-owner", "tracked.txt")
        baseline = self.baseline("worker")
        (self.repo / "tracked.txt").write_text("allowed\n", encoding="utf-8")
        report = self.scope_check(baseline, "tracked.txt", lease_id=lease["lease_id"])
        self.assertEqual(report["verdict"], "SCOPE_OK")

    def test_scope_violation_lists_out_of_scope_edit(self) -> None:
        self.acquire("worker", "tracked.txt")
        baseline = self.baseline()
        (self.repo / "other.txt").write_text("not allowed\n", encoding="utf-8")
        report = self.scope_check(baseline, "tracked.txt", expected=3)
        self.assertEqual(report["verdict"], "SCOPE_VIOLATION")
        row = next(item for item in report["paths"] if item["path"] == "other.txt")
        self.assertEqual(row["disposition"], "out_of_scope")

    def test_scope_check_exempts_bridge_internal_git_visible_delta(self) -> None:
        self.acquire("worker", "tracked.txt")
        baseline = self.baseline()
        internal = self.repo / ".codex-bridge" / "tracked-internal.txt"
        internal.write_text("internal\n", encoding="utf-8")
        self.git("add", "-f", ".codex-bridge/tracked-internal.txt")
        report = self.scope_check(baseline, "tracked.txt")
        self.assertEqual(report["verdict"], "SCOPE_OK")
        row = next(item for item in report["paths"] if item["path"].startswith(".codex-bridge/"))
        self.assertEqual(row["disposition"], "exempt")

    def test_foreign_overlapping_writer_makes_changed_path_indeterminate(self) -> None:
        self.acquire("worker", "tracked.txt")
        baseline = self.baseline("worker")
        lease = self.acquire(
            "foreign",
            "tracked.txt",
            extra=("--override", "--approved-by", "ed", "--reason", "foreign write"),
        )
        (self.repo / "tracked.txt").write_text("ambiguous\n", encoding="utf-8")
        report = self.scope_check(baseline, "tracked.txt", expected=4)
        self.assertEqual(report["verdict"], "ATTRIBUTION_INDETERMINATE")
        row = next(item for item in report["paths"] if item["path"] == "tracked.txt")
        self.assertEqual(row["conflicting_lease_ids"], [lease["lease_id"]])

    def test_overridden_snapshot_overlap_makes_scope_attribution_indeterminate(self) -> None:
        self.acquire("reader", "tracked.txt", access="snapshot_read")
        override = self.acquire(
            "worker",
            "tracked.txt",
            extra=("--override", "--approved-by", "ed", "--reason", "lead-approved write"),
        )
        baseline = self.baseline("worker")
        (self.repo / "tracked.txt").write_text("overridden\n", encoding="utf-8")
        report = self.scope_check(baseline, "tracked.txt", expected=4)
        self.assertEqual(report["verdict"], "ATTRIBUTION_INDETERMINATE")
        row = next(item for item in report["paths"] if item["path"] == "tracked.txt")
        self.assertEqual(row["conflicting_lease_ids"], [override["lease_id"]])

    def test_unauthorized_commit_is_scope_violation_even_when_path_is_scoped(self) -> None:
        self.acquire("worker", "tracked.txt")
        baseline = self.baseline()
        (self.repo / "tracked.txt").write_text("committed\n", encoding="utf-8")
        self.git("add", "tracked.txt")
        self.git("commit", "-qm", "unauthorized")
        report = self.scope_check(baseline, "tracked.txt", expected=3)
        self.assertEqual(report["verdict"], "SCOPE_VIOLATION")
        self.assertEqual(report["head_disposition"], "unauthorized")
        allowed = self.scope_check(baseline, "tracked.txt", allow_commits=True)
        self.assertEqual(allowed["verdict"], "SCOPE_OK")
        self.assertEqual(allowed["head_disposition"], "authorized")

    def test_authorized_commit_then_revert_of_out_of_scope_path_is_violation(self) -> None:
        self.acquire("worker", "tracked.txt")
        baseline = self.baseline()
        (self.repo / "other.txt").write_text("temporary out of scope\n", encoding="utf-8")
        self.git("add", "other.txt")
        self.git("commit", "-qm", "out of scope")
        self.git("revert", "--no-edit", "HEAD")
        report = self.scope_check(
            baseline,
            "tracked.txt",
            expected=3,
            allow_commits=True,
        )
        self.assertEqual(report["verdict"], "SCOPE_VIOLATION")
        row = next(item for item in report["paths"] if item["path"] == "other.txt")
        self.assertEqual(row["disposition"], "out_of_scope")
        self.assertIn("commit history", row["reasons"][0])

    def test_corrupted_manifest_is_check_error(self) -> None:
        baseline = self.baseline()
        path = self.repo / baseline["path"]
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["head_oid"] = "0" * 40
        path.write_text(json.dumps(manifest), encoding="utf-8")
        report = self.scope_check(baseline, "tracked.txt", expected=5)
        self.assertEqual(report["verdict"], "CHECK_ERROR")
        self.assertIn("digest mismatch", report["reasons"][0])

    def test_recomputed_manifest_digest_cannot_replace_prompt_anchor(self) -> None:
        baseline = self.baseline()
        path = self.repo / baseline["path"]
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["captured_at"] = "2026-07-13T01:02:03.000000Z"
        payload = {key: value for key, value in manifest.items() if key != "manifest_sha256"}
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        manifest["manifest_sha256"] = "sha256:" + hashlib.sha256(
            canonical.encode("utf-8")
        ).hexdigest()
        path.write_text(json.dumps(manifest), encoding="utf-8")
        report = self.scope_check(baseline, "tracked.txt", expected=5)
        self.assertEqual(report["verdict"], "CHECK_ERROR")
        self.assertIn("--expect-digest", report["reasons"][0])

    def test_scope_check_missing_expected_digest_is_check_error(self) -> None:
        baseline = self.baseline()
        report = self.bridge(
            "scope-check",
            "--baseline",
            baseline["path"],
            "--scope",
            "tracked.txt",
            expected=5,
        )[1]
        self.assertEqual(report["verdict"], "CHECK_ERROR")
        self.assertIn("--expect-digest", report["reasons"][0])

    def test_thread_pending_event_binds_to_returned_thread(self) -> None:
        self.bridge(
            "thread-record",
            "--invocation-id",
            "invoke-one",
            "--state",
            "pending",
            "--task",
            "review",
        )
        self.bridge(
            "thread-record",
            "--invocation-id",
            "invoke-one",
            "--state",
            "active",
            "--thread-id",
            "thread-123",
            "--last-status",
            "PARTIAL",
        )
        listing = self.bridge("thread-list", "--open")[1]
        self.assertEqual(len(listing["threads"]), 1)
        self.assertEqual(listing["threads"][0]["thread_id"], "thread-123")
        self.assertEqual(listing["threads"][0]["state"], "active")

    def test_lost_before_return_is_terminal_in_derived_open_index(self) -> None:
        event = self.bridge(
            "thread-record",
            "--invocation-id",
            "lost-call",
            "--state",
            "lost_before_return",
            "--resume-policy",
            "fresh_required",
        )[1]
        self.assertIsNone(event["thread_id"])
        self.assertEqual(self.bridge("thread-list", "--open")[1]["threads"], [])
        all_threads = self.bridge("thread-list")[1]["threads"]
        self.assertEqual(all_threads[0]["state"], "lost_before_return")


if __name__ == "__main__":
    unittest.main()
