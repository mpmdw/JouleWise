"""Real S10 programs over cached production-shaped, pinned synthetic windows."""
from __future__ import annotations
import contextlib
import io
import json
from pathlib import Path
import tempfile
import time
import unittest
import sys
import inspect
import shutil
import os
from concurrent.futures import ProcessPoolExecutor

from tests.b5_analysis.fixtures_s10 import chain_fixture,PACK_IDS,ROOT,put
from joulewise.b5_analysis.windows import (SealPins,load_window_index,
    select_analysed_attempts,AnalysedWindow,AnalysisRefusal)
from joulewise.b5_analysis.archive import open_attempt_record,open_archive
from joulewise.b5_analysis.kept_units import load_kept_units
from joulewise.b5_analysis.bracket import evaluate_window_bracket,require_ledger_copies_are_prefixes
from joulewise.b5_analysis.context import build_context
from joulewise import cli,whole_window as ww
from scripts import extract_detection_floors as extract
from dataclasses import replace


def member_cli(args):
    stream=io.StringIO();started=time.monotonic()
    with contextlib.redirect_stdout(stream),contextlib.redirect_stderr(stream):code=cli.main(args)
    return code,stream.getvalue(),time.monotonic()-started


class ChainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture=chain_fixture()
        if os.environ.get('JW_B5_S10_CHAIN_CACHE'):
            cls.custody=cls.fixture.root/'chain-custody';cls.custody.mkdir(exist_ok=True)
        else:
            cls.temporary=tempfile.TemporaryDirectory(prefix='s10-chain-custody-',dir=cls.fixture.root)
            cls.addClassCleanup(cls.temporary.cleanup)
            cls.custody=Path(cls.temporary.name)
        cls.pins=SealPins.load();cls.cache={};cls.kept_cache={};cls.evidence=[]

    @classmethod
    def tearDownClass(cls):
        evidence=ROOT/'.scratch-s10f/chain-evidence.json'
        if evidence.parent.is_dir():
            put(evidence,cls.evidence)
            with (evidence.parent/'chain-evidence-history.jsonl').open('a') as history:
                history.write(json.dumps({'argv':sys.orig_argv,'evidence':cls.evidence},sort_keys=True)+'\n')
            if hasattr(cls,'custody'):
                target=evidence.parent/'chain-output'
                if target.exists():shutil.rmtree(target)
                shutil.copytree(cls.custody,target)

    def window(self,pack):
        if pack not in self.fixture.windows:self.skipTest('window not built')
        return self.fixture.windows[pack]

    @contextlib.contextmanager
    def timed(self,step,pack):
        t=time.monotonic()
        try:
            yield
        except BaseException as exc:
            self.evidence.append({'step':step,'pack':pack,'wall_s':time.monotonic()-t,
                'result':'error','error':str(exc),'raising':type(exc).__name__})
            raise
        else:self.evidence.append({'step':step,'pack':pack,'wall_s':time.monotonic()-t,'result':'passed'})

    def kept_composition(self,pack):
        self.window(pack)
        if pack not in self.kept_cache:
            with self.fixture.seams():
                index=load_window_index(self.fixture.program_index,seal_pins=self.pins)
                records=tuple(open_attempt_record(e,seal_pins=self.pins) for e in index.entries)
                selected=select_analysed_attempts(index,records,seal_pins=self.pins)[pack]
                archive=open_archive(selected,seal_pins=self.pins)
                if pack=='gamma':
                    from joulewise.analysis_engine.inputs import planned_contrast_units
                    manifest=json.loads((ROOT/'configs/campaigns'/PACK_IDS[pack]/'analysis_manifest_v3.json').read_bytes())
                    planned=planned_contrast_units(manifest)
                else:
                    spec=json.loads((ROOT/'configs/campaigns'/PACK_IDS[pack]/'extraction_spec.json').read_bytes())
                    planned={}
                    for cell in spec['cells']:
                        strata=planned.setdefault(cell['condition_family_id'],{})
                        if cell['kind']=='absolute':strata['repeat']={m['bundle_id']:(m['bundle_id'],) for m in cell['members']}
                        else:strata['quad']={b['block_id']:tuple(b['members'][p] for p in ('A1','B1','B2','A2')) for b in cell['blocks']}
                kept=load_kept_units(archive,sealed_catalog_sha256=self.pins.sealed['catalog_sha256'],planned_units=planned)
                self.kept_cache[pack]=(archive,kept)
        return self.kept_cache[pack]

    def composition(self,pack):
        if pack not in self.cache:
            archive,kept=self.kept_composition(pack)
            bracket=evaluate_window_bracket(archive,repo_root=self.fixture.repo_root)
            context=build_context(archive,kept,bracket,self.fixture.windows[pack].writer_row)
            self.cache[pack]=(archive,kept,bracket,context)
        return self.cache[pack]

    def check_c0(self,pack):
        w=self.window(pack)
        with self.timed('C0',pack),self.fixture.seams():
            record=open_attempt_record(w.entry,seal_pins=self.pins)
            direct=AnalysedWindow.from_record(record,seal_pins=self.pins)
            self.assertEqual(direct.pack,pack)
            # open_archive owns the full-block selection fence. Partial builds
            # select against pinned S0 peers through the pack-identity seam.
            index=load_window_index(self.fixture.program_index,seal_pins=self.pins)
            records=tuple(open_attempt_record(e,seal_pins=self.pins) for e in index.entries)
            selected=select_analysed_attempts(index,records,seal_pins=self.pins)[pack]
            archive=open_archive(selected,seal_pins=self.pins)
            self.assertEqual(archive.compare_runs_root(),())
            require_ledger_copies_are_prefixes([archive],w.measurement/'runs/calibration_observation_ledger.jsonl')

    def check_members(self,step,pack):
        w=self.window(pack);archive,kept=self.kept_composition(pack)
        ids=sorted(set().union(*(kept.kept_run_ids(cid) for cid in kept.cells)))
        with self.timed(step,pack):
            destination=(Path(tempfile.mkdtemp(prefix=pack+'-C2-',dir=self.custody)) if step=='C2' else None)
            commands=[]
            for bid in ids:
                args=['validate-bundle','--strict',str(w.claim/bid)] if step=='C1' else [
                    'reduce',str(w.claim/bid),'--output',str(destination/(bid+'.json'))]
                commands.append(args)
            with ProcessPoolExecutor(max_workers=8) as pool:
                for bid,(code,output,seconds) in zip(ids,pool.map(member_cli,commands)):
                    self.assertEqual(code,0,bid+': '+output)
                    if step=='C2':self.assertTrue((destination/(bid+'.json')).is_file())

    def check_c3(self,pack):
        w=self.window(pack)
        with self.timed('C3',pack):
            archive,kept,bracket,context=self.composition(pack)
            self.assertEqual(w.writer_row['status'],'failed')
            self.assertEqual(ww._row_consumption_semantics_id(w.writer_row),ww.MINTED_CONSUMPTION_SEMANTICS_ID)
            self.assertIn(w.aborted,context.removed_bundle_ids)
            self.assertNotIn(w.aborted,w.writer_row['bundle_ids'])
            self.assertIn(w.aborted,{row['bundle_id'] for row in w.writer_row['excluded_bundles']})
            for cid,cell in kept.cells.items():
                for stratum,planned in cell.planned.items():
                    self.assertEqual(planned,len(cell.kept[stratum])+sum(u.stratum==stratum for u in cell.dropped))
            self.assertGreater(bracket.b_fiducial_s,0.)

    def check_c4(self,pack):
        w=self.window(pack)
        with self.timed('C4',pack),self.fixture.seams():
            out=self.custody/(pack+'-extraction.json')
            if out.exists():
                history=self.custody/'previous-extractions';history.mkdir(exist_ok=True)
                out.rename(history/(pack+'-'+str(time.monotonic_ns())+'.json'))
            stream=io.StringIO()
            sessions=[]
            # Observe the real program's returned context so later chain
            # steps reuse that exact composition without another replay.
            def observed(code,offset,result):
                frame=inspect.currentframe().f_back;args=frame.f_locals
                if isinstance(result,ww.ArchiveContext) and args['archive'].window.pack==pack:
                    self.kept_cache[pack]=(args['archive'],args['kept_units'])
                    self.cache[pack]=(args['archive'],args['kept_units'],args['window_bracket'],result)
                session=args.get('self')
                if (isinstance(session,ww.AuthenticatedConsumptionSession)
                    and session.runs_root==w.claim and len(session.referenced_bundle_ids)>1):
                    sessions.append({'ready':session.ready,'reasons':list(session.refusal_reasons),
                        'context':session.archive_context is not None,
                        'removed_member_preparation':list(session.removed_member_preparation)})
            tool=next(i for i in range(6) if sys.monitoring.get_tool(i) is None)
            event=sys.monitoring.events.PY_RETURN;source=build_context.__code__
            sys.monitoring.use_tool_id(tool,'s10-readonly-context-observer')
            sys.monitoring.register_callback(tool,event,observed)
            sys.monitoring.set_local_events(tool,source,event)
            preparation=ww.AuthenticatedConsumptionSession._prepare.__code__
            sys.monitoring.set_local_events(tool,preparation,event)
            try:
                with contextlib.redirect_stdout(stream),contextlib.redirect_stderr(stream):
                    code=extract.main(['--window-index',str(self.fixture.program_index),'--pack',pack,
                        '--out',str(out),'--hash-bundles'])
            finally:
                sys.monitoring.set_local_events(tool,source,0)
                sys.monitoring.set_local_events(tool,preparation,0)
                sys.monitoring.register_callback(tool,event,None)
                sys.monitoring.free_tool_id(tool)
                self.evidence.append({'step':'C4 real sessions','pack':pack,'sessions':sessions})
            self.assertEqual(code,1,stream.getvalue())
            self.assertTrue(out.is_file(),stream.getvalue())
            report=json.loads(out.read_bytes())
            from joulewise.b5_analysis.steps import classify_step4_exit
            spec=json.loads((ROOT/'configs/campaigns'/PACK_IDS[pack]/'extraction_spec.json').read_bytes())
            self.assertEqual(classify_step4_exit(code,report,spec),'p42_floor_cells_only',
                json.dumps({c['cell_id']:c['refusal_reasons'] for c in report['cells']}))
            self.assertTrue(sessions)
            self.assertTrue(all(s['ready'] and s['context'] for s in sessions),sessions)
            bound=self.composition(pack)[2].b_fiducial_s
            self.assertTrue(report['consumption_provenance'])
            for bid,provenance in report['consumption_provenance'].items():
                self.assertEqual(provenance['operative_fiducial_bound_s'],bound,bid)

    def session(self,pack,context=None):
        w=self.window(pack);archive,kept,bracket,primary=self.composition(pack)
        from joulewise.b5_analysis import bracket as wb
        from joulewise.schemas import CampaignPolicy
        inputs=wb._Inputs(archive);raw,prefix,pin=wb._copy(inputs)
        acceptance=json.loads(archive.source_bytes('sources/inputs/acceptance.json'))
        snapshot=wb._snapshot(prefix,pin,repo_root=self.fixture.repo_root,cutoff=acceptance['ledger_cutoff'])
        ids=frozenset(w.writer_row['bundle_ids'])
        session=ww.AuthenticatedConsumptionSession(w.claim,ids,mode='read_replay',
            consumption_semantics_id=ww.MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
            calibration_ledger_snapshot=snapshot,archive_context=context or primary)
        policy=CampaignPolicy.from_mapping(json.loads((ROOT/'configs/campaign_policies/quiet_mac_p2_production.json').read_bytes()))
        session._prepare(bundle_paths={bid:w.claim/bid for bid in ids},policy=policy)
        return session

    def check_f1(self,pack):
        w=self.window(pack)
        with self.timed('C-F1',pack):
            session=self.session(pack)
            self.assertTrue(session.ready,session.refusal_reasons)
            self.assertNotIn(w.aborted,session.referenced_bundle_ids)
            self.assertNotIn(w.aborted,w.writer_row['bundle_ids'])
            self.assertIn(w.aborted,{r['bundle_id'] for r in w.writer_row['excluded_bundles']})
            if w.retired:
                self.assertIn(w.retired,w.writer_row['bundle_ids'])
                self.assertIn(w.retired,self.composition(pack)[3].removed_bundle_ids)
                self.assertIn('removed_member_preparation:capture_pipeline_superseded:'+w.retired,
                    session.removed_member_preparation)
                self.assertIsNone(session.summary_for(w.retired))

    def check_b1(self):
        w=self.window('beta');self.window('alpha')
        with self.timed('C-B1','beta'):
            archive,kept,bracket,context=self.composition('beta')
            session=self.session('beta');self.assertTrue(session.ready,session.refusal_reasons)
            spec=json.loads((ROOT/'configs/campaigns'/PACK_IDS['beta']/'extraction_spec.json').read_bytes())
            target=next(c for c in spec['cells'] if c['kind']=='absolute' and 'decode' in c['cell_id'])
            candidates={m['bundle_id'] for m in target['members']} & kept.kept_run_ids(target['condition_family_id'])
            bid=next(b for b in sorted(candidates)
                if '/phase_energy_j/decode' in session.provenance_for(b)['operative_envelopes'])
            independent=ww._rederive_summary_for_authenticated_fiducial_bound(w.claim/bid,
                authenticated_fiducial_bound_s=bracket.b_fiducial_s)
            pointer='/phase_energy_j/decode'
            actual=session.provenance_for(bid)['operative_envelopes'][pointer]
            expected=ww._complete_envelope_record(independent['energy_anchor_shift_envelopes'][pointer])
            stored=json.loads((w.claim/bid/'summary_metrics.json').read_bytes())['energy_anchor_shift_envelopes'][pointer]
            self.assertEqual(dict(actual),expected)
            self.assertNotEqual(dict(actual),ww._complete_envelope_record(stored))
            self.assertNotEqual(bracket.b_fiducial_s,self.composition('alpha')[2].b_fiducial_s)
            from joulewise.floor_extraction import extract_cells
            # The full C4 report already proves every target cell. These two
            # negative probes need one registered kept decode cell to prove
            # the global bound guard, without repeating unrelated physics.
            mutation_spec={**spec,'cells':[target]}
            for label,bound in [('pre_capture',bracket.evaluation['pre']['b_fiducial_s']),
                                ('other_window',self.composition('alpha')[2].b_fiducial_s)]:
                raw=ww._archive_thaw(context.window_bracket);raw['b_fiducial_s']=bound
                mutated=replace(context,window_bracket=raw)
                report=extract_cells(w.claim,mutation_spec,kept_units=kept,archive_context=mutated,
                    evaluation_basis_sha256=w.writer_row['evaluation_basis']['sha256'],
                    consumption_semantics_id=ww.MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,mode='read_replay')
                reasons=sorted({r for c in report['cells'] for r in c['refusal_reasons']})
                self.assertTrue(all(not c['extractable'] for c in report['cells']),label)
                self.assertTrue(set(reasons)&{'operative_bound_not_the_window_bracket','window_bracket_not_passed',
                    'whole_window_calibration_bracket_invalid','whole_window_verdict_provenance_invalid'},reasons)
                self.evidence.append({'step':'C-B1 mutation','pack':'beta','bound':label,'result':'refused','reasons':reasons})

    def check_c5(self):
        for pack in PACK_IDS:self.window(pack)
        with self.timed('C5','alpha+beta'),self.fixture.seams():
            from scripts import emit_floor_mint_pinset as emit,mint_floor_artifact_generalized as mint
            import subprocess
            head=subprocess.run(['git','-C',str(ROOT),'rev-parse','HEAD'],check=True,capture_output=True,text=True).stdout.strip()
            for pack in ('alpha','beta'):
                if not (self.custody/(pack+'-extraction.json')).exists():self.check_c4(pack)
            out=Path(tempfile.mkdtemp(prefix='mint-',dir=self.custody))
            stream=io.StringIO()
            sites=[]
            def observe(code,offset,result):
                frame=inspect.currentframe().f_back
                session=frame.f_locals.get('self')
                if isinstance(session,ww.AuthenticatedConsumptionSession) and len(session.referenced_bundle_ids)>1:
                    caller=frame.f_back;chain=[]
                    while caller is not None:
                        file=Path(caller.f_code.co_filename).name
                        if file in {'mint_floor_artifact.py','mint_floor_artifact_generalized.py','floor_mint_estimator.py','emit_floor_mint_pinset.py'}:
                            chain.append({'function':caller.f_code.co_name,'line':caller.f_lineno,'file':file,
                                'module':caller.f_globals.get('__name__')})
                        caller=caller.f_back
                    sites.append({'site_chain':chain,'runs_root':str(session.runs_root),
                        'ready':session.ready,'reasons':list(session.refusal_reasons)})
            tool=next(i for i in range(6) if sys.monitoring.get_tool(i) is None)
            event=sys.monitoring.events.PY_RETURN;code=ww.AuthenticatedConsumptionSession._prepare.__code__
            sys.monitoring.use_tool_id(tool,'s10-readonly-session-observer')
            sys.monitoring.register_callback(tool,event,observe)
            sys.monitoring.set_local_events(tool,code,event)
            try:
                for pack in ('alpha','beta'):
                    shutil.copyfile(self.custody/(pack+'-extraction.json'),out/(pack+'-extraction.json'))
                # Seat A owns the emitter's absolute-path repair. Supply
                # actual sibling reports by relative path, as its tests do.
                with contextlib.chdir(out):self._mint_c5(emit,mint,out,head,stream)
            finally:
                sys.monitoring.set_local_events(tool,code,0)
                sys.monitoring.register_callback(tool,event,None)
                sys.monitoring.free_tool_id(tool)
                self.evidence.append({'step':'C5 real session sites','pack':'alpha+beta','sites':sites})
            self.assertTrue(sites)
            self.assertTrue(all(s['ready'] for s in sites),sites)
            self.assertEqual({s['runs_root'] for s in sites},
                {str(self.fixture.windows[p].claim) for p in ('alpha','beta')})

    def _mint_c5(self,emit,mint,out,head,stream):
            with contextlib.redirect_stdout(stream),contextlib.redirect_stderr(stream):
                code=emit.main(['--window-index',str(self.fixture.index),
                    '--alpha-report','alpha-extraction.json',
                    '--beta-report','beta-extraction.json',
                    '--out-dir','.','--project-commit',head])
            self.assertEqual(code,0,stream.getvalue())
            from tests.b5_analysis.fixtures_s10 import sha
            stream=io.StringIO()
            self.floor=out/'aggregate-floor.json';self.sidecar=out/'dominance-replay.json'
            with contextlib.redirect_stdout(stream),contextlib.redirect_stderr(stream):
                code=mint.main(['--window-index',str(self.fixture.index),
                    '--pinset',str(out/'floor-mint-pinset.json'),
                    '--pinset-sha256',sha(out/'floor-mint-pinset.json'),
                    '--v2-input-manifest',str(out/'floor-mint-inputs.json'),
                    '--out',str(self.floor),'--single-count-out',str(out/'single-count.txt'),
                    '--d165-replay-out',str(self.sidecar),'--project-commit',head,'--project-tree-state','clean'])
            self.assertEqual(code,0,stream.getvalue())
            for p in (self.floor,self.sidecar,out/'single-count.txt'):self.assertTrue(p.is_file())
            type(self).floor=self.floor;type(self).sidecar=self.sidecar

    def check_c8(self):
        w=self.window('gamma')
        if not hasattr(type(self),'floor'):self.check_c5()
        with self.timed('C8','gamma'),self.fixture.seams():
            from scripts import finalize_analysis_manifest as finalize
            pack=w.measurement/'configs/campaigns'/PACK_IDS['gamma']
            stream=io.StringIO();output=Path(tempfile.mkdtemp(prefix='finalized-',dir=self.custody))
            with contextlib.redirect_stdout(stream),contextlib.redirect_stderr(stream):
                code=finalize.main(['--window-index',str(self.fixture.index),
                    '--prospective-manifest',str(pack/'analysis_manifest_v3.json'),
                    '--plan-tree',str(pack/'plan_tree.json'),'--custody-root',str(self.fixture.root),
                    '--runs-root',str(w.claim),'--whole-window-verdict',str(w.claim/'whole-window-verdict.json'),
                    '--bracket-binding',str(w.archive/'derived/bracket-binding.json'),
                    '--calibration-ledger',str(w.measurement/'runs/calibration_observation_ledger.jsonl'),
                    '--aggregate-floor-artifact',str(self.floor),'--dominance-replay-sidecar',str(self.sidecar),
                    '--output-dir',str(output)])
            self.assertEqual(code,0,stream.getvalue())
            paths=list(output.glob('*.json'));self.assertEqual(len(paths),1)
            type(self).finalized=paths[0]
            manifest=json.loads(paths[0].read_bytes())
            self.assertEqual(manifest['schema_version'],'joulewise.analysis_manifest.v3.finalized')
            self.assertEqual(manifest['evidence']['window_bracket']['evaluation_sha256'],
                ww.canonical_sha256(ww._archive_thaw(self.composition('gamma')[2].evaluation)))
            # The role is authenticated by the finalizer; inspect its digest
            # again without replacing the claim-input builder.
            from joulewise.analysis_engine.inputs import block5_claim_gate_inputs
            built=block5_claim_gate_inputs(self.fixture.index,paths[0],w.claim)
            self.assertEqual(built['brackets']['gamma'].b_fiducial_s,self.composition('gamma')[2].b_fiducial_s)

    def check_c9(self):
        w=self.window('gamma')
        if not hasattr(type(self),'finalized'):self.check_c8()
        with self.timed('C9/C-N4','gamma'),self.fixture.seams():
            pinset=json.loads((self.floor.parent/'floor-mint-pinset.json').read_bytes());args=['analyze-claims','--analysis-manifest',str(self.finalized),
                '--runs-root',str(w.claim),'--floor-artifact',str(self.floor),'--neg8-harvest-archive',str(w.archive),
                '--window-index',str(self.fixture.index)]
            for pack,producer in zip(('alpha','beta'),pinset['producer_plans'],strict=True):
                root_id=producer['evidence_root_id']
                args+=['--evidence-root',root_id+'='+str(self.fixture.windows[pack].claim)]
            out=self.finalized.parent/'claim-verdicts.json';args+=['--output',str(out)]
            stream=io.StringIO()
            with contextlib.redirect_stdout(stream),contextlib.redirect_stderr(stream):code=cli.main(args)
            self.assertEqual(code,0,stream.getvalue())
            verdicts=json.loads(out.read_bytes())
            self.assertEqual(verdicts['schema_version'],'joulewise.claim_verdicts.v1')
            self.assertEqual(len(verdicts['contrasts']),2)
            type(self).claims=out

    def test_00_c0_alpha(self):self.check_c0('alpha')
    def test_01_c0_beta(self):self.check_c0('beta')
    def test_02_c0_gamma(self):self.check_c0('gamma')
    def test_03_c0_complete_index(self):
        for pack in PACK_IDS:self.window(pack)
        with self.timed('C0 complete index','all'),self.fixture.seams():
            index=load_window_index(self.fixture.index,seal_pins=self.pins)
            records=tuple(open_attempt_record(e,seal_pins=self.pins) for e in index.entries)
            selected=select_analysed_attempts(index,records,seal_pins=self.pins)
            self.assertEqual(set(selected),set(PACK_IDS));self.assertEqual(len(records),5)
            self.assertEqual(selected['beta'].attempt,3)
            self.assertEqual([r.claim_usable for r in sorted((r for r in records if r.entry.pack=='beta'),key=lambda r:r.entry.attempt)],
                [False,False,True])
            archives=[open_archive(selected[p],seal_pins=self.pins) for p in PACK_IDS]
            require_ledger_copies_are_prefixes(archives,
                self.fixture.windows['gamma'].measurement/'runs/calibration_observation_ledger.jsonl')
    def test_10_c1_alpha(self):self.check_members('C1','alpha')
    def test_11_c1_beta(self):self.check_members('C1','beta')
    def test_12_c1_gamma(self):self.check_members('C1','gamma')
    def test_20_c2_alpha(self):self.check_members('C2','alpha')
    def test_21_c2_beta(self):self.check_members('C2','beta')
    def test_22_c2_gamma(self):self.check_members('C2','gamma')
    def test_30_c3_alpha(self):self.check_c3('alpha')
    def test_31_c3_beta(self):self.check_c3('beta')
    def test_32_c3_gamma(self):self.check_c3('gamma')
    def test_33_bracket_skips_authenticated_unreadable_removed_summaries(self):
        w=self.window('alpha')
        archive,kept,bracket,context=self.composition('alpha')
        self.assertEqual((w.claim/w.truncated/'summary_metrics.json').read_bytes(),b'{"status":')
        self.assertIn(w.truncated,context.removed_bundle_ids)
        self.assertEqual(bracket.evaluation['status'],'passed')
    def test_40_c4_alpha(self):self.check_c4('alpha')
    def test_34_relocated_allowance_artifact_authenticates(self):
        w=self.window('alpha')
        context=self.composition('alpha')[3]
        outcome=ww._neg8_screen_outcome(w.writer_row,context=context)
        self.assertTrue(outcome.passed,outcome.problem)
        self.assertEqual(outcome.source,'survivor_rescreen')
        self.assertEqual(ww._hazard_membership_replay_reasons(w.writer_row,w.claim,
            w.writer_row['campaign_policy']['sha256']),set())
    def test_35_stored_bound_uses_archived_corpus_identity(self):
        w=self.window('alpha')
        context=self.composition('alpha')[3]
        artifact=w.writer_row['idle_admission_core']['neg8_bracket']['drift_bound_artifact']
        self.assertTrue(ww.validate_neg8_drift_bound_artifact(artifact,
            reference_corpus_bytes=getattr(context,'archived_reference_corpus_bytes',None),
            require_corpus_identity=True))
    def test_36_reference_campaigns_are_separate_from_floor_campaigns(self):
        w=self.window('alpha')
        from joulewise.analysis_engine.inputs import campaign_cooldown_evidence
        cooldowns=campaign_cooldown_evidence(w.claim,None)
        spec=json.loads((ROOT/'configs/campaigns'/PACK_IDS['alpha']/'extraction_spec.json').read_bytes())
        referenced=set()
        for cell in spec['cells']:
            if cell['kind']=='absolute':
                referenced.update(member['bundle_id'] for member in cell['members'])
            else:
                referenced.update(bid for block in cell['blocks'] for bid in block['members'].values())
        campaigns={}
        for bid,cooldown in cooldowns.items():
            self.assertTrue(cooldown.get('manifest'),bid)
            campaigns.setdefault(cooldown['manifest'],set()).add(bid)
        addressed=[ids for ids in campaigns.values() if ids & referenced]
        self.assertTrue(addressed)
        for ids in addressed:
            self.assertLessEqual(ids,referenced)
    def test_41_c4_beta(self):self.check_c4('beta')
    def test_42_b1_beta(self):self.check_b1()
    def test_50_c5_mint(self):self.check_c5()
    def test_60_c8_gamma(self):self.check_c8()
    def test_61_c9_gamma(self):self.check_c9()
    def test_70_f1_alpha(self):self.check_f1('alpha')
    def test_71_f1_beta(self):self.check_f1('beta')
    def test_72_f1_gamma(self):self.check_f1('gamma')


if __name__=='__main__':unittest.main()
