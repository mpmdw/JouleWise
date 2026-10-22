"""Production-path checks for explicit bound/SD, clock, and timing seams."""
from __future__ import annotations
from dataclasses import replace
import json
import math
from pathlib import Path
import statistics
import tempfile
import unittest

from joulewise.align import energy_residual as er, frontier, runner
from joulewise.align.attribution import attribute_episode, trace_energy
from joulewise.align.interfaces import PowerSampler
from joulewise.align.mock_world import InboxTask, PowerModel, register_mock_factories
from joulewise.align.power.ina3221 import Ina3221Sampler
from joulewise.align.power.nvml import NvmlSampler
from joulewise.align.records import ClockMapping, Episode, PowerTrace, Turn, read_episodes

NS = 1_000_000_000


def power_trace(*, notes="", domain="host", unit="W", source="mock", window=None):
    return PowerTrace(source,"gpu0",domain,(0,NS,2*NS,3*NS),
                      (100.,100.,100.,100.) if unit == "W" else (0.,100.,200.,300.),
                      unit,NS,window,None,.001,notes)


def episode(trace):
    return Episode("seam","mock/seam","benign","synthetic","mock",0,"host",0,3*NS,
                   (Turn(0,0,2*NS,100,50,40,0,NS),),power_traces=(trace,))


