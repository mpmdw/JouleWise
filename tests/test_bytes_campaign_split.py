"""Exercise the pending ALIGN patch with synthetic campaign replies only.

The source snapshot is CampaignWordRates from ALIGN 9c40e4e5d, not a second
implementation of its aggregate assertions. No BYTES runtime is imported.
"""
from contextlib import redirect_stdout
import copy
import io
import json
import math
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock

from tests.git_fixture import init_git_fixture

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/ci"
PATCH = ROOT / "docs/perf/2026-11-08-bytes-world-split.patch"
DESIGN = json.loads((FIXTURES / "bytes_campaign_design.json").read_text())
sys.path.insert(0, str(ROOT / "scripts"))
import shard_tests


def patched_inputs():
    """Apply the actual handoff patch, including its timing declaration."""
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        init_git_fixture(root, "-q")
        source = root / "tests/test_bytes_analysis.py"
        source.parent.mkdir()
        # The actual class sits deep in a larger module. A patch that only
        # applies when the class starts the file is not a usable ALIGN patch.
        source.write_text(
            "# Other tests precede this class.\n" * 5
            + (FIXTURES / "bytes_campaign_word_rates.py.txt").read_text()
            + "# Other tests follow this class.\n"
        )
        timings = root / "scripts/test_timings.json"
        timings.parent.mkdir()
        timings.write_bytes((ROOT / "scripts/test_timings.json").read_bytes())
        subprocess.run(
            ("git", "apply", str(PATCH)), cwd=root, check=True,
            capture_output=True, text=True,
        )
        return source.read_text(), shard_tests.load_split_declarations(timings)


class CampaignReplies:
    BOUNDARIES = ("rails", "rest", "DC input")
    HYPOTHESES = ("bytes", "time", "resident")
    H2_INTERVALS = {"rails": 2, "rest": 4, "DC input": 4}

    def __init__(self, *, missing_word=False, unavailable=False):
        self.archives = {}
        self.calls = []
        self.missing_word = missing_word
        self.unavailable = unavailable

    def archive_campaign(self, root, *, world, seed, **kwargs):
        assert kwargs == {
            "pass_duration_scales": DESIGN["main_campaign"]["pass_duration_scales"],
            "clock_latency_ms": DESIGN["main_campaign"]["clock_latency_ms"],
            "release": "none",
        }
        self.archives[root] = {"world": world, "seed": seed}
        return self.archives[root]

    def cli_stage_chain(self, root, manifest):
        self.calls.append((manifest["world"], manifest["seed"]))

    def load_records(self, path, manifest, *, stage):
        assert stage == "all"
        return manifest

    def student_t_quantile(self, probability, df):
        return 1.96

    def read_json(self, path):
        if path.name == "campaign_design.json":
            return copy.deepcopy(DESIGN)
        seed = self.archives[path.parent.parent]["seed"]
        if path.name == "unavailable.json":
            return ["synthetic refusal"] if self.unavailable else []
        if path.name == "h1.json":
            return [
                {"selection": "primary", "basis": "gross primary", "role": "heldout",
                 "pass_id": "mean", "boundary": boundary, "model": model["model"],
                 "word": self.HYPOTHESES[seed % 3]}
                for boundary in self.BOUNDARIES for model in DESIGN["models"]
                if model["role"] == "heldout" and not self.missing_word
            ]
        assert path.name == "h2.json"
        fitted = {
            "df": 8, "coefficients": [0, seed / 1e6],
            "standard_errors": [0, .02], "ols_standard_errors": [0, .03],
            "intervals": [[0, 0], [-.1, .1]],
            "ols_intervals": [[0, 0], [-.2, .2]],
            "coefficient_C": [0, .04],
            "offset_intervals": [[0, 0], [-.14, .14]],
            "offset_ols_intervals": [[0, 0], [-.24, .24]],
        }
        return [
            {"selection": "primary", "basis": "gross primary", "boundary": boundary,
             "two_term": fitted, "resident_extended": fitted}
            for boundary in self.BOUNDARIES
        ]


