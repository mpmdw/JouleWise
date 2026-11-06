"""WP15 R1 runtime: contract conformance, read-back rules and signal handling.

Synthetic only (``tests.align.r1_synthetic``): fake clock, SMC transport, PM
status, powermetrics-labelled GPU rail, native mlx_lm stream, ``ps`` and
``pmset``. No model, sensor or host setting is touched.
"""
from __future__ import annotations

import io
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock
from types import SimpleNamespace

from joulewise.align.apple import r1_runtime as rt
from joulewise.align.apple import r1_runtime_contract as contract
from scripts import align_r1_rehearsal as r1
from tests.align import r1_synthetic as rs

REPO = Path(__file__).resolve().parents[2]
NS = rt.NS
TMP = os.environ.get("TMPDIR")


def call(config, out, kind, *extra):
    buffer = io.StringIO()
    code = rt.main(["--config", str(config), "--r1-kind", kind, "--output", str(out), *extra], stdout=buffer)
    return code, (json.loads(buffer.getvalue()) if code == 0 else None)


def custody(out):
    return json.loads((Path(out) / rt.CUSTODY_NAME).read_text())


class ConformanceTests(unittest.TestCase):
    """Every driver kind, run by the runtime against the fake backend, returns
    its contract fields and passes the driver's own validators."""

    def test_every_kind_conforms_and_feeds_the_driver(self):
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            root = Path(td)
            config = rs.synthetic_config(root / "cfg", decline_after_s=120.0)
            run = root / "r1"
            run.mkdir()
            results = {}

            def segment(name, kind, *extra, soak=True):
                args = list(extra)
                if soak:
                    args += ["--soak-reference", str(run / "soak_reference.json")]
                code, result = call(config, run / name, kind, *args)
                self.assertEqual(code, 0, custody(run / name).get("error"))
                quiet = kind in r1.QUIET_KINDS
                key = "idle_soak" if name == "idle_soak" else None
                self.assertEqual(contract.missing_fields(kind, result, quiet=True, contract_key=key), [], kind)
                if quiet:
                    r1.os_load_verdict(name, result)
                record = custody(run / name)
                self.assertEqual(record["status"], "complete")
                self.assertEqual(record["files"][rt.RESULT_NAME],
                                 rt.sha256_file(run / name / rt.RESULT_NAME))
                results[name] = result
                return result

            segment("pre_calibration_bracket", "calibration-pre", soak=False)
            soak = segment("idle_soak", "idle", "--duration-s", "1300", soak=False)
            detrended = r1.soak_detrended(soak["sensor_series_c"])
            r1.write_soak_reference(run, {"name": "idle_soak", "output_dir": str(run / "idle_soak"),
                                          "attempt": 0, "soak_detrended": detrended})
            segment("step_30b", "step-30b")
            step = segment(rt.STEP_D_SEGMENT, "step-d")
            slots = r1.derive_slots(step)
            self.assertEqual(slots["class"], "heavy")
            # decline_after_s = 120 s of decode: S9 is finite and N_chunk follows FD 2.6.
            detail = step["slot_detail"]
            self.assertEqual(detail["t_decline_status"], "declined")
            expected = max(256, 256 * int(0.6 * slots["t_decline"] * detail["r_decode_tok_per_s"] / 256))
            self.assertEqual(slots["N_chunk"], expected)
            self.assertAlmostEqual(slots["T_dead"], (1750 - slots["I_D"]) / 1.13544)
            self.assertGreater(step["e_D_j_per_token"], 0)
            cool = segment("cooldown_after_D", "idle-until-soak", "--duration-s", "1500")
            self.assertTrue(cool["recovery_curve"])
            segment("X_G_contrast", "x-g")
            gated = {}
            for name, kind in r1.GATED_D_RUNS:
                gated[name] = segment(name, kind)
                r1._check_gated_t_dead(name, gated[name], step)
                r1.deadman_summary(name, gated[name])
            planning = [segment(f"planning_turn_R_plus_{o}C", f"d-planning-turn-r-plus-{o}c") for o in (0, 2, 4)]
            summary = r1.planning_temperature_summary(planning)
            self.assertEqual(len(summary["points"]), 3)
            r1.u5_verdict(summary, gated)
            r1.projected_mde(step["e_D_j_per_token"], gated)
            release = segment("high_power_A1.g0_release0", "g0-release-soak")
            self.assertIs(release["released"], True)
            legs = [segment(f"high_power_{leg}", f"high-power-aba-{leg.lower()}")["t_decline_s"]
                    for leg in ("A1", "B", "A2")]
            r1.high_power_adoption(*legs)
            segment("post_calibration_bracket", "calibration-post", soak=False)
            harvested = segment("harvest", "harvest")
            battery = r1.battery_report(results, harvested)
            self.assertGreater(battery["drain_pct_per_h"]["D"], 0)
            self.assertGreater(battery["drain_pct_per_h"]["30B"], 0)
            self.assertIsNone(battery["charge_resume_soc_pct"])
            # Every runtime wrote only inside its own segment directory.
            self.assertEqual(sorted(p.name for p in run.iterdir()),
                             sorted([*results, "soak_reference.json"]))

    def test_pending_inputs_refuse_before_work_with_a_terminal_record(self):
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            root = Path(td)
            production = REPO / "configs/align/v4/r1_runtime.json"
            code, _ = call(production, root / "idle", "idle", "--duration-s", "5")
            self.assertEqual(code, rt.EXIT_REFUSED)
            self.assertIn("PENDING R0", custody(root / "idle")["error"])
            config = rs.synthetic_config(root / "cfg")
            code, _ = call(config, root / "g0", "g0-release-soak")
            self.assertEqual(code, rt.EXIT_REFUSED)
            self.assertIn("--soak-reference", custody(root / "g0")["error"])
            code, _ = call(config, root / "bank", "d-bank-benign-s1", "--soak-reference", str(root / "none.json"))
            self.assertEqual(code, rt.EXIT_REFUSED)
            self.assertIn("unreadable", custody(root / "bank")["error"])
            (root / "exists").mkdir()
            code, _ = call(config, root / "exists", "calibration-pre")
            self.assertEqual(code, rt.EXIT_REFUSED)
            self.assertFalse((root / "exists" / rt.CUSTODY_NAME).exists())

    def test_production_templates_refuse_pending_r0_effort_and_wp18_turns(self):
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            root = Path(td)
            production = json.loads((REPO / "configs/align/v4/r1_runtime.json").read_text())
            for key in ("d_spam", "d_bank"):
                _, spec = rt.read_template(production["templates"][key])
                with self.assertRaisesRegex(rt.Refused, "PENDING R0"):
                    rt.require_effort(spec, key)
            # The kit leaves X-G max_turns pending until WP18; the runtime refuses it.
            config = rs.synthetic_config(root / "cfg", )
            data = json.loads(config.read_text())
            data["templates"]["x_g"] = production["templates"]["x_g"]
            config.write_text(json.dumps(data))
            (root / "r1" / rt.STEP_D_SEGMENT).mkdir(parents=True)
            (root / "r1" / rt.STEP_D_SEGMENT / rt.RESULT_NAME).write_text(json.dumps(
                {"kind": "step-d", "slots": {"S7": 30.0}}))
            soak = root / "soak.json"
            soak.write_text(json.dumps({"schema": rt.SOAK_REFERENCE_SCHEMA,
                                        "sensors_c": {rs.syn.FAST: 38.0, rs.syn.SLOW: 38.0},
                                        "detrended": {k: {"detrended_sd_c": 0.1} for k in (rs.syn.FAST, rs.syn.SLOW)}}))
            code, _ = call(config, root / "r1" / "X_G_contrast", "x-g", "--soak-reference", str(soak))
            self.assertEqual(code, rt.EXIT_REFUSED)
            self.assertIn("PENDING WP18", custody(root / "r1" / "X_G_contrast")["error"])


