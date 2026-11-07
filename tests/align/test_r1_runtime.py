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
import threading
import time
import unittest
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
            config = rs.synthetic_config(root / "cfg", decline_after_s=120.0, slow_gain=0.12)
            run = root / "r1"
            run.mkdir()
            results, kinds = {}, {}

            def segment(name, kind, *extra, soak=True):
                kinds[name] = kind
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
            detrended = r1.soak_detrended(soak["sensor_series_c"], soak["sensor_series_t_s"],
                                          soak["sensor_series_end_t_s"])
            r1.write_soak_reference(run, {"name": "idle_soak", "output_dir": str(run / "idle_soak"),
                                          "attempt": 0, "soak_detrended": detrended, "result": soak})
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
            # R5-5 (protocol v4 :243-251): 300 s of quiet before the prefill, a
            # fixed 600 s recovery after the last decode, and the full-inventory
            # WP14(a) classification of the D step.
            bundle = run / rt.STEP_D_SEGMENT / step["bundle"]
            episode = json.loads((bundle / "outputs/align_episode.json").read_text())
            g0 = [r for r in episode["hardware"]["thermal"]["intervals"] if r["kind"] == "G0"][0]
            prefill_ns = episode["turns"][0]["start_ns"]
            self.assertGreaterEqual((prefill_ns - g0["end_ns"]) / NS, rt.STEP_QUIET_S)
            self.assertEqual(episode["hardware"]["token_budget"]["deadline_origin"], "R1_after_G0_release_and_quiet")
            recovery = rt.journal_rows(run / rt.STEP_D_SEGMENT / "recovery/align_thermal.jsonl")
            self.assertGreaterEqual((recovery[-1]["monotonic_ns"] - episode["turns"][0]["end_ns"]) / NS, 600)
            self.assertEqual(detail["recovery_observed_s"], 600)
            thermometry = step["thermometry"]
            self.assertEqual((thermometry["status"], thermometry["s_fast"], thermometry["s_slow"]),
                             ("pass", rs.syn.FAST, rs.syn.SLOW), thermometry)
            self.assertFalse(thermometry["sensor_pick_changed"])
            self.assertEqual(thermometry["keys_inventoried"], 4)
            saved = json.loads((run / rt.STEP_D_SEGMENT / thermometry["classification_file"]).read_text())
            body = dict(saved["classification"])
            digest = body.pop("classification_sha256")
            self.assertEqual(digest, thermometry["classification_sha256"])
            self.assertEqual(digest, __import__("hashlib").sha256(rt.canonical(body).encode()).hexdigest())
            self.assertEqual(detail["S6_tuning"]["status"], "TODO")
            self.assertEqual(results["step_30b"]["thermometry"]["for_record_only"], True)
            cool = segment("cooldown_after_D", "idle-until-soak", "--duration-s", "1500")
            self.assertTrue(cool["recovery_curve"])
            gated = {}
            soak_r = json.loads((run / "soak_reference.json").read_text())["sensors_c"][rs.syn.SLOW]
            for name, kind in r1.GATED_D_RUNS:
                # R6-1: no precool; the member's own W1 idle is the schedule.
                gated[name] = segment(name, kind)
                self.assertEqual(gated[name]["inter_member_idle_s"], 300.0)
                self.assertTrue(r1._check_schedule(name, gated[name], r1.check_w1_schedule(None), "D"))
                self.assertEqual(gated[name]["decode_tokens"],
                                 sum(t["decode_tokens"] for t in json.loads(
                                     (run / name / gated[name]["bundle"] / "outputs/align_episode.json")
                                     .read_text())["turns"]))
                self.assertGreater(gated[name]["decode_tokens"], 0)
                r1._check_gated_t_dead(name, gated[name], step)
                r1._check_soak_reference_consumed(name, gated[name], run / "soak_reference.json")
                r1.deadman_summary(name, gated[name])
                bundle = run / name / gated[name]["bundle"]
                self.assertFalse((bundle / "outputs/align_window_reference.json").exists())
                episode = json.loads((bundle / "outputs/align_episode.json").read_text())
                g0 = [r for r in episode["hardware"]["thermal"]["intervals"] if r["kind"] == "G0"][0]
                self.assertEqual(g0["reference"]["slow_c"], soak_r)
                self.assertEqual(g0["reference"]["source_member"], "r1_soak_reference")
            xg = segment("X_G_contrast", "x-g")
            self.assertEqual(xg["reference_source"], "r1_soak_reference")
            self.assertEqual((xg["inter_member_idle_s"], xg["g0_outcome"]), (300.0, "released"))
            self.assertEqual(r1.gate_wait_medians(gated)["G1_waits"],
                             sum(len(g["gate_waits_s"]["G1"]) for g in gated.values()))
            planning = [segment(f"planning_turn_R_plus_{o}C", f"d-planning-turn-r-plus-{o}c") for o in (0, 2, 4)]
            summary = r1.planning_temperature_summary(planning)
            self.assertEqual(len(summary["points"]), 3)
            r1.u5_verdict(summary, gated)
            r1.projected_mde(step["e_D_j_per_token"], gated)
            release = segment("high_power_A1.g0_release0", "g0-release-soak")
            self.assertIs(release["released"], True)
            legs = [segment(f"high_power_{leg}", f"high-power-aba-{leg.lower()}") for leg in ("A1", "B", "A2")]
            self.assertTrue(all(leg["g0_released"] is True for leg in legs))
            legs = [leg["t_decline_s"] for leg in legs]
            r1.high_power_adoption(*legs)
            segment("post_calibration_bracket", "calibration-post", soak=False)
            harvested = segment("harvest", "harvest")
            battery = r1.battery_report(results, harvested)
            self.assertGreater(battery["drain_pct_per_h"]["D"], 0)
            self.assertGreater(battery["drain_pct_per_h"]["30B"], 0)
            self.assertIsNone(battery["charge_resume_soc_pct"])
            # LEAD-RULINGS-2 R7-2: the gated runs, X-G, step-d and the designed
            # start states arm the runtime config's 1,200 s G0 timeout through
            # the gate policy; every other member keeps the 600 s default. Each
            # reports its G0 wait (the bundle's G0 interval) and that cap.
            armed = {}
            for name, result in results.items():
                if "bundle" not in result:
                    continue
                bundle = run / name / result["bundle"]
                spec = json.loads(json.loads((bundle / "config.json").read_text())["workload_profile"]["prompt_text"])
                armed[kinds[name]] = spec["thermal"].get("g0_cap_s")
                episode = json.loads((bundle / "outputs/align_episode.json").read_text())
                g0 = [r for r in episode["hardware"]["thermal"]["intervals"] if r["kind"] == "G0"][0]
                self.assertEqual(result["g0_wait_s"], g0["duration_s"], name)
                self.assertEqual(result["g0_timeout_s"], 1200 if kinds[name] in rt.G0_TIMEOUT_KINDS else 600, name)
            for kind in ("step-d", "x-g", *contract.GATED_D_KINDS, *contract.PLANNING_KINDS):
                self.assertEqual(armed[kind], 1200, kind)
            for kind in ("step-30b", *contract.HIGH_POWER_KINDS):
                self.assertIsNone(armed[kind], kind)
            # R7-13: the D classification records its alias groups (none here).
            self.assertEqual(step["thermometry"]["alias_groups"], [])
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
            # WP18 is filled (fixtures merged): the production X-G template
            # carries an integer max_turns. A template whose max_turns is still
            # pending (the pre-WP18 kit) is refused by the runtime.
            template, spec = rt.read_template(production["templates"]["x_g"])
            self.assertEqual(spec["max_turns"], 12)
            template["workload_profile"]["prompt_text"] = json.dumps(dict(spec, max_turns=None))
            pending = root / "x_g_pending_wp18.json"
            pending.write_text(json.dumps(template))
            config = rs.synthetic_config(root / "cfg", )
            data = json.loads(config.read_text())
            data["templates"]["x_g"] = str(pending)
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


