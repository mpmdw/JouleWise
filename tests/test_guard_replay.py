"""All samples are synthetic. Historical implementations come from local Git code."""
import importlib.util
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from joulewise import guard_replay as replay
from joulewise.guard_replay_corpus import OpaqueNumber, project_receipt


def cpu(a=0, b=30, rate=.02, *, aggregate=.2, error=None, command="routined", pid=7):
    row = {"pid": pid, "command": command, "start": "synthetic", "cpu_s_per_s": rate}
    return {"interval": {"monotonic_ns": [int(a * 1e9), int(b * 1e9)]}, "elapsed_s": b-a,
            "error": error, "clean": None if error else rate <= .05,
            "max_outside": row, "outside_listed": [row],
            "outside_over_limit": [row] if rate > .05 else [],
            "outside_aggregate_cpu_s_per_s": aggregate, "kernel_task_cpu_s_per_s": 0.}


def run(name, frames, *, label="benign", complete=False, stratum="synthetic"):
    return {"id": name, "label": label, "label_basis": "synthetic control with a defined injected hazard",
            "stratum": stratum, "complete": complete,
            "duration_s": frames[-1]["t"] - frames[0]["t"] if frames else 0, "frames": frames}


def corpus(*runs):
    return {"schema": replay.SCHEMA, "runs": list(runs)}


def synthetic_corpus():
    benign = run("decayed-pcpu-and-routine-daemon", [
        {"t": 0, "pcpu_busy": [[7, 34., "photoanalysisd"]], "quiet_busy": [],
         "smc_cpu": cpu(0, 30, .06), "cpu_era": "prel3",
         "environment": {"display_power_state": "all_asleep", "screensaver_engaged": False},
         "thermal": {"level": 0}},
        {"t": 30, "pcpu_busy": [], "quiet_busy": [], "smc_cpu": cpu(30, 60, .01),
         "cpu_era": "prel3", "environment": {"display_power_state": "all_asleep", "screensaver_engaged": False},
         "thermal": {"level": 0}}], complete=True)
    heavy = run("sustained-single-process", [
        {"t": 0, "smc_cpu": cpu(0, 30, .6), "cpu_era": "prel3"},
        {"t": 30, "smc_cpu": cpu(30, 60, .6), "cpu_era": "prel3"}], label="contended", complete=True)
    display = run("display-wake", [{"t": 0, "environment": {
        "display_power_state": "any_awake", "screensaver_engaged": False}}], label="contended")
    thermal = run("thermal-pressure", [{"t": 0, "thermal": {"level": 1}}], label="contended")
    aggregate = run("idle-host-aggregate-only", [snapshot(0, 0, host_busy=.3),
                    snapshot(1, .01, host_busy=.3), snapshot(30, .3, host_busy=.3)])
    return corpus(benign, heavy, display, thermal, aggregate)


def custom_adapter(tape):
    return replay.thermal(tape)


def snapshot(t, cpu_s, *, command="routined", start="born", error=None, host_busy=0):
    return {"t": t, "snapshot": {"wall_s": 1000+t, "processes": [
        {"pid": 7, "ppid": 1, "start": start, "start_epoch_s": 0,
         "command": command, "cpu_s": cpu_s}], "error": error,
        "host_ticks": [[int(host_busy*t*100), 0, int((1-host_busy)*t*100), 0]]}}


