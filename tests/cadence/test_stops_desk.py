"""Named stops and the Air desk: tables, refusals on planted energy/slot values, the quiet lock."""
from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import unittest

from joulewise.cadence import desk
from joulewise.cadence.stops import evaluate_named_stops

RULES = {"instrument_fault": True, "refusal": True, "contaminated_redos_max": 3, "contaminated_redos_scope": "span",
         "band_unreachable_max": 2, "band_unreachable_scope": "span", "leg_time_factor": 1.5}
OK_RESULT = {"chain_exit_code": 0, "chain_outcome": "COMPLETE", "fault": False, "verdict": "GO"}
METER = {"present": True, "proven_stopped": True, "bad_polls": 0, "usb_errors": 0}


def leg(i, **kw):
    base = {"leg_id": f"L{i:03d}", "start_band": "mid", "band_reached": True, "wall_s": 1200.0, "budget_s": 1500.0,
            "contaminated_redos": 0}
    base.update(kw)
    return base


def span(legs, result=OK_RESULT, meter=METER):
    return {"result": result, "meter": meter, "feeds_proven_stopped": True, "legs": legs}


class NamedStops(unittest.TestCase):
    def codes(self, s, history=(), rules=RULES):
        return [x["code"] for x in evaluate_named_stops(rules, s, history)]

    def test_clean_span_pages_nobody(self):
        self.assertEqual(self.codes(span([leg(1), leg(2)])), [])

    def test_go_with_exit_3_is_a_refusal(self):
        self.assertEqual(self.codes(span([], {**OK_RESULT, "chain_exit_code": 3, "chain_outcome": "REFUSED"})),
                         ["REFUSAL"])
        self.assertIn("REFUSAL", self.codes(span([], None)))

    def test_instrument_fault(self):
        self.assertIn("INSTRUMENT_FAULT", self.codes(span([leg(1)], meter={**METER, "bad_polls": 2})))
        self.assertIn("INSTRUMENT_FAULT", self.codes(span([leg(1)], meter={})))
        self.assertIn("INSTRUMENT_FAULT", self.codes(span([leg(1)], {**OK_RESULT, "fault": True})))

    def test_three_contaminated_redos(self):
        legs = [leg(1, contaminated_redos=1), leg(2, contaminated_redos=1)]
        self.assertEqual(self.codes(span(legs)), [])
        legs.append(leg(3, contaminated_redos=1))
        self.assertEqual(self.codes(span(legs)), ["CONTAMINATED_REDOS"])
        rules = {**RULES, "contaminated_redos_scope": "campaign"}
        self.assertEqual(self.codes(span([leg(4, contaminated_redos=1)]), [span(legs[:2])], rules), ["CONTAMINATED_REDOS"])

    def test_band_unreachable_twice(self):
        legs = [leg(1, band_reached=False), leg(2, start_band="warm", band_reached=False)]
        self.assertEqual(self.codes(span(legs)), [])
        legs.append(leg(3, band_reached=False))
        self.assertEqual(self.codes(span(legs)), ["BAND_UNREACHABLE"])

    def test_leg_over_one_and_a_half_times(self):
        self.assertEqual(self.codes(span([leg(1, wall_s=2250.0)])), [])
        self.assertEqual(self.codes(span([leg(1, wall_s=2251.0)])), ["LEG_OVERTIME"])
        self.assertEqual(self.codes(span([leg(1, wall_s=None)])), ["LEG_OVERTIME"])


