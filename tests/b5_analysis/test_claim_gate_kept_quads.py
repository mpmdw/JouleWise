"""S5 arithmetic and refusal probes: hand-built synthetic members only."""
import copy
from dataclasses import replace
import hashlib
import math
import statistics
from pathlib import Path
import unittest
from unittest import mock
from joulewise import analysis_engine as engine
from joulewise.analysis_engine.artifact import validate_claim_verdicts, render_claim_verdicts
from joulewise.analysis_engine.inputs import AnalysisInputError, REMOVED_UNIT_LABEL, _check_kept_plan
from joulewise.analysis_engine.estimators import estimate_paired_blocks
from joulewise.analysis_engine.multiplicity import adjust_p_values
from joulewise.analysis_engine.reason_kinds import DATA_REASON_CODES, CONTRACT_REASON_CODES, DEAD_REASON_CODES, LOCK_REASON_CODES
from joulewise.analysis_engine.claims import REASON_CODES
from tests.b5_analysis import fixtures_s5 as fx
from tests.test_analysis_integration import _v3_fixture_artifact

EXAMPLE = [3.1,2.9,3.3,3.,2.8,3.2,3.1,2.9,3.,2.7]

class KeptQuadTests(unittest.TestCase):
    def test_t1_plan_nine_quads_and_legacy_counterfactual(self):
        inputs = fx.arithmetic_inputs(EXAMPLE)
        with fx.arithmetic_seams(inputs,floor=1.2):
            prepared, adjusted, evaluated, loo = fx.prepared_pair(inputs)
        p = prepared['decode']; e = p['estimate']
        self.assertEqual(e.n,9); self.assertAlmostEqual(e.estimate,3.)
        self.assertAlmostEqual(e.sample_stddev,.193649,places=5)
        self.assertAlmostEqual(e.se_total,.064550,places=5)
        self.assertEqual(e.t_critical_95,2.306)
        self.assertAlmostEqual(e.metrology_aware_ci95.lower,2.8511,places=4)
        self.assertAlmostEqual(e.metrology_aware_ci95.upper,3.1489,places=4)
        self.assertAlmostEqual(e.decision_interval.lower,2.8011,places=4)
        self.assertAlmostEqual(e.decision_interval.upper,3.1989,places=4)
        self.assertIsInstance(engine._claim_raw_p(p,e),float)
        self.assertEqual(p['block_rows'][3]['reason_codes'],[REMOVED_UNIT_LABEL])
        self.assertFalse(p['block_rows'][3]['included'])
        self.assertNotIn('fixed_n_plan_incomplete',engine._base_reasons(p))
        self.assertNotIn('paired_block_incomplete',engine._base_reasons(p))
        legacy = replace(inputs,kept_quads=None,kept_units=None)
        missing = next(row for row in legacy.effective.values() if row.entry['block_number']==4)
        missing.inclusion_status='excluded'
        with fx.arithmetic_seams(legacy):
            p = engine._prepare_contrast_v3(legacy,legacy.manifest['contrasts'][0],None,None,evidence_class='current')
        self.assertIn('fixed_n_plan_incomplete',engine._base_reasons(p))

    def test_t2_five_quads_and_four_quad_loo(self):
        inputs=fx.arithmetic_inputs([2.,2.2,1.9,2.1,2.3]+[999.]*5,removed=(6,7,8,9,10))
        with fx.arithmetic_seams(inputs): p,a,v,loo=fx.prepared_pair(inputs)
        e=p['decode']['estimate']; row=loo['decode'][-1]
        self.assertEqual(e.n,5); self.assertAlmostEqual(e.estimate,2.1)
        self.assertAlmostEqual(e.sample_stddev,.15811,places=5)
        self.assertAlmostEqual(e.se_total,.070711,places=5); self.assertEqual(e.t_critical_95,2.776)
        self.assertAlmostEqual(e.metrology_aware_ci95.lower,1.9037,places=4)
        self.assertAlmostEqual(e.metrology_aware_ci95.upper,2.2963,places=4)
        self.assertAlmostEqual(e.decision_interval.lower,1.8537,places=4)
        self.assertAlmostEqual(e.decision_interval.upper,2.3463,places=4)
        self.assertAlmostEqual(e.t_critical_95*e.se_total,.19629,places=5)
        leave=estimate_paired_blocks(p['decode']['observations'][:-1],estimator=engine.ABBA_ESTIMATOR_ID)
        self.assertAlmostEqual(leave.sample_stddev,.12910,places=5)
        self.assertAlmostEqual(leave.se_total,.064550,places=5)
        self.assertEqual(leave.t_critical_95,3.182)
        self.assertAlmostEqual(leave.t_critical_95*leave.se_total,.20540,places=5)
        self.assertEqual(len(loo['decode']),5);self.assertEqual((row['n_blocks'],row['df']),(4,3))
        self.assertAlmostEqual(row['estimate'],2.05)
        self.assertAlmostEqual(row['metrology_aware_ci95']['lower'],1.8446,places=4)
        self.assertAlmostEqual(row['metrology_aware_ci95']['upper'],2.2554,places=4)
        self.assertNotIn('estimate_magnitude',row['influence_triggers'])

    def test_t3_five_quads_influence(self):
        # Holm peer: the same five differences; omitting 1.6 makes both p=.0263.
        inputs=fx.arithmetic_inputs([1.5,1.4,1.6,1.3,3.2]+[0.]*5,removed=(6,7,8,9,10))
        with fx.arithmetic_seams(inputs):p,a,v,loo=fx.prepared_pair(inputs)
        e=p['decode']['estimate'];row=loo['decode'][2]
        self.assertAlmostEqual(e.estimate,1.8);self.assertAlmostEqual(e.estimate/e.se_total,5.0912,places=4)
        self.assertAlmostEqual(e.raw_p,.0070,places=4)
        self.assertAlmostEqual(row['estimate'],1.85);self.assertAlmostEqual(row['raw_p'],.0263,places=4)
        self.assertIn('adjusted_rejection',row['influence_triggers'])
        self.assertIn('outcome',row['influence_triggers'])
        leave=estimate_paired_blocks(tuple(o for o in p['decode']['observations'] if o.block_id!=row['omitted_block_id']),estimator=engine.ABBA_ESTIMATOR_ID)
        self.assertAlmostEqual(leave.estimate/leave.se_total,4.0943,places=4)
        self.assertEqual(row['influence_triggers'],['adjusted_rejection','outcome'])
        self.assertAlmostEqual(loo['decode'][-1]['estimate'],1.45)
        self.assertEqual(loo['decode'][-1]['influence_triggers'],['estimate_magnitude'])

    def test_t4_matching_removed_stratum(self):
        inputs=fx.arithmetic_inputs(EXAMPLE)
        calls=[];real=engine._estimate_prepared_observations
        def observe(p,observations):
            calls.append([o.block_id for o in observations]);return real(p,observations)
        with fx.arithmetic_seams(inputs),mock.patch.object(engine,'_estimate_prepared_observations',side_effect=observe):
            p,a,v,loo=fx.prepared_pair(inputs)
        self.assertEqual([len(loo[cid]) for cid in ('decode','prefill')],[9,9])
        self.assertTrue(all(row['n_blocks']==8 for rows in loo.values() for row in rows))
        self.assertEqual(len(calls),18)
        for i,(left,right) in enumerate(zip(calls[::2],calls[1::2])):
            self.assertEqual([bid.removeprefix('prefill-') for bid in right],left)

    def test_t5_asymmetric_pair_uses_other_contrast_whole(self):
        inputs=fx.arithmetic_inputs([1.1,1.7,1.3,1.6,1.2,1.4,1.5,1.8,1.0,1.7],second=[3.0]*10,second_removed=(7,))
        with fx.arithmetic_seams(inputs):p,a,v,loo=fx.prepared_pair(inputs)
        bid=inputs.manifest['contrasts'][0]['block_ids'][6]
        row=next(row for row in loo['decode'] if row['omitted_block_id']==bid)
        raw=estimate_paired_blocks(tuple(o for o in p['decode']['observations'] if o.block_id!=bid),estimator=engine.ABBA_ESTIMATOR_ID).raw_p
        expected=adjust_p_values({'decode':raw,'prefill':p['prefill']['estimate'].raw_p},method='holm',m=2,alpha=.05,q=None)['decode']['adjusted_p']
        self.assertEqual(row['n_blocks'],8);self.assertEqual(row['adjusted_p'],expected)
        self.assertEqual(len(loo['decode']),9);self.assertEqual(len(loo['prefill']),9)
        self.assertNotIn('prefill-'+bid,[row['omitted_block_id'] for row in loo['prefill']])

    def test_j8_reading_ii_alternative_is_not_built(self):
        inputs=fx.arithmetic_inputs(EXAMPLE,second_removed=(7,))
        with fx.arithmetic_seams(inputs):p,a,v,loo=fx.prepared_pair(inputs)
        alternative=[bid for i,bid in enumerate(inputs.manifest['contrasts'][0]['block_ids'],1) if i not in (4,7)]
        self.assertNotEqual([row['omitted_block_id'] for row in loo['decode']],alternative)

    def check_member_code(self,code):
        inputs=fx.arithmetic_inputs(EXAMPLE)
        member=next(row for row in inputs.effective.values() if row.entry['block_number']==1)
        member.base_reason_codes=(code,)
        with fx.arithmetic_seams(inputs),self.assertRaisesRegex(AnalysisInputError,'^member_code_on_kept_unit$'):
            engine._prepare_contrast_v3(inputs,inputs.manifest['contrasts'][0],None,None,evidence_class='current')
        member.base_reason_codes=()
        removed=next(row for row in inputs.effective.values() if row.entry['block_number']==4)
        removed.base_reason_codes=(code,)
        with fx.arithmetic_seams(inputs):
            p=engine._prepare_contrast_v3(inputs,inputs.manifest['contrasts'][0],None,None,evidence_class='current')
        self.assertEqual(p['estimate'].n,9)

    def test_t6_paired_block_incomplete(self): self.check_member_code('paired_block_incomplete')
    def test_t6_fixed_n_plan_incomplete(self): self.check_member_code('fixed_n_plan_incomplete')
    def test_t6_window_evidence_precheck_missing(self): self.check_member_code('window_evidence_precheck_missing')
    def test_t6_campaign_cooldown_evidence_missing(self): self.check_member_code('campaign_cooldown_evidence_missing')
    def test_t6_idle_window_suspect(self): self.check_member_code('idle_window_suspect')

    def test_t7_floor_overrides_manifest_mde(self):
        inputs=fx.arithmetic_inputs([1.5,1.4,1.6,1.3,3.2]+[0.]*5,removed=(6,7,8,9,10),mde=100.)
        with fx.arithmetic_seams(inputs):p,a,v,loo=fx.prepared_pair(inputs)
        self.assertIn('estimate_magnitude',loo['decode'][-1]['influence_triggers'])
        legacy=fx.arithmetic_inputs([1.5,1.4,1.6,1.3,5.6,1.5,1.4,1.6,1.3,1.5],removed=(),mde=100.,block5=False)
        with fx.arithmetic_seams(legacy):p,a,v,loo=fx.prepared_pair(legacy)
        self.assertFalse(any('estimate_magnitude' in row['influence_triggers'] for row in loo['decode']))

    def test_t11_label_partition_and_artifact(self):
        inputs=fx.arithmetic_inputs(EXAMPLE)
        with fx.arithmetic_seams(inputs):
            artifact=engine.analyze_claims(Path('manifest.json'),Path('runs'),Path('floor.json'),strict_validator=lambda *_:[])
        self.assertEqual(validate_claim_verdicts(artifact),[])
        for contrast in artifact['contrasts']:
            self.assertNotIn(REMOVED_UNIT_LABEL,contrast['claim_evaluation']['reason_codes'])
            self.assertNotIn(REMOVED_UNIT_LABEL,__import__('json').dumps(contrast['loo']))
        self.assertEqual(DATA_REASON_CODES|CONTRACT_REASON_CODES|DEAD_REASON_CODES|LOCK_REASON_CODES,REASON_CODES)
        self.assertIn(REMOVED_UNIT_LABEL,CONTRACT_REASON_CODES)

    def test_t13_off_block5_bytes_match_pre_edit_baseline(self):
        raw=render_claim_verdicts(_v3_fixture_artifact())
        self.assertEqual(hashlib.sha256(raw).hexdigest(),'5e8e93e8f3106ec7637baebb0b43ee87f1fda2ba74ed61d1b931893d51a73fe7')

    def test_r1_removed_summary_is_never_read(self):
        """Writer-included removed summaries are modeled; this tests the S5 estimator only."""
        class Poison(dict):
            def get(self,*_):raise AssertionError('removed summary opened')
            def __getitem__(self,*_):raise AssertionError('removed summary opened')
            def __bool__(self):raise AssertionError('removed summary opened')
        inputs=fx.arithmetic_inputs(EXAMPLE)
        for row in inputs.effective.values():
            if row.entry['block_number']==4:row.summary=Poison(extreme=1.e99)
        with fx.arithmetic_seams(inputs):p,a,v,loo=fx.prepared_pair(inputs)
        self.assertEqual(p['decode']['estimate'].estimate,3.)

    def test_r2_kept_bundle_missing_stops(self):
        inputs=fx.arithmetic_inputs(EXAMPLE)
        key=next(key for key,row in inputs.effective.items() if row.entry['block_number']==1)
        del inputs.effective[key]
        with fx.arithmetic_seams(inputs),self.assertRaisesRegex(AnalysisInputError,'^member_code_on_kept_unit$'):
            engine._prepare_contrast_v3(inputs,inputs.manifest['contrasts'][0],None,None,evidence_class='current')

    def test_r11_kept_plan_mismatch(self):
        inputs=fx.arithmetic_inputs(EXAMPLE)
        inputs.manifest['contrasts'][0]['block_ids']=inputs.manifest['contrasts'][0]['block_ids'][:-1]
        with self.assertRaisesRegex(AnalysisInputError,'^exclusions_plan_mismatch$'):
            _check_kept_plan(inputs.manifest,inputs.kept_units)

