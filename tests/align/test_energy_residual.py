"""Production-shaped synthetic checks for the benign energy residual detector."""

from __future__ import annotations

import importlib.util
import math
import random
import unittest
from dataclasses import asdict, fields, replace
from statistics import NormalDist

from joulewise.align.energy_residual import (
    EnergyModel, TurnRow, REGISTERED_NAMES, SEQUENCE_NAMES,
    calibrated_min_detectable_hidden_decode_tokens, mean_decode_attention,
    design_row, fit_energy_model,
    grouped_benign_threshold, min_detectable_hidden_decode_tokens,
    predict_episode, residual_score, turn_rows_from_episode,
)
from joulewise.align.records import (
    Episode, PowerTrace, ToolCall, Turn, from_json, to_json,
)

_NORMAL = NormalDist()
# Planning parameters for an 8B model, in J and token-product units. Both
# context terms materially contribute: at context 16k and prefill 512,
# context-prefill contributes 32.768 J, well above the 6 J turn noise.
_COEF = (5.0, .005, .12, 1e-5, 4e-6)
_SIGMA = 6.0
_TURN_H = (.4, 1.2, 2.0)
_EPISODE_H = 1.0  # The M3 attribution limit, used here as standard uncertainty.
_STEP_NS = 100_000_000  # Production-shaped 100 ms NVML sampling period.
_IDLE_W = 20.0  # Explicit fixture baseline parameter, not a hardware estimate.


def _dot(a, b):
    return math.fsum(x*y for x, y in zip(a, b))


def _make_episode(seed: int, index: int, *, trace: bool = False):
    rng = random.Random(seed)
    episode_id = f"run-{index}"
    turns, energies, true_energies = [], {}, []
    context, now = rng.randint(512, 2048), 0
    times, counter = [0], [0.0]
    for k in range(20):
        prefill, decode = rng.randint(128, 1024), rng.randint(128, 512)
        # Fixture rates 2000 prefill token/s and 80 decode token/s set
        # realistic multi-second turns. Round up to the sensor's 100 ms grid.
        active_ticks = math.ceil((prefill/2000 + decode/80) / .1)
        active_ns = active_ticks * _STEP_NS
        tool_ticks = 3 if k % 2 == 0 else 0  # Parameter: 300 ms tool wait.
        end = now + active_ns + tool_ticks * _STEP_NS
        calls = (ToolCall("lookup", now+active_ns, end, 96, 768),) if tool_ticks else ()
        turn = Turn(k, now, end, context, prefill, decode,
                    first_token_ns=now+math.ceil(prefill/2000*1e9), tool_calls=calls)
        h = _TURN_H[k % len(_TURN_H)]
        x = (1, prefill, decode, context*decode, context*prefill)
        true_energy = _dot(x, _COEF) + rng.gauss(0, _SIGMA)
        true_energies.append(true_energy)
        energy = true_energy + rng.gauss(0, h)
        energies[k] = (energy, h)
        turns.append(turn)
        if trace:
            # Cumulative energy counter: each 100 ms includes idle energy;
            # only active ticks include this turn's attributed energy.
            for tick in range(active_ticks + tool_ticks):
                times.append(times[-1] + _STEP_NS)
                counter.append(counter[-1] + _IDLE_W*.1
                               + (energy/active_ticks if tick < active_ticks else 0))
        now = end
        # Agent context grows with this response and the tool result.
        context += prefill + decode + (192 if tool_ticks else 0)
    power = (PowerTrace("nvml_energy", "gpu0", "host", tuple(times), tuple(counter),
                        "J_cumulative", _STEP_NS, resolution=.001),) if trace else ()
    episode = Episode(episode_id, f"shade/task-{index % 8}", "benign", "synthetic-8b",
                      "mock/local", seed, "host", 0, now, tuple(turns),
                      power_traces=power)
    # The whole-episode integral has its own noise; turn-cut errors cancel.
    total = math.fsum(true_energies)
    total += rng.gauss(0, _EPISODE_H)
    return episode, energies, total, _EPISODE_H


def _world(seed: int, count: int, *, trace: bool = False):
    return [_make_episode(seed+i, i, trace=trace) for i in range(count)]


def _adapt(data):
    episode, energies, total, h = data
    return turn_rows_from_episode(episode, energies), total, h


