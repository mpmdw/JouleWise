"""Synthetic-only full-inventory R1 journals and WP14(a) classification."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import tempfile
import threading
import unittest
from unittest.mock import Mock, patch

from joulewise.align.apple import r1_runtime
from joulewise.align.apple.r1_runtime import (
    InventoryJournal, NS, ProductionBackend, RuntimeFailure, classify_step, s7_for_picks,
)
from tests.align.r1_synthetic import SyntheticBackend
from tests.align.w1_synthetic import AMBIENT_C, FAST, SLOW, FAN

PREFILL_NS = 1300 * NS
LAST_DECODE_NS = 1420 * NS
R0_SENSORS = {"s_fast": FAST, "s_slow": SLOW}
# PR #692 D4/D5: the slow role needs 60 s < cooling tau <= 300 s (and band hold
# tau x ln(rise / 1 C) <= 300 s); a 60 s key is now on the fast side of the boundary.
SLOW_TAU = 120.0


def lean(row):
    """The journal file keeps the full row; memory keeps what the classifier reads."""
    return {**row, "values": {key: row["values"][key] for key in ("sensors", "errors")}}


def file_rows(path):
    return [lean(json.loads(line)) for line in Path(path).read_text().splitlines()]


def step_capture():
    inventory = {"complete": True, "errors": {}, "unsupported_types": {}, "keys": [
        {"key": k, "unit": "rpm" if k == FAN else "degC", "data_type": "flt ", "data_size": 4}
        for k in (FAST, SLOW, FAN, "Ta0P")]}
    rows = []
    for t in range(-1, 1022):
        sensors = {FAN: 1200.0, "Ta0P": 40.0}
        for key, amplitude, tau in ((FAST, 12.0, 3.0), (SLOW, 6.0, SLOW_TAU)):
            if t < 300:
                value = 40.0 + (t % 3 - 1) * 0.01  # three distinct quiet readings
            elif t <= 420:
                value = 40.0 + amplitude * (1 - math.exp(-(t - 300) / tau))
            else:
                value = 40.0 + amplitude * (1 - math.exp(-120 / tau)) * math.exp(-(t - 420) / tau)
            sensors[key] = value
        stamp = (1000 + t) * NS
        rows.append({"started": {"monotonic_ns": stamp}, "finished": {"monotonic_ns": stamp + 1_000_000},
                     "values": {"sensors": sensors, "errors": {}}, "phase": None, "seq": len(rows) + 1})
    return inventory, rows


class ClassificationTests(unittest.TestCase):
    def classify(self, inventory, rows, **kwargs):
        return classify_step(inventory, rows, prefill_ns=PREFILL_NS, last_decode_ns=LAST_DECODE_NS,
                             r0_sensors=kwargs.pop("r0_sensors", R0_SENSORS), **kwargs)

    def test_physical_classes_picks_change_flag_and_digest(self):
        inventory, rows = step_capture()
        original = deepcopy(rows)
        result = self.classify(inventory, rows)
        self.assertEqual(result["status"], "pass")
        self.assertEqual((result["s_fast"], result["s_slow"]), (FAST, SLOW))
        self.assertEqual(result["die_candidates"], [FAST])
        self.assertEqual(result["heatsink_candidates"], [SLOW])
        self.assertEqual(set(result["record_only"]), {"Ta0P", FAN})
        self.assertFalse(result["sensor_pick_changed"])
        self.assertEqual(result["flags"], [])
        self.assertEqual(result["r0_sensors"], R0_SENSORS)
        self.assertEqual(result["journal_rows"], len(rows))
        slow = next(row for row in result["ranking"] if row["key"] == SLOW)
        self.assertAlmostEqual(slow["tau_s"], SLOW_TAU, delta=0.1)
        self.assertEqual(rows, original)
        digest = result.pop("classification_sha256")
        expected = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":"),
                                            allow_nan=False).encode()).hexdigest()
        self.assertEqual(digest, expected)
        for prior in ({"s_fast": "Ta0P", "s_slow": SLOW}, {"s_fast": FAST, "s_slow": "Ta0P"}):
            with self.subTest(prior=prior):
                changed = self.classify(inventory, rows, r0_sensors=prior)
                self.assertEqual(changed["status"], "pass")
                self.assertTrue(changed["sensor_pick_changed"])
                self.assertEqual(changed["flags"], ["r1.sensor_pick_changed"])
                self.assertNotEqual(changed["classification_sha256"], digest)

    def test_phase_boundaries_and_outside_rows(self):
        inventory, rows = step_capture()
        from joulewise.align.apple import smc_enumeration
        with patch.object(smc_enumeration, "rank", wraps=smc_enumeration.rank) as rank:
            result = self.classify(inventory, rows)
        capture = rank.call_args.args[0]
        self.assertEqual(rank.call_args.kwargs, {"stage": "r1"})
        self.assertEqual(capture["started"], {"monotonic_ns": 1000 * NS})
        self.assertEqual(result["phases"], [
            {"phase": "idle", "start_s": 0, "end_s": 300},
            {"phase": "load", "start_s": 300, "end_s": 420},
            {"phase": "recovery", "start_s": 420, "end_s": 1020}])
        phases = {row["started"]["monotonic_ns"]: row["phase"] for row in capture["samples"]}
        for t, phase in ((999, "outside"), (1000, "idle"), (1299, "idle"), (1300, "load"),
                         (1420, "load"), (1421, "recovery"), (2020, "recovery"), (2021, "outside")):
            self.assertEqual(phases[t * NS], phase)
        inside = [row for row in rows if 1000 * NS <= row["started"]["monotonic_ns"] <= 2020 * NS]
        self.assertEqual(result["ranking"], self.classify(inventory, inside)["ranking"])

    def test_record_carries_the_pr692_classifier_fields(self):
        # LEAD-RULINGS-2 R9-1: record only; picks and status are unchanged.
        from joulewise.align.apple import smc_enumeration
        inventory, rows = step_capture()
        alias = "Tp9z"  # an exact copy of the fast key (sorts after it): selected_key_aliases is non-empty
        inventory["keys"].append({"key": alias, "unit": "degC", "data_type": "flt ", "data_size": 4})
        for row in rows:
            row["values"]["sensors"][alias] = row["values"]["sensors"][FAST]
        with patch.object(smc_enumeration, "rank", wraps=smc_enumeration.rank) as rank:
            result = self.classify(inventory, rows)
        ranked = smc_enumeration.rank(rank.call_args.args[0], stage="r1")
        fields = ("heat_ordering_indeterminate", "heat_ordering_wide_exclusion", "recovery_onset_gap_s",
                  "alternative_slow_picks", "selected_key_aliases")
        for field in fields:
            with self.subTest(field=field):
                self.assertIn(field, result)
                self.assertEqual(result[field], ranked[field])
        self.assertEqual(result["selected_key_aliases"][FAST], [alias])
        self.assertIsNotNone(result["recovery_onset_gap_s"])
        self.assertEqual(set(result["alternative_slow_picks"]), {"design_literal", "opus", "sol"})
        self.assertEqual((result["status"], result["s_fast"], result["s_slow"]), ("pass", FAST, SLOW))
        # Inside the digest: a changed diagnostic changes classification_sha256.
        digest = result.pop("classification_sha256")
        result["heat_ordering_indeterminate"] = not result["heat_ordering_indeterminate"]
        self.assertNotEqual(hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":"),
                                                      allow_nan=False).encode()).hexdigest(), digest)

    def test_missing_recovery_tail_fails_even_when_rank_still_has_picks(self):
        inventory, rows = step_capture()
        full_rows = rows
        rows = [row for row in rows if row["started"]["monotonic_ns"] <= 2018 * NS]
        result = self.classify(inventory, rows)
        self.assertEqual((result["s_fast"], result["s_slow"]), (FAST, SLOW))
        self.assertEqual(result["status"], "fail")
        self.assertEqual(result["reason"], "recovery_not_observed")
        rows.append(next(row for row in full_rows if row["started"]["monotonic_ns"] == 2019 * NS))
        self.assertEqual(self.classify(inventory, rows)["status"], "pass")

    def test_missing_quiet_start_fails_even_when_rank_still_has_picks(self):
        inventory, rows = step_capture()
        rows = [row for row in rows if row["started"]["monotonic_ns"] > 1000 * NS]
        result = self.classify(inventory, rows)
        self.assertEqual((result["s_fast"], result["s_slow"]), (FAST, SLOW))
        self.assertEqual(result["status"], "fail")
        self.assertEqual(result["reason"], "quiet_not_observed")

    def test_null_pick_fails(self):
        inventory, rows = step_capture()
        inventory["keys"] = [key for key in inventory["keys"] if key["key"] != SLOW]
        result = self.classify(inventory, rows)
        self.assertEqual(result["status"], "fail")
        self.assertIsNone(result["s_slow"])


class ChangedPickRecoveryTests(unittest.TestCase):
    """Protocol v4 :249-251 (Sol critique of round 5): when R1 changes R0's
    picks, S7 is recomputed for the R1 picks from the full-inventory journal."""

    def test_s7_for_the_r1_picks_from_the_inventory_journal(self):
        _, rows = step_capture()
        result = s7_for_picks(rows, {"s_fast": FAST, "s_slow": SLOW}, prefill_ns=PREFILL_NS, quiet_s=300)
        self.assertAlmostEqual(result["reference_c"]["s_slow"], 40.0, places=6)
        self.assertEqual(result["band_c"]["s_slow"], 1.0)
        # Slow peak 6 (1 - e^-1) = 3.79 C decays (tau 120 s) to 1.0 C after ~160 s.
        self.assertAlmostEqual(result["recovery_s"], SLOW_TAU * math.log(6 * (1 - math.exp(-120 / SLOW_TAU))),
                               delta=1.5)
        self.assertFalse(result["recovery_censored"])
        self.assertAlmostEqual(result["S7"], min(300.0, 3 * result["recovery_s"]))
        short = [r for r in rows if r["started"]["monotonic_ns"] <= 1450 * NS]
        censored = s7_for_picks(short, {"s_fast": FAST, "s_slow": SLOW}, prefill_ns=PREFILL_NS, quiet_s=300)
        self.assertTrue(censored["recovery_censored"])
        quiet_missing = s7_for_picks(rows, {"s_fast": FAST, "s_slow": "TZ9Z"}, prefill_ns=PREFILL_NS, quiet_s=300)
        self.assertIsNone(quiet_missing["S7"])

    def test_reference_and_band_are_the_classifier_d2_baseline(self):
        # LEAD-RULINGS-2 R9-2 (WP14(b), PR #692 D2): the last 60 s median and
        # the OLS residual SD, not the whole-300 s median and raw SD. A quiet
        # drift of 0.6 C/min on the slow key widens the raw SD (about 0.87 C,
        # band 2.6 C) but not the residual SD (band 1.0 C).
        from joulewise.align.apple import smc_enumeration
        inventory, rows = step_capture()
        for row in rows:
            t = row["started"]["monotonic_ns"] / NS - 1000
            if 0 <= t < 300:
                row["values"]["sensors"][SLOW] += 0.01 * (t - 300)
        picks = {"s_fast": FAST, "s_slow": SLOW}
        result = s7_for_picks(rows, picks, prefill_ns=PREFILL_NS, quiet_s=300)
        self.assertEqual(result["rule"], r1_runtime.R1_PICK_S7_RULE)
        with patch.object(smc_enumeration, "rank", wraps=smc_enumeration.rank) as rank:
            classify_step(inventory, rows, prefill_ns=PREFILL_NS, last_decode_ns=LAST_DECODE_NS,
                          r0_sensors=R0_SENSORS)
        ranking = {row["key"]: row for row in smc_enumeration.rank(rank.call_args.args[0], stage="r1")["ranking"]}
        for role, key in picks.items():
            with self.subTest(role=role):
                self.assertEqual(result["reference_c"][role], ranking[key]["baseline"])
                self.assertEqual(result["noise_c"][role], ranking[key]["noise"])
                self.assertEqual(result["band_c"][role], max(1.0, 3 * ranking[key]["noise"]))
        self.assertLess(result["noise_c"]["s_slow"], 0.05)
        self.assertEqual(result["band_c"]["s_slow"], 1.0)
        self.assertAlmostEqual(result["reference_c"]["s_slow"], 40.0 - 0.3, delta=0.02)
        self.assertEqual(result["S7"], r1_runtime.pick_s7(result["recovery_s"]))
        quiet = [r["values"]["sensors"][SLOW] for r in rows if 1000 * NS <= r["started"]["monotonic_ns"] < PREFILL_NS]
        self.assertGreater(3 * statistics.pstdev(quiet), 2.0)  # the pre-R9-2 band this replaces

    def test_short_last_60s_window_has_no_s7(self):
        _, rows = step_capture()
        # Four valid reads in the last 60 s (1240, 1297-1299); the whole 300 s holds 245.
        thin = [r for r in rows if not 1241 * NS <= r["started"]["monotonic_ns"] < 1297 * NS]
        result = s7_for_picks(thin, {"s_fast": FAST, "s_slow": SLOW}, prefill_ns=PREFILL_NS, quiet_s=300)
        self.assertIsNone(result["S7"])
        self.assertIn("last 60 s of the quiet window", result["reason"])


class JournalTests(unittest.TestCase):
    def test_synthetic_reader_journal_and_classification(self):
        backend = SyntheticBackend({})
        self.addCleanup(backend.close)
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as td:
            path = Path(td) / "inventory.jsonl"
            now_ns = lambda: round(backend.monotonic() * NS)
            journal = InventoryJournal(backend.inventory_reader(), now_ns, path)
            journal.start()
            self.assertEqual(journal.keys, sorted((FAST, SLOW, FAN, "Ta0P")))
            self.assertEqual({item["key"]: item["unit"] for item in journal.inventory["keys"]},
                             {FAST: "degC", SLOW: "degC", FAN: "rpm", "Ta0P": "degC"})
            journal.sample()
            stop = backend.ticker(journal.sample)
            self.addCleanup(stop)
            backend.clock.sleep(1)
            backend.world.busy_w = 80.0
            backend.clock.sleep(2)
            stop()
            rows = journal.rows
            self.assertEqual(len(rows), 4)
            self.assertEqual([row["seq"] for row in rows], [1, 2, 3, 4])
            self.assertEqual(file_rows(path), rows)
            self.assertIn("readings", json.loads(path.read_text().splitlines()[0])["values"])
            self.assertTrue(all(row["phase"] is None for row in rows))
            self.assertEqual(set(rows[0]["values"]["sensors"]), set(journal.keys))
            self.assertEqual(rows[0]["values"]["sensors"][FAST], AMBIENT_C)
            self.assertGreater(rows[-1]["values"]["sensors"][FAST], AMBIENT_C)
            self.assertEqual(rows[0]["values"]["sensors"]["Ta0P"], rows[-1]["values"]["sensors"]["Ta0P"])
            rows[0]["values"]["sensors"][FAST] = -999
            self.assertEqual(journal.rows[0]["values"]["sensors"][FAST], AMBIENT_C)
            result = classify_step(journal.inventory, journal.rows, prefill_ns=NS, last_decode_ns=2 * NS,
                                   quiet_s=1, recovery_s=600, r0_sensors=R0_SENSORS)
            self.assertEqual(result["journal_rows"], 4)
            self.assertEqual((result["status"], result["reason"]), ("fail", "recovery_not_observed"))

    def test_failed_sweep_is_a_bracketed_error_row(self):
        inventory, _ = step_capture()
        reader = Mock()
        reader.enumerate_sensors.return_value = inventory
        reader.read.side_effect = OSError("synthetic reader unavailable")
        clock = Mock(side_effect=[10 * NS, 10 * NS + 1_000_000])
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as td:
            path = Path(td) / "inventory.jsonl"
            journal = InventoryJournal(reader, clock, path)
            journal.start()
            journal.sample()
            row, = journal.rows
            self.assertEqual(row["started"]["monotonic_ns"], 10 * NS)
            self.assertEqual(row["finished"]["monotonic_ns"], 10 * NS + 1_000_000)
            self.assertEqual(set(row["values"]["errors"]), set(journal.keys))
            self.assertTrue(all("OSError" in error for error in row["values"]["errors"].values()))
            self.assertTrue(all(value is None for value in row["values"]["sensors"].values()))
            self.assertEqual(file_rows(path), [row])

    def test_concurrent_ticks_keep_sequence_and_file_order(self):
        reader = Mock()
        reader.enumerate_sensors.return_value = {"complete": True, "keys": [{"key": FAST}]}
        reader.read.return_value = {"values": {FAST: 40.0}, "errors": {}, "raw": {}}
        ready = threading.Barrier(4)
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as td:
            path = Path(td) / "inventory.jsonl"
            journal = InventoryJournal(reader, lambda: 0, path)
            journal.start()

            def tick(_):
                ready.wait(timeout=5)
                journal.sample()

            with ThreadPoolExecutor(max_workers=4) as pool:
                list(pool.map(tick, range(4)))
            self.assertEqual([row["seq"] for row in journal.rows], [1, 2, 3, 4])
            self.assertEqual(file_rows(path), journal.rows)

    def test_incomplete_or_empty_inventory_refuses(self):
        for inventory in ({"complete": False, "keys": [{"key": FAST}]}, {"complete": True, "keys": []}):
            with self.subTest(inventory=inventory):
                reader = Mock()
                reader.enumerate_sensors.return_value = inventory
                with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as td:
                    path = Path(td) / "inventory.jsonl"
                    with self.assertRaises(RuntimeFailure):
                        InventoryJournal(reader, lambda: 0, path).start()
                    self.assertFalse(path.exists())

    def test_production_reader_uses_default_transport(self):
        with patch("joulewise.align.apple.smc_reader.Reader") as reader:
            self.assertIs(ProductionBackend({}).inventory_reader(), reader.return_value)
        reader.assert_called_once_with()
