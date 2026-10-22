"""Hand-computable candidate frontier checks; no hardware or network access."""

import math
import unittest
import random
import statistics
from dataclasses import replace

from joulewise.align.records import (
    Episode, MonitorVerdict, PowerTrace, ToolCall, Turn, from_json, to_json,
)

from joulewise.align.frontier import (
    ConfigRow, cheapest_reaching, frontier_agreement, joule_token_divergence,
    pareto_frontier,
)


def row(name, caught, joules, tokens, *, trials=100, half_width=1.0):
    return ConfigRow(name, "Qwen3-8B", 8.0, trials, caught, joules, half_width, tokens)


class FrontierTests(unittest.TestCase):
    def test_dominance_and_frontier_difference(self):
        rows = [row("a", 50, 100, 2000), row("b", 80, 200, 1000),
                row("c", 60, 300, 3000), row("d", 90, 400, 4000)]
        self.assertEqual(pareto_frontier(rows, cost="joules"), ["a", "b", "d"])
        self.assertEqual(pareto_frontier(rows, cost="tokens"), ["b", "d"])
        result = frontier_agreement(rows)
        self.assertEqual(result["symmetric_difference"], {"a"})
        self.assertFalse(result["kill_condition_met"])

    def test_equal_cost_catch_ties_and_strict_dominance(self):
        rows = [row("b", 50, 100, 1000), row("a", 100, 100, 1000, trials=200),
                row("worse", 40, 100, 1000), row("dearer", 50, 200, 2000)]
        for cost in ("joules", "tokens"):
            self.assertEqual(pareto_frontier(rows, cost=cost), ["a", "b"])

    def test_hand_computed_kendall(self):
        rows = [row("a", 50, 100, 1000), row("b", 60, 200, 3000),
                row("c", 70, 300, 2000)]
        # Three pairs: two concordant, one discordant: tau = (2-1)/3.
        # No uncertainty is assigned to ranks: agreement uses 1e-6 relative.
        self.assertTrue(math.isclose(frontier_agreement(rows)["kendall_tau"],
                                     1 / 3, rel_tol=1e-6))

    def test_hand_computed_kendall_with_ties(self):
        rows = [row("a", 50, 100, 1000), row("b", 60, 100, 2000),
                row("c", 70, 200, 2000)]
        # One concordant pair, one joule-only tie, one token-only tie:
        # tau-b = 1 / sqrt((1+1)*(1+1)) = 1/2; same rank tolerance.
        self.assertTrue(math.isclose(frontier_agreement(rows)["kendall_tau"],
                                     0.5, rel_tol=1e-6))

    def test_invalid_input_flags(self):
        self.assertIn("empty_rows", pareto_frontier([], cost="joules").flags)
        self.assertFalse(frontier_agreement([])["kill_condition_met"])
        self.assertIn("invalid_cost", pareto_frontier([row("a", 50, 100, 1000)],
                                                     cost="watts").flags)
        result = frontier_agreement([row("a", 0, 100, 1000, trials=0)])
        self.assertIn("invalid_counts:a", result["flags"])
        self.assertFalse(result["kill_condition_met"])


    def test_nonfinite_and_duplicate_rows_are_not_silently_filtered(self):
        good = row("a", 50, 100, 1000)
        for bad in (replace(good, joules_mean=math.nan),
                    replace(good, joules_mean=math.inf),
                    replace(good, trials=0),
                    replace(good, caught=101)):
            rows = [good, replace(bad, config_id="bad")]
            result = pareto_frontier(rows, cost="joules")
            self.assertEqual(result, ["a"])
            self.assertIn("excluded_row:bad", result.flags)
            self.assertIn("rows_used:1/2", result.flags)
        self.assertIn("duplicate_config_id", frontier_agreement([good, good])["flags"])

    def test_validate_only_fields_read_and_keep_negative_joules(self):
        good = row("a", 50, 100, 1000)
        for changes in ({"params_b": 0}, {"params_b": None},
                        {"joules_half_width": math.nan}, {"joules_half_width": -1},
                        {"tokens_mean": math.inf}):
            self.assertEqual(pareto_frontier([replace(good, **changes)], cost="joules"), ["a"])
        for changes in ({"joules_mean": math.nan}, {"joules_half_width": math.nan}):
            r = replace(good, **changes)
            self.assertEqual(pareto_frontier([r], cost="tokens"), ["a"])
            p = cheapest_reaching([r], 0.5, cost="tokens", n_boot=99)
            self.assertTrue(math.isfinite(p["a"]))
        negative = replace(good, joules_mean=-0.4)
        result = pareto_frontier([negative], cost="joules")
        self.assertEqual(result, ["a"])
        self.assertIn("negative_joules_mean:a", result.flags)

    def test_common_agreement_panel_and_kill_eligibility(self):
        rows = [row("a", 50, 100, 1000),
                replace(row("b", 80, 200, 2000), params_b=14)]
        bad = replace(row("missing", 90, 300, 3000), joules_mean=math.nan)
        agreement = frontier_agreement(rows + [bad])
        self.assertEqual(agreement["joules_frontier"], {"a", "b"})
        self.assertEqual(agreement["tokens_frontier"], {"a", "b"})
        self.assertTrue(math.isfinite(agreement["kendall_tau"]))
        self.assertTrue(agreement["identical"])
        self.assertFalse(agreement["kill_condition_met"])
        self.assertIn("excluded_row:missing", agreement["flags"])
        self.assertIn("rows_used:2/3", agreement["flags"])
        self.assertTrue(frontier_agreement(rows)["kill_condition_met"])
        single = frontier_agreement(rows[:1])
        self.assertFalse(single["kill_condition_met"])
        self.assertIn("single_model_size", single["flags"])
        empty = frontier_agreement([])
        self.assertIsNone(empty["identical"])
        self.assertIsNone(empty["kill_condition_met"])

    def test_cheapest_excludes_only_invalid_required_rows(self):
        rows = [row("a", 100, 1000, 4000),
                replace(row("bad", 100, 2000, 5000), joules_half_width=math.nan)]
        result = cheapest_reaching(rows, 0.8, cost="joules", n_boot=99)
        self.assertEqual(result, {"a": 1.0})  # Degenerate all-success singleton.
        self.assertIn("excluded_row:bad", result.flags)
        self.assertIn("rows_used:1/2", result.flags)
        token_result = cheapest_reaching(rows, 0.8, cost="tokens", n_boot=99)
        self.assertEqual(set(token_result), {"a", "bad"})
        self.assertTrue(all(map(math.isfinite, token_result.values())))

    def test_all_equal_cost_ordering_is_undefined(self):
        rows = [row("a", 50, 100, 1000), row("b", 60, 100, 1000)]
        result = frontier_agreement(rows)
        self.assertTrue(math.isnan(result["kendall_tau"]))
        self.assertIn("undefined_kendall_tau", result["flags"])


