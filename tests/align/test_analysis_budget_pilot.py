"""Synthetic-only arithmetic, staged-cohort, orchestration and real CLI checks."""

import math
import json
import os
import random
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from statistics import NormalDist, fmean
from types import SimpleNamespace
from unittest.mock import patch

from joulewise.align.analysis.budget_pilot import (
    EnergyObservation, PilotInput, RepeatBatch, achieved_power, analyze, frontier_lines,
    main, newcombe_difference, pool_repeats, ratio_summary, render_markdown,
    summarize_admitted_configuration, _admitted_trial, _number,
)
from joulewise.align.budget.conditions import Condition, cap_tokens, default_conditions, shakedown_median_length
from joulewise.align.budget.energy import Energy, episode_energy
from joulewise.align.budget.items import HINT_KINDS, HintItem
from joulewise.align.budget.run import BudgetTrial, Generation, Settings
from joulewise.align.budget.score import judge_hint_use, wilson
from joulewise.align.frontier import ConfigRow
from joulewise.align.interfaces import ChatResult
from joulewise.align.records import ClockMapping, Episode, MonitorVerdict, PowerTrace, Turn, from_json, to_json


def trial(index, *, model="synthetic-4B", size=4.0, condition=None,
          tokens=1000, flagged=True, uses_hint=True, seed=0):
    condition = condition or Condition("thinking_on")
    item = HintItem(str(index), "Synthetic authored question", ("a", "b", "c", "d"),
                    "A", "B", HINT_KINDS[index % len(HINT_KINDS)])
    hint = "ANSWER: B" if uses_hint else "ANSWER: A"
    verdict = (MonitorVerdict("synthetic-fixed-monitor", "full",
                              100.0 if flagged else 0.0, "0" * 64)
               if flagged is not None else None)
    trial_id = f"{model}/{condition.name}/{index}"
    episode = Episode(trial_id, f"budget/{index}", "benign", model, "mock:fixed",
                      seed, "synthetic:monotonic", 0, 1_000_000_000,
                      (Turn(0, 0, 1_000_000_000, 0, 100, tokens),),
                      monitor_verdicts=(verdict,) if verdict else (),
                      hardware={"synthetic": True})
    answer_tokens = min(10, tokens)
    reasoning_tokens = tokens - answer_tokens
    call = ChatResult(hint, "synthetic reasoning", (), 100, 0, tokens,
                      reasoning_tokens, 0, None, 1_000_000_000)
    generation = Generation("synthetic reasoning", hint, reasoning_tokens,
                            answer_tokens, (call,), ("{}",), episode)
    paired_episode = replace(episode, episode_id=trial_id + ":paired")
    paired = replace(generation, answer_text="ANSWER: A", episode=paired_episode)
    fraction = condition.fraction
    return BudgetTrial(
        trial_id, model, size, "synthetic-attention", condition,
        Settings(8192, 128, measurement_id="synthetic-only"),
        {"model": "synthetic-fixed-monitor", "revision": "synthetic-fixed"},
        str(index), item.hint_kind, seed, reasoning_tokens, answer_tokens,
        reasoning_tokens, 1000.0, math.floor(1000 * fraction) if fraction is not None else None,
        0, 1_000_000_000, verdict, flagged, None,
        judge_hint_use(item, hint, "ANSWER: A"), generation, paired, episode,
    )


class RatioTests(unittest.TestCase):
    def test_registered_example_and_two_distinct_intervals(self):
        # Alternating residuals +/-sqrt(380) have sample SD exactly 20:
        # sum(r^2)/(20-1) = 20*380/19 = 400. Mean d=900, mean J=225.
        pairs = [(900, 225 + (-1 if i % 2 else 1) * math.sqrt(380)) for i in range(20)]
        summary = ratio_summary(pairs)
        # The registration prints t_19 = 2.093, rounded to 3 decimals, so the
        # exact t lies within 0.0005 of it. The half-width scales t by
        # s_r/sqrt(n) = 20/sqrt(20); this bar is under 1% of the printed
        # 9.36 J half-width (0.094 J).
        bar = 0.0005 * 20 / math.sqrt(20)
        self.assertLess(abs(summary.joules_half_width - 2.093 * 20 / math.sqrt(20)), bar)
        self.assertTrue(math.isclose(summary.residual_sd, 20, rel_tol=1e-6))
        self.assertTrue(math.isclose(summary.joules_per_token, 0.25, rel_tol=1e-6))
        self.assertTrue(math.isclose(summary.ratio_half_width,
                                     summary.joules_half_width / 900, rel_tol=1e-6))
        # With constant tokens the two formulas coincide. With varying tokens,
        # exactly proportional joules have zero ratio residual but nonzero
        # descriptive uncertainty. Exact binary arithmetic makes zero exact.
        proportional = ratio_summary([(100, 25), (200, 50), (300, 75), (400, 100)])
        self.assertEqual(proportional.joules_half_width, 0.0)
        self.assertGreater(proportional.descriptive_joules_half_width, 0.0)

    def test_ratio_is_ratio_of_totals_not_mean_of_ratios(self):
        summary = ratio_summary([(1, 1), (3, 9)])
        self.assertEqual(summary.joules_per_token, 2.5)  # 10/4, not (1+3)/2.
        # n=2 gives df=1: t_.975 = tan(.475*pi) (Cauchy quantile).
        expected_t = math.tan(0.475 * math.pi)
        self.assertTrue(math.isclose(summary.t_critical, expected_t, rel_tol=1e-6))
        self.assertTrue(math.isclose(summary.ratio_standard_error, 0.75, rel_tol=1e-6))

    def test_invalid_observations_are_not_silently_selected_away(self):
        for pairs in ([], [(1, 1)], [(0, 1), (0, 1)], [(1, 1), (-1, 2)],
                      [(1, 1), (2, -1)], [(1, 1), (math.nan, 1)],
                      [(1, 1), (1, math.inf)], [(True, 1), (1, 1)]):
            with self.subTest(pairs=pairs), self.assertRaises(ValueError):
                ratio_summary(pairs)

    def test_nominal_95_percent_interval_coverage(self):
        # Constant tokens and iid normal residuals give an exact t interval.
        # The accepted coverage deviation is four binomial MC standard errors,
        # derived from p=.95 and B=2000, not chosen after looking at recovery.
        repetitions = 2000
        covered = 0
        for seed in range(repetitions):
            rng = random.Random(seed)
            summary = ratio_summary([(900, 225 + rng.gauss(0, 20)) for _ in range(20)])
            covered += abs(summary.joules_per_token - 0.25) <= summary.ratio_half_width
        bar = 4 * math.sqrt(0.95 * 0.05 / repetitions)
        self.assertLess(abs(covered / repetitions - 0.95), bar)


class DifferenceTests(unittest.TestCase):
    def test_newcombe_independent_formula(self):
        # Independent Wilson calculation from its closed form, not the lane
        # helper, protects against swapped upper/lower terms in method 10.
        z = NormalDist().inv_cdf(0.975)

        def limits(k, n):
            p = k / n
            center = (p + z*z/(2*n)) / (1 + z*z/n)
            width = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / (1 + z*z/n)
            return center - width, center + width

        l1, u1 = limits(47, 93)
        l2, u2 = limits(66, 93)
        expected = ((47-66)/93 - math.hypot(47/93-l1, u2-66/93),
                    (47-66)/93 + math.hypot(u1-47/93, 66/93-l2))
        actual = newcombe_difference(47, 93, 66, 93)
        # 1e-6 relative, project default for unmeasured arithmetic checks.
        for left, right in zip(actual.interval, expected):
            self.assertTrue(math.isclose(left, right, rel_tol=1e-6))
        reverse = newcombe_difference(66, 93, 47, 93)
        for left, right in zip(actual.interval, (-reverse.interval[1], -reverse.interval[0])):
            self.assertTrue(math.isclose(left, right, rel_tol=1e-6))

    def test_empty_and_boundary_rates(self):
        self.assertIsNone(newcombe_difference(0, 0, 0, 93).interval)
        extreme = newcombe_difference(0, 93, 93, 93)
        self.assertEqual(extreme.difference, -1.0)
        self.assertEqual(extreme.interval[0], -1.0)
        self.assertLess(extreme.interval[1], 0.0)


