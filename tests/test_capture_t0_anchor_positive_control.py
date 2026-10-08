"""Offset-preflight fixtures using the real collector and author; no live probes."""
from contextlib import redirect_stdout
import io
import itertools
import subprocess
import time
import unittest
from unittest import mock

from joulewise import arm_readiness as readiness, network_time_off
from joulewise import v5_qualification as q
from scripts import collect_clock_reference
from scripts.ed_session import capture_t0_anchor_positive_control as g10
from tests import test_t0_anchor_positive_control as legacy


class ControlFixture:
    """Reuse the existing real-author fixture with a report-only preflight runner."""
    def __init__(self, owner, *, offset="0.020", uncertainty="0.001"):
        self.case = legacy.PositiveControlTests()
        self.case.setUp()
        owner.addCleanup(self.case.doCleanups)
        self.offset, self.uncertainty = offset, uncertainty
        self.argv = []
        self.preflight_exit = 0
        self.preflight_stderr = b"fixture diagnostic\n"
        # The historical real-author fixture predates the authenticated sizing
        # binding. Its plan/dispatch seam is independent of this anchor test.
        (self.case.inputs / "kernel-frequency-binding.json").write_bytes(
            readiness.render_json({"fixture": "sizing supplied by injected replay"}))

    def runner(self, argv, *, timeout):
        self.argv.append(tuple(argv))
        if tuple(argv) != g10.preflight_argv(self.case.repository):
            with mock.patch.object(q, "authenticated_clock_budget", return_value=(320., ())):
                return self.case.runner(argv, timeout=timeout)
        raw = itertools.count(self.case.base_ns + self.case.elapsed_ns + self.case.sequence * 1000 + 1)
        def clock(clock_id):
            return next(raw) + (legacy.SYNTHETIC_REALTIME_OFFSET_NS if clock_id == time.CLOCK_REALTIME else 0)
        def sntp(command):
            offset = self.offset if self.offset.startswith(("+", "-")) else "+" + self.offset
            text = (f"{offset} +/- {self.uncertainty} "
                    f"{command[-1]} 192.0.2.1\n")
            return subprocess.CompletedProcess(command, 0, text.encode(), b"")
        stream = io.BytesIO()
        collect_clock_reference.main([], runner=sntp, clock_gettime_ns=clock,
            boot_session_id_reader=lambda: legacy.TEST_BOOT_SESSION_ID, stdout=stream)
        return subprocess.CompletedProcess(argv, self.preflight_exit, stream.getvalue(), self.preflight_stderr)

    def run(self):
        with mock.patch.object(g10, "REPO_ROOT", self.case.repository), redirect_stdout(io.StringIO()):
            return g10.run_control(pack_root=self.case.pack, author_inputs=self.case.inputs,
                custody_root=self.case.control, resync_timeout_s=30, sample=self.case.sample,
                runner=self.runner, monotonic_ns=self.case.monotonic_ns, sleep=self.case.sleep)

    def verify(self, **bounds):
        head = subprocess.check_output(["git", "-C", str(self.case.repository), "rev-parse", "HEAD"], text=True).strip()
        options = {"before_monotonic_ns": self.case.base_ns + self.case.elapsed_ns + 10**9,
                   "after_monotonic_ns": self.case.base_ns - 1, "boot_id": legacy.TEST_BOOT_SESSION_ID}
        options.update(bounds)
        return g10.verify_g10_custody(self.case.control / "positive-control.json",
            self.case.control / "custody-manifest.json", code_root=self.case.repository, head=head, **options)

    def reseal(self):
        root = self.case.control
        hashes = {p.relative_to(root).as_posix(): readiness.sha256_bytes(p.read_bytes())
                  for p in sorted(root.rglob("*")) if p.is_file() and p.name != "custody-manifest.json"}
        (root / "custody-manifest.json").write_bytes(readiness.render_json({"files": hashes}))