class CheapestTests(unittest.TestCase):
    def test_clearly_cheapest_default_size_and_reproducibility(self):
        rows = [row("cheap", 100, 1000, 4000), row("dear", 100, 1100, 8000)]
        result = cheapest_reaching(rows, 0.8, cost="joules", seed=12)
        self.assertEqual(result.n_boot, 10001)
        self.assertLess(result.mc_se_bound, 0.005)  # sqrt(1/(4B)), per API precision.
        # Costs differ by 100 / sqrt(1^2+1^2) > 70 normal SDs.
        # With no observed losses, the 95% one-sided binomial lower bound
        # for P(cheap) is 0.05**(1/B), about 0.99970.
        self.assertGreater(result["cheap"], 0.05**(1 / result.n_boot))
        self.assertEqual(result, cheapest_reaching(rows, 0.8, cost="joules", seed=12))
        self.assertEqual(result, cheapest_reaching(rows[::-1], 0.8, cost="joules", seed=12))

    def test_equal_uncertain_costs(self):
        rows = [row("a", 100, 1000, 4000), row("b", 100, 1000, 4000)]
        result = cheapest_reaching(rows, 0.8, cost="joules", seed=4)
        # Equal independent normal costs win with p=1/2. The 99% normal MC
        # interval has half-width z_.995*sqrt(.25/B); B=10001 from the API.
        bar = statistics.NormalDist().inv_cdf(0.995) * math.sqrt(0.25 / result.n_boot)
        for probability in result.values():
            self.assertLess(abs(probability - 0.5), bar)

    def test_exact_ties_tokens_and_unreached_probability(self):
        rows = [row("a", 100, 1000, 4000), row("b", 100, 2000, 4000)]
        tied = cheapest_reaching(rows, 0.8, cost="tokens", n_boot=10)
        # Every replicate is the same exact minimum tie: bit-identical shares.
        self.assertEqual(tied, {"a": 0.5, "b": 0.5})
        self.assertIn("token_cost_uncertainty_unavailable", tied.flags)
        failed = cheapest_reaching([row("a", 0, 1000, 4000)], 0.8,
                                   cost="joules", n_boot=10)
        self.assertEqual(failed["a"], 0.0)  # Binomial(n,0) cannot reach .8.
        self.assertEqual(failed.no_reach_probability, 1.0)
        self.assertTrue(any(f.startswith("no_config_reaches_target:") for f in failed.flags))

    def test_binomial_reach_probability_and_boundary_counts(self):
        # For Binomial(2,.5), P(X>=1)=3/4. This tests count sampling,
        # not merely cost randomness or all-success boundary distributions.
        result = cheapest_reaching([row("a", 1, 1000, 4000, trials=2)],
                                   0.5, cost="joules", seed=3)
        # 99% Monte Carlo bar at the analytically known p=.75.
        bar = statistics.NormalDist().inv_cdf(0.995) * math.sqrt(0.75 * 0.25 / result.n_boot)
        self.assertLess(abs(result["a"] - 0.75), bar)
        # Probability accounting has no measured uncertainty: 1e-6 relative.
        self.assertTrue(math.isclose(result["a"] + result.no_reach_probability,
                                     1.0, rel_tol=1e-6))
        for caught, expected in ((0, 0.0), (2000, 1.0)):
            boundary = cheapest_reaching([row("a", caught, 1000, 4000, trials=2000)],
                                         0.5, cost="joules", n_boot=10)
            self.assertEqual(boundary["a"], expected)  # Degenerate binomial identity.

    def test_invalid_inputs_and_negative_normal_draw_flags(self):
        valid = [row("a", 100, 0, 4000)]
        for kwargs in ({"n_boot": 0}, {"n_boot": True}, {"cost": "watts"},
                       {"target_catch": math.nan}):
            args = dict(target_catch=0.5, cost="joules", n_boot=10)
            args.update(kwargs)
            result = cheapest_reaching(valid, **args)
            self.assertTrue(result.flags)
            self.assertTrue(math.isnan(result["a"]))
        negative = cheapest_reaching(valid, 0.5, cost="joules", n_boot=100, seed=2)
        self.assertTrue(any(f.startswith("negative_normal_cost_draws:") for f in negative.flags))


