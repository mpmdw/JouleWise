"""RL-59/61/64/72/74/75/76, synthetic only; never reads study custody."""
from copy import deepcopy
import ctypes
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise.align.apple import r1_runtime as rt, v4_registration as reg, workload
from scripts import align_r1_rehearsal as r1, align_r1_followup_kit as kit
from tests.align.test_r1_rehearsal import FakeWorld, NOON_SAFE
from tests.align import test_r1_rehearsal as rehearsal
from tests.align import r1_synthetic as syn


class InventoryReader:
    def enumerate_sensors(self):
        return {"complete": True, "keys": [{"key": "TV0h", "unit": "degC"}], "errors": {}}

    def read(self, keys):
        return {"values": {key: 40.0 for key in keys}, "errors": {}}

    def close(self):
        pass


class ProcessSamplerTests(unittest.TestCase):
    def test_main_interpreter_blocked_in_every_phase_does_not_starve_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            journal = rt.ProcessInventory(Path(tmp) / "inventory.jsonl",
                                           reader_factory=__name__ + ":InventoryReader")
            phases = {}
            try:
                # PyDLL holds the GIL for the whole call: a ticker thread in this
                # interpreter cannot run. One core's short load only, no MLX.
                libc = ctypes.PyDLL(None)
                libc.usleep.argtypes = [ctypes.c_uint]
                for phase in ("pre_warmup_idle", "quiet", "load", "recovery"):
                    start = time.monotonic_ns()
                    libc.usleep(2_100_000)
                    phases[phase] = (start, time.monotonic_ns())
            finally:
                journal.close()
            report = kit.phase_coverage(journal.rows, ["TV0h"], phases)
            self.assertTrue(report["pass"], report)
            self.assertFalse(journal.process.is_alive())
            for phase in report["phases"].values():
                self.assertGreaterEqual(phase["TV0h"]["sample_fraction"], .99)
                self.assertLess(phase["TV0h"]["read_error_fraction"], .01)
                self.assertLess(phase["TV0h"]["max_consecutive_empty_cells"], 2)


class PolicyTests(unittest.TestCase):
    def test_timeout_callback_refuses_unobserved_deadman_and_faults_without_reference(self):
        for outcome in ("unobserved", "deadman", "released"):
            session = SimpleNamespace(flags=[], episode_reference=None)
            self.assertFalse(rt.allow_g0_timeout_run(session, {"outcome": outcome}))
            self.assertIsNone(session.episode_reference)
        session = SimpleNamespace(flags=["thermal.collector_failed:x"], episode_reference=None)
        self.assertFalse(rt.allow_g0_timeout_run(session, {"outcome": "timeout"}))
        session.flags = ["thermal.start_gate_timeout"]
        self.assertTrue(rt.allow_g0_timeout_run(session, {"outcome": "timeout"}))
        self.assertIn("r1.g0_timeout_run", session.flags)
        self.assertIsNone(session.episode_reference)
        self.assertTrue(set(rt.TIMEOUT_RUN_KINDS).isdisjoint((*rt.contract.GATED_D_KINDS, "x-g")))

    def test_aba_cross_band_and_bracket_each_veto_adoption(self):
        legs = {k: {"g0_released": True, "g0_release": {"fast_c": 40., "slow_c": 40.},
                    "operating_reference": {"fast_c": 40., "slow_c": 40.},
                    "bands_c": {"delta_fast_c": 1., "delta_slow_c": 1.5}}
                for k in ("A1", "B", "A2")}
        self.assertTrue(r1.aba_start_bars(legs)["pass"])
        legs["B"]["g0_release"]["slow_c"] = 41.6
        self.assertFalse(r1.aba_start_bars(legs)["pass"])
        legs["B"]["g0_release"]["slow_c"] = 40.
        legs["B"]["operating_reference"]["slow_c"] = 40.51
        self.assertFalse(r1.aba_start_bars(legs)["pass"])

    def test_new_fast_family_slow_pick_and_missing_checks_hold_prepare(self):
        config = {"sensors": {"s_fast": "TV0h", "s_slow": "TV0m"}, "slow_band_floor_c": 1.0}
        ruling = {"sensors": config["sensors"], "outcome": 2, "research_lead_ruling": "synthetic",
                  "smoke_part_b_sha256": "a" * 64, "stable_with_borderline_reads": True}
        with self.assertRaisesRegex(ValueError, "RL-75"):
            kit.validate_sensor_ruling(config, ruling, "a" * 64)
        ruling.update(outcome=3, authorizes_night=True)
        kit.validate_sensor_ruling(config, ruling, "a" * 64)
        with self.assertRaisesRegex(ValueError, "RL-62"):
            kit.prepare_checks(r1.ROOT, config)

    def test_gate_module_is_exactly_w1_base(self):
        path = "joulewise/align/apple/thermal_gates.py"
        self.assertEqual((r1.ROOT / path).read_bytes(), reg._committed_bytes(r1.ROOT, "82c14c9ea", [path])[path])