class IncompleteMemberTests(unittest.TestCase):
    """Round-4 executing review HIGH-1 (with the round-4 Fable cold pass HIGH-1):
    a designed start state whose G0 never released, or whose one turn was cut,
    must not reach the driver as a planning point (the G0 case carried the
    last sample as its 'release' temperature and energy_j = 0, because the
    g0_unreleased stop leaves the member with no turn)."""

    class NoReleaseBackend(rs.SyntheticBackend):
        def run_member(self, config_map, runs_root, hook):
            world = self.world
            nominal = type(world).status
            # PM state never Nominal: the production G0 can only time out.
            world.status = lambda: {**nominal(world), "pm_state": "Moderate"}
            try:
                return super().run_member(config_map, runs_root, hook)
            finally:
                del world.status

    def test_planning_turn_with_an_unreleased_g0_is_inconclusive(self):
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            root = Path(td)
            config = rs.synthetic_config(root / "cfg")
            soak = root / "soak.json"
            soak.write_text(json.dumps({"schema": rt.SOAK_REFERENCE_SCHEMA,
                                        "sensors_c": {rs.syn.FAST: 38.0, rs.syn.SLOW: 38.0},
                                        "detrended": {k: {"detrended_sd_c": 0.1} for k in (rs.syn.FAST, rs.syn.SLOW)}}))
            out = root / "planning_turn_R_plus_2C"
            buffer = io.StringIO()
            code = rt.main(["--config", str(config), "--r1-kind", "d-planning-turn-r-plus-2c", "--output", str(out),
                            "--soak-reference", str(soak)], stdout=buffer, backend_factory=self.NoReleaseBackend)
            record = custody(out)
            # LEAD-RULINGS-2 R6-2: INCONCLUSIVE (exit 0), not a failure that
            # refuses the night; still no release temperature and no energy.
            self.assertEqual(code, 0, record)
            self.assertEqual(record["status"], "complete")
            result = json.loads(buffer.getvalue())
            self.assertEqual((result["segment_status"], result["g0_released"], result["g0_outcome"]),
                             ("inconclusive", False, "timeout"))
            self.assertNotIn("g0_release_c", result)
            self.assertNotIn("energy_j", result)
            self.assertEqual(contract.missing_fields("d-planning-turn-r-plus-2c", result, quiet=True), [])
            r1.os_load_verdict("planning_turn_R_plus_2C", result)
            # The member itself ended at G0 with no turn: the evidence stays in DIR.
            bundle = out / "runs" / "align-v4-r1-d-planning-turn-r-plus-2c"
            self.assertTrue((bundle / "summary_metrics.json").exists())

    def test_planning_turn_cut_by_the_deadman_fails_the_segment(self):
        # The Fable cold pass HIGH-1 path: G0 releases, then the deadman cuts
        # the one decode. The old runtime returned that partial turn's energy.
        # (Since R5-2 the deadman is armed after the G0, so it must be shorter
        # than the turn itself to cut it.)
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            root = Path(td)
            config = rs.synthetic_config(root / "cfg")
            data = json.loads(config.read_text())
            data["step"]["deadman_s"] = 20    # synthetic full turn ~232 s
            config.write_text(json.dumps(data))
            soak = root / "soak.json"
            soak.write_text(json.dumps({"schema": rt.SOAK_REFERENCE_SCHEMA,
                                        "sensors_c": {rs.syn.FAST: 38.0, rs.syn.SLOW: 38.0},
                                        "detrended": {k: {"detrended_sd_c": 0.1} for k in (rs.syn.FAST, rs.syn.SLOW)}}))
            out = root / "planning_turn_R_plus_0C"
            code, result = call(config, out, "d-planning-turn-r-plus-0c", "--soak-reference", str(soak))
            record = custody(out)
            self.assertEqual(code, rt.EXIT_FAILED, record)
            self.assertIsNone(result)
            self.assertIn("planning member is not one complete turn", record["error"])
            self.assertIn("episode.deadman:0", record["error"])
            episode = json.loads((out / "runs/align-v4-r1-d-planning-turn-r-plus-0c/outputs/align_episode.json")
                                 .read_text())
            self.assertEqual([r["outcome"] for r in episode["hardware"]["thermal"]["intervals"]
                              if r["kind"] == "G0"], ["released"])
            self.assertEqual(len(episode["turns"]), 1)

    def test_step_d_with_an_unreleased_g0_is_inconclusive(self):
        # R6-2: step-d's G0 timeout used to exit 3 and refuse R1 after hours.
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            root = Path(td)
            config = rs.synthetic_config(root / "cfg")
            soak = write_soak(root / "soak.json")
            out = root / rt.STEP_D_SEGMENT
            buffer = io.StringIO()
            code = rt.main(["--config", str(config), "--r1-kind", "step-d", "--output", str(out),
                            "--soak-reference", str(soak)], stdout=buffer, backend_factory=self.NoReleaseBackend)
            record = custody(out)
            self.assertEqual(code, 0, record)
            result = json.loads(buffer.getvalue())
            self.assertEqual((result["segment_status"], result["g0_released"]), ("inconclusive", False))
            self.assertNotIn("slots", result)
            self.assertEqual(sorted(result["incomplete_reasons"]),
                             ["episode.g0_unreleased:0", "thermal.start_gate_timeout", "turns:0"])
            self.assertEqual(contract.missing_fields("step-d", result, quiet=True), [])
            # A consumer never reads an INCONCLUSIVE step-d as slots.
            run = root
            code, _ = call(config, run / "D_spam_benign_s1_gated_held_a", "d-spam-benign-s1-a",
                           "--soak-reference", str(soak))
            self.assertEqual(code, rt.EXIT_REFUSED)

    def test_only_a_pure_g0_timeout_is_inconclusive(self):
        self.assertTrue(rt.g0_timeout_only(["turns:0", "episode.g0_unreleased:0", "thermal.start_gate_timeout"]))
        self.assertTrue(rt.g0_timeout_only(["thermal.start_gate_timeout"]))
        for reasons in ([], ["turns:0"], ["turns:0", "thermal.start_gate_timeout", "thermal.custody_invalid"],
                        ["episode.g0_unreleased:0", "member_status:failed:unknown_error"],
                        ["thermal.start_gate_timeout", "thermal.collector_failed"]):
            with self.subTest(reasons=reasons):
                self.assertFalse(rt.g0_timeout_only(reasons))
        self.assertFalse(contract.is_g0_inconclusive("x-g", {"segment_status": "inconclusive"}))
        self.assertTrue(contract.is_g0_inconclusive("step-d", {"segment_status": "inconclusive"}))

    def test_incomplete_member_reasons(self):
        def member(status="succeeded", turns=1, flags=()):
            return SimpleNamespace(status=status, failure_reason=None,
                                   ep=SimpleNamespace(turns=[object()] * turns, flags=list(flags)))
        self.assertEqual(rt.incomplete_member_reasons(member(flags=(
            "turn_budget_reached", "episode.malformed_tool_call:0", "turn_token_budget_reached:0"))), [])
        for flag in ("episode.deadman:0", "episode.g0_unreleased:0", "thermal.start_gate_timeout",
                     "thermal.state_unobserved", "episode.decode_budget:0"):
            with self.subTest(flag=flag):
                self.assertEqual(rt.incomplete_member_reasons(member(flags=(flag,))), [flag])
        self.assertEqual(rt.incomplete_member_reasons(member(turns=0)), ["turns:0"])
        self.assertTrue(rt.incomplete_member_reasons(member(status="failed")))