def divergence_world(seed, *, extra_sd=0.0, n=160, half_width=1.0):
    """Twelve-turn episodes, 128-768 tokens/turn, a 1 J attribution floor."""
    rng = random.Random(seed)
    return [(tokens, 400 + 1.5 * tokens + rng.gauss(0, half_width)
             + rng.gauss(0, extra_sd), half_width)
            for tokens in (12 * rng.randrange(128, 769) for _ in range(n))]


class DivergenceTests(unittest.TestCase):
    def test_measurement_noise_at_nominal_rate_across_seeds(self):
        seeds, level, n_boot = 40, 0.95, 399
        # The gate uses the lower tail of a central 95% interval: nominal
        # false opening probability alpha/2=.025. Allow the 99th percentile
        # of Binomial(40,.025), calculated here rather than a magic count.
        nominal = (1 - level) / 2
        cumulative, maximum = 0.0, 0
        for k in range(seeds + 1):
            cumulative += math.comb(seeds, k) * nominal**k * (1 - nominal)**(seeds - k)
            if cumulative >= 0.99:
                maximum = k
                break
        openings = sum(joule_token_divergence(divergence_world(seed), level=level,
                                             n_boot=n_boot, seed=seed)["diverges"]
                       for seed in range(seeds))
        self.assertLessEqual(openings, maximum)

    def test_independent_energy_source_above_floor(self):
        # Extra source SD=8 J is eight times the stated 1 J attribution
        # floor: sqrt(1^2+8^2) is far outside the noise-only interval.
        pairs = divergence_world(12, extra_sd=8.0)
        result = joule_token_divergence(pairs, n_boot=999, seed=5)
        self.assertTrue(result["diverges"])
        self.assertGreater(result["residual_sd_ci"][0], result["median_half_width"])
        self.assertLess(result["residual_sd_ci"][0], result["residual_sd"])
        self.assertGreater(result["residual_sd_ci"][1], result["residual_sd"])
        self.assertLessEqual(result["spearman_ci"][0], result["spearman_rho"])
        self.assertGreaterEqual(result["spearman_ci"][1], result["spearman_rho"])
        self.assertEqual(result, joule_token_divergence(pairs, n_boot=999, seed=5))

    def test_exact_linear_and_default_bootstrap_size(self):
        pairs = [(float(k * 128), float(400 + k * 192), 1.0) for k in range(1, 13)]
        result = joule_token_divergence(pairs)
        self.assertFalse(result["diverges"])
        self.assertEqual(result["n_boot"], 10001)
        # Agreement bar=.001 J (0.1% of the 1 J floor), above 1e6 ulps
        # at this world's ~3 kJ and below 1% of the smallest width.
        self.assertLess(abs(result["residual_sd"]), 0.001)
        # Ranks have no measurement uncertainty: use 1e-6 relative.
        self.assertTrue(math.isclose(result["spearman_rho"], 1.0, rel_tol=1e-6))

    def test_hand_residual_and_average_tied_ranks(self):
        # Centered x=(-1,0,1), centered y=(1,-2,1): slope=0,
        # SSE=6 and n-2=1, so residual SD=sqrt(6).
        pairs = [(100.0, 12.0, 1.0), (200.0, 9.0, 1.0), (300.0, 12.0, 1.0)]
        result = joule_token_divergence(pairs, n_boot=99)
        # .001 J is 0.1% of the 1 J width, between round-off and 1%.
        self.assertLess(abs(result["residual_sd"] - math.sqrt(6)), 0.001)
        # Tied energy ranks (2.5,1,2.5) are orthogonal to (1,2,3).
        # No rank uncertainty exists; 1e-6 times the unit rho scale.
        self.assertLess(abs(result["spearman_rho"]), 1e-6)
        self.assertTrue(any(f.startswith("degenerate_residual_resamples:")
                            for f in result["flags"]))

    def test_invalid_and_unidentified_inputs_are_flagged(self):
        for pairs, kwargs in (([], {}), ([(1, 2, -1)] * 3, {}),
                              ([(1, 2, 1)] * 3, {"level": 1.0}),
                              ([(1, 2, 1)] * 3, {"n_boot": 0})):
            result = joule_token_divergence(pairs, n_boot=kwargs.get("n_boot", 10),
                                           level=kwargs.get("level", 0.95))
            self.assertTrue(result["flags"])
            self.assertIsNone(result["diverges"])
        result = joule_token_divergence([(1000, 1000 + i, 1) for i in range(20)],
                                       n_boot=99)
        self.assertIn("unidentified_ols", result["flags"])
        self.assertIsNone(result["diverges"])


