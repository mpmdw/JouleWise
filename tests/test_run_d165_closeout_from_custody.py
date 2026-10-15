"""Synthetic custody tests for S7, including counterfactual refusal call sites."""

from __future__ import annotations

import copy
import functools
import hashlib
import io
import itertools
import json
import math
import tempfile
import unittest
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from dataclasses import FrozenInstanceError
from pathlib import Path
from unittest import mock

from configs.campaigns.d117_contrast_v5 import generate_configs as generator
from joulewise import analysis_manifest_v3 as manifests, dominance_closeout as core
from scripts import run_d165_closeout_from_custody as driver
from scripts.build_d165_dominance_closeout import build_d165_dominance_closeout
from tests import test_analysis_finalizer as finalizer_fixture
from tests.test_detection_floor import make_cell
from tests.test_d165_dominance_closeout import (
    _file_json_bytes, _recompute_sidecar_cell_result, replay_sidecar,
)


ENERGIES_8 = (10.0, 10.25, 9.875, 10.125, 10.0, 10.25, 9.75, 10.125)
DELTAS_8 = (1.0, -0.5, 2.0, 0.0, 0.5, 1.5, -0.5, 1.0)
PLAN_ENERGIES_9 = (10.0, 10.2, 9.9, 10.1, 10.0, 9.8, 10.1, 10.0, 9.6)
PLAN_DELTAS_8 = (0.10, -0.05, 0.20, 0.00, 0.05, 0.15, -0.05, 0.00)
_FIXTURE_DIRECTORIES = []


def _finalize(fixture, sidecar_path):
    return manifests.finalize_prospective_analysis_manifest_v3(
        fixture["prospective_path"], plan_tree_path=fixture["plan_tree_path"],
        custody_root=fixture["root"], runs_root=fixture["runs_root"],
        whole_window_verdict_path=fixture["verdict_path"], bracket_binding_path=fixture["bracket_path"],
        calibration_ledger_path=fixture["ledger_path"], aggregate_floor_artifact_path=fixture["floor_path"],
        dominance_replay_sidecar_path=sidecar_path, output_dir=fixture["root"],
    )


@functools.cache
def finalized_fixture(kind="default"):
    """Build each distinct finalization once per module, retain its tree and exact bytes."""
    temporary = tempfile.TemporaryDirectory(prefix=f"s7-{kind}-")
    _FIXTURE_DIRECTORIES.append(temporary)
    parameters = {}
    if kind != "default":
        energies, deltas, abs_width, cmp_width = ENERGIES_8, DELTAS_8, 0.0625, 0.25
        if kind == "different_n":
            energies = ENERGIES_8 + (10.0,)
        elif kind == "plan":
            energies, abs_width = PLAN_ENERGIES_9, 0.05
        elif kind == "zero":
            energies = (10.0,) * 8
        elif kind == "branch_a":
            deltas, abs_width, cmp_width = tuple(value / 16 for value in DELTAS_8), 0.5, 0.5
        elif kind in {"nine", "nine_removed"}:
            energies, deltas = ENERGIES_8 + (10.0,), DELTAS_8 + (0.5,)
        elif kind != "eight":
            raise AssertionError(f"unknown synthetic fixture: {kind}")
        parameters = dict(energies=energies, deltas=deltas,
                          absolute_half_widths=(abs_width,) * len(energies),
                          comparative_half_widths=(cmp_width,) * len(deltas))
    with mock.patch.object(finalizer_fixture, "make_cell", functools.partial(make_cell, **parameters)):
        fixture = finalizer_fixture.install_synthetic_finalization_fixture(
            Path(temporary.name), dominance_criterion=generator.dominance_criterion_registration(),
            acceptance_prefix=True,
        )
    floor = json.loads(fixture["floor_path"].read_bytes())
    sidecar = replay_sidecar(floor)
    if kind == "nine_removed":
        blocks = sidecar["cells"][0]["comparative"]["common_mode_replay"]["inputs"]["blocks"]
        removed = copy.deepcopy(blocks[-1])
        removed["block_id"] += "-removed-tenth"
        blocks.append(removed)
        _recompute_sidecar_cell_result(sidecar)
    sidecar_path = fixture["root"] / "dominance_replay_sidecar.json"
    sidecar_path.write_bytes(_file_json_bytes(sidecar))
    manifest = _finalize(fixture, sidecar_path)
    fixture.update(manifest=manifest, floor=floor, sidecar=sidecar, sidecar_path=sidecar_path,
                   manifest_path=fixture["root"] / f"{fixture['prospective']['manifest_id']}.finalized.json")
    fixture["cached_bytes"] = tuple(fixture[key].read_bytes()
                                     for key in ("manifest_path", "floor_path", "sidecar_path"))
    return fixture


def tearDownModule():
    for directory in reversed(_FIXTURE_DIRECTORIES):
        directory.cleanup()
    finalized_fixture.cache_clear()


def point_formula(values, *, comparative=False):
    """Independent D-054 formula, using the registered three-decimal t table."""
    n = len(values)
    t = {5: 2.776, 8: 2.365, 9: 2.306, 10: 2.262}[n]
    mean = sum(values) / n
    deviations = list(values) if comparative else [value - mean for value in values]
    dev_mean = sum(deviations) / n
    scatter = math.sqrt(math.fsum((value - dev_mean) ** 2 for value in deviations) / (n - 1))
    prediction = (abs(mean) if comparative else 0.0) + t * scatter * math.sqrt(1 + 1 / n)
    return max(max(abs(value) for value in deviations), prediction)


def corner_formula(values, width, *, comparative=False):
    return max(point_formula([value + sign * width for value, sign in zip(values, signs)],
                             comparative=comparative)
               for signs in itertools.product((-1, 1), repeat=len(values)))


@contextmanager
def replaced_bytes(path, raw):
    original = path.read_bytes()
    path.write_bytes(raw)
    try:
        yield
    finally:
        path.unlink(missing_ok=True)
        path.write_bytes(original)


def walk_values(value):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from walk_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_values(child)


