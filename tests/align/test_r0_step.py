"""Synthetic step responses only: no native imports, wall-clock waits or data."""
import hashlib
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.r0_host import smc_enumeration
from joulewise.align.r0_runner import execute, main, validate_config
from joulewise.align.r0_step import DEFAULT_PROFILE, ProfileRefused, profile_config, rank_response, step_budget
from tests.align.test_r0_checks import FakeBackend, FakeGuard, config_at


def synthetic_capture(taus, profile=None):
    """Independent analytic first-order pulse at 1 Hz, with realistic stamps."""
    profile = profile_config(profile)
    idle, load, recovery = (profile[k] for k in ("idle_seconds", "load_seconds", "recovery_seconds"))
    total = idle + load + recovery
    origin = 10_000_000_000
    samples = []
    for second in range(total):
        t = second + .1
        phase = "idle" if t < idle else "load" if t < idle + load else "recovery"
        values = {}
        for key, tau in taus.items():
            if phase == "idle":
                rise = 0.0
            elif phase == "load":
                rise = 10 * (1 - math.exp(-(t - idle) / tau))
            else:
                rise = 10 * (1 - math.exp(-load / tau)) * math.exp(-(t - idle - load) / tau)
            values[key] = 40 + rise
        samples.append({"kind": "reading", "phase": phase, "elapsed_s": t,
                        "started": {"monotonic_ns": origin + round(t * 1e9)},
                        "finished": {"monotonic_ns": origin + round((t + .01) * 1e9)},
                        "values": {"sensors": values, "errors": {}}})
    return {"schema": "joulewise.align_smc_r0.v1", "gpu_step": True,
            "inventory": {"keys": [{"key": key, "unit": "degC"} for key in taus]},
            "started": {"monotonic_ns": origin},
            "phases": [{"phase": "idle", "start_s": 0, "end_s": idle},
                       {"phase": "load", "start_s": idle, "end_s": idle + load},
                       {"phase": "recovery", "start_s": idle + load, "end_s": total}],
            "response": {"s_fast": None, "s_slow": None},
            "coverage": {"period_ns": 1_000_000_000, "per_key": {
                key: {"expected_samples": total, "valid_samples": total} for key in taus}}}, samples


def write_capture(output, taus=None, profile=None):
    payload, samples = synthetic_capture(taus or {"TC0P": 20, "TH0P": 400}, profile)
    raw = ("\n".join(json.dumps(s) for s in samples) + "\n").encode()
    payload.update(samples_journal="samples.jsonl", samples_sha256=hashlib.sha256(raw).hexdigest())
    (output / "samples.jsonl").write_bytes(raw)
    (output / "r0.json").write_text(json.dumps(payload))
    return payload


