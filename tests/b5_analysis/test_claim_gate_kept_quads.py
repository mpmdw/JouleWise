"""S5 arithmetic and refusal probes: hand-built synthetic members only."""
import copy
from dataclasses import replace
import hashlib
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
