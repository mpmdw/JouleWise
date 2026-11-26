"""Exercise the pinned serializers with in-memory inputs and synthetic clocks."""
from __future__ import annotations

import ast
from dataclasses import asdict, replace
from functools import cache
from io import BytesIO
import json
from pathlib import Path
import plistlib
import subprocess
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from joulewise.align.apple import cadence_leg, r1_runtime, thermal, thermal_gates, workload
from joulewise.b5 import driver
from joulewise.cadence_looks import admission as A, admission_journals as J
from joulewise.clock import FakeClock
from joulewise.hazards.base import Stamp
from scripts import align_r1_rehearsal, run_align_r1_smoke, run_night
from tests.align.test_cache_checkpoint import HybridAPI, fake_core, hybrid_endpoint
from tests.align.test_pilot3_cache import CacheAPI, chat, fake_endpoint

ROOT = Path(__file__).resolve().parents[2]
POLICY = {"s_fast": "TZ00", "s_slow": "TA00", "r0_sha256": "a" * 64, "fan_keys": []}
STATUS = {"os_level": 0, "pm_state": "Nominal", "pm_observed_ns": 100_000_000_000}


@cache
def source(pin, path):
    return subprocess.run(["git", "-C", str(ROOT), "show", f"{pin}:{path}"],
                          check=True, capture_output=True).stdout


def pinned_function(pin, module, name, *, owner=None):
    """Load only the named function, with the writer's ordinary dependencies."""
    path = Path(module.__file__).relative_to(ROOT).as_posix()
    tree = ast.parse(source(pin, path))
    body = next(node.body for node in tree.body if isinstance(node, ast.ClassDef) and node.name == owner) \
        if owner else tree.body
    function = next(node for node in body if isinstance(node, ast.FunctionDef) and node.name == name)
    env = vars(module).copy()
    exec(compile(ast.Module(body=[function], type_ignores=[]), f"{pin}:{path}", "exec"), env)
    return env[name]


