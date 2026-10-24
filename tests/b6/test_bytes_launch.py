"""Real BYTES consumers, render only, with an isolated synthetic ledger.

The source trees and sizing are production inputs. Only calibration custody
and epoch/T1 vectors are portable fixtures. Nothing installs or executes a
rendered chain, and this is not live hardware validation.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from joulewise.b5 import plan
from joulewise.b6 import plan_inputs, registration
from joulewise.b6.pack_registration import load, validate
from joulewise.flags.catalog import load_catalog
from scripts import bytes_plan_trees

ROOT = Path(__file__).resolve().parents[2]


def git(*args, cwd=None):
    return subprocess.run(["git", "-c", "maintenance.auto=false", "-c", "gc.auto=0", *map(str, args)],
                          cwd=cwd, check=True, capture_output=True, text=True)


def measurement_copy(destination):
    """Commit a fixture pin only in the throwaway clone, as B6 render tests do."""
    git("clone", "--quiet", "--no-hardlinks", ROOT, destination)
    # A build seat leaves its integrated inputs uncommitted. Reproduce those
    # exact tracked bytes in the isolated clone, including the source configs
    # and consumed identity file, before invoking the native plan writer.
    patch = git("diff", "--binary", "HEAD", "--", "configs", "scripts/bytes_plan_trees.py",
                "joulewise/b5/driver.py", cwd=ROOT).stdout
    if patch:
        subprocess.run(["git", "apply", "-"], input=patch, cwd=destination,
                       check=True, capture_output=True, text=True)
    for relative, raw in bytes_plan_trees.build_files().items():
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    seed = ROOT / "tests/fixtures/d117_v2_production/issued"
    target = destination / plan.DEFAULT_LEDGER_RELATIVE
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(seed / "calibration_observation_ledger.jsonl", target)
    shutil.copyfile(seed / "calibration_ledger_head.json", destination / plan.HEAD_PIN_RELATIVE)
    git("add", "configs", "scripts/bytes_plan_trees.py", "joulewise/b5/driver.py",
        plan.HEAD_PIN_RELATIVE, cwd=destination)
    git("-c", "user.name=BYTES render fixture", "-c", "user.email=fixture@invalid",
        "-c", "commit.gpgsign=false", "commit", "--quiet", "-m", "Synthetic ledger fixture pin", cwd=destination)
    return destination


def render_inputs(measurement, scratch, pack, identities=None):
    root = scratch / pack
    root.mkdir()
    runs = root / "runs-parent"
    runs.mkdir()
    if identities is None:
        identities = {}
        for name in ("identity-epoch.json", "t1-bindings.json"):
            target = root / name
            target.write_text('{}\n')
            identities[name] = {"path": str(target), "sha256": hashlib.sha256(target.read_bytes()).hexdigest()}
    inputs = plan_inputs.build(measurement, measurement / registration.DEFAULT_DIR_RELATIVE,
        pack, "render-" + pack, identities, custody_root=root / "custody", runs_parent=runs,
        claim_backup=root / "backup-claim", bound_backup=root / "backup-bound")
    disk = inputs.pop("disk_budget")
    inputs["t0_epoch_s"] = 1800000000.0
    return inputs, disk


class BytesLaunchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="bytes-launch-")
        cls.scratch = Path(cls.temporary.name).resolve()
        cls.measurement = measurement_copy(cls.scratch / "measurement")

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_all_six_pass1_real_consumers(self):
        catalog = load_catalog(ROOT / "configs/b6/flag_catalog_b6.json")
        sized = registration.load_sizing(ROOT / registration.DEFAULT_DIR_RELATIVE)
        for number in range(1, 7):
            pack = f"bytes-s{number}-p1"
            with self.subTest(pack=pack):
                reg = load(ROOT / f"configs/b6/packs/{pack}/registration.json")
                self.assertEqual(reg.status, "draft")
                self.assertEqual({e["version"] for e in reg.estimators},
                                 {hashlib.sha256((ROOT / "joulewise/bytes_analysis.py").read_bytes()).hexdigest()})
                self.assertEqual(validate(reg, catalog, root=ROOT), [])
                inputs, disk = render_inputs(self.measurement, self.scratch, pack)
                self.assertEqual(inputs["programmed_span_s"]["seconds"], sized["packs"][pack]["programmed_span_s"])
                self.assertEqual(inputs["T_stream_max_s"]["seconds"], sized["packs"][pack]["T_stream_max_s"])
                record = plan.write_window_plan(inputs)
                written = json.loads(Path(record["plan"]["path"]).read_bytes())
                self.assertEqual(record["member_count"], 125 if number <= 4 else 75)
                self.assertEqual(record["window_max_s"], plan_inputs.window_max_s(inputs))
                self.assertEqual(3 * record["planned_bytes"] + written["hazard_window"]["thresholds"]["disk"]["headroom_bytes"],
                                 disk["required_free_bytes"])
                self.assertEqual(len(plan.declared_bindings(json.loads((Path(inputs["pack_root"]) / "plan_tree.json").read_bytes()))), 14)
                for locator in (record["plan"], record["chain"], record["window_env"]):
                    self.assertTrue(Path(locator["path"]).is_relative_to(self.scratch))
                    self.assertEqual(hashlib.sha256(Path(locator["path"]).read_bytes()).hexdigest(), locator["sha256"])
                print(f"{pack}: plan_inputs.build PASS; native writer STAGED ({record['member_count']} members, {record['window_max_s']} s); draft registration PASS")

    def test_native_writer_refuses_a_missing_binding_before_any_output(self):
        pack = "bytes-s1-p1"
        target = self.measurement / f"configs/campaigns/{pack}/plan_tree.json"
        raw = target.read_bytes()
        tree = json.loads(raw)
        tree["arm_attachments"]["launch"]["bindings"].pop()
        target.write_text(json.dumps(tree))
        try:
            root = self.scratch / "missing-binding"
            root.mkdir()
            inputs, _ = render_inputs(self.measurement, root, pack)
            with self.assertRaisesRegex(plan.WindowPlanError, "exactly the fourteen"):
                plan.write_window_plan(inputs)
            self.assertFalse(Path(inputs["custody_root"]).exists())
            self.assertEqual(list(Path(inputs["runs_parent"]).iterdir()), [])
            print("missing t1_bindings_json: native writer REFUSED before custody/runs creation")
        finally:
            target.write_bytes(raw)


if __name__ == "__main__":
    unittest.main()
