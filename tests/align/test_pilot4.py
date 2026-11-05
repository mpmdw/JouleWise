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


def native(root, seed=1, noise=0, guard=None, condition='benign', pair='spam_filter_update', collision=False,
           spec_updates=None):
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
    updates.update(spec_updates or {})
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
    @unittest.skipUnless(Path(kit.SHADE_CACHE).is_dir(), 'pinned SHADE cache is not installed')
    def test_real_offline_factory_seeds_equal_preregistration(self):
        from joulewise.align.apple.pilot import offline_shade_task
        plan = h.read(ROOT / kit.KIT / 'collection_plan.json')
        tasks = {}
        values = set()
        for m in plan['members']:
            spec = EpisodeSpec.from_text(json.dumps(m['spec']))
            pair = spec.task_kwargs['task_pair']
            if pair not in tasks:
                tasks[pair] = offline_shade_task(**spec.task_kwargs)
                self.assertFalse(tasks[pair].upstream.allow_fetch)
                self.assertIsNotNone(tasks[pair].upstream.prepare())
            config = BenchmarkConfig.from_mapping(h.read(ROOT / m['config_path']))
            actual = episode_seed(*seed_inputs(config, spec.enable_thinking), tasks[pair].task_pair, spec.seed)
            self.assertEqual(actual, m['expected_episode_seed'])
            values.add(actual)
        self.assertEqual(len(values), 22)

    def test_preregistered_table_equals_seed_law_for_indices_1_to_46(self):
        # Independently hash the protocol text's literal inputs, then check the
        # runtime/factory route too. The table is supplied, never runtime-derived.
        from joulewise.align.apple.pilot import offline_shade_task
        plan = h.read(ROOT / kit.KIT / 'collection_plan.json')
        firsts = {}
        for m in plan['members']:
            spec = EpisodeSpec.from_text(json.dumps(m['spec']))
            firsts.setdefault(spec.task_kwargs['task_pair'], (m, spec))
        for pair, (m, spec) in firsts.items():
            task = offline_shade_task(**spec.task_kwargs)
            config = BenchmarkConfig.from_mapping(h.read(ROOT / m['config_path']))
            table = kit.EXPECTED_EPISODE_SEEDS[pair]
            self.assertEqual(len(table), 46)
            for i in range(1, 47):
                raw = json.dumps(['align-p4-v1', 'qwen3-30b-a3b', 'thinking_on', 'shade/' + pair, i],
                                 separators=(',', ':'), ensure_ascii=True).encode('utf-8')
                self.assertEqual(int.from_bytes(hashlib.sha256(raw).digest()[:8], 'big'), table[i - 1])
                self.assertEqual(episode_seed(*seed_inputs(config, spec.enable_thinking), task.task_pair, i), table[i - 1])

        values = [value for table in kit.EXPECTED_EPISODE_SEEDS.values() for value in table]
        self.assertEqual(len(values), 92)
        self.assertEqual(len(set(values)), 92)
        # Protocol: MLX accepts unsigned 64-bit seeds, including 2**64 - 1.
        self.assertTrue(all(type(value) is int and 0 <= value < 2**64 for value in values))

    def test_anchor_configs_and_sizing_match_pilot9_base_sha256(self):
        # Byte-identity pins from pilot 9 plus ledger-pin base commit
        # 4b77e09c6e8286816ef7dacf6d2449ef906ac394; no lane-only Git objects needed.
        anchors = {
            1: '6d2c4ecda2022b25ccb68bc455bf783851f5d77b7b09c89737cdd0a50df4bb58',
            2: '6a5c0daaa019e66440e8860ef82163312dea84fd9aaaa28f6fd0f3b6464712a8',
            3: '56105368782182d14e5dbd125854de1dff888cad4c1c25d21aa6820fcf2062d2',
            4: '5b893b05211f36450bb60c7c01b39ec1721415022c65797d0c2fb3831d1a7bfa',
            9: '4849f43451c4fa7e28f3ca57a73be825ad709f1ab923e0804aae5e725fe82d1b',
            14: 'a0cb52b7c68b26492b078c572802b520e63adce24ab933e8e656d919c324780e',
            19: 'c6783380aef6869afdbe907ad7c9c8b97c0036874d3b6ec9728dba7dd136cfa7',
            28: 'a5dd8c51ad09a62e6fe271dfb879b6b354dbf90c7598eb4f0066bc80e30ad48f',
        }
        plan = h.read(ROOT / kit.KIT / 'collection_plan.json')
        members = [m for m in plan['members'] if m['ordinal'] in anchors]
        self.assertEqual(len(members), 8)
        for m in members:
            self.assertEqual(hashlib.sha256((ROOT / m['config_path']).read_bytes()).hexdigest(),
                             anchors[m['ordinal']], m['config_path'])
        self.assertEqual(hashlib.sha256((ROOT / kit.KIT / 'registration/sizing_b5.json').read_bytes()).hexdigest(),
                         '8e52a898c4793e56e90e496742e60cf00bf53ce3278ae292577f1ddeaef4aae6')

    def test_planning_statistics_and_spans_are_source_derived(self):
        evidence = h.read(ROOT / kit.KIT / 'registration/sizing_evidence.json')
        inputs = evidence['planning_turn_observations']
        rates = evidence['phase_rates']['A']
        self.assertEqual(inputs['n_turns'], len(rates))
        self.assertEqual(inputs['largest_fed_prefill']['prefill_s'], max(r['prefill_s'] for r in rates))
        self.assertEqual(inputs['largest_fed_prefill']['prefill_tokens'], 9683)
        self.assertEqual(inputs['largest_fed_prefill']['planning_s'], 16.842)
        self.assertEqual(inputs['slowest_decode']['decode_tok_s'], min(r['decode_tok_s'] for r in rates))
        self.assertEqual(inputs['slowest_decode']['planning_tok_s'], 41.95)
        sizing = h.read(ROOT / kit.KIT / 'registration/sizing_b5.json')['packs'][kit.PACK_ID]
        self.assertEqual(sizing['planning_case']['episode_s'], 120 + 4096 / 41.95 + 16.842)
        self.assertEqual(sizing['harvest_and_desk_planned_s'], 90 * 60)
        self.assertIn('sizing.planning_bound_unmeasured', sizing['flags'])

    def test_roster_order_replay_distance_specs_and_byte_stable_generation(self):
        members = kit.ordered_members()
        self.assertEqual(len(members), 28)
        originals = [m for m in members if not m['is_replay']]
        cells = [('spam_filter_update', 'benign'), ('bank_transfer_2', 'sabotage'),
                 ('spam_filter_update', 'sabotage'), ('bank_transfer_2', 'benign')]
        self.assertEqual(kit.SEED_INDICES, (1, *range(37, 47)))
        self.assertEqual([(m['spec'].task_kwargs['task_pair'], m['spec'].condition)
                          for m in originals[:4]], cells)
        fresh = []
        for seed in range(37, 47):
            rows = [m for m in originals if m['spec'].seed == seed]
            pairs = ['spam_filter_update', 'bank_transfer_2'] if seed % 2 else ['bank_transfer_2', 'spam_filter_update']
            self.assertEqual([(m['spec'].task_kwargs['task_pair'], m['spec'].condition)
                              for m in rows], [(p, 'benign') for p in pairs])
            fresh.extend((p, 'benign', seed) for p in pairs)
        expected = [(p, c, 1) for p, c in cells]
        remaining = iter(fresh)
        replays = dict(zip((9, 14, 19, 28), cells))
        for ordinal in range(5, 29):
            expected.append((*replays[ordinal], 1) if ordinal in replays else next(remaining))
        self.assertEqual([(m['spec'].task_kwargs['task_pair'], m['spec'].condition, m['seed_index'])
                          for m in members], expected)
        # Anchors: seed-1 originals and replays retain pilots 4-9's ordinals (1-based).
        self.assertEqual([i for i, m in enumerate(members, 1) if m['spec'].seed == kit.ANCHOR_SEED_INDEX], [1, 2, 3, 4, 9, 14, 19, 28])
        self.assertTrue(all(m['spec'].seed == kit.ANCHOR_SEED_INDEX for m in members if m['is_replay']))
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
    def test_pilot10_production_shaped_28_bundle_desk_and_one_bit_seed_flip(self):
        """Real desk/attribution/provenance/residual paths; all compute/sensors synthetic."""
        from tests.align.test_apple_campaign import base_config
        from tests.test_align_pilot_session import SessionPrepareTests
        prepared = SessionPrepareTests()
        prepared.setUp()
        self.addCleanup(prepared.doCleanups)
        state = prepared.prepared()
        self.assertEqual(state['preparation_status'], 'STAGED')
        with tempfile.TemporaryDirectory() as d:
            session = prepared.session
            collection = h.read(Path(state['registration_dir']).parent / 'collection_plan.json')
            runs = Path(state['runs_roots']['claim'])
            custody = Path(h.read(state['plan_path'])['custody_root'])
            clocks, thermals = [], []
            for m in collection['members']:
                spec = EpisodeSpec.from_text(json.dumps(m['spec']))
                # Keep the kit's seed-law inputs and controls. Only the local
                # review task, fake native model and telemetry are substitutes.
                base = base_config()
                base = replace(base, model=replace(base.model, name='qwen3-30b-a3b-mlx'),
                               run_metadata=replace(base.run_metadata, tags=('align-model=qwen3-30b-a3b',)))
                controls = {k: getattr(spec, k) for k in ('max_turns', 'max_tokens', 'max_context_tokens',
                            'enable_thinking', 'sampler', 'temperature', 'max_episode_seconds')}
                with patch('tests.align.test_apple_endpoint.base_config', return_value=base):
                    bundle, status, _, _ = native(Path(d) / m['run_id'], seed=spec.seed,
                        condition=spec.condition, pair='shade/' + m['task_pair'], spec_updates=controls)
                self.assertEqual(status.status.value, 'succeeded')
                trace = bundle / 'power_trace.csv'
                with trace.open() as stream:
                    reader = csv.DictReader(stream)
                    fields, samples = reader.fieldnames, list(reader)
                for sample in samples:
                    sample.update(source='powermetrics', rail='gpu_power')
                with trace.open('w') as stream:
                    writer = csv.DictWriter(stream, fieldnames=fields)
                    writer.writeheader()
                    writer.writerows(samples)
                target = runs / m['run_id']
                shutil.copytree(bundle, target)
                for name in ('config.json', 'metadata.json', 'summary_metrics.json'):
                    value = h.read(target / name)
                    value['run_id'] = m['run_id']
                    h.write(target / name, value)
                ep = read_episode_bundle(target)
                for event, stamp in (('start', ep.start_ns - 1), ('end', ep.end_ns + 1)):
                    clocks.append({'run_id': m['run_id'], 'event': event, 'clock': {'monotonic_ns': stamp}})
                    thermals.append({'kind': 'reading', 'finished': {'monotonic_ns': stamp},
                                     'values': {'source': 'synthetic_fixture_only', 'level': 0}})
            for path, rows in ((custody / 'collection/run_clock.jsonl', clocks),
                               (custody / 'hazards/monitor/thermal.jsonl', thermals)):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(''.join(json.dumps(r) + '\n' for r in rows))
            h.write(custody / 'night/result.json', {'chain_exit_code': 0, 'synthetic_fixture_only': True})
            h.write(session / 'archive/derived/exclusions.json', {'members_excluded': []})
            with redirect_stdout(io.StringIO()):
                status = desk.desk(session, harvest=False)
            report = h.read(Path(status['pilot']))
            self.assertEqual(status['pilot_status'], 'instrument_ok', report['checks'])
            self.assertTrue(report['checks']['I4_sampler_provenance'])
            self.assertEqual(len(report['members']), 28)
            self.assertEqual(len(report['residual_analysis']), 1)
            sabotage = {m['run_id'] for m in collection['members']
                        if m['condition'] == 'sabotage' and not m['is_replay']}
            self.assertEqual(len(sabotage), 2)
            for scope in report['residual_analysis'][0]['scopes'].values():
                for label in ('counts_logged_headline', 'counts_withheld'):
                    analysis = scope[label]
                    self.assertEqual(analysis['distinct_trajectories'], 24)
                    self.assertEqual(analysis['benign_distinct_trajectories'], 22)
                    scores = analysis['residuals']
                    self.assertEqual({r['run_id'] for r in scores if r['method'] == 'full_benign_fit'}, sabotage)
                    self.assertEqual({r['seed'] for r in scores if r['method'] == 'full_benign_fit'}, {1})
                    self.assertEqual({r['seed'] for r in scores if r['method'] == 'leave_one_trajectory_out'},
                                     {1, *range(37, 47)})
                curve = scope['counts_logged_headline']['tamper_detection_curve']
                self.assertEqual({r['run_id'] for r in curve}, sabotage)
            # Change exactly one recorded per-turn seed bit in a fresh benign
            # bundle, leaving the registered table and bundle seed unchanged.
            victim = next(m for m in collection['members'] if m['seed_index'] == 37)
            path = runs / victim['run_id'] / 'outputs/align_turns.jsonl'
            turns = [json.loads(line) for line in path.read_text().splitlines()]
            turns[0]['generation']['sampler']['per_turn_seed'] ^= 1
            path.write_text(''.join(json.dumps(t) + '\n' for t in turns))
            with redirect_stdout(io.StringIO()):
                changed = h.read(Path(desk.desk(session, harvest=False)['pilot']))
            self.assertEqual(changed['status'], 'instrument_incomplete')
            self.assertFalse(changed['checks']['I4_sampler_provenance'])
            failures = [m['run_id'] for m in changed['members'] if m['summary']['sampler_check']['status'] == 'fail']
            self.assertEqual(failures, [victim['run_id']])

    def test_missing_and_error_only_thermal_are_null_and_ineligible(self):
        for readings in ({}, {'readings_monotonic_ns_level': [[9, None], [15, None], [21, None]],
                              'errors': ['sensor error']}):
            with self.subTest(readings=readings):
                thermal = thermal_onset(10, 20, [10], readings)
                self.assertIsNone(thermal['os_level_nonzero_in_episode'])
                self.assertIsNone(thermal['throttled_fraction'])
                member = {'summary': {'os_thermal': thermal}}
                self.assertFalse(pa.episode_eligible(member))
                self.assertEqual(pa.episode_ineligibility_reasons(member),
                                 ['no_valid_os_reading_inside_or_bracketing_episode'])
        bracketed = thermal_onset(10, 20, [10], {'readings_monotonic_ns_level': [[9, 0], [21, 0]]})
        self.assertIs(bracketed['os_level_nonzero_in_episode'], False)
        self.assertEqual(bracketed['throttled_fraction'], 0)

    def test_preregistered_seed_catches_bundle_consistent_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            bundle, _, _, _ = native(Path(d))
            summary = desk.episode_summary(bundle)
            base = summary['sampler_seed_inputs']['episode_seed']
            good = desk.episode_summary(bundle, expected_episode_seed=base)
            bad = desk.episode_summary(bundle, expected_episode_seed=base + 1)
            self.assertEqual(good['sampler_check']['status'], 'pass')
            self.assertEqual(bad['sampler_check']['status'], 'fail')
            self.assertFalse(bad['sampler_seed_inputs']['preregistered_episode_seed_matches_bundle'])
            for r in bad['sampler_check']['turns']:
                self.assertEqual(r['actual']['per_turn_seed'], r['expected_per_turn_seed'])
                self.assertNotEqual(r['actual']['per_turn_seed'], r['preregistered_per_turn_seed'])

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
        # An unrelated all-turn hidden ledger must not shift logged-row H.
        # Simulate an unlogged leading turn; residual rows remain the witnesses.
        members[6]['summary']['per_turn_hidden_tokens'].insert(0, 999999)
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
                expected = desk.episode_summary(bundle)['sampler_seed_inputs']['episode_seed']
                rows.append({'run_id':label,'task_pair':pair,'condition':condition,'repeat':1,'ordinal':ordinal,
                             'block':'A','bundle':bundle,'expected_episode_seed':expected})
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
            self.assertEqual(report['repeat_token_identity'], {})
            self.assertIn('greedy-only; sampled configurations skipped', printed.getvalue())
            for pairs in report['repeat_energy_spread'].values():
                for replay in pairs:
                    refs = replay['identical_work_difference_sd_references']
                    self.assertEqual([r['df'] for r in refs], [16, 12])
                    self.assertEqual([r['difference_sd_j'] for r in refs],
                                     [math.sqrt(2) * 4.511563, math.sqrt(2) * 4.029927])
            self.assertNotIn(rows[2]['run_id'],report['registered_eligible_members'])
            self.assertIn(rows[2]['run_id'],report['episode_scope_alternative_eligible_members'])
            self.assertNotIn(rows[3]['run_id'],report['episode_scope_alternative_eligible_members'])
            # Both clocks and missing evidence are disclosed per turn.
            self.assertIn('per_turn_active_gpu_clock_mhz',printed.getvalue())
            # The fallback comes from the supplied kit, irrespective of version.
            state = h.read(session / 'session.json')
            state['runs_roots'] = {}
            state['inputs'] = {'runs_parent': str(root)}
            h.write(session / 'session.json', state)
            h.write(measurement / desk.KIT / 'plan_tree.json', {'roots': {'claim_root_leaf': 'runs'}})
            rows[0]['expected_episode_seed'] += 1
            h.write(measurement / desk.KIT / 'collection_plan.json', {'members': rows})
            with patch('joulewise.align.apple.diagnostics.member_thermal_readings',return_value=thermals),redirect_stdout(io.StringIO()):
                changed = h.read(Path(desk.desk(session, harvest=False)['pilot']))
            self.assertEqual(changed['runs_root'], str(runs))
            self.assertTrue(all(m['summary'] for m in changed['members']))
            self.assertFalse(changed['checks']['I4_sampler_provenance'])


if __name__=='__main__':
    unittest.main()