# Suspicion is exactly 0 or 100; their midpoint separates those two labels.
def production_world(*, varying_energy, monitor_threshold=50.0):
    """Real shared records -> trace integration -> ConfigRows and model pairs.

    A 40-trial pilot per condition, twelve agent turns with tools, 80 token/s
    decode, 100 ms NVML cadence, 25 ms documented averaging slices. Whole-GPU
    powers follow each model's chosen J/token (world parameters, not claims).
    """
    models = [
        ("Qwen3-4B", 4.0, 1.5, 1.0, 0),
        ("Qwen3-8B", 8.0, 1.0, 2.0, 2),
        ("Qwen3-14B", 14.0, 0.75, 4.0, 4),
        ("Jamba-12B-hybrid-attention", 12.0, 1.25, 0.7, 2),
    ]
    conditions = [("thinking_off", 256, 14), ("thinking_on", 512, 32),
                  ("budget_half", 384, 26), ("concise", 320, 20),
                  ("random_delete", 448, 28)]
    rows, by_model = [], {}
    trials, n_turns, interval = 40, 12, 100_000_000
    for model_index, (model, params, token_factor, energy_rate, catch_bonus) in enumerate(models):
        rng = random.Random(20_000 + model_index)
        model_pairs = []
        for condition, per_turn, catch_count in conditions:
            energies, counts, caught = [], [], 0
            # Repeatability noise ~0.3 J vs the ~1 J attribution limit:
            # RUN_STATE.md, Current Project Status, central measurement fact.
            # Separate seeded streams give every model its own Gaussian errors.
            errors = [rng.gauss(0, 0.3) for _ in range(trials)]
            if varying_energy and model == "Jamba-12B-hybrid-attention":
                # World parameter: independent source SD 8 J, eight times the
                # 1 J half-width; this must open the gate through real records.
                errors = [v + rng.gauss(0, 8.0) for v in errors]
            # Center within each fixed-token condition, preserving the designed
            # mean costs while retaining episode-level variation for the gate.
            error_mean = statistics.fmean(errors)
            for trial in range(trials):
                decode = int(per_turn * token_factor)
                turn_ns = decode * 12_500_000 + 1_000_000_000  # 80 token/s + tool.
                turns = tuple(Turn(
                    i, i * turn_ns, (i + 1) * turn_ns, i * (decode + 256),
                    256, decode, first_token_ns=i * turn_ns + 100_000_000,
                    tool_calls=(ToolCall("lookup", (i + 1) * turn_ns - 1_000_000_000,
                                         (i + 1) * turn_ns, 256, 1024),))
                    for i in range(n_turns))
                total_tokens, end_ns = n_turns * decode, n_turns * turn_ns
                noise = errors[trial] - error_mean
                target_energy = total_tokens * (energy_rate if varying_energy else 2.0) + noise
                watts = target_energy / (end_ns / 1_000_000_000)
                times = tuple(range(0, end_ns + 1, interval))
                trace = PowerTrace("nvml_power", "gpu0", "mock-monotonic", times,
                                   (watts,) * len(times), "W", interval,
                                   averaging_window_ns=25_000_000,
                                   duty_fraction=0.25, resolution=0.001)  # NVML reports milliwatts.
                verdict = MonitorVerdict("fixed-local-monitor", "full",
                                         100.0 if trial < catch_count + catch_bonus else 0.0,
                                         "0" * 64)
                episode = Episode(
                    f"{model}/{condition}/{trial}", "shade/synthetic_research",
                    "sabotage", model, "mock:vllm", trial, "mock-monotonic",
                    0, end_ns, turns, monitor_verdicts=(verdict,), power_traces=(trace,),
                    hardware={"hint_used": True, "synthetic": True})
                if trial == 0:
                    episode = from_json(Episode, to_json(episode))
                sample = episode.power_traces[0]
                energy = math.fsum((b - a) / 1_000_000_000 * (u + v) / 2
                                   for a, b, u, v in zip(sample.t_ns, sample.t_ns[1:],
                                                         sample.values, sample.values[1:]))
                counts.append(episode.totals()["decode_tokens"])
                energies.append(energy)
                caught += episode.monitor_verdicts[0].suspicion >= monitor_threshold
                model_pairs.append((counts[-1], energy, 1.0))
            rows.append(ConfigRow(f"{model}/{condition}", model, params, trials, caught,
                                  # Print to .001 J: 0.1% of the 1 J width.
                                  # This also removes integration round-off from
                                  # deliberately identical cost means.
                                  round(statistics.fmean(energies), 3), 1.0,
                                  statistics.fmean(counts)))
        by_model[model] = model_pairs
    return rows, by_model