class OffsetPreflightTests(unittest.TestCase):
    def test_19ms_is_non_spending_without_on_or_author_inputs(self):
        fixture = ControlFixture(self, offset="0.019")
        self.assertEqual(fixture.run(), {"status": "g10_preflight_offset_too_small", "g10_attempt": False})
        self.assertNotIn(g10.ON_ARGV, fixture.argv)
        self.assertNotIn(network_time_off.OFF_ARGV, fixture.argv)
        self.assertFalse((fixture.case.control / "author-custody").exists())
        self.assertEqual(fixture.case.author_calls, [])
        self.assertEqual(g10.read_json(fixture.case.control / "outcome.json")["g10_attempt"], False)
        self.assertIn("commands/preflight/stderr.txt", g10.read_json(fixture.case.control / "custody-manifest.json")["files"])

    def test_bound_410ms_and_beyond_author_limit_are_non_spending(self):
        for offset, uncertainty, bound in (("0.020", "0.390", "0.410"), ("1.150", "0.001", "1.151")):
            with self.subTest(bound=bound):
                fixture = ControlFixture(self, offset=offset, uncertainty=uncertainty)
                self.assertEqual(fixture.run(), {"status": "g10_preflight_offset_too_large", "g10_attempt": False})
                self.assertEqual(g10.read_json(fixture.case.control / "preflight.json")["bound_s"], bound)
                self.assertNotIn(g10.ON_ARGV, fixture.argv)
                self.assertFalse((fixture.case.control / "author-custody").exists())

    def test_20ms_and_400ms_bound_pass_and_replay(self):
        for offset, uncertainty in (("0.020", "0.001"), ("-0.020", "0.380")):
            with self.subTest(offset=offset):
                fixture = ControlFixture(self, offset=offset, uncertainty=uncertainty)
                self.assertEqual(fixture.run()["status"], "DISCHARGED")
                self.assertEqual(fixture.argv.count(g10.ON_ARGV), 1)
                self.assertEqual(fixture.verify()["performed_by"], "Ed")
                self.assertEqual(fixture.argv[0], g10.preflight_argv(fixture.case.repository))

    def test_nonzero_collector_does_not_copy_inputs_or_execute_on(self):
        fixture = ControlFixture(self)
        fixture.preflight_exit = 7
        result = fixture.run()
        self.assertEqual(result["reason"], "g10_preflight_command_invalid")
        self.assertFalse(result["g10_attempt"])
        self.assertNotIn(g10.ON_ARGV, fixture.argv)
        self.assertFalse((fixture.case.control / "author-custody").exists())


