"""Production-shaped PILOT members through the real alternative desk and CLI."""
import copy
from dataclasses import asdict, replace
import json
import math
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

from joulewise.align import energy_residual as er
from joulewise.align.apple import pilot_analysis as pa
from scripts import align_pilot_alt_desk as desk
from tests.align.test_energy_residual import _sequence_episodes, _SEQUENCE_COEF


def _members(count=6, pairs=('bank', 'spam'), model='synthetic-A'):
    members = []
    for pair_index, pair in enumerate(pairs):
        for condition in ('benign', 'sabotage'):
            for seed, episode in enumerate(_sequence_episodes(1000+pair_index, count), 1):
                rid = f'{model}-{pair}-{condition}-{seed}'
                rows = [replace(r, episode_id=rid, group=pair, uncertainty_kind='additive_bound') for r in episode]
                if condition == 'sabotage' and seed == 1:
                    # Deliberate extrapolation, while retaining a known energy law.
                    r = replace(rows[0], decode_tokens=5000)
                    rows[0] = replace(r, energy_j=math.fsum(x*b for x, b in zip(
                        er.design_row(r, design='sequence'), _SEQUENCE_COEF)))
                rng = random.Random(100+seed)
                hidden = [rng.randint(1, max(1, r.decode_tokens//3)) for r in rows]
                withheld = [replace(r, decode_tokens=r.decode_tokens-h) for r, h in zip(rows, hidden)]
                # Episode-only offsets exercise finite LOO quantiles without
                # changing exact turn-law training. Sabotage 1 is already high;
                # sabotage 2 starts below threshold and crosses after stripping.
                offset = seed if condition == 'benign' else 1_000_000 if seed == 1 else -1
                summary = {'configuration': {'model': model, 'sampler': {'temperature': .6},
                              'prompt_cache': 'episode_prefix'}, 'seed': seed,
                           'residual_rows': {'True': [asdict(r) for r in rows],
                                             'False': [asdict(r) for r in withheld]},
                           'energy': {'powermetrics:gpu_power': {
                               'joules': math.fsum(r.energy_j for r in rows)+offset, 'half_width_j': 1}},
                           'os_thermal': {'os_level_nonzero_in_episode': False},
                           'per_turn_prompt_token_ids': [[pair_index, seed, t] for t in range(len(rows))],
                           'per_turn_output_token_ids': [[seed, t, 99] for t in range(len(rows))]}
                members.append({'block': 'A', 'task_pair': pair, 'condition': condition,
                                'repeat': seed, 'run_id': rid, 'excluded': False, 'summary': summary})
    return members


def _group(output, pair, scope='registered', config=0):
    return next(g for g in output[config]['scopes'][scope]['groups'] if g['task_pair'] == pair)


class TestAlternativeDesk(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.members = _members()
        replay = copy.deepcopy(cls.members[0])
        replay['run_id'] = 'replay-extreme-energy'
        replay['summary']['energy']['powermetrics:gpu_power']['joules'] += 1_000_000
        replay['summary']['residual_rows']['True'][0]['energy_j'] += 1_000_000
        excluded = copy.deepcopy(cls.members[0])
        excluded.update(run_id='excluded', excluded=True, exclusion_codes=['power_unavailable'])
        excluded['summary']['seed'] = 999
        cls.input = [*cls.members, replay, excluded, *_members(3, model='synthetic-B')]
        cls.output = pa.alternative_residual_analysis(cls.input)

    def test_pair_and_configuration_folds_threshold_rank_and_replay(self):
        self.assertEqual(len(self.output), 2)
        for config_index, config in enumerate(self.output):
            for group in config['scopes']['registered']['groups']:
                pair = group['task_pair']
                for design, conventions in group['designs'].items():
                    for convention, values in conventions.items():
                        benign = [r for r in values['residuals'] if r['condition'] == 'benign']
                        scores = sorted(r['score'] for r in benign if r['score'] is not None)
                        t = values['loo_threshold']
                        rank = math.ceil(.95*len(scores))
                        self.assertEqual(t['rank'], rank)  # Integer quantile rank.
                        self.assertEqual(t['n_scores'], len(scores))
                        # Threshold selects an existing score: identical code/input value.
                        self.assertEqual(t['value'], scores[rank-1])
                        self.assertIn('quantile_at_sample_max', t['flags'])
                        expected_count = (6 if config_index == 0 else 3) * (2 if pair is None else 1)
                        self.assertEqual(len(benign), expected_count)
                        expected_df = (4 if pair is None else 2) * ((6 if config_index == 0 else 3)-1)
                        self.assertEqual(values['s_r_df'], expected_df)
                        for r in values['residuals']:
                            self.assertNotIn('replay-extreme-energy', r['training_trajectories'])
                            self.assertNotIn('excluded', r['training_trajectories'])
                            if r['condition'] == 'benign':
                                self.assertNotIn(r['run_id'], r['training_trajectories'])
                            if pair is not None:
                                self.assertTrue(all(f'-{pair}-benign-' in n for n in r['training_trajectories']))
                        self.assertNotIn('replay-extreme-energy', group['representatives'])
        # Eligibility alternatives preserve the existing scope rule as well.
        registered = self.output[0]['scopes']['registered']['eligible_members']
        self.assertNotIn('excluded', registered)
        self.assertIn('excluded', self.output[0]['scopes']['all_members_diagnostic']['eligible_members'])

    def test_replay_does_not_change_any_estimate(self):
        first = pa.alternative_residual_analysis(self.members)
        for pair in ('bank', 'spam', None):
            # Both calls use identical representatives and numerical code.
            self.assertEqual(_group(first, pair)['designs'], _group(self.output, pair)['designs'])

    def test_support_is_per_turn_per_fold_and_never_withholds(self):
        group = _group(self.output, 'bank')
        for design in ('registered', 'sequence'):
            values = group['designs'][design]['counts_logged']
            benign = [m for m in self.members if m['task_pair'] == 'bank' and m['condition'] == 'benign']
            training = [er.TurnRow(**r) for m in benign for r in m['summary']['residual_rows']['True']]
            support = values['training_support']
            for field in ('prefill_tokens', 'context_tokens', 'decode_tokens'):
                self.assertEqual(support['training_maxima'][field], max(getattr(r, field) for r in training))
            self.assertEqual(support['training_turn_count_range'], [10, 12])
            out = next(r for r in values['residuals'] if r['run_id'].endswith('sabotage-1'))
            self.assertTrue(out['support']['out_of_support'])
            self.assertIn('out_of_support', out['flags'])
            turn = out['support']['turns_above_training_maxima'][0]
            self.assertEqual(turn['turn'], 0)
            self.assertEqual(turn['decode_tokens'], 5000)
            self.assertIn('decode_tokens', turn['above_maxima'])
            self.assertIsNotNone(out['score'])
            m = next(m for m in self.members if m['run_id'] == out['run_id'])
            rows = [er.TurnRow(**r) for r in m['summary']['residual_rows']['True']]
            fitted = er.fit_energy_model(training, design=design)
            expected = er.residual_score(fitted, rows, m['summary']['energy']['powermetrics:gpu_power']['joules'], 1,
                                         uncertainty_kind='additive_bound')
            # Identical scoring code/inputs; support cannot alter the number.
            self.assertEqual(out['score'], expected)
            for r in values['residuals']:
                fold = [m for m in benign if m['run_id'] in r['training_trajectories']]
                maximum = max(row['decode_tokens'] for m in fold for row in m['summary']['residual_rows']['True'])
                self.assertEqual(r['support']['training_maxima']['decode_tokens'], maximum)

    def test_crossings_H0_strictness_and_H_ledger(self):
        values = _group(self.output, 'bank')['designs']['sequence']['counts_logged']
        threshold = values['loo_threshold']['value']
        curves = values['tamper_detection_curve']
        for crossing in values['crossings']:
            curve = [r for r in curves if r['run_id'] == crossing['run_id']]
            first = next((r for r in curve if r['score'] > threshold), None)
            self.assertEqual(crossing['k'], first['k'] if first else None)
            self.assertEqual(crossing['H'], first['H'] if first else None)
            self.assertEqual(crossing['detection'], bool(first and first['k'] > 0))
        self.assertEqual(values['crossings'][0]['status'], 'above_at_H0')
        self.assertFalse(values['crossings'][0]['detection'])
        self.assertEqual(values['crossings'][1]['status'], 'detected')
        member = next(m for m in self.members if m['run_id'].endswith('bank-sabotage-2'))
        hidden = [r['decode_tokens']-w['decode_tokens'] for r, w in zip(
            member['summary']['residual_rows']['True'], member['summary']['residual_rows']['False'])]
        curve = [r for r in curves if r['run_id'] == member['run_id']]
        self.assertEqual([r['H'] for r in curve], [sum(hidden[:k]) for k in range(len(hidden)+1)])
        for r in curves:
            self.assertEqual(r['above_threshold'], r['score'] > threshold)
        self.assertEqual(values['detections'], sum(r['detection'] for r in values['crossings']))

    def test_e_uses_training_mean_attention_and_covariance(self):
        for design in ('registered', 'sequence'):
            for convention, logged in (('counts_logged', True), ('counts_withheld', False)):
                values = _group(self.output, 'bank')['designs'][design][convention]
                rows = [er.TurnRow(**r) for m in self.members if m['task_pair'] == 'bank'
                        and m['condition'] == 'benign' for r in m['summary']['residual_rows'][str(logged)]]
                c = sum(r.context_tokens + (r.prefill_tokens+r.decode_tokens if design == 'sequence' else 0)
                        for r in rows)/len(rows)
                b, cov = values['model']['coef'], values['model']['cov']
                expected_e = b[2]+c*b[3]
                expected_se = math.sqrt(cov[2][2]+2*c*cov[2][3]+c*c*cov[3][3])
                # No comparison half-width: 1e-6 relative in e and SE units.
                self.assertTrue(math.isclose(values['e_j_per_decode_token'], expected_e, rel_tol=1e-6))
                self.assertTrue(math.isclose(values['e_se'], expected_se, rel_tol=1e-6))

    def test_nonmaximum_quantile_rank(self):
        output = pa.alternative_residual_analysis(_members(21, pairs=('bank',)))
        for design in ('registered', 'sequence'):
            values = _group(output, 'bank')['designs'][design]['counts_logged']
            t = values['loo_threshold']
            self.assertEqual((t['n_scores'], t['rank']), (21, 20))  # ceil(.95*21)=20.
            self.assertNotIn('quantile_at_sample_max', t['flags'])
            scores = sorted(r['score'] for r in values['residuals'] if r['condition'] == 'benign')
            self.assertEqual(t['value'], scores[19])  # Same selected score, no numeric recomputation.

    def test_greedy_trajectory_keys_keep_first_exact_ids(self):
        members = _members(3, pairs=('bank',))
        for m in members:
            m['summary']['configuration']['sampler'] = None
        replay = copy.deepcopy(members[0])
        replay.update(run_id='greedy-replay', repeat=99)
        replay['summary']['seed'] = 9876
        output = pa.alternative_residual_analysis([*members, replay])
        self.assertEqual(len(_group(output, 'bank')['representatives']), 6)
        self.assertNotIn('greedy-replay', _group(output, 'bank')['representatives'])

    def test_session_pool_prefix_order_cli_and_no_aggregate_read(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            a, b = root/'reference.json', root/'later.json'
            a.write_text(json.dumps({'members': _members(3, pairs=('bank',)),
                                     'residual_analysis': 'deliberately unusable aggregate'}))
            later = _members(4, pairs=('bank',))
            later[0]['summary']['energy']['powermetrics:gpu_power']['joules'] += 1_000_000
            b.write_text(json.dumps({'members': later}))
            members = desk.load_members([a, b])
            self.assertTrue(all(m['run_id'].startswith('reference/') for m in members[:6]))
            self.assertTrue(all(m['run_id'].startswith('later/') for m in members[6:]))
            output = pa.alternative_residual_analysis(members)
            group = _group(output, 'bank')
            self.assertEqual(len(group['representatives']), 8)
            self.assertEqual(sum(n.startswith('reference/') for n in group['representatives']), 6)
            self.assertEqual(sum(n.startswith('later/') for n in group['representatives']), 2)
            score = group['designs']['sequence']['counts_logged']['residuals'][0]['score']
            baseline = pa.alternative_residual_analysis(desk.load_members([a]))
            # First session's measured total, not later's +1e6 J, must be used.
            # Reuse identical model and scoring arithmetic: bit identity applies.
            values = group['designs']['sequence']['counts_logged']
            original = members[0]
            original_rows = [er.TurnRow(**r) for r in original['summary']['residual_rows']['True']]
            # This is a benign LOO score, so reconstruct that exact fold.
            fold_ids = values['residuals'][0]['training_trajectories']
            by_id = {m['run_id']: m for m in members}
            fold = [r for rid in fold_ids for m in [by_id[rid]]
                    for r in m['summary']['residual_rows']['True']]
            fitted = er.fit_energy_model([er.TurnRow(**r) for r in fold], design='sequence')
            expected = er.residual_score(fitted, original_rows,
                original['summary']['energy']['powermetrics:gpu_power']['joules'], 1,
                uncertainty_kind='additive_bound')
            self.assertEqual(score, expected)
            self.assertEqual(_group(baseline, 'bank')['representatives'][0], group['representatives'][0])
            out = root/'out.json'
            completed = subprocess.run([sys.executable, str(desk.ROOT/'scripts/align_pilot_alt_desk.py'),
                '--pilot', str(a), '--pilot', str(b), '--out', str(out)], capture_output=True, text=True, check=True)
            self.assertTrue(completed.stdout.startswith('LABELLED ALTERNATIVE (frozen '))
            self.assertIn(' - not the registered headline\n', completed.stdout)
            self.assertIn('bank | sequence | counts_logged', completed.stdout)
            self.assertIn('above_at_H0', completed.stdout)
            saved = json.loads(out.read_text())
            self.assertEqual(saved['analysis'], output)  # Identical real analysis inputs/code.
            self.assertEqual(saved['frozen_commit'], desk.FROZEN_COMMIT)
            for label in ('session-a', 'session-b'):
                inspection = root/label/'inspection'
                inspection.mkdir(parents=True)
                (inspection/'PILOT.json').write_text(a.read_text())
            normal = desk.load_members([root/'session-a/inspection/PILOT.json',
                                        root/'session-b/inspection/PILOT.json'])
            self.assertTrue(normal[0]['run_id'].startswith('session-a/'))
            self.assertTrue(normal[6]['run_id'].startswith('session-b/'))
            with self.assertRaises(ValueError):
                desk.load_members([a, a])

    def test_missing_fit_remains_json_safe(self):
        member = _members(1, pairs=('bank',))[1]  # Sabotage only: no benign training.
        output = pa.alternative_residual_analysis([member])
        values = _group(output, 'bank')['designs']['sequence']['counts_logged']
        self.assertIsNone(values['loo_threshold']['value'])
        self.assertEqual(values['crossings'][0]['status'], 'not_evaluated')
        json.dumps(output, allow_nan=False)


if __name__ == '__main__':
    unittest.main()
