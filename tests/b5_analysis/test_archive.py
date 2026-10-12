from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from joulewise.b5_analysis.archive import open_archive, open_attempt_record
from joulewise.b5_analysis import archive
from joulewise.b5_analysis.steps import classify_step4_exit, step_record
from joulewise.b5_analysis.windows import AnalysisRefusal, AnalysedWindow, SealPins, select_analysed_attempts
from tests.b5_analysis import fixtures as fx


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="s0-archive-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "archive"
        self.pins = SealPins.load()
        self.entry = fx.structural_archive(self.root)
        self.window = fx.selected_window(open_attempt_record(self.entry, seal_pins=self.pins, pack_table=fx.PACK_TABLE), seal_pins=self.pins)
        self.handle = open_archive(self.window, seal_pins=self.pins, pack_table=fx.PACK_TABLE)

    def test_roster_digest_guard(self):
        with (self.root / "derived/roster.json").open("ab") as out:
            out.write(b"x")
        with self.assertRaisesRegex(AnalysisRefusal, "^roster_record_unauthenticated$"):
            self.handle.output_bytes("derived/roster.json")

    def test_archive_rechecks_indexed_harvest(self):
        with (self.root / "harvest.json").open("ab") as out:
            out.write(b" ")
        with self.assertRaisesRegex(AnalysisRefusal, "^harvest_record_not_the_indexed_one$"):
            open_archive(self.window, seal_pins=self.pins, pack_table=fx.PACK_TABLE)

    def test_unusable_attempt_is_refused(self):
        entry = fx.structural_archive(Path(self.tmp.name) / "unusable", usable=False)
        window = AnalysedWindow.from_record(open_attempt_record(entry, seal_pins=self.pins, pack_table=fx.PACK_TABLE))
        with self.assertRaisesRegex(AnalysisRefusal, "^attempt_not_claim_usable$"):
            open_archive(window, seal_pins=self.pins, pack_table=fx.PACK_TABLE)

    def dirty_checkout(self, **changes):
        record = json.loads((self.root / "harvest.json").read_bytes())
        record["harvest_checkout"].update(changes)
        exclusions = json.loads((self.root / "derived/exclusions.json").read_bytes())
        exclusions["harvest_checkout"] = record["harvest_checkout"]
        fx.put(self.root / "derived/exclusions.json", exclusions)
        record["outputs"]["derived/exclusions.json"] = fx.sha(self.root / "derived/exclusions.json")
        fx.put(self.root / "harvest.json", record)
        entry = replace(self.entry, harvest_record_sha256=fx.sha(self.root / "harvest.json"))
        return fx.selected_window(open_attempt_record(entry, seal_pins=self.pins, pack_table=fx.PACK_TABLE), seal_pins=self.pins)

    def test_analysed_dirty_status_refuses(self):
        window = self.dirty_checkout(status_clean=False)
        with self.assertRaisesRegex(AnalysisRefusal, "^harvest_checkout_not_clean$"):
            open_archive(window, seal_pins=self.pins, pack_table=fx.PACK_TABLE)

    def test_analysed_nonzero_status_lines_refuses(self):
        window = self.dirty_checkout(status_lines=1)
        with self.assertRaisesRegex(AnalysisRefusal, "^harvest_checkout_not_clean$"):
            open_archive(window, seal_pins=self.pins, pack_table=fx.PACK_TABLE)

    def test_analysed_checkout_errors_refuse(self):
        window = self.dirty_checkout(errors=["status:git_exit_1"])
        with self.assertRaisesRegex(AnalysisRefusal, "^harvest_checkout_not_clean$"):
            open_archive(window, seal_pins=self.pins, pack_table=fx.PACK_TABLE)

    def test_analysed_status_must_be_exactly_true(self):
        for value in (None, 1, "true"):
            with self.subTest(value=value):
                window = self.dirty_checkout(status_clean=value)
                with self.assertRaisesRegex(AnalysisRefusal, "^harvest_checkout_not_clean$"):
                    open_archive(window, seal_pins=self.pins, pack_table=fx.PACK_TABLE)

    def test_analysed_pin3_is_unsupported(self):
        entry = fx.archived_entry("pin3", "NOT_USABLE")
        record = open_attempt_record(entry, seal_pins=self.pins, pack_table=fx.PACK_TABLE)
        # Counterfactual index/selection input: pin3 marked usable.
        record = replace(record, claim_usable=True)
        window = fx.selected_window(record, seal_pins=self.pins)
        with self.assertRaisesRegex(AnalysisRefusal, "^analysed_window_shape_unsupported$"):
            open_archive(window, seal_pins=self.pins, pack_table=fx.PACK_TABLE)

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

    def test_review_n2_symlink_cannot_escape_even_with_matching_digest(self):
        # p4: the outside file has exactly the bytes the output digest pins.
        path = self.root / "derived/roster.json"
        outside = Path(self.tmp.name) / "outside.json"
        outside.write_bytes(path.read_bytes())
        path.unlink()
        path.symlink_to(outside)
        with self.assertRaisesRegex(AnalysisRefusal, "^archive_path_invalid$"):
            self.handle.output_bytes("derived/roster.json")
        path.unlink()
        inside = self.root / "derived/roster.real"
        inside.write_bytes(outside.read_bytes())
        path.symlink_to(inside)
        self.assertEqual(self.handle.output_bytes("derived/roster.json"), inside.read_bytes())

    def test_review_n2_output_digest_pattern_checked_before_io(self):
        # M15 targets _output's format check. A malformed hash would also fail
        # the later byte comparison, so assert refusal before reading bytes.
        for digest in ("A" * 64, "0" * 63, "g" * 64, "0" * 65):
            with self.subTest(digest=digest), mock.patch.object(archive, "_read", return_value=b"counterfactual") as read:
                with self.assertRaisesRegex(AnalysisRefusal, "^roster_record_unauthenticated$"):
                    archive._output({"outputs": {"derived/roster.json": digest}}, self.root, "derived/roster.json", {})
                read.assert_not_called()

    def test_review_n2_p42_subset_is_refused(self):
        # p6 uses the real sealed spec, with just one of its two p42 cells
        # refused. N7's disposition retains the stricter equality for S0.
        spec = json.loads((fx.ROOT / "configs/campaigns/d117_floor_qwen3-8b_v5/extraction_spec.json").read_bytes())
        p42 = [row["cell_id"] for row in spec["cells"] if "p42" in row["condition_family_id"].split("-")
               and row["kind"] in ("absolute", "comparative")]
        self.assertGreater(len(p42), 1)
        report = {"cells": [{"cell_id": row["cell_id"], "extractable": row["cell_id"] != p42[0]}
                            for row in spec["cells"]], "spec_membership_refusals": []}
        self.assertEqual(classify_step4_exit(1, report, spec), "refused")
        for row in report["cells"]:
            row["extractable"] = row["cell_id"] not in p42
        self.assertEqual(classify_step4_exit(1, report, spec), "p42_floor_cells_only")

    def test_review_n3_only_selected_window_can_open(self):
        record = open_attempt_record(self.entry, seal_pins=self.pins, pack_table=fx.PACK_TABLE)
        # The claim-usable record is authentic, but from_record is not selection.
        with self.assertRaisesRegex(AnalysisRefusal, "^analysed_attempt_not_selected$"):
            open_archive(AnalysedWindow.from_record(record), seal_pins=self.pins, pack_table=fx.PACK_TABLE)
        self.assertEqual(open_archive(fx.selected_window(record), seal_pins=self.pins,
                                     pack_table=fx.PACK_TABLE).window.record, record)

    def test_review_n3_later_usable_attempt_cannot_open(self):
        # Any claim-usable record used to open, even a later unselected attempt.
        one = open_attempt_record(self.entry, seal_pins=self.pins, pack_table=fx.PACK_TABLE)
        entry = fx.structural_archive(Path(self.tmp.name) / "later", pack="beta", attempt=2)
        two = open_attempt_record(entry, seal_pins=self.pins, pack_table=fx.PACK_TABLE)
        others = [open_attempt_record(fx.structural_archive(Path(self.tmp.name) / pack, pack=pack),
                                     seal_pins=self.pins, pack_table=fx.PACK_TABLE) for pack in ("alpha", "gamma")]
        records = [one, two, *others]
        chosen = select_analysed_attempts([row.entry for row in records], records)["beta"]
        self.assertEqual(chosen.attempt, 1)
        later = AnalysedWindow.from_record(two)
        for window in (later, replace(later, _selection_token=object()),
                       replace(later, _selection_token=chosen._selection_token)):
            with self.subTest(window=window.attempt), self.assertRaisesRegex(AnalysisRefusal, "^analysed_attempt_not_selected$"):
                open_archive(window, seal_pins=self.pins, pack_table=fx.PACK_TABLE)

    def test_review_n1_malformed_archive_paths_refuse(self):
        # p7b: callers must receive a coded refusal, never TypeError/ValueError.
        for method in (self.handle.output_bytes, self.handle.source_bytes, self.handle.withheld_bytes):
            for name in (None, [], 5, "withheld/a\x00b"):
                with self.subTest(method=method.__name__, name=name), self.assertRaisesRegex(AnalysisRefusal, "^archive_path_invalid$"):
                    method(name)

    def test_review_n1_step4_malformed_spec_and_elements_refuse(self):
        # p6's three crash inputs plus malformed element/id types.
        report = {"cells": [{"cell_id": "floor", "extractable": False}], "spec_membership_refusals": []}
        spec = {"cells": [{"cell_id": "floor", "kind": "absolute", "condition_family_id": "p42"}]}
        malformed_specs = [None, [], {"cells": ["x"]}, {"cells": [dict(spec["cells"][0], condition_family_id=None)]},
                           {"cells": [dict(spec["cells"][0], cell_id=None)]}, {"cells": [dict(spec["cells"][0], cell_id=[])]},
                           {"cells": spec["cells"] * 2}]
        for malformed in malformed_specs:
            with self.subTest(spec=malformed):
                self.assertEqual(classify_step4_exit(1, report, malformed), "refused")
        for cells in (["x"], [{"extractable": False}], [{"cell_id": [], "extractable": False}],
                      [{"cell_id": "floor", "extractable": 0}]):
            with self.subTest(cells=cells):
                self.assertEqual(classify_step4_exit(1, {**report, "cells": cells}, spec), "refused")
        for status in (True, False, "1"):
            self.assertEqual(classify_step4_exit(status, report, spec), "refused")
        self.assertEqual(classify_step4_exit(1, None, spec), "refused")

    def test_review_n6_status_lines_must_be_integer_zero(self):
        # p7h: False == 0 and 0.0 == 0 must not authenticate a clean checkout.
        for value in (False, 0.0):
            with self.subTest(value=value):
                window = self.dirty_checkout(status_lines=value)
                with self.assertRaisesRegex(AnalysisRefusal, "^harvest_checkout_not_clean$"):
                    open_archive(window, seal_pins=self.pins, pack_table=fx.PACK_TABLE)
