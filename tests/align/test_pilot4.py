"""Sampled pilot-4 seed, replay, guard, fitting and production-bundle regressions."""
from contextlib import redirect_stdout
from dataclasses import asdict, replace
import hashlib
import csv
import io
import json
import math
from pathlib import Path
import random
import shutil
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise.align import energy_residual as er
from joulewise.align.apple import pilot_analysis as pa
from joulewise.align.apple.diagnostics import thermal_onset
from joulewise.align.apple.sampling import episode_seed, turn_seed, seed_inputs
from joulewise.align.apple.workload import EpisodeSpec, read_episode_bundle
from joulewise.clock import FakeClock
from joulewise.schemas import BenchmarkConfig
from scripts import align_pilot_kit as kit, align_pilot_session as desk, bytes_h_session as h
from tests.align.test_apple_endpoint import run_native_review
from tests.align.test_pilot3_cache import CacheAPI

ROOT = Path(__file__).resolve().parents[2]


class FakeRandom:
    def __init__(self, collision=False):
        self.collision = collision
        self.rng = random.Random(0)
        self.calls = []
        self.passed_samplers = []
        self.phase = None
        self.seed_phases = []

    def seed(self, value):
        self.calls.append(('seed', value))
        self.seed_phases.append(self.phase)
        self.rng.seed(value)

    def draw(self):
        value = 777777 if self.collision else self.rng.randrange(1000, 1000000)
        self.calls.append(('draw', value))
        return value


def native(root, seed=1, noise=0, guard=None, condition='benign', pair='spam_filter_update', collision=False):
    rng = FakeRandom(collision)
    mlx = ModuleType('mlx')
    core = ModuleType('mlx.core')
    mlx.core, core.random = core, rng
    from joulewise.adapters.mlx_runtime import MlxRuntimeAdapter
    event = MlxRuntimeAdapter._event
    def observe(adapter, event_type, phase, message, metadata=None):
        rng.phase = phase if event_type == 'phase_start' else None
        return event(adapter, event_type, phase, message, metadata)
    updates = {'seed': seed, 'condition': condition, 'sampler': kit.SAMPLER,
               'temperature': kit.SAMPLER['temperature'], 'max_episode_seconds': guard, 'enable_thinking':True,
               'task_kwargs':{'mode':'think','task_pair':pair}}
    with patch.object(MlxRuntimeAdapter, '_event', observe), patch.dict(sys.modules, {'mlx': mlx, 'mlx.core': core}), patch(
        'joulewise.align.apple.prompt_cache.native_cache_api', return_value=CacheAPI()
    ):
        bundle, status, projection = run_native_review(root, 'think', FakeClock(), prompt_cache='episode_prefix',
            spec_updates=updates, fake_rng=rng, warmup_noise=noise)
    return bundle, status, projection, rng