class PreflightSubcommandTests(unittest.TestCase):
    def invoke(self, fixture, *arguments, runner=None, sample=None):
        stream = io.StringIO()
        with mock.patch.object(g10, "REPO_ROOT", fixture.case.repository), \
             mock.patch("builtins.input", side_effect=AssertionError("preflight requested OUTSIDE")), \
             mock.patch.object(g10, "run_control", side_effect=AssertionError("preflight entered run")), \
             redirect_stdout(stream):
            rc = g10.main(["preflight", *arguments], sample=sample or fixture.case.sample,
                          runner=runner or fixture.runner)
        raw = stream.getvalue().encode()
        result = readiness.parse_json_bytes(raw, require_canonical=True)
        self.assertEqual(raw, readiness.render_json(result))
        self.assertEqual(fixture.argv, [g10.preflight_argv(fixture.case.repository)])
        self.assertNotIn(g10.ON_ARGV, fixture.argv)
        self.assertNotIn(network_time_off.OFF_ARGV, fixture.argv)
        self.assertFalse(fixture.case.control.exists())
        self.assertEqual(fixture.case.author_calls, [])
        return rc, result

    def test_bands_and_boundary_exit_codes_without_output_or_setters(self):
        for offset, uncertainty, status, rc in (
                ("0.019", "0.001", "g10_preflight_offset_too_small", 3),
                ("-0.019", "0.001", "g10_preflight_offset_too_small", 3),
                ("0.020", "0.001", "PASS", 0),
                ("-0.020", "0.380", "PASS", 0),
                ("0.020", "0.390", "g10_preflight_offset_too_large", 4),
                ("1.150", "0.001", "g10_preflight_offset_too_large", 4)):
            with self.subTest(offset=offset, uncertainty=uncertainty):
                fixture = ControlFixture(self, offset=offset, uncertainty=uncertainty)
                before = set(fixture.case.repository.parent.rglob("*"))
                code, result = self.invoke(fixture)
                self.assertEqual(code, rc)
                self.assertEqual(result, {"status": status, "midpoint_s": offset,
                    "bound_s": str(abs(g10.Decimal(offset)) + g10.Decimal(uncertainty)),
                    "exit_code": 0, "boot_id": legacy.TEST_BOOT_SESSION_ID})
                self.assertEqual(set(fixture.case.repository.parent.rglob("*")), before)

    def test_nonzero_collector_retains_raw_error_record(self):
        fixture = ControlFixture(self)
        fixture.preflight_exit = 7
        output = fixture.case.repository.parent / "offset.json"
        rc, result = self.invoke(fixture, "--output", str(output))
        self.assertEqual(rc, 2)
        self.assertEqual(result["status"], "ERROR")
        self.assertEqual(result["exit_code"], 7)
        self.assertEqual(result["reason"], "g10_preflight_command_invalid")
        record = g10.read_json(output)
        self.assertEqual(record["measurement"], result)
        self.assertEqual(record["command"]["stderr"], fixture.preflight_stderr.decode())
        self.assertEqual(record["command"]["exit_code"], 7)

    def test_malformed_collector_and_timeout_exit_two_without_setters(self):
        for defect in ("json", "timeout"):
            with self.subTest(defect=defect):
                fixture = ControlFixture(self)
                def runner(argv, *, timeout):
                    if defect == "timeout":
                        fixture.argv.append(tuple(argv))
                        raise subprocess.TimeoutExpired(argv, timeout)
                    completed = fixture.runner(argv, timeout=timeout)
                    completed.stdout = b"not JSON\n"
                    return completed
                rc, result = self.invoke(fixture, runner=runner)
                self.assertEqual(rc, 2)
                self.assertEqual(result["status"], "ERROR")

    def test_boot_change_is_error_without_setters(self):
        fixture = ControlFixture(self)
        def sample():
            value = fixture.case.sample()
            if fixture.argv:
                value["boot_id"] = "00000000-0000-0000-0000-000000000001"
            return value
        rc, result = self.invoke(fixture, sample=sample)
        self.assertEqual(rc, 2)
        self.assertEqual(result["reason"], "g10_preflight_boot_or_order")

    def test_unserializable_raw_record_exits_two_without_creating_output(self):
        fixture = ControlFixture(self)
        fixture.preflight_stderr = b"\xff"
        output = fixture.case.repository.parent / "offset.json"
        rc, result = self.invoke(fixture, "--output", str(output))
        self.assertEqual(rc, 2)
        self.assertEqual(result["status"], "ERROR")
        self.assertEqual(result["reason"], "g10_preflight_output_refused")
        self.assertFalse(output.exists())

    def test_output_is_full_raw_record_and_create_once(self):
        for offset, expected in (("0.020", 0), ("0.019", 3), ("1.150", 4)):
            with self.subTest(offset=offset):
                fixture = ControlFixture(self, offset=offset)
                output = fixture.case.repository.parent / "offset.json"
                rc, result = self.invoke(fixture, "--output", str(output))
                self.assertEqual(rc, expected)
                record = g10.read_json(output)
                self.assertEqual(set(record), {"command", "measurement"})
                self.assertEqual(record["measurement"], result)
                command = record["command"]
                self.assertEqual(command["argv"], list(fixture.argv[0]))
                self.assertEqual(command["stderr"], fixture.preflight_stderr.decode())
                self.assertEqual(command["started"]["boot_id"], result["boot_id"])
                self.assertEqual(g10.preflight_measurement(command, result["boot_id"],
                    repository=fixture.case.repository), {key: result[key] for key in
                    ("midpoint_s", "bound_s", "status")})
                original = output.read_bytes()
                fixture.argv.clear()
                rc, result = self.invoke(fixture, "--output", str(output))
                self.assertEqual(rc, 2)
                self.assertEqual(result["reason"], "g10_preflight_output_refused")
                self.assertEqual(output.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
