"""S8 replay byte equality, closed requests, supply binding and issuer gates."""
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest import mock
from joulewise import paper_custody as c, paper_reported_energy as energy, paper_reported_energy_issuer as issuer
from joulewise.b5_analysis.windows import AnalysisRefusal
from joulewise.authentication_io import V2AuthenticationReadSession
from joulewise.analysis_engine.artifact import finalize_claim_verdicts, render_claim_verdicts, validate_claim_verdicts
from joulewise.analysis_engine.claim_side_bound import produce_claim_side_bound
from joulewise.analysis_engine.claims import evaluate_claim
from tests.b5_analysis import fixtures_s8 as f
from tests.fixtures.paper_custody import repin


def encoded(value):return (json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode()


class ClaimReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.f=f.replay_fixture()

    def test_S8F5_manifest_and_floor_request_digests_precede_engine(self):
        for key in ('analysis_manifest_sha256', 'floor_artifact_sha256'):
            ctx = self.ctx()
            request = json.loads(self.f.request)
            request[key] = '0'*64
            ctx.raws[c.InputRole.CLAIM_REPLAY_REQUEST] = encoded(request)
            with self.subTest(key=key), mock.patch('joulewise.analysis_engine.analyze_claims') as engine:
                self.assertEqual(self.gate(ctx).validator_codes, ('claim_verdicts_replay_refused',))
                engine.assert_not_called()

    def test_S8F5_evidence_root_census_precedes_engine(self):
        for change in ('missing', 'extra'):
            ctx = self.ctx()
            request = json.loads(self.f.request)
            if change == 'missing':
                request['evidence_roots'].pop('a10')
            else:
                request['evidence_roots']['extra'] = 'alpha'
            ctx.raws[c.InputRole.CLAIM_REPLAY_REQUEST] = encoded(request)
            with self.subTest(change=change), mock.patch('joulewise.analysis_engine.analyze_claims') as engine:
                self.assertEqual(self.gate(ctx).validator_codes, ('claim_verdicts_replay_refused',))
                engine.assert_not_called()

    def test_S8F5_worktree_index_must_equal_anchored_blob(self):
        raw = self.f.index_path.read_bytes()
        try:
            self.f.index_path.write_bytes(raw+b' ')
            with mock.patch('joulewise.analysis_engine.analyze_claims') as engine:
                self.assertEqual(self.gate(self.ctx()).validator_codes, ('claim_verdicts_replay_refused',))
                engine.assert_not_called()
        finally:
            self.f.index_path.write_bytes(raw)

    def test_S8F5_engine_receives_block5_objects_and_roots(self):
        from joulewise import analysis_engine
        from joulewise.b5_analysis import windows
        selected = {}
        real_select = windows.select_analysed_attempts
        def select(*args, **kwargs):
            value = real_select(*args, **kwargs)
            selected.update(value)
            return value
        with mock.patch.object(analysis_engine, 'analyze_claims', wraps=analysis_engine.analyze_claims) as engine, \
             mock.patch.object(windows, 'select_analysed_attempts', side_effect=select):
            result = self.gate(self.ctx())
        self.assertTrue(result.authentic, result.validator_codes)
        self.assertTrue(result.admitted)
        engine.assert_called_once()
        kw = engine.call_args.kwargs
        for key in ('kept_units', 'archive_contexts', 'gamma_archive'):
            self.assertIs(kw[key], self.f.built[key])
        self.assertIs(kw['neg8_harvest_archive'], self.f.built['gamma_archive'].window.archive_root)
        self.assertIs(kw['legacy_l1_mechanics'], False)
        self.assertIsNone(kw['output_path'])
        expected = {root_id: selected[pack].claim_runs_root
                    for root_id, pack in json.loads(self.f.request)['evidence_roots'].items()}
        self.assertEqual(kw['evidence_roots'], expected)

    def ctx(self):return replace(self.f.ctx,raws=deepcopy(self.f.ctx.raws))

    def gate(self,ctx):
        # Finalized-manifest custody and floor acceptance are separate seams.
        # Claim validation and side-bound validation are never mocked here.
        with f.replay_seams(self.f),mock.patch('joulewise.analysis_manifest_v3.validate_finalized_analysis_manifest_v3',return_value=()),mock.patch.object(c,'_validate_floor_acceptance'):
            return c._claim_issuance_gate(ctx)

    def bind(self,ctx,artifact,raw=None):
        raw=render_claim_verdicts(artifact) if raw is None else raw
        ctx.raws[c.InputRole.CLAIM_VERDICTS]=raw
        ctx.raws[c.InputRole.CLAIM_SIDE_BOUND]=produce_claim_side_bound(raw,finalized_manifest=self.f.manifest,floor_artifact=self.f.loaded.floor_artifact)
        request=json.loads(self.f.request);request['claim_verdicts_sha256']=hashlib.sha256(raw).hexdigest()
        ctx.raws[c.InputRole.CLAIM_REPLAY_REQUEST]=encoded(request)

    def test_T14_real_engine_writer_validates_and_grants(self):
        self.assertEqual(validate_claim_verdicts(self.f.artifact,frozen_manifest=self.f.manifest),[])
        result=self.gate(self.ctx())
        self.assertTrue(result.authentic,result.validator_codes);self.assertTrue(result.admitted)
        self.assertIn(c._RenderGrant('outcome','decode'),result.grants)

    def forgery(self):
        artifact=deepcopy(self.f.artifact)
        for row in artifact['contrasts']:
            row['estimator']['estimate']+=15
            for interval in (row['estimator']['repeat_point_CI95'],row['estimator']['metrology_aware_CI95'],row['deterministic_bounds']['decision_interval']):
                interval['lower']+=15;interval['upper']+=15
            for loo in row['loo']['rows']:
                loo['estimate']+=15
                for interval in (loo['metrology_aware_ci95'],loo['decision_interval']):
                    interval['lower']+=15;interval['upper']+=15
            row['claim_evaluation']=evaluate_claim(estimate=row['estimator']['estimate'],metrology_aware_ci95=row['estimator']['metrology_aware_CI95'],decision_interval=row['deterministic_bounds']['decision_interval'],floor_gate_j=row['floor']['active_floor_j'],adjusted_rejected=row['multiplicity']['rejected'],base_reason_codes=row['claim_evaluation']['reason_codes'],equivalence=row['equivalence'],claim_role=row['claim_role'],confirmatory_status=row['sampling']['confirmatory_status'],evidence_class='current',hypothesized_direction=row['hypothesized_direction'])
        return finalize_claim_verdicts(artifact)

    def test_R11_consistent_15J_forgery_caught_only_by_replay(self):
        forged=self.forgery();self.assertEqual(validate_claim_verdicts(forged,frozen_manifest=self.f.manifest),[])
        ctx=self.ctx();self.bind(ctx,forged)
        result=self.gate(ctx)
        self.assertFalse(result.authentic);self.assertEqual(result.validator_codes,('claim_verdicts_replay_mismatch',))
        # M16's counterfactual: C1 alone admits these internally coherent bytes.
        with mock.patch.object(c,'_replay_claim_verdicts',return_value=ctx.raws[c.InputRole.CLAIM_VERDICTS]):
            self.assertTrue(self.gate(ctx).admitted)

    def test_R12_equal_numbers_sorted_bytes_refuse(self):
        ctx=self.ctx();self.bind(ctx,self.f.artifact,encoded(self.f.artifact))
        self.assertEqual(self.gate(ctx).validator_codes,('claim_verdicts_replay_mismatch',))

    def test_R13_closed_request_checks_precede_engine(self):
        for key,value in [('claim_verdicts_sha256','0'*64),('window_index_sha256','0'*64),('legacy_l1_mechanics',True),('evidence_roots',{'a10':'/counterfactual/path','window_c':'beta'}),('extra',1)]:
            ctx=self.ctx();request=json.loads(self.f.request);request[key]=value;ctx.raws[c.InputRole.CLAIM_REPLAY_REQUEST]=encoded(request)
            with self.subTest(key=key),mock.patch('joulewise.analysis_engine.analyze_claims') as engine:
                self.assertEqual(self.gate(ctx).validator_codes,('claim_verdicts_replay_refused',));engine.assert_not_called()
        ctx=self.ctx();del ctx.raws[c.InputRole.CLAIM_REPLAY_REQUEST]
        with mock.patch('joulewise.analysis_engine.analyze_claims') as engine:
            result=self.gate(ctx)
            self.assertFalse(result.authentic);self.assertFalse(result.admitted);engine.assert_not_called()

    def test_R14_engine_error_is_code_only(self):
        with mock.patch('joulewise.analysis_engine.analyze_claims',side_effect=ValueError('7331')):
            result=self.gate(self.ctx())
        self.assertEqual(result.validator_codes,('claim_verdicts_replay_refused',));self.assertNotIn('7331',repr(result.validator_codes))

    def test_Q3_manifest_index_is_passed_only_with_request(self):
        for present in (True,False):
            ctx=self.ctx()
            if not present:del ctx.raws[c.InputRole.CLAIM_REPLAY_REQUEST]
            with self.subTest(request_present=present), \
                 mock.patch('joulewise.analysis_manifest_v3.validate_finalized_analysis_manifest_v3',
                            return_value=('synthetic_manifest_refusal',)) as validator, \
                 mock.patch('joulewise.analysis_engine.analyze_claims') as engine:
                result=c._claim_issuance_gate(ctx)
            self.assertEqual('window_index' in validator.call_args.kwargs,present)
            if present:self.assertEqual(validator.call_args.kwargs['window_index'],self.f.repo/c._B5_WINDOW_INDEX_PATH)
            self.assertFalse(result.authentic);self.assertFalse(result.admitted);engine.assert_not_called()

    def test_R13_no_request_hand_built_context_unmocked_manifest_validator(self):
        ctx=self.ctx();del ctx.raws[c.InputRole.CLAIM_REPLAY_REQUEST]
        with mock.patch('joulewise.analysis_engine.analyze_claims') as engine:
            result=c._claim_issuance_gate(ctx)
        self.assertFalse(result.authentic);self.assertFalse(result.admitted);engine.assert_not_called()

    def test_T15_replay_reads_do_not_enter_session(self):
        with f.replay_seams(self.f):outside=c._replay_claim_verdicts(self.ctx(),json.loads(self.f.request))
        with V2AuthenticationReadSession() as session:
            before=session.records
            with f.replay_seams(self.f):inside=c._replay_claim_verdicts(self.ctx(),json.loads(self.f.request))
            self.assertEqual(session.records,before)
        self.assertEqual(inside,outside);self.assertEqual(inside,self.f.raw)

    def test_T16_top_level_evidence_class_rejected_unmocked(self):
        ctx=self.ctx();artifact=deepcopy(self.f.artifact);artifact['evidence_class']='current'
        self.bind(ctx,artifact)
        self.assertFalse(self.gate(ctx).authentic)
        self.assertTrue(validate_claim_verdicts(artifact,frozen_manifest=self.f.manifest))


class SupplyCensusTests(unittest.TestCase):
    def entry(self,role,family):
        entry=repin.fixture_role_entry(family)
        entry.update(mode='production',issuance_gate_id='synthetic.v1',subjects=['synthetic'])
        spec=next(s for s in c._FAMILY_SPECS.values() if s.family==family)
        for r in spec.roles_for('production')[len(entry['inputs']):]:
            entry['inputs'].append({'role':r.value,'base':'runs_root','path':r.value+'.json','authority':'generated','expected_sha256':'0'*64})
        return entry,spec

    def load(self,root,role,spec,map_value):
        with V2AuthenticationReadSession() as session,mock.patch.object(c,'_git_blob',return_value=encoded(map_value)):
            return c._load_supply_entry(session,root,'synthetic',role,spec,runs_root=root)

    def test_T17_census_matches_classic_plus_its_own_binding(self):
        role='synthetic.role';entry,spec=self.entry(role,'claim_evidence')
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);classic={'schema_version':c._SUPPLY_MAP_SCHEMA,'pending_roles':{},'roles':{role:entry}}
            expected=self.load(root,role,spec,classic)
            keys=('inputs','inventory','receipt','source_census')
            census={'schema_version':'joulewise.paper_supply_census.v1','supply_role':role,**{k:entry[k] for k in keys}}
            path=root/'census.json';raw=encoded(census);path.write_bytes(raw)
            dynamic={k:v for k,v in entry.items() if k not in keys};dynamic['binding_census']={'base':'runs_root','path':'census.json'}
            value={**classic,'roles':{role:dynamic}}
            actual=self.load(root,role,spec,value)
            self.assertEqual(actual.sources,expected.sources);self.assertEqual(actual.inventory,expected.inventory);self.assertEqual(actual.receipt,expected.receipt)
            self.assertEqual(actual.source_census,expected.source_census)
            self.assertIsNone(expected.binding_census)
            self.assertEqual(actual.binding_census,c._BoundFile('runs_root',Path('census.json'),hashlib.sha256(raw).hexdigest(),c.InputRole.AUTHENTICATED_SOURCE,'generated'))
            for change in ('other_role','mixed','fixture'):
                bad=deepcopy(value);path.write_bytes(raw)
                if change=='other_role':path.write_bytes(encoded({**census,'supply_role':'other.role'}))
                if change=='mixed':bad['roles'][role]['inputs']=entry['inputs']
                if change=='fixture':bad['roles'][role]['mode']='test_fixture_non_issuing'
                with self.subTest(change=change),self.assertRaises(c.PaperCustodyRefusal) as cm:self.load(root,role,spec,bad)
                self.assertEqual(cm.exception.code,'paper_custody_supply_map_invalid')

    def test_T17_committed_map_schema_three_roles_no_digest(self):
        raw=Path('configs/paper_supply/supply_map.json').read_bytes();value=json.loads(raw)
        self.assertIsNone(re.search(rb'[0-9a-f]{64}',raw));self.assertEqual(value['pending_roles'],{});self.assertEqual(len(value['roles']),3)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for role,entry in value['roles'].items():
                classic,spec=self.entry(role,entry['family'])
                census={'schema_version':'joulewise.paper_supply_census.v1','supply_role':role,**{k:classic[k] for k in ('inputs','inventory','receipt','source_census')}}
                path=root/entry['binding_census']['path'];path.parent.mkdir(exist_ok=True);path.write_bytes(encoded(census))
                resolved=self.load(root,role,spec,value)
                self.assertEqual(resolved.subjects,tuple(entry['subjects']))

    def test_R13b_production_missing_request_refuses_both_entry_forms(self):
        role='synthetic.claim';entry,spec=self.entry(role,'claim_evidence')
        entry['inputs']=[row for row in entry['inputs'] if row['role']!='claim_replay_request']
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            classic={'schema_version':c._SUPPLY_MAP_SCHEMA,'pending_roles':{},'roles':{role:entry}}
            keys=('inputs','inventory','receipt','source_census')
            census={'schema_version':'joulewise.paper_supply_census.v1','supply_role':role,
                    **{k:entry[k] for k in keys}}
            (root/'census.json').write_bytes(encoded(census))
            dynamic={k:v for k,v in entry.items() if k not in keys}
            dynamic['binding_census']={'base':'runs_root','path':'census.json'}
            for form,value in [('classic',classic),('binding_census',{**classic,'roles':{role:dynamic}})]:
                with self.subTest(form=form),self.assertRaises(c.PaperCustodyRefusal) as cm:
                    self.load(root,role,spec,value)
                self.assertEqual(cm.exception.code,'paper_custody_supply_map_invalid')

    def test_T17_census_path_cannot_be_one_of_its_listed_bindings(self):
        role='synthetic.claim';entry,spec=self.entry(role,'claim_evidence')
        entry['source_census'].append({'base':'runs_root','path':'census.json',
            'authority':'generated','expected_sha256':'0'*64})
        keys=('inputs','inventory','receipt','source_census')
        census={'schema_version':'joulewise.paper_supply_census.v1','supply_role':role,
                **{k:entry[k] for k in keys}}
        dynamic={k:v for k,v in entry.items() if k not in keys}
        dynamic['binding_census']={'base':'runs_root','path':'census.json'}
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'census.json').write_bytes(encoded(census))
            with self.assertRaises(c.PaperCustodyRefusal) as cm:
                self.load(root,role,spec,{'schema_version':c._SUPPLY_MAP_SCHEMA,'pending_roles':{},'roles':{role:dynamic}})
            self.assertEqual(cm.exception.code,'paper_custody_evidence_ambiguous')


class ReportedGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = f.indexed_reported_fixture()
        with f.indexed_reported_seams(cls.p):
            cls.projection = f.issue_indexed_reported(cls.p)

    def ctx(self):
        p = self.p
        raws = {c.InputRole.EXTRACTION_SPEC: p.spec_raw, c.InputRole.EXTRACTION_REPORT: b'{}',
                c.InputRole.G2A_SELECTION: p.selection_raw, c.InputRole.PROMPT_PIN: p.prompt_raw,
                c.InputRole.WHOLE_WINDOW_BASIS: encoded(p.row['evaluation_basis'])}
        return c._GateContext('reported_energy_parents', 'synthetic.energy', 'production', 'reported-energy.v1',
                              tuple(x['cell_id'] for x in self.projection['cells']), p.repo, p.window.claim,
                              'synthetic', (), (), raws, None)

    def gate(self, ctx, error=None):
        def sealed_blob(repository, head, path):
            return self.p.spec_raw if path == 'configs/campaigns/d117_floor_qwen3-8b_v5/extraction_spec.json' else b'other sealed bytes'
        with mock.patch('joulewise.floor_extraction.validate_extraction_spec', return_value=[]), \
             mock.patch('joulewise.floor_extraction.validate_d117_mint_consumption_report', return_value=[]), \
             mock.patch.object(energy, '_validate_registered_spec'), \
             mock.patch.object(c, '_git_blob', side_effect=sealed_blob), \
             mock.patch.object(c, '_tracked_window_index', return_value=self.p.index), \
             mock.patch.object(issuer, 'issue_pack', return_value=deepcopy(self.projection), side_effect=error):
            return issuer.reported_energy_issuance_gate(ctx)

    def assert_refused(self, result, code):
        self.assertEqual(result, c._FamilyReplay(False, False, (), (code,)))

    def test_S8F6_selection_byte_mismatch(self):
        ctx = self.ctx()
        ctx.raws[c.InputRole.G2A_SELECTION] += b' '
        self.assert_refused(self.gate(ctx), 'reported_energy_parent_mismatch')

    def test_S8F6_basis_digest_and_object_mismatch(self):
        for raw in (encoded({'sha256': '0'*64}), b'[]\n'):
            ctx = self.ctx()
            ctx.raws[c.InputRole.WHOLE_WINDOW_BASIS] = raw
            with self.subTest(raw=raw):
                self.assert_refused(self.gate(ctx), 'reported_energy_parent_mismatch')

    def test_S8F6_analysis_refusal_becomes_code_only(self):
        self.assert_refused(self.gate(self.ctx(), AnalysisRefusal('synthetic_refusal')),
                            'reported_energy_replay_refused')

    def test_S8F8_replay_exceptions_are_code_only(self):
        for error in (RuntimeError('7331'), KeyError('7331'), OSError('/Users/x/7331'),
                      energy.PaperReportedEnergyRefusal('paper_reported_energy_spec_invalid')):
            with self.subTest(error=type(error).__name__):
                result = self.gate(self.ctx(), error)
                self.assert_refused(result, 'reported_energy_replay_refused')
                self.assertNotIn('7331', repr(result))

    def test_S8F8_process_interrupts_propagate(self):
        for error in (KeyboardInterrupt(), SystemExit(7)):
            with self.subTest(error=type(error).__name__), self.assertRaises(type(error)):
                self.gate(self.ctx(), error)

    def test_T18_projection_grants_and_parent_or_spec_counterfactuals(self):
        p=f.indexed_reported_fixture()
        with f.indexed_reported_seams(p):projection=f.issue_indexed_reported(p)
        self.assertEqual(len(projection['cells']),2)
        self.assertEqual(projection['refused_cells'][0]['code'],'paper_reported_energy_record_invalid')
        raws={c.InputRole.EXTRACTION_SPEC:p.spec_raw,c.InputRole.EXTRACTION_REPORT:b'{}',
              c.InputRole.G2A_SELECTION:p.selection_raw,c.InputRole.PROMPT_PIN:p.prompt_raw,
              c.InputRole.WHOLE_WINDOW_BASIS:encoded(p.row['evaluation_basis'])}
        ctx=c._GateContext('reported_energy_parents','synthetic.energy','production','reported-energy.v1',tuple(x['cell_id'] for x in projection['cells']),p.repo,p.window.claim,'synthetic',(),(),raws,None)
        def sealed_blob(repository,head,path):
            return p.spec_raw if path=='configs/campaigns/d117_floor_qwen3-8b_v5/extraction_spec.json' else b'other sealed bytes'
        real_issue=issuer.issue_pack
        def issue(index,pack,**kwargs):
            # Only the registered synthetic pack table/pins are injected. Both
            # the indexed composition and projection run their real functions.
            with mock.patch.object(issuer,'issue_pack',real_issue):
                return f.issue_indexed_reported(p,index,pack,**kwargs)
        def gate(context):
            with f.indexed_reported_seams(p),mock.patch('joulewise.floor_extraction.validate_extraction_spec',return_value=[]),mock.patch('joulewise.floor_extraction.validate_d117_mint_consumption_report',return_value=[]),mock.patch.object(c,'_git_blob',side_effect=sealed_blob),mock.patch.object(c,'_tracked_window_index',return_value=p.index),mock.patch.object(issuer,'issue_pack',side_effect=issue):
                return issuer.reported_energy_issuance_gate(context)
        result=gate(ctx);self.assertTrue(result.authentic);self.assertTrue(result.admitted)
        self.assertEqual(result.reported_energy_projection,c._freeze_json(projection));self.assertEqual(len(result.grants),2)
        self.assertEqual(set(result.grants),{c._RenderGrant('cell',subject) for subject in ctx.subjects})
        self.assertFalse(gate(replace(ctx,subjects=(*ctx.subjects,p.spec['reported_energy_cells'][1]['cell_id']))).admitted)
        bad=deepcopy(raws);bad[c.InputRole.PROMPT_PIN]+=b' '
        self.assertEqual(gate(replace(ctx,raws=bad)).validator_codes,('reported_energy_parent_mismatch',))
        with f.indexed_reported_seams(p),mock.patch('joulewise.floor_extraction.validate_extraction_spec',return_value=[]),mock.patch('joulewise.floor_extraction.validate_d117_mint_consumption_report',return_value=[]),mock.patch.object(c,'_git_blob',return_value=b'other sealed bytes'):
            self.assertEqual(issuer.reported_energy_issuance_gate(ctx).validator_codes,('reported_energy_spec_not_a_sealed_pack',))
