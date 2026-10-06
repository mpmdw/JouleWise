"""NUMBER coverage: every one of the 1,674 NUMBER rows says where its concern is evaluated now.

``configs/flags/number_rows.json`` (built by ``tests/flags/number_rows_builder.py``)
maps each NUMBER row of the gate-prune inventory either to its flag code, its
evaluation site on the block-5 path and a test, or to "retired path: protects
nothing block 5 runs" with the hazard-path equivalent named. This test fails on
an unmapped row, an evaluation site that does not exist, an unknown flag code
or a test id that does not resolve.
"""

from __future__ import annotations

import ast
import hashlib
import json
import unittest
from functools import lru_cache
from pathlib import Path

from joulewise.flags.catalog import DRAFT_CODES, SEALED_CATALOG_RELATIVE_PATH, load_catalog

REPO = Path(__file__).resolve().parents[2]
MAP = REPO / "configs" / "flags" / "number_rows.json"
EXPECTED_ROWS = 1674
STAGES = {"window", "harvest", "desk_arm", "analysis"}
# Hazard-path modules other lanes own; they may be absent from this lane's tree.
PENDING_SITES = {
    "joulewise/hazards/": "L1",
    "joulewise/b5/": "L2/L5",
    "joulewise/window_lineage.py": "L3",
    "scripts/g10_clock_step_control.py": "L8",
}
RETIRED_SITE_FILES = {
    "joulewise/arm_readiness_evidence.py", "joulewise/arm_readiness_evidence_t0.py",
    "scripts/capture_t0_step.py", "scripts/launch_window.py", "joulewise/t0_rehearsal.py",
    "joulewise/v5_qualification.py", "scripts/write_v5_qualification_plan.py",
    "scripts/harvest_v5_qualification.py", "scripts/harvest_v5_g2b_window.py", "joulewise/night_gate.py",
}


@lru_cache(maxsize=None)
def qualnames(path: str) -> frozenset[str]:
    tree = ast.parse((REPO / path).read_text(encoding="utf-8"))
    names: set[str] = set()

    def walk(node: ast.AST, prefix: list[str]) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                qual = prefix + [child.name]
                names.add(".".join(qual))
                walk(child, qual)
            else:
                walk(child, prefix)

    walk(tree, [])
    return frozenset(names)


@lru_cache(maxsize=None)
def nodes_of_test_file(path: str) -> frozenset[str]:
    tree = ast.parse((REPO / path).read_text(encoding="utf-8"))
    nodes: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            nodes.add(node.name)
        elif isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    nodes.add(f"{node.name}::{item.name}")
    return frozenset(nodes)


def pending_site(path: str) -> bool:
    return any(path == key or (key.endswith("/") and path.startswith(key)) for key in PENDING_SITES)


class NumberCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads(MAP.read_text(encoding="utf-8"))
        cls.rows = cls.document["rows"]
        cls.pending_tests = cls.document["pending_lane_tests"]
        sealed = REPO / SEALED_CATALOG_RELATIVE_PATH
        cls.codes = set(load_catalog(sealed).codes) if sealed.exists() else set(DRAFT_CODES)

    def resolve_test(self, test_id: str, where: str) -> None:
        path, _, node = test_id.partition("::")
        if (REPO / path).is_file():
            if node:
                self.assertIn(node, nodes_of_test_file(path), f"{where}: test {test_id} does not exist")
            return
        if (REPO / path).is_dir():
            self.assertTrue(any((REPO / path).glob("test_*.py")), f"{where}: {path} has no tests")
            return
        self.assertIn(path, self.pending_tests, f"{where}: test file {path} missing and not a pending lane test")
        self.assertFalse(path.startswith("tests/flags/"), f"{where}: this lane's test {path} must exist")

    def resolve_site(self, site: str, where: str) -> None:
        path, _, function = site.partition(":")
        if not (REPO / path).exists():
            self.assertTrue(pending_site(path), f"{where}: evaluation site {path} does not exist")
            return
        if function and path.endswith(".py") and function != "<module>":
            self.assertIn(function, qualnames(path), f"{where}: {site} is not a function in {path}")

    def test_every_number_row_is_mapped_once(self) -> None:
        self.assertEqual(self.document["schema_version"], "joulewise.number_rows.v1")
        self.assertEqual(self.document["inventory"]["number_rows"], EXPECTED_ROWS)
        self.assertEqual(len(self.rows), EXPECTED_ROWS)
        keys = [row["key"] for row in self.rows]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(
            sum(self.document["counts"]["by_disposition"].values()), EXPECTED_ROWS
        )

    def test_evaluated_rows_name_a_live_site_a_known_code_and_a_test(self) -> None:
        for row in self.rows:
            if row["disposition"] != "evaluated":
                continue
            where = row["key"]
            self.assertIn(row["stage"], STAGES, where)
            self.resolve_site(row["evaluation_site"], where)
            self.assertNotIn(row["evaluation_site"].partition(":")[0], RETIRED_SITE_FILES, where)
            if row["stage"] == "analysis":
                self.assertIsNone(row["flag_code"], where)
            else:
                self.assertIn(row["flag_code"], self.codes, where)
            self.assertTrue(row["test_id"], where)
            self.resolve_test(row["test_id"], where)

    def test_retired_rows_name_their_hazard_path_equivalent(self) -> None:
        retired = [row for row in self.rows if row["disposition"] == "retired_path"]
        self.assertTrue(retired)
        for row in retired:
            where = row["key"]
            self.assertEqual(row["note"], "retired path: protects nothing block 5 runs", where)
            equivalent = row["equivalent"]
            self.assertIn(equivalent["stage"], STAGES, where)
            if equivalent["flag_code"] is not None:
                self.assertIn(equivalent["flag_code"], self.codes, where)
            else:
                self.assertTrue(
                    equivalent["evaluation_site"].startswith(
                        ("joulewise/flags/exclusions.py:first_claim_usable", "joulewise/b5/harvest.py",
                         "scripts/run_night.py:_terminate_process_group")
                    ),
                    where,
                )
            self.resolve_site(equivalent["evaluation_site"], where)
            self.resolve_test(equivalent["test_id"], where)

    def test_only_known_dispositions(self) -> None:
        self.assertEqual({row["disposition"] for row in self.rows}, {"evaluated", "retired_path"})

    def test_pending_lane_tests_exist_once_their_lane_has_landed(self) -> None:
        landed = {
            "L1": (REPO / "joulewise" / "hazards").is_dir(),
            "L2": (REPO / "joulewise" / "b5" / "chain.py").exists(),
            "L3": (REPO / "joulewise" / "window_lineage.py").exists(),
            "L5": (REPO / "joulewise" / "b5" / "harvest.py").exists(),
            "L8": (REPO / "scripts" / "g10_clock_step_control.py").exists(),
        }
        for path, lane in self.pending_tests.items():
            with self.subTest(path=path, lane=lane):
                if landed.get(lane):
                    self.assertTrue((REPO / path).exists(), f"{lane} landed without {path}")

    def test_map_covers_the_inventory_when_it_is_available(self) -> None:
        inventory = Path(self.document["inventory"]["path"])
        if not inventory.exists():
            self.skipTest("gate-prune inventory is not on this machine")
        raw = inventory.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), self.document["inventory"]["sha256"])
        number = [row for row in json.loads(raw)["refusals"] if row.get("klass") == "NUMBER"]
        self.assertEqual(len(number), EXPECTED_ROWS)
        mapped = {(row["file"], row["line_at_base"], row["code"]) for row in self.rows}
        missing = [(row["file"], row["line"], row["code"]) for row in number
                   if (row["file"], int(row["line"]), row["code"]) not in mapped]
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
