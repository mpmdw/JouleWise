"""Tests for snapshot-bound quiet-guard process identity and kernel census."""

from __future__ import annotations

import ctypes
import errno
import inspect
import os
from pathlib import Path
import struct
import sys
import unittest

from joulewise.quiet_guard_process import (
    AncestorIdentity,
    DarwinProcessRecord,
    DarwinProcessSource,
    KINFO_PROC_PID_OFFSET,
    KINFO_PROC_PPID_OFFSET,
    KINFO_PROC_SIZE,
    KernelProcessRecord,
    KernelProcessTable,
    ProcessIdentity,
    ProcessIdentityError,
    ProcessObservationError,
    Revalidation,
    SnapshotProcessSource,
    SysctlDarwinProcessReader,
    argv_digest,
    custody_candidate_pids,
    revalidate_identity,
    validate_identity_mapping,
)


def identity(
    pid: int = 42,
    *,
    start_time: str = "1785940800.000001",
    executable: str = "/Applications/T3 Code (Alpha).app/Contents/MacOS/t3",
    argv: tuple[str, ...] = ("t3", "--session", "abc"),
    ancestry: tuple[AncestorIdentity, ...] = (),
) -> ProcessIdentity:
    return ProcessIdentity(pid, start_time, executable, argv_digest(argv), ancestry)


def kinfo_proc_row(
    pid: int,
    ppid: int,
    seconds: int,
    microseconds: int,
) -> bytes:
    """Build one byte-accurate 64-bit Darwin SDK ``struct kinfo_proc``."""

    class Timeval(ctypes.Structure):
        _fields_ = (("tv_sec", ctypes.c_long), ("tv_usec", ctypes.c_int))

    payload = bytearray(KINFO_PROC_SIZE)
    encoded_time = bytes(Timeval(seconds, microseconds))
    payload[: len(encoded_time)] = encoded_time
    struct.pack_into("=i", payload, KINFO_PROC_PID_OFFSET, pid)
    struct.pack_into("=i", payload, KINFO_PROC_PPID_OFFSET, ppid)
    return bytes(payload)


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

    def test_bad_digest_and_ancestry_cycle_are_rejected(self) -> None:
        raw = identity().to_mapping()
        raw["argv_digest"] = "sha256:nope"
        with self.assertRaises(ProcessIdentityError):
            validate_identity_mapping(raw)
        with self.assertRaises(ProcessIdentityError):
            identity(
                42,
                ancestry=(
                    AncestorIdentity(42, "older", "/bin/a", argv_digest(("a",))),
                ),
            )


class SnapshotRevalidationTests(unittest.TestCase):
    def test_exact_match_absence_and_pid_reuse_use_one_snapshot(self) -> None:
        expected = identity()
        matching = SnapshotProcessSource((expected,))
        snapshot = matching.inventory()
        self.assertEqual(
            revalidate_identity(expected, matching, snapshot),
            (Revalidation.MATCH, expected),
        )

        absent = SnapshotProcessSource()
        self.assertEqual(
            revalidate_identity(expected, absent, absent.inventory()),
            (Revalidation.ABSENT, None),
        )

        reused = identity(start_time="1785940800.900101", argv=("t3", "--two"))
        reused_source = SnapshotProcessSource((reused,))
        self.assertEqual(
            revalidate_identity(expected, reused_source, reused_source.inventory()),
            (Revalidation.PID_REUSED, reused),
        )

    def test_observation_failure_is_not_absence(self) -> None:
        expected = identity()
        source = SnapshotProcessSource((expected,), unobservable_pids=(expected.pid,))
        self.assertEqual(
            revalidate_identity(expected, source, source.inventory()),
            (Revalidation.UNOBSERVABLE, None),
        )

    def test_same_start_identity_churn_is_not_pid_reuse(self) -> None:
        expected = identity()
        variants = (
            identity(executable="/tmp/not-t3"),
            identity(argv=("t3", "--different")),
            identity(
                ancestry=(
                    AncestorIdentity(
                        2, "1785940000.1", "/sbin/launchd", argv_digest(("launchd",))
                    ),
                )
            ),
        )
        for changed in variants:
            with self.subTest(changed=changed):
                source = SnapshotProcessSource((changed,))
                self.assertEqual(
                    revalidate_identity(expected, source, source.inventory())[0],
                    Revalidation.UNOBSERVABLE,
                )