def write_soak(path, slow=38.0, fast=38.0, sd=0.1):
    path.write_text(json.dumps({"schema": rt.SOAK_REFERENCE_SCHEMA,
                                "sensors_c": {rs.syn.FAST: fast, rs.syn.SLOW: slow},
                                "detrended": {k: {"detrended_sd_c": sd} for k in (rs.syn.FAST, rs.syn.SLOW)}}))
    return path


class Round5RuntimeTests(unittest.TestCase):
    """LEAD-RULINGS-2 R5-1, R5-2 and R5-3 in the runtime (synthetic backend)."""

    def test_planning_deadman_is_armed_after_the_preheat_and_g0(self):
        # R5-2 (exec MEDIUM-4, cold MEDIUM-3): the preheat and the G0 keep
        # their own caps; the deadman covers the decode only. The synthetic
        # turn takes ~232 s and the preheat plus G0 ~76 s or more, so with the
        # old G0-entry arming a 280 s deadman cut the turn (exit 3).
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            root = Path(td)
            config = rs.synthetic_config(root / "cfg")
            data = json.loads(config.read_text())
            data["step"]["deadman_s"] = 280
            config.write_text(json.dumps(data))
            soak = write_soak(root / "soak.json")
            out = root / "planning_turn_R_plus_2C"
            code, result = call(config, out, "d-planning-turn-r-plus-2c", "--soak-reference", str(soak))
            self.assertEqual(code, 0, custody(out).get("error"))
            self.assertEqual(result["g0_outcome"], "released")
            episode = json.loads((out / "runs/align-v4-r1-d-planning-turn-r-plus-2c/outputs/align_episode.json")
                                 .read_text())
            budget = episode["hardware"]["token_budget"]
            self.assertEqual(budget["deadline_origin"], "R1_after_preheat_and_G0")
            g0 = [r for r in episode["hardware"]["thermal"]["intervals"] if r["kind"] == "G0"][0]
            # Armed after the G0: the deadline is deadman_s past the G0's end.
            self.assertGreaterEqual(budget["deadline_ns"], g0["end_ns"] + 280 * NS)
            self.assertNotIn("episode.deadman:0", episode["flags"])

    def test_gated_d_run_gates_against_the_soak_reference_not_a_warm_capture(self):
        # R5-1 (cold HIGH-2): the old gated run captured its own R from the
        # 60 s before warmup (a warm value) and wrote align_window_reference.json.
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            root = Path(td)
            config = rs.synthetic_config(root / "cfg")
            soak = write_soak(root / "soak.json", slow=38.25, fast=38.5)
            run = root / "r1"
            (run / rt.STEP_D_SEGMENT).mkdir(parents=True)
            (run / rt.STEP_D_SEGMENT / rt.RESULT_NAME).write_text(json.dumps({"kind": "step-d", "slots": {
                "S7": 30.0, "T_dead": 600.0, "N_chunk": 256, "B_D": 4096}}))
            # Sol wp15rev F3 (R5-9): consumers read step-d only under its complete custody.
            rt.write_custody(run / rt.STEP_D_SEGMENT, {"status": "complete"})
            out = run / "D_spam_benign_s1_gated_held_a"
            code, result = call(config, out, "d-spam-benign-s1-a", "--soak-reference", str(soak))
            self.assertEqual(code, 0, custody(out).get("error"))
            self.assertEqual((result["reference_source"], result["reference_c"]), ("r1_soak_reference", 38.25))
            self.assertEqual(result["g0_reference"]["slow_c"], 38.25)
            self.assertEqual(result["g0_reference"]["fast_c"], 38.5)
            self.assertEqual(set(result["gate_waits_s"]), {"G0", "G1", "H"})
            bundle = out / result["bundle"]
            self.assertFalse((bundle / "outputs/align_window_reference.json").exists())
            code, _ = call(config, run / "no_soak", "d-spam-benign-s1-b")
            self.assertEqual(code, rt.EXIT_REFUSED)
            self.assertIn("--soak-reference", custody(run / "no_soak")["error"])

    def test_aba_leg_without_its_own_g0_release_is_inconclusive_not_a_failure(self):
        # R5-3 (exec MEDIUM-1): the leg used to exit 3 ("not one complete turn"),
        # which refused the whole R1 night after ~10 h.
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            root = Path(td)
            config = rs.synthetic_config(root / "cfg")
            soak = write_soak(root / "soak.json")
            out = root / "high_power_B"
            buffer = io.StringIO()
            code = rt.main(["--config", str(config), "--r1-kind", "high-power-aba-b", "--output", str(out),
                            "--soak-reference", str(soak)], stdout=buffer,
                           backend_factory=IncompleteMemberTests.NoReleaseBackend)
            self.assertEqual(code, 0, custody(out).get("error"))
            result = json.loads(buffer.getvalue())
            self.assertIs(result["g0_released"], False)
            self.assertIsNone(result["t_decline_s"])
            self.assertEqual(result["t_decline_status"], "not_measured_g0_unreleased")
            self.assertEqual(result["leg_status"], "inconclusive")
            self.assertEqual(contract.missing_fields("high-power-aba-b", result, quiet=True), [])
            r1.os_load_verdict("high_power_B", result)

    def test_cooldown_releases_on_the_one_sided_g0_band(self):
        # R5-1: "within the G0 band of R" is S_slow <= R + delta_slow. A host
        # already cooler than the soak R has cooled; the old |S_slow - R| <=
        # delta rule waited out the whole cap and reported a timeout.
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            root = Path(td)
            config = rs.synthetic_config(root / "cfg")
            soak = write_soak(root / "soak.json", slow=rs.syn.AMBIENT_C + 5.0)   # world sits at ambient
            out = root / "D_bank_benign_s1_gated_held.precool"
            code, result = call(config, out, "idle-until-soak", "--duration-s", "120", "--soak-reference", str(soak))
            self.assertEqual(code, 0, custody(out).get("error"))
            self.assertIs(result["released"], True)
            self.assertLess(result["recovery_curve"][-1][0], 10)

