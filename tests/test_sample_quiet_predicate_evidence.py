"""Fixture checks plus bounded no-power subprocess and low-duty load checks."""
from dataclasses import asdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import plistlib
import resource
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from scripts import sample_quiet_predicate_evidence as harness


# Headroom on the kernel-charged CPU ceiling: measured child start-up plus
# unreported CPU ≈ 0.34–0.35 s on this host (records 06/11), with a 0.5 s floor.
STARTUP_CPU_S = 0.5


class FakeClock:
    def __init__(self):
        self.now = 0.0
        self.used = 0.0
        self.ratio = 1.0

    def monotonic(self):
        return self.now

    def cpu(self):
        return self.used

    def stamp(self):
        return harness.ClockStamp(1000 + self.now, self.now, self.now, 0, 0)

    def sleep(self, seconds):
        self.now += seconds

    def sleep_until(self, deadline):
        self.now = max(self.now, deadline)

    def burn(self, count):
        self.now += count * .00001 * self.ratio
        self.used += count * .00001


def document(*, timestamp=1001, elapsed_ns=1_000_000_000, cpu=2000):
    return {
        "timestamp": datetime.fromtimestamp(timestamp, timezone.utc).replace(tzinfo=None),
        "elapsed_ns": elapsed_ns, "is_delta": True,
        "processor": {
            "cpu_power": cpu, "gpu_power": 500, "ane_power": 100,
            "combined_power": cpu + 610,
            "cpu_energy": int(cpu * elapsed_ns / 1e9),
            "gpu_energy": int(500 * elapsed_ns / 1e9),
            "ane_energy": int(100 * elapsed_ns / 1e9),
            "clusters": [{"name": "E", "idle_ratio": .25, "down_ratio": .125,
                          "online_ratio": .875,
                          "dvfm_states": [{"freq": 1e9, "used_ratio": .25},
                                          {"freq": 2e9, "used_ratio": .75}],
                          "cpus": [{"cpu": 0, "idle_ratio": .6, "down_ratio": .1,
                                    "freq_hz": 1.2e9}]}],
        },
    }


def stream(*docs):
    return b"\0".join(plistlib.dumps(d) for d in docs) + b"\0"


def placed(frame, start_s, end_s, **extra):
    """Place a parsed frame on the wall timeline in both representations.

    After the cold gate (ruling 10 Q3) the integer-nanosecond endpoints are the
    load-bearing ones and the float seconds are derived from them, so a fixture
    that set only ``start_s``/``end_s`` would no longer describe a frame.
    """
    start_ns, end_ns = round(start_s * 1e9), round(end_s * 1e9)
    return {**frame, "start_ns": start_ns, "end_ns": end_ns,
            "start_s": start_ns / 1e9, "end_s": end_ns / 1e9, **extra}


def aligned_fixture():
    frames, _ = harness.parse_frames(stream(document(), document(timestamp=1003, elapsed_ns=2_000_000_000, cpu=4000)))
    return [placed(frames[0], 1000.0, 1001.0), placed(frames[1], 1001.0, 1003.0)]


def network_time_control(directory, stdout=None, exit_code=0):
    """The chain's OFF receipt, the only admission the collector accepts."""
    path = Path(directory) / "network_time_control.json"
    path.write_text(json.dumps({"schema": "joulewise.network_time_control.v1",
        "off": {"argv": ["/usr/bin/sudo", "-n", "/usr/sbin/systemsetup",
                         "-setusingnetworktime", "off"],
                "exit_code": exit_code, "epoch_s": 1000.0, "monotonic_s": 10.0,
                "stdout": harness.EXPECTED_NETWORK_TIME_OFF_STDOUT if stdout is None else stdout},
        "on": None}))
    return path


class NetworkTimeOffMixin:
    """Ruling 10 Q1 rule 3: every collect() needs the chain's OFF receipt."""

    def setUp(self):
        super().setUp()
        directory = tempfile.TemporaryDirectory(dir="/tmp")
        self.addCleanup(directory.cleanup)
        self.network_time_record = network_time_control(directory.name)
        patcher = patch.dict(os.environ,
                             {harness.NETWORK_TIME_RECORD_ENV: str(self.network_time_record)})
        patcher.start()
        self.addCleanup(patcher.stop)


def collect_args(directory, **kwargs):
    defaults = dict(out=str(directory), state="idle", repeat="1", duration_s=5,
                    sample_interval_s=2, power=False, power_interval_ms=100, load_cores=None)
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def fake_round(interval, deadline, raw_dir, clock):
    initial = clock.monotonic()
    clock.sleep_until(min(deadline, initial + interval))
    partial = clock.monotonic() - initial < interval
    (raw_dir / "test.txt").write_text("fixture raw evidence")
    return {"status": "partial" if partial else "complete",
            "error": "deadline" if partial else None,
            "observation": None if partial else {"metrics": {"busy_cores": .2, "host_busy_cores": .2}},
            "observer_cpu_s": .01, "end_stamp": asdict(clock.stamp()), "workers": [], "argv": []}


def delayed_exit_load_worker(connection, config):
    """Probe C: deliver the result, then need time for child shutdown."""
    connection.send({"ready": True})
    connection.recv()
    connection.send({"periods": []})
    connection.close()
    harness.time.sleep(config["seed"])


def assert_null_reasons(test, value):
    if isinstance(value, dict):
        for key, item in value.items():
            if item is None:
                test.assertIsInstance(value.get(key + "_reason"), str, key)
                test.assertTrue(value[key + "_reason"], key)
            else:
                assert_null_reasons(test, item)
    elif isinstance(value, list):
        for item in value:
            test.assertIsNotNone(item)
            assert_null_reasons(test, item)


class FrameTests(unittest.TestCase):
    def test_absolute_anchor_endpoints_reject_known_arrival_offset(self):
        frames, _ = harness.parse_frames(stream(document(), document(timestamp=1003, elapsed_ns=2_000_000_000)))
        # Fixture anchor model: wall = mono + 900; native endpoint mono=101.25.
        # First parse arrives 0.5 s AFTER that endpoint, outside the 0.01 s bound.
        endpoint, bound = 900 + 101.25, .01
        stamps = {"first_parse": harness.ClockStamp(endpoint + .5, 101.75, 101.75, 0, 0)}
        model = {"status": "bounded", "first_sample_end_point_epoch_s": endpoint,
                 "admissible_lower_epoch_s": endpoint - bound,
                 "admissible_upper_epoch_s": endpoint + bound,
                 "effective_clock_anchor_bound_s": bound}
        aligned, anchor = harness.align_frames(frames, stamps, deriver=Mock(return_value=model))
        for frame, elapsed in zip(aligned, (0, 2)):
            self.assertAlmostEqual(frame["end_s"], endpoint + elapsed)
            self.assertAlmostEqual(frame["start_s"], endpoint + elapsed - frame["elapsed_s"])
            self.assertLessEqual(abs(frame["end_s"] - elapsed - endpoint), bound)
        self.assertEqual(anchor["effective_clock_anchor_bound_s"], bound)
        self.assertGreater(stamps["first_parse"].epoch_s, anchor["admissible_upper_epoch_s"])

    def test_production_argv_list_equality(self):
        adapter = object.__new__(harness.pm.PowermetricsTelemetryAdapter)
        adapter._executable = harness.pm.POWER_METRICS
        adapter._privilege_prefix = ("sudo", "-n")
        for interval in (100, 250):
            expected = adapter._command(None, Path("raw/data.plist"), count=None, interval_ms=interval)
            self.assertEqual(harness.power_argv("raw/data.plist", interval), expected)
            self.assertEqual(expected, ["sudo", "-n", "/usr/bin/powermetrics", "-b", "0", "-i", str(interval),
                                        "--samplers", "cpu_power,gpu_power,ane_power,thermal", "--format", "plist", "-o", "raw/data.plist"])

    def test_native_units_residency_and_missing_dram(self):
        frames, diagnostic = harness.parse_frames(stream(document(elapsed_ns=100_000_000)))
        frame = frames[0]
        self.assertIsNone(diagnostic)
        self.assertEqual(frame["elapsed_s"], .1)
        self.assertEqual(frame["native_timestamp_ns"], 1001_000_000_000)
        self.assertEqual(frame["power"]["cpu_w"], 2)
        self.assertEqual(frame["power"]["rail_sum_w"], 2.6)
        self.assertEqual(frame["power"]["combined_w"], 2.61)
        self.assertIsNone(frame["power"]["dram_w"])
        self.assertTrue(frame["power"]["dram_w_reason"])
        self.assertEqual(frame["clusters"][0]["active_ratio"], .625)
        self.assertEqual(frame["clusters"][0]["freq_hz"], 1.75e9)
        self.assertAlmostEqual(frame["cpus"][0]["active_ratio"], .3)
        self.assertEqual(frame["cpus"][0]["freq_hz"], 1.2e9)

    def test_absent_rail_is_not_zero(self):
        doc = document()
        del doc["processor"]["gpu_power"]
        doc["processor"]["dram_power"] = 123
        frame = harness.parse_frames(stream(doc))[0][0]
        self.assertIsNone(frame["power"]["gpu_w"])
        self.assertIsNone(frame["power"]["rail_sum_w"])
        self.assertEqual(frame["power"]["dram_w"], .123)
        assert_null_reasons(self, harness.reasons(frame))

    def test_truncated_tail_recorded_interior_corruption_refuses(self):
        frames, diagnostic = harness.parse_frames(stream(document()) + b"<?xml incomplete")
        self.assertEqual(len(frames), 1)
        self.assertEqual(diagnostic["frame_index"], 1)
        self.assertEqual(len(diagnostic["sha256"]), 64)
        with self.assertRaises(ValueError):
            harness.parse_frames(stream(document()) + b"broken\0" + stream(document()))

    def test_bad_duration_and_native_stamp_refuse(self):
        for key, value in (("elapsed_ns", 0), ("elapsed_ns", True), ("timestamp", "1000")):
            doc = document()
            doc[key] = value
            with self.assertRaises(ValueError):
                harness.parse_frames(stream(doc))

    def test_alignment_uses_current_record_elapsed_not_previous_or_arrival(self):
        frames, _ = harness.parse_frames(stream(document(elapsed_ns=100_000_000),
                                                 document(elapsed_ns=200_000_000),
                                                 document(elapsed_ns=300_000_000)))
        oracle = Mock(return_value={"status": "bounded", "first_sample_end_point_epoch_s": 1001.25})
        aligned, _ = harness.align_frames(frames, {}, deriver=oracle)
        self.assertEqual([round(f["end_s"], 2) for f in aligned], [1001.25, 1001.45, 1001.75])
        self.assertEqual([round(f["start_s"], 2) for f in aligned], [1001.15, 1001.25, 1001.45])
        self.assertEqual(oracle.call_args.kwargs["records"][1].elapsed_ns, 200_000_000)

    def test_real_production_rate_anchor_and_clock_step_refusal(self):
        docs = [document(timestamp=1001 + i, elapsed_ns=999_000_000 if i == 0 else 1_000_000_000, cpu=1000)
                for i in range(61)]
        for doc in docs:
            doc["processor"]["gpu_power"] = doc["processor"]["ane_power"] = 0
            doc["processor"]["gpu_energy"] = doc["processor"]["ane_energy"] = 0
        frames, _ = harness.parse_frames(stream(*docs))
        def stamp(mono):
            return harness.ClockStamp(mono + 900, mono, mono, 0, 0)
        stamps = {"pre_spawn": stamp(100), "first_parse": stamp(101 + 1 / 1024),
                  "sampling_started": stamp(102), "sampling_stopped": stamp(160), "post_parse": stamp(161)}
        aligned, anchor = harness.align_frames(frames, stamps)
        self.assertEqual(anchor["status"], "bounded", anchor)
        self.assertEqual(len(aligned), 61)
        self.assertLess(anchor["effective_clock_anchor_bound_s"], .005)
        # Affine wall=mono+900 model: production residual allowance gives
        # lower=1001-.00025; the causal first-parse stamp supplies the upper.
        lower, upper = 1001 - .00025, 1001 + 1 / 1024
        midpoint = (lower + upper) / 2
        self.assertAlmostEqual(anchor["admissible_lower_epoch_s"], lower)
        self.assertAlmostEqual(anchor["admissible_upper_epoch_s"], upper)
        self.assertAlmostEqual(aligned[0]["end_s"], midpoint)
        self.assertAlmostEqual(aligned[-1]["end_s"], midpoint + 60)
        # Arrival differs from the anchored endpoint by (upper-lower)/2;
        # centering at arrival would fail to cover the admissible lower end.
        for endpoint in (lower, upper):
            self.assertLessEqual(abs(aligned[0]["end_s"] - endpoint),
                                 anchor["effective_clock_anchor_bound_s"])
        self.assertAlmostEqual(aligned[-1]["end_s"] - aligned[0]["end_s"], 60)
        stamps["sampling_stopped"] = harness.ClockStamp(1061, 160, 160, 0, 0)
        aligned, broken = harness.align_frames(frames, stamps)
        self.assertEqual(aligned, [])
        self.assertNotEqual(broken["status"], "bounded")

    def test_short_capture_does_not_invent_linear_anchor(self):
        frames, _ = harness.parse_frames(stream(document()))
        aligned, anchor = harness.align_frames(frames, {})
        self.assertEqual(aligned, [])
        self.assertEqual(anchor["detail"], "clock_stamp_unavailable")


