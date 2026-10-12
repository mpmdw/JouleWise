from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest

from joulewise.b5_analysis.archive import open_archive, open_attempt_record
from joulewise.b5_analysis.steps import classify_step4_exit, step_record
from joulewise.b5_analysis.windows import AnalysisRefusal, AnalysedWindow, SealPins
from tests.b5_analysis import fixtures as fx


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="s0-archive-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "archive"
        self.pins = SealPins.load()
        self.entry = fx.structural_archive(self.root)
        self.window = AnalysedWindow.from_record(open_attempt_record(self.entry, seal_pins=self.pins))
        self.handle = open_archive(self.window, seal_pins=self.pins)

    def test_roster_digest_guard(self):
        with (self.root / "derived/roster.json").open("ab") as out:
            out.write(b"x")
        with self.assertRaisesRegex(AnalysisRefusal, "^roster_record_unauthenticated$"):
            self.handle.output_bytes("derived/roster.json")

    def test_archive_rechecks_indexed_harvest(self):
        with (self.root / "harvest.json").open("ab") as out:
            out.write(b" ")
        with self.assertRaisesRegex(AnalysisRefusal, "^harvest_record_not_the_indexed_one$"):
            open_archive(self.window, seal_pins=self.pins)

    def test_unusable_attempt_is_refused(self):
        entry = fx.structural_archive(Path(self.tmp.name) / "unusable", usable=False)
        window = AnalysedWindow.from_record(open_attempt_record(entry, seal_pins=self.pins))
        with self.assertRaisesRegex(AnalysisRefusal, "^attempt_not_claim_usable$"):
            open_archive(window, seal_pins=self.pins)

    def test_analysed_pin3_is_unsupported(self):
        entry = fx.archived_entry("pin3", "NOT_USABLE")
        record = open_attempt_record(entry, seal_pins=self.pins)
        # Counterfactual index/selection input: pin3 marked usable.
        record = replace(record, claim_usable=True)
        window = AnalysedWindow.from_record(record)
        with self.assertRaisesRegex(AnalysisRefusal, "^analysed_window_shape_unsupported$"):
            open_archive(window, seal_pins=self.pins)

    def source(self):
        original = self.entry.claim_runs_root
        original.mkdir()
        (original / "member.json").write_bytes(b"synthetic mock adapter input")
        source = self.root / "sources/claim-runs/member.json"
        source.parent.mkdir(parents=True)
        source.write_bytes((original / "member.json").read_bytes())
        (self.root / "sources/SHA256SUMS").write_text(f"{fx.sha(source)}  claim-runs/member.json\n")
        return original, source

    def test_missing_original_source_refuses(self):
        original, _ = self.source()
        (original / "member.json").unlink()
        with self.assertRaisesRegex(AnalysisRefusal, "^runs_root_differs_from_archive$"):
            self.handle.compare_runs_root()

    def test_changed_original_source_refuses(self):
        original, _ = self.source()
        (original / "member.json").write_bytes(b"changed")
        with self.assertRaisesRegex(AnalysisRefusal, "^runs_root_differs_from_archive$"):
            self.handle.compare_runs_root()

    def test_extra_original_file_flags_and_census(self):
        original, _ = self.source()
        (original / "extra.json").write_bytes(b"extra")
        flags = self.handle.compare_runs_root()
        self.assertEqual([dict(flag) for flag in flags], [{"code": "runs_root_has_unlisted_file", "count": 1}])
        self.assertEqual(step_record("0", flags=flags).as_dict()["flags"], [dict(flag) for flag in flags])
        self.assertEqual(self.handle.source_bytes("sources/claim-runs/member.json"), b"synthetic mock adapter input")
        checks = {row.path: row.check for row in self.handle.census()}
        self.assertEqual(checks["sources/SHA256SUMS"], "input_census")
        self.assertEqual(checks["sources/claim-runs/member.json"], "sources_sha256sums")
        self.assertEqual(checks["original/claim-runs/member.json"], "sources_sha256sums")

    def test_source_digest_guard(self):
        _, source = self.source()
        source.write_bytes(b"changed")
        with self.assertRaisesRegex(AnalysisRefusal, "^archive_source_unauthenticated$"):
            self.handle.source_bytes("sources/claim-runs/member.json")

    def test_unlisted_output_and_path_traversal_refuse(self):
        for name in ("derived/absent.json", "../harvest.json", "/tmp/outside"):
            with self.assertRaises(AnalysisRefusal):
                self.handle.output_bytes(name)
        with self.assertRaisesRegex(AnalysisRefusal, "^archive_path_invalid$"):
            self.handle.withheld_bytes("withheld/../../harvest.json")

    def test_unhashed_withheld_bytes_pinned_by_census(self):
        path = self.root / "withheld/mock.json"
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(b"synthetic")
        self.assertEqual(self.handle.withheld_bytes("withheld/mock.json"), b"synthetic")
        row = next(row for row in self.handle.census() if row.path == "withheld/mock.json")
        self.assertEqual((row.sha256, row.check), (fx.sha(path), "input_census"))
        path.write_bytes(b"changed")
        with self.assertRaisesRegex(AnalysisRefusal, "^archive_input_changed$"):
            self.handle.withheld_bytes("withheld/mock.json")

    def test_step4_p42_exception_and_target_refusal(self):
        spec = {"cells": [{"cell_id": "p42-abs", "kind": "absolute", "condition_family_id": "df-ph-prefill-p42-mock"},
                          {"cell_id": "p42-cmp", "kind": "comparative", "condition_family_id": "df-ph-prefill-p42-mock"},
                          {"cell_id": "decode", "kind": "absolute", "condition_family_id": "df-ph-decode-mock"}]}
        report = {"cells": [{"cell_id": row["cell_id"], "extractable": row["cell_id"] == "decode"}
                            for row in spec["cells"]], "spec_membership_refusals": []}
        self.assertEqual(classify_step4_exit(1, report, spec), "p42_floor_cells_only")
        report["cells"][-1]["extractable"] = False
        self.assertEqual(classify_step4_exit(1, report, spec), "refused")
        report["cells"][-1]["extractable"] = True
        report["spec_membership_refusals"] = [{"reason": "campaign_member_omitted_from_spec"}]
        self.assertEqual(classify_step4_exit(1, report, spec), "refused")
        self.assertEqual(classify_step4_exit(0, report, spec), "ok")
        self.assertEqual(classify_step4_exit(2, report, spec), "refused")

    def test_step_record_blinds_outcome_and_unclassified_codes(self):
        classes = {"tooling": ["bad_digest"], "outcome": ["denominator_zero"]}
        for code, status, text in (("bad_digest", "tooling_refusal", "bad_digest"),
                                   ("denominator_zero", "outcome_class", "outcome-class refusal at step 6"),
                                   ("unknown_with_value", "unclassified_refusal", "unclassified refusal at step 6")):
            record = step_record("6", refusal_code=code, classes=classes)
            self.assertEqual((record.status, record.refusal), (status, text))
