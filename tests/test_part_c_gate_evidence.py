"""Synthetic gate evidence for the Part C cited rebind."""
from contextlib import contextmanager
from pathlib import Path
import sys
from types import ModuleType
import unittest
from unittest.mock import patch

from scripts import align_r1_part_c as pc

from scripts.align_r1_part_c import g1_records, gate_durations


def interval(kind, turn, seconds, outcome="released"):
    return {"kind": kind, "turn": turn, "outcome": outcome,
            "start_ns": 1_000_000_000, "end_ns": int((1 + seconds) * 1_000_000_000),
            "duration_s": seconds}


class PartCGateEvidenceTests(unittest.TestCase):
    def test_every_later_admitted_turn_needs_its_own_release(self):
        turns = [{"index": i} for i in range(3)]
        g0, g1, g2 = interval("G0", 0, 10), interval("G1", 1, 20), interval("G1", 2, 30)
        self.assertTrue(g1_records(turns, [g0, g1, g2])["pass"])
        for rows in ([g0], [g0, g1, g1, g2], [g0, g1, {**g2, "turn": 3}],
                     [g0, g1, {**g2, "outcome": "unobserved"}]):
            with self.subTest(rows=rows):
                self.assertFalse(g1_records(turns, rows)["pass"])
        self.assertTrue(g1_records(turns[:1], [g0])["pass"])

    def test_duration_reconciles_to_monotonic_bounds_before_a_total(self):
        g0, g1, hold = interval("G0", 0, 10), interval("G1", 1, 20), interval("H", 1, 30)
        self.assertEqual(gate_durations([g0, g1, hold]), {"pass": True, "errors": [], "total_s": 60})
        for wrong in (0, -1, float("nan"), float("inf"), "20", None):
            with self.subTest(duration=wrong):
                evidence = gate_durations([g0, {**g1, "duration_s": wrong}, hold])
                self.assertFalse(evidence["pass"])
                self.assertIsNone(evidence["total_s"])
        self.assertFalse(gate_durations([g0, {**g1, "end_ns": None}, hold])["pass"])


@contextmanager
def evaluator_world():
    """Supply the two W1-only imports absent on main; keep every Part C check real.

    These doubles accept only this world's clean inputs (three admitted turns,
    fresh stamps). On W1 use the actual helpers instead. Neither double decides
    whether timeout or interval evidence is acceptable.
    """
    modules = {}
    try:
        from scripts.align_r1_rehearsal import turn_check
    except ModuleNotFoundError:
        rehearsal = ModuleType("scripts.align_r1_rehearsal")

        def turn_check(count, x7, flags, minimum):
            assert type(count) is int and count >= minimum
            assert type(x7) is bool and isinstance(flags, list)
            return True, {"own_stop": not x7 and not flags, "why": ", ".join(flags) or None}

        rehearsal.turn_check = turn_check
        modules[rehearsal.__name__] = rehearsal
    try:
        from joulewise.align.apple.rl145_prints import stamp_fresh
    except ModuleNotFoundError:
        prints = ModuleType("joulewise.align.apple.rl145_prints")
        prints.FRESH_STAMP_S = 2.0  # RL-152 section 1.6, the existing evaluator constant.

        def stamp_fresh(age):
            assert isinstance(age, (int, float)) and -2.0 <= age <= 2.0
            return True

        prints.stamp_fresh = stamp_fresh
        modules[prints.__name__] = prints
    with patch.dict(sys.modules, modules):
        yield


def clean_facts(*, contrast=False):
    """Production fact shape: three admissions, no holds, readable flags and G0/G1."""
    status = {"os_level": 0, "pm_state": "Nominal", "pm_age_s": 0.5}
    return {
        "turns": [{"index": i, "decode_tokens": 1500,
                   "first_reading_after_start": dict(status)} for i in range(3)],
        "intervals": [{**interval(kind, i, 20), "release_status": dict(status)}
                      for i, kind in enumerate(("G0", "G1", "G1"))],
        "t_dead_s": 1000.0, "x7": False, "episode_flags": [],
        "role": "x-g" if contrast else "d-bank",
    }


STEP = {"g0_outcome": "released", "g0_wait_s": 20.0,
        "release": {"fast_c": 35.4, "slow_c": 35.4},
        "reference": {"fast_c": 35.0, "slow_c": 35.0},
        "slope_c_per_min": 0.05}


def evaluate_world(*, d_bank=None, x_g=None, step_d=STEP, **kwargs):
    with evaluator_world():
        return pc.evaluate(
            step_d=step_d,
            d_bank=clean_facts() if d_bank is None else d_bank,
            n_chunk=4096, x_g=clean_facts(contrast=True) if x_g is None else x_g, **kwargs)