class IntegrationTests(unittest.TestCase):
    def test_known_overlap_integral_and_weighted_residency(self):
        frames = aligned_fixture()
        frames[1]["cpus"][0]["active_ratio"] = .9
        reduced = harness.integrate(frames, 1000.5, 1002)
        self.assertAlmostEqual(reduced["power"]["energy_j"]["cpu_w"], 5)
        self.assertAlmostEqual(reduced["power"]["cpu_w"], 10 / 3)
        self.assertAlmostEqual(reduced["power"]["energy_j"]["rail_sum_w"], 5.9)
        self.assertEqual(reduced["power"]["coverage_s"], 1.5)
        self.assertAlmostEqual(reduced["cpus"][0]["active_ratio"], .7)
        self.assertFalse(reduced["span_mismatch"])
        self.assertEqual(reduced["error_bound_j"], 0)

    def test_gap_or_span_mismatch_cannot_have_finite_energy_bound(self):
        reduced = harness.integrate(aligned_fixture(), 999, 1002, .01)
        self.assertTrue(reduced["span_mismatch"])
        self.assertEqual(reduced["power"]["coverage_s"], 2)
        self.assertIsNone(reduced["error_bound_j"])

    def test_anchor_uncertainty_exposing_unobserved_edge_is_unbounded(self):
        reduced = harness.integrate(aligned_fixture(), 1000, 1002, .01)
        self.assertFalse(reduced["span_mismatch"])
        self.assertIsNone(reduced["error_bound_j"])

    def test_alignment_bound_contains_shifted_integrals(self):
        frames = aligned_fixture()
        reduced = harness.integrate(frames, 1000.5, 1002, .01)
        energy = reduced["power"]["energy_j"]["rail_sum_w"]
        self.assertAlmostEqual(reduced["error_bound_j"], (2.6 + 4.6) * .02)
        for delta in (-.01, -.003, .01):
            shifted = [placed(f, f["start_s"] + delta, f["end_s"] + delta) for f in frames]
            actual = harness.integrate(shifted, 1000.5, 1002)["power"]["energy_j"]["rail_sum_w"]
            self.assertLessEqual(abs(actual - energy), reduced["error_bound_j"])

    def test_overlapping_frames_are_rejected(self):
        frames = aligned_fixture()
        frames[1] = placed(frames[1], 1000.9, frames[1]["end_s"])
        with self.assertRaises(ValueError):
            harness.integrate(frames, 1000.5, 1002)