class KeptMemberGuardsTests(unittest.TestCase):
    def test_kept_metric_missing_stops(self):
        inputs=fx.arithmetic_inputs(EXAMPLE)
        member=next(row for row in inputs.effective.values() if row.entry['block_number']==1)
        member.summary['test_value']=None
        with fx.arithmetic_seams(inputs),self.assertRaisesRegex(AnalysisInputError,'^member_code_on_kept_unit$'):
            engine._prepare_contrast_v3(inputs,inputs.manifest['contrasts'][0],None,None,evidence_class='current')
    def test_kept_positions_missing_stops(self):
        inputs=fx.arithmetic_inputs(EXAMPLE)
        inputs.manifest['blocks'][0]['position_entry_ids']=None
        with fx.arithmetic_seams(inputs),self.assertRaisesRegex(AnalysisInputError,'^member_code_on_kept_unit$'):
            engine._prepare_contrast_v3(inputs,inputs.manifest['contrasts'][0],None,None,evidence_class='current')
    def test_kept_precheck_code_stops(self):
        inputs=fx.arithmetic_inputs(EXAMPLE)
        with fx.arithmetic_seams(inputs),mock.patch.object(engine,'window_evidence_precheck',return_value={'reasons':('idle_window_suspect',)}), \
             self.assertRaisesRegex(AnalysisInputError,'^member_code_on_kept_unit$'):
            engine._prepare_contrast_v3(inputs,inputs.manifest['contrasts'][0],None,None,evidence_class='current')
    def test_sampling_validator_requires_exact_removed_label(self):
        inputs=fx.arithmetic_inputs(EXAMPLE)
        with fx.arithmetic_seams(inputs):
            artifact=engine.analyze_claims(Path('manifest.json'),Path('runs'),Path('floor.json'),strict_validator=lambda *_:[])
        artifact['contrasts'][0]['bundle_blocks']['blocks'][3]['reason_codes']=['paired_block_incomplete']
        from joulewise.analysis_engine.artifact import calculate_claim_verdicts_id
        artifact['claim_verdicts_id']=calculate_claim_verdicts_id(artifact)
        self.assertTrue(any('exact removed-unit labels' in error for error in validate_claim_verdicts(artifact)))