class PinnedWriters(unittest.TestCase):
    def setUp(self):
        try:
            for pin in A.PINS:
                source(pin, "joulewise/align/apple/thermal.py")
        except subprocess.CalledProcessError:
            self.skipTest("the pinned writers are absent from this checkout's Git history")

    def same_sources(self, *paths):
        """These fixtures import the current writer only if all three pins have its exact source."""
        for path in paths:
            current = (ROOT / path).read_bytes()
            for pin in A.PINS:
                self.assertEqual(current, source(pin, path), f"{pin}:{path}")

    def test_soak_reference_accepts_each_writers_validated_policy(self):
        times = list(range(1201))
        series = {POLICY["s_fast"]: [56] * len(times), POLICY["s_slow"]: [52] * len(times)}
        for pin in A.PINS:
            validate = pinned_function(pin, thermal, "validate_policy")
            write = pinned_function(pin, align_r1_rehearsal, "write_soak_reference")
            detrend = pinned_function(pin, align_r1_rehearsal, "soak_detrended")
            detrended = detrend(series, dict.fromkeys(series, times), times[-1])
            for policy in (POLICY, {**POLICY, "fan_keys": ["F0Ac"], "record_keys": ["TZ00", "TB00"]}, None):
                with self.subTest(pin=pin, policy=policy), TemporaryDirectory() as folder:
                    result = {} if policy is None else {"sensor_roles": validate(policy)}
                    path = write(Path(folder), {"name": "idle_soak", "output_dir": "synthetic", "attempt": 0,
                                                "soak_detrended": detrended, "result": result})
                    doc = A.decode(path.read_bytes(), A.SOAK_REFERENCE)
                    self.assertEqual(doc["sensor_roles"], policy)
                    A._soak_reference(doc, A.SOAK_REFERENCE, mock=False)

    def test_soak_policy_enforces_the_same_closed_shape_as_the_writer(self):
        for changes in ({"fan_keys": "F0Ac"}, {"fan_keys": ["F0Ac", "F0Ac"]},
                        {"record_keys": ["TA00", "TA00"]}, {"s_slow": "TZ00"}, {"extra": "text"}):
            with self.subTest(changes=changes):
                policy = {**POLICY, **changes}
                with self.assertRaises(ValueError):
                    thermal.validate_policy(policy)
                doc = {"schema": A.SOAK_SCHEMA, "source_segment": "idle_soak", "source_output": "synthetic",
                       "attempt": 0, "window_s": 1200, "sensors_c": {"TZ00": 56},
                       "detrended": {"TZ00": {"mean_c": 56, "detrended_sd_c": 0, "slope_c_per_min": 0,
                                             "settled": True, "window_s": 1200, "window_reads": 1200}},
                       "sensor_roles": policy}
                with self.assertRaises(A.Refusal):
                    A._soak_reference(doc, A.SOAK_REFERENCE, mock=False)

    def test_leg_serializes_a_null_source_when_g0_capture_is_unobserved(self):
        for pin, label in A.PINS.items():
            if label == "A":
                continue
            with self.subTest(pin=pin):
                projected = leg_projection(pin)
                self.assertIsNone(projected["g0_reference_source"])
                A._result_leg(label, mock=False)(projected, "leg_record.result")

    def test_aborted_ac_mode_observation_can_report_null_without_an_exception(self):
        for pin, label in A.PINS.items():
            with self.subTest(pin=pin):
                observe = pinned_function(pin, workload, "_observe_ac_powermode", owner="EpisodeRuntimeAdapter")
                result = observe(SimpleNamespace(powermode_reader=lambda: None))
                self.assertIsNone(result["value"])
                projected = leg_projection(pin, {"ac_powermode": result, "source_member": "fixture"})
                A._result_leg(label, mock=False)(projected, "leg_record.result")

    def test_prompt_cache_final_accounting_is_a_turn_production(self):
        self.same_sources("joulewise/align/apple/endpoint.py", "joulewise/align/apple/prompt_cache.py",
                          "joulewise/adapters/mlx_runtime.py", "joulewise/align/apple/generation.py")
        api = CacheAPI()
        with patch("joulewise.align.apple.prompt_cache.native_cache_api", return_value=api):
            endpoint, _ = fake_endpoint(api)
            chat(endpoint, [1, 2, 3])
        turn, = endpoint.turn_provenance
        self.assertEqual(turn["generation"]["cache_represented_tokens_after"], 5)
        J._turns([turn], J.TURNS)

    def test_checkpoint_config_size_is_an_object_in_events_and_turns(self):
        self.same_sources("joulewise/align/apple/endpoint.py", "joulewise/align/apple/prompt_cache.py")
        config = {"model_type": "qwen3_5", "num_hidden_layers": 2, "full_attention_interval": 2,
                  "linear_num_key_heads": 2, "linear_num_value_heads": 4, "linear_key_head_dim": 8,
                  "linear_value_head_dim": 8, "linear_conv_kernel_dim": 4}
        from tests.align import test_cache_checkpoint as checkpoint_tests
        base = checkpoint_tests.base_config()
        with patch.object(checkpoint_tests, "base_config", return_value=replace(
                base, model=replace(base.model, family="qwen3_5"))), patch.dict("sys.modules", fake_core()), patch(
                "joulewise.align.apple.prompt_cache.native_cache_api", return_value=HybridAPI()):
            endpoint, _ = hybrid_endpoint(config, limit=1)
            chat(endpoint, [1, 2, 3])
        setup = next(asdict(event) for event in endpoint.events
                     if (event.phase, event.event_type) == ("generation_setup", "phase_end"))
        self.assertIsInstance(setup["metadata"]["cache_checkpoint_config_size"], dict)
        J._mlx_metadata(setup, J.EVENTS)
        J._turns(endpoint.turn_provenance, J.TURNS)

    def test_gate_with_null_entry_and_exit_values_and_observed_clock(self):
        self.same_sources("joulewise/align/apple/thermal.py", "joulewise/align/apple/thermal_gates.py")
        reader = Mock()
        reader.read.return_value = {"errors": {"TZ00": "fast unavailable", "TA00": "slow unavailable"}}
        clock = FakeClock(100.0)
        policy = r1_runtime.gate_policy(POLICY, {"delta_fast_c": 1, "delta_slow_c": 1},
                                        turn_cap_s=300, chunk_tokens=256, heavy=False, per_turn=False)
        with TemporaryDirectory() as folder:
            session = thermal_gates.ThermalSession(policy, clock, SimpleNamespace(outputs_dir=folder),
                                                   reader=reader, status_reader=lambda: STATUS)
            session.start()
            # The warmup window captured a reference before the failed reads at entry.
            session.reference = {"fast_c": 56, "slow_c": 52, "source_member": "fixture", "span_ns": [0, 1]}
            interval = session.wait("G0")
            session.close()
            rows = journal_rows(folder)
        self.assertEqual(interval["outcome"], "unobserved")
        self.assertIsNone(interval["entry_slope_c_per_min"])
        self.assertEqual(interval["entry_sensors"], {"TZ00": None, "TA00": None})
        self.assertIsNotNone(interval["exit_sample_ns"])
        J._runtime_events([asdict(event) for event in session.events], J.SALVAGE, controller=False,
                          selected=set(thermal.keys(POLICY)))
        J._thermal(rows, J.THERMAL)

    def test_read_error_text_follows_policy_order_after_json_sorting(self):
        self.same_sources("joulewise/align/apple/thermal.py")
        reader = Mock()
        reader.read.return_value = {"errors": {"TA00": "slow unavailable", "TZ00": "fast unavailable"}}
        with TemporaryDirectory() as folder:
            sidecar = sidecar_at(folder, reader=reader)
            sidecar.start(background=False)
            sidecar.tick()
            sidecar.stop()
            rows = journal_rows(folder)
        self.assertEqual(rows[1]["error"], "fast unavailable; slow unavailable")
        J._thermal(rows, J.THERMAL)

    def test_short_thermal_session_emits_null_coverage_fraction(self):
        self.same_sources("joulewise/align/apple/thermal.py")
        with TemporaryDirectory() as folder:
            sidecar = sidecar_at(folder)
            sidecar.start(background=False)
            sidecar.stop()
            rows = journal_rows(folder)
        self.assertIsNone(rows[-1]["values"]["coverage"]["all_keys"]["sample_fraction"])
        J._thermal(rows, J.THERMAL)

    def test_sidecar_persists_a_text_collector_error(self):
        self.same_sources("joulewise/align/apple/thermal.py")
        with TemporaryDirectory() as folder:
            sidecar = sidecar_at(folder)
            sidecar.start(background=False)
            with patch.object(sidecar, "tick", side_effect=RuntimeError("synthetic collector failure")):
                sidecar._loop()
            with self.assertRaises(RuntimeError):
                sidecar.stop()
            rows = journal_rows(folder)
        self.assertEqual(rows[-1]["values"]["collector_error"], "synthetic collector failure")
        J._thermal(rows, J.THERMAL)

    def test_status_can_stamp_a_frame_without_pressure_state(self):
        self.same_sources("joulewise/align/apple/thermal_gates.py")
        capture = SimpleNamespace(open=lambda _: BytesIO(plistlib.dumps({})))
        tap = thermal_gates.PowermetricsStatus(SimpleNamespace(_capture_path=capture), FakeClock(100.0),
                                               notify_reader=SimpleNamespace(read=lambda: 0))
        status = tap()
        self.assertIsNone(status["pm_state"])
        self.assertIsNotNone(status["pm_observed_ns"])
        reading = thermal.sample(None, thermal.keys(POLICY))
        J._reading({**reading, "status": status}, J.THERMAL, set(thermal.keys(POLICY)))

    def test_monitor_stop_omits_returncode_when_no_process_remains(self):
        self.same_sources("joulewise/b5/driver.py")
        with patch.object(driver, "_append_line"):
            monitor = driver.MonitorSupervisor([], night_dir=Path("unused"), popen=Mock())
            summary = monitor.stop()
        self.assertNotIn("returncode", summary["stop"])
        A._SUPERVISOR(summary, "runner_receipt.steps.result.supervisor")

    def test_monitor_exit_and_restart_keep_their_structured_records(self):
        self.same_sources("joulewise/b5/driver.py")
        with TemporaryDirectory() as folder, patch.object(driver, "_append_line"), patch.object(
                driver.time, "clock_gettime_ns", side_effect=OSError("synthetic clock failure")):
            first = SimpleNamespace(pid=100, poll=lambda: 1)
            second = SimpleNamespace(pid=101, poll=lambda: 0)
            monitor = driver.MonitorSupervisor(["synthetic"], night_dir=Path(folder),
                                               popen=Mock(side_effect=[first, second]), name="synthetic")
            self.assertTrue(monitor.start())
            monitor.last_attempt = -float("inf")
            monitor.poll()
            summary = monitor.stop()
        self.assertEqual(len(summary["gaps"]), 1)
        self.assertEqual(len(summary["exits"]), 1)
        self.assertIsNone(summary["stop"]["requested"]["monotonic_raw_ns"])
        A._SUPERVISOR(summary, "runner_receipt.steps.result.supervisor")

    def test_stop_proof_uses_reaping_as_well_as_an_empty_group(self):
        self.same_sources("scripts/run_night.py", "joulewise/b5/driver.py")
        for pin in A.PINS:
            with self.subTest(pin=pin), patch.object(run_night, "_signal_group"), patch.object(
                    run_night, "_prove_group_absent", return_value=(True, [])), patch.object(driver, "_append_line"):
                stop = pinned_function(pin, run_align_r1_smoke, "stop", owner="MeterFeed")
                monitor = driver.MonitorSupervisor([], night_dir=Path("unused"), popen=Mock())
                process = Mock(pid=100)
                process.poll.return_value = 0
                process.wait.side_effect = subprocess.TimeoutExpired("synthetic", 30)
                monitor.process, monitor.starts = process, 1
                feed = SimpleNamespace(stopped=False, stop_record=None, supervisor=monitor)
                result = stop(feed)
                self.assertEqual(result["group"], {"group_census": [], "reaped": False})
                self.assertFalse(result["proven_stopped"])
                A._result_check("stop-meter", "stop", pin=A.PINS[pin], mock=False)(result, "step.result")