class KernelTableAndStateSchemaPrimitiveTests(unittest.TestCase):
    """KERNEL-TABLE-AND-STATE-SCHEMA process-table half."""

    def test_pid_zero_kernel_fixture_decodes_inventories_and_derives_candidates(self) -> None:
        self.assertEqual(
            (KINFO_PROC_SIZE, KINFO_PROC_PID_OFFSET, KINFO_PROC_PPID_OFFSET),
            (648, 40, 560),
        )
        payload = b"".join(
            (
                kinfo_proc_row(0, 0, 1_785_939_000, 999_999),
                kinfo_proc_row(1, 0, 1_785_940_000, 1),
                kinfo_proc_row(321, 1, 1_785_940_800, 654_321),
                kinfo_proc_row(322, 321, 1_785_940_801, 123_456),
            )
        )
        decoded = SysctlDarwinProcessReader.decode_kernel_table(payload)

        class PayloadReader(SysctlDarwinProcessReader):
            def _sysctl_size(self, mib):
                self.size_mib = tuple(mib)
                return len(payload)

            def _sysctl_capacity(self, mib, capacity):
                self.capacity_mib = tuple(mib)
                self.asserted_capacity = capacity
                return payload

        reader = PayloadReader(platform_name="darwin")
        table = reader.inventory()
        self.assertEqual(table, decoded)
        self.assertEqual(
            reader.size_mib,
            (reader.CTL_KERN, reader.KERN_PROC, reader.KERN_PROC_ALL, 0),
        )
        self.assertEqual(
            reader.capacity_mib,
            (reader.CTL_KERN, reader.KERN_PROC, reader.KERN_PROC_ALL, 0),
        )
        self.assertGreater(reader.asserted_capacity, len(payload))
        self.assertEqual(
            table.rows,
            (
                KernelProcessRecord(0, 0, "1785939000.999999"),
                KernelProcessRecord(1, 0, "1785940000.000001"),
                KernelProcessRecord(321, 1, "1785940800.654321"),
                KernelProcessRecord(322, 321, "1785940801.123456"),
            ),
        )
        active, descendants = custody_candidate_pids(
            table, (identity(321, start_time="1785940800.654321"),)
        )
        self.assertEqual(active, {321})
        self.assertEqual(descendants, {322})

    def test_pid_zero_is_inventory_only_not_a_custody_root_or_candidate(self) -> None:
        table = KernelProcessTable(
            (
                KernelProcessRecord(0, 0, "1785939000.999999"),
                KernelProcessRecord(1, 0, "1785940000.000001"),
            )
        )
        with self.assertRaises(ProcessIdentityError):
            identity(0)
        with self.assertRaises(ProcessObservationError):
            table.descendants(0)
        with self.assertRaises(ProcessObservationError):
            DarwinProcessSource().observe(0, table)

    def test_malformed_duplicate_missing_parent_and_cyclic_tables_refuse(self) -> None:
        malformed_payloads = (
            b"",
            b"short",
            kinfo_proc_row(1, 0, 1_785_940_000, 1)
            + kinfo_proc_row(1, 0, 1_785_940_001, 2),
            kinfo_proc_row(2, 99, 1_785_940_000, 1),
            kinfo_proc_row(2, 3, 1_785_940_000, 1)
            + kinfo_proc_row(3, 2, 1_785_940_001, 2),
        )
        for payload in malformed_payloads:
            with self.subTest(size=len(payload)), self.assertRaises(
                ProcessObservationError
            ):
                SysctlDarwinProcessReader.decode_kernel_table(payload)

    def test_candidate_derivation_requires_root_pid_and_microsecond_start(self) -> None:
        table = KernelProcessTable(
            (
                KernelProcessRecord(1, 0, "1785940000.000001"),
                KernelProcessRecord(10, 1, "1785940800.000101"),
                KernelProcessRecord(11, 10, "1785940801.000001"),
                KernelProcessRecord(20, 1, "1785940802.000001"),
            )
        )
        active, descendants = custody_candidate_pids(
            table, (identity(10, start_time="1785940800.000101"),)
        )
        self.assertEqual(active, {10})
        self.assertEqual(descendants, {11})
        reused_active, reused_descendants = custody_candidate_pids(
            table, (identity(10, start_time="1785940800.900101"),)
        )
        self.assertFalse(reused_active)
        self.assertFalse(reused_descendants)

    def test_ps_self_row_failure_mode_is_removed(self) -> None:
        source = Path("joulewise/quiet_guard_process.py").read_text()
        self.assertNotIn("/bin/ps", source)
        self.assertNotIn("subprocess", source)
        self.assertNotIn("protected_identities", source)
        self.assertEqual(
            tuple(inspect.signature(DarwinProcessSource.inventory).parameters),
            ("self",),
        )