class ReadBackTests(unittest.TestCase):
    def test_terminal_custody_includes_nested_file_with_same_basename(self):
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            out = Path(td)
            nested = out / "runs/member" / rt.CUSTODY_NAME
            nested.parent.mkdir(parents=True)
            nested.write_text("nested bundle custody\n")
            rt.write_custody(out, {"status": "complete"})
            self.assertEqual(custody(out)["files"][f"runs/member/{rt.CUSTODY_NAME}"],
                             rt.sha256_file(nested))

    def test_step_d_consumer_requires_complete_digest_bound_custody(self):
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            root = Path(td)
            step_dir = root / rt.STEP_D_SEGMENT
            step_dir.mkdir()
            result = step_dir / rt.RESULT_NAME
            result.write_text(json.dumps({"kind": "step-d", "slots": {"T_dead": 10, "B_D": 1024}}))
            segment = SimpleNamespace(out=root / "consumer", kind="d-spam-benign-s1-a")
            with self.assertRaisesRegex(rt.Refused, "result and custody"):
                rt.Segment.step_d_result(segment)
            rt.write_custody(step_dir, {"status": "complete"})
            self.assertEqual(rt.Segment.step_d_result(segment)["kind"], "step-d")
            result.write_text(json.dumps({"kind": "step-d", "slots": {"T_dead": 11, "B_D": 1024}}))
            with self.assertRaisesRegex(rt.Refused, "complete runtime custody"):
                rt.Segment.step_d_result(segment)

    def test_gated_deadman_refuses_invalid_time_and_decode_budget_before_model(self):
        segment = object.__new__(rt.Segment)
        segment.kind = "d-spam-benign-s1-a"
        segment.step_d_result = mock.Mock(return_value={"slots": {"T_dead": float("nan"), "B_D": 1024}})
        segment.template = mock.Mock(return_value=({}, {}))
        with self.assertRaisesRegex(rt.Refused, "T_dead"):
            segment.k_gated_d()
        segment.step_d_result.return_value = {"slots": {"T_dead": 10.0, "B_D": 1025}}
        with self.assertRaisesRegex(rt.Refused, "B_D"):
            segment.k_gated_d()

    def test_managed_session_closes_all_collectors_once_even_after_failure(self):
        calls = []

        class Session:
            def close(self):
                calls.append("session")
                raise RuntimeError("SMC close failed")

        managed = rt.ManagedSession(Session(), closers=(lambda: calls.append("powermetrics"),),
                                    on_close=lambda: calls.append("unregister"))
        with self.assertRaisesRegex(RuntimeError, "SMC close failed"):
            managed.close()
        managed.close()
        self.assertEqual(calls, ["unregister", "session", "powermetrics"])

    def test_pmset_batt_parsing(self):
        parse = rt.parse_pmset_batt
        head = "Now drawing from 'AC Power'\n"
        self.assertEqual(parse(head + " -InternalBattery-0 (id=4653155)\t95%; AC attached; not charging present: true\n"),
                         {"soc_pct": 95, "state": "not_charging", "ac": True})
        self.assertEqual(parse(head + " -InternalBattery-0 (id=1)\t87%; charging; 1:02 remaining present: true\n")["state"],
                         "charging")
        self.assertEqual(parse(head + " -InternalBattery-0 (id=1)\t99%; finishing charge; present: true\n")["state"],
                         "charging")
        self.assertEqual(parse(head + " -InternalBattery-0 (id=1)\t100%; charged; 0:00 remaining present: true\n")["state"],
                         "charged")
        battery = parse("Now drawing from 'Battery Power'\n -InternalBattery-0 (id=1)\t50%; discharging; 3:00 remaining\n")
        self.assertEqual((battery["soc_pct"], battery["state"], battery["ac"]), (50, "discharging", False))
        self.assertEqual(parse("garbage")["soc_pct"], None)

    def test_battery_drain_rate_and_charge_resume(self):
        rows = [{"epoch_s": 3600.0 * h, "soc_pct": soc, "state": state} for h, soc, state in (
            (0.0, 100, "discharging"), (0.5, 97, "discharging"), (1.0, 94, "discharging"),
            (1.5, 94, "charging"), (2.0, 97, "charging"))]
        summary = rt.battery_summary(rows)
        self.assertAlmostEqual(summary["drain_pct_per_h"], 6.0)
        self.assertEqual(summary["charge_resume_soc_pct"], 94)
        self.assertEqual(summary["charge_resume_events"][0]["prior_soc_pct"], 94)
        charging = rt.battery_summary([{"epoch_s": 0.0, "soc_pct": 90, "state": "charging"},
                                       {"epoch_s": 60.0, "soc_pct": 91, "state": "charging"}])
        self.assertIsNone(charging["drain_pct_per_h"])
        self.assertEqual(charging["drain_unavailable_reason"], "charging_throughout")

    def test_t_decline_rule_and_unobserved_is_not_no_decline(self):
        turn = SimpleNamespace(start_ns=0, first_token_ns=5 * NS, end_ns=200 * NS)

        def rows(clocks):
            return [{"start_ns": (5 + i) * NS, "end_ns": (6 + i) * NS, "clock_mhz": c} for i, c in enumerate(clocks)]
        steady = [1400.0] * 10
        # One dip is not a decline; two consecutive samples below 0.97 x median are.
        value, status = rt.t_decline(rows(steady + [1300.0, 1400.0, 1350.0, 1350.0, 1300.0]), turn)
        self.assertEqual(status, "declined")
        self.assertEqual(value, 18.0)   # end of the first of the two samples (index 12), from step start
        self.assertEqual(rt.t_decline(rows(steady + [1390.0] * 5), turn), (None, "no_decline"))
        self.assertEqual(rt.t_decline([], turn), (None, "unobserved"))
        self.assertEqual(rt.t_decline(rows([None] * 12), turn), (None, "unobserved"))

    def test_step_d_slot_rules(self):
        turn = SimpleNamespace(start_ns=100 * NS, first_token_ns=120 * NS, end_ns=520 * NS,
                               decode_tokens=4000, prefill_tokens=10000)
        ep = SimpleNamespace(start_ns=100 * NS, end_ns=525 * NS, hardware={"thermal": {"intervals": [
            {"kind": "G0", "start_ns": 40 * NS, "end_ns": 100 * NS, "duration_s": 60.0}]}})
        response = {"key": "K", "delta_t_c": 5.0, "t63_s": 3.0, "tau_s": 80.0, "peak_ns": 0}
        bands = {"delta_fast_c": 1.2, "delta_slow_c": 1.5}
        slots, detail = rt.derive_step_d_slots(
            ep=ep, turn=turn, wall_s=800.0, responses={"s_fast": response, "s_slow": response},
            recovery_s=50.0, recovery_censored=False, bands=bands, t_decline_s=200.0,
            t_decline_status="declined", d_class="heavy")
        i_d = 800.0 - 485.0
        self.assertAlmostEqual(slots["I_D"], i_d)
        self.assertAlmostEqual(slots["T_dead"], (1750 - i_d) / 1.13544)
        self.assertEqual(slots["N_chunk"], 256 * int(0.6 * 200.0 * 10.0 / 256))   # r_decode = 10 tok/s
        self.assertEqual(slots["B_D"], 1024 * int(((1800 - i_d) / 1.13544 - 20.0) * 10.0 / 1024))
        self.assertEqual((slots["S5"], slots["S7"], slots["S9"]), (1.5, 150.0, 200.0))
        self.assertEqual(r1.derive_slots({"slots": slots})["class"], "heavy")
        censored, detail = rt.derive_step_d_slots(
            ep=ep, turn=turn, wall_s=800.0, responses={"s_fast": response, "s_slow": response},
            recovery_s=200.0, recovery_censored=True, bands=bands, t_decline_s=None,
            t_decline_status="no_decline", d_class="heavy")
        self.assertEqual((censored["N_chunk"], censored["S7"], censored["t_decline"]), (2048, 300.0, 400.0))
        self.assertTrue(detail["t_decline_censored"])

    def test_episode_phases_split_holds_out_of_decode(self):
        from joulewise.align.records import ToolCall
        tool = ToolCall(name="act", start_ns=60 * NS, end_ns=62 * NS, args_bytes=1, result_bytes=1,
                        state_changed=None, state_before_sha256=None, state_after_sha256=None)
        turns = [SimpleNamespace(index=0, start_ns=10 * NS, first_token_ns=15 * NS, end_ns=60 * NS, tool_calls=(tool,)),
                 SimpleNamespace(index=1, start_ns=70 * NS, first_token_ns=72 * NS, end_ns=100 * NS, tool_calls=())]
        intervals = [{"kind": "G0", "duration_s": 30.0, "turn": 0, "start_ns": 0, "end_ns": 0},
                     {"kind": "H", "duration_s": 8.0, "turn": 0, "start_ns": 30 * NS, "end_ns": 38 * NS},
                     {"kind": "G1", "duration_s": 8.0, "turn": 1, "start_ns": 62 * NS, "end_ns": 70 * NS}]
        ep = SimpleNamespace(turns=turns, end_ns=104 * NS, hardware={
            "thermal": {"intervals": intervals}, "token_budget": {"deadline_ns": 101 * NS}})
        phases = rt.episode_phases(ep)
        self.assertEqual(phases, {"G0": 30.0, "G1": 8.0, "H": 8.0, "prefill": 7.0, "decode": 45.0 - 8.0 + 28.0,
                                  "tool": 2.0, "tail": 3.0})