class PrepareTests(unittest.TestCase):
    def test_prepare_arm_window_equals_computed_worst_case_and_checks_precede_identity(self):
        import hashlib
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            table = root / "smoke-b.json"
            table.write_text('{"synthetic": true}')
            config, _ = rt.load_config(r1.ROOT / r1.DEFAULT_RUNTIME_CONFIG)
            ruling = {"research_lead_ruling": "SYNTHETIC ONLY", "outcome": 1, "sensors": config["sensors"],
                      "smoke_part_b_sha256": hashlib.sha256(table.read_bytes()).hexdigest()}
            calls = []
            with patch.object(reg, "verify_r1_executed_sources", side_effect=lambda *a: calls.append("identity")):
                packet = kit.prepare(root / "prepare.json", ruling=ruling, smoke_table=table,
                    weight_digest_check=lambda *a: calls.append("weights"),
                    runtime_stack_check=lambda *a: calls.append("stack"))
            self.assertEqual(calls, ["weights", "stack", "identity"])
            self.assertEqual(packet["window_max_s"], r1.night_worst_case_s()["window_max_s"])
            self.assertEqual(packet["window_max_s"], 126480)
            self.assertEqual(packet["overhead_s"], 9000)
            self.assertEqual(packet["status"], "FOR_LEAD_ARM")


class CandidateReplayTests(unittest.TestCase):
    def test_each_candidate_band_has_condition_and_reference_sensitivity(self):
        from tests.align.test_r1_inventory import step_capture, PREFILL_NS, LAST_DECODE_NS
        from scripts import align_r1_thermal_replay as replay
        inventory, rows = step_capture()
        fast, slow = "TC0P", "TG0P"
        # These names come from the synthetic inventory, never a host probe.
        fast = inventory["keys"][0]["key"]
        slow = inventory["keys"][1]["key"]
        statuses = [{"monotonic_ns": r["started"]["monotonic_ns"],
                     "status": {"os_level": 0, "pm_state": "Nominal",
                                "pm_observed_ns": r["started"]["monotonic_ns"]}} for r in rows]
        result = replay.candidate_replays(rows, statuses, [slow], fast, PREFILL_NS,
                                          LAST_DECODE_NS, LAST_DECODE_NS+600*rt.NS)
        self.assertEqual([r["band_c"] for r in result], [1.0, 1.5])
        for row in result:
            self.assertIn("deciding_condition", row)
            self.assertIn("reference_sensitivity", row)
            self.assertEqual(len(row["reference_sensitivity"]), 2)
            self.assertLessEqual(row["replay"]["wait_s"], 600)




class DriverTests(unittest.TestCase):
    def run_world(self, root, world):
        with patch.object(r1, "_now_local", lambda: NOON_SAFE), patch.object(r1, "_run", world):
            args = rehearsal.R1Tests.args(None, root, synthetic=True)
            self.assertEqual(r1.run(args), 0, json.loads((args.output / "r1_result.json").read_text()).get("error"))
        return json.loads(args.registration.read_text()), json.loads((args.output / "r1_result.json").read_text())

    def test_order_cuts_timeout_candidates_and_receipt_preservation(self):
        with tempfile.TemporaryDirectory() as tmp:
            world = FakeWorld(calibration_g0_timeouts={"step-d": 1})
            slots, result = self.run_world(tmp, world)
            names = [p["name"] for p in result["phases"]]
            i = names.index(rt.STEP_D_SEGMENT)
            self.assertEqual(names[i-1], "capture_predecessor_30b")
            self.assertNotIn(rt.STEP_D_SEGMENT + ".precool", names)
            self.assertNotIn("D_4bit_optional", names)
            self.assertTrue(all("precool_retry" not in n and "g0_release" not in n for n in names))
            self.assertIn(rt.STEP_D_SEGMENT, slots["inconclusive_segments"])
            self.assertIn("r1.g0_timeout_run", slots["inadmissible_slots"]["B_D"])
            self.assertEqual(slots["s6_tuning"]["to_c"], 1.5)
            self.assertIn("D_bank_benign_s1_gated_held", names)
            from scripts.align_v4_kit import check_r1_evidence
            with self.assertRaisesRegex(ValueError, "INCONCLUSIVE|inconclusive"):
                check_r1_evidence({}, slots, synthetic=True)

    def test_redo_repeats_capture_pair_and_each_planning_precool(self):
        with tempfile.TemporaryDirectory() as tmp:
            slots, result = self.run_world(tmp, FakeWorld(busy_once={"step-d", "d-planning-turn-r-plus-2c"}))
            self.assertEqual(result["load_redos_used"], 2)
            phases = {p["name"]: p for p in result["phases"]}
            for name in ("capture_predecessor_30b", rt.STEP_D_SEGMENT, "planning_turn_R_plus_2C.precool",
                         "planning_turn_R_plus_2C"):
                self.assertEqual(phases[name]["attempt"], 1)
                self.assertTrue(phases[name]["superseded_attempts"])
            self.assertFalse(slots["inconclusive_segments"])

    def test_window_equals_computed_arm_and_batch_admits_whole_pair(self):
        bound = r1.night_worst_case_s()
        self.assertEqual(bound["window_max_s"], 126480)
        self.assertEqual(bound["floor_s"], 99768)
        self.assertEqual(bound["overhead_s"], sum(bound["overhead_caps_s"].values()))
        self.assertAlmostEqual(bound["no_redo_s"], 58711.9616)
        from datetime import datetime, timedelta
        for day in (11, 12, 13):
            moment = datetime(2026, 11, day, 10, 0, tzinfo=r1.ZoneInfo("America/Los_Angeles"))
            now = [moment]
            def sleep(seconds):
                now[0] += timedelta(seconds=seconds)
            waited = r1.wait_outside_os_batch(bound["largest_unit_s"], now=lambda: now[0], sleep=sleep)
            self.assertGreater(waited, 0)
            self.assertEqual((now[0].hour, now[0].minute), (13, 15))


