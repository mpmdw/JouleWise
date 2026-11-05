"""Synthetic-only SMC journal, pinned policy, custody and desk-reader checks."""
from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from joulewise.hazards import base, monitor, temperature
from joulewise.schemas import CampaignPolicy, SchemaError
from tests.hazards.test_monitor import FakeMac

POLICY = {"s_fast": "TG0D", "s_slow": "TH0P", "fan_keys": ["F0Ac", "F1Ac"], "r0_sha256": "a" * 64}
NS = 10 ** 9


class FakeSensors:
    def read(self, selected):
        values = {"TG0D": 50.0, "TH0P": 34.0, "F0Ac": 0, "F1Ac": 1200}
        return {"values": {k: values[k] for k in selected}, "errors": {}}


class TemperatureTests(unittest.TestCase):
    def test_bad_samples_are_null_zero_fan_and_constant_temperature_are_good(self):
        result = temperature.sample(FakeSensors(), temperature.keys(POLICY))
        self.assertEqual(result["sensors"]["F0Ac"], 0)
        self.assertEqual(result["errors"], {})
        bad = SimpleNamespace(read=lambda _: {"values": {"TG0D": float("nan"), "TH0P": 999}, "errors": {}})
        result = temperature.sample(bad, temperature.keys(POLICY))
        self.assertTrue(all(v is None for v in result["sensors"].values()))
        self.assertEqual(set(result["errors"]), set(temperature.keys(POLICY)))

    def test_backend_exceptions_are_journal_data(self):
        class Broken:
            def read(self, _):
                raise OSError("gone")
        result = temperature.sample(Broken(), ["TG0D"])
        self.assertIsNone(result["sensors"]["TG0D"])
        self.assertIn("gone", result["errors"]["TG0D"])

    def test_slot_coverage_includes_edges_failures_duplicates_and_stalls(self):
        stats = temperature.Coverage(100 * NS, ["TG0D", "F0Ac"])
        values = {"sensors": {"TG0D": 50, "F0Ac": 0}, "errors": {}}
        for second in (101, 101, 102, 105):
            stats.observe(second * NS, second * NS + 1, values)
        stats.observe(103 * NS, 103 * NS + 1, {"sensors": {"TG0D": 50, "F0Ac": None},
                                             "errors": {"F0Ac": "unreadable"}})
        stats.observe(104 * NS, 106 * NS, values)  # slow read never fills a slot
        report = stats.report(107 * NS)
        self.assertEqual(report["all_keys"]["expected_samples"], 7)
        self.assertEqual(report["all_keys"]["valid_samples"], 3)
        self.assertEqual(report["per_key"]["TG0D"]["sample_fraction"], 4 / 7)
        self.assertEqual(report["all_keys"]["gaps_ns"], [[100 * NS, 101 * NS],
                         [103 * NS, 105 * NS], [106 * NS, 107 * NS]])

    def test_empty_and_partial_spans(self):
        counter = temperature.Coverage(0, ["TG0D"])
        self.assertIsNone(counter.report(0)["all_keys"]["sample_fraction"])
        self.assertEqual(counter.report(NS + 1)["all_keys"]["expected_samples"], 2)
        with self.assertRaises(ValueError):
            counter.report(-1)

    def test_policy_validation(self):
        self.assertEqual(temperature.validate_policy(POLICY), POLICY)
        for field, bad in (("s_fast", "B0AC"), ("s_slow", "TG0D"), ("fan_keys", ["F0Ac", "F0Ac"]),
                           ("fan_keys", ["FNum"]), ("r0_sha256", "x"), ("s_fast", None)):
            with self.subTest(field=field, bad=bad), self.assertRaises(ValueError):
                temperature.validate_policy({**POLICY, field: bad})
        self.assertEqual(temperature.validate_policy({**POLICY, "fan_keys": []})["fan_keys"], [])

    def test_campaign_policy_extension_roundtrips_and_old_policy_omits_it(self):
        raw = json.loads(Path("tests/fixtures/campaign_policy_test.json").read_text())
        legacy = CampaignPolicy.from_mapping(raw).to_dict()
        self.assertNotIn("smc_temperature", legacy)
        policy = CampaignPolicy.from_mapping({**raw, "smc_temperature": POLICY})
        self.assertEqual(policy.to_dict()["smc_temperature"], POLICY)
        with self.assertRaises(SchemaError):
            CampaignPolicy.from_mapping({**raw, "smc_temperature": {}})

    def test_monitor_journal_uses_existing_custody_shape_and_desk_reader(self):
        from joulewise.b5.harvest import read_monitor_journal
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            mac = FakeMac(root)
            config = monitor.build_config(custody_dir=root, tree_roots=[4000], disk_targets=[],
                                          smc_temperature=POLICY)
            mon = monitor.Monitor(config, ctx=base.Context(clocks=mac.clocks, run=mac.runner),
                                  smc_reader=FakeSensors())
            mon.open_session()
            self.assertIn("temperature", mon.fast_tasks)
            start = mac.clocks.monotonic_ns()
            mon.tick(start, names=["temperature"])
            mac.clocks.advance(3)
            mon.tick(mac.clocks.monotonic_ns(), names=["temperature"])
            mon.close_session("test")
            path = root / "hazards/monitor/temperature.jsonl"
            lines, error = monitor.read_journal(path)
            self.assertIsNone(error)
            self.assertEqual([line["kind"] for line in lines], ["session_start", "reading", "reading", "session_end"])
            self.assertEqual(lines[0]["values"]["smc_temperature"], POLICY)
            expected_hash = hashlib.sha256(base.canonical_json(config)).hexdigest()
            self.assertEqual(lines[0]["values"]["config_sha256"], expected_hash)
            readings, malformed = read_monitor_journal(path, "temperature")
            self.assertEqual(malformed, 0)
            self.assertEqual(len(readings), 2)
            for line in lines:
                base.Stamp.from_json(line["started"])
                base.Stamp.from_json(line["finished"])
            self.assertLess(lines[-1]["values"]["coverage"]["all_keys"]["sample_fraction"], 1)
            self.assertIn("temperature", monitor.load_journals(root))

    def test_disabled_monitor_has_no_new_journal_or_probe(self):
        with tempfile.TemporaryDirectory() as directory:
            mac = FakeMac(Path(directory))
            mon = mac.monitor()
            self.assertNotIn("temperature", mon.due)
            mon.close_session("test")
            self.assertFalse((Path(directory) / "hazards/monitor/temperature.jsonl").exists())

    def test_desk_coverage_crosses_restart_gap(self):
        values = temperature.sample(FakeSensors(), ["TG0D"])
        lines = [{"module": "temperature", "kind": "reading", "session": str(i // 3),
                  "started": {"monotonic_ns": i * NS}, "finished": {"monotonic_ns": i * NS + 1},
                  "values": values} for i in (0, 1, 5, 6)]
        result = temperature.coverage(lines, 0, 7 * NS, ["TG0D"])["all_keys"]
        self.assertEqual(result["sample_fraction"], 4 / 7)
        self.assertEqual(result["gaps_ns"], [[2 * NS, 5 * NS]])


class DriverPolicyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.pack = self.root / "pack"
        self.pack.mkdir()
        self.policy = json.loads(Path("tests/fixtures/campaign_policy_test.json").read_text())
        self.policy["smc_temperature"] = copy.deepcopy(POLICY)
        self.raw = json.dumps(self.policy).encode()
        (self.root / "policy.json").write_bytes(self.raw)
        self.binding = {"path": "policy.json", "sha256": hashlib.sha256(self.raw).hexdigest()}
        self.plan = SimpleNamespace(measurement_root=str(self.root), hazard_window={
            "pack": {"pack_root": str(self.pack)}, "thresholds": {}, "bindings": {},
            "runs_roots": {"claim": str(self.root / "runs"), "bound": str(self.root / "bound")},
            "window_env": {"path": str(self.root / "window.env")}})

    def write_tree(self):
        (self.pack / "plan_tree.json").write_text(json.dumps({"campaign_policy": self.binding}))

    def test_driver_reads_pinned_policy_and_passes_it_to_monitor(self):
        from joulewise.b5.driver import MonitorRequest, production_seams
        self.write_tree()
        request = MonitorRequest(self.plan, self.root / "plan.json", self.root, self.root / "night", 123)
        seam = production_seams(Path.cwd())
        argv = seam.monitor_argv(request)
        self.assertIn("--config", argv)
        config = json.loads((self.root / "hazards/monitor/config.json").read_text())
        self.assertEqual(config["smc_temperature"], POLICY)
        self.assertEqual(seam.monitor_argv(request), argv)
        # Config custody is create-once: an existing different key set is an error.
        config["smc_temperature"]["s_fast"] = "TC0D"
        (self.root / "hazards/monitor/config.json").write_text(json.dumps(config))
        with self.assertRaisesRegex(ValueError, "existing monitor config"):
            seam.monitor_argv(request)

    def test_changed_policy_cannot_silently_disable_journaling(self):
        from joulewise.b5.driver import monitor_temperature_policy
        self.write_tree()
        (self.root / "policy.json").write_text("{}")
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            monitor_temperature_policy(self.plan)

    def test_legacy_pack_is_disabled_and_absolute_policy_is_rejected(self):
        from joulewise.b5.driver import monitor_temperature_policy
        self.assertIsNone(monitor_temperature_policy(self.plan))
        self.binding["path"] = str(self.root / "policy.json")
        self.write_tree()
        with self.assertRaisesRegex(ValueError, "relative"):
            monitor_temperature_policy(self.plan)