RUNTIME = [sys.executable, "-B", str(REPO / "scripts/align_r1_runtime.py")]


class SignalTests(unittest.TestCase):
    def start(self, config, out, kind, *extra, ready):
        process = subprocess.Popen([*RUNTIME, "--config", str(config), "--r1-kind", kind, "--output", str(out),
                                    *extra], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        deadline = time.monotonic() + 120
        while not ready() and time.monotonic() < deadline:
            if process.poll() is not None:
                self.fail(f"runtime exited early: {process.communicate()}")
            time.sleep(0.1)
        self.assertTrue(ready(), "runtime never reached the signal point")
        return process

    def stop(self, process, sig=signal.SIGTERM):
        process.send_signal(sig)
        started = time.monotonic()
        stdout, stderr = process.communicate(timeout=30)
        return time.monotonic() - started, stdout, stderr

    def test_term_during_a_sensor_segment_closes_collectors_and_writes_custody(self):
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            root = Path(td)
            config = rs.synthetic_config(root / "cfg")
            out = root / "idle"
            journal = out / "sensors" / "align_thermal.jsonl"
            process = self.start(config, out, "idle", "--duration-s", "100000000",
                                 ready=lambda: journal.exists() and journal.stat().st_size > 2000)
            elapsed, stdout, stderr = self.stop(process)
            self.assertEqual(process.returncode, 128 + signal.SIGTERM, stderr)
            self.assertLess(elapsed, 20)
            self.assertEqual(stdout, "")                       # no partial result for the driver
            record = custody(out)
            self.assertEqual((record["status"], record["signal"]), ("aborted", signal.SIGTERM))
            last = json.loads(journal.read_text().splitlines()[-1])
            self.assertEqual(last["kind"], "session_end")      # SMC sidecar closed, journal final
            self.assertEqual(record["files"]["sensors/align_thermal.jsonl"], rt.sha256_file(journal))
            self.assertIn("load_journal.json", record["files"])

    def test_term_during_a_model_member_lets_the_controller_finalize_the_bundle(self):
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            root = Path(td)
            config = rs.synthetic_config(root / "cfg")
            soak = root / "soak.json"
            soak.write_text(json.dumps({"schema": rt.SOAK_REFERENCE_SCHEMA,
                                        "sensors_c": {rs.syn.FAST: 38.0, rs.syn.SLOW: 38.0},
                                        "detrended": {k: {"detrended_sd_c": 0.1} for k in (rs.syn.FAST, rs.syn.SLOW)}}))
            out = root / "leg"
            bundle = out / "runs" / "align-v4-r1-high-power-aba-a1"
            process = self.start(config, out, "high-power-aba-a1", "--soak-reference", str(soak),
                                 ready=lambda: (bundle / "outputs" / "align_thermal.jsonl").exists())
            elapsed, stdout, stderr = self.stop(process)
            self.assertEqual(process.returncode, 128 + signal.SIGTERM, stderr)
            self.assertLess(elapsed, 20)
            self.assertEqual(custody(out)["status"], "aborted")
            self.assertTrue((bundle / "summary_metrics.json").exists(), "controller did not finalize the bundle")
            last = json.loads((bundle / "outputs/align_thermal.jsonl").read_text().splitlines()[-1])
            self.assertEqual(last["kind"], "session_end")

    def test_term_during_powermetrics_start_still_stops_the_sampler(self):
        from unittest.mock import patch
        calls = []

        class Adapter:
            def __init__(self, clock):
                pass

            def start_sampling(self, config, context):
                calls.append("start")          # the sudo powermetrics child exists from here
                raise SystemExit(128 + signal.SIGTERM)

            def stop_sampling(self, config, context):
                calls.append("stop")
                return []
        backend = rt.ProductionBackend(json.loads((REPO / "configs/align/v4/r1_runtime.json").read_text()))
        sensors = {"s_fast": rs.syn.FAST, "s_slow": rs.syn.SLOW, "fan_keys": [], "r0_sha256": "a" * 64}
        policy = rt.gate_policy(sensors, {"delta_fast_c": 1.0, "delta_slow_c": 1.0}, turn_cap_s=300,
                                chunk_tokens=256, heavy=False, per_turn=False)
        with tempfile.TemporaryDirectory(dir=TMP) as td, \
                patch("joulewise.adapters.powermetrics.PowermetricsTelemetryAdapter", Adapter), \
                self.assertRaises(SystemExit):
            backend.session(policy, Path(td) / "g0", "r1-test", pm_status=True)
        self.assertEqual(calls, ["start", "stop"])

    def test_second_signal_is_ignored_and_watchdog_bounds_teardown(self):
        exits = []
        term = rt.Termination(timeout_s=0.2, exit_now=exits.append)
        previous = {sig: signal.getsignal(sig) for sig in rt.Termination.SIGNALS}
        term.install()
        try:
            with self.assertRaises(SystemExit) as stop:
                os.kill(os.getpid(), signal.SIGTERM)
                time.sleep(1)
            self.assertEqual(stop.exception.code, 128 + signal.SIGTERM)
            os.kill(os.getpid(), signal.SIGINT)                # ignored: teardown is not interrupted
            time.sleep(0.5)
            self.assertEqual(exits, [128 + signal.SIGTERM])     # the watchdog fired
        finally:
            term.restore()
        self.assertEqual({sig: signal.getsignal(sig) for sig in previous}, previous)


if __name__ == "__main__":
    unittest.main()
