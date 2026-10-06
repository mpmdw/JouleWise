"""The desk/CI pre-check of a rendered block-5 chain (gate-prune core prune A21, lane NONCORE N6).

Every committed v5 pack must check clean, so a refusal that would fire on
committed bytes or argv in the window is caught at the desk instead.  Each
synthetic defect below is one the chain's tools would refuse in the window
(a duplicate run id: run_campaign exits 2 before member 1).
"""

from __future__ import annotations

import contextlib
import copy
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts/check_b5_chain.py"
_spec = importlib.util.spec_from_file_location("check_b5_chain", SCRIPT)
check_b5_chain = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_b5_chain)

PACKS = sorted(path.parent for path in (REPO / "configs/campaigns").glob("*_v5/plan_tree.json"))
ALPHA = REPO / "configs/campaigns/d117_floor_qwen3-1p7b_v5"
REFERENCE_DIR = REPO / "configs/campaigns/window_references_v5/start_triplet"


def run_main(*argv: str) -> tuple[int, dict]:
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        code = check_b5_chain.main(list(argv))
    return code, json.loads(stdout.getvalue())


class CommittedPackTests(unittest.TestCase):
    def test_every_committed_v5_pack_checks_clean(self):
        self.assertGreaterEqual(len(PACKS), 3)
        for pack in PACKS:
            with self.subTest(pack=pack.name):
                code, report = run_main("--pack-root", str(pack), "--no-live-identity")
                self.assertEqual((code, report["findings"]), (0, []))
                self.assertEqual(report["mode"], "pack")
                self.assertIn("doctor_config_gate", report["checks"])
                self.assertIn("acceptance_code_identity", report["checks"])

    def test_the_check_never_imports_mlx(self):
        probe = ("import contextlib, io, runpy, sys\n"
                 f"sys.argv = ['check_b5_chain.py', '--pack-root', {str(ALPHA)!r}, '--no-live-identity']\n"
                 "with contextlib.redirect_stdout(io.StringIO()):\n"
                 "    try:\n"
                 f"        runpy.run_path({str(SCRIPT)!r}, run_name='__main__')\n"
                 "    except SystemExit as exc:\n"
                 "        code = exc.code\n"
                 "print(code, sorted(name for name in sys.modules if name.split('.')[0] == 'mlx'))\n")
        result = subprocess.run([sys.executable, "-B", "-c", probe], capture_output=True, text=True, check=False,
                                cwd=str(REPO), timeout=300)
        self.assertEqual(result.stdout.strip(), "0 []", result.stderr[-2000:])


class SyntheticDefectTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        # A measurement root that is this checkout except for one new pack and one new config directory.
        self.root = Path(self._tmp.name).resolve() / "measurement"
        campaigns = self.root / "configs/campaigns"
        campaigns.mkdir(parents=True)
        for entry in (REPO / "configs").iterdir():
            if entry.name != "campaigns":
                (self.root / "configs" / entry.name).symlink_to(entry)
        for entry in (REPO / "configs/campaigns").iterdir():
            (campaigns / entry.name).symlink_to(entry)
        self.tree = json.loads((ALPHA / "plan_tree.json").read_bytes())

    def collection(self, tree: dict) -> dict:
        return next(stage for stage in tree["stage_graph"] if stage["kind"] == "campaign_collection")

    def write_pack(self, tree: dict, name: str = "b5_static_check_v5") -> Path:
        pack = self.root / "configs/campaigns" / name
        pack.mkdir()
        (pack / "plan_tree.json").write_text(json.dumps(tree))
        return pack

    def test_a_duplicate_run_id_in_a_collection_stage_is_a_finding(self):
        configs = self.root / "configs/campaigns/b5_static_check_dup"
        configs.mkdir()
        for path in REFERENCE_DIR.glob("neg8-window-start-r*.json"):
            shutil.copyfile(path, configs / path.name)
        second = json.loads((configs / "neg8-window-start-r2.json").read_bytes())
        second["run_id"] = "neg8-window-start-r1"
        (configs / "neg8-window-start-r2.json").write_text(json.dumps(second, indent=2))
        tree = copy.deepcopy(self.tree)
        stage = self.collection(tree)
        stage["launch"]["commands"][0]["argv_template"]["arguments"][0]["value"] = \
            "configs/campaigns/b5_static_check_dup"
        code, report = run_main("--pack-root", str(self.write_pack(tree)), "--no-live-identity")
        self.assertEqual(code, 1)
        errors = [item for item in report["findings"] if item["severity"] == "error"]
        self.assertEqual([(item["check"], item["stage_id"]) for item in errors],
                         [("duplicate_run_id", stage["stage_id"])])
        self.assertIn("neg8-window-start-r1", errors[0]["detail"])
        # This measurement root is not the checkout the code identity was read from: said, not failed.
        self.assertEqual([item["check"] for item in report["findings"] if item["severity"] == "warning"],
                         ["checkout"])

    def test_an_argv_the_writer_would_refuse_and_a_pack_outside_configs_campaigns(self):
        tree = copy.deepcopy(self.tree)
        capture = next(stage for stage in tree["stage_graph"] if stage["kind"] == "calibration_capture")
        capture["launch"]["commands"][0]["argv_template"]["arguments"].append(
            {"kind": "literal", "value": "--no-such-writer-flag"})
        pack = self.write_pack(tree)
        report = check_b5_chain.check(tree, pack_root=pack, measurement_root=self.root,
                                      bindings=check_b5_chain.synthetic_bindings(self.root, pack), plan_mode=False,
                                      live_identity=False)
        errors = [(item["check"], item["stage_id"]) for item in report["findings"] if item["severity"] == "error"]
        self.assertEqual(errors, [("argv_parses", capture["stage_id"])])
        self.assertIn("unrecognized arguments: --no-such-writer-flag",
                      next(item["detail"] for item in report["findings"] if item["check"] == "argv_parses"))
        elsewhere = Path(self._tmp.name).resolve() / "packs" / "b5_static_check_v5"
        report = check_b5_chain.check(self.tree, pack_root=elsewhere, measurement_root=self.root,
                                      bindings=check_b5_chain.synthetic_bindings(self.root, elsewhere),
                                      plan_mode=False, live_identity=False)
        self.assertEqual([item["check"] for item in report["findings"] if item["severity"] == "error"],
                         ["pack_root_location"])

    def test_plan_mode_reads_the_real_bindings_and_the_desk_identity(self):
        pack = self.write_pack(copy.deepcopy(self.tree))
        custody = Path(self._tmp.name).resolve() / "custody"
        custody.mkdir()
        bindings = check_b5_chain.synthetic_bindings(self.root, pack)
        bindings["pre_calibration_dir"] = str(custody / "existing-pre")
        os.mkdir(bindings["pre_calibration_dir"])
        identity = custody / "identity_epoch.json"
        identity.write_text(json.dumps({"os_build": "25G83", "hardware_model": "Mac15,9",
                                        "power_policy": "battery_saver"}))
        bindings["identity_epoch_json"] = str(identity)
        plan = custody / "night_plan.json"
        plan.write_text(json.dumps({"measurement_root": str(self.root), "hazard_window": {
            "pack": {"pack_root": str(pack)}, "bindings": bindings}}))
        live = {"kern.osversion": "25G83", "hw.model": "Mac16,1"}
        original = check_b5_chain._sysctl
        check_b5_chain._sysctl = live.get
        try:
            code, report = run_main("--plan", str(plan))
        finally:
            check_b5_chain._sysctl = original
        self.assertEqual(code, 1)
        self.assertEqual(report["mode"], "plan")
        found = {(item["check"], item["severity"]) for item in report["findings"]}
        self.assertEqual(found, {("capture_dir_absent", "error"), ("desk_identity_power_policy", "error"),
                                 ("desk_identity_machine", "warning"), ("checkout", "warning")})
        machine = [item["detail"] for item in report["findings"] if item["check"] == "desk_identity_machine"]
        self.assertEqual(len(machine), 1)
        self.assertIn("hardware_model", machine[0])
        self.assertFalse(os.listdir(custody / "existing-pre"))  # nothing was written

    def test_an_unreadable_input_exits_2(self):
        code, report = run_main("--plan", str(Path(self._tmp.name) / "absent.json"))
        self.assertEqual(code, 2)
        self.assertIn("input_error", report)


if __name__ == "__main__":
    unittest.main()
