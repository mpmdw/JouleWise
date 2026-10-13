"""Synthetic sensitivity seam and pass checks; expensive fixtures cached per module."""
from copy import deepcopy
from dataclasses import replace
import math
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest import mock

from joulewise import whole_window as ww, floor_extraction as fe
from joulewise import paper_reported_energy_issuer as issuer
from joulewise.b5_analysis.windows import AnalysisRefusal
from tests.b5_analysis import fixtures_s8 as s8


class SeamTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.member = s8.production_member()
        cls.pack = s8.synthetic_pack()

    def session(self, bound):
        p = self.member
        context = replace(p.context, sensitivity_bound_s=bound)
        session = ww.AuthenticatedConsumptionSession(p.bundle.parent, {p.bundle.name},
            calibration_ledger_snapshot=p.session.calibration_ledger_snapshot, archive_context=context)
        with mock.patch.object(ww, '_current_strict_summary', return_value=True), \
             mock.patch.object(ww, '_verify_instrument_calibration', return_value=(p.pre, None)):
            session._prepare(bundle_paths={p.bundle.name:p.bundle}, policy=SimpleNamespace(calibration_bracketing=object()))
        return session

    def test_t1_unset_is_neutral(self):
        p = self.member
        self.assertEqual(p.context, replace(p.context, sensitivity_bound_s=None))
        session = self.session(None)
        self.assertEqual(session.summary_for(p.bundle.name), p.session.summary_for(p.bundle.name))
        provenance = session.provenance_for(p.bundle.name)
        self.assertEqual(provenance, p.session.provenance_for(p.bundle.name))
        self.assertEqual(set(provenance), {'consumption_semantics_id', 'minted_bound_dominated',
            'minted_fiducial_bound_s', 'operative_fiducial_bound_s', 'calibration_bracket',
            'calibration_ledger_snapshot', 'operative_envelopes'})

    def test_t2_real_reducer_and_unchanged_bracket(self):
        p = self.member
        session = self.session(p.operative + .006)
        self.assertTrue(session.ready, session.refusal_reasons)
        self.assertEqual(session.operative_fiducial_bound_s, p.operative + .006)
        self.assertEqual(session.calibration_bracket, p.session.calibration_bracket)
        summary = session.summary_for(p.bundle.name)
        primary_summary = p.session.summary_for(p.bundle.name)
        self.assertEqual(summary['phase_energy_j'], primary_summary['phase_energy_j'])
        self.assertGreater(summary['energy_anchor_shift_envelopes']['/phase_energy_j/decode']['max_abs_delta_j'],
            primary_summary['energy_anchor_shift_envelopes']['/phase_energy_j/decode']['max_abs_delta_j'])
        primary = p.session.provenance_for(p.bundle.name)['operative_envelopes']
        sens = session.provenance_for(p.bundle.name)
        self.assertEqual(sens['sensitivity_bound_s'], p.operative + .006)
        growth = []
        for key, value in primary.items():
            other = sens['operative_envelopes'][key]
            self.assertEqual(value['point_j'], other['point_j'])
            self.assertGreaterEqual(other['half_width_j'], value['half_width_j'])
            growth.append(other['half_width_j'] > value['half_width_j'])
        self.assertTrue(any(growth))
        self.assertEqual(self.session(p.operative).summary_for(p.bundle.name), p.session.summary_for(p.bundle.name))

    def test_sensitivity_provenance_remains_unmintable(self):
        p = self.member
        primary = self.session(None)
        def basis(session):
            return {'consumption_semantics_id':ww.MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
                'calibration_bracket_set':ww._calibration_bracket_basis(session.calibration_bracket),
                'consumption_provenance':{p.bundle.name:session.provenance_for(p.bundle.name)}}
        occurrences = [{'bundle_id':p.bundle.name,'bundle_path':p.bundle.name}]
        self.assertTrue(ww._consumption_provenance_valid(basis(primary),occurrences,
            runs_root=p.bundle.parent,consumption_session=primary))
        sensitivity = self.session(p.operative+.006)
        self.assertFalse(ww._consumption_provenance_valid(basis(sensitivity),occurrences,
            runs_root=p.bundle.parent,consumption_session=sensitivity))

    def test_r1_below_operative_refuses_before_serving_summary(self):
        session = self.session(self.member.operative - 1e-6)
        self.assertFalse(session.ready)
        self.assertIn('sensitivity_bound_below_operative', session.refusal_reasons)
        self.assertIsNone(session.summary_for(self.member.bundle.name))

    def test_r2_context_validation(self):
        for bound in (True, -.001, float('nan'), float('inf'), 10**1000, '0.04'):
            with self.subTest(bound=bound), self.assertRaisesRegex(ValueError, '^sensitivity_bound_s_invalid$'):
                replace(self.member.context, sensitivity_bound_s=bound)
        self.assertIs(type(replace(self.member.context, sensitivity_bound_s=0).sensitivity_bound_s), float)

    def test_r3_context_identity(self):
        session = self.session(None)
        self.assertFalse(session._accept_archive_context(replace(self.member.context,
            sensitivity_bound_s=self.member.operative + .006)))
        self.assertIn('archive_context_changed', session.refusal_reasons)

    def test_t3_issuer_acceptance_and_wrong_bound_refusals(self):
        p = self.pack
        context = replace(p.context, sensitivity_bound_s=.05)
        for actual in (.05, .02, .06):
            session = SimpleNamespace(summary_for=p.session.summary_for,
                provenance_for=lambda bid: {'operative_fiducial_bound_s': actual})
            with s8.pack_seams(p):
                call = lambda: issuer.normalized_rows(p.spec['reported_energy_cells'][0],
                    p.kept.for_reported_cell(p.spec, 0), session=session, runs_root=p.root,
                    context=context, binding={'selection_sha256':'a'*64,'prompt_pin_sha256':'b'*64,'whole_window_basis_sha256':'c'*64}, kept_units=p.kept, strict_validator=lambda *a:(),
                    allowances={'gross_energy': {'allowance_j': .1}})
                if actual == .05:
                    self.assertTrue(call())
                else:
                    with self.assertRaisesRegex(AnalysisRefusal, '^operative_bound_not_the_window_bracket$'):
                        call()
        with s8.pack_seams(p), mock.patch.object(issuer, 'archive_context_operative_bound_s', return_value=.06) as helper:
            with self.assertRaisesRegex(AnalysisRefusal, '^operative_bound_not_the_window_bracket$'):
                issuer.normalized_rows(p.spec['reported_energy_cells'][0], p.kept.for_reported_cell(p.spec, 0),
                    session=p.session, runs_root=p.root, context=context, binding={'selection_sha256':'a'*64,'prompt_pin_sha256':'b'*64,'whole_window_basis_sha256':'c'*64}, kept_units=p.kept,
                    strict_validator=lambda *a:(), allowances={})
            helper.assert_called_with(context)

    def test_t3_extractor_acceptance_and_wrong_bound_refusals(self):
        from tests.b5_analysis.test_floor_kept_units import arithmetic, units_for, arithmetic_seams
        root, spec = arithmetic()
        context = ww.ArchiveContext(root, window_bracket={'b_fiducial_s':.04}, sensitivity_bound_s=.05)
        for actual in (.05, .02, .06):
            session = SimpleNamespace(ready=True, refusal_reasons=(),
                consumption_semantics_id=ww.MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
                provenance_for=lambda run: {'operative_fiducial_bound_s':actual})
            def member(**kw):
                return replace(fe._unevaluated_member(slot=kw['slot'], bundle_id=kw['bundle_id'],
                    block_id=kw['block_id'], position=kw['position'], excluded=False),
                    value_j=10., anchor_shift_bound_j=0., consumption_provenance={'operative_fiducial_bound_s':actual})
            with arithmetic_seams(), mock.patch.object(fe, 'AuthenticatedConsumptionSession', return_value=session), \
                 mock.patch.object(fe, '_evaluate_member', side_effect=member):
                call = lambda: fe.extract_cells(root, spec, kept_units=units_for(spec), archive_context=context)
                if actual == .05:
                    self.assertTrue(call()['cells'])
                else:
                    with self.assertRaisesRegex(AnalysisRefusal, '^operative_bound_not_the_window_bracket$'):
                        call()

    def test_t3_gamma_loader_uses_context_bound(self):
        from tests.b5_analysis import fixtures_s5 as s5
        from joulewise.analysis_engine import inputs as im
        # This existing fixture reaches the genuine GAMMA member loop. Its
        # floor-evidence binder is a named seam, independently covered below.
        with s5.loader_case() as case:
            context = replace(case.context, sensitivity_bound_s=.05)
            case.session.provenance_for = lambda bid: {'operative_fiducial_bound_s':.05}
            kwargs = {'archive_contexts':{str(case.runs.resolve()):context}}
            self.assertTrue(case.call(**kwargs).effective)
            for wrong in (.02, .06):
                case.session.provenance_for = lambda bid: {'operative_fiducial_bound_s':wrong}
                with self.assertRaisesRegex(im.AnalysisInputError, '^operative_bound_not_the_window_bracket$'):
                    case.call(**kwargs)
            case.session.provenance_for = lambda bid: {'operative_fiducial_bound_s':.05}
            with mock.patch.object(im, 'archive_context_operative_bound_s', return_value=.06) as helper:
                with self.assertRaisesRegex(im.AnalysisInputError, '^operative_bound_not_the_window_bracket$'):
                    case.call(**kwargs)
                helper.assert_called_with(context)

    def test_t3_floor_binder_helper_moves_refusal(self):
        from joulewise.analysis_engine import inputs as im
        root = self.pack.root
        context = ww.ArchiveContext(root, window_bracket={'b_fiducial_s':.04}, sensitivity_bound_s=.05)
        artifact = {'cells':[{'cell_id':'synthetic-floor',
            'key':{'metric':'phase_energy_j.decode','window_class':'phase'},
            'absolute':{'bundle_observations':[{'bundle_id':'synthetic-member'}]},
            'provenance':{'absolute':{'evidence_root_id':'alpha'}}}]}
        authenticated = im.AuthenticatedFloorArtifact(artifact, b'{}', 'a'*64, frozenset({'alpha'}))
        class AfterBound(Exception):
            pass
        reader = SimpleNamespace(raw_metadata=mock.Mock(side_effect=AfterBound))
        for expected, actual, exception in ((.05,.05,AfterBound),(.05,.02,im.AnalysisInputError),
                (.05,.06,im.AnalysisInputError),(.06,.05,im.AnalysisInputError)):
            session = SimpleNamespace(ready=True,summary_for=lambda bid:{},
                provenance_for=lambda bid:{'operative_fiducial_bound_s':actual})
            with mock.patch.object(im,'archive_snapshot',return_value=None), \
                 mock.patch.object(im,'AuthenticatedConsumptionSession',return_value=session), \
                 mock.patch.object(im,'whole_window_refusal_reasons',return_value=()), \
                 mock.patch.object(im,'_campaign_order_binding_problems',return_value=()), \
                 mock.patch.object(im,'BundleReader',return_value=reader), \
                 mock.patch.object(im,'archive_context_operative_bound_s',return_value=expected) as helper:
                with self.assertRaises(exception) as caught:
                    im.bind_floor_artifact_evidence(artifact, root/'absent-floor.json', {'alpha':root},
                        strict_validator=lambda *a:(), _authenticated_floor=authenticated,
                        archive_contexts={str(root.resolve()):context})
                if exception is im.AnalysisInputError:
                    self.assertEqual(str(caught.exception),'operative_bound_not_the_window_bracket')
                helper.assert_called_with(context)

    def test_t4_comparative_sweep_and_plain_report(self):
        from tests.test_detection_floor import TestTwoSharedEdgeCommonModeFloor as Replay
        from tests.test_floor_extraction import RegisteredCommonModeExtractionTests
        blocks = [{'block_id':f'b{i:02d}', 'members':{pos:f'b{i:02d}-{pos.lower()}'
            for pos in ('A1','B1','B2','A2')}} for i in range(1,len(Replay.REPLAY_DELTAS)+1)]
        def member(**kw):
            delta = Replay.REPLAY_DELTAS[int(kw['block_id'][1:])-1]
            return replace(fe._unevaluated_member(slot=kw['slot'],bundle_id=kw['bundle_id'],
                block_id=kw['block_id'],position=kw['position'],excluded=False),
                value_j=10.+delta if kw['position'].startswith('B') else 10.,
                anchor_shift_bound_j=0., operative_anchor_envelope={'half_width_j':0.})
        def extract(bound):
            session = SimpleNamespace(ready=True,refusal_reasons=(),calibration_bracket=Replay.bracket(),
                operative_fiducial_bound_s=bound or Replay.OPERATIVE_BOUND_S, sensitivity_bound_s=bound)
            with mock.patch.object(fe,'_evaluate_member',side_effect=member), \
                 mock.patch.object(fe,'_common_mode_block_inputs_from_evidence',side_effect=Replay.extracted_replay_inputs()) as builder:
                report = fe.extract_comparative_cell(cell_id='synthetic',metric='phase_energy_j.decode',
                    window_class='phase',blocks=blocks,runs_root=Path('synthetic'),cooldowns={},
                    consumption_session=session,estimator=fe.COMMON_MODE_ESTIMATOR_ID,
                    estimator_registration=fe.two_shared_edge_common_mode_registration(),
                    calibration_basis=RegisteredCommonModeExtractionTests.calibration_basis())
                self.assertTrue(all(c.kwargs['shared_edge_bound_s'] == session.operative_fiducial_bound_s
                    for c in builder.call_args_list))
                return report
        primary = extract(None)
        equal = extract(Replay.OPERATIVE_BOUND_S)
        self.assertIsInstance(primary, fe._RegisteredCellReport)
        self.assertIs(type(equal), fe.CellReport)
        self.assertEqual(equal.floor, primary.floor)
        larger = extract(Replay.OPERATIVE_BOUND_S + .006)
        self.assertIs(type(larger), fe.CellReport)
        self.assertIsNotNone(larger.floor)

    def test_helper_invalid_brackets(self):
        for bound in (True, -1., math.inf, math.nan, '0.04', None):
            self.assertIsNone(ww.archive_context_operative_bound_s(ww.ArchiveContext(Path('.'),
                window_bracket={'b_fiducial_s':bound})))
        self.assertEqual(ww.archive_context_operative_bound_s(self.member.context), self.member.operative)


