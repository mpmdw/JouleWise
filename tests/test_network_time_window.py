"""Injected OS boundary checks for the ruled H5/H6 window records."""

import hashlib
import io
import json
import subprocess
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from contextlib import redirect_stdout

from joulewise import network_time_window as nt


def line(epoch, category="data", body="ordinary"):
    stamp = datetime.fromtimestamp(epoch, timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f+0000")
    return f"{stamp} timed[11] [com.apple.timed:{category}] {body}\n"


class Runner:
    def __init__(self, log=""):
        self.log = log
        self.calls = []
        self.off_output = b"setUsingNetworkTime: Off\n"
        self.on_code = 0

    def __call__(self, argv, timeout):
        self.calls.append(tuple(argv))
        if tuple(argv) == nt.BOOT_ARGV:
            return subprocess.CompletedProcess(argv, 0, b"boot-1\n", b"")
        if tuple(argv) == nt.OFF_ARGV:
            return subprocess.CompletedProcess(argv, 0, self.off_output, b"")
        if tuple(argv) == nt.ON_ARGV:
            return subprocess.CompletedProcess(argv, self.on_code, b"ON output\n", b"")
        if tuple(argv[:len(nt.LOG_PREFIX)]) == nt.LOG_PREFIX:
            return subprocess.CompletedProcess(argv, 0, self.log.encode(), b"")
        raise AssertionError(argv)


class WindowTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.marker = self.root / "pending.json"
        self.runner = Runner()
        nt.set_network_time_off(self.root, "plan", runner=self.runner,
            boot_probe=lambda: "boot-1", clock=lambda: {"epoch_s": 10000, "monotonic_s": 10000},
            marker_path=self.marker)
        self.window = self.root / "night/network_time"
        self.first = {"epoch_s": 10600, "monotonic_before_s": 10600}
        self.last = {"epoch_s": 10610, "monotonic_before_s": 10610}

    def query(self, lines):
        self.runner.log = nt.HEADER + "   \n" + lines
        return nt.run_window_query(self.root / "night", runner=self.runner,
            boot_probe=lambda: "boot-1", clock=lambda: {"epoch_s": 10620, "monotonic_s": 10620})

    def verdict(self):
        return nt.capture_verdict(self.window, self.first, self.last)[0]

    def test_header_only_old_log_is_unattested_with_injected_runner(self):
        # A real old-log bench query is lead-owned; this injected runner gives
        # the exact header-only shape without querying this machine's log.
        self.query("")
        self.assertEqual(self.verdict(), "network_time_unattested")

    def test_lines_only_inside_capture_cannot_witness(self):
        self.query(line(10605))
        self.assertEqual(self.verdict(), "network_time_unattested")

    def test_line_100_seconds_before_first_cannot_witness(self):
        self.query(line(10500))
        self.assertEqual(self.verdict(), "network_time_unattested")

    def test_text_category_cannot_witness(self):
        self.query(line(9900, "text"))
        self.assertEqual(self.verdict(), "network_time_unattested")

    def test_marker_179_seconds_before_first_excludes(self):
        self.query(line(9900) + line(10421, body="ntp_adjtime"))
        self.assertEqual(self.verdict(), "network_time_slew_attested")

    def test_marker_181_seconds_before_first_is_clean(self):
        self.query(line(9900) + line(10419, body="ntp_adjtime"))
        self.assertEqual(self.verdict(), "clean")

    def test_old_log_query_shape_is_header_only_and_unattested(self):
        self.query("")
        self.assertEqual(self.runner.calls[-1][:len(nt.LOG_PREFIX)], nt.LOG_PREFIX)
        self.assertEqual(self.verdict(), "network_time_unattested")

    def test_amended_witness_must_predate_off(self):
        self.query(line(10300))  # 300 s before first; after OFF.
        self.assertEqual(self.verdict(), "network_time_unattested")

    def test_query_start_must_precede_off_by_3600(self):
        record = self.query(line(9900))
        path = self.window / "h6-window-1.json"
        record["start_arg"] = nt._format_epoch(7000)
        record["start_epoch_s"] = 7000
        record["argv"][-3] = record["start_arg"]
        path.write_text(json.dumps(record))
        self.assertEqual(self.verdict(), "network_time_unattested")

    def test_early_query_cannot_cover_capture(self):
        self.runner.log = nt.HEADER + "\n" + line(9900)
        nt.run_window_query(self.root / "night", runner=self.runner,
            boot_probe=lambda: "boot-1", clock=lambda: {"epoch_s": 10610.5, "monotonic_s": 10610.5})
        self.assertEqual(self.verdict(), "network_time_unattested")

    def test_continuation_marker_takes_parent_time(self):
        self.query(line(9900) + line(10421, body="first line") + "  ntp_adjtime continuation\n")
        self.assertEqual(self.verdict(), "network_time_slew_attested")

    def test_unplaced_continuation_refuses_clean(self):
        self.query("  orphan\n" + line(9900))
        self.assertEqual(self.verdict(), "network_time_unattested")

    def test_utc_offset_is_kept_across_fall_back(self):
        self.query(line(9900) + "1970-01-01 01:53:41.000000-0100 timed[11] [com.apple.timed:data] ntp_adjtime\n")
        # 01:53:41-0100 is epoch 10421, not 6821.
        self.assertEqual(self.verdict(), "network_time_slew_attested")

    def test_marker_in_authentic_invalid_run_precedes_clean_valid_run(self):
        self.query(line(9900) + line(10421, body="settimeofday"))
        first = self.window / "h6-window-1.json"
        record = json.loads(first.read_text())
        record["exit_code"] = 1
        first.write_text(json.dumps(record))
        self.query(line(9900))
        self.assertEqual(self.verdict(), "network_time_slew_attested")

    def test_marker_on_first_line_of_bad_header_still_excludes(self):
        self.query(line(9900) + line(10421, body="cmd,apply,src,"))
        raw = self.window / "h6-query-1.txt"
        raw.write_text(line(10421, body="cmd,apply,src,") + line(9900))
        record_path = self.window / "h6-window-1.json"
        record = json.loads(record_path.read_text())
        record["raw_sha256"] = hashlib.sha256(raw.read_bytes()).hexdigest()
        record_path.write_text(json.dumps(record))
        self.assertEqual(self.verdict(), "network_time_slew_attested")

    def test_damaged_raw_and_off_digest_refuse(self):
        self.query(line(9900))
        (self.window / "h6-query-1.txt").write_text(nt.HEADER + "\n")
        self.assertEqual(self.verdict(), "network_time_unattested")
        (self.window / "h5-off.json").write_text("{}")
        self.assertEqual(self.verdict(), "network_time_unattested")

    def test_off_exact_output_and_two_clock_lead(self):
        self.query(line(9900))
        self.assertEqual(self.verdict(), "clean")
        self.first["monotonic_before_s"] = 10599
        self.assertEqual(self.verdict(), "network_time_unattested")
        self.first["monotonic_before_s"] = 10600
        off = self.window / "h5-off.json"
        record = json.loads(off.read_text())
        record["stdout"] = "setUsingNetworkTime: Off\nextra"
        off.write_text(json.dumps(record))
        self.assertEqual(self.verdict(), "network_time_unattested")

    def test_recovery_restores_only_after_chain_proof(self):
        started = self.root / "night/chain.started"
        started.write_text(json.dumps({"pgid": 123}))
        self.assertEqual(nt.recover_network_time(marker_path=self.marker, runner=self.runner,
            boot_probe=lambda: "boot-1", process_group_absent=lambda pgid: False), "chain_unproved")
        self.assertNotIn(nt.ON_ARGV, self.runner.calls)
        self.assertEqual(nt.recover_network_time(marker_path=self.marker, runner=self.runner,
            boot_probe=lambda: "boot-1", process_group_absent=lambda pgid: True), "restored")
        self.assertFalse(self.marker.exists())
        self.assertTrue((self.window / "h5-on.json").exists())

    def test_recovery_requeries_when_only_prior_run_is_invalid(self):
        self.query("")
        self.runner.log = nt.HEADER + "\n" + line(9900)
        self.assertEqual(nt.recover_network_time(marker_path=self.marker, runner=self.runner,
            boot_probe=lambda: "boot-1", clock=lambda: {"epoch_s": 10630, "monotonic_s": 10630}),
            "restored")
        self.assertTrue((self.window / "h6-window-2.json").exists())
        self.assertEqual(self.verdict(), "clean")

    def test_closed_historic_exemptions_and_unknown_required(self):
        self.assertFalse(nt.attestation_required("25F84", "other"))
        self.assertFalse(nt.attestation_required("25G83", "d079-epoch-25g83-derivation-w1-20260927"))
        self.assertTrue(nt.attestation_required("25G83", "future"))
        self.assertTrue(nt.attestation_required(None, "future"))

    def test_failed_on_is_saved_and_recovery_retries_in_new_file(self):
        self.runner.on_code = 1
        first = nt.set_network_time_on(self.root, "plan", runner=self.runner,
            boot_probe=lambda: "boot-1", marker_path=self.marker)
        self.assertEqual(first["exit_code"], 1)
        self.assertTrue(self.marker.exists())
        self.runner.on_code = 0
        self.assertEqual(nt.recover_network_time(marker_path=self.marker, runner=self.runner,
            boot_probe=lambda: "boot-1"), "restored")
        self.assertFalse(self.marker.exists())
        self.assertEqual(json.loads((self.window / "h5-on.json").read_text())["exit_code"], 1)
        self.assertEqual(json.loads((self.window / "h5-on-recovery-1.json").read_text())["exit_code"], 0)

    def test_failed_recovery_receipt_clears_marker_for_fresh_off(self):
        self.runner.on_code = 1
        nt.set_network_time_on(self.root, "plan", runner=self.runner,
            boot_probe=lambda: "boot-1", marker_path=self.marker)
        self.assertEqual(nt.recover_network_time(marker_path=self.marker, runner=self.runner,
            boot_probe=lambda: "boot-1"), "restore_failed")
        self.assertFalse(self.marker.exists())
        self.assertEqual(json.loads((self.window / "h5-on-recovery-1.json").read_text())["exit_code"], 1)

    def test_report_h6_prints_verdict_without_b_and_h7_prints_rate(self):
        self.query(line(9900))
        capture = self.root / "capture.json"
        capture.write_text(json.dumps({"clock_anchor": {"clock_stamps": {
            "pre_spawn": self.first, "post_parse": self.last}}, "B": "forbidden"}))
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(nt.main(["report", "--h6", "--window-dir", str(self.window),
                                     "--capture", str(capture)]), 0)
        row = json.loads(output.getvalue())
        self.assertEqual(row["verdict"], "clean")
        self.assertFalse(row["flagged"])
        self.assertNotIn("B", output.getvalue())
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(nt.main(["report", "--h7", "--window-dir", str(self.window),
                                     "--capture", str(capture)]), 0)
        row = json.loads(output.getvalue())
        self.assertEqual(row["state"], "off")
        self.assertEqual(row["h5_off_sha256"], hashlib.sha256((self.window / "h5-off.json").read_bytes()).hexdigest())
        self.assertEqual(row["standing_rate_ppm"], 0)
        self.assertEqual(row["drift_term_s"], 0)


if __name__ == "__main__":
    unittest.main()