class ProductionWorldTests(unittest.TestCase):
    def test_model_size_and_attention_frontiers_differ(self):
        rows, pairs = production_world(varying_energy=True)
        self.assertEqual(len(rows), 20)
        result = frontier_agreement(rows)
        self.assertTrue(result["symmetric_difference"])
        self.assertFalse(result["kill_condition_met"])
        probabilities = cheapest_reaching(rows, 0.75, cost="joules", seed=11)
        # Unconditional probabilities conserve mass including no-reach cases;
        # no uncertainty assigned to arithmetic: 1e-6 relative.
        self.assertTrue(math.isclose(math.fsum(probabilities.values())
                                     + probabilities.no_reach_probability, 1.0, rel_tol=1e-6))
        for model, values in pairs.items():
            gate = joule_token_divergence(values, n_boot=199, seed=7)
            self.assertEqual(gate["diverges"], model == "Jamba-12B-hybrid-attention")
            if model == "Jamba-12B-hybrid-attention":
                self.assertGreater(gate["residual_sd_ci"][0], gate["median_half_width"])
            else:
                self.assertLess(gate["residual_sd_ci"][1], gate["median_half_width"])
        # Qwen3-14B uses half as many tokens as 4B, but twice the joules:
        # token ratio=.75/1.5=.5; energy ratio=(.75*4)/(1.5*1)=2.
        small = next(r for r in rows if r.config_id == "Qwen3-4B/thinking_on")
        large = next(r for r in rows if r.config_id == "Qwen3-14B/thinking_on")
        self.assertTrue(math.isclose(large.tokens_mean / small.tokens_mean, 0.5, rel_tol=1e-6))
        # .001 J = 0.1% of 1 J uncertainty, above 1e6 floating ulps here.
        self.assertLess(abs(large.joules_mean - 2 * small.joules_mean), 0.001)

    def test_shared_energy_per_token_frontiers_agree(self):
        rows, pairs = production_world(varying_energy=False)
        result = frontier_agreement(rows)
        self.assertFalse(result["symmetric_difference"])
        self.assertTrue(result["kill_condition_met"])
        self.assertTrue(math.isclose(result["kendall_tau"], 1.0, rel_tol=1e-6))
        probabilities = cheapest_reaching(rows, 0.75, cost="tokens", n_boot=999, seed=11)
        self.assertIn("token_cost_uncertainty_unavailable", probabilities.flags)
        for values in pairs.values():
            self.assertFalse(joule_token_divergence(values, n_boot=199, seed=7)["diverges"])


if __name__ == "__main__":
    unittest.main()