class StepTest(unittest.TestCase):
    def test_defaults_and_budget_include_full_thirty_minutes(self):
        config = validate_config(config_at(Path("/tmp/synthetic-r0")))
        self.assertEqual(config["smc_step"], DEFAULT_PROFILE)
        self.assertEqual(step_budget()["capture_seconds"], 1800)
        self.assertEqual(step_budget()["timeout_seconds"], 2400)
        self.assertEqual(step_budget()["journal_bytes_estimate"], 1800 * 16_384)

    def test_short_configured_load_refuses_with_code_before_any_capture(self):
        for load in (60, 120, 600, 899):
            with self.subTest(load=load):
                config = config_at(Path("/tmp/synthetic-r0"))
                config["smc_step"] = {"load_seconds": load}
                with self.assertRaises(ProfileRefused) as caught:
                    validate_config(config)
                self.assertEqual(caught.exception.code, "smc_step.load_below_tau_upper_bound")
                self.assertIn("900 s", str(caught.exception))
                with patch("joulewise.align.r0_host.subprocess.run") as run:
                    result = smc_enumeration(Path("/tmp/synthetic-r0"), Path("/tmp/unused"), config["smc_step"])
                run.assert_not_called()
                self.assertEqual(result["status"], "refused")
                self.assertEqual(result["refusal_code"], caught.exception.code)

    def test_invalid_duration_types_and_unknown_fields_refuse(self):
        for value in ({"load_seconds": True}, {"idle_seconds": 0}, {"recovery_seconds": -1},
                      {"idle_seconds": 300.5}, {"load_seconds": float("nan")}, {"load": 900}, []):
            with self.subTest(value=value), self.assertRaises(ProfileRefused):
                profile_config(value)

    def test_runner_records_refusal_before_probes_or_backend(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = config_at(root)
            config["smc_step"] = {"load_seconds": 60}
            with patch("joulewise.align.r0_runner.host_snapshot") as host, patch.object(FakeBackend, "__init__") as load:
                result = execute(config, root, ["host", "smc", "load"], ["D"],
                                 guard=FakeGuard(), backend_factory=FakeBackend)
            host.assert_not_called()
            load.assert_not_called()
            self.assertEqual(result["status"], "refused")
            saved = json.loads((root / "report.json").read_text())
            self.assertEqual(saved["refusal_code"], "smc_step.load_below_tau_upper_bound")

    def test_runner_passes_configured_profile_and_reports_scaled_budget(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = config_at(root)
            profile = {"idle_seconds": 400, "load_seconds": 1200, "recovery_seconds": 700}
            config["smc_step"] = profile
            with patch("joulewise.align.r0_runner.smc_enumeration", return_value={"status": "pass"}) as smc:
                result = execute(config, root, ["smc"], ["D"], guard=FakeGuard(), backend_factory=FakeBackend)
            self.assertEqual(result["status"], "pass")
            self.assertEqual(smc.call_args.args[2], profile)
            saved = json.loads((root / "report.json").read_text())
            self.assertEqual(saved["smc_step_budget"]["capture_seconds"], 2300)
            self.assertEqual(saved["smc_step_budget"]["journal_bytes_estimate"], 2300 * 16_384)

    def test_cli_short_profile_refuses_before_guard_construction(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = config_at(root)
            config["smc_step"] = {"load_seconds": 60}
            source = root / "config.json"
            source.write_text(json.dumps(config))
            with patch("sys.stderr") as stderr, patch("tests.align.test_r0_step.FakeGuard") as guard:
                with self.assertRaises(SystemExit) as caught:
                    main(["--config", str(source), "--output", str(root / "unused")], guard_factory=guard)
            self.assertEqual(caught.exception.code, 2)
            guard.assert_not_called()
            self.assertIn("smc_step.load_below_tau_upper_bound", "".join(c.args[0] for c in stderr.write.call_args_list))

    def test_ruled_profile_resolves_tau_60_and_400_without_calling_60_fast(self):
        capture, samples = synthetic_capture({"TM0P": 60, "TH0P": 400})
        result = rank_response(capture, samples)
        for row, tau in zip(result["ranking"], (60, 400)):
            self.assertEqual(row["load_fit"]["status"], "pass")
            self.assertAlmostEqual(row["load_fit"]["tau_s"], tau, delta=tau * .01)
            self.assertGreater(row["recovery_r2"], .99)
        self.assertEqual(result["s_slow"], "TH0P")
        self.assertIsNone(result["s_fast"])  # tau=60 violates the strict <30 s role bar.
        self.assertEqual(result["status"], "inconclusive")

    def test_fast_and_slow_roles_pass_with_20_and_400(self):
        capture, samples = synthetic_capture({"TC0P": 20, "TH0P": 400})
        result = rank_response(capture, samples)
        self.assertEqual((result["status"], result["s_fast"], result["s_slow"]), ("pass", "TC0P", "TH0P"))

    def test_slow_tau_can_exceed_recovery_but_not_ruled_upper_bound(self):
        for tau, expected in ((800, "TH0P"), (1000, None)):
            capture, samples = synthetic_capture({"TH0P": tau})
            result = rank_response(capture, samples)
            self.assertEqual(result["s_slow"], expected)

    def test_fast_fit_uses_only_first_120_load_seconds(self):
        capture, samples = synthetic_capture({"TC0P": 20})
        for sample in samples:
            if sample["phase"] == "load" and sample["elapsed_s"] >= 420:
                sample["values"]["sensors"]["TC0P"] += 20
        result = rank_response(capture, samples)
        self.assertEqual(result["s_fast"], "TC0P")
        self.assertEqual(result["ranking"][0]["fast_load_fit"]["fit_seconds"], 120)

    def test_recovery_confirms_but_does_not_change_load_tau(self):
        capture, samples = synthetic_capture({"TH0P": 400})
        before = rank_response(capture, samples)["ranking"][0]["load_fit"]
        for sample in samples:
            if sample["phase"] == "recovery":
                sample["values"]["sensors"]["TH0P"] = 40
        result = rank_response(capture, samples)
        self.assertEqual(result["ranking"][0]["load_fit"], before)
        self.assertIsNone(result["s_slow"])

    def test_missing_slots_and_phase_mismatch_cannot_qualify(self):
        capture, samples = synthetic_capture({"TC0P": 20, "TH0P": 400})
        short = [s for s in samples if s["phase"] != "recovery" or s["elapsed_s"] < 1250]
        self.assertEqual(rank_response(capture, short)["status"], "inconclusive")
        capture["phases"][1]["end_s"] -= 1
        with self.assertRaisesRegex(ValueError, "durations do not match"):
            rank_response(capture, samples)


if __name__ == "__main__":
    unittest.main()
