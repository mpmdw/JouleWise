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
from joulewise.hazards import base, disk

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
        # The block-6 copy may add BYTES pack rows; every block-5 field and row
        # (ALPHA, BETA, GAMMA) must stay exactly as sealed.
        sealed = json.loads((ROOT / plan_inputs.SIZING).read_text())
        current = json.loads((ROOT / "configs/b6/registration/sizing_b5.json").read_text())
        self.assertEqual({k: v for k, v in current.items() if k != "packs"},
                         {k: v for k, v in sealed.items() if k != "packs"})
        for key, row in sealed["packs"].items():
            self.assertEqual(current["packs"].get(key), row, key)
        added = set(current["packs"]) - set(sealed["packs"])
        self.assertTrue(all(current["packs"][key]["pack_id"].startswith("bytes-s") for key in added),
                        sorted(added))

    def test_registered_overrides_still_reach_both_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            reg = Path(directory)
            (reg / "precheck_thresholds.json").write_text(json.dumps({"clock": {"frequency_margin_ppm": 0.5}}))
            self.assertEqual(plan_inputs.thresholds(ROOT, reg)["clock"]["frequency_margin_ppm"], 0.5)
            self.assertEqual(precheck.thresholds_for(ROOT, "ALPHA", reg)["clock"]["frequency_margin_ppm"], 0.5)


class DiskBudgetTests(unittest.TestCase):
    def test_registered_bytes_rows_have_valid_disk_terms(self):
        sized = json.loads((ROOT / "configs/b6/registration/sizing_b5.json").read_text())
        rows = [row for row in sized["packs"].values() if row["pack_id"].startswith("bytes-s")]
        print(f"registered BYTES sizing rows checked: {len(rows)}")
        for row in rows:
            with self.subTest(pack=row["pack_id"]):
                self.assertTrue(plan_inputs.valid_disk_terms(row.get("disk_derivation")))

    def test_precheck_all_twelve_p_and_retained_smoke_boundaries(self):
        # Synthetic integer bytes: exact P reconstruction is the property.
        with tempfile.TemporaryDirectory() as directory:
            reg = Path(directory)
            sized = json.loads((ROOT / "configs/b6/registration/sizing_b5.json").read_text())
            for path in sorted((ROOT / "configs/b6/packs").glob("bytes-s*/registration.json")):
                pack = path.parent.name
                b, wait, fixed = 1000001, 7200, 19
                required = 2 * (b + wait) + fixed
                terms = dict(B_bytes=b, extra_wait_raw_bytes=wait, fixed_retained_bytes=fixed,
                    required_free_bytes=required, peak_copies=2, session_wait_budget_s=plan.SESSION_WAIT_BUDGET_S)
                sized["packs"][pack] = dict(pack_id=pack, programmed_span_s=3600,
                    T_stream_max_s=100, disk_derivation=terms)
            (reg / "sizing_b5.json").write_text(json.dumps(sized))
            for pack in sorted(k for k in sized["packs"] if k.startswith("bytes-s")):
                limits = precheck.thresholds_for(ROOT, pack, reg)["disk"]
                self.assertEqual(limits["largest_session_bytes"], required)
                self.assertEqual(limits["headroom_bytes"], 0)
                encoded = {"pack_root": str(ROOT / "configs/campaigns" / pack),
                           "spare_retries": False, "thresholds": {"disk": {}}}
                plan_inputs.encode_disk_budget(encoded, plan_inputs.registered_disk_terms(reg, pack))
                self.assertEqual(encoded["disk_budget"]["required_free_bytes"], required)
                derivation = limits["smoke_derivation"]
                self.assertEqual(limits["smoke_bytes"], (2 * b * derivation["smoke_members"] +
                    derivation["pack_members"] - 1) // derivation["pack_members"])
                for smoke in (False, True):
                    bar = required + (limits["smoke_bytes"] if smoke else 0)
                    for free, expected in ((bar - 1, base.REFUSE), (bar, base.PASS)):
                        with self.subTest(pack=pack, smoke=smoke, free=free):
                            measured = disk.measure(base.Context(), targets=[{"path": "/synthetic", "copies": 1}],
                                statvfs=lambda path: SimpleNamespace(f_bavail=free, f_frsize=1, f_blocks=bar * 2),
                                stat=lambda path: SimpleNamespace(st_dev=1))
                            verdict = disk.judge(measured, {"planned_bytes": bar, "headroom_bytes": 0})
                            self.assertEqual(verdict.observed["volumes"][0]["required_bytes"], bar)
                            self.assertEqual(verdict.status, expected)

    def test_precheck_missing_p_never_inherits_replication_reserve(self):
        with tempfile.TemporaryDirectory() as directory:
            for pack in ("bytes-s1-p1", "bytes-s6-p2"):
                limits = precheck.thresholds_for(ROOT, pack, directory)["disk"]
                self.assertEqual(limits["flags"], ["disk.budget_missing"])
                self.assertEqual(limits["largest_session_bytes"] + limits["headroom_bytes"] + limits["smoke_bytes"], 0)
            for pack in plan_inputs.PACK_LABELS:
                self.assertEqual(precheck.thresholds_for(ROOT, pack, directory)["disk"],
                                 precheck.PRECHECK_DEFAULTS["disk"])

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
        # Exact integer identity: P = 2*(101+7200)+3 = 14605 bytes.
        exact = dict(B_bytes=101, extra_wait_raw_bytes=7200, fixed_retained_bytes=3,
                     required_free_bytes=14605, peak_copies=2, session_wait_budget_s=7200)
        self.assertTrue(plan_inputs.valid_disk_terms(exact))
        inconsistent = [dict(exact, required_free_bytes=14605 + delta) for delta in (1, -1)]
        for terms in inconsistent:
            self.assertFalse(plan_inputs.valid_disk_terms(terms))
        for terms in (None, {}, {"B_bytes": 10}, *inconsistent):
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
