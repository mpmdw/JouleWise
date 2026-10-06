"""Digest-pin census: locating, resolving and classifying hard-coded SHA-256 pins (lane L7)."""

from __future__ import annotations

from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from scripts import digest_pin_census as census
from tests.git_fixture import init_git_fixture

ROOT = Path(__file__).resolve().parents[1]


def sha(raw: bytes | str) -> str:
    return hashlib.sha256(raw.encode("utf-8") if isinstance(raw, str) else raw).hexdigest()


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


RAW_CAPTURE_DIGEST = sha("raw powermetrics bytes that were never committed")
SYNTHETIC_DIGEST = sha("an inline synthetic test value")
REDUCE_SOURCE = "def reduce(samples):\n    return sum(samples)\n"
BATTERY_SOURCE = "LIMIT_MA = 200\n\n\ndef parse(raw):\n    return raw.strip()\n"


def build_tree(root: Path) -> dict[str, str]:
    """A miniature repository whose pins mirror the real kinds; returns digests by name."""

    run = json_bytes({"model": "qwen3-1p7b", "tokens": 512})
    prompt = json_bytes({"prompt": "Why is the sky blue?"})
    plan = json_bytes({
        "members": [{"config": "run_01.json", "config_sha256": sha(run)}],
        "prompt_pin_sha256": sha(prompt),
    })
    acceptance = json_bytes({"estimator_code_sha256": sha(REDUCE_SOURCE),
                             "raw_capture_sha256": RAW_CAPTURE_DIGEST})
    files: dict[str, bytes] = {
        "joulewise/reduce.py": REDUCE_SOURCE.encode(),
        "joulewise/battery_float.py": BATTERY_SOURCE.encode(),
        "joulewise/paper_validator.py": b"def validate(value):\n    return value\n",
        "configs/campaigns/packx/generate_configs.py": b"print('pack generator')\n",
        "configs/campaigns/packx/run_01.json": run,
        "configs/campaigns/packx/prompt_pin.json": prompt,
        "configs/campaigns/packx/plan_tree.json": plan,
        "configs/calibration/acceptance.json": acceptance,
        "configs/calibration/ledger_head.json": json_bytes({"acceptance_sha256": sha(acceptance)}),
        "tests/test_example.py": (
            f'PLAN_TREE_SHA256 = "{sha(plan)}"\n'
            f'LIMIT_MA_SOURCE_SHA256 = "{sha("LIMIT_MA = 200")}"\n'
            f'PLACEHOLDER = "{"a" * 64}"\n'
            f'SYNTHETIC = "{SYNTHETIC_DIGEST}"\n'
        ).encode(),
        "tests/fixtures/example/record.json": json_bytes({"config_sha256": sha(run)}),
        "tests/test_night_gate.py": f'RULED = {{"{SYNTHETIC_DIGEST}": "x"}}\n'.encode(),
    }
    for relative, raw in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    init_git_fixture(root, "-q")
    subprocess.run(["git", "-C", str(root), "add", "."], check=True)
    return {"run": sha(run), "prompt": sha(prompt), "plan": sha(plan), "acceptance": sha(acceptance)}


def rows_by_path(registry: dict) -> dict[str, list[tuple[str, str, str | None]]]:
    targets = registry["targets"]
    return {entry["path"]: [(pointer, family, None if index is None else targets[index])
                            for pointer, family, index in entry["rows"]]
            for entry in registry["files"]}


class LiteralLocationTests(unittest.TestCase):
    def test_json_pointers_cover_values_keys_and_lists(self) -> None:
        digest = sha("x")
        raw = json.dumps({"a": [{"b": digest}], digest: 1, "c/d": f"sha256:{digest}"}).encode()
        found = {(item.pointer, item.value) for item in census.literals_in("configs/x.json", raw)}
        self.assertEqual(found, {("/a/0/b", digest), (f"/{digest}#key", digest), ("/c~1d", digest)})

    def test_longer_hex_runs_and_uppercase_are_not_sha256_literals(self) -> None:
        raw = ("x = '" + "ab" * 64 + "'\ny = '" + "AB" * 32 + "'\n").encode()
        self.assertEqual(census.literals_in("tests/test_x.py", raw), [])

    def test_python_literals_carry_line_and_enclosing_binding(self) -> None:
        digest = sha("y")
        raw = f'import os\n\nPINS = {{\n    "k": "{digest}",\n}}\n\n\ndef f():\n    return "{digest}"\n'.encode()
        found = [(item.pointer, item.context) for item in census.literals_in("tests/test_x.py", raw)]
        self.assertEqual(found, [("#L4", "PINS"), ("#L9", "f")])

    def test_jsonl_rows_get_line_and_pointer(self) -> None:
        digest = sha("z")
        raw = (json.dumps({"a": 1}) + "\n" + json.dumps({"row": {"sha256": digest}}) + "\n").encode()
        found = [item.pointer for item in census.literals_in("tests/fixtures/x.jsonl", raw)]
        self.assertEqual(found, ["#L2/row/sha256"])


