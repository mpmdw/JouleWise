"""Plan §2.4 (Ed's point a): did we drop a check that protected a number?

``configs/gates/physics_rows.json`` holds the 460 inventory rows classed
PHYSICS_DIRECT (209) and PHYSICS_PROXY (251), keyed by (file, function, code,
occurrence) at a0a4f5a7.  Each row must be in exactly one of:

- one hazard module's ``PROTECTS``;
- "unchanged in core: <file:function>" (the site must still exist);
- "retired proxy, replaced by <module>" (listed in that module's ``SUPERSEDES``);
- "on retired path, not run by block 5";

and must name a test that exists.  The checker fails on an unmapped row and
on a missing test id; both failure modes are exercised below.
"""
from __future__ import annotations

import ast
import copy
import hashlib
import json
import re
import unittest
from collections import Counter
from functools import lru_cache
from pathlib import Path

from joulewise.hazards import arm, battery, clock, contention, disk, instrument, thermal

ROOT = Path(__file__).resolve().parents[2]
ROWS = ROOT / "configs" / "gates" / "physics_rows.json"
INVENTORY = Path("/Users/edr/night-archive/gate-prune/inventory.json")
MODULES = {"clock": clock, "battery": battery, "thermal": thermal, "contention": contention,
           "disk": disk, "instrument": instrument, "arm": arm}
DISPOSITIONS = {"protects", "unchanged_in_core", "retired_proxy", "retired_path"}


@lru_cache(maxsize=None)
def _definitions(path: str) -> frozenset[str]:
    """Dotted names of every class and function defined in a Python file."""

    tree = ast.parse((ROOT / path).read_text())
    names: set[str] = set()

    def walk(node, prefix):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                names.add(prefix + child.name)
                walk(child, prefix + child.name + ".")
            else:
                walk(child, prefix)

    walk(tree, "")
    return frozenset(names)


def has_test(test_id: str) -> bool:
    try:
        path, cls, method = test_id.split("::")
    except ValueError:
        return False
    if not (ROOT / path).is_file():
        return False
    return f"{cls}.{method}" in _definitions(path)


def site_exists(site: str) -> bool:
    path, _sep, function = site.rpartition(":")
    if not (ROOT / path).is_file():
        return False
    if function in ("<module>", "<script>", "<document>"):
        return True
    if path.endswith(".py"):
        return function in _definitions(path)
    if path.endswith(".sh"):
        return re.search(rf"^\s*{re.escape(function)}\s*\(\)\s*\{{", (ROOT / path).read_text(),
                         re.M) is not None
    return function in (ROOT / path).read_text()


def module_keys(modules=MODULES):
    protects, supersedes = {}, {}
    problems = []
    for name, module in modules.items():
        for attribute, table in (("PROTECTS", protects), ("SUPERSEDES", supersedes)):
            for key in getattr(module, attribute):
                if key in table or key in protects or key in supersedes:
                    problems.append(f"{key} listed twice ({name}.{attribute})")
                table[key] = name
    return protects, supersedes, problems


def coverage_problems(document, modules=MODULES) -> list[str]:
    """Every reason the coverage map is not complete and exact."""

    problems = []
    protects, supersedes, duplicated = module_keys(modules)
    problems += duplicated
    seen = set()
    for entry in document["rows"]:
        key = entry.get("key") or {}
        k = (key.get("file"), key.get("function"), key.get("code"), key.get("occurrence"))
        label = f"{k[0]}:{entry.get('line_at_base')} {k[2]}"
        if k in seen:
            problems.append(f"duplicate key {label}")
        seen.add(k)
        disposition = entry.get("disposition")
        if disposition not in DISPOSITIONS:
            problems.append(f"unmapped row {label}")
            continue
        test = entry.get("test")
        if not test or not has_test(test):
            problems.append(f"missing test id {test!r} for {label}")
        if disposition == "protects":
            if protects.get(k) != entry.get("module"):
                problems.append(f"{label} not in {entry.get('module')}.PROTECTS")
            if entry.get("mapping") != f"protected by {entry.get('module')}":
                problems.append(f"{label} mapping text")
        elif disposition == "retired_proxy":
            if supersedes.get(k) != entry.get("module"):
                problems.append(f"{label} not in {entry.get('module')}.SUPERSEDES")
            if entry.get("mapping") != f"retired proxy, replaced by {entry.get('module')}":
                problems.append(f"{label} mapping text")
        elif disposition == "unchanged_in_core":
            if not site_exists(entry.get("site", "")):
                problems.append(f"{label} site {entry.get('site')!r} does not exist")
            if entry.get("mapping") != f"unchanged in core: {entry.get('site')}":
                problems.append(f"{label} mapping text")
        elif entry.get("mapping") != "on retired path, not run by block 5":
            problems.append(f"{label} mapping text")
        if disposition not in ("protects",) and k in protects:
            problems.append(f"{label} is {disposition} but also in {protects[k]}.PROTECTS")
        if disposition != "retired_proxy" and k in supersedes:
            problems.append(f"{label} is {disposition} but also in {supersedes[k]}.SUPERSEDES")
    for k, name in {**protects, **supersedes}.items():
        if k not in seen:
            problems.append(f"{name} lists {k}, which is not a physics row")
    return problems


class PhysicsCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(ROWS.read_text())

    def test_all_460_physics_rows_are_present(self):
        rows = self.document["rows"]
        self.assertEqual(self.document["schema"], "joulewise.physics_rows.v1")
        self.assertEqual(len(rows), 460)
        self.assertEqual(Counter(row["klass"] for row in rows),
                         {"PHYSICS_DIRECT": 209, "PHYSICS_PROXY": 251})

    def test_every_row_is_in_exactly_one_place_with_an_existing_test(self):
        self.assertEqual(coverage_problems(self.document), [])

    def test_the_checker_fails_on_an_unmapped_row(self):
        broken = copy.deepcopy(self.document)
        broken["rows"][17].pop("disposition")
        problems = coverage_problems(broken)
        self.assertTrue(any(problem.startswith("unmapped row") for problem in problems), problems)

    def test_the_checker_fails_on_a_missing_test_id(self):
        broken = copy.deepcopy(self.document)
        broken["rows"][3]["test"] = "tests/hazards/test_clock.py::FrequencyGateTests::test_does_not_exist"
        broken["rows"][4].pop("test")
        problems = [p for p in coverage_problems(broken) if p.startswith("missing test id")]
        self.assertEqual(len(problems), 2, problems)

    def test_the_checker_fails_when_a_module_drops_or_doubles_a_row(self):
        entry = next(row for row in self.document["rows"] if row["disposition"] == "protects"
                     and row["module"] == "thermal")
        key = tuple(entry["key"][field] for field in ("file", "function", "code", "occurrence"))
        fake_thermal = type("M", (), {"PROTECTS": tuple(k for k in thermal.PROTECTS if k != key),
                                      "SUPERSEDES": thermal.SUPERSEDES})
        problems = coverage_problems(self.document, {**MODULES, "thermal": fake_thermal})
        self.assertTrue(any("not in thermal.PROTECTS" in problem for problem in problems))
        fake_disk = type("M", (), {"PROTECTS": disk.PROTECTS + (key,), "SUPERSEDES": disk.SUPERSEDES})
        problems = coverage_problems(self.document, {**MODULES, "disk": fake_disk})
        self.assertTrue(any("listed twice" in problem for problem in problems))

    def test_every_hazard_module_protects_something(self):
        for name in ("clock", "battery", "thermal", "contention", "disk", "instrument"):
            self.assertTrue(MODULES[name].PROTECTS, name)

    def test_rows_match_the_inventory_when_it_is_on_this_machine(self):
        if not INVENTORY.is_file():
            self.skipTest("the gate-prune inventory is not on this machine")
        data = INVENTORY.read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(),
                         self.document["source"]["inventory_sha256"])
        inventory = Counter((row["file"], row["line"], row["code"], row["klass"])
                            for row in json.loads(data)["refusals"]
                            if row["klass"].startswith("PHYSICS"))
        mapped = Counter((row["key"]["file"], row["line_at_base"], row["key"]["code"], row["klass"])
                         for row in self.document["rows"])
        self.assertEqual(inventory, mapped)


if __name__ == "__main__":
    unittest.main()