def campaign_case(source, replies):
    module = types.ModuleType("test_bytes_analysis")
    module.__dict__.update(
        NumericTestCase=unittest.TestCase, ba=replies, FIXTURES=FIXTURES,
        statistics=statistics, math=math, tempfile=tempfile, Path=Path, json=json,
        archive_campaign=replies.archive_campaign, cli_stage_chain=replies.cli_stage_chain,
        assert_d3_exercised=lambda test, records, manifest: {
            "rest_cells": 120, "min_gap_over_B": 2 + manifest["seed"] / 1e6,
            "min_agreement_bars": 3 + manifest["seed"] / 1e6,
        },
    )
    exec(compile(source, "<synthetic CampaignWordRates>", "exec"), module.__dict__)
    return module


def run_campaigns(module):
    result = unittest.TestResult()
    output = io.StringIO()
    with redirect_stdout(output):
        unittest.defaultTestLoader.loadTestsFromModule(module).run(result)
    reports = []
    for line in output.getvalue().splitlines():
        if line.startswith("BYTES_SIMULATION_REPORT="):
            reports.extend(json.loads(line.split("=", 1)[1]))
    # Different runners may emit worlds in different orders; each world's
    # serialized report must still equal its original report byte for byte.
    canonical = json.dumps(sorted(reports, key=lambda row: row["world"]), sort_keys=True)
    return result, canonical


class BytesCampaignSplitTests(unittest.TestCase):
    def test_all_sixty_campaigns_and_aggregate_report_bytes_match_original(self):
        source, _ = patched_inputs()
        original = (FIXTURES / "bytes_campaign_word_rates.py.txt").read_text()
        before, after = CampaignReplies(), CampaignReplies()
        old_result, old_report = run_campaigns(campaign_case(original, before))
        new_result, new_report = run_campaigns(campaign_case(source, after))
        self.assertEqual((old_result.testsRun, new_result.testsRun), (1, 3))
        self.assertTrue(old_result.wasSuccessful(), old_result.errors + old_result.failures)
        self.assertTrue(new_result.wasSuccessful(), new_result.errors + new_result.failures)
        expected = [(world, seed) for world, seeds in DESIGN["seeds"].items() for seed in seeds]
        self.assertEqual(len(expected), 60)
        self.assertCountEqual(before.calls, expected)
        self.assertCountEqual(after.calls, expected)
        for world in DESIGN["seeds"]:
            self.assertEqual([seed for w, seed in after.calls if w == world], DESIGN["seeds"][world])
        self.assertEqual(new_report.encode(), old_report.encode())

    def test_each_world_keeps_unavailable_and_missing_word_assertions(self):
        source, _ = patched_inputs()
        for defect in ("unavailable", "missing_word"):
            with self.subTest(defect=defect):
                replies = CampaignReplies(**{defect: True})
                result, _ = run_campaigns(campaign_case(source, replies))
                self.assertEqual(result.testsRun, 3)
                self.assertEqual(len(result.failures), 3)
                self.assertEqual(result.errors, [])

    def test_timing_patch_schedules_the_three_worlds_exactly_once(self):
        source, splits = patched_inputs()
        module = campaign_case(source, CampaignReplies())
        canonical = "tests.test_bytes_analysis"
        split = splits[canonical]
        self.assertIsNone(split["awaiting_lane"])
        with mock.patch.dict(sys.modules, {module.__name__: module}):
            ids = shard_tests.discover_test_ids(canonical)
            self.assertEqual(set(split["declared"]), ids)
            self.assertEqual(len(ids), 3)
            units, weights = shard_tests.expand_units(
                (canonical,), {canonical: 9121.794}, {canonical: split}, unknown_weight=26.98,
            )
            partitions = shard_tests.partition_modules(units, weights, 3)
            resolved = [
                test for partition in partitions
                for test in shard_tests.resolve_units_to_test_ids(canonical, partition, ids, split["declared"])
            ]
            self.assertCountEqual(resolved, ids)

    def test_new_worlds_and_fewer_than_twenty_seeds_fail_closed(self):
        source, _ = patched_inputs()
        with mock.patch.dict(DESIGN["seeds"], {"unexpected": [9999]}):
            result, _ = run_campaigns(campaign_case(source, CampaignReplies()))
            self.assertEqual(len(result.failures), 3)
        with mock.patch.dict(DESIGN["seeds"], {"bytes": DESIGN["seeds"]["bytes"][:-1]}):
            result, _ = run_campaigns(campaign_case(source, CampaignReplies()))
            self.assertEqual(len(result.failures), 1)
            self.assertEqual(result.errors, [])


if __name__ == "__main__":
    unittest.main()
