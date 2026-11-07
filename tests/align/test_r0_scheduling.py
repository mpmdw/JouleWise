"""R0 wall-time policy with synthetic backends; no native probes or data."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align import r0, r0_runner
from tests.align.test_r0_checks import FakeBackend, FakeGuard, config_at, patch_references


class SchedulingTest(unittest.TestCase):
    def setUp(self):
        for name, status in (("host_snapshot", "pass"), ("host_identity", "pass"),
                             ("disk_census", "diagnostic"), ("smc_enumeration", "pass")):
            probe = patch.object(r0_runner, name, return_value={"status": status, "fake": True})
            probe.start()
            self.addCleanup(probe.stop)
        patch_references(self)

    def run_fake(self, root, checks=None, **kwargs):
        return r0_runner.execute(config_at(root), root, list(r0_runner.CHECKS) if checks is None else checks,
                                 ["D"], guard=FakeGuard(), backend_factory=kwargs.pop("backend_factory", FakeBackend),
                                 **kwargs)

    def test_canonical_order_even_for_reversed_subset_and_unloaded_smc(self):
        backends = []
        class Backend(FakeBackend):
            def __init__(self, *args):
                super().__init__(*args)
                backends.append(self)

        def smc(*args):
            self.assertEqual(backends, [])
            return {"status": "pass"}

        with tempfile.TemporaryDirectory() as tmp, patch.object(r0_runner, "smc_enumeration", side_effect=smc):
            report = self.run_fake(Path(tmp), list(reversed(r0_runner.CHECKS)), backend_factory=Backend)
        self.assertEqual(report["status"], "pass")
        self.assertEqual([r["check"] for r in report["checks"]], [
            "smc", "host", "disk", "host-identity", "model-load", "load", "template", "generated",
            "checkpoint", "memory", "ladder", "long-decode", "tool-envelopes"])
        # SMC now precedes every load; the model needs exactly one lifetime.
        self.assertEqual(len(backends), 1)
        self.assertTrue(all(backend.closed for backend in backends))

    def test_each_early_failure_saves_report_and_stops_remaining_phases(self):
        cases = ((r0_runner, "host_snapshot", "host", "fail"),
                 (r0_runner, "disk_census", "disk", "fail"),
                 (r0_runner, "host_identity", "host-identity", "fail"),
                 (FakeBackend, "device_info", "model-load", "fail"),
                 (r0, "load_coherence", "load", "fail"),
                 (r0, "template_rewrites", "template", "fail"),
                 (r0, "generated_rewrites", "generated", "inconclusive"),
                 (r0, "checkpoint_verdict", "checkpoint", "inconclusive"),
                 (r0, "memory_peak", "memory", "fail"),
                 (r0_runner, "smc_enumeration", "smc", "fail"))
        for owner, name, check, status in cases:
            with self.subTest(check=check), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                with patch.object(owner, name, return_value={"status": status}), \
                        patch.object(r0, "ladder") as ladder, patch.object(r0, "long_decode") as long_decode:
                    report = self.run_fake(root)
                ladder.assert_not_called()
                long_decode.assert_not_called()
                self.assertEqual(report["status"], "fail")
                self.assertFalse(report["complete_r0"])
                self.assertEqual(report["checks"][-1]["check"], check)
                self.assertEqual(report["stopped_after"]["check"], check)
                self.assertEqual(json.loads((root / "report.json").read_text()), report)
                self.assertIn("Status: **fail**", (root / "report.md").read_text())
                self.assertTrue(all("check_seconds" in row for row in report["checks"]))
                self.assertGreaterEqual(report["total_seconds"], 0)

    def test_opus_f3_smc_inconclusive_still_runs_host_disk_and_models(self):
        # Opus order.py: the full CHECKS list with default fail-fast must
        # record inconclusive SMC and continue all independent checks.
        with tempfile.TemporaryDirectory() as tmp, patch.object(
                r0_runner, 'smc_enumeration', return_value={'status': 'inconclusive'}):
            report = self.run_fake(Path(tmp))
        self.assertEqual(report['checks'][0]['status'], 'inconclusive')
        self.assertNotIn('stopped_after', report)
        names = [r['check'] for r in report['checks']]
        for name in ('host', 'disk', 'host-identity', 'model-load', 'load', 'memory', 'ladder', 'long-decode'):
            self.assertIn(name, names)
        self.assertEqual(report['status'], 'pass')
        self.assertFalse(report['complete_r0'])  # injected backend never certifies live R0

    def test_keep_going_runs_later_checks_after_failure_and_still_fails(self):
        with tempfile.TemporaryDirectory() as tmp, \
                patch.object(r0, "template_rewrites", side_effect=ValueError("synthetic failure")):
            root = Path(tmp)
            report = self.run_fake(root, keep_going=True)
            saved = json.loads((root / "report.json").read_text())
        self.assertEqual(report, saved)
        self.assertEqual(report["status"], "fail")
        self.assertNotIn("stopped_after", report)
        self.assertIn("long-decode", [r["check"] for r in report["checks"]])
        self.assertIn("ValueError: synthetic failure", next(r["error"] for r in report["checks"] if r["check"] == "template"))

    def test_keep_going_never_bypasses_host_identity_gate(self):
        with tempfile.TemporaryDirectory() as tmp, \
                patch.object(r0_runner, "host_identity", return_value={"status": "fail"}), \
                patch.object(FakeBackend, "__init__") as load:
            report = self.run_fake(Path(tmp), keep_going=True)
        load.assert_not_called()
        self.assertEqual(report["status"], "fail")
        names = [row["check"] for row in report["checks"]]
        self.assertLess(names.index("smc"), names.index("memory"))
        self.assertLess(names.index("smc"), names.index("ladder"))
        self.assertTrue(all(row["status"] == "blocked" for row in report["checks"] if row["check"] in {
            "load", "template", "generated", "memory", "ladder", "long-decode"}))

    def test_smc_only_does_not_load_or_probe_model_identity(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(FakeBackend, "__init__") as load, \
                patch.object(r0_runner, "host_identity") as identity:
            report = self.run_fake(Path(tmp), ["smc"])
        load.assert_not_called()
        identity.assert_not_called()
        self.assertEqual([r["check"] for r in report["checks"]], ["smc"])
        self.assertEqual(report["status"], "pass")

    def test_keep_going_still_stops_on_census_refusal_and_times_the_phase(self):
        with tempfile.TemporaryDirectory() as tmp, \
                patch.object(r0, "memory_peak", side_effect=r0_runner.Refused("census changed")), \
                patch.object(r0, "ladder") as ladder:
            root = Path(tmp)
            report = self.run_fake(root, ["memory", "ladder"], keep_going=True)
            self.assertEqual(json.loads((root / "report.json").read_text()), report)
        ladder.assert_not_called()
        self.assertEqual(report["status"], "refused")
        self.assertEqual(report["checks"][-1]["status"], "refused")
        self.assertIn("check_seconds", report["checks"][-1])
        self.assertGreaterEqual(report["total_seconds"], report["checks"][-1]["check_seconds"])

    def test_each_phase_and_total_measure_elapsed_wall_time_including_cleanup(self):
        for failed in (False, True):
            with self.subTest(failed=failed), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                elapsed = [0.0]
                def advance(seconds):
                    elapsed[0] += seconds
                def host():
                    advance(3)
                    return {"status": "pass"}
                class Backend(FakeBackend):
                    def device_info(self):
                        advance(2)
                        return super().device_info()
                    def memory_peak(self, **kwargs):
                        advance(5)
                        result = super().memory_peak(**kwargs)
                        if failed:
                            result["errors"] = ["synthetic failure"]
                        return result
                    def close(self):
                        advance(7)
                        super().close()
                with patch.object(r0_runner.time, "monotonic", side_effect=lambda: elapsed[0]), \
                        patch.object(r0_runner, "host_snapshot", side_effect=host):
                    report = self.run_fake(root, ["host", "memory"], backend_factory=Backend)
                self.assertEqual([row["check_seconds"] for row in report["checks"]], [3, 0, 2, 5])
                self.assertEqual(report["total_seconds"], 17)
                self.assertEqual(report["status"], "fail" if failed else "pass")
                self.assertEqual(json.loads((root / "report.json").read_text())["total_seconds"], 17)
                markdown = (root / "report.md").read_text()
                self.assertIn("Total wall duration: 17.000 seconds", markdown)
                self.assertIn("| memory | D | " + ("fail" if failed else "pass") + " | 5.000 |", markdown)

    def test_cli_options_reach_runner_and_retry_can_be_disabled(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "config.json"
            config.write_text(json.dumps(config_at(root)))
            good = FakeBackend().long_decode(eval_metadata=False)
            with patch.object(FakeBackend, "long_decode", return_value={**good, "errors": ["synthetic failure"]}) as probe:
                code = r0_runner.main(["--config", str(config), "--output", str(root / "output"),
                                       "--checks", "long-decode", "--keep-going", "--long-decode-attempts", "1"],
                                      backend_factory=FakeBackend, guard_factory=FakeGuard, lock_path=root / "r0.lock")
            report = json.loads((root / "output/report.json").read_text())
        self.assertEqual(code, 2)
        self.assertTrue(report["keep_going"])
        self.assertEqual(report["long_decode_max_attempts"], 1)
        self.assertEqual(probe.call_count, 1)


class GenerationSchedulingTest(unittest.TestCase):
    def test_xhigh_pass_records_skipped_rungs_without_running_them(self):
        backend = FakeBackend()
        episode = {"turns": [{"hit_cap": False, "closed_reasoning": True, "reasoning_tokens": 1000}]}
        with patch.object(r0, "screen_episode", return_value=episode) as run:
            result = r0.ladder(backend, "D")
        self.assertEqual(run.call_count, 2)  # Both required pairs on the selected rung.
        self.assertEqual(backend.sessions, [None, None])
        self.assertEqual(result["selected"], "xhigh")
        self.assertEqual([r["rung"] for r in result["rungs"]], ["xhigh", "medium", "low"])
        for row in result["rungs"][1:]:
            self.assertEqual(row["status"], "not_run")
            self.assertEqual(row["reason"], "not run: higher rung passed")
            self.assertEqual(row["episodes"], [])
        markdown = r0.markdown({"status": "pass", "checks": [{"check": "ladder", **result}]})
        self.assertEqual(markdown.count("not run: higher rung passed"), 2)

    def test_long_decode_pass_runs_exactly_one_attempt_and_one_deadline_unit(self):
        backend = FakeBackend()
        with patch.object(backend, "long_decode", wraps=backend.long_decode) as probe, \
                patch.object(r0_runner, "deadline", wraps=r0_runner.deadline) as timer, \
                tempfile.TemporaryDirectory() as tmp, \
                patch.object(r0_runner, "host_identity", return_value={"status": "pass"}):
            report = r0_runner.execute(config_at(Path(tmp)), Path(tmp), ["long-decode"], ["D"],
                                       guard=FakeGuard(), backend_factory=lambda *args: backend, per_check_timeout=37)
        probe.assert_called_once_with(eval_metadata=False)
        self.assertEqual(timer.call_count, 3)  # Identity, model load, one decode attempt.
        self.assertTrue(all(call.args == (37,) for call in timer.call_args_list))
        self.assertEqual(len(report["checks"][-1]["attempts"]), 1)
        self.assertEqual(report["status"], "pass")

    def test_long_decode_failure_retries_once_with_unchanged_per_attempt_timeout(self):
        backend = FakeBackend()
        good = {**backend.long_decode(eval_metadata=True), "metadata_arrays_evaluated": 2}
        with patch.object(backend, "long_decode", side_effect=[{**good, "errors": ["failure"]}, good]) as probe, \
                patch.object(r0_runner, "deadline", wraps=r0_runner.deadline) as timer, \
                tempfile.TemporaryDirectory() as tmp, \
                patch.object(r0_runner, "host_identity", return_value={"status": "pass"}):
            report = r0_runner.execute(config_at(Path(tmp)), Path(tmp), ["long-decode"], ["D"],
                                       guard=FakeGuard(), backend_factory=lambda *args: backend, per_check_timeout=37)
        self.assertEqual([call.kwargs for call in probe.call_args_list], [{"eval_metadata": False}, {"eval_metadata": True}])
        self.assertEqual(timer.call_count, 4)
        self.assertTrue(all(call.args == (37,) for call in timer.call_args_list))
        self.assertEqual(report["status"], "pass")
        self.assertTrue(report["checks"][-1]["metadata_eval_required"])

    def test_long_decode_disabled_retry_preserves_failure_and_rejects_invalid_limits(self):
        backend = FakeBackend()
        good = backend.long_decode(eval_metadata=False)
        with patch.object(backend, "long_decode", return_value={**good, "errors": ["failure"]}) as probe:
            result = r0.long_decode(backend, max_attempts=1)
        self.assertEqual(result["status"], "fail")
        self.assertEqual(probe.call_count, 1)
        self.assertEqual(len(result["attempts"]), 1)
        for limit in (0, 3):
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                r0.long_decode(backend, max_attempts=limit)


if __name__ == "__main__":
    unittest.main()