class CollectionTests(NetworkTimeOffMixin, unittest.TestCase):
    def test_hard_probe_results_survive_complete_and_interrupted_rounds(self):
        from joulewise import night_gate
        from scripts import run_night
        # An AC loss, a restricted CPU and a probe error must survive even
        # though smoke_observation_round discards the hard worker's return.
        probes = [
            {"argv": list(night_gate.PMSET_BATT_ARGV), "exit_code": 0,
             "stdout": "Now drawing from 'Battery Power'\n", "stderr": ""},
            {"argv": list(night_gate.THERMAL_ARGV), "exit_code": 0,
             "stdout": "CPU_Speed_Limit = 80\n", "stderr": ""},
            {"argv": list(night_gate.THERMAL_ARGV), "exit_code": 1,
             "stdout": "", "stderr": "fixture probe failure"},
        ]
        for interrupted in (False, True):
            with self.subTest(interrupted=interrupted), tempfile.TemporaryDirectory() as tmp:
                jobs = [SimpleNamespace(job_id=f"smoke-hard-{index}", reaped=True,
                    launch_done=True, process=SimpleNamespace(pid=None),
                    ready=lambda: True, result=lambda probe=probe: [probe])
                    for index, probe in enumerate(probes, 1)]
                def smoke(interval):
                    for job in jobs:
                        run_night._BindTask(job.job_id, None, None)
                    if interrupted:
                        raise harness.CollectionExpired("fixture deadline")
                    return {}, 0
                with patch.object(run_night, "_BindTask", side_effect=jobs), \
                        patch.object(run_night, "smoke_observation_round", side_effect=smoke):
                    result = harness.production_round(1, 5, Path(tmp), FakeClock())
                row = harness.new_row("fixture", collect_args(tmp), 1,
                    FakeClock().stamp(), FakeClock().stamp(), result)
                self.assertEqual(row["status"], "partial" if interrupted else "complete")
                self.assertEqual(row["hard_probes"], [
                    {"job_id": job.job_id, "result": [probe]} for job, probe in zip(jobs, probes)])
                self.assertEqual(row["hard_probe_errors"], [])

    def test_missing_and_failed_hard_workers_are_retained_as_errors(self):
        from scripts import run_night
        jobs = [SimpleNamespace(job_id=f"smoke-hard-{i}", reaped=True, launch_done=True,
                process=SimpleNamespace(pid=None), ready=lambda ready=ready: ready,
                result=Mock(side_effect=RuntimeError("fixture transport failure")))
                for i, ready in enumerate((True, False), 1)]
        def smoke(interval):
            for job in jobs:
                run_night._BindTask(job.job_id, None, None)
            raise harness.CollectionExpired("fixture deadline")
        with tempfile.TemporaryDirectory() as tmp, \
                patch.object(run_night, "_BindTask", side_effect=jobs), \
                patch.object(run_night, "smoke_observation_round", side_effect=smoke):
            result = harness.production_round(1, 5, Path(tmp), FakeClock())
        self.assertEqual(result["hard_probes"], [])
        self.assertEqual(result["hard_probe_errors"], [
            {"job_id": "smoke-hard-1", "error": "fixture transport failure"},
            {"job_id": "smoke-hard-2", "error": "hard probes did not complete during round"}])
        jobs[1].result.assert_not_called()

    def test_collected_os_build_is_validated_persisted_and_used_by_summary(self):
        for build in ("25G83", None, "", "25G83\n", ["25G83"]):
            with self.subTest(build=build), tempfile.TemporaryDirectory() as tmp, \
                    patch.object(harness.subprocess, "Popen", side_effect=AssertionError("no subprocess")):
                session, rows = harness.collect(collect_args(tmp), clock=FakeClock(),
                    round_runner=fake_round, metadata_reader=lambda: {"boot_id": "fixture", "os_build": build})
                valid = build == "25G83"
                self.assertEqual(session["os_build"], build)  # Raw metadata preserved.
                persisted = [json.loads(line) for line in (Path(tmp) / "rounds.jsonl").read_text().splitlines()]
                for row in persisted:
                    self.assertEqual(row["os_build"], build if valid else None)
                    self.assertIs(row["os_build_valid"], valid)
                    if not valid:
                        self.assertIn("missing or malformed", row["os_build_reason"])
                summary = harness.summarize(tmp, "idle")
                self.assertEqual(summary["groups"][0]["os_build"], build if valid else None)
                self.assertEqual(summary["groups"][0]["os_build_unavailable_rounds"], 0 if valid else len(rows))

    def test_partial_round_retains_concurrent_census_and_marks_contamination(self):
        from scripts import run_night
        hit = {"exit_code": 0, "stdout": "123 claude -p\n", "stderr": "", "refusal": {"reason": "agent"}}
        job = SimpleNamespace(job_id="census-1", reaped=True, launch_done=True,
                              process=SimpleNamespace(pid=None), ready=lambda: True,
                              result=lambda: hit)
        def smoke(interval):
            run_night._BindTask("census-1", None, None)
            raise harness.CollectionExpired("fixture deadline")
        with tempfile.TemporaryDirectory() as tmp, patch.object(run_night, "_BindTask", return_value=job), \
                patch.object(run_night, "smoke_observation_round", side_effect=smoke):
            result = harness.production_round(1, 5, Path(tmp), FakeClock())
            row = harness.new_row("fixture", collect_args(tmp), 1, FakeClock().stamp(), FakeClock().stamp(), result)
        self.assertEqual(row["status"], "partial")
        self.assertIsNone(row["observation"])
        self.assertEqual(row["censuses"][0]["result"], hit)
        self.assertIs(row["census_clean"], False)
        # A clean sampler at the end cannot erase the earlier concurrent hit.
        result["observation"] = {"census": {"exit_code": 1, "stdout": "", "stderr": ""}}
        row = harness.new_row("fixture", collect_args("unused"), 1, FakeClock().stamp(), FakeClock().stamp(), result)
        self.assertEqual(len(row["censuses"]), 2)
        self.assertIs(row["census_clean"], False)

    def test_round_without_completed_census_is_reasoned_unknown(self):
        result = {"status": "partial", "error": "deadline", "observation": None, "observer_cpu_s": .1}
        row = harness.new_row("fixture", collect_args("unused"), 1, FakeClock().stamp(), FakeClock().stamp(), result)
        self.assertIsNone(row["censuses"])
        self.assertIsNone(row["census_clean"])
        self.assertIn("no census completed", row["census_clean_reason"])
        result["censuses"] = [{"source": "concurrent", "result": {"exit_code": 1, "stdout": "", "stderr": ""}}]
        row = harness.new_row("fixture", collect_args("unused"), 1, FakeClock().stamp(), FakeClock().stamp(), result)
        self.assertIs(row["census_clean"], True)
        result["census_errors"] = [{"job_id": "census-2", "error": "deadline"}]
        row = harness.new_row("fixture", collect_args("unused"), 1, FakeClock().stamp(), FakeClock().stamp(), result)
        self.assertIsNone(row["census_clean"])

    def test_smoke_temporary_journal_writes_stay_under_output(self):
        from scripts import run_night
        created = []
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            out = root / "out"
            out.mkdir()
            def smoke(interval):
                # Same local import/factory as the production smoke round.
                import tempfile
                with tempfile.TemporaryDirectory(prefix="jw-observer-round-") as directory:
                    journal = Path(directory) / "censuses.jsonl"
                    created.append(journal)
                    self.assertTrue(journal.is_relative_to(out))
                    journal.write_text("{}\n")
                return {}, 0
            with patch.object(run_night, "smoke_observation_round", side_effect=smoke):
                harness.production_round(1, 5, out, FakeClock())
            self.assertTrue(created)
            self.assertTrue(all(path.is_relative_to(out) for path in created))
            self.assertEqual(list(root.iterdir()), [out])

    @unittest.skipUnless(sys.platform == "darwin", "real collect subprocess runs the macOS census and "
                         "power-policy probes (pmset, sysctl); on Linux every round errors and, since fix "
                         "round 4, an all-error session exits 1 by design")
    def test_real_collect_no_power_reaps_all_recorded_workers(self):
        with tempfile.TemporaryDirectory() as tmp:
            # One second is the minimum top sampling interval; use one interval.
            command = [sys.executable, "-B", str(Path(harness.__file__).resolve()),
                       "collect", "--no-power", "--duration-s", "1",
                       "--sample-interval-s", "1", "--state", "integration",
                       "--repeat", "1", "--out", tmp]
            # Audit real parent/production journal writes, including temporary
            # mkdirs that would otherwise disappear before filesystem checks.
            audit = '''import os, runpy, sys
from pathlib import Path
script, target = sys.argv[1:3]
root = Path(target).resolve()
def audit(event, args):
    path = None
    if event == "open" and isinstance(args[0], (str, bytes)) and args[2] & (os.O_WRONLY | os.O_RDWR | os.O_CREAT):
        path = os.fsdecode(args[0])
    elif event == "os.mkdir":
        path = os.fsdecode(args[0])
    if path is not None and path != os.devnull and not Path(path).resolve().is_relative_to(root):
        print("OUTSIDE_OUTPUT", path, flush=True)
        raise AssertionError("write outside --out")
sys.addaudithook(audit)
sys.argv = [script, *sys.argv[3:]]
runpy.run_path(script, run_name="__main__")
'''
            command = [sys.executable, "-B", "-c", audit, command[2], tmp, *command[3:]]
            completed = subprocess.run(command, capture_output=True, text=True, timeout=20,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "TMPDIR": "/tmp",
                     harness.NETWORK_TIME_RECORD_ENV: str(self.network_time_record)})
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertNotIn("OUTSIDE_OUTPUT", completed.stdout)
            root = Path(tmp)
            rows = [json.loads(line) for line in (root / "rounds.jsonl").read_text().splitlines()]
            self.assertTrue(rows)
            for row in rows:
                self.assertIn(row["status"], ("complete", "partial", "error"))
                self.assertIn("error", row)
                if row["status"] != "complete":
                    self.assertTrue(row["error"])
                self.assertIsNone(row["power"]["cpu_w"])
                self.assertEqual(row["power"]["cpu_w_reason"], "power disabled")
            session = json.loads((root / "session.json").read_text())
            jobs = [job for round_ in session["round_workers"] for job in round_["workers"]]
            pids = {job["pid"] for job in jobs if job["pid"] is not None}
            self.assertTrue(pids, jobs)
            self.assertTrue(all(job["reaped"] for job in jobs if job["pid"] is not None))
            for pid in pids:
                with self.assertRaises(ProcessLookupError, msg=f"worker {pid} survived"):
                    os.kill(pid, 0)

    def test_observer_cost_includes_known_reaped_child_delta(self):
        from scripts import run_night
        # SELF grows .2 s; reaped CHILDREN grow .7 s. Observer cost is .9 s.
        usages = {harness.resource.RUSAGE_SELF: iter([(1, .1), (1.15, .15)]),
                  harness.resource.RUSAGE_CHILDREN: iter([(2, .3), (2.5, .5)])}
        def usage(kind):
            user, system = next(usages[kind])
            return SimpleNamespace(ru_utime=user, ru_stime=system)
        with tempfile.TemporaryDirectory() as tmp, \
                patch.object(harness.resource, "getrusage", side_effect=usage), \
                patch.object(run_night, "smoke_observation_round", return_value=({}, 0)):
            result = harness.production_round(1, 5, Path(tmp), FakeClock())
        self.assertAlmostEqual(result["observer_cpu_s"], .9)

    def test_no_power_partial_round_schema_and_hashes(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(harness.subprocess, "Popen", side_effect=AssertionError("no subprocess")):
            args = collect_args(tmp)
            session, rows = harness.collect(args, clock=FakeClock(), round_runner=fake_round,
                metadata_reader=lambda: {"boot_id": "fixture-boot", "os_build": "fixture-build"})
            persisted = [json.loads(line) for line in (Path(tmp) / "rounds.jsonl").read_text().splitlines()]
            self.assertEqual(len(rows), 3)
            self.assertEqual([r["status"] for r in rows], ["complete", "complete", "partial"])
            self.assertEqual(rows[-1]["round_mono_end_s"], 5)
            self.assertIsNone(session["error"])
            self.assertEqual(session["error_rounds"], 0)
            self.assertTrue(session["powermetrics_needs_root"])
            self.assertFalse(session["sudo_policy_probed"])
            for row in persisted:
                self.assertTrue(set(harness.ROUND_KEYS) <= row.keys())
                self.assertTrue(set(harness.RAILS) | {"coverage_s"} <= row["power"].keys())
                self.assertTrue({"anchor_lo", "anchor_hi", "ps_start", "ps_end", "top_start", "top_end", "error_bound_j"} <= row["alignment"].keys())
                assert_null_reasons(self, row)
                for name in row["raw"]["paths"]:
                    self.assertEqual(row["raw"]["sha256"][name], harness.hashlib.sha256((Path(tmp) / name).read_bytes()).hexdigest())

    def test_existing_evidence_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "precious").write_text("old")
            with self.assertRaises(ValueError):
                harness.collect(collect_args(tmp), clock=FakeClock())
            self.assertEqual((Path(tmp) / "precious").read_text(), "old")

    def test_one_recorder_for_all_rounds_and_cleanup_on_round_failure(self):
        clock = FakeClock()
        recorder = Mock()
        recorder.metadata = {"argv": ["fake"]}
        recorder.finish.return_value = ([], {"status": "unknown", "detail": "fixture"})
        factory = Mock(return_value=recorder)
        with tempfile.TemporaryDirectory() as tmp:
            session, rows = harness.collect(collect_args(tmp, power=True), clock=clock,
                recorder_factory=factory, round_runner=fake_round, metadata_reader=lambda: {})
            factory.assert_called_once()
            recorder.start.assert_called_once()
            recorder.finish.assert_called_once()
            self.assertEqual(len(rows), 3)
        recorder.reset_mock()
        with tempfile.TemporaryDirectory() as tmp:
            session, rows = harness.collect(collect_args(tmp, power=True), clock=FakeClock(),
                recorder_factory=factory, round_runner=Mock(side_effect=RuntimeError("test round failed")),
                metadata_reader=lambda: {})
            recorder.finish.assert_called_once()
            self.assertIn("test round failed", session["error"])
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["status"], "error")
        # S3 / probe_a B: collect() must surface all-error rounds through main(),
        # while one returned error among three rounds must not abort the chain.
        real_collect = harness.collect
        for statuses, expected_exit in ((["error"] * 3, 1), (["complete", "error", "complete"], 0)):
            with self.subTest(statuses=statuses), tempfile.TemporaryDirectory() as tmp:
                pending = iter(statuses)
                def round_runner(interval, deadline, raw_dir, clock):
                    result = fake_round(interval, deadline, raw_dir, clock)
                    result["status"] = next(pending)
                    result["error"] = "RuntimeError: smoke blew up" if result["status"] == "error" else None
                    return result
                def collect_for_cli(args):
                    return real_collect(args, clock=FakeClock(), round_runner=round_runner,
                                        metadata_reader=lambda: {})
                with patch.object(harness, "collect", side_effect=collect_for_cli):
                    self.assertEqual(harness.main(["collect", "--no-power", "--out", tmp,
                        "--state", "idle", "--repeat", "1", "--duration-s", "3",
                        "--sample-interval-s", "1"]), expected_exit)
                session = json.loads((Path(tmp) / "session.json").read_text())
                rows = [json.loads(line) for line in (Path(tmp) / "rounds.jsonl").read_text().splitlines()]
                self.assertEqual([row["status"] for row in rows], statuses)
                self.assertEqual(session["error_rounds"], statuses.count("error"))
                if expected_exit:
                    self.assertTrue(session["error"])
                else:
                    self.assertIsNone(session["error"])

    def test_completed_power_collection_reduces_each_round_after_one_finish(self):
        recorder = Mock()
        recorder.metadata = {"argv": ["fake"], "cleanup": {"returncode": 0}}
        frame = aligned_fixture()[0]
        frames = [placed(frame, 999.0, 1006.0, elapsed_s=7)]
        recorder.finish.return_value = (frames, {"status": "bounded", "admissible_lower_epoch_s": 1000,
            "admissible_upper_epoch_s": 1000.002, "effective_clock_anchor_bound_s": .001, "method": "fixture"})
        with tempfile.TemporaryDirectory() as tmp:
            session, rows = harness.collect(collect_args(tmp, power=True), clock=FakeClock(),
                recorder_factory=Mock(return_value=recorder), round_runner=fake_round, metadata_reader=lambda: {})
            self.assertIsNone(session["error"])
            self.assertEqual([r["power"]["coverage_s"] for r in rows], [2, 2, 1])
            self.assertTrue(all(r["power"]["cpu_w"] == 2 for r in rows))
            self.assertTrue(all(r["alignment"]["error_bound_j"] > 0 for r in rows))

    def test_scheduled_interior_does_not_move_with_two_second_collector_start_drift(self):
        clock = FakeClock()
        clock.now = 2
        recorder = Mock()
        recorder.metadata = {'cleanup': {'returncode':0}}
        frames = [placed(aligned_fixture()[0], 1000., 1600., elapsed_s=600)]
        recorder.finish.return_value = (frames, {'status':'bounded', 'effective_clock_anchor_bound_s':0,
            'admissible_lower_epoch_s':1000, 'admissible_upper_epoch_s':1000})
        with tempfile.TemporaryDirectory(dir='/tmp') as tmp:
            args = collect_args(tmp, power=True)
            args.duration_s, args.interior_offset_s, args.interior_s = 600, 60, 480
            args.envelope_start_mono_s = 0
            with patch.object(harness, 'reduce_interior', wraps=harness.reduce_interior) as reduce:
                session, _ = harness.collect(args, clock=clock, recorder_factory=Mock(return_value=recorder),
                                             round_runner=fake_round, metadata_reader=lambda: {})
            self.assertEqual(reduce.call_args.args[2:], (1060, 480))
            self.assertEqual(session['start_drift_s'], 2)
            self.assertEqual(session['deadline_mono_s'], 600)
            self.assertTrue(session['interior']['complete_support'])

    def test_power_supervised_stop_eperm_is_logged_and_finish_still_reaps(self):
        recorder = harness.PowerRecorder(Path('/tmp/absent-fixture-power.plist'), 100, FakeClock(), 5)
        recorder.process = Mock(pid=123)
        recorder.process.wait.return_value = 0
        with patch.object(harness.os, 'kill', side_effect=PermissionError('foreign supervisor')), \
                patch.object(harness.threading, 'Timer'), \
                patch.object(harness, 'parse_frames', return_value=([], None)), \
                patch.object(harness, 'align_frames', return_value=([], {'status':'unresolved'})):
            recorder.request_stop()
            recorder.force_stop()
            recorder.finish()
        recorder.process.wait.assert_called_once()
        self.assertEqual(len(recorder.metadata['signal_errors']), 2)

    def test_smoke_supervision_deadline_and_module_restoration(self):
        from scripts import run_night
        clock = FakeClock()
        job = SimpleNamespace(job_id="sample-1", reaped=False, launch_done=True,
                              process=SimpleNamespace(pid=999), ready=lambda: False)
        job.cancel = Mock()
        def reap():
            job.reaped = True
            return True
        job.poll_cleanup = Mock(side_effect=reap)
        old_time = run_night.time
        captured = []
        def smoke(interval):
            run_night._BindTask("sample-1", None, None)
            captured.append(run_night._bind_argv("sample", "sample-1", 9, {"interval": interval, "observer_pid": 1}))
            while True:
                run_night.time.sleep(.01)
        with tempfile.TemporaryDirectory() as tmp, patch.object(run_night, "_BindTask", return_value=job), \
                patch.object(run_night, "smoke_observation_round", side_effect=smoke), \
                patch.object(harness, "cpu_total", side_effect=[1, 1.2]):
            result = harness.production_round(30, .025, Path(tmp), clock)
        self.assertEqual(result["status"], "partial")
        self.assertAlmostEqual(result["observer_cpu_s"], .2)
        self.assertEqual(result["end_stamp"]["monotonic_after_s"], .025)
        self.assertTrue(job.reaped)
        self.assertIn("_sample", captured[0])
        self.assertIn("--result-fd", captured[0])
        self.assertIn("_exec", captured[0])
        self.assertIs(run_night.time, old_time)

    def test_sampler_publishes_real_length_prefixed_frame_without_live_tools(self):
        reader, writer = os.pipe()
        try:
            with tempfile.TemporaryDirectory() as tmp, \
                    patch.object(harness.quiet_admission, "sample_interval", return_value={"full": "observation"}), \
                    patch.object(harness, "identity", return_value={"pid": 1, "start_identity": "fixture"}):
                harness.sample_worker(SimpleNamespace(raw_dir=tmp, result_fd=writer, job_id="sample-test", sample_interval_s=30, observer_pid=1))
            length = int.from_bytes(os.read(reader, 4), "big")
            value = json.loads(os.read(reader, length))
            self.assertEqual(value, {"job_id": "sample-test", "ok": True, "result": {"full": "observation"}})
            self.assertEqual(os.read(reader, 1), b"")  # Production publisher closes its FD.
        finally:
            os.close(reader)
            try:
                os.close(writer)
            except OSError:
                pass

    def test_power_deadline_signals_independently_and_reaps_after_observer_bracket(self):
        clock = FakeClock()
        process = Mock()
        process.pid = 123
        process.poll.return_value = None
        process.wait.side_effect = [subprocess.TimeoutExpired("fake", 5), -9]
        timers = []
        callbacks = []
        def make_timer(delay, callback):
            callbacks.append((delay, callback))
            timer = Mock()
            timers.append(timer)
            return timer
        with tempfile.TemporaryDirectory() as tmp, \
                patch.object(harness.subprocess, "Popen", return_value=process) as launch, \
                patch.object(harness.threading, "Timer", side_effect=make_timer), \
                patch.object(harness.os, "kill") as kill, \
                patch.object(harness, "identity", return_value={"pid": 123, "start_identity": "fixture"}), \
                patch.object(harness, "command_text", return_value=(None, "fixture process list unavailable")):
            path = Path(tmp) / "power.plist"
            path.write_bytes(stream(document()))
            recorder = harness.PowerRecorder(path, 100, clock, 5)
            recorder.start()
            self.assertEqual(callbacks[0][0], 5)
            self.assertEqual(launch.call_count, 1)
            clock.sleep_until(5)
            callbacks[0][1]()
            self.assertEqual(recorder.stamps["sampling_stopped"].monotonic_after_s, 5)
            kill.assert_called_once_with(123, harness.signal.SIGTERM)
            process.wait.assert_not_called()
            process.poll.assert_not_called()
            self.assertEqual(callbacks[1][0], 5)
            # Slow round cleanup cannot delay KILL; no reaping within its CPU bracket.
            clock.sleep_until(10)
            callbacks[1][1]()
            self.assertEqual(kill.call_args, unittest.mock.call(123, harness.signal.SIGKILL))
            process.wait.assert_not_called()
            recorder.finish()
            self.assertTrue(recorder.metadata["cleanup"]["kill"])
            self.assertTrue(recorder.metadata["cleanup"]["reap_after_observer_bracket"])
            for timer in timers:
                timer.cancel.assert_called_once()

    def test_clock_wall_read_is_bracketed(self):
        events = []
        clock = harness.Clock()
        def mono():
            events.append("mono")
            return len(events)
        with patch.object(clock, "monotonic", side_effect=mono), patch.object(harness.time, "time", side_effect=lambda: events.append("wall") or 1000):
            stamp = clock.stamp()
        self.assertEqual(events, ["mono", "wall", "mono"])
        self.assertEqual((stamp.monotonic_before_s, stamp.monotonic_after_s), (1, 3))

    def test_sampler_hooks_keep_public_observation_and_framed_transport(self):
        observation = {"fixture": "full production return"}
        real_run = harness.quiet_admission.subprocess
        with tempfile.TemporaryDirectory() as tmp:
            args = SimpleNamespace(raw_dir=tmp, result_fd=123, job_id="sample-1", sample_interval_s=30, observer_pid=7)
            def fake_sample(interval, *, observer_pid):
                self.assertEqual((interval, observer_pid), (30, 7))
                harness.quiet_admission.time.time()
                for argv in (harness.quiet_admission.PS_ARGV, harness.quiet_admission.top_argv(30), harness.quiet_admission.PS_ARGV):
                    harness.quiet_admission.subprocess.run(argv, capture_output=True, text=True)
                    harness.quiet_admission.time.monotonic()
                return observation
            published = []
            with patch.object(harness.quiet_admission, "sample_interval", side_effect=fake_sample), \
                    patch.object(harness.quiet_admission, "publish_observation", side_effect=lambda fd, job, call: published.append((fd, job, call()))), \
                    patch.object(harness, "identity", return_value={"pid": 10, "start_identity": "fixture"}), \
                    patch.object(harness.subprocess, "run", return_value=SimpleNamespace(stdout="raw", stderr="", returncode=0)):
                harness.sample_worker(args)
            self.assertEqual(published, [(123, "sample-1", observation)])
            evidence = json.loads((Path(tmp) / "sampler.json").read_text())
            self.assertEqual(len(evidence["tools"]), 3)
            self.assertTrue({"ps_start", "ps_end", "top_start", "top_end"} <= evidence["marks"].keys())
            self.assertEqual((Path(tmp) / "ps_before.txt").read_text(), "raw")
        self.assertIs(harness.quiet_admission.subprocess, real_run)


