"""Block-six clock policy reaches the driver without changing block-five sizing."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from joulewise.b5 import plan
from joulewise.b6 import plan_inputs, precheck
from joulewise.hazards import clock

ROOT = Path(__file__).resolve().parents[2]


class ClockThresholdTests(unittest.TestCase):
    def test_block6_policy_reaches_driver_and_precheck(self):
        reg = ROOT / "configs/b6/registration"
        thresholds = plan_inputs.thresholds(ROOT, reg)
        checked, audit = plan.audit_thresholds(
            thresholds, plan.hazard_threshold_defaults(),
            sized={("clock", "t_stream_max_s"): 335, ("disk", "planned_bytes"): 1})
        self.assertEqual(checked["clock"]["h_ms"], 0)
        self.assertEqual(precheck.thresholds_for(ROOT, "ALPHA", reg)["clock"]["h_ms"], 0)
        self.assertIn({"key": "clock.h_ms", "value": 0, "default": 3.7},
                      audit["differences_from_defaults"])
        self.assertTrue(clock.frequency_bound(4 * clock.FREQUENCY_SCALE, checked["clock"])["passes"])
        self.assertEqual(clock.DEFAULT_THRESHOLDS["h_ms"], 3.7)

    def test_block5_sizing_copy_remains_identical(self):
        self.assertEqual((ROOT / "configs/b6/registration/sizing_b5.json").read_bytes(),
                         (ROOT / plan_inputs.SIZING).read_bytes())

    def test_registered_overrides_still_reach_both_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            reg = Path(directory)
            (reg / "precheck_thresholds.json").write_text(json.dumps({"clock": {"frequency_margin_ppm": 0.5}}))
            self.assertEqual(plan_inputs.thresholds(ROOT, reg)["clock"]["frequency_margin_ppm"], 0.5)
            self.assertEqual(precheck.thresholds_for(ROOT, "ALPHA", reg)["clock"]["frequency_margin_ppm"], 0.5)


class DiskBudgetTests(unittest.TestCase):
    def test_replication_budgets_keep_existing_path(self):
        identities = {name: {"path": "/synthetic/" + name, "sha256": "a" * 64}
                      for name in ("identity-epoch.json", "t1-bindings.json")}
        reg = ROOT / "configs/b6/registration"
        for pack in plan_inputs.PACK_LABELS:
            inputs = plan_inputs.build(ROOT, reg, pack, "synthetic", identities,
                custody_root="/synthetic/custody", runs_parent="/synthetic/runs",
                claim_backup="/synthetic/claim", bound_backup="/synthetic/bound", head="a" * 40)
            self.assertEqual(inputs["bytes_per_member"], 182 * 1024 * 1024)
            self.assertEqual(inputs["thresholds"]["disk"], plan_inputs.thresholds(ROOT, reg)["disk"])
            self.assertNotIn("disk_budget", inputs)

    def test_missing_and_inconsistent_p_are_flags(self):
        for terms in (None, {}, {"B_bytes": 10}):
            inputs = {"pack_root": str(ROOT / "configs/campaigns/bytes-s1-p1"),
                      "bytes_per_member": plan_inputs.BYTES_PER_MEMBER,
                      "thresholds": {"disk": {"headroom_bytes": 20 * 1024 ** 3}}}
            plan_inputs.encode_disk_budget(inputs, terms)
            self.assertEqual(inputs["disk_budget"]["flags"], ["disk.budget_missing"])
            self.assertIsNone(inputs["disk_budget"]["required_free_bytes"])

    def test_spares_count_matches_native_writer_and_rounding_is_exact(self):
        terms = dict(B_bytes=101, extra_wait_raw_bytes=7200, fixed_retained_bytes=3,
                     required_free_bytes=14605, peak_copies=2, session_wait_budget_s=7200)
        stages = [SimpleNamespace(in_chain=True, kind="campaign_collection", expected_count=7,
                                  spare_sets=(2, 3))]
        for spares, n in ((True, 10), (False, 7)):
            inputs = {"pack_root": "/synthetic", "spare_retries": spares, "thresholds": {"disk": {}}}
            with patch.object(plan, "read_plan_tree", return_value=({}, "hash")), \
                    patch.object(plan.b5_chain, "stage_plan", return_value=stages):
                plan_inputs.encode_disk_budget(inputs, terms)
            self.assertEqual(inputs["disk_budget"]["member_count"], n)
            self.assertEqual(3 * n * inputs["bytes_per_member"] +
                             inputs["thresholds"]["disk"]["headroom_bytes"], 14605)