# The following consumers are arithmetic seams. The contrast consumer executes
# the production B4 composition, with S5's loader/member-physics seams only.
from functools import lru_cache
from joulewise.b5_analysis import sensitivity as sensitivity_module
from joulewise.b5_analysis.archive import ArchiveHandle
from joulewise.b5_analysis.bracket import BMax, WindowBracket
from joulewise.b5_analysis.kept_units import KeptUnits
from joulewise.b5_analysis.windows import AnalysedWindow
from joulewise import analysis_engine as engine
from joulewise.analysis_engine.inputs import FloorResolution
from tests.b5_analysis import fixtures_s5 as s5

EXAMPLE = [3.1,2.9,3.3,3.,2.8,3.2,3.1,2.9,3.,2.7]


@lru_cache(maxsize=1)
def pass_fixture():
    root = Path('.scratch-s9b/tmp/s9-arithmetic').resolve()
    windows, contexts, brackets, kept, specs, projections, reports = {}, {}, {}, {}, {}, {}, {}
    loaded = s5.arithmetic_inputs(EXAMPLE)
    bounds = {'alpha':.038,'beta':.045,'gamma':.037}
    for pack, bound in bounds.items():
        window = AnalysedWindow(pack, 'synthetic-'+pack, 'synthetic-plan-'+pack, 1,
            root/pack/'archive', 'a'*64, root/pack/'runs', root/pack/'bound', root,
            root/'measurement', 'b'*40, False, False, SimpleNamespace(record_shape='pin2'))
        windows[pack] = window
        contexts[pack] = ww.ArchiveContext(window.archive_root,
            window_bracket={'status':'passed','b_fiducial_s':bound})
        brackets[pack] = WindowBracket(window,'sealed',contexts[pack].window_bracket,bound,
                                      500,'c'*64,'no_harvest_digest','d'*64)
        kept[pack] = (replace(loaded.kept_units,window=window) if pack=='gamma' else
                      KeptUnits(window,'e'*64,'f'*64,'a'*64,{}, {}, {}))
        if pack == 'gamma':
            continue
        specs[pack] = {'reported_energy_cells':[{'cell_id':pack+'-r'+str(i)} for i in range(3)],
                      'cells':[{'cell_id':'component-17','kind':'absolute'},
                               {'cell_id':'component-23','kind':'comparative'}]}
        projections[pack] = {'cells':[{'cell_id':pack+'-r'+str(i),'mean_j':10.,'lower_j':9.5,'upper_j':10.5,
            'interval':{'h_j':.2,'B_j':.3},'attribution_floor':{'value_j':.1},
            'binding':{'selection_sha256':'a'*64,'prompt_pin_sha256':'b'*64,'whole_window_basis_sha256':'c'*64}}
            for i in (0,2)], 'refused_cells':[{'cell_id':pack+'-r1','code':'paper_reported_energy_record_invalid'}]}
        reports[pack] = {'manifest_id':None,'cells':[
            {'cell_id':'component-17','kind':'absolute','floor':{'drift_widened_guarded_floor_j':1.1},
             'whole_window_drift_allowance':{'allowance_j':.1}},
            {'cell_id':'component-23','kind':'comparative','floor':{'drift_widened_guarded_floor_j':1.25},
             'whole_window_drift_allowance':{'allowance_j':.1}}]}
    artifact = {'cells':[{'cell_id':'minted-'+pack,'floor_abs_j':1.1,'floor_cmp_j':1.25,'floor_gate_j':1.25,
        'provenance':{kind:{'calibration_cell_id':'component-17' if kind=='absolute' else 'component-23',
                            'evidence_root_id':'root-'+pack} for kind in ('absolute','comparative')}}
        for pack in ('alpha','beta')]}
    return SimpleNamespace(windows=windows,contexts=contexts,brackets=brackets,kept=kept,
        specs=specs,projections=projections,reports=reports,artifact=artifact,loaded=loaded,
        evidence_roots={'root-'+pack:windows[pack].claim_runs_root for pack in ('alpha','beta')},
        gamma_archive=ArchiveHandle(windows['gamma'], {}, {}),root=root)


