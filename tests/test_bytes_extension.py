"""BYTES extension packs (docs/registrations/bytes_extension_models_2026-10-27.md).

The extension adds held-out models in their own sub-packs. These tests hold the
three promises of BY-EXT-1: the generator's --check passes, the extension never
enters a registered-roster or family computation, and the registered packs are
byte-identical.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path
from types import SimpleNamespace
import unittest

from joulewise import bytes_analysis
from joulewise.b6 import blinding, compose, pack_registration, queue
from joulewise.flags.catalog import load_catalog

ROOT = Path(__file__).resolve().parents[1]
EXT = ROOT / "configs/campaigns/bytes_v1/extension"
PACK = "bytes-s7-p1"
MODEL = "Qwen3.8-27B-8bit"
# The registered tree this lane was cut from (work/2026-10-23-by-slots-draft).
BASE = "991358f73"


def _module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ext = _module("bytes_extension_generator", EXT / "generate_extension.py")
registered_configs = _module("bytes_registered_configs", ROOT / "configs/campaigns/bytes_v1/generate_configs.py")


def read(path):
    return json.loads(Path(path).read_bytes())


def filled(slots):
    """Synthetic stand-ins for every MAC-PENDING slot; never committed."""
    def fill(value):
        if isinstance(value, dict):
            return {k: ("filled" if k == "status" and v == ext.MAC_PENDING else fill(v)) for k, v in value.items()}
        return "synthetic" if value == ext.MAC_PENDING else value
    out = fill(slots)
    out["packs"][PACK]["est_minutes"]["value"] = 230.0
    return out


class ExtensionGeneratorTests(unittest.TestCase):
    def test_generator_check_passes(self):
        files = ext.generate(check=True)
        self.assertEqual(len([p for p in files if p.name.startswith("bytes-qwen38-27b-8bit-")]), 50)
        self.assertIn(Path("configs/b6/packs") / PACK / "registration.json", files)

    def test_registered_generators_still_check(self):
        registered_configs.generate(check=True)
        bpt = _module("bytes_plan_trees_check", ROOT / "scripts/bytes_plan_trees.py")
        bpt.generate(check=True)

    def test_workload_is_the_registered_one(self):
        template = read(ROOT / registered_configs.TEMPLATE)
        # The extension's config body reproduces a registered config exactly.
        spec = registered_configs.ROSTER[7]  # qwen3-8b-8bit: 8 bit, group size 64
        run = registered_configs.assembly(spec[0])[0][0]
        model = registered_configs.model_config(spec)
        raw = registered_configs.raw_json(ext.run_config(template, run, model, 8, 64, spec[0], extension=False))
        self.assertEqual(raw, (ROOT / registered_configs.config_dirs(spec[0])[0] / (run["run_id"] + ".json")).read_bytes())
        roster = read(EXT / "roster.json")
        self.assertEqual(roster["workload"], read(ROOT / "configs/campaigns/bytes_v1/roster.json")["workload"])
        for directory in ext.config_dirs("qwen38-27b-8bit"):
            for row in read(ROOT / directory / "order_manifest.json")["executed_order"]:
                cfg = read(ROOT / directory / row["config"])
                self.assertEqual(cfg["workload_profile"], {"name": "bytes_synthetic_2048_decode_512", "prompt_tokens": 2048,
                                                           "output_tokens": 512, "repetitions": 1, "warmup_runs": 1})
                self.assertEqual(cfg["quantization"]["bits"], 8)
                self.assertEqual(cfg["model"]["name"], MODEL)
                self.assertIn("bytes-extension", cfg["run_metadata"]["tags"])

    def test_registration_is_one_pass_extension_draft_with_registered_end(self):
        reg = read(ROOT / "configs/b6/packs" / PACK / "registration.json")
        self.assertEqual(reg["status"], "draft")
        self.assertEqual(reg["bytes_pass"], 1)
        self.assertEqual((reg["target_sessions"], reg["minimum_sessions"]), (1, 1))
        self.assertEqual(reg["stopping"], {"count": 1, "end_t0_before": "2026-11-05T00:00:00-08:00", "precision": None})
        self.assertEqual(reg["blinding_group"], "bytes")
        self.assertFalse(reg["bytes_extension"]["registered_roster_member"])
        self.assertEqual(reg["bytes_extension"]["passes"], [1])
        [module] = reg["modules"]
        self.assertEqual((module["kind"], module["phase"], module["run_count"]), ("floor", "decode", 50))
        # Every Mac value is an explicit slot, never a guess.
        self.assertIsNone(module["est_minutes"])
        self.assertEqual(module["est_minutes_source"]["status"], ext.MAC_PENDING)
        pending = set(reg["bytes_extension"]["pending_slots"])
        for slot in ("/models/qwen38-27b-8bit/manifest",
                     "/models/qwen38-27b-8bit/resolvability",
                     "/packs/bytes-s7-p1/sizing_row", "/packs/bytes-s7-p1/disk"):
            self.assertIn(slot, pending)
        self.assertEqual(sorted(pending), ext.pending_slots(ext.read_slots(), "qwen38-27b-8bit"))
        cfg = read(ROOT / ext.config_dirs("qwen38-27b-8bit")[0] / "bytes-qwen38-27b-8bit-abs-r01.json")
        self.assertEqual(cfg["model"]["revision"], "815b83c0df8ffd1d1b5244cf75fd6ef14fca9ef9")
        model_slots = ext.read_slots()["models"]["qwen38-27b-8bit"]
        for name in ("revision", "download", "hf_repo", "config_model_type", "group_size"):
            self.assertEqual(model_slots[name] if name == "revision" else model_slots[name]["status"],
                             cfg["model"]["revision"] if name == "revision" else "filled")
            self.assertNotIn("/models/qwen38-27b-8bit/" + name, pending)
        # The only validator objection is the pending module estimate.
        errors = pack_registration.validate(pack_registration.Registration(reg), load_catalog(ROOT / reg["flag_catalog"]), root=ROOT)
        self.assertEqual(errors, ["modules[0].est_minutes"])

    def test_nemotron_is_recorded_as_dropped_without_a_pack(self):
        roster = read(EXT / "roster.json")
        self.assertEqual([m["model"]["name"] for m in roster["models"]], [MODEL])
        [dropped] = roster["dropped"]
        self.assertEqual(dropped["status"], "dropped_not_feasible")
        self.assertFalse((ROOT / "configs/b6/packs/bytes-s8-p1").exists())
        self.assertFalse((EXT / dropped["model_id"]).exists())

    def test_tree_refuses_while_slots_are_pending(self):
        with self.assertRaisesRegex(ValueError, "MAC-PENDING slots open"):
            ext.tree(ext.PREPARED[0])

    def test_tree_once_filled_matches_single_model_registered_shape(self):
        files, keep = ext.tree(ext.PREPARED[0], ROOT, slots=filled(ext.read_slots()))
        tree = json.loads(files[Path("configs/campaigns") / PACK / "plan_tree.json"])
        self.assertEqual(tree["draft_status"], "draft")
        self.assertEqual(tree["bytes_pass"], 1)
        registered = read(ROOT / "configs/campaigns/bytes-s5-p1/plan_tree.json")
        self.assertEqual([s["kind"] for s in tree["stage_graph"]], [s["kind"] for s in registered["stage_graph"]])
        self.assertEqual(len(tree["science"]), 50)
        self.assertEqual(keep, {f"{PACK}-reference-start": 1, "bytes-qwen38-27b-8bit-absolute": 1,
                                f"{PACK}-reference-end": 1})
        units = [u["identity_unit_id"] for u in tree["arm_attachments"]["identity_pin_projection"]["identity_units"]]
        self.assertEqual(units, ["neg8_reference", "qwen38-27b-8bit"])
        # The patched registered-tree context is restored afterwards.
        bpt = _module("bytes_plan_trees_restore", ROOT / "scripts/bytes_plan_trees.py")
        self.assertEqual(bpt.REGISTERED_PASSES, frozenset({1}))


class ExclusionTests(unittest.TestCase):
    def test_registered_roster_order_sizing_and_smoke_do_not_name_the_extension(self):
        roster = read(ROOT / "configs/campaigns/bytes_v1/roster.json")
        self.assertNotIn(MODEL, {m["model"]["name"] for m in roster["models"]})
        self.assertNotIn(MODEL, bytes_analysis.REGISTERED_MODELS)
        order = read(ROOT / "configs/campaigns/bytes_v1/pass_order.json")
        self.assertNotIn(PACK, sum(order["passes"].values(), []))
        self.assertNotIn(PACK, read(ROOT / "configs/b6/loop.json")["base_order"])
        self.assertNotIn(PACK, read(ROOT / "configs/b6/smoke_keep.json"))
        self.assertNotIn(PACK, read(ROOT / "configs/b6/registration/sizing_b5.json")["packs"])
        bpt = _module("bytes_plan_trees_groups", ROOT / "scripts/bytes_plan_trees.py")
        self.assertNotIn("qwen38-27b-8bit", sum(bpt.GROUPS, ()))
        self.assertFalse(any(PACK in str(path) or "extension" in str(path) for path in bpt.build_files(ROOT)))
        self.assertFalse(any("extension" in str(path) for path in registered_configs.build_files()))

    def test_registered_analysis_family_and_manifest_refuse_the_extension(self):
        manifest = read(ROOT / "configs/bytes/bytes_manifest.json")
        self.assertEqual(bytes_analysis.h1_checks({"models": [{"role": "heldout"}] * 7 + [{"role": "fit"}] * 3}), 21)
        self.assertNotIn(MODEL, {m["model"] for m in manifest["models"]})
        extra = {"model": MODEL, "W_bytes": 1, "KV_bytes": 1, "R_bytes": 1}
        with self.assertRaisesRegex(bytes_analysis.AnalysisError, "differ from registered manifest"):
            bytes_analysis._validate_predictors([extra])

    def test_extension_rows_are_withheld_never_fit(self):
        cfg = read(ROOT / ext.config_dirs("qwen38-27b-8bit")[0] / "bytes-qwen38-27b-8bit-abs-r01.json")
        self.assertEqual(blinding.configuration_stage(cfg), "heldout")
        self.assertNotIn(MODEL, blinding.FIT_MODELS)

    def test_draft_extension_pack_is_never_opened_by_the_loop(self):
        clean = SimpleNamespace(returncode=0, stdout="")
        stamp = SimpleNamespace(returncode=0, stdout="1\n")
        rejected = {}
        opened = pack_registration.open_packs(ROOT, run=lambda argv: stamp if "log" in argv else clean,
                                              rejected=lambda path, problems: rejected.setdefault(path, problems))
        self.assertNotIn(PACK, {r.pack_id for r in opened})
        self.assertIn("draft", rejected[f"configs/b6/packs/{PACK}/registration.json"])

    def test_registered_packs_are_byte_identical_to_the_base(self):
        have = subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e", BASE + "^{commit}"], capture_output=True)
        if have.returncode:
            self.skipTest("base commit not in this clone; the generator checks above still hold")
        paths = [f"configs/b6/packs/bytes-s{n}-p{p}" for n in range(1, 7) for p in (1, 2)]
        paths += [f"configs/campaigns/bytes-s{n}-p{p}" for n in range(1, 7) for p in (1, 2)]
        paths += ["configs/campaigns/bytes_v1/roster.json", "configs/campaigns/bytes_v1/pass_order.json",
                  "configs/campaigns/bytes_v1/generate_configs.py", "scripts/bytes_plan_trees.py",
                  "joulewise/bytes_analysis.py", "configs/bytes",
                  "configs/b6/loop.json", "configs/b6/smoke_keep.json", "configs/b6/registration"]
        paths += [f"configs/campaigns/bytes_v1/{spec[0]}" for spec in registered_configs.ROSTER]
        diff = subprocess.run(["git", "-C", str(ROOT), "diff", "--name-only", BASE, "--", *paths],
                              capture_output=True, text=True, check=True)
        self.assertEqual(diff.stdout, "")


if __name__ == "__main__":
    unittest.main()
