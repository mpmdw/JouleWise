"""Injected OS boundary checks for the ruled H5/H6 window records."""

import hashlib
import gzip
import io
import json
import subprocess
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from contextlib import redirect_stdout
from unittest import mock

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
        (self.root / "night/chain.started").write_text(json.dumps({
            "pid": None, "pgid": None, "launch_error": "fixture Popen failed"}))
        (self.root / "night/chain.exited").write_text(json.dumps({"launch_failed": True}))
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

    def test_unindented_continuation_marker_takes_parent_time(self):
        # Counterfactual: timed emits a marker on an unindented continuation.
        # Production call: capture_verdict -> _placed_lines over saved H6 bytes.
        self.query(line(9900) + line(10421, body="first line") + "ntp_adjtime continuation\n")
        self.query(line(9900))  # A later clean run cannot erase the marker.
        self.assertEqual(self.verdict(), "network_time_slew_attested")

    def test_preserved_real_log_unindented_braces_are_placed(self):
        # The archived 2026-09-27 timed output has five column-zero closing
        # braces. Read its real bytes; never ask the current system log.
        archive = (Path(__file__).resolve().parents[1] /
            "docs/process_traces/2026-09-27-activation-d528efb2/40-sci-a2-network-time/evidence/"
            "timed-full-20260926T0000-20260927T1840-PDT.syslog.txt.gz")
        raw = gzip.decompress(archive.read_bytes())
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
            "2f9bf739fde57accdce86e27a9494303585c976132e5dc5063a2cd31a5880b5c")
        self.assertEqual(sum(line == b"}" for line in raw.splitlines()), 5)
        placed, header, parsed = nt._placed_lines(raw)
        self.assertTrue(header)
        self.assertTrue(parsed)
        self.assertGreater(len(placed), 5)

        bench = Path("/tmp/cg-ntpd-d528efb2/q2_utc.txt")
        if bench.is_file():
            # Optional preserved second real query from the ruling bench.
            second = bench.read_bytes()
            _, second_header, second_parsed = nt._placed_lines(second)
            self.assertTrue(second_header)
            self.assertTrue(second_parsed)

    def test_timestamp_like_invalid_continuation_refuses(self):
        self.query(line(9900) + "1970-99-99 00:00:00.000000+0000 timed[11] bogus\n")
        self.assertEqual(self.verdict(), "network_time_unattested")

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

    def test_non_object_off_receipt_is_unattested(self):
        # Counterfactual: h5-off.json decodes to a list; production call is
        # capture_verdict, which must return a verdict rather than raise.
        self.query(line(9900))
        (self.window / "h5-off.json").write_text("[]")
        try:
            verdict = self.verdict()
        except Exception as error:
            self.fail(f"capture_verdict raised on non-object OFF receipt: {error}")
        self.assertEqual(verdict, "network_time_unattested")

    def test_invalid_off_json_does_not_hide_authenticated_marker(self):
        self.query(line(10421, body="ntp_adjtime"))
        off = self.window / "h5-off.json"
        off.write_text("{")
        record = self.window / "h6-window-1.json"
        value = json.loads(record.read_text())
        value["off_sha256"] = hashlib.sha256(off.read_bytes()).hexdigest()
        record.write_text(json.dumps(value))
        self.assertEqual(self.verdict(), "network_time_slew_attested")

    def test_orphaned_raw_query_file_does_not_block_retry(self):
        # Counterfactual: crash after h6-query-1.txt exclusive publication,
        # before h6-window-1.json. Production call: run_window_query.
        (self.window / "h6-query-1.txt").write_bytes(b"orphaned raw bytes\n")
        try:
            self.query(line(9900))
        except FileExistsError as error:
            self.fail(f"run_window_query reused the orphaned raw path: {error}")
        self.assertEqual((self.window / "h6-query-1.txt").read_bytes(), b"orphaned raw bytes\n")
        self.assertTrue((self.window / "h6-window-2.json").exists())
        self.assertEqual(self.verdict(), "clean")

    def test_witness_category_in_payload_is_not_a_category(self):
        self.query(line(9900, "text", "quoted [com.apple.timed:data]"))
        self.assertEqual(self.verdict(), "network_time_unattested")

    def test_witness_category_is_fixed_to_process_field(self):
        # D3: each timestamped text line puts a fake timed/data pair later
        # in the message. The actual category is still text.
        for body in ("quoted timed[11]: [com.apple.timed:data]",
                     "x timed[1] [com.apple.timed:data] y",
                     "a b c timed[2]: [com.apple.timed:data]"):
            with self.subTest(body=body):
                self.query(line(9900, "text", body))
                self.assertEqual(self.verdict(), "network_time_unattested")

    def test_positional_category_matches_preserved_real_log_counts(self):
        archive = (Path(__file__).resolve().parents[1] /
            "docs/process_traces/2026-09-27-activation-d528efb2/40-sci-a2-network-time/evidence/"
            "timed-full-20260926T0000-20260927T1840-PDT.syslog.txt.gz")
        raw = gzip.decompress(archive.read_bytes())
        self.assertEqual(sum(bool(nt._DATA_CATEGORY.match(value)) for value in raw.decode().splitlines()), 2040)
        second = Path("/tmp/cg-ntpd-d528efb2/q2_utc.txt")
        if second.exists():
            self.assertEqual(sum(bool(nt._DATA_CATEGORY.match(value)) for value in second.read_text().splitlines()), 90)

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

    def test_wall_lead_short_when_monotonic_lead_is_sufficient(self):
        self.query(line(9900))
        self.first.update(epoch_s=10599, monotonic_before_s=10600)
        self.assertEqual(nt.capture_verdict(self.window, self.first, self.last),
                         ("network_time_unattested", "off_lead_short"))

    def test_receipt_clock_uses_capture_writer_pair_of_python_clocks(self):
        with mock.patch.object(nt.time, "time", return_value=123.5) as wall, \
             mock.patch.object(nt.time, "monotonic", return_value=456.25) as elapsed:
            self.assertEqual(nt._clock(), {"epoch_s": 123.5, "monotonic_s": 456.25})
        wall.assert_called_once_with()
        elapsed.assert_called_once_with()

    def test_query_boot_mismatch_refuses_clean(self):
        self.query(line(9900))
        path = self.window / "h6-window-1.json"
        record = json.loads(path.read_text())
        record["boot_id"] = "next-boot"
        path.write_text(json.dumps(record))
        self.assertEqual(self.verdict(), "network_time_unattested")

    def test_marker_interval_matches_original_two_clock_union_plus_lead(self):
        from joulewise.quiet_predicate_campaign import attestation_window
        first = {"epoch_s": 1000, "monotonic_before_s": 500}
        last = {"epoch_s": 1570, "monotonic_before_s": 1100}
        original = attestation_window({"sampling_started": first, "sampling_stopped": last})
        *_, lower, upper = nt._interval(first, last)
        self.assertEqual(lower, original[0] - 179)
        self.assertEqual(upper, original[1])

    def test_registered_predecessor_builds_are_exactly_old_builds(self):
        root = Path(__file__).resolve().parents[1] / "configs/calibration"
        registered = {value["identity_epoch"]["os_build"]
                      for path in root.rglob("*.json")
                      if isinstance(value := json.loads(path.read_bytes()), dict)
                      and isinstance(value.get("identity_epoch"), dict)
                      and "os_build" in value["identity_epoch"]}
        self.assertIn("25G83", registered)
        self.assertEqual(nt.OLD_BUILDS, registered - {"25G83"})
        historic_sessions = {path.stem for path in (root / "battery_float_verdicts").glob(
            "d079-epoch-25g83-derivation-w*-20260927.json")}
        self.assertEqual(nt.OLD_SESSIONS, historic_sessions)

    def test_recovery_restores_only_after_chain_proof(self):
        started = self.root / "night/chain.started"
        started.write_text(json.dumps({"pgid": 123}))
        self.assertEqual(nt.recover_network_time(marker_path=self.marker, runner=self.runner,
            boot_probe=lambda: "boot-1", capture_proof=lambda marker, pgid: (False, {"check": "P1"})), "chain_unproved")
        self.assertNotIn(nt.ON_ARGV, self.runner.calls)
        self.assertEqual(nt.recover_network_time(marker_path=self.marker, runner=self.runner,
            boot_probe=lambda: "boot-1", capture_proof=lambda marker, pgid: (True, {})), "restored")
        self.assertFalse(self.marker.exists())
        self.assertTrue((self.window / "h5-on.json").exists())

    def test_known_group_without_injected_capture_proof_refuses(self):
        (self.root / "night/chain.started").write_text(json.dumps({"pgid": 123}))
        self.assertEqual(nt.recover_network_time(marker_path=self.marker, runner=self.runner,
            process_group_absent=lambda pgid: True), "chain_unproved")
        self.assertNotIn(nt.ON_ARGV, self.runner.calls)

    def test_recovery_reproves_before_on_after_query(self):
        (self.root / "night/chain.started").write_text(json.dumps({"pgid": 123}))
        answers = iter(((True, {}), (False, {"check": "P3"})))
        self.assertEqual(nt.recover_network_time(marker_path=self.marker, runner=self.runner,
            capture_proof=lambda marker, pgid: next(answers)), "chain_unproved")
        self.assertNotIn(nt.ON_ARGV, self.runner.calls)
        self.assertTrue(self.marker.exists())

    def test_empty_start_claim_with_exit_record_still_refuses(self):
        (self.root / "night/chain.started").write_text("")
        self.assertEqual(nt.recover_network_time(marker_path=self.marker, runner=self.runner),
                         "chain_unproved")
        self.assertNotIn(nt.ON_ARGV, self.runner.calls)

    def test_empty_start_claim_without_exit_record_still_refuses(self):
        (self.root / "night/chain.started").write_text("")
        (self.root / "night/chain.exited").unlink()
        self.assertEqual(nt.recover_network_time(marker_path=self.marker, runner=self.runner),
                         "chain_unproved")
        self.assertNotIn(nt.ON_ARGV, self.runner.calls)

    def test_restore_marker_has_written_and_resolved_night_paths(self):
        other = self.root / "marker-with-paths.json"
        chain = self.root / "chain.zsh"
        chain.write_text("exit 0\n")
        nt.create_restore_marker(self.root, "path-plan",
            measurement_root=self.root, chain_path=chain, marker_path=other)
        value = json.loads(other.read_text())
        self.assertEqual(value["measurement_root"], str(self.root))
        self.assertEqual(value["measurement_root_resolved"], str(self.root.resolve()))
        self.assertEqual(value["custody_root_written"], str(self.root))
        self.assertEqual(value["custody_root_resolved"], str(self.root.resolve()))
        self.assertEqual(value["chain_path"], str(chain))
        self.assertEqual(value["chain_path_resolved"], str(chain.resolve()))

    def test_exited_child_record_does_not_override_live_group(self):
        # Counterfactual: direct child exits leaving a capture descendant.
        # Production call: recover_network_time at the next driver start.
        (self.root / "night/chain.started").write_text(json.dumps({"pgid": 123}))
        (self.root / "night/chain.exited").write_text(json.dumps({"exit_code": 0}))
        self.assertEqual(nt.recover_network_time(marker_path=self.marker, runner=self.runner,
            process_group_absent=lambda pgid: False), "chain_unproved")
        self.assertNotIn(nt.ON_ARGV, self.runner.calls)
        self.assertTrue(self.marker.exists())

    def test_unknown_pgid_with_exited_record_is_not_proof(self):
        # Counterfactual: marker exists between Popen and identity publication.
        # Production call: recover_network_time, including dead-man preflight.
        (self.root / "night/chain.started").write_text("{}")
        (self.root / "night/chain.exited").write_text(json.dumps({"exit_code": None}))
        self.assertEqual(nt.recover_network_time(marker_path=self.marker, runner=self.runner,
            process_group_absent=lambda pgid: True), "chain_unproved")
        self.assertNotIn(nt.ON_ARGV, self.runner.calls)
        self.assertTrue(self.marker.exists())

    def test_missing_start_and_exit_records_do_not_prove_chain_absent(self):
        # Counterfactual: custody start/exit files are missing after OFF.
        # Production call: recover_network_time at the next driver start.
        (self.root / "night/chain.started").unlink()
        (self.root / "night/chain.exited").unlink()
        self.assertEqual(nt.recover_network_time(marker_path=self.marker, runner=self.runner,
            process_group_absent=lambda pgid: True), "chain_unproved")
        self.assertNotIn(nt.ON_ARGV, self.runner.calls)
        self.assertTrue(self.marker.exists())

    def test_recovery_runner_exception_returns_chain_unproved_without_on(self):
        def broken(argv, timeout):
            raise RuntimeError("runner unavailable")
        self.assertEqual(nt.recover_network_time(marker_path=self.marker, runner=broken),
                         "chain_unproved")
        self.assertTrue(self.marker.exists())
        self.assertEqual(nt.recover_network_time(marker_path=None), "marker_invalid")

    def test_recovery_attempts_on_when_off_receipt_cannot_drive_query(self):
        # Counterfactual: malformed saved OFF JSON after a proved chain end.
        # Production call: recover_network_time must still attempt ON.
        (self.window / "h5-off.json").write_text("[]")
        self.assertEqual(nt.recover_network_time(marker_path=self.marker, runner=self.runner,
            boot_probe=lambda: "boot-1"), "restored")
        self.assertIn(nt.ON_ARGV, self.runner.calls)
        self.assertFalse(self.marker.exists())

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
        stamps = {
            name: {"epoch_s": 10600 + index * 2,
                   "monotonic_before_s": 10600 + index * 2,
                   "monotonic_after_s": 10600 + index * 2}
            for index, name in enumerate(("pre_spawn", "first_parse", "sampling_started",
                                          "sampling_stopped", "post_parse"))}
        stamps["post_parse"] = dict(self.last, monotonic_after_s=self.last["monotonic_before_s"])
        capture.write_text(json.dumps({"clock_anchor": {"clock_stamps": {
            **stamps}, "rate_fit_baseline_s": 10}, "B": "forbidden"}))
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

    def test_h7_span_and_rate_match_estimator_over_all_five_pairs(self):
        # Counterfactual: a middle reading holds the largest offset while
        # endpoints cancel. Production call: report --h7.
        from joulewise.clock import ClockStamp
        from joulewise.uncertainty_evidence import _offset_envelope_s
        names = ("pre_spawn", "first_parse", "sampling_started", "sampling_stopped", "post_parse")
        stamps = {}
        for index, name in enumerate(names):
            epoch = 10600 + index * 2 + (0.002 if index == 2 else 0)
            stamps[name] = dict(epoch_s=epoch,
                monotonic_before_s=10600 + index * 2,
                monotonic_after_s=10600 + index * 2 + 0.0001,
                wall_resolution_s=1e-6, monotonic_resolution_s=1e-6)
        capture = self.root / "five.json"
        capture.write_text(json.dumps({"clock_anchor": {
            "clock_stamps": stamps, "rate_fit_baseline_s": 8.0}}))
        output = io.StringIO()
        with redirect_stdout(output):
            nt.main(["report", "--h7", "--window-dir", str(self.window), "--capture", str(capture)])
        row = json.loads(output.getvalue())
        expected = _offset_envelope_s([ClockStamp(**stamps[name]) for name in names])[2]
        self.assertEqual(row["drift_term_s"], expected)
        self.assertEqual(row["standing_rate_ppm"], expected / 8 * 1e6)


if __name__ == "__main__":
    unittest.main()