class TimingSeamTests(unittest.TestCase):
    def test_same_domain_has_zero_clock_uncertainty_and_foreign_missing_mapping_is_flagged(self):
        local = attribute_episode(episode(power_trace()),source="mock",channel="gpu0")
        self.assertNotIn("clock.uncertainty_missing",local.flags)
        self.assertNotIn("clock.mapping_missing",local.flags)
        malformed = episode(power_trace())
        # records currently rejects an unmapped foreign domain at construction.
        # Simulate retained malformed input to exercise attribution's flags.
        object.__setattr__(malformed,"power_traces",(power_trace(domain="meter"),))
        foreign = attribute_episode(malformed,source="mock",channel="gpu0")
        self.assertIn("clock.uncertainty_missing",foreign.flags)
        self.assertIn("clock.mapping_missing",foreign.flags)
        # Public trace_energy limits are in the trace domain when no mapping
        # is supplied. No episode-domain mismatch can be inferred there.
        self.assertNotIn("clock.uncertainty_missing",trace_energy(power_trace(domain="meter"),0,NS).flags)

    def test_sample_timing_and_mapping_bounds_add_at_both_endpoints(self):
        for window in (None,NS//4):
            key = "timing_half_width_ns" if window is None else "window_timing_half_width_ns"
            trace = power_trace(notes=json.dumps({key:[1_000_000,2_000_000,3_000_000,4_000_000]}),window=window)
            base = trace_energy(replace(trace,notes=""),NS//2,3*NS//2)
            mapped = trace_energy(trace,NS//2,3*NS//2,
                                  mapping=ClockMapping("host","host",0,5_000_000,"synthetic"))
            # First bracket max h=2 ms, second=3 ms; mapping h=5 ms
            # at EACH end. Constant 100 W => 100*(.002+.003+2*.005)=1.5 J.
            expected = 100*(.002+.003+2*.005)
            self.assertAlmostEqual(mapped.half_width_j-base.half_width_j,expected,delta=1e-6*expected)
            self.assertNotIn("timing.sample_uncertainty_unreported",mapped.flags)

    def test_unknown_sample_adjacent_to_endpoint_is_infinite_and_distant_unknown_is_local(self):
        trace = power_trace(notes=json.dumps({"timing_half_width_ns":[0,None,0,0]}))
        unknown = trace_energy(trace,NS//2,3*NS//2)
        self.assertTrue(math.isinf(unknown.half_width_j))
        self.assertIn("timing.sample_uncertainty_unknown",unknown.flags)
        known = trace_energy(trace,5*NS//2,11*NS//4)
        self.assertTrue(math.isfinite(known.half_width_j))
        self.assertNotIn("timing.sample_uncertainty_unknown",known.flags)
        # At a knot the left and right timestamp brackets both touch it.
        knot = trace_energy(trace,2*NS,5*NS//2)
        self.assertTrue(math.isinf(knot.half_width_j))
        self.assertIn("timing.sample_uncertainty_unreported",trace_energy(power_trace(),0,NS).flags)

    def test_nvml_counter_unknown_update_age_keeps_energy_and_marks_infinite_timing(self):
        trace = power_trace(source="nvml_energy",unit="J_cumulative",notes=json.dumps({
            "format":"joulewise.align.nvml.v1","measurement":"energy",
            "timing_half_width_ns":[1000]*4,"unknown_sensor_age_bound_ns":None}))
        result = trace_energy(trace,0,2*NS)
        # 100 W * 2 s = 200 J; no finite width => 1e-6 relative agreement.
        self.assertAlmostEqual(result.joules,200.,delta=200e-6)
        self.assertTrue(math.isinf(result.half_width_j))
        self.assertIn("timing.sensor_age_unknown",result.flags)
        # A characterized 1 ms age, if later supplied, contributes another
        # 2*100 W*.001 s on top of the two 1 us call brackets.
        bounded = replace(trace,notes=json.dumps({"timing_half_width_ns":[1000]*4,
                                                "unknown_sensor_age_bound_ns":1_000_000}))
        value = trace_energy(bounded,0,2*NS)
        expected = 2*.001+2*100*(.001+.000001)
        self.assertAlmostEqual(value.half_width_j,expected,delta=1e-6)  # Width below 1 J.

    def test_point_phase_edge_exactly_on_sample_knot_contains_opus_five_joule_error(self):
        # Opus ex8: prefill [100,500] ms at 100 W followed by 200 W
        # decode. A right-continuous point at 500 ms smears 100 W across
        # [400,500] ms, adding 100*.1/2 = 5 J to this phase.
        period=100_000_000
        trace = PowerTrace("mock","gpu0","host",tuple(range(0,800_000_000,period)),
                           (100.,100.,100.,100.,100.,200.,200.,200.),"W",period,
                           resolution=0.)
        result=trace_energy(trace,period,5*period)
        truth=100*.4
        self.assertAlmostEqual(result.joules-truth,5.,delta=.01*result.half_width_j)
        self.assertLessEqual(abs(result.joules-truth),result.half_width_j)
        # Triangle belongs to the left bracket at the end knot.
        self.assertAlmostEqual(result.half_width_j,100*.1/2,delta=5e-6)
        # Starting at a knot inspects the right bracket as well.
        rising=replace(trace,values=(100.,100.,200.,200.,200.,200.,200.,200.))
        start=trace_energy(rising,period,4*period)
        self.assertAlmostEqual(start.half_width_j,100*.1/2,delta=5e-6)

    def test_sampler_runtime_protocol_and_declared_domain(self):
        for sampler in (NvmlSampler(clock_domain="episode.domain"),
                        Ina3221Sampler(sample_interval_ns=1_000_000,clock_domain="episode.domain")):
            self.assertIsInstance(sampler,PowerSampler)
            self.assertEqual(sampler.clock_domain,"episode.domain")
            self.assertEqual(sampler.clock_mappings,())


class UncertaintyChainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        register_mock_factories()
        cls.temp=tempfile.TemporaryDirectory()
        root=Path(cls.temp.name)
        # Real matrix, scripted endpoint, inbox tools, and sampled work ledger.
        # Six groups give independent held-out folds; 12 seeds per condition
        # supply 36 benign calibration and 72 evaluation episodes.
        spec={"matrix_id":"power-seams","clock_domain":"mock.monotonic",
              "clock":{"factory":"mock.clock"},"order_seed":7,
              "task_pairs":[{"factory":"mock.inbox","task_pair":f"mock/pair-{k}"} for k in range(6)],
              "conditions":["benign","sabotage"],"seeds":list(range(12)),
              "endpoints":[{"factory":"mock.scripted"}],
              "samplers":[{"factory":"mock.power"}],"token_counter":{"factory":"mock.tokens"},
              "max_turns":40,"max_tokens":600,"temperature":0.,"output_dir":"run"}
        path=root/"matrix.json"; path.write_text(json.dumps(spec))
        cls.episodes=read_episodes(runner.run_matrix(path))
        cls.attributions={e.episode_id:attribute_episode(e,source="mock",channel="gpu0",idle_watts=PowerModel().idle_watts)
                          for e in cls.episodes}

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def rows(self,ep):
        attr=self.attributions[ep.episode_id]
        return er.turn_rows_from_episode(ep,er.turn_energy_from_attribution(attr))

    def test_attribution_adapter_preserves_owned_segments_kind_and_flags_through_power(self):
        ep=self.episodes[0]; attr=self.attributions[ep.episode_id]
        owned=er.turn_energy_from_attribution(attr)
        self.assertEqual(owned.uncertainty_kind,"additive_bound")
        for turn,(energy,width) in owned.items():
            segments=[s.energy for s in attr.segments if s.turn==turn]
            expected=math.fsum(s.joules for s in segments)
            # Joule agreement uses 1% of the printed additive half-width.
            self.assertLessEqual(abs(energy-expected),.01*width)
        cal={e.episode_id:(self.rows(e),self.attributions[e.episode_id].total.joules,
                          self.attributions[e.episode_id].total.half_width_j)
             for e in self.episodes if e.condition=="benign" and e.seed<6}
        model=er.fit_energy_model([r for rows,_,_ in cal.values() for r in rows])
        threshold=er.grouped_benign_threshold(cal,alpha=.05,uncertainty_kind="additive_bound")
        rows=self.rows(ep); total=attr.total
        score=er.residual_score(model,rows,total.joules,total.half_width_j,uncertainty_kind="additive_bound")
        upper=er.min_detectable_hidden_decode_tokens(model,rows,alpha=.05,power=.8,
                measured_half_width_j=total.half_width_j,uncertainty_kind="additive_bound")
        calibrated=er.calibrated_min_detectable_hidden_decode_tokens(model,rows,threshold=threshold,power=.8,
                measured_half_width_j=total.half_width_j,uncertainty_kind="additive_bound")
        for result in (owned,rows,er.design_row(rows[0]),model,threshold,
                       er.predict_episode(model,rows),score,upper,calibrated):
            self.assertIn("uncertainty.bound_read_as_sd",result.flags)
        self.assertIn("uncertainty.normal_theory_conservative_upper_value",upper.flags)
        self.assertIn("uncertainty.print_beside_calibrated_min_detectable_hidden_decode_tokens",upper.flags)
        print("POWER chain H_min conservative upper",float(upper),"H_cal",float(calibrated),"flags",upper.flags)
        # The adapter retains the exact printed bounds; no distribution factor.
        self.assertEqual(rows[0].energy_half_width_j,owned[ep.turns[0].index][1])
        standard=er.turn_rows_from_episode(ep,dict(owned),uncertainty_kind="standard_uncertainty")
        self.assertNotIn("uncertainty.bound_read_as_sd",standard.flags)

    def test_divergence_bound_gate_is_undetermined_where_true_error_sd_passes(self):
        pm=PowerModel(); pairs=[]; errors=[]
        for ep in self.episodes:
            if ep.seed<6: continue
            a=self.attributions[ep.episode_id].total
            truth=math.fsum(pm.prefill_joules_per_token*t.prefill_tokens+
                           (pm.decode_joules_per_token+pm.context_joules_per_token_squared*t.context_tokens)*t.decode_tokens
                           for t in ep.turns)
            errors.append(a.joules-truth)
            pairs.append((ep.totals()["decode_tokens"],a.joules,a.half_width_j))
        sd=statistics.stdev(errors)
        bound=frontier.joule_token_divergence(pairs,n_boot=256,seed=0,uncertainty_kind="additive_bound")
        known=frontier.joule_token_divergence([(x,y,sd) for x,y,_ in pairs],n_boot=256,seed=0)
        self.assertIsNone(bound["diverges"])
        self.assertIn("divergence_undetermined_bound_as_sd",bound["flags"])
        self.assertIn("bound_read_as_sd",bound["flags"])
        self.assertIs(known["diverges"],True)
        print("POWER divergence bound/true SD",statistics.median(p[2] for p in pairs)/sd,
              "bound",bound["diverges"],bound["flags"],"true SD",known["diverges"])

    def test_positive_bound_gate_remains_a_positive_sd_gate(self):
        # Add a known 1000 J work component to truth and observation alike
        # on alternating seeds. Attribution errors and their bounds stay the
        # same, while work unexplained by tokens now clears the bound gate.
        pairs=[(e.totals()["decode_tokens"],
                self.attributions[e.episode_id].total.joules+1000*(e.seed%2),
                self.attributions[e.episode_id].total.half_width_j)
               for e in self.episodes if e.seed>=6]
        result=frontier.joule_token_divergence(pairs,n_boot=256,uncertainty_kind="additive_bound")
        self.assertIs(result["diverges"],True)
        self.assertIn("bound_read_as_sd",result["flags"])

    def test_real_loopback_endpoint_runs_into_attribution_adapter(self):
        from tests.align.test_endpoints import HTTPWorld,stream_packets
        from joulewise.align.endpoints import OpenAICompatEndpoint
        from joulewise.align.mock_world import MockTokenCounter
        with HTTPWorld([stream_packets(reasoning="",hidden=0)]) as server:
            endpoint=OpenAICompatEndpoint(server.url,"synthetic-8b",timeout_s=5)
            ep,_=runner.run_episode(InboxTask(),"benign",endpoint,seed=0,max_turns=1,max_tokens=600,
                                   temperature=0.,clock_domain="host",token_counter=MockTokenCounter())
            self.assertEqual(len(server.requests),1)
        # Synthetic constant 100 W trace covers the actual retained endpoint
        # interval. Timing is the endpoint's real monotonic clock, no hardware.
        trace=PowerTrace("mock","gpu0","host",(ep.start_ns,ep.end_ns),(100.,100.),"W",
                         ep.end_ns-ep.start_ns,resolution=.001)
        ep=replace(ep,power_traces=(trace,))
        result=attribute_episode(ep,source="mock",channel="gpu0")
        rows=er.turn_rows_from_episode(ep,er.turn_energy_from_attribution(result))
        self.assertEqual(len(rows),1)
        self.assertIn("uncertainty.bound_read_as_sd",rows.flags)
        owned=math.fsum(s.energy.joules for s in result.segments if s.turn==ep.turns[0].index)
        self.assertLessEqual(abs(rows[0].energy_j-owned),.01*rows[0].energy_half_width_j)
