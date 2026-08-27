from __future__ import annotations

import ast
import inspect
import io
import json
import subprocess
import time
import unittest
from contextlib import redirect_stderr
from decimal import Decimal
from unittest import mock

from joulewise import arm_readiness as readiness
from joulewise import clock_reference
from scripts import collect_clock_reference as cli


BOOT_SESSION_ID = "11111111-2222-3333-4444-555555555555"
GOLDEN_LINE = "+0.027688 +/- 0.017541 time.apple.com 17.253.4.45"
TOP_LEVEL_KEYS = {
    "schema_version",
    "sample_policy_id",
    "boot_session_id",
    "anchor_realtime_ns",
    "anchor_monotonic_raw_ns",
    "anchor_read_skew_ns",
    "batch_started_monotonic_raw_ns",
    "batch_finished_monotonic_raw_ns",
    "samples",
}
SAMPLE_KEYS = {
    "server",
    "argv",
    "exit_code",
    "started_monotonic_raw_ns",
    "finished_monotonic_raw_ns",
    "stdout",
    "stderr",
    "parsed",
    "offset_s",
    "uncertainty_s",
    "peer_address",
    "raw_line",
}


class SequenceClock:
    def __init__(self, values: list[int]) -> None:
        self._values = iter(values)
        self.clock_ids: list[int] = []

    def __call__(self, clock_id: int) -> int:
        self.clock_ids.append(clock_id)
        return next(self._values)


class FakeRunner:
    def __init__(self) -> None:
        self.argvs: list[list[str]] = []

    def __call__(self, argv: object) -> subprocess.CompletedProcess[bytes]:
        exact_argv = list(argv)  # type: ignore[arg-type]
        self.argvs.append(exact_argv)
        server = exact_argv[-1]
        line = f"+0.010000 +/- 0.020000 {server} 192.0.2.10\n"
        return subprocess.CompletedProcess(exact_argv, 0, line.encode(), b"")


def builder_clock() -> SequenceClock:
    # Anchor's three reads, batch start, three start/finish pairs, batch finish.
    return SequenceClock([100, 1_000, 104, 105, 106, 107, 108, 109, 110, 111, 112])


