"""Registered-writer counterfactuals, using cached S4/S5/S6/S8 fixtures only."""
from contextlib import ExitStack, redirect_stderr, redirect_stdout
from dataclasses import replace
import io
import sys
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from joulewise import paper_reported_energy_issuer as issuer
from joulewise.b5_analysis import context, dry_run, steps
from joulewise.b5_analysis.windows import AnalysisRefusal, SealPins
from scripts import (extract_detection_floors as extract, issue_reported_energy as issue,
                     mint_floor_artifact_generalized as mint, mint_floor_artifact as core,
                     emit_floor_mint_pinset as emit, finalize_analysis_manifest as finalize,
                     build_results_fill_input as fill)
from scripts import run_d165_closeout_from_custody as closeout
from tests.b5_analysis import fixtures as s0, fixtures_s2 as s2, fixtures_s5 as s5, fixtures_s8 as s8
from tests.b5_analysis.test_floor_kept_units import indexed_fixture
from tests.b5_analysis import test_mint_kept_units as mint_tests
from tests.b5_analysis import test_floor_kept_units as floor_tests
from tests.b5_analysis.test_mint_kept_units import governed_case, case, registered

CODE = 'sensitivity_context_on_registered_path'


def wider(value):
    return replace(value, sensitivity_bound_s=value.window_bracket['b_fiducial_s'] + 0.01)


class SensitivityGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # S6 mutates its cached S4 index to use attempt-shaped plan ids. Keep
        # this module's structural fixture independent of module run order.
        floor_cache, mint_cache = dict(floor_tests._CACHE), dict(mint_tests._CACHE)
        capture_cache = dict(s2._CACHE)
        try:
            floor_tests._CACHE.pop('indexed', None)
            mint_tests._CACHE.pop('governed', None)
            # S4 extends this S2 archive in place with p42 aliases. Reusing
            # that source would append aliases again and duplicate each
            # member's (cell_id, stratum, unit_id), which S1 must refuse.
            s2._CACHE.pop('BETA_STD_S3B_ROSTER', None)
            cls.indexed = indexed_fixture()
            cls.reported = s8.indexed_reported_fixture()
            cls.governed, cls.producer = governed_case()
        finally:
            floor_tests._CACHE.clear(); floor_tests._CACHE.update(floor_cache)
            mint_tests._CACHE.clear(); mint_tests._CACHE.update(mint_cache)
            s2._CACHE.clear(); s2._CACHE.update(capture_cache)

    def invoke(self, main, args, output):
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            result = main(args)
        self.assertEqual(result, 2)
        self.assertIn(stderr.getvalue(), (CODE+'\n', 'error: '+CODE+'\n'))
        self.assertEqual(stdout.getvalue(), '')
        self.assertFalse(output.exists())

    def test_G1_extractor_main(self):
        f = self.indexed
        real = extract.extract_indexed_pack
        builder = context.build_context
        def compose(*args, **kwargs):
            table = {**s0.PACK_TABLE, 'beta': {f.window.entry_data['pack_id']: 'v5-b5-beta-a{attempt}-'}}
            return real(*args, **kwargs, seal_pins=SealPins.load(), pack_table=table,
                        test_only_allow_synthetic_binding=True, repo_root=f.local_repo)
        with tempfile.TemporaryDirectory() as tmp, s2.capture_adapter(), \
             mock.patch.object(extract, 'extract_indexed_pack', side_effect=compose), \
             mock.patch.object(context, 'build_context', side_effect=lambda *a, **k: wider(builder(*a, **k))):
            out = Path(tmp)/'floor.json'
            self.invoke(extract.main, ['--window-index', str(f.index), '--pack', 'beta', '--out', str(out)], out)

    def test_G2_issuer_main(self):
        f = self.reported
        builder = issuer.build_context
        def compose(index, pack, **kwargs):
            return s8.issue_indexed_reported(f, index, pack, **kwargs)
        with tempfile.TemporaryDirectory() as tmp, s8.indexed_reported_seams(f), \
             mock.patch.object(issue, 'issue_pack', side_effect=compose), \
             mock.patch.object(issuer, 'build_context', side_effect=lambda *a, **k: wider(builder(*a, **k))):
            out = Path(tmp)/'energy.json'
            self.invoke(issue.main, ['--window-index', str(f.index), '--pack', 'beta', '--output', str(out)], out)

    def test_G3_generalized_mint_main(self):
        f, entry = self.governed, self.producer
        builder = context.build_context
        def before_builder(**kwargs):
            table = {**s0.PACK_TABLE, 'beta': {f.window.entry_data['pack_id']: 'v5-b5-beta-a{attempt}-'}}
            mint.compose_indexed_producers(f.index, seal_pins=SealPins.load(), pack_table=table,
                test_only_allow_synthetic_binding=True, repo_root=f.local_repo, packs=('beta',))
        with tempfile.TemporaryDirectory() as tmp, s2.capture_adapter(), \
             mock.patch.object(mint, 'load_pinset', return_value=mint._parse_v2_pinset(case().pins)), \
             mock.patch.object(mint, 'mint_multi_cell_floor_artifact', side_effect=before_builder), \
             mock.patch.object(context, 'build_context', side_effect=lambda *a, **k: wider(builder(*a, **k))):
            out = Path(tmp)/'floor.json'
            self.invoke(mint.main, mint_tests.CliTests().mint_args(Path(tmp))+['--window-index', str(f.index)], out)

    def test_G4_core_mint_main(self):
        entry = replace(self.producer, archive_context=wider(self.producer.archive_context))
        def before_builder(**kwargs):
            core._block5_producer(entry.window.claim_runs_root)
        with tempfile.TemporaryDirectory() as tmp, registered({str(entry.window.claim_runs_root.resolve()): entry}), \
             mock.patch.object(core, 'mint_floor_artifact', side_effect=before_builder):
            out = Path(tmp)/'floor.json'
            args = ['--artifact-id','synthetic','--out',str(out),'--single-count-out',str(Path(tmp)/'statement'),
                    '--calibration-plan','unused','--calibration-plan-relative-path','unused',
                    '--a10-root','unused','--a10-report','unused','--a10-spec','unused','--a10-order-manifest','unused',
                    '--window-c-root','unused','--window-c-report','unused','--window-c-spec','unused',
                    '--window-c-order-manifest','unused','--project-commit','0'*40,'--project-tree-state','clean']
            self.invoke(core.main, args, out)

    def test_G5_pinset_emitter_main(self):
        entries = {e.window.pack: e for e in case().entries.values()}
        entries['alpha'] = SimpleNamespace(**{**vars(entries['alpha']), 'archive_context': wider(entries['alpha'].archive_context)})
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(mint, 'compose_indexed_producers', return_value=entries):
            out = Path(tmp)/'floor-mint-pinset.json'
            self.invoke(emit.main, ['--window-index','unused','--alpha-report','unused','--beta-report','unused',
                        '--out-dir',tmp,'--project-commit','0'*40], out)
        self.assertFalse(mint.BLOCK5_PRODUCERS)

    def test_G6_finalizer_main(self):
        with s5.finalization_case() as f:
            built = {**f['block5_inputs'], 'archive_contexts': {k: wider(v) for k,v in f['block5_inputs']['archive_contexts'].items()}}
            out = f['root']/(f['prospective']['manifest_id']+'.finalized.json')
            with mock.patch.object(finalize, 'block5_claim_gate_inputs', return_value=built):
                self.invoke(finalize.main, ['--window-index','unused','--prospective-manifest',str(f['prospective_path']),
                    '--plan-tree',str(f['plan_tree_path']),'--custody-root',str(f['root']),'--runs-root',str(f['runs_root']),
                    '--whole-window-verdict',str(f['verdict_path']),'--bracket-binding',str(f['bracket_path']),
                    '--calibration-ledger',str(f['ledger_path']),'--aggregate-floor-artifact',str(f['floor_path']),
                    '--output-dir',str(f['root'])], out)

    def test_G8_fill_builder_main(self):
        from tests.b5_analysis.test_fill_adapter import FillAdapterTests
        f = s8.fill_fixture()
        harness = FillAdapterTests(); harness.f = f
        with tempfile.TemporaryDirectory() as tmp, harness.cli_seams(), \
             mock.patch.object(fill, 'block5_claim_gate_inputs', return_value={
                 'kept_units': f.loaded.kept_units, 'archive_contexts': {'gamma': wider(self.producer.archive_context)}}):
            out = Path(tmp)/'fill.json'
            self.invoke(fill.main, ['--window-index','unused','--custody-root',str(f.root),
                '--finalized-manifest',str(f.root/'manifest.json'),'--claim-verdicts',str(f.root/'verdicts.json'),
                '--out',str(out)], out)

    def test_G7_closeout_main(self):
        # S7's authenticated-source resolver is exercised separately in P2.
        # Its pre-builder custody reads are the boundary doubled here.
        import json
        from joulewise import analysis_manifest_v3 as manifests, dominance_closeout as dominance
        manifest = {'schema_version': dominance.FINALIZED_MANIFEST_SCHEMA_VERSION,
                    'freeze_status':'finalized','manifest_id':'synthetic',
                    'lineage':{'prospective_manifest_path':'prospective.json'},
                    'evidence':{'aggregate_floor_artifact':{'sha256':'unused'},
                        'dominance_replay_sidecar':{'sha256':'unused'},
                        'bracket_binding':{'sha256':'unused'},'analysed_attempt_exclusions':{}}}
        with s5.finalization_case() as f, tempfile.TemporaryDirectory() as tmp:
            built = {**f['block5_inputs'], 'archive_contexts': {
                key: wider(value) for key,value in f['block5_inputs']['archive_contexts'].items()}}
            raws = [b'{}', b'{}', json.dumps({'runs_root':str(f['runs_root'])}).encode()]
            root = Path(tmp); (root/'prospective.json').write_bytes(b'{}')
            (root/'manifest.json').write_bytes(json.dumps(manifest).encode())
            out = root/'closeout.json'
            with mock.patch.object(closeout,'read_authentication_input_nofollow',return_value=json.dumps(manifest).encode()), \
                 mock.patch.object(closeout,'_read_attachment',side_effect=[('unused',raw) for raw in raws]), \
                 mock.patch.object(closeout,'_check_attachment_digest'), \
                 mock.patch.object(closeout,'block5_claim_gate_inputs',return_value=built):
                self.invoke(closeout.main, ['--finalized-manifest',str(root/'manifest.json'),
                    '--custody-root',tmp,'--window-index','unused','--output',str(out)], out)
            self.assertFalse(out.with_suffix('.step.json').exists())

    def test_G9_driver_writer_handoff(self):
        writer = mock.Mock()
        with self.assertRaisesRegex(AnalysisRefusal, '^'+CODE+'$'):
            dry_run.writer_handoff(writer, {'beta': wider(self.producer.archive_context)})
        writer.assert_not_called()

    def test_helper_direct_mapping_sequence_and_session(self):
        primary = self.producer.archive_context
        steps.require_primary_context(primary, None, {'beta': primary}, [primary])
        for value in (wider(primary), {'beta': wider(primary)}, [wider(primary)],
                      SimpleNamespace(sensitivity_bound_s=0.05)):
            with self.subTest(value=type(value).__name__), self.assertRaisesRegex(AnalysisRefusal, '^'+CODE+'$'):
                steps.require_primary_context(value)

    def test_helper_import_does_not_load_whole_window(self):
        import subprocess
        result = subprocess.run([sys.executable,'-B','-c',
            "import sys; import joulewise.b5_analysis.steps; assert 'joulewise.whole_window' not in sys.modules"],
            capture_output=True, text=True)
        self.assertEqual((result.returncode,result.stdout,result.stderr),(0,'',''))


class DriverIntegrationGuardTests(unittest.TestCase):
    def test_G9_full_driver_refuses_wider_context_before_registered_writer(self):
        from tests.b5_analysis import test_dry_run as fixture
        case=fixture.DriverAcceptanceTests()
        case.setUpClass();case.setUp()
        self.addCleanup(case.doClassCleanups)
        from joulewise.whole_window import ArchiveContext
        class WiderDriver(fixture.DriverDouble):
            def run(self,main,argv,**kwargs):
                result=super().run(main,argv,**kwargs)
                if getattr(main,'_operation',None)=='prepare_brackets':
                    primary=ArchiveContext(self.state.windows['alpha'].archive_root,
                                           window_bracket={'status':'passed','b_fiducial_s':0.02})
                    self.state.contexts={'alpha':wider(primary)}
                return result
        result=case.execute(runner=WiderDriver)
        self.assertEqual(result.code,2)
        row=next(row for row in result.record['steps'] if row['step']=='4')
        self.assertEqual((row['status'],row['refusal']),('tooling_refusal',CODE))
        self.assertEqual(row['outputs'],[])
        self.assertFalse(any(step=='4' for step,_,_ in WiderDriver.calls))