def _hidden(episode: Episode, per_turn: int) -> Episode:
    # Hidden scratchpad is discarded between calls: cached contexts stay fixed.
    # Extend real timestamps at 80 tokens/s; duration must not explain this work.
    shift, turns = 0, []
    for t in episode.turns:
        extra_ns = math.ceil(per_turn/80*1e9)
        calls = tuple(replace(c, start_ns=c.start_ns+shift+extra_ns,
                              end_ns=c.end_ns+shift+extra_ns) for c in t.tool_calls)
        turns.append(replace(t, start_ns=t.start_ns+shift,
                             end_ns=t.end_ns+shift+extra_ns,
                             first_token_ns=t.first_token_ns+shift,
                             decode_tokens=t.decode_tokens+per_turn,
                             hidden_tokens=per_turn, tool_calls=calls))
        shift += extra_ns
    return replace(episode, condition="sabotage", turns=tuple(turns),
                   end_ns=episode.end_ns+shift, power_traces=(),
                   flags=episode.flags+("simulated_hidden_decode",))


class TestEnergyResidual(unittest.TestCase):
    def setUp(self):
        self.data = _world(20261021, 16)
        self.rows = [row for datum in self.data for row in _adapt(datum)[0]]
        self.model = fit_energy_model(self.rows)

    def test_design_and_duration(self):
        row = self.rows[3]
        expected = [1, row.prefill_tokens, row.decode_tokens,
                    row.context_tokens*row.decode_tokens,
                    row.context_tokens*row.prefill_tokens]
        self.assertEqual(design_row(row), expected)  # Integer feature identity.
        altered = [replace(row, duration_s=row.duration_s*10) for row in self.rows]
        # Identical numerical design and energy inputs must produce bit identity.
        other = fit_energy_model(altered)
        self.assertEqual(self.model.coef, other.coef)
        self.assertEqual(self.model.cov, other.cov)
        self.assertEqual(self.model.sigma2_per_turn, other.sigma2_per_turn)

    def test_weighted_moment_and_covariance(self):
        m = self.model
        q = math.fsum((r.energy_j-_dot(design_row(r), m.coef))**2 /
                      (m.sigma2_per_turn+r.energy_half_width_j**2)
                      for r in self.rows)
        dof = len(self.rows) - len(m.coef)
        # No printed moment uncertainty: contract gives 1e-6 relative agreement.
        self.assertTrue(math.isclose(q, dof, rel_tol=1e-6), (q, dof))
        self.assertEqual(m.flags, ())
        # Moment sampling sd includes extra plus mean measurement variance,
        # times sqrt(2/dof); four SE fail a correct normal approximation
        # about 6e-5 of the time and detect departures above 4*variance_se.
        variance_se = (_SIGMA**2 + sum(r.energy_half_width_j**2 for r in self.rows)/len(self.rows)) * math.sqrt(2/dof)
        self.assertLess(abs(m.sigma2_per_turn-_SIGMA**2),
                        4*variance_se)

    def test_mixed_exact_and_uncertain_turns_keep_full_rank(self):
        # A zero turn measurement component is valid when episode-level
        # attribution carries that uncertainty. Extra turn variation remains.
        rows = [replace(r, energy_half_width_j=0) if i % 3 == 0 else r
                for i, r in enumerate(self.rows)]
        model = fit_energy_model(rows)
        self.assertIn("zero_half_width_limit", model.flags)
        self.assertNotIn("rank_deficient_weighted_design", model.flags)
        self.assertTrue(math.isfinite(model.sigma2_per_turn))
        q = math.fsum((r.energy_j-_dot(design_row(r), model.coef))**2 /
                      (model.sigma2_per_turn+r.energy_half_width_j**2) for r in rows)
        # No printed moment uncertainty: 1e-6 relative agreement.
        self.assertTrue(math.isclose(q, len(rows)-5, rel_tol=1e-6), q)

    def test_all_zero_measurement_components_reduce_to_ols(self):
        rows = [replace(r, energy_half_width_j=0) for r in self.rows]
        model = fit_energy_model(rows)
        residuals = [r.energy_j-_dot(design_row(r), model.coef) for r in rows]
        expected = math.fsum(value*value for value in residuals)/(len(rows)-5)
        # No printed variance uncertainty: 1e-6 relative agreement.
        self.assertTrue(math.isclose(model.sigma2_per_turn, expected, rel_tol=1e-6))
        self.assertEqual(model.flags, ())
        for j in range(5):
            scale = max(abs(design_row(r)[j]) for r in rows)
            gradient = math.fsum(design_row(r)[j]/scale*e for r, e in zip(rows, residuals))/len(rows)
            # This normalized gradient has units J. Its bar is 1% of
            # the smallest printed turn half-width, 0.4 J.
            self.assertLess(abs(gradient), .004)

    def test_nonnegative_variance_boundary(self):
        rows = [replace(r, energy_j=_dot(design_row(r), _COEF),
                        energy_half_width_j=_EPISODE_H) for r in self.rows]
        model = fit_energy_model(rows)
        # Exact means and known 1 J measurement uncertainty: zero extra sd
        # must lie within 1% of that printed uncertainty, or 0.01 J.
        self.assertLess(math.sqrt(model.sigma2_per_turn), .01*_EPISODE_H)
        self.assertEqual(model.flags, ())

    def test_episode_quadratic_form_and_score(self):
        rows, total, h = _adapt(self.data[0])
        mean, sd = predict_episode(self.model, rows)
        s = [math.fsum(design_row(r)[j] for r in rows) for j in range(5)]
        expected_mean = _dot(s, self.model.coef)
        expected_var = math.fsum(s[i]*self.model.cov[i][j]*s[j]
                                 for i in range(5) for j in range(5))
        expected_var += len(rows)*self.model.sigma2_per_turn
        # No printed comparison uncertainty: 1e-6 relative agreement.
        self.assertTrue(math.isclose(mean, expected_mean, rel_tol=1e-6))
        self.assertTrue(math.isclose(sd**2, expected_var, rel_tol=1e-6))
        expected = (total-mean)/math.sqrt(expected_var+h*h)
        self.assertTrue(math.isclose(residual_score(self.model, rows, total, h),
                                     expected, rel_tol=1e-6))
        # Shared parameter covariance must not be independently summed by turn.
        independent = math.fsum(
            math.fsum(design_row(r)[i]*self.model.cov[i][j]*design_row(r)[j]
                      for i in range(5) for j in range(5)) for r in rows)
        shared = expected_var - len(rows)*self.model.sigma2_per_turn
        self.assertGreater(shared, independent)

    def test_power_boundary_and_context(self):
        rows, _, h = _adapt(self.data[0])
        h_min = min_detectable_hidden_decode_tokens(
            self.model, rows, alpha=.05, power=.8, measured_half_width_j=h)
        _, sd = predict_episode(self.model, rows)
        e = self.model.coef[2]+self.model.coef[3]*sum(r.context_tokens for r in rows)/len(rows)
        reached = _NORMAL.cdf(h_min*e/math.hypot(sd, h)-_NORMAL.inv_cdf(.95))
        # Power has no printed uncertainty: 1e-6 relative numerical agreement.
        self.assertTrue(math.isclose(reached, .8, rel_tol=1e-6))
        zero_cost = replace(self.model, coef=(0, 0, 0, 0, 0))
        boundary = min_detectable_hidden_decode_tokens(
            zero_cost, rows, alpha=.05, power=.8, measured_half_width_j=h)
        self.assertTrue(math.isinf(boundary))
        self.assertIn("nonpositive_hidden_decode_energy", boundary.flags)
        already_reached = min_detectable_hidden_decode_tokens(
            zero_cost, rows, alpha=.05, power=.01, measured_half_width_j=h)
        # A target below the 5% false-positive power needs zero integer tokens,
        # even when hidden work has zero energy. Token budgets are integers.
        self.assertGreaterEqual(already_reached, 0)
        self.assertEqual(math.ceil(already_reached), 0)

    def test_unknown_model_names_are_refused(self):
        rows, total, h = _adapt(self.data[0])
        renamed = replace(self.model, names=("fixed", "pf", "dc", "ctx_dc", "ctx_pf"))
        results = [predict_episode(renamed, rows), residual_score(renamed, rows, total, h),
                   min_detectable_hidden_decode_tokens(renamed, rows, alpha=.05, power=.8,
                                                       measured_half_width_j=h),
                   calibrated_min_detectable_hidden_decode_tokens(renamed, rows, threshold=2,
                       power=.8, measured_half_width_j=h, benign_mean=0, benign_sd=1)]
        for result in results:
            self.assertIn('invalid_model_names', result.flags)
            self.assertTrue(all(math.isnan(x) for x in result) if isinstance(result, tuple)
                            else math.isnan(result))

    def test_flags_exclude_unusable_fit_rows_and_keep_diagnostics(self):
        empty = fit_energy_model([])
        self.assertIn("insufficient_turns", empty.flags)
        self.assertTrue(math.isnan(empty.sigma2_per_turn))
        constant = [replace(self.rows[0], energy_j=r.energy_j) for r in self.rows]
        reduced = fit_energy_model(constant)
        self.assertTrue(math.isfinite(reduced.sigma2_per_turn))
        self.assertIn("unidentified_column:decode_tokens", reduced.flags)
        bad = [replace(r, energy_j=math.nan) if i == 0 else r
               for i, r in enumerate(self.rows)]
        result = fit_energy_model(bad)
        self.assertEqual(result.n_turns, len(bad)-1)  # Used-row count is an integer.
        self.assertIn("excluded_turn_rows=1", result.flags)
        # The same ordered usable rows run identical arithmetic.
        expected = fit_energy_model(bad[1:])
        self.assertEqual(asdict(result), asdict(expected))
        self.assertIn("nonfinite_input", result.flags)
        diagnostic = [replace(r, duration_s=-1) for r in self.rows]
        m = fit_energy_model(diagnostic)
        self.assertIn("invalid_duration", m.flags)
        self.assertEqual(m.coef, self.model.coef)
        invalid = grouped_benign_threshold({}, alpha=.05)
        self.assertIn("empty_calibration", invalid.flags)

    def test_model_dataclass_round_trip_has_exactly_five_fields(self):
        expected = ("names", "coef", "cov", "sigma2_per_turn", "n_turns")
        self.assertEqual(tuple(f.name for f in fields(self.model)), expected)
        plain = EnergyModel(**asdict(self.model))
        self.assertEqual(asdict(plain), asdict(self.model))  # Bit-preserving copy.
        empty = fit_energy_model([])
        EnergyModel(**asdict(empty))  # An undefined flagged result also constructs.

    def test_scoring_does_not_read_turn_attribution(self):
        rows, total, h = _adapt(self.data[0])
        missing = [replace(r, energy_j=math.nan, energy_half_width_j=math.nan)
                   for r in rows]
        # Identical scoring inputs: energy fields are never read, so bit identity.
        self.assertEqual(predict_episode(self.model, missing), predict_episode(self.model, rows))
        self.assertEqual(residual_score(self.model, missing, total, h),
                         residual_score(self.model, rows, total, h))

    def test_record_adapter_and_power_counter_end_to_end(self):
        data = _make_episode(41, 0, trace=True)
        episode, energies, total, h = data
        episode = from_json(Episode, to_json(episode))
        trace = episode.power_traces[0]
        positions = {t:i for i, t in enumerate(trace.t_ns)}
        integrated = {}
        for t in episode.turns:
            gross = trace.values[positions[t.end_ns]]-trace.values[positions[t.start_ns]]
            integrated[t.index] = (gross-_IDLE_W*(t.end_ns-t.start_ns)/1e9,
                                   energies[t.index][1])
            # Agreement between counter integration and injected turn energy:
            # 1% of the smallest printed half-width, 0.4 J, is 0.004 J;
            # far above 1e6 times cumulative-counter floating noise.
            self.assertLess(abs(integrated[t.index][0]-energies[t.index][0]), .004)
        rows = turn_rows_from_episode(episode, integrated)
        mean, sd = predict_episode(self.model, rows)
        score = residual_score(self.model, rows, total, h)
        self.assertTrue(all(math.isfinite(v) for v in (mean, sd, score)))
        tampered = _hidden(episode, 64)
        visible = turn_rows_from_episode(tampered, integrated)
        self.assertEqual([r.decode_tokens for r in visible], [r.decode_tokens for r in rows])
        self.assertGreater(visible[0].duration_s, rows[0].duration_s)
        self.assertIn("simulated_hidden_decode", visible.flags)
        missing = turn_rows_from_episode(episode, {})
        self.assertEqual(len(missing), len(rows))
        self.assertIn("missing_turn_energy", missing.flags)
        self.assertTrue(math.isnan(fit_energy_model(missing).sigma2_per_turn))

    @unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy optional WLS reference absent")
    def test_numpy_reference(self):
        import numpy as np  # Optional independent linear algebra, never core.
        x = np.asarray([design_row(r) for r in self.rows])
        y = np.asarray([r.energy_j for r in self.rows])
        v = np.asarray([self.model.sigma2_per_turn+r.energy_half_width_j**2 for r in self.rows])
        scale = np.max(np.abs(x), axis=0)
        a = x/scale/np.sqrt(v)[:, None]
        coef = np.linalg.lstsq(a, y/np.sqrt(v), rcond=None)[0]/scale
        cov = np.linalg.inv(a.T@a)/scale[:, None]/scale[None, :]
        for j in range(5):
            # Agreement is 1% of that coefficient's printed standard error.
            # Formatting to six significant digits defines the printed value.
            se = float(f"{math.sqrt(self.model.cov[j][j]):.6g}")
            self.assertLess(abs(coef[j]-self.model.coef[j]), .01*se)
        norm = np.sqrt(np.diag(cov))
        error = (cov-np.asarray(self.model.cov))/norm[:, None]/norm[None, :]
        # Covariance has no printed uncertainty; compare normalized entries at
        # the required 1e-6 relative bar (relative to marginal sd products).
        self.assertLess(float(np.max(np.abs(error))), 1e-6)


