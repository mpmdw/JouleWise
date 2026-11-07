"""LEAD-RULINGS-2 round 7, science lane: R7-1 (gated-block order), R7-2 (the
1,200 s R1 G0 timeout, every G0 wait recorded, the R1-derived G0_cap_W1),
R7-12 (the X-G fallback) and R7-13 (alias groups), on the R1 driver, the
runtime and their contract. Synthetic only: no model, sensor, sudo or host
setting is touched.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.apple import r1_runtime as rt
from joulewise.align.apple import r1_runtime_contract as contract
from joulewise.align.apple import thermal_gates
from scripts import align_r1_rehearsal as r1
from tests.align import test_r1_rehearsal as base

FakeWorld, completed = base.FakeWorld, base.completed
BANK, SPAM_A, SPAM_B, XG = ("D_bank_benign_s1_gated_held", "D_spam_benign_s1_gated_held_a",
                            "D_spam_benign_s1_gated_held_b", "X_G_contrast")
ROOT = Path(__file__).resolve().parents[2]


class _World(unittest.TestCase):
    setUp = base.Round5RulingTests.setUp
    run_world = base.Round5RulingTests.run_world


class GatedOrderTests(_World):
    """R7-1: D_bank, D_spam a, D_spam b, X-G after the R + 0 C planning turn."""

    def test_phase_table_runs_bank_then_the_replay_pair_then_x_g(self):
        for include_4bit in (False, True):
            names = [row[0] for row in r1.phase_plan(include_4bit)]
            start = names.index("planning_turn_R_plus_0C")
            self.assertEqual(names[start + 1:start + 5], [BANK, SPAM_A, SPAM_B, XG])
        self.assertEqual([name for name, _ in r1.GATED_D_RUNS], [BANK, SPAM_A, SPAM_B])
        self.assertEqual(r1.REPLAY_PAIR, (SPAM_A, SPAM_B))

    def test_both_replay_runs_follow_a_full_gated_d_episode(self):
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld()
            result, registration = self.run_world(td, world)
            ran = [name for _, name, _ in world.invocations]
            start = ran.index("planning_turn_R_plus_0C")
            self.assertEqual(ran[start + 1:start + 5], [BANK, SPAM_A, SPAM_B, XG])
            follows = {row["run"]: row["follows_d_turn"] for row in registration["deadman_budget"]}
            # The replay pair's predecessors are matched: each a gated, held D run.
            self.assertEqual(follows, {BANK: "planning_turn_R_plus_0C", SPAM_A: BANK, SPAM_B: SPAM_A})
            self.assertEqual(registration["x_g"]["follows_d_turn"], SPAM_B)   # W1's D -> X transition
            self.assertEqual([row["run"] for row in registration["deadman_budget"]], [BANK, SPAM_A, SPAM_B])


class G0TimeoutTests(_World):
    """R7-2: one config constant, 1,200 s, for the gated runs, X-G and the R6-2 calibration segments."""

    def test_the_r1_g0_timeout_is_one_runtime_config_constant(self):
        self.assertEqual(r1.runtime_g0_timeout_s(None), 1200)
        config = json.loads(r1.runtime_config_path(None).read_text())
        self.assertEqual(rt.g0_timeout_s(config), 1200)
        for bad in (None, 599, 1201, True, float("nan"), "1200"):
            with self.subTest(bad=bad), self.assertRaises(rt.Refused):
                rt.g0_timeout_s(dict(config, g0_timeout_s=bad))
        # Only the gated runs, X-G, step-d and the designed start states arm it.
        self.assertEqual(set(rt.G0_TIMEOUT_KINDS),
                         {"step-d", "x-g", *contract.GATED_D_KINDS, *contract.PLANNING_KINDS})
        for kind in ("step-30b", "d-4bit", "g0-release-soak", *contract.HIGH_POWER_KINDS):
            self.assertNotIn(kind, rt.G0_TIMEOUT_KINDS)

    def test_a_runtime_config_without_the_timeout_refuses_at_t0(self):
        with tempfile.TemporaryDirectory() as td:
            config = json.loads(r1.runtime_config_path(None).read_text())
            del config["g0_timeout_s"]
            path = Path(td) / "r1_runtime.json"
            path.write_text(json.dumps(config))
            world = FakeWorld()
            result, registration = self.run_world(td, world, expected=3, runtime=["fake", "--config", str(path)])
            self.assertIn("g0_timeout_s", result["error"])
            self.assertIsNone(registration)
            self.assertFalse([c for c in world.calls if "--r1-kind" in c])
            self.assertNotIn(r1.PowerModeGuard.HIGH, world.calls)

    def test_a_runtime_config_that_overrides_the_committed_timeout_refuses_at_t0(self):
        # Sol critique: the kit re-derives G0_cap_W1 with the committed value.
        with tempfile.TemporaryDirectory() as td:
            config = json.loads(r1.runtime_config_path(None).read_text())
            config["g0_timeout_s"] = 900
            path = Path(td) / "r1_runtime.json"
            path.write_text(json.dumps(config))
            world = FakeWorld()
            result, registration = self.run_world(td, world, expected=3, runtime=["fake", "--config", str(path)])
            self.assertIn("differs from the committed", result["error"])
            self.assertIsNone(registration)
            self.assertFalse([c for c in world.calls if "--r1-kind" in c])

    def test_gate_policies_carry_the_timeout_only_for_its_kinds(self):
        sensors = {"s_fast": "TC0P", "s_slow": "TG0P", "fan_keys": [], "r0_sha256": "a" * 64}
        bands = {"delta_fast_c": 8.0, "delta_slow_c": 1.0}
        policy = rt.gate_policy(sensors, bands, turn_cap_s=120, chunk_tokens=256, heavy=True, per_turn=True,
                                g0_cap_s=1200)
        self.assertEqual(policy["g0_cap_s"], 1200)
        self.assertNotIn("g0_cap_s", rt.gate_policy(sensors, bands, turn_cap_s=120, chunk_tokens=256,
                                                    heavy=True, per_turn=True))
        config = json.loads(r1.runtime_config_path(None).read_text())
        for kind, expected in (("step-d", 1200), ("x-g", 1200), ("d-bank-benign-s1", 1200),
                               ("d-planning-turn-r-plus-0c", 1200), ("step-30b", None),
                               ("high-power-aba-b", None), ("d-4bit", None)):
            segment = rt.Segment.__new__(rt.Segment)
            segment.kind, segment.config = kind, config
            self.assertEqual(segment.g0_cap_s, expected, kind)
            self.assertEqual(segment.armed_g0_cap_s, expected or thermal_gates.G0_CAP_DEFAULT_S, kind)

    def test_step_d_and_the_designed_states_are_bounded_with_the_timeout(self):
        # R7-2 timeout, and (R8-4) the re-armed member's start-up and close:
        # 1,750 + 1.13544 x 1,580 + 120 = 3,663.9952 s around the deadman.
        member = 1750 + 1.13544 * 1580 + 120
        table = r1.segment_bounds(1200, 1580)
        # Round-8 disposition D8-3: step-30b takes the same construction with
        # the 600 s G0 cap it keeps (R7-2): 3,663.9952 + 600 + 300 + 600.
        self.assertAlmostEqual(table["step-30b"], member + 600 + 300 + 600)
        self.assertAlmostEqual(table["step-30b"], 5163.9952)
        self.assertAlmostEqual(r1.segment_bounds(600, 1580)["step-30b"], table["step-30b"])  # not the R1 timeout
        self.assertAlmostEqual(table["step-d"], member + 1200 + 300 + 600)
        for o in (0, 2, 4):
            self.assertAlmostEqual(table[f"d-planning-turn-r-plus-{o}c"], member + 900 + 1200)
        self.assertAlmostEqual(r1.segment_bounds(600, 1580)["step-d"], member + 600 + 300 + 600)

    def test_night_worst_case_with_the_round8_bounds(self):
        # R7-2: +600 s on step-d and each designed state; R8-4: + (3,663.9952
        # - 1,800) s more on each of the four (4 x 1,863.9952 = 7,455.98 s);
        # D8-3: + 1,863.9952 s more on step-30b (5,163.9952 - 3,300).
        value = r1.night_worst_case_s(["fake-runtime"])
        self.assertEqual(value["g0_timeout_s"], 1200)
        self.assertEqual(value["redo_release_s"], 665)
        self.assertAlmostEqual(value["no_redo_s"], 54342.9664 + 1863.9952, places=3)
        self.assertAlmostEqual(value["no_redo_s"], 56206.96, places=1)
        self.assertAlmostEqual(value["with_one_batch_wait_s"], 61606.96, places=1)
        self.assertAlmostEqual(value["r6_2_retry_max_s"], 4 * (1500 + 5763.9952))   # step-30b takes no R6-2 retry
        self.assertAlmostEqual(value["with_retries_and_one_batch_wait_s"], 90662.94, places=1)


class G0CapW1Tests(unittest.TestCase):
    """R7-2/R7-12: G0_cap_W1 = clamp(ceil(1.25 x max wait), 600 s, 1,200 s)."""

    @staticmethod
    def rows(waits, outcomes=None):
        outcomes = outcomes or {}
        return [{"run": run, "g0_outcome": outcomes.get(run, "released"), "phases_s": {"G0": wait}}
                for run, wait in waits.items()]

    def cap(self, d=(120.0, 300.0, 500.0), x=400.0, outcomes=None, x_g=None):
        x_g = x_g or {"status": "measured", "g0_outcome": "released", "g0_wait_s": x}
        return r1.w1_g0_cap(self.rows(dict(zip((BANK, SPAM_A, SPAM_B), d)), outcomes), x_g, 1200.0)

    def test_rule(self):
        value = self.cap()
        self.assertEqual((value["max_g0_s"], value["value_s"], value["x_g_fallback"]), (500.0, 625, False))
        self.assertEqual(value["waits_s"], {BANK: 120.0, SPAM_A: 300.0, SPAM_B: 500.0, XG: 400.0})
        self.assertEqual(self.cap(d=(10.0, 20.0, 30.0), x=40.0)["value_s"], 600)        # floor
        self.assertEqual(self.cap(d=(10.0, 20.0, 1000.0))["value_s"], 1200)             # ceiling
        self.assertEqual(self.cap(d=(10.0, 20.0, 30.0), x=900.4)["value_s"], 1126)      # X-G counts, ceil
        self.assertEqual(type(self.cap()["value_s"]), int)

    def test_an_unreleased_gated_g0_counts_at_the_full_timeout(self):
        for outcome in ("timeout", "deadman", "unobserved"):
            value = self.cap(d=(100.0, 100.0, 700.0), outcomes={SPAM_B: outcome})
            self.assertEqual((value["waits_s"][SPAM_B], value["value_s"], value["censored"]), (1200.0, 1200, [SPAM_B]))

    def test_an_inconclusive_x_g_falls_back_to_the_timeout(self):
        # R7-12: recorded, never a refusal on that alone.
        for x_g in ({"status": "inconclusive", "g0_outcome": "released", "g0_wait_s": 50.0},
                    {"status": "inconclusive", "g0_outcome": "timeout", "g0_wait_s": 1200.0}):
            value = self.cap(d=(10.0, 20.0, 30.0), x_g=x_g)
            self.assertEqual((value["x_g_fallback"], value["waits_s"][XG], value["value_s"]), (True, 1200.0, 1200))
            self.assertEqual(value["censored"], [] if x_g["g0_outcome"] == "released" else [XG])

    def test_registration_records_the_cap_and_every_g0_wait(self):
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld(g0_waits={BANK: 200.0, SPAM_A: 350.0, SPAM_B: 640.0, XG: 300.0},
                              calibration_g0_timeouts={"step-d": 1})
            result, registration = _World.run_world(self, td, world)
            cap = registration["g0_cap_w1"]
            self.assertEqual((cap["value_s"], cap["max_g0_s"], cap["x_g_fallback"]), (800, 640.0, False))
            self.assertEqual(cap["r1_g0_timeout_s"], 1200.0)
            self.assertEqual(registration["x_g"]["g0_wait_s"], 300.0)
            self.assertEqual({row["run"]: row["g0_outcome"] for row in registration["deadman_budget"]},
                             {BANK: "released", SPAM_A: "released", SPAM_B: "released"})
            waits = registration["g0_waits"]
            segments = [row["segment"] for row in waits]
            # The timed-out first step-d attempt and its accepted retry are both recorded.
            self.assertEqual(segments.count(r1.STEP_D_NAME), 2)
            first = next(row for row in waits if row["segment"] == r1.STEP_D_NAME)
            self.assertEqual((first["g0_outcome"], first["g0_wait_s"]), ("timeout", 1200.0))
            self.assertTrue(first["output_dir"].endswith(r1.STEP_D_NAME + r1.G0_TIMEOUT_SUFFIX))
            for name in (BANK, SPAM_A, SPAM_B, XG, "planning_turn_R_plus_4C"):
                self.assertIn(name, segments)
            # Every G0-bearing segment is recorded, each with the cap it ran under,
            # and a release precedes the member it released.
            for name in ("step_30b", "high_power_A1", "high_power_A1.g0_release"):
                self.assertIn(name, segments)
            self.assertLess(segments.index("high_power_A1.g0_release"), segments.index("high_power_A1"))
            caps = {row["segment"]: row["g0_timeout_s"] for row in waits}
            self.assertEqual(caps["step_30b"], 600.0)
            self.assertTrue(all(caps[name] == 1200.0 for name in (BANK, SPAM_A, SPAM_B, XG, r1.STEP_D_NAME)))
            for kind in ("step-30b", "d-4bit", "g0-release-soak", *contract.HIGH_POWER_KINDS):
                self.assertIn("g0_wait_s", contract.required_fields(kind, quiet=True), kind)


class AliasGroupTests(unittest.TestCase):
    """R7-13: aliased keys are one thermometer; the classification records them."""

    @staticmethod
    def rows(series):
        n = len(next(iter(series.values())))
        return [{"started": {"monotonic_ns": i * rt.NS}, "values": {"sensors": {k: v[i] for k, v in series.items()},
                                                                    "errors": {}}} for i in range(n)]

    def test_identical_series_form_one_group(self):
        series = {"TCMb": [40.0, 41.0, None, 42.5], "TVD0": [40.0, 41.0, None, 42.5],
                  "Tf24": [30.0, 30.5, 31.0, 31.5], "Tf2D": [30.0, 30.5, 31.0, 31.5], "Tf2E": [30.0, 30.5, 31.0, 31.5],
                  "TaRT": [30.0, 30.5, 31.0, 31.6],            # differs in one row: not an alias
                  "Tdead": [None, None, None, None], "Tnone": [None, None, None, None]}   # never read
        groups = rt.alias_groups(sorted(series), self.rows(series))
        self.assertEqual(groups, [["TCMb", "TVD0"], ["Tf24", "Tf2D", "Tf2E"]])
        self.assertEqual(rt.alias_groups(["TaRT", "Tf24"], self.rows(series)), [])

    def test_classification_records_alias_groups_inside_its_digest(self):
        series = {"TC0P": [40.0, 41.0, 42.0], "TG0P": [35.0, 35.1, 35.2], "TCMb": [36.0, 36.5, 37.0],
                  "TVD0": [36.0, 36.5, 37.0]}
        inventory = {"keys": [{"key": key} for key in series], "complete": True}
        ranked = {"rule": "stub", "s_fast": "TC0P", "s_slow": "TG0P", "die_candidates": ["TC0P"],
                  "heatsink_candidates": ["TG0P"], "record_only": [], "ranking": []}
        with patch("joulewise.align.apple.smc_enumeration.rank", lambda capture, stage: ranked):
            result = rt.classify_step(inventory, self.rows(series), prefill_ns=1 * rt.NS, last_decode_ns=2 * rt.NS,
                                      quiet_s=1, recovery_s=0.5, r0_sensors={"s_fast": "TC0P", "s_slow": "TG0P"})
        self.assertEqual(result["alias_groups"], [["TCMb", "TVD0"]])
        self.assertIn("R7-13", result["alias_rule"])
        body = {k: v for k, v in result.items() if k != "classification_sha256"}
        self.assertEqual(result["classification_sha256"], hashlib.sha256(rt.canonical(body).encode()).hexdigest())

    def test_the_driver_registers_the_alias_groups(self):
        self.assertIn("thermometry.alias_groups", contract.required_fields("step-d", quiet=True))
        with tempfile.TemporaryDirectory() as td:
            _, registration = _World.run_world(self, td, FakeWorld())
            self.assertEqual(registration["thermometry"]["D"]["alias_groups"], [["TCMb", "TVD0"]])


class ContractTests(unittest.TestCase):
    def test_every_g0_wait_is_a_contract_field(self):
        for kind in ("step-d", "x-g", *contract.GATED_D_KINDS, *contract.PLANNING_KINDS):
            fields = contract.required_fields(kind, quiet=True)
            self.assertIn("g0_wait_s", fields, kind)
            self.assertIn("g0_timeout_s", fields, kind)
        for kind in contract.G0_INCONCLUSIVE_KINDS:
            fields = contract.required_fields(kind, quiet=True, inconclusive=True)
            self.assertIn("g0_wait_s", fields, kind)
        doc = (ROOT / "docs/align/r1_runtime_contract.md").read_text()
        for name in ("`g0_timeout_s`", "`g0_wait_s`", "`r1_slots.g0_cap_w1`", "`r1_slots.g0_waits`", "`alias_groups`",
                     "`x_g_fallback`", "R7-1", "R7-2", "R7-12", "R7-13"):
            self.assertIn(name, doc)


if __name__ == "__main__":
    unittest.main()