class DispatchTests(unittest.TestCase):
    def test_observed_timeout_runs_only_with_callback_and_keeps_null_reference(self):
        for enabled in (False, True):
            with self.subTest(enabled=enabled), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                config, _ = rt.load_config(syn.synthetic_config(root / "cfg"))
                backend = syn.SyntheticBackend(config)
                try:
                    template, tspec = rt.read_template(config["templates"]["d_spam"])
                    policy = rt.gate_policy(config["sensors"], {"delta_fast_c": 1., "delta_slow_c": 1.5},
                                            turn_cap_s=300, chunk_tokens=256, heavy=False, per_turn=False)
                    spec = rt.step_spec(tspec, {**config["step"], "decode_tokens": 8}, policy, deadman_s=1580)
                    member = rt.member_config(template, spec, run_id="timeout-member", kind="step-d")
                    def hook(session):
                        session.reference = {"fast_c": 0., "slow_c": 0., "source_member": "synthetic"}
                        if enabled:
                            session.g0_timeout_hook = rt.allow_g0_timeout_run
                    bundle, summary = backend.run_member(member, root / "runs", hook)
                    ep = workload.read_episode_bundle(bundle)
                    self.assertEqual(len(ep.turns), int(enabled))
                    self.assertIsNone(ep.hardware["thermal"]["episode_reference"])
                    self.assertIn("thermal.start_gate_timeout", ep.flags)
                    self.assertEqual("r1.g0_timeout_run" in ep.flags, enabled)
                finally:
                    backend.close()


class DefaultBundleTests(unittest.TestCase):
    def test_default_member_bundle_equals_pre_callback_workload_bytes(self):
        # Run the actual old adapter and the new adapter against the same tiny
        # deterministic model/clock/config/path. Compare every bundle file.
        old = ModuleType("joulewise.align.apple._r1_legacy_workload")
        old.__package__ = "joulewise.align.apple"
        sys.modules[old.__name__] = old
        self.addCleanup(lambda: sys.modules.pop(old.__name__, None))
        exec(compile(subprocess.check_output(["git", "show", "82c14c9ea:joulewise/align/apple/workload.py"],
                                            cwd=r1.ROOT), old.__name__, "exec"), old.__dict__)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = syn.synthetic_config(root / "cfg")
            config, _ = rt.load_config(path)
            template, tspec = rt.read_template(config["templates"]["d_spam"])
            policy = rt.gate_policy(config["sensors"], {"delta_fast_c": 1., "delta_slow_c": 1.5},
                                    turn_cap_s=300, chunk_tokens=256, heavy=False, per_turn=False)
            spec = rt.step_spec(tspec, {**config["step"], "decode_tokens": 8}, policy, deadman_s=1580)
            member = rt.member_config(template, spec, run_id="same-member", kind="step-d")
            outputs = []
            for adapter in (old.EpisodeRuntimeAdapter, workload.EpisodeRuntimeAdapter):
                backend = syn.SyntheticBackend(config)
                try:
                    from joulewise import controller
                    with patch.object(workload, "EpisodeRuntimeAdapter", adapter), patch.object(
                            controller._Execution, "_battery_stamp", lambda execution: execution._clock.stamp()):
                        bundle, summary = backend.run_member(member, root / "runs", hook=None)
                    self.assertEqual(summary.status.value, "succeeded")
                    outputs.append({p.relative_to(bundle).as_posix(): p.read_bytes()
                                    for p in bundle.rglob("*") if p.is_file()})
                finally:
                    backend.close()
                shutil.rmtree(root / "runs")
            self.assertEqual(set(outputs[0]), set(outputs[1]))
            for name in outputs[0]:
                self.assertEqual(outputs[0][name], outputs[1][name], name)


if __name__ == "__main__":
    unittest.main()
