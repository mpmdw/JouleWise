"""S10 driver primitives, dispatch regression and real joined acceptance."""
from contextlib import contextmanager, redirect_stderr, redirect_stdout
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from joulewise.b5_analysis import dry_run as d
from joulewise.b5_analysis.windows import AnalysisRefusal
from joulewise.b5_analysis.steps import step_record

MARKER = '12.3457331'


class JoinedRunTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from tests.b5_analysis.joined_s10 import cached_primary
        # The scratch repository outlives this class: the release tests reuse
        # this run as their first dry run; the harness removes it at exit.
        cls.fixture, cls.harness, cls.result = cached_primary()

    def rows(self, step):
        self.assertIsNotNone(self.result.record, self.result.stderr)
        rows = [row for row in self.result.record['steps'] if row['step'] == step]
        self.assertTrue(rows, 'missing step ' + step)
        return rows

    def assert_ok(self, step):
        for row in self.rows(step):
            self.assertEqual(row['status'], 'ok', row)

    def test_J1_reaches_step5_with_registered_p42_exit(self):
        for step in ('0', '1', '2', '3', '3b', '4', '5'):
            self.assert_ok(step)
        self.assertEqual({row['window'] for row in self.rows('4')}, {'alpha', 'beta'})
        for row in self.rows('4'):
            self.assertEqual((row['exit_status'], row['registered_exit']),
                             (1, 'p42_floor_cells_only'))

    def test_J2_reaches_step9(self):
        for step in ('5', '8', '6', '9'):
            self.assert_ok(step)

    def test_J3_closeout_openers_issuers_and_disclosures_are_ok(self):
        for step in ('6', '9b', '10', '11'):
            self.assert_ok(step)
        self.assertEqual({row['window'] for row in self.rows('10')}, {'alpha', 'beta'})
        self.assertTrue(self.result.disclosure_reads)

    def test_J4_completed_without_tooling_refusal(self):
        self.assertIs(self.result.record['completed_without_tooling_refusal'], True)
        self.assertEqual(self.result.code, 0, self.result.stderr)

    def test_J5_all_public_bytes_are_blind(self):
        from tests.b5_analysis.joined_s10 import assert_public_bytes
        assert_public_bytes(self, self.result, self.fixture.restricted_floats())


class JoinedHarnessInfrastructureTests(unittest.TestCase):
    def test_outer_capture_keeps_descriptor_writes_in_driver_streams(self):
        from tests.b5_analysis.joined_s10 import capture_driver_streams
        import sys
        with capture_driver_streams() as streams:
            print('python-out')
            print('python-err', file=sys.stderr)
            os.write(1, b'descriptor-out\n')
            os.write(2, b'descriptor-err\n')
        self.assertEqual(set(streams['stdout'].splitlines()), {'python-out', 'descriptor-out'})
        self.assertEqual(set(streams['stderr'].splitlines()), {'python-err', 'descriptor-err'})

    def test_outer_capture_restores_descriptors_after_exception(self):
        from tests.b5_analysis.joined_s10 import capture_driver_streams
        before = [os.fstat(fd) for fd in (1, 2)]
        with self.assertRaisesRegex(RuntimeError, 'outer-capture'):
            with capture_driver_streams():
                raise RuntimeError('outer-capture')
        self.assertEqual([os.fstat(fd) for fd in (1, 2)], before)

    def test_public_byte_scan_rejects_alternate_float_notation_and_false_restricted_roots(self):
        from tests.b5_analysis.joined_s10 import assert_public_bytes
        with tempfile.TemporaryDirectory(prefix='s10-public-scan-') as temporary:
            custody = Path(temporary).resolve()
            directory = custody/'dry-run'
            directory.mkdir()
            path = directory/'B5-BLIND-DRY-RUN-RECORD.json'
            path.write_text('{}')
            result = SimpleNamespace(path=path, custody=custody, record={'steps':[]},
                                     stdout='a'*64+'\n', stderr='step 0 - ok\n')
            secret = directory/'restricted/log.txt'
            secret.parent.mkdir()
            secret.write_text(MARKER)
            assert_public_bytes(self, result, {float(MARKER)})
            for value in (MARKER, '.7331', '-.7331', '7331e-4'):
                with self.subTest(value=value), self.assertRaises(AssertionError):
                    result.stdout = value+'\n'
                    assert_public_bytes(self, result, {float(MARKER)})
            result.stdout = 'a'*64+'\n'
            escaped = custody/'notes/restricted/leak.txt'
            escaped.parent.mkdir(parents=True)
            escaped.write_text(MARKER)
            with self.assertRaises(AssertionError):
                assert_public_bytes(self, result, {float(MARKER)})


