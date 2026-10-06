"""Block-5 window sizing: ``scripts/size_b5_window.py`` and the draft it writes.

The sizer turns block 4's committed sizing source and the three ``_v5`` packs'
stage graphs into the programmed span, T_stream_max and window maximum of each
block-5 window. These tests check its arithmetic against block 4's committed
totals and an independent hand formula, that the block-5 plan writer accepts
its allowances, and that the clock gate check reports a stream that is too long.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import math
import shutil
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path
from typing import Any

from joulewise.b5 import plan as b5_plan
from joulewise.hazards import clock as clock_hazard

ROOT = Path(__file__).resolve().parents[1]
DRAFT = "configs/campaigns/v5_claim_25g83/sizing_b5.json"
SOURCE = ROOT / "configs/campaigns/v5_qualification_25g83/sizing_sources/sizing_source_v2.json"
COPIED = ("configs/campaigns/d117_floor_qwen3-1p7b_v5", "configs/campaigns/d117_floor_qwen3-8b_v5",
          "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5", "configs/campaigns/neg8_reference_corpus_v5",
          "configs/campaigns/window_references_v5", "configs/campaigns/v5_qualification_25g83")


def load_script() -> Any:
    spec = importlib.util.spec_from_file_location("size_b5_window_under_test", ROOT / "scripts/size_b5_window.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


S = load_script()


def hand_span(source: dict[str, Any], small: int, large: int, stages: int = 10) -> int:
    """Block 5's programmed span written out term by term from the source's numbers."""

    member = {klass: sum(source["members"][klass].values()) for klass in ("small", "large")}
    members = small + large
    return ((1 + stages) * 60 + stages * 20                       # chain settles (60 s), campaign arm countdowns
            + source["fixed"]["pre_post_calibration"]             # 770
            + source["auxiliary"]["gamma-bound-derivation"]       # 60
            + small * member["small"] + large * member["large"]   # 595, 619 per member
            + stages * 180 + members * 45 + 2 * 240 + 300 + 120   # stage custody (block 4's labelled terms)
            + members * (15 + 17)                                 # native sampler start and wind-down
            + source["fixed"]["terminal_shutdown"])               # 300


class SizesOfTheCommittedPacks(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = S.derive_document(ROOT, S.DEFAULT_PACKS)
        cls.source = json.loads(SOURCE.read_bytes())

    def test_block4_committed_totals_are_reproduced_by_the_same_arithmetic(self) -> None:
        reproduction = self.document["block4_reproduction"]
        self.assertTrue(reproduction["reproduced"])
        self.assertEqual(22494, reproduction["breakdown"]["programmed_span_s"])
        self.assertEqual(3571, reproduction["breakdown"]["stage_custody_s"])
        self.assertEqual(25800, reproduction["window_max_s"])
        self.assertEqual({"large": 2, "small": 21}, reproduction["members_by_class"])

    def test_each_pack_matches_the_hand_formula(self) -> None:
        expected = {"ALPHA": (119, 0, 100, 19, 314), "BETA": (19, 100, 100, 19, 335), "GAMMA": (61, 40, 80, 21, 335)}
        for label, (small, large, science, auxiliary, longest) in expected.items():
            pack = self.document["packs"][label]
            with self.subTest(label):
                self.assertEqual({key: value for key, value in (("small", small), ("large", large)) if value},
                                 pack["members_by_class"])
                self.assertEqual((science, auxiliary, 10), (pack["science_members"], pack["auxiliary_members"],
                                                            pack["collection_stages"]))
                self.assertEqual(hand_span(self.source, small, large), pack["programmed_span_s"])
                self.assertEqual(60 * math.ceil((pack["programmed_span_s"] + 3300) / 60), pack["window_max_s"])
                self.assertEqual(longest, pack["pack_longest_stream_s"])
                self.assertEqual(335, pack["T_stream_max_s"])
        self.assertEqual((84658, 87058, 73522), tuple(self.document["packs"][label]["programmed_span_s"]
                                                      for label in ("ALPHA", "BETA", "GAMMA")))
        self.assertEqual((87960, 90360, 76860), tuple(self.document["packs"][label]["window_max_s"]
                                                      for label in ("ALPHA", "BETA", "GAMMA")))
        self.assertEqual(60, self.document["terms"]["settle_s"]["seconds"])

    def test_block4_configs_superseded_by_the_timing_regeneration_are_listed(self) -> None:
        # The 2026-10-06 timing ruling regenerated the _v5 packs (idle_seconds 57.6), so the
        # four block-4 science configs no longer hash to block 4's recorded digests; the
        # sizer reads them at the bytes the GAMMA plan tree records and says so.
        self.assertEqual([f"d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b01-{slot}"
                          for slot in ("a1", "a2", "b1", "b2")],
                         self.document["class_map"]["superseded_block4_configs"])
        self.assertEqual({"/Users/edr/jw_models/mlx-community/Qwen3-1.7B-4bit": "small",
                          "/Users/edr/jw_models/mlx-community/Qwen3-8B-4bit": "large"},
                         self.document["class_map"]["model_source"])

    def test_the_clock_gate_still_allows_3_6_ppm(self) -> None:
        limit = float((Fraction(5) - Fraction("3.7")) * 1000 / (Fraction("3.6") + Fraction("0.25")))
        self.assertAlmostEqual(limit, self.document["clock_gate"]["stream_limit_s"])
        for label, pack in self.document["packs"].items():
            with self.subTest(label):
                gate = pack["clock_gate"]["at_T_stream_max"]
                self.assertTrue(gate["passes_at_required"])
                self.assertAlmostEqual(1300 / 335 - 0.25, gate["max_abs_frequency_ppm"])
                self.assertTrue(pack["clock_gate"]["pack_longest_stream_within_limit"])

    def test_the_plan_writer_accepts_the_allowances_and_derives_the_same_window(self) -> None:
        raw = S.render(self.document)
        digest = S.sha256_bytes(raw)
        with tempfile.TemporaryDirectory() as tmp:
            measurement = Path(tmp)
            (measurement / DRAFT).parent.mkdir(parents=True)
            (measurement / DRAFT).write_bytes(raw)
            for label, values in S.allowances(self.document, DRAFT, digest).items():
                pack = self.document["packs"][label]
                with self.subTest(label):
                    span, _record = b5_plan.read_allowance(values["programmed_span_s"], "programmed_span_s",
                                                           measurement=measurement)
                    stream, _record = b5_plan.read_allowance(values["T_stream_max_s"], "T_stream_max_s",
                                                             measurement=measurement)
                    self.assertEqual((pack["programmed_span_s"], pack["T_stream_max_s"]), (span, stream))
                    self.assertEqual(pack["window_max_s"],
                                     60 * math.ceil((math.ceil(span) + b5_plan.T0_STAGE_CAP_S) / 60))
        self.assertEqual(b5_plan.T0_STAGE_CAP_S, self.document["terms"]["t0_stage_cap"]["seconds"])
        self.assertEqual(b5_plan.DWELL_CAP_S, self.document["terms"]["clean_dwell_cap"]["seconds"])
        self.assertEqual(clock_hazard.DEFAULT_THRESHOLDS["t_stream_max_s"], self.document["block"]["T_stream_max_s"])

    def test_the_committed_draft_is_what_the_sizer_writes(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(0, S.main(["--repo", str(ROOT), "--check"]))
        committed = json.loads((ROOT / DRAFT).read_bytes())
        self.assertEqual("UNSEALED_DRAFT", committed["status"])
        self.assertIs(False, committed["sealed"])


class Refusals(unittest.TestCase):
    """A copy of the committed inputs, changed one way at a time."""

    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.repo = Path(directory.name)
        for relative in COPIED:
            shutil.copytree(ROOT / relative, self.repo / relative)
        self.source_path = self.repo / "configs/campaigns/v5_qualification_25g83/sizing_sources/sizing_source_v2.json"
        self.adapter_path = self.repo / S.DEFAULT_ADAPTER

    def rewrite_source(self, change) -> None:
        old = S.sha256_bytes(self.source_path.read_bytes())
        source = json.loads(self.source_path.read_bytes())
        change(source)
        raw = (json.dumps(source, indent=2, sort_keys=True) + "\n").encode()
        self.source_path.write_bytes(raw)
        adapter = self.adapter_path.read_text().replace(old, S.sha256_bytes(raw))
        self.adapter_path.write_text(adapter)
        return json.loads(adapter)

    def test_the_copy_sizes_like_the_checkout(self) -> None:
        self.assertEqual(S.derive_document(ROOT, S.DEFAULT_PACKS)["packs"],
                         S.derive_document(self.repo, S.DEFAULT_PACKS)["packs"])

    def test_a_stream_longer_than_the_clock_limit_is_reported(self) -> None:
        def longer(source: dict[str, Any]) -> None:
            source["streams"]["large"] = 400
            source["totals"]["T_stream_max"] = 400
        self.rewrite_source(longer)
        adapter = json.loads(self.adapter_path.read_bytes())
        for item in adapter["sizing"]["streams"].values():
            if item["source_pointer"] == "/streams/large":
                item["seconds"] = 400
        adapter["totals"]["T_stream_max"]["seconds"] = 400
        self.adapter_path.write_text(json.dumps(adapter, indent=2) + "\n")
        out = "sizing.json"
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(3, S.main(["--repo", str(self.repo), "--out", out]))
        written = json.loads((self.repo / out).read_bytes())
        self.assertEqual(314, written["packs"]["ALPHA"]["pack_longest_stream_s"])
        self.assertTrue(written["packs"]["ALPHA"]["clock_gate"]["pack_longest_stream_within_limit"])
        for label in ("BETA", "GAMMA"):
            self.assertEqual(400, written["packs"][label]["pack_longest_stream_s"])
            self.assertFalse(written["packs"][label]["clock_gate"]["pack_longest_stream_within_limit"])
            self.assertFalse(written["packs"][label]["clock_gate"]["at_T_stream_max"]["passes_at_required"])

    def test_a_changed_custody_formula_refuses(self) -> None:
        def changed(source: dict[str, Any]) -> None:
            source["derivations"]["stage_custody"]["formula"] = source["derivations"]["stage_custody"][
                "formula"].replace("+300 reservation", "+301 reservation")
        self.rewrite_source(changed)
        with self.assertRaisesRegex(S.SizingError, "custody formula evaluates to"):
            S.derive_document(self.repo, S.DEFAULT_PACKS)

    def test_an_adapter_that_disagrees_with_its_source_refuses(self) -> None:
        def changed(source: dict[str, Any]) -> None:
            source["members"]["large"]["cooldown"] = 301
        self.rewrite_source(changed)
        with self.assertRaisesRegex(S.SizingError, "disagrees with the source"):
            S.derive_document(self.repo, S.DEFAULT_PACKS)

    def test_an_order_manifest_that_differs_from_the_plan_tree_refuses(self) -> None:
        manifest = self.repo / "configs/campaigns/d117_floor_qwen3-8b_v5/02_phase_decode_abba_blocks_01_05/order_manifest.json"
        manifest.write_bytes(manifest.read_bytes() + b"\n")
        with self.assertRaisesRegex(S.SizingError, "order manifest .* hashes to"):
            S.derive_document(self.repo, S.DEFAULT_PACKS)

    def test_a_block4_config_recorded_by_no_plan_tree_refuses(self) -> None:
        config = self.repo / ("configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/"
                              "01_decode_contrast_blocks_01_05/"
                              "d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b01-b1.json")
        config.write_bytes(config.read_bytes().replace(b"Qwen3-8B-4bit", b"Qwen3-1.7B-4bit"))
        with self.assertRaisesRegex(S.SizingError, "b01-b1 changed and no block-5 plan tree records"):
            S.derive_document(self.repo, S.DEFAULT_PACKS)

    def test_a_science_config_that_differs_from_its_recorded_digest_refuses(self) -> None:
        config = self.repo / ("configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/"
                              "03_prefill_p2048_contrast_blocks_01_05/"
                              "d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b01-b1.json")
        config.write_bytes(config.read_bytes().replace(b"Qwen3-8B-4bit", b"Qwen3-1.7B-4bit"))
        with self.assertRaisesRegex(S.SizingError, "config .* hashes to"):
            S.derive_document(self.repo, S.DEFAULT_PACKS)


if __name__ == "__main__":
    unittest.main()