class LoadTests(unittest.TestCase):
    def test_burn_profiles_advance_their_generator(self):
        for profile in ("scalar", "memory"):
            burn = harness.burn_profile(profile, 1)
            self.assertNotEqual(burn(1000), burn(1), f"{profile} burn did no work")
        burn = harness.burn_profile("scalar", 1)
        first = burn(1)
        self.assertEqual(first, (1664525 * 1 + 1013904223) & 0xFFFFFFFF)
        self.assertNotEqual(burn(1), first)

    def test_load_worker_runs_its_window_after_the_rendezvous(self):
        clock = FakeClock()
        sent = []
        connection = SimpleNamespace(send=sent.append, recv=lambda: 1.0, close=lambda: None)
        with patch.object(harness, "set_qos", lambda qos: None), \
                patch.object(harness, "identity", return_value={"pid": 11}), \
                patch.object(harness, "burn_profile", return_value=clock.burn), \
                patch.object(harness, "Clock", return_value=clock):
            harness.load_worker(connection, {"share": .1, "duration_s": 3, "period_s": .5,
                "qos": "user-initiated", "profile": "scalar", "seed": 1})
        self.assertEqual(len(sent), 2, sent)
        self.assertNotIn("error", sent[1])
        periods = sent[1]["periods"]
        self.assertGreater(len(periods), 0, "worker reported no period rows for its window")
        self.assertAlmostEqual(sum(p["cpu_used_s"] for p in periods), .3, delta=.001)
        self.assertEqual(clock.monotonic(), 4.0)   # rendezvous at 1.0 plus the 3 s window
        # N3: load() Process.start() failure must close both real Pipe ends.
        parent, child = harness.multiprocessing.get_context("spawn").Pipe()
        failed = Mock()
        failed.start.side_effect = OSError("fixture start failed")
        guarded = SimpleNamespace(Pipe=lambda: (parent, child), Process=lambda **kwargs: failed)
        try:
            with tempfile.TemporaryDirectory() as tmp, \
                    patch.object(harness.multiprocessing, "get_context", return_value=guarded):
                args = harness.parser().parse_args(["load", "--cores", ".1", "--duration-s", "1",
                    "--qos", "user-initiated", "--profile", "scalar", "--seed", "1",
                    "--log", str(Path(tmp) / "load.json")])
                report = harness.load(args)
                self.assertIn("fixture start failed", report["error"])
                self.assertTrue(parent.closed)
                self.assertTrue(child.closed)
                failed.join.assert_not_called()
        finally:
            parent.close()
            child.close()

    @unittest.skipUnless(sys.platform == "darwin", "real spawned worker uses native QoS; "
                         "hosted Linux shards feed the runner via stdin, which spawn cannot re-import")
    def test_load_join_ladder_accepts_slow_exit_and_escalates_a_stuck_child(self):
        # S1/S2 / probe_c: load()'s real join ladder must accept a one-second
        # post-result exit and expose escalation with a short test-only grace.
        context = harness.multiprocessing.get_context("spawn")
        def process(*, target, args):
            return context.Process(target=delayed_exit_load_worker, args=args)
        guarded = SimpleNamespace(Pipe=context.Pipe, Process=process)
        real_load = harness.load
        for delay, expected_exit in ((1, 0), (60, 1)):
            with self.subTest(exit_delay=delay), tempfile.TemporaryDirectory() as tmp, \
                    patch.object(harness.multiprocessing, "get_context", return_value=guarded), \
                    patch.object(harness, "load", side_effect=lambda args: real_load(
                        args, **({"join_grace_s": 0.2} if delay == 60 else {}))):
                log = Path(tmp) / "load.json"
                self.assertEqual(harness.main(["load", "--cores", ".1", "--duration-s", "1",
                    "--qos", "user-initiated", "--profile", "scalar",
                    "--seed", str(delay), "--log", str(log)]), expected_exit)
                report = json.loads(log.read_text())
                child = report["cleanup"][0]
                self.assertFalse(child["alive"])
                if expected_exit:
                    self.assertEqual(child["exitcode"], -harness.signal.SIGTERM)
                    self.assertIn(f"worker cleanup escalated: pid {child['pid']} exitcode {child['exitcode']}",
                                  report["error"])
                else:
                    self.assertIsNone(report["error"])
                    self.assertEqual(child["exitcode"], 0)

    @unittest.skipUnless(sys.platform == "darwin", "native QoS requires macOS")
    def test_native_qos_classes_read_back_in_subprocess(self):
        # S6: set_qos() must apply the requested class, not merely label the report.
        # A fresh subprocess leaves the test runner's own QoS unchanged.
        code = '''import ctypes, json
from scripts import sample_quiet_predicate_evidence as harness
lib = ctypes.CDLL("/usr/lib/libSystem.B.dylib")
lib.pthread_self.argtypes = []
lib.pthread_self.restype = ctypes.c_void_p
lib.pthread_get_qos_class_np.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(ctypes.c_int)]
lib.pthread_get_qos_class_np.restype = ctypes.c_int
rows = []
for qos in ("background", "user-initiated"):
    harness.set_qos(qos)
    cls, priority = ctypes.c_uint(), ctypes.c_int()
    result = lib.pthread_get_qos_class_np(lib.pthread_self(), ctypes.byref(cls), ctypes.byref(priority))
    rows.append([qos, result, cls.value])
print(json.dumps(rows))
'''
        result = subprocess.run([sys.executable, "-B", "-c", code], capture_output=True,
                                text=True, timeout=20, cwd=Path(harness.__file__).resolve().parents[1])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), [["background", 0, 0x09], ["user-initiated", 0, 0x19]])

    @unittest.skipUnless(sys.platform == "darwin", "native QoS requires macOS")
    def test_real_load_tracks_point_one_core_and_guards_worker_budget(self):
        # The controller promises a measured CPU ceiling and no catch-up, never delivery.
        # Use 500 ms periods: this host can coalesce sleeps by ~150 ms, longer
        # than a 100 ms period, and the controller deliberately never catches up.
        # Check config BEFORE launch so the cores mutation cannot burn a core.
        context = harness.multiprocessing.get_context("spawn")
        def process(*args, **kwargs):
            self.assertEqual(kwargs["args"][1]["share"], .1)
            return context.Process(*args, **kwargs)
        guarded = SimpleNamespace(Pipe=context.Pipe, Process=process)
        with tempfile.TemporaryDirectory() as tmp, \
                patch.object(harness.multiprocessing, "get_context", return_value=guarded):
            args = harness.parser().parse_args(["load", "--cores", "0.1", "--duration-s", "3",
                "--period-ms", "500", "--qos", "user-initiated", "--profile", "scalar",
                "--seed", "1", "--log", str(Path(tmp) / "load.json")])
            before = resource.getrusage(resource.RUSAGE_CHILDREN)
            harness.load(args)
            after = resource.getrusage(resource.RUSAGE_CHILDREN)
            report = json.loads(Path(args.log).read_text())
        self.assertIsNone(report["error"], report["error"])
        periods = [p for worker in report["workers"] for p in worker["periods"]]
        claimed_s = sum(p["cpu_used_s"] for p in periods)
        fraction = claimed_s / args.duration_s
        charged_s = (after.ru_utime + after.ru_stime) - (before.ru_utime + before.ru_stime)
        # The controller promises a measured CPU ceiling and never catches up; it
        # promises nothing about CPU the scheduler declines to hand out (D5-T1,
        # cold-gate ruling 10 + refutation 12). Delivery is reported, never asserted;
        # budgeting is proved by test_cpu_budget_overshoot_and_frozen_duty.
        self.assertLessEqual(fraction, .1 + .04, f"over-burned: {fraction:.4f} cores")
        for period in periods:
            self.assertLessEqual(period["cpu_used_s"],
                period["budget_cpu_s"] + period["overshoot_bound_cpu_s"] + 1e-9,
                f"period {period['period']} burned past its budget: {period}")
        # Kernel cross-check on the reaped child (rusage folds in at load()'s join):
        # what the worker claims can never exceed what the OS charged it, and the
        # OS-charged total is bounded by the ceiling plus the child's start-up CPU.
        self.assertGreaterEqual(charged_s, claimed_s - .01,
            f"kernel charged {charged_s:.3f} s < worker claimed {claimed_s:.3f} s")
        self.assertLessEqual(charged_s, .14 * args.duration_s + STARTUP_CPU_S,
            f"child burned {charged_s:.3f} s of kernel-accounted CPU in {args.duration_s} s")
        self.assertTrue(report["cleanup"])
        for child in report["cleanup"]:
            self.assertFalse(child["alive"])
            self.assertEqual(child["exitcode"], 0)
            with self.assertRaises(ProcessLookupError):
                os.kill(child["pid"], 0)

    def test_late_initial_scheduling_never_catches_up(self):
        clock = FakeClock(); clock.now = 2.0          # first wake 2 s after start
        periods = harness.duty_periods(.1, 3, .5, clock.burn, clock, start=0.0)
        self.assertAlmostEqual(sum(p["cpu_used_s"] for p in periods), .1, delta=.001)
        self.assertEqual([p["period"] for p in periods], [4, 5])
        self.assertLessEqual(sum(p["cpu_used_s"] for p in periods) / 3, .14)
        for p in periods:
            self.assertLessEqual(p["work_budget_cpu_s"], .1 * p["elapsed_s"] + 1e-9)
            self.assertLessEqual(p["cpu_used_s"], p["budget_cpu_s"] + p["overshoot_bound_cpu_s"] + 1e-9)
            self.assertLess(p["wake_late_s"], 1e-3)
            self.assertGreaterEqual(p["cpu_used_s"], p["work_budget_cpu_s"] - p["max_quantum_cpu_s"])
            self.assertLessEqual(p["overrun_cpu_s"], p["overshoot_bound_cpu_s"])
            self.assertAlmostEqual(p["wake_late_s"], 0.0, delta=2e-4)   # lateness is blind to this

    def test_preempted_burn_exits_on_the_wall_deadline(self):
        clock = FakeClock(); clock.ratio = 100.0      # burn advances wall 100x thread CPU
        periods = harness.duty_periods(.1, 3, .5, clock.burn, clock, start=0.0)
        self.assertAlmostEqual(sum(p["cpu_used_s"] for p in periods), .03, delta=.001)
        self.assertEqual(len(periods), 6)
        self.assertLessEqual(periods[-1]["end_mono_s"], 3.0 + 1e-9)      # window still honoured
        for p in periods:
            self.assertLessEqual(p["work_budget_cpu_s"], .1 * p["elapsed_s"] + 1e-9)
            self.assertLessEqual(p["cpu_used_s"], p["budget_cpu_s"] + p["overshoot_bound_cpu_s"] + 1e-9)
            self.assertLess(p["cpu_used_s"], p["work_budget_cpu_s"])
            self.assertLess(p["wake_late_s"], .05)

    def test_cpu_budget_overshoot_and_frozen_duty(self):
        clock = FakeClock()
        periods = harness.duty_periods(.2, 9, .1, clock.burn, clock)
        self.assertAlmostEqual(sum(p["cpu_used_s"] for p in periods), 1.8, delta=.01)
        for period in periods:
            self.assertLessEqual(period["overrun_cpu_s"], period["overshoot_bound_cpu_s"] + 1e-10)
            self.assertLess(period["overrun_cpu_s"], .0002)
            self.assertLess(period["wake_late_s"], .0002)
        frozen = [p for p in periods if not p["calibrating"]]
        self.assertGreater(len(frozen), 30)
        self.assertEqual(len({p["duty"] for p in frozen}), 1)
        self.assertEqual(len({p["batch"] for p in frozen}), 1)

    def test_stationarity_stationary_and_known_drift(self):
        periods = [{"start_mono_s": i, "end_mono_s": i + 1, "elapsed_s": 1,
                    "cpu_used_s": .2, "calibrating": False} for i in range(9)]
        result = harness.stationarity(periods, .2)
        self.assertAlmostEqual(result["mean_busy_cores"], .2)
        self.assertAlmostEqual(result["first_last_delta_cores"], 0)
        for period in periods[-3:]:
            period["cpu_used_s"] = .5
        result = harness.stationarity(periods, .2)
        self.assertAlmostEqual(result["mean_busy_cores"], .3)
        self.assertAlmostEqual(result["first_last_delta_cores"], .3)

    def test_stationarity_sums_native_processes_not_averages_them(self):
        periods = [{"start_mono_s": i, "end_mono_s": i + 1, "elapsed_s": 1,
                    "cpu_used_s": .7, "calibrating": False} for i in range(6)]
        result = harness.stationarity(periods + periods, 1.4)
        self.assertAlmostEqual(result["mean_busy_cores"], 1.4)
        self.assertAlmostEqual(result["mean_minus_setting_cores"], 0)

    def test_zero_load_sleeps_and_short_run_has_no_stationarity(self):
        clock = FakeClock()
        burn = Mock(side_effect=AssertionError("zero load cannot burn"))
        periods = harness.duty_periods(0, 2, .1, burn, clock)
        self.assertEqual(clock.monotonic(), 2)
        self.assertEqual(sum(p["cpu_used_s"] for p in periods), 0)
        self.assertIsNone(harness.stationarity(periods, 0)["mean_busy_cores"])


