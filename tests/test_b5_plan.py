"""The block-5 HAZARD_PACK window plan writer (desk only; never arms)."""

from __future__ import annotations

import io
import json
import math
import os
import subprocess
import sys
import tempfile
import time
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from joulewise import arm_readiness_evidence_t0 as t0_author
from joulewise import night_gate
from joulewise.b5 import chain as b5_chain
from joulewise.b5 import plan as b5_plan
from tests.fixtures.b5_plan import fake_window

REPO_ROOT = Path(__file__).resolve().parents[1]


class WindowPlanFixture(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="b5-plan-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.measurement = fake_window.build_checkout(self.root, git=False)
        self.t0 = (int(time.time()) // 60 + 60) * 60

    def inputs(self, pack="alpha", **changes):
        value = fake_window.inputs(self.root, self.measurement, pack, plan_id=f"b5-{pack}-1", t0_epoch_s=self.t0)
        value.update(changes)
        return value

    def write(self, inputs=None, **keywords):
        keywords.setdefault("pack_digest", lambda _root: "e" * 64)
        return b5_plan.write_window_plan(inputs if inputs is not None else self.inputs(), **keywords)


class WindowPlanTests(WindowPlanFixture):
    def test_each_pack_yields_a_parseable_hazard_plan_with_all_fourteen_bindings(self):
        for pack, members in (("alpha", 119), ("beta", 119), ("gamma", 101)):
            with self.subTest(pack=pack):
                root = self.root / pack
                root.mkdir()
                inputs = fake_window.inputs(root, self.measurement, pack, plan_id=f"b5-{pack}-1", t0_epoch_s=self.t0)
                record = self.write(inputs)
                plan = night_gate.NightPlan.from_mapping(json.loads(Path(record["plan"]["path"]).read_text()))
                self.assertIsInstance(plan, night_gate.HazardNightPlan)
                self.assertEqual(night_gate.HAZARD_PACK, plan.receipt_class)
                window = plan.hazard_window
                self.assertEqual(set(night_gate.HAZARD_LAUNCH_BINDINGS), set(window["bindings"]))
                self.assertEqual(members, window["member_count"])
                self.assertEqual(members * inputs["bytes_per_member"], window["planned_bytes"])
                self.assertEqual(inputs["bracket_session_id"], window["bracket_session_id"])
                self.assertEqual(str(self.measurement / b5_plan.DEFAULT_LEDGER_RELATIVE), window["bindings"]["ledger_path"])
                self.assertEqual(fake_window.THRESHOLDS, window["thresholds"])
                self.assertEqual(list(b5_chain.DEVIATIONS), window["chain_deviations"])
                self.assertEqual(Path(window["bindings"]["claim_runs_root"]) / "instrument_validation" /
                                 inputs["pre_attempt_id"], Path(window["bindings"]["pre_calibration_dir"]))
                # The window maximum carries the 3300 s T-0 stage cap (dwell cap 2700 s inside it).
                self.assertEqual(60 * math.ceil((inputs["programmed_span_s"] + 3300) / 60), plan.window_max_s)
                self.assertGreaterEqual(plan.window_max_s - inputs["programmed_span_s"], b5_plan.DWELL_CAP_S)
                # Fresh runs roots exist and are empty; the chain and its sidecar agree.
                for name in ("claim", "bound"):
                    self.assertEqual([], list(Path(window["runs_roots"][name]).iterdir()))
                chain = Path(plan.chain_path).read_bytes()
                self.assertEqual(b5_chain.sidecar_bytes(chain, "chain.zsh"), Path(plan.chain_sha256_path).read_bytes())
                self.assertIn(b"export SETTLE_S=600\n", chain)
                self.assertEqual(600, window["settle_s"])

    def test_window_env_is_the_exact_25_key_allowlist(self):
        record = self.write()
        values = t0_author.parse_window_environment(Path(record["window_env"]["path"]).read_bytes())
        self.assertEqual(set(b5_plan.WINDOW_ENV_KEYS), set(values))
        self.assertEqual(set(t0_author.WINDOW_ENV_KEYS), set(b5_plan.WINDOW_ENV_KEYS))
        self.assertEqual(values["CALIBRATION_LEDGER"], str(self.measurement / b5_plan.DEFAULT_LEDGER_RELATIVE))
        self.assertEqual("b5-alpha-1-calibration", values["BRACKET_SESSION_ID"])

    def test_the_command_line_renders_the_registered_600_s_settle(self):
        path = self.root / "inputs.json"
        path.write_text(json.dumps(self.inputs()))
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(0, __import__("scripts.write_b5_window_plan", fromlist=["main"]).main(["--inputs", str(path)]))
        record = json.loads(output.getvalue())
        self.assertIn(b"export SETTLE_S=600\n", Path(record["chain"]["path"]).read_bytes())
        plan = json.loads(Path(record["plan"]["path"]).read_text())
        self.assertEqual(600, plan["hazard_window"]["settle_s"])

    def test_a_ledger_other_than_the_checkout_default_is_refused_at_the_desk(self):
        other = self.root / "other-ledger.jsonl"
        other.write_text("")
        with self.assertRaisesRegex(b5_plan.WindowPlanError, "default ledger"):
            self.write(self.inputs(ledger_path=str(other)))
        self.assertFalse((self.root / "custody").exists())
        self.assertEqual([], list((self.root / "runs").iterdir()))
        # The default itself is accepted when named explicitly.
        self.write(self.inputs(ledger_path=str(self.measurement / b5_plan.DEFAULT_LEDGER_RELATIVE)))

    def test_an_existing_runs_root_is_never_reused(self):
        leaf = json.loads((REPO_ROOT / "configs/campaigns/d117_floor_qwen3-1p7b_v5/plan_tree.json").read_text())["roots"]
        (self.root / "runs").mkdir(exist_ok=True)
        (self.root / "runs" / leaf["bound_root_leaf"]).mkdir()
        with self.assertRaisesRegex(b5_plan.WindowPlanError, "already exists"):
            self.write()
        self.assertFalse((self.root / "custody").exists())
        self.assertFalse((self.root / "runs" / leaf["claim_root_leaf"]).exists())

    def test_input_refusals_write_nothing(self):
        cases = {
            "custody not empty": None,
            "thresholds missing a module": {"thresholds": {k: v for k, v in fake_window.THRESHOLDS.items() if k != "disk"}},
            "t0 not a whole minute": {"t0_epoch_s": self.t0 + 1},
            "identity digest wrong": {"identity_epoch_json": {"path": str(self.root / "identity-epoch.json"), "sha256": "0" * 64}},
            "pack outside the checkout": {"pack_root": str(REPO_ROOT / "configs/campaigns/d117_floor_qwen3-1p7b_v5")},
            "backup inside custody": {"claim_backup_destination": str(self.root / "custody/backup")},
            "unknown key": {"extra": 1},
            "same pre and post attempt": {"post_attempt_id": "b5-alpha-1-cal-pre"},
        }
        for label, change in cases.items():
            with self.subTest(case=label):
                custody = self.root / "custody"
                if label == "custody not empty":
                    custody.mkdir()
                    (custody / "stale").write_text("x")
                with self.assertRaises(b5_plan.WindowPlanError):
                    self.write(self.inputs(**(change or {})))
                self.assertEqual([], list((self.root / "runs").iterdir()))
                if label == "custody not empty":
                    (custody / "stale").unlink()
                    custody.rmdir()
                self.assertFalse(custody.exists())

    def test_pack_digest_failure_is_recorded_not_refused(self):
        def broken(_root):
            raise RuntimeError("pack is not committed")
        record = self.write(pack_digest=broken)
        self.assertIsNone(record["pack_sha256"])
        self.assertIn("pack is not committed", record["pack_digest_error"])
        plan = json.loads(Path(record["plan"]["path"]).read_text())
        self.assertIsNone(plan["hazard_window"]["pack"]["pack_sha256"])

    def test_both_launch_binding_shapes_are_read(self):
        floor = json.loads((REPO_ROOT / "configs/campaigns/d117_floor_qwen3-1p7b_v5/plan_tree.json").read_text())
        contrast = json.loads((REPO_ROOT / "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/"
                                           "plan_tree.json").read_text())
        self.assertIn("bindings", floor["arm_attachments"]["launch"])
        self.assertIn("closed_bindings", contrast["arm_attachments"]["launch"])
        for tree in (floor, contrast):
            self.assertEqual(set(night_gate.HAZARD_LAUNCH_BINDINGS), set(b5_plan.declared_bindings(tree)))
        broken = json.loads(json.dumps(floor))
        broken["arm_attachments"]["launch"]["bindings"].pop()
        with self.assertRaises(b5_plan.WindowPlanError):
            b5_plan.declared_bindings(broken)

    def test_writer_stays_off_the_retired_arm_path_at_import(self):
        code = ("import sys; import joulewise.b5.plan, joulewise.b5.chain, joulewise.b5.driver; "
                "bad = sorted(m for m in sys.modules if m.split('.')[-1] in {'arm_readiness', "
                "'arm_readiness_evidence', 'arm_readiness_evidence_t0', 'capture_t0_step', 'launch_window', "
                "'t0_rehearsal', 'v5_qualification'}); print(bad); sys.exit(1 if bad else 0)")
        completed = subprocess.run([sys.executable, "-B", "-c", code], cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)


class HazardWindowValidationTests(unittest.TestCase):
    def setUp(self):
        self.root = Path("/fixture/b5")

    def window(self):
        return fake_window.hazard_window_mapping(self.root, pack_root=REPO_ROOT / "configs/campaigns/d117_floor_qwen3-1p7b_v5")

    def test_valid_window_round_trips(self):
        self.assertEqual(self.window(), night_gate.validate_hazard_window(self.window()))

    def test_structural_defects_are_refused(self):
        cases = {
            "extra key": lambda w: w.update(extra=1),
            "missing thresholds module": lambda w: w["thresholds"].pop("clock"),
            "bindings not fourteen": lambda w: w["bindings"].pop("ledger_path"),
            "bracket session drift": lambda w: w.update(bracket_session_id="other"),
            "runs root drift": lambda w: w["runs_roots"].update(claim="/fixture/elsewhere"),
            "relative volume": lambda w: w.update(disk_volumes=["relative/path"]),
            "g10 not boolean": lambda w: w.update(g10="yes"),
            "pack basename": lambda w: w["pack"].update(pack_id="other"),
            "stage shape": lambda w: w["stages"][0].pop("in_chain"),
            "negative span": lambda w: w.update(programmed_span_s=0),
        }
        for label, mutate in cases.items():
            with self.subTest(case=label):
                window = self.window()
                mutate(window)
                with self.assertRaises(ValueError):
                    night_gate.validate_hazard_window(window)


if __name__ == "__main__":
    unittest.main()
