"""Freeze block-5 Git trees, independent of main (F1; freeze_p1_rebind.md)."""
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import unittest
from unittest import mock

from joulewise.freeze_by_commit import (
    ROOT, REGISTRATION_COMMIT_ENV, blob, blob_digests, load_registration, verify_tag,
)

SEALED_DIR = "configs/campaigns/v5_claim_25g83/"
SEAL = "docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md"


def frozen_mismatches(root=ROOT):
    """F1: verify registered Git trees; current main may evolve independently."""
    registration = load_registration(root)
    commits = {tag: verify_tag(root, tag, record)
               for tag, record in registration["tags"].items()}
    analysis = commits[registration["active_analysis"]]
    pins = json.loads(blob(root, analysis, "configs/analysis/b5/seal_pins.json"))
    inventory_raw = blob(root, analysis, SEALED_DIR + "sealed_inventory.json")
    inventory = json.loads(inventory_raw)
    if inventory["head"] != commits["b5/collection"]:
        return ["collection_commit"]
    expected = inventory["files"]
    actual = blob_digests(root, commits["b5/collection"], expected)
    result = [path for path in expected if actual[path] != expected[path]]
    if hashlib.sha256(inventory_raw).hexdigest() != pins["sealed"]["inventory_sha256"]:
        result.append("sealed_inventory_sha256")
    # Each historical harvest amendment owns its own tree, including the
    # whole_window code that the analysis subsequently evolved under rulings.
    for pin in pins["pins"].values():
        actual = blob_digests(root, pin["head"], pin["files"])
        result.extend(path for path, digest in pin["files"].items() if actual[path] != digest)
    for tag in ("b5/analysis", registration["active_analysis"]):
        for name, key in (("registration_block5.md", "registration_sha256"),
                          ("analysis_plan_block5.md", "analysis_plan_sha256"),
                          ("sealed_inventory.json", "inventory_sha256"),
                          ("flag_catalog.json", "catalog_sha256"),
                          ("identity_pins.json", "identity_pins_sha256"),
                          ("sizing_b5.json", "sizing_sha256")):
            path = SEALED_DIR + name
            if hashlib.sha256(blob(root, commits[tag], path)).hexdigest() != pins["sealed"][key]:
                result.append(tag + ":" + path)
    return result


def registered_blob(tag, path):
    value = load_registration()
    return blob(ROOT, verify_tag(ROOT, tag, value["tags"][tag]), path)


def analysis_blob(path):
    return registered_blob(load_registration()["active_analysis"], path)


class FrozenFilesTests(unittest.TestCase):
    def setUp(self):
        environment = mock.patch.dict(os.environ)
        environment.start()
        self.addCleanup(environment.stop)
        os.environ.pop(REGISTRATION_COMMIT_ENV, None)

    def test_frozen_files(self):
        self.assertEqual(frozen_mismatches(), [])

    def test_freeze_does_not_open_worktree_source_bytes(self):
        read_bytes = Path.read_bytes
        def registered_metadata_only(path):
            self.assertEqual(path, ROOT / "configs/analysis/b5/freeze_commits.json")
            return read_bytes(path)
        with mock.patch.object(Path, "read_bytes", registered_metadata_only):
            self.assertEqual(frozen_mismatches(), [])

    def test_seal_pins_match_every_printed_value(self):
        value = json.loads(analysis_blob("configs/analysis/b5/seal_pins.json"))
        text = analysis_blob(SEAL).decode()
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
        for tag in ("b5/collection", load_registration()["active_analysis"]):
            for name in ("scripts/run_campaign.py", "joulewise/b5/harvest.py"):
                with self.subTest(tag=tag, path=name):
                    tree = ast.parse(registered_blob(tag, name))
                    imports = [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
                    imports += [f"{node.module or ''}.{alias.name}" for node in ast.walk(tree)
                                if isinstance(node, ast.ImportFrom) for alias in node.names]
                    imports += [node.value for node in ast.walk(tree) if isinstance(node, ast.Constant)
                                and isinstance(node.value, str) and node.value.startswith("joulewise.b5_analysis")]
                    self.assertFalse(any("b5_analysis" in name for name in imports))
