"""Offline harness checks: no root, no powermetrics, no network, no live load."""
from dataclasses import asdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import plistlib
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from scripts import sample_quiet_predicate_evidence as harness


class FakeClock:
    def __init__(self):
        self.now = 0.0
        self.used = 0.0

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
        self.now += count * .00001
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


def aligned_fixture():
    frames, _ = harness.parse_frames(stream(document(), document(timestamp=1003, elapsed_ns=2_000_000_000, cpu=4000)))
    return [{**frames[0], "start_s": 1000.0, "end_s": 1001.0},
            {**frames[1], "start_s": 1001.0, "end_s": 1003.0}]


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
            shifted = [{**f, "start_s": f["start_s"] + delta, "end_s": f["end_s"] + delta} for f in frames]
            actual = harness.integrate(shifted, 1000.5, 1002)["power"]["energy_j"]["rail_sum_w"]
            self.assertLessEqual(abs(actual - energy), reduced["error_bound_j"])

    def test_overlapping_frames_are_rejected(self):
        frames = aligned_fixture()
        frames[1]["start_s"] = 1000.9
        with self.assertRaises(ValueError):
            harness.integrate(frames, 1000.5, 1002)


class CollectionTests(unittest.TestCase):
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

    def test_completed_power_collection_reduces_each_round_after_one_finish(self):
        recorder = Mock()
        recorder.metadata = {"argv": ["fake"], "cleanup": {"returncode": 0}}
        frame = aligned_fixture()[0]
        frames = [{**frame, "start_s": 999.0, "end_s": 1006.0, "elapsed_s": 7}]
        recorder.finish.return_value = (frames, {"status": "bounded", "admissible_lower_epoch_s": 1000,
            "admissible_upper_epoch_s": 1000.002, "effective_clock_anchor_bound_s": .001, "method": "fixture"})
        with tempfile.TemporaryDirectory() as tmp:
            session, rows = harness.collect(collect_args(tmp, power=True), clock=FakeClock(),
                recorder_factory=Mock(return_value=recorder), round_runner=fake_round, metadata_reader=lambda: {})
            self.assertIsNone(session["error"])
            self.assertEqual([r["power"]["coverage_s"] for r in rows], [2, 2, 1])
            self.assertTrue(all(r["power"]["cpu_w"] == 2 for r in rows))
            self.assertTrue(all(r["alignment"]["error_bound_j"] > 0 for r in rows))

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

    def test_term_then_kill_and_reap(self):
        process = Mock()
        process.poll.return_value = None
        process.wait.side_effect = [subprocess.TimeoutExpired("fake", 5), -9]
        result = harness.stop_process(process)
        self.assertEqual(result, {"returncode": -9, "term": True, "kill": True})
        self.assertEqual(process.method_calls, [unittest.mock.call.poll(), unittest.mock.call.terminate(),
            unittest.mock.call.wait(timeout=5), unittest.mock.call.kill(), unittest.mock.call.wait(timeout=5)])

    def test_exited_recorder_is_reaped_without_signal(self):
        process = Mock()
        process.poll.return_value = 0
        process.wait.return_value = 0
        self.assertFalse(harness.stop_process(process)["term"])
        process.terminate.assert_not_called()

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


class SummaryTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
