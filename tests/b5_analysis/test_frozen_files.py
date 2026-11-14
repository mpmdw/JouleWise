"""Freeze the collection, harvest, exclusions and sealed inputs throughout L9."""
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

from joulewise.b5_analysis.windows import ROOT, SealPins

SEALED_DIR = "configs/campaigns/v5_claim_25g83/"
SEAL = ROOT / "docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md"
# The accepted block-5 analysis commit (RUN_STATE items 83, 88, 93): the dry run and the release run
# there. Main may evolve a collection file after L9's acceptance; for such a file the freeze binds the
# analysis commit's bytes, not main's working tree.
B5_ANALYSIS_COMMIT = "b13a510dc15b5e280309f7dd6b280426bf44afc6"
# Cited in-place rebinds keep the freeze on the accepted analysis commit's bytes:
# joulewise/calibration_bracketing.py -- b5 under-90 round 2 (lead ruling under D-188
# and the 2026-10-30 frozen-components rule): the run-scoped candidate-physics memo
# (_verified_candidate_bound); every value it returns is the frozen refit's own.
# joulewise/flags/exclusions.py -- Block 6 option-c analysis (4e3446e6c), recorded as DLE-14 (RL-144 addendum
# section 3, M2): compute() gained the keyword-only `pack_scoped: bool = True`; with the default the result is
# Block 5's (tests/flags/test_flags_exclusions.py, Block5DefaultEquivalenceTests).
EVOLVED_ON_MAIN = frozenset({"joulewise/b5/harvest.py", "joulewise/calibration_bracketing.py",
                             "joulewise/flags/exclusions.py"})
# A cited rebind moves the pin, it does not remove it (DLE-3, docs/analysis/b5/DEVIATION-LOG.md;
# PR #693 review M2/M1). The analysis executes these files, so beside the seal pin4 check on the
# accepted commit's bytes, the working tree is pinned to the rebound bytes: a further edit fails
# here until it carries its own cited rebind.
REBOUND_WORKING_TREE = {
    # b5 under-90 round 2 (13af1baa8), the candidate-physics memo; DLE-3.
    "joulewise/calibration_bracketing.py": "40fd34bb82b8a0a57ece79ef23e507482a5ea79dd0c6cc001c5e3ea0cfe2a1f2",
    # Block 6 option-c analysis (4e3446e6c), the keyword-only pack_scoped parameter; DLE-14.
    "joulewise/flags/exclusions.py": "ebe1678c0fdd60b1ddd20d432cf07412bd321a8629589f4ce4c6b334378f0ad6",
}
PACK_PREFIXES = ("configs/campaigns/d117_floor_qwen3-1p7b_v5/", "configs/campaigns/d117_floor_qwen3-8b_v5/",
                 "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/")


def frozen_digests():
    pins = SealPins.load()
    inventory = json.loads((ROOT / (SEALED_DIR + "sealed_inventory.json")).read_bytes())["files"]
    singles = {"scripts/run_campaign.py", "joulewise/reduce.py", "joulewise/uncertainty_evidence.py",
               "joulewise/powermetrics_fiducial.py", "joulewise/adapters/powermetrics.py", "scripts/prewindow_check.sh"}
    digests = {path: digest for path, digest in inventory.items()
               if path in singles or path.startswith("joulewise/flags/") or path.startswith(PACK_PREFIXES)}
    digests.update({path: digest for path, digest in pins.pins["pin4"]["files"].items()
                    if path != "joulewise/whole_window.py"})
    for name, key in (("registration_block5.md", "registration_sha256"), ("analysis_plan_block5.md", "analysis_plan_sha256"),
                      ("sealed_inventory.json", "inventory_sha256"), ("flag_catalog.json", "catalog_sha256"),
                      ("identity_pins.json", "identity_pins_sha256"), ("sizing_b5.json", "sizing_sha256")):
        digests[SEALED_DIR + name] = pins.sealed[key]
    return digests


def _bytes(root, path):
    if path not in EVOLVED_ON_MAIN:
        return (root / path).read_bytes()
    return subprocess.run(["git", "-C", str(root), "show", f"{B5_ANALYSIS_COMMIT}:{path}"],
                          check=True, capture_output=True).stdout