class SamplingTests(unittest.TestCase):
    def test_law_is_compact_sha256_big_endian_64_bits_and_condition_free(self):
        def independent(value):
            return int.from_bytes(hashlib.sha256(json.dumps(value, separators=(',', ':')).encode()).digest()[:8], 'big')
        seed = episode_seed('qwen3-30b-a3b', 'thinking_on', 'bank_transfer_2', 6)
        self.assertEqual(seed, independent(['align-p4-v1', 'qwen3-30b-a3b', 'thinking_on', 'bank_transfer_2', 6]))
        for t in range(12):
            self.assertEqual(turn_seed(seed, t), independent(['align-p4-turn-v1', seed, t]))

    def test_nonzero_temperature_alone_cannot_silently_run_greedy(self):
        spec = kit.ordered_specs()[0]
        with self.assertRaisesRegex(ValueError, 'explicit sampler'):
            EpisodeSpec.from_text(replace(spec, sampler=None).to_text())
        for changes in ({'temperature': 0}, {'top_k': -1}, {'top_p': 2}, {'min_p': float('nan')}):
            with self.assertRaises(ValueError):
                EpisodeSpec.from_text(replace(spec, sampler={**kit.SAMPLER, **changes}).to_text())

    def test_first_draw_each_turn_is_reseeded_and_warmup_cannot_shift_stream(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            a, status, projection, rng = native(root / 'a')
            b, status2, _, rng2 = native(root / 'b', noise=113)
            self.assertEqual((status.status.value, status2.status.value), ('succeeded', 'succeeded'))
            ga = [json.loads(l)['generation'] for l in (a / 'outputs/align_turns.jsonl').read_text().splitlines()]
            gb = [json.loads(l)['generation'] for l in (b / 'outputs/align_turns.jsonl').read_text().splitlines()]
            self.assertEqual([g['output_token_ids'] for g in ga], [g['output_token_ids'] for g in gb])
            cfg = BenchmarkConfig.from_mapping(h.read(a / 'config.json'))
            ep = read_episode_bundle(a)
            base = episode_seed(*seed_inputs(cfg, True), ep.task_pair, 1)
            seeds = [turn_seed(base, i) for i in range(4)]
            self.assertEqual([value for kind, value in rng.calls if kind == 'seed'], seeds)
            self.assertEqual(rng.seed_phases, ['generation_setup'] * 4)
            for i, g in enumerate(ga):
                self.assertEqual(g['sampler']['kind'], 'categorical')
                self.assertEqual(g['sampler']['per_turn_seed'], seeds[i])
                ix = rng.calls.index(('seed', seeds[i]))
                self.assertEqual(rng.calls[ix + 1][0], 'draw')
                self.assertEqual(g['output_token_ids'][-1], random.Random(seeds[i]).randrange(1000, 1000000))
                self.assertEqual(rng.passed_samplers[i], {'temp': .6, 'top_p': .95, 'top_k': 20, 'min_p': 0})
            policy = h.read(a / 'metadata.json')['workload_provenance']['sampler']['execution_policy']
            self.assertEqual(policy['seed_bits'], 64)
            self.assertEqual(policy['seed_model_id'],seed_inputs(cfg, True)[0])
            self.assertEqual(policy['seed_index'],1)
            self.assertEqual(policy['seed_task_pair'],ep.task_pair)
            self.assertEqual(policy['seed_law'], 'align-p4-v1')
            self.assertIn('sampler', policy)
            summary = desk.episode_summary(a)
            self.assertEqual(summary['accounting_check']['status'], 'pass')
            self.assertEqual(summary['sampler_check']['status'], 'pass')

    def test_guard_checks_before_next_turn_at_equality_including_replay(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            full, _, _, _ = native(root / 'full')
            ep = read_episode_bundle(full)
            guard = (ep.turns[1].start_ns - ep.start_ns) / 1e9
            for label in ('original', 'replay'):
                bundle, status, _, rng = native(root / label, guard=guard)
                self.assertEqual(status.status.value, 'succeeded')
                stopped = read_episode_bundle(bundle)
                self.assertEqual(len(stopped.turns), 1)
                self.assertIn('episode.time_guard:1', stopped.flags)
                self.assertEqual(desk.episode_summary(bundle)['end_state'], 'episode.time_guard:1')
                self.assertEqual(len([v for k,v in rng.calls if k == 'seed']), 1)
                self.assertEqual(h.read(bundle / 'metadata.json')['workload_provenance']['sampler']['execution_policy']['max_episode_seconds'], guard)

    def test_unset_spec_and_identity_preserve_frozen_pilot3_fields(self):
        plan = h.read(ROOT / 'configs/campaigns/align_pilot_v2/collection_plan.json')
        for m in plan['members']:
            text = json.dumps(m['spec'], sort_keys=True, separators=(',', ':'))
            self.assertEqual(EpisodeSpec.from_text(text).to_text(), text)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            bundle, status, _ = run_native_review(root / 'legacy', 'think', FakeClock())
            self.assertEqual(status.status.value, 'succeeded')
            legacy = h.read(bundle / 'metadata.json')['workload_provenance']['sampler']
            self.assertNotIn('execution_policy', legacy)
            sampled, _, _, _ = native(root / 'sampled')
            actual = h.read(sampled / 'metadata.json')['workload_provenance']['sampler']
            self.assertNotEqual(legacy, actual)
            self.assertEqual(legacy['kind'], 'greedy')


class KitTests(unittest.TestCase):
    def test_roster_order_replay_distance_specs_and_byte_stable_generation(self):
        members = kit.ordered_members()
        self.assertEqual(len(members), 28)
        originals = [m for m in members if not m['is_replay']]
        cells = [('spam_filter_update', 'benign'), ('bank_transfer_2', 'sabotage'),
                 ('spam_filter_update', 'sabotage'), ('bank_transfer_2', 'benign')]
        for seed in range(1,7):
            rows = [m for m in originals if m['spec'].seed == seed]
            self.assertEqual([(m['spec'].task_kwargs['task_pair'],m['spec'].condition) for m in rows], cells if seed % 2 else list(reversed(cells)))
        for i, m in enumerate(members):
            if m['is_replay']:
                j = next(j for j, n in enumerate(members) if n['spec'] == m['spec'] and not n['is_replay'])
                self.assertGreaterEqual(i-j-1,6)
        with tempfile.TemporaryDirectory() as d:
            files = kit.generate(Path(d))
            kit.generate(Path(d), check=True)
            self.assertEqual(len([p for p in files if 'episodes-' in p.name]),28)


def coefficient_bundle(root, rid, pair, condition, seed, rows):
    """Small production-layout bundle with exact rectangular synthetic rail work.

    This is an analytical fixture, not collector or hardware evidence. Turn
    energies follow the five-term law; constant interval means tile each turn.
    """
    from joulewise.align.records import Episode, Turn, to_json
    from joulewise.align.apple.sampler import _stamp_record, monotonic_ns
    from tests.align.test_apple_campaign import base_config
    root.mkdir(parents=True)
    clock = FakeClock()
    start = clock.stamp()
    turns = []
    trace = []
    identity = []
    transcript = []
    for i,r in enumerate(rows):
        before = clock.stamp()
        clock.sleep(1)
        after = clock.stamp()
        turns.append(Turn(i,monotonic_ns(before),monotonic_ns(after),r.context_tokens,r.prefill_tokens,r.decode_tokens,50))
        trace.append({'timestamp_s': after.epoch_s,'power_w':r.energy_j,'source':'powermetrics','rail':'gpu_power',
                      'interval_start_s':before.epoch_s,'interval_end_s':after.epoch_s})
        identity.append({'generation':{'prompt_token_ids':list(range(r.context_tokens+r.prefill_tokens)),
                                       'output_token_ids':list(range(r.decode_tokens))}})
        transcript.append({'role':'assistant','content':str(i)})
    end = clock.stamp()
    ep = Episode(rid,pair,condition,'A','synthetic',seed,'synthetic',monotonic_ns(start),monotonic_ns(end),
                 turns=tuple(turns),hardware={'paired_clock_stamps_ns':[_stamp_record(start),_stamp_record(end)],
                                             'task_diagnostics':{'tool_schemas':[]}},flags=('synthetic_fixture_only',))
    config = base_config()
    spec = replace(kit.ordered_specs()[0],condition=condition,seed=seed,task_kwargs={'task_pair':pair})
    config = replace(config,workload_profile=replace(config.workload_profile,name="align_episode",prompt_text=spec.to_text(),prompt_tokens=None,output_tokens=None))
    h.write(root/'config.json',config.to_dict())
    # The bound is a fixture parameter, not a meter assertion: 1 ms anchor
    # shift at max 1000 W is at most 1 J. It is propagated by the real adapter.
    offset=start.epoch_s-start.monotonic_before_s
    h.write(root/'metadata.json',{'uncertainty_evidence':{'clock_anchor':{
        'status':'bounded','method':'synthetic','wall_minus_monotonic_lower_s':offset,
        'wall_minus_monotonic_upper_s':offset,'effective_clock_anchor_bound_s':.001}}})
    h.write(root/'summary_metrics.json',{})
    (root/'outputs').mkdir()
    (root/'outputs/align_episode.json').write_text(to_json(ep))
    for name,values in (('align_turns.jsonl',identity),('align_transcript.jsonl',transcript)):
        (root/'outputs'/name).write_text(''.join(json.dumps(v)+'\n' for v in values))
    with (root/'power_trace.csv').open('w') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(trace[0]))
        writer.writeheader()
        writer.writerows(trace)
    return desk.episode_summary(root)


class AnalysisTests(unittest.TestCase):
    def test_replay_divergence_reports_exact_turn_and_token_index(self):
        import copy
        turns = [{'prompt_token_ids':[1,2], 'output_token_ids':[3,4],
                  'tool_transcript':[], 'accounting':{}} for _ in range(3)]
        a = {'identity_turns':turns}
        b = copy.deepcopy(a)
        b['identity_turns'][1]['output_token_ids'][1] = 9
        self.assertEqual(pa.first_divergence(a,b),{'status':'divergent','first_divergent_turn':1,
                                                 'field':'output_token_ids','index':1})
        b = copy.deepcopy(a)
        b['identity_turns'][2]['tool_transcript'] = ['changed tool output']
        self.assertEqual(pa.first_divergence(a,b)['field'],'tool_transcript')

    def test_thermal_tail_episode_brackets_and_fraction(self):
        ns = 10**9
        tail = thermal_onset(10*ns,20*ns,[10*ns], {'readings_monotonic_ns_level': [[9*ns,0],[19*ns,0],[21*ns,1]]})
        inside = thermal_onset(10*ns,20*ns,[10*ns], {'readings_monotonic_ns_level': [[9*ns,0],[15*ns,1],[21*ns,1]]})
        self.assertFalse(tail['os_level_nonzero_in_episode'])
        self.assertEqual(tail['throttled_fraction'],0)
        self.assertTrue(inside['os_level_nonzero_in_episode'])
        self.assertEqual(inside['throttled_fraction'],.5)
        self.assertEqual(inside['episode_bracketing_samples']['end']['at_or_after'],[21*ns,1])

    def test_per_turn_gpu_mhz_weights_active_time_and_interval_overlap(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)/'bundle'
            rows = [er.TurnRow('e','p',100,200,300,1,100,1) for _ in range(12)]
            coefficient_bundle(root,'e','p','benign',1,rows)
            ep = read_episode_bundle(root)
            start = ep.hardware['paired_clock_stamps_ns'][0]['epoch_ns']/1e9
            rich = [{'timestamp_s': start+i+1,'elapsed_ns':10**9,
                     'gpu':{'dvfm_states':[{'freq':1000,'used_ns':200_000_000},
                                           {'freq':1500,'used_ns':800_000_000}]}} for i in range(12)]
            (root/'rich_telemetry.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rich))
            observed = desk.episode_summary(root)
            # Exact integer fixture: (1000*2+1500*8)/10=1400 MHz.
            self.assertEqual(observed['per_turn_active_gpu_clock_mhz'],[1400]*12)
            self.assertEqual(observed['active_gpu_clock_mhz'],1400)

    def test_known_coefficients_loo_no_replay_leakage_transfer_and_tamper(self):
        beta = [2, .05, .2, .00003, .000002]
        members = []
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        root = Path(scratch.name)
        rng = random.Random(512)
        for pair in ('spam', 'bank'):
            for condition in ('benign', 'sabotage'):
                for seed in range(1,7):
                    rid = f'{pair}-{condition}-{seed}'
                    rows = []
                    for t in range(12):
                        c,p,d = rng.randrange(100,10000), rng.randrange(10,2000), rng.randrange(100,1000)
                        dummy = er.TurnRow(rid,pair,c,p,d,1,0,1,'additive_bound')
                        rows.append(replace(dummy,energy_j=math.fsum(x*b for x,b in zip(er.design_row(dummy),beta))))
                    energy = math.fsum(r.energy_j for r in rows)
                    summary = coefficient_bundle(root/rid,rid,pair,condition,seed,rows)
                    # Confirm the real record/trace/attribution adapter recovered
                    # the law's energy before fitting. Agreement is 0.5% of
                    # this printed episode half-width, verified above 1e6 ulps.
                    energy_bar = .005 * summary['energy']['powermetrics:gpu_power']['half_width_j']
                    self.assertGreater(energy_bar,1e6*math.ulp(energy))
                    self.assertLess(abs(summary['energy']['powermetrics:gpu_power']['joules']-energy),energy_bar)
                    members.append({'run_id':rid,'block':'A','task_pair':pair,'condition':condition,'summary':summary})
        replay = {**members[0], 'run_id':'replay'}
        members.append(replay)
        out = pa.residual_analysis(members)[0]['scopes']['registered']
        fit = out['counts_logged_headline']
        self.assertEqual(fit['distinct_trajectories'],24)
        self.assertEqual(fit['benign_distinct_trajectories'],12)
        self.assertEqual(fit['s_r_df'],20)
        # Agreement in predicted joules and each coefficient's energy
        # contribution: 0.5% of the smallest printed episode half-width,
        # strictly below 1% and checked above 1e6 ulps at the largest energy.
        bar = .005 * min(m['summary']['energy']['powermetrics:gpu_power']['half_width_j'] for m in members)
        self.assertGreater(bar, 1e6*math.ulp(max(m['summary']['energy']['powermetrics:gpu_power']['joules'] for m in members)))
        model = er.EnergyModel(**fit['model'])
        for j, value in enumerate(beta):
            max_design = max(math.fsum(er.design_row(er.TurnRow(**r))[j] for r in m['summary']['residual_rows']['True']) for m in members)
            self.assertLess(abs(model.coef[j]-value)*max_design,bar)
        self.assertFalse(any(f.startswith('unidentified_column:') for f in fit['flags']))
        for m in members:
            rows = [er.TurnRow(**r) for r in m['summary']['residual_rows']['True']]
            predicted = er.predict_episode(model,rows)[0]
            self.assertLess(abs(predicted-m['summary']['energy']['powermetrics:gpu_power']['joules']),bar)
        for r in fit['residuals']:
            self.assertNotIn('replay',r['training_trajectories'])
            if r['method']=='leave_one_trajectory_out':
                self.assertNotIn(r['run_id'],r['training_trajectories'])
        self.assertEqual(len(fit['cross_pair_transfer']),2)
        self.assertIn('quantile_at_sample_max',fit['grouped_threshold']['flags'])
        curve = [r for r in fit['tamper_detection_curve'] if r['run_id']=='spam-sabotage-1']
        self.assertEqual([r['H'] for r in curve],list(range(0,601,50)))
        self.assertGreater(curve[-1]['residual_j'],curve[0]['residual_j'])
        self.assertNotEqual(fit['model']['coef'],out['counts_withheld']['model']['coef'])

    def test_sampled_bundles_end_to_end_desk_two_replays_collision_and_thermal_scopes(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            session = root / 'session'
            rows = []
            # A deliberately degenerate fake sampling distribution returns the
            # same IDs for two independently seeded streams. This observation
            # must not change the instrument verdict or sampler provenance.
            cases = ((1,'benign','a','spam_filter_update'),(2,'benign','b','spam_filter_update'),
                     (1,'sabotage','c','spam_filter_update'),(2,'sabotage','d','spam_filter_update'),
                     (1,'benign','replay-a','spam_filter_update'),(1,'sabotage','replay-c','spam_filter_update'),
                     (1,'benign','bank-a','bank_transfer_2'),(2,'benign','bank-b','bank_transfer_2'),
                     (1,'sabotage','bank-c','bank_transfer_2'),(2,'sabotage','bank-d','bank_transfer_2'))
            for ordinal,(seed,condition,label,pair) in enumerate(cases,1):
                bundle,status,_,_ = native(root / label,seed=seed,condition=condition,pair=pair,collision=label in ('a','b','replay-a'))
                self.assertEqual(status.status.value,'succeeded')
                # Explicitly synthetic GPU-labelled power samples. Only native
                # compute and sensor values are fake; bundle read/attribution,
                # sampling, fitting and desk execution remain the real chain.
                trace = bundle / 'power_trace.csv'
                with trace.open() as stream:
                    reader = csv.DictReader(stream)
                    fields, samples = reader.fieldnames, list(reader)
                for sample in samples:
                    sample.update(source='powermetrics', rail='gpu_power')
                with trace.open('w') as stream:
                    writer = csv.DictWriter(stream,fieldnames=fields)
                    writer.writeheader()
                    writer.writerows(samples)
                rows.append({'run_id':label,'task_pair':pair,'condition':condition,'repeat':1,'ordinal':ordinal,'block':'A','bundle':bundle})
            runs = root / 'runs'
            for m in rows:
                shutil.copytree(m['bundle'],runs/m['run_id'])
                m.pop('bundle')
            measurement = root / 'measurement'
            h.write(measurement / desk.KIT / 'collection_plan.json',{'members':rows})
            custody = root / 'custody'
            h.write(custody / 'night/result.json',{})
            h.write(root / 'plan.json',{'custody_root':str(custody)})
            h.write(session / 'session.json',{'session_id':'sampled-synthetic','plan_path':str(root/'plan.json'),
                'measurement_root':str(measurement),'registration_dir':str(measurement/desk.KIT/'registration'),
                'runs_roots':{'claim':str(runs)},'inputs':{}})
            thermals={}
            for m in rows:
                ep = read_episode_bundle(runs/m['run_id'])
                onset=ep.end_ns+10**8 if m['ordinal']==3 else ep.end_ns-10**8 if m['ordinal']==4 else None
                thermals[m['run_id']]={'readings_monotonic_ns_level': [[ep.start_ns-1,0],[onset or ep.end_ns+1, int(onset is not None)]]}
            h.write(session / 'archive/derived/exclusions.json',{'members_excluded':[{'run_id':rows[i]['run_id'],'codes':['thermal.os_level_nonzero']} for i in (2,3)]})
            with patch('joulewise.align.apple.diagnostics.member_thermal_readings',return_value=thermals),redirect_stdout(io.StringIO()) as printed:
                status=desk.desk(session,harvest=False)
            report=h.read(Path(status['pilot']))
            for term in ('I4_prime','sampling.identical_independent_seeds','episode_scope_alternative_eligible_members',
                'counts_logged_headline','counts_withheld','leave_one_trajectory_out','cross_pair_transfer','tamper_detection_curve'):
                self.assertIn(term,printed.getvalue())
            replays=[r for cell in report['I4_prime'].values() for r in cell['replay_identity'] if isinstance(r,dict)]
            self.assertEqual(len(replays),2)
            self.assertTrue(report['checks']['I4_sampler_provenance'])
            self.assertTrue(all(r['status']=='identical' for r in replays))
            self.assertEqual(len(report['repeat_energy_spread']),2)
            self.assertNotIn(rows[2]['run_id'],report['registered_eligible_members'])
            self.assertIn(rows[2]['run_id'],report['episode_scope_alternative_eligible_members'])
            self.assertNotIn(rows[3]['run_id'],report['episode_scope_alternative_eligible_members'])
            # Both clocks and missing evidence are disclosed per turn.
            self.assertIn('per_turn_active_gpu_clock_mhz',printed.getvalue())


if __name__=='__main__':
    unittest.main()
