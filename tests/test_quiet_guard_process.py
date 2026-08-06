"""Tests for exact quiet-guard process identities and census primitives."""

from __future__ import annotations

import subprocess
import unittest

from joulewise.quiet_guard_process import (
    AncestorIdentity,
    DarwinProcessRecord,
    ProcessIdentity,
    ProcessIdentityError,
    PsProcessSource,
    Revalidation,
    SnapshotProcessSource,
    SysctlDarwinProcessReader,
    argv_digest,
    descends_from,
    independent_census,
    revalidate_identity,
    validate_identity_mapping,
)


class SequenceReader:
    def __init__(self, rows):
        self.rows = {pid: list(values) for pid, values in rows.items()}
        self.last = {}

    def read(self, pid):
        values = self.rows.get(pid, [])
        if values:
            self.last[pid] = values.pop(0)
        return self.last.get(pid)


def identity(
    pid: int = 42,
    *,
    start_time: str = "boot+10.000001",
    executable: str = "/Applications/T3 Code (Alpha).app/Contents/MacOS/t3",
    argv: tuple[str, ...] = ("t3", "--session", "abc"),
    ancestry: tuple[AncestorIdentity, ...] = (),
) -> ProcessIdentity:
    return ProcessIdentity(pid, start_time, executable, argv_digest(argv), ancestry)


class ArgvDigestTests(unittest.TestCase):
    def test_vector_boundaries_are_unambiguous(self) -> None:
        self.assertNotEqual(argv_digest(("ab", "c")), argv_digest(("a", "bc")))

    def test_raw_observation_is_domain_separated(self) -> None:
        self.assertNotEqual(argv_digest(b"a b"), argv_digest(("a", "b")))

    def test_rejects_non_string_vector_entry(self) -> None:
        with self.assertRaises(ProcessIdentityError):
            argv_digest(("ok", 3))  # type: ignore[arg-type]


class IdentitySchemaTests(unittest.TestCase):
    def test_round_trip_preserves_complete_identity(self) -> None:
        parent = identity(7, argv=("parent",))
        row = identity(
            ancestry=(
                AncestorIdentity(
                    parent.pid,
                    parent.start_time,
                    parent.executable,
                    parent.argv_digest,
                ),
            )
        )
        self.assertEqual(validate_identity_mapping(row.to_mapping()), row)

    def test_extra_field_is_rejected(self) -> None:
        raw = identity().to_mapping()
        raw["ttl"] = 30
        with self.assertRaises(ProcessIdentityError):
            validate_identity_mapping(raw)

    def test_bad_digest_is_rejected(self) -> None:
        raw = identity().to_mapping()
        raw["argv_digest"] = "sha256:nope"
        with self.assertRaises(ProcessIdentityError):
            validate_identity_mapping(raw)

    def test_ancestry_cycle_is_rejected(self) -> None:
        ancestor = AncestorIdentity(42, "older", "/bin/a", argv_digest(("a",)))
        with self.assertRaises(ProcessIdentityError):
            identity(42, ancestry=(ancestor,))


class RevalidationTests(unittest.TestCase):
    def test_exact_match_requires_all_fields(self) -> None:
        expected = identity()
        verdict, observed = revalidate_identity(
            expected, SnapshotProcessSource((expected,))
        )
        self.assertEqual(verdict, Revalidation.MATCH)
        self.assertEqual(observed, expected)

    def test_absent_pid_is_stale(self) -> None:
        verdict, observed = revalidate_identity(identity(), SnapshotProcessSource())
        self.assertEqual(verdict, Revalidation.ABSENT)
        self.assertIsNone(observed)

    def test_reused_pid_start_time_is_not_a_match(self) -> None:
        expected = identity()
        reused = identity(start_time="boot+99")
        verdict, observed = revalidate_identity(
            expected, SnapshotProcessSource((reused,))
        )
        self.assertEqual(verdict, Revalidation.PID_REUSED)
        self.assertEqual(observed, reused)

    def test_executable_change_is_pid_reuse(self) -> None:
        expected = identity()
        changed = identity(executable="/tmp/not-t3")
        self.assertEqual(
            revalidate_identity(expected, SnapshotProcessSource((changed,)))[0],
            Revalidation.PID_REUSED,
        )

    def test_argv_change_is_pid_reuse(self) -> None:
        expected = identity()
        changed = identity(argv=("t3", "--different"))
        self.assertEqual(
            revalidate_identity(expected, SnapshotProcessSource((changed,)))[0],
            Revalidation.PID_REUSED,
        )

    def test_ancestry_change_is_pid_reuse(self) -> None:
        expected = identity()
        parent = AncestorIdentity(2, "boot+1", "/sbin/launchd", argv_digest(("launchd",)))
        changed = identity(ancestry=(parent,))
        self.assertEqual(
            revalidate_identity(expected, SnapshotProcessSource((changed,)))[0],
            Revalidation.PID_REUSED,
        )

    def test_same_second_pid_reuse_is_rejected_by_microsecond_identity(self) -> None:
        expected = identity(start_time="1785940800.000101", argv=("t3", "--one"))
        reused = identity(start_time="1785940800.900101", argv=("t3", "--two"))
        self.assertEqual(expected.start_time.split(".")[0], reused.start_time.split(".")[0])
        self.assertEqual(
            revalidate_identity(expected, SnapshotProcessSource((reused,)))[0],
            Revalidation.PID_REUSED,
        )