class MissingKeptContrastFixTests(unittest.TestCase):
    def test_f4_present_kept_map_requires_the_contrast(self):
        """Structural kept map cannot silently use pre-block-5 sampling."""
        inputs = fx.arithmetic_inputs(EXAMPLE)
        inputs = replace(inputs, kept_quads={cid: cell for cid, cell in inputs.kept_quads.items() if cid != 'decode'})
        with fx.arithmetic_seams(inputs), self.assertRaisesRegex(engine.AnalysisInputError, '^kept_quads_required$'):
            engine._prepare_contrast_v3(inputs, inputs.manifest['contrasts'][0], None, None, evidence_class='current')


class ArtifactValidatorS5FixTests(unittest.TestCase):
    """T-d: execute cross-checks against the frozen synthetic manifest."""
    def build(self, values=None, second=None, **kwargs):
        floor = kwargs.pop('floor', .2)
        inputs = fx.arithmetic_inputs(values or [1.1,1.7,1.3,1.6,1.2,1.4,1.5,1.8,1.0,1.7],
            second=second or [.2,.9,-.3,.8,.1,1.2,.4,-.2,.7,.6], second_removed=(7,), **kwargs)
        with fx.arithmetic_seams(inputs, floor=floor):
            artifact = engine.analyze_claims(Path('manifest.json'), Path('runs'), Path('floor.json'), strict_validator=lambda *_: [])
        return inputs, artifact

    def errors_after(self, artifact, manifest, edit):
        from joulewise.analysis_engine.artifact import calculate_claim_verdicts_id
        altered = copy.deepcopy(artifact)
        edit(altered)
        altered['claim_verdicts_id'] = calculate_claim_verdicts_id(altered)
        return validate_claim_verdicts(altered, frozen_manifest=manifest)

    def test_td_a01_floor_threshold_crosscheck_with_numeric_mde(self):
        inputs, artifact = self.build([1.5,1.4,1.6,1.3,3.2]+[0.]*5,
            removed=(6,7,8,9,10), mde=100., floor=1.)
        self.assertEqual(validate_claim_verdicts(artifact, frozen_manifest=inputs.manifest), [])
        errors = self.errors_after(artifact, inputs.manifest,
            lambda art: art['contrasts'][0]['loo']['rows'][-1].update(influence_triggers=[]))
        self.assertTrue(any('magnitude trigger disagrees' in error for error in errors), errors)

    def test_td_a02_j8_peer_without_row_uses_full_raw_p(self):
        inputs, artifact = self.build()
        self.assertEqual(validate_claim_verdicts(artifact, frozen_manifest=inputs.manifest), [])
        # Decode's block 7 has no peer row: prefill lost it before analysis.
        bid = inputs.manifest['contrasts'][0]['block_ids'][6]
        errors = self.errors_after(artifact, inputs.manifest,
            lambda art: next(row for row in art['contrasts'][0]['loo']['rows']
                if row['omitted_block_id'] == bid).update(adjusted_p=.8))
        self.assertTrue(any('adjusted_p' in error for error in errors), errors)

    def test_td_a03_kept_count_matches_included_rows(self):
        inputs, artifact = self.build()
        errors = self.errors_after(artifact, inputs.manifest,
            lambda art: art['contrasts'][0]['sampling'].update(kept_n=8))
        self.assertTrue(any('kept quads require exact removed-unit labels and counts' in error for error in errors), errors)

    def test_td_a04_removed_label_cannot_be_a_contrast_reason(self):
        inputs, artifact = self.build()
        errors = self.errors_after(artifact, inputs.manifest,
            lambda art: art['contrasts'][0]['claim_evaluation']['reason_codes'].append(REMOVED_UNIT_LABEL))
        self.assertTrue(any('removed-unit label is not a contrast reason' in error for error in errors), errors)

    def test_td_a05_removed_label_requires_kept_sampling(self):
        inputs, artifact = self.build()
        def strip(art):
            sampling = art['contrasts'][0]['sampling']
            sampling.pop('kept_n'); sampling.pop('removed_block_ids')
        errors = self.errors_after(artifact, inputs.manifest, strip)
        self.assertTrue(any('removed-unit labels require kept-quad sampling' in error for error in errors), errors)

    def test_td_a06_planned_count_equals_kept_plus_removed(self):
        inputs, artifact = self.build()
        errors = self.errors_after(artifact, inputs.manifest,
            lambda art: art['contrasts'][0]['sampling'].update(planned_n=11))
        self.assertTrue(any('kept quads require exact removed-unit labels and counts' in error for error in errors), errors)

    def test_td_a07_removed_ids_equal_excluded_rows(self):
        inputs, artifact = self.build()
        errors = self.errors_after(artifact, inputs.manifest,
            lambda art: art['contrasts'][0]['sampling'].update(removed_block_ids=[]))
        self.assertTrue(any('kept quads require exact removed-unit labels and counts' in error for error in errors), errors)

    def test_td_a08_numeric_mde_remains_unregistered_off_block5(self):
        inputs, artifact = self.build(removed=(), block5=False)
        self.assertEqual(validate_claim_verdicts(artifact, frozen_manifest=inputs.manifest), [])
        errors = self.errors_after(artifact, inputs.manifest, lambda art: art['contrasts'][0].update(mde=100.))
        self.assertTrue(any('v3 equivalence and MDE must remain unregistered' in error for error in errors), errors)


