"""RC-CMP-2 M3/M4: the release bar set and the comparator's whole-machine meter line.

The member fixture carries a raw synthetic KM003C stream; its harvest meter record
is written by the parser (joulewise.external.km003c_parse, the reference) and the
recompute runs on the same archive. Each planted fault moves one value by twice its
family bar and is shown passing with the bar disabled (counterfactual).
"""
import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from .support import ROOT, recompute as r, run_cli
from . import test_auditfix, test_comparator
from .test_comparator import BARS, RULES, SHA, cmp

RELEASE = ROOT / "configs/analysis/b5/recompute_bars.json"
MACHINE_RULES = tuple(rule for rule in cmp.COVERAGE if rule[0].startswith("disclosure:window_lines")
                      or rule[1] == cmp.TEXT)


class ReleaseBarsTests(unittest.TestCase):
    def test_release_bars_equal_the_coded_set_plus_meter_families_with_derivations(self):
        release = json.loads(RELEASE.read_text())
        coded = json.loads(BARS["recompute_coded_7e322b76"].read_text())
        self.assertEqual(release["schema"], coded["schema"])
        self.assertEqual(release["rule"], coded["rule"])
        bars = {family: {k: v for k, v in spec.items() if k != "derivation"}
                for family, spec in release["families"].items()}
        self.assertEqual({f: bars[f] for f in coded["families"]}, coded["families"])
        self.assertEqual(set(bars) - set(coded["families"]), set(cmp.METER))
        self.assertEqual(bars["rho"], {"relative": 0.0, "absolute": 1e-6})
        for family in ("meter_j", "meter_w", "machine_j"):
            self.assertEqual(bars[family], {"relative": 1e-6, "absolute": 1e-6})
        # RC-CMP-3 X8: a legacy wall-placed window edge, 1e-6 s on the edge difference (7e322b76).
        self.assertEqual(bars["window_edge_s"], {"relative": 0.0, "absolute": 1e-6})
        self.assertTrue(all(isinstance(spec.get("derivation"), str) and spec["derivation"]
                            for spec in release["families"].values()))
        cmp.load_bars(RELEASE)

    def test_release_bars_are_the_comparator_default(self):
        self.assertEqual(cmp.DEFAULT_BARS, RELEASE)
        self.assertEqual(cmp.run.__defaults__[0], RELEASE)
        # The CLI default: --bars may be omitted.
        case = test_comparator.ComparatorTests("test_baseline_agrees_under_both_bar_sets")
        case.setUp()
        self.addCleanup(case.tmp.cleanup)
        ours = case.root / "o.json"
        ours.write_text(json.dumps(case.ours))
        out, restricted = io.StringIO(), case.root / "restricted.json"
        with mock.patch.object(cmp, "COVERAGE", RULES), contextlib.redirect_stdout(out):
            code = cmp.main(["--l9-custody", str(case.custody()), "--recompute", str(ours),
                             "--restricted-out", str(restricted)])
        self.assertEqual(code, 0, out.getvalue())
        self.assertIn("bar_set=b5_release_recompute_coded_7e322b76 ", out.getvalue())
        self.assertEqual(json.loads(restricted.read_text())["bar_set"], "b5_release_recompute_coded_7e322b76")

    def test_s13_set_stays_in_tests_as_block_6(self):
        self.assertTrue(BARS["s13_block6"].is_file())
        self.assertFalse((ROOT / "configs/analysis/b5/s13_block6.json").exists())


class MeterLineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        root = Path(cls.temp.name)
        holder = type("Holder", (), {"root": root})()
        archive, cls.rid, cls.recorded, _ = test_auditfix.AuditFixTests.machine_archive(holder)
        _, output, _ = run_cli({"ALPHA": archive}, root / "recompute.json", ("--member-detail",))
        whole_machine = output["disclosures"]["whole_machine"]
        # The fixture's harvest record holds one member; L9's disclosure and the recompute's
        # window then hold that member too (X3 requires equal member sets).
        members = whole_machine["windows"]["ALPHA"]["members"]
        whole_machine["windows"]["ALPHA"]["members"] = {cls.rid: members[cls.rid]}
        # A clean window (no battery activity), so the recompute sets the central band L9's line
        # prints; the comparator takes the band's window from the recompute (RC-CMP-5 S2).
        members[cls.rid]["phases"]["request"]["battery_activity"]["active"] = False
        whole_machine["request_cross_check"] = r.request_cross_check(whole_machine["windows"])
        cls.whole_machine = whole_machine

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.case = test_comparator.ComparatorTests("test_baseline_agrees_under_both_bar_sets")
        self.case.setUp()
        self.addCleanup(self.case.tmp.cleanup)
        self.record = copy.deepcopy(self.recorded)
        row = self.record["members"][self.rid]
        # L9's step-11 machine lines, in the shape disclosures._machine_lines writes.
        lines = [{"line": "machine_member", "restricted": True, "label": "machine_member", "text": "synthetic",
                  "model": "qwen3-1p7b", "run_id": self.rid, "rho": row["rho"], "rail_j": row["rail_delta_J"],
                  "machine_j": row["machine"]["delta_J"], "removed": False, "plausible": True, "meter_flags": [],
                  "battery_term_available": row["machine"]["battery_term_available"]},
                 {"line": "machine_summary", "restricted": True, "label": "machine_summary", "text": "synthetic",
                  "model": "qwen3-1p7b", "median": row["rho"], "minimum": row["rho"], "maximum": row["rho"],
                  "q25": row["rho"], "q75": row["rho"], "spread": 0.0,
                  "central_band": {"pack": "alpha", "plan_id": "fixture", "attempt": 1,
                                   "lower": row["rho"], "upper": row["rho"]}}]
        # RC-CMP-8: placed before the window's other producer lines (below_screen_bound, NEG-8), which every
        # window prints; the machine lines keep positions 0 and 1.
        self.case.files[f"disclosures/{SHA}.json"]["window_lines"]["alpha"][:0] = lines
        self.case.ours["disclosures"]["whole_machine"] = copy.deepcopy(self.whole_machine)

    def compare(self, bars=RELEASE, meter=True):
        harvest = self.case.root / "harvest-meter.json"
        harvest.write_text(json.dumps(self.record))
        ours = self.case.root / "ours.json"
        ours.write_text(json.dumps(self.case.ours))
        return cmp.run(self.case.custody(), ours, bars, RULES + MACHINE_RULES,
                       meter=["alpha=" + str(harvest)] if meter else ())

    def fails(self, result):
        return {family: n["fail"] for family, n in result["counts"].items() if n["fail"]}

    def test_meter_line_agrees_and_is_covered(self):
        result = self.compare()
        self.assertEqual(self.fails(result), {})
        self.assertEqual(result["coverage"]["unmapped"], [])
        for family in ("meter_j", "meter_w", "machine_j", "rho", "battery_term"):
            self.assertGreater(result["counts"][family]["pass"], 0, family)
        keys = {row["key"] for row in result["comparisons"]}
        prefix = f"meter/alpha/{self.rid}/request/"
        self.assertTrue({prefix + k for k in ("meter/energy_J", "meter/baseline_W", "meter/n", "rho",
                                              "battery/delta_J", "window_ns/start", "window_ns/end")} <= keys)
        self.assertIn(f"machine/alpha/{self.rid}/request/rho", keys)
        self.assertEqual(result["coverage"]["leaves"]["disclosure:window_lines/alpha/machine_member/rho"], "rho")
        self.assertEqual(len(result["harvest_meter_sha256"]["alpha"]), 64)

    def planted(self, family, edit):
        edit()
        self.assertEqual(self.fails(self.compare()), {family: 1})
        with mock.patch.object(cmp, "bar_for", return_value=float("inf")):
            self.assertEqual(self.fails(self.compare()), {})

    def twice_bar(self, family, value):
        spec = json.loads(RELEASE.read_text())["families"][family]
        return value + 2 * max(spec["absolute"], spec["relative"] * abs(value))

    def test_planted_gross_meter_energy(self):
        meter = self.record["members"][self.rid]["machine"]["meter"]
        self.planted("meter_j", lambda: meter.update(energy_J=self.twice_bar("meter_j", meter["energy_J"])))

    def test_planted_meter_baseline_power(self):
        meter = self.record["members"][self.rid]["machine"]["meter"]
        self.planted("meter_w", lambda: meter.update(baseline_W=self.twice_bar("meter_w", meter["baseline_W"])))

    def test_planted_rho_in_disclosure(self):
        line = self.case.files[f"disclosures/{SHA}.json"]["window_lines"]["alpha"][0]
        self.planted("rho", lambda: line.update(rho=self.twice_bar("rho", line["rho"])))

    def test_planted_rho_on_the_recompute_side(self):
        own = self.case.ours["disclosures"]["whole_machine"]["windows"]["ALPHA"]["members"][self.rid]["phases"]["request"]
        # Both L9 member rows (disclosure and harvest record) see the moved value, and so do the
        # five order statistics and two band bounds re-derived from it (X2); the spread stays 0.
        own["rho"] = self.twice_bar("rho", own["rho"])
        self.assertEqual(self.fails(self.compare()), {"rho": 9})
        with mock.patch.object(cmp, "bar_for", return_value=float("inf")):
            self.assertEqual(self.fails(self.compare()), {})

    def test_planted_machine_delta(self):
        line = self.case.files[f"disclosures/{SHA}.json"]["window_lines"]["alpha"][0]
        self.planted("machine_j", lambda: line.update(machine_j=self.twice_bar("machine_j", line["machine_j"])))

    def test_planted_meter_sample_count(self):
        meter = self.record["members"][self.rid]["machine"]["meter"]
        self.planted("count", lambda: meter.update(n=meter["n"] + 1))

    def test_missing_harvest_record_disagrees(self):
        self.assertEqual(self.fails(self.compare(meter=False)), {"meter_j": 1})

    def test_bar_set_without_meter_families_refuses_a_meter_line(self):
        with self.assertRaisesRegex(cmp.Refusal, "bars_family_missing:rho"):
            self.compare(bars=BARS["s13_block6"])

    def test_mapped_meter_leaf_not_compared_refuses(self):
        # Counterfactual for coverage: without compare_machine the mapped rho leaf is not coverage.
        with mock.patch.object(cmp, "compare_machine", lambda *args: None):
            result = self.compare()
        self.assertIn("disclosure:window_lines/alpha/machine_member/rho", result["coverage"]["uncompared"])


if __name__ == "__main__":
    unittest.main()