class GuardReplayTests(unittest.TestCase):
    def evaluate(self, data, names, **kwargs):
        return replay.replay(data, names, run_seconds=kwargs.pop("run_seconds", 30), **kwargs)["guards"]

    def test_pre691_executes_original_quietguard_and_latches(self):
        data = corpus(run("benign", [{"t": 0, "pcpu_busy": []},
                                    {"t": 15, "pcpu_busy": [[7, 34., "photoanalysisd"]]},
                                    {"t": 30, "pcpu_busy": []}]))
        report = self.evaluate(data, ["quiet-pre691"])[0]
        self.assertEqual(report["decisions"][0]["status"], "REFUSE")
        self.assertEqual(report["decisions"][0]["evaluated"], 2)
        self.assertEqual(report["strata"][0]["refusal_rate"], 1.)
        self.assertEqual(report["strata"][0]["assessment"], "ABOVE_BOUND")

    def test_exact_percent_boundary(self):
        for pcpu, expected in ((5., "PASS"), (5.001, "REFUSE")):
            with self.subTest(pcpu=pcpu):
                d = self.evaluate(corpus(run("x", [{"t": 0, "pcpu_busy": [[7, pcpu, "mdworker"]]}])),
                                  ["quiet-pre691"])[0]["decisions"][0]
                self.assertEqual(d["status"], expected)

    def test_l3_quietguard_records_instead_of_refusing(self):
        busy = [{"pid": 7, "command": "mdworker", "cpu_s_per_s": .06}]
        data = corpus(run("x", [{"t": 30, "quiet_busy": busy}]))
        before, after = self.evaluate(data, ["quiet-prel3", "quiet-l3"])
        self.assertEqual(before["decisions"][0]["status"], "REFUSE")
        self.assertEqual(after["decisions"][0]["status"], "PASS")

    def test_pre_l3_rejects_benign_daemon_l3_accepts_and_detects_sustained(self):
        old, new = self.evaluate(synthetic_corpus(), ["smc-prel3", "smc-l3-redo"])
        self.assertEqual(old["decisions"][0]["status"], "REFUSE")
        self.assertEqual(new["decisions"][0]["status"], "PASS")
        self.assertEqual(new["decisions"][1]["status"], "REFUSE")
        self.assertEqual(new["strata"][1]["refusal_rate"], 1.)

    def test_aggregate_only_cannot_trigger_l3(self):
        frames = [{"t": a, "smc_cpu": cpu(a, a+30, .3, aggregate=1.2)} for a in (0, 30)]
        d = self.evaluate(corpus(run("x", frames)), ["smc-l3-redo"])[0]["decisions"][0]
        self.assertEqual(d["status"], "PASS")

    def test_kernel_task_alone_cannot_trigger_l3(self):
        frames = [{"t": a, "smc_cpu": cpu(a, a+30, 1., command="kernel_task", pid=0)} for a in (0, 30)]
        self.assertEqual(self.evaluate(corpus(run("x", frames)), ["smc-l3-redo"])[0]["decisions"][0]["status"], "PASS")

    def test_gapped_heavy_intervals_do_not_make_sustained_episode(self):
        frames = [{"t": a, "smc_cpu": cpu(a, a+30, .6)} for a in (0, 31)]
        self.assertEqual(self.evaluate(corpus(run("x", frames)), ["smc-l3-redo"])[0]["decisions"][0]["status"], "PASS")

    def test_overlapping_intervals_are_union_not_sum(self):
        frames = [{"t": a, "smc_cpu": cpu(a, a+30, .6)} for a in (0, 15)]
        self.assertEqual(self.evaluate(corpus(run("x", frames)), ["smc-l3-redo"])[0]["decisions"][0]["status"], "PASS")

    def test_unmeasured_never_becomes_true_or_false_refusal(self):
        data = corpus(run("x", [{"t": 30, "smc_cpu": cpu(error="probe failed")}]))
        d = self.evaluate(data, ["smc-prel3"])[0]
        self.assertEqual(d["decisions"][0]["status"], "UNMEASURED")
        self.assertIsNone(d["strata"][0]["refusal_rate"])
        self.assertEqual(d["strata"][0]["unmeasured"], 1)

    def test_missing_channel_is_unsupported(self):
        d = self.evaluate(corpus(run("x", [{"t": 0}])), ["display"])[0]
        self.assertEqual(d["decisions"][0]["status"], "UNSUPPORTED")
        self.assertIsNone(d["strata"][0]["wilson_95"])

    def test_summary_cannot_fake_longer_baseline(self):
        d = self.evaluate(corpus(run("x", [{"t": 0, "smc_cpu": cpu(0, 1)}])), ["smc-prel3"])[0]
        self.assertEqual(d["decisions"][0]["status"], "UNSUPPORTED")

    def test_old_aggregate_probe_imported_with_raw_synthetic_ticks(self):
        data = corpus(run("x", [snapshot(0, 0, host_busy=.3), snapshot(1, .01, host_busy=.3)]))
        d = self.evaluate(data, ["smc-pre691"])[0]
        self.assertEqual(d["decisions"][0]["status"], "REFUSE")

    def test_new_probe_uses_30s_baseline_and_real_counter_deltas(self):
        data = corpus(run("x", [snapshot(0, 0, host_busy=.3), snapshot(30, .3, host_busy=.3)]))
        d = self.evaluate(data, ["smc-prel3"])[0]
        self.assertEqual(d["decisions"][0]["status"], "PASS")

    def test_startup_sleep_subsamples_denser_recording_without_rewriting_time(self):
        r = run("x", [snapshot(t, .01*t, host_busy=.3) for t in range(0, 91, 5)], complete=True)
        d = self.evaluate(corpus(r), ["smc-prel3"])[0]["decisions"][0]
        self.assertEqual(d["status"], "PASS")
        self.assertTrue(d["coverage_complete"])

    def test_insufficient_startup_is_not_a_refusal(self):
        data = corpus(run("x", [snapshot(0, 0), snapshot(10, 0)]))
        d = self.evaluate(data, ["smc-prel3"])[0]
        self.assertEqual(d["decisions"][0]["status"], "UNMEASURED")

    def test_arm_requires_ready_or_cap_not_end_of_file(self):
        data = corpus(run("x", [snapshot(0, 0), snapshot(30, 0)]))
        d = self.evaluate(data, ["contention-arm"])[0]
        self.assertEqual(d["decisions"][0]["status"], "UNMEASURED")

    def test_arm_clean_dwell_and_dirty_cap(self):
        for rate, expected in ((.01, "PASS"), (.6, "REFUSE")):
            r = run("x", [snapshot(t, rate*t) for t in range(0, 181, 30)])
            r["thresholds"] = {"cap_s": 180}
            self.assertEqual(self.evaluate(corpus(r), ["contention-arm"])[0]["decisions"][0]["status"], expected)

    def test_missing_arm_snapshot_gap_never_counts_as_clean(self):
        r = run("x", [snapshot(0, 0), snapshot(180, 0)])
        self.assertEqual(self.evaluate(corpus(r), ["contention-arm"])[0]["decisions"][0]["status"], "UNMEASURED")

    def test_imported_display_and_thermal_predicates(self):
        reports = self.evaluate(synthetic_corpus(), ["display", "thermal"])
        self.assertEqual(reports[0]["decisions"][0]["status"], "PASS")
        self.assertEqual(reports[0]["decisions"][2]["status"], "REFUSE")
        self.assertEqual(reports[1]["decisions"][0]["status"], "PASS")
        self.assertEqual(reports[1]["decisions"][3]["status"], "REFUSE")

    def test_importable_adapter_interface_records_source_and_decision(self):
        g = self.evaluate(synthetic_corpus(), ["tests.test_guard_replay:custom_adapter"])[0]
        self.assertEqual(g["decisions"][3]["status"], "REFUSE")
        self.assertEqual(len(g["sources"][0]["sha256"]), 64)

    def test_custom_adapter_must_live_in_clone(self):
        with self.assertRaises(ValueError):
            self.evaluate(synthetic_corpus(), ["json:loads"])

    def test_historical_decision_dependencies_match_executable_ast(self):
        for era in replay.PINS:
            self.assertTrue(all(s["historical_dependency_ast_matches_current"]
                                for s in replay.historical_dependencies(era)))

    def test_request_predicate_preserves_missing_coverage_and_positive_evidence(self):
        for error, rate, expected in ((None, .01, "PASS"), ("missing", .01, "UNMEASURED"),
                                      ("missing", .6, "REFUSE")):
            r = run("x", [{"t": 30, "contention_interval": cpu(0, 30, rate, error=error)}])
            d = self.evaluate(corpus(r), ["contention-request"])[0]["decisions"][0]
            self.assertEqual(d["status"], expected)

    def test_many_snapshots_still_one_trial(self):
        r = run("x", [{"t": t, "pcpu_busy": []} for t in range(1000)])
        d = self.evaluate(corpus(r), ["quiet-pre691"])[0]
        self.assertEqual(d["strata"][0]["measured"], 1)

    def test_wilson_empty_and_boundaries(self):
        self.assertIsNone(replay.wilson(0, 0))
        self.assertAlmostEqual(replay.wilson(0, 59)[1], .06113, places=4)
        self.assertLess(replay.wilson(0, 73)[1], .05)
        self.assertGreater(replay.wilson(3, 3)[0], .43)

    def test_incident_and_synthetic_evidence_never_qualify(self):
        for stratum in ("recorded_incident", "synthetic"):
            data = corpus(*(run(str(i), [{"t": 0, "pcpu_busy": []}, {"t": 30, "pcpu_busy": []}],
                                complete=True, stratum=stratum) for i in range(80)))
            s = self.evaluate(data, ["quiet-pre691"])[0]["strata"][0]
            self.assertEqual(s["assessment"], "INSUFFICIENT")

    def test_complete_label_cannot_qualify_sparse_channel(self):
        data = corpus(*(run(str(i), [{"t": 0, "pcpu_busy": []}, {"t": 30, "pcpu_busy": []}],
                            complete=True, stratum="recorded_representative") for i in range(80)))
        s = self.evaluate(data, ["quiet-pre691"])[0]["strata"][0]
        self.assertEqual(s["complete_run_trials"], 0)
        self.assertEqual(s["assessment"], "INSUFFICIENT")

    def test_independent_complete_representative_trials_can_meet_idle_screen(self):
        data = corpus(*(run(str(i), [{"t": t, "pcpu_busy": []} for t in (0, 15, 30)],
                            complete=True, stratum="recorded_representative") for i in range(73)))
        s = self.evaluate(data, ["quiet-pre691"])[0]["strata"][0]
        self.assertEqual(s["complete_run_trials"], 73)
        self.assertEqual(s["assessment"], "WITHIN_BOUND")

    def test_unknown_labels_do_not_supply_benign_denominator(self):
        r = run("x", [{"t": 0, "pcpu_busy": []}], label="unknown")
        self.assertEqual(self.evaluate(corpus(r), ["quiet-pre691"])[0]["strata"][0]["metric"], "unlabelled_refusal")

    def test_validation_rejects_duplicate_runs_nonfinite_and_reverse_times(self):
        good = run("x", [{"t": 0}])
        with self.assertRaises(ValueError):
            replay.validate(corpus(good, good))
        for frames in ([{"t": math.nan}], [{"t": 1}, {"t": 0}]):
            with self.assertRaises(ValueError):
                replay.validate(corpus(run("x", frames)))

    def test_virtual_sampler_cannot_silently_fill_a_gap(self):
        t = replay.Tape(run("x", [{"t": 0, "x": 1}, {"t": 1, "x": 2}]))
        self.assertEqual(t.sample("x"), 1)
        t.sleep(3)
        with self.assertRaises(replay.MissingSample):
            t.sample("x")

    def test_projector_discards_outcomes_and_leaves_numbers_opaque_until_selected(self):
        data = json.loads('{"census":[{"monotonic_s":30,"busy":[[7,6,"mdworker"]]}],'
                          '"energy_j":12345,"checks":[]}', parse_int=OpaqueNumber)
        self.assertIsInstance(data["energy_j"], OpaqueNumber)
        projected = project_receipt(data, {"path": "docs/align/r0/synthetic/report.json"})
        self.assertNotIn("12345", json.dumps(projected))
        self.assertEqual(projected["frames"][0]["pcpu_busy"], [[7, 6, "mdworker"]])

    def test_uninjected_live_operations_are_blocked(self):
        with patch("joulewise.hazards.contention.take_snapshot", side_effect=AssertionError("live")), \
             patch("joulewise.measurement_liveness.census", side_effect=AssertionError("live")), \
             patch.object(Path, "home", side_effect=AssertionError("home")):
            self.evaluate(synthetic_corpus(), ["quiet-pre691", "quiet-l3", "smc-prel3", "smc-l3-redo"])

    def test_cli_refuses_outside_and_symlink_before_open(self):
        spec = importlib.util.spec_from_file_location("guard_replay_cli", replay.REPO / "scripts/guard_replay.py")
        cli = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cli)
        with patch.object(cli.os, "open", side_effect=AssertionError("must not open")):
            for path in ("/Users/edr/jw-b5-sealed/data.json", "restricted/data.json", "../x"):
                with self.subTest(path=path), self.assertRaises(ValueError):
                    cli.local_read(path)
        with tempfile.TemporaryDirectory(dir=replay.REPO) as tmp:
            link = Path(tmp) / "link"
            link.symlink_to("/Users/edr/jw-b5-sealed/never-follow")
            with self.assertRaises(OSError):
                cli.local_read(str(link))


if __name__ == "__main__":
    unittest.main()
