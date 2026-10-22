"""Production-shaped synthetic checks for the benign energy residual detector."""

from __future__ import annotations

import importlib.util
import math
import random
import unittest
from dataclasses import replace
from statistics import NormalDist

from joulewise.align.energy_residual import (
    EnergyModel, TurnRow, design_row, fit_energy_model,
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
    turns, energies = [], {}
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
        energy = _dot(x, _COEF) + rng.gauss(0, math.hypot(_SIGMA, h))
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
    total = math.fsum(energy for energy, _ in energies.values())
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
        # times sqrt(2/dof); derive its 95% normal comparison bar.
        variance_se = (_SIGMA**2 + sum(r.energy_half_width_j**2 for r in self.rows)/len(self.rows)) * math.sqrt(2/dof)
        self.assertLess(abs(m.sigma2_per_turn-_SIGMA**2),
                        _NORMAL.inv_cdf(.975)*variance_se)

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
        expected_var += math.fsum(self.model.sigma2_per_turn+r.energy_half_width_j**2
                                  for r in rows)
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
        shared = expected_var - math.fsum(
            self.model.sigma2_per_turn+r.energy_half_width_j**2 for r in rows)
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

    def test_model_labels_do_not_change_the_prescribed_feature_order(self):
        rows, _, _ = _adapt(self.data[0])
        renamed = replace(self.model, names=("fixed", "pf", "dc", "ctx_dc", "ctx_pf"))
        # Identical coefficients, covariance and design arithmetic: bit identity.
        self.assertEqual(predict_episode(renamed, rows), predict_episode(self.model, rows))

    def test_flags_do_not_refuse_or_drop_data(self):
        empty = fit_energy_model([])
        self.assertIn("insufficient_turns", empty.flags)
        self.assertTrue(math.isnan(empty.sigma2_per_turn))
        constant = [replace(self.rows[0], energy_j=r.energy_j) for r in self.rows]
        self.assertIn("rank_deficient_design", fit_energy_model(constant).flags)
        bad = [replace(r, energy_j=math.nan) if i == 0 else r
               for i, r in enumerate(self.rows)]
        result = fit_energy_model(bad)
        self.assertEqual(result.n_turns, len(bad))
        self.assertIn("nonfinite_input", result.flags)
        diagnostic = [replace(r, duration_s=-1) for r in self.rows]
        m = fit_energy_model(diagnostic)
        self.assertIn("invalid_duration", m.flags)
        self.assertEqual(m.coef, self.model.coef)
        invalid = grouped_benign_threshold({}, alpha=.05)
        self.assertIn("empty_calibration", invalid.flags)

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


if __name__ == "__main__":
    unittest.main()