class ClockReferenceTests(unittest.TestCase):
    maxDiff = None

    def test_argv_roster_and_one_invocation_per_host_are_exact(self) -> None:
        runner = FakeRunner()
        result = clock_reference.build_clock_reference(
            boot_session_id=BOOT_SESSION_ID,
            runner=runner,
            clock_gettime_ns=builder_clock(),
        )

        expected = [
            ["/usr/bin/sntp", "-t", "2", "time.apple.com"],
            ["/usr/bin/sntp", "-t", "2", "pool.ntp.org"],
            ["/usr/bin/sntp", "-t", "2", "time.nist.gov"],
        ]
        self.assertEqual(runner.argvs, expected)
        samples = result["samples"]
        self.assertEqual(len(samples), 3)  # type: ignore[arg-type]
        self.assertEqual(
            [sample["argv"] for sample in samples], expected  # type: ignore[union-attr]
        )
        self.assertEqual(
            [sample["server"] for sample in samples],  # type: ignore[union-attr]
            list(clock_reference.SERVER_ROSTER),
        )
        for argv in runner.argvs:
            self.assertTrue({"-s", "-S", "-a"}.isdisjoint(argv))

    def test_report_only_assertion_rejects_every_clock_setting_flag(self) -> None:
        for flag in ("-s", "-S", "-a"):
            with self.subTest(flag=flag), self.assertRaises(ValueError):
                clock_reference.assert_report_only_argv(
                    ["/usr/bin/sntp", flag, "time.apple.com"]
                )

    def test_golden_measured_line_parses_exactly(self) -> None:
        parsed = clock_reference.parse_sntp_stdout(
            GOLDEN_LINE + "\n", server="time.apple.com"
        )
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.offset_s, Decimal("+0.027688"))
        self.assertEqual(parsed.uncertainty_s, Decimal("0.017541"))
        self.assertEqual(parsed.peer_address, "17.253.4.45")
        self.assertEqual(parsed.raw_line, GOLDEN_LINE)

    def test_parser_rejects_negative_uncertainty(self) -> None:
        self.assertIsNone(
            clock_reference.parse_sntp_stdout(
                "+0.027688 +/- -0.017541 time.apple.com 17.253.4.45",
                server="time.apple.com",
            )
        )

    def test_parser_rejects_nan_spelling(self) -> None:
        for spelling in ("nan", "NaN", "NAN"):
            with self.subTest(spelling=spelling):
                self.assertIsNone(
                    clock_reference.parse_sntp_stdout(
                        f"+{spelling} +/- 0.017541 time.apple.com 17.253.4.45",
                        server="time.apple.com",
                    )
                )

    def test_parser_rejects_infinity_spelling(self) -> None:
        for spelling in ("inf", "Inf", "Infinity"):
            with self.subTest(spelling=spelling):
                self.assertIsNone(
                    clock_reference.parse_sntp_stdout(
                        f"+0.027688 +/- {spelling} time.apple.com 17.253.4.45",
                        server="time.apple.com",
                    )
                )

    def test_parser_rejects_trailing_junk(self) -> None:
        self.assertIsNone(
            clock_reference.parse_sntp_stdout(
                GOLDEN_LINE + " trailing", server="time.apple.com"
            )
        )

    def test_parser_rejects_hostname_other_than_invoked_host(self) -> None:
        self.assertIsNone(
            clock_reference.parse_sntp_stdout(
                "+0.027688 +/- 0.017541 time.nist.gov 17.253.4.45",
                server="time.apple.com",
            )
        )

    def test_parser_rejects_missing_address(self) -> None:
        self.assertIsNone(
            clock_reference.parse_sntp_stdout(
                "+0.027688 +/- 0.017541 time.apple.com",
                server="time.apple.com",
            )
        )

    def test_parser_rejects_malformed_address(self) -> None:
        self.assertIsNone(
            clock_reference.parse_sntp_stdout(
                "+0.027688 +/- 0.017541 time.apple.com 999.1.2.3",
                server="time.apple.com",
            )
        )

    def test_parser_rejects_empty_stdout(self) -> None:
        self.assertIsNone(
            clock_reference.parse_sntp_stdout("\n \n", server="time.apple.com")
        )

    def test_parser_uses_last_nonempty_line_when_it_is_good(self) -> None:
        parsed = clock_reference.parse_sntp_stdout(
            "diagnostic\n\n" + GOLDEN_LINE + "\n", server="time.apple.com"
        )
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.raw_line, GOLDEN_LINE)

    def test_parser_rejects_when_last_nonempty_line_is_junk(self) -> None:
        self.assertIsNone(
            clock_reference.parse_sntp_stdout(
                GOLDEN_LINE + "\n\nClock select failed\n", server="time.apple.com"
            )
        )

    def test_parser_accepts_ipv6_peer_address(self) -> None:
        line = "+0.027688 +/- 0.017541 time.apple.com 2001:db8::1"
        parsed = clock_reference.parse_sntp_stdout(line, server="time.apple.com")
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.peer_address, "2001:db8::1")

    def test_exit_69_leg_is_retained_verbatim_in_roster_position(self) -> None:
        timeout_stdout = "sntp_exchange {\n  result = timeout\n}\n"
        timeout_stderr = (
            "Exchange failed: Timeout\n" * 5 + "Clock select failed\n"
        )

        def runner(argv: object) -> subprocess.CompletedProcess[bytes]:
            exact = list(argv)  # type: ignore[arg-type]
            if exact[-1] == "pool.ntp.org":
                return subprocess.CompletedProcess(
                    exact, 69, timeout_stdout.encode(), timeout_stderr.encode()
                )
            line = f"+0.010000 +/- 0.020000 {exact[-1]} 192.0.2.10\n"
            return subprocess.CompletedProcess(exact, 0, line.encode(), b"")

        result = clock_reference.build_clock_reference(
            boot_session_id=BOOT_SESSION_ID,
            runner=runner,
            clock_gettime_ns=builder_clock(),
        )
        samples = result["samples"]
        failed = samples[1]  # type: ignore[index]
        self.assertEqual(failed["server"], "pool.ntp.org")
        self.assertEqual(failed["exit_code"], 69)
        self.assertFalse(failed["parsed"])
        self.assertEqual(failed["stdout"], timeout_stdout)
        self.assertEqual(failed["stderr"], timeout_stderr)
        self.assertIsNone(failed["offset_s"])
        self.assertEqual(len(samples), 3)  # type: ignore[arg-type]

    def test_nonzero_exit_never_parses_even_with_a_matching_line(self) -> None:
        def runner(argv: object) -> subprocess.CompletedProcess[bytes]:
            exact = list(argv)  # type: ignore[arg-type]
            line = f"+0.010000 +/- 0.020000 {exact[-1]} 192.0.2.10\n"
            return subprocess.CompletedProcess(exact, 69, line.encode(), b"")

        result = clock_reference.build_clock_reference(
            boot_session_id=BOOT_SESSION_ID,
            runner=runner,
            clock_gettime_ns=builder_clock(),
        )
        for sample in result["samples"]:  # type: ignore[union-attr]
            self.assertFalse(sample["parsed"])
            self.assertIsNone(sample["offset_s"])
            self.assertIsNone(sample["uncertainty_s"])
            self.assertIsNone(sample["peer_address"])
            self.assertIsNone(sample["raw_line"])

    def test_outputs_decode_invalid_utf8_with_replacement(self) -> None:
        def runner(argv: object) -> subprocess.CompletedProcess[bytes]:
            exact = list(argv)  # type: ignore[arg-type]
            return subprocess.CompletedProcess(exact, 69, b"out\xff", b"err\xfe")

        result = clock_reference.build_clock_reference(
            boot_session_id=BOOT_SESSION_ID,
            runner=runner,
            clock_gettime_ns=builder_clock(),
        )
        sample = result["samples"][0]  # type: ignore[index]
        self.assertEqual(sample["stdout"], "out\ufffd")
        self.assertEqual(sample["stderr"], "err\ufffd")

    def test_anchor_midpoint_skew_and_read_order_are_exact(self) -> None:
        clock = SequenceClock([100, 1_000, 116])
        anchor = clock_reference.sample_anchor(clock)
        self.assertEqual(anchor.realtime_ns, 1_000)
        self.assertEqual(anchor.monotonic_raw_ns, 108)
        self.assertEqual(anchor.read_skew_ns, 16)
        self.assertEqual(
            clock.clock_ids,
            [time.CLOCK_MONOTONIC_RAW, time.CLOCK_REALTIME, time.CLOCK_MONOTONIC_RAW],
        )

    def test_anchor_requests_monotonic_raw_never_uptime_raw(self) -> None:
        clock = SequenceClock([10, 20, 30])
        clock_reference.sample_anchor(clock)
        self.assertEqual(clock.clock_ids[0], time.CLOCK_MONOTONIC_RAW)
        self.assertEqual(clock.clock_ids[2], time.CLOCK_MONOTONIC_RAW)
        if hasattr(time, "CLOCK_UPTIME_RAW"):
            self.assertNotIn(time.CLOCK_UPTIME_RAW, clock.clock_ids)

    def test_builder_uses_monotonic_raw_for_every_batch_and_leg_timestamp(self) -> None:
        clock = builder_clock()
        clock_reference.build_clock_reference(
            boot_session_id=BOOT_SESSION_ID,
            runner=FakeRunner(),
            clock_gettime_ns=clock,
        )
        self.assertEqual(
            clock.clock_ids,
            [
                time.CLOCK_MONOTONIC_RAW,
                time.CLOCK_REALTIME,
                time.CLOCK_MONOTONIC_RAW,
                *([time.CLOCK_MONOTONIC_RAW] * 8),
            ],
        )

    def test_cli_subprocess_is_governed_shell_free_and_noninteractive(self) -> None:
        completed = subprocess.CompletedProcess([], 0, b"", b"")
        argv = ["/usr/bin/sntp", "-t", "2", "time.apple.com"]
        with mock.patch.object(cli.subprocess, "run", return_value=completed) as run:
            observed = cli._run_sntp(argv)
        self.assertIs(observed, completed)
        run.assert_called_once_with(
            argv,
            cwd=cli.REPO_ROOT,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            env=cli.GOVERNED_SUBPROCESS_ENVIRONMENT,
            shell=False,
        )

    def test_cli_defaults_to_the_existing_boot_session_reader(self) -> None:
        default = inspect.signature(cli.main).parameters[
            "boot_session_id_reader"
        ].default
        self.assertIs(default, readiness._current_boot_session_id)

    def test_cli_rejects_runtime_roster_or_timeout_substitution(self) -> None:
        for argv in (
            ["--server", "example.net"],
            ["--timeout", "5"],
        ):
            with (
                self.subTest(argv=argv),
                redirect_stderr(io.StringIO()),
                self.assertRaises(SystemExit),
            ):
                cli.main(
                    argv,
                    runner=FakeRunner(),
                    clock_gettime_ns=builder_clock(),
                    boot_session_id_reader=lambda: BOOT_SESSION_ID,
                    stdout=io.BytesIO(),
                )

    def test_cli_emits_exact_canonical_contract(self) -> None:
        output = io.BytesIO()
        status = cli.main(
            [],
            runner=FakeRunner(),
            clock_gettime_ns=builder_clock(),
            boot_session_id_reader=lambda: BOOT_SESSION_ID,
            stdout=output,
        )
        raw = output.getvalue()
        parsed = json.loads(raw)

        self.assertEqual(status, 0)
        self.assertEqual(set(parsed), TOP_LEVEL_KEYS)
        self.assertEqual(parsed["schema_version"], clock_reference.SCHEMA_VERSION)
        self.assertEqual(parsed["sample_policy_id"], clock_reference.SAMPLE_POLICY_ID)
        self.assertEqual(parsed["boot_session_id"], BOOT_SESSION_ID)
        self.assertEqual(len(parsed["samples"]), 3)
        for sample in parsed["samples"]:
            self.assertEqual(set(sample), SAMPLE_KEYS)
        self.assertEqual(raw, readiness.render_json(parsed))

    def test_module_contains_no_policy_comparison_or_algorithm(self) -> None:
        # Policy absence is a source property, not a runtime branch to exercise:
        # AST inspection catches a future threshold literal or named policy
        # algorithm even when fixtures happen not to drive that path.
        tree = ast.parse(inspect.getsource(clock_reference))
        numeric_literals = {
            node.value
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant)
            and isinstance(node.value, (int, float))
            and not isinstance(node.value, bool)
        }
        self.assertNotIn(0.5, numeric_literals)
        self.assertNotIn(5_000_000, numeric_literals)
        executable_names = {
            node.id.lower()
            for node in ast.walk(tree)
            if isinstance(node, ast.Name)
        } | {
            node.attr.lower()
            for node in ast.walk(tree)
            if isinstance(node, ast.Attribute)
        }
        for forbidden in ("quorum", "intersection"):
            self.assertFalse(
                any(forbidden in name for name in executable_names),
                f"collector unexpectedly contains {forbidden} policy",
            )

    def test_identical_injected_inputs_emit_byte_identically(self) -> None:
        emitted: list[bytes] = []
        for _ in range(2):
            output = io.BytesIO()
            cli.main(
                [],
                runner=FakeRunner(),
                clock_gettime_ns=builder_clock(),
                boot_session_id_reader=lambda: BOOT_SESSION_ID,
                stdout=output,
            )
            emitted.append(output.getvalue())
        self.assertEqual(emitted[0], emitted[1])


if __name__ == "__main__":
    unittest.main()