def rebound_mismatches(root=ROOT):
    result = []
    for path, digest in REBOUND_WORKING_TREE.items():
        try:
            same = hashlib.sha256((root / path).read_bytes()).hexdigest() == digest
        except OSError:
            same = False
        if not same:
            result.append(path)
    return result


def frozen_mismatches(root=ROOT):
    result = []
    for path, digest in frozen_digests().items():
        try:
            same = hashlib.sha256(_bytes(root, path)).hexdigest() == digest
        except (OSError, subprocess.CalledProcessError):
            same = False
        if not same:
            result.append(path)
    return result


class FrozenFilesTests(unittest.TestCase):
    def test_frozen_files(self):
        self.assertEqual(frozen_mismatches(), [])

    def test_rebound_files_keep_their_rebound_bytes(self):
        self.assertEqual(rebound_mismatches(), [])
        self.assertTrue(set(REBOUND_WORKING_TREE) <= EVOLVED_ON_MAIN)
        with tempfile.TemporaryDirectory() as temporary:
            for path in REBOUND_WORKING_TREE:
                edited = Path(temporary) / path
                edited.parent.mkdir(parents=True, exist_ok=True)
                edited.write_bytes((ROOT / path).read_bytes() + b"\n")   # one byte appended
            self.assertEqual(rebound_mismatches(Path(temporary)), sorted(REBOUND_WORKING_TREE))

    def test_seal_pins_match_every_printed_value(self):
        value = json.loads((ROOT / "configs/analysis/b5/seal_pins.json").read_bytes())
        text = SEAL.read_text()
        for shape, pin in value["pins"].items():
            number = shape.removeprefix("pin")
            section = text.split(f"## Addendum {number}:", 1)[1].split("\n## ", 1)[0]
            self.assertIn("B5-HARVEST-PIN: " + pin["head"], section)
            printed = dict(re.findall(r"((?:joulewise|scripts)/[\w/]+\.py) ([0-9a-f]{64})", section))
            self.assertEqual(pin["files"], printed)
        section = text.split("**The sealed digests of the second seal**", 1)[1].split("## Addendum 1:", 1)[0]
        for key, name in (("registration_sha256", "registration_block5.md"), ("analysis_plan_sha256", "analysis_plan_block5.md"),
                          ("inventory_sha256", "sealed_inventory.json"), ("catalog_sha256", "flag_catalog.json"),
                          ("sizing_sha256", "sizing_b5.json"), ("identity_pins_sha256", "identity_pins.json")):
            line = next(line for line in section.splitlines() if f"/{name}`" in line)
            self.assertIn(value["sealed"][key], line)
        for n in (2, 3):
            section = text.split(f"## Addendum {n + 1}:", 1)[1].split("\n## ", 1)[0]
            self.assertRegex(section, r"ERRATUM-" + str(n) + r"-ADMITTED-AT: .*Z")
            self.assertIn(f"epoch {value[f'erratum_{n}_epoch_s']}", section)
            digest = value["sealed"][f"erratum_{n}_sha256"]
            self.assertRegex(section, r"text as committed on main `" + digest + r"`")
        self.assertEqual(set(value), {"schema", "erratum_2_epoch_s", "erratum_3_epoch_s", "sealed", "pins"})
        self.assertEqual(value["schema"], "joulewise.b5_seal_pins.v1")

    def test_collection_does_not_import_analysis(self):
        for name in ("scripts/run_campaign.py", "joulewise/b5/harvest.py"):
            tree = ast.parse((ROOT / name).read_bytes())
            imports = [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
            imports += [f"{node.module or ''}.{alias.name}" for node in ast.walk(tree)
                        if isinstance(node, ast.ImportFrom) for alias in node.names]
            imports += [node.value for node in ast.walk(tree) if isinstance(node, ast.Constant)
                        and isinstance(node.value, str) and node.value.startswith("joulewise.b5_analysis")]
            self.assertFalse(any("b5_analysis" in name for name in imports))
