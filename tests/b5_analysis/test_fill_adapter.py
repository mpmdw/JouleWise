"""S8 copy-only adapter checks and code-only CLI refusals."""
from copy import deepcopy
from dataclasses import replace
import contextlib
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock
from joulewise import results_fill_adapter as a
from joulewise.analysis_engine.artifact import finalize_claim_verdicts, render_claim_verdicts, validate_claim_verdicts
from scripts import build_results_fill_input as cli
from tests.b5_analysis import fixtures_s8 as f
from tests.b5_analysis.fixtures_s5 import arithmetic_inputs


class FillAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.f=f.fill_fixture()

    def adapt(self,raw=None,**overrides):
        kw={'campaigns':{'alpha':{},'beta':{}},'finalized_manifest_raw':self.f.manifest_raw,
            'floor_artifact_raw':self.f.floor_raw,'exclusions_sha256':self.f.exclusions_sha256,
            'kept_quads':self.f.kept,'expected_contrast_ids':('decode','prefill')}
        kw.update(overrides)
        return a.adapt_claim_verdicts(self.f.raw if raw is None else raw,**kw)

    def test_T19_copies_every_number_and_plan_order(self):
        value=self.adapt();again=self.adapt()
        self.assertEqual(a.render_results_fill_input(value),a.render_results_fill_input(again))
        for dst,src in zip(value['gamma']['contrasts'],self.f.artifact['contrasts']):
            self.assertEqual(dst['n'],9);self.assertEqual(len(dst['kept_block_ids']),9);self.assertEqual(len(dst['removed_block_ids']),1)
            self.assertIsNone(dst['j_per_token'])
            for dest,key in [('estimate','estimate'),('interval','metrology_aware_CI95'),('df','df'),('t_critical_95','t_critical_95')]:self.assertEqual(dst[dest],src['estimator'][key])
            self.assertEqual(dst['decision_interval'],src['deterministic_bounds']['decision_interval'])
            for key in ('plan_id','claim_role','hypothesized_direction','equivalence','sampling','loo'):self.assertEqual(dst[key],src[key])
            blocks=src['bundle_blocks']['blocks'];yes={b['block_id'] for b in blocks if b['included']}
            self.assertEqual(dst['kept_block_ids'],[bid for bid in src['bundle_blocks']['planned_block_ids'] if bid in yes])
            self.assertEqual(dst['removed_block_ids'],[bid for bid in src['bundle_blocks']['planned_block_ids'] if bid not in yes])
        self.assertEqual(value['gamma']['finalized_manifest'],self.f.artifact['inputs']['analysis_manifest'])
        self.assertEqual(value['gamma']['exclusions_sha256'],self.f.exclusions_sha256)

    def test_R15_kept_identity_not_only_count(self):
        all_ten=arithmetic_inputs([2+.01*i for i in range(10)],removed=()).kept_units
        for changed in ('all_ten','nine_different'):
            kept=deepcopy(self.f.kept)
            if changed=='all_ten':kept={cid:all_ten.for_contrast(cid) for cid in kept}
            else:
                cell=kept['decode'];units=cell.kept['quad']
                kept['decode']=replace(cell,kept={'quad':(replace(units[0],unit_id='counterfactual-other-quad'),*units[1:])})
            with self.subTest(changed=changed),self.assertRaisesRegex(a.ResultsFillAdapterError,'^results_fill_kept_quads_mismatch'):self.adapt(kept_quads=kept)

    def test_R16_manifest_byte_change(self):
        with self.assertRaisesRegex(a.ResultsFillAdapterError,'^results_fill_manifest_mismatch'):
            self.adapt(finalized_manifest_raw=self.f.manifest_raw+b' ')

    def test_R17_missing_third_and_duplicate_contrast(self):
        for changed in ('decode_only','third','duplicate'):
            value=deepcopy(self.f.artifact)
            if changed=='decode_only':value['contrasts']=value['contrasts'][:1]
            else:
                row=deepcopy(value['contrasts'][0])
                if changed=='third':row['contrast_id']='counterfactual-third'
                value['contrasts'].append(row)
            with self.subTest(changed=changed),self.assertRaisesRegex(a.ResultsFillAdapterError,'^results_fill_contrast_census_mismatch'):
                self.adapt(render_claim_verdicts(value))

    def test_R18_floor_and_exclusions_parents(self):
        # Whitespace preserves a valid floor object but differs from embedded bytes.
        for kw,code in [({'floor_artifact_raw':self.f.floor_raw+b' '},'floor'),({'exclusions_sha256':'0'*64},'exclusions'),({'finalized_manifest_raw':None},'exclusions')]:
            with self.subTest(kw=kw),self.assertRaisesRegex(a.ResultsFillAdapterError,'^results_fill_'+code+'_mismatch'):self.adapt(**kw)

    def test_T20_consistent_forgery_is_accepted_by_copy_adapter(self):
        value=deepcopy(self.f.artifact)
        for row in value['contrasts']:
            row['estimator']['estimate']+=15
            for interval in (row['estimator']['repeat_point_CI95'],row['estimator']['metrology_aware_CI95'],row['deterministic_bounds']['decision_interval']):
                interval['lower']+=15;interval['upper']+=15
            for loo in row['loo']['rows']:
                loo['estimate']+=15
                for interval in (loo['metrology_aware_ci95'],loo['decision_interval']):interval['lower']+=15;interval['upper']+=15
        value=finalize_claim_verdicts(value)
        self.assertEqual(validate_claim_verdicts(value,frozen_manifest=self.f.manifest),[])
        output=self.adapt(render_claim_verdicts(value))
        self.assertEqual(output['gamma']['contrasts'][0]['estimate'],value['contrasts'][0]['estimator']['estimate'])
        # Defence against this internally coherent forgery is custody replay (R11).

    def invoke(self,args):
        out,err=io.StringIO(),io.StringIO()
        with contextlib.redirect_stdout(out),contextlib.redirect_stderr(err):code=cli.main(args)
        return code,out.getvalue(),err.getvalue()

    def args(self,out,verdict=None):
        return ['--window-index','synthetic-index','--custody-root',str(self.f.root),'--finalized-manifest',str(self.f.root/'manifest.json'),'--claim-verdicts',str(verdict or self.f.root/'verdicts.json'),'--out',str(out)]

    def test_R19_existing_output_outside_and_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'out';out.write_bytes(b'preserve')
            self.assertEqual(self.invoke(self.args(out)),(2,'','error: results_fill_output_exists\n'));self.assertEqual(out.read_bytes(),b'preserve')
            out.unlink();other=Path(tmp)/'verdicts.json';other.write_bytes(self.f.raw)
            self.assertEqual(self.invoke(self.args(out,other)),(2,'','error: results_fill_path_refused\n'));self.assertFalse(out.exists())
            link=self.f.root/'symlink-verdicts.json';link.symlink_to(self.f.root/'verdicts.json')
            try:self.assertEqual(self.invoke(self.args(out,link)),(2,'','error: results_fill_path_refused\n'))
            finally:link.unlink()
            for code in ('results_fill_manifest_mismatch','results_fill_floor_mismatch','results_fill_exclusions_mismatch','results_fill_kept_quads_mismatch','results_fill_contrast_census_mismatch'):
                with mock.patch.object(cli,'build',side_effect=a.ResultsFillAdapterError(code+': 7331')):
                    self.assertEqual(self.invoke(self.args(out)),(2,'','error: '+code+'\n'))
                self.assertFalse(out.exists())
            with mock.patch.object(cli,'build',side_effect=RuntimeError('7331')):
                self.assertEqual(self.invoke(self.args(out)),(2,'','error: results_fill_input_invalid\n'))

    def test_cli_all_five_checks_are_on_and_silent(self):
        windows={pack:SimpleNamespace(pack_id='synthetic-'+pack,claim_runs_root=self.f.root/'runs',plan_id='synthetic-'+pack,
            attempt=1,harvest_record_sha256='3'*64,record=SimpleNamespace(claim_usable=True)) for pack in ('alpha','beta','gamma')}
        units=self.f.loaded.kept_units
        with tempfile.TemporaryDirectory() as tmp, \
             mock.patch.object(cli,'load_window_index',return_value=SimpleNamespace(entries=())), \
             mock.patch.object(cli,'select_analysed_attempts',return_value=windows), \
             mock.patch.object(cli,'_registered_contrast_ids',return_value=('decode','prefill')), \
             mock.patch.object(cli,'block5_claim_gate_inputs',return_value={'kept_units':units}), \
             mock.patch('joulewise.b5_analysis.archive.open_archive',return_value=SimpleNamespace(output_bytes=lambda path:b'{}\n')):
            out=Path(tmp)/'out'
            self.assertEqual(self.invoke(self.args(out)),(0,'',''))
            result=json.loads(out.read_bytes())
            self.assertEqual(result['gamma']['contrasts'][0]['n'],9)
            self.assertEqual(set(result['campaigns']['alpha']),{'plan_id','attempt','claim_usable','exclusions_sha256','harvest_record_sha256'})

    def test_cli_failed_write_removes_its_partial_file(self):
        value=self.adapt()
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
            with mock.patch.object(cli,'build',return_value=value),mock.patch.object(Path,'open',open_file):
                self.assertEqual(self.invoke(self.args(target)),(2,'','error: results_fill_input_invalid\n'))
            self.assertFalse(target.exists())