class PartCEvaluatorTimeoutTests(unittest.TestCase):
    def test_flag_only_timeout_on_next_unadmitted_turn_fails(self):
        # The workload waits for G1 before admitting the next turn. The three
        # earlier admissions and their G1s are valid; attempted turn 3 timed out,
        # but its interval row was lost. Only the episode flag records it.
        for role in ("d_bank", "x_g"):
            with self.subTest(role=role):
                facts = clean_facts(contrast=role == "x_g")
                facts["episode_flags"] = ["thermal.gate_timeout:3"]
                result = evaluate_world(**{role: facts})
                self.assertFalse(result["pass"])
                self.assertEqual(result["verdict"], "other_failure")
                check = (result["lines"][role] if role == "x_g" else
                         result["lines"]["d_bank_mechanics"]["checks"]["no_g1_timeout"])
                self.assertFalse(check["pass"])
                self.assertIn("thermal.gate_timeout:3", check["gate_timeout_flags"])

    def test_clean_three_admission_world_still_passes(self):
        result = evaluate_world()
        self.assertTrue(result["pass"], result)
        self.assertEqual(result["verdict"], "pass")
        # X_G's explicitly permitted unobserved outcome also stays permitted.
        contrast = clean_facts(contrast=True)
        contrast["intervals"][1]["outcome"] = "unobserved"
        self.assertTrue(evaluate_world(x_g=contrast)["pass"])

    def test_interval_timeout_and_absent_g1_evidence_fail(self):
        for role in ("d_bank", "x_g"):
            for damage in ("timeout", "missing"):
                with self.subTest(role=role, damage=damage):
                    facts = clean_facts(contrast=role == "x_g")
                    if damage == "timeout":
                        facts["intervals"][-1]["outcome"] = "timeout"
                    else:
                        facts["intervals"].pop()
                    result = evaluate_world(**{role: facts})
                    self.assertFalse(result["pass"])
                    check = (result["lines"][role] if role == "x_g" else
                             result["lines"]["d_bank_mechanics"]["checks"]["no_g1_timeout"])
                    self.assertFalse(check["pass"])
                    self.assertEqual(check["g1_timeout_turns"] if damage == "timeout" else
                                     check["missing_g1_turns"], [2])

    def test_bare_timeout_flag_is_not_lost(self):
        for role in ("d_bank", "x_g"):
            with self.subTest(role=role):
                facts = clean_facts(contrast=role == "x_g")
                facts["episode_flags"] = ["thermal.gate_timeout"]
                self.assertFalse(evaluate_world(**{role: facts})["pass"])


class PartCEvidenceReconciliationTests(unittest.TestCase):
    def test_failure_in_either_flag_source_or_later_interval_fails_both_roles(self):
        for role in ("d_bank", "x_g"):
            for source, flag in (("runtime", "thermal.gate_timeout:3"),
                                 ("runtime", "episode.deadman:3"),
                                 ("episode", "episode.deadman:3"),
                                 ("thermal", "thermal.gate_timeout:3"),
                                 ("interval", None)):
                with self.subTest(role=role, source=source, flag=flag):
                    facts = clean_facts(contrast=role == "x_g")
                    facts["runtime"] = {"admitted_turns": 3, "episode_flags": []}
                    if source == "interval":
                        facts["intervals"].append(interval("G1", 3, 20, outcome="deadman"))
                    elif source == "runtime":
                        facts["runtime"]["episode_flags"] = [flag]
                    else:
                        facts[f"{source}_flags"] = [flag]
                    self.assertEqual(evaluate_world(**{role: facts})["verdict"], "other_failure")

    def test_admissions_count_cannot_be_reconciled_to_truncated_turns(self):
        for role in ("d_bank", "x_g"):
            with self.subTest(role=role):
                facts = clean_facts(contrast=role == "x_g")
                facts["runtime"] = {"admitted_turns": 4, "episode_flags": []}
                self.assertEqual(evaluate_world(**{role: facts})["verdict"], "other_failure")

    def test_runtime_gate_waits_cannot_disagree_with_the_bundle(self):
        for role in ("d_bank", "x_g"):
            with self.subTest(role=role):
                facts = clean_facts(contrast=role == "x_g")
                facts["runtime"] = {"admitted_turns": 3, "g0_outcome": "released", "g0_wait_s": 20,
                                    "deadman": {"T_dead_s": 1000}, "gate_waits_s": {"G0": [20], "G1": [20, 20], "H": []}}
                self.assertTrue(evaluate_world(**{role: facts})["pass"])
                facts["runtime"]["gate_waits_s"]["G1"][1] = 30
                self.assertEqual(evaluate_world(**{role: facts})["verdict"], "other_failure")

    def test_runtime_and_bundle_duty_budgets_are_reported_and_must_match(self):
        facts = clean_facts()
        facts["runtime"] = {"admitted_turns": 3, "deadman": {"T_dead_s": 2000.0}}
        result = evaluate_world(d_bank=facts)
        self.assertEqual(result["verdict"], "other_failure")
        budget = result["lines"]["d_bank_mechanics"]["checks"]["duty_budget"]
        self.assertEqual((budget["runtime_s"], budget["bundle_s"]), (2000.0, 1000.0))

    def test_step_d_g0_interval_must_agree_with_summary_and_bounds(self):
        good = {**interval("G0", 0, 20), **{k: STEP[k] for k in ("release", "reference", "slope_c_per_min")}}
        for damage in ({"outcome": "timeout"}, {"end_ns": 1_202_000_000_000},
                       {"end_ns": 0}, {"duration_s": 19, "end_ns": 20_000_000_000}):
            with self.subTest(damage=damage), patch.object(pc, "facts_from_bundle",
                                                          return_value={"intervals": [{**good, **damage}]}):
                step = pc.step_d_facts(Path("/synthetic"), STEP)
                self.assertEqual(evaluate_world(step_d=step)["verdict"], "other_failure")
        with patch.object(pc, "facts_from_bundle", return_value={"intervals": [good]}):
            self.assertTrue(evaluate_world(step_d=pc.step_d_facts(Path("/synthetic"), STEP))["pass"])

    def test_step_d_requires_finite_nonnegative_wait_and_finite_release_facts(self):
        cases = ({"g0_wait_s": -1}, {"g0_wait_s": float("nan")}, {"g0_wait_s": True},
                 {"reference": {"fast_c": float("inf"), "slow_c": 35.0}},
                 {"slope_c_per_min": float("nan")})
        for damage in cases:
            with self.subTest(damage=damage):
                self.assertEqual(evaluate_world(step_d={**STEP, **damage})["verdict"], "other_failure")