class CloseoutDriverTests(unittest.TestCase):
    maxDiff = None

    def fixture(self, kind="default"):
        fixture = finalized_fixture(kind)
        # Re-read cached source bytes per test; a mutation must have restored the tree.
        self.assertEqual(tuple(fixture[key].read_bytes()
                               for key in ("manifest_path", "floor_path", "sidecar_path")),
                         fixture["cached_bytes"])
        return fixture

    def sources(self, fixture):
        return driver.resolve_closeout_sources(fixture["manifest_path"], fixture["root"])

    def output(self, fixture):
        temporary = tempfile.TemporaryDirectory(prefix="output-", dir=fixture["root"])
        self.addCleanup(temporary.cleanup)
        return Path(temporary.name) / "closeout.json"

    def main_run(self, fixture, output=None, *, manifest=None):
        argv = ["--finalized-manifest", str(manifest or fixture["manifest_path"]),
                "--custody-root", str(fixture["root"])]
        if output is not None:
            argv += ["--output", str(output)]
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = driver.main(argv)
        self.assertEqual(stderr.getvalue(), "")
        self.assertEqual(len(stdout.getvalue().splitlines()), 1)
        record = json.loads(stdout.getvalue())
        if output is not None:
            self.assertEqual(output.with_suffix(".step.json").read_bytes(), stdout.getvalue().encode())
        return status, record, stdout.getvalue()

    def issued(self, kind="eight"):
        fixture = self.fixture(kind)
        sources = self.sources(fixture)
        output = self.output(fixture)
        with redirect_stdout(io.StringIO()) as stdout, redirect_stderr(io.StringIO()) as stderr:
            status = driver.run_closeout(sources, output=output)
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(stderr.getvalue(), "")
        self.assertEqual(status, 0)
        return fixture, sources, output, json.loads(output.with_suffix(".ratio-table.json").read_bytes())

    def assert_no_outputs(self, output):
        self.assertFalse(output.exists())
        self.assertFalse(output.with_suffix(".ratio-table.json").exists())

    def assert_resolver_refusal(self, fixture, code, *, manifest=None):
        with self.assertRaises(driver.CloseoutDriverRefusal) as refused:
            driver.resolve_closeout_sources(manifest or fixture["manifest_path"], fixture["root"])
        self.assertEqual(refused.exception.code, code)
        self.assertEqual(str(refused.exception), code)
        output = self.output(fixture)
        status, record, _ = self.main_run(fixture, output, manifest=manifest)
        self.assertEqual(status, 2)
        self.assertEqual(record["refusal"], code)
        self.assert_no_outputs(output)

    def test_t1_eight_unguarded_ratio_not_times_guard(self):
        fixture, _, _, table = self.issued()
        expected = {}
        for component, values, width, rounded, wrong in (
            ("absolute", ENERGIES_8, 0.0625, 1.3390, 1.5182),
            ("comparative", DELTAS_8, 0.25, 1.2200, 1.3834),
        ):
            point = point_formula(values, comparative=component == "comparative")
            corner = corner_formula(values, width, comparative=component == "comparative")
            expected[component] = corner / point
            self.assertAlmostEqual(expected[component], rounded, places=4)
            self.assertAlmostEqual(expected[component] * math.sqrt(9 / 7), wrong, places=4)
        cells = {cell["cell_id"]: cell for cell in fixture["floor"]["cells"]}
        for row in table["ratios"]:
            if row["status"] == "complete":
                guard = cells[row["cell_id"]][row["component"]]["guard_factor"]
                self.assertEqual(guard, math.sqrt(9 / 7))
                self.assertNotAlmostEqual(
                    row["ratio"], (row["numerator_j"] / row["denominator_j"]) * guard,
                    delta=1e-6,
                )
                if row["ratio_id"] == "attribution_dominance_ratio.v1":
                    self.assertNotAlmostEqual(
                        row["ratio"], expected[row["component"]] * math.sqrt(9 / 7),
                        delta=1e-6,
                    )
                self.assertEqual(row["ratio"], row["numerator_j"] / row["denominator_j"])
                if row["ratio_id"] == "attribution_dominance_ratio.v1":
                    self.assertAlmostEqual(row["ratio"], expected[row["component"]], places=12)

    def test_t2_denominator_is_point_never_operative_unguarded(self):
        fixture, _, _, table = self.issued()
        cells = {cell["cell_id"]: cell for cell in fixture["floor"]["cells"]}
        for row in table["ratios"]:
            component = cells[row["cell_id"]][row["component"]]
            point = point_formula(ENERGIES_8 if row["component"] == "absolute" else DELTAS_8,
                                  comparative=row["component"] == "comparative")
            self.assertEqual(component["unguarded_floor_j"], component["corner_widened_unguarded_floor_j"])
            self.assertNotEqual(point, component["unguarded_floor_j"])
            self.assertAlmostEqual(row["denominator_j"], point, places=12)
            self.assertNotEqual(row["denominator_j"], component["unguarded_floor_j"])
            self.assertEqual(row["denominator_field"], "point_unguarded_floor_j")

    def test_t3_plan_nine_absolute_and_eight_comparative_formula(self):
        _, _, _, table = self.issued("plan")
        point = point_formula(PLAN_ENERGIES_9)
        corner = corner_formula(PLAN_ENERGIES_9, 0.05)
        ratio = corner / point
        self.assertAlmostEqual(point, 0.4382, places=4)
        self.assertAlmostEqual(corner, 0.5435, places=4)
        self.assertAlmostEqual(ratio, 1.2403, places=4)
        self.assertAlmostEqual(ratio * math.sqrt(9 / 8), 1.3156, places=4)
        for row in table["ratios"]:
            if row["component"] == "absolute":
                self.assertAlmostEqual(row["denominator_j"], point, places=12)
                self.assertAlmostEqual(row["numerator_j"], corner, places=12)
                self.assertAlmostEqual(row["ratio"], ratio, places=12)
                self.assertNotEqual(row["ratio"], ratio * math.sqrt(9 / 8))
        # The standard replay helper cannot carry the plan's non-dyadic deltas.
        fixture = self.fixture("eight")
        plan_floor = copy.deepcopy(fixture["floor"])
        for cell in plan_floor["cells"]:
            for block, delta in zip(cell["comparative"]["blocks"], PLAN_DELTAS_8):
                block["delta_j"] = delta
        with self.assertRaisesRegex(ValueError, "common_mode_replay_zero_point_membership_invalid"):
            replay_sidecar(plan_floor)
        comparative = corner_formula(PLAN_DELTAS_8, 0.30, comparative=True) / point_formula(PLAN_DELTAS_8, comparative=True)
        self.assertAlmostEqual(comparative, 3.8604, places=4)
        self.assertAlmostEqual(comparative * math.sqrt(9 / 7), 4.3773, places=4)

    def test_t4_all_twelve_rows_have_parts_and_component_specific_n(self):
        fixture, sources, output, table = self.issued("different_n")
        closeout = json.loads(output.read_bytes())
        cells = {cell["cell_id"]: cell for cell in fixture["floor"]["cells"]}
        records = closeout["independent_ratios"] + closeout["comparative_common_mode_ratios"]
        self.assertEqual(len(table["ratios"]), 12)
        self.assertEqual(table["schema_version"], driver.RATIO_TABLE_SCHEMA)
        self.assertEqual(table["closeout_sha256"], hashlib.sha256(output.read_bytes()).hexdigest())
        self.assertEqual(table["floor_artifact_sha256"], hashlib.sha256(sources.floor_bytes).hexdigest())
        for index, (row, record) in enumerate(zip(table["ratios"], records)):
            component = record.get("component", "comparative")
            numerator_field = ("corner_widened_unguarded_floor_j" if index < 8
                               else "common_mode_corner_widened_unguarded_floor_j")
            self.assertEqual(set(row), {"ratio_id", "cell_id", "component", "numerator_field", "numerator_j",
                                       "denominator_field", "denominator_j", "n", "n_field", "status", "ratio", "label"})
            self.assertEqual(row["cell_id"], record["cell_id"])
            self.assertEqual(row["component"], component)
            self.assertEqual(row["numerator_field"], numerator_field)
            self.assertEqual(row["numerator_j"], record[numerator_field])
            self.assertEqual(row["denominator_j"], record["point_unguarded_floor_j"])
            self.assertEqual(row["denominator_field"], "point_unguarded_floor_j")
            self.assertEqual(row["ratio"], record["ratio"])
            self.assertEqual(row["status"], record["status"])
            self.assertEqual(row["label"], "point diagnostic; no interval")
            self.assertEqual(row["n"], 9 if component == "absolute" else 8)
            self.assertEqual(row["n"], cells[row["cell_id"]][component]["n" if component == "absolute" else "n_blocks"])
            self.assertEqual(row["n_field"], "absolute.n" if component == "absolute" else "comparative.n_blocks")
            self.assertEqual(row["ratio_id"], "attribution_dominance_ratio.v1" if index < 8
                             else "attribution_dominance_ratio_common_mode.v1")
        self.assertNotIn("guard_factor", json.dumps(table))
        self.assertNotIn(str(fixture["root"]), json.dumps(table))

    def test_t4_invalid_counts_are_malformed_at_ratio_table(self):
        fixture = self.fixture("eight")
        sources = self.sources(fixture)
        closeout = build_d165_dominance_closeout(sources.manifest_bytes, sources.floor_bytes, sources.sidecar_bytes)
        for component, key in (("absolute", "n"), ("comparative", "n_blocks")):
            for n in (True, False, 0, -1, 8.0, None, "8"):
                with self.subTest(component=component, n=n):
                    floor = copy.deepcopy(fixture["floor"])
                    floor["cells"][0][component][key] = n
                    with self.assertRaises(driver.CloseoutDriverRefusal) as refused:
                        driver.build_ratio_table(closeout, floor, closeout_sha256="a" * 64, floor_artifact_sha256="b" * 64)
                    self.assertEqual(refused.exception.code, "closeout_input_malformed")

    def test_t5_closeout_bytes_are_builder_encoding_and_valid(self):
        _, sources, output, _ = self.issued()
        closeout = build_d165_dominance_closeout(sources.manifest_bytes, sources.floor_bytes, sources.sidecar_bytes)
        self.assertEqual(output.read_bytes(), _file_json_bytes(closeout))
        self.assertEqual(core.validate_d165_closeout(closeout, finalized_manifest_bytes=sources.manifest_bytes,
                         floor_artifact_bytes=sources.floor_bytes, replay_sidecar_bytes=sources.sidecar_bytes), [])

    def test_t6_branch_a_and_b_release_only_equal_structure(self):
        records = []
        for kind, branch in (("branch_a", "A"), ("default", "B")):
            fixture = self.fixture(kind)
            output = self.output(fixture)
            status, record, stdout = self.main_run(fixture, output)
            self.assertEqual(status, 0)
            closeout = json.loads(output.read_bytes())
            self.assertEqual(closeout["branch"], branch)
            self.assertFalse(any(isinstance(value, float) for value in walk_values(record)))
            self.assertNotIn("branch", stdout)
            self.assertNotIn("passes", stdout)
            for value in walk_values(closeout):
                if isinstance(value, (float, int)) and not isinstance(value, bool):
                    self.assertNotIn(repr(value), stdout)
            for entry in record["outputs"]:
                self.assertEqual(Path(entry["name"]).name, entry["name"])
                entry["sha256"] = "digest"
            records.append(record)
        self.assertEqual(records[0], records[1])

    def test_t7_deterministic_across_two_output_directories(self):
        fixture = self.fixture("eight")
        paths = [self.output(fixture), self.output(fixture)]
        sources = self.sources(fixture)
        for path in paths:
            self.assertEqual(driver.run_closeout(sources, output=path), 0)
        for suffix in (".json", ".ratio-table.json", ".step.json"):
            self.assertEqual(paths[0].with_suffix(suffix).read_bytes(), paths[1].with_suffix(suffix).read_bytes())

    def test_r1_prospective_rejected_at_resolver_schema_before_validator(self):
        """Prospective manifest -> resolve b -> manifest_not_finalized (M5)."""
        fixture = self.fixture()
        self.assert_resolver_refusal(fixture, "d165_closeout_driver_manifest_not_finalized",
                                     manifest=fixture["prospective_path"])
        with mock.patch.object(manifests, "validate_finalized_analysis_manifest_v3") as validator:
            with self.assertRaises(driver.CloseoutDriverRefusal) as refused:
                driver.resolve_closeout_sources(fixture["prospective_path"], fixture["root"])
            self.assertEqual(refused.exception.code, "d165_closeout_driver_manifest_not_finalized")
            validator.assert_not_called()

    def test_r2_swapped_floor_and_sidecar_rejected_at_resolver_digest(self):
        """Valid replacement attachment -> resolve e before validator -> exact digest codes (M6)."""
        fixture, other = self.fixture(), self.fixture("eight")
        for key, code in (("floor_path", "floor_artifact_source_hash_mismatch"),
                          ("sidecar_path", "replay_sidecar_digest_mismatch")):
            with self.subTest(key=key), replaced_bytes(fixture[key], other[key].read_bytes()):
                self.assert_resolver_refusal(fixture, code)

    def test_r2b_builder_still_rejects_swapped_floor_without_driver_guards(self):
        """Without resolve e/c -> builder _manifest_floor_artifact_digest_error still refuses."""
        fixture, other = self.fixture(), self.fixture("eight")
        with replaced_bytes(fixture["floor_path"], other["floor_path"].read_bytes()), \
             mock.patch.object(driver, "_check_attachment_digest"), \
             mock.patch.object(manifests, "validate_finalized_analysis_manifest_v3", return_value=()):
            sources = self.sources(fixture)
            output = self.output(fixture)
            self.assertEqual(driver.run_closeout(sources, output=output), 2)
        record = json.loads(output.with_suffix(".step.json").read_bytes())
        self.assertEqual(record["refusal"], "floor_artifact_source_hash_mismatch")
        self.assert_no_outputs(output)

    def test_r3_zero_point_is_registered_outcome_and_written(self):
        """Honest equal repeats -> builder _build_independent_record -> outcome (M7/M8)."""
        fixture = self.fixture("zero")
        output = self.output(fixture)
        status, record, stdout = self.main_run(fixture, output)
        self.assertEqual(status, 3)
        self.assertEqual(record["status"], "outcome_class")
        self.assertEqual(record["refusal"], "outcome-class refusal at step 6")
        self.assertNotIn("dominance_ratio_zero_denominator", stdout)
        self.assertTrue(record["schema_valid"])
        closeout = json.loads(output.read_bytes())
        self.assertEqual(closeout["refusal_reason"], "dominance_ratio_zero_denominator")
        self.assertIsNone(closeout["branch"])
        sources = self.sources(fixture)
        self.assertEqual(core.validate_d165_closeout(closeout, finalized_manifest_bytes=sources.manifest_bytes,
                         floor_artifact_bytes=sources.floor_bytes, replay_sidecar_bytes=sources.sidecar_bytes), [])
        table = json.loads(output.with_suffix(".ratio-table.json").read_bytes())
        for row in table["ratios"]:
            if row["component"] == "absolute":
                self.assertEqual(row["status"], "refused")
                self.assertIsNone(row["ratio"])
                self.assertEqual(row["denominator_j"], 0.0)
                self.assertGreater(row["numerator_j"], 0.0)
                self.assertEqual(row["n"], 8)

    def test_r4_removed_tenth_block_rejected_at_builder_member_census(self):
        """Valid ten-block sidecar against nine kept blocks -> _floor_member_census_error."""
        fixture = self.fixture("nine")
        output = self.output(fixture)
        self.assertEqual(driver.run_closeout(self.sources(fixture), output=output), 0)
        # This separately cached tree goes through real library finalization without bypasses.
        removed_fixture = self.fixture("nine_removed")
        self.assertEqual(core.validate_d165_replay_sidecar(removed_fixture["sidecar"]), [])
        sources = self.sources(removed_fixture)
        refused_output = self.output(removed_fixture)
        self.assertEqual(driver.run_closeout(sources, output=refused_output), 2)
        self.assertEqual(json.loads(refused_output.with_suffix(".step.json").read_bytes())["refusal"],
                         "floor_member_census_mismatch")
        self.assert_no_outputs(refused_output)
        with mock.patch.object(core, "_floor_member_census_error", return_value=None):
            bypass = build_d165_dominance_closeout(sources.manifest_bytes, sources.floor_bytes, sources.sidecar_bytes)
        self.assertNotEqual(bypass["refusal_reason"], "floor_member_census_mismatch")
        self.assertEqual(removed_fixture["manifest"]["evidence"]["dominance_replay_sidecar"]["sha256"],
                         hashlib.sha256(sources.sidecar_bytes).hexdigest())

    def test_r5_symlink_attachment_rejected_at_nofollow_read(self):
        """Right bytes behind final/parent symlink -> resolve d -> attachment_unreadable (M9)."""
        fixture = self.fixture()
        original = fixture["sidecar_path"].read_bytes()
        target = fixture["root"] / "symlink-target.json"
        target.write_bytes(original)
        fixture["sidecar_path"].unlink()
        fixture["sidecar_path"].symlink_to(target)
        try:
            self.assert_resolver_refusal(fixture, "d165_closeout_driver_attachment_unreadable")
        finally:
            fixture["sidecar_path"].unlink()
            fixture["sidecar_path"].write_bytes(original)
            target.unlink()
        parent = fixture["root"] / "linked-floor-directory"
        parent.symlink_to(fixture["floor_path"].parent, target_is_directory=True)
        manifest = copy.deepcopy(fixture["manifest"])
        manifest["evidence"]["aggregate_floor_artifact"]["path"] = f"{parent.name}/{fixture['floor_path'].name}"
        with replaced_bytes(fixture["manifest_path"], _file_json_bytes(manifest)):
            self.assert_resolver_refusal(fixture, "d165_closeout_driver_attachment_unreadable")
        parent.unlink()

    def test_r5_missing_and_escaping_attachment_rejected_at_path_read(self):
        """Absent file, missing record, ../x or absolute path -> resolve d -> attachment_unreadable."""
        fixture = self.fixture()
        original = fixture["floor_path"].read_bytes()
        fixture["floor_path"].unlink()
        try:
            self.assert_resolver_refusal(fixture, "d165_closeout_driver_attachment_unreadable")
        finally:
            fixture["floor_path"].write_bytes(original)
        for path in ("../x", str(fixture["floor_path"]), "floors/../aggregate_floor.json", ""):
            manifest = copy.deepcopy(fixture["manifest"])
            manifest["evidence"]["aggregate_floor_artifact"]["path"] = path
            with self.subTest(path=path), replaced_bytes(fixture["manifest_path"], _file_json_bytes(manifest)):
                self.assert_resolver_refusal(fixture, "d165_closeout_driver_attachment_unreadable")
        manifest["evidence"].pop("aggregate_floor_artifact")
        with replaced_bytes(fixture["manifest_path"], _file_json_bytes(manifest)):
            self.assert_resolver_refusal(fixture, "d165_closeout_driver_attachment_unreadable")

    def test_r6_unreadable_manifest_at_initial_read(self):
        """Absent, non-JSON, non-object, invalid UTF-8, directory or symlink -> resolve a."""
        fixture = self.fixture()
        self.assert_resolver_refusal(fixture, "d165_closeout_driver_manifest_unreadable",
                                     manifest=fixture["root"] / "absent.json")
        for raw in (b"not JSON", b"[]", b"{} {}", b"\xff", b'{"x":NaN}', b'{"x":1,"x":2}'):
            with self.subTest(raw=raw), replaced_bytes(fixture["manifest_path"], raw):
                self.assert_resolver_refusal(fixture, "d165_closeout_driver_manifest_unreadable")
        link = fixture["root"] / "linked-manifest.json"
        link.symlink_to(fixture["manifest_path"])
        self.assert_resolver_refusal(fixture, "d165_closeout_driver_manifest_unreadable", manifest=link)
        link.unlink()
        self.assert_resolver_refusal(fixture, "d165_closeout_driver_manifest_unreadable", manifest=fixture["root"])
        status, record, _ = self.main_run(fixture, manifest=fixture["root"] / "absent.json")
        self.assertEqual(status, 2)
        self.assertEqual(record["outputs"], [])
        self.assertFalse((fixture["root"] / "d165-closeout-None.step.json").exists())

    def test_r7_changed_bundle_rejected_by_finalized_custody_replay(self):
        """Summary changed one byte after finalization -> resolve c validator -> manifest_invalid (M10)."""
        fixture = self.fixture()
        summary = next(fixture["runs_root"].glob("*/summary_metrics.json"))
        raw = summary.read_bytes()
        self.assertTrue(raw.endswith(b"\n"))
        with replaced_bytes(summary, raw[:-1] + b" "):
            self.assert_resolver_refusal(fixture, "d165_closeout_driver_manifest_invalid")

    def test_r8_paper_gate_refusal_writes_no_registered_output(self):
        """Paper validator returns d165_paper_floor_artifact_invalid -> run d -> tooling (M11)."""
        fixture = self.fixture()
        sources = self.sources(fixture)
        for result in (("d165_paper_floor_artifact_invalid",), [], None):
            with self.subTest(result=result), mock.patch.object(core, "validate_d165_paper_sources", return_value=result):
                output = self.output(fixture)
                self.assertEqual(driver.run_closeout(sources, output=output), 2)
                record = json.loads(output.with_suffix(".step.json").read_bytes())
                self.assertEqual(record["refusal"], "d165_closeout_driver_paper_sources_invalid")
                self.assert_no_outputs(output)

    def test_r8_paper_gate_refusal_on_outcome_arm(self):
        """Zero denominator -> run d's exit-3 arm still requires exactly ()."""
        fixture = self.fixture("zero")
        sources = self.sources(fixture)
        for result in (("d165_paper_floor_artifact_invalid",), [], None):
            with self.subTest(result=result), mock.patch.object(core, "validate_d165_paper_sources", return_value=result):
                output = self.output(fixture)
                self.assertEqual(driver.run_closeout(sources, output=output), 2)
                record = json.loads(output.with_suffix(".step.json").read_bytes())
                self.assertEqual(record["refusal"], "d165_closeout_driver_paper_sources_invalid")
                self.assert_no_outputs(output)

    def test_n4_manifest_validator_accepts_only_empty_tuple(self):
        """Falsey non-tuples -> resolve c -> manifest_invalid; () alone accepts."""
        fixture = self.fixture()
        for result in (None, [], 0, "", ("x",)):
            with self.subTest(result=result), mock.patch.object(
                driver.analysis_manifest_v3, "validate_finalized_analysis_manifest_v3", return_value=result
            ):
                self.assert_resolver_refusal(fixture, "d165_closeout_driver_manifest_invalid")
        with mock.patch.object(driver.analysis_manifest_v3, "validate_finalized_analysis_manifest_v3", return_value=()):
            sources = self.sources(fixture)
        self.assertEqual((sources.manifest_bytes, sources.floor_bytes, sources.sidecar_bytes), fixture["cached_bytes"])

    def test_s2_mixed_refusals_rejected_before_paper_gate(self):
        """Zero first, later comparative fault -> run classification -> blind exit 2."""
        fixture = self.fixture("zero")
        closeout = build_d165_dominance_closeout(*fixture["cached_bytes"])
        self.assertEqual(closeout["refusal_reason"], "dominance_ratio_zero_denominator")
        for code, status_word, refusal in (
            ("common_mode_replay_window_domain_invalid", "unclassified_refusal", "unclassified refusal at step 6"),
            ("floor_member_census_mismatch", "tooling_refusal", "floor_member_census_mismatch"),
        ):
            mixed = copy.deepcopy(closeout)
            mixed["comparative_common_mode_ratios"][0].update(status="refused", refusal_reason=code)
            with self.subTest(code=code), \
                 mock.patch.object(driver, "build_d165_dominance_closeout", return_value=mixed), \
                 mock.patch.object(core, "validate_d165_paper_sources", wraps=core.validate_d165_paper_sources) as paper:
                output = self.output(fixture)
                status, record, stdout = self.main_run(fixture, output)
                self.assertEqual(status, 2)
                self.assertEqual(record["status"], status_word)
                self.assertEqual(record["refusal"], refusal)
                if status_word == "unclassified_refusal":
                    self.assertNotIn(code, stdout)
                self.assert_no_outputs(output)
                paper.assert_not_called()

    def test_s2_classification_checks_both_record_orders(self):
        """Review's two orders -> pure classifier -> same closed unclassified code."""
        zero = {"status": "refused", "refusal_reason": "dominance_ratio_zero_denominator"}
        unclassified = {"status": "refused", "refusal_reason": "common_mode_replay_window_domain_invalid"}
        complete = {"status": "complete", "refusal_reason": None, "passes": True}
        for independent, comparative in (([zero, complete], [unclassified]), ([unclassified, zero], [complete])):
            closeout = dict(core._expected_global_fields(independent, comparative, []),
                            independent_ratios=independent, comparative_common_mode_ratios=comparative)
            with self.subTest(independent=independent):
                self.assertEqual(driver._closeout_refusal_code(closeout), unclassified["refusal_reason"])
        # The first non-outcome refusal wins, independent before comparative;
        # unknown text uses the builder exception path's closed-code fallback.
        for reason in ("floor_member_census_mismatch", "synthetic unknown refusal"):
            closeout = {"refusal_reason": zero["refusal_reason"],
                        "independent_ratios": [zero, dict(status="refused", refusal_reason=reason)],
                        "comparative_common_mode_ratios": [unclassified]}
            with self.subTest(reason=reason):
                self.assertEqual(driver._closeout_refusal_code(closeout), core._closed_refusal_code(reason))
        closeout["refusal_reason"] = "floor_member_census_mismatch"
        self.assertEqual(driver._closeout_refusal_code(closeout), "floor_member_census_mismatch")

    def test_s2_malformed_ratio_lists_rejected_before_paper_gate(self):
        """Non-list or non-mapping records -> pure classifier/run -> malformed, exit 2."""
        fixture = self.fixture("zero")
        closeout = build_d165_dominance_closeout(*fixture["cached_bytes"])
        for field in ("independent_ratios", "comparative_common_mode_ratios"):
            for malformed in (None, {}, (), "records", [None], ["record"]):
                mixed = copy.deepcopy(closeout)
                mixed[field] = malformed
                with self.subTest(field=field, malformed=malformed), \
                     mock.patch.object(driver, "build_d165_dominance_closeout", return_value=mixed), \
                     mock.patch.object(core, "validate_d165_paper_sources", wraps=core.validate_d165_paper_sources) as paper:
                    self.assertEqual(driver._closeout_refusal_code(mixed), "closeout_input_malformed")
                    output = self.output(fixture)
                    status, record, _ = self.main_run(fixture, output)
                    self.assertEqual(status, 2)
                    self.assertEqual(record["refusal"], "closeout_input_malformed")
                    self.assert_no_outputs(output)
                    paper.assert_not_called()

    def test_r9_append_only_pair_preflight_and_idempotence(self):
        """Other closeout/table bytes -> run e pair preflight -> output_conflict (M12)."""
        fixture = self.fixture()
        sources = self.sources(fixture)
        output = self.output(fixture)
        self.assertEqual(driver.run_closeout(sources, output=output), 0)
        paths = [output, output.with_suffix(".ratio-table.json"), output.with_suffix(".step.json")]
        before = [(path.read_bytes(), path.stat().st_ino, path.stat().st_mtime_ns) for path in paths]
        self.assertEqual(driver.run_closeout(sources, output=output), 0)
        after = [(path.read_bytes(), path.stat().st_ino, path.stat().st_mtime_ns) for path in paths]
        self.assertEqual(before[:2], after[:2])
        self.assertEqual(before[2][0], after[2][0])
        for suffix in (".json", ".ratio-table.json"):
            with self.subTest(suffix=suffix):
                conflict_output = self.output(fixture)
                conflict = conflict_output.with_suffix(suffix)
                conflict.write_bytes(b"occupied-7331\n")
                self.assertEqual(driver.run_closeout(sources, output=conflict_output), 2)
                self.assertEqual(conflict.read_bytes(), b"occupied-7331\n")
                peer = conflict_output.with_suffix(".ratio-table.json" if suffix == ".json" else ".json")
                self.assertFalse(peer.exists())
                record = json.loads(conflict_output.with_suffix(".step.json").read_bytes())
                self.assertEqual(record["refusal"], "d165_closeout_driver_output_conflict")
                self.assertEqual(record["outputs"], [])

    def test_r9_output_symlinks_directories_and_atomic_step_replacement(self):
        fixture = self.fixture()
        sources = self.sources(fixture)
        target = self.output(fixture)
        target.write_bytes(b"untouched-7331")
        for suffix in (".json", ".ratio-table.json"):
            for kind in ("symlink", "dangling", "directory"):
                output = self.output(fixture)
                occupied = output.with_suffix(suffix)
                if kind == "directory":
                    occupied.mkdir()
                else:
                    occupied.symlink_to(target if kind == "symlink" else target.parent / "absent")
                self.assertEqual(driver.run_closeout(sources, output=output), 2)
                self.assertEqual(target.read_bytes(), b"untouched-7331")
                self.assertTrue(occupied.is_dir() if kind == "directory" else occupied.is_symlink())
                peer = output.with_suffix(".ratio-table.json" if suffix == ".json" else ".json")
                self.assertFalse(peer.exists())
        output = self.output(fixture)
        output.with_suffix(".step.json").symlink_to(target)
        self.assertEqual(driver.run_closeout(sources, output=output), 0)
        self.assertFalse(output.with_suffix(".step.json").is_symlink())
        self.assertEqual(target.read_bytes(), b"untouched-7331")

    def test_r10_unclassified_and_malformed_builder_exceptions_are_blind(self):
        """Unlisted science code / arbitrary text -> run a,c; RuntimeError -> main blind exit 2 (M13)."""
        fixture = self.fixture()
        for exception, status_word, refusal in (
            (ValueError("point_floor_parent_nonfinite_or_negative"), "unclassified_refusal", "unclassified refusal at step 6"),
            (ValueError("floor_artifact.cells['x'].absolute: missing component"), "tooling_refusal",
             "closeout_input_malformed: source.census_or_block_membership"),
            (TypeError("7331 malformed source"), "tooling_refusal", "closeout_input_malformed: source.census_or_block_membership"),
            (RuntimeError("7331"), "unclassified_refusal", "unclassified refusal at step 6"),
        ):
            with self.subTest(exception=type(exception).__name__), \
                 mock.patch.object(driver, "build_d165_dominance_closeout", side_effect=exception):
                output = self.output(fixture)
                status, record, stdout = self.main_run(fixture, output)
                self.assertEqual(status, 2)
                self.assertEqual(record["status"], status_word)
                self.assertEqual(record["refusal"], refusal)
                self.assertNotIn(str(exception), stdout)
                self.assert_no_outputs(output)
        with mock.patch.object(driver, "resolve_closeout_sources", side_effect=RuntimeError("7331")):
            status, record, stdout = self.main_run(fixture, self.output(fixture))
        self.assertEqual(status, 2)
        self.assertEqual(record["status"], "unclassified_refusal")
        self.assertNotIn("7331", stdout)

    def test_r9_status_write_failure_rolls_back_only_new_registered_files(self):
        """Step-write OSError after pair issuance -> main unclassified 2, no new registered files."""
        fixture = self.fixture()
        sources = self.sources(fixture)
        for existing in (False, True):
            with self.subTest(existing=existing):
                output = self.output(fixture)
                if existing:
                    self.assertEqual(driver.run_closeout(sources, output=output), 0)
                    before = (output.read_bytes(), output.with_suffix(".ratio-table.json").read_bytes())
                stdout, stderr = io.StringIO(), io.StringIO()
                with mock.patch.object(driver, "_replace_step", side_effect=OSError("7331")), \
                     redirect_stdout(stdout), redirect_stderr(stderr):
                    status = driver.main(["--finalized-manifest", str(fixture["manifest_path"]),
                                          "--custody-root", str(fixture["root"]), "--output", str(output)])
                self.assertEqual(status, 2)
                self.assertEqual(stderr.getvalue(), "")
                self.assertEqual(len(stdout.getvalue().splitlines()), 1)
                record = json.loads(stdout.getvalue())
                self.assertEqual(record["status"], "unclassified_refusal")
                self.assertEqual(record["outputs"], [])
                self.assertIsNone(record["schema_valid"])
                self.assertNotIn("7331", stdout.getvalue())
                if existing:
                    self.assertEqual((output.read_bytes(), output.with_suffix(".ratio-table.json").read_bytes()), before)
                else:
                    self.assert_no_outputs(output)

    def test_r11_classification_is_total_closed_and_literal(self):
        remaining = {
            "dominance_ratio_nonfinite_or_negative_denominator", "dominance_ratio_nonfinite_or_negative_numerator",
            "dominance_ratio_nonfinite_result", "point_floor_parent_nonfinite_or_negative",
            "common_mode_replay_zero_point_divergence_out_of_domain", "common_mode_replay_window_domain_invalid",
            "common_mode_replay_authenticated_operative_bound_invalid", "common_mode_replay_input_invalid",
            "common_mode_replay_zero_point_membership_invalid", "d165_mint_adapter_input_invalid",
        }
        self.assertEqual(driver.OUTCOME_CLASS_CODES, {"dominance_ratio_zero_denominator"})
        self.assertEqual(len(driver.STRUCTURAL_BUILDER_CODES), 14)
        self.assertFalse(driver.OUTCOME_CLASS_CODES & driver.STRUCTURAL_BUILDER_CODES)
        self.assertLessEqual(driver.OUTCOME_CLASS_CODES | driver.STRUCTURAL_BUILDER_CODES, core.D165_CLOSEOUT_REFUSAL_CODES)
        self.assertEqual(core.D165_CLOSEOUT_REFUSAL_CODES - driver.OUTCOME_CLASS_CODES - driver.STRUCTURAL_BUILDER_CODES, remaining)
        self.assertEqual(driver.DRIVER_REFUSAL_CODES, {
            "d165_closeout_driver_manifest_unreadable", "d165_closeout_driver_manifest_not_finalized",
            "d165_closeout_driver_manifest_invalid", "d165_closeout_driver_attachment_unreadable",
            "d165_closeout_driver_paper_sources_invalid", "d165_closeout_driver_output_conflict",
        })
        self.assertFalse(driver.DRIVER_REFUSAL_CODES & core.D165_CLOSEOUT_REFUSAL_CODES)
        self.assertEqual(driver.TOOLING_REFUSAL_CODES, driver.DRIVER_REFUSAL_CODES | driver.STRUCTURAL_BUILDER_CODES)
        for code in core.D165_CLOSEOUT_REFUSAL_CODES | driver.DRIVER_REFUSAL_CODES:
            self.assertEqual(driver._exit_for(code), 3 if code in driver.OUTCOME_CLASS_CODES else 2)
            record = driver._step_record(driver._exit_for(code), code)
            self.assertEqual(record["status"], "outcome_class" if code in driver.OUTCOME_CLASS_CODES else
                             "tooling_refusal" if code in driver.TOOLING_REFUSAL_CODES else "unclassified_refusal")

    def test_r12_parser_has_no_caller_chosen_floor_or_sidecar(self):
        options = {option for action in driver._parser()._actions for option in action.option_strings}
        self.assertEqual(options, {"-h", "--help", "--finalized-manifest", "--custody-root", "--output"})

    def test_resolver_location_identity_and_frozen_sources(self):
        fixture = self.fixture()
        sources = self.sources(fixture)
        self.assertEqual(sources.manifest_relative_path, fixture["manifest_path"].name)
        self.assertEqual(sources.floor_relative_path, fixture["manifest"]["evidence"]["aggregate_floor_artifact"]["path"])
        self.assertEqual(sources.sidecar_relative_path, fixture["manifest"]["evidence"]["dominance_replay_sidecar"]["path"])
        self.assertEqual(driver.default_output_path(sources), fixture["root"] / f"d165-closeout-{sources.manifest_id}.json")
        with self.assertRaises(FrozenInstanceError):
            sources.manifest_id = "changed"
        for identity in ("", "../7331", "id/part", None, True):
            manifest = copy.deepcopy(fixture["manifest"])
            manifest["manifest_id"] = identity
            with self.subTest(identity=identity), replaced_bytes(fixture["manifest_path"], _file_json_bytes(manifest)):
                self.assert_resolver_refusal(fixture, "d165_closeout_driver_manifest_invalid")
        outside = self.output(fixture)
        outside.write_bytes(fixture["manifest_path"].read_bytes())
        narrow_root = outside.parent / "custody"
        narrow_root.mkdir()
        with self.assertRaises(driver.CloseoutDriverRefusal) as refused:
            driver.resolve_closeout_sources(outside, narrow_root)
        self.assertEqual(refused.exception.code, "d165_closeout_driver_manifest_invalid")

    def test_main_default_output_and_usage_errors_are_one_blind_line(self):
        fixture = self.fixture()
        default = driver.default_output_path(self.sources(fixture))
        with mock.patch.object(driver, "_replace_step", wraps=driver._replace_step) as status_writer:
            status, record, stdout = self.main_run(fixture)
        status_writer.assert_called_once()
        self.assertEqual(status, 0)
        self.assertEqual(default.with_suffix(".step.json").read_bytes(), stdout.encode())
        self.assertTrue(default.exists())
        for argv in ([], ["--help"], ["--floor-artifact", "7331"],
                     ["--finalized-manifest", str(fixture["manifest_path"]), "--custody-root", str(fixture["root"]),
                      "--output", str(fixture["root"].parent / "outside-7331.json")]):
            stdout, stderr = io.StringIO(), io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                status = driver.main(argv)
            self.assertEqual(status, 2)
            self.assertEqual(stderr.getvalue(), "")
            self.assertEqual(len(stdout.getvalue().splitlines()), 1)
            self.assertEqual(json.loads(stdout.getvalue())["status"], "unclassified_refusal")
            self.assertNotIn("7331", stdout.getvalue())


class WindowIndexHandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = finalized_fixture()
        from tests.b5_analysis import fixtures_s5
        from tests.b5_analysis import test_finalization_block5
        with fixtures_s5.finalization_case() as block5:
            manifest, _path = test_finalization_block5.RoleAttachmentTests().build(block5)
            cls.role = copy.deepcopy(manifest['evidence']['analysed_attempt_exclusions'])
            cls.built = block5['block5_inputs']

    def block5_manifest(self):
        value = copy.deepcopy(self.fixture['manifest'])
        value['evidence']['analysed_attempt_exclusions'] = self.role
        value['manifest_id'] = manifests.calculate_manifest_id(value)
        tmp = tempfile.TemporaryDirectory(prefix='s10-index-', dir=self.fixture['root'])
        self.addCleanup(tmp.cleanup)
        path = Path(tmp.name)/'manifest.json'
        path.write_bytes(_file_json_bytes(value))
        return path

    def invoke(self, path, *, window_index=None):
        out = path.parent/'closeout.json'
        args = ['--finalized-manifest',str(path),'--custody-root',str(self.fixture['root']),
                '--output',str(out)]
        if window_index is not None:args += ['--window-index',str(window_index)]
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = driver.main(args)
        self.assertEqual(stderr.getvalue(),'')
        return status, json.loads(stdout.getvalue()), out

    def test_P2_without_window_index_keeps_manifest_refusal(self):
        status, record, out = self.invoke(self.block5_manifest())
        self.assertEqual(status,2)
        self.assertEqual(record['refusal'],'d165_closeout_driver_manifest_invalid')
        self.assertFalse(out.exists())

    def test_P2_index_reaches_both_finalized_validator_sites(self):
        index = self.fixture['root']/'synthetic-window-index.json'
        # S10: on the block-5 path the paper-source replay authenticates the floor
        # against the pinset beside it, as the claim gate does; this fixture's
        # legacy floor has none, so that loader is observed and answered here.
        from types import SimpleNamespace
        sibling = mock.Mock(side_effect=lambda path, *, require_sibling_pinset=False:
                            SimpleNamespace(file_sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest()))
        with mock.patch.object(driver,'block5_claim_gate_inputs',return_value=self.built) as builder, \
             mock.patch.object(manifests,'validate_finalized_analysis_manifest_v3',return_value=()) as first, \
             mock.patch.object(core,'validate_finalized_analysis_manifest_v3',return_value=()) as second, \
             mock.patch.object(core,'load_floor_artifact',sibling):
            status, record, out = self.invoke(self.block5_manifest(), window_index=index)
        self.assertEqual((status, record['status']),(0,'ok'), record)
        self.assertTrue(out.exists())
        first.assert_called_once(); second.assert_called_once()
        sibling.assert_called_once()
        self.assertIs(sibling.call_args.kwargs.get('require_sibling_pinset'),True)
        self.assertEqual(first.call_args.kwargs.get('window_index'),index)
        self.assertIs(first.call_args.kwargs.get('_block5_inputs'),self.built)
        builder.assert_called_once()
        self.assertEqual(second.call_args.kwargs.get('window_index'),index)

    def test_P2_custody_gate_passes_its_tracked_index(self):
        from types import SimpleNamespace
        from joulewise import paper_custody as custody
        binding = custody._BoundFile('runs_root',Path('manifest.json'),'0'*64,
                                      custody.InputRole.FINALIZED_MANIFEST,'generated')
        ctx = SimpleNamespace(sources=(binding,),repository=self.fixture['root'],
            runs_root=self.fixture['root'],raws={custody.InputRole.FINALIZED_MANIFEST:
                _file_json_bytes({'evidence':{'analysed_attempt_exclusions':self.role}}),
                custody.InputRole.D165_CLOSEOUT:b'{}',custody.InputRole.FLOOR_ARTIFACT:b'{}',
                custody.InputRole.REPLAY_SIDECAR:b'{}'})
        index = self.fixture['root']/'tracked-index.json'
        with mock.patch.object(custody,'_tracked_window_index',return_value=index) as tracked, \
             mock.patch.object(core,'validate_d165_paper_sources',return_value=('synthetic_refusal',)) as replay:
            self.assertFalse(custody._d165_issuance_gate(ctx).authentic)
        tracked.assert_called_once_with(ctx)
        self.assertEqual(replay.call_args.kwargs.get('window_index'),index)