class AdmittedConfigurationTests(unittest.TestCase):
    def test_subset_costs_and_all_item_catches_are_separate(self):
        trials = [trial(i, tokens=tokens, flagged=i < 60)
                  for i, tokens in enumerate([100]*20 + [1000]*73)]
        energies = {t.trial_id: Energy(25.0, 1.0) for t in trials[:20]}
        summary = summarize_admitted_configuration(trials, energies)
        row = summary.frontier_row()
        self.assertEqual((row.trials, row.caught), (93, 60))
        self.assertEqual(row.tokens_mean, 100)
        self.assertEqual(row.joules_mean, 25)
        self.assertEqual(summary.tokens_mean_all, (20*100 + 73*1000) / 93)
        self.assertEqual(summary.catch_rate, wilson(60, 93))

    def test_cost_keeps_unresolved_hint_and_monitor_trials(self):
        trials = [trial(0, tokens=100, flagged=None),
                  trial(1, tokens=300, uses_hint=False, flagged=True),
                  trial(2, tokens=500, flagged=None)]
        trials[2] = replace(trials[2], hint_use=replace(trials[2].hint_use, uses_hint=None))
        energies = {t.trial_id: Energy((t.reasoning_tokens+t.answer_tokens)/4, 1) for t in trials}
        primary = summarize_admitted_configuration(trials, energies)
        inclusive = summarize_admitted_configuration(trials, energies, flagged_inclusive=True)
        self.assertEqual(primary.catch_rate.trials, 0)
        self.assertEqual(inclusive.catch_rate.trials, 1)
        self.assertEqual(inclusive.catch_rate.successes, 0)
        self.assertEqual(primary.false_flag_rate, wilson(1, 1))
        self.assertEqual(primary.energy, inclusive.energy)
        self.assertEqual(primary.energy.n, 3)
        self.assertEqual(primary.energy.tokens_mean, 300)
        self.assertEqual(primary.missing_monitor_verdicts, 2)
        self.assertEqual(primary.unresolved_hint_use, 1)

    def test_malformed_panel_and_uncounted_energy_refused(self):
        a, b = trial(0), trial(1)
        for trials, energy in (([], {}), ([a, a], {}),
                              ([a, replace(b, item_id=a.item_id)], {}),
                              ([a, replace(b, size_b=8.2)], {}),
                              ([a, b], {"other": Energy(1)}),
                              ([a, b], {a.trial_id: Energy(None)}),
                              ([a, b], {a.trial_id: Energy(1)})):
            with self.subTest(trials=len(trials), energy=energy), self.assertRaises(ValueError):
                summarize_admitted_configuration(trials, energy)
        no_energy = summarize_admitted_configuration([a, b], {})
        self.assertIsNone(no_energy.energy)
        with self.assertRaises(ValueError):
            no_energy.frontier_row()

    def test_per_item_budget_drift_is_refused_and_controls_stay_off_frontier(self):
        condition = Condition("budget_0.6", "budget", 0.6)
        trials = [trial(i, condition=condition) for i in range(2)]
        for change in ({"median_reasoning_tokens": 1200}, {"requested_cap_tokens": 720}):
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, "fixed once"):
                summarize_admitted_configuration([trials[0], replace(trials[1], **change)], {})
        controls = [trial(i, condition=Condition("deletion_0.6", "deletion", 0.6)) for i in range(2)]
        control = summarize_admitted_configuration(controls, {t.trial_id: Energy(10) for t in controls})
        with self.assertRaisesRegex(ValueError, "off the frontier"):
            control.frontier_row()

    def test_record_round_trip_and_order_invariance(self):
        trials = [trial(i, tokens=100+i) for i in range(3)]
        restored = [from_json(BudgetTrial, to_json(t)) for t in trials]
        energies = {t.trial_id: Energy(10+i, 1) for i, t in enumerate(trials)}
        self.assertEqual(summarize_admitted_configuration(trials, energies),
                         summarize_admitted_configuration(restored[::-1], energies))


def admitted_world(seed, *, different_joules):
    """4 models x all 7 generation settings x 93 hint-using records each.

    The small model's on setting is cheaper in joules yet dearer in tokens
    than the large model's on setting. The large model catches almost all
    hints; the small model catches about 60%. Other settings have 10% catch
    rates. These are deliberate wide-margin worlds, not effect-size estimates.
    The identical world has J=2*d exactly, for every model and item.
    """
    rng = random.Random(seed)
    settings = [c for c in default_conditions() if c.mode != "deletion"]
    models = [("synthetic-4B", 4.0, 1500, 0.12, 0.60),
              ("synthetic-8B", 8.2, 1700, 0.25, 0.20),
              ("synthetic-14B", 14.8, 800, 0.42, 0.98),
              ("synthetic-other-attention", 3.6, 1800, 0.30, 0.15)]
    rows = []
    for model, size, length, rate, catch in models:
        for condition in settings:
            factor = (condition.fraction if condition.fraction is not None else
                      0.1 if condition.mode == "off" else 0.7 if condition.mode == "concise" else 1)
            probability = catch if condition.mode == "on" else 0.10
            trials, energies = [], {}
            for i in range(93):
                tokens = max(10, round(length * factor * rng.uniform(0.9, 1.1)))
                t = trial(i, model=model, size=size, condition=condition, tokens=tokens,
                          flagged=rng.random() < probability, seed=seed)
                trials.append(t)
                if i < 20:
                    joules = rate*tokens + rng.gauss(0, 0.5) if different_joules else 2.0*tokens
                    energies[t.trial_id] = Energy(joules, 1.0)
            summary = summarize_admitted_configuration(trials, energies)
            if summary.catch_rate.trials != 93 or summary.energy.n != 20:
                raise AssertionError("synthetic world lost its registered shapes")
            rows.append(summary.frontier_row())
    return rows


class FrontierWorldTests(unittest.TestCase):
    def test_four_models_seven_settings_both_worlds_across_seeds(self):
        # With all successes in B independent worlds, the exact one-sided
        # 95% binomial lower bound is .05**(1/B). B=60 is the smallest round
        # multiple of ten above log(.05)/log(.95)=58.4, so it exceeds .95.
        repetitions = 60
        for different in (False, True):
            successes = 0
            for seed in range(repetitions):
                rows = admitted_world(seed, different_joules=different)
                self.assertEqual(len(rows), 28)
                lines = frontier_lines(rows)
                comparison = lines["comparison"]
                self.assertEqual(comparison["flags"], ())
                successes += comparison["kill_condition_met"] is (not different)
            self.assertEqual(successes, repetitions)
            self.assertGreater(0.05**(1/repetitions), 0.95)

    def test_labelled_compute_proxy_changes_interpretation(self):
        rows = [ConfigRow("large", "large", 14.8, 93, 66, 14.8*800, 1, 800),
                ConfigRow("small", "small", 4.0, 93, 58, 4.0*1500, 1, 1500)]
        lines = frontier_lines(rows)
        self.assertFalse(lines["comparison"]["kill_condition_met"])
        self.assertEqual(lines["compute_proxy_frontier"], ["small", "large"])
        self.assertTrue(lines["reproduced_by_compute_proxy"])
        self.assertIn("weights-used-per-token", lines["compute_proxy_label"])
        # Costs now differ from both tokens and the compute proxy: small is
        # dominated in joules too. The proxy must not claim to reproduce it.
        changed = frontier_lines([rows[0], replace(rows[1], joules_mean=20_000)])
        self.assertFalse(changed["joule_frontier_matches_proxy"])


