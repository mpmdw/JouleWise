from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from joulewise.b5 import harvest
from joulewise.b5_analysis.archive import open_attempt_record
from joulewise.b5_analysis.windows import (AnalysisRefusal, IndexEntry, SealPins, WindowIndex, governing_pin,
                                          load_window_index, select_analysed_attempts)
from joulewise.b5_analysis import windows
from tests.b5_analysis import fixtures as fx
from tests.b5_analysis import fixtures_s3b as s3b


class WindowsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="s0-windows-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.pins = SealPins.load()

    def record(self, pack, **kwargs):
        # S0's fast producer must hash the pinned program files, rather than
        # pin4's head paired with the analysis checkout's changed WW bytes.
        # The checkout helper reads the restored files itself; no digest is
        # supplied to, or bypassed in, the archive reader.
        with mock.patch.object(harvest, "__file__", str(s3b.pinned_program_tree() / "joulewise/b5/harvest.py")):
            entry = fx.structural_archive(self.root / (pack + str(len(list(self.root.iterdir())))), pack=pack, **kwargs)
        return open_attempt_record(entry, seal_pins=self.pins, pack_table=fx.PACK_TABLE)

    def history(self):
        records = [self.record("alpha"), self.record("gamma")]
        first = open_attempt_record(fx.archived_entry("pin1", "NOT_USABLE", pack="alpha"), seal_pins=self.pins, pack_table=fx.PACK_TABLE)
        records.append(first)  # first-seal history never participates in selection
        records.append(open_attempt_record(fx.archived_entry("pin2", "NOT_USABLE", pack="beta"), seal_pins=self.pins, pack_table=fx.PACK_TABLE))
        for n, variant in enumerate(("NOT_USABLE", "NO_COLLECTION", "NULL", "UNAVAILABLE"), 2):
            record = open_attempt_record(fx.archived_entry("pin3", variant), seal_pins=self.pins, pack_table=fx.PACK_TABLE)
            # Exported history inputs already carry their attempt ordinals.
            self.assertEqual(record.entry.attempt, n)
            records.append(record)
        entry = replace(records[-1].entry, attempt=7, t0_epoch_s=self.pins.erratum_3_epoch_s + 2,
                        harvest_pin=self.pins.pins["pin4"]["head"], verdict="NO_COLLECTION", entry_kind="no_archive", archive_root=None,
                        harvest_record_sha256=None, claim_usable=False, record_citation="synthetic-window.md:12")
        records.append(open_attempt_record(entry, seal_pins=self.pins, pack_table=fx.PACK_TABLE))
        records.append(self.record("beta", attempt=6))
        return records

    def select(self, records):
        return select_analysed_attempts(WindowIndex(tuple(record.entry for record in records)), records)

    def test_beta_history_selects_attempt6(self):
        result = self.select(self.history())
        self.assertEqual(set(result), {"alpha", "beta", "gamma"})
        self.assertEqual(result["beta"].attempt, 6)
        self.assertEqual(result["beta"].record.record_shape, "pin4")

    def test_release_blocked_earlier_attempt_is_undecided(self):
        records = [self.record("alpha"), self.record("gamma"), self.record("beta", release_blocked=True)]
        records.append(self.record("beta", attempt=2))
        with self.assertRaisesRegex(AnalysisRefusal, "^analysed_attempt_undecided$"):
            self.select(records)

    def test_missing_release_blocked_is_undecided(self):
        records = [self.record("alpha"), self.record("gamma"), self.record("beta")]
        earlier = records[-1]
        relative = "derived/exclusions.json"
        path = earlier.entry.archive_root / relative
        row = json.loads(path.read_bytes()); del row["release_blocked"]; fx.put(path, row)
        flags = earlier.entry.archive_root / "derived/window_flags.json"
        row = json.loads(flags.read_bytes()); row["exclusions"]["release_blocked"] = True; fx.put(flags, row)
        path = earlier.entry.archive_root / "harvest.json"
        row = json.loads(path.read_bytes()); row["outputs"][relative] = fx.sha(earlier.entry.archive_root / relative)
        row["outputs"]["derived/window_flags.json"] = fx.sha(flags); fx.put(path, row)
        records[-1] = open_attempt_record(replace(earlier.entry, harvest_record_sha256=fx.sha(path)), seal_pins=self.pins, pack_table=fx.PACK_TABLE)
        records.append(self.record("beta", attempt=2))
        with self.assertRaisesRegex(AnalysisRefusal, "^analysed_attempt_undecided$"):
            self.select(records)

    def test_governing_pin_strict_epoch_boundaries(self):
        p = self.pins
        for t0, shape in ((p.erratum_2_epoch_s, "pin2"), (p.erratum_2_epoch_s + .5, "pin3"),
                          (p.erratum_3_epoch_s, "pin3"), (p.erratum_3_epoch_s + .5, "pin4")):
            self.assertEqual(governing_pin(t0, "second"), p.pins[shape]["head"])
            self.assertEqual(governing_pin(t0, "first"), p.pins["pin1"]["head"])
        for t0 in (True, float("nan"), float("inf"), "1791738001", None):
            with self.subTest(t0=t0), self.assertRaises(AnalysisRefusal):
                governing_pin(t0, "second")

    def test_pin4_with_pin2_epoch_is_rejected_at_load(self):
        record = self.record("beta")
        data = {field: getattr(record.entry, field) for field in record.entry.__dataclass_fields__}
        for key, value in tuple(data.items()):
            if isinstance(value, Path):
                data[key] = str(value)
        data["t0_epoch_s"] = self.pins.erratum_2_epoch_s
        path = self.root / "index.json"
        fx.put(path, {"schema": "joulewise.b5_window_index.v1", "attempts": [data]})
        with self.assertRaisesRegex(AnalysisRefusal, "^window_index_pin_mismatch$"):
            load_window_index(path, pack_table=fx.PACK_TABLE)

    def test_no_archive_requires_citation_at_load(self):
        record = self.record("beta")
        data = {field: getattr(record.entry, field) for field in record.entry.__dataclass_fields__}
        data.update(entry_kind="no_archive", archive_root=None, harvest_record_sha256=None, claim_usable=False, verdict="NO_COLLECTION")
        for key, value in tuple(data.items()):
            if isinstance(value, Path):
                data[key] = str(value)
        path = self.root / "index.json"
        fx.put(path, {"schema": "joulewise.b5_window_index.v1", "attempts": [data]})
        with self.assertRaisesRegex(AnalysisRefusal, "^window_index_record_citation_required$"):
            load_window_index(path, pack_table=fx.PACK_TABLE)
        data["record_citation"] = "synthetic.md:7"
        fx.put(path, {"schema": "joulewise.b5_window_index.v1", "attempts": [data]})
        entry = load_window_index(path, pack_table=fx.PACK_TABLE).entries[0]
        record = open_attempt_record(entry, seal_pins=self.pins, pack_table=fx.PACK_TABLE)
        self.assertEqual((record.kind, record.claim_usable, record.census), ("no_archive", False, ()))

    def test_malformed_pack_is_a_tooling_refusal(self):
        record = self.record("beta")
        data = {field: getattr(record.entry, field) for field in record.entry.__dataclass_fields__}
        for key, value in tuple(data.items()):
            if isinstance(value, Path):
                data[key] = str(value)
        data["pack"] = {"malformed": True}
        with self.assertRaisesRegex(AnalysisRefusal, "^window_index_invalid$"):
            IndexEntry.from_mapping(data, pack_table=fx.PACK_TABLE)

    def test_duplicate_attempt_is_refused(self):
        record = self.record("beta")
        with self.assertRaisesRegex(AnalysisRefusal, "^window_index_duplicate_attempt$"):
            self.select([record, record])

    def test_block_incomplete_is_refused(self):
        with self.assertRaisesRegex(AnalysisRefusal, "^block_incomplete$"):
            self.select([self.record("alpha"), self.record("beta")])

    def mapping(self, entry):
        return {key: str(value) if isinstance(value, Path) else
                [str(path) for path in value] if key == "superseded_archive_roots" else value
                for key, value in vars(entry).items()}

    def load_entries(self, entries, *, synthetic=True):
        path = self.root / "review-index.json"
        fx.put(path, {"schema": windows.INDEX_SCHEMA, "attempts": [self.mapping(entry) for entry in entries]})
        return load_window_index(path, pack_table=fx.PACK_TABLE if synthetic else None)

    def test_review_s1_pack_label_bound_at_reader(self):
        # p2h: all archive identities say BETA, only the index label says GAMMA.
        entry = replace(self.record("beta").entry, pack="gamma")
        with self.assertRaisesRegex(AnalysisRefusal, "^window_index_pack_mismatch$"):
            open_attempt_record(entry, seal_pins=self.pins, pack_table=fx.PACK_TABLE)

    def test_review_s1_production_pack_and_attempt_prefix_at_load(self):
        table = windows.sealed_pack_table()
        base = self.record("beta").entry
        pack_id = next(iter(table["beta"]))
        valid = replace(base, pack_id=pack_id, plan_id="v5-b5-beta-a1-synthetic")
        self.assertEqual(self.load_entries([valid], synthetic=False).entries, (valid,))
        for changes in ({"pack": "gamma"}, {"pack_id": next(iter(table["gamma"]))},
                        {"plan_id": "v5-b5-alpha-a1-synthetic"}, {"plan_id": "v5-b5-beta-a2-synthetic"},
                        {"plan_id": "v5-b5-beta-a10-synthetic"}):
            with self.subTest(changes=changes), self.assertRaisesRegex(AnalysisRefusal, "^window_index_pack_mismatch$"):
                self.load_entries([replace(valid, **changes)], synthetic=False)

    def test_review_s1_synthetic_identity_requires_explicit_table(self):
        entry = self.record("beta").entry
        with self.assertRaisesRegex(AnalysisRefusal, "^window_index_pack_mismatch$"):
            self.load_entries([entry], synthetic=False)
        self.assertEqual(self.load_entries([entry]).entries, (entry,))

    def test_review_s1_table_is_read_from_pack_directories(self):
        # Changing the sealed input in a scratch root changes the loaded ids;
        # this would fail a table of typed literals or a stale module cache.
        sizing, expected = {"packs": {}}, {}
        for pack in windows.PACKS:
            tree = self.root / "configs/campaigns" / ("counterfactual-" + pack) / "plan_tree.json"
            fx.put(tree, {"synthetic": True})
            sizing["packs"][pack.upper()] = {"plan_tree": {"path": tree.relative_to(self.root).as_posix(),
                                                         "sha256": fx.sha(tree)}}
            expected[pack] = {tree.parent.name: f"v5-b5-{pack}-a{{attempt}}-"}
        fx.put(self.root / "configs/campaigns/v5_claim_25g83/sizing_b5.json", sizing)
        pins = replace(self.pins, sealed={**self.pins.sealed,
            "sizing_sha256": fx.sha(self.root / "configs/campaigns/v5_claim_25g83/sizing_b5.json")})
        with mock.patch.object(windows, "ROOT", self.root):
            self.assertEqual(windows.sealed_pack_table(seal_pins=pins), expected)
            for pack in windows.PACKS:
                pack_id = next(iter(expected[pack]))
                self.assertEqual(windows.sealed_plan_tree_sha256(pack, pack_id, seal_pins=pins),
                    sizing["packs"][pack.upper()]["plan_tree"]["sha256"])

    def test_sizing_record_bytes_must_match_sealed_digest(self):
        # Copy only public, sealed configuration bytes. An otherwise identical
        # JSON value with different bytes must fail the sizing-record binding.
        for relative in ("configs/campaigns/v5_claim_25g83/sizing_b5.json",):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((windows.ROOT / relative).read_bytes())
        sizing_path = self.root / "configs/campaigns/v5_claim_25g83/sizing_b5.json"
        sizing = json.loads(sizing_path.read_bytes())
        for row in sizing["packs"].values():
            relative = row["plan_tree"]["path"]
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((windows.ROOT / relative).read_bytes())
        with mock.patch.object(windows, "ROOT", self.root):
            table = windows.sealed_pack_table(seal_pins=self.pins)
            self.assertTrue(table)
            sizing_path.write_bytes(sizing_path.read_bytes() + b"\n")
            with self.assertRaisesRegex(AnalysisRefusal, "^window_index_pack_mismatch$"):
                windows.sealed_pack_table(seal_pins=self.pins)
            with self.assertRaisesRegex(AnalysisRefusal, "^window_index_pack_mismatch$"):
                windows.sealed_plan_tree_sha256("beta", next(iter(table["beta"])), seal_pins=self.pins)

    def test_review_s2_gap_at_load_and_selection_both_seals(self):
        # p2a: 1 and 3, omitting 2. First-seal history has the same rule.
        for seal in ("first", "second"):
            earlier = self.record("beta", usable=False)
            later = self.record("beta", attempt=3)
            if seal == "first":
                earlier = replace(earlier, entry=replace(earlier.entry, seal=seal, harvest_pin=self.pins.pins["pin1"]["head"]))
                later = replace(later, entry=replace(later.entry, seal=seal, harvest_pin=self.pins.pins["pin1"]["head"]))
            with self.subTest(seal=seal):
                with self.assertRaisesRegex(AnalysisRefusal, "^window_index_attempts_incomplete$"):
                    self.load_entries([earlier.entry, later.entry])
                with self.assertRaisesRegex(AnalysisRefusal, "^window_index_attempts_incomplete$"):
                    self.select([self.record("alpha"), self.record("gamma"), earlier, later])

    def test_review_s2_t0_order_at_load_and_selection(self):
        for seal in ("first", "second"):
            one = self.record("beta", usable=False)
            two = self.record("beta", attempt=2)
            pin = self.pins.pins["pin1" if seal == "first" else "pin4"]["head"]
            one = replace(one, entry=replace(one.entry, seal=seal, harvest_pin=pin, t0_epoch_s=two.entry.t0_epoch_s + 1))
            two = replace(two, entry=replace(two.entry, seal=seal, harvest_pin=pin))
            with self.subTest(seal=seal):
                with self.assertRaisesRegex(AnalysisRefusal, "^window_index_attempts_incomplete$"):
                    self.load_entries([one.entry, two.entry])
                with self.assertRaisesRegex(AnalysisRefusal, "^window_index_attempts_incomplete$"):
                    self.select([self.record("alpha"), self.record("gamma"), one, two])

    def test_review_s2_no_archive_fills_attempt_gap(self):
        one = self.record("beta", usable=False)
        three = self.record("beta", attempt=3)
        entry = replace(one.entry, attempt=2, verdict="NO_COLLECTION", entry_kind="no_archive", archive_root=None,
                        harvest_record_sha256=None, claim_usable=False, record_citation="synthetic.md:2")
        two = open_attempt_record(entry, seal_pins=self.pins, pack_table=fx.PACK_TABLE)
        self.assertEqual(len(self.load_entries([one.entry, entry, three.entry]).entries), 3)
        self.assertEqual(self.select([self.record("alpha"), self.record("gamma"), one, two, three])["beta"].attempt, 3)

    def test_review_n2_first_seal_cannot_fill_second_seal(self):
        # p7a: even a claim-usable first-seal ALPHA cannot rescue this block.
        first = open_attempt_record(fx.archived_entry("pin1", "NOT_USABLE"), seal_pins=self.pins, pack_table=fx.PACK_TABLE)
        first = replace(first, claim_usable=True, release_blocked=False)
        with self.assertRaisesRegex(AnalysisRefusal, "^block_incomplete$"):
            self.select([first, self.record("alpha", usable=False), self.record("beta"), self.record("gamma")])

    def test_review_n2_records_must_follow_index_order(self):
        # p2d: same entries and records, but the records are permuted.
        records = [self.record("alpha"), self.record("beta"), self.record("gamma")]
        with self.assertRaisesRegex(AnalysisRefusal, "^window_index_disagrees_with_archive$"):
            select_analysed_attempts([row.entry for row in records], list(reversed(records)))

    def test_review_n5_absolute_roots_and_superseded_list(self):
        base = self.mapping(self.record("beta").entry)
        mutations = [{key: "relative/root"} for key in
                     ("archive_root", "claim_runs_root", "bound_runs_root", "custody_root", "measurement_root")]
        mutations += [{"superseded_archive_roots": value} for value in ("abc", ["relative"], [3], [None])]
        for changes in mutations:
            with self.subTest(changes=changes), self.assertRaisesRegex(AnalysisRefusal, "^window_index_invalid$"):
                IndexEntry.from_mapping({**base, **changes}, pack_table=fx.PACK_TABLE)
        base["superseded_archive_roots"] = [str(self.root / "superseded")]
        self.assertEqual(IndexEntry.from_mapping(base, pack_table=fx.PACK_TABLE).superseded_archive_roots,
                         (self.root / "superseded",))

    def test_review_n5_no_archive_cannot_be_collected(self):
        entry = replace(self.record("beta").entry, entry_kind="no_archive", archive_root=None,
                        harvest_record_sha256=None, claim_usable=False, record_citation="synthetic.md:1")
        with self.assertRaisesRegex(AnalysisRefusal, "^window_index_invalid$"):
            self.load_entries([entry])

    def test_review_n5_t0_must_be_positive(self):
        for seal in ("first", "second"):
            for t0 in (0, -5):
                with self.subTest(seal=seal, t0=t0), self.assertRaisesRegex(AnalysisRefusal, "^window_index_invalid$"):
                    governing_pin(t0, seal, seal_pins=self.pins)

    def test_review_n1_malformed_index_fields(self):
        base = self.mapping(self.record("beta").entry)
        for changes in ({"entry_kind": []}, {"seal": []}, {"harvest_pin": []}, {"archive_root": 3},
                        {"claim_runs_root": "/tmp/a\x00b"}, {"g10_redraw_cycles": "x"}, {"g10_requested": 1}):
            with self.subTest(changes=changes), self.assertRaisesRegex(AnalysisRefusal, "^window_index_invalid$"):
                IndexEntry.from_mapping({**base, **changes}, pack_table=fx.PACK_TABLE)