class Block5PredicateTests(unittest.TestCase):
    def test_d165_custody_gate_uses_every_block5_role_and_keeps_legacy_behavior(self):
        from types import SimpleNamespace
        from joulewise import paper_custody as custody
        root=Path('synthetic-custody')
        binding=custody._BoundFile('runs_root',Path('manifest.json'),'0'*64,
                                  custody.InputRole.FINALIZED_MANIFEST,'generated')
        for role in (*sorted(manifests._BLOCK5_ROLES),None):
            evidence={} if role is None else {role:{}}
            ctx=SimpleNamespace(sources=(binding,),repository=root,runs_root=root,
                raws={custody.InputRole.FINALIZED_MANIFEST:_file_json_bytes({'evidence':evidence}),
                      custody.InputRole.D165_CLOSEOUT:b'{}',custody.InputRole.FLOOR_ARTIFACT:b'{}',
                      custody.InputRole.REPLAY_SIDECAR:b'{}'})
            index=root/'tracked-index.json'
            with self.subTest(role=role),mock.patch.object(custody,'_tracked_window_index',return_value=index) as tracked, \
                 mock.patch.object(core,'validate_d165_paper_sources',return_value=('synthetic_refusal',)) as replay:
                self.assertFalse(custody._d165_issuance_gate(ctx).authentic)
                if role is None:
                    tracked.assert_not_called()
                    self.assertNotIn('window_index',replay.call_args.kwargs)
                else:
                    tracked.assert_called_once_with(ctx)
                    self.assertEqual(replay.call_args.kwargs['window_index'],index)


if __name__ == "__main__":
    unittest.main()