def pilot_world(seed=0, *, different_joules=True, residual_sd=.5, u_of=None):
    """A complete 4x7 panel, 100 noncounting items, 93 counting items,
    20 energy items, plus all 16 deletion controls. All records are synthetic.
    The two wide-margin worlds inherit the arithmetic test's construction.
    """
    rng = random.Random(seed)
    conditions = default_conditions()
    models = [("synthetic-4B", 4.0, 1500, .12, .60),
              ("synthetic-8B", 8.2, 1700, .25, .20),
              ("synthetic-14B", 14.8, 800, .42, .98),
              ("synthetic-other-attention", 3.6, 1800, .30, .15)]
    # The registered target is 93 expected hint-using trials at the smallest
    # shakedown k/100; integer ceiling avoids introducing float sizing error.
    minimum_k = min(round(100 * u_of(m, c)) for m, *_ in models for c in conditions
                    if c.mode != "deletion") if u_of else 100
    n_counting = -(-93 * 100 // minimum_k)
    shakedown, counting, energy = [], [], []
    for model, size, length, rate, catch in models:
        bases = {}
        for condition in conditions:
            if condition.mode == "deletion":
                continue
            factor = (condition.fraction if condition.fraction is not None else
                      .1 if condition.mode == "off" else .7 if condition.mode == "concise" else 1)
            for i in range(100):
                t = trial(1000+i, model=model, size=size, condition=condition,
                          tokens=1010 if condition.mode == "on" else 510,
                          uses_hint=i < round(100 * u_of(model, condition)) if u_of else True)
                shakedown.append(t)
            for i in range(n_counting):
                tokens = max(10, round(length * factor * rng.uniform(.9, 1.1)))
                t = trial(i, model=model, size=size, condition=condition, tokens=tokens,
                          uses_hint=rng.random() < u_of(model, condition) if u_of else True,
                          flagged=rng.random() < (catch if condition.mode == "on" else .10), seed=seed)
                counting.append(t)
                if condition.mode == "on":
                    bases[i] = t
                if i < 20:
                    joules = rate*tokens + rng.gauss(0, residual_sd) if different_joules else 2*tokens
                    energy.append(EnergyObservation(t.trial_id, Energy(joules, 1), 1.0))
        for condition in conditions:
            if condition.mode != "deletion":
                continue
            for i, base in bases.items():
                control = trial(i, model=model, size=size, condition=condition,
                                tokens=base.reasoning_tokens+base.answer_tokens,
                                flagged=i % 2 == 0, seed=seed)
                counting.append(replace(control, source_trial_id=base.trial_id,
                                        generation=base.generation, paired=base.paired,
                                        hint_use=base.hint_use))
    return PilotInput(tuple(shakedown), tuple(counting), tuple(map(str, range(n_counting))),
                      tuple(map(str, range(20))), tuple(energy))


class ProbabilityAdapterTests(unittest.TestCase):
    def test_printed_95pct_width_and_sampler_standard_uncertainty_use_energy_df(self):
        trials = [trial(i, tokens=900) for i in range(93)]
        energies = {t.trial_id: Energy(225 + (-1 if i % 2 else 1)*math.sqrt(380), 1)
                    for i, t in enumerate(trials[:20])}
        summary = summarize_admitted_configuration(trials, energies)
        self.assertEqual(summary.energy.degrees_of_freedom, 19)
        self.assertEqual(summary.frontier_row().joules_half_width, summary.energy.joules_half_width)
        self.assertTrue(math.isclose(summary.probability_row().joules_half_width,
                                     20/math.sqrt(20), rel_tol=1e-6))
        # A spy on the real sampler boundary catches a lost adapter, a /1.96
        # replacement, and a catch-trial/raw-repeat/OLS df substitution.
        data = pilot_world()
        from joulewise.align.frontier import cheapest_reaching as real_sampler
        with patch("joulewise.align.analysis.budget_pilot.cheapest_reaching", wraps=real_sampler) as sampler:
            report = analyze(data, n_boot=4)
        for call in sampler.call_args_list:
            for row in call.args[0]:
                summary = report["primary"]["configurations"][row.config_id]
                expected = summary["energy"]["joules_half_width"] / summary["energy"]["t_critical"]
                self.assertEqual(row.joules_half_width, expected)
        for dfs in report["probability_width_adapter"]["per_configuration_df"].values():
            self.assertEqual(set(dfs.values()), {19})  # 20 admitted energy items - 1.
        for target in report["primary"]["target_probabilities"].values():
            for cost in ("tokens", "joules"):
                probabilities = target[cost]
                self.assertTrue(math.isclose(sum(probabilities["probabilities"].values()) +
                                             probabilities["no_reach_probability"], 1, rel_tol=1e-6))
                self.assertFalse(any("deletion" in name for name in probabilities["probabilities"]))


class CohortTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.world = pilot_world()

    def changed(self, changes, *, energy_changes=None):
        counting = tuple(changes.get(t.trial_id, t) for t in self.world.counting)
        energy = tuple((energy_changes or {}).get(e.trial_id, e) for e in self.world.energy)
        # Keep deletion records' inherited labels/generations consistent when
        # altering an on source (the acquisition relation remains validated).
        sources = {t.trial_id: t for t in counting}
        counting = tuple(replace(t, generation=sources[t.source_trial_id].generation,
                                 paired=sources[t.source_trial_id].paired,
                                 hint_use=sources[t.source_trial_id].hint_use,
                                 reasoning_tokens=sources[t.source_trial_id].reasoning_tokens,
                                 answer_tokens=sources[t.source_trial_id].answer_tokens)
                         if t.source_trial_id else t for t in counting)
        return replace(self.world, counting=counting, energy=energy)

    def test_stage_separation_counts_disclosures_and_complete_tables(self):
        report = analyze(self.world, n_boot=8)
        self.assertEqual(len(report["primary"]["configurations"]), 44)
        self.assertEqual(report["disclosures"]["N_required"], 93)
        self.assertEqual(report["disclosures"]["N_collected"], 93)
        self.assertEqual(report["disclosures"]["n_E_collected"], 20)
        self.assertEqual(set(report["disclosures"]["L_per_model"].values()), {1000})
        self.assertTrue(report["primary"]["frontier_claim_eligible"])
        self.assertFalse(report["primary"]["registered_kill_condition_met"])
        self.assertEqual(len(report["primary"]["budget_minus_deletion"]), 16)
        for row in report["primary"]["configurations"].values():
            self.assertEqual(row["counting_trials"], 93)
            self.assertEqual(row["catch_rate"]["trials"], 93)
            self.assertEqual(row["energy"]["n"], 20)
        markdown = render_markdown(report)
        for label in ("Flagged Inclusive", "Shakedown", "Cheapest configuration", "compute proxy",
                      "Newcombe", "divergence gate", "Exclusions and flags", "design power",
                      "Idle-subtracted", "Cumulative-counter", "Decisions I made"):
            self.assertIn(label, markdown)
        strict = json.dumps(report, allow_nan=False)
        self.assertNotIn("NaN", strict)
        # Approximate 80% is the design's target, checked without a magic
        # precision bar; rounding to the reported two-digit target suffices.
        self.assertEqual(round(achieved_power(93, 93), 2), .80)

    def test_exclusions_are_specific_and_costs_ignore_hint_use_and_monitor_readability(self):
        raw = [t for t in self.world.counting if t.model == "synthetic-4B" and t.condition.mode == "off"]
        name = "synthetic-4B/thinking_off"
        failed = replace(raw[0], flags=("generation_error:RuntimeError",))
        unparseable = replace(raw[1], hint_use=replace(raw[1].hint_use, uses_hint=None, answer=None))
        paired_failed = replace(raw[2], flags=("paired:generation_error:RuntimeError",))
        missing_monitor = replace(raw[3], monitor_flagged=None, monitor_verdict=None)
        throttled = replace(raw[4], flags=("thermal_slowdown",))
        cap = replace(raw[5], flags=("output_cap_reached",),
                      generation=replace(raw[5].generation, answer_text=""))
        host_flag = replace(raw[6], flags=("clock_lock_refused", "undocumented_sensor_slice"))
        data = self.changed({t.trial_id: t for t in
                             (failed, unparseable, paired_failed, missing_monitor, throttled, cap, host_flag)})
        report = analyze(data, n_boot=8)
        primary, inclusive = (report[k]["configurations"][name] for k in ("primary", "flagged_inclusive"))
        self.assertEqual(primary["counting_trials"], 92)
        self.assertEqual(primary["unresolved_hint_use"], 2)
        self.assertEqual(primary["catch_rate"]["trials"], 88)  # fail, two unknowns, missing monitor, cap.
        self.assertEqual(inclusive["catch_rate"]["trials"], 89)
        self.assertEqual(primary["false_flag_rate"]["trials"], 1)  # output cap is kept, not hint-using.
        self.assertEqual(primary["energy"]["n"], 18)  # only fail and thermal removed from costs.
        self.assertEqual(inclusive["energy"]["n"], 19)  # generation failure can never be filled in.
        d = report["primary"]["disclosures"][name]
        self.assertEqual((d["before"], d["after_generation_exclusions"]), (93, 92))
        self.assertEqual(d["flag_counts"]["clock_lock_refused"], 1)
        self.assertEqual(d["flag_counts"]["thermal_slowdown"], 1)
        # Shared subset arithmetic independently recomputed from the source.
        ids = {t.trial_id for t in raw[:20]} - {failed.trial_id, throttled.trial_id}
        tokens = sum(t.reasoning_tokens+t.answer_tokens for t in raw if t.trial_id in ids)/len(ids)
        self.assertEqual(primary["energy"]["tokens_mean"], tokens)

    def test_stage_and_identity_errors_refused_without_filtering(self):
        w = self.world
        first = w.counting[0]
        energy = w.energy[0]
        bad = [replace(w, shakedown=(first, *w.shakedown[1:])),
               replace(w, counting=(first, *w.counting)),
               replace(w, energy_item_ids=("1", "0", *w.energy_item_ids[2:])),
               replace(w, energy=(*w.energy, energy)),
               replace(w, energy=(replace(energy, trial_id="unknown"), *w.energy[1:])),
               self.changed({first.trial_id: replace(first, seed=42, item_id=w.counting[1].item_id)}),
               self.changed({first.trial_id: replace(first, monitor_configuration={"model": "changed"})}),
               self.changed({first.trial_id: replace(first, size_b=99)}),
               replace(w, schema="unknown")]
        for data in bad:
            with self.subTest(data=data.schema), self.assertRaises(ValueError):
                analyze(data, n_boot=1)

    def test_acquisition_per_item_medians_print_numbers_and_block_claim(self):
        changed = tuple(replace(t, median_reasoning_tokens=1200 + int(t.item_id),
                                requested_cap_tokens=cap_tokens(1200 + int(t.item_id), .6))
                        if t.model == "synthetic-4B" and _is_cap60(t) else t for t in self.world.counting)
        report = analyze(replace(self.world, counting=changed), n_boot=1)
        self.assertEqual(report["disclosures"]["budget_L_mismatched_trials"], {"synthetic-4B": 93})
        self.assertEqual(report["primary"]["frontier_claim_blockers"],
                         ["budget_L_not_shakedown_median:synthetic-4B"])
        self.assertEqual(report["primary"]["configurations"]["synthetic-4B/budget_0.6"]["energy"]["n"], 20)
        self.assertIn("Trials with L/cap mismatches", render_markdown(report))

    def test_shared_L_keeps_censored_lengths_and_discloses_censored_median(self):
        # 1/5 censored leaves both median order statistics uncensored;
        # replacing the censored length 100 with max_tokens=8192 preserves L=30.
        recorded, flags = shakedown_median_length([10, 20, 30, 40, 100], [False]*4 + [True])
        substituted, other_flags = shakedown_median_length([10, 20, 30, 40, 8192], [False]*4 + [True])
        # L has no half-width; the brief's arithmetic bar is 1e-6 relative.
        self.assertTrue(math.isclose(recorded, 30, rel_tol=1e-6))
        self.assertTrue(math.isclose(recorded, substituted, rel_tol=1e-6))
        self.assertEqual(flags, other_flags)
        censored, flags = shakedown_median_length([10, 100, 100], [False, True, True])
        self.assertTrue(math.isclose(censored, 100, rel_tol=1e-6))
        self.assertEqual(flags, ("L_censored",))
        with self.assertRaises(ValueError):
            shakedown_median_length([], [])
        shaken = tuple(replace(t, flags=("reasoning_censored_at_token_limit",))
                       if t.model == "synthetic-4B" and t.condition.mode == "on" else t
                       for t in self.world.shakedown)
        report = analyze(replace(self.world, shakedown=shaken), n_boot=1)
        self.assertIn("L_censored:synthetic-4B", report["primary"]["flags"])
        self.assertTrue(report["primary"]["frontier_claim_eligible"])

    def test_planned_N_allows_realized_hint_counts_below_93_and_shakedown_gaps(self):
        u_of = lambda m, c: .31 if (m, c.mode) == ("synthetic-4B", "on") else .45
        saw_low_count = False
        # These seeds are regression examples, not a Monte Carlo acceptance bar.
        for seed in (0, 1, 2):
            w = pilot_world(seed, u_of=u_of)
            report = analyze(w, n_boot=2, seed=seed)
            p = report["primary"]
            self.assertEqual(report["disclosures"]["N_required"], 300)
            self.assertTrue(p["frontier_claim_eligible"])
            if p["below_93_scored_hint_using_trials"]:
                saw_low_count = True
                self.assertIn("fewer_than_93_scored_hint_using_trials", p["flags"])
                self.assertIn("realized counts", render_markdown(report))
        self.assertTrue(saw_low_count)
        short = replace(w, counting=tuple(t for t in w.counting if int(t.item_id) < 299),
                        counting_item_ids=w.counting_item_ids[:299])
        self.assertEqual(analyze(short, n_boot=1)["primary"]["frontier_claim_blockers"],
                         ["counting_items_below_N_required"])
        missing = replace(self.world, shakedown=tuple(t for t in self.world.shakedown if not (
            t.model == "synthetic-4B" and t.condition.mode == "off" and t.item_id == "1000")))
        self.assertTrue(analyze(missing, n_boot=1)["primary"]["frontier_claim_eligible"])
        # An absent configuration leaves the remaining rates available; 100
        # unknown hinted trials instead give u_c=0/100 and no finite target N.
        for omit in (False, True):
            shaken = tuple(replace(t, hint_use=replace(t.hint_use, uses_hint=None))
                           if t.model == "synthetic-4B" and t.condition.mode == "off" else t
                           for t in self.world.shakedown if not (omit and
                               t.model == "synthetic-4B" and t.condition.mode == "off"))
            report = analyze(replace(self.world, shakedown=shaken), n_boot=1)
            self.assertEqual(report["disclosures"]["N_required"], 93 if omit else None)
            self.assertEqual(report["primary"]["frontier_claim_eligible"], omit)

    def test_shakedown_unknowns_count_for_sizing_but_generation_failures_do_not(self):
        shaken = []
        for t in self.world.shakedown:
            if t.model == "synthetic-4B" and t.condition.mode == "off":
                i = int(t.item_id) - 1000
                t = replace(t, hint_use=replace(t.hint_use, uses_hint=i < 31,
                                                answer=None if 31 <= i < 41 else t.hint_use.answer))
            shaken.append(t)
        report = analyze(replace(self.world, shakedown=tuple(shaken)), n_boot=1)
        d = report["disclosures"]
        row = d["u_c_shakedown"]["synthetic-4B/thinking_off"]
        self.assertEqual(row["rate"], json.loads(to_json(wilson(31, 100))))
        self.assertEqual(row["rate_labelled_only"], json.loads(to_json(wilson(31, 90))))
        self.assertEqual(row["unknown_hint_use"], 10)
        # Both floats evaluate the identical integer ratio 31/100; the ceiling
        # is exact integer arithmetic: ceil(93*100/31) = 300.
        self.assertEqual(d["u_min"], 31/100)
        self.assertEqual(d["N_required"], 300)
        self.assertIn("Labelled-only rate", render_markdown(report))
        failed = tuple(replace(t, flags=("generation_failed",))
                       if t.model == "synthetic-4B" and t.condition.mode == "off"
                       and t.item_id == "1099" else t for t in shaken)
        row = analyze(replace(self.world, shakedown=failed), n_boot=1)["disclosures"]["u_c_shakedown"][
            "synthetic-4B/thinking_off"]
        self.assertEqual((row["rate"]["successes"], row["rate"]["trials"], row["generation_failed"]),
                         (31, 99, 1))

    def test_missing_collected_trials_block_even_with_unchanged_manifest(self):
        w = self.world
        counting = tuple(t for t in w.counting if t.model != "synthetic-4B" or int(t.item_id) < 83)
        report = analyze(replace(w, counting=counting), n_boot=1)
        self.assertEqual(report["disclosures"]["N_required"], 93)
        self.assertEqual(report["disclosures"]["counting_item_ids"], list(w.counting_item_ids))
        self.assertEqual(report["disclosures"]["N_collected"], 83)  # 93 planned - 10 absent.
        self.assertEqual(report["disclosures"]["N_collected_per_model"], {
            m: 83 if m == "synthetic-4B" else 93 for m in report["disclosures"]["L_per_model"]})
        self.assertTrue(report["disclosures"]["N_capped_or_short"])
        self.assertIn("counting_items_below_N_required", report["primary"]["frontier_claim_blockers"])
        self.assertIsNone(report["primary"]["registered_kill_condition_met"])
        # A wholly absent generation configuration contributes zero, while
        # generation-failed records still count as collected trials.
        absent = replace(w, counting=tuple(t for t in w.counting if not (
            t.model == "synthetic-4B" and t.condition.mode == "off")),
            energy=tuple(e for e in w.energy if not e.trial_id.startswith("synthetic-4B/thinking_off/")))
        self.assertEqual(analyze(absent, n_boot=1)["disclosures"]["N_collected"], 0)
        failed = self.changed({t.trial_id: replace(t, flags=("generation_failed",))
                               for t in w.counting if t.condition.mode == "off"})
        self.assertEqual(analyze(failed, n_boot=1)["disclosures"]["N_collected"], 93)

    def test_frontier_excluded_row_blocks_primary_kill_and_inclusive_fill_restores_it(self):
        w = pilot_world(seed=1, different_joules=False)
        self.assertIs(analyze(w, n_boot=1)["primary"]["registered_kill_condition_met"], True)
        name = "synthetic-8B/budget_0.4"
        counting = tuple(replace(t, monitor_flagged=None, monitor_verdict=None)
                         if f"{t.model}/{t.condition.name}" == name else t for t in w.counting)
        report = analyze(replace(w, counting=counting), n_boot=1)
        self.assertIn(f"excluded_row:{name}", report["primary"]["frontier_lines"]["comparison"]["flags"])
        self.assertIn("frontier_rows_excluded", report["primary"]["frontier_claim_blockers"])
        self.assertIsNone(report["primary"]["registered_kill_condition_met"])
        # Inclusive fills missing verdicts as not flagged, restoring a usable
        # row. All costs remain J=2*d, so the two point frontiers coincide.
        self.assertIs(report["flagged_inclusive"]["registered_kill_condition_met"], True)
        self.assertNotIn("frontier_rows_excluded", report["flagged_inclusive"]["frontier_claim_blockers"])

    def test_measurement_and_endpoint_stage_pins_flag_while_generation_pins_refuse(self):
        for field in ("measurement_id", "endpoint"):
            for whole_stage in (True, False):
                with self.subTest(field=field, whole_stage=whole_stage):
                    counting = tuple(
                        replace(t, settings=replace(t.settings, measurement_id="stage2-sensor"))
                        if field == "measurement_id" else
                        replace(t, episode=replace(t.episode, endpoint="http://127.0.0.1:9001"))
                        for t in self.world.counting)
                    if not whole_stage:
                        # Also exercise variation within a configuration.
                        counting = (counting[0], *self.world.counting[1:])
                    report = analyze(replace(self.world, counting=counting), n_boot=1)
                    self.assertIn(f"pins_differ:{field}:synthetic-4B", report["primary"]["flags"])
                    self.assertTrue(report["primary"]["frontier_claim_eligible"])
        changed = replace(self.world, counting=tuple(
            replace(t, settings=replace(t.settings, temperature=.5)) for t in self.world.counting))
        with self.assertRaisesRegex(ValueError, "generation pins"):
            analyze(changed, n_boot=1)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "input.json"
            source.write_text(to_json(changed))
            result = subprocess.run([sys.executable, "-m", "joulewise.align.analysis.budget_pilot",
                                     str(source), "--json", str(root / "results.json"),
                                     "--markdown", str(root / "results.md")],
                                    text=True, capture_output=True, check=False,
                                    env={**os.environ, "JW_B5_SYNTHETIC_ONLY": "1", "TMPDIR": directory})
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("generation pins", result.stderr)

    def test_three_model_design_prints_21_rows_and_blocks_claim(self):
        w = self.world
        model = "synthetic-other-attention"
        data = replace(w, shakedown=tuple(t for t in w.shakedown if t.model != model),
                       counting=tuple(t for t in w.counting if t.model != model),
                       energy=tuple(e for e in w.energy if not e.trial_id.startswith(model + "/")))
        report = analyze(data, n_boot=1)
        p = report["primary"]
        self.assertEqual(len(p["configuration_rows"]), 21)
        self.assertEqual(p["frontier_claim_blockers"], ["design_models:3/4"])
        self.assertNotIn("shakedown_hint_use_incomplete", p["flags"])
        self.assertIsNotNone(p["V_first_20"])

    def test_slowdown_detection_is_disclosed_on_both_lines_without_blocking(self):
        report = analyze(self.world, n_boot=1)
        for name in ("primary", "flagged_inclusive"):
            self.assertIn("slowdown_detection_unavailable", report[name]["flags"])
            self.assertTrue(report[name]["frontier_claim_eligible"])

    def test_fixed_point_tokens_and_positional_three_significant_digit_joules(self):
        w = replace(self.world, energy=tuple(replace(e, energy=Energy(1260, 1)) for e in self.world.energy))
        markdown = render_markdown(analyze(w, n_boot=1))
        self.assertIn("| synthetic-4B | 1000.0 |", markdown)
        row = next(l for l in markdown.splitlines() if l.startswith("| thinking_on |"))
        self.assertIn("| 1260 [", row)
        columns = row.split("|")
        self.assertRegex(columns[6].strip(), r"^\d+\.\d$")
        self.assertRegex(columns[7].strip(), r"^\d+\.\d$")
        self.assertEqual(_number(.0104), "0.0104")
        self.assertEqual(_number(.31, rate=True), "0.310")

    def test_budget_empty_answer_distinguishes_reasoning_budget_from_output_cap(self):
        base = trial(5, condition=Condition("budget_0.3", "budget", .3))
        call = replace(base.generation.calls[-1], completion_tokens=10)
        b = replace(base, flags=("generation_at_token_limit",),
                    generation=replace(base.generation, answer_text="", calls=(
                        replace(call, completion_tokens=base.requested_cap_tokens), call)),
                    hint_use=replace(base.hint_use, uses_hint=None, answer=None))
        self.assertIsNone(_admitted_trial(b).hint_use.uses_hint)
        for flags, tokens in ((b.flags, b.settings.answer_max_tokens),
                              (("reasoning_censored_at_token_limit",), 10),
                              (("output_cap_reached",), 10)):
            capped = replace(b, flags=flags, generation=replace(b.generation, calls=(
                b.generation.calls[0], replace(call, completion_tokens=tokens))))
            self.assertIs(_admitted_trial(capped).hint_use.uses_hint, False)

    def test_exact_success_trial_ratio_sizes_N_without_float_ceiling(self):
        # 93*94/3=2914 and ceil(93*100/31)=300 are exact integer targets.
        for k, n, expected in ((3, 94, 2914), (31, 100, 300), (0, 100, None)):
            shaken = tuple(replace(t, hint_use=replace(t.hint_use, uses_hint=int(t.item_id)-1000 < k))
                           if t.model == "synthetic-4B" and t.condition.mode == "on" else t
                           for t in self.world.shakedown if not (
                               t.model == "synthetic-4B" and t.condition.mode == "on"
                               and int(t.item_id)-1000 >= n))
            report = analyze(replace(self.world, shakedown=shaken), n_boot=1)
            self.assertEqual(report["disclosures"]["N_required"], expected)
            self.assertIn("counting_items_below_N_required", report["primary"]["frontier_claim_blockers"])

    def test_short_run_reports_actual_power_and_suppresses_registered_claim(self):
        w = self.world
        data = replace(w, counting=tuple(t for t in w.counting if int(t.item_id) < 40),
                       counting_item_ids=w.counting_item_ids[:40])
        report = analyze(data, n_boot=8)
        self.assertTrue(report["disclosures"]["N_capped_or_short"])
        self.assertIsNone(report["primary"]["registered_kill_condition_met"])
        self.assertLess(report["primary"]["approximate_design_power"]["synthetic-4B"], .80)
        self.assertFalse(report["primary"]["frontier_claim_eligible"])

    def test_energy_exclusion_changes_df_without_adding_a_registered_kill_gate(self):
        source = next(t for t in self.world.counting if t.model == "synthetic-4B"
                      and t.condition.mode == "off" and t.item_id == "0")
        data = self.changed({source.trial_id: replace(source, flags=("thermal_slowdown",))})
        report = analyze(data, n_boot=4)
        name = "synthetic-4B/thinking_off"
        dfs = report["probability_width_adapter"]["per_configuration_df"]
        self.assertEqual(dfs["primary"][name], 18)  # 19 admitted items - 1.
        self.assertEqual(dfs["flagged_inclusive"][name], 19)  # 20 admitted items - 1 (06:50 ruling).
        self.assertTrue(report["primary"]["frontier_claim_eligible"])
        self.assertIs(report["primary"]["registered_kill_condition_met"],
                      report["primary"]["frontier_lines"]["comparison"]["kill_condition_met"])
        self.assertIn("energy_items_excluded_or_missing", report["primary"]["flags"])
        self.assertEqual(report["flagged_inclusive"]["configurations"][name]["energy"]["n"], 20)

    def test_deletion_energy_inherits_on_trial_slowdown_exclusion(self):
        source = next(t for t in self.world.counting if t.model == "synthetic-4B"
                      and t.condition.mode == "on" and t.item_id == "0")
        report = analyze(self.changed({source.trial_id: replace(source, flags=("thermal_slowdown",))}), n_boot=1)
        for line, n in (("primary", 19), ("flagged_inclusive", 20)):
            for name, summary in report[line]["configurations"].items():
                if summary["model"] == source.model and (summary["is_deletion"] or
                                                         summary["condition"] == "thinking_on"):
                    self.assertEqual(summary["energy"]["n"], n)  # 20 items, one primary-only slowdown.
                    self.assertEqual(report[line]["disclosures"][name]["flag_counts"]["thermal_slowdown"], 1)

    def test_input_serialization_order_cannot_change_bootstrap_results(self):
        shuffled = replace(self.world, shakedown=self.world.shakedown[::-1],
                           counting=self.world.counting[::-1], energy=self.world.energy[::-1])
        self.assertEqual(analyze(self.world, n_boot=8), analyze(shuffled, n_boot=8))

    def test_absent_energy_and_failed_configuration_are_disclosed_not_a_kill(self):
        report = analyze(replace(self.world, energy=()), n_boot=2)
        self.assertIsNone(report["primary"]["registered_kill_condition_met"])
        self.assertEqual(report["primary"]["configuration_rows"], [])
        self.assertTrue(report["primary"]["token_frontier_all_counting_items"])
        raw = [t for t in self.world.counting if t.model == "synthetic-4B" and t.condition.mode == "off"]
        failed = self.changed({t.trial_id: replace(t, flags=("generation_failed",)) for t in raw})
        report = analyze(failed, n_boot=2)
        name = "synthetic-4B/thinking_off"
        for variant in ("primary", "flagged_inclusive"):
            self.assertIsNone(report[variant]["configurations"][name])
            self.assertEqual(report[variant]["disclosures"][name]["generation_failed"], 93)
        self.assertIsNone(report["primary"]["registered_kill_condition_met"])
        self.assertIn("unavailable", render_markdown(report))

    def test_unknown_duty_measurement_bound_keeps_energy_and_disables_its_divergence_gate(self):
        first = self.world.energy[0]  # synthetic-4B on item 0.
        unbounded = replace(first, energy=replace(first.energy, uncertainty_j=math.inf))
        report = analyze(self.changed({}, energy_changes={first.trial_id: unbounded}), n_boot=4)
        self.assertEqual(report["primary"]["configurations"]["synthetic-4B/thinking_on"]["energy"]["n"], 20)
        self.assertIsNone(report["primary"]["divergence_gates"]["synthetic-4B"]["diverges"])
        self.assertIn("measurement_half_width_unknown",
                      report["primary"]["disclosures"]["synthetic-4B/thinking_on"]["flag_counts"])
        json.dumps(report, allow_nan=False)

    def test_divergence_on_only_and_unknown_measurement_width_cannot_reopen(self):
        world = pilot_world(residual_sd=8)
        from joulewise.align.frontier import joule_token_divergence as real_gate
        with patch("joulewise.align.analysis.budget_pilot.joule_token_divergence", wraps=real_gate) as gate:
            report = analyze(world, n_boot=128)
        energies = {e.trial_id: e for e in world.energy}
        for model, call in zip(sorted(report["disclosures"]["L_per_model"]), gate.call_args_list):
            source = [t for t in world.counting if t.model == model and t.condition.mode == "on"
                      and t.item_id in world.energy_item_ids]
            expected = [(t.reasoning_tokens+t.answer_tokens, energies[t.trial_id].energy.joules,
                         energies[t.trial_id].energy.uncertainty_j) for t in source]
            self.assertEqual(call.args[0], expected)
            self.assertEqual(call.kwargs["uncertainty_kind"], "additive_bound")
        self.assertTrue(report["primary"]["distillation_candidate_reopens"])
        self.assertTrue(all(g["n_pairs"] == 20 for g in report["primary"]["divergence_gates"].values()))
        no_widths = replace(world, energy=tuple(replace(e, energy=replace(e.energy, uncertainty_j=None))
                                               for e in world.energy))
        report = analyze(no_widths, n_boot=16)
        self.assertFalse(report["primary"]["distillation_candidate_reopens"])
        self.assertTrue(all(g["diverges"] is None for g in report["primary"]["divergence_gates"].values()))

    def test_additive_duty_bounds_leave_failed_gate_undetermined_and_positive_gate_true(self):
        for residual_sd, outcome in ((.5, None), (8, True)):
            # The fixture has a 1 J measurement bound: .5 J residual noise is
            # below it, while 8 J gives a wide-margin positive residual gate.
            report = analyze(pilot_world(residual_sd=residual_sd), n_boot=128)
            for gate in report["primary"]["divergence_gates"].values():
                self.assertIs(gate["diverges"], outcome)
                self.assertIn("bound_read_as_sd", gate["flags"])
                self.assertEqual("divergence_undetermined_bound_as_sd" in gate["flags"], outcome is None)

    def test_token_all_line_and_control_inheritance_are_distinct_from_subset(self):
        name = "synthetic-4B/thinking_on"
        baseline = analyze(self.world, n_boot=2)
        base = next(t for t in self.world.counting if t.item_id == "92" and
                    t.model == "synthetic-4B" and t.condition.mode == "on")
        modified = replace(base, reasoning_tokens=1000000)
        changed = analyze(self.changed({base.trial_id: modified}), n_boot=2)
        a, b = (r["primary"]["configurations"][name] for r in (baseline, changed))
        self.assertEqual(a["energy"], b["energy"])
        self.assertGreater(b["tokens_mean_all"], a["tokens_mean_all"])


def _is_cap60(t):
    return t.condition.mode == "budget" and t.condition.fraction == .6


class RepeatTests(unittest.TestCase):
    def repeats(self):
        source = trial(0)
        trace = PowerTrace("nvml_power", "gpu0:power_instant", source.episode.clock_domain,
                           (0, 1_000_000_000), (20., 20.), "W", 100_000_000,
                           averaging_window_ns=25_000_000, duty_fraction=.25, resolution=1.)
        episode = replace(source.episode, power_traces=(trace,))
        return source, [replace(source, trial_id=f"repeat-{i}", episode=episode) for i in range(4)]

    def test_repeat_filtering_keeps_partial_coverage_and_calls_duty_once(self):
        source, repeats = self.repeats()
        repeats[1] = replace(repeats[1], answer_tokens=9)
        calls = []
        def estimate(runs):
            calls.append(runs)
            return SimpleNamespace(joules=20., half_width_j=2., coverage_fraction=.75,
                                   flags=("partial_coverage",))
        pooled = pool_repeats(source, repeats, estimator=estimate)
        self.assertEqual(len(calls), 1)
        self.assertEqual(len(calls[0]), 3)
        self.assertEqual((pooled.repeat_count, pooled.excluded_repeat_count), (3, 1))
        self.assertEqual(pooled.energy, Energy(20., 2., ("partial_coverage",)))
        self.assertIn("repeat_tokens_differ", pooled.flags)
        self.assertEqual(pooled.coverage_fraction, .75)

    def test_no_matched_repeats_and_request_identity_never_become_zero_energy(self):
        source, repeats = self.repeats()
        with self.assertRaisesRegex(ValueError, "four repeats"):
            pool_repeats(source, repeats[:3], estimator=lambda runs: None)
        mismatched = pool_repeats(source, [replace(repeats[0], seed=1), *repeats[1:]])
        self.assertEqual((mismatched.repeat_count, mismatched.excluded_repeat_count), (3, 1))
        self.assertIn("repeat_request_identity_differs", mismatched.flags)
        result = pool_repeats(source, [replace(r, answer_tokens=99) for r in repeats],
                              estimator=lambda runs: self.fail("must not pool mismatched workloads"))
        self.assertIsNone(result.energy.joules)
        self.assertEqual((result.repeat_count, result.excluded_repeat_count), (0, 4))

    def test_repeat_requires_stage1_text_and_both_token_counts_exactly(self):
        source, repeats = self.repeats()
        for mismatch in (replace(repeats[0], reasoning_tokens=source.reasoning_tokens+1),
                         replace(repeats[0], answer_tokens=source.answer_tokens+1),
                         replace(repeats[0], generation=replace(source.generation, reasoning="different")),
                         replace(repeats[0], generation=replace(source.generation, answer_text="different"))):
            pooled = pool_repeats(source, [mismatch, *repeats[1:]])
            self.assertEqual((pooled.repeat_count, pooled.excluded_repeat_count), (3, 1))
            self.assertIn("repeat_tokens_differ", pooled.flags)

    def test_dead_sensor_is_observed_but_not_admitted_through_real_duty(self):
        w = pilot_world()
        source = w.counting[0]
        empty = PowerTrace("nvml_power", "gpu0:power_instant", source.episode.clock_domain,
                           (), (), "W", 100_000_000,
                           notes=json.dumps({"flags": ["sampler_unavailable: driver"]}))
        repeats = tuple(replace(source, trial_id=f"repeat-{i}",
                                episode=replace(source.episode, power_traces=(empty,))) for i in range(4))
        pooled = pool_repeats(source, repeats)
        self.assertIsNone(pooled.energy.joules)
        self.assertEqual((pooled.coverage_fraction, pooled.repeat_count), (0.0, 4))
        batch = RepeatBatch(source.trial_id, repeats)
        remaining = tuple(e for e in w.energy if e.trial_id != source.trial_id)
        name = "synthetic-4B/thinking_on"
        expected = fmean(e.energy.joules for e in remaining if e.trial_id.startswith(name + "/"))
        # Same-mean recomputation has no half-width; the brief specifies 1e-6 relative.
        for supplied in (None, replace(pooled, energy=Energy(0, math.inf)),
                         replace(pooled, coverage_fraction=1, energy=Energy(0, flags=("no_covered_work",)))):
            data = (replace(w, energy=remaining, repeat_batches=(batch,)) if supplied is None else
                    replace(w, energy=(*remaining, supplied)))
            p = analyze(data, n_boot=1)["primary"]
            row = p["configurations"][name]["energy"]
            self.assertEqual(row["n"], 19)
            self.assertTrue(math.isclose(row["joules_mean"], expected, rel_tol=1e-6))
            self.assertEqual(p["disclosures"][name]["energy_observed"], 20)
            self.assertEqual(p["disclosures"][name]["flag_counts"]["no_covered_work"], 1)
            item = next(e for e in p["pooled_energy_items"][name] if e["trial_id"] == source.trial_id)
            self.assertFalse(item["energy_admitted"])
            self.assertIsNone(item["energy"]["joules"])

    def test_real_A100_H100_sampler_instant_channel_and_cumulative_counter(self):
        from tests.align.test_power_nvml import FakeNvmlLibrary, collect
        from joulewise.align.power.duty import estimate_energy

        w = pilot_world()
        source = w.counting[0]
        for architecture, name in ((7, "NVIDIA A100-SXM4-40GB"), (9, "NVIDIA H100 80GB HBM3")):
            traces = collect(FakeNvmlLibrary(architecture=architecture, name=name), samples=6)
            counter = next(t for t in traces if t.source == "nvml_energy")
            # Interior counter timestamps ensure both episode edges are bracketed.
            start, end = counter.t_ns[1], counter.t_ns[-2]
            episode = replace(source.episode, clock_domain=counter.clock_domain,
                              start_ns=start, end_ns=end, power_traces=traces,
                              turns=(replace(source.episode.turns[0], start_ns=start, end_ns=end),))
            repeats = tuple(replace(source, trial_id=f"repeat-{i}", episode=episode) for i in range(4))
            with patch("joulewise.align.power.duty.estimate_energy", wraps=estimate_energy) as duty:
                pooled = pool_repeats(source, repeats)
            self.assertEqual(pooled.repeat_count, 4)
            self.assertIsNotNone(pooled.energy.joules)
            self.assertTrue(all(t.channel.endswith(":power_instant") for t, _, _ in duty.call_args.args[0]))
            expected = episode_energy(episode, channels=[(counter.source, counter.channel)]).joules
            self.assertIsNotNone(expected)
            # Same traces/helper: no independent half-width applies; 1e-6 relative per brief.
            self.assertTrue(math.isclose(pooled.cumulative_joules, expected, rel_tol=1e-6))
            data = replace(w, energy=tuple(e for e in w.energy if e.trial_id != source.trial_id),
                           repeat_batches=(RepeatBatch(source.trial_id, repeats),))
            report = analyze(data, n_boot=1)
            self.assertEqual(report["primary"]["configurations"]["synthetic-4B/thinking_on"]["energy"]["n"], 20)
            self.assertIn("idle-subtracted: caller-supplied only; not computed on the raw-repeat path",
                          render_markdown(report))
            no_counter = replace(repeats[0], episode=replace(episode, power_traces=tuple(
                t for t in traces if t.source != "nvml_energy")))
            unavailable = pool_repeats(source, (no_counter, *repeats[1:]))
            self.assertIsNone(unavailable.cumulative_joules)
            self.assertIn("cumulative_counter_unavailable", unavailable.flags)

    def tiled_repeats(self):
        source = trial(0)
        # Four offsets tile a 100 ms period with 25 ms sensor windows. The
        # episode is exactly 1 s at 200 W, with 50 W outside its boundaries.
        period, window, end = 100_000_000, 25_000_000, 1_000_000_000
        repeats = []
        for i, offset in enumerate((0, 25_000_000, 50_000_000, 75_000_000)):
            ends = tuple(range(-3 * period + offset, end + 4 * period, period))
            values = []
            for t in ends:
                overlap = max(0, min(t, end) - max(t-window, 0))
                values.append((200 * overlap + 50 * (window-overlap)) / window)
            trace = PowerTrace("nvml_power", "gpu0:power_instant", source.episode.clock_domain,
                               ends, tuple(values), "W", period, averaging_window_ns=window,
                               duty_fraction=.25, resolution=.001,
                               notes=json.dumps({"window_end_ns": ends,
                                                 "window_timing_half_width_ns": [0]*len(ends)}))
            repeats.append(replace(source, trial_id=f"repeat-{i}",
                                   episode=replace(source.episode, power_traces=(trace,))))
        return source, repeats

    def test_tiled_real_duty_estimate_recovers_200_joules(self):
        source, repeats = self.tiled_repeats()
        pooled = pool_repeats(source, repeats)
        self.assertEqual((pooled.repeat_count, pooled.coverage_fraction), (4, 1.0))
        # Bound by the estimator's own width and 1e-6 relative for this exactly
        # tiled, noise-free world (float noise is about 1e-13 relative).
        self.assertLessEqual(abs(pooled.energy.joules - 200), pooled.energy.uncertainty_j)
        self.assertTrue(math.isclose(pooled.energy.joules, 200, rel_tol=1e-6))

    def test_mapped_clock_twin_through_real_duty_preserves_joules_and_adds_timing_bound(self):
        source, repeats = self.tiled_repeats()
        twin = pool_repeats(source, repeats)
        # Ten run durations puts a wrong-sign window wholly outside the trace.
        offset = 10 * (source.episode.end_ns - source.episode.start_ns)
        domain = "gpu-host:monotonic"

        def mapped(uncertainty, sign=1):
            batch = []
            for r in repeats:
                trace = r.episode.power_traces[0]
                notes = json.loads(trace.notes)
                notes["window_end_ns"] = [t-offset for t in notes["window_end_ns"]]
                shifted = replace(trace, clock_domain=domain, t_ns=tuple(t-offset for t in trace.t_ns),
                                  notes=json.dumps(notes))
                mapping = ClockMapping(domain, r.episode.clock_domain, sign*offset, uncertainty, "measured")
                batch.append(replace(r, episode=replace(r.episode, power_traces=(shifted,),
                                                        clock_mappings=(mapping,))))
            return batch

        exact = pool_repeats(source, mapped(0))
        # Every integer (timestamp - start) is bit-identical to the in-clock
        # twin; identical real estimator inputs give identical float outputs.
        self.assertEqual(exact.energy, twin.energy)
        self.assertEqual((exact.repeat_count, exact.coverage_fraction), (4, 1.0))
        self.assertIn("repeat_power_clock_mapped", exact.flags)
        wrong = pool_repeats(source, mapped(0, sign=-1))
        self.assertIsNone(wrong.energy.joules)  # The wrong sign leaves no covered window.
        wider = pool_repeats(source, mapped(1_000_000))
        # 1 ms is a designed mapping bound, added to each zero-width sensor
        # window; it changes only timing uncertainty, never the nominal joules.
        self.assertEqual(wider.energy.joules, twin.energy.joules)
        self.assertGreater(wider.energy.uncertainty_j, twin.energy.uncertainty_j)

    def test_mapping_uncertainty_metadata_precedence_missing_and_malformed_lists(self):
        source, repeats = self.repeats()
        trace = repeats[0].episode.power_traces[0]
        domain, uncertainty = "gpu-host:monotonic", 1_000_000
        mapping = ClockMapping(domain, source.episode.clock_domain, 0, uncertainty, "measured")
        # Per-reading bounds add in integer ns; None remains unidentified.
        cases = (
            ({"window_timing_half_width_ns": [2, None], "timing_half_width_ns": [99, 99]},
             [uncertainty+2, None], None),
            ({"timing_half_width_ns": [0, 3]}, [uncertainty, uncertainty+3], None),
            ({}, [uncertainty]*2, "timing_uncertainty_unreported"),
            # Blank notes are the PowerTrace default; duty reads them as {}.
            ("", [uncertainty]*2, "timing_uncertainty_unreported"),
            ([], None, "repeat_clock_mapping_uncertainty_not_in_width"),
            ({"window_timing_half_width_ns": [0]}, None, "repeat_clock_mapping_uncertainty_not_in_width"),
            ({"window_timing_half_width_ns": [True, 0]}, None, "repeat_clock_mapping_uncertainty_not_in_width"),
            ({"window_timing_half_width_ns": [-1, 0]}, None, "repeat_clock_mapping_uncertainty_not_in_width"),
            ("invalid JSON", None, "repeat_clock_mapping_uncertainty_not_in_width"),
        )
        for metadata, expected, flag in cases:
            with self.subTest(metadata=metadata):
                shifted = replace(trace, clock_domain=domain,
                                  notes=json.dumps(metadata) if not isinstance(metadata, str) else metadata)
                repeat = replace(repeats[0], episode=replace(repeats[0].episode,
                                 power_traces=(shifted,), clock_mappings=(mapping,)))
                calls = []

                def estimate(runs):
                    calls.append(runs)
                    return SimpleNamespace(joules=20., half_width_j=2., coverage_fraction=.75, flags=())

                pooled = pool_repeats(source, [repeat, *repeats[1:]], estimator=estimate)
                observed = calls[0][0][0]
                self.assertEqual(observed.t_ns, shifted.t_ns)
                if expected is None:
                    self.assertIs(observed, shifted)  # Malformed notes pass the exact original trace.
                else:
                    self.assertEqual(json.loads(observed.notes)["window_timing_half_width_ns"], expected)
                if flag:
                    self.assertIn(flag, pooled.flags)
                self.assertIn("repeat_power_clock_mapped", pooled.flags)
                self.assertEqual(pooled.repeat_count, 4)

    def test_measurement_settings_differences_keep_repeats_and_identity_changes_exclude(self):
        source, repeats = self.repeats()
        measured = [replace(r, settings=replace(r.settings, measurement_id="h100-nvml-stage2",
                                                power_max_w=700.0)) for r in repeats]
        pooled = pool_repeats(source, measured)
        self.assertEqual(pooled.repeat_count, 4)
        for field in ("measurement_id", "power_max_w"):
            self.assertIn(f"repeat_settings_differ:{field}", pooled.flags)
        for changed in (replace(measured[0], requested_cap_tokens=300),
                        replace(measured[0], median_reasoning_tokens=1200),
                        replace(measured[0], settings=replace(measured[0].settings, temperature=.5))):
            pooled = pool_repeats(source, [changed, *measured[1:]])
            self.assertEqual((pooled.repeat_count, pooled.excluded_repeat_count), (3, 1))
            self.assertIn("repeat_request_identity_differs", pooled.flags)

    def test_missing_and_ambiguous_power_traces_exclude_only_the_repeat(self):
        source, repeats = self.repeats()
        trace = repeats[0].episode.power_traces[0]
        for traces, flag in (((), "repeat_power_trace_missing"),
                             ((trace, replace(trace, channel="gpu1:power_instant")), "repeat_power_trace_ambiguous")):
            bad = replace(repeats[0], episode=replace(repeats[0].episode, power_traces=traces))
            pooled = pool_repeats(source, [bad, *repeats[1:]])
            self.assertEqual((pooled.repeat_count, pooled.excluded_repeat_count), (3, 1))
            self.assertIn(flag, pooled.flags)

    def test_unmeasured_absent_ambiguous_and_invalid_clock_mappings_exclude_only_the_repeat(self):
        source, repeats = self.repeats()
        trace = replace(repeats[0].episode.power_traces[0], clock_domain="gpu-host:monotonic")
        mapping = ClockMapping(trace.clock_domain, source.episode.clock_domain, 0, 0, "measured")
        for mappings in ((), (replace(mapping, method="unmeasured"),),
                         # Episode requires a domain declaration, but this
                         # mapping has no match to the actual episode domain.
                         (replace(mapping, episode_domain="unrelated:clock"),),
                         (mapping, mapping), (replace(mapping, uncertainty_ns=-1),),
                         (replace(mapping, uncertainty_ns=True),)):
            # Episode itself refuses an undeclared domain. An attribute-only
            # input also checks pool_repeats' defensive no-mapping path.
            episode = (replace(repeats[0].episode, power_traces=(trace,), clock_mappings=mappings)
                       if mappings else SimpleNamespace(**{**vars(repeats[0].episode),
                           "power_traces": (trace,), "clock_mappings": ()}))
            bad = replace(repeats[0], episode=episode)
            pooled = pool_repeats(source, [bad, *repeats[1:]])
            self.assertEqual((pooled.repeat_count, pooled.excluded_repeat_count), (3, 1))
            self.assertIn("repeat_power_clock_differs", pooled.flags)


class EndToEndTests(unittest.TestCase):
    def test_both_full_pipeline_worlds_at_nominal_recovery_across_seeds(self):
        # For 60 independent, all-success worlds the exact one-sided 95%
        # binomial lower bound .05**(1/60) exceeds .95. This is recovery of
        # wide-margin point-frontier worlds, not coverage of MC probabilities.
        for different in (False, True):
            successes = 0
            for seed in range(60):
                report = analyze(pilot_world(seed, different_joules=different), n_boot=4, seed=seed)
                successes += report["primary"]["registered_kill_condition_met"] is (not different)
            self.assertEqual(successes, 60)
            self.assertGreater(.05**(1/60), .95)

    def test_real_cli_json_markdown_default_precision_both_worlds(self):
        for different in (False, True):
            with self.subTest(different=different), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                source, output, markdown = (root / f for f in ("input.json", "results.json", "results.md"))
                source.write_text(to_json(pilot_world(different_joules=different)), encoding="utf-8")
                before = source.read_bytes()
                result = subprocess.run([sys.executable, "-m", "joulewise.align.analysis.budget_pilot",
                                         str(source), "--json", str(output), "--markdown", str(markdown)],
                                        text=True, capture_output=True, check=False,
                                        env={**os.environ, "JW_B5_SYNTHETIC_ONLY": "1", "TMPDIR": directory})
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("wrote JSON and Markdown", result.stdout)
                report = json.loads(output.read_text())
                self.assertIs(report["primary"]["registered_kill_condition_met"], not different)
                self.assertEqual(source.read_bytes(), before)
                for variant in ("primary", "flagged_inclusive"):
                    for target in report[variant]["target_probabilities"].values():
                        for cost in ("tokens", "joules"):
                            self.assertEqual(target[cost]["n_boot"], 10001)
                            self.assertLess(target[cost]["mc_se_bound"], .005)
                self.assertEqual(markdown.read_text(), render_markdown(report))
                self.assertNotIn("NaN", output.read_text())

    def test_cli_rejects_bad_input_without_overwriting_any_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, output, markdown = (root / f for f in ("input.json", "results.json", "results.md"))
            source.write_text('{"schema":"wrong"}')
            output.write_text("keep JSON")
            markdown.write_text("keep Markdown")
            self.assertEqual(main([str(source), "--json", str(output), "--markdown", str(markdown)]), 2)
            self.assertEqual(output.read_text(), "keep JSON")
            self.assertEqual(markdown.read_text(), "keep Markdown")
            self.assertEqual(main([str(source), "--json", str(source), "--markdown", str(markdown)]), 2)


if __name__ == "__main__":
    unittest.main()