class DarwinProcessSourceTests(unittest.TestCase):
    def test_targeted_observer_builds_full_snapshot_bound_ancestry(self) -> None:
        table = KernelProcessTable(
            (
                KernelProcessRecord(1, 0, "1785940000.000001"),
                KernelProcessRecord(10, 1, "1785940800.123456"),
            )
        )
        exact = {
            1: DarwinProcessRecord(
                1, 0, "1785940000.000001", "/sbin/launchd", ("/sbin/launchd",)
            ),
            10: DarwinProcessRecord(
                10, 1, "1785940800.123456", "/app/t3", ("t3", "--session", "abc")
            ),
        }

        class Reader:
            def __init__(self) -> None:
                self.calls: list[int] = []

            def inventory(self):
                return table

            def read_exact(self, expected):
                self.calls.append(expected.pid)
                return exact[expected.pid]

        reader = Reader()
        source = DarwinProcessSource(reader=reader)
        snapshot = source.inventory()
        observed = source.observe(10, snapshot)
        self.assertIsNotNone(observed)
        assert observed is not None
        self.assertEqual([row.pid for row in observed.ancestry], [1])
        self.assertEqual(observed.argv_digest, argv_digest(("t3", "--session", "abc")))
        self.assertEqual(reader.calls, [10, 1, 10, 1])

    def test_candidate_disappearance_is_not_absence(self) -> None:
        table = KernelProcessTable((KernelProcessRecord(10, 0, "1785940800.1"),))

        class Reader:
            def inventory(self):
                return table

            def read_exact(self, expected):
                del expected
                return None

        source = DarwinProcessSource(reader=Reader())
        self.assertIsNone(source.observe(10, source.inventory()))


class SysctlExactReaderTests(unittest.TestCase):
    def test_exact_decoder_preserves_true_argv_boundaries(self) -> None:
        pid = 321
        row_payload = kinfo_proc_row(pid, 0, 1_785_940_800, 654_321)
        executable = "/Applications/T3 Code (Alpha).app/Contents/MacOS/t3"
        arguments = ("t3", "--label=alpha beta", "", "tail value")
        argv_payload = (
            struct.pack("=i", len(arguments))
            + executable.encode()
            + b"\0\0\0"
            + b"\0".join(argument.encode() for argument in arguments)
            + b"\0PATH=/not-an-argument\0"
        )

        class PayloadReader(SysctlDarwinProcessReader):
            def _sysctl(self, mib, capacity=None):
                del capacity
                key = tuple(mib)
                if key == (self.CTL_KERN, self.KERN_ARGMAX):
                    return struct.pack("=i", 4096)
                if key == (self.CTL_KERN, self.KERN_PROC, self.KERN_PROC_PID, pid):
                    return row_payload
                if key == (self.CTL_KERN, self.KERN_PROCARGS2, pid):
                    return argv_payload
                raise AssertionError(key)

        reader = PayloadReader(platform_name="darwin")
        expected = KernelProcessRecord(pid, 0, "1785940800.654321")
        self.assertEqual(
            reader.read_exact(expected),
            DarwinProcessRecord(
                pid, 0, "1785940800.654321", executable, arguments
            ),
        )

    def test_non_darwin_and_esrch_are_fail_closed(self) -> None:
        with self.assertRaises(ProcessObservationError):
            SysctlDarwinProcessReader(platform_name="linux").read_exact(
                KernelProcessRecord(99, 0, "1.000001")
            )

        class AbsentReader(SysctlDarwinProcessReader):
            def _sysctl(self, mib, capacity=None):
                del mib, capacity
                raise ProcessObservationError("gone", error_number=errno.ESRCH)

        self.assertIsNone(
            AbsentReader(platform_name="darwin").read_exact(
                KernelProcessRecord(99, 0, "1.000001")
            )
        )


@unittest.skipUnless(
    sys.platform == "darwin" and os.environ.get("QG_LIVE_DARWIN") == "1",
    "requires Darwin and explicit QG_LIVE_DARWIN=1 real-acquisition opt-in",
)
class LiveDarwinKernelInventoryTests(unittest.TestCase):
    def test_real_inventory_contains_self_and_parent_with_exact_linkage(self) -> None:
        table = SysctlDarwinProcessReader().inventory()
        by_pid = table.by_pid
        own_pid = os.getpid()
        parent_pid = os.getppid()

        self.assertIn(0, by_pid)
        self.assertIn(own_pid, by_pid)
        self.assertIn(parent_pid, by_pid)
        self.assertEqual(by_pid[own_pid].ppid, parent_pid)
        self.assertEqual(by_pid[parent_pid].pid, parent_pid)
        for row in (by_pid[own_pid], by_pid[parent_pid]):
            seconds, microseconds = row.start_time.split(".", 1)
            self.assertGreater(int(seconds), 0)
            self.assertEqual(len(microseconds), 6)
            self.assertTrue(microseconds.isdigit())


if __name__ == "__main__":
    unittest.main()
