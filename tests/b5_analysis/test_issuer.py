"""Issuer synthetic member, composition and CLI controls."""
import contextlib
from copy import deepcopy
from dataclasses import replace
import hashlib
import io
import json
import math
import statistics
from pathlib import Path
import tempfile
import shutil
from types import SimpleNamespace
import unittest
from unittest import mock
from joulewise import paper_reported_energy as e, paper_reported_energy_issuer as issuer, whole_window as ww
from joulewise.b5_analysis.windows import AnalysisRefusal, SealPins
from scripts import issue_reported_energy as cli
from tests.b5_analysis import fixtures_s8 as f


class IssuerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.f=f.synthetic_pack()

    def test_S8F2_each_cell_uses_its_own_phase(self):
        from tests.test_whole_window import TwoScopeRefusalTests
        summaries = deepcopy(self.f.summaries)
        for cell in self.f.spec['reported_energy_cells']:
            for member in cell['members']:
                summary = summaries[member['bundle_id']]
                ordinal = member['ordinal']
                summary['gross_energy_j'] = 70 + ordinal/10
                summary['energy_anchor_shift_envelopes']['/gross_energy_j'] = (
                    TwoScopeRefusalTests._envelope(70+ordinal/10, .04, .8+ordinal/300))
                for phase, value, half in [('decode', 10+ordinal/100, .2+ordinal/1000),
                                           ('prefill', 31+(ordinal*7 % 13)/10, .5+ordinal/500)]:
                    summary['phase_energy_j'][phase] = value
                    summary['energy_anchor_shift_envelopes']['/phase_energy_j/'+phase] = (
                        TwoScopeRefusalTests._envelope(value, .04, half))
        session = SimpleNamespace(**{**vars(self.f.session), 'summary_for': summaries.get})
        fixture = SimpleNamespace(**{**vars(self.f), 'summaries': summaries, 'session': session})
        with f.pack_seams(fixture):
            projection = f.project(fixture)
        means = []
        for index, phase in [(0, 'decode'), (2, 'prefill')]:
            cell = self.f.spec['reported_energy_cells'][index]
            value = next(c for c in projection['cells'] if c['cell_id'] == cell['cell_id'])
            kept = self.f.kept.for_reported_cell(self.f.spec, index)
            def energy(ordinal):
                return summaries[cell['members'][ordinal-1]['bundle_id']]['phase_energy_j'][phase]
            r = [energy(n) for n in kept.kept_repeat_ordinals]
            b = [statistics.fmean(energy(n) for n in q) for q in kept.kept_quad_ordinals]
            mean = .2*statistics.fmean(r) + .8*statistics.fmean(b)
            variance = .2**2*statistics.variance(r)/len(r) + .8**2*statistics.variance(b)/len(b)
            self.assertAlmostEqual(value['mean_j'], mean, delta=1e-12)
            self.assertAlmostEqual(value['interval']['h_j'],
                                   e.T975[min(len(r), len(b))-1]*math.sqrt(variance), delta=1e-12)
            means.append(value['mean_j'])
        self.assertGreater(abs(means[0]-means[1]), 1e-6)

    def test_S8F3_observed_output_differs_from_requested(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)/'pack'
            shutil.copytree(self.f.root, root)
            for member in self.f.spec['reported_energy_cells'][0]['members']:
                path = root/member['bundle_id']/'metadata.json'
                metadata = json.loads(path.read_bytes())
                self.assertEqual(metadata['workload_provenance']['output_policy']['requested_tokens'], 512)
                metadata['workload_observed'] = {'token_count': 2548, 'output_token_count': 500}
                path.write_text(json.dumps(metadata))
            fixture = SimpleNamespace(**{**vars(self.f), 'root': root})
            with f.pack_seams(fixture):
                value = f.project(fixture)['cells'][0]
        kept = self.f.kept.for_reported_cell(self.f.spec, 0)
        count = len(kept.kept_repeat_ordinals) + 4*len(kept.kept_quad_ordinals)
        self.assertEqual(value['per_token']['observed_token_sum'], count*500)
        self.assertEqual(value['per_token']['status'], 'computed')

    def ownership_counterfactual(self, change):
        original = self.f.kept.for_reported_cell(self.f.spec, 0).cell
        if change == 'repeat_positions':
            transform = lambda u: replace(u, positions=(11-u.positions[0],)) if u.stratum == 'repeat' else u
        elif change == 'repeat_count':
            repeat = original.kept['repeat'][0]
            transform = lambda u: replace(u, run_ids=()) if u.stratum == 'repeat' and u.unit_id == repeat.unit_id else u
        elif change == 'quad_positions':
            kept_quad = original.kept['quad'][0]
            removed_quad = next(u for u in original.dropped if u.stratum == 'quad')
            def transform(u):
                if u.unit_id == kept_quad.unit_id and u.stratum == 'quad':
                    return replace(u, positions=removed_quad.positions)
                if u.unit_id == removed_quad.unit_id and u.stratum == 'quad':
                    return replace(u, positions=kept_quad.positions)
                return u
        else:
            quad = original.kept['quad'][0]
            def transform(u):
                if u.stratum != 'quad' or u.unit_id != quad.unit_id:
                    return u
                ids = (u.run_ids[1], u.run_ids[0], *u.run_ids[2:])
                return replace(u, run_ids=ids if change == 'quad_order' else ids[:3])
        cell = replace(original, kept={s: tuple(transform(u) for u in us) for s, us in original.kept.items()},
                       dropped=tuple(transform(u) for u in original.dropped))
        units = replace(self.f.kept, cells={**self.f.kept.cells, cell.cell_id: cell})
        summary = mock.Mock(side_effect=self.f.session.summary_for)
        provenance = mock.Mock(side_effect=self.f.session.provenance_for)
        session = SimpleNamespace(**{**vars(self.f.session), 'summary_for': summary, 'provenance_for': provenance})
        fixture = SimpleNamespace(**{**vars(self.f), 'kept': units, 'session': session})
        with f.pack_seams(fixture), mock.patch.object(issuer, 'BundleReader', wraps=issuer.BundleReader) as reader:
            with self.assertRaises(AnalysisRefusal) as cm:
                f.project(fixture)
            self.assertEqual(cm.exception.code, 'exclusions_plan_mismatch')
            summary.assert_not_called()
            provenance.assert_not_called()
            reader.assert_not_called()

    def test_S8F4_repeat_positions_refuse_before_member_io(self):
        self.ownership_counterfactual('repeat_positions')

    def test_S8F4_quad_positions_refuse_before_member_io(self):
        self.ownership_counterfactual('quad_positions')

    def test_S8F4_quad_run_order_refuses_before_member_io(self):
        self.ownership_counterfactual('quad_order')

    def test_S8F4_quad_run_count_refuses_before_member_io(self):
        self.ownership_counterfactual('quad_count')

    def test_S8F4_repeat_run_count_refuses_before_member_io(self):
        self.ownership_counterfactual('repeat_count')

    def test_S8F4_kept_ordinal_owned_by_a_dropped_unit_refuses_before_member_io(self):
        # A hand-built kept object: the ordinals keep the removed repeat's slot and
        # remove a kept repeat's, while the units themselves are unchanged.
        cell = self.f.spec['reported_energy_cells'][0]
        kept = self.f.kept.for_reported_cell(self.f.spec, 0)
        gone = kept.removed_repeat_ordinals[0]
        swap = next(n for n in kept.kept_repeat_ordinals if n != gone)
        forged = replace(kept,
            kept_repeat_ordinals=tuple(sorted({*kept.kept_repeat_ordinals, gone} - {swap})),
            removed_repeat_ordinals=tuple(sorted({*kept.removed_repeat_ordinals, swap} - {gone})))
        summary = mock.Mock(side_effect=self.f.session.summary_for)
        session = SimpleNamespace(**{**vars(self.f.session), 'summary_for': summary})
        binding = {'selection_sha256': 'a'*64, 'prompt_pin_sha256': 'b'*64, 'whole_window_basis_sha256': 'c'*64}
        with self.assertRaises(AnalysisRefusal) as cm:
            issuer.normalized_rows(cell, forged, session=session, runs_root=self.f.root, context=self.f.context,
                binding=binding, kept_units=self.f.kept, strict_validator=lambda path, strict: (),
                allowances={'gross_energy': {'allowance_j': .1}})
        self.assertEqual(cm.exception.code, 'exclusions_plan_mismatch')
        summary.assert_not_called()

    def test_S8F4_session_contains_exactly_kept_run_ids(self):
        expected = {run for i in range(3)
                    for units in self.f.kept.for_reported_cell(self.f.spec, i).cell.kept.values()
                    for unit in units for run in unit.run_ids}
        removed = self.f.kept.removed_run_ids()
        self.assertTrue(removed)
        with f.pack_seams(self.f), mock.patch.object(issuer, 'AuthenticatedConsumptionSession',
                                                   return_value=self.f.session) as constructor:
            f.project(self.f)
        constructor.assert_called_once()
        ids = constructor.call_args.args[1]
        self.assertEqual(ids, expected)
        self.assertTrue(set(ids).isdisjoint(removed))

    def rows(self,session=None,strict=None):
        c=self.f.spec['reported_energy_cells'][0];k=self.f.kept.for_reported_cell(self.f.spec,0)
        binding={'selection_sha256':'a'*64,'prompt_pin_sha256':'b'*64,'whole_window_basis_sha256':'c'*64}
        return issuer.normalized_rows(c,k,session=session or self.f.session,runs_root=self.f.root,context=self.f.context,
            binding=binding,kept_units=self.f.kept,strict_validator=strict or (lambda path,strict:()),
            allowances={'gross_energy':{'allowance_j':.1}})

    def test_T10_real_production_dispatch_operative_summary(self):
        p=f.production_member()
        self.assertTrue(p.session.ready,p.session.refusal_reasons)
        self.assertNotEqual(p.pre,p.operative)
        with mock.patch.object(issuer.inputs,'campaign_cooldown_evidence',return_value={p.bundle.name:{'verified':True,'result':'recovered'}}):
            rows=issuer.normalized_rows(p.cell,p.kept,session=p.session,runs_root=p.bundle.parent,context=p.context,
                binding=p.binding,kept_units=self.f.kept,strict_validator=lambda path,strict:(),
                allowances={'gross_energy':{'allowance_j':.1}})
        bound=rows[0]['bounds_j'][e.BOUND_KINDS[0]]
        self.assertEqual(bound,p.independent['energy_anchor_shift_envelopes']['/phase_energy_j/decode']['max_abs_delta_j'])
        self.assertNotEqual(bound,p.stored['energy_anchor_shift_envelopes']['/phase_energy_j/decode']['max_abs_delta_j'])
        self.assertEqual(rows[0]['energy_j'],p.independent['phase_energy_j']['decode'])

    def test_T11_exclusions_digest_and_unit_records(self):
        with f.pack_seams(self.f):v=f.project(self.f)
        self.assertEqual(v['exclusions_sha256'],hashlib.sha256((self.f.root/'exclusions.json').read_bytes()).hexdigest())
        for c in v['cells']:
            idx=next(i for i,x in enumerate(self.f.spec['reported_energy_cells']) if x['cell_id']==c['cell_id'])
            kept=self.f.kept.for_reported_cell(self.f.spec,idx)
            document=json.loads((self.f.root/'exclusions.json').read_bytes())['cells'][kept.cell.cell_id]
            def record(uid):
                stratum,number=uid.split('-');number=int(number)
                return {'stratum':stratum,'unit_id':uid,'ordinals':[number] if stratum=='repeat' else list(range(11+4*(number-1),15+4*(number-1)))}
            expected=[record(uid) for stratum in ('repeat','quad') for uid in document['kept_units'][stratum]]
            self.assertEqual(c['kept_units'],expected)
            self.assertEqual(c['removed_units'],[record(uid) for uid in document['removed_units']])

    def invoke(self,value=None,error=None,out=None,args=None):
        stderr,stdout=io.StringIO(),io.StringIO()
        with mock.patch.object(cli,'issue_pack',return_value=value,side_effect=error),contextlib.redirect_stdout(stdout),contextlib.redirect_stderr(stderr):
            code=cli.main(args or ['--window-index','synthetic.json','--pack','alpha','--output',str(out)])
        return code,stdout.getvalue(),stderr.getvalue()

    def test_T12_independent_p42_refusal_and_script_structure(self):
        with f.pack_seams(self.f):v=f.project(self.f)
        self.assertEqual(len(v['cells']),2)
        self.assertEqual([(x['cell_id'],x['code']) for x in v['refused_cells']],[(self.f.spec['reported_energy_cells'][1]['cell_id'],'paper_reported_energy_record_invalid')])
        with tempfile.TemporaryDirectory() as tmp:
            code,stdout,stderr=self.invoke(v,out=Path(tmp)/'out.json')
        self.assertEqual((code,stderr),(0,''));self.assertEqual(len(stdout.splitlines()),1)
        def nofloat(x):
            if isinstance(x,dict):return all(nofloat(v) for v in x.values())
            if isinstance(x,list):return all(nofloat(v) for v in x)
            return not isinstance(x,float)
        self.assertTrue(nofloat(json.loads(stdout)))
        self.assertTrue(all(row['per_token_status']=='computed' and row['per_token_reason'] is None
                            for row in json.loads(stdout)['cells']))
        original=issuer._tokens
        def zero_tokens(*args):
            return {**original(*args),'output':0,'total':0,'prompt_realized':0,'tokenize_end':0,'prefill_start':0}
        with f.pack_seams(self.f),mock.patch.object(issuer,'_tokens',side_effect=zero_tokens):
            refused=f.project(self.f)
        with tempfile.TemporaryDirectory() as tmp:
            code,stdout,stderr=self.invoke(refused,out=Path(tmp)/'out.json')
        self.assertEqual((code,stderr),(0,''));self.assertTrue(nofloat(json.loads(stdout)))
        self.assertTrue(all(row['per_token_status']=='refused' and row['per_token_reason']==
                            'paper_reported_energy_denominator_invalid'
                            for row in json.loads(stdout)['cells']))

    def test_F1_unbound_triangle_does_not_remove_kept_member(self):
        with f.pack_seams(self.f),mock.patch.object(issuer,'custody_telemetry_identity',
                return_value=SimpleNamespace(custody_bound_config=False,triangle_agrees=False)):
            rows=self.rows()
        self.assertTrue(all(row['strict_valid'] for row in rows))

    def test_F2_kernel_orders_invalid_record_before_missing_kind(self):
        original=issuer.inputs.deterministic_bounds
        def missing_first(*args):
            bounds,reasons=original(*args)
            return {k:v for k,v in bounds.items() if k!=e.BOUND_KINDS[0]},reasons
        with f.pack_seams(self.f),mock.patch.object(issuer.inputs,'deterministic_bounds',side_effect=missing_first):
            value=f.project(self.f)
        refused={r['cell_id']:r for r in value['refused_cells']}
        self.assertEqual(refused[self.f.spec['reported_energy_cells'][1]['cell_id']]['code'],
                         'paper_reported_energy_record_invalid')
        for i in (0,2):
            self.assertEqual(refused[self.f.spec['reported_energy_cells'][i]['cell_id']]['code'],
                             'paper_reported_energy_schema_invalid')

    def test_F3_allowances_are_explicit_and_reach_member_evidence(self):
        original=issuer.normalized_rows
        with f.pack_seams(self.f),mock.patch.object(issuer,'normalized_rows',wraps=original) as rows:
            value=f.project(self.f)
        self.assertEqual(len(value['cells']),2)
        self.assertFalse(hasattr(self.f.session,'_reported_energy_allowances'))
        for call in rows.call_args_list:
            self.assertEqual(call.kwargs['allowances'],{'gross_energy':{'allowance_j':.1}})
        self.assertTrue(all(cell['interval']['kind_averages_j'][e.BOUND_KINDS[2]]==.2*.05+.8*.05
                            for cell in value['cells']))

    def test_F5_target_comes_from_kept_units_and_script_uses_boolean(self):
        with f.pack_seams(self.f):value=f.project(self.f)
        self.assertIs(value['refused_cells'][0]['target'],False)
        # The script must never infer target status from a cell-id substring.
        non_target=deepcopy(value);non_target['refused_cells'][0]['cell_id']='synthetic-no-p42-substring'
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'out.json'
            self.assertEqual(self.invoke(non_target,out=output)[0],0);self.assertTrue(output.exists())
            output.unlink()
            target=deepcopy(non_target);target['refused_cells'][0]['target']=True
            self.assertEqual(self.invoke(target,out=output),
                (2,'','error: paper_reported_energy_record_invalid\n'));self.assertFalse(output.exists())
        # Conversely a cell whose id contains p42 can be a target in the kept census.
        units=self.f.kept.for_reported_cell(self.f.spec,1).cell
        kept=replace(self.f.kept,cells={**self.f.kept.cells,units.cell_id:replace(units,target=True)})
        with f.pack_seams(self.f),mock.patch.object(issuer,'normalized_rows',
                side_effect=e.PaperReportedEnergyRefusal('paper_reported_energy_record_invalid')):
            refused=issuer.project_pack(self.f.spec,kept,context=self.f.context,runs_root=self.f.root,
                evaluation_basis_sha256='c'*64,selection_sha256='a'*64,prompt_pin_sha256='b'*64,
                strict_validator=lambda *a:())
        self.assertTrue(all(row['target'] for row in refused['refused_cells']))
        with mock.patch.object(type(self.f.kept),'for_reported_cell',side_effect=AnalysisRefusal('exclusions_cell_unknown')):
            unknown=issuer.project_pack(self.f.spec,self.f.kept,context=None,runs_root=self.f.root,
                evaluation_basis_sha256='c'*64,selection_sha256='a'*64,prompt_pin_sha256='b'*64,
                strict_validator=lambda *a:())
        self.assertTrue(all(row['target'] is True for row in unknown['refused_cells']))

    def test_F6_session_reasons_and_unready_stop_before_member_io(self):
        for reasons,ready,expected in [(('z_reason','a_reason'),False,'a_reason'),
                                       ((),False,'whole_window_verdict_provenance_invalid')]:
            session=deepcopy(self.f.session);session.refusal_reasons=reasons;session.ready=ready
            with self.subTest(reasons=reasons),f.pack_seams(self.f), \
                 mock.patch.object(issuer,'AuthenticatedConsumptionSession',return_value=session), \
                 mock.patch.object(issuer,'BundleReader') as reader, \
                 self.assertRaises(AnalysisRefusal) as cm:
                f.project(self.f)
            self.assertEqual(cm.exception.code,expected);reader.assert_not_called()

    def test_T13_deterministic_output_no_fixture_path(self):
        with f.pack_seams(self.f):v=f.project(self.f)
        with tempfile.TemporaryDirectory() as tmp:
            a,b=Path(tmp)/'a',Path(tmp)/'b'
            self.assertEqual(self.invoke(v,out=a)[0],0);self.assertEqual(self.invoke(v,out=b)[0],0)
            self.assertEqual(a.read_bytes(),b.read_bytes());self.assertNotIn(str(self.f.root).encode(),a.read_bytes())

    def test_R6_missing_or_wrong_operative_provenance(self):
        for provenance in ({},{'operative_fiducial_bound_s':.026},{'operative_fiducial_bound_s':.06},{'operative_fiducial_bound_s':True}):
            session=deepcopy(self.f.session);session.provenance_for=lambda bid:provenance
            with self.subTest(provenance=provenance),f.pack_seams(self.f),self.assertRaisesRegex(AnalysisRefusal,'^operative_bound_not_the_window_bracket$'):
                self.rows(session)

    def test_R7_realized_wrong_model_reaches_kernel(self):
        with f.pack_seams(self.f),mock.patch.object(issuer.inputs,'realized_scientific_identity',return_value={'model':{'name':'Qwen3-8B-4bit'}}):
            v=f.project(self.f)
        self.assertEqual(v['refused_cells'][0]['code'],'paper_reported_energy_record_identity_mismatch')

    def test_R8_absent_context_and_allowance_never_zero(self):
        with mock.patch.object(issuer,'AuthenticatedConsumptionSession') as session,mock.patch.object(issuer,'BundleReader') as reader:
            v=issuer.project_pack(self.f.spec,self.f.kept,context=None,runs_root=self.f.root,
                evaluation_basis_sha256='c'*64,selection_sha256='a'*64,prompt_pin_sha256='b'*64,strict_validator=lambda *a:())
            session.assert_not_called();reader.assert_not_called()
        self.assertEqual(len(v['refused_cells']),3)
        self.assertTrue(all(c['code']=='paper_reported_energy_whole_window_allowance_unrecorded' and c['plan_code']=='whole_window_drift_allowance_unrecorded' for c in v['refused_cells']))
        with f.pack_seams(self.f),mock.patch.object(issuer,'whole_window_drift_allowances',return_value=ww.WholeWindowDriftAllowanceResult('allowances',{})):
            v=f.project(self.f)
        self.assertEqual(v['refused_cells'][0]['code'],'paper_reported_energy_whole_window_allowance_unrecorded')

    def test_R9_strict_kept_member_stop_and_removed_absent(self):
        with f.pack_seams(self.f),self.assertRaisesRegex(AnalysisRefusal,'^member_code_on_kept_unit$'):
            self.rows(strict=lambda path,strict:['counterfactual strict invalid'])
        with f.pack_seams(self.f), mock.patch.object(issuer,'custody_telemetry_identity',
                return_value=SimpleNamespace(custody_bound_config=True,triangle_agrees=False)), \
                self.assertRaisesRegex(AnalysisRefusal,'^member_code_on_kept_unit$'):
            self.rows()
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'out'
            self.assertEqual(self.invoke(error=AnalysisRefusal('member_code_on_kept_unit'),out=out),(2,'','error: member_code_on_kept_unit\n'));self.assertFalse(out.exists())
        with f.pack_seams(self.f):
            before=f.project(self.f)
            real=issuer.BundleReader
            removed=self.f.kept.removed_run_ids()
            def read(path):
                self.assertNotIn(Path(path).name,removed)
                return real(path)
            with tempfile.TemporaryDirectory() as temporary:
                backup=Path(temporary)
                for bid in removed:
                    shutil.copytree(self.f.root/bid,backup/bid)
                    shutil.rmtree(self.f.root/bid)
                try:
                    with mock.patch.object(issuer,'BundleReader',side_effect=read):after=f.project(self.f)
                finally:
                    for bid in removed:shutil.copytree(backup/bid,self.f.root/bid)
        self.assertEqual(before,after)

    def test_R10_cli_existing_gamma_and_error_redaction(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'out';out.write_bytes(b'preserve')
            self.assertEqual(self.invoke(out=out),(2,'','error: reported_energy_output_exists\n'));self.assertEqual(out.read_bytes(),b'preserve')
            out.unlink();r=self.invoke(error=RuntimeError('7331'),out=out)
            self.assertEqual(r,(2,'','error: reported_energy_input_invalid\n'));self.assertFalse(out.exists())
            with contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit) as cm:
                cli.main(['--window-index','x','--pack','gamma','--output',str(out)])
            self.assertEqual(cm.exception.code,2)
        source=Path(cli.__file__).read_text()
        for flag in ('--runs-root','--spec','--bound','--digest'):self.assertNotIn(flag,source)

    def test_cli_failed_write_removes_its_partial_file(self):
        with f.pack_seams(self.f):value=f.project(self.f)
        with tempfile.TemporaryDirectory() as temporary:
            target=Path(temporary)/'output';original=Path.open
            class BrokenWriter:
                def __enter__(self):
                    self.handle=original(target,'xb')
                    return self
                def write(self,raw):
                    self.handle.write(raw[:1])
                    raise RuntimeError('7331')
                def __exit__(self,*args):self.handle.close()
            def open_file(path,*args,**kwargs):
                return BrokenWriter() if path==target else original(path,*args,**kwargs)
            with mock.patch.object(Path,'open',open_file):
                self.assertEqual(self.invoke(value,out=target),(2,'','error: reported_energy_input_invalid\n'))
            self.assertFalse(target.exists())

    def test_b_override_before_bundle_io(self):
        with mock.patch.object(issuer,'BundleReader') as read,self.assertRaisesRegex(AnalysisRefusal,'b_override_s_unsupported'):
            self.rows_with_override()
        read.assert_not_called()

    def rows_with_override(self):
        return issuer.normalized_rows(None,None,session=None,runs_root=None,context=None,binding=None,kept_units=None,strict_validator=None,allowances={},b_override_s=.05)


class IndexedCompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from tests.b5_analysis.test_floor_kept_units import indexed_fixture
        from tests.b5_analysis import fixtures_s2 as s2
        cls.indexed=indexed_fixture()
        cls.reported=f.indexed_reported_fixture()
        # The S4 archived spec has two families, rather than a registered S8
        # six-cell spec. Projection/spec registration are isolated below; every
        # index, archive, kept-units, bracket and context reader is real.
        pack=cls.indexed.local_spec.parent/'prefill_pin';pack.mkdir(exist_ok=True)
        for name in ('selection.json','prefill_prompt_pin.json'):(pack/name).write_bytes(b'{}\n')

    def test_S8F6_local_spec_must_equal_archive(self):
        p = self.reported
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)/'repo'
            shutil.copytree(p.repo, repo)
            path = repo/'configs/campaigns'/p.window.entry.pack_id/'extraction_spec.json'
            path.write_bytes(path.read_bytes()+b' ')
            changed = SimpleNamespace(**{**vars(p), 'repo': repo})
            with f.indexed_reported_seams(changed), self.assertRaises(AnalysisRefusal) as cm:
                f.issue_indexed_reported(changed)
        self.assertEqual(cm.exception.code, 'extraction_spec_differs_from_archive')

    def test_S8F6_local_prefill_parents_must_equal_archive(self):
        p = self.reported
        for name in ('selection.json', 'prefill_prompt_pin.json'):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                repo = Path(tmp)/'repo'
                shutil.copytree(p.repo, repo)
                path = repo/'configs/campaigns'/p.window.entry.pack_id/'prefill_pin'/name
                path.write_bytes(path.read_bytes()+b' ')
                changed = SimpleNamespace(**{**vars(p), 'repo': repo})
                with f.indexed_reported_seams(changed), self.assertRaises(AnalysisRefusal) as cm:
                    f.issue_indexed_reported(changed)
                self.assertEqual(cm.exception.code, 'reported_energy_parent_differs_from_archive')

    def test_S8F6_verdict_digests_refuse_before_context(self):
        from joulewise.b5_analysis.archive import ArchiveHandle
        original = ArchiveHandle.output_bytes
        for field in ('row_sha256', 'evaluation_basis_sha256'):
            def output(handle, path):
                raw = original(handle, path)
                if path == issuer.NEG8_HARVEST_ALLOWANCE_RECORD:
                    allowance = json.loads(raw)
                    allowance['verdict'][field] = '0'*64
                    return (json.dumps(allowance)+'\n').encode()
                return raw
            with self.subTest(field=field), f.indexed_reported_seams(self.reported), \
                 mock.patch.object(ArchiveHandle, 'output_bytes', output), \
                 mock.patch.object(issuer, 'build_context', wraps=issuer.build_context) as context:
                with self.assertRaises(AnalysisRefusal) as cm:
                    f.issue_indexed_reported(self.reported)
                self.assertEqual(cm.exception.code, 'whole_window_verdict_provenance_invalid')
                context.assert_not_called()

    def test_S8F6_gamma_refuses_before_index_read(self):
        with mock.patch.object(issuer, 'load_window_index') as index, self.assertRaises(AnalysisRefusal) as cm:
            issuer.issue_pack(self.reported.index, 'gamma')
        self.assertEqual(cm.exception.code, 'floor_pack_required')
        index.assert_not_called()

    def compose(self):
        from tests.b5_analysis import fixtures as s0, fixtures_s2 as s2
        # ArchiveContext requires the real ArchiveHandle: patch source method
        # narrowly rather than changing the handle's type.
        from joulewise.b5_analysis.archive import ArchiveHandle
        original=ArchiveHandle.source_bytes
        def source(handle,path):
            if '/prefill_pin/' in path:return b'{}\n'
            return original(handle,path)
        with s2.capture_adapter(),mock.patch.object(ArchiveHandle,'source_bytes',source), \
             mock.patch.object(e,'_validate_registered_spec'),mock.patch.object(issuer,'project_pack',return_value={'synthetic':'projection'}) as projection:
            result=issuer.issue_pack(self.indexed.index,'beta',repo_root=self.indexed.local_repo,
                seal_pins=SealPins.load(),pack_table=s0.PACK_TABLE,test_only_allow_synthetic_binding=True)
        return result,projection

    def test_T11_real_index_archive_and_changed_exclusions(self):
        result,projection=self.compose();self.assertEqual(result,{'synthetic':'projection'})
        args,kw=projection.call_args
        raw=(self.indexed.window.archive/'derived/exclusions.json').read_bytes()
        self.assertEqual(args[1].exclusions_sha256,hashlib.sha256(raw).hexdigest())
        path=self.indexed.window.archive/'derived/exclusions.json'
        try:
            path.write_bytes(raw+b' ')
            with mock.patch.object(issuer,'BundleReader') as reader,self.assertRaises(AnalysisRefusal) as cm:self.compose()
            self.assertEqual(cm.exception.code,'exclusions_record_unauthenticated')
            reader.assert_not_called()
        finally:path.write_bytes(raw)

    def test_F6_real_indexed_session_unready_before_member_io(self):
        from tests.b5_analysis import fixtures_s2 as s2
        p=f.indexed_reported_fixture();sessions=[]
        constructor=issuer.AuthenticatedConsumptionSession
        def session(*args,**kwargs):
            value=constructor(*args,**kwargs);sessions.append(value);return value
        with s2.capture_adapter(),mock.patch.object(e,'_validate_registered_spec'), \
             mock.patch.object(issuer,'AuthenticatedConsumptionSession',side_effect=session), \
             mock.patch.object(issuer,'BundleReader') as reader,self.assertRaises(AnalysisRefusal) as cm:
            f.issue_indexed_reported(p)
        self.assertEqual(cm.exception.code,'whole_window_verdict_provenance_invalid')
        self.assertEqual(sessions[0].refusal_reasons,());self.assertFalse(sessions[0].ready)
        reader.assert_not_called()
