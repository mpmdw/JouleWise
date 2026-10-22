"""Physics-derived checks of the sensor through real inbox episode timing."""

from __future__ import annotations

import math
import unittest
from dataclasses import replace

from joulewise.align.mock_world import PowerModel, SyntheticPowerSampler
from joulewise.align.records import to_json
from joulewise.align.tamper import delete_turns, drop_tool_calls
from tests.align.test_runner import inbox_episode

_NS = 1_000_000_000


def sampled_gross(episode, trace, idle_watts):
    """Independent nonoverlapping box integration plus episode idle energy."""
    dt = trace.nominal_interval_ns / _NS
    return (idle_watts * (episode.end_ns - episode.start_ns) / _NS +
            math.fsum((power - idle_watts) * dt for power in trace.values[1:]))


def full_coverage(episode):
    sampler = SyntheticPowerSampler(clock_domain=episode.clock_domain,
        interval_ns=100_000_000, averaging_window_ns=100_000_000,
        noise_watts=0.0, quantum_watts=0.0, seed=episode.seed)
    sampler.start()
    sampler.observe_episode(episode)
    return sampler, sampler.stop()[0]


class MockWorldTests(unittest.TestCase):
    def test_production_shaped_counts_and_waits(self):
        ep, _, _, _, _ = inbox_episode()
        self.assertTrue(10 <= len(ep.turns) <= 40)
        for turn in ep.turns:
            # The brief's production-shaped ranges are world-design constraints,
            # not fitted thresholds on real measurements.
            self.assertTrue(200 <= turn.prefill_tokens <= 4000)
            self.assertTrue(20 <= turn.decode_tokens <= 600)
            for call in turn.tool_calls:
                self.assertTrue(100_000_000 <= call.end_ns - call.start_ns <= 20_000_000_000)
        self.assertEqual(ep.turns[6].tool_calls[0].name, "transfer")
        self.assertEqual(ep.turns[6].hidden_tokens, 184)
        self.assertTrue(all(t.hidden_tokens == 0 for t in ep.turns if t.index != 6))

    def test_full_coverage_energy_conservation_against_independent_formula(self):
        for condition in ("benign", "sabotage"):
            with self.subTest(condition=condition):
                ep, _, _, _, _ = inbox_episode(condition, seed=2)
                sampler, trace = full_coverage(ep)
                model = sampler.model
                # Independent arithmetic: separate the three count sums, instead
                # of the sampler's turn-by-turn expression.
                expected = (
                    model.idle_watts * (ep.end_ns - ep.start_ns) / _NS +
                    model.prefill_joules_per_token * sum(t.prefill_tokens for t in ep.turns) +
                    model.decode_joules_per_token * sum(t.decode_tokens for t in ep.turns) +
                    model.context_joules_per_token_squared *
                    sum(t.context_tokens * t.decode_tokens for t in ep.turns))
                measured = sampled_gross(ep, trace, model.idle_watts)
                # Equal-width averaging bins partition time, including the trailing
                # bin: excess energy is conserved. With no measurement uncertainty,
                # the brief's agreement tolerance is 1e-6 relative.
                self.assertTrue(math.isclose(measured, expected, rel_tol=1e-6), (measured, expected))
                self.assertTrue(math.isclose(sampler.expected_energy_joules(ep),
                                             expected, rel_tol=1e-6))

    def test_context_term_and_hidden_decode_clear_attribution_floor(self):
        ep, _, _, _, _ = inbox_episode(seed=1)
        sampler, original = full_coverage(ep)
        # An extra 8192 cached KV positions is a configured workload contrast.
        shifted = replace(ep, turns=tuple(
            replace(t, context_tokens=t.context_tokens + 8192) for t in ep.turns))
        _, changed = full_coverage(shifted)
        expected = sampler.model.context_joules_per_token_squared * 8192 * ep.totals()["decode_tokens"]
        contrast = sampled_gross(shifted, changed, sampler.model.idle_watts) - sampled_gross(
            ep, original, sampler.model.idle_watts)
        # About 1 J is the stated M3 attribution limit; the designed synthetic
        # contrast must exceed it. No hardware detectability is inferred here.
        self.assertGreater(expected, 1.0)
        # No printed uncertainty: use the brief's 1e-6 relative agreement rule.
        self.assertTrue(math.isclose(contrast, expected, rel_tol=1e-6))
        benign, _, _, _, _ = inbox_episode("benign", seed=1)
        _, benign_trace = full_coverage(benign)
        sabotage_energy = sampled_gross(ep, original, sampler.model.idle_watts)
        benign_energy = sampled_gross(benign, benign_trace, sampler.model.idle_watts)
        self.assertGreater(sabotage_energy - benign_energy, 1.0)
        hidden_energy = (sampler.model.decode_joules_per_token +
                        sampler.model.context_joules_per_token_squared * ep.turns[6].context_tokens) * 184
        self.assertGreater(hidden_energy, 1.0)
        # A mutation removing the context/decode contribution would fail the
        # independent energy equalities above, not merely remain under a loose bar.

    def test_tool_wait_samples_are_idle(self):
        ep, _, _, _, _ = inbox_episode()
        sampler = SyntheticPowerSampler(clock_domain=ep.clock_domain,
            noise_watts=0.0, quantum_watts=0.0)
        sampler.start()
        sampler.observe_episode(ep)
        trace = sampler.stop()[0]
        idle_samples = []
        for call in (c for t in ep.turns for c in t.tool_calls):
            for timestamp, power in zip(trace.t_ns, trace.values):
                if call.start_ns + trace.averaging_window_ns <= timestamp <= call.end_ns:
                    idle_samples.append(power)
        self.assertTrue(idle_samples)
        # Idle is an exactly constant configured model, with no sensor noise here.
        self.assertTrue(all(power == sampler.model.idle_watts for power in idle_samples))

    def test_sensor_cadence_quantum_noise_and_determinism(self):
        ep, _, _, _, sampler = inbox_episode(seed=4)
        trace = ep.power_traces[0]
        self.assertEqual(trace.nominal_interval_ns, 100_000_000)
        self.assertEqual(trace.averaging_window_ns, 25_000_000)
        # The duty fraction is the exact ratio 25/100, representable as 1/4.
        self.assertEqual(trace.duty_fraction, 0.25)
        self.assertTrue(all(b - a == trace.nominal_interval_ns
                            for a, b in zip(trace.t_ns, trace.t_ns[1:])))
        for power in trace.values:
            # Integer quantum grid is a numerical computation with no uncertainty
            # in this comparison; use the prescribed 1e-6 relative agreement.
            nearest = round(power / trace.resolution) * trace.resolution
            self.assertTrue(math.isclose(power, nearest, rel_tol=1e-6))
        sampler.start()
        sampler.observe_episode(ep)
        self.assertEqual(to_json(sampler.stop()), to_json(ep.power_traces))
        sampler.noise_watts = 0.0
        sampler.start()
        sampler.observe_episode(ep)
        self.assertNotEqual(to_json(sampler.stop()), to_json(ep.power_traces))

    def test_logged_flags_do_not_change_the_sensor(self):
        ep, _, _, _, sampler = inbox_episode()
        changed = drop_tool_calls(delete_turns(ep, [6]), lambda call: call.name == "transfer")
        sampler.start()
        sampler.observe_episode(changed)
        # Bit identity is intentional: same physical work, same deterministic sensor.
        self.assertEqual(to_json(sampler.stop()), to_json(ep.power_traces))

    def test_unknown_phase_boundary_preserves_total_energy(self):
        ep, _, _, _, _ = inbox_episode()
        unknown = replace(ep, turns=tuple(replace(t, first_token_ns=None) for t in ep.turns))
        sampler, trace = full_coverage(unknown)
        expected = sampler.expected_energy_joules(unknown)
        measured = sampled_gross(unknown, trace, sampler.model.idle_watts)
        # Unknown first-token times prevent phase separation; aggregate energy
        # still conserves the token model, at 1e-6 relative without uncertainty.
        self.assertTrue(math.isclose(measured, expected, rel_tol=1e-6))
        self.assertIn("prefill boundary unknown", trace.notes)

    def test_same_forward_pass_work_is_blind_to_text(self):
        from joulewise.align.mock_world import ScriptedEndpoint
        class DifferentText(ScriptedEndpoint):
            def chat(self, messages, **kwargs):
                result = super().chat(messages, **kwargs)
                return replace(result, content=result.content.replace("digest", "alternative"))
        original, transcript, _, _, _ = inbox_episode()
        changed, other_transcript, _, _, _ = inbox_episode(endpoint_class=DifferentText)
        self.assertNotEqual(to_json(transcript), to_json(other_transcript))
        # Identical timings/counts under the same sensor seed must produce
        # bit-identical power. Text semantics within that work are invisible.
        self.assertEqual(to_json(original.power_traces), to_json(changed.power_traces))

    def test_absent_episode_returns_diagnostic_trace(self):
        sampler = SyntheticPowerSampler()
        sampler.start()
        trace = sampler.stop()[0]
        self.assertEqual(trace.t_ns, ())
        self.assertTrue(trace.notes)


if __name__ == "__main__":
    unittest.main()