def leg_projection(pin, observations=None):
    make = pinned_function(pin, cadence_leg, "k_cadence_leg", owner="CadenceLegSegment")
    hardware = observations or {}
    ep = SimpleNamespace(hardware=hardware, turns=[], flags=[])
    template = {"hardware_target": {}, "run_metadata": {}, "workload_profile": {}, "model": {}}
    member = SimpleNamespace(ep=ep, bundle=Path("example/runs/leg"), status="failed", failure_reason="unknown_error")
    segment = SimpleNamespace(
        leg={"leg_id": "L001", "campaign_id": "fixture", "prefill_chars": 500, "decode_tokens": 10,
             "seed": 1, "quiet_s": 0},
        template=lambda _: (template, {}), sensors=POLICY, bands=lambda: {"delta_fast_c": 1, "delta_slow_c": 1},
        g0_cap_s=600, armed_g0_cap_s=600, config={"step": {"deadman_s": 60}}, quiet_spans=[],
        out=Path("example"), kind="cadence-leg", g0_role="capture", span_custody=None,
        reference_hook=lambda reference, **_: reference.update(
            {"source_member": hardware["source_member"]} if "source_member" in hardware else {}),
        run_member=lambda *args: member,
    )
    keep = next(node.value for node in ast.parse(source(pin, "scripts/cadence_legs_runner.py")).body
                if isinstance(node, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "_RESULT_KEEP" for t in node.targets))
    with patch.object(r1_runtime, "journal_rows", return_value=[]):
        result = {**make(segment), "config_sha256": "a" * 64}
    return {key: result[key] for key in ast.literal_eval(keep) if key in result}


def sidecar_at(folder, *, reader=None):
    now = iter(range(1, 10))
    clocks = SimpleNamespace(monotonic_ns=lambda: next(now))
    stamp = lambda: Stamp(1, next(now), 1)
    return thermal.Sidecar(Path(folder), POLICY, reader=reader or Mock(), status_reader=lambda: STATUS,
                           ctx=SimpleNamespace(clocks=clocks, stamp=stamp))


def journal_rows(folder):
    return A.decode_lines((Path(folder) / "align_thermal.jsonl").read_bytes(), J.THERMAL)