class ResolutionTests(unittest.TestCase):
    def test_every_method_round_trips_through_target_digest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            build_tree(root)
            files = census.tracked_files(root)
            index = census.build_index(root, files)
            seen_methods = set()
            for digest, targets in index.items():
                for target in targets:
                    seen_methods.add(target.method)
                    self.assertEqual(census.target_digest(root, target), digest, target)
            self.assertTrue({"file", "git_blob", "canonical_json", "canonical_json_nl", "py_def",
                             "py_segment"} <= seen_methods)
            # The decorator-inclusive form equals what inspect.getsource returns.
            self.assertIn(census.Target("joulewise/reduce.py::reduce", "py_def"), index[sha(REDUCE_SOURCE)])

    def test_missing_target_digest_is_none(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            self.assertIsNone(census.target_digest(Path(temporary), census.Target("gone.json", "file")))
            self.assertIsNone(census.target_digest(
                Path(temporary), census.Target("joulewise/x.py::missing", "py_def")))

    def test_nearest_target_wins_among_identical_files(self) -> None:
        targets = [census.Target("configs/campaigns/a/x.json", "file"),
                   census.Target("configs/campaigns/b/x.json", "file")]
        best = census._best_target(targets, "configs/campaigns/b/plan_tree.json")
        self.assertEqual(best.path, "configs/campaigns/b/x.json")
        self.assertIsNone(census._best_target([census.Target("tests/t.py", "file")], "tests/t.py"))


class ClassificationTests(unittest.TestCase):
    def literal(self, path: str, value: str = SYNTHETIC_DIGEST, context: str = "x") -> census.Literal:
        return census.Literal(path, "#L1", value, 1, context)

    def test_kind_p_families(self) -> None:
        core = census.Target("joulewise/reduce.py", "file")
        cases = {
            ("configs/campaigns/p/run.json", None): "pack_config_bytes",
            ("configs/campaigns/p/registration_block5.md", None): "sealed_registration",
            ("configs/calibration/acceptance.json", None): "calibration_issued",
            ("configs/floor_mint/spec.json", None): "floor_artifact",
            ("configs/paper_supply/supply_map.json", None): "supply_map_production",
            ("configs/model_panels/panel.json", None): "issued_config",
            ("tests/test_x.py", core): "estimator_code",
            ("tests/test_x.py", census.Target("joulewise/battery_float.py::parse", "py_def")): "issued_code",
            ("tests/test_x.py", census.Target("configs/campaigns/p/plan_tree.json", "file")): "pinned_config_copy",
            ("tests/test_x.py", census.Target("docs/process_traces/x/capture.txt", "file")): "recorded_evidence",
        }
        for (path, target), family in cases.items():
            with self.subTest(path=path, target=target):
                self.assertEqual(census.classify(self.literal(path), target), family)
                self.assertEqual(census.FAMILIES[family]["kind"], "P")

    def test_kind_b_families(self) -> None:
        cases = {
            (self.literal("tests/test_x.py", "a" * 64), None): "placeholder",
            (self.literal("tests/fixtures/x/r.json"), census.Target("configs/campaigns/p/run.json", "file")):
                "fixture_content",
            (self.literal("tests/goldens/g.json"), None): "fixture_content",
            (self.literal("tests/test_x.py", context="EXPECTED_ROW"), None): "synthetic_literal",
            (self.literal("tests/test_x.py"), census.Target("joulewise/paper_validator.py::validate", "py_def")):
                "source_digest",
        }
        for (literal, target), family in cases.items():
            with self.subTest(literal=literal.path, target=target):
                self.assertEqual(census.classify(literal, target), family)
                self.assertEqual(census.FAMILIES[family]["kind"], "B")

    def test_unresolved_test_pin_with_number_context_stays_kind_p(self) -> None:
        literal = self.literal("tests/test_x.py", context="V3_REGISTRATION_SHA256")
        self.assertEqual(census.classify(literal, None), "historical_pin")

    def test_estimator_code_key_in_an_acceptance_is_kind_p_even_unresolved(self) -> None:
        literal = census.Literal("configs/calibration/a.json", "/estimator_code_sha256", SYNTHETIC_DIGEST, 1,
                                 "estimator_code_sha256")
        self.assertEqual(census.classify(literal, None), "estimator_code")

    def test_only_resolved_kind_p_outside_fixtures_is_checked(self) -> None:
        plan = "configs/campaigns/p/plan_tree.json"
        self.assertTrue(census.is_checked(plan, "pack_config_bytes", "configs/campaigns/p/run.json"))
        self.assertTrue(census.is_checked("configs/calibration/a.json", "estimator_code", "joulewise/reduce.py"))
        self.assertTrue(census.is_checked("tests/test_x.py", "recorded_evidence", "docs/process_traces/x.txt"))
        self.assertFalse(census.is_checked(plan, "pack_config_bytes", None))
        self.assertFalse(census.is_checked("tests/fixtures/x.json", "recorded_evidence", "docs/x.txt"))
        self.assertFalse(census.is_checked("tests/test_x.py", "synthetic_literal", "tests/x.json"))
        # A config's record of non-core code or archived documents is provenance of its era.
        self.assertFalse(census.is_checked(plan, "pack_config_bytes", "joulewise/__init__.py::x"))
        self.assertFalse(census.is_checked(plan, "pack_config_bytes", "docs/process_traces/runsheet.md"))


class CensusTests(unittest.TestCase):
    def test_census_of_a_miniature_tree(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            digests = build_tree(root)
            registry = census.census(root)
            rows = rows_by_path(registry)
            self.assertEqual(rows["configs/campaigns/packx/plan_tree.json"], [
                ("/members/0/config_sha256", "pack_config_bytes", "file:configs/campaigns/packx/run_01.json"),
                ("/prompt_pin_sha256", "pack_config_bytes", "file:configs/campaigns/packx/prompt_pin.json"),
            ])
            self.assertEqual(rows["configs/calibration/acceptance.json"], [
                ("/estimator_code_sha256", "estimator_code", "file:joulewise/reduce.py"),
                ("/raw_capture_sha256", "calibration_issued", None),
            ])
            self.assertEqual(rows["tests/test_example.py"], [
                ("#L1", "pinned_config_copy", "file:configs/campaigns/packx/plan_tree.json"),
                ("#L2", "issued_code", "py_segment:joulewise/battery_float.py::LIMIT_MA"),
                ("#L3", "placeholder", None),
                ("#L4", "synthetic_literal", None),
            ])
            self.assertEqual(rows["tests/fixtures/example/record.json"],
                             [("/config_sha256", "fixture_content", "file:configs/campaigns/packx/run_01.json")])
            entry = next(item for item in registry["files"] if item["path"] == "configs/campaigns/packx/plan_tree.json")
            self.assertEqual(entry["regenerators"], ["pack:packx"])
            summary = registry["summary"]
            self.assertEqual(summary["literals"], 11)
            self.assertEqual(summary["by_kind"], {"P": 7, "B": 4})
            self.assertEqual(summary["resolved_checked"], 6)
            # A Kind-B literal in another lane's file is a follow-up, never an edit.
            self.assertIn({"lane": "L2", "path": "tests/test_night_gate.py", "family": "synthetic_literal",
                           "count": 1}, registry["followups"])
            self.assertTrue(digests["plan"])

    def test_render_is_line_oriented_and_round_trips(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            build_tree(root)
            registry = census.census(root)
            text = census.render(registry)
            self.assertEqual(json.loads(text), registry)
            self.assertIn('\n      ["#L1", "pinned_config_copy", ', text)
            with redirect_stdout(io.StringIO()):
                self.assertEqual(census.main(["--write", "--root", str(root)]), 0)
            self.assertEqual(census.load_registry(root), registry)


class CommittedRegistryTests(unittest.TestCase):
    """Shape checks on configs/pins/registry.json; freshness is not required."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = census.load_registry(ROOT)

    def test_schema_families_and_targets_are_consistent(self) -> None:
        registry = self.registry
        self.assertEqual(registry["schema"], census.SCHEMA)
        self.assertEqual(set(registry["families"]), set(census.FAMILIES))
        total = 0
        for entry in registry["files"]:
            self.assertTrue(entry["path"].startswith(census.SCOPE), entry["path"])
            for pointer, family, index in entry["rows"]:
                total += 1
                self.assertIn(family, census.FAMILIES)
                self.assertTrue(index is None or 0 <= index < len(registry["targets"]))
        self.assertEqual(total, registry["summary"]["literals"])
        self.assertEqual(sum(registry["summary"]["by_kind"].values()), total)

    def test_fixture_roles_left_the_supply_map(self) -> None:
        paths = {entry["path"] for entry in self.registry["files"]}
        self.assertNotIn("configs/paper_supply/supply_map.json", paths)

    def test_battery_float_freeze_is_kind_p_not_busywork(self) -> None:
        rows = rows_by_path(self.registry)["tests/test_battery_float.py"]
        frozen = [row for row in rows if row[2] and "joulewise/battery_float.py" in row[2]]
        self.assertEqual(len(frozen), 39)  # every FROZEN_FUNCTION_SOURCE_SHA256 entry resolves
        self.assertTrue(all(row[1] == "issued_code" for row in frozen))

    def test_core_source_pins_are_kind_p(self) -> None:
        rows = rows_by_path(self.registry)
        for path in ("tests/test_reduce.py", "tests/test_acc_25g83_rev5.py"):
            core = [row for row in rows[path] if row[2] and row[2].endswith("joulewise/reduce.py")]
            self.assertTrue(core and all(row[1] == "estimator_code" for row in core), path)

    def test_l2_ruled_registrations_table_is_a_named_followup(self) -> None:
        self.assertIn({"path": "joulewise/night_gate.py", "symbol": "RULED_REGISTRATIONS", "lane": "L2",
                       "note": census.EXTRA_FOLLOWUPS[0]["note"]}, self.registry["followups"])


if __name__ == "__main__":
    unittest.main()