class DriverPrimitiveTests(unittest.TestCase):
    def test_T18_class_table_is_sorted_disjoint_and_keeps_S7_split(self):
        from scripts import run_d165_closeout_from_custody as closeout
        from joulewise import dominance_closeout as owner
        classes=json.loads((d.ROOT/'configs/analysis/b5/dry_run_refusal_classes.json').read_bytes())
        self.assertEqual(classes['schema_version'],'joulewise.b5_dry_run_refusal_classes.v1')
        tooling,outcome=classes['tooling_refusal'],classes['outcome_class']
        self.assertEqual(tooling,sorted(set(tooling)))
        self.assertEqual(outcome,sorted(set(outcome)))
        self.assertFalse(set(tooling)&set(outcome))
        for code in tooling:
            if ':' in code:self.assertIn(code.split(':',1)[0],tooling)
        self.assertIn('ledger_copies_disagree_below_T',tooling)
        self.assertLessEqual(closeout.TOOLING_REFUSAL_CODES,set(tooling))
        self.assertEqual(closeout.OUTCOME_CLASS_CODES,set(outcome))
        remaining=owner.D165_CLOSEOUT_REFUSAL_CODES-closeout.TOOLING_REFUSAL_CODES-closeout.OUTCOME_CLASS_CODES
        self.assertEqual(len(remaining),10)
        self.assertFalse(remaining&(set(tooling)|set(outcome)))

    def test_T3_runner_captures_python_and_descriptor_streams(self):
        def main(argv):
            print(MARKER); print(MARKER, file=__import__('sys').stderr)
            os.write(1, (MARKER+'\n').encode()); os.write(2, (MARKER+'\n').encode())
            return 0
        with tempfile.TemporaryDirectory() as tmp:
            restricted = Path(tmp)/'restricted'
            stdout, stderr = io.StringIO(), io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                result = d.StepRunner(restricted).run(main, [], step='5')
                print('restored')
            self.assertEqual(result.exit_status, 0)
            self.assertEqual((stdout.getvalue(),stderr.getvalue()),('restored\n',''))
            self.assertEqual(result.stdout_path.read_text(),(MARKER+'\n')*2)
            self.assertEqual(result.stderr_path.read_text(),(MARKER+'\n')*2)
            self.assertTrue(result.stdout_path.is_relative_to(restricted/'logs'))

    def test_T4_exception_is_restricted_and_unclassified(self):
        def main(argv):raise RuntimeError(MARKER)
        with tempfile.TemporaryDirectory() as tmp:
            stdout, stderr = io.StringIO(), io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                result = d.StepRunner(Path(tmp)/'restricted').run(main, [], step='9')
                print('restored', file=__import__('sys').stderr)
            self.assertEqual((stdout.getvalue(),stderr.getvalue()),('','restored\n'))
            self.assertEqual(result.exit_status,2)
            self.assertTrue(result.exception)
            self.assertIsNone(result.token())
            self.assertIn(MARKER,result.stderr_path.read_text())

    def test_T4_refusal_token_strips_detail_and_rejects_unclosed_strings(self):
        self.assertEqual(d.refusal_token('error: earlier\nerror: some_code: '+MARKER+'\n'),'some_code')
        self.assertEqual(d.refusal_token('irrelevant\nsome_code: '+MARKER+'\n'),'some_code')
        self.assertEqual(d.refusal_token('error: ledger_copies_disagree_below_T: '+MARKER+'\n'),'ledger_copies_disagree_below_T')
        for value in ('','error: code-with-dash\n','error: code \n',
                      'error: '+MARKER+'\n','{"code":"some_code"}\n'):
            with self.subTest(value=value):self.assertIsNone(d.refusal_token(value))

    def test_T4_missing_token_nonzero_is_unclassified(self):
        record=step_record('9',exit_status=2,refusal_code=None,classes={}).as_dict()
        self.assertEqual((record['status'],record['refusal']),
                         ('unclassified_refusal','unclassified refusal at step 9'))
        self.assertEqual(step_record('4',exit_status=1,registered_exit='p42_floor_cells_only').status,'ok')

    def test_T5_unlisted_code_is_not_an_outcome(self):
        record=step_record('9',exit_status=2,refusal_code='unlisted_7331',classes={}).as_dict()
        self.assertEqual(record['status'],'unclassified_refusal')
        self.assertEqual(record['refusal'],'unclassified refusal at step 9')
        self.assertNotIn('unlisted_7331',str(record))

    def test_runner_system_exit_and_error_stream_precedence(self):
        def main(argv):
            print('outcome_code')
            print('error: some_code: '+MARKER, file=__import__('sys').stderr)
            raise SystemExit(2)
        with tempfile.TemporaryDirectory() as tmp:
            result=d.StepRunner(Path(tmp)/'restricted').run(main, [], step='4', window='alpha')
            self.assertEqual(result.exit_status,2)
            self.assertFalse(result.exception)
            self.assertEqual(result.token(),'some_code')

    def test_T13_rehash_detects_output_change_and_path_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            restricted=Path(tmp)/'restricted';restricted.mkdir()
            path=restricted/'output.json';path.write_text(MARKER)
            record={'name':'output.json','sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
            d.require_step_inputs(restricted,[record])
            path.write_text(MARKER+' ')
            with self.assertRaisesRegex(AnalysisRefusal,'^step_input_digest_mismatch$'):
                d.require_step_inputs(restricted,[record])
            with self.assertRaisesRegex(AnalysisRefusal,'^step_input_digest_mismatch$'):
                d.require_step_inputs(restricted,[{**record,'name':'../output.json'}])

    def test_T16_backup_environment_restored_even_after_exception(self):
        for existed in (False,True):
            with self.subTest(existed=existed), mock.patch.dict(os.environ,{},clear=True):
                if existed:os.environ['JOULEWISE_BACKUP_ROOTS']='synthetic'
                with self.assertRaisesRegex(RuntimeError,'synthetic'):
                    with d.without_backup_roots() as ignored:
                        self.assertEqual(ignored,existed)
                        self.assertNotIn('JOULEWISE_BACKUP_ROOTS',os.environ)
                        raise RuntimeError('synthetic')
                self.assertEqual(os.environ.get('JOULEWISE_BACKUP_ROOTS'),'synthetic' if existed else None)

    def test_T17_git_function_rejects_tracked_changes(self):
        with mock.patch.object(d.subprocess,'run',side_effect=[
                mock.Mock(stdout='0'*40+'\n'),mock.Mock(stdout=' M tracked.py\n')]), \
             self.assertRaisesRegex(AnalysisRefusal,'^analysis_checkout_not_clean$') as refusal:
            d.analysis_checkout()
        self.assertEqual(refusal.exception.analysis_commit,'0'*40)
        with mock.patch.object(d.subprocess,'run',side_effect=[
                mock.Mock(stdout='0'*40+'\n'),mock.Mock(stdout='')]):
            self.assertEqual(d.analysis_checkout(),'0'*40)


from copy import deepcopy
from dataclasses import replace
from types import SimpleNamespace
from joulewise.b5_analysis.windows import IndexEntry, WindowIndex, SealPins, load_window_index


class FakeArchive:
    def __init__(self, window):
        self.window=window
        self.record={'outputs':{}}
    def census(self):
        from joulewise.b5_analysis.archive import CensusRow
        return (CensusRow('derived/exclusions.json',_hash(self.window.archive_root/'derived/exclusions.json'),'harvest_outputs'),)
    def source_names(self):
        return tuple('repo/configs/campaigns/'+self.window.pack_id+'/'+name for name in ('analysis_manifest_v3.json','plan_tree.json'))
    def source_bytes(self,relative):
        if relative.endswith('analysis_manifest_v3.json'):return d._canonical({'manifest_id':'c'*64})
        if relative.endswith('plan_tree.json'):return b'{}'
        return b'ledger\n'
    def output_bytes(self,relative):
        return b'{}'


def _hash(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class DriverDouble(d.StepRunner):
    """Only StepRunner is replaced: each registered dispatch builds real argv.

    Internal readers install structure views at the same runner seam. Script
    doubles write their wire skeleton plus the 7331 float marker; the real
    caller still registers, classifies, hashes and consumes those files.
    """
    calls=[]
    refusal=None
    outcome=False
    exception_at=None
    change_at=None
    fail_bundle=False
    p42=False
    target_refusal=False
    bad_projection=False
    release_change=None
    source_case=None

    def _initial(self,s):
        s.index=load_window_index(s.index_path,seal_pins=s.pins,pack_table=s.pack_table)
        s.records=[]
        for entry in s.index.entries:
            record=SimpleNamespace(entry=entry,record_shape='pin2',verdict='COLLECTED',claim_usable=True,census=())
            s.records.append(record)
            window=SimpleNamespace(**{name:getattr(entry,name) for name in (
                'pack','pack_id','plan_id','attempt','harvest_pin','harvest_record_sha256','archive_root',
                'claim_runs_root','bound_runs_root','measurement_root','custody_root')},record=record)
            s.windows[entry.pack]=window;s.archives[entry.pack]=FakeArchive(window)
            s.write('census_'+entry.pack,'supply-census/'+entry.pack+'.json',
                [{'path':'derived/exclusions.json','sha256':_hash(entry.archive_root/'derived/exclusions.json'),'check':'harvest_outputs'}])
        s.records=tuple(s.records)

    def _kept(self,s):
        for pack,window in s.windows.items():
            cell=SimpleNamespace(n_r=1,n_b=1)
            kept=SimpleNamespace(window=window,cells={'cell':cell},kept_run_ids=lambda cid:frozenset({'kept'}),removed_run_ids=lambda:frozenset({'removed'}))
            s.kept[pack]=kept
            s.specs[pack]={'cells':[{'cell_id':pack+'-target','kind':'absolute','condition_family_id':'cell-target'},
                {'cell_id':pack+'-p42','kind':'absolute','condition_family_id':'cell-p42'}]}
        s.rows={p:{'evaluation_basis':{},'idle_admission_core':{},'status':'failed'} for p in d.PACKS}

    def run(self,main,argv,*,step,window=None,stdout_path=None):
        type(self).calls.append((step,window,list(argv)))
        state=getattr(main,'_state',None)
        if state is not None:self.state=state
        s=self.state
        if self.change_at==step:
            s.output('extraction_alpha').write_text('changed')
        name=getattr(main,'_operation',None)
        def program(argv):
            # Reader outputs and logs carry only structure (T19).
            if step not in ('0','3'):
                print(MARKER);print(MARKER,file=__import__('sys').stderr)
            if self.exception_at==step:raise RuntimeError(MARKER)
            if self.refusal and self.refusal[0]==step:
                print('error: '+self.refusal[1]+': '+MARKER,file=__import__('sys').stderr);return 2
            if name=='prepare_initial':
                self._initial(s);return 0
            if name=='prepare_kept':
                self._kept(s);return 0
            if name=='prepare_tripwires':
                for pack in d.PACKS:s.write('kept_'+pack,'kept-units/'+pack+'.json',{'schema_version':'joulewise.b5_kept_units.v1','pack':pack,'cells':{'cell':{'n_r':1,'n_b':1}}})
                return 0
            if name=='prepare_finalization':
                for role,relative,value in (('gamma_pack_manifest','finalized/inputs/gamma-pack/analysis_manifest_v3.json',{'manifest_id':'am-'+'c'*64}),
                        ('gamma_pack_tree','finalized/inputs/gamma-pack/plan_tree.json',{}),('gamma_verdict','finalized/inputs/gamma-verdict.json',{}),
                        ('gamma_binding','finalized/inputs/gamma-binding.json',{}),('gamma_ledger','finalized/inputs/gamma-ledger.jsonl',{})):
                    s.write(role,relative,value)
                for role,basename in (('final_floor','aggregate-floor.json'),('final_sidecar','dominance-replay.json'),
                                  ('final_pinset','floor-mint-pinset.json')):
                    s.write(role,'finalized/mint/'+basename,raw=s.output({'final_floor':'floor_artifact',
                        'final_sidecar':'sidecar','final_pinset':'pinset'}[role]).read_bytes())
                return 0
            if name=='prepare_brackets':
                s.b_max=SimpleNamespace(T=1)
                for pack in d.PACKS:s.write('bracket_'+pack,'brackets/'+pack+'.json',{'marker':12.3457331})
                return 0
            if state is not None and step=='9b':
                s.write('claim_request','custody/request.json',{'schema_version':'joulewise.claim_replay_request.v1','marker':12.3457331})
                return 0
            if state is not None and step=='10':
                return 0
            if state is not None and step=='11':
                s.write('sensitivity','outputs/sensitivity.json',{'schema_version':'joulewise.b5_sensitivity.v1','marker':12.3457331})
                s.write('step_results','outputs/step-results.json',{'windows':{},'marker':12.3457331})
                return 0
            if argv and argv[0]=='validate-bundle':
                return 1 if self.fail_bundle else 0
            if '--validate-rendered' in argv:return 0
            if stdout_path is not None:
                print('# Rendered '+MARKER+(' ' if self.release_change=='results-fills.md' and s.mode=='release' else ''));return 0
            def write(path,value):
                path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
                raw=d._canonical(value)
                if self.release_change and s.mode=='release' and self.release_change==path.name:raw+=b' '
                path.write_bytes(raw)
            def option(flag):return argv[argv.index(flag)+1]
            binding={'exclusions_sha256':'e'*64,'harvest_pin':'a'*40}
            value={'marker':12.3457331}
            module=getattr(main,'__module__','')
            if step=='2':write(option('--output'),{'schema_version':'joulewise.summary_metrics.v1',**value})
            elif step=='4':
                value.update(schema_version='joulewise.detection_floor_extraction.v1',kept_units_binding=binding,
                    spec_membership_refusals=[],cells=[{'cell_id':window+'-target','extractable':not self.target_refusal},
                                                     {'cell_id':window+'-p42','extractable':not self.p42}])
                write(option('--out'),value)
                if self.p42 or self.target_refusal:return 1
            elif step=='5' and '--out-dir' in argv:
                directory=Path(option('--out-dir'))
                for relative in ('floor-mint-pinset.json','floor-mint-inputs.json','alpha/calibration_plan.json','beta/calibration_plan.json',
                                 'alpha/order_manifest.json','beta/order_manifest.json'):
                    write(directory/relative,{'schema_version':'joulewise.floor_mint_inputs.block5.v1',**value})
            elif step=='5':
                value.update(schema_version='joulewise.detection_floor_artifact.v2',cells=[{
                    'cell_id':pack+'-target','provenance':{kind:{'calibration_cell_id':pack+'-target',
                        'evidence_root_id':pack+'-root'} for kind in ('absolute','comparative')}}
                    for pack in ('alpha','beta')])
                write(option('--out'),value);write(option('--single-count-out'),{'schema_version':'joulewise.single_count.v1'})
                write(option('--d165-replay-out'),{'schema_version':'joulewise.d165_dominance_replay.v1',**{'marker':12.3457331}})
            elif step=='8':
                from joulewise.analysis_manifest_v3 import FINALIZED_BASENAME_SUFFIX
                write(Path(option('--output-dir'))/('am-'+'c'*64+FINALIZED_BASENAME_SUFFIX),
                      {'schema_version':'joulewise.analysis_manifest.v3',**value})
            elif step=='6':
                output=Path(option('--output'));write(output,{'schema_version':'joulewise.d165_dominance_closeout.v1',**value})
                write(output.with_name(output.stem+'.ratio-table.json'),{'schema_version':'joulewise.b5_d165_ratio_table.v1',**value})
                if self.outcome:
                    print(json.dumps({'status':'outcome_class','refusal':'outcome-class refusal at step 6'}));return 3
            elif step=='9':write(option('--output'),{'schema_version':'joulewise.claim_verdicts.v1',**value})
            elif step=='10':
                value.update(schema_version='joulewise.paper_reported_energy_projection.v1',
                    window={'harvest_pin':binding['harvest_pin']},exclusions_sha256='f'*64 if self.bad_projection else binding['exclusions_sha256'])
                write(option('--output'),value)
            elif step=='11' and '--step-outputs' in argv:
                root=Path(option('--custody'))/'disclosures'
                for relative in ('record.json','view.unreleased.txt','view.released.txt'):
                    write(root/relative,{'schema_version':'joulewise.b5_disclosures.v1',**value})
            elif step=='11':write(option('--out'),{'schema_version':'joulewise.results_fill_input.v1',**value})
            return 0
        return super().run(program,argv,step=step,window=window,stdout_path=stdout_path)


class DriverAcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(prefix='s10-driver-')
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.root=Path(cls.tmp.name);cls.repo=cls.root/'repo';cls.repo.mkdir()
        cls.table={p:{'s10-'+p:'s10-'+p+'-a{attempt}-'} for p in d.PACKS}
        cls.pins=SealPins.load()
        entries=[]
        for pack in d.PACKS:
            root=cls.root/pack;root.mkdir()
            archive=root/'archive';(archive/'derived').mkdir(parents=True)
            (archive/'derived/exclusions.json').write_text('{}')
            record={'outputs':{'derived/exclusions.json':_hash(archive/'derived/exclusions.json')}}
            (archive/'harvest.json').write_bytes(d._canonical(record))
            runs=root/'runs';runs.mkdir();(runs/'kept').mkdir();(runs/'removed').mkdir()
            measurement=root/'measurement';(measurement/'runs').mkdir(parents=True)
            (measurement/'runs/calibration_observation_ledger.jsonl').write_bytes(b'ledger\n')
            entries.append({'pack':pack,'pack_id':'s10-'+pack,'attempt':1,'plan_id':'s10-'+pack+'-a1-window',
                't0_epoch_s':cls.pins.erratum_2_epoch_s,'seal':'second','entry_kind':'harvested','archive_root':str(archive),
                'harvest_record_sha256':_hash(archive/'harvest.json'),'superseded_archive_roots':[],
                'claim_runs_root':str(runs),'bound_runs_root':str(root/'bound'),'custody_root':str(root/'custody'),
                'measurement_root':str(measurement),'harvest_pin':cls.pins.pins['pin2']['head'],'verdict':'COLLECTED','claim_usable':True})
        cls.index=cls.root/'index.json';cls.index.write_bytes(d._canonical({'schema':'joulewise.b5_window_index.v1','attempts':entries}))
        cls.serial=0

    def setUp(self):
        for key,value in {'calls':[],'refusal':None,'outcome':False,'exception_at':None,'change_at':None,
                'fail_bundle':False,'p42':False,'target_refusal':False,'bad_projection':False,'release_change':None}.items():
            setattr(DriverDouble,key,value)

    def execute(self,*,mode='blind-dry-run',custody=None,runner=DriverDouble,git=None):
        type(self).serial+=1
        custody=custody or self.root/('custody-'+str(self.serial))
        stdout,stderr=io.StringIO(),io.StringIO()
        with redirect_stdout(stdout),redirect_stderr(stderr):
            code=d.run(mode,self.index,custody,_test_pack_table=self.table,_test_repo_root=self.repo,
                       _runner=runner,_git=git or (lambda repo:'b'*40))
        record_path=custody/('dry-run/B5-BLIND-DRY-RUN-RECORD.json' if mode=='blind-dry-run' else 'release/B5-RELEASE-RECORD.json')
        record=json.loads(record_path.read_bytes()) if record_path.exists() else None
        return SimpleNamespace(code=code,custody=custody,record=record,path=record_path,stdout=stdout.getvalue(),stderr=stderr.getvalue())

    def test_T1_closed_record_rejects_float_string_unnamed_integer_unknown_key(self):
        result=self.execute();self.assertEqual(result.code,0,result.stderr)
        valid=result.record
        index=load_window_index(self.index,seal_pins=self.pins,pack_table=self.table)
        kept={p:SimpleNamespace(cells={'cell':None}) for p in d.PACKS}
        d.validate_dry_run_record(valid,index=index,kept_units=kept)
        mutations=[]
        bad=deepcopy(valid);bad['steps'][0]['outputs'][0]['sha256']=12.3457331;mutations.append(bad)
        bad=deepcopy(valid);bad['steps'][0]['status']='arbitrary';mutations.append(bad)
        bad=deepcopy(valid);bad['steps'][0]['schema_valid']=1;mutations.append(bad)
        bad=deepcopy(valid);bad['extra']=None;mutations.append(bad)
        bad=deepcopy(valid);bad['steps'][0]['outputs'][0]['name']='outputs/1e100.json';mutations.append(bad)
        bad=deepcopy(valid);bad['windows'][0]['kept_counts']['invented']={'n_r':1,'n_b':1};mutations.append(bad)
        for bad in mutations:
            with self.subTest(bad=bad),self.assertRaisesRegex(AnalysisRefusal,'^dry_run_record_invalid$'):
                d.validate_dry_run_record(bad,index=index,kept_units=kept)

    def test_T2_driver_streams_are_one_commitment_and_closed_step_lines(self):
        result=self.execute();self.assertEqual(result.code,0,result.stderr)
        self.assertRegex(result.stdout,r'^\S+ [0-9a-f]{64}\n$')
        for line in result.stderr.splitlines():
            self.assertRegex(line,r'^step (?:0|1|2|3|3b|4|5|8|6|9|9b|10|11) (?:alpha|beta|gamma|-) (?:ok|tooling_refusal|outcome_class|unclassified_refusal|not_run)$')

    def test_T3_every_unrestricted_byte_has_no_marker_or_float_token(self):
        result=self.execute();self.assertEqual(result.code,0,result.stderr)
        exposed=[result.stdout,result.stderr]
        for path in result.custody.rglob('*'):
            if path.is_file() and 'restricted' not in path.parts:exposed.append(path.read_text())
        import re
        for text in exposed:
            # A random SHA-256 (the record's own digest on stdout) can contain
            # the marker's digits; search the text with hex digests removed.
            self.assertNotIn('7331',re.sub(r'[0-9a-f]{64}','',text))
            # Hex digests are explicitly admitted tokens, including sequences
            # such as 1e9. Search numeric tokens, not substrings of hashes.
            self.assertIsNone(d._FLOAT_TOKEN.search(text),text)

    def test_T4_exception_and_tooling_detail_never_escape(self):
        DriverDouble.exception_at='9';result=self.execute()
        self.assertEqual(result.code,2);self.assertNotIn('7331',result.path.read_text()+result.stdout+result.stderr)
        self.assertEqual(next(r for r in result.record['steps'] if r['step']=='9')['refusal'],'unclassified refusal at step 9')
        DriverDouble.exception_at=None;DriverDouble.refusal=('5','window_index_required')
        result=self.execute();row=next(r for r in result.record['steps'] if r['step']=='5')
        self.assertEqual(row['refusal'],'window_index_required')
        self.assertNotIn('7331',result.path.read_text()+result.stdout+result.stderr)

    def test_T5_unlisted_step9_refusal_stops_and_is_unclassified(self):
        DriverDouble.refusal=('9','unlisted_7331');result=self.execute()
        self.assertEqual(result.code,2);self.assertFalse(result.record['completed_without_tooling_refusal'])
        self.assertNotIn('unlisted_7331',result.path.read_text()+result.stdout+result.stderr)
        self.assertEqual([r['status'] for r in result.record['steps'] if r['step'] in ('9b','10','11')],['not_run']*3)

    def test_T6_exit3_registers_closeout_and_ratio_but_stops_every_later_step(self):
        DriverDouble.outcome=True;result=self.execute();self.assertEqual(result.code,3,result.stderr)
        row=next(r for r in result.record['steps'] if r['step']=='6')
        self.assertEqual(row['status'],'outcome_class');self.assertEqual(row['refusal'],'outcome-class refusal at step 6')
        self.assertEqual(len(row['outputs']),2);self.assertTrue(result.record['completed_without_tooling_refusal'])
        self.assertTrue(all(r['status']=='not_run' for r in result.record['steps'] if r['step'] in ('9','9b','10','11')))
        self.assertFalse(any(step=='9' for step,_,_ in DriverDouble.calls))

    def test_T7_tooling_step5_refusal_calls_no_later_program(self):
        DriverDouble.refusal=('5','window_index_required');result=self.execute();self.assertEqual(result.code,2)
        self.assertFalse(any(step in ('8','6','9','9b','10','11') for step,_,_ in DriverDouble.calls))
        self.assertTrue(all(r['status']=='not_run' for r in result.record['steps'] if r['step'] in ('8','6','9','9b','10','11')))

    def test_T8_p42_only_exception_and_target_refusal(self):
        DriverDouble.p42=True;result=self.execute();self.assertEqual(result.code,0,result.stderr)
        self.assertTrue(any(step=='5' for step,_,_ in DriverDouble.calls))
        self.assertEqual([r['registered_exit'] for r in result.record['steps'] if r['step']=='4'],['p42_floor_cells_only']*2)
        DriverDouble.calls=[];DriverDouble.target_refusal=True;result=self.execute();self.assertEqual(result.code,2)
        self.assertFalse(any(step=='5' for step,_,_ in DriverDouble.calls))

    def test_T9_strict_validation_stops_and_never_visits_removed_bundle(self):
        result=self.execute();self.assertEqual(result.code,0,result.stderr)
        bundles=[argv[-1] for step,_,argv in DriverDouble.calls if step=='1' and argv]
        self.assertEqual(len(bundles),3);self.assertTrue(all(Path(path).name=='kept' for path in bundles))
        DriverDouble.calls=[];DriverDouble.fail_bundle=True;result=self.execute()
        self.assertEqual(result.code,2);self.assertFalse(any(step=='2' for step,_,_ in DriverDouble.calls))
        row=next(r for r in result.record['steps'] if r['step']=='1')
        self.assertEqual(row['refusal'],'kept_bundle_strict_validation_failed')

    def test_T10_rereductions_under_restricted_and_each_digest_registered(self):
        result=self.execute();self.assertEqual(result.code,0,result.stderr)
        row=next(r for r in result.record['steps'] if r['step']=='2')
        self.assertEqual(len(row['outputs']),3)
        for output in row['outputs']:
            self.assertTrue(output['name'].startswith('rereduced/'))
            path=result.path.parent/'restricted'/output['name']
            self.assertEqual(_hash(path),output['sha256'])
        for step,_,argv in DriverDouble.calls:
            if step=='2':self.assertIn('/restricted/rereduced/',argv[-1])

    def test_closeout_child_record_keeps_its_sibling_output_bindings(self):
        class WithChildRecord(DriverDouble):
            def run(self,main,argv,**kwargs):
                result=super().run(main,argv,**kwargs)
                if kwargs['step']=='6' and '--output' in argv:
                    path=Path(argv[argv.index('--output')+1]);ratio=path.with_suffix('.ratio-table.json')
                    child=step_record('6',schema_valid=True,outputs=tuple(
                        {'name':p.name,'sha256':_hash(p)} for p in (path,ratio)))
                    path.with_suffix('.step.json').write_bytes(d._canonical(child.as_dict()))
                return result
        result=self.execute(runner=WithChildRecord);self.assertEqual(result.code,0,result.stderr)
        step=next(row for row in result.record['steps'] if row['step']=='6')
        child_path=result.path.parent/'restricted'/next(item['name'] for item in step['outputs'] if item['name'].endswith('.step.json'))
        for output in json.loads(child_path.read_bytes())['outputs']:
            sibling=child_path.parent/output['name']
            self.assertTrue(sibling.is_file());self.assertEqual(_hash(sibling),output['sha256'])

    def test_T13_changed_earlier_output_is_refused_before_consuming_program(self):
        class Changed(DriverDouble):
            def run(self,main,argv,**kwargs):
                result=super().run(main,argv,**kwargs)
                if kwargs['step']=='4' and kwargs['window']=='beta':self.state.output('extraction_alpha').write_text('tampered')
                return result
        result=self.execute(runner=Changed);self.assertEqual(result.code,2,result.stderr)
        row=next(r for r in result.record['steps'] if r['step']=='5')
        self.assertEqual(row['refusal'],'step_input_digest_mismatch')
        self.assertFalse(any(step=='5' for step,_,_ in Changed.calls))

    def test_T14_projection_must_match_step4_exclusions_and_harvest_pin(self):
        DriverDouble.bad_projection=True;result=self.execute();self.assertEqual(result.code,2,result.stderr)
        row=next(r for r in result.record['steps'] if r['step']=='10')
        self.assertEqual(row['refusal'],'step10_window_not_admitted_by_step4')
        self.assertFalse(any(step=='11' for step,_,_ in DriverDouble.calls))
        rec=step_record('4',exit_status=0)
        for projection in ({'window':{'harvest_pin':'b'*40},'exclusions_sha256':'e'*64},
                           {'window':{'harvest_pin':'a'*40},'exclusions_sha256':'f'*64},
                           {'kept_units_binding':{'harvest_pin':'a'*40,'exclusions_sha256':'e'*64}},{}):
            with self.assertRaisesRegex(AnalysisRefusal,'^step10_window_not_admitted_by_step4$'):
                d.require_step10_admission(rec,projection,{'kept_units_binding':{'harvest_pin':'a'*40,'exclusions_sha256':'e'*64}})

    def test_finalization_has_its_own_custody_root_and_claim_verdicts_lie_outside_it(self):
        # The finalizer requires output_dir == custody_root; the engine refuses a
        # claim-verdict output inside the finalized manifest's directory (S10).
        DriverDouble.calls=[]
        result=self.execute();self.assertEqual(result.code,0,result.stderr)
        option=lambda argv,flag:Path(str(argv[argv.index(flag)+1]))
        final=next(argv for step,_,argv in DriverDouble.calls if step=='8' and argv)
        self.assertEqual(option(final,'--custody-root'),option(final,'--output-dir'))
        self.assertEqual(option(final,'--custody-root').name,d.FINALIZATION)
        for flag in ('--prospective-manifest','--plan-tree','--whole-window-verdict','--bracket-binding',
                     '--calibration-ledger','--aggregate-floor-artifact','--dominance-replay-sidecar'):
            self.assertTrue(option(final,flag).is_relative_to(option(final,'--custody-root')),flag)
        claim=next(argv for step,_,argv in DriverDouble.calls if step=='9' and argv)
        manifest=option(claim,'--analysis-manifest')
        self.assertEqual(manifest.parent,option(final,'--output-dir'))
        self.assertFalse(option(claim,'--output').is_relative_to(manifest.parent))
        closeout=next(argv for step,_,argv in DriverDouble.calls if step=='6' and argv)
        self.assertEqual(option(closeout,'--custody-root'),option(final,'--custody-root'))
        self.assertTrue(option(closeout,'--output').is_relative_to(option(closeout,'--custody-root')))

    def test_T15_all_block5_script_argv_include_window_index(self):
        result=self.execute();self.assertEqual(result.code,0,result.stderr)
        for step,_,argv in DriverDouble.calls:
            if argv and step in ('4','5','8','6','9','10','11') and '--validate-rendered' not in argv and not str(argv[0]).endswith('results-fill-input.json'):
                self.assertIn('--window-index',argv)
        claim=next(argv for step,_,argv in DriverDouble.calls if step=='9' and argv)
        roots={claim[i+1] for i,arg in enumerate(claim) if arg=='--evidence-root'}
        entries=json.loads(self.index.read_bytes())['attempts']
        self.assertEqual(roots,{row['pack']+'-root='+row['claim_runs_root'] for row in entries if row['pack'] in ('alpha','beta')})

    def test_T16_backup_roots_unset_during_run_flagged_and_restored(self):
        class Env(DriverDouble):
            def run(self,*args,**kwargs):
                if 'JOULEWISE_BACKUP_ROOTS' in os.environ:raise AssertionError('environment override survived')
                return super().run(*args,**kwargs)
        with mock.patch.dict(os.environ,{'JOULEWISE_BACKUP_ROOTS':'synthetic'}):
            result=self.execute(runner=Env)
            self.assertEqual(os.environ['JOULEWISE_BACKUP_ROOTS'],'synthetic')
        self.assertEqual(result.code,0,result.stderr)
        self.assertIn('backup_roots_env_ignored',result.record['steps'][0]['flags'])

    def test_T17_preflight_refuses_inside_symlink_occupied_and_dirty(self):
        cases=[(self.repo/'custody','custody_inside_repository'),
               (self.root/'custody with whitespace','custody_path_invalid')]
        occupied=self.root/'occupied';(occupied/'dry-run').mkdir(parents=True,exist_ok=True)
        cases.append((occupied,'custody_run_directory_exists'))
        link=self.root/'symlink-custody'
        if not link.exists():link.symlink_to(occupied,target_is_directory=True)
        cases.append((link,'custody_path_invalid'))
        nested=self.root/'nested-symlink';nested.mkdir(exist_ok=True)
        if not (nested/'alias').exists():(nested/'alias').symlink_to(occupied,target_is_directory=True)
        cases.append((nested,'custody_path_invalid'))
        for path,code in cases:
            with self.subTest(code=code),self.assertRaisesRegex(AnalysisRefusal,'^'+code+'$'):
                d.custody_preflight('blind-dry-run',path,self.repo)
        with redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):
            code=d.run('blind-dry-run',self.index,self.root/'dirty',_test_repo_root=self.repo,
                _runner=DriverDouble,_git=lambda repo:(_ for _ in ()).throw(AnalysisRefusal('analysis_checkout_not_clean')))
        self.assertEqual(code,2);self.assertEqual(DriverDouble.calls,[])

    def test_T19_no_step0_or_step3_file_contains_a_float_token(self):
        result=self.execute();self.assertEqual(result.code,0,result.stderr)
        for row in result.record['steps']:
            if row['step'] in ('0','3'):
                for output in row['outputs']:
                    self.assertIsNone(d._FLOAT_TOKEN.search((result.path.parent/'restricted'/output['name']).read_text()))
        for path in (result.path.parent/'restricted/logs').glob('*'):
            if path.name.split('-')[1] in ('0','3'):self.assertIsNone(d._FLOAT_TOKEN.search(path.read_text()))

    def test_T20_step11_ends_at_fill_input_without_renderer_capture(self):
        result=self.execute();self.assertEqual(result.code,0,result.stderr)
        row=next(r for r in result.record['steps'] if r['step']=='11')
        self.assertIn('results_rendering_not_run_no_block5_template', row['flags'])
        self.assertTrue(any('results-fill-input' in o['name'] for o in row['outputs']))
        self.assertFalse(any('results-fills.md' in o['name'] for o in row['outputs']))
        self.assertFalse((result.path.parent/'restricted/outputs/results-fills.md').exists())
        self.assertFalse(any('results-fills.md' in str(argv) or '--validate-rendered' in argv
                             for _, _, argv in DriverDouble.calls))
        self.assertNotIn(MARKER,result.stdout+result.stderr)


class ArgumentCensusDouble(DriverDouble):
    """Dispatch-only census: no assigned program's main is executed.

    Keep the established double's output skeletons solely to let every real
    driver dispatch construct its argv. Replace input locators with the public
    chain index, including its explicitly provisional peers while incomplete.
    """
    fixture = None
    census = []

    def _initial(self, s):
        from tests.b5_analysis.joined_s10 import chain_entries
        super()._initial(s)
        self.real_entries = chain_entries(self.fixture)
        s.index_path = self.fixture.program_index
        for pack, window in s.windows.items():
            entry = self.real_entries[pack]
            for field in ('claim_runs_root', 'archive_root', 'bound_runs_root', 'custody_root', 'measurement_root'):
                setattr(window, field, Path(entry[field]))

    def _kept(self, s):
        super()._kept(s)
        for pack, kept in s.kept.items():
            # ALPHA's real member locator; future complete builds supply the
            # corresponding public writer rows for BETA and GAMMA as well.
            window = self.fixture.windows.get(pack)
            if window is None:
                run_id = 'unbuilt-member'
            else:
                exclusions = json.loads((window.archive/'derived/exclusions.json').read_bytes())
                listed = {(cell['cell_id'], stratum, unit_id) for cell in exclusions['cells']
                          for stratum, ids in cell['kept_units'].items() for unit_id in ids}
                roster = json.loads((window.archive/'derived/roster.json').read_bytes())
                run_id = next(member['run_id'] for member in roster['members']
                    if any((unit['cell_id'], unit['stratum'], unit['unit_id']) in listed
                           for unit in member.get('units', [])))
            kept.kept_run_ids = lambda cid, run_id=run_id: frozenset({run_id})

    def run(self, main, argv, **kwargs):
        if not hasattr(main, '_operation'):
            type(self).census.append((kwargs['step'], kwargs.get('window'), main, list(argv)))
        result = super().run(main, argv, **kwargs)
        type(self).last_state = self.state
        return result


class JoinedArgumentTests(unittest.TestCase):
    setUpClass = classmethod(DriverAcceptanceTests.setUpClass.__func__)
    setUp = DriverAcceptanceTests.setUp
    execute = DriverAcceptanceTests.execute

    def test_B2_every_real_dispatch_parses_and_uses_chain_input_roles(self):
        from tests.b5_analysis.fixtures_s10 import chain_fixture
        from tests.b5_analysis.joined_s10 import parse_program_argv, chain_entries
        from scripts import produce_b5_disclosures as disclosures
        ArgumentCensusDouble.fixture = chain_fixture()
        ArgumentCensusDouble.census = []
        result = self.execute(runner=ArgumentCensusDouble)
        self.assertEqual(result.code, 0, result.stderr)
        entries = chain_entries(ArgumentCensusDouble.fixture)
        restricted = result.path.parent / 'restricted'
        state = ArgumentCensusDouble.last_state
        parsed = []
        for step, pack, main, argv in ArgumentCensusDouble.census:
            with self.subTest(step=step, pack=pack, program=main.__module__, argv=argv):
                args = parse_program_argv(main, argv)
                parsed.append((step, pack, main.__module__, args))
                if hasattr(args, 'window_index'):
                    self.assertEqual(Path(args.window_index), ArgumentCensusDouble.fixture.program_index)
                if step in ('1', '2'):
                    self.assertEqual(Path(args.path).parent, Path(entries[pack]['claim_runs_root']))
                    if pack in ArgumentCensusDouble.fixture.windows:
                        self.assertTrue(Path(args.path).is_dir())
                    if step == '1':
                        self.assertTrue(args.strict)
                    else:
                        self.assertEqual(Path(args.output), state.output('rereduced_'+pack+'_'+Path(args.path).name))
                elif step == '4':
                    self.assertEqual(args.pack, pack)
                    self.assertTrue(args.hash_bundles)
                    self.assertEqual(args.out.parent, restricted / 'mint')
                elif step == '5' and hasattr(args, 'out_dir'):
                    self.assertEqual(args.out_dir, restricted / 'mint')
                    for producer in ('alpha', 'beta'):
                        self.assertTrue(getattr(args, producer+'_report').is_file())
                        self.assertEqual(getattr(args, producer+'_report'), state.output('extraction_'+producer))
                    self.assertEqual(args.project_commit, state.commit)
                elif step == '5':
                    self.assertEqual(args.pinset, restricted / 'mint/floor-mint-pinset.json')
                    self.assertEqual(args.v2_input_manifest, restricted / 'mint/floor-mint-inputs.json')
                    self.assertEqual(args.project_tree_state, 'clean')
                    self.assertTrue(args.pinset.is_file())
                    self.assertTrue(args.v2_input_manifest.is_file())
                    self.assertEqual(args.pinset_sha256, state.outputs['pinset']['sha256'])
                    self.assertEqual(args.project_commit, state.commit)
                    self.assertTrue(all(path.parent == args.pinset.parent
                        for path in (args.out, args.single_count_out, args.d165_replay_out)))
                elif step == '8':
                    self.assertEqual(args.runs_root, Path(entries['gamma']['claim_runs_root']))
                    final = restricted / d.FINALIZATION
                    self.assertEqual(args.prospective_manifest, final / 'inputs/gamma-pack/analysis_manifest_v3.json')
                    self.assertEqual(args.plan_tree, final / 'inputs/gamma-pack/plan_tree.json')
                    self.assertEqual(args.custody_root, final)
                    self.assertEqual(args.output_dir, final)
                    self.assertTrue(args.prospective_manifest.is_file())
                    self.assertTrue(args.plan_tree.is_file())
                    for name in ('whole_window_verdict', 'bracket_binding', 'calibration_ledger',
                                 'aggregate_floor_artifact', 'dominance_replay_sidecar'):
                        self.assertTrue(getattr(args, name).is_file(), name)
                    for name, role in {'whole_window_verdict':'gamma_verdict',
                        'bracket_binding':'gamma_binding', 'calibration_ledger':'gamma_ledger',
                        'aggregate_floor_artifact':'final_floor', 'dominance_replay_sidecar':'final_sidecar'}.items():
                        self.assertEqual(getattr(args, name), state.output(role))
                elif step == '6':
                    self.assertEqual(args.custody_root, restricted / d.FINALIZATION)
                    self.assertTrue(args.finalized_manifest.is_file())
                    self.assertEqual(args.finalized_manifest, state.output('finalized_manifest'))
                    self.assertEqual(args.output, state.output('closeout'))
                elif step == '9':
                    self.assertEqual(Path(args.runs_root), Path(entries['gamma']['claim_runs_root']))
                    self.assertEqual(Path(args.neg8_harvest_archive), Path(entries['gamma']['archive_root']))
                    self.assertEqual({str(root) for root in args.evidence_roots.values()},
                                     {entries[p]['claim_runs_root'] for p in ('alpha', 'beta')})
                    self.assertTrue(Path(args.analysis_manifest).is_file())
                    self.assertTrue(Path(args.floor_artifact).is_file())
                    self.assertEqual(Path(args.analysis_manifest), state.output('finalized_manifest'))
                    self.assertEqual(Path(args.floor_artifact), state.output('floor_artifact'))
                elif step == '10':
                    self.assertEqual(args.pack, pack)
                    self.assertEqual(args.output.parent, restricted / 'outputs')
                elif step == '11' and main is disclosures.main:
                    self.assertEqual(args.custody, restricted)
                    registry = json.loads(args.step_outputs.read_bytes())
                    self.assertEqual(set(registry), set(disclosures.ROLES))
                    self.assertTrue(all((restricted/item['path']).is_file() for item in registry.values()))
                    self.assertEqual(args.step_outputs, state.output('step_outputs'))
                    for role, item in registry.items():
                        self.assertEqual(restricted/item['path'], state.output(role))
                        self.assertEqual(item['sha256'], state.outputs[role]['sha256'])
                elif step == '11' and hasattr(args, 'finalized_manifest'):
                    self.assertEqual(args.custody_root, restricted)
                    self.assertTrue(args.finalized_manifest.is_file())
                    self.assertTrue(args.claim_verdicts.is_file())
                    self.assertEqual(args.finalized_manifest, state.output('finalized_manifest'))
                    self.assertEqual(args.claim_verdicts, state.output('claim_verdicts'))
        expected = {'joulewise.cli', 'scripts.extract_detection_floors', 'scripts.emit_floor_mint_pinset',
            'scripts.mint_floor_artifact_generalized', 'scripts.finalize_analysis_manifest',
            'scripts.run_d165_closeout_from_custody', 'scripts.issue_reported_energy',
            'scripts.produce_b5_disclosures', 'scripts.build_results_fill_input'}
        self.assertEqual({module for _, _, module, _ in parsed}, expected)
        self.assertEqual(len(parsed), 17)


class JoinedHarnessMockTests(unittest.TestCase):
    """S0 front-door census, including its missing GAMMA claim manifest.

    This is a fixture-limitation assertion, not J1--J6 acceptance. Advancing
    these old packs requires new producer inputs; no consumer check is stubbed.
    """
    @classmethod
    def setUpClass(cls):
        from tests.b5_analysis import fixtures as fx, fixtures_s3 as s3, fixtures_s3b as sb
        from tests.b5_analysis.joined_s10 import JoinedHarness
        cls.built = {pack:(sb.cached('BETA_STD') if pack == 'beta' else s3.cached(pack.upper()+'_STD'))
                     for pack in d.PACKS}
        rows = [window.entry_data for window in cls.built.values()]
        beta = cls.built['beta'].entry_data
        rows = [{**beta, 'attempt':n, 'entry_kind':'no_archive', 'archive_root':None,
            'harvest_record_sha256':None, 'verdict':'NO_COLLECTION', 'claim_usable':False,
            'record_citation':'synthetic-history.md:1'} for n in range(1, beta['attempt'])] + rows
        cls.temporary = tempfile.TemporaryDirectory(prefix='s10-mock-index-')
        cls.addClassCleanup(cls.temporary.cleanup)
        index = Path(cls.temporary.name)/'index.json'
        index.write_bytes(d._canonical({'schema':'joulewise.b5_window_index.v1', 'attempts':rows}))
        cls.harness = JoinedHarness(index, windows=cls.built.values(), pack_table=fx.PACK_TABLE)
        cls.addClassCleanup(cls.harness.close)
        cls.result = cls.harness.execute()

    def test_B1_s0_missing_gamma_manifest_is_the_first_stop(self):
        self.assertEqual(self.result.record['steps'][0]['status'], 'ok', self.result.stderr)
        stop = next(row for row in self.result.record['steps'] if row['status'] != 'ok')
        self.assertEqual((stop['step'], stop['status'], stop['refusal']),
                         ('1', 'tooling_refusal', 'archive_source_unauthenticated'))
        state = self.result.state
        missing = 'repo/configs/campaigns/'+state.windows['gamma'].pack_id+'/analysis_manifest_v3.json'
        self.assertNotIn(missing, state.archives['gamma'].source_names())
        self.assertEqual(set(state.kept), {'alpha', 'beta'})
        self.assertFalse(any(call['step'] == '4' for call in self.result.calls))
        self.assertTrue(all(row['status'] == 'not_run' for row in self.result.record['steps'][2:]))

    def test_repository_anchor_and_observer_preserve_real_inputs(self):
        from joulewise import paper_custody as custody
        self.assertEqual(self.harness.git('show', self.harness.head+':'+custody._B5_WINDOW_INDEX_PATH).encode(),
                         self.harness.index.read_bytes())
        self.assertEqual((self.harness.repo/custody._SUPPLY_MAP_PATH).read_bytes(),
                         (d.ROOT/custody._SUPPLY_MAP_PATH).read_bytes())
        self.assertEqual(d.analysis_checkout(self.harness.repo), self.harness.head)
        self.assertIsInstance(self.result.state, d.RunState)
        self.assertTrue(self.result.calls)
        self.assertTrue(all(isinstance(call['result'], d.RunnerResult) for call in self.result.calls))
        self.assertFalse(self.result.disclosure_reads)

    def test_only_git_seams_replay_registered_history_and_tracked_index(self):
        from joulewise import paper_custody as custody, paper_reported_energy as energy, identity_pins
        with self.harness.git_seams() as checkout:
            self.assertEqual(checkout(self.harness.repo), self.harness.head)
            energy._verify_gate_ordering(self.harness.repo)
            self.assertEqual(identity_pins._mint_git_anchor(require_origin_main=True),
                             (self.harness.repo, self.harness.head))
            ctx = SimpleNamespace(repository=self.harness.repo, head=self.harness.head)
            self.assertEqual(custody._tracked_window_index(ctx), self.harness.index)


class JoinedPartialIndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from tests.b5_analysis.fixtures_s10 import chain_fixture
        from tests.b5_analysis import fixtures as fx
        from joulewise.b5_analysis.windows import sealed_pack_table
        from tests.b5_analysis.joined_s10 import JoinedHarness, capture_driver_streams
        cls.fixture = chain_fixture()
        table = {pack:{**rows, **fx.PACK_TABLE[pack]} for pack, rows in sealed_pack_table().items()}
        cls.harness = JoinedHarness(cls.fixture.program_index, pack_table=table)
        cls.addClassCleanup(cls.harness.close)
        if len(cls.fixture.windows) == 3:
            # Keep the binding regression active after the join, without an
            # additional full driver run. Only the real initial reader runs.
            restricted = cls.harness.root/'binding-only/restricted'
            restricted.mkdir(parents=True)
            state = d.RunState('blind-dry-run', cls.harness.index, restricted, cls.harness.head,
                pack_table=table, seal_pins=cls.harness.pins, repo_root=cls.harness.repo)
            with capture_driver_streams() as streams:
                records = d.step_0(state, d.StepRunner(restricted))
            cls.result = SimpleNamespace(state=state, stderr=streams['stderr'], reader_failures=[],
                                         record={'steps':[record.as_dict() for record in records]})
        else:
            cls.result = cls.harness.execute()

    def test_B3_mixed_table_keeps_built_sealed_pack_binding(self):
        state = self.result.state
        self.assertIn('alpha', state.archives, self.result.stderr)
        archive = state.archives['alpha']
        self.assertEqual(archive.plan_tree_binding_kind, 'sealed')
        archive.plan_tree_sha256()
        self.assertTrue(any(row.check == 'plan_tree_binding:sealed' for row in archive.census()))
        if len(self.fixture.windows) == 3:
            self.assertTrue(all(row['status'] == 'ok' for row in self.result.record['steps']), self.result.stderr)
        else:
            first = next(row for row in self.result.record['steps'] if row['status'] != 'ok')
            self.assertEqual(first['step'], '0')
            self.assertNotEqual(first['refusal'], 'roster_plan_tree_not_sealed')
            peer = state.windows['beta']
            self.assertEqual(self.result.reader_failures, [dict(error='FileNotFoundError',
                path=str(peer.archive_root/'sources/repo/configs/campaigns'/peer.pack_id/'plan_tree.json'))])


class RealReaderDriverTests(unittest.TestCase):
    """Committed synthetic archives only; no joined re-reduction fixture."""
    @classmethod
    def setUpClass(cls):
        from tests.b5_analysis import fixtures as fx
        from tests.b5_analysis import fixtures_s3b as sb
        cls.fx=fx;cls.sb=sb
        from tests.b5_analysis import fixtures_s3 as s3
        cls.built={pack:(sb.cached(pack.upper()+'_STD') if pack=='beta' else s3.cached(pack.upper()+'_STD')) for pack in d.PACKS}
        cls.pins=SealPins.load()
        cls.tmp=tempfile.TemporaryDirectory(prefix='s10-real-readers-');cls.addClassCleanup(cls.tmp.cleanup)
        cls.root=Path(cls.tmp.name)
        rows=[built.entry_data for built in cls.built.values()]
        beta=next(row for row in rows if row['pack']=='beta')
        rows=[{**beta,'attempt':n,'entry_kind':'no_archive','archive_root':None,'harvest_record_sha256':None,
            'verdict':'NO_COLLECTION','claim_usable':False,'record_citation':'synthetic-history.md:1'}
            for n in range(1,beta['attempt'])]+rows
        cls.index_path=cls.root/'index.json';cls.index_path.write_bytes(d._canonical({'schema':'joulewise.b5_window_index.v1','attempts':rows}))
        cls.serial=0

    def state(self):
        type(self).serial+=1
        restricted=self.root/str(self.serial)/'restricted';restricted.mkdir(parents=True)
        return d.RunState('blind-dry-run',self.index_path,restricted,'b'*40,pack_table=self.fx.PACK_TABLE)

    def test_T11_real_step0_compares_original_runs_bytes(self):
        s=self.state();bundle=next(self.built['alpha'].claim.glob('*/summary_metrics.json'));original=bundle.read_bytes()
        try:
            bundle.write_bytes(original+b' ')
            records=d.step_0(s,d.StepRunner(s.restricted))
        finally:bundle.write_bytes(original)
        self.assertEqual(records[0].status,'tooling_refusal')
        self.assertEqual(records[0].refusal,'runs_root_differs_from_archive')

    def test_T12_real_step0_census_is_three_handle_union_plus_history_and_ledgers(self):
        s=self.state();records=d.step_0(s,d.StepRunner(s.restricted))
        self.assertEqual(records[0].status,'ok',records[0])
        _,_,census=d._record_parts(s)
        expected={(pack,row.path,row.sha256,row.check) for pack,archive in s.archives.items() for row in archive.census()}
        expected.update((row['window'],row['path'],row['sha256'],row['check']) for row in s.ledger_rows)
        selected={window.plan_id for window in s.windows.values()}
        for attempt in s.records:
            if attempt.entry.plan_id not in selected:
                expected.update((attempt.entry.pack,'sources/attempts/'+attempt.entry.plan_id+'/'+row.path,row.sha256,row.check)
                                for row in attempt.census)
        self.assertEqual({(r['window'],r['path'],r['sha256'],r['check']) for r in census},expected)
        self.assertEqual(set(s.archives),set(d.PACKS))
        self.assertTrue(all(not Path(row['path']).is_absolute() for row in census))
        for archive in s.archives.values():
            historical=json.loads(archive.output_bytes('derived/historical-custody.json'))
            # The historical-custody output carries recorded ids/outcomes; any
            # present historical locator is not read as a live capture path.
            def locators(value):
                if isinstance(value,dict):
                    for key,item in value.items():
                        if key in ('custody_locator','capture_locator') and isinstance(item,str):yield item
                        else:yield from locators(item)
                elif isinstance(value,list):
                    for item in value:yield from locators(item)
            for locator in locators(historical):
                self.assertFalse(any(row['path'].startswith(locator.rstrip('/')+'/') for row in census))
        for record in records:
            for output in record.outputs:
                self.assertIsNone(d._FLOAT_TOKEN.search((s.restricted/output['name']).read_text()))

    def test_real_step3_and_3b_boundary_reports_current_fixture_limits(self):
        from joulewise.b5_analysis.kept_units import load_kept_units
        from tests.b5_analysis.fixtures_s1 import s0_planned
        from joulewise.analysis_engine.inputs import archived_verdict_row
        from joulewise.b5_analysis.bracket import evaluate_window_bracket
        s=self.state();self.assertEqual(d.step_0(s,d.StepRunner(s.restricted))[0].status,'ok')
        s.kept={pack:load_kept_units(archive,sealed_catalog_sha256=s.pins.sealed['catalog_sha256'],planned_units=s0_planned())
                for pack,archive in s.archives.items()}
        records=d.step_3(s,d.StepRunner(s.restricted))
        self.assertEqual(records[0].status,'tooling_refusal')
        self.assertEqual(records[0].refusal,'survivor_set_count_mismatch')
        self.assertEqual(len(records[0].outputs),1)
        for output in records[0].outputs:
            self.assertIsNone(d._FLOAT_TOKEN.search((s.restricted/output['name']).read_text()))
        # BETA's committed S3B roster variant reaches the real tripwires.
        beta=self.state();self.assertEqual(d.step_0(beta,d.StepRunner(beta.restricted))[0].status,'ok')
        beta.archives={'beta':beta.archives['beta']}
        beta.kept={'beta':load_kept_units(beta.archives['beta'],sealed_catalog_sha256=beta.pins.sealed['catalog_sha256'],planned_units=s0_planned())}
        beta_records=d.step_3(beta,d.StepRunner(beta.restricted))
        self.assertEqual(beta_records[0].status,'ok',beta_records[0])
        self.assertEqual(len(beta_records[0].outputs),1)
        records=d.step_3b(s,d.StepRunner(s.restricted))
        # The unchanged S3B archive's synthetic capture is rejected by the
        # frozen calibration pipeline; S2's capture adapter is a separate
        # structural probe below, never represented as real re-reduction.
        self.assertEqual(records[0].status,'tooling_refusal')
        self.assertEqual(records[0].refusal,'window_bracket_not_passed')


class AdditionalCustodyTests(unittest.TestCase):
    def test_F2_original_archives_are_not_role_census_inputs(self):
        from joulewise import paper_custody as c
        from joulewise.b5_analysis.archive import CensusRow
        with tempfile.TemporaryDirectory(prefix='s10-custody-gap-') as tmp:
            root=Path(tmp);repo=root/'repo';repo.mkdir();restricted=root/'restricted';restricted.mkdir()
            archive=root/'archive';archive.mkdir();(archive/'harvest.json').write_text('{}')
            s=d.RunState('blind-dry-run',root/'index.json',restricted,'a'*40,repo_root=repo)
            s.archives={'alpha':SimpleNamespace(window=SimpleNamespace(archive_root=archive),
                census=lambda:(CensusRow('harvest.json',_hash(archive/'harvest.json'),'window_index'),))}
            inputs={}
            for role in c._FAMILY_SPECS[c.ReportedEnergyParentsRef].roles_for('production'):
                s.write(role.value,'inputs/'+role.value+'.json',{'schema_version':'synthetic'})
                inputs[role.value]=s.output(role.value)
            d._custody_documents(s,pack='alpha',family='reported_energy_parents',role='synthetic.energy',
                inputs=inputs,census_name='unused')
            census=s.read('role_census_alpha')
            self.assertEqual(census['source_census'],[])
            self.assertEqual({row['path'] for row in census['inputs']},
                {path.relative_to(restricted).as_posix() for path in inputs.values()})
            self.assertTrue(all(row['base']=='runs_root' for row in census['inputs']))

    def test_validator_invalid_container_types_always_raise_named_refusal(self):
        for value in (None,[],1,12.3457331,{}, {'steps':[1]}):
            with self.subTest(value=value),self.assertRaisesRegex(AnalysisRefusal,'^dry_run_record_invalid$'):
                d.validate_dry_run_record(value)

    def test_T19_early_reader_exception_diagnostic_is_discarded(self):
        with tempfile.TemporaryDirectory(prefix='s10-early-exception-') as tmp:
            s=d.RunState('blind-dry-run',Path(tmp)/'index.json',Path(tmp)/'restricted','a'*40)
            def prepare_initial(argv):raise RuntimeError(MARKER)
            result=d.StepRunner(s.restricted).run(s.guarded(prepare_initial),[],step='0')
            self.assertEqual(result.exit_status,2)
            self.assertNotIn('7331',result.stdout_path.read_text()+result.stderr_path.read_text())
            self.assertIsNone(d._FLOAT_TOKEN.search(result.stdout_path.read_text()+result.stderr_path.read_text()))


class ReaderRecordGuardTests(unittest.TestCase):
    def test_T19_reader_output_rejects_float_before_any_file_is_written(self):
        with tempfile.TemporaryDirectory(prefix='s10-reader-guard-') as tmp:
            s=d.RunState('blind-dry-run',Path(tmp)/'index.json',Path(tmp)/'restricted','a'*40)
            for role,value in (('attempt_alpha',{'unexpected':12.3457331}),
                               ('tripwire_alpha',{'problem':'value '+MARKER}),
                               ('tripwire_beta',{'problem':'value 1e100'}),
                               ('census_gamma',{'path':'sources/1e-100.json'}),
                               ('kept_alpha',{'count':12.3457331})):
                with self.subTest(role=role),self.assertRaisesRegex(AnalysisRefusal,'^reader_record_not_structure_only$'):
                    s.write(role,'attempts/test.json',value)
            self.assertEqual(s.outputs,{})
            self.assertFalse(s.restricted.exists())


class CustodyPathWriteTests(unittest.TestCase):
    def test_registered_write_refuses_path_escape_before_mutation(self):
        with tempfile.TemporaryDirectory(prefix='s10-output-path-') as tmp:
            root=Path(tmp);restricted=root/'restricted'
            s=d.RunState('blind-dry-run',root/'index.json',restricted,'a'*40)
            for relative in ('../escaped.json',str(root/'absolute.json'),'outputs/../escaped.json','outputs//bad.json'):
                with self.subTest(path=relative),self.assertRaisesRegex(AnalysisRefusal,'^custody_path_invalid$'):
                    s.write('test',relative,{'structure':True})
            self.assertFalse(restricted.exists())
            self.assertFalse((root/'escaped.json').exists())
            self.assertFalse((root/'absolute.json').exists())

    def test_finalization_exclusions_attachment_keeps_the_name_the_manifest_records(self):
        # S10 joined run: registering the finalizer's exclusions attachment
        # renamed it with a digest prefix, so the finalized manifest's recorded
        # path no longer existed and the close-out refused
        # d165_closeout_driver_manifest_invalid (exclusions digest mismatch).
        with tempfile.TemporaryDirectory(prefix='s10-exclusions-name-') as tmp:
            root=Path(tmp);restricted=root/'restricted'
            s=d.RunState('blind-dry-run',root/'index.json',restricted,'a'*40)
            attachment=restricted/d.FINALIZATION/('analysed-attempt-exclusions-'+'c'*64+'.json')
            attachment.parent.mkdir(parents=True);attachment.write_bytes(b'{"structure":true}\n')
            item=s.register('finalized_exclusions',attachment)
            self.assertTrue(attachment.is_file())
            self.assertEqual(item['name'],attachment.relative_to(restricted).as_posix())
            other=restricted/'outputs/other.json';other.parent.mkdir();other.write_bytes(b'{}\n')
            self.assertTrue(s.register('other',other)['name'].startswith('outputs/'+hashlib.sha256(b'{}\n').hexdigest()))


class CustodyDocumentSchemaTests(unittest.TestCase):
    def test_generated_documents_use_owning_binding_and_role_schemas(self):
        from joulewise import paper_custody as c
        supply_map=(d.ROOT/c._SUPPLY_MAP_PATH).read_bytes()
        head=d.subprocess.run(['git','-C',str(d.ROOT),'rev-parse','HEAD'],check=True,capture_output=True,text=True).stdout.strip()
        cases=(('gamma',c.ClaimEvidenceRef,'production.claim_evidence.gamma.v5','claim-evidence-gamma'),
               ('alpha',c.ReportedEnergyParentsRef,'production.reported_energy_parents.qwen3-1p7b.v5','reported-energy-alpha'))
        for pack,ref_type,role,census_name in cases:
            with self.subTest(pack=pack),tempfile.TemporaryDirectory(prefix='s10-doc-schema-') as tmp:
                root=Path(tmp);repo=root/'repo';repo.mkdir()
                s=d.RunState('blind-dry-run',root/'index.json',root/'restricted',head,repo_root=repo)
                from joulewise.b5_analysis.archive import CensusRow
                source=repo/c._B5_WINDOW_INDEX_PATH;source.parent.mkdir(parents=True);source.write_text('{}')
                s.archives={'alpha':SimpleNamespace(window=SimpleNamespace(archive_root=source.parent),
                    census=lambda:(CensusRow('source.json',_hash(source),'harvest_outputs'),))}
                spec=c._FAMILY_SPECS[ref_type]
                inputs={}
                for input_role in spec.roles_for('production'):
                    if input_role is c.InputRole.FLOOR_ACCEPTANCE:continue
                    s.write(input_role.value,'inputs/'+input_role.value+'.json',{'schema_version':'synthetic'})
                    inputs[input_role.value]=s.output(input_role.value)
                if pack=='gamma':
                    s.write('pinset','mint/floor-mint-pinset.json',{'schema_version':'synthetic pinset'})
                d._custody_documents(s,pack=pack,family=spec.family,role=role,inputs=inputs,census_name=census_name)
                with c.V2AuthenticationReadSession() as session,mock.patch.object(c,'_git_blob',return_value=supply_map):
                    supply=c._load_supply_entry(session,repo,s.commit,role,spec,runs_root=s.restricted)
                consumed=(*supply.sources,*supply.source_census)
                self.assertEqual(tuple(binding.role for binding in supply.sources),spec.roles_for('production'))
                mode,_=c._validate_inventory(s.output('inventory_'+pack).read_bytes(),family=spec.family,
                    expected=(*consumed,supply.receipt.file),expected_mode='production')
                self.assertEqual(mode,'production')
                receipt=c._validate_receipt(s.output('receipt_'+pack).read_bytes(),supply.receipt,
                    family=spec.family,sources=consumed)
                self.assertEqual(receipt['status'],'PASS')
                if pack=='gamma':
                    # S10 joined run: the gate's replay reads the floor's sibling pinset,
                    # so the claim-evidence census binds it (runs_root, generated).
                    self.assertIn(('runs_root','mint/floor-mint-pinset.json',s.outputs['pinset']['sha256']),
                        {(b.base,b.path.as_posix(),b.expected_sha256) for b in supply.source_census})
                    c._validate_floor_acceptance(SimpleNamespace(source_census=supply.source_census,repository=d.ROOT,head=head,
                        raws={c.InputRole.FLOOR_ACCEPTANCE:s.output('floor_acceptance').read_bytes(),
                              c.InputRole.FLOOR_ARTIFACT:inputs['floor_artifact'].read_bytes()}))


class DriverProductionCensusTests(unittest.TestCase):
    """F2: real step functions and open/reopen, with synthetic issuance gates."""

    def logs(self,s):
        return '\n'.join(path.read_text() for path in sorted((s.restricted/'logs').glob('*.stderr.log')))

    @contextmanager
    def state(self):
        from joulewise import paper_custody as c
        with tempfile.TemporaryDirectory(prefix='s10-production-census-') as tmp:
            root=Path(tmp);repo=root/'repo';repo.mkdir()
            index=repo/c._B5_WINDOW_INDEX_PATH;index.parent.mkdir(parents=True);index.write_text('{}\n')
            s=d.RunState('blind-dry-run',index,root/'restricted','a'*40,repo_root=repo)
            s.index=SimpleNamespace(sha256=_hash(index))
            s.windows={}
            for pack in d.PACKS:
                runs=root/(pack+'-original-runs');runs.mkdir()
                s.windows[pack]=SimpleNamespace(claim_runs_root=runs,pack_id='s10-'+pack)
                s.rows[pack]={'evaluation_basis':{'sha256':{'alpha':'a','beta':'b','gamma':'c'}[pack]*64}}
            s.evidence_roots=lambda:{pack+'-evidence':s.windows[pack].claim_runs_root for pack in ('alpha','beta')}
            for role in ('finalized_manifest','floor_artifact','claim_verdicts'):
                s.write(role,'inputs/'+role+'.json',{'schema_version':'synthetic'})
            # Step 5's pinset beside the floor, which the claim-evidence census binds.
            s.write('pinset','mint/floor-mint-pinset.json',{'schema_version':'synthetic pinset'})
            binding={'exclusions_sha256':'e'*64,'harvest_pin':'a'*40}
            projections={}
            for pack in ('alpha','beta'):
                prefix=repo/'configs/campaigns'/s.windows[pack].pack_id
                for name in ('extraction_spec.json','prefill_pin/selection.json','prefill_pin/prefill_prompt_pin.json'):
                    path=prefix/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('{}\n')
                s.write('extraction_'+pack,'inputs/'+pack+'-report.json',{'kept_units_binding':binding})
                s.step_records.append(s.record('4',window=pack))
                projections[pack]={'schema_version':'joulewise.reported_energy_projection.v1',
                    'window':{'harvest_pin':binding['harvest_pin']},'exclusions_sha256':binding['exclusions_sha256'],
                    'cells':[],'refused_cells':[]}
            supply=(d.ROOT/c._SUPPLY_MAP_PATH).read_bytes()
            def blob(repository,head,relative,*args):
                self.assertEqual((repository,head),(repo,s.commit))
                return supply if relative==c._SUPPLY_MAP_PATH else (repo/relative).read_bytes()
            with mock.patch.object(c,'_mint_git_anchor',return_value=(repo,s.commit)), \
                 mock.patch.object(c,'_git_blob',side_effect=blob), \
                 mock.patch('joulewise.analysis_engine.claim_side_bound.produce_claim_side_bound',
                            new=lambda *args,**kwargs:b'{}\n'), \
                 mock.patch('scripts.issue_reported_energy.issue_pack',side_effect=lambda index,pack:projections[pack]), \
                 mock.patch('joulewise.paper_reported_energy._verify_gate_ordering'):
                yield s,projections

    def gate(self, contexts, projections):
        from joulewise import paper_custody as c
        def issue(ctx):
            contexts.append(ctx)
            kind='outcome' if ctx.family=='claim_evidence' else 'cell'
            projection=None
            if ctx.family=='reported_energy_parents':
                pack='alpha' if 'qwen3-1p7b' in ctx.supply_role else 'beta'
                projection=c._freeze_json(projections[pack])
            return c._FamilyReplay(True,True,tuple(c._RenderGrant(kind,subject) for subject in ctx.subjects),(),projection)
        return issue

    def test_F2_step9b_opens_the_production_census_with_the_gate_stubbed(self):
        from joulewise import paper_custody as c
        with self.state() as (s,projections):
            contexts=[];gate=self.gate(contexts,projections)
            with mock.patch.dict(c._ISSUANCE_GATES,{('claim_evidence','claim-evidence.v1'):gate}), \
                 mock.patch.object(c,'open_paper_input',wraps=c.open_paper_input) as opener:
                records=d.step_9b(s,d.StepRunner(s.restricted))
            self.assertEqual(records[0].status,'ok',self.logs(s))
            opener.assert_called_once_with(c.ClaimEvidenceRef(role='production.claim_evidence.gamma.v5',runs_root=s.restricted))
            self.assertEqual(len(contexts),1)
            census=s.read('role_census_gamma')
            self.assertTrue(all(row['base']=='runs_root' for row in census['inputs']))
            # The window index from the repository, and (S10) the floor's sibling
            # pinset from custody, which the gate's verdict replay reads.
            self.assertEqual([(row['base'],row['path']) for row in census['source_census']],
                             [('repository',c._B5_WINDOW_INDEX_PATH),('runs_root','mint/floor-mint-pinset.json')])
            for role in ('claim_request','floor_acceptance','receipt_gamma','inventory_gamma','role_census_gamma'):
                self.assertTrue(s.output(role).is_file())

    def test_F2_step10_opens_both_production_censuses_with_the_gate_stubbed(self):
        from joulewise import paper_custody as c
        with self.state() as (s,projections):
            contexts=[];gate=self.gate(contexts,projections)
            with mock.patch.dict(c._ISSUANCE_GATES,{('reported_energy_parents','reported-energy.v1'):gate}), \
                 mock.patch.object(c,'open_paper_input',wraps=c.open_paper_input) as opener:
                records=d.step_10(s,d.StepRunner(s.restricted))
            self.assertEqual([record.status for record in records],['ok','ok'],self.logs(s))
            self.assertEqual(opener.call_count,2)
            self.assertEqual({ctx.supply_role for ctx in contexts},
                {'production.reported_energy_parents.qwen3-1p7b.v5','production.reported_energy_parents.qwen3-8b.v5'})
            for pack in ('alpha','beta'):
                census=s.read('role_census_'+pack)
                self.assertEqual([row['path'] for row in census['source_census']],[c._B5_WINDOW_INDEX_PATH])
                self.assertTrue(all(row['base']=='runs_root' for row in census['inputs']))
                self.assertTrue(s.output('basis_'+pack).is_file())

    def test_F2_an_opener_refusal_remains_the_step_refusal(self):
        from joulewise import paper_custody as c
        def refusing_gate(ctx):
            raise c.PaperCustodyRefusal('paper_custody_binding_mismatch')
        with self.state() as (s,projections), \
             mock.patch.dict(c._ISSUANCE_GATES,{('claim_evidence','claim-evidence.v1'):
                 refusing_gate}):
            records=d.step_9b(s,d.StepRunner(s.restricted))
            self.assertEqual((records[0].status,records[0].refusal),('tooling_refusal','paper_custody_binding_mismatch'),self.logs(s))
            self.assertTrue(s.output('role_census_gamma').is_file())


class ReferenceParityTests(unittest.TestCase):
    """Step-results uses the context owner's replay signal after row admission."""

    def results(self,*,replay,admitted=True):
        from joulewise import whole_window as ww
        condition='whole_window_campaign_membership_unresolved'
        with tempfile.TemporaryDirectory(prefix='s10-reference-parity-') as tmp:
            root=Path(tmp)
            s=d.RunState('blind-dry-run',root/'index.json',root/'restricted','a'*40)
            s.windows={'alpha':SimpleNamespace(claim_runs_root=root,
                record=SimpleNamespace(entry=SimpleNamespace(superseded_archive_roots=())))}
            s.archives={'alpha':object()}
            s.rows={'alpha':{'status':'failed','evaluation_basis':{'sha256':'b'*64},
                'idle_admission_core':{'conditions':[condition] if replay else []}}}
            s.contexts={'alpha':ww.ArchiveContext(root,sources_replay=replay)}
            s.kept={'alpha':SimpleNamespace(cells={})}
            validation=SimpleNamespace(admitted=admitted,reasons=() if admitted else ('whole_window_verdict_provenance_invalid',),
                answered_conditions=frozenset({condition}) if replay else frozenset())
            with mock.patch('joulewise.b5_analysis.context.rebuilt_roster',return_value={'members':[]}), \
                 mock.patch('joulewise.b5_analysis.context.survivor_set',return_value=SimpleNamespace(bundle_ids=frozenset())), \
                 mock.patch('joulewise.b5_analysis.context._excluded',return_value={}), \
                 mock.patch('joulewise.analysis_engine.inputs.archive_snapshot',return_value=object()), \
                 mock.patch.object(ww,'AuthenticatedConsumptionSession'), \
                 mock.patch.object(ww,'validate_whole_window_verdict_row',return_value=validation) as validator:
                result=d._step_results(s)
                validator.assert_called_once()
                self.assertIs(validator.call_args.kwargs['archive_context'],s.contexts['alpha'])
                return result

    def test_catalog_replay_returned_by_owner_is_passed_after_admission(self):
        result=self.results(replay=lambda row,root:None)
        self.assertEqual(result['windows']['alpha']['reference_parity'],'passed')

    def test_no_owner_replay_is_not_applicable_after_admission(self):
        result=self.results(replay=None)
        self.assertEqual(result['windows']['alpha']['reference_parity'],'not_applicable')

    def test_replay_callback_does_not_bypass_row_admission(self):
        with self.assertRaisesRegex(AnalysisRefusal,'^whole_window_verdict_provenance_invalid$'):
            self.results(replay=lambda row,root:None,admitted=False)


class CommandInterfaceTests(unittest.TestCase):
    def test_cli_only_three_public_arguments_and_one_library_call(self):
        from scripts import run_b5_analysis as script
        with mock.patch.object(script,'run',return_value=0) as run:
            self.assertEqual(script.main(['--mode','release','--index','index.json','--custody','custody']),0)
        run.assert_called_once_with('release',Path('index.json'),Path('custody'))

    def test_cli_usage_error_cannot_echo_an_untrusted_marker(self):
        from scripts import run_b5_analysis as script
        for argv in ([],['--mode',MARKER],['--unknown',MARKER],['--help']):
            out,err=io.StringIO(),io.StringIO()
            with self.subTest(argv=argv),redirect_stdout(out),redirect_stderr(err),mock.patch.object(script,'run') as run:
                self.assertEqual(script.main(argv),2)
            self.assertEqual((out.getvalue(),err.getvalue()),('','step 0 - tooling_refusal\n'))
            run.assert_not_called()


class CustodyRefusalMappingTests(unittest.TestCase):
    def test_production_custody_refusal_is_classified_without_diagnostics(self):
        from joulewise.paper_custody import PaperCustodyRefusal
        with tempfile.TemporaryDirectory(prefix='s10-custody-refusal-') as tmp:
            s=d.RunState('blind-dry-run',Path(tmp)/'index.json',Path(tmp)/'restricted','a'*40)
            def custody_open(argv):
                raise PaperCustodyRefusal('paper_custody_not_issuable',validator_codes=(MARKER,))
            result=d.StepRunner(s.restricted).run(s.guarded(custody_open),[],step='9b')
            self.assertFalse(result.exception)
            self.assertEqual(result.token(),'paper_custody_not_issuable')
            self.assertEqual(s.record('9b',exit_status=result.exit_status,code=result.token()).status,'tooling_refusal')
            self.assertNotIn('7331',result.stdout_path.read_text()+result.stderr_path.read_text())
