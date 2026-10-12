import json
from dataclasses import replace
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from joulewise.b5_analysis.archive import open_attempt_record
from joulewise.b5_analysis.windows import AnalysisRefusal, SealPins
from tests.b5_analysis import fixtures as fx


class AttemptRecordTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="s0-attempt-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "archive"
        self.pins = SealPins.load()
        self.entry = fx.structural_archive(self.root)

    def read(self):
        return open_attempt_record(self.entry, seal_pins=self.pins, pack_table=fx.PACK_TABLE)

    def edit(self, relative, function, *, update_index=True):
        document = json.loads((self.root / relative).read_bytes())
        function(document)
        fx.put(self.root / relative, document)
        if relative != "harvest.json":
            record = json.loads((self.root / "harvest.json").read_bytes())
            record["outputs"][relative] = fx.sha(self.root / relative)
            fx.put(self.root / "harvest.json", record)
        if update_index:
            self.entry = replace(self.entry, harvest_record_sha256=fx.sha(self.root / "harvest.json"))

    def refuses(self, code):
        with self.assertRaises(AnalysisRefusal) as caught:
            self.read()
        self.assertEqual(caught.exception.code, code)

    def test_check1_indexed_bytes(self):
        self.edit("harvest.json", lambda row: row.update(flags=99), update_index=False)
        self.refuses("harvest_record_not_the_indexed_one")

    def test_check2_identity_and_shape(self):
        self.edit("harvest.json", lambda row: row.update(plan_id="another-plan"))
        self.refuses("harvest_record_shape_mismatch")

    def test_malformed_verdict_is_a_tooling_refusal(self):
        self.edit("harvest.json", lambda row: row.update(verdict={"malformed": True}))
        self.refuses("harvest_record_shape_mismatch")

    def test_check3_head(self):
        self.edit("harvest.json", lambda row: row["harvest_checkout"].update(head="0" * 40))
        self.refuses("harvest_commit_not_the_pinned_one")

    def test_check3_file_digest(self):
        self.edit("harvest.json", lambda row: row["harvest_checkout"]["files"].update({"joulewise/b5/harvest.py": "0" * 64}))
        self.refuses("harvest_commit_not_the_pinned_one")

    def test_dirty_checkout_flag_is_accepted(self):
        def dirty(row):
            row["harvest_checkout"]["status_clean"] = False
        self.edit("harvest.json", dirty)
        self.edit("derived/exclusions.json", dirty)
        record = self.read()
        self.assertEqual(record.checkout_flags, ("harvest_checkout_status_not_clean",))
        from joulewise.b5_analysis.steps import step_record
        step = step_record("0", flags=record.checkout_flags)
        self.assertIn("harvest_checkout_status_not_clean", step.as_dict()["flags"])

    def history_checkout(self, **changes):
        # This attempt belongs only to history: its exclusions are not usable.
        self.entry = fx.structural_archive(Path(self.tmp.name) / "history", usable=False)
        self.root = self.entry.archive_root
        def dirty(row):
            row["harvest_checkout"].update(changes)
        self.edit("harvest.json", dirty)
        self.edit("derived/exclusions.json", dirty)
        record = self.read()
        self.assertFalse(record.claim_usable)
        self.assertEqual(record.checkout_flags, ("harvest_checkout_status_not_clean",))
        from joulewise.b5_analysis.steps import step_record
        self.assertIn("harvest_checkout_status_not_clean", step_record("0", flags=record.checkout_flags).as_dict()["flags"])

    def test_unanalysed_dirty_status_is_flagged(self):
        self.history_checkout(status_clean=False)

    def test_unanalysed_nonzero_status_lines_is_flagged(self):
        self.history_checkout(status_lines=1)

    def test_unanalysed_checkout_errors_are_flagged(self):
        self.history_checkout(errors=["status:git_exit_1"])

    def test_check4_catalog(self):
        self.edit("derived/exclusions.json", lambda row: row.update(catalog_sha256="0" * 64))
        self.refuses("exclusions_catalog_mismatch")

    def test_check4_checkout_agreement(self):
        self.edit("derived/exclusions.json", lambda row: row["harvest_checkout"].update(status_clean=False))
        self.refuses("exclusions_harvest_checkout_differs")

    def test_check4_output_digest(self):
        (self.root / "derived/exclusions.json").write_bytes((self.root / "derived/exclusions.json").read_bytes() + b" ")
        self.refuses("exclusions_record_unauthenticated")

    def test_check4_stub_form(self):
        self.edit("derived/exclusions.json", lambda row: row.update(schema_version="unknown"))
        self.refuses("exclusions_record_shape_mismatch")

    def test_check5_inconsistent_claim(self):
        self.edit("derived/exclusions.json", lambda row: row.update(claim_usable=False))
        self.refuses("attempt_record_inconsistent")

    def test_check5_index_disagrees(self):
        self.entry = replace(self.entry, claim_usable=False)
        self.refuses("window_index_disagrees_with_archive")

    def test_check5_index_verdict_disagrees(self):
        self.entry = replace(self.entry, verdict="NULL")
        self.refuses("window_index_disagrees_with_archive")

    def test_check6_flags_consistency(self):
        self.edit("derived/window_flags.json", lambda row: row["exclusions"].update(claim_usable=False))
        self.refuses("window_flags_record_inconsistent")

    def test_check6_output_digest(self):
        (self.root / "derived/window_flags.json").write_bytes((self.root / "derived/window_flags.json").read_bytes() + b" ")
        self.refuses("window_flags_record_unauthenticated")

    def test_reader_never_opens_restricted_member_files(self):
        original = Path.read_bytes
        read = []
        def bounded(path):
            relative = path.relative_to(self.root).as_posix()
            self.assertNotIn(relative.split("/")[0], ("withheld", "sources"))
            self.assertNotEqual(relative, "derived/flags.jsonl")
            read.append(relative)
            return original(path)
        with mock.patch.object(Path, "read_bytes", bounded):
            record = self.read()
        self.assertEqual(set(read), {"harvest.json", "derived/exclusions.json", "derived/window_flags.json"})
        self.assertLessEqual(len(record.census), 4)
        self.assertFalse(hasattr(record, "cells"))
        self.assertFalse(hasattr(record, "members_excluded"))

    def test_pin3_wrong_head_on_unanalysed_attempt(self):
        entry = fx.archived_entry("pin3", "NOT_USABLE")
        directory = Path(self.tmp.name) / "pin3"
        import shutil
        shutil.copytree(entry.archive_root, directory, ignore=shutil.ignore_patterns("sources", "withheld"))
        row = json.loads((directory / "harvest.json").read_bytes())
        row["harvest_checkout"]["head"] = self.pins.pins["pin4"]["head"]
        fx.put(directory / "harvest.json", row)
        self.entry = replace(entry, archive_root=directory, harvest_record_sha256=fx.sha(directory / "harvest.json"))
        self.refuses("harvest_commit_not_the_pinned_one")

    def test_forged_pin2_index_rejects_pin4_before_checkout_check(self):
        # Section 3.2 check 2 is earlier than check 3. S0's prose example
        # says check 3, but the pin4-only key already proves the wrong shape.
        self.entry = replace(self.entry, t0_epoch_s=self.pins.erratum_2_epoch_s,
                             harvest_pin=self.pins.pins["pin2"]["head"])
        self.refuses("harvest_record_shape_mismatch")

    def test_pin2_extra_bracket_key(self):
        entry = fx.archived_entry("pin2", "STD")
        directory = Path(self.tmp.name) / "pin2"
        import shutil
        shutil.copytree(entry.archive_root, directory, ignore=shutil.ignore_patterns("sources", "withheld"))
        row = json.loads((directory / "harvest.json").read_bytes())
        row["calibration_bracket"] = {}
        fx.put(directory / "harvest.json", row)
        self.entry = replace(entry, archive_root=directory, harvest_record_sha256=fx.sha(directory / "harvest.json"))
        self.refuses("harvest_record_shape_mismatch")

    def test_all_exported_attempt_forms(self):
        for shape in ("pin1", "pin3"):
            for name, verdict, form in (("NOT_USABLE", "COLLECTED", "document"), ("NULL", "NULL", "stub_null"),
                                        ("NO_COLLECTION", "NO_COLLECTION", "document"), ("UNAVAILABLE", "COLLECTED", "stub_unavailable")):
                with self.subTest(shape=shape, name=name):
                    record = open_attempt_record(fx.archived_entry(shape, name), seal_pins=self.pins, pack_table=fx.PACK_TABLE)
                    self.assertFalse(record.claim_usable)
                    self.assertEqual((record.verdict, record.exclusions_form), (verdict, form))

    def fresh_review_input(self, name):
        self.root = Path(self.tmp.name) / name
        self.entry = fx.structural_archive(self.root)

    def test_review_s3_authenticated_documents_must_agree(self):
        # p3: each changed document is rehashed in harvest.json and the index.
        cases = [
            ("flag-attempt", "derived/window_flags.json", lambda row: row["window"].update(attempt=99)),
            ("flag-plan", "derived/window_flags.json", lambda row: row["window"].update(plan_id="other")),
            ("flag-pack", "derived/window_flags.json", lambda row: row["window"].update(pack_id="other")),
            ("flag-t0", "derived/window_flags.json", lambda row: row["window"].update(t0_epoch_s=0)),
            ("flag-release", "derived/window_flags.json", lambda row: row["exclusions"].update(release_blocked=True)),
            ("doc-release", "derived/exclusions.json", lambda row: row.update(release_blocked=True)),
            ("flag-reasons", "derived/window_flags.json", lambda row: row["exclusions"].update(reasons=["x.y"])),
            ("doc-reasons", "derived/exclusions.json", lambda row: row.update(reasons=["cell.below_minimum"])),
            ("window-reasons", "harvest.json", lambda row: row.update(exclude_window_reasons=["window.something"])),
            ("flag-total", "harvest.json", lambda row: row.update(flags=7)),
            ("flag-family-total", "derived/window_flags.json", lambda row: row["flags"]["by_family"].update(OTHER=1)),
            ("flag-code-total", "derived/window_flags.json", lambda row: row["flags"]["by_code"].update({"x.y": 1})),
            ("flag-catalog", "derived/window_flags.json", lambda row: row["catalog"].update(sha256="0" * 64)),
        ]
        for name, relative, change in cases:
            with self.subTest(name=name):
                self.fresh_review_input(name)
                self.edit(relative, change)
                self.refuses("attempt_record_inconsistent")

    def test_review_s3_unclassified_requires_release_blocked(self):
        # p7e: counts.unclassified is read, even if both documents say False.
        self.edit("derived/window_flags.json", lambda row: row["flags"].update(unclassified=["new.code"]))
        self.refuses("attempt_record_inconsistent")

    def test_review_s3_release_blocked_requires_unclassified(self):
        self.edit("derived/exclusions.json", lambda row: row.update(release_blocked=True))
        self.edit("derived/window_flags.json", lambda row: row["exclusions"].update(release_blocked=True))
        self.refuses("attempt_record_inconsistent")

    def test_review_s3_coherent_unclassified_history_is_retained(self):
        self.root = Path(self.tmp.name) / "unclassified"
        self.entry = fx.structural_archive(self.root, release_blocked=True)
        record = self.read()
        self.assertEqual(record.unclassified, ("s0.unknown",))
        self.assertIs(record.release_blocked, True)

    def test_review_s3_unclassified_lists_must_agree(self):
        for name, relative, change in (
                ("doc-unclassified", "derived/exclusions.json", lambda row: row.update(unclassified=["other.code"])),
                ("summary-unclassified", "derived/window_flags.json", lambda row: row["exclusions"].update(unclassified=["other.code"]))):
            with self.subTest(name=name):
                self.root = Path(self.tmp.name) / name
                self.entry = fx.structural_archive(self.root, release_blocked=True)
                self.edit(relative, change)
                self.refuses("attempt_record_inconsistent")

    def test_review_s3_unusable_reason_agreement(self):
        # Equal documents remain loadable for a removed attempt. An extra
        # harvest or summary reason must not be silently dropped from history.
        for name, relative, change in (
                ("removed-summary", "derived/window_flags.json", lambda row: row["exclusions"].update(reasons=[])),
                ("removed-harvest", "harvest.json", lambda row: row.update(exclude_window_reasons=[]))):
            with self.subTest(name=name):
                self.root = Path(self.tmp.name) / name
                self.entry = fx.structural_archive(self.root, usable=False)
                self.assertFalse(self.read().claim_usable)
                self.edit(relative, change)
                self.refuses("attempt_record_inconsistent")

    def test_review_n1_malformed_record_fields_refuse(self):
        # p3 and p7d: malformed nested objects, reason strings and elements.
        cases = [
            ("summary-exclusions-null", "derived/window_flags.json", lambda row: row.update(exclusions=None), "window_flags_record_inconsistent"),
            ("summary-flags-list", "derived/window_flags.json", lambda row: row.update(flags=[]), "window_flags_record_inconsistent"),
            ("summary-family-list", "derived/window_flags.json", lambda row: row["flags"].update(by_family=[]), "window_flags_record_inconsistent"),
            ("summary-count-bool", "derived/window_flags.json", lambda row: row["flags"]["by_code"].update({"x.y": False}), "window_flags_record_inconsistent"),
            ("summary-unclassified-string", "derived/window_flags.json", lambda row: row["flags"].update(unclassified="abc"), "window_flags_record_inconsistent"),
            ("summary-unclassified-element", "derived/window_flags.json", lambda row: row["flags"].update(unclassified=[{}]), "window_flags_record_inconsistent"),
            ("summary-window-list", "derived/window_flags.json", lambda row: row.update(window=[]), "attempt_record_inconsistent"),
            ("summary-reasons-string", "derived/window_flags.json", lambda row: row["exclusions"].update(reasons="abc"), "attempt_record_inconsistent"),
            ("doc-reasons-string", "derived/exclusions.json", lambda row: row.update(reasons="abc"), "attempt_record_inconsistent"),
            ("doc-reasons-element", "derived/exclusions.json", lambda row: row.update(reasons=[{}]), "attempt_record_inconsistent"),
            ("doc-unclassified-string", "derived/exclusions.json", lambda row: row.update(unclassified="abc"), "attempt_record_inconsistent"),
            ("doc-unclassified-element", "derived/exclusions.json", lambda row: row.update(unclassified=[{}]), "attempt_record_inconsistent"),
            ("window-reasons-int", "harvest.json", lambda row: row.update(exclude_window_reasons=5), "attempt_record_inconsistent"),
            ("window-reasons-string", "harvest.json", lambda row: row.update(exclude_window_reasons="abc"), "attempt_record_inconsistent"),
            ("window-reasons-element", "harvest.json", lambda row: row.update(exclude_window_reasons=[{}]), "attempt_record_inconsistent"),
            ("yield-list", "harvest.json", lambda row: row.update({"yield": [1, 2]}), "attempt_record_inconsistent"),
            ("bracket-list", "harvest.json", lambda row: row.update(calibration_bracket=[]), "attempt_record_inconsistent"),
        ]
        for name, relative, change, code in cases:
            with self.subTest(name=name):
                self.fresh_review_input(name)
                self.edit(relative, change)
                self.refuses(code)

    def test_review_n1_malformed_reference_source_refuses(self):
        for name, value in (("null-reference", {"rescreen": {"reference_source": None}}),
                            ("object-source", {"rescreen": {"reference_source": {"source": {"a": 1}}}}),
                            ("list-rescreen", {"rescreen": []})):
            with self.subTest(name=name):
                self.fresh_review_input(name)
                fx.put(self.root / "derived/neg8-screen.json", value)
                self.edit("harvest.json", lambda row: row["outputs"].update({"derived/neg8-screen.json": fx.sha(self.root / "derived/neg8-screen.json")}))
                self.refuses("attempt_record_inconsistent")

    def test_review_n1_unusable_reason_elements_refuse(self):
        # Non-usable records still need element validation. Otherwise malformed
        # document reasons reach list concatenation or sorting and raise Python
        # exceptions instead of the required tooling refusal.
        for number, value in enumerate((5, "cell.below_minimum", [{}])):
            with self.subTest(value=value):
                self.root = Path(self.tmp.name) / f"removed-reasons-{number}"
                self.entry = fx.structural_archive(self.root, usable=False)
                self.edit("derived/exclusions.json", lambda row: row.update(reasons=value))
                self.refuses("attempt_record_inconsistent")

    def test_review_n6_noninteger_status_lines_is_flagged(self):
        for value in (False, 0.0):
            with self.subTest(value=value):
                self.fresh_review_input("status-" + type(value).__name__)
                self.edit("harvest.json", lambda row: row["harvest_checkout"].update(status_lines=value))
                self.edit("derived/exclusions.json", lambda row: row["harvest_checkout"].update(status_lines=value))
                self.assertEqual(self.read().checkout_flags, ("harvest_checkout_status_not_clean",))