class Desk(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.inp, self.out = self.root / "in", self.root / "out"
        (self.inp / "span").mkdir(parents=True)
        (self.inp / "span" / "meter.json").write_text(json.dumps(METER))
        (self.inp / "span" / "result.json").write_text(json.dumps(OK_RESULT))

    def tearDown(self):
        self.tmp.cleanup()

    def write_leg(self, doc):
        d = self.inp / "legs" / doc["leg_id"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "leg_summary.json").write_text(json.dumps(doc))

    def build(self, adapter="leg-summary-v1"):
        return desk.build_desk(plan_id="cq-ct-s01-a1", input_dir=self.inp, out_dir=self.out, adapter=adapter,
                               stop_rules=RULES)

    def test_table_and_no_stops(self):
        for i in (1, 2):
            self.write_leg({**leg(i), "g0_s": 114.0, "g0_outcome": "released", "attempts": 1})
        summary, stops = self.build()
        self.assertEqual(stops, [])
        text = (self.out / "JOURNAL-TABLE.md").read_text()
        self.assertIn("| L001 | mid | True | 114.0 | released | 1200.0 | 1500.0 | 0.80 |", text)
        self.assertEqual(json.loads((self.out / "stops.json").read_text()), [])

    def test_overtime_leg_is_flagged_and_stops(self):
        self.write_leg(leg(1, wall_s=3000.0))
        _, stops = self.build()
        self.assertEqual([s["code"] for s in stops], ["LEG_OVERTIME"])
        self.assertIn("**over**", (self.out / "JOURNAL-TABLE.md").read_text())

    def test_planted_energy_value_refuses_and_writes_nothing(self):
        self.write_leg({**leg(1), "energy_j": 1234.56789})
        with self.assertRaises(desk.DeskRefusal):
            self.build()
        self.assertFalse(self.out.exists())

    def test_planted_slot_or_unknown_key_refuses(self):
        for planted in ({"slots": [1]}, {"gpu_power_w": 3.0}, {"prompt_text": "hello"}, {"surprise": 1}):
            self.write_leg({**leg(1), **planted})
            with self.assertRaises(desk.DeskRefusal):
                self.build()

    def test_only_allowlisted_files_are_opened(self):
        with self.assertRaises(desk.DeskRefusal):
            desk._json(self.inp / "span" / "energy.json", "leg-summary-v1")

    def test_r1_adapter_projects_journals_and_never_prints_token_ids(self):
        run = self.inp / "D_bank_test"
        run.mkdir()
        events = [{"event_type": "phase_end", "phase": "align_thermal_gate",
                   "metadata": {"kind": "G0", "turn": 0, "duration_s": 114.2, "outcome": "released",
                                "energy_j": 987.654321}},
                  {"event_type": "phase_end", "phase": "align_thermal_hold",
                   "metadata": {"kind": "H", "turn": 1, "duration_s": 30.0, "outcome": "deadman"}}]
        (run / "align_runtime_events.jsonl").write_text("\n".join(json.dumps(e) for e in events))
        turns = [{"turn": 0, "generation": {"prefill_tokens": 19500, "output_token_ids": [424242] * 7,
                                            "finish_reason": "length"}}]
        (run / "align_turns.jsonl").write_text(json.dumps(turns[0]))
        (run / "energy.jsonl").write_text('{"energy_j": 1}')
        _, stops = self.build("r1-journal-v1")
        text = (self.out / "JOURNAL-TABLE.md").read_text()
        self.assertIn("| D_bank_test | 1 | 114.2 | 0.0 | 1 | 30.0 | none | H@1 | 7 | length |", text)
        for planted in ("987.654321", "424242"):
            self.assertNotIn(planted, text)
            self.assertNotIn(planted, (self.out / "desk_summary.json").read_text())


class QuietLock(unittest.TestCase):
    def test_lock_is_exclusive_and_removed(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "AIR-QUIET.lock"
            with desk.air_quiet_lock("t", path):
                self.assertIn(f"pid={os.getpid()}", path.read_text())
                with self.assertRaises(desk.LockBusy):
                    with desk.air_quiet_lock("u", path):
                        pass
            self.assertFalse(path.exists())

    def test_stale_lock_is_not_stolen(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "AIR-QUIET.lock"
            path.write_text("label=old pid=999999 start=x\n")
            with self.assertRaises(desk.LockBusy) as ctx:
                with desk.air_quiet_lock("t", path):
                    pass
            self.assertIn("stale", str(ctx.exception))
            self.assertTrue(path.exists())


if __name__ == "__main__":
    unittest.main()