class SummaryTests(NetworkTimeOffMixin, unittest.TestCase):
    def test_row_os_build_cannot_be_substituted_or_joined_to_another_session(self):
        for field, replacement in (("os_build", "25G80"), ("session", "other-session")):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                harness.collect(collect_args(tmp), clock=FakeClock(), round_runner=fake_round,
                    metadata_reader=lambda: {"boot_id": "fixture", "os_build": "25G83"})
                path = Path(tmp) / "rounds.jsonl"
                rows = [json.loads(line) for line in path.read_text().splitlines()]
                rows[0][field] = replacement
                path.write_text("\n".join(json.dumps(row) for row in rows))
                before = path.read_bytes()
                with self.assertRaisesRegex(ValueError, "row/session OS build identity mismatch"):
                    harness.summarize(tmp, "idle")
                self.assertEqual(path.read_bytes(), before)
                self.assertFalse((Path(tmp) / "summary.json").exists())

    def test_summary_markdown_distinguishes_boots_and_optional_builds(self):
        for builds in (None, ("25G80", "25G83"), (None, "25G83")):
            with self.subTest(builds=builds), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                rows = [{**self.fixture_row("idle", "1", watts), "boot_id": boot,
                         "census_clean": True}
                        for boot, watts in (("A", 1), ("B", 9))]
                if builds is not None:
                    for row, build in zip(rows, builds):
                        if build is not None:
                            row["os_build"] = build
                (root / "rounds.jsonl").write_text("\n".join(json.dumps(row) for row in rows))
                harness.summarize(root, "idle")
                markdown = (root / "summary.md").read_text()
                tables = markdown.split("| State | ")[1:]
                self.assertEqual(len(tables), 3)
                for table in tables:
                    header = table.splitlines()[0]
                    self.assertIn("| boot_id |", header)
                    self.assertEqual("| os_build |" in header, builds is not None)
                    for index, boot in enumerate(("A", "B")):
                        prefix = f"| idle | 1 / True | {boot} |"
                        if builds is not None:
                            # A missing build renders as null (delta re-audit 22 R3).
                            build = "null" if builds[index] is None else builds[index]
                            prefix += f" {build} |"
                        self.assertIn(prefix, table)
                        if "| Rail |" in header:
                            self.assertIn(prefix + f" cpu_w | {(1, 9)[index]} | 10 | 0 | 9.6 |", table)

    def test_summary_never_pools_census_conditions_or_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows = []
            for clean, watts in ((True, 1), (False, 10), (None, 100)):
                for state, extra in (("idle", 0), ("loaded", 2)):
                    rows.append({**self.fixture_row(state, "1", watts + extra), "census_clean": clean})
            root = Path(tmp)
            (root / "rounds.jsonl").write_text("\n".join(json.dumps(row) for row in rows))
            result = harness.summarize(root, "idle")
            self.assertIsNone(result["reference"])
            self.assertEqual(len(result["references_by_census"]), 3)
            self.assertEqual(len(result["groups"]), 6)
            for group in result["groups"]:
                self.assertEqual(group["complete_rounds"], 1)
                if group["state"] == "loaded":
                    self.assertEqual(group["delta_j_480"]["cpu_w"], 960)
            # A missing matching reference must not borrow the clean reference.
            rows = [r for r in rows if r["state"] != "idle" or r["census_clean"] is True]
            (root / "rounds.jsonl").write_text("\n".join(json.dumps(row) for row in rows))
            result = harness.summarize(root, "idle")
            for group in result["groups"]:
                if group["census_clean"] is not True:
                    self.assertIsNone(group["delta_j_480"]["cpu_w"])
        # S5 / probe_d: summarize() must neither average 1 W and 9 W across
        # boots nor compare the second boot's load to the first boot's idle.
        for field, identities in (("boot_id", ("boot-A-macOS-25G80", "boot-B-macOS-25G83")),
                                  ("os_build", ("25G80", "25G83"))):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                rows = [{**self.fixture_row("idle", "1", watts), "boot_id": "same-boot",
                         field: value, "census_clean": True}
                        for value, watts in zip(identities, (1, 9))]
                (root / "rounds.jsonl").write_text("\n".join(json.dumps(row) for row in rows))
                result = harness.summarize(root, "idle")
                self.assertEqual(len(result["groups"]), 2)
                self.assertEqual({g[field]: g["power"]["cpu_w"] for g in result["groups"]},
                                 dict(zip(identities, (1, 9))))
                self.assertTrue(all("boot_id" in g for g in result["groups"]))
                self.assertIsNone(result["reference"])
                self.assertIn(field.replace("_id", "").replace("os_build", "OS build"),
                              result["reference_reason"])
                self.assertEqual(len(result["references_by_census"]), 2)
                rows.append({**rows[1], "state": "loaded", "power": self.fixture_row("loaded", "1", 5)["power"]})
                (root / "rounds.jsonl").write_text("\n".join(json.dumps(row) for row in rows))
                result = harness.summarize(root, "idle")
                loaded = next(g for g in result["groups"] if g["state"] == "loaded")
                self.assertEqual(loaded["delta_j_480"]["cpu_w"], -1920)
                # Without the matching reference, do not borrow another boot/build.
                (root / "rounds.jsonl").write_text("\n".join(json.dumps(row) for row in (rows[0], rows[2])))
                result = harness.summarize(root, "idle")
                loaded = next(g for g in result["groups"] if g["state"] == "loaded")
                self.assertIsNone(loaded["delta_j_480"]["cpu_w"])
                assert_null_reasons(self, result)

    def test_empty_directory_cli_writes_reasoned_null_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(harness.main(["summarize", "--in", tmp, "--reference-state", "idle"]), 0)
            summary = json.loads((Path(tmp) / "summary.json").read_text())
            self.assertEqual(summary["status"], "no_rounds")
            self.assertTrue(summary["reason"])
            self.assertEqual(summary["evidence_status"], "PROVISIONAL")
            self.assertIsNone(summary["reference"])
            self.assertEqual(summary["groups"], [])
            self.assertEqual(summary["references_by_census"], [])
            self.assertNotIn("alignment_model_reason", summary)
            assert_null_reasons(self, summary)

    def test_summary_preserves_exact_session_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            harness.collect(collect_args(tmp), clock=FakeClock(), round_runner=fake_round,
                            metadata_reader=lambda: {})
            session = json.loads((Path(tmp) / "session.json").read_text())
            result = harness.summarize(tmp, "idle")
            persisted = json.loads((Path(tmp) / "summary.json").read_text())
            # S4 / probe_a A: summarize() must remove reasons for resolved siblings.
            for key in ("reference", "alignment_model"):
                self.assertIsNotNone(result[key])
                self.assertNotIn(key + "_reason", result)
                self.assertNotIn(key + "_reason", persisted)
            for key in ("evidence_status", "alignment_model", "network_time_provenance",
                        "network_time_provenance_reason"):
                self.assertEqual(result[key], session[key])
                self.assertEqual(persisted[key], session[key])
                self.assertEqual(persisted["session_provenance"][0][key], session[key])

    def fixture_row(self, state, repeat, watts, coverage=10, busy=.2, setting=.2, status="complete"):
        return {"schema": harness.SCHEMA, "state": state, "repeat": repeat, "session": "fixture",
                "status": status, "load_setting": setting, "observer_cpu_s": .5,
                "observation": {"metrics": {"busy_cores": busy, "host_busy_cores": busy - .01}},
                "power": {**{r: watts for r in harness.RAILS}, "coverage_s": coverage},
                "alignment": {"rail_error_bound_j": {r: .1 for r in harness.RAILS}}}

    def test_quantiles(self):
        result = harness.quantiles([0, 10, 20])
        self.assertEqual(result, {"min": 0, "p10": 2, "p50": 10, "p90": 18, "max": 20})

    def test_hand_computed_delta_coverage_bound_and_disagreements(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rows = [self.fixture_row("idle", "1", 1, coverage=10),
                    self.fixture_row("idle", "2", 3, coverage=30),
                    self.fixture_row("loaded", "1", 5, coverage=20, busy=.3),
                    self.fixture_row("loaded", "1", 99, status="partial")]
            (root / "rounds.jsonl").write_text("\n".join(json.dumps(row) for row in rows))
            result = harness.summarize(root, "idle")
            loaded = next(g for g in result["groups"] if g["state"] == "loaded")
            # Reference = (1*10+3*30)/40 = 2.5 W; 480*(5-2.5)=1200 J.
            self.assertEqual(loaded["delta_j_480"]["cpu_w"], 1200)
            self.assertAlmostEqual(loaded["delta_alignment_bound_j_480"]["cpu_w"], 480 * (.1 / 20 + .2 / 40))
            self.assertEqual(loaded["coverage_s"]["cpu_w"], 20)
            self.assertEqual(loaded["load_disagreement_rounds"], 1)
            self.assertEqual(loaded["load_compared_rounds"], 1)
            self.assertEqual(loaded["partial_rounds"], 1)
            self.assertEqual(loaded["quantiles"]["busy_cores"]["p50"], .3)
            self.assertIn("1200", (root / "summary.md").read_text())
            assert_null_reasons(self, json.loads((root / "summary.json").read_text()))

    def test_missing_reference_or_alignment_never_becomes_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            row = self.fixture_row("idle", "1", 1)
            row["alignment"] = {}
            row["load_setting"] = None
            (root / "rounds.jsonl").write_text(json.dumps(row))
            result = harness.summarize(root)
            self.assertIsNone(result["groups"][0]["delta_j_480"]["cpu_w"])
            result = harness.summarize(root, "idle")
            self.assertIsNone(result["groups"][0]["delta_alignment_bound_j_480"]["cpu_w"])
            self.assertEqual(result["groups"][0]["load_compared_rounds"], 0)
            with self.assertRaisesRegex(ValueError, "absent"):
                harness.summarize(root, "missing")
            # N2: aggregate() sees a foreign truthy observation with no busy_cores;
            # refuse with ValueError rather than leaking a KeyError from indexing.
            for observation in ({"foreign": True}, {"metrics": {}}):
                row.update(observation=observation, load_setting=.2)
                with self.assertRaisesRegex(ValueError, "busy_cores"):
                    harness.aggregate([row])


if __name__ == "__main__":
    unittest.main()


class NativeInteriorAndLoadJoinTests(NetworkTimeOffMixin, unittest.TestCase):
    def test_interior_uses_native_support_not_scaled_whole_envelope_mean(self):
        frames = aligned_fixture()
        anchor = {'status':'bounded','effective_clock_anchor_bound_s':0}
        value = harness.reduce_interior(frames, anchor, 1001, 2)
        self.assertTrue(value['complete_support'])
        self.assertAlmostEqual(value['power']['energy_j']['rail_sum_w'], 9.2)
        self.assertNotAlmostEqual(value['power']['energy_j']['rail_sum_w'], (2.6+9.2)/3*2)
        partial = harness.reduce_interior(frames, anchor, 1001, 3)
        self.assertFalse(partial['complete_support'])
        self.assertEqual(partial['status'], 'partial')
        self.assertAlmostEqual(partial['power']['energy_j']['rail_sum_w'], 9.2)
        frames[1]['power']['ane_w'] = frames[1]['power']['rail_sum_w'] = None
        self.assertFalse(harness.reduce_interior(frames, anchor, 1001, 2)['complete_support'])
        self.assertFalse(harness.reduce_interior(frames, {'status':'unresolved'}, 1001, 2)['complete_support'])

    def fixture(self):
        row = {'boot_id':'boot','alignment':{'ps_start':10.,'ps_end':20.}}
        identity = {'pid':42,'start_identity':'identity-A'}
        report = {'boot_id':'boot','error':None,'cleanup':[{'pid':42,'alive':False,'exitcode':0}],'workers':[{'identity':identity,'periods':[
            {'start_mono_s':5.,'end_mono_s':15.,'cpu_used_s':2.},
            {'start_mono_s':15.,'end_mono_s':25.,'cpu_used_s':4.}]}]}
        before = {(42,'identity-A'):{'cumulative_cpu_seconds':1.}}
        after = {(42,'identity-A'):{'cumulative_cpu_seconds':4.}}
        return row, report, before, after

    def test_load_join_matches_worker_identity_and_exact_monotonic_overlap(self):
        value = harness.join_load_log(*self.fixture())
        self.assertEqual(value['status'], 'joined')
        self.assertAlmostEqual(value['delivered_busy_cores'], .3)
        self.assertAlmostEqual(value['sampled_busy_cores'], .3)

    def test_reused_pid_wrong_boot_and_partial_load_support_do_not_join(self):
        row, report, before, after = self.fixture()
        wrong = {(42,'identity-B'):{'cumulative_cpu_seconds':4.}}
        self.assertEqual(harness.join_load_log(row,report,before,wrong)['status'], 'unresolved')
        report['boot_id']='another-boot'
        self.assertEqual(harness.join_load_log(row,report,before,after)['status'], 'unresolved')
        report['boot_id']='boot'
        report['workers'][0]['periods'].pop()
        value = harness.join_load_log(row,report,before,after)
        self.assertEqual(value['status'], 'unresolved')
        self.assertEqual(value['workers'][0]['support_s'], 5)

    def test_overlapping_load_periods_refuse_double_counting(self):
        row, report, before, after = self.fixture()
        report['workers'][0]['periods'][1]['start_mono_s']=14.
        with self.assertRaisesRegex(ValueError,'overlapping'):
            harness.join_load_log(row,report,before,after)

    def test_calibrating_periods_and_failed_cleanup_do_not_qualify_as_delivered_support(self):
        row, report, before, after = self.fixture()
        report['workers'][0]['periods'][0]['calibrating'] = True
        result = harness.join_load_log(row,report,before,after)
        self.assertEqual(result['status'], 'unresolved')
        self.assertEqual(result['workers'][0]['calibration_overlap_s'], 5)
        report['cleanup'] = [{'alive':True,'exitcode':None}]
        self.assertEqual(harness.join_load_log(row,report,before,after)['reason'], 'load cleanup incomplete or escalated')


# --------------------------------------------------------------------------
# A267 QPE01-CLOCK-DISCIPLINE-ANCHOR-01 — cold-gate regressions 6 and 9
# (ruling 10 Q3 as worded by 14 R5; Q1 rule 3).  Envelope 11 of the pilot
# night qpe01-pilot-n1-20260922-0217 is the real mis-tiled capture.
# --------------------------------------------------------------------------

PILOT_FIXTURES = Path(__file__).resolve().parent / "fixtures" / "qpe01_pilot_n1_20260922"


def pilot_envelope(index):
    return json.loads((PILOT_FIXTURES / f"envelope-{index:02d}.json").read_text())


def pilot_frames(fixture):
    """Parsed-frame dicts rebuilt from the archived native rows."""
    frames = []
    for elapsed_ns, native_ns, rail_sum_w, energy_j, is_delta in fixture["records"]:
        power = dict.fromkeys(harness.RAILS)
        power["rail_sum_w"] = power["combined_w"] = rail_sum_w
        frames.append({"native_timestamp_s": native_ns / 1e9,
                       "native_timestamp_ns": native_ns, "elapsed_ns": elapsed_ns,
                       "elapsed_s": elapsed_ns / 1e9, "is_delta": is_delta,
                       "energy_j": energy_j, "power": power,
                       "clusters": [], "cpus": []})
    return frames


def pilot_interior_epoch(fixture):
    interior = fixture["interior"]
    return (interior["start_stamp"]["epoch_s"] - (interior["start_drift_s"] or 0)
            + interior["interior_offset_s"])


class ExactTilingTests(unittest.TestCase):
    """Regression 6: envelope 11's interior covers exactly 480 s, or it does not."""

    def envelope_eleven(self):
        fixture = pilot_envelope(11)
        stamps = {name: harness.ClockStamp(**value)
                  for name, value in fixture["clock_stamps"].items()}
        aligned, anchor = harness.align_frames(pilot_frames(fixture), stamps)
        return fixture, aligned, anchor

    def test_envelope_eleven_interior_covers_exactly_four_hundred_eighty_seconds(self):
        fixture, aligned, anchor = self.envelope_eleven()
        self.assertEqual(anchor["status"], "bounded", anchor.get("detail"))
        interior = harness.reduce_interior(
            aligned, anchor, pilot_interior_epoch(fixture),
            fixture["interior"]["interior_s"])
        # The night recorded span_mismatch True and error_bound_j None for this
        # envelope; under exact tiling the coverage is the integer 480 s and the
        # conservative energy bound exists.
        self.assertFalse(interior["span_mismatch"])
        self.assertEqual(interior["coverage_ns"], 480_000_000_000)
        self.assertEqual(interior["rail_coverage_ns"]["rail_sum_w"], 480_000_000_000)
        self.assertIsNotNone(interior["error_bound_j"])
        self.assertTrue(interior["complete_support"])
        self.assertEqual(interior["status"], "complete")

    def test_one_nanosecond_of_missing_support_is_a_gap_not_a_rounding_error(self):
        fixture, aligned, anchor = self.envelope_eleven()
        epoch = pilot_interior_epoch(fixture)
        duration = fixture["interior"]["interior_s"]
        start_ns = round(epoch * 1e9)
        index = next(i for i, frame in enumerate(aligned)
                     if frame["start_ns"] > start_ns + 1_000_000_000)
        mutated = list(aligned)
        # One frame reports one nanosecond less support than it tiles: the
        # exact comparator must see the hole.  A 1 microsecond float tolerance
        # would not.
        mutated[index] = {**mutated[index],
                          "start_ns": mutated[index]["start_ns"] + 1,
                          "start_s": (mutated[index]["start_ns"] + 1) / 1e9}
        interior = harness.reduce_interior(mutated, anchor, epoch, duration)
        self.assertTrue(interior["span_mismatch"])
        self.assertEqual(interior["coverage_ns"], 480_000_000_000 - 1)
        self.assertIsNone(interior["error_bound_j"])
        self.assertFalse(interior["complete_support"])

    def test_frames_tile_exactly_and_the_sampler_asks_for_the_v3_1_identity(self):
        from joulewise.uncertainty_evidence import CLOCK_METHOD_V3_1

        fixture, aligned, anchor = self.envelope_eleven()
        self.assertEqual(anchor["method"], CLOCK_METHOD_V3_1)
        self.assertEqual(anchor["clock_anchor_method"], CLOCK_METHOD_V3_1)
        endpoint_ns = round(anchor["first_sample_end_point_epoch_s"] * 1e9)
        self.assertEqual(aligned[0]["end_ns"], endpoint_ns)
        for left, right in zip(aligned, aligned[1:]):
            self.assertEqual(right["start_ns"], left["end_ns"])
            self.assertEqual(right["end_ns"] - right["start_ns"], right["elapsed_ns"])
        self.assertEqual(aligned[-1]["end_ns"] - aligned[0]["end_ns"],
                         sum(f["elapsed_ns"] for f in aligned[1:]))
        oracle = Mock(return_value={"status": "unknown"})
        harness.align_frames([], {}, deriver=oracle)
        self.assertEqual(oracle.call_args.kwargs["method"], CLOCK_METHOD_V3_1)


class NetworkTimeProvenanceTests(unittest.TestCase):
    """Regression on ruling 10 Q1 rule 3: no receipt, no envelope."""

    def collect(self, value, control=None):
        environment = {} if value is None else {harness.NETWORK_TIME_RECORD_ENV: str(value)}
        with tempfile.TemporaryDirectory(dir="/tmp") as tmp, \
                patch.dict(os.environ, environment, clear=False), \
                patch.object(harness, "PowerRecorder",
                             side_effect=AssertionError("powermetrics must not be spawned")):
            if value is None:
                os.environ.pop(harness.NETWORK_TIME_RECORD_ENV, None)
            args = collect_args(tmp, power=True)
            session, rows = harness.collect(args, clock=FakeClock(),
                                            round_runner=fake_round,
                                            metadata_reader=lambda: {})
            persisted = json.loads((Path(tmp) / "session.json").read_text())
            plists = list((Path(tmp) / "raw").rglob("*.plist"))
            return session, rows, persisted, plists

    def test_absent_unreadable_and_inexact_receipts_each_refuse_the_envelope(self):
        cases = {}
        with tempfile.TemporaryDirectory(dir="/tmp") as tmp:
            lower = network_time_control(tmp, stdout="setUsingNetworkTime: off\n")
            cases["lower case stdout"] = str(lower)
            failed = Path(tmp) / "failed.json"
            failed.write_text(network_time_control(tmp, exit_code=1).read_text())
            cases["nonzero exit"] = str(failed)
            cases["absent variable"] = None
            cases["unreadable record"] = str(Path(tmp) / "does-not-exist.json")
            for label, value in cases.items():
                with self.subTest(case=label):
                    session, rows, persisted, plists = self.collect(value)
                    self.assertEqual(rows, [])
                    self.assertIsNone(session["network_time_provenance"])
                    self.assertEqual(session["error_class"], harness.NETWORK_TIME_REFUSAL)
                    self.assertIn("network time provenance not established",
                                  session["error"])
                    self.assertEqual(persisted["error"], session["error"])
                    self.assertFalse(plists)

    def test_the_chain_receipt_becomes_structured_provenance_on_the_session(self):
        with tempfile.TemporaryDirectory(dir="/tmp") as tmp:
            record = network_time_control(tmp)
            with patch.dict(os.environ,
                            {harness.NETWORK_TIME_RECORD_ENV: str(record)}), \
                    tempfile.TemporaryDirectory(dir="/tmp") as out:
                session, rows = harness.collect(collect_args(out), clock=FakeClock(),
                                                round_runner=fake_round,
                                                metadata_reader=lambda: {})
            provenance = session["network_time_provenance"]
            self.assertEqual(provenance["state"], "off")
            self.assertEqual(provenance["method"],
                             "systemsetup_setusingnetworktime_off_exact_stdout")
            self.assertEqual(provenance["record"], "network_time_control.json")
            self.assertEqual(provenance["record_sha256"],
                             harness.hashlib.sha256(record.read_bytes()).hexdigest())
            self.assertEqual(provenance["established_epoch_s"], 1000.0)
            self.assertEqual(session["network_time_provenance_reason"],
                             "established by the evidence chain before settle")
            self.assertIsNone(session["error"])
            self.assertTrue(rows)

    def test_the_command_line_maps_the_refusal_to_its_own_exit_code(self):
        with tempfile.TemporaryDirectory(dir="/tmp") as tmp:
            os.environ.pop(harness.NETWORK_TIME_RECORD_ENV, None)
            code = harness.main(["collect", "--no-power", "--out", tmp, "--state", "idle",
                                 "--repeat", "1", "--duration-s", "1",
                                 "--sample-interval-s", "1"])
        self.assertEqual(code, harness.NETWORK_TIME_REFUSAL_EXIT)
        self.assertEqual(code, 3)