class J8HandHolmS5FixTests(unittest.TestCase):
    """T-h: nonzero peer variance and independent scalar t/hand Holm arithmetic."""
    @staticmethod
    def raw_p(values):
        n = len(values)
        t = statistics.mean(values) / (statistics.stdev(values) / math.sqrt(n))
        df = n - 1
        coefficient = math.exp(math.lgamma((df + 1) / 2) - math.lgamma(df / 2)) / math.sqrt(df * math.pi)
        def density(x):
            return coefficient * (1 + x * x / df) ** (-(df + 1) / 2)
        steps = 8192
        h = abs(t) / steps
        area = h / 3 * (density(0) + density(abs(t)) + sum(
            (4 if i % 2 else 2) * density(i * h) for i in range(1, steps)))
        return max(0., 1. - 2 * area)

    @staticmethod
    def hand_holm(raw):
        ranked = sorted(raw, key=raw.get)
        smaller = min(1., 2 * raw[ranked[0]])
        larger = min(1., max(smaller, raw[ranked[1]]))
        return {ranked[0]: smaller, ranked[1]: larger}

    def test_th_j8_each_kept_stratum_uses_the_correct_whole_peer(self):
        decode = [1.1,1.7,1.3,1.6,1.2,1.4,1.5,1.8,1.0,1.7]
        prefill = [.2,.9,-.3,.8,.1,1.2,.4,-.2,.7,.6]
        loaded = fx.arithmetic_inputs(decode, second=prefill, removed=(4,), second_removed=(7,))
        with fx.arithmetic_seams(loaded):
            prepared, adjusted, evaluated, loo = fx.prepared_pair(loaded)
        kept = {'decode': {k: v for k, v in enumerate(decode, 1) if k != 4},
                'prefill': {k: v for k, v in enumerate(prefill, 1) if k != 7}}
        self.assertGreater(statistics.variance(list(kept['prefill'].values())), 0)
        row_maps = {cid: {loaded.manifest['contrasts'][index]['block_ids'].index(row['omitted_block_id']) + 1: row
                         for row in loo[cid]}
                    for index, cid in enumerate(('decode', 'prefill'))}
        for cid in kept:
            self.assertEqual(set(row_maps[cid]), set(kept[cid]))
        for k in range(1, 11):
            raw = {cid: self.raw_p([v for j, v in values.items() if j != k]) for cid, values in kept.items()}
            expected = self.hand_holm(raw)
            for cid in kept:
                if k in kept[cid]:
                    with self.subTest(contrast=cid, block=k):
                        row = row_maps[cid][k]
                        self.assertAlmostEqual(row['adjusted_p'], expected[cid], places=6)
                        self.assertAlmostEqual(row['raw_p'], raw[cid], places=6)
                        self.assertEqual(row['n_blocks'], len(kept[cid]) - 1)
        # Each asymmetric row's peer stays at its whole kept n.
        self.assertEqual(len(kept['prefill']), 9)
        self.assertEqual(len(kept['decode']), 9)