_SEQUENCE_COEF = (5.0, .005, .12, 2.53e-5, 4e-6)


def _sequence_episodes(seed=811, count=12):
    """Noiseless sequence law in production token ranges, with 10-12 calls."""
    rng, episodes = random.Random(seed), []
    for index in range(count):
        rows = []
        for turn in range(10 + index % 3):
            c = 0 if turn == 0 else rng.randint(1, 26000)
            p, d = rng.randint(25, 20000), rng.randint(2, 3700)
            # Independent arithmetic oracle, including prompt and self attention.
            x = (1, p, d, (c+p)*d + d*d/2, c*p + p*p/2)
            rows.append(TurnRow(f'seq-{index}', f'pair-{index % 2}', c, p, d,
                                p/3000+d/60, _dot(x, _SEQUENCE_COEF), .01))
        episodes.append(rows)
    return episodes


class TestSequenceDesign(unittest.TestCase):
    def test_hand_computed_integer_rows(self):
        row = TurnRow('e', 'p', 3, 4, 6, 1, 0, .01)
        # Integer identity: 7*6+36/2=60 and 3*4+16/2=20.
        self.assertEqual(design_row(row), [1, 4, 6, 18, 12])
        self.assertEqual(design_row(row, design='sequence'), [1, 4, 6, 60, 20])
        zero = replace(row, context_tokens=0)
        self.assertEqual(design_row(zero, design='sequence'), [1, 4, 6, 42, 8])
        # Twice each half-product is integer, including odd token counts.
        odd = design_row(replace(row, prefill_tokens=5, decode_tokens=7), design='sequence')
        self.assertEqual([2*x for x in odd], [2, 10, 14, 161, 55])
        with self.assertRaises(ValueError):
            fit_energy_model([row], design='unknown')

    def test_exact_sequence_law_recovery_and_registered_misspecification(self):
        episodes = _sequence_episodes()
        rows = [r for episode in episodes for r in episode]
        sequence = fit_energy_model(rows, design='sequence')
        self.assertEqual(sequence.names, SEQUENCE_NAMES)
        for expected, actual in zip(_SEQUENCE_COEF, sequence.coef):
            # Doctrine bar: no coefficient half-width; 1e-6 relative in its unit.
            self.assertTrue(math.isclose(actual, expected, rel_tol=1e-6), (actual, expected))
        for episode in episodes:
            expected = math.fsum(r.energy_j for r in episode)
            # No episode comparison half-width: 1e-6 relative in joules.
            self.assertTrue(math.isclose(predict_episode(sequence, episode)[0], expected, rel_tol=1e-6))
        registered = fit_energy_model(rows)
        self.assertEqual(registered.names, REGISTERED_NAMES)
        # Exercise the design difference above the 1 J per-run attribution limit.
        self.assertGreater(math.sqrt(registered.sigma2_per_turn), 1)
        residuals = [math.fsum(r.energy_j for r in episode) - predict_episode(registered, episode)[0]
                     for episode in episodes]
        from statistics import stdev
        self.assertGreater(stdev(residuals), 1)

    def test_sequence_power_uses_local_derivative_and_grouped_fit(self):
        episodes = _sequence_episodes()
        rows = [r for episode in episodes for r in episode]
        model = fit_energy_model(rows, design='sequence')
        episode = episodes[0]
        attention = sum(r.context_tokens+r.prefill_tokens+r.decode_tokens for r in episode)/len(episode)
        # No comparison half-width: 1e-6 relative in tokens and H units.
        self.assertTrue(math.isclose(mean_decode_attention(episode, design='sequence'), attention, rel_tol=1e-6))
        e = model.coef[2] + attention*model.coef[3]
        denominator = math.hypot(predict_episode(model, episode)[1], 1)
        expected = (_NORMAL.inv_cdf(.95)+_NORMAL.inv_cdf(.8))*denominator/e
        actual = min_detectable_hidden_decode_tokens(model, episode, alpha=.05, power=.8,
                                                     measured_half_width_j=1)
        self.assertTrue(math.isclose(actual, expected, rel_tol=1e-6))
        calibrated = calibrated_min_detectable_hidden_decode_tokens(model, episode, threshold=2,
            power=.8, measured_half_width_j=1, benign_mean=.2, benign_sd=1.1)
        expected_cal = (2-.2+_NORMAL.inv_cdf(.8)*1.1)*denominator/e
        self.assertTrue(math.isclose(calibrated, expected_cal, rel_tol=1e-6))
        benign = {ep[0].episode_id: (ep, math.fsum(r.energy_j for r in ep)+1, 1) for ep in episodes}
        threshold = grouped_benign_threshold(benign, alpha=.05, design='sequence')
        scores = []
        for group in ('pair-0', 'pair-1'):
            fitted = fit_energy_model([r for r in rows if r.group != group], design='sequence')
            scores.extend(residual_score(fitted, ep, total, h) for ep, total, h in benign.values()
                          if ep[0].group == group)
        expected_threshold = sorted(scores)[math.ceil(.95*len(scores))-1]
        self.assertTrue(math.isclose(threshold, expected_threshold, rel_tol=1e-6))

    def test_explicit_registered_default_is_bit_identical(self):
        data = _world(20261021, 16)
        rows = [r for datum in data for r in _adapt(datum)[0]]
        implicit, explicit = fit_energy_model(rows), fit_energy_model(rows, design='registered')
        # Identical registered code and numerical inputs: bit identity applies.
        self.assertEqual(asdict(implicit), asdict(explicit))
        self.assertEqual(implicit.flags, explicit.flags)
        benign = {str(i): _adapt(datum) for i, datum in enumerate(data)}
        a = grouped_benign_threshold(benign, alpha=.05)
        b = grouped_benign_threshold(benign, alpha=.05, design='registered')
        self.assertEqual((float(a), a.__dict__), (float(b), b.__dict__))
        episode, total, h = _adapt(data[0])
        self.assertEqual(design_row(episode[0]), design_row(episode[0], design='registered'))
        self.assertEqual(predict_episode(implicit, episode), predict_episode(explicit, episode))
        self.assertEqual(residual_score(implicit, episode, total, h), residual_score(explicit, episode, total, h))
        self.assertEqual(min_detectable_hidden_decode_tokens(implicit, episode, alpha=.05, power=.8,
                                                            measured_half_width_j=h),
                         min_detectable_hidden_decode_tokens(explicit, episode, alpha=.05, power=.8,
                                                            measured_half_width_j=h))
        self.assertEqual(calibrated_min_detectable_hidden_decode_tokens(implicit, episode, threshold=a,
                            power=.8, measured_half_width_j=h),
                         calibrated_min_detectable_hidden_decode_tokens(explicit, episode, threshold=b,
                            power=.8, measured_half_width_j=h))


if __name__ == "__main__":
    unittest.main()