class Round5Tests(unittest.TestCase):
    """Lead rulings R5-4, R5-9 and R5-10 (round-5 infrastructure)."""

    def test_terminal_custody_includes_nested_file_with_same_basename(self):
        # Sol wp15rev F2: only DIR's own record is excluded, not a nested namesake.
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            out = Path(td)
            nested = out / "runs/member" / rt.CUSTODY_NAME
            nested.parent.mkdir(parents=True)
            nested.write_text("nested bundle custody\n")
            rt.write_custody(out, {"status": "complete"})
            self.assertEqual(custody(out)["files"][f"runs/member/{rt.CUSTODY_NAME}"], rt.sha256_file(nested))
            self.assertNotIn(rt.CUSTODY_NAME, custody(out)["files"])

    def test_step_d_consumer_requires_complete_digest_bound_custody(self):
        # Sol wp15rev F3: B_D/N_chunk/T_dead are read only from the bytes the
        # step-d runtime's complete custody digested.
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
            result.write_text(json.dumps({"kind": "step-d", "slots": {"T_dead": 11, "B_D": 8192}}))
            with self.assertRaisesRegex(rt.Refused, "complete runtime custody"):
                rt.Segment.step_d_result(segment)
            rt.write_custody(step_dir, {"status": "failed"})
            with self.assertRaisesRegex(rt.Refused, "complete runtime custody"):
                rt.Segment.step_d_result(segment)

    def test_gated_d_never_runs_unbudgeted(self):
        # Lead ruling R5-4 / Sol wp15rev F4: B_D 0 used to arm no decode cap.
        from unittest import mock
        segment = object.__new__(rt.Segment)
        segment.kind = "d-spam-benign-s1-a"
        segment.template = mock.Mock(return_value=({}, {}))
        segment.run_member = mock.Mock(side_effect=AssertionError("model work before the refusal"))
        for slots, message in (({"T_dead": float("nan"), "B_D": 1024}, "T_dead"),
                               ({"T_dead": True, "B_D": 1024}, "T_dead"),
                               ({"T_dead": -1.0, "B_D": 1024}, "T_dead"),
                               ({"T_dead": 10.0, "B_D": 0}, "B_D 0 is not an admissible"),
                               ({"T_dead": 10.0, "B_D": 1025}, "B_D"),
                               ({"T_dead": 10.0, "B_D": 41984}, "B_D"),
                               ({"T_dead": 10.0, "B_D": None}, "B_D"),
                               ({"T_dead": 10.0, "B_D": True}, "B_D")):
            segment.step_d_result = mock.Mock(return_value={"slots": slots})
            with self.subTest(slots=slots), self.assertRaisesRegex(rt.Refused, message):
                segment.k_gated_d()
        self.assertEqual(rt.gated_budget({"T_dead": 1200.0, "B_D": 8192}), (1200.0, 8192))

    def test_segment_close_survives_a_signal_and_still_stops_the_journals(self):
        # Sol wp15rev triage: a first TERM (SystemExit) while one session
        # closes must not strand the others (powermetrics) or the journals.
        closed, journals = [], []

        class Session:
            def __init__(self, name, error=None):
                self.name, self.error = name, error

            def close(self):
                closed.append(self.name)
                if self.error is not None:
                    raise self.error
        def bare_segment(sessions):
            segment = object.__new__(rt.Segment)
            segment.heaters = []
            segment.inventory_readers, segment._stop_inventory = [], None
            segment.open_sessions = sessions
            segment._stop_ticker = lambda: None
            segment.stop_journals = lambda final=True: journals.append(final)
            return segment
        segment = bare_segment([Session("powermetrics"), Session("smc", SystemExit(143))])
        errors = segment.close()
        self.assertEqual(closed, ["smc", "powermetrics"])
        self.assertEqual(journals, [False])
        self.assertEqual([type(e) for e in errors], [SystemExit])
        # Round-5 integration: the R5-5 inventory journal stops first; a TERM
        # there must not strand the sessions (powermetrics) or the journals.
        closed.clear(), journals.clear()
        segment = bare_segment([Session("powermetrics"), Session("smc")])

        def interrupted():
            raise SystemExit(143)
        segment._stop_inventory = interrupted
        errors = segment.close()
        self.assertEqual(closed, ["smc", "powermetrics"])
        self.assertEqual(journals, [False])
        self.assertEqual([type(e) for e in errors], [SystemExit])

    def test_step_response_with_no_rise_has_a_null_censored_t63(self):
        # Executing review round 4 LOW-9: never t63 = 0.0 (a "fast" key).
        rows = [{"monotonic_ns": t * NS, "sensors": {"K": 40.0 - 0.001 * t}, "errors": {}} for t in range(200)]
        response = rt.step_response(rows, "K", 100 * NS, 150 * NS)
        self.assertIsNone(response["t63_s"])
        self.assertIn("t63_censored", response["flags"])
        turn = SimpleNamespace(start_ns=100 * NS, first_token_ns=120 * NS, end_ns=520 * NS,
                               decode_tokens=4000, prefill_tokens=10000)
        ep = SimpleNamespace(start_ns=100 * NS, end_ns=525 * NS, hardware={"thermal": {"intervals": []}})
        slots, detail = rt.derive_step_d_slots(
            ep=ep, turn=turn, wall_s=800.0, responses={"s_fast": response, "s_slow": response},
            recovery_s=50.0, recovery_censored=False, bands={"delta_fast_c": 1.0, "delta_slow_c": 1.0},
            t_decline_s=200.0, t_decline_status="declined", d_class="heavy")
        self.assertIsNone(slots["S2"])
        self.assertIsNone(detail["classification"]["s_fast_t63_le_5s"])
        with self.assertRaisesRegex(r1.Refusal, "slot S2 is not finite"):
            r1.derive_slots({"slots": slots})

    def test_watchdog_runs_its_teardown_then_always_exits(self):
        # Executing review round 4 LOW-1.
        exits, order = [], []
        term = rt.Termination(exit_now=lambda code: (order.append("exit"), exits.append(code)))
        term.on_timeout = lambda: order.append("teardown")
        term.expire(143)
        self.assertEqual((order, exits), (["teardown", "exit"], [143]))

        def broken():
            raise SystemExit(1)
        term.on_timeout = broken
        term.expire(130)
        self.assertEqual(exits, [143, 130])

    def test_watchdog_teardown_stops_powermetrics_and_writes_the_terminal_record(self):
        ps = ("1 0 /sbin/launchd\n"
              "500 1 /usr/bin/python -B scripts/align_r1_runtime.py\n"
              "501 500 sudo -n /usr/bin/powermetrics --samplers gpu_power -i 100\n"
              "502 501 /usr/bin/powermetrics --samplers gpu_power -i 100\n"
              "503 500 /usr/bin/python -c heater\n"
              "600 1 sudo -n /usr/bin/powermetrics --other-session\n")
        sent = []

        def kill(pid, sig):
            if sig == 0:
                raise ProcessLookupError(pid)        # gone at the first check
            if pid == 502:
                raise PermissionError("root process")
            sent.append((pid, sig))
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            out = Path(td)
            (out / "load_journal.json").write_text("{}")
            rt.watchdog_teardown(out, {"kind": "step-d", "status": "aborted", "signal": 15},
                                 run=lambda argv: SimpleNamespace(stdout=ps), kill=kill, root_pid=500)
            record = custody(out)
        self.assertEqual(sent, [(501, signal.SIGTERM)])   # own tree only; EPERM on root ignored
        self.assertEqual((record["status"], record["watchdog"], record["signal"]), ("aborted", True, 15))
        self.assertEqual(record["watchdog_powermetrics_signalled"], [501])
        self.assertIn("load_journal.json", record["files"])

    def test_a_pid_that_left_the_tree_before_signalling_is_not_signalled(self):
        snapshots = iter(["500 1 runtime\n501 500 sudo -n /usr/bin/powermetrics\n",
                          "500 1 runtime\n501 1 /usr/bin/powermetrics --someone-else\n"])
        sent = []
        stopped = rt.stop_powermetrics_descendants(
            500, run=lambda argv: SimpleNamespace(stdout=next(snapshots)),
            kill=lambda pid, sig: sent.append((pid, sig)), wait_s=0)
        self.assertEqual((stopped, sent), ([], []))

    def test_watchdog_digests_stop_at_the_deadline_inside_a_file(self):
        # Sol critique: the deadline is checked per block, not only between files.
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            out = Path(td)
            (out / "big.bin").write_bytes(b"x" * (3 << 20))
            (out / "small.txt").write_text("y")
            ticks = iter([0.0, 0.0, 0.0, 10.0, 10.0, 10.0, 10.0, 10.0])
            from unittest import mock
            with mock.patch.object(rt.time, "monotonic", lambda: next(ticks, 10.0)):
                rt.write_custody(out, {"status": "aborted"}, deadline=5.0)
            files = custody(out)["files"]
            self.assertEqual(files["big.bin"], "unhashed: watchdog deadline")
            self.assertEqual(files["small.txt"], "unhashed: watchdog deadline")

    def test_watchdog_has_a_hard_exit_independent_of_its_teardown(self):
        exits = []
        term = rt.Termination(exit_now=exits.append, hard_s=0.2)
        release = threading.Event()
        term.on_timeout = lambda: release.wait(5)          # a stalled teardown
        worker = threading.Thread(target=term.expire, args=(143,), daemon=True)
        worker.start()
        time.sleep(0.6)
        self.assertEqual(exits, [143])                      # the hard exit fired while stalled
        release.set()
        worker.join(5)

    def test_one_owner_writes_the_terminal_record(self):
        # Sol critique: once the watchdog published, the normal path never
        # replaces its record (and vice versa).
        from unittest import mock
        captured = []

        class Capture(rt.Termination):
            def install(self):
                captured.append(self)
                return super().install()
        with tempfile.TemporaryDirectory(dir=TMP) as td, mock.patch.object(rt, "Termination", Capture), \
                mock.patch.object(rt, "stop_powermetrics_descendants", return_value=[]):
            out = Path(td) / "g0"
            real = rt.Segment.run

            def run_then_watchdog(segment):
                captured[0].on_timeout()                     # the watchdog publishes mid-run
                return real(segment)
            with mock.patch.object(rt.Segment, "run", run_then_watchdog):
                code, _ = call(rs.synthetic_config(Path(td) / "cfg"), out, "calibration-pre")
            self.assertEqual(custody(out)["watchdog"], True)
            self.assertEqual(custody(out)["status"], "aborted")

    def test_main_arms_the_watchdog_teardown_once_dir_exists(self):
        from unittest import mock
        captured = []

        class Capture(rt.Termination):
            def install(self):
                captured.append(self)
                return super().install()
        with tempfile.TemporaryDirectory(dir=TMP) as td, mock.patch.object(rt, "Termination", Capture), \
                mock.patch.object(rt, "stop_powermetrics_descendants", return_value=[]):
            out = Path(td) / "g0"
            real = rt.write_custody
            with mock.patch.object(rt, "write_custody",
                                   side_effect=lambda o, r, **k: real(o, r, **k) if k else (_ for _ in ()).throw(
                                       OSError("disk"))):
                code, _ = call(rs.synthetic_config(Path(td) / "cfg"), out, "g0-release-soak")
                self.assertEqual(code, rt.EXIT_REFUSED)
                self.assertFalse((out / rt.CUSTODY_NAME).exists())   # the normal write failed here
                captured[0].on_timeout()                               # what the watchdog thread runs
            record = custody(out)
            self.assertEqual((record["status"], record["watchdog"]), ("aborted", True))


if __name__ == "__main__":
    unittest.main()
