"""Defect-shaped checks for the tracked bridge-protocol/v1 helper."""

from __future__ import annotations

import hashlib
import json
import multiprocessing
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
BRIDGE = REPO_ROOT / "scripts" / "bridge"


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
