"""Synthetic-only ALIGN samples, config slots and desk coverage checks."""
from __future__ import annotations

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
    def close(self):
        pass

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
        self.assertEqual(report["all_keys"]["gaps_ns"], [[102 * NS, 105 * NS], [105 * NS, 107 * NS]])

    def test_empty_and_partial_spans(self):
        counter = temperature.Coverage(0, ["TG0D"])
        self.assertIsNone(counter.report(0)["all_keys"]["sample_fraction"])
        self.assertEqual(counter.report(NS + 1)["all_keys"]["expected_samples"], 1)
        with self.assertRaises(ValueError):
            counter.report(-1)

    def test_policy_validation(self):
        self.assertEqual(temperature.validate_policy(POLICY), POLICY)
        for field, bad in (("s_fast", "B0AC"), ("s_slow", "TG0D"), ("fan_keys", ["F0Ac", "F0Ac"]),
                           ("fan_keys", ["FNum"]), ("r0_sha256", "x"), ("s_fast", None)):
            with self.subTest(field=field, bad=bad), self.assertRaises(ValueError):
                temperature.validate_policy({**POLICY, field: bad})
        self.assertEqual(temperature.validate_policy({**POLICY, "fan_keys": []})["fan_keys"], [])

    def test_campaign_policy_does_not_own_align_config_slots(self):
        raw = json.loads(Path("tests/fixtures/campaign_policy_test.json").read_text())
        self.assertNotIn("smc_temperature", CampaignPolicy.from_mapping(raw).to_dict())
        with self.assertRaises(SchemaError):
            CampaignPolicy.from_mapping({**raw, "smc_temperature": POLICY})

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
        self.assertEqual(result["gaps_ns"], [[NS, 5 * NS]])