class PassHarness:
    def __init__(self):
        base = pass_fixture()
        self.f = SimpleNamespace(**{name: deepcopy(value) if name in
            ('specs','projections','reports','artifact','loaded') else value
            for name,value in vars(base).items()})
        self.calls = []
        self.hold_D = False
        self.hold_floors = False
        self.decrease = False
        self.shift = None
        self.refusal_change = None
        self.contrast_shift = False
        self.primary = self.primary_verdicts()

    def resolutions(self):
        return [FloorResolution(status='exact',artifact_id='synthetic-floor',artifact_sha256='a'*64,
            source_cell_ids=(cell['cell_id'],),transport_group_id=None,transport_rule_id=None,
            floor_abs_j=cell['floor_abs_j'],floor_cmp_j=cell['floor_cmp_j'],floor_gate_j=cell['floor_gate_j'],
            reason_codes=()) for cell in self.f.artifact['cells']]

    def math(self, D):
        import contextlib
        stack = contextlib.ExitStack()
        stack.enter_context(s5.arithmetic_seams(self.f.loaded))
        stack.enter_context(mock.patch.object(engine,'_resolve_contrast_floor',side_effect=lambda *a,**k:self.resolutions()))
        stack.enter_context(mock.patch.object(engine,'deterministic_bounds',return_value=({'E_clock_anchor_shift_bound_j':D/2,'E_interpolation_joint_edge_bound_j':0.},())))
        return stack

    def primary_verdicts(self):
        # Primary arithmetic seam: base evaluations. A separate test compares
        # the pass with the full engine's primary verdict at equal bounds.
        with self.math(2.6):
            rows = sensitivity_module._engine_contrasts(
                gamma_manifest_path=self.f.root/'manifest.json',
                runs_root=self.f.windows['gamma'].claim_runs_root,
                floor_artifact_path=self.f.root/'floor.json',kept_units=self.f.kept['gamma'],
                archive_contexts={str(w.claim_runs_root.resolve()):self.f.contexts[p]
                                  for p,w in self.f.windows.items()},
                gamma_archive=self.f.gamma_archive,evidence_roots=self.f.evidence_roots,
                strict_validator=lambda *a:(),
                sensitivity_floors={c['cell_id']:{k:c[k] for k in sensitivity_module._FLOOR_KEYS}
                                    for c in self.f.artifact['cells']})
        return {'schema_version':'joulewise.claim_verdicts.v1','contrasts':rows}

    def set_floors(self, absolute, comparative):
        for pack in ('alpha','beta'):
            self.f.reports[pack]['cells'][0]['floor']['drift_widened_guarded_floor_j'] = absolute
            self.f.reports[pack]['cells'][1]['floor']['drift_widened_guarded_floor_j'] = comparative
        for cell in self.f.artifact['cells']:
            cell.update(floor_abs_j=absolute,floor_cmp_j=comparative,floor_gate_j=max(absolute,comparative))
        self.primary = self.primary_verdicts()

    def project(self, spec, kept, *, context, **kwargs):
        pack = kept.window.pack
        self.calls.append(('project',pack,context,kwargs))
        delta = context.sensitivity_bound_s - self.f.brackets[pack].b_fiducial_s
        result = deepcopy(self.f.projections[pack])
        for cell in result['cells']:
            if delta > 0:
                sign = -1 if self.decrease else 1
                growth = delta*(1 if self.decrease else 10)
                cell['interval']['B_j'] += sign*growth
                cell['lower_j'] -= sign*growth
                cell['upper_j'] += sign*growth
                cell['attribution_floor']['value_j'] += sign*growth
            if self.shift == 'mean':
                cell['mean_j'] = math.nextafter(cell['mean_j'], math.inf)
            elif self.shift == 'h':
                cell['interval']['h_j'] = math.nextafter(cell['interval']['h_j'], math.inf)
            elif self.shift == 'equal':
                cell['attribution_floor']['value_j'] = math.nextafter(cell['attribution_floor']['value_j'], math.inf)
        if self.refusal_change == 'computed':
            result['refused_cells'] = []
            cell = deepcopy(result['cells'][0]);cell['cell_id']=pack+'-r1';result['cells'].append(cell)
        elif self.refusal_change == 'code':
            result['refused_cells'][0]['code'] = 'paper_reported_energy_binding_mismatch'
        return result

    def extract(self, runs_root, spec, *, kept_units, archive_context, **kwargs):
        pack = kept_units.window.pack
        self.calls.append(('extract',pack,archive_context,kwargs))
        result = deepcopy(self.f.reports[pack])
        if archive_context.sensitivity_bound_s > self.f.brackets[pack].b_fiducial_s and not self.hold_floors:
            for i, cell in enumerate(result['cells']):
                cell['floor']['drift_widened_guarded_floor_j'] = (.9 if self.decrease else (1.6 if i==0 else 1.4))
        return result

    def contrasts(self, **kwargs):
        context = kwargs['archive_contexts'][str(self.f.windows['gamma'].claim_runs_root.resolve())]
        self.calls.append(('contrasts','gamma',context,kwargs))
        larger = context.sensitivity_bound_s is not None and context.sensitivity_bound_s > self.f.brackets['gamma'].b_fiducial_s
        D = 2.6 if self.hold_D or not larger else 2.4 if self.decrease else 3.
        with self.math(D):
            rows = sensitivity_module._engine_contrasts(**kwargs)
        self.last_contrast_rows = deepcopy(rows)
        if self.contrast_shift:
            rows[0]['estimator']['estimate'] = math.nextafter(rows[0]['estimator']['estimate'],math.inf)
        return rows

    def call(self, maximum=.04, **overrides):
        kwargs = dict(extraction_specs=self.f.specs,primary_projections=self.f.projections,
            primary_extraction_reports=self.f.reports,floor_artifact=self.f.artifact,
            floor_artifact_path=self.f.root/'floor.json',gamma_manifest_path=self.f.root/'manifest.json',
            primary_claim_verdicts=self.primary,evidence_roots=self.f.evidence_roots,strict_validator=lambda *a:(),
            gamma_archive=self.f.gamma_archive,
            consumers=sensitivity_module.SensitivityConsumers(self.project,self.extract,self.contrasts))
        kwargs.update(overrides)
        return sensitivity_module.sensitivity_pass(self.f.windows,self.f.kept,self.f.contexts,self.f.brackets,
            maximum if isinstance(maximum,BMax) else BMax(maximum,456,500),**kwargs)


class PassTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass_fixture()

    def setUp(self):
        self.h = PassHarness()

    def test_t5_D_rederived_moves_word(self):
        self.h.set_floors(1.2,1.2);self.h.hold_floors=True
        result = self.h.call()
        row = result['contrasts'][0]
        self.assertEqual(row['primary']['outcome'],'direction_supported')
        self.assertEqual(row['sensitivity']['D_j'],3.)
        self.assertEqual(row['sensitivity']['outcome'],'not_resolvable')
        self.assertFalse(row['outcome_equals_primary'])
        self.assertIn('deterministic_bound_obscures_direction',
            self.h.last_contrast_rows[0]['claim_evaluation']['reason_codes'])
        estimate = self.h.primary['contrasts'][0]['estimator']
        self.assertAlmostEqual(estimate['estimate'],3.)
        self.assertAlmostEqual(estimate['SE_total'],.064550,places=6)
        self.assertAlmostEqual(estimate['metrology_aware_CI95']['lower'],2.8511,places=4)
        self.h.hold_D=True
        held = self.h.call()['contrasts'][0]
        self.assertEqual(held['sensitivity']['outcome'],'direction_supported')
        self.assertTrue(held['outcome_equals_primary'])
        # With only the floor moved (still below dbar), D held, the word stays.
        self.h.hold_floors=False
        self.assertTrue(self.h.call()['contrasts'][0]['outcome_equals_primary'])

    def test_t6_both_forms_compose_gate(self):
        result = self.h.call()
        row = result['floor_cells'][0]
        self.assertEqual(row['primary'],{'floor_abs_j':1.1,'floor_cmp_j':1.25,'floor_gate_j':1.25,'allowance_j':.1})
        self.assertEqual(row['sensitivity'],{'floor_abs_j':1.6,'floor_cmp_j':1.4,'floor_gate_j':1.6,'allowance_j':.1})
        self.assertEqual(result['contrasts'][0]['sensitivity']['floor_gate_j'],1.6)

    def test_t7_each_window_own_context(self):
        result = self.h.call()
        self.assertEqual({pack:row['b_sens_s'] for pack,row in result['windows'].items()},
                         {'alpha':.04,'beta':.045,'gamma':.04})
        self.assertEqual({pack:row['widened'] for pack,row in result['windows'].items()},
                         {'alpha':True,'beta':False,'gamma':True})
        self.assertEqual([row[:2] for row in self.h.calls],
                         [('project','alpha'),('extract','alpha'),('project','beta'),('extract','beta'),('contrasts','gamma')])
        for kind,pack,context,kwargs in self.h.calls:
            self.assertIsNot(context,self.h.f.contexts[pack])
            self.assertEqual(context.sensitivity_bound_s,result['windows'][pack]['b_sens_s'])
            self.assertEqual(context.window_bracket,self.h.f.contexts[pack].window_bracket)
            if kind == 'contrasts':
                for floor_pack in ('alpha','beta'):
                    root = str(self.h.f.windows[floor_pack].claim_runs_root.resolve())
                    self.assertIs(kwargs['archive_contexts'][root],self.h.f.contexts[floor_pack])
            else:
                self.assertEqual(kwargs['evaluation_basis_sha256'],'c'*64)

    def test_t8_equal_bounds_equal_values(self):
        result = self.h.call(.03)
        self.assertTrue(all(not row['widened'] for row in result['windows'].values()))
        for key in ('reported_cells','floor_cells'):
            for row in result[key]:
                if row.get('status')!='refused':
                    self.assertTrue(row['equals_primary'])
                    self.assertEqual(row['primary'],row['sensitivity'])
        for row in result['contrasts']:
            self.assertTrue(row['outcome_equals_primary'])
            self.assertEqual(row['primary'],row['sensitivity'])
        self.assertEqual(len(self.h.calls),5)

    def test_t9_widened_monotonic_and_independent_means(self):
        result = self.h.call(.05)
        for key in ('reported_cells','floor_cells','contrasts'):
            for row in result[key]:
                if row.get('status')!='refused':
                    self.assertTrue(row['not_below_primary'])
        for row in result['reported_cells']:
            if row['status']=='computed':
                self.assertEqual(row['primary']['mean_j'],row['sensitivity']['mean_j'])
                self.assertEqual(row['primary']['h_j'],row['sensitivity']['h_j'])
                self.assertTrue(row['mean_and_half_width_equal_primary'])

    def test_t10_isolation_two_maxima(self):
        inputs = [self.h.f.projections,self.h.f.reports,self.h.f.artifact,self.h.primary]
        before = [ww.canonical_sha256(value) for value in inputs]
        first = self.h.call(.04)
        self.assertEqual(before,[ww.canonical_sha256(value) for value in inputs])
        second = self.h.call(.05)
        self.assertNotEqual(ww.canonical_sha256(first),ww.canonical_sha256(second))
        self.assertEqual(before,[ww.canonical_sha256(value) for value in inputs])
        for value in inputs:
            self.assertNotIn('b_max',value)
            self.assertNotIn('windows',value)
            self.assertNotIn('sensitivity',value)

    def test_t11_shape_determinism_and_structure(self):
        value = self.h.call()
        self.assertEqual(ww.canonical_sha256(value),ww.canonical_sha256(self.h.call()))
        self.assertEqual(set(value),{'schema_version','label','b_max','windows','reported_cells','floor_cells','contrasts'})
        self.assertEqual(set(value['b_max']),{'value_s','attained_by_sequence','T'})
        for row in value['windows'].values():
            self.assertEqual(set(row),{'plan_id','b_op_s','b_sens_s','widened'})
        reported_values={'mean_j','h_j','B_j','lower_j','upper_j','attribution_floor_j'}
        for row in value['reported_cells']:
            if row['status']=='refused':
                self.assertEqual(set(row),{'pack','cell_id','status','code'})
            else:
                self.assertEqual(set(row),{'pack','cell_id','status','primary','sensitivity',
                    'mean_and_half_width_equal_primary','equals_primary','not_below_primary'})
                self.assertEqual(set(row['primary']),reported_values)
                self.assertEqual(set(row['sensitivity']),reported_values)
        for row in value['floor_cells']:
            self.assertEqual(set(row),{'pack','cell_id','primary','sensitivity','equals_primary','not_below_primary'})
            for kind in ('primary','sensitivity'):
                self.assertEqual(set(row[kind]),{'floor_abs_j','floor_cmp_j','floor_gate_j','allowance_j'})
        for row in value['contrasts']:
            self.assertEqual(set(row),{'contrast_id','floor_cell_ids','primary','sensitivity',
                'bound_independent_values_equal_primary','outcome_equals_primary','not_below_primary'})
            for kind in ('primary','sensitivity'):
                self.assertEqual(set(row[kind]),{'floor_abs_j','floor_cmp_j','floor_gate_j','D_j','outcome'})
        structure = sensitivity_module.to_structure_record(value)
        self.assertEqual(set(structure),{'schema_version','record_sha256','counts'})
        self.assertEqual(structure['record_sha256'],ww.canonical_sha256(value))
        self.assertEqual(structure['counts'],{'reported_cells':6,'floor_cells':2,'contrasts':2})
        def walk(item):
            self.assertNotIsInstance(item,float)
            if isinstance(item,dict):
                for key,value_ in item.items():
                    self.assertNotIn(key,{'widened','outcome','outcome_equals_primary'})
                    walk(value_)
            elif isinstance(item,list):
                for value_ in item:walk(value_)
        walk(structure)
        self.assertNotIn(str(self.h.f.root),str(value))

    def test_t12_design_B_max_example(self):
        from joulewise.b5_analysis import bracket as br
        from tests.b5_analysis import fixtures_s2 as s2
        acceptance = deepcopy(br.calibration.load_calibration_acceptance_bound())
        acceptance['derivation_corpus']['members'] = [{'b_fiducial_s':'.036'}]*24
        raw = s2.toy_ledger(T=500)
        maximum = br.block_b_max(acceptance,br.ledger_prefix(raw,s2.pin_at(raw,500)))
        result = self.h.call(maximum)
        self.assertEqual(result['b_max'],{'value_s':.04,'attained_by_sequence':456,'T':500})
        self.assertEqual(result['windows']['alpha']['b_op_s'],.038)
        self.assertEqual(result['windows']['alpha']['b_sens_s'],.04)
        self.assertTrue(result['windows']['alpha']['widened'])
        self.assertEqual(result['windows']['beta']['b_op_s'],.045)
        self.assertEqual(result['windows']['beta']['b_sens_s'],.045)
        self.assertFalse(result['windows']['beta']['widened'])

    def test_r4_primary_composition_self_check_before_consumers(self):
        self.h.f.artifact['cells'][0]['floor_cmp_j'] = math.nextafter(1.25,math.inf)
        with self.assertRaisesRegex(AnalysisRefusal,'^sensitivity_floor_composition_differs_from_mint$'):
            self.h.call()
        self.assertEqual(self.h.calls,[])

    def test_r5_equal_bound_shift_refuses(self):
        self.h.shift='equal'
        with self.assertRaisesRegex(AnalysisRefusal,'^sensitivity_differs_at_primary_bound$'):
            self.h.call(.03)

    def test_r6_bound_independent_mean_half_width_and_dbar(self):
        for shift in ('mean','h'):
            self.h.shift=shift
            with self.assertRaisesRegex(AnalysisRefusal,'^sensitivity_changed_bound_independent_value$'):
                self.h.call(.05)
        self.h.shift=None;self.h.contrast_shift=True
        with self.assertRaisesRegex(AnalysisRefusal,'^sensitivity_changed_bound_independent_value$'):
            self.h.call(.05)

    def test_r7_exact_three_pack_inputs(self):
        for missing in (True,False):
            windows=dict(self.h.f.windows)
            if missing:windows.pop('gamma')
            else:windows['fourth']=windows['gamma']
            with self.assertRaisesRegex(AnalysisRefusal,'^sensitivity_inputs_invalid$'):
                sensitivity_module.sensitivity_pass(windows,self.h.f.kept,self.h.f.contexts,self.h.f.brackets,
                    BMax(.04,456,500),extraction_specs={},primary_projections={},primary_extraction_reports={},
                    floor_artifact={},floor_artifact_path=Path('none'),gamma_manifest_path=Path('none'),
                    primary_claim_verdicts={},evidence_roots={},strict_validator=lambda *a:(),
                    gamma_archive=self.h.f.gamma_archive)
        self.assertEqual(self.h.calls,[])

    def test_wrong_window_gamma_archive_refuses_before_consumers(self):
        beta_archive = ArchiveHandle(self.h.f.windows['beta'], {}, {})
        with self.assertRaisesRegex(AnalysisRefusal,'^sensitivity_inputs_invalid$'):
            self.h.call(gamma_archive=beta_archive)
        self.assertEqual(self.h.calls,[])

    def test_r8_refused_cell_must_stay_refused_same_code(self):
        for mode in ('computed','code'):
            self.h.refusal_change=mode
            with self.assertRaisesRegex(AnalysisRefusal,'^sensitivity_changed_bound_independent_value$'):
                self.h.call(.05)

    def test_false_monotonicity_is_recorded(self):
        self.h.decrease=True
        value = self.h.call(.05)
        self.assertTrue(any(not row['not_below_primary'] for row in value['floor_cells']))
        self.assertTrue(all(not row['not_below_primary'] for row in value['contrasts']))

    def test_primary_contexts_never_mutated(self):
        contexts = dict(self.h.f.contexts)
        brackets = dict(self.h.f.brackets)
        self.h.call(.05)
        self.assertEqual(self.h.f.contexts,contexts)
        self.assertEqual(self.h.f.brackets,brackets)
        self.assertTrue(all(context.sensitivity_bound_s is None for context in contexts.values()))

    def test_full_primary_verdict_equal_bound_neutrality(self):
        with self.h.math(2.6):
            full = engine.analyze_claims(self.h.f.root/'manifest.json',
                self.h.f.windows['gamma'].claim_runs_root,self.h.f.root/'floor.json',strict_validator=lambda *a:())
        value = self.h.call(.03,primary_claim_verdicts=full)
        self.assertTrue(all(row['outcome_equals_primary'] for row in value['contrasts']))

    def test_equal_floor_and_contrast_shifts_refuse(self):
        original_extract = self.h.extract
        def extract(*args,**kwargs):
            result = original_extract(*args,**kwargs)
            value = result['cells'][0]['floor']['drift_widened_guarded_floor_j']
            result['cells'][0]['floor']['drift_widened_guarded_floor_j'] = math.nextafter(value,math.inf)
            return result
        consumers = sensitivity_module.SensitivityConsumers(self.h.project,extract,self.h.contrasts)
        with self.assertRaisesRegex(AnalysisRefusal,'^sensitivity_differs_at_primary_bound$'):
            self.h.call(.03,consumers=consumers)
        original_contrasts = self.h.contrasts
        def contrasts(**kwargs):
            rows = original_contrasts(**kwargs)
            value = rows[0]['deterministic_bounds']['total']
            rows[0]['deterministic_bounds']['total'] = math.nextafter(value,math.inf)
            return rows
        consumers = sensitivity_module.SensitivityConsumers(self.h.project,self.h.extract,contrasts)
        with self.assertRaisesRegex(AnalysisRefusal,'^sensitivity_differs_at_primary_bound$'):
            self.h.call(.03,consumers=consumers)

    def test_same_gross_allowance_is_required(self):
        original = self.h.extract
        def extract(*args,**kwargs):
            result = original(*args,**kwargs)
            for cell in result['cells']:
                cell['whole_window_drift_allowance']['allowance_j'] = .101
            return result
        consumers = sensitivity_module.SensitivityConsumers(self.h.project,extract,self.h.contrasts)
        with self.assertRaisesRegex(AnalysisRefusal,'^sensitivity_changed_bound_independent_value$'):
            self.h.call(.05,consumers=consumers)

    def test_numeric_equality_distinguishes_signed_zero(self):
        self.assertFalse(sensitivity_module._same(0.,-0.))
