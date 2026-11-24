"""Synthetic BYTES rosters carry no key the harvest does not write (cold review of #949, RL-201 §4.2(1)).

The harvest's own writer (``joulewise/b5/harvest.py`` ``build_roster`` and
``l4_exclusion_inputs``, written by ``Harvest.finish``), run on the registered
configs of all twelve BYTES sub-packs, fixes the real roster shape without
opening any archive. The BYTES generators write rosters through the one shared
writer, ``tests/fixtures/bytes/harvest_roster.py``. This module generates with
each generator and walks every roster it writes.
"""
from collections import Counter
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from joulewise.b5 import harvest
from tests.fixtures.bytes import harvest_roster

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/bytes"
PACKS = tuple(f"bytes-s{n}-p{p}" for p in (1, 2) for n in range(1, 7))


def load(name):
    spec = importlib.util.spec_from_file_location("roster_shape_" + name, FIXTURES / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def harvest_written(pack):
    """``derived/roster.json`` as the harvest writes it for a registered sub-pack (configs only)."""
    pack_root = ROOT / "configs/campaigns" / pack
    document, _spans = harvest.l4_exclusion_inputs(harvest.build_roster(pack_root, ROOT), {}, plan_id=pack, attempt=1)
    return {key: value for key, value in document.items() if key not in harvest_roster.WITHHELD_KEYS}


def shape_of(documents):
    shape = {"document": set(), "member": set(), "unit": set(), "cell": set()}
    for document in documents:
        shape["document"].update(document)
        for member in document["members"]:
            shape["member"].update(member)
            for unit in member["units"]:
                shape["unit"].update(unit)
        for cell in document["cells"]:
            shape["cell"].update(cell)
    return shape


def foreign_keys(document, shape):
    """Each key of a roster document that the harvest does not write, with where it sits."""
    found = [("document", key) for key in document if key not in shape["document"]]
    for member in document.get("members", []):
        found += [(f"member {member.get('run_id')}", key) for key in member if key not in shape["member"]]
        for unit in member.get("units", []):
            found += [(f"unit of {member.get('run_id')}", key) for key in unit if key not in shape["unit"]]
    for cell in document.get("cells", []):
        if not isinstance(cell, dict):
            found.append(("cell", type(cell).__name__))
            continue
        found += [("cell", key) for key in cell if key not in shape["cell"]]
    return found


class RosterShapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.written = {pack: harvest_written(pack) for pack in PACKS}
        cls.shape = shape_of(cls.written.values())

    def test_the_harvest_writes_units_and_no_member_role(self):
        self.assertEqual(self.shape["member"], {"run_id", "stage_id", "kind", "units"})
        self.assertEqual(self.shape["unit"], {"cell_id", "stratum", "unit_id"})
        self.assertEqual(self.shape["document"], {"schema", "pack_id", "plan_id", "attempt", "members", "cells"})
        census = Counter((member["kind"], len(member["units"]))
                         for document in self.written.values() for member in document["members"])
        self.assertEqual(census, {("science", 1): 1000, ("auxiliary", 0): 300})

    def test_the_shared_writer_reproduces_the_harvest_members(self):
        for pack, written in self.written.items():
            with self.subTest(pack=pack):
                ours = harvest_roster.document(pack, [
                    harvest_roster.member(member["run_id"], member["stage_id"], member["units"])
                    for member in written["members"]])
                self.assertEqual(ours["members"], written["members"])
                self.assertEqual(set(ours), set(written))
                self.assertEqual(foreign_keys(ours, self.shape), [])

    def test_generated_rosters_carry_only_harvest_keys(self):
        with tempfile.TemporaryDirectory(prefix="bytes-roster-shape-") as directory:
            root = Path(directory)
            load("twin_synth").generate(root / "twin", seed=1, passes=2, defects=True,
                                        models=["Qwen3-4B-4bit", "Llama-3.3-70B-Instruct-4bit"])
            collected = ("bytes-s1-p1", "bytes-s5-p2")
            with patch("os.fsync", return_value=None):
                load("campaign").archive_campaign(
                    root / "campaign", non_claim=False, release="none", subpack_sessions=True,
                    uncollected_sessions=tuple(pack for pack in PACKS if pack not in collected))
            rosters = sorted(root.rglob("derived/roster.json"))
            self.assertGreaterEqual(len(rosters), 4)
            for path in rosters:
                raw = path.read_bytes()
                document = json.loads(raw)
                with self.subTest(roster=path.relative_to(root).as_posix()):
                    self.assertEqual(foreign_keys(document, self.shape), [])
                    self.assertTrue(document["members"])
                    self.assertEqual({key for member in document["members"] for key in member}, self.shape["member"])
                    # Written by the harvest's own writer, byte for byte.
                    self.assertEqual(raw, (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())

    def test_a_key_the_harvest_does_not_write_is_reported(self):
        document = harvest_roster.document("sim", [harvest_roster.member(
            "r1", "decode", [{"cell_id": "c", "stratum": "repeat", "unit_id": "0"}])])
        self.assertEqual(foreign_keys(document, self.shape), [])
        document["members"][0]["role"] = "science"
        document["members"][0]["units"][0]["config_key"] = "synthetic"
        document["cells"].append("c")
        self.assertEqual(foreign_keys(document, self.shape),
                         [("member r1", "role"), ("unit of r1", "config_key"), ("cell", "str")])


if __name__ == "__main__":
    unittest.main()
