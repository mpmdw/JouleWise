"""The tracked block-5 window index (S11): structure, citations and selection.

The structural tests run anywhere: they load the tracked index with the real
seal pins and the sealed pack table, check every cited record line, and run
the real selection over stand-in attempt records built from the index alone.
The archive test opens every indexed attempt record with the real reader and
selects from those; it skips, naming what is absent, unless every archive
root is on this machine.
"""
import json
import os
from pathlib import Path
import unittest

from joulewise.b5_analysis.archive import AttemptRecord, open_attempt_record
from joulewise.b5_analysis.windows import (SealPins, freeze, governing_pin, load_window_index,
                                          sealed_pack_table, select_analysed_attempts)

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / "configs/analysis/b5/analysed_windows.json"
MANIFESTS = ROOT / "docs/process_traces/2026-10-27-l9-restart/b5-transfer"
DATA_ROOT = Path("/Users/edr")
ANALYSED = {"alpha": ("v5-b5-alpha-a1-20261009T2312Z", 1),
            "beta": ("v5-b5-beta-a6-20261011T2011Z", 6),
            "gamma": ("v5-b5-gamma-a1-20261012T0420Z", 1)}
# RUN_STATE items 28 and 31; the scout report's governing harvest pins.
ANALYSED_PINS = {"alpha": "224a264c5faaae90cdf56118df37e773a932700b",
                 "beta": "b039c0257d1b1d407ee9598222db3f78f6ad7beb",
                 "gamma": "b039c0257d1b1d407ee9598222db3f78f6ad7beb"}
ROOT_FIELDS = ("archive_root", "claim_runs_root", "bound_runs_root", "custody_root", "measurement_root")


def stand_in(entry):
    """A structural record: the index's own verdict and claim_usable, nothing read."""
    return AttemptRecord(entry, "harvested", None, entry.verdict, entry.claim_usable,
                         False if entry.claim_usable else None, "none", (), 0, freeze({}), freeze({}),
                         None, None, None, (), ())


class AnalysedWindowsIndexTests(unittest.TestCase):
    def setUp(self):
        self.pins = SealPins.load()
        self.index = load_window_index(INDEX)
        self.raw = json.loads(INDEX.read_bytes())

    def test_every_attempt_of_every_pack_is_indexed(self):
        attempts = {(e.seal, e.pack): [] for e in self.index.entries}
        for entry in self.index.entries:
            attempts[(entry.seal, entry.pack)].append(entry.attempt)
        self.assertEqual(attempts, {("first", "alpha"): [1, 2, 3], ("second", "alpha"): [1],
                                    ("second", "beta"): [1, 2, 3, 4, 5, 6], ("second", "gamma"): [1]})
        table = sealed_pack_table(seal_pins=self.pins)
        for entry in self.index.entries:
            self.assertIn(entry.pack_id, table[entry.pack])
            self.assertEqual(entry.harvest_pin, governing_pin(entry.t0_epoch_s, entry.seal, seal_pins=self.pins))
            self.assertEqual(entry.entry_kind, "harvested")
            for field in ROOT_FIELDS:
                self.assertTrue(getattr(entry, field).is_relative_to(DATA_ROOT), field)

    def test_selection_over_the_index_gives_the_fixed_analysed_attempts(self):
        records = [stand_in(entry) for entry in self.index.entries]
        windows = select_analysed_attempts(self.index, records, seal_pins=self.pins)
        self.assertEqual({pack: (w.plan_id, w.attempt) for pack, w in windows.items()}, ANALYSED)
        self.assertEqual({pack: w.harvest_pin for pack, w in windows.items()}, ANALYSED_PINS)
        self.assertEqual([e.plan_id for e in self.index.entries if e.claim_usable],
                         [plan for plan, _ in ANALYSED.values()])
        for window in windows.values():
            self.assertEqual(window.record.entry.superseded_archive_roots, ())

    def test_every_citation_names_a_line_holding_the_value(self):
        for row in self.raw["attempts"]:
            citations = row["record_citation"]
            for field in ("verdict", "harvest_record_sha256", "harvest_pin", "t0_epoch_s", "archive_root",
                          "history_table"):
                self.assertIn(field, citations, (row["plan_id"], field))
            for field, cite in citations.items():
                with self.subTest(plan=row["plan_id"], field=field):
                    if ":" not in cite.rsplit("/", 1)[-1]:
                        self.assertTrue((ROOT / cite).is_file() or cite.startswith("pattern "), cite)
                        continue
                    path, line = cite.rsplit(":", 1)
                    text = (ROOT / path).read_text(encoding="utf-8").splitlines()[int(line) - 1]
                    values = {"verdict": ("claim_usable", "true" if row["claim_usable"] else "false"),
                              "history_table": (row["plan_id"], f"| {row['verdict']} |",
                                                "**yes**" if row["claim_usable"] else "| no |"),
                              "harvest_record_sha256": (row["harvest_record_sha256"],),
                              "harvest_pin": (row["harvest_pin"],), "t0_epoch_s": (str(row["t0_epoch_s"]),),
                              "archive_root": (row["archive_root"],), "custody_root": (row["custody_root"],),
                              "measurement_root": (row["measurement_root"],)}.get(field, ())
                    for value in values:
                        self.assertIn(value, text)

    def test_analysed_roots_and_harvest_records_match_the_transfer_manifests(self):
        if not MANIFESTS.is_dir():
            self.skipTest("transfer manifests are on main, not on this branch: " + str(MANIFESTS.relative_to(ROOT)))
        for pack, (plan, _) in ANALYSED.items():
            entry = next(e for e in self.index.entries if e.plan_id == plan)
            files = {}
            for item in ("harvest", "runs", "custody"):
                manifest = json.loads((MANIFESTS / f"{plan}-{item}.manifest.json").read_bytes())
                self.assertEqual(manifest["data_root"], str(DATA_ROOT))
                files.update({DATA_ROOT / row["path"]: row["sha256"] for row in manifest["files"]})
            self.assertEqual(files[entry.archive_root / "harvest.json"], entry.harvest_record_sha256)
            for field in ("archive_root", "claim_runs_root", "bound_runs_root", "custody_root"):
                self.assertTrue(any(path.is_relative_to(getattr(entry, field)) for path in files), field)
            ledger = json.loads((MANIFESTS / "measurement-corpus18-data.manifest.json").read_bytes())
            self.assertIn(str((entry.measurement_root / "runs/calibration_observation_ledger.jsonl")
                              .relative_to(DATA_ROOT)), {row["path"] for row in ledger["files"]})

    def test_real_attempt_records_select_the_analysed_attempts(self):
        if os.environ.get("JW_B5_SYNTHETIC_ONLY") == "1":
            self.skipTest("JW_B5_SYNTHETIC_ONLY=1 forbids reading the real block-5 archives")
        absent = sorted({str(root) for e in self.index.entries for root in (e.archive_root, e.claim_runs_root,
                         e.measurement_root) if not root.is_dir()})
        if absent:
            self.skipTest("block-5 roots absent on this machine: " + ", ".join(absent))
        records = [open_attempt_record(entry, seal_pins=self.pins) for entry in self.index.entries]
        windows = select_analysed_attempts(self.index, records, seal_pins=self.pins)
        self.assertEqual({pack: (w.plan_id, w.attempt) for pack, w in windows.items()}, ANALYSED)
        self.assertEqual({pack: w.record.record_shape for pack, w in windows.items()},
                         {"alpha": "pin2", "beta": "pin4", "gamma": "pin4"})


if __name__ == "__main__":
    unittest.main()