class CensusTests(unittest.TestCase):
    def test_independent_census_filters_and_sorts(self) -> None:
        source = SnapshotProcessSource((identity(8), identity(3), identity(5)))
        rows = independent_census(source, lambda row: row.pid != 5)
        self.assertEqual([row.pid for row in rows], [3, 8])

    def test_descendant_requires_exact_ancestor(self) -> None:
        parent = identity(7, start_time="parent-start", argv=("parent",))
        child = identity(
            8,
            ancestry=(
                AncestorIdentity(
                    parent.pid,
                    parent.start_time,
                    parent.executable,
                    parent.argv_digest,
                ),
            ),
        )
        self.assertTrue(descends_from(child, parent))
        self.assertFalse(descends_from(child, identity(7, start_time="reused")))


class PsProcessSourceTests(unittest.TestCase):
    def test_observer_builds_full_ancestry_and_rechecks_entire_chain(self) -> None:
        child = DarwinProcessRecord(10, 1, "1785940800.123456", "/app/t3", ("t3", "--session", "abc"))
        parent = DarwinProcessRecord(1, 0, "1785940000.000001", "/sbin/launchd", ("/sbin/launchd",))
        reader = SequenceReader({10: (child, child), 1: (parent, parent)})
        observed = PsProcessSource(reader=reader).observe(10)
        self.assertIsNotNone(observed)
        assert observed is not None
        self.assertEqual(observed.pid, 10)
        self.assertEqual([row.pid for row in observed.ancestry], [1])
        self.assertEqual(observed.start_time, "1785940800.123456")
        self.assertEqual(observed.executable, "/app/t3")

    def test_child_change_during_ancestry_traversal_is_torn(self) -> None:
        child = DarwinProcessRecord(10, 1, "1785940800.123456", "/app/t3", ("t3", "--one"))
        changed_child = DarwinProcessRecord(10, 99, "1785940800.123456", "/app/t3", ("t3", "--one"))
        parent = DarwinProcessRecord(1, 0, "1785940000.000001", "/sbin/launchd", ("launchd",))
        reader = SequenceReader({10: (child, changed_child), 1: (parent,)})
        self.assertIsNone(PsProcessSource(reader=reader).observe(10))

    def test_true_argv_ambiguity_changes_identity_despite_same_display(self) -> None:
        display_command = "t3 --token REDACTED"
        first = DarwinProcessRecord(10, 0, "1785940800.123456", "/app/t3", ("t3", "--token", "one"))
        second = DarwinProcessRecord(10, 0, "1785940800.123456", "/app/t3", ("t3", "--token", "two"))
        first_identity = PsProcessSource(reader=SequenceReader({10: (first, first)})).observe(10)
        second_identity = PsProcessSource(reader=SequenceReader({10: (second, second)})).observe(10)
        self.assertEqual(display_command, display_command)
        self.assertIsNotNone(first_identity)
        self.assertIsNotNone(second_identity)
        self.assertNotEqual(first_identity, second_identity)

    def test_non_darwin_sysctl_reader_fails_closed(self) -> None:
        reader = SysctlDarwinProcessReader(platform_name="linux")
        self.assertIsNone(reader.read(99))

    def test_failed_census_is_refusal_not_false_zero(self) -> None:
        def runner(arguments, **kwargs):
            del kwargs
            return subprocess.CompletedProcess(arguments, 1, stdout=b"", stderr=b"gone")

        with self.assertRaises(ProcessIdentityError):
            PsProcessSource(runner, reader=SequenceReader({})).census()


if __name__ == "__main__":
    unittest.main()
